# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 300 | 0.5367 (161/300) | 0.0100 (3/300) | 0.5000 (150/300) | 1.0000 (150/150) | 0.0000 (0/150) | 0.0200 (3/150) |
| json_p500 | 300 | 0.8533 (256/300) | 0.8533 (256/300) | 0.6767 (203/300) | 0.5933 (89/150) | 0.7600 (114/150) | 0.4000 (60/150) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | aigc_editing | 100 | 0.5000 (50/100) | 1.0000 (50/50) | 0.0000 (0/50) | 0.0000 (0/50) |
| json_p500 | aigc_editing | 100 | 0.4400 (44/100) | 0.3200 (16/50) | 0.5600 (28/50) | 0.0000 (0/50) |
| base | deepfake | 100 | 0.5000 (50/100) | 1.0000 (50/50) | 0.0000 (0/50) | 0.0600 (3/50) |
| json_p500 | deepfake | 100 | 0.9200 (92/100) | 0.9800 (49/50) | 0.8600 (43/50) | 0.9800 (49/50) |
| base | photoshop | 100 | 0.5000 (50/100) | 1.0000 (50/50) | 0.0000 (0/50) | 0.0000 (0/50) |
| json_p500 | photoshop | 100 | 0.6700 (67/100) | 0.4800 (24/50) | 0.8600 (43/50) | 0.2200 (11/50) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | CASIA | 100 | 0.5000 (50/100) | 1.0000 (50/50) | 0.0000 (0/50) | 0.0000 (0/50) |
| json_p500 | CASIA | 100 | 0.6700 (67/100) | 0.4800 (24/50) | 0.8600 (43/50) | 0.2200 (11/50) |
| base | FFHQ | 50 | 0.0000 (0/50) | n/a (0/0) | 0.0000 (0/50) | n/a (0/0) |
| json_p500 | FFHQ | 50 | 0.8600 (43/50) | n/a (0/0) | 0.8600 (43/50) | n/a (0/0) |
| base | FaceApp | 50 | 1.0000 (50/50) | 1.0000 (50/50) | n/a (0/0) | 0.0600 (3/50) |
| json_p500 | FaceApp | 50 | 0.9800 (49/50) | 0.9800 (49/50) | n/a (0/0) | 0.9800 (49/50) |
| base | SD-inpaint | 100 | 0.5000 (50/100) | 1.0000 (50/50) | 0.0000 (0/50) | 0.0000 (0/50) |
| json_p500 | SD-inpaint | 100 | 0.4400 (44/100) | 0.3200 (16/50) | 0.5600 (28/50) | 0.0000 (0/50) |

## Dataset Build

