# Stage2 DeepFake News Evaluation

- total: `400`
- valid JSON: `1.0000 (400/400)`
- valid schema: `0.9975 (399/400)`
- image verdict accuracy: `0.8700 (348/400)`
- DeepFake recall: `0.8500 (170/200)`
- FFHQ authentic accuracy: `0.8900 (178/200)`
- relation accuracy: `0.7550 (302/400)`
- relation balanced accuracy: `0.7550`
- final news verdict accuracy: `0.8025 (321/400)`
- exact core accuracy: `0.6500 (260/400)`
- FaceApp tampered IoU: `0.5627240268821516`
- FaceApp tampered pixel F1: `0.6717674426391157`
- FFHQ empty-mask accuracy: `0.8950 (179/200)`
- FFHQ FP-mask rate: `0.1050 (21/200)`

## Four-Cell Accuracy

| cell | final_accuracy | exact_core_accuracy | n |
|---|---:|---:|---:|
| `authentic_consistent` | 0.8900 | 0.8900 | 100 |
| `authentic_mismatched` | 0.5300 | 0.4200 | 100 |
| `tampered_consistent` | 0.8500 | 0.8500 | 100 |
| `tampered_mismatched` | 0.9400 | 0.4400 | 100 |

## Four-Cell Confusion

```json
{
  "authentic_consistent": {
    "authentic_consistent": 89,
    "tampered_consistent": 11
  },
  "authentic_mismatched": {
    "authentic_consistent": 47,
    "authentic_mismatched": 42,
    "tampered_mismatched": 7,
    "tampered_consistent": 4
  },
  "tampered_consistent": {
    "authentic_consistent": 15,
    "tampered_consistent": 85
  },
  "tampered_mismatched": {
    "authentic_consistent": 6,
    "tampered_mismatched": 44,
    "tampered_consistent": 41,
    "authentic_mismatched": 9
  }
}
```
