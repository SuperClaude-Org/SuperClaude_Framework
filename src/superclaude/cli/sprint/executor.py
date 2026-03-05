"""Sprint executor — core orchestration loop."""

from __future__ import annotations

import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from .debug_logger import debug_log, setup_debug_logger
from .diagnostics import DiagnosticCollector, FailureClassifier, ReportGenerator
from .logging_ import SprintLogger
from .models import (
    MonitorState,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
)
from .monitor import OutputMonitor
from .notify import notify_phase_complete, notify_sprint_complete
from .process import ClaudeProcess, SignalHandler
from .tmux import update_tail_pane
from .tui import SprintTUI

# Debug logger name for executor-specific events
_DBG_NAME = "superclaude.sprint.debug.executor"


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


def _determine_phase_status(
    exit_code: int,
    result_file: Path,
    output_file: Path,
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
        return PhaseStatus.PASS_NO_REPORT

    return PhaseStatus.ERROR
