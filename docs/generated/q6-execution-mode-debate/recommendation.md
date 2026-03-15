# Final Recommendation -- Q6: execution_mode Annotation Location

## Verdict: 3a (Index-level column)

**Confidence**: 92%
**Convergence**: 82% across all advocates

## One-paragraph rationale

The `execution_mode` annotation should be a new column in the Phase Files table of `tasklist-index.md`. This is the only location that satisfies all five evaluation dimensions without trade-offs. The runner already reads the index file in `discover_phases()` before entering the phase execution loop, so the annotation is available at exactly the right time. Phase-level granularity is sufficient for all known and foreseeable use cases (no existing or planned sprint has mixed-mode phases). The change requires approximately 10 lines of parser code, 1 field addition to the `Phase` dataclass, and a column addition to the generator template. It is fully backward-compatible (missing column defaults to `claude`) and has a clean, non-breaking evolution path to dual-level (3d) if mixed-mode phases ever become necessary.

## Why not the others

| Variant | Elimination reason |
|---|---|
| 3b (YAML frontmatter) | Introduces a format convention (YAML in markdown) that exists nowhere else in the tasklist ecosystem. Solves no problem that 3a does not solve more simply. |
| 3c (Per-task field) | Fails the primary constraint: task metadata is not available before subprocess launch without restructuring the parser. Also violates YAGNI -- task-level granularity is not needed for any known use case. |
| 3d (Dual-level) | Correct in principle but pays complexity cost (two parse sites, inheritance resolution) for a scenario that has not materialized. Clean migration from 3a to 3d means we can defer this cost. |

## Unresolved conflicts

1. **Self-describing phase files**: Advocates 3b and 3c raised a valid point that individual phase files do not indicate their execution mode under 3a. This is accepted as a minor documentation gap, not a functional issue. If desired, a comment line (not parsed) could be added to phase files: `<!-- Execution Mode: python -->`.

## Concrete next steps

1. Add `execution_mode: str = "claude"` to the `Phase` dataclass in `models.py`
2. Extend `discover_phases()` to extract the Execution Mode column from the Phase Files table
3. Update the `/sc:tasklist` generator template to emit the new column
4. Add the `phase.execution_mode` branch in `execute_sprint()`
5. Write tests for backward compatibility (index without the column)
