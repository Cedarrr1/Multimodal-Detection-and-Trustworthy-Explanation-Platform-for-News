# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 75 | 0.7200 (54/75) | 0.0267 (2/75) | 0.6667 (50/75) | 1.0000 (50/50) | 0.0000 (0/25) | 0.0600 (3/50) |
| json_p500 | 75 | 0.9067 (68/75) | 0.9067 (68/75) | 0.8533 (64/75) | 0.9800 (49/50) | 0.6000 (15/25) | 0.9800 (49/50) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | aigc_editing | 25 | 0.0000 (0/25) | n/a (0/0) | 0.0000 (0/25) | n/a (0/0) |
| json_p500 | aigc_editing | 25 | 0.6000 (15/25) | n/a (0/0) | 0.6000 (15/25) | n/a (0/0) |
| base | deepfake | 50 | 1.0000 (50/50) | 1.0000 (50/50) | n/a (0/0) | 0.0600 (3/50) |
| json_p500 | deepfake | 50 | 0.9800 (49/50) | 0.9800 (49/50) | n/a (0/0) | 0.9800 (49/50) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | FaceApp | 50 | 1.0000 (50/50) | 1.0000 (50/50) | n/a (0/0) | 0.0600 (3/50) |
| json_p500 | FaceApp | 50 | 0.9800 (49/50) | 0.9800 (49/50) | n/a (0/0) | 0.9800 (49/50) |
| base | SD-inpaint | 25 | 0.0000 (0/25) | n/a (0/0) | 0.0000 (0/25) | n/a (0/0) |
| json_p500 | SD-inpaint | 25 | 0.6000 (15/25) | n/a (0/0) | 0.6000 (15/25) | n/a (0/0) |

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
