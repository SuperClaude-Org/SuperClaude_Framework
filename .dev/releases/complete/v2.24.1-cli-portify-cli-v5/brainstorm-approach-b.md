# Approach B: Manifest-Based Workflow Resolution

**Status**: DRAFT SPEC
**Date**: 2026-03-13
**Author**: System Architect (Opus 4.6)
**Scope**: cli-portify v5 -- Fixes Gaps 1, 2, 3 in workflow component resolution

---

## 1. Problem Statement

The `superclaude cli-portify run` command has three critical design gaps that prevent it from portifying real SuperClaude workflows:

**Gap 1 -- Input Target Too Narrow**: The command accepts ONLY a skill directory containing `SKILL.md`. A real SuperClaude workflow spans three tiers across three disjoint directory trees:

```
src/superclaude/commands/<name>.md          (Tier 0: Command)
src/superclaude/skills/sc-<name>-protocol/  (Tier 1: Skill + refs/ + rules/ + templates/ + scripts/)
src/superclaude/agents/<agent>.md           (Tier 2+: Agent delegation targets)
```

The command should accept a command name (e.g., `roadmap` or `cli-portify`) and resolve all tiers automatically.

**Gap 2 -- Discovery Only Inventories Skill Directory**: `discover_components.py` (Step 2) scans ONLY within the skill directory: `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/`, and loose `.md` files. It completely misses:
- The Tier 0 command `.md` file in `src/superclaude/commands/`
- Agent `.md` files in `src/superclaude/agents/` referenced by the skill
- Agent delegation patterns (parallel vs sequential, orchestrator vs worker)
- Cross-directory data flow between tiers

**Gap 3 -- Subprocess Scoping Too Limited**: `PortifyProcess._build_add_dir_args()` passes `--add-dir` for only two paths: `work_dir` (output) and `workflow_path` (skill dir). The `commands/` and `agents/` directories are NOT scoped into Claude subprocesses, so Steps 3-7 cannot read the full workflow context.

### Impact

These gaps mean the portification analysis (Step 3) operates on an incomplete picture of the workflow. The generated CLI pipeline will miss command-level arguments, agent delegation contracts, and cross-tier data flow -- producing an incorrect or incomplete portification.

---

## 2. Proposed Solution: Workflow Manifest

Introduce a **Workflow Manifest** as the canonical input unit for portification. The manifest is a structured document that enumerates every component participating in a workflow, their roles, their paths, and their relationships.

### Core Idea

Instead of the pipeline discovering components by walking a single directory at runtime, it first generates (or loads) a manifest that provides a complete, verified inventory of all components across all tiers. This manifest then drives every downstream step: discovery, subprocess scoping, analysis, and code generation.

### Two Modes of Operation

1. **Auto-generation**: Given a command name or path, resolve the manifest automatically by following the Tier 0 -> Tier 1 -> Tier 2 chain defined in `command-skill-policy.md`.
2. **Manual/pre-built**: Load a hand-authored or previously-generated manifest file, enabling custom component inclusion, partial portification, and cross-workflow composition.

### Key Design Principles

- The manifest is a **plain Markdown file with YAML frontmatter** -- consistent with every other SuperClaude artifact format.
- The manifest is a **reusable, versionable artifact** that can be committed, shared, and diffed.
- The manifest is **the single source of truth** for what a portification run will consume. If a component is not in the manifest, it does not participate.
- Auto-generation is **deterministic and fast** (no Claude subprocess, no inference).

---

## 3. Manifest Schema Definition

### 3.1 YAML Frontmatter

```yaml
---
manifest_version: "1.0"
workflow_name: roadmap                    # Canonical name (no sc- prefix, no -protocol suffix)
command_name: sc:roadmap                  # Full command invocation name
skill_name: sc:roadmap-protocol           # Full skill invocation name
generated_at: "2026-03-13T14:30:00Z"      # ISO 8601 timestamp
generated_by: auto                        # "auto" | "manual" | "hybrid"
source_root: /path/to/repo               # Repository root for relative path resolution
component_count: 14                       # Total component count
total_lines: 2847                         # Aggregate line count
tier_counts:
  command: 1
  skill: 1
  ref: 5
  rule: 0
  template: 0
  script: 0
  agent: 3
  other: 0
agent_delegation:
  pattern: parallel                       # "parallel" | "sequential" | "orchestrator-worker" | "none"
  agent_count: 3
complexity_estimate: high                 # "simple" | "moderate" | "high"
---
```

### 3.2 Markdown Body Structure

