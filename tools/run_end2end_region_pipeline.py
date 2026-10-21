#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import cv2
import numpy as np
import torch
from peft import PeftModel
from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from eval_region_grounding_p60 import build_sam_runner, read_rgb_image
from eval_stage1_multisource import extract_json_object, normalize_domain, parse_prediction


GLOBAL_PROMPT = (
    "Analyze whether this image has been digitally manipulated. "
    "Return only valid compact JSON with exactly these keys: verdict and tamper_domain. "
    'Use verdict "authentic" or "tampered"; use tamper_domain "none", "photoshop", "deepfake", or "aigc_inpaint".'
)

PROPOSAL_PROMPT = (
    "The first image is the full image and the second image is a candidate crop from it. "
    "Decide whether the crop itself contains manipulated pixels from the full image. "
    "Return only valid compact JSON with exactly these keys: crop_tampered, tamper_domain, and crop_role. "
    'Use crop_tampered true or false; use tamper_domain "none", "photoshop", "deepfake", or "aigc_inpaint".'
)

FORBIDDEN_PIPELINE_KEYS = {"label", "verdict", "tamper_domain", "gt_mask", "gt_bbox", "mask", "mask_member", "resolved_gt_mask", "resolved_mask"}
GLOBAL_REQUIRED_KEYS = {"verdict", "tamper_domain"}
GLOBAL_FULL_KEYS = {"verdict", "tampered_region", "tamper_domain", "evidence"}
VALID_VERDICTS = {"authentic", "tampered"}
VALID_DOMAINS = {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}


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


def load_model(base_model: str, adapter: str | None, dtype: torch.dtype, device: str):
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
        local_files_only=True,
    )
    if adapter:
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model


def image_content(path: str, max_pixels: int | None) -> dict[str, Any]:
    payload: dict[str, Any] = {"type": "image", "image": path}
    if max_pixels is not None:
        payload["max_pixels"] = max_pixels
    return payload


def infer_batch(
    model,
    processor,
    messages_list: list[list[dict[str, Any]]],
    device: str,
    max_new_tokens: int,
) -> list[str]:
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


def global_messages(row: dict[str, Any], max_pixels: int | None) -> list[dict[str, Any]]:
    return [{"role": "user", "content": [image_content(row["resolved_image"], max_pixels), {"type": "text", "text": GLOBAL_PROMPT}]}]


def proposal_messages(full_image: str, crop_image: str, max_pixels: int | None) -> list[dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": [
                image_content(full_image, max_pixels),
                image_content(crop_image, max_pixels),
                {"type": "text", "text": PROPOSAL_PROMPT},
            ],
        }
    ]


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "yes", "1", "tampered", "manipulated"}:
        return True
    if text in {"false", "no", "0", "authentic", "clean"}:
        return False
    return None


def parse_proposal_output(raw: str) -> dict[str, Any]:
    obj, error = extract_json_object(raw)
    crop_tampered = None
    domain = "unknown"
    role = "unknown"
    valid_schema = False
    if obj is not None:
        crop_tampered = parse_bool(obj.get("crop_tampered"))
        domain = normalize_domain(obj.get("tamper_domain"))
        role = str(obj.get("crop_role", "unknown")).strip().lower()
        valid_schema = (
            set(obj) == {"crop_tampered", "tamper_domain", "crop_role"}
            and crop_tampered is not None
            and domain in {"none", "photoshop", "deepfake", "aigc_inpaint"}
            and role in {"positive_region", "hard_negative", "adjacent_distractor", "authentic_negative"}
        )
    if crop_tampered is None:
        lowered = raw.lower()
        if "true" in lowered or "tampered" in lowered or "manipulated" in lowered:
            crop_tampered = True
        elif "false" in lowered or "authentic" in lowered or "clean" in lowered:
            crop_tampered = False
    if domain == "unknown":
        domain = normalize_domain(raw)
    return {
        "raw": raw,
        "valid_json": obj is not None,
        "valid_schema": valid_schema,
        "parse_error": error,
        "parsed": obj,
        "crop_tampered": bool(crop_tampered) if crop_tampered is not None else False,
        "pred_tamper_domain": domain,
        "crop_role": role,
    }


