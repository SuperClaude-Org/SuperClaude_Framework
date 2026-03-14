# Synthesized Spec: Command-Centric Resolution with Manifest Output

**Status**: FINAL SPEC (post-adversarial debate)
**Version**: v2.24.1-cli-portify-cli-v5
**Date**: 2026-03-13
**Base**: Approach A (Command-Centric Resolution)
**Incorporated from Approach B**: Resolution log artifact, `--include-agent`, `--save-manifest`

---

## 1. Problem Statement

The `superclaude cli-portify run` command has three design gaps that prevent it from portifying complete SuperClaude workflows:

| Gap | Current Behavior | Required Behavior |
|-----|-----------------|-------------------|
| **Gap 1: Input Target** | Accepts only a skill directory path containing `SKILL.md` | Accept a command name, command path, or skill path and resolve the full component tree |
| **Gap 2: Discovery** | Inventories only `SKILL.md` + subdirs within skill dir | Discover the command file, all referenced agents, and cross-directory data flows |
| **Gap 3: Subprocess Scoping** | `--add-dir` for `work_dir` + `workflow_path` only | Scope `commands/` and `agents/` directories so Claude subprocesses can read all components |

These gaps cause the portification analysis to operate on an incomplete picture of the workflow, producing incorrect or incomplete pipeline specifications.

---

## 2. Solution Overview

The solution makes the **command** the primary entry point while retaining backward compatibility with skill-directory input. The system resolves the entire component tree automatically using a deterministic, pure-Python resolution algorithm that runs in under 1 second.

### Architecture

```
User Input ("roadmap")
    |
    v
resolve_target()          -- pure Python, <1s
    |
    v
ResolvedTarget            -- normalized input
    |
    v
build_component_tree()    -- pure Python, filesystem reads only
    |
    v
ComponentTree             -- full Tier 0/1/2 hierarchy (in-memory)
    |
    +---> component-inventory.md artifact (enriched with command, agents, data flow)
    +---> workflow-manifest.md artifact (optional, via --save-manifest)
    +---> PortifyProcess.additional_dirs (for --add-dir scoping)
    +---> tree.to_flat_inventory() (backward-compatible bridge)
```

### Key Design Decisions

1. **Command-first, skill-fallback**: Primary input is a command name or path. Skill directory paths remain supported and trigger backward-resolution.
2. **In-memory ComponentTree**: Resolution produces an in-memory tree, not a persistent manifest. The tree is optionally serialized via `--save-manifest` for debugging.
3. **No new pipeline step**: Resolution runs within the existing Step 1 (validate-config) or as a pre-step in the CLI handler. Step numbering is unchanged.
4. **Deterministic resolution**: All resolution logic is pure Python with no Claude subprocess involvement.
5. **Escape hatches**: `--include-agent` allows manual agent injection when heuristics miss references.

---

## 3. Detailed Design

### 3.1 Input Model (Gap 1)

#### 3.1.1 Input Acceptance

The `run` subcommand accepts a `TARGET` positional argument:

| Input Form | Example | Resolution Strategy |
|-----------|---------|---------------------|
| Bare command name | `roadmap` | Search `commands/` dir for `roadmap.md` |
| Command name with prefix | `sc:roadmap` | Strip `sc:`, search `commands/` for `roadmap.md` |
| Command file path | `src/superclaude/commands/roadmap.md` | Use directly |
| Skill directory path | `src/superclaude/skills/sc-roadmap-protocol/` | Backward-resolve command |
| Skill directory name | `sc-roadmap-protocol` | Find in `skills/`, backward-resolve command |
| SKILL.md path | `.../sc-roadmap-protocol/SKILL.md` | Use parent as skill dir, backward-resolve |

#### 3.1.2 CLI Interface Change

```python
# BEFORE (v2.24):
@click.argument("workflow_path", type=click.Path(exists=True))

# AFTER (v2.24.1):
@click.argument("target")  # No exists=True -- resolution handles validation
@click.option(
    "--commands-dir",
    default=None,
    type=click.Path(exists=True),
    help="Override commands directory (default: auto-detect)",
)
@click.option(
    "--skills-dir",
    default=None,
    type=click.Path(exists=True),
    help="Override skills directory (default: auto-detect)",
)
@click.option(
    "--agents-dir",
    default=None,
    type=click.Path(exists=True),
    help="Override agents directory (default: auto-detect)",
)
@click.option(
    "--include-agent",
    multiple=True,
    help="Include additional agent(s) not auto-discovered (by name or path)",
)
@click.option(
    "--save-manifest",
    type=click.Path(),
    default=None,
    help="Save the resolved component tree as a manifest file for debugging",
)
```

