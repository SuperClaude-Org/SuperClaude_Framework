"""Tests for monitoring, diagnostics, and failure classification.

Covers:
- NDJSON event logger produces valid JSONL using signal vocabulary
- All 7 failure types are classifiable
- Timing capture records per-phase and per-step durations
- Markdown report generation produces readable summaries
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from superclaude.cli.cli_portify.models import FailureClassification
from superclaude.cli.cli_portify.monitor import (
    EventLogger,
    EventRecord,
    TimingCapture,
    classify_failure,
    generate_diagnostic_report,
)
from superclaude.cli.cli_portify.utils import (
    GATE_FAIL,
    GATE_PASS,
    SIGNAL_VOCABULARY,
    STEP_COMPLETE,
    STEP_ERROR,
    STEP_START,
    STEP_TIMEOUT,
)


class TestEventLogger:
    """NDJSON event logger produces valid JSONL using signal vocabulary."""

    def test_emit_produces_valid_json(self):
        logger = EventLogger()
        logger.emit(STEP_START, step="analyze-workflow", phase=2)
        output = logger.get_output()
        lines = output.strip().splitlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["event"] == STEP_START
        assert parsed["step"] == "analyze-workflow"
        assert parsed["phase"] == 2
        assert "ts" in parsed

    def test_multiple_events_produce_ndjson(self):
        logger = EventLogger()
        logger.emit(STEP_START, step="s1")
        logger.emit(STEP_COMPLETE, step="s1")
        logger.emit(STEP_START, step="s2")
        output = logger.get_output()
        lines = output.strip().splitlines()
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert "event" in parsed

    def test_events_list_preserved(self):
        logger = EventLogger()
        logger.emit(STEP_START, step="test")
        logger.emit(GATE_PASS, step="test")
        assert len(logger.events) == 2
        assert logger.events[0].event_type == STEP_START
        assert logger.events[1].event_type == GATE_PASS

    def test_extra_data_included(self):
        logger = EventLogger()
        logger.emit(STEP_ERROR, step="s1", error_code=42, message="fail")
        output = logger.get_output()
        parsed = json.loads(output.strip())
        assert parsed["error_code"] == 42
        assert parsed["message"] == "fail"

    def test_uses_signal_vocabulary_constants(self):
        """All signal vocabulary constants produce valid events."""
        logger = EventLogger()
        for sig in SIGNAL_VOCABULARY:
            logger.emit(sig, step="test")
        assert len(logger.events) == len(SIGNAL_VOCABULARY)


class TestEventRecord:
    """EventRecord serialization."""

    def test_to_dict(self):
        r = EventRecord(event_type="step_start", step="s1", phase=1, timestamp=123.0)
        d = r.to_dict()
        assert d["event"] == "step_start"
        assert d["step"] == "s1"
        assert d["phase"] == 1
        assert d["ts"] == 123.0

    def test_to_json_is_valid(self):
        r = EventRecord(event_type="test", timestamp=1.0)
        parsed = json.loads(r.to_json())
        assert parsed["event"] == "test"


class TestFailureClassification:
    """All 7 failure types are classifiable."""

    def test_timeout(self):
        result = classify_failure(exit_code=124, timed_out=True, stdout="")
        assert result == FailureClassification.TIMEOUT

    def test_missing_artifact(self, tmp_path):
        result = classify_failure(
            exit_code=0,
            timed_out=False,
            stdout="",
            artifact_path=tmp_path / "nonexistent.md",
        )
        assert result == FailureClassification.MISSING_ARTIFACT

    def test_malformed_frontmatter(self, tmp_path):
        artifact = tmp_path / "output.md"
        artifact.write_text("No frontmatter here\n# Just content")
        result = classify_failure(
            exit_code=0,
            timed_out=False,
            stdout="",
            artifact_path=artifact,
        )
        assert result == FailureClassification.MALFORMED_FRONTMATTER

    def test_gate_failure(self):
        result = classify_failure(
            exit_code=1,
            timed_out=False,
            stdout="output",
            gate_passed=False,
        )
        assert result == FailureClassification.GATE_FAILURE

    def test_user_rejection(self):
        result = classify_failure(
            exit_code=0,
            timed_out=False,
            stdout="",
            user_rejected=True,
        )
        assert result == FailureClassification.USER_REJECTION

    def test_budget_exhaustion(self):
        result = classify_failure(
            exit_code=0,
            timed_out=False,
            stdout="",
            budget_exhausted=True,
        )
        assert result == FailureClassification.BUDGET_EXHAUSTION

    def test_partial_artifact(self, tmp_path):
        artifact = tmp_path / "output.md"
        artifact.write_text("---\nstep: test\n---\n\n{{SC_PLACEHOLDER:missing}}")
        result = classify_failure(
            exit_code=0,
            timed_out=False,
            stdout="",
            artifact_path=artifact,
        )
        assert result == FailureClassification.PARTIAL_ARTIFACT

    def test_all_seven_types_covered(self):
        """Verify all 7 FailureClassification values exist."""
        expected = {
            "timeout", "missing_artifact", "malformed_frontmatter",
            "gate_failure", "user_rejection", "budget_exhaustion",
            "partial_artifact",
        }
        actual = {fc.value for fc in FailureClassification}
        assert actual == expected

    def test_priority_user_rejection_over_timeout(self):
        """user_rejection takes priority over timeout."""
        result = classify_failure(
            exit_code=124,
            timed_out=True,
            stdout="",
            user_rejected=True,
        )
        assert result == FailureClassification.USER_REJECTION

    def test_priority_budget_over_timeout(self):
        """budget_exhaustion takes priority over timeout."""
        result = classify_failure(
            exit_code=124,
            timed_out=True,
            stdout="",
            budget_exhausted=True,
        )
        assert result == FailureClassification.BUDGET_EXHAUSTION


class TestTimingCapture:
    """Timing capture records per-phase and per-step durations."""

    def test_step_timing(self):
        tc = TimingCapture()
        tc.start_step("analyze-workflow", phase=2)
        time.sleep(0.01)
        tc.end_step("analyze-workflow")
        st = tc.get_step_timing("analyze-workflow")
        assert st is not None
        assert st.duration_seconds > 0

    def test_phase_timing(self):
        tc = TimingCapture()
        tc.start_step("s1", phase=1)
        tc.end_step("s1")
        tc.start_step("s2", phase=1)
        tc.end_step("s2")
        pt = tc.get_phase_timing(1)
        assert pt is not None
        assert len(pt.step_timings) == 2

    def test_pipeline_total_duration(self):
        tc = TimingCapture()
        tc.start_pipeline()
        time.sleep(0.01)
        tc.end_pipeline()
        assert tc.total_duration > 0

    def test_step_timings_list(self):
        tc = TimingCapture()
        tc.start_step("a", phase=1)
        tc.end_step("a")
        tc.start_step("b", phase=2)
        tc.end_step("b")
        assert len(tc.step_timings) == 2

    def test_unknown_step_returns_none(self):
        tc = TimingCapture()
        assert tc.get_step_timing("nonexistent") is None


class TestDiagnosticReport:
    """Markdown report generation produces readable diagnostic summaries."""

    def test_report_contains_summary(self):
        tc = TimingCapture()
        tc.start_pipeline()
        tc.end_pipeline()

        report = generate_diagnostic_report(
            timing=tc,
            events=[],
            step_results=[
                {"step": "s1", "status": "pass", "duration": 1.0},
                {"step": "s2", "status": "fail", "duration": 2.0, "failure_type": "timeout"},
            ],
        )
        assert "# Portify Pipeline Diagnostic Report" in report
        assert "Steps executed: 2" in report
        assert "Passed: 1" in report
        assert "Failed: 1" in report

    def test_report_contains_step_table(self):
        tc = TimingCapture()
        tc.start_pipeline()
        tc.end_pipeline()

        report = generate_diagnostic_report(
            timing=tc,
            events=[],
            step_results=[
                {"step": "analyze", "status": "pass", "duration": 0.5},
            ],
        )
        assert "| analyze |" in report
        assert "| pass |" in report

    def test_report_contains_event_summary(self):
        logger = EventLogger()
        logger.emit(STEP_START, step="s1")
        logger.emit(STEP_COMPLETE, step="s1")
        logger.emit(STEP_START, step="s2")

        tc = TimingCapture()
        tc.start_pipeline()
        tc.end_pipeline()

        report = generate_diagnostic_report(
            timing=tc,
            events=logger.events,
            step_results=[],
        )
        assert "Event Summary" in report
        assert "step_start: 2" in report
        assert "step_complete: 1" in report

    def test_report_contains_phase_timings(self):
        tc = TimingCapture()
        tc.start_pipeline()
        tc.start_step("s1", phase=1)
        tc.end_step("s1")
        tc.end_pipeline()

        report = generate_diagnostic_report(
            timing=tc,
            events=[],
            step_results=[],
        )
        assert "Phase Timings" in report
        assert "Phase 1" in report


# ---------------------------------------------------------------------------
# T03.11 acceptance criteria: test_output_monitor
# ---------------------------------------------------------------------------


class TestOutputMonitor:
    """T03.11 — OutputMonitor tracks all 8 metrics and detects stalls.

    Validation command: uv run pytest tests/ -k "test_output_monitor"
    """

    def test_output_monitor_instantiates(self):
        from superclaude.cli.cli_portify.monitor import OutputMonitor
        mon = OutputMonitor()
        assert mon.state.output_bytes == 0
        assert mon.state.growth_rate_bps == 0.0

    def test_output_monitor_tracks_output_bytes(self):
        from superclaude.cli.cli_portify.monitor import OutputMonitor
        mon = OutputMonitor()
        mon.update(1024)
        assert mon.state.output_bytes == 1024

    def test_output_monitor_tracks_events(self):
        from superclaude.cli.cli_portify.monitor import OutputMonitor
        mon = OutputMonitor()
        mon.update(100)
        mon.update(200)
        assert mon.state.events == 2

    def test_output_monitor_tracks_line_count(self):
        from superclaude.cli.cli_portify.monitor import OutputMonitor
        mon = OutputMonitor()
        mon.update(100, new_lines=5)
        mon.update(200, new_lines=3)
        assert mon.state.line_count == 8

    def test_output_monitor_stall_detection_triggers_kill(self):
        from superclaude.cli.cli_portify.monitor import OutputMonitor
        killed = [False]

        def kill():
            killed[0] = True

        import time
        mon = OutputMonitor(
            stall_threshold_bps=1000.0,  # High threshold → immediate stall
            stall_timeout_seconds=0.0,   # Zero timeout → trigger immediately
            kill_fn=kill,
        )
        # First call establishes baseline
        mon.update(0)
        # Second call with no byte growth triggers stall → kill
        time.sleep(0.01)
        mon.update(0)
        assert killed[0] is True

    def test_output_monitor_has_all_eight_fields(self):
        from superclaude.cli.cli_portify.models import MonitorState
        fields = set(MonitorState.__dataclass_fields__.keys())
        expected = {
            "output_bytes", "growth_rate_bps", "stall_seconds", "events",
            "line_count", "convergence_iteration", "findings_count", "placeholder_count",
        }
        assert expected == fields
