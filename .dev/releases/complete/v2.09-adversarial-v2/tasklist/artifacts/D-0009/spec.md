# D-0009: Reference Integrity Validation for depends_on Phase IDs

## Overview

Validates that all `depends_on` phase IDs reference existing phases. Reports ALL invalid references in a single error (not fail-fast on first).

## Algorithm

1. Build set of all defined phase IDs from structured phase list
2. For each phase, check each `depends_on` entry against the ID set
3. Collect ALL invalid references
4. If any found, report all in a single error message

## Error Format

- Single: `Unknown phase reference: <id>`
- Multiple: `Unknown phase references: <id1>, <id2>`

## Integration Point

Runs during `dag_builder.step_2_create_edges`, before cycle detection.

## Test Cases

| Input | Expected |
|-------|----------|
| depends_on: ["nonexistent"] | `Unknown phase reference: nonexistent` |
| depends_on: ["bad1", "bad2"] | `Unknown phase references: bad1, bad2` |
| Valid references | No error |

## Deliverable Status

- **Task**: T02.05
- **Roadmap Item**: R-009
- **Status**: COMPLETE
- **Tier**: STANDARD
