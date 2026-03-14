```yaml
---
title: "Portification Enhancement: Full Workflow Resolution for cli-portify"
version: "1.0.0"
status: reviewed
feature_id: FR-PORTIFY-WORKFLOW
parent_feature: FR-PORTIFY-CLI
spec_type: portification
complexity_score: 0.65
complexity_class: moderate
target_release: v2.24.1
authors: [user, claude]
created: 2026-03-13
quality_scores:
  clarity: 8.5
  completeness: 8.5
  testability: 8.0
  consistency: 8.5
  overall: 8.5
---
```

# FR-PORTIFY-WORKFLOW: Full Workflow Resolution for cli-portify

## 1. Problem Statement

The `superclaude cli-portify run` command has three design gaps that prevent it from portifying complete SuperClaude workflows:

| Gap | Current Behavior | Required Behavior |
|-----|-----------------|-------------------|
| **Gap 1: Input Target** | Accepts only a skill directory path containing `SKILL.md` | Accept a command name, command path, or skill path and resolve the full component tree |
| **Gap 2: Discovery** | Inventories only `SKILL.md` + subdirs within skill dir | Discover the command file, all referenced agents, and cross-directory data flows |
| **Gap 3: Subprocess Scoping** | `--add-dir` for `work_dir` + `workflow_path` only | Scope `commands/` and `agents/` directories so Claude subprocesses can read all components |

