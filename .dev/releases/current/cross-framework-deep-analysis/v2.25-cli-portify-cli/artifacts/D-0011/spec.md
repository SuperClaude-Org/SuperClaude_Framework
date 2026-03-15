# D-0011: models.py Error Code Foundations Spec

**Task**: T02.07 — Implement models.py Error Code Foundations
**Date**: 2026-03-15
**Status**: COMPLETE

---

## Error Code Constants

All 5 Phase 2 error codes defined in `src/superclaude/cli/cli_portify/models.py`:

| Constant | String Value | Exception Class |
|---|---|---|
| `NAME_COLLISION` | `"NAME_COLLISION"` | `NameCollisionError` |
| `OUTPUT_NOT_WRITABLE` | `"OUTPUT_NOT_WRITABLE"` | `OutputNotWritableError` |
| `AMBIGUOUS_PATH` | `"AMBIGUOUS_PATH"` | `AmbiguousPathError` |
| `INVALID_PATH` | `"INVALID_PATH"` | `InvalidPathError` |
| `DERIVATION_FAILED` | `"DERIVATION_FAILED"` | `DerivationFailedError` |

## Exception Hierarchy

```
PortifyValidationError(Exception)   — base class with error_code field
├── NameCollisionError             — error_code = NAME_COLLISION
├── OutputNotWritableError         — error_code = OUTPUT_NOT_WRITABLE
├── AmbiguousPathError             — error_code = AMBIGUOUS_PATH
├── InvalidPathError               — error_code = INVALID_PATH
└── DerivationFailedError          — error_code = DERIVATION_FAILED
```

## Additional Model Types

All types required for Phase 2-9 pipeline:

### Enums
- `PortifyStatus` — 11 values: PENDING, RUNNING, PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, INCOMPLETE, HALT, TIMEOUT, ERROR, FAIL, SKIPPED
- `FailureClassification` — 7 values: MISSING_ARTIFACT, MALFORMED_FRONTMATTER, TIMEOUT, PARTIAL_ARTIFACT, BUDGET_EXHAUSTION, USER_REJECTION, GATE_FAILURE
- `TargetInputType` — 5 values: COMMAND_NAME, COMMAND_PATH, SKILL_DIR, SKILL_NAME, SKILL_FILE

### Dataclasses
- `PortifyConfig` — pipeline configuration with derive_cli_name(), resolve_workflow_path(), to_snake_case()
- `PortifyStepResult` — step execution result with status, failure_classification, resume_context
- `ResumeContext` — step resume metadata (resume_command, resume_step, resume_phase)
- `ResolvedTarget` — 8-field resolved input target
- `ComponentEntry` — single component {name, path, component_type, line_count, purpose}
- `ComponentInventory` — flat component list with source_skill, component_count, total_lines
- `ComponentTree` — tiered tree with command, skill, agents entries
- `CommandEntry` — Tier 0 component (tier=0)
- `SkillEntry` — Tier 1 component (tier=1)
- `AgentEntry` — Tier 2 component (tier=2, found, referenced_in)

### Error Code Constants (v2.24.1 target resolution)
- `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`

---

## Import Path

```python
from superclaude.cli.cli_portify.models import (
    NAME_COLLISION, OUTPUT_NOT_WRITABLE, AMBIGUOUS_PATH, INVALID_PATH, DERIVATION_FAILED,
    PortifyValidationError,
    NameCollisionError, OutputNotWritableError, AmbiguousPathError,
    InvalidPathError, DerivationFailedError,
    PortifyStatus, FailureClassification, TargetInputType,
    PortifyConfig, PortifyStepResult, ResumeContext,
    ResolvedTarget, ComponentTree, ComponentInventory,
    CommandEntry, SkillEntry, AgentEntry, ComponentEntry,
)
```

---

## Test Coverage

Test file: `tests/cli_portify/test_models.py` — 28 tests (all pass)
- TargetInputType enum: 5 members, string values
- ResolvedTarget: 8 fields, construction
- Tiered entries: CommandEntry.tier==0, SkillEntry.tier==1, AgentEntry.tier==2
- ComponentTree: component_count, total_lines, all_source_dirs (deduplication)
- ComponentInventory round-trip via to_flat_inventory()
- to_manifest_markdown() with YAML frontmatter
- Error constants: exact string values verified
