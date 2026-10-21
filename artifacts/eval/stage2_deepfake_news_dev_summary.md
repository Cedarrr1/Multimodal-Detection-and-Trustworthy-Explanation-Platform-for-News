# Stage2 DeepFake News Evaluation

- total: `200`
- valid JSON: `1.0000 (200/200)`
- valid schema: `1.0000 (200/200)`
- image verdict accuracy: `0.9100 (182/200)`
- DeepFake recall: `0.9000 (90/100)`
- FFHQ authentic accuracy: `0.9200 (92/100)`
- relation accuracy: `0.9050 (181/200)`
- relation balanced accuracy: `0.9050`
- final news verdict accuracy: `0.9100 (182/200)`
- exact core accuracy: `0.8150 (163/200)`
- FaceApp tampered IoU: `0.5929880518090591`
- FaceApp tampered pixel F1: `0.7071015326406861`
- FFHQ empty-mask accuracy: `0.9200 (92/100)`
- FFHQ FP-mask rate: `0.0800 (8/100)`

## Four-Cell Accuracy

| cell | final_accuracy | exact_core_accuracy | n |
|---|---:|---:|---:|
| `authentic_consistent` | 0.9600 | 0.9600 | 50 |
| `authentic_mismatched` | 0.8000 | 0.6800 | 50 |
| `tampered_consistent` | 0.8800 | 0.8800 | 50 |
| `tampered_mismatched` | 1.0000 | 0.7400 | 50 |

## Four-Cell Confusion

```json
{
  "authentic_consistent": {
    "authentic_consistent": 48,
    "tampered_consistent": 2
  },
  "authentic_mismatched": {
    "authentic_mismatched": 34,
    "authentic_consistent": 10,
    "tampered_mismatched": 6
  },
  "tampered_consistent": {
    "tampered_consistent": 44,
    "authentic_consistent": 6
  },
  "tampered_mismatched": {
    "tampered_consistent": 9,
    "tampered_mismatched": 37,
    "authentic_mismatched": 4
  }
}
```