These gaps cause the portification analysis to operate on an incomplete picture of the workflow, producing incorrect or incomplete pipeline specifications.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| `resolve_workflow_path()` requires `SKILL.md` in directory | `models.py:91-94` | Commands, agents excluded from portification input |
| `discover_components.py` scans only `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/` | `steps/discover_components.py` | Agent delegation patterns, command frontmatter not inventoried |
| `PortifyProcess` passes `--add-dir` for 2 dirs only | `process.py` | Claude subprocesses cannot read command or agent files |
| `analysis-protocol.md` Step 1: "Find the Command" | `.claude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | Protocol expects command discovery; runner doesn't perform it |

### 1.2 Scope Boundary

**In scope**:
- Accept command name, command path, skill directory, or skill name as input
- Resolve command -> skill -> agents component tree automatically
- Extend subprocess scoping to include all discovered component directories
- Backward compatibility with existing skill-directory input
- Escape hatches for manual agent inclusion (`--include-agent`)

**Out of scope**:
- Recursive agent-to-agent reference resolution (deferred to future release)
- Multi-skill command resolution beyond primary activation skill
- Manifest loading as an input mode (`--manifest` flag deferred)
- Code generation from the portification output
- Changes to `pipeline/` or `sprint/` base modules

## 2. Solution Overview

The solution makes the **command** the primary entry point while retaining backward compatibility with skill-directory input. The system resolves the entire component tree automatically using a deterministic, pure-Python resolution algorithm that runs in under 1 second.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Input entry point | Command-first, skill-fallback | Manifest-first (Approach B) | Simpler, 1 new file vs 4-5, no new pipeline step |
| Component tree model | In-memory ComponentTree | Persistent manifest file | Tree is transient; optional `--save-manifest` for debugging |
| Pipeline step count | No new steps (resolve in Step 1) | New Step 0 (Approach B) | Avoids step renumbering, resume logic changes |
| Resolution algorithm | Pure Python, deterministic | Claude-assisted discovery | <1s execution, no subprocess budget consumed |
| Agent discovery scope | O(1)-depth, SKILL.md only | Recursive agent-to-agent | Bounded complexity; escape hatch via --include-agent |

### 2.2 Workflow / Data Flow

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

## 3. Functional Requirements

### FR-PORTIFY-WORKFLOW.1: Multi-Form Target Resolution

**Description**: Accept 6 input forms (bare command name, prefixed name, command path, skill directory, skill name, SKILL.md path) and resolve to a normalized `ResolvedTarget` containing the command path, skill directory, and project root.

**Acceptance Criteria**:
- [ ] `resolve_target("roadmap")` resolves to command + skill + agents
- [ ] `resolve_target("sc:roadmap")` strips prefix and resolves identically
- [ ] `resolve_target("src/.../sc-roadmap-protocol/")` backward-resolves command
- [ ] `resolve_target("nonexistent")` returns `ERR_TARGET_NOT_FOUND`
- [ ] Resolution completes in <1s for all input forms
- [ ] `--commands-dir`, `--skills-dir`, `--agents-dir` override auto-detection

**Dependencies**: None

### FR-PORTIFY-WORKFLOW.2: Full Component Tree Discovery

**Description**: Build a hierarchical `ComponentTree` containing Tier 0 (command), Tier 1 (skill + refs/rules/templates/scripts), and agents. Enrich `component-inventory.md` with Command, Agents, and Data Flow sections.

**Acceptance Criteria**:
- [ ] `ComponentTree` contains `CommandEntry`, `SkillEntry`, `AgentEntry` for a standard workflow
- [ ] Agent extraction finds references matching 6 regex patterns in SKILL.md
- [ ] `--include-agent` adds manually specified agents to the tree
- [ ] Missing agents recorded with `found=False`, emitted as warnings, not errors
- [ ] `component-inventory.md` frontmatter includes `source_command`, `agent_count`, `has_command`
- [ ] `to_flat_inventory()` produces backward-compatible `ComponentInventory`
- [ ] `to_manifest_markdown()` produces readable Markdown (for `--save-manifest`)
- [ ] Standalone command (no skill) produces ComponentTree with skill=None, agents=[], refs/rules/templates/scripts=[]

**Dependencies**: FR-PORTIFY-WORKFLOW.1

### FR-PORTIFY-WORKFLOW.3: Extended Subprocess Scoping

**Description**: Extend `PortifyProcess` to pass all discovered component directories via `--add-dir`, enabling Claude subprocesses to read command files, agent definitions, and cross-skill references.

**Acceptance Criteria**:
- [ ] `PortifyProcess` accepts `additional_dirs` parameter
- [ ] `_build_add_dir_args()` includes all dirs from `ComponentTree.all_source_dirs`
- [ ] Duplicate directories are deduplicated
- [ ] >10 directories triggers consolidation warning
- [ ] `additional_dirs=None` preserves existing v2.24 behavior

**Dependencies**: FR-PORTIFY-WORKFLOW.2

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/cli/cli_portify/resolution.py` | `ResolvedTarget`, `TargetInputType`, `resolve_target()`, `build_component_tree()`, agent extraction regex, project root detection (~350-450 lines) | `models.py` |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `models.py` | Add `ComponentTree`, `CommandEntry`, `SkillEntry`, `AgentEntry` dataclasses. Extend `PortifyConfig` with new fields (+180-220 lines) | Data model foundation for resolution and tree building |
| `cli.py` | Change `workflow_path` argument to `target`. Add `--commands-dir`, `--skills-dir`, `--agents-dir`, `--include-agent`, `--save-manifest` options. Wire resolution into run handler (+40-60 lines) | Enable new input forms and resolution wiring |
| `config.py` | Update `load_portify_config()` to accept and pass through new parameters (+15-25 lines) | Propagate new CLI options to config |
| `validate_config.py` | Add validation checks 5-6 (command-skill link, agent existence). Add error codes `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`. Extend `ValidateConfigResult` (+60-80 lines) | Validate resolved targets and provide clear error messages |
| `discover_components.py` | Add `run_discover_component_tree()`. Refactor existing function as wrapper. Enrich `component-inventory.md` artifact output. Add manifest save logic (+80-120 lines) | Full tree discovery with backward-compatible wrapper |
| `process.py` | Add `additional_dirs` parameter to `__init__`. Update `_build_add_dir_args()` with deduplication and cap (+20-30 lines) | Extended subprocess scoping for all discovered directories |

### 4.3 Removed Files

No files are removed by this work. All existing modules are preserved with backward-compatible extensions.

### 4.4 Module Dependency Graph

```
resolution.py ──> models.py (ResolvedTarget, ComponentTree)
cli.py ──> resolution.py (resolve_target)
validate_config.py ──> resolution.py (resolve_target)
discover_components.py ──> resolution.py (build_component_tree)
process.py ──> models.py (ComponentTree.all_source_dirs)
```

### 4.5 Data Models

#### Input Resolution Types

