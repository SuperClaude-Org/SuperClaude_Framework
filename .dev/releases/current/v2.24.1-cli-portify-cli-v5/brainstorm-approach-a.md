# Approach A: Command-Centric Resolution

**Status**: DRAFT SPEC
**Date**: 2026-03-13
**Author**: Backend Architect (brainstorm session)
**Scope**: Fix 3 critical design gaps in `superclaude cli-portify run`

---

## 1. Problem Statement

The `superclaude cli-portify run` command currently accepts only a skill directory containing `SKILL.md` as input. This is fundamentally misaligned with the SuperClaude architecture, which structures workflows as a multi-tier component tree:

```
Tier 0: Command (.md)              src/superclaude/commands/<name>.md
  dispatches to -->
Tier 1: Skill / Protocol (.md)     src/superclaude/skills/sc-<name>-protocol/
  loads on-demand -->
Tier 2: Refs (refs/*.md)           src/superclaude/skills/sc-<name>-protocol/refs/
         Rules (rules/)
         Templates (templates/)
         Scripts (scripts/)
  + Agents (agents/*.md)           src/superclaude/agents/
```

Three gaps result from this misalignment:

| Gap | Current Behavior | Required Behavior |
|-----|-----------------|-------------------|
| **Gap 1: Input Target** | Accepts only a skill directory path | Should accept a command name, command path, or skill path and resolve the full tree |
| **Gap 2: Discovery** | Inventories only `SKILL.md` + subdirs within skill dir | Must discover the command file, all referenced agents, and cross-directory data flows |
| **Gap 3: Subprocess Scoping** | `--add-dir` for `work_dir` + `workflow_path` only | Must scope `commands/` and `agents/` directories so Claude subprocesses can read all components |

These gaps mean the analysis protocol (`refs/analysis-protocol.md`) cannot be fulfilled by the programmatic pipeline. The protocol explicitly requires: "Find the Command", "Find the Skill", "Find the Agents", and "Map the Data Flow" -- but only step 2 (Find the Skill) is partially supported.

---

## 2. Proposed Solution Overview

**Approach A** makes the **command** the primary entry point. The user provides a command name (e.g., `roadmap`, `cleanup-audit`) or a command file path (e.g., `src/superclaude/commands/roadmap.md`), and the system resolves the entire component tree automatically.

### Resolution Flow

```
User Input                     Resolution Chain
-----------                    ----------------
"roadmap"                  --> find commands/roadmap.md
                           --> parse Activation section --> "Skill sc:roadmap-protocol"
                           --> resolve sc-roadmap-protocol/ in skills/
                           --> scan SKILL.md for agent references
                           --> resolve each agent in agents/
                           --> inventory refs/, rules/, templates/, scripts/
                           --> build ComponentTree

"src/.../commands/roadmap.md"  --> same chain, starting from file

"src/.../skills/sc-roadmap-protocol/"  --> backward-resolve command
                                       --> then same chain
```

### Key Design Decisions

1. **Command-first, skill-fallback**: The primary input is a command name or path. Skill directory paths remain supported for backward compatibility but trigger a backward-resolution step to find the paired command.

2. **ComponentTree replaces ComponentInventory**: The flat list model (`ComponentInventory`) is replaced with a tree model (`ComponentTree`) that captures the Tier 0/1/2 hierarchy and inter-component references.

3. **Multi-directory scoping**: `PortifyProcess` gains an `additional_dirs` list, populated from the resolved component tree, so Claude subprocesses can access all relevant source files.

4. **Deterministic resolution**: All resolution logic is pure Python with no Claude subprocess involvement. It runs in under 1 second. Ambiguity (multiple matches) results in a clear error, not a guess.

---

## 3. Detailed Design

### 3.1 Gap 1: New Input Model

#### 3.1.1 Input Acceptance

The `run` subcommand accepts a `TARGET` positional argument that can be one of:

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
# cli.py -- BEFORE
@click.argument("workflow_path", type=click.Path(exists=True))

