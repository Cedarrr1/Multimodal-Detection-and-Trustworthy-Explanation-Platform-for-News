#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import tarfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from PIL import Image

from build_stage1_domain_boost_json import (
    Candidate,
    bbox_from_mask,
    close_archives,
    copy_archive_member,
    discover_casia,
    discover_faceapp,
    discover_ffhq,
    discover_sd_inpaint,
    get_archive,
    read_binary_mask,
    safe_name,
    stable_seed,
)


DEFAULT_EXCLUDES = [
    Path("artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_multisource_eval_p600/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_multisource_eval_p600_final/manifest.jsonl"),
    Path("artifacts/lora_data/stage1_domain_boost_json/manifest.jsonl"),
    Path("artifacts/region_eval/region_eval_p60/manifest.jsonl"),
    Path("artifacts/region_eval/region_eval_p150/samples.jsonl"),
    Path("artifacts/region_eval/region_eval_p150_v2_final/manifest.jsonl"),
]

GT_KEYS = {"label", "verdict", "tamper_domain", "gt_mask", "gt_bbox", "mask", "mask_member", "resolved_gt_mask", "resolved_mask"}


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
        keys.add(text.rsplit("/", 1)[-1])
    return {key for key in keys if key}


def row_source_keys(row: dict[str, Any]) -> set[str]:
    fields = [
        "id",
        "image",
        "resolved_image",
        "archive_member",
        "image_member",
        "sample_key",
        "source_id",
    ]
    keys: set[str] = set()
    for field in fields:
        keys.update(path_keys(row.get(field)))
    source = row.get("source_archive") or row.get("source_path")
    member = row.get("image_member") or row.get("archive_member")
    if source and member:
        keys.add(f"{source}::{member}")
    return keys


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_exclusions(paths: Iterable[Path]) -> tuple[set[str], set[str], dict[str, Any]]:
    keys: set[str] = set()
    hashes: set[str] = set()
    stats: dict[str, Any] = {}
    for path in paths:
        rows = load_jsonl(path)
        image_hashes = 0
        for row in rows:
            keys.update(row_source_keys(row))
            existing_hash = row.get("sha256") or row.get("image_sha256")
            if existing_hash:
                hashes.add(str(existing_hash))
            resolved = row.get("resolved_image") or row.get("image_path")
            if resolved and Path(str(resolved)).exists():
                try:
                    hashes.add(sha256_file(Path(str(resolved))))
                    image_hashes += 1
                except OSError:
                    pass
        stats[str(path)] = {"rows": len(rows), "image_hashes": image_hashes}
    return keys, hashes, stats


def candidate_source_keys(candidate: Candidate) -> set[str]:
    keys = {candidate.id, f"{candidate.source_path}::{candidate.image_member}"}
    keys.update(path_keys(candidate.image_member))
    return {key for key in keys if key}


def read_candidate_image_bytes(candidate: Candidate) -> bytes:
    suffix = candidate.source_path.suffix.lower()
    if suffix == ".zip":
        archive = get_archive(candidate.source_path)
        if not isinstance(archive, zipfile.ZipFile):
            raise TypeError(f"expected zip archive for {candidate.source_path}")
        return archive.read(candidate.image_member)
    if suffix == ".tar":
        archive = get_archive(candidate.source_path)
        if not isinstance(archive, tarfile.TarFile):
            raise TypeError(f"expected tar archive for {candidate.source_path}")
        src = archive.extractfile(candidate.image_member)
        if src is None:
            raise FileNotFoundError(candidate.image_member)
        with src:
            return src.read()
    return candidate.source_path.read_bytes()


def candidate_sha256(candidate: Candidate) -> str:
    return hashlib.sha256(read_candidate_image_bytes(candidate)).hexdigest()


def discover_groups(args: argparse.Namespace) -> dict[str, list[Candidate]]:
    casia = discover_casia(args.casia_zip)
    ffhq = discover_ffhq(args.ffhq_zip, args.ffhq_split)
    faceapp = discover_faceapp(args.faceapp_zip, args.faceapp_split)
    sd_eval = discover_sd_inpaint(args.sd_eval_tar, "eval")
    groups = {
        "CASIA:authentic": [c for c in casia if c.label == "authentic"],
        "CASIA:tampered": [c for c in casia if c.label == "tampered" and c.mask_member],
        "FFHQ:authentic": [c for c in ffhq if c.label == "authentic"],
        "FaceApp:tampered": [c for c in faceapp if c.label == "tampered" and c.mask_member],
        "SD-inpaint:authentic": [c for c in sd_eval if c.label == "authentic"],
        "SD-inpaint:tampered": [c for c in sd_eval if c.label == "tampered" and c.mask_member],
    }
    return groups


