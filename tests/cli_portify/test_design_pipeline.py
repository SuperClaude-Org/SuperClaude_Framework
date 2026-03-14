"""Tests for design-pipeline step (Step 4).

Covers:
- Happy path: mock subprocess + gate passes
- Dry-run halt: emits dry_run contract with phases 3-4 skipped (SC-011)
- Review gate: y/n response handling, USER_REJECTED on n
- Subprocess timeout/failure
- Gate failure
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
)
from superclaude.cli.cli_portify.steps.design_pipeline import run_design_pipeline
from tests.cli_portify.fixtures.mock_harness import (
    DESIGN_PIPELINE_GOOD,
    MALFORMED_FRONTMATTER,
    patch_portify_process,
)


@pytest.fixture
def workflow_dir(tmp_path: Path) -> Path:
    wf = tmp_path / "sc-test-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Test Skill\n\nContent.\n")
    return wf


@pytest.fixture
def config_with_analysis(workflow_dir: Path, tmp_path: Path):
    """Config with prior analysis artifact."""
    output = tmp_path / "output"
    output.mkdir()
    results = output / "results"
    results.mkdir()

    # Write component inventory and analysis (Steps 2-3 outputs)
    (results / "component-inventory.md").write_text(
        "---\nsource_skill: sc-test-protocol\ncomponent_count: 1\n---\n\n"
        "# Component Inventory\n"
    )
    from tests.cli_portify.fixtures.mock_harness import ANALYZE_WORKFLOW_GOOD

    (results / "portify-analysis.md").write_text(ANALYZE_WORKFLOW_GOOD)

    config = load_portify_config(
        workflow_path=str(workflow_dir),
        output_dir=str(output),
    )
    return config


class TestDesignPipelineHappyPath:

    def test_produces_pass_result(self, config_with_analysis):
        config_with_analysis.skip_review = True
        with patch_portify_process("design-pipeline"):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "design-pipeline"
        assert result.step_number == 4
        assert result.gate_tier == "STRICT"

    def test_produces_artifact(self, config_with_analysis):
        config_with_analysis.skip_review = True
        with patch_portify_process("design-pipeline"):
            result = run_design_pipeline(config_with_analysis)

        artifact = Path(result.artifact_path)
        assert artifact.exists()
        content = artifact.read_text()
        assert "## Pipeline Overview" in content


class TestDesignPipelineDryRun:
    """Test --dry-run halt logic (SC-011)."""

    def test_dry_run_emits_contract(self, config_with_analysis, capsys):
        config_with_analysis.dry_run = True
        config_with_analysis.skip_review = True
        with patch_portify_process("design-pipeline"):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.SKIPPED

        captured = capsys.readouterr()
        contract = json.loads(captured.out)
        assert contract["status"] == "dry_run"

    def test_dry_run_marks_phases_skipped(self, config_with_analysis, capsys):
        config_with_analysis.dry_run = True
        config_with_analysis.skip_review = True
        with patch_portify_process("design-pipeline"):
            run_design_pipeline(config_with_analysis)

        captured = capsys.readouterr()
        contract = json.loads(captured.out)
        # Phases 3-4 should be marked skipped
        phases = contract["phases"]
        for p in phases[2:]:
            assert p["status"] == "skipped"


class TestDesignPipelineReviewGate:
    """Test user review gate (y/n on stderr)."""

    def test_review_accept(self, config_with_analysis):
        config_with_analysis.skip_review = False
        with (
            patch_portify_process("design-pipeline"),
            patch("builtins.input", return_value="y"),
        ):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.PASS
        assert result.review_required is True
        assert result.review_accepted is True

    def test_review_reject(self, config_with_analysis):
        config_with_analysis.skip_review = False
        with (
            patch_portify_process("design-pipeline"),
            patch("builtins.input", return_value="n"),
        ):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.review_accepted is False
        assert result.failure_classification == FailureClassification.USER_REJECTION


class TestDesignPipelineFailures:

    def test_missing_analysis_fails(self, workflow_dir, tmp_path):
        output = tmp_path / "empty-output"
        output.mkdir()
        (output / "results").mkdir()

        config = load_portify_config(
            workflow_path=str(workflow_dir),
            output_dir=str(output),
        )
        config.skip_review = True
        result = run_design_pipeline(config)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_subprocess_timeout(self, config_with_analysis):
        config_with_analysis.skip_review = True
        with patch_portify_process("design-pipeline", exit_code=124, timed_out=True):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.TIMEOUT

    def test_gate_failure(self, config_with_analysis):
        config_with_analysis.skip_review = True
        with patch_portify_process(
            "design-pipeline", fixture_override=MALFORMED_FRONTMATTER
        ):
            result = run_design_pipeline(config_with_analysis)

        assert result.portify_status == PortifyStatus.FAIL
