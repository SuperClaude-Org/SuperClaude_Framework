---
component: sprint-executor
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude Sprint Executor

## 1. Design Philosophy

The sprint executor exists to run multi-phase, multi-task Claude agent workflows from declarative tasklist files, with deterministic phase-level checkpointing and budget control. The design philosophy centers on **supervised orchestration**: the executor is a thin Python supervisor that manages subprocess lifecycle, output monitoring, gate evaluation, and budget accounting — while delegating all task-level reasoning to Claude subprocess instances.

**Why this design exists**: Running complex multi-task agent workflows directly as a single Claude session creates token budget exhaustion, loss of intermediate progress on failure, and no mechanism for human review between phases. The sprint executor decouples the orchestrator (Python supervisor) from the agent (Claude subprocess) to enable: phase-level restart (`--start N`), budget-tracked multi-task execution, and observable progress via TUI and logging.

**Trade-off**: The supervisor model introduces subprocess spawn overhead per phase and constrains task execution to one subprocess per phase. A single Claude subprocess handles all tasks in a phase sequentially, which means a long-running task in Phase 2 blocks all subsequent Phase 2 tasks. The benefit is simplicity in the supervisor loop and clean phase-level isolation.

## 2. Execution Model

`execute_sprint(config: SprintConfig)` (`src/superclaude/cli/sprint/executor.py:490`) implements the main orchestration loop:

For each active phase:
1. Spawn `ClaudeProcess(config, phase)` — a sprint-specific subprocess (`src/superclaude/cli/sprint/process.py:88`)
2. Start `OutputMonitor` thread tracking output byte growth
3. Poll TUI in a monotonic-clock timeout loop
4. On process exit, parse result file for CONTINUE/HALT signal
5. Record `PhaseResult`; decide whether to proceed or halt

**ClaudeProcess**: Extends `_PipelineClaudeProcess` with sprint-specific prompt builder (`build_prompt()`) and lifecycle hooks (spawn, signal, exit) wired via factory closures. Timeout is computed as `max_turns * 120 + 300` seconds — a linear function of turn budget ensuring timeout scales with expected workload (`src/superclaude/cli/sprint/process.py:108`).

**TurnLedger**: `execute_phase_tasks()` (`src/superclaude/cli/sprint/executor.py:349`) uses `TurnLedger` for budget allocation across tasks in a phase. Ledger enforces monotonicity (consumed can only increase), tracks reimbursement at 80% rate for PASS tasks, and enforces `minimum_allocation=5` turns before launching a subprocess (`src/superclaude/cli/sprint/models.py:466`). Tasks below minimum allocation are skipped and logged as remaining.

**Phase discovery**: `load_sprint_config()` (`src/superclaude/cli/sprint/config.py:104`) discovers phase files matching `PHASE_FILE_PATTERN` regex — supporting 4 canonical filename conventions (e.g., `phase-1-tasklist.md`, `p1-tasklist.md`). Phase range filtering via `--start` / `--end` produces `config.active_phases`.

**Tmux integration**: By default, sprint launches inside a tmux session for SSH-disconnect resilience. `launch_in_tmux()` re-launches the sprint command inside a named tmux session; `update_tail_pane()` tails output to a tmux split pane.

## 3. Quality Enforcement

**Gate validation**: After each phase, `gate_passed(output_file, criteria)` (`src/superclaude/cli/pipeline/gates.py:20`) validates the phase output file against tier-proportional criteria. STRICT gates include semantic checks (pure Python lambdas). Gate failure triggers HALT unless `--shadow-gates` is active.

**Shadow gate mode**: `--shadow-gates` runs `TrailingGateRunner` (`src/superclaude/cli/pipeline/trailing_gate.py`) as a daemon thread — gates execute asynchronously without blocking the main executor loop. Failures are logged as metrics-only warnings, not execution halts. This allows pipeline progress monitoring without enforcement during development or debugging.

**Stall detection**: `detect_error_max_turns()` and byte-growth monitoring in `OutputMonitor` detect processes that have stopped producing output. `stall_timeout` + `stall_action` (kill/warn) provide configurable watchdog behavior.

