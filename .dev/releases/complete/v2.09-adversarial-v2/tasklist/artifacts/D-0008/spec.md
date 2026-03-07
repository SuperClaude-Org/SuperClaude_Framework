# D-0008: Cycle Detection with Descriptive Error Messages

## Overview

DFS-based cycle detection integrated into the DAG builder that aborts with a descriptive error showing the exact cycle path when a circular dependency is found.

## Algorithm

1. Initialize all nodes as `UNVISITED`
2. For each `UNVISITED` node, start DFS traversal
3. Mark entering node as `IN_PROGRESS`
4. For each neighbor (depends_on target):
   - `IN_PROGRESS` -> cycle detected, extract path
   - `UNVISITED` -> recurse
   - `VISITED` -> skip
5. Mark exiting node as `VISITED`

## Error Format

```
Circular dependency detected: A -> B -> A
Circular dependency detected: A -> B -> C -> A
```

## Integration Point

Runs during `dag_builder.step_3_assign_levels`, before level assignment. Must complete before any phase execution begins.

## Test Cases

| Input | Expected Error |
|-------|---------------|
| A depends_on B, B depends_on A | `Circular dependency detected: A -> B -> A` |
| A -> B -> C -> A | `Circular dependency detected: A -> B -> C -> A` |
| Self-dependency: A depends_on A | `Circular dependency detected: A -> A` |
| Valid DAG (no cycles) | No error |

## Deliverable Status

- **Task**: T02.04
- **Roadmap Item**: R-008
- **Status**: COMPLETE
- **Tier**: STANDARD
