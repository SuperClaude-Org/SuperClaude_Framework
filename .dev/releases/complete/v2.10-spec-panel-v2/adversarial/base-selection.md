# Base Selection: Adversarial Scoring

## Quantitative Scoring (50% weight)

| Metric | Weight | V1 (opus:scribe) | V2 (haiku:scribe) |
|--------|--------|-----------------|-----------------|
| Requirement Coverage (RC) | 0.30 | 0.95 | 0.85 |
| Internal Consistency (IC) | 0.25 | 1.00 | 1.00 |
| Specificity Ratio (SR) | 0.15 | 0.82 | 0.80 |
| Dependency Completeness (DC) | 0.15 | 0.95 | 0.95 |
| Section Coverage (SC) | 0.15 | 1.00 | 0.57 |
| **Quant Score** | | **0.951** | **0.853** |

*V1 RC advantage: Narrative prose explicitly addresses FR-14.1..14.6 modified behaviors and all acceptance criteria from spec. V1 SC advantage: 14 top-level sections vs 8.*

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)
| Criterion | V1 | V2 |
|-----------|----|----|
| Covers all explicit requirements from source | MET | MET |
| Addresses edge cases and failure scenarios | MET | MET |
| Includes dependencies and prerequisites | MET | MET |
| Defines success/completion criteria | MET | MET |
| Specifies what is explicitly out of scope | MET | NOT MET (no spec for non-guard spec behavior) |

### Correctness (5 criteria)
| Criterion | V1 | V2 |
|-----------|----|----|
| No factual errors or hallucinated claims | MET | MET |
| Technical approaches are feasible with stated constraints | MET | MET |
| Terminology used consistently | MET | MET |
| No internal contradictions | MET | MET |
| Claims supported by evidence or rationale | MET | MET |

### Structure (5 criteria)
| Criterion | V1 | V2 |
|-----------|----|----|
| Logical section ordering | MET | MET |
| Consistent hierarchy depth | MET | MET |
| Clear separation of concerns | MET | MET |
| Navigation aids (cross-references, index, TOC) | MET (phase summaries + appendix mapping) | NOT MET |
| Follows roadmap artifact conventions | MET | MET |

### Clarity (5 criteria)
| Criterion | V1 | V2 |
|-----------|----|----|
| Unambiguous language | NOT MET (minor: "as appropriate" in R-4 mitigation) | NOT MET (minor: similar) |
| Concrete rather than abstract | MET | MET |
| Each section has clear purpose | MET | MET |
| Acronyms defined on first use | MET | MET |
| Actionable next steps clearly identified | MET | MET |

### Risk Coverage (5 criteria)
| Criterion | V1 | V2 |
|-----------|----|----|
| Identifies at least 3 risks with probability/impact | MET (6 risks) | MET (6 risks) |
| Provides mitigation strategy for each risk | MET | MET |
| Addresses failure modes and recovery | MET (release rollback, phase rollback) | MET (Gate B rollback plan) |
| Considers external dependencies | MET (integration drift risk R-7 noted) | NOT MET |
| Monitoring/validation mechanism | MET (quality metrics + M6 suite) | MET |

### Qualitative Summary
| Variant | Score | Total |
|---------|-------|-------|
| V1 | 24/25 | **0.96** |
| V2 | 21/25 | **0.84** |

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined | Debate Points Won |
|---------|-------------|------------|----------|-----------------|
| V1 (opus:scribe) | 0.951 × 0.5 = 0.476 | 0.96 × 0.5 = 0.480 | **0.956** | 11/14 |
| V2 (haiku:scribe) | 0.853 × 0.5 = 0.427 | 0.84 × 0.5 = 0.420 | **0.847** | 3/14 |

**Margin**: 10.9% — no tiebreaker required (threshold: 5%)

## Selected Base: Variant 1 (opus:scribe)

**Selection rationale**: V1 wins on 11 of 14 debate points, has significantly higher section coverage (14 vs 8), and scores 12% higher on combined metric. V1's narrative prose provides stakeholder context, correctly identifies M4+M5 parallelism, and covers all requirement details.

**Strengths to preserve from V1**:
- Phase narrative overviews (Phase 1/2/3 context sections)
- M4+M5 parallel dependency graph with linearized critical path
- Integration Map section with ASCII diagram
- SP-5 quantified revisit trigger (10 reviews + FP rate)
- Risk Register with R-7 integration drift coverage
- Appendix: Phase-to-Milestone Mapping table
- 7-column boundary table column spec in M3

**Strengths to incorporate from V2**:
- Gate A (M3 milestone) with evidence pack: v0.04 run logs, overhead report, artifact completeness report
- Gate B (M6 milestone) with evidence pack: metrics dashboard, risk review, integration verification, go/no-go decision + rollback plan
- Dedicated Validation-first checkpoints table (Section 5 of V2)
- M6 explicit rollback plan requirement
