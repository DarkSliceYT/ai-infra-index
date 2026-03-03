# Contributing to AI Infrastructure Index

Thank you for your interest in contributing! This project aims to be the most comprehensive open-source reference for AI hardware specs, cloud GPU pricing, and infrastructure benchmarks.

## How to Contribute

### Pricing Data
- **Add a new provider**: Submit a PR adding the provider to `scripts/fetch_pricing.py` and `data/cloud-pricing.json`
- **Fix stale pricing**: If you spot outdated prices, open an issue or submit a correction PR with a source link

### GPU Specifications
- **Add new hardware**: Update `data/gpu-specs.json` and `specs/gpu-specifications.md` with official datasheet references
- **Benchmark data**: Add real-world benchmarks to `specs/inference-benchmarks.md` with methodology and source

### Documentation
- **Improve guides**: The `specs/` directory contains sizing guides, cost optimization playbooks, and decision frameworks
- **Fix errors**: Typos, broken links, or unclear explanations — all welcome

## Submitting a Pull Request

1. Fork the repository
2. Create a feature branch (`git checkout -b add-provider-xyz`)
3. Make your changes with clear commit messages
4. Ensure data files are valid JSON (`python -m json.tool data/cloud-pricing.json`)
5. Submit a PR with:
   - What you changed and why
   - Source links for any new data
   - Screenshot if updating the GitHub Pages site

## Data Quality Standards

- All pricing data must include a verifiable source URL
- GPU specifications must reference official vendor datasheets
- Benchmark results must include methodology, hardware config, and software versions
- No estimated or projected numbers without clear labeling

## Reporting Issues

- **Incorrect data**: Open an issue with the correct value and source link
- **Missing provider**: Open an issue tagged `provider` with the provider name and pricing page URL
- **Feature requests**: Open an issue tagged `enhancement`

## Code of Conduct

Be respectful and constructive. This is a data-driven project — back claims with sources.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
