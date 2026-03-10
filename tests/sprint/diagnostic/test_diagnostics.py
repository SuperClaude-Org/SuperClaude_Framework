"""Tests for Phase 5 — DiagnosticBundle, DiagnosticCollector, FailureClassifier, ReportGenerator."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from superclaude.cli.sprint.diagnostics import (
    DiagnosticBundle,
    DiagnosticCollector,
    FailureCategory,
    FailureClassifier,
    ReportGenerator,
)
from superclaude.cli.sprint.models import (
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(tmp_path: Path, debug: bool = True, **kwargs) -> SprintConfig:
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


def _make_phase_result(
    phase: Phase,
    status: PhaseStatus = PhaseStatus.ERROR,
    exit_code: int = 1,
) -> PhaseResult:
    now = datetime.now(timezone.utc)
    return PhaseResult(
        phase=phase,
        status=status,
        exit_code=exit_code,
        started_at=now,
        finished_at=now,
        output_bytes=1024,
    )


# ---------------------------------------------------------------------------
# T05.01 — DiagnosticBundle
# ---------------------------------------------------------------------------


class TestDiagnosticBundle:
    def test_default_category_unknown(self):
        phase = Phase(number=1, file=Path("test.md"))
        pr = _make_phase_result(phase)
        bundle = DiagnosticBundle(phase=phase, phase_result=pr)
        assert bundle.category == FailureCategory.UNKNOWN

    def test_summary_format(self):
        phase = Phase(number=2, file=Path("test.md"))
        pr = _make_phase_result(phase, exit_code=124, status=PhaseStatus.TIMEOUT)
        bundle = DiagnosticBundle(
            phase=phase,
            phase_result=pr,
            category=FailureCategory.TIMEOUT,
        )
        s = bundle.summary
        assert "Phase 2" in s
        assert "timeout" in s


# ---------------------------------------------------------------------------
# T05.02 — DiagnosticCollector
# ---------------------------------------------------------------------------


class TestDiagnosticCollector:
    def test_collect_captures_monitor_state(self, tmp_path):
        config = _make_config(tmp_path, debug=False)
        phase = config.phases[0]
        pr = _make_phase_result(phase)
        ms = MonitorState(
            output_bytes=2048,
            events_received=15,
            stall_seconds=5.0,
            last_task_id="T01.03",
            last_tool_used="Edit",
            files_changed=3,
        )

        collector = DiagnosticCollector(config)
        bundle = collector.collect(phase, pr, ms)

        assert bundle.monitor_state_snapshot["output_bytes"] == 2048
        assert bundle.monitor_state_snapshot["events_received"] == 15
        assert bundle.monitor_state_snapshot["last_task_id"] == "T01.03"
        assert bundle.stall_duration == 5.0

    def test_collect_reads_output_tail(self, tmp_path):
        config = _make_config(tmp_path, debug=False)
        phase = config.phases[0]

        # Create output file
        output_file = config.output_file(phase)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("line1\nline2\nline3\n")

        pr = _make_phase_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(config)
        bundle = collector.collect(phase, pr, ms)
        assert "line3" in bundle.output_tail

    def test_collect_reads_stderr_tail(self, tmp_path):
        config = _make_config(tmp_path, debug=False)
        phase = config.phases[0]

        error_file = config.error_file(phase)
        error_file.parent.mkdir(parents=True, exist_ok=True)
        error_file.write_text("error: something failed\n")

        pr = _make_phase_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(config)
        bundle = collector.collect(phase, pr, ms)
        assert "something failed" in bundle.stderr_tail

    def test_collect_reads_debug_log_entries(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        phase = config.phases[0]

        # Create debug log with phase entries
        debug_log_path = config.debug_log_path
        debug_log_path.parent.mkdir(parents=True, exist_ok=True)
        debug_log_path.write_text(
            "# debug-log-version: 1.0\n"
            "2026-01-01T00:00:00.000 DEBUG    [executor] PHASE_BEGIN phase=1 file=test.md\n"
            "2026-01-01T00:00:01.000 DEBUG    [executor] poll_tick phase=1 pid=1234\n"
            "2026-01-01T00:00:02.000 DEBUG    [executor] PHASE_END phase=1 exit_code=1\n"
        )

        pr = _make_phase_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(config)
        bundle = collector.collect(phase, pr, ms)
        assert len(bundle.debug_log_entries) == 3
        assert "PHASE_BEGIN" in bundle.debug_log_entries[0]

    def test_collect_detects_watchdog(self, tmp_path):
        config = _make_config(tmp_path, debug=True)
        phase = config.phases[0]

        debug_log_path = config.debug_log_path
        debug_log_path.parent.mkdir(parents=True, exist_ok=True)
        debug_log_path.write_text(
            "# debug-log-version: 1.0\n"
            "2026-01-01T00:00:00.000 DEBUG    [executor] PHASE_BEGIN phase=1 file=test.md\n"
            "2026-01-01T00:01:00.000 DEBUG    [executor] watchdog_triggered phase=1 action=warn\n"
            "2026-01-01T00:02:00.000 DEBUG    [executor] PHASE_END phase=1 exit_code=1\n"
        )

        pr = _make_phase_result(phase)
        ms = MonitorState()

        collector = DiagnosticCollector(config)
        bundle = collector.collect(phase, pr, ms)
        assert bundle.watchdog_triggered is True


# ---------------------------------------------------------------------------
# T05.03 — FailureClassifier
# ---------------------------------------------------------------------------


class TestFailureClassifier:
    def _make_bundle(self, **kwargs):
        phase = Phase(number=1, file=Path("test.md"))
        pr = _make_phase_result(phase, **{k: v for k, v in kwargs.items() if k in ("status", "exit_code")})
        bundle = DiagnosticBundle(phase=phase, phase_result=pr)
        for k, v in kwargs.items():
            if hasattr(bundle, k) and k not in ("status", "exit_code"):
                setattr(bundle, k, v)
        return bundle

    def test_classify_stall_by_watchdog(self):
        bundle = self._make_bundle(watchdog_triggered=True)
        classifier = FailureClassifier()
        assert classifier.classify(bundle) == FailureCategory.STALL

    def test_classify_stall_by_high_duration(self):
        bundle = self._make_bundle(stall_duration=150.0)
        classifier = FailureClassifier()
        assert classifier.classify(bundle) == FailureCategory.STALL

    def test_classify_timeout(self):
        bundle = self._make_bundle(exit_code=124, status=PhaseStatus.TIMEOUT)
        classifier = FailureClassifier()
        assert classifier.classify(bundle) == FailureCategory.TIMEOUT

    def test_classify_crash(self):
        bundle = self._make_bundle(exit_code=1, stall_duration=5.0, status=PhaseStatus.ERROR)
        classifier = FailureClassifier()
        assert classifier.classify(bundle) == FailureCategory.CRASH

    def test_classify_error_halt(self):
        bundle = self._make_bundle(exit_code=0, stall_duration=5.0, status=PhaseStatus.HALT)
        classifier = FailureClassifier()
        assert classifier.classify(bundle) == FailureCategory.ERROR

    def test_classify_unknown_when_no_evidence(self):
        phase = Phase(number=1, file=Path("test.md"))
        pr = PhaseResult(
            phase=phase,
            status=PhaseStatus.PASS,
            exit_code=0,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        bundle = DiagnosticBundle(phase=phase, phase_result=pr)
        classifier = FailureClassifier()
        assert classifier.classify(bundle) == FailureCategory.UNKNOWN

    def test_evidence_populated(self):
        bundle = self._make_bundle(watchdog_triggered=True)
        classifier = FailureClassifier()
        classifier.classify(bundle)
        assert len(bundle.classification_evidence) > 0


# ---------------------------------------------------------------------------
# T05.04 — ReportGenerator
# ---------------------------------------------------------------------------


class TestReportGenerator:
    def test_generate_contains_sections(self):
        phase = Phase(number=1, file=Path("test.md"))
        pr = _make_phase_result(phase)
        bundle = DiagnosticBundle(
            phase=phase,
            phase_result=pr,
            category=FailureCategory.STALL,
            classification_evidence=["Watchdog triggered"],
            monitor_state_snapshot={"output_bytes": 2048},
            last_events=["event1", "event2"],
            output_tail="last output line",
            stderr_tail="error line",
        )

        gen = ReportGenerator()
        report = gen.generate(bundle)

        assert "# Diagnostic Report" in report
        assert "## Summary" in report
        assert "stall" in report
        assert "## Evidence" in report
        assert "Watchdog triggered" in report
        assert "## Monitor State" in report
        assert "## Last Debug Events" in report
        assert "## Output Tail" in report
        assert "## Stderr Tail" in report

    def test_write_creates_file(self, tmp_path):
        phase = Phase(number=1, file=Path("test.md"))
        pr = _make_phase_result(phase)
        bundle = DiagnosticBundle(
            phase=phase,
            phase_result=pr,
            category=FailureCategory.ERROR,
            classification_evidence=["Process error"],
        )

        gen = ReportGenerator()
        out_path = tmp_path / "results" / "phase-1-diagnostic.md"
        gen.write(bundle, out_path)

        assert out_path.exists()
        content = out_path.read_text()
        assert "# Diagnostic Report" in content
        assert "error" in content