# cli.py -- AFTER
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
```

The three `--*-dir` options default to auto-detection relative to the project root. Auto-detection algorithm:

1. If `target` is an absolute or relative path, derive project root by walking up to find `src/superclaude/` or `pyproject.toml`.
2. If `target` is a bare name, search known locations: `src/superclaude/commands/`, `.claude/commands/sc/`.
3. Fall back to CWD-relative paths.

#### 3.1.3 Input Normalization

A new function `resolve_target()` normalizes any input form into a `ResolvedTarget`:

```python
@dataclass
class ResolvedTarget:
    """Normalized target after input resolution."""
    input_form: str                    # What the user typed
    input_type: TargetInputType        # Enum: COMMAND_NAME, COMMAND_PATH, SKILL_DIR, SKILL_NAME, SKILL_FILE
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

### 3.2 Gap 2: Full Component Tree Discovery

#### 3.2.1 Resolution Algorithm

The resolution algorithm runs in 5 deterministic steps:

**Step R1: Resolve Command**

If `input_type` is `COMMAND_NAME` or `COMMAND_PATH`:
- Locate the command `.md` file
- Parse its YAML frontmatter for `name`, `category`, `complexity`, `allowed-tools`, `mcp-servers`, `personas`
- Parse the `## Activation` section for the skill reference pattern: `Skill sc:<name>-protocol`
- Extract the skill name from the activation directive

If `input_type` is `SKILL_DIR`, `SKILL_NAME`, or `SKILL_FILE`:
- Reverse-resolve the command by: take skill dir name, strip `sc-` prefix and `-protocol` suffix, search `commands_dir` for `<name>.md`
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
]
```

For each extracted agent name, resolve to `agents_dir/<name>.md`. Record which agents were found vs. referenced-but-missing.

Additionally, scan for cross-references to other skills (for multi-skill commands, see edge cases).

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

Assemble all discovered components into a tree structure (see 3.2.2).

#### 3.2.2 ComponentTree Data Model

```python
@dataclass
class AgentEntry:
    """An agent referenced by the workflow."""
    name: str
    path: Path | None           # None if referenced but not found
    line_count: int
    referenced_in: str          # "skill" or "command" -- where the reference was found
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

    Replaces ComponentInventory with a hierarchical model
    that captures the Tier 0/1/2 architecture.
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
```

#### 3.2.3 Changes to `discover_components.py`

The existing `run_discover_components()` function is refactored:

1. **New entry point**: `run_discover_component_tree(config, resolved_target, output_dir)` -- builds the full `ComponentTree`.
2. **Existing function preserved**: `run_discover_components()` becomes a thin wrapper that calls the new function and converts via `tree.to_flat_inventory()`.
3. **Artifact output**: The `component-inventory.md` artifact is enriched with a `## Agents` section and `## Command` section, plus a `## Data Flow` section listing cross-directory references.

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

### 3.3 Gap 3: Subprocess Scoping

#### 3.3.1 Changes to `PortifyProcess`

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

The `_build_add_dir_args()` method expands to include all source directories:

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

#### 3.3.2 Where Additional Dirs Come From

The executor (or the step runner) populates `additional_dirs` from `ComponentTree.all_source_dirs`. This happens at process construction time, not at config time, because the tree is built in Step 2 (discover) and the subprocess is not launched until Step 3+.

Typical directories for a workflow like `cleanup-audit`:

```
additional_dirs = [
    src/superclaude/commands/          # contains cleanup-audit.md
    src/superclaude/agents/            # contains audit-scanner.md, audit-analyzer.md, etc.
]
```

Note: the `workflow_path` already covers the skill directory, so it is not duplicated.

### 3.4 Changes to `PortifyConfig` / `models.py`

#### 3.4.1 New Fields on PortifyConfig

```python
@dataclass
class PortifyConfig(PipelineConfig):
    # EXISTING
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
    component_tree: ComponentTree | None = None     # Populated in Step 2
```

#### 3.4.2 Updated `resolve_workflow_path()`

The existing method is preserved for backward compatibility but augmented:

```python
def resolve_workflow_path(self) -> Path:
    """Resolve and validate the workflow path.

    If workflow_path points to a skill directory (contains SKILL.md),
    returns that directory. This is the backward-compatible path.

    For command-centric resolution, use resolve_target() instead.
    """
    # ... existing logic unchanged ...
```

A new method `resolve_target()` is added that runs the full resolution algorithm described in 3.2.1.

#### 3.4.3 Updated `derive_cli_name()`

When a command is resolved, the CLI name can be derived from the command name directly (which is simpler and more reliable than parsing the skill directory name):

