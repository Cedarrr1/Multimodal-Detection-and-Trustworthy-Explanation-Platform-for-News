# Stage1 Photoshop Crop Enhancement

This experiment follows the `stage1_mmtd_p500_json` baseline with a focused
Photoshop local-manipulation enhancement run.

## Motivation

The first usable Stage1 baseline, `qwen2_5_vl_stage1_p500_json`, reached stable
JSON output and good overall performance, but remained weak on Photoshop local
edits:

- `photoshop_edit` verdict accuracy: 5/10
- failure pattern: 4 Photoshop-tampered samples predicted as authentic

The crop experiment tests whether full-image plus deterministic region-crop
training improves local manipulation recall without hurting deepfake/AIGC
behavior.

## Data

Dataset:

- key: `stage1_photoshop_crop_json`
- path: `artifacts/lora_data/stage1_photoshop_crop_json/llamafactory_qwen_vl_sft.jsonl`
- records: 1000
- authentic: 500
- tampered: 500
- image count: 1500 files under `artifacts/lora_data/stage1_photoshop_crop_json/images`

Each record has two images:

1. full image
2. deterministic crop

Target JSON extends Stage1 with `region_focus`:

```json
{
  "verdict": "authentic|tampered",
  "tampered_region": "...",
  "tamper_domain": "photoshop|none",
  "evidence": ["..."],
  "region_focus": "..."
}
```

Important caveat: CASIAv2 in `dataset/photoshop/CASIAv2.zip` did not expose
ground-truth masks in the checked archive, so this is weak region supervision
from MMTD text plus deterministic crop heuristics, not true pixel-level
localization.

## Training

Config:

- `configs/llamafactory/qwen2_5_vl_lora_stage1_photoshop_crop_json.yaml`

Initialization:

- base model: `Qwen/Qwen2.5-VL-3B-Instruct`
- initial adapter: `artifacts/lora_runs/qwen2_5_vl_stage1_p500_json`

Command:

```bash
CUDA_VISIBLE_DEVICES=2 MPLCONFIGDIR=/tmp/matplotlib_fakeshield \
/home/Master/CaoMJ/.mamba/envs/vfd/bin/llamafactory-cli train \
  configs/llamafactory/qwen2_5_vl_lora_stage1_photoshop_crop_json.yaml
```

Result:

- output: `artifacts/lora_runs/qwen2_5_vl_stage1_photoshop_crop_json`
- global steps: 2500
- epochs: 1.0
- train loss: 0.6213052071869374
- train runtime: 2340.3506 seconds
- adapter size: 59941192 bytes

## Fixed eval_p30 Result

Evaluation:

- split: `artifacts/lora_data/stage1_mmtd_eval_p30_json`
- generation cap: `max_new_tokens=420`
- summary: `artifacts/eval/stage1_eval_p30_p500_vs_photoshop_crop_max420_summary.md`
- raw predictions: `artifacts/eval/stage1_eval_p30_p500_vs_photoshop_crop_max420.jsonl`

Command:

```bash
CUDA_VISIBLE_DEVICES=2 MPLCONFIGDIR=/tmp/matplotlib_fakeshield \
/home/Master/CaoMJ/.mamba/envs/vfd/bin/python tools/eval_stage1_p30_three_way.py \
  --old-adapter artifacts/lora_runs/qwen2_5_vl_stage1_p500_json \
  --json-adapter artifacts/lora_runs/qwen2_5_vl_stage1_photoshop_crop_json \
  --first-adapter-name json_p500 \
  --second-adapter-name photoshop_crop \
  --output-jsonl artifacts/eval/stage1_eval_p30_p500_vs_photoshop_crop_max420.jsonl \
  --summary-md artifacts/eval/stage1_eval_p30_p500_vs_photoshop_crop_max420_summary.md \
  --max-new-tokens 420
```

| model | valid_json | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|
| `json_p500` | 30/30 | 22/30 | 11/15 | 11/15 | 11/15 |
| `photoshop_crop` | 30/30 | 26/30 | 14/15 | 12/15 | 14/15 |

Per-domain verdict accuracy:

| model | photoshop_edit | deepfake_face | aigc_edit |
|---|---:|---:|---:|
| `json_p500` | 5/10 | 8/10 | 9/10 |
| `photoshop_crop` | 9/10 | 8/10 | 9/10 |

## Interpretation

The crop enhancement is a clear positive Stage1 result on the fixed eval set:

- overall verdict accuracy improved by 4 samples
- tampered recall improved by 3 samples
- tamper-domain accuracy improved by 3 samples
- Photoshop verdict accuracy improved from 5/10 to 9/10
- deepfake and AIGC verdict accuracy did not regress

`qwen2_5_vl_stage1_photoshop_crop_json` should be treated as the current best
Stage1 image-forensics candidate, while `qwen2_5_vl_stage1_p500_json` remains the
first stable baseline and ablation reference.

## Remaining Errors

Wrong verdicts for `photoshop_crop` on fixed `eval_p30`:

| idx | source_domain | label | prediction | image |
|---:|---|---|---|---|
| 5 | `photoshop_edit` | `tampered / photoshop` | `authentic / none` | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2/image/Tp_S_CNN_M_N_nat00044_nat00044_10557.jpg` |
| 10 | `deepfake_face` | `authentic / none` | `tampered / deepfake` | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_03340.png` |
| 13 | `deepfake_face` | `authentic / none` | `tampered / deepfake` | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_02051.png` |
| 21 | `aigc_edit` | `authentic / none` | `tampered / photoshop` | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Au/image/000000270708.jpg` |

The only remaining false negative among tampered samples is idx 5, still a
Photoshop tampered example predicted authentic. The other three remaining errors
are false positives on authentic images.

## Next Steps

- Use `qwen2_5_vl_stage1_photoshop_crop_json` as the default Stage1 visual
  forensics module for Stage2 claim-image fusion.
- Keep `qwen2_5_vl_stage1_p500_json` as a baseline ablation in Stage2.
- If more Photoshop work is needed, prioritize real mask/bbox supervision rather
  than additional heuristic crops.
- Add a small authenticity calibration set, because the remaining non-Photoshop
  errors are false positives on authentic images.
