"""Output monitoring, diagnostics, and failure classification.

Implements:
- OutputMonitor tracking 8 metrics (NFR-009, T03.11)
- Stall detection with kill action on growth_rate_bps drop (R-001)
- EventLogger producing NDJSON using signal vocabulary
- TimingCapture for per-phase and per-step timing
- classify_failure() for all 7 FailureClassification types
- generate_diagnostic_report() Markdown report
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from superclaude.cli.cli_portify.models import FailureClassification, MonitorState


# ---------------------------------------------------------------------------
# EventRecord
# ---------------------------------------------------------------------------


@dataclass
class EventRecord:
    """A single NDJSON event record."""

    event_type: str
    step: str = ""
    phase: int = 0
    timestamp: float = field(default_factory=time.time)
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict[str, Any] = {
            "event": self.event_type,
            "step": self.step,
            "phase": self.phase,
            "ts": self.timestamp,
        }
        d.update(self.extra)
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


# ---------------------------------------------------------------------------
# EventLogger
# ---------------------------------------------------------------------------


class EventLogger:
    """NDJSON event logger using signal vocabulary."""

    def __init__(self) -> None:
        self.events: list[EventRecord] = []

    def emit(self, event_type: str, step: str = "", phase: int = 0, **kwargs) -> None:
        record = EventRecord(
            event_type=event_type,
            step=step,
            phase=phase,
            extra=kwargs,
        )
        self.events.append(record)

    def get_output(self) -> str:
        """Return all events as newline-delimited JSON."""
        lines = [e.to_json() for e in self.events]
        return "\n".join(lines) + ("\n" if lines else "")


# ---------------------------------------------------------------------------
# classify_failure()
# ---------------------------------------------------------------------------


def classify_failure(
    exit_code: int,
    timed_out: bool,
    stdout: str,
    *,
    artifact_path: Optional[Path] = None,
    gate_passed: bool = True,
    user_rejected: bool = False,
    budget_exhausted: bool = False,
) -> FailureClassification:
    """Classify a step failure into one of the 7 FailureClassification types.

    Priority order:
      1. USER_REJECTION (overrides all other signals)
      2. BUDGET_EXHAUSTION
      3. TIMEOUT (exit 124 or timed_out)
      4. GATE_FAILURE (non-zero exit with gate failure)
      5. MISSING_ARTIFACT (exit 0, artifact path given but not found)
      6. MALFORMED_FRONTMATTER (exit 0, artifact found but no --- frontmatter)
      7. PARTIAL_ARTIFACT (exit 0, artifact found, frontmatter ok, but placeholders)
    """
    if user_rejected:
        return FailureClassification.USER_REJECTION

    if budget_exhausted:
        return FailureClassification.BUDGET_EXHAUSTION

    if timed_out or exit_code == 124:
        return FailureClassification.TIMEOUT

    if not gate_passed:
        return FailureClassification.GATE_FAILURE

    # exit 0 paths
    if artifact_path is not None:
        if not artifact_path.exists():
            return FailureClassification.MISSING_ARTIFACT
        content = artifact_path.read_text(errors="replace")
        if not content.startswith("---"):
            return FailureClassification.MALFORMED_FRONTMATTER
        if "{{SC_PLACEHOLDER:" in content:
            return FailureClassification.PARTIAL_ARTIFACT

    return FailureClassification.MISSING_ARTIFACT


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------


@dataclass
class StepTiming:
    step: str
    phase: int
    start_time: float
    end_time: float = 0.0

    @property
    def duration_seconds(self) -> float:
        return self.end_time - self.start_time


@dataclass
class PhaseTiming:
    phase: int
    step_timings: list[StepTiming] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        return sum(s.duration_seconds for s in self.step_timings)


class TimingCapture:
    """Captures per-phase and per-step timing."""

    def __init__(self) -> None:
        self._step_timings: dict[str, StepTiming] = {}
        self._phase_timings: dict[int, PhaseTiming] = {}
        self._pipeline_start: float = 0.0
        self._pipeline_end: float = 0.0

    def start_pipeline(self) -> None:
        self._pipeline_start = time.monotonic()

    def end_pipeline(self) -> None:
        self._pipeline_end = time.monotonic()

    @property
    def total_duration(self) -> float:
        return self._pipeline_end - self._pipeline_start

    def start_step(self, step: str, phase: int = 0) -> None:
        st = StepTiming(step=step, phase=phase, start_time=time.monotonic())
        self._step_timings[step] = st
        if phase not in self._phase_timings:
            self._phase_timings[phase] = PhaseTiming(phase=phase)

    def end_step(self, step: str) -> None:
        if step in self._step_timings:
            st = self._step_timings[step]
            st.end_time = time.monotonic()
            phase = st.phase
            if phase in self._phase_timings:
                self._phase_timings[phase].step_timings.append(st)

    def get_step_timing(self, step: str) -> Optional[StepTiming]:
        return self._step_timings.get(step)

    def get_phase_timing(self, phase: int) -> Optional[PhaseTiming]:
        return self._phase_timings.get(phase)

    @property
    def step_timings(self) -> list[StepTiming]:
        return list(self._step_timings.values())


# ---------------------------------------------------------------------------
# OutputMonitor (NFR-009, R-001)
# ---------------------------------------------------------------------------


class OutputMonitor:
    """Tracks 8 output metrics and detects stalls via growth_rate_bps.

    Stall detection: if growth_rate_bps drops below stall_threshold_bps for
    stall_timeout_seconds, the kill_fn is called.
    """

    def __init__(
        self,
        stall_threshold_bps: float = 1.0,
        stall_timeout_seconds: float = 60.0,
        kill_fn: Optional[callable] = None,
    ) -> None:
        self.state = MonitorState()
        self._stall_threshold_bps = stall_threshold_bps
        self._stall_timeout_seconds = stall_timeout_seconds
        self._kill_fn = kill_fn
        self._last_update_time: float = time.monotonic()
        self._last_bytes: int = 0

    def update(self, new_bytes: int, new_lines: int = 0) -> None:
        """Update metrics with fresh byte/line count."""
        now = time.monotonic()
        elapsed = now - self._last_update_time
        delta_bytes = new_bytes - self._last_bytes

        if elapsed > 0:
            self.state.growth_rate_bps = delta_bytes / elapsed
        else:
            self.state.growth_rate_bps = float(delta_bytes)

        self.state.output_bytes = new_bytes
        self.state.line_count += new_lines
        self.state.events += 1

        if self.state.growth_rate_bps < self._stall_threshold_bps:
            self.state.stall_seconds += elapsed
            if self.state.stall_seconds >= self._stall_timeout_seconds:
                if self._kill_fn is not None:
                    self._kill_fn()
        else:
            self.state.stall_seconds = 0.0

        self._last_bytes = new_bytes
        self._last_update_time = now


# ---------------------------------------------------------------------------
# generate_diagnostic_report()
# ---------------------------------------------------------------------------


def generate_diagnostic_report(
    timing: TimingCapture,
    events: list[EventRecord],
    step_results: list[dict],
) -> str:
    """Generate a Markdown diagnostic report."""
    lines: list[str] = ["# Portify Pipeline Diagnostic Report", ""]

    # Summary
    total = len(step_results)
    passed = sum(1 for s in step_results if s.get("status") == "pass")
    failed = total - passed

    lines += [
        "## Summary",
        f"- Steps executed: {total}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
        f"- Total duration: {timing.total_duration:.2f}s",
        "",
    ]

    # Step table
    if step_results:
        lines += ["## Steps", "", "| Step | Status | Duration |"]
        lines += ["|------|--------|----------|"]
        for sr in step_results:
            step = sr.get("step", "")
            status = sr.get("status", "")
            duration = sr.get("duration", 0.0)
            lines.append(f"| {step} | {status} | {duration:.2f}s |")
        lines.append("")

    # Event summary
    if events:
        lines += ["## Event Summary", ""]
        event_counts: dict[str, int] = {}
        for e in events:
            event_counts[e.event_type] = event_counts.get(e.event_type, 0) + 1
        for etype, count in sorted(event_counts.items()):
            lines.append(f"- {etype}: {count}")
        lines.append("")

    # Phase timings
    phase_data = {p: t for p, t in timing._phase_timings.items() if t.step_timings}
    if phase_data:
        lines += ["## Phase Timings", ""]
        for phase, pt in sorted(phase_data.items()):
            lines.append(f"### Phase {phase}")
            for st in pt.step_timings:
                lines.append(f"- {st.step}: {st.duration_seconds:.3f}s")
            lines.append("")

    return "\n".join(lines)