```python
class TargetInputType(Enum):
    COMMAND_NAME = "command_name"       # bare name like "roadmap"
    COMMAND_PATH = "command_path"       # path to .md file in commands/
    SKILL_DIR = "skill_dir"            # path to skill directory
    SKILL_NAME = "skill_name"          # bare name like "sc-roadmap-protocol"
    SKILL_FILE = "skill_file"          # path to SKILL.md


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
```

#### Input Acceptance Matrix

| Input Form | Example | Resolution Strategy |
|-----------|---------|---------------------|
| Bare command name | `roadmap` | Search `commands/` dir for `roadmap.md` |
| Command name with prefix | `sc:roadmap` | Strip `sc:`, search `commands/` for `roadmap.md` |
| Command file path | `src/superclaude/commands/roadmap.md` | Use directly |
| Skill directory path | `src/superclaude/skills/sc-roadmap-protocol/` | Backward-resolve command |
| Skill directory name | `sc-roadmap-protocol` | Find in `skills/`, backward-resolve command |
| SKILL.md path | `.../sc-roadmap-protocol/SKILL.md` | Use parent as skill dir, backward-resolve |

#### Resolution Algorithm

The resolution algorithm runs in 6 deterministic steps (R0-R5). All steps are pure Python filesystem operations.

**Step R0: Input Validation**

Before classifying `input_type`, validate the raw `target` string:
- If `target` is empty, whitespace-only, or `None`: return `ERR_TARGET_NOT_FOUND` with message "No target specified. Provide a command name, path, or skill directory."
- Strip leading/trailing whitespace from `target` before proceeding to classification.

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

**Ambiguity Resolution Policy**

`ERR_AMBIGUOUS_TARGET` is raised only when multiple matches exist **within the same input type class**:
- Bare name `"roadmap"` matching two files in `commands/` (e.g., `roadmap.md` and `roadmap-v2.md`) → ERR_AMBIGUOUS_TARGET
- Bare name `"roadmap"` matching both `commands/roadmap.md` AND `skills/roadmap/` → **NOT ambiguous** — command wins per command-first policy

A bare name that matches a command always resolves as COMMAND_NAME. The skill is discovered from the command's `## Activation` directive, not from name matching. Only if no command matches does the resolver attempt SKILL_NAME matching.

After prefix stripping (removing `sc:` prefix), if the resulting name is empty (i.e., input was exactly `"sc:"`), return `ERR_TARGET_NOT_FOUND` with message "Empty command name after prefix stripping. Provide a valid command name after 'sc:'."

**Guard: Skill-less Command Path**

If `ResolvedTarget.skill_dir` is `None` after R2 (standalone command with no paired skill):
- Skip R3 (agent extraction) — no SKILL.md to parse
- Skip R4 (Tier 2 inventory) — no subdirectories to scan
- Proceed directly to R5 with `agents = []`, `refs = []`, `rules = []`, `templates = []`, `scripts = []`
- Record in `resolution_log`: "Standalone command — no skill directory, skipping component discovery"

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

Additionally, inject any agents specified via `--include-agent` CLI option. These are resolved the same way: if a bare name, look up in `agents_dir`; if a path, use directly. If `--include-agent` receives an empty string `""`, it is silently ignored (no agent lookup attempted).

**Deduplication rule**: All agents — both auto-discovered and manually injected — are deduplicated by name. If `--include-agent` specifies an agent already discovered from SKILL.md:
- The manually specified entry takes precedence (overwrites auto-discovered)
- `referenced_in` is set to `"cli-override"` for the merged entry
- No duplicate `AgentEntry` objects exist in the final `ComponentTree.agents` list

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

Assemble all discovered components into a `ComponentTree`.

**Type Convention Note**: The existing `ComponentEntry` dataclass (v2.24) uses `path: str` for backward compatibility with serialization and artifact generation. All new dataclasses introduced in this spec (`ResolvedTarget`, `CommandEntry`, `SkillEntry`, `AgentEntry`, `ComponentTree`) use `Path` objects for type safety. The `to_flat_inventory()` method converts `Path` → `str` via `str()` at the boundary. This convention is intentional and should be preserved — do not change `ComponentEntry.path` to `Path`.

#### Component Tree Model

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

