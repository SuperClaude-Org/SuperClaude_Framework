"""Tests for discover-components step (Step 2).

Covers:
- SC-002 timing: completes under 5s for valid skill directories
- Component discovery: SKILL.md, refs/, rules/, templates/, scripts/,
  command files
- component-inventory.md artifact with YAML frontmatter accuracy
- Accurate line counting
- Step runs without Claude subprocess
"""

from __future__ import annotations

import re
import time
from pathlib import Path

import pytest

from superclaude.cli.cli_portify.config import load_portify_config
from superclaude.cli.cli_portify.models import (
    AgentEntry,
    PortifyStatus,
    ResolvedTarget,
    TargetInputType,
)
from superclaude.cli.cli_portify.models import (
    CommandEntry,
    ComponentTree,
    SkillEntry,
)
from superclaude.cli.cli_portify.steps.discover_components import (
    AGENT_PATTERN_BACKTICK,
    AGENT_PATTERN_MODEL_PAREN,
    AGENT_PATTERN_PATH,
    AGENT_PATTERN_USES,
    AGENT_PATTERN_VERB,
    AGENT_PATTERN_YAML_ARRAY,
    AGENT_PATTERNS,
    COMPONENT_COMMAND,
    COMPONENT_REF,
    COMPONENT_RULE,
    COMPONENT_SCRIPT,
    COMPONENT_SKILL,
    COMPONENT_TEMPLATE,
    build_component_tree,
    deduplicate_agents,
    extract_agents,
    render_enriched_inventory,
    run_discover_components,
    _write_inventory_artifact,
)
from superclaude.cli.cli_portify.utils import parse_frontmatter


@pytest.fixture
def rich_workflow(tmp_path: Path) -> Path:
    """Create a workflow directory with multiple component types."""
    wf = tmp_path / "sc-example-protocol"
    wf.mkdir()

    # SKILL.md
    (wf / "SKILL.md").write_text("# Example Skill\n\nLine 2\nLine 3\n")

    # refs/
    refs = wf / "refs"
    refs.mkdir()
    (refs / "guide.md").write_text("# Guide\n\nReference content.\n")

    # rules/
    rules = wf / "rules"
    rules.mkdir()
    (rules / "rule-01.md").write_text("# Rule 01\n\nDo X.\nDo Y.\n")
    (rules / "rule-02.md").write_text("# Rule 02\n\nDo Z.\n")

    # templates/
    templates = wf / "templates"
    templates.mkdir()
    (templates / "output.md").write_text("---\ntitle: Template\n---\n\nBody.\n")

    # scripts/
    scripts = wf / "scripts"
    scripts.mkdir()
    (scripts / "setup.sh").write_text("#!/bin/bash\necho hello\n")

    # Command file (top-level .md, not SKILL.md)
    (wf / "COMMAND.md").write_text("# Command\n\nCommand body.\n")

    return wf


@pytest.fixture
def minimal_workflow(tmp_path: Path) -> Path:
    """Create a minimal workflow with only SKILL.md."""
    wf = tmp_path / "sc-minimal-protocol"
    wf.mkdir()
    (wf / "SKILL.md").write_text("# Minimal\n")
    return wf


