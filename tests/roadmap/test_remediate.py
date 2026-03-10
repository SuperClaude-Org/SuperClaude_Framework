"""Tests for Phase 3 -- remediation summary, prompt, filter, tasklist, gate.

Covers:
- T03.01: format_validation_summary, should_skip_prompt
- T03.02: filter_findings, RemediationScope, auto-SKIP
- T03.03: generate_stub_tasklist, zero-findings guard
- T03.04: generate_remediation_tasklist
- T03.05: REMEDIATE_GATE, _all_actionable_have_status, _frontmatter_values_non_empty
"""

import pytest

from superclaude.cli.roadmap.models import Finding
from superclaude.cli.roadmap.remediate import (
    RemediationScope,
    filter_findings,
    format_validation_summary,
    generate_remediation_tasklist,
    generate_stub_tasklist,
    should_skip_prompt,
)
from superclaude.cli.roadmap.gates import (
    REMEDIATE_GATE,
    _all_actionable_have_status,
    _frontmatter_values_non_empty,
)


# ── Shared fixtures ──────────────────────────────────────────────────────


def _make_finding(
    id: str = "F-01",
    severity: str = "BLOCKING",
    status: str = "PENDING",
    agreement_category: str = "",
    fix_guidance: str = "Fix it",
    files_affected: list[str] | None = None,
) -> Finding:
    return Finding(
        id=id,
        severity=severity,
        dimension="Test",
        description=f"Finding {id}",
        location="file.py:1",
        evidence="test evidence",
        fix_guidance=fix_guidance,
        files_affected=files_affected or ["file.py"],
        status=status,
        agreement_category=agreement_category,
    )


MIXED_FINDINGS = [
    _make_finding("F-01", "BLOCKING"),
    _make_finding("F-02", "BLOCKING"),
    _make_finding("F-03", "WARNING"),
    _make_finding("F-04", "WARNING"),
    _make_finding("F-05", "INFO", fix_guidance="Informational fix"),
]

AUTO_SKIP_FINDINGS = [
    _make_finding("F-01", "BLOCKING"),
    _make_finding("F-02", "WARNING", agreement_category="NO_ACTION_REQUIRED"),
    _make_finding("F-03", "BLOCKING", agreement_category="OUT_OF_SCOPE"),
    _make_finding("F-04", "INFO"),
]

ALREADY_FIXED_FINDINGS = [
    _make_finding("F-01", "BLOCKING", status="FIXED"),
    _make_finding("F-02", "WARNING"),
    _make_finding("F-03", "INFO", status="SKIPPED"),
]


# ═══════════════════════════════════════════════════════════════
# T03.01 -- Terminal Summary and Prompt
# ═══════════════════════════════════════════════════════════════


class TestFormatValidationSummary:
    """T03.01: format_validation_summary() is a pure function."""

    def test_groups_by_severity(self):
        result = format_validation_summary(MIXED_FINDINGS)
        assert "BLOCKING" in result
        assert "WARNING" in result
        assert "INFO" in result

    def test_shows_counts(self):
        result = format_validation_summary(MIXED_FINDINGS)
        assert "BLOCKING: 2" in result
        assert "WARNING: 2" in result
        assert "INFO: 1" in result
        assert "Total findings: 5" in result

    def test_includes_finding_ids(self):
        result = format_validation_summary(MIXED_FINDINGS)
        assert "F-01" in result
        assert "F-05" in result

    def test_includes_descriptions(self):
        result = format_validation_summary(MIXED_FINDINGS)
        assert "Finding F-01" in result

    def test_empty_findings(self):
        result = format_validation_summary([])
        assert "Total findings: 0" in result
        assert "BLOCKING: 0" in result

    def test_pure_function(self):
        """Same input produces same output."""
        r1 = format_validation_summary(MIXED_FINDINGS)
        r2 = format_validation_summary(MIXED_FINDINGS)
        assert r1 == r2

    def test_only_blocking(self):
        findings = [_make_finding("F-01", "BLOCKING")]
        result = format_validation_summary(findings)
        assert "BLOCKING: 1" in result
        assert "WARNING: 0" in result
        # WARNING section header should not appear
        assert "--- WARNING ---" not in result


