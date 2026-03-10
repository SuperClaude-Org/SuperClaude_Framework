"""Tests for batch failure and retry handling (T01.10 / D-0010 / AC18)."""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.audit.batch_retry import (
    BatchResult,
    BatchRetryHandler,
    MinimumViableReport,
)
from superclaude.cli.audit.checkpoint import (
    CheckpointState,
    CheckpointWriter,
)


@pytest.fixture()
def tmp_progress(tmp_path: Path) -> Path:
    return tmp_path / "progress.json"


@pytest.fixture()
def state() -> CheckpointState:
    return CheckpointState(run_id="test-run", total_batches=3)


@pytest.fixture()
def handler(tmp_progress: Path) -> BatchRetryHandler:
    writer = CheckpointWriter(tmp_progress)
    return BatchRetryHandler(writer, max_retries=2)


class TestRetryBehavior:
    """Verify retry attempts and FAILED marking."""

    def test_success_on_first_attempt(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        def succeed(batch_id: str) -> BatchResult:
            return BatchResult(batch_id=batch_id, success=True, files_processed=5)

        result = handler.execute_batch("b1", succeed, state)
        assert result.success
        assert handler.retry_records["b1"].attempts == 1
        assert handler.retry_records["b1"].final_status == "COMPLETED"

    def test_success_on_second_attempt(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        call_count = 0

        def fail_then_succeed(batch_id: str) -> BatchResult:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return BatchResult(batch_id=batch_id, success=False, error="transient")
            return BatchResult(batch_id=batch_id, success=True, files_processed=3)

        result = handler.execute_batch("b1", fail_then_succeed, state)
        assert result.success
        assert handler.retry_records["b1"].attempts == 2

    def test_failed_after_max_retries(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        call_count = 0

        def always_fail(batch_id: str) -> BatchResult:
            nonlocal call_count
            call_count += 1
            return BatchResult(batch_id=batch_id, success=False, error=f"err-{call_count}")

        result = handler.execute_batch("b1", always_fail, state)
        assert not result.success
        assert call_count == 2  # max_retries=2
        assert handler.retry_records["b1"].final_status == "FAILED"
        assert handler.retry_records["b1"].attempts == 2

    def test_failed_batch_in_progress_json(
        self, handler: BatchRetryHandler, state: CheckpointState, tmp_progress: Path
    ) -> None:
        def always_fail(batch_id: str) -> BatchResult:
            return BatchResult(batch_id=batch_id, success=False, error="boom")

        handler.execute_batch("b1", always_fail, state)

        # Verify FAILED recorded in state
        assert any(
            b.batch_id == "b1" and b.status == "FAILED" and b.failure_reason == "boom"
            for b in state.batches
        )
        # Verify progress.json was written
        assert tmp_progress.exists()


class TestCascadingFailure:
    """Verify cascading failure detection and minimum viable report."""

    def test_cascading_failure_detected(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        def always_fail(batch_id: str) -> BatchResult:
            return BatchResult(batch_id=batch_id, success=False, error="fail")

        handler.execute_all(["b1", "b2", "b3"], always_fail, state)
        assert handler.is_cascading_failure()

    def test_not_cascading_if_one_succeeds(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        results = {"b1": False, "b2": True, "b3": False}

        def selective_fn(batch_id: str) -> BatchResult:
            return BatchResult(
                batch_id=batch_id,
                success=results[batch_id],
                error=None if results[batch_id] else "fail",
            )

        handler.execute_all(["b1", "b2", "b3"], selective_fn, state)
        assert not handler.is_cascading_failure()

    def test_minimum_viable_report(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        def always_fail(batch_id: str) -> BatchResult:
            return BatchResult(batch_id=batch_id, success=False, error=f"err-{batch_id}")

        handler.execute_all(["b1", "b2", "b3"], always_fail, state)
        report = handler.minimum_viable_report(state)

        assert isinstance(report, MinimumViableReport)
        assert report.run_id == "test-run"
        assert report.total_batches == 3
        assert report.failed_batches == 3
        assert len(report.error_summary) == 3

    def test_minimum_viable_report_serialization(
        self, handler: BatchRetryHandler, state: CheckpointState
    ) -> None:
        def always_fail(batch_id: str) -> BatchResult:
            return BatchResult(batch_id=batch_id, success=False, error="fail")

        handler.execute_all(["b1", "b2"], always_fail, state)
        report = handler.minimum_viable_report(state)
        d = report.to_dict()

        assert d["status"] == "CASCADING_FAILURE"
        assert d["failed_batches"] == 2
        assert isinstance(d["error_summary"], list)


class TestRetryPolicy:
    """Verify retry count is configurable and defaults correct."""

    def test_default_max_retries(self, tmp_progress: Path) -> None:
        writer = CheckpointWriter(tmp_progress)
        handler = BatchRetryHandler(writer)
        assert handler.max_retries == 2

    def test_custom_max_retries(self, tmp_progress: Path) -> None:
        writer = CheckpointWriter(tmp_progress)
        handler = BatchRetryHandler(writer, max_retries=5)
        assert handler.max_retries == 5

    def test_three_retries(
        self, tmp_progress: Path, state: CheckpointState
    ) -> None:
        writer = CheckpointWriter(tmp_progress)
        handler = BatchRetryHandler(writer, max_retries=3)
        call_count = 0

        def always_fail(batch_id: str) -> BatchResult:
            nonlocal call_count
            call_count += 1
            return BatchResult(batch_id=batch_id, success=False, error="fail")

        handler.execute_batch("b1", always_fail, state)
        assert call_count == 3
