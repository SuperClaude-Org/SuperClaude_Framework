# Unified Audit Gating System — Requirements Spec

## Goal
Create a new audit-gating capability (single primary command + supporting skills/agents/refs/templates + sprint CLI integration) that enforces completion at three levels:
1. Task gate (frequent, lightweight)
2. Milestone/Phase gate (moderate depth)
3. Release gate (deep/comprehensive)

Completion transitions are blocked unless corresponding tier audit passes.

## Locked Decisions
1. Gate strictness/configuration is configurable
2. Tier-1 audit required for LIGHT/EXEMPT too
3. Overrides allowed only at task/milestone tiers (not release)
4. Single command as primary interface
5. Explicit audit_* workflow states

## Functional Requirements
### Task-Level Gate
- Task cannot be marked completed until task audit status is PASS.
- Validate existence, schema, minimum traceability, local drift pointers.
- Required states: ready_for_audit_task, audit_task_running, audit_task_passed, audit_task_failed.

### Milestone-Level Gate
- Milestone cannot be completed unless all child tasks are audit-passed or explicitly overridden.
- Additional milestone checks: cross-task consistency, milestone artifact completeness.
- Required states: ready_for_audit_milestone, audit_milestone_running, audit_milestone_passed, audit_milestone_failed.

### Release-Level Gate
- Release cannot be marked released unless all milestones are audit-passed.
- Full deliverable closure + full drift audit + checkpoint completeness required.
- Required states: ready_for_audit_release, audit_release_running, audit_release_passed, audit_release_failed.

### Command & Enforcement
- Primary entrypoint: /sc:audit-gate
- Tier policy applied by scope (task/milestone/release)
- LIGHT/EXEMPT still require Tier-1
- Release overrides prohibited by policy

### Reporting
- Standardized reports for task/milestone/release
- Machine-readable + human-readable outputs
- Drift split: edited vs non-edited

## Non-Functional Requirements
- Deterministic pass/fail
- Evidence-backed findings (path and/or file:line)
- Fast task-gate runtime
- Auditability of all gate transitions and overrides
- Fail-safe defaults (unknown => fail/blocked)

## User Stories
- Developer cannot complete task without artifact proof.
- PM cannot close milestone with unresolved audited tasks.
- Release owner cannot close release with unresolved major/critical drift.
- Auditor can reconstruct decisions from artifacts.

## Acceptance Criteria
1. Task completion blocked when task gate fails.
2. Milestone completion blocked when milestone gate fails.
3. Release completion blocked when release gate fails.
4. Overrides accepted only for task/milestone with required reason record.
5. Release gate rejects override attempts.
6. Gate outputs include pass/fail, criteria outcomes, evidence references.
