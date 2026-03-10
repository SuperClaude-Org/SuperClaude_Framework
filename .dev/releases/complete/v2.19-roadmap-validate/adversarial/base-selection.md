# Base Selection: Spec-Fidelity Gap Analysis

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A (GPT) | Variant B (Claude) | Notes |
|--------|--------|-----------------|-------------------|-------|
| Requirement Coverage (RC) | 0.30 | 0.65 | 0.90 | B covers deviation inventory, gate analysis, solutions, and decision framework; A covers problem + existing mechanisms + conceptual solutions |
| Internal Consistency (IC) | 0.25 | 0.95 | 0.90 | A has no contradictions; B's gap map "No output↔spec check" entry at sprint layer is slightly inconsistent with its own layered model |
| Specificity Ratio (SR) | 0.15 | 0.55 | 0.85 | B has specific counts (29/15/1), gate names, file paths, function names, cost estimates; A has file paths and line numbers but vague solution descriptions |
| Dependency Completeness (DC) | 0.15 | 0.85 | 0.90 | Both have good internal references; B's tables resolve consistently |
| Section Coverage (SC) | 0.15 | 0.78 | 1.00 | A: ~7 logical sections / B: 9 sections (normalized to max) |

**Quant scores**:
- Variant A: (0.65×0.30) + (0.95×0.25) + (0.55×0.15) + (0.85×0.15) + (0.78×0.15) = 0.195 + 0.238 + 0.083 + 0.128 + 0.117 = **0.760**
- Variant B: (0.90×0.30) + (0.90×0.25) + (0.85×0.15) + (0.90×0.15) + (1.00×0.15) = 0.270 + 0.225 + 0.128 + 0.135 + 0.150 = **0.908**

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements | NOT MET — identifies problem but not full deviation inventory | MET — comprehensive deviation counts with severity |
| 2 | Addresses edge cases / failure scenarios | MET — identifies advisory-vs-blocking gap, harness patterns | MET — identifies `_cross_refs_resolve()` always True, dead code params |
| 3 | Includes dependencies and prerequisites | MET — key files listing, existing mechanisms inventory | MET — gate inventory, file references per solution |
| 4 | Defines success/completion criteria | NOT MET — asks questions, doesn't define criteria | MET — minimum viable fix clearly stated |
| 5 | Specifies what is explicitly out of scope | NOT MET | NOT MET |

A: 2/5 | B: 4/5

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors or hallucinated claims | MET | MET |
| 2 | Technical approaches feasible | MET — conceptual gates are feasible | MET — specific implementations are feasible |
| 3 | Terminology consistent and accurate | MET | MET |
| 4 | No internal contradictions | MET | NOT MET — gap map implies spec check at execution layer vs own layered model |
| 5 | Claims supported by evidence | MET — all claims cite specific files/lines | MET — deviation counts backed by section references |

A: 5/5 | B: 4/5

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | MET — problem → evidence → mechanisms → solutions | MET — problem → evidence → inventory → gap → solutions |
| 2 | Consistent hierarchy depth | NOT MET — flat text, no heading hierarchy | MET — consistent H2/H3/H4 |
| 3 | Clear separation of concerns | MET — sections have distinct purposes | MET — clean separation |
| 4 | Navigation aids present | NOT MET — no headers, no ToC | NOT MET — no ToC (but headers help) |
| 5 | Follows conventions of artifact type | NOT MET — conversational style for an analysis doc | MET — professional analysis format |

A: 2/5 | B: 4/5

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | MET — clear statements, explicit layering | MET — definitive framing throughout |
| 2 | Concrete rather than abstract | NOT MET — solutions are conceptual ("Gate A", "Gate B") | MET — specific files, functions, costs |
| 3 | Each section has clear purpose | MET | MET |
| 4 | Acronyms/terms defined on first use | MET | MET |
| 5 | Actionable next steps identified | NOT MET — questions for future agents, not steps | MET — 4 solutions prioritized with implementation details |

A: 3/5 | B: 5/5

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Identifies at least 3 risks | MET — identifies 3 failure scenarios | MET — per-solution risk/cost |
| 2 | Provides mitigation for each risk | NOT MET — suggests harness but no specific mitigation | MET — each solution includes implementation approach |
| 3 | Addresses failure modes and recovery | NOT MET | NOT MET |
| 4 | Considers external dependencies | MET — identifies skill protocol dependency | MET — notes tasklist is skill not CLI |
| 5 | Monitoring/validation mechanism | NOT MET | MET — discusses deterministic + LLM hybrid |

A: 2/5 | B: 4/5

### Invariant & Edge Case Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Collection boundary conditions | NOT MET | NOT MET |
| 2 | State variable interactions across boundaries | MET — identifies advisory/blocking state as root cause | MET — traces extraction→roadmap information loss chain |
| 3 | Guard condition gaps | MET — identifies semantic gates as advisory | MET — identifies `_cross_refs_resolve()` always True |
| 4 | Count divergence scenarios | NOT MET | NOT MET |
| 5 | Interaction effects when combining | MET — identifies cascade across spec→roadmap→tasklist | MET — quantifies cascade (75% from roadmap level) |

A: 2/5 | B: 2/5

### Qualitative Summary

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 2/5 | 4/5 |
| Correctness | 5/5 | 4/5 |
| Structure | 2/5 | 4/5 |
| Clarity | 3/5 | 5/5 |
| Risk Coverage | 2/5 | 4/5 |
| Invariant Coverage | 2/5 | 2/5 |
| **Total** | **16/30** | **23/30** |

**Qual scores**: A = 0.533 | B = 0.767

### Edge Case Floor Check
- Variant A: 2/5 (above 1/5 threshold) — ELIGIBLE
- Variant B: 2/5 (above 1/5 threshold) — ELIGIBLE

## Position-Bias Mitigation

Pass 1 (A→B order) and Pass 2 (B→A order) agreed on all verdicts. No disagreements requiring re-evaluation.

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined |
|---------|-------------|------------|----------|
| A (GPT briefing) | 0.760 × 0.50 = 0.380 | 0.533 × 0.50 = 0.267 | **0.647** |
| B (Claude analysis) | 0.908 × 0.50 = 0.454 | 0.767 × 0.50 = 0.384 | **0.837** |

**Margin**: 19.0% (no tiebreaker needed)

## Selected Base: Variant B (spec-fidelity-gap-analysis.md)

**Selection Rationale**: Variant B scores significantly higher on both quantitative (0.908 vs 0.760) and qualitative (0.767 vs 0.533) dimensions. Its quantified deviation inventory, gate-by-gate analysis, actionable solutions with specific implementation details, gap map visualization, and decision framework make it the substantially stronger base. Variant A's sole qualitative advantage is correctness (5/5 vs 4/5), as it avoids the minor gap-map consistency issue.

**Strengths to Preserve from Base (B)**:
- Quantified deviation inventory (29/15/1) with severity tiers
- Adversarial debate verdicts per deviation
- Gate-by-gate inventory with check/don't-check analysis
- Gap map visualization
- 4 prioritized solutions with implementation specificity
- Decision framework with trade-off table
- Dead code and `_cross_refs_resolve()` findings

**Strengths to Incorporate from Variant A**:
- Validation layering principle (X-002 winner at 85%): "validate each artifact against immediate upstream"
- Normalized output contract (X-003 winner at 80%): 6-field schema for deviation reports
- Harness conceptual definition: reusable abstraction for solution framing
- Future agent onboarding questions: structured entry point for follow-up work
- Advisory-vs-blocking root cause insight (SKILL.md:864-868 citation)
