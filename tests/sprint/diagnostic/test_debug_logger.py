"""Tests for debug_logger module — Phase 1 foundation tests.

Covers: _FlushHandler, _DebugFormatter, setup_debug_logger(), debug_log(),
and SprintConfig diagnostic field additions.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

import pytest

from superclaude.cli.sprint.debug_logger import (
    DEBUG_LOG_VERSION,
    LOGGER_NAME,
    _DebugFormatter,
    _FlushHandler,
    debug_log,
    setup_debug_logger,
)
from superclaude.cli.sprint.models import Phase, SprintConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(tmp_path: Path, debug: bool = True, **kwargs) -> SprintConfig:
    """Build a minimal SprintConfig pointing at tmp_path."""
    index_file = tmp_path / "tasklist-index.md"
    index_file.touch()
    phase_file = tmp_path / "phase-1-tasklist.md"
    phase_file.touch()
    return SprintConfig(
        index_path=index_file,
        release_dir=tmp_path,
        phases=[Phase(number=1, file=phase_file)],
        debug=debug,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# T01.01 — _FlushHandler
# ---------------------------------------------------------------------------


class TestFlushHandler:
    """_FlushHandler must flush to disk after every emit."""

    def test_entry_on_disk_after_emit(self, tmp_path):
        log_file = tmp_path / "test.log"
        handler = _FlushHandler(str(log_file), mode="w")
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger = logging.getLogger("test.flush_handler")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.debug("crash-safe entry")

        # Read without closing — data must already be on disk
        content = log_file.read_text()
        assert "crash-safe entry" in content

        handler.close()
        logger.removeHandler(handler)

    def test_io_errors_suppressed(self, tmp_path):
        """I/O errors in emit() do not propagate."""
        log_file = tmp_path / "test.log"
        handler = _FlushHandler(str(log_file), mode="w")

        logger = logging.getLogger("test.flush_handler_err")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        # Close the stream to force an I/O error on next emit
        handler.close()

        # Should not raise
        logger.debug("this should not crash")

        logger.removeHandler(handler)


# ---------------------------------------------------------------------------
# T01.02 — _DebugFormatter
# ---------------------------------------------------------------------------


class TestDebugFormatter:
    """_DebugFormatter produces structured output matching the spec."""

    def test_format_matches_spec_pattern(self):
        formatter = _DebugFormatter()
        record = logging.LogRecord(
            name="superclaude.sprint.debug.executor",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="poll_tick pid=1234 elapsed=5.2",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)

        # Pattern: timestamp LEVEL    [component] message
        pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3} \w+\s+\[executor\] poll_tick pid=1234 elapsed=5.2"
        assert re.match(pattern, output), f"Output did not match pattern: {output}"

    def test_timestamp_is_iso8601_with_milliseconds(self):
        formatter = _DebugFormatter()
        record = logging.LogRecord(
            name="superclaude.sprint.debug.test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test event",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        ts = output.split(" ")[0]
        # ISO 8601 with milliseconds: 2026-03-04T19:00:00.123
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$", ts)

    def test_component_extracted_from_logger_name(self):
        formatter = _DebugFormatter()
        record = logging.LogRecord(
            name="superclaude.sprint.debug.monitor",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="event",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "[monitor]" in output

    def test_level_uppercase(self):
        formatter = _DebugFormatter()
        record = logging.LogRecord(
            name="a.b",
            level=logging.WARNING,
            pathname="",
            lineno=0,
            msg="x",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "WARNING" in output


# ---------------------------------------------------------------------------
# T01.03 — setup_debug_logger()
# ---------------------------------------------------------------------------


class TestSetupDebugLogger:
    """setup_debug_logger configures enabled and disabled paths correctly."""

    def test_enabled_creates_file_with_version_header(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)

        assert config.debug_log_path.exists()
        content = config.debug_log_path.read_text()
        assert content.startswith(f"# debug-log-version: {DEBUG_LOG_VERSION}\n")

        # Clean up
        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)

    def test_disabled_no_file_created(self, tmp_path):
        config = _make_config(tmp_path, debug=False)
        logger = setup_debug_logger(config)

        assert not config.debug_log_path.exists()
        assert any(isinstance(h, logging.NullHandler) for h in logger.handlers)

        for h in logger.handlers[:]:
            logger.removeHandler(h)

    def test_logger_propagate_false(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)
        assert logger.propagate is False

        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)

    def test_logger_name_correct(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)
        assert logger.name == LOGGER_NAME

        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)

    def test_enabled_logger_can_write(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)

        child = logging.getLogger(f"{LOGGER_NAME}.executor")
        child.debug("poll_tick pid=1234")

        content = config.debug_log_path.read_text()
        assert "poll_tick pid=1234" in content
        assert "[executor]" in content

        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)


# ---------------------------------------------------------------------------
# T01.04 — debug_log() helper
# ---------------------------------------------------------------------------


class TestDebugLog:
    """debug_log() emits structured events and is a no-op when disabled."""

    def test_structured_output_format(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)
        child = logging.getLogger(f"{LOGGER_NAME}.executor")

        debug_log(child, "poll_tick", pid=1234, elapsed=5.2)

        content = config.debug_log_path.read_text()
        # Key-value pairs should be present (sorted)
        assert "poll_tick" in content
        assert "elapsed=5.2" in content
        assert "pid=1234" in content

        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)

    def test_noop_when_disabled(self, tmp_path):
        config = _make_config(tmp_path, debug=False)
        logger = setup_debug_logger(config)
        child = logging.getLogger(f"{LOGGER_NAME}.executor")

        # Should not raise, should not create file
        debug_log(child, "poll_tick", pid=1234)
        assert not config.debug_log_path.exists()

        for h in logger.handlers[:]:
            logger.removeHandler(h)

    def test_noop_performance(self, tmp_path):
        """Disabled path should be very fast (< 1ms per call)."""
        config = _make_config(tmp_path, debug=False)
        logger = setup_debug_logger(config)
        child = logging.getLogger(f"{LOGGER_NAME}.executor")

        start = time.monotonic()
        for _ in range(10000):
            debug_log(child, "poll_tick", pid=1234, elapsed=5.2)
        elapsed = time.monotonic() - start

        # 10k calls in < 0.1s = < 10 microseconds each
        assert elapsed < 0.1, f"No-op path too slow: {elapsed:.3f}s for 10k calls"

        for h in logger.handlers[:]:
            logger.removeHandler(h)

    def test_event_without_kwargs(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)
        child = logging.getLogger(f"{LOGGER_NAME}.executor")

        debug_log(child, "PHASE_BEGIN")

        content = config.debug_log_path.read_text()
        assert "PHASE_BEGIN" in content

        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)

    def test_handles_various_value_types(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        logger = setup_debug_logger(config)
        child = logging.getLogger(f"{LOGGER_NAME}.test")

        debug_log(child, "test_event", count=42, rate=3.14, name="foo", flag=None)

        content = config.debug_log_path.read_text()
        assert "count=42" in content
        assert "rate=3.14" in content
        assert "name=foo" in content
        assert "flag=None" in content

        for h in logger.handlers[:]:
            h.close()
            logger.removeHandler(h)


# ---------------------------------------------------------------------------
# T01.05 — SprintConfig diagnostic fields
# ---------------------------------------------------------------------------


class TestSprintConfigDiagnosticFields:
    """New diagnostic fields on SprintConfig must default to pre-change behavior."""

    def test_default_debug_false(self, tmp_path):
        config = _make_config(tmp_path, debug=False)
        assert config.debug is False

    def test_default_stall_timeout_zero(self, tmp_path):
        config = _make_config(tmp_path)
        assert config.stall_timeout == 0

    def test_default_stall_action_warn(self, tmp_path):
        config = _make_config(tmp_path)
        assert config.stall_action == "warn"

    def test_default_phase_timeout_zero(self, tmp_path):
        config = _make_config(tmp_path)
        assert config.phase_timeout == 0

    def test_debug_log_path_in_results_dir(self, tmp_path):
        config = _make_config(tmp_path)
        assert config.debug_log_path == tmp_path / "results" / "debug.log"

    def test_backward_compat_existing_instantiation(self, tmp_path):
        """SprintConfig without new args produces identical behavior."""
        index_file = tmp_path / "tasklist-index.md"
        index_file.touch()
        phase_file = tmp_path / "phase-1-tasklist.md"
        phase_file.touch()

        # Original instantiation pattern (no new kwargs)
        config = SprintConfig(
            index_path=index_file,
            release_dir=tmp_path,
            phases=[Phase(number=1, file=phase_file)],
        )
        assert config.debug is False
        assert config.stall_timeout == 0
        assert config.stall_action == "warn"
        assert config.phase_timeout == 0

    def test_custom_values(self, tmp_path):
        config = _make_config(
            tmp_path,
            debug=True,
            stall_timeout=120,
            stall_action="kill",
            phase_timeout=3600,
        )
        assert config.debug is True
        assert config.stall_timeout == 120
        assert config.stall_action == "kill"
        assert config.phase_timeout == 3600
