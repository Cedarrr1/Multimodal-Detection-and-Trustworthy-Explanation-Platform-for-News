#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from build_end2end_region_eval import DEFAULT_EXCLUDES, candidate_sha256, load_exclusions
from build_stage1_domain_boost_json import (
    Candidate,
    bbox_from_mask,
    close_archives,
    copy_archive_member,
    discover_casia,
    discover_faceapp,
    discover_ffhq,
    discover_sd_inpaint,
    read_binary_mask,
    safe_name,
    stable_seed,
)


PROMPT = (
    "<image>\n"
    "<image>\n"
    "The first image is the full image and the second image is a candidate crop from it. "
    "Decide whether the crop itself contains manipulated pixels from the full image. "
    "Return only valid compact JSON with exactly these keys: crop_tampered, tamper_domain, and crop_role. "
    'Use crop_tampered true or false; use tamper_domain "none", "photoshop", "deepfake", or "aigc_inpaint".'
)

VALID_ROLES = {"positive_region", "hard_negative", "adjacent_distractor", "authentic_negative"}


def box_area(box: list[int]) -> int:
    return max(0, int(box[2]) - int(box[0])) * max(0, int(box[3]) - int(box[1]))


def clamp_box(box: list[int], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(width - 1, x0))
    y0 = max(0, min(height - 1, y0))
    x1 = max(x0 + 1, min(width, x1))
    y1 = max(y0 + 1, min(height, y1))
    return [x0, y0, x1, y1]


def expand_box(box: list[int], width: int, height: int, scale: float) -> list[int]:
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    bw = max(1.0, (x1 - x0) * scale)
    bh = max(1.0, (y1 - y0) * scale)
    return clamp_box([cx - bw / 2.0, cy - bh / 2.0, cx + bw / 2.0, cy + bh / 2.0], width, height)


def mask_overlap_ratio(mask: np.ndarray, box: list[int]) -> tuple[float, float]:
    x0, y0, x1, y1 = box
    gt = int(mask.sum())
    if gt == 0:
        return 0.0, 0.0
    covered = int(mask[y0:y1, x0:x1].sum())
    crop_area = max(1, box_area(box))
    return covered / float(gt), covered / float(crop_area)


