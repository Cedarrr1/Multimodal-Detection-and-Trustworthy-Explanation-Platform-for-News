#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_stage2_relation_v3_data import RELATIONS, VERIFIABILITY, aggregate_relation, validate_target


UNKNOWN = "unknown"
RELATION_ORDER = ["supports", "contradicts", "unrelated", "insufficient"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_all(path: Path, records: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for key in sorted(records):
            f.write(json.dumps(records[key], ensure_ascii=False) + "\n")
    tmp.replace(path)


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    stripped = text.strip()
    candidates = [stripped]
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        candidates.insert(0, fence.group(1).strip())
    brace = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if brace:
        candidates.append(brace.group(0))
    last_error = None
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
        except Exception as exc:
            last_error = str(exc)
            continue
        if isinstance(obj, dict):
            return obj, None
    return None, last_error or "no JSON object found"


def normalize_relation(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in RELATIONS:
        return text
    if "support" in text or "match" in text or "consistent" in text:
        return "supports"
    if "contradict" in text or "conflict" in text or "mismatch" in text or "opposite" in text:
        return "contradicts"
    if "unrelated" in text or "irrelevant" in text or "different scene" in text:
        return "unrelated"
    if "insufficient" in text or "not verifiable" in text or "cannot verify" in text or "uncertain" in text:
        return "insufficient"
    return UNKNOWN


def normalize_verifiability(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in VERIFIABILITY:
        return text
    if "not" in text or "insufficient" in text or "cannot" in text:
        return "not_verifiable"
    if "verifiable" in text or "visible" in text:
        return "verifiable"
    return UNKNOWN


def parse_prediction(raw: str) -> dict[str, Any]:
    obj, error = extract_json_object(raw)
    parsed = {"claims": [], "overall_relation": UNKNOWN}
    valid_schema = False
    if isinstance(obj, dict):
        raw_claims = obj.get("claims")
        if isinstance(raw_claims, list):
            for idx, item in enumerate(raw_claims, start=1):
                if not isinstance(item, dict):
                    continue
                evidence = item.get("visual_evidence")
                attrs = item.get("evidence_attributes")
                parsed["claims"].append(
                    {
                        "claim_id": str(item.get("claim_id") or f"C{idx}").strip() or f"C{idx}",
                        "claim": str(item.get("claim") or "").strip(),
                        "visual_verifiability": normalize_verifiability(item.get("visual_verifiability")),
                        "relation": normalize_relation(item.get("relation")),
                        "visual_evidence": evidence if isinstance(evidence, list) else [],
                        "evidence_attributes": attrs if isinstance(attrs, list) else [],
                    }
                )
        parsed["overall_relation"] = normalize_relation(obj.get("overall_relation"))
        if parsed["overall_relation"] == UNKNOWN and parsed["claims"]:
            claim_relations = [item["relation"] for item in parsed["claims"]]
            if all(relation in RELATIONS for relation in claim_relations):
                parsed["overall_relation"] = aggregate_relation(parsed["claims"])
        try:
            validate_target(parsed)
            valid_schema = True
        except Exception:
            valid_schema = False
    return {
        "raw": raw,
        "valid_json": obj is not None,
        "valid_schema": valid_schema,
        "parse_error": error,
        "parsed": obj,
        "pred": parsed,
    }


def load_rows(data_path: Path, manifest_path: Path, limit: int | None) -> list[dict[str, Any]]:
    data_rows = load_jsonl(data_path)
    manifest_rows = load_jsonl(manifest_path)
    if len(data_rows) != len(manifest_rows):
        raise ValueError("data and manifest row counts differ")
    rows = []
    for idx, (data, manifest) in enumerate(zip(data_rows, manifest_rows)):
        if data["id"] != manifest["id"]:
            raise ValueError(f"row {idx}: id mismatch")
        image = Path(str(data["images"][0]))
        if not image.exists():
            raise FileNotFoundError(image)
        rows.append(
            {
                "index": idx,
                "id": data["id"],
                "image": str(image),
                "prompt": str(data["messages"][0]["content"]),
                "target": validate_target(dict(manifest["target"])),
                "manifest": manifest,
            }
        )
    return rows[:limit] if limit is not None else rows


def load_model(args: argparse.Namespace):
    import torch
    from peft import PeftModel
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    local_files_only = not args.allow_network
    device = args.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.dtype]
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=local_files_only)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    return torch, process_vision_info, processor, model, device


def infer_batch(
    torch_mod,
    process_vision_info,
    processor,
    model,
    device: str,
    batch: list[dict[str, Any]],
    max_new_tokens: int,
    max_pixels: int | None,
) -> list[str]:
    messages_list = []
    for row in batch:
        image = {"type": "image", "image": row["image"]}
        if max_pixels is not None:
            image["max_pixels"] = max_pixels
        prompt = str(row["prompt"]).replace("<image>", "").strip()
        messages_list.append([{"role": "user", "content": [image, {"type": "text", "text": prompt}]}])
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
    with torch_mod.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)


def run_inference(args: argparse.Namespace, rows: list[dict[str, Any]], records: dict[str, dict[str, Any]]) -> None:
    pending = [row for row in rows if row["id"] not in records]
    if not pending:
        return
    model_bundle = load_model(args)
    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        labels = ", ".join(
            f"{row['id']}:{row['manifest'].get('case_type')}:{row['target']['overall_relation']}" for row in batch
        )
        print(f"infer batch {start + 1}-{start + len(batch)}/{len(pending)} [{labels}]", flush=True)
        raw_outputs = infer_batch(*model_bundle, batch, args.max_new_tokens, args.max_pixels)
        for row, raw in zip(batch, raw_outputs):
            records[row["id"]] = {
                "id": row["id"],
                "index": row["index"],
                "image": row["image"],
                "case_type": row["manifest"].get("case_type"),
                "difficulty": row["manifest"].get("difficulty"),
                "counterfactual_pair_id": row["manifest"].get("counterfactual_pair_id"),
                "counterfactual_pair_role": row["manifest"].get("counterfactual_pair_role"),
                "target": row["target"],
                "prediction": parse_prediction(raw.strip()),
            }
        write_all(args.output_jsonl, records)


def safe_div(num: int | float, den: int | float) -> float | None:
    return float(num) / float(den) if den else None


def metric(correct: int, total: int) -> dict[str, Any]:
    return {"correct": correct, "total": total, "value": safe_div(correct, total)}


def precision_recall_f1(tp: int, fp: int, fn: int) -> dict[str, Any]:
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    if precision is None or recall is None or precision + recall == 0:
        f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def claim_alignment(target: dict[str, Any], pred: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any] | None]]:
    pred_by_id = {str(item.get("claim_id")): item for item in pred.get("claims", []) if isinstance(item, dict)}
    aligned = []
    for item in target["claims"]:
        aligned.append((item, pred_by_id.get(item["claim_id"])))
    return aligned


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    valid_json = sum(bool(record["prediction"]["valid_json"]) for record in records)
    valid_schema = sum(bool(record["prediction"]["valid_schema"]) for record in records)
    overall_correct = 0
    confusion: dict[str, Counter] = defaultdict(Counter)
    difficulty_stats: dict[str, Counter] = defaultdict(Counter)
    case_stats: dict[str, Counter] = defaultdict(Counter)
    claim_total = 0
    claim_relation_correct = 0
    verifiability_correct = 0
    attr_exact_correct = 0
    attr_overlap_correct = 0

    for record in records:
        target = record["target"]
        pred = record["prediction"]["pred"]
        truth = target["overall_relation"]
        guess = pred["overall_relation"]
        hit = guess == truth
        overall_correct += int(hit)
        confusion[truth][guess] += 1

        difficulty = str(record.get("difficulty") or "unknown")
        case_type = str(record.get("case_type") or "unknown")
        difficulty_stats[difficulty]["total"] += 1
        difficulty_stats[difficulty]["correct"] += int(hit)
        case_stats[case_type]["total"] += 1
        case_stats[case_type]["correct"] += int(hit)

        for target_claim, pred_claim in claim_alignment(target, pred):
            claim_total += 1
            if pred_claim is None:
                continue
            claim_relation_correct += int(pred_claim.get("relation") == target_claim["relation"])
            verifiability_correct += int(pred_claim.get("visual_verifiability") == target_claim["visual_verifiability"])
            target_attrs = set(target_claim["evidence_attributes"])
            pred_attrs = {str(item).strip().lower() for item in pred_claim.get("evidence_attributes", [])}
            attr_exact_correct += int(pred_attrs == target_attrs)
            attr_overlap_correct += int(bool(pred_attrs & target_attrs))

    per_relation = {}
    f1_values = []
    recall_values = []
    for relation in RELATION_ORDER:
        tp = confusion[relation][relation]
        fp = sum(confusion[truth][relation] for truth in RELATION_ORDER if truth != relation)
        fn = sum(count for guess, count in confusion[relation].items() if guess != relation)
        payload = precision_recall_f1(tp, fp, fn)
        per_relation[relation] = payload
        if payload["f1"] is not None:
            f1_values.append(payload["f1"])
        if payload["recall"] is not None:
            recall_values.append(payload["recall"])

    pair_stats = summarize_pairs(records)
    return {
        "n": total,
        "json": {
            "valid_json": metric(valid_json, total),
            "valid_schema": metric(valid_schema, total),
        },
        "overall_relation": {
            "accuracy": metric(overall_correct, total),
            "macro_f1": {"value": sum(f1_values) / len(f1_values) if f1_values else None},
            "balanced_accuracy": {"value": sum(recall_values) / len(recall_values) if recall_values else None},
            "per_relation": per_relation,
            "confusion": {key: dict(value) for key, value in sorted(confusion.items())},
        },
        "claim_level": {
            "claim_relation_accuracy": metric(claim_relation_correct, claim_total),
            "visual_verifiability_accuracy": metric(verifiability_correct, claim_total),
            "evidence_attribute_exact_accuracy": metric(attr_exact_correct, claim_total),
            "evidence_attribute_overlap_accuracy": metric(attr_overlap_correct, claim_total),
        },
        "by_difficulty": {
            key: metric(value["correct"], value["total"]) for key, value in sorted(difficulty_stats.items())
        },
        "by_case_type": {key: metric(value["correct"], value["total"]) for key, value in sorted(case_stats.items())},
        "counterfactual_pairs": pair_stats,
    }


