---
spec_source: docs/generated/unified-audit-gating-v1.2.1-release-spec.md
generated: 2026-03-03T00:00:00Z
generator: sc:roadmap
complexity_score: 0.654
complexity_class: MEDIUM
domain_distribution:
  frontend: 0
  backend: 45
  security: 25
  performance: 20
  documentation: 10
primary_persona: architect
consulting_personas: [backend, security]
milestone_count: 6
milestone_index:
  - id: M1
    title: Blocker Resolution and Decision Lock
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 5
    risk_level: High
  - id: M2
    title: State Machine Implementation and Illegal-Transition Test Suite
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 8
    risk_level: High
  - id: M3
    title: Deterministic Gate Evaluator and Profile Test Suite
    type: FEATURE
    priority: P0
    dependencies: [M1, M2]
    deliverable_count: 8
    risk_level: High
  - id: M4
    title: Runtime Controls, Override Governance, Override Test Suite, and Reliability Hardening
    type: FEATURE
    priority: P1
    dependencies: [M1, M2, M3]
    deliverable_count: 13
    risk_level: High
  - id: M5
    title: Sprint CLI Regression Gate
    type: TEST
    priority: P1
    dependencies: [M2, M4]
    deliverable_count: 5
    risk_level: Medium
  - id: M6
    title: Rollout Validation, Rollback Drill, and Phase Promotion Gate
    type: TEST
    priority: P0
    dependencies: [M3, M4, M5]
    deliverable_count: 10
    risk_level: High
total_deliverables: 49
total_risks: 13
estimated_phases: 4
validation_score: 0.0
validation_status: SKIPPED
adversarial:
  mode: multi-roadmap
  agents:
    - opus:architect:"deterministic contracts first"
    - sonnet:qa:"validation and acceptance rigor"
    - haiku:analyzer:"risk/reliability and rollout safety"
  convergence_score: 0.92
  base_variant: sonnet:qa
  artifacts_dir: .dev/releases/current/unified-audit-gating-v1.2.1/adversarial/
---

# Roadmap: Unified Audit Gating System v1.2.1

**Document date**: 2026-03-03
**Base variant**: V2 (sonnet:qa) — score 0.9488
**Integrations from**: V1 (opus:architect) [U-001, U-002], V3 (haiku:analyzer) [U-005, U-006]
**Adversarial convergence**: 92% across 3 debate rounds (deep depth)
**Source specification**: `docs/generated/unified-audit-gating-v1.2.1-release-spec.md`

---

## Overview

This roadmap drives delivery of the Unified Audit Gating System v1.2.1 from a validation-first perspective, enhanced with architectural decisions from the contracts-first variant and reliability hardening from the risk-first variant.

The central premise is that **testing milestones cannot be deferred to the end of a release cycle** when the feature under test is itself a gating mechanism. A state machine that controls task, milestone, and release completions will be exercised under adversarial conditions from the moment the first prototype exists. Any gap in test coverage of illegal transitions, override governance failures, or rollback triggers becomes a production escape path.

The four current blockers — unfinalized profile thresholds, unresolved retry/backoff/timeout values, undefined rollback triggers, and unassigned decision owners — are not documentation gaps. Each one makes a corresponding test suite non-deterministic or untestable. No milestone that depends on these inputs can reach a passing acceptance gate until the blockers are closed. The roadmap therefore opens with a dedicated milestone (M1) that treats blocker resolution as a testable deliverable with explicit closure criteria.

<!-- Provenance: QA base (V2) overview, unchanged -->

The state machine transition validator uses a **closed-world assumption**: only transitions explicitly listed in the transition table are legal; all others are illegal by default. This eliminates an entire class of bypass vulnerabilities where new states are added without declaring transitions. Additionally, the release override prohibition is enforced at two independent layers: at OverrideRecord construction time (compile-time defense) and at transition validation time (runtime defense).

<!-- Provenance: Integrated from V1 (Architect) U-001 closed-world, U-002 compile-time override -->

Reliability controls (lease, heartbeat, retry, timeout, deadlock resistance) are proven under fault injection before any rollout phase begins. The rollout milestone is structured with explicit sub-phase ordering: Shadow-to-Soft promotion must be signed off before Soft enforcement deliverables begin, and the rollback drill must pass before Soft-to-Full promotion can be approved.

