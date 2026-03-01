# Model GPU Sizing Guide

> **How many GPUs does your model need?** This guide provides memory and compute requirements for training and deploying major AI models across all major GPU types.

## Quick Reference: Inference (FP16)

| Model | Parameters | VRAM Required | Min GPU Config | Recommended Config |
|-------|-----------|---------------|----------------|-------------------|
| LLaMA 3 8B | 8B | ~16 GB | 1x RTX 4090 (24GB) | 1x A100 40GB |
| LLaMA 3 70B | 70B | ~140 GB | 2x H100 80GB | 2x H100 80GB |
| LLaMA 3 405B | 405B | ~810 GB | 11x H100 80GB | 12x H100 80GB |
| Mistral 7B | 7B | ~14 GB | 1x RTX 4090 (24GB) | 1x A100 40GB |
| Mixtral 8x7B | 47B active | ~94 GB | 2x A100 80GB | 2x H100 80GB |
| Mixtral 8x22B | 141B active | ~282 GB | 4x H100 80GB | 4x H100 80GB |
| GPT-4 (est.) | ~1.8T | ~3.6 TB | 48x H100 80GB | 64x H100 80GB |
| Claude 3 Opus (est.) | ~2T | ~4 TB | 52x H100 80GB | 64x H100 80GB |
| Gemini Ultra (est.) | ~1.6T | ~3.2 TB | 40x H100 80GB | 48x H100 80GB |
| Falcon 180B | 180B | ~360 GB | 5x H100 80GB | 8x H100 80GB |
| Yi 34B | 34B | ~68 GB | 1x H100 80GB | 1x H100 80GB |
| DeepSeek V3 | 671B | ~1.34 TB | 17x H100 80GB | 24x H100 80GB |
| DeepSeek R1 | 671B | ~1.34 TB | 17x H100 80GB | 24x H100 80GB |

## Memory Calculation Formula

```
VRAM (GB) = (Parameters x Bytes_per_param) / 1e9

Precision bytes:
  FP32  = 4 bytes
  BF16  = 2 bytes
  FP16  = 2 bytes
  INT8  = 1 byte
  INT4  = 0.5 bytes
  NF4   = 0.5 bytes

Add ~20% overhead for KV cache, activations, runtime
```

### Examples
- LLaMA 3 70B in FP16: (70e9 × 2) / 1e9 = **140 GB** + 20% overhead = ~168 GB
- LLaMA 3 70B in INT4: (70e9 × 0.5) / 1e9 = **35 GB** + 20% overhead = ~42 GB

## Training Memory Requirements

Training requires significantly more VRAM than inference due to optimizer states, gradients, and activations.

### Full Fine-Tuning (AdamW)

| Precision | Memory Multiplier | Formula |
|-----------|------------------|----------|
| FP32 training | ~16x params | 16 bytes/param |
| Mixed precision (BF16 + FP32 master) | ~18x params | 18 bytes/param |
| Pure BF16 | ~12x params | 12 bytes/param |

**Example:** Fine-tuning LLaMA 3 8B with full precision:
- 8B × 18 bytes = **144 GB** minimum
- Requires: 2x A100 80GB or 2x H100 80GB

### Parameter-Efficient Fine-Tuning (PEFT)

| Method | Memory Overhead | Notes |
|--------|----------------|-------|
| LoRA (r=16) | +~5% base model | Trains only low-rank matrices |
| QLoRA (4-bit + LoRA) | ~0.5x params | 4-bit base + FP16 adapters |
| IA3 | +~1% base model | Fewer trainable params than LoRA |
| Prefix Tuning | +~2% base model | Trainable prefix tokens |

**Example:** QLoRA on LLaMA 3 70B:
- Base: 70B × 0.5 bytes = 35 GB + LoRA adapters ~2 GB = **~37 GB**
- Fits on: 1x H100 80GB

## Context Length Impact on VRAM

KV cache memory scales with sequence length:

```
KV_cache_GB = (2 × n_layers × n_heads × head_dim × seq_len × batch_size × bytes) / 1e9
```

| Model | Context | KV Cache @ batch=1 |
|-------|---------|-------------------|
| LLaMA 3 8B | 8K | ~0.5 GB |
| LLaMA 3 8B | 128K | ~7.5 GB |
| LLaMA 3 70B | 8K | ~3.5 GB |
| LLaMA 3 70B | 128K | ~56 GB |
| LLaMA 3 405B | 128K | ~320 GB |

