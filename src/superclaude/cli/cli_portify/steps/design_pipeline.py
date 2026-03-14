"""Step 4: design-pipeline — Claude-assisted pipeline design with dry-run and review gate.

Reads portify-analysis.md from Step 3 and produces portify-spec.md with:
step graph, domain models, prompt builder specs, gate criteria with
semantic checks, pure-programmatic steps as runnable Python code,
executor loop, and Click CLI integration.

Implements:
- --dry-run halt: emits dry_run contract with phases 3-4 marked skipped (SC-011)
- User review gate: stderr prompt, y/n response, USER_REJECTED on n

Per SC-004: STRICT gate — step_mapping_count, model_count,
gate_definition_count frontmatter fields.
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from superclaude.cli.cli_portify.contract import build_dry_run_contract, StepTiming
from superclaude.cli.cli_portify.gates import gate_design_pipeline
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult
from superclaude.cli.cli_portify.prompts import DesignPipelinePrompt, PromptContext
from superclaude.cli.cli_portify.utils import count_lines

_log = logging.getLogger("superclaude.cli_portify.steps.design_pipeline")


def run_design_pipeline(
    config: PortifyConfig,
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
    prior_step_results: list[PortifyStepResult] | None = None,
    prior_step_timings: list[StepTiming] | None = None,
) -> PortifyStepResult:
    """Execute the design-pipeline step (Step 4).

    Constructs a pipeline design prompt with @path reference to the
    analysis artifact, executes via PortifyProcess, then applies:
    1. --dry-run halt (if config.dry_run): emit contract, return SKIPPED
    2. User review gate (unless config.skip_review): stderr prompt
    3. SC-004 STRICT gate validation

    Args:
        config: Pipeline configuration.
        workflow_path: Resolved workflow path. If None, resolves from config.
        output_dir: Directory for artifacts. Defaults to config.results_dir.
        prior_step_results: Results from prior steps (for dry-run contract).
        prior_step_timings: Timings from prior steps (for dry-run contract).

    Returns:
        PortifyStepResult with gate status and artifact path.
    """
    start = time.monotonic()
    results_dir = output_dir or config.results_dir
    results_dir.mkdir(parents=True, exist_ok=True)

    # Resolve paths
    wf_path = workflow_path or config.resolve_workflow_path()
    analysis_path = results_dir / "portify-analysis.md"
    inventory_path = results_dir / "component-inventory.md"

    # Fail-fast if analysis artifact is missing
    if not analysis_path.exists():
        _log.error("portify-analysis.md not found at %s", analysis_path)
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="design-pipeline",
            step_number=4,
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
    builder = DesignPipelinePrompt(context)
    prompt = builder.build()

    # Output and error files
    output_file = results_dir / "portify-spec.md"
    error_file = results_dir / "design-pipeline.err"

    # Execute via PortifyProcess (D-0017)
    proc = PortifyProcess(
        prompt=prompt,
        output_file=output_file,
        error_file=error_file,
        work_dir=config.work_dir,
        workflow_path=wf_path,
        artifact_refs=[inventory_path, analysis_path],
        max_turns=config.max_turns,
        model=config.model,
        timeout_seconds=config.iteration_timeout,
    )

    result = proc.run()
    elapsed = time.monotonic() - start

    _log.info(
        "design_pipeline exit=%d timeout=%s duration=%.1fs",
        result.exit_code,
        result.timed_out,
        elapsed,
    )

    # Handle subprocess failure
    if result.timed_out:
        return PortifyStepResult(
            portify_status=PortifyStatus.TIMEOUT,
            step_name="design-pipeline",
            step_number=4,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            failure_classification=FailureClassification.TIMEOUT,
        )

    if not result.succeeded:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="design-pipeline",
            step_number=4,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    # --- Dry-run halt (SC-011) ---
    if config.dry_run:
        _log.info("--dry-run active: halting after design-pipeline")
        all_results = list(prior_step_results or [])
        all_timings = list(prior_step_timings or [])
        all_timings.append(StepTiming(step="design-pipeline", duration_seconds=elapsed))
        artifacts = [str(output_file)]

        dry_contract = build_dry_run_contract(
            step_results=all_results,
            artifacts=artifacts,
            step_timings=all_timings,
            total_duration=elapsed,
        )

        # Emit contract to stdout
        print(dry_contract.to_json())

        return PortifyStepResult(
            portify_status=PortifyStatus.SKIPPED,
            step_name="design-pipeline",
            step_number=4,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
        )

    # --- User review gate ---
    if not config.skip_review:
        accepted = _prompt_user_review(output_file)
        if not accepted:
            _log.info("User rejected design-pipeline output")
            return PortifyStepResult(
                portify_status=PortifyStatus.FAIL,
                step_name="design-pipeline",
                step_number=4,
                phase=2,
                artifact_path=str(output_file),
                gate_tier="STRICT",
                review_required=True,
                review_accepted=False,
                failure_classification=FailureClassification.USER_REJECTION,
            )

    # Run SC-004 STRICT gate
    gate_passed, gate_msg = gate_design_pipeline(output_file)
    _log.info("SC-004 gate: passed=%s msg=%s", gate_passed, gate_msg)

    if not gate_passed:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="design-pipeline",
            step_number=4,
            phase=2,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    return PortifyStepResult(
        portify_status=PortifyStatus.PASS,
        step_name="design-pipeline",
        step_number=4,
        phase=2,
        artifact_path=str(output_file),
        gate_tier="STRICT",
        review_required=not config.skip_review,
        review_accepted=True if not config.skip_review else None,
    )


def _prompt_user_review(artifact_path: Path) -> bool:
    """Prompt user on stderr for review gate approval.

    Args:
        artifact_path: Path to the artifact for review.

    Returns:
        True if user accepts (y), False if rejects (n).
    """
    print(
        f"\n[REVIEW GATE] Pipeline design produced: {artifact_path}\n"
        "Review the output and confirm to proceed.\n"
        "Continue? [y/n]: ",
        file=sys.stderr,
        end="",
        flush=True,
    )
    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return response in ("y", "yes")
