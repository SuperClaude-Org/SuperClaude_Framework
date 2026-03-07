---
spec_source: .dev/releases/current/unified-audit-gating-v1.2.1/unified-spec-v1.0.md
generated: 2026-03-06T12:00:00Z
generator: sc:roadmap
functional_requirements: 28
nonfunctional_requirements: 8
total_requirements: 36
domains_detected: [backend, performance, frontend]
complexity_score: 0.650
complexity_class: MEDIUM
risks_identified: 16
dependencies_identified: 10
success_criteria_count: 7
extraction_mode: "chunked (4 chunks)"
pipeline_diagnostics:
  prereq_checks:
    spec_validated: true
    output_collision_resolved: false
    adversarial_skill_present: na
    tier1_templates_found: 0
  fallback_activated: false
---

# Extraction: Turn-Budget Reimbursement with Trailing Gate Enforcement

## Project Overview

**Title**: Turn-Budget Reimbursement with Trailing Gate Enforcement
**Version**: Unified Specification v1.0
**Summary**: A unified solution merging per-task subprocess spawning with TurnLedger economics (Solution A) and trailing gate enforcement with deferred remediation (Solution B) to eliminate silent incompletion in the sprint runner. Panel-reviewed by Fowler, Nygard, Newman, Wiegers, Crispin, and Hohpe with 7 gaps addressed and 3 overlaps resolved.

---

## Functional Requirements

| ID | Description | Domain | Priority | Source |
|----|-------------|--------|----------|--------|
| FR-001 | TurnLedger dataclass: per-sprint budget with debit/credit/reimbursement economics, 90% reimbursement rate, minimum_allocation and minimum_remediation_budget guards | backend | P0 | L160-200, §3.1 |
| FR-002 | error_max_turns NDJSON detection: regex on last NDJSON line to distinguish normal completion from budget exhaustion | backend | P0 | L329-338, §4.4 |
| FR-003 | Reclassify PASS_NO_REPORT + error_max_turns as INCOMPLETE status instead of success | backend | P0 | L953-954, §11 Phase 1 |
| FR-004 | Per-task subprocess spawning: one Claude Code subprocess per task with runner-owned sequencing, context injection, and result aggregation | backend | P0 | L266-284, §4.1 |
| FR-005 | 4-layer subprocess isolation: scoped working directory, git boundary, empty plugin directory, restricted settings | backend | P0 | L288-297, §4.2 |
| FR-006 | Context injection: deterministic summary of prior task results (including gate outcomes and remediation history) injected into each task prompt | backend | P1 | L300-327, §4.3 |
| FR-007 | Runner as source of truth: runner owns task inventory parsed from tasklist file, tracks launches/completions/gates/budget | backend | P0 | L340-363, §4.5 |
| FR-008 | TrailingGateRunner: async gate evaluation via daemon threads with synchronization point (wait_for_pending) | backend | P1 | L396-500, §5.2 |
| FR-009 | GateResultQueue: thread-safe queue for trailing gate results using stdlib queue.Queue | backend | P1 | L426-437, §5.2 |
| FR-010 | DeferredRemediationLog: tracks deferred gate failures and remediation state, serializable for --resume support | backend | P1 | L439-454, §5.2 |
| FR-011 | Scope-based gate strategy: Release=BLOCKING (always), Milestone=configurable (blocking default), Task=TRAILING (grace_period=1 default) | backend | P0 | L503-514, §5.3 |
| FR-012 | Unified retry + remediation model: gate FAIL → budget check → remediation subprocess → retry on fail → halt + diagnostic on persistent failure | backend | P1 | L549-580, §6.1 |
| FR-013 | Reimbursement rules: 90% credit on gate PASS, remediation-only credit on remediation PASS, zero credit on persistent failure | backend | P1 | L582-589, §6.2 |
| FR-014 | TrailingGatePolicy protocol: consumer-owned hooks for remediation prompt construction and changed-file detection | backend | P1 | L593-619, §6.3 |
| FR-015 | Conflict review: file-level overlap detection between remediation changes and intervening work, with re-gate logic | backend | P1 | L623-673, §7 |
| FR-016 | Diagnostic chain: troubleshoot → adversarial(root causes) → adversarial(solutions) → summary. Runner-side sub-agents, best-effort | backend | P1 | L677-756, §8 |
| FR-017 | Resume semantics: actionable resume command with task ID, remaining tasks, diagnostic output, and budget suggestion | backend | P1 | L758-787, §8.4 |
| FR-018 | Task-level result (TaskResult): runner-constructed dataclass combining execution data, gate outcome, and reimbursement decision | backend | P1 | L791-813, §9.1 |
| FR-019 | Phase-level report aggregation: runner constructs phase reports from task results, no agent self-reporting dependency | backend | P1 | L815-838, §9.2 |
| FR-020 | TUI gate column: inline gate status column in phase table with 7 visual states (GateDisplayState) | frontend | P2 | L840-866, §9.3 |
| FR-021 | GateMode enum (BLOCKING/TRAILING) with backward-compatible BLOCKING default on Step dataclass | backend | P0 | L887-901, §10.2 |
| FR-022 | Executor branching: trailing vs blocking gate path based on GateMode + grace_period configuration | backend | P1 | L912-941, §10.4 |
| FR-023 | Pre-remediation budget check: ledger.can_remediate() before spawning remediation; halt with budget-specific message if insufficient (Gap 1) | backend | P0 | L238-255, §3.5 |
| FR-024 | Diagnostic chain budget boundary: chain runs runner-side, does NOT consume TurnLedger turns; fires regardless of ledger state (Gap 2) | backend | P0 | L258-261, §3.6 |
| FR-025 | Tasklist parser: markdown → task inventory with task IDs, dependency annotations, malformed input handling | backend | P1 | L966, §11 Phase 2 |
| FR-026 | Turn counting + reimbursement wiring: count actual turns from subprocess output, wire to TurnLedger debit/credit | backend | P1 | L973, §11 Phase 2 |
| FR-027 | GateDisplayState enum: 7 visual states for TUI gate column rendering (NONE, CHECKING, PASS, FAIL_DEFERRED, REMEDIATING, REMEDIATED, HALT) | frontend | P2 | L855-863, §9.3 |
| FR-028 | Remediation retry with TurnLedger integration: retry once on remediation failure, both attempts' turns permanently lost on persistent failure | backend | P1 | L996, §11 Phase 3 |

