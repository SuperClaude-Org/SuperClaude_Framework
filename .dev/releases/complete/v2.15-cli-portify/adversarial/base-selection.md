# Base Selection: Session Findings Comparison

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A | Variant B |
|--------|--------|-----------|-----------|
| Requirement Coverage (RC) | 0.30 | 0.95 | 0.98 |
| Internal Consistency (IC) | 0.25 | 1.00 | 0.967 |
| Specificity Ratio (SR) | 0.15 | 0.90 | 0.89 |
| Dependency Completeness (DC) | 0.15 | 0.95 | 0.90 |
| Section Coverage (SC) | 0.15 | 0.917 | 1.00 |
| **Weighted Total** | | **0.950** | **0.954** |

---

## Qualitative Scoring (50% weight) -- Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements | MET -- all 15 findings, 9 RCs, 8 solutions (Sec 3-10) | MET -- all findings plus supplementary analyses (Sec 3-6) |
| 2 | Addresses edge cases and failure scenarios | MET -- 5 Whittaker attacks (Sec 3.5) | MET -- 5 attacks + 12 GAP entries (Sec 3.4, 3.6) |
| 3 | Includes dependencies and prerequisites | MET -- 3 peer protocol references (Sec 2.2) | MET -- pipeline description (Sec 4) |
| 4 | Defines success/completion criteria | NOT MET -- % estimates without verification methodology | MET -- unit/integration/regression per PR (Sec 6.3) |
| 5 | Specifies what is out of scope | MET -- deferred solutions with rationale (Sec 10.1) | MET -- deferred solutions (Sec 6.2) |
| | **Subtotal** | **4/5** | **5/5** |

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors | MET -- all citations verified | NOT MET -- "four-PR" in abstract vs 3 PRs in body |
| 2 | Technical approaches feasible | MET -- solutions target specific files (Sec 9.2) | MET -- solutions target specific files (Sec 6.1) |
| 3 | Terminology consistent | MET -- consistent IDs throughout | NOT MET -- multiple inconsistent ID schemes (SV/GAP/RC/S/PR/A) |
| 4 | No internal contradictions | MET -- consistent throughout | NOT MET -- 4-PR/3-PR inconsistency; S6 #1 ranked but in PR2 |
| 5 | Claims supported by evidence | MET -- all RCs cite file:line (Sec 7) | MET -- all RCs cite file:line with extended context (Sec 5.3) |
| | **Subtotal** | **5/5** | **2/5** |

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | MET -- background->findings->failure->RCA->solutions (Sec 2-10) | MET -- Part I->II->III->IV follows dependency chain |
| 2 | Consistent hierarchy depth | MET -- max H3 throughout, no orphans | NOT MET -- H4 in some areas but not others |
| 3 | Clear separation of concerns | MET -- each section has one purpose | MET -- Part-based grouping with clear concerns |
| 4 | Navigation aids present | NOT MET -- no TOC or systematic cross-references | MET -- timeline table + 3 standalone appendices |
| 5 | Follows artifact type conventions | MET -- standard engineering findings format | MET -- formal academic-style with abstract |
| | **Subtotal** | **4/5** | **3/5** |

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | MET -- specific, minimal hedging | MET -- specific with occasional hedging |
| 2 | Concrete rather than abstract | MET -- specific code, files, lines | MET -- fuller code context |
| 3 | Each section has clear purpose | MET -- descriptive section names | MET -- Part labels indicate purpose |
| 4 | Terms defined on first use | MET -- sc:cli-portify defined (Sec 2.1) | MET -- similar definitions |
| 5 | Actionable next steps identified | MET -- 3-PR roadmap (Sec 10.1) | MET -- 3-PR sequence + verification (Sec 6.2-6.3) |
| | **Subtotal** | **5/5** | **5/5** |

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | 3+ risks with probability/impact | MET -- 9 RCs with likelihood 6-10/10 (Sec 7) | MET -- 9 RCs with severity ratings (Sec 5.3) |
| 2 | Mitigation for each risk | MET -- 8 solutions mapped to RCs (Sec 9) | MET -- 8 solutions mapped to RCs (Sec 6.1) |
| 3 | Failure modes and recovery | MET -- retry failure analysis (Sec 6.4) | MET -- failure mode analysis (Sec 4.2) |
| 4 | External dependencies considered | MET -- CLAUDE.md, claude CLI behavior (RC7) | MET -- same (RC7) |
| 5 | Monitoring/validation mechanism | NOT MET -- no verification strategy | MET -- Sec 6.3 verification strategy |
| | **Subtotal** | **4/5** | **5/5** |

