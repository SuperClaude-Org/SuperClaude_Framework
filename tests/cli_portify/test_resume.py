"""Tests for resume semantics with resumability matrix.

Tests resume command generation for Steps 5-7 and verifies
non-resumable steps (1-4) do not generate resume commands.

Per D-0037, D-0038 (SC-014), D-0052.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
    PortifyStepResult,
)
from superclaude.cli.cli_portify.resume import (
    RESUMABILITY_MATRIX,
    TOTAL_STEPS,
    build_resume_command,
    build_resume_context,
    get_entry_requirements,
    get_preserved_context,
    is_resumable,
    suggest_budget,
    validate_resume_entry,
)


class TestResumabilityMatrix:
    """Tests for the resumability matrix data structure."""

    def test_matrix_has_all_7_steps(self):
        assert len(RESUMABILITY_MATRIX) == 7

    def test_total_steps_is_7(self):
        assert TOTAL_STEPS == 7

    def test_steps_1_4_not_resumable(self):
        non_resumable = [
            "validate-config",
            "discover-components",
            "analyze-workflow",
            "design-pipeline",
        ]
        for step in non_resumable:
            assert RESUMABILITY_MATRIX[step].resumable is False

    def test_steps_5_7_resumable(self):
        resumable = ["synthesize-spec", "brainstorm-gaps", "panel-review"]
        for step in resumable:
            assert RESUMABILITY_MATRIX[step].resumable is True

    def test_step_numbers_are_sequential(self):
        expected = {
            "validate-config": 1,
            "discover-components": 2,
            "analyze-workflow": 3,
            "design-pipeline": 4,
            "synthesize-spec": 5,
            "brainstorm-gaps": 6,
            "panel-review": 7,
        }
        for step_name, expected_num in expected.items():
            assert RESUMABILITY_MATRIX[step_name].step_number == expected_num

    def test_brainstorm_gaps_preserves_focus_findings(self):
        entry = RESUMABILITY_MATRIX["brainstorm-gaps"]
        assert "focus-findings.md" in entry.preserved_context

    def test_panel_review_preserves_focus_findings(self):
        entry = RESUMABILITY_MATRIX["panel-review"]
        assert "focus-findings.md" in entry.preserved_context

    def test_synthesize_spec_entry_requirements(self):
        entry = RESUMABILITY_MATRIX["synthesize-spec"]
        assert "portify-analysis.md" in entry.required_artifacts
        assert "portify-spec.md" in entry.required_artifacts

    def test_brainstorm_gaps_entry_requirements(self):
        entry = RESUMABILITY_MATRIX["brainstorm-gaps"]
        assert "synthesized-spec.md" in entry.required_artifacts

    def test_panel_review_entry_requirements(self):
        entry = RESUMABILITY_MATRIX["panel-review"]
        assert "synthesized-spec.md" in entry.required_artifacts
        assert "brainstorm-gaps.md" in entry.required_artifacts


class TestIsResumable:
    """Tests for is_resumable function."""

    def test_resumable_steps(self):
        assert is_resumable("synthesize-spec") is True
        assert is_resumable("brainstorm-gaps") is True
        assert is_resumable("panel-review") is True

    def test_non_resumable_steps(self):
        assert is_resumable("validate-config") is False
        assert is_resumable("discover-components") is False
        assert is_resumable("analyze-workflow") is False
        assert is_resumable("design-pipeline") is False

    def test_unknown_step(self):
        assert is_resumable("nonexistent") is False


class TestGetEntryRequirements:
    """Tests for entry requirement lookups."""

    def test_synthesize_spec_requirements(self):
        reqs = get_entry_requirements("synthesize-spec")
        assert len(reqs) >= 2

    def test_unknown_step_returns_empty(self):
        assert get_entry_requirements("nonexistent") == ()


class TestGetPreservedContext:
    """Tests for preserved context lookups."""

    def test_brainstorm_gaps_preserves_focus_findings(self):
        ctx = get_preserved_context("brainstorm-gaps")
        assert "focus-findings.md" in ctx

    def test_panel_review_preserves_focus_findings(self):
        ctx = get_preserved_context("panel-review")
        assert "focus-findings.md" in ctx

    def test_non_resumable_step_returns_empty(self):
        assert get_preserved_context("validate-config") == ()


class TestSuggestBudget:
    """Tests for budget suggestion."""

    def test_resumable_step_returns_budget(self):
        budget = suggest_budget("synthesize-spec", max_convergence=3)
        assert budget is not None
        assert budget > 0

    def test_non_resumable_step_returns_none(self):
        assert suggest_budget("validate-config") is None

    def test_custom_max_convergence(self):
        budget = suggest_budget("panel-review", max_convergence=5)
        assert budget == 5


class TestBuildResumeCommand:
    """Tests for resume command generation (SC-014)."""

    def test_resumable_step_generates_command(self):
        cmd = build_resume_command("synthesize-spec", "/path/to/workflow")
        assert "--start synthesize-spec" in cmd
        assert "superclaude cli-portify run" in cmd

    def test_command_includes_workflow_path(self):
        cmd = build_resume_command("brainstorm-gaps", "/my/workflow")
        assert "/my/workflow" in cmd

    def test_command_includes_budget(self):
        cmd = build_resume_command("panel-review", max_convergence=5)
        assert "--max-convergence 5" in cmd

    def test_non_resumable_step_returns_empty(self):
        assert build_resume_command("validate-config") == ""
        assert build_resume_command("discover-components") == ""
        assert build_resume_command("analyze-workflow") == ""
        assert build_resume_command("design-pipeline") == ""

    def test_step_6_generates_command(self):
        cmd = build_resume_command("brainstorm-gaps")
        assert "--start brainstorm-gaps" in cmd
        assert cmd != ""

    def test_step_7_generates_command(self):
        cmd = build_resume_command("panel-review")
        assert "--start panel-review" in cmd
        assert cmd != ""


class TestValidateResumeEntry:
    """Tests for resume entry validation."""

    def test_valid_entry_with_all_artifacts(self, tmp_path):
        # Create required artifacts for brainstorm-gaps
        (tmp_path / "synthesized-spec.md").write_text("content")
        (tmp_path / "focus-findings.md").write_text("content")

        valid, missing, preserved = validate_resume_entry("brainstorm-gaps", tmp_path)
        assert valid is True
        assert missing == []
        assert len(preserved) >= 1

    def test_missing_required_artifact(self, tmp_path):
        # brainstorm-gaps requires synthesized-spec.md
        valid, missing, preserved = validate_resume_entry("brainstorm-gaps", tmp_path)
        assert valid is False
        assert "synthesized-spec.md" in missing

    def test_non_resumable_step_fails_validation(self, tmp_path):
        valid, missing, preserved = validate_resume_entry("validate-config", tmp_path)
        assert valid is False
        assert "not resumable" in missing[0]

    def test_unknown_step_fails_validation(self, tmp_path):
        valid, missing, preserved = validate_resume_entry("nonexistent", tmp_path)
        assert valid is False
        assert "Unknown step" in missing[0]

    def test_panel_review_with_all_artifacts(self, tmp_path):
        (tmp_path / "synthesized-spec.md").write_text("content")
        (tmp_path / "brainstorm-gaps.md").write_text("content")
        (tmp_path / "focus-findings.md").write_text("context")

        valid, missing, preserved = validate_resume_entry("panel-review", tmp_path)
        assert valid is True
        assert missing == []
        # focus-findings.md should be in preserved list
        preserved_names = [Path(p).name for p in preserved]
        assert "focus-findings.md" in preserved_names

    def test_partial_artifacts_reports_missing(self, tmp_path):
        # panel-review needs both synthesized-spec.md and brainstorm-gaps.md
        (tmp_path / "synthesized-spec.md").write_text("content")
        # brainstorm-gaps.md is missing

        valid, missing, preserved = validate_resume_entry("panel-review", tmp_path)
        assert valid is False
        assert "brainstorm-gaps.md" in missing


class TestBuildResumeContext:
    """Tests for resume context construction."""

    def test_builds_context_for_failed_step(self, tmp_path):
        (tmp_path / "synthesized-spec.md").write_text("content")

        result = PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="brainstorm-gaps",
            step_number=6,
            phase=4,
            failure_classification=FailureClassification.TIMEOUT,
        )

        ctx = build_resume_context(result, tmp_path, max_convergence=3)
        assert ctx.failed_step == "brainstorm-gaps"
        assert ctx.failed_step_number == 6
        assert ctx.last_completed_step == "synthesize-spec"
        assert ctx.last_completed_step_number == 5
        assert ctx.failure_classification == FailureClassification.TIMEOUT
        assert ctx.re_run_required is True
        assert ctx.resume_command != ""
        assert "--start brainstorm-gaps" in ctx.resume_command

    def test_non_resumable_step_has_empty_command(self, tmp_path):
        result = PortifyStepResult(
            portify_status=PortifyStatus.FAIL,
            step_name="validate-config",
            step_number=1,
            phase=1,
            failure_classification=FailureClassification.GATE_FAILURE,
        )

        ctx = build_resume_context(result, tmp_path)
        assert ctx.resume_command == ""
        assert ctx.failed_step == "validate-config"

    def test_preserves_artifacts_list(self, tmp_path):
        (tmp_path / "synthesized-spec.md").write_text("spec")
        (tmp_path / "brainstorm-gaps.md").write_text("gaps")
        (tmp_path / "focus-findings.md").write_text("findings")

        result = PortifyStepResult(
            portify_status=PortifyStatus.TIMEOUT,
            step_name="panel-review",
            step_number=7,
            phase=4,
            failure_classification=FailureClassification.TIMEOUT,
        )

        ctx = build_resume_context(result, tmp_path, max_convergence=3)
        preserved_names = [Path(p).name for p in ctx.artifacts_preserved]
        assert "focus-findings.md" in preserved_names
        assert "synthesized-spec.md" in preserved_names
