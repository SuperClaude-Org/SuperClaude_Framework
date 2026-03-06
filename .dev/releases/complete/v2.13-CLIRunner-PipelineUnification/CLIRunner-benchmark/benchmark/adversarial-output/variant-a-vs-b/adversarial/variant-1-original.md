---
title: "Complete Pipeline Unification: Sprint Must Adopt execute_pipeline()"
author: analysis-agent-alpha
scope: src/superclaude/cli/{pipeline,sprint,roadmap}/
analysis_type: architectural-refactoring-proposal
position: pro-unification
confidence: 0.85
---

# Position: Sprint Must Be Refactored to Use execute_pipeline() as the Single Orchestration Point

## 1. Problem Statement

The SuperClaude CLI has a shared pipeline layer (`src/superclaude/cli/pipeline/`) that was extracted from sprint to provide generic orchestration. Roadmap uses it. Sprint does not. This half-completed extraction has produced:

- Two independent orchestration loops with divergent behavior
- Two incompatible file-passing strategies (inline vs --file)
- Two separate state management systems
- Two signal handling implementations
- Process method overrides that exist only for debug logging
- Dead code from the incomplete migration

The proposal is to complete the extraction: make sprint use `execute_pipeline()` and push sprint-specific features into callbacks.

## 2. Evidence: The Current Architecture

### 2a. Sprint has its own orchestration loop

File: `src/superclaude/cli/sprint/executor.py`, lines 32-304

Sprint's `execute_sprint()` is a 300-line function that reimplements what `pipeline/executor.py:execute_pipeline()` provides:

- Step sequencing (iterating over phases)
- Process lifecycle management (launch, poll, wait, terminate)
- Timeout enforcement
- Signal handling / cancellation
- Exit code interpretation
- Status determination
- Result collection

On top of this, sprint adds TUI updates, output monitoring, watchdog stall detection, tmux integration, and diagnostic collection. These are sprint-specific features, but they are interleaved with generic orchestration logic rather than composed via callbacks.

Evidence: Searching for `execute_pipeline` in `src/superclaude/cli/sprint/` returns zero matches — sprint does not import or call the shared executor.

### 2b. Roadmap cleanly uses the pipeline

File: `src/superclaude/cli/roadmap/executor.py`, lines 472-512

Roadmap's `execute_roadmap()` delegates to `execute_pipeline()` and passes step-specific logic via the `roadmap_run_step` callable and `on_step_start`/`on_step_complete` callbacks. This is the intended composition pattern.

### 2c. File-passing divergence is a symptom

Sprint uses inline `@file` in prompt strings (`sprint/process.py:54`). Roadmap uses `--file` flags via `extra_args` (`roadmap/executor.py:112-116`). This divergence exists because each consumer independently decides how to construct its subprocess — there is no shared strategy at the pipeline level. If both used the same executor, this would be a single configurable concern.

### 2d. Two state management systems

Sprint persists state via `SprintLogger` → `execution-log.jsonl` + `.sprint-exitcode` + per-phase result files. Roadmap persists state via `_save_state()` → `.roadmap-state.json`. Resume logic is completely independent: sprint uses `--start N` (phase range), roadmap uses `--resume` (gate-based skip). Neither knows about the other's state format.

### 2e. Process method overrides for debug logging

`sprint/process.py:25` subclasses `pipeline/process.py:ClaudeProcess` but overrides `start()`, `wait()`, and `terminate()` with near-identical code. The only difference is sprint-specific `debug_log()` calls — about 4-6 extra lines per method, totaling ~90 lines of duplicated process management. The pipeline base class has no hook points for logging.

### 2f. Dead code in roadmap

`roadmap/executor.py:53-76` defines `_build_subprocess_argv()` which manually constructs a `claude` command list. This function is never called — `roadmap_run_step()` at line 103 uses `ClaudeProcess` directly. Grep across the entire source tree (excluding tests) confirms zero call sites.

## 3. Proposed Unified Architecture

### 3a. execute_pipeline() becomes the single orchestration point

Both sprint and roadmap define their steps as `list[Step | list[Step]]` and pass them to `execute_pipeline()` with consumer-specific callbacks:

