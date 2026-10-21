# Stage1 Multisource Image-Level Evaluation

## Overall

| model | n | valid_json | valid_schema | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| base | 150 | 0.4400 (66/150) | 0.0000 (0/150) | 0.6600 (99/150) | 0.9900 (99/100) | 0.0000 (0/50) | 0.0000 (0/100) |
| json_p500 | 150 | 0.7467 (112/150) | 0.7467 (112/150) | 0.3933 (59/150) | 0.3800 (38/100) | 0.4200 (21/50) | 0.0100 (1/100) |

## By Forgery Type

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | aigc_editing | 150 | 0.6600 (99/150) | 0.9900 (99/100) | 0.0000 (0/50) | 0.0000 (0/100) |
| json_p500 | aigc_editing | 150 | 0.3933 (59/150) | 0.3800 (38/100) | 0.4200 (21/50) | 0.0100 (1/100) |

## By Source

| model | group | n | verdict_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|
| base | SD-inpaint | 150 | 0.6600 (99/150) | 0.9900 (99/100) | 0.0000 (0/50) | 0.0000 (0/100) |
| json_p500 | SD-inpaint | 150 | 0.3933 (59/150) | 0.3800 (38/100) | 0.4200 (21/50) | 0.0100 (1/100) |

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
| 450 | SD-inpaint | aigc_editing | authentic / none | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000374342.jpg` |
| 451 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000563155.jpg` |
| 452 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000033958.jpg` |
| 453 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000320020.jpg` |
| 454 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000334380.jpg` |
| 455 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000574760.jpg` |
| 456 | SD-inpaint | aigc_editing | authentic / none | tampered / sky / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000503091.jpg` |
| 457 | SD-inpaint | aigc_editing | authentic / none | tampered / signage / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000478511.jpg` |
| 458 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000176649.jpg` |
| 459 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000385514.jpg` |
| 460 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000145629.jpg` |
| 461 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000232254.jpg` |
| 462 | SD-inpaint | aigc_editing | authentic / none | tampered / sky / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000189182.jpg` |
| 463 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000470972.jpg` |
| 464 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000516868.jpg` |
| 465 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000471358.jpg` |
| 466 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000327813.jpg` |
| 467 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000162768.jpg` |
| 468 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000469467.jpg` |
| 469 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000563987.jpg` |
| 470 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000463424.jpg` |
| 471 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000006920.jpg` |
| 472 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000265327.jpg` |
| 473 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000093883.jpg` |
| 474 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000115637.jpg` |
| 475 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000346437.jpg` |
| 476 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000365999.jpg` |
| 477 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000158179.jpg` |
| 478 | SD-inpaint | aigc_editing | authentic / none | tampered / background / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000453682.jpg` |
| 479 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000038801.jpg` |
| 480 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000230381.jpg` |
| 481 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000227621.jpg` |
| 482 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000045299.jpg` |
| 483 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000299498.jpg` |
| 484 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000056306.jpg` |
| 485 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000483451.jpg` |
| 486 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000501502.jpg` |
| 487 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000100303.jpg` |
| 488 | SD-inpaint | aigc_editing | authentic / none | tampered / food / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000054517.jpg` |
| 489 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000374984.jpg` |
| 490 | SD-inpaint | aigc_editing | authentic / none | tampered / logo design / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000100642.jpg` |
| 491 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000005832.jpg` |
| 492 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000369514.jpg` |
| 493 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000045270.jpg` |
| 494 | SD-inpaint | aigc_editing | authentic / none | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000512292.jpg` |
| 495 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000027050.jpg` |
| 496 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000166320.jpg` |
| 497 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000349469.jpg` |
| 498 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000203304.jpg` |
| 499 | SD-inpaint | aigc_editing | authentic / none | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/authentic/000000174228.jpg` |
| 500 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4355.jpg` |
| 501 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/10416.jpg` |
| 502 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2768.jpg` |
| 503 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/16138.jpg` |
| 504 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4048.jpg` |
| 505 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/6640.jpg` |
| 506 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0311.jpg` |
| 507 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13130.jpg` |
| 508 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0390.jpg` |
| 509 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/19506.jpg` |
| 510 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13292.jpg` |
| 511 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/10479.jpg` |
| 512 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9378.jpg` |
| 513 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0671.jpg` |
| 514 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13810.jpg` |
| 515 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/1227.jpg` |
| 516 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / background / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18700.jpg` |
| 517 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/3050.jpg` |
| 518 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / entire image / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4519.jpg` |
| 519 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/19995.jpg` |
| 520 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / color correction / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/7053.jpg` |
| 521 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/11005.jpg` |
| 522 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18662.jpg` |
| 523 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/8573.jpg` |
| 524 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/15990.jpg` |
| 525 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0442.jpg` |
| 526 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/1671.jpg` |
| 527 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/16855.jpg` |
| 528 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2420.jpg` |
| 529 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4944.jpg` |
| 530 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/15810.jpg` |
| 531 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0617.jpg` |
| 532 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0825.jpg` |
| 533 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9160.jpg` |
| 534 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/14721.jpg` |
| 535 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18581.jpg` |
| 536 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/17173.jpg` |
| 537 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/3068.jpg` |
| 538 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/6227.jpg` |
| 539 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/16119.jpg` |
| 540 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / object / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/14566.jpg` |
| 541 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/1056.jpg` |
| 542 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18892.jpg` |
| 543 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/12703.jpg` |
| 544 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / background / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/7058.jpg` |
| 545 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | authentic / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18822.jpg` |
| 546 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/3244.jpg` |
| 547 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/16661.jpg` |
| 548 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4791.jpg` |
| 549 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13087.jpg` |
| 550 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / clothing / json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/17067.jpg` |
| 551 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2935.jpg` |
| 552 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9730.jpg` |
| 553 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/11139.jpg` |
| 554 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9699.jpg` |
| 555 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / food / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/14312.jpg` |
| 556 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/8880.jpg` |
| 557 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13275.jpg` |
| 558 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / aigc_inpaint / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/8758.jpg` |
| 559 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/17145.jpg` |
| 560 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2680.jpg` |
| 561 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13742.jpg` |
| 562 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/8709.jpg` |
| 563 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/16863.jpg` |
| 564 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/10834.jpg` |
| 565 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13595.jpg` |
| 566 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/7898.jpg` |
| 567 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/15385.jpg` |
| 568 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0555.jpg` |
| 569 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/15121.jpg` |
| 570 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/17276.jpg` |
| 571 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2528.jpg` |
| 572 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4877.jpg` |
| 573 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9632.jpg` |
| 574 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9168.jpg` |
| 575 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9670.jpg` |
| 576 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/8825.jpg` |
| 577 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/1578.jpg` |
| 578 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/15456.jpg` |
| 579 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/7464.jpg` |
| 580 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18583.jpg` |
| 581 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9991.jpg` |
| 582 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2524.jpg` |
| 583 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/15691.jpg` |
| 584 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / digital manipulation / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/10903.jpg` |
| 585 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/1773.jpg` |
| 586 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4262.jpg` |
| 587 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / license plate / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/0206.jpg` |
| 588 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/2615.jpg` |
| 589 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/1011.jpg` |
| 590 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/3265.jpg` |
| 591 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/4441.jpg` |
| 592 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18254.jpg` |
| 593 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9830.jpg` |
| 594 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / background / json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/13496.jpg` |
| 595 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/17438.jpg` |
| 596 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / photoshop / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/9488.jpg` |
| 597 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/18769.jpg` |
| 598 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | authentic / none / json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/10220.jpg` |
| 599 | SD-inpaint | aigc_editing | tampered / aigc_inpaint | tampered / unknown / non-json | tampered / unknown / non-json | `artifacts/lora_data/stage1_multisource_eval_p600/images/aigc_editing/SD-inpaint/tampered/3026.jpg` |