<!-- Provenance: Integrated from V3 (Analyzer) U-005 reliability hardening, U-006 rollout granularity -->

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Blocker Resolution and Decision Lock | FEATURE | P0 | M | None | 5 | High |
| M2 | State Machine Implementation and Illegal-Transition Test Suite | FEATURE | P0 | L | M1 | 8 | High |
| M3 | Deterministic Gate Evaluator and Profile Test Suite | FEATURE | P0 | L | M1, M2 | 8 | High |
| M4 | Runtime Controls, Override Governance, Override Test Suite, and Reliability Hardening | FEATURE | P1 | XL | M1, M2, M3 | 13 | High |
| M5 | Sprint CLI Regression Gate | TEST | P1 | M | M2, M4 | 5 | Medium |
| M6 | Rollout Validation, Rollback Drill, and Phase Promotion Gate | TEST | P0 | L | M3, M4, M5 | 10 | High |

---

## Dependency Graph

```
M1 (Blocker Resolution)
  --> M2 (State Machine + Illegal-Transition Tests)
  --> M3 (Evaluator + Profile Tests)  [also depends on M2 for state enum baseline]
  --> M4 (Runtime Controls + Override Tests + Reliability Hardening)  [also depends on M2, M3]

M2 --> M5 (Sprint CLI Regression)
M4 --> M5

M3 --> M6 (Rollout Validation + Rollback Drill)
M4 --> M6
M5 --> M6
```

Shadow-to-Soft promotion gate requires: M1 + M4 (determinism) + M3 (evidence) + M4 (stale-running) + M4 (override governance) all passing — per spec Section 7.2.
Soft-to-Full promotion gate requires: M1 through M5 passing for two consecutive windows plus rollback drill (M6).

---

## M1: Blocker Resolution and Decision Lock

### Objective

Establish the four factual inputs that make downstream testing deterministic. Until profile thresholds, retry/backoff/timeout values, rollback triggers, and decision ownership are concretely assigned, any test against these behaviors is testing against a placeholder that will change. This milestone closes the blockers as testable, verifiable artifacts — not as prose commitments.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Profile thresholds and major-severity behavior decision document | Document exists with: numeric threshold values per profile (strict, standard, legacy_migration); explicit pass/fail behavior for major-severity findings at task tier under standard profile; owner name and UTC sign-off date recorded; no [TBD] fields remaining |
| D1.2 | Retry/backoff/timeout policy decision document | Document states: maximum retry attempt budget per scope (task, milestone, release); budget semantics (per-entity vs per-run); backoff strategy with base values; absolute timeout values in seconds per scope; heartbeat interval and missed-heartbeat threshold; owner name and UTC sign-off date; no [TBD] fields remaining |
| D1.3 | Rollback and safe-disable trigger contract | Document enumerates the five normative triggers from spec Section 7.3 with concrete threshold values; emergency safe-disable procedure documented; owner name and UTC sign-off date; no [TBD] fields remaining |
| D1.4 | Open decision registry with owners and UTC deadlines | All five decisions from spec Section 12.4 appear in a tracked registry with owner, UTC deadline, and effective rollout phase; checklist section 10 moves from NO-GO to PASS |
| D1.5 | Override approver model decision | Single-approver vs. dual-approver resolved; review cadence (review_due_at window) specified numerically; owner and UTC deadline recorded |

### Dependencies

None. This milestone is the root of the dependency graph.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Decision owners unavailable or unresponsive | Medium | Critical | Escalate to program manager within 48 hours; spec Section 9.2 assigns program manager role explicitly for this purpose |
| Thresholds set without empirical basis, requiring revision after shadow data | High | High | Mark thresholds as provisional in shadow mode per spec Section 8.1; build profile test suite to accept threshold as injected parameter |
| Decision registry not maintained after initial population | Medium | Medium | Registry must be version-controlled and diff-auditable; changes require owner acknowledgment |
| Rollback trigger thresholds set too conservatively | Low | Medium | Allow one revision cycle before normative lock, require owner sign-off for each revision |

---

## M2: State Machine Implementation and Illegal-Transition Test Suite

### Objective