def global_schema_issue(prediction: dict[str, Any]) -> str | None:
    if prediction.get("valid_schema"):
        return None
    raw = str(prediction.get("raw") or "")
    if not raw.strip():
        return "empty_raw"
    parsed = prediction.get("parsed")
    if parsed is None:
        return "invalid_json"
    keys = set(parsed)
    if keys not in {GLOBAL_REQUIRED_KEYS, GLOBAL_FULL_KEYS}:
        return "bad_keys:" + ",".join(sorted(keys))
    verdict = str(parsed.get("verdict", "")).strip().lower()
    if verdict not in VALID_VERDICTS:
        return "bad_verdict:" + (verdict or "missing")
    domain = normalize_domain(parsed.get("tamper_domain"))
    if domain not in VALID_DOMAINS:
        return "bad_domain:" + str(parsed.get("tamper_domain", "missing"))
    if keys == GLOBAL_FULL_KEYS and (not isinstance(parsed.get("tampered_region"), str) or not isinstance(parsed.get("evidence"), list)):
        return "bad_full_payload"
    return "invalid_schema_unknown"


def role_weight(parsed: dict[str, Any]) -> float:
    role = str(parsed.get("crop_role") or "unknown")
    return {
        "positive_region": 1.0,
        "adjacent_distractor": 0.35,
        "hard_negative": 0.2,
        "authentic_negative": 0.0,
        "unknown": 0.5,
    }.get(role, 0.5)


def domain_patch_score(parsed: dict[str, Any], domain: str) -> float:
    if not parsed.get("crop_tampered"):
        return 0.0
    pred_domain = str(parsed.get("pred_tamper_domain"))
    if pred_domain != domain:
        return 0.0
    return role_weight(parsed)


def proposal_score(parsed: dict[str, Any], routed_domain: str) -> float:
    if not parsed.get("crop_tampered"):
        return 0.0
    pred_domain = str(parsed.get("pred_tamper_domain"))
    weight = role_weight(parsed)
    if pred_domain == routed_domain:
        return weight
    if pred_domain in {"photoshop", "deepfake", "aigc_inpaint"}:
        return 0.7 * weight
    return 0.0


def proposal_domain_scores(parsed: dict[str, Any]) -> dict[str, float]:
    return {
        "photoshop": domain_patch_score(parsed, "photoshop"),
        "aigc_inpaint": domain_patch_score(parsed, "aigc_inpaint"),
        "deepfake": domain_patch_score(parsed, "deepfake"),
    }


def sam_cache_score(item: dict[str, Any]) -> float:
    domain_scores = item.get("domain_scores") or {}
    values = [float(item.get("proposal_score", 0.0))]
    values.extend(float(domain_scores.get(domain, 0.0)) for domain in ("photoshop", "aigc_inpaint", "deepfake"))
    values.extend(float(item.get(key, 0.0)) for key in ("photoshop_patch_score", "aigc_patch_score", "deepfake_patch_score"))
    return max(values)


def sliding_window_boxes(width: int, height: int, scales: list[float]) -> list[dict[str, Any]]:
    short = min(width, height)
    proposals: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int, int]] = set()
    for scale in scales:
        side = max(8, min(width, height, int(round(short * scale))))
        stride = max(1, side // 2)
        xs = list(range(0, max(1, width - side + 1), stride))
        ys = list(range(0, max(1, height - side + 1), stride))
        if not xs or xs[-1] != width - side:
            xs.append(max(0, width - side))
        if not ys or ys[-1] != height - side:
            ys.append(max(0, height - side))
        for y0 in sorted(set(ys)):
            for x0 in sorted(set(xs)):
                box = (x0, y0, x0 + side, y0 + side)
                if box in seen:
                    continue
                seen.add(box)
                proposals.append({"box_xyxy": list(box), "scale": scale})
    return proposals


def make_crop(image_path: Path, crop_path: Path, box: list[int]) -> None:
    crop_path.parent.mkdir(parents=True, exist_ok=True)
    if crop_path.exists():
        return
    with Image.open(image_path) as image:
        image.convert("RGB").crop(tuple(box)).save(crop_path, quality=95)


def save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask.astype(np.uint8) * 255).save(path)


def box_area(box: list[int]) -> int:
    return max(0, int(box[2]) - int(box[0])) * max(0, int(box[3]) - int(box[1]))


