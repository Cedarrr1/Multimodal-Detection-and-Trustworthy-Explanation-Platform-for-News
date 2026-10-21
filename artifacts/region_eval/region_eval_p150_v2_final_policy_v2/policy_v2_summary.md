# region_eval_p150_v2_final_policy_v2 Region Policy v2

## Boundary

GT bbox prompt conditioned mask refinement; not automatic forged-region discovery.

## Thresholds

- thresholds: `{'t_ps': 0.34, 't_face': 1.0, 't_sam_score': 0.5, 'sam_area_bbox_ratio_min': 0.2, 'sam_area_bbox_ratio_max': 1.0}`
- threshold source: `loaded`

## Evaluation

| method | n | IoU | F1 | Precision | Recall | selected |
|---|---:|---:|---:|---:|---:|---|
| bbox_mask_baseline | 150 | 0.7264 [0.6878, 0.7634] | 0.8172 [0.7887, 0.8459] | 0.7264 [0.6862, 0.7596] | 1.0000 [1.0000, 1.0000] | `{'bbox_mask_baseline': 150}` |
| sam_best_of3 | 150 | 0.7831 [0.7519, 0.8132] | 0.8611 [0.8350, 0.8857] | 0.9153 [0.8893, 0.9383] | 0.8426 [0.8128, 0.8701] | `{'sam_refinement': 150}` |
| old_domain_aware_predicted | 150 | 0.8103 [0.7792, 0.8391] | 0.8798 [0.8563, 0.9021] | 0.8550 [0.8239, 0.8853] | 0.9381 [0.9144, 0.9561] | `{'bbox_mask_baseline': 80, 'sam_refinement': 70}` |
| oracle_domain_aware | 150 | 0.8464 [0.8168, 0.8726] | 0.9050 [0.8831, 0.9244] | 0.9140 [0.8895, 0.9362] | 0.9145 [0.8909, 0.9345] | `{'bbox_mask_baseline': 50, 'sam_refinement': 100}` |
| policy_v2 | 150 | 0.8394 [0.8114, 0.8674] | 0.9005 [0.8768, 0.9219] | 0.8946 [0.8663, 0.9185] | 0.9276 [0.9048, 0.9462] | `{'bbox_mask_baseline': 66, 'sam_refinement': 84}` |

## By Domain

| domain | method | n | IoU | F1 | selected |
|---|---|---:|---:|---:|---|
| aigc_editing | bbox_mask_baseline | 50 | 0.5922 [0.5371, 0.6409] | 0.7230 [0.6756, 0.7672] | `{'bbox_mask_baseline': 50}` |
| aigc_editing | sam_best_of3 | 50 | 0.7341 [0.6771, 0.7848] | 0.8283 [0.7760, 0.8732] | `{'sam_refinement': 50}` |
| aigc_editing | old_domain_aware_predicted | 50 | 0.7341 [0.6759, 0.7822] | 0.8283 [0.7790, 0.8735] | `{'sam_refinement': 50}` |
| aigc_editing | oracle_domain_aware | 50 | 0.7341 [0.6800, 0.7836] | 0.8283 [0.7805, 0.8732] | `{'sam_refinement': 50}` |
| aigc_editing | policy_v2 | 50 | 0.7341 [0.6742, 0.7848] | 0.8283 [0.7770, 0.8702] | `{'sam_refinement': 50}` |
| deepfake | bbox_mask_baseline | 50 | 0.9456 [0.9150, 0.9667] | 0.9688 [0.9473, 0.9827] | `{'bbox_mask_baseline': 50}` |
| deepfake | sam_best_of3 | 50 | 0.7558 [0.6905, 0.8113] | 0.8369 [0.7777, 0.8882] | `{'sam_refinement': 50}` |
| deepfake | old_domain_aware_predicted | 50 | 0.9456 [0.9174, 0.9665] | 0.9688 [0.9455, 0.9826] | `{'bbox_mask_baseline': 50}` |
| deepfake | oracle_domain_aware | 50 | 0.9456 [0.9140, 0.9663] | 0.9688 [0.9488, 0.9827] | `{'bbox_mask_baseline': 50}` |
| deepfake | policy_v2 | 50 | 0.9456 [0.9176, 0.9668] | 0.9688 [0.9474, 0.9828] | `{'bbox_mask_baseline': 50}` |
| photoshop | bbox_mask_baseline | 50 | 0.6415 [0.5836, 0.6962] | 0.7597 [0.7113, 0.8062] | `{'bbox_mask_baseline': 50}` |
| photoshop | sam_best_of3 | 50 | 0.8594 [0.8194, 0.8936] | 0.9180 [0.8909, 0.9406] | `{'sam_refinement': 50}` |
| photoshop | old_domain_aware_predicted | 50 | 0.7511 [0.6975, 0.8018] | 0.8421 [0.8030, 0.8822] | `{'bbox_mask_baseline': 30, 'sam_refinement': 20}` |
| photoshop | oracle_domain_aware | 50 | 0.8594 [0.8190, 0.8933] | 0.9180 [0.8904, 0.9429] | `{'sam_refinement': 50}` |
| photoshop | policy_v2 | 50 | 0.8386 [0.7972, 0.8736] | 0.9045 [0.8737, 0.9299] | `{'bbox_mask_baseline': 16, 'sam_refinement': 34}` |

## Gains

- policy_v2 IoU gain vs bbox: `0.1130`
- policy_v2 F1 gain vs bbox: `0.0833`

## Prediction Stats

- global domain accuracy: `0.7867`
- global domain counts: `{'aigc_inpaint': 50, 'deepfake': 48, 'none': 32, 'photoshop': 20}`
- mean patch score by domain: `{'aigc_editing': 0.48, 'deepfake': 0.0, 'photoshop': 0.68}`
- nonzero patch scores by domain: `{'aigc_editing': 24, 'deepfake': 0, 'photoshop': 34}`
