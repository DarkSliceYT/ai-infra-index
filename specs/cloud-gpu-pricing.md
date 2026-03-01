# Cloud GPU Pricing Index

> Comprehensive pricing comparison for AI/ML GPU instances across major cloud providers.
> Last verified: 2026-02-28 | Updated monthly

---

## How to Use This Index

This document tracks on-demand per-GPU-hour pricing for AI training and inference GPUs across hyperscale and specialist cloud providers. All prices are in USD and verified against provider pricing pages. Spot/preemptible pricing is noted separately where available.

---

## Pricing Summary — Current Generation GPUs

### NVIDIA H100 80GB (SXM/HGX)

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Region | Last Verified |
|---|---|---|---|---|---|
| AWS (P5) | p5.48xlarge | $3.93 | 8 | us-east-1 | 2026-02-28 |
| Google Cloud (A3-High) | a3-highgpu-8g | $3.67 | 8 | us-central1 | 2026-02-28 |
| Microsoft Azure | ND H100 v5 | $3.50–$5.00 | 8 | East US | 2026-02-28 |
| CoreWeave | HGX H100 | $6.15 | 8 | US-East | 2026-02-28 |
| Lambda Labs | On-demand | $2.99 | 8 | us-west | 2026-02-28 |
| RunPod | Community Cloud | $2.49 | 1 | Various | 2026-02-28 |
| GMI Cloud | H100 SXM | $2.10 | 1 | US | 2026-02-28 |
| Vast.ai | Marketplace | $1.87–$3.50 | 1 | Various | 2026-02-28 |

**Price Range:** $1.87–$6.15/GPU-hr on-demand
**Spot/Preemptible:** AWS ~$2.50/hr | GCP ~$2.25/hr

### NVIDIA H200 141GB

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Region | Last Verified |
|---|---|---|---|---|---|
| CoreWeave | HGX H200 | $6.31 | 8 | US-East | 2026-02-28 |
| Lambda Labs | On-demand | $3.29 | 1 | us-west | 2026-02-28 |
| GMI Cloud | H200 Container | $3.35 | 1 | US | 2026-02-28 |
| Fluence | Decentralized | $2.56–$5.35 | 1 | Various | 2026-02-28 |

**Price Range:** $2.56–$6.31/GPU-hr on-demand

### NVIDIA B200 192GB

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Region | Last Verified |
|---|---|---|---|---|---|
| AWS (P6) | p6.48xlarge | ~$14.00 | 8 | us-east-1 | 2026-02-28 |
| Lambda Labs | On-demand | $4.99 | 8 | us-west | 2026-02-28 |
| CoreWeave | HGX B200 | $8.60 | 8 | US-East | 2026-02-28 |

**Price Range:** $4.99–$14.00/GPU-hr on-demand

### NVIDIA GH200 96GB

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Region | Last Verified |
|---|---|---|---|---|---|
| CoreWeave | Grace Hopper | $6.50 | 1 | US-East | 2026-02-28 |
| Lambda Labs | On-demand | $1.49 | 1 | us-west | 2026-02-28 |

---

## Previous Generation GPUs

### NVIDIA A100 80GB (SXM)

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Region | Last Verified |
|---|---|---|---|---|---|
| AWS (P4d) | p4d.24xlarge | $2.75 | 8 | us-east-1 | 2026-02-28 |
| Google Cloud (A2) | a2-ultragpu-8g | $2.93 | 8 | us-central1 | 2026-02-28 |
| CoreWeave | A100 SXM | $2.70 | 8 | US-East | 2026-02-28 |
| Lambda Labs | On-demand | $1.79 | 8 | us-west | 2026-02-28 |
| Vast.ai | Marketplace | $0.80–$1.50 | 1 | Various | 2026-02-28 |

**Price Range:** $0.80–$2.93/GPU-hr on-demand
**Spot/Preemptible:** GCP ~$1.57/hr | AWS ~$1.40/hr

### NVIDIA A100 40GB (PCIe)

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Last Verified |
|---|---|---|---|---|
| Lambda Labs | On-demand | $1.29 | 1 | 2026-02-28 |
| AWS (P4de) | p4de.24xlarge | $2.74 | 8 | 2026-02-28 |

