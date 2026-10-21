#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import random
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rel_image(path: str, output_html: Path) -> str:
    image = Path(path)
    try:
        return html.escape(str(image.resolve().relative_to(output_html.parent.resolve())))
    except ValueError:
        return html.escape(str(image.resolve()))


def render(rows: list[dict[str, Any]], output_html: Path, source_path: Path) -> None:
    parts = [
        "<!doctype html>",
        "<meta charset=\"utf-8\">",
        "<title>Stage2 DeepFake News Pair Audit</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;color:#111}",
        "table{border-collapse:collapse;width:100%}",
        "td,th{border:1px solid #ddd;padding:8px;vertical-align:top}",
        "img{max-width:220px;max-height:220px;display:block}",
        ".meta{font-size:12px;color:#555}",
        "</style>",
        "<h1>Stage2 DeepFake News Pair Audit</h1>",
        f"<p class=\"meta\">source: {html.escape(str(source_path))}; sampled rows: {len(rows)}</p>",
        "<table>",
        "<thead><tr><th>image</th><th>article text</th><th>labels</th><th>source</th></tr></thead>",
        "<tbody>",
    ]
    for row in rows:
        target = row.get("target", {})
        labels = {
            "cell": row.get("cell"),
            "image_verdict": target.get("image_verdict"),
            "text_image_relation": target.get("text_image_relation"),
            "final_news_verdict": target.get("final_news_verdict"),
        }
        parts.extend(
            [
                "<tr>",
                f"<td><img src=\"{rel_image(str(row['image']), output_html)}\"><div class=\"meta\">{html.escape(str(row.get('id')))}</div></td>",
                f"<td><strong>{html.escape(str(row.get('title')))}</strong><br>{html.escape(str(row.get('body')))}</td>",
                f"<td><pre>{html.escape(json.dumps(labels, ensure_ascii=False, indent=2))}</pre></td>",
                (
                    "<td class=\"meta\">"
                    f"target: {html.escape(str(row.get('source_key')))}<br>"
                    f"donor: {html.escape(str(row.get('donor_source_key')))}"
                    "</td>"
                ),
                "</tr>",
            ]
        )
    parts.extend(["</tbody>", "</table>"])
    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text("\n".join(parts) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> None:
    rows = load_jsonl(args.input)
    if args.cell:
        rows = [row for row in rows if row.get("cell") == args.cell]
    rng = random.Random(args.seed)
    rng.shuffle(rows)
    sampled = rows[: args.sample_size]
    render(sampled, args.output_html, args.input)
    jsonl_path = args.output_html.with_suffix(".jsonl")
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in sampled:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("wrote", args.output_html)
    print("wrote", jsonl_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a random HTML audit sheet for Stage2 DeepFake-news pairs.")
    parser.add_argument("--input", type=Path, default=Path("artifacts/stage2/deepfake_news_pairs/final_raw.jsonl"))
    parser.add_argument("--output-html", type=Path, default=Path("artifacts/stage2/deepfake_news_pairs/final_audit.html"))
    parser.add_argument("--sample-size", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20260718)
    parser.add_argument("--cell")
    args = parser.parse_args()
    if args.sample_size < 1:
        raise ValueError("--sample-size must be positive")
    return args


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
