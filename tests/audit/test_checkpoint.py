"""Tests for batch-level checkpointing with progress.json persistence.

Validates AC3: batch-level checkpointing for interrupted run resume.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from superclaude.cli.audit.checkpoint import (
    BatchStatus,
    CheckpointReader,
    CheckpointState,
    CheckpointWriter,
)


class TestCheckpointWriteAndRead:
    def test_write_creates_valid_json(self, tmp_path: Path):
        progress = tmp_path / "progress.json"
        writer = CheckpointWriter(progress)
        state = CheckpointState(
            run_id="test-001",
            total_batches=3,
            batches=[
                BatchStatus(batch_id="b1", status="COMPLETED", files_processed=5, files_remaining=0),
                BatchStatus(batch_id="b2", status="PENDING", files_processed=0, files_remaining=5),
            ],
        )
        writer.write(state)

        assert progress.exists()
        data = json.loads(progress.read_text())
        assert data["run_id"] == "test-001"
        assert data["total_batches"] == 3
        assert len(data["batches"]) == 2
        assert data["last_updated"] != ""

    def test_read_after_write(self, tmp_path: Path):
        progress = tmp_path / "progress.json"
        writer = CheckpointWriter(progress)
        reader = CheckpointReader(progress)

        state = CheckpointState(
            run_id="r1",
            total_batches=2,
            batches=[
                BatchStatus(batch_id="b1", status="COMPLETED", files_processed=3, files_remaining=0),
            ],
        )
        writer.write(state)
        restored = reader.read()

        assert restored is not None
        assert restored.run_id == "r1"
        assert restored.total_batches == 2
        assert len(restored.batches) == 1
        assert restored.batches[0].batch_id == "b1"
        assert restored.batches[0].status == "COMPLETED"

    def test_read_nonexistent_returns_none(self, tmp_path: Path):
        reader = CheckpointReader(tmp_path / "nope.json")
        assert reader.read() is None

    def test_completed_batch_ids(self, tmp_path: Path):
        progress = tmp_path / "progress.json"
        writer = CheckpointWriter(progress)
        reader = CheckpointReader(progress)

        state = CheckpointState(
            run_id="r1",
            total_batches=3,
            batches=[
                BatchStatus(batch_id="b1", status="COMPLETED", files_processed=5, files_remaining=0),
                BatchStatus(batch_id="b2", status="FAILED", files_processed=2, files_remaining=3),
                BatchStatus(batch_id="b3", status="PENDING", files_processed=0, files_remaining=5),
            ],
        )
        writer.write(state)

        completed = reader.completed_batch_ids()
        assert completed == {"b1"}


class TestResumeScenario:
    def test_interrupt_and_resume_skips_completed(self, tmp_path: Path):
        """Simulate 3-batch run: complete batch 1, interrupt, resume."""
        progress = tmp_path / "progress.json"
        writer = CheckpointWriter(progress)
        reader = CheckpointReader(progress)

        # Batch 1 completes
        state = CheckpointState(
            run_id="r1",
            total_batches=3,
            batches=[
                BatchStatus(batch_id="b1", status="COMPLETED", files_processed=5, files_remaining=0),
            ],
        )
        writer.write(state)

        # "Interruption" happens here -- new session starts
        completed = reader.completed_batch_ids()
        pending_batches = ["b1", "b2", "b3"]
        to_execute = [b for b in pending_batches if b not in completed]

        assert to_execute == ["b2", "b3"]

    def test_atomic_write_no_partial(self, tmp_path: Path):
        """Verify the file is always valid JSON (no partial writes)."""
        progress = tmp_path / "progress.json"
        writer = CheckpointWriter(progress)

        for i in range(5):
            state = CheckpointState(
                run_id="r1",
                total_batches=5,
                batches=[
                    BatchStatus(
                        batch_id=f"b{j}",
                        status="COMPLETED",
                        files_processed=10,
                        files_remaining=0,
                    )
                    for j in range(i + 1)
                ],
            )
            writer.write(state)

            # After each write, file must be valid JSON
            data = json.loads(progress.read_text())
            assert len(data["batches"]) == i + 1
