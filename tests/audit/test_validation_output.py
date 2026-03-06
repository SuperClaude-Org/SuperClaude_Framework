"""Tests for consistency-rate language and calibration framing (T04.03 / D-0029)."""

import pytest

from superclaude.cli.audit.spot_check import SpotCheckResult
from superclaude.cli.audit.validation_output import (
    CALIBRATION_NOTES,
    METHODOLOGY_LIMITATIONS,
    format_validation_report,
    render_validation_text,
)


def _make_spot_check_result() -> SpotCheckResult:
    return SpotCheckResult(
        total_consolidated=100,
        sample_size=10,
        consistent_count=9,
        inconsistent_count=1,
        overall_consistency_rate=0.90,
        per_tier_rates={"tier-1": 0.80, "tier-2": 0.95},
        per_tier_sample_counts={"tier-1": 4, "tier-2": 6},
        inconsistencies=[{
            "file_path": "bad.py",
            "original_tier": "tier-1",
            "original_action": "DELETE",
            "re_tier": "tier-2",
            "re_action": "KEEP",
        }],
    )


class TestConsistencyRateLanguage:
    """Verify no 'accuracy' language, only 'consistency rate'."""

    def test_report_uses_consistency_rate(self):
        """Formatted report uses 'consistency_rate' key, not 'accuracy'."""
        result = _make_spot_check_result()
        report = format_validation_report(result)
        assert "overall_consistency_rate" in report
        assert "accuracy" not in str(report).lower()

    def test_text_uses_consistency_rate(self):
        """Text rendering uses 'Consistency Rate', never 'Accuracy'."""
        result = _make_spot_check_result()
        text = render_validation_text(result)
        assert "Consistency Rate" in text
        assert "accuracy" not in text.lower()

    def test_calibration_notes_present_in_report(self):
        """Calibration notes section is present in formatted report."""
        result = _make_spot_check_result()
        report = format_validation_report(result)
        assert "calibration_notes" in report
        assert len(report["calibration_notes"]) > 50

    def test_calibration_notes_present_in_text(self):
        """Calibration notes section appears in text rendering."""
        result = _make_spot_check_result()
        text = render_validation_text(result)
        assert "Calibration Notes" in text
        assert "self-agreement" in text

    def test_methodology_limitations_present(self):
        """Methodology limitations are stated."""
        result = _make_spot_check_result()
        report = format_validation_report(result)
        assert "methodology_limitations" in report

    def test_per_tier_summary_in_report(self):
        """Per-tier summary is included in formatted report."""
        result = _make_spot_check_result()
        report = format_validation_report(result)
        assert len(report["per_tier_summary"]) == 2

    def test_text_per_tier_breakdown(self):
        """Text rendering includes per-tier breakdown."""
        result = _make_spot_check_result()
        text = render_validation_text(result)
        assert "tier-1" in text
        assert "tier-2" in text

    def test_inconsistencies_in_text(self):
        """Text rendering includes inconsistency details."""
        result = _make_spot_check_result()
        text = render_validation_text(result)
        assert "bad.py" in text