def sample_group(
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
        if candidate_source_keys(candidate) & excluded_keys:
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
        raise RuntimeError(f"{name}: requested {count}, selected {len(selected)} after exclusions")
    return selected, {
        "available": len(candidates),
        "excluded_by_source_key": excluded_by_key,
        "excluded_by_sha256": excluded_by_sha,
        "duplicate_sha256_in_output": duplicate_sha,
        "selected": len(selected),
        "selected_from_excluded_fallback": 0,
    }


def rel_paths(dataset_name: str, candidate: Candidate, index: int) -> tuple[Path, Path | None]:
    suffix = Path(candidate.image_member).suffix.lower()
    source_domain = candidate.source_domain
    label = candidate.label
    sid = safe_name(f"{dataset_name}_{source_domain}_{label}_{index:03d}_{candidate.source}_{candidate.id}")
    image_rel = Path("images") / source_domain / candidate.source / label / f"{sid}{suffix}"
    mask_rel = None
    if candidate.label == "tampered":
        mask_rel = Path("masks") / source_domain / candidate.source / f"{sid}.png"
    return image_rel, mask_rel


def write_rows(args: argparse.Namespace, selected_by_group: dict[str, list[tuple[Candidate, str]]], group_stats: dict[str, Any], exclusion_stats: dict[str, Any]) -> dict[str, Any]:
    dataset_name = args.dataset_name or args.output_root.name
    args.output_root.mkdir(parents=True, exist_ok=True)
    eval_manifest = args.output_root / "eval_manifest.jsonl"
    pipeline_manifest = args.output_root / "pipeline_manifest.jsonl"
    meta_path = args.output_root / "dataset_meta.json"

    eval_rows: list[dict[str, Any]] = []
    pipeline_rows: list[dict[str, Any]] = []
    bucket_counts: dict[str, int] = defaultdict(int)
    for bucket, items in selected_by_group.items():
        for candidate, digest in items:
            bucket_counts[bucket] += 1
            image_rel, mask_rel = rel_paths(dataset_name, candidate, bucket_counts[bucket])
            image_path = args.output_root / image_rel
            copy_archive_member(candidate, candidate.image_member, image_path)
            width, height = Image.open(image_path).size

            mask_path = None
            gt_bbox = None
            mask_area = 0
            mask_area_ratio = 0.0
            if candidate.label == "tampered":
                if not candidate.mask_member or mask_rel is None:
                    raise RuntimeError(f"missing mask for tampered candidate {candidate.source}:{candidate.image_member}")
                mask_path = args.output_root / mask_rel
                copy_archive_member(candidate, candidate.mask_member, mask_path)
                mask = read_binary_mask(mask_path, (width, height))
                gt_bbox = bbox_from_mask(mask)
                mask_area = int(mask.sum())
                mask_area_ratio = mask_area / float(width * height)

            row_id = safe_name(f"{dataset_name}_{bucket.replace(':', '_')}_{bucket_counts[bucket]:03d}")
            common = {
                "id": row_id,
                "image": str(image_rel),
                "resolved_image": str(image_path),
                "source": candidate.source,
                "source_dataset": candidate.source,
                "source_domain": candidate.source_domain,
                "source_split": candidate.source_split,
                "source_archive": str(candidate.source_path),
                "image_member": candidate.image_member,
                "image_width": width,
                "image_height": height,
                "sha256": digest,
            }
            eval_row = {
                **common,
                "label": candidate.label,
                "verdict": "tampered" if candidate.label == "tampered" else "authentic",
                "tamper_domain": candidate.tamper_domain,
                "gt_mask": str(mask_rel) if mask_rel else None,
                "resolved_gt_mask": str(mask_path) if mask_path else None,
                "mask_member": candidate.mask_member,
                "gt_bbox": gt_bbox,
                "bbox_format": "xyxy_half_open" if gt_bbox else None,
                "mask_area_pixels": mask_area,
                "mask_area_ratio": mask_area_ratio,
            }
            pipeline_row = {key: value for key, value in common.items() if key not in {"source_archive", "image_member"}}
            if GT_KEYS & set(pipeline_row):
                raise RuntimeError(f"pipeline manifest leaked GT keys: {GT_KEYS & set(pipeline_row)}")
            eval_rows.append(eval_row)
            pipeline_rows.append(pipeline_row)

    with eval_manifest.open("w", encoding="utf-8") as f:
        for row in eval_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with pipeline_manifest.open("w", encoding="utf-8") as f:
        for row in pipeline_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    meta = {
        "name": dataset_name,
        "output_root": str(args.output_root),
        "seed": args.seed,
        "per_bucket": args.per_bucket,
        "total": len(eval_rows),
        "eval_manifest": str(eval_manifest),
        "pipeline_manifest": str(pipeline_manifest),
        "group_stats": group_stats,
        "excluded_manifests": [str(path) for path in args.exclude_manifest],
        "exclusion_stats": exclusion_stats,
        "pipeline_manifest_forbidden_keys": sorted(GT_KEYS),
        "boundary": "image-only pipeline manifest; GT masks/bboxes only in eval_manifest for scoring",
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_outputs(eval_manifest, pipeline_manifest, args.per_bucket)
    return meta


def validate_outputs(eval_manifest: Path, pipeline_manifest: Path, per_bucket: int) -> None:
    eval_rows = load_jsonl(eval_manifest)
    pipeline_rows = load_jsonl(pipeline_manifest)
    if len(eval_rows) != len(pipeline_rows):
        raise ValueError("eval and pipeline manifest row counts differ")
    buckets = defaultdict(int)
    for eval_row, pipe_row in zip(eval_rows, pipeline_rows):
        if eval_row["id"] != pipe_row["id"]:
            raise ValueError(f"id mismatch: {eval_row['id']} vs {pipe_row['id']}")
        leaked = GT_KEYS & set(pipe_row)
        if leaked:
            raise ValueError(f"{pipe_row['id']}: pipeline manifest leaked {sorted(leaked)}")
        image_path = Path(pipe_row["resolved_image"])
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        label = eval_row["label"]
        bucket = f"{eval_row['source']}:{label}"
        buckets[bucket] += 1
        if label == "tampered":
            if not eval_row.get("resolved_gt_mask"):
                raise ValueError(f"{eval_row['id']}: tampered row missing gt mask")
            if not Path(eval_row["resolved_gt_mask"]).exists():
                raise FileNotFoundError(eval_row["resolved_gt_mask"])
            if not eval_row.get("gt_bbox"):
                raise ValueError(f"{eval_row['id']}: tampered row missing gt bbox")
        elif any(eval_row.get(key) for key in ["gt_mask", "resolved_gt_mask", "gt_bbox"]):
            raise ValueError(f"{eval_row['id']}: authentic row should not expose a forged mask")
    expected = {
        "CASIA:authentic",
        "CASIA:tampered",
        "FFHQ:authentic",
        "FaceApp:tampered",
        "SD-inpaint:authentic",
        "SD-inpaint:tampered",
    }
    if set(buckets) != expected or any(value != per_bucket for value in buckets.values()):
        raise ValueError(f"unexpected bucket counts: {dict(sorted(buckets.items()))}")


def build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    excluded_keys, excluded_hashes, exclusion_stats = load_exclusions(args.exclude_manifest)
    groups = discover_groups(args)
    selected_by_group: dict[str, list[tuple[Candidate, str]]] = {}
    group_stats: dict[str, Any] = {}
    used_hashes: set[str] = set()
    for name in sorted(groups):
        selected, stats = sample_group(name, groups[name], args.per_bucket, args.seed, excluded_keys, excluded_hashes, used_hashes)
        selected_by_group[name] = selected
        group_stats[name] = stats
    return write_rows(args, selected_by_group, group_stats, exclusion_stats)


def preset_defaults(args: argparse.Namespace) -> None:
    if args.preset == "dev":
        args.output_root = args.output_root or Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev")
        args.dataset_name = args.dataset_name or "end2end_region_eval_p300_dev"
        args.per_bucket = args.per_bucket or 50
        args.seed = args.seed or 20260716
    elif args.preset == "final":
        args.output_root = args.output_root or Path("artifacts/end2end_region_eval/end2end_region_eval_p600_final")
        args.dataset_name = args.dataset_name or "end2end_region_eval_p600_final"
        args.per_bucket = args.per_bucket or 100
        args.seed = args.seed or 20260717
        dev_eval = Path("artifacts/end2end_region_eval/end2end_region_eval_p300_dev/eval_manifest.jsonl")
        if dev_eval not in args.exclude_manifest:
            args.exclude_manifest.append(dev_eval)
    else:
        if args.output_root is None:
            raise ValueError("--output-root is required when --preset custom")
        args.dataset_name = args.dataset_name or args.output_root.name
        args.per_bucket = args.per_bucket or 10
        args.seed = args.seed or 20260716


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build image-only end-to-end region localization eval manifests.")
    parser.add_argument("--preset", choices=["dev", "final", "custom"], default="dev")
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--dataset-name")
    parser.add_argument("--per-bucket", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--ffhq-zip", type=Path, default=Path("dataset/deepfake/ffhq.zip"))
    parser.add_argument("--ffhq-split", default="train")
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--faceapp-split", default="test")
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument("--exclude-manifest", type=Path, action="append", default=list(DEFAULT_EXCLUDES))
    args = parser.parse_args()
    preset_defaults(args)
    if args.per_bucket < 1:
        raise ValueError("--per-bucket must be positive")
    return args


def main() -> None:
    args = parse_args()
    try:
        meta = build_dataset(args)
    finally:
        close_archives()
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
