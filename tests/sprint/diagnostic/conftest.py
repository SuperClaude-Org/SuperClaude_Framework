"""Diagnostic test fixtures — test harness, debug log reader, and shared helpers.

Provides reusable fixtures for all diagnostic test levels (L0-L3).
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pytest

from superclaude.cli.sprint.debug_logger import (
    DEBUG_LOG_VERSION,
    LOGGER_NAME,
    debug_log,
    setup_debug_logger,
)
from superclaude.cli.sprint.diagnostics import (
    DiagnosticBundle,
    DiagnosticCollector,
    FailureCategory,
    FailureClassifier,
    ReportGenerator,
)
from superclaude.cli.sprint.models import (
    MonitorState,
    Phase,
    PhaseResult,
    PhaseStatus,
    SprintConfig,
    SprintResult,
)


# ---------------------------------------------------------------------------
# DebugLogReader
# ---------------------------------------------------------------------------


@dataclass
class DebugLogEntry:
    """Parsed entry from a debug log file."""

    timestamp: str
    level: str
    component: str
    event: str
    fields: dict = field(default_factory=dict)
    raw: str = ""


class DebugLogReader:
    """Parses structured debug log files for test assertions.

    Understands the log format:
        timestamp LEVEL    [component] event key=value key=value
    """

    LOG_LINE_PATTERN = re.compile(
        r"^(\S+)\s+(\w+)\s+\[(\w+)\]\s+(\S+)\s*(.*)?$"
    )

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._entries: list[DebugLogEntry] | None = None

    @property
    def entries(self) -> list[DebugLogEntry]:
        if self._entries is None:
            self._entries = self._parse()
        return self._entries

    def _parse(self) -> list[DebugLogEntry]:
        entries = []
        if not self.log_path.exists():
            return entries
        for line in self.log_path.read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            m = self.LOG_LINE_PATTERN.match(line)
            if m:
                ts, level, component, event, rest = m.groups()
                fields = {}
                if rest:
                    for pair in rest.strip().split(" "):
                        if "=" in pair:
                            k, v = pair.split("=", 1)
                            fields[k] = v
                entries.append(DebugLogEntry(
                    timestamp=ts,
                    level=level,
                    component=component,
                    event=event,
                    fields=fields,
                    raw=line,
                ))
        return entries

    def events(self, event_name: str | None = None) -> list[DebugLogEntry]:
        """Filter entries by event name."""
        if event_name is None:
            return self.entries
        return [e for e in self.entries if e.event == event_name]

    def phase_events(self, phase_num: int) -> list[DebugLogEntry]:
        """Get all events for a specific phase (between PHASE_BEGIN and PHASE_END)."""
        result = []
        in_phase = False
        for entry in self.entries:
            if entry.event == "PHASE_BEGIN" and entry.fields.get("phase") == str(phase_num):
                in_phase = True
            if in_phase:
                result.append(entry)
            if entry.event == "PHASE_END" and entry.fields.get("phase") == str(phase_num):
                break
        return result

    @property
    def version(self) -> str | None:
        """Extract version from header comment."""
        if self.log_path.exists():
            first_line = self.log_path.read_text().splitlines()[0]
            if first_line.startswith("# debug-log-version:"):
                return first_line.split(":", 1)[1].strip()
        return None


# ---------------------------------------------------------------------------
# DiagnosticTestHarness
# ---------------------------------------------------------------------------


class DiagnosticTestHarness:
    """Test harness providing a controlled environment for diagnostic testing.

    Creates a complete sprint environment with configurable phases, output
    files, and debug logging. Provides methods to simulate various failure
    scenarios for testing the diagnostic pipeline.
    """

    def __init__(self, tmp_path: Path, num_phases: int = 1, debug: bool = True, **config_kwargs):
        self.tmp_path = tmp_path
        self.phases = []
        for i in range(1, num_phases + 1):
            phase_file = tmp_path / f"phase-{i}-tasklist.md"
            phase_file.write_text(f"# Phase {i}\nContent")
            self.phases.append(Phase(number=i, file=phase_file))

        index_file = tmp_path / "tasklist-index.md"
        index_file.write_text(
            "\n".join(f"- {p.file.name}" for p in self.phases)
        )

        self.config = SprintConfig(
            index_path=index_file,
            release_dir=tmp_path,
            phases=self.phases,
            debug=debug,
            **config_kwargs,
        )

        # Ensure results dir
        self.config.results_dir.mkdir(parents=True, exist_ok=True)

        # Setup debug logger if enabled
        self._logger = None
        if debug:
            self._logger = setup_debug_logger(self.config)

    def simulate_phase_output(self, phase: Phase, ndjson_events: list[dict]):
        """Write NDJSON events to the phase output file."""
        output_file = self.config.output_file(phase)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            for event in ndjson_events:
                f.write(json.dumps(event) + "\n")

    def simulate_phase_error(self, phase: Phase, stderr_content: str):
        """Write stderr content for a phase."""
        error_file = self.config.error_file(phase)
        error_file.parent.mkdir(parents=True, exist_ok=True)
        error_file.write_text(stderr_content)

    def emit_debug_events(self, phase: Phase, events: list[tuple[str, dict]]):
        """Emit debug log events for a phase."""
        dbg = logging.getLogger(f"{LOGGER_NAME}.executor")
        debug_log(dbg, "PHASE_BEGIN", phase=phase.number, file=str(phase.file))
        for event_name, kwargs in events:
            debug_log(dbg, event_name, **kwargs)
        debug_log(dbg, "PHASE_END", phase=phase.number, exit_code=0, duration=10.0)

    def make_phase_result(
        self,
        phase: Phase,
        status: PhaseStatus = PhaseStatus.PASS,
        exit_code: int = 0,
    ) -> PhaseResult:
        now = datetime.now(timezone.utc)
        output_file = self.config.output_file(phase)
        output_bytes = output_file.stat().st_size if output_file.exists() else 0
        return PhaseResult(
            phase=phase,
            status=status,
            exit_code=exit_code,
            started_at=now,
            finished_at=now,
            output_bytes=output_bytes,
        )

    def get_log_reader(self) -> DebugLogReader:
        return DebugLogReader(self.config.debug_log_path)

    def cleanup(self):
        if self._logger:
            for h in self._logger.handlers[:]:
                h.close()
                self._logger.removeHandler(h)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def harness(tmp_path):
    """Provide a single-phase DiagnosticTestHarness."""
    h = DiagnosticTestHarness(tmp_path)
    yield h
    h.cleanup()


@pytest.fixture
def multi_phase_harness(tmp_path):
    """Provide a 3-phase DiagnosticTestHarness."""
    h = DiagnosticTestHarness(tmp_path, num_phases=3)
    yield h
    h.cleanup()


@pytest.fixture
def log_reader_factory(tmp_path):
    """Factory for creating DebugLogReader instances."""
    def factory(content: str) -> DebugLogReader:
        log_path = tmp_path / "debug.log"
        log_path.write_text(content)
        return DebugLogReader(log_path)
    return factory
