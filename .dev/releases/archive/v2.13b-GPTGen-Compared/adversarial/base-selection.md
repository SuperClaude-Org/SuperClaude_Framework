# Base Selection: Tasklist-Index Comparison

## Quantitative Scoring (50% weight)

| Metric | Weight | GPT5.4 (A) | Opus4.6 (B) | Notes |
|--------|--------|--------------------|--------------------|-------|
| Requirement Coverage (RC) | 0.30 | 0.76 (13/17 roadmap items mapped to tasks) | 1.00 (20/20 roadmap items mapped 1:1) | B achieves perfect 1:1 mapping |
| Internal Consistency (IC) | 0.25 | 0.82 (3 contradictions: fabricated deps X-001, R-003 mapping X-003, Phase 4 tier debatable X-002) | 0.93 (1 contestable issue: Phase 4 EXEMPT debatable X-002) | A has 3 inconsistencies vs B's 1 |
| Specificity Ratio (SR) | 0.15 | 0.55 ("characterization plan" deliverables, "M" effort across board, no concrete file names) | 0.88 (test_watchdog.py, pytest commands, `grep -n` criteria, XS/S/M sizing, case counts) | B dramatically more specific |
| Dependency Completeness (DC) | 0.15 | 0.90 (all internal refs resolve; sequential deps are self-consistent even if incorrect) | 0.95 (all refs resolve; TASKLIST_ROOT used consistently; dependency chains valid) | Both strong; B slightly better |
| Section Coverage (SC) | 0.15 | 0.92 (12/13 sections vs B's max; missing Generation Notes detail) | 1.00 (all sections present including detailed Generation Notes) | B is the reference maximum |

**Quantitative Formula**: `quant_score = (RC x 0.30) + (IC x 0.25) + (SR x 0.15) + (DC x 0.15) + (SC x 0.15)`

| Variant | RC (0.30) | IC (0.25) | SR (0.15) | DC (0.15) | SC (0.15) | **Quant Score** |
|---------|-----------|-----------|-----------|-----------|-----------|-----------------|
| A | 0.228 | 0.205 | 0.083 | 0.135 | 0.138 | **0.789** |
| B | 0.300 | 0.233 | 0.132 | 0.143 | 0.150 | **0.957** |

## Qualitative Scoring (50% weight) -- Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | GPT5.4 (A) | Opus4.6 (B)|
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements from source input | NOT MET -- 13 deliverables vs roadmap's 20 | MET -- 20/20 deliverables, 1:1 mapping |
| 2 | Addresses edge cases and failure scenarios | NOT MET -- no rollback strategies | MET -- rollback per task, risk drivers noted |
| 3 | Includes dependencies and prerequisites | MET -- sequential deps documented (though incorrect) | MET -- deps documented per task |
| 4 | Defines success/completion criteria | MET -- acceptance criteria per task | MET -- acceptance criteria with concrete commands |
| 5 | Specifies what is explicitly out of scope | NOT MET -- no scope exclusions | NOT MET -- no explicit scope exclusions |

**Completeness**: A = 2/5, B = 4/5

### Correctness (5 criteria)

| # | Criterion | GPT5.4 (A) | Opus4.6 (B)|
|---|-----------|-----------|-----------|
| 1 | No factual errors or hallucinated claims | NOT MET -- X-001 fabricated sequential deps; X-003 R-003 mapping error | MET -- no identified factual errors |
| 2 | Technical approaches are feasible | MET -- all approaches feasible | MET -- all approaches feasible |
| 3 | Terminology used consistently | MET -- consistent throughout | MET -- consistent throughout |
| 4 | No internal contradictions | NOT MET -- X-001, X-003 contradictions with roadmap source | MET -- internally consistent |
| 5 | Claims supported by evidence or rationale | MET -- traceability matrix with confidence scores | MET -- traceability matrix with confidence scores |

**Correctness**: A = 3/5, B = 5/5

### Structure (5 criteria)

| # | Criterion | GPT5.4 (A) | Opus4.6 (B)|
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | MET -- standard tasklist-index structure | MET -- standard tasklist-index structure |
| 2 | Consistent hierarchy depth | MET -- uniform depth throughout | MET -- uniform depth throughout |
| 3 | Clear separation of concerns | MET -- phases well-separated | MET -- phases well-separated |
| 4 | Navigation aids (TOC, cross-refs) | MET -- artifact paths, phase files, registries | MET -- artifact paths, phase files, registries |
| 5 | Follows conventions of artifact type | MET -- follows tasklist-index spec | MET -- follows tasklist-index spec |

**Structure**: A = 5/5, B = 5/5

### Clarity (5 criteria)

| # | Criterion | GPT5.4 (A) | Opus4.6 (B)|
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | NOT MET -- "characterization plan" deliverables are ambiguous (plan doc vs test code?) | MET -- "test suite (3 cases)" is unambiguous |
| 2 | Concrete rather than abstract | NOT MET -- no test file names, no pytest commands, no grep criteria | MET -- test_watchdog.py, `uv run pytest`, `grep -n` |
| 3 | Each section has clear purpose | MET -- sections purposeful | MET -- sections purposeful |
| 4 | Acronyms and domain terms defined | MET -- NFR-007 referenced, tiers explained | MET -- NFR-007, NFR-004 referenced |
| 5 | Actionable next steps clearly identified | NOT MET -- steps are generic ("Load roadmap context", "Check dependencies") | MET -- steps name exact files, commands, line ranges |

**Clarity**: A = 2/5, B = 5/5

### Risk Coverage (5 criteria)

| # | Criterion | GPT5.4 (A) | Opus4.6 (B)|
|---|-----------|-----------|-----------|
| 1 | Identifies >= 3 risks with probability/impact | NOT MET -- no explicit risk identification beyond "Risk: Low" | MET -- Source Snapshot cites "5 risks identified; highest: hook refactor breaking SIGTERM" |
| 2 | Mitigation strategy for each risk | NOT MET -- no mitigation strategies | MET -- characterization tests as safety net, per-commit isolation |
| 3 | Failure modes and recovery procedures | NOT MET -- no rollback strategies | MET -- rollback per task (git revert, file deletion) |
| 4 | External dependency failure scenarios | NOT MET | NOT MET |
| 5 | Monitoring/validation mechanism for risk detection | MET -- checkpoints at phase boundaries | MET -- checkpoints + mid-phase checkpoint |

**Risk Coverage**: A = 1/5, B = 4/5

### Qualitative Summary

| Dimension | GPT5.4 (A) | Opus4.6 (B)|
|-----------|-----------|-----------|
| Completeness | 2/5 | 4/5 |
| Correctness | 3/5 | 5/5 |
| Structure | 5/5 | 5/5 |
| Clarity | 2/5 | 5/5 |
| Risk Coverage | 1/5 | 4/5 |
| **Total** | **13/25** | **23/25** |

**Qualitative Score**: A = 0.520, B = 0.920

## Position-Bias Mitigation

| Dimension | Variant | Pass 1 (A,B order) | Pass 2 (B,A order) | Agreement | Final |
|-----------|---------|---------------------|---------------------|-----------|-------|
| Completeness | A | 2/5 | 2/5 | Yes | 2/5 |
| Completeness | B | 4/5 | 4/5 | Yes | 4/5 |
| Correctness | A | 3/5 | 3/5 | Yes | 3/5 |
| Correctness | B | 5/5 | 5/5 | Yes | 5/5 |
| Structure | A | 5/5 | 5/5 | Yes | 5/5 |
| Structure | B | 5/5 | 5/5 | Yes | 5/5 |
| Clarity | A | 2/5 | 2/5 | Yes | 2/5 |
| Clarity | B | 5/5 | 5/5 | Yes | 5/5 |
| Risk Coverage | A | 1/5 | 1/5 | Yes | 1/5 |
| Risk Coverage | B | 4/5 | 4/5 | Yes | 4/5 |

Disagreements found: 0
Verdicts changed: 0

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | **Combined Score** |
|---------|-------------|------------|-------------------|
| A (Current) | 0.789 x 0.50 = 0.395 | 0.520 x 0.50 = 0.260 | **0.655** |
| B (Backlog) | 0.957 x 0.50 = 0.479 | 0.920 x 0.50 = 0.460 | **0.939** |

**Margin**: 28.4% (well outside 5% tiebreaker threshold)
**Tiebreaker applied**: No

## Selected Base: Opus4.6 (B)(B)

**Selection Rationale**: Opus4.6 (B)wins decisively across all scoring dimensions. It achieves perfect requirement coverage (1:1 roadmap mapping), higher internal consistency (no fabricated dependencies), dramatically better specificity (concrete test files, commands, grep criteria), and superior qualitative scores in completeness (4/5 vs 2/5), correctness (5/5 vs 3/5), clarity (5/5 vs 2/5), and risk coverage (4/5 vs 1/5). The only dimension where both tie is structure (5/5). The 28.4% margin is the largest possible indicator of clear superiority.

**Strengths to Preserve from Base (Opus4.6)**:
- 1:1 roadmap-to-task mapping (20 tasks, 20 deliverables)
- Phase 1 independence (no fabricated sequential deps)
- Concrete deliverables with test file names, pytest commands, grep criteria
- Rollback strategies per task
- TASKLIST_ROOT-relative paths
- Mid-phase checkpoint in Phase 2
- XS/S/M effort calibration
- Separate NFR-007 verification tasks

**Strengths to Incorporate from GPT5.4 (A)**:
1. **Phase 4 tier resolution**: X-002 remains contested. Both advocates partially conceded. The merged output should resolve Phase 4 tier to a defensible middle ground.
2. **Strategic context capture**: GPT5.4 (A)'s Source Snapshot-style capture of "executor unification is non-goal" should be preserved or strengthened in the merged Source Snapshot.
3. **Visual confidence indicators**: GPT5.4 (A)'s `[████████--] 80%` format is more scannable than bare percentages.
