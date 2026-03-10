# Roadmap: Unified Audit Gating System v1.2.1 [Analyzer Variant]

Document date: 2026-03-03
Persona: analyzer — risk/reliability and rollout safety
Source specification: `docs/generated/unified-audit-gating-v1.2.1-release-spec.md`

## Overview
This roadmap is intentionally risk-first: all implementation work is blocked until the four current NO-GO blockers are resolved as explicit risks (RISK-001 through RISK-004), with accountable owners, deadlines, and signed decisions. That ordering reduces rework risk and prevents unsafe rollout assumptions (thresholds, timeout policy, rollback contracts) from being embedded into runtime behavior.

Rollout safety is treated as a product requirement, not an afterthought. The roadmap includes explicit phase-gate milestones for **Shadow→Soft** and **Soft→Full**, plus a mandatory rollback drill and safe-disable verification before full enforcement. This aligns to the release spec's phased rollout and rollback trigger requirements.

Implementation is sequenced to harden reliability before enforcement expansion: state-machine correctness and contract validation first, then runtime resilience (lease/heartbeat timeout handling, deadlock resistance, stale-state recovery, retry-budget exhaustion behavior), then governance and rollout gates with measurable evidence and rollback readiness.

## Milestone Summary
| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|---|---|---|---|---|---|---|---|
| M1 | Blocker Closure & Governance Lock (RISK-001..004) | Decision/Governance | P0 | M | None | Finalized policy values, rollback/safe-disable contract, owner+deadline matrix | High (front-loaded) |
| M2 | Contract & State-Transition Foundation | Build/Validation | P0 | M | M1 | GateResult/Override/Event schemas, transition validator, illegal-transition hard fails | Medium |
| M3 | Reliability Runtime Hardening | Reliability | P0 | L | M2 | Lease+heartbeat timeout handling, deadlock resistance, stale-state recovery, retry-budget exhaustion controls | High |
| M4 | Shadow Rollout + Calibration Evidence + Shadow→Soft Gate | Rollout Gate | P0 | M | M3 | Shadow metrics pipeline, two-window calibration, gate checklist | Medium |
| M5 | Soft Enforcement + Governance Enforcement + Rollback Drill | Rollout Gate | P0 | L | M4 | Selective enforcement, override validity blocking, rollback drill pass + safe-disable artifact retention | High |
| M6 | Full Enforcement Activation + Stabilization (Soft→Full Gate) | Rollout Gate | P0 | M | M5 | Full enforcement go-live, monitored SLO/KPI windows, auto-rollback triggers active | High |

## Dependency Graph
`M1 → M2 → M3 → M4 (Shadow→Soft checkpoint) → M5 (Rollback drill checkpoint) → M6 (Soft→Full checkpoint)`

---

## M1: Blocker Closure & Governance Lock (RISK-001..004)
### Objective
Resolve all four current NO-GO blockers before code path changes; lock policy and rollout safety decisions with accountable ownership.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D1.1 | **RISK-001**: Profile thresholds + major-severity behavior finalized | Signed decision doc: strict/standard/legacy_migration thresholds and major-severity task-tier behavior frozen |
| D1.2 | **RISK-002**: Retry/backoff/timeout values finalized | Per-scope retry budgets, backoff policy, lease TTL, heartbeat interval/timeouts approved |
| D1.3 | **RISK-003**: Rollback/safe-disable triggers finalized | Trigger matrix finalized (M4 breach, M5 failure, M7 stale, M10 drill fail, validator bypass equivalents) + safe-disable semantics documented |
| D1.4 | **RISK-004**: Blocking decisions owner+deadline assigned | Named owners (policy/state-machine/reliability/migration/program) + dated commitments recorded |
| D1.5 | Release-governance baseline | Decision log and escalation path approved; unresolved blocker = explicit launch stop |

### Dependencies
None

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Decision deadlock across owners | Medium | High | Program manager arbitration SLA + escalation within 48h |
| Unverifiable policy values | Medium | High | Require measurable criteria per threshold; reject ambiguous entries |
| Rollback trigger ambiguity | Medium | Critical | Trigger truth-table and simulation walkthrough before sign-off |

---

