#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from build_stage2_relation_v3_data import EVIDENCE_ATTRIBUTES, RELATIONS, prompt_for, validate_target


OPTIONAL_MANIFEST_KEYS = [
    "source",
    "source_split",
    "source_key",
    "group_id",
    "image_verdict",
    "tamper_domain",
    "forensic_region",
    "gt_mask",
    "gt_mask_rel",
    "title",
    "body",
    "caption",
    "case_type",
    "difficulty",
    "counterfactual_pair_id",
    "counterfactual_pair_role",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


def resolve_path(value: Any, root: Path, field: str) -> Path:
    path = Path(normalize_text(value, field))
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def copy_or_reference_image(row_id: str, image_path: Path, output_root: Path, copy_images: bool) -> Path:
    if not copy_images:
        return image_path
    suffix = image_path.suffix.lower() or ".jpg"
    dst = output_root / "images" / f"{row_id}{suffix}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(image_path, dst)
    return dst


def convert(input_path: Path, image_root: Path, output_root: Path, copy_images: bool) -> Counter:
    rows = load_jsonl(input_path)
    output_root.mkdir(parents=True, exist_ok=True)
    data_path = output_root / "llamafactory_qwen_vl_sft.jsonl"
    manifest_path = output_root / "manifest.jsonl"

    stats: Counter = Counter()
    with data_path.open("w", encoding="utf-8") as data_f, manifest_path.open("w", encoding="utf-8") as manifest_f:
        for idx, row in enumerate(rows):
            row_id = normalize_text(row.get("id") or f"stage2_relation_v3_{idx:06d}", "id")
            target = validate_target(dict(row.get("target") or {}))
            image_path = resolve_path(row.get("image"), image_root, "image")
            output_image = copy_or_reference_image(row_id, image_path, output_root, copy_images)
            prompt = normalize_text(row.get("prompt") or prompt_for(target["claims"]), "prompt")
            if prompt.count("<image>") != 1:
                raise ValueError(f"{row_id}: prompt must contain exactly one <image> placeholder")

            record = {
                "id": row_id,
                "images": [str(output_image)],
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                ],
            }
            manifest = {
                "id": row_id,
                "split": row.get("split"),
                "image": str(output_image),
                "claims": target["claims"],
                "overall_relation": target["overall_relation"],
                "target": target,
            }
            for key in OPTIONAL_MANIFEST_KEYS:
                if key in row:
                    manifest[key] = row.get(key)

            data_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            manifest_f.write(json.dumps(manifest, ensure_ascii=False) + "\n")
            stats["total"] += 1
            stats[("overall_relation", target["overall_relation"])] += 1
            stats[("case_type", str(row.get("case_type")))] += 1
            stats[("difficulty", str(row.get("difficulty")))] += 1
            for item in target["claims"]:
                stats[("claim_relation", item["relation"])] += 1
                for attr in item["evidence_attributes"]:
                    stats[("evidence_attribute", attr)] += 1

    validate_output(data_path, manifest_path)
    write_readme(output_root, input_path, image_root, stats, copy_images)
    return stats


def validate_output(data_path: Path, manifest_path: Path) -> None:
    data_rows = load_jsonl(data_path)
    manifest_rows = load_jsonl(manifest_path)
    if len(data_rows) != len(manifest_rows):
        raise ValueError("data and manifest row counts differ")
    for idx, (row, manifest) in enumerate(zip(data_rows, manifest_rows)):
        if row["id"] != manifest["id"]:
            raise ValueError(f"row {idx}: id mismatch")
        images = row.get("images")
        messages = row.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: expected one image")
        if not Path(str(images[0])).exists():
            raise FileNotFoundError(images[0])
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"row {idx}: expected user and assistant messages")
        if str(messages[0].get("content", "")).count("<image>") != 1:
            raise ValueError(f"row {idx}: expected one image placeholder")
        target = validate_target(json.loads(str(messages[1].get("content", ""))))
        if target != validate_target(dict(manifest["target"])):
            raise ValueError(f"row {idx}: target mismatch")


def write_readme(output_root: Path, input_path: Path, image_root: Path, stats: Counter, copy_images: bool) -> None:
    lines = [
        "# Stage2 Relation V3 JSON Data",
        "",
        "This directory contains relation-only LLaMA-Factory ShareGPT records.",
        "The assistant target supervises claim-level text-image relation only;",
        "it deliberately excludes image manipulation labels.",
        "",
        f"- input_path: `{input_path}`",
        f"- image_root: `{image_root}`",
        f"- copy_images: `{copy_images}`",
        f"- total records: `{stats['total']}`",
        f"- relation labels: `{', '.join(sorted(RELATIONS))}`",
        f"- evidence attributes: `{', '.join(sorted(EVIDENCE_ATTRIBUTES))}`",
        "",
        "Target schema: `schemas/stage2_relation_v3_report.schema.json`.",
    ]
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Stage2 relation-v3 raw JSONL to Qwen-VL ShareGPT JSONL.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage2_relation_v3_json"))
    parser.add_argument("--copy-images", action="store_true")
    args = parser.parse_args()

    stats = convert(args.input, args.image_root, args.output_root, args.copy_images)
    print("wrote", args.output_root)
    print(json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
