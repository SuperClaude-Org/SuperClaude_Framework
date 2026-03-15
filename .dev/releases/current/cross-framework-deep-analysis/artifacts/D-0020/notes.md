---
deliverable: D-0020
task: T05.03
title: OQ-004 Resolution — Discard-Both Verdict Handling for Phase 7
status: complete
discard_both_count: 0
generated: 2026-03-15
---

# D-0020: OQ-004 Resolution — Discard-Both Verdict Handling

## Resolution Statement

**OQ-004 is resolved with zero "discard both" verdicts.**

Review of all 8 comparison files in D-0018 found no comparison pair that received a "discard both" verdict class. The verdict class distribution is:

| Verdict Class | Count |
|---|---|
| IC stronger | 5 |
| split by context | 3 |
| LW stronger | 0 |
| no clear winner | 0 |
| discard both | 0 |

---

## OQ-004 Rule Statement

Per the Phase 5 tasklist, OQ-004 establishes: for any "discard both" verdict, Phase 7 (T07.04) shall produce an IC-native improvement item with explicit rationale; placeholder omission is not permitted.

---

## Per-Pair Discard-Both Check

| Comparison Pair | Verdict Class | Discard Both? | Phase 7 IC-Native Item Required? |
|---|---|---|---|
| comparison-roadmap-pipeline.md | split by context | No | No |
| comparison-sprint-executor.md | IC stronger | No | No |
| comparison-pm-agent.md | split by context | No | No |
| comparison-adversarial-pipeline.md | IC stronger | No | No |
| comparison-task-unified-tier.md | IC stronger | No | No |
| comparison-quality-agents.md | split by context | No | No |
| comparison-pipeline-analysis.md | IC stronger | No | No |
| comparison-cleanup-audit.md | IC stronger | No | No |

**Result**: Zero "discard both" verdicts across all 8 pairs.

---

## Phase 7 Reference

T07.04 is the responsible execution task for IC-native improvement items arising from "discard both" verdicts. With zero "discard both" verdicts, T07.04 has no OQ-004 obligations from Phase 5 comparisons. T07.04 should record this explicitly in its own deliverable.

---

## Why No "Discard Both" Verdicts

The absence of "discard both" verdicts is consistent with the D-0010 finding that all 8 IC component groups have at least one functional analog in llm-workflows. Even in partial-mapping pairs (Cleanup-Audit, Pipeline Analysis), the IC component had demonstrable strengths justifying an "IC stronger" verdict rather than discarding both. LW components, even where their implementation vehicles are weak (bash scripts, behavioral-only rules), contributed adoptable patterns that prevented a "discard both" classification.

---

## Acceptance Criteria Check

| Criterion | Required | Actual | Status |
|---|---|---|---|
| File `D-0020/notes.md` exists | Yes | Yes | PASS |
| Complete list of "discard both" pairs with IC-native improvement directions | Yes | Present (count = 0) | PASS |
| Zero "discard both" verdicts without IC-native improvement direction | Yes | N/A (0 discard-both verdicts) | PASS |
| Resolution stable: same comparison files → same discard-both list | Yes | Deterministic (0) | PASS |
| Document explicitly references Phase 7 (T07.04) | Yes | Yes | PASS |