```markdown
# Workflow Manifest: {workflow_name}

## Tier 0: Command

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| roadmap.md | src/superclaude/commands/roadmap.md | 86 | Entry point, argument definition, skill dispatch |

## Tier 1: Skill

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| SKILL.md | src/superclaude/skills/sc-roadmap-protocol/SKILL.md | 847 | Full behavioral protocol |

### Tier 1.1: Refs

| Component | Path | Lines | Role | Loaded At |
|-----------|------|-------|------|-----------|
| extraction-pipeline.md | .../refs/extraction-pipeline.md | 210 | Extraction algorithm | Wave 1 |
| scoring.md | .../refs/scoring.md | 180 | Scoring rubric | Wave 2 |
| templates.md | .../refs/templates.md | 150 | Output format templates | Wave 3 |
| validation.md | .../refs/validation.md | 120 | Validation criteria | Wave 4 |
| adversarial-integration.md | .../refs/adversarial-integration.md | 95 | Multi-roadmap merge protocol | Wave 2 (conditional) |

### Tier 1.2: Rules

(none for this workflow)

### Tier 1.3: Templates

(none for this workflow)

### Tier 1.4: Scripts

(none for this workflow)

## Tier 2: Agents

| Agent | Path | Lines | Delegation Pattern | Used In |
|-------|------|-------|--------------------|---------|
| system-architect.md | src/superclaude/agents/system-architect.md | 245 | parallel | Wave 2 variant generation |
| requirements-analyst.md | src/superclaude/agents/requirements-analyst.md | 180 | parallel | Wave 1 extraction |
| debate-orchestrator.md | src/superclaude/agents/debate-orchestrator.md | 310 | orchestrator | Wave 3 adversarial merge |

## Cross-Tier Data Flow

```
[spec-input] --> Command (parse args, validate)
                    |
                    v
             Skill (Wave 0: setup)
                    |
                    v
          Ref: extraction-pipeline.md
                    |
                    v
             Skill (Wave 1: extract)
            /       |        \
           v        v         v
    [agent-1]  [agent-2]  [agent-3]   (parallel variant generation)
           \        |        /
                    v
          Ref: scoring.md
                    |
                    v
             Skill (Wave 2: score + select)
                    |
                    v
          Ref: templates.md
                    |
                    v
             Skill (Wave 3: synthesize)
                    |
                    v
          Ref: validation.md
                    |
                    v
             Skill (Wave 4: validate)
                    |
                    v
              [roadmap.md, extraction.md, test-strategy.md]
```

## Resolution Log

How this manifest was generated:

1. Input: `roadmap` (resolved to command `src/superclaude/commands/roadmap.md`)
2. Parsed command frontmatter: found `Skill sc:roadmap-protocol` in Activation section
3. Resolved skill directory: `src/superclaude/skills/sc-roadmap-protocol/`
4. Scanned skill subdirectories: refs/ (5 files), rules/ (0), templates/ (0), scripts/ (0)
5. Parsed SKILL.md for agent references: found 3 agent references
6. Resolved agents: system-architect.md, requirements-analyst.md, debate-orchestrator.md
7. Manifest generated in 0.12s
```

---

## 4. Detailed Design: Gap 1 Fix -- Expanded Input Resolution

### 4.1 New Input Modes

The `run` command accepts a `WORKFLOW_TARGET` that can be any of:

| Input Form | Example | Resolution Strategy |
|------------|---------|---------------------|
| Command name (bare) | `roadmap` | Look up `src/superclaude/commands/roadmap.md` |
| Command name (prefixed) | `sc:roadmap` | Strip `sc:` prefix, look up command file |
| Command file path | `src/superclaude/commands/roadmap.md` | Use directly as Tier 0 entry |
| Skill directory path | `src/superclaude/skills/sc-roadmap-protocol/` | Current behavior (backward compat) |
| Skill name | `sc-roadmap-protocol` | Resolve to skill directory |
| Manifest file path | `manifests/roadmap-manifest.md` | Load pre-built manifest directly |

### 4.2 Resolution Algorithm

