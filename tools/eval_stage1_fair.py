#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from eval_stage1_multisource import load_eval_rows, parse_prediction


PROMPTS = {
    "compact": (
        "Analyze whether this image has been digitally manipulated. "
        "Return only valid compact JSON with exactly these keys: verdict and tamper_domain. "
        'Use verdict "authentic" or "tampered"; use tamper_domain "none", '
        '"photoshop", "deepfake", or "aigc_inpaint".'
    ),
    "explanation": (
        "Analyze whether this image has been digitally manipulated. "
        "Return only valid JSON with exactly these keys: verdict, tamper_domain, "
        "tampered_region, and evidence."
    ),
}

DEFAULT_VARIANTS = (
    "base,"
    "json_p500=artifacts/lora_runs/qwen2_5_vl_stage1_p500_json,"
    "domain_boost=artifacts/lora_runs/qwen2_5_vl_stage1_domain_boost_json"
)

METRIC_NAMES = [
    "valid_json",
    "valid_schema",
    "verdict_accuracy",
    "balanced_accuracy",
    "tampered_recall",
    "authentic_accuracy",
    "tamper_domain_accuracy",
]


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


def image_content_for(row: dict[str, Any], max_pixels: int | None) -> dict[str, Any]:
    content = {"type": "image", "image": row["image"]}
    if max_pixels is not None:
        content["max_pixels"] = max_pixels
    return content


def infer_batch(
    model,
    processor,
    batch: list[dict[str, Any]],
    prompt: str,
    device: str,
    max_new_tokens: int,
    max_pixels: int | None,
) -> list[str]:
    messages_list = [
        [{"role": "user", "content": [image_content_for(row, max_pixels), {"type": "text", "text": prompt}]}]
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
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)


def parse_variants(text: str) -> list[tuple[str, str | None]]:
    variants: list[tuple[str, str | None]] = []
    for item in [part.strip() for part in text.split(",") if part.strip()]:
        if item == "base":
            variants.append(("base", None))
            continue
        if "=" not in item:
            raise ValueError(f"variant must be 'base' or name=adapter_path: {item}")
        name, adapter = item.split("=", 1)
        name = name.strip()
        adapter = adapter.strip()
        if not name or not adapter:
            raise ValueError(f"bad variant spec: {item}")
        variants.append((name, adapter))
    if not variants:
        raise ValueError("no variants configured")
    return variants


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
    lo = 0 if start is None else start
    hi = len(rows) if end is None else end
    return [row for row in rows if lo <= int(row["index"]) < hi]


def sample_rows(rows: list[dict[str, Any]], sample_size: int | None, seed: int) -> list[dict[str, Any]]:
    if sample_size is None or sample_size >= len(rows):
        return rows
    rng = random.Random(seed)
    sampled = list(rows)
    rng.shuffle(sampled)
    return sorted(sampled[:sample_size], key=lambda row: int(row["index"]))


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
    pending = [row for row in rows if name not in records.get(int(row["index"]), {}).get("predictions", {})]
    prompt = PROMPTS[args.schema]
    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        labels = ", ".join(f"{row['index']}:{row['label']['source']}/{row['label']['verdict']}" for row in batch)
        print(f"infer {name} batch {start + 1}-{start + len(batch)}/{len(pending)} [{labels}]", flush=True)
        outputs = infer_batch(model, processor, batch, prompt, device, args.max_new_tokens, args.max_pixels)
        for row, raw in zip(batch, outputs):
            idx = int(row["index"])
            record = records.get(idx)
            if record is None:
                record = {**row, "predictions": {}}
            record["predictions"][name] = parse_prediction(raw.strip())
            records[idx] = record
        write_all(args.output_jsonl, records)
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def safe_div(num: int, den: int) -> float | None:
    return num / den if den else None


