# region_eval_p150_gtmask_to_sam GT Mask to SAM Grounding

## Boundary

GT mask -> GT bbox -> SAM bbox prompt -> predicted mask; evaluates bbox-prompt mask refinement, not automatic forged-region discovery

## Setup

- samples: 150
- bbox matches manifest: 150/150
- sam status: run
- sam checkpoint: `weight/sam_vit_b_01ec64.pth`
- mask threshold: > 0

## Overall

| method | n | IoU | Dice/F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| bbox_from_gtmask | 150 | 0.7234 | 0.8099 | 0.7234 | 1.0000 |
| sam_from_gtbbox | 150 | 0.7408 | 0.8282 | 0.8773 | 0.8391 |

## By Domain

| domain | method | n | IoU | Dice/F1 |
|---|---|---:|---:|---:|
| aigc_editing | bbox_from_gtmask | 50 | 0.5735 | 0.6991 |
| aigc_editing | sam_from_gtbbox | 50 | 0.6952 | 0.7945 |
| deepfake | bbox_from_gtmask | 50 | 0.9532 | 0.9755 |
| deepfake | sam_from_gtbbox | 50 | 0.7473 | 0.8331 |
| photoshop | bbox_from_gtmask | 50 | 0.6436 | 0.7551 |
| photoshop | sam_from_gtbbox | 50 | 0.7798 | 0.8568 |
