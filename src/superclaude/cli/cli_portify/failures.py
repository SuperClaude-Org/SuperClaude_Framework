"""Failure handlers for the CLI Portify pipeline.

Implements 7 failure type handlers per NFR-009:
  1. MISSING_ARTIFACT    — handle_missing_template()
  2. MALFORMED_FRONTMATTER — handle_malformed_artifact()
  3. TIMEOUT             — handle_timeout()
  4. PARTIAL_ARTIFACT    — handle_partial_artifact()
  5. BUDGET_EXHAUSTION   — handle_budget_exhausted()
  6. USER_REJECTION      — handled by review module (no handler here)
  7. GATE_FAILURE        — handled inline (no handler here)

T02.06 — handle_timeout() enforces Step 0 (30s) and Step 1 (60s) limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .models import (
    FailureClassification,
    PortifyStatus,
    PortifyStepResult,
    ResumeContext,
)

# Steps that support --start <step-name> resume
_RESUMABLE_STEPS = frozenset({"brainstorm-gaps", "synthesize-spec", "panel-review"})

# Step 0 and Step 1 timeout limits (NFR-001)
STEP_0_TIMEOUT_SECONDS = 30
STEP_1_TIMEOUT_SECONDS = 60


@dataclass
class FailureHandlerResult:
    """Result from a failure handler invocation.

    Attributes:
        step_result: Populated PortifyStepResult with failure metadata.
        error_message: Human-readable description of the failure.
        remediation: Suggested action for the user.
        is_terminal: Whether the failure stops the pipeline.
    """

    step_result: PortifyStepResult = field(default_factory=PortifyStepResult)
    error_message: str = ""
    remediation: str = ""
    is_terminal: bool = True


# ---------------------------------------------------------------------------
# Handler implementations
# ---------------------------------------------------------------------------


def handle_missing_template(
    step_name: str,
    step_number: int,
    phase: int,
    template_path: str,
) -> FailureHandlerResult:
    """Handle a missing template/artifact failure (MISSING_ARTIFACT)."""
    resume_cmd = (
        f"superclaude portify --start {step_name}"
        if step_name in _RESUMABLE_STEPS
        else ""
    )
    step_result = PortifyStepResult(
        step_name=step_name,
        step_number=step_number,
        phase=phase,
        portify_status=PortifyStatus.FAIL,
        failure_classification=FailureClassification.MISSING_ARTIFACT,
        resume_context=ResumeContext(resume_command=resume_cmd, resume_step=step_name),
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=f"Template artifact not found: {template_path}",
        remediation=(
            f"Ensure the template file exists at '{template_path}'. "
            "Check that the workflow directory contains all required templates."
        ),
        is_terminal=True,
    )


def handle_malformed_artifact(
    step_name: str,
    step_number: int,
    phase: int,
    artifact_path: str,
    diagnostic: str = "",
) -> FailureHandlerResult:
    """Handle a malformed artifact (MALFORMED_FRONTMATTER)."""
    resume_cmd = (
        f"superclaude portify --start {step_name}"
        if step_name in _RESUMABLE_STEPS
        else ""
    )
    msg = f"Artifact has malformed frontmatter: {artifact_path}"
    if diagnostic:
        msg += f" — {diagnostic}"

    step_result = PortifyStepResult(
        step_name=step_name,
        step_number=step_number,
        phase=phase,
        portify_status=PortifyStatus.FAIL,
        failure_classification=FailureClassification.MALFORMED_FRONTMATTER,
        resume_context=ResumeContext(resume_command=resume_cmd, resume_step=step_name),
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=msg,
        remediation=(
            "Verify the artifact file starts with '---' frontmatter delimiter. "
            f"Re-run from this step: `{resume_cmd}`" if resume_cmd else
            "Verify the artifact file starts with '---' frontmatter delimiter."
        ),
        is_terminal=True,
    )


def handle_timeout(
    step_name: str,
    step_number: int,
    phase: int,
    timeout_seconds: float,
    is_per_iteration: bool = False,
    total_budget_exhausted: bool = False,
    iteration: int = 0,
) -> FailureHandlerResult:
    """Handle a step timeout failure (TIMEOUT or BUDGET_EXHAUSTION).

    T02.06: Step 0 enforces 30s, Step 1 enforces 60s.

    Args:
        step_name: Name of the timed-out step.
        step_number: Step number (1-12).
        phase: Pipeline phase number.
        timeout_seconds: The timeout limit that was exceeded.
        is_per_iteration: True if this is a per-iteration timeout.
        total_budget_exhausted: True if total convergence budget exhausted.
        iteration: Current iteration number (for convergence steps).
    """
    resume_cmd = (
        f"superclaude portify --start {step_name}"
        if step_name in _RESUMABLE_STEPS
        else ""
    )

    if total_budget_exhausted:
        classification = FailureClassification.BUDGET_EXHAUSTION
        msg = (
            f"Total convergence budget exhausted at iteration {iteration} "
            f"in step '{step_name}' (limit: {int(timeout_seconds)}s)"
        )
    elif is_per_iteration and iteration:
        classification = FailureClassification.TIMEOUT
        msg = (
            f"Step '{step_name}' timed out at iteration {iteration} "
            f"after {int(timeout_seconds)}s"
        )
    else:
        classification = FailureClassification.TIMEOUT
        msg = f"Step '{step_name}' timed out after {int(timeout_seconds)}s"

    step_result = PortifyStepResult(
        step_name=step_name,
        step_number=step_number,
        phase=phase,
        portify_status=PortifyStatus.TIMEOUT,
        failure_classification=classification,
        resume_context=ResumeContext(resume_command=resume_cmd, resume_step=step_name),
        iteration_number=iteration,
        iteration_timeout=int(timeout_seconds),
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=msg,
        remediation=(
            "Increase the timeout with --timeout or reduce input complexity. "
            + (f"Resume from this step: `{resume_cmd}`" if resume_cmd else "")
        ).strip(),
        is_terminal=True,
    )


def handle_partial_artifact(
    step_name: str,
    step_number: int,
    phase: int,
    artifact_path: str,
    placeholder_count: int = 0,
) -> FailureHandlerResult:
    """Handle a partial artifact with unresolved placeholders (PARTIAL_ARTIFACT)."""
    resume_cmd = (
        f"superclaude portify --start {step_name}"
        if step_name in _RESUMABLE_STEPS
        else ""
    )
    placeholder_str = (
        f"Found {placeholder_count} placeholder(s) still unresolved. "
        if placeholder_count
        else ""
    )
    step_result = PortifyStepResult(
        step_name=step_name,
        step_number=step_number,
        phase=phase,
        portify_status=PortifyStatus.FAIL,
        failure_classification=FailureClassification.PARTIAL_ARTIFACT,
        resume_context=ResumeContext(resume_command=resume_cmd, resume_step=step_name),
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=(
            f"Artifact at '{artifact_path}' is incomplete. "
            + placeholder_str
        ).strip(),
        remediation=(
            "Re-run the step to complete the artifact. "
            + (f"Use: `{resume_cmd}`" if resume_cmd else "")
        ).strip(),
        is_terminal=True,
    )


def handle_non_writable_output(
    output_dir: str,
) -> FailureHandlerResult:
    """Handle a non-writable output directory (validate-config step)."""
    step_result = PortifyStepResult(
        step_name="validate-config",
        step_number=1,
        phase=1,
        portify_status=PortifyStatus.FAIL,
        failure_classification=FailureClassification.MISSING_ARTIFACT,
        gate_tier="EXEMPT",
        resume_context=ResumeContext(),
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=f"Output directory is not writable: {output_dir}",
        remediation=(
            f"Ensure the output directory '{output_dir}' is writable. "
            "Try: `chmod +w <directory>` or choose a different output path."
        ),
        is_terminal=True,
    )


def handle_budget_exhausted(
    step_name: str,
    step_number: int,
    phase: int,
    current_iteration: int,
    max_convergence: int,
) -> FailureHandlerResult:
    """Handle convergence budget exhaustion (BUDGET_EXHAUSTION)."""
    resume_cmd = (
        f"superclaude portify --start {step_name} --max-convergence {max_convergence + 2}"
        if step_name in _RESUMABLE_STEPS
        else ""
    )
    step_result = PortifyStepResult(
        step_name=step_name,
        step_number=step_number,
        phase=phase,
        portify_status=PortifyStatus.FAIL,
        failure_classification=FailureClassification.BUDGET_EXHAUSTION,
        resume_context=ResumeContext(resume_command=resume_cmd, resume_step=step_name),
        iteration_number=current_iteration,
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=(
            f"Convergence budget exhausted after {current_iteration}/{max_convergence} iterations "
            f"in step '{step_name}'"
        ),
        remediation=(
            "Increase convergence budget: "
            + (f"`{resume_cmd}`" if resume_cmd else "--max-convergence <n>")
        ),
        is_terminal=True,
    )


def handle_missing_skills(
    step_name: str,
    step_number: int,
    phase: int,
    missing_skills: list[str],
) -> FailureHandlerResult:
    """Handle missing skill files (graceful fallback — non-terminal PASS)."""
    skills_str = ", ".join(missing_skills)
    step_result = PortifyStepResult(
        step_name=step_name,
        step_number=step_number,
        phase=phase,
        portify_status=PortifyStatus.PASS,
        failure_classification=None,
        resume_context=ResumeContext(),
    )
    return FailureHandlerResult(
        step_result=step_result,
        error_message=(
            f"Some skills could not be found: {skills_str}. "
            "Continuing with available skills."
        ),
        remediation=(
            f"Install the missing skills: {skills_str}. "
            "Use `superclaude install` to install all skills."
        ),
        is_terminal=False,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

FAILURE_HANDLERS: dict[FailureClassification, Optional[Callable]] = {
    FailureClassification.MISSING_ARTIFACT: handle_missing_template,
    FailureClassification.MALFORMED_FRONTMATTER: handle_malformed_artifact,
    FailureClassification.TIMEOUT: handle_timeout,
    FailureClassification.PARTIAL_ARTIFACT: handle_partial_artifact,
    FailureClassification.BUDGET_EXHAUSTION: handle_budget_exhausted,
    # USER_REJECTION handled by review module (no callable handler registered)
    FailureClassification.USER_REJECTION: None,
    # GATE_FAILURE handled inline by executor (no callable handler registered)
    FailureClassification.GATE_FAILURE: None,
}


def has_handler(classification: FailureClassification) -> bool:
    """Return True if a callable failure handler exists for the given classification."""
    return FAILURE_HANDLERS.get(classification) is not None


def get_failure_handler_name(classification: FailureClassification) -> Optional[str]:
    """Return the name of the handler function for a classification, or None."""
    handler = FAILURE_HANDLERS.get(classification)
    return handler.__name__ if handler else None
