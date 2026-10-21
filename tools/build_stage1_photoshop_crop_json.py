#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image


PROMPT = (
    "<image>\n"
    "<image>\n"
    "Analyze whether this image has been digitally manipulated. "
    "The first image is the full image and the second image is a deterministic "
    "region crop for closer inspection. Return only valid JSON with verdict, "
    "tampered_region, tamper_domain, evidence, and region_focus."
)

REQUIRED_TARGET_KEYS = {
    "verdict",
    "tampered_region",
    "tamper_domain",
    "evidence",
    "region_focus",
}


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["id"]), str(row["image"])


def conversation_text(row: dict[str, Any], speaker: str) -> str:
    for turn in row.get("conversations", []):
        if turn.get("from") == speaker:
            return str(turn.get("value", "")).strip()
    raise ValueError(f"missing {speaker!r} conversation for row {row.get('id')!r}")


def extract_region(assistant_text: str, is_tampered: bool) -> str:
    if not is_tampered:
        return "none"

    first_para = assistant_text.split("\n\n", 1)[0]
    if ":" in first_para:
        first_para = first_para.split(":", 1)[1]
    desc = clean_space(first_para)
    desc = re.sub(
        r"^The (?:picture|image) has been tampered with(?:,)?\s*",
        "",
        desc,
        flags=re.IGNORECASE,
    )
    desc = re.sub(r"^[\s,.;:]+", "", desc)
    desc = re.sub(r"^specifically\s+", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"^The tampered area is\s+", "", desc, flags=re.IGNORECASE)
    return desc or "unknown"


