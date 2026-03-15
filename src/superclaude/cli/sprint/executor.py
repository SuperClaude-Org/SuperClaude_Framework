"""Sprint executor — core orchestration loop."""

from __future__ import annotations

import re
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .debug_logger import debug_log, setup_debug_logger
from .diagnostics import DiagnosticCollector, FailureClassifier, ReportGenerator
from .logging_ import SprintLogger
from .models import (
    GateOutcome,
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
    TaskEntry,
    TaskResult,
    TaskStatus,
    TurnLedger,
)
from .monitor import OutputMonitor, detect_error_max_turns, detect_prompt_too_long
from .notify import notify_phase_complete, notify_sprint_complete
from .process import ClaudeProcess, SignalHandler
from .tmux import update_tail_pane
from .tui import SprintTUI

from superclaude.cli.pipeline.models import Step, StepResult
from superclaude.cli.pipeline.trailing_gate import TrailingGatePolicy, TrailingGateResult

# Debug logger name for executor-specific events
_DBG_NAME = "superclaude.sprint.debug.executor"


# ---------------------------------------------------------------------------
# T07.01 -- Concrete TrailingGatePolicy for sprint consumer
# ---------------------------------------------------------------------------


class SprintGatePolicy:
    """Sprint-specific implementation of TrailingGatePolicy.

    Builds remediation steps from gate failures and tracks file changes
    within the sprint execution context.
    """

    def __init__(self, config: SprintConfig) -> None:
        self._config = config

    def build_remediation_step(self, gate_result: TrailingGateResult) -> Step:
        """Build a focused remediation Step from a gate failure.

        Constructs a Step whose prompt targets the specific failure reason
        and acceptance criteria, rather than re-executing the entire task.
        """
        from superclaude.cli.pipeline.models import GateCriteria

        prompt = (
            f"REMEDIATION: Fix the following gate failure for step '{gate_result.step_id}'.\n"
            f"Failure reason: {gate_result.failure_reason or 'Unknown'}\n"
            f"Focus only on resolving this specific issue."
        )
        output_dir = self._config.work_dir / "remediation"
        output_dir.mkdir(parents=True, exist_ok=True)

        return Step(
            id=f"{gate_result.step_id}_remediation",
            prompt=prompt,
            output_file=output_dir / f"{gate_result.step_id}_remediation.md",
            gate=None,
            timeout_seconds=self._config.max_turns * 60,
        )

    def files_changed(self, step_result: StepResult) -> set[Path]:
        """Return file paths modified during step execution.

        Scans the step's output file and working directory for modifications
        since the step started.
        """
        changed: set[Path] = set()
        if step_result.step is not None and step_result.step.output_file.exists():
            changed.add(step_result.step.output_file)
        return changed


# ---------------------------------------------------------------------------
# 4-Layer Subprocess Isolation
# ---------------------------------------------------------------------------

@dataclass
class IsolationLayers:
    """Configuration for the 4-layer subprocess isolation.

    Each layer prevents cross-task state leakage:
    1. scoped_work_dir: Restrict working directory to release dir
    2. git_boundary: Set GIT_CEILING_DIRECTORIES to prevent upward traversal
    3. empty_plugin_dir: Point CLAUDE_PLUGIN_DIR to an empty tempdir
    4. restricted_settings: Set CLAUDE_SETTINGS_DIR to an isolated tempdir

    The ``env_vars`` property returns a dict of environment variable overrides
    that should be merged into the subprocess environment.
    """

    scoped_work_dir: Path
    git_boundary: Path
    plugin_dir: Path
    settings_dir: Path

    @property
    def env_vars(self) -> dict[str, str]:
        """Return environment variable overrides for all 4 isolation layers."""
        return {
            "CLAUDE_WORK_DIR": str(self.scoped_work_dir),
            "GIT_CEILING_DIRECTORIES": str(self.git_boundary),
            "CLAUDE_PLUGIN_DIR": str(self.plugin_dir),
            "CLAUDE_SETTINGS_DIR": str(self.settings_dir),
        }

    @property
    def layers_active(self) -> list[str]:
        """Return list of active isolation layer names for verification."""
        active = []
        if self.scoped_work_dir.exists():
            active.append("scoped_work_dir")
        if self.git_boundary.exists():
            active.append("git_boundary")
        if self.plugin_dir.exists():
            active.append("empty_plugin_dir")
        if self.settings_dir.exists():
            active.append("restricted_settings")
        return active


