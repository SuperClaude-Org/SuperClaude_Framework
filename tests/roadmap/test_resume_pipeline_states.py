"""Tests for resume from all pipeline states (T06.04).

Covers 4 resume scenarios:
1. Post-validate resume -> skips to remediate
2. Post-remediate resume with valid hash -> skips to certify
3. Post-remediate resume with stale hash -> re-runs remediate
4. Post-certify resume -> no-op
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from superclaude.cli.pipeline.models import GateCriteria, Step
from superclaude.cli.roadmap.executor import (
    _check_tasklist_hash_current,
    check_certify_resume,
    check_remediate_resume,
    derive_pipeline_status,
    read_state,
    write_state,
)
from superclaude.cli.roadmap.models import AgentSpec, RoadmapConfig


def _make_config(tmp_path: Path) -> RoadmapConfig:
    spec = tmp_path / "spec.md"
    spec.write_text("# Test Spec\n")
    output = tmp_path / "output"
    output.mkdir(exist_ok=True)
    return RoadmapConfig(
        spec_file=spec,
        output_dir=output,
        agents=[AgentSpec("opus", "architect")],
    )


def _make_valid_tasklist(report_content: str, source_report: str) -> str:
    """Create a valid remediation tasklist with correct hash."""
    source_hash = hashlib.sha256(report_content.encode("utf-8")).hexdigest()
    return (
        "---\n"
        "type: remediation-tasklist\n"
        f"source_report: {source_report}\n"
        f"source_report_hash: {source_hash}\n"
        "generated: 2026-03-10T00:00:00Z\n"
        "total_findings: 2\n"
        "actionable: 1\n"
        "skipped: 1\n"
        "---\n"
        "\n"
        "# Remediation Tasklist\n"
        "\n"
        "## BLOCKING\n"
        "\n"
        "- [x] F-01 | roadmap.md | FIXED -- Missing milestone\n"
        "\n"
        "## SKIPPED\n"
        "\n"
        "- [x] F-02 | extraction.md | SKIPPED -- Info only\n"
        "\n"
    )


def _make_valid_certification_report() -> str:
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


# ═══════════════════════════════════════════════════════════════
# Scenario 1: Post-validate resume -> remediate should run
# ═══════════════════════════════════════════════════════════════


class TestPostValidateResume:
    """Resume from post-validate: no remediate output -> skip to remediate."""

    def test_no_tasklist_means_remediate_needed(self, tmp_path):
        config = _make_config(tmp_path)
        gate_fn = MagicMock(return_value=(True, None))

        result = check_remediate_resume(config, gate_fn)
        assert result is False  # No tasklist -> must run remediate

    def test_pipeline_status_validated_with_issues(self):
        state = {"validation": {"status": "fail"}}
        assert derive_pipeline_status(state) == "validated-with-issues"

    def test_pipeline_status_validated(self):
        state = {"validation": {"status": "pass"}}
        assert derive_pipeline_status(state) == "validated"


# ═══════════════════════════════════════════════════════════════
# Scenario 2: Post-remediate resume with valid hash -> skip to certify
# ═══════════════════════════════════════════════════════════════


class TestPostRemediateResumeValidHash:
    """Resume from post-remediate with matching hash: skip remediate, run certify."""

    def test_valid_hash_skips_remediate(self, tmp_path):
        config = _make_config(tmp_path)
        out = config.output_dir

        # Create validation report
        report_content = "# Validation Report\nSome findings.\n"
        report_path = out / "reflect-merged.md"
        report_path.write_text(report_content)

        # Create tasklist with matching hash
        tasklist_content = _make_valid_tasklist(report_content, str(report_path))
        tasklist_path = out / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        def gate_fn(output_file, criteria):
            return (True, None)

        result = check_remediate_resume(config, gate_fn)
        assert result is True  # Hash matches -> skip remediate

    def test_no_certification_means_certify_needed(self, tmp_path):
        config = _make_config(tmp_path)
        gate_fn = MagicMock(return_value=(True, None))

        result = check_certify_resume(config, gate_fn)
        assert result is False  # No report -> must run certify

    def test_pipeline_status_remediated(self):
        state = {"remediate": {"status": "PASS"}}
        assert derive_pipeline_status(state) == "remediated"


# ═══════════════════════════════════════════════════════════════
# Scenario 3: Post-remediate resume with stale hash -> re-run remediate
# ═══════════════════════════════════════════════════════════════


class TestPostRemediateResumeStaleHash:
    """Resume from post-remediate with hash mismatch: re-run remediate."""

    def test_stale_hash_triggers_rerun(self, tmp_path):
        config = _make_config(tmp_path)
        out = config.output_dir

        # Create validation report (current)
        report_path = out / "reflect-merged.md"
        report_path.write_text("# Updated Report\nDifferent content.\n")

        # Create tasklist with OLD hash (stale)
        old_content = "# Old Report\nOriginal content.\n"
        tasklist_content = _make_valid_tasklist(old_content, str(report_path))
        tasklist_path = out / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        def gate_fn(output_file, criteria):
            return (True, None)

        result = check_remediate_resume(config, gate_fn)
        assert result is False  # Hash mismatch -> must re-run

    def test_hash_check_missing_report_fails_closed(self, tmp_path):
        config = _make_config(tmp_path)
        out = config.output_dir

        # Create tasklist referencing non-existent report
        tasklist_content = (
            "---\n"
            "type: remediation-tasklist\n"
            "source_report: nonexistent-report.md\n"
            "source_report_hash: abc123\n"
            "generated: 2026-03-10T00:00:00Z\n"
            "total_findings: 1\n"
            "actionable: 1\n"
            "skipped: 0\n"
            "---\n"
            "\n"
            "# Tasklist\n"
            "\n"
        )
        (out / "remediation-tasklist.md").write_text(tasklist_content)

        def gate_fn(output_file, criteria):
            return (True, None)

        result = check_remediate_resume(config, gate_fn)
        assert result is False  # Missing report -> fail closed

    def test_hash_check_missing_frontmatter_fails_closed(self, tmp_path):
        config = _make_config(tmp_path)
        out = config.output_dir

        # Create tasklist without frontmatter
        (out / "remediation-tasklist.md").write_text("# No frontmatter\nContent\n")

        def gate_fn(output_file, criteria):
            return (True, None)

        result = check_remediate_resume(config, gate_fn)
        # Gate check will fail since no frontmatter
        assert result is False


# ═══════════════════════════════════════════════════════════════
# Scenario 4: Post-certify resume -> no-op
# ═══════════════════════════════════════════════════════════════


class TestPostCertifyResume:
    """Resume from post-certify: both steps complete -> no-op."""

    def test_both_steps_skip(self, tmp_path):
        config = _make_config(tmp_path)
        out = config.output_dir

        # Create validation report
        report_content = "# Report\nFindings.\n"
        report_path = out / "reflect-merged.md"
        report_path.write_text(report_content)

        # Create tasklist with valid hash
        tasklist_content = _make_valid_tasklist(report_content, str(report_path))
        (out / "remediation-tasklist.md").write_text(tasklist_content)

        # Create valid certification report
        cert_content = _make_valid_certification_report()
        (out / "certification-report.md").write_text(cert_content)

        def gate_fn(output_file, criteria):
            return (True, None)

        # Both should skip
        assert check_remediate_resume(config, gate_fn) is True
        assert check_certify_resume(config, gate_fn) is True

    def test_pipeline_status_certified(self):
        state = {"certify": {"certified": True, "status": "certified"}}
        assert derive_pipeline_status(state) == "certified"

    def test_pipeline_status_certified_with_caveats(self):
        state = {"certify": {"certified": False, "status": "certified-with-caveats"}}
        assert derive_pipeline_status(state) == "certified-with-caveats"


# ═══════════════════════════════════════════════════════════════
# Hash detection unit tests
# ═══════════════════════════════════════════════════════════════


class TestCheckTasklistHashCurrent:
    """Unit tests for _check_tasklist_hash_current()."""

    def test_matching_hash_returns_true(self, tmp_path):
        report_content = "# Report\nContent.\n"
        report_path = tmp_path / "reflect-merged.md"
        report_path.write_text(report_content)

        tasklist_content = _make_valid_tasklist(report_content, str(report_path))
        tasklist_path = tmp_path / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        assert _check_tasklist_hash_current(tasklist_path, tmp_path) is True

    def test_mismatched_hash_returns_false(self, tmp_path):
        # Hash computed from old content
        old_content = "# Old Report\n"
        report_path = tmp_path / "reflect-merged.md"
        report_path.write_text("# New Report\nChanged.\n")

        tasklist_content = _make_valid_tasklist(old_content, str(report_path))
        tasklist_path = tmp_path / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        assert _check_tasklist_hash_current(tasklist_path, tmp_path) is False

    def test_missing_report_returns_false(self, tmp_path):
        tasklist_content = (
            "---\n"
            "source_report: missing.md\n"
            "source_report_hash: abc123\n"
            "---\n"
            "\n"
            "# Tasklist\n"
        )
        tasklist_path = tmp_path / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        assert _check_tasklist_hash_current(tasklist_path, tmp_path) is False

    def test_no_frontmatter_returns_false(self, tmp_path):
        tasklist_path = tmp_path / "remediation-tasklist.md"
        tasklist_path.write_text("No frontmatter here.\n")

        assert _check_tasklist_hash_current(tasklist_path, tmp_path) is False

    def test_empty_hash_returns_false(self, tmp_path):
        tasklist_content = (
            "---\n"
            "source_report: report.md\n"
            "source_report_hash:\n"
            "---\n"
        )
        tasklist_path = tmp_path / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        # Empty hash should fail closed
        assert _check_tasklist_hash_current(tasklist_path, tmp_path) is False

    def test_default_report_path_fallback(self, tmp_path):
        """When source_report is empty, falls back to reflect-merged.md."""
        report_content = "# Report\n"
        (tmp_path / "reflect-merged.md").write_text(report_content)

        source_hash = hashlib.sha256(report_content.encode("utf-8")).hexdigest()
        tasklist_content = (
            "---\n"
            "source_report:\n"
            f"source_report_hash: {source_hash}\n"
            "---\n"
            "\n"
            "# Tasklist\n"
        )
        tasklist_path = tmp_path / "remediation-tasklist.md"
        tasklist_path.write_text(tasklist_content)

        # source_report is empty/blank -> falls back, but _parse_frontmatter
        # will see "source_report:" as empty -> fail on "not saved_hash" check
        # Actually the hash field is non-empty, so it falls through to default path
        assert _check_tasklist_hash_current(tasklist_path, tmp_path) is True


# ═══════════════════════════════════════════════════════════════
# Pipeline status derivation tests
# ═══════════════════════════════════════════════════════════════


class TestDerivePipelineStatus:
    """Tests for derive_pipeline_status() state transitions."""

    def test_pending_when_no_data(self):
        assert derive_pipeline_status({}) == "pending"

    def test_validated_on_pass(self):
        assert derive_pipeline_status({"validation": {"status": "pass"}}) == "validated"

    def test_validated_with_issues_on_fail(self):
        assert derive_pipeline_status({"validation": {"status": "fail"}}) == "validated-with-issues"

    def test_remediated_overrides_validation(self):
        state = {
            "validation": {"status": "fail"},
            "remediate": {"status": "PASS"},
        }
        assert derive_pipeline_status(state) == "remediated"

    def test_certified_overrides_remediate(self):
        state = {
            "validation": {"status": "fail"},
            "remediate": {"status": "PASS"},
            "certify": {"certified": True},
        }
        assert derive_pipeline_status(state) == "certified"

    def test_certified_with_caveats(self):
        state = {
            "remediate": {"status": "PASS"},
            "certify": {"certified": False},
        }
        assert derive_pipeline_status(state) == "certified-with-caveats"

    def test_transitions_are_ordered(self):
        """Verify the transition priority: certify > remediate > validation."""
        # Each additional entry moves pipeline forward
        s1 = derive_pipeline_status({})
        s2 = derive_pipeline_status({"validation": {"status": "pass"}})
        s3 = derive_pipeline_status({"validation": {"status": "pass"}, "remediate": {"status": "PASS"}})
        s4 = derive_pipeline_status({
            "validation": {"status": "pass"},
            "remediate": {"status": "PASS"},
            "certify": {"certified": True},
        })

        assert s1 == "pending"
        assert s2 == "validated"
        assert s3 == "remediated"
        assert s4 == "certified"
