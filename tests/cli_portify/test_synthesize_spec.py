"""Tests for synthesize-spec step (Step 5).

Covers:
- Happy path: mock subprocess produces clean output, SC-005 gate passes
- Sentinel scan: detects remaining {{SC_PLACEHOLDER:*}} sentinels
- Retry logic: retries with specific placeholder names on sentinel failure
- Template missing: fail-fast with clear error
- Missing prior artifacts: fail-fast
- Subprocess timeout/failure
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, call

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.models import (
    FailureClassification,
    PortifyStatus,
)
from superclaude.cli.cli_portify.steps.synthesize_spec import (
    run_synthesize_spec,
    scan_sentinels,
)
from tests.cli_portify.fixtures.mock_harness import (
    SYNTHESIZE_SPEC_GOOD,
    PARTIAL_OUTPUT,
    MALFORMED_FRONTMATTER,
    patch_portify_process,
)


@pytest.fixture
def workflow_dir(tmp_path: Path) -> Path:
    wf = tmp_path / "sc-test-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Test Skill\n\nContent.\n")
    (wf / "release-spec-template.md").write_text(
        "---\ntemplate: true\n---\n\n# Release Spec Template\n\n"
        "{{SC_PLACEHOLDER:content}}\n"
    )
    return wf


@pytest.fixture
def config_with_prior_artifacts(workflow_dir: Path, tmp_path: Path):
    """Config with all prior artifacts (Steps 2-4)."""
    output = tmp_path / "output"
    output.mkdir()
    results = output / "results"
    results.mkdir()

    from tests.cli_portify.fixtures.mock_harness import (
        ANALYZE_WORKFLOW_GOOD,
        DESIGN_PIPELINE_GOOD,
    )

    (results / "component-inventory.md").write_text(
        "---\nsource_skill: sc-test-protocol\ncomponent_count: 1\n---\n\n"
        "# Component Inventory\n"
    )
    (results / "portify-analysis.md").write_text(ANALYZE_WORKFLOW_GOOD)
    (results / "portify-spec.md").write_text(DESIGN_PIPELINE_GOOD)

    config = load_portify_config(
        workflow_path=str(workflow_dir),
        output_dir=str(output),
    )
    return config


class TestSynthesizeSpecHappyPath:

    def test_produces_pass_result(self, config_with_prior_artifacts, workflow_dir):
        with patch_portify_process("synthesize-spec"):
            result = run_synthesize_spec(
                config_with_prior_artifacts,
                template_path=workflow_dir / "release-spec-template.md",
            )

        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "synthesize-spec"
        assert result.step_number == 5
        assert result.phase == 3
        assert result.gate_tier == "STRICT"

    def test_produces_artifact(self, config_with_prior_artifacts, workflow_dir):
        with patch_portify_process("synthesize-spec"):
            result = run_synthesize_spec(
                config_with_prior_artifacts,
                template_path=workflow_dir / "release-spec-template.md",
            )

        artifact = Path(result.artifact_path)
        assert artifact.exists()
        content = artifact.read_text()
        assert "{{SC_PLACEHOLDER:" not in content


class TestSentinelScan:
    """Test sentinel scanning functionality."""

    def test_clean_output_has_no_sentinels(self, tmp_path):
        f = tmp_path / "clean.md"
        f.write_text(SYNTHESIZE_SPEC_GOOD)
        assert scan_sentinels(f) == []

    def test_partial_output_has_sentinels(self, tmp_path):
        f = tmp_path / "partial.md"
        f.write_text(PARTIAL_OUTPUT)
        sentinels = scan_sentinels(f)
        assert len(sentinels) == 2
        assert "architecture_details" in sentinels
        assert "implementation_notes" in sentinels

    def test_nonexistent_file_returns_empty(self, tmp_path):
        assert scan_sentinels(tmp_path / "missing.md") == []


class TestSynthesizeSpecFailures:

    def test_missing_template_fails(self, tmp_path):
        """Missing release-spec-template.md should trigger fail-fast."""
        wf = tmp_path / "sc-test-protocol"
        wf.mkdir()
        (wf / "SKILL.md").write_text("# Test\n")
        # No release-spec-template.md

        output = tmp_path / "output"
        output.mkdir()
        results = output / "results"
        results.mkdir()
        (results / "portify-analysis.md").write_text("---\nstep: x\n---\n\ncontent\n")
        (results / "portify-spec.md").write_text("---\nstep: x\n---\n\ncontent\n")

        config = load_portify_config(
            workflow_path=str(wf),
            output_dir=str(output),
        )
        result = run_synthesize_spec(config)
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_missing_analysis_fails(self, workflow_dir, tmp_path):
        """Missing portify-analysis.md should fail-fast."""
        output = tmp_path / "output"
        output.mkdir()
        results = output / "results"
        results.mkdir()
        # Only portify-spec.md, no analysis
        (results / "portify-spec.md").write_text("---\nstep: x\n---\n\ncontent\n")

        config = load_portify_config(
            workflow_path=str(workflow_dir),
            output_dir=str(output),
        )
        result = run_synthesize_spec(
            config,
            template_path=workflow_dir / "release-spec-template.md",
        )
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_subprocess_timeout(self, config_with_prior_artifacts, workflow_dir):
        with patch_portify_process("synthesize-spec", exit_code=124, timed_out=True):
            result = run_synthesize_spec(
                config_with_prior_artifacts,
                template_path=workflow_dir / "release-spec-template.md",
            )
        assert result.portify_status == PortifyStatus.TIMEOUT

    def test_sentinels_exhaust_retries(self, config_with_prior_artifacts, workflow_dir):
        """Persistent sentinels should exhaust retries and return FAIL."""
        with patch_portify_process(
            "synthesize-spec", fixture_override=PARTIAL_OUTPUT
        ):
            result = run_synthesize_spec(
                config_with_prior_artifacts,
                template_path=workflow_dir / "release-spec-template.md",
            )

        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.PARTIAL_ARTIFACT