```python
def derive_cli_name(self) -> str:
    if self.cli_name:
        return self.cli_name

    # Prefer command name if resolved
    if self.command_path and self.command_path.exists():
        name = self.command_path.stem  # e.g., "roadmap" from "roadmap.md"
        return name.replace("_", "-")

    # Fall back to skill directory name derivation
    name = self.workflow_path.resolve().name
    if name.startswith("sc-"):
        name = name[3:]
    if name.endswith("-protocol"):
        name = name[: -len("-protocol")]
    name = name.replace("_", "-")
    return name
```

### 3.5 Changes to `validate_config.py` (Step 1)

The validation step gains new checks:

| Check # | Current | New |
|---------|---------|-----|
| 1 | Workflow path exists | Target resolves to at least one component (command or skill) |
| 2 | SKILL.md present | SKILL.md present in resolved skill dir (warn if missing, not error) |
| 3 | Output dir writable | Output dir writable (unchanged) |
| 4 | Name collision | Name collision (unchanged) |
| 5 | (none) | **NEW**: Command -> Skill link valid (Activation section references existing skill) |
| 6 | (none) | **NEW**: Referenced agents exist (warn for missing, not error) |

Error code additions:

```python
ERR_TARGET_NOT_FOUND = "ERR_TARGET_NOT_FOUND"      # No command or skill matches target
ERR_AMBIGUOUS_TARGET = "ERR_AMBIGUOUS_TARGET"       # Multiple matches for bare name
ERR_BROKEN_ACTIVATION = "ERR_BROKEN_ACTIVATION"     # Command's Activation references non-existent skill
ERR_MISSING_AGENTS = "ERR_MISSING_AGENTS"           # Warning-level: referenced agents not found
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

---

## 4. Data Model Changes Summary

| Model | Change Type | Description |
|-------|------------|-------------|
| `PortifyConfig` | Extended | New fields: `target_input`, `target_type`, `command_path`, `commands_dir`, `skills_dir`, `agents_dir`, `project_root`, `component_tree` |
| `ComponentInventory` | Preserved | Remains for backward compat; `ComponentTree.to_flat_inventory()` converts |
| `ComponentTree` | **New** | Hierarchical model with `CommandEntry`, `SkillEntry`, `AgentEntry`, Tier 2 lists |
| `CommandEntry` | **New** | Command file metadata including frontmatter and activation reference |
| `SkillEntry` | **New** | Skill directory metadata including frontmatter |
| `AgentEntry` | **New** | Agent file metadata including delegation pattern |
| `ResolvedTarget` | **New** | Input normalization result |
| `TargetInputType` | **New** | Enum for input classification |
| `ValidateConfigResult` | Extended | New fields: `warnings`, `command_path`, `skill_dir`, `target_type`, `agent_count` |
| `PortifyProcess` | Extended | New `additional_dirs` parameter |

---

## 5. Migration and Backward Compatibility Plan

### 5.1 Input Backward Compatibility

The existing input form (skill directory path) continues to work unchanged. The resolution logic detects this case and runs backward-resolution to find the command.

| Current Usage | Still Works? | Behavior Change |
|--------------|-------------|-----------------|
| `superclaude cli-portify run src/superclaude/skills/sc-roadmap-protocol/` | Yes | Now also discovers the command and agents |
| `superclaude cli-portify run src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | Yes | Resolves parent dir, then same |
| `superclaude cli-portify run roadmap` | **New** | Resolves command, then skill, then agents |

### 5.2 API Backward Compatibility

| Function | Status | Notes |
|----------|--------|-------|
| `run_discover_components()` | Preserved | Returns `ComponentInventory` via `tree.to_flat_inventory()` |
| `load_portify_config()` | Extended | New optional params, old params unchanged |
| `validate_portify_config()` | Extended | Returns same type, new error codes added |
| `PortifyProcess.__init__()` | Extended | `additional_dirs` defaults to `None` (no change) |

### 5.3 Migration Steps

1. **Phase 1**: Add new data models (`ComponentTree`, `ResolvedTarget`, etc.) -- no existing code changes
2. **Phase 2**: Add `resolve_target()` function and the 5-step resolution algorithm -- new code only
3. **Phase 3**: Update `run_discover_components()` to call `run_discover_component_tree()` internally and convert
4. **Phase 4**: Update `PortifyProcess` with `additional_dirs` support
5. **Phase 5**: Update CLI (`cli.py`) to accept `target` instead of `workflow_path`
6. **Phase 6**: Update `validate_config.py` with new validation checks
7. **Phase 7**: Update existing tests, add new tests for resolution paths

