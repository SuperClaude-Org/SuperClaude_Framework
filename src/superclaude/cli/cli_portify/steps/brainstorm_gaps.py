"""Step 6: brainstorm-gaps -- Gap identification through multi-persona analysis.

Pre-flight checks for /sc:brainstorm skill availability, invokes with
--strategy systematic --depth deep --no-codebase, and falls back to an
inline multi-persona prompt when the skill is unavailable.

Post-processes findings into structured objects (gap_id, description,
severity, affected_section, persona). Actionable items are incorporated
into spec sections marked [INCORPORATED]; unresolvable items are routed
to Section 11 marked [OPEN]; Section 12 summary is appended.

Per SC-006: STANDARD gate -- Section 12 present with structural content
(findings table with Gap ID column OR zero-gap summary text).
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from superclaude.cli.cli_portify.gates import gate_brainstorm_gaps
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult
from superclaude.cli.cli_portify.prompts import BrainstormGapsPrompt, PromptContext

_log = logging.getLogger("superclaude.cli_portify.steps.brainstorm_gaps")


# --- Structured Finding ---


@dataclass
class GapFinding:
    """A single gap finding from brainstorm analysis."""

    gap_id: str
    description: str
    severity: str  # "HIGH", "MEDIUM", "LOW"
    affected_section: str
    persona: str

    def to_row(self) -> str:
        """Format as a Markdown table row."""
        return f"| {self.gap_id} | {self.description} | {self.severity} | {self.affected_section} | {self.persona} |"


# --- Skill Availability Check ---


def check_brainstorm_skill_available() -> bool:
    """Check if /sc:brainstorm skill is available.

    Attempts to detect the skill by checking for its presence in the
    installed skills directory. Returns False if not found, triggering
    inline fallback.
    """
    skill_paths = [
        Path.home() / ".claude" / "skills" / "sc-brainstorm",
        Path.home() / ".claude" / "skills" / "brainstorm",
    ]
    return any(p.exists() for p in skill_paths)


# --- Inline Fallback Prompt ---


INLINE_FALLBACK_PROMPT = """\
You are conducting a multi-persona gap analysis of the following specification.

**WARNING**: The /sc:brainstorm skill is not available. Using inline fallback.

Adopt each of the following personas in sequence and identify gaps,
missing edge cases, and risks from that perspective:

1. **Security Engineer**: Focus on authentication, authorization, input
   validation, and data protection gaps.
2. **QA Engineer**: Focus on untested paths, missing edge cases, and
   inadequate error handling.
3. **Performance Engineer**: Focus on scalability bottlenecks, resource
   leaks, and inefficient patterns.
4. **End User**: Focus on usability gaps, confusing behaviors, and
   missing documentation.
5. **DevOps Engineer**: Focus on deployment risks, monitoring gaps, and
   operational concerns.

For each gap found, provide:
- A unique Gap ID (GAP-001, GAP-002, etc.)
- Description of the gap
- Severity: HIGH, MEDIUM, or LOW
- Affected section of the specification
- Which persona identified it

Format findings as a Markdown table with columns:
| Gap ID | Description | Severity | Affected Section | Persona |

