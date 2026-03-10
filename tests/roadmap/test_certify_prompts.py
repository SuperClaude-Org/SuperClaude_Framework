"""Tests for certify_prompts.py -- certification prompt builder, context extractor,
report generator, output parser, and outcome routing.

Covers:
- T05.01: build_certification_prompt (pure function, spec section 2.4.2 template)
- T05.02: extract_finding_context (scoped extraction, NFR-011)
- T05.03: generate_certification_report (YAML frontmatter, per-finding table)
- T05.04: route_certification_outcome (all-pass and some-fail paths, no-loop)
"""

import pytest

from superclaude.cli.roadmap.models import Finding
from superclaude.cli.roadmap.certify_prompts import (
    build_certification_prompt,
    extract_finding_context,
    generate_certification_report,
    parse_certification_output,
    route_certification_outcome,
)


# ── Shared fixtures ──────────────────────────────────────────────────────


def _make_finding(
    id: str = "F-01",
    severity: str = "BLOCKING",
    status: str = "PENDING",
    fix_guidance: str = "Fix it",
    files_affected: list[str] | None = None,
    location: str = "file.md:10",
    description: str | None = None,
) -> Finding:
    return Finding(
        id=id,
        severity=severity,
        dimension="Test",
        description=description or f"Finding {id}",
        location=location,
        evidence="test evidence",
        fix_guidance=fix_guidance,
        files_affected=files_affected if files_affected is not None else ["file.md"],
        status=status,
    )


# ═══════════════════════════════════════════════════════════════
# T05.01 -- Build Certification Prompt Builder
# ═══════════════════════════════════════════════════════════════


class TestBuildCertificationPrompt:
    """T05.01: build_certification_prompt() is a pure function per spec §2.4.2."""

    def test_has_header(self):
        result = build_certification_prompt([_make_finding()], {})
        assert "certification specialist" in result

    def test_has_skeptical_instruction(self):
        result = build_certification_prompt([_make_finding()], {})
        assert "skeptical" in result.lower()

    def test_has_verification_section(self):
        result = build_certification_prompt([_make_finding()], {})
        assert "## Findings to Verify" in result

    def test_has_output_format(self):
        result = build_certification_prompt([_make_finding()], {})
        assert "## Output Format" in result
        assert "PASS|FAIL" in result

    def test_per_finding_checklist(self):
        f = _make_finding(
            id="F-01",
            severity="BLOCKING",
            description="Missing milestone count",
            location="roadmap.md:42",
            fix_guidance="Add milestone count",
        )
        result = build_certification_prompt([f], {})
        assert "**Original Issue**: Missing milestone count" in result
        assert "**Location**: roadmap.md:42" in result
        assert "**Fix Guidance**: Add milestone count" in result
        assert "**Check Instruction**" in result

    def test_context_sections_included(self):
        context = {"roadmap.md:42": "## Milestones\n\n1. Alpha\n2. Beta"}
        result = build_certification_prompt([_make_finding()], context)
        assert "## Context Sections" in result
        assert "## Milestones" in result

    def test_empty_context_sections(self):
        result = build_certification_prompt([_make_finding()], {})
        assert "## Context Sections" not in result

    def test_multiple_findings(self):
        findings = [
            _make_finding("F-01", "BLOCKING"),
            _make_finding("F-02", "WARNING"),
        ]
        result = build_certification_prompt(findings, {})
        assert "### F-01 [BLOCKING]" in result
        assert "### F-02 [WARNING]" in result

    def test_pure_function_deterministic(self):
        f = _make_finding()
        r1 = build_certification_prompt([f], {})
        r2 = build_certification_prompt([f], {})
        assert r1 == r2

    def test_pure_function_no_io(self):
        """No I/O operations: nonexistent paths don't raise."""
        f = _make_finding(location="/nonexistent/path.md:99")
        result = build_certification_prompt([f], {})
        assert "/nonexistent/path.md:99" in result

    def test_accepts_pre_extracted_context(self):
        """Function accepts pre-extracted context sections, not full file content."""
        context = {"section-key": "pre-extracted content"}
        result = build_certification_prompt([_make_finding()], context)
        assert "pre-extracted content" in result


