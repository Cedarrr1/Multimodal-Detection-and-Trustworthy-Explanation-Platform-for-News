#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FROZEN_STAGE1_ADAPTER = Path("artifacts/lora_runs/qwen2_5_vl_stage1_p500_json")
DEFAULT_IMAGE_FORENSICS_ADAPTER = Path("artifacts/lora_runs/qwen2_5_vl_stage1_domain_boost_json")
DEFAULT_STAGE2_DEEPFAKE_NEWS_ADAPTER = Path("artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_v2_json")
DEFAULT_RELATION_V3_ADAPTER = Path("artifacts/lora_runs/qwen2_5_vl_relation_v3_claim_json")
FROZEN_STAGE1_EVAL_CACHE = Path("artifacts/eval/stage1_eval_p30_base_jsonp100_jsonp500_max420.jsonl")
DEFAULT_OUTPUT = Path("artifacts/reports/sample_news_report.json")
VALID_IMAGE_VERDICTS = {"authentic", "tampered", "unknown", "uncertain"}
VALID_TAMPER_DOMAINS = {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}
VALID_RELATION_V3 = {"supports", "contradicts", "unrelated", "insufficient"}
VALID_FINAL_V3 = {"credible", "fake_news", "uncertain"}
VALID_EVIDENCE_ATTRIBUTES_V3 = {
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
STAGE2_NEWS_KEYS = (
    "image_verdict",
    "tamper_domain",
    "text_image_relation",
    "final_news_verdict",
    "forensic_region",
    "evidence",
)
STAGE2_NEWS_KEY_SET = set(STAGE2_NEWS_KEYS)
STAGE3_NEWS_KEYS = (
    "image_verdict",
    "tamper_domain",
    "text_image_relation",
    "final_news_verdict",
    "forensic_region",
    "claims",
    "evidence",
)
STAGE3_NEWS_KEY_SET = set(STAGE3_NEWS_KEYS)


@dataclass(frozen=True)
class NewsInput:
    title: str
    body: str
    image: Path
    metadata: dict[str, Any]


def load_news(path: Path) -> NewsInput:
    row = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(row, dict):
        raise ValueError("input JSON must be an object")

    title = str(row.get("title", "")).strip()
    body = str(row.get("body", "")).strip()
    image_text = str(row.get("image", "")).strip()
    if not title:
        raise ValueError("input JSON requires non-empty title")
    if not body:
        raise ValueError("input JSON requires non-empty body")
    if not image_text:
        raise ValueError("input JSON requires non-empty image")

    image = Path(image_text)
    if not image.is_absolute():
        image = (path.parent / image).resolve()
        if not image.exists():
            image = Path(image_text).resolve()
    if not image.exists():
        raise FileNotFoundError(image)

    metadata = row.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {"raw_metadata": metadata}
    return NewsInput(title=title, body=body, image=image, metadata=metadata)


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?。！？])\s+", normalized)
    return [part.strip() for part in parts if part.strip()]


def extract_text_claims(news: NewsInput, max_claims: int = 4) -> list[dict[str, Any]]:
    candidates = [news.title, *split_sentences(news.body)]
    claims: list[dict[str, Any]] = []
    seen: set[str] = set()
    for text in candidates:
        compact = re.sub(r"\s+", " ", text).strip()
        if not compact or compact.lower() in seen:
            continue
        seen.add(compact.lower())
        claim_type = "headline" if compact == news.title else "body"
        claims.append(
            {
                "claim_id": f"C{len(claims) + 1}",
                "text": compact,
                "source": claim_type,
                "needs_visual_support": likely_visual_claim(compact),
            }
        )
        if len(claims) >= max_claims:
            break
    return claims


def likely_visual_claim(text: str) -> bool:
    lowered = text.lower()
    visual_terms = {
        "photo",
        "image",
        "picture",
        "shows",
        "shown",
        "seen",
        "video",
        "scene",
        "at the site",
        "现场",
        "照片",
        "图片",
        "显示",
        "画面",
    }
    return any(term in lowered for term in visual_terms)


def infer_scene_from_text(news: NewsInput) -> dict[str, Any]:
    text = f"{news.title} {news.body}".lower()
    entities = []
    for pattern in [
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b",
    ]:
        entities.extend(re.findall(pattern, f"{news.title} {news.body}"))
    keywords = []
    for word in [
        "protest",
        "fire",
        "flood",
        "explosion",
        "hospital",
        "official",
        "police",
        "election",
        "war",
        "earthquake",
        "accident",
    ]:
        if word in text:
            keywords.append(word)
    return {
        "summary": "Rule-based scene placeholder derived from the news text; replace with Qwen2.5-VL base captioning when available.",
        "text_keywords": keywords,
        "mentioned_entities": sorted(set(entities))[:12],
    }


