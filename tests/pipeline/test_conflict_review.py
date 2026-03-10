"""Tests for pipeline/conflict_review.py -- file-level overlap detection.

Covers T07.04 acceptance criteria.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.pipeline.conflict_review import (
    ConflictAction,
    ConflictReviewResult,
    detect_file_overlap,
    review_conflicts,
)


class TestDetectFileOverlap:
    """File-level overlap detection between remediation and intervening work."""

    def test_overlap_detected(self):
        """Overlapping files detected when both sets modify same file(s)."""
        remediation = {Path("src/foo.py"), Path("src/bar.py")}
        intervening = {Path("src/bar.py"), Path("src/baz.py")}
        overlap = detect_file_overlap(remediation, intervening)
        assert overlap == {Path("src/bar.py")}

    def test_no_overlap(self):
        """No overlap when file sets are disjoint."""
        remediation = {Path("src/foo.py")}
        intervening = {Path("src/bar.py")}
        overlap = detect_file_overlap(remediation, intervening)
        assert overlap == set()

    def test_empty_remediation(self):
        """Empty remediation set → no overlap."""
        overlap = detect_file_overlap(set(), {Path("src/bar.py")})
        assert overlap == set()

    def test_empty_intervening(self):
        """Empty intervening set → no overlap."""
        overlap = detect_file_overlap({Path("src/foo.py")}, set())
        assert overlap == set()

    def test_both_empty(self):
        """Both empty → no overlap."""
        overlap = detect_file_overlap(set(), set())
        assert overlap == set()

    def test_multiple_overlaps(self):
        """Multiple overlapping files returned."""
        shared = {Path("a.py"), Path("b.py"), Path("c.py")}
        remediation = shared | {Path("d.py")}
        intervening = shared | {Path("e.py")}
        overlap = detect_file_overlap(remediation, intervening)
        assert overlap == shared


class TestReviewConflicts:
    """Conflict review triggers re-gate on overlap, passthrough otherwise."""

    def test_regate_on_overlap(self):
        """Re-gate triggered when overlap found."""
        remediation = {Path("src/foo.py"), Path("src/bar.py")}
        intervening = {Path("src/bar.py")}
        result = review_conflicts(remediation, intervening)
        assert result.action == ConflictAction.REGATE
        assert result.has_conflict is True
        assert Path("src/bar.py") in result.overlapping_files

    def test_passthrough_no_overlap(self):
        """Passthrough when no overlap."""
        remediation = {Path("src/foo.py")}
        intervening = {Path("src/bar.py")}
        result = review_conflicts(remediation, intervening)
        assert result.action == ConflictAction.PASSTHROUGH
        assert result.has_conflict is False
        assert result.overlapping_files == set()

    def test_passthrough_empty_remediation(self):
        """No false positives with empty remediation."""
        result = review_conflicts(set(), {Path("src/bar.py")})
        assert result.action == ConflictAction.PASSTHROUGH
        assert result.has_conflict is False

    def test_passthrough_empty_intervening(self):
        """No false positives with empty intervening work."""
        result = review_conflicts({Path("src/foo.py")}, set())
        assert result.action == ConflictAction.PASSTHROUGH
        assert result.has_conflict is False

    def test_passthrough_both_empty(self):
        """No false positives when both empty."""
        result = review_conflicts(set(), set())
        assert result.action == ConflictAction.PASSTHROUGH
        assert result.has_conflict is False

    def test_result_includes_all_file_sets(self):
        """Result includes remediation and intervening file sets."""
        remediation = {Path("a.py")}
        intervening = {Path("a.py"), Path("b.py")}
        result = review_conflicts(remediation, intervening)
        assert result.remediation_files == remediation
        assert result.intervening_files == intervening
