# Stage1 eval_p30 three-way evaluation

| model | valid_json_rate | verdict_accuracy | tampered_recall | authentic_accuracy | tamper_domain_accuracy |
|---|---:|---:|---:|---:|---:|
| base | 0.9667 (29/30) | 0.5333 (16/30) | 1.0000 (15/15) | 0.0667 (1/15) | 0.0000 (0/15) |
| json_p500 | 1.0000 (30/30) | 0.7333 (22/30) | 0.7333 (11/15) | 0.7333 (11/15) | 0.7333 (11/15) |
| photoshop_crop | 1.0000 (30/30) | 0.8667 (26/30) | 0.9333 (14/15) | 0.8000 (12/15) | 0.9333 (14/15) |

## Per-domain verdict accuracy

### base

| source_domain | accuracy | correct/total |
|---|---:|---:|
| aigc_edit | 0.6000 | 6/10 |
| deepfake_face | 0.5000 | 5/10 |
| photoshop_edit | 0.5000 | 5/10 |

### json_p500

| source_domain | accuracy | correct/total |
|---|---:|---:|
| aigc_edit | 0.9000 | 9/10 |
| deepfake_face | 0.8000 | 8/10 |
| photoshop_edit | 0.5000 | 5/10 |

### photoshop_crop

| source_domain | accuracy | correct/total |
|---|---:|---:|
| aigc_edit | 0.9000 | 9/10 |
| deepfake_face | 0.8000 | 8/10 |
| photoshop_edit | 0.9000 | 9/10 |

## Predictions

| idx | source_domain | label | base | json_p500 | photoshop_crop | image |
|---:|---|---|---|---|---|---|
| 0 | photoshop_edit | authentic / none | tampered / digital manipulation / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2_Au/image/Au_arc_30693.jpg` |
| 1 | photoshop_edit | authentic / none | tampered / color / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2_Au/image/Au_nat_30430.jpg` |
| 2 | photoshop_edit | authentic / none | tampered / unknown / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2_Au/image/Au_ind_30020.jpg` |
| 3 | photoshop_edit | authentic / none | tampered / digital manipulation / json | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2_Au/image/Au_art_30400.jpg` |
| 4 | photoshop_edit | authentic / none | tampered / photoshop / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2_Au/image/Au_pla_30023.jpg` |
| 5 | photoshop_edit | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2/image/Tp_S_CNN_M_N_nat00044_nat00044_10557.jpg` |
| 6 | photoshop_edit | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | tampered / photoshop / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2/image/Tp_S_NNN_S_N_pla00084_pla00084_10454.jpg` |
| 7 | photoshop_edit | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | tampered / photoshop / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2/image/Tp_D_NRN_M_N_sec10115_cha00062_11533.jpg` |
| 8 | photoshop_edit | tampered / photoshop | tampered / lighting / json | authentic / none / json | tampered / photoshop / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2/image/Tp_S_CRN_M_N_nat00001_nat00001_10556.jpg` |
| 9 | photoshop_edit | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | tampered / photoshop / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/ps/CASIA2/image/Tp_D_CRN_M_N_pla00026_pla00038_10147.jpg` |
| 10 | deepfake_face | authentic / none | tampered / photoshop / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_03340.png` |
| 11 | deepfake_face | authentic / none | tampered / digital manipulation / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_00864.png` |
| 12 | deepfake_face | authentic / none | tampered / digital manipulation / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_03285.png` |
| 13 | deepfake_face | authentic / none | tampered / photoshop / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_02051.png` |
| 14 | deepfake_face | authentic / none | tampered / digital manipulation / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/ffhq/train/image/R_FFHQ_02934.png` |
| 15 | deepfake_face | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/faceapp/train/image/F_FAP0_01626-2.png` |
| 16 | deepfake_face | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/faceapp/train/image/F_FAP0_00446-3.png` |
| 17 | deepfake_face | tampered / deepfake | tampered / headwear / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/faceapp/train/image/F_FAP0_00623-1.png` |
| 18 | deepfake_face | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/faceapp/train/image/F_FAP0_02202-2.png` |
| 19 | deepfake_face | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/df/dffd/faceapp/train/image/F_FAP0_00488-1.png` |
| 20 | aigc_edit | authentic / none | tampered / unknown / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Au/image/000000183806.jpg` |
| 21 | aigc_edit | authentic / none | tampered / color grading / json | tampered / photoshop / json | tampered / photoshop / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Au/image/000000270708.jpg` |
| 22 | aigc_edit | authentic / none | authentic / unknown / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Au/image/000000132954.jpg` |
| 23 | aigc_edit | authentic / none | tampered / unknown / non-json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Au/image/000000456446.jpg` |
| 24 | aigc_edit | authentic / none | tampered / unknown / json | authentic / none / json | authentic / none / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Au/image/000000296821.jpg` |
| 25 | aigc_edit | tampered / aigc_inpaint | tampered / digital manipulation / json | tampered / aigc_inpaint / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Tp/image/0270.png` |
| 26 | aigc_edit | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Tp/image/13568.png` |
| 27 | aigc_edit | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Tp/image/16253.png` |
| 28 | aigc_edit | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Tp/image/2419.png` |
| 29 | aigc_edit | tampered / aigc_inpaint | tampered / digital manipulation / json | tampered / aigc_inpaint / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_mmtd_eval_p30_json/images/aigc_inpaint/Tp/image/11387.png` |