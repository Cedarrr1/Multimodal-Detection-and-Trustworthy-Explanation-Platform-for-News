#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from eval_region_grounding_p60 import bbox_mask, mask_metrics, read_binary_mask


METRIC_KEYS = ["iou", "pixel_f1", "pixel_precision", "pixel_recall"]
DEFAULT_POLICY = {
    "routing_mode": "global_domain",
    "allow_patch_verdict_override": False,
    "proposal_score_threshold": 0.5,
    "photoshop_patch_threshold": 0.5,
    "aigc_patch_threshold": 0.5,
    "face_score_threshold": 0.5,
    "max_boxes_per_image": 2,
    "nms_iou_threshold": 0.5,
    "sam_score_threshold": 0.5,
    "sam_area_box_ratio_min": 0.005,
    "sam_area_box_ratio_max": 1.0,
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def safe_div(num: int, den: int) -> float | None:
    return num / den if den else None


def label_domain(label: dict[str, Any]) -> str:
    domain = str(label.get("tamper_domain") or "none")
    if domain == "aigc_editing":
        return "aigc_inpaint"
    return domain


def domain_matches(pred: str, truth: str) -> bool:
    if truth == "aigc_editing":
        truth = "aigc_inpaint"
    return pred == truth


def box_iou(a: list[int], b: list[int]) -> float:
    ax0, ay0, ax1, ay1 = [int(v) for v in a]
    bx0, by0, bx1, by1 = [int(v) for v in b]
    ix0 = max(ax0, bx0)
    iy0 = max(ay0, by0)
    ix1 = min(ax1, bx1)
    iy1 = min(ay1, by1)
    inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
    area_a = max(0, ax1 - ax0) * max(0, ay1 - ay0)
    area_b = max(0, bx1 - bx0) * max(0, by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union else 0.0


def box_area(box: list[int]) -> int:
    return max(0, int(box[2]) - int(box[0])) * max(0, int(box[3]) - int(box[1]))


def candidate_domain_score(item: dict[str, Any], domain: str) -> float:
    if domain == "photoshop":
        return float(item.get("photoshop_patch_score", (item.get("domain_scores") or {}).get("photoshop", item.get("proposal_score", 0.0))))
    if domain == "aigc_inpaint":
        return float(item.get("aigc_patch_score", (item.get("domain_scores") or {}).get("aigc_inpaint", item.get("proposal_score", 0.0))))
    if domain == "deepfake":
        return float(item.get("deepfake_patch_score", (item.get("domain_scores") or {}).get("deepfake", 0.0)))
    return float(item.get("proposal_score", 0.0))


def candidate_score_for_policy(item: dict[str, Any], policy: dict[str, Any], domain: str | None = None) -> float:
    if domain is None or policy.get("routing_mode") != "patch_priority":
        return float(item.get("proposal_score", 0.0))
    return candidate_domain_score(item, domain)


def patch_domain_max(record: dict[str, Any], domain: str) -> float:
    return max([candidate_domain_score(item, domain) for item in (record.get("raw_proposals") or [])], default=0.0)


def nms(candidates: list[dict[str, Any]], threshold: float, policy: dict[str, Any] | None = None, domain: str | None = None) -> list[dict[str, Any]]:
    ordered = sorted(
        candidates,
        key=lambda item: (candidate_score_for_policy(item, policy or {}, domain), float(item.get("sam_score") or 0.0)),
        reverse=True,
    )
    kept: list[dict[str, Any]] = []
    for item in ordered:
        if all(box_iou(item["box_xyxy"], other["box_xyxy"]) <= threshold for other in kept):
            kept.append(item)
    return kept


class MaskCache:
    def __init__(self) -> None:
        self.cache: dict[str, np.ndarray] = {}

    def load(self, path: str, size: tuple[int, int] | None = None) -> np.ndarray:
        if path not in self.cache:
            with Image.open(path) as image:
                mask = image.convert("L")
                if size and mask.size != size:
                    mask = mask.resize(size, Image.Resampling.NEAREST)
                self.cache[path] = np.asarray(mask) > 0
        return self.cache[path]


def empty_mask(width: int, height: int) -> np.ndarray:
    return np.zeros((height, width), dtype=bool)


def save_mask(mask: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask.astype(np.uint8) * 255).save(path)


def select_sam_candidates(record: dict[str, Any], policy: dict[str, Any], domain: str | None = None) -> list[dict[str, Any]]:
    candidates = []
    for item in record.get("sam_candidates") or []:
        sam_score = item.get("sam_score")
        ratio = item.get("mask_area_box_ratio")
        if candidate_score_for_policy(item, policy, domain) < float(policy["proposal_score_threshold"]):
            continue
        if sam_score is None or float(sam_score) < float(policy["sam_score_threshold"]):
            continue
        if ratio is None:
            continue
        ratio_f = float(ratio)
        if ratio_f < float(policy["sam_area_box_ratio_min"]):
            continue
        if ratio_f > float(policy["sam_area_box_ratio_max"]):
            continue
        candidates.append(item)
    return nms(candidates, float(policy["nms_iou_threshold"]), policy, domain)[: int(policy["max_boxes_per_image"])]


def route_policy(record: dict[str, Any], policy: dict[str, Any]) -> tuple[str, str]:
    global_pred = record.get("global_prediction") or {}
    verdict = str(global_pred.get("pred_verdict", "unknown"))
    domain = str(global_pred.get("pred_tamper_domain", "unknown"))
    valid_schema = bool(global_pred.get("valid_schema"))
    if not valid_schema:
        return "none", "global_invalid_or_not_tampered"
    if policy.get("routing_mode") != "patch_priority":
        if verdict != "tampered":
            return "none", "global_invalid_or_not_tampered"
        if domain in {"photoshop", "aigc_inpaint", "deepfake"}:
            return domain, "global_domain"
        return "none", "unsupported_or_unknown_predicted_domain"

    if patch_domain_max(record, "photoshop") >= float(policy.get("photoshop_patch_threshold", 0.5)):
        if verdict != "tampered" and not bool(policy.get("allow_patch_verdict_override", False)):
            return "none", "global_invalid_or_not_tampered"
        return "photoshop", "photoshop_patch"

    if verdict != "tampered":
        return "none", "global_invalid_or_not_tampered"

    face = record.get("face_candidate") or {}
    if float(face.get("face_score", 0.0)) >= float(policy.get("face_score_threshold", 0.5)):
        return "deepfake", "face"

    if domain == "aigc_inpaint" and patch_domain_max(record, "aigc_inpaint") >= float(policy.get("aigc_patch_threshold", policy["proposal_score_threshold"])):
        return "aigc_inpaint", "global_aigc"

    return "none", "patch_priority_fallback"


def apply_policy(
    record: dict[str, Any],
    label: dict[str, Any],
    policy: dict[str, Any],
    mask_cache: MaskCache,
    save_dir: Path | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    width = int(label.get("image_width") or record.get("image_width"))
    height = int(label.get("image_height") or record.get("image_height"))
    pred = empty_mask(width, height)
    global_pred = record.get("global_prediction") or {}
    verdict = str(global_pred.get("pred_verdict", "unknown"))
    global_domain = str(global_pred.get("pred_tamper_domain", "unknown"))
    valid_schema = bool(global_pred.get("valid_schema"))
    routed_domain, route_reason = route_policy(record, policy)
    decision: dict[str, Any] = {
        "pred_verdict": verdict,
        "pred_tamper_domain": global_domain,
        "routed_domain": routed_domain,
        "route_reason": route_reason,
        "mask_policy": "empty",
        "selected_boxes": [],
        "selected_candidate_indices": [],
        "fallback_reason": None,
        "pred_mask": None,
    }
    if not valid_schema or (verdict != "tampered" and routed_domain == "none"):
        decision["fallback_reason"] = "global_invalid_or_not_tampered"
    elif routed_domain == "deepfake":
        face = record.get("face_candidate") or {}
        box = face.get("box_xyxy")
        if box:
            pred = bbox_mask((height, width), [int(v) for v in box])
            decision["mask_policy"] = "deepfake_face_bbox"
            decision["selected_boxes"] = [[int(v) for v in box]]
            decision["fallback_reason"] = face.get("fallback_reason")
        else:
            decision["fallback_reason"] = "deepfake_no_face_candidate"
    elif routed_domain in {"photoshop", "aigc_inpaint"}:
        selected = select_sam_candidates(record, policy, routed_domain)
        if selected:
            for item in selected:
                mask = mask_cache.load(str(item["mask_path"]), (width, height))
                pred = np.logical_or(pred, mask)
            decision["mask_policy"] = "sam_union"
            decision["selected_boxes"] = [[int(v) for v in item["box_xyxy"]] for item in selected]
            decision["selected_candidate_indices"] = [int(item["index"]) for item in selected]
        else:
            decision["fallback_reason"] = "no_sam_candidate_after_gate"
    else:
        decision["fallback_reason"] = route_reason

    if save_dir is not None:
        mask_path = save_dir / f"{label['id']}.png"
        save_mask(pred, mask_path)
        decision["pred_mask"] = str(mask_path)
    return pred, decision


def proposal_boxes_for_record(record: dict[str, Any], policy: dict[str, Any]) -> list[list[int]]:
    global_pred = record.get("global_prediction") or {}
    if not bool(global_pred.get("valid_schema")):
        return []
    routed_domain, _reason = route_policy(record, policy)
    if routed_domain == "none":
        return []
    if routed_domain == "deepfake":
        face = record.get("face_candidate") or {}
        return [face["box_xyxy"]] if face.get("box_xyxy") else []
    if routed_domain in {"photoshop", "aigc_inpaint"}:
        return [
            item["box_xyxy"]
            for item in (record.get("raw_proposals") or [])
            if candidate_score_for_policy(item, policy, routed_domain) >= float(policy["proposal_score_threshold"])
        ]
    return []


def tampered_failure_reason(row: dict[str, Any]) -> str:
    if not row["valid_schema"] or row["pred_verdict"] != "tampered":
        return "image_level_miss"
    if not row["route_domain_correct"]:
        return "domain_route_error"
    if row["proposal_count"] == 0:
        return "no_candidate"
    if row["best_box_iou"] < 0.3:
        return "proposal_miss"
    if row["pred_pixels"] == 0:
        return "empty_final_mask"
    if row["iou"] < 0.3:
        return "refinement_fail"
    return "success"


def evaluate_dataset(
    name: str,
    cache_records: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
    policy: dict[str, Any],
    output_dir: Path | None,
    mask_cache: MaskCache | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mask_cache = mask_cache or MaskCache()
    records_by_id = {str(row["id"]): row for row in cache_records}
    missing = sorted(str(row["id"]) for row in eval_rows if str(row["id"]) not in records_by_id)
    if missing:
        raise RuntimeError(f"{name}: missing pipeline cache records: {len(missing)} first={missing[:5]}")
    results: list[dict[str, Any]] = []
    pred_mask_dir = output_dir / "pred_masks" if output_dir else None
    for label in eval_rows:
        record = records_by_id[str(label["id"])]
        pred_mask, decision = apply_policy(record, label, policy, mask_cache, pred_mask_dir)
        width = int(label.get("image_width") or record.get("image_width"))
        height = int(label.get("image_height") or record.get("image_height"))
        is_tampered = str(label["label"]) == "tampered"
        global_pred = record.get("global_prediction") or {}
        pred_verdict = str(global_pred.get("pred_verdict", "unknown"))
        pred_domain = str(global_pred.get("pred_tamper_domain", "unknown"))
        routed_domain = str(decision.get("routed_domain", "none"))
        pred_pixels = int(pred_mask.sum())
        base = {
            "split": name,
            "id": label["id"],
            "source": label.get("source"),
            "source_domain": label.get("source_domain"),
            "label": label["label"],
            "truth_verdict": label["verdict"],
            "truth_tamper_domain": label.get("tamper_domain"),
            "pred_verdict": pred_verdict,
            "pred_tamper_domain": pred_domain,
            "routed_domain": routed_domain,
            "route_reason": decision.get("route_reason"),
            "valid_json": bool(global_pred.get("valid_json")),
            "valid_schema": bool(global_pred.get("valid_schema")),
            "verdict_correct": pred_verdict == label["verdict"],
            "domain_correct": (not is_tampered) or domain_matches(pred_domain, label_domain(label)),
            "route_domain_correct": (not is_tampered) or domain_matches(routed_domain, label_domain(label)),
            "mask_policy": decision["mask_policy"],
            "selected_boxes": decision["selected_boxes"],
            "fallback_reason": decision["fallback_reason"],
            "pred_mask": decision["pred_mask"],
            "pred_pixels": pred_pixels,
            "pred_area_ratio": pred_pixels / float(width * height),
        }
        if is_tampered:
            gt_mask = read_binary_mask(Path(label["resolved_gt_mask"]), (width, height))
            metrics = mask_metrics(pred_mask, gt_mask)
            proposal_boxes = proposal_boxes_for_record(record, policy)
            gt_bbox = label.get("gt_bbox")
            best_box_iou = max([box_iou(box, gt_bbox) for box in proposal_boxes], default=0.0) if gt_bbox else 0.0
            row = {
                **base,
                **{key: float(metrics[key]) for key in METRIC_KEYS},
                "proposal_count": len(proposal_boxes),
                "best_box_iou": best_box_iou,
                "proposal_recall_iou_0_3": best_box_iou >= 0.3,
                "proposal_recall_iou_0_5": best_box_iou >= 0.5,
            }
            row["failure_reason"] = tampered_failure_reason(row)
            results.append(row)
        else:
            results.append(
                {
                    **base,
                    "empty_mask_correct": pred_pixels == 0,
                    "false_positive_mask": pred_pixels > 0,
                }
            )
    return results, summarize_all(results)


def bootstrap_ci(rows: list[dict[str, Any]], key: str, samples: int, seed: int) -> dict[str, float] | None:
    values = [float(row[key]) for row in rows if key in row and row[key] is not None]
    if not values or samples <= 0:
        return None
    rng = random.Random(seed)
    boot = []
    for _ in range(samples):
        boot.append(mean([values[rng.randrange(len(values))] for _ in values]))
    boot.sort()
    lo = boot[int(0.025 * (len(boot) - 1))]
    hi = boot[int(0.975 * (len(boot) - 1))]
    return {"low": lo, "high": hi}


def add_metric_ci(payload: dict[str, Any], rows: list[dict[str, Any]], samples: int, seed: int, keys: list[str]) -> None:
    for key in keys:
        ci = bootstrap_ci(rows, key, samples, seed + len(key) * 9973)
        if ci:
            payload[f"{key}_ci95"] = ci


def image_level_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    tampered = [row for row in rows if row["label"] == "tampered"]
    authentic = [row for row in rows if row["label"] == "authentic"]
    tampered_hit = sum(row["pred_verdict"] == "tampered" for row in tampered)
    authentic_hit = sum(row["pred_verdict"] == "authentic" for row in authentic)
    return {
        "n": total,
        "valid_json": safe_div(sum(bool(row["valid_json"]) for row in rows), total),
        "valid_schema": safe_div(sum(bool(row["valid_schema"]) for row in rows), total),
        "verdict_accuracy": safe_div(sum(bool(row["verdict_correct"]) for row in rows), total),
        "balanced_accuracy": ((tampered_hit / len(tampered)) + (authentic_hit / len(authentic))) / 2.0 if tampered and authentic else None,
        "tampered_recall": safe_div(tampered_hit, len(tampered)),
        "authentic_accuracy": safe_div(authentic_hit, len(authentic)),
        "tamper_domain_accuracy": safe_div(sum(bool(row["domain_correct"]) for row in tampered), len(tampered)),
        "route_domain_accuracy": safe_div(sum(bool(row.get("route_domain_correct")) for row in tampered), len(tampered)),
    }


def localization_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {"n": len(rows)}
    for key in METRIC_KEYS:
        payload[key] = mean([float(row[key]) for row in rows]) if rows else None
    return payload


def authentic_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    return {
        "n": n,
        "empty_mask_accuracy": safe_div(sum(bool(row["empty_mask_correct"]) for row in rows), n),
        "false_positive_mask_rate": safe_div(sum(bool(row["false_positive_mask"]) for row in rows), n),
        "mean_false_positive_area_ratio": mean([float(row["pred_area_ratio"]) for row in rows]) if rows else None,
    }


def route_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    return {
        "n": n,
        "global_domain_accuracy": safe_div(sum(bool(row.get("domain_correct")) for row in rows), n),
        "route_domain_accuracy": safe_div(sum(bool(row.get("route_domain_correct")) for row in rows), n),
        "routed_domain_counts": dict(sorted(Counter(str(row.get("routed_domain", "missing")) for row in rows).items())),
        "route_reason_counts": dict(sorted(Counter(str(row.get("route_reason", "missing")) for row in rows).items())),
    }


def proposal_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    return {
        "n": n,
        "mean_best_box_iou": mean([float(row["best_box_iou"]) for row in rows]) if rows else None,
        "proposal_recall_iou_0_3": safe_div(sum(bool(row["proposal_recall_iou_0_3"]) for row in rows), n),
        "proposal_recall_iou_0_5": safe_div(sum(bool(row["proposal_recall_iou_0_5"]) for row in rows), n),
        "failure_reason_counts": dict(sorted(Counter(str(row["failure_reason"]) for row in rows).items())),
    }


def summarize_by(rows: list[dict[str, Any]], key: str, fn) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    return {name: fn(group) for name, group in sorted(groups.items())}


def summarize_all(rows: list[dict[str, Any]], bootstrap_samples: int = 0, bootstrap_seed: int = 0) -> dict[str, Any]:
    tampered = [row for row in rows if row["label"] == "tampered"]
    authentic = [row for row in rows if row["label"] == "authentic"]
    conditional = [row for row in tampered if row["valid_schema"] and row["pred_verdict"] == "tampered"]
    summary = {
        "image_level": image_level_summary(rows),
        "tampered_full_end2end": localization_summary(tampered),
        "tampered_conditional": localization_summary(conditional),
        "authentic_handling": authentic_summary(authentic),
        "proposal_diagnostics": proposal_summary(tampered),
        "tampered_full_by_domain": summarize_by(tampered, "source_domain", localization_summary),
        "tampered_full_by_source": summarize_by(tampered, "source", localization_summary),
        "authentic_by_domain": summarize_by(authentic, "source_domain", authentic_summary),
        "tampered_route_by_domain": summarize_by(tampered, "source_domain", route_summary),
    }
    if bootstrap_samples > 0:
        add_metric_ci(summary["tampered_full_end2end"], tampered, bootstrap_samples, bootstrap_seed, METRIC_KEYS)
        add_metric_ci(summary["tampered_conditional"], conditional, bootstrap_samples, bootstrap_seed + 101, METRIC_KEYS)
        add_metric_ci(summary["proposal_diagnostics"], tampered, bootstrap_samples, bootstrap_seed + 202, ["best_box_iou"])
    return summary


def float_grid(start: float, end: float, step: float) -> list[float]:
    values = []
    value = start
    while value <= end + 1e-9:
        values.append(round(value, 6))
        value += step
    return values


def parse_float_list(text: str) -> list[float]:
    return [float(item.strip()) for item in text.split(",") if item.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def policy_hash(policy: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(policy, sort_keys=True).encode("utf-8")).hexdigest()[:12]


def quantiles(values: list[float], points: list[float]) -> dict[str, float]:
    if not values:
        return {}
    ordered = sorted(values)
    return {
        f"{point:.2f}": ordered[min(len(ordered) - 1, int(point * (len(ordered) - 1)))]
        for point in points
    }


def sam_score_distribution(records: list[dict[str, Any]], thresholds: list[float]) -> dict[str, Any]:
    scores = [
        float(item["sam_score"])
        for record in records
        for item in (record.get("sam_candidates") or [])
        if item.get("sam_score") is not None
    ]
    if not scores:
        return {
            "count": 0,
            "threshold_pass_counts": {str(threshold): 0 for threshold in thresholds},
        }
    return {
        "count": len(scores),
        "min": min(scores),
        "max": max(scores),
        "mean": mean(scores),
        "quantiles": quantiles(scores, [0.0, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0]),
        "above_one_count": sum(score > 1.0 for score in scores),
        "threshold_pass_counts": {str(threshold): sum(score >= threshold for score in scores) for threshold in thresholds},
    }


def sam_score_thresholds(args: argparse.Namespace) -> list[float]:
    if args.sam_score_thresholds:
        thresholds = parse_float_list(args.sam_score_thresholds)
    else:
        thresholds = float_grid(args.sam_score_start, args.sam_score_end, args.sam_score_step)
    if not args.allow_sam_score_threshold_gt_1:
        over_one = [threshold for threshold in thresholds if threshold > 1.0]
        if over_one:
            raise ValueError(
                "SAM score thresholds > 1.0 are disabled by default; "
                f"got {over_one}. Use --allow-sam-score-threshold-gt-1 only for debug reproduction."
            )
    return thresholds


def policy_candidates(args: argparse.Namespace) -> list[dict[str, Any]]:
    out = []
    score_thresholds = sam_score_thresholds(args)
    routing_modes = [item.strip() for item in args.routing_modes.split(",") if item.strip()]
    for routing_mode in routing_modes:
        if routing_mode not in {"global_domain", "patch_priority"}:
            raise ValueError(f"unsupported routing mode: {routing_mode}")
        photoshop_thresholds = parse_float_list(args.photoshop_patch_thresholds) if routing_mode == "patch_priority" else [0.5]
        aigc_thresholds = parse_float_list(args.aigc_patch_thresholds) if routing_mode == "patch_priority" else [0.5]
        face_thresholds = parse_float_list(args.face_score_thresholds) if routing_mode == "patch_priority" else [0.5]
        for photoshop_threshold in photoshop_thresholds:
            for aigc_threshold in aigc_thresholds:
                for face_threshold in face_thresholds:
                    for proposal_threshold in parse_float_list(args.proposal_score_thresholds):
                        for max_boxes in parse_int_list(args.max_boxes_per_image_values):
                            for nms_threshold in parse_float_list(args.nms_iou_thresholds):
                                for sam_score in score_thresholds:
                                    for area_min in parse_float_list(args.sam_area_min_values):
                                        for area_max in parse_float_list(args.sam_area_max_values):
                                            if area_max < area_min:
                                                continue
                                            out.append(
                                                {
                                                    "routing_mode": routing_mode,
                                                    "proposal_score_threshold": proposal_threshold,
                                                    "photoshop_patch_threshold": photoshop_threshold,
                                                    "aigc_patch_threshold": aigc_threshold,
                                                    "face_score_threshold": face_threshold,
                                                    "max_boxes_per_image": max_boxes,
                                                    "nms_iou_threshold": nms_threshold,
                                                    "sam_score_threshold": sam_score,
                                                    "sam_area_box_ratio_min": area_min,
                                                    "sam_area_box_ratio_max": area_max,
                                                }
                                            )
    return out


def selected_sam_key(record: dict[str, Any], policy: dict[str, Any], domain: str | None = None) -> tuple[int, ...]:
    return tuple(int(item["index"]) for item in select_sam_candidates(record, policy, domain))


def cached_selected_sam_metrics(
    record: dict[str, Any],
    label: dict[str, Any],
    policy: dict[str, Any],
    domain: str | None,
    mask_cache: MaskCache,
    metrics_cache: dict[tuple[str, str | None, tuple[int, ...]], dict[str, Any]],
) -> dict[str, Any]:
    key = (str(label["id"]), domain, selected_sam_key(record, policy, domain))
    if key in metrics_cache:
        return metrics_cache[key]

    width = int(label.get("image_width") or record.get("image_width"))
    height = int(label.get("image_height") or record.get("image_height"))
    pred = empty_mask(width, height)
    selected_by_index = {int(item["index"]): item for item in select_sam_candidates(record, policy, domain)}
    for index in key[2]:
        item = selected_by_index[index]
        pred = np.logical_or(pred, mask_cache.load(str(item["mask_path"]), (width, height)))
    gt_mask = mask_cache.load(str(label["resolved_gt_mask"]), (width, height))
    metrics = mask_metrics(pred, gt_mask)
    out = {
        **{metric_key: float(metrics[metric_key]) for metric_key in METRIC_KEYS},
        "pred_pixels": int(pred.sum()),
        "selected_count": len(key[1]),
    }
    metrics_cache[key] = out
    return out


def face_metrics(record: dict[str, Any], label: dict[str, Any]) -> dict[str, Any]:
    width = int(label.get("image_width") or record.get("image_width"))
    height = int(label.get("image_height") or record.get("image_height"))
    face = record.get("face_candidate") or {}
    box = face.get("box_xyxy")
    pred = bbox_mask((height, width), [int(v) for v in box]) if box else empty_mask(width, height)
    gt_mask = read_binary_mask(Path(label["resolved_gt_mask"]), (width, height))
    metrics = mask_metrics(pred, gt_mask)
    return {
        **{metric_key: float(metrics[metric_key]) for metric_key in METRIC_KEYS},
        "pred_pixels": int(pred.sum()),
    }


def fast_search_summary(
    dev_cache: list[dict[str, Any]],
    dev_eval: list[dict[str, Any]],
    policy: dict[str, Any],
    mask_cache: MaskCache,
    metrics_cache: dict[tuple[str, tuple[int, ...]], dict[str, Any]],
    face_cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    records_by_id = {str(row["id"]): row for row in dev_cache}
    tampered_rows = []
    authentic_fp = 0
    authentic_n = 0
    selected_sam_image_count = 0
    selected_sam_candidate_count = 0

    for label in dev_eval:
        record = records_by_id[str(label["id"])]
        global_pred = record.get("global_prediction") or {}
        pred_verdict = str(global_pred.get("pred_verdict", "unknown"))
        pred_domain = str(global_pred.get("pred_tamper_domain", "unknown"))
        valid_schema = bool(global_pred.get("valid_schema"))
        routed_domain, _route_reason = route_policy(record, policy)
        is_tampered = str(label["label"]) == "tampered"

        if not is_tampered:
            authentic_n += 1
            pred_pixels = 0
            if valid_schema and (pred_verdict == "tampered" or routed_domain != "none"):
                if routed_domain == "deepfake":
                    face = record.get("face_candidate") or {}
                    pred_pixels = box_area(face.get("box_xyxy") or [0, 0, 0, 0])
                elif routed_domain in {"photoshop", "aigc_inpaint"}:
                    selected = select_sam_candidates(record, policy, routed_domain)
                    selected_sam_image_count += int(bool(selected))
                    selected_sam_candidate_count += len(selected)
                    pred_pixels = sum(
                        int(item.get("mask_area_pixels") or 0)
                        for item in selected
                    )
            authentic_fp += int(pred_pixels > 0)
            continue

        domain_correct = domain_matches(pred_domain, label_domain(label))
        route_domain_correct = domain_matches(routed_domain, label_domain(label))
        metrics = {metric_key: 0.0 for metric_key in METRIC_KEYS}
        pred_pixels = 0
        proposal_count = 0
        best_box_iou = 0.0

        if valid_schema and (pred_verdict == "tampered" or routed_domain != "none"):
            proposal_boxes = proposal_boxes_for_record(record, policy)
            proposal_count = len(proposal_boxes)
            gt_bbox = label.get("gt_bbox")
            best_box_iou = max([box_iou(box, gt_bbox) for box in proposal_boxes], default=0.0) if gt_bbox else 0.0
            if routed_domain == "deepfake":
                face_key = str(label["id"])
                if face_key not in face_cache:
                    face_cache[face_key] = face_metrics(record, label)
                metrics = {metric_key: float(face_cache[face_key][metric_key]) for metric_key in METRIC_KEYS}
                pred_pixels = int(face_cache[face_key]["pred_pixels"])
            elif routed_domain in {"photoshop", "aigc_inpaint"}:
                selected = select_sam_candidates(record, policy, routed_domain)
                selected_sam_image_count += int(bool(selected))
                selected_sam_candidate_count += len(selected)
                cached = cached_selected_sam_metrics(record, label, policy, routed_domain, mask_cache, metrics_cache)
                metrics = {metric_key: float(cached[metric_key]) for metric_key in METRIC_KEYS}
                pred_pixels = int(cached["pred_pixels"])

        row = {
            "label": label["label"],
            "valid_schema": valid_schema,
            "pred_verdict": pred_verdict,
            "domain_correct": domain_correct,
            "route_domain_correct": route_domain_correct,
            "pred_pixels": pred_pixels,
            "proposal_count": proposal_count,
            "best_box_iou": best_box_iou,
            "proposal_recall_iou_0_3": best_box_iou >= 0.3,
            "proposal_recall_iou_0_5": best_box_iou >= 0.5,
            **metrics,
        }
        row["failure_reason"] = tampered_failure_reason(row)
        tampered_rows.append(row)

    return {
        "tampered_full_iou": mean([float(row["iou"]) for row in tampered_rows]),
        "tampered_full_f1": mean([float(row["pixel_f1"]) for row in tampered_rows]),
        "authentic_false_positive_mask_rate": safe_div(authentic_fp, authentic_n) or 0.0,
        "selected_sam_image_count": selected_sam_image_count,
        "selected_sam_candidate_count": selected_sam_candidate_count,
        "failure_reason_counts": dict(sorted(Counter(str(row["failure_reason"]) for row in tampered_rows).items())),
    }


def search_policy(dev_cache: list[dict[str, Any]], dev_eval: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    candidates = policy_candidates(args)
    mask_cache = MaskCache()
    metrics_cache: dict[tuple[str, str | None, tuple[int, ...]], dict[str, Any]] = {}
    face_cache: dict[str, dict[str, Any]] = {}
    best: dict[str, Any] | None = None
    search_rows = []
    for idx, policy in enumerate(candidates):
        summary = fast_search_summary(dev_cache, dev_eval, policy, mask_cache, metrics_cache, face_cache)
        full_iou = summary["tampered_full_iou"]
        full_f1 = summary["tampered_full_f1"]
        auth_fpr = summary["authentic_false_positive_mask_rate"]
        eligible = auth_fpr <= args.max_auth_fpr
        key = (1 if eligible else 0, full_iou, full_f1, -auth_fpr)
        item = {
            "policy": policy,
            "policy_hash": policy_hash(policy),
            "eligible": eligible,
            "tampered_full_iou": full_iou,
            "tampered_full_f1": full_f1,
            "authentic_false_positive_mask_rate": auth_fpr,
            "selected_sam_image_count": summary["selected_sam_image_count"],
            "selected_sam_candidate_count": summary["selected_sam_candidate_count"],
            "failure_reason_counts": summary["failure_reason_counts"],
        }
        search_rows.append(item)
        if best is None or key > best["score_key"]:
            best = {**item, "score_key": key, "candidate_index": idx}
    if best is None:
        raise RuntimeError("policy search produced no candidates")
    top = sorted(search_rows, key=lambda item: (item["eligible"], item["tampered_full_iou"], item["tampered_full_f1"], -item["authentic_false_positive_mask_rate"]), reverse=True)[:20]
    return {
        "locked_policy": best["policy"],
        "locked_policy_hash": best["policy_hash"],
        "best_dev": {key: value for key, value in best.items() if key not in {"score_key"}},
        "searched_candidates": len(search_rows),
        "max_auth_fpr": args.max_auth_fpr,
        "sam_score_thresholds": sam_score_thresholds(args),
        "sam_score_distribution": sam_score_distribution(dev_cache, sam_score_thresholds(args)),
        "locked_policy_selected_no_sam_candidates": int(best["selected_sam_candidate_count"]) == 0,
        "top_candidates": top,
    }


def render_md(summary: dict[str, Any]) -> str:
    eval_summary = summary["eval_summary"]
    lines = [
        f"# {summary['name']} End-to-End Region Localization",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "## Policy",
        "",
        f"- source: `{summary['policy_source']}`",
        f"- hash: `{summary['locked_policy_hash']}`",
        f"- policy: `{summary['locked_policy']}`",
        "",
        "## Image-Level",
        "",
        "| n | valid_schema | verdict_acc | balanced_acc | tampered_recall | authentic_acc | domain_acc | route_domain_acc |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    policy_search = summary.get("policy_search")
    if policy_search:
        best_dev = policy_search.get("best_dev") or {}
        score_dist = policy_search.get("sam_score_distribution") or {}
        lines[lines.index("## Image-Level"):lines.index("## Image-Level")] = [
            "## Policy Search Diagnostics",
            "",
            f"- searched candidates: `{policy_search.get('searched_candidates')}`",
            f"- max authentic FP-mask rate: `{fmt(policy_search.get('max_auth_fpr'))}`",
            f"- SAM score thresholds: `{policy_search.get('sam_score_thresholds')}`",
            f"- SAM score count/min/max/mean: `{score_dist.get('count')}` / `{fmt(score_dist.get('min'))}` / `{fmt(score_dist.get('max'))}` / `{fmt(score_dist.get('mean'))}`",
            f"- SAM score quantiles: `{score_dist.get('quantiles')}`",
            f"- SAM threshold pass counts: `{score_dist.get('threshold_pass_counts')}`",
            f"- SAM score > 1.0 count: `{score_dist.get('above_one_count', 0)}`",
            f"- locked selected SAM candidates/images on dev: `{best_dev.get('selected_sam_candidate_count')}` / `{best_dev.get('selected_sam_image_count')}`",
            f"- locked policy selected no SAM candidates: `{policy_search.get('locked_policy_selected_no_sam_candidates')}`",
            "",
        ]
    image = eval_summary["image_level"]
    lines.append(
        f"| {image['n']} | {fmt(image['valid_schema'])} | {fmt(image['verdict_accuracy'])} | {fmt(image['balanced_accuracy'])} | "
        f"{fmt(image['tampered_recall'])} | {fmt(image['authentic_accuracy'])} | {fmt(image['tamper_domain_accuracy'])} | "
        f"{fmt(image.get('route_domain_accuracy'))} |"
    )
    lines.extend(
        [
            "",
            "## Localization",
            "",
            "| set | n | IoU | F1 | Precision | Recall |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for key, title in [("tampered_full_end2end", "tampered full end-to-end"), ("tampered_conditional", "tampered conditional")]:
        payload = eval_summary[key]
        lines.append(
            f"| {title} | {payload['n']} | {fmt_ci(payload, 'iou')} | {fmt_ci(payload, 'pixel_f1')} | "
            f"{fmt_ci(payload, 'pixel_precision')} | {fmt_ci(payload, 'pixel_recall')} |"
        )
    for key, title in [("tampered_full_by_domain", "Tampered Full By Domain"), ("tampered_full_by_source", "Tampered Full By Source")]:
        groups = eval_summary.get(key) or {}
        if groups:
            lines.extend(
                [
                    "",
                    f"## {title}",
                    "",
                    "| group | n | IoU | F1 | Precision | Recall |",
                    "|---|---:|---:|---:|---:|---:|",
                ]
            )
            for group_name, payload in groups.items():
                lines.append(
                    f"| {group_name} | {payload['n']} | {fmt(payload.get('iou'))} | {fmt(payload.get('pixel_f1'))} | "
                    f"{fmt(payload.get('pixel_precision'))} | {fmt(payload.get('pixel_recall'))} |"
                )
    auth = eval_summary["authentic_handling"]
    prop = eval_summary["proposal_diagnostics"]
    lines.extend(
        [
            "",
            "## Authentic Handling",
            "",
            f"- empty-mask accuracy: `{fmt(auth['empty_mask_accuracy'])}`",
            f"- false-positive-mask rate: `{fmt(auth['false_positive_mask_rate'])}`",
            f"- mean false-positive area ratio: `{fmt(auth['mean_false_positive_area_ratio'])}`",
        ]
    )
    auth_groups = eval_summary.get("authentic_by_domain") or {}
    if auth_groups:
        lines.extend(
            [
                "",
                "## Authentic By Domain",
                "",
                "| group | n | empty-mask acc | FP-mask rate | mean FP area ratio |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for group_name, payload in auth_groups.items():
            lines.append(
                f"| {group_name} | {payload['n']} | {fmt(payload.get('empty_mask_accuracy'))} | "
                f"{fmt(payload.get('false_positive_mask_rate'))} | {fmt(payload.get('mean_false_positive_area_ratio'))} |"
            )
    route_groups = eval_summary.get("tampered_route_by_domain") or {}
    if route_groups:
        lines.extend(
            [
                "",
                "## Route By Domain",
                "",
                "| group | n | global domain acc | route domain acc | routed domain counts | route reasons |",
                "|---|---:|---:|---:|---|---|",
            ]
        )
        for group_name, payload in route_groups.items():
            lines.append(
                f"| {group_name} | {payload['n']} | {fmt(payload.get('global_domain_accuracy'))} | "
                f"{fmt(payload.get('route_domain_accuracy'))} | `{payload.get('routed_domain_counts')}` | "
                f"`{payload.get('route_reason_counts')}` |"
            )
    lines.extend(
        [
            "",
            "## Proposal Diagnostics",
            "",
            f"- mean best-box IoU: `{fmt(prop['mean_best_box_iou'])}`",
            f"- proposal recall IoU@0.3: `{fmt(prop['proposal_recall_iou_0_3'])}`",
            f"- proposal recall IoU@0.5: `{fmt(prop['proposal_recall_iou_0_5'])}`",
            f"- failure reasons: `{prop['failure_reason_counts']}`",
            "",
            "## GT-Bbox Refinement Reference",
            "",
            "- Existing frozen GT-bbox-conditioned refinement: `0.8394 IoU / 0.9005 F1`.",
            "- This is reported only as a coarse-box-known refinement ablation, not merged with image-only metrics.",
        ]
    )
    return "\n".join(lines) + "\n"


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


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.policy_only:
        return run_policy_only(args)

    dev_cache = load_jsonl(args.dev_pipeline_records)
    eval_cache = load_jsonl(args.eval_pipeline_records)
    dev_eval = load_jsonl(args.dev_eval_manifest)
    eval_rows = load_jsonl(args.eval_manifest)

    policy_source = "loaded"
    policy_search = None
    if args.locked_policy and args.locked_policy.exists():
        payload = load_json(args.locked_policy)
        policy = payload.get("locked_policy") or payload.get("policy") or payload
    elif args.skip_search:
        policy_source = "default"
        policy = dict(DEFAULT_POLICY)
    else:
        policy_source = "tuned_on_dev"
        policy_search = search_policy(dev_cache, dev_eval, args)
        policy = policy_search["locked_policy"]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    dev_results, dev_summary = evaluate_dataset("dev", dev_cache, dev_eval, policy, args.output_dir / "dev")
    eval_results, eval_summary = evaluate_dataset("eval", eval_cache, eval_rows, policy, args.output_dir / "eval")
    dev_summary = summarize_all(dev_results, args.bootstrap_samples, args.bootstrap_seed + 17)
    eval_summary = summarize_all(eval_results, args.bootstrap_samples, args.bootstrap_seed + 31)

    all_results = dev_results + eval_results
    results_path = args.output_dir / "end2end_results.jsonl"
    with results_path.open("w", encoding="utf-8") as f:
        for row in all_results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "name": args.output_dir.name,
        "boundary": "image-only end-to-end localization; GT masks/bboxes used only by this evaluator for scoring",
        "dev_pipeline_records": str(args.dev_pipeline_records),
        "eval_pipeline_records": str(args.eval_pipeline_records),
        "dev_eval_manifest": str(args.dev_eval_manifest),
        "eval_manifest": str(args.eval_manifest),
        "policy_source": policy_source,
        "locked_policy": policy,
        "locked_policy_hash": policy_hash(policy),
        "policy_search": policy_search,
        "dev_summary": dev_summary,
        "eval_summary": eval_summary,
        "results": str(results_path),
        "bootstrap_samples": args.bootstrap_samples,
    }
    summary_json = args.output_dir / "end2end_summary.json"
    summary_md = args.output_dir / "end2end_summary.md"
    policy_json = args.output_dir / "policy.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_md.write_text(render_md(summary), encoding="utf-8")
    policy_json.write_text(
        json.dumps(
            {
                "locked_policy": policy,
                "locked_policy_hash": policy_hash(policy),
                "policy_source": policy_source,
                "policy_search": policy_search,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("wrote", results_path)
    print("wrote", summary_json)
    print("wrote", summary_md)
    print("wrote", policy_json)
    return summary


def run_policy_only(args: argparse.Namespace) -> dict[str, Any]:
    dev_cache = load_jsonl(args.dev_pipeline_records)
    dev_eval = load_jsonl(args.dev_eval_manifest)

    policy_source = "loaded"
    policy_search = None
    if args.locked_policy and args.locked_policy.exists():
        payload = load_json(args.locked_policy)
        policy = payload.get("locked_policy") or payload.get("policy") or payload
    elif args.skip_search:
        policy_source = "default"
        policy = dict(DEFAULT_POLICY)
    else:
        policy_source = "tuned_on_dev"
        policy_search = search_policy(dev_cache, dev_eval, args)
        policy = policy_search["locked_policy"]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    dev_results, dev_summary = evaluate_dataset("dev", dev_cache, dev_eval, policy, args.output_dir / "dev")
    dev_summary = summarize_all(dev_results, args.bootstrap_samples, args.bootstrap_seed + 17)

    results_path = args.output_dir / "dev_policy_results.jsonl"
    with results_path.open("w", encoding="utf-8") as f:
        for row in dev_results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "name": args.output_dir.name,
        "boundary": "dev-only policy lock; GT masks/bboxes used only by this evaluator for scoring",
        "dev_pipeline_records": str(args.dev_pipeline_records),
        "dev_eval_manifest": str(args.dev_eval_manifest),
        "policy_source": policy_source,
        "locked_policy": policy,
        "locked_policy_hash": policy_hash(policy),
        "policy_search": policy_search,
        "dev_summary": dev_summary,
        "results": str(results_path),
        "bootstrap_samples": args.bootstrap_samples,
    }
    summary_json = args.output_dir / "dev_policy_summary.json"
    policy_json = args.output_dir / "policy.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    policy_json.write_text(
        json.dumps(
            {
                "locked_policy": policy,
                "locked_policy_hash": policy_hash(policy),
                "policy_source": policy_source,
                "policy_search": policy_search,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("wrote", results_path)
    print("wrote", summary_json)
    print("wrote", policy_json)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune/evaluate image-only end-to-end localization policy.")
    parser.add_argument("--dev-pipeline-records", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev_pipeline/pipeline_records.jsonl"))
    parser.add_argument("--eval-pipeline-records", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p600_final_pipeline/pipeline_records.jsonl"))
    parser.add_argument("--dev-eval-manifest", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev/eval_manifest.jsonl"))
    parser.add_argument("--eval-manifest", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p600_final/eval_manifest.jsonl"))
    parser.add_argument("--locked-policy", type=Path)
    parser.add_argument("--skip-search", action="store_true")
    parser.add_argument("--policy-only", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/end2end_region_eval/end2end_region_eval_p600_final_end2end"))
    parser.add_argument("--routing-modes", default="global_domain")
    parser.add_argument("--proposal-score-thresholds", default="0.5,0.7,1.0")
    parser.add_argument("--photoshop-patch-thresholds", default="0.5,0.7,1.0")
    parser.add_argument("--aigc-patch-thresholds", default="0.5,0.7,1.0")
    parser.add_argument("--face-score-thresholds", default="0.5,1.0")
    parser.add_argument("--max-boxes-per-image-values", default="1,2,3")
    parser.add_argument("--nms-iou-thresholds", default="0.3,0.5,0.7")
    parser.add_argument("--sam-score-thresholds", default="0,0.25,0.5,0.75,0.9,0.95,1.0")
    parser.add_argument("--sam-score-start", type=float, default=0.0)
    parser.add_argument("--sam-score-end", type=float, default=1.0)
    parser.add_argument("--sam-score-step", type=float, default=0.25)
    parser.add_argument("--allow-sam-score-threshold-gt-1", action="store_true")
    parser.add_argument("--sam-area-min-values", default="0.005,0.01,0.02,0.05")
    parser.add_argument("--sam-area-max-values", default="0.5,0.8,1.0,1.2")
    parser.add_argument("--max-auth-fpr", type=float, default=0.10)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260719)
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
