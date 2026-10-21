# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 150 | 0.4733 (71/150) | 0.0000 (0/150) | 0.3333 (50/150) | 1.0000 (50/50) | 0.0000 (0/100) | 0.0200 (1/50) |
| json_p500 | 150 | 0.8533 (128/150) | 0.8533 (128/150) | 0.7000 (105/150) | 0.5000 (25/50) | 0.8000 (80/100) | 0.2800 (14/50) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | photoshop | 150 | 0.3333 (50/150) | 1.0000 (50/50) | 0.0000 (0/100) | 0.0200 (1/50) |
| json_p500 | photoshop | 150 | 0.7000 (105/150) | 0.5000 (25/50) | 0.8000 (80/100) | 0.2800 (14/50) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | CASIA | 150 | 0.3333 (50/150) | 1.0000 (50/50) | 0.0000 (0/100) | 0.0200 (1/50) |
| json_p500 | CASIA | 150 | 0.7000 (105/150) | 0.5000 (25/50) | 0.8000 (80/100) | 0.2800 (14/50) |

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
| 0 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30341.jpg` |
| 1 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30313.jpg` |
| 2 | CASIA | photoshop | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30277.jpg` |
| 3 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_10120.jpg` |
| 4 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30064.jpg` |
| 5 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30246.jpg` |
| 6 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30224.jpg` |
| 7 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30345.jpg` |
| 8 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_30657.jpg` |
| 9 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30042.jpg` |
| 10 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30111.jpg` |
| 11 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_00062.jpg` |
| 12 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30124.jpg` |
| 13 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_20024.jpg` |
| 14 | CASIA | photoshop | authentic / none | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ind_00095.jpg` |
| 15 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30740.jpg` |
| 16 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30177.jpg` |
| 17 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ind_00029.jpg` |
| 18 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_20028.jpg` |
| 19 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30217.jpg` |
| 20 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30721.jpg` |
| 21 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30340.jpg` |
| 22 | CASIA | photoshop | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30523.jpg` |
| 23 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30587.jpg` |
| 24 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_00095.jpg` |
| 25 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_30198.jpg` |
| 26 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_30245.jpg` |
| 27 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30169.jpg` |
| 28 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30272.jpg` |
| 29 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30588.jpg` |
| 30 | CASIA | photoshop | authentic / none | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ind_20033.jpg` |
| 31 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30433.jpg` |
| 32 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30031.jpg` |
| 33 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30084.jpg` |
| 34 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_10130.jpg` |
| 35 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_10117.jpg` |
| 36 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30637.jpg` |
| 37 | CASIA | photoshop | authentic / none | tampered / color correction / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30655.jpg` |
| 38 | CASIA | photoshop | authentic / none | tampered / color / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_10001.jpg` |
| 39 | CASIA | photoshop | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30111.jpg` |
| 40 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30436.jpg` |
| 41 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30466.jpg` |
| 42 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30258.jpg` |
| 43 | CASIA | photoshop | authentic / none | tampered / sky and horizon / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30225.jpg` |
| 44 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_00067.jpg` |
| 45 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30407.jpg` |
| 46 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_00017.jpg` |
| 47 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30339.jpg` |
| 48 | CASIA | photoshop | authentic / none | tampered / text alignment / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_30233.jpg` |
| 49 | CASIA | photoshop | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_20039.jpg` |
| 50 | CASIA | photoshop | authentic / none | tampered / clothing / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30672.jpg` |
| 51 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30724.jpg` |
| 52 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30181.jpg` |
| 53 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_txt_00064.jpg` |
| 54 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30533.jpg` |
| 55 | CASIA | photoshop | authentic / none | tampered / background / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_20023.jpg` |
| 56 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30251.jpg` |
| 57 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_00024.jpg` |
| 58 | CASIA | photoshop | authentic / none | tampered / color saturation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30392.jpg` |
| 59 | CASIA | photoshop | authentic / none | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30186.jpg` |
| 60 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ind_30158.jpg` |
| 61 | CASIA | photoshop | authentic / none | tampered / color saturation or contrast / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30404.jpg` |
| 62 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30072.jpg` |
| 63 | CASIA | photoshop | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30169.jpg` |
| 64 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_20045.jpg` |
| 65 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_20072.jpg` |
| 66 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30002.jpg` |
| 67 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30554.jpg` |
| 68 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_20099.jpg` |
| 69 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30553.jpg` |
| 70 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ind_30092.jpg` |
| 71 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30596.jpg` |
| 72 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30657.jpg` |
| 73 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30341.jpg` |
| 74 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30318.jpg` |
| 75 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_30469.jpg` |
| 76 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30683.jpg` |
| 77 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30313.jpg` |
| 78 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30532.jpg` |
| 79 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30087.jpg` |
| 80 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30556.jpg` |
| 81 | CASIA | photoshop | authentic / none | tampered / color / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30494.jpg` |
| 82 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30563.jpg` |
| 83 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30042.jpg` |
| 84 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30370.jpg` |
| 85 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_00045.jpg` |
| 86 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_30466.jpg` |
| 87 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30398.jpg` |
| 88 | CASIA | photoshop | authentic / none | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_20032.jpg` |
| 89 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_arc_30329.jpg` |
| 90 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_pla_30672.jpg` |
| 91 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_txt_00017.jpg` |
| 92 | CASIA | photoshop | authentic / none | tampered / color / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30248.jpg` |
| 93 | CASIA | photoshop | authentic / none | tampered / background / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_cha_00064.jpg` |
| 94 | CASIA | photoshop | authentic / none | tampered / background / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_sec_30707.jpg` |
| 95 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_nat_30267.jpg` |
| 96 | CASIA | photoshop | authentic / none | tampered / reflection / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ind_20053.jpg` |
| 97 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_00008.jpg` |
| 98 | CASIA | photoshop | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_ani_30155.jpg` |
| 99 | CASIA | photoshop | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/authentic/Au_art_30188.jpg` |
| 100 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_art00013_art00014_10271.tif` |
| 101 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NNN_S_N_nat20023_nat20015_01527.tif` |
| 102 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_cha00036_cha00036_11736.jpg` |
| 103 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_txt00085_txt00085_11309.jpg` |
| 104 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRD_S_O_art00052_art00052_00927.tif` |
| 105 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_nat00002_cha00086_11517.jpg` |
| 106 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CND_S_N_ind00070_ind00070_01357.tif` |
| 107 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRD_L_N_ani10110_art10101_10228.tif` |
| 108 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_art00024_ind00098_01424.tif` |
| 109 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_cha00084_ani00081_00404.tif` |
| 110 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_sec00028_sec00028_10783.jpg` |
| 111 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NNN_M_N_sec00089_cha00062_11491.jpg` |
| 112 | CASIA | photoshop | tampered / photoshop | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_sec00093_cha00096_00713.tif` |
| 113 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc00096_arc00096_01034.tif` |
| 114 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_nat20054_nat20054_02249.tif` |
| 115 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec00028_sec00028_00767.tif` |
| 116 | CASIA | photoshop | tampered / photoshop | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_sec20083_sec20083_02143.tif` |
| 117 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_ani00054_ani00054_11129.jpg` |
| 118 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_S_N_art20058_art20058_01864.tif` |
| 119 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_S_B_cha00047_cha00047_00367.tif` |
| 120 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CND_S_N_ind00078_ind00077_00476.tif` |
| 121 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_ani20046_ani20046_02089.tif` |
| 122 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_arc20041_arc20041_02177.tif` |
| 123 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_art00043_art00043_01227.tif` |
| 124 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_nat00025_ani00058_00642.tif` |
| 125 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_B_art00060_art00060_01235.tif` |
| 126 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NND_S_N_nat00011_nat00007_00631.tif` |
| 127 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_M_N_sec00070_sec00070_10716.jpg` |
| 128 | CASIA | photoshop | tampered / photoshop | tampered / background / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_nat10145_ani00024_11981.jpg` |
| 129 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_B_ani00023_ani00022_20073.jpg` |
| 130 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRD_S_B_ani00042_ani00042_00162.tif` |
| 131 | CASIA | photoshop | tampered / photoshop | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_cha00016_cha00014_11153.jpg` |
| 132 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_B_pla00014_pla00014_10986.jpg` |
| 133 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_pla00031_pla00031_10985.jpg` |
| 134 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NRN_S_N_arc20078_arc20078_01718.tif` |
| 135 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_pla10121_cha00050_11658.jpg` |
| 136 | CASIA | photoshop | tampered / photoshop | tampered / sky / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CRN_S_B_arc00095_arc00095_01035.tif` |
| 137 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_cha00027_cha00028_11785.jpg` |
| 138 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_B_sec20041_sec20041_02447.tif` |
| 139 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CRN_S_B_ind00029_art00030_20103.jpg` |
| 140 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CRN_M_N_cha10198_nat10160_12365.jpg` |
| 141 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_M_N_nat00093_nat00093_10586.jpg` |
| 142 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_S_N_sec00052_sec00055_11239.jpg` |
| 143 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_B_nat00001_art00021_11421.jpg` |
| 144 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NND_S_N_ind00067_ind00067_10688.jpg` |
| 145 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_CRN_M_N_art00067_nat00013_11804.jpg` |
| 146 | CASIA | photoshop | tampered / photoshop | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_CNN_M_N_pla10116_pla10116_10602.jpg` |
| 147 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_cha10158_cha10158_12262.jpg` |
| 148 | CASIA | photoshop | tampered / photoshop | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_D_NRN_M_N_nat10149_nat00060_12003.jpg` |
| 149 | CASIA | photoshop | tampered / photoshop | tampered / wallpaper design / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/photoshop/CASIA/tampered/Tp_S_NNN_S_N_sec00077_sec00077_00752.tif` |
