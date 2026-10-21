#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


METRIC_KEYS = ["iou", "dice", "pixel_precision", "pixel_recall", "pixel_f1"]
GATE_DOMAINS = ["photoshop", "aigc_editing"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize_domain(value: Any) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    if text in {"photoshop", "deepfake", "aigc_inpaint", "aigc_editing", "none", "unknown"}:
        return text
    if "photo" in text or "splic" in text or "composit" in text:
        return "photoshop"
    if "deepfake" in text or "face" in text:
        return "deepfake"
    if "aigc" in text or "inpaint" in text or "ai-generated" in text:
        return "aigc_inpaint"
    if text in {"null", "no", "n/a"}:
        return "none"
    return text or "unknown"


def domain_matches(predicted: str, target: str) -> bool:
    if target == "aigc_editing":
        return predicted in {"aigc_editing", "aigc_inpaint"}
    return predicted == target


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def sample_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["domain"]), str(row.get("sample_key") or Path(str(row.get("image", ""))).stem)


def method_metrics(record: dict[str, Any], method: str) -> dict[str, float]:
    payload = record["methods"][method]
    if payload.get("status") != "run":
        payload = record["methods"]["bbox_mask_baseline"]
    return {key: float(payload["metrics"][key]) for key in METRIC_KEYS}


def sam_score(record: dict[str, Any]) -> float | None:
    value = record["methods"].get("sam_refinement", {}).get("score")
    return float(value) if value is not None else None


def predicted_domain_for(record: dict[str, Any], predictions: dict[str, dict[str, Any]]) -> str:
    prediction = predictions.get(str(record["id"]))
    if prediction is None:
        return "unknown"
    return normalize_domain(prediction.get("predicted_domain") or prediction.get("pred_tamper_domain"))


def predicted_strategy(record: dict[str, Any], predictions: dict[str, dict[str, Any]]) -> tuple[str, str]:
    predicted_domain = predicted_domain_for(record, predictions)
    if predicted_domain in {"photoshop", "aigc_inpaint", "aigc_editing"}:
        return "sam_refinement", predicted_domain
    return "bbox_mask_baseline", predicted_domain


def gated_strategy(
    record: dict[str, Any],
    predictions: dict[str, dict[str, Any]],
    thresholds: dict[str, float],
) -> tuple[str, str, str]:
    predicted_domain = predicted_domain_for(record, predictions)
    target_domain = str(record["domain"])
    score = sam_score(record)
    if target_domain == "deepfake":
        return "bbox_mask_baseline", predicted_domain, "deepfake_forced_bbox"
    if target_domain in GATE_DOMAINS:
        threshold = thresholds[target_domain]
        if domain_matches(predicted_domain, target_domain) and score is not None and score >= threshold:
            return "sam_refinement", predicted_domain, "domain_match_and_score_pass"
        if not domain_matches(predicted_domain, target_domain):
            return "bbox_mask_baseline", predicted_domain, "domain_mismatch"
        return "bbox_mask_baseline", predicted_domain, "score_below_threshold"
    return "bbox_mask_baseline", predicted_domain, "unknown_domain_fallback"


def build_row(record: dict[str, Any], method: str, predicted_domain: str | None = None, gate_reason: str | None = None) -> dict[str, Any]:
    return {
        "id": record["id"],
        "domain": record["domain"],
        "source": record.get("source") or record.get("source_dataset"),
        "selected_method": method,
        "predicted_domain": predicted_domain,
        "sam_score": sam_score(record),
        "gate_reason": gate_reason,
        **method_metrics(record, method),
    }


