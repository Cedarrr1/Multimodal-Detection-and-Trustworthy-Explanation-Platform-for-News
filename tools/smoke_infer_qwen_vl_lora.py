#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


DEFAULT_PROMPT = (
    "This image is suspected to have been manipulated. "
    "Determine whether there is evidence of image tampering and explain the visual clues."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test Qwen2.5-VL LoRA inference.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_demo")
    parser.add_argument(
        "--image",
        default="artifacts/lora_data/stage1_mmtd_demo/images/ps/CASIA2_Au/image/Au_ani_30630.jpg",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--max-new-tokens", type=int, default=192)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter_path = Path(args.adapter)
    image_path = Path(args.image).resolve()

    if not image_path.exists():
        raise FileNotFoundError(image_path)
    if not (adapter_path / "adapter_model.safetensors").exists():
        raise FileNotFoundError(adapter_path / "adapter_model.safetensors")
    if not (adapter_path / "adapter_config.json").exists():
        raise FileNotFoundError(adapter_path / "adapter_config.json")

    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True)
    base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, str(adapter_path))
    model.eval()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": str(image_path)},
                {"type": "text", "text": args.prompt},
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
        generated_ids = model.generate(**inputs, max_new_tokens=args.max_new_tokens)

    prompt_len = inputs["input_ids"].shape[1]
    generated_ids = generated_ids[:, prompt_len:]
    output = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    print("base_model", args.base_model)
    print("adapter", adapter_path)
    print("adapter_loaded", isinstance(model, PeftModel))
    print("device", device)
    print("image", image_path)
    print("prompt", args.prompt)
    print("generated_text")
    print(output.strip())


if __name__ == "__main__":
    main()