The three `--*-dir` options default to auto-detection. Auto-detection algorithm:

1. If `target` is an absolute or relative path, derive project root by walking up to find `src/superclaude/` or `pyproject.toml`.
2. If `target` is a bare name, search known locations: `src/superclaude/commands/`, `.claude/commands/sc/`.
3. Fall back to CWD-relative paths.

#### 3.1.3 Input Normalization

A new function `resolve_target()` in `resolution.py` normalizes any input form into a `ResolvedTarget`:

```python
@dataclass
class ResolvedTarget:
    """Normalized target after input resolution."""
    input_form: str                    # What the user typed
    input_type: TargetInputType        # Enum classification
    command_path: Path | None          # Resolved Tier 0 command file
    skill_dir: Path | None             # Resolved Tier 1 skill directory
    project_root: Path                 # Detected project root
    commands_dir: Path                 # Resolved commands directory
    skills_dir: Path                   # Resolved skills directory
    agents_dir: Path                   # Resolved agents directory


class TargetInputType(Enum):
    COMMAND_NAME = "command_name"       # bare name like "roadmap"
    COMMAND_PATH = "command_path"       # path to .md file in commands/
    SKILL_DIR = "skill_dir"            # path to skill directory
    SKILL_NAME = "skill_name"          # bare name like "sc-roadmap-protocol"
    SKILL_FILE = "skill_file"          # path to SKILL.md
```

### 3.2 Resolution Algorithm (Gap 2)

The resolution algorithm runs in 5 deterministic steps. All steps are pure Python filesystem operations.

**Step R1: Resolve Command**

If `input_type` is `COMMAND_NAME` or `COMMAND_PATH`:
- Locate the command `.md` file in `commands_dir`
- Parse its YAML frontmatter for `name`, `category`, `complexity`, `allowed-tools`, `mcp-servers`, `personas`
- Parse the `## Activation` section for the skill reference pattern: `Skill sc:<name>-protocol`
- Extract the skill name from the activation directive

If `input_type` is `SKILL_DIR`, `SKILL_NAME`, or `SKILL_FILE`:
- Reverse-resolve the command: take skill dir name, strip `sc-` prefix and `-protocol` suffix, search `commands_dir` for `<name>.md`
- If no command found, record `command_path = None` (valid edge case: standalone skills)

**Step R2: Resolve Skill**

From the skill name extracted in R1 (or from the input if skill-based):
- Construct expected directory name: `sc-<name>-protocol`
- Locate in `skills_dir`
- Validate `SKILL.md` exists within the directory

**Step R3: Parse Skill for Agent References**

Read `SKILL.md` and extract agent references using these patterns:

```python
AGENT_PATTERNS = [
    r'`(\w[\w-]+)`\s+(?:agent|Agent)',           # `audit-scanner` agent
    r'agent[s]?\s*:\s*\[([^\]]+)\]',             # agents: [name1, name2]
    r'(?:spawn|delegate|invoke)\s+(\w[\w-]+)',    # spawn audit-scanner
    r'uses?\s+`(\w[\w-]+)`',                     # uses `audit-scanner`
    r'(\w[\w-]+)\s+\((?:Haiku|Sonnet|Opus)',      # audit-scanner (Haiku,
    r'agents/(\w[\w-]+)\.md',                    # agents/audit-scanner.md (from Approach B)
]
```

For each extracted agent name:
- Resolve to `agents_dir/<name>.md`
- Record whether the agent file was found or is referenced-but-missing
- Deduplicate by name

Additionally, inject any agents specified via `--include-agent` CLI option. These are resolved the same way: if a bare name, look up in `agents_dir`; if a path, use directly.

**Step R4: Inventory Tier 2 Components**

Within the skill directory, scan subdirectories:

| Subdirectory | Component Type | Scanned |
|-------------|---------------|---------|
| `refs/` | `ref` | All `.md` files |
| `rules/` | `rule` | All files |
| `templates/` | `template` | All files |
| `scripts/` | `script` | All files |

This step is identical to the current `discover_components.py` subdirectory scan.

