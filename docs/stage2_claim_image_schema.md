# Stage2 Claim-Image Fusion Schema

Stage2 moves from image-only forensics to fake-news forensics. The model input
should contain the news claim and the image. Optional upstream visual-forensics
signals can be included when available, but the target remains one JSON object.

## Input Contract

Recommended user prompt shape:

```text
<image>
Claim: {claim}

Analyze whether the image supports the claim and whether the image itself shows
forensic signs of manipulation. Return only valid JSON matching the requested
schema.
```

Optional fields for data construction:

- `claim`: news text or concise claim
- `image`: news image path
- `source`: dataset/source identifier
- `visual_forensics_hint`: Stage1 output or human label, used only when the task
  explicitly trains evidence integration
- `claim_image_label`: relation label such as `supports`, `contradicts`,
  `unrelated`, or `insufficient`

Do not leak the final news verdict in the user prompt.

## Target JSON

```json
{
  "claim": "...",
  "verdict": "authentic|tampered|misleading|unknown",
  "visual_forensics": {
    "image_verdict": "authentic|tampered|unknown",
    "tampered_region": "...",
    "tamper_domain": "photoshop|deepfake|aigc_inpaint|none|unknown",
    "evidence": ["..."]
  },
  "claim_image_consistency": "supports|contradicts|unrelated|insufficient",
  "final_reason": "..."
}
```

## Label Semantics

- `authentic`: image is not forensically tampered and supports the claim.
- `tampered`: image-level manipulation is central to the false or unreliable
  news item.
- `misleading`: image may be authentic, but it does not support the claim, is
  out of context, or is paired with a false/misleading claim.
- `unknown`: evidence is insufficient or contradictory.

Keep image manipulation and claim-image consistency separate. A real image can
still be misleading, and a manipulated image can be unrelated to the claim.

## Evaluation Plan

Stage2 evaluation should report at least:

- final verdict accuracy
- image-level verdict accuracy
- tampered recall for visually manipulated samples
- consistency-label accuracy
- valid JSON rate
- Photoshop subset recall, to track whether Stage1 local-manipulation weakness
  propagates into final fake-news decisions

When using Stage1 outputs as hints, evaluate both with and without the hints so
the project can distinguish visual-forensics ability from fusion ability.

For the fast-forward end-to-end MVP, freeze
`artifacts/lora_runs/qwen2_5_vl_stage1_p500_json` as the default visual
forensics module. Keep `artifacts/lora_runs/qwen2_5_vl_stage1_photoshop_crop_json`
as an optional later enhancement or ablation, but do not let Photoshop subdomain
tuning block the claim-image reporting loop.

## Conversion Entry

Raw Stage2 JSONL can be converted to LLaMA-Factory ShareGPT format with:

```bash
python tools/convert_stage2_claim_image_to_qwen_vl.py \
  --input artifacts/stage2/claim_image_raw.jsonl \
  --image-root dataset \
  --output-root artifacts/lora_data/stage2_claim_image_json
```

If the experiment intentionally trains the model to integrate an upstream
Stage1 visual-forensics module, add `--include-visual-hint`. Otherwise leave the
hint out of the prompt and keep the task end-to-end from claim plus image.

## Bootstrap Data

The current repository does not yet contain a real news claim-image dataset.
`dataset/MMTD-Set-34k/MMTD-Set-34k.json` only provides image-forensics
conversations with `id`, `image`, and `conversations`.

To validate the Stage2 data and training path before real news data is added,
build a clearly marked bootstrap dataset from Stage1 labels:

```bash
python tools/build_stage2_claim_image_bootstrap.py \
  --source-root artifacts/lora_data/stage1_mmtd_p500_json \
  --output artifacts/stage2/claim_image_bootstrap_raw.jsonl \
  --per-domain-label 20

python tools/convert_stage2_claim_image_to_qwen_vl.py \
  --input artifacts/stage2/claim_image_bootstrap_raw.jsonl \
  --image-root . \
  --output-root artifacts/lora_data/stage2_claim_image_bootstrap_json
```

The bootstrap claim is intentionally narrow:

```text
The image is an authentic, unmanipulated photograph.
```

Authentic images support the claim; tampered images contradict it. This checks
the Stage2 JSON schema, conversion code, and LoRA training wiring, but it is not
a substitute for real fake-news claim-image supervision.

Bootstrap training config:

```text
configs/llamafactory/qwen2_5_vl_lora_stage2_claim_image_bootstrap_json.yaml
```