def build_region_proposals() -> list[dict[str, Any]]:
    return [
        {
            "proposal_id": "R1",
            "bbox_xyxy_norm": [0.0, 0.0, 1.0, 1.0],
            "source": "full_image",
            "description": "Whole image for baseline visual forensics.",
        },
        {
            "proposal_id": "R2",
            "bbox_xyxy_norm": [0.2, 0.2, 0.8, 0.8],
            "source": "rule_center_crop",
            "description": "Center crop fallback for region-level rechecking.",
        },
    ]


def module1_parse(news: NewsInput) -> dict[str, Any]:
    claims = extract_text_claims(news)
    scene = infer_scene_from_text(news)
    caption = (
        "Caption is generated by the rule fallback from the article text. "
        "Use the qwen-vl parser backend to replace this with image-grounded captioning."
    )
    return {
        "text_claims": claims,
        "image_parse": {
            "caption": caption,
            "scene": scene,
            "region_proposals": build_region_proposals(),
        },
        "backend": "rule_mock",
    }


def infer_mock_forensics(news: NewsInput, module1: dict[str, Any]) -> dict[str, Any]:
    text = f"{news.title} {news.body}".lower()
    image_name = news.image.name.lower()
    suspicious_terms = [
        "fake",
        "forged",
        "tampered",
        "manipulated",
        "photoshop",
        "deepfake",
        "ai-generated",
        "aigc",
        "inpaint",
        "edited",
    ]
    looks_suspicious = any(term in text or term in image_name for term in suspicious_terms)
    if looks_suspicious:
        verdict = "tampered"
        domain = "deepfake" if "deepfake" in text or "face" in image_name else "photoshop"
        confidence = 0.62
        evidence = [
            "Rule fallback detected manipulation-related wording or filename cues.",
            "The MVP is using the frozen Stage1 adapter contract, but live model inference was not requested.",
        ]
        tampered_region = "unknown suspicious region; use qwen-lora backend for image-grounded evidence"
    else:
        verdict = "unknown"
        domain = "unknown"
        confidence = 0.35
        evidence = [
            "Rule fallback found no explicit manipulation cue in the article text or image filename.",
            "No image-grounded model inference was run in mock mode.",
        ]
        tampered_region = "unknown"

    suspicious_regions = []
    for proposal in module1["image_parse"]["region_proposals"]:
        suspicious_regions.append(
            {
                "proposal_id": proposal["proposal_id"],
                "region_verdict": verdict if proposal["proposal_id"] == "R1" else "unknown",
                "tamper_domain": domain if proposal["proposal_id"] == "R1" else "unknown",
                "artifact_evidence": evidence[:1],
                "confidence": confidence if proposal["proposal_id"] == "R1" else 0.2,
                "short_reasoning": "Mock region result; replace with crop inference for production.",
            }
        )

    return {
        "image_verdict": verdict,
        "tamper_domain": domain,
        "tampered_region": tampered_region,
        "evidence": evidence,
        "suspicious_regions": suspicious_regions,
        "forensic_confidence": confidence,
        "backend": "mock",
        "stage1_adapter": str(FROZEN_STAGE1_ADAPTER),
    }


def lookup_cached_json_p500_forensics(news: NewsInput) -> dict[str, Any] | None:
    if not FROZEN_STAGE1_EVAL_CACHE.exists():
        return None
    news_image = news.image.resolve()
    for line in FROZEN_STAGE1_EVAL_CACHE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cached_image = Path(str(row.get("image", ""))).resolve()
        if cached_image != news_image:
            continue
        prediction = row.get("predictions", {}).get("json_p500", {})
        parsed = prediction.get("parsed")
        if not isinstance(parsed, dict):
            return None
        result = normalize_forensics(parsed, "cached-json-p500")
        result["forensic_confidence"] = 0.8 if prediction.get("valid_schema") else 0.6
        result["eval_cache"] = str(FROZEN_STAGE1_EVAL_CACHE)
        result["eval_index"] = row.get("index")
        result["suspicious_regions"] = [
            {
                "proposal_id": "R1",
                "region_verdict": result["image_verdict"],
                "tamper_domain": result["tamper_domain"],
                "artifact_evidence": result["evidence"][:3],
                "confidence": result["forensic_confidence"],
                "short_reasoning": "Whole-image cached json_p500 Stage1 prediction.",
            }
        ]
        return result
    return None


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    candidates = [stripped]
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        candidates.insert(0, fence.group(1).strip())
    brace = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if brace:
        candidates.append(brace.group(0))
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    raise ValueError("model output did not contain a JSON object")


