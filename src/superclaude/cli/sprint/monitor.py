"""Sidecar output monitor — daemon thread that watches output files."""

from __future__ import annotations

import re
import threading
import time
from pathlib import Path

from .models import MonitorState

# Patterns to extract from claude output
TASK_ID_PATTERN = re.compile(r"T\d{2}\.\d{2}")
TOOL_PATTERN = re.compile(
    r"\b(Read|Edit|MultiEdit|Write|Grep|Glob|Bash|TodoWrite|TodoRead|Task)\b"
)
FILES_CHANGED_PATTERN = re.compile(
    r"(?:modified|created|edited|wrote|updated)\s+[`'\"]?([^\s`'\"]+\.\w+)"
)


class OutputMonitor:
    """Background thread that watches an output file and extracts signals.

    The monitor does not hold the file open. It stat()s and reads only
    the new bytes since the last poll. This is safe even when the file
    is being written by a child process.
    """

    def __init__(self, output_path: Path, poll_interval: float = 0.5):
        self.output_path = output_path
        self.poll_interval = poll_interval
        self.state = MonitorState()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_read_pos: int = 0
        self._seen_files: set[str] = set()

    def start(self):
        """Start the monitor thread."""
        self._stop_event.clear()
        self._last_read_pos = 0
        self._seen_files.clear()
        self.state = MonitorState()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="output-monitor",
        )
        self._thread.start()

    def stop(self):
        """Stop the monitor thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def reset(self, new_output_path: Path):
        """Reset for a new phase (new output file)."""
        self.output_path = new_output_path
        self._last_read_pos = 0
        self._seen_files.clear()
        self.state = MonitorState()

    def _poll_loop(self):
        while not self._stop_event.is_set():
            self._poll_once()
            self._stop_event.wait(self.poll_interval)

    def _poll_once(self):
        now = time.monotonic()

        try:
            size = self.output_path.stat().st_size
        except FileNotFoundError:
            return

        self.state.output_bytes_prev = self.state.output_bytes
        self.state.output_bytes = size

        if size > self._last_read_pos:
            # New data available -- read incremental chunk
            self.state.last_growth_time = now
            self.state.stall_seconds = 0.0  # reset stall on growth
            new_text = self._read_new_bytes(size)
            self._extract_signals(new_text)
        else:
            # No growth -- update stall counter
            self.state.stall_seconds = now - self.state.last_growth_time

        # Growth rate: exponential moving average
        delta = self.state.output_bytes - self.state.output_bytes_prev
        alpha = 0.3
        self.state.growth_rate_bps = (
            alpha * (delta / self.poll_interval)
            + (1 - alpha) * self.state.growth_rate_bps
        )

    def _read_new_bytes(self, current_size: int) -> str:
        """Read only the bytes added since last poll."""
        try:
            with open(self.output_path, errors="replace") as f:
                f.seek(self._last_read_pos)
                chunk = f.read(current_size - self._last_read_pos)
                self._last_read_pos = current_size
                return chunk
        except (OSError, UnicodeDecodeError):
            return ""

    def _extract_signals(self, text: str):
        """Extract task IDs, tool names, file paths from new output text."""
        # Last task ID (take the last match)
        task_matches = TASK_ID_PATTERN.findall(text)
        if task_matches:
            self.state.last_task_id = task_matches[-1]

        # Last tool used
        tool_matches = TOOL_PATTERN.findall(text)
        if tool_matches:
            self.state.last_tool_used = tool_matches[-1]

        # Files changed (accumulate unique paths)
        file_matches = FILES_CHANGED_PATTERN.findall(text)
        for f in file_matches:
            self._seen_files.add(f)
        self.state.files_changed = len(self._seen_files)

        # Line count
        self.state.lines_total += text.count("\n")