def setup_isolation(config: SprintConfig) -> IsolationLayers:
    """Create 4-layer isolation for subprocess execution.

    Sets up:
    1. Scoped working directory (the release dir)
    2. Git boundary (prevents git operations above release dir)
    3. Empty plugin directory (no plugins loaded)
    4. Restricted settings directory (minimal settings)

    All directories are created if they don't exist. The caller is
    responsible for passing ``layers.env_vars`` to the subprocess.

    Args:
        config: Sprint configuration providing the release directory.

    Returns:
        IsolationLayers with all 4 layers configured.
    """
    base = config.results_dir / ".isolation"
    base.mkdir(parents=True, exist_ok=True)

    plugin_dir = base / "plugins"
    plugin_dir.mkdir(exist_ok=True)

    settings_dir = base / "settings"
    settings_dir.mkdir(exist_ok=True)

    return IsolationLayers(
        scoped_work_dir=config.release_dir,
        git_boundary=config.release_dir,
        plugin_dir=plugin_dir,
        settings_dir=settings_dir,
    )


# ---------------------------------------------------------------------------
# Result Aggregation — runner-constructed phase reports
# ---------------------------------------------------------------------------

@dataclass
class AggregatedPhaseReport:
    """Runner-constructed phase report from collected TaskResults.

    This report is built by the runner, not by parsing agent self-reported
    output, ensuring accurate task outcome tracking even when subprocesses
    are budget-exhausted.
    """

    phase_number: int
    tasks_total: int = 0
    tasks_passed: int = 0
    tasks_failed: int = 0
    tasks_incomplete: int = 0
    tasks_skipped: int = 0
    tasks_not_attempted: int = 0
    budget_remaining: int = 0
    total_turns_consumed: int = 0
    total_duration_seconds: float = 0.0
    task_results: list[TaskResult] = field(default_factory=list)
    remaining_task_ids: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        """Overall phase status: PASS, FAIL, or PARTIAL."""
        if self.tasks_total == 0:
            return "PASS"
        if self.tasks_passed == self.tasks_total:
            return "PASS"
        if self.tasks_passed == 0:
            return "FAIL"
        return "PARTIAL"

    def to_yaml(self) -> str:
        """Render the report as a YAML string.

        Produces a machine-readable YAML document with standardized fields
        for downstream tooling and TUI display.
        """
        lines = [
            f"phase: {self.phase_number}",
            f"status: {self.status}",
            f"tasks_total: {self.tasks_total}",
            f"tasks_passed: {self.tasks_passed}",
            f"tasks_failed: {self.tasks_failed}",
            f"tasks_incomplete: {self.tasks_incomplete}",
            f"tasks_not_attempted: {self.tasks_not_attempted}",
            f"budget_remaining: {self.budget_remaining}",
            f"total_turns_consumed: {self.total_turns_consumed}",
            f"total_duration_seconds: {self.total_duration_seconds:.1f}",
            "tasks:",
        ]
        for tr in self.task_results:
            lines.append(f"  - task_id: {tr.task.task_id}")
            lines.append(f"    title: \"{tr.task.title}\"")
            lines.append(f"    status: {tr.status.value}")
            lines.append(f"    gate_outcome: {tr.gate_outcome.value}")
            lines.append(f"    turns_consumed: {tr.turns_consumed}")
            lines.append(f"    duration_seconds: {tr.duration_seconds:.1f}")
        if self.remaining_task_ids:
            lines.append("remaining_tasks:")
            for tid in self.remaining_task_ids:
                lines.append(f"  - {tid}")
        return "\n".join(lines) + "\n"

    def to_markdown(self) -> str:
        """Render the report as a markdown string with YAML frontmatter."""
        lines = [
            "---",
            f"phase: {self.phase_number}",
            f"status: {self.status}",
            f"tasks_total: {self.tasks_total}",
            f"tasks_passed: {self.tasks_passed}",
            f"tasks_failed: {self.tasks_failed}",
            "---",
            "",
            f"# Phase {self.phase_number} — Aggregated Task Report",
            "",
            "| Task ID | Title | Status | Turns | Duration |",
            "|---------|-------|--------|-------|----------|",
        ]
        for tr in self.task_results:
            dur = f"{tr.duration_seconds:.1f}s"
            lines.append(
                f"| {tr.task.task_id} | {tr.task.title} | {tr.status.value} "
                f"| {tr.turns_consumed} | {dur} |"
            )
        lines.append("")
        lines.append(f"**Total turns consumed:** {self.total_turns_consumed}")
        lines.append(f"**Total duration:** {self.total_duration_seconds:.1f}s")

        if self.remaining_task_ids:
            lines.append("")
            lines.append("## Remaining Tasks (Budget Exhausted)")
            for tid in self.remaining_task_ids:
                lines.append(f"- {tid}")

        lines.append("")
        if self.status == "PASS":
            lines.append("EXIT_RECOMMENDATION: CONTINUE")
        else:
            lines.append("EXIT_RECOMMENDATION: HALT")

        return "\n".join(lines) + "\n"


