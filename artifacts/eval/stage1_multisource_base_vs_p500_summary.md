# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 120 | 0.9833 (118/120) | 0.0167 (2/120) | 0.5583 (67/120) | 0.9833 (59/60) | 0.1333 (8/60) | 0.0167 (1/60) |
| json_p500 | 120 | 1.0000 (120/120) | 1.0000 (120/120) | 0.7500 (90/120) | 0.5667 (34/60) | 0.9333 (56/60) | 0.5667 (34/60) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | aigc_editing | 40 | 0.6750 (27/40) | 0.9500 (19/20) | 0.4000 (8/20) | 0.0000 (0/20) |
| json_p500 | aigc_editing | 40 | 0.9250 (37/40) | 0.9500 (19/20) | 0.9000 (18/20) | 0.9500 (19/20) |
| base | deepfake | 40 | 0.5000 (20/40) | 1.0000 (20/20) | 0.0000 (0/20) | 0.0000 (0/20) |
| json_p500 | deepfake | 40 | 0.6500 (26/40) | 0.3000 (6/20) | 1.0000 (20/20) | 0.3000 (6/20) |
| base | photoshop | 40 | 0.5000 (20/40) | 1.0000 (20/20) | 0.0000 (0/20) | 0.0500 (1/20) |
| json_p500 | photoshop | 40 | 0.6750 (27/40) | 0.4500 (9/20) | 0.9000 (18/20) | 0.4500 (9/20) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | CASIA | 40 | 0.5000 (20/40) | 1.0000 (20/20) | 0.0000 (0/20) | 0.0500 (1/20) |
| json_p500 | CASIA | 40 | 0.6750 (27/40) | 0.4500 (9/20) | 0.9000 (18/20) | 0.4500 (9/20) |
| base | FFHQ | 20 | 0.0000 (0/20) | n/a (0/0) | 0.0000 (0/20) | n/a (0/0) |
| json_p500 | FFHQ | 20 | 1.0000 (20/20) | n/a (0/0) | 1.0000 (20/20) | n/a (0/0) |
| base | FaceApp | 20 | 1.0000 (20/20) | 1.0000 (20/20) | n/a (0/0) | 0.0000 (0/20) |
| json_p500 | FaceApp | 20 | 0.3000 (6/20) | 0.3000 (6/20) | n/a (0/0) | 0.3000 (6/20) |
| base | SD-inpaint | 40 | 0.6750 (27/40) | 0.9500 (19/20) | 0.4000 (8/20) | 0.0000 (0/20) |
| json_p500 | SD-inpaint | 40 | 0.9250 (37/40) | 0.9500 (19/20) | 0.9000 (18/20) | 0.9500 (19/20) |

## Dataset Build

- total: `120`
- per_label: `20`
- seed: `42`

### Skipped Sources

| source | reason |
|---|---|
| IMD2020 | missing dataset/photoshop/IMD2020 |
| Columbia | missing dataset/photoshop/Columbia |
| Coverage | missing dataset/photoshop/Coverage |

## Conclusion

`json_p500` supports cross-type image-level discrimination on the sampled subsets.

## Predictions

