---
spec_source: .dev/releases/current/unified-audit-gating-v1.2.1/unified-spec-v1.0.md
generated: 2026-03-06T12:00:00Z
generator: sc:roadmap
complexity_score: 0.650
complexity_class: MEDIUM
domain_distribution:
  backend: 65
  performance: 20
  frontend: 10
  security: 3
  documentation: 2
primary_persona: backend
consulting_personas: [architect, performance]
milestone_count: 9
milestone_index:
  - id: M1
    title: "Foundation — TurnLedger & Immediate Detection"
    type: FEATURE
    priority: P0
    effort: S
    dependencies: []
    deliverable_count: 4
    risk_level: Low
  - id: M2
    title: "Per-Task Subprocess Architecture"
    type: FEATURE
    priority: P0
    effort: L
    dependencies: [M1]
    deliverable_count: 6
    risk_level: High
  - id: V1
    title: "Validation — Foundation & Subprocess"
    type: TEST
    priority: P3
    effort: S
    dependencies: [M1, M2]
    deliverable_count: 3
    risk_level: Low
  - id: M3
    title: "Context Injection & Runner Reporting"
    type: FEATURE
    priority: P1
    effort: M
    dependencies: [M2]
    deliverable_count: 5
    risk_level: Medium
  - id: M4
    title: "Trailing Gate Infrastructure"
    type: FEATURE
    priority: P1
    effort: M
    dependencies: [M2]
    deliverable_count: 5
    risk_level: Medium
  - id: V2
    title: "Validation — Context & Gate Infrastructure"
    type: TEST
    priority: P3
    effort: S
    dependencies: [M3, M4]
    deliverable_count: 3
    risk_level: Low
  - id: M5
    title: "Remediation, Conflict Review & Diagnostic Chain"
    type: FEATURE
    priority: P1
    effort: L
    dependencies: [M4]
    deliverable_count: 7
    risk_level: High
  - id: M6
    title: "TUI Integration & Rollout Hardening"
    type: IMPROVEMENT
    priority: P2
    effort: S
    dependencies: [M4, M5]
    deliverable_count: 4
    risk_level: Low
  - id: V3
    title: "Final Validation — End-to-End Acceptance"
    type: TEST
    priority: P3
    effort: M
    dependencies: [M5, M6]
    deliverable_count: 4
    risk_level: Medium
total_deliverables: 41
total_risks: 16
estimated_phases: 6
validation_score: 0.937
validation_status: PASS
---

# Roadmap: Turn-Budget Reimbursement with Trailing Gate Enforcement

## Overview

This roadmap addresses the silent incompletion problem in the sprint runner (`superclaude sprint`) where budget-exhausted subprocesses exit with code 0 and unfinished tasks are reported as successes. The solution merges two architectural approaches: per-task subprocess spawning with TurnLedger economics (Solution A) and trailing gate enforcement with deferred remediation (Solution B), unified via panel review by Fowler, Nygard, Newman, Wiegers, Crispin, and Hohpe.

The roadmap follows Newman's independently-deployable-per-phase principle: Phase 1 alone detects the problem (no more silent failures), Phase 1+2 structurally eliminates it (per-task subprocess + TurnLedger), Phase 1+2+3 adds quality enforcement (trailing gates + remediation), and Phase 4 hardens for production. A user can stop at M2 and have a fully working solution to the MaxTurn problem.

The implementation spans approximately 1,740 lines of new code across 10+ independently testable components, with backward compatibility preserved via `grace_period=0` defaults that produce behavior identical to v1.2.1.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation — TurnLedger & Immediate Detection | FEATURE | P0 | S | None | 4 | Low |
| M2 | Per-Task Subprocess Architecture | FEATURE | P0 | L | M1 | 6 | High |
| V1 | Validation — Foundation & Subprocess | TEST | P3 | S | M1, M2 | 3 | Low |
| M3 | Context Injection & Runner Reporting | FEATURE | P1 | M | M2 | 5 | Medium |
| M4 | Trailing Gate Infrastructure | FEATURE | P1 | M | M2 | 5 | Medium |
| V2 | Validation — Context & Gate Infrastructure | TEST | P3 | S | M3, M4 | 3 | Low |
| M5 | Remediation, Conflict Review & Diagnostic Chain | FEATURE | P1 | L | M4 | 7 | High |
| M6 | TUI Integration & Rollout Hardening | IMPROVEMENT | P2 | S | M4, M5 | 4 | Low |
| V3 | Final Validation — End-to-End Acceptance | TEST | P3 | M | M5, M6 | 4 | Medium |

