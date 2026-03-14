"""Step 7: panel-review -- Multi-iteration panel review with convergence.

Runs focus+critique passes per iteration with quality scoring,
downstream readiness gating (7.0 boundary), and convergence loop
integration. Each iteration runs as a single Claude subprocess with
per-iteration independent timeout (default 300s per SC-016).

Integrates:
- Convergence engine (D-0030) for iteration management
- Section hashing (D-0033/NFR-008) for additive-only enforcement
- Quality scoring: clarity, completeness, testability, consistency
- Downstream readiness gate: overall >= 7.0 passes (SC-009)
- User review gate at end of panel-review step

Per SC-007: STRICT gate -- convergence terminal state reached,
quality scores populated, downstream readiness evaluated.
"""

from __future__ import annotations

import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from superclaude.cli.cli_portify.convergence import (
    ConvergenceEngine,
    ConvergenceResult,
    ConvergenceState,
    IterationResult,
    SimpleBudgetGuard,
)
from superclaude.cli.cli_portify.gates import gate_panel_review
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult
from superclaude.cli.cli_portify.prompts import PanelReviewPrompt, PromptContext
from superclaude.cli.cli_portify.utils import (
    extract_sections,
    hash_section,
    verify_additive_only,
)

_log = logging.getLogger("superclaude.cli_portify.steps.panel_review")


# --- Quality Score Parsing ---


_SCORE_RE = re.compile(
    r"(?:^|\|)\s*(\w+)\s*[:\|]\s*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
    re.MULTILINE,
)

QUALITY_DIMENSIONS = ("clarity", "completeness", "testability", "consistency")

DOWNSTREAM_READINESS_THRESHOLD = 7.0


def parse_quality_scores(content: str) -> dict[str, float]:
    """Parse quality dimension scores from panel review output.

    Looks for patterns like:
    - clarity: 8.5
    - | completeness | 7.0 |
    - testability: 9/10

    Args:
        content: Panel review output content.

    Returns:
        Dict mapping dimension name to score (0-10 scale).
    """
    scores: dict[str, float] = {}
    content_lower = content.lower()

    for dim in QUALITY_DIMENSIONS:
        # Try pattern: dimension: score or dimension | score
        pattern = re.compile(
            rf"{dim}\s*[:\|]\s*(\d+(?:\.\d+)?)",
            re.IGNORECASE,
        )
        match = pattern.search(content)
        if match:
            scores[dim] = float(match.group(1))

    return scores


def compute_overall_score(scores: dict[str, float]) -> float:
    """Compute overall quality score as mean of 4 dimensions.

    Per SC-008: overall = mean of clarity, completeness, testability,
    consistency (+/- 0.01 tolerance).

    Args:
        scores: Dict of dimension scores.

    Returns:
        Mean of the 4 dimensions, or 0.0 if no scores.
    """
    values = [scores.get(d, 0.0) for d in QUALITY_DIMENSIONS]
    if not any(values):
        return 0.0
    return sum(values) / len(QUALITY_DIMENSIONS)


def check_downstream_readiness(overall_score: float) -> bool:
    """Check downstream readiness gate per SC-009.

    Boundary: 7.0 true, 6.9 false.

    Args:
        overall_score: Overall quality score.

    Returns:
        True if overall >= 7.0.
    """
    return overall_score >= DOWNSTREAM_READINESS_THRESHOLD


# --- CRITICAL Finding Counter ---


_CRITICAL_RE = re.compile(r"\bCRITICAL\b", re.IGNORECASE)


def count_unaddressed_criticals(content: str) -> int:
    """Count unaddressed CRITICAL findings in panel review output.

    Looks for the word CRITICAL in the findings, excluding resolved ones.

    Args:
        content: Panel review output content.

    Returns:
        Count of unaddressed CRITICAL findings.
    """
    # Count all CRITICAL mentions
    criticals = len(_CRITICAL_RE.findall(content))

    # Subtract resolved CRITICALs (marked with [RESOLVED] or strikethrough)
    resolved = len(re.findall(r"\[RESOLVED\].*CRITICAL|~~.*CRITICAL.*~~", content, re.IGNORECASE))

    return max(0, criticals - resolved)


# --- Section Hashing for Additive-Only (D-0033 / NFR-008) ---


def capture_section_hashes(content: str) -> dict[str, str]:
    """Capture section hashes before an iteration.

    Args:
        content: Document content to hash.

    Returns:
        Dict mapping section heading to SHA-256 hash.
    """
    sections = extract_sections(content)
    return {heading: hash_section(body) for heading, body in sections.items()}


# --- User Review Gate ---


def prompt_user_review(skip_review: bool = False) -> bool:
    """Prompt user for review acceptance at end of panel-review.

    Args:
        skip_review: If True, auto-accept without prompting.

    Returns:
        True if accepted, False if rejected.
    """
    if skip_review:
        return True

    try:
        response = input("\nAccept panel review result? [y/N]: ").strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


