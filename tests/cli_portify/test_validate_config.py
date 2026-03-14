"""Tests for validate-config step (Step 1).

Covers:
- SC-001 timing: completes under 1s for valid and invalid inputs
- All 4 error codes: ERR_INVALID_PATH, ERR_MISSING_SKILL,
  ERR_OUTPUT_NOT_WRITABLE, ERR_NAME_COLLISION
- validate-config-result.json artifact output
- Step runs without Claude subprocess
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.models import (
    AgentEntry,
    ComponentTree,
    ERR_BROKEN_ACTIVATION,
    PortifyStatus,
    WARN_MISSING_AGENTS,
)
from superclaude.cli.cli_portify.steps.validate_config import (
    ERR_INVALID_PATH,
    ERR_MISSING_SKILL,
    ERR_NAME_COLLISION,
    ERR_OUTPUT_NOT_WRITABLE,
    ValidateConfigResult,
    _classify_warnings,
    run_validate_config,
)


@pytest.fixture
def tmp_workflow(tmp_path: Path) -> Path:
    """Create a temporary workflow directory with SKILL.md."""
    wf = tmp_path / "sc-test-workflow-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Test Skill\n\nTest content.\n")
    return wf


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    out = tmp_path / "output"
    out.mkdir()
    return out


class TestValidateConfigTiming:
    """SC-001: validate-config must complete under 1s."""

    def test_valid_input_under_one_second(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        start = time.monotonic()
        result, step_result = run_validate_config(config)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"validate-config took {elapsed:.3f}s (>1s)"
        assert result.valid is True

    def test_invalid_input_under_one_second(self, tmp_path):
        config = load_portify_config(
            workflow_path=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
        )
        start = time.monotonic()
        result, step_result = run_validate_config(config)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"validate-config took {elapsed:.3f}s (>1s)"
        assert result.valid is False


class TestValidateConfigErrors:
    """All 4 error code paths."""

    def test_err_invalid_path(self, tmp_path):
        config = load_portify_config(
            workflow_path=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
        )
        result, step_result = run_validate_config(config)
        assert result.valid is False
        codes = [e["code"] for e in result.errors]
        assert ERR_INVALID_PATH in codes
        assert step_result.portify_status == PortifyStatus.FAIL

    def test_err_missing_skill(self, tmp_path):
        wf = tmp_path / "empty-workflow"
        wf.mkdir()
        config = load_portify_config(
            workflow_path=wf,
            output_dir=tmp_path / "output",
        )
        result, step_result = run_validate_config(config)
        assert result.valid is False
        codes = [e["code"] for e in result.errors]
        assert ERR_MISSING_SKILL in codes

    def test_err_output_not_writable(self, tmp_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir="/proc/1/cli_portify_test_nonexistent",
        )
        # Provide a valid artifact output_dir since config.results_dir is non-writable
        result, step_result = run_validate_config(
            config, output_dir=tmp_path / "artifact-out"
        )
        assert result.valid is False
        codes = [e["code"] for e in result.errors]
        assert ERR_OUTPUT_NOT_WRITABLE in codes

    def test_err_name_collision(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
            cli_name="sprint",
        )
        result, step_result = run_validate_config(config)
        assert result.valid is False
        codes = [e["code"] for e in result.errors]
        assert ERR_NAME_COLLISION in codes


class TestValidateConfigArtifact:
    """validate-config-result.json output."""

    def test_artifact_written(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        result, step_result = run_validate_config(config)
        artifact = Path(step_result.artifact_path)
        assert artifact.exists()
        data = json.loads(artifact.read_text())
        assert data["step"] == "validate-config"
        assert data["valid"] is True

    def test_artifact_contains_derived_name(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        result, step_result = run_validate_config(config)
        data = json.loads(Path(step_result.artifact_path).read_text())
        # sc-test-workflow-protocol -> test-workflow
        assert data["cli_name_kebab"] == "test-workflow"
        assert data["cli_name_snake"] == "test_workflow"

    def test_artifact_contains_errors_on_failure(self, tmp_path):
        config = load_portify_config(
            workflow_path=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
        )
        result, step_result = run_validate_config(config)
        data = json.loads(Path(step_result.artifact_path).read_text())
        assert data["valid"] is False
        assert len(data["errors"]) >= 1
        assert "code" in data["errors"][0]

    def test_artifact_duration_recorded(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        result, step_result = run_validate_config(config)
        data = json.loads(Path(step_result.artifact_path).read_text())
        assert data["duration_seconds"] >= 0
        assert data["duration_seconds"] < 1.0


class TestValidateConfigStepResult:
    """PortifyStepResult metadata."""

    def test_step_metadata(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        _, step_result = run_validate_config(config)
        assert step_result.step_name == "validate-config"
        assert step_result.step_number == 1
        assert step_result.phase == 1
        assert step_result.gate_tier == "EXEMPT"

    def test_pass_status_on_valid(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        _, step_result = run_validate_config(config)
        assert step_result.portify_status == PortifyStatus.PASS

    def test_fail_status_on_invalid(self, tmp_path):
        config = load_portify_config(
            workflow_path=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
        )
        _, step_result = run_validate_config(config)
        assert step_result.portify_status == PortifyStatus.FAIL


# --- Check 5: Command-to-Skill Link Validity (R-038) ---


class TestCheck5BrokenActivation:
    """Check 5: ERR_BROKEN_ACTIVATION when command_path set but skill dir invalid."""

    def test_broken_link_detected(self, tmp_path):
        """Command exists but workflow path is a non-directory file."""
        cmd = tmp_path / "commands" / "test.md"
        cmd.parent.mkdir(parents=True)
        cmd.write_text("# Command\n")
        out = tmp_path / "output"

        # workflow_path points to the command file itself (not a directory)
        config = load_portify_config(
            workflow_path=cmd,
            output_dir=out,
        )
        config.command_path = cmd
        result, step_result = run_validate_config(config)
        assert result.valid is False
        codes = [e["code"] for e in result.errors]
        assert ERR_BROKEN_ACTIVATION in codes

    def test_valid_link_no_error(self, tmp_workflow, tmp_output):
        """When workflow path is a valid directory, no broken activation error."""
        cmd = tmp_workflow / "test.md"
        cmd.write_text("# Command\n")
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.command_path = cmd
        result, step_result = run_validate_config(config)
        codes = [e["code"] for e in result.errors]
        assert ERR_BROKEN_ACTIVATION not in codes

    def test_no_command_path_no_check(self, tmp_workflow, tmp_output):
        """When command_path is None, check 5 is skipped."""
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.command_path = None
        result, _ = run_validate_config(config)
        codes = [e["code"] for e in result.errors]
        assert ERR_BROKEN_ACTIVATION not in codes

    def test_existing_checks_unaffected(self, tmp_workflow, tmp_output):
        """Checks 1-4 remain functional with check 5 added."""
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        result, _ = run_validate_config(config)
        assert result.valid is True
        assert result.errors == []


# --- Check 6: Referenced Agent Existence (R-039) ---


class TestCheck6MissingAgents:
    """Check 6: WARN_MISSING_AGENTS for agents with found=False."""

    def test_missing_agent_produces_warning(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.component_tree = ComponentTree(
            agents=[
                AgentEntry(name="found-agent", found=True),
                AgentEntry(name="ghost-agent", found=False),
            ]
        )
        result, _ = run_validate_config(config)
        assert any("ghost-agent" in w for w in result.warnings)
        assert any(WARN_MISSING_AGENTS in w for w in result.warnings)

    def test_all_agents_found_no_warning(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.component_tree = ComponentTree(
            agents=[
                AgentEntry(name="agent-a", found=True),
                AgentEntry(name="agent-b", found=True),
            ]
        )
        result, _ = run_validate_config(config)
        assert len(result.warnings) == 0

    def test_no_component_tree_no_warning(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.component_tree = None
        result, _ = run_validate_config(config)
        assert len(result.warnings) == 0

    def test_multiple_missing_agents(self, tmp_workflow, tmp_output):
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.component_tree = ComponentTree(
            agents=[
                AgentEntry(name="missing-a", found=False),
                AgentEntry(name="missing-b", found=False),
            ]
        )
        result, _ = run_validate_config(config)
        assert len(result.warnings) == 2
        names_warned = [w.split(": ")[1] for w in result.warnings]
        assert "missing-a" in names_warned
        assert "missing-b" in names_warned

    def test_missing_agents_dont_fail_validation(self, tmp_workflow, tmp_output):
        """SC-8: Missing agents warn, don't fail."""
        config = load_portify_config(
            workflow_path=tmp_workflow,
            output_dir=tmp_output,
        )
        config.component_tree = ComponentTree(
            agents=[AgentEntry(name="ghost-agent", found=False)]
        )
        result, step_result = run_validate_config(config)
        assert result.valid is True
        assert step_result.portify_status == PortifyStatus.PASS