def aggregate_task_results(
    phase_number: int,
    task_results: list[TaskResult],
    remaining_task_ids: list[str] | None = None,
    budget_remaining: int = 0,
) -> AggregatedPhaseReport:
    """Aggregate individual TaskResults into a runner-constructed PhaseReport.

    This function is the runner's authoritative source of task outcomes.
    It does not rely on agent self-reporting.

    Args:
        phase_number: The phase number being aggregated.
        task_results: List of TaskResult from execute_phase_tasks().
        remaining_task_ids: Task IDs that were not attempted due to budget.

    Returns:
        AggregatedPhaseReport with computed counts and status.
    """
    report = AggregatedPhaseReport(
        phase_number=phase_number,
        task_results=task_results,
        remaining_task_ids=remaining_task_ids or [],
        budget_remaining=budget_remaining,
    )

    report.tasks_total = len(task_results) + len(report.remaining_task_ids)
    report.tasks_passed = sum(
        1 for r in task_results if r.status == TaskStatus.PASS
    )
    report.tasks_failed = sum(
        1 for r in task_results if r.status == TaskStatus.FAIL
    )
    report.tasks_incomplete = sum(
        1 for r in task_results if r.status == TaskStatus.INCOMPLETE
    )
    report.tasks_skipped = sum(
        1 for r in task_results if r.status == TaskStatus.SKIPPED
    )
    report.tasks_not_attempted = len(report.remaining_task_ids)
    report.total_turns_consumed = sum(r.turns_consumed for r in task_results)
    report.total_duration_seconds = sum(
        r.duration_seconds for r in task_results
    )

    return report


def check_budget_guard(ledger: TurnLedger | None) -> str | None:
    """Pre-launch budget guard: returns a halt message if budget is insufficient.

    Returns None if launch is allowed, or a descriptive message string
    if the budget is too low to launch a subprocess.
    """
    if ledger is None:
        return None
    if ledger.can_launch():
        return None
    return (
        f"Budget exhausted: {ledger.available()} turns remaining, "
        f"minimum {ledger.minimum_allocation} required for launch"
    )


