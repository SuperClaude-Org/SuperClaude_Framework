"""Tests for sprint process management — command construction, env, signals."""

import builtins
import signal
from pathlib import Path
from unittest.mock import MagicMock, patch

from superclaude.cli.sprint.models import Phase, SprintConfig
from superclaude.cli.sprint.process import ClaudeProcess, SignalHandler


def _make_config(**kwargs):
    defaults = dict(
        index_path=Path("/tmp/tasklist-index.md"),
        release_dir=Path("/tmp/release"),
        phases=[Phase(number=1, file=Path("/tmp/phase-1-tasklist.md"))],
        max_turns=50,
    )
    defaults.update(kwargs)
    return SprintConfig(**defaults)


class TestClaudeProcess:
    """Test command construction and environment building."""

    def test_build_command_required_flags(self):
        config = _make_config()
        phase = config.phases[0]
        proc = ClaudeProcess(config, phase)

        cmd = proc.build_command()
        assert "claude" in cmd
        assert "--print" in cmd
        assert "--no-session-persistence" in cmd
        assert "--output-format" in cmd
        assert "stream-json" in cmd
        assert "--max-turns" in cmd
        assert "50" in cmd

    def test_build_command_permission_flag(self):
        config = _make_config(permission_flag="--dangerously-skip-permissions")
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--dangerously-skip-permissions" in cmd

    def test_build_command_with_model(self):
        config = _make_config(model="claude-sonnet")
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--model" in cmd
        assert "claude-sonnet" in cmd

    def test_build_command_without_model(self):
        config = _make_config(model="")
        proc = ClaudeProcess(config, config.phases[0])
        cmd = proc.build_command()
        assert "--model" not in cmd

    def test_build_env_claudecode_removed(self):
        config = _make_config()
        proc = ClaudeProcess(config, config.phases[0])
        env = proc.build_env()
        assert "CLAUDECODE" not in env

    def test_build_prompt_contains_task_unified(self):
        config = _make_config()
        proc = ClaudeProcess(config, config.phases[0])
        prompt = proc.build_prompt()
        assert "/sc:task-unified" in prompt

    def test_build_prompt_contains_compliance_strict(self):
        config = _make_config()
        proc = ClaudeProcess(config, config.phases[0])
        prompt = proc.build_prompt()
        assert "--compliance strict" in prompt

    def test_timeout_calculation(self):
        config = _make_config(max_turns=50)
        proc = ClaudeProcess(config, config.phases[0])
        # 50 * 120 + 300 = 6300
        assert proc.timeout_seconds == 6300

    def test_timeout_calculation_custom(self):
        config = _make_config(max_turns=100)
        proc = ClaudeProcess(config, config.phases[0])
        assert proc.timeout_seconds == 12300


class TestClaudeProcessPlatformFallback:
    def test_start_without_setpgrp_fallback(self, tmp_path):
        config = _make_config(
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
        )
        config.phases[0].file.write_text("# Phase 1\n")
        proc = ClaudeProcess(config, config.phases[0])

        fake_process = MagicMock()
        with (
            patch("superclaude.cli.sprint.process.hasattr", side_effect=lambda obj, name: False if obj.__name__ == "os" and name == "setpgrp" else builtins.hasattr(obj, name)),
            patch("superclaude.cli.sprint.process.subprocess.Popen", return_value=fake_process) as mock_popen,
        ):
            proc.start()

        kwargs = mock_popen.call_args.kwargs
        assert "preexec_fn" not in kwargs

    def test_terminate_non_unix_fallback_calls_process_methods(self, tmp_path):
        config = _make_config(
            release_dir=tmp_path,
            phases=[Phase(number=1, file=tmp_path / "phase-1-tasklist.md")],
        )
        config.phases[0].file.write_text("# Phase 1\n")
        proc = ClaudeProcess(config, config.phases[0])

        fake_process = MagicMock()
        fake_process.pid = 43210
        fake_process.poll.return_value = None
        proc._process = fake_process

        with patch(
            "superclaude.cli.sprint.process.hasattr",
            side_effect=lambda obj, name: False
            if obj.__name__ == "os" and name in {"getpgid", "killpg"}
            else builtins.hasattr(obj, name),
        ):
            proc.terminate()

        fake_process.terminate.assert_called_once()
        fake_process.wait.assert_called()


class TestSignalHandler:
    """Test signal handler registration and flag management."""

    def test_initial_state(self):
        handler = SignalHandler()
        assert handler.shutdown_requested is False

    def test_install_uninstall(self):
        handler = SignalHandler()
        original_sigint = signal.getsignal(signal.SIGINT)

        handler.install()
        # Signal handler should be changed
        assert signal.getsignal(signal.SIGINT) != original_sigint

        handler.uninstall()
        # Should be restored
        current = signal.getsignal(signal.SIGINT)
        assert current == original_sigint

    def test_handle_sets_flag(self):
        handler = SignalHandler()
        handler.install()

        try:
            # Directly call the handler
            handler._handle(signal.SIGINT, None)
            assert handler.shutdown_requested is True
        finally:
            handler.uninstall()

    def test_idempotent_handle(self):
        handler = SignalHandler()
        handler.install()

        try:
            handler._handle(signal.SIGINT, None)
            handler._handle(signal.SIGTERM, None)
            assert handler.shutdown_requested is True
        finally:
            handler.uninstall()
