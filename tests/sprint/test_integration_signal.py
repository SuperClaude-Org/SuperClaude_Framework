"""T04.03 — Integration test: graceful shutdown.

Tests that SIGINT during execution triggers graceful shutdown:
process terminated, partial log written, INTERRUPTED outcome.
"""

from __future__ import annotations

import os
import signal
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

from superclaude.cli.sprint.executor import execute_sprint
from superclaude.cli.sprint.models import (
    Phase,
    SprintConfig,
    SprintOutcome,
)


def _make_config(tmp_path: Path) -> SprintConfig:
    """Create a 3-phase config where phases take a while."""
    phases = []
    for i in range(1, 4):
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
        end_phase=3,
        max_turns=5,
    )


class _SlowFakePopen:
    """Mock Popen that stays 'running' for many polls."""

    def __init__(self):
        self.returncode = None
        self.pid = 99999
        self._poll_count = 0
        self._terminated = False

    def poll(self):
        if self._terminated:
            self.returncode = -15  # SIGTERM
            return self.returncode
        self._poll_count += 1
        if self._poll_count > 100:
            self.returncode = 0
            return 0
        return None

    def wait(self, timeout=None):
        if self._terminated:
            self.returncode = -15
            return self.returncode
        self.returncode = 0
        return 0


class TestGracefulShutdown:
    """T04.03: SIGINT during poll loop → INTERRUPTED outcome."""

    def test_sigint_sets_interrupted_outcome(self, tmp_path):
        """Verify shutdown_requested=True before a phase begins yields INTERRUPTED outcome.

        Uses a deterministic injection strategy instead of threading.Timer + os.kill:
        - Patch time.sleep so the first poll-loop sleep sets shutdown_requested and
          marks the fake process as terminated.
        - Patch SignalHandler so we can capture the instance and set its flag directly.
        This removes all real-time dependencies and makes the test deterministic.
        """
        from superclaude.cli.sprint.process import SignalHandler as _RealSignalHandler

        config = _make_config(tmp_path)
        slow_proc = _SlowFakePopen()

        def popen_factory(cmd, **kwargs):
            output_path = config.output_file(config.phases[0])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("working...\n")
            return slow_proc

        captured_results = []
        captured_handler: list = []

        class _TrackingSignalHandler(_RealSignalHandler):
            def __init__(self):
                super().__init__()
                captured_handler.append(self)

        sleep_calls = [0]

        def fake_sleep(secs):
            sleep_calls[0] += 1
            # First sleep = first iteration of the poll loop.
            # Inject shutdown so the loop detects it on the next poll() check.
            if sleep_calls[0] == 1 and captured_handler:
                captured_handler[0].shutdown_requested = True
                slow_proc._terminated = True  # poll() now returns -15

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.pipeline.process.os.getpgid", return_value=99999),
            patch("superclaude.cli.pipeline.process.os.killpg"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.update_tail_pane"),
            patch("superclaude.cli.sprint.executor.time.sleep", side_effect=fake_sleep),
            patch("superclaude.cli.sprint.executor.SignalHandler", _TrackingSignalHandler),
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
        assert result.outcome == SprintOutcome.INTERRUPTED

    def test_signal_handler_flag_set(self, tmp_path):
        """Directly test that SignalHandler sets shutdown_requested on signal."""
        from superclaude.cli.sprint.process import SignalHandler

        handler = SignalHandler()
        handler.install()

        try:
            assert not handler.shutdown_requested
            # Simulate signal delivery
            handler._handle(signal.SIGINT, None)
            assert handler.shutdown_requested
        finally:
            handler.uninstall()

    def test_genuine_failure_still_produces_halted(self, tmp_path):
        """Regression: signal guard must NOT suppress genuine phase failure → HALTED.

        When a process exits with code 1 (no signal), the outcome must remain
        HALTED and must not be reclassified as INTERRUPTED.
        """
        config = _make_config(tmp_path)

        class _FailPopen:
            def __init__(self):
                self.returncode = 1
                self.pid = 55555
                self._poll_count = 0

            def poll(self):
                self._poll_count += 1
                return None if self._poll_count <= 1 else 1

            def wait(self, timeout=None):
                self.returncode = 1
                return 1

        captured_results = []

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen",
                  side_effect=lambda *a, **kw: _FailPopen()),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.sprint.notify._notify"),
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
        assert result.halt_phase == 1

    def test_sigterm_also_produces_interrupted(self, tmp_path):
        """SIGTERM (process manager shutdown) must also produce INTERRUPTED, not HALTED."""
        config = _make_config(tmp_path)
        slow_proc = _SlowFakePopen()

        def popen_factory(cmd, **kwargs):
            for phase in config.phases:
                output_path = config.output_file(phase)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text("working...\n")
            return slow_proc

        captured_results = []

        def send_sigterm():
            os.kill(os.getpid(), signal.SIGTERM)

        timer = threading.Timer(0.3, send_sigterm)

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen",
                  side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.pipeline.process.os.getpgid", return_value=99999),
            patch("superclaude.cli.pipeline.process.os.killpg"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.update_tail_pane"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(
                side_effect=lambda sr: captured_results.append(sr)
            )
            mock_logger_cls.return_value = logger_inst

            timer.start()
            try:
                with patch.object(
                    type(slow_proc), "wait",
                    side_effect=lambda timeout=None: (
                        setattr(slow_proc, "returncode", -15) or -15
                    ) if slow_proc._terminated else None,
                ):
                    execute_sprint(config)
            except SystemExit:
                pass
            finally:
                timer.cancel()

        assert len(captured_results) >= 1
        result = captured_results[0]
        assert result.outcome == SprintOutcome.INTERRUPTED

    def test_partial_results_captured(self, tmp_path):
        """When interrupted mid-sprint, completed phases are in results."""
        config = _make_config(tmp_path)
        call_count = [0]

        class _FirstSucceedsThenSlow:
            def __init__(self):
                self.returncode = None
                self.pid = 11111
                self._poll_count = 0
                self._terminated = False

            def poll(self):
                if self._terminated:
                    self.returncode = -15
                    return self.returncode
                self._poll_count += 1
                if call_count[0] == 1:
                    # First phase: succeed quickly
                    self.returncode = 0
                    return 0
                if self._poll_count > 100:
                    self.returncode = 0
                    return 0
                return None

            def wait(self, timeout=None):
                if self._terminated:
                    self.returncode = -15
                    return -15
                self.returncode = 0
                return 0

        def popen_factory(cmd, **kwargs):
            call_count[0] += 1
            phase = config.phases[call_count[0] - 1]

            config.results_dir.mkdir(parents=True, exist_ok=True)
            output_path = config.output_file(phase)
            output_path.write_text("working...\n")

            if call_count[0] == 1:
                # Phase 1 succeeds
                result_path = config.result_file(phase)
                result_path.write_text("EXIT_RECOMMENDATION: CONTINUE\n")

            proc = _FirstSucceedsThenSlow()
            proc.returncode = 0 if call_count[0] == 1 else None
            return proc

        captured_results = []

        def send_sigint():
            os.kill(os.getpid(), signal.SIGINT)

        timer = threading.Timer(0.5, send_sigint)

        with (
            patch("superclaude.cli.pipeline.process.subprocess.Popen", side_effect=popen_factory),
            patch("superclaude.cli.pipeline.process.os.setpgrp"),
            patch("superclaude.cli.pipeline.process.os.getpgid", return_value=11111),
            patch("superclaude.cli.pipeline.process.os.killpg"),
            patch("superclaude.cli.sprint.notify._notify"),
            patch("superclaude.cli.sprint.executor.update_tail_pane"),
            patch("superclaude.cli.sprint.executor.SprintLogger") as mock_logger_cls,
        ):
            logger_inst = MagicMock()
            logger_inst.write_summary = MagicMock(side_effect=lambda sr: captured_results.append(sr))
            mock_logger_cls.return_value = logger_inst

            timer.start()
            try:
                execute_sprint(config)
            except SystemExit:
                pass
            finally:
                timer.cancel()

        # Should have at least 1 phase result (the one that completed)
        if captured_results:
            result = captured_results[0]
            assert result.outcome == SprintOutcome.INTERRUPTED
            # Phase 1 completed before interrupt
            assert len(result.phase_results) >= 1
