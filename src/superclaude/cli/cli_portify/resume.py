"""Resume semantics for cli-portify pipeline.

Defines the resumability matrix, resume command generation with
budget suggestions, and prior-context injection for pipeline re-entry.

Resumable steps (5-7): synthesize-spec, brainstorm-gaps, panel-review
Non-resumable steps (1-4): validate-config, discover-components,
  analyze-workflow, design-pipeline

Per D-0037 (resumability matrix), D-0038 (resume commands / SC-014),
D-0052 (prior-context injection).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStepResult,
    PortifyStatus,
    ResumeContext,
)


# --- Resumability Matrix (D-0037) ---


@dataclass(frozen=True)
class ResumeEntryPoint:
    """Defines resume requirements for a single step."""

    step_name: str
    step_number: int
    resumable: bool
    required_artifacts: tuple[str, ...]
    preserved_context: tuple[str, ...]


RESUMABILITY_MATRIX: dict[str, ResumeEntryPoint] = {
    "validate-config": ResumeEntryPoint(
        step_name="validate-config",
        step_number=1,
        resumable=False,
        required_artifacts=(),
        preserved_context=(),
    ),
    "discover-components": ResumeEntryPoint(
        step_name="discover-components",
        step_number=2,
        resumable=False,
        required_artifacts=(),
        preserved_context=(),
    ),
    "analyze-workflow": ResumeEntryPoint(
        step_name="analyze-workflow",
        step_number=3,
        resumable=False,
        required_artifacts=("component-inventory.md",),
        preserved_context=(),
    ),
    "design-pipeline": ResumeEntryPoint(
        step_name="design-pipeline",
        step_number=4,
        resumable=False,
        required_artifacts=("portify-analysis.md", "component-inventory.md"),
        preserved_context=(),
    ),
    "synthesize-spec": ResumeEntryPoint(
        step_name="synthesize-spec",
        step_number=5,
        resumable=True,
        required_artifacts=(
            "portify-analysis.md",
            "portify-spec.md",
        ),
        preserved_context=("portify-analysis.md", "portify-spec.md"),
    ),
    "brainstorm-gaps": ResumeEntryPoint(
        step_name="brainstorm-gaps",
        step_number=6,
        resumable=True,
        required_artifacts=("synthesized-spec.md",),
        preserved_context=("synthesized-spec.md", "focus-findings.md"),
    ),
    "panel-review": ResumeEntryPoint(
        step_name="panel-review",
        step_number=7,
        resumable=True,
        required_artifacts=("synthesized-spec.md", "brainstorm-gaps.md"),
        preserved_context=(
            "synthesized-spec.md",
            "brainstorm-gaps.md",
            "focus-findings.md",
        ),
    ),
}

# Total pipeline steps
TOTAL_STEPS = 7


def is_resumable(step_name: str) -> bool:
    """Check if a step supports resume entry."""
    entry = RESUMABILITY_MATRIX.get(step_name)
    return entry is not None and entry.resumable


def get_entry_requirements(step_name: str) -> tuple[str, ...]:
    """Get required artifacts for resuming at a given step."""
    entry = RESUMABILITY_MATRIX.get(step_name)
    if entry is None:
        return ()
    return entry.required_artifacts


def get_preserved_context(step_name: str) -> tuple[str, ...]:
    """Get artifacts that should be preserved when resuming at a step."""
    entry = RESUMABILITY_MATRIX.get(step_name)
    if entry is None:
        return ()
    return entry.preserved_context


# --- Resume Command Generation (D-0038 / SC-014) ---


def suggest_budget(step_name: str, max_convergence: int = 3) -> int | None:
    """Suggest a convergence budget for resuming at a given step.

    Budget is based on remaining steps from the resume point.
    Returns None for non-resumable steps.

    Args:
        step_name: Step to resume from.
        max_convergence: Original max convergence setting.

    Returns:
        Suggested budget, or None if not resumable.
    """
    entry = RESUMABILITY_MATRIX.get(step_name)
    if entry is None or not entry.resumable:
        return None
    remaining = TOTAL_STEPS - entry.step_number + 1
    if remaining <= 2:
        return max_convergence
    return max_convergence


def build_resume_command(
    failed_step: str,
    workflow_path: str = "<workflow_path>",
    max_convergence: int = 3,
) -> str:
    """Generate a resume command with --start and suggested budget.

    Per SC-014: resumable failures generate --start <step> commands
    with a suggested budget for remaining work.

    Args:
        failed_step: The step name that failed.
        workflow_path: Path to the workflow (for command string).
        max_convergence: Original max convergence setting.

    Returns:
        CLI command string for resuming, or empty string if not resumable.
    """
    if not is_resumable(failed_step):
        return ""

    budget = suggest_budget(failed_step, max_convergence)
    cmd = f"superclaude cli-portify run {workflow_path} --start {failed_step}"
    if budget is not None:
        cmd += f" --max-convergence {budget}"
    return cmd


# --- Prior-Context Injection (D-0052) ---


def validate_resume_entry(
    step_name: str,
    results_dir: Path,
) -> tuple[bool, list[str], list[str]]:
    """Validate that all required artifacts exist for resume entry.

    Checks the resumability matrix for the step and verifies that
    all required artifacts are present in the results directory.

    Args:
        step_name: Step to resume from.
        results_dir: Directory containing pipeline artifacts.

    Returns:
        Tuple of:
        - valid: True if all requirements are met
        - missing: List of missing artifact filenames
        - preserved: List of preserved context artifact paths that exist
    """
    entry = RESUMABILITY_MATRIX.get(step_name)
    if entry is None:
        return False, [f"Unknown step: {step_name}"], []

    if not entry.resumable:
        return False, [f"Step '{step_name}' is not resumable"], []

    missing: list[str] = []
    for artifact in entry.required_artifacts:
        artifact_path = results_dir / artifact
        if not artifact_path.exists():
            missing.append(artifact)

    preserved: list[str] = []
    for ctx_artifact in entry.preserved_context:
        ctx_path = results_dir / ctx_artifact
        if ctx_path.exists():
            preserved.append(str(ctx_path))

    return len(missing) == 0, missing, preserved


def build_resume_context(
    step_result: PortifyStepResult,
    results_dir: Path,
    max_convergence: int = 3,
) -> ResumeContext:
    """Build a typed ResumeContext from a failed step result.

    Populates all resume metadata fields including the resume command,
    artifact preservation list, and failure classification.

    Args:
        step_result: The failed step result.
        results_dir: Directory containing pipeline artifacts.
        max_convergence: Original max convergence setting.

    Returns:
        Populated ResumeContext.
    """
    step_name = step_result.step_name
    step_number = step_result.step_number

    # Determine last completed step (the one before the failed step)
    step_order = [
        "validate-config", "discover-components", "analyze-workflow",
        "design-pipeline", "synthesize-spec", "brainstorm-gaps", "panel-review",
    ]
    last_completed = ""
    last_completed_number = 0
    for i, name in enumerate(step_order):
        if name == step_name:
            break
        last_completed = name
        last_completed_number = i + 1

    # Get preserved artifacts
    _, _, preserved = validate_resume_entry(step_name, results_dir)

    # Build resume command
    resume_cmd = build_resume_command(
        step_name,
        workflow_path="<workflow_path>",
        max_convergence=max_convergence,
    )

    return ResumeContext(
        last_completed_step=last_completed,
        last_completed_step_number=last_completed_number,
        failed_step=step_name,
        failed_step_number=step_number,
        failure_classification=step_result.failure_classification,
        re_run_required=step_result.portify_status in (
            PortifyStatus.FAIL, PortifyStatus.TIMEOUT, PortifyStatus.ERROR
        ),
        artifacts_preserved=preserved,
        resume_command=resume_cmd,
    )
