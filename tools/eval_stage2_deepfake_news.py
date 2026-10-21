#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from convert_stage2_deepfake_news_to_qwen_vl import TARGET_KEYS, validate_target


VALID_IMAGE_VERDICTS = {"authentic", "tampered"}
VALID_TAMPER_DOMAINS = {"none", "deepfake"}
VALID_RELATIONS = {"consistent", "mismatched"}
VALID_FINAL = {"credible", "fake_news"}
VALID_REGIONS = {"face", "none"}
UNKNOWN_CELL = "unknown"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_all(path: Path, records: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for key in sorted(records):
            f.write(json.dumps(records[key], ensure_ascii=False) + "\n")
    tmp.replace(path)


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    stripped = text.strip()
    candidates = [stripped]
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        candidates.insert(0, fence.group(1).strip())
    brace = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if brace:
        candidates.append(brace.group(0))
    last_error = None
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
        except Exception as exc:
            last_error = str(exc)
            continue
        if isinstance(obj, dict):
            return obj, None
    return None, last_error or "no JSON object found"


def normalize_enum(value: Any, valid: set[str], fallback: str = "unknown") -> str:
    text = str(value or "").strip().lower()
    if text in valid:
        return text
    if valid == VALID_IMAGE_VERDICTS:
        if "tamper" in text or "manipulat" in text or "fake" in text:
            return "tampered"
        if "authentic" in text or "genuine" in text or "unaltered" in text:
            return "authentic"
    if valid == VALID_TAMPER_DOMAINS:
        if "deepfake" in text or "face" in text:
            return "deepfake"
        if text in {"", "none", "no", "null", "n/a"}:
            return "none"
    if valid == VALID_RELATIONS:
        if "mismatch" in text or "inconsistent" in text or "contradict" in text:
            return "mismatched"
        if "consistent" in text or "match" in text or "support" in text:
            return "consistent"
    if valid == VALID_FINAL:
        if "fake" in text or "misleading" in text:
            return "fake_news"
        if "credible" in text:
            return "credible"
    if valid == VALID_REGIONS:
        if "face" in text:
            return "face"
        if text in {"", "none", "no", "null", "n/a"}:
            return "none"
    return fallback


def parse_prediction(raw: str) -> dict[str, Any]:
    obj, error = extract_json_object(raw)
    valid_json = obj is not None
    pred = {
        "image_verdict": "unknown",
        "tamper_domain": "unknown",
        "text_image_relation": "unknown",
        "final_news_verdict": "unknown",
        "forensic_region": "unknown",
        "evidence": [],
    }
    valid_schema = False
    if obj is not None:
        pred = {
            "image_verdict": normalize_enum(obj.get("image_verdict"), VALID_IMAGE_VERDICTS),
            "tamper_domain": normalize_enum(obj.get("tamper_domain"), VALID_TAMPER_DOMAINS),
            "text_image_relation": normalize_enum(obj.get("text_image_relation"), VALID_RELATIONS),
            "final_news_verdict": normalize_enum(obj.get("final_news_verdict"), VALID_FINAL),
            "forensic_region": normalize_enum(obj.get("forensic_region"), VALID_REGIONS),
            "evidence": obj.get("evidence") if isinstance(obj.get("evidence"), list) else [],
        }
        try:
            validate_target(obj)
            valid_schema = True
        except Exception:
            valid_schema = False
    if pred["final_news_verdict"] == "unknown" and pred["image_verdict"] in VALID_IMAGE_VERDICTS and pred["text_image_relation"] in VALID_RELATIONS:
        pred["final_news_verdict"] = (
            "fake_news"
            if pred["image_verdict"] == "tampered" or pred["text_image_relation"] == "mismatched"
            else "credible"
        )
    return {
        "raw": raw,
        "valid_json": valid_json,
        "valid_schema": valid_schema,
        "parse_error": error,
        "parsed": obj,
        "pred": pred,
    }


def target_from_manifest(row: dict[str, Any]) -> dict[str, Any]:
    if isinstance(row.get("target"), dict):
        return validate_target(dict(row["target"]))
    return validate_target({key: row[key] for key in TARGET_KEYS})


def load_eval_rows(data_path: Path, manifest_path: Path, limit: int | None) -> list[dict[str, Any]]:
    data_rows = load_jsonl(data_path)
    manifest_rows = load_jsonl(manifest_path)
    if len(data_rows) != len(manifest_rows):
        raise ValueError("data and manifest row counts differ")
    rows: list[dict[str, Any]] = []
    for idx, (data, manifest) in enumerate(zip(data_rows, manifest_rows)):
        if data["id"] != manifest["id"]:
            raise ValueError(f"row {idx}: id mismatch")
        images = data.get("images")
        messages = data.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: expected one image")
        image = Path(str(images[0]))
        if not image.exists():
            raise FileNotFoundError(image)
        gt_mask = manifest.get("gt_mask")
        rows.append(
            {
                "index": idx,
                "id": data["id"],
                "image": str(image),
                "prompt": str(messages[0]["content"]),
                "manifest": manifest,
                "target": target_from_manifest(manifest),
                "gt_mask": str(gt_mask) if gt_mask else None,
                "cell": manifest.get("cell"),
            }
        )
    if limit is not None:
        rows = rows[:limit]
    return rows


def load_model(args: argparse.Namespace):
    import torch
    from peft import PeftModel
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    local_files_only = not args.allow_network
    device = args.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.dtype]
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=local_files_only)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    return torch, process_vision_info, processor, model, device


