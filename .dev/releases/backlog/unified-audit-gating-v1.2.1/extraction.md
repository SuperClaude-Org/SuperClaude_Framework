---
spec_source: docs/generated/unified-audit-gating-v1.2.1-release-spec.md
generated: 2026-03-03T00:00:00Z
generator: sc:roadmap
functional_requirements: 34
nonfunctional_requirements: 10
total_requirements: 44
domains_detected: [backend, security, performance]
complexity_score: 0.654
complexity_class: MEDIUM
risks_identified: 10
dependencies_identified: 9
success_criteria_count: 12
extraction_mode: standard
---

# Extraction: Unified Audit Gating System v1.2.1

## Project Overview

**Title**: Unified Audit Gating System v1.2.1
**Version**: v1.2.1
**Source**: `docs/generated/unified-audit-gating-v1.2.1-release-spec.md`
**Summary**: Implements deterministic pass/fail audit gating that blocks task/milestone/release transitions unless the corresponding gate passes. Provides three-scope gating (task, milestone, release) with explicit audit workflow states, a single primary command interface (`/sc:audit-gate`), and rollout-safe enforcement via shadow→soft→full phases. The system is defined by normative data contracts (GateResult, OverrideRecord, event schemas), a normative state machine transition table, and a phased rollout with explicit promotion criteria and rollback triggers.

---

## Functional Requirements

| ID | Description | Priority | Domain | Source Lines |
|----|-------------|----------|--------|--------------|
| FR-001 | Block task completion transitions unless task-level audit gate passes | P0 | backend | L25-L30 |
| FR-002 | Block milestone completion transitions unless milestone-level audit gate passes | P0 | backend | L25-L30 |
| FR-003 | Block release transitions unless release-level audit gate passes | P0 | backend | L25-L30 |
| FR-004 | Configurable strictness/profile behavior (strict, standard, legacy_migration) | P0 | backend | L51-L53 |
| FR-005 | Tier-1 gate required even for LIGHT/EXEMPT compliance flows | P0 | backend | L52 |
| FR-006 | Overrides allowed for task/milestone scope only; release overrides forbidden | P0 | security | L53-L54 |
| FR-007 | Single primary command interface: `/sc:audit-gate` | P0 | backend | L55 |
| FR-008 | Explicit `audit_*` states required in state machine for all scopes | P0 | backend | L56 |
| FR-009 | Canonical model uses `--profile strict\|standard\|legacy_migration`; `--strictness` is temporary alias removed at full enforcement | P0 | backend | L70-L94 |
| FR-010 | Explicit legal/illegal transition table is authoritative (normative state machine) | P0 | backend | L100-L136 |
| FR-011 | Task scope: legal transitions including retry path and approved-override path to completed | P0 | backend | L102-L109 |
| FR-012 | Milestone scope: legal transitions including retry path and approved-override path | P0 | backend | L111-L117 |
| FR-013 | Release scope: `audit_release_failed → released` is categorically forbidden | P0 | security | L119-L124 |
| FR-014 | Illegal transitions (bypass, running→completed, failed→completed without override) must be enforced | P0 | backend | L128-L135 |
| FR-015 | `audit_*_running` uses lease + heartbeat; missing heartbeat causes `audit_*_failed(timeout)` | P0 | backend | L144-L151 |
| FR-016 | Retry bounded by per-scope attempt budget; exhaustion remains failed and blocks | P0 | backend | L147-L150 |
| FR-017 | Runtime policy resolver consumes `profile` as canonical; `strictness` mapped as alias | P0 | backend | L88-L94 |
| FR-018 | GateResult must include: version, gate_run_id, scope, entity_id, profile, status, score, threshold, checks[], drift_summary, override, timing, artifacts, failure_class | P0 | backend | L188-L200 |
| FR-019 | OverrideRecord must include: record_id, scope, entity_id, actor, reason_code, reason_text, created_at, expires_at, linked_gate_run_id, approver, approval_state, review_due_at | P0 | security | L202-L211 |
| FR-020 | GateTransitionEvent and GateCheckEvent schemas with minimum required fields | P0 | backend | L213-L225 |
| FR-021 | Backward-compatible additions use minor bump; breaking changes use major bump; evaluator rejects unsupported major versions as failed(unknown) | P0 | backend | L227-L232 |
| FR-022 | Rollout via phases: Shadow (no hard blocking), Soft (selective enforcement), Full (global enforcement) | P0 | backend | L239-L243 |
| FR-023 | Shadow→Soft promotion: pass M1, M4, M5, M7, M9 | P0 | backend | L246-L248 |
| FR-024 | Soft→Full promotion: pass M1-M12 for two consecutive windows + rollback drill M10 pass | P0 | backend | L247-L249 |
| FR-025 | Immediate rollback to prior phase on: M4 determinism breach, M5 evidence failure, M7 stale-running, M10 rollback drill fail, transition validator bypass | P0 | backend | L251-L259 |
| FR-026 | Rollback order: full→soft→shadow; emergency safe-disable keeps shadow artifact production | P0 | backend | L259 |
| FR-027 | Sprint CLI integration: transition blocking/override rules enforced before completion transitions | P0 | backend | L337-L342 |
| FR-028 | models.py: states/enums/constraints/profile fields updated | P0 | backend | L337 |
| FR-029 | tui.py: completion/release guards and operator guidance updated | P0 | backend | L338 |
| FR-030 | Phase 0: design/policy lock and owner/date assignments | P0 | backend | L328 |
| FR-031 | Phase 1: deterministic contracts + evaluator + transition validator | P0 | backend | L329 |
| FR-032 | Phase 2: runtime controls (lease/heartbeat/retry/recovery) | P0 | backend | L330 |
| FR-033 | Phase 3: sprint CLI + override governance + report persistence | P0 | backend | L331 |
| FR-034 | Phase 4: rollout execution + KPI gates + rollback drills | P0 | backend | L332 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source Lines |
|----|-------------|----------|-----------|--------------|
| NFR-001 | Deterministic pass/fail: same input always produces same gate decision (replay stability) | reliability | 100% determinism for identical inputs | L11-L12, L170 |
| NFR-002 | Evidence completeness: every failed check must include at least one file path or file:line reference | reliability | Zero tolerance — any miss is a failure (M5) | L175-L182 |
| NFR-003 | Fail-safe defaults: unknown/missing deterministic inputs must resolve to `failed` | reliability | No unknown inputs may pass | L167-L173 |
| NFR-004 | Timeout/retry semantics must be concrete and deadlock-resistant | reliability | No deadlocks; retry must terminate deterministically | L144-L151 |
| NFR-005 | KPI thresholds provisional in shadow, normative only after calibration and sign-off | reliability | Two shadow windows of data before normative activation | L267-L279 |
| NFR-006 | Checklist sections 2,3,4,6,7 must fully pass; remaining sections pass or have non-critical tracked gaps | quality | All 5 critical sections at full pass | L384-L387 |
| NFR-007 | All blocking decisions must have owner, UTC deadline, and effective rollout phase before GO | governance | 0 unresolved blocking decisions at GO | L313-L319 |
| NFR-008 | Override approval metadata must be complete (approver identity, approval state, review due date); incomplete overrides are invalid and block completion | governance | Strict completeness enforcement | L299-L304 |
| NFR-009 | Drift summary must separate edited vs non-edited files | reliability | Explicit separation in every GateResult | L178-L180 |
| NFR-010 | KPI calibration: collect M1-M12 for two shadow windows before proposing thresholds | reliability | Two full windows required | L273-L278 |

