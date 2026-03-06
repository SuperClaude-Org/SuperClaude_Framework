"""Tests for report depth modes (T04.10 / D-0036)."""

import pytest

from superclaude.cli.audit.classification import V2Action, V2Tier
from superclaude.cli.audit.consolidation import (
    ConsolidatedFinding,
    ConsolidationReport,
)
from superclaude.cli.audit.report_depth import (
    ReportDepth,
    parse_depth,
    render_detailed,
    render_report,
    render_standard,
    render_summary,
)


def _make_report(count: int = 20) -> ConsolidationReport:
    findings = []
    for i in range(count):
        action = V2Action.DELETE if i % 4 == 0 else V2Action.KEEP
        tier = V2Tier.TIER_1 if action == V2Action.DELETE else V2Tier.TIER_2
        findings.append(ConsolidatedFinding(
            file_path=f"src/file_{i}.py",
            tier=tier,
            action=action,
            confidence=0.80 + (i % 5) * 0.04,
            evidence=[f"ev_{i}"],
            source_phases=["surface"],
        ))
    return ConsolidationReport(
        findings=findings,
        total_input_findings=count,
        total_consolidated=count,
    )


class TestParseDepth:
    """Verify depth flag parsing."""

    def test_default_is_standard(self):
        assert parse_depth(None) == ReportDepth.STANDARD

    def test_summary(self):
        assert parse_depth("summary") == ReportDepth.SUMMARY

    def test_standard(self):
        assert parse_depth("standard") == ReportDepth.STANDARD

    def test_detailed(self):
        assert parse_depth("detailed") == ReportDepth.DETAILED

    def test_case_insensitive(self):
        assert parse_depth("SUMMARY") == ReportDepth.SUMMARY

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Invalid depth"):
            parse_depth("verbose")


class TestSummaryMode:
    """Verify summary depth output."""

    def test_has_tier_counts(self):
        report = _make_report()
        result = render_summary(report)
        assert "tier_counts" in result

    def test_top_10_only(self):
        report = _make_report(30)
        result = render_summary(report)
        assert len(result["top_findings"]) == 10

    def test_depth_label(self):
        report = _make_report()
        result = render_summary(report)
        assert result["depth"] == "summary"


class TestStandardMode:
    """Verify standard depth output."""

    def test_has_sections(self):
        report = _make_report()
        result = render_standard(report)
        assert "sections" in result

    def test_sections_have_evidence(self):
        report = _make_report()
        result = render_standard(report)
        for section_name, entries in result["sections"].items():
            for entry in entries:
                assert "evidence" in entry

    def test_is_default(self):
        report = _make_report()
        result = render_report(report)
        assert result["depth"] == "standard"


class TestDetailedMode:
    """Verify detailed depth output."""

    def test_per_file_entries(self):
        report = _make_report(15)
        result = render_detailed(report)
        assert len(result["files"]) == 15

    def test_full_evidence_chains(self):
        report = _make_report()
        result = render_detailed(report)
        for f in result["files"]:
            assert "evidence" in f
            assert "v1_category" in f

    def test_conflicts_included(self):
        report = _make_report()
        result = render_detailed(report)
        assert "conflicts" in result


class TestRenderReport:
    """Verify depth routing."""

    def test_summary_route(self):
        report = _make_report()
        result = render_report(report, ReportDepth.SUMMARY)
        assert result["depth"] == "summary"

    def test_detailed_route(self):
        report = _make_report()
        result = render_report(report, ReportDepth.DETAILED)
        assert result["depth"] == "detailed"

    def test_standard_route(self):
        report = _make_report()
        result = render_report(report, ReportDepth.STANDARD)
        assert result["depth"] == "standard"
