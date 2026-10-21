#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

from build_stage2_deepfake_news_pairs import (
    close_archives,
    cosine_distance,
    forbidden_hits,
    image_vector,
    load_jsonl,
    normalize_label,
    prepare_media,
    select_by_label,
    stable_int,
    target_for,
    validate_caption,
    write_jsonl,
)
from generate_stage2_deepfake_captions_qwen_vl import FORBIDDEN_TERMS


PROMPT_V2 = (
    "<image>\n"
    "Title: {title}\n"
    "Body: {body}\n\n"
    "Determine whether the image is digitally manipulated and whether the title "
    "and body match the visible image. This is a controlled text-image "
    "consistency benchmark, not real-world news fact checking. Return only "
    "valid compact JSON with exactly these keys: image_verdict, tamper_domain, "
    "text_image_relation, final_news_verdict, forensic_region, and evidence. "
    "Do not output labels outside the listed enum values. "
    'Use image_verdict "authentic" or "tampered"; tamper_domain "none" or '
    '"deepfake"; text_image_relation "consistent" or "mismatched"; '
    'final_news_verdict "credible" or "fake_news"; forensic_region "face" or "none".'
)


ATTRIBUTE_PATTERNS: dict[str, dict[str, list[str]]] = {
    "gender": {
        "woman": [r"\bwoman\b", r"\bfemale\b", r"\bgirl\b", r"\blady\b"],
        "man": [r"\bman\b", r"\bmale\b", r"\bboy\b", r"\bgentleman\b"],
    },
    "age": {
        "child": [r"\bchild\b", r"\bkid\b", r"\bbaby\b", r"\btoddler\b"],
        "young": [r"\byoung\b"],
        "older": [r"\bolder\b", r"\belderly\b", r"\bgray-haired\b", r"\bgrey-haired\b"],
    },
    "hair_color": {
        "blonde": [r"\bblonde hair\b", r"\bblond hair\b", r"\bblonde\b", r"\bblond\b"],
        "dark": [r"\bdark hair\b", r"\bblack hair\b"],
        "brown": [r"\bbrown hair\b", r"\blight brown hair\b"],
        "red": [r"\bred hair\b", r"\bred-haired\b"],
        "gray": [r"\bgray hair\b", r"\bgrey hair\b", r"\bsilver hair\b"],
        "white": [r"\bwhite hair\b"],
    },
    "hair_length": {
        "long": [r"\blong hair\b", r"\blong, straight\b"],
        "short": [r"\bshort hair\b"],
        "bald": [r"\bbald\b", r"\bshaved head\b"],
    },
    "eyewear": {
        "glasses": [r"\bglasses\b", r"\bspectacles\b"],
        "sunglasses": [r"\bsunglasses\b"],
    },
    "facial_hair": {
        "beard": [r"\bbeard\b", r"\bbearded\b"],
        "mustache": [r"\bmustache\b", r"\bmoustache\b"],
    },
    "headwear": {
        "hat": [r"\bhat\b"],
        "cap": [r"\bcap\b"],
        "headscarf": [r"\bheadscarf\b", r"\bhead scarf\b", r"\bhijab\b"],
        "hood": [r"\bhood\b", r"\bhoodie\b"],
    },
    "expression": {
        "smiling": [r"\bsmil(?:e|es|ing)\b"],
        "neutral": [r"\bneutral expression\b", r"\bserious expression\b", r"\bnot smiling\b"],
    },
    "clothing_color": {
        "white": [r"\bwhite (?:shirt|top|garment|clothing|jacket|suit)\b"],
        "black": [r"\bblack (?:shirt|top|garment|clothing|jacket|suit)\b"],
        "blue": [r"\bblue (?:shirt|top|garment|clothing|jacket|suit)\b"],
        "red": [r"\bred (?:shirt|top|garment|clothing|jacket|suit)\b"],
        "dark": [r"\bdark(?:-colored)? (?:shirt|top|garment|clothing|jacket|suit)\b"],
        "light": [r"\blight(?:-colored)? (?:shirt|top|garment|clothing|jacket|suit)\b"],
    },
    "clothing_item": {
        "suit": [r"\bsuit\b"],
        "jacket": [r"\bjacket\b"],
        "shirt": [r"\bshirt\b"],
        "tie": [r"\btie\b"],
    },
    "background": {
        "outdoor": [r"\boutdoor\b", r"\boutdoors\b", r"\boutside\b"],
        "indoor": [r"\bindoor\b", r"\bindoors\b"],
        "blue": [r"\bblue background\b"],
        "light": [r"\blight background\b"],
        "dark": [r"\bdark background\b"],
        "blurred": [r"\bblurred background\b"],
    },
    "makeup": {
        "lipstick": [r"\blipstick\b", r"\bred lip\b", r"\bred lips\b"],
        "face_paint": [r"\bface paint\b", r"\bpainted face\b"],
    },
    "object": {
        "microphone": [r"\bmicrophone\b"],
        "earrings": [r"\bearrings?\b"],
    },
}