**Step R5: Build ComponentTree**

Assemble all discovered components into a `ComponentTree` (see Section 3.3).

### 3.3 ComponentTree Data Model

```python
@dataclass
class AgentEntry:
    """An agent referenced by the workflow."""
    name: str
    path: Path | None           # None if referenced but not found
    line_count: int
    referenced_in: str          # "skill" | "command" | "cli-override"
    delegation_pattern: str     # "parallel" | "sequential" | "unknown"
    found: bool                 # Whether the agent .md file exists


@dataclass
class CommandEntry:
    """The Tier 0 command file."""
    name: str
    path: Path
    line_count: int
    frontmatter: dict           # Parsed YAML frontmatter
    activation_skill: str       # Skill name from ## Activation
    category: str
    complexity: str


@dataclass
class SkillEntry:
    """The Tier 1 skill/protocol."""
    name: str
    path: Path                  # Directory path
    skill_md_path: Path         # Path to SKILL.md
    line_count: int             # Lines in SKILL.md
    frontmatter: dict           # Parsed YAML frontmatter from SKILL.md


@dataclass
class ComponentTree:
    """Full component tree for a SuperClaude workflow.

    Replaces ComponentInventory as the primary discovery model.
    Provides backward-compatible conversion via to_flat_inventory().
    """
    # Tier 0
    command: CommandEntry | None = None

    # Tier 1
    skill: SkillEntry | None = None

    # Tier 2
    refs: list[ComponentEntry] = field(default_factory=list)
    rules: list[ComponentEntry] = field(default_factory=list)
    templates: list[ComponentEntry] = field(default_factory=list)
    scripts: list[ComponentEntry] = field(default_factory=list)

    # Agents
    agents: list[AgentEntry] = field(default_factory=list)

    # Metadata
    resolution_log: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def component_count(self) -> int:
        count = 0
        if self.command:
            count += 1
        if self.skill:
            count += 1
        count += len(self.refs) + len(self.rules)
        count += len(self.templates) + len(self.scripts)
        count += len(self.agents)
        return count

    @property
    def total_lines(self) -> int:
        total = 0
        if self.command:
            total += self.command.line_count
        if self.skill:
            total += self.skill.line_count
        for group in [self.refs, self.rules, self.templates, self.scripts]:
            total += sum(c.line_count for c in group)
        total += sum(a.line_count for a in self.agents if a.found)
        return total

    @property
    def all_source_dirs(self) -> list[Path]:
        """All unique directories containing source components.

        Used by PortifyProcess for --add-dir scoping.
        """
        dirs: set[Path] = set()
        if self.command:
            dirs.add(self.command.path.parent)
        if self.skill:
            dirs.add(self.skill.path)
        for agent in self.agents:
            if agent.path:
                dirs.add(agent.path.parent)
        return sorted(dirs)

    def to_flat_inventory(self) -> ComponentInventory:
        """Backward-compatible conversion to flat ComponentInventory."""
        inventory = ComponentInventory(
            source_skill=self.skill.name if self.skill else "",
        )
        if self.command:
            inventory.components.append(ComponentEntry(
                name=self.command.name,
                path=str(self.command.path),
                component_type="command",
                line_count=self.command.line_count,
            ))
        if self.skill:
            inventory.components.append(ComponentEntry(
                name="SKILL.md",
                path=str(self.skill.skill_md_path),
                component_type="skill",
                line_count=self.skill.line_count,
            ))
        for group, comp_type in [
            (self.refs, "ref"),
            (self.rules, "rule"),
            (self.templates, "template"),
            (self.scripts, "script"),
        ]:
            for entry in group:
                inventory.components.append(entry)
        for agent in self.agents:
            if agent.found:
                inventory.components.append(ComponentEntry(
                    name=agent.name,
                    path=str(agent.path),
                    component_type="agent",
                    line_count=agent.line_count,
                ))
        return inventory

    def to_manifest_markdown(self) -> str:
        """Serialize the tree as a human-readable Markdown manifest.

        Used by --save-manifest for debugging. Format follows
        Approach B's manifest structure for readability.
        """
        lines: list[str] = []
        lines.append("---")
        lines.append(f"workflow_name: {self.command.name if self.command else (self.skill.name if self.skill else 'unknown')}")
        lines.append(f"component_count: {self.component_count}")
        lines.append(f"total_lines: {self.total_lines}")
        lines.append(f"agent_count: {len(self.agents)}")
        lines.append(f"has_command: {self.command is not None}")
        lines.append(f"has_skill: {self.skill is not None}")
        lines.append("---")
        lines.append("")

        # Tier 0
        lines.append("## Tier 0: Command")
        lines.append("")
        if self.command:
            lines.append("| Component | Path | Lines | Purpose |")
            lines.append("|-----------|------|-------|---------|")
            lines.append(f"| {self.command.name} | {self.command.path} | {self.command.line_count} | Entry point, skill dispatch |")
        else:
            lines.append("(no command resolved)")
        lines.append("")

        # Tier 1
        lines.append("## Tier 1: Skill")
        lines.append("")
        if self.skill:
            lines.append("| Component | Path | Lines |")
            lines.append("|-----------|------|-------|")
            lines.append(f"| SKILL.md | {self.skill.skill_md_path} | {self.skill.line_count} |")
        else:
            lines.append("(no skill resolved)")
        lines.append("")

        # Refs, Rules, Templates, Scripts
        for section_name, entries in [
            ("Refs", self.refs),
            ("Rules", self.rules),
            ("Templates", self.templates),
            ("Scripts", self.scripts),
        ]:
            lines.append(f"### {section_name}")
            lines.append("")
            if entries:
                lines.append("| Component | Path | Lines |")
                lines.append("|-----------|------|-------|")
                for e in entries:
                    lines.append(f"| {e.name} | {e.path} | {e.line_count} |")
            else:
                lines.append(f"(none)")
            lines.append("")

        # Agents
        lines.append("## Tier 2: Agents")
        lines.append("")
        if self.agents:
            lines.append("| Agent | Path | Lines | Pattern | Source | Found |")
            lines.append("|-------|------|-------|---------|--------|-------|")
            for a in self.agents:
                lines.append(
                    f"| {a.name} | {a.path or 'NOT FOUND'} | {a.line_count} "
                    f"| {a.delegation_pattern} | {a.referenced_in} | {a.found} |"
                )
        else:
            lines.append("(no agents referenced)")
        lines.append("")

        # Resolution Log
        lines.append("## Resolution Log")
        lines.append("")
        for i, entry in enumerate(self.resolution_log, 1):
            lines.append(f"{i}. {entry}")
        lines.append("")

        # Warnings
        if self.warnings:
            lines.append("## Warnings")
            lines.append("")
            for w in self.warnings:
                lines.append(f"- {w}")
            lines.append("")

        return "\n".join(lines)
```

