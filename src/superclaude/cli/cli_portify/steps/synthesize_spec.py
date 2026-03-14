"""Step 5: synthesize-spec — Claude-assisted spec synthesis with sentinel scan.

Populates release-spec-template.md from prior outputs, eliminates all
{{SC_PLACEHOLDER:*}} sentinels, and retries on gate failure with specific
placeholder names.

Implements:
- Template existence fail-fast (Recommendation #5)
- SC-003 sentinel scan: regex for remaining {{SC_PLACEHOLDER:*}}
- Retry with specific remaining placeholder names
- Resume policy: prefer re-running over trusting partially gated output

Per SC-005: STRICT gate — zero remaining sentinels, synthesized content.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

from superclaude.cli.cli_portify.gates import gate_synthesize_spec
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult
from superclaude.cli.cli_portify.prompts import SynthesizeSpecPrompt, PromptContext
from superclaude.cli.cli_portify.utils import count_lines

_log = logging.getLogger("superclaude.cli_portify.steps.synthesize_spec")

# Sentinel scan regex per SC-003
_SENTINEL_RE = re.compile(r"\{\{SC_PLACEHOLDER:([^}]+)\}\}")

# Maximum retry attempts for sentinel resolution
_MAX_RETRIES = 2


def run_synthesize_spec(
    config: PortifyConfig,
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
    template_path: Path | None = None,
) -> PortifyStepResult:
    """Execute the synthesize-spec step (Step 5).

    Verifies release-spec-template.md exists (fail-fast), then constructs
    a synthesis prompt with @path references to analysis and design artifacts.
    Runs sentinel scan on output and retries with specific placeholder names
    if sentinels remain.

    Args:
        config: Pipeline configuration.
        workflow_path: Resolved workflow path. If None, resolves from config.
        output_dir: Directory for artifacts. Defaults to config.results_dir.
        template_path: Path to release-spec-template.md. If None, searches
            in workflow_path.

    Returns:
        PortifyStepResult with gate status and artifact path.
    """
    start = time.monotonic()
    results_dir = output_dir or config.results_dir
    results_dir.mkdir(parents=True, exist_ok=True)

    # Resolve paths
    wf_path = workflow_path or config.resolve_workflow_path()

    # Fail-fast: verify template exists (Recommendation #5)
    if template_path is None:
        template_path = wf_path / "release-spec-template.md"
    if not template_path.exists():
        # Also check results dir
        alt_template = results_dir / "release-spec-template.md"
        if alt_template.exists():
            template_path = alt_template
        else:
            _log.error(
                "release-spec-template.md not found at %s or %s",
                template_path,
                alt_template,
            )
            return PortifyStepResult(
                portify_status=PortifyStatus.FAIL,
                step_name="synthesize-spec",
                step_number=5,
                phase=3,
                gate_tier="STRICT",
                failure_classification=FailureClassification.MISSING_ARTIFACT,
            )

    # Verify prior artifacts exist
    analysis_path = results_dir / "portify-analysis.md"
    spec_path = results_dir / "portify-spec.md"
    for required, name in [(analysis_path, "portify-analysis.md"), (spec_path, "portify-spec.md")]:
        if not required.exists():
            _log.error("%s not found at %s", name, required)
            return PortifyStepResult(
                portify_status=PortifyStatus.FAIL,
                step_name="synthesize-spec",
                step_number=5,
                phase=3,
                gate_tier="STRICT",
                failure_classification=FailureClassification.MISSING_ARTIFACT,
            )

    # Build prompt context
    context = PromptContext(
        workflow_path=wf_path,
        work_dir=config.work_dir,
        cli_name=config.derive_cli_name(),
        source_skill=wf_path.name,
    )
    builder = SynthesizeSpecPrompt(context)

    # Output and error files
    output_file = results_dir / "synthesized-spec.md"
    error_file = results_dir / "synthesize-spec.err"

    # Execute with retry loop for sentinel resolution
    attempt = 0
    remaining_placeholders: list[str] = []

    while attempt <= _MAX_RETRIES:
        # Build prompt (with retry augmentation if needed)
        if attempt == 0:
            prompt = builder.build()
        else:
            prompt = builder.build_retry(
                failure_reason=f"Sentinel scan found {len(remaining_placeholders)} unresolved placeholders",
                remaining_placeholders=remaining_placeholders,
            )

        # Execute via PortifyProcess (D-0017)
        proc = PortifyProcess(
            prompt=prompt,
            output_file=output_file,
            error_file=error_file,
            work_dir=config.work_dir,
            workflow_path=wf_path,
            artifact_refs=[analysis_path, spec_path, template_path],
            max_turns=config.max_turns,
            model=config.model,
            timeout_seconds=config.iteration_timeout,
        )

        result = proc.run()
        elapsed = time.monotonic() - start

        _log.info(
            "synthesize_spec attempt=%d exit=%d timeout=%s duration=%.1fs",
            attempt + 1,
            result.exit_code,
            result.timed_out,
            elapsed,
        )

        # Handle subprocess failure
        if result.timed_out:
            return PortifyStepResult(
                portify_status=PortifyStatus.TIMEOUT,
                step_name="synthesize-spec",
                step_number=5,
                phase=3,
                artifact_path=str(output_file),
                gate_tier="STRICT",
                iteration_number=attempt,
                failure_classification=FailureClassification.TIMEOUT,
            )

        if not result.succeeded:
            return PortifyStepResult(
                portify_status=PortifyStatus.FAIL,
                step_name="synthesize-spec",
                step_number=5,
                phase=3,
                artifact_path=str(output_file),
                gate_tier="STRICT",
                iteration_number=attempt,
                failure_classification=FailureClassification.GATE_FAILURE,
            )

        # Sentinel scan
        remaining_placeholders = scan_sentinels(output_file)
        if not remaining_placeholders:
            break

        _log.warning(
            "Sentinel scan found %d unresolved placeholders (attempt %d/%d): %s",
            len(remaining_placeholders),
            attempt + 1,
            _MAX_RETRIES + 1,
            remaining_placeholders,
        )
        attempt += 1

    elapsed = time.monotonic() - start

    # If sentinels still remain after retries, fail
    if remaining_placeholders:
        _log.error(
            "Sentinel scan still found %d placeholders after %d attempts",
            len(remaining_placeholders),
            _MAX_RETRIES + 1,
        )
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="synthesize-spec",
            step_number=5,
            phase=3,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            iteration_number=attempt,
            failure_classification=FailureClassification.PARTIAL_ARTIFACT,
        )

    # Run SC-005 STRICT gate
    gate_passed_result, gate_msg = gate_synthesize_spec(output_file)
    _log.info("SC-005 gate: passed=%s msg=%s", gate_passed_result, gate_msg)

    if not gate_passed_result:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="synthesize-spec",
            step_number=5,
            phase=3,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            iteration_number=attempt,
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    return PortifyStepResult(
        portify_status=PortifyStatus.PASS,
        step_name="synthesize-spec",
        step_number=5,
        phase=3,
        artifact_path=str(output_file),
        gate_tier="STRICT",
        iteration_number=attempt,
    )


def scan_sentinels(artifact_path: Path) -> list[str]:
    """Scan an artifact file for remaining {{SC_PLACEHOLDER:*}} sentinels.

    Args:
        artifact_path: Path to the artifact to scan.

    Returns:
        List of placeholder names found (empty if clean).
    """
    if not artifact_path.exists():
        return []
    content = artifact_path.read_text(encoding="utf-8")
    return _SENTINEL_RE.findall(content)