# ═══════════════════════════════════════════════════════════════
# T05.02 -- Certification Context Extractor
# ═══════════════════════════════════════════════════════════════


class TestExtractFindingContext:
    """T05.02: extract_finding_context() returns scoped sections, not full content."""

    def test_line_range_extraction(self):
        content = "\n".join([f"Line {i}" for i in range(1, 30)])
        f = _make_finding(location="file.md:15")
        result = extract_finding_context(content, f)
        assert "Line 15" in result
        # Should NOT include all 30 lines (scoped, not full)
        assert "Line 1\n" not in result or "Line 28" not in result

    def test_line_range_with_end(self):
        content = "\n".join([f"Line {i}" for i in range(1, 30)])
        f = _make_finding(location="file.md:10-15")
        result = extract_finding_context(content, f)
        assert "Line 10" in result
        assert "Line 15" in result

    def test_section_reference_extraction(self):
        content = "# Doc\n\n## 3.1 Milestones\n\nContent here\n\n## 3.2 Timeline\n\nOther content"
        f = _make_finding(location="roadmap.md:§3.1")
        result = extract_finding_context(content, f)
        assert "3.1 Milestones" in result
        assert "Content here" in result
        # Should stop at next same-level heading
        assert "3.2 Timeline" not in result

    def test_empty_content_returns_empty(self):
        f = _make_finding(location="file.md:10")
        result = extract_finding_context("", f)
        assert result == ""

    def test_empty_location_returns_empty(self):
        f = _make_finding(location="")
        result = extract_finding_context("Some content", f)
        assert result == ""

    def test_token_cost_proportional_to_section(self):
        """Token cost per finding is proportional to section size, not file size."""
        # Large file with small relevant section
        large_content = "\n".join([f"Line {i}" for i in range(1, 500)])
        f = _make_finding(location="file.md:250")
        result = extract_finding_context(large_content, f)
        # Result should be much smaller than full file
        assert len(result) < len(large_content) * 0.2

    def test_includes_enclosing_heading(self):
        content = "# Title\n\n## Section A\n\nContent A line 1\nContent A line 2\nContent A line 3\n\n## Section B\n\nContent B"
        f = _make_finding(location="file.md:5")
        result = extract_finding_context(content, f)
        assert "## Section A" in result


# ═══════════════════════════════════════════════════════════════
# T05.03 -- Certification Report Generation
# ═══════════════════════════════════════════════════════════════


class TestGenerateCertificationReport:
    """T05.03: generate_certification_report() produces spec §2.4.3 format."""

    def test_yaml_frontmatter_present(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "Fixed"}]
        report = generate_certification_report(results, [_make_finding()])
        assert report.startswith("---\n")
        assert "\n---\n" in report[3:]

    def test_frontmatter_has_all_five_fields(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "Fixed"}]
        report = generate_certification_report(results, [_make_finding()])
        assert "findings_verified:" in report
        assert "findings_passed:" in report
        assert "findings_failed:" in report
        assert "certified:" in report
        assert "certification_date:" in report

    def test_frontmatter_values_computed(self):
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Fixed"},
            {"finding_id": "F-02", "result": "FAIL", "justification": "Not fixed"},
        ]
        findings = [_make_finding("F-01"), _make_finding("F-02", "WARNING")]
        report = generate_certification_report(results, findings)
        assert "findings_verified: 2" in report
        assert "findings_passed: 1" in report
        assert "findings_failed: 1" in report
        assert "certified: false" in report

    def test_certified_true_when_all_pass(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "Fixed"}]
        report = generate_certification_report(results, [_make_finding()])
        assert "certified: true" in report

    def test_per_finding_table_columns(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "Fixed"}]
        report = generate_certification_report(results, [_make_finding()])
        assert "| Finding | Severity | Result | Justification |" in report

    def test_per_finding_table_data(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "All good"}]
        report = generate_certification_report(results, [_make_finding()])
        assert "| F-01 | BLOCKING | PASS | All good |" in report

    def test_summary_section_present(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "Fixed"}]
        report = generate_certification_report(results, [_make_finding()])
        assert "## Summary" in report

    def test_report_minimum_lines(self):
        results = [{"finding_id": "F-01", "result": "PASS", "justification": "Fixed"}]
        report = generate_certification_report(results, [_make_finding()])
        assert len(report.splitlines()) >= 15


