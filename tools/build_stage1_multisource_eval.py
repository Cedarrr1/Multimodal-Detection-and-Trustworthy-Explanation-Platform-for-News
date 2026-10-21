#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PROMPT = (
    "<image>\n"
    "Analyze whether this image has been digitally manipulated. "
    "Return only valid JSON with verdict, tampered_region, tamper_domain, and evidence."
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


@dataclass(frozen=True)
class Candidate:
    source: str
    source_path: Path
    archive_member: str | None
    label: str
    source_domain: str
    tamper_domain: str
    id: str


def image_id(member: str) -> str:
    return Path(member).stem


def is_image(name: str) -> bool:
    return Path(name).suffix.lower() in IMAGE_EXTS and not name.endswith("/")


def path_keys(value: Any) -> set[str]:
    if value is None:
        return set()
    text = str(value).replace("\\", "/")
    path = Path(text)
    keys = {text, path.name, path.stem}
    if "/" in text:
        keys.add(text.rsplit("/", 1)[-1])
    return {key for key in keys if key}


def load_excluded_ids(paths: Iterable[Path]) -> set[str]:
    excluded: set[str] = set()
    fields = ["id", "image", "resolved_image", "archive_member", "image_member", "sample_key"]
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for field in fields:
                excluded.update(path_keys(row.get(field)))
    return excluded


def list_zip_members(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as zf:
        return sorted(name for name in zf.namelist() if is_image(name))


def list_tar_members(path: Path) -> list[str]:
    with tarfile.open(path) as tf:
        return sorted(member.name for member in tf.getmembers() if member.isfile() and is_image(member.name))


def candidate_keys(candidate: Candidate) -> set[str]:
    keys = {candidate.id}
    if candidate.archive_member is not None:
        keys.update(path_keys(candidate.archive_member))
    keys.update(path_keys(candidate.source_path))
    return {key for key in keys if key}


def is_excluded(candidate: Candidate, excluded_ids: set[str]) -> bool:
    return bool(candidate_keys(candidate) & excluded_ids)


def sample_group(candidates: list[Candidate], per_label: int, seed: int, excluded_ids: set[str]) -> list[Candidate]:
    usable = [c for c in candidates if not is_excluded(c, excluded_ids)]
    rng = random.Random(seed)
    rng.shuffle(usable)
    return usable[:per_label]


def stable_group_seed(seed: int, key: tuple[str, str]) -> int:
    digest = hashlib.sha256(f"{seed}:{key[0]}:{key[1]}".encode("utf-8")).hexdigest()
    return seed + int(digest[:8], 16)


def discover_casia(path: Path) -> tuple[list[Candidate], list[dict[str, Any]]]:
    if not path.exists():
        return [], [{"source": "CASIA", "status": "skipped", "reason": f"missing {path}"}]
    members = list_zip_members(path)
    out: list[Candidate] = []
    for member in members:
        if member.startswith("CASIA2/Au/"):
            out.append(
                Candidate(
                    source="CASIA",
                    source_path=path,
                    archive_member=member,
                    label="authentic",
                    source_domain="photoshop",
                    tamper_domain="none",
                    id=image_id(member),
                )
            )
        elif member.startswith("CASIA2/Tp/"):
            out.append(
                Candidate(
                    source="CASIA",
                    source_path=path,
                    archive_member=member,
                    label="tampered",
                    source_domain="photoshop",
                    tamper_domain="photoshop",
                    id=image_id(member),
                )
            )
    return out, []


def discover_zip_source(path: Path, source: str, label: str, source_domain: str, tamper_domain: str) -> tuple[list[Candidate], list[dict[str, Any]]]:
    if not path.exists():
        return [], [{"source": source, "status": "skipped", "reason": f"missing {path}"}]
    return [
        Candidate(
            source=source,
            source_path=path,
            archive_member=member,
            label=label,
            source_domain=source_domain,
            tamper_domain=tamper_domain,
            id=image_id(member),
        )
        for member in list_zip_members(path)
    ], []


def discover_faceapp(path: Path, splits: set[str]) -> tuple[list[Candidate], list[dict[str, Any]]]:
    if not path.exists():
        return [], [{"source": "FaceApp", "status": "skipped", "reason": f"missing {path}"}]
    allowed_prefixes = tuple(f"faceapp/{split}/" for split in sorted(splits))
    candidates = [
        Candidate(
            source="FaceApp",
            source_path=path,
            archive_member=member,
            label="tampered",
            source_domain="deepfake",
            tamper_domain="deepfake",
            id=image_id(member),
        )
        for member in list_zip_members(path)
        if member.startswith(allowed_prefixes)
    ]
    return candidates, []


def discover_sd_inpaint(paths: list[Path]) -> tuple[list[Candidate], list[dict[str, Any]]]:
    out: list[Candidate] = []
    skipped: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            skipped.append({"source": f"SD-inpaint:{path.name}", "status": "skipped", "reason": f"missing {path}"})
            continue
        for member in list_tar_members(path):
            if "/Au/image/" in f"/{member}":
                out.append(
                    Candidate(
                        source="SD-inpaint",
                        source_path=path,
                        archive_member=member,
                        label="authentic",
                        source_domain="aigc_editing",
                        tamper_domain="none",
                        id=image_id(member),
                    )
                )
            elif "/Tp/image/" in f"/{member}":
                out.append(
                    Candidate(
                        source="SD-inpaint",
                        source_path=path,
                        archive_member=member,
                        label="tampered",
                        source_domain="aigc_editing",
                        tamper_domain="aigc_inpaint",
                        id=image_id(member),
                    )
                )
    return out, skipped


def discover_directory_source(path: Path, source: str) -> tuple[list[Candidate], list[dict[str, Any]]]:
    if not path.exists():
        return [], [{"source": source, "status": "skipped", "reason": f"missing {path}"}]
    candidates: list[Candidate] = []
    for image in sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS):
        lowered = str(image.relative_to(path)).lower()
        if any(token in lowered for token in ["authentic", "original", "/au/", "\\au\\", "real"]):
            label = "authentic"
            tamper_domain = "none"
        elif any(token in lowered for token in ["tampered", "forged", "/tp/", "\\tp\\", "fake", "splice"]):
            label = "tampered"
            tamper_domain = "photoshop"
        else:
            continue
        candidates.append(
            Candidate(
                source=source,
                source_path=image,
                archive_member=None,
                label=label,
                source_domain="photoshop",
                tamper_domain=tamper_domain,
                id=image.stem,
            )
        )
    if not candidates:
        return [], [{"source": source, "status": "skipped", "reason": f"no labeled images found under {path}"}]
    return candidates, []


