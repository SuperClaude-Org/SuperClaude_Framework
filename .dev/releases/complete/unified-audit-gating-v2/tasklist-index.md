# TASKLIST INDEX -- unified-audit-gating v2.0

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | unified-audit-gating v2.0 |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-06T00:00:00Z |
| TASKLIST_ROOT | `.dev/releases/current/unified-audit-gating-v2/` |
| Total Phases | 6 |
| Total Tasks | 33 |
| Total Deliverables | 33 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | architect, scribe |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `.dev/releases/current/unified-audit-gating-v2/tasklist-index.md` |
| Phase 1 Tasklist | `.dev/releases/current/unified-audit-gating-v2/phase-1-tasklist.md` |
| Phase 2 Tasklist | `.dev/releases/current/unified-audit-gating-v2/phase-2-tasklist.md` |
| Phase 3 Tasklist | `.dev/releases/current/unified-audit-gating-v2/phase-3-tasklist.md` |
| Phase 4 Tasklist | `.dev/releases/current/unified-audit-gating-v2/phase-4-tasklist.md` |
| Phase 5 Tasklist | `.dev/releases/current/unified-audit-gating-v2/phase-5-tasklist.md` |
| Phase 6 Tasklist | `.dev/releases/current/unified-audit-gating-v2/phase-6-tasklist.md` |
| Execution Log | `.dev/releases/current/unified-audit-gating-v2/execution-log.md` |
| Checkpoint Reports | `.dev/releases/current/unified-audit-gating-v2/checkpoints/` |
| Evidence Directory | `.dev/releases/current/unified-audit-gating-v2/evidence/` |
| Artifacts Directory | `.dev/releases/current/unified-audit-gating-v2/artifacts/` |
| Feedback Log | `.dev/releases/current/unified-audit-gating-v2/feedback-log.md` |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation & Source Defaults | T01.01-T01.07 | STRICT: 3, STANDARD: 4 |
| 2 | phase-2-tasklist.md | Shell & CLI Alignment | T02.01-T02.05 | STANDARD: 4, LIGHT: 1 |
| 3 | phase-3-tasklist.md | Validation — Source Integrity | T03.01-T03.03 | EXEMPT: 3 |
| 4 | phase-4-tasklist.md | Test Suite Updates | T04.01-T04.10 | STANDARD: 10 |
| 5 | phase-5-tasklist.md | Documentation & Spec Alignment | T05.01-T05.04 | STRICT: 1, EXEMPT: 3 |
| 6 | phase-6-tasklist.md | Validation — End-to-End | T06.01-T06.04 | STANDARD: 4 |

## Source Snapshot

- Configuration change release correcting two sprint pipeline defaults: `max_turns` (50→100) and `reimbursement_rate` (0.5→0.8)
- 12 source edits across Python and shell files, 4 test assertion updates, 6 new tests, and spec documentation alignment
- Structured in 4 work milestones (M1-M4) plus 2 interleaved validation milestones (V1, V2)
- Tiered edit strategy: Python source defaults first, then shell/CLI alignment, then test suite updates, then documentation
- Compliance tier: STRICT (user-specified); all changes require validation before proceeding
- Critical path: M1 → M2 → V1 → M3 → M4 → V2

## Deterministic Rules Applied

