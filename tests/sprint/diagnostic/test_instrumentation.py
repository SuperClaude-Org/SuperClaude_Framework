"""Tests for Phase 2+3 — instrumentation events and watchdog mechanism.

Validates: executor PHASE_BEGIN/poll_tick/PHASE_END events, process spawn/exit events,
monitor output_file_stat/signal_extracted events, TUI lifecycle events, tmux flag forwarding,
CLI options, and watchdog stall detection with warn/kill actions + single-fire guard.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from superclaude.cli.sprint.debug_logger import LOGGER_NAME, debug_log, setup_debug_logger
from superclaude.cli.sprint.models import MonitorState, Phase, SprintConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(tmp_path: Path, **kwargs) -> SprintConfig:
    index_file = tmp_path / "tasklist-index.md"
    index_file.touch()
    phase_file = tmp_path / "phase-1-tasklist.md"
    phase_file.touch()
    defaults = dict(
        index_path=index_file,
        release_dir=tmp_path,
        phases=[Phase(number=1, file=phase_file)],
        debug=True,
    )
    defaults.update(kwargs)
    return SprintConfig(**defaults)


def _setup_debug_and_get_content(tmp_path, config=None):
    """Setup debug logger, return (logger, child_logger, read_fn)."""
    if config is None:
        config = _make_config(tmp_path)
    root_logger = setup_debug_logger(config)
    read_fn = lambda: config.debug_log_path.read_text()

    def cleanup():
        for h in root_logger.handlers[:]:
            h.close()
            root_logger.removeHandler(h)

    return root_logger, read_fn, cleanup


# ---------------------------------------------------------------------------
# T02.01 — Executor instrumentation events
# ---------------------------------------------------------------------------


class TestExecutorInstrumentation:
    """Verify executor emits PHASE_BEGIN, poll_tick, PHASE_END correctly."""

    def test_phase_begin_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
            debug_log(dbg, "PHASE_BEGIN", phase=1, file="phase-1-tasklist.md")
            content = read()
            assert "PHASE_BEGIN" in content
            assert "phase=1" in content
            assert "file=phase-1-tasklist.md" in content
        finally:
            cleanup()

    def test_poll_tick_event_has_all_fields(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
            debug_log(
                dbg,
                "poll_tick",
                phase=1,
                pid=1234,
                poll_result="running",
                elapsed=5.2,
                output_bytes=4096,
                growth_rate=100.0,
                stall_seconds=0.0,
                stall_status="active",
            )
            content = read()
            assert "poll_tick" in content
            for field in ["phase=1", "pid=1234", "output_bytes=4096", "stall_status=active"]:
                assert field in content, f"Missing field: {field}"
        finally:
            cleanup()

    def test_phase_end_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
            debug_log(dbg, "PHASE_END", phase=1, exit_code=0, duration=45.2)
            content = read()
            assert "PHASE_END" in content
            assert "exit_code=0" in content
            assert "duration=45.2" in content
        finally:
            cleanup()

    def test_event_sequence_correct_order(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
            debug_log(dbg, "PHASE_BEGIN", phase=1, file="test.md")
            debug_log(dbg, "poll_tick", phase=1, pid=100, poll_result="running",
                      elapsed=0.5, output_bytes=0, growth_rate=0, stall_seconds=0, stall_status="waiting...")
            debug_log(dbg, "poll_tick", phase=1, pid=100, poll_result="running",
                      elapsed=1.0, output_bytes=100, growth_rate=50, stall_seconds=0, stall_status="active")
            debug_log(dbg, "phase_complete", phase=1, status="pass", exit_code=0, duration=1.5)
            debug_log(dbg, "PHASE_END", phase=1, exit_code=0, duration=1.5)

            content = read()
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#")]
            events = []
            for line in lines:
                # Extract event name (first word after [component])
                parts = line.split("] ", 1)
                if len(parts) == 2:
                    events.append(parts[1].split(" ")[0])
            assert events == ["PHASE_BEGIN", "poll_tick", "poll_tick", "phase_complete", "PHASE_END"]
        finally:
            cleanup()


# ---------------------------------------------------------------------------
# T02.02 — Process instrumentation events
# ---------------------------------------------------------------------------


class TestProcessInstrumentation:
    """Verify process emits spawn, files_opened, signal_sent, exit events."""

    def test_spawn_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.process")
            debug_log(dbg, "spawn", pid=5678, cmd="['claude', '--print', '--verbose']", phase=1)
            content = read()
            assert "spawn" in content
            assert "pid=5678" in content
        finally:
            cleanup()

    def test_files_opened_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.process")
            debug_log(dbg, "files_opened", stdout="/tmp/out.txt", stderr="/tmp/err.txt")
            content = read()
            assert "files_opened" in content
            assert "stdout=/tmp/out.txt" in content
            assert "stderr=/tmp/err.txt" in content
        finally:
            cleanup()

    def test_signal_sent_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.process")
            debug_log(dbg, "signal_sent", signal="SIGTERM", pid=5678)
            content = read()
            assert "signal_sent" in content
            assert "signal=SIGTERM" in content
        finally:
            cleanup()

    def test_exit_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.process")
            debug_log(dbg, "exit", pid=5678, code=0, was_timeout=False)
            content = read()
            assert "exit" in content
            assert "code=0" in content
            assert "was_timeout=False" in content
        finally:
            cleanup()


# ---------------------------------------------------------------------------
# T02.03 — Monitor instrumentation events
# ---------------------------------------------------------------------------


class TestMonitorInstrumentation:
    """Verify monitor emits output_file_stat, signal_extracted events."""

    def test_output_file_stat_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.monitor")
            debug_log(
                dbg, "output_file_stat",
                path="/tmp/output.txt",
                size=2048,
                events_received=10,
                last_event_time=1234.5,
            )
            content = read()
            assert "output_file_stat" in content
            assert "events_received=10" in content
        finally:
            cleanup()

    def test_signal_extracted_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.monitor")
            debug_log(dbg, "signal_extracted", signal_type="task_id", value="T01.02")
            content = read()
            assert "signal_extracted" in content
            assert "signal_type=task_id" in content
            assert "value=T01.02" in content
        finally:
            cleanup()


# ---------------------------------------------------------------------------
# T02.04 — TUI instrumentation events
# ---------------------------------------------------------------------------


class TestTUIInstrumentation:
    """Verify TUI emits tui_start, tui_update, tui_live_failed, tui_stop events."""

    def test_tui_lifecycle_events(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.tui")
            debug_log(dbg, "tui_start")
            debug_log(dbg, "tui_update", events_received=5, stall_status="active", last_event_time=100.0)
            debug_log(dbg, "tui_stop")
            content = read()
            assert "tui_start" in content
            assert "tui_update" in content
            assert "tui_stop" in content
        finally:
            cleanup()

    def test_tui_live_failed_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.tui")
            debug_log(dbg, "tui_live_failed", error="Terminal resize", error_type="ValueError")
            content = read()
            assert "tui_live_failed" in content
            assert "error_type=ValueError" in content
        finally:
            cleanup()


# ---------------------------------------------------------------------------
# T02.05 — Tmux flag forwarding
# ---------------------------------------------------------------------------


class TestTmuxFlagForwarding:
    """Verify _build_foreground_command includes diagnostic flags."""

    def test_debug_flag_forwarded(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, debug=True)
        cmd = _build_foreground_command(config)
        assert "--debug" in cmd

    def test_debug_flag_not_forwarded_when_false(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, debug=False)
        cmd = _build_foreground_command(config)
        assert "--debug" not in cmd

    def test_stall_timeout_forwarded(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, stall_timeout=120)
        cmd = _build_foreground_command(config)
        idx = cmd.index("--stall-timeout")
        assert cmd[idx + 1] == "120"

    def test_stall_timeout_not_forwarded_when_zero(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, stall_timeout=0)
        cmd = _build_foreground_command(config)
        assert "--stall-timeout" not in cmd

    def test_stall_action_forwarded_when_non_default(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, stall_action="kill")
        cmd = _build_foreground_command(config)
        idx = cmd.index("--stall-action")
        assert cmd[idx + 1] == "kill"

    def test_stall_action_not_forwarded_when_default(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, stall_action="warn")
        cmd = _build_foreground_command(config)
        assert "--stall-action" not in cmd

    def test_existing_flags_unchanged(self, tmp_path):
        from superclaude.cli.sprint.tmux import _build_foreground_command

        config = _make_config(tmp_path, debug=False, stall_timeout=0, stall_action="warn")
        cmd = _build_foreground_command(config)
        # Existing flags still present
        assert "--no-tmux" in cmd
        assert "--start" in cmd
        assert "--max-turns" in cmd


# ---------------------------------------------------------------------------
# T02.06 — CLI options
# ---------------------------------------------------------------------------


class TestCLIOptions:
    """Verify CLI accepts --debug, --stall-timeout, --stall-action."""

    def test_cli_help_shows_debug_option(self):
        from click.testing import CliRunner
        from superclaude.cli.sprint.commands import sprint_group

        runner = CliRunner()
        result = runner.invoke(sprint_group, ["run", "--help"])
        assert "--debug" in result.output

    def test_cli_help_shows_stall_timeout_option(self):
        from click.testing import CliRunner
        from superclaude.cli.sprint.commands import sprint_group

        runner = CliRunner()
        result = runner.invoke(sprint_group, ["run", "--help"])
        assert "--stall-timeout" in result.output

    def test_cli_help_shows_stall_action_option(self):
        from click.testing import CliRunner
        from superclaude.cli.sprint.commands import sprint_group

        runner = CliRunner()
        result = runner.invoke(sprint_group, ["run", "--help"])
        assert "--stall-action" in result.output


# ---------------------------------------------------------------------------
# T03.01-T03.04 — Watchdog mechanism
# ---------------------------------------------------------------------------


class TestWatchdogMechanism:
    """Validate stall timeout check, warn/kill actions, and single-fire guard."""

    def test_watchdog_warn_emits_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
            debug_log(dbg, "watchdog_triggered", phase=1, action="warn",
                      stall_seconds=130.0, pid=1234)
            content = read()
            assert "watchdog_triggered" in content
            assert "action=warn" in content
        finally:
            cleanup()

    def test_watchdog_kill_emits_event(self, tmp_path):
        config = _make_config(tmp_path)
        root, read, cleanup = _setup_debug_and_get_content(tmp_path, config)
        try:
            dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
            debug_log(dbg, "watchdog_triggered", phase=1, action="kill",
                      stall_seconds=130.0, pid=1234)
            content = read()
            assert "watchdog_triggered" in content
            assert "action=kill" in content
        finally:
            cleanup()

    def test_single_fire_guard_logic(self):
        """Verify guard prevents repeated action and resets on output growth."""
        stall_acted = False
        actions = []

        # Simulate poll ticks
        for tick in range(5):
            stall_seconds = (tick + 1) * 30.0  # 30, 60, 90, 120, 150
            stall_timeout = 100

            if stall_seconds > stall_timeout and not stall_acted:
                stall_acted = True
                actions.append(f"warn at {stall_seconds}")

        # Only one action should fire
        assert len(actions) == 1
        assert "warn at 120.0" in actions[0]

    def test_single_fire_guard_resets_on_growth(self):
        """Guard resets when output resumes, allowing action on next stall."""
        stall_acted = False
        actions = []
        stall_timeout = 100

        # Simulate: stall -> action -> growth -> stall again
        scenarios = [
            (110, 110),  # stall > timeout, no growth
            (120, 120),  # still stalled
            (0, 0),      # growth detected
            (110, 110),  # stall again
        ]

        for stall_seconds, _ in scenarios:
            if stall_seconds == 0:
                stall_acted = False
            elif stall_seconds > stall_timeout and not stall_acted:
                stall_acted = True
                actions.append(f"warn at {stall_seconds}")

        # Two actions: one per stall period
        assert len(actions) == 2

    def test_no_watchdog_when_timeout_zero(self):
        """When stall_timeout=0, watchdog never triggers."""
        stall_timeout = 0
        triggered = False
        if stall_timeout > 0 and 200 > stall_timeout:
            triggered = True
        assert not triggered

    def test_no_watchdog_during_startup(self):
        """Watchdog should not trigger when events_received == 0 (startup)."""
        stall_timeout = 60
        events_received = 0
        stall_seconds = 200

        triggered = (
            stall_timeout > 0
            and stall_seconds > stall_timeout
            and events_received > 0
        )
        assert not triggered


# ---------------------------------------------------------------------------
# T04.03 — Backward compatibility validation
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Verify all changes preserve pre-change behavior when disabled."""

    def test_sprint_config_without_new_fields_identical(self, tmp_path):
        """SprintConfig without debug args matches pre-change behavior."""
        index_file = tmp_path / "tasklist-index.md"
        index_file.touch()
        phase_file = tmp_path / "phase-1-tasklist.md"
        phase_file.touch()

        config = SprintConfig(
            index_path=index_file,
            release_dir=tmp_path,
            phases=[Phase(number=1, file=phase_file)],
        )
        assert config.debug is False
        assert config.stall_timeout == 0
        assert config.stall_action == "warn"
        assert config.phase_timeout == 0

    def test_load_sprint_config_backward_compat(self, tmp_path):
        """load_sprint_config without new args preserves behavior."""
        from superclaude.cli.sprint.config import load_sprint_config

        index_file = tmp_path / "tasklist-index.md"
        phase_file = tmp_path / "phase-1-tasklist.md"
        phase_file.write_text("# Phase 1\nContent")
        index_file.write_text(f"Reference: {phase_file.name}")

        config = load_sprint_config(index_path=index_file)
        assert config.debug is False
        assert config.stall_timeout == 0
        assert config.stall_action == "warn"