Implement the normative audit states and transition validator in `models.py`, and build an exhaustive test suite covering every legal and illegal transition defined in spec Sections 4.1 and 4.2. The transition validator uses a **closed-world assumption**: only transitions explicitly listed in the transition table are legal; all other (from_state, to_state) pairs are illegal by default. The OverrideRecord enforces release-scope prohibition at **construction time** (not only at transition validation time), providing defense-in-depth.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `models.py` audit state enums | Six new audit states per scope (ready_for_audit_*, audit_*_running, audit_*_passed, audit_*_failed) for task, milestone, and release; each state has `is_terminal` property; PhaseStatus enum does not regress |
| D2.2 | Transition validator function (closed-world) | `validate_transition(scope, from_state, to_state, override_record=None)` → `(allowed: bool, reason: str)`; closed-world: only listed transitions return allowed=True; test: synthetic state pair not in table returns allowed=False |
| D2.3 | `test_audit_gate_state_machine.py` — legal transitions | One test per legal transition for each scope (task: 6, milestone: 6, release: 5); all 17 legal-transition tests pass |
| D2.4 | `test_audit_gate_state_machine.py` — illegal transitions | One test per illegal transition from spec Section 4.2 items 1-6; all 6 classes covered; each returns allowed=False with non-empty reason |
| D2.5 | `test_audit_gate_state_machine.py` — stuck-state recovery | Tests for: heartbeat timeout → audit_*_failed(timeout); retry from failed → ready_for_audit_* (budget remaining); retry budget exhaustion → permanent failed; reopen from terminal via explicit operation only |
| D2.6 | Validator enforced in `tui.py` completion guard | `tui.py` calls transition validator before every completion/release action; allowed=False raises blocking error with reason string in user-facing message |
| D2.7 | No regression in existing sprint CLI tests | All tests in `tests/sprint/` passing before this milestone continue to pass; `test_regression_gaps.py` scenarios unaffected |
| D2.8 | OverrideRecord compile-time release prohibition | OverrideRecord constructor rejects scope='release' at instantiation time; test: attempt to create OverrideRecord with scope='release' and all other fields valid raises ValueError; independent of and in addition to transition validator prohibition |

### Dependencies

- M1-D1 (profile threshold document) — needed for failure class → profile mapping
- M1-D2 (retry budget values) — needed for stuck-state recovery test parameterization

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| New audit states conflict with existing PhaseStatus in tui.py or executor | Medium | High | Add backward-compatibility test asserting all pre-existing PhaseStatus values remain present with identical properties |
| Illegal-transition validator bypassed by direct state assignment | Medium | Critical | Validate via property setter or __setattr__ hook; test that sets state directly asserts the validator fires |
| Transition validator test coverage incomplete for multi-scope interactions | Low | Medium | Parametrize test suite across all three scopes for every transition type |
| Retry budget semantics ambiguous (per-run vs. per-entity lifetime) | High — M1-D2 must resolve | High | Block M2 retry test authoring until M1-D2 is signed off |
| Closed-world assumption creates false negatives for future legitimate states | Low | Medium | Document: any new state MUST be accompanied by explicit transition declarations |

---

## M3: Deterministic Gate Evaluator and Profile Test Suite

### Objective

Implement the deterministic gate evaluator in `sc-audit-gate-protocol/SKILL.md` that produces a fully specified `GateResult` for every input, and build a profile test suite demonstrating replay stability, failure-class correctness, and evidence completeness. Non-determinism in the evaluator invalidates shadow metrics and makes KPI calibration impossible.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | `sc-audit-gate-protocol/SKILL.md` evaluator behavior contract | Specifies: input contract (scope, entity_id, profile); output contract (GateResult with all fields from spec Section 6.1); failure-class taxonomy; unknown/missing inputs map to failed(unknown) |
| D3.2 | `sc-audit-gate/SKILL.md` command behavior | `/sc:audit-gate` specifies: `--profile strict\|standard\|legacy_migration` as canonical flag; `--strictness` retained as alias only in shadow/soft modes; output includes all required fields |
| D3.3 | GateResult schema conformance | All GateResult outputs include every required field from spec Section 6.1 including drift_summary (edited + non_edited), failure_class |
| D3.4 | `test_audit_gate_profiles.py` — profile determinism | Same input replayed 3 times per profile produces identical GateResult; 9 determinism assertions total, all pass |
| D3.5 | `test_audit_gate_profiles.py` — major-severity behavior | Under `standard` profile at task tier: expected outcome per M1-D1 decision; behavior matches signed decision exactly |
| D3.6 | `test_audit_gate_profiles.py` — unknown/missing input handling | Missing entity_id → failed(unknown); unsupported schema version → failed(unknown); null evidence check → failed (non-completable); all three pass |
| D3.7 | `test_audit_gate_profiles.py` — evidence completeness | Every failed check contains file path or file:line reference; drift_summary has separate edited/non_edited; failed check with no evidence is non-completable |
| D3.8 | `--strictness` alias behavior test | Shadow/soft: `--strictness strict` = `--profile strict`; `legacy_migration` not expressible via strictness; full enforcement: `--strictness` rejected with deprecation message |

