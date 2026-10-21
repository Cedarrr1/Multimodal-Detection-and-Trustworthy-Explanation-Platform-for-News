#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
DEFAULT_SEED = 20260705


@dataclass(frozen=True)
class RegionPair:
    domain: str
    source: str
    source_archive: Path
    image_member: str
    mask_member: str
    sample_key: str


def is_image_member(name: str) -> bool:
    return not name.endswith("/") and Path(name).suffix.lower() in IMAGE_EXTS


def read_zip_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(name for name in zf.namelist() if is_image_member(name))


def read_tar_members(path: Path) -> list[str]:
    with tarfile.open(path) as tf:
        return sorted(member.name for member in tf.getmembers() if member.isfile() and is_image_member(member.name))


def trailing_numeric_id(stem: str) -> str:
    match = re.search(r"_(\d+)$", stem)
    return match.group(1) if match else stem


def discover_casia(casia_zip: Path) -> list[RegionPair]:
    if not casia_zip.exists():
        raise FileNotFoundError(casia_zip)
    images: dict[str, str] = {}
    masks: dict[str, str] = {}
    for member in read_zip_members(casia_zip):
        if member.startswith("CASIA2/Tp/"):
            images[trailing_numeric_id(Path(member).stem)] = member
        elif member.startswith("CASIA2/CASIA 2 Groundtruth/") and member.endswith("_gt.png"):
            stem = Path(member).stem
            if stem.endswith("_gt"):
                stem = stem[:-3]
            masks[trailing_numeric_id(stem)] = member
    shared = sorted(set(images) & set(masks))
    return [
        RegionPair(
            domain="photoshop",
            source="CASIA",
            source_archive=casia_zip,
            image_member=images[key],
            mask_member=masks[key],
            sample_key=key,
        )
        for key in shared
    ]


def discover_faceapp(faceapp_zip: Path) -> list[RegionPair]:
    if not faceapp_zip.exists():
        raise FileNotFoundError(faceapp_zip)
    images: dict[str, str] = {}
    masks: dict[str, str] = {}
    for member in read_zip_members(faceapp_zip):
        if member.startswith("faceapp/test/"):
            images[Path(member).name] = member
        elif member.startswith("faceapp/test_mask/"):
            masks[Path(member).name] = member
    shared = sorted(set(images) & set(masks))
    return [
        RegionPair(
            domain="deepfake",
            source="FaceApp",
            source_archive=faceapp_zip,
            image_member=images[key],
            mask_member=masks[key],
            sample_key=Path(key).stem,
        )
        for key in shared
    ]


def discover_sd_inpaint(sd_eval_tar: Path) -> list[RegionPair]:
    if not sd_eval_tar.exists():
        raise FileNotFoundError(sd_eval_tar)
    images: dict[str, str] = {}
    masks: dict[str, str] = {}
    for member in read_tar_members(sd_eval_tar):
        if member.startswith("eval/Tp/image/"):
            images[Path(member).stem] = member
        elif member.startswith("eval/Tp/mask/"):
            masks[Path(member).stem] = member
    shared = sorted(set(images) & set(masks))
    return [
        RegionPair(
            domain="aigc_editing",
            source="SD-inpaint",
            source_archive=sd_eval_tar,
            image_member=images[key],
            mask_member=masks[key],
            sample_key=key,
        )
        for key in shared
    ]


def sample_pairs(pairs: list[RegionPair], per_domain: int, seed: int) -> list[RegionPair]:
    if len(pairs) < per_domain:
        raise ValueError(f"requested {per_domain} samples from {pairs[0].source if pairs else 'empty source'}, found {len(pairs)}")
    rng = random.Random(seed)
    shuffled = list(pairs)
    rng.shuffle(shuffled)
    return shuffled[:per_domain]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def path_keys(value: Any) -> set[str]:
    if value is None:
        return set()
    text = str(value).replace("\\", "/")
    path = Path(text)
    keys = {text, path.name, path.stem}
    if "/" in text:
        keys.add(text.split("/")[-1])
    return {key for key in keys if key}