DISTINCTIVE_ABSENT_CATEGORIES = {
    "eyewear",
    "facial_hair",
    "headwear",
    "clothing_item",
    "makeup",
    "object",
}

GENERIC_TEXTS = {
    "a close-up of a person's face",
    "close-up of a person's face",
    "a close-up portrait",
    "close-up portrait",
    "portrait close-up",
    "portrait of a person",
    "portrait released alongside a community event update",
}


def text_for_attributes(row: dict[str, Any]) -> str:
    return " ".join(str(row.get(key) or "") for key in ["title", "body", "caption"]).lower()


def attribute_values(row: dict[str, Any]) -> dict[str, set[str]]:
    text = text_for_attributes(row)
    attrs: dict[str, set[str]] = {}
    for category, values in ATTRIBUTE_PATTERNS.items():
        hits: set[str] = set()
        for value, patterns in values.items():
            if any(re.search(pattern, text) for pattern in patterns):
                hits.add(value)
        if hits:
            attrs[category] = hits
    return attrs


def compact_attrs(attrs: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(values) for key, values in sorted(attrs.items())}


def specificity_score(attrs: dict[str, set[str]]) -> int:
    return sum(len(values) for values in attrs.values())


def is_generic_text(row: dict[str, Any], attrs: dict[str, set[str]]) -> bool:
    title = str(row.get("title") or "").strip().lower()
    caption = str(row.get("caption") or "").strip().lower()
    body = str(row.get("body") or "").strip().lower()
    if title in GENERIC_TEXTS or caption in GENERIC_TEXTS:
        return specificity_score(attrs) < 2
    if "person's face" in body and specificity_score(attrs) < 2:
        return True
    return specificity_score(attrs) < 1


def mismatch_score(target_attrs: dict[str, set[str]], donor_attrs: dict[str, set[str]]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    for category, donor_values in sorted(donor_attrs.items()):
        target_values = target_attrs.get(category, set())
        if target_values and donor_values.isdisjoint(target_values):
            score += 2
            reasons.append(
                f"{category} conflict: image={','.join(sorted(target_values))}; text={','.join(sorted(donor_values))}"
            )
        elif category in DISTINCTIVE_ABSENT_CATEGORIES:
            absent = donor_values - target_values
            if absent:
                score += len(absent)
                reasons.append(f"text mentions {category}={','.join(sorted(absent))} not found in image caption")
    return score, reasons


def build_donor_map_v2(
    rows: list[dict[str, Any]],
    seed: int,
    min_mismatch_score: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    vectors = {str(row["source_key"]): image_vector(Path(str(row["image"]))) for row in rows}
    attrs = {str(row["source_key"]): attribute_values(row) for row in rows}
    generic = {str(row["source_key"]): is_generic_text(row, attrs[str(row["source_key"])]) for row in rows}
    rng = random.Random(seed)
    donor_map: dict[str, dict[str, Any]] = {}
    diagnostics: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row["source_key"])
        candidates = [candidate for candidate in rows if str(candidate["source_key"]) != key]
        rng.shuffle(candidates)
        ranked = []
        for candidate in candidates:
            donor_key = str(candidate["source_key"])
            score, reasons = mismatch_score(attrs[key], attrs[donor_key])
            distance = cosine_distance(vectors[key], vectors[donor_key])
            donor_specificity = specificity_score(attrs[donor_key])
            usable = score >= min_mismatch_score and not generic[donor_key]
            ranked.append((usable, score, donor_specificity, distance, donor_key, candidate, reasons))
        if not ranked:
            raise RuntimeError("cannot build mismatched pairs with fewer than two images")
        ranked.sort(key=lambda item: (item[0], item[1], item[2], item[3]), reverse=True)
        usable, score, donor_specificity, distance, donor_key, donor, reasons = ranked[0]
        fallback_reason = None
        if score < min_mismatch_score:
            fallback_reason = "below_min_mismatch_score"
        elif generic[donor_key]:
            fallback_reason = "generic_donor_used"
        donor_map[key] = donor
        diagnostics[key] = {
            "mismatch_score": score,
            "mismatch_reasons": reasons,
            "fallback_reason": fallback_reason,
            "target_attributes": compact_attrs(attrs[key]),
            "donor_attributes": compact_attrs(attrs[donor_key]),
            "donor_specificity": donor_specificity,
            "donor_generic": generic[donor_key],
            "donor_cosine_distance": distance,
        }
    return donor_map, diagnostics


def build_split_v2(
    split: str,
    selected: dict[str, list[dict[str, Any]]],
    output_root: Path,
    seed: int,
    min_mismatch_score: int,
) -> list[dict[str, Any]]:
    source_rows = selected["authentic"] + selected["tampered"]
    donor_map, diagnostics = build_donor_map_v2(source_rows, stable_int(seed, split, "donors_v2"), min_mismatch_score)
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
            record_id = f"stage2_deepfake_news_v2_{split}_{cell}_{idx:04d}"
            mismatch_diag = diagnostics[source_key] if relation == "mismatched" else {}
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
                "mismatch_score": int(mismatch_diag.get("mismatch_score", 0)),
                "mismatch_reasons": mismatch_diag.get("mismatch_reasons", []),
                "mismatch_fallback_reason": mismatch_diag.get("fallback_reason"),
                "target_attributes": mismatch_diag.get("target_attributes", compact_attrs(attribute_values(row))),
                "donor_attributes": mismatch_diag.get("donor_attributes") if relation == "mismatched" else None,
                "donor_specificity": mismatch_diag.get("donor_specificity") if relation == "mismatched" else None,
                "donor_generic": mismatch_diag.get("donor_generic") if relation == "mismatched" else None,
                "donor_cosine_distance": mismatch_diag.get("donor_cosine_distance") if relation == "mismatched" else None,
                "image": media["image"],
                "image_rel": media["image_rel"],
                "gt_mask": media["gt_mask"],
                "gt_mask_rel": media["gt_mask_rel"],
                "image_width": media["image_width"],
                "image_height": media["image_height"],
                "target": target,
                "prompt": PROMPT_V2.format(title=text_row["title"], body=text_row["body"]),
            }
            records.append(record)
    rng = random.Random(stable_int(seed, split, "shuffle_v2"))
    rng.shuffle(records)
    return records


