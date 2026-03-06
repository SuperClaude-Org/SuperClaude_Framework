# Roadmap: Unified Audit Gating System v1.2.1 [Architect Variant]

Document status: **Generated from release spec v1.2.1**
Generation date: **2026-03-03**
Persona: **architect** -- deterministic contracts first
Source specification: `docs/generated/unified-audit-gating-v1.2.1-release-spec.md`

---

## Overview

This roadmap enforces a contracts-first ordering for the Unified Audit Gating System. The central architectural decision is that **no runtime behavior, CLI integration, or rollout activity may begin until the data contracts (GateResult, OverrideRecord, GateTransitionEvent, GateCheckEvent) and the state machine transition table are normatively locked, versioned, and covered by deterministic tests**. This is not a stylistic preference; it is a prerequisite chain. Every downstream component -- the evaluator, the CLI guards, the override governance flow, the rollout phases -- depends on the shape and invariants of these contracts. Changing them after implementation begins creates cascading rework that compounds with each dependent module.

The existing codebase (`src/superclaude/cli/sprint/models.py`) defines `PhaseStatus`, `SprintOutcome`, and related dataclasses for sprint execution. The audit-gating system introduces a parallel but distinct state machine operating at three scopes (task, milestone, release) with explicit `audit_*` states, failure classes, and override governance. These new types must coexist with the existing sprint models without collision. The `tui.py` module will eventually consume gate status for display, but that integration is deferred until contracts are stable and the transition validator is proven correct.

The six milestones below are ordered by strict technical prerequisite. M1 locks schemas and the state machine. M2 builds the deterministic evaluator and transition validator on top of those locked contracts. M3 adds runtime controls (lease, heartbeat, retry, timeout) that require the failure classes from M1 and the evaluator from M2. M4 integrates the CLI, override governance, and report persistence -- all of which consume the evaluator and runtime semantics. M5 is the rollout execution phase. M6 is the final release gate. No milestone may begin before its predecessors are accepted.

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Lock Data Contracts and State Machine | Contract/Schema | P0-Critical | 3-4 days | None | GateResult, OverrideRecord, event schemas, transition table, versioning policy, tests | Low -- pure specification work, no runtime coupling |
| M2 | Deterministic Evaluator and Transition Validator | Core Engine | P0-Critical | 4-5 days | M1 | Gate evaluator, transition validator, fail-safe unknown handling, replay tests | Medium -- evaluator correctness is the system's integrity boundary |
| M3 | Runtime Controls: Lease, Heartbeat, Retry, Recovery | Runtime | P1-High | 3-4 days | M1, M2 | Lease/heartbeat mechanism, retry with bounded attempts, timeout semantics, deadlock-free proof | High -- concurrency and timeout logic is the primary deadlock surface |
| M4 | CLI Integration, Override Governance, Report Persistence | Integration | P1-High | 4-5 days | M1, M2, M3 | /sc:audit-gate command, completion/release guards in tui.py, override flow, report storage | Medium -- integration surface is wide but contracts are stable |
| M5 | Rollout Execution: Shadow, Soft, Full | Rollout | P2-Standard | 3-4 days | M1, M2, M3, M4 | Phase transitions, KPI calibration, rollback drills, safe-disable mechanism | Medium -- operational, not architectural; depends on all prior milestones |
| M6 | Release Decision Gate | Governance | P2-Standard | 1-2 days | M1, M2, M3, M4, M5 | Blocker closure, owner/deadline assignments, GO/NO-GO decision | Low -- administrative gate, no new code |

---

## Dependency Graph

```
M1 ──────────────────────────────┐
│                                │
├──► M2 ──────────┐              │
│                  │              │
├──► M3 ◄─── M2   │              │
│         │        │              │
│         ▼        ▼              │
│         M4 ◄──── M3            │
│                                │
│         M5 ◄──── M4 ◄──────────┘
│
│         M6 ◄──── M5
```

Linearized: M1 --> M2 --> M3 --> M4 --> M5 --> M6

