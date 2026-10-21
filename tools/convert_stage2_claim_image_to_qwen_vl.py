#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any


VALID_VERDICTS = {"authentic", "tampered", "misleading", "unknown"}
VALID_IMAGE_VERDICTS = {"authentic", "tampered", "unknown"}
VALID_TAMPER_DOMAINS = {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}
VALID_CONSISTENCY = {"supports", "contradicts", "unrelated", "insufficient"}
TARGET_KEYS = {
    "claim",
    "verdict",
    "visual_forensics",
    "claim_image_consistency",
    "final_reason",
}
VISUAL_KEYS = {"image_verdict", "tampered_region", "tamper_domain", "evidence"}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"line {line_no}: expected JSON object")
        rows.append(row)
    return rows


def normalize_text(value: Any, field: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field} must be a non-empty string")
    return text


def resolve_image(image: Any, image_root: Path) -> Path:
    image_text = normalize_text(image, "image")
    image_path = Path(image_text)
    if not image_path.is_absolute():
        image_path = image_root / image_path
    image_path = image_path.resolve()
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    return image_path


def build_target(row: dict[str, Any]) -> dict[str, Any]:
    if isinstance(row.get("target"), dict):
        target = dict(row["target"])
    else:
        target = {
            "claim": row.get("claim"),
            "verdict": row.get("verdict"),
            "visual_forensics": row.get("visual_forensics"),
            "claim_image_consistency": row.get("claim_image_consistency"),
            "final_reason": row.get("final_reason"),
        }
    if "claim" not in target or target.get("claim") is None:
        target["claim"] = row.get("claim")
    return validate_target(target)


def validate_target(target: dict[str, Any]) -> dict[str, Any]:
    if set(target) != TARGET_KEYS:
        raise ValueError(f"bad target keys: {sorted(target)}")

    claim = normalize_text(target["claim"], "target.claim")
    verdict = normalize_text(target["verdict"], "target.verdict").lower()
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"bad verdict: {verdict!r}")

    visual = target["visual_forensics"]
    if not isinstance(visual, dict) or set(visual) != VISUAL_KEYS:
        raise ValueError(f"bad visual_forensics keys: {sorted(visual) if isinstance(visual, dict) else visual!r}")
    image_verdict = normalize_text(visual["image_verdict"], "visual_forensics.image_verdict").lower()
    if image_verdict not in VALID_IMAGE_VERDICTS:
        raise ValueError(f"bad image_verdict: {image_verdict!r}")
    tamper_domain = normalize_text(visual["tamper_domain"], "visual_forensics.tamper_domain").lower()
    if tamper_domain not in VALID_TAMPER_DOMAINS:
        raise ValueError(f"bad tamper_domain: {tamper_domain!r}")
    tampered_region = str(visual["tampered_region"]).strip()
    evidence = visual["evidence"]
    if not isinstance(evidence, list) or len(evidence) > 5:
        raise ValueError("visual_forensics.evidence must be a list with at most 5 items")
    evidence = [normalize_text(item, "visual_forensics.evidence[]") for item in evidence]

    consistency = normalize_text(target["claim_image_consistency"], "claim_image_consistency").lower()
    if consistency not in VALID_CONSISTENCY:
        raise ValueError(f"bad claim_image_consistency: {consistency!r}")
    final_reason = normalize_text(target["final_reason"], "final_reason")

    return {
        "claim": claim,
        "verdict": verdict,
        "visual_forensics": {
            "image_verdict": image_verdict,
            "tampered_region": tampered_region,
            "tamper_domain": tamper_domain,
            "evidence": evidence,
        },
        "claim_image_consistency": consistency,
        "final_reason": final_reason,
    }


def prompt_for_claim(claim: str, visual_hint: Any | None) -> str:
    prompt = (
        "<image>\n"
        f"Claim: {claim}\n\n"
        "Analyze whether the image supports the claim and whether the image itself "
        "shows forensic signs of manipulation. Return only valid JSON with claim, "
        "verdict, visual_forensics, claim_image_consistency, and final_reason."
    )
    if visual_hint is not None:
        prompt += "\n\nUpstream visual-forensics hint: "
        prompt += json.dumps(visual_hint, ensure_ascii=False, sort_keys=True)
    return prompt