- Phase bucketing: 6 explicit milestones (M1, M2, V1, M3, M4, V2) mapped to Phases 1-6 in appearance order
- Phase renumbering: sequential 1-6 with no gaps applied (M1→1, M2→2, V1→3, M3→4, M4→5, V2→6)
- Task ID scheme: `T<PP>.<TT>` zero-padded 2-digit format (T01.01 through T06.04)
- 1:1 task-to-deliverable mapping: each roadmap deliverable generates exactly one task (33 tasks total)
- Checkpoint cadence: every 5 tasks within a phase plus mandatory end-of-phase checkpoint
- Effort scoring: keyword-based EFFORT_SCORE → XS/S/M/L/XL mapping per Section 5.2.1
- Risk scoring: keyword-based RISK_SCORE → Low/Medium/High mapping per Section 5.2.2
- Tier classification: `/sc:task-unified` algorithm with compound phrase overrides, keyword matching, context boosters
- Critical path override: tasks touching `models/` paths receive STRICT enforcement regardless of keyword score
- Verification routing: STRICT→sub-agent, STANDARD→direct test, LIGHT→sanity check, EXEMPT→skip
- MCP requirements: STRICT tasks require Sequential + Serena; STANDARD prefer Sequential + Context7
- Traceability: R-### → T<PP>.<TT> → D-#### fully traced with artifact paths

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | Apply all 7 Tier 1 Python source default changes to establish the new max_turns=100 and reimbursement_rate=0.8 |
| R-002 | Phase 1 | `PipelineConfig.max_turns` default → 100; `pipeline/models.py:175` reads `max_turns: int = 100` |
| R-003 | Phase 1 | `SprintConfig.max_turns` default → 100; `sprint/models.py:285` reads `max_turns: int = 100` |
| R-004 | Phase 1 | CLI `--max-turns` default → 100; `sprint/commands.py:54` reads `default=100` |
| R-005 | Phase 1 | CLI `--max-turns` help text → "default: 100"; `sprint/commands.py:55` help string updated |
| R-006 | Phase 1 | `load_sprint_config(max_turns)` default → 100; `sprint/config.py:108` reads `max_turns: int = 100` |
| R-007 | Phase 1 | `ClaudeProcess.__init__(max_turns)` default → 100; `pipeline/process.py:43` reads `max_turns: int = 100` |
| R-008 | Phase 1 | `TurnLedger.reimbursement_rate` default → 0.8; `sprint/models.py:476` reads `reimbursement_rate: float = 0.8` |
| R-009 | Phase 2 | Apply the 5 panel-identified edits in shell scripts and roadmap CLI to eliminate configuration drift |
| R-010 | Phase 2 | `execute-sprint.sh` `MAX_TURNS=100`; `.dev/releases/execute-sprint.sh:47` reads `MAX_TURNS=100` |
| R-011 | Phase 2 | `execute-sprint.sh` help text → "default: 100"; `.dev/releases/execute-sprint.sh:14` updated |
| R-012 | Phase 2 | `rerun-incomplete-phases.sh` comment → "max_turns (100)"; `scripts/rerun-incomplete-phases.sh:4` updated |
| R-013 | Phase 2 | Roadmap CLI `--max-turns` default → 100; `roadmap/commands.py:75` reads `default=100` |
| R-014 | Phase 2 | Roadmap CLI help text → "Default: 100"; `roadmap/commands.py:76` updated |
| R-015 | Phase 3 | Verify all 12 source edits are correctly applied, no residual old values remain |
| R-016 | Phase 3 | Grep verification: no remaining `max_turns.*50` defaults; zero matches in source files |
| R-017 | Phase 3 | Grep verification: no remaining `reimbursement_rate.*0.5` defaults; zero matches in source files |
| R-018 | Phase 3 | Cross-reference check: all 12 FRs verified against file:line targets |
| R-019 | Phase 4 | Update 4 existing test assertions and add 6 new tests covering budget decay, sprint sustainability |
| R-020 | Phase 4 | Update `test_models.py:54` assertion → `== 100`; test passes |
| R-021 | Phase 4 | Update `test_models.py:188` assertion → `== 100`; test passes |
| R-022 | Phase 4 | Update `test_config.py:215` assertion → `== 100`; test passes |
| R-023 | Phase 4 | Update `test_models.py:527` assertion → `== 0.8`; test passes |
| R-024 | Phase 4 | New: `test_budget_decay_rate_08` (unit); verifies net cost = 4 at rate=0.8, actual=8 |
| R-025 | Phase 4 | New: `test_max_sustainable_tasks_at_08` (unit); verifies exhaustion at ~50 tasks with budget=200 |
| R-026 | Phase 4 | New: `test_46_task_sprint_sustainability` (integration); 46-task loop completes with budget > 0 |
| R-027 | Phase 4 | New: `test_budget_exhaustion_property` (property-based); random tasks/turns always reach budget=0 |
| R-028 | Phase 4 | New: `test_explicit_max_turns_override` (regression); `--max-turns=50` overrides new default |
| R-029 | Phase 4 | New: `test_rate_boundary_validation` (boundary); rate=0.0, 0.99, 1.0(rejected), -0.1(rejected) |
| R-030 | Phase 5 | Write mandatory CHANGELOG entry with migration guide, update spec prose, add budget guidance |
| R-031 | Phase 5 | CHANGELOG entry for v2.0.0 with migration guide; entry matches spec §11 template |
| R-032 | Phase 5 | Update `unified-spec-v1.0.md` §3.1 → `rate = 0.80`; line 178 corrected |
| R-033 | Phase 5 | Update `unified-spec-v1.0.md` §3.4 proof → rate=0.80 math; lines 225-235 corrected |
| R-034 | Phase 5 | Add budget guidance note for >40 task sprints; `initial_budget ≥ 250` recommendation documented |
| R-035 | Phase 6 | Run the complete test suite, verify backward compatibility, confirm 46-task sprint sustainability |
| R-036 | Phase 6 | Full test suite passes (existing + new); zero failures |
| R-037 | Phase 6 | 46-task sprint integration test passes; budget remaining > 0 |
| R-038 | Phase 6 | Explicit override regression passes; `--max-turns=50` preserved |
| R-039 | Phase 6 | Tier 3 (no-change) tests still pass; no regressions in explicit-fixture tests |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-002 | `PipelineConfig.max_turns` default set to 100 in `pipeline/models.py:175` | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0001/evidence.md` | XS | Low |
| D-0002 | T01.02 | R-003 | `SprintConfig.max_turns` default set to 100 in `sprint/models.py:285` | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0002/evidence.md` | XS | Low |
| D-0003 | T01.03 | R-004 | CLI `--max-turns` default set to 100 in `sprint/commands.py:54` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0003/evidence.md` | XS | Low |
| D-0004 | T01.04 | R-005 | CLI `--max-turns` help text updated in `sprint/commands.py:55` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0004/evidence.md` | XS | Low |
| D-0005 | T01.05 | R-006 | `load_sprint_config(max_turns)` default set to 100 in `sprint/config.py:108` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0005/evidence.md` | XS | Low |
| D-0006 | T01.06 | R-007 | `ClaudeProcess.__init__(max_turns)` default set to 100 in `pipeline/process.py:43` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0006/evidence.md` | XS | Low |
| D-0007 | T01.07 | R-008 | `TurnLedger.reimbursement_rate` default set to 0.8 in `sprint/models.py:476` | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0007/evidence.md` | XS | Low |
| D-0008 | T02.01 | R-010 | `MAX_TURNS=100` in `execute-sprint.sh:47` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0008/evidence.md` | XS | Low |
| D-0009 | T02.02 | R-011 | Help text "default: 100" in `execute-sprint.sh:14` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0009/evidence.md` | XS | Low |
| D-0010 | T02.03 | R-012 | Comment "max_turns (100)" in `rerun-incomplete-phases.sh:4` | LIGHT | Quick sanity check | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0010/evidence.md` | XS | Low |
| D-0011 | T02.04 | R-013 | Roadmap CLI `--max-turns` default=100 in `roadmap/commands.py:75` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0011/evidence.md` | XS | Low |
| D-0012 | T02.05 | R-014 | Roadmap CLI help text "Default: 100" in `roadmap/commands.py:76` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0012/evidence.md` | XS | Low |
| D-0013 | T03.01 | R-016 | Grep report: zero `max_turns.*50` default matches in source files | EXEMPT | Skip verification | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0013/evidence.md` | XS | Low |
| D-0014 | T03.02 | R-017 | Grep report: zero `reimbursement_rate.*0.5` default matches in source files | EXEMPT | Skip verification | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0014/evidence.md` | XS | Low |
| D-0015 | T03.03 | R-018 | Cross-reference verification: all 12 FRs confirmed at target file:line locations | EXEMPT | Skip verification | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0015/evidence.md` | XS | Low |
| D-0016 | T04.01 | R-020 | Updated assertion `== 100` in `tests/pipeline/test_models.py:54` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0016/evidence.md` | XS | Low |
| D-0017 | T04.02 | R-021 | Updated assertion `== 100` in `tests/sprint/test_models.py:188` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0017/evidence.md` | XS | Low |
| D-0018 | T04.03 | R-022 | Updated assertion `== 100` in `tests/sprint/test_config.py:215` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0018/evidence.md` | XS | Low |
| D-0019 | T04.04 | R-023 | Updated assertion `== 0.8` in `tests/sprint/test_models.py:527` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0019/evidence.md` | XS | Low |
| D-0020 | T04.05 | R-024 | New test `test_budget_decay_rate_08` in `tests/sprint/test_models.py` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0020/evidence.md` | XS | Low |
| D-0021 | T04.06 | R-025 | New test `test_max_sustainable_tasks_at_08` in `tests/sprint/test_models.py` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0021/evidence.md` | XS | Low |
| D-0022 | T04.07 | R-026 | New test `test_46_task_sprint_sustainability` in `tests/sprint/test_models.py` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0022/evidence.md` | XS | Low |
| D-0023 | T04.08 | R-027 | New test `test_budget_exhaustion_property` in `tests/sprint/test_models.py` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0023/evidence.md` | XS | Low |
| D-0024 | T04.09 | R-028 | New test `test_explicit_max_turns_override` in `tests/sprint/test_config.py` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0024/evidence.md` | XS | Low |
| D-0025 | T04.10 | R-029 | New test `test_rate_boundary_validation` in `tests/sprint/test_models.py` | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0025/evidence.md` | XS | Low |
| D-0026 | T05.01 | R-031 | CHANGELOG entry for v2.0.0 with migration guide | STRICT | Sub-agent (quality-engineer) | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0026/spec.md` | S | Medium |
| D-0027 | T05.02 | R-032 | Updated `unified-spec-v1.0.md` §3.1 with `rate = 0.80` | EXEMPT | Skip verification | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0027/evidence.md` | XS | Low |
| D-0028 | T05.03 | R-033 | Updated `unified-spec-v1.0.md` §3.4 proof with rate=0.80 math | EXEMPT | Skip verification | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0028/evidence.md` | XS | Low |
| D-0029 | T05.04 | R-034 | Budget guidance note for >40 task sprints documented | EXEMPT | Skip verification | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0029/evidence.md` | XS | Low |
| D-0030 | T06.01 | R-036 | Full test suite execution report with zero failures | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0030/evidence.md` | S | Low |
| D-0031 | T06.02 | R-037 | 46-task sprint integration test passes with budget > 0 | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0031/evidence.md` | XS | Low |
| D-0032 | T06.03 | R-038 | Explicit `--max-turns=50` override regression test passes | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0032/evidence.md` | XS | Low |
| D-0033 | T06.04 | R-039 | Tier 3 no-change tests pass with no regressions | STANDARD | Direct test execution | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0033/evidence.md` | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01-T01.07 | — | — | — | (objective; traced via child items) |
| R-002 | T01.01 | D-0001 | STRICT | 75% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0001/evidence.md` |
| R-003 | T01.02 | D-0002 | STRICT | 75% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0002/evidence.md` |
| R-004 | T01.03 | D-0003 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0003/evidence.md` |
| R-005 | T01.04 | D-0004 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0004/evidence.md` |
| R-006 | T01.05 | D-0005 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0005/evidence.md` |
| R-007 | T01.06 | D-0006 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0006/evidence.md` |
| R-008 | T01.07 | D-0007 | STRICT | 75% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0007/evidence.md` |
| R-009 | T02.01-T02.05 | — | — | — | (objective; traced via child items) |
| R-010 | T02.01 | D-0008 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0008/evidence.md` |
| R-011 | T02.02 | D-0009 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0009/evidence.md` |
| R-012 | T02.03 | D-0010 | LIGHT | 72% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0010/evidence.md` |
| R-013 | T02.04 | D-0011 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0011/evidence.md` |
| R-014 | T02.05 | D-0012 | STANDARD | 55% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0012/evidence.md` |
| R-015 | T03.01-T03.03 | — | — | — | (objective; traced via child items) |
| R-016 | T03.01 | D-0013 | EXEMPT | 80% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0013/evidence.md` |
| R-017 | T03.02 | D-0014 | EXEMPT | 80% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0014/evidence.md` |
| R-018 | T03.03 | D-0015 | EXEMPT | 80% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0015/evidence.md` |
| R-019 | T04.01-T04.10 | — | — | — | (objective; traced via child items) |
| R-020 | T04.01 | D-0016 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0016/evidence.md` |
| R-021 | T04.02 | D-0017 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0017/evidence.md` |
| R-022 | T04.03 | D-0018 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0018/evidence.md` |
| R-023 | T04.04 | D-0019 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0019/evidence.md` |
| R-024 | T04.05 | D-0020 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0020/evidence.md` |
| R-025 | T04.06 | D-0021 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0021/evidence.md` |
| R-026 | T04.07 | D-0022 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0022/evidence.md` |
| R-027 | T04.08 | D-0023 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0023/evidence.md` |
| R-028 | T04.09 | D-0024 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0024/evidence.md` |
| R-029 | T04.10 | D-0025 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0025/evidence.md` |
| R-030 | T05.01-T05.04 | — | — | — | (objective; traced via child items) |
| R-031 | T05.01 | D-0026 | STRICT | 43% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0026/spec.md` |
| R-032 | T05.02 | D-0027 | EXEMPT | 80% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0027/evidence.md` |
| R-033 | T05.03 | D-0028 | EXEMPT | 80% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0028/evidence.md` |
| R-034 | T05.04 | D-0029 | EXEMPT | 80% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0029/evidence.md` |
| R-035 | T06.01-T06.04 | — | — | — | (objective; traced via child items) |
| R-036 | T06.01 | D-0030 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0030/evidence.md` |
| R-037 | T06.02 | D-0031 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0031/evidence.md` |
| R-038 | T06.03 | D-0032 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0032/evidence.md` |
| R-039 | T06.04 | D-0033 | STANDARD | 60% | `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0033/evidence.md` |

## Execution Log Template

**Intended Path:** `.dev/releases/current/unified-audit-gating-v2/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
| | | | | | | | |