def stage2_deepfake_news_prompt(news: NewsInput) -> str:
    return (
        f"Title: {news.title}\n"
        f"Body: {news.body}\n\n"
        "Determine whether the image is digitally manipulated and whether the title "
        "and body match the visible image. This is a controlled text-image "
        "consistency benchmark, not real-world news fact checking. Return only "
        "valid compact JSON with exactly these keys: image_verdict, tamper_domain, "
        "text_image_relation, final_news_verdict, forensic_region, and evidence. "
        'Use image_verdict "authentic" or "tampered"; tamper_domain "none" or '
        '"deepfake"; text_image_relation "consistent" or "mismatched"; '
        'final_news_verdict "credible" or "fake_news"; forensic_region "face" or "none".'
    )


def normalize_stage2_deepfake_news(obj: dict[str, Any], backend: str) -> dict[str, Any]:
    image_verdict = str(obj.get("image_verdict", "")).strip().lower()
    if image_verdict not in {"authentic", "tampered"}:
        image_verdict = "tampered" if "tamper" in image_verdict or "fake" in image_verdict else "authentic"

    tamper_domain = str(obj.get("tamper_domain", "")).strip().lower()
    if tamper_domain not in {"none", "deepfake"}:
        tamper_domain = "deepfake" if image_verdict == "tampered" else "none"
    if image_verdict == "authentic":
        tamper_domain = "none"
    elif image_verdict == "tampered":
        tamper_domain = "deepfake"

    relation = str(obj.get("text_image_relation", "")).strip().lower()
    if relation not in {"consistent", "mismatched"}:
        relation = "mismatched" if "mismatch" in relation or "inconsistent" in relation else "consistent"

    final = "fake_news" if image_verdict == "tampered" or relation == "mismatched" else "credible"
    forensic_region = "face" if image_verdict == "tampered" else "none"
    evidence = obj.get("evidence", [])
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        evidence = []
    evidence = [str(item).strip() for item in evidence if str(item).strip()][:5]
    if not evidence:
        evidence = [
            "The final verdict follows the fixed fusion rule over image manipulation and text-image relation."
        ]
    return {
        "image_verdict": image_verdict,
        "tamper_domain": tamper_domain,
        "text_image_relation": relation,
        "final_news_verdict": final,
        "forensic_region": forensic_region,
        "evidence": evidence,
        "_backend": backend,
    }


def validate_stage2_deepfake_news_report(report: dict[str, Any]) -> None:
    if set(report) != STAGE2_NEWS_KEY_SET:
        raise ValueError(f"bad Stage2 report keys: {sorted(report)}")
    if report["image_verdict"] not in {"authentic", "tampered"}:
        raise ValueError("bad image_verdict")
    if report["tamper_domain"] not in {"none", "deepfake"}:
        raise ValueError("bad tamper_domain")
    if report["text_image_relation"] not in {"consistent", "mismatched"}:
        raise ValueError("bad text_image_relation")
    expected_final = (
        "fake_news"
        if report["image_verdict"] == "tampered" or report["text_image_relation"] == "mismatched"
        else "credible"
    )
    if report["final_news_verdict"] != expected_final:
        raise ValueError("final_news_verdict violates the fixed fusion rule")
    expected_region = "face" if report["image_verdict"] == "tampered" else "none"
    if report["forensic_region"] != expected_region:
        raise ValueError("forensic_region is inconsistent with image_verdict")
    if not isinstance(report["evidence"], list) or not report["evidence"]:
        raise ValueError("evidence must be a non-empty list")