## GPU Configurations for Popular Models

### LLaMA 3 8B
| Use Case | GPU Config | Throughput |
|----------|-----------|------------|
| Inference (FP16) | 1x RTX 4090 | ~2,400 tok/s |
| Inference (FP16) | 1x A100 80GB | ~4,100 tok/s |
| Inference (FP16) | 1x H100 80GB | ~7,200 tok/s |
| Fine-tune (QLoRA) | 1x A100 40GB | ~5,000 tok/s training |
| Fine-tune (Full FP16) | 2x A100 80GB | ~2,200 tok/s training |

### LLaMA 3 70B
| Use Case | GPU Config | Throughput |
|----------|-----------|------------|
| Inference (FP16) | 2x H100 80GB | ~2,100 tok/s |
| Inference (FP16) | 2x A100 80GB | ~1,200 tok/s |
| Inference (INT4) | 1x H100 80GB | ~1,800 tok/s |
| Fine-tune (QLoRA) | 2x A100 80GB | ~400 tok/s training |
| Fine-tune (Full FP16) | 8x A100 80GB | ~1,100 tok/s training |

### LLaMA 3 405B
| Use Case | GPU Config | Throughput |
|----------|-----------|------------|
| Inference (FP16) | 8x H100 80GB | ~580 tok/s |
| Inference (INT4) | 4x H100 80GB | ~640 tok/s |
| Fine-tune (Full BF16) | 64x H100 80GB | ~800 tok/s training |

## Multi-GPU Parallelism Strategies

### Tensor Parallelism (TP)
- Splits individual layers across GPUs
- Requires high-bandwidth interconnect (NVLink, InfiniBand)
- Recommended for inference: 2-8 GPUs per node
- Linear scaling up to ~8 GPUs with NVLink

### Pipeline Parallelism (PP)
- Splits model layers across GPU groups
- Works across nodes with lower-bandwidth networking
- Higher latency but enables very large models
- Typical: 4-16 pipeline stages

### Data Parallelism (DP)
- Replicates model across GPU groups
- Used for training throughput scaling
- Requires gradient synchronization (AllReduce)

### Recommended for Large Models

| Model Size | Strategy | Example |
|-----------|----------|----------|
| 7-13B | Single GPU or TP-2 | 1-2x H100 |
| 34-70B | TP-4 or TP-8 | 4-8x H100 |
| 100-200B | TP-8 + DP | 8-16x H100 |
| 405B+ | TP-8 + PP-4 + DP | 32-64x H100 |

## Inference Frameworks & Quantization

| Framework | Quantization | Best For |
|-----------|-------------|----------|
| vLLM | FP16, INT8, AWQ, GPTQ | Production serving, high throughput |
| TensorRT-LLM | FP16, INT8, INT4 | NVIDIA optimized, lowest latency |
| llama.cpp | GGUF (Q2-Q8) | CPU+GPU, local deployment |
| Ollama | GGUF | Developer-friendly local LLMs |
| ExLlamaV2 | EXL2 | High-quality quantization |
| Transformers | FP32/FP16/BF16 | Research, flexibility |
| bitsandbytes | INT8, NF4 | Easy quantization integration |

## Cost Estimation (AWS on-demand)

### Inference Cost per 1M Tokens

| Model | GPU Config | Cost/Hr | Throughput | Cost/1M tok |
|-------|-----------|---------|------------|-------------|
| LLaMA 3 8B | 1x H100 (p5) | $12.29 | 7,200 tok/s | $0.47 |
| LLaMA 3 70B | 2x H100 (p5) | $24.58 | 2,100 tok/s | $3.25 |
| LLaMA 3 405B | 8x H100 (p5) | $98.32 | 580 tok/s | $47.11 |

### Training Cost Estimates

| Model | Tokens | GPU Config | Est. Time | Est. Cost |
|-------|--------|-----------|-----------|----------|
| 7B from scratch | 1T | 64x H100 | ~20 days | ~$2.5M |
| 7B fine-tune (10B tok) | 10B | 8x H100 | ~5 days | ~$94K |
| 70B from scratch | 1T | 512x H100 | ~25 days | ~$25M |
| 70B fine-tune (10B tok) | 10B | 64x H100 | ~7 days | ~$1.1M |

---

*Last updated: February 2026 | Sources: model cards, empirical benchmarks, provider documentation*
*See [inference-benchmarks.md](inference-benchmarks.md) for detailed throughput measurements*
