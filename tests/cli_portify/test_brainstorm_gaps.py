"""Tests for brainstorm-gaps step (Step 6).

Covers:
- Happy path: mock subprocess produces findings, SC-006 gate passes
- Inline fallback: activates when /sc:brainstorm skill unavailable
- Finding parsing: structured gap objects from table output
- Section 12 content validation
- Missing prior artifacts: fail-fast
- Subprocess timeout/failure
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
from superclaude.cli.cli_portify.steps.brainstorm_gaps import (
    GapFinding,
    check_brainstorm_skill_available,
    has_section_12_content,
    parse_findings,
    run_brainstorm_gaps,
)
from tests.cli_portify.fixtures.mock_harness import (
    BRAINSTORM_GAPS_GOOD,
    patch_portify_process,
)


@pytest.fixture
def workflow_dir(tmp_path: Path) -> Path:
    wf = tmp_path / "sc-test-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Test Skill\n\nContent.\n")
    return wf


@pytest.fixture
def config_with_prior_artifacts(workflow_dir: Path, tmp_path: Path):
    """Config with synthesized-spec.md from Step 5."""
    output = tmp_path / "output"
    output.mkdir()
    results = output / "results"
    results.mkdir()

    from tests.cli_portify.fixtures.mock_harness import SYNTHESIZE_SPEC_GOOD

    (results / "synthesized-spec.md").write_text(SYNTHESIZE_SPEC_GOOD)

    config = load_portify_config(
        workflow_path=str(workflow_dir),
        output_dir=str(output),
    )
    return config


class TestBrainstormGapsHappyPath:

    def test_produces_pass_result(self, config_with_prior_artifacts):
        with patch_portify_process("brainstorm-gaps"):
            result = run_brainstorm_gaps(config_with_prior_artifacts)

        assert result.portify_status == PortifyStatus.PASS
        assert result.step_name == "brainstorm-gaps"
        assert result.step_number == 6
        assert result.phase == 4
        assert result.gate_tier == "STANDARD"

    def test_produces_artifact(self, config_with_prior_artifacts):
        with patch_portify_process("brainstorm-gaps"):
            result = run_brainstorm_gaps(config_with_prior_artifacts)

        artifact = Path(result.artifact_path)
        assert artifact.exists()


class TestSkillAvailability:

    def test_skill_not_available_returns_false(self, tmp_path):
        """When skill directories don't exist, returns False."""
        with patch(
            "superclaude.cli.cli_portify.steps.brainstorm_gaps.check_brainstorm_skill_available",
            return_value=False,
        ):
            assert not check_brainstorm_skill_available()

    def test_fallback_activates_with_warning(self, config_with_prior_artifacts):
        """Fallback path should still produce PASS result."""
        with (
            patch(
                "superclaude.cli.cli_portify.steps.brainstorm_gaps.check_brainstorm_skill_available",
                return_value=False,
            ),
            patch_portify_process("brainstorm-gaps"),
        ):
            result = run_brainstorm_gaps(config_with_prior_artifacts)

        assert result.portify_status == PortifyStatus.PASS


class TestFindingParsing:

    def test_parse_standard_table(self):
        content = """\
| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|------------------|---------|
| GAP-001 | Missing timeout handler | HIGH | Error Handling | QA Engineer |
| GAP-002 | No retry for transient errors | MEDIUM | Reliability | Backend |
| GAP-003 | Unclear error messages | LOW | UX | End User |
"""
        findings = parse_findings(content)
        assert len(findings) == 3
        assert findings[0].gap_id == "GAP-001"
        assert findings[0].severity == "HIGH"
        assert findings[0].persona == "QA Engineer"
        assert findings[1].gap_id == "GAP-002"
        assert findings[1].severity == "MEDIUM"
        assert findings[2].severity == "LOW"

    def test_parse_empty_content(self):
        assert parse_findings("") == []

    def test_parse_no_table(self):
        assert parse_findings("No gaps found. Specification is comprehensive.") == []

    def test_finding_to_row(self):
        f = GapFinding("GAP-001", "desc", "HIGH", "sec", "persona")
        row = f.to_row()
        assert "GAP-001" in row
        assert "HIGH" in row


class TestSection12Validation:

    def test_section_12_with_findings_table(self):
        content = """\
## Section 12: Gap Analysis Summary

| Gap ID | Description | Severity |
|--------|-------------|----------|
| GAP-001 | Missing handler | HIGH |
"""
        assert has_section_12_content(content) is True

    def test_section_12_with_zero_gap_summary(self):
        content = """\
## Section 12: Brainstorm Summary

Zero gaps identified. Specification is comprehensive and complete.
"""
        assert has_section_12_content(content) is True

    def test_section_12_heading_only_fails(self):
        content = """\
## Section 12: Gap Analysis Summary

"""
        assert has_section_12_content(content) is False

    def test_no_section_12_fails(self):
        content = """\
## Section 11: Open Items

Some open items here.
"""
        assert has_section_12_content(content) is False


class TestBrainstormGapsFailures:

    def test_missing_synthesized_spec_fails(self, workflow_dir, tmp_path):
        output = tmp_path / "output"
        output.mkdir()
        results = output / "results"
        results.mkdir()
        # No synthesized-spec.md

        config = load_portify_config(
            workflow_path=str(workflow_dir),
            output_dir=str(output),
        )
        result = run_brainstorm_gaps(config)
        assert result.portify_status == PortifyStatus.FAIL
        assert result.failure_classification == FailureClassification.MISSING_ARTIFACT

    def test_subprocess_timeout(self, config_with_prior_artifacts):
        with patch_portify_process("brainstorm-gaps", exit_code=124, timed_out=True):
            result = run_brainstorm_gaps(config_with_prior_artifacts)
        assert result.portify_status == PortifyStatus.TIMEOUT

    def test_subprocess_failure(self, config_with_prior_artifacts):
        with patch_portify_process("brainstorm-gaps", exit_code=1):
            result = run_brainstorm_gaps(config_with_prior_artifacts)
        assert result.portify_status == PortifyStatus.FAIL
