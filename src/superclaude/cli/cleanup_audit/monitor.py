"""Sidecar output monitor for Cleanup Audit pipeline.

Daemon thread that watches output files, parses NDJSON output from
``claude --print --output-format stream-json``, and extracts signals
to drive the TUI.

Follows the sprint monitor pattern. See src/superclaude/cli/sprint/monitor.py.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

from .models import CleanupAuditMonitorState

# Patterns to extract from stringified event content
TASK_ID_PATTERN = re.compile(r"T\d{2}\.\d{2}")
TOOL_PATTERN = re.compile(
    r"\b(Read|Edit|MultiEdit|Write|Grep|Glob|Bash|TodoWrite|TodoRead|Task)\b"
)
FILES_CHANGED_PATTERN = re.compile(
    r"(?:modified|created|edited|wrote|updated)\s+[`'\"]?([^\s`'\"]+\.\w+)"
)

# Pattern for detecting budget exhaustion in NDJSON output
ERROR_MAX_TURNS_PATTERN = re.compile(r'"subtype"\s*:\s*"error_max_turns"')


def detect_error_max_turns(output_path: Path) -> bool:
    """Check if the last NDJSON line indicates budget exhaustion."""
    try:
        content = output_path.read_text(errors="replace")
    except (FileNotFoundError, OSError):
        return False

    if not content.strip():
        return False

    lines = content.strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if line:
            return bool(ERROR_MAX_TURNS_PATTERN.search(line))

    return False


class OutputMonitor:
    """Background thread that watches a stream-json output file.

    Reads incremental bytes, splits on newlines, and parses each complete
    line as JSON. Partial lines are buffered across poll cycles.
    """

    def __init__(self, output_path: Path, poll_interval: float = 0.5):
        self.output_path = output_path
        self.poll_interval = poll_interval
        self.state = CleanupAuditMonitorState()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_read_pos: int = 0
        self._line_buffer: str = ""
        self._seen_files: set[str] = set()

    def start(self):
        """Start the monitor thread."""
        self._stop_event.clear()
        self._last_read_pos = 0
        self._line_buffer = ""
        self._seen_files.clear()
        self.state = CleanupAuditMonitorState()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="cleanup-audit-monitor",
        )
        self._thread.start()

    def stop(self):
        """Stop the monitor thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def reset(self, new_output_path: Path):
        """Reset for a new step (new output file)."""
        self.output_path = new_output_path
        self._last_read_pos = 0
        self._line_buffer = ""
        self._seen_files.clear()
        self.state = CleanupAuditMonitorState()

    def get_state(self) -> CleanupAuditMonitorState:
        """Return current monitor state."""
        return self.state

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
            chunk = self._read_new_chunk(size)
            if chunk:
                self._process_chunk(chunk, now)
        else:
            self.state.stall_seconds = now - self.state.last_event_time

        # Growth rate: exponential moving average
        delta = self.state.output_bytes - self.state.output_bytes_prev
        alpha = 0.3
        self.state.growth_rate_bps = (
            alpha * (delta / self.poll_interval)
            + (1 - alpha) * self.state.growth_rate_bps
        )

    def _read_new_chunk(self, current_size: int) -> str:
        """Read only the bytes added since last poll."""
        try:
            with open(self.output_path, errors="replace") as f:
                f.seek(self._last_read_pos)
                chunk = f.read(current_size - self._last_read_pos)
                self._last_read_pos = current_size
                return chunk
        except (OSError, UnicodeDecodeError):
            return ""

    def _process_chunk(self, chunk: str, now: float):
        """Split chunk into lines, parse complete NDJSON lines."""
        data = self._line_buffer + chunk
        lines = data.split("\n")
        self._line_buffer = lines[-1]

        for line in lines[:-1]:
            line = line.strip()
            if not line:
                continue

            self.state.last_growth_time = now
            self.state.last_event_time = now
            self.state.stall_seconds = 0.0
            self.state.events_received += 1
            self.state.lines_total += 1

            try:
                event = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                self._extract_signals_from_text(line)
                continue

            self._extract_signals_from_event(event)

    def _extract_signals_from_event(self, event: dict):
        """Extract task IDs, tool names, file paths from a parsed NDJSON event."""
        event_type = event.get("type", "")

        if event_type == "tool_use":
            tool = event.get("tool", "")
            if tool:
                self.state.last_tool_used = tool

        text = json.dumps(event, default=str)
        self._extract_signals_from_text(text)

    def _extract_signals_from_text(self, text: str):
        """Extract task IDs, tool names, file paths from text using regex."""
        task_matches = TASK_ID_PATTERN.findall(text)
        if task_matches:
            self.state.last_task_id = task_matches[-1]

        tool_matches = TOOL_PATTERN.findall(text)
        if tool_matches:
            self.state.last_tool_used = tool_matches[-1]

        file_matches = FILES_CHANGED_PATTERN.findall(text)
        for f in file_matches:
            self._seen_files.add(f)
        self.state.files_changed = len(self._seen_files)
