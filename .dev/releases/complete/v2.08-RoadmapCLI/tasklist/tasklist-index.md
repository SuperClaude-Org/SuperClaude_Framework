# TASKLIST INDEX -- superclaude roadmap CLI Command

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | `superclaude roadmap CLI Command` |
| Generator Version | `Roadmap->Tasklist Generator v3.0` |
| Generated | `2026-03-05` |
| TASKLIST_ROOT | `.dev/releases/current/v2.08-RoadmapCLI/tasklist/` |
| Total Phases | `5` |
| Total Tasks | `33` |
| Total Deliverables | `33` |
| Complexity Class | `MEDIUM` |
| Primary Persona | `architect` |
| Consulting Personas | `backend` |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| Phase 3 Tasklist | `TASKLIST_ROOT/phase-3-tasklist.md` |
| Phase 4 Tasklist | `TASKLIST_ROOT/phase-4-tasklist.md` |
| Phase 5 Tasklist | `TASKLIST_ROOT/phase-5-tasklist.md` |
| Execution Log | `TASKLIST_ROOT/execution-log.md` |
| Checkpoint Reports | `TASKLIST_ROOT/checkpoints/` |
| Evidence Directory | `TASKLIST_ROOT/evidence/` |
| Artifacts Directory | `TASKLIST_ROOT/artifacts/` |
| Feedback Log | `TASKLIST_ROOT/feedback-log.md` |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation: Pipeline Module | T01.01-T01.07 | STRICT: 4, STANDARD: 3 |
| 2 | phase-2-tasklist.md | Sprint Migration to Pipeline | T02.01-T02.04 | STRICT: 3, STANDARD: 1 |
| 3 | phase-3-tasklist.md | Roadmap Command Implementation | T03.01-T03.10 | STRICT: 7, STANDARD: 3 |
| 4 | phase-4-tasklist.md | CLI Interface & UX | T04.01-T04.07 | STRICT: 4, STANDARD: 3 |
| 5 | phase-5-tasklist.md | Validation & Acceptance Testing | T05.01-T05.05 | STRICT: 2, STANDARD: 3 |

## Source Snapshot

- Implementation of `superclaude roadmap` CLI command as external conductor calling Claude as subprocess per pipeline step
- Bottom-up architecture: extract shared `pipeline/` module from `sprint/`, migrate sprint, build `roadmap/` on top
- Composition via callable `StepRunner` injection rather than inheritance or template method
- 8-step pipeline with context isolation, parallel generate steps, gate enforcement, retry-then-halt failure policy
- 5 milestones, 33 deliverables, dependency graph M1→M2→M5 and M1→M3→M4→M5
- 6 identified risks; highest: Claude subprocess non-conforming output (R-002, High probability)

## Deterministic Rules Applied

