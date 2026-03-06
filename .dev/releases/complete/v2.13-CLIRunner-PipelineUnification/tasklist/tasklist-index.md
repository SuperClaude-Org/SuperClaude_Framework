# TASKLIST INDEX -- v2.13 CLIRunner Pipeline Targeted Fixes

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.13 CLIRunner Pipeline Targeted Fixes |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-05T00:00:00Z |
| TASKLIST_ROOT | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/tasklist/ |
| Total Phases | 4 |
| Total Tasks | 20 |
| Total Deliverables | 20 |
| Complexity Class | LOW |
| Primary Persona | refactorer |
| Consulting Personas | architect, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | TASKLIST_ROOT/tasklist-index.md |
| Phase 1 Tasklist | TASKLIST_ROOT/phase-1-tasklist.md |
| Phase 2 Tasklist | TASKLIST_ROOT/phase-2-tasklist.md |
| Phase 3 Tasklist | TASKLIST_ROOT/phase-3-tasklist.md |
| Phase 4 Tasklist | TASKLIST_ROOT/phase-4-tasklist.md |
| Execution Log | TASKLIST_ROOT/execution-log.md |
| Checkpoint Reports | TASKLIST_ROOT/checkpoints/ |
| Evidence Directory | TASKLIST_ROOT/evidence/ |
| Artifacts Directory | TASKLIST_ROOT/artifacts/ |
| Feedback Log | TASKLIST_ROOT/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Sprint Executor Characterization Tests | T01.01-T01.04 | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| 2 | phase-2-tasklist.md | Process Duplication Elimination | T02.01-T02.07 | STRICT: 3, STANDARD: 3, LIGHT: 0, EXEMPT: 1 |
| 3 | phase-3-tasklist.md | Roadmap File-Passing Fix | T03.01-T03.03 | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 4 | phase-4-tasklist.md | Validation and Acceptance | T04.01-T04.06 | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 6 |

## Source Snapshot

- Implements Option 3 (Targeted Fixes) from adversarial-debated pipeline architecture decision (convergence 0.72)
- Test-first strategy: characterization tests before refactoring, establishing safety net for hook migration
- Refactoring split into 3 independent sub-steps: wait deletion, hook migration, dead code removal
- Executor-level unification is an explicit non-goal; deferred as hypothesis for future validation
- Critical path: M1 (Tests) -> M2 (Hooks + Dead Code) -> M3 (File-Passing) -> M4 (Validation)
- 5 risks identified; highest impact: hook refactor breaking SIGTERM/SIGKILL escalation (Low probability, High impact)

## Deterministic Rules Applied

