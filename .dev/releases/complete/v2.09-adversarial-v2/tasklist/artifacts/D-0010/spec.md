# D-0010: Dry-Run Render for Pipeline Execution Plan

## Overview

Dry-run mode validates the DAG and outputs the execution plan to console/file without executing any phases. Triggered by `--dry-run` in combination with `--pipeline`.

## Output Format

```markdown
# Pipeline Execution Plan (Dry Run)
- Total phases: <N>
- Parallel groups: <N>
- Estimated execution levels: <N>

## Phase Details
| Phase ID | Type | Agents | Depends On | Level | Parallel Group |
|----------|------|--------|------------|-------|----------------|
| ...      | ...  | ...    | ...        | ...   | ...            |

## Execution Order
Level 0: <phase_ids> (parallel)
Level 1: <phase_ids> (parallel)
...

## Estimated Token Costs
- generate phases: ~<N> tokens each
- compare phases: ~<N> tokens each
- Total estimated: ~<N> tokens
```

## Validation Guarantee

If dry-run completes without error, the pipeline definition is valid:
- All phase types recognized
- All depends_on references valid
- No circular dependencies
- DAG can be constructed and topologically sorted

## Output Routing

- Default: console (stdout)
- File: `--output <path>` writes to file

## SC-002 Compliance

Dry-run output for the 3-phase canonical workflow must match the actual execution plan (phase order, parallelization groups).

## Deliverable Status

- **Task**: T02.06
- **Roadmap Item**: R-010
- **Status**: COMPLETE
- **Tier**: STANDARD
