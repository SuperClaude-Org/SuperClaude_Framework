"""Characterization tests for TUI, OutputMonitor lifecycle, and tmux integration.

Pins current behavior of TUI.update(), OutputMonitor reset/start/stop,
TUI exception resilience, and tmux tail pane updates before Phase 2
refactoring.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    PhaseStatus,
    SprintConfig,
    SprintOutcome,
)


def _make_config(tmp_path: Path, num_phases: int = 1, **overrides) -> SprintConfig:
    phases = []
    for i in range(1, num_phases + 1):
        pf = tmp_path / f"phase-{i}-tasklist.md"
        pf.write_text(f"# Phase {i}\n")
        phases.append(Phase(number=i, file=pf, name=f"Phase {i}"))

    index = tmp_path / "tasklist-index.md"
    index.write_text("index\n")

    kwargs = dict(
        index_path=index,
        release_dir=tmp_path,
        phases=phases,
        start_phase=1,
        end_phase=num_phases,
        max_turns=5,
    )
    kwargs.update(overrides)
    return SprintConfig(**kwargs)


class _PassPopen:
    def __init__(self):
        self.returncode = 0
        self.pid = 4000
        self._poll = 0

    def poll(self):
        self._poll += 1
        return None if self._poll <= 1 else 0

    def wait(self, timeout=None):
        self.returncode = 0
        return 0


class TestTUIUpdateCalledWithMonitorState:
    """TUI.update() must be called with MonitorState during execution."""

    def test_tui_update_called_with_monitor_state(self, tmp_path):
        config = _make_config(tmp_path)

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _PassPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.SprintTUI") as tui_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            tui_mock = MagicMock()
            tui_cls.return_value = tui_mock

            execute_sprint(config)

        # TUI.update() should have been called at least once
        assert tui_mock.update.call_count >= 1
        # At least one call should have a MonitorState as second arg
        from superclaude.cli.sprint.models import MonitorState
        monitor_state_seen = False
        for c in tui_mock.update.call_args_list:
            args = c[0]
            if len(args) >= 2 and isinstance(args[1], MonitorState):
                monitor_state_seen = True
                break
        assert monitor_state_seen, "TUI.update() never called with MonitorState"
        # TUI lifecycle: start() and stop() called
        tui_mock.start.assert_called_once()
        tui_mock.stop.assert_called_once()


class TestTUIExceptionNonFatal:
    """TUI.update() raising an exception must NOT abort the sprint."""

    def test_tui_exception_non_fatal(self, tmp_path):
        config = _make_config(tmp_path)

        class _SlowPopen:
            """Popen that runs for a few poll cycles to trigger TUI update in poll loop."""
            def __init__(self):
                self.returncode = 0
                self.pid = 4001
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 2 else 0

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _SlowPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.SprintTUI") as tui_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            tui_mock = MagicMock()
            # Only the poll loop call (line 167) is wrapped in try/except.
            # Calls at lines 92, 237, 271 are NOT protected. We need to raise
            # only during the poll loop. The poll loop call has `phase` (non-None)
            # as 3rd arg AND is not the first call with a non-None 3rd arg.
            # Simplest: track calls and only raise on 2nd call (first poll loop iteration).
            call_count = [0]
            def _tui_update(*args, **kwargs):
                call_count[0] += 1
                # Call 1 = line 92 (before poll loop, phase arg)
                # Call 2 = line 167 (poll loop, phase arg) — PROTECTED
                # Call 3 = line 237 (post-phase, None arg)
                # Call 4 = line 271 (final, None arg)
                if call_count[0] == 2:
                    raise RuntimeError("TUI rendering crashed")
            tui_mock.update.side_effect = _tui_update
            tui_cls.return_value = tui_mock

            execute_sprint(config)

        result = captured[0]
        # Sprint should succeed despite TUI errors
        assert result.outcome == SprintOutcome.SUCCESS
        assert result.phase_results[0].status == PhaseStatus.PASS


class TestOutputMonitorLifecycle:
    """OutputMonitor reset/start/stop lifecycle across phases."""

    def test_output_monitor_lifecycle(self, tmp_path):
        config = _make_config(tmp_path, num_phases=2)
        phase_counter = [0]

        class _Popen:
            def __init__(self):
                self.returncode = 0
                self.pid = 4002
                self._poll = 0

            def poll(self):
                self._poll += 1
                return None if self._poll <= 1 else 0

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase_counter[0] += 1
            phase = config.phases[phase_counter[0] - 1]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text(f"output phase {phase.number}\n")
            return _Popen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.OutputMonitor") as monitor_cls,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            monitor_mock = MagicMock()
            from superclaude.cli.sprint.models import MonitorState
            monitor_mock.state = MonitorState()
            monitor_cls.return_value = monitor_mock

            execute_sprint(config)

        result = captured[0]
        assert result.outcome == SprintOutcome.SUCCESS
        assert len(result.phase_results) == 2

        # Monitor should have been reset once per phase (2 phases)
        assert monitor_mock.reset.call_count == 2
        # Monitor should have been started once per phase
        assert monitor_mock.start.call_count == 2
        # Monitor should have been stopped (at least once per phase + finally cleanup)
        assert monitor_mock.stop.call_count >= 2


class TestTmuxUpdateWithSessionName:
    """tmux update_tail_pane should only be called when session_name is set."""

    def test_tmux_update_with_session_name(self, tmp_path):
        config = _make_config(tmp_path, tmux_session_name="test-sprint")

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _PassPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.update_tail_pane") as tmux_mock,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            execute_sprint(config)

        # tmux update should have been called with the session name
        assert tmux_mock.call_count >= 1
        first_call_args = tmux_mock.call_args_list[0][0]
        assert first_call_args[0] == "test-sprint"

    def test_tmux_not_called_without_session_name(self, tmp_path):
        config = _make_config(tmp_path)  # no tmux_session_name

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _PassPopen()

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.update_tail_pane") as tmux_mock,
        ):
            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            execute_sprint(config)

        # tmux update should NOT have been called
        tmux_mock.assert_not_called()
