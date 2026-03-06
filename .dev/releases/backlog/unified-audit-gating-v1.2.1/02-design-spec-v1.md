# Unified Audit Gating System — Official Design Spec v1.0

## Command / API Surface
Primary command: /sc:audit-gate

Examples:
- /sc:audit-gate task --id T02.04
- /sc:audit-gate milestone --id M2
- /sc:audit-gate release --id v2.05

Flags:
- --strictness standard|strict
- --mode auto|manual
- --output human|json|both
- --override --reason "..." (task/milestone only)
- --fail-on missing|drift|all
- --non-edited-only

## State Machine
Task:
in_progress -> ready_for_audit_task -> audit_task_running -> audit_task_passed|audit_task_failed -> completed

Milestone:
in_progress -> ready_for_audit_milestone -> audit_milestone_running -> audit_milestone_passed|audit_milestone_failed -> completed

Release:
in_progress -> ready_for_audit_release -> audit_release_running -> audit_release_passed|audit_release_failed -> released

## Data Model (v1.0)
- GateDefinition
- GateRun
- CheckResult
- OverrideRecord
- ArtifactIndex

## Tier Weights / Depth
Tier 1 (Task): high frequency, shallow checks
Tier 2 (Milestone): medium frequency, medium depth
Tier 3 (Release): low frequency, deep/full audit

## Skills / Agents / Templates
Skills:
- sc-audit-gate
- sc-audit-gate-protocol

Agents:
- audit-scanner
- audit-analyzer
- audit-comparator
- audit-consolidator

Templates:
- task-audit-report.md
- milestone-audit-report.md
- release-audit-report.md
- drift-ledger.md
- override-record.md

## Sprint CLI Integration
Invoke gates before:
1) task completion
2) milestone completion
3) release completion

## Configuration Model
- gate-policy.yaml
- gate-check-catalog.yaml
- gate-thresholds.yaml
- state-machine.md

## Failure / Override Policy
- Fail blocks completion transition
- Override allowed only task/milestone with required reason
- Release override forbidden

## Migration / Rollout
- Shadow mode -> soft enforcement -> full enforcement
- Legacy status mapping adapters
