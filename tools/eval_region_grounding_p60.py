#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image


BOUNDARY_TEXT = (
    "bbox-prompt conditioned mask refinement / grounding evaluation; "
    "not automatic forged-region discovery"
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_rgb_image(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGB"))


def read_binary_mask(path: Path, target_size: tuple[int, int]) -> np.ndarray:
    with Image.open(path) as image:
        mask = image.convert("L")
        if mask.size != target_size:
            mask = mask.resize(target_size, Image.Resampling.NEAREST)
        arr = np.asarray(mask)
    return arr > 0


def bbox_from_mask(mask: np.ndarray) -> list[int]:
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        raise ValueError("GT mask is empty")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def bbox_mask(shape: tuple[int, int], bbox_xyxy: list[int]) -> np.ndarray:
    height, width = shape
    x0, y0, x1, y1 = bbox_xyxy
    x0 = max(0, min(width, int(x0)))
    x1 = max(0, min(width, int(x1)))
    y0 = max(0, min(height, int(y0)))
    y1 = max(0, min(height, int(y1)))
    pred = np.zeros((height, width), dtype=bool)
    pred[y0:y1, x0:x1] = True
    return pred


def mask_metrics(pred: np.ndarray, gt: np.ndarray) -> dict[str, float | int]:
    pred = pred.astype(bool)
    gt = gt.astype(bool)
    tp = int(np.logical_and(pred, gt).sum())
    fp = int(np.logical_and(pred, np.logical_not(gt)).sum())
    fn = int(np.logical_and(np.logical_not(pred), gt).sum())
    pred_pixels = tp + fp
    gt_pixels = tp + fn
    union = tp + fp + fn
    precision = tp / pred_pixels if pred_pixels else 0.0
    recall = tp / gt_pixels if gt_pixels else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    dice = (2 * tp / (pred_pixels + gt_pixels)) if (pred_pixels + gt_pixels) else 0.0
    iou = tp / union if union else 0.0
    return {
        "iou": iou,
        "dice": dice,
        "pixel_precision": precision,
        "pixel_recall": recall,
        "pixel_f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "pred_pixels": pred_pixels,
        "gt_pixels": gt_pixels,
    }


class SegmentAnythingRunner:
    def __init__(self, checkpoint: Path, model_type: str, device: str, multimask: bool) -> None:
        from segment_anything import SamPredictor, sam_model_registry

        sam = sam_model_registry[model_type](checkpoint=str(checkpoint))
        sam.to(device=device)
        sam.eval()
        self.predictor = SamPredictor(sam)
        self.multimask = multimask

    def predict(self, image_rgb: np.ndarray, bbox_xyxy: list[int]) -> tuple[np.ndarray, float | None]:
        self.predictor.set_image(image_rgb)
        box = np.asarray(bbox_xyxy, dtype=np.float32)
        masks, scores, _ = self.predictor.predict(box=box, multimask_output=self.multimask)
        if len(masks) == 0:
            return np.zeros(image_rgb.shape[:2], dtype=bool), None
        idx = int(np.argmax(scores)) if scores is not None and len(scores) else 0
        score = float(scores[idx]) if scores is not None and len(scores) else None
        return masks[idx].astype(bool), score


class NativeSamRunner:
    def __init__(self, checkpoint: Path, model_type: str, device: str, multimask: bool) -> None:
        from MFLM.model.SAM import sam_model_registry
        from MFLM.model.SAM.utils.transforms import ResizeLongestSide

        sam = sam_model_registry[model_type](checkpoint=str(checkpoint))
        sam.to(device=device)
        sam.eval()
        self.sam = sam
        self.device = device
        self.multimask = multimask
        self.transform = ResizeLongestSide(sam.image_encoder.img_size)

    @torch.inference_mode()
    def predict(self, image_rgb: np.ndarray, bbox_xyxy: list[int]) -> tuple[np.ndarray, float | None]:
        original_size = image_rgb.shape[:2]
        resized = self.transform.apply_image(image_rgb)
        image_tensor = torch.as_tensor(resized, device=self.device).permute(2, 0, 1).contiguous()
        box = self.transform.apply_boxes(np.asarray([bbox_xyxy], dtype=np.float32), original_size)
        box_tensor = torch.as_tensor(box, dtype=torch.float, device=self.device)
        outputs = self.sam(
            [{"image": image_tensor, "boxes": box_tensor, "original_size": original_size}],
            multimask_output=self.multimask,
        )
        masks = outputs[0]["masks"][0]
        scores = outputs[0]["iou_predictions"][0]
        idx = int(torch.argmax(scores).item()) if scores.numel() else 0
        score = float(scores[idx].detach().cpu().item()) if scores.numel() else None
        return masks[idx].detach().cpu().numpy().astype(bool), score


def build_sam_runner(args: argparse.Namespace) -> tuple[Any | None, str, str | None]:
    if args.skip_sam:
        return None, "skipped", "--skip-sam was set"
    if args.sam_checkpoint is None:
        return None, "not_run", "--sam-checkpoint was not provided"
    if not args.sam_checkpoint.exists():
        return None, "not_run", f"SAM checkpoint not found: {args.sam_checkpoint}"

    errors: list[str] = []
    if args.sam_impl in {"auto", "segment_anything"}:
        try:
            return SegmentAnythingRunner(args.sam_checkpoint, args.sam_model_type, args.device, args.multimask), "run", None
        except Exception as exc:
            errors.append(f"segment_anything: {type(exc).__name__}: {exc}")
            if args.sam_impl == "segment_anything":
                return None, "failed", errors[-1]

    if args.sam_impl in {"auto", "native"}:
        try:
            return NativeSamRunner(args.sam_checkpoint, args.sam_model_type, args.device, args.multimask), "run", None
        except Exception as exc:
            errors.append(f"native: {type(exc).__name__}: {exc}")
            if args.sam_impl == "native":
                return None, "failed", errors[-1]

    return None, "failed", " | ".join(errors) if errors else f"unsupported --sam-impl {args.sam_impl}"


def limit_rows(rows: list[dict[str, Any]], limit_per_domain: int | None) -> list[dict[str, Any]]:
    if limit_per_domain is None:
        return rows
    counts: dict[str, int] = defaultdict(int)
    limited: list[dict[str, Any]] = []
    for row in rows:
        domain = str(row["domain"])
        if counts[domain] >= limit_per_domain:
            continue
        counts[domain] += 1
        limited.append(row)
    return limited


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize(records: list[dict[str, Any]], method: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    metric_records = [r for r in records if r["methods"].get(method, {}).get("status") == "run"]
    for record in metric_records:
        groups[str(record["domain"])].append(record)

    def group_summary(group: list[dict[str, Any]]) -> dict[str, Any]:
        metrics = [r["methods"][method]["metrics"] for r in group]
        return {
            "n": len(group),
            "iou": mean([float(m["iou"]) for m in metrics]),
            "dice": mean([float(m["dice"]) for m in metrics]),
            "pixel_precision": mean([float(m["pixel_precision"]) for m in metrics]),
            "pixel_recall": mean([float(m["pixel_recall"]) for m in metrics]),
            "pixel_f1": mean([float(m["pixel_f1"]) for m in metrics]),
        }

    return {
        "status": "run" if metric_records else "not_run",
        "overall": group_summary(metric_records),
        "by_domain": {domain: group_summary(group) for domain, group in sorted(groups.items())},
    }


def domain_aware_oracle_source_method(domain: str) -> str:
    if domain in {"photoshop", "aigc_editing"}:
        return "sam_refinement"
    if domain == "deepfake":
        return "bbox_mask_baseline"
    return "bbox_mask_baseline"


def normalize_predicted_domain(value: Any) -> str:
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


def domain_aware_predicted_source_method(predicted_domain: str) -> str:
    if predicted_domain in {"photoshop", "aigc_inpaint", "aigc_editing"}:
        return "sam_refinement"
    return "bbox_mask_baseline"


def source_method_payload(record: dict[str, Any], source_method: str) -> tuple[str, dict[str, Any]]:
    source = record["methods"].get(source_method, {})
    if source.get("status") != "run":
        source_method = "bbox_mask_baseline"
        source = record["methods"][source_method]
    return source_method, source


def load_domain_predictions(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    return {str(row["id"]): row for row in load_jsonl(path)}


def add_domain_aware_methods(records: list[dict[str, Any]], domain_predictions: dict[str, dict[str, Any]]) -> None:
    for record in records:
        oracle_method, oracle_source = source_method_payload(record, domain_aware_oracle_source_method(str(record["domain"])))
        record["methods"]["domain_aware_oracle"] = {
            "status": oracle_source["status"],
            "source_method": oracle_method,
            "metrics": oracle_source["metrics"],
        }
        record["methods"]["domain_aware_refinement"] = {
            "status": oracle_source["status"],
            "source_method": oracle_method,
            "metrics": oracle_source["metrics"],
            "alias_of": "domain_aware_oracle",
        }

        prediction = domain_predictions.get(str(record["id"]))
        predicted_domain = normalize_predicted_domain(prediction.get("predicted_domain") if prediction else None)
        predicted_method, predicted_source = source_method_payload(record, domain_aware_predicted_source_method(predicted_domain))
        record["domain_prediction"] = prediction
        record["methods"]["domain_aware_predicted"] = {
            "status": predicted_source["status"],
            "source_method": predicted_method,
            "predicted_domain": predicted_domain,
            "prediction_found": prediction is not None,
            "metrics": predicted_source["metrics"],
        }


def fmt(value: float) -> str:
    return f"{value:.4f}"


def fmt_optional_metric(metrics: dict[str, Any], key: str) -> str:
    if key not in metrics:
        return "n/a"
    return fmt(float(metrics[key]))


def write_summary_md(path: Path, summary: dict[str, Any], records: list[dict[str, Any]]) -> None:
    lines = [
        f"# {summary['name']} Mask Refinement / Grounding Evaluation",
        "",
        f"Boundary: **{BOUNDARY_TEXT}**.",
        "",
        "Each bbox prompt is computed from the GT mask. These numbers therefore evaluate mask refinement under a provided bbox prompt, not automatic forged-region discovery.",
        "",
        "## Overall",
        "",
        "| method | status | n | IoU | Dice | pixel Precision | pixel Recall | pixel F1 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method, row in summary["methods"].items():
        overall = row.get("overall", {})
        lines.append(
            f"| {method} | {row.get('status')} | {overall.get('n', 0)} | "
            f"{fmt(float(overall.get('iou', 0.0)))} | {fmt(float(overall.get('dice', 0.0)))} | "
            f"{fmt(float(overall.get('pixel_precision', 0.0)))} | {fmt(float(overall.get('pixel_recall', 0.0)))} | "
            f"{fmt(float(overall.get('pixel_f1', 0.0)))} |"
        )

    lines.extend(["", "## Per Domain", ""])
    lines.append("| method | domain | n | mean IoU | mean pixel F1 |")
    lines.append("|---|---|---:|---:|---:|")
    for method, row in summary["methods"].items():
        for domain, group in row.get("by_domain", {}).items():
            lines.append(f"| {method} | {domain} | {group['n']} | {fmt(float(group['iou']))} | {fmt(float(group['pixel_f1']))} |")

    if "domain_aware_oracle" in summary["methods"]:
        lines.extend(
            [
                "",
                "## Domain-Aware Strategy",
                "",
                "Oracle policy: Photoshop and AIGC-editing use SAM bbox-prompt refinement; DeepFake uses bbox / face-region fallback.",
                "",
                "Predicted policy: use the LoRA-predicted tamper domain; Photoshop/AIGC predictions use SAM, DeepFake/none/unknown fallback to bbox.",
            ]
        )

    if summary.get("prediction_stats"):
        stats = summary["prediction_stats"]
        lines.extend(["", "## Predicted Domain Stats", ""])
        lines.append(f"- predictions found: `{stats.get('found')}/{stats.get('total')}`")
        lines.append(f"- valid JSON: `{stats.get('valid_json')}/{stats.get('total')}`")
        lines.append(f"- valid schema: `{stats.get('valid_schema')}/{stats.get('total')}`")
        lines.append(f"- fallback to bbox: `{stats.get('bbox_fallback')}/{stats.get('total')}`")

    if summary.get("sam_status") != "run":
        lines.extend(["", "## SAM Status", "", f"- status: `{summary.get('sam_status')}`"])
        if summary.get("sam_reason"):
            lines.append(f"- reason: `{summary.get('sam_reason')}`")

    lines.extend(["", "## Samples", ""])
    lines.append("| id | domain | bbox_xyxy | bbox IoU | bbox F1 | SAM IoU | SAM F1 |")
    lines.append("|---|---|---|---:|---:|---:|---:|")
    for record in records:
        bbox = record["methods"]["bbox_mask_baseline"]["metrics"]
        sam = record["methods"].get("sam_refinement", {})
        sam_metrics = sam.get("metrics") or {}
        lines.append(
            f"| {record['id']} | {record['domain']} | `{record['bbox_xyxy']}` | "
            f"{fmt(float(bbox['iou']))} | {fmt(float(bbox['pixel_f1']))} | "
            f"{fmt_optional_metric(sam_metrics, 'iou')} | {fmt_optional_metric(sam_metrics, 'pixel_f1')} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    rows = limit_rows(load_jsonl(args.manifest), args.limit_per_domain)
    dataset_name = args.dataset_name or args.manifest.parent.name
    domain_predictions = load_domain_predictions(args.domain_predictions)
    sam_runner, sam_status, sam_reason = build_sam_runner(args)
    if sam_status == "failed" and args.fail_on_sam_error:
        raise RuntimeError(sam_reason)

    records: list[dict[str, Any]] = []
    for row in rows:
        image_path = Path(row["resolved_image"])
        mask_path = Path(row.get("resolved_gt_mask") or row.get("resolved_mask"))
        image = read_rgb_image(image_path)
        height, width = image.shape[:2]
        gt = read_binary_mask(mask_path, (width, height))
        bbox = bbox_from_mask(gt)
        methods: dict[str, Any] = {}

        base_pred = bbox_mask(gt.shape, bbox)
        methods["bbox_mask_baseline"] = {"status": "run", "metrics": mask_metrics(base_pred, gt)}

        if sam_runner is not None:
            sam_pred, sam_score = sam_runner.predict(image, bbox)
            if sam_pred.shape != gt.shape:
                sam_pred = np.asarray(Image.fromarray(sam_pred.astype(np.uint8) * 255).resize((width, height), Image.Resampling.NEAREST)) > 0
            methods["sam_refinement"] = {
                "status": "run",
                "score": sam_score,
                "metrics": mask_metrics(sam_pred, gt),
            }
        else:
            methods["sam_refinement"] = {"status": sam_status, "reason": sam_reason}

        manifest_bbox = row.get("gt_bbox") or row.get("bbox_xyxy")
        records.append(
            {
                "id": row["id"],
                "domain": row["domain"],
                "source": row.get("source") or row.get("source_dataset"),
                "source_dataset": row.get("source_dataset") or row.get("source"),
                "image": row["image"],
                "mask": row.get("gt_mask") or row.get("mask"),
                "gt_mask": row.get("gt_mask") or row.get("mask"),
                "bbox_xyxy": bbox,
                "gt_bbox": bbox,
                "manifest_bbox_xyxy": manifest_bbox,
                "manifest_bbox_matches": manifest_bbox == bbox,
                "image_width": width,
                "image_height": height,
                "mask_area_pixels": int(gt.sum()),
                "mask_area_ratio": int(gt.sum()) / float(width * height),
                "methods": methods,
            }
        )

    add_domain_aware_methods(records, domain_predictions)
    prediction_stats = {
        "total": len(records),
        "found": sum(1 for record in records if record.get("domain_prediction") is not None),
        "valid_json": sum(1 for record in records if (record.get("domain_prediction") or {}).get("valid_json")),
        "valid_schema": sum(1 for record in records if (record.get("domain_prediction") or {}).get("valid_schema")),
        "bbox_fallback": sum(1 for record in records if record["methods"]["domain_aware_predicted"]["source_method"] == "bbox_mask_baseline"),
    }
    summary = {
        "name": dataset_name,
        "boundary": BOUNDARY_TEXT,
        "manifest": str(args.manifest),
        "n": len(records),
        "sam_status": sam_status,
        "sam_reason": sam_reason,
        "sam_checkpoint": str(args.sam_checkpoint) if args.sam_checkpoint else None,
        "sam_model_type": args.sam_model_type,
        "sam_impl": args.sam_impl,
        "domain_predictions": str(args.domain_predictions) if args.domain_predictions else None,
        "prediction_stats": prediction_stats,
        "methods": {
            "bbox_mask_baseline": summarize(records, "bbox_mask_baseline"),
            "sam_refinement": summarize(records, "sam_refinement"),
            "domain_aware_oracle": summarize(records, "domain_aware_oracle"),
            "domain_aware_predicted": summarize(records, "domain_aware_predicted"),
        },
        "domain_aware_oracle_policy": {
            "photoshop": "sam_refinement",
            "aigc_editing": "sam_refinement",
            "deepfake": "bbox_mask_baseline",
            "fallback": "bbox_mask_baseline if selected method is unavailable",
        },
        "domain_aware_predicted_policy": {
            "photoshop": "sam_refinement",
            "aigc_inpaint": "sam_refinement",
            "aigc_editing": "sam_refinement",
            "deepfake": "bbox_mask_baseline",
            "none": "bbox_mask_baseline",
            "unknown": "bbox_mask_baseline",
            "fallback": "bbox_mask_baseline if selected method is unavailable",
        },
    }

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_jsonl.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.summary_md.parent.mkdir(parents=True, exist_ok=True)
    write_summary_md(args.summary_md, summary, records)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate region_eval_p60 bbox baseline and optional SAM bbox-prompt refinement.")
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/region_eval/region_eval_p60/manifest.jsonl"))
    parser.add_argument("--dataset-name", help="Dataset name used in summaries. Defaults to manifest parent directory name.")
    parser.add_argument("--output-jsonl", type=Path, default=Path("artifacts/region_eval/region_eval_p60/results.jsonl"))
    parser.add_argument("--summary-json", type=Path, default=Path("artifacts/region_eval/region_eval_p60/summary.json"))
    parser.add_argument("--summary-md", type=Path, default=Path("artifacts/region_eval/region_eval_p60/summary.md"))
    parser.add_argument("--domain-predictions", type=Path, help="Optional JSONL with LoRA predicted tamper domains keyed by sample id.")
    parser.add_argument("--limit-per-domain", type=int)
    parser.add_argument("--skip-sam", action="store_true")
    parser.add_argument("--sam-checkpoint", type=Path)
    parser.add_argument("--sam-model-type", choices=["vit_b", "vit_l", "vit_h", "default"], default="vit_b")
    parser.add_argument("--sam-impl", choices=["auto", "segment_anything", "native"], default="auto")
    parser.add_argument("--device", default="cuda:0" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--multimask", action="store_true", help="Request SAM multimask output and select the highest predicted-IoU mask.")
    parser.add_argument("--fail-on-sam-error", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.limit_per_domain is not None and args.limit_per_domain < 1:
        raise ValueError("--limit-per-domain must be positive")
    summary = run_eval(args)
    print("wrote_jsonl", args.output_jsonl)
    print("wrote_summary_json", args.summary_json)
    print("wrote_summary_md", args.summary_md)
    print(json.dumps(summary["methods"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