def summarize_pairs(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        pair_id = record.get("counterfactual_pair_id")
        if pair_id:
            by_pair[str(pair_id)].append(record)
    total = 0
    correct = 0
    malformed = 0
    for rows in by_pair.values():
        if len(rows) != 2:
            malformed += 1
            continue
        total += 1
        correct += int(
            all(row["prediction"]["pred"]["overall_relation"] == row["target"]["overall_relation"] for row in rows)
        )
    return {
        "pair_accuracy": metric(correct, total),
        "malformed_pairs": malformed,
    }


def fmt_metric(payload: dict[str, Any] | None) -> str:
    if not payload:
        return "n/a"
    value = payload.get("value")
    if value is None:
        return "n/a"
    if "correct" in payload and "total" in payload:
        return f"{value:.4f} ({payload['correct']}/{payload['total']})"
    return f"{value:.4f}"


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Stage2 Relation V3 Evaluation",
        "",
        f"- total: `{summary['n']}`",
        f"- valid JSON: `{fmt_metric(summary['json']['valid_json'])}`",
        f"- valid schema: `{fmt_metric(summary['json']['valid_schema'])}`",
        f"- relation accuracy: `{fmt_metric(summary['overall_relation']['accuracy'])}`",
        f"- relation Macro-F1: `{fmt_metric(summary['overall_relation']['macro_f1'])}`",
        f"- relation balanced accuracy: `{fmt_metric(summary['overall_relation']['balanced_accuracy'])}`",
        f"- claim relation accuracy: `{fmt_metric(summary['claim_level']['claim_relation_accuracy'])}`",
        f"- visual verifiability accuracy: `{fmt_metric(summary['claim_level']['visual_verifiability_accuracy'])}`",
        f"- evidence attribute exact accuracy: `{fmt_metric(summary['claim_level']['evidence_attribute_exact_accuracy'])}`",
        f"- evidence attribute overlap accuracy: `{fmt_metric(summary['claim_level']['evidence_attribute_overlap_accuracy'])}`",
        f"- counterfactual pair accuracy: `{fmt_metric(summary['counterfactual_pairs']['pair_accuracy'])}`",
        f"- malformed counterfactual pairs: `{summary['counterfactual_pairs']['malformed_pairs']}`",
        "",
        "## Per-Relation",
        "",
        "| relation | precision | recall | f1 | tp | fp | fn |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for relation in RELATION_ORDER:
        payload = summary["overall_relation"]["per_relation"][relation]
        lines.append(
            f"| `{relation}` | {payload['precision'] if payload['precision'] is not None else 'n/a'} | "
            f"{payload['recall'] if payload['recall'] is not None else 'n/a'} | "
            f"{payload['f1'] if payload['f1'] is not None else 'n/a'} | "
            f"{payload['tp']} | {payload['fp']} | {payload['fn']} |"
        )
    lines.extend(["", "## By Difficulty", "", "| difficulty | accuracy |", "|---|---:|"])
    for key, payload in summary["by_difficulty"].items():
        lines.append(f"| `{key}` | {fmt_metric(payload)} |")
    lines.extend(["", "## By Case Type", "", "| case_type | accuracy |", "|---|---:|"])
    for key, payload in summary["by_case_type"].items():
        lines.append(f"| `{key}` | {fmt_metric(payload)} |")
    lines.extend(["", "## Confusion", "", "```json", json.dumps(summary["overall_relation"]["confusion"], ensure_ascii=False, indent=2), "```"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    rows = load_rows(args.data, args.manifest, args.limit)
    records = {row["id"]: row for row in load_jsonl(args.output_jsonl)} if args.resume else {}
    if not args.resume and args.output_jsonl.exists():
        args.output_jsonl.unlink()
        records = {}
    if not args.skip_infer:
        run_inference(args, rows, records)
    missing = [row["id"] for row in rows if row["id"] not in records]
    if missing:
        raise ValueError(f"missing predictions for {len(missing)} rows; first={missing[0]}")
    ordered = [records[row["id"]] for row in rows]
    summary = summarize(ordered)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary_md(args.summary_md, summary)
    write_all(args.output_jsonl, records)
    print("wrote", args.output_jsonl)
    print("wrote", args.summary_json)
    print("wrote", args.summary_md)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Stage2 relation-v3 claim-level predictions.")
    parser.add_argument("--data", type=Path, default=Path("artifacts/lora_data/stage2_relation_v3_final_json/llamafactory_qwen_vl_sft.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/lora_data/stage2_relation_v3_final_json/manifest.jsonl"))
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/eval/stage2_relation_v3_predictions.jsonl"))
    parser.add_argument("--summary-json", type=Path, default=Path("artifacts/eval/stage2_relation_v3_summary.json"))
    parser.add_argument("--summary-md", type=Path, default=Path("artifacts/eval/stage2_relation_v3_summary.md"))
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--adapter", default="artifacts/lora_runs/qwen2_5_vl_relation_v3_claim_json")
    parser.add_argument("--device")
    parser.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--max-new-tokens", type=int, default=384)
    parser.add_argument("--max-pixels", type=int, default=524288)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--skip-infer", action="store_true")
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")
    return args


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
