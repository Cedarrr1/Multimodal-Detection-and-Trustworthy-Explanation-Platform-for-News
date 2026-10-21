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
    "You are an image forensics analyst. Decide whether the image is authentic or tampered. "
    "If tampered, describe the likely manipulated region and give domain-specific visual evidence. "
    "Mention cues such as deepfake facial boundary artifacts, AIGC inpainting texture discontinuities, "
    "or Photoshop splicing/compositing traces when relevant."
)

DEFAULT_SAMPLE_INDICES = [0, 1, 2, 5, 8, 13]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare base Qwen2.5-VL and LoRA adapter outputs.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p100")
    parser.add_argument("--data", default="artifacts/lora_data/stage1_mmtd_p100/llamafactory_qwen_vl_sft.jsonl")
    parser.add_argument("--output-jsonl", default="artifacts/eval/qwen2_5_vl_stage1_p100_compare.jsonl")
    parser.add_argument("--output-md", default="artifacts/eval/qwen2_5_vl_stage1_p100_compare.md")
    parser.add_argument("--indices", default=",".join(str(i) for i in DEFAULT_SAMPLE_INDICES))
    parser.add_argument("--max-new-tokens", type=int, default=192)
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


def infer(
    model,
    processor,
    image_path: str,
    prompt: str,
    device: str,
    max_new_tokens: int,
) -> str:
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


def write_markdown(path: Path, records: list[dict[str, Any]]) -> None:
    lines = ["# Qwen2.5-VL Base vs p100 LoRA Comparison", ""]
    for record in records:
        lines.extend(
            [
                f"## Sample {record['index']}",
                "",
                f"- image: `{record['image']}`",
                f"- reference: {record['reference_first_line']}",
                "",
                "### Base",
                "",
                record["base_output"],
                "",
                "### p100 LoRA",
                "",
                record["lora_output"],
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

    print("loading_base_model", args.base_model)
    base_model = load_model(args.base_model, None, dtype, device)
    base_outputs = []
    for row in rows:
        print("base_infer", row["index"], row["images"][0])
        base_outputs.append(infer(base_model, processor, row["images"][0], args.prompt, device, args.max_new_tokens))

    del base_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    print("loading_lora_adapter", args.adapter)
    lora_model = load_model(args.base_model, args.adapter, dtype, device)
    records = []
    for row, base_output in zip(rows, base_outputs):
        print("lora_infer", row["index"], row["images"][0])
        lora_output = infer(lora_model, processor, row["images"][0], args.prompt, device, args.max_new_tokens)
        assistant = row["messages"][1]["content"].strip().splitlines()[0]
        records.append(
            {
                "index": row["index"],
                "image": row["images"][0],
                "reference_first_line": assistant,
                "base_output": base_output,
                "lora_output": lora_output,
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
