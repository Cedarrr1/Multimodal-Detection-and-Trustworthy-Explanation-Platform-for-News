#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


METRIC_KEYS = ["iou", "dice", "pixel_precision", "pixel_recall", "pixel_f1"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def predicted_strategy(predicted_domain: str) -> str:
    if predicted_domain in {"photoshop", "aigc_inpaint", "aigc_editing"}:
        return "sam_refinement"
    return "bbox_mask_baseline"


def pct(correct: int, total: int) -> dict[str, Any]:
    return {
        "correct": correct,
        "total": total,
        "value": correct / total if total else None,
    }


def fmt_metric(metric: dict[str, Any]) -> str:
    value = metric.get("value")
    if value is None:
        return "n/a"
    return f"{value:.4f} ({metric.get('correct')}/{metric.get('total')})"


def fmt_float(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.4f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_metric_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n": 0}
    return {
        "n": len(rows),
        **{key: mean([float(row[key]) for row in rows]) for key in METRIC_KEYS},
    }


def method_metrics_from_summary(region_summary: dict[str, Any], method: str) -> dict[str, Any]:
    payload = region_summary["methods"][method]
    return {
        "overall": payload["overall"],
        "by_domain": payload["by_domain"],
    }


def gtmask_metrics(gtmask_summary: dict[str, Any], method: str) -> dict[str, Any]:
    payload = gtmask_summary["methods"][method]
    return {
        "overall": payload["overall"],
        "by_domain": payload["by_domain"],
    }


def collect_predicted_bestof3_metrics(
    records: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    gtmask_rows: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    metric_rows: list[dict[str, Any]] = []
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for record in records:
        sample_id = str(record["id"])
        prediction = predictions.get(sample_id)
        predicted_domain = normalize_domain(prediction.get("predicted_domain") if prediction else None)
        source_method = predicted_strategy(predicted_domain)
        if source_method == "sam_refinement":
            source = gtmask_rows[(sample_id, "sam_from_gtbbox")]
            metrics = {key: float(source[key]) for key in METRIC_KEYS}
        else:
            source = gtmask_rows[(sample_id, "bbox_from_gtmask")]
            metrics = {key: float(source[key]) for key in METRIC_KEYS}

        row = {
            "id": sample_id,
            "domain": record["domain"],
            "source_method": "sam_from_gtbbox" if source_method == "sam_refinement" else "bbox_from_gtmask",
            **metrics,
        }
        metric_rows.append(row)
        by_domain[str(record["domain"])].append(row)

    return {
        "overall": summarize_metric_rows(metric_rows),
        "by_domain": {domain: summarize_metric_rows(rows) for domain, rows in sorted(by_domain.items())},
    }


def summarize_predictions(
    records: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    total = len(records)
    found = 0
    valid_json = 0
    valid_schema = 0
    tampered_hits = 0
    domain_hits = 0
    predicted_domains: Counter[str] = Counter()
    selected_methods: Counter[str] = Counter()
    by_domain: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for record in records:
        domain = str(record["domain"])
        prediction = predictions.get(str(record["id"]))
        if prediction is not None:
            found += 1
            valid_json += int(bool(prediction.get("valid_json")))
            valid_schema += int(bool(prediction.get("valid_schema")))
        predicted_verdict = str((prediction or {}).get("predicted_verdict", "unknown")).strip().lower()
        predicted_domain = normalize_domain((prediction or {}).get("predicted_domain"))
        strategy = predicted_strategy(predicted_domain)

        predicted_domains[predicted_domain] += 1
        selected_methods[strategy] += 1
        tampered_hit = predicted_verdict == "tampered"
        domain_hit = domain_matches(predicted_domain, domain)
        tampered_hits += int(tampered_hit)
        domain_hits += int(domain_hit)

        by_domain[domain]["n"] += 1
        by_domain[domain]["found"] += int(prediction is not None)
        by_domain[domain]["valid_json"] += int(bool((prediction or {}).get("valid_json")))
        by_domain[domain]["valid_schema"] += int(bool((prediction or {}).get("valid_schema")))
        by_domain[domain]["tampered_hits"] += int(tampered_hit)
        by_domain[domain]["domain_hits"] += int(domain_hit)
        by_domain[domain][f"select_{strategy}"] += 1

    return {
        "total": total,
        "found": found,
        "valid_json": pct(valid_json, total),
        "valid_schema": pct(valid_schema, total),
        "tampered_recall": pct(tampered_hits, total),
        "domain_accuracy": pct(domain_hits, total),
        "predicted_domain_counts": dict(sorted(predicted_domains.items())),
        "selected_method_counts": dict(sorted(selected_methods.items())),
        "by_domain": {
            domain: {
                "n": counts["n"],
                "found": counts["found"],
                "valid_json": pct(counts["valid_json"], counts["n"]),
                "valid_schema": pct(counts["valid_schema"], counts["n"]),
                "tampered_recall": pct(counts["tampered_hits"], counts["n"]),
                "domain_accuracy": pct(counts["domain_hits"], counts["n"]),
                "selected_method_counts": {
                    "bbox_mask_baseline": counts["select_bbox_mask_baseline"],
                    "sam_refinement": counts["select_sam_refinement"],
                },
            }
            for domain, counts in sorted(by_domain.items())
        },
    }


def render_method_table(methods: dict[str, Any]) -> list[str]:
    lines = [
        "| method | n | IoU | Dice/F1 | Precision | Recall |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, payload in methods.items():
        metrics = payload["overall"]
        lines.append(
            f"| {name} | {metrics.get('n', 0)} | {fmt_float(metrics.get('iou'))} | "
            f"{fmt_float(metrics.get('pixel_f1'))} | {fmt_float(metrics.get('pixel_precision'))} | "
            f"{fmt_float(metrics.get('pixel_recall'))} |"
        )
    return lines


def render_domain_table(methods: dict[str, Any]) -> list[str]:
    lines = [
        "| domain | method | n | IoU | Dice/F1 |",
        "|---|---|---:|---:|---:|",
    ]
    domains = sorted({domain for payload in methods.values() for domain in payload["by_domain"]})
    for domain in domains:
        for name, payload in methods.items():
            metrics = payload["by_domain"].get(domain, {"n": 0})
            lines.append(
                f"| {domain} | {name} | {metrics.get('n', 0)} | "
                f"{fmt_float(metrics.get('iou'))} | {fmt_float(metrics.get('pixel_f1'))} |"
            )
    return lines


def render_md(summary: dict[str, Any]) -> str:
    pred = summary["image_level_predictions"]
    lines = [
        f"# {summary['name']} Chain Evaluation",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "This experiment uses GT masks only to derive bbox prompts. It evaluates bbox-prompt mask refinement / grounding, not automatic forged-region discovery.",
        "",
        "## Image-Level LoRA Predictions",
        "",
        f"- samples: `{pred['total']}`",
        f"- predictions found: `{pred['found']}/{pred['total']}`",
        f"- valid JSON: `{fmt_metric(pred['valid_json'])}`",
        f"- valid schema: `{fmt_metric(pred['valid_schema'])}`",
        f"- tampered recall: `{fmt_metric(pred['tampered_recall'])}`",
        f"- domain accuracy: `{fmt_metric(pred['domain_accuracy'])}`",
        f"- selected bbox fallback: `{pred['selected_method_counts'].get('bbox_mask_baseline', 0)}/{pred['total']}`",
        f"- selected SAM refinement: `{pred['selected_method_counts'].get('sam_refinement', 0)}/{pred['total']}`",
        "",
        "## Mask Refinement",
        "",
        "Primary chain metrics below use the existing p150 region-eval SAM setting. The GT-mask-to-SAM closure is reported separately because it uses SAM multimask best-of-3.",
        "",
        *render_method_table(summary["mask_refinement_methods"]),
        "",
        "## Per Domain Mask Metrics",
        "",
        *render_domain_table(summary["mask_refinement_methods"]),
        "",
        "## GT Mask to SAM Closure",
        "",
        f"- output dir: `{summary['gtmask_to_sam']['output_dir']}`",
        f"- bbox matches manifest: `{summary['gtmask_to_sam']['bbox_matches_manifest']}/{summary['gtmask_to_sam']['n_samples']}`",
        f"- SAM status: `{summary['gtmask_to_sam']['sam_status']}`",
        f"- SAM setting: `{summary['gtmask_to_sam']['sam_setting']}`",
        "",
        *render_method_table(summary["gtmask_to_sam"]["methods"]),
        "",
        "## Strategy",
        "",
        "Oracle policy: Photoshop and AIGC-editing use SAM; DeepFake uses bbox / face-region fallback.",
        "",
        "Predicted policy: use the LoRA-predicted tamper domain; Photoshop/AIGC predictions use SAM, DeepFake/none/unknown fallback to bbox.",
    ]
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Any]:
    records = load_jsonl(args.region_results)
    manifest_rows = load_jsonl(args.manifest)
    predictions = {str(row["id"]): row for row in load_jsonl(args.domain_predictions)}
    region_summary = load_json(args.region_summary)
    gtmask_summary = load_json(args.gtmask_summary)
    gtmask_rows = {
        (str(row["id"]), str(row["method"])): row
        for row in load_jsonl(args.gtmask_results)
        if row.get("status") == "run"
    }

    missing_predictions = sorted({str(row["id"]) for row in records} - set(predictions))
    if missing_predictions:
        raise ValueError(f"missing domain predictions for {len(missing_predictions)} samples")

    methods = {
        "bbox_mask_baseline": method_metrics_from_summary(region_summary, "bbox_mask_baseline"),
        "sam_refinement": method_metrics_from_summary(region_summary, "sam_refinement"),
        "domain_aware_oracle": method_metrics_from_summary(region_summary, "domain_aware_oracle"),
        "domain_aware_predicted": method_metrics_from_summary(region_summary, "domain_aware_predicted"),
    }
    gtmask_methods = {
        "bbox_from_gtmask": gtmask_metrics(gtmask_summary, "bbox_from_gtmask"),
        "sam_from_gtbbox": gtmask_metrics(gtmask_summary, "sam_from_gtbbox"),
        "domain_aware_predicted_bestof3": collect_predicted_bestof3_metrics(records, predictions, gtmask_rows),
    }
    summary = {
        "name": args.name,
        "boundary": (
            "image -> LoRA tampered/domain prediction -> GT mask-derived bbox prompt -> "
            "bbox or SAM mask refinement -> GT mask metrics; bbox prompts come from GT masks, "
            "so this is not automatic forged-region discovery"
        ),
        "manifest": str(args.manifest),
        "region_results": str(args.region_results),
        "region_summary": str(args.region_summary),
        "domain_predictions": str(args.domain_predictions),
        "n_manifest": len(manifest_rows),
        "n_results": len(records),
        "image_level_predictions": summarize_predictions(records, predictions),
        "mask_refinement_methods": methods,
        "gtmask_to_sam": {
            "output_dir": str(args.gtmask_summary.parent),
            "summary": str(args.gtmask_summary),
            "results": str(args.gtmask_results),
            "n_samples": gtmask_summary["n_samples"],
            "bbox_matches_manifest": gtmask_summary["bbox_matches_manifest"],
            "sam_status": gtmask_summary["sam_status"],
            "sam_setting": "segment-anything multimask_output=True, select highest predicted-IoU score",
            "methods": gtmask_methods,
        },
        "policies": {
            "domain_aware_oracle": {
                "photoshop": "sam_refinement",
                "aigc_editing": "sam_refinement",
                "deepfake": "bbox_mask_baseline",
            },
            "domain_aware_predicted": {
                "photoshop": "sam_refinement",
                "aigc_editing": "sam_refinement",
                "aigc_inpaint": "sam_refinement",
                "deepfake": "bbox_mask_baseline",
                "none": "bbox_mask_baseline",
                "unknown": "bbox_mask_baseline",
            },
        },
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_md(summary), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize image-level LoRA domain prediction and region-level mask-refinement chain metrics.")
    parser.add_argument("--name", default="region_eval_p150")
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/region_eval/region_eval_p150/manifest.jsonl"))
    parser.add_argument("--region-results", type=Path, default=Path("artifacts/region_eval/region_eval_p150/results.jsonl"))
    parser.add_argument("--region-summary", type=Path, default=Path("artifacts/region_eval/region_eval_p150/summary.json"))
    parser.add_argument("--domain-predictions", type=Path, default=Path("artifacts/region_eval/region_eval_p150/domain_predictions.jsonl"))
    parser.add_argument("--gtmask-results", type=Path, default=Path("artifacts/region_eval/region_eval_p150_gtmask_to_sam/gtmask_to_sam_results.jsonl"))
    parser.add_argument("--gtmask-summary", type=Path, default=Path("artifacts/region_eval/region_eval_p150_gtmask_to_sam/gtmask_to_sam_summary.json"))
    parser.add_argument("--output-json", type=Path, default=Path("artifacts/region_eval/region_eval_p150/chain_summary.json"))
    parser.add_argument("--output-md", type=Path, default=Path("artifacts/region_eval/region_eval_p150/chain_summary.md"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run(args)
    print("wrote_chain_summary_json", args.output_json)
    print("wrote_chain_summary_md", args.output_md)
    pred = summary["image_level_predictions"]
    print("tampered_recall", fmt_metric(pred["tampered_recall"]))
    print("domain_accuracy", fmt_metric(pred["domain_accuracy"]))


if __name__ == "__main__":
    main()
