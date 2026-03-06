# TASKLIST INDEX -- v2.14 Sprint Report Scaffolding

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.14 Sprint Report Scaffolding |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-06 |
| TASKLIST_ROOT | `.dev/releases/backlog/v2.14-SprintReportScaffolding/tasklist/` |
| Total Phases | 3 |
| Total Tasks | 11 |
| Total Deliverables | 11 |
| Complexity Class | LOW |
| Primary Persona | backend |
| Consulting Personas | qa, refactorer |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| Phase 3 Tasklist | `TASKLIST_ROOT/phase-3-tasklist.md` |
| Execution Log | `TASKLIST_ROOT/execution-log.md` |
| Checkpoint Reports | `TASKLIST_ROOT/checkpoints/` |
| Evidence Directory | `TASKLIST_ROOT/evidence/` |
| Artifacts Directory | `TASKLIST_ROOT/artifacts/` |
| Feedback Log | `TASKLIST_ROOT/feedback-log.md` |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Parser and Scaffold Module | T01.01-T01.04 | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| 2 | phase-2-tasklist.md | Executor Integration and Prompt | T02.01-T02.03 | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 3 | phase-3-tasklist.md | Tests and Validation | T03.01-T03.04 | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |

## Source Snapshot

- v2.14 addresses the lost-report problem: 3 of 5 phases in a recent sprint finished as `pass_no_report` due to `max_turns` exhaustion
- Two-layer defense: Layer 1 (deterministic scaffold) + Layer 2 (incremental prompt updates)
- No changes to `_determine_phase_status()`, `PhaseStatus`, or status classification logic
- Scaffold maps to existing `PASS_NO_SIGNAL` status (`is_success=True`)
- All work sequenced after v2.13 M1 (characterization tests must exist first)
- Scope: `src/superclaude/cli/sprint/` — 3 files modified, 2 new files created

## Deterministic Rules Applied

