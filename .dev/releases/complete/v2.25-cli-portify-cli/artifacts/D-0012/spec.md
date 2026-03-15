---
deliverable: D-0012
task: T03.01
title: Core Domain Models
status: PASS
---

# D-0012: Core Domain Models

## Model Hierarchy

All models defined in `src/superclaude/cli/cli_portify/models.py`.

### Enums

| Model | Values |
|-------|--------|
| `PortifyPhaseType` | PREREQUISITES, ANALYSIS, USER_REVIEW, SPECIFICATION, SYNTHESIS, CONVERGENCE |
| `ConvergenceState` | NOT_STARTED, REVIEWING, INCORPORATING, SCORING, CONVERGED, ESCALATED |
| `PortifyStatus` | PENDING, RUNNING, PASS, PASS_NO_SIGNAL, PASS_NO_REPORT, INCOMPLETE, HALT, TIMEOUT, ERROR, FAIL, SKIPPED |
| `PortifyOutcome` | SUCCESS, FAILURE, TIMEOUT, INTERRUPTED, HALTED, DRY_RUN |

### Dataclasses

| Model | Description |
|-------|-------------|
| `PortifyConfig` | Full pipeline configuration (workflow_path, cli_name, etc.) |
| `PortifyStep` | Single pipeline step with phase_type, prompt, timeout |
| `PortifyStepResult` | Execution result of a single step |
| `MonitorState` | OutputMonitor telemetry (8 fields per NFR-009) |

### Executor-internal

| Model | Description |
|-------|-------------|
| `TurnLedger` | Turn budget tracker; `can_launch()` returns False when exhausted (FR-040) |

## Base Type Inheritance

`PortifyConfig` contains fields equivalent to `PipelineConfig` (work_dir, dry_run, max_turns, model, debug).
`PortifyStep` contains fields equivalent to `Step` (prompt, output_file, timeout_seconds, retry_limit).
`PortifyStepResult` contains fields equivalent to `StepResult` (step_name, status, duration_seconds).

## Validation

`uv run pytest tests/ -k "test_domain_models"` → 13 passed
