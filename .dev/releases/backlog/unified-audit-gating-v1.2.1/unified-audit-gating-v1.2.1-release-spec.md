# Unified Audit Gating System v1.2.1 — Release Specification (Implementation-Ready)

Document status: **Draft for sign-off**
Decision baseline date: **2026-03-03**
Primary intent: direct input for roadmap generation and phased tasklist creation.

---

## 0. Evidence Model and Decision Method

### 0.1 Deterministic findings (normative in this spec)
Deterministic items are requirements, invariants, contracts, and state/decision rules that are directly specified in source artifacts and are testable/replayable.

### 0.2 Heuristic judgments (advisory in this spec)
Heuristic items are operational recommendations (e.g., rollout pacing, UX friction mitigation) derived from reviews/risk analysis and are non-authoritative unless promoted to a locked decision.

### 0.3 Citation rule used
Critical claims cite source file + section label. If section labels are absent, file heading context is used.

---

## 1. Release Scope and Goals

### 1.1 Scope
Implement a unified audit-gating capability that blocks completion/release transitions unless the corresponding gate passes at three scopes:
1. Task gate
2. Milestone gate
3. Release gate

(Source: `01-requirements-spec.md` → Goal; Task-Level Gate; Milestone-Level Gate; Release-Level Gate)

### 1.2 Primary goals
1. Deterministic pass/fail gating with evidence-backed outputs
2. Explicit audit workflow states for all scopes
3. Single primary user interface (`/sc:audit-gate`)
4. Rollout-safe enforcement (shadow → soft → full)

(Source: `01-requirements-spec.md` → Locked Decisions, Non-Functional Requirements, Command & Enforcement; `02-design-spec-v1.md` → Command/API Surface, Migration/Rollout; `04-design-v1.1-delta-handoff.md` → v1.1 Delta Summary)

### 1.3 Out-of-scope for v1.2.1
- New non-gating product features unrelated to transition control
- Security hardening expansions not required for correctness of gate transitions
- Full auto-tuning of profiles during rollout (deferred)

(Constraint source: user hard requirement + `executive-summary.md` → deferred improvements)

---

## 2. Locked Decisions, Non-Goals, and Contradiction Resolution

### 2.1 Locked decisions (authoritative)
1. Configurable strictness/profile behavior exists
2. Tier-1 gate is required even for LIGHT/EXEMPT flows
3. Overrides allowed only for task/milestone (never release)
4. Single primary command interface
5. Explicit `audit_*` states are required

(Source: `01-requirements-spec.md` → Locked Decisions; `04-design-v1.1-delta-handoff.md` → Locked User Decisions)

### 2.2 Non-goals
- Release-level override capability
- LLM/agent heuristics as source of truth for pass/fail

(Source: `01-requirements-spec.md` → Locked Decisions/Acceptance Criteria; `04-design-v1.1-delta-handoff.md` → v1.1 Delta Summary A)

### 2.3 Contradictions and winning decisions

| Contradiction | Evidence | Winner in v1.2.1 | Rationale |
|---|---|---|---|
| `--strictness standard|strict` vs profile set `strict|standard|legacy_migration` | `02-design-spec-v1.md` → Flags; `04-design-v1.1-delta-handoff.md` → v1.1 Delta Summary B | Canonical model is `--profile strict|standard|legacy_migration`; `--strictness` retained only as temporary alias in shadow/soft, removed at full | Needed for deterministic policy selection and migration compatibility (`design-delta-v1.2.md` → Change 1) |
| Shorthand state expression can imply terminal transition from failed branch | `02-design-spec-v1.md` → State Machine; `state-machine-validation.md` → Current gap | Explicit legal/illegal transition table is authoritative | Removes ambiguity and enables validator enforcement |
| “State machine hardening added” vs retry/backoff still open | `04-design-v1.1-delta-handoff.md` → Delta D + Open Items (3) | v1.2.1 must lock concrete retry/backoff/timeout semantics before GO | Required for deadlock resistance and reproducibility |
| Rollout phases present but rollback/safe-disable not concrete | `02-design-spec-v1.md` → Migration/Rollout; `05-review-checklist.md` → Section 8 | v1.2.1 defines explicit rollback triggers/contracts | Checklist compliance and operational safety |

