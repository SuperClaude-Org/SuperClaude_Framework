---
spec_source: .dev/releases/current/v.2.08-roadmap-v4/brainstorm-roadmap.md
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 1
work_milestones: 4
interleave_ratio: "1:3"
major_issue_policy: stop-and-fix
complexity_class: LOW
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:3** (one validation milestone per three work milestones), derived from complexity class **LOW** (score: 0.378)

**Note on this roadmap's complexity**: The 1:3 ratio reflects the LOW complexity score of the *specification document*. However, the *implementation* involves behavioral changes to sc:roadmap's generation pipeline that have medium implementation risk (R-006, R-008, R-013 are High severity). The validation milestone (V1) is therefore positioned at a critical point: after M1-M3 are complete and before M4's conditional pass is attempted. This matches the spec's Phase 2 boundary (M1+M2+M3 = Phase 2 complete).

---

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M3 (Guard and Sentinel Analysis) | Full Phase 2 validation: M1 (decomposition + schema), M2 (invariant registry + FMEA), M3 (guard analysis). Validates: all three passes compose correctly in sequence; release gating works end-to-end; no regressions in existing roadmap generation. | Any Critical issue; more than 1 Major issue; release gate rules not enforced; invariant registry empty for a spec with known state variables; FMEA silent corruption not triggered for a known case |

**Placement rationale**: V1 after M3 (not after M1 or M2) because the 1:3 ratio places one validation after the first three work milestones. V1 validates the full Phase 2 boundary — the point at which the core detection methodology (M1+M2+M3) is complete and M4's data flow tracing can proceed if the go/no-go pilot succeeds.

---

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Release Gate Rule 1/2/3 not enforced; existing roadmap generation produces different output (regression); invariant registry produces incorrect cross-references |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | State variable detector misses a pattern present in the source bugs; FMEA produces no output for a computational deliverable with known degenerate cases; guard analysis misses bool→int transition |
| Minor | Log, address in next validation pass | Accumulated count >5 triggers review | Deliverable count higher than expected (R-003); synonym dictionary entry missing; acceptance criteria wording vague |
| Info | Log only, no action required | N/A | Alternative implementation approach worth considering; optimization opportunity in pipeline execution order |

---

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | (1) All behavioral deliverables in test spec appear as `.a/.b` pairs. (2) Non-behavioral deliverables pass through unchanged. (3) Decomposition is idempotent. (4) Each `.b` deliverable contains at least one state assertion or boundary case (Release Gate Rule 3). | All 4 criteria met; 0 Critical issues; ≤1 Major issue |
| M2 | (1) Invariant registry section present in output for a spec with `self._*` patterns. (2) FMEA failure mode table generated for deliverable with computational verb. (3) Silent corruption classified as highest severity. (4) Release Gate Rule 1 triggered for a known silent corruption case. (5) Dual detection Signal 2 independently fires even when no invariant registered. | All 5 criteria met; 0 Critical issues; ≤1 Major issue |
| M3 | (1) Bool→int type change detected in deliverable description. (2) Ambiguity for value `0` flagged. (3) Release Gate Rule 2 generates warning with mandatory owner field. (4) Unambiguous boolean guard produces no flag. (5) Guard severity correctly elevated when FMEA has registered silent corruption for same variable. | All 5 criteria met; 0 Critical issues; ≤1 Major issue |
| V1 (Phase 2 validation) | (1) M1→M2→M3 pipeline composes correctly in sequence (idempotent, no interference between passes). (2) Release Gate Rules 1, 2, and 3 all enforceable end-to-end. (3) No regressions in roadmap generation for a spec with no state variables or computational deliverables (existing behavior unchanged). (4) M2 FMEA detects the v0.04 Bug 2 pattern (empty tail → silent zero offset) when given a representative spec. (5) M2 Invariant Registry detects the v0.04 Bug 1 pattern (wrong-operand decrement) when given a representative spec. | All 5 criteria met; 0 Critical issues; ≤2 Major issues |
| M4 | (1) Below 6-milestone threshold: skip summary present, M2 reference included. (2) Above threshold: cross-milestone edge for a known state variable detected. (3) Scope mismatch conflict detected. (4) Pilot go/no-go decision documented with evidence before general enablement (D4.6b accepted). | All 4 criteria met; 0 Critical issues; ≤1 Major issue |

---

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (State Variable Invariant Registry) | V1 | M2 | Regression test: spec with `self._*` patterns → verify invariant registry section present and cross-referenced |
| FR-002 (FMEA Pass) | V1 | M2 | Regression test: spec with computational verb → verify failure mode table generated |
| FR-003 (Guard and Sentinel Analysis) | V1 | M3 | Regression test: spec with bool→int type change → verify ambiguity flagged |
| FR-004 (Implement/Verify Decomposition) | V1 | M1 | Regression test: known spec → verify .a/.b pairs for all behavioral deliverables |
| FR-005 (Cross-Deliverable Data Flow Tracing) | Post-pilot | M4 | Pilot test: one 6+ milestone roadmap → verify cross-milestone contracts extracted |
| FR-006 (State variable scan automation) | V1 | M2 | Unit test: state variable detector on representative deliverable descriptions |
| FR-007 (Computational verb scan automation) | V1 | M2 | Unit test: FMEA trigger on representative deliverable descriptions |
| FR-008 (Silent corruption = highest severity) | V1 | M2 | Unit test: classifier with "offset advances by wrong amount, no error" → highest severity output |
| FR-009 (Guard transition analysis for type changes) | V1 | M3 | Unit test: bool→int deliverable → transition analysis triggered |
| FR-010 (Data flow trace fields) | Post-pilot | M4 | Pilot test: verify birth/write/read/contract/conflict all captured |
| NFR-001 (Medium cost for P1+P2) | V1 | M2 | Implementation review: no new external dependencies introduced; pipeline add-on only |
| NFR-002 (Low cost for P3+P4) | V1 | M1, M3 | Implementation review: structural changes only; no external dependencies |
| NFR-003 (High cost for P5, conditional) | Post-pilot | M4 | D4.6 pilot measurement: overhead recorded and compared against defects prevented |
| NFR-004 (Composability, incremental adoption) | V1 | M1-M3 | Integration test: disable M2 pass → M1 output still valid; disable M3 → M1+M2 still valid |
| NFR-005 (Dual-purpose artifacts) | V1 | M1-M3 | Manual review: invariant tables, failure mode tables, guard tables usable as review checklists |
| SC-001 (Bug 1 class caught by M1+M2) | V1 | M1, M2 | Regression test: representative spec with wrong-operand pattern → invariant registry flags it |
| SC-002 (Bug 2 class caught by M2+M3) | V1 | M2, M3 | Regression test: representative spec with bool→int zero ambiguity → guard analysis + FMEA both flag it |
| SC-003 (All artifacts dual-purpose) | V1 | M1-M3 | Manual review: artifacts usable as implementation guidance and review checklists |
| SC-004 (Incremental adoption) | V1 | M1-M3 | Integration test: Phase 1 (M1 only), Phase 2 (M1+M2+M3) produce valid incremental outputs |
| SC-005 (Silent corruption blocked by Release Gate Rule 1) | V1 | M2 | End-to-end test: silent corruption finding → pipeline blocks downstream milestone with explicit gate message |