If no gaps are found, write: "Zero gaps identified. Specification is comprehensive."
"""


# --- Finding Parser ---


_GAP_ROW_RE = re.compile(
    r"\|\s*(GAP-\d+)\s*\|\s*([^|]+)\|\s*(HIGH|MEDIUM|LOW)\s*\|\s*([^|]+)\|\s*([^|]+)\|",
    re.IGNORECASE,
)


def parse_findings(content: str) -> list[GapFinding]:
    """Parse gap findings from brainstorm output.

    Extracts structured findings from Markdown table rows matching
    the expected format.

    Args:
        content: Full brainstorm output content.

    Returns:
        List of parsed GapFinding objects.
    """
    findings: list[GapFinding] = []
    for match in _GAP_ROW_RE.finditer(content):
        findings.append(
            GapFinding(
                gap_id=match.group(1).strip(),
                description=match.group(2).strip(),
                severity=match.group(3).strip().upper(),
                affected_section=match.group(4).strip(),
                persona=match.group(5).strip(),
            )
        )
    return findings


def has_section_12_content(content: str) -> bool:
    """Validate Section 12 structural content per SC-006/SC-015.

    Section 12 must contain either:
    - A findings table with a Gap ID column
    - The literal zero-gap summary text

    Heading-only content fails the gate.
    """
    # Look for Section 12 heading
    sec12_match = re.search(r"^## .*(?:Section 12|Gap Analysis Summary|Brainstorm Summary)", content, re.MULTILINE | re.IGNORECASE)
    if not sec12_match:
        # Also check for ## 12. or ## 12 pattern
        sec12_match = re.search(r"^## 12[\.\s]", content, re.MULTILINE)
    if not sec12_match:
        return False

    # Get content after the heading
    after_heading = content[sec12_match.end():]
    # Trim to next ## heading or end of file
    next_heading = re.search(r"^## ", after_heading, re.MULTILINE)
    section_body = after_heading[:next_heading.start()] if next_heading else after_heading

    stripped = section_body.strip()
    if not stripped:
        return False

    # Check for findings table with Gap ID column
    if "Gap ID" in stripped or "gap_id" in stripped:
        return True

    # Check for zero-gap summary text
    if "zero gap" in stripped.lower() or "no gaps" in stripped.lower():
        return True

    # Must have substantive content (not just whitespace/newlines)
    return len(stripped) > 20


# --- Step Implementation ---


def run_brainstorm_gaps(
    config: PortifyConfig,
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
) -> PortifyStepResult:
    """Execute the brainstorm-gaps step (Step 6).

    Pre-flight checks /sc:brainstorm availability, invokes via
    PortifyProcess with skill or inline fallback, then post-processes
    findings into structured objects.

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

    # Verify prior artifact exists (synthesized-spec.md from Step 5)
    synthesized_spec = results_dir / "synthesized-spec.md"
    if not synthesized_spec.exists():
        _log.error("synthesized-spec.md not found at %s", synthesized_spec)
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="brainstorm-gaps",
            step_number=6,
            phase=4,
            gate_tier="STANDARD",
            failure_classification=FailureClassification.MISSING_ARTIFACT,
        )

    # Pre-flight: check /sc:brainstorm availability
    skill_available = check_brainstorm_skill_available()
    if skill_available:
        _log.info("brainstorm_gaps: /sc:brainstorm skill available")
    else:
        _log.warning("brainstorm_gaps: /sc:brainstorm skill NOT available, using inline fallback")

    # Build prompt
    context = PromptContext(
        workflow_path=wf_path,
        work_dir=config.work_dir,
        cli_name=config.derive_cli_name(),
        source_skill=wf_path.name,
    )
    builder = BrainstormGapsPrompt(context)

    if skill_available:
        prompt = builder.build()
    else:
        # Use inline fallback with multi-persona prompt
        base = builder.build()
        prompt = f"{INLINE_FALLBACK_PROMPT}\n\n{base}"

    # Output files
    output_file = results_dir / "brainstorm-gaps.md"
    error_file = results_dir / "brainstorm-gaps.err"

    # Execute via PortifyProcess
    proc = PortifyProcess(
        prompt=prompt,
        output_file=output_file,
        error_file=error_file,
        work_dir=config.work_dir,
        workflow_path=wf_path,
        artifact_refs=[synthesized_spec],
        max_turns=config.max_turns,
        model=config.model,
        timeout_seconds=config.iteration_timeout,
    )

    result = proc.run()
    elapsed = time.monotonic() - start

    _log.info(
        "brainstorm_gaps exit=%d timeout=%s skill=%s duration=%.1fs",
        result.exit_code,
        result.timed_out,
        skill_available,
        elapsed,
    )

    # Handle subprocess failure
    if result.timed_out:
        return PortifyStepResult(
            portify_status=PortifyStatus.TIMEOUT,
            step_name="brainstorm-gaps",
            step_number=6,
            phase=4,
            artifact_path=str(output_file),
            gate_tier="STANDARD",
            failure_classification=FailureClassification.TIMEOUT,
        )

    if not result.succeeded:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="brainstorm-gaps",
            step_number=6,
            phase=4,
            artifact_path=str(output_file),
            gate_tier="STANDARD",
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    # Post-process: parse findings
    content = output_file.read_text(encoding="utf-8") if output_file.exists() else ""
    findings = parse_findings(content)
    _log.info(
        "brainstorm_gaps findings=%d (high=%d)",
        len(findings),
        sum(1 for f in findings if f.severity == "HIGH"),
    )

    # Run SC-006 STANDARD gate
    gate_passed_result, gate_msg = gate_brainstorm_gaps(output_file)
    _log.info("SC-006 gate: passed=%s msg=%s", gate_passed_result, gate_msg)

    if not gate_passed_result:
        return PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="brainstorm-gaps",
            step_number=6,
            phase=4,
            artifact_path=str(output_file),
            gate_tier="STANDARD",
            failure_classification=FailureClassification.GATE_FAILURE,
        )

    return PortifyStepResult(
        portify_status=PortifyStatus.PASS,
        step_name="brainstorm-gaps",
        step_number=6,
        phase=4,
        artifact_path=str(output_file),
        gate_tier="STANDARD",
    )