class TestShouldSkipPrompt:
    """T03.01: zero-BLOCKING-zero-WARNING case auto-skips prompt."""

    def test_skip_when_only_info(self):
        findings = [_make_finding("F-01", "INFO")]
        assert should_skip_prompt(findings) is True

    def test_skip_when_empty(self):
        assert should_skip_prompt([]) is True

    def test_no_skip_when_blocking(self):
        findings = [_make_finding("F-01", "BLOCKING")]
        assert should_skip_prompt(findings) is False

    def test_no_skip_when_warning(self):
        findings = [_make_finding("F-01", "WARNING")]
        assert should_skip_prompt(findings) is False

    def test_no_skip_mixed(self):
        assert should_skip_prompt(MIXED_FINDINGS) is False


# ═══════════════════════════════════════════════════════════════
# T03.02 -- Scope Filter and Auto-SKIP
# ═══════════════════════════════════════════════════════════════


class TestFilterFindings:
    """T03.02: filter_findings() is a pure function with no I/O."""

    def test_blocking_only_scope(self):
        actionable, skipped = filter_findings(MIXED_FINDINGS, RemediationScope.BLOCKING_ONLY)
        assert len(actionable) == 2
        assert all(f.severity == "BLOCKING" for f in actionable)
        assert len(skipped) == 3

    def test_blocking_warning_scope(self):
        actionable, skipped = filter_findings(MIXED_FINDINGS, RemediationScope.BLOCKING_WARNING)
        assert len(actionable) == 4
        assert all(f.severity in ("BLOCKING", "WARNING") for f in actionable)
        assert len(skipped) == 1

    def test_all_scope(self):
        actionable, skipped = filter_findings(MIXED_FINDINGS, RemediationScope.ALL)
        assert len(actionable) == 5
        assert len(skipped) == 0

    def test_all_scope_skips_no_guidance(self):
        findings = [_make_finding("F-01", "INFO", fix_guidance="")]
        actionable, skipped = filter_findings(findings, RemediationScope.ALL)
        assert len(actionable) == 0
        assert len(skipped) == 1

    def test_auto_skip_no_action_required(self):
        actionable, skipped = filter_findings(
            AUTO_SKIP_FINDINGS, RemediationScope.ALL
        )
        # F-02 (NO_ACTION_REQUIRED) and F-03 (OUT_OF_SCOPE) are auto-skipped
        assert len(skipped) == 2
        assert any(f.id == "F-02" for f in skipped)
        assert any(f.id == "F-03" for f in skipped)

    def test_auto_skip_out_of_scope(self):
        actionable, skipped = filter_findings(
            AUTO_SKIP_FINDINGS, RemediationScope.BLOCKING_ONLY
        )
        # F-01 is actionable BLOCKING; F-03 OUT_OF_SCOPE auto-skipped despite BLOCKING
        assert len(actionable) == 1
        assert actionable[0].id == "F-01"

    def test_already_fixed_skipped(self):
        actionable, skipped = filter_findings(
            ALREADY_FIXED_FINDINGS, RemediationScope.ALL
        )
        # F-01 FIXED -> skipped, F-03 SKIPPED -> skipped
        assert len(actionable) == 1
        assert actionable[0].id == "F-02"
        assert len(skipped) == 2

    def test_returns_both_lists(self):
        actionable, skipped = filter_findings(MIXED_FINDINGS, RemediationScope.BLOCKING_ONLY)
        assert isinstance(actionable, list)
        assert isinstance(skipped, list)

    def test_pure_function(self):
        r1 = filter_findings(MIXED_FINDINGS, RemediationScope.ALL)
        r2 = filter_findings(MIXED_FINDINGS, RemediationScope.ALL)
        assert len(r1[0]) == len(r2[0])
        assert len(r1[1]) == len(r2[1])

    def test_empty_findings(self):
        actionable, skipped = filter_findings([], RemediationScope.ALL)
        assert actionable == []
        assert skipped == []


# ═══════════════════════════════════════════════════════════════
# T03.03 -- Zero-Findings Guard and Skip-Remediation Path
# ═══════════════════════════════════════════════════════════════


