"""Tests for remediate_prompts.py -- prompt builder, grouping, cross-file handling.

Covers:
- T04.01: build_remediation_prompt (pure function, spec section 2.3.4 template)
- T04.02: group_findings_by_file, build_cross_file_fragment
"""

import pytest

from superclaude.cli.roadmap.models import Finding
from superclaude.cli.roadmap.remediate_prompts import (
    build_cross_file_fragment,
    build_remediation_prompt,
    group_findings_by_file,
)


# ── Shared fixtures ──────────────────────────────────────────────────────


def _make_finding(
    id: str = "F-01",
    severity: str = "BLOCKING",
    status: str = "PENDING",
    fix_guidance: str = "Fix it",
    files_affected: list[str] | None = None,
    location: str = "file.py:1",
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
        files_affected=files_affected if files_affected is not None else ["file.py"],
        status=status,
    )


# ═══════════════════════════════════════════════════════════════
# T04.01 -- Build Remediation Prompt Builder
# ═══════════════════════════════════════════════════════════════


class TestBuildRemediationPrompt:
    """T04.01: build_remediation_prompt() is a pure function."""

    def test_has_header(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "remediation specialist" in result

    def test_has_target_file_section(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "## Target File" in result
        assert "`roadmap.md`" in result

    def test_has_findings_section(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "## Findings to Fix" in result

    def test_has_constraints_section(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "## Constraints" in result

    def test_constraints_edit_only(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "ONLY edit the target file" in result
        assert "`roadmap.md`" in result

    def test_constraints_preserve_yaml(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "Preserve YAML frontmatter" in result

    def test_constraints_preserve_headings(self):
        result = build_remediation_prompt("roadmap.md", [_make_finding()])
        assert "Preserve heading hierarchy" in result

    def test_finding_block_has_six_fields(self):
        f = _make_finding(
            id="F-01",
            severity="BLOCKING",
            description="Test desc",
            location="file.py:10",
            fix_guidance="Do the fix",
        )
        result = build_remediation_prompt("file.py", [f])
        assert "**ID**: F-01" in result
        assert "**Severity**: BLOCKING" in result
        assert "**Description**: Test desc" in result
        assert "**Location**: file.py:10" in result
        assert "**Evidence**: test evidence" in result
        assert "**Fix Guidance**: Do the fix" in result

    def test_multiple_findings(self):
        findings = [
            _make_finding("F-01", "BLOCKING"),
            _make_finding("F-02", "WARNING"),
        ]
        result = build_remediation_prompt("file.py", findings)
        assert "F-01" in result
        assert "F-02" in result
        assert "### F-01 [BLOCKING]" in result
        assert "### F-02 [WARNING]" in result

    def test_pure_function_deterministic(self):
        f = _make_finding()
        r1 = build_remediation_prompt("file.py", [f])
        r2 = build_remediation_prompt("file.py", [f])
        assert r1 == r2

    def test_pure_function_no_io(self):
        """Verify no I/O operations by running with a nonexistent file path."""
        f = _make_finding()
        # Should not raise -- it's a pure string builder
        result = build_remediation_prompt("/nonexistent/path.md", [f])
        assert "`/nonexistent/path.md`" in result

    def test_empty_findings(self):
        result = build_remediation_prompt("file.py", [])
        assert "## Target File" in result
        assert "## Findings to Fix" in result
        assert "## Constraints" in result


# ═══════════════════════════════════════════════════════════════
# T04.02 -- File-Level Grouping and Cross-File Finding Handler
# ═══════════════════════════════════════════════════════════════


class TestGroupFindingsByFile:
    """T04.02: group_findings_by_file() grouping logic."""

    def test_single_file_single_finding(self):
        f = _make_finding(files_affected=["roadmap.md"])
        groups = group_findings_by_file([f])
        assert "roadmap.md" in groups
        assert len(groups["roadmap.md"]) == 1

    def test_multiple_files_separate_groups(self):
        f1 = _make_finding("F-01", files_affected=["roadmap.md"])
        f2 = _make_finding("F-02", files_affected=["test-strategy.md"])
        groups = group_findings_by_file([f1, f2])
        assert len(groups) == 2
        assert "roadmap.md" in groups
        assert "test-strategy.md" in groups

    def test_cross_file_finding_in_both_groups(self):
        f = _make_finding(
            "F-01",
            files_affected=["roadmap.md", "test-strategy.md"],
        )
        groups = group_findings_by_file([f])
        assert "roadmap.md" in groups
        assert "test-strategy.md" in groups
        assert f in groups["roadmap.md"]
        assert f in groups["test-strategy.md"]

    def test_no_orphaned_findings(self):
        findings = [
            _make_finding("F-01", files_affected=["roadmap.md"]),
            _make_finding("F-02", files_affected=["test-strategy.md"]),
            _make_finding("F-03", files_affected=["roadmap.md", "extraction.md"]),
        ]
        groups = group_findings_by_file(findings)
        all_grouped = set()
        for file_findings in groups.values():
            for f in file_findings:
                all_grouped.add(f.id)
        assert all_grouped == {"F-01", "F-02", "F-03"}

    def test_no_concurrent_same_file(self):
        """Each file appears as exactly one group key."""
        findings = [
            _make_finding("F-01", files_affected=["roadmap.md"]),
            _make_finding("F-02", files_affected=["roadmap.md"]),
        ]
        groups = group_findings_by_file(findings)
        assert len(groups) == 1
        assert len(groups["roadmap.md"]) == 2

    def test_empty_findings(self):
        groups = group_findings_by_file([])
        assert groups == {}

    def test_no_files_affected_goes_to_unknown(self):
        f = _make_finding("F-01", files_affected=[])
        groups = group_findings_by_file([f])
        assert "unknown" in groups

    def test_pure_function_deterministic(self):
        findings = [_make_finding("F-01", files_affected=["a.md", "b.md"])]
        r1 = group_findings_by_file(findings)
        r2 = group_findings_by_file(findings)
        assert list(r1.keys()) == list(r2.keys())


class TestBuildCrossFileFragment:
    """T04.02: cross-file prompt scoping."""

    def test_fix_guidance_your_file(self):
        f = _make_finding(
            files_affected=["roadmap.md", "test-strategy.md"],
            fix_guidance="Update the milestone count",
        )
        result = build_cross_file_fragment(f, "roadmap.md")
        assert "Fix Guidance (YOUR FILE)" in result
        assert "Update the milestone count" in result

    def test_note_about_other_file(self):
        f = _make_finding(
            files_affected=["roadmap.md", "test-strategy.md"],
        )
        result = build_cross_file_fragment(f, "roadmap.md")
        assert "Note" in result
        assert "`test-strategy.md`" in result
        assert "separate agent" in result

    def test_single_file_no_note(self):
        f = _make_finding(files_affected=["roadmap.md"])
        result = build_cross_file_fragment(f, "roadmap.md")
        assert "Fix Guidance (YOUR FILE)" in result
        assert "separate agent" not in result

    def test_multiple_other_files(self):
        f = _make_finding(
            files_affected=["roadmap.md", "test-strategy.md", "extraction.md"],
        )
        result = build_cross_file_fragment(f, "roadmap.md")
        assert "`test-strategy.md`" in result
        assert "`extraction.md`" in result
