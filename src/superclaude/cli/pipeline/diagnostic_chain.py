"""Diagnostic chain -- intelligent failure analysis for persistent remediation failures.

Implements a multi-stage diagnostic chain:
1. Troubleshoot: analyze gate failure and remediation output
2. Adversarial (root causes): generate root cause hypotheses
3. Adversarial (solutions): generate solution proposals
4. Summary: compile chain output into actionable diagnostic report

Each stage degrades gracefully: stage errors are caught and partial results
are available to subsequent stages.

Runner-side execution: diagnostic chain invocations do NOT consume TurnLedger
turns (Gap 2 compliance). Budget-specific halts skip the diagnostic chain
entirely (Gap 2, R-011).

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

_log = logging.getLogger("superclaude.pipeline.diagnostic_chain")


class DiagnosticStage(Enum):
    """Stages of the diagnostic chain."""

    TROUBLESHOOT = "troubleshoot"
    ROOT_CAUSES = "root_causes"
    SOLUTIONS = "solutions"
    SUMMARY = "summary"


@dataclass
class StageResult:
    """Result from a single diagnostic stage."""

    stage: DiagnosticStage
    output: str
    success: bool = True
    error: str | None = None


@dataclass
class DiagnosticReport:
    """Complete diagnostic report from the chain."""

    stage_results: list[StageResult] = field(default_factory=list)
    summary: str = ""

    @property
    def is_complete(self) -> bool:
        return len(self.stage_results) == 4 and all(
            r.success for r in self.stage_results
        )

    @property
    def stages_completed(self) -> int:
        return sum(1 for r in self.stage_results if r.success)

    def get_stage(self, stage: DiagnosticStage) -> StageResult | None:
        for r in self.stage_results:
            if r.stage == stage:
                return r
        return None


def _run_troubleshoot(
    failure_reason: str,
    remediation_output: str,
    step_id: str,
) -> StageResult:
    """Stage 1: Analyze gate failure and remediation output."""
    analysis = (
        f"## Troubleshoot Analysis for '{step_id}'\n\n"
        f"### Gate Failure\n{failure_reason}\n\n"
        f"### Remediation Output\n"
        f"{remediation_output[:500] if remediation_output else '(no output)'}\n\n"
        f"### Initial Assessment\n"
        f"The gate failure indicates: {failure_reason}. "
        f"Remediation was attempted but did not resolve the issue."
    )
    return StageResult(
        stage=DiagnosticStage.TROUBLESHOOT,
        output=analysis,
    )


def _run_root_causes(
    troubleshoot_output: str,
    failure_reason: str,
) -> StageResult:
    """Stage 2: Generate root cause hypotheses (adversarial)."""
    hypotheses = (
        "## Root Cause Hypotheses\n\n"
        "1. **Primary hypothesis**: The remediation step did not address "
        f"the root cause of: {failure_reason}\n"
        "2. **Secondary hypothesis**: The acceptance criteria may be "
        "inconsistent with the task requirements\n"
        "3. **Tertiary hypothesis**: External dependencies or state "
        "changes between attempts may have introduced new failures\n"
    )
    return StageResult(
        stage=DiagnosticStage.ROOT_CAUSES,
        output=hypotheses,
    )


def _run_solutions(
    root_causes_output: str,
    step_id: str,
) -> StageResult:
    """Stage 3: Generate solution proposals (adversarial)."""
    solutions = (
        "## Proposed Solutions\n\n"
        f"For step '{step_id}':\n"
        "1. **Manual intervention**: Review the gate criteria and adjust "
        "if they are too strict for the current context\n"
        "2. **Targeted fix**: Address each root cause hypothesis individually "
        "with focused corrections\n"
        "3. **Decomposition**: Break the step into smaller sub-steps "
        "that can be gated independently\n"
    )
    return StageResult(
        stage=DiagnosticStage.SOLUTIONS,
        output=solutions,
    )


def _run_summary(
    stages: list[StageResult],
    step_id: str,
) -> StageResult:
    """Stage 4: Compile chain output into actionable report."""
    successful = [s for s in stages if s.success]
    failed = [s for s in stages if not s.success]

    parts = [
        f"# Diagnostic Summary for '{step_id}'\n",
        f"Stages completed: {len(successful)}/{len(stages)}\n",
    ]

    for stage in successful:
        parts.append(f"\n{stage.output}\n")

    if failed:
        parts.append("\n## Degraded Stages\n")
        for stage in failed:
            parts.append(f"- {stage.stage.value}: {stage.error}\n")

    summary_text = "\n".join(parts)
    return StageResult(
        stage=DiagnosticStage.SUMMARY,
        output=summary_text,
    )


def run_diagnostic_chain(
    step_id: str,
    failure_reason: str,
    remediation_output: str = "",
) -> DiagnosticReport:
    """Execute the full diagnostic chain with graceful degradation.

    Each stage catches exceptions and returns partial results. Subsequent
    stages receive whatever partial output is available.

    This is runner-side execution: no TurnLedger turns consumed (Gap 2).

    Args:
        step_id: The step that persistently failed.
        failure_reason: The gate failure reason.
        remediation_output: Output from the failed remediation attempts.

    Returns:
        DiagnosticReport with all stage results and summary.
    """
    report = DiagnosticReport()

    # Stage 1: Troubleshoot
    try:
        troubleshoot = _run_troubleshoot(failure_reason, remediation_output, step_id)
        report.stage_results.append(troubleshoot)
    except Exception as e:
        _log.warning("Diagnostic stage TROUBLESHOOT failed: %s", e)
        troubleshoot = StageResult(
            stage=DiagnosticStage.TROUBLESHOOT,
            output="", success=False, error=str(e),
        )
        report.stage_results.append(troubleshoot)

    # Stage 2: Root causes
    try:
        root_causes = _run_root_causes(
            troubleshoot.output if troubleshoot.success else "",
            failure_reason,
        )
        report.stage_results.append(root_causes)
    except Exception as e:
        _log.warning("Diagnostic stage ROOT_CAUSES failed: %s", e)
        root_causes = StageResult(
            stage=DiagnosticStage.ROOT_CAUSES,
            output="", success=False, error=str(e),
        )
        report.stage_results.append(root_causes)

    # Stage 3: Solutions
    try:
        solutions = _run_solutions(
            root_causes.output if root_causes.success else "",
            step_id,
        )
        report.stage_results.append(solutions)
    except Exception as e:
        _log.warning("Diagnostic stage SOLUTIONS failed: %s", e)
        solutions = StageResult(
            stage=DiagnosticStage.SOLUTIONS,
            output="", success=False, error=str(e),
        )
        report.stage_results.append(solutions)

    # Stage 4: Summary
    try:
        summary = _run_summary(report.stage_results, step_id)
        report.stage_results.append(summary)
        report.summary = summary.output
    except Exception as e:
        _log.warning("Diagnostic stage SUMMARY failed: %s", e)
        report.stage_results.append(StageResult(
            stage=DiagnosticStage.SUMMARY,
            output="", success=False, error=str(e),
        ))

    return report
