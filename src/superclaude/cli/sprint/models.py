"""Sprint data models — enums, dataclasses, and pure-data types.

All other sprint modules depend on these types. This file has zero
external dependencies beyond the stdlib.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class PhaseStatus(Enum):
    """Lifecycle of a single phase."""

    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    # SKIPPED removed — was never returned by _determine_phase_status and
    # created an orphaned terminal state that was neither success nor failure,
    # causing SprintOutcome.ERROR if accidentally used.

    @property
    def is_terminal(self) -> bool:
        return self in (
            PhaseStatus.PASS,
            PhaseStatus.PASS_NO_SIGNAL,
            PhaseStatus.PASS_NO_REPORT,
            PhaseStatus.HALT,
            PhaseStatus.TIMEOUT,
            PhaseStatus.ERROR,
        )

    @property
    def is_success(self) -> bool:
        return self in (
            PhaseStatus.PASS,
            PhaseStatus.PASS_NO_SIGNAL,
            PhaseStatus.PASS_NO_REPORT,
        )

    @property
    def is_failure(self) -> bool:
        return self in (PhaseStatus.HALT, PhaseStatus.TIMEOUT, PhaseStatus.ERROR)


class SprintOutcome(Enum):
    """Final sprint result."""

    SUCCESS = "success"
    HALTED = "halted"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class Phase:
    """A single phase discovered from the tasklist index."""

    number: int
    file: Path
    name: str = ""  # extracted from phase file heading, or auto-generated

    @property
    def basename(self) -> str:
        return self.file.name

    @property
    def display_name(self) -> str:
        return self.name or f"Phase {self.number}"


@dataclass
class SprintConfig:
    """Complete configuration for a sprint execution."""

    index_path: Path
    release_dir: Path
    phases: list[Phase]
    start_phase: int = 1
    end_phase: int = 0  # 0 = auto-detect (last phase)
    max_turns: int = 50
    model: str = ""  # empty = claude default
    dry_run: bool = False
    permission_flag: str = "--dangerously-skip-permissions"
    tmux_session_name: str = ""

    @property
    def results_dir(self) -> Path:
        return self.release_dir / "results"

    @property
    def execution_log_jsonl(self) -> Path:
        return self.release_dir / "execution-log.jsonl"

    @property
    def execution_log_md(self) -> Path:
        return self.release_dir / "execution-log.md"

    @property
    def active_phases(self) -> list[Phase]:
        """Phases within the [start, end] range."""
        end = self.end_phase or max(p.number for p in self.phases)
        return [p for p in self.phases if self.start_phase <= p.number <= end]

    def output_file(self, phase: Phase) -> Path:
        return self.results_dir / f"phase-{phase.number}-output.txt"

    def error_file(self, phase: Phase) -> Path:
        return self.results_dir / f"phase-{phase.number}-errors.txt"

    def result_file(self, phase: Phase) -> Path:
        return self.results_dir / f"phase-{phase.number}-result.md"


@dataclass
class PhaseResult:
    """Outcome of executing a single phase."""

    phase: Phase
    status: PhaseStatus
    exit_code: int
    started_at: datetime
    finished_at: datetime
    output_bytes: int = 0
    error_bytes: int = 0
    last_task_id: str = ""
    files_changed: int = 0

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()

    @property
    def duration_display(self) -> str:
        s = int(self.duration_seconds)
        if s < 60:
            return f"{s}s"
        return f"{s // 60}m {s % 60}s"


@dataclass
class SprintResult:
    """Aggregate result for the entire sprint."""

    config: SprintConfig
    phase_results: list[PhaseResult] = field(default_factory=list)
    outcome: SprintOutcome = SprintOutcome.SUCCESS
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None
    halt_phase: Optional[int] = None

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or datetime.now(timezone.utc)
        return (end - self.started_at).total_seconds()

    @property
    def duration_display(self) -> str:
        s = int(self.duration_seconds)
        if s < 3600:
            return f"{s // 60}m {s % 60}s"
        return f"{s // 3600}h {(s % 3600) // 60}m"

    @property
    def phases_passed(self) -> int:
        return sum(1 for r in self.phase_results if r.status.is_success)

    @property
    def phases_failed(self) -> int:
        return sum(1 for r in self.phase_results if r.status.is_failure)

    def resume_command(self) -> str:
        if self.halt_phase is not None:
            end = self.config.end_phase or max(
                p.number for p in self.config.phases
            )
            return (
                f"superclaude sprint run {self.config.index_path} "
                f"--start {self.halt_phase} --end {end}"
            )
        return ""


@dataclass
class MonitorState:
    """Real-time state extracted by the sidecar monitor thread."""

    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = field(default_factory=time.monotonic)
    last_task_id: str = ""
    last_tool_used: str = ""
    files_changed: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0  # bytes per second
    stall_seconds: float = 0.0

    @property
    def stall_status(self) -> str:
        if self.stall_seconds > 60:
            return "STALLED"
        if self.stall_seconds > 30:
            return "thinking..."
        return "active"

    @property
    def output_size_display(self) -> str:
        if self.output_bytes < 1024:
            return f"{self.output_bytes} B"
        if self.output_bytes < 1024 * 1024:
            return f"{self.output_bytes / 1024:.1f} KB"
        return f"{self.output_bytes / (1024 * 1024):.1f} MB"
