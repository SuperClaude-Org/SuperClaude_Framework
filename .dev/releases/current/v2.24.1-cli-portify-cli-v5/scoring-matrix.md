# Scoring Matrix: Approach A vs Approach B

**Date**: 2026-03-13
**Orchestrator**: Debate Orchestrator (Opus 4.6)

---

## Criteria Definitions

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Simplicity | 20% | Number of new concepts, files, abstractions, and cognitive overhead |
| Correctness | 25% | Complete and accurate resolution of all 3 gaps (input target, discovery, subprocess scoping) |
| Backward Compat | 15% | Impact on existing CLI invocations, API surfaces, step numbering, and test suites |
| Testability | 15% | Unit test isolation, test surface area, fixture complexity |
| Consistency | 15% | Alignment with existing SuperClaude patterns (pipeline/, sprint/, models.py conventions) |
| Extensibility | 10% | Support for future requirements (multi-skill, partial portification, debugging, reuse) |

---

## Raw Scores (1-10)

| Criterion | Weight | Approach A | Approach B | Delta | Favors |
|-----------|--------|-----------|-----------|-------|--------|
| Simplicity | 20% | 8 | 5 | +3 | A |
| Correctness | 25% | 9 | 9 | 0 | Tie |
| Backward Compat | 15% | 8 | 6 | +2 | A |
| Testability | 15% | 8 | 7 | +1 | A |
| Consistency | 15% | 8 | 6 | +2 | A |
| Extensibility | 10% | 5 | 9 | -4 | B |

---

## Weighted Calculation

| Criterion | Approach A (score * weight) | Approach B (score * weight) |
|-----------|----------------------------|----------------------------|
| Simplicity (20%) | 8 * 0.20 = 1.60 | 5 * 0.20 = 1.00 |
| Correctness (25%) | 9 * 0.25 = 2.25 | 9 * 0.25 = 2.25 |
| Backward Compat (15%) | 8 * 0.15 = 1.20 | 6 * 0.15 = 0.90 |
| Testability (15%) | 8 * 0.15 = 1.20 | 7 * 0.15 = 1.05 |
| Consistency (15%) | 8 * 0.15 = 1.20 | 6 * 0.15 = 0.90 |
| Extensibility (10%) | 5 * 0.10 = 0.50 | 9 * 0.10 = 0.90 |
| **TOTAL** | **7.95** | **7.00** |

---

## Winner

**Approach A (Command-Centric Resolution)** wins with a weighted score of **7.95** vs **7.00** (delta: +0.95).

Approach A wins 4 of 6 criteria, ties on 1, and loses on 1 (Extensibility). The margin is decisive -- even re-weighting Extensibility to 20% (doubling it) and reducing Simplicity to 10% (halving it) would produce A: 7.45 vs B: 7.40, still a narrow A win.

---

## Sensitivity Analysis

The only weight configuration that flips the result to Approach B requires:
- Extensibility weight raised to 30%+ AND
- Simplicity weight reduced to 5% or less

This represents a value system that prioritizes future flexibility over current implementation cost -- reasonable for a major version, but not for a v2.24.1 patch release.

---

## Incorporation from Loser

Three elements from Approach B are incorporated into the synthesized spec:

| Element | Source | Justification |
|---------|--------|---------------|
| Resolution log artifact | B, Section 5.3 | Self-documenting debuggability; low implementation cost |
| `--include-agent` CLI flag | B, Section 4.3 | Escape hatch for heuristic failures; essential for correctness |
| `--save-manifest` CLI flag | B, Section 4.4 | Debug workflow; write-only (no load); minimal complexity |

---

*Scoring completed: 2026-03-13*
