"""Level 0 — Pipeline smoke tests.

Validates the fundamental diagnostic pipeline works end-to-end:
debug logger → events → debug log file → reader → parse → assertions.
"""

from __future__ import annotations

import logging

import pytest

pytestmark = [pytest.mark.diagnostic, pytest.mark.diagnostic_l0]

from superclaude.cli.sprint.debug_logger import DEBUG_LOG_VERSION, LOGGER_NAME, debug_log


class TestL0DebugLogPipeline:
    """Smoke tests: log → file → reader → parsed entries."""

    def test_debug_log_created_with_version_header(self, harness):
        reader = harness.get_log_reader()
        assert reader.version == DEBUG_LOG_VERSION

    def test_event_appears_in_log(self, harness):
        phase = harness.phases[0]
        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100, "elapsed": 0.5}),
        ])
        reader = harness.get_log_reader()
        assert len(reader.events("poll_tick")) >= 1

    def test_phase_begin_end_bracketing(self, harness):
        phase = harness.phases[0]
        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100}),
        ])
        reader = harness.get_log_reader()
        begins = reader.events("PHASE_BEGIN")
        ends = reader.events("PHASE_END")
        assert len(begins) == 1
        assert len(ends) == 1

    def test_phase_events_extraction(self, harness):
        phase = harness.phases[0]
        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 100}),
            ("poll_tick", {"phase": 1, "pid": 100}),
        ])
        reader = harness.get_log_reader()
        phase_events = reader.phase_events(1)
        # PHASE_BEGIN + 2 poll_tick + PHASE_END = 4
        assert len(phase_events) == 4

    def test_entry_fields_parsed(self, harness):
        phase = harness.phases[0]
        harness.emit_debug_events(phase, [
            ("poll_tick", {"phase": 1, "pid": 1234, "elapsed": 5.2}),
        ])
        reader = harness.get_log_reader()
        ticks = reader.events("poll_tick")
        assert ticks[0].fields["pid"] == "1234"
        assert ticks[0].component == "executor"

    def test_empty_log_when_disabled(self, tmp_path):
        from tests.sprint.diagnostic.conftest import DiagnosticTestHarness
        h = DiagnosticTestHarness(tmp_path, debug=False)
        reader = h.get_log_reader()
        assert len(reader.entries) == 0
        h.cleanup()


class TestL0DiagnosticPipeline:
    """Smoke tests: collect → classify → report."""

    def test_collector_produces_bundle(self, harness):
        from superclaude.cli.sprint.diagnostics import DiagnosticCollector
        from superclaude.cli.sprint.models import MonitorState

        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, exit_code=1)
        ms = MonitorState(events_received=5)

        collector = DiagnosticCollector(harness.config)
        bundle = collector.collect(phase, pr, ms)
        assert bundle.phase == phase
        assert bundle.monitor_state_snapshot is not None

    def test_classifier_returns_category(self, harness):
        from superclaude.cli.sprint.diagnostics import (
            DiagnosticBundle,
            FailureCategory,
            FailureClassifier,
        )

        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, exit_code=124)
        bundle = DiagnosticBundle(phase=phase, phase_result=pr)
        bundle.phase_result.status = pr.status

        classifier = FailureClassifier()
        cat = classifier.classify(bundle)
        assert isinstance(cat, FailureCategory)

    def test_report_generator_produces_markdown(self, harness):
        from superclaude.cli.sprint.diagnostics import (
            DiagnosticBundle,
            FailureCategory,
            ReportGenerator,
        )

        phase = harness.phases[0]
        pr = harness.make_phase_result(phase, exit_code=1)
        bundle = DiagnosticBundle(
            phase=phase,
            phase_result=pr,
            category=FailureCategory.ERROR,
            classification_evidence=["Test evidence"],
        )
        gen = ReportGenerator()
        report = gen.generate(bundle)
        assert "# Diagnostic Report" in report