def detect_face_box(image_path: Path) -> dict[str, Any]:
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
            "fallback_reason": None,
            "face_count": int(len(faces)),
            "face_score": 1.0,
        }
    box = [
        int(round(0.18 * width)),
        int(round(0.08 * height)),
        int(round(0.82 * width)),
        int(round(0.92 * height)),
    ]
    return {
        "box_xyxy": box,
        "source": "center_face_prior",
        "fallback_reason": "face_detector_failed_center_prior",
        "face_count": 0,
        "face_score": 0.25,
    }


def validate_pipeline_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        leaked = FORBIDDEN_PIPELINE_KEYS & set(row)
        if leaked:
            raise ValueError(f"{row.get('id')}: pipeline manifest leaked forbidden keys {sorted(leaked)}")
        if not Path(row["resolved_image"]).exists():
            raise FileNotFoundError(row["resolved_image"])


def maybe_limit(rows: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None:
        return rows
    return rows[:limit]


def reusable_region_record(reuse_record: dict[str, Any] | None, pred_domain: str) -> bool:
    if not reuse_record or not reuse_record.get("pipeline_complete"):
        return False
    if str(reuse_record.get("routed_domain", "unknown")) != pred_domain:
        return False
    if pred_domain == "deepfake":
        return bool(reuse_record.get("face_candidate"))
    if pred_domain in {"photoshop", "aigc_inpaint"}:
        return "raw_proposals" in reuse_record and "sam_candidates" in reuse_record
    return False


def reusable_all_tampered_record(reuse_record: dict[str, Any] | None, pred_domain: str) -> bool:
    if not reuse_record or not reuse_record.get("pipeline_complete"):
        return False
    if pred_domain == "deepfake":
        return bool(reuse_record.get("face_candidate"))
    if pred_domain in {"photoshop", "aigc_inpaint"}:
        return "raw_proposals" in reuse_record and "sam_candidates" in reuse_record
    return False


def reusable_all_images_record(reuse_record: dict[str, Any] | None) -> bool:
    if not reuse_record or not reuse_record.get("pipeline_complete"):
        return False
    return bool(reuse_record.get("raw_proposals")) and "sam_candidates" in reuse_record


def backfill_domain_scores(item: dict[str, Any], pred_domain: str) -> dict[str, Any]:
    parsed = item.get("proposal_prediction") or {}
    domain_scores = item.get("domain_scores")
    if not isinstance(domain_scores, dict):
        domain_scores = proposal_domain_scores(parsed)
    item["domain_scores"] = domain_scores
    item["photoshop_patch_score"] = float(item.get("photoshop_patch_score", domain_scores.get("photoshop", 0.0)))
    item["aigc_patch_score"] = float(item.get("aigc_patch_score", domain_scores.get("aigc_inpaint", 0.0)))
    item["deepfake_patch_score"] = float(item.get("deepfake_patch_score", domain_scores.get("deepfake", 0.0)))
    if "proposal_score" not in item:
        item["proposal_score"] = proposal_score(parsed, pred_domain)
    return item


def backfill_reused_region_record(record: dict[str, Any], pred_domain: str) -> dict[str, Any]:
    record["raw_proposals"] = [backfill_domain_scores(item, pred_domain) for item in (record.get("raw_proposals") or [])]
    raw_by_index = {int(item["index"]): item for item in record["raw_proposals"] if "index" in item}
    filled_sam = []
    for item in record.get("sam_candidates") or []:
        source = raw_by_index.get(int(item.get("index", -1)), {})
        domain_scores = item.get("domain_scores") or source.get("domain_scores") or {}
        item["domain_scores"] = domain_scores
        item["photoshop_patch_score"] = float(item.get("photoshop_patch_score", source.get("photoshop_patch_score", domain_scores.get("photoshop", 0.0))))
        item["aigc_patch_score"] = float(item.get("aigc_patch_score", source.get("aigc_patch_score", domain_scores.get("aigc_inpaint", 0.0))))
        item["deepfake_patch_score"] = float(item.get("deepfake_patch_score", source.get("deepfake_patch_score", domain_scores.get("deepfake", 0.0))))
        filled_sam.append(item)
    record["sam_candidates"] = filled_sam
    face = record.get("face_candidate")
    if isinstance(face, dict) and "face_score" not in face:
        face["face_score"] = 1.0 if face.get("source") == "opencv_haar" else 0.25
    return record


def copy_reusable_region_fields(record: dict[str, Any], reuse_record: dict[str, Any], reuse_path: Path) -> dict[str, Any]:
    for key in ["raw_proposals", "sam_candidates", "face_candidate", "fallback_reason", "sam_status", "sam_reason"]:
        if key in reuse_record:
            record[key] = reuse_record[key]
    record["proposal_complete"] = True
    record["pipeline_complete"] = True
    record["region_reused_from"] = str(reuse_path)
    return record


def copy_reusable_all_tampered_fields(record: dict[str, Any], reuse_record: dict[str, Any], reuse_path: Path, pred_domain: str) -> dict[str, Any]:
    for key in ["raw_proposals", "sam_candidates", "face_candidate", "fallback_reason", "sam_status", "sam_reason"]:
        if key in reuse_record:
            record[key] = reuse_record[key]
    record = backfill_reused_region_record(record, pred_domain)
    record["proposal_complete"] = True
    record["pipeline_complete"] = True
    record["region_reused_from"] = str(reuse_path)
    return record


def run_global_predictions(args: argparse.Namespace, rows: list[dict[str, Any]], records: dict[str, dict[str, Any]], processor, dtype: torch.dtype) -> None:
    pending = [row for row in rows if args.overwrite or str(row["id"]) not in records or "global_prediction" not in records[str(row["id"])]]
    if not pending:
        return
    model = load_model(args.base_model, args.domain_adapter, dtype, args.device)
    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        messages = [global_messages(row, args.max_pixels) for row in batch]
        outputs = infer_batch(model, processor, messages, args.device, args.max_new_tokens)
        for row, raw in zip(batch, outputs):
            record = records.get(str(row["id"]), {**row})
            record["global_prediction"] = parse_prediction(raw.strip())
            records[str(row["id"])] = record
        write_all(args.output_jsonl, records)
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def run_region_candidates(args: argparse.Namespace, rows: list[dict[str, Any]], records: dict[str, dict[str, Any]], processor, dtype: torch.dtype) -> None:
    reuse_records = load_existing(args.reuse_region_cache) if args.reuse_region_cache else {}
    model = load_model(args.base_model, args.proposal_adapter, dtype, args.device)
    scales = [float(item) for item in args.proposal_scales.split(",") if item.strip()]
    for row in rows:
        sample_id = str(row["id"])
        existing = records.get(sample_id, {})
        if not args.overwrite and (existing.get("pipeline_complete") or existing.get("proposal_complete")):
            continue
        record = records.get(sample_id, {**row})
        global_pred = record.get("global_prediction") or {}
        pred_verdict = str(global_pred.get("pred_verdict", "unknown"))
        pred_domain = str(global_pred.get("pred_tamper_domain", "unknown"))
        record["routed_domain"] = pred_domain
        record["region_routing"] = args.region_routing
        record["raw_proposals"] = []
        record["sam_candidates"] = []
        record["face_candidate"] = None
        record["fallback_reason"] = None
        record["proposal_complete"] = False
        record.pop("region_reused_from", None)

        if args.region_routing != "all_images" and (not bool(global_pred.get("valid_schema")) or pred_verdict != "tampered"):
            record["fallback_reason"] = "global_invalid_or_not_tampered"
            record["proposal_complete"] = True
            record["pipeline_complete"] = True
            records[sample_id] = record
            write_all(args.output_jsonl, records)
            continue

        image_path = Path(row["resolved_image"])
        width = int(row.get("image_width") or Image.open(image_path).size[0])
        height = int(row.get("image_height") or Image.open(image_path).size[1])

        reuse_record = reuse_records.get(sample_id)
        if args.region_routing == "global_domain" and reusable_region_record(reuse_record, pred_domain):
            record = copy_reusable_region_fields(record, reuse_record, args.reuse_region_cache)
            record["region_routing"] = args.region_routing
            records[sample_id] = record
            write_all(args.output_jsonl, records)
            continue
        if args.region_routing == "all_tampered" and reusable_all_tampered_record(reuse_record, pred_domain):
            record = copy_reusable_all_tampered_fields(record, reuse_record, args.reuse_region_cache, pred_domain)
            record["region_routing"] = args.region_routing
            records[sample_id] = record
            write_all(args.output_jsonl, records)
            continue
        if args.region_routing == "all_images" and reusable_all_images_record(reuse_record):
            record = copy_reusable_all_tampered_fields(record, reuse_record, args.reuse_region_cache, pred_domain)
            record["region_routing"] = args.region_routing
            records[sample_id] = record
            write_all(args.output_jsonl, records)
            continue

        if args.region_routing in {"all_tampered", "all_images"}:
            record["face_candidate"] = detect_face_box(image_path)
        else:
            if pred_domain == "deepfake":
                record["face_candidate"] = detect_face_box(image_path)
                record["proposal_complete"] = True
                record["pipeline_complete"] = True
                records[sample_id] = record
                write_all(args.output_jsonl, records)
                continue

            if pred_domain not in {"photoshop", "aigc_inpaint"}:
                record["fallback_reason"] = "unsupported_or_unknown_predicted_domain"
                record["proposal_complete"] = True
                record["pipeline_complete"] = True
                records[sample_id] = record
                write_all(args.output_jsonl, records)
                continue

        proposals = sliding_window_boxes(width, height, scales)
        proposal_items: list[dict[str, Any]] = []
        for idx, proposal in enumerate(proposals):
            crop_path = args.output_dir / "proposal_crops" / sample_id / f"crop_{idx:04d}.jpg"
            make_crop(image_path, crop_path, proposal["box_xyxy"])
            proposal_items.append({**proposal, "index": idx, "crop_path": str(crop_path)})

        for start in range(0, len(proposal_items), args.batch_size):
            batch = proposal_items[start : start + args.batch_size]
            messages = [proposal_messages(str(image_path), item["crop_path"], args.max_pixels) for item in batch]
            outputs = infer_batch(model, processor, messages, args.device, args.proposal_max_new_tokens)
            for item, raw in zip(batch, outputs):
                parsed = parse_proposal_output(raw.strip())
                score = proposal_score(parsed, pred_domain)
                domain_scores = proposal_domain_scores(parsed)
                record["raw_proposals"].append(
                    {
                        **item,
                        "proposal_score": score,
                        "domain_scores": domain_scores,
                        "photoshop_patch_score": domain_scores["photoshop"],
                        "aigc_patch_score": domain_scores["aigc_inpaint"],
                        "deepfake_patch_score": domain_scores["deepfake"],
                        "proposal_prediction": parsed,
                    }
                )

        record["proposal_complete"] = True
        record["pipeline_complete"] = False
        records[sample_id] = record
        write_all(args.output_jsonl, records)

    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    sam_runner, sam_status, sam_reason = build_sam_runner(args)
    for row in rows:
        sample_id = str(row["id"])
        record = records.get(sample_id)
        if record is None:
            continue
        record["sam_status"] = sam_status
        record["sam_reason"] = sam_reason
        if record.get("pipeline_complete"):
            records[sample_id] = record
            continue
        global_pred = record.get("global_prediction") or {}
        pred_verdict = str(global_pred.get("pred_verdict", "unknown"))
        pred_domain = str(global_pred.get("pred_tamper_domain", "unknown"))
        should_run_sam = (
            bool(global_pred.get("valid_schema"))
            and pred_verdict == "tampered"
            and (
                args.region_routing in {"all_tampered", "all_images"}
                or pred_domain in {"photoshop", "aigc_inpaint"}
            )
        )
        if args.region_routing == "all_images":
            should_run_sam = True
        if not should_run_sam:
            record["pipeline_complete"] = True
            records[sample_id] = record
            write_all(args.output_jsonl, records)
            continue

        image_path = Path(row["resolved_image"])
        width = int(row.get("image_width") or Image.open(image_path).size[0])
        height = int(row.get("image_height") or Image.open(image_path).size[1])
        image_rgb = read_rgb_image(image_path)
        if sam_runner is not None:
            for item in record["raw_proposals"]:
                if sam_cache_score(item) < args.sam_min_proposal_score:
                    continue
                box = [int(v) for v in item["box_xyxy"]]
                pred_mask, sam_score = sam_runner.predict(image_rgb, box)
                if pred_mask.shape != image_rgb.shape[:2]:
                    pred_mask = np.asarray(
                        Image.fromarray(pred_mask.astype(np.uint8) * 255).resize((width, height), Image.Resampling.NEAREST)
                    ) > 0
                mask_path = args.output_dir / "sam_candidate_masks" / sample_id / f"candidate_{int(item['index']):04d}.png"
                save_mask(pred_mask, mask_path)
                record["sam_candidates"].append(
                    {
                        "index": int(item["index"]),
                        "box_xyxy": box,
                        "proposal_score": float(item["proposal_score"]),
                        "domain_scores": item.get("domain_scores") or {},
                        "photoshop_patch_score": float(item.get("photoshop_patch_score", 0.0)),
                        "aigc_patch_score": float(item.get("aigc_patch_score", 0.0)),
                        "deepfake_patch_score": float(item.get("deepfake_patch_score", 0.0)),
                        "sam_score": sam_score,
                        "mask_area_pixels": int(pred_mask.sum()),
                        "mask_area_box_ratio": int(pred_mask.sum()) / float(max(1, box_area(box))),
                        "mask_path": str(mask_path),
                    }
                )
        record["pipeline_complete"] = True
        records[sample_id] = record
        write_all(args.output_jsonl, records)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def write_summary(args: argparse.Namespace, records: dict[str, dict[str, Any]]) -> None:
    rows = list(records.values())
    global_predictions = [row.get("global_prediction") or {} for row in rows]
    invalid_schema_reasons = Counter(
        reason
        for prediction in global_predictions
        for reason in [global_schema_issue(prediction)]
        if reason is not None
    )
    unknown_verdict_rows = [row for row in rows if str((row.get("global_prediction") or {}).get("pred_verdict", "missing")) == "unknown"]
    unknown_domain_rows = [row for row in rows if str((row.get("global_prediction") or {}).get("pred_tamper_domain", "missing")) == "unknown"]
    summary = {
        "name": args.output_dir.name,
        "pipeline_manifest": str(args.pipeline_manifest),
        "output_jsonl": str(args.output_jsonl),
        "n": len(rows),
        "completed": sum(bool(row.get("pipeline_complete")) for row in rows),
        "global_verdict_counts": {},
        "global_domain_counts": {},
        "global_valid_json_count": sum(bool(prediction.get("valid_json")) for prediction in global_predictions),
        "global_valid_schema_count": sum(bool(prediction.get("valid_schema")) for prediction in global_predictions),
        "global_empty_raw_count": sum(1 for prediction in global_predictions if not str(prediction.get("raw") or "").strip()),
        "global_parse_error_count": sum(1 for prediction in global_predictions if prediction.get("parse_error")),
        "global_invalid_schema_by_reason": dict(sorted(invalid_schema_reasons.items())),
        "global_unknown_verdict_by_source": dict(sorted(Counter(str(row.get("source", "missing")) for row in unknown_verdict_rows).items())),
        "global_unknown_verdict_by_source_domain": dict(sorted(Counter(str(row.get("source_domain", "missing")) for row in unknown_verdict_rows).items())),
        "global_unknown_domain_by_source": dict(sorted(Counter(str(row.get("source", "missing")) for row in unknown_domain_rows).items())),
        "global_unknown_domain_by_source_domain": dict(sorted(Counter(str(row.get("source_domain", "missing")) for row in unknown_domain_rows).items())),
        "route_counts": {},
        "region_routing_counts": dict(sorted(Counter(str(row.get("region_routing", "missing")) for row in rows).items())),
        "face_fallback_count": sum(1 for row in rows if (row.get("face_candidate") or {}).get("source") == "center_face_prior"),
        "sam_candidate_count": sum(len(row.get("sam_candidates") or []) for row in rows),
        "raw_proposal_count": sum(len(row.get("raw_proposals") or []) for row in rows),
        "region_reuse_count": sum(1 for row in rows if row.get("region_reused_from")),
        "region_reuse_sources": dict(sorted(Counter(str(row.get("region_reused_from")) for row in rows if row.get("region_reused_from")).items())),
        "forbidden_pipeline_keys": sorted(FORBIDDEN_PIPELINE_KEYS),
        "boundary": "image-only pipeline cache; no GT mask/bbox fields are accepted in the input manifest",
    }
    for key, field in [("global_verdict_counts", "pred_verdict"), ("global_domain_counts", "pred_tamper_domain")]:
        counts: dict[str, int] = {}
        for row in rows:
            value = str((row.get("global_prediction") or {}).get(field, "missing"))
            counts[value] = counts.get(value, 0) + 1
        summary[key] = dict(sorted(counts.items()))
    route_counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get("routed_domain", "missing"))
        route_counts[value] = route_counts.get(value, 0) + 1
    summary["route_counts"] = dict(sorted(route_counts.items()))
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.summary_md.write_text(render_md(summary), encoding="utf-8")