def grid_boxes(width: int, height: int, scales: list[float]) -> list[list[int]]:
    short = min(width, height)
    boxes: list[list[int]] = []
    for scale in scales:
        side = max(8, min(width, height, int(round(short * scale))))
        stride = max(1, side // 2)
        xs = list(range(0, max(1, width - side + 1), stride))
        ys = list(range(0, max(1, height - side + 1), stride))
        if not xs or xs[-1] != width - side:
            xs.append(max(0, width - side))
        if not ys or ys[-1] != height - side:
            ys.append(max(0, height - side))
        for y0 in sorted(set(ys)):
            for x0 in sorted(set(xs)):
                boxes.append([x0, y0, x0 + side, y0 + side])
    return boxes


def parse_scales(text: str) -> list[float]:
    values = [float(item.strip()) for item in text.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one grid scale is required")
    for value in values:
        if value <= 0:
            raise ValueError(f"grid scale must be positive: {value}")
    return values


def candidate_seed(seed: int, candidate: Candidate, role: str) -> int:
    digest = hashlib.sha256(f"{seed}:{candidate.source}:{candidate.id}:{candidate.image_member}:{role}".encode("utf-8")).hexdigest()
    return seed + int(digest[:8], 16)


def hard_negative_box(mask: np.ndarray, width: int, height: int) -> list[int]:
    scored = []
    for box in grid_boxes(width, height, [0.35, 0.50, 0.65]):
        gt_coverage, crop_ratio = mask_overlap_ratio(mask, box)
        scored.append((gt_coverage, crop_ratio, box_area(box), box))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    return list(scored[0][3])


def adjacent_box(mask: np.ndarray, gt_box: list[int], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = gt_box
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    candidates = [
        [x0 - bw, y0, x1 - bw, y1],
        [x0 + bw, y0, x1 + bw, y1],
        [x0, y0 - bh, x1, y1 - bh],
        [x0, y0 + bh, x1, y1 + bh],
        [x0 - bw // 2, y0 - bh // 2, x1 - bw // 2, y1 - bh // 2],
        [x0 + bw // 2, y0 + bh // 2, x1 + bw // 2, y1 + bh // 2],
    ]
    scored = []
    for raw in candidates:
        box = clamp_box(raw, width, height)
        gt_coverage, crop_ratio = mask_overlap_ratio(mask, box)
        scored.append((gt_coverage <= 0.15, gt_coverage, crop_ratio, box))
    scored.sort(key=lambda item: (not item[0], item[1], item[2]))
    return list(scored[0][3])


def authentic_boxes(candidate: Candidate, width: int, height: int, seed: int) -> list[list[int]]:
    boxes = grid_boxes(width, height, [0.35, 0.50, 0.65])
    rng = random.Random(candidate_seed(seed, candidate, "authentic_negative"))
    rng.shuffle(boxes)
    return boxes[:3]


def authentic_grid_boxes(candidate: Candidate, width: int, height: int, seed: int, scales: list[float], count: int) -> list[list[int]]:
    boxes = grid_boxes(width, height, scales)
    rng = random.Random(candidate_seed(seed, candidate, "authentic_grid_negative"))
    rng.shuffle(boxes)
    return boxes[:count]


def make_crop(image_path: Path, crop_path: Path, box: list[int]) -> None:
    crop_path.parent.mkdir(parents=True, exist_ok=True)
    if crop_path.exists():
        return
    with Image.open(image_path) as image:
        image.convert("RGB").crop(tuple(box)).save(crop_path, quality=95)


def output_image_rel(candidate: Candidate) -> Path:
    suffix = Path(candidate.image_member).suffix.lower()
    return Path("images") / candidate.source_domain / candidate.source / candidate.label / f"{safe_name(candidate.id)}{suffix}"


def output_mask_rel(candidate: Candidate) -> Path:
    return Path("masks") / candidate.source_domain / candidate.source / f"{safe_name(candidate.id)}.png"


def output_crop_rel(candidate: Candidate, role: str, index: int) -> Path:
    return Path("crops") / candidate.source_domain / candidate.source / candidate.label / f"{safe_name(candidate.id)}_{role}_{index}.jpg"


def discover_groups(args: argparse.Namespace) -> dict[str, list[Candidate]]:
    casia = discover_casia(args.casia_zip)
    faceapp = discover_faceapp(args.faceapp_zip, args.faceapp_split)
    ffhq = discover_ffhq(args.ffhq_zip, args.ffhq_split)
    sd = discover_sd_inpaint(args.sd_train_tar, "train") + discover_sd_inpaint(args.sd_eval_tar, "eval")
    return {
        "photoshop_tampered": [c for c in casia if c.label == "tampered" and c.mask_member],
        "photoshop_authentic": [c for c in casia if c.label == "authentic"],
        "deepfake_tampered": [c for c in faceapp if c.label == "tampered" and c.mask_member],
        "deepfake_authentic": [c for c in ffhq if c.label == "authentic"],
        "aigc_tampered": [c for c in sd if c.label == "tampered" and c.mask_member],
        "aigc_authentic": [c for c in sd if c.label == "authentic"],
    }


def candidate_keys(candidate: Candidate) -> set[str]:
    keys = {candidate.id, f"{candidate.source_path}::{candidate.image_member}"}
    keys.add(candidate.image_member)
    keys.add(Path(candidate.image_member).name)
    keys.add(Path(candidate.image_member).stem)
    return {key for key in keys if key}


def sample_candidates(
    name: str,
    candidates: list[Candidate],
    count: int,
    seed: int,
    excluded_keys: set[str],
    excluded_hashes: set[str],
    used_hashes: set[str],
) -> tuple[list[tuple[Candidate, str]], dict[str, Any]]:
    rng = random.Random(stable_seed(seed, name))
    shuffled = list(candidates)
    rng.shuffle(shuffled)
    selected: list[tuple[Candidate, str]] = []
    excluded_by_key = 0
    excluded_by_sha = 0
    duplicate_sha = 0
    for candidate in shuffled:
        if candidate_keys(candidate) & excluded_keys:
            excluded_by_key += 1
            continue
        digest = candidate_sha256(candidate)
        if digest in excluded_hashes:
            excluded_by_sha += 1
            continue
        if digest in used_hashes:
            duplicate_sha += 1
            continue
        selected.append((candidate, digest))
        used_hashes.add(digest)
        if len(selected) >= count:
            break
    if len(selected) < count:
        raise RuntimeError(f"{name}: requested {count}, selected {len(selected)}")
    return selected, {
        "available": len(candidates),
        "excluded_by_source_key": excluded_by_key,
        "excluded_by_sha256": excluded_by_sha,
        "duplicate_sha256_in_output": duplicate_sha,
        "selected": len(selected),
        "selected_from_excluded_fallback": 0,
    }


def target(crop_tampered: bool, tamper_domain: str, role: str) -> dict[str, Any]:
    if role not in VALID_ROLES:
        raise ValueError(f"bad crop role: {role}")
    return {
        "crop_tampered": bool(crop_tampered),
        "tamper_domain": tamper_domain if crop_tampered else "none",
        "crop_role": role,
    }


def prepare_candidate(candidate: Candidate, output_root: Path) -> dict[str, Any]:
    image_rel = output_image_rel(candidate)
    image_path = output_root / image_rel
    copy_archive_member(candidate, candidate.image_member, image_path)
    with Image.open(image_path) as image:
        width, height = image.size
    mask_rel = None
    mask_path = None
    gt_mask = None
    gt_bbox = None
    if candidate.label == "tampered":
        if not candidate.mask_member:
            raise RuntimeError(f"missing mask for {candidate.source}:{candidate.image_member}")
        mask_rel = output_mask_rel(candidate)
        mask_path = output_root / mask_rel
        copy_archive_member(candidate, candidate.mask_member, mask_path)
        gt_mask = read_binary_mask(mask_path, (width, height))
        gt_bbox = bbox_from_mask(gt_mask)
    return {
        "image_rel": image_rel,
        "image_path": image_path,
        "mask_rel": mask_rel,
        "mask_path": mask_path,
        "width": width,
        "height": height,
        "gt_mask": gt_mask,
        "gt_bbox": gt_bbox,
    }


def crop_specs_focused(candidate: Candidate, prepared: dict[str, Any], seed: int) -> list[tuple[str, list[int], bool]]:
    width = int(prepared["width"])
    height = int(prepared["height"])
    if candidate.label != "tampered":
        return [("authentic_negative", box, False) for box in authentic_boxes(candidate, width, height, seed)]
    mask = prepared["gt_mask"]
    gt_bbox = prepared["gt_bbox"]
    assert mask is not None and gt_bbox is not None
    positive = expand_box(gt_bbox, width, height, 1.10)
    gt_coverage, crop_ratio = mask_overlap_ratio(mask, positive)
    if gt_coverage < 0.70 or crop_ratio < 0.03:
        positive = clamp_box(gt_bbox, width, height)
    return [
        ("positive_region", positive, True),
        ("hard_negative", hard_negative_box(mask, width, height), False),
        ("adjacent_distractor", adjacent_box(mask, gt_bbox, width, height), False),
    ]


def take_ranked(
    rows: list[tuple[float, float, int, list[int]]],
    count: int,
    used: set[tuple[int, int, int, int]],
) -> list[list[int]]:
    out: list[list[int]] = []
    for _gt_coverage, _crop_ratio, _area, box in rows:
        key = tuple(int(v) for v in box)
        if key in used:
            continue
        used.add(key)
        out.append(list(box))
        if len(out) >= count:
            break
    return out


def crop_specs_sliding(candidate: Candidate, prepared: dict[str, Any], args: argparse.Namespace) -> list[tuple[str, list[int], bool]]:
    width = int(prepared["width"])
    height = int(prepared["height"])
    scales = parse_scales(args.grid_scales)
    if candidate.label != "tampered":
        boxes = authentic_grid_boxes(candidate, width, height, args.seed, scales, args.authentic_crops_per_image)
        return [("authentic_negative", box, False) for box in boxes]

    mask = prepared["gt_mask"]
    gt_bbox = prepared["gt_bbox"]
    assert mask is not None and gt_bbox is not None
    scored: list[tuple[float, float, int, list[int]]] = []
    for box in grid_boxes(width, height, scales):
        gt_coverage, crop_ratio = mask_overlap_ratio(mask, box)
        scored.append((gt_coverage, crop_ratio, box_area(box), box))

    positives = [
        row
        for row in scored
        if row[0] >= args.positive_min_gt_coverage and row[1] >= args.positive_min_crop_ratio
    ]
    positives.sort(key=lambda item: (item[0], item[1], -item[2]), reverse=True)
    if not positives:
        positives = sorted(scored, key=lambda item: (item[0], item[1], -item[2]), reverse=True)[:1]

    hard_negatives = [
        row
        for row in scored
        if row[0] <= args.hard_negative_max_gt_coverage and row[1] <= args.hard_negative_max_crop_ratio
    ]
    hard_negatives.sort(key=lambda item: (item[0], item[1], -item[2]), reverse=True)

    adjacent = [
        row
        for row in scored
        if args.adjacent_min_gt_coverage <= row[0] <= args.adjacent_max_gt_coverage
        and row[1] <= args.adjacent_max_crop_ratio
    ]
    adjacent.sort(key=lambda item: (item[0], item[1], -item[2]), reverse=True)

    used: set[tuple[int, int, int, int]] = set()
    specs: list[tuple[str, list[int], bool]] = []
    for box in take_ranked(positives, args.positive_per_tampered, used):
        specs.append(("positive_region", box, True))
    for box in take_ranked(hard_negatives, args.hard_negative_per_tampered, used):
        specs.append(("hard_negative", box, False))
    for box in take_ranked(adjacent, args.adjacent_per_tampered, used):
        specs.append(("adjacent_distractor", box, False))
    return specs


def crop_specs(candidate: Candidate, prepared: dict[str, Any], args: argparse.Namespace) -> list[tuple[str, list[int], bool]]:
    if args.crop_mode == "focused":
        return crop_specs_focused(candidate, prepared, args.seed)
    if args.crop_mode == "sliding":
        return crop_specs_sliding(candidate, prepared, args)
    raise ValueError(f"unsupported crop mode: {args.crop_mode}")


def write_dataset(args: argparse.Namespace) -> dict[str, Any]:
    excluded_keys, excluded_hashes, exclusion_stats = load_exclusions(args.exclude_manifest)
    groups = discover_groups(args)
    quotas = {
        "photoshop_tampered": args.tampered_per_domain,
        "photoshop_authentic": args.authentic_per_domain,
        "deepfake_tampered": args.tampered_per_domain,
        "deepfake_authentic": args.authentic_per_domain,
        "aigc_tampered": args.tampered_per_domain,
        "aigc_authentic": args.authentic_per_domain,
    }
    selected: list[tuple[str, Candidate, str]] = []
    stats: dict[str, Any] = {}
    used_hashes: set[str] = set()
    for name in sorted(groups):
        chosen, group_stats = sample_candidates(name, groups[name], quotas[name], args.seed, excluded_keys, excluded_hashes, used_hashes)
        selected.extend((name, candidate, digest) for candidate, digest in chosen)
        stats[name] = group_stats

    args.output_root.mkdir(parents=True, exist_ok=True)
    sft_path = args.output_root / "llamafactory_qwen_vl_sft.jsonl"
    manifest_path = args.output_root / "manifest.jsonl"
    meta_path = args.output_root / "dataset_meta.json"

    role_counts: dict[str, int] = defaultdict(int)
    total_rows = 0
    with sft_path.open("w", encoding="utf-8") as sf, manifest_path.open("w", encoding="utf-8") as mf:
        for group_name, candidate, digest in selected:
            prepared = prepare_candidate(candidate, args.output_root)
            specs = crop_specs(candidate, prepared, args)
            for idx, (role, box, crop_tampered) in enumerate(specs):
                crop_rel = output_crop_rel(candidate, role, idx)
                crop_path = args.output_root / crop_rel
                make_crop(prepared["image_path"], crop_path, box)
                payload = target(crop_tampered, candidate.tamper_domain, role)
                row_id = safe_name(f"{candidate.source}_{candidate.source_split}_{candidate.label}_{candidate.id}_{role}_{idx}")
                sft = {
                    "id": row_id,
                    "images": [str(prepared["image_path"]), str(crop_path)],
                    "messages": [
                        {"role": "user", "content": PROMPT},
                        {"role": "assistant", "content": json.dumps(payload, ensure_ascii=False)},
                    ],
                }
                manifest = {
                    "id": row_id,
                    "source_group": group_name,
                    "source": candidate.source,
                    "source_split": candidate.source_split,
                    "source_domain": candidate.source_domain,
                    "label": candidate.label,
                    "tamper_domain": candidate.tamper_domain,
                    "image_member": candidate.image_member,
                    "mask_member": candidate.mask_member,
                    "sha256": digest,
                    "image": str(prepared["image_rel"]),
                    "resolved_image": str(prepared["image_path"]),
                    "crop": str(crop_rel),
                    "resolved_crop": str(crop_path),
                    "crop_box_xyxy": box,
                    "crop_tampered": crop_tampered,
                    "crop_role": role,
                    "target": payload,
                }
                sf.write(json.dumps(sft, ensure_ascii=False) + "\n")
                mf.write(json.dumps(manifest, ensure_ascii=False) + "\n")
                role_counts[role] += 1
                total_rows += 1

    meta = {
        "name": args.dataset_name,
        "output_root": str(args.output_root),
        "seed": args.seed,
        "tampered_per_domain": args.tampered_per_domain,
        "authentic_per_domain": args.authentic_per_domain,
        "crop_mode": args.crop_mode,
        "grid_scales": parse_scales(args.grid_scales),
        "positive_per_tampered": args.positive_per_tampered,
        "hard_negative_per_tampered": args.hard_negative_per_tampered,
        "adjacent_per_tampered": args.adjacent_per_tampered,
        "authentic_crops_per_image": args.authentic_crops_per_image,
        "positive_min_gt_coverage": args.positive_min_gt_coverage,
        "positive_min_crop_ratio": args.positive_min_crop_ratio,
        "hard_negative_max_gt_coverage": args.hard_negative_max_gt_coverage,
        "hard_negative_max_crop_ratio": args.hard_negative_max_crop_ratio,
        "adjacent_min_gt_coverage": args.adjacent_min_gt_coverage,
        "adjacent_max_gt_coverage": args.adjacent_max_gt_coverage,
        "adjacent_max_crop_ratio": args.adjacent_max_crop_ratio,
        "selected_source_images": len(selected),
        "total_sft_rows": total_rows,
        "role_counts": dict(sorted(role_counts.items())),
        "group_stats": stats,
        "excluded_manifests": [str(path) for path in args.exclude_manifest],
        "exclusion_stats": exclusion_stats,
        "supervision": "full image + candidate crop -> crop_tampered/domain/role; no GT coordinates in target",
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_dataset(sft_path, manifest_path)
    return meta


def validate_dataset(sft_path: Path, manifest_path: Path) -> None:
    sft_rows = [json.loads(line) for line in sft_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest_rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(sft_rows) != len(manifest_rows):
        raise ValueError("SFT and manifest row counts differ")
    for idx, row in enumerate(sft_rows):
        if len(row.get("images", [])) != 2:
            raise ValueError(f"row {idx}: expected two images")
        for image in row["images"]:
            if not Path(image).exists():
                raise FileNotFoundError(image)
        prompt = row["messages"][0]["content"]
        if str(prompt).count("<image>") != 2:
            raise ValueError(f"row {idx}: prompt must contain two image placeholders")
        target_obj = json.loads(row["messages"][1]["content"])
        if set(target_obj) != {"crop_tampered", "tamper_domain", "crop_role"}:
            raise ValueError(f"row {idx}: bad target keys")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build full-domain crop proposal SFT data for image-only localization.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/end2end_region_proposal_json"))
    parser.add_argument("--dataset-name", default="end2end_region_proposal_json")
    parser.add_argument("--seed", type=int, default=20260718)
    parser.add_argument("--tampered-per-domain", type=int, default=300)
    parser.add_argument("--authentic-per-domain", type=int, default=100)
    parser.add_argument("--crop-mode", choices=["focused", "sliding"], default="focused")
    parser.add_argument("--grid-scales", default="0.35,0.50,0.65")
    parser.add_argument("--positive-per-tampered", type=int, default=3)
    parser.add_argument("--hard-negative-per-tampered", type=int, default=3)
    parser.add_argument("--adjacent-per-tampered", type=int, default=2)
    parser.add_argument("--authentic-crops-per-image", type=int, default=6)
    parser.add_argument("--positive-min-gt-coverage", type=float, default=0.35)
    parser.add_argument("--positive-min-crop-ratio", type=float, default=0.02)
    parser.add_argument("--hard-negative-max-gt-coverage", type=float, default=0.02)
    parser.add_argument("--hard-negative-max-crop-ratio", type=float, default=0.005)
    parser.add_argument("--adjacent-min-gt-coverage", type=float, default=0.02)
    parser.add_argument("--adjacent-max-gt-coverage", type=float, default=0.25)
    parser.add_argument("--adjacent-max-crop-ratio", type=float, default=0.02)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--ffhq-zip", type=Path, default=Path("dataset/deepfake/ffhq.zip"))
    parser.add_argument("--ffhq-split", default="train")
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--faceapp-split", default="test")
    parser.add_argument("--sd-train-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/train.tar"))
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument(
        "--exclude-manifest",
        type=Path,
        action="append",
        default=DEFAULT_EXCLUDES
        + [
            Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev/eval_manifest.jsonl"),
            Path("artifacts/end2end_region_eval/end2end_region_eval_p600_final/eval_manifest.jsonl"),
        ],
    )
    args = parser.parse_args()
    if args.tampered_per_domain < 1 or args.authentic_per_domain < 1:
        raise ValueError("sample counts must be positive")
    for name in ["positive_per_tampered", "hard_negative_per_tampered", "adjacent_per_tampered", "authentic_crops_per_image"]:
        if getattr(args, name) < 0:
            raise ValueError(f"--{name.replace('_', '-')} must be non-negative")
    parse_scales(args.grid_scales)
    return args


def main() -> None:
    args = parse_args()
    try:
        meta = write_dataset(args)
    finally:
        close_archives()
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
