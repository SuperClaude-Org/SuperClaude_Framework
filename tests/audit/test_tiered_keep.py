"""Tests for tiered KEEP evidence enforcement (T03.04 / D-0020)."""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
)
from superclaude.cli.audit.tiered_keep import (
    TIER_REQUIREMENTS,
    check_tiered_keep,
)


def _make_keep(evidence: list[str]) -> ClassificationResult:
    return ClassificationResult(
        file_path="src/main.py",
        tier=V2Tier.TIER_2,
        action=V2Action.KEEP,
        v1_category=V1Category.KEEP,
        confidence=0.85,
        evidence=evidence,
    )


def _make_delete() -> ClassificationResult:
    return ClassificationResult(
        file_path="src/old.py",
        tier=V2Tier.TIER_1,
        action=V2Action.DELETE,
        v1_category=V1Category.DELETE,
        confidence=0.90,
        evidence=["zero references found"],
    )


class TestTierRequirements:
    def test_low_requires_1(self):
        assert TIER_REQUIREMENTS["low"] == 1

    def test_medium_requires_2(self):
        assert TIER_REQUIREMENTS["medium"] == 2

    def test_high_requires_3(self):
        assert TIER_REQUIREMENTS["high"] == 3


class TestCheckTieredKeep:
    def test_low_risk_1_ref_passes(self):
        result = _make_keep(["reference found in app.py"])
        gate = check_tiered_keep(result, "low")
        assert gate.passed

    def test_low_risk_0_ref_fails(self):
        result = _make_keep([])
        gate = check_tiered_keep(result, "low")
        assert not gate.passed

    def test_medium_risk_2_refs_passes(self):
        result = _make_keep([
            "reference found in app.py",
            "imported by main.py",
        ])
        gate = check_tiered_keep(result, "medium")
        assert gate.passed

    def test_medium_risk_1_ref_fails(self):
        result = _make_keep(["reference found in app.py"])
        gate = check_tiered_keep(result, "medium")
        assert not gate.passed

    def test_high_risk_3_refs_passes(self):
        result = _make_keep([
            "reference found in app.py",
            "imported by main.py",
            "used by test_main.py",
        ])
        gate = check_tiered_keep(result, "high")
        assert gate.passed

    def test_high_risk_2_refs_fails(self):
        result = _make_keep([
            "reference found in app.py",
            "imported by main.py",
        ])
        gate = check_tiered_keep(result, "high")
        assert not gate.passed

    def test_non_keep_passes(self):
        result = _make_delete()
        gate = check_tiered_keep(result, "high")
        assert gate.passed
        assert gate.reason == "Non-KEEP action, gate not applicable"

    def test_escalation_with_additional_evidence(self):
        result = _make_keep(["reference found in app.py"])
        gate = check_tiered_keep(
            result, "high",
            additional_evidence=[
                "imported by utils.py",
                "used by cli.py",
            ],
        )
        assert gate.passed
        assert gate.escalation_attempted

    def test_escalation_still_fails(self):
        result = _make_keep(["reference found in app.py"])
        gate = check_tiered_keep(
            result, "high",
            additional_evidence=["no matching evidence here"],
        )
        assert not gate.passed
        assert gate.escalation_attempted

    def test_gate_result_serializable(self):
        result = _make_keep(["reference found in app.py"])
        gate = check_tiered_keep(result, "low")
        d = gate.to_dict()
        assert "risk_tier" in d
        assert "required_references" in d
        assert "found_references" in d
