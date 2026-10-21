# region_eval_p150_v2_final Mask Refinement / Grounding Evaluation

Boundary: **bbox-prompt conditioned mask refinement / grounding evaluation; not automatic forged-region discovery**.

Each bbox prompt is computed from the GT mask. These numbers therefore evaluate mask refinement under a provided bbox prompt, not automatic forged-region discovery.

## Overall

| method | status | n | IoU | Dice | pixel Precision | pixel Recall | pixel F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| bbox_mask_baseline | run | 150 | 0.7264 | 0.8172 | 0.7264 | 1.0000 | 0.8172 |
| sam_refinement | run | 150 | 0.7831 | 0.8611 | 0.9153 | 0.8426 | 0.8611 |
| domain_aware_oracle | run | 150 | 0.8464 | 0.9050 | 0.9140 | 0.9145 | 0.9050 |
| domain_aware_predicted | run | 150 | 0.8103 | 0.8798 | 0.8550 | 0.9381 | 0.8798 |

## Per Domain

| method | domain | n | mean IoU | mean pixel F1 |
|---|---|---:|---:|---:|
| bbox_mask_baseline | aigc_editing | 50 | 0.5922 | 0.7230 |
| bbox_mask_baseline | deepfake | 50 | 0.9456 | 0.9688 |
| bbox_mask_baseline | photoshop | 50 | 0.6415 | 0.7597 |
| sam_refinement | aigc_editing | 50 | 0.7341 | 0.8283 |
| sam_refinement | deepfake | 50 | 0.7558 | 0.8369 |
| sam_refinement | photoshop | 50 | 0.8594 | 0.9180 |
| domain_aware_oracle | aigc_editing | 50 | 0.7341 | 0.8283 |
| domain_aware_oracle | deepfake | 50 | 0.9456 | 0.9688 |
| domain_aware_oracle | photoshop | 50 | 0.8594 | 0.9180 |
| domain_aware_predicted | aigc_editing | 50 | 0.7341 | 0.8283 |
| domain_aware_predicted | deepfake | 50 | 0.9456 | 0.9688 |
| domain_aware_predicted | photoshop | 50 | 0.7511 | 0.8421 |

## Domain-Aware Strategy

Oracle policy: Photoshop and AIGC-editing use SAM bbox-prompt refinement; DeepFake uses bbox / face-region fallback.

Predicted policy: use the LoRA-predicted tamper domain; Photoshop/AIGC predictions use SAM, DeepFake/none/unknown fallback to bbox.

## Predicted Domain Stats

- predictions found: `150/150`
- valid JSON: `150/150`
- valid schema: `150/150`
- fallback to bbox: `80/150`

## Samples

