from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


def load_binary_mask(path: Path, target_size: tuple[int, int], threshold: int) -> np.ndarray:
    mask_image = Image.open(path).convert("L")
    if mask_image.size != target_size:
        mask_image = mask_image.resize(target_size, Image.Resampling.NEAREST)
    mask = np.array(mask_image)
    return mask > threshold


def compute_bbox_xyxy(mask: np.ndarray) -> list[int]:
    ys, xs = np.where(mask)
    if len(xs) == 0 or len(ys) == 0:
        raise ValueError("empty mask")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def bbox_to_mask(shape: tuple[int, int], bbox: list[int]) -> np.ndarray:
    height, width = shape
    x1, y1, x2, y2 = bbox
    x1 = max(0, min(width, x1))
    x2 = max(0, min(width, x2))
    y1 = max(0, min(height, y1))
    y2 = max(0, min(height, y2))
    mask = np.zeros((height, width), dtype=bool)
    mask[y1:y2, x1:x2] = True
    return mask


def mask_metrics(pred: np.ndarray, gt: np.ndarray) -> dict[str, float]:
    pred = pred.astype(bool)
    gt = gt.astype(bool)
    intersection = float(np.logical_and(pred, gt).sum())
    pred_area = float(pred.sum())
    gt_area = float(gt.sum())
    union = float(np.logical_or(pred, gt).sum())
    precision = intersection / pred_area if pred_area else 0.0
    recall = intersection / gt_area if gt_area else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    iou = intersection / union if union else 0.0
    dice = 2 * intersection / (pred_area + gt_area) if pred_area + gt_area else 0.0
    return {
        "iou": iou,
        "dice": dice,
        "pixel_precision": precision,
        "pixel_recall": recall,
        "pixel_f1": f1,
    }


def relative_or_absolute(path_text: str, root: Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    if path.exists():
        return path
    return root / path


class SamRunner:
    def __init__(self, checkpoint: Path, model_type: str, device: str) -> None:
        try:
            import torch
            from segment_anything import SamPredictor, sam_model_registry
        except Exception as exc:  # pragma: no cover - depends on optional server env
            raise RuntimeError(f"SAM dependencies are unavailable: {exc}") from exc

        if not checkpoint.exists():
            raise FileNotFoundError(checkpoint)

        self.torch = torch
        sam = sam_model_registry[model_type](checkpoint=str(checkpoint))
        if device != "cpu" and not torch.cuda.is_available():
            device = "cpu"
        sam.to(device=device)
        self.predictor = SamPredictor(sam)
        self.device = device

    def predict(self, image_path: Path, bbox_xyxy: list[int]) -> np.ndarray:
        image = np.array(Image.open(image_path).convert("RGB"))
        self.predictor.set_image(image)
        box = np.array(bbox_xyxy, dtype=np.float32)
        masks, scores, _ = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=box[None, :],
            multimask_output=True,
        )
        best = int(np.argmax(scores))
        return masks[best].astype(bool)


def try_make_sam(args: argparse.Namespace) -> tuple[SamRunner | None, str | None]:
    if args.skip_sam:
        return None, "disabled_by_flag"
    try:
        return SamRunner(Path(args.sam_checkpoint), args.sam_model_type, args.device), None
    except Exception as exc:
        return None, repr(exc)


def aggregate(rows: list[dict[str, Any]], method: str) -> dict[str, Any]:
    metric_names = ["iou", "dice", "pixel_precision", "pixel_recall", "pixel_f1"]
    selected = [row for row in rows if row["method"] == method and row["status"] == "run"]
    if not selected:
        return {"n": 0}
    return {
        "n": len(selected),
        **{name: float(np.mean([row[name] for row in selected])) for name in metric_names},
    }