---

## 6. Impact on Existing Tests

### 6.1 Test Files Affected

| Test File | Impact | Changes Required |
|-----------|--------|-----------------|
| `test_config.py` | Moderate | Add tests for new config fields; existing tests pass unchanged |
| `test_validate_config.py` | Moderate | Add tests for new error codes; existing validation tests pass unchanged |
| `test_discover_components.py` | High | Major rewrite: test full tree discovery, agent resolution, command resolution. Existing tests for flat inventory still pass via `to_flat_inventory()` |
| `test_process.py` | Low | Add tests for `additional_dirs`; existing tests pass unchanged |
| `test_contracts.py` | Low | Verify new fields appear in contract output |
| All other test files | None | No changes expected |

### 6.2 New Test Coverage Required

| Test Area | Priority | Description |
|-----------|----------|-------------|
| Target resolution: bare name | P0 | `"roadmap"` resolves to command + skill + agents |
| Target resolution: command path | P0 | Full path to command .md resolves correctly |
| Target resolution: skill dir (backward compat) | P0 | Existing skill dir input still works |
| Target resolution: ambiguous name | P0 | Error when multiple matches found |
| Target resolution: non-existent target | P0 | Clear error message |
| Agent extraction from SKILL.md | P1 | Regex patterns find all agent references |
| Agent extraction: missing agent file | P1 | Warning, not error |
| Command without skill (standalone) | P1 | Resolves command-only, no skill |
| Skill without command (standalone) | P1 | Resolves skill-only, no command |
| ComponentTree.all_source_dirs | P1 | Correct deduplication, correct paths |
| PortifyProcess with additional_dirs | P1 | `--add-dir` args include all dirs |
| ComponentTree.to_flat_inventory() | P2 | Backward-compatible conversion |

### 6.3 Test Fixtures Required

A set of fixture skill/command/agent directories under `tests/cli_portify/fixtures/`:

```
fixtures/
  mock_project/
    src/superclaude/
      commands/
        mock-workflow.md          # Tier 0 command with Activation
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

---

## 7. Edge Cases

### 7.1 Commands Without Skills

Some commands (e.g., `help.md`, `sc.md`) have no paired skill. They contain inline behavioral logic only.

**Handling**: Resolution succeeds with `skill = None`. The `ComponentTree` has a populated `command` but empty skill/refs/agents. The portify pipeline can still analyze the command, though with limited material (it produces a simpler pipeline). A warning is emitted: "No paired skill found for command '<name>'. Analysis will be limited to the command file."

### 7.2 Skills Without Commands

Standalone skills (e.g., a utility skill invoked via `Skill` tool but never via `/sc:<name>`) have no command file.

**Handling**: Resolution succeeds with `command = None`. This is the backward-compatible path: the current behavior, plus the new agent discovery. No warning is needed because this was the original intended usage.

### 7.3 Multi-Skill Commands

A command could theoretically reference multiple skills (e.g., a meta-command that dispatches to different skills based on flags). The current convention uses a single `## Activation` section pointing to one skill.

**Handling**: The resolution algorithm extracts the primary skill from the `## Activation` section. If the command file contains additional `Skill <name>` references in other sections, those are recorded as `secondary_skills` in the `CommandEntry` but NOT automatically resolved into the component tree. A warning is emitted listing secondary skill references for manual review.

Rationale: Multi-skill commands are architecturally unusual and may require different portification strategies. Automatic full-tree resolution for all referenced skills could produce an unwieldy component tree. Better to let the user decide.

### 7.4 Circular or Diamond References

If Agent A's `.md` file references Agent B, and the skill also references Agent B directly, the agent should appear once in the tree (deduplication by name).

**Handling**: `AgentEntry` objects are deduplicated by `name`. If the same agent is referenced from multiple sources, the `referenced_in` field records the first source found, and a note is added to `resolution_log`.

### 7.5 Agent Files That Reference Other Agents

Some agents (e.g., `debate-orchestrator.md`) may reference other agents for delegation.

