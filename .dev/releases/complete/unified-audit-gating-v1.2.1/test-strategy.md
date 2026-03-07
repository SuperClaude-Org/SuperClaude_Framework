---
spec_source: .dev/releases/current/unified-audit-gating-v1.2.1/unified-spec-v1.0.md
generated: 2026-03-06T12:00:00Z
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 3
work_milestones: 6
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score: 0.650)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Per-Task Subprocess Architecture) | M1 foundation (TurnLedger arithmetic, error_max_turns detection, INCOMPLETE reclassification) + M2 subprocess architecture (tasklist parser, per-task loop, 4-layer isolation, result aggregation, backward-compatible defaults) | TurnLedger invariant violation; budget calculation error; subprocess failing to launch with correct isolation; grace_period=0 behavioral divergence from v1.2.1 |
| V2 | M4 (Trailing Gate Infrastructure) | M3 context injection (prior work summary, gate outcomes, remediation history, progressive summarization) + M4 trailing gates (TrailingGateRunner, GateResultQueue thread safety, scope-based strategy, executor branching) | Context injection missing gate/remediation fields; thread safety violation under concurrent access; gate evaluation exceeding 50ms NFR; scope misclassification (release gate allowed to trail) |
| V3 | M6 (TUI Integration & Rollout Hardening) | M5 remediation pipeline (retry economics, conflict review, diagnostic chain, resume semantics, full-flow integration) + M6 TUI + production hardening (GateDisplayState, shadow mode, KPI reporting) | Full-flow integration test fails any of 4 scenarios (pass, fail-remediate-pass, fail-halt, low-budget-halt); diagnostic chain produces unusable resume command; TUI gate column renders incorrect state; shadow mode affects blocking behavior |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | TurnLedger invariant violation (available ≠ initial - consumed + reimbursed); deadlock in gate evaluation; release gate allowed to trail; silent incompletion reproduced |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Context injection missing gate outcomes (Gap 4); remediation spawned without budget check (Gap 1); gate evaluation >50ms on 100KB (Gap 7); backward compatibility broken |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Documentation gaps; unused import in new module; non-deterministic test timing; TUI rendering edge case |
| Info | Log only, no action required | N/A | Performance optimization opportunity; alternative implementation approach noted; code style suggestion |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | TurnLedger arithmetic correct; error_max_turns detected; INCOMPLETE status fires HALT | All D1.1–D1.4 acceptance criteria met; no Critical/Major issues |
| M2 | Per-task subprocess loop functional; 4-layer isolation active; result aggregation correct; GateMode defaults backward-compatible | All D2.1–D2.6 acceptance criteria met; cold-start ≤5K tokens; budget accounting correct across 5+ tasks |
| M3 | Context injection includes gate outcomes + remediation history (Gap 4); phase reports runner-constructed; progressive summarization bounded | All D3.1–D3.5 acceptance criteria met; no agent self-reporting dependency |
| M4 | TrailingGateRunner submit/drain/wait functional; thread safety verified; scope-based strategy correct (release=BLOCKING always); gate evaluation <50ms (Gap 7) | All D4.1–D4.5 acceptance criteria met; no deadlock possible; NFR-003 benchmark passes |
| M5 | Remediation retry economics correct; conflict review detects overlaps; diagnostic chain fires runner-side (Gap 2); resume command actionable (Gap 5); full-flow integration passes 4 scenarios (Gap 6) | All D5.1–D5.7 acceptance criteria met; no TurnLedger turns consumed by diagnostic chain |
| M6 | GateDisplayState renders all 7 states; TUI gate column functional; shadow mode collects metrics without behavior change | All D6.1–D6.4 acceptance criteria met; no regression in existing TUI |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 (TurnLedger) | V1 | M1 | Unit tests: debit/credit arithmetic, boundary conditions, budget monotonicity property |
| FR-002 (error_max_turns) | V1 | M1 | Unit tests: regex detection on synthetic NDJSON, false positive rejection |
| FR-003 (INCOMPLETE reclassification) | V1 | M1 | Integration test: status classified as INCOMPLETE on budget exhaustion |
| FR-004 (Per-task subprocess) | V1 | M2 | Integration test: per-task loop with 5+ tasks, all launched and tracked |
| FR-005 (4-layer isolation) | V1 | M2 | Integration test: verify all 4 isolation layers active per subprocess |
| FR-006 (Context injection) | V2 | M3 | Unit tests: prior results summary, gate outcomes, remediation history, progressive summarization |
| FR-007 (Runner as truth) | V1 | M2 | Integration test: runner tracks all launches/completions/gates/budget |
| FR-008 (TrailingGateRunner) | V2 | M4 | Unit + thread safety tests: submit/drain/wait_for_pending under concurrency |
| FR-009 (GateResultQueue) | V2 | M4 | Thread safety tests: concurrent put/drain, pending count accuracy |
| FR-010 (DeferredRemediationLog) | V2 | M4 | Unit tests: append/pending/mark, serialization roundtrip |
| FR-011 (Scope-based strategy) | V2 | M4 | Unit tests: release=BLOCKING enforced; task=TRAILING with grace_period=1 |
| FR-012 (Retry + remediation) | V3 | M5 | Full-flow integration test: 4 scenarios |
| FR-013 (Reimbursement rules) | V1 | M1 | Unit tests: 90% credit on PASS, zero on persistent failure |
| FR-014 (TrailingGatePolicy) | V3 | M5 | Unit tests: protocol implementation, remediation prompt construction |
| FR-015 (Conflict review) | V3 | M5 | Unit tests: overlap detection, re-gate logic, no-overlap passthrough |
| FR-016 (Diagnostic chain) | V3 | M5 | Unit tests: chain step sequencing (mocked sub-agents), graceful degradation |
| FR-017 (Resume semantics) | V3 | M5 | Integration test: HALT output includes task ID, remaining tasks, budget |
| FR-018 (TaskResult) | V2 | M3 | Unit tests: all fields populated from subprocess output |
| FR-019 (Phase reports) | V2 | M3 | Integration test: aggregate results match expectations |
| FR-020 (TUI gate column) | V3 | M6 | Integration test: all 7 GateDisplayState values render correctly |
| FR-021 (GateMode defaults) | V1 | M2 | Unit + integration test: BLOCKING default preserves v1.2.1 behavior |
| FR-022 (Executor branching) | V2 | M4 | Integration test: correct path taken per configuration |
| FR-023 (Pre-remediation budget check, Gap 1) | V3 | M5 | Full-flow scenario 4: budget too low → skip remediation → HALT |
| FR-024 (Diagnostic budget boundary, Gap 2) | V3 | M5 | Integration test: chain fires regardless of ledger state; no TurnLedger turns consumed |
| FR-025 (Tasklist parser) | V1 | M2 | Unit tests: markdown parsing, ID extraction, dependency annotation, malformed input |
| FR-026 (Turn counting) | V1 | M2 | Integration test: actual turns counted and debited correctly |
| FR-027 (GateDisplayState) | V3 | M6 | Unit tests: all 7 enum values; TUI rendering |
| FR-028 (Remediation retry) | V3 | M5 | Integration test: retry economics, budget drain on persistent failure |
| NFR-001 (Thread safety) | V2 | M4 | Stress test: concurrent submit/drain under load |
| NFR-002 (Layer isolation) | V2 | M4 | Code review: no cross-layer imports in trailing_gate.py |
| NFR-003 (Gate perf <50ms) | V2 | M4 | Benchmark: gate_passed() on 100KB synthetic output |
| NFR-004 (Backward compat) | V1, V3 | M2, all | grace_period=0 behavioral equivalence test |
| NFR-005 (No deadlock) | V2 | M4 | Analysis: verify no locks in daemon threads; bounded wait in main |
| NFR-006 (Daemon lifecycle) | V2 | M4 | Test: daemon threads abandoned on pipeline exit |
| NFR-007 (Budget monotonicity) | V1 | M1 | Property-based test: available() non-increasing across operations |
| NFR-008 (No infinite run) | V1 | M1 | Mathematical proof: net_cost_per_task > 0 with 90% rate |
