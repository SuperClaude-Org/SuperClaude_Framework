# Base Selection

**Pipeline**: sc:adversarial comparison of 3 approaches
**Date**: 2026-02-23

---

## Selected Base: Approach 2 (claude -p as Primary Invocation)

### Selection Evidence

| Dimension | Ap1 Score | Ap2 Score | Ap3 Score | Winner |
|-----------|-----------|-----------|-----------|--------|
| Reliability | 9/10 | 7/10 | 9/10 | Ap1/Ap3 tie |
| Implementation Complexity | 3/10 | 8/10 | 4/10 | **Ap2** |
| Pipeline Fidelity | 5/10 | 8/10 | 9/10 | Ap3 |
| Risk Management | 9/10 | 8/10 | 8/10 | Ap1 |
| Maintainability | 5/10 | 8/10 | 5/10 | **Ap2** |
| Sprint Fit | 4/10 | 9/10 | 5/10 | **Ap2** |
| **Combined (hybrid rubric)** | **0.667** | **0.900** | **0.825** | **Ap2** |

### Selection Rationale

Approach 2 wins on the three dimensions that matter most for sprint execution: **Implementation Complexity** (8 vs 4 and 3), **Maintainability** (8 vs 5 and 5), and **Sprint Fit** (9 vs 5 and 4).

The dimensions where Approach 2 scores lower (Reliability, Pipeline Fidelity) are precisely the dimensions where targeted improvements from Approaches 1 and 3 can be absorbed without changing Approach 2's core architecture.

Specifically:
- **Reliability gap** (7/10 → 9/10): Close by absorbing Approach 1's behavioral adherence testing and Approach 3's simplified mid-pipeline awareness.
- **Fidelity gap** (8/10 → 9/10): Close by absorbing Approach 3's enhanced 5-step fallback with real convergence tracking.

These absorptions are additive improvements to Approach 2's existing structure. They do NOT require architectural changes (no routing tree, no dual-path, no new flags).

### Why Not Approach 3?

Approach 3 has the highest Pipeline Fidelity (9/10) and shares the highest Reliability (9/10). However, its Sprint Fit (5/10) and Maintainability (5/10) are disqualifying for the current sprint scope. The dual-path architecture, routing decision tree, `--invocation-mode` flag, and enhanced Task-agent pipeline together represent ~40-60% more implementation work than Approach 2. The marginal quality improvement does not justify this scope expansion.

The specific elements of Approach 3 that ARE valuable (enhanced 5-step fallback, mid-pipeline awareness, `invocation_method` field) can be absorbed into Approach 2's primary/fallback architecture at a fraction of the complexity cost.

### Why Not Approach 1?

Approach 1 is not a competing design — it's a pre-gate. It correctly identifies the risk of committing to `claude -p` without testing, but it does not provide an implementation specification. The probe's most valuable elements (behavioral adherence rubric, multi-round verification) are absorbed into the merged approach as Task 0.0 enhancements and post-implementation verification criteria.
