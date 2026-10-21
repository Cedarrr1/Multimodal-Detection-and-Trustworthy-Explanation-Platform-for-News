# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 150 | 0.7000 (105/150) | 0.0533 (8/150) | 0.6667 (100/150) | 1.0000 (100/100) | 0.0000 (0/50) | 0.0700 (7/100) |
| json_p500 | 150 | 0.8933 (134/150) | 0.8933 (134/150) | 0.8133 (122/150) | 0.9400 (94/100) | 0.5600 (28/50) | 0.9400 (94/100) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | aigc_editing | 50 | 0.0000 (0/50) | n/a (0/0) | 0.0000 (0/50) | n/a (0/0) |
| json_p500 | aigc_editing | 50 | 0.5600 (28/50) | n/a (0/0) | 0.5600 (28/50) | n/a (0/0) |
| base | deepfake | 100 | 1.0000 (100/100) | 1.0000 (100/100) | n/a (0/0) | 0.0700 (7/100) |
| json_p500 | deepfake | 100 | 0.9400 (94/100) | 0.9400 (94/100) | n/a (0/0) | 0.9400 (94/100) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | FaceApp | 100 | 1.0000 (100/100) | 1.0000 (100/100) | n/a (0/0) | 0.0700 (7/100) |
| json_p500 | FaceApp | 100 | 0.9400 (94/100) | 0.9400 (94/100) | n/a (0/0) | 0.9400 (94/100) |
| base | SD-inpaint | 50 | 0.0000 (0/50) | n/a (0/0) | 0.0000 (0/50) | n/a (0/0) |
| json_p500 | SD-inpaint | 50 | 0.5600 (28/50) | n/a (0/0) | 0.5600 (28/50) | n/a (0/0) |

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
| 300 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00752-2.png` |
| 301 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01640-1.png` |
| 302 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00271-3.png` |
| 303 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01346-1.png` |
| 304 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00372-2.png` |
| 305 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00404-3.png` |
| 306 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01100-3.png` |
| 307 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01204-2.png` |
| 308 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00502-2.png` |
| 309 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00000-3.png` |
| 310 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00617-2.png` |
| 311 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01115-1.png` |
| 312 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01923-2.png` |
| 313 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00746-2.png` |
| 314 | FaceApp | deepfake | tampered / deepfake | tampered / headwear / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01816-1.png` |
| 315 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00038-2.png` |
| 316 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01446-1.png` |
| 317 | FaceApp | deepfake | tampered / deepfake | tampered / facial features / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00448-3.png` |
| 318 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01921-1.png` |
| 319 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01361-3.png` |
| 320 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01450-3.png` |
| 321 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00719-1.png` |
| 322 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00512-3.png` |
| 323 | FaceApp | deepfake | tampered / deepfake | tampered / digital / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00384-1.png` |
| 324 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_02136-2.png` |
| 325 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00981-2.png` |
| 326 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00407-1.png` |
| 327 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01026-2.png` |
| 328 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01663-1.png` |
| 329 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00800-1.png` |
| 330 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01682-1.png` |
| 331 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01306-3.png` |
| 332 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00903-1.png` |
| 333 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00817-3.png` |
| 334 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00839-3.png` |
| 335 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01276-2.png` |
| 336 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00877-3.png` |
| 337 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00167-2.png` |
| 338 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_02195-1.png` |
| 339 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00666-1.png` |
| 340 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00381-3.png` |
| 341 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00464-2.png` |
| 342 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_02163-1.png` |
| 343 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_02156-1.png` |
| 344 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01376-1.png` |
| 345 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01558-1.png` |
| 346 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01627-2.png` |
| 347 | FaceApp | deepfake | tampered / deepfake | tampered / digital / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00116-1.png` |
| 348 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01861-1.png` |
| 349 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00579-1.png` |
| 350 | FaceApp | deepfake | tampered / deepfake | tampered / headwear / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_02101-1.png` |
| 351 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01438-1.png` |
| 352 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00727-1.png` |
| 353 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01343-1.png` |
| 354 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01648-2.png` |
| 355 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_02062-1.png` |
| 356 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00586-3.png` |
| 357 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00901-3.png` |
| 358 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01776-1.png` |
| 359 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01059-2.png` |
| 360 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00343-1.png` |
| 361 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01485-3.png` |
| 362 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01732-1.png` |
| 363 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_02191-1.png` |
| 364 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00230-2.png` |
| 365 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01058-3.png` |
| 366 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01957-1.png` |
| 367 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01300-3.png` |
| 368 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00575-2.png` |
| 369 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_02342-1.png` |
| 370 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00983-3.png` |
| 371 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01719-2.png` |
| 372 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01922-2.png` |
| 373 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00990-1.png` |
| 374 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01439-2.png` |
| 375 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01008-3.png` |
| 376 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01692-1.png` |
| 377 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00751-3.png` |
| 378 | FaceApp | deepfake | tampered / deepfake | tampered / clothing / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00439-2.png` |
| 379 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00431-2.png` |
| 380 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00387-3.png` |
| 381 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_02188-1.png` |
| 382 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01893-1.png` |
| 383 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00257-1.png` |
| 384 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01275-2.png` |
| 385 | FaceApp | deepfake | tampered / deepfake | tampered / deepfake / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00700-2.png` |
| 386 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01774-1.png` |
| 387 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_00931-1.png` |
| 388 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01885-1.png` |
| 389 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00355-3.png` |
| 390 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_02163-2.png` |
| 391 | FaceApp | deepfake | tampered / deepfake | tampered / background / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00344-1.png` |
| 392 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01522-1.png` |
| 393 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01586-2.png` |
| 394 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01522-2.png` |
| 395 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00856-3.png` |
| 396 | FaceApp | deepfake | tampered / deepfake | tampered / photoshop / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00388-2.png` |
| 397 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_00803-2.png` |
| 398 | FaceApp | deepfake | tampered / deepfake | tampered / unknown / non-json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP1_01053-3.png` |
| 399 | FaceApp | deepfake | tampered / deepfake | tampered / digital manipulation / json | tampered / deepfake / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/deepfake/FaceApp/tampered/F_FAP0_01814-1.png` |
| 400 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000212591.jpg` |
| 401 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000323399.jpg` |
| 402 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation of the bus's license plate. / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000377226.jpg` |
| 403 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000552510.jpg` |
| 404 | SD-inpaint | aigc_editing | authentic / none | tampered / lighting / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000424554.jpg` |
| 405 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000195332.jpg` |
| 406 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000144322.jpg` |
| 407 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000565625.jpg` |
| 408 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000490695.jpg` |
| 409 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000106010.jpg` |
| 410 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000153262.jpg` |
| 411 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000554232.jpg` |
| 412 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000124931.jpg` |
| 413 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000337446.jpg` |
| 414 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000473575.jpg` |
| 415 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000452457.jpg` |
| 416 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000092217.jpg` |
| 417 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000069523.jpg` |
| 418 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000038030.jpg` |
| 419 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000471654.jpg` |
| 420 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000261414.jpg` |
| 421 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000400966.jpg` |
| 422 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000238051.jpg` |
| 423 | SD-inpaint | aigc_editing | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000107729.jpg` |
| 424 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000014756.jpg` |
| 425 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000278646.jpg` |
| 426 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000375021.jpg` |
| 427 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000433705.jpg` |
| 428 | SD-inpaint | aigc_editing | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000296797.jpg` |
| 429 | SD-inpaint | aigc_editing | authentic / none | tampered / photoshop / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000366788.jpg` |
| 430 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000152162.jpg` |
| 431 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000463800.jpg` |
| 432 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000050980.jpg` |
| 433 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000431133.jpg` |
| 434 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000223497.jpg` |
| 435 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000255155.jpg` |
| 436 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000022759.jpg` |
| 437 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000203160.jpg` |
| 438 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000008379.jpg` |
| 439 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation of the horse's hooves / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000147735.jpg` |
| 440 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000012896.jpg` |
| 441 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000150538.jpg` |
| 442 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000543407.jpg` |
| 443 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000127555.jpg` |
| 444 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000043872.jpg` |
| 445 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000143756.jpg` |
| 446 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000028823.jpg` |
| 447 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000435951.jpg` |
| 448 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000101431.jpg` |
| 449 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000054336.jpg` |