### Invariant & Edge Case Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Collection boundary conditions | NOT MET -- absent | MET -- GAP-5 step count, GAP-9 module collision (Sec 3.6) |
| 2 | State variable interactions | NOT MET -- absent | MET -- SV1-SV11 registry (Sec 3.5) |
| 3 | Guard condition gaps identified | NOT MET -- findings exist but no inventory | MET -- GAP-1 through GAP-12 (Sec 3.6) |
| 4 | Count divergence scenarios | NOT MET -- conservation equation only | MET -- GAP-5 step budget analysis (Sec 3.6) |
| 5 | Interaction effects | NOT MET -- no solution interaction analysis | NOT MET -- not in document (found by invariant probe only) |
| | **Subtotal** | **0/5** | **4/5** |

### Qualitative Summary

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness | 4/5 | 5/5 |
| Correctness | 5/5 | 2/5 |
| Structure | 4/5 | 3/5 |
| Clarity | 5/5 | 5/5 |
| Risk Coverage | 4/5 | 5/5 |
| Invariant & Edge Case | **0/5** | 4/5 |
| **Total** | **22/30** | **24/30** |
| **qual_score** | **0.733** | **0.800** |

### Edge Case Floor Check

| Variant | Score | Threshold (1/5) | Eligibility |
|---------|-------|-----------------|-------------|
| Variant A | 0/5 | BELOW | **INELIGIBLE as base** |
| Variant B | 4/5 | ABOVE | Eligible |

---

## Position-Bias Mitigation

| Dimension | Pass 1 (A→B) | Pass 2 (B→A) | Agreement |
|-----------|-------------|-------------|-----------|
| Completeness | A:4, B:5 | A:4, B:5 | Agreed |
| Correctness | A:5, B:2 | A:5, B:2 | Agreed |
| Structure | A:4, B:3 | A:4, B:3 | Agreed |
| Clarity | A:5, B:5 | A:5, B:5 | Agreed |
| Risk Coverage | A:4, B:5 | A:4, B:5 | Agreed |
| Invariant | A:0, B:4 | A:0, B:4 | Agreed |

Disagreements found: 0. No re-evaluation needed.

---

## Combined Scoring

| Component | Weight | Variant A | Variant B |
|-----------|--------|-----------|-----------|
| Quantitative | 0.50 | 0.950 | 0.954 |
| Qualitative | 0.50 | 0.733 | 0.800 |
| **Combined** | | **0.842** | **0.877** |
| Edge Case Floor | | **INELIGIBLE** | Eligible |

Margin: 0.877 - 0.842 = 0.035 (3.5%)
Tiebreaker applied: No (floor rule determines base independently of score)

---

## Selected Base: Variant B (haiku:analyzer)

**Selection rationale**: Variant A is ineligible as base due to scoring 0/5 on Invariant & Edge Case Coverage (below the 1/5 floor threshold). Even without the floor rule, Variant B scores higher overall (0.877 vs 0.842). B's decisive advantages are its State Variable Registry, Guard Condition Boundary Table, verification strategy, and named expert/debater structures. B's correctness weaknesses (4-PR inconsistency, identifier fragmentation) are editorial errors correctable during merge.

**Strengths to preserve from base (Variant B)**:
- State Variable Registry (SV1-SV11)
- Guard Condition Boundary Table (GAP-1 through GAP-12)
- Named expert perspectives and structured debater positions
- Verification Strategy (Section 6.3)
- Comprehensive File Reference Index (Appendix C)
- Extended root cause evidence with causal chain tracing

**Strengths to incorporate from non-base (Variant A)**:
- Traceability Matrix (Sec 11.3): Spec Finding -> RC -> Solution -> PR mapping
- Critical Code Locations table (Sec 11.2): compact RC -> File:Line -> Code Pattern
- Release directory references with "already created" status
- Cleaner scope framing (document only what session produced)
- Fix 4-PR/3-PR inconsistency (use A's consistent "3 PRs + 2 deferred" framing)
- Fix ranking/sequencing tension (clarify why S6 is ranked #1 but in PR2)
