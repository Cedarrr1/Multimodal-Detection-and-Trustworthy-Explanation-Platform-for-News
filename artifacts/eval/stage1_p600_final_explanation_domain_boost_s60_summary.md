# Stage1 Fair Image-Level Evaluation

## Protocol

- schema: `explanation`
- max_pixels: `524288`
- max_new_tokens: `420`
- decoding: `greedy`
- bootstrap samples: `1000`

## Overall

| model | n | valid_schema | verdict_acc | balanced_acc | tampered_recall | authentic_acc | domain_acc |
|---|---:|---:|---:|---:|---:|---:|---:|
| domain_boost | 60 | 1.0000 [1.0000, 1.0000] | 0.8167 [0.7167, 0.9167] | 0.8170 [0.7165, 0.9057] | 0.8065 [0.6429, 0.9333] | 0.8276 [0.6765, 0.9583] | 0.8065 [0.6562, 0.9355] |

## By Forgery Type

| model | group | n | verdict_acc | balanced_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|---:|
| domain_boost | aigc_editing | 27 | 0.9630 [0.8889, 1.0000] | 0.9615 [0.8750, 1.0000] | 1.0000 [1.0000, 1.0000] | 0.9231 [0.7692, 1.0000] | 1.0000 [1.0000, 1.0000] |
| domain_boost | deepfake | 17 | 0.7059 [0.4706, 0.8824] | 0.7348 [0.5139, 0.9231] | 0.8333 [0.5000, 1.0000] | 0.6364 [0.3333, 0.9091] | 0.8333 [0.5000, 1.0000] |
| domain_boost | photoshop | 16 | 0.6875 [0.4375, 0.8750] | 0.7727 [0.6250, 0.9333] | 0.5455 [0.2308, 0.8333] | 1.0000 [1.0000, 1.0000] | 0.5455 [0.2308, 0.8333] |

## By Source

| model | group | n | verdict_acc | balanced_acc | tampered_recall | authentic_acc | domain_acc |
|---|---|---:|---:|---:|---:|---:|---:|
| domain_boost | CASIA | 16 | 0.6875 [0.4375, 0.8750] | 0.7727 [0.6250, 0.9231] | 0.5455 [0.2500, 0.8333] | 1.0000 [1.0000, 1.0000] | 0.5455 [0.2500, 0.8333] |
| domain_boost | FFHQ | 11 | 0.6364 [0.3636, 0.9091] | n/a | n/a | 0.6364 [0.3636, 0.9091] | n/a |
| domain_boost | FaceApp | 6 | 0.8333 [0.5000, 1.0000] | n/a | 0.8333 [0.5000, 1.0000] | n/a | 0.8333 [0.5000, 1.0000] |
| domain_boost | SD-inpaint | 27 | 0.9630 [0.8889, 1.0000] | 0.9615 [0.8636, 1.0000] | 1.0000 [1.0000, 1.0000] | 0.9231 [0.7273, 1.0000] | 1.0000 [1.0000, 1.0000] |

## Dataset

- output_root: `artifacts/lora_data/stage1_multisource_eval_p600_final`
- total: `600`
- per_label: `100`
- seed: `20260711`