def manifest_exclusion_keys(paths: list[Path]) -> set[str]:
    keys: set[str] = set()
    fields = ["id", "image", "resolved_image", "archive_member", "image_member", "sample_key"]
    for path in paths:
        for row in load_jsonl(path):
            for field in fields:
                keys.update(path_keys(row.get(field)))
    return keys


def pair_keys(pair: RegionPair) -> set[str]:
    keys = {pair.sample_key}
    keys.update(path_keys(pair.image_member))
    return {key for key in keys if key}


def is_excluded(pair: RegionPair, exclusion_keys: set[str]) -> bool:
    return bool(pair_keys(pair) & exclusion_keys)


def sample_pairs_with_exclusion(
    pairs: list[RegionPair],
    per_domain: int,
    seed: int,
    exclusion_keys: set[str],
) -> tuple[list[RegionPair], dict[str, Any]]:
    rng = random.Random(seed)
    clean = [pair for pair in pairs if not is_excluded(pair, exclusion_keys)]
    excluded = [pair for pair in pairs if is_excluded(pair, exclusion_keys)]
    rng.shuffle(clean)
    rng.shuffle(excluded)
    selected = clean[:per_domain]
    fallback_used = 0
    if len(selected) < per_domain:
        need = per_domain - len(selected)
        selected.extend(excluded[:need])
        fallback_used = min(need, len(excluded))
    if len(selected) < per_domain:
        raise ValueError(f"requested {per_domain} samples from {pairs[0].source if pairs else 'empty source'}, found {len(selected)} after fallback")
    return selected, {
        "available": len(pairs),
        "excluded_by_manifest": len(excluded),
        "available_after_exclusion": len(clean),
        "selected": len(selected),
        "selected_from_excluded_fallback": fallback_used,
    }


def copy_archive_member(archive_path: Path, member: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive_path) as zf:
            with zf.open(member) as src, output_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    elif archive_path.suffix.lower() == ".tar":
        with tarfile.open(archive_path) as tf:
            src = tf.extractfile(member)
            if src is None:
                raise FileNotFoundError(member)
            with src, output_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    else:
        raise ValueError(f"unsupported archive type: {archive_path}")


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


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


def rel_output_paths(pair: RegionPair, domain_index: int) -> tuple[Path, Path]:
    suffix = Path(pair.image_member).suffix.lower()
    sid = safe_id(f"{domain_index:03d}_{pair.source}_{pair.sample_key}")
    image_rel = Path("images") / pair.domain / pair.source / f"{sid}{suffix}"
    mask_rel = Path("masks") / pair.domain / pair.source / f"{sid}.png"
    return image_rel, mask_rel