M3 has a hard dependency on both M1 (failure classes, state definitions) and M2 (evaluator outcomes feed retry logic). M4 depends on M1, M2, and M3 because the CLI must enforce transitions validated by M2 and handle runtime states from M3. M5 and M6 are strictly sequential after M4.

---

## M1: Lock Data Contracts and State Machine

### Objective

Define, version, and freeze all data schemas and the state machine transition table so that every downstream milestone has an immutable contract surface to build against. This milestone produces no runtime code -- only type definitions, enums, dataclasses, and deterministic tests that assert schema shape and transition legality.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M1.1 | `GateResult` dataclass in `models.py` with all required fields (version, gate_run_id, scope, entity_id, profile, status, score, threshold, checks[], drift_summary, override, timing, artifacts, failure_class) | Dataclass instantiation with all fields succeeds. Missing required field raises TypeError. JSON round-trip preserves all fields. Version field is `"1.2.1"`. |
| M1.2 | `OverrideRecord` dataclass with all required fields (record_id, scope, entity_id, actor, reason_code, reason_text, created_at, expires_at, linked_gate_run_id, approver, approval_state, review_due_at) | Same shape tests as M1.1. Scope field rejects `"release"` at construction time via validator. |
| M1.3 | `GateTransitionEvent` and `GateCheckEvent` dataclasses | Event schemas instantiate correctly. `correlation_id` links events across a gate run. `evidence_refs[]` on GateCheckEvent is non-empty when outcome is failure. |
| M1.4 | Scope enum (`task`, `milestone`, `release`), Profile enum (`strict`, `standard`, `legacy_migration`), FailureClass enum (`policy`, `transient`, `system`, `timeout`, `unknown`), GateStatus enum (`passed`, `failed`) | All enums are exhaustive. No member can be added without a code change. String values match canonical terminology from spec section 3.1. |
| M1.5 | State machine transition table: legal transitions per scope (task, milestone, release) encoded as a data structure (dict or frozen set) | `test_audit_gate_state_machine.py` asserts every legal transition succeeds and every illegal transition (spec section 4.2, items 1-6) raises `IllegalTransitionError`. Release scope: `audit_release_failed -> released` is always illegal. |
| M1.6 | Versioning policy enforcement: evaluator rejects unsupported major versions | Test: GateResult with `version="2.0.0"` fed to version checker returns `failed(unknown)`. GateResult with `version="1.3.0"` (minor bump) is accepted. |
| M1.7 | Profile/strictness resolution logic (spec section 3.2) | `strictness=strict` maps to `profile=strict`. `legacy_migration` cannot be expressed via strictness. At full enforcement phase, strictness alias is rejected. Tests cover all four rules from spec 3.2. |

### Dependencies

None. This is the foundation milestone.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Schema churn after lock | Low | High -- every downstream milestone reworks | Require explicit sign-off on M1 deliverables before M2 begins. No "soft lock." |
| Conflict with existing `PhaseStatus`/`SprintOutcome` enums | Low | Medium -- naming collisions in models.py | New audit enums use `Audit` prefix or separate module (`audit_models.py`). Verify no import collision. |
| Incomplete illegal transition set | Medium | High -- unblocked bypass paths | Enumerate all (state, state) pairs exhaustively in tests. Any pair not in the legal set is illegal by default (closed-world assumption). |

---

## M2: Deterministic Evaluator and Transition Validator

### Objective

