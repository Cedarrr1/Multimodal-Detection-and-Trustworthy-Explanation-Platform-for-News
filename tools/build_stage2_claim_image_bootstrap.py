#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DOMAIN_MAP = {
    "photoshop_edit": "photoshop",
    "deepfake_face": "deepfake",
    "aigc_edit": "aigc_inpaint",
}

CLAIM = "The image is an authentic, unmanipulated photograph."


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


def build_target(row: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    is_tampered = bool(meta["is_tampered"])
    source_domain = str(meta["domain"])
    assistant_text = conversation_text(row, "gpt")
    image_verdict = "tampered" if is_tampered else "authentic"
    tamper_domain = DOMAIN_MAP.get(source_domain, "unknown") if is_tampered else "none"
    consistency = "contradicts" if is_tampered else "supports"
    verdict = "tampered" if is_tampered else "authentic"
    tampered_region = extract_region(assistant_text, is_tampered)
    evidence = extract_evidence(assistant_text)

    if is_tampered:
        final_reason = (
            "The claim says the image is unmanipulated, but visual forensics indicate "
            f"{tamper_domain} tampering in {tampered_region}."
        )
    else:
        final_reason = (
            "The image-level forensic evidence supports the claim that the image is "
            "authentic and unmanipulated."
        )

    return {
        "claim": CLAIM,
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


def select_rows(
    rows: list[dict[str, Any]],
    manifest: dict[tuple[str, str], dict[str, Any]],
    per_domain_label: int,
    seed: int,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    buckets: dict[tuple[str, bool], list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for row in rows:
        meta = manifest.get(row_key(row))
        if meta is None:
            raise KeyError(f"missing manifest row for {row_key(row)}")
        buckets[(str(meta["domain"]), bool(meta["is_tampered"]))].append((row, meta))

    rng = random.Random(seed)
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for domain in sorted({domain for domain, _ in buckets}):
        for is_tampered in (False, True):
            group = list(buckets[(domain, is_tampered)])
            if len(group) < per_domain_label:
                raise RuntimeError(
                    f"insufficient rows for {domain} is_tampered={is_tampered}: "
                    f"need {per_domain_label}, have {len(group)}"
                )
            rng.shuffle(group)
            selected.extend(group[:per_domain_label])

    rng.shuffle(selected)
    return selected


def build_dataset(source_root: Path, output_path: Path, per_domain_label: int, seed: int) -> Counter:
    rows, manifest = load_stage1(source_root)
    image_root = source_root / "images"
    if not image_root.exists():
        raise FileNotFoundError(image_root)

    selected = select_rows(rows, manifest, per_domain_label, seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats: Counter = Counter()
    with output_path.open("w", encoding="utf-8") as out_f:
        for row, meta in selected:
            image_path = image_root / str(row["image"])
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            target = build_target(row, meta)
            record = {
                "id": f"stage2_bootstrap_{row['id']}",
                "source": "stage1_bootstrap_from_mmtd",
                "image": str(image_path),
                "claim": target["claim"],
                "target": target,
                "bootstrap_note": (
                    "Synthetic Stage2 bootstrap item derived from Stage1 image-forensics "
                    "labels. Use for pipeline validation and warm-start experiments, not "
                    "as a substitute for real news claim-image data."
                ),
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            stats["total"] += 1
            stats[(str(meta["domain"]), bool(meta["is_tampered"]))] += 1
            stats[("verdict", target["verdict"])] += 1
            stats[("consistency", target["claim_image_consistency"])] += 1

    validate_output(output_path)
    return stats


def validate_output(path: Path) -> Counter:
    stats: Counter = Counter()
    required_target = {"claim", "verdict", "visual_forensics", "claim_image_consistency", "final_reason"}
    required_visual = {"image_verdict", "tampered_region", "tamper_domain", "evidence"}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        image = Path(str(row["image"]))
        if not image.exists():
            raise FileNotFoundError(f"line {line_no}: {image}")
        target = row.get("target")
        if not isinstance(target, dict) or set(target) != required_target:
            raise ValueError(f"line {line_no}: bad target keys")
        visual = target.get("visual_forensics")
        if not isinstance(visual, dict) or set(visual) != required_visual:
            raise ValueError(f"line {line_no}: bad visual_forensics keys")
        if target["verdict"] not in {"authentic", "tampered", "misleading", "unknown"}:
            raise ValueError(f"line {line_no}: bad verdict")
        if visual["image_verdict"] not in {"authentic", "tampered", "unknown"}:
            raise ValueError(f"line {line_no}: bad image_verdict")
        if visual["tamper_domain"] not in {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}:
            raise ValueError(f"line {line_no}: bad tamper_domain")
        if target["claim_image_consistency"] not in {"supports", "contradicts", "unrelated", "insufficient"}:
            raise ValueError(f"line {line_no}: bad consistency")
        if not isinstance(visual["evidence"], list) or len(visual["evidence"]) > 5:
            raise ValueError(f"line {line_no}: bad evidence")
        stats["total"] += 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path("artifacts/lora_data/stage1_mmtd_p500_json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/stage2/claim_image_bootstrap_raw.jsonl"))
    parser.add_argument("--per-domain-label", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.per_domain_label < 1:
        raise ValueError("--per-domain-label must be positive")

    stats = build_dataset(args.source_root, args.output, args.per_domain_label, args.seed)
    print("wrote", args.output)
    print(json.dumps({str(k): v for k, v in stats.items()}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
