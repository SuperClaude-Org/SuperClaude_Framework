"""Gate performance NFR benchmark tests (D-0026).

Validates that gate_passed() meets the <50ms performance NFR for 100KB output.
Also verifies TrailingGateResult.evaluation_ms is populated with actual timing.

NFR from roadmap Gap 7: gate evaluation <50ms for 100KB output.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from superclaude.cli.pipeline.gates import gate_passed
from superclaude.cli.pipeline.models import GateCriteria, GateMode, Step
from superclaude.cli.pipeline.trailing_gate import (
    TrailingGateResult,
    TrailingGateRunner,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_100kb_output(path: Path) -> None:
    """Generate a synthetic ~100KB NDJSON-like output file with valid frontmatter."""
    lines = ["---", "title: benchmark output", "status: pass", "---"]
    # Each line ~80 chars; need ~1250 lines for 100KB
    while sum(len(line) + 1 for line in lines) < 100 * 1024:
        lines.append(f'{{"task": "T01.01", "event": "tool_use", "data": "x" * 60}}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def _step(
    step_id: str = "perf-1",
    gate: GateCriteria | None = None,
    tmp_path: Path | None = None,
) -> Step:
    return Step(
        id=step_id,
        prompt="benchmark",
        output_file=(tmp_path or Path("/tmp")) / f"{step_id}.md",
        gate=gate,
        timeout_seconds=60,
        gate_mode=GateMode.BLOCKING,
    )


def _strict_gate() -> GateCriteria:
    """STRICT tier gate with frontmatter and line checks."""
    return GateCriteria(
        required_frontmatter_fields=["title", "status"],
        min_lines=10,
        enforcement_tier="STRICT",
    )


# ===========================================================================
# Gate Performance NFR
# ===========================================================================


class TestGatePerformanceNFR:
    """Performance benchmark: gate_passed() < 50ms for 100KB output."""

    @pytest.mark.gate_performance
    def test_gate_performance_100kb_under_50ms(self, tmp_path):
        """gate_passed() on 100KB synthetic output completes in <50ms."""
        output_file = tmp_path / "benchmark.md"
        _generate_100kb_output(output_file)

        # Verify file is ~100KB
        size_kb = output_file.stat().st_size / 1024
        assert size_kb >= 95, f"Generated file too small: {size_kb:.1f}KB"

        gate = _strict_gate()

        # Warm-up run
        gate_passed(output_file, gate)

        # Timed benchmark — run 10 iterations, take median
        timings = []
        for _ in range(10):
            start = time.perf_counter()
            passed, reason = gate_passed(output_file, gate)
            elapsed_ms = (time.perf_counter() - start) * 1000
            timings.append(elapsed_ms)
            assert passed is True, f"Gate should pass: {reason}"

        median = sorted(timings)[len(timings) // 2]
        p95 = sorted(timings)[int(len(timings) * 0.95)]

        assert median < 50.0, (
            f"Median gate_passed() time {median:.1f}ms exceeds 50ms NFR. "
            f"Timings: {[f'{t:.1f}' for t in timings]}"
        )

    @pytest.mark.gate_performance
    def test_gate_performance_evaluation_ms_populated(self, tmp_path):
        """TrailingGateResult.evaluation_ms is populated with actual duration."""
        step = _step(gate=_strict_gate(), tmp_path=tmp_path)
        _generate_100kb_output(step.output_file)

        runner = TrailingGateRunner()
        runner.submit(step)
        results = runner.wait_for_pending(timeout=10.0)
        results.extend(runner.drain())

        assert len(results) == 1
        r = results[0]
        assert r.passed is True
        assert r.evaluation_ms > 0.0, (
            f"evaluation_ms should be populated with actual timing, "
            f"got {r.evaluation_ms}"
        )

    @pytest.mark.gate_performance
    def test_gate_performance_deterministic(self, tmp_path):
        """Benchmark is deterministic: passes on ≥95% of runs."""
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

    @pytest.mark.gate_performance
    def test_gate_performance_no_gate_instant(self, tmp_path):
        """No-gate path produces evaluation_ms=0.0 (instant pass)."""
        step = _step(gate=None, tmp_path=tmp_path)
        runner = TrailingGateRunner()
        runner.submit(step)
        results = runner.drain()

        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].evaluation_ms == 0.0