def execute_phase_tasks(
    tasks: list[TaskEntry],
    config: SprintConfig,
    phase,
    ledger: TurnLedger | None = None,
    *,
    _subprocess_factory=None,
) -> tuple[list[TaskResult], list[str]]:
    """Per-task subprocess orchestration loop.

    Iterates over a task inventory, spawning one subprocess per task with
    budget allocation from the TurnLedger. Returns task results and a list
    of remaining (unattempted) task IDs if budget was exhausted.

    Args:
        tasks: Ordered list of TaskEntry from the tasklist parser.
        config: Sprint configuration.
        phase: The Phase being executed.
        ledger: Optional TurnLedger for budget tracking.
        _subprocess_factory: Optional callable for testing; signature
            ``(task, config, phase) -> (exit_code, turns_consumed, output_bytes)``.

    Returns:
        Tuple of (results, remaining_task_ids). remaining_task_ids is non-empty
        only when the loop halted due to budget exhaustion.
    """
    results: list[TaskResult] = []
    remaining: list[str] = []

    if not tasks:
        return results, remaining

    for i, task in enumerate(tasks):
        started_at = datetime.now(timezone.utc)

        # Budget check: can we launch?
        if ledger is not None and not ledger.can_launch():
            # Mark this and all subsequent tasks as skipped
            remaining = [t.task_id for t in tasks[i:]]
            for t in tasks[i:]:
                results.append(
                    TaskResult(
                        task=t,
                        status=TaskStatus.SKIPPED,
                        started_at=started_at,
                        finished_at=datetime.now(timezone.utc),
                    )
                )
            break

        # Debit the minimum allocation upfront
        if ledger is not None:
            ledger.debit(ledger.minimum_allocation)

        # Spawn subprocess for this task
        if _subprocess_factory is not None:
            exit_code, turns_consumed, output_bytes = _subprocess_factory(
                task, config, phase
            )
        else:
            # Default: delegate to ClaudeProcess (real execution)
            exit_code, turns_consumed, output_bytes = _run_task_subprocess(
                task, config, phase
            )

        finished_at = datetime.now(timezone.utc)

        # Determine task status from exit code
        if exit_code == 0:
            status = TaskStatus.PASS
        elif exit_code == 124:
            status = TaskStatus.INCOMPLETE
        else:
            status = TaskStatus.FAIL

        # Reconcile budget: debit actual consumption, credit back pre-allocation
        if ledger is not None:
            # We pre-debited minimum_allocation; now adjust for actual turns
            actual = max(turns_consumed, 0)
            pre_allocated = ledger.minimum_allocation
            if actual > pre_allocated:
                ledger.debit(actual - pre_allocated)
            elif actual < pre_allocated:
                ledger.credit(pre_allocated - actual)

        results.append(
            TaskResult(
                task=task,
                status=status,
                turns_consumed=turns_consumed,
                exit_code=exit_code,
                started_at=started_at,
                finished_at=finished_at,
                output_bytes=output_bytes,
            )
        )

    return results, remaining


def _run_task_subprocess(
    task: TaskEntry,
    config: SprintConfig,
    phase,
) -> tuple[int, int, int]:
    """Run a single task in a subprocess. Returns (exit_code, turns, output_bytes).

    This is the real implementation that spawns a ClaudeProcess. For testing,
    callers of execute_phase_tasks pass _subprocess_factory instead.
    """
    # Build a task-specific prompt
    prompt = (
        f"Execute task {task.task_id}: {task.title}\n"
        f"From phase file: {phase.file}\n"
        f"Description: {task.description}\n"
    )

    proc = ClaudeProcess.__new__(ClaudeProcess)
    proc.config = config
    proc.phase = phase
    from superclaude.cli.pipeline.process import ClaudeProcess as _Base
    _Base.__init__(
        proc,
        prompt=prompt,
        output_file=config.output_file(phase),
        error_file=config.error_file(phase),
        max_turns=config.max_turns,
        model=config.model,
        permission_flag=config.permission_flag,
        timeout_seconds=config.max_turns * 120 + 300,
        output_format="stream-json",
    )
    proc.start()
    proc.wait()
    exit_code = proc._process.returncode if proc._process else -1
    output_path = config.output_file(phase)
    output_bytes = output_path.stat().st_size if output_path.exists() else 0
    # Turn counting is wired separately in T02.06
    return (exit_code if exit_code is not None else -1, 0, output_bytes)