## Dependency Graph

```
M1 → M2 → M3 ──→ V2
        └→ M4 ──→ V2
             └→ M5 → V3
             └→ M6 → V3
M1 → V1 (also depends on M2)
```

Linear critical path: M1 → M2 → M4 → M5 → V3

---

## M1: Foundation — TurnLedger & Immediate Detection

### Objective
Implement the TurnLedger economic model and error_max_turns detection to immediately detect silent incompletion. This delivers detection value without requiring per-task subprocess migration.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | TurnLedger dataclass in sprint/models.py (~50 lines): initial_budget, consumed, reimbursed, reimbursement_rate, minimum_allocation, minimum_remediation_budget, debit(), credit(), can_launch(), can_remediate(), available() | All arithmetic operations correct; can_launch() returns False when available() < minimum_allocation; budget monotonicity invariant holds |
| D1.2 | error_max_turns NDJSON detection in sprint/monitor.py (~15 lines): regex on last NDJSON line detects "subtype":"error_max_turns" | Detection fires on synthetic error_max_turns output; no false positives on normal NDJSON output |
| D1.3 | PASS_NO_REPORT + error_max_turns → INCOMPLETE reclassification (~10 lines) | Status classified as INCOMPLETE (not success) when error_max_turns detected; HALT triggered instead of silent PASS |
| D1.4 | Budget check before subprocess launch: ledger.can_launch() guard (~10 lines) | Subprocess not launched when budget insufficient; HALT with budget-specific message |

### Dependencies
- None (first milestone)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Regex false positives on NDJSON | Low | Medium | Test against diverse NDJSON payloads including edge cases |

---

## M2: Per-Task Subprocess Architecture

### Objective
Migrate from per-phase subprocess to per-task subprocess spawning with runner-owned task sequencing, 4-layer isolation, and TurnLedger integration. This structurally eliminates the MaxTurn problem.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Tasklist parser in sprint/config.py (~100 lines): markdown → task inventory with IDs, dependency annotations | Parses phase tasklist files; extracts task IDs and dependencies; handles malformed input gracefully |
| D2.2 | Per-task subprocess orchestration loop in sprint/executor.py (~200 lines): one subprocess per task with ledger integration | Each task gets its own subprocess; runner tracks all launches/completions; no task starvation |
| D2.3 | 4-layer subprocess isolation setup (~40 lines): scoped working dir, git boundary, empty plugin dir, restricted settings | Cold-start cost ≤5K tokens (~2 turns); all 4 layers verified active per subprocess |
| D2.4 | Result aggregation + runner-constructed phase reports (~140 lines): aggregate TaskResults into PhaseResult | Phase reports constructed without agent self-reporting; all task outcomes tracked |
| D2.5 | GateMode enum + Step.gate_mode field (~20 lines) + PipelineConfig.grace_period (~10 lines) | GateMode.BLOCKING is default; grace_period=0 is default; backward compatibility verified |
| D2.6 | Turn counting from subprocess output + TurnLedger debit wiring (~15 lines) + pre-remediation budget check (~20 lines, Gap 1) | Actual turns counted from output; debited from ledger; can_remediate() checked before remediation spawn |

### Dependencies
- M1: TurnLedger must exist for budget integration

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Cold-start overhead exceeds budget | Medium | High | 4-layer isolation reduces to ~5K tokens; TurnLedger budgets for ~2 turns per task |
| Context fragmentation across tasks | High | Medium | Structured context injection (M3) mitigates; per-task model trades implicit for explicit context |
| Complex orchestration (~925 lines) | Medium | Medium | 10+ independently testable components; incremental integration |

---

## V1: Validation — Foundation & Subprocess

### Objective
Validate M1 and M2 deliverables against spec requirements before proceeding to trailing gate infrastructure.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV1.1 | TurnLedger unit tests: debit/credit arithmetic, budget exhaustion, boundary conditions, reimbursement rate, budget monotonicity property | All tests pass; 100% branch coverage on TurnLedger methods |
| DV1.2 | Per-task subprocess integration test: full task loop with budget tracking across ≥5 tasks | All tasks launched, results aggregated, budget accounting correct |
| DV1.3 | Backward compatibility test: grace_period=0 produces identical results to v1.2.1, zero daemon threads | Behavioral equivalence verified; threading.active_count() unchanged |

