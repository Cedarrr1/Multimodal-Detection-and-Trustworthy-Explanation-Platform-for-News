#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_stage1_multisource_eval import build_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the held-out p600_final Stage1 image-level test set.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_p600_final"))
    parser.add_argument("--per-label", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--ffhq-zip", type=Path, default=Path("dataset/deepfake/ffhq.zip"))
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--faceapp-splits", default="train,test")
    parser.add_argument("--sd-train-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/train.tar"))
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument("--include-sd-train", action="store_true")
    parser.add_argument("--imd2020-root", type=Path, default=Path("dataset/photoshop/IMD2020"))
    parser.add_argument("--columbia-root", type=Path, default=Path("dataset/photoshop/Columbia"))
    parser.add_argument("--coverage-root", type=Path, default=Path("dataset/photoshop/Coverage"))
    parser.add_argument(
        "--exclude-manifest",
        type=Path,
        action="append",
        default=[
            Path("artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_multisource_eval_p600/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_domain_boost_json/manifest.jsonl"),
            Path("artifacts/region_eval/region_eval_p150/samples.jsonl"),
        ],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.per_label != 100:
        raise ValueError("p600_final must use --per-label 100")
    meta = build_dataset(args)
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
