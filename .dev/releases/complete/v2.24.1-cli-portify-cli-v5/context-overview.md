---
title: "v2.24.1 Context Overview: CLI-Portify Input Target Gap"
severity: HIGH
affects: src/superclaude/cli/cli_portify/
discovered: 2026-03-13
discovered_by: user + analysis session
status: remediation-in-progress
parent_release: v2.24-cli-portify-cli-v4
---

# Context Overview: CLI-Portify Input Target Gap

## 1. Discovery Summary

During post-release analysis of v2.24 (`superclaude cli-portify`), a fundamental design-level gap was identified: **the command portifies individual skill directories, not complete SuperClaude workflows**. This is a spec-inherited gap — the original `portify-release-spec.md` defined the input as "a skill directory containing `SKILL.md`", which does not match the actual portification target.

The `sc:cli-portify-protocol` skill (`analysis-protocol.md`) explicitly defines a 4-step discovery checklist:
1. Find the **Command** in `src/superclaude/commands/`
2. Find the **Skill** in `src/superclaude/skills/`
3. Find all **Agents** referenced in the skill
4. Map the full **data flow** across all components

The v2.24 Python implementation only performs step 2.

---

## 2. SuperClaude Workflow Architecture

A "workflow" in SuperClaude is not a single file — it is a multi-component system spanning 3 tiers and multiple directories:

```
src/superclaude/
  commands/<name>.md              <-- Tier 0: Command (thin entry point, ~150 lines)
                                      Auto-loaded on /sc:<name>
                                      Contains: frontmatter, usage, activation section
                                      Activation: "Skill sc:<name>-protocol"
  skills/sc-<name>-protocol/      <-- Tier 1: Skill (full behavioral spec, unlimited)
    SKILL.md                           Loaded on-demand via Skill tool
    refs/                              Step-specific reference documents
    rules/                             Validation rules and taxonomies
    templates/                         Output format templates
    scripts/                           Shell scripts for preprocessing
  agents/<agent-name>.md          <-- Cross-cutting: Agent definitions
                                      Referenced by skills for delegation
                                      Contains: triggers, tools, responsibilities, boundaries
```

### Example: `sc:roadmap` workflow

| Component | Location | Role |
|-----------|----------|------|
| Command | `commands/roadmap.md` | Thin entry point, dispatches to skill |
| Skill | `skills/sc-roadmap-protocol/SKILL.md` | 5-wave roadmap generation protocol |
| Ref: templates | `skills/sc-roadmap-protocol/refs/templates.md` | Roadmap/extraction body templates |
| Ref: adversarial | `skills/sc-roadmap-protocol/refs/adversarial-integration.md` | Multi-roadmap debate integration |
| Agent: architect | `agents/system-architect.md` | Architectural analysis persona |
| Agent: scribe | `agents/technical-writer.md` | Documentation generation persona |
| Cross-skill: adversarial | `skills/sc-adversarial-protocol/SKILL.md` | Invoked by roadmap for multi-spec/multi-roadmap |

A correct portification of `sc:roadmap` must analyze ALL of these components to understand the full behavioral flow, delegation patterns, and data dependencies.

---

## 3. Three Specific Gaps

### Gap 1: Input Target Too Narrow

**Current behavior**: `superclaude cli-portify run <WORKFLOW_PATH>` requires a directory containing `SKILL.md`.

```python
# cli.py
@click.argument("workflow_path", type=click.Path(exists=True))

# models.py — resolve_workflow_path()
skill_file = resolved / "SKILL.md"
if not skill_file.exists():
    raise ValueError(f"No SKILL.md found in workflow directory: {resolved}")
```

**Expected behavior**: Accept a command name (e.g., `sc:roadmap`), a command file path (e.g., `commands/roadmap.md`), OR a skill directory — and resolve the complete component tree from whichever entry point is provided.

**Evidence from protocol**: The `analysis-protocol.md` ref starts with "Find the Command" as Step 1, not "Find the Skill".

