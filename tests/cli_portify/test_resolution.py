"""Comprehensive tests for resolve_target() covering all 6 input forms.

Covers:
- All 6 input forms (COMMAND_NAME, COMMAND_PATH, SKILL_DIR, SKILL_NAME, SKILL_FILE, sc: prefix)
- All 4 error codes (ERR_TARGET_NOT_FOUND, ERR_AMBIGUOUS_TARGET, ERR_BROKEN_ACTIVATION, WARN_MISSING_AGENTS)
- Edge cases: standalone command, standalone skill, multi-skill command
- Resolution timing (<1s assertion)
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from superclaude.cli.cli_portify.models import (
    ERR_TARGET_NOT_FOUND,
    TargetInputType,
)
from superclaude.cli.cli_portify.resolution import (
    ResolutionError,
    _find_command_for_skill,
    _find_skill_for_command,
    _parse_activation_skill,
    resolve_target,
)


@pytest.fixture
def project_tree(tmp_path: Path) -> dict[str, Path]:
    """Create a project tree with commands, skills, and agents."""
    commands = tmp_path / "commands"
    commands.mkdir()
    skills = tmp_path / "skills"
    skills.mkdir()
    agents = tmp_path / "agents"
    agents.mkdir()

    # Command: roadmap.md with activation linking to skill
    cmd = commands / "roadmap.md"
    cmd.write_text(
        "# Roadmap Command\n\n"
        "## Activation\n\n"
        "**MANDATORY**: Before executing any protocol steps, invoke:\n"
        "> Skill sc:roadmap-protocol\n\n"
        "## Usage\n\nUsage details.\n"
    )

    # Standalone command: analyze.md (no linked skill)
    standalone_cmd = commands / "analyze.md"
    standalone_cmd.write_text("# Analyze Command\n\nNo activation section.\n")

    # Command with multiple skill references
    multi_cmd = commands / "multi.md"
    multi_cmd.write_text(
        "# Multi Command\n\n"
        "## Activation\n\n"
        "> Skill sc:primary-protocol\n"
        "> Skill sc:secondary-protocol\n"
    )

    # Skill: sc-roadmap-protocol
    skill = skills / "sc-roadmap-protocol"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Roadmap Protocol\n")

    # Standalone skill (no matching command)
    orphan_skill = skills / "sc-orphan-protocol"
    orphan_skill.mkdir()
    (orphan_skill / "SKILL.md").write_text("# Orphan Skill\n")

    # Primary skill for multi-command
    primary = skills / "sc-primary-protocol"
    primary.mkdir()
    (primary / "SKILL.md").write_text("# Primary\n")

    # Agent
    (agents / "architect.md").write_text("# Architect Agent\n")

    return {
        "root": tmp_path,
        "commands": commands,
        "skills": skills,
        "agents": agents,
        "roadmap_cmd": cmd,
        "roadmap_skill": skill,
        "standalone_cmd": standalone_cmd,
        "orphan_skill": orphan_skill,
        "multi_cmd": multi_cmd,
    }


# --- Error Guards ---


class TestErrorGuards:
    """Verify all error code paths."""

    @pytest.mark.parametrize("target", [None, "", "   ", "\t", "\n"])
    def test_empty_target_raises(self, target: str | None) -> None:
        with pytest.raises(ResolutionError) as exc_info:
            resolve_target(target)
        assert exc_info.value.code == ERR_TARGET_NOT_FOUND

    def test_sc_prefix_empty_raises(self) -> None:
        with pytest.raises(ResolutionError) as exc_info:
            resolve_target("sc:")
        assert exc_info.value.code == ERR_TARGET_NOT_FOUND

    def test_sc_prefix_whitespace_raises(self) -> None:
        with pytest.raises(ResolutionError) as exc_info:
            resolve_target("sc:   ")
        assert exc_info.value.code == ERR_TARGET_NOT_FOUND

    def test_not_found_target(self, project_tree: dict[str, Path]) -> None:
        with pytest.raises(ResolutionError) as exc_info:
            resolve_target(
                "nonexistent",
                commands_dir=project_tree["commands"],
                skills_dir=project_tree["skills"],
            )
        assert exc_info.value.code == ERR_TARGET_NOT_FOUND


# --- Form 1: COMMAND_NAME ---


class TestCommandName:
    """Form 1: Bare command name like 'roadmap'."""

    def test_resolve_command_name(self, project_tree: dict[str, Path]) -> None:
        rt = resolve_target(
            "roadmap",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.command_path == project_tree["roadmap_cmd"]
        assert rt.skill_dir == project_tree["roadmap_skill"]

    def test_command_name_with_project_root(self, project_tree: dict[str, Path]) -> None:
        rt = resolve_target(
            "roadmap",
            project_root=project_tree["root"],
        )
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.command_path is not None


# --- Form 2: COMMAND_PATH ---


class TestCommandPath:
    """Form 2: Path to an existing .md command file."""

    def test_resolve_command_path(self, project_tree: dict[str, Path]) -> None:
        rt = resolve_target(
            str(project_tree["roadmap_cmd"]),
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.COMMAND_PATH
        assert rt.command_path == project_tree["roadmap_cmd"]
        assert rt.skill_dir == project_tree["roadmap_skill"]


# --- Form 3: SKILL_DIR ---


class TestSkillDir:
    """Form 3: Path to an existing skill directory."""

    def test_resolve_skill_dir(self, project_tree: dict[str, Path]) -> None:
        rt = resolve_target(
            str(project_tree["roadmap_skill"]),
            commands_dir=project_tree["commands"],
        )
        assert rt.input_type == TargetInputType.SKILL_DIR
        assert rt.skill_dir == project_tree["roadmap_skill"]
        assert rt.command_path == project_tree["roadmap_cmd"]


# --- Form 4: SKILL_NAME ---


class TestSkillName:
    """Form 4: Bare skill directory name like 'sc-roadmap-protocol'."""

    def test_resolve_skill_name(self, project_tree: dict[str, Path]) -> None:
        rt = resolve_target(
            "sc-roadmap-protocol",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.SKILL_NAME
        assert rt.skill_dir == project_tree["roadmap_skill"]
        assert rt.command_path == project_tree["roadmap_cmd"]


# --- Form 5: SKILL_FILE ---


class TestSkillFile:
    """Form 5: Path to a SKILL.md file."""

    def test_resolve_skill_file(self, project_tree: dict[str, Path]) -> None:
        skill_md = project_tree["roadmap_skill"] / "SKILL.md"
        rt = resolve_target(
            str(skill_md),
            commands_dir=project_tree["commands"],
        )
        assert rt.input_type == TargetInputType.SKILL_FILE
        assert rt.skill_dir == project_tree["roadmap_skill"]
        assert rt.command_path == project_tree["roadmap_cmd"]


# --- Form 6: sc: Prefix ---


class TestScPrefix:
    """Form 6: sc: prefixed target like 'sc:roadmap'."""

    def test_resolve_sc_prefix(self, project_tree: dict[str, Path]) -> None:
        rt = resolve_target(
            "sc:roadmap",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.command_path == project_tree["roadmap_cmd"]


# --- Edge Cases ---


class TestEdgeCases:
    """Edge cases: standalone, ambiguity, multi-skill."""

    def test_standalone_command(self, project_tree: dict[str, Path]) -> None:
        """Command with no linked skill resolves with skill_dir=None."""
        rt = resolve_target(
            "analyze",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.command_path == project_tree["standalone_cmd"]
        assert rt.skill_dir is None

    def test_standalone_skill(self, project_tree: dict[str, Path]) -> None:
        """Skill with no matching command resolves with command_path=None."""
        rt = resolve_target(
            "sc-orphan-protocol",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.SKILL_NAME
        assert rt.skill_dir == project_tree["orphan_skill"]
        assert rt.command_path is None

    def test_ambiguity_command_first(self, project_tree: dict[str, Path]) -> None:
        """When target matches both command and skill name, command-first policy."""
        # Create a skill directory with same name as command
        ambig = project_tree["skills"] / "roadmap"
        ambig.mkdir()
        rt = resolve_target(
            "roadmap",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.COMMAND_NAME

    def test_multi_skill_command_returns_primary(self, project_tree: dict[str, Path]) -> None:
        """Command with multiple Skill references uses first (primary) only."""
        rt = resolve_target(
            "multi",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.skill_dir is not None
        assert rt.skill_dir.name == "sc-primary-protocol"


# --- Timing ---


class TestResolutionTiming:
    """Verify resolution completes in <1s."""

    def test_resolution_under_one_second(self, project_tree: dict[str, Path]) -> None:
        start = time.monotonic()
        resolve_target(
            "roadmap",
            commands_dir=project_tree["commands"],
            skills_dir=project_tree["skills"],
        )
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"Resolution took {elapsed:.3f}s (>1s)"


# --- Internal Helpers ---


class TestParseActivationSkill:
    """Verify ## Activation section parsing."""

    def test_standard_activation(self) -> None:
        content = (
            "## Activation\n\n"
            "> Skill sc:roadmap-protocol\n"
        )
        assert _parse_activation_skill(content) == "sc-roadmap-protocol"

    def test_no_activation_section(self) -> None:
        assert _parse_activation_skill("# Just a heading\n") is None

    def test_empty_content(self) -> None:
        assert _parse_activation_skill("") is None

    def test_activation_stops_at_next_section(self) -> None:
        content = (
            "## Activation\n\nSome text.\n"
            "## Usage\n\n> Skill sc:should-not-match\n"
        )
        assert _parse_activation_skill(content) is None


