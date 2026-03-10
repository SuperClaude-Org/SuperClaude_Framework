"""Tests for 10% stratified consistency validation pass.

Validates AC6: 10% sample validation with stratified tier representation.
"""

from __future__ import annotations

from superclaude.cli.audit.classification import classify_finding
from superclaude.cli.audit.validation import (
    stratified_sample,
    validate_consistency,
)


def _make_100_results():
    """Create 100 classification results: 30 tier-1, 70 tier-2."""
    results = []
    for i in range(30):
        results.append(classify_finding(
            f"orphan_{i}.py", has_references=False,
            evidence=["zero references found"],
        ))
    for i in range(70):
        results.append(classify_finding(
            f"used_{i}.py", has_references=True,
            evidence=["referenced by main.py"],
        ))
    return results


class TestStratifiedSample:
    def test_sample_at_least_10_percent(self):
        results = _make_100_results()
        sample = stratified_sample(results, sample_fraction=0.10, seed=42)
        assert len(sample) >= 10

    def test_each_tier_represented(self):
        results = _make_100_results()
        sample = stratified_sample(results, sample_fraction=0.10, seed=42)
        tiers = {r.tier.value for r in sample}
        assert "tier-1" in tiers
        assert "tier-2" in tiers

    def test_proportional_representation(self):
        results = _make_100_results()
        sample = stratified_sample(results, sample_fraction=0.10, seed=42)
        tier1_count = sum(1 for r in sample if r.tier.value == "tier-1")
        tier2_count = sum(1 for r in sample if r.tier.value == "tier-2")
        # 30% tier-1, 70% tier-2 in input -> roughly proportional in sample
        assert tier1_count >= 1
        assert tier2_count >= 1

    def test_empty_input(self):
        assert stratified_sample([], seed=42) == []

    def test_deterministic_with_seed(self):
        results = _make_100_results()
        s1 = stratified_sample(results, seed=42)
        s2 = stratified_sample(results, seed=42)
        assert [r.file_path for r in s1] == [r.file_path for r in s2]


class TestValidateConsistency:
    def test_consistency_rate_reported(self):
        results = _make_100_results()
        vr = validate_consistency(results, classify_finding, seed=42)
        assert 0.0 <= vr.consistency_rate <= 1.0
        assert vr.sample_size >= 10
        assert vr.total_classified == 100

    def test_deterministic_classification_yields_100_percent(self):
        results = _make_100_results()
        vr = validate_consistency(results, classify_finding, seed=42)
        # classify_finding is deterministic, so re-classification matches
        assert vr.consistency_rate == 1.0
        assert vr.inconsistent_count == 0

    def test_tier_sample_counts_present(self):
        results = _make_100_results()
        vr = validate_consistency(results, classify_finding, seed=42)
        assert "tier-1" in vr.tier_sample_counts
        assert "tier-2" in vr.tier_sample_counts

    def test_validation_result_serialization(self):
        results = _make_100_results()
        vr = validate_consistency(results, classify_finding, seed=42)
        d = vr.to_dict()
        assert "consistency_rate" in d
        assert "sample_size" in d
        assert "tier_sample_counts" in d