## M2: Contract & State-Transition Foundation
### Objective
Implement immutable data/state contracts and validator enforcement to prevent illegal transitions and missing-evidence completion.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D2.1 | GateResult v1.2.1 model implementation | All required fields present (incl. failure_class, drift_summary, artifacts, timing); schema validation tests pass |
| D2.2 | OverrideRecord v1.2.1 model implementation | Incomplete metadata marked invalid and blocks completion; release override prohibited |
| D2.3 | GateTransitionEvent + GateCheckEvent implementation | Correlation IDs and causality chain validated in tests |
| D2.4 | Transition validator | Illegal transitions hard-fail (bypass, running→completed, failed→completed w/o override, release fail→released) |
| D2.5 | Failure-class contract enforcement | policy/transient/system/timeout/unknown mapped deterministically; unknown input => failed |

### Dependencies
M1

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Contract drift across modules | Medium | High | Central schema version guard + contract tests in CI |
| Transition loopholes | Low | Critical | Negative-path test suite for all illegal transitions |
| Override misuse at release scope | Low | Critical | Explicit release override deny rule + audit log alerts |

---

## M3: Reliability Runtime Hardening
### Objective
Deliver resilience controls needed for safe enforcement: deadlock resistance, stale-state recovery, timeout correctness, and retry-budget exhaustion handling.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D3.1 | Lease + heartbeat runtime | Missing heartbeat transitions to `audit_*_failed(timeout)` with deterministic timing tests |
| D3.2 | Deadlock resistance package | No cyclical waits between evaluator/transition paths in stress tests; watchdog breaks stalled runs |
| D3.3 | Stale-state recovery mechanism | Recovery job requeues eligible stale entities or fails safely with reasoned event trace |
| D3.4 | Retry-budget exhaustion controls | Per-scope retry exhaustion blocks completion/release and emits explicit failure class |
| D3.5 | Reliability fault-injection suite | Transient/system/timeout fault tests meet pass threshold before rollout milestones |

### Dependencies
M2

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Timeout false positives/negatives | Medium | High | Boundary-condition tests and clock-skew tolerance |
| Recovery creates duplicate gate runs | Low | High | Idempotent gate_run_id/correlation checks |
| Retry storms under transient failure | Medium | Critical | Backoff caps + global concurrency guard |

---

## M4: Shadow Rollout + Calibration Evidence + Shadow→Soft Gate
### Objective
Run non-blocking shadow safely, collect calibrated evidence, and approve the first enforcement gate only with objective readiness proof.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D4.1 | Shadow deployment (no hard blocking) | Production shadow active; completion/release not blocked |
| D4.2 | KPI and evidence pipeline | Score/threshold/check outcome metrics available by scope/profile |
| D4.3 | Two shadow windows calibration | Two consecutive windows complete; provisional thresholds calibrated and signed off |
| D4.4 | Shadow→Soft gate checklist | Gate checklist passed (M1 closure, reliability controls, stale-state monitoring, policy readiness, validator integrity) |
| D4.5 | Rollback trigger observability | Trigger telemetry and alerting active before Soft enablement |

### Dependencies
M3

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Shadow data quality insufficient | Medium | High | Data completeness SLO; block gate if below threshold |
| Calibration bias by profile mix | Low | High | Stratified analysis by scope/profile |
| Hidden stale-state accumulation | Low | Critical | Stale-state dashboard + alert thresholds |

---

## M5: Soft Enforcement + Governance Enforcement + Rollback Drill
### Objective
Enable selective enforcement with strict governance validity checks, then prove rollback/safe-disable in a controlled drill before full rollout.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D5.1 | Soft enforcement by scope/profile | Enforcement active for selected profiles/scopes with error budgets monitored |
| D5.2 | Override governance enforcement | Missing approver/approval_state/review_due_at blocks completion; task/milestone-only override path verified |
| D5.3 | Rollback drill (full→soft→shadow order) | Drill passes scripted triggers and order requirements without artifact loss |
| D5.4 | Safe-disable contract verification | Safe-disable preserves shadow artifacts and disables hard blocking deterministically |
| D5.5 | Soft stabilization windows | Two consecutive stable windows under Soft with no critical reliability breach |

### Dependencies
M4

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Enforcement causes operational disruption | Medium | Critical | Gradual scope enablement + immediate safe-disable hook |
| Governance metadata bypass attempts | Low | Critical | Validator hard-block + immutable event audit trail |
| Rollback drill incompleteness | Medium | Critical | Predefined pass/fail script and independent observer sign-off |

---

## M6: Full Enforcement Activation + Stabilization (Soft→Full Gate)
### Objective
Activate global enforcement only after all prior controls are proven; keep continuous rollback readiness and reliability monitoring post-cutover.

