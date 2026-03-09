# D-0020: Integration Test Evidence -- SC-001, SC-003

## Test File

`tests/roadmap/test_validate_sc001_sc003.py`

## SC-001: Single-Agent Validation (4 tests)

| Test | Verifies |
|------|----------|
| test_produces_report_file | validate/validation-report.md exists after single-agent run |
| test_report_has_required_frontmatter | blocking_issues_count, warnings_count, tasklist_ready present |
| test_returns_parsed_counts | execute_validate returns dict with blocking/warning/info counts |
| test_single_agent_builds_one_step | Single agent produces exactly 1 "reflect" step |

## SC-003: Multi-Agent Validation (4 tests)

| Test | Verifies |
|------|----------|
| test_multi_agent_builds_parallel_reflects_and_merge | Parallel reflect group + sequential merge step |
| test_per_agent_reflection_files_exist | reflect-opus-architect.md and reflect-haiku-architect.md created |
| test_merged_report_has_agreement_table | Agreement table with BOTH_AGREE categories present |
| test_merged_report_frontmatter_has_all_fields | validation_mode and validation_agents in frontmatter |

## Execution Evidence

```
$ uv run pytest tests/roadmap/test_validate_sc001_sc003.py -v
8 passed in 0.13s
```

## Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| SC-001: single-agent produces validation-report.md with valid frontmatter | PASS |
| SC-003: multi-agent produces per-agent reflection files and merged report | PASS |
| Both verify frontmatter contains required fields | PASS |
| All tests pass | PASS |
