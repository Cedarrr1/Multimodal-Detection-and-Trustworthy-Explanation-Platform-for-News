# Stage2 DeepFake News Benchmark

This is a controlled `title + body + image` benchmark for two separable risks:
DeepFake image manipulation and text-image semantic mismatch. It is not
real-world news fact checking.

## Build Data

Generate and freeze neutral captions:

```bash
python tools/generate_stage2_deepfake_captions_qwen_vl.py \
  --output-root artifacts/stage2/deepfake_news_caption_pool \
  --per-source-split 500 \
  --batch-size 4 \
  --resume
```

Build balanced train/dev/final pairs:

```bash
python tools/build_stage2_deepfake_news_pairs.py \
  --captions artifacts/stage2/deepfake_news_caption_pool/captions.jsonl \
  --output-root artifacts/stage2/deepfake_news_pairs \
  --train-per-cell 200 \
  --dev-per-cell 50 \
  --final-per-cell 100
```

Convert the training split and mix it with Stage1 DeepFake rehearsal rows:

```bash
python tools/convert_stage2_deepfake_news_to_qwen_vl.py \
  --input artifacts/stage2/deepfake_news_pairs/train_raw.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_json

python tools/mix_stage2_deepfake_news_with_stage1.py \
  --stage2-data artifacts/lora_data/stage2_deepfake_news_json/llamafactory_qwen_vl_sft.jsonl \
  --stage2-manifest artifacts/lora_data/stage2_deepfake_news_json/manifest.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_mixed_json
```

Convert dev/final separately for evaluation:

```bash
python tools/convert_stage2_deepfake_news_to_qwen_vl.py \
  --input artifacts/stage2/deepfake_news_pairs/dev_raw.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_dev_json

python tools/convert_stage2_deepfake_news_to_qwen_vl.py \
  --input artifacts/stage2/deepfake_news_pairs/final_raw.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_final_json
```

### V2 Attribute-Strong Mismatch

The v2 quick-fix split keeps the same controlled task and fusion rule, but makes
mismatched pairs depend on stronger visible attribute conflicts between two
single-person portraits. The builder records `mismatch_score`,
`mismatch_reasons`, and donor/target attribute diagnostics for audit.

```bash
python tools/build_stage2_deepfake_news_pairs_v2.py \
  --captions artifacts/stage2/deepfake_news_caption_pool/captions.jsonl \
  --output-root artifacts/stage2/deepfake_news_pairs_v2 \
  --train-per-cell 200 \
  --dev-per-cell 50 \
  --final-per-cell 100
```

Convert v2 train/dev/final:

```bash
python tools/convert_stage2_deepfake_news_to_qwen_vl.py \
  --input artifacts/stage2/deepfake_news_pairs_v2/train_raw.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_v2_json

python tools/convert_stage2_deepfake_news_to_qwen_vl.py \
  --input artifacts/stage2/deepfake_news_pairs_v2/dev_raw.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_v2_dev_json

python tools/convert_stage2_deepfake_news_to_qwen_vl.py \
  --input artifacts/stage2/deepfake_news_pairs_v2/final_raw.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_v2_final_json
```

Mix v2 Stage2 rows with mismatch oversampling and Stage1 DeepFake rehearsal:

```bash
python tools/mix_stage2_deepfake_news_with_stage1_v2.py \
  --stage2-data artifacts/lora_data/stage2_deepfake_news_v2_json/llamafactory_qwen_vl_sft.jsonl \
  --stage2-manifest artifacts/lora_data/stage2_deepfake_news_v2_json/manifest.jsonl \
  --output-root artifacts/lora_data/stage2_deepfake_news_v2_mixed_json
```

### V3 Claim-Level Relation Data

The v3 relation data upgrades text-image consistency from binary
`consistent|mismatched` to claim-level `supports|contradicts|unrelated|insufficient`.
It is relation-only supervision and deliberately excludes image manipulation
labels from the assistant target.

