# region_eval_p150 Mask Refinement / Grounding Evaluation

Boundary: **bbox-prompt conditioned mask refinement / grounding evaluation; not automatic forged-region discovery**.

Each bbox prompt is computed from the GT mask. These numbers therefore evaluate mask refinement under a provided bbox prompt, not automatic forged-region discovery.

## Overall

| method | status | n | IoU | Dice | pixel Precision | pixel Recall | pixel F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| bbox_mask_baseline | run | 150 | 0.7234 | 0.8099 | 0.7234 | 1.0000 | 0.8099 |
| sam_refinement | run | 150 | 0.6656 | 0.7690 | 0.9065 | 0.7258 | 0.7690 |
| domain_aware_oracle | run | 150 | 0.7944 | 0.8645 | 0.9068 | 0.8633 | 0.8645 |
| domain_aware_predicted | run | 150 | 0.7234 | 0.8099 | 0.7234 | 1.0000 | 0.8099 |

## Per Domain

| method | domain | n | mean IoU | mean pixel F1 |
|---|---|---:|---:|---:|
| bbox_mask_baseline | aigc_editing | 50 | 0.5735 | 0.6991 |
| bbox_mask_baseline | deepfake | 50 | 0.9532 | 0.9755 |
| bbox_mask_baseline | photoshop | 50 | 0.6436 | 0.7551 |
| sam_refinement | aigc_editing | 50 | 0.6521 | 0.7627 |
| sam_refinement | deepfake | 50 | 0.5669 | 0.6890 |
| sam_refinement | photoshop | 50 | 0.7778 | 0.8553 |
| domain_aware_oracle | aigc_editing | 50 | 0.6521 | 0.7627 |
| domain_aware_oracle | deepfake | 50 | 0.9532 | 0.9755 |
| domain_aware_oracle | photoshop | 50 | 0.7778 | 0.8553 |
| domain_aware_predicted | aigc_editing | 50 | 0.5735 | 0.6991 |
| domain_aware_predicted | deepfake | 50 | 0.9532 | 0.9755 |
| domain_aware_predicted | photoshop | 50 | 0.6436 | 0.7551 |

## Domain-Aware Strategy

Oracle policy: Photoshop and AIGC-editing use SAM bbox-prompt refinement; DeepFake uses bbox / face-region fallback.

Predicted policy: use the LoRA-predicted tamper domain; Photoshop/AIGC predictions use SAM, DeepFake/none/unknown fallback to bbox.

## Predicted Domain Stats

- predictions found: `0/150`
- valid JSON: `0/150`
- valid schema: `0/150`
- fallback to bbox: `150/150`

## Samples