```
resolve_workflow_target(target: str) -> ManifestSource:

  1. If target ends with "-manifest.md" or contains manifest_version frontmatter:
     -> return ManifestSource(mode=PREBUILT, path=target)

  2. If target is a path to a .md file:
     a. If filename matches a known command in src/superclaude/commands/:
        -> return ManifestSource(mode=FROM_COMMAND, command_path=target)
     b. If filename is SKILL.md:
        -> return ManifestSource(mode=FROM_SKILL, skill_dir=target.parent)

  3. If target is a directory path containing SKILL.md:
     -> return ManifestSource(mode=FROM_SKILL, skill_dir=target)

  4. If target is a bare name (no path separators, no extension):
     a. Check src/superclaude/commands/{target}.md exists:
        -> return ManifestSource(mode=FROM_COMMAND, command_path=...)
     b. Check src/superclaude/skills/sc-{target}-protocol/ exists:
        -> return ManifestSource(mode=FROM_SKILL, skill_dir=...)
     c. Check src/superclaude/skills/{target}/ exists:
        -> return ManifestSource(mode=FROM_SKILL, skill_dir=...)

  5. If target starts with "sc:":
     Strip prefix, retry from step 4.

  6. Raise ResolutionError with candidates list.
```

### 4.3 CLI Changes

```python
# Current:
@click.argument("workflow_path", type=click.Path(exists=True))

# Proposed:
@click.argument("workflow_target")  # No exists=True -- resolution handles validation
@click.option("--manifest", type=click.Path(exists=True),
              help="Use a pre-built manifest file instead of auto-generating")
@click.option("--save-manifest", type=click.Path(),
              help="Save the generated manifest to this path for reuse")
@click.option("--include-agent", multiple=True,
              help="Include additional agent(s) not auto-discovered")
@click.option("--exclude-component", multiple=True,
              help="Exclude component(s) from the manifest by name")
```

### 4.4 New `--manifest` and `--save-manifest` Flags

- `--manifest path/to/manifest.md`: Skip auto-resolution entirely. Load the manifest and use it as-is. Validation still runs (paths must exist, frontmatter must parse).
- `--save-manifest path/to/manifest.md`: After auto-resolution, write the generated manifest to the specified path before proceeding. Useful for debugging, sharing, and iterating.
- Both flags can be combined: `--manifest` loads, modifies via `--include-agent`/`--exclude-component`, then `--save-manifest` persists the modified version.

---

## 5. Detailed Design: Gap 2 Fix -- Manifest-Driven Discovery

### 5.1 New Module: `manifest.py`

Replaces the role of `discover_components.py` as the primary discovery mechanism. Located at `src/superclaude/cli/cli_portify/manifest.py`.

#### Core Functions

```python
@dataclass
class WorkflowManifest:
    """Complete workflow manifest with all tiers."""
    manifest_version: str = "1.0"
    workflow_name: str = ""
    command_name: str = ""
    skill_name: str = ""
    generated_at: str = ""
    generated_by: Literal["auto", "manual", "hybrid"] = "auto"
    source_root: Path = field(default_factory=lambda: Path("."))

    command: ManifestComponent | None = None
    skill: ManifestComponent | None = None
    refs: list[ManifestComponent] = field(default_factory=list)
    rules: list[ManifestComponent] = field(default_factory=list)
    templates: list[ManifestComponent] = field(default_factory=list)
    scripts: list[ManifestComponent] = field(default_factory=list)
    agents: list[AgentComponent] = field(default_factory=list)
    other: list[ManifestComponent] = field(default_factory=list)

    # Derived
    agent_delegation_pattern: str = "none"
    complexity_estimate: str = "simple"
    resolution_log: list[str] = field(default_factory=list)

    @property
    def all_components(self) -> list[ManifestComponent]:
        """Flat list of all components across all tiers."""
        ...

    @property
    def all_directories(self) -> set[Path]:
        """Unique parent directories of all components -- used for --add-dir scoping."""
        ...

    @property
    def component_count(self) -> int: ...

    @property
    def total_lines(self) -> int: ...

    @property
    def tier_counts(self) -> dict[str, int]: ...

    def to_inventory(self) -> ComponentInventory:
        """Convert to legacy ComponentInventory for backward compatibility."""
        ...


@dataclass
class ManifestComponent:
    """A single component in the manifest."""
    name: str
    path: Path
    component_type: str  # "command" | "skill" | "ref" | "rule" | "template" | "script" | "agent" | "other"
    line_count: int
    purpose: str = ""
    loaded_at: str = ""  # Phase/wave when loaded (for refs)


@dataclass
class AgentComponent(ManifestComponent):
    """Agent component with delegation metadata."""
    delegation_pattern: str = ""  # "parallel" | "sequential" | "orchestrator" | "worker"
    used_in: str = ""             # Which phases/steps reference this agent
```

#### Auto-Generation Pipeline

