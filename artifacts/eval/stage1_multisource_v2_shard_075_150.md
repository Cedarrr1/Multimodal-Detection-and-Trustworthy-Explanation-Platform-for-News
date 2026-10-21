# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 75 | 0.6267 (47/75) | 0.0133 (1/75) | 0.3333 (25/75) | 1.0000 (25/25) | 0.0000 (0/50) | 0.0000 (0/25) |
| json_p500 | 75 | 0.9467 (71/75) | 0.9467 (71/75) | 0.7200 (54/75) | 0.4400 (11/25) | 0.8600 (43/50) | 0.2800 (7/25) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | deepfake | 50 | 0.0000 (0/50) | n/a (0/0) | 0.0000 (0/50) | n/a (0/0) |
| json_p500 | deepfake | 50 | 0.8600 (43/50) | n/a (0/0) | 0.8600 (43/50) | n/a (0/0) |
| base | photoshop | 25 | 1.0000 (25/25) | 1.0000 (25/25) | n/a (0/0) | 0.0000 (0/25) |
| json_p500 | photoshop | 25 | 0.4400 (11/25) | 0.4400 (11/25) | n/a (0/0) | 0.2800 (7/25) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | CASIA | 25 | 1.0000 (25/25) | 1.0000 (25/25) | n/a (0/0) | 0.0000 (0/25) |
| json_p500 | CASIA | 25 | 0.4400 (11/25) | 0.4400 (11/25) | n/a (0/0) | 0.2800 (7/25) |
| base | FFHQ | 50 | 0.0000 (0/50) | n/a (0/0) | 0.0000 (0/50) | n/a (0/0) |
| json_p500 | FFHQ | 50 | 0.8600 (43/50) | n/a (0/0) | 0.8600 (43/50) | n/a (0/0) |

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