- Phase buckets derived from roadmap milestone headings (M1, M2, M3) → Phase 1, 2, 3
- Phase numbering sequential with no gaps (1, 2, 3)
- Task IDs: `T<PP>.<TT>` zero-padded format (T01.01 through T03.04)
- Checkpoint cadence: end-of-phase only (all phases have <5 tasks)
- No clarification tasks needed (spec provides complete interface definitions, acceptance criteria, and code examples)
- Deliverable IDs: `D-0001` through `D-0011` in task appearance order
- Effort computed from roadmap text length + keyword matching per deterministic algorithm
- Risk computed from keyword matching (security, migration, cross-cutting scope keywords)
- Tier classification: all tasks classified STANDARD (implementation tasks, single-file scope, no security/auth paths)
- Verification routing: all STANDARD → direct test execution (300-500 tokens, 30s timeout)
- MCP requirements: all STANDARD → preferred Sequential + Context7, fallback allowed
- Multi-file output: 1 index + 3 phase files

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | Create a self-contained scaffold.py module that can parse task metadata from phase tasklist files |
| R-002 | Phase 1 | TaskMeta dataclass in scaffold.py — Fields: id, title, tier. Tier defaults to UNKNOWN |
| R-003 | Phase 1 | parse_phase_tasks() function — Extracts task ID, title, tier from headings and metadata rows |
| R-004 | Phase 1 | SCAFFOLD_TEMPLATE constant — Template string with YAML frontmatter, no status field, no EXIT_RECOMMENDATION |
| R-005 | Phase 1 | scaffold_result_file() function — Creates scaffold at specified path, creates parent dirs, overwrites existing |
| R-006 | Phase 2 | Wire the scaffold module into the sprint execution pipeline at the correct lifecycle |
| R-007 | Phase 2 | Scaffold call in execute_sprint() between ClaudeProcess construction and proc_manager.start() |
| R-008 | Phase 2 | Graceful degradation on scaffold failure — try/except, logged to debug_log and stderr |
| R-009 | Phase 2 | Replace Completion Protocol with Reporting Protocol — scaffold report already exists, incremental updates |
| R-010 | Phase 2 | Prompt references correct result file path returned by config.result_file(phase) |
| R-011 | Phase 3 | Comprehensive test coverage for scaffold lifecycle: parsing, creation, status classification, integration |
| R-012 | Phase 3 | TestParsePhaseTasks class — 5 tests covering ID/title/tier extraction, edge cases, real fixture |
| R-013 | Phase 3 | TestScaffoldResultFile class — 7 tests covering file creation, YAML, task table, parent dirs |
| R-014 | Phase 3 | TestScaffoldStatusClassification + TestScaffoldPrimaryScenario — 6 tests covering status mapping |
| R-015 | Phase 3 | Prompt content tests in test_process.py + full regression suite verification |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-002 | `TaskMeta` dataclass with id, title, tier fields | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0001/evidence.md` | XS | Low |
| D-0002 | T01.02 | R-003 | `parse_phase_tasks()` regex-based parser function | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0002/evidence.md` | S | Low |
| D-0003 | T01.03 | R-004 | `SCAFFOLD_TEMPLATE` format constant | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0003/evidence.md` | XS | Low |
| D-0004 | T01.04 | R-005 | `scaffold_result_file()` creation function | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` | XS | Low |
| D-0005 | T02.01 | R-007 | Scaffold call site in `execute_sprint()` | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0005/evidence.md` | XS | Low |
| D-0006 | T02.02 | R-008 | Graceful degradation error handling | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0006/evidence.md` | XS | Low |
| D-0007 | T02.03 | R-009, R-010 | Reporting Protocol prompt section | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0007/evidence.md` | S | Low |
| D-0008 | T03.01 | R-012 | `TestParsePhaseTasks` class (5 tests) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0008/evidence.md` | XS | Low |
| D-0009 | T03.02 | R-013 | `TestScaffoldResultFile` class (7 tests) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0009/evidence.md` | XS | Low |
| D-0010 | T03.03 | R-014 | `TestScaffoldStatusClassification` + primary scenario (6 tests) | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0010/evidence.md` | XS | Low |
| D-0011 | T03.04 | R-015 | Prompt content tests (3 tests) + regression pass | STANDARD | Direct test | `TASKLIST_ROOT/artifacts/D-0011/evidence.md` | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01, T01.02, T01.03, T01.04 | D-0001, D-0002, D-0003, D-0004 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0001/` through `D-0004/` |
| R-002 | T01.01 | D-0001 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0001/evidence.md` |
| R-003 | T01.02 | D-0002 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0002/evidence.md` |
| R-004 | T01.03 | D-0003 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0003/evidence.md` |
| R-005 | T01.04 | D-0004 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` |
| R-006 | T02.01, T02.02, T02.03 | D-0005, D-0006, D-0007 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0005/` through `D-0007/` |
| R-007 | T02.01 | D-0005 | STANDARD | 80% | `TASKLIST_ROOT/artifacts/D-0005/evidence.md` |
| R-008 | T02.02 | D-0006 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0006/evidence.md` |
| R-009 | T02.03 | D-0007 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0007/evidence.md` |
| R-010 | T02.03 | D-0007 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0007/evidence.md` |
| R-011 | T03.01, T03.02, T03.03, T03.04 | D-0008, D-0009, D-0010, D-0011 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0008/` through `D-0011/` |
| R-012 | T03.01 | D-0008 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0008/evidence.md` |
| R-013 | T03.02 | D-0009 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0009/evidence.md` |
| R-014 | T03.03 | D-0010 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0010/evidence.md` |
| R-015 | T03.04 | D-0011 | STANDARD | 85% | `TASKLIST_ROOT/artifacts/D-0011/evidence.md` |

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | T01.01 | STANDARD | D-0001 | | `uv run pytest tests/sprint/test_scaffold.py -v` | TBD | `TASKLIST_ROOT/evidence/` |

## Checkpoint Report Template

# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
**Scope:** <tasks covered>

## Status
- Overall: Pass | Fail | TBD

## Verification Results
- (exactly 3 bullets aligned to checkpoint verification)

## Exit Criteria Assessment
- (exactly 3 bullets aligned to checkpoint exit criteria)

## Issues & Follow-ups
- Reference `T<PP>.<TT>` and `D-####` for any blocking issues

## Evidence
- `TASKLIST_ROOT/evidence/<task-specific-path>`

## Feedback Collection Template

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| T01.01 | STANDARD | | | | | |
| T01.02 | STANDARD | | | | | |
| T01.03 | STANDARD | | | | | |
| T01.04 | STANDARD | | | | | |
| T02.01 | STANDARD | | | | | |
| T02.02 | STANDARD | | | | | |
| T02.03 | STANDARD | | | | | |
| T03.01 | STANDARD | | | | | |
| T03.02 | STANDARD | | | | | |
| T03.03 | STANDARD | | | | | |
| T03.04 | STANDARD | | | | | |

## Generation Notes

- All tasks classified STANDARD: no security/auth/crypto paths, no database migrations, all single-file scope per task
- Phase 1 depends on external v2.13 M1 (characterization tests) — this is not tracked as a task but as a blocking prerequisite
- D2.3 and D2.4 from the roadmap were combined into T02.03 (both modify `build_prompt()` in the same code section)
- Effort scores are low (XS-S) because individual tasks are focused single-concern changes; the roadmap's overall "S" effort per milestone distributes across multiple small tasks
- No clarification tasks generated: the release spec provides complete Python interfaces, regex patterns, acceptance criteria, and integration code examples
