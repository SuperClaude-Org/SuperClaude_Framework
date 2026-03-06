"""Tests for two-tier classification with backward mapping to v1 categories.

Validates AC1 (core action sections) and AC15 (v2-to-v1 mapping compatibility).
"""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
    all_v1_categories_covered,
    classify_finding,
    map_to_v1,
)


class TestMapToV1:
    """Verify deterministic v2 -> v1 mapping."""

    def test_delete_maps_to_delete(self):
        assert map_to_v1(V2Tier.TIER_1, V2Action.DELETE) == V1Category.DELETE

    def test_investigate_maps_to_investigate(self):
        assert map_to_v1(V2Tier.TIER_1, V2Action.INVESTIGATE) == V1Category.INVESTIGATE

    def test_keep_maps_to_keep(self):
        assert map_to_v1(V2Tier.TIER_2, V2Action.KEEP) == V1Category.KEEP

    def test_reorganize_maps_to_reorganize(self):
        assert map_to_v1(V2Tier.TIER_2, V2Action.REORGANIZE) == V1Category.REORGANIZE

    def test_archive_maps_to_delete(self):
        assert map_to_v1(V2Tier.TIER_2, V2Action.ARCHIVE) == V1Category.DELETE

    def test_unmapped_raises(self):
        with pytest.raises(ValueError, match="No v1 mapping"):
            map_to_v1(V2Tier.TIER_1, V2Action.KEEP)

    def test_all_v1_categories_covered(self):
        """No v1 category is orphaned."""
        assert all_v1_categories_covered()


class TestClassifyFinding:
    """Verify classification determinism and correctness."""

    def test_no_references_produces_delete(self):
        result = classify_finding("orphan.py", has_references=False)
        assert result.tier == V2Tier.TIER_1
        assert result.action == V2Action.DELETE
        assert result.v1_category == V1Category.DELETE

    def test_has_references_produces_keep(self):
        result = classify_finding("used.py", has_references=True)
        assert result.tier == V2Tier.TIER_2
        assert result.action == V2Action.KEEP
        assert result.v1_category == V1Category.KEEP

    def test_temporal_artifact_produces_archive(self):
        result = classify_finding(
            "old-release.md", has_references=False, is_temporal_artifact=True
        )
        assert result.tier == V2Tier.TIER_2
        assert result.action == V2Action.ARCHIVE
        assert result.v1_category == V1Category.DELETE

    def test_test_config_produces_keep(self):
        result = classify_finding(
            "conftest.py", has_references=True, is_test_or_config=True
        )
        assert result.tier == V2Tier.TIER_2
        assert result.action == V2Action.KEEP
        assert result.v1_category == V1Category.KEEP

    def test_determinism_three_runs(self):
        """Same input produces same output across 3 runs (AC determinism)."""
        results = [
            classify_finding("x.py", has_references=False) for _ in range(3)
        ]
        assert all(r.tier == results[0].tier for r in results)
        assert all(r.action == results[0].action for r in results)
        assert all(r.v1_category == results[0].v1_category for r in results)
        assert all(r.confidence == results[0].confidence for r in results)

    def test_evidence_preserved(self):
        result = classify_finding(
            "a.py",
            has_references=False,
            evidence=["zero refs found by grep"],
            qualifiers=["unused"],
        )
        assert "zero refs found by grep" in result.evidence
        assert "unused" in result.qualifiers


class TestClassificationResultSerialization:
    """Verify round-trip serialization."""

    def test_to_dict_and_back(self):
        original = classify_finding("file.py", has_references=False)
        d = original.to_dict()
        restored = ClassificationResult.from_dict(d)
        assert restored.file_path == original.file_path
        assert restored.tier == original.tier
        assert restored.action == original.action
        assert restored.v1_category == original.v1_category
        assert restored.confidence == original.confidence
