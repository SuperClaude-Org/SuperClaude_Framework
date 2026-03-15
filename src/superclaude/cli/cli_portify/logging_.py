"""Execution log emission skeleton for CLI Portify (NFR-007).

Emits:
- execution-log.jsonl  — machine-readable NDJSON log
- execution-log.md     — human-readable Markdown summary
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class ExecutionLog:
    """Writes execution-log.jsonl and execution-log.md to workdir."""

    def __init__(self, workdir: Path) -> None:
        self.workdir = workdir
        self._entries: list[dict[str, Any]] = []

    def record(self, event_type: str, **kwargs) -> None:
        """Record a log entry."""
        entry = {"ts": time.time(), "event": event_type}
        entry.update(kwargs)
        self._entries.append(entry)

    def flush(self, phase: str = "", status: str = "", elapsed: float = 0.0) -> None:
        """Write both log files to workdir."""
        self.workdir.mkdir(parents=True, exist_ok=True)

        # NDJSON
        jsonl_path = self.workdir / "execution-log.jsonl"
        with open(jsonl_path, "a") as fh:
            for entry in self._entries:
                fh.write(json.dumps(entry) + "\n")

        # Markdown
        md_path = self.workdir / "execution-log.md"
        with open(md_path, "a") as fh:
            fh.write(f"| {phase} | {status} | {elapsed:.3f}s |\n")

        self._entries.clear()
