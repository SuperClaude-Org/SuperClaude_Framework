"""Negative tests — failure mode validation.

Tests that the diagnostic framework handles edge cases, missing files,
corrupt data, and unexpected states gracefully without crashing.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

pytestmark = [pytest.mark.diagnostic, pytest.mark.diagnostic_negative]

from superclaude.cli.sprint.diagnostics import (
    DiagnosticBundle,
    DiagnosticCollector,
    FailureCategory,
    FailureClassifier,
    ReportGenerator,
)
from superclaude.cli.sprint.models import MonitorState, Phase, PhaseResult, PhaseStatus, SprintConfig


def _make_result(phase, **kwargs):
    now = datetime.now(timezone.utc)
    defaults = dict(
        phase=phase, status=PhaseStatus.ERROR, exit_code=1,
        started_at=now, finished_at=now,
    )
    defaults.update(kwargs)
    return PhaseResult(**defaults)


class TestMissingFiles:
    """Diagnostics handle missing output/error/debug files."""

    def test_missing_output_file(self, harness):
        phase = harness.phases[0]
        # Don't create output file
        pr = _make_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        assert bundle.output_tail == ""

    def test_missing_error_file(self, harness):
        phase = harness.phases[0]
        pr = _make_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        assert bundle.stderr_tail == ""

    def test_missing_debug_log(self, tmp_path):
        """No debug log when debug=False — collector handles gracefully."""
        from tests.sprint.diagnostic.conftest import DiagnosticTestHarness

        h = DiagnosticTestHarness(tmp_path, debug=False)
        phase = h.phases[0]
        pr = _make_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(h.config)
        bundle = collector.collect(phase, pr, ms)
        assert len(bundle.debug_log_entries) == 0
        assert bundle.watchdog_triggered is False
        h.cleanup()


class TestCorruptData:
    """Diagnostics handle corrupt or malformed data."""

    def test_empty_debug_log(self, harness):
        # Overwrite debug log with empty content
        harness.config.debug_log_path.write_text("")
        reader = harness.get_log_reader()
        assert len(reader.entries) == 0

    def test_debug_log_with_only_comments(self, harness):
        harness.config.debug_log_path.write_text(
            "# debug-log-version: 1.0\n# comment\n"
        )
        reader = harness.get_log_reader()
        assert len(reader.entries) == 0

    def test_classifier_with_empty_bundle(self):
        phase = Phase(number=1, file=Path("test.md"))
        pr = PhaseResult(
            phase=phase, status=PhaseStatus.PASS, exit_code=0,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        bundle = DiagnosticBundle(phase=phase, phase_result=pr)
        classifier = FailureClassifier()
        cat = classifier.classify(bundle)
        assert cat == FailureCategory.UNKNOWN


class TestEdgeCases:
    """Edge cases in diagnostic processing."""

    def test_report_with_no_evidence(self):
        phase = Phase(number=1, file=Path("test.md"))
        pr = _make_result(phase)
        bundle = DiagnosticBundle(phase=phase, phase_result=pr)
        gen = ReportGenerator()
        report = gen.generate(bundle)
        assert "# Diagnostic Report" in report

    def test_report_with_empty_strings(self):
        phase = Phase(number=1, file=Path("test.md"))
        pr = _make_result(phase)
        bundle = DiagnosticBundle(
            phase=phase,
            phase_result=pr,
            output_tail="",
            stderr_tail="",
        )
        gen = ReportGenerator()
        report = gen.generate(bundle)
        # Should not include empty sections
        assert "## Output Tail" not in report
        assert "## Stderr Tail" not in report

    def test_phase_events_for_nonexistent_phase(self, log_reader_factory):
        reader = log_reader_factory(
            "# debug-log-version: 1.0\n"
            "2026-01-01T00:00:00.000 DEBUG    [executor] PHASE_BEGIN phase=1\n"
            "2026-01-01T00:00:01.000 DEBUG    [executor] PHASE_END phase=1\n"
        )
        events = reader.phase_events(99)
        assert len(events) == 0