| idx | source | type | label | base | json_p500 | image |
|---:|---|---|---|---|---|---|
| 0 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_nat_30130.jpg` |
| 1 | CASIA | photoshop | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_cha_30176.jpg` |
| 2 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_art_30618.jpg` |
| 3 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ani_30307.jpg` |
| 4 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ani_30494.jpg` |
| 5 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ani_00062.jpg` |
| 6 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_nat_30059.jpg` |
| 7 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_pla_30025.jpg` |
| 8 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ani_30622.jpg` |
| 9 | CASIA | photoshop | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_pla_30314.jpg` |
| 10 | CASIA | photoshop | authentic / none | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_sec_30237.jpg` |
| 11 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ani_00003.jpg` |
| 12 | CASIA | photoshop | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_sec_30560.jpg` |
| 13 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ind_30111.jpg` |
| 14 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_sec_30019.jpg` |
| 15 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_pla_30691.jpg` |
| 16 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_sec_30566.jpg` |
| 17 | CASIA | photoshop | authentic / none | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ind_30004.jpg` |
| 18 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_ani_30098.jpg` |
| 19 | CASIA | photoshop | authentic / none | tampered / color saturation and contrast / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/authentic/Au_cha_30158.jpg` |
| 20 | CASIA | photoshop | tampered / photoshop | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CRD_S_N_cha10204_cha10204_12351.jpg` |
| 21 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CNN_S_B_nat10109_nat10109_11354.jpg` |
| 22 | CASIA | photoshop | tampered / photoshop | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_art00056_art00056_10291.tif` |
| 23 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_cha10151_cha00062_12220.jpg` |
| 24 | CASIA | photoshop | tampered / photoshop | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_ani10221_ani10221_12392.jpg` |
| 25 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_sec20015_sec20015_01605.tif` |
| 26 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NND_S_N_art00071_art00071_01242.tif` |
| 27 | CASIA | photoshop | tampered / photoshop | tampered / foreground / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_art20012_art20012_01818.tif` |
| 28 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_nat20045_nat20045_01549.tif` |
| 29 | CASIA | photoshop | tampered / photoshop | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec00008_sec00008_00028.tif` |
| 30 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec00080_sec00080_10381.tif` |
| 31 | CASIA | photoshop | tampered / photoshop | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_ind20006_ind20006_02266.tif` |
| 32 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_nat00086_nat00086_10599.jpg` |
| 33 | CASIA | photoshop | tampered / photoshop | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_sec20004_sec20004_02116.tif` |
| 34 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_nat10142_arc00069_11962.jpg` |
| 35 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_CRN_S_N_txt00051_txt00051_01278.tif` |
| 36 | CASIA | photoshop | tampered / photoshop | tampered / background elements / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_D_NRN_M_B_arc00091_nat00097_11202.jpg` |
| 37 | CASIA | photoshop | tampered / photoshop | tampered / lighting and blurring / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_nat10146_nat10146_11992.jpg` |
| 38 | CASIA | photoshop | tampered / photoshop | tampered / photoshop / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc00084_arc00084_01046.tif` |
| 39 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/photoshop/CASIA/tampered/Tp_D_NNN_S_O_pla10121_sec00097_11693.jpg` |
| 40 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_14165.png` |
| 41 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_05113.png` |
| 42 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_12413.png` |
| 43 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_01721.png` |
| 44 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_18216.png` |
| 45 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_04617.png` |
| 46 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_17925.png` |
| 47 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_04575.png` |
| 48 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_15429.png` |
| 49 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_05813.png` |
| 50 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_02735.png` |
| 51 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_16677.png` |
| 52 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_15761.png` |
| 53 | FFHQ | deepfake | authentic / none | tampered / skin texture / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_00752.png` |
| 54 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_13484.png` |
| 55 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_02059.png` |
| 56 | FFHQ | deepfake | authentic / none | tampered / piercings / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_02125.png` |
| 57 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_17848.png` |
| 58 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_15359.png` |
| 59 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FFHQ/authentic/R_FFHQ_11198.png` |
| 60 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_00287-3.png` |
| 61 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_01070-1.png` |
| 62 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00164-2.png` |
| 63 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_01791-2.png` |
| 64 | FaceApp | deepfake | tampered / deepfake | tampered / lighting and exposure / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_00591-1.png` |
| 65 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_01267-2.png` |
| 66 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_01714-1.png` |
| 67 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00773-1.png` |
| 68 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00034-2.png` |
| 69 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00128-3.png` |
| 70 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00081-2.png` |
| 71 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_00112-1.png` |
| 72 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_00757-3.png` |
| 73 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00094-1.png` |
| 74 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_01709-1.png` |
| 75 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_00310-2.png` |
| 76 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_01877-1.png` |
| 77 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP1_00767-2.png` |
| 78 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_00054-1.png` |
| 79 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/deepfake/FaceApp/tampered/F_FAP0_01481-3.png` |
| 80 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000114101.jpg` |
| 81 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000252986.jpg` |
| 82 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000226524.jpg` |
| 83 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000034423.jpg` |
| 84 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000496939.jpg` |
| 85 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000047515.jpg` |
| 86 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000483796.jpg` |
| 87 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000190413.jpg` |
| 88 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000309817.jpg` |
| 89 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation of the train's appearance inside the fireplace. / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000406557.jpg` |
| 90 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000272610.jpg` |
| 91 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000393274.jpg` |
| 92 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000243773.jpg` |
| 93 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000556568.jpg` |
| 94 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000427070.jpg` |
| 95 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000322869.jpg` |
| 96 | SD-inpaint | aigc_editing | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000367977.jpg` |
| 97 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000431168.jpg` |
| 98 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000028690.jpg` |
| 99 | SD-inpaint | aigc_editing | authentic / none | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/authentic/000000323288.jpg` |
| 100 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / entire image / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/14069.png` |
| 101 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / black and white filter / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/16320.png` |
| 102 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/11263.png` |
| 103 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation of the deer's legs and feet / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/9147.png` |
| 104 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/7303.png` |
| 105 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/11267.png` |
| 106 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/19312.png` |
| 107 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/5674.png` |
| 108 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/14522.png` |
| 109 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / color saturation and contrast / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/14051.png` |
| 110 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | authentic / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/3665.png` |
| 111 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / head / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/15634.png` |
| 112 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/0088.png` |
| 113 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/2048.png` |
| 114 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / background / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/19808.png` |
| 115 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/12116.png` |
| 116 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / food / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/18578.png` |
| 117 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/18296.jpg` |
| 118 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/19650.png` |
| 119 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / entire_image / json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval/images/aigc_editing/SD-inpaint/tampered/15619.png` |