def copy_or_reference_image(image_path: Path, output_root: Path, copy_images: bool) -> Path:
    if not copy_images:
        return image_path

    dst = output_root / "images" / image_path.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(image_path, dst)
    return dst


def convert(
    input_path: Path,
    image_root: Path,
    output_root: Path,
    copy_images: bool,
    include_visual_hint: bool,
) -> Counter:
    rows = load_jsonl(input_path)
    output_root.mkdir(parents=True, exist_ok=True)
    output_jsonl = output_root / "llamafactory_qwen_vl_sft.jsonl"
    manifest_path = output_root / "manifest.jsonl"

    stats: Counter = Counter()
    with output_jsonl.open("w", encoding="utf-8") as out_f, manifest_path.open("w", encoding="utf-8") as manifest_f:
        for idx, row in enumerate(rows):
            target = build_target(row)
            image_path = resolve_image(row.get("image"), image_root)
            output_image = copy_or_reference_image(image_path, output_root, copy_images)
            visual_hint = row.get("visual_forensics_hint") if include_visual_hint else None

            record = {
                "id": row.get("id", f"stage2_{idx:06d}"),
                "images": [str(output_image)],
                "messages": [
                    {"role": "user", "content": prompt_for_claim(target["claim"], visual_hint)},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                ],
            }
            manifest = {
                "id": record["id"],
                "source": row.get("source", "unknown"),
                "image": str(output_image),
                "claim": target["claim"],
                "verdict": target["verdict"],
                "image_verdict": target["visual_forensics"]["image_verdict"],
                "tamper_domain": target["visual_forensics"]["tamper_domain"],
                "claim_image_consistency": target["claim_image_consistency"],
                "has_visual_hint": visual_hint is not None,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            manifest_f.write(json.dumps(manifest, ensure_ascii=False) + "\n")
            stats["total"] += 1
            stats[("verdict", target["verdict"])] += 1
            stats[("image_verdict", target["visual_forensics"]["image_verdict"])] += 1
            stats[("consistency", target["claim_image_consistency"])] += 1

    write_readme(output_root, input_path, image_root, stats, copy_images, include_visual_hint)
    validate_output(output_jsonl)
    return stats


def validate_output(path: Path) -> Counter:
    stats: Counter = Counter()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        images = row.get("images")
        messages = row.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"line {line_no}: expected exactly one image")
        if not Path(str(images[0])).exists():
            raise FileNotFoundError(f"line {line_no}: {images[0]}")
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"line {line_no}: expected user and assistant messages")
        user, assistant = messages
        if user.get("role") != "user" or assistant.get("role") != "assistant":
            raise ValueError(f"line {line_no}: bad message roles")
        if str(user.get("content", "")).count("<image>") != 1:
            raise ValueError(f"line {line_no}: image placeholder mismatch")
        target = json.loads(str(assistant.get("content", "")))
        validate_target(target)
        stats["total"] += 1
    return stats


def write_readme(
    output_root: Path,
    input_path: Path,
    image_root: Path,
    stats: Counter,
    copy_images: bool,
    include_visual_hint: bool,
) -> None:
    lines = [
        "# Stage2 Claim-Image JSON Data",
        "",
        "This directory contains LLaMA-Factory ShareGPT records for Stage2 fake-news",
        "claim-image fusion.",
        "",
        f"- input_path: `{input_path}`",
        f"- image_root: `{image_root}`",
        f"- copy_images: `{copy_images}`",
        f"- include_visual_hint: `{include_visual_hint}`",
        f"- total records: `{stats['total']}`",
        "",
        "Target schema: `schemas/stage2_claim_image_report.schema.json`.",
    ]
    (output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True, help="Raw Stage2 JSONL")
    parser.add_argument("--image-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage2_claim_image_json"))
    parser.add_argument("--copy-images", action="store_true")
    parser.add_argument("--include-visual-hint", action="store_true")
    args = parser.parse_args()

    stats = convert(args.input, args.image_root, args.output_root, args.copy_images, args.include_visual_hint)
    print("wrote", args.output_root)
    print(json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
