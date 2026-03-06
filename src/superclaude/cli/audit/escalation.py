"""Signal-triggered full-file escalation for ambiguous classifications.

Implements T03.03 / D-0019: detects low-confidence classification signals
and initiates full-file read for deeper evidence gathering.

Escalation signals:
  - confidence < 0.6
  - conflicting evidence (import says KEEP, no references says DELETE)
  - INVESTIGATE classification (inherently ambiguous)

Escalation is bounded by configurable token limit to prevent excessive reads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .classification import ClassificationResult, V2Action, V2Tier, classify_finding


# Default escalation configuration
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_MAX_LINES = 500
DEFAULT_TOKEN_BUDGET = 5000  # approximate tokens per escalation


@dataclass
class EscalationConfig:
    """Configuration for escalation trigger."""

    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    max_file_lines: int = DEFAULT_MAX_LINES
    token_budget: int = DEFAULT_TOKEN_BUDGET


@dataclass
class EscalationSignal:
    """A detected escalation signal."""

    signal_type: str  # "low_confidence", "conflicting_evidence", "investigate_status"
    description: str
    original_confidence: float


@dataclass
class EscalationResult:
    """Result of an escalation attempt."""

    file_path: str
    triggered: bool
    signals: list[EscalationSignal] = field(default_factory=list)
    original_classification: ClassificationResult | None = None
    escalated_classification: ClassificationResult | None = None
    tokens_used: int = 0
    bounded: bool = False  # True if escalation was token-bounded

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "triggered": self.triggered,
            "signals": [
                {
                    "type": s.signal_type,
                    "description": s.description,
                    "original_confidence": s.original_confidence,
                }
                for s in self.signals
            ],
            "tokens_used": self.tokens_used,
            "bounded": self.bounded,
            "original_confidence": (
                self.original_classification.confidence
                if self.original_classification else None
            ),
            "escalated_confidence": (
                self.escalated_classification.confidence
                if self.escalated_classification else None
            ),
        }


def detect_signals(
    result: ClassificationResult,
    config: EscalationConfig | None = None,
) -> list[EscalationSignal]:
    """Detect escalation signals in a classification result."""
    cfg = config or EscalationConfig()
    signals: list[EscalationSignal] = []

    # Signal 1: Low confidence
    if result.confidence < cfg.confidence_threshold:
        signals.append(EscalationSignal(
            signal_type="low_confidence",
            description=f"Confidence {result.confidence:.2f} < threshold {cfg.confidence_threshold}",
            original_confidence=result.confidence,
        ))

    # Signal 2: Conflicting evidence
    has_keep_evidence = any(
        "ref" in e.lower() or "import" in e.lower() for e in result.evidence
    )
    has_delete_evidence = any(
        "zero" in e.lower() or "no ref" in e.lower() or "unused" in e.lower()
        for e in result.evidence
    )
    if has_keep_evidence and has_delete_evidence:
        signals.append(EscalationSignal(
            signal_type="conflicting_evidence",
            description="Evidence contains both KEEP and DELETE indicators",
            original_confidence=result.confidence,
        ))

    # Signal 3: INVESTIGATE status
    if result.action == V2Action.INVESTIGATE:
        signals.append(EscalationSignal(
            signal_type="investigate_status",
            description="INVESTIGATE classification requires deeper analysis",
            original_confidence=result.confidence,
        ))

    return signals


def _estimate_tokens(content: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(content) // 4


def escalate(
    result: ClassificationResult,
    file_content: str | None = None,
    additional_evidence: list[str] | None = None,
    config: EscalationConfig | None = None,
) -> EscalationResult:
    """Attempt escalation for a classification result.

    If signals are detected and file content is provided (within bounds),
    re-classify with additional evidence from full-file read.

    Args:
        result: Original classification result.
        file_content: Full file content for deep analysis (optional).
        additional_evidence: Extra evidence from full-file read.
        config: Escalation configuration.

    Returns:
        EscalationResult with updated classification if escalated.
    """
    cfg = config or EscalationConfig()
    signals = detect_signals(result, cfg)

    if not signals:
        return EscalationResult(
            file_path=result.file_path,
            triggered=False,
            original_classification=result,
        )

    # Check token budget
    tokens_needed = 0
    bounded = False
    if file_content:
        lines = file_content.splitlines()
        if len(lines) > cfg.max_file_lines:
            # Truncate to bounds
            file_content = "\n".join(lines[:cfg.max_file_lines])
            bounded = True
        tokens_needed = _estimate_tokens(file_content)
        if tokens_needed > cfg.token_budget:
            bounded = True
            # Truncate content to fit budget
            char_budget = cfg.token_budget * 4
            file_content = file_content[:char_budget]
            tokens_needed = cfg.token_budget

    # Gather additional evidence from full-file read
    new_evidence = list(result.evidence)
    if additional_evidence:
        new_evidence.extend(additional_evidence)

    # Re-classify with enhanced evidence
    has_refs = any(
        "ref" in e.lower() or "import" in e.lower()
        for e in new_evidence
    )
    is_test_or_config = any(
        "test" in e.lower() or "config" in e.lower()
        for e in new_evidence
    )

    escalated = classify_finding(
        result.file_path,
        has_references=has_refs,
        is_test_or_config=is_test_or_config,
        evidence=new_evidence,
        qualifiers=result.qualifiers + ["escalated"],
    )

    # If escalated confidence isn't higher and action unchanged,
    # keep INVESTIGATE to signal human review needed
    if (
        escalated.confidence <= result.confidence
        and escalated.action == result.action
    ):
        escalated = ClassificationResult(
            file_path=result.file_path,
            tier=V2Tier.TIER_1,
            action=V2Action.INVESTIGATE,
            v1_category=result.v1_category,
            confidence=max(result.confidence, 0.50),
            evidence=new_evidence,
            qualifiers=result.qualifiers + ["escalated", "unresolved"],
        )

    return EscalationResult(
        file_path=result.file_path,
        triggered=True,
        signals=signals,
        original_classification=result,
        escalated_classification=escalated,
        tokens_used=tokens_needed,
        bounded=bounded,
    )
