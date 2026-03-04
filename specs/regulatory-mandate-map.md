# AI Infrastructure Regulatory Mandate Map

> **A cross-jurisdictional matrix mapping AI hardware and infrastructure requirements to active regulatory frameworks. Covers EU AI Act, UK AI Safety Institute (AISI) evaluation requirements, and NIST AI Risk Management Framework.**

_Last updated: March 2026. This document is maintained as a living reference; regulatory guidance evolves — check linked primary sources before compliance decisions._

---

## What Is the Regulatory Mandate Map?

This file maps three active regulatory frameworks — the EU AI Act, the UK AI Safety Institute (AISI) Frontier AI Evaluation Protocols, and the NIST AI Risk Management Framework (AI RMF 1.0) — against the infrastructure-layer obligations they impose. The goal is to let procurement teams, data center operators, and safety engineers understand which regulatory requirements touch hardware selection, compute capacity reporting, evaluation infrastructure, and model-level testing obligations.

---

## Framework Overview

| Framework | Jurisdiction | Status (March 2026) | Primary Source | Binding? |
|-----------|-------------|---------------------|----------------|----------|
| **EU AI Act** | European Union | In force (Aug 2024); GPAI obligations phased Aug 2025 | [EUR-Lex 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689) | Yes — legal regulation |
| **UK AI Safety Institute (AISI) Evaluation Requirements** | United Kingdom | Voluntary (pre-deployment evaluations); DSIT policy framework | [DSIT / AISI Evaluation Protocols](https://www.gov.uk/government/organisations/ai-safety-institute) | Voluntary (expected to harden) |
| **NIST AI RMF 1.0** | United States | Published Jan 2023; referenced in Executive Orders | [NIST AI 100-1](https://airc.nist.gov/RMF) | Voluntary framework |

---

## Infrastructure-Layer Requirement Matrix

This matrix covers the intersection of each framework with the key infrastructure dimensions relevant to AI hardware procurement, model training, and deployment. Cells indicate whether the framework imposes a **Requirement (R)**, **Recommendation (Rec)**, or **Not Addressed (—)**.

| Infrastructure Dimension | EU AI Act | UK AISI Eval Reqs | NIST AI RMF 1.0 | Notes |
|--------------------------|-----------|-------------------|-----------------|-------|
| **Compute capacity disclosure (FLOPs threshold)** | **R** — GPAI general-purpose models exceeding 10²⁵ FLOPs training compute must notify EU AI Office | **Rec** — AISI uses compute thresholds as a proxy trigger for evaluation | **—** | EU Act Art. 51; AISI [Responsible Scaling Policy alignment](https://www.gov.uk/government/publications/frontier-ai-safety-commitments-ai-seoul-summit-2024) |
| **Pre-deployment safety evaluation infrastructure** | **R** — High-risk and GPAI systemic-risk models require technical testing before market placement | **R** — Frontier models must undergo AISI evaluation before UK deployment (voluntary agreement, 2024 Seoul Summit signatories) | **Rec** — GOVERN 1.1, MEASURE 2.5 recommend evaluation infrastructure | EU Act Art. 9, 40, 55; AISI [Evals Protocol v1.0](https://www.gov.uk/government/publications/advanced-ai-evaluations-at-aisi) |
| **Hardware provenance / supply chain documentation** | **R** — Art. 23 requires technical documentation including hardware used for training | **Rec** — AISI requests hardware details in eval submissions | **Rec** — GOVERN 6.1, MAP 1.5 address supply chain risk | Relevant for H100/A100 export-controlled hardware |
| **Data center energy / power reporting** | **Rec** — GPAI Code of Practice (voluntary) includes energy efficiency metrics | **—** | **—** — outside scope of AI RMF | EU AI Office [GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/ai-code-practice) |
| **Model card / system card requirements** | **R** — Art. 53 requires usage documentation for GPAI providers | **Rec** — AISI requests model cards in frontier eval packs | **Rec** — MANAGE 4.2 recommends documentation practices | |
| **Red-teaming / adversarial testing** | **R** — Art. 55 systemic-risk GPAI models must conduct adversarial testing | **R** — AISI evaluations include red-teaming for dangerous capabilities (CBRN, cyber, persuasion) | **Rec** — MEASURE 2.6, 2.7 recommend adversarial testing | AISI [dangerous capabilities eval framework](https://www.gov.uk/government/publications/advanced-ai-evaluations-at-aisi) |
| **Incident reporting / logging** | **R** — Art. 73 requires serious incident reporting within 15 days | **Rec** — AISI expects post-incident disclosure from evaluated models | **Rec** — RESPOND 1.1, RECOVER 1.1 recommend incident logging | |
| **Benchmark/evaluation reproducibility** | **Rec** — Technical standards (Art. 40) to reference harmonized standards | **R** — AISI requires reproducible eval runs for model registrations | **Rec** — MEASURE 1.3 addresses measurement reproducibility | AISI publishes [eval methodology](https://www.gov.uk/government/publications/advanced-ai-evaluations-at-aisi) |
| **Export control / access restrictions (hardware)** | **—** — Separate BIS/OFAC regime; not within AI Act scope | **—** — DSIT coordinates with UKDMO but AISI is eval-focused | **—** — Outside NIST AI RMF scope | US BIS Entity List, EAR controls apply independently |
| **Third-party audit requirements** | **R** — Art. 43 conformity assessments for high-risk AI; Art. 55 for GPAI systemic risk | **Rec** — AISI may share evaluation results with deployers; no mandated third-party audit yet | **Rec** — GOVERN 1.4 recommends independent review | EU notified bodies handle Art. 43 audits |

**Legend:** R = Requirement (legally binding or formal protocol requirement) | Rec = Recommendation | — = Not addressed

---

## EU AI Act: Key Infrastructure Obligations

The EU AI Act (Regulation 2024/1689) imposes the following infrastructure-level obligations for AI providers and deployers:

- **GPAI compute threshold (Art. 51):** Any general-purpose AI model trained with more than **10²⁵ FLOPs** is automatically classified as a model with systemic risk, triggering enhanced obligations regardless of downstream application.
- **Technical documentation (Art. 53, Annex XI):** GPAI providers must document training compute (FLOP count), training data sources, hardware architecture used, and energy consumed during training.
- **Adversarial testing (Art. 55):** Systemic-risk GPAI models must undergo red-teaming and adversarial testing, including for CBRN applications, cybersecurity misuse, and critical infrastructure attack vectors.
- **Incident reporting (Art. 73):** Serious incidents involving AI systems must be reported to national supervisory authorities within 15 days.

Primary source: [EUR-Lex 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)

---

## UK AI Safety Institute (AISI): Evaluation Requirements

The UK AISI (now renamed AI Security Institute, Feb 2025) establishes pre-deployment evaluation protocols for frontier AI models. Key infrastructure requirements:

- **Pre-deployment evaluation (Seoul Summit commitment):** Frontier AI developers who signed the 2024 Seoul Summit commitments agreed to provide AISI access for pre-deployment safety evaluations before market release.
- **Dangerous capabilities evaluation:** AISI evaluates models for dangerous capability uplift across four domains: CBRN (biological, chemical, radiological, nuclear weapons), cybersecurity attack capability, human deception/persuasion at scale, and autonomous replication.
- **Hardware/infrastructure submission:** Eval submissions must include the hardware configuration used for training (GPU cluster type, scale, interconnect), compute budget in FLOPs, and training run reproducibility details.
- **Evaluation reproducibility:** Results must be reproducible by AISI staff; submitters must provide sufficient infrastructure documentation to enable re-running key evaluations.
- **Post-evaluation disclosure:** AISI may share evaluation findings with governments and deployers; developers should expect potential public summary reports.

Primary source: [DSIT / AISI Advanced AI Evaluations](https://www.gov.uk/government/publications/advanced-ai-evaluations-at-aisi)

---

## NIST AI RMF 1.0: Infrastructure Guidance

NIST AI RMF 1.0 (NIST AI 100-1, January 2023) is a voluntary framework organized around four core functions: GOVERN, MAP, MEASURE, MANAGE. Infrastructure-relevant guidance includes:

- **GOVERN 1.1:** Establish policies for AI risk management including compute resource governance and access controls.
- **GOVERN 6.1:** Address supply chain risks — including hardware sourcing from vendors subject to export controls or geopolitical risk.
- **MAP 1.5:** Document AI system context including hardware, infrastructure dependencies, and operational environment.
- **MEASURE 1.3:** Ensure measurement practices and benchmarks are reproducible and documented.
- **MEASURE 2.5:** Implement pre-deployment testing proportionate to risk level.
- **MEASURE 2.6–2.7:** Conduct adversarial testing including red-teaming; document results with hardware/software configuration used.
- **MANAGE 4.2:** Maintain system cards and model documentation as part of lifecycle management.

Primary source: [NIST AI 100-1](https://airc.nist.gov/RMF) | Playbook: [NIST AI RMF Playbook](https://airc.nist.gov/Docs/2)

---

## Compute Threshold Reference

For EU AI Act classification, training compute (in FLOPs) determines regulatory tier:

| Compute Level | EU AI Act Tier | AISI Trigger | Example Models |
|--------------|---------------|--------------|---------------|
| < 10²³ FLOPs | Standard GPAI obligations | No automatic trigger | Most fine-tuned models |
| 10²³ – 10²⁵ FLOPs | Standard GPAI (Art. 53 docs required) | Voluntary notification recommended | Llama 3 70B range |
| > 10²⁵ FLOPs | **Systemic risk GPAI** (Art. 55 red-teaming, audit) | **Required pre-deployment evaluation** | GPT-4 class, Gemini Ultra class |

> Note: FLOPs thresholds are defined in EU AI Act Recital 110 and Art. 51(1)(a). The 10²⁵ FLOPs boundary may be updated by EU AI Office delegated act.

---

## Infrastructure Checklist for Compliance Teams

Use this checklist when procuring or deploying AI infrastructure for GPAI or high-risk AI applications:

- [ ] Calculate and document total training FLOPs for all model runs (EU AI Act Art. 51 threshold check)
- [ ] Document GPU cluster configuration (model, count, interconnect, memory) per training run
- [ ] Record energy consumption per training run in MWh (GPAI Code of Practice)
- [ ] Establish hardware provenance documentation — confirm no export-restricted components (BIS Entity List)
- [ ] For frontier models: initiate AISI pre-deployment eval submission at least 30 days before launch
- [ ] Maintain reproducible benchmark/eval configurations to satisfy AISI and NIST MEASURE requirements
- [ ] Implement incident logging with ≤15 day reporting SLA for EU markets (AI Act Art. 73)
- [ ] Complete technical documentation per EU AI Act Annex XI before EU market placement

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-04 | Initial publication — EU AI Act, UK AISI, NIST AI RMF 1.0 matrix |

---

## See Also

- [EU AI Act Full Text (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- [UK AISI Evaluation Publications (DSIT)](https://www.gov.uk/government/publications/advanced-ai-evaluations-at-aisi)
- [NIST AI RMF 1.0 (NIST)](https://airc.nist.gov/RMF)
- [NIST AI RMF Playbook](https://airc.nist.gov/Docs/2)
- [Seoul AI Safety Summit Commitments (2024)](https://www.gov.uk/government/publications/frontier-ai-safety-commitments-ai-seoul-summit-2024)
- [EU AI Office GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/ai-code-practice)
- [AI Infrastructure Index — Inference Benchmarks](inference-benchmarks.md)
- [AI Infrastructure Index — GPU Specifications](gpu-specifications.md)