---

## Domain Distribution

| Domain | Percentage | Basis |
|--------|-----------|-------|
| backend | 45% | State machine, evaluator, CLI, schema, API, data models, retry/timeout |
| security | 25% | Override governance, audit log, release prohibition, compliance |
| performance | 20% | KPI metrics, determinism, replay stability, latency/throughput considerations |
| documentation | 10% | Spec, changelog, release notes, checklist sections |

---

## Dependencies

| ID | Description | Type | Affected Requirements | Source Lines |
|----|-------------|------|----------------------|--------------|
| DEP-001 | Transition validator must exist before completion guard enforcement (Phase 1 before Phase 3) | internal | FR-031, FR-027, FR-033 | L328-L332 |
| DEP-002 | GateResult schema must be finalized before evaluator implementation | internal | FR-018, FR-031 | L186-L200 |
| DEP-003 | OverrideRecord schema finalized before override governance flow (Phase 1 before Phase 3) | internal | FR-019, FR-033 | L202-L211 |
| DEP-004 | Shadow phase KPI data (2 windows) required before proposing normative thresholds | internal | NFR-005, FR-023, FR-024 | L273-L279 |
| DEP-005 | Rollback drill (M10) must pass before Soft→Full promotion | internal | FR-024, FR-025 | L247-L249 |
| DEP-006 | Profile thresholds and severity behavior must be locked (owner+deadline) before Phase 1 implementation | internal | FR-030, FR-004 | L382-L388 |
| DEP-007 | Sprint CLI (models.py, tui.py) depends on deterministic transition validator from Phase 1 | internal | FR-027, FR-028, FR-029, FR-031 | L337-L342 |
| DEP-008 | Event schema (GateTransitionEvent, GateCheckEvent) must be finalized before Phase 2 runtime controls | internal | FR-020, FR-032 | L213-L225 |
| DEP-009 | All 4 blocking decisions must be closed (owner+deadline) before any GO | internal | FR-030, NFR-007 | L400-L416 |

