"""Tests for directory assessment blocks (T04.05 / D-0031)."""

import pytest

from superclaude.cli.audit.classification import V2Action, V2Tier
from superclaude.cli.audit.consolidation import ConsolidatedFinding
from superclaude.cli.audit.dir_assessment import (
    DirectoryAssessment,
    build_assessment_block,
    generate_assessment_blocks,
    identify_large_directories,
)


def _make_finding(
    file_path: str,
    tier: V2Tier = V2Tier.TIER_2,
    action: V2Action = V2Action.KEEP,
    confidence: float = 0.85,
) -> ConsolidatedFinding:
    return ConsolidatedFinding(
        file_path=file_path,
        tier=tier,
        action=action,
        confidence=confidence,
        evidence=["ev"],
        source_phases=["surface"],
    )


class TestIdentifyLargeDirectories:
    """Verify directory size detection."""

    def test_large_dir_detected(self):
        """Directories exceeding threshold are identified."""
        findings = [_make_finding(f"big_dir/file_{i}.py") for i in range(60)]
        large = identify_large_directories(findings, threshold=50)
        assert "big_dir" in large
        assert len(large["big_dir"]) == 60

    def test_small_dir_excluded(self):
        """Directories below threshold are not included."""
        findings = [_make_finding(f"small_dir/file_{i}.py") for i in range(10)]
        large = identify_large_directories(findings, threshold=50)
        assert len(large) == 0

    def test_mixed_directories(self):
        """Only directories exceeding threshold are returned."""
        findings = (
            [_make_finding(f"big/file_{i}.py") for i in range(55)]
            + [_make_finding(f"small/file_{i}.py") for i in range(10)]
        )
        large = identify_large_directories(findings, threshold=50)
        assert "big" in large
        assert "small" not in large


class TestBuildAssessmentBlock:
    """Verify aggregate assessment block generation."""

    def test_block_has_file_count(self):
        """Assessment block includes correct file count."""
        findings = [_make_finding(f"dir/f_{i}.py") for i in range(60)]
        block = build_assessment_block("dir", findings)
        assert block.file_count == 60

    def test_block_has_tier_distribution(self):
        """Assessment block includes tier distribution."""
        findings = [
            _make_finding(f"dir/f_{i}.py", tier=V2Tier.TIER_1, action=V2Action.DELETE)
            for i in range(20)
        ] + [
            _make_finding(f"dir/k_{i}.py") for i in range(40)
        ]
        block = build_assessment_block("dir", findings)
        assert block.tier_distribution["tier-1"] == 20
        assert block.tier_distribution["tier-2"] == 40

    def test_block_has_dominant_classification(self):
        """Assessment block reports dominant tier and action."""
        findings = [_make_finding(f"dir/f_{i}.py") for i in range(60)]
        block = build_assessment_block("dir", findings)
        assert block.dominant_tier == "tier-2"
        assert block.dominant_action == "KEEP"

    def test_block_has_risk_summary(self):
        """Assessment block includes risk summary string."""
        findings = [_make_finding(f"dir/f_{i}.py") for i in range(60)]
        block = build_assessment_block("dir", findings)
        assert "risk" in block.risk_summary.lower()

    def test_block_serializes(self):
        """Assessment block serializes to dict."""
        findings = [_make_finding(f"dir/f_{i}.py") for i in range(60)]
        block = build_assessment_block("dir", findings)
        d = block.to_dict()
        assert d["file_count"] == 60
        assert "directory" in d


class TestGenerateAssessmentBlocks:
    """Verify assessment block generation with pass-through."""

    def test_large_dir_gets_block(self):
        """Large directory produces an assessment block."""
        findings = [_make_finding(f"big/f_{i}.py") for i in range(60)]
        blocks, remaining = generate_assessment_blocks(findings, threshold=50)
        assert len(blocks) == 1
        assert blocks[0].directory == "big"

    def test_small_dir_passes_through(self):
        """Small directory findings remain as individual entries."""
        findings = [_make_finding(f"small/f_{i}.py") for i in range(10)]
        blocks, remaining = generate_assessment_blocks(findings, threshold=50)
        assert len(blocks) == 0
        assert len(remaining) == 10

    def test_mixed_replacement(self):
        """Large dirs get blocks, small dirs get per-file entries."""
        findings = (
            [_make_finding(f"big/f_{i}.py") for i in range(55)]
            + [_make_finding(f"small/f_{i}.py") for i in range(10)]
        )
        blocks, remaining = generate_assessment_blocks(findings, threshold=50)
        assert len(blocks) == 1
        assert len(remaining) == 10
        assert all(f.file_path.startswith("small/") for f in remaining)

    def test_100_file_fixture(self):
        """100-file directory produces single assessment block."""
        findings = [_make_finding(f"huge/f_{i}.py") for i in range(100)]
        blocks, remaining = generate_assessment_blocks(findings, threshold=50)
        assert len(blocks) == 1
        assert blocks[0].file_count == 100
        assert len(remaining) == 0