def build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    dataset_name = args.dataset_name or args.output_root.name
    exclusion_keys = manifest_exclusion_keys(args.exclude_manifest)
    discoveries = {
        "photoshop": discover_casia(args.casia_zip),
        "deepfake": discover_faceapp(args.faceapp_zip),
        "aigc_editing": discover_sd_inpaint(args.sd_eval_tar),
    }
    selected: list[RegionPair] = []
    group_stats: dict[str, Any] = {}
    for offset, (domain, pairs) in enumerate(sorted(discoveries.items())):
        chosen, stats = sample_pairs_with_exclusion(pairs, args.per_domain, args.seed + offset * 997, exclusion_keys)
        selected.extend(chosen)
        group_stats[domain] = stats

    args.output_root.mkdir(parents=True, exist_ok=True)
    samples_path = args.output_root / "samples.jsonl"
    manifest_path = args.output_root / "manifest.jsonl"
    meta_path = args.output_root / "dataset_meta.json"

    domain_counts: dict[str, int] = {domain: 0 for domain in discoveries}
    rows: list[dict[str, Any]] = []
    for pair in selected:
        domain_counts[pair.domain] += 1
        image_rel, mask_rel = rel_output_paths(pair, domain_counts[pair.domain])
        image_path = args.output_root / image_rel
        mask_path = args.output_root / mask_rel
        copy_archive_member(pair.source_archive, pair.image_member, image_path)
        copy_archive_member(pair.source_archive, pair.mask_member, mask_path)

        width, height = image_size(image_path)
        mask = read_binary_mask(mask_path, (width, height))
        bbox = bbox_from_mask(mask)
        mask_area = int(mask.sum())
        sample_id = f"{dataset_name}_{pair.domain}_{domain_counts[pair.domain]:03d}"
        rows.append(
            {
                "id": sample_id,
                "domain": pair.domain,
                "source": pair.source,
                "source_dataset": pair.source,
                "split": "tampered",
                "image": str(image_rel),
                "mask": str(mask_rel),
                "gt_mask": str(mask_rel),
                "resolved_image": str(image_path),
                "resolved_mask": str(mask_path),
                "resolved_gt_mask": str(mask_path),
                "source_archive": str(pair.source_archive),
                "image_member": pair.image_member,
                "mask_member": pair.mask_member,
                "sample_key": pair.sample_key,
                "image_width": width,
                "image_height": height,
                "bbox_xyxy": bbox,
                "gt_bbox": bbox,
                "bbox_format": "xyxy_half_open",
                "mask_area_pixels": mask_area,
                "mask_area_ratio": mask_area / float(width * height),
            }
        )

    for output_path in [samples_path, manifest_path]:
        with output_path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    meta = {
        "name": dataset_name,
        "output_root": str(args.output_root),
        "samples": str(samples_path),
        "manifest": str(manifest_path),
        "seed": args.seed,
        "per_domain": args.per_domain,
        "total": len(rows),
        "exclude_manifests": [str(path) for path in args.exclude_manifest],
        "exclusion_key_count": len(exclusion_keys),
        "group_stats": group_stats,
        "bbox_source": "computed from GT mask",
        "evaluation_boundary": "bbox-prompt conditioned mask refinement / grounding evaluation; not automatic forged-region discovery",
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_manifest(manifest_path, args.per_domain)
    return meta


def validate_manifest(manifest_path: Path, per_domain: int) -> None:
    rows = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    expected_domains = {"photoshop", "deepfake", "aigc_editing"}
    counts = {domain: 0 for domain in expected_domains}
    for row in rows:
        domain = row["domain"]
        if domain not in expected_domains:
            raise ValueError(f"unexpected domain: {domain}")
        counts[domain] += 1
        image_path = Path(row["resolved_image"])
        mask_path = Path(row["resolved_mask"])
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if not mask_path.exists():
            raise FileNotFoundError(mask_path)
        width = int(row["image_width"])
        height = int(row["image_height"])
        x0, y0, x1, y1 = row["bbox_xyxy"]
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError(f"{row['id']}: invalid bbox {row['bbox_xyxy']} for {(width, height)}")
        if float(row["mask_area_ratio"]) <= 0:
            raise ValueError(f"{row['id']}: empty mask")
    if counts != {domain: per_domain for domain in expected_domains}:
        raise ValueError(f"unexpected per-domain counts: {counts}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a region grounding eval set from tampered image/mask pairs.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/region_eval/region_eval_p60"))
    parser.add_argument("--dataset-name", help="Dataset name used in metadata and sample ids. Defaults to output directory name.")
    parser.add_argument("--per-domain", type=int, default=20)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument(
        "--exclude-manifest",
        type=Path,
        action="append",
        default=[
            Path("artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"),
        ],
        help="Manifest JSONL whose image/archive keys should be excluded before sampling. Can be repeated.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.per_domain < 1:
        raise ValueError("--per-domain must be positive")
    meta = build_dataset(args)
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
