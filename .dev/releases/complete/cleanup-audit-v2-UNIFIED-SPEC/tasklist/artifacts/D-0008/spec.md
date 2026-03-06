# D-0008 Spec: Phase-1 Scanner Output Schema

## Module
`src/superclaude/cli/audit/scanner_schema.py`

## Required Fields
| Field | Type | Description |
|-------|------|-------------|
| file_path | str | Path to scanned file |
| classification | str | V2 action label |
| evidence | list | Evidence strings |
| confidence | float | 0.0-1.0 confidence score |
| tier | str | V2 tier label |

## Validation
`validate_phase1(output) -> SchemaValidationResult` — rejects missing/wrong-type fields.
