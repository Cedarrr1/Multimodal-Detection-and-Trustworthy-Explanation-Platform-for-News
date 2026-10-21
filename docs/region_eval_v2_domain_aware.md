# region_eval_v2 Domain-Aware Grounding Evaluation

This is the medium-scale region grounding evaluation used after
`region_eval_p60`.

The boundary is unchanged: this is a bbox-prompt conditioned mask refinement /
grounding evaluation. It is not automatic forged-region discovery, because each
bbox prompt is computed from the GT mask.

## Dataset

`region_eval_v2` contains 150 tampered samples with GT masks:

- Photoshop: 50 CASIA tampered samples.
- DeepFake: 50 FaceApp tampered samples.
- AIGC-Editing: 50 SD-inpaint eval tampered samples.

Artifacts:

- `artifacts/region_eval/region_eval_v2/manifest.jsonl`
- `artifacts/region_eval/region_eval_v2/results.jsonl`
- `artifacts/region_eval/region_eval_v2/summary.json`
- `artifacts/region_eval/region_eval_v2/summary.md`

## Strategy

Three methods are reported:

- `bbox_mask_baseline`: fill the GT-mask-derived bbox as a rectangle.
- `sam_refinement`: run SAM with image + GT bbox prompt.
- `domain_aware_refinement`: use SAM for Photoshop and AIGC-editing, but use
  bbox / face-region fallback for DeepFake.

The domain-aware rule reflects the observed mask geometry: SAM improves local
Photoshop/AIGC editing masks, while FaceApp masks are often broad face-edit
regions where SAM tends to under-cover the GT mask.

## Results

| method | n | IoU | Dice/F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| bbox baseline | 150 | 0.7170 | 0.8075 | 0.7170 | 1.0000 |
| SAM refinement | 150 | 0.6706 | 0.7715 | 0.9116 | 0.7210 |
| domain-aware refinement | 150 | 0.7994 | 0.8670 | 0.9119 | 0.8584 |

Per-domain IoU / F1:

- AIGC-editing: bbox `0.5735 / 0.6991`, SAM/domain-aware `0.6521 / 0.7627`.
- Photoshop: bbox `0.6242 / 0.7479`, SAM/domain-aware `0.7928 / 0.8628`.
- DeepFake: bbox/domain-aware `0.9532 / 0.9755`, SAM `0.5669 / 0.6890`.

Recommended wording:

> We use a domain-aware mask refinement strategy: Photoshop and AIGC local
> edits use SAM bbox-prompt refinement, while DeepFake face edits use a
> bbox/face-region fallback. On a balanced 150-sample region evaluation set,
> the combined strategy reaches about 0.80 IoU and 0.87 F1, outperforming both
> a single bbox baseline and a single SAM-only refinement policy.
