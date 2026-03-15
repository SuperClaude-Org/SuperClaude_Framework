# TASKLIST INDEX -- v2.24.5 CLI Bug Fixes (Tool Schema Discovery + Arg Too Long)

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.24.5 CLI Bug Fixes (Tool Schema Discovery + Arg Too Long) |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-15 |
| TASKLIST_ROOT | .dev/releases/current/v2.24.5/ |
| Total Phases | 7 |
| Total Tasks | 35 |
| Total Deliverables | 35 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | analyzer, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.24.5/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.24.5/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.24.5/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.24.5/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/v2.24.5/phase-4-tasklist.md |
| Phase 5 Tasklist | .dev/releases/current/v2.24.5/phase-5-tasklist.md |
| Phase 6 Tasklist | .dev/releases/current/v2.24.5/phase-6-tasklist.md |
| Phase 7 Tasklist | .dev/releases/current/v2.24.5/phase-7-tasklist.md |
| Execution Log | .dev/releases/current/v2.24.5/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.24.5/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.24.5/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.24.5/artifacts/ |
| Validation Reports | .dev/releases/current/v2.24.5/validation/ |
| Feedback Log | .dev/releases/current/v2.24.5/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Empirical Validation Gate | T01.01-T01.05 | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 5 |
| 2 | phase-2-tasklist.md | FIX-001 Add --tools default | T02.01-T02.06 | STRICT: 2, STANDARD: 3, LIGHT: 0, EXEMPT: 1 |
| 3 | phase-3-tasklist.md | FIX-ARG-TOO-LONG Constants and Guard | T03.01-T03.07 | STRICT: 4, STANDARD: 2, LIGHT: 0, EXEMPT: 1 |
| 4 | phase-4-tasklist.md | Rename Test Class | T04.01 | STRICT: 0, STANDARD: 0, LIGHT: 1, EXEMPT: 0 |
| 5 | phase-5-tasklist.md | Conditional --file Fallback | T05.01-T05.07 | STRICT: 4, STANDARD: 2, LIGHT: 0, EXEMPT: 1 |
| 6 | phase-6-tasklist.md | Integration Verification | T06.01-T06.03 | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 7 | phase-7-tasklist.md | Commit and Release | T07.01-T07.06 | STRICT: 0, STANDARD: 0, LIGHT: 0, EXEMPT: 6 |

## Source Snapshot

- Two independent bugs: FIX-001 (missing `--tools default` in `ClaudeProcess.build_command()`) and FIX-ARG-TOO-LONG (hardcoded 200 KB embed limit exceeds Linux 128 KB `MAX_ARG_STRLEN`)
- Phase 0 is a blocking empirical gate to determine `--file` CLI behavior (WORKING vs BROKEN)
- Phase 1.5 (conditional) activates only if Phase 0 result is BROKEN (~80% probability per roadmap)
- Scope: 6-7 source files, 2 test files; no new abstractions; within existing module boundaries
- Primary critical path: embed guard fix (active hard-crash `OSError`); secondary: `--tools default`
- Version ambiguity: roadmap uses v2.24.5 as working title pending confirmation against v2.25.1

## Deterministic Rules Applied

