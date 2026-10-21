# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 75 | 0.4800 (36/75) | 0.0000 (0/75) | 0.6667 (50/75) | 1.0000 (50/50) | 0.0000 (0/25) | 0.0000 (0/50) |
| json_p500 | 75 | 0.7333 (55/75) | 0.7333 (55/75) | 0.3867 (29/75) | 0.3200 (16/50) | 0.5200 (13/25) | 0.0000 (0/50) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | aigc_editing | 75 | 0.6667 (50/75) | 1.0000 (50/50) | 0.0000 (0/25) | 0.0000 (0/50) |
| json_p500 | aigc_editing | 75 | 0.3867 (29/75) | 0.3200 (16/50) | 0.5200 (13/25) | 0.0000 (0/50) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | SD-inpaint | 75 | 0.6667 (50/75) | 1.0000 (50/50) | 0.0000 (0/25) | 0.0000 (0/50) |
| json_p500 | SD-inpaint | 75 | 0.3867 (29/75) | 0.3200 (16/50) | 0.5200 (13/25) | 0.0000 (0/50) |

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