Implement the gate evaluator (pass/fail decision engine) and the transition validator (state machine enforcement) as pure functions operating on the M1 contracts. Both must be deterministic: given identical inputs, they produce identical outputs with no side effects.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M2.1 | Gate evaluator function: `evaluate(checks: list[Check], profile: Profile) -> GateResult` | Any blocking check failure returns `status=failed`. Unknown/missing deterministic inputs return `failed`. Missing evidence for a failed check returns `failed` with `failure_class=policy`. 100% replay stability: same inputs produce byte-identical GateResult (excluding timing fields). |
| M2.2 | Transition validator function: `validate_transition(scope, from_state, to_state, gate_result, override) -> bool` | Rejects all six illegal transition categories from spec section 4.2. Accepts legal transitions. Override with approved OverrideRecord allows `audit_task_failed -> completed` and `audit_milestone_failed -> completed`. Override never allows `audit_release_failed -> released`. |
| M2.3 | Fail-safe unknown handling | GateResult with `failure_class=unknown` blocks completion. Evaluator returns `failed` for any check it cannot classify. Test: inject an unrecognized check type; evaluator returns `failed(unknown)`, not an exception. |
| M2.4 | Evidence validation in evaluator | Every failed check in GateResult must contain at least one `evidence_ref` (file path or file:line). Evaluator rejects a failed check with empty evidence_refs as `failed` and `non-completable`. Drift summary separates edited vs non-edited files. |
| M2.5 | `test_audit_gate_profiles.py` -- profile determinism tests | Each profile (strict, standard, legacy_migration) produces predictable severity mappings. Changing profile changes gate behavior deterministically. No profile produces non-deterministic results across runs. |
| M2.6 | `test_audit_gate_state_machine.py` -- stuck-state recovery transitions | `audit_*_running` with expired lease transitions to `audit_*_failed(timeout)`. Retry from `audit_*_failed` re-enters `audit_*_running` if attempt budget remains. Exhausted retry budget stays in `failed` permanently. |

### Dependencies

- **M1** (all deliverables): Evaluator and validator consume GateResult, OverrideRecord, enums, and the transition table.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Evaluator produces non-deterministic results due to ordering | Medium | High -- gate trust collapses | Sort checks by ID before evaluation. Freeze all intermediate collections. Test with permuted input orders. |
| Transition validator has gaps in the illegal set | Low | Critical -- bypass allows unapproved completion | Closed-world approach: only explicitly listed transitions are legal. All others fail. Exhaustive pair testing in M2.6. |
| Profile severity mapping ambiguity for edge cases | Medium | Medium -- inconsistent gate outcomes | Require spec owner to sign off on severity table before M2 begins. Add property-based tests. |

---

## M3: Runtime Controls -- Lease, Heartbeat, Retry, Recovery

### Objective

Implement the timeout, retry, and recovery semantics that prevent the state machine from entering deadlock or stale-running states. This milestone introduces the only concurrency-sensitive components in the system.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M3.1 | Lease/heartbeat mechanism for `audit_*_running` states | Running gate acquires lease with configurable TTL. Heartbeat extends lease. Missing heartbeat past TTL triggers `audit_*_failed(timeout)`. Test: simulate heartbeat stop; verify state transitions to failed(timeout) within 2x TTL. |
| M3.2 | Bounded retry with per-scope attempt budget | Retry from `failed` re-enters `running` only if attempts < max. Configurable per scope (task: 3, milestone: 2, release: 1 -- defaults). Exhausted budget stays in `failed` permanently. Test: exhaust budget, verify no further retry allowed. |
| M3.3 | Backoff strategy between retries | Exponential backoff with jitter. Configurable base delay and max delay. Test: verify delay sequence is monotonically non-decreasing (modulo jitter). |
| M3.4 | Stale-running recovery | Background check detects `audit_*_running` with expired lease and no heartbeat. Transitions to `failed(timeout)`. Test: inject stale-running state, verify automatic recovery within one polling interval. |
| M3.5 | Deadlock-free proof by construction | No cycle exists in the state machine that can be entered without an exit. Formal argument (documented) showing every `running` state has a timeout exit, every `failed` state has either retry or terminal, and retry is bounded. Test: property-based test with random state sequences; verify all terminate. |
| M3.6 | Timeout/retry/backoff configuration schema | Configuration dataclass with per-scope overrides. Validated at load time (no negative TTLs, max_attempts >= 1). Test: invalid config raises ValueError at construction. |

### Dependencies

