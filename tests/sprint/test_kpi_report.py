"""Tests for KPI report generation from gate and remediation metrics."""

from pathlib import Path

from superclaude.cli.pipeline.trailing_gate import (
    DeferredRemediationLog,
    TrailingGateResult,
)
from superclaude.cli.sprint.kpi import GateKPIReport, build_kpi_report


def _gate(step_id: str, passed: bool, ms: float) -> TrailingGateResult:
    return TrailingGateResult(
        step_id=step_id,
        passed=passed,
        evaluation_ms=ms,
        failure_reason=None if passed else "test failure",
    )


class TestGateKPIReportProperties:
    """Verify computed properties of the KPI report."""

    def test_empty_report(self):
        r = GateKPIReport()
        assert r.gate_pass_rate == 0.0
        assert r.gate_fail_rate == 0.0
        assert r.remediation_frequency == 0.0
        assert r.conflict_review_rate == 0.0
        assert r.p50_latency_ms == 0.0
        assert r.p95_latency_ms == 0.0

    def test_pass_rate(self):
        r = GateKPIReport(total_gates_evaluated=4, gates_passed=3, gates_failed=1)
        assert r.gate_pass_rate == 0.75
        assert r.gate_fail_rate == 0.25

    def test_remediation_frequency(self):
        r = GateKPIReport(total_gates_evaluated=10, total_remediations=3)
        assert abs(r.remediation_frequency - 0.3) < 0.001

    def test_conflict_review_rate(self):
        r = GateKPIReport(total_conflict_reviews=5, conflicts_detected=2)
        assert abs(r.conflict_review_rate - 0.4) < 0.001

    def test_latency_p50_odd(self):
        r = GateKPIReport(gate_latency_ms=[10.0, 20.0, 30.0, 40.0, 50.0])
        assert r.p50_latency_ms == 30.0

    def test_latency_p50_even(self):
        r = GateKPIReport(gate_latency_ms=[10.0, 20.0, 30.0, 40.0])
        assert r.p50_latency_ms == 25.0

    def test_latency_p95(self):
        r = GateKPIReport(gate_latency_ms=[float(i) for i in range(1, 101)])
        assert r.p95_latency_ms >= 95.0


class TestBuildKPIReport:
    """Verify build_kpi_report aggregates metrics correctly."""

    def test_from_gate_results_all_pass(self):
        results = [_gate(f"T{i}", True, 10.0 * i) for i in range(1, 6)]
        report = build_kpi_report(results)
        assert report.total_gates_evaluated == 5
        assert report.gates_passed == 5
        assert report.gates_failed == 0
        assert report.gate_pass_rate == 1.0

    def test_from_gate_results_mixed(self):
        results = [
            _gate("T1", True, 10.0),
            _gate("T2", False, 20.0),
            _gate("T3", True, 15.0),
            _gate("T4", False, 30.0),
        ]
        report = build_kpi_report(results)
        assert report.total_gates_evaluated == 4
        assert report.gates_passed == 2
        assert report.gates_failed == 2
        assert report.gate_pass_rate == 0.5

    def test_latency_from_gate_results(self):
        results = [
            _gate("T1", True, 10.0),
            _gate("T2", True, 20.0),
            _gate("T3", True, 30.0),
        ]
        report = build_kpi_report(results)
        assert report.p50_latency_ms == 20.0

    def test_with_remediation_log(self):
        results = [_gate("T1", False, 10.0), _gate("T2", False, 20.0)]
        log = DeferredRemediationLog()
        log.append(results[0])
        log.append(results[1])
        log.mark_remediated("T1")

        report = build_kpi_report(results, remediation_log=log)
        assert report.total_remediations == 2
        assert report.remediations_resolved == 1
        assert report.remediations_pending == 1

    def test_with_conflict_reviews(self):
        report = build_kpi_report(
            gate_results=[],
            conflict_reviews_total=10,
            conflicts_detected=3,
        )
        assert report.total_conflict_reviews == 10
        assert report.conflicts_detected == 3
        assert abs(report.conflict_review_rate - 0.3) < 0.001

    def test_empty_inputs(self):
        report = build_kpi_report(gate_results=[])
        assert report.total_gates_evaluated == 0
        assert report.gate_pass_rate == 0.0

    def test_no_remediation_log(self):
        results = [_gate("T1", True, 10.0)]
        report = build_kpi_report(results)
        assert report.total_remediations == 0
        assert report.remediations_resolved == 0
        assert report.remediations_pending == 0


class TestKPIReportFormat:
    """KPI report produces human-readable formatted output."""

    def test_format_report_contains_sections(self):
        report = build_kpi_report(
            gate_results=[_gate("T1", True, 15.0), _gate("T2", False, 25.0)],
            conflict_reviews_total=3,
            conflicts_detected=1,
        )
        text = report.format_report()
        assert "Gate Evaluation" in text
        assert "Remediation" in text
        assert "Conflict Review" in text
        assert "p50" in text
        assert "p95" in text

    def test_format_report_accurate_values(self):
        report = GateKPIReport(
            total_gates_evaluated=10,
            gates_passed=8,
            gates_failed=2,
            gate_latency_ms=[10.0, 20.0, 30.0],
            total_remediations=2,
            remediations_resolved=1,
            remediations_pending=1,
            total_conflict_reviews=5,
            conflicts_detected=2,
        )
        text = report.format_report()
        assert "80.0%" in text  # pass rate
        assert "20.0ms" in text  # p50 latency
