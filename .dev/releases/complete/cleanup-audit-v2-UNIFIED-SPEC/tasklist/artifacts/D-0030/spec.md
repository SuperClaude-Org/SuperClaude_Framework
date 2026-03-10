# D-0030: Output Artifacts Specification

**Task**: T04.04 — Output Artifact Schemas
**Status**: Complete

## Purpose

Define JSON schemas for the two mandatory output artifacts: coverage and validation.

## Coverage Artifact Schema

```json
{
  "type": "object",
  "required": ["total_files_scanned", "tier_breakdown", "timestamp", "phases_completed"],
  "properties": {
    "total_files_scanned": {"type": "integer", "minimum": 0},
    "tier_breakdown": {
      "type": "object",
      "properties": {
        "remove": {"type": "integer"},
        "refactor": {"type": "integer"},
        "keep": {"type": "integer"},
        "unclassified": {"type": "integer"}
      }
    },
    "phases_completed": {"type": "array", "items": {"type": "integer"}},
    "timestamp": {"type": "string", "format": "date-time"},
    "scan_duration_seconds": {"type": "number"}
  }
}
```

## Validation Artifact Schema

```json
{
  "type": "object",
  "required": ["consistency_rate", "sample_size", "per_tier_rates"],
  "properties": {
    "consistency_rate": {"type": "number", "minimum": 0, "maximum": 1},
    "sample_size": {"type": "integer"},
    "total_files": {"type": "integer"},
    "per_tier_rates": {"type": "object"},
    "mismatches": {"type": "array", "items": {"type": "object"}},
    "seed": {"type": "string"}
  }
}
```

## Constraints

- Both artifacts must validate against their schemas before being written.
- Missing required fields cause a hard failure, not a warning.
- Artifacts are written as pretty-printed JSON (2-space indent).
