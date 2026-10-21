#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from convert_stage2_deepfake_news_to_qwen_vl import PROMPT, validate_target


GENERIC_TITLE = "Portrait released alongside a community event update"
GENERIC_BODY = "The accompanying image shows a close-up portrait of a person in an indoor setting."


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


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
        if not Path(str(row["images"][0])).exists():
            raise FileNotFoundError(row["images"][0])
        validate_target(json.loads(str(row["messages"][1]["content"])))
        if row["id"] != manifest[idx]["id"]:
            raise ValueError(f"Stage2 row {idx}: id mismatch")
    return rows, manifest


def select_stage1_rows(stage1_manifest: Path, count: int, seed: int) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in load_jsonl(stage1_manifest)
        if row.get("task") == "compact_judgment"
        and row.get("source_domain") == "deepfake"
        and row.get("verdict") in {"authentic", "tampered"}
    ]
    buckets = {
        "authentic": [row for row in candidates if row["verdict"] == "authentic"],
        "tampered": [row for row in candidates if row["verdict"] == "tampered"],
    }
    per_label = count // 2
    remainder = count - 2 * per_label
    selected: list[dict[str, Any]] = []
    for verdict in ["authentic", "tampered"]:
        need = per_label + (1 if remainder and verdict == "tampered" else 0)
        group = list(buckets[verdict])
        rng = random.Random(seed + (17 if verdict == "tampered" else 7))
        rng.shuffle(group)
        if len(group) < need:
            raise RuntimeError(f"Stage1 {verdict}: need {need}, found {len(group)}")
        selected.extend(group[:need])
    rng = random.Random(seed + 101)
    rng.shuffle(selected)
    return selected


def stage1_to_record(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    image_path = Path(str(row["image_path"]))
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    target = validate_target(target_for(str(row["verdict"])))
    record_id = f"stage1_deepfake_rehearsal_{row['source_id']}"
    record = {
        "id": record_id,
        "images": [str(image_path)],
        "messages": [
            {"role": "user", "content": PROMPT.format(title=GENERIC_TITLE, body=GENERIC_BODY)},
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
        **target,
        "target": target,
        "stage1_source_id": row.get("source_id"),
    }
    return record, manifest


def run(args: argparse.Namespace) -> None:
    stage2_rows, stage2_manifest = load_stage2_rows(args.stage2_data, args.stage2_manifest)
    stage1_count = args.stage1_count if args.stage1_count is not None else len(stage2_rows)
    stage1_rows = select_stage1_rows(args.stage1_manifest, stage1_count, args.seed)
    converted_stage1 = [stage1_to_record(row) for row in stage1_rows]

    mixed_rows = list(stage2_rows) + [record for record, _ in converted_stage1]
    mixed_manifest = list(stage2_manifest) + [manifest for _, manifest in converted_stage1]
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
        stats[("source", "stage1_rehearsal" if str(row["id"]).startswith("stage1_") else "stage2_news_pair")] += 1

    meta = {
        "stage2_data": str(args.stage2_data),
        "stage2_manifest": str(args.stage2_manifest),
        "stage1_manifest": str(args.stage1_manifest),
        "stage2_rows": len(stage2_rows),
        "stage1_rehearsal_rows": len(converted_stage1),
        "total_rows": len(mixed_rows),
        "seed": args.seed,
        "stats": {str(key): value for key, value in stats.items()},
    }
    (args.output_root / "dataset_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "README.md").write_text(
        "# Stage2 DeepFake News Mixed JSON Data\n\n"
        "Mixed Stage2 title/body/image consistency rows with Stage1 DeepFake image-level rehearsal rows.\n",
        encoding="utf-8",
    )
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mix Stage2 DeepFake-news rows with Stage1 DeepFake image-level rehearsal rows.")
    parser.add_argument("--stage2-data", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_json/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--stage2-manifest", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_json/manifest.jsonl"))
    parser.add_argument("--stage1-manifest", type=Path, default=Path("artifacts/lora_data/stage1_domain_boost_json/manifest.jsonl"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_mixed_json"))
    parser.add_argument("--stage1-count", type=int)
    parser.add_argument("--seed", type=int, default=20260718)
    args = parser.parse_args()
    if args.stage1_count is not None and args.stage1_count < 0:
        raise ValueError("--stage1-count must be non-negative")
    return args


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