---

## Success Criteria

| ID | Description | Derived From | Measurable | Source Lines |
|----|-------------|-------------|-----------|--------------|
| SC-001 | Phase 0: all blocking decisions closed with owner+UTC deadline+effective phase | FR-030, NFR-007 | Yes | L350 |
| SC-002 | Phase 1: deterministic replay stability for identical inputs (100%) | FR-031, NFR-001 | Yes | L351 |
| SC-003 | Phase 1: fail-safe unknown handling produces `failed` for any unknown input | FR-031, NFR-003 | Yes | L351 |
| SC-004 | Phase 2: timeout/retry paths terminate deterministically, no deadlocks | FR-032, NFR-004 | Yes | L352 |
| SC-005 | Phase 3: transition blocking and override rules enforced per scope | FR-033, FR-027 | Yes | L353 |
| SC-006 | Phase 4: phase gates pass KPI criteria + rollback drill success | FR-034, FR-024, FR-025 | Yes | L354 |
| SC-007 | Shadow→Soft: M1, M4, M5, M7, M9 all pass | FR-023 | Yes | L246-L248 |
| SC-008 | Soft→Full: M1-M12 for two consecutive windows + M10 pass | FR-024 | Yes | L247-L249 |
| SC-009 | Evidence completeness: every failed gate check has at least one file path or file:line reference | NFR-002 | Yes | L175-L182 |
| SC-010 | Checklist sections 2,3,4,6,7 fully pass at GO | NFR-006 | Yes | L384-L387 |
| SC-011 | Release override path cannot be triggered under any conditions | FR-013, FR-006 | Yes | L122-L124 |
| SC-012 | `--strictness` alias rejected at full enforcement phase | FR-009 | Yes | L92-L94 |

---

## Risks

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|-------------|-------------|--------|----------------------|--------|
| RISK-001 | Profile thresholds unresolved → system ships with unpredictable gate behavior | High | High | FR-004, FR-017 | L400-L405 |
| RISK-002 | Retry/backoff/timeout values unfinalized → deadlock or stale-running incidents | High | High | NFR-004, FR-015, FR-016 | L401 |
| RISK-003 | Rollback triggers not finalized → inability to safely regress phase | High | High | FR-025, FR-026 | L402 |
| RISK-004 | Open blocking decisions unassigned → NO-GO at release gate | High | High | NFR-007, FR-030 | L403-L404 |
| RISK-005 | Release override path discovered (state machine bug) → compliance breach | Low | Critical | FR-013, FR-014 | L392-L398 |
| RISK-006 | Determinism breach (M4) in shadow data reveals non-deterministic evaluator | Medium | High | NFR-001, SC-002 | L252, L394 |
| RISK-007 | Evidence completeness (M5) failure blocks entire phase gate progression | Medium | High | NFR-002, SC-009 | L253, L283-L286 |
| RISK-008 | Sprint CLI (models.py, tui.py) integration complexity causes regressions | Medium | Medium | FR-027, FR-028, FR-029 | L337-L342 |
| RISK-009 | Circular/ambiguous state machine implementation deviating from normative table | Medium | High | FR-010, FR-011, FR-012 | inferred |
| RISK-010 | Legacy `--strictness` alias not removed at full enforcement | Low | Medium | FR-009, FR-017 | inferred |

---

## Complexity Scoring

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|---------|
| requirement_count | 44 | 0.88 | 0.25 | 0.220 |
| dependency_depth | 5 (chain: DEP-009→FR-030→DEP-006→FR-031→DEP-001→FR-027) | 0.625 | 0.25 | 0.156 |
| domain_spread | 3 domains ≥10% | 0.60 | 0.20 | 0.120 |
| risk_severity | weighted avg 2.22 → norm 0.611 | 0.611 | 0.15 | 0.092 |
| scope_size | 441 lines | 0.441 | 0.15 | 0.066 |
| **Total** | | | | **0.654 (MEDIUM)** |

**Classification**: MEDIUM (0.4–0.7) → 5-7 milestones, 1:2 interleave ratio
**Primary Persona**: architect (confidence 0.410) — multi-domain generalist optimal for cross-domain system work
**Consulting Personas**: backend (0.378), security (0.193)
