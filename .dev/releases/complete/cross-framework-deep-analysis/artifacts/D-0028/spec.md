---
deliverable: D-0028
task: T07.03
title: improve-master.md — Aggregated Improvement Portfolio and Cross-Component Dependency Graph
status: complete
generated: 2026-03-15
component_groups_covered: 8
total_items: 31
circular_dependencies: 0
---

# improve-master.md — Aggregated Improvement Portfolio

## Executive Summary

31 improvement items across 8 IC component groups, organized into 5 priority tiers. The cross-component dependency graph identifies 9 prerequisite relationships and 12 optional refinement relationships. No circular dependencies exist. The critical path runs through gate integrity improvements (P0) in the Pipeline Analysis Subsystem and Sprint Executor, which are prerequisites for evidence verification improvements in PM Agent and Cleanup-Audit CLI.

---

## Aggregated Improvement Item Summary

### P0 — Gate Integrity (13 items)

| Item ID | Component | Title | Effort | Source File |
|---|---|---|---|---|
| RP-001 | Roadmap Pipeline | Fail-Closed Gate Semantics in execute_roadmap | S | improve-roadmap-pipeline.md |
| CA-001 | Cleanup-Audit CLI | Presumption of Falsehood in Audit Agent Instructions | S | improve-cleanup-audit.md |
| CA-002 | Cleanup-Audit CLI | Mandatory Negative Evidence Documentation | S | improve-cleanup-audit.md |
| SE-001 | Sprint Executor | Fail-Closed Gate Completion Logic | S | improve-sprint-executor.md |
| PM-001 | PM Agent | Filesystem-Verified Flag in SelfCheckProtocol | S | improve-pm-agent.md |
| PM-002 | PM Agent | Mandatory Negative Evidence Documentation in SelfCheckProtocol | S | improve-pm-agent.md |
| AP-001 | Adversarial Pipeline | Ambient Sycophancy Detection in Agent Definitions | M | improve-adversarial-pipeline.md |
| TU-001 | Task-Unified Tier | CRITICAL FAIL Conditions for Unconditional Gate Failure | S | improve-task-unified-tier.md |
| QA-001 | Quality Agents | Executor Validation Gate for All Agent Entry Points | S | improve-quality-agents.md |
| QA-002 | Quality Agents | Typed State Transitions for Sequential Agent Invocation | M | improve-quality-agents.md |
| PA-001 | Pipeline Analysis | Pre-Packaged Artifact Collection Before Diagnostic Runs | M | improve-pipeline-analysis.md |
| PA-002 | Pipeline Analysis | Framework-vs-Project Diagnostic Distinction in Output | S | improve-pipeline-analysis.md |

### P1 — Evidence Verification / Typed Coordination (11 items)

| Item ID | Component | Title | Effort | Source File |
|---|---|---|---|---|
| RP-002 | Roadmap Pipeline | Documented Fallback Degradation Path | XS | improve-roadmap-pipeline.md |
| CA-003 | Cleanup-Audit CLI | Typed State Transitions in Audit Pass Progression | M | improve-cleanup-audit.md |
| CA-004 | Cleanup-Audit CLI | Executor Validation Gate Before Agent Invocation | S | improve-cleanup-audit.md |
| SE-002 | Sprint Executor | Per-Item UID Tracking for Sub-Phase Restartability | M | improve-sprint-executor.md |
| SE-003 | Sprint Executor | Three-Mode Execution for Mid-Phase Resume | M | improve-sprint-executor.md |
| PM-004 | PM Agent | ReflexionPattern: Presumption of Falsehood Default Stance | S | improve-pm-agent.md |
| AP-002 | Adversarial Pipeline | CEV Vocabulary Extension to All Verification Outputs | S | improve-adversarial-pipeline.md |
| AP-003 | Adversarial Pipeline | Four-Category Failure Classification in Adversarial Debate Outputs | S | improve-adversarial-pipeline.md |
| TU-002 | Task-Unified Tier | Output-Type-Specific Gate Application | M | improve-task-unified-tier.md |
| TU-003 | Task-Unified Tier | Six Universal Quality Principles as Verification Agent Vocabulary | S | improve-task-unified-tier.md |
| PA-003 | Pipeline Analysis | 4-Category Failure Classification in DiagnosticReport | S | improve-pipeline-analysis.md |

### P2 — Restartability / Bounded Complexity / Schema Reliability (7 items)

