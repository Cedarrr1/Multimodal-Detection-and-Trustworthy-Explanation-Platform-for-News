#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROMPT = (
    "<image>\n"
    "Analyze whether this image has been digitally manipulated. "
    "Return only valid JSON with verdict, tampered_region, tamper_domain, and evidence."
)

DOMAIN_MAP = {
    "photoshop_edit": "photoshop",
    "deepfake_face": "deepfake",
    "aigc_edit": "aigc_inpaint",
}


def conversation_text(row: dict[str, Any], speaker: str) -> str:
    for turn in row.get("conversations", []):
        if turn.get("from") == speaker:
            return str(turn.get("value", "")).strip()
    raise ValueError(f"missing {speaker!r} conversation for row {row.get('id')!r}")


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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
    bullets: list[str] = []
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

    sentences = [
        clean_space(part)
        for part in re.split(r"(?<=[.!?])\s+", basis)
        if clean_space(part)
    ]
    return sentences[:max_items]


def load_manifest(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    manifest: dict[tuple[str, str], dict[str, Any]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        key = (str(row["id"]), str(row["image"]))
        if key in manifest:
            raise ValueError(f"duplicate manifest key at line {line_no}: {key}")
        manifest[key] = row
    return manifest


def convert(input_path: Path, manifest_path: Path, image_root: Path, output_path: Path) -> Counter:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    manifest = load_manifest(manifest_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats: Counter = Counter()
    with output_path.open("w", encoding="utf-8") as f:
        for row in data:
            key = (str(row["id"]), str(row["image"]))
            meta = manifest.get(key)
            if meta is None:
                raise KeyError(f"missing manifest row for {key}")

            image_path = image_root / row["image"]
            if not image_path.exists():
                raise FileNotFoundError(image_path)

            is_tampered = bool(meta["is_tampered"])
            source_domain = str(meta["domain"])
            verdict = "tampered" if is_tampered else "authentic"
            tamper_domain = DOMAIN_MAP.get(source_domain, "unknown") if is_tampered else "none"
            assistant_text = conversation_text(row, "gpt")
            target = {
                "verdict": verdict,
                "tampered_region": extract_region(assistant_text, is_tampered),
                "tamper_domain": tamper_domain,
                "evidence": extract_evidence(assistant_text),
            }

            record = {
                "id": row["id"],
                "images": [str(image_path)],
                "messages": [
                    {"role": "user", "content": PROMPT},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                ],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            stats[(source_domain, verdict)] += 1
            stats["total"] += 1

    return stats


def validate(path: Path) -> Counter:
    stats: Counter = Counter()
    required = {"verdict", "tampered_region", "tamper_domain", "evidence"}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        messages = row.get("messages")
        images = row.get("images")
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"line {line_no}: messages must contain user and assistant")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"line {line_no}: images must contain exactly one path")
        if not Path(images[0]).exists():
            raise FileNotFoundError(f"line {line_no}: {images[0]}")

        user, assistant = messages
        if user.get("role") != "user" or assistant.get("role") != "assistant":
            raise ValueError(f"line {line_no}: bad roles")
        user_content = str(user.get("content", ""))
        if user_content.count("<image>") != len(images):
            raise ValueError(f"line {line_no}: <image> placeholder mismatch")
        if any(token in user_content.lower() for token in ["photoshop", "deepfake", "aigc"]):
            raise ValueError(f"line {line_no}: user prompt leaks domain hint")

        target = json.loads(str(assistant.get("content", "")))
        if set(target) != required:
            raise ValueError(f"line {line_no}: bad target keys {sorted(target)}")
        if target["verdict"] not in {"authentic", "tampered"}:
            raise ValueError(f"line {line_no}: bad verdict {target['verdict']!r}")
        if target["tamper_domain"] not in {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}:
            raise ValueError(f"line {line_no}: bad tamper_domain {target['tamper_domain']!r}")
        if not isinstance(target["evidence"], list):
            raise ValueError(f"line {line_no}: evidence must be a list")
        if len(target["evidence"]) > 5:
            raise ValueError(f"line {line_no}: evidence has more than 5 items")

        stats["total"] += 1
        stats[("verdict", target["verdict"])] += 1
        stats[("domain", target["tamper_domain"])] += 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_p100/stage1_dte_sft.json"))
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_p100/manifest.jsonl"))
    parser.add_argument("--image-root", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_p100/images"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/lora_data/stage1_mmtd_p100_json/llamafactory_qwen_vl_sft.jsonl"),
    )
    args = parser.parse_args()

    stats = convert(args.input, args.manifest, args.image_root, args.output)
    validation = validate(args.output)
    print("wrote", args.output)
    print("convert_stats", json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))
    print("validate_stats", json.dumps({str(k): v for k, v in validation.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