def validate_records_v2(records: list[dict[str, Any]], split: str, per_cell: int) -> Counter:
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
        if row["cell"].endswith("_mismatched") and row["donor_source_key"] == row["source_key"]:
            raise ValueError(f"{row['id']}: donor equals target")
        stats[row["cell"]] += 1
        if row["cell"].endswith("_mismatched"):
            stats[("mismatch_score", int(row["mismatch_score"]))] += 1
            if row.get("mismatch_fallback_reason"):
                stats[("mismatch_fallback", str(row["mismatch_fallback_reason"]))] += 1
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
        "min_mismatch_score": args.min_mismatch_score,
        "forbidden_terms": sorted(FORBIDDEN_TERMS),
        "prompt_template": PROMPT_V2,
        "splits": {},
    }
    for split, per_cell in split_counts.items():
        if per_cell < 1:
            continue
        records = build_split_v2(split, selected[split], args.output_root, args.seed, args.min_mismatch_score)
        stats = validate_records_v2(records, split, per_cell)
        write_jsonl(args.output_root / f"{split}_raw.jsonl", records)
        all_source_keys[split] = {str(row["source_key"]) for row in records}
        mismatch_scores = [int(row["mismatch_score"]) for row in records if row["cell"].endswith("_mismatched")]
        fallback_counts = Counter(str(row.get("mismatch_fallback_reason")) for row in records if row.get("mismatch_fallback_reason"))
        meta["splits"][split] = {
            "raw_path": str(args.output_root / f"{split}_raw.jsonl"),
            "records": len(records),
            "per_cell": per_cell,
            "cell_counts": {str(key): value for key, value in stats.items() if isinstance(key, str)},
            "unique_target_images": len(all_source_keys[split]),
            "mismatch_score_min": min(mismatch_scores) if mismatch_scores else None,
            "mismatch_score_mean": sum(mismatch_scores) / len(mismatch_scores) if mismatch_scores else None,
            "mismatch_score_histogram": {
                str(key): stats[key] for key in sorted(k for k in stats if isinstance(k, tuple) and k[0] == "mismatch_score")
            },
            "mismatch_fallback_counts": dict(fallback_counts),
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
    parser = argparse.ArgumentParser(description="Build Stage2 v2 DeepFake-news pairs with attribute-strong mismatches.")
    parser.add_argument("--captions", type=Path, default=Path("artifacts/stage2/deepfake_news_caption_pool/captions.jsonl"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/stage2/deepfake_news_pairs_v2"))
    parser.add_argument("--train-per-cell", type=int, default=200)
    parser.add_argument("--dev-per-cell", type=int, default=50)
    parser.add_argument("--final-per-cell", type=int, default=100)
    parser.add_argument("--min-mismatch-score", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260719)
    args = parser.parse_args()
    for name in ["train_per_cell", "dev_per_cell", "final_per_cell", "min_mismatch_score"]:
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