def extract_evidence(assistant_text: str, max_items: int = 5) -> list[str]:
    bullets = []
    for line in assistant_text.splitlines():
        stripped = line.strip()
        if re.match(r"^[-*]\s+", stripped):
            bullets.append(clean_space(re.sub(r"^[-*]\s+", "", stripped)))
    if bullets:
        return bullets[:max_items]

    basis = assistant_text
    match = re.search(r"2\.\s*Judgment basis\s*:\s*(.*)", assistant_text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        basis = match.group(1)
    return [clean_space(part) for part in re.split(r"(?<=[.!?])\s+", basis) if clean_space(part)][:max_items]


def load_stage1(source_root: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    stage1_path = source_root / "stage1_dte_sft.json"
    manifest_path = source_root / "manifest.jsonl"
    if not stage1_path.exists():
        raise FileNotFoundError(stage1_path)
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)

    rows = json.loads(stage1_path.read_text(encoding="utf-8"))
    manifest_rows = load_jsonl(manifest_path)
    manifest = {row_key(row): row for row in manifest_rows}
    if len(manifest) != len(manifest_rows):
        raise ValueError("manifest has duplicate (id, image) keys")
    return rows, manifest


def focus_candidates(region_text: str, is_tampered: bool) -> list[str]:
    if not is_tampered:
        return ["center_context", "wide_context"]

    lowered = region_text.lower()
    candidates: list[str] = []
    directional = [
        ("left", "left_region"),
        ("right", "right_region"),
        ("upper", "upper_region"),
        ("top", "upper_region"),
        ("lower", "lower_region"),
        ("bottom", "lower_region"),
        ("center", "center_region"),
        ("central", "center_region"),
        ("middle", "center_region"),
    ]
    for needle, focus in directional:
        if needle in lowered and focus not in candidates:
            candidates.append(focus)

    if "corner" in lowered:
        for focus in ("upper_left_region", "upper_right_region", "lower_left_region", "lower_right_region"):
            if focus not in candidates:
                candidates.append(focus)

    if not candidates:
        candidates.append("center_region")
    if "wide_context" not in candidates:
        candidates.append("wide_context")
    return candidates


def crop_box(width: int, height: int, focus: str, scale: float) -> tuple[int, int, int, int]:
    crop_w = max(1, min(width, round(width * scale)))
    crop_h = max(1, min(height, round(height * scale)))

    centers = {
        "center_context": (0.5, 0.5),
        "wide_context": (0.5, 0.5),
        "center_region": (0.5, 0.5),
        "left_region": (0.32, 0.5),
        "right_region": (0.68, 0.5),
        "upper_region": (0.5, 0.32),
        "lower_region": (0.5, 0.68),
        "upper_left_region": (0.32, 0.32),
        "upper_right_region": (0.68, 0.32),
        "lower_left_region": (0.32, 0.68),
        "lower_right_region": (0.68, 0.68),
    }
    cx_ratio, cy_ratio = centers.get(focus, (0.5, 0.5))
    cx = round(width * cx_ratio)
    cy = round(height * cy_ratio)
    left = min(max(0, cx - crop_w // 2), width - crop_w)
    top = min(max(0, cy - crop_h // 2), height - crop_h)
    return left, top, left + crop_w, top + crop_h


def safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")


def make_crop(src_image: Path, dst_image: Path, focus: str, scale: float) -> tuple[int, int, int, int]:
    with Image.open(src_image) as image:
        image = image.convert("RGB")
        box = crop_box(image.width, image.height, focus, scale)
        crop = image.crop(box)
        dst_image.parent.mkdir(parents=True, exist_ok=True)
        crop.save(dst_image, quality=95)
        return box


def copy_full_image(src_image: Path, dst_image: Path) -> None:
    dst_image.parent.mkdir(parents=True, exist_ok=True)
    if not dst_image.exists():
        shutil.copy2(src_image, dst_image)


def select_photoshop_rows(
    rows: list[dict[str, Any]],
    manifest: dict[tuple[str, str], dict[str, Any]],
    max_per_label: int | None,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    buckets: dict[bool, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for row in rows:
        meta = manifest.get(row_key(row))
        if meta is None:
            raise KeyError(f"missing manifest for {row_key(row)}")
        if meta.get("domain") != "photoshop_edit":
            continue
        buckets[bool(meta["is_tampered"])].append((row, meta))

    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for is_tampered in (False, True):
        group = buckets[is_tampered]
        if max_per_label is not None:
            group = group[:max_per_label]
        selected.extend(group)
    return selected


def build_dataset(
    source_root: Path,
    output_root: Path,
    crops_per_source: int,
    crop_scales: list[float],
    max_per_label: int | None,
) -> Counter:
    rows, manifest = load_stage1(source_root)
    source_image_root = source_root / "images"
    if not source_image_root.exists():
        raise FileNotFoundError(source_image_root)

    selected = select_photoshop_rows(rows, manifest, max_per_label)
    if not selected:
        raise RuntimeError("no photoshop_edit rows found in source dataset")

    output_root.mkdir(parents=True, exist_ok=True)
    image_root = output_root / "images"
    jsonl_path = output_root / "llamafactory_qwen_vl_sft.jsonl"
    manifest_path = output_root / "manifest.jsonl"

    stats: Counter = Counter()
    with jsonl_path.open("w", encoding="utf-8") as jf, manifest_path.open("w", encoding="utf-8") as mf:
        for row, meta in selected:
            src_image = source_image_root / row["image"]
            if not src_image.exists():
                raise FileNotFoundError(src_image)

            is_tampered = bool(meta["is_tampered"])
            verdict = "tampered" if is_tampered else "authentic"
            tamper_domain = "photoshop" if is_tampered else "none"
            assistant_text = conversation_text(row, "gpt")
            region_text = extract_region(assistant_text, is_tampered)
            evidence = extract_evidence(assistant_text)
            focuses = focus_candidates(region_text, is_tampered)

            full_image = image_root / "full" / row["image"]
            copy_full_image(src_image, full_image)

            emitted_for_row = 0
            for focus in focuses:
                for scale in crop_scales:
                    if emitted_for_row >= crops_per_source:
                        break
                    crop_rel = Path("crops") / f"{safe_name(str(row['id']))}_{focus}_{scale:.2f}.jpg"
                    crop_image = image_root / crop_rel
                    box = make_crop(src_image, crop_image, focus, scale)
                    region_focus = (
                        f"{focus} crop at scale {scale:.2f}; full image is provided as context. "
                        f"Region supervision: {region_text}"
                    )
                    target = {
                        "verdict": verdict,
                        "tampered_region": region_text,
                        "tamper_domain": tamper_domain,
                        "evidence": evidence,
                        "region_focus": region_focus,
                    }
                    record = {
                        "messages": [
                            {"role": "user", "content": PROMPT},
                            {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                        ],
                        "images": [str(full_image), str(crop_image)],
                    }
                    out_meta = {
                        "source_id": str(row["id"]),
                        "source_image": str(row["image"]),
                        "full_image": str(full_image),
                        "crop_image": str(crop_image),
                        "crop_box_xyxy": list(box),
                        "crop_focus": focus,
                        "crop_scale": scale,
                        "domain": "photoshop_edit",
                        "is_tampered": is_tampered,
                        "region_text": region_text,
                    }
                    jf.write(json.dumps(record, ensure_ascii=False) + "\n")
                    mf.write(json.dumps(out_meta, ensure_ascii=False) + "\n")
                    stats[(verdict, focus)] += 1
                    stats[verdict] += 1
                    stats["total"] += 1
                    emitted_for_row += 1
                if emitted_for_row >= crops_per_source:
                    break

    write_readme(output_root, source_root, stats, crops_per_source, crop_scales, max_per_label)
    validate_output(output_root)
    return stats


def validate_output(output_root: Path) -> Counter:
    stats: Counter = Counter()
    rows = load_jsonl(output_root / "llamafactory_qwen_vl_sft.jsonl")
    manifest = load_jsonl(output_root / "manifest.jsonl")
    if len(rows) != len(manifest):
        raise ValueError(f"jsonl rows {len(rows)} != manifest rows {len(manifest)}")
    for idx, row in enumerate(rows):
        images = row.get("images")
        messages = row.get("messages")
        if not isinstance(images, list) or len(images) != 2:
            raise ValueError(f"row {idx}: expected full image and crop image")
        for image in images:
            if not Path(str(image)).exists():
                raise FileNotFoundError(f"row {idx}: {image}")
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"row {idx}: messages must contain user and assistant")
        if str(messages[0].get("content", "")).count("<image>") != 2:
            raise ValueError(f"row {idx}: prompt/image placeholder mismatch")
        target = json.loads(str(messages[1].get("content", "")))
        if set(target) != REQUIRED_TARGET_KEYS:
            raise ValueError(f"row {idx}: bad target keys {sorted(target)}")
        if target["verdict"] not in {"authentic", "tampered"}:
            raise ValueError(f"row {idx}: bad verdict {target['verdict']!r}")
        if target["tamper_domain"] not in {"photoshop", "none"}:
            raise ValueError(f"row {idx}: bad tamper_domain {target['tamper_domain']!r}")
        if not isinstance(target["evidence"], list):
            raise ValueError(f"row {idx}: evidence must be a list")
        stats[target["verdict"]] += 1
        stats["total"] += 1
    return stats


def write_readme(
    output_root: Path,
    source_root: Path,
    stats: Counter,
    crops_per_source: int,
    crop_scales: list[float],
    max_per_label: int | None,
) -> None:
    lines = [
        "# Stage1 Photoshop Crop JSON Data",
        "",
        "This dataset is a weakly supervised Photoshop-localization enhancement set.",
        "Each training record contains two images: the full image and a deterministic crop.",
        "The crop is guided by region text heuristics when available, not by a ground-truth mask.",
        "",
        f"- source_root: `{source_root}`",
        f"- crops_per_source: `{crops_per_source}`",
        f"- crop_scales: `{','.join(f'{scale:.2f}' for scale in crop_scales)}`",
        f"- max_per_label: `{max_per_label}`",
        f"- total records: `{stats['total']}`",
        f"- authentic records: `{stats['authentic']}`",
        f"- tampered records: `{stats['tampered']}`",
        "",
        "Use this as a focused follow-up experiment for Photoshop recall. It should not be treated",
        "as true pixel-level localization supervision unless real masks/bboxes are added later.",
    ]
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_scales(raw: str) -> list[float]:
    scales = [float(part.strip()) for part in raw.split(",") if part.strip()]
    if not scales:
        raise ValueError("at least one crop scale is required")
    for scale in scales:
        if not 0.1 <= scale <= 1.0:
            raise ValueError(f"crop scale must be in [0.1, 1.0], got {scale}")
    return scales


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_p500_json"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage1_photoshop_crop_json"))
    parser.add_argument("--crops-per-source", type=int, default=2)
    parser.add_argument("--crop-scales", default="0.70,0.45")
    parser.add_argument("--max-per-label", type=int, help="Optional smoke-test cap per authentic/tampered label")
    args = parser.parse_args()

    if args.crops_per_source < 1:
        raise ValueError("--crops-per-source must be positive")

    stats = build_dataset(
        args.source_root,
        args.output_root,
        args.crops_per_source,
        parse_scales(args.crop_scales),
        args.max_per_label,
    )
    print("wrote", args.output_root)
    print(json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
