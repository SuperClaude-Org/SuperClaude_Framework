# D-0005: Inline Shorthand Parser for Pipeline Phase Definitions

## Overview

The inline shorthand parser accepts `--pipeline "<shorthand>"` syntax and returns a structured phase list with `generate:<agents>` and `compare` phase type support.

## Grammar

```
pipeline     ::= phase_group ( '->' phase_group )*
phase_group  ::= phase ( '|' phase )*
phase        ::= PHASE_ID ':' phase_type | phase_type
phase_type   ::= 'generate:' AGENT_LIST | 'compare'
```

### Tokens

| Token | Symbol | Meaning |
|-------|--------|---------|
| ARROW | `->` | Sequential dependency |
| PIPE | `\|` | Parallel grouping |
| GENERATE | `generate:` | Generate phase type |
| COMPARE | `compare` | Compare phase type |
| AGENT_LIST | `a,b,...` | Comma-separated agent specs |
| PHASE_ID | `[a-zA-Z_][a-zA-Z0-9_]*` | Named phase identifier |

## Output Schema

```yaml
phases:
  - id: string        # Auto-assigned or user-named
    type: string       # "generate" | "compare"
    agents: [string]   # Agent specs (empty for compare)
    depends_on: [string]  # Phase IDs this phase depends on
    parallel_group: int   # Phases with same group run concurrently
```

## Parse Examples

### Simple 3-phase
Input: `generate:opus:architect,haiku:architect -> generate:opus:security,haiku:security -> compare`
Output:
- phase_1: generate [opus:architect, haiku:architect], depends_on: [], group: 0
- phase_2: generate [opus:security, haiku:security], depends_on: [phase_1], group: 1
- phase_3: compare [], depends_on: [phase_2], group: 2

### Parallel generate
Input: `generate:opus:architect,haiku:architect | generate:opus:security,haiku:security -> compare`
Output:
- phase_1: generate [opus:architect, haiku:architect], depends_on: [], group: 0
- phase_2: generate [opus:security, haiku:security], depends_on: [], group: 0
- phase_3: compare [], depends_on: [phase_1, phase_2], group: 1

### Named phases
Input: `arch:generate:opus:architect,haiku:architect -> sec:generate:opus:security -> final:compare`
Output:
- arch: generate [opus:architect, haiku:architect], depends_on: [], group: 0
- sec: generate [opus:security], depends_on: [arch], group: 1
- final: compare [], depends_on: [sec], group: 2

## Error Messages

| Condition | Message |
|-----------|---------|
| Missing arrow | `Malformed shorthand: expected -> between phase groups, got: <token>` |
| Unmatched pipe | `Malformed shorthand: unmatched \| in phase group: <group>` |
| Unknown type | `Unknown phase type: <type>. Expected generate:<agents> or compare` |
| Empty agents | `generate phase requires at least one agent: generate:<agent_spec>` |
| Duplicate name | `Duplicate phase name: <name>. Each phase must have a unique identifier` |

## Implementation Location

`src/superclaude/skills/sc-adversarial-protocol/SKILL.md` section "Meta-Orchestrator: Pipeline Mode > Inline Shorthand Parser"

## Deliverable Status

- **Task**: T02.01
- **Roadmap Item**: R-005
- **Status**: COMPLETE
- **Tier**: STRICT