---

## 3. Canonical Terminology and Policy Model

### 3.1 Canonical terms
- **Scope**: `task | milestone | release`
- **Tier**: `Tier-1(task), Tier-2(milestone), Tier-3(release)`
- **Profile**: `strict | standard | legacy_migration`
- **Gate status**: `passed | failed`
- **Failure class**: `policy | transient | system | timeout | unknown`

(Source: `01-requirements-spec.md` → tier goals; `04-design-v1.1-delta-handoff.md` → profile + schema direction; `design-delta-v1.2.md` → failure-class taxonomy)

### 3.2 Strictness vs profile resolution (normative)
1. Runtime policy resolver consumes `profile` as canonical input.
2. If `strictness` is provided, map `strictness=strict|standard` to `profile=strict|standard`.
3. `legacy_migration` cannot be expressed through `strictness`; must use `profile`.
4. At full enforcement, `strictness` alias is rejected.

(Source: `design-delta-v1.2.md` → Change 1)

---

## 4. Normative State Machine

### 4.1 Legal transitions

#### Task scope
- `in_progress -> ready_for_audit_task`
- `ready_for_audit_task -> audit_task_running`
- `audit_task_running -> audit_task_passed | audit_task_failed`
- `audit_task_passed -> completed`
- `audit_task_failed -> ready_for_audit_task` (retry path)
- `audit_task_failed -> completed` only with approved task override

#### Milestone scope
- `in_progress -> ready_for_audit_milestone`
- `ready_for_audit_milestone -> audit_milestone_running`
- `audit_milestone_running -> audit_milestone_passed | audit_milestone_failed`
- `audit_milestone_passed -> completed`
- `audit_milestone_failed -> ready_for_audit_milestone` (retry path)
- `audit_milestone_failed -> completed` only with approved milestone override

#### Release scope
- `in_progress -> ready_for_audit_release`
- `ready_for_audit_release -> audit_release_running`
- `audit_release_running -> audit_release_passed | audit_release_failed`
- `audit_release_passed -> released`
- `audit_release_failed -> ready_for_audit_release` (retry path)
- `audit_release_failed -> released` is forbidden

(Source: `state-machine-validation.md` → proposed normative form; `01-requirements-spec.md` → Acceptance Criteria; `02-design-spec-v1.md` → Failure/Override Policy)

### 4.2 Illegal transitions (minimum mandatory set)
1. `in_progress -> completed/released` (bypass)
2. `ready_for_audit_* -> completed/released`
3. `audit_*_running -> completed/released`
4. `audit_*_failed -> completed` without approved override (task/milestone only)
5. `audit_release_failed -> released` always
6. Any transition from terminal state except explicit reopen operation

(Source: `state-machine-validation.md` → Illegal transitions)

### 4.3 Override rules (normative)
- Task and milestone may override failed gate only with approved `OverrideRecord`
- Release override is forbidden by invariant

(Source: `01-requirements-spec.md` → Locked Decisions/Acceptance Criteria; `02-design-spec-v1.md` → Failure/Override Policy)

### 4.4 Timeout, retry, recovery semantics
1. `audit_*_running` uses lease + heartbeat.
2. Missing heartbeat past timeout causes `audit_*_failed(timeout)`.
3. Retry is bounded by per-scope attempt budget.
4. Retry exhaustion remains failed and blocks completion/release.
5. Requeue allowed only while budget remains.

(Source: `state-machine-validation.md` → Stuck-state handling/recovery; `risk-register-v1.2.md` → R2; `design-delta-v1.2.md` → Add 4)

---

## 5. Deterministic Gate Decision Contract

### 5.1 Failure classes
- `policy`: rule/threshold violation
- `transient`: recoverable execution issue
- `system`: non-recoverable runner/system error
- `timeout`: stale/expired running state
- `unknown`: unmapped condition (fail-safe)

(Source: `design-delta-v1.2.md` → Add 2; `01-requirements-spec.md` → fail-safe defaults)

### 5.2 Pass/fail rules (normative)
1. Any blocking check failure => gate `failed`.
2. Unknown/missing deterministic inputs => `failed`.
3. Missing evidence for failed check => `failed` and non-completable.
4. Completion/release transitions require latest gate `passed` except approved task/milestone override path.