| id | domain | bbox_xyxy | bbox IoU | bbox F1 | SAM IoU | SAM F1 |
|---|---|---|---:|---:|---:|---:|
| region_eval_p150_aigc_editing_001 | aigc_editing | `[0, 0, 512, 404]` | 0.4661 | 0.6359 | 0.6046 | 0.7536 |
| region_eval_p150_aigc_editing_002 | aigc_editing | `[0, 322, 512, 512]` | 0.6568 | 0.7929 | 0.7931 | 0.8846 |
| region_eval_p150_aigc_editing_003 | aigc_editing | `[265, 179, 457, 373]` | 0.5672 | 0.7238 | 0.5424 | 0.7033 |
| region_eval_p150_aigc_editing_004 | aigc_editing | `[0, 0, 106, 506]` | 0.5680 | 0.7245 | 0.6324 | 0.7748 |
| region_eval_p150_aigc_editing_005 | aigc_editing | `[47, 0, 451, 273]` | 0.1238 | 0.2203 | 0.5367 | 0.6985 |
| region_eval_p150_aigc_editing_006 | aigc_editing | `[0, 258, 511, 512]` | 0.6351 | 0.7768 | 0.7258 | 0.8411 |
| region_eval_p150_aigc_editing_007 | aigc_editing | `[0, 0, 512, 134]` | 0.6157 | 0.7621 | 0.9441 | 0.9713 |
| region_eval_p150_aigc_editing_008 | aigc_editing | `[0, 297, 181, 512]` | 0.9348 | 0.9663 | 0.9344 | 0.9661 |
| region_eval_p150_aigc_editing_009 | aigc_editing | `[38, 321, 326, 512]` | 0.4940 | 0.6613 | 0.9226 | 0.9597 |
| region_eval_p150_aigc_editing_010 | aigc_editing | `[261, 195, 512, 512]` | 0.3405 | 0.5080 | 0.5747 | 0.7299 |
| region_eval_p150_aigc_editing_011 | aigc_editing | `[273, 0, 512, 321]` | 0.7864 | 0.8804 | 0.9358 | 0.9668 |
| region_eval_p150_aigc_editing_012 | aigc_editing | `[0, 0, 421, 14]` | 0.5612 | 0.7190 | 0.8744 | 0.9330 |
| region_eval_p150_aigc_editing_013 | aigc_editing | `[0, 50, 417, 284]` | 0.2855 | 0.4442 | 0.8589 | 0.9241 |
| region_eval_p150_aigc_editing_014 | aigc_editing | `[211, 0, 512, 80]` | 0.7475 | 0.8555 | 0.8363 | 0.9108 |
| region_eval_p150_aigc_editing_015 | aigc_editing | `[0, 247, 410, 512]` | 0.3815 | 0.5523 | 0.5665 | 0.7232 |
| region_eval_p150_aigc_editing_016 | aigc_editing | `[52, 74, 284, 259]` | 0.7298 | 0.8438 | 0.5356 | 0.6975 |
| region_eval_p150_aigc_editing_017 | aigc_editing | `[70, 28, 281, 509]` | 0.4031 | 0.5745 | 0.7024 | 0.8252 |
| region_eval_p150_aigc_editing_018 | aigc_editing | `[0, 199, 512, 512]` | 0.4561 | 0.6265 | 0.7138 | 0.8330 |
| region_eval_p150_aigc_editing_019 | aigc_editing | `[154, 0, 512, 127]` | 0.8235 | 0.9032 | 0.8754 | 0.9336 |
| region_eval_p150_aigc_editing_020 | aigc_editing | `[76, 49, 303, 512]` | 0.2849 | 0.4434 | 0.4597 | 0.6298 |
| region_eval_p150_aigc_editing_021 | aigc_editing | `[0, 293, 512, 512]` | 0.8232 | 0.9030 | 0.5280 | 0.6911 |
| region_eval_p150_aigc_editing_022 | aigc_editing | `[8, 392, 512, 512]` | 0.4753 | 0.6444 | 0.6863 | 0.8140 |
| region_eval_p150_aigc_editing_023 | aigc_editing | `[213, 355, 512, 502]` | 0.9228 | 0.9598 | 0.9819 | 0.9909 |
| region_eval_p150_aigc_editing_024 | aigc_editing | `[0, 314, 512, 512]` | 0.7549 | 0.8603 | 0.9264 | 0.9618 |
| region_eval_p150_aigc_editing_025 | aigc_editing | `[362, 0, 512, 58]` | 0.8322 | 0.9084 | 0.2496 | 0.3995 |
| region_eval_p150_aigc_editing_026 | aigc_editing | `[153, 150, 512, 512]` | 0.4950 | 0.6622 | 0.8257 | 0.9045 |
| region_eval_p150_aigc_editing_027 | aigc_editing | `[108, 49, 500, 391]` | 0.4083 | 0.5799 | 0.6556 | 0.7920 |
| region_eval_p150_aigc_editing_028 | aigc_editing | `[256, 0, 512, 113]` | 0.6045 | 0.7535 | 0.5096 | 0.6752 |
| region_eval_p150_aigc_editing_029 | aigc_editing | `[334, 205, 512, 386]` | 0.8167 | 0.8991 | 0.7649 | 0.8668 |
| region_eval_p150_aigc_editing_030 | aigc_editing | `[0, 332, 512, 512]` | 0.4462 | 0.6171 | 0.8440 | 0.9154 |
| region_eval_p150_aigc_editing_031 | aigc_editing | `[0, 0, 109, 158]` | 0.9375 | 0.9678 | 0.1643 | 0.2822 |
| region_eval_p150_aigc_editing_032 | aigc_editing | `[0, 0, 231, 436]` | 0.5043 | 0.6705 | 0.4591 | 0.6293 |
| region_eval_p150_aigc_editing_033 | aigc_editing | `[0, 325, 512, 475]` | 0.4230 | 0.5946 | 0.0347 | 0.0670 |
| region_eval_p150_aigc_editing_034 | aigc_editing | `[0, 394, 82, 512]` | 0.1859 | 0.3136 | 0.3250 | 0.4906 |
| region_eval_p150_aigc_editing_035 | aigc_editing | `[0, 30, 94, 512]` | 0.8425 | 0.9145 | 0.4821 | 0.6505 |
| region_eval_p150_aigc_editing_036 | aigc_editing | `[366, 367, 462, 419]` | 0.1729 | 0.2948 | 0.5401 | 0.7014 |
| region_eval_p150_aigc_editing_037 | aigc_editing | `[63, 15, 402, 502]` | 0.3478 | 0.5161 | 0.5086 | 0.6742 |
| region_eval_p150_aigc_editing_038 | aigc_editing | `[36, 228, 512, 447]` | 0.7745 | 0.8729 | 0.8025 | 0.8904 |
| region_eval_p150_aigc_editing_039 | aigc_editing | `[112, 378, 512, 498]` | 0.6479 | 0.7863 | 0.9333 | 0.9655 |
| region_eval_p150_aigc_editing_040 | aigc_editing | `[0, 24, 342, 402]` | 0.4865 | 0.6546 | 0.6675 | 0.8006 |
| region_eval_p150_aigc_editing_041 | aigc_editing | `[190, 255, 317, 512]` | 0.9730 | 0.9863 | 0.9877 | 0.9938 |
| region_eval_p150_aigc_editing_042 | aigc_editing | `[0, 0, 92, 363]` | 0.9077 | 0.9516 | 0.9853 | 0.9926 |
| region_eval_p150_aigc_editing_043 | aigc_editing | `[0, 302, 204, 512]` | 0.5913 | 0.7431 | 0.1996 | 0.3327 |
| region_eval_p150_aigc_editing_044 | aigc_editing | `[0, 412, 512, 512]` | 0.9008 | 0.9478 | 0.7174 | 0.8354 |
| region_eval_p150_aigc_editing_045 | aigc_editing | `[208, 273, 512, 512]` | 0.3403 | 0.5078 | 0.6487 | 0.7869 |
| region_eval_p150_aigc_editing_046 | aigc_editing | `[0, 0, 512, 512]` | 0.1965 | 0.3285 | 0.2913 | 0.4511 |
| region_eval_p150_aigc_editing_047 | aigc_editing | `[146, 0, 282, 387]` | 0.6927 | 0.8184 | 0.6975 | 0.8218 |
| region_eval_p150_aigc_editing_048 | aigc_editing | `[0, 371, 512, 512]` | 0.8202 | 0.9012 | 0.4580 | 0.6282 |
| region_eval_p150_aigc_editing_049 | aigc_editing | `[0, 191, 512, 512]` | 0.2684 | 0.4232 | 0.5840 | 0.7374 |
| region_eval_p150_aigc_editing_050 | aigc_editing | `[96, 91, 512, 427]` | 0.2197 | 0.3602 | 0.5760 | 0.7310 |
| region_eval_p150_deepfake_001 | deepfake | `[0, 0, 299, 299]` | 0.9057 | 0.9505 | 0.4592 | 0.6294 |
| region_eval_p150_deepfake_002 | deepfake | `[0, 0, 299, 299]` | 0.9822 | 0.9910 | 0.3483 | 0.5166 |
| region_eval_p150_deepfake_003 | deepfake | `[0, 0, 299, 299]` | 0.9979 | 0.9989 | 0.3015 | 0.4633 |
| region_eval_p150_deepfake_004 | deepfake | `[0, 0, 299, 299]` | 0.8704 | 0.9307 | 0.7897 | 0.8825 |
| region_eval_p150_deepfake_005 | deepfake | `[0, 0, 299, 299]` | 0.8631 | 0.9265 | 0.2732 | 0.4292 |
| region_eval_p150_deepfake_006 | deepfake | `[0, 0, 299, 299]` | 0.8824 | 0.9375 | 0.7478 | 0.8557 |
| region_eval_p150_deepfake_007 | deepfake | `[0, 0, 299, 299]` | 0.9984 | 0.9992 | 0.2774 | 0.4344 |
| region_eval_p150_deepfake_008 | deepfake | `[0, 0, 299, 299]` | 0.9458 | 0.9721 | 0.3697 | 0.5399 |
| region_eval_p150_deepfake_009 | deepfake | `[0, 0, 299, 299]` | 0.9970 | 0.9985 | 0.8711 | 0.9311 |
| region_eval_p150_deepfake_010 | deepfake | `[0, 0, 299, 299]` | 0.9141 | 0.9551 | 0.3898 | 0.5609 |
| region_eval_p150_deepfake_011 | deepfake | `[0, 0, 299, 299]` | 0.9905 | 0.9952 | 0.3329 | 0.4995 |
| region_eval_p150_deepfake_012 | deepfake | `[0, 0, 299, 299]` | 0.9611 | 0.9802 | 0.8213 | 0.9019 |
| region_eval_p150_deepfake_013 | deepfake | `[0, 0, 299, 299]` | 0.9583 | 0.9787 | 0.3511 | 0.5197 |
| region_eval_p150_deepfake_014 | deepfake | `[0, 0, 299, 299]` | 0.8670 | 0.9288 | 0.6805 | 0.8099 |
| region_eval_p150_deepfake_015 | deepfake | `[0, 0, 299, 299]` | 0.9958 | 0.9979 | 0.9742 | 0.9869 |
| region_eval_p150_deepfake_016 | deepfake | `[0, 0, 299, 299]` | 0.9993 | 0.9997 | 0.8274 | 0.9055 |
| region_eval_p150_deepfake_017 | deepfake | `[0, 0, 299, 299]` | 0.8721 | 0.9317 | 0.7856 | 0.8799 |
| region_eval_p150_deepfake_018 | deepfake | `[0, 0, 299, 299]` | 0.9297 | 0.9636 | 0.3863 | 0.5573 |
| region_eval_p150_deepfake_019 | deepfake | `[0, 0, 299, 299]` | 0.9139 | 0.9550 | 0.7182 | 0.8360 |
| region_eval_p150_deepfake_020 | deepfake | `[0, 0, 299, 299]` | 0.9878 | 0.9939 | 0.9376 | 0.9678 |
| region_eval_p150_deepfake_021 | deepfake | `[0, 0, 299, 299]` | 0.8267 | 0.9052 | 0.7894 | 0.8823 |
| region_eval_p150_deepfake_022 | deepfake | `[0, 0, 299, 299]` | 1.0000 | 1.0000 | 0.7309 | 0.8445 |
| region_eval_p150_deepfake_023 | deepfake | `[0, 0, 299, 299]` | 0.9679 | 0.9837 | 0.3889 | 0.5600 |
| region_eval_p150_deepfake_024 | deepfake | `[0, 0, 299, 299]` | 0.9054 | 0.9503 | 0.6829 | 0.8116 |
| region_eval_p150_deepfake_025 | deepfake | `[0, 0, 299, 299]` | 0.9048 | 0.9500 | 0.5201 | 0.6843 |
| region_eval_p150_deepfake_026 | deepfake | `[0, 0, 299, 299]` | 0.9893 | 0.9946 | 0.2971 | 0.4582 |
| region_eval_p150_deepfake_027 | deepfake | `[0, 0, 299, 299]` | 0.9877 | 0.9938 | 0.8948 | 0.9445 |
| region_eval_p150_deepfake_028 | deepfake | `[0, 0, 299, 299]` | 0.9575 | 0.9783 | 0.9205 | 0.9586 |
| region_eval_p150_deepfake_029 | deepfake | `[0, 0, 299, 299]` | 0.9420 | 0.9702 | 0.8471 | 0.9172 |
| region_eval_p150_deepfake_030 | deepfake | `[0, 0, 299, 299]` | 0.9732 | 0.9864 | 0.3385 | 0.5058 |
| region_eval_p150_deepfake_031 | deepfake | `[0, 0, 299, 299]` | 0.9769 | 0.9883 | 0.3767 | 0.5472 |
| region_eval_p150_deepfake_032 | deepfake | `[0, 0, 299, 299]` | 0.9840 | 0.9919 | 0.2727 | 0.4286 |
| region_eval_p150_deepfake_033 | deepfake | `[0, 0, 299, 299]` | 0.9012 | 0.9481 | 0.6629 | 0.7973 |
| region_eval_p150_deepfake_034 | deepfake | `[0, 0, 299, 299]` | 0.9952 | 0.9976 | 0.3403 | 0.5078 |
| region_eval_p150_deepfake_035 | deepfake | `[0, 0, 299, 299]` | 0.9638 | 0.9816 | 0.9011 | 0.9480 |
| region_eval_p150_deepfake_036 | deepfake | `[0, 0, 299, 299]` | 0.9793 | 0.9895 | 0.9641 | 0.9817 |
| region_eval_p150_deepfake_037 | deepfake | `[0, 0, 299, 299]` | 0.8648 | 0.9275 | 0.3755 | 0.5460 |
| region_eval_p150_deepfake_038 | deepfake | `[0, 0, 299, 299]` | 0.9927 | 0.9964 | 0.9043 | 0.9497 |
| region_eval_p150_deepfake_039 | deepfake | `[0, 0, 299, 299]` | 0.9518 | 0.9753 | 0.2969 | 0.4579 |
| region_eval_p150_deepfake_040 | deepfake | `[0, 0, 299, 299]` | 0.9921 | 0.9961 | 0.3284 | 0.4944 |
| region_eval_p150_deepfake_041 | deepfake | `[0, 0, 299, 299]` | 0.9967 | 0.9983 | 0.2995 | 0.4609 |
| region_eval_p150_deepfake_042 | deepfake | `[0, 0, 299, 299]` | 0.9827 | 0.9913 | 0.0947 | 0.1730 |
| region_eval_p150_deepfake_043 | deepfake | `[0, 0, 299, 299]` | 0.9819 | 0.9909 | 0.5338 | 0.6960 |
| region_eval_p150_deepfake_044 | deepfake | `[0, 0, 299, 299]` | 0.9476 | 0.9731 | 0.8816 | 0.9371 |
| region_eval_p150_deepfake_045 | deepfake | `[0, 0, 299, 299]` | 0.9673 | 0.9834 | 0.3371 | 0.5042 |
| region_eval_p150_deepfake_046 | deepfake | `[0, 0, 299, 299]` | 0.9910 | 0.9955 | 0.8875 | 0.9404 |
| region_eval_p150_deepfake_047 | deepfake | `[0, 0, 299, 299]` | 0.9828 | 0.9913 | 0.3376 | 0.5047 |
| region_eval_p150_deepfake_048 | deepfake | `[0, 0, 299, 299]` | 0.9842 | 0.9920 | 0.4003 | 0.5717 |
| region_eval_p150_deepfake_049 | deepfake | `[0, 0, 299, 299]` | 0.9578 | 0.9784 | 0.8317 | 0.9081 |
| region_eval_p150_deepfake_050 | deepfake | `[0, 0, 299, 299]` | 0.9784 | 0.9891 | 0.2659 | 0.4201 |
| region_eval_p150_photoshop_001 | photoshop | `[0, 0, 124, 138]` | 0.4539 | 0.6244 | 0.8338 | 0.9094 |
| region_eval_p150_photoshop_002 | photoshop | `[0, 0, 640, 259]` | 0.8527 | 0.9205 | 0.9678 | 0.9836 |
| region_eval_p150_photoshop_003 | photoshop | `[184, 34, 201, 256]` | 0.5148 | 0.6797 | 0.8834 | 0.9381 |
| region_eval_p150_photoshop_004 | photoshop | `[22, 68, 35, 97]` | 0.7931 | 0.8846 | 0.7746 | 0.8730 |
| region_eval_p150_photoshop_005 | photoshop | `[25, 28, 98, 271]` | 0.4044 | 0.5759 | 0.9203 | 0.9585 |
| region_eval_p150_photoshop_006 | photoshop | `[13, 132, 256, 244]` | 0.1134 | 0.2037 | 0.4894 | 0.6571 |
| region_eval_p150_photoshop_007 | photoshop | `[246, 250, 350, 344]` | 0.4227 | 0.5942 | 0.8241 | 0.9035 |
| region_eval_p150_photoshop_008 | photoshop | `[140, 239, 247, 359]` | 0.7013 | 0.8244 | 0.9274 | 0.9623 |
| region_eval_p150_photoshop_009 | photoshop | `[1, 203, 111, 289]` | 0.7329 | 0.8458 | 0.9286 | 0.9630 |
| region_eval_p150_photoshop_010 | photoshop | `[157, 208, 209, 289]` | 0.6168 | 0.7630 | 0.8783 | 0.9352 |
| region_eval_p150_photoshop_011 | photoshop | `[289, 129, 326, 167]` | 0.7895 | 0.8824 | 0.7324 | 0.8456 |
| region_eval_p150_photoshop_012 | photoshop | `[279, 104, 332, 183]` | 0.6093 | 0.7572 | 0.8543 | 0.9214 |
| region_eval_p150_photoshop_013 | photoshop | `[399, 377, 566, 480]` | 0.5169 | 0.6815 | 0.8898 | 0.9417 |
| region_eval_p150_photoshop_014 | photoshop | `[0, 206, 22, 236]` | 0.7879 | 0.8814 | 0.8850 | 0.9390 |
| region_eval_p150_photoshop_015 | photoshop | `[0, 0, 550, 178]` | 0.6346 | 0.7765 | 0.9661 | 0.9828 |
| region_eval_p150_photoshop_016 | photoshop | `[165, 0, 256, 384]` | 0.9416 | 0.9699 | 0.2586 | 0.4109 |
| region_eval_p150_photoshop_017 | photoshop | `[153, 358, 346, 420]` | 0.8477 | 0.9176 | 0.9529 | 0.9759 |
| region_eval_p150_photoshop_018 | photoshop | `[231, 251, 447, 480]` | 0.2709 | 0.4263 | 0.9402 | 0.9692 |
| region_eval_p150_photoshop_019 | photoshop | `[210, 0, 299, 40]` | 0.6685 | 0.8013 | 0.9429 | 0.9706 |
| region_eval_p150_photoshop_020 | photoshop | `[233, 15, 250, 57]` | 0.4678 | 0.6374 | 0.9196 | 0.9581 |
| region_eval_p150_photoshop_021 | photoshop | `[0, 0, 384, 153]` | 0.9948 | 0.9974 | 0.9486 | 0.9736 |
| region_eval_p150_photoshop_022 | photoshop | `[235, 0, 500, 375]` | 0.9981 | 0.9990 | 0.3582 | 0.5275 |
| region_eval_p150_photoshop_023 | photoshop | `[0, 219, 256, 384]` | 0.8206 | 0.9014 | 0.9719 | 0.9857 |
| region_eval_p150_photoshop_024 | photoshop | `[0, 171, 112, 218]` | 0.5484 | 0.7084 | 0.9101 | 0.9529 |
| region_eval_p150_photoshop_025 | photoshop | `[147, 266, 193, 351]` | 0.9473 | 0.9729 | 0.7238 | 0.8398 |
| region_eval_p150_photoshop_026 | photoshop | `[150, 86, 216, 223]` | 0.2231 | 0.3648 | 0.7591 | 0.8631 |
| region_eval_p150_photoshop_027 | photoshop | `[102, 20, 141, 82]` | 0.5414 | 0.7024 | 0.5723 | 0.7279 |
| region_eval_p150_photoshop_028 | photoshop | `[155, 152, 264, 249]` | 0.5937 | 0.7450 | 0.7350 | 0.8473 |
| region_eval_p150_photoshop_029 | photoshop | `[282, 200, 370, 285]` | 0.7881 | 0.8815 | 0.9211 | 0.9589 |
| region_eval_p150_photoshop_030 | photoshop | `[187, 151, 287, 249]` | 0.7855 | 0.8799 | 0.8728 | 0.9321 |
| region_eval_p150_photoshop_031 | photoshop | `[0, 430, 26, 498]` | 0.7675 | 0.8685 | 0.9558 | 0.9774 |
| region_eval_p150_photoshop_032 | photoshop | `[44, 141, 139, 164]` | 0.6426 | 0.7824 | 0.7591 | 0.8631 |
| region_eval_p150_photoshop_033 | photoshop | `[14, 0, 106, 238]` | 0.5849 | 0.7381 | 0.6293 | 0.7725 |
| region_eval_p150_photoshop_034 | photoshop | `[133, 40, 384, 173]` | 0.2392 | 0.3860 | 0.6554 | 0.7918 |
| region_eval_p150_photoshop_035 | photoshop | `[37, 211, 128, 256]` | 0.6701 | 0.8025 | 0.7878 | 0.8813 |
| region_eval_p150_photoshop_036 | photoshop | `[249, 102, 384, 248]` | 0.4582 | 0.6285 | 0.8990 | 0.9468 |
| region_eval_p150_photoshop_037 | photoshop | `[162, 110, 208, 147]` | 0.8578 | 0.9235 | 0.8479 | 0.9177 |
| region_eval_p150_photoshop_038 | photoshop | `[1, 25, 41, 179]` | 0.1981 | 0.3306 | 0.1813 | 0.3070 |
| region_eval_p150_photoshop_039 | photoshop | `[115, 68, 185, 147]` | 0.6816 | 0.8106 | 0.8076 | 0.8936 |
| region_eval_p150_photoshop_040 | photoshop | `[0, 206, 131, 384]` | 0.6443 | 0.7837 | 0.9583 | 0.9787 |
| region_eval_p150_photoshop_041 | photoshop | `[46, 212, 81, 283]` | 0.6946 | 0.8198 | 0.9285 | 0.9629 |
| region_eval_p150_photoshop_042 | photoshop | `[106, 109, 137, 124]` | 0.2796 | 0.4370 | 0.7927 | 0.8844 |
| region_eval_p150_photoshop_043 | photoshop | `[504, 220, 550, 317]` | 0.7916 | 0.8837 | 0.9372 | 0.9676 |
| region_eval_p150_photoshop_044 | photoshop | `[494, 253, 606, 319]` | 0.7777 | 0.8750 | 0.6947 | 0.8198 |
| region_eval_p150_photoshop_045 | photoshop | `[300, 37, 348, 92]` | 0.9068 | 0.9511 | 0.9466 | 0.9726 |
| region_eval_p150_photoshop_046 | photoshop | `[262, 0, 565, 233]` | 0.1411 | 0.2473 | 0.4600 | 0.6302 |
| region_eval_p150_photoshop_047 | photoshop | `[133, 52, 319, 226]` | 0.8240 | 0.9035 | 0.9620 | 0.9806 |
| region_eval_p150_photoshop_048 | photoshop | `[205, 0, 384, 256]` | 0.9943 | 0.9971 | 0.1937 | 0.3246 |
| region_eval_p150_photoshop_049 | photoshop | `[201, 0, 384, 256]` | 0.9934 | 0.9967 | 0.5350 | 0.6971 |
| region_eval_p150_photoshop_050 | photoshop | `[241, 454, 308, 487]` | 0.6499 | 0.7878 | 0.4152 | 0.5867 |
