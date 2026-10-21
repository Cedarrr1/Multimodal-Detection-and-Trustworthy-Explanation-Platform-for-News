# region_eval_p150_policy_v2_dev Region Policy v2

## Boundary

GT bbox prompt conditioned mask refinement; not automatic forged-region discovery.

## Thresholds

- thresholds: `{'t_ps': 0.34, 't_face': 1.0, 't_sam_score': 0.5, 'sam_area_bbox_ratio_min': 0.2, 'sam_area_bbox_ratio_max': 1.0}`
- threshold source: `tuned_on_dev`

## Evaluation

| method | n | IoU | F1 | Precision | Recall | selected |
|---|---:|---:|---:|---:|---:|---|
| bbox_mask_baseline | 150 | 0.7234 [0.6802, 0.7625] | 0.8099 [0.7786, 0.8422] | 0.7234 [0.6798, 0.7618] | 1.0000 [1.0000, 1.0000] | `{'bbox_mask_baseline': 150}` |
| sam_best_of3 | 150 | 0.6656 [0.6269, 0.7062] | 0.7690 [0.7351, 0.8021] | 0.9065 [0.8793, 0.9303] | 0.7258 [0.6807, 0.7643] | `{'sam_refinement': 150}` |
| old_domain_aware_predicted | 150 | 0.7584 [0.7211, 0.7954] | 0.8362 [0.8044, 0.8659] | 0.8491 [0.8148, 0.8811] | 0.8873 [0.8521, 0.9162] | `{'bbox_mask_baseline': 78, 'sam_refinement': 72}` |
| oracle_domain_aware | 150 | 0.7944 [0.7588, 0.8292] | 0.8645 [0.8367, 0.8902] | 0.9068 [0.8789, 0.9312] | 0.8633 [0.8325, 0.8923] | `{'bbox_mask_baseline': 50, 'sam_refinement': 100}` |
| policy_v2 | 150 | 0.7774 [0.7399, 0.8144] | 0.8514 [0.8214, 0.8793] | 0.8655 [0.8317, 0.8954] | 0.8914 [0.8598, 0.9194] | `{'bbox_mask_baseline': 71, 'sam_refinement': 79}` |

## By Domain

| domain | method | n | IoU | F1 | selected |
|---|---|---:|---:|---:|---|
| aigc_editing | bbox_mask_baseline | 50 | 0.5735 [0.5103, 0.6424] | 0.6991 [0.6419, 0.7519] | `{'bbox_mask_baseline': 50}` |
| aigc_editing | sam_best_of3 | 50 | 0.6521 [0.5926, 0.7183] | 0.7627 [0.7055, 0.8171] | `{'sam_refinement': 50}` |
| aigc_editing | old_domain_aware_predicted | 50 | 0.6521 [0.5887, 0.7093] | 0.7627 [0.7019, 0.8149] | `{'sam_refinement': 50}` |
| aigc_editing | oracle_domain_aware | 50 | 0.6521 [0.5856, 0.7106] | 0.7627 [0.7071, 0.8161] | `{'sam_refinement': 50}` |
| aigc_editing | policy_v2 | 50 | 0.6619 [0.5925, 0.7211] | 0.7709 [0.7141, 0.8201] | `{'bbox_mask_baseline': 4, 'sam_refinement': 46}` |
| deepfake | bbox_mask_baseline | 50 | 0.9532 [0.9403, 0.9656] | 0.9755 [0.9680, 0.9818] | `{'bbox_mask_baseline': 50}` |
| deepfake | sam_best_of3 | 50 | 0.5669 [0.4978, 0.6384] | 0.6890 [0.6290, 0.7471] | `{'sam_refinement': 50}` |
| deepfake | old_domain_aware_predicted | 50 | 0.9532 [0.9407, 0.9648] | 0.9755 [0.9683, 0.9820] | `{'bbox_mask_baseline': 50}` |
| deepfake | oracle_domain_aware | 50 | 0.9532 [0.9404, 0.9648] | 0.9755 [0.9685, 0.9817] | `{'bbox_mask_baseline': 50}` |
| deepfake | policy_v2 | 50 | 0.9532 [0.9398, 0.9652] | 0.9755 [0.9688, 0.9821] | `{'bbox_mask_baseline': 50}` |
| photoshop | bbox_mask_baseline | 50 | 0.6436 [0.5777, 0.7094] | 0.7551 [0.6959, 0.8081] | `{'bbox_mask_baseline': 50}` |
| photoshop | sam_best_of3 | 50 | 0.7778 [0.7198, 0.8332] | 0.8553 [0.8086, 0.8999] | `{'sam_refinement': 50}` |
| photoshop | old_domain_aware_predicted | 50 | 0.6700 [0.5941, 0.7336] | 0.7703 [0.7045, 0.8296] | `{'bbox_mask_baseline': 28, 'sam_refinement': 22}` |
| photoshop | oracle_domain_aware | 50 | 0.7778 [0.7177, 0.8312] | 0.8553 [0.8062, 0.8987] | `{'sam_refinement': 50}` |
| photoshop | policy_v2 | 50 | 0.7171 [0.6511, 0.7778] | 0.8077 [0.7529, 0.8636] | `{'bbox_mask_baseline': 17, 'sam_refinement': 33}` |

## Gains

- policy_v2 IoU gain vs bbox: `0.0540`
- policy_v2 F1 gain vs bbox: `0.0415`

## Prediction Stats

- global domain accuracy: `0.8067`
- global domain counts: `{'aigc_inpaint': 50, 'deepfake': 49, 'none': 29, 'photoshop': 22}`
- mean patch score by domain: `{'aigc_editing': 0.56, 'deepfake': 0.0, 'photoshop': 0.66}`
- nonzero patch scores by domain: `{'aigc_editing': 28, 'deepfake': 0, 'photoshop': 33}`