def execute_sprint(config: SprintConfig):
    """Main orchestration loop.

    For each active phase:
    1. Launch claude -p subprocess
    2. Start output monitor thread
    3. Update TUI in a polling loop until process exits (with timeout)
    4. Parse result file for CONTINUE/HALT
    5. Record PhaseResult
    6. Decide whether to continue or halt
    """
    # Pre-flight: verify claude binary is available before starting TUI/logging
    if shutil.which("claude") is None:
        raise SystemExit(
            "Error: 'claude' binary not found in PATH. "
            "Install Claude Code CLI before running sprint."
        )

    signal_handler = SignalHandler()
    signal_handler.install()

    setup_debug_logger(config)
    import logging as _logging
    _dbg = _logging.getLogger(_DBG_NAME)

    logger = SprintLogger(config)
    tui = SprintTUI(config)
    monitor = OutputMonitor(Path("/dev/null"))  # reset per phase
    proc_manager: ClaudeProcess | None = None

    sprint_result = SprintResult(config=config)
    logger.write_header(sprint_result)

    tui.start()

    try:
        for phase in config.active_phases:
            if signal_handler.shutdown_requested:
                sprint_result.outcome = SprintOutcome.INTERRUPTED
                break

            # Reset monitor for this phase
            output_path = config.output_file(phase)
            monitor.reset(output_path)
            monitor.start()

            # Update tmux tail pane if running in tmux
            if config.tmux_session_name:
                update_tail_pane(config.tmux_session_name, output_path)

            # Launch claude
            proc_manager = ClaudeProcess(config, phase)
            proc_manager.start()
            started_at = datetime.now(timezone.utc)
            # Use monotonic clock for deadline enforcement to be immune to NTP adjustments
            deadline = time.monotonic() + proc_manager.timeout_seconds
            logger.write_phase_start(phase, started_at)

            debug_log(_dbg, "PHASE_BEGIN", phase=phase.number, file=str(phase.file))

            tui.update(sprint_result, monitor.state, phase)

            # Poll loop: wait for process to finish while updating TUI
            # Enforces monotonic timeout via deadline check.
            _timed_out = False
            _stall_acted = False  # single-fire guard for watchdog
            _poll_start = time.monotonic()
            while proc_manager._process.poll() is None:
                if signal_handler.shutdown_requested:
                    proc_manager.terminate()
                    break
                if time.monotonic() > deadline:
                    # Timeout reached: kill the process, exit loop
                    _timed_out = True
                    proc_manager.terminate()
                    break

                ms = monitor.state
                _elapsed = time.monotonic() - _poll_start

                debug_log(
                    _dbg,
                    "poll_tick",
                    phase=phase.number,
                    pid=proc_manager._process.pid,
                    poll_result="running",
                    elapsed=round(_elapsed, 1),
                    output_bytes=ms.output_bytes,
                    growth_rate=round(ms.growth_rate_bps, 1),
                    stall_seconds=round(ms.stall_seconds, 1),
                    stall_status=ms.stall_status,
                )

                # --- Watchdog: stall timeout check ---
                if (
                    config.stall_timeout > 0
                    and ms.stall_seconds > config.stall_timeout
                    and ms.events_received > 0  # don't trigger during startup
                    and not _stall_acted
                ):
                    _stall_acted = True
                    debug_log(
                        _dbg,
                        "watchdog_triggered",
                        phase=phase.number,
                        action=config.stall_action,
                        stall_seconds=round(ms.stall_seconds, 1),
                        pid=proc_manager._process.pid,
                    )
                    if config.stall_action == "kill":
                        import sys
                        print(
                            f"[WATCHDOG] Stall detected ({ms.stall_seconds:.0f}s > "
                            f"{config.stall_timeout}s) — killing phase {phase.number}",
                            file=sys.stderr,
                        )
                        _timed_out = True
                        proc_manager.terminate()
                        break
                    else:
                        # warn action: log and continue
                        import sys
                        print(
                            f"[WATCHDOG] Stall detected ({ms.stall_seconds:.0f}s > "
                            f"{config.stall_timeout}s) — warning for phase {phase.number}",
                            file=sys.stderr,
                        )

                # Reset single-fire guard when output resumes
                if _stall_acted and ms.stall_seconds == 0.0:
                    _stall_acted = False

                # Update TUI at ~2 Hz (monitor thread handles data extraction)
                # Wrap in try/except so a display glitch cannot abort the sprint
                try:
                    tui.update(sprint_result, monitor.state, phase)
                except Exception as _tui_exc:
                    import sys
                    print(f"[TUI] Display error (continuing sprint): {_tui_exc}", file=sys.stderr)
                time.sleep(0.5)

            # Safely read exit code: returncode may be None if terminate raced.
            # Use _timed_out flag instead of assigning directly to returncode.
            raw_rc = proc_manager._process.returncode
            if _timed_out:
                exit_code = 124
            else:
                exit_code = raw_rc if raw_rc is not None else -1
            monitor.stop()
            finished_at = datetime.now(timezone.utc)
            _phase_dur = (finished_at - started_at).total_seconds()
            debug_log(
                _dbg,
                "PHASE_END",
                phase=phase.number,
                exit_code=exit_code,
                duration=round(_phase_dur, 1),
            )

            # If shutdown was requested during the poll loop, classify as
            # INTERRUPTED rather than letting _determine_phase_status see
            # exit_code=-1 (None→-1 fallback) and return PhaseStatus.ERROR,
            # which would incorrectly set the outcome to HALTED.
            if signal_handler.shutdown_requested:
                logger.write_phase_interrupt(phase, started_at, finished_at, exit_code)
                sprint_result.outcome = SprintOutcome.INTERRUPTED
                break

            # Determine phase status
            status = _determine_phase_status(
                exit_code=exit_code,
                result_file=config.result_file(phase),
                output_file=config.output_file(phase),
                config=config,
                phase=phase,
                started_at=started_at.timestamp(),
            )

            # Write executor result file for downstream consumers.
            # Written AFTER status determination to avoid circularity.
            # Overwrites any agent-written file — executor is authoritative.
            _write_executor_result_file(
                config=config,
                phase=phase,
                status=status,
                exit_code=exit_code,
                monitor_state=monitor.state,
                started_at=started_at,
                finished_at=finished_at,
            )

            # Collect stderr size for telemetry
            error_file = config.error_file(phase)
            error_bytes = error_file.stat().st_size if error_file.exists() else 0

            phase_result = PhaseResult(
                phase=phase,
                status=status,
                exit_code=exit_code,
                started_at=started_at,
                finished_at=finished_at,
                output_bytes=monitor.state.output_bytes,
                error_bytes=error_bytes,
                last_task_id=monitor.state.last_task_id,
                files_changed=monitor.state.files_changed,
            )
            sprint_result.phase_results.append(phase_result)

            debug_log(
                _dbg,
                "phase_complete",
                phase=phase.number,
                status=status.value,
                exit_code=exit_code,
                duration=round(_phase_dur, 1),
            )

            # Log and notify
            logger.write_phase_result(phase_result)
            notify_phase_complete(phase_result)

            tui.update(sprint_result, monitor.state, None)

            # Decide: continue or halt?
            if status.is_failure:
                # Collect diagnostics for the failed phase
                try:
                    collector = DiagnosticCollector(config)
                    bundle = collector.collect(phase, phase_result, monitor.state)
                    classifier = FailureClassifier()
                    bundle.category = classifier.classify(bundle)
                    reporter = ReportGenerator()
                    diag_path = config.results_dir / f"phase-{phase.number}-diagnostic.md"
                    reporter.write(bundle, diag_path)
                    debug_log(
                        _dbg,
                        "diagnostic_report",
                        phase=phase.number,
                        category=bundle.category.value,
                        path=str(diag_path),
                    )
                except Exception as _diag_exc:
                    debug_log(_dbg, "diagnostic_error", phase=phase.number, error=str(_diag_exc))

                sprint_result.outcome = SprintOutcome.HALTED
                sprint_result.halt_phase = phase.number
                break

        # Sprint finished
        sprint_result.finished_at = datetime.now(timezone.utc)
        if sprint_result.outcome == SprintOutcome.SUCCESS:
            # Verify all phases actually passed
            if not all(r.status.is_success for r in sprint_result.phase_results):
                sprint_result.outcome = SprintOutcome.ERROR

        tui.update(sprint_result, MonitorState(), None)
        logger.write_summary(sprint_result)
        notify_sprint_complete(sprint_result)

    finally:
        # Ensure monitor thread and subprocess are cleaned up even on exception.
        # Each step is independent so one failure does not prevent others.
        try:
            monitor.stop()
        except Exception:
            pass
        if proc_manager is not None:
            try:
                proc_manager.terminate()
            except Exception:
                pass
        try:
            tui.stop()
        except Exception:
            pass
        try:
            signal_handler.uninstall()
        except Exception:
            pass

    # Write sentinel exit code file so tmux caller can read the outcome
    _exitcode = 0 if sprint_result.outcome == SprintOutcome.SUCCESS else 1
    try:
        (config.release_dir / ".sprint-exitcode").write_text(str(_exitcode))
    except OSError:
        pass  # best-effort; do not mask the real exit

    if _exitcode != 0:
        raise SystemExit(_exitcode)


