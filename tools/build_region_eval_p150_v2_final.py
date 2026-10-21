#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_region_eval_p60 import build_dataset


DEFAULT_EXCLUDES = [
    Path("artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_multisource_eval_p600/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_multisource_eval_p600_final/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_domain_boost_json/manifest.jsonl"),
    Path("artifacts/region_eval/region_eval_p60/manifest.jsonl"),
    Path("artifacts/region_eval/region_eval_p150/samples.jsonl"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build independent region_eval_p150_v2_final split.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/region_eval/region_eval_p150_v2_final"))
    parser.add_argument("--dataset-name", default="region_eval_p150_v2_final")
    parser.add_argument("--per-domain", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260715)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument(
        "--exclude-manifest",
        type=Path,
        action="append",
        default=list(DEFAULT_EXCLUDES),
        help="Additional exclusion manifest JSONL. Defaults already exclude train/dev/final image-level and old region splits.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.per_domain < 1:
        raise ValueError("--per-domain must be positive")
    meta = build_dataset(args)
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
