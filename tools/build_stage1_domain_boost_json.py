#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image


COMPACT_PROMPT = (
    "<image>\n"
    "Analyze whether this image has been digitally manipulated. "
    "Return only valid compact JSON with exactly these keys: "
    "verdict and tamper_domain. "
    'Use verdict "authentic" or "tampered"; use tamper_domain '
    '"none", "photoshop", "deepfake", or "aigc_inpaint".'
)

EXPLANATION_PROMPT = (
    "<image>\n"
    "<image>\n"
    "Analyze whether this image has been digitally manipulated. "
    "The first image is the full image and the second image is a deterministic "
    "region crop for closer inspection. Return only valid JSON with exactly "
    "these keys: verdict, tamper_domain, tampered_region, and evidence."
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}
ARCHIVE_CACHE: dict[str, zipfile.ZipFile | tarfile.TarFile] = {}


@dataclass(frozen=True)
class Candidate:
    source: str
    source_split: str
    source_path: Path
    image_member: str
    mask_member: str | None
    label: str
    source_domain: str
    tamper_domain: str
    id: str


def is_image(name: str) -> bool:
    return Path(name).suffix.lower() in IMAGE_EXTS and not name.endswith("/")


def image_id(member: str) -> str:
    return Path(member).stem


def trailing_numeric_id(stem: str) -> str:
    match = re.search(r"_(\d+)$", stem)
    return match.group(1) if match else stem


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")


def list_zip_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(name for name in zf.namelist() if is_image(name))


def list_tar_members(path: Path) -> list[str]:
    with tarfile.open(path) as tf:
        return sorted(member.name for member in tf.getmembers() if member.isfile() and is_image(member.name))


def path_keys(value: Any) -> set[str]:
    if value is None:
        return set()
    text = str(value).replace("\\", "/")
    path = Path(text)
    keys = {text, path.name, path.stem}
    if "/" in text:
        keys.add(text.rsplit("/", 1)[-1])
    return {key for key in keys if key}


def load_exclusion_keys(paths: Iterable[Path]) -> set[str]:
    fields = ["id", "image", "resolved_image", "archive_member", "image_member", "mask_member", "sample_key"]
    excluded: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for field in fields:
                excluded.update(path_keys(row.get(field)))
    return excluded


def candidate_keys(candidate: Candidate) -> set[str]:
    keys = {candidate.id}
    keys.update(path_keys(candidate.image_member))
    keys.update(path_keys(candidate.mask_member))
    return {key for key in keys if key}


def is_excluded(candidate: Candidate, exclusion_keys: set[str]) -> bool:
    return bool(candidate_keys(candidate) & exclusion_keys)


def stable_seed(seed: int, *parts: str) -> int:
    digest = hashlib.sha256(":".join([str(seed), *parts]).encode("utf-8")).hexdigest()
    return seed + int(digest[:8], 16)


def sample_candidates(candidates: list[Candidate], count: int, seed: int, exclusion_keys: set[str]) -> tuple[list[Candidate], dict[str, Any]]:
    clean = [candidate for candidate in candidates if not is_excluded(candidate, exclusion_keys)]
    excluded = [candidate for candidate in candidates if is_excluded(candidate, exclusion_keys)]
    rng = random.Random(seed)
    rng.shuffle(clean)
    rng.shuffle(excluded)
    selected = clean[:count]
    fallback = 0
    if len(selected) < count:
        need = count - len(selected)
        selected.extend(excluded[:need])
        fallback = min(need, len(excluded))
    if len(selected) < count:
        raise RuntimeError(f"requested {count} candidates but only found {len(selected)}")
    return selected, {
        "available": len(candidates),
        "excluded_by_manifest": len(excluded),
        "available_after_exclusion": len(clean),
        "selected": len(selected),
        "selected_from_excluded_fallback": fallback,
    }


def discover_casia(path: Path) -> list[Candidate]:
    members = list_zip_members(path)
    masks: dict[str, str] = {}
    for member in members:
        if member.startswith("CASIA2/CASIA 2 Groundtruth/") and Path(member).stem.endswith("_gt"):
            stem = Path(member).stem[:-3]
            masks[trailing_numeric_id(stem)] = member

    out: list[Candidate] = []
    for member in members:
        if member.startswith("CASIA2/Au/"):
            out.append(
                Candidate(
                    source="CASIA",
                    source_split="all",
                    source_path=path,
                    image_member=member,
                    mask_member=None,
                    label="authentic",
                    source_domain="photoshop",
                    tamper_domain="none",
                    id=image_id(member),
                )
            )
        elif member.startswith("CASIA2/Tp/"):
            out.append(
                Candidate(
                    source="CASIA",
                    source_split="all",
                    source_path=path,
                    image_member=member,
                    mask_member=masks.get(trailing_numeric_id(Path(member).stem)),
                    label="tampered",
                    source_domain="photoshop",
                    tamper_domain="photoshop",
                    id=image_id(member),
                )
            )
    return out


