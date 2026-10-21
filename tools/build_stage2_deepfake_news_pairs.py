#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from build_stage1_domain_boost_json import (
    Candidate,
    close_archives,
    copy_archive_member,
    safe_name,
)
from generate_stage2_deepfake_captions_qwen_vl import FORBIDDEN_TERMS, forbidden_hits


PROMPT = (
    "<image>\n"
    "Title: {title}\n"
    "Body: {body}\n\n"
    "Determine whether the image is digitally manipulated and whether the title "
    "and body match the visible image. This is a controlled text-image "
    "consistency benchmark, not real-world news fact checking. Return only "
    "valid compact JSON with exactly these keys: image_verdict, tamper_domain, "
    "text_image_relation, final_news_verdict, forensic_region, and evidence. "
    'Use image_verdict "authentic" or "tampered"; tamper_domain "none" or '
    '"deepfake"; text_image_relation "consistent" or "mismatched"; '
    'final_news_verdict "credible" or "fake_news"; forensic_region "face" or "none".'
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_label(row: dict[str, Any]) -> str:
    verdict = str(row.get("image_verdict") or "").strip().lower()
    if verdict in {"authentic", "tampered"}:
        return verdict
    label = str(row.get("label") or "").strip().lower()
    if label in {"authentic", "tampered"}:
        return label
    raise ValueError(f"bad image label for caption row {row.get('source_key')}")


def validate_caption(row: dict[str, Any]) -> None:
    for key in ["source_key", "image", "title", "body", "caption"]:
        if not str(row.get(key, "")).strip():
            raise ValueError(f"caption row missing {key}: {row}")
    image = Path(str(row["image"]))
    if not image.exists():
        raise FileNotFoundError(image)
    hits = forbidden_hits(str(row["title"]), str(row["body"]))
    if hits:
        raise ValueError(f"{row['source_key']}: forbidden article terms: {hits}")
    verdict = normalize_label(row)
    domain = str(row.get("tamper_domain") or ("deepfake" if verdict == "tampered" else "none")).lower()
    if verdict == "authentic" and domain != "none":
        raise ValueError(f"{row['source_key']}: authentic row must use tamper_domain none")
    if verdict == "tampered" and domain != "deepfake":
        raise ValueError(f"{row['source_key']}: tampered row must use tamper_domain deepfake")


def stable_int(seed: int, *parts: str) -> int:
    digest = hashlib.sha256(":".join([str(seed), *parts]).encode("utf-8")).hexdigest()
    return seed + int(digest[:8], 16)


def image_vector(image_path: Path) -> np.ndarray:
    with Image.open(image_path) as image:
        arr = np.asarray(image.convert("RGB").resize((64, 64)), dtype=np.float32) / 255.0
    hist, _ = np.histogramdd(
        arr.reshape(-1, 3),
        bins=(8, 8, 8),
        range=((0.0, 1.0), (0.0, 1.0), (0.0, 1.0)),
    )
    vec = hist.reshape(-1).astype(np.float32)
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    return 1.0 - float(np.dot(a, b))


def select_by_label(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, dict[str, list[dict[str, Any]]]]:
    per_label_needed = args.train_per_cell + args.dev_per_cell + args.final_per_cell
    buckets = {
        "authentic": [row for row in rows if normalize_label(row) == "authentic"],
        "tampered": [row for row in rows if normalize_label(row) == "tampered"],
    }
    out: dict[str, dict[str, list[dict[str, Any]]]] = {
        "train": {"authentic": [], "tampered": []},
        "dev": {"authentic": [], "tampered": []},
        "final": {"authentic": [], "tampered": []},
    }
    for verdict, group in buckets.items():
        if len(group) < per_label_needed:
            raise RuntimeError(f"{verdict}: need {per_label_needed} caption rows, found {len(group)}")
        rng = random.Random(stable_int(args.seed, verdict))
        shuffled = list(group)
        rng.shuffle(shuffled)
        cursor = 0
        for split, count in [("train", args.train_per_cell), ("dev", args.dev_per_cell), ("final", args.final_per_cell)]:
            out[split][verdict] = shuffled[cursor : cursor + count]
            cursor += count
    return out


def candidate_from_caption(row: dict[str, Any]) -> Candidate:
    verdict = normalize_label(row)
    return Candidate(
        source=str(row.get("source") or ("FaceApp" if verdict == "tampered" else "FFHQ")),
        source_split=str(row.get("source_split") or "unknown"),
        source_path=Path(str(row["source_path"])),
        image_member=str(row["image_member"]),
        mask_member=str(row.get("mask_member") or "") or None,
        label=verdict,
        source_domain="deepfake",
        tamper_domain="deepfake" if verdict == "tampered" else "none",
        id=safe_name(Path(str(row["image_member"])).stem),
    )


def prepare_media(row: dict[str, Any], output_root: Path, split: str, index: int) -> dict[str, Any]:
    verdict = normalize_label(row)
    source = str(row.get("source") or ("FaceApp" if verdict == "tampered" else "FFHQ"))
    suffix = Path(str(row["image"])).suffix.lower() or Path(str(row["image_member"])).suffix.lower() or ".jpg"
    sample_key = safe_name(f"{split}_{verdict}_{index:04d}_{source}_{Path(str(row['image_member'])).stem}")
    image_rel = Path("images") / split / verdict / f"{sample_key}{suffix}"
    image_path = output_root / image_rel
    image_path.parent.mkdir(parents=True, exist_ok=True)
    if not image_path.exists():
        shutil.copy2(Path(str(row["image"])), image_path)

    with Image.open(image_path) as image:
        width, height = image.size

    mask_rel = None
    mask_path = None
    if verdict == "tampered" and row.get("mask_member"):
        candidate = candidate_from_caption(row)
        mask_rel = Path("masks") / split / f"{sample_key}.png"
        mask_path = output_root / mask_rel
        copy_archive_member(candidate, str(row["mask_member"]), mask_path)

    return {
        "image": str(image_path),
        "image_rel": str(image_rel),
        "gt_mask": str(mask_path) if mask_path is not None else None,
        "gt_mask_rel": str(mask_rel) if mask_rel is not None else None,
        "image_width": width,
        "image_height": height,
    }


def target_for(image_verdict: str, relation: str) -> dict[str, Any]:
    tampered = image_verdict == "tampered"
    final = "fake_news" if tampered or relation == "mismatched" else "credible"
    evidence = []
    if tampered:
        evidence.append("Image-level supervision marks the face region as manipulated.")
    else:
        evidence.append("Image-level supervision marks the portrait as authentic.")
    if relation == "consistent":
        evidence.append("The title and body are paired with the same portrait image.")
    else:
        evidence.append("The title and body are paired from a different portrait image.")
    return {
        "image_verdict": image_verdict,
        "tamper_domain": "deepfake" if tampered else "none",
        "text_image_relation": relation,
        "final_news_verdict": final,
        "forensic_region": "face" if tampered else "none",
        "evidence": evidence,
    }


def build_donor_map(rows: list[dict[str, Any]], seed: int) -> dict[str, dict[str, Any]]:
    vectors: dict[str, np.ndarray] = {}
    for row in rows:
        vectors[str(row["source_key"])] = image_vector(Path(str(row["image"])))
    rng = random.Random(seed)
    donor_map: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row["source_key"])
        candidates = [candidate for candidate in rows if str(candidate["source_key"]) != key]
        rng.shuffle(candidates)
        candidates.sort(
            key=lambda candidate: cosine_distance(vectors[key], vectors[str(candidate["source_key"])]),
            reverse=True,
        )
        if not candidates:
            raise RuntimeError("cannot build mismatched pairs with fewer than two images")
        donor_map[key] = candidates[0]
    return donor_map