### Deliverables
| ID | Description | Acceptance Criteria |
|---|---|---|
| D6.1 | Soft→Full gate approval | All prerequisite controls validated, including rollback drill evidence and stable windows |
| D6.2 | Full enforcement activation | Global blocking enabled across task/milestone/release according to policy |
| D6.3 | Continuous reliability guardrails | Deadlock/stale/retry-exhaustion monitors and paging active with runbooks |
| D6.4 | Automated rollback trigger execution | Triggered rollback executes full→soft→shadow and confirms safe-disable artifacts retained |
| D6.5 | Post-launch reliability review | 30-day review with incident trends, threshold adjustments, and governance actions |

### Dependencies
M5

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Full rollout exposes latent edge case | Medium | Critical | Canary-like staged activation + auto-rollback |
| Alert fatigue hides true incidents | Medium | Medium | Severity tuning + SLO-linked paging |
| Policy drift post-go-live | Low | High | Change-control board + versioned policy registry |

---

## Risk Register
| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| RISK-001 | Profile thresholds and major-severity task-tier behavior not finalized | M1, M4, M5, M6 | High | Critical | Freeze policy matrix in M1 with measurable criteria; no rollout gate without sign-off | Policy Owner |
| RISK-002 | Retry/backoff/timeout values undefined causing unstable runtime behavior | M1, M3, M4, M5, M6 | High | Critical | Finalize runtime parameters in M1; validate via fault-injection in M3 | Reliability Owner |
| RISK-004 | Blocking decisions lack explicit owner/deadline accountability | M1, M4, M5, M6 | High | High | RACI + dated commitments as launch precondition | Program Manager |
| RISK-003 | Rollback/safe-disable triggers not finalized, risking unsafe rollout | M1, M5, M6 | High | Critical | Trigger truth-table + drill validation + automated rollback hooks | Migration Owner |
| RISK-005 | Deadlock under concurrent audits | M3, M5, M6 | Medium | Critical | Watchdog, lock ordering, stress/fault tests | State-Machine Owner |
| RISK-006 | Stale-state accumulation leads to false blocks or silent bypass | M3, M4, M6 | Medium | High | Recovery worker + stale thresholds + observability SLO | Reliability Owner |
| RISK-007 | Retry-budget exhaustion causes workflow paralysis in soft/full phases | M3, M5, M6 | Medium | High | Per-scope budget tuning + controlled backoff + ops runbook | Reliability Owner |
| RISK-008 | Override governance metadata incompleteness bypasses compliance intent | M2, M5, M6 | Low | Critical | Hard validation + immutable audit event chain | Policy Owner |

## Decision Summary
| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Rollout strategy | Shadow → Soft → Full with explicit checkpoints | Direct Full rollout; Shadow→Full | Minimizes blast radius and supports measurable confidence building |
| Override policy | Task/milestone override only; release override forbidden | Allow release override under emergency | Protects release integrity and reduces governance loopholes |
| Unknown/missing evidence handling | Fail-closed (failed/non-completable) | Fail-open with warning | Reliability/safety priority requires deterministic blocking on uncertainty |
| Reliability gating | Dedicated milestone before rollout gates (M3) | Parallel with Soft rollout | Prevents enforcing on unstable control plane |
| Rollback approach | Ordered rollback full→soft→shadow + safe-disable artifact retention | Single-step disable | Ordered degradation preserves observability and recovery data |

## Success Criteria
| ID | Criterion | Validates Milestone(s) | Measurable |
|---|---|---|---|
| SC-01 | All four blockers resolved with signed owner+deadline evidence | M1 | 4/4 blocker records approved; no open NO-GO blockers |
| SC-02 | State-machine validator blocks all illegal transitions | M2 | 100% pass on negative transition test suite |
| SC-03 | Reliability controls withstand injected timeout/transient/system failures | M3 | Fault-injection suite pass rate meets release threshold |
| SC-04 | Shadow calibration completed across two consecutive windows | M4 | 2/2 windows complete with data completeness and approved thresholds |
| SC-05 | Shadow→Soft checkpoint passed with checklist evidence | M4 | Gate checklist signed by required owners |
| SC-06 | Rollback drill and safe-disable contract pass under Soft | M5 | Drill pass + artifact retention verified + no critical defects |
| SC-07 | Soft→Full checkpoint approved only after stable windows and drill evidence | M6 | Formal go/no-go record with all prerequisites attached |
| SC-08 | Post-full rollout reliability objectives sustained | M6 | No unresolved critical incidents tied to deadlock/stale/retry exhaustion within review window |