Build raw train/dev/final from v2:

```bash
python tools/build_stage2_relation_v3_data.py \
  --v2-root artifacts/stage2/deepfake_news_pairs_v2 \
  --output-root artifacts/stage2/relation_v3
```

Convert train/dev/final:

```bash
python tools/convert_stage2_relation_v3_to_qwen_vl.py \
  --input artifacts/stage2/relation_v3/train_raw.jsonl \
  --output-root artifacts/lora_data/stage2_relation_v3_json

python tools/convert_stage2_relation_v3_to_qwen_vl.py \
  --input artifacts/stage2/relation_v3/dev_raw.jsonl \
  --output-root artifacts/lora_data/stage2_relation_v3_dev_json

python tools/convert_stage2_relation_v3_to_qwen_vl.py \
  --input artifacts/stage2/relation_v3/final_raw.jsonl \
  --output-root artifacts/lora_data/stage2_relation_v3_final_json
```

## Train And Evaluate

Train a new adapter without overwriting Stage1 domain boost:

```bash
llamafactory-cli train configs/llamafactory/qwen2_5_vl_lora_stage2_deepfake_news_json.yaml
```

For v2:

```bash
llamafactory-cli train configs/llamafactory/qwen2_5_vl_lora_stage2_deepfake_news_v2_json.yaml
```

For v3 relation-only:

```bash
llamafactory-cli train configs/llamafactory/qwen2_5_vl_lora_stage2_relation_v3_claim_json.yaml
```

Evaluate dev/final:

```bash
python tools/eval_stage2_deepfake_news.py \
  --data artifacts/lora_data/stage2_deepfake_news_final_json/llamafactory_qwen_vl_sft.jsonl \
  --manifest artifacts/lora_data/stage2_deepfake_news_final_json/manifest.jsonl \
  --output-jsonl artifacts/eval/stage2_deepfake_news_final_predictions.jsonl \
  --summary-json artifacts/eval/stage2_deepfake_news_final_summary.json \
  --summary-md artifacts/eval/stage2_deepfake_news_final_summary.md \
  --pred-mask-dir artifacts/eval/stage2_deepfake_news_final_masks \
  --adapter artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_json \
  --resume
```

For v2 final, switch to:

```bash
python tools/eval_stage2_deepfake_news.py \
  --data artifacts/lora_data/stage2_deepfake_news_v2_final_json/llamafactory_qwen_vl_sft.jsonl \
  --manifest artifacts/lora_data/stage2_deepfake_news_v2_final_json/manifest.jsonl \
  --output-jsonl artifacts/eval/stage2_deepfake_news_v2_final_predictions.jsonl \
  --summary-json artifacts/eval/stage2_deepfake_news_v2_final_summary.json \
  --summary-md artifacts/eval/stage2_deepfake_news_v2_final_summary.md \
  --pred-mask-dir artifacts/eval/stage2_deepfake_news_v2_final_masks \
  --adapter artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_v2_json \
  --resume
```

For v3 relation final:

```bash
python tools/eval_stage2_relation_v3.py \
  --data artifacts/lora_data/stage2_relation_v3_final_json/llamafactory_qwen_vl_sft.jsonl \
  --manifest artifacts/lora_data/stage2_relation_v3_final_json/manifest.jsonl \
  --output-jsonl artifacts/eval/stage2_relation_v3_final_predictions.jsonl \
  --summary-json artifacts/eval/stage2_relation_v3_final_summary.json \
  --summary-md artifacts/eval/stage2_relation_v3_final_summary.md \
  --adapter artifacts/lora_runs/qwen2_5_vl_relation_v3_claim_json \
  --resume
```

Export a manual audit sheet:

```bash
python tools/audit_stage2_deepfake_news_pairs.py \
  --input artifacts/stage2/deepfake_news_pairs/final_raw.jsonl \
  --output-html artifacts/stage2/deepfake_news_pairs/final_audit.html \
  --sample-size 80
```

