"""Failure-path handlers for all 7 failure types in cli-portify pipeline.

Each failure type has an explicit handler producing a populated
PortifyStepResult with clear error messages, remediation guidance,
and contract-compatible fields (no None/empty per NFR-009).

Failure types:
1. Missing template — fail-fast with clear error and remediation path
2. Missing skills — graceful fallback with warning
3. Malformed artifact — diagnostic classification and targeted retry
4. Timeout — per-iteration and total budget handling
5. Partial artifact — re-run policy (prefer re-run over trust)
6. Non-writable output — early detection in validate-config
7. Exhausted budget — ESCALATED terminal state with resume guidance

Per D-0039 / R-027.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
    PortifyStepResult,
    ResumeContext,
)
from superclaude.cli.cli_portify.resume import build_resume_command, is_resumable


@dataclass
class FailureHandlerResult:
    """Result from a failure handler with message and remediation."""

    step_result: PortifyStepResult
    error_message: str
    remediation: str
    is_terminal: bool


def handle_missing_template(
    step_name: str,
    step_number: int,
    phase: int,
    template_path: str,
) -> FailureHandlerResult:
    """Handle missing template failure — fail-fast with remediation.

    This is a non-recoverable configuration error. The user must
    provide the missing template before re-running.
    """
    error_msg = f"Required template not found: {template_path}"
    remediation = (
        f"Ensure the template file exists at '{template_path}' "
        "before running the pipeline. Check that the workflow "
        "directory contains all required source files."
    )

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name=step_name,
            step_number=step_number,
            phase=phase,
            failure_classification=FailureClassification.MISSING_ARTIFACT,
            artifact_path=template_path,
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=True,
    )


def handle_missing_skills(
    step_name: str,
    step_number: int,
    phase: int,
    missing_skills: list[str],
) -> FailureHandlerResult:
    """Handle missing skills — graceful fallback with warning.

    Pipeline continues with reduced functionality. The missing skills
    are noted as warnings but do not block execution.
    """
    skills_str = ", ".join(missing_skills)
    error_msg = f"Optional skills not found: {skills_str}"
    remediation = (
        f"Install missing skills ({skills_str}) for full functionality. "
        "Pipeline will continue with fallback behavior."
    )

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.PASS,
            step_name=step_name,
            step_number=step_number,
            phase=phase,
            failure_classification=None,
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=False,
    )


def handle_malformed_artifact(
    step_name: str,
    step_number: int,
    phase: int,
    artifact_path: str,
    diagnostic: str = "",
) -> FailureHandlerResult:
    """Handle malformed artifact — diagnostic classification with retry suggestion.

    The artifact exists but has invalid structure (e.g., missing
    frontmatter, wrong format). Suggests targeted retry.
    """
    error_msg = f"Malformed artifact at '{artifact_path}'"
    if diagnostic:
        error_msg += f": {diagnostic}"
    remediation = (
        "Re-run the step that produced this artifact. "
        "If the problem persists, check the prompt template "
        "for formatting issues or increase --max-turns."
    )

    resume_cmd = build_resume_command(step_name) if is_resumable(step_name) else ""

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name=step_name,
            step_number=step_number,
            phase=phase,
            artifact_path=artifact_path,
            failure_classification=FailureClassification.MALFORMED_FRONTMATTER,
            resume_context=ResumeContext(
                failed_step=step_name,
                failed_step_number=step_number,
                failure_classification=FailureClassification.MALFORMED_FRONTMATTER,
                re_run_required=True,
                resume_command=resume_cmd,
            ),
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=True,
    )


def handle_timeout(
    step_name: str,
    step_number: int,
    phase: int,
    timeout_seconds: float,
    is_per_iteration: bool = True,
    iteration: int = 0,
    total_budget_exhausted: bool = False,
) -> FailureHandlerResult:
    """Handle timeout — distinguish per-iteration and total budget.

    Per-iteration timeouts may be retried. Total budget exhaustion
    is a terminal ESCALATED state.
    """
    if total_budget_exhausted:
        error_msg = (
            f"Total budget exhausted after {iteration} iterations "
            f"(timeout: {timeout_seconds}s per iteration)"
        )
        classification = FailureClassification.BUDGET_EXHAUSTION
        is_terminal = True
    elif is_per_iteration:
        error_msg = (
            f"Step '{step_name}' timed out after {timeout_seconds}s "
            f"(iteration {iteration})"
        )
        classification = FailureClassification.TIMEOUT
        is_terminal = True
    else:
        error_msg = f"Step '{step_name}' timed out after {timeout_seconds}s"
        classification = FailureClassification.TIMEOUT
        is_terminal = True

    remediation = (
        "Increase --iteration-timeout or --max-convergence, "
        "or simplify the workflow to reduce processing time."
    )

    resume_cmd = build_resume_command(step_name) if is_resumable(step_name) else ""

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.TIMEOUT,
            step_name=step_name,
            step_number=step_number,
            phase=phase,
            iteration_timeout=int(timeout_seconds),
            iteration_number=iteration,
            failure_classification=classification,
            resume_context=ResumeContext(
                failed_step=step_name,
                failed_step_number=step_number,
                failure_classification=classification,
                re_run_required=True,
                resume_command=resume_cmd,
            ),
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=is_terminal,
    )


def handle_partial_artifact(
    step_name: str,
    step_number: int,
    phase: int,
    artifact_path: str,
    placeholder_count: int = 0,
) -> FailureHandlerResult:
    """Handle partial artifact — prefer re-run over trust.

    The artifact exists but contains placeholder sentinels or
    incomplete sections. Policy: always re-run rather than
    trusting partial output.
    """
    error_msg = (
        f"Partial artifact at '{artifact_path}': "
        f"{placeholder_count} placeholder(s) remain"
    )
    remediation = (
        "Re-run the step to regenerate the artifact. "
        "Partial artifacts are never trusted — the re-run policy "
        "ensures output completeness."
    )

    resume_cmd = build_resume_command(step_name) if is_resumable(step_name) else ""

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name=step_name,
            step_number=step_number,
            phase=phase,
            artifact_path=artifact_path,
            failure_classification=FailureClassification.PARTIAL_ARTIFACT,
            resume_context=ResumeContext(
                failed_step=step_name,
                failed_step_number=step_number,
                failure_classification=FailureClassification.PARTIAL_ARTIFACT,
                re_run_required=True,
                resume_command=resume_cmd,
            ),
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=True,
    )


def handle_non_writable_output(
    output_dir: str,
) -> FailureHandlerResult:
    """Handle non-writable output directory — early detection in validate-config.

    Detected during Step 1 (validate-config). Pipeline cannot proceed
    if it cannot write artifacts.
    """
    error_msg = f"Output directory is not writable: {output_dir}"
    remediation = (
        f"Ensure the directory '{output_dir}' exists and is writable, "
        "or specify a different --output directory."
    )

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="validate-config",
            step_number=1,
            phase=1,
            gate_tier="EXEMPT",
            failure_classification=FailureClassification.MISSING_ARTIFACT,
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=True,
    )


def handle_budget_exhausted(
    step_name: str,
    step_number: int,
    phase: int,
    iterations_completed: int,
    max_convergence: int,
) -> FailureHandlerResult:
    """Handle exhausted budget — ESCALATED terminal state with resume guidance.

    The convergence budget (max iterations) has been exhausted without
    reaching convergence. This is a terminal ESCALATED state.
    """
    error_msg = (
        f"Convergence budget exhausted: {iterations_completed}/{max_convergence} "
        f"iterations completed without convergence"
    )
    remediation = (
        "Increase --max-convergence to allow more iterations, "
        "or review the brainstorm-gaps output for persistent issues "
        "preventing convergence."
    )

    resume_cmd = build_resume_command(
        step_name, max_convergence=max_convergence + 2
    )

    return FailureHandlerResult(
        step_result=PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name=step_name,
            step_number=step_number,
            phase=phase,
            iteration_number=iterations_completed,
            failure_classification=FailureClassification.BUDGET_EXHAUSTION,
            resume_context=ResumeContext(
                failed_step=step_name,
                failed_step_number=step_number,
                failure_classification=FailureClassification.BUDGET_EXHAUSTION,
                re_run_required=True,
                resume_command=resume_cmd,
            ),
        ),
        error_message=error_msg,
        remediation=remediation,
        is_terminal=True,
    )


# --- Dispatcher ---

FAILURE_HANDLERS = {
    FailureClassification.MISSING_ARTIFACT: "handle_missing_template",
    FailureClassification.MALFORMED_FRONTMATTER: "handle_malformed_artifact",
    FailureClassification.TIMEOUT: "handle_timeout",
    FailureClassification.PARTIAL_ARTIFACT: "handle_partial_artifact",
    FailureClassification.BUDGET_EXHAUSTION: "handle_budget_exhausted",
    FailureClassification.USER_REJECTION: None,  # Handled by review module
    FailureClassification.GATE_FAILURE: None,  # Handled inline by gate logic
}


def get_failure_handler_name(
    classification: FailureClassification,
) -> str | None:
    """Get the handler function name for a failure classification."""
    return FAILURE_HANDLERS.get(classification)


def has_handler(classification: FailureClassification) -> bool:
    """Check if a failure classification has a dedicated handler."""
    return FAILURE_HANDLERS.get(classification) is not None
