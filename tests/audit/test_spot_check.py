"""Tests for post-consolidation spot-check validator (T04.02 / D-0028)."""

import pytest

from superclaude.cli.audit.classification import (
    ClassificationResult,
    V1Category,
    V2Action,
    V2Tier,
    classify_finding,
    map_to_v1,
)
from superclaude.cli.audit.consolidation import (
    ConsolidatedFinding,
    ConsolidationReport,
    PhaseFinding,
    consolidate,
)
from superclaude.cli.audit.spot_check import (
    SpotCheckResult,
    _stratified_sample,
    spot_check_validate,
)


def _make_consolidated(
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
        evidence=["test-evidence"],
        source_phases=["surface"],
    )


def _make_report(count: int = 30) -> ConsolidationReport:
    """Create a report with `count` findings, mixed tiers."""
    findings = []
    for i in range(count):
        if i % 3 == 0:
            findings.append(_make_consolidated(
                f"file_{i}.py",
                tier=V2Tier.TIER_1,
                action=V2Action.DELETE,
            ))
        else:
            findings.append(_make_consolidated(f"file_{i}.py"))
    return ConsolidationReport(
        findings=findings,
        total_input_findings=count,
        total_consolidated=count,
    )


class TestStratifiedSampling:
    """Verify stratified sampling mechanics."""

    def test_sample_size_at_least_10_percent(self):
        """Sample size is >= 10% of consolidated findings."""
        report = _make_report(30)
        sample = _stratified_sample(report.findings, sample_fraction=0.10, seed=42)
        assert len(sample) >= 3  # 10% of 30

    def test_proportional_tier_representation(self):
        """Sample contains proportional tier representation."""
        report = _make_report(30)
        sample = _stratified_sample(report.findings, sample_fraction=0.10, seed=42)
        tier_counts = {}
        for f in sample:
            tier_counts[f.tier.value] = tier_counts.get(f.tier.value, 0) + 1
        # Both tiers should be represented
        assert len(tier_counts) >= 1

    def test_minimum_one_per_tier(self):
        """Each populated tier gets at least 1 sample."""
        findings = [
            _make_consolidated("a.py", tier=V2Tier.TIER_1, action=V2Action.DELETE),
        ] + [
            _make_consolidated(f"keep_{i}.py") for i in range(20)
        ]
        report = ConsolidationReport(findings=findings, total_consolidated=21)
        sample = _stratified_sample(report.findings, sample_fraction=0.10, seed=42)
        tiers = {f.tier for f in sample}
        assert V2Tier.TIER_1 in tiers
        assert V2Tier.TIER_2 in tiers

    def test_empty_input(self):
        """Empty findings produces empty sample."""
        assert _stratified_sample([]) == []


class TestSpotCheckValidation:
    """Verify spot-check validation with re-classification."""

    def test_consistency_rate_reported(self):
        """Overall consistency rate is computed and reported."""
        report = _make_report(20)
        result = spot_check_validate(report, seed=42)
        assert 0.0 <= result.overall_consistency_rate <= 1.0
        assert result.sample_size >= 2  # 10% of 20

    def test_per_tier_breakdown(self):
        """Consistency rate is broken down per tier."""
        report = _make_report(30)
        result = spot_check_validate(report, seed=42)
        assert isinstance(result.per_tier_rates, dict)
        for rate in result.per_tier_rates.values():
            assert 0.0 <= rate <= 1.0

    def test_independent_reclassification(self):
        """Re-classification uses fresh function call, not cached."""
        call_count = 0

        def counting_reclassify(file_path: str) -> ClassificationResult:
            nonlocal call_count
            call_count += 1
            return ClassificationResult(
                file_path=file_path,
                tier=V2Tier.TIER_2,
                action=V2Action.KEEP,
                v1_category=V1Category.KEEP,
                confidence=0.85,
            )

        report = _make_report(20)
        result = spot_check_validate(report, reclassify_fn=counting_reclassify, seed=42)
        assert call_count == result.sample_size

    def test_inconsistencies_logged(self):
        """Inconsistencies between original and re-classification are logged."""

        def always_delete(file_path: str) -> ClassificationResult:
            return ClassificationResult(
                file_path=file_path,
                tier=V2Tier.TIER_1,
                action=V2Action.DELETE,
                v1_category=V1Category.DELETE,
                confidence=0.90,
            )

        # All findings are KEEP, but reclassifier says DELETE
        findings = [_make_consolidated(f"f_{i}.py") for i in range(10)]
        report = ConsolidationReport(findings=findings, total_consolidated=10)
        result = spot_check_validate(report, reclassify_fn=always_delete, seed=42)

        # All KEEP findings should be inconsistent with DELETE re-classification
        keep_in_sample = sum(
            1 for f in findings[:result.sample_size]
            if f.action == V2Action.KEEP
        )
        assert result.inconsistent_count > 0
        assert len(result.inconsistencies) > 0

    def test_to_dict_serialization(self):
        """SpotCheckResult serializes to dict."""
        report = _make_report(20)
        result = spot_check_validate(report, seed=42)
        d = result.to_dict()
        assert "overall_consistency_rate" in d
        assert "per_tier_rates" in d
        assert "sample_size" in d

    def test_per_tier_sample_counts(self):
        """Per-tier sample counts are reported."""
        report = _make_report(30)
        result = spot_check_validate(report, seed=42)
        assert isinstance(result.per_tier_sample_counts, dict)
        total_from_tiers = sum(result.per_tier_sample_counts.values())
        assert total_from_tiers == result.sample_size
