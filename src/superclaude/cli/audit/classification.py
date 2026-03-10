"""Two-tier classification engine with backward mapping to v1 categories.

Implements AC1 (core action sections) and AC15 (v2-to-v1 category mapping).

Tier-1 (actionable): findings that require immediate action (DELETE, INVESTIGATE).
Tier-2 (informational): findings that are stable or advisory (KEEP, REORGANIZE).

v1 categories: DELETE, KEEP, INVESTIGATE, REORGANIZE
v2 tiers map deterministically to v1 categories via TIER_TO_V1_MAP.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class V1Category(Enum):
    """Legacy v1 classification categories."""

    DELETE = "DELETE"
    KEEP = "KEEP"
    INVESTIGATE = "INVESTIGATE"
    REORGANIZE = "REORGANIZE"


class V2Tier(Enum):
    """v2 two-tier classification."""

    TIER_1 = "tier-1"  # Actionable
    TIER_2 = "tier-2"  # Informational


class V2Action(Enum):
    """v2 fine-grained action labels assigned during classification."""

    DELETE = "DELETE"
    KEEP = "KEEP"
    INVESTIGATE = "INVESTIGATE"
    REORGANIZE = "REORGANIZE"
    MODIFY = "MODIFY"
    ARCHIVE = "ARCHIVE"
    FLAG = "FLAG"


# Deterministic mapping: (tier, action) -> v1 category
_TIER_ACTION_TO_V1: dict[tuple[V2Tier, V2Action], V1Category] = {
    (V2Tier.TIER_1, V2Action.DELETE): V1Category.DELETE,
    (V2Tier.TIER_1, V2Action.INVESTIGATE): V1Category.INVESTIGATE,
    (V2Tier.TIER_1, V2Action.MODIFY): V1Category.REORGANIZE,
    (V2Tier.TIER_1, V2Action.FLAG): V1Category.INVESTIGATE,
    (V2Tier.TIER_2, V2Action.KEEP): V1Category.KEEP,
    (V2Tier.TIER_2, V2Action.REORGANIZE): V1Category.REORGANIZE,
    (V2Tier.TIER_2, V2Action.ARCHIVE): V1Category.DELETE,
    (V2Tier.TIER_2, V2Action.FLAG): V1Category.KEEP,
}


@dataclass
class ClassificationResult:
    """Result of classifying a single audit finding."""

    file_path: str
    tier: V2Tier
    action: V2Action
    v1_category: V1Category
    confidence: float
    evidence: list[str] = field(default_factory=list)
    qualifiers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "tier": self.tier.value,
            "action": self.action.value,
            "v1_category": self.v1_category.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "qualifiers": self.qualifiers,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClassificationResult:
        return cls(
            file_path=data["file_path"],
            tier=V2Tier(data["tier"]),
            action=V2Action(data["action"]),
            v1_category=V1Category(data["v1_category"]),
            confidence=data["confidence"],
            evidence=data.get("evidence", []),
            qualifiers=data.get("qualifiers", []),
        )


def map_to_v1(tier: V2Tier, action: V2Action) -> V1Category:
    """Map a v2 (tier, action) pair to a v1 category.

    Every valid (tier, action) pair maps to exactly one v1 category.
    Raises ValueError for unmapped combinations.
    """
    key = (tier, action)
    if key not in _TIER_ACTION_TO_V1:
        raise ValueError(
            f"No v1 mapping for tier={tier.value}, action={action.value}"
        )
    return _TIER_ACTION_TO_V1[key]


def classify_finding(
    file_path: str,
    *,
    has_references: bool,
    is_test_or_config: bool = False,
    is_temporal_artifact: bool = False,
    evidence: list[str] | None = None,
    qualifiers: list[str] | None = None,
) -> ClassificationResult:
    """Classify a single audit finding into the two-tier system.

    Deterministic: same inputs always produce same output.

    Args:
        file_path: Path to the file being classified.
        has_references: Whether the file has incoming references from other files.
        is_test_or_config: Whether the file is a test or config file (bias toward KEEP).
        is_temporal_artifact: Whether the file is a temporal artifact (bias toward ARCHIVE).
        evidence: List of evidence strings supporting the classification.
        qualifiers: Additional qualifier labels.

    Returns:
        ClassificationResult with tier, action, v1 mapping, and evidence.
    """
    ev = evidence or []
    quals = qualifiers or []

    if is_temporal_artifact and not has_references:
        tier = V2Tier.TIER_2
        action = V2Action.ARCHIVE
        confidence = 0.85
    elif not has_references:
        tier = V2Tier.TIER_1
        action = V2Action.DELETE
        confidence = 0.90
    elif is_test_or_config:
        tier = V2Tier.TIER_2
        action = V2Action.KEEP
        confidence = 0.95
    elif has_references:
        tier = V2Tier.TIER_2
        action = V2Action.KEEP
        confidence = 0.85
    else:
        tier = V2Tier.TIER_1
        action = V2Action.INVESTIGATE
        confidence = 0.60

    v1_cat = map_to_v1(tier, action)

    return ClassificationResult(
        file_path=file_path,
        tier=tier,
        action=action,
        v1_category=v1_cat,
        confidence=confidence,
        evidence=ev,
        qualifiers=quals,
    )


def all_v1_categories_covered() -> bool:
    """Verify that all 4 v1 categories are reachable from the mapping table."""
    reachable = {v for v in _TIER_ACTION_TO_V1.values()}
    return reachable == set(V1Category)
