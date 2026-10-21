#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from eval_stage1_multisource import extract_json_object, normalize_domain


FULL_PROMPT = (
    "Analyze whether this image has been digitally manipulated. "
    "The first image is the full image and the second image is a crop around the provided region. "
    "Return only valid JSON with verdict, tampered_region, tamper_domain, evidence, and region_focus."
)
COMPACT_PROMPT = (
    "Analyze whether this image has been digitally manipulated. "
    "The first image is the full image and the second image is a crop around the provided region. "
    "Return only valid compact JSON with exactly these keys: verdict and tamper_domain. "
    'Use verdict "authentic" or "tampered"; use tamper_domain "none", '
    '"photoshop", "deepfake", or "aigc_inpaint".'
)

VALID_VERDICTS = {"authentic", "tampered"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_existing(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["id"])] = row
    return rows


def write_all(path: Path, records: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for key in sorted(records):
            f.write(json.dumps(records[key], ensure_ascii=False) + "\n")
    tmp.replace(path)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def clamp_box(box: list[int], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(width - 1, x0))
    y0 = max(0, min(height - 1, y0))
    x1 = max(x0 + 1, min(width, x1))
    y1 = max(y0 + 1, min(height, y1))
    return [x0, y0, x1, y1]


def expand_box(box: list[int], width: int, height: int, scale: float) -> list[int]:
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    bw = max(1.0, (x1 - x0) * scale)
    bh = max(1.0, (y1 - y0) * scale)
    return clamp_box(
        [
            round(cx - bw / 2.0),
            round(cy - bh / 2.0),
            round(cx + bw / 2.0),
            round(cy + bh / 2.0),
        ],
        width,
        height,
    )


def make_crop(image_path: Path, crop_path: Path, box: list[int]) -> None:
    if crop_path.exists():
        return
    crop_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image.crop(tuple(box)).save(crop_path, quality=95)


def parse_scales(text: str) -> list[float]:
    values = [float(item.strip()) for item in text.split(",") if item.strip()]
    if not values:
        raise ValueError("--crop-scales must contain at least one value")
    for value in values:
        if value <= 0:
            raise ValueError(f"crop scale must be positive: {value}")
    return values


def parse_patch_output(raw: str) -> dict[str, Any]:
    obj, error = extract_json_object(raw)
    verdict = "unknown"
    domain = "unknown"
    if obj is not None:
        raw_verdict = str(obj.get("verdict", "")).strip().lower()
        if raw_verdict in VALID_VERDICTS:
            verdict = raw_verdict
        elif raw_verdict in {"yes", "manipulated", "possibly manipulated"}:
            verdict = "tampered"
        elif raw_verdict in {"no", "genuine", "not tampered"}:
            verdict = "authentic"
        domain = normalize_domain(obj.get("tamper_domain"))
    if verdict == "unknown":
        verdict_match = re.search(r'"verdict"\s*:\s*"([^"]+)"', raw, flags=re.IGNORECASE)
        if verdict_match:
            raw_verdict = verdict_match.group(1).strip().lower()
            if raw_verdict in VALID_VERDICTS:
                verdict = raw_verdict
    if domain == "unknown":
        domain_match = re.search(r'"tamper_domain"\s*:\s*"([^"]+)"', raw, flags=re.IGNORECASE)
        if domain_match:
            domain = normalize_domain(domain_match.group(1))
    if verdict == "unknown":
        lowered = raw.lower()
        if "not tampered" in lowered or "authentic" in lowered:
            verdict = "authentic"
        elif "tampered" in lowered or "manipulated" in lowered:
            verdict = "tampered"
    if domain == "unknown":
        domain = normalize_domain(raw)
    valid_json = obj is not None
    valid_vote_fields = verdict in VALID_VERDICTS and domain in {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}
    return {
        "raw": raw,
        "valid_json": valid_json,
        "valid_vote_fields": valid_vote_fields,
        "parse_error": error,
        "parsed": obj,
        "predicted_verdict": verdict,
        "predicted_domain": domain,
        "photoshop_vote": bool(verdict == "tampered" and domain == "photoshop"),
    }


def image_content(path: str, max_pixels: int | None) -> dict[str, Any]:
    content: dict[str, Any] = {"type": "image", "image": path}
    if max_pixels is not None:
        content["max_pixels"] = max_pixels
    return content


def infer_batch(
    model,
    processor,
    batch: list[dict[str, Any]],
    prompt: str,
    device: str,
    max_new_tokens: int,
    max_pixels: int | None,
) -> list[str]:
    messages_list = [
        [
            {
                "role": "user",
                "content": [
                    image_content(str(item["full_image"]), max_pixels),
                    image_content(str(item["crop_image"]), max_pixels),
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        for item in batch
    ]
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
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)


def load_model(base_model: str, adapter: str, dtype: torch.dtype, device: str):
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
        local_files_only=True,
    )
    model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model


def prepare_views(row: dict[str, Any], crop_root: Path, scales: list[float]) -> list[dict[str, Any]]:
    image_path = Path(row["resolved_image"])
    width = int(row.get("image_width") or Image.open(image_path).size[0])
    height = int(row.get("image_height") or Image.open(image_path).size[1])
    bbox = row.get("gt_bbox") or row.get("bbox_xyxy")
    if not bbox:
        raise ValueError(f"{row['id']}: missing gt_bbox/bbox_xyxy")

    views = []
    for scale in scales:
        box = expand_box([int(v) for v in bbox], width, height, scale)
        crop_path = crop_root / str(row["domain"]) / f"{safe_name(str(row['id']))}_bbox_{scale:.2f}.jpg"
        make_crop(image_path, crop_path, box)
        views.append(
            {
                "sample_id": row["id"],
                "scale": scale,
                "crop_box_xyxy": box,
                "full_image": image_path,
                "crop_image": crop_path,
            }
        )
    return views


def aggregate_views(row: dict[str, Any], view_records: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [item for item in view_records if item["valid_vote_fields"]]
    votes = sum(1 for item in valid if item["photoshop_vote"])
    score = votes / len(valid) if valid else 0.0
    domains = [item["predicted_domain"] for item in view_records]
    verdicts = [item["predicted_verdict"] for item in view_records]
    return {
        "id": row["id"],
        "domain": row["domain"],
        "source_dataset": row.get("source_dataset") or row.get("source"),
        "image": row["image"],
        "resolved_image": row["resolved_image"],
        "bbox_xyxy": row.get("gt_bbox") or row.get("bbox_xyxy"),
        "photoshop_patch_score": score,
        "photoshop_votes": votes,
        "valid_views": len(valid),
        "total_views": len(view_records),
        "invalid_patch_outputs": len(view_records) - len(valid),
        "view_predicted_domains": domains,
        "view_predicted_verdicts": verdicts,
        "views": view_records,
    }


def run(args: argparse.Namespace) -> None:
    rows = load_jsonl(args.samples)
    if args.only_domain:
        rows = [row for row in rows if str(row.get("domain")) == args.only_domain]
    if args.limit is not None:
        rows = rows[: args.limit]
    scales = parse_scales(args.crop_scales)
    records = load_existing(args.output_jsonl) if args.resume else {}
    if not args.resume and args.output_jsonl.exists():
        args.output_jsonl.unlink()

    pending_rows = [row for row in rows if str(row["id"]) not in records]
    view_items: list[dict[str, Any]] = []
    row_views: dict[str, list[dict[str, Any]]] = {}
    for row in pending_rows:
        views = prepare_views(row, args.crop_root, scales)
        row_views[str(row["id"])] = views
        view_items.extend(views)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=True)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"
    model = load_model(args.base_model, args.adapter, dtype, device)
    prompt = COMPACT_PROMPT if args.prompt_mode == "compact" else FULL_PROMPT

    parsed_by_sample: dict[str, list[dict[str, Any]]] = {key: [] for key in row_views}
    for start in range(0, len(view_items), args.batch_size):
        batch = view_items[start : start + args.batch_size]
        labels = ", ".join(f"{item['sample_id']}@{item['scale']:.2f}" for item in batch)
        print(f"infer patch batch {start + 1}-{start + len(batch)}/{len(view_items)} [{labels}]", flush=True)
        outputs = infer_batch(model, processor, batch, prompt, device, args.max_new_tokens, args.max_pixels)
        for item, raw in zip(batch, outputs):
            parsed = parse_patch_output(raw.strip())
            view_record = {
                "scale": item["scale"],
                "crop_box_xyxy": item["crop_box_xyxy"],
                "crop_image": str(item["crop_image"]),
                **parsed,
            }
            parsed_by_sample[str(item["sample_id"])].append(view_record)

    rows_by_id = {str(row["id"]): row for row in pending_rows}
    with args.output_jsonl.open("a", encoding="utf-8") as f:
        for sample_id in sorted(parsed_by_sample):
            record = aggregate_views(rows_by_id[sample_id], parsed_by_sample[sample_id])
            record["prompt_mode"] = args.prompt_mode
            records[sample_id] = record
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()

    write_all(args.output_jsonl, records)
    print("wrote_jsonl", args.output_jsonl, flush=True)
    print("records", len(records), flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score Photoshop routing with full image + GT-bbox crop patch expert.")
    parser.add_argument("--samples", type=Path, default=Path("artifacts/region_eval/region_eval_p150/samples.jsonl"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/region_eval/region_eval_p150/photoshop_patch_predictions.jsonl"))
    parser.add_argument("--crop-root", type=Path, default=Path("artifacts/region_eval/region_eval_p150/patch_crops"))
    parser.add_argument("--base-model", default="/home/Master/CaoMJ/.cache/huggingface/hub/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/66285546d2b821cf421d4f5eb2576359d3770cd3")
    parser.add_argument("--adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_photoshop_crop_json")
    parser.add_argument("--crop-scales", default="1.00,1.25,1.50")
    parser.add_argument("--only-domain", choices=["photoshop", "deepfake", "aigc_editing"])
    parser.add_argument("--prompt-mode", choices=["compact", "full"], default="compact")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--max-pixels", type=int, default=524288)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")
    run(args)


if __name__ == "__main__":
    main()
