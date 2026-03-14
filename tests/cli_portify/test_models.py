"""Unit tests for v2.24.1 model additions.

Covers:
- TargetInputType enum membership (5 values)
- ResolvedTarget construction
- CommandEntry/SkillEntry/AgentEntry tier assignments
- ComponentTree computed properties
- to_flat_inventory() round-trip (Path -> str boundary)
- to_manifest_markdown() output
- Error code constant values
"""

from __future__ import annotations

from pathlib import Path

import pytest

from superclaude.cli.cli_portify.models import (
    AgentEntry,
    CommandEntry,
    ComponentEntry,
    ComponentInventory,
    ComponentTree,
    ERR_AMBIGUOUS_TARGET,
    ERR_BROKEN_ACTIVATION,
    ERR_TARGET_NOT_FOUND,
    ResolvedTarget,
    SkillEntry,
    TargetInputType,
    WARN_MISSING_AGENTS,
)


# --- TargetInputType Enum ---


class TestTargetInputType:
    """Verify TargetInputType enum has exactly 5 spec-defined members."""

    @pytest.mark.parametrize(
        "member",
        ["COMMAND_NAME", "COMMAND_PATH", "SKILL_DIR", "SKILL_NAME", "SKILL_FILE"],
    )
    def test_enum_has_member(self, member: str) -> None:
        assert hasattr(TargetInputType, member)

    def test_enum_has_exactly_five_members(self) -> None:
        assert len(TargetInputType) == 5

    def test_enum_values_are_strings(self) -> None:
        for member in TargetInputType:
            assert isinstance(member.value, str)


# --- ResolvedTarget Dataclass ---


class TestResolvedTarget:
    """Verify ResolvedTarget construction and field types."""

    def test_construction_with_required_fields(self) -> None:
        rt = ResolvedTarget(
            input_form="roadmap",
            input_type=TargetInputType.COMMAND_NAME,
        )
        assert rt.input_form == "roadmap"
        assert rt.input_type == TargetInputType.COMMAND_NAME
        assert rt.command_path is None
        assert rt.skill_dir is None

    def test_construction_with_all_fields(self) -> None:
        rt = ResolvedTarget(
            input_form="roadmap",
            input_type=TargetInputType.COMMAND_NAME,
            command_path=Path("/tmp/roadmap.md"),
            skill_dir=Path("/tmp/sc-roadmap-protocol"),
            project_root=Path("/tmp"),
            commands_dir=Path("/tmp/commands"),
            skills_dir=Path("/tmp/skills"),
            agents_dir=Path("/tmp/agents"),
        )
        assert rt.command_path == Path("/tmp/roadmap.md")
        assert rt.agents_dir == Path("/tmp/agents")

    def test_has_eight_fields(self) -> None:
        assert len(ResolvedTarget.__dataclass_fields__) == 8


# --- Tiered Component Entries ---


class TestTieredEntries:
    """Verify CommandEntry, SkillEntry, AgentEntry tier assignments."""

    def test_command_entry_tier(self) -> None:
        assert CommandEntry().tier == 0

    def test_skill_entry_tier(self) -> None:
        assert SkillEntry().tier == 1

    def test_agent_entry_tier(self) -> None:
        assert AgentEntry().tier == 2


# --- ComponentTree ---


