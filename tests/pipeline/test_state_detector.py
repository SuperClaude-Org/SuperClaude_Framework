"""Tests for state variable detector.

Covers T02.02 acceptance criteria:
- "Replace boolean with int offset" -> replacement type detected
- "Add replay guard flag" -> flag type detected
- "Document offset behavior" -> NOT detected (doc suppression)
- "Introduce cursor for pagination" -> cursor type detected
- Multiple variables in one deliverable handled
"""

from __future__ import annotations

import pytest

from superclaude.cli.pipeline.models import Deliverable, DeliverableKind
from superclaude.cli.pipeline.state_detector import (
    DetectionResult,
    IntroductionType,
    detect_state_variables,
)


def _make_deliverable(id: str, desc: str) -> Deliverable:
    return Deliverable(id=id, description=desc, kind=DeliverableKind.IMPLEMENT)


class TestStateVariableDetector:
    """Five-scenario test suite per tasklist spec."""

    def test_replacement_detected(self):
        """'Replace boolean with int offset' -> replacement type."""
        deliverables = [_make_deliverable("D-001", "Replace boolean with int offset")]
        results = detect_state_variables(deliverables)
        assert len(results) >= 1
        replacement = [r for r in results if r.introduction_type == IntroductionType.REPLACEMENT]
        assert len(replacement) >= 1
        assert replacement[0].variable_name == "boolean"

    def test_flag_detected(self):
        """'Add replay guard flag' -> flag type."""
        deliverables = [_make_deliverable("D-002", "Add replay guard flag")]
        results = detect_state_variables(deliverables)
        flag_results = [r for r in results if r.introduction_type == IntroductionType.FLAG]
        assert len(flag_results) >= 1

    def test_document_not_detected(self):
        """'Document offset behavior' -> not detected (doc suppression)."""
        deliverables = [_make_deliverable("D-003", "Document offset behavior")]
        results = detect_state_variables(deliverables)
        assert len(results) == 0

    def test_cursor_detected(self):
        """'Introduce cursor for pagination' -> cursor type."""
        deliverables = [_make_deliverable("D-004", "Introduce cursor for pagination")]
        results = detect_state_variables(deliverables)
        cursor_results = [r for r in results if r.introduction_type == IntroductionType.CURSOR]
        assert len(cursor_results) >= 1

    def test_multiple_variables_one_deliverable(self):
        """Multiple variables in one deliverable all detected."""
        deliverables = [_make_deliverable(
            "D-005",
            "Add counter for retries and introduce cursor for pagination and add flag for completion"
        )]
        results = detect_state_variables(deliverables)
        types = {r.introduction_type for r in results}
        assert IntroductionType.COUNTER in types
        assert IntroductionType.CURSOR in types
        assert IntroductionType.FLAG in types


class TestSelfFieldDetection:
    """self._field pattern detection."""

    def test_self_field(self):
        deliverables = [_make_deliverable("D-010", "Set self._loaded_start_index to initial value")]
        results = detect_state_variables(deliverables)
        assert any(r.variable_name == "_loaded_start_index" for r in results)

    def test_multiple_self_fields(self):
        deliverables = [_make_deliverable(
            "D-011",
            "Initialize self._offset and self._cursor from config"
        )]
        results = detect_state_variables(deliverables)
        names = {r.variable_name for r in results}
        assert "_offset" in names
        assert "_cursor" in names


class TestConfidenceFlagging:
    """Low-confidence detections flagged for human review."""

    def test_high_confidence_no_review(self):
        deliverables = [_make_deliverable("D-020", "Set self._counter to zero")]
        results = detect_state_variables(deliverables)
        assert all(not r.needs_review for r in results)

    def test_empty_description_skipped(self):
        deliverables = [_make_deliverable("D-021", "")]
        results = detect_state_variables(deliverables)
        assert len(results) == 0

    def test_non_state_description_empty(self):
        deliverables = [_make_deliverable("D-022", "Update README with usage instructions")]
        results = detect_state_variables(deliverables)
        assert len(results) == 0
