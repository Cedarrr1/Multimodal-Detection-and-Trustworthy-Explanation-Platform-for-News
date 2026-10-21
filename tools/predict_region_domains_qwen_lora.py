#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from eval_stage1_multisource import parse_prediction


PROMPT = (
    "Analyze whether this image has been digitally manipulated. "
    "Return only valid compact JSON with exactly these keys: verdict and tamper_domain. "
    'Use verdict "authentic" or "tampered"; use tamper_domain "none", '
    '"photoshop", "deepfake", or "aigc_inpaint".'
)


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


def image_content_for(row: dict[str, Any], max_pixels: int | None) -> dict[str, Any]:
    content = {"type": "image", "image": row["resolved_image"]}
    if max_pixels is not None:
        content["max_pixels"] = max_pixels
    return content


def infer_batch(model, processor, batch: list[dict[str, Any]], device: str, max_new_tokens: int, max_pixels: int | None) -> list[str]:
    messages_list = [
        [{"role": "user", "content": [image_content_for(row, max_pixels), {"type": "text", "text": PROMPT}]}]
        for row in batch
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
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
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


def run(args: argparse.Namespace) -> None:
    rows = load_jsonl(args.samples)
    if args.limit is not None:
        rows = rows[: args.limit]
    records = load_existing(args.output_jsonl) if args.resume else {}
    if not args.resume and args.output_jsonl.exists():
        args.output_jsonl.unlink()

    pending = [row for row in rows if str(row["id"]) not in records]
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=True)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"
    model = load_model(args.base_model, args.adapter, dtype, device)

    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        labels = ", ".join(f"{row['id']}:{row['domain']}" for row in batch)
        print(f"infer domain batch {start + 1}-{start + len(batch)}/{len(pending)} [{labels}]", flush=True)
        outputs = infer_batch(model, processor, batch, device, args.max_new_tokens, args.max_pixels)
        with args.output_jsonl.open("a", encoding="utf-8") as f:
            for row, raw in zip(batch, outputs):
                pred = parse_prediction(raw.strip())
                record = {
                    "id": row["id"],
                    "domain": row["domain"],
                    "source_dataset": row.get("source_dataset") or row.get("source"),
                    "image": row["image"],
                    "resolved_image": row["resolved_image"],
                    "raw": raw.strip(),
                    "valid_json": pred["valid_json"],
                    "valid_schema": pred["valid_schema"],
                    "predicted_verdict": pred["pred_verdict"],
                    "predicted_domain": pred["pred_tamper_domain"],
                    "parsed": pred["parsed"],
                    "parse_error": pred["parse_error"],
                }
                records[str(row["id"])] = record
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()

    write_all(args.output_jsonl, records)
    print("wrote_jsonl", args.output_jsonl, flush=True)
    print("records", len(records), flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict region_eval sample tamper domains with Qwen2.5-VL LoRA.")
    parser.add_argument("--samples", type=Path, default=Path("artifacts/region_eval/region_eval_p150/samples.jsonl"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/region_eval/region_eval_p150/domain_predictions.jsonl"))
    parser.add_argument("--base-model", default="/home/Master/CaoMJ/.cache/huggingface/hub/models--Qwen--Qwen2.5-VL-3B-Instruct/snapshots/66285546d2b821cf421d4f5eb2576359d3770cd3")
    parser.add_argument("--adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_domain_boost_json")
    parser.add_argument("--batch-size", type=int, default=8)
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
