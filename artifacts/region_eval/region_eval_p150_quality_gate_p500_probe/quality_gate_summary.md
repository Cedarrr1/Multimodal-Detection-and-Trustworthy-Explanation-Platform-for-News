# region_eval_p150_quality_gate_p500_probe Region Quality Gate

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
| bbox_mask_baseline | 90 | 0.7336 [0.6802, 0.7853] | 0.8170 [0.7793, 0.8526] | 0.7336 [0.6780, 0.7817] | 1.0000 [1.0000, 1.0000] |
| sam_best_of3 | 90 | 0.6587 [0.6036, 0.7089] | 0.7603 [0.7144, 0.8000] | 0.9190 [0.8874, 0.9505] | 0.7057 [0.6480, 0.7633] |
| domain_aware_predicted | 90 | 0.7501 [0.6878, 0.7987] | 0.8287 [0.7812, 0.8690] | 0.7652 [0.7129, 0.8154] | 0.9839 [0.9614, 0.9967] |
| domain_aware_predicted_gate | 90 | 0.7501 [0.6885, 0.7964] | 0.8293 [0.7879, 0.8644] | 0.7545 [0.7013, 0.7981] | 0.9956 [0.9899, 0.9996] |

## Test p90 By Domain

| domain | method | n | IoU | F1 |
|---|---|---:|---:|---:|
| aigc_editing | bbox_mask_baseline | 30 | 0.5937 [0.5004, 0.6768] | 0.7114 [0.6409, 0.7840] |
| aigc_editing | sam_best_of3 | 30 | 0.6011 [0.5050, 0.6856] | 0.7158 [0.6213, 0.7816] |
| aigc_editing | domain_aware_predicted | 30 | 0.5936 [0.5002, 0.6918] | 0.7096 [0.6338, 0.7846] |
| aigc_editing | domain_aware_predicted_gate | 30 | 0.5937 [0.4834, 0.6734] | 0.7114 [0.6373, 0.7869] |
| deepfake | bbox_mask_baseline | 30 | 0.9609 [0.9481, 0.9750] | 0.9796 [0.9701, 0.9859] |
| deepfake | sam_best_of3 | 30 | 0.5568 [0.4636, 0.6542] | 0.6781 [0.5967, 0.7532] |
| deepfake | domain_aware_predicted | 30 | 0.9609 [0.9446, 0.9739] | 0.9796 [0.9713, 0.9862] |
| deepfake | domain_aware_predicted_gate | 30 | 0.9609 [0.9444, 0.9755] | 0.9796 [0.9708, 0.9872] |
| photoshop | bbox_mask_baseline | 30 | 0.6461 [0.5633, 0.7158] | 0.7600 [0.6747, 0.8273] |
| photoshop | sam_best_of3 | 30 | 0.8181 [0.7510, 0.8701] | 0.8869 [0.8292, 0.9346] |
| photoshop | domain_aware_predicted | 30 | 0.6957 [0.6125, 0.7678] | 0.7970 [0.7344, 0.8591] |
| photoshop | domain_aware_predicted_gate | 30 | 0.6957 [0.6120, 0.7805] | 0.7970 [0.7199, 0.8600] |

## Gains

- gated IoU gain vs bbox: `0.0166`
- gated F1 gain vs bbox: `0.0123`

## Domain Predictions

- test p90 domain accuracy: `0.3778`
- predicted domain counts: `{'deepfake': 30, 'none': 40, 'photoshop': 7, 'unknown': 13}`
