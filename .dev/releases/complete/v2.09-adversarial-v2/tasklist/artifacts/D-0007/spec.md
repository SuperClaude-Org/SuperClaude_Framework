# D-0007: DAG Builder from Phase Definitions

## Overview

The DAG builder constructs a directed acyclic graph from the structured phase list, identifying parallel phases (same dependency level) and sequential gates (dependency edges) for execution scheduling.

## Algorithm

### Step 1: Create Nodes
- One node per phase definition
- Node schema: `{id, type, agents, config, level}`

### Step 2: Create Edges
- Directed edges from `depends_on` references
- Edge schema: `{from, to}` where `from` must complete before `to` starts
- Implicit edges from `->` shorthand ordering

### Step 3: Assign Levels (Topological Sort)
- Algorithm: Kahn's algorithm (BFS-based)
- Level 0: Phases with no dependencies
- Level N+1: Phases depending only on level-N phases
- Phases at the same level can execute concurrently

## Output Schema

```yaml
dag:
  nodes: [{id, type, agents, config, level}]
  edges: [{from, to}]
  levels: [[phase_ids_at_level_0], [phase_ids_at_level_1], ...]
  execution_order: [phase_ids_in_topological_order]
```

## Canonical 3-Phase Example

Input: `generate:opus:architect,haiku:architect -> generate:opus:security -> compare`

```yaml
dag:
  nodes:
    - {id: phase_1, type: generate, level: 0}
    - {id: phase_2, type: generate, level: 1}
    - {id: phase_3, type: compare, level: 2}
  edges:
    - {from: phase_1, to: phase_2}
    - {from: phase_2, to: phase_3}
  levels:
    - [phase_1]
    - [phase_2]
    - [phase_3]
  execution_order: [phase_1, phase_2, phase_3]
```

## Validation

- Cycle detection runs during step 3 (see D-0008)
- Reference integrity runs during step 2 (see D-0009)

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` section "Meta-Orchestrator: Pipeline Mode > DAG Builder"

## Deliverable Status

- **Task**: T02.03
- **Roadmap Item**: R-007
- **Status**: COMPLETE
- **Tier**: STRICT
