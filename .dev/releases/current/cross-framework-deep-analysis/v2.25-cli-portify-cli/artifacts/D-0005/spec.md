# D-0005: Workflow Path Resolution Spec

**Task**: T02.01 — Implement Workflow Path Resolution in config.py
**Date**: 2026-03-15
**Status**: COMPLETE

---

## Path Resolution Algorithm

Implemented in `src/superclaude/cli/cli_portify/config.py::resolve_workflow_path()`.

### Rules (in order)

1. **Direct path resolution**: If input is an existing path:
   - If it's a file named `SKILL.md` → return its parent directory
   - If it's a directory → check for `SKILL.md`, raise `INVALID_PATH` if missing
   - If it's any other file → raise `INVALID_PATH`

2. **Skills root search**: If `skills_root` is provided and the direct path doesn't exist:
   - Find all subdirectories whose name contains the input name (case-insensitive)
   - Exactly 1 match → return it (after SKILL.md check)
   - 0 matches → raise `INVALID_PATH`
   - 2+ matches → raise `AMBIGUOUS_PATH` with candidate list

3. **Fallback**: If no skills_root, treat input as a literal path → `INVALID_PATH` if not found.

### Error Codes

| Code | Trigger |
|------|---------|
| `INVALID_PATH` | Path does not exist OR exists but lacks SKILL.md |
| `AMBIGUOUS_PATH` | Partial name matches 2+ skill directories |

### Module Location

```python
# src/superclaude/cli/cli_portify/config.py
def resolve_workflow_path(name_or_path, skills_root=None) -> Path: ...

# Error exceptions in models.py
class InvalidPathError(PortifyValidationError): ...   # error_code = INVALID_PATH
class AmbiguousPathError(PortifyValidationError): ...  # error_code = AMBIGUOUS_PATH
```

### Integration in load_portify_config

`PortifyConfig.resolve_workflow_path()` handles the SKILL.md file → parent dir case:
```python
def resolve_workflow_path(self) -> Path:
    p = self.workflow_path
    if p.is_file():
        return p.parent
    return p
```

---

## Test Coverage

Test file: `tests/cli_portify/test_config.py::TestConfigHappyPath`
- `test_workflow_path_resolution_with_skill_file` — passes SKILL.md file, expects parent dir
- `test_valid_config` — valid directory with SKILL.md
- `test_missing_skill_md` — directory without SKILL.md → error
- `test_invalid_workflow_path` — non-existent path → error
