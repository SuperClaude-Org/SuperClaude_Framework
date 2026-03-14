"""Tests for Claude subprocess mock harness.

Covers:
- Mock harness returns known-good outputs for all 5 step types
- Mock outputs pass their respective gate checks
- Edge case fixtures for partial, malformed frontmatter, and timeout
- Harness integrates with PortifyProcess
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.process import PortifyProcess, ProcessResult
from superclaude.cli.cli_portify.utils import parse_frontmatter
from tests.cli_portify.fixtures.mock_harness import (
    EDGE_CASE_FIXTURES,
    STEP_FIXTURES,
    get_edge_case,
    get_fixture,
    mock_process_run,
    patch_portify_process,
)


class TestStepFixtures:
    """Mock harness returns known-good outputs for all 5 step types."""

    STEP_NAMES = [
        "analyze-workflow",
        "design-pipeline",
        "synthesize-spec",
        "brainstorm-gaps",
        "panel-review",
    ]

    @pytest.mark.parametrize("step_name", STEP_NAMES)
    def test_fixture_exists(self, step_name):
        content = get_fixture(step_name)
        assert len(content) > 0

    @pytest.mark.parametrize("step_name", STEP_NAMES)
    def test_fixture_has_frontmatter(self, step_name):
        content = get_fixture(step_name)
        fm, body = parse_frontmatter(content)
        assert fm, f"No frontmatter in {step_name} fixture"
        assert fm.get("step") == step_name

    @pytest.mark.parametrize("step_name", STEP_NAMES)
    def test_fixture_has_sections(self, step_name):
        content = get_fixture(step_name)
        assert "## " in content, f"No sections in {step_name} fixture"

    def test_registry_has_five_entries(self):
        assert len(STEP_FIXTURES) == 5

    def test_unknown_step_raises(self):
        with pytest.raises(KeyError, match="No fixture"):
            get_fixture("nonexistent-step")


class TestFixtureGateCompatibility:
    """Mock outputs pass their respective gate checks."""

    def test_analyze_workflow_has_required_sections(self):
        content = get_fixture("analyze-workflow")
        required = [
            "## Workflow Summary",
            "## Component Analysis",
            "## Data Flow",
            "## Complexity Assessment",
            "## Recommendations",
        ]
        for section in required:
            assert section in content

    def test_analyze_workflow_frontmatter_fields(self):
        fm, _ = parse_frontmatter(get_fixture("analyze-workflow"))
        for field in ["step", "source_skill", "cli_name", "component_count", "analysis_sections"]:
            assert field in fm

    def test_design_pipeline_frontmatter_fields(self):
        fm, _ = parse_frontmatter(get_fixture("design-pipeline"))
        for field in ["step", "source_skill", "cli_name", "pipeline_steps", "gate_count"]:
            assert field in fm

    def test_synthesize_spec_zero_placeholders(self):
        content = get_fixture("synthesize-spec")
        fm, _ = parse_frontmatter(content)
        assert fm.get("placeholder_count") == 0
        assert "{{SC_PLACEHOLDER:" not in content

    def test_brainstorm_gaps_frontmatter_fields(self):
        fm, _ = parse_frontmatter(get_fixture("brainstorm-gaps"))
        for field in ["step", "source_skill", "cli_name", "gaps_found", "severity_high"]:
            assert field in fm

    def test_panel_review_convergence_state(self):
        fm, _ = parse_frontmatter(get_fixture("panel-review"))
        assert fm.get("convergence_state") == "converged"
        assert fm.get("iteration") == 1


class TestEdgeCaseFixtures:
    """Edge case fixtures for partial, malformed frontmatter, and timeout."""

    def test_partial_has_placeholders(self):
        content = get_edge_case("partial")
        assert "{{SC_PLACEHOLDER:" in content

    def test_partial_has_frontmatter_with_nonzero_count(self):
        fm, _ = parse_frontmatter(get_edge_case("partial"))
        assert fm.get("placeholder_count") == 2

    def test_malformed_has_no_frontmatter(self):
        content = get_edge_case("malformed_frontmatter")
        fm, _ = parse_frontmatter(content)
        assert not fm

    def test_timeout_is_empty(self):
        content = get_edge_case("timeout")
        assert content == ""

    def test_three_edge_cases_exist(self):
        assert len(EDGE_CASE_FIXTURES) == 3

    def test_unknown_edge_case_raises(self):
        with pytest.raises(KeyError, match="No edge case"):
            get_edge_case("nonexistent")


class TestMockHarnessIntegration:
    """Harness integrates with PortifyProcess to intercept subprocess calls."""

    def test_patch_portify_process_returns_fixture(self, tmp_path):
        out = tmp_path / "out.md"
        err = tmp_path / "err.log"
        proc = PortifyProcess(
            prompt="test",
            output_file=out,
            error_file=err,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )

        with patch_portify_process("analyze-workflow"):
            result = proc.run()

        assert result.succeeded is True
        assert result.exit_code == 0
        assert "Workflow Summary" in result.stdout_text

    def test_patch_with_timeout(self, tmp_path):
        out = tmp_path / "out.md"
        err = tmp_path / "err.log"
        proc = PortifyProcess(
            prompt="test",
            output_file=out,
            error_file=err,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )

        with patch_portify_process("analyze-workflow", exit_code=124, timed_out=True):
            result = proc.run()

        assert result.timed_out is True
        assert result.succeeded is False

    def test_patch_with_edge_case(self, tmp_path):
        out = tmp_path / "out.md"
        err = tmp_path / "err.log"
        proc = PortifyProcess(
            prompt="test",
            output_file=out,
            error_file=err,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )

        partial = get_edge_case("partial")
        with patch_portify_process("synthesize-spec", fixture_override=partial):
            result = proc.run()

        assert result.succeeded is True
        assert "{{SC_PLACEHOLDER:" in result.stdout_text

    def test_output_file_written(self, tmp_path):
        out = tmp_path / "results" / "out.md"
        err = tmp_path / "err.log"
        proc = PortifyProcess(
            prompt="test",
            output_file=out,
            error_file=err,
            work_dir=tmp_path,
            workflow_path=tmp_path,
        )

        with patch_portify_process("design-pipeline"):
            result = proc.run()

        assert out.exists()
        content = out.read_text()
        assert "Pipeline Overview" in content
