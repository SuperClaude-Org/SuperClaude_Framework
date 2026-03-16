---
deliverable: D-0026
task: T07.01
title: Index of 8 Component Improvement Plan Files
status: complete
generated: 2026-03-15
---

# D-0026: Component Improvement Plan Files — Index

## Summary

8 improve-*.md files produced, one per IC component group from D-0008. Each file contains improvement items ordered by structural leverage priority: gate integrity (P0) > evidence verification (P1) > restartability/traceability (P2) > bounded complexity/schema reliability (P3).

---

## File Index

| # | Filename | Component Group | Verdict | Items | Priority Range |
|---|---|---|---|---|---|
| 1 | `improve-roadmap-pipeline.md` | Roadmap Pipeline | split by context | 4 | P0–P2 |
| 2 | `improve-cleanup-audit.md` | Cleanup-Audit CLI | IC stronger | 4 | P0–P1 |
| 3 | `improve-sprint-executor.md` | Sprint Executor | IC stronger | 5 | P0–P2 |
| 4 | `improve-pm-agent.md` | PM Agent | split by context | 4 | P0–P2 |
| 5 | `improve-adversarial-pipeline.md` | Adversarial Pipeline | IC stronger | 3 | P0–P1 |
| 6 | `improve-task-unified-tier.md` | Task-Unified Tier System | IC stronger | 4 | P0–P2 |
| 7 | `improve-quality-agents.md` | Quality Agents | split by context | 3 | P0–P2 |
| 8 | `improve-pipeline-analysis.md` | Pipeline Analysis Subsystem | IC stronger | 4 | P0–P2 |

---

## Structural Leverage Priority Ordering

All 8 files apply the same priority ordering:
1. **Gate integrity** (P0): fail-closed semantics, CRITICAL FAIL conditions, executor validation gates
2. **Evidence verification** (P1): presumption of falsehood, mandatory negative evidence documentation, CEV vocabulary, typed state transitions
3. **Restartability/traceability** (P2): per-item UID tracking, three-mode execution, sub-phase resume, auto-trigger diagnostics, typed handoff states
4. **Bounded complexity / schema reliability** (P3): resource caps, model tier proportionality policy, documented fallback degradation

---

## LW-Pattern Adoption Summary

All items with LW-pattern adoptions include `patterns_not_mass: true` and a "Why not full import" sentence.

| Item ID | patterns_not_mass | Adopted Pattern | Rejected Mass |
|---|---|---|---|
| RP-001 | true | LW fail-closed verdict logic | LW bash gate mechanism |
| RP-002 | true | LW fallback documentation pattern | LW dual-mode event-driven/phased-parallel arch |
| RP-003 | true | LW per-track state formalism | LW CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS |
| RP-004 | true | LW track-cap principle | LW Rigorflow runtime scheduler |
| CA-001 | true | LW Presumption of Falsehood stance | LW per-claim evidence tables + FAS -100 penalty |
| CA-002 | true | LW mandatory negative evidence | LW PABLOV chain |
| CA-003 | true | LW typed inter-agent communication | LW bash IPC |
| CA-004 | true | LW executor validation gate | LW permissionMode:bypassPermissions |
| SE-001 | true | LW fail-closed verdict logic | LW bash batch state machine |
| SE-002 | true | LW per-item UID tracking | LW 6000-line bash batch state machine |
| SE-003 | true | LW three-mode prompt selection | LW bash prompt template system |
| SE-004 | true | LW auto-trigger diagnostic pattern | LW bash monitoring infrastructure |
| SE-005 | true | LW Sev 1/2/3 severity taxonomy | LW point-based scoring system |
| PM-001 | true | LW claim/proof distinction | LW full five-artifact PABLOV chain |
| PM-002 | true | LW mandatory negative evidence | LW all-output-types per-claim tables |
| PM-003 | true | LW model tier proportionality principle | LW all-opus mandate |
| PM-004 | true | LW Presumption of Falsehood stance | LW mandatory sequential PABLOV chain |
| AP-001 | true | LW 12-category sycophancy risk taxonomy | LW static weight system without adaptive learning |
| AP-002 | n/a | IC-native CEV extension (not LW adoption) | — |
| AP-003 | true | LW 4-category failure taxonomy | LW point-based scoring with confidence tiers |
| TU-001 | true | audit-validator CRITICAL FAIL pattern | LW behavioral-only quality gate application |
| TU-002 | true | LW output-type-specific gate tables concept | LW manual quality gate application |
| TU-003 | true | LW six quality principles vocabulary | LW quality gate menu with manual operator selection |
| TU-004 | n/a | IC-native gate blocking improvement | — |
| QA-001 | true | LW executor validation gate pattern | LW permissionMode:bypassPermissions |
| QA-002 | true | LW typed message protocol concept | LW bash IPC + all-opus model mandate |
| QA-003 | n/a | IC-native policy formalization (anti-regression) | — |
| PA-001 | true | LW pre-packaged artifact collection | LW bash artifact collection scripts |
| PA-002 | true | LW framework-vs-project distinction | LW grep-based bash failure classification |
| PA-003 | true | LW 4-category failure taxonomy | LW point-based scoring system |
| PA-004 | true | LW resource cap principle | LW runtime dynamic load balancer |

---

## Acceptance Criteria Verification

| Criterion | Required | Actual | Status |
|---|---|---|---|
| 8 improve-*.md files exist in artifacts/ | 8 | 8 | PASS |
| Each file has P-tier fields | Yes | All 31 items have explicit P0/P1/P2 | PASS |
| Each file has effort fields | Yes | All 31 items have XS/S/M | PASS |
| Each file has file paths | Yes | All 31 items reference specific files | PASS |
| Each LW-adoption item has patterns_not_mass: true | Yes | 27 LW-adoption items, all marked | PASS |
| Each LW-adoption item has "why not full import" sentence | Yes | All 27 have explicit why-not sentence | PASS |
| Priority ordering: P0 before P1 before P2 in each file | Yes | All 8 files verified | PASS |