**Handling**: In v1 of this design, agent-to-agent references are NOT recursively resolved. The resolution algorithm scans the SKILL.md (and optionally the command file) for agent references, but does not recursively scan agent files. This keeps the algorithm simple and O(1)-depth. Recursive resolution can be added in a future iteration if needed.

### 7.6 Renamed or Missing Components

If a command's `## Activation` references a skill that does not exist:

**Handling**: `ERR_BROKEN_ACTIVATION` error. The pipeline halts. The error message includes the expected skill directory path and suggests checking the naming convention.

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Agent extraction regex misses references | Medium | Medium | Start with conservative patterns, add test cases for each real skill, iterate |
| Backward-compatible resolution breaks existing skill-dir workflows | Low | High | Extensive test coverage with existing fixture; `resolve_workflow_path()` preserved unchanged |
| `--add-dir` with many directories causes Claude subprocess issues | Low | Medium | Cap at 10 additional dirs; warn if more found |
| YAML frontmatter parsing failures in command/skill files | Low | Low | Graceful degradation: if frontmatter fails, still discover by convention |
| Project root detection fails in non-standard layouts | Medium | Low | Allow explicit `--commands-dir`, `--skills-dir`, `--agents-dir` overrides |
| Performance regression in Step 2 (scanning more files) | Low | Low | All operations are filesystem reads; even 50 files is sub-second |

---

## 9. Estimated Effort

| Phase | Description | Files Changed | New Files | Estimated Effort |
|-------|-------------|--------------|-----------|-----------------|
| 1 | New data models | `models.py` | `resolution.py` | 3-4 hours |
| 2 | Resolution algorithm | -- | `resolution.py` | 4-6 hours |
| 3 | Update `discover_components.py` | `discover_components.py` | -- | 3-4 hours |
| 4 | Update `PortifyProcess` | `process.py` | -- | 1-2 hours |
| 5 | Update CLI | `cli.py`, `config.py` | -- | 2-3 hours |
| 6 | Update `validate_config.py` | `validate_config.py` | -- | 2-3 hours |
| 7 | Tests | Multiple test files | `fixtures/mock_project/` | 6-8 hours |
| 8 | Integration testing | -- | -- | 2-3 hours |
| **Total** | | **~6 files modified** | **~2 new files + fixtures** | **23-33 hours** |

---

## 10. Open Questions

1. **Should agent-to-agent references be recursively resolved?** Current design says no (O(1)-depth). If a workflow has orchestrator agents that delegate to worker agents, and the worker agents are not referenced in SKILL.md, they will be missed. Is this acceptable for v1?

2. **Should the command frontmatter `mcp-servers` and `personas` fields be surfaced in the ComponentTree?** They could inform the portification analysis (e.g., which MCP servers the generated pipeline should integrate with). Current design captures them in `CommandEntry.frontmatter` but does not expose them as typed fields.

3. **How should the `--dry-run` output change?** Currently prints a simple plan. With the new resolution, it could print the full component tree summary. Is that desirable, or should it remain minimal?

4. **Should `resolve_target()` live in `resolution.py` (new file) or `config.py` (existing)?** The resolution logic is substantial enough to warrant its own module, but config.py already handles path resolution. Recommendation: new `resolution.py` module to maintain single responsibility.

5. **Should the `component-inventory.md` artifact retain its current format or adopt the tree format?** The analysis protocol (`refs/analysis-protocol.md`) expects a "Source Components" table with Command, Skill, Agent entries. The tree format naturally produces this. Recommendation: adopt tree format, which is a superset of the current format.

---

## 11. Relationship to Analysis Protocol

The `refs/analysis-protocol.md` file defines the discovery checklist that Phase 1 must follow:

| Protocol Step | Current Support | After This Change |
|--------------|----------------|-------------------|
| 1. Find the Command | Not supported | Fully resolved in R1 |
| 2. Find the Skill | Partially supported (only SKILL.md + subdirs) | Fully resolved in R2 + R4 |
| 3. Find the Agents | Not supported | Resolved in R3 |
| 4. Map the Data Flow | Not supported (no cross-dir awareness) | Enabled by ComponentTree + subprocess scoping |

The output format in the analysis protocol expects:

```markdown
## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Command | ... | ... | ... |
| Skill | ... | ... | ... |
| Agent: ... | ... | ... | ... |
| Ref: ... | ... | ... | ... |
```

The `ComponentTree` model directly supports rendering this table.

---

*End of Approach A Draft Spec*
