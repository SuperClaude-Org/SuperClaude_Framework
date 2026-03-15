"""Sprint data models — enums, dataclasses, and pure-data types.

All other sprint modules depend on these types. Pipeline base types
(PipelineConfig, Step, StepResult, StepStatus) are imported from
superclaude.cli.pipeline for inheritance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from superclaude.cli.pipeline.models import (
    PipelineConfig,
    Step,
    StepResult,
    StepStatus,
)


@dataclass
class TaskEntry:
    """A single task parsed from a phase tasklist markdown file.

    Represents one ``### T<PP>.<TT> -- Title`` block with its metadata.
    """

    task_id: str
    title: str
    description: str = ""
    dependencies: list[str] = field(default_factory=list)


class TaskStatus(Enum):
    """Outcome status for a single task within a phase."""

    PASS = "pass"
    FAIL = "fail"
    INCOMPLETE = "incomplete"
    SKIPPED = "skipped"

    @property
    def is_success(self) -> bool:
        return self == TaskStatus.PASS

    @property
    def is_failure(self) -> bool:
        return self in (TaskStatus.FAIL, TaskStatus.INCOMPLETE)


class GateOutcome(Enum):
    """Outcome of a quality gate check for a task."""

    PASS = "pass"
    FAIL = "fail"
    DEFERRED = "deferred"
    PENDING = "pending"

    @property
    def is_success(self) -> bool:
        return self == GateOutcome.PASS


class GateDisplayState(Enum):
    """Visual state for gate status in the TUI phase table.

    Maps gate lifecycle stages to distinct display properties (color, icon, label)
    for at-a-glance feedback on trailing gate progress.

    Valid transitions:
        NONE → CHECKING → PASS
        NONE → CHECKING → FAIL_DEFERRED → REMEDIATING → REMEDIATED
        NONE → CHECKING → FAIL_DEFERRED → REMEDIATING → HALT
    """

    NONE = "none"
    CHECKING = "checking"
    PASS = "pass"
    FAIL_DEFERRED = "fail_deferred"
    REMEDIATING = "remediating"
    REMEDIATED = "remediated"
    HALT = "halt"

    @property
    def color(self) -> str:
        """Rich style string for TUI rendering."""
        return _GATE_DISPLAY_COLORS[self]

    @property
    def icon(self) -> str:
        """Short icon/label for TUI column rendering."""
        return _GATE_DISPLAY_ICONS[self]

    @property
    def label(self) -> str:
        """Human-readable label for reports."""
        return _GATE_DISPLAY_LABELS[self]


# Valid transitions: frozenset of (from_state, to_state) pairs
GATE_DISPLAY_TRANSITIONS: frozenset[tuple[GateDisplayState, GateDisplayState]] = frozenset({
    (GateDisplayState.NONE, GateDisplayState.CHECKING),
    (GateDisplayState.CHECKING, GateDisplayState.PASS),
    (GateDisplayState.CHECKING, GateDisplayState.FAIL_DEFERRED),
    (GateDisplayState.FAIL_DEFERRED, GateDisplayState.REMEDIATING),
    (GateDisplayState.REMEDIATING, GateDisplayState.REMEDIATED),
    (GateDisplayState.REMEDIATING, GateDisplayState.HALT),
})


def is_valid_gate_transition(from_state: GateDisplayState, to_state: GateDisplayState) -> bool:
    """Check whether a gate display state transition is valid."""
    return (from_state, to_state) in GATE_DISPLAY_TRANSITIONS


_GATE_DISPLAY_COLORS: dict[GateDisplayState, str] = {
    GateDisplayState.NONE: "dim",
    GateDisplayState.CHECKING: "bold cyan",
    GateDisplayState.PASS: "bold green",
    GateDisplayState.FAIL_DEFERRED: "bold yellow",
    GateDisplayState.REMEDIATING: "bold magenta",
    GateDisplayState.REMEDIATED: "green",
    GateDisplayState.HALT: "bold red",
}

_GATE_DISPLAY_ICONS: dict[GateDisplayState, str] = {
    GateDisplayState.NONE: "[dim]—[/]",
    GateDisplayState.CHECKING: "[cyan]⏳[/]",
    GateDisplayState.PASS: "[green]✓[/]",
    GateDisplayState.FAIL_DEFERRED: "[yellow]⚠[/]",
    GateDisplayState.REMEDIATING: "[magenta]🔧[/]",
    GateDisplayState.REMEDIATED: "[green]✓✓[/]",
    GateDisplayState.HALT: "[red]✗[/]",
}

_GATE_DISPLAY_LABELS: dict[GateDisplayState, str] = {
    GateDisplayState.NONE: "No gate",
    GateDisplayState.CHECKING: "Checking",
    GateDisplayState.PASS: "Passed",
    GateDisplayState.FAIL_DEFERRED: "Deferred",
    GateDisplayState.REMEDIATING: "Remediating",
    GateDisplayState.REMEDIATED: "Remediated",
    GateDisplayState.HALT: "Halted",
}


@dataclass
class TaskResult:
    """Outcome of executing a single task subprocess.

    Constructed by the runner from subprocess output — not agent self-reported.
    Includes execution data, gate outcome, and reimbursement tracking.
    """

    task: TaskEntry
    status: TaskStatus = TaskStatus.SKIPPED
    turns_consumed: int = 0
    exit_code: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    output_bytes: int = 0
    gate_outcome: GateOutcome = GateOutcome.PENDING
    reimbursement_amount: int = 0
    output_path: str = ""

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()

    def to_context_summary(self, *, verbose: bool = True) -> str:
        """Serialize to structured markdown for context injection.

        Args:
            verbose: If True, include full detail. If False, produce a
                compressed one-line summary for progressive summarization.

        Returns:
            Deterministic markdown string suitable for context injection.
        """
        if not verbose:
            return (
                f"- **{self.task.task_id}**: {self.status.value} "
                f"| gate: {self.gate_outcome.value}"
            )
        lines = [
            f"### {self.task.task_id} — {self.task.title}",
            f"- **Status**: {self.status.value}",
            f"- **Gate**: {self.gate_outcome.value}",
            f"- **Turns consumed**: {self.turns_consumed}",
            f"- **Duration**: {self.duration_seconds:.1f}s",
            f"- **Exit code**: {self.exit_code}",
        ]
        if self.reimbursement_amount > 0:
            lines.append(f"- **Reimbursement**: {self.reimbursement_amount} turns")
        if self.output_path:
            lines.append(f"- **Output**: {self.output_path}")
        return "\n".join(lines)


class PhaseStatus(Enum):
    """Lifecycle of a single phase."""

    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    PASS_NO_SIGNAL = "pass_no_signal"
    PASS_NO_REPORT = "pass_no_report"
    PASS_RECOVERED = "pass_recovered"  # non-zero exit but evidence of success
    INCOMPLETE = "incomplete"
    HALT = "halt"
    TIMEOUT = "timeout"
    ERROR = "error"
    SKIPPED = "skipped"

    @property
    def is_terminal(self) -> bool:
        return self in (
            PhaseStatus.PASS,
            PhaseStatus.PASS_NO_SIGNAL,
            PhaseStatus.PASS_NO_REPORT,
            PhaseStatus.PASS_RECOVERED,
            PhaseStatus.INCOMPLETE,
            PhaseStatus.HALT,
            PhaseStatus.TIMEOUT,
            PhaseStatus.ERROR,
            PhaseStatus.SKIPPED,
        )

    @property
    def is_success(self) -> bool:
        return self in (
            PhaseStatus.PASS,
            PhaseStatus.PASS_NO_SIGNAL,
            PhaseStatus.PASS_NO_REPORT,
            PhaseStatus.PASS_RECOVERED,
        )

    @property
    def is_failure(self) -> bool:
        return self in (PhaseStatus.INCOMPLETE, PhaseStatus.HALT, PhaseStatus.TIMEOUT, PhaseStatus.ERROR)


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
class SprintConfig(PipelineConfig):
    """Complete configuration for a sprint execution.

    Inherits shared fields from PipelineConfig (work_dir, dry_run,
    max_turns, model, permission_flag, debug). Sprint-specific fields
    are defined here. The ``release_dir`` field maps to ``work_dir``
    via __post_init__ for backward compatibility.
    """

    index_path: Path = field(default_factory=lambda: Path("."))
    release_dir: Path = field(default_factory=lambda: Path("."))
    phases: list[Phase] = field(default_factory=list)
    start_phase: int = 1
    end_phase: int = 0  # 0 = auto-detect (last phase)
    max_turns: int = 100
    model: str = ""  # empty = claude default
    dry_run: bool = False
    permission_flag: str = "--dangerously-skip-permissions"
    tmux_session_name: str = ""
    # Diagnostic fields (all default to pre-change behavior)
    debug: bool = False
    stall_timeout: int = 0  # 0 = disabled
    stall_action: str = "warn"  # "warn" or "kill"
    phase_timeout: int = 0  # 0 = disabled
    # Shadow mode: trailing gates run in parallel, results are metrics-only
    shadow_gates: bool = False

    def __post_init__(self):
        # Sync release_dir to PipelineConfig.work_dir so both access paths
        # return the same value.
        object.__setattr__(self, "work_dir", self.release_dir)

    @property
    def debug_log_path(self) -> Path:
        """Path to the debug log file within the results directory."""
        return self.results_dir / "debug.log"

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
class SprintStep(Step):
    """A pipeline step specialised for sprint phase execution.

    Extends pipeline.Step with sprint-specific fields.
    """

    phase_number: int = 0


@dataclass
class PhaseResult(StepResult):
    """Outcome of executing a single phase.

    Inherits from pipeline.StepResult for shared timing fields.
    Sprint-specific fields (phase, exit_code, etc.) are defined here.
    """

    phase: Phase = field(default_factory=lambda: Phase(number=0, file=Path(".")))
    status: PhaseStatus = PhaseStatus.PENDING
    exit_code: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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
    """Real-time state extracted by the sidecar monitor thread.

    With stream-json output, liveness is tracked via ``last_event_time``
    (updated on each parsed NDJSON line) rather than raw byte growth.
    """

    output_bytes: int = 0
    output_bytes_prev: int = 0
    last_growth_time: float = field(default_factory=time.monotonic)
    last_event_time: float = field(default_factory=time.monotonic)
    phase_started_at: float = field(default_factory=time.monotonic)
    events_received: int = 0
    last_task_id: str = ""
    last_tool_used: str = ""
    files_changed: int = 0
    lines_total: int = 0
    growth_rate_bps: float = 0.0  # bytes per second
    stall_seconds: float = 0.0

    @property
    def stall_status(self) -> str:
        now = time.monotonic()
        if self.events_received == 0:
            # No events yet — subprocess is starting up
            if now - self.phase_started_at > 120:
                return "STALLED"
            return "waiting..."
        # Events have been flowing — check time since last event
        since_last = now - self.last_event_time
        if since_last > 120:
            return "STALLED"
        if since_last > 30:
            return "thinking..."
        return "active"

    @property
    def output_size_display(self) -> str:
        if self.output_bytes < 1024:
            return f"{self.output_bytes} B"
        if self.output_bytes < 1024 * 1024:
            return f"{self.output_bytes / 1024:.1f} KB"
        return f"{self.output_bytes / (1024 * 1024):.1f} MB"


@dataclass
class TurnLedger:
    """Economic model for subprocess turn budget tracking.

    Tracks budget allocation, consumption, and reimbursement for sprint
    subprocesses. Enforces monotonicity: consumed can only increase.
    """

    initial_budget: int
    consumed: int = 0
    reimbursed: int = 0
    reimbursement_rate: float = 0.8
    minimum_allocation: int = 5
    minimum_remediation_budget: int = 3

    def available(self) -> int:
        """Return available turns: initial_budget - consumed + reimbursed."""
        return self.initial_budget - self.consumed + self.reimbursed

    def debit(self, turns: int) -> None:
        """Consume turns from the budget. Enforces monotonicity."""
        if turns < 0:
            raise ValueError("debit amount must be non-negative")
        self.consumed += turns

    def credit(self, turns: int) -> None:
        """Reimburse turns to the budget."""
        if turns < 0:
            raise ValueError("credit amount must be non-negative")
        self.reimbursed += turns

    def can_launch(self) -> bool:
        """Return True if enough budget remains for a subprocess launch."""
        return self.available() >= self.minimum_allocation

    def can_remediate(self) -> bool:
        """Return True if enough budget remains for remediation."""
        return self.available() >= self.minimum_remediation_budget


def build_resume_output(
    config: SprintConfig,
    halt_task_id: str,
    remaining_tasks: list[TaskEntry],
    diagnostic_path: str | None = None,
    ledger: TurnLedger | None = None,
) -> str:
    """Build actionable HALT output with resume command and context.

    Produces an actionable resume block containing:
    - Resume command with exact task ID
    - Remaining tasks in execution order
    - Diagnostic output reference (if available)
    - Budget suggestion based on remaining work

    Args:
        config: Sprint configuration.
        halt_task_id: The first uncompleted task ID.
        remaining_tasks: Tasks not yet attempted, in execution order.
        diagnostic_path: Path to diagnostic output (if chain produced results).
        ledger: TurnLedger for budget suggestion.

    Returns:
        Formatted HALT output string.
    """
    remaining_count = len(remaining_tasks)
    budget_suggestion = max(remaining_count * 10, 50) if remaining_count > 0 else 0

    lines = [
        "## HALT — Sprint Paused",
        "",
        "### Resume Command",
        f"```",
        f"superclaude sprint run {config.index_path} --resume {halt_task_id} --budget {budget_suggestion}",
        f"```",
        "",
        f"### Remaining Tasks ({remaining_count})",
    ]

    for task in remaining_tasks:
        lines.append(f"- {task.task_id}: {task.title}")

    if diagnostic_path:
        lines.append("")
        lines.append("### Diagnostic Output")
        lines.append(f"See: {diagnostic_path}")

    if ledger:
        lines.append("")
        lines.append("### Budget Status")
        lines.append(f"- Consumed: {ledger.consumed} turns")
        lines.append(f"- Available: {ledger.available()} turns")
        lines.append(f"- Suggested budget for resume: {budget_suggestion} turns")

    return "\n".join(lines)


@dataclass
class ShadowGateMetrics:
    """Aggregated metrics from shadow gate evaluation.

    Collected when ``--shadow-gates`` is enabled. Shadow metrics are
    informational only and do not affect sprint behavior.
    """

    total_evaluated: int = 0
    passed: int = 0
    failed: int = 0
    latency_ms: list[float] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        """Fraction of gates that passed (0.0–1.0)."""
        if self.total_evaluated == 0:
            return 0.0
        return self.passed / self.total_evaluated

    @property
    def p50_latency_ms(self) -> float:
        """Median gate evaluation latency in milliseconds."""
        if not self.latency_ms:
            return 0.0
        s = sorted(self.latency_ms)
        mid = len(s) // 2
        if len(s) % 2 == 0:
            return (s[mid - 1] + s[mid]) / 2
        return s[mid]

    @property
    def p95_latency_ms(self) -> float:
        """95th percentile gate evaluation latency in milliseconds."""
        if not self.latency_ms:
            return 0.0
        s = sorted(self.latency_ms)
        idx = int(len(s) * 0.95)
        return s[min(idx, len(s) - 1)]

    def record(self, passed: bool, evaluation_ms: float) -> None:
        """Record a single shadow gate result."""
        self.total_evaluated += 1
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.latency_ms.append(evaluation_ms)