| id | domain | bbox_xyxy | bbox IoU | bbox F1 | SAM IoU | SAM F1 |
|---|---|---|---:|---:|---:|---:|
| region_eval_p150_v2_final_aigc_editing_001 | aigc_editing | `[373, 214, 512, 364]` | 0.3517 | 0.5203 | 0.4515 | 0.6222 |
| region_eval_p150_v2_final_aigc_editing_002 | aigc_editing | `[0, 275, 154, 368]` | 0.8450 | 0.9160 | 0.8929 | 0.9434 |
| region_eval_p150_v2_final_aigc_editing_003 | aigc_editing | `[0, 0, 512, 197]` | 0.8416 | 0.9140 | 0.9465 | 0.9725 |
| region_eval_p150_v2_final_aigc_editing_004 | aigc_editing | `[205, 163, 289, 358]` | 0.6993 | 0.8230 | 0.8357 | 0.9105 |
| region_eval_p150_v2_final_aigc_editing_005 | aigc_editing | `[222, 246, 512, 512]` | 0.4687 | 0.6383 | 0.6135 | 0.7605 |
| region_eval_p150_v2_final_aigc_editing_006 | aigc_editing | `[0, 388, 512, 512]` | 0.8939 | 0.9440 | 0.9794 | 0.9896 |
| region_eval_p150_v2_final_aigc_editing_007 | aigc_editing | `[0, 422, 512, 512]` | 0.4921 | 0.6596 | 0.8426 | 0.9146 |
| region_eval_p150_v2_final_aigc_editing_008 | aigc_editing | `[0, 0, 499, 225]` | 0.3712 | 0.5415 | 0.5557 | 0.7144 |
| region_eval_p150_v2_final_aigc_editing_009 | aigc_editing | `[125, 0, 338, 259]` | 0.4570 | 0.6274 | 0.4581 | 0.6284 |
| region_eval_p150_v2_final_aigc_editing_010 | aigc_editing | `[72, 0, 349, 242]` | 0.5425 | 0.7034 | 0.8986 | 0.9466 |
| region_eval_p150_v2_final_aigc_editing_011 | aigc_editing | `[105, 158, 226, 307]` | 0.9316 | 0.9646 | 0.9571 | 0.9781 |
| region_eval_p150_v2_final_aigc_editing_012 | aigc_editing | `[245, 149, 486, 387]` | 0.5245 | 0.6881 | 0.6354 | 0.7771 |
| region_eval_p150_v2_final_aigc_editing_013 | aigc_editing | `[123, 204, 442, 419]` | 0.5360 | 0.6979 | 0.8603 | 0.9249 |
| region_eval_p150_v2_final_aigc_editing_014 | aigc_editing | `[0, 333, 512, 482]` | 0.2841 | 0.4425 | 0.5412 | 0.7023 |
| region_eval_p150_v2_final_aigc_editing_015 | aigc_editing | `[0, 425, 512, 500]` | 0.8404 | 0.9133 | 0.7457 | 0.8543 |
| region_eval_p150_v2_final_aigc_editing_016 | aigc_editing | `[0, 0, 512, 171]` | 0.4061 | 0.5777 | 0.4710 | 0.6404 |
| region_eval_p150_v2_final_aigc_editing_017 | aigc_editing | `[162, 351, 406, 512]` | 0.5942 | 0.7455 | 0.7325 | 0.8456 |
| region_eval_p150_v2_final_aigc_editing_018 | aigc_editing | `[129, 5, 336, 512]` | 0.7148 | 0.8337 | 0.9868 | 0.9934 |
| region_eval_p150_v2_final_aigc_editing_019 | aigc_editing | `[77, 23, 393, 407]` | 0.4157 | 0.5873 | 0.7680 | 0.8688 |
| region_eval_p150_v2_final_aigc_editing_020 | aigc_editing | `[0, 0, 512, 349]` | 0.2999 | 0.4614 | 0.9444 | 0.9714 |
| region_eval_p150_v2_final_aigc_editing_021 | aigc_editing | `[0, 293, 499, 367]` | 0.5683 | 0.7247 | 0.9000 | 0.9474 |
| region_eval_p150_v2_final_aigc_editing_022 | aigc_editing | `[0, 73, 238, 158]` | 0.6503 | 0.7881 | 0.7311 | 0.8446 |
| region_eval_p150_v2_final_aigc_editing_023 | aigc_editing | `[250, 183, 512, 512]` | 0.3880 | 0.5591 | 0.5958 | 0.7467 |
| region_eval_p150_v2_final_aigc_editing_024 | aigc_editing | `[0, 42, 153, 398]` | 0.7633 | 0.8657 | 0.8227 | 0.9027 |
| region_eval_p150_v2_final_aigc_editing_025 | aigc_editing | `[207, 0, 512, 118]` | 0.2709 | 0.4263 | 0.4997 | 0.6664 |
| region_eval_p150_v2_final_aigc_editing_026 | aigc_editing | `[71, 142, 288, 417]` | 0.4648 | 0.6346 | 0.8277 | 0.9058 |
| region_eval_p150_v2_final_aigc_editing_027 | aigc_editing | `[16, 0, 243, 458]` | 0.5849 | 0.7381 | 0.6721 | 0.8039 |
| region_eval_p150_v2_final_aigc_editing_028 | aigc_editing | `[300, 4, 471, 176]` | 0.5381 | 0.6997 | 0.5917 | 0.7435 |
| region_eval_p150_v2_final_aigc_editing_029 | aigc_editing | `[256, 325, 512, 512]` | 0.6632 | 0.7975 | 0.5647 | 0.7218 |
| region_eval_p150_v2_final_aigc_editing_030 | aigc_editing | `[20, 256, 276, 492]` | 0.5515 | 0.7110 | 0.6690 | 0.8017 |
| region_eval_p150_v2_final_aigc_editing_031 | aigc_editing | `[0, 9, 212, 211]` | 0.8783 | 0.9352 | 0.8275 | 0.9056 |
| region_eval_p150_v2_final_aigc_editing_032 | aigc_editing | `[339, 0, 512, 192]` | 0.5617 | 0.7194 | 0.8997 | 0.9472 |
| region_eval_p150_v2_final_aigc_editing_033 | aigc_editing | `[132, 358, 512, 471]` | 0.5996 | 0.7497 | 0.7992 | 0.8884 |
| region_eval_p150_v2_final_aigc_editing_034 | aigc_editing | `[53, 320, 236, 512]` | 0.8069 | 0.8931 | 0.7794 | 0.8760 |
| region_eval_p150_v2_final_aigc_editing_035 | aigc_editing | `[0, 435, 512, 512]` | 0.7097 | 0.8302 | 0.6598 | 0.7951 |
| region_eval_p150_v2_final_aigc_editing_036 | aigc_editing | `[0, 0, 512, 230]` | 0.8510 | 0.9195 | 0.9451 | 0.9718 |
| region_eval_p150_v2_final_aigc_editing_037 | aigc_editing | `[0, 328, 512, 501]` | 0.6252 | 0.7694 | 0.6954 | 0.8204 |
| region_eval_p150_v2_final_aigc_editing_038 | aigc_editing | `[0, 294, 78, 428]` | 0.8044 | 0.8916 | 0.7360 | 0.8479 |
| region_eval_p150_v2_final_aigc_editing_039 | aigc_editing | `[115, 0, 512, 293]` | 0.4880 | 0.6559 | 0.8459 | 0.9165 |
| region_eval_p150_v2_final_aigc_editing_040 | aigc_editing | `[125, 74, 223, 171]` | 0.3450 | 0.5131 | 0.6847 | 0.8129 |
| region_eval_p150_v2_final_aigc_editing_041 | aigc_editing | `[112, 0, 512, 76]` | 0.6135 | 0.7604 | 0.8091 | 0.8945 |
| region_eval_p150_v2_final_aigc_editing_042 | aigc_editing | `[142, 0, 453, 169]` | 0.8370 | 0.9113 | 0.5922 | 0.7439 |
| region_eval_p150_v2_final_aigc_editing_043 | aigc_editing | `[0, 301, 512, 512]` | 0.8687 | 0.9297 | 0.8624 | 0.9261 |
| region_eval_p150_v2_final_aigc_editing_044 | aigc_editing | `[54, 147, 384, 456]` | 0.1194 | 0.2133 | 0.0025 | 0.0049 |
| region_eval_p150_v2_final_aigc_editing_045 | aigc_editing | `[213, 114, 469, 276]` | 0.6336 | 0.7757 | 0.8304 | 0.9073 |
| region_eval_p150_v2_final_aigc_editing_046 | aigc_editing | `[226, 283, 434, 512]` | 0.8356 | 0.9105 | 0.8706 | 0.9308 |
| region_eval_p150_v2_final_aigc_editing_047 | aigc_editing | `[0, 0, 512, 455]` | 0.1905 | 0.3201 | 0.2323 | 0.3770 |
| region_eval_p150_v2_final_aigc_editing_048 | aigc_editing | `[0, 388, 127, 512]` | 0.6994 | 0.8231 | 0.8572 | 0.9231 |
| region_eval_p150_v2_final_aigc_editing_049 | aigc_editing | `[0, 163, 187, 512]` | 0.6720 | 0.8038 | 0.9743 | 0.9870 |
| region_eval_p150_v2_final_aigc_editing_050 | aigc_editing | `[130, 0, 512, 341]` | 0.5176 | 0.6822 | 0.8118 | 0.8961 |
| region_eval_p150_v2_final_deepfake_001 | deepfake | `[0, 0, 299, 299]` | 0.9963 | 0.9982 | 0.8820 | 0.9373 |
| region_eval_p150_v2_final_deepfake_002 | deepfake | `[0, 0, 299, 299]` | 0.8179 | 0.8998 | 0.7406 | 0.8510 |
| region_eval_p150_v2_final_deepfake_003 | deepfake | `[0, 0, 299, 299]` | 0.9967 | 0.9983 | 0.9454 | 0.9719 |
| region_eval_p150_v2_final_deepfake_004 | deepfake | `[0, 0, 299, 299]` | 0.9988 | 0.9994 | 0.7952 | 0.8859 |
| region_eval_p150_v2_final_deepfake_005 | deepfake | `[0, 0, 299, 299]` | 0.8773 | 0.9346 | 0.7882 | 0.8815 |
| region_eval_p150_v2_final_deepfake_006 | deepfake | `[0, 0, 299, 299]` | 0.9935 | 0.9968 | 0.2513 | 0.4017 |
| region_eval_p150_v2_final_deepfake_007 | deepfake | `[0, 0, 299, 299]` | 1.0000 | 1.0000 | 0.9510 | 0.9749 |
| region_eval_p150_v2_final_deepfake_008 | deepfake | `[0, 0, 299, 299]` | 0.9610 | 0.9801 | 0.8900 | 0.9418 |
| region_eval_p150_v2_final_deepfake_009 | deepfake | `[0, 0, 299, 299]` | 0.9640 | 0.9817 | 0.8525 | 0.9204 |
| region_eval_p150_v2_final_deepfake_010 | deepfake | `[0, 0, 299, 299]` | 0.9877 | 0.9938 | 0.7712 | 0.8708 |
| region_eval_p150_v2_final_deepfake_011 | deepfake | `[0, 0, 299, 299]` | 0.9672 | 0.9834 | 0.8779 | 0.9350 |
| region_eval_p150_v2_final_deepfake_012 | deepfake | `[0, 0, 299, 299]` | 0.3670 | 0.5369 | 0.3375 | 0.5047 |
| region_eval_p150_v2_final_deepfake_013 | deepfake | `[0, 0, 299, 299]` | 0.9956 | 0.9978 | 0.9258 | 0.9615 |
| region_eval_p150_v2_final_deepfake_014 | deepfake | `[0, 0, 299, 299]` | 0.8901 | 0.9419 | 0.7567 | 0.8615 |
| region_eval_p150_v2_final_deepfake_015 | deepfake | `[0, 0, 299, 299]` | 0.9031 | 0.9491 | 0.7838 | 0.8788 |
| region_eval_p150_v2_final_deepfake_016 | deepfake | `[0, 0, 299, 299]` | 0.9653 | 0.9824 | 0.8763 | 0.9341 |
| region_eval_p150_v2_final_deepfake_017 | deepfake | `[0, 0, 299, 299]` | 0.8965 | 0.9454 | 0.8509 | 0.9195 |
| region_eval_p150_v2_final_deepfake_018 | deepfake | `[0, 0, 299, 299]` | 0.9980 | 0.9990 | 0.9177 | 0.9571 |
| region_eval_p150_v2_final_deepfake_019 | deepfake | `[0, 0, 299, 299]` | 0.9949 | 0.9975 | 0.8734 | 0.9324 |
| region_eval_p150_v2_final_deepfake_020 | deepfake | `[0, 0, 299, 299]` | 0.9951 | 0.9975 | 0.8698 | 0.9304 |
| region_eval_p150_v2_final_deepfake_021 | deepfake | `[0, 0, 299, 299]` | 0.9876 | 0.9938 | 0.9106 | 0.9532 |
| region_eval_p150_v2_final_deepfake_022 | deepfake | `[0, 0, 299, 299]` | 0.9267 | 0.9620 | 0.7598 | 0.8635 |
| region_eval_p150_v2_final_deepfake_023 | deepfake | `[0, 0, 299, 299]` | 0.9379 | 0.9680 | 0.2168 | 0.3564 |
| region_eval_p150_v2_final_deepfake_024 | deepfake | `[0, 0, 299, 299]` | 0.8469 | 0.9171 | 0.7552 | 0.8605 |
| region_eval_p150_v2_final_deepfake_025 | deepfake | `[0, 0, 299, 299]` | 0.9433 | 0.9708 | 0.1710 | 0.2921 |
| region_eval_p150_v2_final_deepfake_026 | deepfake | `[0, 0, 299, 299]` | 0.9743 | 0.9870 | 0.8639 | 0.9270 |
| region_eval_p150_v2_final_deepfake_027 | deepfake | `[0, 0, 299, 299]` | 0.9364 | 0.9672 | 0.8344 | 0.9097 |
| region_eval_p150_v2_final_deepfake_028 | deepfake | `[0, 0, 299, 299]` | 0.9983 | 0.9992 | 0.1693 | 0.2896 |
| region_eval_p150_v2_final_deepfake_029 | deepfake | `[0, 0, 299, 299]` | 0.9443 | 0.9713 | 0.7522 | 0.8586 |
| region_eval_p150_v2_final_deepfake_030 | deepfake | `[0, 0, 299, 299]` | 0.8553 | 0.9220 | 0.7679 | 0.8687 |
| region_eval_p150_v2_final_deepfake_031 | deepfake | `[0, 0, 299, 299]` | 0.9911 | 0.9956 | 0.8340 | 0.9095 |
| region_eval_p150_v2_final_deepfake_032 | deepfake | `[0, 0, 299, 299]` | 0.9963 | 0.9981 | 0.9581 | 0.9786 |
| region_eval_p150_v2_final_deepfake_033 | deepfake | `[0, 0, 299, 299]` | 0.8864 | 0.9398 | 0.2291 | 0.3728 |
| region_eval_p150_v2_final_deepfake_034 | deepfake | `[0, 0, 299, 299]` | 0.9643 | 0.9818 | 0.8960 | 0.9452 |
| region_eval_p150_v2_final_deepfake_035 | deepfake | `[0, 0, 299, 299]` | 0.9840 | 0.9919 | 0.8382 | 0.9120 |
| region_eval_p150_v2_final_deepfake_036 | deepfake | `[0, 0, 299, 299]` | 0.9841 | 0.9920 | 0.8531 | 0.9207 |
| region_eval_p150_v2_final_deepfake_037 | deepfake | `[0, 0, 299, 299]` | 0.9799 | 0.9898 | 0.8832 | 0.9380 |
| region_eval_p150_v2_final_deepfake_038 | deepfake | `[0, 0, 299, 299]` | 0.9327 | 0.9652 | 0.8681 | 0.9294 |
| region_eval_p150_v2_final_deepfake_039 | deepfake | `[0, 0, 299, 299]` | 0.9663 | 0.9828 | 0.3374 | 0.5046 |
| region_eval_p150_v2_final_deepfake_040 | deepfake | `[0, 0, 299, 299]` | 0.9974 | 0.9987 | 0.9164 | 0.9564 |
| region_eval_p150_v2_final_deepfake_041 | deepfake | `[0, 0, 299, 299]` | 0.9591 | 0.9791 | 0.4492 | 0.6199 |
| region_eval_p150_v2_final_deepfake_042 | deepfake | `[0, 0, 299, 299]` | 0.9860 | 0.9929 | 0.8461 | 0.9166 |
| region_eval_p150_v2_final_deepfake_043 | deepfake | `[0, 0, 299, 299]` | 0.9926 | 0.9963 | 0.8583 | 0.9238 |
| region_eval_p150_v2_final_deepfake_044 | deepfake | `[0, 0, 299, 299]` | 0.9744 | 0.9870 | 0.9018 | 0.9484 |
| region_eval_p150_v2_final_deepfake_045 | deepfake | `[0, 0, 299, 299]` | 0.9609 | 0.9800 | 0.8622 | 0.9260 |
| region_eval_p150_v2_final_deepfake_046 | deepfake | `[0, 0, 299, 299]` | 0.8734 | 0.9324 | 0.7505 | 0.8575 |
| region_eval_p150_v2_final_deepfake_047 | deepfake | `[0, 0, 299, 299]` | 0.9889 | 0.9944 | 0.8709 | 0.9310 |
| region_eval_p150_v2_final_deepfake_048 | deepfake | `[0, 0, 299, 299]` | 0.9868 | 0.9934 | 0.7779 | 0.8751 |
| region_eval_p150_v2_final_deepfake_049 | deepfake | `[0, 0, 299, 299]` | 0.9613 | 0.9803 | 0.8507 | 0.9193 |
| region_eval_p150_v2_final_deepfake_050 | deepfake | `[0, 0, 299, 299]` | 0.9955 | 0.9978 | 0.8715 | 0.9313 |
| region_eval_p150_v2_final_photoshop_001 | photoshop | `[346, 177, 410, 274]` | 0.6207 | 0.7659 | 0.8608 | 0.9252 |
| region_eval_p150_v2_final_photoshop_002 | photoshop | `[668, 272, 755, 343]` | 0.5412 | 0.7023 | 0.7930 | 0.8846 |
| region_eval_p150_v2_final_photoshop_003 | photoshop | `[0, 37, 138, 201]` | 0.6663 | 0.7997 | 0.9102 | 0.9530 |
| region_eval_p150_v2_final_photoshop_004 | photoshop | `[379, 281, 600, 406]` | 0.8490 | 0.9183 | 0.9847 | 0.9923 |
| region_eval_p150_v2_final_photoshop_005 | photoshop | `[274, 140, 472, 221]` | 0.7525 | 0.8587 | 0.6839 | 0.8123 |
| region_eval_p150_v2_final_photoshop_006 | photoshop | `[87, 86, 162, 160]` | 0.9861 | 0.9930 | 0.9303 | 0.9639 |
| region_eval_p150_v2_final_photoshop_007 | photoshop | `[0, 0, 555, 164]` | 0.6930 | 0.8187 | 0.9690 | 0.9843 |
| region_eval_p150_v2_final_photoshop_008 | photoshop | `[101, 113, 150, 320]` | 0.6566 | 0.7927 | 0.8913 | 0.9425 |
| region_eval_p150_v2_final_photoshop_009 | photoshop | `[168, 263, 256, 384]` | 0.3623 | 0.5319 | 0.9001 | 0.9474 |
| region_eval_p150_v2_final_photoshop_010 | photoshop | `[309, 155, 376, 256]` | 0.5412 | 0.7023 | 0.9246 | 0.9608 |
| region_eval_p150_v2_final_photoshop_011 | photoshop | `[242, 84, 273, 111]` | 0.8913 | 0.9425 | 0.9023 | 0.9486 |
| region_eval_p150_v2_final_photoshop_012 | photoshop | `[210, 14, 252, 143]` | 0.1192 | 0.2131 | 0.8473 | 0.9173 |
| region_eval_p150_v2_final_photoshop_013 | photoshop | `[28, 220, 54, 244]` | 0.8574 | 0.9232 | 0.9252 | 0.9612 |
| region_eval_p150_v2_final_photoshop_014 | photoshop | `[249, 97, 267, 191]` | 0.4226 | 0.5941 | 0.8747 | 0.9331 |
| region_eval_p150_v2_final_photoshop_015 | photoshop | `[454, 100, 589, 239]` | 0.5264 | 0.6897 | 0.9134 | 0.9547 |
| region_eval_p150_v2_final_photoshop_016 | photoshop | `[234, 227, 242, 243]` | 0.6328 | 0.7751 | 0.6142 | 0.7610 |
| region_eval_p150_v2_final_photoshop_017 | photoshop | `[283, 34, 351, 58]` | 0.2947 | 0.4553 | 0.9031 | 0.9491 |
| region_eval_p150_v2_final_photoshop_018 | photoshop | `[0, 0, 561, 175]` | 0.7691 | 0.8695 | 0.9710 | 0.9853 |
| region_eval_p150_v2_final_photoshop_019 | photoshop | `[166, 123, 384, 256]` | 0.6501 | 0.7880 | 0.9485 | 0.9736 |
| region_eval_p150_v2_final_photoshop_020 | photoshop | `[54, 67, 76, 129]` | 0.5770 | 0.7318 | 0.8966 | 0.9455 |
| region_eval_p150_v2_final_photoshop_021 | photoshop | `[96, 192, 143, 237]` | 0.5357 | 0.6977 | 0.8358 | 0.9106 |
| region_eval_p150_v2_final_photoshop_022 | photoshop | `[122, 256, 174, 368]` | 0.2610 | 0.4139 | 0.8357 | 0.9105 |
| region_eval_p150_v2_final_photoshop_023 | photoshop | `[308, 22, 371, 44]` | 0.7172 | 0.8353 | 0.9485 | 0.9736 |
| region_eval_p150_v2_final_photoshop_024 | photoshop | `[201, 84, 258, 205]` | 0.5108 | 0.6762 | 0.8529 | 0.9206 |
| region_eval_p150_v2_final_photoshop_025 | photoshop | `[182, 69, 289, 125]` | 0.2078 | 0.3441 | 0.8722 | 0.9317 |
| region_eval_p150_v2_final_photoshop_026 | photoshop | `[238, 83, 281, 122]` | 0.7627 | 0.8654 | 0.9273 | 0.9623 |
| region_eval_p150_v2_final_photoshop_027 | photoshop | `[244, 149, 256, 204]` | 0.7591 | 0.8630 | 0.5808 | 0.7348 |
| region_eval_p150_v2_final_photoshop_028 | photoshop | `[72, 0, 308, 95]` | 0.4116 | 0.5832 | 0.8732 | 0.9323 |
| region_eval_p150_v2_final_photoshop_029 | photoshop | `[55, 91, 157, 256]` | 0.5053 | 0.6714 | 0.7881 | 0.8815 |
| region_eval_p150_v2_final_photoshop_030 | photoshop | `[42, 14, 108, 81]` | 0.3650 | 0.5348 | 0.8960 | 0.9451 |
| region_eval_p150_v2_final_photoshop_031 | photoshop | `[0, 111, 37, 240]` | 0.8207 | 0.9015 | 0.9715 | 0.9855 |
| region_eval_p150_v2_final_photoshop_032 | photoshop | `[0, 56, 157, 256]` | 0.9539 | 0.9764 | 0.7537 | 0.8595 |
| region_eval_p150_v2_final_photoshop_033 | photoshop | `[119, 23, 459, 104]` | 0.7548 | 0.8603 | 0.6640 | 0.7981 |
| region_eval_p150_v2_final_photoshop_034 | photoshop | `[0, 0, 256, 72]` | 0.6309 | 0.7737 | 0.9641 | 0.9817 |
| region_eval_p150_v2_final_photoshop_035 | photoshop | `[157, 27, 214, 98]` | 0.7166 | 0.8349 | 0.9543 | 0.9766 |
| region_eval_p150_v2_final_photoshop_036 | photoshop | `[217, 77, 349, 256]` | 0.5973 | 0.7479 | 0.9658 | 0.9826 |
| region_eval_p150_v2_final_photoshop_037 | photoshop | `[284, 117, 350, 206]` | 0.5809 | 0.7349 | 0.8415 | 0.9139 |
| region_eval_p150_v2_final_photoshop_038 | photoshop | `[393, 307, 526, 338]` | 0.8077 | 0.8936 | 0.8122 | 0.8964 |
| region_eval_p150_v2_final_photoshop_039 | photoshop | `[331, 0, 347, 236]` | 0.7783 | 0.8754 | 0.9538 | 0.9764 |
| region_eval_p150_v2_final_photoshop_040 | photoshop | `[4, 0, 204, 68]` | 0.2971 | 0.4581 | 0.9241 | 0.9606 |
| region_eval_p150_v2_final_photoshop_041 | photoshop | `[128, 16, 218, 120]` | 0.8698 | 0.9303 | 0.9661 | 0.9827 |
| region_eval_p150_v2_final_photoshop_042 | photoshop | `[646, 210, 744, 282]` | 0.8546 | 0.9216 | 0.9318 | 0.9647 |
| region_eval_p150_v2_final_photoshop_043 | photoshop | `[235, 175, 333, 220]` | 0.9834 | 0.9917 | 0.9080 | 0.9518 |
| region_eval_p150_v2_final_photoshop_044 | photoshop | `[48, 54, 205, 195]` | 0.8287 | 0.9064 | 0.9474 | 0.9730 |
| region_eval_p150_v2_final_photoshop_045 | photoshop | `[101, 42, 157, 93]` | 0.5455 | 0.7059 | 0.4564 | 0.6268 |
| region_eval_p150_v2_final_photoshop_046 | photoshop | `[0, 0, 178, 256]` | 0.9927 | 0.9963 | 0.3392 | 0.5065 |
| region_eval_p150_v2_final_photoshop_047 | photoshop | `[177, 94, 192, 128]` | 0.9078 | 0.9517 | 0.8140 | 0.8975 |
| region_eval_p150_v2_final_photoshop_048 | photoshop | `[443, 276, 515, 314]` | 0.5936 | 0.7450 | 0.8806 | 0.9365 |
| region_eval_p150_v2_final_photoshop_049 | photoshop | `[0, 0, 384, 106]` | 0.5486 | 0.7085 | 0.9496 | 0.9741 |
| region_eval_p150_v2_final_photoshop_050 | photoshop | `[323, 58, 361, 153]` | 0.5645 | 0.7217 | 0.9146 | 0.9554 |
