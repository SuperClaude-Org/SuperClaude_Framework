"""Tests for CERTIFY_GATE definition in gates.py.

Covers:
- T05.05: CERTIFY_GATE with required frontmatter, min_lines, semantic checks
"""

import pytest

from superclaude.cli.roadmap.gates import (
    CERTIFY_GATE,
    _frontmatter_values_non_empty,
    _has_per_finding_table,
)


# ═══════════════════════════════════════════════════════════════
# T05.05 -- CERTIFY_GATE Definition
# ═══════════════════════════════════════════════════════════════


class TestCertifyGateDefinition:
    """T05.05: CERTIFY_GATE matches spec §2.4.5 field-for-field."""

    def test_required_frontmatter_fields(self):
        expected = {
            "findings_verified",
            "findings_passed",
            "findings_failed",
            "certified",
            "certification_date",
        }
        assert set(CERTIFY_GATE.required_frontmatter_fields) == expected

    def test_min_lines(self):
        assert CERTIFY_GATE.min_lines == 15

    def test_enforcement_tier(self):
        assert CERTIFY_GATE.enforcement_tier == "STRICT"

    def test_has_semantic_checks(self):
        assert CERTIFY_GATE.semantic_checks is not None
        assert len(CERTIFY_GATE.semantic_checks) == 2

    def test_semantic_check_names(self):
        check_names = {c.name for c in CERTIFY_GATE.semantic_checks}
        assert "frontmatter_values_non_empty" in check_names
        assert "per_finding_table_present" in check_names


# ═══════════════════════════════════════════════════════════════
# T05.05 -- Semantic Check: per_finding_table_present
# ═══════════════════════════════════════════════════════════════


class TestHasPerFindingTable:
    """T05.05: _has_per_finding_table() semantic check."""

    def test_valid_report_passes(self):
        content = (
            "---\n"
            "findings_verified: 2\n"
            "findings_passed: 1\n"
            "findings_failed: 1\n"
            "certified: false\n"
            "certification_date: 2026-03-10T00:00:00Z\n"
            "---\n"
            "\n"
            "# Certification Report\n"
            "\n"
            "## Per-Finding Results\n"
            "\n"
            "| Finding | Severity | Result | Justification |\n"
            "|---------|----------|--------|---------------|\n"
            "| F-01 | BLOCKING | PASS | Fixed correctly |\n"
            "| F-02 | WARNING | FAIL | Not addressed |\n"
        )
        assert _has_per_finding_table(content) is True

    def test_missing_table_header_fails(self):
        content = (
            "---\n"
            "findings_verified: 1\n"
            "---\n"
            "\n"
            "# Report\n"
            "\n"
            "No table here.\n"
        )
        assert _has_per_finding_table(content) is False

    def test_missing_data_rows_fails(self):
        content = (
            "| Finding | Severity | Result | Justification |\n"
            "|---------|----------|--------|---------------|\n"
            "No data rows\n"
        )
        assert _has_per_finding_table(content) is False

    def test_header_only_no_data_fails(self):
        content = (
            "| Finding | Severity | Result | Justification |\n"
            "|---------|----------|--------|---------------|\n"
        )
        assert _has_per_finding_table(content) is False

    def test_rejects_malformed_reports(self):
        content = "Just some text without any table"
        assert _has_per_finding_table(content) is False


# ═══════════════════════════════════════════════════════════════
# T05.05 -- Gate Validation Integration
# ═══════════════════════════════════════════════════════════════


class TestCertifyGateValidation:
    """Gate passes on well-formed reports and rejects malformed ones."""

    def _make_valid_report(self) -> str:
        return (
            "---\n"
            "findings_verified: 2\n"
            "findings_passed: 2\n"
            "findings_failed: 0\n"
            "certified: true\n"
            "certification_date: 2026-03-10T00:00:00Z\n"
            "---\n"
            "\n"
            "# Certification Report\n"
            "\n"
            "## Per-Finding Results\n"
            "\n"
            "| Finding | Severity | Result | Justification |\n"
            "|---------|----------|--------|---------------|\n"
            "| F-01 | BLOCKING | PASS | Fixed correctly |\n"
            "| F-02 | WARNING | PASS | Addressed |\n"
            "\n"
            "## Summary\n"
            "\n"
            "All findings verified and passed.\n"
        )

    def test_well_formed_report_passes_all_checks(self):
        content = self._make_valid_report()
        # Check frontmatter non-empty
        assert _frontmatter_values_non_empty(content) is True
        # Check per-finding table
        assert _has_per_finding_table(content) is True
        # Check min lines
        assert len(content.splitlines()) >= CERTIFY_GATE.min_lines

    def test_missing_frontmatter_fails(self):
        content = "# Report\n\nNo frontmatter here.\n" * 5
        assert _frontmatter_values_non_empty(content) is False

    def test_empty_frontmatter_value_fails(self):
        content = (
            "---\n"
            "findings_verified:\n"
            "findings_passed: 1\n"
            "findings_failed: 0\n"
            "certified: true\n"
            "certification_date: 2026-03-10T00:00:00Z\n"
            "---\n"
        )
        assert _frontmatter_values_non_empty(content) is False