```python
def generate_manifest(
    target: str,
    source_root: Path,
    include_agents: list[str] | None = None,
    exclude_components: list[str] | None = None,
) -> WorkflowManifest:
    """Generate a complete workflow manifest from a target identifier.

    Steps:
    1. Resolve target to ManifestSource (command path, skill dir, or pre-built)
    2. If FROM_COMMAND: parse command .md, extract skill reference from ## Activation
    3. Resolve skill directory from skill name
    4. Scan skill directory (SKILL.md, refs/, rules/, templates/, scripts/)
    5. Parse SKILL.md for agent references (regex for agent .md file names)
    6. Resolve agent paths in src/superclaude/agents/
    7. Apply include/exclude overrides
    8. Compute metadata (line counts, complexity estimate, delegation pattern)
    9. Return populated WorkflowManifest
    """
```

#### Agent Reference Extraction

Agents are referenced in SKILL.md via several patterns. The extractor uses heuristic regex matching:

```python
def extract_agent_references(skill_content: str) -> list[str]:
    """Extract agent names referenced in a SKILL.md file.

    Patterns matched:
    - "Agent: <name>" or "agent: <name>" in tables
    - "agents/<name>.md" path references
    - "Task tool" delegations naming an agent
    - "## Agent Delegation" section entries
    - Frontmatter personas list (mapped to known agent files)
    """
```

This is heuristic, not perfect. The manifest can always be manually corrected via `--include-agent` or by editing the saved manifest.

### 5.2 Changes to `discover_components.py`

`discover_components.py` is NOT deleted. It becomes a thin adapter:

```python
def run_discover_components(
    config: PortifyConfig,
    manifest: WorkflowManifest | None = None,  # NEW parameter
    workflow_path: Path | None = None,
    output_dir: Path | None = None,
) -> tuple[ComponentInventory, PortifyStepResult]:
    """Execute the discover-components step.

    If a manifest is provided, convert it to ComponentInventory directly.
    Otherwise, fall back to legacy directory-only scanning.
    """
    if manifest is not None:
        inventory = manifest.to_inventory()
        # ... write artifact, build step result
    else:
        # Legacy path (backward compatibility)
        # ... existing directory scanning logic
    ...
```

This preserves all existing tests while enabling the new manifest path.

### 5.3 Manifest Persistence

The manifest is written as an artifact at Step 0 (new step) or Step 1 (augmented):

- File: `{results_dir}/workflow-manifest.md`
- Format: YAML frontmatter + Markdown body (as defined in Section 3)
- The manifest artifact is then passed as an `@path` reference to all subsequent Claude-assisted steps

---

## 6. Detailed Design: Gap 3 Fix -- Manifest-Driven Subprocess Scoping

### 6.1 Changes to `PortifyProcess`

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
        manifest: WorkflowManifest | None = None,  # NEW
        artifact_refs: list[Path] | None = None,
        # ... rest unchanged
    ):
        self._manifest = manifest
        # ... existing init

    def _build_add_dir_args(self) -> list[str]:
        """Build --add-dir arguments from manifest directories.

        If a manifest is present, scope ALL unique parent directories
        of manifest components. This ensures the Claude subprocess can
        read commands/, skills/, and agents/ directories.

        Falls back to legacy dual-dir scoping if no manifest.
        """
        args: list[str] = []

        if self._manifest is not None:
            # Collect all unique directories from manifest components
            dirs = self._manifest.all_directories
            # Always include work_dir
            dirs.add(self._work_dir)
            for d in sorted(dirs):
                args.extend(["--add-dir", str(d)])
        else:
            # Legacy: work_dir + workflow_path only
            args.extend(["--add-dir", str(self._work_dir)])
            if self._workflow_path != self._work_dir:
                args.extend(["--add-dir", str(self._workflow_path)])

        return args
