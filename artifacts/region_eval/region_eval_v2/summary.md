# region_eval_v2 Mask Refinement / Grounding Evaluation

Boundary: **bbox-prompt conditioned mask refinement / grounding evaluation; not automatic forged-region discovery**.

Each bbox prompt is computed from the GT mask. These numbers therefore evaluate mask refinement under a provided bbox prompt, not automatic forged-region discovery.

## Overall

| method | status | n | IoU | Dice | pixel Precision | pixel Recall | pixel F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| bbox_mask_baseline | run | 150 | 0.7170 | 0.8075 | 0.7170 | 1.0000 | 0.8075 |
| sam_refinement | run | 150 | 0.6706 | 0.7715 | 0.9116 | 0.7210 | 0.7715 |
| domain_aware_refinement | run | 150 | 0.7994 | 0.8670 | 0.9119 | 0.8584 | 0.8670 |

## Per Domain

| method | domain | n | mean IoU | mean pixel F1 |
|---|---|---:|---:|---:|
| bbox_mask_baseline | aigc_editing | 50 | 0.5735 | 0.6991 |
| bbox_mask_baseline | deepfake | 50 | 0.9532 | 0.9755 |
| bbox_mask_baseline | photoshop | 50 | 0.6242 | 0.7479 |
| sam_refinement | aigc_editing | 50 | 0.6521 | 0.7627 |
| sam_refinement | deepfake | 50 | 0.5669 | 0.6890 |
| sam_refinement | photoshop | 50 | 0.7928 | 0.8628 |
| domain_aware_refinement | aigc_editing | 50 | 0.6521 | 0.7627 |
| domain_aware_refinement | deepfake | 50 | 0.9532 | 0.9755 |
| domain_aware_refinement | photoshop | 50 | 0.7928 | 0.8628 |

## Domain-Aware Strategy

Photoshop and AIGC-editing use SAM bbox-prompt refinement; DeepFake uses bbox / face-region fallback.

## Samples

