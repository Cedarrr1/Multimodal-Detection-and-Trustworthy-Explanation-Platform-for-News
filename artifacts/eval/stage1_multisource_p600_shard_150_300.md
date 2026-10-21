# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 150 | 0.7000 (105/150) | 0.0200 (3/150) | 0.3333 (50/150) | 1.0000 (50/50) | 0.0000 (0/100) | 0.0400 (2/50) |
| json_p500 | 150 | 0.9400 (141/150) | 0.9400 (141/150) | 0.6933 (104/150) | 0.4200 (21/50) | 0.8300 (83/100) | 0.2400 (12/50) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | deepfake | 100 | 0.0000 (0/100) | n/a (0/0) | 0.0000 (0/100) | n/a (0/0) |
| json_p500 | deepfake | 100 | 0.8300 (83/100) | n/a (0/0) | 0.8300 (83/100) | n/a (0/0) |
| base | photoshop | 50 | 1.0000 (50/50) | 1.0000 (50/50) | n/a (0/0) | 0.0400 (2/50) |
| json_p500 | photoshop | 50 | 0.4200 (21/50) | 0.4200 (21/50) | n/a (0/0) | 0.2400 (12/50) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | CASIA | 50 | 1.0000 (50/50) | 1.0000 (50/50) | n/a (0/0) | 0.0400 (2/50) |
| json_p500 | CASIA | 50 | 0.4200 (21/50) | 0.4200 (21/50) | n/a (0/0) | 0.2400 (12/50) |
| base | FFHQ | 100 | 0.0000 (0/100) | n/a (0/0) | 0.0000 (0/100) | n/a (0/0) |
| json_p500 | FFHQ | 100 | 0.8300 (83/100) | n/a (0/0) | 0.8300 (83/100) | n/a (0/0) |

## Dataset Build