- **M1**: Failure classes (timeout, transient), state definitions, GateResult schema.
- **M2**: Evaluator outcomes feed retry decisions. Transition validator enforces retry legality.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Heartbeat race condition: heartbeat arrives after timeout fires | Medium | High -- state oscillation between running and failed | Lease check uses monotonic clock. Heartbeat rejected if lease already expired. Single-writer state transitions with compare-and-swap semantics. |
| Retry budget not decremented atomically | Low | Medium -- extra retries allowed | Atomic decrement or single-threaded retry controller. Test under concurrent heartbeat + retry. |
| Stale-running detector fires during normal operation | Low | Medium -- false timeout | TTL must be significantly longer than expected gate duration. Configurable per scope. Alert on TTL < 2x median gate duration. |

---

## M4: CLI Integration, Override Governance, Report Persistence

### Objective

Wire the evaluator (M2) and runtime controls (M3) into the user-facing CLI (`/sc:audit-gate`), the sprint TUI completion guards, and the override governance workflow. Persist gate reports for audit trail.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M4.1 | `/sc:audit-gate` command skill (SKILL.md + rules + templates) in `src/superclaude/skills/sc-audit-gate/` | Command accepts `--scope`, `--profile`, `--entity-id`. Returns GateResult JSON. Handles all three scopes. Test: invoke with mock evaluator, verify GateResult output matches schema. |
| M4.2 | Evaluator protocol skill in `src/superclaude/skills/sc-audit-gate-protocol/` | SKILL.md defines deterministic evaluator workflow, transition legality rules, and recovery flow. Consumable by agent system. |
| M4.3 | Completion/release guards in `tui.py` | `in_progress -> completed` blocked unless latest gate status is `passed` or approved override exists (task/milestone only). `-> released` blocked unless gate status is `passed` (no override). Test: attempt illegal transition via TUI path, verify rejection with error message. |
| M4.4 | Override governance flow | Override request creates OverrideRecord with required metadata (approver, reason_code, review_due_at). Incomplete metadata rejects override. Override for release scope rejected at creation. Test: `test_audit_gate_overrides.py` covers scope-limited creation, metadata validation, release rejection. |
| M4.5 | Report persistence | GateResult serialized to JSON file in results directory. GateTransitionEvent and GateCheckEvent appended to JSONL event log. Test: run gate, verify files exist and parse correctly. |
| M4.6 | Profile parameter handling with strictness alias | `--profile strict` works. `--strictness strict` works in shadow/soft phases (mapped to profile). `--strictness` rejected in full enforcement phase. `--profile legacy_migration` works; no strictness equivalent. |

### Dependencies

- **M1**: All schemas consumed by CLI serialization and TUI guards.
- **M2**: Evaluator and transition validator called by CLI command and TUI guards.
- **M3**: Runtime controls (lease, retry) active during gate execution initiated by CLI.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TUI guard integration breaks existing sprint flow | Medium | High -- sprint runner regression | Guard logic added behind feature flag (shadow mode default). Existing `PhaseStatus` flow untouched. New audit states are additive. Run full sprint regression suite (`test_regression_gaps.py`) after integration. |
| Override metadata validation too strict for early adoption | Low | Medium -- user friction | Shadow mode logs but does not block on incomplete metadata. Soft mode warns. Full mode blocks. |
| Report persistence I/O failure during gate execution | Low | Medium -- gate result lost | Write report before returning result. Retry write once on I/O error. Log warning if write fails but do not fail the gate itself. |

---

## M5: Rollout Execution -- Shadow, Soft, Full

### Objective