- Phase renumbering: roadmap phases 0, 1.1, 1.2, 1.3, 1.5, 2, 3 renumbered to contiguous 1-7
- Task IDs: T<PP>.<TT> format, zero-padded, 2-digit, assigned in roadmap appearance order
- Checkpoint cadence: after every 5 tasks within a phase, plus mandatory end-of-phase checkpoint
- Clarification tasks: none required (all tasks are fully specified in roadmap)
- Deliverable registry: D-0001 through D-0035, 1:1 with tasks
- Effort mapping: computed from text length, keywords (deploy, pipeline, auth, etc.), splits, dependencies
- Risk mapping: computed from security/migration/performance/cross-cutting keyword categories
- Tier classification: /sc:task-unified algorithm with compound phrase overrides, keyword scoring, context boosters
- Verification routing: STRICT->sub-agent, STANDARD->direct test, LIGHT->sanity check, EXEMPT->skip
- MCP requirements: STRICT tasks require Sequential+Serena; STANDARD prefer Sequential+Context7
- Traceability matrix: R-### -> T<PP>.<TT> -> D-#### with tier and confidence
- Multi-file output: 1 index + 7 phase files, Sprint CLI compatible

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Summary | FIX-001 (Tool Schema Discovery): `ClaudeProcess.build_command()` omits `--tools default`, causing subprocess invocations to lack tool access |
| R-002 | Summary | FIX-ARG-TOO-LONG: embed size guard uses hardcoded 200 KB limit that exceeds Linux kernel 128 KB |
| R-003 | Phase 1 | Verify `claude` CLI availability: `claude --print -p "hello" --max-turns 1` succeeds |
| R-004 | Phase 1 | Check `claude --help` for `--file` format: record whether `file_id:path` prefix is required |
| R-005 | Phase 1 | Execute empirical test: echo secret answer PINEAPPLE then test `claude --print --file` |
| R-006 | Phase 1 | Record result: WORKING (mentions PINEAPPLE), BROKEN (no mention), CLI FAILURE (non-zero exit) |
| R-007 | Phase 1 | Gate decision: WORKING skip Phase 1.5, BROKEN Phase 1.5 activates after Phase 1.2 |
| R-008 | Phase 2 | Verify no subclass overrides: read all `ClaudeProcess` subclasses, confirm none override `build_command()` without |
| R-009 | Phase 2 | Edit `process.py`: add `"--tools", "default"` after `--no-session-persistence` and before `--max-turns` in |
| R-010 | Phase 2 | Update `test_required_flags`: assert `--tools` and `default` present in command list |
| R-011 | Phase 2 | Update `test_stream_json_matches_sprint_flags`: assert `--tools` and `default` present |
| R-012 | Phase 2 | Add `test_tools_default_in_command`: assert adjacency `cmd[cmd.index("--tools") + 1] == "default"` |
| R-013 | Phase 2 | Run pipeline tests: `uv run pytest tests/pipeline/test_process.py -v` -- 0 failures |
| R-014 | Phase 3 | Replace constants in `executor.py`: remove `_EMBED_SIZE_LIMIT = 200 * 1024`, add three named constants |
| R-015 | Phase 3 | Add module-level assertion: `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` immediately after constant definitions |
| R-016 | Phase 3 | Fix embed guard: evaluate `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where composed = prompt |
| R-017 | Phase 3 | Update renamed test class `test_embed_size_guard_fallback`: update docstring, import `_EMBED_SIZE_LIMIT` from executor |
| R-018 | Phase 3 | Add `TestComposedStringGuard` with `test_prompt_plus_embedded_exceeds_limit`: file at 90% limit + large |
| R-019 | Phase 3 | Add exact-limit boundary test: composed length exactly equal to `_EMBED_SIZE_LIMIT` still embeds inline |
| R-020 | Phase 3 | Run roadmap tests: `uv run pytest tests/roadmap/test_file_passing.py -v` -- 0 failures |
| R-021 | Phase 4 | Rename test class: `test_100kb_guard_fallback` to `test_embed_size_guard_fallback` in `tests/roadmap/test_file_passing.py` |
| R-022 | Phase 5 | Fix `executor.py` fallback path: replace `--file` with inline `-p` embedding |
| R-023 | Phase 5 | Fix `remediate_executor.py:177`: replace unconditional `--file` with inline embedding |
| R-024 | Phase 5 | Fix `validate_executor.py:109`: replace `--file` with inline embedding |
| R-025 | Phase 5 | Fix `tasklist/executor.py:121`: replace `--file` with inline embedding |
| R-026 | Phase 5 | Assess OQ-4 for non-inheriting executors: determine if these executors also need `--tools default` |
| R-027 | Phase 5 | Add conditional tests: `test_remediate_inline_embed_replaces_file_flag`, `test_inline_embed_fallback_when_file_broken` parameterized over three |
| R-028 | Phase 5 | Run affected test suites: `uv run pytest tests/roadmap/ tests/pipeline/ -v` -- 0 failures |
| R-029 | Phase 6 | Combined test run: `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v` -- 0 failures |
| R-030 | Phase 6 | CLI smoke test: `superclaude sprint run ... --dry-run` completes without error |
| R-031 | Phase 6 | Large file E2E test: pipeline run with >=120 KB spec file completes without `OSError` |
| R-032 | Phase 7 | Final `git diff` review: confirm only expected files changed |
| R-033 | Phase 7 | Commit FIX-001: `feat(pipeline): add --tools default to ClaudeProcess.build_command()` |
| R-034 | Phase 7 | Commit FIX-ARG-TOO-LONG: `fix(executor): derive embed limit from MAX_ARG_STRLEN, measure composed string` |
| R-035 | Phase 7 | Commit Phase 1.5 (if activated): `fix(executors): replace --file fallback with inline embedding` |
| R-036 | Phase 7 | Resolve version number: confirm v2.24.5 or v2.25.1 against project version history before tagging |
| R-037 | Phase 7 | Tag release: `v2.24.5` (pending version confirmation) |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001, R-003 | CLI availability confirmation | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0001/evidence.md | XS | Low |
| D-0002 | T01.02 | R-004 | `--file` format documentation | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0002/notes.md | XS | Low |
| D-0003 | T01.03 | R-005 | Empirical test result (PINEAPPLE probe) | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0003/evidence.md | XS | Low |
| D-0004 | T01.04 | R-006 | Phase 0 result recorded (WORKING/BROKEN) | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0004/evidence.md | XS | Low |
| D-0005 | T01.05 | R-007 | Gate decision documented | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0005/spec.md | XS | Low |
| D-0006 | T02.01 | R-008 | Subclass override audit report | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0006/evidence.md | S | Low |
| D-0007 | T02.02 | R-009 | Modified `process.py` with `--tools default` | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0007/evidence.md | S | Medium |
| D-0008 | T02.03 | R-010 | Updated `test_required_flags` assertion | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0008/evidence.md | XS | Low |
| D-0009 | T02.04 | R-011 | Updated `test_stream_json_matches_sprint_flags` | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0009/evidence.md | XS | Low |
| D-0010 | T02.05 | R-012 | New `test_tools_default_in_command` test | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0010/evidence.md | S | Low |
| D-0011 | T02.06 | R-013 | Pipeline test suite passing | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0011/evidence.md | XS | Low |
| D-0012 | T03.01 | R-002, R-014 | Replaced constants in `executor.py` | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0012/evidence.md | M | Medium |
| D-0013 | T03.02 | R-015 | Module-level assertion in `executor.py` | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0013/evidence.md | S | Low |
| D-0014 | T03.03 | R-016 | Fixed embed guard measuring composed string | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0014/evidence.md | M | Medium |
| D-0015 | T03.04 | R-017 | Updated `test_embed_size_guard_fallback` class | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0015/evidence.md | S | Low |
| D-0016 | T03.05 | R-018 | New `TestComposedStringGuard` test class | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0016/evidence.md | M | Low |
| D-0017 | T03.06 | R-019 | Exact-limit boundary test | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0017/evidence.md | S | Low |
| D-0018 | T03.07 | R-020 | Roadmap test suite passing | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0018/evidence.md | XS | Low |
| D-0019 | T04.01 | R-021 | Renamed test class in `test_file_passing.py` | LIGHT | Quick sanity check | .dev/releases/current/v2.24.5/artifacts/D-0019/evidence.md | XS | Low |
| D-0020 | T05.01 | R-022 | Fixed `executor.py` fallback (inline embed) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0020/evidence.md | M | Medium |
| D-0021 | T05.02 | R-023 | Fixed `remediate_executor.py` inline embedding | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0021/evidence.md | M | Medium |
| D-0022 | T05.03 | R-024 | Fixed `validate_executor.py` inline embedding | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0022/evidence.md | M | Medium |
| D-0023 | T05.04 | R-025 | Fixed `tasklist/executor.py` inline embedding | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.5/artifacts/D-0023/evidence.md | M | Medium |
| D-0024 | T05.05 | R-026 | OQ-4 assessment for `--tools default` | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0024/notes.md | S | Medium |
| D-0025 | T05.06 | R-027 | Conditional fallback test suite | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0025/evidence.md | M | Low |
| D-0026 | T05.07 | R-028 | Affected test suites passing | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0026/evidence.md | XS | Low |
| D-0027 | T06.01 | R-029 | Combined test run passing (sprint/roadmap/pipeline) | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0027/evidence.md | S | Low |
| D-0028 | T06.02 | R-030 | CLI smoke test passing | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0028/evidence.md | S | Low |
| D-0029 | T06.03 | R-031 | Large file E2E test passing (>=120 KB) | STANDARD | Direct test | .dev/releases/current/v2.24.5/artifacts/D-0029/evidence.md | M | Medium |
| D-0030 | T07.01 | R-032 | Git diff review completed | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0030/evidence.md | XS | Low |
| D-0031 | T07.02 | R-033 | FIX-001 commit created | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0031/evidence.md | XS | Low |
| D-0032 | T07.03 | R-034 | FIX-ARG-TOO-LONG commit created | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0032/evidence.md | XS | Low |
| D-0033 | T07.04 | R-035 | Phase 1.5 commit (conditional) | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0033/evidence.md | XS | Low |
| D-0034 | T07.05 | R-036 | Version number resolved | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0034/notes.md | XS | Low |
| D-0035 | T07.06 | R-037 | Release tagged | EXEMPT | Skip | .dev/releases/current/v2.24.5/artifacts/D-0035/evidence.md | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0001/ |
| R-002 | T03.01 | D-0012 | STRICT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0012/ |
| R-003 | T01.01 | D-0001 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0001/ |
| R-004 | T01.02 | D-0002 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0002/ |
| R-005 | T01.03 | D-0003 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0003/ |
| R-006 | T01.04 | D-0004 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0004/ |
| R-007 | T01.05 | D-0005 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0005/ |
| R-008 | T02.01 | D-0006 | STRICT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0006/ |
| R-009 | T02.02 | D-0007 | STRICT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0007/ |
| R-010 | T02.03 | D-0008 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0008/ |
| R-011 | T02.04 | D-0009 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0009/ |
| R-012 | T02.05 | D-0010 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0010/ |
| R-013 | T02.06 | D-0011 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0011/ |
| R-014 | T03.01 | D-0012 | STRICT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0012/ |
| R-015 | T03.02 | D-0013 | STRICT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0013/ |
| R-016 | T03.03 | D-0014 | STRICT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0014/ |
| R-017 | T03.04 | D-0015 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0015/ |
| R-018 | T03.05 | D-0016 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0016/ |
| R-019 | T03.06 | D-0017 | STRICT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0017/ |
| R-020 | T03.07 | D-0018 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0018/ |
| R-021 | T04.01 | D-0019 | LIGHT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0019/ |
| R-022 | T05.01 | D-0020 | STRICT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0020/ |
| R-023 | T05.02 | D-0021 | STRICT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0021/ |
| R-024 | T05.03 | D-0022 | STRICT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0022/ |
| R-025 | T05.04 | D-0023 | STRICT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0023/ |
| R-026 | T05.05 | D-0024 | EXEMPT | 80% | .dev/releases/current/v2.24.5/artifacts/D-0024/ |
| R-027 | T05.06 | D-0025 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0025/ |
| R-028 | T05.07 | D-0026 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0026/ |
| R-029 | T06.01 | D-0027 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0027/ |
| R-030 | T06.02 | D-0028 | STANDARD | 80% | .dev/releases/current/v2.24.5/artifacts/D-0028/ |
| R-031 | T06.03 | D-0029 | STANDARD | 85% | .dev/releases/current/v2.24.5/artifacts/D-0029/ |
| R-032 | T07.01 | D-0030 | EXEMPT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0030/ |
| R-033 | T07.02 | D-0031 | EXEMPT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0031/ |
| R-034 | T07.03 | D-0032 | EXEMPT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0032/ |
| R-035 | T07.04 | D-0033 | EXEMPT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0033/ |
| R-036 | T07.05 | D-0034 | EXEMPT | 85% | .dev/releases/current/v2.24.5/artifacts/D-0034/ |
| R-037 | T07.06 | D-0035 | EXEMPT | 90% | .dev/releases/current/v2.24.5/artifacts/D-0035/ |

## Execution Log Template

**Intended Path:** .dev/releases/current/v2.24.5/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| (to be filled during execution) | | | | | | | |

## Checkpoint Report Template

**Template:**

```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>
## Status
- Overall: Pass | Fail | TBD
## Verification Results
- (bullet 1)
- (bullet 2)
- (bullet 3)
## Exit Criteria Assessment
- (bullet 1)
- (bullet 2)
- (bullet 3)
## Issues & Follow-ups
- (list blocking issues referencing T<PP>.<TT> and D-####)
## Evidence
- (bullet list of intended evidence paths under .dev/releases/current/v2.24.5/evidence/)
```

## Feedback Collection Template

**Intended Path:** .dev/releases/current/v2.24.5/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| (to be filled during execution) | | | | | | |

## Generation Notes

- Phase renumbering applied: roadmap phases 0, 1.1, 1.2, 1.3, 1.5, 2, 3 mapped to contiguous 1-7
- Phase 5 (conditional --file fallback) preserves roadmap's conditional activation semantics (Phase 0 = BROKEN)
- R-001 and R-002 (executive summary items) traced to their implementation tasks rather than generating standalone tasks
- No clarification tasks needed: all roadmap items are fully specified with concrete deliverables
- TASKLIST_ROOT derived from roadmap file path (rule 1 match: `.dev/releases/current/v2.24.5/`)
