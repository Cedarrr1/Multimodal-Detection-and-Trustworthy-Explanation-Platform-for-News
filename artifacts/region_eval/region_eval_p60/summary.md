# region_eval_p60 Mask Refinement / Grounding Evaluation

Boundary: **bbox-prompt conditioned mask refinement / grounding evaluation; not automatic forged-region discovery**.

Each bbox prompt is computed from the GT mask. These numbers therefore evaluate mask refinement under a provided bbox prompt, not automatic forged-region discovery.

## Overall

| method | status | n | IoU | Dice | pixel Precision | pixel Recall | pixel F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| bbox_mask_baseline | run | 60 | 0.7087 | 0.8031 | 0.7087 | 1.0000 | 0.8031 |
| sam_refinement | run | 60 | 0.6809 | 0.7830 | 0.8947 | 0.7398 | 0.7830 |

## Per Domain

| method | domain | n | mean IoU | mean pixel F1 |
|---|---|---:|---:|---:|
| bbox_mask_baseline | aigc_editing | 20 | 0.5431 | 0.6807 |
| bbox_mask_baseline | deepfake | 20 | 0.9416 | 0.9692 |
| bbox_mask_baseline | photoshop | 20 | 0.6415 | 0.7594 |
| sam_refinement | aigc_editing | 20 | 0.7285 | 0.8330 |
| sam_refinement | deepfake | 20 | 0.5821 | 0.7054 |
| sam_refinement | photoshop | 20 | 0.7322 | 0.8105 |

## Samples