def _classify_from_result_file(
    result_file: Path,
    started_at: float,
) -> PhaseStatus | None:
    """Classify phase outcome from the agent-written result file.

    Returns a PhaseStatus if the result file exists, is fresh (mtime > started_at),
    and contains a recognizable EXIT_RECOMMENDATION. Returns None if the file is
    missing, stale, or unreadable.
    """
    if not result_file.exists():
        return None
    try:
        mtime = result_file.stat().st_mtime
    except OSError:
        return None
    if started_at > 0 and mtime < started_at:
        # Stale file from a previous run — do not trust
        return None
    try:
        content = result_file.read_text(errors="replace")
    except OSError:
        return None
    upper = content.upper()
    if "EXIT_RECOMMENDATION: HALT" in upper:
        return PhaseStatus.HALT
    if "EXIT_RECOMMENDATION: CONTINUE" in upper:
        return PhaseStatus.PASS_RECOVERED
    if re.search(r"status:\s*PASS\b", content, re.IGNORECASE):
        return PhaseStatus.PASS_RECOVERED
    if re.search(r"status:\s*FAIL(?:ED|URE)?\b", content, re.IGNORECASE):
        return PhaseStatus.HALT
    if re.search(r"status:\s*PARTIAL\b", content, re.IGNORECASE):
        return PhaseStatus.INCOMPLETE
    return None


