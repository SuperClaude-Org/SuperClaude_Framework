"""Domain models for Cleanup Audit pipeline.

Extends shared pipeline base types with CleanupAudit-specific
status tracking, configuration, and result telemetry.

Source workflow: sc-cleanup-audit-protocol
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from superclaude.cli.pipeline.models import (
    GateCriteria,
    GateMode,
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)


# --- Enums ---


class CleanupAuditStatus(Enum):
    """Step-level status for Cleanup Audit pipeline.

    Extends generic StepStatus with domain-specific states.
    """

    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    INCOMPLETE = "incomplete"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"


class CleanupAuditOutcome(Enum):
    """Aggregate pipeline outcome."""

    SUCCESS = "success"
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"


class AuditPassType(Enum):
    """Classification of audit pass types."""

    SURFACE = "surface"
    STRUCTURAL = "structural"
    CROSS_CUTTING = "cross_cutting"
    CONSOLIDATION = "consolidation"
    VALIDATION = "validation"


# --- Configuration ---


@dataclass
class CleanupAuditConfig(PipelineConfig):
    """Cleanup Audit pipeline configuration.

    Extends PipelineConfig with audit-specific settings.
    """

    target_path: Path = field(default_factory=lambda: Path("."))
    pass_selection: str = "all"
    batch_size: int = 20
    focus: str = "all"
    stall_timeout: int = 300
    stall_action: str = "kill"
    output_dir: Path = field(default_factory=lambda: Path("."))

    def __post_init__(self):
        """Ensure work_dir is set from pipeline-specific paths."""
        if not self.work_dir or self.work_dir == Path("."):
            self.work_dir = self.output_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)

    @property
    def results_dir(self) -> Path:
        return self.work_dir / "results"

    @property
    def artifacts_dir(self) -> Path:
        return self.work_dir / "artifacts"

    @property
    def execution_log_jsonl(self) -> Path:
        return self.work_dir / "execution-log.jsonl"

    @property
    def execution_log_md(self) -> Path:
        return self.work_dir / "execution-log.md"


# --- Step Specialization ---


@dataclass
class CleanupAuditStep(Step):
    """Cleanup Audit-specific step with domain metadata."""

    pass_type: AuditPassType = AuditPassType.SURFACE
    batch_index: int = 0
    batch_total: int = 1
    agent_type: str = ""


# --- Result Types ---


@dataclass
class CleanupAuditStepResult(StepResult):
    """Result for a single Cleanup Audit step.

    Extends StepResult with execution telemetry.
    """

    status: CleanupAuditStatus = CleanupAuditStatus.PENDING
    exit_code: int | None = None
    started_at: float | None = None
    finished_at: float | None = None
    output_bytes: int = 0
    error_bytes: int = 0
    finding_count: int = 0
    severity_distribution: dict[str, int] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return 0.0


@dataclass
class CleanupAuditResult:
    """Aggregate result for the entire Cleanup Audit pipeline."""

    config: CleanupAuditConfig
    step_results: list[CleanupAuditStepResult] = field(default_factory=list)
    outcome: CleanupAuditOutcome = CleanupAuditOutcome.SUCCESS
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    halt_step: str | None = None

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or time.time()
        return end - self.started_at

    @property
    def steps_passed(self) -> int:
        return sum(
            1
            for r in self.step_results
            if r.status
            in (CleanupAuditStatus.PASS, CleanupAuditStatus.PASS_NO_SIGNAL)
        )

    @property
    def steps_failed(self) -> int:
        return sum(
            1
            for r in self.step_results
            if r.status
            in (
                CleanupAuditStatus.HALT,
                CleanupAuditStatus.ERROR,
                CleanupAuditStatus.TIMEOUT,
            )
        )

    def resume_command(self) -> str | None:
        """Generate CLI command to resume from the failed step."""
        if self.halt_step:
            return f"superclaude cleanup-audit run --resume --start {self.halt_step}"
        return None


# --- Monitor State ---


@dataclass
class CleanupAuditMonitorState:
    """Live execution state fed by the output monitor."""

    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = 0.0
    last_event_time: float = 0.0
    step_started_at: float = 0.0
    events_received: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0
    stall_seconds: float = 0.0
    last_task_id: str = ""
    last_tool_used: str = ""
    files_changed: int = 0
    findings_detected: int = 0

    @property
    def stall_status(self) -> str:
        if self.events_received == 0:
            elapsed = (
                time.time() - self.step_started_at if self.step_started_at else 0
            )
            return "waiting..." if elapsed < 30 else "STALLED"
        if self.stall_seconds > 120:
            return "STALLED"
        if self.stall_seconds > 30:
            return "thinking..."
        return "active"

    @property
    def output_size_display(self) -> str:
        if self.output_bytes < 1024:
            return f"{self.output_bytes}B"
        return f"{self.output_bytes / 1024:.1f}KB"
