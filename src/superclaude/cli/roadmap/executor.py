"""Roadmap executor -- orchestrates the 9-step roadmap pipeline.

Builds the step list with parallel generate group, defines
``roadmap_run_step`` as the StepRunner, and delegates to
``execute_pipeline()`` from the pipeline module.

Context isolation: each subprocess receives only its prompt and --file inputs.
No --continue, --session, or --resume flags are passed (FR-003, FR-023).
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ..pipeline.deliverables import decompose_deliverables
from ..pipeline.executor import execute_pipeline
from ..pipeline.models import Deliverable, PipelineConfig, Step, StepResult, StepStatus
from ..pipeline.process import ClaudeProcess
from .gates import (
    CERTIFY_GATE,
    DEBATE_GATE,
    DIFF_GATE,
    EXTRACT_GATE,
    GENERATE_A_GATE,
    GENERATE_B_GATE,
    MERGE_GATE,
    SCORE_GATE,
    SPEC_FIDELITY_GATE,
    TEST_STRATEGY_GATE,
)
from .models import RoadmapConfig
from .prompts import (
    build_debate_prompt,
    build_diff_prompt,
    build_extract_prompt,
    build_generate_prompt,
    build_merge_prompt,
    build_score_prompt,
    build_spec_fidelity_prompt,
    build_test_strategy_prompt,
)
from .certify_prompts import build_certification_prompt

_log = logging.getLogger("superclaude.roadmap.executor")

# Threshold above which inline embedding falls back to --file flags
_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB


def _embed_inputs(input_paths: list[Path]) -> str:
    """Read input files and return their contents as fenced code blocks.

    Each file is wrapped in a fenced block with a ``# <path>`` header.
    Returns an empty string when *input_paths* is empty (no-op).
    """
    if not input_paths:
        return ""

    blocks: list[str] = []
    for p in input_paths:
        content = Path(p).read_text(encoding="utf-8")
        blocks.append(f"# {p}\n```\n{content}\n```")
    return "\n\n".join(blocks)


def _sanitize_output(output_file: Path) -> int:
    """Strip conversational preamble before YAML frontmatter in a step output file.

    Reads the file, finds the first ``^---`` line, and removes everything before
    it.  Uses atomic write (write to ``.tmp`` then ``os.replace()``) to prevent
    partial file states.

    Returns the byte count of the stripped preamble (0 when file already starts
    with ``---`` or no frontmatter delimiter is found).
    """
    import os
    import re

    try:
        content = output_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        return 0

    # Already starts with frontmatter delimiter -- nothing to strip
    if content.lstrip().startswith("---"):
        return 0

    # Search for the first ^--- line
    match = re.search(r"^---[ \t]*$", content, re.MULTILINE)
    if match is None:
        # No frontmatter found at all -- leave file unchanged
        return 0

    preamble = content[: match.start()]
    cleaned = content[match.start() :]
    preamble_bytes = len(preamble.encode("utf-8"))

    # Atomic write: tmp file + os.replace
    tmp_file = output_file.with_suffix(output_file.suffix + ".tmp")
    tmp_file.write_text(cleaned, encoding="utf-8")
    os.replace(tmp_file, output_file)

    _log.info("Stripped %d-byte preamble from %s", preamble_bytes, output_file)
    return preamble_bytes


def _inject_pipeline_diagnostics(
    output_file: Path,
    started_at: datetime,
    finished_at: datetime,
) -> None:
    """Inject executor-populated pipeline_diagnostics into extraction frontmatter.

    The LLM cannot reliably produce execution timing or environment metadata,
    so the executor injects these fields post-subprocess (FR-033).
    """
    content = output_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return

    # Find end of frontmatter
    end_idx = content.find("\n---", 3)
    if end_idx == -1:
        return

    elapsed = (finished_at - started_at).total_seconds()
    diagnostics_line = (
        f"pipeline_diagnostics: "
        f"{{elapsed_seconds: {elapsed:.1f}, "
        f"started_at: \"{started_at.isoformat()}\", "
        f"finished_at: \"{finished_at.isoformat()}\"}}"
    )

    # Insert before the closing ---
    new_content = (
        content[: end_idx]
        + "\n"
        + diagnostics_line
        + content[end_idx:]
    )
    output_file.write_text(new_content, encoding="utf-8")


def roadmap_run_step(
    step: Step,
    config: PipelineConfig,
    cancel_check: Callable[[], bool],
) -> StepResult:
    """Execute a single roadmap step as a Claude subprocess.

    Builds argv with context isolation, launches process, waits with
    timeout, and returns StepResult.
    """
    started_at = datetime.now(timezone.utc)

    if config.dry_run:
        _log.info("[dry-run] Would execute step '%s'", step.id)
        return StepResult(
            step=step,
            status=StepStatus.PASS,
            attempt=1,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
        )

    # Inline embedding: read input files into the prompt instead of --file flags
    embedded = _embed_inputs(step.inputs)
    if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
        effective_prompt = step.prompt + "\n\n" + embedded
        extra_args: list[str] = []
    elif embedded:
        _log.warning(
            "Step '%s': embedded inputs exceed %d bytes, falling back to --file flags",
            step.id,
            _EMBED_SIZE_LIMIT,
        )
        effective_prompt = step.prompt
        extra_args = [
            arg
            for input_path in step.inputs
            for arg in ("--file", str(input_path))
        ]
    else:
        effective_prompt = step.prompt
        extra_args = []

    proc = ClaudeProcess(
        prompt=effective_prompt,
        output_file=step.output_file,
        error_file=step.output_file.with_suffix(".err"),
        max_turns=config.max_turns,
        model=step.model or config.model,
        permission_flag=config.permission_flag,
        timeout_seconds=step.timeout_seconds,
        output_format="text",
        extra_args=extra_args,
    )

    proc.start()

    # Poll for cancellation while waiting
    while proc._process is not None and proc._process.poll() is None:
        if cancel_check():
            proc.terminate()
            return StepResult(
                step=step,
                status=StepStatus.CANCELLED,
                attempt=1,
                gate_failure_reason="Cancelled by external signal",
                started_at=started_at,
                finished_at=datetime.now(timezone.utc),
            )
        time.sleep(1)

    exit_code = proc.wait()
    finished_at = datetime.now(timezone.utc)

    if exit_code == 124:
        return StepResult(
            step=step,
            status=StepStatus.TIMEOUT,
            attempt=1,
            gate_failure_reason=f"Step '{step.id}' timed out after {step.timeout_seconds}s",
            started_at=started_at,
            finished_at=finished_at,
        )

    if exit_code != 0:
        return StepResult(
            step=step,
            status=StepStatus.FAIL,
            attempt=1,
            gate_failure_reason=f"Step '{step.id}' exited with code {exit_code}",
            started_at=started_at,
            finished_at=finished_at,
        )

    # Sanitize output: strip conversational preamble before gate validation
    _sanitize_output(step.output_file)

    # Inject executor-populated fields into extract step frontmatter (FR-033)
    if step.id == "extract" and step.output_file.exists():
        _inject_pipeline_diagnostics(step.output_file, started_at, finished_at)

    # Process completed successfully; gate check happens in execute_pipeline
    return StepResult(
        step=step,
        status=StepStatus.PASS,
        attempt=1,
        started_at=started_at,
        finished_at=finished_at,
    )


def build_certify_step(
    config: RoadmapConfig,
    findings: list | None = None,
    context_sections: dict[str, str] | None = None,
) -> Step:
    """Build a certify Step for execution via execute_pipeline().

    The certify step runs as a standard Step (not ClaudeProcess directly)
    per spec section 2.5. It uses CERTIFY_GATE for output validation.

    Parameters
    ----------
    config:
        RoadmapConfig with output_dir.
    findings:
        List of Finding objects to certify. If None, an empty prompt is built.
    context_sections:
        Pre-extracted context sections per finding location (NFR-011).
    """
    from .models import Finding

    out = config.output_dir
    certification_report = out / "certification-report.md"

    prompt = build_certification_prompt(
        findings=findings or [],
        context_sections=context_sections or {},
    )

    return Step(
        id="certify",
        prompt=prompt,
        output_file=certification_report,
        gate=CERTIFY_GATE,
        timeout_seconds=300,
        inputs=[out / "remediation-tasklist.md"],
        retry_limit=1,
    )


def _build_steps(config: RoadmapConfig) -> list[Step | list[Step]]:
    """Build the 9-step pipeline with parallel generate group.

    Returns a list where each element is either a single Step (sequential)
    or a list[Step] (parallel group).
    """
    out = config.output_dir

    # Agent specs
    agent_a = config.agents[0]
    agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]

    # Output paths
    extraction = out / "extraction.md"
    roadmap_a = out / f"roadmap-{agent_a.id}.md"
    roadmap_b = out / f"roadmap-{agent_b.id}.md"
    diff_file = out / "diff-analysis.md"
    debate_file = out / "debate-transcript.md"
    score_file = out / "base-selection.md"
    merge_file = out / "roadmap.md"
    test_strat = out / "test-strategy.md"
    spec_fidelity_file = out / "spec-fidelity.md"

    # Load retrospective content if configured (missing file handled gracefully)
    retrospective_content: str | None = None
    if config.retrospective_file is not None and config.retrospective_file.is_file():
        try:
            retrospective_content = config.retrospective_file.read_text(
                encoding="utf-8"
            )
        except OSError:
            retrospective_content = None

    steps: list[Step | list[Step]] = [
        # Step 1: Extract
        Step(
            id="extract",
            prompt=build_extract_prompt(
                config.spec_file,
                retrospective_content=retrospective_content,
            ),
            output_file=extraction,
            gate=EXTRACT_GATE,
            timeout_seconds=300,
            inputs=[config.spec_file],
            retry_limit=1,
        ),
        # Steps 2a+2b: Generate (parallel)
        [
            Step(
                id=f"generate-{agent_a.id}",
                prompt=build_generate_prompt(agent_a, extraction),
                output_file=roadmap_a,
                gate=GENERATE_A_GATE,
                timeout_seconds=900,
                inputs=[extraction],
                retry_limit=1,
                model=agent_a.model,
            ),
            Step(
                id=f"generate-{agent_b.id}",
                prompt=build_generate_prompt(agent_b, extraction),
                output_file=roadmap_b,
                gate=GENERATE_B_GATE,
                timeout_seconds=900,
                inputs=[extraction],
                retry_limit=1,
                model=agent_b.model,
            ),
        ],
        # Step 3: Diff
        Step(
            id="diff",
            prompt=build_diff_prompt(roadmap_a, roadmap_b),
            output_file=diff_file,
            gate=DIFF_GATE,
            timeout_seconds=300,
            inputs=[roadmap_a, roadmap_b],
            retry_limit=1,
        ),
        # Step 4: Debate
        Step(
            id="debate",
            prompt=build_debate_prompt(diff_file, roadmap_a, roadmap_b, config.depth),
            output_file=debate_file,
            gate=DEBATE_GATE,
            timeout_seconds=600,
            inputs=[diff_file, roadmap_a, roadmap_b],
            retry_limit=1,
        ),
        # Step 5: Score
        Step(
            id="score",
            prompt=build_score_prompt(debate_file, roadmap_a, roadmap_b),
            output_file=score_file,
            gate=SCORE_GATE,
            timeout_seconds=300,
            inputs=[debate_file, roadmap_a, roadmap_b],
            retry_limit=1,
        ),
        # Step 6: Merge
        Step(
            id="merge",
            prompt=build_merge_prompt(score_file, roadmap_a, roadmap_b, debate_file),
            output_file=merge_file,
            gate=MERGE_GATE,
            timeout_seconds=600,
            inputs=[score_file, roadmap_a, roadmap_b, debate_file],
            retry_limit=1,
        ),
        # Step 7: Test Strategy
        Step(
            id="test-strategy",
            prompt=build_test_strategy_prompt(merge_file, extraction),
            output_file=test_strat,
            gate=TEST_STRATEGY_GATE,
            timeout_seconds=300,
            inputs=[merge_file, extraction],
            retry_limit=1,
        ),
        # Step 8: Spec Fidelity (after test-strategy, FR-008 through FR-010)
        Step(
            id="spec-fidelity",
            prompt=build_spec_fidelity_prompt(config.spec_file, merge_file),
            output_file=spec_fidelity_file,
            gate=SPEC_FIDELITY_GATE,
            timeout_seconds=600,
            inputs=[config.spec_file, merge_file],
            retry_limit=1,
        ),
    ]

    return steps


def _format_halt_output(results: list[StepResult], config: RoadmapConfig) -> str:
    """Format HALT diagnostic output per spec section 6.2."""
    failed = [r for r in results if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)]
    passed = [r for r in results if r.status == StepStatus.PASS]
    cancelled = [r for r in results if r.status == StepStatus.CANCELLED]

    if not failed:
        return ""

    fail = failed[-1]
    step = fail.step

    # Calculate file details if output exists
    file_info = ""
    if step and step.output_file.exists():
        content = step.output_file.read_text(encoding="utf-8")
        byte_count = len(content.encode("utf-8"))
        line_count = len(content.splitlines())
        file_info = f"  Output size: {byte_count} bytes ({line_count} lines)\n"
    elif step:
        file_info = "  Output file: not created\n"

    elapsed = f"{fail.duration_seconds:.0f}s"

    lines = [
        f"ERROR: Roadmap pipeline halted at step '{step.id}' (attempt {fail.attempt}/2)",
        f"  Gate failure: {fail.gate_failure_reason}",
        f"  Output file: {step.output_file}",
        file_info.rstrip(),
        f"  Step timeout: {step.timeout_seconds}s | Elapsed: {elapsed}",
        "",
        f"Completed steps: {', '.join(f'{r.step.id} (PASS, attempt {r.attempt})' for r in passed) or 'none'}",
        f"Failed step:     {step.id} ({fail.status.value}, attempt {fail.attempt})",
    ]

    # Collect skipped steps
    all_step_ids = _get_all_step_ids(config)
    executed_ids = {r.step.id for r in results}
    skipped_ids = [sid for sid in all_step_ids if sid not in executed_ids]
    if cancelled:
        skipped_ids = [r.step.id for r in cancelled] + skipped_ids

    if skipped_ids:
        lines.append(f"Skipped steps:   {', '.join(skipped_ids)}")

    lines.extend([
        "",
        "To retry from this step:",
        f"  superclaude roadmap run {config.spec_file} --resume",
        "",
        "To inspect the failing output:",
        f"  cat {step.output_file}",
    ])

    return "\n".join(lines)


def _get_all_step_ids(config: RoadmapConfig) -> list[str]:
    """Get all step IDs in pipeline order."""
    agent_a = config.agents[0]
    agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]
    return [
        "extract",
        f"generate-{agent_a.id}",
        f"generate-{agent_b.id}",
        "diff",
        "debate",
        "score",
        "merge",
        "test-strategy",
        "spec-fidelity",
        "remediate",
        "certify",
    ]


def _print_step_start(step: Step) -> None:
    """Print progress output when a step starts."""
    print(f"[roadmap] Starting step: {step.id}", flush=True)


def _print_step_complete(step: Step, result: StepResult) -> None:
    """Print progress output when a step completes."""
    duration = f"{result.duration_seconds:.0f}s"
    if result.status == StepStatus.PASS:
        print(
            f"[roadmap] Step {step.id}  PASS (attempt {result.attempt}, {duration})",
            flush=True,
        )
    else:
        print(
            f"[roadmap] Step {step.id}  {result.status.value} (attempt {result.attempt}, {duration})",
            flush=True,
        )
        if result.gate_failure_reason:
            print(f"           Reason: {result.gate_failure_reason}", flush=True)


def _dry_run_output(steps: list[Step | list[Step]]) -> None:
    """Print step plan and gate criteria for --dry-run."""
    step_num = 0
    for entry in steps:
        if isinstance(entry, list):
            for s in entry:
                step_num += 1
                _print_step_plan(step_num, s, parallel=True)
        else:
            step_num += 1
            _print_step_plan(step_num, entry)


def _print_step_plan(num: int, step: Step, parallel: bool = False) -> None:
    """Print a single step's plan entry."""
    par_label = " (parallel)" if parallel else ""
    print(f"Step {num}{par_label}: {step.id}")
    print(f"  Output: {step.output_file}")
    print(f"  Timeout: {step.timeout_seconds}s")
    if step.model:
        print(f"  Model: {step.model}")
    if step.gate:
        print(f"  Gate tier: {step.gate.enforcement_tier}")
        print(f"  Gate min_lines: {step.gate.min_lines}")
        if step.gate.required_frontmatter_fields:
            print(f"  Gate frontmatter: {', '.join(step.gate.required_frontmatter_fields)}")
        if step.gate.semantic_checks:
            checks = [c.name for c in step.gate.semantic_checks]
            print(f"  Semantic checks: {', '.join(checks)}")
    print()


