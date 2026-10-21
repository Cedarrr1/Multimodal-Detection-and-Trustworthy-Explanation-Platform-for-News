# region_eval_p150_quality_gate Region Quality Gate

## Boundary

GT bbox prompt conditioned mask refinement; not automatic forged-region discovery.

## Split And Thresholds

- dev p60: `60`
- test p90: `90`
- Photoshop threshold: `0.50`
- AIGC threshold: `0.50`

## Test p90

| method | n | IoU | F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| bbox_mask_baseline | 90 | 0.7336 [0.6806, 0.7826] | 0.8170 [0.7752, 0.8565] | 0.7336 [0.6798, 0.7817] | 1.0000 [1.0000, 1.0000] |
| sam_best_of3 | 90 | 0.6587 [0.6051, 0.7105] | 0.7603 [0.7126, 0.8058] | 0.9190 [0.8837, 0.9486] | 0.7057 [0.6527, 0.7608] |
| domain_aware_predicted | 90 | 0.7488 [0.6923, 0.7990] | 0.8263 [0.7845, 0.8684] | 0.8534 [0.8091, 0.8961] | 0.8712 [0.8202, 0.9136] |
| domain_aware_predicted_gate | 90 | 0.7488 [0.6942, 0.7957] | 0.8263 [0.7796, 0.8667] | 0.8534 [0.8058, 0.8946] | 0.8712 [0.8234, 0.9167] |

## Test p90 By Domain

| domain | method | n | IoU | F1 |
|---|---|---:|---:|---:|
| aigc_editing | bbox_mask_baseline | 30 | 0.5937 [0.5006, 0.6890] | 0.7114 [0.6407, 0.7840] |
| aigc_editing | sam_best_of3 | 30 | 0.6011 [0.5017, 0.6820] | 0.7158 [0.6299, 0.7892] |
| aigc_editing | domain_aware_predicted | 30 | 0.6011 [0.5144, 0.6879] | 0.7158 [0.6270, 0.7956] |
| aigc_editing | domain_aware_predicted_gate | 30 | 0.6011 [0.5062, 0.6903] | 0.7158 [0.6280, 0.7918] |
| deepfake | bbox_mask_baseline | 30 | 0.9609 [0.9452, 0.9740] | 0.9796 [0.9717, 0.9873] |
| deepfake | sam_best_of3 | 30 | 0.5568 [0.4652, 0.6595] | 0.6781 [0.5956, 0.7577] |
| deepfake | domain_aware_predicted | 30 | 0.9609 [0.9446, 0.9739] | 0.9796 [0.9705, 0.9869] |
| deepfake | domain_aware_predicted_gate | 30 | 0.9609 [0.9452, 0.9748] | 0.9796 [0.9711, 0.9870] |
| photoshop | bbox_mask_baseline | 30 | 0.6461 [0.5726, 0.7206] | 0.7600 [0.6846, 0.8290] |
| photoshop | sam_best_of3 | 30 | 0.8181 [0.7506, 0.8763] | 0.8869 [0.8323, 0.9315] |
| photoshop | domain_aware_predicted | 30 | 0.6844 [0.5963, 0.7748] | 0.7836 [0.7101, 0.8513] |
| photoshop | domain_aware_predicted_gate | 30 | 0.6844 [0.5990, 0.7690] | 0.7836 [0.7139, 0.8477] |

## Gains

- gated IoU gain vs bbox: `0.0153`
- gated F1 gain vs bbox: `0.0093`

## Domain Predictions

- test p90 domain accuracy: `0.8111`
- predicted domain counts: `{'aigc_inpaint': 30, 'deepfake': 30, 'none': 17, 'photoshop': 13}`