---

## Non-Functional Requirements

| ID | Description | Category | Constraint | Source |
|----|-------------|----------|------------|--------|
| NFR-001 | Thread safety via queue.Queue for gate result communication between daemon threads and main thread | reliability | stdlib queue.Queue inherent thread safety | L519-544, §5.4 |
| NFR-002 | No sprint/roadmap imports in trailing_gate.py module — layer isolation | maintainability | Zero cross-layer imports | L399, §5.2 |
| NFR-003 | Gate evaluation performance: complete within 50ms for output files up to 100KB | performance | <50ms evaluation time | L400, L1287-1294, Gap 7 |
| NFR-004 | Backward compatibility: grace_period=0 produces identical behavior to v1.2.1, zero daemon threads, all existing tests pass | reliability | Behavioral equivalence | L52, L873-881, §10.1 |
| NFR-005 | No deadlock possible: gate daemon threads never acquire locks or wait on main thread | reliability | Zero deadlock conditions | L539-544, §5.4.3 |
| NFR-006 | Daemon threads are daemon=True — abandoned on pipeline exit, no cleanup required | reliability | Thread lifecycle safety | L544, §5.4.3 |
| NFR-007 | Budget monotonicity: available() is non-increasing over time (credits never exceed debits due to 90% rate) | reliability | Mathematical invariant | L1284, §14.4 |
| NFR-008 | Mathematical impossibility of infinite run — 90% reimbursement rate creates natural budget decay | reliability | Net cost per task > 0 | L227-235, §3.4 |

---

## Domain Distribution