#### PortifyConfig Extensions (models.py)

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

#### Subprocess Scoping Extensions (process.py)

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

Typical directories for `cleanup-audit`:

```
additional_dirs = [
    src/superclaude/commands/          # contains cleanup-audit.md
    src/superclaude/agents/            # contains audit-scanner.md, etc.
]
```

The `workflow_path` already covers the skill directory, so it is not duplicated.

**Directory Cap and Consolidation**

If `all_source_dirs` returns more than 10 directories:

1. Emit a warning: "Component tree spans {N} directories (cap: 10). Consolidating to parent directories."
2. Group directories by their nearest common parent using `os.path.commonpath()` for each pair within 2 levels of depth.
3. Replace groups sharing a common parent with the common parent directory, provided the parent directory contains no more than 3x the total file count of its constituent directories.
4. If consolidation still exceeds 10 directories, use only the top 10 by component count (most components first).
5. Record all consolidation decisions in `resolution_log`.

This prevents `--add-dir` argument explosion while limiting over-scoping of Claude subprocess access.

#### ValidateConfigResult Extensions (validate_config.py)

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

The `to_dict()` method MUST be updated to include all new fields:

```python
def to_dict(self) -> dict[str, Any]:
    return {
        "step": "validate-config",
        "valid": self.valid,
        "cli_name_kebab": self.cli_name_kebab,
        "cli_name_snake": self.cli_name_snake,
        "workflow_path_resolved": self.workflow_path_resolved,
        "output_dir": self.output_dir,
        "errors": self.errors,
        "warnings": self.warnings,          # NEW
        "duration_seconds": self.duration_seconds,
        "command_path": self.command_path,   # NEW
        "skill_dir": self.skill_dir,         # NEW
        "target_type": self.target_type,     # NEW
        "agent_count": self.agent_count,     # NEW
    }
```

These fields are consumed by downstream contract emission (`contract.py`) and resume context (`resume.py`). Omitting them would cause silent data loss in pipeline telemetry.

#### Manifest Save (from Approach B)

When `--save-manifest` is specified, after Step 2 (discover-components) completes and the `ComponentTree` is built, the tree is serialized via `ComponentTree.to_manifest_markdown()` and written to the specified path.

This is a write-only operation. There is no `--manifest` (load) flag in v2.24.1. The saved manifest is a debugging and inspection artifact, not an input.

#### Discovery Extensions (discover_components.py)

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

### 4.6 Implementation Order

```
1. models.py (data models)                    -- no existing code changes
2. resolution.py (new module)                 -- [parallel with 1]
3. discover_components.py (discovery)         -- depends on 1, 2
4. process.py (subprocess scoping)            -- depends on 1
   validate_config.py (validation)            -- [parallel with 4]
5. cli.py + config.py (CLI wiring)            -- depends on 3, 4
6. Tests + fixtures                            -- depends on all above
```

## 5. Interface Contracts

### 5.1 CLI Surface

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `TARGET` | STRING (argument) | required | Command name, path, skill directory, or skill name to portify. Must be non-empty. |
| `--commands-dir` | PATH | auto-detect | Override commands directory |
| `--skills-dir` | PATH | auto-detect | Override skills directory |
| `--agents-dir` | PATH | auto-detect | Override agents directory |
| `--include-agent` | STRING (multiple) | none | Include additional agent(s) by name or path |
| `--save-manifest` | PATH | none | Save resolved component tree as manifest file |
| `--output` | PATH | auto | Output directory for generated artifacts |
| `--dry-run` | FLAG | false | Halt after Step 2 |
| `--skip-review` | FLAG | false | Skip interactive review gates |
| `--start` | STRING | none | Resume from specific step |
| ... | | | (existing options unchanged) |

CLI interface change:

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

### 5.2 Gate Criteria

Gate criteria are unchanged from v2.24. All existing gates (ANALYZE_WORKFLOW_GATE through PANEL_REVIEW_GATE) remain valid. The enriched `component-inventory.md` artifact provides more context to Claude subprocesses but does not alter gate evaluation logic.

### 5.3 Phase Contracts

