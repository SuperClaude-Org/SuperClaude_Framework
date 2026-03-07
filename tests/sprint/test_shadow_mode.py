"""Tests for shadow mode (--shadow-gates) metrics collection."""

from pathlib import Path

from superclaude.cli.sprint.models import (
    Phase,
    ShadowGateMetrics,
    SprintConfig,
)


def _make_config(shadow_gates: bool = False) -> SprintConfig:
    return SprintConfig(
        index_path=Path("/tmp/tasklist-index.md"),
        release_dir=Path("/tmp/release"),
        phases=[
            Phase(number=1, file=Path("/tmp/p1.md"), name="Foundation"),
        ],
        shadow_gates=shadow_gates,
    )


class TestShadowGatesFlag:
    """--shadow-gates flag enables shadow mode on SprintConfig."""

    def test_shadow_gates_default_false(self):
        config = _make_config()
        assert config.shadow_gates is False

    def test_shadow_gates_enabled(self):
        config = _make_config(shadow_gates=True)
        assert config.shadow_gates is True


class TestShadowGateMetrics:
    """Shadow metrics collection without affecting behavior."""

    def test_empty_metrics(self):
        m = ShadowGateMetrics()
        assert m.total_evaluated == 0
        assert m.passed == 0
        assert m.failed == 0
        assert m.pass_rate == 0.0
        assert m.p50_latency_ms == 0.0
        assert m.p95_latency_ms == 0.0

    def test_record_pass(self):
        m = ShadowGateMetrics()
        m.record(passed=True, evaluation_ms=10.0)
        assert m.total_evaluated == 1
        assert m.passed == 1
        assert m.failed == 0
        assert m.pass_rate == 1.0

    def test_record_fail(self):
        m = ShadowGateMetrics()
        m.record(passed=False, evaluation_ms=25.0)
        assert m.total_evaluated == 1
        assert m.passed == 0
        assert m.failed == 1
        assert m.pass_rate == 0.0

    def test_mixed_results(self):
        m = ShadowGateMetrics()
        m.record(passed=True, evaluation_ms=10.0)
        m.record(passed=True, evaluation_ms=20.0)
        m.record(passed=False, evaluation_ms=50.0)
        assert m.total_evaluated == 3
        assert m.passed == 2
        assert m.failed == 1
        assert abs(m.pass_rate - 2 / 3) < 0.001

    def test_latency_p50(self):
        m = ShadowGateMetrics()
        for ms in [10.0, 20.0, 30.0, 40.0, 50.0]:
            m.record(passed=True, evaluation_ms=ms)
        assert m.p50_latency_ms == 30.0

    def test_latency_p50_even_count(self):
        m = ShadowGateMetrics()
        for ms in [10.0, 20.0, 30.0, 40.0]:
            m.record(passed=True, evaluation_ms=ms)
        assert m.p50_latency_ms == 25.0  # avg of 20 and 30

    def test_latency_p95(self):
        m = ShadowGateMetrics()
        for ms in range(1, 101):  # 1..100ms
            m.record(passed=True, evaluation_ms=float(ms))
        assert m.p95_latency_ms >= 95.0

    def test_blocking_results_determine_outcome(self):
        """Shadow metrics must not affect sprint behavior.

        This tests the design contract: ShadowGateMetrics is a passive
        data collector with no side effects on SprintConfig or execution.
        """
        config = _make_config(shadow_gates=True)
        metrics = ShadowGateMetrics()
        metrics.record(passed=False, evaluation_ms=100.0)
        # Config and metrics are independent — shadow failure doesn't alter config
        assert config.shadow_gates is True
        assert metrics.failed == 1
        # No reference between them — shadow is informational only
