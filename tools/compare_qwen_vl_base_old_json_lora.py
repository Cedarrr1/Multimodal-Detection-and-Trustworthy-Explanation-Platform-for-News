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


DEFAULT_PROMPT = (
    "Analyze whether this image has been digitally manipulated. "
    "Return only valid JSON with verdict, tampered_region, tamper_domain, and evidence."
)
DEFAULT_SAMPLE_INDICES = [0, 1, 2, 5, 8, 13]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare base, old p100 LoRA, and JSON p100 LoRA outputs.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--old-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p100")
    parser.add_argument("--json-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p100_json")
    parser.add_argument("--data", default="artifacts/lora_data/stage1_mmtd_p100_json/llamafactory_qwen_vl_sft.jsonl")
    parser.add_argument("--output-jsonl", default="artifacts/eval/qwen2_5_vl_stage1_p100_three_way_compare.jsonl")
    parser.add_argument("--output-md", default="artifacts/eval/qwen2_5_vl_stage1_p100_three_way_compare.md")
    parser.add_argument("--indices", default=",".join(str(i) for i in DEFAULT_SAMPLE_INDICES))
    parser.add_argument("--max-new-tokens", type=int, default=220)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    return parser.parse_args()


def load_rows(path: Path, indices: list[int]) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    selected = []
    for idx in indices:
        if idx < 0 or idx >= len(rows):
            raise IndexError(f"sample index {idx} out of range for {len(rows)} rows")
        row = rows[idx]
        image = Path(row["images"][0])
        if not image.exists():
            raise FileNotFoundError(image)
        selected.append({"index": idx, **row})
    return selected


def load_model(base_model: str, adapter: str | None, dtype: torch.dtype, device: str):
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
    )
    if adapter is not None:
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model


def infer(model, processor, image_path: str, prompt: str, device: str, max_new_tokens: int) -> str:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()


def run_variant(
    name: str,
    base_model: str,
    adapter: str | None,
    processor,
    rows: list[dict[str, Any]],
    dtype: torch.dtype,
    device: str,
    prompt: str,
    max_new_tokens: int,
) -> list[str]:
    print("loading", name, adapter or base_model)
    model = load_model(base_model, adapter, dtype, device)
    outputs = []
    for row in rows:
        print("infer", name, row["index"], row["images"][0])
        outputs.append(infer(model, processor, row["images"][0], prompt, device, max_new_tokens))
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return outputs


def write_markdown(path: Path, records: list[dict[str, Any]]) -> None:
    lines = ["# Qwen2.5-VL Base vs p100 vs p100-json Comparison", ""]
    for record in records:
        lines.extend(
            [
                f"## Sample {record['index']}",
                "",
                f"- image: `{record['image']}`",
                f"- reference: `{record['reference']}`",
                "",
                "### Base",
                "",
                record["base_output"],
                "",
                "### old p100 LoRA",
                "",
                record["old_p100_output"],
                "",
                "### json p100 LoRA",
                "",
                record["json_p100_output"],
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    indices = [int(x) for x in args.indices.split(",") if x.strip()]
    rows = load_rows(Path(args.data), indices)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True)

    base_outputs = run_variant(
        "base", args.base_model, None, processor, rows, dtype, device, args.prompt, args.max_new_tokens
    )
    old_outputs = run_variant(
        "old_p100", args.base_model, args.old_adapter, processor, rows, dtype, device, args.prompt, args.max_new_tokens
    )
    json_outputs = run_variant(
        "json_p100", args.base_model, args.json_adapter, processor, rows, dtype, device, args.prompt, args.max_new_tokens
    )

    records = []
    for row, base_output, old_output, json_output in zip(rows, base_outputs, old_outputs, json_outputs):
        records.append(
            {
                "index": row["index"],
                "image": row["images"][0],
                "reference": row["messages"][1]["content"],
                "base_output": base_output,
                "old_p100_output": old_output,
                "json_p100_output": json_output,
            }
        )

    output_jsonl = Path(args.output_jsonl)
    output_md = Path(args.output_md)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_markdown(output_md, records)
    print("wrote_jsonl", output_jsonl)
    print("wrote_md", output_md)


if __name__ == "__main__":
    main()