# --- Panel Report Generation (D-0034) ---


def generate_panel_report(
    convergence_result: ConvergenceResult,
    quality_scores: dict[str, float],
    overall_score: float,
    downstream_ready: bool,
    output_path: Path,
) -> None:
    """Generate panel-report.md with machine-readable convergence block.

    Produces YAML frontmatter with terminal state, iteration count,
    quality scores, and human-readable summary.

    Args:
        convergence_result: Final convergence engine result.
        quality_scores: Quality dimension scores.
        overall_score: Computed overall score.
        downstream_ready: Whether downstream readiness gate passed.
        output_path: Path to write the report.
    """
    # Build YAML frontmatter
    fm_lines = [
        "---",
        f"terminal_state: {convergence_result.state.value}",
        f"iteration_count: {convergence_result.iterations_completed}",
    ]

    for dim in QUALITY_DIMENSIONS:
        fm_lines.append(f"{dim}: {quality_scores.get(dim, 0.0):.1f}")
    fm_lines.append(f"overall: {overall_score:.2f}")
    fm_lines.append(f"downstream_ready: {str(downstream_ready).lower()}")

    if convergence_result.escalation_reason:
        fm_lines.append(f"escalation_reason: {convergence_result.escalation_reason.value}")

    fm_lines.append("---")

    # Build human-readable body
    body_lines = [
        "",
        "# Panel Review Report",
        "",
        "## Convergence Summary",
        "",
        f"- **Terminal State**: {convergence_result.state.value.upper()}",
        f"- **Iterations Completed**: {convergence_result.iterations_completed}",
        f"- **Overall Quality Score**: {overall_score:.2f}/10",
        f"- **Downstream Ready**: {'Yes' if downstream_ready else 'No'}",
        "",
    ]

    if convergence_result.escalation_reason:
        body_lines.extend([
            f"- **Escalation Reason**: {convergence_result.escalation_reason.value}",
            "",
        ])

    body_lines.extend([
        "## Quality Scores",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
    ])
    for dim in QUALITY_DIMENSIONS:
        score = quality_scores.get(dim, 0.0)
        body_lines.append(f"| {dim} | {score:.1f} |")
    body_lines.append(f"| **overall** | **{overall_score:.2f}** |")

    body_lines.extend([
        "",
        "## Downstream Readiness",
        "",
        f"Overall score {overall_score:.2f} {'meets' if downstream_ready else 'does not meet'} "
        f"the {DOWNSTREAM_READINESS_THRESHOLD:.1f} threshold.",
    ])

    content = "\n".join(fm_lines + body_lines) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    _log.info("panel_report written to %s", output_path)


# --- Step Implementation ---