def _save_state(
    config: RoadmapConfig,
    results: list[StepResult],
    remediate_metadata: dict | None = None,
    certify_metadata: dict | None = None,
) -> None:
    """Write .roadmap-state.json to output_dir via atomic tmp + os.replace().

    Preserves existing ``validation``, ``fidelity_status``, ``remediate``,
    and ``certify`` keys if present. Accepts optional remediate/certify
    metadata dicts for Phase 6 state finalization.
    """
    state_file = config.output_dir / ".roadmap-state.json"
    spec_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()

    # Preserve existing keys across state rewrites
    existing = read_state(state_file)
    existing_validation = existing.get("validation") if existing else None
    existing_fidelity = existing.get("fidelity_status") if existing else None
    existing_remediate = existing.get("remediate") if existing else None
    existing_certify = existing.get("certify") if existing else None

    state = {
        "schema_version": 1,
        "spec_file": str(config.spec_file),
        "spec_hash": spec_hash,
        "agents": [{"model": a.model, "persona": a.persona} for a in config.agents],
        "depth": config.depth,
        "last_run": datetime.now(timezone.utc).isoformat(),
        "steps": {
            r.step.id: {
                "status": r.status.value,
                "attempt": r.attempt,
                "output_file": str(r.step.output_file),
                "started_at": r.started_at.isoformat(),
                "completed_at": r.finished_at.isoformat(),
            }
            for r in results
            if r.step
        },
    }

    if existing_validation is not None:
        state["validation"] = existing_validation

    # Derive fidelity_status from spec-fidelity step result
    fidelity_result = next(
        (r for r in results if r.step and r.step.id == "spec-fidelity"),
        None,
    )
    if fidelity_result is not None:
        state["fidelity_status"] = _derive_fidelity_status(fidelity_result)
    elif existing_fidelity is not None:
        state["fidelity_status"] = existing_fidelity

    # Remediate metadata (spec §3.1)
    if remediate_metadata is not None:
        state["remediate"] = remediate_metadata
    elif existing_remediate is not None:
        state["remediate"] = existing_remediate

    # Certify metadata (spec §3.1)
    if certify_metadata is not None:
        state["certify"] = certify_metadata
    elif existing_certify is not None:
        state["certify"] = existing_certify

    write_state(state, state_file)