| id | domain | bbox_xyxy | bbox IoU | bbox F1 | SAM IoU | SAM F1 |
|---|---|---|---:|---:|---:|---:|
| region_eval_p60_aigc_editing_001 | aigc_editing | `[0, 0, 512, 404]` | 0.4661 | 0.6359 | 0.6046 | 0.7535 |
| region_eval_p60_aigc_editing_002 | aigc_editing | `[0, 322, 512, 512]` | 0.6568 | 0.7929 | 0.7934 | 0.8848 |
| region_eval_p60_aigc_editing_003 | aigc_editing | `[265, 179, 457, 373]` | 0.5672 | 0.7238 | 0.5424 | 0.7033 |
| region_eval_p60_aigc_editing_004 | aigc_editing | `[0, 0, 106, 506]` | 0.5680 | 0.7245 | 0.6324 | 0.7748 |
| region_eval_p60_aigc_editing_005 | aigc_editing | `[47, 0, 451, 273]` | 0.1238 | 0.2203 | 0.5375 | 0.6991 |
| region_eval_p60_aigc_editing_006 | aigc_editing | `[0, 258, 511, 512]` | 0.6351 | 0.7768 | 0.7256 | 0.8410 |
| region_eval_p60_aigc_editing_007 | aigc_editing | `[0, 0, 512, 134]` | 0.6157 | 0.7621 | 0.9441 | 0.9713 |
| region_eval_p60_aigc_editing_008 | aigc_editing | `[0, 297, 181, 512]` | 0.9348 | 0.9663 | 0.9343 | 0.9661 |
| region_eval_p60_aigc_editing_009 | aigc_editing | `[38, 321, 326, 512]` | 0.4940 | 0.6613 | 0.9226 | 0.9598 |
| region_eval_p60_aigc_editing_010 | aigc_editing | `[261, 195, 512, 512]` | 0.3405 | 0.5080 | 0.5747 | 0.7299 |
| region_eval_p60_aigc_editing_011 | aigc_editing | `[273, 0, 512, 321]` | 0.7864 | 0.8804 | 0.9358 | 0.9668 |
| region_eval_p60_aigc_editing_012 | aigc_editing | `[0, 0, 421, 14]` | 0.5612 | 0.7190 | 0.8744 | 0.9330 |
| region_eval_p60_aigc_editing_013 | aigc_editing | `[0, 50, 417, 284]` | 0.2855 | 0.4442 | 0.8589 | 0.9241 |
| region_eval_p60_aigc_editing_014 | aigc_editing | `[211, 0, 512, 80]` | 0.7475 | 0.8555 | 0.8365 | 0.9110 |
| region_eval_p60_aigc_editing_015 | aigc_editing | `[0, 247, 410, 512]` | 0.3815 | 0.5523 | 0.5665 | 0.7233 |
| region_eval_p60_aigc_editing_016 | aigc_editing | `[52, 74, 284, 259]` | 0.7298 | 0.8438 | 0.5355 | 0.6975 |
| region_eval_p60_aigc_editing_017 | aigc_editing | `[70, 28, 281, 509]` | 0.4031 | 0.5745 | 0.7024 | 0.8252 |
| region_eval_p60_aigc_editing_018 | aigc_editing | `[0, 199, 512, 512]` | 0.4561 | 0.6265 | 0.7138 | 0.8330 |
| region_eval_p60_aigc_editing_019 | aigc_editing | `[154, 0, 512, 127]` | 0.8235 | 0.9032 | 0.8754 | 0.9336 |
| region_eval_p60_aigc_editing_020 | aigc_editing | `[76, 49, 303, 512]` | 0.2849 | 0.4434 | 0.4595 | 0.6297 |
| region_eval_p60_deepfake_001 | deepfake | `[0, 0, 299, 299]` | 0.9057 | 0.9505 | 0.4591 | 0.6293 |
| region_eval_p60_deepfake_002 | deepfake | `[0, 0, 299, 299]` | 0.9822 | 0.9910 | 0.3483 | 0.5167 |
| region_eval_p60_deepfake_003 | deepfake | `[0, 0, 299, 299]` | 0.9979 | 0.9989 | 0.3015 | 0.4633 |
| region_eval_p60_deepfake_004 | deepfake | `[0, 0, 299, 299]` | 0.8704 | 0.9307 | 0.7896 | 0.8825 |
| region_eval_p60_deepfake_005 | deepfake | `[0, 0, 299, 299]` | 0.8631 | 0.9265 | 0.2733 | 0.4293 |
| region_eval_p60_deepfake_006 | deepfake | `[0, 0, 299, 299]` | 0.8824 | 0.9375 | 0.7476 | 0.8556 |
| region_eval_p60_deepfake_007 | deepfake | `[0, 0, 299, 299]` | 0.9984 | 0.9992 | 0.2774 | 0.4343 |
| region_eval_p60_deepfake_008 | deepfake | `[0, 0, 299, 299]` | 0.9458 | 0.9721 | 0.3697 | 0.5399 |
| region_eval_p60_deepfake_009 | deepfake | `[0, 0, 299, 299]` | 0.9970 | 0.9985 | 0.8710 | 0.9310 |
| region_eval_p60_deepfake_010 | deepfake | `[0, 0, 299, 299]` | 0.9141 | 0.9551 | 0.3898 | 0.5609 |
| region_eval_p60_deepfake_011 | deepfake | `[0, 0, 299, 299]` | 0.9905 | 0.9952 | 0.3329 | 0.4995 |
| region_eval_p60_deepfake_012 | deepfake | `[0, 0, 299, 299]` | 0.9611 | 0.9802 | 0.8212 | 0.9019 |
| region_eval_p60_deepfake_013 | deepfake | `[0, 0, 299, 299]` | 0.9583 | 0.9787 | 0.3509 | 0.5195 |
| region_eval_p60_deepfake_014 | deepfake | `[0, 0, 299, 299]` | 0.8670 | 0.9288 | 0.6806 | 0.8100 |
| region_eval_p60_deepfake_015 | deepfake | `[0, 0, 299, 299]` | 0.9958 | 0.9979 | 0.9742 | 0.9869 |
| region_eval_p60_deepfake_016 | deepfake | `[0, 0, 299, 299]` | 0.9993 | 0.9997 | 0.8274 | 0.9055 |
| region_eval_p60_deepfake_017 | deepfake | `[0, 0, 299, 299]` | 0.8721 | 0.9317 | 0.7856 | 0.8800 |
| region_eval_p60_deepfake_018 | deepfake | `[0, 0, 299, 299]` | 0.9297 | 0.9636 | 0.3864 | 0.5574 |
| region_eval_p60_deepfake_019 | deepfake | `[0, 0, 299, 299]` | 0.9139 | 0.9550 | 0.7182 | 0.8360 |
| region_eval_p60_deepfake_020 | deepfake | `[0, 0, 299, 299]` | 0.9878 | 0.9939 | 0.9377 | 0.9678 |
| region_eval_p60_photoshop_001 | photoshop | `[0, 97, 234, 160]` | 0.8677 | 0.9292 | 0.9483 | 0.9735 |
| region_eval_p60_photoshop_002 | photoshop | `[112, 319, 181, 374]` | 0.5657 | 0.7227 | 0.8872 | 0.9402 |
| region_eval_p60_photoshop_003 | photoshop | `[10, 162, 121, 307]` | 0.5806 | 0.7346 | 0.9264 | 0.9618 |
| region_eval_p60_photoshop_004 | photoshop | `[431, 345, 482, 399]` | 0.6336 | 0.7757 | 0.8454 | 0.9162 |
| region_eval_p60_photoshop_005 | photoshop | `[5, 3, 64, 256]` | 0.8461 | 0.9166 | 0.5731 | 0.7286 |
| region_eval_p60_photoshop_006 | photoshop | `[263, 20, 384, 142]` | 0.4585 | 0.6287 | 0.9474 | 0.9730 |
| region_eval_p60_photoshop_007 | photoshop | `[278, 138, 323, 186]` | 0.4171 | 0.5887 | 0.3732 | 0.5435 |
| region_eval_p60_photoshop_008 | photoshop | `[43, 293, 72, 384]` | 0.9360 | 0.9669 | 0.9293 | 0.9634 |
| region_eval_p60_photoshop_009 | photoshop | `[0, 0, 184, 256]` | 0.9973 | 0.9987 | 0.2620 | 0.4152 |
| region_eval_p60_photoshop_010 | photoshop | `[1, 8, 197, 256]` | 0.6807 | 0.8100 | 0.0419 | 0.0804 |
| region_eval_p60_photoshop_011 | photoshop | `[95, 94, 145, 173]` | 0.8010 | 0.8895 | 0.8831 | 0.9379 |
| region_eval_p60_photoshop_012 | photoshop | `[191, 25, 248, 216]` | 0.5244 | 0.6880 | 0.8128 | 0.8967 |
| region_eval_p60_photoshop_013 | photoshop | `[403, 145, 579, 337]` | 0.7074 | 0.8286 | 0.9579 | 0.9785 |
| region_eval_p60_photoshop_014 | photoshop | `[438, 87, 635, 411]` | 0.4749 | 0.6440 | 0.8906 | 0.9422 |
| region_eval_p60_photoshop_015 | photoshop | `[0, 0, 194, 59]` | 0.4540 | 0.6244 | 0.9219 | 0.9593 |
| region_eval_p60_photoshop_016 | photoshop | `[189, 162, 356, 254]` | 0.5137 | 0.6788 | 0.9241 | 0.9606 |
| region_eval_p60_photoshop_017 | photoshop | `[220, 0, 296, 147]` | 0.7887 | 0.8818 | 0.8238 | 0.9034 |
| region_eval_p60_photoshop_018 | photoshop | `[279, 109, 335, 157]` | 0.7868 | 0.8807 | 0.5267 | 0.6900 |
| region_eval_p60_photoshop_019 | photoshop | `[117, 92, 272, 256]` | 0.0977 | 0.1780 | 0.4115 | 0.5830 |
| region_eval_p60_photoshop_020 | photoshop | `[78, 144, 123, 172]` | 0.6984 | 0.8224 | 0.7574 | 0.8619 |