Phase contract schema is unchanged from v2.24. The `PortifyContract` emitted by `contract.py` retains all existing fields. New fields in `ValidateConfigResult` (command_path, skill_dir, target_type, agent_count) are informational additions that do not alter contract structure.

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-WORKFLOW.1 | Target resolution performance | <1s for all 6 input forms | `time.monotonic()` in `resolve_target()` |
| NFR-WORKFLOW.2 | Zero base-module modifications | 0 changes to `pipeline/` or `sprint/` | `git diff --name-only` |
| NFR-WORKFLOW.3 | Synchronous-only execution | No `async def` or `await` in new code | `grep -r "async def\|await"` |
| NFR-WORKFLOW.4 | Backward compatibility | All existing skill-dir inputs produce identical behavior | Existing test suite passes unchanged |
| NFR-WORKFLOW.5 | Subprocess directory cap | Warning at >10 `--add-dir` entries | Consolidation logic in `_build_add_dir_args()` |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Agent extraction regex misses references | Medium | Medium | Start with 6 patterns covering known formats. `--include-agent` escape hatch. Iterate patterns based on real-world testing. |
| Backward-compatible resolution breaks existing workflows | Low | High | Extensive test coverage with existing fixtures. `resolve_workflow_path()` preserved unchanged. |
| `--add-dir` with many directories causes subprocess issues | Low | Medium | Cap at 10 dirs with consolidation. |
| YAML frontmatter parsing failures | Low | Low | Graceful degradation: if frontmatter fails, still discover by convention. |
| Project root detection fails in non-standard layouts | Medium | Low | Explicit `--commands-dir`, `--skills-dir`, `--agents-dir` overrides. |
| Reverse-resolution (skill -> command) fragile with non-standard naming | Medium | Low | Best-effort; missing command is a warning, not error. |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `resolve_target()`: bare command name | `test_resolution.py` | `"mock-workflow"` resolves to command + skill + agents |
| `resolve_target()`: command path | `test_resolution.py` | Full path to command .md resolves correctly |
| `resolve_target()`: skill dir (backward compat) | `test_resolution.py` | Existing skill dir input still works, backward-resolves command |
| `resolve_target()`: ambiguous name | `test_resolution.py` | Error when multiple matches found |
| `resolve_target()`: non-existent target | `test_resolution.py` | Clear error with `ERR_TARGET_NOT_FOUND` |
| `resolve_target()`: prefixed name (sc:) | `test_resolution.py` | `"sc:mock-workflow"` strips prefix correctly |
| `resolve_target()`: SKILL.md path | `test_resolution.py` | Resolves parent dir, then backward-resolves |
| `resolve_target()`: skill name | `test_resolution.py` | `"sc-mock-workflow-protocol"` resolves |
| Agent extraction from SKILL.md | `test_resolution.py` | Each regex pattern finds references; combined extraction |
| Agent extraction: missing agent file | `test_resolution.py` | Warning recorded, `found=False`, not fatal |
| Agent extraction: no agents | `test_resolution.py` | Empty agents list, no error |
| Agent extraction: deduplication | `test_resolution.py` | Same agent referenced twice appears once |
| `--include-agent` injection | `test_resolution.py` | Manual agent added to tree; missing manual agent warned |
| Command without skill (standalone) | `test_resolution.py` | Resolves command-only, skill=None |
| Skill without command (standalone) | `test_resolution.py` | Resolves skill-only, command=None |
| `ComponentTree.all_source_dirs` | `test_models.py` | Correct deduplication; correct paths |
| `ComponentTree.to_flat_inventory()` | `test_models.py` | All components present; backward-compatible format |
| `ComponentTree.to_manifest_markdown()` | `test_models.py` | Readable Markdown output |
| `ValidateConfigResult` new fields | `test_validate_config.py` | New fields populated correctly |
| Directory cap (>10 dirs) | `test_process.py` | Warning emitted, consolidation occurs |
| `resolve_target()`: empty/whitespace input | `test_resolution.py` | Returns ERR_TARGET_NOT_FOUND for `""`, `" "` |
| `resolve_target()`: `"sc:"` prefix with empty name | `test_resolution.py` | Returns ERR_TARGET_NOT_FOUND after stripping |
| `resolve_target()`: standalone command (no skill) | `test_resolution.py` | R3/R4 skipped, agents=[], skill=None |
| `--include-agent` dedup against auto-discovered | `test_resolution.py` | Manual agent replaces auto-discovered, no duplicates |
| `ValidateConfigResult.to_dict()` new fields | `test_validate_config.py` | New fields and `warnings` present in dict output |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| `PortifyProcess` with `additional_dirs` | `--add-dir` args include all dirs; deduplication works |
| `PortifyProcess` without `additional_dirs` | Legacy behavior preserved |
| Full resolution + discovery + subprocess scoping | End-to-end pipeline from command name to enriched inventory |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Portify sc:roadmap by name | `superclaude cli-portify run roadmap --dry-run` | Resolves command + skill + agents; component-inventory.md has all tiers |
| Portify by skill dir (backward compat) | `superclaude cli-portify run src/.../sc-roadmap-protocol/` | Same result as name-based; command backward-resolved |
| Missing agent graceful degradation | Use skill referencing nonexistent agent | Warning emitted; pipeline continues with found=False agent |
| Manifest save | `superclaude cli-portify run roadmap --save-manifest ./manifest.md --dry-run` | manifest.md written with full tree |

