#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _conversation_text(row: dict, speaker: str) -> str:
    for turn in row.get("conversations", []):
        if turn.get("from") == speaker:
            return str(turn.get("value", "")).replace("<image>", "").strip()
    raise ValueError(f"missing {speaker!r} conversation for row {row.get('id')!r}")


def convert(input_path: Path, image_root: Path, output_path: Path) -> int:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for row in data:
            image_path = (image_root / row["image"]).resolve()
            user_text = _conversation_text(row, "human")
            assistant_text = _conversation_text(row, "gpt")

            record = {
                "id": row.get("id", row["image"]),
                "images": [str(image_path)],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": str(image_path)},
                            {"type": "text", "text": user_text},
                        ],
                    },
                    {
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": assistant_text},
                        ],
                    },
                ],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(data)


def convert_llamafactory(input_path: Path, image_root: Path, output_path: Path) -> int:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for row in data:
            image_path = (image_root / row["image"]).resolve()
            user_text = _conversation_text(row, "human")
            assistant_text = _conversation_text(row, "gpt")
            record = {
                "id": row.get("id", row["image"]),
                "images": [str(image_path)],
                "messages": [
                    {"role": "user", "content": f"<image>{user_text}"},
                    {"role": "assistant", "content": assistant_text},
                ],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("artifacts/lora_data/stage1_mmtd_demo/stage1_dte_sft.json"),
    )
    parser.add_argument(
        "--image-root",
        type=Path,
        default=Path("artifacts/lora_data/stage1_mmtd_demo/images"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/lora_data/stage1_mmtd_demo/qwen_vl_sft.jsonl"),
    )
    parser.add_argument(
        "--llamafactory-output",
        type=Path,
        default=Path("artifacts/lora_data/stage1_mmtd_demo/llamafactory_qwen_vl_sft.jsonl"),
    )
    args = parser.parse_args()

    count = convert(args.input, args.image_root, args.output)
    print(f"wrote {count} records to {args.output}")
    lf_count = convert_llamafactory(args.input, args.image_root, args.llamafactory_output)
    print(f"wrote {lf_count} records to {args.llamafactory_output}")


if __name__ == "__main__":
    main()
