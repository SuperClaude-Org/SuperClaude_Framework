# D-0034: Override Handler Specification

**Task**: T04.08 — Capability Override Handler
**Status**: Complete

## Purpose

Allow users to reorder or disable analysis capabilities via an override flag.

## Override Schema

```json
{
  "overrides": [
    {"capability": "string", "action": "enable|disable|reorder", "priority": "integer"}
  ]
}
```

## Supported Capabilities

| Capability Name | Default Priority | Description |
|----------------|-----------------|-------------|
| `import_analysis` | 1 | Scan import/require statements |
| `reference_check` | 2 | Check symbol references |
| `test_coverage` | 3 | Analyze test coverage data |
| `git_history` | 4 | Examine commit history |
| `cross_reference` | 5 | Cross-module dependency analysis |

## Reorder Logic

- User provides a list of capability names in desired order.
- Capabilities are executed in the specified order.
- Omitted capabilities retain their default position after listed ones.

## Invalid Name Rejection

- Any capability name not in the supported list causes a validation error.
- Error message lists the invalid name and all valid options.
- Partial overrides are rejected: all-or-nothing validation.

## CLI Interface

```
--capability-order import_analysis,git_history,reference_check
--disable-capability test_coverage
```

## Constraints

- At least one capability must remain enabled.
- Disabling all capabilities is a validation error.
- Override state is logged and included in the report metadata.