```

### 6.2 Scoping Example

For the `roadmap` workflow, the manifest would produce these `--add-dir` entries:

```
--add-dir /repo/src/superclaude/commands/        (Tier 0)
--add-dir /repo/src/superclaude/skills/sc-roadmap-protocol/       (Tier 1)
--add-dir /repo/src/superclaude/skills/sc-roadmap-protocol/refs/  (Tier 1.1)
--add-dir /repo/src/superclaude/agents/          (Tier 2)
--add-dir /repo/output/                          (work_dir)
```

### 6.3 Directory Deduplication

The `all_directories` property on `WorkflowManifest` returns deduplicated parent directories. If a parent directory already covers a subdirectory (e.g., `skills/sc-roadmap-protocol/` covers `skills/sc-roadmap-protocol/refs/`), the implementation should check whether `--add-dir` is recursive or flat. If flat, include subdirectories explicitly. If recursive, only the parent is needed.

**Decision needed**: Verify `claude -p --add-dir` scoping semantics (recursive vs flat). Design assumes flat (subdirectories need explicit inclusion) as the safer default.

---

## 7. Data Model Changes

### 7.1 New Dataclass: `WorkflowManifest` (in `manifest.py`)

See Section 5.1 for full definition. This is the primary new data structure.

### 7.2 Changes to `PortifyConfig` (in `models.py`)

```python
@dataclass
class PortifyConfig(PipelineConfig):
    workflow_path: Path = field(default_factory=lambda: Path("."))
    workflow_target: str = ""           # NEW: raw user input before resolution
    manifest_path: Path | None = None   # NEW: path to pre-built manifest
    save_manifest_path: Path | None = None  # NEW: where to save generated manifest
    include_agents: list[str] = field(default_factory=list)   # NEW
    exclude_components: list[str] = field(default_factory=list)  # NEW
    output_dir: Path = field(default_factory=lambda: Path("."))
    cli_name: str = ""
    skip_review: bool = False
    start_step: str | None = None
    iteration_timeout: int = 300
    max_convergence: int = 3

    def resolve_workflow_path(self) -> Path:
        """Resolve and validate the workflow path.

        CHANGED: Now supports resolution from command name, not just SKILL.md.
        If workflow_target is set but workflow_path is default, resolve
        workflow_target first to find the skill directory.

        Legacy behavior preserved: if workflow_path points to a directory
        with SKILL.md, returns that directory as before.
        """
        ...
```

### 7.3 Changes to `ComponentInventory` (in `models.py`)

```python
@dataclass
class ComponentInventory:
    source_skill: str = ""
    source_command: str = ""            # NEW: Tier 0 command name
    components: list[ComponentEntry] = field(default_factory=list)
    agents: list[ComponentEntry] = field(default_factory=list)  # NEW: separated for clarity
    manifest_path: str = ""             # NEW: path to the manifest that generated this inventory
```

### 7.4 Changes to `ComponentEntry` (in `models.py`)

```python
@dataclass
class ComponentEntry:
    name: str
    path: str
    component_type: str
    line_count: int
    purpose: str = ""                   # NEW: human-readable purpose
    tier: int = 1                       # NEW: 0=command, 1=skill/ref/rule/template/script, 2=agent
```

---

## 8. New Step: Step 0 -- Resolve Manifest

### 8.1 Rationale

Manifest resolution is a separate, deterministic step that runs before `validate-config` (Step 1). It needs its own step because:
- It can fail independently (command not found, ambiguous name, agent resolution failure)
- It produces a distinct artifact (the manifest file)
- It has different error codes and recovery strategies than config validation

### 8.2 Step Definition

```
Step 0: resolve-manifest
  Type: pure-programmatic (no Claude subprocess)
  Input: workflow_target (from CLI), source_root (repo root)
  Output: workflow-manifest.md artifact
  Gate: EXEMPT (deterministic)
  Timing: must complete under 2s (SC-000)
  Error codes:
    ERR_TARGET_NOT_FOUND    -- no matching command or skill
    ERR_AMBIGUOUS_TARGET    -- multiple candidates
    ERR_SKILL_NOT_FOUND     -- command found but referenced skill missing
    ERR_AGENT_NOT_FOUND     -- referenced agent .md file missing (warning, not fatal)
    ERR_MANIFEST_PARSE      -- pre-built manifest has invalid structure
