# region_eval_p150 Chain Evaluation

## Boundary

image -> LoRA tampered/domain prediction -> GT mask-derived bbox prompt -> bbox or SAM mask refinement -> GT mask metrics; bbox prompts come from GT masks, so this is not automatic forged-region discovery

This experiment uses GT masks only to derive bbox prompts. It evaluates bbox-prompt mask refinement / grounding, not automatic forged-region discovery.

## Image-Level LoRA Predictions

- samples: `150`
- predictions found: `150/150`
- valid JSON: `0.8467 (127/150)`
- valid schema: `0.8467 (127/150)`
- tampered recall: `0.5733 (86/150)`
- domain accuracy: `0.3800 (57/150)`
- selected bbox fallback: `137/150`
- selected SAM refinement: `13/150`

## Mask Refinement

Primary chain metrics below use the existing p150 region-eval SAM setting. The GT-mask-to-SAM closure is reported separately because it uses SAM multimask best-of-3.

| method | n | IoU | Dice/F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| bbox_mask_baseline | 150 | 0.7234 | 0.8099 | 0.7234 | 1.0000 |
| sam_refinement | 150 | 0.6656 | 0.7690 | 0.9065 | 0.7258 |
| domain_aware_oracle | 150 | 0.7944 | 0.8645 | 0.9068 | 0.8633 |
| domain_aware_predicted | 150 | 0.7427 | 0.8245 | 0.7573 | 0.9832 |

## Per Domain Mask Metrics

| domain | method | n | IoU | Dice/F1 |
|---|---|---:|---:|---:|
| aigc_editing | bbox_mask_baseline | 50 | 0.5735 | 0.6991 |
| aigc_editing | sam_refinement | 50 | 0.6521 | 0.7627 |
| aigc_editing | domain_aware_oracle | 50 | 0.6521 | 0.7627 |
| aigc_editing | domain_aware_predicted | 50 | 0.5806 | 0.7042 |
| deepfake | bbox_mask_baseline | 50 | 0.9532 | 0.9755 |
| deepfake | sam_refinement | 50 | 0.5669 | 0.6890 |
| deepfake | domain_aware_oracle | 50 | 0.9532 | 0.9755 |
| deepfake | domain_aware_predicted | 50 | 0.9532 | 0.9755 |
| photoshop | bbox_mask_baseline | 50 | 0.6436 | 0.7551 |
| photoshop | sam_refinement | 50 | 0.7778 | 0.8553 |
| photoshop | domain_aware_oracle | 50 | 0.7778 | 0.8553 |
| photoshop | domain_aware_predicted | 50 | 0.6943 | 0.7940 |

## GT Mask to SAM Closure

- output dir: `artifacts/region_eval/region_eval_p150_gtmask_to_sam`
- bbox matches manifest: `150/150`
- SAM status: `run`
- SAM setting: `segment-anything multimask_output=True, select highest predicted-IoU score`

| method | n | IoU | Dice/F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| bbox_from_gtmask | 150 | 0.7234 | 0.8099 | 0.7234 | 1.0000 |
| sam_from_gtbbox | 150 | 0.7408 | 0.8282 | 0.8773 | 0.8391 |
| domain_aware_predicted_bestof3 | 150 | 0.7483 | 0.8286 | 0.7543 | 0.9915 |

## Strategy

Oracle policy: Photoshop and AIGC-editing use SAM; DeepFake uses bbox / face-region fallback.

Predicted policy: use the LoRA-predicted tamper domain; Photoshop/AIGC predictions use SAM, DeepFake/none/unknown fallback to bbox.
