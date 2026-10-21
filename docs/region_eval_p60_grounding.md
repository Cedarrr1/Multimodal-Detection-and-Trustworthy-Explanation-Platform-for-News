# region_eval_p60 Grounding Evaluation

This experiment is a lightweight region grounding check for the image forensics
module.

It evaluates bbox-prompt conditioned mask refinement / grounding. It is not an
automatic forged-region discovery evaluation, because every bbox prompt is
computed from the GT mask.

## Dataset

`region_eval_p60` contains 60 tampered samples:

- Photoshop: 20 CASIA tampered images with `CASIA 2 Groundtruth` masks.
- DeepFake: 20 FaceApp tampered images with `test_mask` masks.
- AIGC-Editing: 20 SD-inpaint eval tampered images with `Tp/mask` masks.

The builder extracts image/mask pairs into
`artifacts/region_eval/region_eval_p60` and writes `manifest.jsonl`. Each row
stores the resolved image, resolved mask, image size, GT-mask-derived bbox, and
mask area ratio.

Build command:

```bash
python tools/build_region_eval_p60.py
```

## Evaluation

For each sample:

1. Load the GT mask and compute the GT bbox.
2. Run `bbox_mask_baseline` by filling that bbox as a rectangular mask.
3. Optionally run `sam_refinement` using image + GT bbox as SAM input.
4. Compare predicted masks against the GT mask.

Metrics:

- IoU
- Dice
- pixel Precision
- pixel Recall
- pixel F1
- per-domain mean IoU and pixel F1

Baseline-only smoke command:

```bash
python tools/eval_region_grounding_p60.py --skip-sam
```

SAM command, when a checkpoint is available:

```bash
python tools/eval_region_grounding_p60.py \
  --sam-checkpoint /path/to/sam_vit_b_01ec64.pth \
  --sam-model-type vit_b
```

If `segment_anything` is installed, the evaluator uses it first. Otherwise it
falls back to the SAM implementation vendored under `MFLM/model/SAM`. The
repository currently does not include a SAM checkpoint, so `sam_refinement` is
reported as `not_run` unless `--sam-checkpoint` is provided.

## Outputs

- `artifacts/region_eval/region_eval_p60/results.jsonl`
- `artifacts/region_eval/region_eval_p60/summary.json`
- `artifacts/region_eval/region_eval_p60/summary.md`

The summary repeats the boundary statement so the result is not described as
automatic localization or automatic forged-region discovery.