```

### 8.3 Step Ordering

```
Step 0: resolve-manifest     (NEW -- deterministic)
Step 1: validate-config      (MODIFIED -- receives manifest)
Step 2: discover-components  (MODIFIED -- delegates to manifest)
Step 3+: unchanged           (receive manifest via artifact refs)
```

Step 1 (`validate-config`) now receives the manifest and can validate the CLI name derivation from either the command name or skill name. The `resolve_workflow_path()` method in `PortifyConfig` is updated to work with the resolved manifest.

---

## 9. Advanced Use Cases Enabled by Manifest

### 9.1 Multi-Skill Commands

Some commands dispatch to multiple skills (e.g., a hypothetical `sc:full-audit` that invokes both `sc:cleanup-audit-protocol` and `sc:adversarial-protocol`). The manifest format supports this by allowing multiple entries in the Tier 1 section. The CLI supports `--include-skill` to add additional skill directories.

### 9.2 Partial Portification

A user may want to portify only a subset of the workflow. The `--exclude-component` flag removes components from the manifest before portification begins. Example:

```bash
superclaude cli-portify run roadmap --exclude-component validation.md --exclude-component adversarial-integration.md
```

This produces a manifest that omits the validation ref and adversarial integration ref, resulting in a simpler pipeline without Wave 4 validation or multi-roadmap support.

### 9.3 Custom Component Inclusion

A user may have custom agents or refs not discovered by auto-resolution. The `--include-agent` flag adds them:

```bash
superclaude cli-portify run roadmap --include-agent custom-reviewer.md
```

### 9.4 Manifest as Reusable Artifact

The manifest can be:
- **Committed to version control**: `manifests/roadmap-v2.md` alongside the workflow
- **Shared across teams**: "Use this manifest to portify the roadmap workflow"
- **Diffed between versions**: See exactly what changed in the workflow's component graph
- **Used in CI**: Validate that manifests are up-to-date with the actual component tree
- **Iterated manually**: Save with `--save-manifest`, edit, re-run with `--manifest`

### 9.5 Manifest Staleness Detection

When loading a pre-built manifest, the system can optionally verify that all listed paths still exist and that no new components have appeared in the expected directories. This is a `--validate-manifest` flag that runs a quick diff between the manifest and the filesystem.

---

## 10. Migration and Backward Compatibility

### 10.1 Backward Compatibility Guarantee

The existing invocation pattern MUST continue to work:

```bash
# This still works -- resolved as FROM_SKILL mode
superclaude cli-portify run src/superclaude/skills/sc-cleanup-audit/
```

When a skill directory is passed directly (existing behavior), the system:
1. Detects FROM_SKILL mode
2. Attempts reverse-resolution to find the matching command file (best-effort, not required)
3. Generates a manifest with the skill as the anchor (command may be absent)
4. Proceeds as normal

### 10.2 Migration Path

**Phase A (non-breaking)**: Add `manifest.py`, `WorkflowManifest`, and the resolution algorithm. Add `--manifest` and `--save-manifest` flags to CLI. The `discover_components.py` adapter delegates to manifest when present.

**Phase B (non-breaking)**: Update `PortifyProcess` to accept and use manifest for `--add-dir` scoping. Existing behavior unchanged when no manifest.

**Phase C (breaking -- minor)**: Change `WORKFLOW_PATH` argument semantics from `click.Path(exists=True)` to a free-form `WORKFLOW_TARGET` string. This is technically breaking because `click.Path(exists=True)` validates at parse time, while the new resolver validates at Step 0. Error messages will differ.

**Phase D (cleanup)**: Deprecation warning when skill-directory-only input is used without a matching command file. Encourage command-name-based invocation.

### 10.3 Test Migration

All existing tests in `tests/cli_portify/test_discover_components.py` continue to pass because:
- The `run_discover_components` function retains its legacy path when `manifest=None`
- Test fixtures create skill directories with SKILL.md (the FROM_SKILL path)
- No test depends on the CLI argument parser rejecting non-path inputs

New tests are added for:
- Manifest auto-generation from command names
- Manifest loading from pre-built files
- Agent reference extraction from SKILL.md content
- Resolution algorithm for all input forms
- Subprocess scoping with manifest-derived directories
- Round-trip: generate manifest -> save -> load -> compare

---

## 11. Impact on Existing Tests

### 11.1 Tests That Pass Unchanged

| Test File | Reason |
|-----------|--------|
| `test_validate_config.py` | Config validation logic unchanged; manifest is upstream |
| `test_discover_components.py` | Legacy path preserved; all fixtures use skill directories |
| `test_config.py` | `load_portify_config()` signature gains optional params with defaults |
| `test_gates.py` | Gate logic is independent of discovery |
| `test_prompts.py` | Prompt construction independent of discovery |
| `test_monitor.py` | TUI monitoring independent of discovery |
| `test_mock_harness.py` | Mock infrastructure unchanged |

### 11.2 Tests That Need Modification

| Test File | Change Required |
|-----------|----------------|
| `test_process.py` | Add tests for manifest-driven `--add-dir` scoping. Existing tests pass (no manifest = legacy path). |
| `test_contracts.py` | Update contract expectations if `ComponentInventory` gains new fields. |
| `integration/test_orchestration.py` | Update to test manifest flow through the full pipeline. |

### 11.3 New Test Files

| Test File | Coverage |
|-----------|----------|
| `test_manifest.py` | `WorkflowManifest` dataclass, `generate_manifest()`, `load_manifest()`, `save_manifest()` |
| `test_resolution.py` | `resolve_workflow_target()` for all input forms, error cases, ambiguity detection |
| `test_agent_extraction.py` | `extract_agent_references()` regex patterns against real SKILL.md content |

### 11.4 Estimated New Test Count

- `test_manifest.py`: ~20 tests (dataclass, serialization, round-trip, to_inventory adapter)
- `test_resolution.py`: ~15 tests (6 input forms x success + failure + edge cases)
- `test_agent_extraction.py`: ~10 tests (various SKILL.md patterns, no-agents case, malformed content)
- Additions to `test_process.py`: ~5 tests (manifest scoping, directory deduplication)

Total new tests: ~50

---

## 12. Risk Assessment

### 12.1 High Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent extraction heuristic is unreliable | Missing agents in manifest -> incomplete portification | Make agent extraction best-effort with warnings. Provide `--include-agent` escape hatch. Log all extraction decisions in resolution log. |
| `--add-dir` explosion with many directories | Claude subprocess may hit argument limits or performance issues | Cap at 10 `--add-dir` entries. If manifest has more, consolidate to common parent directories. |

### 12.2 Medium Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking change to CLI argument semantics | Users with scripts targeting `cli-portify run <path>` | Phase C is explicit. Deprecation warning in Phase D. Old path continues to work. |
| Manifest format evolution | Future schema changes break saved manifests | `manifest_version` field enables forward-compatible parsing. Version 1.0 manifests always loadable. |
| Reverse-resolution from skill to command is fragile | Some skills may not have matching commands (standalone skills) | Reverse-resolution is best-effort. Missing command is a warning, not an error. |

### 12.3 Low Risk

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance regression in Step 0 | Manifest generation adds time before pipeline starts | Manifest generation is pure filesystem operations. 2s budget is generous. |
| Manifest artifact bloats results directory | One more file in results/ | Manifest is typically <5KB. Negligible. |

---

## 13. Estimated Effort

### 13.1 New Code

| Component | Files | Estimated Lines | Complexity |
|-----------|-------|-----------------|------------|
| `manifest.py` (data model + generation) | 1 | 350-450 | Moderate |
| `resolution.py` (target resolution algorithm) | 1 | 150-200 | Moderate |
| `agent_extraction.py` (SKILL.md parsing) | 1 | 100-150 | Low-Moderate |
| Step 0: `resolve_manifest.py` | 1 | 100-150 | Low |
| CLI changes in `cli.py` | 1 (modify) | +30-50 | Low |

### 13.2 Modified Code

| Component | Estimated Change | Complexity |
|-----------|-----------------|------------|
| `models.py` -- PortifyConfig, ComponentInventory, ComponentEntry | +40-60 lines | Low |
| `discover_components.py` -- manifest adapter | +20-30 lines | Low |
| `process.py` -- manifest-driven scoping | +30-40 lines | Low |
| `config.py` -- new parameters | +15-20 lines | Low |

### 13.3 Tests

| Component | Estimated Tests | Estimated Lines |
|-----------|----------------|-----------------|
| `test_manifest.py` | ~20 | 300-400 |
| `test_resolution.py` | ~15 | 250-350 |
| `test_agent_extraction.py` | ~10 | 150-200 |
| Additions to existing tests | ~10 | 100-150 |

### 13.4 Total Estimate

- **New code**: ~730-1050 lines across 4-5 new files
- **Modified code**: ~105-170 lines across 4 existing files
- **New tests**: ~800-1100 lines across 3 new files + modifications
- **Total**: ~1635-2320 lines
- **Estimated implementation time**: 2-3 focused sessions (assuming one session = ~2 hours of productive implementation)

---

## 14. Open Questions

1. **`--add-dir` recursion semantics**: Does `claude -p --add-dir /path/` recursively include subdirectories, or only files directly in that directory? This determines whether we need to include both `skills/sc-roadmap-protocol/` and `skills/sc-roadmap-protocol/refs/` separately.

2. **Agent delegation pattern detection**: How reliably can we detect whether agents are used in parallel vs sequential from SKILL.md prose? Should we default to "unknown" and let the user correct in the manifest?

3. **Source root detection**: Should source_root be auto-detected via `git rev-parse --show-toplevel`, or should it be an explicit parameter? Git-based detection is fragile in worktree setups.

4. **Manifest caching**: Should generated manifests be cached (e.g., in `.dev/cache/manifests/`) so repeated `--dry-run` invocations don't re-resolve? The resolution is fast (<2s) so this may be premature optimization.

5. **Validation of agent paths**: When an agent reference is extracted from SKILL.md but the corresponding `.md` file does not exist in `src/superclaude/agents/`, should this be a warning (continue with reduced manifest) or an error (abort)?

---

## 15. Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Manifest format | Markdown + YAML frontmatter | Consistent with all SuperClaude artifacts; human-readable; diff-friendly |
| Primary input mode | Command name (bare string) | Most natural for users; matches `/sc:<name>` invocation pattern |
| Backward compatibility | Skill-directory input still works | Non-breaking migration; existing scripts preserved |
| Agent extraction | Heuristic regex, best-effort | Perfect extraction is impossible without executing the skill; escape hatch via `--include-agent` |
| Step ordering | New Step 0 before existing Step 1 | Clean separation of concerns; independent error handling |
| Legacy `discover_components.py` | Adapter pattern, not deleted | All existing tests pass; gradual migration |
| Subprocess scoping | All manifest directories via `--add-dir` | Claude subprocess needs access to all tiers |

---

## Appendix A: Example Manifest for `cli-portify` Workflow

This is the manifest that `superclaude cli-portify run cli-portify --save-manifest` would produce -- a self-referential portification:

```yaml
---
manifest_version: "1.0"
workflow_name: cli-portify
command_name: sc:cli-portify
skill_name: sc:cli-portify-protocol
generated_at: "2026-03-13T15:00:00Z"
generated_by: auto
source_root: /config/workspace/IronClaude
component_count: 7
total_lines: 1842
tier_counts:
  command: 1
  skill: 1
  ref: 3
  rule: 0
  template: 0
  script: 0
  agent: 0
  other: 1
