# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 75 | 0.3200 (24/75) | 0.0000 (0/75) | 0.3333 (25/75) | 1.0000 (25/25) | 0.0000 (0/50) | 0.0000 (0/25) |
| json_p500 | 75 | 0.8267 (62/75) | 0.8267 (62/75) | 0.7467 (56/75) | 0.5200 (13/25) | 0.8600 (43/50) | 0.1600 (4/25) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | photoshop | 75 | 0.3333 (25/75) | 1.0000 (25/25) | 0.0000 (0/50) | 0.0000 (0/25) |
| json_p500 | photoshop | 75 | 0.7467 (56/75) | 0.5200 (13/25) | 0.8600 (43/50) | 0.1600 (4/25) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | CASIA | 75 | 0.3333 (25/75) | 1.0000 (25/25) | 0.0000 (0/50) | 0.0000 (0/25) |
| json_p500 | CASIA | 75 | 0.7467 (56/75) | 0.5200 (13/25) | 0.8600 (43/50) | 0.1600 (4/25) |

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

`json_p500` is inconclusive on cross-type image-level discrimination.

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