### Gap 2: Discovery Step Only Inventories Skill Directory

**Current behavior**: `discover_components.py` scans only within the skill directory:

| Component | Discovered | Source |
|-----------|-----------|--------|
| SKILL.md | Yes | Direct file check |
| refs/ | Yes | Directory listing |
| rules/ | Yes | Directory listing |
| templates/ | Yes | Directory listing |
| scripts/ | Yes | Directory listing |
| Command .md | **No** | Not scanned |
| Agent .md files | **No** | Not scanned |
| Agent delegation patterns | **No** | Not analyzed |
| Cross-skill references | **No** | Not analyzed |
| Matching command files | **Partial** | Listed in spec but not in v2.24 implementation |

**Evidence from protocol**: `analysis-protocol.md` Section "3. Find the Agents" explicitly requires:
> Search for agents referenced in the skill. Look in `src/superclaude/agents/` for `.md` files. Note each agent's: triggers, tools, responsibilities, boundaries. Identify delegation patterns: parallel vs sequential, orchestrator vs worker.

The analysis output template includes:
- `source_command: <command-name>` in frontmatter
- `agent_count: <N>` in frontmatter
- `## Agent Delegation Map` section with `Agent | Used In Steps | Parallel | Contract` table

None of this is populated by the current discovery step.

### Gap 3: Subprocess Scoping Too Limited

**Current behavior**: `PortifyProcess` only adds two directories to Claude's scope:

```python
# process.py (conceptual)
args.extend(["--add-dir", str(self._work_dir)])      # output artifacts
args.extend(["--add-dir", str(self._workflow_path)])  # skill directory ONLY
```

**Impact**: When Claude runs Steps 3-7 (the Claude-assisted steps), it CANNOT read:
- `src/superclaude/commands/` — the command file
- `src/superclaude/agents/` — agent definitions
- Any cross-skill dependencies (e.g., `sc-adversarial-protocol/` referenced by `sc-roadmap-protocol/`)

Even if the prompts instructed Claude to analyze these files, Claude would get "file not found" or "outside allowed directories" errors.

---

## 4. Impact Assessment

### Severity: HIGH

This is not a bug in a specific module — it is a **design-level gap inherited from the spec**. The portify-release-spec.md defined the input narrowly, and the implementation correctly followed that narrow definition.

### What works correctly

Everything the v2.24 pipeline does with skill-directory-scoped input works well:
- Config validation, name derivation, output writability, collision detection
- Skill directory component inventory with line counts
- Gate system, convergence engine, contracts, resume, TUI
- The entire subprocess orchestration platform

### What produces incorrect results

Any portification that depends on understanding the full workflow:
- Step 3 (analyze-workflow) produces an incomplete analysis — no command frontmatter, no agent delegation map
- Step 4 (design-pipeline) designs a pipeline based on incomplete input
- Steps 5-7 build on the incomplete foundation

### Practical consequence

Running `superclaude cli-portify run src/superclaude/skills/sc-roadmap-protocol/` would produce a release spec that describes a pipeline for `SKILL.md` alone, missing:
- The 5-wave orchestration context from `commands/roadmap.md`
- The adversarial integration via `sc-adversarial-protocol`
- Agent delegation to `system-architect`, `technical-writer`, `analyzer`
- Template loading patterns from `refs/templates.md` (these ARE discovered, but their relationship to the command is not)

---

## 5. Root Cause Analysis

| Factor | Detail |
|--------|--------|
| Spec definition | `portify-release-spec.md` Section 5.1 defines `WORKFLOW` as `PATH (argument) - Path to skill directory to portify` |
| Protocol awareness | The `analysis-protocol.md` ref knows about all 3 tiers but the Python runner doesn't use it for discovery |
| Naming confusion | "Workflow" was used to mean "skill directory" in the spec, but "skill + command + agents" in the protocol |
| Scope creep avoidance | The spec deliberately constrained scope to "one skill directory" for v2.24 feasibility |
| Claude subprocess scoping | `--add-dir` was modeled after existing CLI runners (roadmap, sprint) which operate on single artifacts |

