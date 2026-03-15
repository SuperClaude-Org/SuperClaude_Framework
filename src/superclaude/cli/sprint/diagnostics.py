"""Sprint diagnostics — failure classification, bundle collection, and reporting.

Provides post-failure analysis by collecting debug logs, process state,
and output artifacts into a structured diagnostic bundle. The failure
classifier assigns a category (stall, timeout, crash, error, unknown) based
on evidence from the debug log and process exit state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .models import MonitorState, Phase, PhaseResult, PhaseStatus, SprintConfig


class FailureCategory(Enum):
    """Classification of phase failure root cause."""

    STALL = "stall"
    TIMEOUT = "timeout"
    CRASH = "crash"
    ERROR = "error"
    UNKNOWN = "unknown"
    CONTEXT_EXHAUSTION = "context_exhaustion"


@dataclass
class DiagnosticBundle:
    """Structured collection of diagnostic evidence for a failed phase.

    Contains everything needed to understand why a phase failed:
    debug log entries, process state, output samples, and classified
    failure category.
    """

    phase: Phase
    phase_result: PhaseResult
    category: FailureCategory = FailureCategory.UNKNOWN
    debug_log_entries: list[str] = field(default_factory=list)
    last_events: list[str] = field(default_factory=list)
    output_tail: str = ""
    stderr_tail: str = ""
    monitor_state_snapshot: Optional[dict] = None
    watchdog_triggered: bool = False
    stall_duration: float = 0.0
    classification_evidence: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        """One-line summary of the diagnosis."""
        return (
            f"Phase {self.phase.number}: {self.category.value} "
            f"(exit={self.phase_result.exit_code}, "
            f"duration={self.phase_result.duration_display})"
        )


class DiagnosticCollector:
    """Collects diagnostic evidence from various sources into a bundle."""

    def __init__(self, config: SprintConfig):
        self.config = config

    def collect(
        self,
        phase: Phase,
        phase_result: PhaseResult,
        monitor_state: MonitorState,
    ) -> DiagnosticBundle:
        """Collect all available diagnostic data for a failed phase.

        Reads the debug log (if enabled), output and error files, and
        captures the monitor state snapshot.
        """
        bundle = DiagnosticBundle(
            phase=phase,
            phase_result=phase_result,
        )

        # Capture monitor state
        bundle.monitor_state_snapshot = {
            "output_bytes": monitor_state.output_bytes,
            "events_received": monitor_state.events_received,
            "stall_seconds": monitor_state.stall_seconds,
            "stall_status": monitor_state.stall_status,
            "last_task_id": monitor_state.last_task_id,
            "last_tool_used": monitor_state.last_tool_used,
            "files_changed": monitor_state.files_changed,
            "growth_rate_bps": monitor_state.growth_rate_bps,
        }
        bundle.stall_duration = monitor_state.stall_seconds

        # Read debug log entries for this phase
        if self.config.debug and self.config.debug_log_path.exists():
            bundle.debug_log_entries = self._read_phase_debug_entries(phase)
            bundle.watchdog_triggered = any(
                "watchdog_triggered" in entry
                for entry in bundle.debug_log_entries
            )
            # Extract last N events
            bundle.last_events = bundle.debug_log_entries[-20:]

        # Read output tail
        output_file = self.config.output_file(phase)
        if output_file.exists():
            bundle.output_tail = self._read_tail(output_file, lines=10)

        # Read stderr tail
        error_file = self.config.error_file(phase)
        if error_file.exists():
            bundle.stderr_tail = self._read_tail(error_file, lines=10)

        return bundle

    def _read_phase_debug_entries(self, phase: Phase) -> list[str]:
        """Read debug log entries relevant to this phase."""
        entries = []
        in_phase = False
        try:
            for line in self.config.debug_log_path.open():
                line = line.rstrip()
                if not line or line.startswith("#"):
                    continue
                if "PHASE_BEGIN" in line and f"phase={phase.number}" in line:
                    in_phase = True
                if in_phase:
                    entries.append(line)
                if "PHASE_END" in line and f"phase={phase.number}" in line:
                    break
        except OSError:
            pass
        return entries

    def _read_tail(self, path: Path, lines: int = 10) -> str:
        """Read the last N lines of a file."""
        try:
            all_lines = path.read_text(errors="replace").splitlines()
            return "\n".join(all_lines[-lines:])
        except OSError:
            return ""


class FailureClassifier:
    """Classifies phase failures based on diagnostic evidence."""

    def classify(self, bundle: DiagnosticBundle) -> FailureCategory:
        """Determine the most likely failure category.

        Classification priority:
        1. STALL: watchdog triggered or high stall duration
        2. TIMEOUT: exit code 124 (process timeout)
        3. CRASH: non-zero exit with low stall (subprocess died)
        4. ERROR: result file indicates error/halt
        5. UNKNOWN: no clear evidence
        """
        evidence = []
        status = bundle.phase_result.status
        exit_code = bundle.phase_result.exit_code

        # 1. Stall detection
        if bundle.watchdog_triggered:
            evidence.append("Watchdog triggered — stall detected by timeout")
            bundle.classification_evidence = evidence
            return FailureCategory.STALL

        if bundle.stall_duration > 120:
            evidence.append(f"High stall duration: {bundle.stall_duration:.0f}s")
            bundle.classification_evidence = evidence
            return FailureCategory.STALL

        # 2. Timeout
        if status == PhaseStatus.TIMEOUT or exit_code == 124:
            evidence.append(f"Process timeout (exit code {exit_code})")
            bundle.classification_evidence = evidence
            return FailureCategory.TIMEOUT

        # 2.5. Context exhaustion (prompt too long)
        from .monitor import detect_prompt_too_long

        output_file = bundle.phase_result.phase.file.parent.parent / "results" / f"phase-{bundle.phase_result.phase.number}-output.txt"
        if exit_code != 0 and detect_prompt_too_long(output_file):
            evidence.append(f"Context exhaustion detected (exit code {exit_code})")
            bundle.classification_evidence = evidence
            return FailureCategory.CONTEXT_EXHAUSTION

        # 3. Crash (non-zero exit, not timeout, low stall)
        if exit_code != 0 and bundle.stall_duration < 30:
            evidence.append(f"Process crash (exit code {exit_code}, stall {bundle.stall_duration:.0f}s)")
            bundle.classification_evidence = evidence
            return FailureCategory.CRASH

        # 4. Error (result file signals)
        if status in (PhaseStatus.HALT, PhaseStatus.ERROR):
            evidence.append(f"Phase status: {status.value}")
            bundle.classification_evidence = evidence
            return FailureCategory.ERROR

        # 5. Unknown
        evidence.append("No clear failure pattern identified")
        bundle.classification_evidence = evidence
        return FailureCategory.UNKNOWN


class ReportGenerator:
    """Generates human-readable diagnostic reports."""

    def generate(self, bundle: DiagnosticBundle) -> str:
        """Generate a structured diagnostic report from a bundle."""
        lines = [
            f"# Diagnostic Report — Phase {bundle.phase.number}",
            "",
            "## Summary",
            f"- **Category**: {bundle.category.value}",
            f"- **Status**: {bundle.phase_result.status.value}",
            f"- **Exit Code**: {bundle.phase_result.exit_code}",
            f"- **Duration**: {bundle.phase_result.duration_display}",
            f"- **Stall Duration**: {bundle.stall_duration:.0f}s",
            f"- **Watchdog Triggered**: {bundle.watchdog_triggered}",
            "",
            "## Evidence",
        ]

        for ev in bundle.classification_evidence:
            lines.append(f"- {ev}")

        if bundle.monitor_state_snapshot:
            lines.append("")
            lines.append("## Monitor State")
            for k, v in bundle.monitor_state_snapshot.items():
                lines.append(f"- **{k}**: {v}")

        if bundle.last_events:
            lines.append("")
            lines.append("## Last Debug Events")
            lines.append("```")
            for entry in bundle.last_events[-10:]:
                lines.append(entry)
            lines.append("```")

        if bundle.output_tail:
            lines.append("")
            lines.append("## Output Tail")
            lines.append("```")
            lines.append(bundle.output_tail)
            lines.append("```")

        if bundle.stderr_tail:
            lines.append("")
            lines.append("## Stderr Tail")
            lines.append("```")
            lines.append(bundle.stderr_tail)
            lines.append("```")

        return "\n".join(lines)

    def write(self, bundle: DiagnosticBundle, output_path: Path) -> None:
        """Write diagnostic report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = self.generate(bundle)
        output_path.write_text(report, encoding="utf-8")