def _derive_fidelity_status(result: StepResult) -> str:
    """Derive fidelity_status enum from a spec-fidelity StepResult.

    Returns one of: 'pass', 'fail', 'skipped', 'degraded'.
    """
    if result.status == StepStatus.PASS:
        # Check if the output indicates degraded mode
        if result.step and result.step.output_file.exists():
            content = result.step.output_file.read_text(encoding="utf-8")
            if "validation_complete: false" in content:
                return "degraded"
        return "pass"
    if result.status == StepStatus.SKIPPED:
        return "skipped"
    if result.status in (StepStatus.FAIL, StepStatus.TIMEOUT):
        return "fail"
    return "skipped"


def generate_degraded_report(
    output_file: Path,
    failed_agent: str,
    failure_reason: str,
) -> None:
    """Generate a degraded fidelity report when the agent fails.

    Produces a report with validation_complete=false and
    fidelity_check_attempted=true so the SPEC_FIDELITY_GATE
    can distinguish degraded from clean passes (NFR-007).

    The degraded report names the failed agent and reason in the body.
    """
    report = (
        "---\n"
        "high_severity_count: 0\n"
        "medium_severity_count: 0\n"
        "low_severity_count: 0\n"
        "total_deviations: 0\n"
        "validation_complete: false\n"
        "fidelity_check_attempted: true\n"
        "tasklist_ready: false\n"
        "---\n"
        "\n"
        "## Degraded Fidelity Report\n"
        "\n"
        "Spec-fidelity validation could not be completed.\n"
        "\n"
        f"**Failed Agent**: {failed_agent}\n"
        f"**Failure Reason**: {failure_reason}\n"
        "\n"
        "This is a degraded report produced after agent failure and retry "
        "exhaustion. No deviations were analyzed. The pipeline continues "
        "in degraded mode with validation_complete=false.\n"
        "\n"
        "### Recommended Actions\n"
        "\n"
        "1. Investigate the agent failure\n"
        "2. Re-run the spec-fidelity step manually\n"
        "3. Review the roadmap against the specification\n"
    )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding="utf-8")


