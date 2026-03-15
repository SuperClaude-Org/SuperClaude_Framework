# D-0011: Error Code Taxonomy Spec

## Task: T02.07

**Implementation:** `src/superclaude/cli/cli_portify/models.py`

## Error Code Constants

All 5 error codes are defined as string constants at the module level:

```python
NAME_COLLISION: str = "NAME_COLLISION"
OUTPUT_NOT_WRITABLE: str = "OUTPUT_NOT_WRITABLE"
AMBIGUOUS_PATH: str = "AMBIGUOUS_PATH"
INVALID_PATH: str = "INVALID_PATH"
DERIVATION_FAILED: str = "DERIVATION_FAILED"
```

**Source:** `src/superclaude/cli/cli_portify/models.py:27-31`

## Exception Hierarchy

```
Exception
  └── PortifyValidationError(error_code: str, message: str, details: str = "")
        ├── NameCollisionError(cli_name: str, existing_path: str = "")
        ├── OutputNotWritableError(path: str)
        ├── AmbiguousPathError(name: str, candidates: list[str])
        ├── InvalidPathError(path: str)
        └── DerivationFailedError(workflow_name: str)
```

## Usage

Each exception carries its error code in `exc.error_code` and can be caught via the base `PortifyValidationError`:

```python
try:
    raise InvalidPathError("/bad/path")
except PortifyValidationError as exc:
    print(exc.error_code)  # "INVALID_PATH"
```

## Error Code Semantics

| Code | Exception | When Raised |
|------|-----------|-------------|
| `NAME_COLLISION` | `NameCollisionError` | Derived CLI name conflicts with existing non-portified module |
| `OUTPUT_NOT_WRITABLE` | `OutputNotWritableError` | Output path not writable or cannot be created |
| `AMBIGUOUS_PATH` | `AmbiguousPathError` | Partial skill name matches multiple directories |
| `INVALID_PATH` | `InvalidPathError` | Path exists but lacks SKILL.md, or does not exist |
| `DERIVATION_FAILED` | `DerivationFailedError` | Stripping prefix/suffix yields empty name with no --name override |

## Test Coverage

- `uv run pytest tests/ -k "test_error_codes"` — 13 tests, exits 0
- `TestErrorCodes` class in `test_models.py`

## Source Location

- `src/superclaude/cli/cli_portify/models.py:23-108`
