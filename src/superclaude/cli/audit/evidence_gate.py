"""Evidence-gated DELETE and KEEP classification rules.

Implements AC4 (DELETE requires zero-reference evidence) and
AC5 (KEEP requires reference evidence for tier-1/tier-2 files).

The evidence gate sits in the classification pipeline and blocks:
- DELETE without zero-reference proof
- Tier-1/Tier-2 KEEP without at least one reference evidence record
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .classification import ClassificationResult, V2Action, V2Tier


@dataclass
class GateResult:
    """Result of an evidence gate check."""

    passed: bool
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "reason": self.reason}


def check_delete_evidence(result: ClassificationResult) -> GateResult:
    """Verify DELETE entries carry zero-reference evidence.

    Returns GateResult with passed=False if a DELETE classification
    lacks evidence proving zero references.
    """
    if result.action != V2Action.DELETE:
        return GateResult(passed=True)

    has_zero_ref_evidence = any(
        "zero" in e.lower() and "ref" in e.lower()
        for e in result.evidence
    )
    if not has_zero_ref_evidence:
        return GateResult(
            passed=False,
            reason=f"DELETE classification for {result.file_path} lacks zero-reference evidence",
        )
    return GateResult(passed=True)


def check_keep_evidence(result: ClassificationResult) -> GateResult:
    """Verify KEEP entries for tier-1/tier-2 carry reference evidence.

    Returns GateResult with passed=False if a KEEP classification
    at tier-1 or tier-2 lacks reference evidence.
    """
    if result.action != V2Action.KEEP:
        return GateResult(passed=True)

    if result.tier not in (V2Tier.TIER_1, V2Tier.TIER_2):
        return GateResult(passed=True)

    has_ref_evidence = any(
        "ref" in e.lower() for e in result.evidence
    )
    if not has_ref_evidence:
        return GateResult(
            passed=False,
            reason=f"KEEP classification for {result.file_path} lacks reference evidence",
        )
    return GateResult(passed=True)


def evidence_gate(result: ClassificationResult) -> GateResult:
    """Run all evidence gates on a classification result.

    Combines DELETE and KEEP evidence checks.
    Returns first failure or passes.
    """
    delete_check = check_delete_evidence(result)
    if not delete_check.passed:
        return delete_check

    keep_check = check_keep_evidence(result)
    if not keep_check.passed:
        return keep_check

    return GateResult(passed=True)
