"""Return contract emission for cli-portify pipeline.

Per D-0002 Ownership Boundary 5 (Contract Emission): produces Phase
Contracts schema on all exit paths (success/partial/failed/dry_run).

NFR-009: All failure paths must produce populated contract objects.
No exit path may produce an empty or null contract.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from .models import PortifyOutcome, PortifyStepResult, PortifyStatus


class ContractStatus(Enum):
    """Contract emission status aligned with D-0003 Artifact 8."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    DRY_RUN = "dry_run"


@dataclass
class PhaseStatus:
    """Status of a single pipeline phase within the contract."""

    phase: int
    name: str
    status: str = "pending"
    steps_completed: int = 0
    steps_total: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "name": self.name,
            "status": self.status,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
        }


@dataclass
class StepTiming:
    """Timing data for a single step."""

    step: str
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"step": self.step, "duration_seconds": self.duration_seconds}


@dataclass
class PortifyContract:
    """Return contract emitted on all exit paths.

    Per D-0003 Artifact 8:
    - Required fields: status, phases, artifacts, resume_command, timing
    - Failure Default (NFR-009): status: "failed", all phase statuses
      populated with last-known state, artifacts: [], resume_command
      generated for resumable failures.
    """

    status: ContractStatus = ContractStatus.FAILED
    phases: list[PhaseStatus] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    resume_command: str = ""
    timing: dict[str, Any] = field(default_factory=dict)
    step_timings: list[StepTiming] = field(default_factory=list)
    gate_results: dict[str, str] = field(default_factory=dict)
    error_message: str = ""

    def __post_init__(self) -> None:
        """Ensure default phases are populated if empty."""
        if not self.phases:
            self.phases = _default_phases()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON output."""
        return {
            "status": self.status.value,
            "phases": [p.to_dict() for p in self.phases],
            "artifacts": self.artifacts,
            "resume_command": self.resume_command,
            "timing": self.timing,
            "step_timings": [t.to_dict() for t in self.step_timings],
            "gate_results": self.gate_results,
            "error_message": self.error_message,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def _default_phases() -> list[PhaseStatus]:
    """Generate default phase statuses for the 7-step pipeline.

    Maps to the conceptual phases of the portify pipeline:
    - Phase 1: Config validation (Steps 1-2, deterministic)
    - Phase 2: Workflow analysis (Steps 3-4, Claude-assisted)
    - Phase 3: Spec synthesis (Step 5, Claude-assisted)
    - Phase 4: Gap analysis and review (Steps 6-7, Claude-assisted)
    """
    return [
        PhaseStatus(phase=1, name="config-validation", steps_total=2),
        PhaseStatus(phase=2, name="workflow-analysis", steps_total=2),
        PhaseStatus(phase=3, name="spec-synthesis", steps_total=1),
        PhaseStatus(phase=4, name="review-convergence", steps_total=2),
    ]


# --- Contract Builders ---


def build_success_contract(
    artifacts: list[str],
    step_timings: list[StepTiming],
    gate_results: dict[str, str],
    total_duration: float,
) -> PortifyContract:
    """Build a contract for successful pipeline completion."""
    phases = _default_phases()
    for p in phases:
        p.status = "completed"
        p.steps_completed = p.steps_total
    return PortifyContract(
        status=ContractStatus.SUCCESS,
        phases=phases,
        artifacts=artifacts,
        resume_command="",
        timing={"total_seconds": total_duration},
        step_timings=step_timings,
        gate_results=gate_results,
    )


def build_partial_contract(
    step_results: list[PortifyStepResult],
    artifacts: list[str],
    step_timings: list[StepTiming],
    gate_results: dict[str, str],
    total_duration: float,
    resume_step: str = "",
) -> PortifyContract:
    """Build a contract for partial (ESCALATED) pipeline completion."""
    phases = _build_phases_from_results(step_results)
    resume_cmd = generate_resume_command(resume_step) if resume_step else ""
    return PortifyContract(
        status=ContractStatus.PARTIAL,
        phases=phases,
        artifacts=artifacts,
        resume_command=resume_cmd,
        timing={"total_seconds": total_duration},
        step_timings=step_timings,
        gate_results=gate_results,
    )


def build_failed_contract(
    step_results: list[PortifyStepResult],
    artifacts: list[str],
    step_timings: list[StepTiming],
    gate_results: dict[str, str],
    total_duration: float,
    error_message: str = "",
    resume_step: str = "",
) -> PortifyContract:
    """Build a contract for failed pipeline execution.

    NFR-009: All phase statuses populated with last-known state.
    """
    phases = _build_phases_from_results(step_results)
    resume_cmd = generate_resume_command(resume_step) if resume_step else ""
    return PortifyContract(
        status=ContractStatus.FAILED,
        phases=phases,
        artifacts=artifacts,
        resume_command=resume_cmd,
        timing={"total_seconds": total_duration},
        step_timings=step_timings,
        gate_results=gate_results,
        error_message=error_message,
    )


def build_dry_run_contract(
    step_results: list[PortifyStepResult],
    artifacts: list[str],
    step_timings: list[StepTiming],
    total_duration: float,
) -> PortifyContract:
    """Build a contract for dry-run termination.

    Per D-0003: dry_run contracts mark phases 3-4 as ``skipped``.
    """
    phases = _default_phases()
    # Phases 1-2 completed (config validation + deterministic steps)
    for p in phases[:2]:
        p.status = "completed"
        p.steps_completed = p.steps_total
    # Phases 3-4 skipped (Claude-assisted steps)
    for p in phases[2:]:
        p.status = "skipped"
    return PortifyContract(
        status=ContractStatus.DRY_RUN,
        phases=phases,
        artifacts=artifacts,
        resume_command="",
        timing={"total_seconds": total_duration},
        step_timings=step_timings,
    )


# --- Resume Command Generation ---

# Steps 5-7 are resumable per the tasklist spec
RESUMABLE_STEPS = {
    "synthesize-spec": 5,
    "brainstorm-gaps": 6,
    "panel-review": 7,
}


def generate_resume_command(
    failed_step: str,
    suggested_budget: int | None = None,
) -> str:
    """Generate a ``--start`` command for resumable failure steps.

    Args:
        failed_step: The step name that failed.
        suggested_budget: Suggested max_convergence for remaining work.

    Returns:
        A CLI command string for resuming, or empty string if step
        is not resumable.
    """
    if failed_step not in RESUMABLE_STEPS:
        return ""
    cmd = f"superclaude cli-portify run <workflow_path> --start {failed_step}"
    if suggested_budget is not None:
        cmd += f" --max-convergence {suggested_budget}"
    return cmd


# --- Internal Helpers ---

# Step-to-phase mapping
_STEP_PHASE_MAP = {
    "validate-config": 1,
    "discover-components": 1,
    "analyze-workflow": 2,
    "design-pipeline": 2,
    "synthesize-spec": 3,
    "brainstorm-gaps": 4,
    "panel-review": 4,
}


def _build_phases_from_results(
    step_results: list[PortifyStepResult],
) -> list[PhaseStatus]:
    """Build phase statuses from step results, preserving last-known state."""
    phases = _default_phases()
    phase_map = {p.phase: p for p in phases}

    for sr in step_results:
        phase_num = _STEP_PHASE_MAP.get(sr.step_name, 0)
        if phase_num == 0:
            continue
        phase = phase_map.get(phase_num)
        if phase is None:
            continue
        if sr.portify_status in (PortifyStatus.PASS,):
            phase.steps_completed += 1
        # Set phase status based on highest step status
        if sr.portify_status == PortifyStatus.FAIL:
            phase.status = "failed"
        elif sr.portify_status == PortifyStatus.TIMEOUT:
            phase.status = "timeout"
        elif sr.portify_status == PortifyStatus.PASS and phase.status == "pending":
            phase.status = "in_progress"

    # Mark completed phases
    for p in phases:
        if p.steps_completed == p.steps_total and p.status not in ("failed", "timeout"):
            p.status = "completed"

    return phases
