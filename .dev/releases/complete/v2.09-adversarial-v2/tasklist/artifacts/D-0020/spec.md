# D-0020: Phase Executor Specification

## Overview

Phase Executor translates each pipeline phase configuration into a Mode A (compare) or Mode B (generate) invocation, scoped to an isolated phase output directory.

## Translation Rules

| Phase Type | Maps To | Key Parameters |
|-----------|---------|----------------|
| `generate` | Mode B | --source, --generate, --agents from phase config |
| `compare` | Mode A | --compare with variant paths from artifact routing |

## Output Isolation

Each phase writes to `<pipeline_output>/<phase_id>/`. Directory created before execution begins.

## Execution Flow

1. Read phase config (type, agents, dependencies, overrides)
2. Resolve input artifacts from dependency phases
3. Create isolated output directory
4. Translate phase type to Mode A/B parameters
5. Execute Mode A/B with phase-specific parameters
6. Collect return contract from execution
7. Update pipeline manifest with results

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` — Meta-Orchestrator section, Phase Executor subsection.

## Acceptance Test

Single-phase pipeline `--pipeline "generate:opus:architect"` produces output identical to direct Mode B invocation.

## Deliverable Status

- **Task**: T03.04
- **Roadmap Item**: R-020
- **Status**: COMPLETE
- **Tier**: STRICT