### Dependencies

- M1-D1 (profile thresholds) — tests cannot assert threshold pass/fail without finalized numeric values
- M2-D1 (audit state enums) — evaluator output feeds state transitions
- M1-D5 (override approver model) — override block in GateResult must reflect correct approver fields

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Profile threshold values change post-M3 test authoring | Medium | High | Parameterize threshold values as fixtures derived from M1-D1; only fixture changes on threshold revision |
| Evaluator uses LLM/agent judgment for pass/fail | Medium | Critical | Replay stability test (D3.4) required; flag any conditional logic reading non-reproducible sources |
| Evidence reference format inconsistent across check types | High | High | Define shared evidence reference validator callable used in both evaluator and test suite |
| `--strictness` alias removal causes breakage in agent callers | Low | Medium | Document alias deprecation in SKILL.md with specific removal date tied to full enforcement |

---

## M4: Runtime Controls, Override Governance, Override Test Suite, and Reliability Hardening

### Objective

Implement lease/heartbeat/retry runtime controls, the scope-limited override governance flow, and the `tui.py` release guard, then validate all three with the override test suite. Override governance failures must be tested as blocking conditions, not warnings. Additionally, prove that runtime controls withstand adversarial conditions through a dedicated fault-injection suite and formal deadlock-resistance argument.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Lease/heartbeat runtime implementation | `audit_*_running` uses lease with heartbeat; missing heartbeat past timeout → `audit_*_failed(timeout)`; retry re-enters `ready_for_audit_*`; budget exhausted → permanent `audit_*_failed`; all values from M1-D2 |
| D4.2 | `tui.py` release guard — hard stop | Completing/releasing from `audit_release_failed` blocked unconditionally; error includes gate_run_id and failure_class |
| D4.3 | `tui.py` task/milestone override path | Completion from audit_*_failed permitted only with valid OverrideRecord with all required fields; incomplete metadata causes blocking error listing missing fields |
| D4.4 | OverrideRecord validation | All 11 required fields enforced (record_id, scope, entity_id, actor, reason_code, reason_text, created_at, expires_at, linked_gate_run_id, approver, approval_state, review_due_at); expired override treated as absent |
| D4.5 | `test_audit_gate_overrides.py` — approved override allows task/milestone completion | Entity in audit_task_failed + valid OverrideRecord → completion allowed; same for milestone; both pass |
| D4.6 | `test_audit_gate_overrides.py` — incomplete override metadata blocks completion | One test per required OverrideRecord field: field absent → completion blocked → error names missing field; minimum 11 tests, all pass |
| D4.7 | `test_audit_gate_overrides.py` — release override unconditionally forbidden | Entity in audit_release_failed + fully valid OverrideRecord → blocked; test asserts allowed=False, reason contains "release override forbidden" |
| D4.8 | `test_audit_gate_overrides.py` — override scope isolation | task OverrideRecord does not authorize milestone-scope entity; milestone OverrideRecord does not authorize release-scope entity; both mismatch cases → blocking errors |
| D4.9 | `test_audit_gate_overrides.py` — expired override treated as absent | OverrideRecord with expires_at in past → completion blocked; same behavior as no record |
| D4.10 | `test_audit_gate_overrides.py` — timeout/retry exhaustion path | Parametrized across task and milestone: heartbeat timeout → failed(timeout); retry → ready_for_audit_*; budget → permanent failed |
| D4.11 | Correlation ID propagation | GateTransitionEvent and GateCheckEvent share correlation_id traceable through a full gate run |
| D4.12 | Fault-injection suite | Four scenarios: (1) heartbeat failure mid-run → failed(timeout); (2) lease expiry during evaluation → clean failure; (3) concurrent retry + heartbeat → no state oscillation; (4) system fault during state transition → atomic change or clean rollback; all pass before M6 can begin |
| D4.13 | Deadlock-resistance formal argument | Proof-by-construction: every running state has timeout exit; every failed state has bounded retry or terminal; retry budget monotonically decreasing; supported by property-based test (10K random sequences, all terminate) |

