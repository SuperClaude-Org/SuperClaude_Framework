# D-0005: Workflow Path Resolution Spec

## Task: T02.01

**Implementation:** `src/superclaude/cli/cli_portify/config.py::resolve_workflow_path()`

## Algorithm

1. Convert `name_or_path` to an absolute `Path` and check if it exists.
2. If it exists as a file named `SKILL.md`, return its parent.
3. If it exists as a directory:
   - If the directory contains `SKILL.md`, return it.
   - Otherwise, raise `InvalidPathError`.
4. If the path does not exist and `skills_root` is provided:
   - Enumerate subdirectories of `skills_root`.
   - Filter those where `name_or_path` is a case-insensitive substring of the directory name.
   - If exactly 1 match and it contains `SKILL.md`, return it.
   - If >1 match, raise `AmbiguousPathError` with the candidate list.
5. If no match, raise `InvalidPathError`.

## Error Codes

| Code | Condition |
|------|-----------|
| `INVALID_PATH` | Resolved path does not contain `SKILL.md` |
| `AMBIGUOUS_PATH` | Partial name matches multiple skill directories |

## Test Coverage

- `uv run pytest tests/ -k "test_workflow_path"` — 1 test, exits 0
- Additional coverage in `TestConfigValidationErrors` (test_config.py)

## Source Location

- `src/superclaude/cli/cli_portify/config.py:182-233`
- `src/superclaude/cli/cli_portify/models.py:80-98` (AmbiguousPathError, InvalidPathError)
