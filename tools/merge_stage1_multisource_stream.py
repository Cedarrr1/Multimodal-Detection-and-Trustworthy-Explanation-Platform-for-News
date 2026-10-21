#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from eval_stage1_multisource import compute_metrics, load_eval_rows, write_summary


def load_records(paths: list[Path]) -> dict[int, dict[str, Any]]:
    records: dict[int, dict[str, Any]] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            idx = int(row["index"])
            current = records.get(idx)
            if current is None:
                records[idx] = row
            else:
                current.setdefault("predictions", {}).update(row.get("predictions", {}))
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge streaming multisource eval shards.")
    parser.add_argument("--data", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_v2/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--labels", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_v2/eval_labels.jsonl"))
    parser.add_argument("--dataset-meta", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_v2/dataset_meta.json"))
    parser.add_argument("--input-jsonl", type=Path, action="append", required=True)
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--summary-md", type=Path, required=True)
    parser.add_argument("--variants", default="base,json_p500")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_eval_rows(args.data, args.labels)
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    records_by_idx = load_records(args.input_jsonl)
    missing = [int(row["index"]) for row in rows if set(records_by_idx.get(int(row["index"]), {}).get("predictions", {})) != set(variants)]
    if missing:
        raise RuntimeError(f"missing complete predictions for {len(missing)} rows, first={missing[:10]}")
    records = [records_by_idx[int(row["index"])] for row in rows]
    metrics = compute_metrics(records, variants)
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_jsonl.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    dataset_meta = json.loads(args.dataset_meta.read_text(encoding="utf-8")) if args.dataset_meta.exists() else None
    args.summary_md.parent.mkdir(parents=True, exist_ok=True)
    write_summary(args.summary_md, metrics, records, variants, dataset_meta)
    print("wrote_jsonl", args.output_jsonl)
    print("wrote_summary", args.summary_md)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
