"""Batch failure and retry handling policy.

Implements AC18 (partial): graceful batch failure handling with configurable
retry count, FAILED status marking in progress.json, and minimum viable
report output on cascading failure.

Retry policy: up to max_retries attempts per batch before marking FAILED.
Cascading failure: all batches fail → emit minimum viable report with error summary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .checkpoint import BatchStatus, CheckpointState, CheckpointWriter


DEFAULT_MAX_RETRIES = 2


@dataclass
class BatchResult:
    """Result of a single batch execution attempt."""

    batch_id: str
    success: bool
    error: str | None = None
    files_processed: int = 0


@dataclass
class RetryRecord:
    """Record of retry attempts for a single batch."""

    batch_id: str
    attempts: int = 0
    errors: list[str] = field(default_factory=list)
    final_status: str = "PENDING"


@dataclass
class MinimumViableReport:
    """Minimum viable report emitted on cascading failure."""

    run_id: str
    total_batches: int
    failed_batches: int
    error_summary: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "total_batches": self.total_batches,
            "failed_batches": self.failed_batches,
            "status": "CASCADING_FAILURE",
            "error_summary": self.error_summary,
        }


class BatchRetryHandler:
    """Wraps batch execution with configurable retry and failure handling.

    Provides retry logic per batch, FAILED status marking via checkpoint
    writer, and minimum viable report generation on cascading failure.
    """

    def __init__(
        self,
        checkpoint_writer: CheckpointWriter,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._writer = checkpoint_writer
        self._max_retries = max_retries
        self._retry_records: dict[str, RetryRecord] = {}

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def retry_records(self) -> dict[str, RetryRecord]:
        return dict(self._retry_records)

    def execute_batch(
        self,
        batch_id: str,
        execute_fn: Callable[[str], BatchResult],
        state: CheckpointState,
    ) -> BatchResult:
        """Execute a batch with retry logic.

        Retries up to max_retries times on failure. Updates checkpoint
        state after each attempt.

        Args:
            batch_id: Identifier for the batch.
            execute_fn: Function that executes the batch, returns BatchResult.
            state: Current checkpoint state (mutated in place).

        Returns:
            Final BatchResult after retries exhausted or success.
        """
        record = RetryRecord(batch_id=batch_id)
        self._retry_records[batch_id] = record

        last_result: BatchResult | None = None

        for attempt in range(1, self._max_retries + 1):
            record.attempts = attempt
            result = execute_fn(batch_id)
            last_result = result

            if result.success:
                record.final_status = "COMPLETED"
                self._update_batch_status(
                    state, batch_id, "COMPLETED",
                    files_processed=result.files_processed,
                )
                self._writer.write(state)
                return result

            record.errors.append(result.error or f"Attempt {attempt} failed")

        # All retries exhausted
        record.final_status = "FAILED"
        self._update_batch_status(
            state, batch_id, "FAILED",
            failure_reason=record.errors[-1] if record.errors else "Unknown failure",
        )
        self._writer.write(state)
        return last_result  # type: ignore[return-value]

    def execute_all(
        self,
        batch_ids: list[str],
        execute_fn: Callable[[str], BatchResult],
        state: CheckpointState,
    ) -> list[BatchResult]:
        """Execute all batches with retry handling.

        Args:
            batch_ids: Ordered list of batch IDs to execute.
            execute_fn: Function that executes a single batch.
            state: Current checkpoint state (mutated in place).

        Returns:
            List of BatchResults for all batches.
        """
        results: list[BatchResult] = []
        for bid in batch_ids:
            result = self.execute_batch(bid, execute_fn, state)
            results.append(result)
        return results

    def is_cascading_failure(self) -> bool:
        """Check if all executed batches failed (cascading failure)."""
        if not self._retry_records:
            return False
        return all(
            r.final_status == "FAILED" for r in self._retry_records.values()
        )

    def minimum_viable_report(self, state: CheckpointState) -> MinimumViableReport:
        """Generate a minimum viable report for cascading failure.

        Returns a report with error summary for each failed batch.
        """
        error_summary = []
        for batch_id, record in self._retry_records.items():
            if record.final_status == "FAILED":
                error_summary.append({
                    "batch_id": batch_id,
                    "attempts": record.attempts,
                    "last_error": record.errors[-1] if record.errors else "Unknown",
                })

        return MinimumViableReport(
            run_id=state.run_id,
            total_batches=state.total_batches,
            failed_batches=len(error_summary),
            error_summary=error_summary,
        )

    @staticmethod
    def _update_batch_status(
        state: CheckpointState,
        batch_id: str,
        status: str,
        *,
        files_processed: int = 0,
        failure_reason: str | None = None,
    ) -> None:
        """Update or create a batch status entry in checkpoint state."""
        for batch in state.batches:
            if batch.batch_id == batch_id:
                batch.status = status
                batch.files_processed = files_processed
                batch.failure_reason = failure_reason
                return

        state.batches.append(BatchStatus(
            batch_id=batch_id,
            status=status,
            files_processed=files_processed,
            failure_reason=failure_reason,
        ))
