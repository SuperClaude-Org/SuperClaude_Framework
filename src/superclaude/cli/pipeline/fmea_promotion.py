"""FMEA deliverable promotion -- promotes failure modes above severity threshold.

Failure modes at or above "wrong_state" severity are promoted to fmea_test deliverables.
Below-threshold modes become accepted risk in metadata.
High-severity findings trigger Release Gate Rule 1 (block downstream progression).

R-008 mitigation: Release Gate Rule 1 ensures FMEA findings are acted on.

NFR-007: No imports from superclaude.cli.sprint or superclaude.cli.roadmap.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .fmea_classifier import (
    DetectionDifficulty,
    FMEAFailureMode,
    Severity,
)
from .models import Deliverable, DeliverableKind


# Default promotion threshold
DEFAULT_PROMOTION_THRESHOLD = Severity.WRONG_STATE


@dataclass
class ReleaseGateViolation:
    """A Release Gate Rule 1 violation triggered by silent corruption."""

    failure_mode: FMEAFailureMode
    rule: str = "Release Gate Rule 1"
    reason: str = ""
    accepted: bool = False
    accepted_by: str = ""
    acceptance_rationale: str = ""


@dataclass
class FMEAPromotionOutput:
    """Output of the FMEA deliverable promotion pass.

    Attributes:
        promoted_deliverables: Generated fmea_test deliverables for above-threshold modes.
        accepted_risks: Below-threshold modes recorded as accepted risk.
        release_gate_violations: Silent corruption findings that block downstream.
        section_markdown: Rendered markdown section for pipeline output.
    """

    promoted_deliverables: list[Deliverable] = field(default_factory=list)
    accepted_risks: list[dict] = field(default_factory=list)
    release_gate_violations: list[ReleaseGateViolation] = field(default_factory=list)
    section_markdown: str = ""

    @property
    def has_blocking_violations(self) -> bool:
        """True if there are unresolved release gate violations."""
        return any(not v.accepted for v in self.release_gate_violations)


def promote_failure_modes(
    failure_modes: list[FMEAFailureMode],
    promotion_threshold: Severity = DEFAULT_PROMOTION_THRESHOLD,
) -> FMEAPromotionOutput:
    """Promote failure modes above severity threshold to fmea_test deliverables.

    Args:
        failure_modes: Classified failure modes from the FMEA classifier.
        promotion_threshold: Severity at/above which modes are promoted.

    Returns:
        FMEAPromotionOutput with promoted deliverables, accepted risks, and gate violations.
    """
    if not failure_modes:
        return FMEAPromotionOutput(
            section_markdown=_render_empty_section(),
        )

    promoted: list[Deliverable] = []
    accepted_risks: list[dict] = []
    violations: list[ReleaseGateViolation] = []
    seq = 1

    for mode in failure_modes:
        if mode.severity >= promotion_threshold:
            # Promote to fmea_test deliverable
            milestone = _extract_milestone(mode.deliverable_id)
            deliverable_id = f"D{milestone}.{seq}.fmea"

            description = (
                f"FMEA test: verify {mode.deliverable_id} handles "
                f"{mode.domain_description} input. "
                f"Detection: {mode.detection_difficulty.value}, "
                f"severity: {mode.severity.value}. "
                f"Detection mechanism: {mode.description[:100]}"
            )

            d = Deliverable(
                id=deliverable_id,
                description=description,
                kind=DeliverableKind.FMEA_TEST,
                metadata={
                    "source_deliverable_id": mode.deliverable_id,
                    "domain_description": mode.domain_description,
                    "detection_difficulty": mode.detection_difficulty.value,
                    "severity": mode.severity.value,
                    "signal_source": mode.signal_source,
                    "invariant_predicate": mode.invariant_predicate,
                },
            )
            promoted.append(d)
            seq += 1

            # Silent corruption triggers Release Gate Rule 1
            if mode.detection_difficulty == DetectionDifficulty.SILENT:
                violations.append(ReleaseGateViolation(
                    failure_mode=mode,
                    reason=(
                        f"Silent corruption detected in {mode.deliverable_id}: "
                        f"{mode.description[:150]}"
                    ),
                ))
        else:
            # Below threshold: record as accepted risk
            accepted_risks.append({
                "deliverable_id": mode.deliverable_id,
                "domain_description": mode.domain_description,
                "detection_difficulty": mode.detection_difficulty.value,
                "severity": mode.severity.value,
                "rationale": (
                    f"Below promotion threshold ({promotion_threshold.value}). "
                    f"Severity: {mode.severity.value}."
                ),
            })

    section = _render_promotion_section(promoted, accepted_risks, violations)

    return FMEAPromotionOutput(
        promoted_deliverables=promoted,
        accepted_risks=accepted_risks,
        release_gate_violations=violations,
        section_markdown=section,
    )


def accept_violation(
    violation: ReleaseGateViolation,
    accepted_by: str,
    rationale: str,
) -> None:
    """Accept a release gate violation with named owner and documented rationale.

    Args:
        violation: The violation to accept.
        accepted_by: Named owner accepting the risk (must not be empty).
        rationale: Documented rationale for acceptance (must not be empty).

    Raises:
        ValueError: If accepted_by or rationale is empty.
    """
    if not accepted_by or not accepted_by.strip():
        raise ValueError("accepted_by must not be empty")
    if not rationale or not rationale.strip():
        raise ValueError("acceptance_rationale must not be empty")

    violation.accepted = True
    violation.accepted_by = accepted_by.strip()
    violation.acceptance_rationale = rationale.strip()


def _extract_milestone(deliverable_id: str) -> str:
    """Extract milestone number from deliverable ID."""
    m = re.match(r"D(\d+)\.", deliverable_id)
    if m:
        return m.group(1)
    m = re.match(r"D-(\d+)", deliverable_id)
    if m:
        return m.group(1)
    return deliverable_id.lstrip("D-")


def _render_empty_section() -> str:
    return "## FMEA Failure Mode Analysis\n\nNo failure modes detected.\n"


def _render_promotion_section(
    promoted: list[Deliverable],
    accepted_risks: list[dict],
    violations: list[ReleaseGateViolation],
) -> str:
    """Render the FMEA promotion section as markdown."""
    lines = ["## FMEA Failure Mode Analysis", ""]
    lines.append(f"**Promoted to fmea_test**: {len(promoted)}")
    lines.append(f"**Accepted risk**: {len(accepted_risks)}")
    lines.append(f"**Release Gate violations**: {len(violations)}")
    lines.append("")

    if violations:
        lines.append("### Release Gate Rule 1 Violations")
        lines.append("")
        lines.append("| Source | Domain | Description | Status |")
        lines.append("|--------|--------|-------------|--------|")
        for v in violations:
            status = "ACCEPTED" if v.accepted else "**BLOCKING**"
            lines.append(
                f"| {v.failure_mode.deliverable_id} | "
                f"{v.failure_mode.domain_description} | "
                f"{v.reason[:80]}... | {status} |"
            )
        lines.append("")

    if promoted:
        lines.append("### Promoted Deliverables")
        lines.append("")
        for d in promoted:
            lines.append(f"- `{d.id}`: {d.description[:80]}...")
        lines.append("")

    if accepted_risks:
        lines.append("### Accepted Risks")
        lines.append("")
        lines.append("| Deliverable | Domain | Severity | Rationale |")
        lines.append("|-------------|--------|----------|-----------|")
        for risk in accepted_risks:
            lines.append(
                f"| {risk['deliverable_id']} | {risk['domain_description']} | "
                f"{risk['severity']} | {risk['rationale'][:60]}... |"
            )
        lines.append("")

    return "\n".join(lines)