def infer_batch(
    torch_mod,
    process_vision_info,
    processor,
    model,
    device: str,
    batch: list[dict[str, Any]],
    max_new_tokens: int,
    max_pixels: int | None,
) -> list[str]:
    messages_list = []
    for row in batch:
        image = {"type": "image", "image": row["image"]}
        if max_pixels is not None:
            image["max_pixels"] = max_pixels
        prompt = str(row["prompt"]).replace("<image>", "").strip()
        messages_list.append([{"role": "user", "content": [image, {"type": "text", "text": prompt}]}])
    texts = [processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) for messages in messages_list]
    image_inputs_list = []
    video_inputs_list = []
    for messages in messages_list:
        image_inputs, video_inputs = process_vision_info(messages)
        image_inputs_list.extend(image_inputs or [])
        if video_inputs:
            video_inputs_list.extend(video_inputs)
    inputs = processor(
        text=texts,
        images=image_inputs_list or None,
        videos=video_inputs_list or None,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch_mod.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)


def run_inference(args: argparse.Namespace, rows: list[dict[str, Any]], records: dict[str, dict[str, Any]]) -> None:
    pending = [row for row in rows if row["id"] not in records]
    if not pending:
        return
    model_bundle = load_model(args)
    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        labels = ", ".join(f"{row['id']}:{row['cell']}" for row in batch)
        print(f"infer batch {start + 1}-{start + len(batch)}/{len(pending)} [{labels}]", flush=True)
        raw_outputs = infer_batch(*model_bundle, batch, args.max_new_tokens, args.max_pixels)
        for row, raw in zip(batch, raw_outputs):
            records[row["id"]] = {
                "id": row["id"],
                "index": row["index"],
                "image": row["image"],
                "cell": row["cell"],
                "target": row["target"],
                "prediction": parse_prediction(raw.strip()),
            }
        write_all(args.output_jsonl, records)


def bool_mask_from_box(width: int, height: int, box: list[int] | None) -> np.ndarray:
    mask = np.zeros((height, width), dtype=bool)
    if box is None:
        return mask
    x0, y0, x1, y1 = box
    x0 = max(0, min(width, int(x0)))
    x1 = max(0, min(width, int(x1)))
    y0 = max(0, min(height, int(y0)))
    y1 = max(0, min(height, int(y1)))
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = True
    return mask