### Dependencies
- M1, M2

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Test infrastructure gaps | Low | Low | Existing test patterns for sprint module provide scaffolding |

---

## M3: Context Injection & Runner Reporting

### Objective
Implement deterministic context injection (including gate/remediation history per Gap 4) and runner-constructed reporting to ensure task N+1 has full visibility into prior work.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Context injection builder in sprint/process.py (~180 lines): deterministic summary from result files, gate outcomes, remediation history | Each task prompt includes structured prior work context; gate outcomes visible; remediation history included |
| D3.2 | TaskResult dataclass in sprint/models.py: runner-constructed result combining execution data, gate outcome, reimbursement | All fields populated from subprocess output; no agent self-reporting dependency |
| D3.3 | Phase-level report aggregation: runner constructs phase YAML from TaskResults | Phase reports include tasks_total, tasks_passed, tasks_failed, tasks_incomplete, tasks_not_attempted, budget_remaining |
| D3.4 | Git diff context integration: `git diff --stat` since sprint start appended to context | Structural overview of changes available to each task |
| D3.5 | Progressive summarization: running summary compressed every N tasks to stay within token budget | Summary size bounded; no context overflow for long sprints |

### Dependencies
- M2: per-task subprocess architecture must be operational

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Context too large for task prompt | Medium | Medium | Progressive summarization (D3.5) caps context size |
| Missing gate/remediation context (Gap 4) | Medium | High | Explicit inclusion of gate outcomes and remediation history in context builder |

---

## M4: Trailing Gate Infrastructure

### Objective
Implement the trailing gate evaluation infrastructure: TrailingGateRunner, GateResultQueue, DeferredRemediationLog, and scope-based gate strategy. This is the quality enforcement layer.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | TrailingGateRunner in pipeline/trailing_gate.py (~120 lines): submit(), drain(), wait_for_pending(), cancel() | Gate evaluation spawns daemon thread; wait_for_pending() blocks bounded; cancel propagates to all threads |
| D4.2 | GateResultQueue in pipeline/trailing_gate.py: thread-safe queue using stdlib queue.Queue | put/drain thread-safe under concurrent access; pending_count() accurate |
| D4.3 | DeferredRemediationLog in pipeline/trailing_gate.py (~80 lines): append, pending_remediations, mark_remediated, serialization | Serializable to disk for --resume; single-writer thread safety |
| D4.4 | Scope-based gate strategy: Release=BLOCKING always, Milestone=configurable, Task=TRAILING default | Release gates never trailing; scope detection uses existing validate_transition() |
| D4.5 | Executor branching in execute_pipeline(): trailing vs blocking path based on GateMode + grace_period | Correct path taken per configuration; trailing path executes sync point |

### Dependencies
- M2: per-task subprocess architecture (trailing gates evaluate static output from terminated subprocesses)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gate daemon thread crashes | Low | Medium | Daemons catch all exceptions and post FAIL result to queue |
| Deadlock in gate evaluation | Low | High | Deadlock analysis proves impossibility: no locks acquired by daemons, bounded wait in main thread |
| Gate evaluation too slow (Gap 7) | Low | Medium | NFR: <50ms for 100KB; tracked in TrailingGateResult.evaluation_ms |

---

## V2: Validation — Context & Gate Infrastructure

### Objective
Validate M3 and M4 deliverables: context injection correctness, trailing gate thread safety, and scope-based gate strategy.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV2.1 | Context injection tests: prior results summary, gate outcome inclusion, remediation history, progressive summarization | Context includes all required fields; summary bounded; gate outcomes visible |
| DV2.2 | Trailing gate thread safety tests: concurrent submit/drain, pending count accuracy, cancel propagation | No race conditions under concurrent access; results arrive in correct association by step_id |
| DV2.3 | Gate performance NFR test: gate_passed() on synthetic 100KB output completes in <50ms (Gap 7) | Timed benchmark passes; evaluation_ms field populated |

### Dependencies
- M3, M4

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Thread timing sensitivity in tests | Medium | Low | Use deterministic fixtures and bounded timeouts |

---

## M5: Remediation, Conflict Review & Diagnostic Chain