### 3.4 Subprocess Scoping (Gap 3)

#### 3.4.1 Changes to PortifyProcess

The `PortifyProcess.__init__` signature gains an `additional_dirs` parameter:

```python
class PortifyProcess(ClaudeProcess):
    def __init__(
        self,
        *,
        prompt: str,
        output_file: Path,
        error_file: Path,
        work_dir: Path,
        workflow_path: Path,
        additional_dirs: list[Path] | None = None,  # NEW
        artifact_refs: list[Path] | None = None,
        max_turns: int = 100,
        model: str = "",
        timeout_seconds: int = 300,
        output_format: str = "text",
        extra_args: list[str] | None = None,
    ):
        self._additional_dirs = [d.resolve() for d in (additional_dirs or [])]
        # ... rest unchanged
```

The `_build_add_dir_args()` method expands:

```python
def _build_add_dir_args(self) -> list[str]:
    args: list[str] = []
    seen: set[Path] = set()

    # Work directory (output artifacts)
    args.extend(["--add-dir", str(self._work_dir)])
    seen.add(self._work_dir)

    # Workflow path (source skill files)
    if self._workflow_path not in seen:
        args.extend(["--add-dir", str(self._workflow_path)])
        seen.add(self._workflow_path)

    # Additional source directories (commands/, agents/, etc.)
    for d in self._additional_dirs:
        if d not in seen:
            args.extend(["--add-dir", str(d)])
            seen.add(d)

    return args
```

#### 3.4.2 Where Additional Dirs Come From

The executor populates `additional_dirs` from `ComponentTree.all_source_dirs` at process construction time. Typical directories for `cleanup-audit`:

```
additional_dirs = [
    src/superclaude/commands/          # contains cleanup-audit.md
    src/superclaude/agents/            # contains audit-scanner.md, etc.
]
```

