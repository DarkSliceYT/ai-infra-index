# AWS Data Exchange — Product Listing Draft

> Ready-to-paste copy for the ADX marketplace listing.
> Delete this file after publishing, or keep for reference.

---

## Product Name

```
AI Infrastructure GPU Cloud Pricing Index
```

## Short Description (max 100 characters)

```
Hourly-updated GPU cloud pricing across 12 providers, 66 SKUs. JSON format, auto-delivered via ADX.
```

## Long Description

```
The AI Infrastructure GPU Cloud Pricing Index provides structured, machine-readable pricing data for GPU compute instances across major cloud and specialty providers. Data is collected hourly and delivered automatically as new ADX revisions.

COVERAGE

- 12 providers: Azure, RunPod, Lambda Labs, CoreWeave, Together AI, Vast.ai, Vultr, Nebius, Oracle Cloud (OCI), Cudo Compute, Fluidstack, Paperspace
- 66 GPU SKUs including NVIDIA H100, H200, B200, A100, A10G, L40S, RTX 4090, and more
- On-demand and spot pricing where available
- Memory capacity per GPU configuration

DATA FORMAT

Each revision contains a single cloud-pricing.json file with:
- Per-provider arrays of GPU offerings
- Fields: gpu, cnt (GPU count), mem (VRAM in GB), on_demand ($/hr), spot ($/hr where available)
- Metadata: timestamp, provider count, total SKUs, methodology, source URLs

UPDATE FREQUENCY

- New revision every hour (24 revisions/day)
- Azure pricing sourced live from the Azure Retail Prices API
- All other providers curated from official pricing pages monthly, with spot prices updated hourly where APIs are available

USE CASES

- Cloud cost optimization: Compare GPU instance pricing across providers in real time
- Financial modeling: Track GPU pricing trends for infrastructure budgeting
- Procurement automation: Feed live pricing into provisioning and orchestration pipelines
- Market research: Monitor the AI compute market's pricing dynamics over time

DATA QUALITY

- Automated validation on every update (schema checks, price range validation)
- Full provenance metadata with source URLs for independent verification
- Historical snapshots retained in S3 for time-series analysis
- Open-source methodology documented at https://github.com/alpha-one-index/ai-infra-index

LICENSE

MIT License. Free for commercial and non-commercial use.
```

## Pricing Tier

```
Free
```

## Data Set Tags

```
GPU pricing, cloud computing, AI infrastructure, machine learning, NVIDIA, compute costs, cloud GPU, pricing index, H100, H200
```

## Logo / Icon

Use the SVG below. AWS Data Exchange requires a square image (minimum 150x150 px).
Export the SVG as a 500x500 PNG for upload.

### adx-logo.svg

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1a1a2e"/>
      <stop offset="100%" stop-color="#0d0d1a"/>
    </radialGradient>
    <linearGradient id="glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00d4ff"/>
      <stop offset="50%" stop-color="#0099cc"/>
      <stop offset="100%" stop-color="#006699"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#006699" stop-opacity="0.3"/>
    </linearGradient>
    <filter id="glowFilter">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="outerGlow">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="500" height="500" rx="60" fill="url(#bg)"/>

  <!-- Outer ring -->
  <circle cx="250" cy="230" r="155" fill="none" stroke="url(#glow)" stroke-width="2.5" opacity="0.6" filter="url(#outerGlow)"/>

  <!-- Inner ring -->
  <circle cx="250" cy="230" r="120" fill="none" stroke="url(#glow)" stroke-width="1.5" opacity="0.3"/>

  <!-- Stylized "A" -->
  <g filter="url(#glowFilter)">
    <!-- Left leg -->
    <line x1="195" y1="310" x2="250" y2="150" stroke="url(#glow)" stroke-width="5" stroke-linecap="round"/>
    <!-- Right leg -->
    <line x1="305" y1="310" x2="250" y2="150" stroke="url(#glow)" stroke-width="5" stroke-linecap="round"/>
    <!-- Crossbar -->
    <line x1="215" y1="265" x2="285" y2="265" stroke="url(#glow)" stroke-width="4" stroke-linecap="round"/>
    <!-- Apex dot -->
    <circle cx="250" cy="148" r="6" fill="#00d4ff" opacity="0.9"/>
  </g>

  <!-- Data flow lines (representing pricing streams) -->
  <g opacity="0.4" stroke="url(#accent)" stroke-width="1.5">
    <line x1="140" y1="180" x2="175" y2="210" stroke-linecap="round"/>
    <line x1="130" y1="230" x2="170" y2="230" stroke-linecap="round"/>
    <line x1="140" y1="280" x2="175" y2="250" stroke-linecap="round"/>
    <line x1="360" y1="180" x2="325" y2="210" stroke-linecap="round"/>
    <line x1="370" y1="230" x2="330" y2="230" stroke-linecap="round"/>
    <line x1="360" y1="280" x2="325" y2="250" stroke-linecap="round"/>
  </g>

  <!-- Small data dots -->
  <g fill="#00d4ff" opacity="0.6">
    <circle cx="135" cy="180" r="3"/>
    <circle cx="125" cy="230" r="3"/>
    <circle cx="135" cy="280" r="3"/>
    <circle cx="365" cy="180" r="3"/>
    <circle cx="375" cy="230" r="3"/>
    <circle cx="365" cy="280" r="3"/>
  </g>

  <!-- Text: "ALPHA ONE INDEX" -->
  <text x="250" y="395" text-anchor="middle" fill="#ffffff" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="22" font-weight="600" letter-spacing="4" opacity="0.9">ALPHA ONE INDEX</text>

  <!-- Subtext: "GPU PRICING" -->
  <text x="250" y="425" text-anchor="middle" fill="#00d4ff" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="13" font-weight="400" letter-spacing="6" opacity="0.7">GPU PRICING</text>
</svg>
```

### How to export as PNG

Option A — Browser method:
1. Save the SVG code above as `adx-logo.svg`
2. Open it in Chrome
3. Right-click > Inspect > Console, paste:
```js
const svg = document.querySelector('svg');
const canvas = document.createElement('canvas');
canvas.width = 500; canvas.height = 500;
const ctx = canvas.getContext('2d');
const img = new Image();
img.onload = () => { ctx.drawImage(img, 0, 0); const a = document.createElement('a'); a.download = 'adx-logo.png'; a.href = canvas.toDataURL('image/png'); a.click(); };
img.src = 'data:image/svg+xml;base64,' + btoa(new XMLSerializer().serializeToString(svg));
```

Option B — Command line (requires Inkscape):
```bash
inkscape adx-logo.svg --export-type=png --export-width=500 --export-height=500 --export-filename=adx-logo.png
```

---

## Checklist (complete when publishing)

- [ ] AWS account verified as data provider
- [ ] S3 bucket `ai-infra-index-data` created
- [ ] IAM user created with minimal policy from AWS-DATA-EXCHANGE-SETUP.md
- [ ] ADX dataset created, Dataset ID noted
- [ ] GitHub secrets added: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `ADX_DATASET_ID`
- [ ] Logo exported as 500x500 PNG and uploaded to ADX listing
- [ ] Product listing copy pasted into ADX console
- [ ] First hourly run verified (check Actions tab)
- [ ] ADX revision auto-finalized and visible to subscribers