---

## 6. Remediation Strategy

Three capabilities must be added:

1. **Input resolution**: Accept command name, command path, or skill directory. Resolve the full component tree from any entry point.

2. **Full discovery**: Extend `discover_components.py` to inventory commands, agents, cross-skill references, and delegation patterns across all relevant directories.

3. **Subprocess scoping**: Extend `PortifyProcess` to add all discovered component directories to Claude's `--add-dir` list.

### Constraints

- Zero modifications to `pipeline/` or `sprint/` base modules (existing invariant)
- Synchronous-only execution (existing invariant)
- All changes within `cli_portify/` package
- Backward compatible with skill-directory-only input (existing behavior should still work)

### Approach

Two competing approaches are being brainstormed in parallel:
- **Approach A** (`brainstorm-approach-a.md`): Command-centric resolution — walk the command->skill->agent chain at runtime
- **Approach B** (`brainstorm-approach-b.md`): Manifest-based resolution — generate a comprehensive manifest listing all components, then use that as input

These will be debated via `sc:adversarial` and the winning approach will be refined into a spec.

---

## 7. Files Affected

### Must Change

| File | Change Type | Description |
|------|-------------|-------------|
| `cli_portify/models.py` | Modify | Extend `PortifyConfig` with command/agent resolution |
| `cli_portify/cli.py` | Modify | Accept command name/path input in addition to skill dir |
| `cli_portify/steps/validate_config.py` | Modify | Validate command + skill + agents, not just skill |
| `cli_portify/steps/discover_components.py` | Modify | Inventory full component tree |
| `cli_portify/process.py` | Modify | Add all discovered directories to `--add-dir` |
| `cli_portify/prompts.py` | Modify | Include command/agent context in prompts |
| `cli_portify/config.py` | Modify | Config loader for new input model |

### Must Add Tests

| File | Description |
|------|-------------|
| `tests/cli_portify/test_config.py` | Command resolution, multi-entry-point input |
| `tests/cli_portify/test_discover_components.py` | Full tree discovery, agent detection |
| `tests/cli_portify/test_process.py` | Multi-directory scoping |

### No Change Required

| File | Reason |
|------|--------|
| `pipeline/*` | Zero-modification invariant |
| `sprint/*` | Zero-modification invariant |
| `cli_portify/convergence.py` | Independent of input model |
| `cli_portify/gates.py` | Gate checks are content-based, not input-based |
| `cli_portify/contract.py` | Contract schema unchanged |
| `cli_portify/resume.py` | Resume semantics unchanged |

---

## 8. Cross-References

| Document | Location | Relevance |
|----------|----------|-----------|
| v2.24 roadmap | `.dev/releases/current/v2.24-cli-portify-cli-v4/roadmap.md` | Original implementation plan |
| v2.24 release spec | `.dev/releases/current/v2.24-cli-portify-cli-v4/portify-release-spec.md` | Source of narrow input definition |
| DEV-001 acceptance | `.dev/releases/current/v2.24-cli-portify-cli-v4/dev-001-accepted-deviation.md` | Architectural deviations |
| Analysis protocol | `.claude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | What discovery SHOULD do |
| Command-skill policy | `docs/architecture/command-skill-policy.md` | Tier 0/1/2 architecture definition |
| v2.24 release guide | `docs/generated/release-guide-v2.24-cli-portify-cli.md` | Released capability documentation |
| Brainstorm A | `.dev/releases/current/v2.24.1-cli-portify-cli-v5/brainstorm-approach-a.md` | Command-centric approach |
| Brainstorm B | `.dev/releases/current/v2.24.1-cli-portify-cli-v5/brainstorm-approach-b.md` | Manifest-based approach |

---

*Context document authored: 2026-03-13*
*Status: Brainstorm agents running, adversarial debate pending*
