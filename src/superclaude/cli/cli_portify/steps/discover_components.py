"""Step 2: discover-components — deterministic component inventory.

Traverses a skill workflow directory to discover and inventory all
components: SKILL.md, refs/, rules/, templates/, scripts/, and
matching command files. Produces component-inventory.md with YAML
frontmatter.

Per SC-002: must complete under 5s for valid skill directories.
Runs without Claude subprocesses.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any

from superclaude.cli.cli_portify.models import (
    AgentEntry,
    CommandEntry,
    ComponentEntry,
    ComponentInventory,
    ComponentTree,
    PortifyConfig,
    PortifyStatus,
    PortifyStepResult,
    ResolvedTarget,
    SkillEntry,
    WARN_MISSING_AGENTS,
)
from superclaude.cli.cli_portify.utils import count_lines

logger = logging.getLogger(__name__)

# Component type constants
COMPONENT_SKILL = "skill"
COMPONENT_REF = "ref"
COMPONENT_RULE = "rule"
COMPONENT_TEMPLATE = "template"
COMPONENT_SCRIPT = "script"
COMPONENT_COMMAND = "command"

# Standard subdirectories to scan
_SUBDIRS: list[tuple[str, str]] = [
    ("refs", COMPONENT_REF),
    ("rules", COMPONENT_RULE),
    ("templates", COMPONENT_TEMPLATE),
    ("scripts", COMPONENT_SCRIPT),
]

# --- 6 AGENT_PATTERNS for agent extraction from SKILL.md ---

# Pattern 1: Backtick-agent notation — `agent-name` in prose (Haiku), (Sonnet)
AGENT_PATTERN_BACKTICK = re.compile(
    r"`([a-z][a-z0-9-]+)`\s*\((?:Haiku|Sonnet|Opus)\)"
)

# Pattern 2: YAML array items — - agent-name (in frontmatter or config blocks)
AGENT_PATTERN_YAML_ARRAY = re.compile(
    r"^[\s-]*\b(audit-[a-z-]+|quality-engineer|[a-z]+-(?:agent|architect|engineer|expert|guide|analyst|writer|executor|orchestrator|validator|scanner|analyzer|comparator|consolidator))\b",
    re.MULTILINE,
)

# Pattern 3: Spawn/delegate/invoke verbs — Spawn agent-name, Delegate to agent-name
AGENT_PATTERN_VERB = re.compile(
    r"(?:spawn|delegate(?:\s+to)?|invoke|dispatch)\s+(?:verification\s+agent\s+\()?([a-z][a-z0-9-]+)\)?"
    , re.IGNORECASE,
)

# Pattern 4: `uses` references — uses: agent-name or uses `agent-name`
AGENT_PATTERN_USES = re.compile(
    r"uses[:\s]+`?([a-z][a-z0-9-]+)`?"
    , re.IGNORECASE,
)

# Pattern 5: Model-parenthetical patterns — agent-name (Haiku|Sonnet|Opus)
AGENT_PATTERN_MODEL_PAREN = re.compile(
    r"\b([a-z][a-z0-9-]+)\s+\((?:Haiku|Sonnet|Opus)\b"
)

# Pattern 6: agents/ path patterns — agents/agent-name or agent_type: agent-name
AGENT_PATTERN_PATH = re.compile(
    r"(?:agents/|agent[_\s]type[:\s]+[`\"']?)([a-z][a-z0-9-]+)"
    , re.IGNORECASE,
)

# All 6 patterns collected
AGENT_PATTERNS: list[re.Pattern[str]] = [
    AGENT_PATTERN_BACKTICK,
    AGENT_PATTERN_YAML_ARRAY,
    AGENT_PATTERN_VERB,
    AGENT_PATTERN_USES,
    AGENT_PATTERN_MODEL_PAREN,
    AGENT_PATTERN_PATH,
]


def run_discover_components(
    config: PortifyConfig,
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
) -> tuple[ComponentInventory, PortifyStepResult]:
    """Execute the discover-components step.

    Args:
        config: Pipeline configuration.
        workflow_path: Resolved workflow path. If None, resolves from config.
        output_dir: Directory for the inventory artifact. Defaults to
            config.results_dir.

    Returns:
        Tuple of (ComponentInventory, PortifyStepResult).
    """
    start = time.monotonic()

    # Resolve workflow path
    if workflow_path is None:
        wf_path = config.resolve_workflow_path()
    else:
        wf_path = workflow_path

    inventory = ComponentInventory(source_skill=wf_path.name)

    # 1. Discover SKILL.md
    skill_file = wf_path / "SKILL.md"
    if skill_file.exists():
        inventory.components.append(ComponentEntry(
            name="SKILL.md",
            path=str(skill_file),
            component_type=COMPONENT_SKILL,
            line_count=count_lines(skill_file),
        ))

    # 2. Discover subdirectory components
    for subdir_name, component_type in _SUBDIRS:
        subdir = wf_path / subdir_name
        if subdir.is_dir():
            for f in sorted(subdir.iterdir()):
                if f.is_file() and not f.name.startswith("."):
                    inventory.components.append(ComponentEntry(
                        name=f.name,
                        path=str(f),
                        component_type=component_type,
                        line_count=count_lines(f),
                    ))

    # 3. Discover command files (*.md files in workflow dir, excluding SKILL.md)
    for f in sorted(wf_path.iterdir()):
        if (
            f.is_file()
            and f.suffix == ".md"
            and f.name != "SKILL.md"
            and not f.name.startswith(".")
        ):
            inventory.components.append(ComponentEntry(
                name=f.name,
                path=str(f),
                component_type=COMPONENT_COMMAND,
                line_count=count_lines(f),
            ))

    elapsed = time.monotonic() - start

    # Write inventory artifact
    artifact_dir = output_dir or config.results_dir
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / "component-inventory.md"
    artifact_path.write_text(
        _render_inventory(inventory, elapsed),
        encoding="utf-8",
    )

    step_result = PortifyStepResult(
        portify_status=PortifyStatus.PASS,
        step_name="discover-components",
        step_number=2,
        phase=1,
        artifact_path=str(artifact_path),
        gate_tier="STANDARD",
    )

    return inventory, step_result


def _render_inventory(inventory: ComponentInventory, duration: float) -> str:
    """Render ComponentInventory as Markdown with YAML frontmatter."""
    lines = [
        "---",
        f"source_skill: {inventory.source_skill}",
        f"component_count: {inventory.component_count}",
        f"total_lines: {inventory.total_lines}",
        f"duration_seconds: {round(duration, 4)}",
        "---",
        "",
        "# Component Inventory",
        "",
    ]

    if not inventory.components:
        lines.append("No components discovered.")
        return "\n".join(lines) + "\n"

    # Group by type
    by_type: dict[str, list[ComponentEntry]] = {}
    for comp in inventory.components:
        by_type.setdefault(comp.component_type, []).append(comp)

    for comp_type, entries in by_type.items():
        lines.append(f"## {comp_type}")
        lines.append("")
        lines.append("| Name | Lines | Path |")
        lines.append("|------|-------|------|")
        for entry in entries:
            lines.append(f"| {entry.name} | {entry.line_count} | {entry.path} |")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_enriched_inventory(
    tree: ComponentTree,
    duration: float,
    resolution_log: dict[str, object] | None = None,
) -> str:
    """Render enriched component-inventory.md from a ComponentTree.

    Produces Markdown with 8 YAML frontmatter fields, Command section,
    Agents table, Cross-Tier Data Flow section, and Resolution Log.

    Args:
        tree: Populated ComponentTree with command, skill, and agents.
        duration: Discovery duration in seconds.
        resolution_log: Optional consolidation log from directory resolution.

    Returns:
        Complete Markdown string with frontmatter and all sections.
    """
    cmd_name = tree.command.name if tree.command else ""
    skill_name = tree.skill.name if tree.skill else ""

    lines = [
        "---",
        f"source_command: {cmd_name}",
        f"source_skill: {skill_name}",
        f"component_count: {tree.component_count}",
        f"total_lines: {tree.total_lines}",
        f"agent_count: {len(tree.agents)}",
        f"has_command: {tree.command is not None}".lower(),
        f"has_skill: {tree.skill is not None}".lower(),
        f"duration_seconds: {round(duration, 4)}",
        "---",
        "",
        "# Component Inventory",
        "",
    ]

    # Command section (Tier 0)
    if tree.command is not None:
        lines.append("## Command (Tier 0)")
        lines.append("")
        lines.append(f"- **Name**: {tree.command.name}")
        lines.append(f"- **Path**: {tree.command.path}")
        lines.append(f"- **Lines**: {tree.command.line_count}")
        if tree.command.source_dir:
            lines.append(f"- **Source Dir**: {tree.command.source_dir}")
        lines.append("")

    # Skill section (Tier 1)
    if tree.skill is not None:
        lines.append("## Skill (Tier 1)")
        lines.append("")
        lines.append(f"- **Name**: {tree.skill.name}")
        lines.append(f"- **Path**: {tree.skill.path}")
        lines.append(f"- **Lines**: {tree.skill.line_count}")
        if tree.skill.source_dir:
            lines.append(f"- **Source Dir**: {tree.skill.source_dir}")
        lines.append("")

    # Agents table (Tier 2)
    if tree.agents:
        lines.append("## Agents (Tier 2)")
        lines.append("")
        lines.append("| Name | Source | Found |")
        lines.append("|------|--------|-------|")
        for agent in tree.agents:
            source = str(agent.source_dir) if agent.source_dir else "N/A"
            found_str = "yes" if agent.found else "**NO**"
            lines.append(f"| {agent.name} | {source} | {found_str} |")
        lines.append("")

    # Cross-Tier Data Flow
    lines.append("## Cross-Tier Data Flow")
    lines.append("")
    flow_parts = []
    if tree.command:
        flow_parts.append(f"Command ({tree.command.name})")
    if tree.skill:
        flow_parts.append(f"Skill ({tree.skill.name})")
    if tree.agents:
        agent_names = ", ".join(a.name for a in tree.agents)
        flow_parts.append(f"Agents ({agent_names})")
    if flow_parts:
        lines.append(" -> ".join(flow_parts))
    else:
        lines.append("No components discovered.")
    lines.append("")

    # Resolution Log
    lines.append("## Resolution Log")
    lines.append("")
    if resolution_log:
        for key, value in resolution_log.items():
            lines.append(f"- **{key}**: {value}")
    else:
        lines.append("No consolidation applied.")
    lines.append("")

    return "\n".join(lines) + "\n"


# --- Agent Extraction ---

# Names to exclude from agent extraction (common false positives)
_AGENT_EXCLUDE = frozenset({
    "sub-agent",
    "subagent",
    "agent-name",
    "agent-type",
    "multi-agent",
})


def extract_agents(
    skill_content: str,
    agents_dir: Path | None = None,
) -> list[AgentEntry]:
    """Extract agent references from SKILL.md content using all 6 AGENT_PATTERNS.

    Args:
        skill_content: Text content of a SKILL.md file.
        agents_dir: Directory containing agent .md files for existence checks.

    Returns:
        List of AgentEntry with found=True/False based on agents_dir lookup.
    """
    seen: set[str] = set()
    agents: list[AgentEntry] = []

    for pattern in AGENT_PATTERNS:
        for match in pattern.finditer(skill_content):
            name = match.group(1).strip().lower()
            if not name or name in seen or name in _AGENT_EXCLUDE:
                continue
            # Basic sanity: must be at least 3 chars and contain a hyphen
            if len(name) < 3 or "-" not in name:
                continue
            seen.add(name)

            # Check if agent file exists
            agent_path: Path | None = None
            found = False
            if agents_dir is not None:
                candidate = agents_dir / f"{name}.md"
                if candidate.exists() and candidate.is_file():
                    agent_path = candidate
                    found = True

            line_count = 0
            source_dir: Path | None = None
            if agent_path is not None:
                try:
                    line_count = len(agent_path.read_text(encoding="utf-8").splitlines())
                except OSError:
                    line_count = 0
                source_dir = agents_dir

            entry = AgentEntry(
                name=name,
                path=agent_path,
                line_count=line_count,
                source_dir=source_dir,
                found=found,
                referenced_in="auto",
            )
            if not found:
                logger.warning(
                    "%s: agent '%s' referenced but not found in %s",
                    WARN_MISSING_AGENTS,
                    name,
                    agents_dir,
                )
            agents.append(entry)

    return agents


def deduplicate_agents(
    auto_agents: list[AgentEntry],
    cli_agents: list[str],
    agents_dir: Path | None = None,
) -> list[AgentEntry]:
    """Merge CLI-override agents with auto-discovered agents.

    CLI-override agents (referenced_in="cli-override") take precedence
    over auto-discovered agents with the same name.

    Args:
        auto_agents: Agents discovered from SKILL.md.
        cli_agents: Agent names from --include-agent CLI option.
        agents_dir: Directory containing agent .md files.

    Returns:
        Merged and deduplicated list of AgentEntry.
    """
    if not cli_agents:
        return auto_agents

    # Build lookup of auto-discovered agents
    auto_by_name: dict[str, AgentEntry] = {a.name: a for a in auto_agents}

    result: list[AgentEntry] = []
    cli_names: set[str] = set()

    for name in cli_agents:
        name = name.strip().lower()
        if not name:
            continue
        cli_names.add(name)

        # Check if agent file exists
        agent_path: Path | None = None
        found = False
        line_count = 0
        source_dir: Path | None = None
        if agents_dir is not None:
            candidate = agents_dir / f"{name}.md"
            if candidate.exists() and candidate.is_file():
                agent_path = candidate
                found = True
                try:
                    line_count = len(candidate.read_text(encoding="utf-8").splitlines())
                except OSError:
                    line_count = 0
                source_dir = agents_dir

        result.append(AgentEntry(
            name=name,
            path=agent_path,
            line_count=line_count,
            source_dir=source_dir,
            found=found,
            referenced_in="cli-override",
        ))

    # Add auto-discovered agents that weren't overridden
    for agent in auto_agents:
        if agent.name not in cli_names:
            result.append(agent)

    return result


def build_component_tree(resolved: ResolvedTarget) -> ComponentTree:
    """Assemble a ComponentTree from a ResolvedTarget.

    Populates command (Tier 0), skill (Tier 1), and agents (Tier 2)
    by reading resolved paths and extracting agent references from SKILL.md.

    Args:
        resolved: A ResolvedTarget with resolved paths.

    Returns:
        ComponentTree with populated fields.
    """
    tree = ComponentTree()

    # Tier 0: Command
    if resolved.command_path is not None and resolved.command_path.exists():
        try:
            lc = len(resolved.command_path.read_text(encoding="utf-8").splitlines())
        except OSError:
            lc = 0
        tree.command = CommandEntry(
            name=resolved.command_path.stem,
            path=resolved.command_path,
            line_count=lc,
            source_dir=resolved.command_path.parent,
        )

    # Tier 1: Skill
    if resolved.skill_dir is not None and resolved.skill_dir.is_dir():
        skill_file = resolved.skill_dir / "SKILL.md"
        lc = 0
        if skill_file.exists():
            try:
                lc = len(skill_file.read_text(encoding="utf-8").splitlines())
            except OSError:
                lc = 0
        tree.skill = SkillEntry(
            name=resolved.skill_dir.name,
            path=skill_file if skill_file.exists() else resolved.skill_dir,
            line_count=lc,
            source_dir=resolved.skill_dir,
        )

        # Tier 2: Agents — extract from SKILL.md content
        if skill_file.exists():
            try:
                skill_content = skill_file.read_text(encoding="utf-8")
            except OSError:
                skill_content = ""
            tree.agents = extract_agents(skill_content, resolved.agents_dir)

    return tree