agent_delegation:
  pattern: none
  agent_count: 0
complexity_estimate: high
---
```

```markdown
# Workflow Manifest: cli-portify

## Tier 0: Command

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| cli-portify.md | src/superclaude/commands/cli-portify.md | 120 | Entry point, argument validation, skill dispatch |

## Tier 1: Skill

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| SKILL.md | src/superclaude/skills/sc-cli-portify-protocol/SKILL.md | 850 | Full portification behavioral protocol |

### Tier 1.1: Refs

| Component | Path | Lines | Role | Loaded At |
|-----------|------|-------|------|-----------|
| analysis-protocol.md | .../refs/analysis-protocol.md | 216 | Workflow decomposition algorithm | Phase 1 |
| pipeline-spec.md | .../refs/pipeline-spec.md | 340 | Pipeline specification format | Phase 2 |
| code-templates.md | .../refs/code-templates.md | 280 | Python code generation templates | Phase 3 |

### Tier 1.4: Other

| Component | Path | Lines | Role |
|-----------|------|-------|------|
| decisions.yaml | .../decisions.yaml | 36 | Architectural decision log |

## Tier 2: Agents

(none -- cli-portify does not delegate to agents)

## Resolution Log

1. Input: `cli-portify` (resolved to command `src/superclaude/commands/cli-portify.md`)
2. Parsed command: found `Skill sc:cli-portify-protocol` in Activation section
3. Resolved skill: `src/superclaude/skills/sc-cli-portify-protocol/`
4. Scanned subdirectories: refs/ (3), rules/ (0), templates/ (0), scripts/ (0)
5. Parsed SKILL.md: no agent references found
6. Manifest generated in 0.08s
```

---

## Appendix B: Comparison with Approach A (Runtime Chain-Walking)

| Dimension | Approach A (Runtime) | Approach B (Manifest) |
|-----------|---------------------|----------------------|
| Discoverability | Walk chain at runtime in Step 2 | Generate manifest in Step 0 |
| Persistence | Transient (in-memory only) | Artifact on disk (versionable) |
| Editability | None -- what you discover is what you get | Full -- edit manifest, re-run |
| Reusability | None -- re-discovers every run | Full -- save and reload |
| Debugging | Read Step 2 logs | Read the manifest file directly |
| Partial portification | Not supported | Supported via exclude flags |
| Multi-skill | Not supported without major refactor | Supported via manifest structure |
| Backward compat | Breaking -- Step 2 behavior changes | Non-breaking -- adapter pattern |
| Complexity | Lower (fewer new files) | Higher (new data model, new step) |
| Correctness ceiling | Limited by heuristics at runtime | Same heuristics, but user can correct |

**Verdict**: Approach B trades ~500 more lines of code for significantly better debuggability, reusability, and extensibility. The manifest-as-artifact pattern aligns with SuperClaude's existing artifact-driven pipeline philosophy.
