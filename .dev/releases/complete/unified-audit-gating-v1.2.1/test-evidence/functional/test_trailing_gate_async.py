"""Functional test: TrailingGateRunner under concurrent access.

Exercises the real TrailingGateRunner, GateResultQueue, and
DeferredRemediationLog classes from src/superclaude/cli/pipeline/trailing_gate.py.

Verifies:
  1. Thread-safe submit/drain under 3+ concurrent submitter threads
  2. pending_count accuracy across the submission lifecycle
  3. Daemon thread cleanup behavior (threads marked daemon=True, abandoned on exit)
  4. DeferredRemediationLog captures failures correctly
  5. wait_for_pending returns all results within timeout
"""

from __future__ import annotations

import tempfile
import threading
import time
from pathlib import Path
from typing import Callable

import pytest

from superclaude.cli.pipeline.models import GateCriteria, GateMode, Step
from superclaude.cli.pipeline.trailing_gate import (
    DeferredRemediationLog,
    GateResultQueue,
    TrailingGateResult,
    TrailingGateRunner,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_step(
    step_id: str,
    gate: GateCriteria | None = None,
    output_file: Path | None = None,
) -> Step:
    """Build a minimal Step for testing."""
    return Step(
        id=step_id,
        prompt=f"Test prompt for {step_id}",
        output_file=output_file or Path("/tmp/fake_output.md"),
        gate=gate,
        timeout_seconds=30,
    )


def _slow_gate_check(
    delay: float = 0.05,
    passed: bool = True,
    reason: str | None = None,
) -> Callable[[Path, GateCriteria], tuple[bool, str | None]]:
    """Return a gate_check callable that sleeps before returning."""

    def _check(output_file: Path, criteria: GateCriteria) -> tuple[bool, str | None]:
        time.sleep(delay)
        return passed, reason

    return _check


def _make_gate_criteria() -> GateCriteria:
    return GateCriteria(
        required_frontmatter_fields=["title"],
        min_lines=1,
        enforcement_tier="STANDARD",
    )


# ---------------------------------------------------------------------------
# Test: GateResultQueue thread safety
# ---------------------------------------------------------------------------


class TestGateResultQueueThreadSafety:
    """Verify GateResultQueue under concurrent put/drain from multiple threads."""

    def test_concurrent_put_then_drain_collects_all(self):
        """3+ threads concurrently put results; drain returns every result."""
        queue = GateResultQueue()
        num_threads = 5
        results_per_thread = 20
        total_expected = num_threads * results_per_thread
        barrier = threading.Barrier(num_threads)

        def _producer(thread_idx: int) -> None:
            barrier.wait()  # all threads start simultaneously
            for i in range(results_per_thread):
                queue.put(
                    TrailingGateResult(
                        step_id=f"t{thread_idx}-s{i}",
                        passed=True,
                        evaluation_ms=1.0,
                    )
                )

        threads = [
            threading.Thread(target=_producer, args=(idx,))
            for idx in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        drained = queue.drain()
        assert len(drained) == total_expected, (
            f"Expected {total_expected} results from {num_threads} threads, got {len(drained)}"
        )

    def test_interleaved_put_and_drain(self):
        """Concurrent put and drain do not lose results or raise exceptions."""
        queue = GateResultQueue()
        total_puts = 100
        collected: list[TrailingGateResult] = []
        lock = threading.Lock()
        stop_event = threading.Event()

        def _producer() -> None:
            for i in range(total_puts):
                queue.put(
                    TrailingGateResult(
                        step_id=f"step-{i}",
                        passed=True,
                        evaluation_ms=0.5,
                    )
                )
                time.sleep(0.001)

        def _consumer() -> None:
            while not stop_event.is_set():
                batch = queue.drain()
                if batch:
                    with lock:
                        collected.extend(batch)
                time.sleep(0.005)

        producer = threading.Thread(target=_producer)
        consumer = threading.Thread(target=_consumer)
        producer.start()
        consumer.start()
        producer.join(timeout=10)
        # Give consumer time to catch last items
        time.sleep(0.1)
        stop_event.set()
        consumer.join(timeout=5)

        # Drain any stragglers
        stragglers = queue.drain()
        collected.extend(stragglers)

        assert len(collected) == total_puts, (
            f"Expected {total_puts} results, got {len(collected)}"
        )

    def test_pending_count_reflects_queue_size(self):
        """pending_count() returns the actual queue depth."""
        queue = GateResultQueue()

        assert queue.pending_count() == 0

        for i in range(5):
            queue.put(
                TrailingGateResult(step_id=f"s{i}", passed=True, evaluation_ms=0.1)
            )

        # pending_count is based on qsize, should reflect items not yet drained
        assert queue.pending_count() == 5

        queue.drain()
        assert queue.pending_count() == 0


# ---------------------------------------------------------------------------
# Test: TrailingGateRunner concurrent submissions
# ---------------------------------------------------------------------------


class TestTrailingGateRunnerConcurrency:
    """Verify TrailingGateRunner under concurrent submit from 3+ threads."""

    def test_concurrent_submit_from_multiple_threads(self):
        """Submit gate evaluations from 3 concurrent threads, collect all results."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()
        num_threads = 4
        steps_per_thread = 5
        total_steps = num_threads * steps_per_thread
        barrier = threading.Barrier(num_threads)

        def _submitter(thread_idx: int) -> None:
            barrier.wait()
            for i in range(steps_per_thread):
                step = _make_step(
                    f"t{thread_idx}-step{i}",
                    gate=gate,
                )
                runner.submit(step, gate_check=_slow_gate_check(delay=0.01))

        threads = [
            threading.Thread(target=_submitter, args=(idx,))
            for idx in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        # Wait for all daemon threads to finish evaluation
        results = runner.wait_for_pending(timeout=10)

        assert len(results) == total_steps, (
            f"Expected {total_steps} results, got {len(results)}"
        )
        # All should pass since _slow_gate_check defaults to passed=True
        for r in results:
            assert r.passed is True

    def test_steps_without_gate_return_immediate_pass(self):
        """Steps with gate=None produce immediate pass results without spawning threads."""
        runner = TrailingGateRunner()

        for i in range(3):
            step = _make_step(f"no-gate-{i}", gate=None)
            runner.submit(step)

        # No pending evaluations -- gate=None path is synchronous
        assert runner.pending_count == 0

        results = runner.drain()
        assert len(results) == 3
        for r in results:
            assert r.passed is True
            assert r.evaluation_ms == 0.0


# ---------------------------------------------------------------------------
# Test: pending_count accuracy
# ---------------------------------------------------------------------------


class TestPendingCountAccuracy:
    """Verify pending_count tracks active evaluations accurately."""

    def test_pending_count_rises_and_falls(self):
        """pending_count increments on submit and decrements when evaluation completes."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()

        # Submit steps with a deliberate delay so they stay pending
        for i in range(3):
            step = _make_step(f"pending-{i}", gate=gate)
            runner.submit(step, gate_check=_slow_gate_check(delay=0.2))

        # Immediately after submit, pending_count should be > 0
        # (race: some may already finish, so assert >= 1)
        time.sleep(0.01)  # tiny settle time for thread startup
        initial_pending = runner.pending_count
        assert initial_pending >= 1, (
            f"Expected at least 1 pending evaluation, got {initial_pending}"
        )

        # After waiting, all should complete
        runner.wait_for_pending(timeout=5)
        assert runner.pending_count == 0, (
            f"Expected 0 pending after wait_for_pending, got {runner.pending_count}"
        )

    def test_pending_count_zero_when_no_submissions(self):
        """Fresh runner has pending_count == 0."""
        runner = TrailingGateRunner()
        assert runner.pending_count == 0


# ---------------------------------------------------------------------------
# Test: Daemon thread cleanup behavior
# ---------------------------------------------------------------------------


class TestDaemonThreadBehavior:
    """Verify that spawned threads are daemon threads."""

    def test_spawned_threads_are_daemon(self):
        """All threads created by submit() have daemon=True."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()

        # Use a longer delay so thread is still alive when we inspect
        step = _make_step("daemon-check", gate=gate)
        runner.submit(step, gate_check=_slow_gate_check(delay=0.5))

        # Inspect threads stored on the runner
        assert len(runner._threads) >= 1, "Expected at least one thread to be tracked"
        for t in runner._threads:
            assert t.daemon is True, (
                f"Thread {t.name} is not daemon -- would block process exit"
            )

        # Clean up
        runner.wait_for_pending(timeout=5)

    def test_cancel_stops_pending_evaluations(self):
        """cancel() sets cancellation event; threads that have not started
        evaluation yet observe it and skip work."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()

        # Submit a step that would take a long time
        step = _make_step("cancel-target", gate=gate)
        runner.submit(step, gate_check=_slow_gate_check(delay=2.0))

        # Cancel immediately
        runner.cancel()

        # After cancel, internal thread list should be cleared
        assert len(runner._threads) == 0, (
            "Expected _threads to be cleared after cancel()"
        )


# ---------------------------------------------------------------------------
# Test: DeferredRemediationLog integration
# ---------------------------------------------------------------------------


class TestDeferredRemediationLogIntegration:
    """Verify DeferredRemediationLog captures and persists failed gate results."""

    def test_failed_gates_captured_in_remediation_log(self):
        """Run submissions that fail, collect results, feed into remediation log."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()
        rlog = DeferredRemediationLog()

        # Submit steps that will fail
        for i in range(3):
            step = _make_step(f"fail-{i}", gate=gate)
            runner.submit(
                step,
                gate_check=_slow_gate_check(
                    delay=0.01,
                    passed=False,
                    reason=f"Missing title field in step fail-{i}",
                ),
            )

        results = runner.wait_for_pending(timeout=5)
        assert len(results) == 3

        for r in results:
            assert r.passed is False
            rlog.append(r)

        pending = rlog.pending_remediations()
        assert len(pending) == 3
        for entry in pending:
            assert entry.remediation_status == "pending"
            assert "Missing title field" in entry.failure_reason

    def test_remediation_log_disk_persistence(self, tmp_path: Path):
        """DeferredRemediationLog persists to disk and reloads correctly."""
        persist_file = tmp_path / "remediation.json"
        rlog = DeferredRemediationLog(persist_path=persist_file)

        failed_result = TrailingGateResult(
            step_id="persist-test",
            passed=False,
            evaluation_ms=42.0,
            failure_reason="Test failure for persistence",
        )
        rlog.append(failed_result)

        assert persist_file.exists(), "Persist file should exist after append"

        # Reload from disk
        loaded = DeferredRemediationLog.load_from_disk(persist_file)
        pending = loaded.pending_remediations()
        assert len(pending) == 1
        assert pending[0].step_id == "persist-test"
        assert pending[0].failure_reason == "Test failure for persistence"

    def test_mark_remediated_changes_status(self):
        """mark_remediated transitions an entry from pending to remediated."""
        rlog = DeferredRemediationLog()
        rlog.append(
            TrailingGateResult(
                step_id="mark-me",
                passed=False,
                evaluation_ms=1.0,
                failure_reason="test",
            )
        )

        assert len(rlog.pending_remediations()) == 1
        assert rlog.mark_remediated("mark-me") is True
        assert len(rlog.pending_remediations()) == 0


# ---------------------------------------------------------------------------
# Test: wait_for_pending timeout behavior
# ---------------------------------------------------------------------------


class TestWaitForPendingTimeout:
    """Verify wait_for_pending returns within timeout even if threads hang."""

    def test_wait_for_pending_respects_timeout(self):
        """If gate_check hangs, wait_for_pending returns after timeout, not indefinitely."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()

        # Submit a step with a very long evaluation
        step = _make_step("slow-step", gate=gate)
        runner.submit(step, gate_check=_slow_gate_check(delay=60.0))

        start = time.monotonic()
        # Short timeout -- should not block for 60s
        results = runner.wait_for_pending(timeout=0.5)
        elapsed = time.monotonic() - start

        assert elapsed < 5.0, (
            f"wait_for_pending blocked for {elapsed:.1f}s, expected ~0.5s"
        )
        # The slow step may or may not have produced a result
        # (it is still running in a daemon thread). That is acceptable.

    def test_wait_for_pending_returns_all_completed_results(self):
        """After all evaluations finish, wait_for_pending returns every result."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()

        for i in range(5):
            step = _make_step(f"fast-{i}", gate=gate)
            runner.submit(step, gate_check=_slow_gate_check(delay=0.01))

        results = runner.wait_for_pending(timeout=5)
        assert len(results) == 5
        step_ids = {r.step_id for r in results}
        expected_ids = {f"fast-{i}" for i in range(5)}
        assert step_ids == expected_ids, (
            f"Missing step IDs: {expected_ids - step_ids}"
        )


# ---------------------------------------------------------------------------
# Test: Mixed pass/fail under concurrency
# ---------------------------------------------------------------------------


class TestMixedPassFailConcurrency:
    """End-to-end: concurrent mix of passing and failing gates."""

    def test_mixed_results_collected_correctly(self):
        """Submit a mix of pass/fail steps from multiple threads;
        verify each result has the correct pass/fail status."""
        runner = TrailingGateRunner()
        gate = _make_gate_criteria()
        rlog = DeferredRemediationLog()
        num_threads = 3
        steps_per_thread = 10
        barrier = threading.Barrier(num_threads)

        def _submitter(thread_idx: int) -> None:
            barrier.wait()
            for i in range(steps_per_thread):
                step_id = f"t{thread_idx}-s{i}"
                should_pass = (i % 2 == 0)
                step = _make_step(step_id, gate=gate)
                runner.submit(
                    step,
                    gate_check=_slow_gate_check(
                        delay=0.005,
                        passed=should_pass,
                        reason=None if should_pass else f"Forced fail: {step_id}",
                    ),
                )

        threads = [
            threading.Thread(target=_submitter, args=(idx,))
            for idx in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        results = runner.wait_for_pending(timeout=10)
        total = num_threads * steps_per_thread
        assert len(results) == total, f"Expected {total} results, got {len(results)}"

        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        # Even indices pass, odd fail: 5 pass + 5 fail per thread
        expected_pass = num_threads * (steps_per_thread // 2)
        expected_fail = num_threads * (steps_per_thread // 2)
        assert len(passed) == expected_pass, (
            f"Expected {expected_pass} passes, got {len(passed)}"
        )
        assert len(failed) == expected_fail, (
            f"Expected {expected_fail} failures, got {len(failed)}"
        )

        # Feed failures into remediation log
        for r in failed:
            rlog.append(r)

        assert rlog.entry_count == expected_fail
        assert len(rlog.pending_remediations()) == expected_fail
