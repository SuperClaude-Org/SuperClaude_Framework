"""Tests for anti-lazy distribution guards (T04.12 / D-0038)."""

import pytest

from superclaude.cli.audit.classification import V2Action, V2Tier
from superclaude.cli.audit.consolidation import ConsolidatedFinding
from superclaude.cli.audit.anti_lazy import (
    check_batch_uniformity,
    run_anti_lazy_guard,
)


def _make_finding(
    path: str,
    action: V2Action = V2Action.KEEP,
) -> ConsolidatedFinding:
    tier = V2Tier.TIER_2 if action == V2Action.KEEP else V2Tier.TIER_1
    return ConsolidatedFinding(
        file_path=path, tier=tier, action=action,
        confidence=0.85, evidence=["ev"], source_phases=["surface"],
    )


class TestBatchUniformity:
    """Verify uniformity detection."""

    def test_all_keep_flagged(self):
        """All-KEEP batch exceeds 90% threshold."""
        findings = [_make_finding(f"f_{i}.py") for i in range(50)]
        flag = check_batch_uniformity("B-001", findings, threshold=0.90)
        assert flag is not None
        assert flag.dominant_action == "KEEP"
        assert flag.uniformity_ratio == 1.0

    def test_48_of_50_flagged(self):
        """48 KEEP + 2 DELETE in 50 files: 96% > 90% → flagged."""
        findings = (
            [_make_finding(f"k_{i}.py") for i in range(48)]
            + [_make_finding(f"d_{i}.py", V2Action.DELETE) for i in range(2)]
        )
        flag = check_batch_uniformity("B-001", findings, threshold=0.90)
        assert flag is not None
        assert flag.uniformity_ratio == pytest.approx(0.96)

    def test_diverse_not_flagged(self):
        """Diverse batch (50% KEEP, 50% DELETE) is not flagged."""
        findings = (
            [_make_finding(f"k_{i}.py") for i in range(25)]
            + [_make_finding(f"d_{i}.py", V2Action.DELETE) for i in range(25)]
        )
        flag = check_batch_uniformity("B-001", findings, threshold=0.90)
        assert flag is None

    def test_empty_batch(self):
        """Empty batch returns None."""
        flag = check_batch_uniformity("B-001", [], threshold=0.90)
        assert flag is None


class TestAntiLazyGuard:
    """Verify anti-lazy guard across batches."""

    def test_uniform_batch_triggers_reanalysis(self):
        """Flagged batches trigger reanalysis."""
        batches = {
            "B-001": [_make_finding(f"f_{i}.py") for i in range(50)],
        }
        report = run_anti_lazy_guard(batches, threshold=0.90)
        assert report.reanalysis_triggered
        assert report.flagged_count == 1

    def test_diverse_batches_pass(self):
        """Diverse batches do not trigger reanalysis."""
        batches = {
            "B-001": (
                [_make_finding(f"k_{i}.py") for i in range(25)]
                + [_make_finding(f"d_{i}.py", V2Action.DELETE) for i in range(25)]
            ),
        }
        report = run_anti_lazy_guard(batches, threshold=0.90)
        assert not report.reanalysis_triggered

    def test_mixed_batches(self):
        """Mix of uniform and diverse batches correctly identified."""
        batches = {
            "B-001": [_make_finding(f"f_{i}.py") for i in range(50)],  # uniform
            "B-002": (
                [_make_finding(f"k_{i}.py") for i in range(25)]
                + [_make_finding(f"d_{i}.py", V2Action.DELETE) for i in range(25)]
            ),  # diverse
        }
        report = run_anti_lazy_guard(batches, threshold=0.90)
        assert report.flagged_count == 1
        assert report.batches_passed == 1

    def test_report_serialization(self):
        """AntiLazyReport serializes to dict."""
        batches = {"B-001": [_make_finding(f"f_{i}.py") for i in range(50)]}
        report = run_anti_lazy_guard(batches)
        d = report.to_dict()
        assert "flagged_count" in d
        assert "reanalysis_triggered" in d
