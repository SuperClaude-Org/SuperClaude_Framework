# D-0023: Dead Code Detector Specification

## Candidate Identification

A file is a dead-code candidate when it meets **all** of these conditions:
1. File has at least one export (function, class, or variable)
2. Zero Tier-A importers (no AST-verified imports from other files)
3. Zero Tier-B importers (no grep-verified references from other files)

Tier-C (inferred) relationships are ignored for candidate selection per the Tier-C safety policy.

## Exclusion Rules

| Category | Patterns | Rationale |
|----------|----------|-----------|
| entry_point | `main.py`, `app.py`, `index.js`, `__main__.py` | Application entry points are used by runtime, not imports |
| framework_hook | `pytest_*.py`, `conftest.py`, `setup.py`, `manage.py` | Framework conventions invoke these files without explicit imports |

## Evidence Per Candidate

Each reported candidate includes:
- `export_location`: file path and line numbers of exports found
- `boundary_search_scope`: directories and file patterns searched for importers

## Implementation

- Module: `src/superclaude/cli/audit/dead_code.py`
- Consumes the dependency graph from D-0022 to check importer counts
- Applies exclusion rules before reporting candidates
- Output is a list of candidates with evidence, not an automatic deletion list