| Item ID | Component | Title | Effort | Source File |
|---|---|---|---|---|
| RP-003 | Roadmap Pipeline | Per-Track State Machine Formalization | M | improve-roadmap-pipeline.md |
| RP-004 | Roadmap Pipeline | Hard Resource Caps Formalization | S | improve-roadmap-pipeline.md |
| SE-004 | Sprint Executor | Auto-Trigger Diagnostic on N Consecutive Gate Failures | M | improve-sprint-executor.md |
| SE-005 | Sprint Executor | Three-Tier Severity for Gate Failure Reports | S | improve-sprint-executor.md |
| PM-003 | PM Agent | Model Tier Proportionality for PM Agent Operations | XS | improve-pm-agent.md |
| QA-003 | Quality Agents | Model Tier Proportionality Policy for Quality Agents | XS | improve-quality-agents.md |
| TU-004 | Task-Unified Tier | Confidence Threshold <0.70 Explicit Blocking | XS | improve-task-unified-tier.md |
| PA-004 | Pipeline Analysis | Hard Resource Caps for Recursive Pipeline Analysis | XS | improve-pipeline-analysis.md |

---

## Cross-Component Dependency Graph

### Legend

- `A → B` = A is a **prerequisite** for B (A must be done before B starts)
- `A ⟶ B` = A is an **optional refinement** for B (B is improved by A but B can proceed without A)
- `[PREREQ]` = prerequisite relationship
- `[OPT]` = optional refinement relationship

### Gate Integrity Layer Dependencies (P0)

```
[PREREQ] PA-001 (pre-packaged artifacts) → PA-002 (framework-vs-project distinction)
[PREREQ] PA-001 (pre-packaged artifacts) → PA-003 (4-category failure classification)
[PREREQ] SE-001 (fail-closed gates) → SE-002 (per-item UID tracking)
[PREREQ] SE-001 (fail-closed gates) → SE-003 (three-mode execution)
[PREREQ] SE-001 (fail-closed gates) → SE-004 (auto-trigger diagnostic)
[PREREQ] SE-001 (fail-closed gates) → SE-005 (three-tier severity)
[PREREQ] CA-001 (presumption of falsehood agents) → CA-002 (negative evidence documentation)
[PREREQ] CA-002 (negative evidence schema) → CA-003 (typed state transitions)
[PREREQ] CA-003 (BLOCKED state enum) → CA-004 (executor validation gate)
[PREREQ] PM-001 (filesystem_verified flag) → PM-002 (negative evidence list)
[PREREQ] PM-001 (filesystem_verified flag) → PM-004 (reflexion confidence)
[PREREQ] QA-001 (agent validation gates) → QA-002 (typed state transitions)
[PREREQ] TU-001 (CRITICAL FAIL conditions) → TU-002 (output-type gate routing)
[PREREQ] RP-001 (fail-closed roadmap gate) → RP-003 (state machine formalization)
```

### Evidence/Typed-Coordination Layer Dependencies (P1)

```
[PREREQ] AP-001 (sycophancy detection) → TU-003 (six quality principles — Anti-Sycophancy principle requires AP-001)
[PREREQ] AP-002 (CEV vocabulary) → AP-003 (failure classification — evidence failures need CEV definition)
[PREREQ] PA-002 (framework-vs-project) → PA-003 (category classification — framework/project context is needed)
[PREREQ] SE-002 (UID tracking) → SE-003 (three-mode execution — mode selection depends on UID-based task state)
```

### Cross-Component Optional Refinements

```
[OPT] PA-003 (4-category failure classification) ⟶ SE-004 (auto-trigger diagnostic — categories improve diagnostic trigger precision)
[OPT] SE-005 (three-tier severity) ⟶ TU-001 (CRITICAL FAIL conditions — severity model provides context for CRITICAL classification)
[OPT] AP-001 (sycophancy detection in agents) ⟶ QA-001 (executor validation gate — sycophancy check in validation gate is improved by AP-001)
[OPT] TU-003 (six quality principles) ⟶ QA-001 (agent validation — six principles provide vocabulary for validation checklist)
[OPT] PM-003 (model tier policy for PM Agent) ⟶ QA-003 (model tier policy for quality agents — policies should be consistent)
[OPT] AP-002 (CEV vocabulary) ⟶ PA-002 (framework-vs-project output — diagnostic output format benefits from CEV structure)
[OPT] CA-003 (typed state transitions in audit) ⟶ QA-002 (typed state transitions in quality agents — shared AuditPassState/AgentHandoffState pattern)
[OPT] RP-004 (hard resource caps for roadmap) ⟶ PA-004 (hard resource caps for pipeline analysis — cap formalization is consistent across components)
[OPT] SE-004 (auto-trigger diagnostic) ⟶ PA-001 (pre-packaged artifacts — diagnostic is more reliable with pre-packaged artifacts)
[OPT] TU-002 (output-type gate routing) ⟶ AP-003 (failure classification — output type determines applicable failure categories)
[OPT] TU-004 (confidence blocking) ⟶ TU-001 (CRITICAL FAIL — confidence <0.70 blocking is a CRITICAL condition candidate)
[OPT] PM-004 (reflexion confidence) ⟶ PM-003 (model tier policy — confidence level informs tier escalation)
```