class TestStubTasklist:
    """T03.03: zero-findings guard produces stub with actionable: 0."""

    def test_stub_has_frontmatter(self):
        result = generate_stub_tasklist("report.md", "content")
        assert result.startswith("---")
        assert "actionable: 0" in result
        assert "total_findings: 0" in result
        assert "skipped: 0" in result

    def test_stub_has_type(self):
        result = generate_stub_tasklist("report.md", "content")
        assert "type: remediation-tasklist" in result

    def test_stub_has_hash(self):
        result = generate_stub_tasklist("report.md", "content")
        assert "source_report_hash:" in result

    def test_stub_has_source_report(self):
        result = generate_stub_tasklist("path/to/report.md", "content")
        assert "source_report: path/to/report.md" in result

    def test_stub_has_generated_timestamp(self):
        result = generate_stub_tasklist("report.md", "content")
        assert "generated:" in result

    def test_stub_mentions_no_actionable(self):
        result = generate_stub_tasklist("report.md", "content")
        assert "No actionable findings" in result

    def test_zero_findings_after_filter(self):
        """Integration: filter -> zero actionable -> stub tasklist."""
        findings = [
            _make_finding("F-01", "BLOCKING", agreement_category="OUT_OF_SCOPE"),
            _make_finding("F-02", "WARNING", agreement_category="NO_ACTION_REQUIRED"),
        ]
        actionable, skipped = filter_findings(findings, RemediationScope.ALL)
        assert len(actionable) == 0
        result = generate_stub_tasklist("report.md", "content")
        assert "actionable: 0" in result


# ═══════════════════════════════════════════════════════════════
# T03.04 -- Remediation Tasklist Generation
# ═══════════════════════════════════════════════════════════════


class TestGenerateRemediationTasklist:
    """T03.04: generate_remediation_tasklist() is a pure function."""

    def test_has_yaml_frontmatter(self):
        result = generate_remediation_tasklist(
            MIXED_FINDINGS, "report.md", "report content"
        )
        assert result.startswith("---")
        assert "type: remediation-tasklist" in result

    def test_frontmatter_fields(self):
        result = generate_remediation_tasklist(
            MIXED_FINDINGS, "report.md", "report content"
        )
        assert "source_report: report.md" in result
        assert "source_report_hash:" in result
        assert "generated:" in result
        assert "total_findings: 5" in result
        assert "actionable: 5" in result
        assert "skipped: 0" in result

    def test_source_report_hash_is_sha256(self):
        import hashlib

        content = "test report content"
        expected_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        result = generate_remediation_tasklist(
            [_make_finding("F-01")], "r.md", content
        )
        assert expected_hash in result

    def test_severity_grouped(self):
        result = generate_remediation_tasklist(
            MIXED_FINDINGS, "report.md", "content"
        )
        blocking_pos = result.find("## BLOCKING")
        warning_pos = result.find("## WARNING")
        info_pos = result.find("## INFO")
        assert blocking_pos < warning_pos < info_pos

    def test_entry_format(self):
        result = generate_remediation_tasklist(
            [_make_finding("F-01", "BLOCKING")], "r.md", "c"
        )
        # Expected: - [ ] F-01 | file.py | PENDING -- Finding F-01
        assert "- [ ] F-01 | file.py | PENDING -- Finding F-01" in result

    def test_skipped_entries_checked(self):
        findings = [_make_finding("F-01", "BLOCKING", status="SKIPPED")]
        result = generate_remediation_tasklist(findings, "r.md", "c")
        assert "- [x] F-01" in result

    def test_pure_function_deterministic(self):
        r1 = generate_remediation_tasklist(MIXED_FINDINGS, "r.md", "c")
        r2 = generate_remediation_tasklist(MIXED_FINDINGS, "r.md", "c")
        # Timestamps will differ slightly, but structure should match
        assert r1.split("generated:")[0] == r2.split("generated:")[0]

    def test_multiple_files_affected(self):
        f = _make_finding("F-01", "BLOCKING", files_affected=["a.py", "b.py"])
        result = generate_remediation_tasklist([f], "r.md", "c")
        assert "a.py, b.py" in result

    def test_no_files_affected(self):
        f = Finding(
            id="F-01", severity="BLOCKING", dimension="Test",
            description="No files", location="", evidence="ev",
            fix_guidance="fix", files_affected=[], status="PENDING",
        )
        result = generate_remediation_tasklist([f], "r.md", "c")
        assert "unknown" in result

    def test_min_lines_threshold(self):
        result = generate_remediation_tasklist(
            MIXED_FINDINGS, "report.md", "content"
        )
        lines = result.strip().splitlines()
        assert len(lines) >= 10, f"Expected >= 10 lines, got {len(lines)}"


# ═══════════════════════════════════════════════════════════════
# T03.05 -- REMEDIATE_GATE
# ═══════════════════════════════════════════════════════════════