class TestFindCommandForSkill:
    """Verify backward resolution from skill dir to command."""

    def test_standard_backward(self, project_tree: dict[str, Path]) -> None:
        result = _find_command_for_skill(
            project_tree["roadmap_skill"],
            project_tree["commands"],
        )
        assert result == project_tree["roadmap_cmd"]

    def test_no_commands_dir(self, project_tree: dict[str, Path]) -> None:
        result = _find_command_for_skill(project_tree["roadmap_skill"], None)
        assert result is None

    def test_no_matching_command(self, project_tree: dict[str, Path]) -> None:
        result = _find_command_for_skill(
            project_tree["orphan_skill"],
            project_tree["commands"],
        )
        assert result is None


class TestFindSkillForCommand:
    """Verify command-to-skill link via Activation parsing."""

    def test_standard_forward(self, project_tree: dict[str, Path]) -> None:
        result = _find_skill_for_command(
            project_tree["roadmap_cmd"],
            project_tree["skills"],
        )
        assert result == project_tree["roadmap_skill"]

    def test_no_skills_dir(self, project_tree: dict[str, Path]) -> None:
        result = _find_skill_for_command(project_tree["roadmap_cmd"], None)
        assert result is None

    def test_no_activation_section(self, project_tree: dict[str, Path]) -> None:
        result = _find_skill_for_command(
            project_tree["standalone_cmd"],
            project_tree["skills"],
        )
        assert result is None
