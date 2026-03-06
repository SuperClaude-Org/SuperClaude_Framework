"""T09.04 — Performance NFR validation benchmarks.

Validates non-functional requirements under controlled conditions:
1. Gate evaluation: <50ms for 100KB output (p95 across 10 runs)
2. TurnLedger operations: O(1) constant time regardless of operation count

Acceptance criteria (D-0041):
- Gate evaluation completes in <50ms on 100KB synthetic output (p95 across 10 runs)
- TurnLedger debit/credit/available operations are O(1): time at 1000 ops within 2x of time at 10 ops
- Benchmarks are deterministic: pass on >=95% of runs
- `uv run pytest tests/ -k nfr_benchmark` exits 0

SC-007 validation: gate evaluation <50ms for 100KB output.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import GateCriteria, Step
from superclaude.cli.pipeline.trailing_gate import TrailingGateRunner
from superclaude.cli.sprint.models import TurnLedger


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_100kb_output(path: Path) -> None:
    """Generate a synthetic ~100KB file with valid YAML frontmatter."""
    lines = ["---", "title: benchmark output", "status: pass", "---"]
    while sum(len(line) + 1 for line in lines) < 100 * 1024:
        lines.append(f'{{"task": "T01.01", "event": "tool_use", "data": "x" * 60}}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def _strict_gate() -> GateCriteria:
    return GateCriteria(
        required_frontmatter_fields=["title", "status"],
        min_lines=10,
        enforcement_tier="STRICT",
    )


def _time_operation(fn, iterations: int = 100) -> float:
    """Time a function over N iterations, return total time in ms."""
    start = time.perf_counter()
    for _ in range(iterations):
        fn()
    return (time.perf_counter() - start) * 1000


# ===========================================================================
# NFR-1: Gate Evaluation Performance (<50ms for 100KB)
# ===========================================================================


class TestNFRGatePerformance:
    """Gate evaluation performance NFR: <50ms for 100KB output."""

    @pytest.mark.nfr_benchmark
    def test_gate_evaluation_100kb_under_50ms(self, tmp_path):
        """gate_passed() on 100KB synthetic output completes in <50ms (p95)."""
        output_file = tmp_path / "benchmark.md"
        _generate_100kb_output(output_file)

        # Verify file is approximately 100KB
        size_kb = output_file.stat().st_size / 1024
        assert size_kb >= 95, f"Generated file too small: {size_kb:.1f}KB"

        gate = _strict_gate()

        # Warm-up
        gate_passed(output_file, gate)

        # Benchmark: 10 iterations
        timings = []
        for _ in range(10):
            start = time.perf_counter()
            passed, reason = gate_passed(output_file, gate)
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)
            assert passed is True, f"Gate should pass: {reason}"

        p95 = sorted(timings)[int(len(timings) * 0.95)]
        assert p95 < 50.0, (
            f"p95 gate_passed() time {p95:.1f}ms exceeds 50ms NFR. "
            f"Timings: {[f'{t:.1f}' for t in timings]}"
        )

    @pytest.mark.nfr_benchmark
    def test_gate_evaluation_deterministic(self, tmp_path):
        """Gate benchmark passes on >=95% of runs."""
        output_file = tmp_path / "deterministic.md"
        _generate_100kb_output(output_file)
        gate = _strict_gate()

        pass_count = 0
        total = 20
        for _ in range(total):
            start = time.perf_counter()
            gate_passed(output_file, gate)
            elapsed_ms = (time.perf_counter() - start) * 1000
            if elapsed_ms < 50.0:
                pass_count += 1

        pass_rate = pass_count / total
        assert pass_rate >= 0.95, (
            f"Pass rate {pass_rate:.0%} below 95% threshold. "
            f"{pass_count}/{total} runs under 50ms."
        )


# ===========================================================================
# NFR-2: TurnLedger O(1) Operations
# ===========================================================================


class TestNFRTurnLedgerConstantTime:
    """TurnLedger debit/credit/available are O(1): constant time regardless
    of total operation count."""

    @pytest.mark.nfr_benchmark
    def test_debit_constant_time(self):
        """TurnLedger.debit() at 1000 ops is within 2x of time at 10 ops."""
        ledger_small = TurnLedger(initial_budget=100000)
        ledger_large = TurnLedger(initial_budget=100000)

        # Warm up
        for _ in range(10):
            ledger_small.debit(1)
            ledger_large.debit(1)

        # Reset
        ledger_small = TurnLedger(initial_budget=100000)
        ledger_large = TurnLedger(initial_budget=100000)

        # Time 10 debit operations
        time_10 = _time_operation(lambda: ledger_small.debit(1), iterations=10)

        # Time 1000 debit operations
        time_1000 = _time_operation(lambda: ledger_large.debit(1), iterations=1000)

        # O(1) check: per-operation time at 1000 should be within 2x of per-operation time at 10
        per_op_10 = time_10 / 10
        per_op_1000 = time_1000 / 1000

        # Guard against near-zero timings on fast hardware
        if per_op_10 > 0.0001:  # at least 0.1 microseconds
            ratio = per_op_1000 / per_op_10
            assert ratio < 2.0, (
                f"debit() not O(1): per-op at 1000={per_op_1000:.4f}ms, "
                f"per-op at 10={per_op_10:.4f}ms, ratio={ratio:.2f}"
            )

    @pytest.mark.nfr_benchmark
    def test_credit_constant_time(self):
        """TurnLedger.credit() at 1000 ops is within 2x of time at 10 ops."""
        ledger_small = TurnLedger(initial_budget=100000)
        ledger_large = TurnLedger(initial_budget=100000)

        # Warm up
        for _ in range(10):
            ledger_small.credit(1)
            ledger_large.credit(1)

        ledger_small = TurnLedger(initial_budget=100000)
        ledger_large = TurnLedger(initial_budget=100000)

        time_10 = _time_operation(lambda: ledger_small.credit(1), iterations=10)
        time_1000 = _time_operation(lambda: ledger_large.credit(1), iterations=1000)

        per_op_10 = time_10 / 10
        per_op_1000 = time_1000 / 1000

        if per_op_10 > 0.0001:
            ratio = per_op_1000 / per_op_10
            assert ratio < 2.0, (
                f"credit() not O(1): per-op at 1000={per_op_1000:.4f}ms, "
                f"per-op at 10={per_op_10:.4f}ms, ratio={ratio:.2f}"
            )

    @pytest.mark.nfr_benchmark
    def test_available_constant_time(self):
        """TurnLedger.available() at 1000 ops is within 2x of time at 10 ops."""
        ledger = TurnLedger(initial_budget=100000)

        # Pre-populate with varying operations
        for i in range(500):
            ledger.debit(1)
            ledger.credit(1)

        time_10 = _time_operation(ledger.available, iterations=10)
        time_1000 = _time_operation(ledger.available, iterations=1000)

        per_op_10 = time_10 / 10
        per_op_1000 = time_1000 / 1000

        if per_op_10 > 0.0001:
            ratio = per_op_1000 / per_op_10
            assert ratio < 2.0, (
                f"available() not O(1): per-op at 1000={per_op_1000:.4f}ms, "
                f"per-op at 10={per_op_10:.4f}ms, ratio={ratio:.2f}"
            )

    @pytest.mark.nfr_benchmark
    def test_can_launch_constant_time(self):
        """TurnLedger.can_launch() at 1000 ops is within 2x of time at 10 ops."""
        ledger = TurnLedger(initial_budget=100000)

        for i in range(500):
            ledger.debit(1)

        time_10 = _time_operation(ledger.can_launch, iterations=10)
        time_1000 = _time_operation(ledger.can_launch, iterations=1000)

        per_op_10 = time_10 / 10
        per_op_1000 = time_1000 / 1000

        if per_op_10 > 0.0001:
            ratio = per_op_1000 / per_op_10
            assert ratio < 2.0, (
                f"can_launch() not O(1): per-op at 1000={per_op_1000:.4f}ms, "
                f"per-op at 10={per_op_10:.4f}ms, ratio={ratio:.2f}"
            )

    @pytest.mark.nfr_benchmark
    def test_operation_timing_absolute(self):
        """Each TurnLedger operation completes in <1ms even after 10000 operations."""
        ledger = TurnLedger(initial_budget=1_000_000)

        # Execute 10000 operations to build up state
        for _ in range(10000):
            ledger.debit(1)

        # Each individual operation should be sub-millisecond
        ops = [
            ("debit", lambda: ledger.debit(1)),
            ("credit", lambda: ledger.credit(1)),
            ("available", ledger.available),
            ("can_launch", ledger.can_launch),
            ("can_remediate", ledger.can_remediate),
        ]

        for name, fn in ops:
            start = time.perf_counter()
            fn()
            elapsed_ms = (time.perf_counter() - start) * 1000
            assert elapsed_ms < 1.0, (
                f"TurnLedger.{name}() took {elapsed_ms:.3f}ms after 10000 ops"
            )
