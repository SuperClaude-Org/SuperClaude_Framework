# D-0006: YAML Pipeline File Loader with Schema Validation

## Overview

The YAML pipeline file loader reads `--pipeline @path.yaml`, validates against the phase schema, and produces the same structured phase list as the inline parser.

## Trigger

`--pipeline` value starts with `@` character. The `@` is stripped and the remaining path is resolved relative to the working directory.

## Schema

### Required Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phases | array | Yes | Array of phase definitions |

### Per-Phase Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | `generate` or `compare` |
| id | string | No | Unique phase identifier (auto-assigned if absent) |
| agents | array | Conditional | Required for generate, forbidden for compare |
| depends_on | array | No | Phase IDs this phase depends on |
| config | object | No | Phase-specific configuration overrides |

### Config Fields

| Field | Type | Description |
|-------|------|-------------|
| depth | string | quick/standard/deep override |
| convergence | number | 0.50-0.99 override |
| output | string | Output path override |

## Validation Rules

| Condition | Error Message |
|-----------|---------------|
| Unknown field | `Unknown field in phase definition: <field>. Allowed: id, type, agents, depends_on, config` |
| Missing type | `Missing required field in phase definition: type` |
| Invalid type | `Invalid phase type: <value>. Must be generate or compare` |
| Agents on compare | `compare phase must not specify agents` |
| No agents on generate | `generate phase requires agents field with at least one agent spec` |
| Empty phases | `Pipeline must contain at least one phase` |

## Example YAML (3-phase canonical)

```yaml
phases:
  - id: arch_gen
    type: generate
    agents: ["opus:architect", "haiku:architect"]
  - id: sec_gen
    type: generate
    agents: ["opus:security", "haiku:security"]
    depends_on: ["arch_gen"]
  - id: final_compare
    type: compare
    depends_on: ["sec_gen"]
```

## Output

Structured phase list identical to inline parser output schema (see D-0005).

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` section "Meta-Orchestrator: Pipeline Mode > YAML Pipeline File Loader"

## Deliverable Status

- **Task**: T02.02
- **Roadmap Item**: R-006
- **Status**: COMPLETE
- **Tier**: STRICT