- total: `300`
- per_label: `50`
- seed: `20260705`

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
| 0 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_arc_30341.jpg` |
| 1 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_arc_30313.jpg` |
| 2 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30277.jpg` |
| 3 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_10120.jpg` |
| 4 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30064.jpg` |
| 5 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30246.jpg` |
| 6 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30224.jpg` |
| 7 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_30345.jpg` |
| 8 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_art_30657.jpg` |
| 9 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30042.jpg` |
| 10 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30111.jpg` |
| 11 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_arc_00062.jpg` |
| 12 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30124.jpg` |
| 13 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_20024.jpg` |
| 14 | CASIA | photoshop | authentic / none | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ind_00095.jpg` |
| 15 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_arc_30740.jpg` |
| 16 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_30177.jpg` |
| 17 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ind_00029.jpg` |
| 18 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_20028.jpg` |
| 19 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_30217.jpg` |
| 20 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_30721.jpg` |
| 21 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_30340.jpg` |
| 22 | CASIA | photoshop | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30523.jpg` |
| 23 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30587.jpg` |
| 24 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_cha_00095.jpg` |
| 25 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_art_30198.jpg` |
| 26 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_art_30245.jpg` |
| 27 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_30169.jpg` |
| 28 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_30272.jpg` |
| 29 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30588.jpg` |
| 30 | CASIA | photoshop | authentic / none | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ind_20033.jpg` |
| 31 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_30433.jpg` |
| 32 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_30031.jpg` |
| 33 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30084.jpg` |
| 34 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_10130.jpg` |
| 35 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_10117.jpg` |
| 36 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_30637.jpg` |
| 37 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_30655.jpg` |
| 38 | CASIA | photoshop | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_pla_10001.jpg` |
| 39 | CASIA | photoshop | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_arc_30111.jpg` |
| 40 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30436.jpg` |
| 41 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_sec_30466.jpg` |
| 42 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30258.jpg` |
| 43 | CASIA | photoshop | authentic / none | tampered / sky and horizon / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_nat_30225.jpg` |
| 44 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_00067.jpg` |
| 45 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30407.jpg` |
| 46 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_art_00017.jpg` |
| 47 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_ani_30339.jpg` |
| 48 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_art_30233.jpg` |
| 49 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/authentic/Au_arc_20039.jpg` |
| 50 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_art00013_art00014_10271.tif` |
| 51 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NNN_S_N_nat20023_nat20015_01527.tif` |
| 52 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_cha00036_cha00036_11736.jpg` |
| 53 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_txt00085_txt00085_11309.jpg` |
| 54 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRD_S_O_art00052_art00052_00927.tif` |
| 55 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_nat00002_cha00086_11517.jpg` |
| 56 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CND_S_N_ind00070_ind00070_01357.tif` |
| 57 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRD_L_N_ani10110_art10101_10228.tif` |
| 58 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_art00024_ind00098_01424.tif` |
| 59 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_cha00084_ani00081_00404.tif` |
| 60 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_sec00028_sec00028_10783.jpg` |
| 61 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NNN_M_N_sec00089_cha00062_11491.jpg` |
| 62 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_sec00093_cha00096_00713.tif` |
| 63 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc00096_arc00096_01034.tif` |
| 64 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_nat20054_nat20054_02249.tif` |
| 65 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec00028_sec00028_00767.tif` |
| 66 | CASIA | photoshop | tampered / photoshop | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_sec20083_sec20083_02143.tif` |
| 67 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_ani00054_ani00054_11129.jpg` |
| 68 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_art20058_art20058_01864.tif` |
| 69 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CNN_S_B_cha00047_cha00047_00367.tif` |
| 70 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_CND_S_N_ind00078_ind00077_00476.tif` |
| 71 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_ani20046_ani20046_02089.tif` |
| 72 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc20041_arc20041_02177.tif` |
| 73 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_art00043_art00043_01227.tif` |
| 74 | CASIA | photoshop | tampered / photoshop | tampered / lighting / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_nat00025_ani00058_00642.tif` |
| 75 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_B_art00060_art00060_01235.tif` |
| 76 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NND_S_N_nat00011_nat00007_00631.tif` |
| 77 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRN_M_N_sec00070_sec00070_10716.jpg` |
| 78 | CASIA | photoshop | tampered / photoshop | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_nat10145_ani00024_11981.jpg` |
| 79 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_B_ani00023_ani00022_20073.jpg` |
| 80 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRD_S_B_ani00042_ani00042_00162.tif` |
| 81 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_cha00016_cha00014_11153.jpg` |
| 82 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRN_S_B_pla00014_pla00014_10986.jpg` |
| 83 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla00031_pla00031_10985.jpg` |
| 84 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_arc20078_arc20078_01718.tif` |
| 85 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_pla10121_cha00050_11658.jpg` |
| 86 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CRN_S_B_arc00095_arc00095_01035.tif` |
| 87 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_cha00027_cha00028_11785.jpg` |
| 88 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_B_sec20041_sec20041_02447.tif` |
| 89 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_CRN_S_B_ind00029_art00030_20103.jpg` |
| 90 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_CRN_M_N_cha10198_nat10160_12365.jpg` |
| 91 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_M_N_nat00093_nat00093_10586.jpg` |
| 92 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_sec00052_sec00055_11239.jpg` |
| 93 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_M_B_nat00001_art00021_11421.jpg` |
| 94 | CASIA | photoshop | tampered / photoshop | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NND_S_N_ind00067_ind00067_10688.jpg` |
| 95 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_CRN_M_N_art00067_nat00013_11804.jpg` |
| 96 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_pla10116_pla10116_10602.jpg` |
| 97 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_cha10158_cha10158_12262.jpg` |
| 98 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_nat10149_nat00060_12003.jpg` |
| 99 | CASIA | photoshop | tampered / photoshop | tampered / wallpaper design / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec00077_sec00077_00752.tif` |
| 100 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_14310.png` |
| 101 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_15891.png` |
| 102 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_17790.png` |
| 103 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_04497.png` |
| 104 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_07541.png` |
| 105 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_03792.png` |
| 106 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_07796.png` |
| 107 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_01659.png` |
| 108 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_07337.png` |
| 109 | FFHQ | deepfake | authentic / none | tampered / clothing / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_03216.png` |
| 110 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_12637.png` |
| 111 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_04153.png` |
| 112 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_06425.png` |
| 113 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_12169.png` |
| 114 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_18922.png` |
| 115 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_03757.png` |
| 116 | FFHQ | deepfake | authentic / none | tampered / head / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_10506.png` |
| 117 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_17934.png` |
| 118 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_06042.png` |
| 119 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_18240.png` |
| 120 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_07937.png` |
| 121 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_17736.png` |
| 122 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_16322.png` |
| 123 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_08285.png` |
| 124 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_03894.png` |
| 125 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_06917.png` |
| 126 | FFHQ | deepfake | authentic / none | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_02855.png` |
| 127 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_17300.png` |
| 128 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_08242.png` |
| 129 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_17160.png` |
| 130 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_12636.png` |
| 131 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_13331.png` |
| 132 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_06244.png` |
| 133 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_09200.png` |
| 134 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_15778.png` |
| 135 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_19080.png` |
| 136 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_09163.png` |
| 137 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_02348.png` |
| 138 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_12977.png` |
| 139 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_18963.png` |
| 140 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_13891.png` |
| 141 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_02931.png` |
| 142 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_10077.png` |
| 143 | FFHQ | deepfake | authentic / none | tampered / digital / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_09195.png` |
| 144 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_15495.png` |
| 145 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_13551.png` |
| 146 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_08221.png` |
| 147 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_06433.png` |
| 148 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_11297.png` |
| 149 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FFHQ/authentic/R_FFHQ_08012.png` |
| 150 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00752-2.png` |
| 151 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01640-1.png` |
| 152 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00271-3.png` |
| 153 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01346-1.png` |
| 154 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00372-2.png` |
| 155 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00404-3.png` |
| 156 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01100-3.png` |
| 157 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01204-2.png` |
| 158 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00502-2.png` |
| 159 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00000-3.png` |
| 160 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00617-2.png` |
| 161 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01115-1.png` |
| 162 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01923-2.png` |
| 163 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00746-2.png` |
| 164 | FaceApp | deepfake | tampered / deepfake | tampered / headwear / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01816-1.png` |
| 165 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00038-2.png` |
| 166 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01446-1.png` |
| 167 | FaceApp | deepfake | tampered / deepfake | tampered / facial features / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00448-3.png` |
| 168 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01921-1.png` |
| 169 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01361-3.png` |
| 170 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01450-3.png` |
| 171 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00719-1.png` |
| 172 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00512-3.png` |
| 173 | FaceApp | deepfake | tampered / deepfake | tampered / digital / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00384-1.png` |
| 174 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_02136-2.png` |
| 175 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00981-2.png` |
| 176 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00407-1.png` |
| 177 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01026-2.png` |
| 178 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01663-1.png` |
| 179 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00800-1.png` |
| 180 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01682-1.png` |
| 181 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01306-3.png` |
| 182 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00903-1.png` |
| 183 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00817-3.png` |
| 184 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00839-3.png` |
| 185 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01276-2.png` |
| 186 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00877-3.png` |
| 187 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00167-2.png` |
| 188 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_02195-1.png` |
| 189 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00666-1.png` |
| 190 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_00381-3.png` |
| 191 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00464-2.png` |
| 192 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_02163-1.png` |
| 193 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_02156-1.png` |
| 194 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01376-1.png` |
| 195 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01558-1.png` |
| 196 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP1_01627-2.png` |
| 197 | FaceApp | deepfake | tampered / deepfake | tampered / digital / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00116-1.png` |
| 198 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_01861-1.png` |
| 199 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/deepfake/FaceApp/tampered/F_FAP0_00579-1.png` |
| 200 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000212591.jpg` |
| 201 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000323399.jpg` |
| 202 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation of the bus's license plate. / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000377226.jpg` |
| 203 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000552510.jpg` |
| 204 | SD-inpaint | aigc_editing | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000424554.jpg` |
| 205 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000195332.jpg` |
| 206 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000144322.jpg` |
| 207 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000565625.jpg` |
| 208 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000490695.jpg` |
| 209 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000106010.jpg` |
| 210 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000153262.jpg` |
| 211 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000554232.jpg` |
| 212 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000124931.jpg` |
| 213 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000337446.jpg` |
| 214 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000473575.jpg` |
| 215 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000452457.jpg` |
| 216 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000092217.jpg` |
| 217 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000069523.jpg` |
| 218 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000038030.jpg` |
| 219 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000471654.jpg` |
| 220 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000261414.jpg` |
| 221 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000400966.jpg` |
| 222 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000238051.jpg` |
| 223 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000107729.jpg` |
| 224 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000014756.jpg` |
| 225 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000278646.jpg` |
| 226 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000375021.jpg` |
| 227 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000433705.jpg` |
| 228 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000296797.jpg` |
| 229 | SD-inpaint | aigc_editing | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000366788.jpg` |
| 230 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000152162.jpg` |
| 231 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000463800.jpg` |
| 232 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000050980.jpg` |
| 233 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000431133.jpg` |
| 234 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000223497.jpg` |
| 235 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000255155.jpg` |
| 236 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000022759.jpg` |
| 237 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000203160.jpg` |
| 238 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000008379.jpg` |
| 239 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000147735.jpg` |
| 240 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000012896.jpg` |
| 241 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000150538.jpg` |
| 242 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000543407.jpg` |
| 243 | SD-inpaint | aigc_editing | authentic / none | tampered / photoshop / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000127555.jpg` |
| 244 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000043872.jpg` |
| 245 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000143756.jpg` |
| 246 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000028823.jpg` |
| 247 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000435951.jpg` |
| 248 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000101431.jpg` |
| 249 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/authentic/000000054336.jpg` |
| 250 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/4355.jpg` |
| 251 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/10416.jpg` |
| 252 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/2768.jpg` |
| 253 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / photoshop / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/16138.jpg` |
| 254 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/4048.jpg` |
| 255 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/6640.jpg` |
| 256 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/0311.jpg` |
| 257 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/13130.jpg` |
| 258 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/0390.jpg` |
| 259 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/19506.jpg` |
| 260 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/13292.jpg` |
| 261 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/10479.jpg` |
| 262 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/9378.jpg` |
| 263 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/0671.jpg` |
| 264 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/13810.jpg` |
| 265 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/1227.jpg` |
| 266 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/18700.jpg` |
| 267 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/3050.jpg` |
| 268 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / entire image / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/4519.jpg` |
| 269 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/19995.jpg` |
| 270 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/7053.jpg` |
| 271 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/11005.jpg` |
| 272 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/18662.jpg` |
| 273 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/8573.jpg` |
| 274 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/15990.jpg` |
| 275 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/0442.jpg` |
| 276 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/1671.jpg` |
| 277 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/16855.jpg` |
| 278 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/2420.jpg` |
| 279 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/4944.jpg` |
| 280 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/15810.jpg` |
| 281 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/0617.jpg` |
| 282 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/0825.jpg` |
| 283 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/9160.jpg` |
| 284 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/14721.jpg` |
| 285 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/18581.jpg` |
| 286 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/17173.jpg` |
| 287 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/3068.jpg` |
| 288 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/6227.jpg` |
| 289 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/16119.jpg` |
| 290 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / door / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/14566.jpg` |
| 291 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/1056.jpg` |
| 292 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/18892.jpg` |
| 293 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/12703.jpg` |
| 294 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/7058.jpg` |
| 295 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/18822.jpg` |
| 296 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/3244.jpg` |
| 297 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/16661.jpg` |
| 298 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/4791.jpg` |
| 299 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_v2/images/aigc_editing/SD-inpaint/tampered/13087.jpg` |