```
execute_pipeline(
    steps=...,
    config=...,
    run_step=sprint_run_step,        # or roadmap_run_step
    on_step_start=tui.on_start,      # sprint: TUI update / roadmap: print
    on_step_complete=tui.on_complete, # sprint: TUI + diagnostics / roadmap: print
    on_state_update=logger.save,     # sprint: jsonl / roadmap: json
    cancel_check=signal.check,       # sprint: SignalHandler / roadmap: lambda
)
```

### 3b. Sprint-specific features become callbacks and wrappers

| Sprint Feature | Current Location | Proposed Location |
|---|---|---|
| TUI updates | Inline in poll loop | `on_step_start` / `on_step_complete` callbacks |
| Output monitoring | Inline in poll loop | Wrapper around `run_step` that starts/stops monitor |
| Watchdog stall detection | Inline in poll loop | Polling wrapper around `run_step` or separate thread |
| Tmux integration | Inline in poll loop | `on_step_start` callback |
| Diagnostic collection | After poll loop | `on_step_complete` callback |
| Signal handling | `SignalHandler` class | `cancel_check` callback (already supported) |
| Phase status parsing | `_determine_phase_status()` | Gate criteria on sprint Steps (already supported) |

### 3c. File passing becomes a Step-level concern

The `Step` dataclass already has an `inputs: list[Path]` field. The file-passing strategy (inline embedding vs `--file` vs `@file` reference) becomes a method on `ClaudeProcess` or a configurable field on `Step`, not a per-consumer decision. Default: inline embedding (works everywhere, proven by sprint).

### 3d. State management gets a shared interface

```python
class StateManager(Protocol):
    def save(self, results: list[StepResult]) -> None: ...
    def load_resume_point(self) -> int | None: ...
```

Sprint and roadmap each provide their own `StateManager` implementation with their serialization format, but the executor calls the same interface.

## 4. Benefits of Unification

### 4a. Bug fixes apply everywhere
Currently, a fix to retry logic in `pipeline/executor.py` benefits roadmap but not sprint. Sprint has no retry logic at all — a bug that would be fixed for free if sprint used the shared executor.

### 4b. New features compose
The pipeline already supports parallel step groups (`list[Step]`). Sprint cannot use this because it has its own loop. If sprint used `execute_pipeline()`, it could run independent phases in parallel with no additional work.

### 4c. Testing surface shrinks
Instead of testing two orchestration loops, you test one. Sprint's tests focus on its callbacks (TUI, monitoring, diagnostics). Roadmap's tests focus on its callbacks (gate criteria, prompts). The shared executor tests cover sequencing, retry, parallel dispatch, and cancellation.

### 4d. The --file vs inline debate disappears
It becomes a single decision point in `ClaudeProcess.build_command()` or `Step`, not a per-consumer architectural choice.

## 5. Estimated Scope

| Component | Action | Estimated Effort |
|---|---|---|
| `pipeline/executor.py` | Add hook points for polling/monitoring | Small — extend existing callbacks |
| `pipeline/process.py` | Add logging hooks, configurable file-passing | Small |
| `sprint/executor.py` | Refactor to use `execute_pipeline()` with callbacks | Medium — main work |
| `sprint/process.py` | Remove method overrides, use base hooks | Small |
| `sprint/models.py` | Express phases as `Step` instances with gates | Small |
| `roadmap/executor.py` | Remove dead `_build_subprocess_argv()` | Trivial |
| State management | Extract shared protocol, implement per-consumer | Medium |
| Tests | Update sprint tests to test callbacks, not loop | Medium |

## 6. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Sprint's TUI polling is tightly coupled to the execution loop | Medium | The `run_step` wrapper can include the poll loop internally |
| Watchdog stall detection requires access to monitor state during execution | Medium | Pass monitor as context to `run_step` wrapper |
| Sprint has features the pipeline executor doesn't model (phase-level vs step-level) | Low | Sprint maps phases to steps — conceptually identical |
| Regression risk in sprint behavior | High | Sprint's existing test suite validates behavior regardless of orchestration layer |