### Dependencies

- M1-D2 (retry/backoff/timeout values) — D4.1, D4.10, D4.12 cannot be written without concrete values
- M1-D5 (override approver model) — D4.3, D4.4, D4.6 depend on which fields are required
- M2-D2 (transition validator) — D4.2 and D4.3 call validator as enforcement mechanism
- M3-D3 (GateResult schema) — override block and gate_run_id fields feed D4.3 and D4.11

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Heartbeat implementation creates timing-dependent flaky tests | High | Medium | Mock clock; injectable time source in lease/heartbeat implementation |
| Override bypass via direct model mutation rather than API | Medium | Critical | Guard enforced at persistence layer; test that mutates state directly asserts guard catches it |
| Scope-mismatch override silently allowed | Medium | High | D4.8 is mandatory; scope check is first validation in OverrideRecord validation logic |
| Fault-injection tests produce non-deterministic results | Medium | Medium | Deterministic mock-based fault injection; injectable time source for all timeout paths |
| Deadlock-resistance proof incomplete for concurrent multi-entity scenarios | Low | High | Scope formal argument to single-entity paths; add operational runbook for concurrent scenarios |

---

## M5: Sprint CLI Regression Gate

### Objective

Confirm that all changes to `models.py` and `tui.py` introduced in M2 and M4 do not regress any existing sprint CLI behavior. These are shared infrastructure files used by the executor, monitor, and config modules.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | Baseline regression audit | Before M2 changes: run full `tests/sprint/` suite, record baseline pass count, document which tests exercise `models.py` and `tui.py` |
| D5.2 | PhaseStatus backward-compatibility assertions | All pre-existing PhaseStatus values (PENDING, RUNNING, PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, HALT, TIMEOUT, ERROR, SKIPPED) present; is_terminal, is_success, is_failure properties unchanged; SprintOutcome values (SUCCESS, HALTED, INTERRUPTED) unchanged |
| D5.3 | `test_regression_gaps.py` scenarios still pass | All existing scenarios pass after M2 and M4 changes: timeout path, PASS_NO_SIGNAL, PASS_NO_REPORT, CONTINUE+HALT priority, PARTIAL→HALT, double-stop idempotency, reset before start, shutdown_requested at phase top, ClaudeProcess.terminate, ClaudeProcess.wait timeout, build_command model flag behavior |
| D5.4 | tui.py guard does not fire on non-audit transitions | Existing sprint completion flow (no audit state) proceeds without triggering audit guard; guard active only when entity is in audit_* state |
| D5.5 | Zero new test failures in `tests/sprint/` | Post-M2 and post-M4 merge: failing test count = 0; any failure is a blocking regression requiring resolution before M6 |

### Dependencies

- M2-D1, M2-D6 (models.py changes and tui.py guard from M2)
- M4-D2, M4-D3 (tui.py release guard and override path from M4)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Audit state enums import into models.py breaks existing executor imports | Medium | High | Smoke test importing all sprint modules after every models.py change; add to pre-commit hook |
| tui.py guard silently skips on None entity state | Medium | High | Explicit test asserting guard behavior when entity_state is None (no-bypass default) |
| Regression tests not run against final merged state | Medium | High | CI runs `tests/sprint/` on integration branch after every merge from M2 and M4 |

---

## M6: Rollout Validation, Rollback Drill, and Phase Promotion Gate

### Objective

Execute and validate the shadow → soft → full rollout sequence per spec Section 7. Structured in two sub-phases with explicit ordering constraints.

