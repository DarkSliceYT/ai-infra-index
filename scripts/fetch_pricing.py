#!/usr/bin/env python3
"""
fetch_pricing.py - Automated GPU cloud pricing fetcher
Runs hourly via GitHub Actions to update data/cloud-pricing.json

Sources:
- AWS EC2 Pricing API
- GCP Cloud Pricing API
- Azure Retail Prices API
- Lambda Labs API
- CoreWeave public pricing
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "data"
PRICING_FILE = DATA_DIR / "cloud-pricing.json"

GPU_INSTANCE_MAP = {
    "aws": {
        "p5.48xlarge":   {"gpu_model": "NVIDIA H100 SXM", "gpu_count": 8, "gpu_memory_gb": 640},
        "p4d.24xlarge":  {"gpu_model": "NVIDIA A100 40GB", "gpu_count": 8, "gpu_memory_gb": 320},
        "p4de.24xlarge": {"gpu_model": "NVIDIA A100 80GB", "gpu_count": 8, "gpu_memory_gb": 640},
        "g6.48xlarge":   {"gpu_model": "NVIDIA L4",         "gpu_count": 8, "gpu_memory_gb": 192},
        "g5.48xlarge":   {"gpu_model": "NVIDIA A10G",       "gpu_count": 8, "gpu_memory_gb": 192},
    },
    "gcp": {
        "a3-highgpu-8g":  {"gpu_model": "NVIDIA H100 SXM",  "gpu_count": 8,  "gpu_memory_gb": 640},
        "a2-ultragpu-8g": {"gpu_model": "NVIDIA A100 80GB", "gpu_count": 8,  "gpu_memory_gb": 640},
        "a2-highgpu-8g":  {"gpu_model": "NVIDIA A100 40GB", "gpu_count": 8,  "gpu_memory_gb": 320},
        "g2-standard-96": {"gpu_model": "NVIDIA L4",         "gpu_count": 8,  "gpu_memory_gb": 192},
    },
    "azure": {
        "Standard_ND96isr_H100_v5":  {"gpu_model": "NVIDIA H100 SXM",  "gpu_count": 8, "gpu_memory_gb": 640},
        "Standard_ND96amsr_A100_v4": {"gpu_model": "NVIDIA A100 80GB", "gpu_count": 8, "gpu_memory_gb": 640},
        "Standard_ND96asr_v4":       {"gpu_model": "NVIDIA A100 40GB", "gpu_count": 8, "gpu_memory_gb": 320},
    },
}


def fetch_json(url: str, timeout: int = 30) -> dict | None:
    """Fetch JSON from URL with error handling."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ai-infra-index/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, Exception) as e:
        print(f"  WARNING: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_aws_pricing(region: str = "us-east-1") -> list[dict]:
    """Fetch AWS EC2 on-demand pricing for GPU instances."""
    print("Fetching AWS pricing...")
    instances = []
    url = (
        f"https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/"
        f"{region}/index.json"
    )
    # AWS pricing file is very large; use the bulk API filter approach
    filter_url = (
        "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/"
        f"{region}/index.json"
    )
    data = fetch_json(filter_url)
    if not data:
        return instances

    products = data.get("products", {})
    terms = data.get("terms", {}).get("OnDemand", {})

    target_types = set(INSTANCE_MAP["aws"].keys()) if "aws" in INSTANCE_MAP else set(GPU_INSTANCE_MAP["aws"].keys())

    for sku, product in products.items():
        attrs = product.get("attributes", {})
        itype = attrs.get("instanceType", "")
        if itype not in target_types:
            continue
        if attrs.get("operatingSystem") != "Linux":
            continue
        if attrs.get("tenancy") != "Shared":
            continue
        # Get price
        price = None
        for term_sku, term_data in terms.get(sku, {}).items():
            for dim_key, dim_val in term_data.get("priceDimensions", {}).items():
                usd = float(dim_val["pricePerUnit"].get("USD", 0))
                if usd > 0:
                    price = usd
                    break
            if price:
                break
        if price is None:
            continue
        meta = GPU_INSTANCE_MAP["aws"].get(itype, {})
        instances.append({
            "instance_type": itype,
            "gpu_model": meta.get("gpu_model", attrs.get("gpu", "Unknown")),
            "gpu_count": meta.get("gpu_count", int(attrs.get("gpuCount", 1))),
            "gpu_memory_gb": meta.get("gpu_memory_gb"),
            "vcpus": int(attrs.get("vcpu", 0)),
            "ram_gb": attrs.get("memory", "").replace(" GiB", ""),
            "on_demand_hourly": round(price, 4),
            "region": region,
        })
    return instances


def fetch_gcp_pricing() -> list[dict]:
    """Fetch GCP Compute Engine GPU instance pricing."""
    print("Fetching GCP pricing...")
    instances = []
    url = (
        "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json"
    )
    data = fetch_json(url)
    if not data:
        return instances
    gcp_prices = data.get("gcp_price_list", {})
    for itype, meta in GPU_INSTANCE_MAP["gcp"].items():
        key = f"CP-COMPUTEENGINE-{itype.upper()}"
        price_data = gcp_prices.get(key, {})
        us_price = price_data.get("us", price_data.get("us-central1"))
        if not us_price:
            continue
        instances.append({
            "instance_type": itype,
            "gpu_model": meta["gpu_model"],
            "gpu_count": meta["gpu_count"],
            "gpu_memory_gb": meta["gpu_memory_gb"],
            "on_demand_hourly": round(float(us_price), 4),
            "region": "us-central1",
        })
    return instances


def fetch_azure_pricing() -> list[dict]:
    """Fetch Azure Retail Prices for GPU VMs."""
    print("Fetching Azure pricing...")
    instances = []
    for vm_size, meta in GPU_INSTANCE_MAP["azure"].items():
        url = (
            f"https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview"
            f"&$filter=serviceName eq 'Virtual Machines' and "
            f"armSkuName eq '{vm_size}' and "
            f"priceType eq 'Consumption' and "
            f"armRegionName eq 'eastus'"
        )
        data = fetch_json(url)
        if not data:
            continue
        items = data.get("Items", [])
        for item in items:
            if item.get("type") == "Consumption" and "Windows" not in item.get("productName", ""):
                instances.append({
                    "instance_type": vm_size,
                    "gpu_model": meta["gpu_model"],
                    "gpu_count": meta["gpu_count"],
                    "gpu_memory_gb": meta["gpu_memory_gb"],
                    "on_demand_hourly": round(item.get("retailPrice", 0), 4),
                    "region": "eastus",
                })
                break
    return instances


def fetch_lambda_pricing() -> list[dict]:
    """Fetch Lambda Labs public pricing."""
    print("Fetching Lambda Labs pricing...")
    url = "https://cloud.lambdalabs.com/api/v1/instance-types"
    data = fetch_json(url)
    if not data:
        return []
    instances = []
    for name, info in data.get("data", {}).items():
        specs = info.get("instance_type", {})
        price_cents = info.get("regions_with_capacity_available", [{}])
        price = specs.get("price_cents_per_hour", 0) / 100
        gpu_info = specs.get("gpu", {})
        instances.append({
            "instance_type": name,
            "gpu_model": f"NVIDIA {gpu_info.get('name', 'Unknown')}",
            "gpu_count": specs.get("gpus", 1),
            "gpu_memory_gb": gpu_info.get("memory_gib"),
            "vcpus": specs.get("vcpus"),
            "ram_gb": specs.get("memory_gib"),
            "on_demand_hourly": round(price, 4),
            "region": "us-south-1",
        })
    return instances


def update_pricing_file(new_data: dict) -> None:
    """Load existing file, merge new prices, update timestamp, write back."""
    if PRICING_FILE.exists():
        with open(PRICING_FILE, "r") as f:
            existing = json.load(f)
    else:
        existing = {"metadata": {}, "providers": [], "price_history": {}}

    # Update metadata timestamp
    existing["metadata"]["last_updated"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    existing["metadata"]["update_frequency"] = "hourly"
    existing["metadata"]["script_version"] = "1.0.0"

    # Merge provider data
    provider_map = {p["provider"]: p for p in existing.get("providers", [])}
    for provider_name, provider_instances in new_data.items():
        if not provider_instances:
            continue
        if provider_name not in provider_map:
            provider_map[provider_name] = {"provider": provider_name, "instances": []}
        # Replace instances for this provider with fresh data
        provider_map[provider_name]["instances"] = provider_instances
    existing["providers"] = list(provider_map.values())

    with open(PRICING_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"Updated {PRICING_FILE}")


def main():
    print(f"Starting pricing fetch at {datetime.now(timezone.utc).isoformat()}")

    new_data = {
        "AWS": fetch_aws_pricing(),
        "Google Cloud": fetch_gcp_pricing(),
        "Microsoft Azure": fetch_azure_pricing(),
        "Lambda": fetch_lambda_pricing(),
    }

    total = sum(len(v) for v in new_data.values())
    print(f"Fetched {total} instance pricing records")

    update_pricing_file(new_data)
    print("Done.")


if __name__ == "__main__":
    main()
