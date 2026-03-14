"""Step 3: analyze-workflow — Claude-assisted workflow analysis.

Reads component inventory from Step 2 via @path references and produces
portify-analysis.md with behavioral flow, step boundaries, programmatic
spectrum classification, dependency/parallel groups, and gate requirements.

Includes data flow diagram with arrow notation and 5 YAML frontmatter fields.

Per SC-003: STRICT gate — 5 required sections, data flow diagram,
5 YAML frontmatter fields.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from superclaude.cli.cli_portify.gates import gate_analyze_workflow
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult
from superclaude.cli.cli_portify.prompts import AnalyzeWorkflowPrompt, PromptContext
from superclaude.cli.cli_portify.utils import count_lines

_log = logging.getLogger("superclaude.cli_portify.steps.analyze_workflow")


def run_analyze_workflow(
    config: PortifyConfig,
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
) -> PortifyStepResult:
    """Execute the analyze-workflow step (Step 3).

    Constructs an analysis prompt with @path references to the component
    inventory (D-0015), executes via PortifyProcess with --add-dir scoping,
    and validates output through the SC-003 STRICT gate.

    Args:
        config: Pipeline configuration.
        workflow_path: Resolved workflow path. If None, resolves from config.
        output_dir: Directory for artifacts. Defaults to config.results_dir.

    Returns:
        PortifyStepResult with gate status and artifact path.
    """
    start = time.monotonic()
    results_dir = output_dir or config.results_dir
    results_dir.mkdir(parents=True, exist_ok=True)

    # Resolve paths
    wf_path = workflow_path or config.resolve_workflow_path()
    inventory_path = results_dir / "component-inventory.md"

    # Fail-fast if component inventory is missing
    if not inventory_path.exists():
        elapsed = time.monotonic() - start
        _log.error("component-inventory.md not found at %s", inventory_path)
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="analyze-workflow",
            step_number=3,
            phase=2,
            gate_tier="STRICT",
            failure_classification=FailureClassification.MISSING_ARTIFACT,
        )

    # Build prompt via prompt builder (D-0018)
    context = PromptContext(
        workflow_path=wf_path,
        work_dir=config.work_dir,
        cli_name=config.derive_cli_name(),
        source_skill=wf_path.name,
    )
    builder = AnalyzeWorkflowPrompt(context)
    prompt = builder.build()

    # Output and error files
    output_file = results_dir / "portify-analysis.md"
    error_file = results_dir / "analyze-workflow.err"

    # Execute via PortifyProcess (D-0017) with --add-dir scoping
    proc = PortifyProcess(
        prompt=prompt,
        output_file=output_file,
        error_file=error_file,
        work_dir=config.work_dir,
        workflow_path=wf_path,
        artifact_refs=[inventory_path],
        max_turns=config.max_turns,
        model=config.model,
        timeout_seconds=config.iteration_timeout,
    )

    result = proc.run()
    elapsed = time.monotonic() - start

    _log.info(
        "analyze_workflow exit=%d timeout=%s duration=%.1fs lines=%d",
        result.exit_code,
        result.timed_out,
        elapsed,
        count_lines(output_file) if output_file.exists() else 0,
    )

    # Handle subprocess failure
    if result.timed_out:
        return PortifyStepResult(
            portify_status=PortifyStatus.TIMEOUT,
            step_name="analyze-workflow",
            step_number=3,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            failure_classification=FailureClassification.TIMEOUT,
        )

    if not result.succeeded:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="analyze-workflow",
            step_number=3,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    # Validate line count (<400 lines)
    line_count = count_lines(output_file)
    if line_count >= 400:
        _log.warning("portify-analysis.md exceeds 400 lines: %d", line_count)

    # Run SC-003 STRICT gate
    gate_passed, gate_msg = gate_analyze_workflow(output_file)
    _log.info("SC-003 gate: passed=%s msg=%s", gate_passed, gate_msg)

    if not gate_passed:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="analyze-workflow",
            step_number=3,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    return PortifyStepResult(
        portify_status=PortifyStatus.PASS,
        step_name="analyze-workflow",
        step_number=3,
        phase=2,
        artifact_path=str(output_file),
        gate_tier="STRICT",
    )
