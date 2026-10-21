# Stage2 DeepFake News Evaluation

- total: `200`
- valid JSON: `1.0000 (200/200)`
- valid schema: `1.0000 (200/200)`
- image verdict accuracy: `0.8950 (179/200)`
- DeepFake recall: `0.9400 (94/100)`
- FFHQ authentic accuracy: `0.8500 (85/100)`
- relation accuracy: `0.9800 (196/200)`
- relation balanced accuracy: `0.9800`
- final news verdict accuracy: `0.9400 (188/200)`
- exact core accuracy: `0.8900 (178/200)`
- FaceApp tampered IoU: `0.6168941638701935`
- FaceApp tampered pixel F1: `0.7380063723996774`
- FFHQ empty-mask accuracy: `0.8500 (85/100)`
- FFHQ FP-mask rate: `0.1500 (15/100)`

## Four-Cell Accuracy

| cell | final_accuracy | exact_core_accuracy | n |
|---|---:|---:|---:|
| `authentic_consistent` | 0.8800 | 0.8800 | 50 |
| `authentic_mismatched` | 0.9800 | 0.8000 | 50 |
| `tampered_consistent` | 0.9400 | 0.9400 | 50 |
| `tampered_mismatched` | 0.9600 | 0.9400 | 50 |

## Four-Cell Confusion

```json
{
  "authentic_consistent": {
    "authentic_consistent": 44,
    "tampered_consistent": 6
  },
  "authentic_mismatched": {
    "authentic_mismatched": 40,
    "authentic_consistent": 1,
    "tampered_mismatched": 8,
    "tampered_consistent": 1
  },
  "tampered_consistent": {
    "authentic_consistent": 3,
    "tampered_consistent": 47
  },
  "tampered_mismatched": {
    "tampered_mismatched": 47,
    "authentic_consistent": 2,
    "authentic_mismatched": 1
  }
}
```
