# Base Selection: Forensic Workflow Diagnostics

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A | Variant B | Variant C |
|--------|--------|-----------|-----------|-----------|
| Evidence specificity (RC equivalent) | 0.30 | 0.75 | 0.95 | 0.60 |
| Internal consistency | 0.25 | 0.90 | 0.85 | 0.90 |
| Specificity ratio | 0.15 | 0.80 | 0.90 | 0.65 |
| Cross-reference completeness | 0.15 | 0.70 | 0.85 | 0.75 |
| Topic coverage (10 identified) | 0.15 | 0.70 | 0.90 | 1.00 |
| **Weighted quantitative** | | **0.78** | **0.90** | **0.76** |

## Qualitative Assessment

| Dimension | Variant A | Variant B | Variant C |
|-----------|-----------|-----------|-----------|
| Forensic accuracy | 4/5 | 5/5 | 3/5 |
| Evidence quality | 4/5 | 5/5 | 3/5 |
| Causal validity | 3/5 | 4/5 | 4/5 |
| Analytical usefulness | 5/5 | 4/5 | 4/5 |
| Epistemic honesty | 3/5 | 3/5 | 5/5 |
| **Total** | **19/25** | **21/25** | **19/25** |
| **Normalized** | **0.76** | **0.84** | **0.76** |

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined | Rank |
|---------|-------------|------------|----------|------|
| **B** | 0.450 | 0.420 | **0.870** | **1** |
| A | 0.390 | 0.380 | 0.770 | 2 |
| C | 0.380 | 0.380 | 0.760 | 3 |

Margin: B leads A by 10% (above 5% tiebreaker threshold)

## Selected Base: Variant B

**Selection rationale**: Variant B provides the strongest evidence chains, most specific code-level citations, and most comprehensive coverage (9/10 topics). Its 4-dynamic model offers actionable diagnostic categories. However, the merged output will adopt C's epistemic structure (separating findings from theories) and incorporate A's analytical frameworks (proxy table, can/cannot table) as the output is reorganized around the user's requested structure.

**Strengths to preserve from base**:
- Code-level evidence chains (gate functions, schema drift, API divergence)
- Temporal impossibility evidence for retrospective propagation
- "Noted But Not Prevented" anti-pattern identification
- Specific quantifications (17→3 fields, 78% growth, PARTIAL→PASS)

**Strengths to incorporate from non-base variants**:
- From A: Proxy measurement table, Can/Cannot table, "category error" thesis (as partially validated theory)
- From C: 7-theory modular structure (as organizational principle), seam enumeration, Theory 6 (shared abstractions), Stage 7 (retrospective as pipeline stage), epistemic separation of findings vs theories