For v2:

```bash
python tools/audit_stage2_deepfake_news_pairs.py \
  --input artifacts/stage2/deepfake_news_pairs_v2/final_raw.jsonl \
  --output-html artifacts/stage2/deepfake_news_pairs_v2/final_audit.html \
  --sample-size 80
```

Run the fixed six-key report path after training:

```bash
python -m fake_news_forensics.pipeline.cli \
  --input examples/sample_news.json \
  --output artifacts/reports/stage2_deepfake_news_report.json \
  --report-task stage2-deepfake-news \
  --forensics-backend qwen-lora \
  --stage2-adapter artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_v2_json
```

Run the v3 split-adapter report path:

```bash
python -m fake_news_forensics.pipeline.cli \
  --input examples/sample_news.json \
  --output artifacts/reports/stage3_deepfake_news_v3_report.json \
  --report-task stage3-deepfake-news-v3 \
  --forensics-backend qwen-lora \
  --relation-backend qwen-lora \
  --image-adapter artifacts/lora_runs/qwen2_5_vl_stage1_domain_boost_json \
  --relation-adapter artifacts/lora_runs/qwen2_5_vl_relation_v3_claim_json
```

The fixed fusion rule is:

```text
final_news_verdict = fake_news
iff image_verdict == tampered or text_image_relation == mismatched
otherwise credible
```

For v3, `insufficient` is not credible. The deterministic fusion rule is:

```text
if image_verdict == tampered -> fake_news
elif text_image_relation in {contradicts, unrelated} -> fake_news
elif text_image_relation == insufficient -> uncertain
else -> credible
```

## Current Results

### V3 Claim-Level Relation Data

The v3 code path is implemented and the relation-only data is generated.
Training is pending GPU availability.

Artifacts:

- raw data: `artifacts/stage2/relation_v3`
- train ShareGPT: `artifacts/lora_data/stage2_relation_v3_json`
- dev ShareGPT: `artifacts/lora_data/stage2_relation_v3_dev_json`
- final ShareGPT: `artifacts/lora_data/stage2_relation_v3_final_json`
- schema: `schemas/stage2_relation_v3_report.schema.json`
- train config: `configs/llamafactory/qwen2_5_vl_lora_stage2_relation_v3_claim_json.yaml`

Data scale:

| split | easy v2 | hard/medium v3 | total |
|---|---:|---:|---:|
| train | 800 | 1600 | 2400 |
| dev | 200 | 400 | 600 |
| final | 400 | 800 | 1200 |

V3 relation labels:

| label | meaning |
|---|---|
| `supports` | Visible image content supports the claim. |
| `contradicts` | The same visual context provides clear opposite evidence. |
| `unrelated` | Image and claim lack enough subject or scene linkage. |
| `insufficient` | The image is related, but the claim needs time, identity, causality, viewpoint, or event-truth evidence unavailable from one image. |

Generated train distribution:

- overall relation: `supports=800`, `contradicts=800`, `unrelated=400`, `insufficient=400`
- difficulty: `easy=800`, `medium=400`, `hard=1200`
- counterfactual pairs: `100`

The hard/medium subset is balanced by source image: each source contributes one
support, one contradiction, one unrelated, and one insufficient relation item.

### V2 Quick Fix

Adapter: `artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_v2_json`

Train split: `1200` rows, including `800` Stage2 v2 controlled title/body/image
rows, `200` mismatched oversample rows, and `200` Stage1 DeepFake image-level
rehearsal rows. The mixed split is balanced for `image_verdict`
(`600` authentic / `600` tampered) and `text_image_relation` (`600` consistent /
`600` mismatched).

Raw splits:

- train: `800` rows, four cells x200
- dev: `200` rows, four cells x50
- final: `400` rows, four cells x100

Mismatch diagnostics:

