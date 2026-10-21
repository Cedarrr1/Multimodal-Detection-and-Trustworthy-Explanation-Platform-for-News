#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from build_stage2_deepfake_news_pairs_v2 import PROMPT_V2
from convert_stage2_deepfake_news_to_qwen_vl import validate_target
from mix_stage2_deepfake_news_with_stage1 import load_jsonl, select_stage1_rows, write_jsonl


GENERIC_TITLE = "Portrait released alongside a community event update"
GENERIC_BODY = "The accompanying image shows a close-up portrait of a person in an indoor setting."


def target_for(verdict: str) -> dict[str, Any]:
    tampered = verdict == "tampered"
    return {
        "image_verdict": verdict,
        "tamper_domain": "deepfake" if tampered else "none",
        "text_image_relation": "consistent",
        "final_news_verdict": "fake_news" if tampered else "credible",
        "forensic_region": "face" if tampered else "none",
        "evidence": [
            "This rehearsal row preserves the DeepFake image-level supervision.",
            "The neutral title and body describe a generic single-person portrait.",
        ],
    }


def load_stage2_rows(data_path: Path, manifest_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = load_jsonl(data_path)
    manifest = load_jsonl(manifest_path)
    if len(rows) != len(manifest):
        raise ValueError("Stage2 data and manifest counts differ")
    for idx, row in enumerate(rows):
        if row["id"] != manifest[idx]["id"]:
            raise ValueError(f"Stage2 row {idx}: id mismatch")
        if not Path(str(row["images"][0])).exists():
            raise FileNotFoundError(row["images"][0])
        validate_target(json.loads(str(row["messages"][1]["content"])))
    return rows, manifest


def stage1_to_record(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    image_path = Path(str(row["image_path"]))
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    target = validate_target(target_for(str(row["verdict"])))
    record_id = f"stage1_deepfake_rehearsal_v2_{row['source_id']}"
    record = {
        "id": record_id,
        "images": [str(image_path)],
        "messages": [
            {"role": "user", "content": PROMPT_V2.format(title=GENERIC_TITLE, body=GENERIC_BODY)},
            {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
        ],
    }
    manifest = {
        "id": record_id,
        "source": row.get("source"),
        "source_split": row.get("source_split"),
        "source_key": f"{row.get('source_path')}::{row.get('image_member')}",
        "image": str(image_path),
        "gt_mask": row.get("mask_path"),
        "cell": f"{target['image_verdict']}_consistent_stage1_rehearsal",
        "title": GENERIC_TITLE,
        "body": GENERIC_BODY,
        "source_mix_type": "stage1_deepfake_rehearsal",
        **target,
        "target": target,
        "stage1_source_id": row.get("source_id"),
    }
    return record, manifest


def oversample_mismatched(
    stage2_rows: list[dict[str, Any]],
    stage2_manifest: list[dict[str, Any]],
    per_cell: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if per_cell <= 0:
        return [], []
    rng = random.Random(seed)
    rows_by_id = {row["id"]: row for row in stage2_rows}
    manifest_by_cell: dict[str, list[dict[str, Any]]] = {
        "authentic_mismatched": [],
        "tampered_mismatched": [],
    }
    for manifest in stage2_manifest:
        cell = str(manifest.get("cell") or "")
        if cell in manifest_by_cell:
            manifest_by_cell[cell].append(manifest)

    extra_rows: list[dict[str, Any]] = []
    extra_manifest: list[dict[str, Any]] = []
    for cell, manifests in manifest_by_cell.items():
        if not manifests:
            raise RuntimeError(f"no Stage2 rows found for oversample cell {cell}")
        ordered = list(manifests)
        rng.shuffle(ordered)
        selected = [ordered[idx % len(ordered)] for idx in range(per_cell)]
        for idx, manifest in enumerate(selected, start=1):
            source_id = str(manifest["id"])
            record = copy.deepcopy(rows_by_id[source_id])
            manifest_copy = copy.deepcopy(manifest)
            new_id = f"{source_id}_v2_oversample_{idx:04d}"
            record["id"] = new_id
            manifest_copy["id"] = new_id
            manifest_copy["oversample_source_id"] = source_id
            manifest_copy["source_mix_type"] = "stage2_mismatch_oversample"
            extra_rows.append(record)
            extra_manifest.append(manifest_copy)
    return extra_rows, extra_manifest


def run(args: argparse.Namespace) -> None:
    stage2_rows, stage2_manifest = load_stage2_rows(args.stage2_data, args.stage2_manifest)
    stage1_rows = select_stage1_rows(args.stage1_manifest, args.stage1_count, args.seed)
    converted_stage1 = [stage1_to_record(row) for row in stage1_rows]
    extra_rows, extra_manifest = oversample_mismatched(
        stage2_rows,
        stage2_manifest,
        args.mismatched_oversample_per_cell,
        args.seed + 211,
    )

    mixed_rows = list(stage2_rows) + extra_rows + [record for record, _ in converted_stage1]
    mixed_manifest = list(stage2_manifest) + extra_manifest + [manifest for _, manifest in converted_stage1]
    order = list(range(len(mixed_rows)))
    rng = random.Random(args.seed)
    rng.shuffle(order)
    mixed_rows = [mixed_rows[idx] for idx in order]
    mixed_manifest = [mixed_manifest[idx] for idx in order]

    args.output_root.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_root / "llamafactory_qwen_vl_sft.jsonl", mixed_rows)
    write_jsonl(args.output_root / "manifest.jsonl", mixed_manifest)

    stats: Counter = Counter()
    for row in mixed_manifest:
        target = row.get("target") or row
        stats["total"] += 1
        stats[("image_verdict", target["image_verdict"])] += 1
        stats[("text_image_relation", target["text_image_relation"])] += 1
        stats[("final_news_verdict", target["final_news_verdict"])] += 1
        stats[("source_mix_type", str(row.get("source_mix_type") or "stage2_news_pair"))] += 1
        stats[("cell", str(row.get("cell")))] += 1

    meta = {
        "stage2_data": str(args.stage2_data),
        "stage2_manifest": str(args.stage2_manifest),
        "stage1_manifest": str(args.stage1_manifest),
        "stage2_rows": len(stage2_rows),
        "stage2_mismatch_oversample_rows": len(extra_rows),
        "stage1_rehearsal_rows": len(converted_stage1),
        "total_rows": len(mixed_rows),
        "mismatched_oversample_per_cell": args.mismatched_oversample_per_cell,
        "seed": args.seed,
        "stats": {str(key): value for key, value in stats.items()},
    }
    (args.output_root / "dataset_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "README.md").write_text(
        "# Stage2 DeepFake News v2 Mixed JSON Data\n\n"
        "Mixed Stage2 v2 title/body/image consistency rows, mismatched relation oversampling, "
        "and Stage1 DeepFake image-level rehearsal rows.\n",
        encoding="utf-8",
    )
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mix Stage2 v2 DeepFake-news rows with relation-heavy oversampling.")
    parser.add_argument(
        "--stage2-data",
        type=Path,
        default=Path("artifacts/lora_data/stage2_deepfake_news_v2_json/llamafactory_qwen_vl_sft.jsonl"),
    )
    parser.add_argument(
        "--stage2-manifest",
        type=Path,
        default=Path("artifacts/lora_data/stage2_deepfake_news_v2_json/manifest.jsonl"),
    )
    parser.add_argument("--stage1-manifest", type=Path, default=Path("artifacts/lora_data/stage1_domain_boost_json/manifest.jsonl"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_v2_mixed_json"))
    parser.add_argument("--stage1-count", type=int, default=200)
    parser.add_argument("--mismatched-oversample-per-cell", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260719)
    args = parser.parse_args()
    for name in ["stage1_count", "mismatched_oversample_per_cell"]:
        if getattr(args, name) < 0:
            raise ValueError(f"--{name.replace('_', '-')} must be non-negative")
    return args


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
