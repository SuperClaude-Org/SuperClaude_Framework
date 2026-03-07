# Roadmap: Unified Audit Gating System v1.2.1 [QA Variant]

Document date: 2026-03-03
Persona: QA specialist — validation and acceptance rigor
Source specification: `docs/generated/unified-audit-gating-v1.2.1-release-spec.md`

---

## Overview

This roadmap drives delivery of the Unified Audit Gating System v1.2.1 from a QA-first perspective. The central premise is that **testing milestones cannot be deferred to the end of a release cycle** when the feature under test is itself a gating mechanism. A state machine that controls task, milestone, and release completions will be exercised under adversarial conditions from the moment the first prototype exists. Any gap in test coverage of illegal transitions, override governance failures, or rollback triggers becomes a production escape path. For that reason, testing activities are interleaved with every implementation phase rather than consolidated in a separate validation sprint.

The four current blockers — unfinalized profile thresholds, unresolved retry/backoff/timeout values, undefined rollback triggers, and unassigned decision owners — are not merely documentation gaps. Each one makes a corresponding test suite non-deterministic or untestable. No milestone that depends on these inputs can reach a passing acceptance gate until the blockers are closed. The roadmap therefore opens with a dedicated milestone that treats blocker resolution as a testable deliverable with explicit closure criteria and an assigned owner verification step.

The rollout validation sequence (shadow → soft → full) is treated as a first-class milestone with its own acceptance gate table and mandatory rollback drill. KPI promotion criteria drawn directly from Section 7 of the specification are embedded as measurable pass/fail conditions, not aspirational guidance. Regression coverage for the sprint CLI changes in `models.py` and `tui.py` is an explicit deliverable, not an implicit assumption, because those files sit at the enforcement boundary where illegal transitions would escape if guards regress.

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Blocker Resolution and Decision Lock | Prerequisites / Governance | Critical | Medium | None | Signed decisions for all 4 blockers; owners + UTC deadlines assigned | High — no downstream testing is meaningful without this |
| M2 | State Machine Implementation and Illegal-Transition Test Suite | Implementation + Testing | Critical | High | M1 | `models.py` audit states; transition validator; `test_audit_gate_state_machine.py` passing | High — bypass paths are a direct security/integrity risk |
| M3 | Deterministic Gate Evaluator and Profile Test Suite | Implementation + Testing | Critical | High | M1 (thresholds), M2 (state enum baseline) | `sc-audit-gate-protocol/SKILL.md`; `test_audit_gate_profiles.py` passing | High — non-determinism invalidates shadow metrics |
| M4 | Runtime Controls, Override Governance, and Override Test Suite | Implementation + Testing | High | High | M1 (retry values, override model), M2, M3 | Lease/heartbeat/retry logic; `tui.py` guards; `test_audit_gate_overrides.py` passing | High — incomplete override metadata is a blocking escape path |
| M5 | Sprint CLI Regression Gate | Testing / Regression | High | Medium | M2, M4 | Regression suite covering all modified `models.py` and `tui.py` behaviors; zero regression baseline confirmed | Medium — existing sprint CLI behavior must not regress |
| M6 | Rollout Validation, Rollback Drill, and Phase Promotion Gate | Rollout + Testing | Critical | High | M3, M4, M5; rollback triggers finalized in M1 | Shadow window metrics; rollback drill pass; KPI promotion report; `test_audit_gate_rollout.py` passing | High — premature promotion to full enforcement is irreversible in the short term |

---

## Dependency Graph

