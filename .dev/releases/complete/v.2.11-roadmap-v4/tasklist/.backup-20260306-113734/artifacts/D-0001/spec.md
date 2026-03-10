# D-0001: Extended Deliverable Schema Specification

## Overview

The `Deliverable` dataclass and `DeliverableKind` enum extend the pipeline model layer with a structured deliverable representation supporting decomposition passes and metadata attachment.

## Location

- **Module**: `src/superclaude/cli/pipeline/models.py`
- **Exports**: `src/superclaude/cli/pipeline/__init__.py`

## DeliverableKind Enum

Six valid values:

| Value | Purpose |
|-------|---------|
| `implement` | Code implementation deliverable (default) |
| `verify` | Verification/test deliverable paired with implement |
| `invariant_check` | Invariant validation (M2 pass) |
| `fmea_test` | Failure mode analysis test (M3 pass) |
| `guard_test` | Guard condition test (M3 pass) |
| `contract_test` | Contract verification test (M4 pass) |

- `DeliverableKind.from_str(value)` raises `ValueError` on unknown values
- All six values are validated; unknown values are never silently accepted

## Deliverable Dataclass

```python
@dataclass
class Deliverable:
    id: str                                    # e.g. "D-0001", "D-0001.a"
    description: str                           # Human-readable description
    kind: DeliverableKind = IMPLEMENT          # Defaults for backward compat
    metadata: dict = field(default_factory=dict)  # Attachment point for M2-M4
```

## Backward Compatibility

- Pre-extension deliverables without `kind` field parse successfully via `from_dict()` and default to `implement`
- Pre-extension deliverables without `metadata` field default to empty dict `{}`
- Existing `PipelineConfig`, `Step`, `StepResult` types are unchanged

## Serialization

- `to_dict()` → `{"id": ..., "description": ..., "kind": "implement", "metadata": {...}}`
- `from_dict(data)` → `Deliverable` with defaults for missing fields
- Round-trip: `Deliverable.from_dict(d.to_dict()) == d` (value equality)
