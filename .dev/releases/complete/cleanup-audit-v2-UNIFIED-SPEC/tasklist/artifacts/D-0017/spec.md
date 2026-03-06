# D-0017: 8-Field Profile Generator Specification

## Field Extraction Methodology

| Field | Data Source | Extraction Method |
|-------|------------|-------------------|
| imports | ToolOrchestrator cache | Line-based pattern matching (Python `import/from`, JS `import`) |
| exports | ToolOrchestrator cache | Line-based pattern matching (Python `__all__`, JS `export`) |
| size | File content | Line count via `str.splitlines()` |
| complexity | File content | Cyclomatic approximation: 1 + branch keyword count |
| age | Git history | `git log --follow --diff-filter=A --format=%aI` (earliest commit) |
| churn | Git history | `git log --follow --oneline` line count |
| coupling | Import graph | In-degree ratio: files importing this / (total files - 1) |
| test_coverage | File name matching | Heuristic: test_X, X_test, X.test, X.spec naming conventions |

## Implementation

- Module: `src/superclaude/cli/audit/profile_generator.py`
- Class: `ProfileGenerator` with `profile_file()` and `profile_batch()` methods
- Cache integration: leverages `ToolOrchestrator.ResultCache` from T02.03
- Schema validation: `validate_phase2()` from `scanner_schema.py`

## Determinism

Same file content + same git state = identical profile output. Verified by `test_deterministic_output`.