| Domain | Percentage | Primary Keywords | Requirement Count |
|--------|-----------|-----------------|-------------------|
| backend | 65% | subprocess, queue, daemon, model, handler, middleware, service, thread | 26 |
| performance | 20% | async, parallel, budget, reimbursement, optimization, latency | 5 |
| frontend | 10% | TUI, display, column, rendering, visual state | 3 |
| security | 3% | (no significant presence) | 1 |
| documentation | 2% | (no significant presence) | 1 |

---

## Dependencies

| ID | Description | Type | Affected Requirements |
|----|-------------|------|----------------------|
| DEP-001 | Per-task subprocess (FR-004) requires 4-layer isolation (FR-005) for viable cold-start cost | internal | FR-004, FR-005 |
| DEP-002 | Trailing gates (FR-008) require per-task subprocess (FR-004) — gates evaluate static output from terminated subprocesses | internal | FR-008, FR-004 |
| DEP-003 | Remediation model (FR-012) requires trailing gates (FR-008) + TurnLedger (FR-001) for budget-aware retry | internal | FR-012, FR-008, FR-001 |
| DEP-004 | Diagnostic chain (FR-016) triggers on persistent remediation failure (FR-012) | internal | FR-016, FR-012 |
| DEP-005 | Conflict review (FR-015) activates after remediation (FR-012) to detect file overlaps | internal | FR-015, FR-012 |
| DEP-006 | Context injection (FR-006) requires per-task subprocess (FR-004) architecture | internal | FR-006, FR-004 |
| DEP-007 | TUI gate column (FR-020) requires trailing gate infrastructure (FR-008) for state data | internal | FR-020, FR-008 |
| DEP-008 | Phase-level reports (FR-019) aggregate from task-level results (FR-018) | internal | FR-019, FR-018 |
| DEP-009 | Resume semantics (FR-017) include diagnostic chain output (FR-016) | internal | FR-017, FR-016 |
| DEP-010 | error_max_turns detection (FR-002) extends existing OutputMonitor module | external | FR-002 |

---

## Success Criteria

| ID | Description | Derived From | Measurable |
|----|-------------|-------------|------------|
| SC-001 | No silent incompletion: runner detects when budget is exhausted and reports INCOMPLETE, not PASS | FR-001, FR-002, FR-003 | Yes — test with budget-exhaustion scenario |
| SC-002 | Every task gets its own budget allocation — no task starvation because another consumed too many turns | FR-004, FR-007 | Yes — verify all tasks in a 46-task sprint get launched |
| SC-003 | Every task output passes gate before runner considers it complete | FR-008, FR-011 | Yes — gate evaluation recorded per task |
| SC-004 | Budget is mathematically bounded — no infinite loops possible with 90% reimbursement | FR-001, FR-013, NFR-008 | Yes — net_cost_per_task > 0 provable |
| SC-005 | grace_period=0 produces identical behavior to v1.2.1 — zero daemon threads, all existing tests pass | FR-021, NFR-004 | Yes — behavioral comparison test |
| SC-006 | Full-flow integration test passes all 4 scenarios (pass, fail-remediate-pass, fail-halt, low-budget-halt) | FR-012, FR-023 | Yes — 4-scenario integration test (Gap 6) |
| SC-007 | Gate evaluation completes within 50ms for 100KB output files | NFR-003 | Yes — timed benchmark test |

---

## Risk Register

