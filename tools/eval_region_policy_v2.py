#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


METRIC_KEYS = ["iou", "dice", "pixel_precision", "pixel_recall", "pixel_f1"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def float_grid(start: float, end: float, step: float) -> list[float]:
    values = []
    current = start
    while current <= end + 1e-9:
        values.append(round(current, 4))
        current += step
    return values


def parse_float_list(text: str) -> list[float]:
    values = [float(item.strip()) for item in text.split(",") if item.strip()]
    if not values:
        raise ValueError("float list cannot be empty")
    return values


def method_payload(record: dict[str, Any], method: str) -> dict[str, Any]:
    payload = record["methods"].get(method, {})
    if payload.get("status") != "run":
        payload = record["methods"]["bbox_mask_baseline"]
    return payload


def method_metrics(record: dict[str, Any], method: str) -> dict[str, float]:
    payload = method_payload(record, method)
    return {key: float(payload["metrics"][key]) for key in METRIC_KEYS}


def bbox_area(record: dict[str, Any]) -> int:
    bbox = record.get("gt_bbox") or record.get("bbox_xyxy")
    if not bbox:
        return 0
    x0, y0, x1, y1 = [int(v) for v in bbox]
    return max(0, x1 - x0) * max(0, y1 - y0)


def sam_score(record: dict[str, Any]) -> float | None:
    value = record["methods"].get("sam_refinement", {}).get("score")
    return float(value) if value is not None else None


def sam_area_bbox_ratio(record: dict[str, Any]) -> float | None:
    area = bbox_area(record)
    if area <= 0:
        return None
    payload = record["methods"].get("sam_refinement", {})
    metrics = payload.get("metrics") or {}
    pred_pixels = metrics.get("pred_pixels")
    if pred_pixels is None:
        return None
    return float(pred_pixels) / float(area)


def global_prediction(record: dict[str, Any], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    prediction = predictions.get(str(record["id"])) or {}
    return {
        "global_verdict": str(prediction.get("predicted_verdict") or prediction.get("pred_verdict") or "unknown").strip().lower(),
        "global_domain": normalize_domain(prediction.get("predicted_domain") or prediction.get("pred_tamper_domain")),
        "global_valid_json": bool(prediction.get("valid_json")),
        "global_valid_schema": bool(prediction.get("valid_schema")),
    }


def patch_prediction(record: dict[str, Any], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    prediction = predictions.get(str(record["id"])) or {}
    return {
        "photoshop_patch_score": float(prediction.get("photoshop_patch_score") or 0.0),
        "photoshop_votes": int(prediction.get("photoshop_votes") or 0),
        "patch_valid_views": int(prediction.get("valid_views") or 0),
        "patch_total_views": int(prediction.get("total_views") or 0),
        "invalid_patch_outputs": int(prediction.get("invalid_patch_outputs") or 0),
    }


def old_predicted_method(global_domain: str) -> str:
    if global_domain in {"photoshop", "aigc_inpaint", "aigc_editing"}:
        return "sam_refinement"
    return "bbox_mask_baseline"


def oracle_method(domain: str) -> str:
    if domain in {"photoshop", "aigc_editing"}:
        return "sam_refinement"
    return "bbox_mask_baseline"


def v2_decision(features: dict[str, Any], thresholds: dict[str, float]) -> tuple[str, str, str]:
    patch_score = float(features["photoshop_patch_score"])
    face_score = float(features["face_score"])
    global_domain = str(features["global_domain"])
    score = features["sam_score"]
    ratio = features["sam_area_bbox_ratio"]

    if patch_score >= thresholds["t_ps"]:
        return "sam_refinement", "photoshop", "photoshop_patch_score_pass"
    if face_score >= thresholds["t_face"]:
        return "bbox_mask_baseline", "deepfake", "face_score_pass"
    if global_domain in {"aigc_inpaint", "aigc_editing"}:
        if score is None:
            return "bbox_mask_baseline", "aigc_inpaint", "aigc_sam_missing_score"
        if ratio is None:
            return "bbox_mask_baseline", "aigc_inpaint", "aigc_sam_missing_area_ratio"
        if score < thresholds["t_sam_score"]:
            return "bbox_mask_baseline", "aigc_inpaint", "aigc_sam_score_below_threshold"
        if ratio < thresholds["sam_area_bbox_ratio_min"]:
            return "bbox_mask_baseline", "aigc_inpaint", "aigc_sam_area_ratio_too_small"
        if ratio > thresholds["sam_area_bbox_ratio_max"]:
            return "bbox_mask_baseline", "aigc_inpaint", "aigc_sam_area_ratio_too_large"
        return "sam_refinement", "aigc_inpaint", "aigc_sam_gate_pass"
    return "bbox_mask_baseline", global_domain, "fallback_bbox"


def row_for_method(record: dict[str, Any], method_name: str, method: str, features: dict[str, Any], reason: str | None = None, routed_domain: str | None = None) -> dict[str, Any]:
    metrics = method_metrics(record, method)
    return {
        "id": record["id"],
        "domain": record["domain"],
        "source": record.get("source") or record.get("source_dataset"),
        "method": method_name,
        "selected_method": method,
        "routed_domain": routed_domain,
        "route_reason": reason,
        **features,
        **metrics,
    }


def features_for_record(
    record: dict[str, Any],
    global_predictions: dict[str, dict[str, Any]],
    patch_predictions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    global_payload = global_prediction(record, global_predictions)
    patch_payload = patch_prediction(record, patch_predictions)
    global_domain = global_payload["global_domain"]
    return {
        **global_payload,
        **patch_payload,
        "face_score": 1.0 if global_domain == "deepfake" else 0.0,
        "sam_score": sam_score(record),
        "sam_area_bbox_ratio": sam_area_bbox_ratio(record),
    }


def evaluate_records(
    records: list[dict[str, Any]],
    global_predictions: dict[str, dict[str, Any]],
    patch_predictions: dict[str, dict[str, Any]],
    thresholds: dict[str, float],
) -> dict[str, list[dict[str, Any]]]:
    rows_by_method: dict[str, list[dict[str, Any]]] = {
        "bbox_mask_baseline": [],
        "sam_best_of3": [],
        "old_domain_aware_predicted": [],
        "oracle_domain_aware": [],
        "policy_v2": [],
    }
    for record in records:
        features = features_for_record(record, global_predictions, patch_predictions)
        rows_by_method["bbox_mask_baseline"].append(row_for_method(record, "bbox_mask_baseline", "bbox_mask_baseline", features))
        rows_by_method["sam_best_of3"].append(row_for_method(record, "sam_best_of3", "sam_refinement", features))
        old_method = old_predicted_method(str(features["global_domain"]))
        rows_by_method["old_domain_aware_predicted"].append(
            row_for_method(record, "old_domain_aware_predicted", old_method, features, "old_global_domain_policy", str(features["global_domain"]))
        )
        oracle = oracle_method(str(record["domain"]))
        rows_by_method["oracle_domain_aware"].append(
            row_for_method(record, "oracle_domain_aware", oracle, features, "oracle_domain_policy", str(record["domain"]))
        )
        v2_method, routed_domain, reason = v2_decision(features, thresholds)
        rows_by_method["policy_v2"].append(row_for_method(record, "policy_v2", v2_method, features, reason, routed_domain))
    return rows_by_method


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_domain[str(row["domain"])].append(row)

    def group_summary(group: list[dict[str, Any]]) -> dict[str, Any]:
        payload = {"n": len(group)}
        for key in METRIC_KEYS:
            payload[key] = mean([float(row[key]) for row in group])
        payload["selected_method_counts"] = dict(sorted(Counter(str(row["selected_method"]) for row in group).items()))
        payload["route_reason_counts"] = dict(sorted(Counter(str(row.get("route_reason")) for row in group if row.get("route_reason")).items()))
        payload["routed_domain_counts"] = dict(sorted(Counter(str(row.get("routed_domain")) for row in group if row.get("routed_domain")).items()))
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
        if ci:
            summary["overall"][f"{key}_ci95"] = ci
    by_domain_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_domain_rows[str(row["domain"])].append(row)
    for domain, group in by_domain_rows.items():
        for key in METRIC_KEYS:
            ci = bootstrap_ci(group, key, samples, seed + len(domain + key) * 3571)
            if ci:
                summary["by_domain"][domain][f"{key}_ci95"] = ci


def score_threshold(rows: list[dict[str, Any]]) -> tuple[float, float, float, int]:
    overall_iou = mean([float(row["iou"]) for row in rows])
    overall_f1 = mean([float(row["pixel_f1"]) for row in rows])
    photoshop_rows = [row for row in rows if row["domain"] == "photoshop"]
    photoshop_iou = mean([float(row["iou"]) for row in photoshop_rows])
    false_photoshop_routes = sum(1 for row in rows if row["domain"] != "photoshop" and row.get("routed_domain") == "photoshop")
    return overall_iou, overall_f1, photoshop_iou, -false_photoshop_routes


def tune_thresholds(
    records: list[dict[str, Any]],
    global_predictions: dict[str, dict[str, Any]],
    patch_predictions: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    t_ps_values = parse_float_list(args.t_ps_values)
    t_face_values = parse_float_list(args.t_face_values)
    t_sam_values = float_grid(args.t_sam_start, args.t_sam_end, args.t_sam_step)
    ratio_min_values = float_grid(args.ratio_min_start, args.ratio_min_end, args.ratio_min_step)
    ratio_max_values = float_grid(args.ratio_max_start, args.ratio_max_end, args.ratio_max_step)

    best: dict[str, Any] | None = None
    search_rows = []
    for t_ps in t_ps_values:
        for t_face in t_face_values:
            for t_sam in t_sam_values:
                for ratio_min in ratio_min_values:
                    for ratio_max in ratio_max_values:
                        if ratio_max < ratio_min:
                            continue
                        thresholds = {
                            "t_ps": t_ps,
                            "t_face": t_face,
                            "t_sam_score": t_sam,
                            "sam_area_bbox_ratio_min": ratio_min,
                            "sam_area_bbox_ratio_max": ratio_max,
                        }
                        rows = evaluate_records(records, global_predictions, patch_predictions, thresholds)["policy_v2"]
                        key = score_threshold(rows)
                        item = {
                            "thresholds": thresholds,
                            "overall_iou": key[0],
                            "overall_f1": key[1],
                            "photoshop_iou": key[2],
                            "negative_false_photoshop_routes": key[3],
                        }
                        search_rows.append(item)
                        if best is None or key > best["score_key"]:
                            best = {**item, "score_key": key}
    if best is None:
        raise RuntimeError("threshold search produced no candidates")
    return {
        "locked_thresholds": best["thresholds"],
        "best_dev": {k: v for k, v in best.items() if k != "score_key"},
        "searched_candidates": len(search_rows),
        "top_candidates": sorted(search_rows, key=lambda item: (item["overall_iou"], item["overall_f1"], item["photoshop_iou"], item["negative_false_photoshop_routes"]), reverse=True)[:20],
    }


def prediction_stats(records: list[dict[str, Any]], global_predictions: dict[str, dict[str, Any]], patch_predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    domain_hits = 0
    global_counts: Counter[str] = Counter()
    patch_scores: dict[str, list[float]] = defaultdict(list)
    patch_route_hits: dict[str, int] = defaultdict(int)
    for record in records:
        features = features_for_record(record, global_predictions, patch_predictions)
        global_domain = str(features["global_domain"])
        global_counts[global_domain] += 1
        domain_hits += int(domain_matches(global_domain, str(record["domain"])))
        patch_scores[str(record["domain"])].append(float(features["photoshop_patch_score"]))
        patch_route_hits[str(record["domain"])] += int(float(features["photoshop_patch_score"]) > 0)
    return {
        "n": len(records),
        "global_domain_accuracy": domain_hits / len(records) if records else None,
        "global_domain_counts": dict(sorted(global_counts.items())),
        "mean_photoshop_patch_score_by_domain": {domain: mean(values) for domain, values in sorted(patch_scores.items())},
        "nonzero_patch_score_counts_by_domain": dict(sorted(patch_route_hits.items())),
    }


def gains(summary: dict[str, Any]) -> dict[str, float]:
    bbox = summary["bbox_mask_baseline"]["overall"]
    v2 = summary["policy_v2"]["overall"]
    return {
        "iou_abs_gain_vs_bbox": float(v2["iou"]) - float(bbox["iou"]),
        "pixel_f1_abs_gain_vs_bbox": float(v2["pixel_f1"]) - float(bbox["pixel_f1"]),
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
        f"# {summary['name']} Region Policy v2",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "## Thresholds",
        "",
        f"- thresholds: `{summary['locked_thresholds']}`",
        f"- threshold source: `{summary['threshold_source']}`",
        "",
        "## Evaluation",
        "",
        "| method | n | IoU | F1 | Precision | Recall | selected |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for method, payload in summary["eval_methods"].items():
        overall = payload["overall"]
        lines.append(
            f"| {method} | {overall['n']} | {fmt_ci(overall, 'iou')} | {fmt_ci(overall, 'pixel_f1')} | "
            f"{fmt_ci(overall, 'pixel_precision')} | {fmt_ci(overall, 'pixel_recall')} | "
            f"`{overall['selected_method_counts']}` |"
        )
    lines.extend(["", "## By Domain", "", "| domain | method | n | IoU | F1 | selected |", "|---|---|---:|---:|---:|---|"])
    domains = sorted({domain for payload in summary["eval_methods"].values() for domain in payload["by_domain"]})
    for domain in domains:
        for method, payload in summary["eval_methods"].items():
            group = payload["by_domain"].get(domain)
            if not group:
                continue
            lines.append(
                f"| {domain} | {method} | {group['n']} | {fmt_ci(group, 'iou')} | {fmt_ci(group, 'pixel_f1')} | "
                f"`{group['selected_method_counts']}` |"
            )
    lines.extend(
        [
            "",
            "## Gains",
            "",
            f"- policy_v2 IoU gain vs bbox: `{summary['eval_gains']['iou_abs_gain_vs_bbox']:.4f}`",
            f"- policy_v2 F1 gain vs bbox: `{summary['eval_gains']['pixel_f1_abs_gain_vs_bbox']:.4f}`",
            "",
            "## Prediction Stats",
            "",
            f"- global domain accuracy: `{fmt(summary['eval_prediction_stats']['global_domain_accuracy'])}`",
            f"- global domain counts: `{summary['eval_prediction_stats']['global_domain_counts']}`",
            f"- mean patch score by domain: `{summary['eval_prediction_stats']['mean_photoshop_patch_score_by_domain']}`",
            f"- nonzero patch scores by domain: `{summary['eval_prediction_stats']['nonzero_patch_score_counts_by_domain']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Any]:
    dev_records = load_jsonl(args.dev_results)
    eval_records = load_jsonl(args.eval_results)
    dev_global = {str(row["id"]): row for row in load_jsonl(args.dev_global_predictions)}
    eval_global = {str(row["id"]): row for row in load_jsonl(args.eval_global_predictions)}
    dev_patch = {str(row["id"]): row for row in load_jsonl(args.dev_patch_predictions)}
    eval_patch = {str(row["id"]): row for row in load_jsonl(args.eval_patch_predictions)}

    dev_ids = {str(row["id"]) for row in dev_records}
    eval_ids = {str(row["id"]) for row in eval_records}
    missing_dev_global = sorted(dev_ids - set(dev_global))
    missing_dev_patch = sorted(dev_ids - set(dev_patch))
    missing_eval_global = sorted(eval_ids - set(eval_global))
    missing_eval_patch = sorted(eval_ids - set(eval_patch))
    if missing_dev_global or missing_dev_patch:
        raise RuntimeError(
            "missing dev predictions: "
            f"global={len(missing_dev_global)} first={missing_dev_global[:5]}, "
            f"patch={len(missing_dev_patch)} first={missing_dev_patch[:5]}"
        )
    if missing_eval_global or missing_eval_patch:
        raise RuntimeError(
            "missing eval predictions: "
            f"global={len(missing_eval_global)} first={missing_eval_global[:5]}, "
            f"patch={len(missing_eval_patch)} first={missing_eval_patch[:5]}"
        )

    threshold_source = "loaded"
    threshold_search = None
    if args.locked_thresholds and args.locked_thresholds.exists():
        thresholds = load_json(args.locked_thresholds)["locked_thresholds"]
    else:
        threshold_source = "tuned_on_dev"
        threshold_search = tune_thresholds(dev_records, dev_global, dev_patch, args)
        thresholds = threshold_search["locked_thresholds"]

    dev_rows_by_method = evaluate_records(dev_records, dev_global, dev_patch, thresholds)
    eval_rows_by_method = evaluate_records(eval_records, eval_global, eval_patch, thresholds)
    dev_summary = {method: summarize(rows) for method, rows in dev_rows_by_method.items()}
    eval_summary = {method: summarize(rows) for method, rows in eval_rows_by_method.items()}
    for idx, method in enumerate(eval_summary):
        add_ci(eval_summary[method], eval_rows_by_method[method], args.bootstrap_samples, args.bootstrap_seed + idx * 1009)

    all_rows = []
    for split_name, method_rows in [("dev", dev_rows_by_method), ("eval", eval_rows_by_method)]:
        for method, rows in method_rows.items():
            for row in rows:
                all_rows.append({"split": split_name, **row})

    summary = {
        "name": args.output_dir.name,
        "boundary": "GT bbox prompt conditioned mask refinement; not automatic forged-region discovery.",
        "dev_results": str(args.dev_results),
        "eval_results": str(args.eval_results),
        "dev_global_predictions": str(args.dev_global_predictions),
        "eval_global_predictions": str(args.eval_global_predictions),
        "dev_patch_predictions": str(args.dev_patch_predictions),
        "eval_patch_predictions": str(args.eval_patch_predictions),
        "threshold_source": threshold_source,
        "threshold_search": threshold_search,
        "locked_thresholds": thresholds,
        "dev_methods": dev_summary,
        "eval_methods": eval_summary,
        "eval_prediction_stats": prediction_stats(eval_records, eval_global, eval_patch),
        "eval_gains": gains(eval_summary),
        "bootstrap_samples": args.bootstrap_samples,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "policy_v2_results.jsonl"
    summary_json = args.output_dir / "policy_v2_summary.json"
    summary_md = args.output_dir / "policy_v2_summary.md"
    thresholds_json = args.output_dir / "policy_v2_thresholds.json"
    results_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in all_rows), encoding="utf-8")
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_md.write_text(render_md(summary), encoding="utf-8")
    thresholds_json.write_text(
        json.dumps(
            {
                "locked_thresholds": thresholds,
                "threshold_source": threshold_source,
                "dev_results": str(args.dev_results),
                "threshold_search": threshold_search,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune and evaluate region routing policy v2 with Photoshop patch expert.")
    parser.add_argument("--dev-results", type=Path, default=Path("artifacts/region_eval/region_eval_p150/results.jsonl"))
    parser.add_argument("--eval-results", type=Path, default=Path("artifacts/region_eval/region_eval_p150/results.jsonl"))
    parser.add_argument("--dev-global-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p150/domain_predictions_domain_boost_compact.jsonl"))
    parser.add_argument("--eval-global-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p150/domain_predictions_domain_boost_compact.jsonl"))
    parser.add_argument("--dev-patch-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p150/photoshop_patch_predictions.jsonl"))
    parser.add_argument("--eval-patch-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p150/photoshop_patch_predictions.jsonl"))
    parser.add_argument("--locked-thresholds", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/region_eval/region_eval_p150_policy_v2_dev"))
    parser.add_argument("--t-ps-values", default="0.34,0.67,1.00")
    parser.add_argument("--t-face-values", default="1.00")
    parser.add_argument("--t-sam-start", type=float, default=0.50)
    parser.add_argument("--t-sam-end", type=float, default=1.04)
    parser.add_argument("--t-sam-step", type=float, default=0.02)
    parser.add_argument("--ratio-min-start", type=float, default=0.05)
    parser.add_argument("--ratio-min-end", type=float, default=0.50)
    parser.add_argument("--ratio-min-step", type=float, default=0.05)
    parser.add_argument("--ratio-max-start", type=float, default=0.80)
    parser.add_argument("--ratio-max-end", type=float, default=1.50)
    parser.add_argument("--ratio-max-step", type=float, default=0.10)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260715)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args)
    print("wrote", args.output_dir / "policy_v2_results.jsonl")
    print("wrote", args.output_dir / "policy_v2_summary.json")
    print("wrote", args.output_dir / "policy_v2_summary.md")
    print("wrote", args.output_dir / "policy_v2_thresholds.json")
    print(json.dumps(summary["eval_methods"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
