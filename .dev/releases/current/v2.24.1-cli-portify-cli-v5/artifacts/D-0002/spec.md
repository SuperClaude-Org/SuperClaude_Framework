# D-0002: Compatibility Checklist

## Constraints

| # | Constraint | Status |
|---|-----------|--------|
| C-1 | No edits to `pipeline/` directory | PASS - no pipeline/ files in change map |
| C-2 | No edits to `sprint/` directory | PASS - no sprint/ files in change map |
| C-3 | No async code in resolution.py | PASS - resolve_target() is synchronous |
| C-4 | Existing skill-directory behavior unchanged | PASS - resolve_workflow_path() untouched |
| C-5 | resolve_workflow_path() untouched | PASS - no modifications to that method |
| C-6 | Existing ComponentEntry/ComponentInventory preserved | PASS - new types added alongside, not replacing |
| C-7 | PortifyConfig backward-compatible | PASS - new fields have None defaults |
| C-8 | derive_cli_name() backward-compatible | PASS - falls back to existing logic when command_path is None |
| C-9 | All existing 505 tests pass | BASELINE - verified at session start |
