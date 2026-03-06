"""Tests for evidence-gated DELETE and KEEP classification rules.

Validates AC4 (DELETE evidence) and AC5 (KEEP evidence).
"""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
)
from superclaude.cli.audit.evidence_gate import (
    check_delete_evidence,
    check_keep_evidence,
    evidence_gate,
)


class TestDeleteEvidenceGate:
    def test_delete_with_evidence_passes(self):
        result = ClassificationResult(
            file_path="orphan.py",
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.9,
            evidence=["zero references found by grep"],
        )
        gate = check_delete_evidence(result)
        assert gate.passed

    def test_delete_without_evidence_fails(self):
        result = ClassificationResult(
            file_path="orphan.py",
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.9,
            evidence=[],
        )
        gate = check_delete_evidence(result)
        assert not gate.passed
        assert "lacks zero-reference evidence" in gate.reason

    def test_non_delete_always_passes(self):
        result = ClassificationResult(
            file_path="used.py",
            tier=V2Tier.TIER_2,
            action=V2Action.KEEP,
            v1_category=V1Category.KEEP,
            confidence=0.9,
            evidence=[],
        )
        gate = check_delete_evidence(result)
        assert gate.passed

    def test_referenced_file_rejected_as_delete(self):
        """File with 3 known references must not pass DELETE gate."""
        result = ClassificationResult(
            file_path="important.py",
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.5,
            evidence=["has 3 references"],  # Not zero-ref evidence
        )
        gate = check_delete_evidence(result)
        assert not gate.passed


class TestKeepEvidenceGate:
    def test_keep_with_evidence_passes(self):
        result = ClassificationResult(
            file_path="used.py",
            tier=V2Tier.TIER_2,
            action=V2Action.KEEP,
            v1_category=V1Category.KEEP,
            confidence=0.9,
            evidence=["referenced by main.py"],
        )
        gate = check_keep_evidence(result)
        assert gate.passed

    def test_keep_without_evidence_fails(self):
        result = ClassificationResult(
            file_path="used.py",
            tier=V2Tier.TIER_2,
            action=V2Action.KEEP,
            v1_category=V1Category.KEEP,
            confidence=0.9,
            evidence=[],
        )
        gate = check_keep_evidence(result)
        assert not gate.passed
        assert "lacks reference evidence" in gate.reason


class TestCombinedEvidenceGate:
    def test_valid_delete_passes(self):
        result = ClassificationResult(
            file_path="orphan.py",
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.9,
            evidence=["zero references found"],
        )
        gate = evidence_gate(result)
        assert gate.passed

    def test_invalid_delete_rejected(self):
        result = ClassificationResult(
            file_path="orphan.py",
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.9,
            evidence=[],
        )
        gate = evidence_gate(result)
        assert not gate.passed

    def test_valid_keep_passes(self):
        result = ClassificationResult(
            file_path="used.py",
            tier=V2Tier.TIER_2,
            action=V2Action.KEEP,
            v1_category=V1Category.KEEP,
            confidence=0.9,
            evidence=["referenced by 2 files"],
        )
        gate = evidence_gate(result)
        assert gate.passed

    def test_gate_result_serialization(self):
        result = ClassificationResult(
            file_path="x.py",
            tier=V2Tier.TIER_1,
            action=V2Action.DELETE,
            v1_category=V1Category.DELETE,
            confidence=0.9,
            evidence=[],
        )
        gate = evidence_gate(result)
        d = gate.to_dict()
        assert "passed" in d
        assert "reason" in d
