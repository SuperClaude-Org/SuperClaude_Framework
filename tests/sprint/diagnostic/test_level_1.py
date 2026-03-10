"""Level 1 — Component-level tests.

Tests individual diagnostic components in isolation with controlled inputs.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.diagnostic, pytest.mark.diagnostic_l1]

from superclaude.cli.sprint.debug_logger import DEBUG_LOG_VERSION


class TestDebugLogReader:
    """DebugLogReader parses structured log files correctly."""

    def test_parses_standard_entries(self, log_reader_factory):
        reader = log_reader_factory(
            "# debug-log-version: 1.0\n"
            "2026-01-01T00:00:00.000 DEBUG    [executor] PHASE_BEGIN phase=1 file=test.md\n"
            "2026-01-01T00:00:01.000 DEBUG    [executor] poll_tick phase=1 pid=1234\n"
        )
        assert len(reader.entries) == 2
        assert reader.entries[0].event == "PHASE_BEGIN"
        assert reader.entries[1].fields["pid"] == "1234"

    def test_extracts_version(self, log_reader_factory):
        reader = log_reader_factory(f"# debug-log-version: {DEBUG_LOG_VERSION}\n")
        assert reader.version == DEBUG_LOG_VERSION

    def test_skips_comment_lines(self, log_reader_factory):
        reader = log_reader_factory(
            "# comment\n"
            "# another\n"
            "2026-01-01T00:00:00.000 DEBUG    [test] event key=val\n"
        )
        assert len(reader.entries) == 1

    def test_skips_empty_lines(self, log_reader_factory):
        reader = log_reader_factory(
            "# debug-log-version: 1.0\n"
            "\n"
            "2026-01-01T00:00:00.000 DEBUG    [test] event\n"
            "\n"
        )
        assert len(reader.entries) == 1

    def test_phase_events_filters_correctly(self, log_reader_factory):
        reader = log_reader_factory(
            "# debug-log-version: 1.0\n"
            "2026-01-01T00:00:00.000 DEBUG    [executor] PHASE_BEGIN phase=1 file=a.md\n"
            "2026-01-01T00:00:01.000 DEBUG    [executor] poll_tick phase=1 pid=100\n"
            "2026-01-01T00:00:02.000 DEBUG    [executor] PHASE_END phase=1 exit_code=0\n"
            "2026-01-01T00:00:03.000 DEBUG    [executor] PHASE_BEGIN phase=2 file=b.md\n"
            "2026-01-01T00:00:04.000 DEBUG    [executor] poll_tick phase=2 pid=200\n"
            "2026-01-01T00:00:05.000 DEBUG    [executor] PHASE_END phase=2 exit_code=0\n"
        )
        p1 = reader.phase_events(1)
        p2 = reader.phase_events(2)
        assert len(p1) == 3
        assert len(p2) == 3
        assert all(e.fields.get("phase") in ("1", None) for e in p1)

    def test_events_filter_by_name(self, log_reader_factory):
        reader = log_reader_factory(
            "# debug-log-version: 1.0\n"
            "2026-01-01T00:00:00.000 DEBUG    [executor] PHASE_BEGIN phase=1\n"
            "2026-01-01T00:00:01.000 DEBUG    [executor] poll_tick phase=1\n"
            "2026-01-01T00:00:02.000 DEBUG    [executor] poll_tick phase=1\n"
            "2026-01-01T00:00:03.000 DEBUG    [executor] PHASE_END phase=1\n"
        )
        assert len(reader.events("poll_tick")) == 2
        assert len(reader.events("PHASE_BEGIN")) == 1


class TestDebugLogReaderEntry:
    """Individual entry parsing."""

    def test_timestamp_extracted(self, log_reader_factory):
        reader = log_reader_factory(
            "2026-03-04T19:00:00.123 DEBUG    [test] event\n"
        )
        assert reader.entries[0].timestamp == "2026-03-04T19:00:00.123"

    def test_level_extracted(self, log_reader_factory):
        reader = log_reader_factory(
            "2026-01-01T00:00:00.000 WARNING  [test] event\n"
        )
        assert reader.entries[0].level == "WARNING"

    def test_component_extracted(self, log_reader_factory):
        reader = log_reader_factory(
            "2026-01-01T00:00:00.000 DEBUG    [monitor] event\n"
        )
        assert reader.entries[0].component == "monitor"

    def test_multiple_fields_extracted(self, log_reader_factory):
        reader = log_reader_factory(
            "2026-01-01T00:00:00.000 DEBUG    [executor] poll_tick elapsed=5.2 output_bytes=4096 pid=1234\n"
        )
        entry = reader.entries[0]
        assert entry.fields["elapsed"] == "5.2"
        assert entry.fields["output_bytes"] == "4096"
        assert entry.fields["pid"] == "1234"
