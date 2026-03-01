# GPU Cost Optimization Playbook

> **The definitive open-source GPU cost optimization guide.** No other repository, tool, or resource consolidates these techniques with real 2025–2026 pricing data.
>
> Part of the [AI Infrastructure Index](../README.md) — an independent, vendor-neutral reference maintained by [Alpha One Index](https://github.com/alpha-one-index).
>
> **Last updated:** March 2026 | **Audience:** ML engineers, MLOps, AI infrastructure leads

---

## Table of Contents

1. [What Are the Biggest Levers for Reducing GPU Cloud Costs?](#section-1-overview--executive-summary)
2. [Which GPU Should I Actually Use for My Workload?](#section-2-instance-right-sizing)
3. [How Much Can Quantization Save, and What Do I Lose?](#section-3-quantization-cost-impact)
4. [How Do I Use Spot Instances Without Losing Training Progress?](#section-4-spot-instance-strategies)
5. [When Does a Reserved Instance Actually Pay Off?](#section-5-reserved-instance--commitment-optimization)
6. [How Do Batching and Scheduling Reduce My Per-Token Cost?](#section-6-batch-processing--scheduling)
7. [Should I Be Shopping Across GPU Cloud Providers?](#section-7-multi-cloud-arbitrage)
8. [How Do I Track and Govern GPU Spend Across My Team?](#section-8-cost-monitoring--governance)
9. [Quick Wins Summary](#quick-wins-summary)

---

## Section 1: What Are the Biggest Levers for Reducing GPU Cloud Costs?

The GPU cloud market fundamentally changed in 2025. [H100 on-demand prices dropped 64–75% from their Q4 2024 peak of ~$8/hr](https://introl.com/blog/gpu-cloud-price-collapse-h100-market-december-2025) as 300+ new providers entered the market and hyperscalers initiated price wars (AWS cut H100 pricing ~44% in June 2025 alone). By late 2025, effective H100 rates ranged from [$1.49/hr on marketplaces like Vast.ai to $6.98/hr on Azure](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison) — a nearly 5× spread for identical hardware. That spread is your opportunity.

The table below shows the headline savings potential from each optimization technique covered in this playbook. Start with the techniques that have the highest savings potential and lowest effort.

### Savings Potential by Technique

| Technique | Baseline Scenario | Optimized Scenario | Potential Savings | Effort |
|---|---|---|---|---|
| Right-sizing GPU tier | H100 serving a 7B model | L4 serving a 7B model | 60–70% | Low |
| FP8 quantization (vs FP16) | 2× H100 for inference | 1× H100 (50% fewer GPUs) | ~50% | Low |
| INT4 quantization (vs FP16) | 2× A100 80GB | 1× A100 40GB | ~75% | Medium |
| Spot vs. on-demand | H100 on-demand $3.50/hr | H100 spot $1.87/hr | 45–60% | Medium |
| Reserved vs. on-demand | H100 on-demand $3.50/hr | Reserved $1.90–2.10/hr | 40–46% | Low (commit) |
| Continuous batching | GPU utilization ~40% | GPU utilization 90%+ | ~50% per-token | Medium |
| Batch processing (size 32) | Single-request inference | Batched inference | ~85% per-token | Medium |
| Provider arbitrage | AWS on-demand $3.90/hr | RunPod/Vast.ai $1.87–2.49/hr | 36–52% | Medium |
| MIG partitioning | 1 GPU, 1 workload | 1 GPU, 7 workloads | Up to 7× density | Medium |
| Auto-shutdown idle GPUs | 8 hrs/day idle at $3.50/hr | Scale to zero when idle | 33% of monthly bill | Low |

**Key principle:** These techniques compound. Right-sizing + quantization + continuous batching together can reduce cost per token by 80–90% compared to a naive deployment running an oversized GPU at 40% utilization in FP16.

---

## Section 2: Which GPU Should I Actually Use for My Workload?

### The Right-Sizing Imperative

The most common—and most expensive—mistake in AI infrastructure is defaulting to the most powerful GPU available. [A team running a 7B parameter model on H100s is spending 4–6× more than necessary](https://www.spheron.network/blog/gpu-cost-optimization-playbook/), while the H100's additional capabilities go entirely unused.

GPU selection is a three-factor problem:
1. **Memory capacity** — can the model fit on the GPU (or multi-GPU)?
2. **Memory bandwidth** — critical for autoregressive inference (memory-bound)
3. **Compute throughput** — critical for training and large-batch inference (compute-bound)

### GPU Tier Selection Table

| Model Size | FP16 VRAM | Recommended GPU(s) | On-Demand Cost/hr | Use Case Notes |
|---|---|---|---|---|
| ≤3B params | ≤6 GB | L4 (24 GB GDDR6) | ~$0.50–0.80 | Cheapest inference; fit 4+ models per L4 with MIG or time-slicing |
| 7B–13B params | 14–28 GB | L4, L40S (48 GB) | $0.50–1.20 | L4 wins on cost-per-token; L40S if you need 13B in one card |
| 13B–30B params | 28–60 GB | A100 40GB, L40S | $1.20–2.00 | L40S for inference (lower cost); A100 40GB for fine-tuning |
| 30B–70B params | 60–140 GB | A100 80GB, H100 80GB | $1.90–3.90 | 70B FP16 requires 2× A100 80GB or 1× H100; consider INT4 to fit on single A100 40GB |
| 70B–130B params | 140–260 GB | 2× H100, H200 (141 GB) | $3.90–8.00 | H200 fits Llama-3 70B in one card vs. 2× H100 — often cheaper despite higher per-card rate |
| 130B+ params | >260 GB | Multi-H100/H200 cluster | $8.00+ | NVLink essential; evaluate distillation or quantization first |

### GPU Specs Comparison (2025–2026)

| GPU | Memory | Memory BW | FP16 TFLOPS | TDP | Typical On-Demand | Best For |
|---|---|---|---|---|---|---|
| L4 | 24 GB GDDR6 | 300 GB/s | 242 | 72 W | $0.50–0.80/hr | Small model inference, cost-sensitive |
| L40S | 48 GB GDDR6 | 864 GB/s | 733 | 350 W | $0.87–1.20/hr | Mid-model inference, graphics+AI |
| A100 40GB | 40 GB HBM2e | 1.6 TB/s | 312 | 300 W | $1.20–1.60/hr | Legacy; fine-tuning mid-size models |
| A100 80GB | 80 GB HBM2e | 2.0 TB/s | 312 | 400 W | $1.50–2.00/hr | Legacy; 70B inference (2-card) |
| H100 SXM | 80 GB HBM3 | 3.35 TB/s | 989 | 700 W | $2.99–3.90/hr | Training, high-QPS 70B inference |
| H200 | 141 GB HBM3e | 4.8 TB/s | ~1,000 | 700 W | ~$4.50–5.50/hr | 100B+ models, long-context inference |
| B200 | 192 GB HBM3e | ~8 TB/s | ~4,500 | 1,000 W | ~$6–8/hr (early 2026) | Next-gen training; limited availability |

> **Note:** A100 is officially EOL (Feb 2024). Do not build new infrastructure on A100 — use as legacy until replacement cycle. [H100 SXM delivers 86% lower training cost per token vs. A100 PCIe](https://www.cudocompute.com/blog/real-world-gpu-benchmarks) ($0.88 vs. $6.32 per 10M tokens) despite higher hourly rate.

### Memory-Bound vs. Compute-Bound Workloads

**Memory-bound** (throughput limited by GPU memory bandwidth):
- Autoregressive inference at small batch sizes (batch=1 to batch=8)
- KV cache operations
- *Decision:* Prioritize memory bandwidth (TB/s), not TFLOPS. The H100's 3.35 TB/s vs. A100's 2.0 TB/s matters more than raw FLOPS for chatbot-style inference.

**Compute-bound** (throughput limited by TFLOPS):
- Training
- Large-batch inference (batch≥32)
- Prefill/context encoding
- *Decision:* Prioritize FP16/BF16/FP8 TFLOPS. H100 FP8 Tensor Core performance (3,958 TFLOPS) makes it the clear leader here.

**Rule of thumb:** For a production chatbot serving 1 request at a time, L40S often beats H100 on cost-per-token because both are memory-bound and L40S is ~65% cheaper per hour.

---

## Section 3: How Much Can Quantization Save, and What Do I Lose?

### The Core Tradeoff

Quantization reduces the numerical precision of model weights—from FP32 or FP16 down to FP8, INT8, or INT4—shrinking model size, reducing memory bandwidth demand, and increasing throughput. The cost savings come from two channels: (1) fitting larger models on cheaper/fewer GPUs, and (2) serving more tokens per second on the same hardware.

[Oracle's production benchmarks on Llama 3.3-70B](https://blogs.oracle.com/cloud-infrastructure/cost-efficient-llm-serving-with-quantization) found FP8 quantization achieved 99%+ model quality recovery, 30% latency reduction, and 50% throughput increase — using the same number of GPUs. [GPTQ-Int4 on Qwen3-32B delivers a 2.69× throughput increase over BF16](https://research.aimultiple.com/llm-quantization/), cutting hardware cost per million tokens by 63%.

### Precision Level Comparison Table

| Precision | VRAM vs. FP16 | Throughput Gain | Accuracy Retention | GPU Tier Change? | Best Use Case |
|---|---|---|---|---|---|
| FP32 → FP16/BF16 | −50% | +0–20% | ~100% | Often yes (half the cards) | Always use FP16/BF16 as your default; no reason to run FP32 in inference |
| FP16 → FP8 (dynamic) | −50% | +100% (2×) | 99–100% | Sometimes (H100+ required for native FP8) | Production inference on H100/H200; near-lossless compression |
| FP16 → INT8 (GPTQ W8A8) | −50% | +30–40% | ~99% | Rarely | High-quality inference on Ampere+ GPUs |
| FP16 → INT4 (GPTQ/AWQ) | −75% | +2.5–3× | 95–99.5% | Yes — often drops to half the GPU count | Chatbots, RAG, production APIs where slight quality drop is acceptable |
| FP16 → INT4 (aggressive) | −75% | +2.5–3× | 90–96% | Yes | Batch processing, classification, embedding workloads |
| FP16 → INT2/3 | −81–87% | +3–4× | 80–90% | Yes | Research only; significant quality degradation |

> **FP8 note:** Native FP8 tensor core support requires H100/H200 (Hopper) or B200 (Blackwell). On A100 or older GPUs, FP8 falls back to software emulation and provides no speedup. Plan GPU tier accordingly.

### When Quantization Changes Your GPU Tier

This is where the real money is. A tier change means you pay for fewer or cheaper GPUs.

| Model | FP16 Requirement | After INT4 (GPTQ/AWQ) | GPU Cost Reduction |
|---|---|---|---|
| Llama 3.1 8B | ~17 GB → 1× L40S | ~4.5 GB → 1× L4 (24 GB) | ~40% (L40S $1.20 → L4 $0.65/hr) |
| Llama 3.3 70B | ~140 GB → 2× H100 80GB | ~41 GB → 1× A100 80GB | ~75% ($7.80 → $1.90/hr total) |
| Qwen2.5 72B | ~144 GB → 2× H100 | ~36–44 GB → 1× A100 80GB | ~75% |
| Llama 3.1 405B | ~810 GB → 10× H100 | ~200 GB → 3× H100 | ~70% |
| GPT-style 13B | ~26 GB → 1× A100 40GB | ~6.5 GB → 1× L4 | ~50–60% |

**Practical formula:**  
`VRAM required (GB) = (Params_billions × Bits_per_weight) / 8 × 1.2`  
The 1.2× factor accounts for KV cache and activation overhead at moderate batch sizes. Double it for large batches.

### Recommended Quantization by Use Case

| Use Case | Recommended Precision | Rationale |
|---|---|---|
| Real-time chatbot / customer-facing API | FP8 (H100+) or INT4-AWQ | 99% accuracy, lowest latency per token |
| Internal RAG / knowledge base | INT4-AWQ or INT4-GPTQ | Acceptable quality loss, major GPU savings |
| Batch processing / classification | INT4-GPTQ | Throughput matters; accuracy secondary |
| Code generation / copilot | FP8 or INT4-AWQ | Coherence matters; AWQ preserves code accuracy better than GPTQ |
| Research / fine-tuning | BF16 or FP16 | Don't quantize during training; use BF16 as default |
| Embedding generation | INT8 | 99% accuracy, 50% VRAM reduction, no perceptible quality loss |
| Vision-language models | FP8 (W8A8) or INT4-W4A16 | FP8 recovers >99% accuracy; INT4 slightly lower on smaller VLMs |

### Key Quantization Libraries (2025)

- **[bitsandbytes](https://github.com/TimDettmers/bitsandbytes):** Simplest INT4/INT8 for HuggingFace; best for getting started
- **[AutoAWQ](https://github.com/casper-hansen/AutoAWQ):** Best quality-preservation at 4-bit; preferred for production chatbots
- **[AutoGPTQ](https://github.com/AutoGPTQ/AutoGPTQ):** Highest throughput at 4-bit on CUDA; preferred for batch inference
- **[llama.cpp / GGUF](https://github.com/ggerganov/llama.cpp):** Cross-platform CPU+GPU inference; best for self-hosted deployments

---

## Section 4: How Do I Use Spot Instances Without Losing Training Progress?

### The Economics of Spot

[Spot/preemptible instances typically run 40–70% cheaper than on-demand](https://introl.com/blog/spot-instances-preemptible-gpus-ai-cost-savings). In concrete 2025 numbers:

| Provider | H100 On-Demand | H100 Spot/Preemptible | Discount |
|---|---|---|---|
| AWS (P5) | $3.50/hr | ~$2.50/hr | ~29% |
| GCP (A3-High) | $3.25/hr | $2.25/hr | ~31% |
| Azure (ND H100 v5) | $3.40/hr | ~$2.60/hr | ~24% |
| RunPod | $2.39/hr | $1.87/hr | ~22% |
| Vast.ai marketplace | Variable | $1.49–$1.87/hr | ~40–60% vs. hyperscaler |

> **Important context:** The hyperscaler spot discounts for H100 are narrower in 2025 than for earlier GPU generations because on-demand prices already fell steeply. The bigger arbitrage in 2025 is **provider arbitrage** (Section 7), not spot vs. on-demand within a single hyperscaler. Spot on specialized providers like Vast.ai can reach $1.49/hr—65% below AWS on-demand.

### Interruption Rates to Plan Around

[H100 spot instances have a ~4.1% hourly interruption rate on AWS](https://introl.com/blog/spot-instances-preemptible-gpus-ai-cost-savings), higher than A100 (2.3%) or V100 (0.8%). This means statistically, an H100 spot instance runs ~24 hours uninterrupted before interruption. Weekend interruption rates are ~40% lower than weekdays. US-East-1 has 3× higher interruption rates than US-West-2.

**Interruption notice windows:**
- AWS: 2-minute termination notice via [instance metadata service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html)
- GCP Preemptible: 30-second notice
- Azure Spot: configurable, up to 30 minutes in some regions

### Checkpointing Strategy

The only way to use spot instances safely for training is aggressive, automated checkpointing to durable storage.

```python
import signal
import time
import torch

class SpotCheckpointer:
    def __init__(self, checkpoint_path: str, interval_seconds: int = 600):
        self.checkpoint_path = checkpoint_path  # S3/GCS/AZ blob URL
        self.interval_seconds = interval_seconds  # 10 min default
        self.last_checkpoint = time.time()
        
        # Register termination signal handler
        signal.signal(signal.SIGTERM, self._emergency_checkpoint)
    
    def _emergency_checkpoint(self, signum, frame):
        """Called on 2-minute AWS termination notice (SIGTERM)."""
        print("Termination notice received — saving emergency checkpoint...")
        self.save(emergency=True)
        sys.exit(0)
    
    def maybe_checkpoint(self, model, optimizer, step, epoch):
        """Call at the end of every training step."""
        if time.time() - self.last_checkpoint > self.interval_seconds:
            self.save(model, optimizer, step, epoch)
    
    def save(self, model, optimizer, step, epoch, emergency=False):
        state = {
            'step': step,
            'epoch': epoch, 
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }
        torch.save(state, f"{self.checkpoint_path}/ckpt-step-{step}.pt")
        self.last_checkpoint = time.time()
        if not emergency:
            # Clean up older checkpoints to limit storage cost
            self._cleanup_old_checkpoints(keep_last=3)
```

**Checkpoint interval recommendations:**
- H100 training runs: every 5–10 minutes (high interruption rate)
- A100/V100: every 10–15 minutes (lower interruption rate)
- Batch inference: checkpoint per job; use message queue (SQS, Pub/Sub) for task state

### Architecture Patterns

**Pattern 1: Spot for training, on-demand for inference (standard)**
```
Training cluster: 100% spot (fault-tolerant with checkpointing)
    ↓ saves model artifacts to S3/GCS
Inference fleet: 70% on-demand + 30% spot
    (spot instances serve traffic; on-demand provides baseline availability)
```

**Pattern 2: Reserved baseline + spot burst**
```
Reserved: 60–80% of steady-state GPU requirement (predictable cost)
Spot: burst capacity for peak training windows, batch jobs
On-demand: emergency failover only
```

**Pattern 3: Spot-only with queue-based fault tolerance**
- All training jobs submitted to a durable queue (SQS, Pub/Sub, Ray)
- Workers pull jobs, run with checkpointing, re-queue on interruption
- Effective for hyperparameter sweeps, batch processing, fine-tuning pipelines
- [Pinterest used this pattern to save $4.8M/year (72% reduction) training recommendation models](https://introl.com/blog/spot-instances-preemptible-gpus-ai-cost-savings)

### When NOT to Use Spot

| Scenario | Use Instead | Reason |
|---|---|---|
| Real-time inference (user-facing API) | On-demand or reserved | Interruptions cause user-visible errors |
| Training runs >24 hours without checkpointing | On-demand (or add checkpointing first) | Guaranteed interruption on GCP Preemptible; high risk on AWS |
| Regulatory/compliance workloads | On-demand or private cloud | Compliance may require guaranteed capacity |
| Stateful streaming or online learning | On-demand | State reconstruction cost exceeds spot savings |

---

## Section 5: When Does a Reserved Instance Actually Pay Off?

### The Break-Even Framework

Reserved instances (also called "Savings Plans," "Committed Use Discounts," or "reservations" depending on provider) require committing to a specific GPU type and quantity for 1–3 years in exchange for 30–50% discounts. The key question is: **what utilization rate makes a reservation economical?**

**Formula:**
```
Break-even utilization = Reserved rate / On-demand rate
```

Example: If reserved H100 = $1.90/hr and on-demand = $3.50/hr:
```
Break-even = $1.90 / $3.50 = 54%
```

If your GPU runs >54% of the time, the reservation saves money. If it runs 80% of the time, you save 46% overall vs. pure on-demand.

### Commitment Term vs. Discount Table

| Term | Typical Discount vs. On-Demand | Effective H100 Rate | Break-Even Utilization |
|---|---|---|---|
| No commitment (on-demand) | 0% | $3.50/hr | N/A |
| 1-year reserved | 35–40% | ~$2.10/hr | 60% |
| 3-year reserved | 50–60% | ~$1.90/hr | 54% |
| Spot (no term) | 29–65% | $1.49–2.50/hr | N/A (variable) |

> **Real 2025 reserved rates:** [AWS Savings Plans can bring H100 to $1.90–2.10/hr](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison); [Lambda Labs reserved starts at $1.85/hr](https://www.gmicloud.ai/blog/how-much-does-it-cost-to-rent-or-buy-nvidia-h100-gpus-for-data-centers-in-2025); Hyperstack from $1.90/hr.

### Provider Reserved Pricing Comparison (H100, late 2025)

| Provider | On-Demand | 1-Year Reserved | 3-Year Reserved | Notes |
|---|---|---|---|---|
| AWS (P5) | $3.50/hr | ~$2.10/hr | ~$1.90/hr | Savings Plans, flexible across instance families |
| GCP (A3-High) | $3.25/hr | ~$2.00/hr | ~$1.85/hr | Committed Use Discounts, 1- or 3-year |
| Azure (ND H100) | $3.40/hr | ~$2.15/hr | ~$1.95/hr | Reserved Instances, 1- or 3-year |
| Lambda Labs | $2.40/hr | $1.85–1.89/hr | N/A | Flat reserved pricing |
| Hyperstack | $2.40/hr | $1.90/hr | N/A | Best non-hyperscaler reserved rate |
| CoreWeave | Variable | Custom enterprise | Custom enterprise | Contact for cluster commitments |

### Reserved Instance Decision Tree

```
Is your GPU utilization >70% consistently?
├── YES → Reserved is likely profitable; calculate break-even with your on-demand rate
│         Is it >80%? → 3-year reserved; lock in the lowest rate
│         Is it 70-80%? → 1-year reserved; preserve some flexibility
└── NO → Is it 40–70%?
         ├── YES → Mix: reserve 50% of baseline, spot for remainder
         └── NO (<40%) → Pure on-demand or spot; reservation will not break even

Is your workload predictable (same GPU type, same volume)?
├── YES → Standard Reserved Instance
└── NO → AWS Compute Savings Plans (flex across instance families at ~5% less discount)
```

### On-Premises Break-Even Analysis

For teams considering buying GPUs outright, the math is more complex:

| Scenario | Cloud Cost (annual) | On-Prem TCO (annual, 5-yr amortized) | Break-Even Point |
|---|---|---|---|
| 4× H100, 100% utilization | ~$122K/yr at $3.50/hr | ~$85K/yr (hardware + power + ops) | ~12 months |
| 4× H100, 70% utilization | ~$86K/yr | ~$85K/yr (fixed) | ~14–16 months |
| 4× H100, 40% utilization | ~$49K/yr | ~$85K/yr (fixed) | Never breaks even |

[Lenovo's 5-year TCO study for 4× A100 servers found on-prem break-even at ~12 months at 100% utilization](https://www.memorysolution.de/en/cloud-or-n-premises-what-really-pays-off), with $1.5–3.4M in 5-year savings vs. cloud at that utilization. However, [GPU hardware loses 30–40% of value in the first year](https://localaimaster.com/tutorials/cloud-vs-local-calculator), and realistic utilization for most teams is 60–80%, pushing break-even to 14–18 months.

**On-prem checklist — only proceed if all are true:**
- [ ] Utilization consistently >70% (measure before buying)
- [ ] You have or can hire dedicated infra team
- [ ] You have data center space, power (≥60 kW per 8-GPU node), and cooling
- [ ] Regulatory requirements mandate on-prem (HIPAA, FedRAMP, etc.)
- [ ] 3+ year commitment to this hardware generation
- [ ] Provider profitability floor (~$1.65/hr for H100) means cloud prices are unlikely to fall much further

---

## Section 6: How Do Batching and Scheduling Reduce My Per-Token Cost?

### Why Naive Inference Is Expensive

A typical naive inference deployment runs at [~40% GPU utilization because each request is processed sequentially](https://www.linkedin.com/pulse/optimizing-nvidia-gpu-utilization-llm-inference-deep-dive-markevich-rqcge), leaving the GPU idle while waiting for the next request. This means you're paying for an H100 but using 40% of it. Batching and scheduling are how you recover that 60%.

### Continuous Batching (In-Flight Batching)

Traditional static batching waits for a fixed number of requests before processing. If batch size = 32 and only 8 requests arrive, you wait — wasting throughput. [Continuous batching (pioneered by vLLM) eliminates batch boundaries](https://introl.com/blog/vllm-production-deployment-inference-serving-architecture): when a sequence completes, its GPU slot immediately accepts a new request. The GPU processes whatever exists at each decoding step.

**Result:** [GPU utilization rises from ~40% to 90%+, reducing per-token cost by ~50%](https://www.redhat.com/en/blog/meet-vllm-faster-more-efficient-llm-inference-and-serving). [Stripe achieved 73% inference cost reduction via vLLM migration](https://introl.com/blog/vllm-production-deployment-inference-serving-architecture), processing the same 50M daily API calls on one-third the GPU fleet.

**vLLM quick-start:**
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.3-70B-Instruct \
    --tensor-parallel-size 2 \
    --max-model-len 8192 \
    --enable-chunked-prefill \
    --gpu-memory-utilization 0.92
```

### Batch Size vs. Cost vs. Latency

For workloads that tolerate latency (batch inference, offline processing):

| Batch Size | vs. BS=1 Cost Per Token | vs. BS=1 Latency | Use Case |
|---|---|---|---|
| 1 (no batching) | 100% (baseline) | Baseline | Real-time chat, <50ms SLA |
| 4 | ~50% | +5–10% | Interactive tools, copilots |
| 8 | ~30% | +10–20% | Internal APIs, RAG |
| 16 | ~20% | +30–50% | Batch document processing |
| 32 | ~15% (−85%) | +50–100% | Overnight batch jobs, analytics |
| 64+ | ~10% | +100–200% | Bulk classification, embedding |

[Batch size 32 achieves ~85% per-token cost reduction with ~20% additional latency in well-optimized inference stacks](https://research.aimultiple.com/llm-quantization/). For batch inference pipelines without strict latency requirements, this is often the single highest-ROI change available.

### MIG (Multi-Instance GPU) Partitioning

[NVIDIA MIG technology (A100+, H100+) partitions a single physical GPU into up to 7 isolated instances](https://aws.amazon.com/blogs/machine-learning/hyperpod-now-supports-multi-instance-gpu-to-maximize-gpu-utilization-for-generative-ai-tasks/), each with dedicated VRAM, SMs, and memory controllers. Unlike time-slicing, there is no performance interference between instances.

**H100 80GB MIG profiles:**

| Profile | Memory | SMs | Instances/GPU | Best For |
|---|---|---|---|---|
| 1g.10gb | 10 GB | 16 | 7 | Tiny models, embedding, small inference |
| 2g.20gb | 20 GB | 32 | 3 | 7B inference, fine-tuning |
| 3g.40gb | 40 GB | 60 | 2 | 13B–30B inference |
| 4g.40gb | 40 GB | 64 | 1 | Single large inference + headroom |
| 7g.80gb | 80 GB | 132 | 1 | Full GPU (MIG off) |

**Cost arithmetic example:**
- 1× H100 on-demand at $3.50/hr
- Split 7 ways with MIG (7× 1g.10gb)
- Each partition costs $0.50/hr effective
- Equivalent cost of 7 independent L4 GPUs ($3.50/hr) for the price of one H100

**When to use MIG:**
- Serving multiple small models (≤7B) simultaneously
- Multi-tenant environments where workload isolation is required
- Development/staging: run 7 developer instances on 1 GPU
- Disaggregated prefill/decode: larger partitions for prefill (compute-heavy), smaller for decode (memory-bound)

**MIG setup on Kubernetes:**
```bash
# Enable MIG mode on H100 node
nvidia-smi -mig 1

# Configure 7× 1g.10gb partitions
nvidia-smi mig -cgi 19,19,19,19,19,19,19 -C

# Label node for MIG in Kubernetes
kubectl label node <node> nvidia.com/mig.config=all-1g.10gb
```

### Off-Peak Scheduling and Auto-Shutdown

**Off-peak scheduling:** Some specialized GPU cloud providers (and even spot instances) have lower effective rates during off-peak hours (typically 11 PM–7 AM local datacenter time, and weekends). Spot interruption rates on weekends are [40% lower than weekdays](https://introl.com/blog/spot-instances-preemptible-gpus-ai-cost-savings), making them safer for long training runs.

**Auto-shutdown for idle GPUs:** [A GPU left running overnight at H100 prices costs ~$28 per 8 idle hours](https://www.spheron.network/blog/gpu-cost-optimization-playbook/). For a team of 10 developers with 10 GPUs, that's $280/night in waste if everyone forgets to shut down.

Implementation patterns:
```python
# Cloud-agnostic auto-shutdown via utilization monitoring
# Run this as a sidecar or cron job

import subprocess
import time

GPU_IDLE_THRESHOLD = 5  # % utilization
IDLE_DURATION_MINUTES = 15  # shut down after 15 min of idleness

def get_gpu_utilization():
    result = subprocess.run(
        ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader'],
        capture_output=True, text=True
    )
    return int(result.stdout.strip().replace(' %', ''))

idle_start = None
while True:
    util = get_gpu_utilization()
    if util < GPU_IDLE_THRESHOLD:
        if idle_start is None:
            idle_start = time.time()
        elif (time.time() - idle_start) / 60 > IDLE_DURATION_MINUTES:
            # Trigger shutdown (cloud-specific)
            subprocess.run(['aws', 'ec2', 'terminate-instances', '--instance-ids', 
                           get_instance_id()])
    else:
        idle_start = None
    time.sleep(60)
```

**Autoscaling for inference:** [Autoscaling inference replicas based on request queue depth or GPU utilization typically saves 40–50% on inference costs](https://www.spheron.network/blog/gpu-cost-optimization-playbook/) compared to static provisioning. Scale to zero during off-hours; maintain minimum replicas for SLA compliance.

---

## Section 7: Should I Be Shopping Across GPU Cloud Providers?

### The 2025 Price Spread Reality

As of late 2025/early 2026, you can rent identical H100 80GB hardware for anywhere from $1.49/hr (Vast.ai marketplace) to $6.98/hr (Azure East US) — a **4.7× spread**. This is provider arbitrage, and it's real money.

### H100 On-Demand Price Comparison (Late 2025)

| Provider | H100 On-Demand | H100 Spot | Notes |
|---|---|---|---|
| [AWS (P5)](https://aws.amazon.com) | $3.90/hr | ~$2.50/hr | 44% price cut June 2025; Savings Plans available |
| [GCP (A3-High)](https://cloud.google.com/compute/docs/gpus) | $3.00/hr | $2.25/hr | Sustained-use discounts; best hyperscaler value |
| [Azure (ND H100 v5)](https://azure.microsoft.com) | $6.98/hr | ~$2.60/hr | Highest on-demand; strong enterprise SLA |
| [Lambda Labs](https://lambdalabs.com) | $2.99/hr | N/A | Dev-friendly; reserved from $1.85/hr |
| [CoreWeave](https://coreweave.com) | ~$2.21/hr (cluster) | N/A | Best for large H100 clusters; InfiniBand |
| [RunPod](https://runpod.io) | $1.99–2.39/hr | $1.87/hr | Community vs. Secure Cloud tiers |
| [Vast.ai](https://vast.ai) | Variable | $1.49–1.87/hr | Marketplace model; variable reliability |
| [Hyperstack](https://hyperstack.cloud) | $2.40/hr | N/A | Reserved from $1.90/hr |
| [TensorDock](https://tensordock.com) | $2.25/hr | N/A | Competitive on A100 too |
| [Nebius](https://nebius.com) | ~$2.00/hr | N/A | European provider; growing availability |

> **Sources:** [IntuitionLabs H100 comparison (Feb 2026)](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison), [Introl GPU price collapse analysis](https://introl.com/blog/gpu-cloud-price-collapse-h100-market-december-2025), [Fluence best GPU providers 2026](https://www.fluence.network/blog/best-cloud-gpu-providers-ai/)

> **Provider profitability floor:** The break-even cost for a GPU cloud operator running H100s is approximately $1.65/hr (hardware amortization + power + facility). Prices are unlikely to fall significantly below this floor, so the current $1.49–1.87/hr marketplace rates on Vast.ai represent near-floor pricing.

### Also Right-Size by GPU Type Across Providers

| GPU | Cheapest Provider | Rate | Notes |
|---|---|---|---|
| L4 (24 GB) | GCP (on-demand) | ~$0.54/hr | Native GCP; good for scale-out inference |
| A100 40GB | TensorDock, RunPod | ~$1.15–1.19/hr | Community cloud; high availability |
| A100 80GB | Lambda, Vast.ai | ~$1.29–1.57/hr | Better VRAM/dollar than H100 for many workloads |
| H100 80GB | Vast.ai, RunPod | ~$1.49–1.99/hr | Community cloud; spot availability |
| H100 80GB (enterprise SLA) | Lambda, CoreWeave | ~$2.21–2.99/hr | Guaranteed availability |
| H200 141GB | Lambda, RunPod | ~$3.50–4.50/hr | New in 2025; availability expanding |

### Maintaining Portability: The Multi-Cloud Architecture

The prerequisite for effective multi-cloud arbitrage is **portability**. A workload locked into AWS-specific services cannot move to RunPod overnight.

**Portability checklist:**
- [ ] **Containerize everything.** Docker/OCI containers run identically on any provider. Use multi-stage builds to keep images lean.
- [ ] **Decouple compute from storage.** Use S3-compatible object storage (works with MinIO, Wasabi, Backblaze B2, GCS, Azure Blob via adapters). Never store training data or model weights on local instance storage.
- [ ] **Infrastructure as Code.** Terraform or Pulumi for provisioning. Use provider-specific modules but abstract the interface.
- [ ] **OpenAI-compatible inference APIs.** Deploy with vLLM or Triton (both serve OpenAI-compatible endpoints). Switching inference providers requires only a base URL change.
- [ ] **Avoid provider-specific ML services for critical paths.** AWS SageMaker, GCP Vertex AI, Azure ML are convenient but add lock-in. Use them for orchestration, not as the irreplaceable component.

### Egress Cost Considerations

Egress (data leaving a cloud provider) is often an invisible cost that erodes multi-cloud savings.

| Provider | Egress Rate | Notes |
|---|---|---|
| AWS | $0.09/GB (first 10 TB/mo) | Waived to internet in some regions; not waived cross-region |
| GCP | $0.08/GB (US) | Also charges for cross-region |
| Azure | $0.08/GB | First 5 GB/mo free |
| Lambda Labs | $0.00 | No egress fees |
| RunPod | $0.00 | No egress fees |
| CoreWeave | $0.00 | No egress fees; major advantage for large model downloads |

**Rule of thumb:** For a 100 GB model checkpoint, AWS egress costs $9.00. Across 10 training runs, that's $90 in hidden costs. Factor this into your TCO calculation. Specialized providers with no egress fees are particularly attractive for large model training.

**When to switch providers:**
- If a competitor's price for your GPU type is >20% lower AND you can port the workload within 1 day
- If your current provider has recurring availability issues on the GPU type you need
- If a new GPU generation (e.g., H200, B200) is available on one provider but not another

---

## Section 8: How Do I Track and Govern GPU Spend Across My Team?

### The Three Core Metrics

Without measurement, optimization is guesswork. Track these three metrics as your north stars:

**1. Cost per million tokens (inference)**
```
Cost/M tokens = (GPU_hourly_rate × hours) / (tokens_generated / 1,000,000)
```
This normalizes cost across GPU types, models, and batch sizes. A well-optimized H100 + INT4 + continuous batching setup should reach $0.01–0.10/M tokens for 70B models. Compare to OpenAI API (~$1.00–3.00/M tokens) to understand your cost advantage.

**2. GPU utilization % (efficiency)**
```
GPU utilization = (time GPU is processing) / (total billable time)
```
Target: >80% average utilization. Below 50% indicates right-sizing problems, idle instances, or lack of batching. Use `nvidia-smi dmon -s u` for real-time monitoring, or Prometheus + `dcgm-exporter` for cluster-level dashboards.

**3. Cost per training run**
```
Training run cost = GPU_hourly_rate × GPU_count × hours_to_completion
```
Track this per experiment. If hyperparameter searches are consuming 10× the budget of your final training run, that's a signal to use cheaper GPUs for exploration (L40S or A100) and only use H100 for the final run.

### Key Metrics Dashboard

| Metric | Target | Alert Threshold | Tool |
|---|---|---|---|
| GPU utilization (inference) | >80% | <50% for >30 min | Prometheus + dcgm-exporter |
| GPU utilization (training) | >70% | <40% | nvidia-smi, Weights & Biases |
| Cost per M tokens | Workload-specific | >2× baseline | Custom billing dashboard |
| Idle GPU hours | <5% of total | >15% | Cloud billing API + custom script |
| Spot interruptions per week | <5 | >10 | Cloud CloudWatch / Stackdriver |
| Reserved utilization | >75% | <60% | Cloud billing console |
| Egress cost % of total | <10% | >20% | Cloud Cost Explorer |

### Budget Alerts and Spend Limits

**AWS:**
```bash
# Set billing alert at 80% of monthly GPU budget
aws cloudwatch put-metric-alarm \
  --alarm-name "GPU-Budget-80pct" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 4000 \  # $4,000 = 80% of $5,000 budget
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:gpu-budget-alerts
```

**GCP Budget Alerts:**
- Console → Billing → Budgets & Alerts
- Set budget at project or label level (use labels like `team=nlp`, `env=prod`)
- Alert at 50%, 90%, 100% thresholds

**Tag/label strategy** (implement before spend scales):
```
team: nlp | cv | infra | research
env: dev | staging | prod
project: gpt4-finetune | recommendation-v3 | experiment-123
cost-center: engineering | research | product
```

### Team-Level GPU Allocation Strategies

**Namespace-based quotas (Kubernetes):**
```yaml
# ResourceQuota per team namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota-nlp-team
  namespace: nlp
spec:
  hard:
    requests.nvidia.com/gpu: "8"    # Max 8 GPUs requested at once
    limits.nvidia.com/gpu: "8"
```

**Showback vs. chargeback:**
- **Showback:** Report GPU cost per team without affecting their budget. Builds cost-awareness culture with no friction. Start here.
- **Chargeback:** Deduct GPU costs from team's allocated budget. Drives rigorous right-sizing but adds overhead. Use after showback culture is established.

**GPU time banking:**
- Allocate each team a monthly GPU-hour budget (e.g., 500 H100-hours = ~$1,750/mo at reserved rates)
- Teams can "borrow" from future months but must justify overruns
- Unused hours expire (no rollover incentives misaligned with fiscal year timing)

**FinOps review cadence:**
- **Weekly:** Utilization anomalies, new idle instances, spot interruption rate
- **Monthly:** Cost per team/project, reserved vs. on-demand mix, quantization opportunities
- **Quarterly:** Reserved capacity commitments, GPU tier right-sizing review, provider contract renewal

### Monitoring Stack Reference

```yaml
# docker-compose snippet for GPU observability
services:
  dcgm-exporter:
    image: nvcr.io/nvidia/k8s/dcgm-exporter:3.3.5-3.4.1-ubuntu22.04
    runtime: nvidia
    ports: ["9400:9400"]
    # Exposes: DCGM_FI_DEV_GPU_UTIL, DCGM_FI_DEV_MEM_USED, 
    #          DCGM_FI_DEV_POWER_USAGE per GPU
    
  prometheus:
    image: prom/prometheus:v2.48.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana:10.2.0
    # Import dashboard ID 12239 (NVIDIA DCGM Exporter Dashboard)
```

**Key Prometheus queries for GPU cost governance:**
```promql
# Average GPU utilization across fleet
avg(DCGM_FI_DEV_GPU_UTIL) by (kubernetes_node)

# GPUs below 50% utilization for more than 30 min (right-sizing candidates)
min_over_time(DCGM_FI_DEV_GPU_UTIL[30m]) < 50

# Memory utilization (signals quantization opportunity if consistently <60%)
avg(DCGM_FI_DEV_MEM_USED) / avg(DCGM_FI_DEV_FB_TOTAL) * 100
```

---

## Quick Wins Summary

These are the changes you can make this week, ranked by expected ROI:

| Technique | Effort Level | Potential Savings | Time to Implement | Prerequisites |
|---|---|---|---|---|
| **Shut down idle GPUs / add auto-shutdown** | Low | 10–30% of monthly bill | 1 day | Access to cloud console or infra code |
| **Switch on-demand to reserved (for baseline load)** | Low (just commit) | 35–50% on committed capacity | 1 hour | 60%+ utilization confirmed |
| **Right-size GPU tier** (e.g., L4 for 7B models instead of H100) | Low | 50–70% on those workloads | 1 day | Profile model VRAM + latency requirements |
| **Enable FP8 quantization** (H100/H200 only, near-lossless) | Low | ~50% (half the GPU count) | 1–2 days | H100+ hardware; vLLM or TGI with FP8 flag |
| **Apply INT4 quantization (AWQ)** to serving stack | Medium | 50–75% (tier change possible) | 2–5 days | Accuracy validation on your specific workload |
| **Deploy vLLM with continuous batching** | Medium | 40–60% per-token cost | 1–3 days | Containerized inference stack |
| **Move training to spot instances with checkpointing** | Medium | 30–65% on training spend | 3–5 days | Checkpoint infrastructure (S3 + PyTorch Lightning or equivalent) |
| **Provider arbitrage** (benchmark RunPod/Vast.ai vs. AWS/GCP) | Medium | 20–55% on GPU hourly rate | 1 week | Containerized workloads, portable storage |
| **Enable MIG partitioning for small-model inference** | Medium | 50–80% (density improvement) | 2–3 days | A100 or H100; Kubernetes GPU operator |
| **Implement batch processing** (batch size 16–32 for async jobs) | Medium | 60–85% per-token (async) | 3–7 days | Async job queue (Celery, Ray, SQS) |
| **Tag all resources + set up cost dashboard** | Low | Indirect (enables all other savings) | 1 day | Cloud billing API access |

---

## Cross-References (ai-infra-index)

- [`specs/gpu-specifications.md`](gpu-specifications.md) — Full GPU hardware specs (NVIDIA, AMD, Intel)
- [`specs/cloud-gpu-pricing.md`](cloud-gpu-pricing.md) — Multi-provider cloud pricing tables
- [`specs/model-gpu-sizing.md`](model-gpu-sizing.md) — Model-to-GPU VRAM requirements and configuration guide
- [`specs/inference-benchmarks.md`](inference-benchmarks.md) — MLPerf results and per-model throughput data
- [`specs/training-costs.md`](training-costs.md) — Training cost estimates by model size and scale
- [`specs/networking-interconnects.md`](networking-interconnects.md) — NVLink, InfiniBand, and multi-GPU networking
- [`specs/buy-vs-rent-decision-framework.md`](buy-vs-rent-decision-framework.md) — Buy vs. rent GPU infrastructure decision framework
- [`data/cloud-pricing.json`](../data/cloud-pricing.json) — Live cloud GPU pricing data (auto-updated hourly)

---

## Sources

- [IntuitionLabs: H100 Rental Prices Compared (Feb 2026)](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison)
- [Introl: GPU Cloud Prices Collapse, H100 Market December 2025](https://introl.com/blog/gpu-cloud-price-collapse-h100-market-december-2025)
- [Introl: Spot Instances and Preemptible GPUs — AI Cost Savings](https://introl.com/blog/spot-instances-preemptible-gpus-ai-cost-savings)
- [Introl: vLLM Production Deployment — Inference Serving Architecture](https://introl.com/blog/vllm-production-deployment-inference-serving-architecture)
- [Oracle Cloud: Cost-Efficient LLM Serving with Quantization (Jun 2025)](https://blogs.oracle.com/cloud-infrastructure/cost-efficient-llm-serving-with-quantization)
- [AIMultiple: LLM Quantization Benchmark BF16 vs FP8 vs INT4 (Jan 2026)](https://research.aimultiple.com/llm-quantization/)
- [AWS: Accelerating LLM Inference with AWQ and GPTQ on SageMaker AI (Jan 2026)](https://aws.amazon.com/blogs/machine-learning/accelerating-llm-inference-with-post-training-weight-and-activation-using-awq-and-gptq-on-amazon-sagemaker-ai/)
- [AWS: Navigating GPU Challenges — Cost Optimizing AI Workloads (Jun 2025)](https://aws.amazon.com/blogs/aws-cloud-financial-management/navigating-gpu-challenges-cost-optimizing-ai-workloads-on-aws/)
- [AWS HyperPod: MIG Support for Generative AI (Nov 2025)](https://aws.amazon.com/blogs/machine-learning/hyperpod-now-supports-multi-instance-gpu-to-maximize-gpu-utilization-for-generative-ai-tasks/)
- [CUDO Compute: Real-World GPU Benchmarks H100 vs A100 vs L40S](https://www.cudocompute.com/blog/real-world-gpu-benchmarks)
- [AceCloud: NVIDIA H200 vs H100 vs A100 vs L40S vs L4 GPUs Compared (Feb 2026)](https://acecloud.ai/blog/nvidia-h200-vs-h100-vs-a100-vs-l40s-vs-l4/)
- [Fluence: Best Cloud GPU Providers for AI 2026](https://www.fluence.network/blog/best-cloud-gpu-providers-ai/)
- [Northflank: Cheapest Cloud GPU Providers 2026](https://northflank.com/blog/cheapest-cloud-gpu-providers)
- [GMI Cloud: H100 GPU Pricing 2025 — Cloud vs. On-Premise](https://www.gmicloud.ai/blog/h100-gpu-pricing-2025-cloud-vs-on-premise-cost-analysis)
- [Memorysolution: TCO Analysis — Cloud vs. On-Premises](https://www.memorysolution.de/en/cloud-or-n-premises-what-really-pays-off)
- [Spheron: GPU Cloud Cost Optimization Playbook (Feb 2026)](https://www.spheron.network/blog/gpu-cost-optimization-playbook/)
- [CrazyDomains Cloud: Multi-Cloud for AI Workloads (Feb 2026)](https://crazydomains.cloud/multi-cloud-for-ai-workloads-costs-and-latency-tradeoffs-wit/)
- [LinkedIn: Optimizing NVIDIA GPU Utilization for LLM Inference](https://www.linkedin.com/pulse/optimizing-nvidia-gpu-utilization-llm-inference-deep-dive-markevich-rqcge)
- [RunPod: AI Model Quantization Guide (Jul 2025)](https://www.runpod.io/articles/guides/ai-model-quantization-reducing-memory-usage-without-sacrificing-performance)
- [Red Hat: Meet vLLM — Faster, More Efficient LLM Inference (Mar 2025)](https://www.redhat.com/en/blog/meet-vllm-faster-more-efficient-llm-inference-and-serving)
- [LocalAIMaster: Cloud GPU vs Local Hardware Calculator (Oct 2025)](https://localaimaster.com/tutorials/cloud-vs-local-calculator)