- Phase bucketing: milestones M1-M5 mapped to Phases 1-5 in dependency order (M1→M2→M3→M4→M5)
- Phase numbering: contiguous 1-5 with no gaps
- Task IDs: `T<PP>.<TT>` zero-padded format, one task per deliverable (no splits needed)
- Checkpoint cadence: after every 5 tasks within a phase, plus end-of-phase checkpoint
- Clarification tasks: none required (roadmap is fully specified with concrete acceptance criteria)
- Deliverable registry: D-0001 through D-0033 in task order
- Effort scoring: deterministic keyword-based EFFORT_SCORE mapping (Section 5.2.1)
- Risk scoring: deterministic keyword-based RISK_SCORE mapping (Section 5.2.2)
- Tier classification: keyword matching + context boosters per Section 5.3
- Verification routing: tier-proportional method assignment per Section 4.10
- MCP requirements: tier-based tool dependency declaration per Section 5.5
- Multi-file output: index + 5 phase files, Sprint CLI compatible

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | `pipeline/models.py` — `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `SemanticCheck` dataclasses |
| R-002 | Phase 1 | `pipeline/gates.py` — `gate_passed()` function |
| R-003 | Phase 1 | `pipeline/executor.py` — `execute_pipeline()` generic executor |
| R-004 | Phase 1 | `pipeline/process.py` — `ClaudeProcess` moved from sprint |
| R-005 | Phase 1 | `pipeline/_run_parallel_steps()` — parallel step execution |
| R-006 | Phase 1 | `pipeline/__init__.py` — public API exports |
| R-007 | Phase 1 | `tests/pipeline/` — unit test suite |
| R-008 | Phase 2 | `sprint/config.py` — `SprintConfig` inherits from `PipelineConfig` |
| R-009 | Phase 2 | `sprint/models.py` — types inherit from pipeline models |
| R-010 | Phase 2 | `sprint/process.py` — re-exports `ClaudeProcess` from `pipeline.process` |
| R-011 | Phase 2 | Sprint regression validation |
| R-012 | Phase 3 | `roadmap/commands.py` — Click CLI entry point |
| R-013 | Phase 3 | `roadmap/models.py` — `RoadmapConfig` extends `PipelineConfig`; `AgentSpec` dataclass |
| R-014 | Phase 3 | `roadmap/prompts.py` — 7 prompt builder pure functions |
| R-015 | Phase 3 | `roadmap/gates.py` — gate criteria definitions as data |
| R-016 | Phase 3 | `roadmap/executor.py` — `execute_roadmap()` wrapping `execute_pipeline()` |
| R-017 | Phase 3 | Parallel generate implementation |
| R-018 | Phase 3 | Context isolation enforcement |
| R-019 | Phase 3 | Gate enforcement integration |
| R-020 | Phase 3 | Failure policy: retry-then-halt |
| R-021 | Phase 3 | Semantic checks for STRICT-tier steps |
| R-022 | Phase 4 | `--resume` implementation |
| R-023 | Phase 4 | `--dry-run` implementation |
| R-024 | Phase 4 | Progress display |
| R-025 | Phase 4 | `.roadmap-state.json` management |
| R-026 | Phase 4 | HALT output formatting |
| R-027 | Phase 4 | Depth-to-prompt mapping |
| R-028 | Phase 4 | `--agents` parsing and model routing |
| R-029 | Phase 5 | `tests/pipeline/` test suite |
| R-030 | Phase 5 | `tests/roadmap/` test suite |
| R-031 | Phase 5 | Sprint regression verification |
| R-032 | Phase 5 | Acceptance criteria validation |
| R-033 | Phase 5 | NFR compliance verification |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | `pipeline/models.py` dataclasses | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0001/spec.md`, `TASKLIST_ROOT/artifacts/D-0001/evidence.md` | M | Medium |
| D-0002 | T01.02 | R-002 | `pipeline/gates.py` gate_passed() function | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0002/spec.md`, `TASKLIST_ROOT/artifacts/D-0002/evidence.md` | M | Medium |
| D-0003 | T01.03 | R-003 | `pipeline/executor.py` generic executor | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0003/spec.md`, `TASKLIST_ROOT/artifacts/D-0003/evidence.md` | L | Medium |
| D-0004 | T01.04 | R-004 | `pipeline/process.py` ClaudeProcess extraction | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0004/spec.md`, `TASKLIST_ROOT/artifacts/D-0004/evidence.md` | M | Medium |
| D-0005 | T01.05 | R-005 | `pipeline/_run_parallel_steps()` parallel dispatch | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0005/spec.md`, `TASKLIST_ROOT/artifacts/D-0005/evidence.md` | M | Medium |
| D-0006 | T01.06 | R-006 | `pipeline/__init__.py` public API | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0006/spec.md`, `TASKLIST_ROOT/artifacts/D-0006/evidence.md` | S | Low |
| D-0007 | T01.07 | R-007 | `tests/pipeline/` unit test suite | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0007/spec.md`, `TASKLIST_ROOT/artifacts/D-0007/evidence.md` | M | Low |
| D-0008 | T02.01 | R-008 | `sprint/config.py` SprintConfig inherits PipelineConfig | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0008/spec.md`, `TASKLIST_ROOT/artifacts/D-0008/evidence.md` | M | Medium |
| D-0009 | T02.02 | R-009 | `sprint/models.py` types inherit pipeline models | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0009/spec.md`, `TASKLIST_ROOT/artifacts/D-0009/evidence.md` | M | Medium |
| D-0010 | T02.03 | R-010 | `sprint/process.py` re-exports ClaudeProcess | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0010/spec.md`, `TASKLIST_ROOT/artifacts/D-0010/evidence.md` | S | Medium |
| D-0011 | T02.04 | R-011 | Sprint regression validation (all sprint test files pass; no modifications during migration) | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0011/spec.md`, `TASKLIST_ROOT/artifacts/D-0011/evidence.md` | S | Medium |
| D-0012 | T03.01 | R-012 | `roadmap/commands.py` Click CLI entry point | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0012/spec.md`, `TASKLIST_ROOT/artifacts/D-0012/evidence.md` | L | Medium |
| D-0013 | T03.02 | R-013 | `roadmap/models.py` RoadmapConfig and AgentSpec | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0013/spec.md`, `TASKLIST_ROOT/artifacts/D-0013/evidence.md` | M | Low |
| D-0014 | T03.03 | R-014 | `roadmap/prompts.py` 7 prompt builder functions | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0014/spec.md`, `TASKLIST_ROOT/artifacts/D-0014/evidence.md` | M | Low |
| D-0015 | T03.04 | R-015 | `roadmap/gates.py` gate criteria data definitions | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0015/spec.md`, `TASKLIST_ROOT/artifacts/D-0015/evidence.md` | M | Medium |
| D-0016 | T03.05 | R-016 | `roadmap/executor.py` execute_roadmap() | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0016/spec.md`, `TASKLIST_ROOT/artifacts/D-0016/evidence.md` | L | Medium |
| D-0017 | T03.06 | R-017 | Parallel generate-A/generate-B step execution | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0017/spec.md`, `TASKLIST_ROOT/artifacts/D-0017/evidence.md` | M | High |
| D-0018 | T03.07 | R-018 | Context isolation per subprocess | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0018/spec.md`, `TASKLIST_ROOT/artifacts/D-0018/evidence.md` | M | Medium |
| D-0019 | T03.08 | R-019 | Gate enforcement after each subprocess | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0019/spec.md`, `TASKLIST_ROOT/artifacts/D-0019/evidence.md` | M | Medium |
| D-0020 | T03.09 | R-020 | Retry-then-halt failure policy | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0020/spec.md`, `TASKLIST_ROOT/artifacts/D-0020/evidence.md` | M | Medium |
| D-0021 | T03.10 | R-021 | Semantic checks for STRICT-tier steps | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0021/spec.md`, `TASKLIST_ROOT/artifacts/D-0021/evidence.md` | M | Medium |
| D-0022 | T04.01 | R-022 | `--resume` with stale spec detection | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0022/spec.md`, `TASKLIST_ROOT/artifacts/D-0022/evidence.md` | L | Medium |
| D-0023 | T04.02 | R-023 | `--dry-run` preview output | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0023/spec.md`, `TASKLIST_ROOT/artifacts/D-0023/evidence.md` | S | Low |
| D-0024 | T04.03 | R-024 | Progress display with 5s update interval | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0024/spec.md`, `TASKLIST_ROOT/artifacts/D-0024/evidence.md` | M | Low |
| D-0025 | T04.04 | R-025 | `.roadmap-state.json` atomic state management | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0025/spec.md`, `TASKLIST_ROOT/artifacts/D-0025/evidence.md` | M | Medium |
| D-0026 | T04.05 | R-026 | HALT output formatting to stderr | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0026/spec.md`, `TASKLIST_ROOT/artifacts/D-0026/evidence.md` | S | Low |
| D-0027 | T04.06 | R-027 | Depth-to-prompt mapping (quick/standard/deep) | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0027/spec.md`, `TASKLIST_ROOT/artifacts/D-0027/evidence.md` | S | Low |
| D-0028 | T04.07 | R-028 | `--agents` model:persona parsing and routing | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0028/spec.md`, `TASKLIST_ROOT/artifacts/D-0028/evidence.md` | M | Low |
| D-0029 | T05.01 | R-029 | `tests/pipeline/` comprehensive test suite | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0029/spec.md`, `TASKLIST_ROOT/artifacts/D-0029/evidence.md` | M | Low |
| D-0030 | T05.02 | R-030 | `tests/roadmap/` comprehensive test suite | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0030/spec.md`, `TASKLIST_ROOT/artifacts/D-0030/evidence.md` | L | Low |
| D-0031 | T05.03 | R-031 | Sprint regression (all sprint test files pass unmodified during pipeline/ migration) | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0031/spec.md`, `TASKLIST_ROOT/artifacts/D-0031/evidence.md` | S | Medium |
| D-0032 | T05.04 | R-032 | Acceptance criteria AC-01,03,04,05,07 via CliRunner | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0032/spec.md`, `TASKLIST_ROOT/artifacts/D-0032/evidence.md` | M | Low |
| D-0033 | T05.05 | R-033 | NFR-003,004,005,006,007 compliance verification | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0033/spec.md`, `TASKLIST_ROOT/artifacts/D-0033/evidence.md` | M | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0001/` |
| R-002 | T01.02 | D-0002 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0002/` |
| R-003 | T01.03 | D-0003 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0003/` |
| R-004 | T01.04 | D-0004 | STRICT | 80% | `TASKLIST_ROOT/artifacts/D-0004/` |
| R-005 | T01.05 | D-0005 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0005/` |
| R-006 | T01.06 | D-0006 | STANDARD | 75% | `TASKLIST_ROOT/artifacts/D-0006/` |
| R-007 | T01.07 | D-0007 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0007/` |
| R-008 | T02.01 | D-0008 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0008/` |
| R-009 | T02.02 | D-0009 | STRICT | 80% | `TASKLIST_ROOT/artifacts/D-0009/` |
| R-010 | T02.03 | D-0010 | STRICT | 80% | `TASKLIST_ROOT/artifacts/D-0010/` |
| R-011 | T02.04 | D-0011 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0011/` |
| R-012 | T03.01 | D-0012 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0012/` |
| R-013 | T03.02 | D-0013 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0013/` |
| R-014 | T03.03 | D-0014 | STANDARD | 75% | `TASKLIST_ROOT/artifacts/D-0014/` |
| R-015 | T03.04 | D-0015 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0015/` |
| R-016 | T03.05 | D-0016 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0016/` |
| R-017 | T03.06 | D-0017 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0017/` |
| R-018 | T03.07 | D-0018 | STRICT | 80% | `TASKLIST_ROOT/artifacts/D-0018/` |
| R-019 | T03.08 | D-0019 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0019/` |
| R-020 | T03.09 | D-0020 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0020/` |
| R-021 | T03.10 | D-0021 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0021/` |
| R-022 | T04.01 | D-0022 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0022/` |
| R-023 | T04.02 | D-0023 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0023/` |
| R-024 | T04.03 | D-0024 | STANDARD | 75% | `TASKLIST_ROOT/artifacts/D-0024/` |
| R-025 | T04.04 | D-0025 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0025/` |
| R-026 | T04.05 | D-0026 | STANDARD | 75% | `TASKLIST_ROOT/artifacts/D-0026/` |
| R-027 | T04.06 | D-0027 | STRICT | 80% | `TASKLIST_ROOT/artifacts/D-0027/` |
| R-028 | T04.07 | D-0028 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0028/` |
| R-029 | T05.01 | D-0029 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0029/` |
| R-030 | T05.02 | D-0030 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0030/` |
| R-031 | T05.03 | D-0031 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0031/` |
| R-032 | T05.04 | D-0032 | STRICT | 85% | `TASKLIST_ROOT/artifacts/D-0032/` |
| R-033 | T05.05 | D-0033 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0033/` |

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
**Scope:** <tasks covered>

## Status
- Overall: Pass | Fail | TBD

## Verification Results
- <bullet 1>
- <bullet 2>
- <bullet 3>

## Exit Criteria Assessment
- <bullet 1>
- <bullet 2>
- <bullet 3>

## Issues & Follow-ups
- List blocking issues; reference `T<PP>.<TT>` and `D-####`

## Evidence
- `TASKLIST_ROOT/evidence/<relevant-file>`

## Feedback Collection Template

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- Phase bucketing derived from explicit milestone headings M1-M5 in roadmap
- All 33 deliverables mapped 1:1 to tasks (no splits required; each deliverable is independently deliverable)
- No clarification tasks needed: roadmap provides concrete acceptance criteria for all deliverables
- TASKLIST_ROOT derived from roadmap path segment `v2.08-RoadmapCLI`
- Tier classification skewed toward STRICT due to multi-file scope, database/model/schema keywords, and refactoring patterns throughout
- Risk register items R-001 through R-006 from roadmap incorporated into task risk drivers