**Sub-Phase A (Shadow + Shadow-to-Soft Gate)**: D6.1, D6.5, D6.6, D6.7, D6.9. D6.9 (Shadow-to-Soft sign-off) must be complete before any Sub-Phase B deliverable can begin.

**Sub-Phase B (Soft/Full Enforcement + Rollback Drill + Soft-to-Full Gate)**: D6.2, D6.3, D6.4, D6.8, D6.10. D6.8 (Rollback drill) must pass before D6.10 (Soft-to-Full sign-off).

### Deliverables

**Sub-Phase A: Shadow Deployment and Shadow-to-Soft Gate**

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | `test_audit_gate_rollout.py` — shadow mode | Gate decision recorded without blocking; GateResult artifact produced; transition events emitted with correlation_id; no business operation interrupted |
| D6.5 | `test_audit_gate_rollout.py` — `--strictness` alias deprecation | Shadow/soft: `--strictness` produces deprecation warning but succeeds; full mode: produces error, does not execute |
| D6.6 | Shadow window KPI report | Two consecutive shadow windows; report contains: gate execution count by scope, pass/fail ratio by profile, evidence completeness rate (target 100%), determinism rate (per M1-D1 floor), false-block rate; approved by policy owner and reliability owner |
| D6.7 | Threshold calibration | Provisional thresholds reviewed against shadow data; confirmed or revised with owner sign-off; revised thresholds reflected in profile test fixtures (M3-D4 re-run if values change) |
| D6.9 | Shadow-to-Soft promotion gate sign-off | Five promotion criteria from spec Section 7.2 confirmed; sign-off by policy owner and program manager; **GATE: Sub-Phase B cannot begin until M6-D9 is signed off** |

**Sub-Phase B: Soft/Full Enforcement, Rollback Drill, and Soft-to-Full Gate**

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.2 | `test_audit_gate_rollout.py` — soft mode | Strict-profile entities blocked by failed gates; standard-profile enforcement matches M1-D1 decision; switching modes does not corrupt persisted GateResult state |
| D6.3 | `test_audit_gate_rollout.py` — full mode | All scopes enforced; `--strictness` rejected; Tier-1 gate fires even for LIGHT/EXEMPT flows |
| D6.4 | `test_audit_gate_rollout.py` — rollback trigger tests | One test per normative trigger from spec Section 7.3 (5 triggers); all five pass |
| D6.8 | Rollback drill | Forced rollback soft→shadow: completes within defined window; shadow artifact production remains active; no GateResult data lost; drill documented with pass/fail verdict and drill log; **GATE: D6.10 cannot be signed off until D6.8 passes** |
| D6.10 | Soft-to-Full promotion gate sign-off | All milestones M1-M6 passing across two consecutive windows; rollback drill passed; sign-off by policy owner, reliability owner, and program manager; no outstanding NO-GO criteria from spec Section 12.2 |

### Dependencies

