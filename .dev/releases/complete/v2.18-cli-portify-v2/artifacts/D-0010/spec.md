# D-0010: Contract Schema Versioning Policy

**Task**: T02.01
**Roadmap Items**: R-018, R-019, R-020, R-026
**Date**: 2026-03-08

## Schema Version Format

All portify contracts use semantic versioning in the `schema_version` field:

```
schema_version: "1.0"
```

**Format**: `MAJOR.MINOR` (string, quoted)
- **MAJOR**: Incremented on breaking changes (field removal, type change, semantic redefinition)
- **MINOR**: Incremented on additive changes (new optional fields)

## Backward-Compatibility Rules

| Change Type | Allowed? | Version Impact |
|-------------|----------|----------------|
| Add new optional field | Yes | Minor bump |
| Add new required field | No (breaking) | Major bump |
| Remove field | No (breaking) | Major bump |
| Change field type | No (breaking) | Major bump |
| Change allowed enum values (additive) | Yes | Minor bump |
| Remove enum value | No (breaking) | Major bump |
| Rename field | No (breaking) | Major bump |

## Version Validation on Contract Read

When a phase reads an incoming contract:

1. Parse `schema_version` field
2. Extract `MAJOR.MINOR` components
3. Validate compatibility:
   - **Same MAJOR, same or lower MINOR**: Compatible — proceed
   - **Higher MINOR**: Compatible (additive fields ignored by older consumer) — proceed with advisory warning
   - **Different MAJOR**: Incompatible — abort with actionable error

**Error format on incompatible version**:

```
CONTRACT_VERSION_MISMATCH: Expected schema_version 1.x, got 2.0.
Phase {N} contract at {path} was produced by an incompatible schema version.
Action: Re-run Phase {N-1} to regenerate the contract with schema version 1.x.
```

## Common Header Schema

Every portify contract includes this common header:

```yaml
schema_version: "1.0"          # String. Required. Format: "MAJOR.MINOR"
phase: <int>                    # Integer 0-4. Required. Producing phase number.
status: <enum>                  # String. Required. One of: "passed", "failed", "skipped"
timestamp: <ISO8601>            # String. Required. UTC ISO 8601 datetime.
resume_checkpoint: <string>     # String. Required. Identifier for resume point.
                                # Format: "phase-{N}:{step}" e.g. "phase-0:collision-check"
validation_status:              # Object. Required.
  blocking_passed: <int>        # Integer. Count of blocking validations that passed.
  blocking_failed: <int>        # Integer. Count of blocking validations that failed.
  advisory: <list[string]>      # List of strings. Advisory warnings (non-blocking).
```

**Field Type Summary**:

| Field | Type | Required | Allowed Values |
|-------|------|----------|----------------|
| `schema_version` | string | Yes | Semantic version "MAJOR.MINOR" |
| `phase` | integer | Yes | 0, 1, 2, 3, 4 |
| `status` | string | Yes | "passed", "failed", "skipped" |
| `timestamp` | string | Yes | ISO 8601 UTC datetime |
| `resume_checkpoint` | string | Yes | "phase-{N}:{step}" |
| `validation_status` | object | Yes | See sub-fields |
| `validation_status.blocking_passed` | integer | Yes | >= 0 |
| `validation_status.blocking_failed` | integer | Yes | >= 0 |
| `validation_status.advisory` | list[string] | Yes | Free-form advisory messages |

## Null-Field Policy

Fields for unreached phases or inapplicable data are explicitly set to `null`, never omitted.

**Rules**:
1. All fields defined in a contract schema MUST be present in the emitted YAML
2. Unreached or inapplicable fields are set to `null`
3. Empty lists are represented as `[]`, not `null`
4. Empty objects are represented as `{}`, not `null`
5. A consumer reading a contract can distinguish "not yet computed" (`null`) from "computed and empty" (`[]` / `{}`)

**Example — Phase 0 contract emitted before Phase 1 runs**:

```yaml
schema_version: "1.0"
phase: 0
status: "passed"
timestamp: "2026-03-08T14:30:00Z"
resume_checkpoint: "phase-0:complete"
validation_status:
  blocking_passed: 3
  blocking_failed: 0
  advisory: []
# Phase 0 specific fields populated:
workflow_path: "src/superclaude/skills/sc-cleanup-audit-protocol/"
api_snapshot_hash: "sha256:abc123..."
collision_status: "clean"
pattern_scan_result: "supported"
# Phase 1+ fields not yet populated:
component_inventory: null
step_graph: null
```

## Contract File Naming Convention

| Phase | Contract File | Producer | Consumer |
|-------|--------------|----------|----------|
| 0 | `portify-prerequisites.yaml` | Phase 0 | Phase 1 |
| 1 | `portify-analysis.yaml` | Phase 1 | Phase 2 |
| 2 | `portify-spec.yaml` | Phase 2 | Phase 3 |
| 3 | `portify-codegen.yaml` | Phase 3 | Phase 4 |
| 4 | `portify-integration.yaml` | Phase 4 | Return contract |
| Return | embedded in return contract | Phase 5 / aggregator | Caller |

## Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial schema definition |

## References

- OQ-004: Integration schema resolution (decisions.yaml)
- OQ-007: Approval gate mechanism resolution (decisions.yaml)
- Roadmap M2.1: Contract Infrastructure and Schema Versioning