The `workflow_path` already covers the skill directory, so it is not duplicated.

#### 3.4.3 Directory Cap

If `all_source_dirs` returns more than 10 directories, emit a warning and consolidate to common parent directories. This prevents `--add-dir` argument explosion.

### 3.5 Changes to PortifyConfig (models.py)

```python
@dataclass
class PortifyConfig(PipelineConfig):
    # EXISTING (unchanged)
    workflow_path: Path = field(default_factory=lambda: Path("."))
    output_dir: Path = field(default_factory=lambda: Path("."))
    cli_name: str = ""
    skip_review: bool = False
    start_step: str | None = None
    iteration_timeout: int = 300
    max_convergence: int = 3

    # NEW -- populated after resolution
    target_input: str = ""                          # Raw user input
    target_type: str = ""                           # TargetInputType value
    command_path: Path | None = None                # Resolved command .md
    commands_dir: Path | None = None                # Commands directory
    skills_dir: Path | None = None                  # Skills directory
    agents_dir: Path | None = None                  # Agents directory
    project_root: Path | None = None                # Detected project root
    include_agents: list[str] = field(default_factory=list)  # From --include-agent
    save_manifest_path: Path | None = None          # From --save-manifest
    component_tree: ComponentTree | None = None     # Populated in Step 2
```

The existing `resolve_workflow_path()` method is preserved unchanged for backward compatibility. A new `resolve_target()` method is added that runs the full resolution algorithm.

The `derive_cli_name()` method is augmented to prefer the command name when available:

```python
def derive_cli_name(self) -> str:
    if self.cli_name:
        return self.cli_name

    # Prefer command name if resolved
    if self.command_path and self.command_path.exists():
        name = self.command_path.stem  # e.g., "roadmap" from "roadmap.md"
        return name.replace("_", "-")

    # Fall back to skill directory name derivation (existing logic)
    name = self.workflow_path.resolve().name
    if name.startswith("sc-"):
        name = name[3:]
    if name.endswith("-protocol"):
        name = name[: -len("-protocol")]
    name = name.replace("_", "-")
    return name
```

### 3.6 Changes to validate_config.py (Step 1)

New validation checks:

| Check # | Current | New |
|---------|---------|-----|
| 1 | Workflow path exists | Target resolves to at least one component (command or skill) |
| 2 | SKILL.md present | SKILL.md present in resolved skill dir (warn if missing, not error) |
| 3 | Output dir writable | Output dir writable (unchanged) |
| 4 | Name collision | Name collision (unchanged) |
| 5 | (none) | **NEW**: Command -> Skill link valid |
| 6 | (none) | **NEW**: Referenced agents exist (warn, not error) |

New error codes:

```python
ERR_TARGET_NOT_FOUND = "ERR_TARGET_NOT_FOUND"
ERR_AMBIGUOUS_TARGET = "ERR_AMBIGUOUS_TARGET"
ERR_BROKEN_ACTIVATION = "ERR_BROKEN_ACTIVATION"
WARN_MISSING_AGENTS = "WARN_MISSING_AGENTS"       # Warning, not error
```

The `ValidateConfigResult` gains new fields:

```python
@dataclass
class ValidateConfigResult:
    valid: bool = True
    cli_name_kebab: str = ""
    cli_name_snake: str = ""
    workflow_path_resolved: str = ""
    output_dir: str = ""
    errors: list[dict[str, str]] = field(default_factory=list)
    warnings: list[dict[str, str]] = field(default_factory=list)   # NEW
    duration_seconds: float = 0.0
    # NEW
    command_path: str = ""
    skill_dir: str = ""
    target_type: str = ""
    agent_count: int = 0
```

### 3.7 Changes to discover_components.py (Step 2)

The existing `run_discover_components()` function is refactored:

1. **New entry point**: `run_discover_component_tree(config, resolved_target, output_dir)` builds the full `ComponentTree`.
2. **Existing function preserved**: `run_discover_components()` becomes a thin wrapper that calls the new function and converts via `tree.to_flat_inventory()`.
3. **Artifact output**: The `component-inventory.md` artifact is enriched with:
   - `## Command` section (Tier 0 metadata)
   - `## Agents` section (Tier 2 agent table)
   - `## Cross-Tier Data Flow` section (directory references)
   - `## Resolution Log` section (how components were discovered)

New artifact frontmatter:

