# Base Selection: Tasklist Generator Refactor Proposals

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A | Variant B |
|--------|--------|-----------|-----------|
| Requirement Coverage (RC) | 0.30 | 0.95 | 0.60 |
| Internal Consistency (IC) | 0.25 | 1.00 | 0.97 |
| Specificity Ratio (SR) | 0.15 | 0.90 | 0.70 |
| Dependency Completeness (DC) | 0.15 | 1.00 | 0.95 |
| Section Coverage (SC) | 0.15 | 1.00 | 0.75 |
| **Quant Total** | **1.00** | **0.970** | **0.783** |

## Qualitative Scoring (50% weight) — Additive Binary Rubric

| Dimension | Variant A | Variant B |
|-----------|-----------|-----------|
| Completeness (5 criteria) | 4/5 | 2/5 |
| Correctness (5 criteria) | 5/5 | 3/5 |
| Structure (5 criteria) | 5/5 | 4/5 |
| Clarity (5 criteria) | 5/5 | 4/5 |
| Risk Coverage (5 criteria) | 5/5 | 3/5 |
| **Qual Total** | **24/25 = 0.960** | **16/25 = 0.640** |

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined | Rank |
|---------|-------------|------------|----------|------|
| **A (opus)** | 0.485 | 0.480 | **0.965** | **1** |
| B (haiku) | 0.392 | 0.320 | 0.711 | 2 |

**Margin**: 25.4% (well above 5% tiebreaker threshold)
**Tiebreaker applied**: No

## Debate Performance

| Metric | Variant A | Variant B |
|--------|-----------|-----------|
| Points won (scoring matrix) | 16 | 2 |
| Draws | 1 | 1 |
| Opponent concessions received | 3 major | 1 minor |

## Selected Base: Variant A (tasklist-generator-v3-refactor-proposal.md)

### Selection Rationale
Variant A scores decisively higher on both quantitative (0.970 vs 0.783) and qualitative (0.960 vs 0.640) dimensions. The margin (25.4%) eliminates any tiebreaker consideration. Variant A won 16 of 19 diff points in the debate, and Variant B's advocate made 3 major concessions acknowledging A's superiority on sc:task-unified depth, template completeness, and completion protocol correctness. Both advocates agreed A's content is superior; the sole disagreement was merge direction (A-base vs B-base), resolved by A's higher combined score.

### Strengths to Preserve from Base (Variant A)
- Code-evidenced Sprint CLI contract (regex patterns, discovery strategy, prompt template, result parsing)
- sc:task-unified classification and execution analysis with field taxonomy
- Complete Index File Template and Phase File Template
- 7 severity-rated gaps (GAP-01 through GAP-07)
- 6 refactoring specifications (R-01 through R-06) with section mappings
- Compatibility matrix
- Migration path with effort estimates
- Open questions section

### Strengths to Incorporate from Variant B
1. **Sprint Compatibility Self-Check phrasing** (B item 10, lines 106-113) — crisper 5-point version to complement A's R-06
2. **Canonical naming enforcement language** (B lines 67-72) — stronger "Do not emit mixed aliases" directive
3. **Directory-level target layout** (B lines 118-130) — holistic view missing from A
4. **Conciseness pass** — tighten A's language where possible without losing substance