def aggregate_by_domain(rows: list[dict[str, Any]], method: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["method"] == method and row["status"] == "run":
            grouped[row["domain"]].append(row)
    return {domain: aggregate(items, method) for domain, items in sorted(grouped.items())}


def save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((mask.astype(np.uint8) * 255)).save(path)


def run(args: argparse.Namespace) -> None:
    manifest_path = Path(args.manifest)
    dataset_root = Path(args.dataset_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pred_mask_dir = output_dir / "pred_masks"

    rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    sam, sam_error = try_make_sam(args)
    results: list[dict[str, Any]] = []
    bbox_matches = 0

    for row in rows:
        image_path = relative_or_absolute(row.get("resolved_image") or row["image"], dataset_root)
        mask_path = relative_or_absolute(row.get("resolved_mask") or row["mask"], dataset_root)
        image_size = Image.open(image_path).size
        gt_mask = load_binary_mask(mask_path, image_size, args.mask_threshold)
        gt_bbox = compute_bbox_xyxy(gt_mask)
        manifest_bbox = row.get("bbox_xyxy")
        bbox_matches += int(manifest_bbox == gt_bbox)

        bbox_pred = bbox_to_mask(gt_mask.shape, gt_bbox)
        bbox_metrics = mask_metrics(bbox_pred, gt_mask)
        results.append(
            {
                "id": row["id"],
                "domain": row["domain"],
                "source": row.get("source"),
                "image": str(image_path),
                "gt_mask": str(mask_path),
                "gt_bbox": gt_bbox,
                "manifest_bbox": manifest_bbox,
                "bbox_matches_manifest": manifest_bbox == gt_bbox,
                "method": "bbox_from_gtmask",
                "status": "run",
                **bbox_metrics,
            }
        )

        if sam is None:
            results.append(
                {
                    "id": row["id"],
                    "domain": row["domain"],
                    "source": row.get("source"),
                    "image": str(image_path),
                    "gt_mask": str(mask_path),
                    "gt_bbox": gt_bbox,
                    "manifest_bbox": manifest_bbox,
                    "bbox_matches_manifest": manifest_bbox == gt_bbox,
                    "method": "sam_from_gtbbox",
                    "status": "skipped",
                    "skip_reason": sam_error,
                }
            )
            continue

        sam_pred = sam.predict(image_path, gt_bbox)
        sam_metrics = mask_metrics(sam_pred, gt_mask)
        pred_mask_path = pred_mask_dir / row["domain"] / f"{row['id']}_sam.png"
        save_mask(sam_pred, pred_mask_path)
        results.append(
            {
                "id": row["id"],
                "domain": row["domain"],
                "source": row.get("source"),
                "image": str(image_path),
                "gt_mask": str(mask_path),
                "gt_bbox": gt_bbox,
                "manifest_bbox": manifest_bbox,
                "bbox_matches_manifest": manifest_bbox == gt_bbox,
                "method": "sam_from_gtbbox",
                "status": "run",
                "pred_mask": str(pred_mask_path),
                **sam_metrics,
            }
        )

    methods = ["bbox_from_gtmask", "sam_from_gtbbox"]
    summary = {
        "name": output_dir.name,
        "boundary": "GT mask -> GT bbox -> SAM bbox prompt -> predicted mask; evaluates bbox-prompt mask refinement, not automatic forged-region discovery",
        "manifest": str(manifest_path),
        "n_samples": len(rows),
        "bbox_matches_manifest": bbox_matches,
        "sam_status": "run" if sam is not None else "skipped",
        "sam_skip_reason": sam_error,
        "sam_checkpoint": args.sam_checkpoint,
        "sam_model_type": args.sam_model_type,
        "mask_threshold": args.mask_threshold,
        "methods": {
            method: {
                "overall": aggregate(results, method),
                "by_domain": aggregate_by_domain(results, method),
            }
            for method in methods
        },
    }

    results_path = output_dir / "gtmask_to_sam_results.jsonl"
    summary_json_path = output_dir / "gtmask_to_sam_summary.json"
    summary_md_path = output_dir / "gtmask_to_sam_summary.md"
    results_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in results),
        encoding="utf-8",
    )
    summary_json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_summary_md(summary), encoding="utf-8")

    print(f"wrote_results={results_path}")
    print(f"wrote_summary={summary_md_path}")
    print(f"sam_status={summary['sam_status']}")


def render_summary_md(summary: dict[str, Any]) -> str:
    lines = [
        f"# {summary['name']} GT Mask to SAM Grounding",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "## Setup",
        "",
        f"- samples: {summary['n_samples']}",
        f"- bbox matches manifest: {summary['bbox_matches_manifest']}/{summary['n_samples']}",
        f"- sam status: {summary['sam_status']}",
        f"- sam checkpoint: `{summary['sam_checkpoint']}`",
        f"- mask threshold: > {summary['mask_threshold']}",
        "",
        "## Overall",
        "",
        "| method | n | IoU | Dice/F1 | Precision | Recall |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for method, payload in summary["methods"].items():
        metrics = payload["overall"]
        lines.append(
            f"| {method} | {metrics.get('n', 0)} | {metrics.get('iou', 0):.4f} | "
            f"{metrics.get('pixel_f1', 0):.4f} | {metrics.get('pixel_precision', 0):.4f} | "
            f"{metrics.get('pixel_recall', 0):.4f} |"
        )
    lines.extend(["", "## By Domain", "", "| domain | method | n | IoU | Dice/F1 |", "|---|---|---:|---:|---:|"])
    domains = sorted(
        {
            domain
            for payload in summary["methods"].values()
            for domain in payload["by_domain"].keys()
        }
    )
    for domain in domains:
        for method, payload in summary["methods"].items():
            metrics = payload["by_domain"].get(domain, {"n": 0})
            lines.append(
                f"| {domain} | {method} | {metrics.get('n', 0)} | "
                f"{metrics.get('iou', 0):.4f} | {metrics.get('pixel_f1', 0):.4f} |"
            )
    if summary.get("sam_skip_reason"):
        lines.extend(["", "## SAM Skip Reason", "", f"`{summary['sam_skip_reason']}`"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GT-mask -> GT-bbox -> SAM-prompt grounding evaluation.")
    parser.add_argument("--manifest", required=True, help="Region eval manifest JSONL.")
    parser.add_argument("--dataset-root", default=".", help="Root used to resolve relative image/mask paths.")
    parser.add_argument("--output-dir", required=True, help="Output directory.")
    parser.add_argument("--sam-checkpoint", default="weight/sam_vit_b_01ec64.pth")
    parser.add_argument("--sam-model-type", default="vit_b")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--skip-sam", action="store_true")
    parser.add_argument("--mask-threshold", type=int, default=0, help="Mask pixels greater than this value are foreground.")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