(Source: `01-requirements-spec.md` → Non-Functional Requirements/Acceptance Criteria; `metrics-and-gates.md` → M5; `state-machine-validation.md`)

### 5.3 Evidence requirements
Every failed check must include at least one evidence reference:
- file path OR
- `file:line`

Drift summary must separate `edited` vs `non-edited`.

(Source: `01-requirements-spec.md` → Reporting + Non-Functional Requirements; `04-design-v1.1-delta-handoff.md` → GateResult schema)

---

## 6. Data Contracts and Versioning

### 6.1 GateResult (normative v1.2.1)
Required fields:
- `version`
- `gate_run_id`
- `scope`, `entity_id`, `profile`
- `status`, `score`, `threshold`
- `checks[]` (includes severity + evidence)
- `drift_summary` (`edited`, `non_edited`)
- `override` block
- `timing` block
- `artifacts` block
- `failure_class` (v1.2 addition)

(Source: `04-design-v1.1-delta-handoff.md` → Canonical GateResult; `design-delta-v1.2.md` → Add 2)

### 6.2 OverrideRecord (normative v1.2.1)
Required fields:
- `record_id`, `scope`, `entity_id`
- `actor`
- `reason_code`, `reason_text`
- `created_at`, `expires_at`
- `linked_gate_run_id`
- `approver`, `approval_state`, `review_due_at` (v1.2 governance addition)

(Source: `04-design-v1.1-delta-handoff.md` → Canonical OverrideRecord; `design-delta-v1.2.md` → Change 2)

### 6.3 Transition event schema (normative)
`GateTransitionEvent` minimum fields:
- `event_id`, `correlation_id`, `occurred_at`
- `scope`, `entity_id`
- `from_state`, `to_state`
- `cause` (`check_failure|timeout|retry|override|manual_reopen|system_error`)
- `gate_run_id` (nullable when pre-run)

`GateCheckEvent` minimum fields:
- `event_id`, `correlation_id`, `gate_run_id`
- `check_id`, `severity`, `outcome`, `evidence_refs[]`

(Source: `design-delta-v1.2.md` → Add 6; `state-machine-validation.md` → correlation ID replay requirement)

### 6.4 Versioning policy
- Backward-compatible additions: minor bump
- Breaking field/semantic changes: major bump
- Gate evaluator must reject unsupported major versions as `failed(unknown)`

(Source basis: determinism/fail-safe requirements in `01-requirements-spec.md`)

---

## 7. Rollout Contract

### 7.1 Phases
1. **Shadow**: collect decisions/metrics; no hard business blocking
2. **Soft**: selective enforcement by profile/scope
3. **Full**: global enforcement

(Source: `02-design-spec-v1.md` → Migration/Rollout; `04-design-v1.1-delta-handoff.md` → Delta G)

### 7.2 Promotion criteria
- Shadow -> Soft: pass M1, M4, M5, M7, M9
- Soft -> Full: pass M1–M12 for two consecutive windows + pass rollback drill (M10)

(Source: `metrics-and-gates.md` → Gate thresholds by rollout phase)

### 7.3 Rollback / safe-disable triggers (normative)
Immediate rollback to prior phase if any occurs:
1. M4 determinism breach below threshold
2. Any M5 evidence completeness failure
3. Unresolved stale-running incident (M7 fail)
4. Failed rollback drill in current window (M10 fail)
5. Transition validator bypass discovered

Rollback order: `full -> soft -> shadow`. Emergency safe-disable keeps shadow artifact production enabled.

(Source: `metrics-and-gates.md`; `risk-register-v1.2.md` R1/R2/R8/R10; `design-delta-v1.2.md` Add 5)

---

## 8. KPI/SLO Framework

### 8.1 Provisional vs normative thresholds
- Thresholds in current KPI table are **provisional** in shadow mode.
- They become **normative** only after calibration and explicit approval at phase gate.

(Source: `metrics-and-gates.md` → KPI/SLO table note)

