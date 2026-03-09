#!/usr/bin/env python3
"""Automated new page generator.

Reads data/cloud-pricing.json and data/gpu-specs.json to detect
coverage gaps, then generates unique Markdown pages for:
  - Per-GPU spec pages (specs/gpu/)
  - Per-provider profile pages (providers/)
  - Head-to-head GPU comparisons (comparisons/)
  - Weekly market snapshots (snapshots/)

Each page is unique because it pulls from live, hourly-updated
pricing data and per-GPU spec data.
"""

import argparse
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
PRICING_FILE = ROOT / "data" / "cloud-pricing.json"
SPECS_FILE = ROOT / "data" / "gpu-specs.json"

GPU_SPEC_DIR = ROOT / "specs" / "gpu"
PROVIDER_DIR = ROOT / "providers"
COMPARISON_DIR = ROOT / "comparisons"
SNAPSHOT_DIR = ROOT / "snapshots"

MIN_PAGES = 2
MAX_PAGES = 5


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def load_json(path: Path) -> dict:
    """Load a JSON file, return empty dict on failure."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ---------------------------------------------------------------------------
# Gap detection — find pages that don't exist yet
# ---------------------------------------------------------------------------
def find_gpu_spec_gaps(pricing: dict, specs: dict) -> list[dict]:
    """Find GPU models in our data that lack a dedicated spec page."""
    existing = {p.stem for p in GPU_SPEC_DIR.glob("*.md")}
    # Collect unique GPU models from pricing data
    gpu_models = set()
    for provider, skus in pricing.get("providers", {}).items():
        for sku in skus:
            gpu_models.add(sku.get("gpu", ""))
    # Also from gpu-specs.json
    for gpu in specs.get("gpus", []):
        gpu_models.add(gpu.get("model", ""))
    gaps = []
    for model in sorted(gpu_models):
        if not model:
            continue
        slug = slugify(model)
        if slug not in existing:
            gaps.append({"type": "gpu_spec", "model": model, "slug": slug})
    return gaps


def find_provider_gaps(pricing: dict) -> list[dict]:
    """Find providers that lack a dedicated profile page."""
    existing = {p.stem for p in PROVIDER_DIR.glob("*.md")}
    all_providers = set(pricing.get("providers", {}).keys())
    gaps = []
    for name in sorted(all_providers):
        slug = slugify(name)
        if slug not in existing:
            gaps.append({"type": "provider", "name": name, "slug": slug})
    return gaps


def find_comparison_gaps(pricing: dict) -> list[dict]:
    """Find GPU pair comparisons that don't exist yet."""
    existing = {p.stem for p in COMPARISON_DIR.glob("*.md")}
    gpu_models = set()
    for provider, skus in pricing.get("providers", {}).items():
        for sku in skus:
            gpu_models.add(sku.get("gpu", ""))
    models = sorted(m for m in gpu_models if m)
    gaps = []
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            slug = f"{slugify(a)}-vs-{slugify(b)}"
            slug_rev = f"{slugify(b)}-vs-{slugify(a)}"
            if slug not in existing and slug_rev not in existing:
                gaps.append({"type": "comparison", "gpu_a": a, "gpu_b": b, "slug": slug})
    return gaps


def find_snapshot_gap() -> list[dict]:
    """Check if this week's market snapshot exists."""
    now = datetime.now(timezone.utc)
    # ISO week format: 2026-W11
    week_label = now.strftime("%G-W%V")
    slug = f"gpu-cloud-pricing-{week_label}"
    target = SNAPSHOT_DIR / f"{slug}.md"
    if not target.exists():
        return [{"type": "snapshot", "week": week_label, "slug": slug}]
    return []



