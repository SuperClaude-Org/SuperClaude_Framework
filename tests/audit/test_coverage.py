"""Tests for coverage tracking with per-risk-tier metrics.

Validates AC2: coverage artifacts with per-tier file counts and percentages.
"""

from __future__ import annotations

import pytest

from superclaude.cli.audit.classification import classify_finding
from superclaude.cli.audit.coverage import CoverageTracker


class TestCoverageTracker:
    def _make_tracker_with_10_files(self):
        """Create a tracker with 10 classified files: 3 tier-1, 7 tier-2."""
        tracker = CoverageTracker(total_files_scanned=10)
        # 3 files with no references -> tier-1 DELETE
        for i in range(3):
            r = classify_finding(f"orphan_{i}.py", has_references=False)
            tracker.add(r)
        # 7 files with references -> tier-2 KEEP
        for i in range(7):
            r = classify_finding(f"used_{i}.py", has_references=True)
            tracker.add(r)
        return tracker

    def test_per_tier_counts(self):
        tracker = self._make_tracker_with_10_files()
        artifact = tracker.emit()
        assert artifact.tier_breakdown["tier-1"]["file_count"] == 3
        assert artifact.tier_breakdown["tier-2"]["file_count"] == 7

    def test_percentages_sum_to_100(self):
        tracker = self._make_tracker_with_10_files()
        artifact = tracker.emit()
        assert abs(artifact.percentages_sum - 100.0) < 0.01

    def test_percentages_correct(self):
        tracker = self._make_tracker_with_10_files()
        artifact = tracker.emit()
        assert artifact.tier_breakdown["tier-1"]["percentage"] == 30.0
        assert artifact.tier_breakdown["tier-2"]["percentage"] == 70.0

    def test_no_double_counting(self):
        tracker = CoverageTracker(total_files_scanned=1)
        r = classify_finding("same.py", has_references=False)
        tracker.add(r)
        tracker.add(r)  # duplicate
        artifact = tracker.emit()
        assert artifact.total_files_classified == 1

    def test_identical_output_on_same_input(self):
        t1 = self._make_tracker_with_10_files()
        t2 = self._make_tracker_with_10_files()
        a1 = t1.emit()
        a2 = t2.emit()
        assert a1.to_dict() == a2.to_dict()

    def test_empty_tracker(self):
        tracker = CoverageTracker(total_files_scanned=0)
        artifact = tracker.emit()
        assert artifact.total_files_classified == 0
        assert artifact.percentages_sum == 0.0

    def test_artifact_schema_fields(self):
        tracker = self._make_tracker_with_10_files()
        artifact = tracker.emit()
        d = artifact.to_dict()
        assert "total_files_scanned" in d
        assert "total_files_classified" in d
        assert "tier_breakdown" in d
        assert "percentages_sum" in d
