# End-to-End Fake-News MVP

The fast-forward MVP freezes `artifacts/lora_runs/qwen2_5_vl_stage1_p500_json`
as the Stage1 image-forensics baseline and focuses on the full project loop:

```text
news text + image -> claim parsing -> image forensics -> consistency judgment -> structured report
```

Run the dependency-light path:

```bash
python -m fake_news_forensics.pipeline.cli \
  --input examples/sample_news.json \
  --output artifacts/reports/sample_news_report.json
```

Module behavior:

- Module1 extracts `text_claims`, a placeholder caption, scene hints, and region proposals.
- Module2 records the frozen `json_p500` adapter and returns image forensics. The default
  `mock` backend first reuses cached `json_p500` predictions for known eval/demo
  images, then falls back to rules if no cache entry exists.
- Module3 aggregates Module1/2 into `final_verdict`, `fake_type`,
  `claim_analysis`, `final_reasoning`, and `report`.

To run the real frozen LoRA backend when the model stack and GPU are available:

```bash
python -m fake_news_forensics.pipeline.cli \
  --input examples/sample_news.json \
  --output artifacts/reports/sample_news_report.json \
  --forensics-backend qwen-lora \
  --max-new-tokens 420
```