| ID | Description | Probability | Impact | Affected Requirements | Source |
|----|-------------|-------------|--------|----------------------|--------|
| RISK-001 | Context fragmentation: task N+1 doesn't know what task N did | High | Medium | FR-006 | L1169, §13.1 |
| RISK-002 | Subprocess cold-start overhead: ~92 turns for 46 tasks (2 turns each) | Certain | Medium | FR-004, FR-005 | L1170, §13.1 |
| RISK-003 | Loss of inter-task optimization: redundant file reads across tasks | Medium | Low | FR-004 | L1171, §13.1 |
| RISK-004 | More total turns consumed: ~138 turns overhead vs ~12 for per-phase model | Certain | Medium | FR-001, FR-004 | L1172, §13.1 |
| RISK-005 | Complex orchestration: ~1,740 lines of new code across 10+ components | Medium | Medium | All | L1173, §13.1 |
| RISK-006 | API rate limiting: 46+ subprocess spawns may hit rate limits | Low | Low | FR-004 | L1174, §13.1 |
| RISK-007 | Gate daemon thread crashes: undetected gate failure | Low | Medium | FR-008, FR-009 | L1175, §13.1 |
| RISK-008 | Remediation breaks subsequent work: cascading failures | Low | High | FR-012, FR-015 | L1176, §13.1 |
| RISK-009 | Queue corruption under load: results lost from GateResultQueue | Low | Medium | FR-009, NFR-001 | L1177, §13.1 |
| RISK-010 | Low budget + gate failure compound: wasted turns on doomed remediation | Medium | High | FR-023, FR-001 | L1183, Gap 1 |
| RISK-011 | Diagnostic chain confused by budget problem: wrong root cause analysis | Low | Medium | FR-024, FR-016 | L1184, Gap 2 |
| RISK-012 | Isolation boundary confusion: implementer creates daemon inside subprocess | Low | Medium | FR-005, FR-008 | L1185, Gap 3 |
| RISK-013 | Missing gate/remediation context: task N+1 unaware of prior gate failures | Medium | High | FR-006 | L1186, Gap 4 |
| RISK-014 | Unusable resume after diagnostic: user can't act on HALT output | Medium | Medium | FR-017 | L1187, Gap 5 |
| RISK-015 | No full-flow integration test: compound scenarios untested | Medium | High | FR-012 | L1188, Gap 6 |
| RISK-016 | Gate evaluation too slow on large output: sync point blocks pipeline | Low | Medium | NFR-003, FR-008 | L1189, Gap 7 |

---

## Complexity Assessment

| Factor | Raw Value | Normalized | Weight | Weighted |
|--------|-----------|-----------|--------|----------|
| requirement_count | 36 (28 FR + 8 NFR) | 0.72 | 0.25 | 0.180 |
| dependency_depth | 4 (FR-001→FR-012→FR-016→FR-017) | 0.50 | 0.25 | 0.125 |
| domain_spread | 3 domains ≥10% (backend, performance, frontend) | 0.60 | 0.20 | 0.120 |
| risk_severity | 2.0 weighted average (4H + 8M + 4L) | 0.50 | 0.15 | 0.075 |
| scope_size | 1,343 lines | 1.00 | 0.15 | 0.150 |

**Complexity Score**: 0.650 — **MEDIUM** (0.4 ≤ 0.650 ≤ 0.7)

**Implications**: 5-7 milestones, 1:2 interleave ratio (one validation per two work milestones)

---

## Persona Assignment

| Role | Persona | Confidence | Rationale |
|------|---------|------------|-----------|
| Primary | backend | 0.546 | Dominant domain at 65% — subprocess model, data models, threading |
| Consulting | architect | 0.455 | System-wide design decisions, dependency management |
| Consulting | performance | 0.154 | Budget optimization, async evaluation, gate latency |

---

## Chunked Extraction Metadata

| Chunk | Sections | Line Range | FRs | NFRs | Deps | SCs | Risks |
|-------|----------|-----------|-----|------|------|-----|-------|
| 1 | §1-§4 (Problem + Architecture + TurnLedger + Subprocess) | L1-L364 | 7 | 0 | 2 | 2 | 0 |
| 2 | §5-§9 (Gates + Retry + Conflict + Diagnostic + Reporting) | L367-L866 | 15 | 6 | 6 | 3 | 0 |
| 3 | §10-§13 (Compat + Roadmap + Traceability + Risks) | L870-L1202 | 6 | 2 | 2 | 2 | 16 |
| 4 | §14 + Appendices (Test Strategy + Worked Examples) | L1206-L1343 | 0 | 0 | 0 | 0 | 0 |

**Deduplication**: 0 exact matches, 0 ID collisions, 0 review-needed pairs.
**Verification**: Pass 1 (Source Coverage): 98% WARN — appendix examples not extracted. Pass 2 (Anti-Hallucination): 100% PASS. Pass 3 (Section Coverage): 100% PASS. Pass 4 (Count Reconciliation): exact match PASS.