def _check_checkpoint_pass(config: SprintConfig, phase: Phase) -> bool:
    """Return True if the end-of-phase checkpoint file exists with status PASS."""
    checkpoint_path = config.release_dir / "checkpoints" / f"CP-P{phase.number:02d}-END.md"
    if not checkpoint_path.exists():
        return False
    try:
        content = checkpoint_path.read_text(errors="replace").upper()
        return "STATUS: PASS" in content or "**RESULT**: PASS" in content
    except OSError:
        return False


def _check_contamination(config: SprintConfig, phase: Phase) -> list[str]:
    """Return list of artifact files containing cross-phase task ID patterns."""
    import re as _re

    contaminated: list[str] = []
    artifacts_dir = config.release_dir / "artifacts"
    if not artifacts_dir.exists():
        return contaminated
    next_phase = phase.number + 1
    pattern = _re.compile(rf"T{next_phase:02d}\.\d{{2}}", _re.IGNORECASE)
    for md_file in artifacts_dir.rglob("*.md"):
        try:
            if pattern.search(md_file.read_text(errors="replace")):
                contaminated.append(str(md_file.relative_to(config.release_dir)))
        except OSError:
            pass
    return contaminated


def _write_crash_recovery_log(
    config: SprintConfig,
    phase: Phase,
    contaminated: list[str],
) -> None:
    """Append crash recovery entry to results/crash_recovery_log.md."""
    log_path = config.results_dir / "crash_recovery_log.md"
    entry = (
        f"\n## Phase {phase.number} — PASS_RECOVERED Recovery\n"
        f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}\n"
        f"**Checkpoint**: checkpoints/CP-P{phase.number:02d}-END.md (PASS)\n"
        f"**Contamination check**: "
        + ("CLEAN" if not contaminated else f"WARNING — {len(contaminated)} file(s): {contaminated}")
        + "\n"
        "**Action**: Phase reclassified ERROR→PASS_RECOVERED.\n"
    )
    try:
        with open(log_path, "a") as f:
            f.write(entry)
    except OSError:
        pass


