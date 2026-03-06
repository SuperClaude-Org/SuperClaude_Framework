"""Tiered KEEP evidence enforcement with graduated requirements.

Implements T03.04 / D-0020: KEEP classifications carry evidence proportional
to risk tier. High-risk KEEP needs stronger evidence than low-risk.

Evidence tiers:
  - low-risk KEEP: 1 reference required
  - medium-risk KEEP: 2 references required
  - high-risk KEEP: 3+ references required

Insufficient evidence triggers escalation before final rejection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .classification import ClassificationResult, V2Action


# Tier thresholds
TIER_REQUIREMENTS: dict[str, int] = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


@dataclass
class TieredGateResult:
    """Result of tiered KEEP evidence gate."""

    file_path: str
    risk_tier: str
    required_references: int
    found_references: int
    passed: bool
    escalation_attempted: bool = False
    reason: str | None = None
    matched_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "risk_tier": self.risk_tier,
            "required_references": self.required_references,
            "found_references": self.found_references,
            "passed": self.passed,
            "escalation_attempted": self.escalation_attempted,
            "reason": self.reason,
        }


def _count_references(evidence: list[str]) -> tuple[int, list[str]]:
    """Count reference evidence entries.

    Returns (count, matched_entries).
    """
    ref_keywords = {"ref", "import", "reference", "usage", "used by", "imported by"}
    matched = []
    for ev in evidence:
        ev_lower = ev.lower()
        if any(kw in ev_lower for kw in ref_keywords):
            matched.append(ev)
    return len(matched), matched


def check_tiered_keep(
    result: ClassificationResult,
    risk_tier: str,
    additional_evidence: list[str] | None = None,
) -> TieredGateResult:
    """Enforce tiered KEEP evidence requirements.

    Args:
        result: Classification result to check.
        risk_tier: File's risk tier ("low", "medium", "high").
        additional_evidence: Extra evidence for escalation attempt.

    Returns:
        TieredGateResult with pass/fail and escalation info.
    """
    # Only enforce for KEEP actions
    if result.action != V2Action.KEEP:
        return TieredGateResult(
            file_path=result.file_path,
            risk_tier=risk_tier,
            required_references=0,
            found_references=0,
            passed=True,
            reason="Non-KEEP action, gate not applicable",
        )

    required = TIER_REQUIREMENTS.get(risk_tier, 1)
    found, matched = _count_references(result.evidence)

    if found >= required:
        return TieredGateResult(
            file_path=result.file_path,
            risk_tier=risk_tier,
            required_references=required,
            found_references=found,
            passed=True,
            matched_evidence=matched,
        )

    # Attempt escalation with additional evidence
    if additional_evidence:
        all_evidence = result.evidence + additional_evidence
        found_escalated, matched_escalated = _count_references(all_evidence)

        if found_escalated >= required:
            return TieredGateResult(
                file_path=result.file_path,
                risk_tier=risk_tier,
                required_references=required,
                found_references=found_escalated,
                passed=True,
                escalation_attempted=True,
                matched_evidence=matched_escalated,
            )

        return TieredGateResult(
            file_path=result.file_path,
            risk_tier=risk_tier,
            required_references=required,
            found_references=found_escalated,
            passed=False,
            escalation_attempted=True,
            reason=(
                f"KEEP for {risk_tier}-risk file requires {required} references, "
                f"found {found_escalated} after escalation"
            ),
            matched_evidence=matched_escalated,
        )

    # No escalation possible, reject
    return TieredGateResult(
        file_path=result.file_path,
        risk_tier=risk_tier,
        required_references=required,
        found_references=found,
        passed=False,
        reason=(
            f"KEEP for {risk_tier}-risk file requires {required} references, "
            f"found {found}"
        ),
        matched_evidence=matched,
    )
