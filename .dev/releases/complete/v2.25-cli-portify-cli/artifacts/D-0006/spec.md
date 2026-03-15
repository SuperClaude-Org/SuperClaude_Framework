# D-0006: CLI Name Derivation Algorithm Spec

## Task: T02.02

**Implementation:** `src/superclaude/cli/cli_portify/config.py::derive_cli_name()`
**Helper:** `src/superclaude/cli/cli_portify/models.py::_derive_name_from_path()`

## Algorithm

1. If `explicit_name` is provided (non-empty), return it directly — bypasses all derivation.
2. Otherwise, apply derivation to `workflow_path.name`:
   a. Normalize to lowercase.
   b. Strip leading `sc-` prefix (if present).
   c. Strip trailing `-protocol` suffix (if present).
   d. Replace any non-`[a-z0-9-]` characters with `-`.
   e. Collapse multiple consecutive hyphens to a single `-`.
   f. Strip leading/trailing hyphens.
3. If the result is empty, raise `DerivationFailedError`.

## Examples

| Input | Output |
|-------|--------|
| `sc-cli-portify-protocol` | `cli-portify` |
| `sc-roadmap-protocol` | `roadmap` |
| `sc-test-workflow-protocol` | `test-workflow` |
| `my-tool` (no prefix/suffix) | `my-tool` |
| `---` (empty after strip) | `DERIVATION_FAILED` |

## Explicit Override

When `--name custom-name` is provided, `derive_cli_name()` returns `custom-name` unchanged.

## Test Coverage

- `uv run pytest tests/ -k "test_cli_name"` — 2 tests, exits 0
- `TestConfigHappyPath::test_cli_name_derivation` — derivation
- `TestConfigHappyPath::test_cli_name_override` — explicit override

## Source Location

- `src/superclaude/cli/cli_portify/config.py:241-258`
- `src/superclaude/cli/cli_portify/models.py:522-549`