def relation_v3_prompt(claims: list[dict[str, Any]]) -> str:
    claim_lines = "\n".join(f"{item['claim_id']}: {item['claim']}" for item in claims)
    return (
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


def stage3_claims_from_module1(module1: dict[str, Any]) -> list[dict[str, Any]]:
    claims = []
    for idx, item in enumerate(module1.get("text_claims", []), start=1):
        claims.append(
            {
                "claim_id": str(item.get("claim_id") or f"C{idx}"),
                "claim": str(item.get("text") or item.get("claim") or "").strip(),
            }
        )
    return [item for item in claims if item["claim"]]


def normalize_relation_label(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in VALID_RELATION_V3:
        return text
    if "unrelated" in text or "irrelevant" in text or "different scene" in text:
        return "unrelated"
    if "contradict" in text or "conflict" in text or "mismatch" in text or "opposite" in text:
        return "contradicts"
    if "insufficient" in text or "not verifiable" in text or "cannot verify" in text:
        return "insufficient"
    if "support" in text or "match" in text or "consistent" in text:
        return "supports"
    return "insufficient"


def aggregate_relation_v3(claims: list[dict[str, Any]]) -> str:
    relations = [claim["relation"] for claim in claims]
    if any(relation == "unrelated" for relation in relations):
        return "unrelated"
    if any(relation == "contradicts" for relation in relations):
        return "contradicts"
    if not any(claim["visual_verifiability"] == "verifiable" for claim in claims):
        return "insufficient"
    if all(relation == "supports" for relation in relations if relation != "insufficient"):
        return "supports"
    return "insufficient"


def normalize_relation_v3_report(obj: dict[str, Any], requested_claims: list[dict[str, Any]], backend: str) -> dict[str, Any]:
    raw_claims = obj.get("claims") if isinstance(obj, dict) else None
    claims = []
    if isinstance(raw_claims, list):
        source_claims = raw_claims
    else:
        source_claims = requested_claims
    requested_by_id = {item["claim_id"]: item["claim"] for item in requested_claims}
    for idx, item in enumerate(source_claims, start=1):
        if not isinstance(item, dict):
            item = {}
        claim_id = str(item.get("claim_id") or f"C{idx}").strip() or f"C{idx}"
        claim_text = str(item.get("claim") or requested_by_id.get(claim_id) or "").strip()
        relation = normalize_relation_label(item.get("relation"))
        verifiability = str(item.get("visual_verifiability") or "").strip().lower()
        if verifiability not in {"verifiable", "not_verifiable"}:
            verifiability = "not_verifiable" if relation == "insufficient" else "verifiable"
        if relation == "insufficient":
            verifiability = "not_verifiable"
        evidence = item.get("visual_evidence")
        if isinstance(evidence, str):
            evidence = [evidence]
        if not isinstance(evidence, list):
            evidence = []
        evidence = [str(value).strip() for value in evidence if str(value).strip()][:5]
        if not evidence:
            evidence = ["The relation follows the visible-image claim judgment."]
        attrs = item.get("evidence_attributes")
        if isinstance(attrs, str):
            attrs = [attrs]
        if not isinstance(attrs, list):
            attrs = []
        attrs = [
            str(value).strip().lower()
            for value in attrs
            if str(value).strip().lower() in VALID_EVIDENCE_ATTRIBUTES_V3
        ][:8]
        if not attrs:
            attrs = ["event_truth"] if relation == "insufficient" else ["scene"]
        claims.append(
            {
                "claim_id": claim_id,
                "claim": claim_text or requested_by_id.get(claim_id) or "unknown claim",
                "visual_verifiability": verifiability,
                "relation": relation,
                "visual_evidence": evidence,
                "evidence_attributes": attrs,
            }
        )
    overall = normalize_relation_label(obj.get("overall_relation") if isinstance(obj, dict) else None)
    expected = aggregate_relation_v3(claims)
    if overall != expected:
        overall = expected
    return {"claims": claims, "overall_relation": overall, "_backend": backend}


def validate_relation_v3_report(report: dict[str, Any]) -> None:
    if set(report) - {"claims", "overall_relation", "_backend"}:
        raise ValueError(f"bad relation report keys: {sorted(report)}")
    if report["overall_relation"] not in VALID_RELATION_V3:
        raise ValueError("bad overall_relation")
    claims = report["claims"]
    if not isinstance(claims, list) or not claims:
        raise ValueError("claims must be a non-empty list")
    for item in claims:
        required = {"claim_id", "claim", "visual_verifiability", "relation", "visual_evidence", "evidence_attributes"}
        if set(item) != required:
            raise ValueError(f"bad claim keys: {sorted(item)}")
        if item["visual_verifiability"] not in {"verifiable", "not_verifiable"}:
            raise ValueError("bad visual_verifiability")
        if item["relation"] not in VALID_RELATION_V3:
            raise ValueError("bad claim relation")
        if item["relation"] == "insufficient" and item["visual_verifiability"] != "not_verifiable":
            raise ValueError("insufficient claim must be not_verifiable")
        if item["relation"] != "insufficient" and item["visual_verifiability"] != "verifiable":
            raise ValueError("visual relation claim must be verifiable")
        if not isinstance(item["visual_evidence"], list) or not item["visual_evidence"]:
            raise ValueError("visual_evidence must be non-empty")
        if not isinstance(item["evidence_attributes"], list) or not item["evidence_attributes"]:
            raise ValueError("evidence_attributes must be non-empty")
        if any(attr not in VALID_EVIDENCE_ATTRIBUTES_V3 for attr in item["evidence_attributes"]):
            raise ValueError("bad evidence_attributes")
    if report["overall_relation"] != aggregate_relation_v3(claims):
        raise ValueError("overall_relation violates aggregation rule")


def infer_mock_relation_v3(news: NewsInput, claims: list[dict[str, Any]]) -> dict[str, Any]:
    output_claims = []
    for item in claims:
        text = item["claim"].lower()
        if any(term in text for term in ["yesterday", "identity", "mayor", "caused", "proves", "policy", "view", "真实", "因果"]):
            relation = "insufficient"
            verifiability = "not_verifiable"
            evidence = ["The claim depends on time, identity, causality, viewpoint, or event truth that a single image cannot verify."]
            attrs = ["event_truth"]
        elif any(term in text for term in ["flooded streets", "landscape", "mountains", "meeting room", "rescue scene"]):
            relation = "unrelated"
            verifiability = "verifiable"
            evidence = ["The claim describes a different subject or scene from the provided image."]
            attrs = ["scene"]
        elif any(term in text for term in ["glasses", "microphone", "two people", "side by side"]):
            relation = "contradicts"
            verifiability = "verifiable"
            evidence = ["The mock relation backend treats this as a visible counterfactual claim requiring the relation LoRA for grounding."]
            attrs = ["object"]
        else:
            relation = "supports"
            verifiability = "verifiable"
            evidence = ["The mock relation backend found no explicit unrelated, counterfactual, or non-visual cue."]
            attrs = ["scene"]
        output_claims.append(
            {
                "claim_id": item["claim_id"],
                "claim": item["claim"],
                "visual_verifiability": verifiability,
                "relation": relation,
                "visual_evidence": evidence,
                "evidence_attributes": attrs,
            }
        )
    return normalize_relation_v3_report({"claims": output_claims, "overall_relation": aggregate_relation_v3(output_claims)}, claims, "mock")


def infer_qwen_lora_relation_v3(news: NewsInput, claims: list[dict[str, Any]], adapter: Path, max_new_tokens: int) -> dict[str, Any]:
    if not adapter.exists():
        raise FileNotFoundError(adapter)
    try:
        import torch
        from peft import PeftModel
        from qwen_vl_utils import process_vision_info
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
    except Exception as exc:  # pragma: no cover - depends on optional model stack
        raise RuntimeError(
            "qwen-lora relation backend requires torch, transformers, peft, and qwen_vl_utils"
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    base_model = "Qwen/Qwen2.5-VL-3B-Instruct"
    processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=True)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, str(adapter))
    model.eval()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": str(news.image)},
                {"type": "text", "text": relation_v3_prompt(claims)},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    raw = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()
    return normalize_relation_v3_report(extract_json_object(raw), claims, "qwen-lora")


def stage3_final_verdict(image_verdict: str, relation: str) -> str:
    if image_verdict == "tampered":
        return "fake_news"
    if relation in {"contradicts", "unrelated"}:
        return "fake_news"
    if relation == "insufficient":
        return "uncertain"
    return "credible"


def forensic_region_from_image_verdict(image_verdict: str) -> str:
    return "face" if image_verdict == "tampered" else "none"


def validate_stage3_deepfake_news_report(report: dict[str, Any]) -> None:
    if set(report) != STAGE3_NEWS_KEY_SET:
        raise ValueError(f"bad Stage3 report keys: {sorted(report)}")
    if report["image_verdict"] not in {"authentic", "tampered", "unknown"}:
        raise ValueError("bad image_verdict")
    if report["tamper_domain"] not in VALID_TAMPER_DOMAINS:
        raise ValueError("bad tamper_domain")
    if report["text_image_relation"] not in VALID_RELATION_V3:
        raise ValueError("bad text_image_relation")
    if report["final_news_verdict"] not in VALID_FINAL_V3:
        raise ValueError("bad final_news_verdict")
    expected = stage3_final_verdict(report["image_verdict"], report["text_image_relation"])
    if report["final_news_verdict"] != expected:
        raise ValueError("final_news_verdict violates v3 fusion rule")
    if report["forensic_region"] != forensic_region_from_image_verdict(report["image_verdict"]):
        raise ValueError("forensic_region is inconsistent with image_verdict")
    validate_relation_v3_report({"claims": report["claims"], "overall_relation": report["text_image_relation"]})
    if not isinstance(report["evidence"], list) or not report["evidence"]:
        raise ValueError("evidence must be a non-empty list")


def infer_mock_deepfake_news(news: NewsInput) -> dict[str, Any]:
    text = f"{news.title} {news.body} {news.image.name}".lower()
    image_verdict = "tampered" if any(term in text for term in ["faceapp", "deepfake", "tampered"]) else "authentic"
    return normalize_stage2_deepfake_news(
        {
            "image_verdict": image_verdict,
            "tamper_domain": "deepfake" if image_verdict == "tampered" else "none",
            "text_image_relation": "consistent",
            "evidence": [
                "Mock mode uses filename/text cues only; run qwen-lora for image-grounded inference."
            ],
        },
        "mock",
    )


def infer_qwen_lora_deepfake_news(news: NewsInput, adapter: Path, max_new_tokens: int) -> dict[str, Any]:
    if not adapter.exists():
        raise FileNotFoundError(adapter)
    try:
        import torch
        from peft import PeftModel
        from qwen_vl_utils import process_vision_info
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
    except Exception as exc:  # pragma: no cover - depends on optional model stack
        raise RuntimeError(
            "qwen-lora backend requires torch, transformers, peft, and qwen_vl_utils"
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    base_model = "Qwen/Qwen2.5-VL-3B-Instruct"
    processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=True)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, str(adapter))
    model.eval()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": str(news.image)},
                {"type": "text", "text": stage2_deepfake_news_prompt(news)},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    raw = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()
    return normalize_stage2_deepfake_news(extract_json_object(raw), "qwen-lora")