- Phase buckets derived from roadmap milestone headings (M1-M4), mapped to Phase 1-4 in appearance order
- Phase numbering already contiguous; no renumbering required
- Task IDs assigned as T<PP>.<TT> with zero-padded 2-digit format
- 1:1 mapping from roadmap deliverables to tasks (no splits required; each deliverable is independently deliverable)
- Checkpoint cadence: every 5 tasks within a phase, plus mandatory end-of-phase checkpoint
- Clarification tasks: none required (all deliverables have sufficient specificity)
- Deliverable registry: D-0001 through D-0020, sequential by task order
- Effort scores computed via keyword matching and text length thresholds per Section 5.2.1
- Risk scores computed via keyword matching per Section 5.2.2
- Tier classification via compound phrase check, keyword scoring, and context boosters per Section 5.3
- Verification routing: STRICT -> sub-agent, STANDARD -> direct test, EXEMPT -> skip per Section 4.10
- Multi-file output: 1 index + 4 phase files

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | Watchdog/stall detection tests (3 cases: kill action, warn action, reset on resume) |
| R-002 | Phase 1 | Multi-phase sequencing tests (2 cases: 3-phase happy path, halt at phase 3) |
| R-003 | Phase 1 | TUI/monitor/tmux integration tests (4 cases: TUI updates, TUI error resilience, monitor lifecycle, tmux tail pane) |
| R-004 | Phase 1 | Diagnostics tests (2 cases: failure triggers collector, collection failure is non-fatal) |
| R-005 | Phase 2 | M2a: Delete sprint's wait() override (pure no-op duplication) |
| R-006 | Phase 2 | M2b-base: Add on_spawn, on_signal, on_exit hook params to pipeline ClaudeProcess.__init__ |
| R-007 | Phase 2 | M2b-base: Add on_exit call to wait() success path |
| R-008 | Phase 2 | M2b-migrate: Add hook factory functions to sprint/process.py (_make_spawn_hook, _make_signal_hook, _make_exit_hook) |
| R-009 | Phase 2 | M2b-migrate: Wire hooks in sprint ClaudeProcess.__init__ and delete start(), terminate() overrides |
| R-010 | Phase 2 | M2b-migrate: Verify NFR-007 compliance |
| R-011 | Phase 2 | M2c: Delete _FORBIDDEN_FLAGS and _build_subprocess_argv from roadmap/executor.py |
| R-012 | Phase 3 | Add _embed_inputs() helper to roadmap/executor.py |
| R-013 | Phase 3 | Modify roadmap_run_step() to use inline embedding with 100KB size guard |
| R-014 | Phase 3 | Integration test for file-passing |
| R-015 | Phase 4 | Full test suite passes (zero regressions) |
| R-016 | Phase 4 | Sprint executor coverage >= 70% |
| R-017 | Phase 4 | Net lines removed >= 58 from sprint/process.py |
| R-018 | Phase 4 | Dead code lines removed >= 25 from roadmap/executor.py |
| R-019 | Phase 4 | NFR-007 zero violations |
| R-020 | Phase 4 | No new Python package dependencies (NFR-004) |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Watchdog/stall detection test suite (3 cases) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0001/evidence.md | S | Low |
| D-0002 | T01.02 | R-002 | Multi-phase sequencing test suite (2 cases) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0002/evidence.md | XS | Low |
| D-0003 | T01.03 | R-003 | TUI/monitor/tmux integration test suite (4 cases) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0003/evidence.md | S | Low |
| D-0004 | T01.04 | R-004 | Diagnostics test suite (2 cases) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0004/evidence.md | XS | Low |
| D-0005 | T02.01 | R-005 | Sprint wait() override deleted | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0005/evidence.md | XS | Low |
| D-0006 | T02.02 | R-006 | on_spawn/on_signal/on_exit hook params in pipeline ClaudeProcess.__init__ | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0006/spec.md, TASKLIST_ROOT/artifacts/D-0006/evidence.md | S | Low |
| D-0007 | T02.03 | R-007 | on_exit call in wait() success path | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0007/spec.md, TASKLIST_ROOT/artifacts/D-0007/evidence.md | XS | Low |
| D-0008 | T02.04 | R-008 | Hook factory functions in sprint/process.py | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0008/evidence.md | S | Low |
| D-0009 | T02.05 | R-009 | Sprint ClaudeProcess reduced to __init__ + build_prompt | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0009/spec.md, TASKLIST_ROOT/artifacts/D-0009/evidence.md | S | Medium |
| D-0010 | T02.06 | R-010 | NFR-007 compliance verification result | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0010/evidence.md | XS | Low |
| D-0011 | T02.07 | R-011 | _FORBIDDEN_FLAGS and _build_subprocess_argv deleted from roadmap/executor.py | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0011/evidence.md | XS | Low |
| D-0012 | T03.01 | R-012 | _embed_inputs() helper in roadmap/executor.py | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0012/evidence.md | XS | Low |
| D-0013 | T03.02 | R-013 | roadmap_run_step() inline embedding with 100KB size guard | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0013/evidence.md | S | Low |
| D-0014 | T03.03 | R-014 | Integration test for file-passing (3 scenarios) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0014/evidence.md | S | Low |
| D-0015 | T04.01 | R-015 | Full test suite green confirmation | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0015/evidence.md | XS | Low |
| D-0016 | T04.02 | R-016 | Sprint executor coverage report >= 70% | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0016/evidence.md | XS | Low |
| D-0017 | T04.03 | R-017 | git diff --stat confirming >= 58 lines removed from sprint/process.py | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0017/evidence.md | XS | Low |
| D-0018 | T04.04 | R-018 | git diff --stat confirming >= 25 lines removed from roadmap/executor.py | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0018/evidence.md | XS | Low |
| D-0019 | T04.05 | R-019 | NFR-007 grep returning 0 results | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0019/evidence.md | XS | Low |
| D-0020 | T04.06 | R-020 | pyproject.toml diff showing no new dependencies | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0020/evidence.md | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STANDARD | 85% | TASKLIST_ROOT/artifacts/D-0001/evidence.md |
| R-002 | T01.02 | D-0002 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0002/evidence.md |
| R-003 | T01.03 | D-0003 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0003/evidence.md |
| R-004 | T01.04 | D-0004 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0004/evidence.md |
| R-005 | T02.01 | D-0005 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0005/evidence.md |
| R-006 | T02.02 | D-0006 | STRICT | 80% | TASKLIST_ROOT/artifacts/D-0006/spec.md, TASKLIST_ROOT/artifacts/D-0006/evidence.md |
| R-007 | T02.03 | D-0007 | STRICT | 75% | TASKLIST_ROOT/artifacts/D-0007/spec.md, TASKLIST_ROOT/artifacts/D-0007/evidence.md |
| R-008 | T02.04 | D-0008 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0008/evidence.md |
| R-009 | T02.05 | D-0009 | STRICT | 85% | TASKLIST_ROOT/artifacts/D-0009/spec.md, TASKLIST_ROOT/artifacts/D-0009/evidence.md |
| R-010 | T02.06 | D-0010 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0010/evidence.md |
| R-011 | T02.07 | D-0011 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0011/evidence.md |
| R-012 | T03.01 | D-0012 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0012/evidence.md |
| R-013 | T03.02 | D-0013 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0013/evidence.md |
| R-014 | T03.03 | D-0014 | STANDARD | 80% | TASKLIST_ROOT/artifacts/D-0014/evidence.md |
| R-015 | T04.01 | D-0015 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0015/evidence.md |
| R-016 | T04.02 | D-0016 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0016/evidence.md |
| R-017 | T04.03 | D-0017 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0017/evidence.md |
| R-018 | T04.04 | D-0018 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0018/evidence.md |
| R-019 | T04.05 | D-0019 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0019/evidence.md |
| R-020 | T04.06 | D-0020 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0020/evidence.md |

## Execution Log Template

**Intended Path:** TASKLIST_ROOT/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md
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
- List blocking issues; reference T<PP>.<TT> and D-####

## Evidence
- Intended evidence paths under TASKLIST_ROOT/evidence/

## Feedback Collection Template

**Intended Path:** TASKLIST_ROOT/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- All 4 milestones mapped 1:1 to phases; no default bucketing required
- No clarification tasks needed; all deliverables have concrete acceptance criteria in roadmap
- No XL effort tasks; no subtask splitting required
- No circular dependencies detected; dependency chain is linear: Phase 1 -> Phase 2 -> Phase 3 -> Phase 4
- No critical path override triggered (no auth/, security/, crypto/ paths in task targets)
- Tier conflict on T02.05: "restructure" (STRICT) vs "delete" (STANDARD) -> resolved to STRICT by priority rule
