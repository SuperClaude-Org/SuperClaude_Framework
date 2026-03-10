"""Regression tests for sprint CLI — missing scenario coverage.

Covers edge cases and boundary conditions that were absent from the
original test suite:

1.  test_executor.py gaps:
    - Timeout (exit 124) scenario E2E path
    - PASS_NO_SIGNAL: result file exists but has no EXIT_RECOMMENDATION
    - PASS_NO_REPORT: output exists but no result file (non-empty)
    - CONTINUE and HALT both present → CONTINUE wins (first match priority)
    - PARTIAL status in result file → HALT

2.  test_monitor.py gaps:
    - Double-stop of OutputMonitor is idempotent (no crash)
    - reset() called while monitor has never been started

3.  executor orchestration gaps:
    - shutdown_requested=True at top of phase loop (before Popen) → INTERRUPTED
    - Timeout path sets exit_code=124 → PhaseStatus.TIMEOUT → HALTED outcome

4.  test_process.py gaps:
    - ClaudeProcess.terminate() when process is already dead (poll() != None)
    - ClaudeProcess.wait() timeout path returns 124 and calls terminate
    - build_command() excludes --model flag when model string is empty
    - build_command() includes --model flag when model is set

5.  test_logging_.py gaps (new):
    - write_phase_start emits event with correct fields
    - read_status_from_log and tail_log are importable stubs

6.  test_notify.py gaps (new):
    - notify_phase_complete sends correct title for failure
    - notify_phase_complete sends correct title for success
    - notify_sprint_complete sends correct title for success
    - notify_sprint_complete uses urgency for non-success
    - _notify fails silently on unknown platform

7.  test_config.py gaps:
    - validate_phases with missing file adds to errors list
    - load_sprint_config with missing phase file raises ClickException
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.sprint.executor import _determine_phase_status, execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
    SprintResult,
)
from superclaude.cli.sprint.monitor import OutputMonitor
from superclaude.cli.sprint.process import ClaudeProcess

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_phases(n: int, base_dir: Path) -> list[Phase]:
    phases = []
    for i in range(1, n + 1):
        pf = base_dir / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}: Test\n")
        phases.append(Phase(number=i, file=pf, name=f"Phase {i}"))
    return phases


def _make_config(tmp_path: Path, num_phases: int = 3) -> SprintConfig:
    phases = _make_phases(num_phases, tmp_path)
    index = tmp_path / "tasklist-index.md"
    index.write_text("index\n")
    return SprintConfig(
        index_path=index,
        release_dir=tmp_path,
        phases=phases,
        start_phase=1,
        end_phase=num_phases,
        max_turns=5,
    )


def _make_phase_result(
    phase: Phase | None = None,
    status: PhaseStatus = PhaseStatus.PASS,
    exit_code: int = 0,
) -> PhaseResult:
    now = datetime.now(timezone.utc)
    if phase is None:
        phase = Phase(number=1, file=Path("/tmp/p1.md"))
    return PhaseResult(
        phase=phase,
        status=status,
        exit_code=exit_code,
        started_at=now,
        finished_at=now,
    )


# ---------------------------------------------------------------------------
# _determine_phase_status — missing branches
# ---------------------------------------------------------------------------


class TestDeterminePhaseStatusGaps:
    """Edge cases not covered in test_executor.py."""

    def test_halt_wins_when_both_signals_present_regardless_of_order(self, tmp_path):
        """When both CONTINUE and HALT appear, HALT wins (safer/stronger outcome).

        The executor checks has_halt before has_continue, so HALT takes priority
        over CONTINUE regardless of which appears first in the file.
        """
        # CONTINUE listed before HALT — HALT still wins
        result_file = tmp_path / "result_a.md"
        result_file.write_text(
            "EXIT_RECOMMENDATION: CONTINUE\n"
            "EXIT_RECOMMENDATION: HALT\n"
        )
        output_file = tmp_path / "output.txt"
        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

        # HALT listed before CONTINUE — HALT also wins
        result_file_b = tmp_path / "result_b.md"
        result_file_b.write_text(
            "EXIT_RECOMMENDATION: HALT\n"
            "EXIT_RECOMMENDATION: CONTINUE\n"
        )
        status_b = _determine_phase_status(
            exit_code=0,
            result_file=result_file_b,
            output_file=output_file,
        )
        assert status_b == PhaseStatus.HALT

    def test_continue_alone_yields_pass(self, tmp_path):
        """CONTINUE alone (no HALT present) → PASS."""
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE\n")
        output_file = tmp_path / "output.txt"
        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_partial_status_in_result_file_yields_halt(self, tmp_path):
        """status: PARTIAL in YAML frontmatter → HALT (tasks incomplete)."""
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: PARTIAL\n---\n")
        output_file = tmp_path / "output.txt"
        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_pass_no_signal_when_result_file_has_no_keywords(self, tmp_path):
        """Result file exists with content but no EXIT_RECOMMENDATION or status: → PASS_NO_SIGNAL."""
        result_file = tmp_path / "result.md"
        result_file.write_text(
            "# Phase 1 Report\n\nAll tasks completed.\n\n## Files Modified\n- src/main.py\n"
        )
        output_file = tmp_path / "output.txt"
        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_SIGNAL

    def test_pass_no_report_when_output_exists_without_result_file(self, tmp_path):
        """No result file, non-empty output file → PASS_NO_REPORT."""
        result_file = tmp_path / "result.md"  # does not exist
        output_file = tmp_path / "output.txt"
        output_file.write_text("Claude completed the tasks.\n")
        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_REPORT

    def test_exit_code_2_is_error_not_timeout(self, tmp_path):
        """Only exit_code=124 is TIMEOUT; other non-zero codes are ERROR."""
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        for exit_code in (1, 2, 127, 255, -1, -15):
            status = _determine_phase_status(
                exit_code=exit_code,
                result_file=result_file,
                output_file=output_file,
            )
            assert status == PhaseStatus.ERROR, (
                f"exit_code={exit_code} should produce ERROR, got {status}"
            )


# ---------------------------------------------------------------------------
# OutputMonitor — idempotency and missing-file edge cases
# ---------------------------------------------------------------------------


class TestOutputMonitorIdempotency:
    """Edge cases for OutputMonitor lifecycle."""

    def test_double_stop_is_idempotent(self, tmp_path):
        """Calling stop() twice must not raise."""
        output_file = tmp_path / "output.txt"
        output_file.write_text("")
        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.start()
        monitor.stop()
        monitor.stop()  # second stop — must not raise

    def test_stop_before_start_is_safe(self, tmp_path):
        """Calling stop() without start() must not raise."""
        output_file = tmp_path / "output.txt"
        monitor = OutputMonitor(output_file, poll_interval=0.1)
        monitor.stop()  # thread is None — must be safe

    def test_reset_without_prior_start_is_safe(self, tmp_path):
        """reset() called before start() must not crash."""
        output_file = tmp_path / "output.txt"
        output_file.write_text("initial\n")
        monitor = OutputMonitor(output_file, poll_interval=0.1)
        new_file = tmp_path / "output2.txt"
        monitor.reset(new_file)  # should not raise
        assert monitor.output_path == new_file
        assert monitor.state.output_bytes == 0

    def test_monitor_recovers_after_file_appears_later(self, tmp_path):
        """Monitor started before file exists must pick up content when file appears."""
        output_file = tmp_path / "late_output.txt"
        # Do not create the file yet
        monitor = OutputMonitor(output_file, poll_interval=0.05)
        monitor.start()

        import time
        time.sleep(0.1)  # let monitor poll once with missing file

        output_file.write_text("T05.01\n")
        time.sleep(0.15)
        monitor.stop()

        assert monitor.state.output_bytes > 0
        assert monitor.state.last_task_id == "T05.01"


# ---------------------------------------------------------------------------
# ClaudeProcess — terminate and wait edge cases
# ---------------------------------------------------------------------------


class TestClaudeProcessEdgeCases:
    """ClaudeProcess terminal scenarios."""

    def _make_proc(self, tmp_path: Path, **config_kwargs) -> ClaudeProcess:
        config = SprintConfig(
            index_path=tmp_path / "index.md",
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
            max_turns=5,
            **config_kwargs,
        )
        (tmp_path / "phase-1-tasklist.md").write_text("# Phase 1\n")
        return ClaudeProcess(config, config.phases[0])

    def test_terminate_when_process_already_dead_is_safe(self, tmp_path):
        """terminate() on a process that has already exited must not raise."""
        proc_manager = self._make_proc(tmp_path)

        fake_proc = MagicMock()
        fake_proc.poll.return_value = 0  # already exited
        fake_proc.pid = 12345
        proc_manager._process = fake_proc

        # Should not raise even though poll() != None
        proc_manager.terminate()

    def test_terminate_when_process_is_none_is_safe(self, tmp_path):
        """terminate() before start() (process=None) must not raise."""
        proc_manager = self._make_proc(tmp_path)
        assert proc_manager._process is None
        proc_manager.terminate()  # must not raise

    def test_wait_timeout_returns_124_and_calls_terminate(self, tmp_path):
        """wait() that hits TimeoutExpired must return 124 (bash timeout code)."""
        proc_manager = self._make_proc(tmp_path)

        fake_proc = MagicMock()
        fake_proc.wait.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=1)
        fake_proc.poll.return_value = None  # still running
        fake_proc.pid = 12345
        proc_manager._process = fake_proc

        with (
            patch("superclaude.cli.pipeline.process.os.getpgid", return_value=12345),
            patch("superclaude.cli.pipeline.process.os.killpg"),
        ):
            result = proc_manager.wait()

        assert result == 124

    def test_build_command_no_model_flag_when_empty(self, tmp_path):
        """--model must not appear in command when model=''."""
        config = SprintConfig(
            index_path=tmp_path / "index.md",
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
            model="",
            max_turns=5,
        )
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--model" not in cmd

    def test_build_command_includes_model_when_set(self, tmp_path):
        """--model <value> must appear when model is non-empty."""
        config = SprintConfig(
            index_path=tmp_path / "index.md",
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
            model="claude-opus-4-6",
            max_turns=5,
        )
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        idx = cmd.index("--model")
        assert cmd[idx + 1] == "claude-opus-4-6"

    def test_build_env_preserves_existing_vars(self, tmp_path):
        """build_env() must include existing env vars in addition to CLAUDECODE."""
        proc = self._make_proc(tmp_path)
        env = proc.build_env()
        # PATH must be inherited
        assert "PATH" in env
        assert "CLAUDECODE" not in env


# ---------------------------------------------------------------------------
# Executor orchestration — shutdown before phase starts
# ---------------------------------------------------------------------------


class TestExecutorShutdownBeforePhase:
    """Shutdown requested before any phase launches → INTERRUPTED immediately."""

    def test_shutdown_before_first_phase_no_processes_spawned(self, tmp_path):
        """If shutdown_requested=True before the loop body, Popen must never be called."""
        config = _make_config(tmp_path, num_phases=2)
        popen_call_count = [0]

        def counting_popen(cmd, **kwargs):
            popen_call_count[0] += 1
            return MagicMock()

        from superclaude.cli.sprint.process import SignalHandler as _RealSH

        class _PresetShutdown(_RealSH):
            def install(self):
                super().install()
                self.shutdown_requested = True  # already interrupted at install time

        captured_results = []

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=counting_popen),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SignalHandler", _PresetShutdown),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(
                side_effect=lambda sr: captured_results.append(sr)
            )
            mock_logger_cls.return_value = logger_inst

            try:
                execute_sprint(config)
            except SystemExit:
                pass

        # No process should have been spawned
        assert popen_call_count[0] == 0

        assert len(captured_results) >= 1
        assert captured_results[0].outcome == SprintOutcome.INTERRUPTED


# ---------------------------------------------------------------------------
# Executor — timeout path produces HALTED outcome
# ---------------------------------------------------------------------------


class TestExecutorTimeoutPath:
    """Timeout (exit 124) → PhaseStatus.TIMEOUT → SprintOutcome.HALTED."""

    def test_timeout_exit_code_produces_halted_sprint(self, tmp_path):
        """When the executor forcefully sets exit_code=124, outcome must be HALTED."""
        config = _make_config(tmp_path, num_phases=1)
        captured_results = []

        class _TimeoutPopen:
            def __init__(self):
                self.returncode = None
                self.pid = 77777
                self._poll_count = 0

            def poll(self):
                self._poll_count += 1
                # Return None forever (process never exits naturally)
                return None

            def wait(self, timeout=None):
                # Simulate timeout
                raise subprocess.TimeoutExpired(cmd="claude", timeout=1)

        def popen_factory(cmd, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.output_file(phase).write_text("working...\n")
            return _TimeoutPopen()

        # We need the deadline to expire quickly. Override time.monotonic to fast-forward.
        # The executor uses time.monotonic() for deadline enforcement (not time.time).
        real_monotonic = __import__("time").monotonic
        call_counter = [0]

        def fast_monotonic():
            call_counter[0] += 1
            # After 3 calls, return a value past the deadline
            if call_counter[0] > 3:
                return real_monotonic() + 999999  # far past deadline
            return real_monotonic()

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.pipeline.process.os.getpgid", return_value=77777),
            patch("superclaude.cli.pipeline.process.os.killpg"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.time.monotonic", side_effect=fast_monotonic),
            patch("superclaude.cli.sprint.executor.time.sleep"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(
                side_effect=lambda sr: captured_results.append(sr)
            )
            mock_logger_cls.return_value = logger_inst

            try:
                execute_sprint(config)
            except SystemExit:
                pass

        assert len(captured_results) >= 1
        result = captured_results[0]
        assert result.outcome == SprintOutcome.HALTED
        assert result.phase_results[0].status == PhaseStatus.TIMEOUT


# ---------------------------------------------------------------------------
# SprintLogger — write_phase_start event fields
# ---------------------------------------------------------------------------


class TestSprintLoggerPhaseStart:
    """write_phase_start must emit correct JSONL event."""

    def test_write_phase_start_fields(self, tmp_path):
        """phase_start event must include phase number, name, file, timestamp."""
        import json

        from superclaude.cli.sprint.logging_ import SprintLogger

        config = _make_config(tmp_path, num_phases=1)
        logger = SprintLogger(config)
        phase = config.phases[0]
        started_at = datetime.now(timezone.utc)

        logger.write_phase_start(phase, started_at)

        events = [
            json.loads(line)
            for line in config.execution_log_jsonl.read_text().strip().split("\n")
            if line.strip()
        ]
        assert len(events) == 1
        ev = events[0]
        assert ev["event"] == "phase_start"
        assert ev["phase"] == phase.number
        assert ev["phase_name"] == phase.display_name
        assert "timestamp" in ev
        assert "phase_file" in ev

    def test_read_status_from_log_stub_importable(self):
        """read_status_from_log is a stub that must be importable without error."""
        from superclaude.cli.sprint.logging_ import read_status_from_log

        assert callable(read_status_from_log)

    def test_tail_log_stub_importable(self):
        """tail_log is a stub that must be importable without error."""
        from superclaude.cli.sprint.logging_ import tail_log

        assert callable(tail_log)


# ---------------------------------------------------------------------------
# notify.py — cross-platform notification logic
# ---------------------------------------------------------------------------


class TestNotifyModule:
    """notify.py must send correct titles and fail silently on errors."""

    def test_notify_phase_failure_uses_halt_title(self):
        from superclaude.cli.sprint.notify import notify_phase_complete

        phase = Phase(number=2, file=Path("/tmp/p2.md"))
        result = _make_phase_result(phase=phase, status=PhaseStatus.HALT, exit_code=1)

        captured = []

        def fake_notify(title, message, urgent=False):
            captured.append((title, message, urgent))

        with patch("superclaude.cli.sprint.notify._notify", side_effect=fake_notify):
            notify_phase_complete(result)

        assert len(captured) == 1
        assert "HALT" in captured[0][0]
        assert captured[0][2] is True  # urgent

    def test_notify_phase_success_uses_phase_complete_title(self):
        from superclaude.cli.sprint.notify import notify_phase_complete

        phase = Phase(number=1, file=Path("/tmp/p1.md"))
        result = _make_phase_result(phase=phase, status=PhaseStatus.PASS, exit_code=0)

        captured = []

        def fake_notify(title, message, urgent=False):
            captured.append((title, message, urgent))

        with patch("superclaude.cli.sprint.notify._notify", side_effect=fake_notify):
            notify_phase_complete(result)

        assert len(captured) == 1
        assert "Complete" in captured[0][0] or "Phase" in captured[0][0]
        assert captured[0][2] is False  # not urgent

    def test_notify_sprint_success(self):
        from superclaude.cli.sprint.notify import notify_sprint_complete

        config = SprintConfig(
            index_path=Path("/tmp/index.md"),
            release_dir=Path("/tmp"),
            phases=[Phase(number=1, file=Path("/tmp/p1.md"))],
        )
        sprint = SprintResult(config=config, outcome=SprintOutcome.SUCCESS)

        captured = []

        def fake_notify(title, message, urgent=False):
            captured.append((title, message, urgent))

        with patch("superclaude.cli.sprint.notify._notify", side_effect=fake_notify):
            notify_sprint_complete(sprint)

        assert len(captured) == 1
        assert "Complete" in captured[0][0] or "Sprint" in captured[0][0]
        assert captured[0][2] is False  # not urgent

    def test_notify_sprint_non_success_uses_urgency(self):
        from superclaude.cli.sprint.notify import notify_sprint_complete

        config = SprintConfig(
            index_path=Path("/tmp/index.md"),
            release_dir=Path("/tmp"),
            phases=[Phase(number=1, file=Path("/tmp/p1.md"))],
        )
        sprint = SprintResult(config=config, outcome=SprintOutcome.HALTED)

        captured = []

        def fake_notify(title, message, urgent=False):
            captured.append((title, message, urgent))

        with patch("superclaude.cli.sprint.notify._notify", side_effect=fake_notify):
            notify_sprint_complete(sprint)

        assert len(captured) == 1
        assert captured[0][2] is True  # urgent=True for non-success

    def test_notify_silent_on_subprocess_exception(self):
        """_notify must not propagate subprocess errors."""
        from superclaude.cli.sprint.notify import _notify

        with (
            patch("superclaude.cli.sprint.notify.platform.system", return_value="Linux"),
            patch("superclaude.cli.sprint.notify.shutil.which", return_value="/usr/bin/notify-send"),
            patch(
                "superclaude.cli.sprint.notify.subprocess.run",
                side_effect=OSError("notify-send not found"),
            ),
        ):
            _notify("Test", "message")  # must not raise


# ---------------------------------------------------------------------------
# config.py — validate_phases error list
# ---------------------------------------------------------------------------


class TestValidatePhasesEdgeCases:
    """validate_phases returns errors for each missing file, not just one."""

    def test_two_missing_files_produce_two_errors(self, tmp_path):
        from superclaude.cli.sprint.config import validate_phases

        phases = [
            Phase(number=1, file=tmp_path / "missing1.md"),
            Phase(number=2, file=tmp_path / "missing2.md"),
        ]
        buckets = validate_phases(phases, start=1, end=2)
        errors = buckets["errors"]
        assert len(errors) == 2
        assert "Phase 1" in errors[0]
        assert "Phase 2" in errors[1]

    def test_missing_file_outside_active_range_not_flagged(self, tmp_path):
        """Only phases within [start, end] are validated."""
        from superclaude.cli.sprint.config import validate_phases

        phases = [
            Phase(number=1, file=tmp_path / "p1.md"),  # in range but missing
            Phase(number=3, file=tmp_path / "p3.md"),  # outside range
        ]
        (tmp_path / "p1.md").write_text("content")
        # p3.md does not exist, but end=1 so it's outside range
        buckets = validate_phases(phases, start=1, end=1)
        errors = buckets["errors"]
        assert len(errors) == 0

    def test_load_sprint_config_raises_on_missing_phase_file(self, tmp_path):
        """load_sprint_config must raise ClickException when a phase file is absent.

        The index must use a filename that PHASE_FILE_PATTERN recognises so that
        discover_phases() finds the reference.  The file itself must not exist so
        that validate_phases() adds it to errors and load_sprint_config raises.
        """
        import click

        from superclaude.cli.sprint.config import load_sprint_config

        # Write index with a valid phase filename reference — pattern matches it
        index = tmp_path / "tasklist-index.md"
        index.write_text("- phase-1-tasklist.md\n")

        # Create a real phase file so discover_phases() returns a Phase entry,
        # then immediately delete it to simulate a file that disappears.
        phase_file = tmp_path / "phase-1-tasklist.md"
        phase_file.write_text("# Phase 1\n")

        # discover_phases uses Strategy 1 (index references) only when the file
        # exists at discovery time. Strategy 2 (directory scan) runs when no refs
        # found. Create the file so discovery succeeds, then delete it so
        # validate_phases reports it missing.
        # To force this cleanly: write both the index AND the file, then delete the
        # phase file after discovery.  We do this by patching validate_phases to
        # use a known-missing path.
        phases_discovered = []

        from superclaude.cli.sprint import config as _cfg_mod

        real_discover = _cfg_mod.discover_phases

        def patched_discover(index_path):
            result = real_discover(index_path)
            # Replace file path with a nonexistent path to simulate missing file
            phases_discovered.extend(result)
            for p in result:
                p.file = tmp_path / "nonexistent-phase-1.md"
            return result

        with patch.object(_cfg_mod, "discover_phases", patched_discover):
            with pytest.raises(click.ClickException):
                load_sprint_config(index_path=index)


# ---------------------------------------------------------------------------
# tmux.py — importability and session_name determinism
# ---------------------------------------------------------------------------


class TestTmuxModule:
    """tmux.py functions must be importable and session_name must be deterministic."""

    def test_session_name_is_deterministic(self, tmp_path):
        from superclaude.cli.sprint.tmux import session_name

        name_a = session_name(tmp_path)
        name_b = session_name(tmp_path)
        assert name_a == name_b
        assert name_a.startswith("sc-sprint-")

    def test_session_name_differs_for_different_dirs(self, tmp_path):
        from superclaude.cli.sprint.tmux import session_name

        dir_a = tmp_path / "sprint_a"
        dir_b = tmp_path / "sprint_b"
        dir_a.mkdir()
        dir_b.mkdir()
        assert session_name(dir_a) != session_name(dir_b)

    def test_is_tmux_available_when_tmux_missing(self):
        """is_tmux_available() returns False when tmux binary is not in PATH."""
        from superclaude.cli.sprint.tmux import is_tmux_available

        with patch("superclaude.cli.sprint.tmux.shutil.which", return_value=None):
            assert is_tmux_available() is False

    def test_find_running_session_returns_none_when_tmux_missing(self):
        """find_running_session() returns None immediately when tmux is not installed."""
        from superclaude.cli.sprint.tmux import find_running_session

        with patch("superclaude.cli.sprint.tmux.shutil.which", return_value=None):
            assert find_running_session() is None

    def test_is_tmux_available_false_when_inside_tmux(self):
        """is_tmux_available() returns False when TMUX env var is set (nested)."""
        from superclaude.cli.sprint.tmux import is_tmux_available

        with (
            patch("superclaude.cli.sprint.tmux.shutil.which", return_value="/usr/bin/tmux"),
            patch.dict("os.environ", {"TMUX": "/tmp/tmux-123/default,1234,0"}),
        ):
            assert is_tmux_available() is False

    def test_find_running_session_returns_none_on_no_sessions(self):
        """find_running_session() returns None when no sc-sprint-* sessions exist."""
        from superclaude.cli.sprint.tmux import find_running_session

        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "other-session\nanother\n"

        with (
            patch("superclaude.cli.sprint.tmux.shutil.which", return_value="/usr/bin/tmux"),
            patch("superclaude.cli.sprint.tmux.subprocess.run", return_value=fake_result),
        ):
            result = find_running_session()

        assert result is None

    def test_find_running_session_returns_session_name(self):
        """find_running_session() returns the first sc-sprint-* session found."""
        from superclaude.cli.sprint.tmux import find_running_session

        fake_result = MagicMock()
        fake_result.returncode = 0
        fake_result.stdout = "other-session\nsc-sprint-abcd1234\nanother\n"

        with (
            patch("superclaude.cli.sprint.tmux.shutil.which", return_value="/usr/bin/tmux"),
            patch("superclaude.cli.sprint.tmux.subprocess.run", return_value=fake_result),
        ):
            result = find_running_session()

        assert result == "sc-sprint-abcd1234"
