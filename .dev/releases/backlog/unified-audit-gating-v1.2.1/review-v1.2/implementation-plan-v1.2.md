# Unified Audit Gating System v1.2 — Implementation Plan

## Plan objective
Implement v1.2 as deterministic, measurable, and rollout-safe gating with low Tier-1 friction and explicit transition legality.

## Deterministic findings driving plan
- Open items in v1.1 block reliable implementation readiness.
  - Evidence: `04-design-v1.1-delta-handoff.md` → **Open Items for Next Reviewer**.
- Checklist requires rollback/safe-disable and explicit transition reliability controls.
  - Evidence: `05-review-checklist.md` → **3) State Machine**, **8) Migration**, **9) Risk & Reliability**, **10) Readiness**.

## Phased plan

### Phase 0 — Design lock and policy freeze
- Lock profile thresholds (`strict|standard|legacy_migration`) and major-severity behavior at task tier.
- Lock legal/illegal transition table and retry/backoff policy.
- Define rollback/safe-disable rules and owner approvals.

**Acceptance checks**
- All v1.1 open items have owner + decision date + approved value.
- Transition table and illegal transitions approved.

### Phase 1 — Core gate contracts + deterministic evaluator
- Implement canonical `GateResult`/`OverrideRecord` concrete schemas with version + evidence requirements.
- Add deterministic evaluator for pass/fail independent of agent enrichment.
- Add transition validator before completion/release operations.

**Acceptance checks**
- Same input replay produces identical pass/fail and check outcomes.
- Missing/unknown evidence path causes fail/blocked.

### Phase 2 — State-machine runtime controls
- Implement heartbeat/lease for `audit_*_running`.
- Implement bounded retry/backoff and failure-class mapping.
- Add stuck-state auto-recovery transitions.

**Acceptance checks**
- Timeout scenarios move to deterministic failed state.
- Retry exhaustion handled without deadlock.

### Phase 3 — Sprint CLI integration and governance flow
- Invoke gates at task/milestone/release completion transition points.
- Enforce release override prohibition; implement task/milestone override approval workflow.
- Persist machine + human-readable reports and transition events.

**Acceptance checks**
- Completion/release is blocked on failed gate per scope.
- Overrides accepted only where policy allows and with mandatory reason metadata.

### Phase 4 — Rollout and measurement gates
- Shadow mode: collect baseline metrics and false-block rate.
- Soft mode: enforce in selected scopes/profiles.
- Full mode: enforce globally when KPI thresholds pass.
- Add rollback hooks from full→soft→shadow.

**Acceptance checks**
- KPI thresholds in `metrics-and-gates.md` pass for two consecutive windows.
- Rollback drill succeeds without data loss.

## File-level change map (target)

> Note: this is implementation mapping, not code execution.

1. `src/superclaude/cli/sprint/models.py`
- Add explicit audit state enums/transition constraints and profile fields.

2. `src/superclaude/cli/sprint/tui.py`
- Add completion/release guards and clear operator failure guidance.

3. `src/superclaude/skills/sc-audit-gate/SKILL.md` (or equivalent skill package path)
- Define command behavior, profile semantics, output contract.

4. `src/superclaude/skills/sc-audit-gate-protocol/SKILL.md` (or protocol path)
- Define deterministic evaluator + retry/timeout flow + legality checks.

5. `src/superclaude/agents/*.md` (audit scanners/analyzers/consolidators as enrichment only)
- Clarify they enrich evidence; they do not define pass/fail truth.

6. `tests/sprint/test_audit_gate_state_machine.py` (new)
- Legal/illegal transition tests and stuck-state recovery tests.

7. `tests/sprint/test_audit_gate_profiles.py` (new)
- Threshold/profile determinism tests and major-severity behavior tests.

8. `tests/sprint/test_audit_gate_overrides.py` (new)
- Scope-constrained override governance tests.

9. `tests/sprint/test_audit_gate_rollout.py` (new)
- Shadow/soft/full and rollback behavior tests.

10. `.dev/releases/backlog/audit-gate/review-v1.2/*.md`
- Keep as design governance source for v1.2 acceptance and rollout control.

## Dependencies and sequencing
- Phase 0 must complete before all other phases.
- Phase 1 before Phase 3.
- Phase 2 before Phase 4 full enforcement.
- Phase 3 and part of Phase 2 can run in parallel once Phase 1 contracts are frozen.

## Heuristic judgments
- Fastest stable path is: **contract lock first**, then implementation, then rollout.
- Attempting rollout before deterministic profile/transition freeze likely increases churn and rollback frequency.