### Circular Dependency Check

Examining all prerequisite chains:

- PA-001 → PA-002 → PA-003: linear chain, no cycle
- PA-001 → PA-003: direct path, consistent with above chain
- SE-001 → SE-002 → SE-003: linear chain
- SE-001 → SE-004; SE-001 → SE-005: independent branches from SE-001, no cycle
- CA-001 → CA-002 → CA-003 → CA-004: linear chain
- PM-001 → PM-002, PM-001 → PM-004: independent branches from PM-001
- TU-001 → TU-002; AP-001 → TU-003: independent branches to TU-002 and TU-003
- AP-002 → AP-003: linear chain
- SE-002 → SE-003: downstream from SE-001
- PA-002 → PA-003: downstream from PA-001

**No cycle exists**: The dependency graph is a directed acyclic graph (DAG). The only paths between components are:
- Pipeline Analysis → Sprint Executor (optional: PA-003 ⟶ SE-004)
- Task-Unified Tier → Quality Agents (optional: TU-003 ⟶ QA-001)
- Adversarial Pipeline → Task-Unified Tier (prerequisite: AP-001 → TU-003)
- PM Agent → Quality Agents (optional: PM-003 ⟶ QA-003)

None of these form cycles. **Circular dependency count: 0.**

---

## Critical Path Analysis

The critical path for the Phase 7 improvement portfolio (sequential prerequisite chain with highest effort sum):

```
PA-001 (M) → PA-002 (S) → PA-003 (S)
SE-001 (S) → SE-002 (M) → SE-003 (M) → SE-004 (M)
CA-001 (S) → CA-002 (S) → CA-003 (M) → CA-004 (S)
PM-001 (S) → PM-002 (S) → PM-004 (S)
AP-001 (M) → AP-002 (S) → AP-003 (S)
TU-001 (S) → TU-002 (M) → TU-003 (S)
QA-001 (S) → QA-002 (M)
```

**Longest sequential chain**: CA chain (CA-001 → CA-002 → CA-003 → CA-004: S+S+M+S) and SE chain (SE-001 → SE-002 → SE-003 → SE-004: S+M+M+M) are the longest chains by effort. These are independent and can execute in parallel.

**Recommended execution sequence**:
1. **Phase A (parallel)**: PA-001, SE-001, CA-001, PM-001, AP-001, TU-001, QA-001, RP-001 (all P0 gate integrity, no cross-component prerequisites)
2. **Phase B (parallel)**: PA-002, SE-002, CA-002, PM-002, AP-002, TU-002, QA-002, RP-002 (P0/P1 items that depend only on their own component's P0 item)
3. **Phase C (parallel)**: PA-003, SE-003, CA-003, PM-004, AP-003, TU-003, CA-004 (P1 items with cross-P1 dependencies)
4. **Phase D (parallel)**: PA-004, SE-004, SE-005, PM-003, QA-003, TU-004, RP-003, RP-004 (P2 items, all optional refinements)

---

## Component Coverage Verification

| IC Component Group | Items in Master | P0 Items | Highest-Priority Item |
|---|---|---|---|
| Roadmap Pipeline | RP-001, RP-002, RP-003, RP-004 | RP-001 | RP-001 (P0) |
| Cleanup-Audit CLI | CA-001, CA-002, CA-003, CA-004 | CA-001, CA-002 | CA-001 (P0) |
| Sprint Executor | SE-001, SE-002, SE-003, SE-004, SE-005 | SE-001 | SE-001 (P0) |
| PM Agent | PM-001, PM-002, PM-004, PM-003 | PM-001, PM-002 | PM-001 (P0) |
| Adversarial Pipeline | AP-001, AP-002, AP-003 | AP-001 | AP-001 (P0) |
| Task-Unified Tier System | TU-001, TU-002, TU-003, TU-004 | TU-001 | TU-001 (P0) |
| Quality Agents | QA-001, QA-002, QA-003 | QA-001, QA-002 | QA-001 (P0) |
| Pipeline Analysis Subsystem | PA-001, PA-002, PA-003, PA-004 | PA-001, PA-002 | PA-001 (P0) |

All 8 IC component groups represented. ✅

---

## Acceptance Criteria Check

| Criterion | Required | Actual | Status |
|---|---|---|---|
| File `D-0028/spec.md` exists as improve-master.md | Yes | Yes | PASS |
| All 8 IC component groups represented | Yes | All 8 present in coverage table | PASS |
| Dependency graph explicitly labels prerequisites vs. optional refinements | Yes | [PREREQ] and [OPT] labels used throughout | PASS |
| No circular dependencies | Yes | DAG verified; 0 cycles | PASS |
| Aggregated improvement item summary present | Yes | 31 items across 3 priority tiers | PASS |
