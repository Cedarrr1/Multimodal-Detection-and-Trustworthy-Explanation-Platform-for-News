#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


VALID_IMAGE_VERDICTS = {"authentic", "tampered"}
VALID_TAMPER_DOMAINS = {"none", "deepfake"}
VALID_RELATIONS = {"consistent", "mismatched"}
VALID_FINAL = {"credible", "fake_news"}
VALID_REGIONS = {"face", "none"}
TARGET_KEYS = {
    "image_verdict",
    "tamper_domain",
    "text_image_relation",
    "final_news_verdict",
    "forensic_region",
    "evidence",
}
OPTIONAL_MANIFEST_KEYS = [
    "donor_image_member",
    "caption",
    "donor_caption",
    "mismatch_score",
    "mismatch_reasons",
    "mismatch_fallback_reason",
    "target_attributes",
    "donor_attributes",
    "donor_specificity",
    "donor_generic",
    "donor_cosine_distance",
]

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


def normalize_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


def validate_target(target: dict[str, Any]) -> dict[str, Any]:
    if set(target) != TARGET_KEYS:
        raise ValueError(f"bad target keys: {sorted(target)}")
    image_verdict = normalize_text(target["image_verdict"], "image_verdict").lower()
    tamper_domain = normalize_text(target["tamper_domain"], "tamper_domain").lower()
    relation = normalize_text(target["text_image_relation"], "text_image_relation").lower()
    final = normalize_text(target["final_news_verdict"], "final_news_verdict").lower()
    region = normalize_text(target["forensic_region"], "forensic_region").lower()
    evidence = target["evidence"]
    if image_verdict not in VALID_IMAGE_VERDICTS:
        raise ValueError(f"bad image_verdict: {image_verdict}")
    if tamper_domain not in VALID_TAMPER_DOMAINS:
        raise ValueError(f"bad tamper_domain: {tamper_domain}")
    if relation not in VALID_RELATIONS:
        raise ValueError(f"bad text_image_relation: {relation}")
    if final not in VALID_FINAL:
        raise ValueError(f"bad final_news_verdict: {final}")
    if region not in VALID_REGIONS:
        raise ValueError(f"bad forensic_region: {region}")
    expected_final = "fake_news" if image_verdict == "tampered" or relation == "mismatched" else "credible"
    if final != expected_final:
        raise ValueError(f"final_news_verdict {final} violates fusion rule {expected_final}")
    expected_domain = "deepfake" if image_verdict == "tampered" else "none"
    if tamper_domain != expected_domain:
        raise ValueError(f"tamper_domain {tamper_domain} inconsistent with image_verdict {image_verdict}")
    expected_region = "face" if image_verdict == "tampered" else "none"
    if region != expected_region:
        raise ValueError(f"forensic_region {region} inconsistent with image_verdict {image_verdict}")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 5:
        raise ValueError("evidence must be a non-empty list with at most 5 items")
    return {
        "image_verdict": image_verdict,
        "tamper_domain": tamper_domain,
        "text_image_relation": relation,
        "final_news_verdict": final,
        "forensic_region": region,
        "evidence": [normalize_text(item, "evidence[]") for item in evidence],
    }


def resolve_path(value: Any, root: Path, field: str, required: bool = True) -> Path | None:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field} is required")
        return None
    path = Path(text)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if required and not path.exists():
        raise FileNotFoundError(path)
    if not required and not path.exists():
        return None
    return path


def copy_or_reference_image(row_id: str, image_path: Path, output_root: Path, copy_images: bool) -> Path:
    if not copy_images:
        return image_path
    suffix = image_path.suffix.lower() or ".jpg"
    dst = output_root / "images" / f"{row_id}{suffix}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(image_path, dst)
    return dst


def prompt_for(row: dict[str, Any]) -> str:
    prompt = str(row.get("prompt") or "").strip()
    if prompt:
        return prompt
    return PROMPT.format(title=normalize_text(row.get("title"), "title"), body=normalize_text(row.get("body"), "body"))