- M3 (evaluator and profile tests)
- M4 (runtime controls, override tests, reliability hardening, fault-injection suite)
- M5 (regression gate — zero regressions confirmed)
- M1-D3 (rollback trigger thresholds finalized)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shadow window data insufficient to calibrate thresholds | Medium | High | Define minimum gate-run count for valid window in M1-D3; extend window if threshold not met |
| Rollback drill fails due to GateResult persistence layer issue | Low | Critical | Run drill in staging first; artifact retention verified before drill |
| KPI determinism breach below threshold after soft enforcement | Medium | High | Monitoring alert fires within one gate cycle of a determinism breach |
| `--strictness` alias used by external callers not updated before full enforcement | Medium | Medium | Document deprecation in SKILL.md; provide one soft-enforcement window for migration |
| Rollback drill skipped under schedule pressure | Medium | Critical | D6.10 acceptance criterion is non-waivable; promotion gate cannot be signed off without drill log |
| Sub-Phase A delayed, compressing Sub-Phase B timeline | Medium | High | Shadow windows begin as early as possible; D6.9 can proceed in parallel with M5 if M3/M4 complete |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Profile threshold values changed after test suite written, requiring test rework | M3, M6 | High | High | Parameterize thresholds as fixtures; only fixture changes, not test logic | Policy owner (TBD per M1) |
| R-002 | Retry/backoff values unresolved, blocking M2 stuck-state and M4 timeout tests | M2, M4 | High (current blocker) | Critical | M1-D2 must close before M2/M4 retry test authoring begins | Reliability owner (TBD per M1) |
| R-003 | Release override path reachable through indirect state manipulation | M2, M4, M6 | Medium | Critical | Enforce at construction time (M2-D8), at validator (M2-D2), and at persistence layer; adversarial test (D4.7) | State-machine owner (TBD per M1) |
| R-004 | Non-determinism in evaluator (LLM/agent input leaks into pass/fail) | M3, M6 | Medium | Critical | Replay stability test (D3.4) required; evaluator uses only deterministic inputs | Policy owner |
| R-005 | models.py changes break existing sprint CLI executor or monitor | M5 | Medium | High | Baseline regression audit (D5.1) before any changes; smoke-import test in CI | State-machine owner |
| R-006 | Rollback drill never executed before Soft-to-Full promotion | M6 | Medium | Critical | D6.10 acceptance criterion is non-waivable; promotion checklist requires drill log attachment | Migration owner (TBD per M1) |
| R-007 | Shadow window sample size too small for meaningful KPI calibration | M6 | Medium | High | Define minimum gate-run threshold per window in M1-D3; extend window if threshold not met | Program manager |
| R-008 | Override scope-mismatch silently permitted | M4 | Medium | High | D4.8 scope isolation test mandatory; scope check is first validation | State-machine owner |
| R-009 | Heartbeat/lease tests become timing-dependent and flaky | M4 | High | Medium | Injectable clock in lease implementation; mock time in all timeout tests | Reliability owner |
| R-010 | Incomplete override metadata silently allows completion | M4 | Medium | Critical | D4.6 tests each field individually; validation is all-or-nothing | Policy owner |
| R-011 | Closed-world assumption creates friction when adding new states | M2 | Low | Medium | Document: any new state MUST have explicit transition declarations | State-machine owner |
| R-012 | Fault-injection tests produce non-deterministic results due to timing | M4 | Medium | Medium | Deterministic mock-based fault injection; injectable time source for all paths | Reliability owner |
| R-013 | Deadlock-resistance proof incomplete for concurrent multi-entity scenarios | M4 | Low | High | Scope formal argument to single-entity paths; add operational runbook | Reliability owner |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|-------------------------|-----------|
| Blocker resolution as standalone M1 | Standalone prerequisite milestone | Resolve inline with contracts (V1 M1); defer to M6 (V1 original) | Non-deterministic inputs produce non-deterministic tests; any test written before M1 closes is untrustworthy |
| Testing milestones interleaved with implementation | Interleaved per milestone | Single validation sprint at end; separate test-only milestones | Feature is a gating mechanism; deferring testing means gate is unvalidated during shadow mode |
| Profile test suite uses parameterized threshold fixtures | Parameterized fixtures | Hard-coded threshold assertions | Provisional thresholds (spec Section 8.1) expected to change; parameterization prevents test rewrites |
| Rollback drill as non-waivable gate for Soft-to-Full | Non-waivable | Optional/best-effort drill | Spec Section 7.2 explicitly requires rollback drill passage; waiver would violate rollout contract |
| Sprint CLI regression gate (M5) as standalone milestone | Standalone milestone | Folded into M2 or M4 (V1 approach); omitted (V3 approach) | `models.py` and `tui.py` are shared infrastructure; regression scope warrants dedicated tracking |
| Transition validator uses closed-world assumption | Closed-world (only listed transitions legal) | Open-world (only listed transitions illegal) | Closed-world eliminates bypass categories by default; any new state requires explicit transition declaration |
| Release override prohibition at construction time | Compile-time enforcement (OverrideRecord constructor) | Runtime check only at transition validator | Catches invalid overrides at creation, not transition time; defense in depth with two independent layers |
| Adversarial release override test with fully valid record | Adversarial test with valid OverrideRecord at forbidden scope | Test only with absent record | Dangerous failure mode is valid record incorrectly accepted at release scope; absent-record test insufficient |
| Rollout milestone structured with sub-phase ordering | M6 with Sub-Phase A (Shadow + gate) and Sub-Phase B (Soft/Full + drill + gate) | Three separate milestones (V3 approach); single flat milestone (V2 original) | Sub-phases provide V3's ordering guarantees without consuming extra milestones |
| Fault-injection suite as explicit M4 deliverable | Explicit deliverable within M4 | Implicit testing (V2 original); dedicated reliability milestone (V3 approach) | Explicit deliverable ensures reliability proven before rollout; within M4 avoids milestone proliferation |
| Primary Persona | architect | backend (0.378), security (0.193) | Multi-domain generalist (0.410 confidence) optimal for cross-domain system design |
| Template | inline | None available in Tiers 1-3 | No template scored ≥0.6; inline generation from extraction data |
| Milestone Count | 6 | 5-7 (MEDIUM range) | base=5 + floor(3/2)=1 = 6 milestones |
| Adversarial Mode | multi-roadmap | N/A | --multi-roadmap flag with 3 agents specified |
| Adversarial Base Variant | sonnet:qa (score 0.9488) | opus:architect (0.8825), haiku:analyzer (0.8425) | Highest combined score; strongest on completeness, correctness, clarity, risk coverage |