```yaml
---
source_command: roadmap
source_skill: sc-roadmap-protocol
component_count: 14
total_lines: 2847
agent_count: 3
has_command: true
has_skill: true
duration_seconds: 0.0312
---
```

### 3.8 Manifest Save (from Approach B)

When `--save-manifest` is specified, after Step 2 (discover-components) completes and the `ComponentTree` is built, the tree is serialized via `ComponentTree.to_manifest_markdown()` and written to the specified path.

This is a write-only operation. There is no `--manifest` (load) flag in v2.24.1. The saved manifest is a debugging and inspection artifact, not an input.

---

## 4. Module-Level Implementation Plan

### 4.1 New Files

| File | Location | Contents | Lines (est.) |
|------|----------|----------|-------------|
| `resolution.py` | `src/superclaude/cli/cli_portify/resolution.py` | `ResolvedTarget`, `TargetInputType`, `resolve_target()`, `build_component_tree()`, agent extraction regex, project root detection | 350-450 |

### 4.2 Modified Files

| File | Changes | Lines Changed (est.) |
|------|---------|---------------------|
| `models.py` | Add `ComponentTree`, `CommandEntry`, `SkillEntry`, `AgentEntry` dataclasses. Extend `PortifyConfig` with new fields. | +180-220 |
| `cli.py` | Change `workflow_path` argument to `target`. Add `--commands-dir`, `--skills-dir`, `--agents-dir`, `--include-agent`, `--save-manifest` options. Wire resolution into the run handler. | +40-60 |
| `config.py` | Update `load_portify_config()` to accept and pass through new parameters. | +15-25 |
| `validate_config.py` | Add new validation checks (5, 6). Add new error codes. Extend `ValidateConfigResult`. Run `resolve_target()` as part of validation. | +60-80 |
| `discover_components.py` | Add `run_discover_component_tree()`. Refactor existing function as wrapper. Enrich artifact output. Add manifest save logic. | +80-120 |
| `process.py` | Add `additional_dirs` parameter to `__init__`. Update `_build_add_dir_args()`. | +20-30 |

### 4.3 Implementation Phases

**Phase 1: Data Models (no existing code changes)**
- Add `ComponentTree`, `CommandEntry`, `SkillEntry`, `AgentEntry` to `models.py`
- Add `ResolvedTarget`, `TargetInputType` to new `resolution.py`
- All existing tests continue to pass

**Phase 2: Resolution Algorithm (new code only)**
- Implement `resolve_target()` in `resolution.py`
- Implement `build_component_tree()` in `resolution.py`
- Implement agent extraction regex patterns
- Implement project root auto-detection
- All existing tests continue to pass

**Phase 3: Discovery Integration**
- Add `run_discover_component_tree()` to `discover_components.py`
- Refactor `run_discover_components()` as wrapper calling the new function
- Enrich `component-inventory.md` artifact format
- Add `to_manifest_markdown()` and manifest save logic
- All existing tests continue to pass (wrapper preserves behavior)

**Phase 4: Subprocess Scoping**
- Add `additional_dirs` parameter to `PortifyProcess.__init__`
- Update `_build_add_dir_args()` with deduplication and cap
- All existing tests continue to pass (`additional_dirs=None` preserves behavior)

**Phase 5: CLI Update**
- Change `workflow_path` argument to `target`
- Add new CLI options
- Wire resolution into the run handler
- Update `load_portify_config()` in `config.py`

**Phase 6: Validation Update**
- Add new validation checks to `validate_config.py`
- Add new error codes
- Extend `ValidateConfigResult`

**Phase 7: Tests**
- Add test fixtures (`tests/cli_portify/fixtures/mock_project/`)
- Add resolution tests
- Add component tree tests
- Add subprocess scoping tests
- Update existing tests as needed

---

## 5. Test Plan

### 5.1 Test Fixtures

Create a mock project structure under `tests/cli_portify/fixtures/`:

```
fixtures/
  mock_project/
    src/superclaude/
      commands/
        mock-workflow.md          # Tier 0 command with ## Activation
        standalone-cmd.md         # Command without skill
      skills/
        sc-mock-workflow-protocol/
          SKILL.md                # References mock-agent-1, mock-agent-2
          refs/
            ref-1.md
          rules/
            rule-1.md
        standalone-skill/         # Skill without command
          SKILL.md
      agents/
        mock-agent-1.md
        mock-agent-2.md
```

