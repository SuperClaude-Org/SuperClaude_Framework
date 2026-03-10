"""Tests for signal-triggered escalation (T03.03 / D-0019)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
)
from superclaude.cli.audit.escalation import (
    DEFAULT_TOKEN_BUDGET,
    EscalationConfig,
    detect_signals,
    escalate,
)


def _make_result(
    confidence: float = 0.85,
    action: V2Action = V2Action.KEEP,
    evidence: list[str] | None = None,
) -> ClassificationResult:
    tier = V2Tier.TIER_2 if action == V2Action.KEEP else V2Tier.TIER_1
    v1 = V1Category.KEEP if action == V2Action.KEEP else V1Category.INVESTIGATE
    return ClassificationResult(
        file_path="src/test.py",
        tier=tier,
        action=action,
        v1_category=v1,
        confidence=confidence,
        evidence=evidence or [],
    )


class TestDetectSignals:
    def test_low_confidence_triggers(self):
        result = _make_result(confidence=0.50)
        signals = detect_signals(result)
        types = [s.signal_type for s in signals]
        assert "low_confidence" in types

    def test_normal_confidence_no_signal(self):
        result = _make_result(confidence=0.85)
        signals = detect_signals(result)
        types = [s.signal_type for s in signals]
        assert "low_confidence" not in types

    def test_conflicting_evidence_triggers(self):
        result = _make_result(evidence=[
            "import reference found in app.py",
            "zero references from external modules",
        ])
        signals = detect_signals(result)
        types = [s.signal_type for s in signals]
        assert "conflicting_evidence" in types

    def test_investigate_triggers(self):
        result = _make_result(action=V2Action.INVESTIGATE, confidence=0.60)
        signals = detect_signals(result)
        types = [s.signal_type for s in signals]
        assert "investigate_status" in types

    def test_no_signals_for_clean_result(self):
        result = _make_result(confidence=0.90, evidence=["reference found"])
        signals = detect_signals(result)
        assert len(signals) == 0

    def test_custom_threshold(self):
        config = EscalationConfig(confidence_threshold=0.9)
        result = _make_result(confidence=0.85)
        signals = detect_signals(result, config)
        types = [s.signal_type for s in signals]
        assert "low_confidence" in types


class TestEscalate:
    def test_no_escalation_when_clean(self):
        result = _make_result(confidence=0.90, evidence=["reference found"])
        esc = escalate(result)
        assert not esc.triggered

    def test_escalation_triggered_on_low_confidence(self):
        result = _make_result(confidence=0.50)
        esc = escalate(result, additional_evidence=["reference found in main.py"])
        assert esc.triggered
        assert esc.escalated_classification is not None

    def test_escalation_produces_higher_confidence_or_investigate(self):
        result = _make_result(confidence=0.50, action=V2Action.INVESTIGATE)
        esc = escalate(result, additional_evidence=["reference found"])
        assert esc.triggered
        ec = esc.escalated_classification
        assert ec is not None
        # Should either have higher confidence or explicit INVESTIGATE
        assert (
            ec.confidence > result.confidence
            or ec.action == V2Action.INVESTIGATE
        )

    def test_token_budget_respected(self):
        result = _make_result(confidence=0.50)
        big_content = "x = 1\n" * 10000  # large file
        config = EscalationConfig(token_budget=100)
        esc = escalate(result, file_content=big_content, config=config)
        assert esc.triggered
        assert esc.tokens_used <= 100
        assert esc.bounded

    def test_max_lines_respected(self):
        result = _make_result(confidence=0.50)
        big_content = "x = 1\n" * 1000
        config = EscalationConfig(max_file_lines=50)
        esc = escalate(result, file_content=big_content, config=config)
        assert esc.bounded

    def test_escalation_result_serializable(self):
        result = _make_result(confidence=0.50)
        esc = escalate(result, additional_evidence=["reference found"])
        d = esc.to_dict()
        assert "triggered" in d
        assert "signals" in d
        assert "tokens_used" in d
