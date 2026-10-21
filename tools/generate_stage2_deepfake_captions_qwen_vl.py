#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Any

from build_stage1_domain_boost_json import (
    Candidate,
    close_archives,
    copy_archive_member,
    discover_faceapp,
    discover_ffhq,
    safe_name,
    stable_seed,
)


IMAGE_PROMPT = (
    "Describe only the visible content of this single portrait image for a "
    "controlled text-image consistency dataset. Mention apparent visual cues "
    "such as person count, pose, clothing color, hair, glasses, expression, "
    "and background only when they are visible. Do not identify the person. "
    "Do not mention authenticity, manipulation, datasets, filenames, software, "
    "or forensic terms. Return only JSON with exactly these string keys: "
    "caption, title, and body. Use neutral news style. The title should be "
    "short. The body should be one sentence."
)

FALLBACK_CAPTION = "a close-up portrait of a person in an indoor setting"
FALLBACK_TITLE = "Portrait released alongside a community event update"
FALLBACK_BODY = "The accompanying image shows a close-up portrait of a person in an indoor setting."

FORBIDDEN_TERMS = {
    "authentic",
    "deepfake",
    "faceapp",
    "fake",
    "ffhq",
    "forensic",
    "forged",
    "manipulated",
    "real",
    "tamper",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def output_image_rel(candidate: Candidate) -> Path:
    suffix = Path(candidate.image_member).suffix.lower()
    return (
        Path("images")
        / candidate.source
        / candidate.source_split
        / candidate.label
        / f"{safe_name(candidate.id)}{suffix}"
    )


def source_key(candidate: Candidate) -> str:
    return f"{candidate.source_path}::{candidate.image_member}"


def clean_space(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def forbidden_hits(*texts: str) -> list[str]:
    haystack = " ".join(texts).lower()
    return sorted(term for term in FORBIDDEN_TERMS if re.search(rf"\b{re.escape(term)}\b", haystack))


def extract_json_object(text: str) -> dict[str, Any] | None:
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
    return None


def normalize_caption(text: str) -> str:
    caption = clean_space(text)
    caption = re.sub(r"^the image (?:shows|depicts)\s+", "", caption, flags=re.IGNORECASE)
    caption = re.sub(r"^this image (?:shows|depicts)\s+", "", caption, flags=re.IGNORECASE)
    caption = caption.strip(" .")
    if not caption:
        caption = FALLBACK_CAPTION
    return caption[:220]


def article_from_caption(caption: str, title: str | None = None, body: str | None = None) -> tuple[str, str]:
    caption = normalize_caption(caption)
    title_text = clean_space(title) if title else ""
    body_text = clean_space(body) if body else ""
    if not title_text or forbidden_hits(title_text):
        title_text = FALLBACK_TITLE
    if not body_text or forbidden_hits(body_text):
        body_text = f"The accompanying image shows {caption}."
    if forbidden_hits(title_text, body_text):
        title_text = FALLBACK_TITLE
        body_text = FALLBACK_BODY
    return title_text[:120], body_text[:260]


def parse_caption(raw: str) -> dict[str, Any]:
    obj = extract_json_object(raw)
    if obj is None:
        caption = normalize_caption(raw)
        title, body = article_from_caption(caption)
        return {
            "caption": caption,
            "title": title,
            "body": body,
            "valid_json": False,
            "parse_error": "no JSON object found",
        }

    caption = normalize_caption(str(obj.get("caption", "")))
    title, body = article_from_caption(caption, str(obj.get("title", "")), str(obj.get("body", "")))
    return {
        "caption": caption,
        "title": title,
        "body": body,
        "valid_json": True,
        "parse_error": None,
    }


def discover_pool(args: argparse.Namespace) -> list[Candidate]:
    candidates: list[Candidate] = []
    for split in args.ffhq_splits.split(","):
        split = split.strip()
        if split:
            candidates.extend(discover_ffhq(args.ffhq_zip, split))
    for split in args.faceapp_splits.split(","):
        split = split.strip()
        if split:
            candidates.extend(discover_faceapp(args.faceapp_zip, split))

    buckets: dict[tuple[str, str], list[Candidate]] = {}
    for candidate in candidates:
        buckets.setdefault((candidate.source, candidate.source_split), []).append(candidate)

    rng = random.Random(args.seed)
    selected: list[Candidate] = []
    for key in sorted(buckets):
        group = list(buckets[key])
        rng.shuffle(group)
        selected.extend(group[: args.per_source_split])
    rng.shuffle(selected)
    if args.limit is not None:
        selected = selected[: args.limit]
    return selected


def prepare_row(candidate: Candidate, output_root: Path) -> dict[str, Any]:
    image_rel = output_image_rel(candidate)
    image_path = output_root / image_rel
    copy_archive_member(candidate, candidate.image_member, image_path)
    return {
        "source_key": source_key(candidate),
        "source": candidate.source,
        "source_split": candidate.source_split,
        "label": candidate.label,
        "image_verdict": "tampered" if candidate.label == "tampered" else "authentic",
        "tamper_domain": candidate.tamper_domain,
        "source_path": str(candidate.source_path),
        "image_member": candidate.image_member,
        "mask_member": candidate.mask_member,
        "image": str(image_path),
        "image_rel": str(image_rel),
    }


def load_existing(output_path: Path) -> dict[str, dict[str, Any]]:
    rows = load_jsonl(output_path)
    return {str(row["source_key"]): row for row in rows}


def write_all(output_path: Path, rows: dict[str, dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_suffix(output_path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for key in sorted(rows):
            f.write(json.dumps(rows[key], ensure_ascii=False) + "\n")
    tmp.replace(output_path)


def load_model(args: argparse.Namespace):
    import torch
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    local_files_only = not args.allow_network
    device = args.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[args.dtype]
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True, local_files_only=local_files_only)
    if hasattr(processor, "tokenizer"):
        processor.tokenizer.padding_side = "left"
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    model.eval()
    return torch, process_vision_info, processor, model, device


def infer_batch(
    torch_mod,
    process_vision_info,
    processor,
    model,
    device: str,
    batch: list[dict[str, Any]],
    max_new_tokens: int,
    max_pixels: int | None,
) -> list[str]:
    messages_list = []
    for row in batch:
        image = {"type": "image", "image": row["image"]}
        if max_pixels is not None:
            image["max_pixels"] = max_pixels
        messages_list.append(
            [{"role": "user", "content": [image, {"type": "text", "text": IMAGE_PROMPT}]}]
        )
    texts = [processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) for messages in messages_list]
    image_inputs_list = []
    video_inputs_list = []
    for messages in messages_list:
        image_inputs, video_inputs = process_vision_info(messages)
        image_inputs_list.extend(image_inputs or [])
        if video_inputs:
            video_inputs_list.extend(video_inputs)
    inputs = processor(
        text=texts,
        images=image_inputs_list or None,
        videos=video_inputs_list or None,
        padding=True,
        return_tensors="pt",
    ).to(device)
    with torch_mod.inference_mode():
        generated_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    generated_ids = generated_ids[:, inputs["input_ids"].shape[1] :]
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)


def template_caption(row: dict[str, Any]) -> dict[str, Any]:
    title, body = article_from_caption(FALLBACK_CAPTION)
    return {
        "caption": FALLBACK_CAPTION,
        "title": title,
        "body": body,
        "valid_json": True,
        "parse_error": None,
        "raw_caption_output": "",
        "caption_backend": "template_only",
    }


def validate_record(row: dict[str, Any]) -> None:
    for field in ["caption", "title", "body"]:
        if not clean_space(row.get(field)):
            raise ValueError(f"{row.get('source_key')}: empty {field}")
    hits = forbidden_hits(str(row["title"]), str(row["body"]))
    if hits:
        raise ValueError(f"{row.get('source_key')}: forbidden terms in article text: {hits}")


def run(args: argparse.Namespace) -> None:
    output_path = args.output_root / "captions.jsonl"
    selected = discover_pool(args)
    existing = load_existing(output_path) if args.resume else {}
    if not args.resume and output_path.exists():
        output_path.unlink()
        existing = {}

    prepared = [prepare_row(candidate, args.output_root) for candidate in selected]
    pending = [row for row in prepared if str(row["source_key"]) not in existing]

    model_bundle = None
    if not args.template_only and pending:
        model_bundle = load_model(args)

    for start in range(0, len(pending), args.batch_size):
        batch = pending[start : start + args.batch_size]
        print(f"caption batch {start + 1}-{start + len(batch)}/{len(pending)}", flush=True)
        if args.template_only:
            parsed = [template_caption(row) for row in batch]
        else:
            if model_bundle is None:
                raise RuntimeError("model was not loaded")
            raw_outputs = infer_batch(*model_bundle, batch, args.max_new_tokens, args.max_pixels)
            parsed = []
            for raw in raw_outputs:
                item = parse_caption(raw.strip())
                item["raw_caption_output"] = raw.strip()
                item["caption_backend"] = "qwen2_5_vl_base"
                parsed.append(item)

        for row, item in zip(batch, parsed):
            record = {**row, **item}
            validate_record(record)
            existing[str(row["source_key"])] = record
        write_all(output_path, existing)

    meta = {
        "output": str(output_path),
        "seed": args.seed,
        "per_source_split": args.per_source_split,
        "total_records": len(existing),
        "caption_backend": "template_only" if args.template_only else "qwen2_5_vl_base",
        "forbidden_terms": sorted(FORBIDDEN_TERMS),
        "prompt": IMAGE_PROMPT,
    }
    (args.output_root / "caption_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", output_path)
    print(json.dumps(meta, ensure_ascii=False, sort_keys=True))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate frozen neutral captions for Stage2 DeepFake-news pairs.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/stage2/deepfake_news_caption_pool"))
    parser.add_argument("--ffhq-zip", type=Path, default=Path("dataset/deepfake/ffhq.zip"))
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--ffhq-splits", default="train,test")
    parser.add_argument("--faceapp-splits", default="train,test")
    parser.add_argument("--per-source-split", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260718)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--template-only", action="store_true", help="Smoke-test fallback; not intended for final training data.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--device")
    parser.add_argument("--dtype", choices=["bf16", "fp16", "fp32"], default="bf16")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--max-pixels", type=int, default=524288)
    parser.add_argument("--allow-network", action="store_true")
    args = parser.parse_args()
    if args.per_source_split < 1:
        raise ValueError("--per-source-split must be positive")
    if args.batch_size < 1:
        raise ValueError("--batch-size must be positive")
    return args


def main() -> None:
    args = parse_args()
    try:
        run(args)
    finally:
        close_archives()


if __name__ == "__main__":
    main()