The `mock-workflow.md` command fixture should contain:

```yaml
---
name: mock-workflow
category: testing
complexity: moderate
---

# /sc:mock-workflow

## Activation
Skill sc:mock-workflow-protocol
```

The `SKILL.md` fixture should contain agent references in multiple patterns to test extraction:

```markdown
## Agent Delegation

| Agent | Role |
|-------|------|
| `mock-agent-1` agent | Primary analysis |
| `mock-agent-2` agent | Secondary review |

Uses `mock-agent-1` for parallel variant generation.
```

### 5.2 Test Coverage Matrix

| Test Area | Priority | Tests | Description |
|-----------|----------|-------|-------------|
| `resolve_target()`: bare command name | P0 | 2 | `"mock-workflow"` resolves to command + skill + agents |
| `resolve_target()`: command path | P0 | 2 | Full path to command .md resolves correctly |
| `resolve_target()`: skill dir (backward compat) | P0 | 2 | Existing skill dir input still works, backward-resolves command |
| `resolve_target()`: ambiguous name | P0 | 1 | Error when multiple matches found |
| `resolve_target()`: non-existent target | P0 | 1 | Clear error with `ERR_TARGET_NOT_FOUND` |
| `resolve_target()`: prefixed name (sc:) | P1 | 1 | `"sc:mock-workflow"` strips prefix correctly |
| `resolve_target()`: SKILL.md path | P1 | 1 | Resolves parent dir, then backward-resolves |
| `resolve_target()`: skill name | P1 | 1 | `"sc-mock-workflow-protocol"` resolves |
| Agent extraction from SKILL.md | P0 | 4 | Each regex pattern finds references; combined extraction |
| Agent extraction: missing agent file | P1 | 1 | Warning recorded, `found=False`, not fatal |
| Agent extraction: no agents | P1 | 1 | Empty agents list, no error |
| Agent extraction: deduplication | P1 | 1 | Same agent referenced twice appears once |
| `--include-agent` injection | P1 | 2 | Manual agent added to tree; missing manual agent warned |
| Command without skill (standalone) | P1 | 1 | Resolves command-only, skill=None |
| Skill without command (standalone) | P1 | 1 | Resolves skill-only, command=None |
| `ComponentTree.all_source_dirs` | P1 | 2 | Correct deduplication; correct paths |
| `ComponentTree.to_flat_inventory()` | P2 | 2 | All components present; backward-compatible format |
| `ComponentTree.to_manifest_markdown()` | P2 | 1 | Readable Markdown output |
| `PortifyProcess` with `additional_dirs` | P1 | 2 | `--add-dir` args include all dirs; deduplication works |
| `PortifyProcess` without `additional_dirs` | P1 | 1 | Legacy behavior preserved |
| `ValidateConfigResult` new fields | P2 | 1 | New fields populated correctly |
| Directory cap (>10 dirs) | P2 | 1 | Warning emitted, consolidation occurs |

**Total estimated new tests**: ~32

### 5.3 Existing Test Impact

| Test File | Impact | Changes Required |
|-----------|--------|-----------------|
| `test_config.py` | Low | Add tests for new config fields; existing tests pass unchanged |
| `test_validate_config.py` | Moderate | Add tests for new error codes; existing validation tests pass |
| `test_discover_components.py` | Moderate | Existing tests pass via `to_flat_inventory()` wrapper; add new tree tests |
| `test_process.py` | Low | Add tests for `additional_dirs`; existing tests pass |
| `test_contracts.py` | Low | Verify new fields in contract output |
| All other test files | None | No changes expected |

---

## 6. Migration and Backward Compatibility

### 6.1 Input Backward Compatibility

| Current Usage | Still Works? | Behavior Change |
|--------------|-------------|-----------------|
| `superclaude cli-portify run src/.../skills/sc-roadmap-protocol/` | Yes | Now also discovers command and agents |
| `superclaude cli-portify run src/.../skills/sc-roadmap-protocol/SKILL.md` | Yes | Resolves parent dir, then same |
| `superclaude cli-portify run roadmap` | **New** | Resolves command, then skill, then agents |

### 6.2 API Backward Compatibility

| Function | Status | Notes |
|----------|--------|-------|
| `run_discover_components()` | Preserved | Returns `ComponentInventory` via wrapper |
| `load_portify_config()` | Extended | New optional params with defaults |
| `validate_portify_config()` | Extended | Returns same type, new fields added |
| `PortifyProcess.__init__()` | Extended | `additional_dirs` defaults to `None` |