### 8.2 Calibration method (normative)
1. Collect M1–M12 for at least two shadow windows.
2. Compute baseline distributions and replay stability.
3. Propose thresholds and warning/fail bands.
4. Obtain owner sign-off for normative activation at soft/full gate.

(Source: `metrics-and-gates.md` → Shadow and phase gates)

### 8.3 Warning/fail bands (authoritative examples)
- Runtime bands M1–M3 as defined in KPI table
- Determinism floor M4 strict by tier
- Evidence completeness M5 has no warning band (any miss is fail)

(Source: `metrics-and-gates.md`)

### 8.4 Heuristic operational guidance
If runtime degrades but determinism/evidence remain compliant, optimize check execution before relaxing policy thresholds.

(Source: `metrics-and-gates.md` → Heuristic judgments)

---

## 9. Governance

### 9.1 Override approval model (normative)
- Scope eligibility: task/milestone only
- Required approval metadata: approver identity, approval state, review due date
- Incomplete override metadata is invalid and blocks completion

(Source: `05-review-checklist.md` → Section 6; `design-delta-v1.2.md` → Change 2; `metrics-and-gates.md` → M9)

### 9.2 Owner responsibilities
- **Policy owner**: profile thresholds + severity mapping
- **State-machine owner**: legal/illegal transition validator correctness
- **Reliability owner**: timeout/retry/backoff + stale recovery
- **Migration owner**: rollout/rollback readiness and drills
- **Program manager**: open-decision closure with owner+deadline tracking

(Source: `risk-register-v1.2.md` owners; `checklist-outcome-v1.2.md` blockers)

### 9.3 Decision deadlines (normative requirement)
All open blocking decisions must have:
- Owner
- UTC decision deadline
- Effective rollout phase

No GO decision without all three assigned.

(Source: `05-review-checklist.md` → Section 10; `executive-summary.md` → critical decisions; `checklist-outcome-v1.2.md`)

---

## 10. Implementation Mapping

### 10.1 Phase plan
- **Phase 0**: design/policy lock and owner/date assignments
- **Phase 1**: deterministic contracts + evaluator + transition validator
- **Phase 2**: runtime controls (lease/heartbeat/retry/recovery)
- **Phase 3**: sprint CLI integration + override governance flow + report persistence
- **Phase 4**: rollout execution + KPI gates + rollback drills

(Source: `implementation-plan-v1.2.md`)

### 10.2 File-level change map (implementation target)
1. `src/superclaude/cli/sprint/models.py` — states/enums/constraints/profile fields
2. `src/superclaude/cli/sprint/tui.py` — completion/release guards and operator guidance
3. `src/superclaude/skills/sc-audit-gate/SKILL.md` — command behavior/profile/output contract
4. `src/superclaude/skills/sc-audit-gate-protocol/SKILL.md` — deterministic evaluator and transition legality/recovery flow
5. `src/superclaude/agents/*.md` — enrichment-only role clarification
6. `tests/sprint/test_audit_gate_state_machine.py` — legal/illegal transitions + stuck-state recovery
7. `tests/sprint/test_audit_gate_profiles.py` — profile determinism + severity behavior
8. `tests/sprint/test_audit_gate_overrides.py` — scope-limited override governance
9. `tests/sprint/test_audit_gate_rollout.py` — shadow/soft/full + rollback behavior

(Source: `implementation-plan-v1.2.md` → File-level change map)

### 10.3 Acceptance criteria per phase
- Phase 0: all blocking decisions closed with owner/date
- Phase 1: deterministic replay stability for same input; fail-safe unknown handling
- Phase 2: timeout/retry paths terminate deterministically (no deadlocks)
- Phase 3: transition blocking/override rules enforced per scope
- Phase 4: phase gates pass by KPI criteria and rollback drill success

(Source: `implementation-plan-v1.2.md`; `metrics-and-gates.md`)

---

## 11. Checklist Closure Matrix (Sections 1–10)

Source checklist: `05-review-checklist.md`.