### Objective
Implement the complete failure recovery pipeline: unified retry + remediation model, conflict review for file-level overlap detection, and diagnostic chain (troubleshoot → adversarial → summary) for intelligent failure analysis.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | TrailingGatePolicy protocol: consumer-owned hooks for build_remediation_step() and files_changed() | Protocol implemented; sprint consumer provides concrete implementation |
| D5.2 | Remediation subprocess construction: focused prompt with gate failure reason + acceptance criteria | Remediation subprocess targets specific failure; prompt includes necessary context |
| D5.3 | Remediation retry with TurnLedger integration (~60 lines): retry once on failure, both attempts' turns lost on persistent failure | Retry economics correct; budget drain on persistent failure; ledger accounting verified |
| D5.4 | conflict_review.py (~80 lines): file-level overlap detection between remediation and intervening work | Overlapping files detected; re-gate triggered when overlap found; no-overlap passthrough works |
| D5.5 | diagnostic_chain.py (~100 lines): troubleshoot → adversarial(root causes) → adversarial(solutions) → summary | Chain fires on persistent remediation failure; runner-side (not TurnLedger turns — Gap 2); best-effort with graceful degradation |
| D5.6 | Resume semantics (~40 lines, Gap 5): actionable resume command with task ID, remaining tasks, diagnostic output, budget suggestion | HALT output includes resume command; task ID correct; remaining tasks listed |
| D5.7 | Full-flow integration test (~200 lines, Gap 6): 4 scenarios — pass, fail-remediate-pass, fail-halt, low-budget-halt | All 4 scenarios pass; compound flow exercises budget + gate + remediation + context |

### Dependencies
- M4: trailing gate infrastructure must be operational (gates trigger remediation)

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Remediation breaks subsequent work | Low | High | Conflict review (D5.4) detects file overlaps; re-gate on overlap |
| Complex orchestration (remediation state machine) | Medium | Medium | Independently testable components; clear state transitions |
| Diagnostic chain sub-agent failures | Medium | Low | Best-effort: chain errors caught; user still gets standard HALT output |

---

## M6: TUI Integration & Rollout Hardening

### Objective
Add the TUI gate column for user visibility and implement production hardening features: shadow mode, KPI reporting, and promotion gates.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D6.1 | GateDisplayState enum (~30 lines): 7 visual states (NONE, CHECKING, PASS, FAIL_DEFERRED, REMEDIATING, REMEDIATED, HALT) | All states render correctly in TUI; state transitions follow gate lifecycle |
| D6.2 | TUI gate column in sprint/tui.py (~40 lines): inline gate status column in phase table | Column renders gate states per task; non-blocking TUI reads (existing pattern) |
| D6.3 | Shadow mode: trailing gate metrics alongside blocking, configurable via --shadow-gates | Metrics collected without affecting behavior; comparison to blocking baseline available |
| D6.4 | KPI report: trailing gate latency, remediation frequency, conflict review rate | Report generated after sprint; metrics accurate |

### Dependencies
- M4: trailing gate infrastructure for gate state data
- M5: remediation infrastructure for remediation/conflict metrics

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TUI rendering overhead | Low | Low | Existing best-effort snapshot pattern; no locks added |

---

## V3: Final Validation — End-to-End Acceptance

### Objective
End-to-end acceptance testing of the complete unified solution: budget economics, per-task subprocess, trailing gates, remediation, diagnostic chain, and backward compatibility.

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV3.1 | End-to-end sprint test with trailing gates: multi-task sprint exercising the complete flow including gate evaluation, remediation, and context injection | Sprint completes with correct per-task results; budget accounting verified; no silent incompletion |
| DV3.2 | Backward compatibility regression: grace_period=0 sprint identical to v1.2.1 output | Byte-for-byte equivalent results; zero daemon threads; all existing tests pass without modification |
| DV3.3 | Property-based tests: TurnLedger invariants, gate result ordering, remediation idempotency | All properties hold across randomized inputs |
| DV3.4 | Performance NFR validation: gate evaluation <50ms on 100KB output; budget calculations O(1) | Benchmarks pass within NFR thresholds |

