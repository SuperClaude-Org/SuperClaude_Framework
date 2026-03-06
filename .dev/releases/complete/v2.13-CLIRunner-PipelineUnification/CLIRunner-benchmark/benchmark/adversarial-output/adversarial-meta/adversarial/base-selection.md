# Base Selection: Pipeline Architecture Decision Comparison

## Quantitative Scoring (50% weight)

### Variant 1 (merged-decision.md)

| Metric | Weight | Score | Computation |
|--------|--------|-------|-------------|
| Requirement Coverage (RC) | 0.30 | 0.95 | Covers all 7 evidence points, all 3 options, all 6 empirical questions from source debate |
| Internal Consistency (IC) | 0.25 | 0.92 | 1 minor issue: treats all questions as "settled" while one is "PARTIALLY OPEN" — internally consistent otherwise |
| Specificity Ratio (SR) | 0.15 | 0.88 | High: "273-line", "60-80 lines", "100-150 line", "7 interleaved subsystems", "2 Hz", line numbers, commit SHAs |
| Dependency Completeness (DC) | 0.15 | 0.90 | Cross-refs to challenges, options, and Q&A table all resolve; provenance tags present |
| Section Coverage (SC) | 0.15 | 1.00 | 22 sections (max across variants) |
| **Quant Total** | | **0.934** | (0.95×0.30)+(0.92×0.25)+(0.88×0.15)+(0.90×0.15)+(1.00×0.15) |

### Variant 2 (merged-adversarial-analysis.md)

| Metric | Weight | Score | Computation |
|--------|--------|-------|
| Requirement Coverage (RC) | 0.30 | 0.75 | Covers core findings and recommendation; omits explicit option comparison, subsystem analysis, benefit rebuttals |
| Internal Consistency (IC) | 0.25 | 0.85 | X-001/X-002: body analysis reaches same conclusions as V1 but "Unverified" section contradicts body; self-inconsistency |
| Specificity Ratio (SR) | 0.15 | 0.78 | Good line-number citations but fewer concrete metrics; phases lack trigger conditions |
| Dependency Completeness (DC) | 0.15 | 0.88 | Internal references resolve; section cross-refs work; no frontmatter to cross-ref |
| Section Coverage (SC) | 0.15 | 0.55 | 12 sections vs. 22 max |
| **Quant Total** | | **0.789** | (0.75×0.30)+(0.85×0.25)+(0.78×0.15)+(0.88×0.15)+(0.55×0.15) |

---

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | V1 Pass 1 | V1 Pass 2 | V1 Final | V2 Pass 1 | V2 Pass 2 | V2 Final |
|---|-----------|-----------|-----------|----------|-----------|-----------|----------|
| 1 | Covers all explicit requirements from source input | MET | MET | **MET** | NOT MET | NOT MET | **NOT MET** |
| 2 | Addresses edge cases and failure scenarios | MET | MET | **MET** | NOT MET | NOT MET | **NOT MET** |
| 3 | Includes dependencies and prerequisites | MET | MET | **MET** | MET | MET | **MET** |
| 4 | Defines success/completion criteria | MET | MET | **MET** | NOT MET | NOT MET | **NOT MET** |
| 5 | Specifies what is explicitly out of scope | MET | NOT MET | **MET** | NOT MET | NOT MET | **NOT MET** |

V1: 5/5 | V2: 1/5

### Correctness (5 criteria)

| # | Criterion | V1 Final | V2 Final |
|---|-----------|----------|----------|
| 1 | No factual errors or hallucinated claims | **MET** | **MET** |
| 2 | Technical approaches are feasible with stated constraints | **MET** | **MET** |
| 3 | Terminology used consistently and accurately | **MET** | **MET** |
| 4 | No internal contradictions | **MET** | **NOT MET** |
| 5 | Claims supported by evidence or rationale | **MET** | **MET** |

V1: 5/5 | V2: 4/5
Evidence for V2 criterion 4 failure: "Confidence and Caveats" lists extraction history as "Unverified" while Section 4 ("There is also local roadmap debt") implicitly relies on verified extraction context.

### Structure (5 criteria)

