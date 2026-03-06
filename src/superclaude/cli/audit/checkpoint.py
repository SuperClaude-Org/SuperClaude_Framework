"""Batch-level checkpointing with progress.json persistence.

Implements AC3: batch-level checkpointing so interrupted runs can resume.
Checkpoint writer persists after each batch; reader restores on resume.
Atomic writes via write-to-temp-then-rename pattern.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class BatchStatus:
    """Status of a single batch within an audit run."""

    batch_id: str
    status: str  # "PENDING", "COMPLETED", "FAILED"
    files_processed: int = 0
    files_remaining: int = 0
    failure_reason: str | None = None


@dataclass
class CheckpointState:
    """Full checkpoint state persisted to progress.json."""

    run_id: str
    total_batches: int
    batches: list[BatchStatus] = field(default_factory=list)
    last_updated: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "total_batches": self.total_batches,
            "batches": [asdict(b) for b in self.batches],
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CheckpointState:
        batches = [
            BatchStatus(**b) for b in data.get("batches", [])
        ]
        return cls(
            run_id=data["run_id"],
            total_batches=data["total_batches"],
            batches=batches,
            last_updated=data.get("last_updated", ""),
        )


class CheckpointWriter:
    """Atomically writes checkpoint state to progress.json after each batch."""

    def __init__(self, progress_file: Path) -> None:
        self._path = progress_file

    def write(self, state: CheckpointState) -> None:
        """Atomically write state to progress.json.

        Uses write-to-temp-then-rename for crash safety.
        """
        state.last_updated = datetime.now(timezone.utc).isoformat()
        data = state.to_dict()

        self._path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(
            dir=str(self._path.parent),
            prefix=".progress_",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, str(self._path))
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


class CheckpointReader:
    """Reads checkpoint state from progress.json for resume."""

    def __init__(self, progress_file: Path) -> None:
        self._path = progress_file

    def read(self) -> CheckpointState | None:
        """Load checkpoint state. Returns None if file doesn't exist."""
        if not self._path.exists():
            return None
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return CheckpointState.from_dict(data)

    def completed_batch_ids(self) -> set[str]:
        """Return set of batch IDs already completed."""
        state = self.read()
        if state is None:
            return set()
        return {
            b.batch_id for b in state.batches if b.status == "COMPLETED"
        }