### Test Fixtures

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

### Existing Test Impact

| Test File | Impact | Changes Required |
|-----------|--------|-----------------|
| `test_config.py` | Low | Add tests for new config fields; existing tests pass unchanged |
| `test_validate_config.py` | Moderate | Add tests for new error codes; existing validation tests pass |
| `test_discover_components.py` | Moderate | Existing tests pass via `to_flat_inventory()` wrapper; add new tree tests |
| `test_process.py` | Low | Add tests for `additional_dirs`; existing tests pass |
| `test_contracts.py` | Low | Verify new fields in contract output |
| All other test files | None | No changes expected |

**Total estimated new tests**: ~37

## 9. Migration & Rollout

- **Breaking changes**: No. The `TARGET` argument is a superset of the old `WORKFLOW_PATH`.
- **Backwards compatibility**: Existing skill-directory inputs resolve identically via backward-resolution. `resolve_workflow_path()` preserved unchanged.
- **Rollback plan**: Revert to v2.24 CLI argument (`WORKFLOW_PATH` with `type=click.Path(exists=True)`). No data model migration needed -- new fields have defaults.

### Input Backward Compatibility

| Current Usage | Still Works? | Behavior Change |
|--------------|-------------|-----------------|
| `superclaude cli-portify run src/.../skills/sc-roadmap-protocol/` | Yes | Now also discovers command and agents |
| `superclaude cli-portify run src/.../skills/sc-roadmap-protocol/SKILL.md` | Yes | Resolves parent dir, then same |
| `superclaude cli-portify run roadmap` | **New** | Resolves command, then skill, then agents |

### API Backward Compatibility

| Function | Status | Notes |
|----------|--------|-------|
| `run_discover_components()` | Preserved | Returns `ComponentInventory` via wrapper |
| `load_portify_config()` | Extended | New optional params with defaults |
| `validate_portify_config()` | Extended | Returns same type, new fields added |
| `PortifyProcess.__init__()` | Extended | `additional_dirs` defaults to `None` |

### Step Numbering

Step numbering is **unchanged**. Resolution runs within Step 1 (validate-config) as part of the validation flow. No new pipeline step is introduced.

## 10. Downstream Inputs

### For sc:roadmap
- **Themes**: "Workflow resolution", "Component tree discovery", "Subprocess scoping"
- **Milestones**: 7 implementation phases (data models -> resolution -> discovery -> scoping -> CLI -> validation -> tests)
- **Estimated tasks**: 15-20 tasks across 7 phases
- **Complexity class**: MODERATE (0.65)