Execute the three-phase rollout (shadow, soft, full) with promotion criteria, rollback triggers, and safe-disable mechanisms. Calibrate KPI thresholds during shadow mode.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M5.1 | Shadow mode implementation | Gates execute and produce artifacts but do not block transitions. All gate results logged. Existing sprint flow unmodified. Test: run sprint with shadow gating enabled, verify completion succeeds regardless of gate outcome. |
| M5.2 | Soft mode implementation | Gates produce warnings on failure. Completion proceeds with logged warning. Override flow active but advisory. Test: failed gate produces warning in TUI, completion allowed. |
| M5.3 | Full mode implementation | Gates block transitions. Override flow enforced. Strictness alias rejected. Test: failed gate blocks completion, only approved override allows it (task/milestone). Release never overridable. |
| M5.4 | Promotion criteria enforcement | Shadow->Soft requires passing M1, M4, M5 acceptance tests. Soft->Full requires all milestones passing for two consecutive windows plus rollback drill success. Test: simulate promotion with failing prerequisite, verify rejection. |
| M5.5 | Rollback triggers and safe-disable | Five normative triggers from spec section 7.3 implemented. Rollback order: full->soft->shadow. Emergency safe-disable keeps shadow artifact production. Test: `test_audit_gate_rollout.py` covers all five triggers and rollback path. |
| M5.6 | KPI baseline calibration | Collect gate metrics during shadow window. Compute baseline distributions. Thresholds remain provisional until explicit owner sign-off. Test: verify calibration produces threshold proposals, not enforcement. |

### Dependencies

- **M1, M2, M3, M4**: All prior milestones must be accepted. Rollout is the integration test of the entire system.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shadow mode artifacts diverge from soft/full behavior | Medium | Medium -- calibration data invalid | Shadow mode uses identical evaluator and transition validator as soft/full. Only enforcement differs. |
| Rollback drill fails, blocking soft->full promotion | Medium | High -- release delayed | Schedule rollback drills early in soft phase. Fix issues before promotion window. |
| KPI thresholds set too aggressively after calibration | Low | Medium -- false gate failures in full mode | Thresholds are advisory until explicit owner sign-off. Include safety margin in proposals. |

---

## M6: Release Decision Gate

### Objective

Close all blocking decisions, verify owner/deadline assignments, and execute the GO/NO-GO decision for v1.2.1 release.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| M6.1 | Blocker closure verification | All four blockers from spec section 12.3 resolved: profile thresholds finalized, retry/backoff values finalized, rollback triggers finalized, blocking decisions assigned owner+deadline. Evidence: decision records with signatures. |
| M6.2 | Required user decisions obtained | All five decisions from spec section 12.4 approved: canonical profile model, major-severity behavior at task tier, retry/backoff/timeout values, rollback triggers, override governance model. Evidence: approval artifacts. |
| M6.3 | Owner/deadline assignment for all open decisions | Every open blocking decision has: Owner (named individual), UTC deadline, Effective rollout phase. No exceptions. |
| M6.4 | GO/NO-GO decision | All M1-M5 acceptance criteria met. All blockers closed. All required decisions approved. Rollback drill passed. GO decision documented with date and signatories. |

### Dependencies

