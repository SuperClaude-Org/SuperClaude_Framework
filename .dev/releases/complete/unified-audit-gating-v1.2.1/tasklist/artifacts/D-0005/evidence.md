# D-0005: Tasklist Parser Evidence

## Deliverable

Tasklist parser in `src/superclaude/cli/sprint/config.py` that converts phase tasklist markdown into a task inventory with task IDs, descriptions, and dependency annotations.

## Implementation

- **Data model**: `TaskEntry` dataclass added to `src/superclaude/cli/sprint/models.py`
  - Fields: `task_id`, `title`, `description`, `dependencies`
- **Parser functions**: `parse_tasklist()` and `parse_tasklist_file()` added to `src/superclaude/cli/sprint/config.py`
  - Regex-based extraction of `### T<PP>.<TT> -- Title` headings
  - Dependency extraction from `**Dependencies:**` lines
  - Description extraction from `**Deliverables:**` sections
  - Graceful handling of malformed input (empty, missing headings, invalid IDs)

## Verification

```
uv run pytest tests/sprint/test_config.py -k TasklistParser -v
# 13 passed
```

### Test Coverage

| Test | Status |
|------|--------|
| test_extracts_task_ids | PASS |
| test_extracts_titles | PASS |
| test_extracts_dependencies_none | PASS |
| test_extracts_dependencies_multiple | PASS |
| test_extracts_dependencies_single | PASS |
| test_extracts_description_from_deliverables | PASS |
| test_empty_content_returns_empty | PASS |
| test_whitespace_only_returns_empty | PASS |
| test_no_headings_returns_empty | PASS |
| test_malformed_heading_skipped | PASS |
| test_em_dash_separator | PASS |
| test_parse_tasklist_file | PASS |
| test_parse_tasklist_file_missing | PASS |

## Files Modified

- `src/superclaude/cli/sprint/models.py` (added TaskEntry dataclass)
- `src/superclaude/cli/sprint/config.py` (added parse_tasklist, parse_tasklist_file)
- `tests/sprint/test_config.py` (added TestTasklistParser class)
