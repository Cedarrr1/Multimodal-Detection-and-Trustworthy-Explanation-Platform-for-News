# 伪造新闻检测项目快速推进计划

## 当前推进原则

当前项目目标不是把某一个子模块性能打满，而是尽快形成一个可展示、可复现、可解释的端到端伪造新闻检测系统。

阶段性原则：

- 能用且相对 baseline 有提升，就进入下一阶段。
- 不再把 Photoshop 局部篡改性能优化作为主线阻塞项。
- 已跑通的 `json_p500` LoRA 作为 Stage1 图像级取证 baseline 固化。
- Stage2/Stage3 优先打通新闻 claim、图像取证、最终报告的闭环。
- SAM、region proposal、GPT 综合推理可以先用可替换实现或轻量规则版本，后续再逐步替换。

## 已完成基础

### Stage1：图像级取证 LoRA

当前可用模型：

```text
Qwen/Qwen2.5-VL-3B-Instruct + LoRA
artifacts/lora_runs/qwen2_5_vl_stage1_p500_json
```

训练数据：

```text
artifacts/lora_data/stage1_mmtd_p500_json
```

固定训练外验证集：

```text
artifacts/lora_data/stage1_mmtd_eval_p30_json
```

关键评估结果：

```text
valid_json:      30/30
verdict_acc:     22/30
tampered_recall: 11/15
authentic_acc:   11/15
domain_acc:      11/15
```

结论：

- Stage1 已达可用门槛。
- `json_p500` 比 `json_p100` 有稳定提升。
- Photoshop 子域仍弱，但不再作为当前主线阻塞项。

## 三层 LoRA 数据路线

### 第一层：DTE-style 图像级 SFT

状态：已完成。

用途：

- 训练图像级真假判断。
- 训练伪造领域标签：Photoshop、DeepFake、AIGC editing。
- 训练结构化 JSON 输出。
- 作为后续 region/claim 数据的基础取证模型。

当前采用：

```text
stage1_mmtd_p500_json
```

### 第二层：Region Forensics SFT

目标：让模型不只判断整图，还能围绕候选区域做判断。

快速推进版不追求真实 mask 完整训练，先构造可用 region 样本：

- global sample：整图输入。
- positive region：从 MMTD assistant 文本抽取疑似区域描述，配合粗 bbox 或 crop。
- hard negative：同图中非疑似区域 crop。
- authentic negative：真实图随机 crop。

MVP 输出格式：

```json
{
  "proposal_id": "R1",
  "region_verdict": "tampered",
  "tamper_domain": "photoshop|deepfake|aigc_inpaint|none|unknown",
  "artifact_evidence": ["..."],
  "confidence": 0.0,
  "short_reasoning": "..."
}
```

快速验收：

- 能处理 `image + bbox/crop + claim`。
- 能输出合法 JSON。
- 在少量 case study 中比全图 Stage1 更能指出局部证据。

### 第三层：Claim-conditioned SFT

目标：贴近最终伪造新闻检测任务。

输入：

```text
新闻 title/body
新闻 image
claim
caption/scene
region proposal
Stage1/Stage2 图像取证结果
```

输出：

```json
{
  "final_verdict": "real_news|suspicious|fake_news|uncertain",
  "fake_type": [
    "image_tampering",
    "text_image_inconsistency",
    "claim_depends_on_tampered_region"
  ],
  "claim_analysis": [
    {
      "claim_id": "C1",
      "status": "supported|contradicted|depends_on_suspicious_region|not_verifiable|uncertain",
      "evidence": "..."
    }
  ],
  "final_reasoning": "...",
  "report": "..."
}
```

快速推进版可以先合成小规模数据，不等待真实新闻大数据集。

## 端到端模块推进顺序

### Module 1：输入解析

目标：从新闻文本和图片中提取结构化 claim 与候选区域。

快速实现：

- 文本 claim extraction 先用 Qwen2.5-VL text-only 或 GPT API。
- 图像 caption/scene parsing 先用 Qwen2.5-VL base。
- bbox/region proposal 初版可以用规则或模型输出粗 bbox，不追求完美 grounding。

输出：

```json
{
  "text_claims": [],
  "image_parse": {
    "caption": "...",
    "scene": {},
    "region_proposals": []
  }
}
```

### Module 2：图像取证

目标：复用 Stage1 `json_p500` LoRA，输出图像级或区域级取证结果。

快速实现：

- 第一版直接用整图 Stage1 LoRA。
- 对 Module 1 给出的关键 region，裁剪 crop 后再次调用 Stage1 LoRA。
- SAM mask refinement 先作为可选模块；没有 SAM 时使用 bbox mask fallback。

输出：

```json
{
  "image_verdict": "authentic|tampered|uncertain",
  "tamper_domain": "photoshop|deepfake|aigc_inpaint|none|unknown",
  "suspicious_regions": [],
  "forensic_confidence": 0.0
}
```

### Module 3：综合推理与报告

目标：把 claim、图像解析和取证证据合成最终新闻判断。

快速实现：

- 优先用 GPT-4o/API 或 Qwen text 模型做 JSON 综合推理。
- 严格限制只能使用 Module 1/2 证据，不引入外部知识。
- 输出最终 verdict、fake type、claim analysis、report。

## 最近两周执行计划

### 第 1 步：冻结 Stage1 baseline

交付：

- 记录 `p500_json` 数据、训练配置、评估结果。
- 明确 Stage1 作为可用视觉取证模块。

不再做：

- 不继续调 p500 epoch。
- 不继续单独追 Photoshop accuracy。

### 第 2 步：打通端到端 MVP

交付：

- 输入一条新闻 JSON 和图片。
- 自动生成 claims。
- 自动生成 caption/scene/regions。
- 调用 Stage1 LoRA 生成图像取证 JSON。
- 生成最终 fake-news report。

验收：

```text
python -m fake_news_forensics.pipeline.cli --input examples/sample_news.json
```

输出完整结构化报告。

### 第 3 步：构造 10-30 条 case study

来源可以先用：

- MMTD 图片 + 合成新闻 claim。
- 真实新闻标题模板 + MMTD 图像。
- 人工构造图文不一致案例。

目标不是大规模评测，而是证明系统链路和展示效果。

### 第 4 步：小规模 Claim-conditioned SFT

构造：

```text
stage3_claim_sft_demo: 100-300 条
```

训练目标：

- 学会最终 JSON schema。
- 学会 claim-image consistency reasoning。
- 学会引用图像取证证据做结论。

## 暂缓事项

以下内容先不作为主线：

- Photoshop crop/bbox 专项大规模优化。
- SAM 精细 mask 质量优化。
- CLIP domain classifier 单独训练。
- 多模型 ensemble。
- 大规模真实新闻数据收集。
- 与 FakeShield 原始 DTE-FDM 权重路线对齐。

这些可以作为后续加分实验，不影响当前项目闭环。

## 当前一句话路线

冻结 `json_p500` 作为图像级取证 baseline，快速把系统推进到 `新闻文本 + 图片 -> claim 解析 -> 图像取证 -> 图文一致性判断 -> 结构化报告` 的端到端 MVP，再用小规模 claim-conditioned SFT 做最终项目效果展示。