def build_remediate_metadata(
    status: str,
    scope: str,
    findings_total: int,
    findings_actionable: int,
    findings_fixed: int,
    findings_failed: int,
    findings_skipped: int,
    agents_spawned: int,
    tasklist_file: str,
) -> dict:
    """Build remediate metadata dict for state schema §3.1.

    Parameters map 1:1 to .roadmap-state.json ``remediate`` entry fields.
    """
    return {
        "status": status,
        "scope": scope,
        "findings_total": findings_total,
        "findings_actionable": findings_actionable,
        "findings_fixed": findings_fixed,
        "findings_failed": findings_failed,
        "findings_skipped": findings_skipped,
        "agents_spawned": agents_spawned,
        "tasklist_file": tasklist_file,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def build_certify_metadata(
    status: str,
    findings_verified: int,
    findings_passed: int,
    findings_failed: int,
    certified: bool,
    report_file: str,
) -> dict:
    """Build certify metadata dict for state schema §3.1.

    Parameters map 1:1 to .roadmap-state.json ``certify`` entry fields.
    """
    return {
        "status": status,
        "findings_verified": findings_verified,
        "findings_passed": findings_passed,
        "findings_failed": findings_failed,
        "certified": certified,
        "report_file": report_file,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def derive_pipeline_status(state: dict) -> str:
    """Derive the overall pipeline status from state transitions.

    State transitions at each boundary:
    - post-validate: validated | validated-with-issues
    - post-remediate: remediated
    - post-certify: certified | certified-with-caveats

    Returns one of: 'pending', 'validated', 'validated-with-issues',
    'remediated', 'certified', 'certified-with-caveats'.
    """
    certify = state.get("certify")
    if certify is not None:
        if certify.get("certified", False):
            return "certified"
        return "certified-with-caveats"

    remediate = state.get("remediate")
    if remediate is not None:
        return "remediated"

    validation = state.get("validation")
    if validation is not None:
        if validation.get("status") == "pass":
            return "validated"
        if validation.get("status") == "fail":
            return "validated-with-issues"

    return "pending"


def write_state(state: dict, path: Path) -> None:
    """Write state dict to path atomically via tmp file + os.replace()."""
    import os as _os

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    _os.replace(str(tmp), str(path))


def read_state(path: Path) -> dict | None:
    """Read state from path with graceful recovery on missing/malformed files."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return None
        return json.loads(text)
    except (json.JSONDecodeError, OSError):
        return None


def apply_decomposition_pass(deliverables: list[Deliverable]) -> list[Deliverable]:
    """Post-generation decomposition pass for the roadmap pipeline.

    Runs after deliverable generation, before output formatting.
    Splits behavioral deliverables into Implement/Verify pairs.

    Idempotent: running twice produces identical results because
    already-decomposed deliverables (IDs ending .a/.b) are skipped.

    Preserves milestone-internal ordering: deliverables within each
    milestone maintain their relative order after decomposition.
    """
    return decompose_deliverables(deliverables)


def execute_roadmap(
    config: RoadmapConfig,
    resume: bool = False,
    no_validate: bool = False,
    auto_accept: bool = False,
) -> None:
    """Execute the roadmap generation pipeline.

    Builds the step list, handles --dry-run and --resume, then
    delegates to execute_pipeline() with roadmap_run_step.

    After all 9 steps pass, auto-invokes validation unless
    --no-validate is set or --resume halted on a failed step.

    Note: --no-validate does NOT skip the spec-fidelity step
    (FR-010, AC-005). It only skips the post-pipeline validation
    subsystem.

    Args:
        auto_accept: When True, the spec-patch resume cycle skips the
            interactive prompt and proceeds automatically if evidence is
            found. When False (default), the cycle prompts the user.
            This is an internal parameter, not exposed on the CLI.
    """
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # FR-2.24.1.11: Recursion guard — local variable, per-invocation
    _spec_patch_cycle_count = 0

    # FR-2.24.1.9 Condition 3: Capture spec hash at function entry
    initial_spec_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()

    steps = _build_steps(config)

    # --dry-run: print plan and exit
    if config.dry_run:
        _dry_run_output(steps)
        return

    # --resume: check which steps already pass their gates
    if resume:
        from ..pipeline.gates import gate_passed

        steps = _apply_resume(steps, config, gate_passed)

    # Execute pipeline
    results = execute_pipeline(
        steps=steps,
        config=config,
        run_step=roadmap_run_step,
        on_step_start=_print_step_start,
        on_step_complete=_print_step_complete,
    )

    # Save state
    _save_state(config, results)

    # Check for failures
    failures = [r for r in results if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)]
    if failures:
        # FR-2.24.1.9: Check if spec-fidelity failed and auto-resume is possible
        spec_fidelity_failed = any(
            r.step and r.step.id == "spec-fidelity"
            and r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)
            for r in results
        )

        if spec_fidelity_failed:
            resumed = _apply_resume_after_spec_patch(
                config=config,
                results=results,
                auto_accept=auto_accept,
                initial_spec_hash=initial_spec_hash,
                cycle_count=_spec_patch_cycle_count,
            )
            if resumed:
                _spec_patch_cycle_count += 1
                # Cycle complete — resumed pipeline ran to completion or failure
                # inside _apply_resume_after_spec_patch. If it returned True,
                # we're done (either success or failure was handled internally).
                return

        halt_msg = _format_halt_output(results, config)
        print(halt_msg, file=sys.stderr)
        sys.exit(1)

    print(f"\n[roadmap] Pipeline complete: {len(results)} steps passed", flush=True)

    # Auto-invoke validation after successful pipeline completion
    if no_validate:
        print("[roadmap] Validation skipped (--no-validate)", flush=True)
        _save_validation_status(config, "skipped")
        return

    # Check if validation already completed (--resume path)
    if resume:
        state_file = config.output_dir / ".roadmap-state.json"
        state = read_state(state_file)
        if state and "validation" in state:
            saved = state["validation"]
            if saved.get("status") in ("pass", "fail"):
                print(
                    f"[roadmap] Validation already completed ({saved['status']}), skipping",
                    flush=True,
                )
                return

    _auto_invoke_validate(config)



def _find_qualifying_deviation_files(
    config: RoadmapConfig,
    results: list[StepResult],
) -> list:
    """Find deviation files written after spec-fidelity started.

    Returns qualifying DeviationRecord objects, or empty list if
    conditions are not met.

    Implementation detail — not specified in the spec. Extracted for
    testability of the three-condition detection gate.
    """
    from .spec_patch import scan_accepted_deviation_records

    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    if state is None:
        return []

    # Get spec-fidelity started_at timestamp
    steps_state = state.get("steps", {})
    fidelity_state = steps_state.get("spec-fidelity", {})
    started_at_str = fidelity_state.get("started_at")

    # Fail-closed: if started_at is absent, condition not met
    if not started_at_str:
        return []

    try:
        started_at_ts = datetime.fromisoformat(started_at_str).timestamp()
    except (ValueError, TypeError):
        return []

    # Scan all deviation records
    all_records = scan_accepted_deviation_records(config.output_dir)
    if not all_records:
        return []

    # Filter to records written AFTER spec-fidelity started (strict >)
    qualifying = [r for r in all_records if r.mtime > started_at_ts]
    return qualifying


def _apply_resume_after_spec_patch(
    config: RoadmapConfig,
    results: list[StepResult],
    auto_accept: bool,
    initial_spec_hash: str,
    cycle_count: int,
) -> bool:
    """Attempt a single spec-patch auto-resume cycle after spec-fidelity FAIL.

    Evaluates the three-condition detection gate (FR-2.24.1.9):
      1. Recursion guard: cycle_count == 0
      2. Qualifying deviation files exist with mtime > started_at
      3. Spec file hash changed since run started (initial_spec_hash)

    If all conditions pass, executes the six-step disk-reread sequence
    (FR-2.24.1.10) and re-runs the pipeline via _apply_resume.

    Single-writer assumption: no concurrent writer modifies
    .roadmap-state.json between the reread and write steps.

    Returns True if the cycle was attempted (regardless of outcome),
    False if conditions were not met.
    """
    # FR-2.24.1.11: Recursion guard
    if cycle_count >= 1:
        print(
            "[roadmap] Spec-patch cycle already exhausted "
            f"(cycle_count={cycle_count}). Proceeding to normal failure.",
            flush=True,
        )
        return False

    # FR-2.24.1.9 Condition 2: Qualifying deviation files
    qualifying = _find_qualifying_deviation_files(config, results)
    if not qualifying:
        return False

    # FR-2.24.1.9 Condition 3: Spec hash changed since run started
    current_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
    if current_hash == initial_spec_hash:
        return False

    # All three conditions met — enter the cycle
    # FR-2.24.1.12: Cycle entry logging
    print(
        f"[roadmap] Spec patched by subprocess. "
        f"Found {len(qualifying)} accepted deviation record(s).",
        flush=True,
    )
    print(
        "[roadmap] Triggering spec-hash sync and resume (cycle 1/1).",
        flush=True,
    )

    # FR-2.24.1.10: Six-step disk-reread sequence
    state_file = config.output_dir / ".roadmap-state.json"

    # Step 1: Re-read state from disk
    _fresh_state = read_state(state_file)  # noqa: F841

    # Step 2: Recompute spec hash
    new_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()

    # Step 3: Atomic write of new hash
    try:
        # Read again for fresh copy, update only spec_hash, write atomically
        fresh_for_write = read_state(state_file) or {}
        fresh_for_write["spec_hash"] = new_hash
        write_state(fresh_for_write, state_file)
    except OSError as exc:
        print(
            f"[roadmap] ERROR: Failed to update spec_hash during "
            f"auto-resume cycle: {exc}. Falling through to normal failure.",
            file=sys.stderr,
            flush=True,
        )
        return True  # Cycle was attempted but failed — don't retry

    # Step 4: Re-read state from disk AGAIN (this is what _apply_resume gets)
    post_write_state = read_state(state_file)
    if post_write_state is None:
        print(
            "[roadmap] ERROR: Could not re-read state after write. "
            "Falling through to normal failure.",
            file=sys.stderr,
            flush=True,
        )
        return True

    # Step 5: Rebuild steps
    steps = _build_steps(config)

    # Step 6: Apply resume with post-write state
    from ..pipeline.gates import gate_passed

    steps = _apply_resume(steps, config, gate_passed)

    # Re-execute pipeline from the resumed point
    resumed_results = execute_pipeline(
        steps=steps,
        config=config,
        run_step=roadmap_run_step,
        on_step_start=_print_step_start,
        on_step_complete=_print_step_complete,
    )

    # Save state from resumed run
    _save_state(config, resumed_results)

    # FR-2.24.1.12: Cycle completion logging
    print("[roadmap] Spec-patch resume cycle complete.", flush=True)

    # Check if resumed pipeline also failed
    resumed_failures = [
        r for r in resumed_results
        if r.status in (StepStatus.FAIL, StepStatus.TIMEOUT)
    ]
    if resumed_failures:
        # FR-2.24.1.13: Normal failure on cycle exhaustion
        # Use second-run results only
        halt_msg = _format_halt_output(resumed_results, config)
        print(halt_msg, file=sys.stderr)
        sys.exit(1)

    # Resumed pipeline succeeded
    print(
        f"\n[roadmap] Pipeline complete: {len(resumed_results)} steps passed",
        flush=True,
    )
    return True

def _save_validation_status(
    config: RoadmapConfig,
    status: str,
) -> None:
    """Update .roadmap-state.json with validation status.

    Adds or updates the ``validation`` key without modifying existing state.

    Parameters
    ----------
    config:
        RoadmapConfig with output_dir.
    status:
        One of "pass", "fail", or "skipped".
    """
    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    if state is None:
        state = {}
    state["validation"] = {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    write_state(state, state_file)


def _auto_invoke_validate(config: RoadmapConfig) -> None:
    """Auto-invoke validation after a successful roadmap pipeline run.

    Inherits --model, --max-turns, --debug from the parent roadmap config.
    Default agent count for roadmap-run invocation is 2 (dual-agent for rigor).
    """
    from .models import AgentSpec, ValidateConfig
    from .validate_executor import execute_validate

    # Default to 2 agents for roadmap-run auto-invocation (dual-agent for rigor per OQ-1)
    validate_agents = config.agents[:2] if len(config.agents) >= 2 else config.agents

    validate_config = ValidateConfig(
        output_dir=config.output_dir,
        agents=validate_agents,
        work_dir=config.output_dir,
        max_turns=config.max_turns,
        model=config.model,
        debug=config.debug,
    )

    print("\n[roadmap] Auto-invoking validation...", flush=True)

    try:
        counts = execute_validate(validate_config)
        blocking = counts.get("blocking_count", 0)
        warning = counts.get("warning_count", 0)
        info = counts.get("info_count", 0)
        print(
            f"[validate] Complete: {blocking} blocking, {warning} warning, {info} info",
            flush=True,
        )
        validation_status = "fail" if blocking > 0 else "pass"
        _save_validation_status(config, validation_status)
    except FileNotFoundError as exc:
        _log.error("Validation skipped: %s", exc)
        print(f"[validate] Skipped: {exc}", file=sys.stderr, flush=True)
        _save_validation_status(config, "skipped")


def check_remediate_resume(
    config: RoadmapConfig,
    gate_fn: Callable,
) -> bool:
    """Check if the remediate step can be skipped on --resume.

    Returns True (skip) when:
    1. remediation-tasklist.md exists
    2. Passes REMEDIATE_GATE
    3. source_report_hash matches current validation report SHA-256

    Returns False (re-run needed) otherwise.
    """
    from .gates import REMEDIATE_GATE

    tasklist_file = config.output_dir / "remediation-tasklist.md"
    if not tasklist_file.exists():
        return False

    passed, _reason = gate_fn(tasklist_file, REMEDIATE_GATE)
    if not passed:
        return False

    # Hash check: verify tasklist was generated from current validation report
    if not _check_tasklist_hash_current(tasklist_file, config.output_dir):
        print(
            "[roadmap] Remediation tasklist stale (hash mismatch), will re-run remediate",
            flush=True,
        )
        return False

    return True


def check_certify_resume(
    config: RoadmapConfig,
    gate_fn: Callable,
) -> bool:
    """Check if the certify step can be skipped on --resume.

    Returns True (skip) when:
    1. certification-report.md exists
    2. Passes CERTIFY_GATE

    Returns False (re-run needed) otherwise.
    """
    from .gates import CERTIFY_GATE

    report_file = config.output_dir / "certification-report.md"
    if not report_file.exists():
        return False

    passed, _reason = gate_fn(report_file, CERTIFY_GATE)
    return passed


def _check_tasklist_hash_current(
    tasklist_file: Path,
    output_dir: Path,
) -> bool:
    """Check if remediation tasklist's source_report_hash matches current report.

    Reads the YAML frontmatter source_report_hash and compares against
    SHA-256 of the validation report file. Returns False on mismatch
    (fail closed).
    """
    from .gates import _parse_frontmatter

    content = tasklist_file.read_text(encoding="utf-8")
    fm = _parse_frontmatter(content)
    if fm is None:
        return False

    saved_hash = fm.get("source_report_hash", "")
    if not saved_hash:
        return False

    # Find the validation report (source_report field)
    source_report = fm.get("source_report", "")
    if source_report:
        report_path = Path(source_report)
        if not report_path.is_absolute():
            report_path = output_dir / report_path
    else:
        # Default to reflect-merged.md or merged-validation-report.md
        report_path = output_dir / "reflect-merged.md"
        if not report_path.exists():
            report_path = output_dir / "merged-validation-report.md"

    if not report_path.exists():
        return False

    current_hash = hashlib.sha256(report_path.read_bytes()).hexdigest()
    return saved_hash == current_hash


def _apply_resume(
    steps: list[Step | list[Step]],
    config: RoadmapConfig,
    gate_fn: Callable,
) -> list[Step | list[Step]]:
    """Apply --resume logic: skip steps whose outputs already pass gates.

    Also checks for stale spec detection.
    """
    state_file = config.output_dir / ".roadmap-state.json"
    state = read_state(state_file)
    force_extract = False
    if state is not None:
        saved_hash = state.get("spec_hash", "")
        current_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
        if saved_hash and saved_hash != current_hash:
            print(
                f"WARNING: spec-file has changed since last run.\n"
                f"  Last hash: {saved_hash[:12]}...\n"
                f"  Current:   {current_hash[:12]}...\n"
                f"Forcing re-run of extract step.",
                file=sys.stderr,
                flush=True,
            )
            force_extract = True

    skipped = 0
    result: list[Step | list[Step]] = []
    found_failure = False

    for entry in steps:
        if found_failure:
            # After first failing step, include all remaining steps
            result.append(entry)
            continue

        if isinstance(entry, list):
            # Parallel group: check all steps
            all_pass = True
            for s in entry:
                if s.gate:
                    passed, _reason = gate_fn(s.output_file, s.gate)
                    if not passed:
                        all_pass = False
                        break
                else:
                    all_pass = False
                    break
            if all_pass:
                skipped += len(entry)
                print(f"[roadmap] Skipping {', '.join(s.id for s in entry)} (gates pass)", flush=True)
            else:
                found_failure = True
                result.append(entry)
        else:
            # Force re-run of extract on stale spec
            if force_extract and entry.id == "extract":
                found_failure = True
                result.append(entry)
                continue

            if entry.gate:
                passed, _reason = gate_fn(entry.output_file, entry.gate)
                if passed:
                    skipped += 1
                    print(f"[roadmap] Skipping {entry.id} (gate passes)", flush=True)
                    continue
            found_failure = True
            result.append(entry)

    if skipped > 0:
        print(f"[roadmap] Skipped {skipped} steps (gates pass)", flush=True)

    if not result:
        print("[roadmap] All steps already pass gates. Nothing to do.", flush=True)

    return result
