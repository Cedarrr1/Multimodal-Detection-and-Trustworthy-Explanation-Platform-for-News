# Qwen2.5-VL LoRA Dry-Run Plan

We are no longer using FakeShield DTE-FDM weights or the LLaVA training script.
The new baseline is `Qwen/Qwen2.5-VL-3B-Instruct` with LoRA/SFT on converted
Stage1 MMTD data.

## Current Blocker

GPU visibility must be checked outside the sandbox:

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count(), torch.__version__)"
```

Expected before training:

- `nvidia-smi` lists at least one GPU.
- `torch.cuda.is_available()` is `True`.
- `torch.cuda.device_count()` is at least `1`.

Current LLaMA-Factory blocker:

- `llamafactory==0.9.3` is installed and `llamafactory-cli` exists.
- The current environment has `transformers==4.57.6` and `trl==0.29.1`.
- LLaMA-Factory 0.9.3 requires `transformers>=4.45.0,<=4.52.4` with excluded
  versions, and `trl>=0.8.6,<=0.9.6`.
- `llamafactory-cli train` currently fails before model loading with:
  `ImportError: cannot import name 'AutoModelForCausalLMWithValueHead' from 'trl'`.

Recommended fix before running the dry-run:

```bash
pip install "transformers>=4.45.0,<=4.52.4,!=4.46.0,!=4.46.1,!=4.46.2,!=4.46.3,!=4.47.0,!=4.47.1,!=4.48.0,!=4.52.0" "trl>=0.8.6,<=0.9.6"
```

## Data

Converted demo data:

```text
artifacts/lora_data/stage1_mmtd_demo/qwen_vl_sft.jsonl
```

LLaMA-Factory-compatible demo data:

```text
artifacts/lora_data/stage1_mmtd_demo/llamafactory_qwen_vl_sft.jsonl
```

Each record contains absolute image paths and Qwen2.5-VL-style `messages`:

- `images`: list with one absolute image path.
- `messages[0]`: user turn with image content and text content.
- `messages[1]`: assistant turn with text content.

## Preferred: LLaMA-Factory

Install only after confirming the target Python/CUDA environment:

```bash
python -V
python -c "import torch, transformers; print(torch.__version__, torch.version.cuda, transformers.__version__)"
```

Example command template:

```bash
llamafactory-cli train configs/llamafactory/qwen2_5_vl_lora_stage1_demo.yaml
```

The local dataset registry is:

```text
configs/llamafactory/dataset_info.json
```

Keep the first run at `max_samples=12`.

## Alternative: ms-swift

Use this if LLaMA-Factory version compatibility is poor:

```bash
swift sft \
  --model Qwen/Qwen2.5-VL-3B-Instruct \
  --train_type lora \
  --dataset artifacts/lora_data/stage1_mmtd_demo/qwen_vl_sft.jsonl \
  --torch_dtype bfloat16 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 1 \
  --learning_rate 1e-4 \
  --lora_rank 8 \
  --lora_alpha 16 \
  --max_length 4096 \
  --save_strategy epoch \
  --logging_steps 1 \
  --output_dir artifacts/lora_runs/qwen2_5_vl_3b_stage1_demo_swift_lora
```

Check the installed `swift sft --help` output before running because dataset
schema flags vary between versions.

## Dry-Run Success Criteria

- `Qwen/Qwen2.5-VL-3B-Instruct` loads.
- All images in `qwen_vl_sft.jsonl` are readable.
- One GPU is used.
- Forward/backward completes for the 12 demo samples.
- LoRA adapter files are saved in the output directory.
