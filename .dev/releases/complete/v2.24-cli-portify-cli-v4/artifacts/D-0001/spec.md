---
deliverable_id: D-0001
task_id: T01.01
roadmap_item: R-001
phase: 1
type: decision-record
status: FINAL
---

# D-0001: Blocking Spec Ambiguity Resolution Record

## Purpose

Resolve 4 blocking spec ambiguities identified in Roadmap Phase 0 before implementation begins. Each decision includes rationale derived from roadmap text or DEV-001, and is triaged as must-resolve, safe-default, or defer-to-follow-up with blocking-phase annotations.

---

## Resolution 1: Timeout Semantics for Convergence Iterations

**Question**: Per-iteration independent timeout vs. total timeout divided by `max_convergence`?

**Decision**: Per-iteration independent timeout (default 300s).

**Triage**: Must-resolve `[Blocking Phase 5]`

**Rationale**: The roadmap Phase 5 explicitly states: "Per-iteration independent timeout (default 300s, per Phase 0 decision)." Each convergence iteration in `panel-review` (Step 7) receives its own independent 300-second timeout. This means that if `max_convergence=3`, the theoretical maximum wall-clock time for the convergence loop is 3 x 300s = 900s, not 300s / 3 = 100s per iteration.

**Impact on `PortifyConfig`**: Requires a single `iteration_timeout` field (default 300s). No separate `total_budget` field is needed for timeout semantics. The `max_convergence` field controls iteration count, not timeout division.

**Source**: Roadmap Phase 5, Work Item 3 (panel-review); SC-016 validation criterion.

---

## Resolution 2: Resume Behavior for Partially Written `synthesize-spec`

**Question**: Re-run `synthesize-spec` vs. skip when output is partial?

**Decision**: Prefer re-running `synthesize-spec` over trusting partially gated output.

**Triage**: Must-resolve `[Blocking Phase 4]`

**Rationale**: The roadmap Phase 4, Work Item 3 (synthesize-spec) explicitly states: "Resume policy: prefer re-running `synthesize-spec` over trusting partially gated output (per Phase 0 decision)." A partially written spec that failed its STRICT gate (SC-005: zero remaining `{{SC_PLACEHOLDER:*}}` sentinels) cannot be trusted. Re-running is safer because:
1. The gate failure means the output is incomplete by definition.
2. Partial artifacts may have structural corruption beyond the specific gate failure.
3. The cost of re-running one Claude subprocess is far lower than the cost of downstream failures from a corrupt spec.

**Impact on `PortifyStepResult`**: The `resume_context` for `synthesize-spec` should mark the step as "re-run required" rather than "skip to next." The `resume.py` module's decision table must classify `synthesize-spec` as re-runnable (not skip-eligible) on partial failure.

**Source**: Roadmap Phase 4, Work Item 3; Risk R-7 mitigation.

---

## Resolution 3: Scoring Precision and 7.0 Boundary Rounding Behavior

**Question**: How is the 7.0 downstream readiness boundary handled with respect to rounding?

**Decision**: Boundary is exact: 7.0 evaluates to `true` (pass), 6.9 evaluates to `false` (fail). No rounding is applied.

**Triage**: Must-resolve `[Blocking Phase 5]`

**Rationale**: The roadmap Phase 5 explicitly states: "Downstream readiness gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false)." The SC-009 validation criterion confirms: "Downstream: 7.0 true, 6.9 false." The overall score is computed as the arithmetic mean of 4 quality dimensions (clarity, completeness, testability, consistency), and the comparison uses `>=` with no rounding. This means:
- `overall = 7.0` -> gate passes
- `overall = 6.99999` -> gate fails
- `overall = 7.0001` -> gate passes
- Arithmetic precision is maintained to at least 2 decimal places (+/-0.01 per SC-008).

**Impact on gate implementation**: The gate function must use `>=` comparison with no rounding. The SC-008 criterion ("Overall = mean(4 dimensions) +/-0.01") defines the acceptable precision tolerance for the arithmetic computation, not a rounding policy for gate evaluation.

**Source**: Roadmap Phase 5, Work Item 3; SC-008 and SC-009 validation criteria.

---

## Resolution 4: Authoritative Module Layout

**Question**: Section 4.1 (13 files) vs. Section 4.6 (roadmap 18 modules) -- which is authoritative?

**Decision**: 18-module structure per DEV-001 accepted deviation is authoritative. The roadmap's module layout supersedes the spec's original Section 4.1 table.

**Triage**: Must-resolve `[Blocking Phase 1]`

**Rationale**: DEV-001 (disposition: ACCEPTED) formally resolves this conflict. The roadmap was produced through a two-round adversarial debate between Opus-Architect and Haiku-Architect, achieving a convergence score of 0.72. The debate produced validated architectural improvements including:
1. `steps/` subdirectory layout (D-02 consensus) replacing flat `pipeline_steps.py`
2. `executor.py` as first-class module (D-04 consensus) extracted from `cli.py`
3. `convergence.py` with `ConvergenceState` enum (D-11 consensus)
4. `resume.py` as dedicated module (D-12 consensus)
5. `contract.py` for return contract emission (Opus original, unchallenged)
6. `monitor.py` merging `tui.py`, `logging_.py`, `diagnostics.py` (D-14/coherence)
7. `cli.py` replacing `commands.py` (naming alignment)

The accepted architecture has 18 modules (excluding `__init__.py`): 11 top-level modules + 7 `steps/` modules.

**Impact**: All implementation tasks must use the roadmap's 18-module structure. The spec's Section 4.1 table is superseded. Implementers MUST NOT create `commands.py`, `tui.py`, `logging_.py`, `diagnostics.py`, or `pipeline_steps.py`.

**Source**: DEV-001 accepted deviation document; Roadmap Section 4.1; debate-transcript.md decisions D-02, D-04, D-11, D-12, D-14.

---

## Summary

| # | Ambiguity | Decision | Triage | Blocking Phase |
|---|-----------|----------|--------|----------------|
| 1 | Timeout semantics | Per-iteration independent (300s default) | Must-resolve | Phase 5 |
| 2 | Resume behavior for synthesize-spec | Re-run (not skip) | Must-resolve | Phase 4 |
| 3 | Scoring precision / 7.0 boundary | Exact >= 7.0, no rounding | Must-resolve | Phase 5 |
| 4 | Authoritative module layout | 18-module per DEV-001 | Must-resolve | Phase 1 |

All 4 ambiguities are classified as **must-resolve**. None are deferred to follow-up. Each resolution has explicit roadmap or DEV-001 text as its source of truth.
