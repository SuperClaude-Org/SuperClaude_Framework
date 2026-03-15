"""Sidecar output monitor — daemon thread that watches output files.

Parses stream-json (NDJSON) output from ``claude --print --output-format stream-json``.
Each line is a JSON object with a ``type`` field.  The monitor extracts task IDs,
tool names, and file-change signals from these events to drive the TUI.
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from pathlib import Path

from .debug_logger import debug_log
from .models import MonitorState

_dbg = logging.getLogger("superclaude.sprint.debug.monitor")

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
PROMPT_TOO_LONG_PATTERN = re.compile(r'"Prompt is too long"')


def detect_error_max_turns(output_path: Path) -> bool:
    """Check if the last NDJSON line indicates budget exhaustion.

    Scans the last non-empty line of the output file for the
    ``"subtype":"error_max_turns"`` pattern, which signals that a
    subprocess exhausted its turn budget.

    Returns True if error_max_turns is detected, False otherwise.
    """
    try:
        content = output_path.read_text(errors="replace")
    except (FileNotFoundError, OSError):
        return False

    if not content.strip():
        return False

    # Get last non-empty line
    lines = content.strip().splitlines()
    for line in reversed(lines):
        line = line.strip()
        if line:
            return bool(ERROR_MAX_TURNS_PATTERN.search(line))

    return False


def detect_prompt_too_long(output_path: Path) -> bool:
    """Check if NDJSON output contains a prompt-too-long error.

    Scans the last 10 non-empty lines of the output file for the
    ``"Prompt is too long"`` pattern, which signals that the subprocess
    context window was exhausted.

    Returns True if the pattern is found, False otherwise.
    """
    try:
        content = output_path.read_text(errors="replace")
    except (FileNotFoundError, OSError):
        return False

    if not content.strip():
        return False

    lines = content.strip().splitlines()
    # Scan last 10 non-empty lines (pattern may not be in the final line)
    count = 0
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        if PROMPT_TOO_LONG_PATTERN.search(line):
            return True
        count += 1
        if count >= 10:
            break

    return False


# Pattern for counting assistant message turns in NDJSON output
# Each "assistant" type message represents one turn consumed.
_TURN_INDICATOR_PATTERN = re.compile(r'"type"\s*:\s*"assistant"')


def count_turns_from_output(output_path: Path) -> int:
    """Extract the number of turns consumed from subprocess NDJSON output.

    Counts lines containing ``"type":"assistant"`` which represent
    individual assistant response turns. Each such line indicates
    one turn was consumed from the budget.

    Args:
        output_path: Path to the subprocess NDJSON output file.

    Returns:
        Number of turns counted. Returns 0 if file is missing or empty.
    """
    try:
        content = output_path.read_text(errors="replace")
    except (FileNotFoundError, OSError):
        return 0

    if not content.strip():
        return 0

    count = 0
    for line in content.splitlines():
        line = line.strip()
        if line and _TURN_INDICATOR_PATTERN.search(line):
            count += 1

    return count


class OutputMonitor:
    """Background thread that watches a stream-json output file.

    Reads incremental bytes, splits on newlines, and parses each complete
    line as JSON.  Partial lines are buffered across poll cycles so no
    data is lost when a write straddles a poll boundary.
    """

    def __init__(self, output_path: Path, poll_interval: float = 0.5):
        self.output_path = output_path
        self.poll_interval = poll_interval
        self.state = MonitorState()
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
        self._line_buffer = ""
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
            # New data available — read incremental chunk
            chunk = self._read_new_chunk(size)
            if chunk:
                self._process_chunk(chunk, now)
        else:
            # No growth — update stall counter
            self.state.stall_seconds = now - self.state.last_event_time

        debug_log(
            _dbg,
            "output_file_stat",
            path=str(self.output_path),
            size=size,
            events_received=self.state.events_received,
            last_event_time=round(self.state.last_event_time, 1),
        )

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
        """Split chunk into lines, parse complete NDJSON lines, buffer partials."""
        # Prepend any leftover partial line from previous poll
        data = self._line_buffer + chunk
        lines = data.split("\n")

        # Last element is either "" (if chunk ended with \n) or a partial line
        self._line_buffer = lines[-1]

        # Process all complete lines (everything except the last split element)
        for line in lines[:-1]:
            line = line.strip()
            if not line:
                continue

            # Update liveness on every complete line
            self.state.last_growth_time = now
            self.state.last_event_time = now
            self.state.stall_seconds = 0.0
            self.state.events_received += 1
            self.state.lines_total += 1

            # Try to parse as JSON
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                # Not valid JSON — still counts as a line for liveness,
                # but try text-mode signal extraction as fallback
                self._extract_signals_from_text(line)
                continue

            self._extract_signals_from_event(event)

    def _extract_signals_from_event(self, event: dict):
        """Extract task IDs, tool names, file paths from a parsed NDJSON event."""
        event_type = event.get("type", "")
        debug_log(_dbg, "ndjson_line_parsed", event_type=event_type, parsed=True)

        # Tool use events: extract tool name directly
        if event_type == "tool_use":
            tool = event.get("tool", "")
            if tool:
                self.state.last_tool_used = tool

        # Stringify the event for regex-based signal extraction
        # This catches task IDs and file changes regardless of event structure
        text = json.dumps(event, default=str)
        self._extract_signals_from_text(text)

    def _extract_signals_from_text(self, text: str):
        """Extract task IDs, tool names, file paths from text using regex."""
        # Last task ID (take the last match)
        task_matches = TASK_ID_PATTERN.findall(text)
        if task_matches:
            self.state.last_task_id = task_matches[-1]
            debug_log(_dbg, "signal_extracted", signal_type="task_id", value=task_matches[-1])

        # Last tool used (only if not already set by structured extraction)
        tool_matches = TOOL_PATTERN.findall(text)
        if tool_matches:
            self.state.last_tool_used = tool_matches[-1]
            debug_log(_dbg, "signal_extracted", signal_type="tool_name", value=tool_matches[-1])

        # Files changed (accumulate unique paths)
        file_matches = FILES_CHANGED_PATTERN.findall(text)
        for f in file_matches:
            self._seen_files.add(f)
        self.state.files_changed = len(self._seen_files)
