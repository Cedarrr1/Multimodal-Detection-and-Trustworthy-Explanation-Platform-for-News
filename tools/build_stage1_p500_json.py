#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import shutil
from collections import Counter, defaultdict
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


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row["id"]), str(row["image"])


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def infer_domain(image: str) -> str:
    if image.startswith("ps/"):
        return "photoshop_edit"
    if image.startswith("df/"):
        return "deepfake_face"
    if image.startswith("aigc_inpaint/"):
        return "aigc_edit"
    raise ValueError(f"cannot infer domain from image path: {image}")


def infer_is_tampered(image: str) -> bool:
    name = Path(image).name
    path = f"/{image}"
    if "/CASIA2_Au/" in path or "/Au/" in path or name.startswith("R_"):
        return False
    if "/CASIA2/" in path or "/Tp/" in path or name.startswith("F_"):
        return True
    raise ValueError(f"cannot infer tamper label from image path: {image}")


def validate_source(source_root: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    stage1_path = source_root / "stage1_dte_sft.json"
    manifest_path = source_root / "manifest.jsonl"
    image_root = source_root / "images"
    if not stage1_path.exists():
        raise FileNotFoundError(stage1_path)
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    if not image_root.exists():
        raise FileNotFoundError(image_root)

    stage1_rows = json.loads(stage1_path.read_text(encoding="utf-8"))
    manifest_rows = load_jsonl(manifest_path)
    manifest = {row_key(row): row for row in manifest_rows}
    if len(manifest) != len(manifest_rows):
        raise ValueError("manifest has duplicate (id, image) keys")
    for row in stage1_rows:
        key = row_key(row)
        if key not in manifest:
            raise KeyError(f"missing manifest for {key}")
        image_path = image_root / row["image"]
        if not image_path.exists():
            raise FileNotFoundError(image_path)
    return stage1_rows, manifest


def validate_json_source(source_json: Path, image_root: Path) -> tuple[list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    if not source_json.exists():
        raise FileNotFoundError(source_json)
    if not image_root.exists():
        raise FileNotFoundError(image_root)

    stage1_rows = json.loads(source_json.read_text(encoding="utf-8"))
    manifest = {}
    for row in stage1_rows:
        image = str(row["image"])
        key = row_key(row)
        manifest[key] = {
            "id": str(row["id"]),
            "image": image,
            "domain": infer_domain(image),
            "is_tampered": infer_is_tampered(image),
        }
    if len(manifest) != len(stage1_rows):
        raise ValueError("source JSON has duplicate (id, image) keys")
    return stage1_rows, manifest


def build_dataset(
    source_root: Path | None,
    source_json: Path | None,
    image_root: Path | None,
    output_root: Path,
    exclude_manifest: Path,
    per_label: int,
    seed: int,
) -> Counter:
    if source_json is not None:
        if image_root is None:
            raise ValueError("--image-root is required with --source-json")
        stage1_rows, manifest = validate_json_source(source_json, image_root)
        source_image_root = image_root
    elif source_root is not None:
        stage1_rows, manifest = validate_source(source_root)
        source_image_root = source_root / "images"
    else:
        raise ValueError("provide either --source-root or --source-json with --image-root")

    exclude = {row_key(row) for row in load_jsonl(exclude_manifest)}

    buckets: dict[tuple[str, bool], list[dict[str, Any]]] = defaultdict(list)
    missing_images: Counter = Counter()
    for row in stage1_rows:
        key = row_key(row)
        if key in exclude:
            continue
        meta = manifest[key]
        image_path = source_image_root / row["image"]
        if not image_path.exists():
            missing_images[(str(meta["domain"]), bool(meta["is_tampered"]))] += 1
            continue
        buckets[(str(meta["domain"]), bool(meta["is_tampered"]))].append(row)

    required_domains = ["photoshop_edit", "deepfake_face", "aigc_edit"]
    availability = Counter({str(k): len(v) for k, v in buckets.items()})
    missing = []
    for domain in required_domains:
        for is_tampered in [False, True]:
            count = len(buckets[(domain, is_tampered)])
            if count < per_label:
                missing.append(f"{domain} is_tampered={is_tampered}: need {per_label}, have {count}")
    if missing:
        details = "\n".join(missing)
        raise RuntimeError(
            "insufficient source samples with existing images after excluding eval set:\n"
            f"{details}\navailability={dict(availability)}\nmissing_images={dict(missing_images)}"
        )

    rng = random.Random(seed)
    selected = []
    for domain in required_domains:
        for is_tampered in [False, True]:
            group = list(buckets[(domain, is_tampered)])
            rng.shuffle(group)
            selected.extend(group[:per_label])

    stage1_out = output_root / "stage1_dte_sft.json"
    manifest_out = output_root / "manifest.jsonl"
    jsonl_out = output_root / "llamafactory_qwen_vl_sft.jsonl"
    image_out_root = output_root / "images"
    output_root.mkdir(parents=True, exist_ok=True)
    image_out_root.mkdir(parents=True, exist_ok=True)

    stats: Counter = Counter()
    with manifest_out.open("w", encoding="utf-8") as mf, jsonl_out.open("w", encoding="utf-8") as jf:
        for row in selected:
            key = row_key(row)
            meta = dict(manifest[key])
            is_tampered = bool(meta["is_tampered"])
            source_domain = str(meta["domain"])
            verdict = "tampered" if is_tampered else "authentic"
            tamper_domain = DOMAIN_MAP[source_domain] if is_tampered else "none"
            assistant_text = conversation_text(row, "gpt")
            target = {
                "verdict": verdict,
                "tampered_region": extract_region(assistant_text, is_tampered),
                "tamper_domain": tamper_domain,
                "evidence": extract_evidence(assistant_text),
            }

            src_image = source_image_root / row["image"]
            dst_image = image_out_root / row["image"]
            dst_image.parent.mkdir(parents=True, exist_ok=True)
            if not dst_image.exists():
                shutil.copy2(src_image, dst_image)

            record = {
                "id": row["id"],
                "images": [str(dst_image)],
                "messages": [
                    {"role": "user", "content": PROMPT},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                ],
            }
            jf.write(json.dumps(record, ensure_ascii=False) + "\n")
            mf.write(json.dumps(meta, ensure_ascii=False) + "\n")
            stats[(source_domain, verdict)] += 1
            stats["total"] += 1

    stage1_out.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    validate_output(output_root, expected_total=per_label * 2 * len(required_domains))
    return stats


def validate_output(output_root: Path, expected_total: int) -> None:
    rows = load_jsonl(output_root / "llamafactory_qwen_vl_sft.jsonl")
    manifest = load_jsonl(output_root / "manifest.jsonl")
    if len(rows) != expected_total:
        raise ValueError(f"jsonl rows {len(rows)} != expected {expected_total}")
    if len(manifest) != expected_total:
        raise ValueError(f"manifest rows {len(manifest)} != expected {expected_total}")
    for idx, row in enumerate(rows):
        images = row.get("images")
        messages = row.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: bad images")
        if not Path(images[0]).exists():
            raise FileNotFoundError(f"row {idx}: {images[0]}")
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"row {idx}: bad messages")
        if str(messages[0].get("content", "")).count("<image>") != 1:
            raise ValueError(f"row {idx}: bad image placeholder")
        target = json.loads(str(messages[1].get("content", "")))
        if set(target) != {"verdict", "tampered_region", "tamper_domain", "evidence"}:
            raise ValueError(f"row {idx}: bad target keys")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, help="Directory containing stage1_dte_sft.json, manifest.jsonl, images/")
    parser.add_argument("--source-json", type=Path, help="MMTD-Set-34k style JSON file with id/image/conversations")
    parser.add_argument("--image-root", type=Path, help="Image root for source-json image paths")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_p500_json"))
    parser.add_argument("--exclude-manifest", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"))
    parser.add_argument("--per-label", type=int, default=250)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    stats = build_dataset(
        args.source_root,
        args.source_json,
        args.image_root,
        args.output_root,
        args.exclude_manifest,
        args.per_label,
        args.seed,
    )
    print("wrote", args.output_root)
    print(json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