| # | Criterion | V1 Final | V2 Final |
|---|-----------|----------|----------|
| 1 | Logical section ordering (prerequisites before dependents) | **MET** | **MET** |
| 2 | Consistent hierarchy depth | **MET** | **MET** |
| 3 | Clear separation of concerns between sections | **MET** | **MET** |
| 4 | Navigation aids present | **MET** | **NOT MET** |
| 5 | Follows conventions of the artifact type | **MET** | **NOT MET** |

V1: 5/5 | V2: 3/5
Evidence: V2 lacks table of contents, frontmatter, and machine-readable metadata expected for architectural decision records.

### Clarity (5 criteria)

| # | Criterion | V1 Final | V2 Final |
|---|-----------|----------|----------|
| 1 | Unambiguous language | **MET** | **MET** |
| 2 | Concrete rather than abstract | **MET** | **MET** |
| 3 | Each section has a clear purpose | **MET** | **MET** |
| 4 | Acronyms and domain terms defined on first use | **MET** | **MET** |
| 5 | Actionable next steps clearly identified | **MET** | **MET** |

V1: 5/5 | V2: 5/5

### Risk Coverage (5 criteria)

| # | Criterion | V1 Final | V2 Final |
|---|-----------|----------|----------|
| 1 | Identifies at least 3 risks with probability and impact | **MET** | **NOT MET** |
| 2 | Provides mitigation strategy for each identified risk | **MET** | **NOT MET** |
| 3 | Addresses failure modes and recovery procedures | **MET** | **NOT MET** |
| 4 | Considers external dependencies and their failure scenarios | **MET** | **MET** |
| 5 | Includes monitoring or validation mechanism | **MET** | **NOT MET** |

V1: 5/5 | V2: 1/5

### Qualitative Summary

| Dimension | V1 Score | V2 Score |
|-----------|----------|----------|
| Completeness | 5/5 | 1/5 |
| Correctness | 5/5 | 4/5 |
| Structure | 5/5 | 3/5 |
| Clarity | 5/5 | 5/5 |
| Risk Coverage | 5/5 | 1/5 |
| **Total** | **25/25** | **14/25** |
| **Qual Score** | **1.000** | **0.560** |

---

## Position-Bias Mitigation

- Pass 1 order: Variant 1, Variant 2
- Pass 2 order: Variant 2, Variant 1
- Disagreements found: 1 (V1 Completeness criterion 5)
- Verdicts changed by re-evaluation: 0 (re-evaluation confirmed MET for V1)

---

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined | Rank |
|---------|-------------|------------|----------|------|
| Variant 1 | 0.934 × 0.50 = 0.467 | 1.000 × 0.50 = 0.500 | **0.967** | **1** |
| Variant 2 | 0.789 × 0.50 = 0.395 | 0.560 × 0.50 = 0.280 | **0.675** | 2 |

**Margin: 29.2%** — well outside 5% tiebreaker threshold.
**Tiebreaker applied: No**

---

## Selected Base: Variant 1 (merged-decision.md)

### Selection Rationale

Variant 1 scored substantially higher across both quantitative (0.934 vs 0.789) and qualitative (25/25 vs 14/25) dimensions. The margin of 29.2% is decisive. Key differentiators:

- **Completeness**: Variant 1 covers all 3 options explicitly, tracks 6 empirical questions, and includes revisit conditions. Variant 2 omits option enumeration, edge case analysis, and completion criteria.
- **Correctness**: Variant 2 has an internal contradiction (X-001) where its body implicitly treats extraction history as verified while its confidence section lists it as unverified.
- **Risk Coverage**: Variant 1 provides per-option risk assessments, subsystem enumeration for regression risk, and mitigation strategies. Variant 2 provides minimal risk analysis.
- **Unique contributions**: Variant 1 contains 3 HIGH-value unique contributions (subsystem enumeration, StepRunner analysis, benefit rebuttals) that Variant 2 cannot supply.

### Strengths to Preserve from Base
- 7-point evidence summary with code citations
- 5 Challenge sections with structured analysis
- 3-option decision framework with metrics tables
- Questions Settled and Open tracking table
- Explicit revisit conditions
- YAML frontmatter metadata

### Strengths to Incorporate from Variant 2
- "Phased extraction" framing (U-004) — reframes targeted fixes as Phase 1 of longer roadmap
- Pro-unification acknowledgment (U-005) — adds balanced recognition of long-term extraction value
- Hypothesis framing language — "executor unification as a hypothesis to validate"