def run_stage2_deepfake_news_pipeline(
    input_path: Path,
    output_path: Path,
    backend: str,
    adapter: Path,
    max_new_tokens: int,
) -> dict[str, Any]:
    news = load_news(input_path)
    if backend == "mock":
        result = infer_mock_deepfake_news(news)
    elif backend == "qwen-lora":
        result = infer_qwen_lora_deepfake_news(news, adapter, max_new_tokens)
    else:
        raise ValueError(f"unknown backend: {backend}")
    report = {key: result[key] for key in STAGE2_NEWS_KEYS}
    validate_stage2_deepfake_news_report(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def run_stage3_deepfake_news_v3_pipeline(
    input_path: Path,
    output_path: Path,
    forensics_backend: str,
    relation_backend: str,
    image_adapter: Path,
    relation_adapter: Path,
    max_new_tokens: int,
) -> dict[str, Any]:
    news = load_news(input_path)
    module1 = module1_parse(news)
    image_result = module2_forensics(news, module1, forensics_backend, max_new_tokens, image_adapter)
    claims = stage3_claims_from_module1(module1)
    if not claims:
        claims = [{"claim_id": "C1", "claim": f"{news.title} {news.body}".strip()}]
    if relation_backend == "mock":
        relation_result = infer_mock_relation_v3(news, claims)
    elif relation_backend == "qwen-lora":
        relation_result = infer_qwen_lora_relation_v3(news, claims, relation_adapter, max_new_tokens)
    else:
        raise ValueError(f"unknown relation backend: {relation_backend}")

    validate_relation_v3_report(relation_result)
    image_verdict = str(image_result["image_verdict"]).strip().lower()
    if image_verdict not in {"authentic", "tampered"}:
        image_verdict = "unknown"
    tamper_domain = str(image_result["tamper_domain"]).strip().lower()
    if image_verdict == "authentic":
        tamper_domain = "none"
    elif image_verdict == "tampered" and tamper_domain in {"none", "unknown", ""}:
        tamper_domain = "deepfake"
    relation = relation_result["overall_relation"]
    evidence = []
    evidence.extend(str(item).strip() for item in image_result.get("evidence", []) if str(item).strip())
    for item in relation_result["claims"]:
        evidence.extend(str(value).strip() for value in item.get("visual_evidence", []) if str(value).strip())
    evidence = evidence[:5] or ["The final verdict follows deterministic v3 fusion over image forensics and text-image relation."]

    report = {
        "image_verdict": image_verdict,
        "tamper_domain": tamper_domain,
        "text_image_relation": relation,
        "final_news_verdict": stage3_final_verdict(image_verdict, relation),
        "forensic_region": forensic_region_from_image_verdict(image_verdict),
        "claims": relation_result["claims"],
        "evidence": evidence,
    }
    validate_stage3_deepfake_news_report(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def normalize_forensics(obj: dict[str, Any], backend: str) -> dict[str, Any]:
    verdict = str(obj.get("verdict") or obj.get("image_verdict") or "unknown").strip().lower()
    if verdict == "authentic":
        image_verdict = "authentic"
    elif verdict == "tampered":
        image_verdict = "tampered"
    else:
        image_verdict = "unknown"

    domain = str(obj.get("tamper_domain", "unknown")).strip().lower()
    if domain not in VALID_TAMPER_DOMAINS:
        if "photo" in domain or "splice" in domain or "composit" in domain:
            domain = "photoshop"
        elif "deepfake" in domain or "face" in domain:
            domain = "deepfake"
        elif "aigc" in domain or "inpaint" in domain:
            domain = "aigc_inpaint"
        elif domain in {"", "null", "no", "n/a"}:
            domain = "none"
        else:
            domain = "unknown"

    evidence = obj.get("evidence", [])
    if isinstance(evidence, str):
        evidence = [evidence]
    if not isinstance(evidence, list):
        evidence = []
    evidence = [str(item).strip() for item in evidence if str(item).strip()][:5]
    if not evidence:
        evidence = ["The Stage1 backend returned no explicit evidence."]

    return {
        "image_verdict": image_verdict,
        "tamper_domain": domain,
        "tampered_region": str(obj.get("tampered_region", "unknown")).strip() or "unknown",
        "evidence": evidence,
        "suspicious_regions": [],
        "forensic_confidence": 0.75 if image_verdict != "unknown" else 0.45,
        "backend": backend,
        "stage1_adapter": str(FROZEN_STAGE1_ADAPTER),
        "raw_stage1": obj,
    }


def infer_qwen_lora_forensics(news: NewsInput, max_new_tokens: int, adapter: Path = FROZEN_STAGE1_ADAPTER) -> dict[str, Any]:
    if not adapter.exists():
        raise FileNotFoundError(adapter)
    try:
        import torch
        from peft import PeftModel
        from qwen_vl_utils import process_vision_info
        from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
    except Exception as exc:  # pragma: no cover - depends on optional model stack
        raise RuntimeError(
            "qwen-lora backend requires torch, transformers, peft, and qwen_vl_utils"
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    base_model = "Qwen/Qwen2.5-VL-3B-Instruct"
    processor = AutoProcessor.from_pretrained(base_model, trust_remote_code=True)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(model, str(adapter))
    model.eval()

    prompt = (
        "Analyze whether this news image has been digitally manipulated. "
        "Return only valid JSON with verdict, tampered_region, tamper_domain, and evidence."
    )
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": str(news.image)},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    raw = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0].strip()
    result = normalize_forensics(extract_json_object(raw), "qwen-lora")
    result["stage1_adapter"] = str(adapter)
    return result


def module2_forensics(
    news: NewsInput,
    module1: dict[str, Any],
    backend: str,
    max_new_tokens: int,
    adapter: Path = FROZEN_STAGE1_ADAPTER,
) -> dict[str, Any]:
    if backend == "mock":
        cached = lookup_cached_json_p500_forensics(news)
        if cached is not None:
            return cached
        return infer_mock_forensics(news, module1)
    if backend == "qwen-lora":
        result = infer_qwen_lora_forensics(news, max_new_tokens, adapter)
        result["suspicious_regions"] = [
            {
                "proposal_id": "R1",
                "region_verdict": result["image_verdict"],
                "tamper_domain": result["tamper_domain"],
                "artifact_evidence": result["evidence"][:3],
                "confidence": result["forensic_confidence"],
                "short_reasoning": "Whole-image Stage1 json_p500 inference.",
            }
        ]
        return result
    raise ValueError(f"unknown Module2 backend: {backend}")


def consistency_for_claim(claim: dict[str, Any], module2: dict[str, Any]) -> tuple[str, str]:
    text = claim["text"].lower()
    image_verdict = module2["image_verdict"]
    if image_verdict == "tampered":
        if any(term in text for term in ["authentic", "real", "unmanipulated", "真实", "未篡改"]):
            return "contradicted", "The claim depends on the image being authentic, while Module2 flags image tampering."
        return "depends_on_suspicious_region", "The visual evidence is suspicious, so this claim should not be treated as fully supported."
    if claim.get("needs_visual_support"):
        return "not_verifiable", "The MVP has no external retrieval or fully grounded captioning, so visual support is not proven."
    return "uncertain", "The claim is text-level and cannot be verified by the image-only evidence."


def module3_aggregate(news: NewsInput, module1: dict[str, Any], module2: dict[str, Any]) -> dict[str, Any]:
    claim_analysis = []
    for claim in module1["text_claims"]:
        status, evidence = consistency_for_claim(claim, module2)
        claim_analysis.append(
            {
                "claim_id": claim["claim_id"],
                "claim": claim["text"],
                "status": status,
                "evidence": evidence,
            }
        )

    fake_type: list[str] = []
    if module2["image_verdict"] == "tampered":
        final_verdict = "fake_news"
        fake_type.append("image_tampering")
        if any(item["status"] in {"contradicted", "depends_on_suspicious_region"} for item in claim_analysis):
            fake_type.append("claim_depends_on_tampered_region")
    elif any(item["status"] == "not_verifiable" for item in claim_analysis):
        final_verdict = "uncertain"
        fake_type.append("insufficient_visual_grounding")
    else:
        final_verdict = "uncertain"
        fake_type.append("not_enough_evidence")

    final_reasoning = (
        f"Module1 extracted {len(module1['text_claims'])} claim(s) and "
        f"{len(module1['image_parse']['region_proposals'])} region proposal(s). "
        f"Module2 used frozen Stage1 baseline {FROZEN_STAGE1_ADAPTER} with backend "
        f"{module2['backend']} and returned image_verdict={module2['image_verdict']}, "
        f"tamper_domain={module2['tamper_domain']}."
    )
    report = (
        f"Final verdict: {final_verdict}. "
        f"Image forensics: {module2['image_verdict']} ({module2['tamper_domain']}). "
        f"Reason: {final_reasoning}"
    )
    return {
        "final_verdict": final_verdict,
        "fake_type": fake_type,
        "claim_analysis": claim_analysis,
        "final_reasoning": final_reasoning,
        "report": report,
    }


def build_report(news: NewsInput, module1: dict[str, Any], module2: dict[str, Any], module3: dict[str, Any]) -> dict[str, Any]:
    return {
        "input": {
            "title": news.title,
            "body": news.body,
            "image": str(news.image),
            "metadata": news.metadata,
        },
        "pipeline": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "stage1_policy": "frozen_json_p500_baseline",
            "stage1_adapter": str(FROZEN_STAGE1_ADAPTER),
            "objective": "news text + image -> claim parsing -> image forensics -> consistency judgment -> structured report",
        },
        "module1": module1,
        "module2": module2,
        "module3": module3,
    }


def validate_report(report: dict[str, Any]) -> None:
    required = {"input", "pipeline", "module1", "module2", "module3"}
    missing = required - set(report)
    if missing:
        raise ValueError(f"report missing keys: {sorted(missing)}")
    module3 = report["module3"]
    for key in ["final_verdict", "fake_type", "claim_analysis", "final_reasoning", "report"]:
        if key not in module3:
            raise ValueError(f"module3 missing {key}")
    module1 = report["module1"]
    if "text_claims" not in module1 or "image_parse" not in module1:
        raise ValueError("module1 must include text_claims and image_parse")
    module2 = report["module2"]
    for key in ["image_verdict", "tamper_domain", "suspicious_regions", "forensic_confidence"]:
        if key not in module2:
            raise ValueError(f"module2 missing {key}")
    if module2["image_verdict"] not in VALID_IMAGE_VERDICTS:
        raise ValueError(f"bad image_verdict: {module2['image_verdict']}")
    if module2["tamper_domain"] not in VALID_TAMPER_DOMAINS:
        raise ValueError(f"bad tamper_domain: {module2['tamper_domain']}")


def run_pipeline(input_path: Path, output_path: Path, forensics_backend: str, max_new_tokens: int) -> dict[str, Any]:
    news = load_news(input_path)
    module1 = module1_parse(news)
    module2 = module2_forensics(news, module1, forensics_backend, max_new_tokens)
    module3 = module3_aggregate(news, module1, module2)
    report = build_report(news, module1, module2, module3)
    validate_report(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the end-to-end fake-news forensics MVP.")
    parser.add_argument("--input", type=Path, required=True, help="News JSON with title/body/image.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output report JSON path.")
    parser.add_argument(
        "--report-task",
        choices=["legacy", "stage2-deepfake-news", "stage3-deepfake-news-v3"],
        default="legacy",
        help="legacy keeps the original nested MVP report; stage2-deepfake-news writes the v2 six-key JSON; stage3-deepfake-news-v3 writes the split-adapter claim relation JSON.",
    )
    parser.add_argument(
        "--forensics-backend",
        choices=["mock", "qwen-lora"],
        default="mock",
        help="Module2 backend. mock is dependency-light; qwen-lora runs frozen json_p500.",
    )
    parser.add_argument(
        "--relation-backend",
        choices=["mock", "qwen-lora"],
        default="mock",
        help="Stage3 relation backend. mock is dependency-light; qwen-lora runs the relation-v3 adapter.",
    )
    parser.add_argument(
        "--stage2-adapter",
        type=Path,
        default=DEFAULT_STAGE2_DEEPFAKE_NEWS_ADAPTER,
        help="Adapter for --report-task stage2-deepfake-news with --forensics-backend qwen-lora.",
    )
    parser.add_argument(
        "--image-adapter",
        type=Path,
        default=DEFAULT_IMAGE_FORENSICS_ADAPTER,
        help="Image-only forensics adapter for --report-task stage3-deepfake-news-v3.",
    )
    parser.add_argument(
        "--relation-adapter",
        type=Path,
        default=DEFAULT_RELATION_V3_ADAPTER,
        help="Relation-only adapter for --report-task stage3-deepfake-news-v3 with --relation-backend qwen-lora.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=420)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.report_task == "stage2-deepfake-news":
        report = run_stage2_deepfake_news_pipeline(
            args.input,
            args.output,
            args.forensics_backend,
            args.stage2_adapter,
            args.max_new_tokens,
        )
        print(json.dumps({"output": str(args.output), "final_news_verdict": report["final_news_verdict"]}, ensure_ascii=False))
        return
    if args.report_task == "stage3-deepfake-news-v3":
        report = run_stage3_deepfake_news_v3_pipeline(
            args.input,
            args.output,
            args.forensics_backend,
            args.relation_backend,
            args.image_adapter,
            args.relation_adapter,
            args.max_new_tokens,
        )
        print(json.dumps({"output": str(args.output), "final_news_verdict": report["final_news_verdict"]}, ensure_ascii=False))
        return

    report = run_pipeline(args.input, args.output, args.forensics_backend, args.max_new_tokens)
    print(json.dumps({"output": str(args.output), "final_verdict": report["module3"]["final_verdict"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
