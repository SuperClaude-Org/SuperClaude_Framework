"""Tests for analyze-workflow step (Step 3).

Covers:
- Happy path: mock subprocess produces valid output, SC-003 gate passes
- Missing component inventory: fail-fast with MISSING_ARTIFACT
- Subprocess timeout: returns TIMEOUT status
- Subprocess failure: returns FAIL status
- Gate failure: returns FAIL with GATE_FAILURE classification
- Uses mock harness for all Claude subprocess calls
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
)
from superclaude.cli.cli_portify.steps.analyze_workflow import run_analyze_workflow
from tests.cli_portify.fixtures.mock_harness import (
    ANALYZE_WORKFLOW_GOOD,
    MALFORMED_FRONTMATTER,
    patch_portify_process,
)


@pytest.fixture
def workflow_dir(tmp_path: Path) -> Path:
    """Create a minimal workflow directory."""
    wf = tmp_path / "sc-test-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Test Skill\n\nContent.\n")
    return wf


@pytest.fixture
def config_with_inventory(workflow_dir: Path, tmp_path: Path):
    """Create config with a pre-populated component inventory."""
    output = tmp_path / "output"
    output.mkdir()
    results = output / "results"
    results.mkdir()

    # Write a component inventory (Step 2 output)
    (results / "component-inventory.md").write_text(
        "---\nsource_skill: sc-test-protocol\ncomponent_count: 1\n"
        "total_lines: 3\n---\n\n# Component Inventory\n\n## skill\n\n"
        "| Name | Lines | Path |\n|------|-------|------|\n"
        "| SKILL.md | 3 | /path/to/SKILL.md |\n"
    )

    config = load_portify_config(
        workflow_path=str(workflow_dir),
        output_dir=str(output),
    )
    return config


class TestAnalyzeWorkflowHappyPath:
    """Test successful analyze-workflow execution."""

    def test_produces_pass_result(self, config_with_inventory):
        with patch_portify_process("analyze-workflow"):
            result = run_analyze_workflow(config_with_inventory)

        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "analyze-workflow"
        assert result.step_number == 3
        assert result.phase == 2
        assert result.gate_tier == "STRICT"

    def test_produces_artifact(self, config_with_inventory):
        with patch_portify_process("analyze-workflow"):
            result = run_analyze_workflow(config_with_inventory)

        artifact = Path(result.artifact_path)
        assert artifact.exists()
        content = artifact.read_text()
        assert "## Workflow Summary" in content
        assert "## Component Analysis" in content

    def test_gate_passes(self, config_with_inventory):
        with patch_portify_process("analyze-workflow"):
            result = run_analyze_workflow(config_with_inventory)

        assert result.portify_status == PortifyStatus.PASS
        assert result.failure_classification is None


class TestAnalyzeWorkflowFailures:
    """Test failure paths for analyze-workflow."""

    def test_missing_inventory_fails(self, workflow_dir, tmp_path):
        """Missing component inventory should fail-fast."""
        output = tmp_path / "empty-output"
        output.mkdir()
        (output / "results").mkdir()
        # No component-inventory.md

        config = load_portify_config(
            workflow_path=str(workflow_dir),
            output_dir=str(output),
        )
        result = run_analyze_workflow(config)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_subprocess_timeout(self, config_with_inventory):
        """Subprocess timeout should return TIMEOUT."""
        with patch_portify_process(
            "analyze-workflow", exit_code=124, timed_out=True
        ):
            result = run_analyze_workflow(config_with_inventory)

        assert result.portify_status == PortifyStatus.TIMEOUT
        assert result.failure_classification == FailureClassification.TIMEOUT

    def test_subprocess_failure(self, config_with_inventory):
        """Non-zero exit code should return FAIL."""
        with patch_portify_process("analyze-workflow", exit_code=1):
            result = run_analyze_workflow(config_with_inventory)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.GATE_FAILURE

    def test_gate_failure_malformed(self, config_with_inventory):
        """Malformed output should fail SC-003 gate."""
        with patch_portify_process(
            "analyze-workflow", fixture_override=MALFORMED_FRONTMATTER
        ):
            result = run_analyze_workflow(config_with_inventory)

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.GATE_FAILURE
