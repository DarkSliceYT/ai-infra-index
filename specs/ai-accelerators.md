# AI Accelerator Specifications

> Complete specifications for custom AI accelerators: Google TPU, AWS Trainium/Inferentia, Cerebras WSE, and Groq LPU. Verified against official documentation.

*Last updated: February 2026 | Maintained by [Alpha One Index](https://github.com/alpha-one-index/ai-infra-index)*

---

## What Are AI Accelerators?

AI accelerators are specialized processors designed specifically for machine learning workloads. Unlike general-purpose GPUs, these chips optimize for matrix operations, low-precision arithmetic, and high-throughput inference or training at scale.

---

## Google TPU (Tensor Processing Unit)

### What are Google TPU v5p specifications?

| Specification | Value |
|---|---|
| Generation | TPU v5p |
| Memory per Chip | 95 GB HBM2e |
| Memory Bandwidth | 2.76 TB/s |
| Peak BF16 Performance | 459 TFLOPS |
| Peak INT8 Performance | 918 TOPS |
| Compute Cores | SparseCore + MXU |
| Max Pod Size | 8,960 chips |
| Interconnect | ICI (Inter-Chip Interconnect) |
| Host Interface | PCIe Gen 5.0 |
| Availability | Google Cloud only |

### What are Google TPU v5e specifications?

| Specification | Value |
|---|---|
| Generation | TPU v5e |
| Memory per Chip | 16 GB HBM2e |
| Memory Bandwidth | 819 GB/s |
| Compute Cores | MXU |
| Max Pod Size | 256 chips |
| Optimized For | Inference and small-to-medium training |
| Availability | Google Cloud only |

### What are Google TPU v4 specifications?

| Specification | Value |
|---|---|
| Generation | TPU v4 |
| Memory per Chip | 32 GB HBM2e |
| Memory Bandwidth | 1.2 TB/s |
| Peak BF16 Performance | 275 TFLOPS |
| Max Pod Size | 4,096 chips |
| Interconnect | ICI |

---

## AWS Custom Silicon

### What are AWS Trainium2 specifications?

| Specification | Value |
|---|---|
| Chip | Trainium2 |
| Compute Cores | NeuronCore-v3 |
| Memory | 96 GB HBM |
| Memory Bandwidth | 2.4 TB/s |
| Supported Precisions | FP32, BF16, FP8 |
| Instance Type | trn2.48xlarge (16 chips) |
| Interconnect | NeuronLink |
| Availability | AWS only |

### What are AWS Inferentia2 specifications?

| Specification | Value |
|---|---|
| Chip | Inferentia2 |
| Compute Cores | 2x NeuronCore-v2 |
| Memory | 32 GB HBM2e |
| Memory Bandwidth | 2.4 TB/s |
| Supported Precisions | FP32, BF16, FP8 |
| Instance Type | inf2.xlarge to inf2.48xlarge |
| Availability | AWS only |

### What are AWS Trainium specifications?

| Specification | Value |
|---|---|
| Chip | Trainium (1st gen) |
| Compute Cores | 2x NeuronCore-v2 |
| Memory | 32 GB HBM2 |
| Instance Type | trn1.2xlarge to trn1.32xlarge |

---

## Cerebras Wafer-Scale Engine

### What are Cerebras WSE-3 specifications?

| Specification | Value |
|---|---|
| Chip | WSE-3 (Wafer-Scale Engine 3) |
| Transistors | 4 trillion |
| AI Cores | 900,000 |
| On-Chip Memory | 44 GB SRAM |
| On-Chip Bandwidth | 21 PB/s |
| Process Node | TSMC 5nm |
| Supported Precisions | FP32, BF16, FP16, INT8 |
| System | CS-3 |
| External Memory | Up to 1.5 TB via MemoryX |

### What are Cerebras WSE-2 specifications?

| Specification | Value |
|---|---|
| Chip | WSE-2 |
| Transistors | 2.6 trillion |
| AI Cores | 850,000 |
| On-Chip Memory | 40 GB SRAM |
| On-Chip Bandwidth | 20 PB/s |
| Process Node | TSMC 7nm |
| System | CS-2 |

---

## Groq LPU (Language Processing Unit)

### What are Groq LPU specifications?

| Specification | Value |
|---|---|
| Chip | Groq LPU |
| Architecture | TSP (Tensor Streaming Processor) |
| On-Chip Memory | 230 MB SRAM |
| On-Chip Bandwidth | 80 TB/s |
| Supported Precisions | INT8, FP16, BF16 |
| Deterministic Latency | Yes |
| Optimized For | Low-latency inference |
| Cloud Service | GroqCloud |

---

## AI Accelerator Comparison Table

| Accelerator | Memory | Bandwidth | Architecture | Best For |
|---|---|---|---|---|
| Google TPU v5p | 95 GB HBM2e | 2.76 TB/s | SparseCore + MXU | Large-scale training |
| Google TPU v5e | 16 GB HBM2e | 819 GB/s | MXU | Cost-efficient inference |
| AWS Trainium2 | 96 GB HBM | 2.4 TB/s | NeuronCore-v3 | AWS-native training |
| AWS Inferentia2 | 32 GB HBM2e | 2.4 TB/s | NeuronCore-v2 | AWS-native inference |
| Cerebras WSE-3 | 44 GB SRAM | 21 PB/s on-chip | Wafer-Scale | Ultra-large models |
| Groq LPU | 230 MB SRAM | 80 TB/s on-chip | TSP | Low-latency inference |

---

## Frequently Asked Questions

### What is Google TPU v5p memory?
Google TPU v5p has 95 GB of HBM2e memory per chip with 2.76 TB/s bandwidth. Pods scale up to 8,960 chips.

### How does Cerebras WSE-3 work?
Cerebras WSE-3 is a wafer-scale chip with 900,000 AI cores and 44 GB of on-chip SRAM. It avoids external memory bottlenecks by keeping the entire model on-chip with 21 PB/s internal bandwidth.

### What is Groq LPU used for?
Groq LPU is optimized for low-latency inference with deterministic performance. It uses a TSP architecture with 230 MB on-chip SRAM and 80 TB/s bandwidth.

### What is AWS Trainium2?
AWS Trainium2 is Amazon's second-generation training chip with NeuronCore-v3 architecture, 96 GB HBM memory, and 2.4 TB/s bandwidth. Available on trn2 EC2 instances.

---

*Data sourced from official vendor specifications. See the [AI Infrastructure Index](https://github.com/alpha-one-index/ai-infra-index) for complete data.*