def render_md(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {summary['name']} End-to-End Pipeline Cache",
            "",
            "## Boundary",
            "",
            summary["boundary"],
            "",
            "## Counts",
            "",
            f"- samples: `{summary['n']}`",
            f"- completed: `{summary['completed']}`",
            f"- global verdict counts: `{summary['global_verdict_counts']}`",
            f"- global domain counts: `{summary['global_domain_counts']}`",
            f"- global valid JSON/schema: `{summary['global_valid_json_count']}/{summary['n']}` / `{summary['global_valid_schema_count']}/{summary['n']}`",
            f"- global empty raw outputs: `{summary['global_empty_raw_count']}`",
            f"- global parse-error count: `{summary['global_parse_error_count']}`",
            f"- global invalid schema by reason: `{summary['global_invalid_schema_by_reason']}`",
            f"- unknown verdict by source: `{summary['global_unknown_verdict_by_source']}`",
            f"- unknown verdict by source domain: `{summary['global_unknown_verdict_by_source_domain']}`",
            f"- unknown domain by source: `{summary['global_unknown_domain_by_source']}`",
            f"- unknown domain by source domain: `{summary['global_unknown_domain_by_source_domain']}`",
            f"- route counts: `{summary['route_counts']}`",
            f"- region routing counts: `{summary['region_routing_counts']}`",
            f"- raw proposals: `{summary['raw_proposal_count']}`",
            f"- SAM candidates: `{summary['sam_candidate_count']}`",
            f"- region cache reuse count: `{summary['region_reuse_count']}`",
            f"- region cache reuse sources: `{summary['region_reuse_sources']}`",
            f"- face detector center-prior fallbacks: `{summary['face_fallback_count']}`",
        ]
    ) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run image-only end-to-end localization pipeline cache generation.")
    parser.add_argument("--pipeline-manifest", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev/pipeline_manifest.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev_pipeline"))
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--domain-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_domain_boost_json")
    parser.add_argument("--proposal-adapter", default="artifacts/lora_runs/qwen2_5_vl_region_proposal_expert_json")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-pixels", type=int, default=524288)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--proposal-max-new-tokens", type=int, default=96)
    parser.add_argument("--proposal-scales", default="0.35,0.50,0.65")
    parser.add_argument("--region-routing", choices=["global_domain", "all_tampered", "all_images"], default="global_domain")
    parser.add_argument("--sam-min-proposal-score", type=float, default=0.5)
    parser.add_argument("--sam-checkpoint", type=Path, default=Path("weight/sam_vit_b_01ec64.pth"))
    parser.add_argument("--sam-model-type", default="vit_b")
    parser.add_argument("--sam-impl", choices=["auto", "segment_anything", "native"], default="auto")
    parser.add_argument("--reuse-region-cache", type=Path)
    parser.add_argument("--skip-sam", action="store_true")
    parser.add_argument("--multimask", action="store_true", default=True)
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.output_jsonl = args.output_dir / "pipeline_records.jsonl"
    args.summary_json = args.output_dir / "pipeline_summary.json"
    args.summary_md = args.output_dir / "pipeline_summary.md"
    return args


def main() -> None:
    args = parse_args()
    if args.allow_network:
        os.environ["HF_HUB_OFFLINE"] = "0"
        os.environ["TRANSFORMERS_OFFLINE"] = "0"
    rows = maybe_limit(load_jsonl(args.pipeline_manifest), args.limit)
    validate_pipeline_rows(rows)
    records = {} if args.overwrite else load_existing(args.output_jsonl)
    dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.dtype]
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=True)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"
    run_global_predictions(args, rows, records, processor, dtype)
    run_region_candidates(args, rows, records, processor, dtype)
    write_summary(args, records)
    print("wrote", args.output_jsonl)
    print("wrote", args.summary_json)
    print("wrote", args.summary_md)


if __name__ == "__main__":
    main()