def run_panel_review(
    config: PortifyConfig,
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
) -> PortifyStepResult:
    """Execute the panel-review step (Step 7).

    Runs iterative panel review with convergence engine, section
    hashing for additive-only enforcement, quality scoring, and
    downstream readiness gating.

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

    # Verify prior artifacts
    synthesized_spec = results_dir / "synthesized-spec.md"
    brainstorm_gaps = results_dir / "brainstorm-gaps.md"
    for required, name in [
        (synthesized_spec, "synthesized-spec.md"),
        (brainstorm_gaps, "brainstorm-gaps.md"),
    ]:
        if not required.exists():
            _log.error("%s not found at %s", name, required)
            return PortifyStepResult(
                portify_status=PortifyStatus.FAIL,
                step_name="panel-review",
                step_number=7,
                phase=4,
                gate_tier="STRICT",
                failure_classification=FailureClassification.MISSING_ARTIFACT,
            )

    # Initialize convergence engine
    budget_guard = SimpleBudgetGuard(
        total_budget=config.max_convergence * 2.0,
        per_iteration_cost=1.0,
    )
    engine = ConvergenceEngine(
        max_iterations=config.max_convergence,
        budget_guard=budget_guard,
    )

    # Build prompt context
    prompt_context = PromptContext(
        workflow_path=wf_path,
        work_dir=config.work_dir,
        cli_name=config.derive_cli_name(),
        source_skill=wf_path.name,
        max_convergence=config.max_convergence,
    )

    # Output files
    output_file = results_dir / "panel-review.md"
    error_file = results_dir / "panel-review.err"
    report_file = results_dir / "panel-report.md"

    # Capture initial section hashes for additive-only enforcement
    current_content = ""
    section_hashes: dict[str, str] = {}

    # Quality scores across iterations
    quality_scores: dict[str, float] = {}

    # Iteration loop
    while not engine.is_done:
        iteration = engine.current_iteration + 1

        # Budget guard check
        if not engine.check_budget(1.0):
            engine.escalate_budget()
            break

        _log.info("panel_review iteration=%d/%d", iteration, config.max_convergence)

        # Update prompt context with iteration number
        prompt_context.iteration = iteration
        builder = PanelReviewPrompt(prompt_context)
        prompt = builder.build()

        # Execute via PortifyProcess
        proc = PortifyProcess(
            prompt=prompt,
            output_file=output_file,
            error_file=error_file,
            work_dir=config.work_dir,
            workflow_path=wf_path,
            artifact_refs=[synthesized_spec, brainstorm_gaps],
            max_turns=config.max_turns,
            model=config.model,
            timeout_seconds=config.iteration_timeout,
        )

        result = proc.run()
        elapsed = time.monotonic() - start

        _log.info(
            "panel_review iteration=%d exit=%d timeout=%s duration=%.1fs",
            iteration,
            result.exit_code,
            result.timed_out,
            elapsed,
        )

        # Handle subprocess failure
        if result.timed_out:
            return PortifyStepResult(
                portify_status=PortifyStatus.TIMEOUT,
                step_name="panel-review",
                step_number=7,
                phase=4,
                artifact_path=str(output_file),
                gate_tier="STRICT",
                iteration_number=iteration,
                failure_classification=FailureClassification.TIMEOUT,
            )

        if not result.succeeded:
            return PortifyStepResult(
                portify_status=PortifyStatus.FAIL,
                step_name="panel-review",
                step_number=7,
                phase=4,
                artifact_path=str(output_file),
                gate_tier="STRICT",
                iteration_number=iteration,
                failure_classification=FailureClassification.GATE_FAILURE,
            )

        # Read iteration output
        new_content = output_file.read_text(encoding="utf-8") if output_file.exists() else ""

        # Section hashing: verify additive-only (skip on first iteration)
        if section_hashes:
            violations = verify_additive_only(section_hashes, new_content)
            if violations:
                _log.warning(
                    "panel_review iteration=%d additive-only violations: %s",
                    iteration,
                    violations,
                )
                # Reject this iteration's output per NFR-008
                return PortifyStepResult(
                    portify_status=PortifyStatus.FAIL,
                    step_name="panel-review",
                    step_number=7,
                    phase=4,
                    artifact_path=str(output_file),
                    gate_tier="STRICT",
                    iteration_number=iteration,
                    failure_classification=FailureClassification.GATE_FAILURE,
                )

        # Update section hashes for next iteration
        current_content = new_content
        section_hashes = capture_section_hashes(current_content)

        # Parse quality scores
        quality_scores = parse_quality_scores(current_content)
        overall = compute_overall_score(quality_scores)

        # Count criticals
        criticals = count_unaddressed_criticals(current_content)

        # Submit to convergence engine
        iter_result = IterationResult(
            iteration=iteration,
            unaddressed_criticals=criticals,
            quality_scores=quality_scores,
            content=current_content,
        )
        engine.submit(iter_result)

        # Record budget spend
        budget_guard.record_spend(1.0)

    # Get convergence result
    conv_result = engine.result()
    overall = compute_overall_score(quality_scores)
    downstream_ready = check_downstream_readiness(overall)

    _log.info(
        "panel_review complete: state=%s iterations=%d overall=%.2f downstream_ready=%s",
        conv_result.state.value,
        conv_result.iterations_completed,
        overall,
        downstream_ready,
    )

    # Generate panel-report.md (D-0034)
    generate_panel_report(
        convergence_result=conv_result,
        quality_scores=quality_scores,
        overall_score=overall,
        downstream_ready=downstream_ready,
        output_path=report_file,
    )

    # User review gate (at end of panel-review)
    user_accepted = prompt_user_review(skip_review=config.skip_review)
    if not user_accepted:
        engine.escalate_user()
        conv_result = engine.result()
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="panel-review",
            step_number=7,
            phase=4,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            iteration_number=conv_result.iterations_completed,
            review_required=True,
            review_accepted=False,
            failure_classification=FailureClassification.USER_REJECTION,
        )

    # Run SC-007 STRICT gate
    gate_passed_result, gate_msg = gate_panel_review(output_file)
    _log.info("SC-007 gate: passed=%s msg=%s", gate_passed_result, gate_msg)

    if not gate_passed_result:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="panel-review",
            step_number=7,
            phase=4,
            artifact_path=str(output_file),
            gate_tier="STRICT",
            iteration_number=conv_result.iterations_completed,
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    return PortifyStepResult(
        portify_status=PortifyStatus.PASS,
        step_name="panel-review",
        step_number=7,
        phase=4,
        artifact_path=str(output_file),
        gate_tier="STRICT",
        iteration_number=conv_result.iterations_completed,
        review_required=True,
        review_accepted=True,
    )
