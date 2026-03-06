# D-0035: Guard Analysis Pipeline Pass Specification

## Pipeline Position

```
M1 (decomposition) → M2 (invariant+FMEA) → M3 (guard analysis) → M4 (data flow)
```

Guard analysis runs after M2 combined pass and before M4 data flow tracing.

## Cross-Reference Schema

### Invariant Cross-Reference
- For each guard variable, lookup matching `InvariantEntry` by `variable_name`
- Also checks stripped version (without leading `_`)
- Result: `dict[guard_variable, InvariantEntry | None]`

### FMEA Severity Cross-Reference
- Input: `fmea_severity_map: dict[deliverable_id, severity_level]`
- Elevation rule: guard ambiguity + FMEA severity in {high, critical} → silent corruption
- Output: `fmea_elevations: list[str]` (elevated variable names)

## Output Section Format

### Guard Analysis Section
- Header: `## Guard Analysis`
- Summary: guards detected, ambiguous guards, FMEA elevations
- State enumeration table: Variable, Kind, States, Ambiguous, Invariant Registered, FMEA Elevated
- Guard resolution subsection (from T03.02)
- Release Gate Rule 2 status (blocking/clear)

## API

```python
run_guard_analysis_pass(
    deliverables: list[Deliverable],
    invariant_output: InvariantRegistryOutput | None = None,
    fmea_severity_map: dict[str, str] | None = None,
) -> GuardAnalysisOutput
```

## Implementation

- File: `src/superclaude/cli/pipeline/guard_pass.py`
- Exports: `run_guard_analysis_pass`, `GuardAnalysisOutput`
- Pipeline registration: exported via `__init__.py`
- NFR-007 compliant
