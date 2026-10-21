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

from eval_stage1_multisource import compute_metrics, load_eval_rows, parse_prediction, write_summary


def load_model(base_model: str, adapter: str | None, dtype: torch.dtype, device: str):
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
        local_files_only=True,
    )
    if adapter is not None:
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model


def infer(model, processor, image_path: str, prompt: str, device: str, max_new_tokens: int) -> str:
    image_content = {"type": "image", "image": image_path}
    messages = [{"role": "user", "content": [image_content, {"type": "text", "text": prompt}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(device)
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()


def image_content_for(row: dict[str, Any], max_pixels: int | None) -> dict[str, Any]:
    content = {"type": "image", "image": row["image"]}
    if max_pixels is not None:
        content["max_pixels"] = max_pixels
    return content


def infer_batch(model, processor, batch: list[dict[str, Any]], device: str, max_new_tokens: int, max_pixels: int | None) -> list[str]:
    messages_list = [
        [{"role": "user", "content": [image_content_for(row, max_pixels), {"type": "text", "text": row["user_prompt"]}]}]
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


def load_existing(path: Path) -> dict[int, dict[str, Any]]:
    if not path.exists():
        return {}
    records: dict[int, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        records[int(row["index"])] = row
    return records


def write_all(path: Path, records: dict[int, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for idx in sorted(records):
            f.write(json.dumps(records[idx], ensure_ascii=False) + "\n")
    tmp.replace(path)


def slice_rows(rows: list[dict[str, Any]], start: int | None, end: int | None) -> list[dict[str, Any]]:
    if start is None and end is None:
        return rows
    lo = 0 if start is None else start
    hi = len(rows) if end is None else end
    return [row for row in rows if lo <= int(row["index"]) < hi]


def run_variant(
    name: str,
    adapter: str | None,
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    processor,
    dtype: torch.dtype,
    device: str,
    records: dict[int, dict[str, Any]],
) -> None:
    print(f"loading {name} {adapter or args.base_model}", flush=True)
    model = load_model(args.base_model, adapter, dtype, device)
    max_new_tokens = args.base_max_new_tokens if name == "base" else args.json_max_new_tokens
    pending = [row for row in rows if name not in records.get(int(row["index"]), {}).get("predictions", {})]
    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        labels = ", ".join(f"{row['index']}:{row['label']['source']}/{row['label']['verdict']}" for row in batch)
        print(f"infer {name} batch {start + 1}-{start + len(batch)}/{len(pending)} [{labels}]", flush=True)
        outputs = infer_batch(model, processor, batch, device, max_new_tokens, args.max_pixels)
        with args.output_jsonl.open("a", encoding="utf-8") as f:
            for row, raw in zip(batch, outputs):
                idx = int(row["index"])
                pred = parse_prediction(raw.strip())
                record = records.get(idx)
                if record is None:
                    record = {**row, "predictions": {}}
                record["predictions"][name] = pred
                records[idx] = record
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    write_all(args.output_jsonl, records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Streaming/resumable multisource Stage1 evaluation.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--json-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p500_json")
    parser.add_argument("--data", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_v2/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--labels", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_v2/eval_labels.jsonl"))
    parser.add_argument("--dataset-meta", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_v2/dataset_meta.json"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/eval/stage1_multisource_v2_base_vs_p500_stream.jsonl"))
    parser.add_argument("--summary-md", type=Path, default=Path("artifacts/eval/stage1_multisource_v2_base_vs_p500_stream_summary.md"))
    parser.add_argument("--max-new-tokens", type=int, default=220)
    parser.add_argument("--base-max-new-tokens", type=int)
    parser.add_argument("--json-max-new-tokens", type=int)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-pixels", type=int, help="Optional Qwen-VL image max_pixels limit for faster eval.")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start", type=int, help="Inclusive original row index for sharded evaluation.")
    parser.add_argument("--end", type=int, help="Exclusive original row index for sharded evaluation.")
    parser.add_argument("--variants", default="base,json_p500")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")
    if args.base_max_new_tokens is None:
        args.base_max_new_tokens = args.max_new_tokens
    if args.json_max_new_tokens is None:
        args.json_max_new_tokens = args.max_new_tokens
    rows = load_eval_rows(args.data, args.labels)
    rows = slice_rows(rows, args.start, args.end)
    if args.limit is not None:
        rows = rows[: args.limit]
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=True)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"

    records = load_existing(args.output_jsonl) if args.resume else {}
    if not args.resume and args.output_jsonl.exists():
        args.output_jsonl.unlink()

    variant_specs = []
    for variant in [v.strip() for v in args.variants.split(",") if v.strip()]:
        if variant == "base":
            variant_specs.append(("base", None))
        elif variant == "json_p500":
            variant_specs.append(("json_p500", args.json_adapter))
        else:
            raise ValueError(f"unknown variant: {variant}")

    for name, adapter in variant_specs:
        run_variant(name, adapter, args, rows, processor, dtype, device, records)

    records_list = [records[int(row["index"])] for row in rows if int(row["index"]) in records]
    variants = [name for name, _ in variant_specs]
    missing = [row["index"] for row in rows if set(records.get(int(row["index"]), {}).get("predictions", {})) != set(variants)]
    if missing:
        raise RuntimeError(f"missing predictions for rows: {missing[:10]} total={len(missing)}")
    metrics = compute_metrics(records_list, variants)
    dataset_meta = json.loads(args.dataset_meta.read_text(encoding="utf-8")) if args.dataset_meta.exists() else None
    args.summary_md.parent.mkdir(parents=True, exist_ok=True)
    write_summary(args.summary_md, metrics, records_list, variants, dataset_meta)
    print("wrote_jsonl", args.output_jsonl, flush=True)
    print("wrote_summary", args.summary_md, flush=True)
    print(json.dumps(metrics, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
