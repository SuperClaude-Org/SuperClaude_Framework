"""Level 3 — System-level tests.

Tests the full diagnostic framework as an integrated system, validating
that all components work together correctly in realistic scenarios.
"""

from __future__ import annotations

import json
import logging

import pytest

pytestmark = [pytest.mark.diagnostic, pytest.mark.diagnostic_l3]

from superclaude.cli.sprint.debug_logger import LOGGER_NAME, debug_log
from superclaude.cli.sprint.diagnostics import (
    DiagnosticCollector,
    FailureCategory,
    FailureClassifier,
    ReportGenerator,
)
from superclaude.cli.sprint.models import MonitorState, PhaseStatus


class TestFullDiagnosticScenarios:
    """Realistic end-to-end scenarios exercising the entire diagnostic stack."""

    def test_stall_with_output_and_debug(self, harness):
        """Full stall scenario: events flow, stall occurs, watchdog warns, phase fails."""
        phase = harness.phases[0]

        # Simulate NDJSON output that stops
        harness.simulate_phase_output(phase, [
            {"type": "text", "text": "Starting task T01.01"},
            {"type": "tool_use", "tool": "Read"},
            {"type": "tool_use", "tool": "Edit"},
        ])

        harness.simulate_phase_error(phase, "")

        # Emit debug events
        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 0, "stall_status": "active"}),
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 30, "stall_status": "thinking..."}),
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 121, "stall_status": "STALLED"}),
            ("watchdog_triggered", {"phase": 1, "action": "warn", "stall_seconds": 130}),
        ])

        # Collect, classify, report
        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=1)
        ms = MonitorState(stall_seconds=130.0, events_received=3)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)

        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.STALL
        assert bundle.watchdog_triggered
        assert bundle.output_tail != ""

        gen = ReportGenerator()
        report = gen.generate(bundle)
        assert "stall" in report.lower()
        assert "## Output Tail" in report

    def test_timeout_without_debug(self, tmp_path):
        """Timeout scenario with debug disabled — diagnostics still work."""
        from tests.sprint.diagnostic.conftest import DiagnosticTestHarness

        h = DiagnosticTestHarness(tmp_path, debug=False)

        phase = h.phases[0]
        h.simulate_phase_output(phase, [{"type": "text", "text": "output"}])

        pr = h.make_phase_result(phase, status=PhaseStatus.TIMEOUT, exit_code=124)
        ms = MonitorState(events_received=1)

        collector = DiagnosticCollector(h.config)
        bundle = collector.collect(phase, pr, ms)

        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.TIMEOUT
        assert len(bundle.debug_log_entries) == 0  # no debug log
        assert bundle.output_tail != ""  # but output still captured

        gen = ReportGenerator()
        report = gen.generate(bundle)
        assert "timeout" in report.lower()

        h.cleanup()

    def test_crash_with_stderr(self, harness):
        """Crash scenario: process dies immediately with stderr output."""
        phase = harness.phases[0]

        harness.simulate_phase_output(phase, [])
        harness.simulate_phase_error(phase, "Segmentation fault (core dumped)\n")

        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 0}),
        ])

        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=139)
        ms = MonitorState(stall_seconds=1.0, events_received=0)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)

        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.CRASH
        assert "Segmentation fault" in bundle.stderr_tail

        gen = ReportGenerator()
        report = gen.generate(bundle)
        assert "## Stderr Tail" in report

    def test_halt_from_result_file(self, harness):
        """HALT scenario: phase completes but result file says HALT."""
        phase = harness.phases[0]

        # Write result file with HALT
        result_file = harness.config.result_file(phase)
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text("EXIT_RECOMMENDATION: HALT\nstatus: FAIL\n")

        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 0}),
        ])

        pr = harness.make_phase_result(phase, status=PhaseStatus.HALT, exit_code=0)
        ms = MonitorState(stall_seconds=0, events_received=10)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)

        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.ERROR

    def test_diagnostic_report_written_and_readable(self, harness):
        """Full pipeline: collect → classify → write → read back."""
        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=1)
        ms = MonitorState(stall_seconds=150, events_received=5)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        gen = ReportGenerator()
        diag_path = harness.config.results_dir / f"phase-{phase.number}-diagnostic.md"
        gen.write(bundle, diag_path)

        # Read back and verify structure
        content = diag_path.read_text()
        assert "# Diagnostic Report" in content
        assert "## Summary" in content
        assert "## Evidence" in content