def build_split(split: str, selected: dict[str, list[dict[str, Any]]], output_root: Path, seed: int) -> list[dict[str, Any]]:
    source_rows = selected["authentic"] + selected["tampered"]
    donor_map = build_donor_map(source_rows, stable_int(seed, split, "donors"))
    records: list[dict[str, Any]] = []
    media_by_key: dict[str, dict[str, Any]] = {}
    for idx, row in enumerate(source_rows, start=1):
        media_by_key[str(row["source_key"])] = prepare_media(row, output_root, split, idx)

    for idx, row in enumerate(source_rows, start=1):
        image_verdict = normalize_label(row)
        source_key = str(row["source_key"])
        media = media_by_key[source_key]
        for relation in ["consistent", "mismatched"]:
            text_row = row if relation == "consistent" else donor_map[source_key]
            target = target_for(image_verdict, relation)
            cell = f"{image_verdict}_{relation}"
            record_id = safe_name(f"stage2_deepfake_news_{split}_{cell}_{idx:04d}")
            record = {
                "id": record_id,
                "split": split,
                "cell": cell,
                "source_key": source_key,
                "source": row.get("source"),
                "source_split": row.get("source_split"),
                "source_path": row.get("source_path"),
                "image_member": row.get("image_member"),
                "mask_member": row.get("mask_member"),
                "donor_source_key": str(text_row["source_key"]) if relation == "mismatched" else None,
                "donor_image_member": text_row.get("image_member") if relation == "mismatched" else None,
                "title": text_row["title"],
                "body": text_row["body"],
                "caption": row["caption"],
                "donor_caption": text_row["caption"] if relation == "mismatched" else None,
                "image": media["image"],
                "image_rel": media["image_rel"],
                "gt_mask": media["gt_mask"],
                "gt_mask_rel": media["gt_mask_rel"],
                "image_width": media["image_width"],
                "image_height": media["image_height"],
                "target": target,
                "prompt": PROMPT.format(title=text_row["title"], body=text_row["body"]),
            }
            records.append(record)
    rng = random.Random(stable_int(seed, split, "shuffle"))
    rng.shuffle(records)
    return records