# --- T03.02: to_dict() Completeness ---


class TestToDictCompleteness:
    """to_dict() includes all v2.24.1 fields with correct types."""

    def test_all_new_fields_present(self):
        result = ValidateConfigResult(
            valid=True,
            command_path="/tmp/cmd.md",
            skill_dir="/tmp/skill",
            target_type="command_name",
            agent_count=3,
            warnings=["WARN_MISSING_AGENTS: ghost"],
        )
        d = result.to_dict()
        assert "command_path" in d
        assert "skill_dir" in d
        assert "target_type" in d
        assert "agent_count" in d
        assert "warnings" in d

    def test_no_path_objects_in_dict(self):
        """All values in to_dict() must be JSON-serializable (no Path objects)."""
        from pathlib import Path
        result = ValidateConfigResult(
            command_path=str(Path("/tmp/cmd.md")),
            skill_dir=str(Path("/tmp/skill")),
        )
        d = result.to_dict()
        for key, value in d.items():
            assert not isinstance(value, Path), f"Path object in to_dict()['{key}']"

    def test_roundtrip_json_serializable(self):
        """to_dict() output is JSON-serializable."""
        import json
        result = ValidateConfigResult(
            valid=True,
            cli_name_kebab="test",
            cli_name_snake="test",
            workflow_path_resolved="/tmp",
            output_dir="/tmp/out",
            errors=[],
            duration_seconds=0.01,
            command_path="/tmp/cmd.md",
            skill_dir="/tmp/skill",
            target_type="command_name",
            agent_count=2,
            warnings=["WARN_MISSING_AGENTS: ghost"],
        )
        d = result.to_dict()
        serialized = json.dumps(d)
        deserialized = json.loads(serialized)
        assert deserialized["command_path"] == "/tmp/cmd.md"
        assert deserialized["agent_count"] == 2
        assert deserialized["warnings"] == ["WARN_MISSING_AGENTS: ghost"]
        assert deserialized["target_type"] == "command_name"

    def test_field_count_is_thirteen(self):
        """to_dict() returns exactly 13 fields."""
        d = ValidateConfigResult().to_dict()
        assert len(d) == 13
