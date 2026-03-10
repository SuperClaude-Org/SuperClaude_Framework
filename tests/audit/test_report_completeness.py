"""Tests for final report section completeness checks (T04.13 / D-0039)."""

import pytest

from superclaude.cli.audit.report_completeness import (
    MANDATED_SECTIONS,
    check_directory_assessments,
    check_section_completeness,
    validate_report_completeness,
)


def _make_complete_report() -> dict:
    """Create a report with all mandated sections."""
    return {
        "executive_summary": "Summary of findings...",
        "findings_by_tier": {"tier-1": [], "tier-2": []},
        "action_items": ["item1", "item2"],
        "coverage_metrics": {"total": 100, "classified": 95},
        "validation_results": {"consistency_rate": 0.92},
        "dependency_graph_summary": {"nodes": 50, "edges": 120},
        "directory_assessments": [
            {"directory": "big_dir", "file_count": 100},
        ],
    }


class TestSectionCompleteness:
    """Verify section presence checking."""

    def test_all_present(self):
        """Complete report has all sections."""
        report = _make_complete_report()
        present, missing = check_section_completeness(report)
        assert len(missing) == 0
        assert set(present) == set(MANDATED_SECTIONS)

    def test_missing_section_detected(self):
        """Missing section is correctly identified."""
        report = _make_complete_report()
        del report["executive_summary"]
        present, missing = check_section_completeness(report)
        assert "executive_summary" in missing

    def test_multiple_missing(self):
        """Multiple missing sections detected."""
        report = {"action_items": []}
        present, missing = check_section_completeness(report)
        assert len(missing) == len(MANDATED_SECTIONS) - 1


class TestDirectoryAssessments:
    """Verify directory assessment checking."""

    def test_all_assessed(self):
        """All large directories have assessment blocks."""
        report = {
            "directory_assessments": [
                {"directory": "big_dir", "file_count": 100},
            ],
        }
        ok, missing = check_directory_assessments(report, ["big_dir"])
        assert ok
        assert len(missing) == 0

    def test_missing_assessment(self):
        """Missing directory assessment is detected."""
        report = {"directory_assessments": []}
        ok, missing = check_directory_assessments(report, ["big_dir"])
        assert not ok
        assert "big_dir" in missing

    def test_no_large_dirs(self):
        """No large directories means check passes."""
        report = {}
        ok, missing = check_directory_assessments(report, [])
        assert ok


class TestValidateCompleteness:
    """Verify full completeness validation."""

    def test_complete_report_passes(self):
        """Complete report passes validation."""
        report = _make_complete_report()
        result = validate_report_completeness(report, ["big_dir"])
        assert result.complete

    def test_incomplete_report_fails(self):
        """Incomplete report fails validation."""
        report = _make_complete_report()
        del report["executive_summary"]
        result = validate_report_completeness(report)
        assert not result.complete
        assert "executive_summary" in result.missing_sections

    def test_missing_dir_assessment_fails(self):
        """Missing directory assessment fails validation."""
        report = _make_complete_report()
        result = validate_report_completeness(report, ["missing_dir"])
        assert not result.complete

    def test_serialization(self):
        """CompletenessResult serializes to dict."""
        report = _make_complete_report()
        result = validate_report_completeness(report)
        d = result.to_dict()
        assert "complete" in d
        assert "missing_sections" in d

    def test_empty_report_fails(self):
        """Empty report fails completely."""
        result = validate_report_completeness({})
        assert not result.complete
        assert len(result.missing_sections) == len(MANDATED_SECTIONS)
