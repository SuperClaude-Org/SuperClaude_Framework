# TASKLIST INDEX -- Turn-Budget Reimbursement with Trailing Gate Enforcement

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | Turn-Budget Reimbursement with Trailing Gate Enforcement |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-06 |
| TASKLIST_ROOT | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/ |
| Total Phases | 9 |
| Total Tasks | 41 |
| Total Deliverables | 41 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | architect, performance |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-5-tasklist.md |
| Phase 6 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-6-tasklist.md |
| Phase 7 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-7-tasklist.md |
| Phase 8 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-8-tasklist.md |
| Phase 9 Tasklist | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/phase-9-tasklist.md |
| Execution Log | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/execution-log.md |
| Checkpoint Reports | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/ |
| Evidence Directory | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/evidence/ |
| Artifacts Directory | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/ |
| Feedback Log | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation — TurnLedger & Detection | T01.01-T01.04 | STRICT: 4 |
| 2 | phase-2-tasklist.md | Per-Task Subprocess Architecture | T02.01-T02.06 | STRICT: 6 |
| 3 | phase-3-tasklist.md | Validation — Foundation & Subprocess | T03.01-T03.03 | STANDARD: 3 |
| 4 | phase-4-tasklist.md | Context Injection & Runner Reporting | T04.01-T04.05 | STRICT: 2, STANDARD: 3 |
| 5 | phase-5-tasklist.md | Trailing Gate Infrastructure | T05.01-T05.05 | STRICT: 5 |
| 6 | phase-6-tasklist.md | Validation — Context & Gate Infra | T06.01-T06.03 | STANDARD: 2, STRICT: 1 |
| 7 | phase-7-tasklist.md | Remediation, Conflict & Diagnostics | T07.01-T07.07 | STRICT: 6, STANDARD: 1 |
| 8 | phase-8-tasklist.md | TUI Integration & Rollout Hardening | T08.01-T08.04 | STANDARD: 4 |
| 9 | phase-9-tasklist.md | Final Validation — E2E Acceptance | T09.01-T09.04 | STANDARD: 3, STRICT: 1 |

## Source Snapshot

- Addresses silent incompletion in `superclaude sprint` where budget-exhausted subprocesses exit code 0
- Merges per-task subprocess spawning with TurnLedger economics and trailing gate enforcement with deferred remediation
- Implementation spans ~1,740 lines across 10+ independently testable components
- Backward compatibility preserved via `grace_period=0` defaults identical to v1.2.1
- Critical path: M1 → M2 → M4 → M5 → V3
- Validation milestones interleaved at 1:2 ratio (V1 after M1+M2, V2 after M3+M4, V3 after M5+M6)

## Deterministic Rules Applied

