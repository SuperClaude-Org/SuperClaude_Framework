"""Tests for sprint executor — status determination and orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.sprint.executor import _determine_phase_status, execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
)


def _make_config(tmp_path: Path, num_phases: int = 2) -> SprintConfig:
    phases = []
    for i in range(1, num_phases + 1):
        pf = tmp_path / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}\n")
        phases.append(Phase(number=i, file=pf, name=f"Phase {i}"))

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


class TestDeterminePhaseStatus:
    """Test the 7-level status priority chain."""

    def test_timeout_exit_code(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        output_file.write_text("some output")

        status = _determine_phase_status(
            exit_code=124,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.TIMEOUT

    def test_timeout_overrides_result_file(self, tmp_path):
        """Timeout (exit 124) takes priority over result file content."""
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=124,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.TIMEOUT

    def test_nonzero_exit_error(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        output_file.write_text("some output")

        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    def test_nonzero_exit_overrides_continue_signal(self, tmp_path):
        """Non-zero exit takes priority over CONTINUE signal."""
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=1,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    def test_halt_signal(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: HALT")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_continue_signal(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("EXIT_RECOMMENDATION: CONTINUE")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_yaml_status_pass(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: PASS\n---\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_yaml_status_fail(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: FAIL\n---\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_result_file_no_signals(self, tmp_path):
        result_file = tmp_path / "result.md"
        result_file.write_text("Some result content without signals")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_SIGNAL

    def test_no_result_file_with_output(self, tmp_path):
        result_file = tmp_path / "result.md"
        # Don't create result file
        output_file = tmp_path / "output.txt"
        output_file.write_text("Claude output here")

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS_NO_REPORT

    def test_no_result_no_output(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        # Neither file exists

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    def test_empty_output_file(self, tmp_path):
        result_file = tmp_path / "result.md"
        output_file = tmp_path / "output.txt"
        output_file.write_text("")  # empty

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.ERROR

    # --- Regression tests for case-sensitivity and signal conflict fixes ---

    def test_continue_signal_case_insensitive(self, tmp_path):
        """Lowercase EXIT_RECOMMENDATION: continue must still produce PASS."""
        result_file = tmp_path / "result.md"
        result_file.write_text("exit_recommendation: continue\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.PASS

    def test_halt_signal_case_insensitive(self, tmp_path):
        """Lowercase EXIT_RECOMMENDATION: halt must still produce HALT."""
        result_file = tmp_path / "result.md"
        result_file.write_text("exit_recommendation: halt\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_both_continue_and_halt_halt_wins(self, tmp_path):
        """When both EXIT_RECOMMENDATION tokens appear, HALT must win (safer outcome)."""
        result_file = tmp_path / "result.md"
        # CONTINUE appears before HALT — HALT must still win
        result_file.write_text(
            "EXIT_RECOMMENDATION: CONTINUE\n"
            "Some tasks failed.\n"
            "EXIT_RECOMMENDATION: HALT\n"
        )
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT

    def test_partial_status_produces_halt(self, tmp_path):
        """PARTIAL status in result file must produce HALT (existing behavior, regression guard)."""
        result_file = tmp_path / "result.md"
        result_file.write_text("---\nstatus: PARTIAL\n---\n")
        output_file = tmp_path / "output.txt"

        status = _determine_phase_status(
            exit_code=0,
            result_file=result_file,
            output_file=output_file,
        )
        assert status == PhaseStatus.HALT


class TestExecuteSprintIntegrationCoverage:
    def test_execute_sprint_pass(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)

        class _PassPopen:
            def __init__(self):
                self.returncode = 0
                self.pid = 1001
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 1 else 0

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _PassPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger
            execute_sprint(config)

        assert captured[0].outcome == SprintOutcome.SUCCESS
        assert captured[0].phase_results[0].status == PhaseStatus.PASS

    def test_execute_sprint_halt(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)

        class _HaltPopen:
            def __init__(self):
                self.returncode = 0
                self.pid = 1002
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 1 else 0

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: HALT\n")
            config.output_file(phase).write_text("output\n")
            return _HaltPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger
            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        assert captured[0].outcome == SprintOutcome.HALTED
        assert captured[0].halt_phase == 1

    def test_execute_sprint_timeout_exit_code_124(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)

        class _TimeoutPopen:
            def __init__(self):
                self.returncode = 1
                self.pid = 1003

            def poll(self):
                return None

            def wait(self, timeout=None):
                return 1

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.output_file(phase).write_text("still running\n")
            return _TimeoutPopen()

        monotonic_calls = [0]

        def _fast_monotonic():
            monotonic_calls[0] += 1
            if monotonic_calls[0] <= 2:
                return 100.0
            return 999999.0

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.process.os.getpgid", return_value=1003),
            patch("superclaude.cli.sprint.process.os.killpg"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.time.monotonic", side_effect=_fast_monotonic),
            patch("superclaude.cli.sprint.executor.time.sleep"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger
            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        assert captured[0].outcome == SprintOutcome.HALTED
        assert captured[0].phase_results[0].status == PhaseStatus.TIMEOUT
        assert captured[0].phase_results[0].exit_code == 124

    def test_execute_sprint_interrupted(self, tmp_path):
        config = _make_config(tmp_path, num_phases=1)

        class _InterruptPopen:
            def __init__(self):
                self.returncode = None
                self.pid = 1004
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 2 else -15

            def wait(self, timeout=None):
                self.returncode = -15
                return -15

        from superclaude.cli.sprint.process import SignalHandler as _RealSignalHandler

        captured_handler = []

        class _TrackingSignalHandler(_RealSignalHandler):
            def __init__(self):
                super().__init__()
                captured_handler.append(self)

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.output_file(phase).write_text("running\n")
            return _InterruptPopen()

        sleep_calls = [0]

        def _sleep(_secs):
            sleep_calls[0] += 1
            if sleep_calls[0] == 1 and captured_handler:
                captured_handler[0].shutdown_requested = True

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.sprint.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.sprint.process.os.setpgrp"),
            patch("superclaude.cli.sprint.process.os.getpgid", return_value=1004),
            patch("superclaude.cli.sprint.process.os.killpg"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SignalHandler", _TrackingSignalHandler),
            patch("superclaude.cli.sprint.executor.time.sleep", side_effect=_sleep),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger
            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        assert captured[0].outcome == SprintOutcome.INTERRUPTED
        assert captured[0].phase_results == []