def _write_executor_result_file(
    config: SprintConfig,
    phase: Phase,
    status: PhaseStatus,
    exit_code: int,
    monitor_state: MonitorState,
    started_at: datetime,
    finished_at: datetime,
) -> None:
    """Write executor-sourced result file for downstream consumers.

    This is written AFTER _determine_phase_status returns, so it does not
    create circularity. It provides a deterministic result file even when
    the agent failed to write one.
    """
    duration = (finished_at - started_at).total_seconds()
    recommendation = "CONTINUE" if status.is_success else "HALT"
    content = (
        "---\n"
        f"phase: {phase.number}\n"
        f"status: {'PASS' if status.is_success else 'FAIL'}\n"
        f"tasks_total: 1\n"
        f"tasks_passed: {1 if status.is_success else 0}\n"
        f"tasks_failed: {0 if status.is_success else 1}\n"
        "---\n"
        "\n"
        f"# Phase {phase.number} — Executor Result Report\n"
        "\n"
        f"| Phase | Status | Exit Code | Duration |\n"
        f"|-------|--------|-----------|----------|\n"
        f"| {phase.number} | {status.value} | {exit_code} | {duration:.1f}s |\n"
        "\n"
        f"**Source**: executor (not agent self-report)\n"
        f"**Output bytes**: {monitor_state.output_bytes}\n"
        f"**Last task ID**: {monitor_state.last_task_id or 'n/a'}\n"
        f"**Files changed**: {monitor_state.files_changed}\n"
        "\n"
        f"EXIT_RECOMMENDATION: {recommendation}\n"
    )
    result_path = config.result_file(phase)
    try:
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(content)
    except OSError:
        pass  # Non-fatal — best effort


def _determine_phase_status(
    exit_code: int,
    result_file: Path,
    output_file: Path,
    *,
    config: SprintConfig | None = None,
    phase: Phase | None = None,
    started_at: float = 0.0,
) -> PhaseStatus:
    """Parse result file and exit code to determine phase status.

    Priority:
    1. Timeout (exit 124) -> TIMEOUT
    2. Non-zero exit -> ERROR
    3. Result file with EXIT_RECOMMENDATION: HALT -> HALT
    4. Result file with EXIT_RECOMMENDATION: CONTINUE -> PASS
    5. Result file with status: PASS/FAIL -> PASS/HALT
    6. No result file but output exists -> PASS_NO_REPORT
    7. No result file and no output -> ERROR
    """
    if exit_code == 124:
        return PhaseStatus.TIMEOUT
    if exit_code != 0:
        # Path 1 — Specific: context exhaustion (Spec B S2)
        # detect_prompt_too_long reads NDJSON output for "Prompt is too long"
        if detect_prompt_too_long(output_file):
            # Check if the agent managed to write a result file before exhaustion
            result_status = _classify_from_result_file(result_file, started_at)
            if result_status is not None:
                return result_status
            # No valid result file — context exhausted without completing
            return PhaseStatus.INCOMPLETE

        # Path 2 — General: checkpoint inference (Spec A SOL-C)
        # Reads agent-written checkpoint files (pre-crash evidence)
        if config is not None and phase is not None:
            if _check_checkpoint_pass(config, phase):
                contaminated = _check_contamination(config, phase)
                _write_crash_recovery_log(config, phase, contaminated)
                if not contaminated:
                    return PhaseStatus.PASS_RECOVERED

        # Path 3 — Default: unchanged
        return PhaseStatus.ERROR

    if result_file.exists():
        content = result_file.read_text(errors="replace")
        # Use case-insensitive search for EXIT_RECOMMENDATION tokens to handle
        # model output that varies in casing. When both CONTINUE and HALT appear
        # (conflicting signals), HALT wins — the stronger/safer outcome.
        upper = content.upper()
        has_continue = "EXIT_RECOMMENDATION: CONTINUE" in upper
        has_halt = "EXIT_RECOMMENDATION: HALT" in upper
        if has_halt:
            return PhaseStatus.HALT
        if has_continue:
            return PhaseStatus.PASS
        if re.search(r"status:\s*PASS\b", content, re.IGNORECASE):
            return PhaseStatus.PASS
        if re.search(r"status:\s*FAIL(?:ED|URE)?\b", content, re.IGNORECASE):
            return PhaseStatus.HALT
        # PARTIAL result means tasks did not fully complete — treat as halt
        if re.search(r"status:\s*PARTIAL\b", content, re.IGNORECASE):
            return PhaseStatus.HALT
        return PhaseStatus.PASS_NO_SIGNAL

    if output_file.exists() and output_file.stat().st_size > 0:
        # Check for budget exhaustion: a subprocess that exits 0 but hit
        # error_max_turns produced no useful result — reclassify as INCOMPLETE
        # to trigger HALT instead of silent continuation.
        if detect_error_max_turns(output_file):
            return PhaseStatus.INCOMPLETE
        return PhaseStatus.PASS_NO_REPORT

    return PhaseStatus.ERROR