**Trade-off**: Shadow gates trade safety for observability — pipelines can proceed past failing gates, accumulating invalid artifacts. This is appropriate for development but must never be used in production sprint runs where downstream tasks depend on upstream gate outputs.

## 4. Error Handling Strategy

**Phase-level HALT**: If `gate_passed()` returns `(False, reason)` and retries are exhausted, the sprint halts at that phase. All results up to that point are written to `results/` dir on disk. `--start N` allows re-entry from the halted phase after human intervention.

**Signal handling**: `SignalHandler` installs SIGINT/SIGTERM handlers. On signal, `shutdown_requested = True` is set; the executor cleans up the active subprocess and writes `INTERRUPTED` outcome before exiting.

**Budget exhaustion**: If `TurnLedger.available()` falls below `minimum_allocation`, remaining tasks are returned as unattempted. The executor logs which tasks were skipped and records budget exhaustion in the phase result.

**Diagnostic chain**: On failure, the 4-stage diagnostic chain (`run_diagnostic_chain()`) can be triggered: troubleshoot → adversarial analysis × 2 → summary. This is runner-side and does not consume TurnLedger turns (diagnostic invocations are not billed against task budget per spec Gap 2).

**Trade-off**: Phase-level granularity for `--start` restart means that if a phase completes 9 tasks and fails on task 10, all 10 tasks must re-run on restart (the executor cannot resume mid-phase). Intra-phase checkpoint granularity is not supported.

## 5. Extension Points

- `--start` / `--end` phase range — limit execution to a subset of phases without modifying the tasklist.
- `--shadow-gates` — decouple gate evaluation from execution blocking.
- `stall_timeout` + `stall_action` — configurable watchdog per deployment environment.
- `_subprocess_factory` parameter on `execute_phase_tasks` — injectable for test-time subprocess substitution without modifying executor code (`src/superclaude/cli/sprint/executor.py:356`).
- `TrailingGatePolicy` injectable on sprint executor — allows custom gate evaluation policies per consumer (T07.01 design).
- `--no-tmux` flag — disable tmux wrapping for environments where tmux is unavailable.

## 6. System Qualities

**Maintainability**: Sprint and roadmap share the same `execute_pipeline()` function and `ClaudeProcess` base class. Changes to the generic executor benefit both consumers. The sprint-specific `execute_sprint()` is a thin loop over `execute_phase_tasks()` with TUI and logging decorators.

**Weakness**: The supervisor loop is monolithic — TUI polling, timeout enforcement, and gate evaluation are all in the same polling loop. Extracting these concerns independently would improve testability and allow alternative frontends (e.g., headless CI mode).

**Checkpoint Reliability**: Phase results are written to `results/` dir after each phase completes. `--start N` enables phase-level re-entry. TurnLedger state is not persisted to disk — if the supervisor is killed mid-phase, budget consumption tracking is lost and must be re-estimated on restart.

**Weakness**: No intra-phase checkpoint. A phase with many tasks that crashes at task N requires re-running tasks 1 through N-1, consuming turn budget and time.

**Extensibility**: `TrailingGatePolicy` and `_subprocess_factory` injection points make the executor testable and consumer-adaptable. Phase discovery via regex supports 4 filename conventions, accommodating different project naming styles.

**Weakness**: Phase discovery regex is hard-coded. Projects using non-canonical naming conventions (e.g., `sprint-phase-3.md`) require modifying `PHASE_FILE_PATTERN`.

**Operational Determinism**: Gate tiers (EXEMPT/LIGHT/STANDARD/STRICT) produce deterministic pass/fail for a given output file and criteria. Turn budget arithmetic is pure Python with no floating-point ambiguity (integer arithmetic). Monotonic clock (`time.monotonic()`) for deadline enforcement prevents NTP adjustment interference.

**Weakness**: Phase execution order depends on the filesystem sort order of discovered phase files. Phases with the same number prefix from different naming conventions could collide in ordering; the regex captures only the first matched number group.