def group_metric_values(records: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    total = len(records)
    tampered = [record for record in records if record["label"]["verdict"] == "tampered"]
    authentic = [record for record in records if record["label"]["verdict"] == "authentic"]
    valid_json = sum(bool(record["predictions"][variant]["valid_json"]) for record in records)
    valid_schema = sum(bool(record["predictions"][variant]["valid_schema"]) for record in records)
    verdict_correct = sum(record["predictions"][variant]["pred_verdict"] == record["label"]["verdict"] for record in records)
    tampered_hit = sum(record["predictions"][variant]["pred_verdict"] == "tampered" for record in tampered)
    authentic_hit = sum(record["predictions"][variant]["pred_verdict"] == "authentic" for record in authentic)
    domain_hit = sum(record["predictions"][variant]["pred_tamper_domain"] == record["label"]["tamper_domain"] for record in tampered)
    tampered_recall = safe_div(tampered_hit, len(tampered))
    authentic_accuracy = safe_div(authentic_hit, len(authentic))
    balanced = None
    if tampered_recall is not None and authentic_accuracy is not None:
        balanced = (tampered_recall + authentic_accuracy) / 2.0
    return {
        "n": total,
        "valid_json": {"correct": valid_json, "total": total, "value": safe_div(valid_json, total)},
        "valid_schema": {"correct": valid_schema, "total": total, "value": safe_div(valid_schema, total)},
        "verdict_accuracy": {"correct": verdict_correct, "total": total, "value": safe_div(verdict_correct, total)},
        "balanced_accuracy": {"correct": None, "total": total, "value": balanced},
        "tampered_recall": {"correct": tampered_hit, "total": len(tampered), "value": tampered_recall},
        "authentic_accuracy": {"correct": authentic_hit, "total": len(authentic), "value": authentic_accuracy},
        "tamper_domain_accuracy": {"correct": domain_hit, "total": len(tampered), "value": safe_div(domain_hit, len(tampered))},
    }


def bootstrap_ci(
    records: list[dict[str, Any]],
    variant: str,
    metric_name: str,
    samples: int,
    seed: int,
) -> dict[str, float] | None:
    if not records or samples <= 0:
        return None
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(samples):
        resampled = [records[rng.randrange(len(records))] for _ in range(len(records))]
        value = group_metric_values(resampled, variant)[metric_name]["value"]
        if value is not None:
            values.append(float(value))
    if not values:
        return None
    values.sort()
    lo_idx = max(0, min(len(values) - 1, int(0.025 * (len(values) - 1))))
    hi_idx = max(0, min(len(values) - 1, int(0.975 * (len(values) - 1))))
    return {"low": values[lo_idx], "high": values[hi_idx]}


def add_ci(payload: dict[str, Any], records: list[dict[str, Any]], variant: str, args: argparse.Namespace, salt: str) -> None:
    for metric_name in METRIC_NAMES:
        ci = bootstrap_ci(
            records,
            variant,
            metric_name,
            args.bootstrap_samples,
            stable_seed(args.bootstrap_seed, variant, metric_name, salt),
        )
        if ci is not None:
            payload[metric_name]["ci95"] = ci


def stable_seed(seed: int, *parts: str) -> int:
    text = ":".join([str(seed), *parts])
    value = 0
    for char in text:
        value = (value * 131 + ord(char)) % (2**31 - 1)
    return value


def compute_metrics(records: list[dict[str, Any]], variants: list[str], args: argparse.Namespace) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for variant in variants:
        overall = group_metric_values(records, variant)
        add_ci(overall, records, variant, args, "overall")
        out[variant] = {"overall": overall, "by_source_domain": {}, "by_source": {}}
        grouped: dict[str, dict[str, list[dict[str, Any]]]] = {
            "by_source_domain": defaultdict(list),
            "by_source": defaultdict(list),
        }
        for record in records:
            grouped["by_source_domain"][record["label"]["source_domain"]].append(record)
            grouped["by_source"][record["label"]["source"]].append(record)
        for group_name, groups in grouped.items():
            for group, group_records in sorted(groups.items()):
                payload = group_metric_values(group_records, variant)
                add_ci(payload, group_records, variant, args, f"{group_name}:{group}")
                out[variant][group_name][group] = payload
    return out


def fmt_value(metric: dict[str, Any]) -> str:
    value = metric.get("value")
    if value is None:
        return "n/a"
    ci = metric.get("ci95")
    if ci:
        return f"{value:.4f} [{ci['low']:.4f}, {ci['high']:.4f}]"
    return f"{value:.4f}"


def write_summary_md(path: Path, metrics: dict[str, Any], variants: list[str], dataset_meta: dict[str, Any] | None, args: argparse.Namespace) -> None:
    lines = [
        "# Stage1 Fair Image-Level Evaluation",
        "",
        "## Protocol",
        "",
        f"- schema: `{args.schema}`",
        f"- max_pixels: `{args.max_pixels}`",
        f"- max_new_tokens: `{args.max_new_tokens}`",
        "- decoding: `greedy`",
        f"- bootstrap samples: `{args.bootstrap_samples}`",
        "",
        "## Overall",
        "",
        "| model | n | valid_schema | verdict_acc | balanced_acc | tampered_recall | authentic_acc | domain_acc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in variants:
        row = metrics[variant]["overall"]
        lines.append(
            f"| {variant} | {row['n']} | {fmt_value(row['valid_schema'])} | "
            f"{fmt_value(row['verdict_accuracy'])} | {fmt_value(row['balanced_accuracy'])} | "
            f"{fmt_value(row['tampered_recall'])} | {fmt_value(row['authentic_accuracy'])} | "
            f"{fmt_value(row['tamper_domain_accuracy'])} |"
        )
    for group_name, title in [("by_source_domain", "By Forgery Type"), ("by_source", "By Source")]:
        lines.extend(["", f"## {title}", ""])
        lines.append("| model | group | n | verdict_acc | balanced_acc | tampered_recall | authentic_acc | domain_acc |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
        groups = sorted({group for variant in variants for group in metrics[variant][group_name]})
        for group in groups:
            for variant in variants:
                row = metrics[variant][group_name].get(group)
                if row is None:
                    continue
                lines.append(
                    f"| {variant} | {group} | {row['n']} | {fmt_value(row['verdict_accuracy'])} | "
                    f"{fmt_value(row['balanced_accuracy'])} | {fmt_value(row['tampered_recall'])} | "
                    f"{fmt_value(row['authentic_accuracy'])} | {fmt_value(row['tamper_domain_accuracy'])} |"
                )
    if dataset_meta:
        lines.extend(["", "## Dataset", ""])
        for key in ["output_root", "total", "per_label", "seed"]:
            if key in dataset_meta:
                lines.append(f"- {key}: `{dataset_meta[key]}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fair Stage1 image-level evaluation with compact/explanation schemas.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--data", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_p600_final/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--labels", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_p600_final/eval_labels.jsonl"))
    parser.add_argument("--dataset-meta", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval_p600_final/dataset_meta.json"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/eval/stage1_p600_final_fair_compact.jsonl"))
    parser.add_argument("--summary-json", type=Path, default=Path("artifacts/eval/stage1_p600_final_fair_compact_summary.json"))
    parser.add_argument("--summary-md", type=Path, default=Path("artifacts/eval/stage1_p600_final_fair_compact_summary.md"))
    parser.add_argument("--variants", default=DEFAULT_VARIANTS)
    parser.add_argument("--schema", choices=sorted(PROMPTS), default="compact")
    parser.add_argument("--max-pixels", type=int, default=524288)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start", type=int)
    parser.add_argument("--end", type=int)
    parser.add_argument("--sample-size", type=int, help="Optional deterministic subset size, e.g. 60 for explanation evaluation.")
    parser.add_argument("--sample-seed", type=int, default=20260711)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260711)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")
    rows = load_eval_rows(args.data, args.labels)
    rows = slice_rows(rows, args.start, args.end)
    if args.limit is not None:
        rows = rows[: args.limit]
    rows = sample_rows(rows, args.sample_size, args.sample_seed)
    variant_specs = parse_variants(args.variants)
    variant_names = [name for name, _ in variant_specs]

    records = load_existing(args.output_jsonl) if args.resume else {}
    if not args.resume and args.output_jsonl.exists():
        args.output_jsonl.unlink()

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=True)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"

    for name, adapter in variant_specs:
        run_variant(name, adapter, args, rows, processor, dtype, device, records)

    missing = [
        row["index"]
        for row in rows
        if set(records.get(int(row["index"]), {}).get("predictions", {})) != set(variant_names)
    ]
    if missing:
        raise RuntimeError(f"missing predictions for {len(missing)} rows, first={missing[:10]}")

    records_list = [records[int(row["index"])] for row in rows]
    metrics = compute_metrics(records_list, variant_names, args)
    dataset_meta = json.loads(args.dataset_meta.read_text(encoding="utf-8")) if args.dataset_meta.exists() else None
    summary = {
        "protocol": {
            "schema": args.schema,
            "max_pixels": args.max_pixels,
            "max_new_tokens": args.max_new_tokens,
            "decoding": "greedy",
            "bootstrap_samples": args.bootstrap_samples,
        },
        "variants": {name: adapter for name, adapter in variant_specs},
        "dataset_meta": dataset_meta,
        "metrics": metrics,
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_md(args.summary_md, metrics, variant_names, dataset_meta, args)
    write_all(args.output_jsonl, records)
    print("wrote_jsonl", args.output_jsonl)
    print("wrote_summary_json", args.summary_json)
    print("wrote_summary_md", args.summary_md)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
