#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


REQUIRED_KEYS = {"verdict", "tampered_region", "tamper_domain", "evidence"}
VALID_VERDICTS = {"authentic", "tampered"}
VALID_DOMAINS = {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate base and two LoRA adapters on eval_p30.")
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-VL-3B-Instruct")
    parser.add_argument("--old-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p100")
    parser.add_argument("--json-adapter", default="artifacts/lora_runs/qwen2_5_vl_stage1_p100_json")
    parser.add_argument("--first-adapter-name", default="old_p100")
    parser.add_argument("--second-adapter-name", default="json_p100")
    parser.add_argument("--data", default="artifacts/lora_data/stage1_mmtd_eval_p30_json/llamafactory_qwen_vl_sft.jsonl")
    parser.add_argument("--labels", default="artifacts/lora_data/stage1_mmtd_eval_p30_json/eval_labels.jsonl")
    parser.add_argument("--output-jsonl", default="artifacts/eval/stage1_eval_p30_three_way.jsonl")
    parser.add_argument("--summary-md", default="artifacts/eval/stage1_eval_p30_summary.md")
    parser.add_argument("--max-new-tokens", type=int, default=220)
    return parser.parse_args()


def load_eval_rows(data_path: Path, label_path: Path) -> list[dict[str, Any]]:
    data_rows = [json.loads(line) for line in data_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    labels = [json.loads(line) for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(data_rows) != len(labels):
        raise ValueError(f"data rows ({len(data_rows)}) != labels ({len(labels)})")

    rows = []
    for idx, (data, label) in enumerate(zip(data_rows, labels)):
        images = data.get("images")
        messages = data.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: expected exactly one image")
        if not isinstance(messages, list) or len(messages) < 1:
            raise ValueError(f"row {idx}: missing messages")
        image_path = Path(images[0])
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if not str(image_path).endswith(str(label["image"])):
            raise ValueError(f"row {idx}: image mismatch data={image_path} label={label['image']}")
        user_prompt = str(messages[0]["content"]).replace("<image>", "").strip()
        rows.append(
            {
                "index": idx,
                "image": str(image_path),
                "user_prompt": user_prompt,
                "label": label,
            }
        )
    return rows


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
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
            if isinstance(obj, dict):
                return obj, None
        except Exception as exc:
            last_error = str(exc)
    return None, last_error if "last_error" in locals() else "no JSON object found"


def normalize_domain(value: Any) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    if text in VALID_DOMAINS:
        return text
    if "photo" in text or "splic" in text or "composit" in text:
        return "photoshop"
    if "deepfake" in text or "face" in text:
        return "deepfake"
    if "aigc" in text or "inpaint" in text:
        return "aigc_inpaint"
    if text in {"null", "none", "no", "n/a"}:
        return "none"
    return text or "unknown"


def parse_prediction(raw: str) -> dict[str, Any]:
    obj, error = extract_json_object(raw)
    valid_json = obj is not None
    schema_valid = False
    verdict = "unknown"
    tamper_domain = "unknown"

    if obj is not None:
        schema_valid = (
            set(obj.keys()) == REQUIRED_KEYS
            and obj.get("verdict") in VALID_VERDICTS
            and normalize_domain(obj.get("tamper_domain")) in VALID_DOMAINS
            and isinstance(obj.get("tampered_region"), str)
            and isinstance(obj.get("evidence"), list)
        )
        raw_verdict = str(obj.get("verdict", "")).strip().lower()
        if raw_verdict in VALID_VERDICTS:
            verdict = raw_verdict
        elif raw_verdict in {"yes", "possibly manipulated", "manipulated"}:
            verdict = "tampered"
        elif raw_verdict in {"no", "not tampered", "genuine"}:
            verdict = "authentic"
        tamper_domain = normalize_domain(obj.get("tamper_domain"))

    if verdict == "unknown":
        lowered = raw.lower()
        if "not tampered" in lowered or "authentic" in lowered:
            verdict = "authentic"
        elif "tampered" in lowered or "manipulated" in lowered:
            verdict = "tampered"

    return {
        "valid_json": valid_json,
        "valid_schema": schema_valid,
        "parse_error": error,
        "parsed": obj,
        "pred_verdict": verdict,
        "pred_tamper_domain": tamper_domain,
    }


def load_model(base_model: str, adapter: str | None, dtype: torch.dtype, device: str):
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        base_model,
        torch_dtype=dtype,
        device_map={"": device},
        trust_remote_code=True,
    )
    if adapter is not None:
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model


def infer(model, processor, image_path: str, prompt: str, device: str, max_new_tokens: int) -> str:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
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
    return processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()


def run_variant(
    name: str,
    base_model: str,
    adapter: str | None,
    processor,
    rows: list[dict[str, Any]],
    dtype: torch.dtype,
    device: str,
    max_new_tokens: int,
) -> list[str]:
    print("loading", name, adapter or base_model)
    model = load_model(base_model, adapter, dtype, device)
    outputs = []
    for row in rows:
        print("infer", name, row["index"], row["image"])
        outputs.append(infer(model, processor, row["image"], row["user_prompt"], device, max_new_tokens))
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return outputs


def pct(num: int, den: int) -> str:
    if den == 0:
        return "n/a"
    return f"{num / den:.4f}"


def compute_metrics(records: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    total = len(records)
    tampered = [r for r in records if r["label"]["verdict"] == "tampered"]
    authentic = [r for r in records if r["label"]["verdict"] == "authentic"]
    valid_json = sum(r["predictions"][variant]["valid_json"] for r in records)
    verdict_correct = sum(
        r["predictions"][variant]["pred_verdict"] == r["label"]["verdict"] for r in records
    )
    tampered_hit = sum(r["predictions"][variant]["pred_verdict"] == "tampered" for r in tampered)
    authentic_hit = sum(r["predictions"][variant]["pred_verdict"] == "authentic" for r in authentic)
    domain_hit = sum(
        r["predictions"][variant]["pred_tamper_domain"] == r["label"]["tamper_domain"] for r in tampered
    )

    per_domain: dict[str, dict[str, int | str]] = {}
    domain_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        domain_groups[record["label"]["source_domain"]].append(record)
    for domain, group in sorted(domain_groups.items()):
        correct = sum(r["predictions"][variant]["pred_verdict"] == r["label"]["verdict"] for r in group)
        per_domain[domain] = {
            "correct": correct,
            "total": len(group),
            "accuracy": pct(correct, len(group)),
        }

    return {
        "valid_json_rate": {"correct": valid_json, "total": total, "value": pct(valid_json, total)},
        "verdict_accuracy": {"correct": verdict_correct, "total": total, "value": pct(verdict_correct, total)},
        "tampered_recall": {"correct": tampered_hit, "total": len(tampered), "value": pct(tampered_hit, len(tampered))},
        "authentic_accuracy": {"correct": authentic_hit, "total": len(authentic), "value": pct(authentic_hit, len(authentic))},
        "tamper_domain_accuracy": {"correct": domain_hit, "total": len(tampered), "value": pct(domain_hit, len(tampered))},
        "per_domain_verdict_accuracy": per_domain,
    }


def write_summary(path: Path, metrics: dict[str, Any], records: list[dict[str, Any]], variants: list[str]) -> None:
    lines = ["# Stage1 eval_p30 three-way evaluation", ""]
    lines.extend(
        [
            "| model | valid_json_rate | verdict_accuracy | tampered_recall | authentic_accuracy | tamper_domain_accuracy |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for variant in variants:
        m = metrics[variant]
        lines.append(
            "| {variant} | {valid} ({valid_n}/{total}) | {verdict} ({verdict_n}/{total}) | "
            "{tampered} ({tampered_n}/{tampered_total}) | {authentic} ({authentic_n}/{authentic_total}) | "
            "{domain} ({domain_n}/{domain_total}) |".format(
                variant=variant,
                valid=m["valid_json_rate"]["value"],
                valid_n=m["valid_json_rate"]["correct"],
                total=m["valid_json_rate"]["total"],
                verdict=m["verdict_accuracy"]["value"],
                verdict_n=m["verdict_accuracy"]["correct"],
                tampered=m["tampered_recall"]["value"],
                tampered_n=m["tampered_recall"]["correct"],
                tampered_total=m["tampered_recall"]["total"],
                authentic=m["authentic_accuracy"]["value"],
                authentic_n=m["authentic_accuracy"]["correct"],
                authentic_total=m["authentic_accuracy"]["total"],
                domain=m["tamper_domain_accuracy"]["value"],
                domain_n=m["tamper_domain_accuracy"]["correct"],
                domain_total=m["tamper_domain_accuracy"]["total"],
            )
        )

    lines.extend(["", "## Per-domain verdict accuracy", ""])
    for variant in variants:
        lines.extend([f"### {variant}", "", "| source_domain | accuracy | correct/total |", "|---|---:|---:|"])
        for domain, row in metrics[variant]["per_domain_verdict_accuracy"].items():
            lines.append(f"| {domain} | {row['accuracy']} | {row['correct']}/{row['total']} |")
        lines.append("")

    lines.extend(["## Predictions", ""])
    lines.extend(
        [
            "| idx | source_domain | label | " + " | ".join(variants) + " | image |",
            "|---:|---|---|" + "|".join("---" for _ in variants) + "|---|",
        ]
    )
    for record in records:
        label = f"{record['label']['verdict']} / {record['label']['tamper_domain']}"
        preds = []
        for variant in variants:
            pred = record["predictions"][variant]
            valid = "json" if pred["valid_json"] else "non-json"
            preds.append(f"{pred['pred_verdict']} / {pred['pred_tamper_domain']} / {valid}")
        lines.append(
            f"| {record['index']} | {record['label']['source_domain']} | {label} | "
            f"{' | '.join(preds)} | `{record['image']}` |"
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = load_eval_rows(Path(args.data), Path(args.labels))
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    processor = AutoProcessor.from_pretrained(args.base_model, trust_remote_code=True)

    variant_specs = [
        ("base", None),
        (args.first_adapter_name, args.old_adapter),
        (args.second_adapter_name, args.json_adapter),
    ]
    outputs = {
        name: run_variant(name, args.base_model, adapter, processor, rows, dtype, device, args.max_new_tokens)
        for name, adapter in variant_specs
    }

    records = []
    for idx, row in enumerate(rows):
        predictions = {}
        for name, _ in variant_specs:
            raw = outputs[name][idx]
            predictions[name] = {
                "raw": raw,
                **parse_prediction(raw),
            }
        records.append(
            {
                "index": row["index"],
                "image": row["image"],
                "label": row["label"],
                "predictions": predictions,
            }
        )

    variants = [name for name, _ in variant_specs]
    metrics = {name: compute_metrics(records, name) for name in variants}

    output_jsonl = Path(args.output_jsonl)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with output_jsonl.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    summary_md = Path(args.summary_md)
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    write_summary(summary_md, metrics, records, variants)

    print("wrote_jsonl", output_jsonl)
    print("wrote_summary", summary_md)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
