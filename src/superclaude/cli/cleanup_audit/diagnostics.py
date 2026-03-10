"""Cleanup Audit diagnostics — failure classification, bundle collection, and reporting.

Provides post-failure analysis by collecting process state and output artifacts
into a structured diagnostic bundle.

Follows the sprint diagnostics pattern. See src/superclaude/cli/sprint/diagnostics.py.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .models import (
    CleanupAuditConfig,
    CleanupAuditMonitorState,
    CleanupAuditStatus,
    CleanupAuditStepResult,
)


class FailureCategory(Enum):
    """Classification of step failure root cause."""

    STALL = "stall"
    TIMEOUT = "timeout"
    CRASH = "crash"
    ERROR = "error"
    GATE_FAILURE = "gate_failure"
    UNKNOWN = "unknown"


@dataclass
class DiagnosticBundle:
    """Structured collection of diagnostic evidence for a failed step."""

    step_result: CleanupAuditStepResult
    category: FailureCategory = FailureCategory.UNKNOWN
    output_tail: str = ""
    stderr_tail: str = ""
    monitor_state_snapshot: Optional[dict] = None
    stall_duration: float = 0.0
    classification_evidence: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        """One-line summary of the diagnosis."""
        step_id = self.step_result.step.id if self.step_result.step else "unknown"
        return (
            f"Step {step_id}: {self.category.value} "
            f"(exit={self.step_result.exit_code}, "
            f"duration={self.step_result.duration_seconds:.1f}s)"
        )


class DiagnosticCollector:
    """Collects diagnostic evidence from various sources into a bundle."""

    def __init__(self, config: CleanupAuditConfig):
        self.config = config

    def collect(
        self,
        step_result: CleanupAuditStepResult,
        monitor_state: CleanupAuditMonitorState,
    ) -> DiagnosticBundle:
        """Collect all available diagnostic data for a failed step."""
        bundle = DiagnosticBundle(step_result=step_result)

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

        # Read output tail
        if step_result.step:
            output_file = self.config.work_dir / f"{step_result.step.id}-output.jsonl"
            if output_file.exists():
                bundle.output_tail = self._read_tail(output_file)

            error_file = self.config.work_dir / f"{step_result.step.id}-error.log"
            if error_file.exists():
                bundle.stderr_tail = self._read_tail(error_file)

        return bundle

    def _read_tail(self, path: Path, lines: int = 10) -> str:
        """Read the last N lines of a file."""
        try:
            all_lines = path.read_text(errors="replace").splitlines()
            return "\n".join(all_lines[-lines:])
        except OSError:
            return ""


class FailureClassifier:
    """Classifies step failures based on diagnostic evidence."""

    def classify(self, bundle: DiagnosticBundle) -> FailureCategory:
        """Determine the most likely failure category."""
        evidence = []
        status = bundle.step_result.status
        exit_code = bundle.step_result.exit_code

        # 1. Gate failure
        if bundle.step_result.gate_failure_reason:
            evidence.append(f"Gate failure: {bundle.step_result.gate_failure_reason}")
            bundle.classification_evidence = evidence
            return FailureCategory.GATE_FAILURE

        # 2. Stall detection
        if bundle.stall_duration > 120:
            evidence.append(f"High stall duration: {bundle.stall_duration:.0f}s")
            bundle.classification_evidence = evidence
            return FailureCategory.STALL

        # 3. Timeout
        if status == CleanupAuditStatus.TIMEOUT or exit_code == 124:
            evidence.append(f"Process timeout (exit code {exit_code})")
            bundle.classification_evidence = evidence
            return FailureCategory.TIMEOUT

        # 4. Crash
        if exit_code and exit_code != 0 and bundle.stall_duration < 30:
            evidence.append(
                f"Process crash (exit code {exit_code}, "
                f"stall {bundle.stall_duration:.0f}s)"
            )
            bundle.classification_evidence = evidence
            return FailureCategory.CRASH

        # 5. Error
        if status in (CleanupAuditStatus.HALT, CleanupAuditStatus.ERROR):
            evidence.append(f"Step status: {status.value}")
            bundle.classification_evidence = evidence
            return FailureCategory.ERROR

        # 6. Unknown
        evidence.append("No clear failure pattern identified")
        bundle.classification_evidence = evidence
        return FailureCategory.UNKNOWN


class ReportGenerator:
    """Generates human-readable diagnostic reports."""

    def generate(self, bundle: DiagnosticBundle) -> str:
        """Generate a structured diagnostic report from a bundle."""
        step_id = bundle.step_result.step.id if bundle.step_result.step else "unknown"
        lines = [
            f"# Diagnostic Report — Step {step_id}",
            "",
            "## Summary",
            f"- **Category**: {bundle.category.value}",
            f"- **Status**: {bundle.step_result.status.value}",
            f"- **Exit Code**: {bundle.step_result.exit_code}",
            f"- **Duration**: {bundle.step_result.duration_seconds:.1f}s",
            f"- **Stall Duration**: {bundle.stall_duration:.0f}s",
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

    def write(self, bundle: DiagnosticBundle, config: CleanupAuditConfig) -> None:
        """Write diagnostic report to file."""
        step_id = bundle.step_result.step.id if bundle.step_result.step else "unknown"
        output_path = config.work_dir / f"{step_id}-diagnostic.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = self.generate(bundle)
        output_path.write_text(report, encoding="utf-8")