def discover_ffhq(path: Path, split: str) -> list[Candidate]:
    prefix = f"ffhq/{split}/"
    return [
        Candidate(
            source="FFHQ",
            source_split=split,
            source_path=path,
            image_member=member,
            mask_member=None,
            label="authentic",
            source_domain="deepfake",
            tamper_domain="none",
            id=image_id(member),
        )
        for member in list_zip_members(path)
        if member.startswith(prefix)
    ]


def discover_faceapp(path: Path, split: str) -> list[Candidate]:
    image_prefix = f"faceapp/{split}/"
    mask_prefix = f"faceapp/{split}_mask/"
    members = list_zip_members(path)
    masks = {Path(member).name: member for member in members if member.startswith(mask_prefix)}
    out: list[Candidate] = []
    for member in members:
        if not member.startswith(image_prefix):
            continue
        out.append(
            Candidate(
                source="FaceApp",
                source_split=split,
                source_path=path,
                image_member=member,
                mask_member=masks.get(Path(member).name),
                label="tampered",
                source_domain="deepfake",
                tamper_domain="deepfake",
                id=image_id(member),
            )
        )
    return out


def discover_sd_inpaint(path: Path, split: str) -> list[Candidate]:
    members = list_tar_members(path)
    masks: dict[tuple[str, str], str] = {}
    for member in members:
        if f"{split}/Tp/mask/" in member:
            masks[("tampered", image_id(member))] = member

    out: list[Candidate] = []
    for member in members:
        if member.startswith(f"{split}/Au/image/"):
            out.append(
                Candidate(
                    source="SD-inpaint",
                    source_split=split,
                    source_path=path,
                    image_member=member,
                    mask_member=None,
                    label="authentic",
                    source_domain="aigc_editing",
                    tamper_domain="none",
                    id=image_id(member),
                )
            )
        elif member.startswith(f"{split}/Tp/image/"):
            out.append(
                Candidate(
                    source="SD-inpaint",
                    source_split=split,
                    source_path=path,
                    image_member=member,
                    mask_member=masks.get(("tampered", image_id(member))),
                    label="tampered",
                    source_domain="aigc_editing",
                    tamper_domain="aigc_inpaint",
                    id=image_id(member),
                )
            )
    return out


def get_archive(path: Path) -> zipfile.ZipFile | tarfile.TarFile:
    key = str(path)
    if key not in ARCHIVE_CACHE:
        suffix = path.suffix.lower()
        if suffix == ".zip":
            ARCHIVE_CACHE[key] = zipfile.ZipFile(path)
        elif suffix == ".tar":
            ARCHIVE_CACHE[key] = tarfile.open(path)
        else:
            raise ValueError(f"unsupported archive: {path}")
    return ARCHIVE_CACHE[key]


def close_archives() -> None:
    for archive in ARCHIVE_CACHE.values():
        archive.close()
    ARCHIVE_CACHE.clear()