def convert(input_path: Path, image_root: Path, output_root: Path, copy_images: bool) -> Counter:
    rows = load_jsonl(input_path)
    output_root.mkdir(parents=True, exist_ok=True)
    output_jsonl = output_root / "llamafactory_qwen_vl_sft.jsonl"
    manifest_path = output_root / "manifest.jsonl"

    stats: Counter = Counter()
    with output_jsonl.open("w", encoding="utf-8") as out_f, manifest_path.open("w", encoding="utf-8") as manifest_f:
        for idx, row in enumerate(rows):
            row_id = normalize_text(row.get("id") or f"stage2_deepfake_news_{idx:06d}", "id")
            title = normalize_text(row.get("title"), "title")
            body = normalize_text(row.get("body"), "body")
            target = validate_target(dict(row.get("target") or {}))
            image_path = resolve_path(row.get("image"), image_root, "image")
            if image_path is None:
                raise ValueError("image is required")
            output_image = copy_or_reference_image(row_id, image_path, output_root, copy_images)
            gt_mask = resolve_path(row.get("gt_mask"), image_root, "gt_mask", required=False)

            record = {
                "id": row_id,
                "images": [str(output_image)],
                "messages": [
                    {"role": "user", "content": prompt_for(row)},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                ],
            }
            manifest = {
                "id": row_id,
                "split": row.get("split"),
                "cell": row.get("cell"),
                "source": row.get("source"),
                "source_split": row.get("source_split"),
                "source_key": row.get("source_key"),
                "donor_source_key": row.get("donor_source_key"),
                "image": str(output_image),
                "gt_mask": str(gt_mask) if gt_mask is not None else None,
                "title": title,
                "body": body,
                "image_verdict": target["image_verdict"],
                "tamper_domain": target["tamper_domain"],
                "text_image_relation": target["text_image_relation"],
                "final_news_verdict": target["final_news_verdict"],
                "forensic_region": target["forensic_region"],
                "target": target,
            }
            for key in OPTIONAL_MANIFEST_KEYS:
                if key in row:
                    manifest[key] = row.get(key)
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            manifest_f.write(json.dumps(manifest, ensure_ascii=False) + "\n")
            stats["total"] += 1
            stats[("cell", str(row.get("cell")))] += 1
            stats[("image_verdict", target["image_verdict"])] += 1
            stats[("text_image_relation", target["text_image_relation"])] += 1
            stats[("final_news_verdict", target["final_news_verdict"])] += 1

    write_readme(output_root, input_path, image_root, stats, copy_images)
    validate_output(output_jsonl, manifest_path)
    return stats


def validate_output(data_path: Path, manifest_path: Path) -> None:
    data_rows = load_jsonl(data_path)
    manifest_rows = load_jsonl(manifest_path)
    if len(data_rows) != len(manifest_rows):
        raise ValueError("data and manifest row counts differ")
    for idx, (row, manifest) in enumerate(zip(data_rows, manifest_rows)):
        images = row.get("images")
        messages = row.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: expected exactly one image")
        if not Path(str(images[0])).exists():
            raise FileNotFoundError(images[0])
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"row {idx}: expected user and assistant messages")
        if str(messages[0].get("content", "")).count("<image>") != 1:
            raise ValueError(f"row {idx}: expected one image placeholder")
        validate_target(json.loads(str(messages[1].get("content", ""))))
        if row["id"] != manifest["id"]:
            raise ValueError(f"row {idx}: id mismatch")


def write_readme(output_root: Path, input_path: Path, image_root: Path, stats: Counter, copy_images: bool) -> None:
    lines = [
        "# Stage2 DeepFake News JSON Data",
        "",
        "This directory contains LLaMA-Factory ShareGPT records for the controlled",
        "title/body/image DeepFake-news benchmark. It evaluates image manipulation",
        "and text-image consistency, not real-world news fact verification.",
        "",
        f"- input_path: `{input_path}`",
        f"- image_root: `{image_root}`",
        f"- copy_images: `{copy_images}`",
        f"- total records: `{stats['total']}`",
        "",
        "Target schema: `schemas/stage2_deepfake_news_report.schema.json`.",
    ]
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert raw Stage2 DeepFake-news pairs to Qwen-VL ShareGPT JSONL.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage2_deepfake_news_json"))
    parser.add_argument("--copy-images", action="store_true")
    args = parser.parse_args()

    stats = convert(args.input, args.image_root, args.output_root, args.copy_images)
    print("wrote", args.output_root)
    print(json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