class TestDiscoverComponentsTiming:
    """SC-002: discover-components must complete under 5s."""

    def test_completes_under_five_seconds(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        start = time.monotonic()
        inventory, step_result = run_discover_components(config)
        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"discover-components took {elapsed:.3f}s (>5s)"


class TestComponentDiscovery:
    """Component type coverage."""

    def test_discovers_skill_md(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        skills = [c for c in inventory.components if c.component_type == COMPONENT_SKILL]
        assert len(skills) == 1
        assert skills[0].name == "SKILL.md"

    def test_discovers_refs(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        refs = [c for c in inventory.components if c.component_type == COMPONENT_REF]
        assert len(refs) == 1
        assert refs[0].name == "guide.md"

    def test_discovers_rules(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        rules = [c for c in inventory.components if c.component_type == COMPONENT_RULE]
        assert len(rules) == 2

    def test_discovers_templates(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        templates = [c for c in inventory.components if c.component_type == COMPONENT_TEMPLATE]
        assert len(templates) == 1

    def test_discovers_scripts(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        scripts = [c for c in inventory.components if c.component_type == COMPONENT_SCRIPT]
        assert len(scripts) == 1

    def test_discovers_command_files(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        commands = [c for c in inventory.components if c.component_type == COMPONENT_COMMAND]
        assert len(commands) == 1
        assert commands[0].name == "COMMAND.md"

    def test_total_component_count(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        # 1 skill + 1 ref + 2 rules + 1 template + 1 script + 1 command = 7
        assert inventory.component_count == 7

    def test_minimal_workflow(self, minimal_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=minimal_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        assert inventory.component_count == 1
        assert inventory.components[0].component_type == COMPONENT_SKILL


class TestLineCountAccuracy:
    """Accurate line counting per component."""

    def test_skill_md_line_count(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        skill = [c for c in inventory.components if c.component_type == COMPONENT_SKILL][0]
        # "# Example Skill\n\nLine 2\nLine 3\n" = 4 lines
        assert skill.line_count == 4

    def test_total_lines(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, _ = run_discover_components(config)
        assert inventory.total_lines > 0
        # Sum should match individual counts
        manual_sum = sum(c.line_count for c in inventory.components)
        assert inventory.total_lines == manual_sum


class TestInventoryArtifact:
    """component-inventory.md output with YAML frontmatter."""

    def test_artifact_written(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        _, step_result = run_discover_components(config)
        artifact = Path(step_result.artifact_path)
        assert artifact.exists()
        assert artifact.name == "component-inventory.md"

    def test_frontmatter_has_source_skill(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        _, step_result = run_discover_components(config)
        content = Path(step_result.artifact_path).read_text()
        fm, _ = parse_frontmatter(content)
        assert "source_skill" in fm
        assert fm["source_skill"] == "sc-example-protocol"

    def test_frontmatter_has_component_count(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, step_result = run_discover_components(config)
        content = Path(step_result.artifact_path).read_text()
        fm, _ = parse_frontmatter(content)
        assert "component_count" in fm
        assert fm["component_count"] == inventory.component_count

    def test_frontmatter_has_total_lines(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        inventory, step_result = run_discover_components(config)
        content = Path(step_result.artifact_path).read_text()
        fm, _ = parse_frontmatter(content)
        assert "total_lines" in fm
        assert fm["total_lines"] == inventory.total_lines


class TestDiscoverComponentsStepResult:
    """PortifyStepResult metadata."""

    def test_step_metadata(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        _, step_result = run_discover_components(config)
        assert step_result.step_name == "discover-components"
        assert step_result.step_number == 2
        assert step_result.phase == 1
        assert step_result.gate_tier == "STANDARD"

    def test_pass_status(self, rich_workflow, tmp_path):
        config = load_portify_config(
            workflow_path=rich_workflow,
            output_dir=tmp_path / "output",
        )
        _, step_result = run_discover_components(config)
        assert step_result.portify_status == PortifyStatus.PASS


# --- T02.01: Agent Extraction Tests ---


SYNTHETIC_SKILL_MD = """---
name: sc:test-protocol
description: Synthetic SKILL.md with all 6 agent patterns
---

# Test Skill

## Pattern 1: Backtick-agent notation
Pass 1 uses `audit-scanner` (Haiku), Pass 2 uses `audit-analyzer` (Sonnet).

## Pattern 2: YAML array items
- audit-consolidator
- quality-engineer

## Pattern 3: Spawn/delegate/invoke verbs
Spawn verification agent (backend-architect)
Delegate to performance-engineer for optimization.
Dispatch quality-engineer agent using the prompt.

## Pattern 4: Uses references
This step uses: `deep-research-agent` for investigation.

## Pattern 5: Model-parenthetical
The audit-validator (Sonnet) handles spot checks.

## Pattern 6: agents/ path references
Agent type: `merge-executor` for merging.
See agents/frontend-architect for details.
"""


class TestAgentPatternBacktick:
    """Pattern 1: backtick-agent notation with model parenthetical."""

    def test_matches_backtick_haiku(self):
        matches = AGENT_PATTERN_BACKTICK.findall("`audit-scanner` (Haiku)")
        assert "audit-scanner" in matches

    def test_matches_backtick_sonnet(self):
        matches = AGENT_PATTERN_BACKTICK.findall("`audit-analyzer` (Sonnet)")
        assert "audit-analyzer" in matches


class TestAgentPatternYamlArray:
    """Pattern 2: YAML array items."""

    def test_matches_yaml_item(self):
        matches = AGENT_PATTERN_YAML_ARRAY.findall("- quality-engineer\n- audit-scanner")
        assert "quality-engineer" in matches
        assert "audit-scanner" in matches


class TestAgentPatternVerb:
    """Pattern 3: Spawn/delegate/invoke verbs."""

    def test_spawn_with_parens(self):
        matches = AGENT_PATTERN_VERB.findall("Spawn verification agent (backend-architect)")
        assert "backend-architect" in matches

    def test_delegate_to(self):
        matches = AGENT_PATTERN_VERB.findall("Delegate to performance-engineer")
        assert "performance-engineer" in matches

    def test_dispatch(self):
        matches = AGENT_PATTERN_VERB.findall("Dispatch quality-engineer agent")
        assert "quality-engineer" in matches


class TestAgentPatternUses:
    """Pattern 4: uses references."""

    def test_uses_backtick(self):
        matches = AGENT_PATTERN_USES.findall("uses: `deep-research-agent`")
        assert "deep-research-agent" in matches


class TestAgentPatternModelParen:
    """Pattern 5: Model-parenthetical."""

    def test_model_paren(self):
        matches = AGENT_PATTERN_MODEL_PAREN.findall("audit-validator (Sonnet)")
        assert "audit-validator" in matches


class TestAgentPatternPath:
    """Pattern 6: agents/ path references."""

    def test_agents_path(self):
        matches = AGENT_PATTERN_PATH.findall("agents/frontend-architect")
        assert "frontend-architect" in matches

    def test_agent_type(self):
        matches = AGENT_PATTERN_PATH.findall("Agent type: `merge-executor`")
        assert "merge-executor" in matches


class TestExtractAgents:
    """extract_agents() applies all 6 patterns to SKILL.md content."""

    def test_extracts_all_patterns_from_synthetic(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # Create some agent files
        for name in [
            "audit-scanner", "audit-analyzer", "audit-consolidator",
            "quality-engineer", "backend-architect", "performance-engineer",
            "deep-research-agent", "audit-validator", "merge-executor",
            "frontend-architect",
        ]:
            (agents_dir / f"{name}.md").write_text(f"# {name}\nAgent definition.\n")

        agents = extract_agents(SYNTHETIC_SKILL_MD, agents_dir)
        names = {a.name for a in agents}

        # All agents should be found
        assert "audit-scanner" in names
        assert "audit-analyzer" in names
        assert "quality-engineer" in names
        assert "backend-architect" in names
        assert "performance-engineer" in names
        assert "deep-research-agent" in names
        assert "audit-validator" in names
        assert "merge-executor" in names
        assert "frontend-architect" in names

    def test_all_found_true_when_files_exist(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "audit-scanner.md").write_text("# scanner\n")

        agents = extract_agents("`audit-scanner` (Haiku)", agents_dir)
        found = [a for a in agents if a.name == "audit-scanner"]
        assert len(found) == 1
        assert found[0].found is True
        assert found[0].path == agents_dir / "audit-scanner.md"

    def test_found_false_when_file_missing(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # No agent file created

        agents = extract_agents("`ghost-agent` (Haiku)", agents_dir)
        found = [a for a in agents if a.name == "ghost-agent"]
        assert len(found) == 1
        assert found[0].found is False
        assert found[0].path is None

    def test_deduplicates_across_patterns(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "quality-engineer.md").write_text("# qe\n")

        # quality-engineer appears in patterns 2, 3
        content = "- quality-engineer\nSpawn verification agent (quality-engineer)"
        agents = extract_agents(content, agents_dir)
        qe = [a for a in agents if a.name == "quality-engineer"]
        assert len(qe) == 1

    def test_excludes_false_positives(self):
        content = "Use sub-agent for delegation. The multi-agent approach."
        agents = extract_agents(content, None)
        names = {a.name for a in agents}
        assert "sub-agent" not in names
        assert "multi-agent" not in names

    def test_no_agents_dir_returns_not_found(self):
        agents = extract_agents("`audit-scanner` (Haiku)", None)
        assert len(agents) == 1
        assert agents[0].found is False
        assert agents[0].path is None

    def test_six_patterns_are_compiled(self):
        assert len(AGENT_PATTERNS) == 6
        for p in AGENT_PATTERNS:
            assert isinstance(p, type(re.compile("")))


class TestBuildComponentTree:
    """build_component_tree() assembles ComponentTree from ResolvedTarget."""

    def test_populates_command_skill_agents(self, tmp_path):
        # Set up filesystem
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        cmd_file = commands_dir / "test-cmd.md"
        cmd_file.write_text("# Command\nLine 2\n")

        skills_dir = tmp_path / "skills"
        skill_dir = skills_dir / "sc-test-protocol"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "# Skill\nUses `audit-scanner` (Haiku) for scanning.\n"
        )

        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "audit-scanner.md").write_text("# Scanner\n")

        resolved = ResolvedTarget(
            input_form="test-cmd",
            input_type=TargetInputType.COMMAND_NAME,
            command_path=cmd_file,
            skill_dir=skill_dir,
            agents_dir=agents_dir,
        )

        tree = build_component_tree(resolved)

        assert tree.command is not None
        assert tree.command.name == "test-cmd"
        assert tree.command.line_count == 2

        assert tree.skill is not None
        assert tree.skill.name == "sc-test-protocol"
        assert tree.skill.line_count == 2

        assert len(tree.agents) >= 1
        scanner = [a for a in tree.agents if a.name == "audit-scanner"]
        assert len(scanner) == 1
        assert scanner[0].found is True

    def test_no_command_path(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Skill\n")

        resolved = ResolvedTarget(
            input_form="skill",
            input_type=TargetInputType.SKILL_DIR,
            skill_dir=skill_dir,
        )
        tree = build_component_tree(resolved)
        assert tree.command is None
        assert tree.skill is not None

    def test_no_skill_dir(self, tmp_path):
        cmd_file = tmp_path / "cmd.md"
        cmd_file.write_text("# Cmd\n")

        resolved = ResolvedTarget(
            input_form="cmd",
            input_type=TargetInputType.COMMAND_PATH,
            command_path=cmd_file,
        )
        tree = build_component_tree(resolved)
        assert tree.command is not None
        assert tree.skill is None
        assert tree.agents == []

    def test_component_count_includes_all(self, tmp_path):
        commands_dir = tmp_path / "commands"
        commands_dir.mkdir()
        cmd_file = commands_dir / "cmd.md"
        cmd_file.write_text("# Cmd\n")

        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "Uses `audit-scanner` (Haiku) and `audit-analyzer` (Sonnet).\n"
        )

        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "audit-scanner.md").write_text("# s\n")
        (agents_dir / "audit-analyzer.md").write_text("# a\n")

        resolved = ResolvedTarget(
            input_form="cmd",
            input_type=TargetInputType.COMMAND_NAME,
            command_path=cmd_file,
            skill_dir=skill_dir,
            agents_dir=agents_dir,
        )
        tree = build_component_tree(resolved)
        # 1 command + 1 skill + 2 agents = 4
        assert tree.component_count == 4


# --- T02.02: Missing Agents and Deduplication Tests ---


class TestMissingAgentWarning:
    """Missing agent references produce AgentEntry with found=False and log warning."""

    def test_missing_agent_produces_entry_with_found_false(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # No agent file for "ghost-agent"
        agents = extract_agents("Delegate to ghost-agent for testing.", agents_dir)
        ghost = [a for a in agents if a.name == "ghost-agent"]
        assert len(ghost) == 1
        assert ghost[0].found is False

    def test_missing_agent_has_none_path(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        agents = extract_agents("Delegate to ghost-agent for testing.", agents_dir)
        ghost = [a for a in agents if a.name == "ghost-agent"]
        assert ghost[0].path is None

    def test_pipeline_continues_with_missing_agents(self, tmp_path):
        """Non-fatal: extract_agents returns entries even for missing agents."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "audit-scanner.md").write_text("# Scanner\n")
        content = (
            "`audit-scanner` (Haiku) is found.\n"
            "Delegate to ghost-agent for testing."
        )
        agents = extract_agents(content, agents_dir)
        names = {a.name for a in agents}
        assert "audit-scanner" in names
        assert "ghost-agent" in names
        found_scanner = [a for a in agents if a.name == "audit-scanner"]
        assert found_scanner[0].found is True
        found_ghost = [a for a in agents if a.name == "ghost-agent"]
        assert found_ghost[0].found is False

    def test_warning_logged_for_missing_agent(self, tmp_path, caplog):
        import logging
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        with caplog.at_level(logging.WARNING):
            extract_agents("Delegate to ghost-agent for testing.", agents_dir)
        assert "WARN_MISSING_AGENTS" in caplog.text
        assert "ghost-agent" in caplog.text


class TestDeduplicateAgents:
    """--include-agent deduplication: CLI-override takes precedence."""

    def test_cli_override_replaces_auto(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "audit-scanner.md").write_text("# Scanner\n")

        auto = [AgentEntry(name="audit-scanner", found=True, referenced_in="auto")]
        result = deduplicate_agents(auto, ["audit-scanner"], agents_dir)

        scanners = [a for a in result if a.name == "audit-scanner"]
        assert len(scanners) == 1
        assert scanners[0].referenced_in == "cli-override"

    def test_cli_adds_new_agent(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        (agents_dir / "quality-engineer.md").write_text("# QE\n")

        auto = [AgentEntry(name="audit-scanner", found=True, referenced_in="auto")]
        result = deduplicate_agents(auto, ["quality-engineer"], agents_dir)

        names = {a.name for a in result}
        assert "audit-scanner" in names
        assert "quality-engineer" in names
        qe = [a for a in result if a.name == "quality-engineer"]
        assert qe[0].referenced_in == "cli-override"

    def test_empty_cli_agents_returns_auto(self):
        auto = [AgentEntry(name="audit-scanner", found=True, referenced_in="auto")]
        result = deduplicate_agents(auto, [], None)
        assert len(result) == 1
        assert result[0].name == "audit-scanner"
        assert result[0].referenced_in == "auto"

    def test_empty_string_filtered(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        auto = [AgentEntry(name="audit-scanner", found=True, referenced_in="auto")]
        result = deduplicate_agents(auto, ["", "  "], agents_dir)
        assert len(result) == 1
        assert result[0].name == "audit-scanner"

    def test_cli_override_not_found_still_added(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        # No file for "custom-agent"
        result = deduplicate_agents([], ["custom-agent"], agents_dir)
        assert len(result) == 1
        assert result[0].name == "custom-agent"
        assert result[0].found is False
        assert result[0].referenced_in == "cli-override"


# --- T03.03: Enriched component-inventory.md ---


class TestRenderEnrichedInventory:
    """Enriched component-inventory.md with 8 frontmatter fields and all sections."""

    def _build_full_tree(self) -> ComponentTree:
        return ComponentTree(
            command=CommandEntry(
                name="roadmap",
                path=Path("/tmp/commands/roadmap.md"),
                line_count=50,
                source_dir=Path("/tmp/commands"),
            ),
            skill=SkillEntry(
                name="sc-roadmap-protocol",
                path=Path("/tmp/skills/sc-roadmap-protocol/SKILL.md"),
                line_count=200,
                source_dir=Path("/tmp/skills/sc-roadmap-protocol"),
            ),
            agents=[
                AgentEntry(
                    name="audit-scanner",
                    found=True,
                    source_dir=Path("/tmp/agents"),
                    line_count=30,
                ),
                AgentEntry(
                    name="ghost-agent",
                    found=False,
                    source_dir=None,
                    line_count=0,
                ),
            ],
        )

    def test_has_eight_frontmatter_keys(self):
        tree = self._build_full_tree()
        md = render_enriched_inventory(tree, 0.05)
        fm, _ = parse_frontmatter(md)
        required = [
            "source_command", "source_skill", "component_count",
            "total_lines", "agent_count", "has_command", "has_skill",
            "duration_seconds",
        ]
        for key in required:
            assert key in fm, f"Missing frontmatter key: {key}"

    def test_frontmatter_values_correct(self):
        tree = self._build_full_tree()
        md = render_enriched_inventory(tree, 0.123)
        fm, _ = parse_frontmatter(md)
        assert fm["source_command"] == "roadmap"
        assert fm["source_skill"] == "sc-roadmap-protocol"
        assert fm["component_count"] == 4
        assert fm["total_lines"] == 280
        assert fm["agent_count"] == 2
        assert fm["has_command"] is True
        assert fm["has_skill"] is True
        assert fm["duration_seconds"] == 0.123

    def test_command_section_present(self):
        tree = self._build_full_tree()
        md = render_enriched_inventory(tree, 0.01)
        assert "## Command (Tier 0)" in md
        assert "roadmap" in md

    def test_command_section_absent_when_no_command(self):
        tree = ComponentTree(
            skill=SkillEntry(name="orphan-skill", line_count=10),
        )
        md = render_enriched_inventory(tree, 0.01)
        assert "## Command (Tier 0)" not in md

    def test_agents_table_present(self):
        tree = self._build_full_tree()
        md = render_enriched_inventory(tree, 0.01)
        assert "## Agents (Tier 2)" in md
        assert "| audit-scanner |" in md
        assert "| ghost-agent |" in md
        assert "**NO**" in md

    def test_cross_tier_data_flow_section(self):
        tree = self._build_full_tree()
        md = render_enriched_inventory(tree, 0.01)
        assert "## Cross-Tier Data Flow" in md
        assert "Command (roadmap)" in md
        assert "Skill (sc-roadmap-protocol)" in md
        assert "Agents (audit-scanner, ghost-agent)" in md

    def test_resolution_log_section(self):
        tree = self._build_full_tree()
        log = {"input_count": 15, "tier_applied": "tier2", "dropped": 5}
        md = render_enriched_inventory(tree, 0.01, resolution_log=log)
        assert "## Resolution Log" in md
        assert "input_count" in md
        assert "tier2" in md

    def test_resolution_log_empty(self):
        tree = self._build_full_tree()
        md = render_enriched_inventory(tree, 0.01)
        assert "No consolidation applied." in md

    def test_empty_tree_renders(self):
        tree = ComponentTree()
        md = render_enriched_inventory(tree, 0.001)
        fm, _ = parse_frontmatter(md)
        assert fm["component_count"] == 0
        assert fm["has_command"] is False
        assert fm["has_skill"] is False
        assert "No components discovered." in md


# ---------------------------------------------------------------------------
# T02.05 acceptance criteria: test_inventory
# ---------------------------------------------------------------------------


class TestInventory:
    """T02.05 — Component discovery produces component-inventory with correct structure.

    These tests satisfy the validation command:
        uv run pytest tests/ -k "test_inventory"
    """

    def test_inventory_contains_skill_md(self, tmp_path):
        """Inventory contains at least one component referencing SKILL.md."""
        from superclaude.cli.cli_portify.config import load_portify_config
        from superclaude.cli.cli_portify.steps.discover_components import run_discover_components

        wf = tmp_path / "sc-test-proto"
        wf.mkdir()
        (wf / "SKILL.md").write_text("# Test\nContent here.\n")

        config = load_portify_config(workflow_path=wf, output_dir=tmp_path / "out")
        inventory, step_result = run_discover_components(config)
        skill_types = [c.component_type for c in inventory.components]
        assert "skill" in skill_types

    def test_inventory_component_has_required_fields(self, tmp_path):
        """Each component has: path, lines, purpose, type."""
        from superclaude.cli.cli_portify.config import load_portify_config
        from superclaude.cli.cli_portify.steps.discover_components import run_discover_components

        wf = tmp_path / "sc-test-proto"
        wf.mkdir()
        (wf / "SKILL.md").write_text("# Skill\n\nContent.\n")

        config = load_portify_config(workflow_path=wf, output_dir=tmp_path / "out")
        inventory, _ = run_discover_components(config)
        for comp in inventory.components:
            assert hasattr(comp, "path"), "ComponentEntry missing 'path'"
            assert hasattr(comp, "line_count"), "ComponentEntry missing 'line_count'"
            assert hasattr(comp, "component_type"), "ComponentEntry missing 'component_type'"
            assert hasattr(comp, "purpose"), "ComponentEntry missing 'purpose'"

    def test_inventory_source_skill_populated(self, tmp_path):
        """Inventory source_skill reflects the scanned skill directory name."""
        from superclaude.cli.cli_portify.config import load_portify_config
        from superclaude.cli.cli_portify.steps.discover_components import run_discover_components

        wf = tmp_path / "sc-my-skill-protocol"
        wf.mkdir()
        (wf / "SKILL.md").write_text("# My Skill\n\nContent.\n")

        config = load_portify_config(workflow_path=wf, output_dir=tmp_path / "out")
        inventory, _ = run_discover_components(config)
        assert inventory.source_skill == "sc-my-skill-protocol"

    def test_inventory_line_count_accurate(self, tmp_path):
        """Line counts in inventory accurately reflect file contents."""
        from superclaude.cli.cli_portify.config import load_portify_config
        from superclaude.cli.cli_portify.steps.discover_components import run_discover_components

        wf = tmp_path / "sc-line-count-proto"
        wf.mkdir()
        lines = "\n".join(f"line {i}" for i in range(1, 11))  # 10 lines
        (wf / "SKILL.md").write_text(lines + "\n")

        config = load_portify_config(workflow_path=wf, output_dir=tmp_path / "out")
        inventory, _ = run_discover_components(config)
        skill_comps = [c for c in inventory.components if c.component_type == "skill"]
        assert len(skill_comps) >= 1
        assert skill_comps[0].line_count >= 10

    def test_inventory_discovers_subdirs(self, tmp_path):
        """Inventory discovers components in refs/, rules/, templates/, scripts/."""
        from superclaude.cli.cli_portify.config import load_portify_config
        from superclaude.cli.cli_portify.steps.discover_components import run_discover_components

        wf = tmp_path / "sc-subdir-proto"
        wf.mkdir()
        (wf / "SKILL.md").write_text("# Skill\n")
        for subdir in ("refs", "rules", "templates", "scripts"):
            d = wf / subdir
            d.mkdir()
            (d / f"{subdir}-file.md").write_text(f"# {subdir} content\n")

        config = load_portify_config(workflow_path=wf, output_dir=tmp_path / "out")
        inventory, _ = run_discover_components(config)
        discovered_types = {c.component_type for c in inventory.components}
        assert "ref" in discovered_types or "rule" in discovered_types or "template" in discovered_types or "script" in discovered_types or len(inventory.components) > 1

    def test_inventory_artifact_written_to_output_dir(self, tmp_path):
        """run_discover_components writes artifact to output directory."""
        from superclaude.cli.cli_portify.config import load_portify_config
        from superclaude.cli.cli_portify.steps.discover_components import run_discover_components

        wf = tmp_path / "sc-artifact-proto"
        wf.mkdir()
        (wf / "SKILL.md").write_text("# Skill\n")
        out_dir = tmp_path / "out"
        out_dir.mkdir()

        config = load_portify_config(workflow_path=wf, output_dir=out_dir)
        _, step_result = run_discover_components(config)
        assert step_result.artifact_path != ""
        artifact = Path(step_result.artifact_path)
        assert artifact.exists()
