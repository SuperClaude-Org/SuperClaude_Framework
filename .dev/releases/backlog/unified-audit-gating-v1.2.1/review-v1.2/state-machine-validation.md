# Unified Audit Gating System v1.2 — State Machine Validation

## Deterministic findings

Evidence base:
- `02-design-spec-v1.md` → **State Machine**
- `04-design-v1.1-delta-handoff.md` → **State Machine (v1.1)**, **Transition invariants**
- `05-review-checklist.md` → **3) State Machine & Transition Invariants**

Current gap: transition notation is concise but not normative enough to guarantee illegal-transition rejection and recovery behavior.

## Transition table (proposed normative form)

### Task scope
| From | To | Allowed | Guard | Action |
|---|---|---|---|---|
| in_progress | ready_for_audit_task | Yes | task exists and mutable | enqueue gate run |
| ready_for_audit_task | audit_task_running | Yes | runner acquired lease | start checks |
| audit_task_running | audit_task_passed | Yes | all blocking checks pass | persist GateResult(pass) |
| audit_task_running | audit_task_failed | Yes | any blocking check fails or timeout | persist GateResult(fail) |
| audit_task_passed | completed | Yes | no superseding drift detected | finalize completion |
| audit_task_failed | ready_for_audit_task | Yes | retry policy allows | schedule rerun |
| audit_task_failed | completed | Conditional | explicit approved override exists (task scope only) | finalize completion with linked OverrideRecord |
| audit_task_failed | completed | **No** | no approved override | reject transition |

### Milestone scope
| From | To | Allowed | Guard | Action |
|---|---|---|---|---|
| in_progress | ready_for_audit_milestone | Yes | all child tasks terminal | enqueue gate run |
| ready_for_audit_milestone | audit_milestone_running | Yes | runner acquired lease | start checks |
| audit_milestone_running | audit_milestone_passed | Yes | all blocking checks pass | persist GateResult(pass) |
| audit_milestone_running | audit_milestone_failed | Yes | blocking failure or timeout | persist GateResult(fail) |
| audit_milestone_passed | completed | Yes | no unresolved blockers | finalize completion |
| audit_milestone_failed | ready_for_audit_milestone | Yes | retry policy allows | schedule rerun |
| audit_milestone_failed | completed | Conditional | explicit approved override exists (milestone scope only) | finalize completion with linked OverrideRecord |
| audit_milestone_failed | completed | **No** | no approved override | reject transition |

### Release scope
| From | To | Allowed | Guard | Action |
|---|---|---|---|---|
| in_progress | ready_for_audit_release | Yes | all milestones terminal | enqueue gate run |
| ready_for_audit_release | audit_release_running | Yes | runner acquired lease | start checks |
| audit_release_running | audit_release_passed | Yes | all release checks pass | persist GateResult(pass) |
| audit_release_running | audit_release_failed | Yes | blocking failure or timeout | persist GateResult(fail) |
| audit_release_passed | released | Yes | pass is current | finalize release |
| audit_release_failed | ready_for_audit_release | Yes | retry policy allows | schedule rerun |
| audit_release_failed | released | **No** | always false | hard block |

## Illegal transitions (minimum set)
1. `in_progress -> completed` (task/milestone) or `in_progress -> released` (release)
2. `ready_for_audit_* -> completed` (task/milestone) or `ready_for_audit_release -> released`
3. `audit_*_running -> completed` (task/milestone) or `audit_release_running -> released`
4. `audit_*_failed -> completed` (task/milestone without approved override)
5. `audit_release_failed -> released` (release override forbidden)
6. Any transition out of terminal state (`completed` or `released`) except explicit reopen operation

Evidence anchors:
- `01-requirements-spec.md` → **Acceptance Criteria (1,2,3,5)**
- `02-design-spec-v1.md` → **Failure / Override Policy**
- `04-design-v1.1-delta-handoff.md` → **Transition invariants**

## Recovery paths
1. **Timeout recovery**: `audit_*_running -> audit_*_failed(timeout)` then requeue allowed by bounded retry policy.
2. **Transient runner failure**: same as timeout path.
3. **Policy failure**: remain failed until evidence/artifacts corrected.
4. **Override (task/milestone only)**: explicit governance record enables completion path.

## Stuck-state handling
1. Add lease + heartbeat on `audit_*_running`.
2. Mark stale if heartbeat missing beyond threshold.
3. Force transition to `audit_*_failed(timeout)`.
4. Emit transition event with correlation ID for replay.
5. Requeue only if retry budget remains.

## Heuristic judgments
- Without explicit lease/heartbeat and bounded retries, deadlock resistance remains weak despite v1.1 intent.
- A deterministic transition validator should run before all completion/release operations to prevent bypass.
