"""Level 2 — Integration-level tests.

Tests component interactions: logging + collection + classification pipeline.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import pytest

pytestmark = [pytest.mark.diagnostic, pytest.mark.diagnostic_l2]

from superclaude.cli.sprint.debug_logger import LOGGER_NAME, debug_log
from superclaude.cli.sprint.diagnostics import (
    DiagnosticCollector,
    FailureCategory,
    FailureClassifier,
    ReportGenerator,
)
from superclaude.cli.sprint.models import MonitorState, PhaseStatus


class TestLogToClassificationPipeline:
    """End-to-end: emit events → collect → classify → report."""

    def test_stall_scenario_classified_correctly(self, harness):
        phase = harness.phases[0]

        # Emit events including watchdog
        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 0}),
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 60}),
            ("watchdog_triggered", {"phase": 1, "action": "warn", "stall_seconds": 130}),
        ])

        # Create phase result for failure
        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=1)
        ms = MonitorState(stall_seconds=130.0, events_received=5)

        # Collect and classify
        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.STALL
        assert bundle.watchdog_triggered is True

    def test_timeout_scenario_classified_correctly(self, harness):
        phase = harness.phases[0]

        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100, "stall_seconds": 0}),
        ])

        pr = harness.make_phase_result(phase, status=PhaseStatus.TIMEOUT, exit_code=124)
        ms = MonitorState(events_received=10)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.TIMEOUT

    def test_crash_scenario_classified_correctly(self, harness):
        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=137)
        ms = MonitorState(stall_seconds=2.0, events_received=10)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        assert bundle.category == FailureCategory.CRASH

    def test_report_generated_for_classified_failure(self, harness):
        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=1)
        ms = MonitorState(stall_seconds=150.0, events_received=5)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        classifier = FailureClassifier()
        bundle.category = classifier.classify(bundle)

        gen = ReportGenerator()
        report = gen.generate(bundle)

        assert "# Diagnostic Report" in report
        assert "stall" in report
        assert "## Evidence" in report


class TestMultiPhaseDiagnostics:
    """Diagnostics work correctly with multi-phase sprints."""

    def test_collect_isolates_per_phase(self, multi_phase_harness):
        h = multi_phase_harness

        # Emit events for phase 1 and 2
        h.emit_debug_events(h.phases[0], [
            ("poll_tick", {"phase": 1, "pid": 100}),
        ])
        h.emit_debug_events(h.phases[1], [
            ("poll_tick", {"phase": 2, "pid": 200}),
            ("watchdog_triggered", {"phase": 2, "action": "warn", "stall_seconds": 130}),
        ])

        reader = h.get_log_reader()
        p1_events = reader.phase_events(1)
        p2_events = reader.phase_events(2)

        # Phase 1: BEGIN + poll_tick + END = 3
        assert len(p1_events) == 3
        # Phase 2: BEGIN + poll_tick + watchdog + END = 4
        assert len(p2_events) == 4

    def test_report_written_to_correct_path(self, harness):
        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, status=PhaseStatus.ERROR, exit_code=1)
        ms = MonitorState()

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        bundle.category = FailureCategory.ERROR
        bundle.classification_evidence = ["Test error"]

        gen = ReportGenerator()
        diag_path = harness.config.results_dir / f"phase-{phase.number}-diagnostic.md"
        gen.write(bundle, diag_path)

        assert diag_path.exists()
        assert "# Diagnostic Report" in diag_path.read_text()