def validate_records(records: list[dict[str, Any]], split: str, per_cell: int) -> Counter:
    stats: Counter = Counter()
    for row in records:
        if row["split"] != split:
            raise ValueError(f"{row['id']}: split mismatch")
        hits = forbidden_hits(str(row["title"]), str(row["body"]))
        if hits:
            raise ValueError(f"{row['id']}: forbidden article terms: {hits}")
        if not Path(str(row["image"])).exists():
            raise FileNotFoundError(row["image"])
        target = row["target"]
        final = "fake_news" if target["image_verdict"] == "tampered" or target["text_image_relation"] == "mismatched" else "credible"
        if target["final_news_verdict"] != final:
            raise ValueError(f"{row['id']}: bad final_news_verdict")
        if target["image_verdict"] == "tampered" and not row.get("gt_mask"):
            raise ValueError(f"{row['id']}: missing FaceApp mask")
        if row["cell"] == "authentic_mismatched" and row["donor_source_key"] == row["source_key"]:
            raise ValueError(f"{row['id']}: donor equals target")
        stats[row["cell"]] += 1
    expected = {
        "authentic_consistent": per_cell,
        "authentic_mismatched": per_cell,
        "tampered_consistent": per_cell,
        "tampered_mismatched": per_cell,
    }
    if {key: stats[key] for key in expected} != expected:
        raise ValueError(f"{split}: cell counts {dict(stats)} != {expected}")
    return stats


def run(args: argparse.Namespace) -> None:
    caption_rows = load_jsonl(args.captions)
    for row in caption_rows:
        validate_caption(row)
    selected = select_by_label(caption_rows, args)
    args.output_root.mkdir(parents=True, exist_ok=True)

    split_counts = {
        "train": args.train_per_cell,
        "dev": args.dev_per_cell,
        "final": args.final_per_cell,
    }
    all_source_keys: dict[str, set[str]] = {}
    meta: dict[str, Any] = {
        "name": args.output_root.name,
        "caption_source": str(args.captions),
        "seed": args.seed,
        "forbidden_terms": sorted(FORBIDDEN_TERMS),
        "prompt_template": PROMPT,
        "splits": {},
    }
    for split, per_cell in split_counts.items():
        if per_cell < 1:
            continue
        records = build_split(split, selected[split], args.output_root, args.seed)
        stats = validate_records(records, split, per_cell)
        write_jsonl(args.output_root / f"{split}_raw.jsonl", records)
        all_source_keys[split] = {str(row["source_key"]) for row in records}
        meta["splits"][split] = {
            "raw_path": str(args.output_root / f"{split}_raw.jsonl"),
            "records": len(records),
            "per_cell": per_cell,
            "cell_counts": dict(stats),
            "unique_target_images": len(all_source_keys[split]),
        }

    split_names = sorted(all_source_keys)
    for i, left in enumerate(split_names):
        for right in split_names[i + 1 :]:
            overlap = all_source_keys[left] & all_source_keys[right]
            if overlap:
                raise ValueError(f"{left}/{right}: target image overlap: {sorted(overlap)[:5]}")

    (args.output_root / "dataset_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build controlled Stage2 DeepFake-news title/body/image pairs.")
    parser.add_argument("--captions", type=Path, default=Path("artifacts/stage2/deepfake_news_caption_pool/captions.jsonl"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/stage2/deepfake_news_pairs"))
    parser.add_argument("--train-per-cell", type=int, default=200)
    parser.add_argument("--dev-per-cell", type=int, default=50)
    parser.add_argument("--final-per-cell", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20260718)
    args = parser.parse_args()
    for name in ["train_per_cell", "dev_per_cell", "final_per_cell"]:
        if getattr(args, name) < 0:
            raise ValueError(f"--{name.replace('_', '-')} must be non-negative")
    return args


def main() -> None:
    args = parse_args()
    try:
        run(args)
    finally:
        close_archives()


if __name__ == "__main__":
    main()