def evaluate_method(
    records: list[dict[str, Any]],
    method_name: str,
    predictions: dict[str, dict[str, Any]],
    thresholds: dict[str, float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        if method_name == "bbox_mask_baseline":
            rows.append(build_row(record, "bbox_mask_baseline"))
        elif method_name == "sam_best_of3":
            rows.append(build_row(record, "sam_refinement"))
        elif method_name == "domain_aware_predicted":
            method, predicted_domain = predicted_strategy(record, predictions)
            rows.append(build_row(record, method, predicted_domain))
        elif method_name == "domain_aware_predicted_gate":
            method, predicted_domain, reason = gated_strategy(record, predictions, thresholds)
            rows.append(build_row(record, method, predicted_domain, reason))
        else:
            raise ValueError(f"unknown method: {method_name}")
        rows[-1]["method"] = method_name
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_domain[str(row["domain"])].append(row)

    def group_summary(group: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"n": len(group)}
        for key in METRIC_KEYS:
            payload[key] = mean([float(row[key]) for row in group])
        payload["selected_method_counts"] = dict(sorted(Counter(str(row["selected_method"]) for row in group).items()))
        payload["gate_reason_counts"] = dict(sorted(Counter(str(row.get("gate_reason")) for row in group if row.get("gate_reason")).items()))
        return payload

    return {
        "overall": group_summary(rows),
        "by_domain": {domain: group_summary(group) for domain, group in sorted(by_domain.items())},
    }


def bootstrap_ci(rows: list[dict[str, Any]], metric: str, samples: int, seed: int) -> dict[str, float] | None:
    if not rows or samples <= 0:
        return None
    rng = random.Random(seed)
    values = []
    for _ in range(samples):
        sampled = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        values.append(mean([float(row[metric]) for row in sampled]))
    values.sort()
    lo = values[int(0.025 * (len(values) - 1))]
    hi = values[int(0.975 * (len(values) - 1))]
    return {"low": lo, "high": hi}


def add_ci(summary: dict[str, Any], rows: list[dict[str, Any]], samples: int, seed: int) -> None:
    for key in METRIC_KEYS:
        ci = bootstrap_ci(rows, key, samples, seed + len(key) * 7919)
        if ci is not None:
            summary["overall"][f"{key}_ci95"] = ci
    by_domain_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_domain_rows[str(row["domain"])].append(row)
    for domain, group in by_domain_rows.items():
        for key in METRIC_KEYS:
            ci = bootstrap_ci(group, key, samples, seed + len(domain + key) * 3571)
            if ci is not None:
                summary["by_domain"][domain][f"{key}_ci95"] = ci


def tune_threshold_for_domain(
    records: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    domain: str,
    candidate_thresholds: list[float],
) -> dict[str, Any]:
    domain_records = [record for record in records if record["domain"] == domain]
    best_threshold = candidate_thresholds[0]
    best_iou = -1.0
    search_rows = []
    for threshold in candidate_thresholds:
        thresholds = {"photoshop": 1.0, "aigc_editing": 1.0}
        thresholds[domain] = threshold
        rows = []
        for record in domain_records:
            method, predicted_domain, reason = gated_strategy(record, predictions, thresholds)
            rows.append(build_row(record, method, predicted_domain, reason))
        iou = mean([float(row["iou"]) for row in rows])
        search_rows.append({"threshold": threshold, "mean_iou": iou})
        if iou > best_iou:
            best_iou = iou
            best_threshold = threshold
    return {"domain": domain, "threshold": best_threshold, "mean_iou": best_iou, "search": search_rows}


def threshold_grid(start: float, end: float, step: float) -> list[float]:
    values = []
    current = start
    while current <= end + 1e-9:
        values.append(round(current, 2))
        current += step
    return values


def split_test_records(args: argparse.Namespace, records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p150_samples = load_jsonl(args.p150_samples)
    p150_by_id = {str(row["id"]): row for row in p150_samples}
    dev_manifest = load_jsonl(args.dev_manifest)
    dev_keys = {sample_key(row) for row in dev_manifest}
    overlapping_ids = {row_id for row_id, row in p150_by_id.items() if sample_key(row) in dev_keys}
    remaining = [record for record in records if str(record["id"]) not in overlapping_ids]

    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in remaining:
        by_domain[str(record["domain"])].append(record)

    test: list[dict[str, Any]] = []
    test_counts: dict[str, int] = {}
    for domain in sorted(by_domain):
        group = by_domain[domain]
        if len(group) < args.test_per_domain:
            raise RuntimeError(f"not enough p90 candidates for {domain}: need {args.test_per_domain}, have {len(group)}")
        chosen = group[: args.test_per_domain]
        test.extend(chosen)
        test_counts[domain] = len(chosen)

    return test, {
        "p150_n": len(records),
        "p60_manifest_n": len(dev_manifest),
        "p150_overlap_with_p60": len(overlapping_ids),
        "p150_remaining_after_excluding_p60": len(remaining),
        "test_per_domain": args.test_per_domain,
        "test_counts": test_counts,
        "test_n": len(test),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    dev_records = load_jsonl(args.dev_results)
    records = load_jsonl(args.region_results)
    predictions = {str(row["id"]): row for row in load_jsonl(args.domain_predictions)}
    dev_predictions_path = args.dev_domain_predictions or args.domain_predictions
    dev_predictions = {str(row["id"]): row for row in load_jsonl(dev_predictions_path)}
    missing = sorted({str(record["id"]) for record in records} - set(predictions))
    if missing:
        raise RuntimeError(f"missing predictions for {len(missing)} p150 records; first={missing[:10]}")
    missing_dev = sorted({str(record["id"]) for record in dev_records} - set(dev_predictions))
    if missing_dev:
        print(f"warning: missing predictions for {len(missing_dev)} p60 dev records; they will use unknown fallback")

    test_records, split_meta = split_test_records(args, records)
    split_meta["dev_n"] = len(dev_records)

    grid = threshold_grid(args.threshold_start, args.threshold_end, args.threshold_step)
    tuned = {
        domain: tune_threshold_for_domain(dev_records, dev_predictions, domain, grid)
        for domain in GATE_DOMAINS
    }
    thresholds = {domain: tuned[domain]["threshold"] for domain in GATE_DOMAINS}

    method_names = [
        "bbox_mask_baseline",
        "sam_best_of3",
        "domain_aware_predicted",
        "domain_aware_predicted_gate",
    ]
    dev_method_rows = {
        method: evaluate_method(dev_records, method, dev_predictions, thresholds)
        for method in method_names
    }
    test_method_rows = {
        method: evaluate_method(test_records, method, predictions, thresholds)
        for method in method_names
    }

    dev_summary = {method: summarize(rows) for method, rows in dev_method_rows.items()}
    test_summary = {method: summarize(rows) for method, rows in test_method_rows.items()}
    for idx, method in enumerate(method_names):
        add_ci(test_summary[method], test_method_rows[method], args.bootstrap_samples, args.bootstrap_seed + idx * 1009)

    all_rows = []
    for split_name, method_rows in [("dev_p60", dev_method_rows), ("test_p90", test_method_rows)]:
        for method, rows in method_rows.items():
            for row in rows:
                all_rows.append({"split": split_name, **row})

    bbox = test_summary["bbox_mask_baseline"]["overall"]
    gated = test_summary["domain_aware_predicted_gate"]["overall"]
    gains = {
        "iou_abs_gain_vs_bbox": gated["iou"] - bbox["iou"],
        "pixel_f1_abs_gain_vs_bbox": gated["pixel_f1"] - bbox["pixel_f1"],
    }

    prediction_stats = summarize_predictions(test_records, predictions)
    summary = {
        "name": args.output_dir.name,
        "boundary": "GT bbox prompt conditioned mask refinement; not automatic forged-region discovery.",
        "region_results": str(args.region_results),
        "domain_predictions": str(args.domain_predictions),
        "dev_results": str(args.dev_results),
        "dev_domain_predictions": str(dev_predictions_path),
        "dev_manifest": str(args.dev_manifest),
        "p150_samples": str(args.p150_samples),
        "split": split_meta,
        "threshold_search": tuned,
        "locked_thresholds": thresholds,
        "dev_p60_methods": dev_summary,
        "test_p90_methods": test_summary,
        "test_p90_prediction_stats": prediction_stats,
        "test_p90_gains": gains,
        "bootstrap_samples": args.bootstrap_samples,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "quality_gate_results.jsonl"
    summary_json = args.output_dir / "quality_gate_summary.json"
    summary_md = args.output_dir / "quality_gate_summary.md"
    results_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in all_rows), encoding="utf-8")
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_md.write_text(render_md(summary), encoding="utf-8")
    return summary


def summarize_predictions(records: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    hits = 0
    for record in records:
        pred = predicted_domain_for(record, predictions)
        counts[pred] += 1
        hits += int(domain_matches(pred, str(record["domain"])))
    return {
        "n": len(records),
        "domain_accuracy": hits / len(records) if records else None,
        "predicted_domain_counts": dict(sorted(counts.items())),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.4f}"


def fmt_ci(payload: dict[str, Any], key: str) -> str:
    value = fmt(payload.get(key))
    ci = payload.get(f"{key}_ci95")
    if not ci:
        return value
    return f"{value} [{ci['low']:.4f}, {ci['high']:.4f}]"


def render_md(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['name']} Region Quality Gate",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "## Split And Thresholds",
        "",
        f"- dev p60: `{summary['split']['dev_n']}`",
        f"- test p90: `{summary['split']['test_n']}`",
        f"- Photoshop threshold: `{summary['locked_thresholds']['photoshop']:.2f}`",
        f"- AIGC threshold: `{summary['locked_thresholds']['aigc_editing']:.2f}`",
        "",
        "## Test p90",
        "",
        "| method | n | IoU | F1 | Precision | Recall |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method, payload in summary["test_p90_methods"].items():
        overall = payload["overall"]
        lines.append(
            f"| {method} | {overall['n']} | {fmt_ci(overall, 'iou')} | "
            f"{fmt_ci(overall, 'pixel_f1')} | {fmt_ci(overall, 'pixel_precision')} | "
            f"{fmt_ci(overall, 'pixel_recall')} |"
        )
    lines.extend(
        [
            "",
            "## Test p90 By Domain",
            "",
            "| domain | method | n | IoU | F1 |",
            "|---|---|---:|---:|---:|",
        ]
    )
    domains = sorted({domain for payload in summary["test_p90_methods"].values() for domain in payload["by_domain"]})
    for domain in domains:
        for method, payload in summary["test_p90_methods"].items():
            group = payload["by_domain"].get(domain)
            if group is None:
                continue
            lines.append(f"| {domain} | {method} | {group['n']} | {fmt_ci(group, 'iou')} | {fmt_ci(group, 'pixel_f1')} |")
    gains = summary["test_p90_gains"]
    pred = summary["test_p90_prediction_stats"]
    lines.extend(
        [
            "",
            "## Gains",
            "",
            f"- gated IoU gain vs bbox: `{gains['iou_abs_gain_vs_bbox']:.4f}`",
            f"- gated F1 gain vs bbox: `{gains['pixel_f1_abs_gain_vs_bbox']:.4f}`",
            "",
            "## Domain Predictions",
            "",
            f"- test p90 domain accuracy: `{fmt(pred['domain_accuracy'])}`",
            f"- predicted domain counts: `{pred['predicted_domain_counts']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune p60 SAM quality gates and evaluate frozen p90 region metrics.")
    parser.add_argument("--dev-results", type=Path, default=Path("artifacts/region_eval/region_eval_p60/results.jsonl"))
    parser.add_argument("--dev-domain-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p60/domain_predictions_domain_boost_compact.jsonl"))
    parser.add_argument("--region-results", type=Path, default=Path("artifacts/region_eval/region_eval_p150/results.jsonl"))
    parser.add_argument("--domain-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p150/domain_predictions_domain_boost_compact.jsonl"))
    parser.add_argument("--p150-samples", type=Path, default=Path("artifacts/region_eval/region_eval_p150/samples.jsonl"))
    parser.add_argument("--dev-manifest", type=Path, default=Path("artifacts/region_eval/region_eval_p60/manifest.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/region_eval/region_eval_p150_quality_gate"))
    parser.add_argument("--test-per-domain", type=int, default=30)
    parser.add_argument("--threshold-start", type=float, default=0.50)
    parser.add_argument("--threshold-end", type=float, default=1.04)
    parser.add_argument("--threshold-step", type=float, default=0.02)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260711)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args)
    print("wrote", args.output_dir / "quality_gate_results.jsonl")
    print("wrote", args.output_dir / "quality_gate_summary.json")
    print("wrote", args.output_dir / "quality_gate_summary.md")
    print(json.dumps(summary["test_p90_methods"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