- total: `600`
- per_label: `100`
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
| 150 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NND_S_N_ani00012_ani00012_00132.tif` |
| 151 | CASIA | photoshop | tampered / photoshop | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc10118_arc10118_10760.jpg` |
| 152 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_art00098_sec10101_10345.tif` |
| 153 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_arc00065_cha00072_11460.jpg` |
| 154 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc20091_arc20091_01731.tif` |
| 155 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_ind00012_ind00012_10411.tif` |
| 156 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_O_sec00001_sec00007_10032.tif` |
| 157 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_nat00082_nat00082_00986.tif` |
| 158 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CRN_M_N_txt00084_txt00084_11301.jpg` |
| 159 | CASIA | photoshop | tampered / photoshop | tampered / entire image / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRD_S_N_art00005_art00076_11791.jpg` |
| 160 | CASIA | photoshop | tampered / photoshop | tampered / clock / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NNN_S_N_ind00070_ind00074_10930.jpg` |
| 161 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_B_arc00056_arc00056_00276.tif` |
| 162 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_nat10150_nat10124_12033.jpg` |
| 163 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_nat00002_nat00002_11058.jpg` |
| 164 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CRD_S_O_ani10111_ani10103_10635.jpg` |
| 165 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CRN_S_N_txt00041_txt00039_10829.jpg` |
| 166 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_nat10110_cha00086_11370.jpg` |
| 167 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CRN_M_O_pla10102_ani10104_10028.tif` |
| 168 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla20060_pla20060_02372.tif` |
| 169 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_O_sec20054_sec20042_01644.tif` |
| 170 | CASIA | photoshop | tampered / photoshop | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NNN_M_O_sec00039_nat00001_00060.tif` |
| 171 | CASIA | photoshop | tampered / photoshop | tampered / photoshop / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CNN_M_N_cha00026_cha00028_11784.jpg` |
| 172 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CND_S_N_pla20091_pla20091_02351.tif` |
| 173 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_ani20019_ani20019_02062.tif` |
| 174 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CNN_S_B_art10110_cha10110_11564.jpg` |
| 175 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_M_N_cha10156_cha10156_12249.jpg` |
| 176 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CRN_S_N_cha10190_cha10190_12326.jpg` |
| 177 | CASIA | photoshop | tampered / photoshop | tampered / lighting / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_ind20042_ind20042_01783.tif` |
| 178 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NNN_S_B_nat00079_nat00040_00676.tif` |
| 179 | CASIA | photoshop | tampered / photoshop | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla00032_pla00032_01147.tif` |
| 180 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec20100_sec20100_02139.tif` |
| 181 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla00022_pla00022_20085.jpg` |
| 182 | CASIA | photoshop | tampered / photoshop | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_B_ind00077_ind00077_01363.tif` |
| 183 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_ani10207_ani10207_12418.jpg` |
| 184 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_cha00040_ani00013_00360.tif` |
| 185 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_txt10113_txt10113_10865.jpg` |
| 186 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_pla00055_pla00055_00589.tif` |
| 187 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_nat20011_nat20011_01515.tif` |
| 188 | CASIA | photoshop | tampered / photoshop | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NND_S_N_ind20002_ind20002_02262.tif` |
| 189 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_O_arc00023_cha00014_10011.tif` |
| 190 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_nat10137_nat00095_11938.jpg` |
| 191 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_ani10197_ani10197_12406.jpg` |
| 192 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_ani00004_ani00004_00124.tif` |
| 193 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_art00003_ani00013_01193.tif` |
| 194 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CNN_S_N_ani00053_ani00051_11148.jpg` |
| 195 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRD_S_B_sec00001_sec00001_00021.tif` |
| 196 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla20076_pla20076_01976.tif` |
| 197 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla20060_pla20060_02488.tif` |
| 198 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NNN_S_N_ani10174_ani10173_12454.jpg` |
| 199 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_B_ind00025_cha10101_10050.tif` |
| 200 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14310.png` |
| 201 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_15891.png` |
| 202 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17790.png` |
| 203 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_04497.png` |
| 204 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_07541.png` |
| 205 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03792.png` |
| 206 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_07796.png` |
| 207 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_01659.png` |
| 208 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_07337.png` |
| 209 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03216.png` |
| 210 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_12637.png` |
| 211 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_04153.png` |
| 212 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06425.png` |
| 213 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_12169.png` |
| 214 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_18922.png` |
| 215 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03757.png` |
| 216 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_10506.png` |
| 217 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17934.png` |
| 218 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06042.png` |
| 219 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_18240.png` |
| 220 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_07937.png` |
| 221 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17736.png` |
| 222 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_16322.png` |
| 223 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08285.png` |
| 224 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03894.png` |
| 225 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06917.png` |
| 226 | FFHQ | deepfake | authentic / none | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_02855.png` |
| 227 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17300.png` |
| 228 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08242.png` |
| 229 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17160.png` |
| 230 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_12636.png` |
| 231 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_13331.png` |
| 232 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06244.png` |
| 233 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_09200.png` |
| 234 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_15778.png` |
| 235 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_19080.png` |
| 236 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_09163.png` |
| 237 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_02348.png` |
| 238 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_12977.png` |
| 239 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_18963.png` |
| 240 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_13891.png` |
| 241 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_02931.png` |
| 242 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_10077.png` |
| 243 | FFHQ | deepfake | authentic / none | tampered / digital / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_09195.png` |
| 244 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_15495.png` |
| 245 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_13551.png` |
| 246 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08221.png` |
| 247 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06433.png` |
| 248 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_11297.png` |
| 249 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08012.png` |
| 250 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_19350.png` |
| 251 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_01810.png` |
| 252 | FFHQ | deepfake | authentic / none | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_10030.png` |
| 253 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_19332.png` |
| 254 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_00804.png` |
| 255 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14732.png` |
| 256 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08616.png` |
| 257 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_04611.png` |
| 258 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_02287.png` |
| 259 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_16092.png` |
| 260 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03543.png` |
| 261 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_10671.png` |
| 262 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_11157.png` |
| 263 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_04356.png` |
| 264 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_13099.png` |
| 265 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14139.png` |
| 266 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_07271.png` |
| 267 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_05003.png` |
| 268 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_02919.png` |
| 269 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_05135.png` |
| 270 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14226.png` |
| 271 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_11688.png` |
| 272 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17539.png` |
| 273 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08760.png` |
| 274 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_07064.png` |
| 275 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_09143.png` |
| 276 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_05523.png` |
| 277 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_19050.png` |
| 278 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_18334.png` |
| 279 | FFHQ | deepfake | authentic / none | tampered / clothing / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_12796.png` |
| 280 | FFHQ | deepfake | authentic / none | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06388.png` |
| 281 | FFHQ | deepfake | authentic / none | tampered / digital / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_10580.png` |
| 282 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_19041.png` |
| 283 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_05839.png` |
| 284 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_19706.png` |
| 285 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_10757.png` |
| 286 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08310.png` |
| 287 | FFHQ | deepfake | authentic / none | tampered / clothing / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_18508.png` |
| 288 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03418.png` |
| 289 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_09951.png` |
| 290 | FFHQ | deepfake | authentic / none | tampered / clothing / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_04823.png` |
| 291 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_06227.png` |
| 292 | FFHQ | deepfake | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_15429.png` |
| 293 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_03837.png` |
| 294 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14544.png` |
| 295 | FFHQ | deepfake | authentic / none | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_11078.png` |
| 296 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14993.png` |
| 297 | FFHQ | deepfake | authentic / none | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_08667.png` |
| 298 | FFHQ | deepfake | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_14079.png` |
| 299 | FFHQ | deepfake | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FFHQ/authentic/R_FFHQ_17633.png` |
