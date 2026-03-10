# D-0018: File-Type Verification Rules Specification

## File Type Categories

| Category | Extensions/Patterns | Evidence Required |
|----------|-------------------|-------------------|
| source | .py, .ts, .js, .jsx, .tsx, .go, .rs, .java | import/export/reference evidence |
| config | .json, .yaml, .yml, .toml, .ini, .cfg, .env | reference evidence (something reads it) |
| docs | .md, .rst, .txt, .adoc | link validation (min 0 - can exist alone) |
| test | test_*, *.test.*, *.spec.*, tests/ directory | test target reference |
| binary | .png, .jpg, .pyc, .so, .zip | at least one usage reference |

## Rule Engine

- Module: `src/superclaude/cli/audit/filetype_rules.py`
- `classify_file_type()`: priority-ordered detection (test > binary > config > docs > source)
- `verify_classification()`: dispatches to file-type-specific rule set
- Only enforced for KEEP and DELETE actions; INVESTIGATE/REORGANIZE pass through