### NVIDIA L40S 48GB

| Provider | Instance Type | Per-GPU-Hour (On-Demand) | Min GPUs | Last Verified |
|---|---|---|---|---|
| Lambda Labs | On-demand | $1.29 | 1 | 2026-02-28 |
| RunPod | Community Cloud | $0.99 | 1 | 2026-02-28 |
| CoreWeave | L40S | $1.58 | 1 | 2026-02-28 |

---

## Pricing Trends (2023–2026)

### H100 Average On-Demand Price Per GPU-Hour

| Period | Hyperscalers Avg | Specialist Avg | Market Low |
|---|---|---|---|
| Q4 2023 | $8.00–$10.00 | $4.00–$5.00 | ~$3.50 |
| Q2 2024 | $6.50–$8.00 | $3.00–$4.00 | ~$2.50 |
| Q4 2024 | $5.00–$6.50 | $2.50–$3.50 | ~$2.00 |
| Q2 2025 (post AWS cut) | $3.50–$4.50 | $2.00–$3.00 | ~$1.50 |
| Q1 2026 | $3.50–$4.00 | $1.87–$3.00 | ~$1.50 |

Key events:
- **June 2025:** AWS cut H100 (P5) pricing by ~44%, triggering industry-wide repricing
- **Late 2025:** H200 availability expanded, pushing H100 prices further down
- **Early 2026:** B200/GB200 availability begins shifting demand away from H100

---

## Provider Categories

### Hyperscale Clouds
- **AWS** — Broadest GPU instance selection; P5 (H100), P4d (A100), P6 (B200)
- **Google Cloud** — A3 (H100), A2 (A100); competitive spot pricing
- **Microsoft Azure** — ND H100 v5 series; strong enterprise integration

### Specialist GPU Clouds (Neoclouds)
- **CoreWeave** — GPU-native infrastructure; Kubernetes-based; H100/H200/B200/GB200
- **Lambda Labs** — Developer-focused; competitive single-GPU pricing; H100/H200/GH200/B200
- **RunPod** — Serverless GPU inference + on-demand; community marketplace pricing
- **Together AI** — Inference-optimized; serverless endpoints

### GPU Marketplaces
- **Vast.ai** — Peer-to-peer GPU marketplace; lowest prices, variable quality
- **Fluence** — Decentralized GPU cloud; competitive H200 pricing

### European Sovereign Cloud
- **Nebius** — EU-based; GDPR compliant; H100/A100
- **Northern Data Group (Taiga Cloud)** — EU-based; H100 availability

---

## Cost Optimization Notes

### Spot vs On-Demand Savings
| GPU | On-Demand Avg | Spot Avg | Typical Savings |
|---|---|---|---|
| H100 | $3.50 | $2.25 | 35–40% |
| A100 80GB | $2.50 | $1.40 | 40–45% |

### Reserved/Committed Pricing
- **1-year commits:** 25–40% discount vs on-demand (varies by provider)
- **3-year commits:** 40–60% discount vs on-demand
- **AWS H100 long-term:** As low as $1.90–$2.10/GPU-hr with commitments

---

## Methodology

- All prices sourced from official provider pricing pages
- Cross-referenced with GPU price aggregators (getdeploying.com, gpucompare.com, computeprices.com)
- Spot prices represent typical availability, not guaranteed
- Multi-GPU instance prices divided by GPU count for per-GPU-hour rate
- Prices exclude egress, storage, and networking costs

---

## Related Specifications

- [GPU Hardware Specifications](gpu-specifications.md) — Full technical specs for each GPU
- [AI Accelerators](ai-accelerators.md) — Non-GPU AI hardware comparison
- [Networking & Interconnects](networking-interconnects.md) — NVLink, InfiniBand, and cluster networking

---

*Part of the [AI Infrastructure Index](https://github.com/alpha-one-index/ai-infra-index) — Maintained by [Alpha One Index](https://github.com/alpha-one-index)*
