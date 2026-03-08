# Base Selection: Roadmap Extract Failure Documents

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A | Variant B | Notes |
|--------|--------|-----------|-----------|-------|
| Requirement Coverage (RC) | 0.30 | 0.70 | 0.85 | B covers fix requirements; A covers investigation requirements but not resolution |
| Internal Consistency (IC) | 0.25 | 0.95 | 0.90 | A has no internal contradictions; B's "conservatively estimated 10%" is unsubstantiated |
| Specificity Ratio (SR) | 0.15 | 0.60 | 0.85 | B has specific code, effort estimates, probabilities; A has file paths but vague conclusions |
| Dependency Completeness (DC) | 0.15 | 0.90 | 0.80 | A's internal cross-references all resolve; B references artifacts not included in doc |
| Section Coverage (SC) | 0.15 | 1.00 | 0.64 | A: 11 sections / B: 7 sections; normalized to max |

**Quant scores**:
- Variant A: (0.70×0.30) + (0.95×0.25) + (0.60×0.15) + (0.90×0.15) + (1.00×0.15) = 0.210 + 0.238 + 0.090 + 0.135 + 0.150 = **0.823**
- Variant B: (0.85×0.30) + (0.90×0.25) + (0.85×0.15) + (0.80×0.15) + (0.64×0.15) = 0.255 + 0.225 + 0.128 + 0.120 + 0.096 = **0.824**

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements from source input | NOT MET — does not address resolution | MET — covers diagnosis and fix |
| 2 | Addresses edge cases and failure scenarios | MET — identifies --verbose, protocol mismatch | MET — covers all 8 steps, horizontal rule safety |
| 3 | Includes dependencies and prerequisites | MET — key files, execution flow | MET — implementation dependencies |
| 4 | Defines success/completion criteria | NOT MET — lists "constraints" not criteria | MET — phase 4 validation criteria |
| 5 | Specifies what is explicitly out of scope | NOT MET | NOT MET |

A: 2/5 | B: 4/5

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors or hallucinated claims | MET | MET |
| 2 | Technical approaches feasible with stated constraints | MET (no approaches proposed) | MET — regex, sanitizer, prompts all feasible |
| 3 | Terminology used consistently and accurately | MET | MET |
| 4 | No internal contradictions | MET | MET |
| 5 | Claims supported by evidence or rationale | MET — all claims cite specific files/lines | NOT MET — "10% preamble rate" has no supporting evidence |

A: 5/5 | B: 4/5

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | MET — evidence → analysis → conclusion | MET — summary → cause → fix → impact |
| 2 | Consistent hierarchy depth | MET | MET |
| 3 | Clear separation of concerns | NOT MET — some overlap between sections | MET — clean separation |
| 4 | Navigation aids present | NOT MET — no ToC, no cross-refs | NOT MET — no ToC |
| 5 | Follows conventions of artifact type | MET — investigation doc conventions | MET — RCA report conventions |

A: 3/5 | B: 4/5

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | NOT MET — "Likely Root-Cause Families" is hedged | MET — definitive causal chain |
| 2 | Concrete rather than abstract | MET — specific files, code blocks | MET — specific code solutions |
| 3 | Each section has clear purpose | MET | MET |
| 4 | Acronyms/terms defined on first use | MET | MET |
| 5 | Actionable next steps identified | NOT MET — "constraints for follow-up" not actionable | MET — "Recommended Implementation Order" with phases |

A: 3/5 | B: 5/5

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Identifies at least 3 risks | MET — 3 root cause families as risks | MET — per-fix risk ratings |
| 2 | Provides mitigation for each risk | NOT MET — no mitigations proposed | MET — each fix is a mitigation |
| 3 | Addresses failure modes and recovery | NOT MET | MET — atomic rewrite, retry logic |
| 4 | Considers external dependencies | MET — source protocol dependency | NOT MET — doesn't consider protocol dependency |
| 5 | Monitoring/validation mechanism | NOT MET | MET — Phase 4 validation run |

A: 2/5 | B: 4/5

### Invariant & Edge Case Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Collection boundary conditions | NOT MET | MET — horizontal rule safety in regex |
| 2 | State variable interactions | MET — subprocess state → artifact → gate interaction | MET — preamble propagation via _embed_inputs() |
| 3 | Guard condition gaps | MET — identifies gate's missing tolerance | MET — regex guards against false positives |
| 4 | Count divergence scenarios | NOT MET | NOT MET |
| 5 | Interaction effects when combining | MET — identifies multi-step compound effects | MET — compound reliability across 8 steps |

A: 3/5 | B: 4/5

### Qualitative Summary

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 2/5 | 4/5 |
| Correctness | 5/5 | 4/5 |
| Structure | 3/5 | 4/5 |
| Clarity | 3/5 | 5/5 |
| Risk Coverage | 2/5 | 4/5 |
| Invariant Coverage | 3/5 | 4/5 |
| **Total** | **18/30** | **25/30** |

**Qual scores**: A = 0.600 | B = 0.833

### Edge Case Floor Check
- Variant A: 3/5 (above 1/5 threshold) — ELIGIBLE
- Variant B: 4/5 (above 1/5 threshold) — ELIGIBLE

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined |
|---------|-------------|------------|----------|
| A (context) | 0.823 × 0.50 = 0.412 | 0.600 × 0.50 = 0.300 | **0.712** |
| B (report) | 0.824 × 0.50 = 0.412 | 0.833 × 0.50 = 0.417 | **0.829** |

**Margin**: 11.7% (no tiebreaker needed)

## Selected Base: Variant B (Final Root Cause Analysis Report)

**Selection Rationale**: Variant B scores significantly higher on qualitative dimensions — particularly completeness, clarity, risk coverage, and actionability. Its production-ready code, impact analysis, and implementation plan make it the stronger base for a merged document. The quantitative scores are nearly identical, meaning Variant B's qualitative superiority is decisive.

**Strengths to Preserve from Base (B)**:
- Executive summary with clear "compound failure" framing
- Root cause chain with ASCII diagram
- Three-priority fix strategy with production code
- Impact analysis table across all 8 steps
- Compound reliability calculation
- Phased implementation plan

**Strengths to Incorporate from Variant A**:
- Protocol mismatch finding (C-003): CLI extract prompt missing 10+ fields vs. source protocol
- `--verbose` flag investigation note (X-002): Follow-up item for preamble source validation
- Key files listing: Comprehensive file inventory for developer reference
- Evaluation constraints: Protocol parity, resumability, gate strictness criteria