def extract_candidate(candidate: Candidate, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        return
    if candidate.archive_member is None:
        shutil.copy2(candidate.source_path, output_path)
    elif candidate.source_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(candidate.source_path) as zf:
            with zf.open(candidate.archive_member) as src, output_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    elif candidate.source_path.suffix.lower() == ".tar":
        with tarfile.open(candidate.source_path) as tf:
            member = tf.getmember(candidate.archive_member)
            src = tf.extractfile(member)
            if src is None:
                raise FileNotFoundError(candidate.archive_member)
            with src, output_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    else:
        raise ValueError(f"unsupported source archive: {candidate.source_path}")


def output_relpath(candidate: Candidate) -> Path:
    suffix = Path(candidate.archive_member or candidate.source_path.name).suffix.lower()
    safe_id = candidate.id.replace("/", "_").replace("\\", "_")
    return Path(candidate.source_domain) / candidate.source / candidate.label / f"{safe_id}{suffix}"


def target_for(candidate: Candidate) -> dict[str, Any]:
    verdict = "tampered" if candidate.label == "tampered" else "authentic"
    return {
        "verdict": verdict,
        "tampered_region": "unknown" if verdict == "tampered" else "none",
        "tamper_domain": candidate.tamper_domain,
        "evidence": [],
    }


def build_dataset(args: argparse.Namespace) -> dict[str, Any]:
    skipped: list[dict[str, Any]] = []
    discovered: list[Candidate] = []

    for candidates, skip in [
        discover_casia(args.casia_zip),
        discover_zip_source(args.ffhq_zip, "FFHQ", "authentic", "deepfake", "none"),
        discover_faceapp(args.faceapp_zip, set(args.faceapp_splits.split(","))),
        discover_sd_inpaint(([args.sd_train_tar] if args.include_sd_train else []) + [args.sd_eval_tar]),
        discover_directory_source(args.imd2020_root, "IMD2020"),
        discover_directory_source(args.columbia_root, "Columbia"),
        discover_directory_source(args.coverage_root, "Coverage"),
    ]:
        discovered.extend(candidates)
        skipped.extend(skip)

    excluded_ids = load_excluded_ids(args.exclude_manifest)
    by_group: dict[tuple[str, str], list[Candidate]] = {}
    for candidate in discovered:
        by_group.setdefault((candidate.source, candidate.label), []).append(candidate)

    selected: list[Candidate] = []
    group_stats: dict[str, Any] = {}
    for key in sorted(by_group):
        group = by_group[key]
        chosen = sample_group(group, args.per_label, stable_group_seed(args.seed, key), excluded_ids)
        selected.extend(chosen)
        group_stats[f"{key[0]}:{key[1]}"] = {
            "available": len(group),
            "selected": len(chosen),
            "excluded_by_manifest": sum(is_excluded(c, excluded_ids) for c in group),
        }

    args.output_root.mkdir(parents=True, exist_ok=True)
    image_root = args.output_root / "images"
    manifest_path = args.output_root / "manifest.jsonl"
    labels_path = args.output_root / "eval_labels.jsonl"
    sft_path = args.output_root / "llamafactory_qwen_vl_sft.jsonl"
    meta_path = args.output_root / "dataset_meta.json"

    with manifest_path.open("w", encoding="utf-8") as mf, labels_path.open("w", encoding="utf-8") as lf, sft_path.open("w", encoding="utf-8") as sf:
        for idx, candidate in enumerate(selected):
            rel = output_relpath(candidate)
            image_path = image_root / rel
            extract_candidate(candidate, image_path)
            target = target_for(candidate)
            row_id = f"{candidate.source}_{candidate.label}_{candidate.id}"
            manifest = {
                "id": row_id,
                "image": str(rel),
                "resolved_image": str(image_path),
                "source": candidate.source,
                "source_domain": candidate.source_domain,
                "label": candidate.label,
                "verdict": target["verdict"],
                "tamper_domain": target["tamper_domain"],
                "source_path": str(candidate.source_path),
                "archive_member": candidate.archive_member,
            }
            label = {
                "id": row_id,
                "image": str(rel),
                "source": candidate.source,
                "source_domain": candidate.source_domain,
                "is_tampered": candidate.label == "tampered",
                "verdict": target["verdict"],
                "tampered_region": target["tampered_region"],
                "tamper_domain": target["tamper_domain"],
                "evidence": [],
            }
            sft = {
                "id": row_id,
                "images": [str(image_path)],
                "messages": [
                    {"role": "user", "content": PROMPT},
                    {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)},
                ],
            }
            mf.write(json.dumps(manifest, ensure_ascii=False) + "\n")
            lf.write(json.dumps(label, ensure_ascii=False) + "\n")
            sf.write(json.dumps(sft, ensure_ascii=False) + "\n")

    meta = {
        "output_root": str(args.output_root),
        "per_label": args.per_label,
        "seed": args.seed,
        "total": len(selected),
        "group_stats": group_stats,
        "skipped_sources": skipped,
        "excluded_manifests": [str(p) for p in args.exclude_manifest],
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    validate_output(args.output_root)
    return meta


def validate_output(output_root: Path) -> None:
    sft_rows = [json.loads(line) for line in (output_root / "llamafactory_qwen_vl_sft.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    label_rows = [json.loads(line) for line in (output_root / "eval_labels.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest_rows = [json.loads(line) for line in (output_root / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if not (len(sft_rows) == len(label_rows) == len(manifest_rows)):
        raise ValueError("row count mismatch between sft, labels, and manifest")
    for idx, (sft, label) in enumerate(zip(sft_rows, label_rows)):
        images = sft.get("images")
        messages = sft.get("messages")
        if not isinstance(images, list) or len(images) != 1:
            raise ValueError(f"row {idx}: expected one image")
        if not Path(images[0]).exists():
            raise FileNotFoundError(images[0])
        if not isinstance(messages, list) or len(messages) != 2:
            raise ValueError(f"row {idx}: expected two messages")
        user_prompt = str(messages[0].get("content", ""))
        if user_prompt.count("<image>") != 1:
            raise ValueError(f"row {idx}: prompt must contain exactly one <image>")
        lowered_prompt = user_prompt.lower()
        if any(token in lowered_prompt for token in ["photoshop", "deepfake", "aigc", "casia", "faceapp", "ffhq", "inpaint"]):
            raise ValueError(f"row {idx}: prompt leaks source/domain")
        target = json.loads(str(messages[1].get("content", "")))
        if set(target) != {"verdict", "tampered_region", "tamper_domain", "evidence"}:
            raise ValueError(f"row {idx}: bad target keys")
        if target["verdict"] not in {"authentic", "tampered"}:
            raise ValueError(f"row {idx}: bad verdict")
        if target["tamper_domain"] not in {"photoshop", "deepfake", "aigc_inpaint", "none", "unknown"}:
            raise ValueError(f"row {idx}: bad tamper_domain")
        if label["image"] not in images[0]:
            raise ValueError(f"row {idx}: label image mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a small multisource Stage1 image-forensics eval set.")
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/lora_data/stage1_multisource_eval"))
    parser.add_argument("--per-label", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--casia-zip", type=Path, default=Path("dataset/photoshop/CASIAv2.zip"))
    parser.add_argument("--ffhq-zip", type=Path, default=Path("dataset/deepfake/ffhq.zip"))
    parser.add_argument("--faceapp-zip", type=Path, default=Path("dataset/deepfake/faceapp.zip"))
    parser.add_argument("--faceapp-splits", default="train,test", help="Comma-separated FaceApp image splits. Mask directories are never used.")
    parser.add_argument("--sd-train-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/train.tar"))
    parser.add_argument("--sd-eval-tar", type=Path, default=Path("dataset/aigc/SD_inpaint_dataset/eval.tar"))
    parser.add_argument("--include-sd-train", action="store_true", help="Include SD-inpaint train.tar in addition to eval.tar.")
    parser.add_argument("--imd2020-root", type=Path, default=Path("dataset/photoshop/IMD2020"))
    parser.add_argument("--columbia-root", type=Path, default=Path("dataset/photoshop/Columbia"))
    parser.add_argument("--coverage-root", type=Path, default=Path("dataset/photoshop/Coverage"))
    parser.add_argument(
        "--exclude-manifest",
        type=Path,
        action="append",
        default=[
            Path("artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl"),
            Path("artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl"),
        ],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.per_label < 1:
        raise ValueError("--per-label must be positive")
    meta = build_dataset(args)
    print("wrote", args.output_root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
