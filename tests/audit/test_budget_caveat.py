"""Tests for budget realism caveats (T04.09 / D-0035)."""

import pytest

from superclaude.cli.audit.budget_caveat import (
    BUDGET_CAVEAT,
    ESTIMATION_METHODOLOGY,
    VARIANCE_RANGE,
    add_caveat_to_dry_run,
    add_caveat_to_report,
)


class TestBudgetCaveatDryRun:
    """Verify caveats in dry-run output."""

    def test_caveat_section_present(self):
        """Dry-run output includes budget realism caveat section."""
        dry_run = {"file_count": 100, "estimated_tokens": 50000}
        result = add_caveat_to_dry_run(dry_run)
        assert "budget_realism_caveat" in result

    def test_caveat_text_present(self):
        """Caveat text describes estimation methodology and variance."""
        dry_run = {"file_count": 100}
        result = add_caveat_to_dry_run(dry_run)
        caveat = result["budget_realism_caveat"]
        assert "20-50%" in caveat["variance_range"]
        assert "heuristic" in caveat["estimation_methodology"].lower()

    def test_original_data_preserved(self):
        """Original dry-run data is not modified."""
        dry_run = {"file_count": 100, "batch_count": 5}
        result = add_caveat_to_dry_run(dry_run)
        assert result["file_count"] == 100
        assert result["batch_count"] == 5


class TestBudgetCaveatReport:
    """Verify caveats in final report output."""

    def test_caveat_section_present(self):
        """Final report includes budget realism caveat section."""
        report = {"total_findings": 50}
        result = add_caveat_to_report(report)
        assert "budget_realism_caveat" in result

    def test_caveat_content(self):
        """Caveat states estimation methodology and variance range."""
        report = {}
        result = add_caveat_to_report(report)
        caveat = result["budget_realism_caveat"]
        assert "caveat" in caveat
        assert "estimation_methodology" in caveat
        assert "variance_range" in caveat

    def test_original_data_preserved(self):
        """Original report data is not modified."""
        report = {"total_findings": 50, "status": "complete"}
        result = add_caveat_to_report(report)
        assert result["total_findings"] == 50