- **M1, M2, M3, M4, M5**: All milestones accepted.

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Decision owners unavailable for sign-off | Medium | High -- release blocked | Assign backup decision owners. Set deadlines with 3-day buffer before release target. |
| Late-breaking blocker discovered during GO review | Low | High -- release delayed | M5 rollback drill is specifically designed to surface these. Address in soft phase. |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R1 | Schema churn after M1 lock invalidates downstream work | M2, M3, M4 | Low | Critical | Hard lock with sign-off. No changes without version bump and impact assessment. | State-machine owner |
| R2 | Evaluator non-determinism due to input ordering | M2, M4, M5 | Medium | High | Sort inputs, freeze collections, property-based testing with permuted orders. | State-machine owner |
| R3 | Heartbeat race condition causes state oscillation | M3, M4 | Medium | High | Monotonic clock, lease expiry rejects late heartbeats, single-writer transitions. | Reliability owner |
| R4 | Deadlock in retry/timeout interaction | M3 | Low | Critical | Bounded retries, formal termination argument, property-based random walk tests. | Reliability owner |
| R5 | TUI guard integration regresses sprint runner | M4 | Medium | High | Feature flag (shadow default), full regression suite, rollback capability. | Migration owner |
| R6 | Rollback drill failure blocks promotion | M5, M6 | Medium | High | Early drill scheduling, fix-forward in soft phase, backup rollback procedure. | Migration owner |
| R7 | Incomplete illegal transition set allows bypass | M1, M2 | Low | Critical | Closed-world assumption: only listed transitions are legal. Exhaustive pair tests. | State-machine owner |
| R8 | Profile threshold disagreement delays release | M6 | Medium | Medium | Provisional thresholds in shadow, calibration data informs decision, owner escalation path. | Policy owner |
| R9 | Strictness/profile alias confusion during rollout | M4, M5 | Low | Medium | Clear deprecation messaging, reject strictness at full enforcement, migration guide. | Migration owner |
| R10 | Override metadata validation blocks legitimate overrides | M4 | Low | Medium | Shadow: log only. Soft: warn. Full: enforce. Graduated strictness reduces friction. | Policy owner |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|-------------------------|-----------|
| Milestone ordering | Contracts-first (M1 before all implementation) | Parallel contract/implementation, feature-first | Prevents cascading rework. Every component depends on schema shape. 3-4 day upfront cost saves weeks of rework. |
| State machine enforcement approach | Closed-world (only listed transitions legal) | Open-world (only listed transitions illegal) | Closed-world eliminates bypass categories by default. Any new state requires explicit transition declaration. |
| Audit types location | Separate from existing sprint models (new module or prefixed types) | Merge into existing `models.py` | Avoids collision with `PhaseStatus`/`SprintOutcome`. Independent versioning. Clear ownership boundary. |
| Override scope restriction | Compile-time enforcement (OverrideRecord validator rejects release scope) | Runtime check only | Catches invalid overrides at creation, not at transition time. Defense in depth. |
| Rollout default | Shadow mode (non-blocking) as initial state | Soft mode as default | Shadow produces calibration data with zero user impact. Reduces adoption risk. |
| Retry termination guarantee | Bounded attempt budget with formal argument | Unbounded retry with circuit breaker | Bounded budget is provably terminating. Circuit breaker adds operational complexity without stronger guarantees. |

---

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|------------------------|------------|
| SC1 | All data contracts (GateResult, OverrideRecord, event schemas) instantiate correctly with required fields and reject invalid inputs | M1 | Unit tests: 100% field coverage, all validators exercised |
| SC2 | State machine transition table rejects all six illegal transition categories from spec section 4.2 | M1, M2 | Test: exhaustive (state, state) pair coverage, zero false accepts |
| SC3 | Gate evaluator produces identical GateResult for identical inputs across 1000 replay runs | M2 | Property-based test: determinism assertion, zero bit-level variance (excluding timing) |
| SC4 | No state machine path exists that enters a cycle without a bounded exit | M3 | Formal argument documented + property-based random walk test (10K sequences, all terminate) |
| SC5 | `/sc:audit-gate` command returns valid GateResult JSON for all three scopes | M4 | Integration test: invoke command, parse output, validate against schema |
| SC6 | Override for release scope is rejected at every enforcement layer (creation, transition, CLI) | M1, M2, M4 | Three independent tests: OverrideRecord validator, transition validator, CLI handler |
| SC7 | Shadow mode produces gate artifacts without blocking any transition | M5 | End-to-end test: sprint run with shadow gating, all phases complete regardless of gate outcome |
| SC8 | Rollback from full to shadow completes within one polling interval and re-enables artifact production | M5 | Integration test: trigger rollback, verify shadow mode active, verify artifacts produced |
| SC9 | All five normative rollback triggers cause automatic phase demotion | M5 | `test_audit_gate_rollout.py`: five trigger scenarios, all produce correct phase transition |
| SC10 | All blocking decisions from spec section 12.3 closed with owner, deadline, and approval artifact | M6 | Checklist: four blockers verified, five required decisions approved, zero open items |
