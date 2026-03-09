---
spec_source: ".dev/releases/backlog/v2.14-SprintReportScaffolding/release-spec.md"
generated: "2026-03-06"
generator: "sc:roadmap"
validation_philosophy: continuous-parallel
validation_milestones: 1
work_milestones: 3
interleave_ratio: "1:3"
major_issue_policy: stop-and-fix
complexity_class: LOW
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is **1:3** (one validation pass after all 3 work milestones), derived from complexity class LOW

**Note on interleave ratio**: With only 3 milestones in a linear dependency chain, the 1:3 ratio means validation occurs once after all work is complete (M3 IS the validation milestone). This is appropriate because:
- M1 and M2 are both P0 and must be built together before meaningful integration testing
- M3 explicitly includes status classification tests that validate M1+M2 interaction
- The spec's own milestone structure already encodes this pattern

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M3 (Tests and Validation) | Full scaffold lifecycle: parse → create → classify → integrate → prompt | Any test failure in `test_scaffold.py` or regression in `tests/sprint/` |

**V1 is embedded within M3**: M3's deliverables (D3.1-D3.4) ARE the validation activities. This is by design — the spec explicitly structures M3 as the validation milestone.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Scaffold causes `ERROR` instead of `PASS_NO_SIGNAL`; `_determine_phase_status()` modified; scaffold creation prevents sprint execution |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Scaffold YAML contains `status:` field; regex fails on real tasklist fixture; prompt still contains "Completion Protocol" |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Missing `encoding="utf-8"` on write; import at top-level instead of inside try-block; test naming inconsistency |
| Info | Log only, no action required | N/A | Alternative regex pattern noted; scaffold template could include more metadata; edge case coverage suggestion |

## Acceptance Gates

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | `parse_phase_tasks()` returns correct TaskMeta list from real tasklist fixture | All D1.1-D1.4 acceptance criteria met |
| M1 | `scaffold_result_file()` creates parseable file without `status:` or `EXIT_RECOMMENDATION:` | File validated against `_determine_phase_status()` → `PASS_NO_SIGNAL` |
| M2 | Scaffold file exists at `config.result_file(phase)` before `proc_manager.start()` | Integration test with mock subprocess confirms timing |
| M2 | Scaffold failure does not prevent sprint execution | OSError simulation test passes |
| M2 | `build_prompt()` output contains "scaffold report already exists" and "you MUST finalize" | String containment assertions pass |
| M3 | All 17+ tests pass | `uv run pytest tests/sprint/test_scaffold.py -v` exits 0 |
| M3 | No regressions in existing sprint tests | `uv run pytest tests/sprint/ -v` exits 0 |
| M3 | No regressions in full project suite | `uv run pytest tests/ -v` exits 0 |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | `test_parse_extracts_ids_titles_tiers`, `test_parse_real_tasklist_fixture` | M1, M3 | Unit test with synthetic + real fixture data |
| FR-002 | `test_scaffold_creates_file`, `test_scaffold_yaml_frontmatter` | M1, M3 | Unit test asserting file content |
| FR-003 | `test_scaffold_yaml_frontmatter` | M1, M3 | Assert `status:` absent from YAML block |
| FR-004 | `test_scaffold_no_exit_recommendation` | M1, M3 | Assert `EXIT_RECOMMENDATION` absent from full content |
| FR-005 | `test_untouched_scaffold_returns_pass_no_signal` | M3 | Integration test: scaffold → `_determine_phase_status()` → `PASS_NO_SIGNAL` |
| FR-006 | Integration test (mock subprocess) | M2, M3 | Verify file exists before `process.start()` called |
| FR-007 | `test_scaffold_failure_continues_sprint` | M2, M3 | Simulate OSError, verify sprint proceeds |
| FR-008 | `test_scaffold_failure_logs_to_debug_and_stderr` | M2, M3 | Capture stderr + debug_log output on failure |
| FR-009 | `test_prompt_no_old_completion_protocol` | M2, M3 | Assert "Completion Protocol" absent |
| FR-010 | `test_prompt_references_scaffold` | M2, M3 | Assert "scaffold report already exists" present |
| FR-011 | `test_prompt_incremental_protocol` | M2, M3 | Assert "you MUST finalize" present |
| FR-012 | `test_scaffold_creates_parent_dirs` | M1, M3 | Create scaffold in non-existent directory tree |
| FR-013 | `test_scaffold_overwrites_existing` | M1, M3 | Write file, scaffold over it, verify new content |
| NFR-001 | Full sprint test regression | M3 | `uv run pytest tests/sprint/ -v` exits 0 |
| NFR-002 | `test_untouched_scaffold_returns_pass_no_signal` | M3 | No changes to `_determine_phase_status()` code |
| NFR-003 | v2.13 characterization test pass | M3 | Run characterization tests before and after changes |
| NFR-004 | No new entries in pyproject.toml dependencies | M3 | Manual verification |
| NFR-005 | `test_scaffold_failure_continues_sprint` | M2, M3 | Graceful degradation verified |

## Pre-Implementation Verification

Before starting M1, verify:
1. v2.13 M1 characterization tests exist and pass: `uv run pytest tests/sprint/ -v`
2. Current sprint module files are unmodified from v2.13 baseline
3. No pending changes in `executor.py`, `process.py`, or `models.py`

This ensures the safety net is in place before any scaffold changes land.