class TestComponentTree:
    """Verify ComponentTree computed properties."""

    def test_empty_tree(self) -> None:
        ct = ComponentTree()
        assert ct.component_count == 0
        assert ct.total_lines == 0
        assert ct.all_source_dirs == []

    def test_full_tree(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(
                name="roadmap",
                line_count=50,
                source_dir=Path("/commands"),
            ),
            skill=SkillEntry(
                name="sc-roadmap-protocol",
                line_count=200,
                source_dir=Path("/skills"),
            ),
            agents=[
                AgentEntry(name="architect", line_count=30, source_dir=Path("/agents")),
                AgentEntry(name="qa", line_count=20, source_dir=Path("/agents")),
            ],
        )
        assert ct.component_count == 4
        assert ct.total_lines == 300
        assert len(ct.all_source_dirs) == 3

    def test_all_source_dirs_deduplicates(self) -> None:
        shared = Path("/shared")
        ct = ComponentTree(
            command=CommandEntry(source_dir=shared),
            skill=SkillEntry(source_dir=shared),
        )
        assert ct.all_source_dirs == [shared]

    def test_command_only_tree(self) -> None:
        ct = ComponentTree(command=CommandEntry(name="solo", line_count=10))
        assert ct.component_count == 1
        assert ct.total_lines == 10

    def test_skill_only_tree(self) -> None:
        ct = ComponentTree(skill=SkillEntry(name="solo-skill", line_count=25))
        assert ct.component_count == 1
        assert ct.total_lines == 25


# --- to_flat_inventory() Round-trip ---


class TestToFlatInventory:
    """Verify ComponentTree -> ComponentInventory conversion."""

    def test_roundtrip_field_equivalence(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(
                name="roadmap",
                path=Path("/tmp/roadmap.md"),
                line_count=50,
            ),
            skill=SkillEntry(
                name="sc-roadmap-protocol",
                path=Path("/tmp/sc-roadmap-protocol"),
                line_count=200,
            ),
        )
        inv = ct.to_flat_inventory()
        assert isinstance(inv, ComponentInventory)
        assert inv.component_count == 2
        assert inv.source_skill == "sc-roadmap-protocol"

    def test_no_path_leakage(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(path=Path("/tmp/cmd.md"), line_count=10),
        )
        inv = ct.to_flat_inventory()
        for comp in inv.components:
            assert isinstance(comp.path, str), f"Path leakage: {type(comp.path)}"
            assert isinstance(comp.name, str)

    def test_empty_tree_inventory(self) -> None:
        ct = ComponentTree()
        inv = ct.to_flat_inventory()
        assert inv.component_count == 0
        assert inv.source_skill == ""

    def test_agents_included(self) -> None:
        ct = ComponentTree(
            agents=[
                AgentEntry(name="a1", path=Path("/tmp/a1.md"), line_count=10),
                AgentEntry(name="a2", path=Path("/tmp/a2.md"), line_count=20),
            ],
        )
        inv = ct.to_flat_inventory()
        assert inv.component_count == 2
        agent_types = [c.component_type for c in inv.components]
        assert all(t == "agent" for t in agent_types)


# --- to_manifest_markdown() ---


class TestToManifestMarkdown:
    """Verify Markdown manifest output."""

    def test_has_yaml_frontmatter(self) -> None:
        ct = ComponentTree(
            command=CommandEntry(name="roadmap", line_count=50),
            skill=SkillEntry(name="sc-roadmap-protocol", line_count=200),
        )
        md = ct.to_manifest_markdown()
        assert md.startswith("---\n")
        assert "source_command: roadmap" in md
        assert "source_skill: sc-roadmap-protocol" in md
        assert "component_count: 2" in md

    def test_empty_tree_manifest(self) -> None:
        md = ComponentTree().to_manifest_markdown()
        assert "No components discovered." in md


# --- Error Code Constants ---


class TestErrorConstants:
    """Verify exact string values of all 4 error code constants."""

    def test_err_target_not_found(self) -> None:
        assert ERR_TARGET_NOT_FOUND == "ERR_TARGET_NOT_FOUND"

    def test_err_ambiguous_target(self) -> None:
        assert ERR_AMBIGUOUS_TARGET == "ERR_AMBIGUOUS_TARGET"

    def test_err_broken_activation(self) -> None:
        assert ERR_BROKEN_ACTIVATION == "ERR_BROKEN_ACTIVATION"

    def test_warn_missing_agents(self) -> None:
        assert WARN_MISSING_AGENTS == "WARN_MISSING_AGENTS"
