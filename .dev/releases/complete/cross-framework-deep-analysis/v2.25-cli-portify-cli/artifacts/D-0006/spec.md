# D-0006: CLI Name Derivation Spec

**Task**: T02.02 — Implement CLI Name Derivation Logic
**Date**: 2026-03-15
**Status**: COMPLETE

---

## Derivation Algorithm

Implemented in `src/superclaude/cli/cli_portify/models.py::_derive_name_from_path()`.

### Steps

1. Take the **directory name** from the workflow path
2. Normalize to **lowercase**
3. Strip **`sc-` prefix** if present
4. Strip **`-protocol` suffix** if present
5. Replace non-alphanumeric characters (except `-`) with `-`
6. Collapse multiple consecutive hyphens
7. Strip leading/trailing hyphens
8. If result is **empty** → raise `DerivationFailedError`

### Examples

| Workflow Dir Name | Derived CLI Name |
|---|---|
| `sc-cli-portify-protocol` | `cli-portify` |
| `sc-roadmap-protocol` | `roadmap` |
| `sc-test-workflow-protocol` | `test-workflow` |
| `my-skill` | `my-skill` |
| `sc-` (edge case) | `DerivationFailedError` |

### Explicit Override

`PortifyConfig.cli_name` field stores the explicit override. When set, `derive_cli_name()` returns it directly without running derivation.

```python
config = load_portify_config(workflow_path=wf, cli_name="custom-name")
assert config.derive_cli_name() == "custom-name"
```

### Error Codes

| Code | Trigger |
|------|---------|
| `DERIVATION_FAILED` | Stripping prefix/suffix yields empty string, no `--name` override |

### Module Location

```python
# src/superclaude/cli/cli_portify/models.py
def _derive_name_from_path(workflow_path: Path) -> str: ...
class DerivationFailedError(PortifyValidationError): ...  # error_code = DERIVATION_FAILED

# PortifyConfig method
def derive_cli_name(self) -> str: ...
def to_snake_case(kebab: str) -> str: ...  # kebab → snake_case conversion
```

---

## Test Coverage

Test file: `tests/cli_portify/test_config.py::TestConfigHappyPath`
- `test_cli_name_derivation` — `sc-test-workflow-protocol` → `test-workflow`
- `test_cli_name_override` — explicit `--name custom-name` passes through unchanged
- `test_snake_case_conversion` — `my-kebab-name` → `my_kebab_name`