class TestRemediateGate:
    """T03.05: REMEDIATE_GATE matches spec section 2.3.7."""

    def test_gate_exists(self):
        assert REMEDIATE_GATE is not None

    def test_gate_enforcement_tier(self):
        assert REMEDIATE_GATE.enforcement_tier == "STRICT"

    def test_gate_min_lines(self):
        assert REMEDIATE_GATE.min_lines == 10

    def test_gate_required_frontmatter_fields(self):
        expected = {
            "type", "source_report", "source_report_hash",
            "total_findings", "actionable", "skipped",
        }
        assert set(REMEDIATE_GATE.required_frontmatter_fields) == expected

    def test_gate_has_semantic_checks(self):
        assert REMEDIATE_GATE.semantic_checks is not None
        assert len(REMEDIATE_GATE.semantic_checks) == 2

    def test_gate_semantic_check_names(self):
        names = {c.name for c in REMEDIATE_GATE.semantic_checks}
        assert "frontmatter_values_non_empty" in names
        assert "all_actionable_have_status" in names


class TestAllActionableHaveStatus:
    """T03.05: _all_actionable_have_status semantic check."""

    def test_all_fixed_passes(self):
        content = (
            "---\ntype: remediation-tasklist\n---\n\n"
            "## BLOCKING\n\n"
            "- [ ] F-01 | file.py | FIXED -- desc\n"
            "- [ ] F-02 | file.py | FAILED -- desc\n"
        )
        assert _all_actionable_have_status(content) is True

    def test_pending_fails(self):
        content = (
            "---\ntype: remediation-tasklist\n---\n\n"
            "## BLOCKING\n\n"
            "- [ ] F-01 | file.py | PENDING -- desc\n"
        )
        assert _all_actionable_have_status(content) is False

    def test_skipped_entries_ignored(self):
        content = (
            "---\ntype: remediation-tasklist\n---\n\n"
            "## SKIPPED\n\n"
            "- [x] F-01 | file.py | SKIPPED -- desc\n"
        )
        assert _all_actionable_have_status(content) is True

    def test_no_actionable_entries_passes(self):
        content = "---\ntype: remediation-tasklist\n---\n\nNo findings.\n"
        assert _all_actionable_have_status(content) is True

    def test_mixed_statuses(self):
        content = (
            "---\ntype: remediation-tasklist\n---\n\n"
            "- [ ] F-01 | file.py | FIXED -- ok\n"
            "- [ ] F-02 | file.py | PENDING -- not done\n"
        )
        assert _all_actionable_have_status(content) is False


class TestFrontmatterValuesNonEmptyForRemediate:
    """T03.05: _frontmatter_values_non_empty rejects empty values."""

    def test_valid_frontmatter_passes(self):
        content = (
            "---\n"
            "type: remediation-tasklist\n"
            "source_report: report.md\n"
            "source_report_hash: abc123\n"
            "total_findings: 5\n"
            "actionable: 3\n"
            "skipped: 2\n"
            "---\n"
            "\n# Tasklist\n"
        )
        assert _frontmatter_values_non_empty(content) is True

    def test_empty_value_fails(self):
        content = (
            "---\n"
            "type: remediation-tasklist\n"
            "source_report:\n"
            "---\n"
        )
        assert _frontmatter_values_non_empty(content) is False

    def test_no_frontmatter_fails(self):
        content = "No frontmatter here."
        assert _frontmatter_values_non_empty(content) is False


class TestRemediateGateIntegration:
    """Integration: generated tasklist validates against REMEDIATE_GATE."""

    def test_generated_tasklist_passes_gate_checks(self):
        """A well-formed tasklist passes all semantic checks."""
        tasklist = generate_remediation_tasklist(
            [
                _make_finding("F-01", "BLOCKING", status="FIXED"),
                _make_finding("F-02", "WARNING", status="FAILED"),
            ],
            "report.md",
            "report content",
        )
        # Check semantic checks pass
        for check in REMEDIATE_GATE.semantic_checks:
            assert check.check_fn(tasklist), f"Semantic check '{check.name}' failed"

    def test_stub_tasklist_passes_semantic_checks(self):
        stub = generate_stub_tasklist("report.md", "content")
        for check in REMEDIATE_GATE.semantic_checks:
            assert check.check_fn(stub), f"Semantic check '{check.name}' failed on stub"

    def test_pre_execution_tasklist_fails_status_check(self):
        """Pre-execution tasklist (PENDING status) should fail status check."""
        tasklist = generate_remediation_tasklist(
            [_make_finding("F-01", "BLOCKING", status="PENDING")],
            "report.md",
            "content",
        )
        status_check = next(
            c for c in REMEDIATE_GATE.semantic_checks
            if c.name == "all_actionable_have_status"
        )
        assert status_check.check_fn(tasklist) is False
