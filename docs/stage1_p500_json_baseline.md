# Stage1 p500_json Baseline

This document freezes the first usable Stage1 image-forensics baseline for the
fake-news forensics project.

## Baseline

- Base model: `Qwen/Qwen2.5-VL-3B-Instruct`
- Training stack: LLaMA-Factory SFT + LoRA
- Main adapter: `artifacts/lora_runs/qwen2_5_vl_stage1_p500_json`
- Training config: `configs/llamafactory/qwen2_5_vl_lora_stage1_p500_json.yaml`
- Dataset registry: `configs/llamafactory/dataset_info.json`
- Dataset key: `stage1_mmtd_p500_json`
- Dataset file: `artifacts/lora_data/stage1_mmtd_p500_json/llamafactory_qwen_vl_sft.jsonl`
- Evaluation split: `artifacts/lora_data/stage1_mmtd_eval_p30_json`
- Evaluation summary: `artifacts/eval/stage1_eval_p30_base_jsonp100_jsonp500_max420_summary.md`
- Evaluation generation cap: `max_new_tokens=420`

## Training Data

`stage1_mmtd_p500_json` contains 1500 samples built from MMTD/FakeShield-style
Stage1 image forensics supervision. The fixed `eval_p30` split was excluded from
training.

| source_domain | authentic | tampered | total |
|---|---:|---:|---:|
| `photoshop_edit` | 250 | 250 | 500 |
| `deepfake_face` | 250 | 250 | 500 |
| `aigc_edit` | 250 | 250 | 500 |
| total | 750 | 750 | 1500 |

The assistant target is strict JSON:

```json
{
  "verdict": "authentic|tampered",
  "tampered_region": "...",
  "tamper_domain": "photoshop|deepfake|aigc_inpaint|none|unknown",
  "evidence": ["..."]
}
```

## Training Result

From `artifacts/lora_runs/qwen2_5_vl_stage1_p500_json/train_results.json` and
`trainer_state.json`:

- global steps: 3000
- epochs: 2.0
- train loss: 0.8768975688318411
- adapter size: 59941192 bytes (`adapter_model.safetensors`)

## Fixed eval_p30 Result

The fixed train-out `eval_p30` comparison at `max_new_tokens=420`:

| model | valid_json_rate | verdict_accuracy | tampered_recall | authentic_accuracy | tamper_domain_accuracy |
|---|---:|---:|---:|---:|---:|
| base | 29/30 | 16/30 | 15/15 | 1/15 | 0/15 |
| json_p100 | 30/30 | 18/30 | 8/15 | 10/15 | 8/15 |
| json_p500 | 30/30 | 22/30 | 11/15 | 11/15 | 11/15 |

Per-domain verdict accuracy for `json_p500`:

| source_domain | correct/total |
|---|---:|
| `aigc_edit` | 9/10 |
| `deepfake_face` | 8/10 |
| `photoshop_edit` | 5/10 |

## Interpretation

`p500_json` is the current Stage1 baseline. It solves the minimum requirement for
structured image-level forensics output and improves over `json_p100` on verdict,
tampered recall, authentic accuracy, and tamper-domain accuracy.

The main weakness is Photoshop local manipulation. In `eval_p30`, four
Photoshop-tampered examples are predicted as authentic by `json_p500`, while
deepfake and AIGC cases improve clearly. The next Stage1 experiment should add
crop/region/patch supervision for Photoshop samples without losing the general
three-domain behavior already learned by `p500_json`.

## Follow-up Crop Enhancement

The planned Photoshop crop/region follow-up has been completed:

- experiment record: `docs/stage1_photoshop_crop_experiment.md`
- adapter: `artifacts/lora_runs/qwen2_5_vl_stage1_photoshop_crop_json`
- evaluation: `artifacts/eval/stage1_eval_p30_p500_vs_photoshop_crop_max420_summary.md`

On the same fixed `eval_p30` split with `max_new_tokens=420`,
`photoshop_crop` improved over `json_p500`:

| model | valid_json | verdict_acc | tampered_recall | authentic_acc | domain_acc | photoshop_acc |
|---|---:|---:|---:|---:|---:|---:|
| `json_p500` | 30/30 | 22/30 | 11/15 | 11/15 | 11/15 | 5/10 |
| `photoshop_crop` | 30/30 | 26/30 | 14/15 | 12/15 | 14/15 | 9/10 |

`p500_json` remains the first stable Stage1 baseline. The crop-enhanced adapter
is now the current best Stage1 image-forensics candidate for downstream Stage2
experiments.

## Reproduction Pointers

Train:

```bash
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib_fakeshield \
llamafactory-cli train configs/llamafactory/qwen2_5_vl_lora_stage1_p500_json.yaml
```

Evaluate with the same generation cap used in the accepted baseline:

```bash
CUDA_VISIBLE_DEVICES=0 MPLCONFIGDIR=/tmp/matplotlib_fakeshield \
python tools/eval_stage1_p30_three_way.py \
  --old-adapter artifacts/lora_runs/qwen2_5_vl_stage1_p100_json \
  --json-adapter artifacts/lora_runs/qwen2_5_vl_stage1_p500_json \
  --first-adapter-name json_p100 \
  --second-adapter-name json_p500 \
  --output-jsonl artifacts/eval/stage1_eval_p30_base_jsonp100_jsonp500_max420.jsonl \
  --summary-md artifacts/eval/stage1_eval_p30_base_jsonp100_jsonp500_max420_summary.md \
  --max-new-tokens 420
```