### 6.3 Step Numbering

Step numbering is **unchanged**. Resolution runs within Step 1 (validate-config) as part of the validation flow. No new pipeline step is introduced.

---

## 7. Edge Cases

### 7.1 Commands Without Skills

Some commands (e.g., `help.md`, `sc.md`) have no paired skill. Resolution succeeds with `skill = None`. A warning is emitted. The pipeline can still analyze the command file alone.

### 7.2 Skills Without Commands

Standalone skills have no command file. Resolution succeeds with `command = None`. This is the backward-compatible path. No warning needed.

### 7.3 Multi-Skill Commands

A command referencing multiple skills: extract the primary skill from `## Activation`. Secondary skill references are recorded in warnings for manual review. NOT automatically resolved in v2.24.1.

### 7.4 Circular or Diamond References

Agents referenced from multiple sources are deduplicated by name. The first source is recorded in `referenced_in`.

### 7.5 Agent-to-Agent References

In v2.24.1, agent-to-agent references are NOT recursively resolved. Only SKILL.md (and optionally command file) is scanned for agent references. This keeps the algorithm O(1)-depth.

### 7.6 Broken Activation Link

If a command's `## Activation` references a non-existent skill: `ERR_BROKEN_ACTIVATION` error. Pipeline halts. Error message includes expected path.

### 7.7 Project Root Detection Failure

If auto-detection cannot find `src/superclaude/` or `pyproject.toml`: use `--commands-dir`, `--skills-dir`, `--agents-dir` explicit overrides. Error message suggests these flags.

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Agent extraction regex misses references | Medium | Medium | Start with 6 patterns covering known formats. `--include-agent` escape hatch. Iterate patterns based on real-world testing. |
| Backward-compatible resolution breaks existing workflows | Low | High | Extensive test coverage with existing fixtures. `resolve_workflow_path()` preserved unchanged. |
| `--add-dir` with many directories causes subprocess issues | Low | Medium | Cap at 10 dirs with consolidation. |
| YAML frontmatter parsing failures | Low | Low | Graceful degradation: if frontmatter fails, still discover by convention. |
| Project root detection fails in non-standard layouts | Medium | Low | Explicit `--commands-dir`, `--skills-dir`, `--agents-dir` overrides. |
| Reverse-resolution (skill -> command) fragile with non-standard naming | Medium | Low | Best-effort; missing command is a warning, not error. |

---

## 9. Effort Estimate

| Phase | Description | Files Changed | New Files | Estimated Effort |
|-------|-------------|--------------|-----------|-----------------|
| 1 | Data models | `models.py` | -- | 2-3 hours |
| 2 | Resolution algorithm | -- | `resolution.py` | 4-6 hours |
| 3 | Discovery integration | `discover_components.py` | -- | 3-4 hours |
| 4 | Subprocess scoping | `process.py` | -- | 1-2 hours |
| 5 | CLI update | `cli.py`, `config.py` | -- | 2-3 hours |
| 6 | Validation update | `validate_config.py` | -- | 2-3 hours |
| 7 | Tests | Multiple test files | `fixtures/mock_project/` | 5-7 hours |
| **Total** | | **6 files modified** | **1 new file + fixtures** | **19-28 hours** |

Estimated sessions: 2-3 focused implementation sessions.

---

## 10. Open Questions (Resolved)

| Question | Resolution |
|----------|-----------|
| Should agent-to-agent refs be recursively resolved? | **No** for v2.24.1. O(1)-depth. Future iteration if needed. |
| Should `resolve_target()` live in `resolution.py` or `config.py`? | **`resolution.py`** -- new module for single responsibility. |
| Should `component-inventory.md` adopt tree format? | **Yes** -- enrich with Command, Agents, Data Flow sections. Superset of current format. |
| Should the user be able to override discovery? | **Yes** -- `--include-agent` for adding agents. No `--exclude-component` in v2.24.1. |
| Should the resolved tree be persistable? | **Yes** -- via `--save-manifest` (write-only). No `--manifest` (load) in v2.24.1. |

---

*Synthesized spec completed: 2026-03-13*
*Base: Approach A (score 7.95) + selected elements from Approach B*
*Adversarial debate orchestrator: Opus 4.6*