| Checklist section | Current status | Closure condition for GO | Evidence source |
|---|---|---|---|
| 1. Context completeness | PASS (conditional) | Assign owners/deadlines to open items | `checklist-outcome-v1.2.md` |
| 2. Command/API surface | PASS (conditional) | Approve canonical `--profile` and alias policy | `checklist-outcome-v1.2.md`, `design-delta-v1.2.md` |
| 3. State machine/invariants | PASS (conditional) | Enforce legal/illegal transitions in implementation | `checklist-outcome-v1.2.md`, `state-machine-validation.md` |
| 4. Data contracts | PASS (conditional) | Finalize event contracts + compatibility rules | `checklist-outcome-v1.2.md` |
| 5. Tier model soundness | PASS (conditional) | Finalize numeric thresholds + major severity behavior | `checklist-outcome-v1.2.md` |
| 6. Override/governance | PASS (conditional) | Finalize approver model + review cadence | `checklist-outcome-v1.2.md` |
| 7. Sprint CLI integration | PASS (conditional) | Integrate deterministic transition validator before completion transitions | `checklist-outcome-v1.2.md` |
| 8. Migration/backward compatibility | PASS (conditional) | Approve rollback/safe-disable trigger contract | `checklist-outcome-v1.2.md` |
| 9. Risk/reliability controls | PASS (conditional) | Finalize retry/backoff/timeout values and budgets | `checklist-outcome-v1.2.md`, `risk-register-v1.2.md` |
| 10. Implementation readiness | NO-GO (current) | Close all 4 blockers with owner/date and reflect in artifacts | `checklist-outcome-v1.2.md`, `executive-summary.md` |

---

## 12. Final Release Decision Gate

### 12.1 GO criteria
All must be true:
1. Blocking decisions closed (profile thresholds, major severity behavior, retry/backoff/timeout, rollback triggers)
2. Transition legality and recovery semantics implemented and tested
3. Deterministic contract and evidence completeness validated
4. Checklist sections 2,3,4,6,7 fully pass; remaining sections pass or have non-critical tracked gaps
5. Owners/deadlines assigned for any residual non-blocking items

(Source: `05-review-checklist.md` → Minimum Acceptance Threshold + Section 10; `checklist-outcome-v1.2.md`)

### 12.2 NO-GO criteria
Any one is sufficient:
- Any unresolved blocker from section 11
- Missing owner/deadline on blocking decision
- Determinism/evidence gate failure (M4/M5)
- Release override path exists or can be triggered

(Source: `executive-summary.md`; `metrics-and-gates.md`; `01-requirements-spec.md`)

### 12.3 Current blocker list
1. Profile thresholds and task-tier major-severity behavior not finalized
2. Retry/backoff/timeout values not finalized
3. Rollback/safe-disable triggers not finalized
4. Open blocking decisions not yet assigned owner+deadline in final artifact set

(Source: `checklist-outcome-v1.2.md` → Blocking items)

### 12.4 Required user decisions
1. Approve canonical profile model and numeric thresholds
2. Approve major-severity behavior at task tier under `standard`
3. Approve retry/backoff/timeout values and max attempts
4. Approve rollback/safe-disable objective triggers
5. Approve override governance model (single vs dual approver) and review cadence

(Source: `executive-summary.md` → Critical decisions)

---

## Top 5 Immediate Actions
1. Finalize and sign off profile thresholds + major-severity behavior.
2. Finalize retry/backoff/timeout and stale-state budgets.
3. Ratify explicit legal/illegal transition table as implementation authority.
4. Approve rollback/safe-disable triggers and phase regression policy.
5. Assign owner + UTC deadline + effective phase to each blocking decision.

## Top 5 Deferred Improvements
1. Add readiness preview mode pre-gate.
2. Improve human-readable remediation hints in gate failures.
3. Add trend dashboards for drift/override quality.
4. Add profile auto-tuning recommendations from shadow telemetry.
5. Optimize long-horizon artifact retention policy.

## Open Decisions Needed from User
| Decision | Owner | Deadline (UTC) | Effective phase |
|---|---|---|---|
| Profile thresholds + major-severity behavior | [TBD] | [TBD] | Soft |
| Retry/backoff/timeout policy | [TBD] | [TBD] | Soft |
| Rollback/safe-disable triggers | [TBD] | [TBD] | Full |
| Override approver model + review cadence | [TBD] | [TBD] | Soft |
| `--strictness` alias deprecation date | [TBD] | [TBD] | Full |