- Phase bucketing: each roadmap milestone (M1-M6, V1-V3) mapped to one phase in appearance order
- Phase renumbering: M1→P1, M2→P2, V1→P3, M3→P4, M4→P5, V2→P6, M5→P7, M6→P8, V3→P9 (contiguous, no gaps)
- Task IDs: `T<PP>.<TT>` zero-padded; one task per roadmap deliverable (41 total, no splits needed)
- Checkpoint cadence: every 5 tasks within a phase + mandatory end-of-phase checkpoint
- Clarification tasks: none required (roadmap provides sufficient specificity for all deliverables)
- Deliverable registry: D-0001 through D-0041 in global appearance order
- Effort mapping: deterministic EFFORT_SCORE from text length, splits, keyword presence, dependency words
- Risk mapping: deterministic RISK_SCORE from security, migration, auth, performance, cross-cutting keywords
- Tier classification: STRICT/STANDARD/LIGHT/EXEMPT per keyword matching + context boosters
- Verification routing: STRICT → sub-agent, STANDARD → direct test, per tier table
- MCP requirements: STRICT requires Sequential + Serena; STANDARD prefers Sequential + Context7
- Traceability: every R-### mapped to T<PP>.<TT> mapped to D-#### with artifact paths

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | -- | Roadmap: Turn-Budget Reimbursement with Trailing Gate Enforcement |
| R-002 | -- | This roadmap addresses the silent incompletion problem in the sprint runner where budget-exhausted subprocesses exit with code 0 |
| R-003 | P1 | M1: Foundation — TurnLedger & Immediate Detection |
| R-004 | P1 | D1.1 TurnLedger dataclass in sprint/models.py (~50 lines): initial_budget, consumed, reimbursed, reimbursement_rate, minimum_allocation, minimum_remediation_budget, debit(), credit(), can_launch(), can_remediate(), available() |
| R-005 | P1 | D1.2 error_max_turns NDJSON detection in sprint/monitor.py (~15 lines): regex on last NDJSON line detects |
| R-006 | P1 | D1.3 PASS_NO_REPORT + error_max_turns → INCOMPLETE reclassification (~10 lines) |
| R-007 | P1 | D1.4 Budget check before subprocess launch: ledger.can_launch() guard (~10 lines) |
| R-008 | P2 | M2: Per-Task Subprocess Architecture |
| R-009 | P2 | D2.1 Tasklist parser in sprint/config.py (~100 lines): markdown → task inventory with IDs, dependency annotations |
| R-010 | P2 | D2.2 Per-task subprocess orchestration loop in sprint/executor.py (~200 lines): one subprocess per task with |
| R-011 | P2 | D2.3 4-layer subprocess isolation setup (~40 lines): scoped working dir, git boundary, empty plugin dir, restricted |
| R-012 | P2 | D2.4 Result aggregation + runner-constructed phase reports (~140 lines): aggregate TaskResults into PhaseResult |
| R-013 | P2 | D2.5 GateMode enum + Step.gate_mode field (~20 lines) + PipelineConfig.grace_period (~10 lines) |
| R-014 | P2 | D2.6 Turn counting from subprocess output + TurnLedger debit wiring (~15 lines) + pre-remediation budget check |
| R-015 | P3 | V1: Validation — Foundation & Subprocess |
| R-016 | P3 | DV1.1 TurnLedger unit tests: debit/credit arithmetic, budget exhaustion, boundary conditions, reimbursement rate, budget monotonicity property |
| R-017 | P3 | DV1.2 Per-task subprocess integration test: full task loop with budget tracking across ≥5 tasks |
| R-018 | P3 | DV1.3 Backward compatibility test: grace_period=0 produces identical results to v1.2.1, zero daemon threads |
| R-019 | P4 | M3: Context Injection & Runner Reporting |
| R-020 | P4 | D3.1 Context injection builder in sprint/process.py (~180 lines): deterministic summary from result files, gate outcomes, |
| R-021 | P4 | D3.2 TaskResult dataclass in sprint/models.py: runner-constructed result combining execution data, gate outcome, reimbursement |
| R-022 | P4 | D3.3 Phase-level report aggregation: runner constructs phase YAML from TaskResults |
| R-023 | P4 | D3.4 Git diff context integration: git diff --stat since sprint start appended to context |
| R-024 | P4 | D3.5 Progressive summarization: running summary compressed every N tasks to stay within token budget |
| R-025 | P5 | M4: Trailing Gate Infrastructure |
| R-026 | P5 | D4.1 TrailingGateRunner in pipeline/trailing_gate.py (~120 lines): submit(), drain(), wait_for_pending(), cancel() |
| R-027 | P5 | D4.2 GateResultQueue in pipeline/trailing_gate.py: thread-safe queue using stdlib queue.Queue |
| R-028 | P5 | D4.3 DeferredRemediationLog in pipeline/trailing_gate.py (~80 lines): append, pending_remediations, mark_remediated, serialization |
| R-029 | P5 | D4.4 Scope-based gate strategy: Release=BLOCKING always, Milestone=configurable, Task=TRAILING default |
| R-030 | P5 | D4.5 Executor branching in execute_pipeline(): trailing vs blocking path based on GateMode + grace_period |
| R-031 | P6 | V2: Validation — Context & Gate Infrastructure |
| R-032 | P6 | DV2.1 Context injection tests: prior results summary, gate outcome inclusion, remediation history, progressive summarization |
| R-033 | P6 | DV2.2 Trailing gate thread safety tests: concurrent submit/drain, pending count accuracy, cancel propagation |
| R-034 | P6 | DV2.3 Gate performance NFR test: gate_passed() on synthetic 100KB output completes in <50ms |
| R-035 | P7 | M5: Remediation, Conflict Review & Diagnostic Chain |
| R-036 | P7 | D5.1 TrailingGatePolicy protocol: consumer-owned hooks for build_remediation_step() and files_changed() |
| R-037 | P7 | D5.2 Remediation subprocess construction: focused prompt with gate failure reason + acceptance criteria |
| R-038 | P7 | D5.3 Remediation retry with TurnLedger integration (~60 lines): retry once on failure, both attempts turns |
| R-039 | P7 | D5.4 conflict_review.py (~80 lines): file-level overlap detection between remediation and intervening work |
| R-040 | P7 | D5.5 diagnostic_chain.py (~100 lines): troubleshoot → adversarial(root causes) → adversarial(solutions) → summary |
| R-041 | P7 | D5.6 Resume semantics (~40 lines, Gap 5): actionable resume command with task ID, remaining tasks, diagnostic output, |
| R-042 | P7 | D5.7 Full-flow integration test (~200 lines, Gap 6): 4 scenarios — pass, fail-remediate-pass, fail-halt, low-budget-halt |
| R-043 | P8 | M6: TUI Integration & Rollout Hardening |
| R-044 | P8 | D6.1 GateDisplayState enum (~30 lines): 7 visual states |
| R-045 | P8 | D6.2 TUI gate column in sprint/tui.py (~40 lines): inline gate status column in phase table |
| R-046 | P8 | D6.3 Shadow mode: trailing gate metrics alongside blocking, configurable via --shadow-gates |
| R-047 | P8 | D6.4 KPI report: trailing gate latency, remediation frequency, conflict review rate |
| R-048 | P9 | V3: Final Validation — End-to-End Acceptance |
| R-049 | P9 | DV3.1 End-to-end sprint test with trailing gates |
| R-050 | P9 | DV3.2 Backward compatibility regression: grace_period=0 sprint identical to v1.2.1 output |
| R-051 | P9 | DV3.3 Property-based tests: TurnLedger invariants, gate result ordering, remediation idempotency |
| R-052 | P9 | DV3.4 Performance NFR validation: gate evaluation <50ms on 100KB output; budget calculations O(1) |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-004 | TurnLedger dataclass with budget arithmetic | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0001/spec.md | M | Medium |
| D-0002 | T01.02 | R-005 | error_max_turns NDJSON regex detection | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0002/spec.md | S | Low |
| D-0003 | T01.03 | R-006 | INCOMPLETE reclassification on error_max_turns | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0003/spec.md | S | Low |
| D-0004 | T01.04 | R-007 | Pre-launch budget guard via can_launch() | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0004/spec.md | S | Low |
| D-0005 | T02.01 | R-009 | Tasklist parser: markdown → task inventory | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0005/spec.md | M | Medium |
| D-0006 | T02.02 | R-010 | Per-task subprocess orchestration loop | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0006/spec.md | L | High |
| D-0007 | T02.03 | R-011 | 4-layer subprocess isolation setup | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0007/spec.md | M | Medium |
| D-0008 | T02.04 | R-012 | Result aggregation + phase reports | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0008/spec.md | M | Low |
| D-0009 | T02.05 | R-013 | GateMode enum + grace_period config | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0009/spec.md | S | Low |
| D-0010 | T02.06 | R-014 | Turn counting + TurnLedger debit wiring | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0010/spec.md | M | Medium |
| D-0011 | T03.01 | R-016 | TurnLedger unit tests with 100% branch coverage | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0011/spec.md | M | Low |
| D-0012 | T03.02 | R-017 | Per-task subprocess integration test (≥5 tasks) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0012/spec.md | M | Low |
| D-0013 | T03.03 | R-018 | Backward compatibility test (grace_period=0) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0013/spec.md | M | Medium |
| D-0014 | T04.01 | R-020 | Context injection builder in sprint/process.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0014/spec.md | L | Medium |
| D-0015 | T04.02 | R-021 | TaskResult dataclass in sprint/models.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0015/spec.md | M | Low |
| D-0016 | T04.03 | R-022 | Phase-level YAML report aggregation | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0016/spec.md | S | Low |
| D-0017 | T04.04 | R-023 | Git diff context integration | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0017/spec.md | S | Low |
| D-0018 | T04.05 | R-024 | Progressive summarization for token budget | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0018/spec.md | M | Low |
| D-0019 | T05.01 | R-026 | TrailingGateRunner with submit/drain/wait/cancel | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0019/spec.md | M | Medium |
| D-0020 | T05.02 | R-027 | GateResultQueue (thread-safe stdlib queue) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0020/spec.md | S | Medium |
| D-0021 | T05.03 | R-028 | DeferredRemediationLog with serialization | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0021/spec.md | M | Medium |
| D-0022 | T05.04 | R-029 | Scope-based gate strategy (Release/Milestone/Task) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0022/spec.md | M | Medium |
| D-0023 | T05.05 | R-030 | Executor trailing vs blocking branch logic | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0023/spec.md | M | Medium |
| D-0024 | T06.01 | R-032 | Context injection correctness tests | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0024/spec.md | M | Low |
| D-0025 | T06.02 | R-033 | Trailing gate thread safety tests | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0025/spec.md | M | Medium |
| D-0026 | T06.03 | R-034 | Gate performance NFR benchmark (<50ms) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0026/spec.md | S | Low |
| D-0027 | T07.01 | R-036 | TrailingGatePolicy protocol definition | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0027/spec.md | M | Medium |
| D-0028 | T07.02 | R-037 | Remediation subprocess prompt construction | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0028/spec.md | M | Medium |
| D-0029 | T07.03 | R-038 | Remediation retry with TurnLedger economics | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0029/spec.md | M | High |
| D-0030 | T07.04 | R-039 | conflict_review.py file-level overlap detection | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0030/spec.md | M | Medium |
| D-0031 | T07.05 | R-040 | diagnostic_chain.py troubleshoot → adversarial → summary | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0031/spec.md | M | Medium |
| D-0032 | T07.06 | R-041 | Resume semantics with actionable resume command | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0032/spec.md | M | Medium |
| D-0033 | T07.07 | R-042 | Full-flow integration test (4 scenarios) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0033/spec.md | L | High |
| D-0034 | T08.01 | R-044 | GateDisplayState enum (7 visual states) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0034/spec.md | S | Low |
| D-0035 | T08.02 | R-045 | TUI gate column in sprint/tui.py | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0035/spec.md | S | Low |
| D-0036 | T08.03 | R-046 | Shadow mode (--shadow-gates) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0036/spec.md | M | Low |
| D-0037 | T08.04 | R-047 | KPI report for gate/remediation metrics | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0037/spec.md | S | Low |
| D-0038 | T09.01 | R-049 | End-to-end sprint test with trailing gates | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0038/spec.md | L | Medium |
| D-0039 | T09.02 | R-050 | Backward compat regression (grace_period=0) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0039/spec.md | M | Medium |
| D-0040 | T09.03 | R-051 | Property-based tests (TurnLedger invariants) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0040/spec.md | M | Medium |
| D-0041 | T09.04 | R-052 | Performance NFR validation (<50ms gate, O(1) budget) | STANDARD | Direct test execution | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0041/spec.md | S | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-004 | T01.01 | D-0001 | STRICT | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0001/ |
| R-005 | T01.02 | D-0002 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0002/ |
| R-006 | T01.03 | D-0003 | STRICT | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0003/ |
| R-007 | T01.04 | D-0004 | STRICT | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0004/ |
| R-009 | T02.01 | D-0005 | STRICT | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0005/ |
| R-010 | T02.02 | D-0006 | STRICT | 85% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0006/ |
| R-011 | T02.03 | D-0007 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0007/ |
| R-012 | T02.04 | D-0008 | STRICT | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0008/ |
| R-013 | T02.05 | D-0009 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0009/ |
| R-014 | T02.06 | D-0010 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0010/ |
| R-016 | T03.01 | D-0011 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0011/ |
| R-017 | T03.02 | D-0012 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0012/ |
| R-018 | T03.03 | D-0013 | STANDARD | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0013/ |
| R-020 | T04.01 | D-0014 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0014/ |
| R-021 | T04.02 | D-0015 | STRICT | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0015/ |
| R-022 | T04.03 | D-0016 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0016/ |
| R-023 | T04.04 | D-0017 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0017/ |
| R-024 | T04.05 | D-0018 | STANDARD | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0018/ |
| R-026 | T05.01 | D-0019 | STRICT | 85% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0019/ |
| R-027 | T05.02 | D-0020 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0020/ |
| R-028 | T05.03 | D-0021 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0021/ |
| R-029 | T05.04 | D-0022 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0022/ |
| R-030 | T05.05 | D-0023 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0023/ |
| R-032 | T06.01 | D-0024 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0024/ |
| R-033 | T06.02 | D-0025 | STRICT | 85% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0025/ |
| R-034 | T06.03 | D-0026 | STANDARD | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0026/ |
| R-036 | T07.01 | D-0027 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0027/ |
| R-037 | T07.02 | D-0028 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0028/ |
| R-038 | T07.03 | D-0029 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0029/ |
| R-039 | T07.04 | D-0030 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0030/ |
| R-040 | T07.05 | D-0031 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0031/ |
| R-041 | T07.06 | D-0032 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0032/ |
| R-042 | T07.07 | D-0033 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0033/ |
| R-044 | T08.01 | D-0034 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0034/ |
| R-045 | T08.02 | D-0035 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0035/ |
| R-046 | T08.03 | D-0036 | STANDARD | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0036/ |
| R-047 | T08.04 | D-0037 | STANDARD | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0037/ |
| R-049 | T09.01 | D-0038 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0038/ |
| R-050 | T09.02 | D-0039 | STRICT | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0039/ |
| R-051 | T09.03 | D-0040 | STANDARD | 80% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0040/ |
| R-052 | T09.04 | D-0041 | STANDARD | 75% | .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0041/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| (to be filled during execution) | | | | | | | |

## Checkpoint Report Template

**Template:**

```markdown
# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>

## Status
Overall: Pass | Fail | TBD

## Verification Results
- (aligned to checkpoint Verification bullets)
- ...
- ...

## Exit Criteria Assessment
- (aligned to checkpoint Exit Criteria bullets)
- ...
- ...

## Issues & Follow-ups
- (list blocking issues; reference T<PP>.<TT> and D-####)

## Evidence
- (intended evidence paths under .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/evidence/)
```

## Feedback Collection Template

**Intended Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| (to be filled during execution) | | | | | | |

## Generation Notes

- Phase bucketing used explicit milestone headings (M1-M6, V1-V3) from roadmap, mapped to 9 sequential phases
- No clarification tasks needed: all deliverables have sufficient specificity from the roadmap
- No task splits applied: each deliverable maps to exactly one task
- Tier classification relies heavily on STRICT due to model/schema/system-wide/multi-file keywords present in most implementation tasks
- Validation milestone tasks (V1, V2, V3) classified as STANDARD since they implement tests, not modify production code
- Risk register items (R-001 through R-016) inform risk labels but are not themselves tasks
- Success criteria (SC-001 through SC-007) inform acceptance criteria but are not themselves tasks