| id | domain | bbox_xyxy | bbox IoU | bbox F1 | SAM IoU | SAM F1 |
|---|---|---|---:|---:|---:|---:|
| region_eval_v2_aigc_editing_001 | aigc_editing | `[0, 0, 512, 404]` | 0.4661 | 0.6359 | 0.6046 | 0.7535 |
| region_eval_v2_aigc_editing_002 | aigc_editing | `[0, 322, 512, 512]` | 0.6568 | 0.7929 | 0.7934 | 0.8848 |
| region_eval_v2_aigc_editing_003 | aigc_editing | `[265, 179, 457, 373]` | 0.5672 | 0.7238 | 0.5424 | 0.7033 |
| region_eval_v2_aigc_editing_004 | aigc_editing | `[0, 0, 106, 506]` | 0.5680 | 0.7245 | 0.6324 | 0.7748 |
| region_eval_v2_aigc_editing_005 | aigc_editing | `[47, 0, 451, 273]` | 0.1238 | 0.2203 | 0.5375 | 0.6991 |
| region_eval_v2_aigc_editing_006 | aigc_editing | `[0, 258, 511, 512]` | 0.6351 | 0.7768 | 0.7256 | 0.8410 |
| region_eval_v2_aigc_editing_007 | aigc_editing | `[0, 0, 512, 134]` | 0.6157 | 0.7621 | 0.9441 | 0.9713 |
| region_eval_v2_aigc_editing_008 | aigc_editing | `[0, 297, 181, 512]` | 0.9348 | 0.9663 | 0.9343 | 0.9661 |
| region_eval_v2_aigc_editing_009 | aigc_editing | `[38, 321, 326, 512]` | 0.4940 | 0.6613 | 0.9226 | 0.9598 |
| region_eval_v2_aigc_editing_010 | aigc_editing | `[261, 195, 512, 512]` | 0.3405 | 0.5080 | 0.5747 | 0.7299 |
| region_eval_v2_aigc_editing_011 | aigc_editing | `[273, 0, 512, 321]` | 0.7864 | 0.8804 | 0.9358 | 0.9668 |
| region_eval_v2_aigc_editing_012 | aigc_editing | `[0, 0, 421, 14]` | 0.5612 | 0.7190 | 0.8744 | 0.9330 |
| region_eval_v2_aigc_editing_013 | aigc_editing | `[0, 50, 417, 284]` | 0.2855 | 0.4442 | 0.8589 | 0.9241 |
| region_eval_v2_aigc_editing_014 | aigc_editing | `[211, 0, 512, 80]` | 0.7475 | 0.8555 | 0.8365 | 0.9110 |
| region_eval_v2_aigc_editing_015 | aigc_editing | `[0, 247, 410, 512]` | 0.3815 | 0.5523 | 0.5665 | 0.7233 |
| region_eval_v2_aigc_editing_016 | aigc_editing | `[52, 74, 284, 259]` | 0.7298 | 0.8438 | 0.5355 | 0.6975 |
| region_eval_v2_aigc_editing_017 | aigc_editing | `[70, 28, 281, 509]` | 0.4031 | 0.5745 | 0.7024 | 0.8252 |
| region_eval_v2_aigc_editing_018 | aigc_editing | `[0, 199, 512, 512]` | 0.4561 | 0.6265 | 0.7138 | 0.8330 |
| region_eval_v2_aigc_editing_019 | aigc_editing | `[154, 0, 512, 127]` | 0.8235 | 0.9032 | 0.8754 | 0.9336 |
| region_eval_v2_aigc_editing_020 | aigc_editing | `[76, 49, 303, 512]` | 0.2849 | 0.4434 | 0.4595 | 0.6297 |
| region_eval_v2_aigc_editing_021 | aigc_editing | `[0, 293, 512, 512]` | 0.8232 | 0.9030 | 0.5278 | 0.6909 |
| region_eval_v2_aigc_editing_022 | aigc_editing | `[8, 392, 512, 512]` | 0.4753 | 0.6444 | 0.6859 | 0.8137 |
| region_eval_v2_aigc_editing_023 | aigc_editing | `[213, 355, 512, 502]` | 0.9228 | 0.9598 | 0.9819 | 0.9909 |
| region_eval_v2_aigc_editing_024 | aigc_editing | `[0, 314, 512, 512]` | 0.7549 | 0.8603 | 0.9263 | 0.9618 |
| region_eval_v2_aigc_editing_025 | aigc_editing | `[362, 0, 512, 58]` | 0.8322 | 0.9084 | 0.2496 | 0.3995 |
| region_eval_v2_aigc_editing_026 | aigc_editing | `[153, 150, 512, 512]` | 0.4950 | 0.6622 | 0.8257 | 0.9045 |
| region_eval_v2_aigc_editing_027 | aigc_editing | `[108, 49, 500, 391]` | 0.4083 | 0.5799 | 0.6556 | 0.7920 |
| region_eval_v2_aigc_editing_028 | aigc_editing | `[256, 0, 512, 113]` | 0.6045 | 0.7535 | 0.5096 | 0.6752 |
| region_eval_v2_aigc_editing_029 | aigc_editing | `[334, 205, 512, 386]` | 0.8167 | 0.8991 | 0.7649 | 0.8668 |
| region_eval_v2_aigc_editing_030 | aigc_editing | `[0, 332, 512, 512]` | 0.4462 | 0.6171 | 0.8440 | 0.9154 |
| region_eval_v2_aigc_editing_031 | aigc_editing | `[0, 0, 109, 158]` | 0.9375 | 0.9678 | 0.1643 | 0.2822 |
| region_eval_v2_aigc_editing_032 | aigc_editing | `[0, 0, 231, 436]` | 0.5043 | 0.6705 | 0.4591 | 0.6293 |
| region_eval_v2_aigc_editing_033 | aigc_editing | `[0, 325, 512, 475]` | 0.4230 | 0.5946 | 0.0347 | 0.0670 |
| region_eval_v2_aigc_editing_034 | aigc_editing | `[0, 394, 82, 512]` | 0.1859 | 0.3136 | 0.3250 | 0.4906 |
| region_eval_v2_aigc_editing_035 | aigc_editing | `[0, 30, 94, 512]` | 0.8425 | 0.9145 | 0.4820 | 0.6505 |
| region_eval_v2_aigc_editing_036 | aigc_editing | `[366, 367, 462, 419]` | 0.1729 | 0.2948 | 0.5401 | 0.7014 |
| region_eval_v2_aigc_editing_037 | aigc_editing | `[63, 15, 402, 502]` | 0.3478 | 0.5161 | 0.5084 | 0.6741 |
| region_eval_v2_aigc_editing_038 | aigc_editing | `[36, 228, 512, 447]` | 0.7745 | 0.8729 | 0.8025 | 0.8904 |
| region_eval_v2_aigc_editing_039 | aigc_editing | `[112, 378, 512, 498]` | 0.6479 | 0.7863 | 0.9333 | 0.9655 |
| region_eval_v2_aigc_editing_040 | aigc_editing | `[0, 24, 342, 402]` | 0.4865 | 0.6546 | 0.6676 | 0.8006 |
| region_eval_v2_aigc_editing_041 | aigc_editing | `[190, 255, 317, 512]` | 0.9730 | 0.9863 | 0.9877 | 0.9938 |
| region_eval_v2_aigc_editing_042 | aigc_editing | `[0, 0, 92, 363]` | 0.9077 | 0.9516 | 0.9853 | 0.9926 |
| region_eval_v2_aigc_editing_043 | aigc_editing | `[0, 302, 204, 512]` | 0.5913 | 0.7431 | 0.1995 | 0.3327 |
| region_eval_v2_aigc_editing_044 | aigc_editing | `[0, 412, 512, 512]` | 0.9008 | 0.9478 | 0.7174 | 0.8354 |
| region_eval_v2_aigc_editing_045 | aigc_editing | `[208, 273, 512, 512]` | 0.3403 | 0.5078 | 0.6485 | 0.7868 |
| region_eval_v2_aigc_editing_046 | aigc_editing | `[0, 0, 512, 512]` | 0.1965 | 0.3285 | 0.2915 | 0.4514 |
| region_eval_v2_aigc_editing_047 | aigc_editing | `[146, 0, 282, 387]` | 0.6927 | 0.8184 | 0.6975 | 0.8218 |
| region_eval_v2_aigc_editing_048 | aigc_editing | `[0, 371, 512, 512]` | 0.8202 | 0.9012 | 0.4579 | 0.6282 |
| region_eval_v2_aigc_editing_049 | aigc_editing | `[0, 191, 512, 512]` | 0.2684 | 0.4232 | 0.5840 | 0.7374 |
| region_eval_v2_aigc_editing_050 | aigc_editing | `[96, 91, 512, 427]` | 0.2197 | 0.3602 | 0.5761 | 0.7311 |
| region_eval_v2_deepfake_001 | deepfake | `[0, 0, 299, 299]` | 0.9057 | 0.9505 | 0.4591 | 0.6293 |
| region_eval_v2_deepfake_002 | deepfake | `[0, 0, 299, 299]` | 0.9822 | 0.9910 | 0.3483 | 0.5167 |
| region_eval_v2_deepfake_003 | deepfake | `[0, 0, 299, 299]` | 0.9979 | 0.9989 | 0.3015 | 0.4633 |
| region_eval_v2_deepfake_004 | deepfake | `[0, 0, 299, 299]` | 0.8704 | 0.9307 | 0.7896 | 0.8825 |
| region_eval_v2_deepfake_005 | deepfake | `[0, 0, 299, 299]` | 0.8631 | 0.9265 | 0.2733 | 0.4293 |
| region_eval_v2_deepfake_006 | deepfake | `[0, 0, 299, 299]` | 0.8824 | 0.9375 | 0.7476 | 0.8556 |
| region_eval_v2_deepfake_007 | deepfake | `[0, 0, 299, 299]` | 0.9984 | 0.9992 | 0.2774 | 0.4343 |
| region_eval_v2_deepfake_008 | deepfake | `[0, 0, 299, 299]` | 0.9458 | 0.9721 | 0.3697 | 0.5399 |
| region_eval_v2_deepfake_009 | deepfake | `[0, 0, 299, 299]` | 0.9970 | 0.9985 | 0.8710 | 0.9310 |
| region_eval_v2_deepfake_010 | deepfake | `[0, 0, 299, 299]` | 0.9141 | 0.9551 | 0.3898 | 0.5609 |
| region_eval_v2_deepfake_011 | deepfake | `[0, 0, 299, 299]` | 0.9905 | 0.9952 | 0.3329 | 0.4995 |
| region_eval_v2_deepfake_012 | deepfake | `[0, 0, 299, 299]` | 0.9611 | 0.9802 | 0.8212 | 0.9019 |
| region_eval_v2_deepfake_013 | deepfake | `[0, 0, 299, 299]` | 0.9583 | 0.9787 | 0.3509 | 0.5195 |
| region_eval_v2_deepfake_014 | deepfake | `[0, 0, 299, 299]` | 0.8670 | 0.9288 | 0.6806 | 0.8100 |
| region_eval_v2_deepfake_015 | deepfake | `[0, 0, 299, 299]` | 0.9958 | 0.9979 | 0.9742 | 0.9869 |
| region_eval_v2_deepfake_016 | deepfake | `[0, 0, 299, 299]` | 0.9993 | 0.9997 | 0.8274 | 0.9055 |
| region_eval_v2_deepfake_017 | deepfake | `[0, 0, 299, 299]` | 0.8721 | 0.9317 | 0.7856 | 0.8800 |
| region_eval_v2_deepfake_018 | deepfake | `[0, 0, 299, 299]` | 0.9297 | 0.9636 | 0.3864 | 0.5574 |
| region_eval_v2_deepfake_019 | deepfake | `[0, 0, 299, 299]` | 0.9139 | 0.9550 | 0.7182 | 0.8360 |
| region_eval_v2_deepfake_020 | deepfake | `[0, 0, 299, 299]` | 0.9878 | 0.9939 | 0.9377 | 0.9678 |
| region_eval_v2_deepfake_021 | deepfake | `[0, 0, 299, 299]` | 0.8267 | 0.9052 | 0.7894 | 0.8823 |
| region_eval_v2_deepfake_022 | deepfake | `[0, 0, 299, 299]` | 1.0000 | 1.0000 | 0.7312 | 0.8447 |
| region_eval_v2_deepfake_023 | deepfake | `[0, 0, 299, 299]` | 0.9679 | 0.9837 | 0.3889 | 0.5600 |
| region_eval_v2_deepfake_024 | deepfake | `[0, 0, 299, 299]` | 0.9054 | 0.9503 | 0.6829 | 0.8116 |
| region_eval_v2_deepfake_025 | deepfake | `[0, 0, 299, 299]` | 0.9048 | 0.9500 | 0.5201 | 0.6843 |
| region_eval_v2_deepfake_026 | deepfake | `[0, 0, 299, 299]` | 0.9893 | 0.9946 | 0.2971 | 0.4581 |
| region_eval_v2_deepfake_027 | deepfake | `[0, 0, 299, 299]` | 0.9877 | 0.9938 | 0.8948 | 0.9445 |
| region_eval_v2_deepfake_028 | deepfake | `[0, 0, 299, 299]` | 0.9575 | 0.9783 | 0.9204 | 0.9586 |
| region_eval_v2_deepfake_029 | deepfake | `[0, 0, 299, 299]` | 0.9420 | 0.9702 | 0.8473 | 0.9173 |
| region_eval_v2_deepfake_030 | deepfake | `[0, 0, 299, 299]` | 0.9732 | 0.9864 | 0.3381 | 0.5054 |
| region_eval_v2_deepfake_031 | deepfake | `[0, 0, 299, 299]` | 0.9769 | 0.9883 | 0.3766 | 0.5471 |
| region_eval_v2_deepfake_032 | deepfake | `[0, 0, 299, 299]` | 0.9840 | 0.9919 | 0.2727 | 0.4286 |
| region_eval_v2_deepfake_033 | deepfake | `[0, 0, 299, 299]` | 0.9012 | 0.9481 | 0.6629 | 0.7973 |
| region_eval_v2_deepfake_034 | deepfake | `[0, 0, 299, 299]` | 0.9952 | 0.9976 | 0.3403 | 0.5078 |
| region_eval_v2_deepfake_035 | deepfake | `[0, 0, 299, 299]` | 0.9638 | 0.9816 | 0.9011 | 0.9480 |
| region_eval_v2_deepfake_036 | deepfake | `[0, 0, 299, 299]` | 0.9793 | 0.9895 | 0.9641 | 0.9817 |
| region_eval_v2_deepfake_037 | deepfake | `[0, 0, 299, 299]` | 0.8648 | 0.9275 | 0.3755 | 0.5460 |
| region_eval_v2_deepfake_038 | deepfake | `[0, 0, 299, 299]` | 0.9927 | 0.9964 | 0.9043 | 0.9498 |
| region_eval_v2_deepfake_039 | deepfake | `[0, 0, 299, 299]` | 0.9518 | 0.9753 | 0.2969 | 0.4579 |
| region_eval_v2_deepfake_040 | deepfake | `[0, 0, 299, 299]` | 0.9921 | 0.9961 | 0.3284 | 0.4944 |
| region_eval_v2_deepfake_041 | deepfake | `[0, 0, 299, 299]` | 0.9967 | 0.9983 | 0.2995 | 0.4609 |
| region_eval_v2_deepfake_042 | deepfake | `[0, 0, 299, 299]` | 0.9827 | 0.9913 | 0.0946 | 0.1728 |
| region_eval_v2_deepfake_043 | deepfake | `[0, 0, 299, 299]` | 0.9819 | 0.9909 | 0.5337 | 0.6960 |
| region_eval_v2_deepfake_044 | deepfake | `[0, 0, 299, 299]` | 0.9476 | 0.9731 | 0.8816 | 0.9371 |
| region_eval_v2_deepfake_045 | deepfake | `[0, 0, 299, 299]` | 0.9673 | 0.9834 | 0.3371 | 0.5042 |
| region_eval_v2_deepfake_046 | deepfake | `[0, 0, 299, 299]` | 0.9910 | 0.9955 | 0.8875 | 0.9404 |
| region_eval_v2_deepfake_047 | deepfake | `[0, 0, 299, 299]` | 0.9828 | 0.9913 | 0.3375 | 0.5047 |
| region_eval_v2_deepfake_048 | deepfake | `[0, 0, 299, 299]` | 0.9842 | 0.9920 | 0.3999 | 0.5714 |
| region_eval_v2_deepfake_049 | deepfake | `[0, 0, 299, 299]` | 0.9578 | 0.9784 | 0.8317 | 0.9081 |
| region_eval_v2_deepfake_050 | deepfake | `[0, 0, 299, 299]` | 0.9784 | 0.9891 | 0.2659 | 0.4201 |
| region_eval_v2_photoshop_001 | photoshop | `[0, 97, 234, 160]` | 0.8677 | 0.9292 | 0.9483 | 0.9735 |
| region_eval_v2_photoshop_002 | photoshop | `[112, 319, 181, 374]` | 0.5657 | 0.7227 | 0.8872 | 0.9402 |
| region_eval_v2_photoshop_003 | photoshop | `[10, 162, 121, 307]` | 0.5806 | 0.7346 | 0.9264 | 0.9618 |
| region_eval_v2_photoshop_004 | photoshop | `[431, 345, 482, 399]` | 0.6336 | 0.7757 | 0.8454 | 0.9162 |
| region_eval_v2_photoshop_005 | photoshop | `[5, 3, 64, 256]` | 0.8461 | 0.9166 | 0.5731 | 0.7286 |
| region_eval_v2_photoshop_006 | photoshop | `[263, 20, 384, 142]` | 0.4585 | 0.6287 | 0.9474 | 0.9730 |
| region_eval_v2_photoshop_007 | photoshop | `[278, 138, 323, 186]` | 0.4171 | 0.5887 | 0.3732 | 0.5435 |
| region_eval_v2_photoshop_008 | photoshop | `[43, 293, 72, 384]` | 0.9360 | 0.9669 | 0.9293 | 0.9634 |
| region_eval_v2_photoshop_009 | photoshop | `[0, 0, 184, 256]` | 0.9973 | 0.9987 | 0.2620 | 0.4152 |
| region_eval_v2_photoshop_010 | photoshop | `[1, 8, 197, 256]` | 0.6807 | 0.8100 | 0.0419 | 0.0804 |
| region_eval_v2_photoshop_011 | photoshop | `[95, 94, 145, 173]` | 0.8010 | 0.8895 | 0.8831 | 0.9379 |
| region_eval_v2_photoshop_012 | photoshop | `[191, 25, 248, 216]` | 0.5244 | 0.6880 | 0.8128 | 0.8967 |
| region_eval_v2_photoshop_013 | photoshop | `[403, 145, 579, 337]` | 0.7074 | 0.8286 | 0.9579 | 0.9785 |
| region_eval_v2_photoshop_014 | photoshop | `[438, 87, 635, 411]` | 0.4749 | 0.6440 | 0.8906 | 0.9422 |
| region_eval_v2_photoshop_015 | photoshop | `[0, 0, 194, 59]` | 0.4540 | 0.6244 | 0.9219 | 0.9593 |
| region_eval_v2_photoshop_016 | photoshop | `[189, 162, 356, 254]` | 0.5137 | 0.6788 | 0.9241 | 0.9606 |
| region_eval_v2_photoshop_017 | photoshop | `[220, 0, 296, 147]` | 0.7887 | 0.8818 | 0.8238 | 0.9034 |
| region_eval_v2_photoshop_018 | photoshop | `[279, 109, 335, 157]` | 0.7868 | 0.8807 | 0.5267 | 0.6900 |
| region_eval_v2_photoshop_019 | photoshop | `[117, 92, 272, 256]` | 0.0977 | 0.1780 | 0.4115 | 0.5830 |
| region_eval_v2_photoshop_020 | photoshop | `[78, 144, 123, 172]` | 0.6984 | 0.8224 | 0.7574 | 0.8619 |
| region_eval_v2_photoshop_021 | photoshop | `[249, 27, 356, 256]` | 0.7104 | 0.8307 | 0.9356 | 0.9667 |
| region_eval_v2_photoshop_022 | photoshop | `[217, 140, 339, 256]` | 0.7069 | 0.8283 | 0.3367 | 0.5038 |
| region_eval_v2_photoshop_023 | photoshop | `[253, 93, 298, 222]` | 0.6331 | 0.7753 | 0.9338 | 0.9658 |
| region_eval_v2_photoshop_024 | photoshop | `[208, 80, 384, 156]` | 0.5625 | 0.7200 | 0.8210 | 0.9017 |
| region_eval_v2_photoshop_025 | photoshop | `[101, 171, 164, 221]` | 0.9854 | 0.9926 | 0.9742 | 0.9869 |
| region_eval_v2_photoshop_026 | photoshop | `[22, 68, 35, 97]` | 0.7931 | 0.8846 | 0.7746 | 0.8730 |
| region_eval_v2_photoshop_027 | photoshop | `[296, 27, 353, 47]` | 0.7640 | 0.8662 | 0.7838 | 0.8788 |
| region_eval_v2_photoshop_028 | photoshop | `[412, 356, 457, 431]` | 0.7831 | 0.8784 | 0.9484 | 0.9735 |
| region_eval_v2_photoshop_029 | photoshop | `[56, 180, 90, 303]` | 0.2525 | 0.4032 | 0.9307 | 0.9641 |
| region_eval_v2_photoshop_030 | photoshop | `[40, 27, 96, 52]` | 0.3793 | 0.5500 | 0.8380 | 0.9119 |
| region_eval_v2_photoshop_031 | photoshop | `[3, 116, 43, 230]` | 0.8053 | 0.8921 | 0.2867 | 0.4456 |
| region_eval_v2_photoshop_032 | photoshop | `[251, 37, 361, 125]` | 0.2907 | 0.4505 | 0.6272 | 0.7709 |
| region_eval_v2_photoshop_033 | photoshop | `[183, 115, 216, 139]` | 0.7626 | 0.8653 | 0.7440 | 0.8532 |
| region_eval_v2_photoshop_034 | photoshop | `[701, 196, 771, 262]` | 0.6335 | 0.7757 | 0.9109 | 0.9534 |
| region_eval_v2_photoshop_035 | photoshop | `[23, 307, 107, 369]` | 0.5578 | 0.7161 | 0.9111 | 0.9535 |
| region_eval_v2_photoshop_036 | photoshop | `[0, 145, 384, 256]` | 0.6690 | 0.8017 | 0.8473 | 0.9173 |
| region_eval_v2_photoshop_037 | photoshop | `[19, 0, 384, 137]` | 0.5340 | 0.6962 | 0.9363 | 0.9671 |
| region_eval_v2_photoshop_038 | photoshop | `[17, 0, 384, 42]` | 0.4866 | 0.6547 | 0.9463 | 0.9724 |
| region_eval_v2_photoshop_039 | photoshop | `[204, 126, 326, 308]` | 0.1822 | 0.3083 | 0.9212 | 0.9590 |
| region_eval_v2_photoshop_040 | photoshop | `[190, 112, 287, 228]` | 0.5589 | 0.7171 | 0.8988 | 0.9467 |
| region_eval_v2_photoshop_041 | photoshop | `[18, 0, 384, 40]` | 0.4878 | 0.6558 | 0.9708 | 0.9852 |
| region_eval_v2_photoshop_042 | photoshop | `[291, 315, 369, 400]` | 0.7154 | 0.8341 | 0.7755 | 0.8735 |
| region_eval_v2_photoshop_043 | photoshop | `[93, 106, 132, 140]` | 0.6207 | 0.7659 | 0.8551 | 0.9219 |
| region_eval_v2_photoshop_044 | photoshop | `[353, 6, 384, 117]` | 0.6277 | 0.7713 | 0.6365 | 0.7779 |
| region_eval_v2_photoshop_045 | photoshop | `[243, 91, 288, 128]` | 0.5766 | 0.7314 | 0.8930 | 0.9435 |
| region_eval_v2_photoshop_046 | photoshop | `[81, 148, 120, 175]` | 0.6382 | 0.7791 | 0.8403 | 0.9132 |
| region_eval_v2_photoshop_047 | photoshop | `[0, 395, 130, 418]` | 0.8244 | 0.9038 | 0.9152 | 0.9557 |
| region_eval_v2_photoshop_048 | photoshop | `[90, 38, 283, 256]` | 0.2573 | 0.4093 | 0.9287 | 0.9630 |
| region_eval_v2_photoshop_049 | photoshop | `[0, 288, 640, 480]` | 0.9490 | 0.9738 | 0.9791 | 0.9894 |
| region_eval_v2_photoshop_050 | photoshop | `[0, 307, 137, 368]` | 0.6337 | 0.7758 | 0.8946 | 0.9444 |
