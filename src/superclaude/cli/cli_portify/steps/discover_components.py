"""Step 2: discover-components — deterministic component inventory (Step 1).

Scans the workflow skill directory and related directories to produce a
component-inventory.md artifact. No Claude subprocess required.

Enforces SC-002: completes in <60s (in practice <5s for filesystem scans).

Component types:
  COMPONENT_SKILL    — SKILL.md in skill directory
  COMPONENT_COMMAND  — command .md files (top-level, not SKILL.md)
  COMPONENT_REF      — files in refs/ subdirectory
  COMPONENT_RULE     — files in rules/ subdirectory
  COMPONENT_TEMPLATE — files in templates/ subdirectory
  COMPONENT_SCRIPT   — files in scripts/ subdirectory
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Optional

from ..models import (
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
from ..utils import count_lines, parse_frontmatter

log = logging.getLogger(__name__)

# Component type constants
COMPONENT_SKILL: str = "skill"
COMPONENT_COMMAND: str = "command"
COMPONENT_REF: str = "ref"
COMPONENT_RULE: str = "rule"
COMPONENT_TEMPLATE: str = "template"
COMPONENT_SCRIPT: str = "script"

STEP_NAME = "discover-components"
STEP_NUMBER = 2
PHASE = 1
GATE_TIER = "STANDARD"

# ---------------------------------------------------------------------------
# Agent extraction patterns (6 patterns)
# ---------------------------------------------------------------------------

# Pattern 1: Backtick-agent notation with optional model parenthetical
# e.g. `audit-scanner` (Haiku)
AGENT_PATTERN_BACKTICK = re.compile(
    r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`(?:\s*\([^)]+\))?",
    re.IGNORECASE,
)

# Pattern 2: YAML array items
# e.g. - quality-engineer
AGENT_PATTERN_YAML_ARRAY = re.compile(
    r"^\s*-\s+([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# Pattern 3: Spawn / delegate / dispatch / invoke verbs
# e.g. Spawn verification agent (backend-architect)
# e.g. Delegate to performance-engineer
# Uses lookahead approach with single capture group for the agent name.
# Captures name from: (1) parenthetical form, or (2) direct bare word.
# We run 2 sub-patterns and combine them in extract_agents.
_AGENT_VERB_PAREN = re.compile(
    r"(?:spawn|delegate(?:\s+to)?|dispatch|invoke)(?:\s+\w+)*\s+\(([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\)",
    re.IGNORECASE,
)
_AGENT_VERB_BARE = re.compile(
    r"(?:spawn|delegate(?:\s+to)?|dispatch|invoke)\s+(?:to\s+)?([a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?:\s+(?:agent|for))?",
    re.IGNORECASE,
)


class _VerbPattern:
    """Composite of 2 single-group patterns; findall returns flat strings."""

    def __init__(self) -> None:
        self._paren = _AGENT_VERB_PAREN
        self._bare = _AGENT_VERB_BARE

    def findall(self, text: str) -> list[str]:
        results = self._paren.findall(text) + self._bare.findall(text)
        return results

    def finditer(self, text: str):
        import itertools
        return itertools.chain(
            self._paren.finditer(text),
            self._bare.finditer(text),
        )


AGENT_PATTERN_VERB = _VerbPattern()

# Pattern 4: Uses references
# e.g. uses: `deep-research-agent`
AGENT_PATTERN_USES = re.compile(
    r"uses:\s*`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`",
    re.IGNORECASE,
)

# Pattern 5: Model-parenthetical (agent-name (Model))
# e.g. audit-validator (Sonnet)
AGENT_PATTERN_MODEL_PAREN = re.compile(
    r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\s+\((?:Haiku|Sonnet|Opus|Claude)[^)]*\)",
    re.IGNORECASE,
)

# Pattern 6: agents/ path references OR "Agent type:" prefix
# e.g. agents/frontend-architect
# e.g. Agent type: `merge-executor`
_AGENT_PATH_AGENTS = re.compile(
    r"agents/([a-z][a-z0-9]*(?:-[a-z0-9]+)+)",
    re.IGNORECASE,
)
_AGENT_PATH_TYPE = re.compile(
    r"[Aa]gent\s+type:\s*`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`",
    re.IGNORECASE,
)


class _PathPattern:
    """Composite of 2 single-group path patterns; findall returns flat strings."""

    def __init__(self) -> None:
        self._agents = _AGENT_PATH_AGENTS
        self._type = _AGENT_PATH_TYPE

    def findall(self, text: str) -> list[str]:
        return self._agents.findall(text) + self._type.findall(text)

    def finditer(self, text: str):
        import itertools
        return itertools.chain(
            self._agents.finditer(text),
            self._type.finditer(text),
        )


AGENT_PATTERN_PATH = _PathPattern()

AGENT_PATTERNS = [
    AGENT_PATTERN_BACKTICK,
    AGENT_PATTERN_YAML_ARRAY,
    _AGENT_VERB_PAREN,
    AGENT_PATTERN_USES,
    AGENT_PATTERN_MODEL_PAREN,
    _AGENT_PATH_AGENTS,
]

# False-positive filter: names that look like agents but aren't
_FALSE_POSITIVES = frozenset({"sub-agent", "multi-agent", "re-run", "step-by-step"})


def extract_agents(
    content: str,
    agents_dir: Optional[Path],
) -> list[AgentEntry]:
    """Extract agent references from SKILL.md content using all 6 patterns.

    Each discovered agent name is checked against agents_dir for existence.
    Returns deduplicated list; logs WARN_MISSING_AGENTS for each not found.

    False positives (sub-agent, multi-agent, etc.) are filtered out.
    """
    raw_names: list[str] = []

    # All compiled patterns (single-group)
    all_patterns = [
        AGENT_PATTERN_BACKTICK,
        AGENT_PATTERN_YAML_ARRAY,
        _AGENT_VERB_PAREN,
        _AGENT_VERB_BARE,
        AGENT_PATTERN_USES,
        AGENT_PATTERN_MODEL_PAREN,
        _AGENT_PATH_AGENTS,
        _AGENT_PATH_TYPE,
    ]

    for pattern in all_patterns:
        for match in pattern.finditer(content):
            # Single capture group → match.group(1)
            name = match.group(1) if match.lastindex and match.lastindex >= 1 else None
            if name:
                raw_names.append(name.lower())

    # Deduplicate preserving first-occurrence order, filter false positives
    seen: set[str] = set()
    unique_names: list[str] = []
    for name in raw_names:
        if name not in seen and name not in _FALSE_POSITIVES:
            seen.add(name)
            unique_names.append(name)

    agents: list[AgentEntry] = []
    for name in unique_names:
        agent_path: Optional[Path] = None
        found = False
        line_count = 0

        if agents_dir is not None and agents_dir.exists():
            # Try exact match first, then with .md extension
            candidate = agents_dir / f"{name}.md"
            if candidate.exists():
                agent_path = candidate
                found = True
                line_count = count_lines(candidate)
            else:
                # Also try without extension (directory-style agent)
                candidate_dir = agents_dir / name
                if candidate_dir.exists():
                    agent_path = candidate_dir
                    found = True

        if not found:
            log.warning(
                "%s: agent '%s' referenced in SKILL.md but not found in agents dir",
                WARN_MISSING_AGENTS,
                name,
            )

        agents.append(
            AgentEntry(
                name=name,
                path=agent_path,
                line_count=line_count,
                source_dir=agents_dir,
                found=found,
                referenced_in="auto",
            )
        )

    return agents


def deduplicate_agents(
    auto_agents: list[AgentEntry],
    cli_override_names: list[str],
    agents_dir: Optional[Path],
) -> list[AgentEntry]:
    """Merge auto-discovered and CLI-override agents.

    CLI-override names take precedence: they replace auto entries with the
    same name (changing referenced_in to 'cli-override'). New CLI-specified
    agents not in auto list are appended.
    """
    # Filter empty/whitespace names
    override_names = [n.strip() for n in cli_override_names if n.strip()]

    if not override_names:
        return list(auto_agents)

    # Build lookup from auto
    auto_by_name: dict[str, AgentEntry] = {a.name: a for a in auto_agents}

    result: list[AgentEntry] = []

    # Start with auto agents not overridden
    for agent in auto_agents:
        if agent.name not in override_names:
            result.append(agent)

    # Add/replace from CLI overrides
    for name in override_names:
        agent_path: Optional[Path] = None
        found = False
        line_count = 0

        if agents_dir is not None and agents_dir.exists():
            candidate = agents_dir / f"{name}.md"
            if candidate.exists():
                agent_path = candidate
                found = True
                line_count = count_lines(candidate)

        result.append(
            AgentEntry(
                name=name,
                path=agent_path,
                line_count=line_count,
                source_dir=agents_dir,
                found=found,
                referenced_in="cli-override",
            )
        )

    return result


def build_component_tree(resolved: ResolvedTarget) -> ComponentTree:
    """Build a ComponentTree from a ResolvedTarget.

    Populates:
      - command: from resolved.command_path
      - skill: from resolved.skill_dir (reads SKILL.md for agent extraction)
      - agents: extracted from SKILL.md content + available in resolved.agents_dir
    """
    command: Optional[CommandEntry] = None
    skill: Optional[SkillEntry] = None
    agents: list[AgentEntry] = []

    # Command entry
    if resolved.command_path is not None and resolved.command_path.exists():
        command = CommandEntry(
            name=resolved.command_path.stem,
            path=resolved.command_path,
            line_count=count_lines(resolved.command_path),
            source_dir=resolved.command_path.parent,
        )

    # Skill entry + agent extraction
    if resolved.skill_dir is not None and resolved.skill_dir.exists():
        skill_md = resolved.skill_dir / "SKILL.md"
        line_count = count_lines(skill_md) if skill_md.exists() else 0
        skill = SkillEntry(
            name=resolved.skill_dir.name,
            path=skill_md if skill_md.exists() else resolved.skill_dir,
            line_count=line_count,
            source_dir=resolved.skill_dir,
        )

        # Extract agents from SKILL.md content
        if skill_md.exists():
            content = skill_md.read_text(errors="replace")
            agents = extract_agents(content, resolved.agents_dir)

    return ComponentTree(command=command, skill=skill, agents=agents)


# ---------------------------------------------------------------------------
# Directory scanner
# ---------------------------------------------------------------------------

def _scan_skill_dir(workflow_dir: Path) -> list[ComponentEntry]:
    """Scan a skill directory and return all component entries.

    Scans:
      - SKILL.md → type=skill
      - refs/     → type=ref
      - rules/    → type=rule
      - templates/ → type=template
      - scripts/  → type=script
      - top-level .md files (not SKILL.md) → type=command
    """
    components: list[ComponentEntry] = []

    # SKILL.md
    skill_md = workflow_dir / "SKILL.md"
    if skill_md.exists():
        components.append(
            ComponentEntry(
                name="SKILL.md",
                path=str(skill_md),
                component_type=COMPONENT_SKILL,
                line_count=count_lines(skill_md),
                purpose="skill definition",
            )
        )

    # Subdirectories
    subdir_type_map = {
        "refs": COMPONENT_REF,
        "rules": COMPONENT_RULE,
        "templates": COMPONENT_TEMPLATE,
        "scripts": COMPONENT_SCRIPT,
    }
    for subdir_name, comp_type in subdir_type_map.items():
        subdir = workflow_dir / subdir_name
        if subdir.is_dir():
            for f in sorted(subdir.iterdir()):
                if f.is_file():
                    components.append(
                        ComponentEntry(
                            name=f.name,
                            path=str(f),
                            component_type=comp_type,
                            line_count=count_lines(f),
                            purpose=f"{comp_type} file",
                        )
                    )

    # Top-level .md command files (not SKILL.md)
    for f in sorted(workflow_dir.iterdir()):
        if f.is_file() and f.suffix == ".md" and f.name != "SKILL.md":
            components.append(
                ComponentEntry(
                    name=f.name,
                    path=str(f),
                    component_type=COMPONENT_COMMAND,
                    line_count=count_lines(f),
                    purpose="command file",
                )
            )

    return components


# ---------------------------------------------------------------------------
# Inventory artifact rendering
# ---------------------------------------------------------------------------

def render_enriched_inventory(
    tree: ComponentTree,
    duration_seconds: float,
    resolution_log: Optional[dict] = None,
) -> str:
    """Render an enriched component-inventory.md Markdown document.

    Frontmatter contains 8 fields:
      source_command, source_skill, component_count, total_lines,
      agent_count, has_command, has_skill, duration_seconds

    Sections:
      ## Command (Tier 0)     — if tree.command is not None
      ## Skill (Tier 1)       — if tree.skill is not None
      ## Agents (Tier 2)      — if tree.agents is non-empty
      ## Cross-Tier Data Flow
      ## Resolution Log
    """
    source_command = tree.command.name if tree.command else ""
    source_skill = tree.skill.name if tree.skill else ""
    agent_count = len(tree.agents)
    has_command = tree.command is not None
    has_skill = tree.skill is not None

    lines = [
        "---",
        f"source_command: {source_command}",
        f"source_skill: {source_skill}",
        f"component_count: {tree.component_count}",
        f"total_lines: {tree.total_lines}",
        f"agent_count: {agent_count}",
        f"has_command: {str(has_command).lower()}",
        f"has_skill: {str(has_skill).lower()}",
        f"duration_seconds: {duration_seconds}",
        "---",
        "",
    ]

    if tree.component_count == 0:
        lines.append("No components discovered.")
    else:
        # Command section
        if tree.command is not None:
            lines += [
                "## Command (Tier 0)",
                f"- **{tree.command.name}** ({tree.command.line_count} lines)",
                f"  - Path: `{tree.command.path}`",
                "",
            ]

        # Skill section
        if tree.skill is not None:
            lines += [
                "## Skill (Tier 1)",
                f"- **{tree.skill.name}** ({tree.skill.line_count} lines)",
                f"  - Path: `{tree.skill.path}`",
                "",
            ]

        # Agents section
        if tree.agents:
            lines += ["## Agents (Tier 2)", ""]
            lines += ["| Agent | Lines | Found | Referenced In |", "| --- | --- | --- | --- |"]
            for agent in tree.agents:
                found_str = "**YES**" if agent.found else "**NO**"
                lines.append(
                    f"| {agent.name} | {agent.line_count} | {found_str} | {agent.referenced_in} |"
                )
            lines.append("")

        # Cross-Tier Data Flow section
        lines += ["## Cross-Tier Data Flow", ""]
        flow_parts = []
        if tree.command:
            flow_parts.append(f"Command ({tree.command.name})")
        if tree.skill:
            flow_parts.append(f"Skill ({tree.skill.name})")
        if tree.agents:
            agent_names = ", ".join(a.name for a in tree.agents)
            flow_parts.append(f"Agents ({agent_names})")
        lines.append(" → ".join(flow_parts) if flow_parts else "No data flow.")
        lines.append("")

        # Resolution Log section
        lines += ["## Resolution Log", ""]
        if resolution_log:
            for k, v in resolution_log.items():
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append("No consolidation applied.")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# run_discover_components (Step 2 entrypoint)
# ---------------------------------------------------------------------------

def run_discover_components(
    config: PortifyConfig,
) -> tuple[ComponentInventory, PortifyStepResult]:
    """Execute the discover-components step.

    Returns:
        (ComponentInventory, PortifyStepResult) tuple.

    Does not invoke Claude. All scanning is pure Python filesystem operations.
    Enforces SC-002: <60s timeout (measured, not enforced here — executor handles).
    """
    start = time.monotonic()

    # Resolve workflow directory
    workflow_dir = config.resolve_workflow_path()
    source_skill = workflow_dir.name

    # Scan the workflow directory for all components
    components = _scan_skill_dir(workflow_dir)

    inventory = ComponentInventory(
        components=components,
        source_skill=source_skill,
        source_command="",
    )

    elapsed = time.monotonic() - start

    # Determine output directory for artifact
    out_dir = config.output_dir or workflow_dir.parent

    # Render and write artifact
    # Build a simple ComponentTree for the enriched render
    tree = _build_simple_tree(workflow_dir, config)
    md_content = _render_simple_inventory(inventory, source_skill, elapsed)
    artifact_path = _write_inventory_artifact(md_content, out_dir)

    step_result = PortifyStepResult(
        step_name=STEP_NAME,
        step_number=STEP_NUMBER,
        phase=PHASE,
        portify_status=PortifyStatus.PASS,
        gate_tier=GATE_TIER,
        artifact_path=str(artifact_path),
        duration_seconds=elapsed,
    )

    return inventory, step_result


def _build_simple_tree(workflow_dir: Path, config: PortifyConfig) -> ComponentTree:
    """Build a minimal ComponentTree for the inventory artifact."""
    skill_md = workflow_dir / "SKILL.md"
    skill: Optional[SkillEntry] = None
    if skill_md.exists():
        skill = SkillEntry(
            name=workflow_dir.name,
            path=skill_md,
            line_count=count_lines(skill_md),
            source_dir=workflow_dir,
        )
    return ComponentTree(skill=skill)


def _render_simple_inventory(
    inventory: ComponentInventory,
    source_skill: str,
    duration_seconds: float,
) -> str:
    """Render a simple component-inventory.md with YAML frontmatter."""
    lines = [
        "---",
        f"source_skill: {source_skill}",
        f"component_count: {inventory.component_count}",
        f"total_lines: {inventory.total_lines}",
        f"duration_seconds: {duration_seconds:.4f}",
        "---",
        "",
        f"# Component Inventory: {source_skill}",
        "",
    ]

    if inventory.component_count == 0:
        lines.append("No components discovered.")
    else:
        lines += [
            "| Component | Type | Lines |",
            "| --- | --- | --- |",
        ]
        for comp in inventory.components:
            lines.append(f"| {comp.name} | {comp.component_type} | {comp.line_count} |")
        lines.append("")

    return "\n".join(lines)


def _write_inventory_artifact(content: str, out_dir: Path) -> Path:
    """Write component-inventory.md to the output directory."""
    import tempfile
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        artifact = out_dir / "component-inventory.md"
        artifact.write_text(content)
        return artifact
    except OSError:
        tmp_dir = Path(tempfile.mkdtemp())
        artifact = tmp_dir / "component-inventory.md"
        artifact.write_text(content)
        return artifact