### For sc:tasklist
- **Phase structure**: 7 phases with clear dependency ordering
- **Tier distribution**: Mix of STRICT (resolution correctness, subprocess scoping), STANDARD (discovery enrichment), EXEMPT (data model additions)
- **Deliverable count**: ~15 deliverables (1 new module, 6 modified modules, 1 fixture set, ~32 tests)
- **Parallelization**: Phases 1-2 (models + resolution) can run in parallel; Phase 3-4 (discovery + scoping) can run in parallel after 1-2 complete

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| OI-1 | Should agent-to-agent refs be recursively resolved? | Medium -- some agents delegate to sub-agents | Deferred to v2.25. O(1)-depth in v2.24.1. |
| OI-2 | Should manifest loading be supported as input? | Low -- save-manifest is write-only in v2.24.1 | Deferred to v2.25 if user demand exists. |
| OI-3 | Should `--exclude-component` be supported? | Low -- not needed if discovery is accurate | Deferred to v2.25. |
| OI-4 | Quality scores for this spec | Required for release readiness | **RESOLVED** -- panel review completed 2026-03-13, scores populated |

## 12. Brainstorm Gap Analysis

Gap analysis was performed via structured adversarial debate between two competing approaches (Approach A: Command-Centric, Approach B: Manifest-Based). Three ideas from the losing approach were incorporated.

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-B1 | No debugging output for resolution logic | Medium | 5.1 CLI Surface | analyzer |
| GAP-B2 | Heuristic agent extraction may miss references | Medium | 3, FR-2 | qa |
| GAP-B3 | Enriched inventory aids Claude analysis quality | Low | FR-2 | architect |

**Resolution**: GAP-B1 addressed via `--save-manifest`. GAP-B2 addressed via `--include-agent`. GAP-B3 addressed via enriched `component-inventory.md`.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Tier 0 | Command `.md` file -- thin entry point that dispatches to a skill |
| Tier 1 | Skill/Protocol -- full behavioral specification in a skill directory |
| Tier 2 | Refs, rules, templates, scripts -- step-specific detail loaded on-demand |
| ComponentTree | In-memory hierarchical model of all workflow components |
| ResolvedTarget | Normalized result of input resolution -- command path, skill dir, project root |
| Backward-resolution | Deriving the command file from a skill directory name |
| Manifest | Optional serialized representation of the ComponentTree for debugging |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `synthesized-spec.md` (this spec's source) | Pre-template-alignment version |
| `brainstorm-approach-a.md` | Winning approach (command-centric) |
| `brainstorm-approach-b.md` | Losing approach (manifest-based) -- 3 ideas incorporated |
| `debate-transcript.md` | 3-round adversarial debate record |
| `scoring-matrix.md` | 6-criteria weighted scoring (A: 7.95, B: 7.00) |
| `context-overview.md` | Gap discovery documentation |
| `docs/architecture/command-skill-policy.md` | Tier 0/1/2 architecture definition |
| `.claude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | Protocol-level discovery requirements |
| `src/superclaude/examples/release-spec-template.md` | Target template for this alignment |
| `spec-panel-review.md` | Panel review findings (C-1, M-1..M-7, m-1..m-3) driving remediation |

*Synthesis provenance: Approach A (score 7.95) + selected elements from Approach B. Adversarial debate orchestrator: Opus 4.6. Date: 2026-03-13.*

## Appendix C: Effort Estimate

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

### Edge Cases

#### Commands Without Skills

Some commands (e.g., `help.md`, `sc.md`) have no paired skill. Resolution succeeds with `skill = None`. A warning is emitted. The pipeline can still analyze the command file alone.

#### Skills Without Commands

Standalone skills have no command file. Resolution succeeds with `command = None`. This is the backward-compatible path. No warning needed.

#### Multi-Skill Commands

A command referencing multiple skills: extract the primary skill from `## Activation`. Secondary skill references are recorded in warnings for manual review. NOT automatically resolved in v2.24.1.

#### Circular or Diamond References

Agents referenced from multiple sources are deduplicated by name. The first source is recorded in `referenced_in`.

#### Agent-to-Agent References

In v2.24.1, agent-to-agent references are NOT recursively resolved. Only SKILL.md (and optionally command file) is scanned for agent references. This keeps the algorithm O(1)-depth.

#### Broken Activation Link

If a command's `## Activation` references a non-existent skill: `ERR_BROKEN_ACTIVATION` error. Pipeline halts. Error message includes expected path.

#### Project Root Detection Failure

If auto-detection cannot find `src/superclaude/` or `pyproject.toml`: use `--commands-dir`, `--skills-dir`, `--agents-dir` explicit overrides. Error message suggests these flags.