def detect_face_box(image_path: Path) -> dict[str, Any]:
    import cv2

    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade_path = str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(24, 24))
    if len(faces):
        x, y, w, h = max(faces, key=lambda item: int(item[2]) * int(item[3]))
        return {
            "box_xyxy": [int(x), int(y), int(x + w), int(y + h)],
            "source": "opencv_haar",
            "face_count": int(len(faces)),
            "fallback_reason": None,
        }
    return {
        "box_xyxy": [
            int(round(0.18 * width)),
            int(round(0.08 * height)),
            int(round(0.82 * width)),
            int(round(0.92 * height)),
        ],
        "source": "center_face_prior",
        "face_count": 0,
        "fallback_reason": "face_detector_failed_center_prior",
    }


def load_gt_mask(path: str | None, width: int, height: int) -> np.ndarray:
    if not path:
        return np.zeros((height, width), dtype=bool)
    with Image.open(path) as image:
        mask = image.convert("L")
        if mask.size != (width, height):
            mask = mask.resize((width, height), Image.Resampling.NEAREST)
        return np.asarray(mask) > 0


def mask_metrics(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    pred_sum = int(pred.sum())
    truth_sum = int(truth.sum())
    tp = int(np.logical_and(pred, truth).sum())
    union = int(np.logical_or(pred, truth).sum())
    precision = tp / pred_sum if pred_sum else (1.0 if truth_sum == 0 else 0.0)
    recall = tp / truth_sum if truth_sum else (1.0 if pred_sum == 0 else 0.0)
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    iou = tp / union if union else 1.0
    return {
        "iou": iou,
        "pixel_f1": f1,
        "pixel_precision": precision,
        "pixel_recall": recall,
        "pred_pixels": float(pred_sum),
        "truth_pixels": float(truth_sum),
    }


def add_region_metrics(records: dict[str, dict[str, Any]], rows_by_id: dict[str, dict[str, Any]], pred_mask_dir: Path | None) -> None:
    for record in records.values():
        row = rows_by_id.get(record["id"])
        if row is None:
            continue
        pred = record["prediction"]["pred"]
        with Image.open(row["image"]) as image:
            width, height = image.size
        box_info = None
        if pred["image_verdict"] == "tampered" and pred["tamper_domain"] == "deepfake":
            box_info = detect_face_box(Path(row["image"]))
            pred_mask = bool_mask_from_box(width, height, box_info["box_xyxy"])
        else:
            pred_mask = bool_mask_from_box(width, height, None)
        truth_mask = load_gt_mask(row.get("gt_mask"), width, height)
        metrics = mask_metrics(pred_mask, truth_mask)
        if pred_mask_dir is not None:
            pred_mask_dir.mkdir(parents=True, exist_ok=True)
            mask_path = pred_mask_dir / f"{record['id']}.png"
            Image.fromarray(pred_mask.astype(np.uint8) * 255).save(mask_path)
            metrics["pred_mask"] = str(mask_path)
        record["region_prediction"] = box_info or {"box_xyxy": [], "source": "empty_mask"}
        record["region_metrics"] = metrics


def safe_div(num: int | float, den: int | float) -> float | None:
    return float(num) / float(den) if den else None


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def predicted_cell(pred: dict[str, Any]) -> str:
    if pred["image_verdict"] in VALID_IMAGE_VERDICTS and pred["text_image_relation"] in VALID_RELATIONS:
        return f"{pred['image_verdict']}_{pred['text_image_relation']}"
    return UNKNOWN_CELL


def metric_payload(correct: int, total: int) -> dict[str, Any]:
    return {"correct": correct, "total": total, "value": safe_div(correct, total)}


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    valid_json = sum(bool(record["prediction"]["valid_json"]) for record in records)
    valid_schema = sum(bool(record["prediction"]["valid_schema"]) for record in records)
    image_correct = 0
    relation_correct = 0
    final_correct = 0
    exact_correct = 0
    tampered = []
    authentic = []
    consistent = []
    mismatched = []
    confusion: dict[str, Counter] = defaultdict(Counter)
    cell_stats: dict[str, Counter] = defaultdict(Counter)

    for record in records:
        target = record["target"]
        pred = record["prediction"]["pred"]
        image_hit = pred["image_verdict"] == target["image_verdict"]
        relation_hit = pred["text_image_relation"] == target["text_image_relation"]
        final_hit = pred["final_news_verdict"] == target["final_news_verdict"]
        exact_hit = image_hit and relation_hit and final_hit
        image_correct += int(image_hit)
        relation_correct += int(relation_hit)
        final_correct += int(final_hit)
        exact_correct += int(exact_hit)
        if target["image_verdict"] == "tampered":
            tampered.append(record)
        else:
            authentic.append(record)
        if target["text_image_relation"] == "consistent":
            consistent.append(record)
        else:
            mismatched.append(record)
        truth_cell = f"{target['image_verdict']}_{target['text_image_relation']}"
        pred_cell = predicted_cell(pred)
        confusion[truth_cell][pred_cell] += 1
        cell_stats[truth_cell]["total"] += 1
        cell_stats[truth_cell]["final_correct"] += int(final_hit)
        cell_stats[truth_cell]["exact_correct"] += int(exact_hit)

    relation_consistent = sum(r["prediction"]["pred"]["text_image_relation"] == "consistent" for r in consistent)
    relation_mismatched = sum(r["prediction"]["pred"]["text_image_relation"] == "mismatched" for r in mismatched)
    deepfake_recall = sum(r["prediction"]["pred"]["image_verdict"] == "tampered" for r in tampered)
    ffhq_auth = sum(r["prediction"]["pred"]["image_verdict"] == "authentic" for r in authentic)

    faceapp_region = [r for r in records if r["target"]["image_verdict"] == "tampered" and "region_metrics" in r]
    ffhq_region = [r for r in records if r["target"]["image_verdict"] == "authentic" and "region_metrics" in r]
    ffhq_empty = sum(int(r["region_metrics"]["pred_pixels"] == 0) for r in ffhq_region)
    ffhq_fp = sum(int(r["region_metrics"]["pred_pixels"] > 0) for r in ffhq_region)

    cell_payload = {}
    for cell, counts in sorted(cell_stats.items()):
        total_cell = counts["total"]
        cell_payload[cell] = {
            "total": total_cell,
            "final_accuracy": safe_div(counts["final_correct"], total_cell),
            "exact_core_accuracy": safe_div(counts["exact_correct"], total_cell),
        }

    return {
        "n": total,
        "json": {
            "valid_json": metric_payload(valid_json, total),
            "valid_schema": metric_payload(valid_schema, total),
        },
        "image_forensics": {
            "image_verdict_accuracy": metric_payload(image_correct, total),
            "deepfake_recall": metric_payload(deepfake_recall, len(tampered)),
            "ffhq_authentic_accuracy": metric_payload(ffhq_auth, len(authentic)),
        },
        "text_image_relation": {
            "accuracy": metric_payload(relation_correct, total),
            "consistent_accuracy": metric_payload(relation_consistent, len(consistent)),
            "mismatched_accuracy": metric_payload(relation_mismatched, len(mismatched)),
            "balanced_accuracy": {
                "value": avg(
                    [
                        value
                        for value in [
                            safe_div(relation_consistent, len(consistent)),
                            safe_div(relation_mismatched, len(mismatched)),
                        ]
                        if value is not None
                    ]
                )
            },
        },
        "joint_decision": {
            "final_news_verdict_accuracy": metric_payload(final_correct, total),
            "exact_core_accuracy": metric_payload(exact_correct, total),
            "four_cell_confusion": {cell: dict(values) for cell, values in sorted(confusion.items())},
            "per_cell_accuracy": cell_payload,
        },
        "region_evidence": {
            "faceapp_tampered_iou": avg([float(r["region_metrics"]["iou"]) for r in faceapp_region]),
            "faceapp_tampered_pixel_f1": avg([float(r["region_metrics"]["pixel_f1"]) for r in faceapp_region]),
            "ffhq_empty_mask_accuracy": metric_payload(ffhq_empty, len(ffhq_region)),
            "ffhq_fp_mask_rate": metric_payload(ffhq_fp, len(ffhq_region)),
        },
    }


def fmt_metric(payload: dict[str, Any] | None) -> str:
    if not payload:
        return "n/a"
    value = payload.get("value")
    if value is None:
        return "n/a"
    if "correct" in payload and "total" in payload:
        return f"{value:.4f} ({payload['correct']}/{payload['total']})"
    return f"{value:.4f}"


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Stage2 DeepFake News Evaluation",
        "",
        f"- total: `{summary['n']}`",
        f"- valid JSON: `{fmt_metric(summary['json']['valid_json'])}`",
        f"- valid schema: `{fmt_metric(summary['json']['valid_schema'])}`",
        f"- image verdict accuracy: `{fmt_metric(summary['image_forensics']['image_verdict_accuracy'])}`",
        f"- DeepFake recall: `{fmt_metric(summary['image_forensics']['deepfake_recall'])}`",
        f"- FFHQ authentic accuracy: `{fmt_metric(summary['image_forensics']['ffhq_authentic_accuracy'])}`",
        f"- relation accuracy: `{fmt_metric(summary['text_image_relation']['accuracy'])}`",
        f"- relation balanced accuracy: `{fmt_metric(summary['text_image_relation']['balanced_accuracy'])}`",
        f"- final news verdict accuracy: `{fmt_metric(summary['joint_decision']['final_news_verdict_accuracy'])}`",
        f"- exact core accuracy: `{fmt_metric(summary['joint_decision']['exact_core_accuracy'])}`",
        f"- FaceApp tampered IoU: `{summary['region_evidence']['faceapp_tampered_iou']}`",
        f"- FaceApp tampered pixel F1: `{summary['region_evidence']['faceapp_tampered_pixel_f1']}`",
        f"- FFHQ empty-mask accuracy: `{fmt_metric(summary['region_evidence']['ffhq_empty_mask_accuracy'])}`",
        f"- FFHQ FP-mask rate: `{fmt_metric(summary['region_evidence']['ffhq_fp_mask_rate'])}`",
        "",
        "## Four-Cell Accuracy",
        "",
        "| cell | final_accuracy | exact_core_accuracy | n |",
        "|---|---:|---:|---:|",
    ]
    for cell, payload in summary["joint_decision"]["per_cell_accuracy"].items():
        lines.append(
            f"| `{cell}` | {payload['final_accuracy']:.4f} | {payload['exact_core_accuracy']:.4f} | {payload['total']} |"
        )
    lines.extend(["", "## Four-Cell Confusion", "", "```json", json.dumps(summary["joint_decision"]["four_cell_confusion"], ensure_ascii=False, indent=2), "```"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    rows = load_eval_rows(args.data, args.manifest, args.limit)
    records = {row["id"]: row for row in load_jsonl(args.output_jsonl)} if args.resume else {}
    if not args.resume and args.output_jsonl.exists():
        args.output_jsonl.unlink()
        records = {}
    if not args.skip_infer:
        run_inference(args, rows, records)
    rows_by_id = {row["id"]: row for row in rows}
    add_region_metrics(records, rows_by_id, args.pred_mask_dir)
    write_all(args.output_jsonl, records)
    summary = summarize(list(records.values()))
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_md(args.summary_md, summary)
    print("wrote", args.output_jsonl)
    print("wrote", args.summary_json)
    print("wrote", args.summary_md)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Stage2 DeepFake-news title/body/image predictions.")
    parser.add_argument("--data", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_json/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_json/manifest.jsonl"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/eval/stage2_deepfake_news_predictions.jsonl"))
    parser.add_argument("--summary-json", type=Path, default=Path("artifacts/eval/stage2_deepfake_news_summary.json"))
    parser.add_argument("--summary-md", type=Path, default=Path("artifacts/eval/stage2_deepfake_news_summary.md"))
    parser.add_argument("--pred-mask-dir", type=Path)
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--adapter", default="artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_json")
    parser.add_argument("--device")
    parser.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-new-tokens", type=int, default=192)
    parser.add_argument("--max-pixels", type=int, default=524288)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-infer", action="store_true", help="Only summarize an existing prediction JSONL.")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")
    return args


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