```
M1 (Blocker Resolution)
  --> M2 (State Machine + Illegal-Transition Tests)
  --> M3 (Evaluator + Profile Tests)  [also depends on M2 for state enum baseline]
  --> M4 (Runtime Controls + Override Tests)  [also depends on M2, M3]

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
| M1-D1 | Profile thresholds and major-severity behavior decision document | Document exists with: numeric threshold values per profile (strict, standard, legacy_migration); explicit pass/fail behavior for major-severity findings at task tier under standard profile; owner name and UTC sign-off date recorded; no [TBD] fields remaining |
| M1-D2 | Retry/backoff/timeout policy decision document | Document states: maximum retry attempt budget per scope (task, milestone, release); backoff strategy (constant, linear, or exponential with base values); absolute timeout values in seconds per scope; heartbeat interval and missed-heartbeat threshold; owner name and UTC sign-off date; no [TBD] fields remaining |
| M1-D3 | Rollback and safe-disable trigger contract | Document enumerates the five normative triggers from spec Section 7.3 with concrete threshold values for each (e.g., M4 determinism breach: what percentage below what floor triggers rollback); emergency safe-disable procedure documented; owner name and UTC sign-off date; no [TBD] fields remaining |
| M1-D4 | Open decision registry with owners and UTC deadlines | All five decisions from spec Section 12.4 appear in a tracked registry with owner, UTC deadline, and effective rollout phase; checklist section 10 moves from NO-GO to PASS |
| M1-D5 | Override approver model decision | Single-approver vs. dual-approver resolved; review cadence (review_due_at window) specified numerically; owner and UTC deadline recorded |

### Dependencies

None. This milestone is the root of the dependency graph and must not be blocked by implementation work.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Decision owners unavailable or unresponsive | Medium | Critical — entire downstream is blocked | Escalate to program manager within 48 hours of missed response; spec Section 9.2 assigns a program manager role explicitly for this purpose |
| Thresholds set without empirical basis, requiring revision after shadow data | High | High — changes to thresholds after M3 is built force re-testing of profile suite | Mark thresholds as provisional in shadow mode per spec Section 8.1; build profile test suite to accept threshold as an injected parameter so re-baselining does not require test rewrites |
| Decision registry not maintained after initial population | Medium | Medium — reopened decisions cause milestone regression | Registry must be version-controlled and diff-auditable; changes require owner acknowledgment |
| Rollback trigger thresholds set too conservatively, causing false rollbacks in shadow | Low | Medium — wastes calibration windows | Allow one revision cycle before normative lock, but require owner sign-off for each revision |

---

## M2: State Machine Implementation and Illegal-Transition Test Suite

### Objective

Implement the normative audit states and transition validator in `models.py`, and build an exhaustive test suite covering every legal and illegal transition defined in spec Sections 4.1 and 4.2. The test suite must be the authoritative enforcement reference — not the prose specification — by the time this milestone closes.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M2-D1 | `models.py` audit state enums | Six new audit states exist per scope (ready_for_audit_*, audit_*_running, audit_*_passed, audit_*_failed) for task, milestone, and release; each state has an `is_terminal` property; PhaseStatus enum does not regress (all existing values present and behavior-equivalent) |
| M2-D2 | Transition validator function | A callable `validate_transition(scope, from_state, to_state, override_record=None)` exists; returns (allowed: bool, reason: str); raises no exceptions for any combination of valid enum values |
| M2-D3 | `test_audit_gate_state_machine.py` — legal transitions | One test per legal transition for each scope (task: 6 transitions, milestone: 6 transitions, release: 5 transitions); each test asserts `validate_transition` returns allowed=True; all 17 legal-transition tests pass |
| M2-D4 | `test_audit_gate_state_machine.py` — illegal transitions | One test per illegal transition from spec Section 4.2 items 1-6; each test asserts allowed=False with a non-empty reason string; the six mandatory illegal classes all covered: bypass from in_progress, bypass from ready_for_audit_*, bypass from audit_*_running, failed-to-completed without override (task/milestone), audit_release_failed-to-released, transition from terminal state without reopen |
| M2-D5 | `test_audit_gate_state_machine.py` — stuck-state recovery | Tests for: heartbeat timeout triggers audit_*_failed(timeout); retry from audit_*_failed re-enters ready_for_audit_* when budget remains; retry budget exhaustion leaves entity in audit_*_failed and blocks completion; reopen from terminal state succeeds only via explicit reopen operation |
| M2-D6 | Validator enforced in `tui.py` completion guard | `tui.py` calls the transition validator before every completion or release action; if validator returns allowed=False, the guard raises a blocking error with the reason string included in the user-facing message |
| M2-D7 | No regression in existing sprint CLI tests | All tests in `tests/sprint/` that were passing before this milestone continue to pass; `test_regression_gaps.py` scenarios unaffected |

### Dependencies

- M1-D1 (profile threshold document) — needed to know which failure classes map to which profiles for state-machine-adjacent checks
- M1-D3 (retry budget values) — needed for stuck-state recovery test parameterization

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| New audit states conflict with existing PhaseStatus usage in tui.py or executor | Medium | High — runtime errors in existing sprint flows | Add a backward-compatibility test asserting all pre-existing PhaseStatus values remain present and their is_terminal/is_success/is_failure properties are unchanged |
| Illegal-transition validator is bypassed by direct state assignment in models | Medium | Critical — the feature's core invariant is void | Validate via property setter or __setattr__ hook in the state dataclass; add a test that sets state directly and asserts the validator fires |
| Transition validator test coverage is incomplete for multi-scope interactions | Low | Medium | Parametrize test suite across all three scopes (task, milestone, release) for every transition type to prevent scope-specific gaps |
| Retry budget semantics ambiguous (per-run vs. per-entity lifetime) | High — M1-D2 must resolve this | High — tests will be wrong if budget semantics are misunderstood | Block M2 test authoring for retry scenarios until M1-D2 is signed off |

---

## M3: Deterministic Gate Evaluator and Profile Test Suite

### Objective

Implement the deterministic gate evaluator in `sc-audit-gate-protocol/SKILL.md` that produces a fully specified `GateResult` for every input, and build a profile test suite demonstrating replay stability, failure-class correctness, and evidence completeness. Non-determinism in the evaluator invalidates shadow metrics and makes KPI calibration impossible.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M3-D1 | `sc-audit-gate-protocol/SKILL.md` evaluator behavior contract | Evaluator section specifies: input contract (scope, entity_id, profile); output contract (GateResult with all fields from spec Section 6.1); failure-class taxonomy (policy, transient, system, timeout, unknown); unknown/missing inputs map to failed(unknown) |
| M3-D2 | `sc-audit-gate/SKILL.md` command behavior | `/sc:audit-gate` command section specifies: `--profile strict|standard|legacy_migration` as canonical flag; `--strictness` retained as alias only in shadow/soft modes; output includes gate_run_id, scope, status, score, threshold, failure_class, evidence_refs |
| M3-D3 | GateResult schema conformance | All GateResult outputs include every required field from spec Section 6.1: version, gate_run_id, scope, entity_id, profile, status, score, threshold, checks[], drift_summary (edited + non_edited), override block, timing block, artifacts block, failure_class |
| M3-D4 | `test_audit_gate_profiles.py` — profile determinism | For each profile (strict, standard, legacy_migration): same input replayed 3 times produces identical GateResult (status, score, failure_class, check outcomes); test parameterized across profiles; 9 determinism assertions total, all pass |
| M3-D5 | `test_audit_gate_profiles.py` — major-severity behavior | Under `standard` profile at task tier: one test where major-severity finding is present asserts the expected outcome per M1-D1 decision; one test where no major-severity finding exists confirms no false positive; behavior matches M1-D1 signed decision exactly |
| M3-D6 | `test_audit_gate_profiles.py` — unknown/missing input handling | Test with missing entity_id produces failed(unknown); test with unsupported schema version produces failed(unknown); test with all required inputs present but one check returning null evidence produces failed (non-completable); all three tests pass |
| M3-D7 | `test_audit_gate_profiles.py` — evidence completeness | Every failed check in test output contains at least one evidence reference that is either a file path or file:line format; drift_summary contains separate edited and non_edited fields; one test specifically verifies a failed check with no evidence reference is itself treated as failed and non-completable |
| M3-D8 | `--strictness` alias behavior test | Test in shadow/soft mode: `--strictness strict` produces same GateResult as `--profile strict`; `--strictness standard` produces same GateResult as `--profile standard`; `--strictness` does not express `legacy_migration` (error or rejection); at full enforcement simulation, `--strictness` flag is rejected with a clear deprecation message |

### Dependencies

- M1-D1 (profile thresholds and major-severity behavior) — tests cannot assert correct threshold pass/fail without finalized numeric values
- M2-D1 (audit state enums) — evaluator output feeds state transitions; schema must be consistent
- M1-D5 (override approver model) — override block in GateResult must reflect correct approver fields

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Profile threshold values change post-M3 test authoring | Medium — thresholds are provisional in shadow | High — profile test assertions become incorrect | Parameterize threshold values as fixtures derived from M1-D1 document; when thresholds change, only the fixture changes, not test logic |
| Evaluator uses LLM/agent judgment for pass/fail (non-goal per spec) | Medium | Critical — violates locked decision 2.2 | Add a test that runs the evaluator twice with identical deterministic inputs and asserts outputs are byte-for-byte identical across fields that are not timestamps or run IDs |
| Evidence reference format inconsistent across check types | High | High — M5 evidence completeness is a hard gate with no warning band | Define a shared evidence reference validator callable used in both the evaluator and the test suite |
| `--strictness` alias removal causes breakage in agent callers during shadow | Low | Medium | Document alias deprecation in SKILL.md with a specific removal date tied to full enforcement phase |

---

## M4: Runtime Controls, Override Governance, and Override Test Suite

### Objective

Implement lease/heartbeat/retry runtime controls, the scope-limited override governance flow, and the `tui.py` release guard, then validate all three with the override test suite. Override governance failures — missing approver identity, absent approval state, expired or missing review_due_at — must be tested as blocking conditions, not as warnings.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M4-D1 | Lease/heartbeat runtime implementation | `audit_*_running` states use a lease with heartbeat; missing heartbeat past configured timeout causes `audit_*_failed(timeout)`; retry re-enters `ready_for_audit_*`; retry budget exhausted leaves entity in `audit_*_failed`; all values sourced from M1-D2 signed decision |
| M4-D2 | `tui.py` release guard — audit_release_failed is a hard stop | Completing or releasing from `audit_release_failed` is blocked unconditionally; no override path exists; error message includes the gate_run_id and failure_class of the blocking gate result |
| M4-D3 | `tui.py` task/milestone override path | Completion from `audit_task_failed` or `audit_milestone_failed` permitted only when a valid `OverrideRecord` is present with all required fields from spec Section 6.2; incomplete override metadata causes a blocking error listing missing fields |
| M4-D4 | OverrideRecord validation | OverrideRecord validation enforces all required fields: record_id, scope, entity_id, actor, reason_code, reason_text, created_at, expires_at, linked_gate_run_id, approver, approval_state, review_due_at; any missing field produces a blocking error; expired override (expires_at < now) is treated as absent |
| M4-D5 | `test_audit_gate_overrides.py` — approved override allows task/milestone completion | Test: entity in audit_task_failed + valid OverrideRecord → completion allowed; same for milestone scope; both pass |
| M4-D6 | `test_audit_gate_overrides.py` — incomplete override metadata blocks completion | Test for each required OverrideRecord field: one field absent → completion blocked → error message names the missing field; minimum 11 tests (one per required field); all pass |
| M4-D7 | `test_audit_gate_overrides.py` — release override is unconditionally forbidden | Test: entity in audit_release_failed + any OverrideRecord (including a fully valid one) → completion/release blocked; override record presence makes no difference; test explicitly asserts allowed=False with reason containing "release override forbidden" |
| M4-D8 | `test_audit_gate_overrides.py` — override scope isolation | Test: OverrideRecord with scope=task does not authorize completion of a milestone-scope entity; OverrideRecord with scope=milestone does not authorize completion of a release-scope entity; both mismatch cases produce blocking errors |
| M4-D9 | `test_audit_gate_overrides.py` — expired override treated as absent | Test: OverrideRecord with expires_at in the past → completion blocked; same behavior as no override record present |
| M4-D10 | `test_audit_gate_overrides.py` — timeout/retry exhaustion path | Test: audit_*_running heartbeat timeout → audit_*_failed(timeout); retry from failed → ready_for_audit_*; retry count at budget → completion remains blocked; all three assertions in one parametrized test across task and milestone scopes |
| M4-D11 | Correlation ID propagation | GateTransitionEvent and GateCheckEvent share correlation_id traceable through a full gate run; test asserts correlation_id is non-null and consistent across all events for a single gate run |

### Dependencies

- M1-D2 (retry/backoff/timeout values) — M4-D1 and M4-D10 cannot be written without concrete values
- M1-D5 (override approver model) — M4-D3, M4-D4, M4-D6 depend on which approver fields are required
- M2-D2 (transition validator) — M4-D2 and M4-D3 call the validator as their enforcement mechanism
- M3-D3 (GateResult schema) — override block and gate_run_id fields in GateResult feed M4-D3 and M4-D11

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Heartbeat implementation creates a timing-dependent test (flaky) | High | Medium — flaky tests erode confidence in the suite | Mock clock in tests; use injectable time source in the lease/heartbeat implementation so tests control elapsed time deterministically |
| Override bypass discovered via direct model mutation rather than API | Medium | Critical — the invariant fails silently | Add a test that mutates entity state directly to `completed` while in `audit_release_failed` and asserts the guard catches this; guard must be enforced at persistence layer, not only at UI layer |
| Scope-mismatch override silently allowed due to missing scope check | Medium | High | M4-D8 is explicitly required; add scope field to override validation before any other field check |
| Dual-approver model (if chosen in M1-D5) doubles the required-field tests | Low | Medium | M4-D6 test count is parameterized; M1-D5 resolution updates the fixture, not the test structure |

---

## M5: Sprint CLI Regression Gate

### Objective

Confirm that all changes to `models.py` and `tui.py` introduced in M2 and M4 do not regress any existing sprint CLI behavior. The modified files are shared infrastructure: `models.py` defines PhaseStatus and SprintOutcome used by the executor, monitor, and config modules; `tui.py` controls user-facing completion flows. Any regression in these components silently breaks sprint execution in ways unrelated to audit gating.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M5-D1 | Baseline regression audit | Before M2 changes land: run full `tests/sprint/` suite and record baseline pass count; document which tests exercise `models.py` and `tui.py` directly; record as the regression baseline |
| M5-D2 | PhaseStatus backward-compatibility assertions | Explicit tests asserting: all pre-existing PhaseStatus values (PENDING, RUNNING, PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, HALT, TIMEOUT, ERROR, SKIPPED) remain present; their is_terminal, is_success, is_failure properties return the same values as baseline; SprintOutcome values (SUCCESS, HALTED, INTERRUPTED) unchanged |
| M5-D3 | `test_regression_gaps.py` scenarios still pass | All scenarios from the existing regression gap file pass after M2 and M4 changes: timeout (exit 124) path, PASS_NO_SIGNAL, PASS_NO_REPORT, CONTINUE+HALT priority, PARTIAL→HALT, double-stop idempotency, reset before start, shutdown_requested at phase top, ClaudeProcess.terminate on dead process, ClaudeProcess.wait timeout, build_command model flag behavior |
| M5-D4 | tui.py guard does not fire on non-audit transitions | Test: existing sprint completion flow (where no audit state is involved) proceeds without triggering the new audit guard; guard is only active when entity is in an audit_* state |
| M5-D5 | Zero new test failures in `tests/sprint/` | Post-M2 and post-M4 merge: total failing test count in `tests/sprint/` is 0; any failure is a blocking regression that must be resolved before M6 can begin |

### Dependencies

- M2-D1, M2-D6 (models.py changes and tui.py guard from M2)
- M4-D2, M4-D3 (tui.py release guard and override path from M4)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Audit state enums import into models.py breaks existing executor imports | Medium | High — executor crashes at runtime | Run a smoke test importing all sprint modules after every change to models.py; add to pre-commit hook |
| tui.py guard introduces a conditional that silently skips on None entity state | Medium | High — guard has no effect when entity_state is None | Add an explicit test asserting guard behavior when entity_state is None (should default to no-bypass, i.e., treat as not in audit state) |
| Regression tests not run against the final merged state (only against feature branch) | Medium | High — merge conflicts can reintroduce regressions | CI must run `tests/sprint/` on the integration branch after every merge from M2 and M4 |

---

## M6: Rollout Validation, Rollback Drill, and Phase Promotion Gate

### Objective

Execute and validate the shadow → soft → full rollout sequence per spec Section 7, collect KPI data across at least two shadow windows, pass the rollback drill, and formally gate promotion to each phase. This milestone is the release gate for v1.2.1: no production enforcement begins until M6 acceptance criteria are met.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M6-D1 | `test_audit_gate_rollout.py` — shadow mode produces metrics without blocking | Tests assert: in shadow mode, gate decision is recorded but does not block completion/release; GateResult artifact is produced with all required fields; transition events are emitted with correlation_id; no business operation is interrupted |
| M6-D2 | `test_audit_gate_rollout.py` — soft mode enforces selective profiles | Tests assert: under soft enforcement, strict-profile entities are blocked by failed gates; standard-profile entities enforcement matches M1-D1 decision; legacy_migration profile behaves per its defined policy; switching between modes does not corrupt persisted GateResult state |
| M6-D3 | `test_audit_gate_rollout.py` — full mode enforces globally | Tests assert: all scopes enforced; `--strictness` alias rejected with a clear error message; override governance applies per M4-D3 and M4-D7 rules in full mode; Tier-1 gate fires even for LIGHT/EXEMPT flows per locked decision |
| M6-D4 | `test_audit_gate_rollout.py` — rollback trigger tests | One test per normative rollback trigger from spec Section 7.3: (1) M4 determinism breach below threshold → rollback to prior phase; (2) M5 evidence completeness failure → rollback; (3) stale-running incident unresolved → rollback; (4) rollback drill failure → rollback; (5) validator bypass discovered → rollback; all five trigger tests pass |
| M6-D5 | `test_audit_gate_rollout.py` — `--strictness` alias deprecation path | Test: in shadow/soft mode, `--strictness` flag produces a deprecation warning but succeeds; in full mode, `--strictness` flag produces an error and does not execute |
| M6-D6 | Shadow window KPI report | Two consecutive shadow windows completed; report contains: gate execution count by scope, pass/fail ratio by profile, evidence completeness rate (target: 100%), determinism rate (target: per M1-D1 floor), false-block rate; report reviewed and approved by policy owner and reliability owner |
| M6-D7 | Threshold calibration and normative promotion | Provisional thresholds from M1-D1 reviewed against shadow window data; thresholds either confirmed or revised with owner sign-off; revised thresholds reflected in profile test fixture (M3-D4 re-run if values change) |
| M6-D8 | Rollback drill | Forced rollback from soft to shadow executed; drill validates: rollback completes within defined window; shadow artifact production remains active; no GateResult data lost; completion/release blocking is disabled in the rolled-back phase; drill result documented with pass/fail verdict and drill log |
| M6-D9 | Shadow-to-Soft promotion gate sign-off | All five promotion criteria from spec Section 7.2 confirmed: M1 (decisions closed), M4 (determinism gate), M5 (evidence gate, per the spec's M5 metric label), M7 (stale-running gate, per spec), M9 (override governance gate, per spec); sign-off by policy owner and program manager |
| M6-D10 | Soft-to-Full promotion gate sign-off | All milestones M1-M6 passing across two consecutive windows; rollback drill (M6-D8) passed; sign-off by policy owner, reliability owner, and program manager; no outstanding NO-GO criteria from spec Section 12.2 |

### Dependencies

- M3 (evaluator and profile tests)
- M4 (runtime controls and override tests)
- M5 (regression gate — zero regressions confirmed)
- M1-D3 (rollback trigger thresholds must be finalized)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shadow window data insufficient to calibrate thresholds (low traffic) | Medium | High — normative threshold lock cannot proceed | Define minimum gate-run count for a valid shadow window in M1-D3; if count not reached, extend window rather than promoting on sparse data |
| Rollback drill fails due to data loss in GateResult persistence layer | Low | Critical — M6-D10 blocked; production rollout cannot proceed | Rollback drill must be run in staging environment first; artifact retention must be verified before drill |
| KPI metrics show determinism breach below threshold after soft enforcement starts | Medium | High — immediate rollback to shadow required per spec 7.3 trigger 1 | Define monitoring alert that fires within one gate cycle of a determinism breach; do not rely on manual review |
| `--strictness` alias used by external agent callers that are not updated before full enforcement | Medium | Medium — callers fail at full enforcement | Document alias deprecation in SKILL.md and send advance notice; provide one soft-enforcement window for callers to migrate |
| Rollback drill not included in the promotion checklist, skipped under schedule pressure | Medium | Critical — violates spec Section 7.2 Soft-to-Full criteria | M6-D10 acceptance criterion explicitly lists rollback drill as a non-waivable prerequisite; promotion gate cannot be signed off without the drill log |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R1 | Profile threshold values changed after test suite written, requiring test rework | M3, M6 | High | High | Parameterize thresholds as fixtures; only fixture changes, not test logic | Policy owner (TBD per M1) |
| R2 | Retry/backoff values unresolved, blocking M2 stuck-state and M4 timeout tests | M2, M4 | High (currently a blocker) | Critical | M1-D2 must close before M2/M4 test authoring begins for retry-dependent scenarios | Reliability owner (TBD per M1) |
| R3 | Release override path discovered or reachable through indirect state manipulation | M2, M4, M6 | Medium | Critical | Enforce prohibition at persistence layer and at validator; add adversarial test that attempts every known bypass pattern | State-machine owner (TBD per M1) |
| R4 | Non-determinism in evaluator (LLM/agent input leaks into pass/fail) | M3, M6 | Medium | Critical | Replay stability test (M3-D4) required; evaluator must use only deterministic inputs; flag any conditional logic that reads from non-reproducible sources | Policy owner |
| R5 | models.py changes break existing sprint CLI executor or monitor | M5 | Medium | High | Baseline regression audit (M5-D1) before any changes; smoke-import test in CI | State-machine owner |
| R6 | Rollback drill never executed before Soft-to-Full promotion | M6 | Medium | Critical | M6-D10 acceptance criterion is non-waivable; promotion checklist requires drill log attachment | Migration owner (TBD per M1) |
| R7 | Shadow window sample size too small for meaningful KPI calibration | M6 | Medium | High | Define minimum gate-run threshold per window in M1-D3; extend window if threshold not met | Program manager |
| R8 | Override scope-mismatch silently permitted (task override used for milestone entity) | M4 | Medium | High | M4-D8 scope isolation test is mandatory; scope check is the first validation in OverrideRecord validation logic | State-machine owner |
| R9 | Heartbeat/lease tests become timing-dependent and flaky | M4 | High | Medium | Injectable clock in lease implementation; mock time in all timeout tests | Reliability owner |
| R10 | Incomplete override metadata (missing approver/approval_state/review_due_at) silently allows completion | M4 | Medium | Critical | M4-D6 tests each field individually; OverrideRecord validation is all-or-nothing (no partial approval) | Policy owner |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|-------------------------|-----------|
| Blocker resolution as a standalone milestone (M1) rather than inline with implementation | Standalone prerequisite milestone | Resolve blockers in parallel with early implementation work | Non-deterministic inputs produce non-deterministic tests; any test written before M1 closes is untrustworthy and likely requires rewrite |
| Testing milestones interleaved with implementation (not a trailing validation phase) | Interleaved per milestone | Single validation sprint at the end | The feature is a gating mechanism; deferring testing means the gate is unvalidated while it is being relied upon in shadow mode |
| Profile test suite uses parameterized threshold fixtures | Parameterized fixtures | Hard-coded threshold assertions | Provisional thresholds (spec Section 8.1) are expected to change after shadow calibration; parameterization prevents test rewrites |
| Rollback drill as a non-waivable gate for Soft-to-Full promotion | Non-waivable | Optional/best-effort drill | Spec Section 7.2 explicitly requires rollback drill passage; any waiver would violate the rollout contract |
| Sprint CLI regression gate (M5) as a standalone milestone | Standalone milestone | Folded into M2 or M4 | `models.py` and `tui.py` are shared infrastructure; regression scope is broad enough to warrant dedicated tracking and a zero-failure acceptance criterion |
| Illegal-transition tests as an exhaustive enumeration (one test per transition) | One test per transition | Combinatorial or property-based only | Spec Section 4.2 enumerates exactly six illegal transition classes; exhaustive enumeration is the most auditable form and maps directly to spec acceptance criteria |
| Release override prohibition tested adversarially (with a fully valid OverrideRecord) | Adversarial test with valid record | Test only with absent record | The dangerous failure mode is a valid record being incorrectly accepted at release scope; testing only absent records does not validate the prohibition |

---

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|------------------------|------------|
| SC-1 | All four blockers closed with owner, UTC deadline, and effective phase before any M2/M3/M4 test authoring begins for blocker-dependent scenarios | M1 | Yes — decision registry contains zero [TBD] fields; four documents exist and are version-controlled |
| SC-2 | All 17 legal-transition tests pass for task, milestone, and release scopes | M2 | Yes — test count is fixed by the spec; CI reports 17/17 |
| SC-3 | All 6 illegal-transition classes are covered with passing tests; `validate_transition` returns allowed=False with non-empty reason for every illegal combination | M2 | Yes — 6 test classes enumerated; CI reports 6/6 |
| SC-4 | Stuck-state recovery: retry budget exhaustion produces audit_*_failed with no completion path; rollback path from audit_*_failed re-enters ready_for_audit_* correctly | M2 | Yes — test assertions on return values of transition validator after retry budget exceeded |
| SC-5 | Profile determinism: identical inputs produce identical GateResult (status, score, failure_class, check outcomes) across 3 replays for each of 3 profiles | M3 | Yes — 9 determinism assertions in CI; all pass |
| SC-6 | Evidence completeness: every failed check contains a file path or file:line reference; missing evidence makes the check non-completable | M3 | Yes — test assertions on checks[] in GateResult; zero failed checks with empty evidence_refs |
| SC-7 | Release override is unconditionally blocked even when a fully valid OverrideRecord is supplied | M4 | Yes — test asserts allowed=False; reason string contains "release override forbidden" |
| SC-8 | Incomplete override metadata (any single required field absent) blocks completion with an error naming the missing field | M4 | Yes — 11+ individual field-absence tests all pass |
| SC-9 | Zero regressions in `tests/sprint/` after M2 and M4 changes land on the integration branch | M5 | Yes — CI failing test count is 0 |
| SC-10 | All pre-existing PhaseStatus and SprintOutcome enum values retain identical is_terminal, is_success, is_failure semantics | M5 | Yes — explicit backward-compatibility assertions pass |
| SC-11 | Two consecutive shadow windows complete with evidence completeness rate = 100% and determinism rate at or above M1-D1 floor | M6 | Yes — KPI report filed and approved by policy owner |
| SC-12 | Rollback drill executed and documented with pass verdict before Soft-to-Full promotion sign-off | M6 | Yes — drill log attached to M6-D10 sign-off document |
| SC-13 | All five rollback trigger tests pass in `test_audit_gate_rollout.py` | M6 | Yes — 5 trigger tests in CI; all pass |
| SC-14 | `--strictness` alias rejected with clear error in full enforcement mode; accepted with deprecation warning in shadow/soft | M3, M6 | Yes — two explicit tests, both pass |
| SC-15 | Soft-to-Full promotion sign-off includes: policy owner, reliability owner, program manager signatures; no outstanding NO-GO criteria from spec Section 12.2 | M6 | Yes — sign-off document contains three named approvers; checklist Section 10 status is PASS |