# ═══════════════════════════════════════════════════════════════
# T05.03 -- Parse Certification Output
# ═══════════════════════════════════════════════════════════════


class TestParseCertificationOutput:
    """Certification output parsing."""

    def test_parse_pass_line(self):
        output = "F-01: PASS -- Milestone count updated correctly"
        results = parse_certification_output(output)
        assert len(results) == 1
        assert results[0]["finding_id"] == "F-01"
        assert results[0]["result"] == "PASS"
        assert "Milestone count" in results[0]["justification"]

    def test_parse_fail_line(self):
        output = "F-02: FAIL -- Content still references old value"
        results = parse_certification_output(output)
        assert len(results) == 1
        assert results[0]["result"] == "FAIL"

    def test_parse_multiple_lines(self):
        output = (
            "F-01: PASS -- Fixed correctly\n"
            "F-02: FAIL -- Not addressed\n"
            "F-03: PASS -- Good\n"
        )
        results = parse_certification_output(output)
        assert len(results) == 3

    def test_skip_non_matching_lines(self):
        output = (
            "Some preamble text\n"
            "F-01: PASS -- Fixed\n"
            "More text\n"
        )
        results = parse_certification_output(output)
        assert len(results) == 1

    def test_empty_output(self):
        results = parse_certification_output("")
        assert results == []


# ═══════════════════════════════════════════════════════════════
# T05.04 -- Outcome Routing and No-Loop Constraint
# ═══════════════════════════════════════════════════════════════


class TestRouteCertificationOutcome:
    """T05.04: outcome routing per spec §2.4.4 with NFR-012 no-loop."""

    def test_all_pass_certified(self):
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Good"},
            {"finding_id": "F-02", "result": "PASS", "justification": "Good"},
        ]
        outcome = route_certification_outcome(results)
        assert outcome["status"] == "certified"
        assert outcome["tasklist_ready"] is True

    def test_some_fail_certified_with_caveats(self):
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Good"},
            {"finding_id": "F-02", "result": "FAIL", "justification": "Not fixed"},
        ]
        outcome = route_certification_outcome(results)
        assert outcome["status"] == "certified-with-caveats"
        assert outcome["tasklist_ready"] is False
        assert "F-02" in outcome["failed_findings"]

    def test_all_fail(self):
        results = [
            {"finding_id": "F-01", "result": "FAIL", "justification": "Bad"},
        ]
        outcome = route_certification_outcome(results)
        assert outcome["status"] == "certified-with-caveats"
        assert outcome["findings_failed"] == 1

    def test_no_loop_enforcement(self):
        """NFR-012: pipeline completes after single certification pass."""
        results = [
            {"finding_id": "F-01", "result": "FAIL", "justification": "Bad"},
        ]
        outcome = route_certification_outcome(results)
        assert outcome["loop"] is False

    def test_no_loop_on_success(self):
        """NFR-012: no loop even on success."""
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Good"},
        ]
        outcome = route_certification_outcome(results)
        assert outcome["loop"] is False

    def test_state_updates_atomic(self):
        """State updates are consistent dict values."""
        results = [
            {"finding_id": "F-01", "result": "PASS", "justification": "Good"},
        ]
        outcome = route_certification_outcome(results)
        assert isinstance(outcome["status"], str)
        assert isinstance(outcome["tasklist_ready"], bool)
        assert isinstance(outcome["findings_passed"], int)
        assert isinstance(outcome["findings_failed"], int)

    def test_empty_results(self):
        outcome = route_certification_outcome([])
        assert outcome["status"] == "certified-with-caveats"
        assert outcome["tasklist_ready"] is False
