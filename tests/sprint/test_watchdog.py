"""Characterization tests for sprint executor watchdog/stall detection (lines 125-162).

Pins current behavior of stall_timeout, stall_action, and _stall_acted
before any refactoring in Phase 2.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    MonitorState,
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


class TestWatchdogKillAction:
    """stall_action='kill' should terminate process and produce TIMEOUT/HALTED."""

    def test_stall_kill_action(self, tmp_path):
        config = _make_config(tmp_path, stall_timeout=10, stall_action="kill")

        # Popen that never exits until terminated
        poll_calls = [0]
        terminated = [False]

        class _KillPopen:
            def __init__(self):
                self.returncode = None
                self.pid = 9999

            def poll(self):
                poll_calls[0] += 1
                if terminated[0]:
                    self.returncode = 1
                    return 1
                return None

            def wait(self, timeout=None):
                self.returncode = 1
                return 1

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.output_file(phase).write_text("some output\n")
            return _KillPopen()

        # Monitor mock that reports stall
        stalled_state = MonitorState(stall_seconds=15.0, events_received=5)

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.pipeline.process.os.getpgid", return_value=9999),
            patch("superclaude.cli.pipeline.process.os.killpg", side_effect=lambda *a, **k: terminated.__setitem__(0, True)),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.time.sleep"),
            patch("superclaude.cli.sprint.executor.OutputMonitor") as monitor_cls,
        ):
            monitor_mock = MagicMock()
            monitor_mock.state = stalled_state
            monitor_cls.return_value = monitor_mock

            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            with pytest.raises(SystemExit) as exc:
                execute_sprint(config)
            assert exc.value.code == 1

        assert len(captured) == 1
        result = captured[0]
        # Kill action on stall should halt the sprint
        assert result.outcome == SprintOutcome.HALTED
        assert result.phase_results[0].exit_code == 124  # treated as timeout


class TestWatchdogWarnAction:
    """stall_action='warn' should print warning but continue execution."""

    def test_stall_warn_action(self, tmp_path):
        config = _make_config(tmp_path, stall_timeout=10, stall_action="warn")

        poll_count = [0]

        class _WarnPopen:
            def __init__(self):
                self.returncode = 0
                self.pid = 8888

            def poll(self):
                poll_count[0] += 1
                if poll_count[0] > 3:
                    self.returncode = 0
                    return 0
                return None

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _WarnPopen()

        stalled_state = MonitorState(stall_seconds=15.0, events_received=5)

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.time.sleep"),
            patch("superclaude.cli.sprint.executor.OutputMonitor") as monitor_cls,
        ):
            monitor_mock = MagicMock()
            monitor_mock.state = stalled_state
            monitor_cls.return_value = monitor_mock

            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            execute_sprint(config)

        assert len(captured) == 1
        result = captured[0]
        # Warn action should NOT kill — sprint continues and succeeds
        assert result.outcome == SprintOutcome.SUCCESS
        assert result.phase_results[0].status == PhaseStatus.PASS


class TestWatchdogStallReset:
    """_stall_acted resets when output resumes (stall_seconds == 0.0)."""

    def test_stall_reset_on_resume(self, tmp_path):
        config = _make_config(tmp_path, stall_timeout=10, stall_action="warn")

        poll_count = [0]

        class _ResumePopen:
            def __init__(self):
                self.returncode = 0
                self.pid = 7777

            def poll(self):
                poll_count[0] += 1
                if poll_count[0] > 5:
                    self.returncode = 0
                    return 0
                return None

            def wait(self, timeout=None):
                self.returncode = 0
                return 0

        def _factory(*args, **kwargs):
            phase = config.phases[0]
            config.results_dir.mkdir(parents=True, exist_ok=True)
            config.result_file(phase).write_text("EXIT_RECOMMENDATION: CONTINUE\n")
            config.output_file(phase).write_text("output\n")
            return _ResumePopen()

        # Sequence of states: stalled -> resumed -> stalled again -> resumed
        # This exercises the _stall_acted reset path (line 161-162)
        states = [
            MonitorState(stall_seconds=15.0, events_received=5),   # stall triggers warn
            MonitorState(stall_seconds=15.0, events_received=5),   # still stalled, _stall_acted=True
            MonitorState(stall_seconds=0.0, events_received=10),   # resumed → reset _stall_acted
            MonitorState(stall_seconds=15.0, events_received=15),  # stall again → warn again
            MonitorState(stall_seconds=0.0, events_received=20),   # resumed
        ]
        state_idx = [0]

        class _StatefulMonitor(MagicMock):
            @property
            def state(self):
                idx = min(state_idx[0], len(states) - 1)
                state_idx[0] += 1
                return states[idx]

        captured = []
        with (
            patch("superclaude.cli.sprint.executor.shutil.which", return_value="/usr/bin/claude"),
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as logger_cls,
            patch("superclaude.cli.sprint.executor.time.sleep"),
            patch("superclaude.cli.sprint.executor.OutputMonitor") as monitor_cls,
        ):
            monitor_mock = _StatefulMonitor()
            monitor_cls.return_value = monitor_mock

            logger = MagicMock()
            logger.write_summary = MagicMock(side_effect=lambda sr: captured.append(sr))
            logger_cls.return_value = logger

            execute_sprint(config)

        assert len(captured) == 1
        result = captured[0]
        # Warn action with resume should succeed
        assert result.outcome == SprintOutcome.SUCCESS
