"""Tests for pipeline ClaudeProcess lifecycle hooks (on_spawn, on_signal, on_exit).

Verifies that hooks fire with correct arguments on start(), terminate(), and wait() paths.
"""

from __future__ import annotations

import builtins
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.pipeline.process import ClaudeProcess


@pytest.fixture
def tmp_output(tmp_path: Path):
    """Create output/error files for ClaudeProcess."""
    return tmp_path / "out.txt", tmp_path / "err.txt"


def _make_proc(tmp_output, **hook_kwargs) -> ClaudeProcess:
    out, err = tmp_output
    return ClaudeProcess(
        prompt="test prompt",
        output_file=out,
        error_file=err,
        max_turns=1,
        timeout_seconds=5,
        **hook_kwargs,
    )


class TestOnSpawnHook:
    """Verify on_spawn fires with pid after start()."""

    def test_on_spawn_called_with_pid(self, tmp_output):
        on_spawn = MagicMock()
        proc = _make_proc(tmp_output, on_spawn=on_spawn)

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 12345

        with patch("superclaude.cli.pipeline.process.subprocess.Popen", return_value=fake_popen):
            proc.start()

        on_spawn.assert_called_once_with(12345)

    def test_on_spawn_none_no_error(self, tmp_output):
        proc = _make_proc(tmp_output)  # no hook

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 99

        with patch("superclaude.cli.pipeline.process.subprocess.Popen", return_value=fake_popen):
            proc.start()
        # Should not raise


class TestOnSignalHook:
    """Verify on_signal fires with (pid, signal_name) before signal send in terminate()."""

    def test_on_signal_called_before_sigterm(self, tmp_output):
        on_signal = MagicMock()
        proc = _make_proc(tmp_output, on_signal=on_signal)

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 555
        fake_popen.poll.return_value = None  # process still running
        fake_popen.wait.return_value = -15
        fake_popen.returncode = -15
        proc._process = fake_popen

        # Disable pgroup by making hasattr checks fail for os attrs
        original_hasattr = builtins.hasattr

        def patched_hasattr(obj, name):
            if obj is os and name in ("getpgid", "killpg"):
                return False
            return original_hasattr(obj, name)

        with patch("builtins.hasattr", side_effect=patched_hasattr):
            with patch.object(proc, "_close_handles"):
                proc.terminate()

        on_signal.assert_called_once_with(555, "SIGTERM")

    def test_on_signal_none_no_error(self, tmp_output):
        proc = _make_proc(tmp_output)  # no hook

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 555
        fake_popen.poll.return_value = 0  # already exited
        proc._process = fake_popen

        proc.terminate()  # Should not raise


class TestOnExitHookWaitPath:
    """Verify on_exit fires with (pid, returncode) on normal wait() completion."""

    def test_on_exit_called_on_normal_wait(self, tmp_output):
        on_exit = MagicMock()
        proc = _make_proc(tmp_output, on_exit=on_exit)

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 777
        fake_popen.returncode = 0
        fake_popen.wait.return_value = 0
        proc._process = fake_popen

        with patch.object(proc, "_close_handles"):
            rc = proc.wait()

        assert rc == 0
        on_exit.assert_called_once_with(777, 0)

    def test_on_exit_called_with_nonzero_returncode(self, tmp_output):
        on_exit = MagicMock()
        proc = _make_proc(tmp_output, on_exit=on_exit)

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 888
        fake_popen.returncode = 1
        fake_popen.wait.return_value = 1
        proc._process = fake_popen

        with patch.object(proc, "_close_handles"):
            rc = proc.wait()

        assert rc == 1
        on_exit.assert_called_once_with(888, 1)


class TestOnExitHookTerminatePath:
    """Verify on_exit fires with (pid, returncode) in terminate() path."""

    def test_on_exit_called_in_terminate(self, tmp_output):
        on_exit = MagicMock()
        proc = _make_proc(tmp_output, on_exit=on_exit)

        fake_popen = MagicMock(spec=subprocess.Popen)
        fake_popen.pid = 999
        fake_popen.poll.return_value = None  # still running
        fake_popen.returncode = -15
        fake_popen.wait.return_value = -15
        proc._process = fake_popen

        # Disable pgroup to simplify test
        with patch("superclaude.cli.pipeline.process.hasattr", return_value=False):
            with patch.object(proc, "_close_handles"):
                proc.terminate()

        on_exit.assert_called_once_with(999, -15)


class TestHookDefaultsNone:
    """Verify all hooks default to None and don't affect existing behavior."""

    def test_defaults_are_none(self, tmp_output):
        proc = _make_proc(tmp_output)
        assert proc._on_spawn is None
        assert proc._on_signal is None
        assert proc._on_exit is None
