#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_stage2_deepfake_news_pairs import load_jsonl, stable_int, write_jsonl
from build_stage2_deepfake_news_pairs_v2 import attribute_values


RELATIONS = {"supports", "contradicts", "unrelated", "insufficient"}
VERIFIABILITY = {"verifiable", "not_verifiable"}
EVIDENCE_ATTRIBUTES = {
    "person",
    "gender",
    "age",
    "eyewear",
    "facial_hair",
    "hair_color",
    "hair_length",
    "headwear",
    "clothing",
    "color",
    "object",
    "count",
    "scene",
    "background",
    "action",
    "expression",
    "ocr",
    "spatial",
    "identity",
    "time",
    "causality",
    "event_truth",
    "viewpoint",
}


def clean_text(value: Any, field: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


def split_body_claims(title: str, body: str) -> list[str]:
    text = f"{title}. {body}"
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    claims = []
    seen = set()
    for part in parts:
        claim = part.strip()
        if not claim or claim.lower() in seen:
            continue
        seen.add(claim.lower())
        claims.append(claim)
    return claims or [body]


def claim(
    claim_id: str,
    text: str,
    relation: str,
    evidence: list[str],
    attrs: list[str],
    verifiability: str | None = None,
) -> dict[str, Any]:
    relation = relation.lower()
    if relation not in RELATIONS:
        raise ValueError(f"bad relation: {relation}")
    if verifiability is None:
        verifiability = "not_verifiable" if relation == "insufficient" else "verifiable"
    if verifiability not in VERIFIABILITY:
        raise ValueError(f"bad visual_verifiability: {verifiability}")
    attr_values = sorted({item for item in attrs if item in EVIDENCE_ATTRIBUTES})
    if not attr_values:
        attr_values = ["scene"] if relation == "unrelated" else ["person"]
    return {
        "claim_id": claim_id,
        "claim": clean_text(text, "claim"),
        "visual_verifiability": verifiability,
        "relation": relation,
        "visual_evidence": [clean_text(item, "visual_evidence[]") for item in evidence][:5],
        "evidence_attributes": attr_values[:8],
    }


def aggregate_relation(claims: list[dict[str, Any]]) -> str:
    relations = [str(item["relation"]).lower() for item in claims]
    verifiable = [item for item in claims if item["visual_verifiability"] == "verifiable"]
    if any(relation == "unrelated" for relation in relations):
        return "unrelated"
    if any(relation == "contradicts" for relation in relations):
        return "contradicts"
    if not verifiable or all(relation == "insufficient" for relation in relations):
        return "insufficient"
    if all(relation == "supports" for relation in relations if relation != "insufficient"):
        return "supports"
    raise ValueError(f"cannot aggregate relations: {relations}")


def target_for(claims: list[dict[str, Any]]) -> dict[str, Any]:
    target = {"claims": claims, "overall_relation": aggregate_relation(claims)}
    validate_target(target)
    return target


def validate_target(target: dict[str, Any]) -> dict[str, Any]:
    if set(target) != {"claims", "overall_relation"}:
        raise ValueError(f"bad target keys: {sorted(target)}")
    claims = target["claims"]
    if not isinstance(claims, list) or not claims:
        raise ValueError("target.claims must be a non-empty list")
    seen = set()
    normalized_claims = []
    for idx, item in enumerate(claims, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"claim {idx}: expected object")
        if set(item) != {
            "claim_id",
            "claim",
            "visual_verifiability",
            "relation",
            "visual_evidence",
            "evidence_attributes",
        }:
            raise ValueError(f"claim {idx}: bad keys {sorted(item)}")
        claim_id = clean_text(item["claim_id"], "claim_id")
        if claim_id in seen:
            raise ValueError(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        relation = clean_text(item["relation"], "relation").lower()
        verifiability = clean_text(item["visual_verifiability"], "visual_verifiability").lower()
        if relation not in RELATIONS:
            raise ValueError(f"bad claim relation: {relation}")
        if verifiability not in VERIFIABILITY:
            raise ValueError(f"bad visual_verifiability: {verifiability}")
        evidence = item["visual_evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 5:
            raise ValueError("visual_evidence must contain 1-5 items")
        attrs = item["evidence_attributes"]
        if not isinstance(attrs, list) or not 1 <= len(attrs) <= 8:
            raise ValueError("evidence_attributes must contain 1-8 items")
        bad_attrs = sorted(set(str(attr) for attr in attrs) - EVIDENCE_ATTRIBUTES)
        if bad_attrs:
            raise ValueError(f"bad evidence_attributes: {bad_attrs}")
        if relation == "insufficient" and verifiability != "not_verifiable":
            raise ValueError("insufficient claims must be not_verifiable")
        if relation in {"supports", "contradicts", "unrelated"} and verifiability != "verifiable":
            raise ValueError(f"{relation} claims must be verifiable")
        normalized_claims.append(
            {
                "claim_id": claim_id,
                "claim": clean_text(item["claim"], "claim"),
                "visual_verifiability": verifiability,
                "relation": relation,
                "visual_evidence": [clean_text(value, "visual_evidence[]") for value in evidence],
                "evidence_attributes": [clean_text(value, "evidence_attributes[]").lower() for value in attrs],
            }
        )
    overall = clean_text(target["overall_relation"], "overall_relation").lower()
    expected = aggregate_relation(normalized_claims)
    if overall != expected:
        raise ValueError(f"overall_relation {overall} violates aggregation rule {expected}")
    return {"claims": normalized_claims, "overall_relation": overall}


def prompt_for(claims: list[dict[str, Any]]) -> str:
    claim_lines = "\n".join(f'{item["claim_id"]}: {item["claim"]}' for item in claims)
    return (
        "<image>\n"
        "Claims:\n"
        f"{claim_lines}\n\n"
        "For each claim, judge only whether the visible image supports the claim, "
        "contradicts it, is unrelated to it, or is insufficient to verify it. "
        "Do not decide whether the image is digitally manipulated. This is a "
        "controlled text-image relation benchmark, not real-world news fact "
        "checking. Return only compact JSON with exactly these keys: claims and "
        "overall_relation. Each claim must contain claim_id, claim, "
        "visual_verifiability, relation, visual_evidence, and evidence_attributes. "
        'Use relation "supports", "contradicts", "unrelated", or "insufficient"; '
        'use visual_verifiability "verifiable" or "not_verifiable".'
    )


def source_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("source_key") or row.get("image"))
        if key not in by_key or str(row.get("cell", "")).endswith("_consistent"):
            by_key[key] = row
    return list(by_key.values())


def mismatched_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in rows:
        if str(row.get("cell", "")).endswith("_mismatched"):
            out[str(row.get("source_key") or row.get("image"))] = row
    return out


def easy_record(row: dict[str, Any], split: str, index: int) -> dict[str, Any]:
    v2_relation = str(row["target"]["text_image_relation"]).lower()
    if v2_relation == "consistent":
        relation = "supports"
        claims = [
            claim(
                "C1",
                split_body_claims(str(row["title"]), str(row["body"]))[-1],
                relation,
                ["The visible portrait matches the paired title and body description."],
                ["person", "scene"],
            )
        ]
        case_type = "easy_v2_supports"
    elif v2_relation == "mismatched":
        reasons = row.get("mismatch_reasons") or []
        evidence = [str(item) for item in reasons[:3]] or [
            "The paired text was selected from a different portrait with visible attribute conflicts."
        ]
        claims = [
            claim(
                "C1",
                split_body_claims(str(row["title"]), str(row["body"]))[-1],
                "contradicts",
                evidence,
                attrs_from_reasons(evidence),
            )
        ]
        case_type = "easy_v2_contradicts"
    else:
        raise ValueError(f"{row.get('id')}: bad v2 relation {v2_relation}")
    target = target_for(claims)
    return base_record(row, split, f"stage2_relation_v3_{split}_easy_{index:04d}", case_type, "easy", target)


def attrs_from_reasons(reasons: list[str]) -> list[str]:
    text = " ".join(reasons).lower()
    attrs = []
    for key in [
        "gender",
        "age",
        "eyewear",
        "facial_hair",
        "hair_color",
        "hair_length",
        "headwear",
        "object",
        "background",
        "expression",
    ]:
        if key in text:
            attrs.append(key)
    if "clothing" in text:
        attrs.extend(["clothing", "color"])
    return attrs or ["person"]


def base_record(
    row: dict[str, Any],
    split: str,
    record_id: str,
    case_type: str,
    difficulty: str,
    target: dict[str, Any],
    pair_id: str | None = None,
    pair_role: str | None = None,
) -> dict[str, Any]:
    claims = target["claims"]
    record = {
        "id": record_id,
        "split": split,
        "source": row.get("source"),
        "source_split": row.get("source_split"),
        "source_key": row.get("source_key"),
        "group_id": group_id(row),
        "image": row["image"],
        "image_rel": row.get("image_rel"),
        "image_verdict": row.get("target", {}).get("image_verdict"),
        "tamper_domain": row.get("target", {}).get("tamper_domain"),
        "forensic_region": row.get("target", {}).get("forensic_region"),
        "gt_mask": row.get("gt_mask"),
        "gt_mask_rel": row.get("gt_mask_rel"),
        "title": row.get("title"),
        "body": row.get("body"),
        "caption": row.get("caption"),
        "case_type": case_type,
        "difficulty": difficulty,
        "claims": claims,
        "overall_relation": target["overall_relation"],
        "target": target,
        "prompt": prompt_for(claims),
    }
    if pair_id is not None:
        record["counterfactual_pair_id"] = pair_id
    if pair_role is not None:
        record["counterfactual_pair_role"] = pair_role
    return record


def group_id(row: dict[str, Any]) -> str:
    source_key = str(row.get("source_key") or "").strip()
    if source_key:
        return source_key
    member = str(row.get("image_member") or "").strip()
    if member:
        return member
    return str(row["image"])


def support_case(row: dict[str, Any], split: str, index: int, pair_id: str | None) -> dict[str, Any]:
    if index % 2:
        claims = [
            claim(
                "C1",
                "The image shows a close-up portrait of one visible person.",
                "supports",
                ["The image is a single-person portrait in the existing controlled portrait pool."],
                ["person", "count"],
            )
        ]
        case_type = "positive_paraphrase"
    else:
        claims = [
            claim(
                "C1",
                "Exactly one person is visible in the portrait.",
                "supports",
                ["The image contains one central portrait subject."],
                ["person", "count"],
            )
        ]
        case_type = "ocr_count_spatial"
    return base_record(
        row,
        split,
        f"stage2_relation_v3_{split}_{case_type}_{index:04d}",
        case_type,
        "medium",
        target_for(claims),
        pair_id=pair_id,
        pair_role="support" if pair_id else None,
    )


def contradict_case(
    row: dict[str, Any],
    split: str,
    index: int,
    mismatch_by_source: dict[str, dict[str, Any]],
    subtype_index: int,
    pair_id: str | None,
) -> dict[str, Any]:
    subtype = [
        "single_attribute_counterfactual",
        "near_person_mismatch",
        "event_context_mismatch",
        "ocr_count_spatial",
    ][subtype_index % 4]
    if subtype == "single_attribute_counterfactual":
        item = single_attribute_claim(row)
    elif subtype == "near_person_mismatch":
        item = near_person_claim(row, mismatch_by_source)
    elif subtype == "event_context_mismatch":
        item = claim(
            "C1",
            "The person is speaking into a visible microphone during a public meeting.",
            "contradicts",
            ["The controlled portrait image does not show a public meeting setting or a visible microphone."],
            ["action", "object", "scene"],
        )
    else:
        item = claim(
            "C1",
            "Two people are standing side by side in the image.",
            "contradicts",
            ["The image is a close-up portrait with one central visible person."],
            ["person", "count", "spatial"],
        )
    return base_record(
        row,
        split,
        f"stage2_relation_v3_{split}_{subtype}_{index:04d}",
        subtype,
        "hard",
        target_for([item]),
        pair_id=pair_id,
        pair_role="counterfactual" if pair_id else None,
    )


def single_attribute_claim(row: dict[str, Any]) -> dict[str, Any]:
    attrs = attribute_values(row)
    if "gender" in attrs:
        value = sorted(attrs["gender"])[0]
        opposite = "woman" if value == "man" else "man"
        return claim(
            "C1",
            f"The portrait shows a {opposite}.",
            "contradicts",
            [f"The frozen visual description indicates the portrait subject is a {value}."],
            ["gender", "person"],
        )
    if "eyewear" in attrs:
        value = sorted(attrs["eyewear"])[0]
        return claim(
            "C1",
            f"The person is not wearing {value}.",
            "contradicts",
            [f"The frozen visual description mentions {value}."],
            ["eyewear"],
        )
    if "hair_color" in attrs:
        value = sorted(attrs["hair_color"])[0]
        opposite = "blonde" if value not in {"blonde", "blond"} else "dark"
        return claim(
            "C1",
            f"The person has {opposite} hair.",
            "contradicts",
            [f"The frozen visual description indicates {value} hair."],
            ["hair_color"],
        )
    if "headwear" in attrs:
        value = sorted(attrs["headwear"])[0]
        return claim(
            "C1",
            f"The person is not wearing a {value}.",
            "contradicts",
            [f"The frozen visual description mentions a {value}."],
            ["headwear"],
        )
    return claim(
        "C1",
        "Two people are visible in the close-up portrait.",
        "contradicts",
        ["The controlled portrait image is treated as a single-person portrait."],
        ["person", "count"],
    )


def near_person_claim(row: dict[str, Any], mismatch_by_source: dict[str, dict[str, Any]]) -> dict[str, Any]:
    mismatch = mismatch_by_source.get(str(row.get("source_key") or row.get("image")))
    if mismatch is None:
        return single_attribute_claim(row)
    donor_claims = split_body_claims(str(mismatch.get("title")), str(mismatch.get("body")))
    reasons = mismatch.get("mismatch_reasons") or []
    evidence = [str(item) for item in reasons[:3]] or [
        "The donor text describes a different portrait with conflicting visible attributes."
    ]
    return claim("C1", donor_claims[-1], "contradicts", evidence, attrs_from_reasons(evidence))


def unrelated_case(row: dict[str, Any], split: str, index: int) -> dict[str, Any]:
    templates = [
        (
            "The image shows emergency workers carrying residents through flooded streets.",
            "The actual image is a close-up portrait, not a flood rescue scene.",
            ["scene", "action", "person"],
        ),
        (
            "The image shows a wide landscape with mountains and no portrait subject.",
            "The actual image contains a portrait subject rather than a landscape scene.",
            ["scene", "background", "person"],
        ),
        (
            "The image shows a crowded government meeting room with people seated at desks.",
            "The actual image is a close-up portrait and lacks a meeting-room scene.",
            ["scene", "count", "person"],
        ),
    ]
    text, evidence, attrs = templates[index % len(templates)]
    return base_record(
        row,
        split,
        f"stage2_relation_v3_{split}_unrelated_pair_{index:04d}",
        "unrelated_pair",
        "hard",
        target_for([claim("C1", text, "unrelated", [evidence], attrs)]),
    )


def insufficient_case(row: dict[str, Any], split: str, index: int) -> dict[str, Any]:
    templates = [
        (
            "This portrait was taken yesterday after the policy announcement.",
            "The image may show a person, but a single image cannot verify the time or policy context.",
            ["time", "event_truth"],
        ),
        (
            "The visible person is the newly appointed city mayor.",
            "The image alone cannot verify the person's identity or appointment status.",
            ["identity"],
        ),
        (
            "The image proves the person caused the incident described in the article.",
            "A single image cannot establish causality for the described incident.",
            ["causality", "event_truth"],
        ),
        (
            "The person supports the political view described in the story.",
            "The image alone cannot verify the person's viewpoint.",
            ["viewpoint"],
        ),
    ]
    text, evidence, attrs = templates[index % len(templates)]
    return base_record(
        row,
        split,
        f"stage2_relation_v3_{split}_non_visual_claim_{index:04d}",
        "non_visual_claim",
        "hard",
        target_for([claim("C1", text, "insufficient", [evidence], attrs, verifiability="not_verifiable")]),
    )


def hard_records(split: str, rows: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    sources = source_rows(rows)
    mismatch_by_source = mismatched_rows(rows)
    rng = random.Random(stable_int(seed, split, "relation_v3_hard"))
    rng.shuffle(sources)
    records: list[dict[str, Any]] = []
    for idx, row in enumerate(sources, start=1):
        pair_id = f"stage2_relation_v3_{split}_pair_{idx:04d}" if idx % 4 == 1 else None
        records.append(support_case(row, split, idx, pair_id))
        records.append(contradict_case(row, split, idx, mismatch_by_source, idx - 1, pair_id))
        records.append(unrelated_case(row, split, idx))
        records.append(insufficient_case(row, split, idx))
    rng.shuffle(records)
    return records


def validate_records(records: list[dict[str, Any]], split: str) -> Counter:
    stats: Counter = Counter()
    group_to_split: dict[str, str] = {}
    pair_roles: dict[str, set[str]] = defaultdict(set)
    for row in records:
        if row["split"] != split:
            raise ValueError(f"{row['id']}: bad split")
        if not Path(str(row["image"])).exists():
            raise FileNotFoundError(row["image"])
        target = validate_target(dict(row["target"]))
        if row["overall_relation"] != target["overall_relation"]:
            raise ValueError(f"{row['id']}: relation mismatch")
        if row["prompt"] != prompt_for(target["claims"]):
            raise ValueError(f"{row['id']}: prompt mismatch")
        group = str(row["group_id"])
        seen_split = group_to_split.setdefault(group, split)
        if seen_split != split:
            raise ValueError(f"{row['id']}: group crossed splits")
        if row.get("counterfactual_pair_id"):
            pair_roles[str(row["counterfactual_pair_id"])].add(str(row.get("counterfactual_pair_role")))
        stats["total"] += 1
        stats[("difficulty", row["difficulty"])] += 1
        stats[("case_type", row["case_type"])] += 1
        stats[("overall_relation", target["overall_relation"])] += 1
        stats[("image_verdict", str(row.get("image_verdict")))] += 1
    for pair_id, roles in pair_roles.items():
        if roles != {"support", "counterfactual"}:
            raise ValueError(f"{pair_id}: expected support/counterfactual pair, got {roles}")
    stats["counterfactual_pairs"] = len(pair_roles)
    return stats


def build_split(input_path: Path, output_root: Path, split: str, seed: int) -> dict[str, Any]:
    rows = load_jsonl(input_path)
    easy = [easy_record(row, split, idx) for idx, row in enumerate(rows, start=1)]
    hard = hard_records(split, rows, seed)
    records = easy + hard
    rng = random.Random(stable_int(seed, split, "relation_v3_shuffle"))
    rng.shuffle(records)
    stats = validate_records(records, split)
    out_path = output_root / f"{split}_raw.jsonl"
    write_jsonl(out_path, records)
    return {
        "split": split,
        "input": str(input_path),
        "output": str(out_path),
        "stats": {str(key): value for key, value in sorted(stats.items(), key=lambda item: str(item[0]))},
    }


def validate_cross_split(output_root: Path) -> dict[str, Any]:
    group_split: dict[str, str] = {}
    overlaps = []
    for split in ["train", "dev", "final"]:
        rows = load_jsonl(output_root / f"{split}_raw.jsonl")
        for row in rows:
            group = str(row["group_id"])
            if group in group_split and group_split[group] != split:
                overlaps.append({"group_id": group, "first_split": group_split[group], "second_split": split})
            group_split.setdefault(group, split)
    if overlaps:
        raise ValueError(f"group leakage across splits: {overlaps[:5]}")
    return {"group_count": len(group_split), "overlap_count": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Stage2 relation-v3 claim-level data from v2 DeepFake-news pairs.")
    parser.add_argument("--v2-root", type=Path, default=Path("artifacts/stage2/deepfake_news_pairs_v2"))
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/stage2/relation_v3"))
    parser.add_argument("--seed", type=int, default=20260719)
    args = parser.parse_args()

    args.output_root.mkdir(parents=True, exist_ok=True)
    meta = {
        "source": "stage2_deepfake_news_pairs_v2",
        "v2_root": str(args.v2_root),
        "output_root": str(args.output_root),
        "seed": args.seed,
        "label_set": sorted(RELATIONS),
        "aggregation_rule": [
            "any unrelated -> unrelated",
            "else any contradicts -> contradicts",
            "else only not_verifiable/insufficient -> insufficient",
            "else all verifiable supported -> supports",
        ],
        "splits": [],
    }
    for split in ["train", "dev", "final"]:
        meta["splits"].append(build_split(args.v2_root / f"{split}_raw.jsonl", args.output_root, split, args.seed))
    meta["cross_split"] = validate_cross_split(args.output_root)
    (args.output_root / "dataset_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("wrote", args.output_root)
    print(json.dumps(meta["cross_split"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