def copy_archive_member(candidate: Candidate, member: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        return
    archive = get_archive(candidate.source_path)
    if isinstance(archive, zipfile.ZipFile):
        with archive.open(member) as src, output_path.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    else:
        src = archive.extractfile(member)
        if src is None:
            raise FileNotFoundError(member)
        with src, output_path.open("wb") as dst:
            shutil.copyfileobj(src, dst)


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
        raise ValueError("empty mask")
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def expand_bbox(bbox: list[int], width: int, height: int, scale: float) -> list[int]:
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    bw = max(1.0, (x1 - x0) * scale)
    bh = max(1.0, (y1 - y0) * scale)
    nx0 = max(0, int(round(cx - bw / 2.0)))
    ny0 = max(0, int(round(cy - bh / 2.0)))
    nx1 = min(width, int(round(cx + bw / 2.0)))
    ny1 = min(height, int(round(cy + bh / 2.0)))
    if nx1 <= nx0:
        nx1 = min(width, nx0 + 1)
    if ny1 <= ny0:
        ny1 = min(height, ny0 + 1)
    return [nx0, ny0, nx1, ny1]


def negative_crop_box(candidate: Candidate, width: int, height: int) -> tuple[str, list[int]]:
    focus_names = ["center", "upper_left", "upper_right", "lower_left", "lower_right"]
    digest = hashlib.sha256(f"{candidate.source}:{candidate.id}:{candidate.image_member}".encode("utf-8")).hexdigest()
    focus = focus_names[int(digest[:8], 16) % len(focus_names)]
    centers = {
        "center": (0.5, 0.5),
        "upper_left": (0.3, 0.3),
        "upper_right": (0.7, 0.3),
        "lower_left": (0.3, 0.7),
        "lower_right": (0.7, 0.7),
    }
    crop_w = max(1, round(width * 0.5))
    crop_h = max(1, round(height * 0.5))
    cx = round(width * centers[focus][0])
    cy = round(height * centers[focus][1])
    x0 = min(max(0, cx - crop_w // 2), width - crop_w)
    y0 = min(max(0, cy - crop_h // 2), height - crop_h)
    return focus, [x0, y0, x0 + crop_w, y0 + crop_h]


def make_crop(full_image: Path, crop_path: Path, bbox: list[int]) -> None:
    crop_path.parent.mkdir(parents=True, exist_ok=True)
    if crop_path.exists():
        return
    with Image.open(full_image) as image:
        crop = image.convert("RGB").crop(tuple(bbox))
        crop.save(crop_path, quality=95)


def output_image_rel(candidate: Candidate) -> Path:
    suffix = Path(candidate.image_member).suffix.lower()
    return (
        Path("images")
        / candidate.source_domain
        / candidate.source
        / candidate.source_split
        / candidate.label
        / f"{safe_name(candidate.id)}{suffix}"
    )


def output_mask_rel(candidate: Candidate) -> Path:
    return (
        Path("masks")
        / candidate.source_domain
        / candidate.source
        / candidate.source_split
        / f"{safe_name(candidate.id)}.png"
    )


def output_crop_rel(candidate: Candidate) -> Path:
    return (
        Path("crops")
        / candidate.source_domain
        / candidate.source
        / candidate.source_split
        / candidate.label
        / f"{safe_name(candidate.id)}_crop.jpg"
    )


def compact_target(candidate: Candidate) -> dict[str, Any]:
    verdict = "tampered" if candidate.label == "tampered" else "authentic"
    return {"verdict": verdict, "tamper_domain": candidate.tamper_domain}


def evidence_for(candidate: Candidate) -> list[str]:
    if candidate.label != "tampered":
        return [
            "No localized tamper region is annotated for this authentic image.",
            "The deterministic crop is negative context from the original image.",
        ]
    if candidate.tamper_domain == "photoshop":
        return [
            "The crop targets a mask-annotated edited region with local boundary or blending artifacts.",
            "The full image context helps compare lighting, texture, and geometry around the edit.",
        ]
    if candidate.tamper_domain == "aigc_inpaint":
        return [
            "The crop targets an inpainted region with texture or semantic inconsistencies.",
            "The full image context helps compare the generated content against nearby structures.",
        ]
    if candidate.tamper_domain == "deepfake":
        return [
            "The crop targets the mask-annotated face region where identity blending may appear.",
            "The full image context helps compare facial texture and boundary consistency.",
        ]
    return ["The crop targets the annotated manipulated region."]


def explanation_target(candidate: Candidate, crop_box: list[int]) -> dict[str, Any]:
    verdict = "tampered" if candidate.label == "tampered" else "authentic"
    region = "none"
    if verdict == "tampered":
        region = f"crop around annotated {candidate.tamper_domain} region, bbox_xyxy={crop_box}"
    evidence = [item[:160] for item in evidence_for(candidate)[:2]]
    return {
        "verdict": verdict,
        "tamper_domain": candidate.tamper_domain,
        "tampered_region": region,
        "evidence": evidence,
    }


def prepare_images(candidate: Candidate, output_root: Path, crop_scale: float) -> dict[str, Any]:
    image_rel = output_image_rel(candidate)
    image_path = output_root / image_rel
    copy_archive_member(candidate, candidate.image_member, image_path)

    mask_rel = None
    mask_path = None
    with Image.open(image_path) as image:
        width, height = image.size

    if candidate.mask_member is not None:
        mask_rel = output_mask_rel(candidate)
        mask_path = output_root / mask_rel
        copy_archive_member(candidate, candidate.mask_member, mask_path)

    if candidate.label == "tampered":
        if mask_path is None:
            raise RuntimeError(f"missing GT mask for tampered candidate: {candidate.source} {candidate.image_member}")
        mask = read_binary_mask(mask_path, (width, height))
        gt_bbox = bbox_from_mask(mask)
        crop_focus = "gt_mask_bbox"
        crop_box = expand_bbox(gt_bbox, width, height, crop_scale)
    else:
        gt_bbox = None
        crop_focus, crop_box = negative_crop_box(candidate, width, height)

    crop_rel = output_crop_rel(candidate)
    crop_path = output_root / crop_rel
    make_crop(image_path, crop_path, crop_box)

    return {
        "image_rel": str(image_rel),
        "image_path": str(image_path),
        "mask_rel": str(mask_rel) if mask_rel is not None else None,
        "mask_path": str(mask_path) if mask_path is not None else None,
        "crop_rel": str(crop_rel),
        "crop_path": str(crop_path),
        "image_width": width,
        "image_height": height,
        "gt_bbox": gt_bbox,
        "crop_box": crop_box,
        "crop_focus": crop_focus,
    }


def select_all(args: argparse.Namespace, exclusion_keys: set[str]) -> tuple[list[Candidate], dict[str, Any]]:
    discoveries = {
        "aigc_train_authentic": [c for c in discover_sd_inpaint(args.sd_train_tar, "train") if c.label == "authentic"],
        "aigc_train_tampered": [c for c in discover_sd_inpaint(args.sd_train_tar, "train") if c.label == "tampered"],
        "aigc_eval_authentic": [c for c in discover_sd_inpaint(args.sd_eval_tar, "eval") if c.label == "authentic"],
        "aigc_eval_tampered": [c for c in discover_sd_inpaint(args.sd_eval_tar, "eval") if c.label == "tampered"],
        "photoshop_authentic": [c for c in discover_casia(args.casia_zip) if c.label == "authentic"],
        "photoshop_tampered": [c for c in discover_casia(args.casia_zip) if c.label == "tampered"],
        "deepfake_authentic": discover_ffhq(args.ffhq_zip, args.ffhq_split),
        "deepfake_tampered": discover_faceapp(args.faceapp_zip, args.faceapp_split),
    }
    quotas = {
        "aigc_train_authentic": args.aigc_per_split_label,
        "aigc_train_tampered": args.aigc_per_split_label,
        "aigc_eval_authentic": args.aigc_per_split_label,
        "aigc_eval_tampered": args.aigc_per_split_label,
        "photoshop_authentic": args.photoshop_per_label,
        "photoshop_tampered": args.photoshop_per_label,
        "deepfake_authentic": args.deepfake_per_label,
        "deepfake_tampered": args.deepfake_per_label,
    }

    selected: list[Candidate] = []
    stats: dict[str, Any] = {}
    for name, candidates in discoveries.items():
        chosen, group_stats = sample_candidates(candidates, quotas[name], stable_seed(args.seed, name), exclusion_keys)
        selected.extend(chosen)
        stats[name] = group_stats
    return selected, stats


def write_dataset(args: argparse.Namespace) -> dict[str, Any]:
    exclusion_keys = load_exclusion_keys(args.exclude_manifest)
    selected, group_stats = select_all(args, exclusion_keys)
    args.output_root.mkdir(parents=True, exist_ok=True)

    jsonl_path = args.output_root / "llamafactory_qwen_vl_sft.jsonl"
    manifest_path = args.output_root / "manifest.jsonl"
    selected_path = args.output_root / "selected_sources.jsonl"
    meta_path = args.output_root / "dataset_meta.json"

    total_rows = 0
    with jsonl_path.open("w", encoding="utf-8") as jf, manifest_path.open("w", encoding="utf-8") as mf, selected_path.open("w", encoding="utf-8") as sf:
        for candidate in selected:
            prepared = prepare_images(candidate, args.output_root, args.crop_scale)
            source_payload = {
                "source_id": f"{candidate.source}_{candidate.source_split}_{candidate.label}_{candidate.id}",
                "source": candidate.source,
                "source_split": candidate.source_split,
                "source_domain": candidate.source_domain,
                "label": candidate.label,
                "verdict": "tampered" if candidate.label == "tampered" else "authentic",
                "tamper_domain": candidate.tamper_domain,
                "source_path": str(candidate.source_path),
                "image_member": candidate.image_member,
                "mask_member": candidate.mask_member,
                **prepared,
            }
            sf.write(json.dumps(source_payload, ensure_ascii=False) + "\n")

            compact_id = f"{source_payload['source_id']}_compact"
            compact_record = {
                "id": compact_id,
                "images": [prepared["image_path"]],
                "messages": [
                    {"role": "user", "content": COMPACT_PROMPT},
                    {"role": "assistant", "content": json.dumps(compact_target(candidate), ensure_ascii=False)},
                ],
            }
            compact_manifest = {
                **source_payload,
                "id": compact_id,
                "task": "compact_judgment",
                "images": [prepared["image_rel"]],
                "target": compact_target(candidate),
            }
            jf.write(json.dumps(compact_record, ensure_ascii=False) + "\n")
            mf.write(json.dumps(compact_manifest, ensure_ascii=False) + "\n")
            total_rows += 1

            explanation_id = f"{source_payload['source_id']}_explanation"
            explanation = explanation_target(candidate, prepared["crop_box"])
            explanation_record = {
                "id": explanation_id,
                "images": [prepared["image_path"], prepared["crop_path"]],
                "messages": [
                    {"role": "user", "content": EXPLANATION_PROMPT},
                    {"role": "assistant", "content": json.dumps(explanation, ensure_ascii=False)},
                ],
            }
            explanation_manifest = {
                **source_payload,
                "id": explanation_id,
                "task": "full_explanation",
                "images": [prepared["image_rel"], prepared["crop_rel"]],
                "target": explanation,
            }
            jf.write(json.dumps(explanation_record, ensure_ascii=False) + "\n")
            mf.write(json.dumps(explanation_manifest, ensure_ascii=False) + "\n")
            total_rows += 1

    meta = {
        "name": args.output_root.name,
        "output_root": str(args.output_root),
        "seed": args.seed,
        "crop_scale": args.crop_scale,
        "selected_source_images": len(selected),
        "total_sft_rows": total_rows,
        "expected_sft_rows": 2
        * (
            4 * args.aigc_per_split_label
            + 2 * args.photoshop_per_label
            + 2 * args.deepfake_per_label
        ),
        "group_stats": group_stats,
        "excluded_manifests": [str(path) for path in args.exclude_manifest],
        "prompts": {
            "compact": COMPACT_PROMPT,
            "explanation": EXPLANATION_PROMPT,
        },
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_output(args.output_root, meta["expected_sft_rows"])
    return meta


def validate_output(output_root: Path, expected_rows: int) -> None:
    rows = [json.loads(line) for line in (output_root / "llamafactory_qwen_vl_sft.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = [json.loads(line) for line in (output_root / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != expected_rows:
        raise ValueError(f"row count {len(rows)} != expected {expected_rows}")
    if len(rows) != len(manifest):
        raise ValueError("manifest row count mismatch")
    for idx, row in enumerate(rows):
        images = row.get("images")
        messages = row.get("messages")
        if not isinstance(images, list) or not images:
            raise ValueError(f"row {idx}: missing images")
        for image in images:
            if not Path(image).exists():
                raise FileNotFoundError(image)
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"row {idx}: expected two messages")
        target = json.loads(str(messages[1].get("content", "")))
        task = manifest[idx]["task"]
        if task == "compact_judgment" and set(target) != {"verdict", "tamper_domain"}:
            raise ValueError(f"row {idx}: bad compact target keys {set(target)}")
        if task == "full_explanation" and set(target) != {"verdict", "tamper_domain", "tampered_region", "evidence"}:
            raise ValueError(f"row {idx}: bad explanation target keys {set(target)}")
        if target["verdict"] not in {"authentic", "tampered"}:
            raise ValueError(f"row {idx}: bad verdict")
        if target["tamper_domain"] not in {"none", "photoshop", "deepfake", "aigc_inpaint"}:
            raise ValueError(f"row {idx}: bad tamper_domain")
        if "evidence" in target:
            evidence = target["evidence"]
            if not isinstance(evidence, list) or len(evidence) > 2:
                raise ValueError(f"row {idx}: bad evidence list")
            if any(len(str(item)) > 160 for item in evidence):
                raise ValueError(f"row {idx}: evidence too long")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Stage1 domain-boost SFT data with compact and explanation supervision.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage1_domain_boost_json"))
    parser.add_argument("--seed", type=int, default=20260711)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--ffhq-zip", type=Path, default=Path("dataset/deepfake/ffhq.zip"))
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--ffhq-split", default="train")
    parser.add_argument("--faceapp-split", default="train")
    parser.add_argument("--sd-train-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/train.tar"))
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument("--aigc-per-split-label", type=int, default=150)
    parser.add_argument("--photoshop-per-label", type=int, default=200)
    parser.add_argument("--deepfake-per-label", type=int, default=100)
    parser.add_argument("--crop-scale", type=float, default=1.25)
    parser.add_argument(
        "--exclude-manifest",
        type=Path,
        action="append",
        default=[
            Path("artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_multisource_eval_p600/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_multisource_eval_p600_final/manifest.jsonl"),
            Path("artifacts/region_eval/region_eval_p150/samples.jsonl"),
        ],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.crop_scale < 1.0:
        raise ValueError("--crop-scale must be >= 1.0")
    try:
        meta = write_dataset(args)
    finally:
        close_archives()
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
