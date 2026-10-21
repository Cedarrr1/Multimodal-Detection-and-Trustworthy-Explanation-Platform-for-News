# Multimodal Detection and Trustworthy Explanation Platform for News

A research project for multimodal news verification, combining image forensics, tampered-region localization, text-image consistency analysis, and structured evidence-based explanations.

## Project structure

- `fake_news_forensics/`: news input processing and report generation pipeline.
- `tools/`: data preparation, model inference, localization, and evaluation utilities.
- `configs/llamafactory/`: Qwen2.5-VL LoRA training configurations.
- `schemas/`: structured report JSON schemas.
- `examples/`: sample news input.
- `DTE-FDM/` and `MFLM/`: image forensic and localization model code.
- `scripts/`: training, inference, and evaluation scripts.
- `artifacts/`: available experiment data and evaluation outputs.
- `weight/`: available pretrained weights, stored with Git LFS.

## Download

Install [Git LFS](https://git-lfs.com/) before cloning to download the model weight files:

```sh
git lfs install
git clone https://github.com/Cedarrr1/Multimodal-Detection-and-Trustworthy-Explanation-Platform-for-News.git
cd Multimodal-Detection-and-Trustworthy-Explanation-Platform-for-News
```

## Pipeline usage

From the repository root, inspect the available pipeline options:

```sh
python -m fake_news_forensics.pipeline.cli --help
```

`examples/sample_news.json` documents the news input format. Set its image path to an existing image before running an example. Training and model-backed inference require the relevant model dependencies, base models, LoRA adapters, and datasets referenced by the selected configuration; the presence of configuration files does not imply that all trained adapters or datasets are included.

The legacy model components have their own dependency requirements; see `DTE-FDM/pyproject.toml` and the scripts under `scripts/`. See [FAST_FORWARD_PLAN.md](FAST_FORWARD_PLAN.md) for experiment notes and the development roadmap.

## Acknowledgements

This repository includes code based on FakeShield, LLaVA, and related model libraries. Existing source attributions and notices are retained in their respective files. Third-party code, datasets, and pretrained weights remain subject to their original terms.
