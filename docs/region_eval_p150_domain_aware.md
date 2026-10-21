# region_eval_p150 Domain-Aware Grounding Evaluation

This experiment evaluates bbox-prompt conditioned mask refinement / grounding.
It is not automatic forged-region discovery: every bbox prompt is computed from
the GT mask.

## Dataset

`region_eval_p150` contains 150 tampered samples with GT masks:

- Photoshop: 50 CASIA v2 tampered samples.
- AIGC-Editing: 50 SD-inpaint tampered samples.
- DeepFake: 50 FaceApp tampered samples.

Sampling excludes images found in:

- `artifacts/lora_data/stage1_mmtd_p500_json/manifest.jsonl`
- `artifacts/lora_data/stage1_mmtd_eval_p30_json/manifest.jsonl`

No fallback to excluded samples was needed.

Artifacts:

- `artifacts/region_eval/region_eval_p150/samples.jsonl`
- `artifacts/region_eval/region_eval_p150/manifest.jsonl`
- `artifacts/region_eval/region_eval_p150/domain_predictions.jsonl`
- `artifacts/region_eval/region_eval_p150/results.jsonl`
- `artifacts/region_eval/region_eval_p150/summary.json`
- `artifacts/region_eval/region_eval_p150/summary.md`

## Methods

- `bbox_mask_baseline`: fill the GT-mask-derived bbox as a rectangle.
- `sam_refinement`: run SAM with image + GT bbox prompt.
- `domain_aware_oracle`: Photoshop/AIGC use SAM; DeepFake uses bbox fallback.
- `domain_aware_predicted`: use Qwen2.5-VL p500 LoRA predicted domain; Photoshop/AIGC predictions use SAM, DeepFake/none/unknown fallback to bbox.

## Results

| method | n | IoU | Dice/F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| bbox baseline | 150 | 0.7234 | 0.8099 | 0.7234 | 1.0000 |
| SAM refinement | 150 | 0.6656 | 0.7690 | 0.9065 | 0.7258 |
| domain-aware oracle | 150 | 0.7944 | 0.8645 | 0.9068 | 0.8633 |
| domain-aware predicted | 150 | 0.7427 | 0.8245 | 0.7573 | 0.9832 |

Per-domain IoU / F1:

- AIGC-editing: bbox `0.5735 / 0.6991`, SAM/oracle `0.6521 / 0.7627`, predicted `0.5806 / 0.7042`.
- Photoshop: bbox `0.6436 / 0.7551`, SAM/oracle `0.7778 / 0.8553`, predicted `0.6943 / 0.7940`.
- DeepFake: bbox/oracle/predicted `0.9532 / 0.9755`, SAM `0.5669 / 0.6890`.

LoRA domain prediction stats:

- predictions found: `150/150`
- valid JSON/schema: `127/150`
- fallback to bbox: `137/150`

Recommended wording:

> We evaluate region-level grounding under a GT-bbox prompt, not automatic
> region discovery. On a balanced 150-sample region set, domain-aware oracle
> refinement reaches 0.794 IoU / 0.864 F1, outperforming bbox-only and SAM-only
> policies. A predicted-domain variant using the image-level LoRA reaches 0.743
> IoU / 0.825 F1, showing a system-realistic but domain-prediction-limited
> refinement path.