### Dependencies
- M5: complete remediation and diagnostic chain
- M6: TUI integration and shadow mode

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| End-to-end test complexity | Medium | Medium | Build on M5's full-flow integration test; extend with TUI and shadow mode |
| Performance regression under load | Low | Medium | Benchmark against v1.2.1 baseline |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Context fragmentation: task N+1 lacks context from task N | M2, M3 | High | Medium | Structured context injection with gate/remediation history (M3) | backend |
| R-002 | Subprocess cold-start overhead: ~2 turns per task (~92 total for 46 tasks) | M2 | Certain | Medium | 4-layer isolation reduces to ~5K tokens; budgeted in TurnLedger model | performance |
| R-003 | Loss of inter-task optimization: redundant file reads | M2 | Medium | Low | Context injection + git diff; most tasks touch different files | backend |
| R-004 | More total turns consumed: ~138 overhead vs ~12 for per-phase | M1, M2 | Certain | Medium | Budget model accommodates with 71 turns of margin on 200-turn budget | performance |
| R-005 | Complex orchestration: ~1,740 lines across 10+ components | All | Medium | Medium | Independently testable components; validation milestones after every 2 work milestones | architect |
| R-006 | API rate limiting on 46+ subprocess spawns | M2 | Low | Low | Configurable concurrency; sequential default; backoff between spawns | backend |
| R-007 | Gate daemon thread crashes: gate failure undetected | M4 | Low | Medium | Daemons catch all exceptions; post FAIL to queue on error | backend |
| R-008 | Remediation cascading failure: remediation breaks subsequent work | M5 | Low | High | Conflict review with file-level overlap detection (M5) | backend |
| R-009 | Queue corruption under load | M4 | Low | Medium | stdlib queue.Queue well-tested; no custom synchronization | backend |
| R-010 | Low budget + gate failure compound: wasted turns on doomed remediation (Gap 1) | M2, M5 | Medium | High | Pre-remediation budget check: can_remediate() guard | backend |
| R-011 | Diagnostic chain confused by budget problem (Gap 2) | M5 | Low | Medium | Budget-specific halt skips diagnostic chain; chain is runner-side, free | backend |
| R-012 | Isolation boundary confusion: daemon created inside subprocess (Gap 3) | M2, M4 | Low | Medium | Explicit documentation: gate daemons are runner-side | architect |
| R-013 | Missing gate/remediation context in next task prompt (Gap 4) | M3 | Medium | High | Context builder explicitly includes gate outcomes + remediation history | backend |
| R-014 | Unusable resume after diagnostic (Gap 5) | M5 | Medium | Medium | Resume command includes task ID + remaining tasks + budget suggestion | backend |
| R-015 | No full-flow integration test (Gap 6) | M5 | Medium | High | Full-flow integration test is M5 deliverable, not deferred (Crispin) | backend |
| R-016 | Gate evaluation too slow on large output (Gap 7) | M4 | Low | Medium | NFR: <50ms for 100KB; tracked in evaluation_ms field | performance |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | backend (0.546) | architect (0.455), performance (0.154) | Backend domain dominates at 65% — subprocess model, data models, threading |
| Template | inline | No templates in Tiers 1-3 | Tier 4 fallback; no local/user templates available |
| Milestone Count | 9 (6 work + 3 validation) | 5-7 range from MEDIUM complexity | base(5) + floor(3 domains / 2) = 6 work; 1:2 interleave adds 3 validation |
| Adversarial Mode | none | N/A | Single-spec mode, no --specs or --multi-roadmap flags |
| Adversarial Base Variant | N/A | N/A | No adversarial mode active |
| Interleave Strategy | 1:2 (validation every 2 work milestones) | 1:1 (HIGH), 1:3 (LOW) | MEDIUM complexity class → 1:2 ratio |
| Phase Alignment | Spec's 4-phase roadmap → 6 work milestones + 3 validation | Direct 1:1 phase mapping | Finer granularity enables independent testability per Newman's principle |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | No silent incompletion: runner detects budget exhaustion and reports INCOMPLETE | M1, V1 | Yes — budget-exhaustion scenario test |
| SC-002 | Every task gets own budget allocation — no task starvation | M2, V1 | Yes — verify all 46 tasks launched in worked example |
| SC-003 | Every task output passes gate before runner considers complete | M4, V2 | Yes — gate evaluation recorded per task |
| SC-004 | Budget mathematically bounded — no infinite loops with 90% reimbursement | M1, V3 | Yes — net_cost_per_task > 0 provable |
| SC-005 | grace_period=0 identical to v1.2.1 — zero daemon threads, all tests pass | M2, V3 | Yes — behavioral comparison test |
| SC-006 | Full-flow integration test passes all 4 scenarios | M5, V3 | Yes — 4-scenario integration test (Gap 6) |
| SC-007 | Gate evaluation <50ms for 100KB output | M4, V2 | Yes — timed benchmark |
