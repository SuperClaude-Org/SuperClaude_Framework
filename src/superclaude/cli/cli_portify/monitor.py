"""Monitoring, diagnostics, and failure classification for cli-portify.

Provides:
- NDJSON event logging using signal vocabulary constants (D-0004/D-0010)
- Failure classification for 7 types: timeout, missing_artifact,
  malformed_frontmatter, gate_failure, user_rejection, budget_exhaustion,
  partial_artifact
- Per-phase and per-step timing capture
- Markdown report generation from diagnostic data

Per D-0019 (NDJSON logging), D-0020 (failure classification), D-0048 (report).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, TextIO

from superclaude.cli.cli_portify.models import FailureClassification, PortifyStatus
from superclaude.cli.cli_portify.utils import SIGNAL_VOCABULARY


@dataclass
class EventRecord:
    """A single NDJSON event record."""

    event_type: str
    step: str = ""
    phase: int = 0
    timestamp: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": self.event_type,
            "step": self.step,
            "phase": self.phase,
            "ts": self.timestamp,
            **self.data,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventLogger:
    """NDJSON event logger using signal vocabulary constants.

    Writes one JSON object per line to the output stream.
    Event types come from the D-0004 signal vocabulary.
    """

    def __init__(self, output: TextIO | None = None):
        self._output = output or StringIO()
        self._events: list[EventRecord] = []

    def emit(
        self,
        event_type: str,
        step: str = "",
        phase: int = 0,
        **data: Any,
    ) -> EventRecord:
        """Emit an NDJSON event record.

        Args:
            event_type: Signal vocabulary constant (e.g. step_start).
            step: Step name.
            phase: Phase number.
            **data: Additional event data.

        Returns:
            The emitted EventRecord.
        """
        record = EventRecord(
            event_type=event_type,
            step=step,
            phase=phase,
            timestamp=time.time(),
            data=data,
        )
        self._events.append(record)
        self._output.write(record.to_json() + "\n")
        return record

    @property
    def events(self) -> list[EventRecord]:
        return list(self._events)

    def get_output(self) -> str:
        """Get all NDJSON output as a string (only works with StringIO)."""
        if isinstance(self._output, StringIO):
            return self._output.getvalue()
        return ""


@dataclass
class StepTiming:
    """Timing data for a single step."""

    step: str
    phase: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def duration_seconds(self) -> float:
        if self.finished_at <= 0 or self.started_at <= 0:
            return 0.0
        return self.finished_at - self.started_at


@dataclass
class PhaseTiming:
    """Timing data for a pipeline phase."""

    phase: int
    name: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0
    step_timings: list[StepTiming] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        if self.finished_at <= 0 or self.started_at <= 0:
            return 0.0
        return self.finished_at - self.started_at


class TimingCapture:
    """Captures per-step and per-phase timing."""

    def __init__(self) -> None:
        self._steps: dict[str, StepTiming] = {}
        self._phases: dict[int, PhaseTiming] = {}
        self._pipeline_start: float = 0.0
        self._pipeline_end: float = 0.0

    def start_pipeline(self) -> None:
        self._pipeline_start = time.time()

    def end_pipeline(self) -> None:
        self._pipeline_end = time.time()

    def start_step(self, step: str, phase: int = 0) -> None:
        self._steps[step] = StepTiming(step=step, phase=phase, started_at=time.time())
        if phase not in self._phases:
            self._phases[phase] = PhaseTiming(phase=phase, started_at=time.time())

    def end_step(self, step: str) -> None:
        if step in self._steps:
            self._steps[step].finished_at = time.time()
            phase_num = self._steps[step].phase
            if phase_num in self._phases:
                self._phases[phase_num].step_timings.append(self._steps[step])
                self._phases[phase_num].finished_at = time.time()

    def get_step_timing(self, step: str) -> StepTiming | None:
        return self._steps.get(step)

    def get_phase_timing(self, phase: int) -> PhaseTiming | None:
        return self._phases.get(phase)

    @property
    def total_duration(self) -> float:
        if self._pipeline_end <= 0 or self._pipeline_start <= 0:
            return 0.0
        return self._pipeline_end - self._pipeline_start

    @property
    def step_timings(self) -> list[StepTiming]:
        return list(self._steps.values())

    @property
    def phase_timings(self) -> list[PhaseTiming]:
        return list(self._phases.values())


def classify_failure(
    exit_code: int,
    timed_out: bool,
    stdout: str,
    artifact_path: Path | None = None,
    gate_passed: bool | None = None,
    user_rejected: bool = False,
    budget_exhausted: bool = False,
) -> FailureClassification:
    """Classify a step failure into one of 7 failure types.

    Classification priority (first match wins):
    1. user_rejection - explicit user rejection
    2. budget_exhaustion - iteration/convergence budget exceeded
    3. timeout - subprocess timed out
    4. missing_artifact - expected output file not found
    5. malformed_frontmatter - output exists but frontmatter invalid
    6. gate_failure - gate check failed
    7. partial_artifact - output exists but incomplete
    """
    if user_rejected:
        return FailureClassification.USER_REJECTION

    if budget_exhausted:
        return FailureClassification.BUDGET_EXHAUSTION

    if timed_out:
        return FailureClassification.TIMEOUT

    if artifact_path is not None and not artifact_path.exists():
        return FailureClassification.MISSING_ARTIFACT

    if artifact_path is not None and artifact_path.exists():
        content = ""
        try:
            content = artifact_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass

        # Check for malformed frontmatter
        if content and not content.startswith("---"):
            return FailureClassification.MALFORMED_FRONTMATTER

        # Check for partial artifact (has content but incomplete)
        if content and "{{SC_PLACEHOLDER:" in content:
            return FailureClassification.PARTIAL_ARTIFACT

    if gate_passed is False:
        return FailureClassification.GATE_FAILURE

    # Default: gate failure if we can't determine more specific type
    return FailureClassification.GATE_FAILURE


def generate_diagnostic_report(
    timing: TimingCapture,
    events: list[EventRecord],
    step_results: list[dict[str, Any]],
) -> str:
    """Generate a Markdown diagnostic report from captured data.

    Args:
        timing: Captured timing data.
        events: List of NDJSON event records.
        step_results: List of step result dicts with keys:
            step, status, duration, failure_type (optional).

    Returns:
        Markdown report string.
    """
    lines: list[str] = []

    lines.append("# Portify Pipeline Diagnostic Report")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(f"- Total duration: {timing.total_duration:.1f}s")
    lines.append(f"- Steps executed: {len(step_results)}")
    lines.append(f"- Events logged: {len(events)}")

    passed = sum(1 for r in step_results if r.get("status") == "pass")
    failed = sum(1 for r in step_results if r.get("status") == "fail")
    lines.append(f"- Passed: {passed}")
    lines.append(f"- Failed: {failed}")
    lines.append("")

    # Per-step table
    lines.append("## Step Results")
    lines.append("")
    lines.append("| Step | Status | Duration | Failure Type |")
    lines.append("|------|--------|----------|-------------|")
    for r in step_results:
        step = r.get("step", "?")
        status = r.get("status", "?")
        dur = r.get("duration", 0.0)
        ftype = r.get("failure_type", "-")
        lines.append(f"| {step} | {status} | {dur:.1f}s | {ftype} |")
    lines.append("")

    # Phase timings
    if timing.phase_timings:
        lines.append("## Phase Timings")
        lines.append("")
        lines.append("| Phase | Duration | Steps |")
        lines.append("|-------|----------|-------|")
        for pt in timing.phase_timings:
            lines.append(
                f"| Phase {pt.phase} | {pt.duration_seconds:.1f}s | {len(pt.step_timings)} |"
            )
        lines.append("")

    # Event log summary
    if events:
        lines.append("## Event Summary")
        lines.append("")
        event_counts: dict[str, int] = {}
        for e in events:
            event_counts[e.event_type] = event_counts.get(e.event_type, 0) + 1
        for etype, count in sorted(event_counts.items()):
            lines.append(f"- {etype}: {count}")
        lines.append("")

    return "\n".join(lines)