# ---------------------------------------------------------------------------
# Page generators — produce unique Markdown content
# ---------------------------------------------------------------------------
def generate_gpu_spec_page(gap: dict, pricing: dict, specs: dict) -> str:
    """Generate a per-GPU spec page with live pricing data."""
    model = gap["model"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Find spec data
    spec = {}
    for g in specs.get("gpus", []):
        if g.get("model") == model:
            spec = g
            break
    # Find pricing across providers
    provider_prices = []
    for prov, skus in pricing.get("providers", {}).items():
        for sku in skus:
            if sku.get("gpu") == model:
                price = sku.get("price_hr")
                if price:
                    provider_prices.append({"provider": prov, "price": price, "mem": sku.get("mem", "")})
    provider_prices.sort(key=lambda x: x["price"])
    # Build page
    lines = [
        f"# {model} GPU Specifications and Cloud Pricing",
        "",
        f"> Comprehensive specifications and live cloud pricing for the {model}.",
        f"*Last updated: {now} | Maintained by [Alpha One Index](https://github.com/alpha-one-index/ai-infra-index)*",
        "",
        "---",
        "",
    ]
    # Spec table
    if spec:
        lines.append("## Technical Specifications")
        lines.append("")
        lines.append("| Specification | Value |")
        lines.append("|---|---|")
        field_map = [
            ("architecture", "GPU Architecture"),
            ("process_node", "Process Node"),
            ("vram_gb", "GPU Memory (GB)"),
            ("memory_type", "Memory Type"),
            ("memory_bandwidth_tb_s", "Memory Bandwidth (TB/s)"),
            ("fp16_tflops", "FP16 Performance (TFLOPS)"),
            ("bf16_tflops", "BF16 Performance (TFLOPS)"),
            ("fp32_tflops", "FP32 Performance (TFLOPS)"),
            ("fp8_tflops", "FP8 Performance (TFLOPS)"),
            ("tdp_watts", "TDP (Watts)"),
            ("interconnect", "Interconnect"),
            ("form_factor", "Form Factor"),
            ("cuda_cores", "CUDA Cores"),
            ("tensor_cores", "Tensor Cores"),
        ]
        for key, label in field_map:
            val = spec.get(key)
            if val is not None:
                lines.append(f"| {label} | {val} |")
        lines.append("")
    # Pricing table
    if provider_prices:
        lines.append("## Cloud Pricing")
        lines.append("")
        lines.append("| Provider | Price/hr (USD) | VRAM |")
        lines.append("|---|---|---|")
        for pp in provider_prices:
            lines.append(f"| {pp['provider']} | ${pp['price']:.2f} | {pp['mem']} GB |")
        lines.append("")
        cheapest = provider_prices[0]
        lines.append(f"Lowest price: **${cheapest['price']:.2f}/hr** on {cheapest['provider']}.")
        lines.append("")
    # FAQ section
    lines.extend([
        "## FAQ",
        "",
        f"### How much does {model} cloud rental cost?",
        "",
    ])
    if provider_prices:
        lines.append(f"Cloud rental for the {model} starts at ${provider_prices[0]['price']:.2f}/hr across {len(provider_prices)} providers tracked by the Alpha One Index.")
    else:
        lines.append(f"Pricing data for the {model} is currently being collected. Check back soon.")
    lines.extend([
        "",
        f"### What is the {model} best for?",
        "",
    ])
    vram = spec.get("vram_gb", 0)
    if vram >= 80:
        lines.append(f"With {vram} GB of VRAM, the {model} is well-suited for large-scale LLM training, fine-tuning, and multi-model inference workloads.")
    elif vram >= 24:
        lines.append(f"With {vram} GB of VRAM, the {model} is a strong choice for inference, fine-tuning smaller models, and image generation workloads.")
    else:
        lines.append(f"The {model} is suitable for lightweight inference and development workloads.")
    lines.append("")
    return "\n".join(lines)


def generate_provider_page(gap: dict, pricing: dict) -> str:
    """Generate a per-provider profile page."""
    name = gap["name"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    skus = pricing.get("providers", {}).get(name, [])
    source_url = pricing.get("pricing_sources", {}).get(name, "")
    lines = [
        f"# {name} — GPU Cloud Provider Profile",
        "",
        f"> Provider overview and live GPU pricing for {name}.",
        f"*Last updated: {now} | Maintained by [Alpha One Index](https://github.com/alpha-one-index/ai-infra-index)*",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"{name} is a cloud GPU provider tracked by the Alpha One Index.",
    ]
    if source_url:
        lines.append(f"Official pricing page: [{source_url}]({source_url})")
    lines.extend(["", "## GPU Inventory", ""])
    if skus:
        lines.append("| GPU | Count | VRAM (GB) | Price/hr (USD) |")
        lines.append("|---|---|---|---|")
        sorted_skus = sorted(skus, key=lambda s: s.get("price_hr", 999))
        for sku in sorted_skus:
            price = sku.get("price_hr", "N/A")
            price_str = f"${price:.2f}" if isinstance(price, (int, float)) else str(price)
            lines.append(f"| {sku.get('gpu', 'N/A')} | {sku.get('cnt', 1)} | {sku.get('mem', 'N/A')} | {price_str} |")
        lines.append("")
        gpu_set = sorted(set(s.get("gpu", "") for s in skus if s.get("gpu")))
        lines.append(f"**{len(gpu_set)} unique GPU models** available across {len(skus)} SKUs.")
    else:
        lines.append("GPU inventory data is currently being collected.")
    lines.extend(["", "## FAQ", "", f"### What GPUs does {name} offer?", ""])
    if skus:
        gpu_list = sorted(set(s.get("gpu", "") for s in skus if s.get("gpu")))
        lines.append(f"{name} currently offers: {', '.join(gpu_list)}.")
    lines.extend(["", f"### Is {name} good for AI training?", ""])
    lines.append(f"See the pricing table above to evaluate {name} for your specific workload. Compare with other providers in our [cloud GPU pricing overview](/specs/cloud-gpu-pricing.md).")
    lines.append("")
    return "\n".join(lines)


def generate_comparison_page(gap: dict, pricing: dict, specs: dict) -> str:
    """Generate a head-to-head GPU comparison page."""
    gpu_a, gpu_b = gap["gpu_a"], gap["gpu_b"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Find specs
    spec_a, spec_b = {}, {}
    for g in specs.get("gpus", []):
        if g.get("model") == gpu_a:
            spec_a = g
        if g.get("model") == gpu_b:
            spec_b = g
    # Find cheapest prices
    def cheapest(model):
        best = None
        for prov, skus in pricing.get("providers", {}).items():
            for sku in skus:
                if sku.get("gpu") == model:
                    p = sku.get("price_hr")
                    if p and (best is None or p < best[1]):
                        best = (prov, p)
        return best
    price_a = cheapest(gpu_a)
    price_b = cheapest(gpu_b)
    lines = [
        f"# {gpu_a} vs {gpu_b} — GPU Comparison",
        "",
        f"> Side-by-side comparison of {gpu_a} and {gpu_b} specifications and cloud pricing.",
        f"*Last updated: {now} | Maintained by [Alpha One Index](https://github.com/alpha-one-index/ai-infra-index)*",
        "",
        "---",
        "",
        "## Specifications Comparison",
        "",
        f"| Spec | {gpu_a} | {gpu_b} |",
        "|---|---|---|",
    ]
    compare_fields = [
        ("architecture", "Architecture"),
        ("vram_gb", "VRAM (GB)"),
        ("memory_type", "Memory Type"),
        ("memory_bandwidth_tb_s", "Bandwidth (TB/s)"),
        ("fp16_tflops", "FP16 (TFLOPS)"),
        ("fp8_tflops", "FP8 (TFLOPS)"),
        ("fp32_tflops", "FP32 (TFLOPS)"),
        ("tdp_watts", "TDP (Watts)"),
        ("interconnect", "Interconnect"),
        ("cuda_cores", "CUDA Cores"),
        ("tensor_cores", "Tensor Cores"),
    ]
    for key, label in compare_fields:
        va = spec_a.get(key, "N/A")
        vb = spec_b.get(key, "N/A")
        lines.append(f"| {label} | {va} | {vb} |")
    lines.extend(["", "## Pricing Comparison", ""])
    lines.append(f"| GPU | Cheapest Provider | Price/hr |")
    lines.append("|---|---|---|")
    if price_a:
        lines.append(f"| {gpu_a} | {price_a[0]} | ${price_a[1]:.2f} |")
    else:
        lines.append(f"| {gpu_a} | N/A | N/A |")
    if price_b:
        lines.append(f"| {gpu_b} | {price_b[0]} | ${price_b[1]:.2f} |")
    else:
        lines.append(f"| {gpu_b} | N/A | N/A |")
    lines.extend(["", "## When to Choose Each", ""])
    vram_a = spec_a.get("vram_gb", 0)
    vram_b = spec_b.get("vram_gb", 0)
    lines.append(f"**Choose {gpu_a}** if you need {vram_a} GB VRAM and prioritize {'raw performance' if spec_a.get('fp16_tflops', 0) > spec_b.get('fp16_tflops', 0) else 'this specific GPU architecture'}.")
    lines.append("")
    lines.append(f"**Choose {gpu_b}** if you need {vram_b} GB VRAM and prioritize {'raw performance' if spec_b.get('fp16_tflops', 0) > spec_a.get('fp16_tflops', 0) else 'this specific GPU architecture'}.")
    lines.append("")
    return "\n".join(lines)


def generate_snapshot_page(gap: dict, pricing: dict) -> str:
    """Generate a weekly market snapshot page."""
    week = gap["week"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    providers = pricing.get("providers", {})
    total_skus = sum(len(v) for v in providers.values())
    # Aggregate stats
    all_prices = []
    gpu_counts = {}
    for prov, skus in providers.items():
        for sku in skus:
            p = sku.get("price_hr")
            gpu = sku.get("gpu", "")
            if p and isinstance(p, (int, float)):
                all_prices.append(p)
            if gpu:
                gpu_counts[gpu] = gpu_counts.get(gpu, 0) + 1
    lines = [
        f"# GPU Cloud Pricing Report — {week}",
        "",
        f"> Weekly snapshot of cloud GPU pricing across {len(providers)} providers.",
        f"*Generated: {now} | Maintained by [Alpha One Index](https://github.com/alpha-one-index/ai-infra-index)*",
        "",
        "---",
        "",
        "## Market Summary",
        "",
        f"- **Providers tracked**: {len(providers)}",
        f"- **Total SKUs**: {total_skus}",
        f"- **Unique GPU models**: {len(gpu_counts)}",
    ]
    if all_prices:
        lines.append(f"- **Cheapest GPU/hr**: ${min(all_prices):.2f}")
        lines.append(f"- **Most expensive GPU/hr**: ${max(all_prices):.2f}")
        lines.append(f"- **Median price/hr**: ${sorted(all_prices)[len(all_prices)//2]:.2f}")
    lines.extend(["", "## Most Available GPUs", ""])
    lines.append("| GPU | Providers Offering |")
    lines.append("|---|---|")
    for gpu, cnt in sorted(gpu_counts.items(), key=lambda x: -x[1])[:10]:
        lines.append(f"| {gpu} | {cnt} |")
    lines.extend(["", "## Cheapest Options by GPU", ""])
    lines.append("| GPU | Provider | Price/hr |")
    lines.append("|---|---|---|")
    cheapest_by_gpu = {}
    for prov, skus in providers.items():
        for sku in skus:
            gpu = sku.get("gpu", "")
            p = sku.get("price_hr")
            if gpu and p and isinstance(p, (int, float)):
                if gpu not in cheapest_by_gpu or p < cheapest_by_gpu[gpu][1]:
                    cheapest_by_gpu[gpu] = (prov, p)
    for gpu, (prov, p) in sorted(cheapest_by_gpu.items()):
        lines.append(f"| {gpu} | {prov} | ${p:.2f} |")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------
def set_output(name: str, value: str):
    """Set a GitHub Actions output variable."""
    ghout = os.environ.get("GITHUB_OUTPUT", "")
    if ghout:
        with open(ghout, "a") as f:
            f.write(f"{name}={value}\n")
    print(f"  [{name}] = {value}")


def main():
    parser = argparse.ArgumentParser(description="Generate new pages from data gaps")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--force-type", type=str, default="", help="Force page type")
    parser.add_argument("--max-pages", type=int, default=0, help="Max pages")
    args = parser.parse_args()

    pricing = load_json(PRICING_FILE)
    specs = load_json(SPECS_FILE)

    if not pricing.get("providers"):
        print("No pricing data found. Skipping.")
        set_output("count", "0")
        set_output("summary", "no data")
        return

    # Ensure output dirs exist
    for d in [GPU_SPEC_DIR, PROVIDER_DIR, COMPARISON_DIR, SNAPSHOT_DIR]:
        d.mkdir(parents=True, exist_ok=True)

    # Collect all gaps
    all_gaps = []
    if not args.force_type or args.force_type == "gpu_spec":
        all_gaps.extend(find_gpu_spec_gaps(pricing, specs))
    if not args.force_type or args.force_type == "provider":
        all_gaps.extend(find_provider_gaps(pricing))
    if not args.force_type or args.force_type == "comparison":
        all_gaps.extend(find_comparison_gaps(pricing))
    if not args.force_type or args.force_type == "snapshot":
        all_gaps.extend(find_snapshot_gap())

    if not all_gaps:
        print("No coverage gaps found. All pages up to date.")
        set_output("count", "0")
        set_output("summary", "all covered")
        return

    # Determine how many pages to create
    max_pages = args.max_pages if args.max_pages > 0 else random.randint(MIN_PAGES, MAX_PAGES)
    # Prioritize: snapshots first, then spread across types
    random.shuffle(all_gaps)
    # But always prioritize snapshots
    all_gaps.sort(key=lambda g: 0 if g["type"] == "snapshot" else 1)
    selected = all_gaps[:max_pages]

    print(f"Found {len(all_gaps)} total gaps. Generating {len(selected)} pages.")

    type_counts = {}
    created = []
    for gap in selected:
        gtype = gap["type"]
        slug = gap["slug"]

        if gtype == "gpu_spec":
            content = generate_gpu_spec_page(gap, pricing, specs)
            path = GPU_SPEC_DIR / f"{slug}.md"
        elif gtype == "provider":
            content = generate_provider_page(gap, pricing)
            path = PROVIDER_DIR / f"{slug}.md"
        elif gtype == "comparison":
            content = generate_comparison_page(gap, pricing, specs)
            path = COMPARISON_DIR / f"{slug}.md"
        elif gtype == "snapshot":
            content = generate_snapshot_page(gap, pricing)
            path = SNAPSHOT_DIR / f"{slug}.md"
        else:
            continue

        if args.dry_run:
            print(f"  [DRY RUN] Would create: {path}")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"  Created: {path}")

        type_counts[gtype] = type_counts.get(gtype, 0) + 1
        created.append(str(path))

    count = len(created)
    summary_parts = [f"{v} {k}s" for k, v in sorted(type_counts.items())]
    summary = ", ".join(summary_parts)

    set_output("count", str(count))
    set_output("summary", summary)
    set_output("files", " ".join(created))

    print(f"\nDone. {count} pages generated: {summary}")


if __name__ == "__main__":
    main()
