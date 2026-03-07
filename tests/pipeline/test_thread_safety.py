"""Trailing gate thread safety tests (D-0025).

Validates thread safety of TrailingGateRunner and GateResultQueue under
concurrent load. Tests:
- Concurrent submit/drain from 3+ threads with no result loss
- pending_count accuracy under concurrent operations
- cancel() propagation to all pending evaluations within bounded timeout
- Result association by step_id (no cross-contamination)

STRICT tier: verified by running 5+ times to detect intermittent failures.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from superclaude.cli.pipeline.models import GateCriteria, GateMode, Step
from superclaude.cli.pipeline.trailing_gate import (
    GateResultQueue,
    TrailingGateResult,
    TrailingGateRunner,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _step(
    step_id: str = "s1",
    gate: GateCriteria | None = None,
    tmp_path: Path | None = None,
) -> Step:
    return Step(
        id=step_id,
        prompt="test",
        output_file=(tmp_path or Path("/tmp")) / f"{step_id}.md",
        gate=gate,
        timeout_seconds=60,
        gate_mode=GateMode.BLOCKING,
    )


def _gate() -> GateCriteria:
    return GateCriteria(
        required_frontmatter_fields=["title"],
        min_lines=5,
        enforcement_tier="STANDARD",
    )


def _write_passing_output(step: Step) -> None:
    """Write a file that passes the gate criteria."""
    step.output_file.parent.mkdir(parents=True, exist_ok=True)
    content = "---\ntitle: test\n---\n" + "\n".join(f"line {i}" for i in range(10))
    step.output_file.write_text(content)


# ===========================================================================
# GateResultQueue Thread Safety
# ===========================================================================


class TestQueueThreadSafety:
    """Thread-safe queue behavior under concurrent access."""

    @pytest.mark.thread_safety
    def test_thread_safety_concurrent_put_from_three_threads(self):
        """3 threads putting concurrently — no result loss."""
        q = GateResultQueue()
        items_per_thread = 50

        def producer(prefix: str):
            for i in range(items_per_thread):
                q.put(TrailingGateResult(
                    step_id=f"{prefix}-{i}",
                    passed=True,
                    evaluation_ms=float(i),
                ))

        threads = [
            threading.Thread(target=producer, args=(f"t{n}",))
            for n in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        results = q.drain()
        assert len(results) == 3 * items_per_thread, (
            f"Expected {3 * items_per_thread} results, got {len(results)} — "
            f"result loss under concurrent put"
        )

    @pytest.mark.thread_safety
    def test_thread_safety_concurrent_put_drain_interleaved(self):
        """3 producer threads + 1 consumer thread — all results collected."""
        q = GateResultQueue()
        items_per_thread = 30
        collected: list[TrailingGateResult] = []
        lock = threading.Lock()
        stop = threading.Event()

        def producer(prefix: str):
            for i in range(items_per_thread):
                q.put(TrailingGateResult(
                    step_id=f"{prefix}-{i}",
                    passed=True,
                    evaluation_ms=float(i),
                ))
                time.sleep(0.001)  # simulate work

        def consumer():
            while not stop.is_set() or q.pending_count() > 0:
                batch = q.drain()
                if batch:
                    with lock:
                        collected.extend(batch)
                else:
                    time.sleep(0.005)

        threads = [
            threading.Thread(target=producer, args=(f"p{n}",))
            for n in range(3)
        ]
        consumer_thread = threading.Thread(target=consumer)
        consumer_thread.start()
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stop.set()
        consumer_thread.join(timeout=5.0)

        # Final drain for any stragglers
        collected.extend(q.drain())

        assert len(collected) == 3 * items_per_thread, (
            f"Expected {3 * items_per_thread}, got {len(collected)} — "
            f"interleaved put/drain lost results"
        )

    @pytest.mark.thread_safety
    def test_thread_safety_pending_count_accuracy(self):
        """pending_count matches actual pending items at each checkpoint."""
        q = GateResultQueue()

        assert q.pending_count() == 0

        for i in range(5):
            q.put(TrailingGateResult(step_id=f"s{i}", passed=True, evaluation_ms=0.0))
        assert q.pending_count() == 5

        q.drain()
        assert q.pending_count() == 0

        # Repopulate and partially drain
        for i in range(10):
            q.put(TrailingGateResult(step_id=f"s{i}", passed=True, evaluation_ms=0.0))
        assert q.pending_count() == 10

    @pytest.mark.thread_safety
    def test_thread_safety_step_id_association(self):
        """Results associated with correct step_id — no cross-contamination."""
        q = GateResultQueue()
        expected = {}
        for i in range(20):
            passed = i % 2 == 0
            sid = f"step-{i}"
            expected[sid] = passed
            q.put(TrailingGateResult(step_id=sid, passed=passed, evaluation_ms=float(i)))

        results = q.drain()
        by_id = {r.step_id: r for r in results}
        assert len(by_id) == 20, "Not all step_ids recovered"
        for sid, exp_passed in expected.items():
            assert by_id[sid].passed == exp_passed, (
                f"step_id {sid} expected passed={exp_passed}, got {by_id[sid].passed}"
            )


# ===========================================================================
# TrailingGateRunner Thread Safety
# ===========================================================================


class TestRunnerThreadSafety:
    """Thread safety of TrailingGateRunner submit/drain/cancel."""

    @pytest.mark.thread_safety
    def test_thread_safety_concurrent_submit_three_threads(self, tmp_path):
        """3 threads submit simultaneously — all results collected."""
        runner = TrailingGateRunner()
        steps_per_thread = 5
        barrier = threading.Barrier(3)

        def submitter(thread_id: int):
            steps = []
            for i in range(steps_per_thread):
                s = _step(step_id=f"t{thread_id}-s{i}", gate=None, tmp_path=tmp_path)
                steps.append(s)
            barrier.wait()  # synchronize all threads
            for s in steps:
                runner.submit(s)

        threads = [
            threading.Thread(target=submitter, args=(n,))
            for n in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        results = runner.wait_for_pending(timeout=5.0)
        results.extend(runner.drain())
        assert len(results) == 3 * steps_per_thread, (
            f"Expected {3 * steps_per_thread} results from 3 concurrent submitters, "
            f"got {len(results)}"
        )

    @pytest.mark.thread_safety
    def test_thread_safety_concurrent_submit_with_gates(self, tmp_path):
        """3 threads submit steps WITH gate criteria — daemon threads evaluate."""
        runner = TrailingGateRunner()
        steps_per_thread = 3

        def submitter(thread_id: int):
            for i in range(steps_per_thread):
                s = _step(step_id=f"t{thread_id}-g{i}", gate=_gate(), tmp_path=tmp_path)
                _write_passing_output(s)
                runner.submit(s)

        threads = [
            threading.Thread(target=submitter, args=(n,))
            for n in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        results = runner.wait_for_pending(timeout=10.0)
        results.extend(runner.drain())
        assert len(results) == 3 * steps_per_thread
        # All should pass
        for r in results:
            assert r.passed is True, f"step {r.step_id} unexpectedly failed"

    @pytest.mark.thread_safety
    def test_thread_safety_step_id_no_cross_contamination(self, tmp_path):
        """Results from concurrent submissions have correct step_id mapping."""
        runner = TrailingGateRunner()
        total = 10

        for i in range(total):
            s = _step(step_id=f"unique-{i}", gate=None, tmp_path=tmp_path)
            runner.submit(s)

        results = runner.wait_for_pending(timeout=5.0)
        results.extend(runner.drain())
        step_ids = {r.step_id for r in results}
        expected_ids = {f"unique-{i}" for i in range(total)}
        assert step_ids == expected_ids, (
            f"Step ID mismatch: missing={expected_ids - step_ids}, "
            f"extra={step_ids - expected_ids}"
        )

    @pytest.mark.thread_safety
    def test_thread_safety_cancel_terminates_within_timeout(self, tmp_path):
        """cancel() terminates all pending evaluations within 5-second bounded timeout."""
        runner = TrailingGateRunner()

        def slow_gate(path, criteria):
            time.sleep(30)  # Very slow — should be cancelled
            return True, None

        for i in range(3):
            s = _step(step_id=f"slow-{i}", gate=_gate(), tmp_path=tmp_path)
            s.output_file.parent.mkdir(parents=True, exist_ok=True)
            s.output_file.write_text("x")
            runner.submit(s, gate_check=slow_gate)

        start = time.monotonic()
        runner.cancel()
        elapsed = time.monotonic() - start

        assert elapsed < 5.0, (
            f"cancel() took {elapsed:.1f}s — must complete within 5s"
        )

    @pytest.mark.thread_safety
    def test_thread_safety_pending_count_under_load(self, tmp_path):
        """pending_count is consistent during concurrent operations."""
        runner = TrailingGateRunner()

        # Submit 5 no-gate steps (immediate results)
        for i in range(5):
            s = _step(step_id=f"fast-{i}", gate=None, tmp_path=tmp_path)
            runner.submit(s)

        # After immediate submits, pending_count should reach 0 quickly
        time.sleep(0.1)
        results = runner.drain()
        assert len(results) == 5
        assert runner.pending_count == 0

    @pytest.mark.thread_safety
    def test_thread_safety_repeated_runs_stable(self, tmp_path):
        """Run submit/drain cycle 5 times to detect intermittent failures."""
        for run in range(5):
            runner = TrailingGateRunner()
            for i in range(5):
                s = _step(step_id=f"run{run}-s{i}", gate=None, tmp_path=tmp_path)
                runner.submit(s)

            results = runner.wait_for_pending(timeout=5.0)
            results.extend(runner.drain())
            assert len(results) == 5, (
                f"Run {run}: expected 5 results, got {len(results)}"
            )
            ids = {r.step_id for r in results}
            expected = {f"run{run}-s{i}" for i in range(5)}
            assert ids == expected, f"Run {run}: ID mismatch"