- train mismatch score: minimum `4`, mean `6.83`, fallbacks `0`
- final mismatch score: minimum `4`, mean `6.50`, fallbacks `0`

Dev (`200`, four cells x50):

- valid JSON/schema: `1.0000` / `1.0000`
- image verdict accuracy: `0.8950`
- DeepFake recall / FFHQ authentic accuracy: `0.9400` / `0.8500`
- text-image relation accuracy / balanced accuracy: `0.9800` / `0.9800`
- final news verdict accuracy: `0.9400`
- exact core accuracy: `0.8900`
- FaceApp tampered IoU / pixel F1: `0.6169` / `0.7380`
- FFHQ empty-mask accuracy / FP-mask rate: `0.8500` / `0.1500`

Final (`400`, four cells x100):

- valid JSON/schema: `1.0000` / `1.0000`
- image verdict accuracy: `0.8600`
- DeepFake recall / FFHQ authentic accuracy: `0.9300` / `0.7900`
- text-image relation accuracy / balanced accuracy: `0.9750` / `0.9750`
- final news verdict accuracy: `0.9250`
- exact core accuracy: `0.8350`
- FaceApp tampered IoU / pixel F1: `0.6134` / `0.7312`
- FFHQ empty-mask accuracy / FP-mask rate: `0.7900` / `0.2100`

V2 final four-cell accuracy:

| cell | final_accuracy | exact_core_accuracy | n |
|---|---:|---:|---:|
| `authentic_consistent` | 0.8200 | 0.8200 | 100 |
| `authentic_mismatched` | 0.9500 | 0.7100 | 100 |
| `tampered_consistent` | 0.9300 | 0.9300 | 100 |
| `tampered_mismatched` | 1.0000 | 0.8800 | 100 |

V2 fixes the v1 text-image mismatch bottleneck. The main remaining issue is
image forensics false positives on authentic FFHQ portraits, visible in the
`0.7900` FFHQ authentic accuracy and `0.2100` FP-mask rate.

### V1 Baseline

Adapter: `artifacts/lora_runs/qwen2_5_vl_stage2_deepfake_news_json`

Train split: `1000` rows, including `800` Stage2 controlled title/body/image rows
and `200` Stage1 DeepFake image-level rehearsal rows.

Dev (`200`, four cells x50):

- valid JSON/schema: `1.0000` / `1.0000`
- image verdict accuracy: `0.9100`
- DeepFake recall / FFHQ authentic accuracy: `0.9000` / `0.9200`
- text-image relation accuracy / balanced accuracy: `0.9050` / `0.9050`
- final news verdict accuracy: `0.9100`
- exact core accuracy: `0.8150`
- FaceApp tampered IoU / pixel F1: `0.5930` / `0.7071`

Final (`400`, four cells x100):

- valid JSON/schema: `1.0000` / `0.9975`
- image verdict accuracy: `0.8700`
- DeepFake recall / FFHQ authentic accuracy: `0.8500` / `0.8900`
- text-image relation accuracy / balanced accuracy: `0.7550` / `0.7550`
- final news verdict accuracy: `0.8025`
- exact core accuracy: `0.6500`
- FaceApp tampered IoU / pixel F1: `0.5627` / `0.6718`
- FFHQ empty-mask accuracy / FP-mask rate: `0.8950` / `0.1050`

Final four-cell accuracy:

| cell | final_accuracy | exact_core_accuracy | n |
|---|---:|---:|---:|
| `authentic_consistent` | 0.8900 | 0.8900 | 100 |
| `authentic_mismatched` | 0.5300 | 0.4200 | 100 |
| `tampered_consistent` | 0.8500 | 0.8500 | 100 |
| `tampered_mismatched` | 0.9400 | 0.4400 | 100 |

The current adapter is usable for the first closed loop, but the final split shows
that mismatched text-image relation detection is the main bottleneck. A next
training pass should prioritize harder mismatched pairs and stricter schema
rehearsal instead of simply repeating the same configuration.
