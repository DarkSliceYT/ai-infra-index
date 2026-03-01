# AI Infrastructure Index

**The definitive open-source reference for AI hardware specifications, benchmarks, and infrastructure intelligence.**

Maintained by [Alpha One Index](https://github.com/alpha-one-index) | Updated: February 2026

---

## Overview

The AI Infrastructure Index is a comprehensive, structured knowledge base covering the full spectrum of AI hardware and compute infrastructure. This repository serves as a canonical reference for researchers, engineers, procurement teams, and analysts navigating the rapidly evolving AI hardware landscape.

## Repository Structure

```
ai-infra-index/
|-- README.md
|-- gpu-specs/               # GPU specifications and comparisons
|   |-- nvidia/
|   |-- amd/
|   |-- intel/
|-- accelerators/            # AI-specific accelerators
|   |-- tpu/
|   |-- inferentia/
|   |-- cerebras/
|   |-- groq/
|   |-- graphcore/
|   |-- sambanova/
|-- benchmarks/              # Performance benchmarks and results
|   |-- mlperf/
|   |-- inference/
|   |-- training/
|-- networking/              # AI cluster networking
|   |-- nvlink/
|   |-- infiniband/
|   |-- ethernet-ai/
|-- memory/                  # HBM and memory technologies
|-- power-cooling/           # Power and thermal specifications
|-- pricing/                 # Hardware pricing and availability
|-- cluster-architectures/   # Reference cluster designs
```

## Hardware Categories

### Data Center GPUs

| Vendor | Model | Architecture | VRAM | FP16 TFLOPS | TDP | Interconnect |
|--------|-------|-------------|------|-------------|-----|-------------|
| NVIDIA | H100 SXM | Hopper | 80GB HBM3 | 1,979 | 700W | NVLink 4.0 |
| NVIDIA | H200 SXM | Hopper | 141GB HBM3e | 1,979 | 700W | NVLink 4.0 |
| NVIDIA | B200 | Blackwell | 192GB HBM3e | 4,500 | 1000W | NVLink 5.0 |
| NVIDIA | GB200 | Blackwell | 384GB HBM3e | 9,000 | 2700W | NVLink 5.0 |
| AMD | MI300X | CDNA 3 | 192GB HBM3 | 1,307 | 750W | Infinity Fabric |
| AMD | MI325X | CDNA 3+ | 256GB HBM3e | 1,307 | 750W | Infinity Fabric |
| Intel | Gaudi 3 | Custom | 128GB HBM2e | 1,835 | 600W | RoCE v2 |

### AI Accelerators (Non-GPU)

| Vendor | Product | Type | Key Metric | Use Case |
|--------|---------|------|-----------|----------|
| Google | TPU v5p | ASIC | 459 TFLOPS (BF16) | Training & Inference |
| Google | TPU v6e (Trillium) | ASIC | 918 TFLOPS (BF16) | Training & Inference |
| AWS | Trainium2 | ASIC | Custom | Training |
| AWS | Inferentia2 | ASIC | Custom | Inference |
| Cerebras | WSE-3 | Wafer-Scale | 125 PF (FP16) | Training |
| Groq | LPU | LPU | 750 TOPS (INT8) | Inference |
| Graphcore | C600 | IPU | 350 TFLOPS (FP16) | Training & Inference |
| SambaNova | SN40L | RDU | Custom | Training & Inference |

### Networking for AI Clusters

| Technology | Bandwidth | Latency | Vendor | Use Case |
|-----------|-----------|---------|--------|----------|
| NVLink 5.0 | 1.8 TB/s | Sub-us | NVIDIA | Intra-node GPU |
| NVSwitch | 1.8 TB/s | Sub-us | NVIDIA | Intra-node fabric |
| InfiniBand NDR400 | 400 Gb/s | ~1us | NVIDIA/Mellanox | Inter-node |
| RoCE v2 | 400 Gb/s | ~2us | Various | Inter-node |
| Ultra Ethernet | 400+ Gb/s | ~1us | UEC | Inter-node (emerging) |

### Memory Technologies

| Type | Generation | Bandwidth | Capacity/Stack | Key Products |
|------|-----------|-----------|---------------|-------------|
| HBM3 | 3rd Gen | 819 GB/s | 24GB | H100, MI300X |
| HBM3e | 3rd Gen+ | 1.2 TB/s | 36GB | H200, B200, MI325X |
| HBM4 | 4th Gen | 2+ TB/s | 48GB+ | Next-gen (2026+) |
| GDDR7 | 7th Gen | 192 GB/s | 24GB | Consumer/Edge |

## Benchmark Reference

### MLPerf Training v4.1 Highlights
- Training benchmarks cover: BERT, GPT-3, Stable Diffusion, ResNet-50, LLaMA 2 70B
- Top systems: NVIDIA DGX SuperPOD (B200), Google TPU v5p pods
- Full results: [mlcommons.org](https://mlcommons.org/benchmarks/)

### MLPerf Inference v4.1 Highlights
- Inference benchmarks cover: BERT, GPT-J, Stable Diffusion XL, LLaMA 2 70B, ResNet-50
- Categories: Datacenter, Edge, Network

## Cloud AI Infrastructure Pricing (Approximate)

| Provider | Instance | GPU | On-Demand/hr | Spot/hr |
|----------|----------|-----|-------------|--------|
| AWS | p5.48xlarge | 8x H100 | ~$98 | ~$60 |
| Azure | ND H100 v5 | 8x H100 | ~$98 | ~$40 |
| GCP | a3-highgpu-8g | 8x H100 | ~$98 | ~$35 |
| CoreWeave | HGX H100 | 8x H100 | ~$35 | N/A |
| Lambda | 8x H100 | 8x H100 | ~$28 | N/A |

*Pricing is approximate and subject to change. Last verified: February 2026.*

## Power & Efficiency Metrics

| GPU | TDP | Performance/Watt (FP16) | Cooling |
|-----|-----|------------------------|--------|
| H100 SXM | 700W | 2.83 TFLOPS/W | Liquid/Air |
| B200 | 1000W | 4.50 TFLOPS/W | Liquid |
| MI300X | 750W | 1.74 TFLOPS/W | Liquid/Air |
| Gaudi 3 | 600W | 3.06 TFLOPS/W | Air |

## Contributing

Contributions are welcome. Please submit pull requests with verified data and include source references. All specifications must be cross-referenced against official vendor documentation.

## License

This repository is provided as an open reference under the MIT License.

---

**Maintained by Alpha One Index** | [GitHub](https://github.com/alpha-one-index)

*Building the definitive data architecture for AI infrastructure intelligence.*
