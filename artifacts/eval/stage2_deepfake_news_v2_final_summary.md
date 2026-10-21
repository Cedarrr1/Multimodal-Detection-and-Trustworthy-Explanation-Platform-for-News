# Stage2 DeepFake News Evaluation

- total: `400`
- valid JSON: `1.0000 (400/400)`
- valid schema: `1.0000 (400/400)`
- image verdict accuracy: `0.8600 (344/400)`
- DeepFake recall: `0.9300 (186/200)`
- FFHQ authentic accuracy: `0.7900 (158/200)`
- relation accuracy: `0.9750 (390/400)`
- relation balanced accuracy: `0.9750`
- final news verdict accuracy: `0.9250 (370/400)`
- exact core accuracy: `0.8350 (334/400)`
- FaceApp tampered IoU: `0.6134373784925128`
- FaceApp tampered pixel F1: `0.7312103755382064`
- FFHQ empty-mask accuracy: `0.7900 (158/200)`
- FFHQ FP-mask rate: `0.2100 (42/200)`

## Four-Cell Accuracy

| cell | final_accuracy | exact_core_accuracy | n |
|---|---:|---:|---:|
| `authentic_consistent` | 0.8200 | 0.8200 | 100 |
| `authentic_mismatched` | 0.9500 | 0.7100 | 100 |
| `tampered_consistent` | 0.9300 | 0.9300 | 100 |
| `tampered_mismatched` | 1.0000 | 0.8800 | 100 |

## Four-Cell Confusion

```json
{
  "authentic_consistent": {
    "authentic_consistent": 82,
    "tampered_consistent": 18
  },
  "authentic_mismatched": {
    "authentic_mismatched": 71,
    "tampered_mismatched": 24,
    "authentic_consistent": 5
  },
  "tampered_consistent": {
    "tampered_consistent": 93,
    "authentic_consistent": 7
  },
  "tampered_mismatched": {
    "tampered_mismatched": 88,
    "authentic_mismatched": 7,
    "tampered_consistent": 5
  }
}
```
