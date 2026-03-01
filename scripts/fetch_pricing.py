#!/usr/bin/env python3
"""
fetch_pricing.py - Automated GPU cloud pricing fetcher
Runs hourly via GitHub Actions to update data/cloud-pricing.json

Sources:
- Azure Retail Prices API (public, no auth required)
- Lambda Labs API (public, no auth required)

Note: AWS and GCP bulk pricing APIs require large downloads or auth.
We fetch from Azure and Lambda directly, and maintain manual data for
AWS/GCP/CoreWeave/Together AI from their published pricing pages.
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# Config
DATA_DIR = Path(__file__).parent.parent / "data"
PRICING_FILE = DATA_DIR / "cloud-pricing.json"

GPU_INSTANCE_MAP = {
    "azure": {
        "Standard_ND96isr_H100_v5": {
            "gpu_model": "NVIDIA H100 SXM",
            "gpu_count": 8,
            "gpu_memory_gb": 640,
        },
        "Standard_ND96amsr_A100_v4": {
            "gpu_model": "NVIDIA A100 80GB",
            "gpu_count": 8,
            "gpu_memory_gb": 640,
        },
        "Standard_ND96asr_v4": {
            "gpu_model": "NVIDIA A100 40GB",
            "gpu_count": 8,
            "gpu_memory_gb": 320,
        },
    },
}


def fetch_json(url, timeout=30):
    """Fetch JSON from URL with error handling."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "ai-infra-index/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  WARNING: Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_azure_pricing():
    """Fetch Azure Retail Prices for GPU VMs."""
    print("Fetching Azure pricing...")
    instances = []
    for vm_size, meta in GPU_INSTANCE_MAP["azure"].items():
        url = (
            "https://prices.azure.com/api/retail/prices"
            "?api-version=2023-01-01-preview"
            "&$filter=serviceName eq 'Virtual Machines'"
            f" and armSkuName eq '{vm_size}'"
            " and priceType eq 'Consumption'"
            " and armRegionName eq 'eastus'"
        )
        data = fetch_json(url)
        if not data:
            continue
        items = data.get("Items", [])
        for item in items:
            product_name = item.get("productName", "")
            if "Windows" in product_name:
                continue
            if item.get("type") != "Consumption":
                continue
            price = item.get("retailPrice", 0)
            if price <= 0:
                continue
            instances.append({
                "instance_type": vm_size,
                "gpu_model": meta["gpu_model"],
                "gpu_count": meta["gpu_count"],
                "gpu_memory_gb": meta["gpu_memory_gb"],
                "on_demand_hourly": round(price, 4),
                "spot_hourly": None,
                "region": "eastus",
                "availability": "available",
                "source": "Azure Retail Prices API",
                "fetched_at": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
            })
            break  # Take first matching Linux price
    print(f"  Azure: {len(instances)} instances fetched")
    return instances


def fetch_lambda_pricing():
    """Fetch Lambda Labs public instance type pricing."""
    print("Fetching Lambda Labs pricing...")
    url = "https://cloud.lambdalabs.com/api/v1/instance-types"
    data = fetch_json(url)
    if not data or "data" not in data:
        print("  Lambda: API unavailable or no data")
        return []
    instances = []
    for name, info in data.get("data", {}).items():
        specs = info.get("instance_type", {})
        price_cents = specs.get("price_cents_per_hour", 0)
        if price_cents <= 0:
            continue
        price = price_cents / 100.0
        desc = specs.get("description", "")
        gpu_count = specs.get("specs", {}).get("gpus", 1)
        vcpus = specs.get("specs", {}).get("vcpus", 0)
        ram = specs.get("specs", {}).get("ram_gib", 0)
        storage = specs.get("specs", {}).get("storage_gib", 0)
        # Determine availability from regions
        regions = info.get("regions_with_capacity_available", [])
        avail = "available" if len(regions) > 0 else "sold_out"
        instances.append({
            "instance_type": name,
            "gpu_model": desc,
            "gpu_count": gpu_count,
            "gpu_memory_gb": None,
            "vcpus": vcpus,
            "ram_gb": ram,
            "storage_gb": storage,
            "on_demand_hourly": round(price, 4),
            "spot_hourly": None,
            "region": regions[0].get("name", "unknown") if regions else "none",
            "availability": avail,
            "source": "Lambda Labs API",
            "fetched_at": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
        })
    print(f"  Lambda: {len(instances)} instances fetched")
    return instances


def update_pricing_file(live_data):
    """Merge live-fetched data into existing pricing file."""
    if PRICING_FILE.exists():
        with open(PRICING_FILE, "r") as f:
            existing = json.load(f)
    else:
        existing = {"metadata": {}, "providers": [], "price_history": {}}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Update metadata
    existing["metadata"]["last_updated"] = now
    existing["metadata"]["update_frequency"] = "hourly"
    existing["metadata"]["script_version"] = "1.1.0"
    existing["metadata"]["sources"] = [
        "Azure Retail Prices API",
        "Lambda Labs API",
        "AWS (manual)",
        "GCP (manual)",
        "CoreWeave (manual)",
        "Together AI (manual)",
    ]

    # Build provider map from existing data
    provider_map = {}
    for p in existing.get("providers", []):
        provider_map[p["provider"]] = p

    # Merge live-fetched provider data
    for provider_name, instances in live_data.items():
        if not instances:
            continue
        if provider_name in provider_map:
            provider_map[provider_name]["instances"] = instances
            provider_map[provider_name]["last_fetched"] = now
            provider_map[provider_name]["fetch_method"] = "api"
        else:
            provider_map[provider_name] = {
                "provider": provider_name,
                "instances": instances,
                "last_fetched": now,
                "fetch_method": "api",
            }

    existing["providers"] = list(provider_map.values())

    # Write back
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PRICING_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"Updated {PRICING_FILE}")


def main():
    start = datetime.now(timezone.utc)
    print(f"Starting pricing fetch at {start.isoformat()}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Pricing file: {PRICING_FILE}")
    print()

    live_data = {}

    # Fetch from Azure (public API, no auth)
    try:
        azure_instances = fetch_azure_pricing()
        if azure_instances:
            live_data["Microsoft Azure"] = azure_instances
    except Exception as e:
        print(f"  ERROR fetching Azure: {e}", file=sys.stderr)

    # Fetch from Lambda Labs (public API, no auth)
    try:
        lambda_instances = fetch_lambda_pricing()
        if lambda_instances:
            live_data["Lambda"] = lambda_instances
    except Exception as e:
        print(f"  ERROR fetching Lambda: {e}", file=sys.stderr)

    print()
    total = sum(len(v) for v in live_data.values())
    print(f"Fetched {total} live instance pricing records")
    print(f"Providers updated: {list(live_data.keys())}")

    # Update the pricing file
    update_pricing_file(live_data)

    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