## Checkpoint Report Template

### Template

```markdown
# Checkpoint Report -- <Checkpoint Title>

**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/<deterministic-name>.md`
**Scope:** <tasks covered>

## Status
Overall: Pass | Fail | TBD

## Verification Results
- <bullet 1>
- <bullet 2>
- <bullet 3>

## Exit Criteria Assessment
- <bullet 1>
- <bullet 2>
- <bullet 3>

## Issues & Follow-ups
- <list blocking issues; reference T<PP>.<TT> and D-####>

## Evidence
- <bullet list of intended evidence paths>
```

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/unified-audit-gating-v2/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
| | | | | | | |

## Generation Notes

- TASKLIST_ROOT derived via substring match: roadmap contains `.dev/releases/current/unified-audit-gating-v2/`
- All 6 milestones mapped 1:1 to phases; no phase renumbering needed (already sequential)
- Milestone objectives (R-001, R-009, R-015, R-019, R-030, R-035) serve as phase context; no standalone tasks generated for objectives
- T05.01 (CHANGELOG with migration guide) classified STRICT due to "migration" keyword match despite being documentation; tier conflict [STRICT vs EXEMPT] resolved to STRICT by priority rule
- Confidence scores are generally moderate (43-80%) due to single-keyword matches on short task descriptions; critical path overrides enforce correct tiers regardless
- No clarification tasks needed: roadmap provides exact file:line targets for all 12 edits, specific test names for all 6 new tests, and explicit acceptance criteria
