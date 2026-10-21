#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


FULL_REQUIRED_KEYS = {"verdict", "tampered_region", "tamper_domain", "evidence"}
COMPACT_REQUIRED_KEYS = {"verdict", "tamper_domain"}
VALID_VERDICTS = {"authentic", "tampered"}
VALID_DOMAINS = {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_eval_rows(data_path: Path, label_path: Path) -> list[dict[str, Any]]:
    data_rows = load_jsonl(data_path)
    labels = load_jsonl(label_path)
    if len(data_rows) != len(labels):
        raise ValueError(f"data rows ({len(data_rows)}) != labels ({len(labels)})")
    rows = []
    for idx, (data, label) in enumerate(zip(data_rows, labels)):
        images = data.get("images")
        messages = data.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: expected exactly one image")
        image_path = Path(str(images[0]))
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if str(label["image"]) not in str(image_path):
            raise ValueError(f"row {idx}: image mismatch data={image_path} label={label['image']}")
        prompt = str(messages[0]["content"]).replace("<image>", "").strip()
        rows.append({"index": idx, "image": str(image_path), "user_prompt": prompt, "label": label})
    return rows


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    stripped = text.strip()
    candidates = [stripped]
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        candidates.insert(0, fence.group(1).strip())
    brace = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if brace:
        candidates.append(brace.group(0))
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
        except Exception as exc:
            last_error = str(exc)
            continue
        if isinstance(obj, dict):
            return obj, None
    return None, last_error if "last_error" in locals() else "no JSON object found"


def normalize_domain(value: Any) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    if text in VALID_DOMAINS:
        return text
    if "photo" in text or "splic" in text or "composit" in text:
        return "photoshop"
    if "deepfake" in text or "face" in text:
        return "deepfake"
    if "aigc" in text or "inpaint" in text or "ai-generated" in text:
        return "aigc_inpaint"
    if text in {"null", "none", "no", "n/a"}:
        return "none"
    return text or "unknown"


def parse_prediction(raw: str) -> dict[str, Any]:
    obj, error = extract_json_object(raw)
    valid_json = obj is not None
    valid_schema = False
    verdict = "unknown"
    tamper_domain = "unknown"
    if obj is not None:
        keys = set(obj.keys())
        has_valid_keys = keys == FULL_REQUIRED_KEYS or keys == COMPACT_REQUIRED_KEYS
        has_valid_common_values = (
            str(obj.get("verdict", "")).strip().lower() in VALID_VERDICTS
            and normalize_domain(obj.get("tamper_domain")) in VALID_DOMAINS
        )
        has_valid_full_values = (
            keys == FULL_REQUIRED_KEYS
            and isinstance(obj.get("tampered_region"), str)
            and isinstance(obj.get("evidence"), list)
        )
        valid_schema = (
            has_valid_keys
            and has_valid_common_values
            and (keys == COMPACT_REQUIRED_KEYS or has_valid_full_values)
        )
        raw_verdict = str(obj.get("verdict", "")).strip().lower()
        if raw_verdict in VALID_VERDICTS:
            verdict = raw_verdict
        elif raw_verdict in {"yes", "possibly manipulated", "manipulated"}:
            verdict = "tampered"
        elif raw_verdict in {"no", "not tampered", "genuine"}:
            verdict = "authentic"
        tamper_domain = normalize_domain(obj.get("tamper_domain"))
    if verdict == "unknown":
        lowered = raw.lower()
        if "not tampered" in lowered or "authentic" in lowered:
            verdict = "authentic"
        elif "tampered" in lowered or "manipulated" in lowered:
            verdict = "tampered"
    return {
        "raw": raw,
        "valid_json": valid_json,
        "valid_schema": valid_schema,
        "parse_error": error,
        "parsed": obj,
        "pred_verdict": verdict,
        "pred_tamper_domain": tamper_domain,
    }


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
    messages = [{"role": "user", "content": [{"type": "image", "image": image_path}, {"type": "text", "text": prompt}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(device)
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()


def run_variant(name: str, base_model: str, adapter: str | None, processor, rows: list[dict[str, Any]], dtype: torch.dtype, device: str, max_new_tokens: int) -> list[str]:
    print("loading", name, adapter or base_model)
    model = load_model(base_model, adapter, dtype, device)
    outputs = []
    for row in rows:
        print("infer", name, row["index"], row["label"]["source"], row["label"]["verdict"], row["image"])
        outputs.append(infer(model, processor, row["image"], row["user_prompt"], device, max_new_tokens))
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return outputs


def pct(num: int, den: int) -> str:
    if den == 0:
        return "n/a"
    return f"{num / den:.4f}"


def group_metrics(records: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    total = len(records)
    tampered = [r for r in records if r["label"]["verdict"] == "tampered"]
    authentic = [r for r in records if r["label"]["verdict"] == "authentic"]
    valid_json = sum(r["predictions"][variant]["valid_json"] for r in records)
    valid_schema = sum(r["predictions"][variant]["valid_schema"] for r in records)
    verdict_correct = sum(r["predictions"][variant]["pred_verdict"] == r["label"]["verdict"] for r in records)
    tampered_hit = sum(r["predictions"][variant]["pred_verdict"] == "tampered" for r in tampered)
    authentic_hit = sum(r["predictions"][variant]["pred_verdict"] == "authentic" for r in authentic)
    domain_hit = sum(r["predictions"][variant]["pred_tamper_domain"] == r["label"]["tamper_domain"] for r in tampered)
    return {
        "n": total,
        "valid_json": {"correct": valid_json, "total": total, "value": pct(valid_json, total)},
        "valid_schema": {"correct": valid_schema, "total": total, "value": pct(valid_schema, total)},
        "verdict_accuracy": {"correct": verdict_correct, "total": total, "value": pct(verdict_correct, total)},
        "tampered_recall": {"correct": tampered_hit, "total": len(tampered), "value": pct(tampered_hit, len(tampered))},
        "authentic_accuracy": {"correct": authentic_hit, "total": len(authentic), "value": pct(authentic_hit, len(authentic))},
        "tamper_domain_accuracy": {"correct": domain_hit, "total": len(tampered), "value": pct(domain_hit, len(tampered))},
    }


def compute_metrics(records: list[dict[str, Any]], variants: list[str]) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for variant in variants:
        metrics[variant] = {"overall": group_metrics(records, variant), "by_source_domain": {}, "by_source": {}}
        domain_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        source_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            domain_groups[record["label"]["source_domain"]].append(record)
            source_groups[record["label"]["source"]].append(record)
        for name, group in sorted(domain_groups.items()):
            metrics[variant]["by_source_domain"][name] = group_metrics(group, variant)
        for name, group in sorted(source_groups.items()):
            metrics[variant]["by_source"][name] = group_metrics(group, variant)
    return metrics


def fmt_metric(row: dict[str, Any], key: str) -> str:
    metric = row[key]
    return f"{metric['value']} ({metric['correct']}/{metric['total']})"


def write_summary(path: Path, metrics: dict[str, Any], records: list[dict[str, Any]], variants: list[str], dataset_meta: dict[str, Any] | None) -> None:
    lines = ["# Stage1 Multisource Image-Level Evaluation", ""]
    lines.append("## Overall")
    lines.append("")
    lines.append("| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for variant in variants:
        row = metrics[variant]["overall"]
        lines.append(
            f"| {variant} | {row['n']} | {fmt_metric(row, 'valid_json')} | {fmt_metric(row, 'valid_schema')} | "
            f"{fmt_metric(row, 'verdict_accuracy')} | {fmt_metric(row, 'tampered_recall')} | "
            f"{fmt_metric(row, 'authentic_accuracy')} | {fmt_metric(row, 'tamper_domain_accuracy')} |"
        )

    for group_name, title in [("by_source_domain", "By Forgery Type"), ("by_source", "By Source")]:
        lines.extend(["", f"## {title}", ""])
        lines.append("| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |")
        lines.append("|---|---|---:|---:|---:|---:|---:|")
        groups = sorted({g for variant in variants for g in metrics[variant][group_name]})
        for group in groups:
            for variant in variants:
                row = metrics[variant][group_name].get(group)
                if row is None:
                    continue
                lines.append(
                    f"| {variant} | {group} | {row['n']} | {fmt_metric(row, 'verdict_accuracy')} | "
                    f"{fmt_metric(row, 'tampered_recall')} | {fmt_metric(row, 'authentic_accuracy')} | "
                    f"{fmt_metric(row, 'tamper_domain_accuracy')} |"
                )

    if dataset_meta:
        lines.extend(["", "## Dataset Build", ""])
        lines.append(f"- total: `{dataset_meta.get('total')}`")
        lines.append(f"- per_label: `{dataset_meta.get('per_label')}`")
        lines.append(f"- seed: `{dataset_meta.get('seed')}`")
        skipped = dataset_meta.get("skipped_sources") or []
        if skipped:
            lines.extend(["", "### Skipped Sources", "", "| source | reason |", "|---|---|"])
            for item in skipped:
                lines.append(f"| {item.get('source')} | {item.get('reason')} |")

    p500 = metrics.get("json_p500", {}).get("overall")
    conclusion = "not evaluated"
    if p500:
        conclusion = (
            "supports cross-type image-level discrimination on the sampled subsets"
            if p500["verdict_accuracy"]["correct"] > 0 and len(metrics["json_p500"]["by_source_domain"]) >= 3
            else "is inconclusive on cross-type image-level discrimination"
        )
    lines.extend(["", "## Conclusion", "", f"`json_p500` {conclusion}."])

    lines.extend(["", "## Predictions", ""])
    lines.append("| idx | source | type | label | " + " | ".join(variants) + " | image |")
    lines.append("|---:|---|---|---|" + "|".join("---" for _ in variants) + "|---|")
    for record in records:
        label = f"{record['label']['verdict']} / {record['label']['tamper_domain']}"
        preds = []
        for variant in variants:
            pred = record["predictions"][variant]
            valid = "json" if pred["valid_json"] else "non-json"
            preds.append(f"{pred['pred_verdict']} / {pred['pred_tamper_domain']} / {valid}")
        lines.append(
            f"| {record['index']} | {record['label']['source']} | {record['label']['source_domain']} | {label} | "
            f"{' | '.join(preds)} | `{record['image']}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate base and frozen json_p500 on multisource Stage1 data.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--json-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p500_json")
    parser.add_argument("--data", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--labels", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval/eval_labels.jsonl"))
    parser.add_argument("--dataset-meta", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval/dataset_meta.json"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/eval/stage1_multisource_base_vs_p500.jsonl"))
    parser.add_argument("--summary-md", type=Path, default=Path("artifacts/eval/stage1_multisource_base_vs_p500_summary.md"))
    parser.add_argument("--max-new-tokens", type=int, default=420)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_eval_rows(args.data, args.labels)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True)
    specs = [("base", None), ("json_p500", args.json_adapter)]
    outputs = {
        name: run_variant(name, args.base_model, adapter, processor, rows, dtype, device, args.max_new_tokens)
        for name, adapter in specs
    }
    records = []
    for idx, row in enumerate(rows):
        predictions = {name: parse_prediction(outputs[name][idx]) for name, _ in specs}
        records.append({**row, "predictions": predictions})
    variants = [name for name, _ in specs]
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
