# D-0021: Artifact Routing Specification

## Overview

Resolves `merged_output` and `all_variants` path references between dependent phases and passes resolved paths as inputs to consuming phases.

## Artifact Types

| Type | Produced By | Path Pattern |
|------|------------|--------------|
| merged_output | generate, compare | `<pipeline_output>/<phase_id>/merged-output.md` |
| all_variants | generate | `<pipeline_output>/<phase_id>/variant-*.md` |

## Routing Contract

- generate produces: merged_output + all_variants
- compare produces: merged_output
- compare consumes: all_variants from dependencies (>=2 required)

## Error Handling

- Missing artifact: STOP with descriptive error
- Insufficient variants for compare: STOP with count

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Meta-Orchestrator section, Artifact Routing subsection.

## Deliverable Status

- **Task**: T03.05
- **Roadmap Item**: R-021
- **Status**: COMPLETE
- **Tier**: STRICT
