# Unified Audit Gating System — Design v1.1 Delta + Handoff

## Purpose
This packet is optimized for a new model to review/iterate with minimal missing context.

## Locked User Decisions
1. Configurable strictness
2. Tier-1 required for LIGHT/EXEMPT
3. Overrides allowed only task/milestone
4. Single primary command
5. Explicit audit_* states

## v1.1 Delta Summary
A) Deterministic-first gate core (agents for enrichment, not core truth)
B) Policy profiles added: strict, standard, legacy_migration
C) Tier-1 runtime budget and reduced check scope
D) State machine hardening with retry/timeout/recovery
E) Structured override governance records
F) Drift severity classes: critical/major/minor
G) Mandatory phased rollout: shadow -> soft -> full

## Canonical GateResult Schema (v1.1)
- version
- gate_run_id
- scope/entity_id/profile
- status/score/threshold
- checks[] with severity + evidence
- drift_summary edited/non_edited
- override block
- timing block
- artifacts block

## Canonical OverrideRecord Schema (v1.1)
- record_id
- scope (task|milestone only)
- entity_id
- actor
- reason_code + reason_text
- created_at / expires_at
- linked_gate_run_id

## State Machine (v1.1)
Task:
in_progress -> ready_for_audit_task -> audit_task_running -> audit_task_passed|audit_task_failed -> completed

Milestone:
in_progress -> ready_for_audit_milestone -> audit_milestone_running -> audit_milestone_passed|audit_milestone_failed -> completed

Release:
in_progress -> ready_for_audit_release -> audit_release_running -> audit_release_passed|audit_release_failed -> released

Transition invariants:
- completion blocked without audit pass
- release overrides forbidden
- running timeout -> failed(error)

## Tier Check Matrix (v1.1)
Task: light deterministic checks
Milestone: aggregate + consistency checks
Release: full closure + drift + checkpoint completeness

## Open Items for Next Reviewer
1. Numeric thresholds by profile
2. Standard-profile handling of major severity at task tier
3. Retry/backoff policy tuning
4. Artifact retention policy

## Recommended Review Order
1) GateResult schema
2) Transition invariants
3) Tier policy realism
4) Rollout safety
5) File-level implementation mapping