---

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|------------------------|------------|
| SC-001 | All four blockers closed with owner, UTC deadline, effective phase before M2/M3/M4 blocker-dependent test authoring | M1 | Decision registry contains zero [TBD] fields; four documents version-controlled |
| SC-002 | All 17 legal-transition tests pass for task, milestone, and release scopes | M2 | CI reports 17/17 |
| SC-003 | All 6 illegal-transition classes covered with passing tests; validate_transition returns allowed=False with non-empty reason | M2 | CI reports 6/6 |
| SC-004 | Closed-world enforcement: synthetic state not in transition table returns allowed=False | M2 | One explicit test asserting unknown state pair is rejected |
| SC-005 | OverrideRecord with scope='release' rejected at construction time | M2 | Explicit test in D2.8 |
| SC-006 | Stuck-state recovery: retry budget exhaustion → permanent failed; retry from failed → ready_for_audit_* | M2 | Test assertions on transition validator return values |
| SC-007 | Profile determinism: identical inputs → identical GateResult across 3 replays for each of 3 profiles | M3 | 9 determinism assertions in CI, all pass |
| SC-008 | Evidence completeness: every failed check contains file path or file:line; missing evidence → non-completable | M3 | Zero failed checks with empty evidence_refs in test outputs |
| SC-009 | Release override unconditionally blocked even with fully valid OverrideRecord | M4 | Test asserts allowed=False; reason contains "release override forbidden" |
| SC-010 | Incomplete override metadata (any single field absent) blocks completion with error naming missing field | M4 | 11+ individual field-absence tests all pass |
| SC-011 | Fault-injection suite passes: heartbeat failure, lease expiry, concurrent retry, system fault → clean state transitions | M4 | 4 fault-injection test scenarios pass |
| SC-012 | Deadlock-resistance: 10K random state sequences all terminate within bounded steps | M4 | Property-based test with termination assertion |
| SC-013 | Zero regressions in `tests/sprint/` after M2 and M4 changes on integration branch | M5 | CI failing test count = 0 |
| SC-014 | All pre-existing PhaseStatus and SprintOutcome values retain identical is_terminal, is_success, is_failure semantics | M5 | Explicit backward-compatibility assertions pass |
| SC-015 | Two consecutive shadow windows complete with evidence completeness = 100% and determinism rate ≥ M1-D1 floor | M6 | KPI report filed and approved by policy owner |
| SC-016 | Rollback drill executed and documented with pass verdict before Soft-to-Full promotion sign-off | M6 | Drill log attached to D6.10 sign-off document |
| SC-017 | All five rollback trigger tests pass in `test_audit_gate_rollout.py` | M6 | 5 trigger tests in CI, all pass |
| SC-018 | `--strictness` alias rejected in full enforcement; accepted with deprecation warning in shadow/soft | M3, M6 | Two explicit tests, both pass |
| SC-019 | Soft-to-Full promotion sign-off includes policy owner, reliability owner, program manager; no outstanding NO-GO criteria | M6 | Sign-off document has three named approvers; checklist Section 10 status is PASS |
| SC-020 | Sub-Phase A (Shadow-to-Soft) signed off before any Sub-Phase B deliverable begins | M6 | D6.9 sign-off timestamp precedes D6.2/D3/D4/D8 start timestamps |
