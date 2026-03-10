# SuperClaude Skills Development Patterns - Multi-Complexity Extraction

## Source Files

| File | Path |
|------|------|
| Confidence Check SKILL.md | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/confidence-check/SKILL.md` |
| Task Unified SKILL.md | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-task-unified/SKILL.md` |
| Cleanup Audit SKILL.md | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-cleanup-audit/SKILL.md` |
| Pass 1 Rules | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-cleanup-audit/rules/pass1-surface-scan.md` |
| Batch Report Template | `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-cleanup-audit/templates/batch-report.md` |

---

## 1. Three Complexity Levels Identified

The examined skills represent three distinct complexity tiers for skill development:

| Level | Skill | Directory Contents | Subdirectories |
|-------|-------|--------------------|----------------|
| **Simple** | `confidence-check` | `SKILL.md`, `confidence.ts`, `__init__.py` | None |
| **Medium** | `sc-task-unified` | `SKILL.md`, `__init__.py` | None |
| **Complex** | `sc-cleanup-audit` | `SKILL.md`, `__init__.py` | `rules/` (5 files), `templates/` (4 files), `scripts/` (1 file) |

An additional complex skill, `sc-adversarial`, follows a similar pattern but uses `refs/` instead of `rules/` and `templates/`:

| Skill | Subdirectories |
|-------|----------------|
| `sc-adversarial` | `refs/` (4 files: `agent-specs.md`, `artifact-templates.md`, `debate-protocol.md`, `scoring-protocol.md`) |

---

## 2. SKILL.md Frontmatter Structure

### 2.1 Simple Skill Frontmatter (confidence-check)

Minimal frontmatter with only `name` and `description`:

```yaml
---
name: Confidence Check
description: Pre-implementation confidence assessment (>=90% required). Use before starting any implementation to verify readiness with duplicate check, architecture compliance, official docs verification, OSS references, and root cause identification.
---
```

**Notable**: No `allowed-tools`, no `category`, no `complexity`, no `mcp-servers`, no `personas`, no `argument-hint`.

### 2.2 Medium Skill Frontmatter (sc-task-unified)

Adds `allowed-tools` but still omits several fields present in complex skills:

```yaml
---
name: sc-task-unified
description: Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation. Merges orchestration capabilities with MCP compliance into a single coherent interface.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**Notable**: Has `allowed-tools` but no `category`, `complexity`, `mcp-servers`, `personas`, or `argument-hint`.

### 2.3 Complex Skill Frontmatter (sc-cleanup-audit)

Full frontmatter with all available fields:

```yaml
---
name: cleanup-audit
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"
---
```

**Notable**: All fields present. `allowed-tools` includes restricted Bash patterns (`Bash(git *)`, `Bash(wc *)` etc.). Lists `mcp-servers` and `personas` as arrays.

### 2.4 Frontmatter Field Summary

| Field | Simple | Medium | Complex | Purpose |
|-------|--------|--------|---------|---------|
| `name` | Yes | Yes | Yes | Skill identifier |
| `description` | Yes | Yes | Yes (quoted) | Human-readable purpose |
| `category` | No | No | Yes | Organizational grouping |
| `complexity` | No | No | Yes | Complexity rating |
| `mcp-servers` | No | No | Yes (array) | Required MCP server dependencies |
| `personas` | No | No | Yes (array) | Auto-activated persona list |
| `allowed-tools` | No | Yes | Yes | Tool whitelist for execution |
| `argument-hint` | No | No | Yes | CLI usage hint string |

---

## 3. SKILL.md Body Structure Comparison

### 3.1 Simple Skill Body (confidence-check)

Sections: Purpose, When to Use, Confidence Assessment Criteria (5 numbered checks), Confidence Score Calculation, Output Format, Implementation Details, ROI.

Key structural pattern -- a **checklist-style assessment** with weighted criteria:

```
### 1. No Duplicate Implementations? (25%)
### 2. Architecture Compliance? (25%)
### 3. Official Documentation Verified? (20%)
### 4. Working OSS Implementations Referenced? (15%)
### 5. Root Cause Identified? (15%)
```

Each check follows: **Check description** -> tool usage hint -> pass/fail criteria. The skill defines a simple scoring formula:

```
Total = Check1 (25%) + Check2 (25%) + Check3 (20%) + Check4 (15%) + Check5 (15%)

If Total >= 0.90:  Proceed with implementation
If Total >= 0.70:  Present alternatives, ask questions
If Total < 0.70:   STOP - Request more context
```

**No Behavioral Flow section** -- the skill is a single-phase assessment, not a multi-phase workflow.

**No MCP Integration section** -- MCP references are embedded inline within individual checks (e.g., "Use Context7 MCP for official docs", "Use Tavily MCP or WebSearch").

**No Tool Coordination section** -- tool usage is mentioned per-check rather than as a coordinated system.

**No Boundaries section** -- the simple skill does not define explicit will/will-not boundaries.

### 3.2 Medium Skill Body (sc-task-unified)

Sections: Purpose, Triggers, Usage, Behavioral Flow (5 phases), MCP Integration, Tool Coordination, Examples, Boundaries, Success Criteria, Configuration References.

The medium skill introduces several structural elements absent from the simple skill:

**Mandatory First Output** -- a machine-readable classification header:

```
> **MANDATORY FIRST OUTPUT**: You MUST output the classification header block below as your VERY FIRST output, before ANY text, questions, or analysis. This is NON-NEGOTIABLE for telemetry.
```

```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
KEYWORDS: [comma-separated keywords or "none"]
OVERRIDE: [true|false]
RATIONALE: [one-line reason]
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

**Multi-Phase Behavioral Flow** with numbered phases:
- Phase 0: Mandatory Classification Header
- Phase 1: Classification Phase (tier assignment)
- Phase 2: Confidence Display (human-readable)
- Phase 3: Execution Phase (tier-specific steps)
- Phase 4: Verification Phase (tier-routed)
- Phase 5: Feedback Collection

**Tier-differentiated execution** -- different step counts per tier:

| Tier | Steps in Execution Phase |
|------|-------------------------|
| STRICT | 11 steps |
| STANDARD | 5 steps |
| LIGHT | 4 steps |
| EXEMPT | 2 steps |

**MCP Integration section** as a standalone section:

```
**Required Servers by Tier**:
- STRICT: Sequential, Serena (fallback not allowed)
- STANDARD: Sequential, Context7 (fallback allowed)
- LIGHT: None required (fallback allowed)
- EXEMPT: None required
```

**Tool Coordination section** organized by phase:

```
**Planning Phase**:
1. TodoWrite: Create task breakdown
2. codebase-retrieval: Load context
3. list_memories / read_memory: Check project state

**Execution Phase**:
1. Edit/MultiEdit/Write: Make changes
2. Grep/Glob: Find references
3. find_referencing_symbols: Trace dependencies

**Verification Phase**:
1. Task (quality-engineer): Spawn verification agent (STRICT only)
2. Bash: Run tests directly (STANDARD)
3. think_about_task_adherence: Reflect on completeness

**Completion Phase**:
1. write_memory: Save session state
2. think_about_whether_you_are_done: Final check
```

**Boundaries section** with explicit Will/Will Not:

```
**Will:**
- Classify tasks into appropriate compliance tiers
- Enforce tier-appropriate verification requirements
...

**Will Not:**
- Skip safety-critical verification for STRICT tasks
- Apply STRICT overhead to genuinely trivial changes
...
```

**Success Criteria section** with measurable targets:

```
| Metric | Target | Measurement |
|--------|--------|-------------|
| Tier classification accuracy | >=80% | User feedback on appropriateness |
| User confusion rate | <10% | "Which command?" questions eliminated |
| Skip rate (--skip-compliance) | <12% | Override tracking |
```

**Configuration References** pointing to external YAML configs:

```
- Keywords: `config/tier-keywords.yaml`
- Verification routing: `config/verification-routing.yaml`
- Acceptance criteria: `config/tier-acceptance-criteria.yaml`
```

### 3.3 Complex Skill Body (sc-cleanup-audit)

Sections: Triggers, Usage (with Arguments subsection), Repository Context, Target Scope, Behavioral Flow, MCP Integration, Tool Coordination, Key Patterns, Examples, Boundaries, Critical Boundaries.

The complex skill adds several unique structural elements:

**Shell Preprocessing in the SKILL.md** -- inline shell commands executed during skill loading:

```
## Repository Context
- Total files: !`git ls-files | wc -l`
- File breakdown: !`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15`
- Repo size: !`du -sh . --exclude=.git --exclude=node_modules 2>/dev/null`
- Current branch: !`git branch --show-current`
- Last commit: !`git log --oneline -1`
```

The `!` backtick syntax appears to be a SuperClaude convention for shell preprocessing within skill files.

**Behavioral Flow as a numbered workflow** with 5 orchestration phases:

```
1. **Discover**: Enumerate repository files via shell preprocessing and `repo-inventory.sh`.
2. **Configure**: Parse `$ARGUMENTS` for pass selection and focus area. Load pass-specific rules from `rules/` supporting files.
3. **Orchestrate**: Spawn parallel subagents via Task tool in waves of 7-8 concurrent agents.
4. **Validate**: Spawn `audit-validator` for 10% spot-check sampling.
5. **Report**: Spawn `audit-consolidator` to merge batch reports into pass summaries.
```

**Subagent orchestration** -- defines 5 specialized agent types:

```
audit-scanner (Haiku, Pass 1)
audit-analyzer (Sonnet, Pass 2)
audit-comparator (Sonnet, Pass 3)
audit-consolidator (Sonnet, reports)
audit-validator (Sonnet, spot-check)
```

**Key Patterns section** documenting reusable architectural patterns:

```
- **Haiku-First Escalation**: All files -> Haiku surface scan -> flagged subset -> Sonnet deep analysis
- **Evidence-Gated Classification**: File content -> grep references + import check -> evidence-backed recommendation
- **Incremental Checkpoint**: Batch complete -> write to disk -> update progress.json -> resume-safe state
- **Fan-Out/Fan-In Orchestration**: File inventory -> parallel agent waves (7-8) -> disk-based results -> consolidated report
- **Conservative Escalation**: Uncertain classification -> FLAG/REVIEW (never DELETE) -> human review gate
```

**Dual Boundaries sections** -- both a standard `Boundaries` and a `CRITICAL BOUNDARIES` section:

```
## CRITICAL BOUNDARIES

**READ-ONLY AUDIT -- NO REPOSITORY MODIFICATIONS**

**Explicitly Will NOT**:
- Edit, delete, move, or rename any existing repository file
- Execute cleanup recommendations -- human review gate is mandatory
- Modify CI/CD pipelines, configs, or any operational infrastructure
- Make speculative deletions based on filename patterns without evidence
```

**External references** to rules/ and templates/ subdirectories within the Behavioral Flow.

---

## 4. Rules Subdirectory Pattern

Only the complex skill (`sc-cleanup-audit`) has a `rules/` subdirectory. The `sc-adversarial` skill uses `refs/` for a similar purpose.

### 4.1 Rules Directory Contents (sc-cleanup-audit)

```
rules/
  dynamic-use-checklist.md
  pass1-surface-scan.md
  pass2-structural-audit.md
  pass3-cross-cutting.md
  verification-protocol.md
```

### 4.2 Rules File Structure (pass1-surface-scan.md)

A rules file defines the behavioral contract for one phase of the skill. Structure:

```markdown
# Pass 1: Surface Scan Rules

## Goal
## Guiding Question
## Classification Taxonomy (table)
## Verification Protocol (numbered steps)
## Output Format (markdown template)
## Batch Size Guidance (table)
## Binary Asset Handling
## "Zero References" Evidence Standard
## Dynamic Loading Check
## Incremental Save Protocol
```

Key structural elements within a rules file:

**Goal** -- single sentence defining the pass objective:
> "Quickly identify obvious waste -- test artifacts, runtime files committed by accident, empty placeholders, files nothing references."

**Guiding Question** -- a simple heuristic for the agent:
> **"Is this file junk?"**

**Classification Taxonomy** as a table with Category, Meaning, Action, Evidence Required columns.

**Verification Protocol** as numbered steps (4-step for pass 1):

```
1. **Read**: Read first 20-30 lines to understand purpose
2. **Grep**: Search for filename across repo
3. **Check Imports**: Verify file is not imported/sourced/required
4. **Categorize**: Assign DELETE/REVIEW/KEEP with brief justification
```

**Evidence Standards** -- explicit requirements for what constitutes sufficient evidence:

```
Every DELETE classification must embed:
1. **Grep pattern used**: The exact command
2. **Match count**: Number of matches found (must be 0 for DELETE)
3. **Zero-result confirmation**: Explicit statement "0 matches found across N files searched"

**"No imports found" without a reproducible grep command is insufficient evidence for DELETE.**
```

**Batch Size Guidance** as a table mapping file types to recommended batch sizes.

**Incremental Save Protocol** -- operational constraints for the agent:

```
1. Create output file with header template before auditing any files
2. Work in batches of 5-10 files
3. After each mini-batch, immediately save/update the output file
4. Never accumulate more than 10 unwritten results
```

### 4.3 How Rules Files Are Referenced

The SKILL.md Behavioral Flow references rules files during the Configure phase:

> "Load pass-specific rules from `rules/` supporting files."

Rules files are also cross-referenced within themselves:

> "Before classifying any file as DELETE, verify it is not dynamically loaded. See `rules/dynamic-use-checklist.md` for the 5 patterns to check."

---

## 5. Templates Subdirectory Pattern

Only the complex skill has a `templates/` subdirectory.

### 5.1 Templates Directory Contents (sc-cleanup-audit)

```
templates/
  batch-report.md
  final-report.md
  finding-profile.md
  pass-summary.md
```

### 5.2 Template File Structure (batch-report.md)

Templates define the exact output format that subagents must produce. The batch report template is a markdown document with placeholder variables in `{curly braces}`:

```markdown
# {Scope Description} Audit (Pass {N})

**Status**: In Progress / Complete
**Files audited**: X / Y total
**Date**: YYYY-MM-DD
**Agent**: {agent-type}
**Batch**: {batch-number}
```

The template defines mandatory sections with structured fields per finding:

```markdown
## Files to DELETE
### `filepath`
- **What it does**: {1-2 sentence description}
- **Nature**: {script / test / doc / config / source code / data / asset / migration / one-time artifact}
- **References**: {grep results -- pattern used, match count, zero-result confirmation}
- **Dynamic loading check**: {checked all 5 patterns -- none apply}
- **CI/CD usage**: {not referenced by any automation}
- **Evidence**: Why this should be deleted -- {grep pattern + count + zero-result}
- **Recommendation**: DELETE -- {reason}
```

Classification categories in the template: DELETE, CONSOLIDATE (Pass 3 only), MOVE, FLAG, KEEP, Broken References Found, Remaining / Not Audited.

A mandatory summary section:

```markdown
## Summary
- **Total files audited**: X / Y assigned
- **DELETE**: N | **CONSOLIDATE**: N | **MOVE**: N | **FLAG**: N | **KEEP**: N
- **Broken references found**: N
- **Coverage**: X/Y = {percentage}%
```

A transparency requirement:

```markdown
## Remaining / Not Audited
<!-- MANDATORY if scope was not completed -- transparency beats pretending completeness -->
- `filepath` -- not reached (reason: {batch limit / time constraint / error})
```

---

## 6. Scripts Subdirectory Pattern

Only the complex skill has a `scripts/` subdirectory.

```
scripts/
  repo-inventory.sh
```

The script is referenced in the Behavioral Flow:

> "Enumerate repository files via shell preprocessing and `repo-inventory.sh`."

Scripts provide executable automation that the skill orchestrator runs during execution phases.

---

## 7. Refs Subdirectory Pattern (sc-adversarial)

The `sc-adversarial` skill uses `refs/` instead of `rules/` and `templates/`:

```
refs/
  agent-specs.md
  artifact-templates.md
  debate-protocol.md
  scoring-protocol.md
```

This suggests `refs/` serves as a combined reference directory for skills that blend protocol definitions, agent specifications, and output templates into a single supporting directory rather than separating them.

---

## 8. Integration with Commands and Agents

### 8.1 Command Integration

Skills are invoked as slash commands. The mapping from COMMANDS.md:

```
/sc:task -> sc-task-unified skill
/sc:cleanup-audit -> sc-cleanup-audit skill (cleanup-audit)
/sc:adversarial -> sc-adversarial skill
```

The `confidence-check` skill is different -- it is referenced as a pre-implementation gate rather than a standalone command. From CLAUDE.md:

> "Confidence-First Implementation: Check confidence BEFORE starting: >=90% proceed, 70-89% present alternatives, <70% ask questions."

### 8.2 Agent Integration

Complex skills define agent types that are spawned via the `Task` tool:

**sc-cleanup-audit agents** (5 specialized types):
- `audit-scanner` (Haiku) -- Pass 1 surface scanning
- `audit-analyzer` (Sonnet) -- Pass 2 structural analysis
- `audit-comparator` (Sonnet) -- Pass 3 cross-cutting comparison
- `audit-consolidator` (Sonnet) -- Report merging
- `audit-validator` (Sonnet) -- Quality spot-checking

**sc-task-unified agents** (1 type):
- `quality-engineer` -- Verification agent spawned for STRICT tier only

**sc-adversarial agents** (from COMMANDS.md):
- `debate-orchestrator` -- coordinator
- `merge-executor` -- specialist
- `advocate agents` -- dynamic

Agent definitions live in `src/superclaude/agents/` as `.md` files and are installed to `.claude/agents/` via `superclaude install`.

### 8.3 Persona Integration

Complex skills activate multiple personas. From the cleanup-audit frontmatter:

```yaml
personas: [analyzer, architect, devops, qa, refactorer]
```

The SKILL.md body explains persona coordination:

> "Analyzer leads all passes; Architect activated for infrastructure batches; DevOps for Docker/CI/deploy; QA for test file batches; Refactorer for duplication findings"

Simple and medium skills do not declare personas in frontmatter but may reference them implicitly through the command system (COMMANDS.md defines persona auto-activation per command).

---

## 9. Tool Coordination Patterns

### 9.1 Simple Skill Tool Coordination

No formal tool coordination. Tools mentioned inline per assessment check:

```
# Within checks:
"Use Grep to search for similar functions"
"Use Glob to find related modules"
"Use Context7 MCP for official docs"
"Use WebFetch for documentation URLs"
"Use Tavily MCP or WebSearch"
```

### 9.2 Medium Skill Tool Coordination

Formal `Tool Coordination` section organized by execution phase:

```
Planning Phase -> TodoWrite, codebase-retrieval, list_memories/read_memory
Execution Phase -> Edit/MultiEdit/Write, Grep/Glob, find_referencing_symbols
Verification Phase -> Task (quality-engineer), Bash, think_about_task_adherence
Completion Phase -> write_memory, think_about_whether_you_are_done
```

### 9.3 Complex Skill Tool Coordination

Formal `Tool Coordination` section organized by tool capability, with access restrictions:

```
- **Read/Grep/Glob**: Core audit tools available to all subagents
- **Bash(git/wc/find/du)**: Controlled shell access for orchestrator only
- **Write**: Report generation restricted to `.claude-audit/` output directory
- **TodoWrite**: Progress tracking with per-batch tasks
- **Task**: Subagent delegation with 5 specialized agent types
```

Key difference: complex skills enforce **tool access restrictions** per actor (orchestrator vs subagent) and restrict **output paths** (Write only to `.claude-audit/`).

The `allowed-tools` frontmatter in the complex skill uses **parameterized Bash restrictions**:

```yaml
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
```

This pattern `Bash(command *)` limits shell access to specific command prefixes rather than granting unrestricted Bash.

---

## 10. Structural Comparison Summary

### 10.1 Directory Structure by Complexity

```
# Simple Skill
skills/confidence-check/
  __init__.py
  SKILL.md
  confidence.ts            # Optional reference implementation

# Medium Skill
skills/sc-task-unified/
  __init__.py
  SKILL.md

# Complex Skill (audit pattern)
skills/sc-cleanup-audit/
  __init__.py
  SKILL.md
  rules/                   # Phase-specific behavioral rules
    pass1-surface-scan.md
    pass2-structural-audit.md
    pass3-cross-cutting.md
    dynamic-use-checklist.md
    verification-protocol.md
  templates/               # Output format templates
    batch-report.md
    final-report.md
    finding-profile.md
    pass-summary.md
  scripts/                 # Executable automation
    repo-inventory.sh

# Complex Skill (adversarial pattern)
skills/sc-adversarial/
  __init__.py
  SKILL.md
  refs/                    # Combined protocols, specs, and templates
    agent-specs.md
    artifact-templates.md
    debate-protocol.md
    scoring-protocol.md
```

### 10.2 SKILL.md Section Comparison

| Section | Simple | Medium | Complex |
|---------|--------|--------|---------|
| Frontmatter (name, description) | Yes | Yes | Yes |
| Frontmatter (allowed-tools) | No | Yes | Yes |
| Frontmatter (category, complexity) | No | No | Yes |
| Frontmatter (mcp-servers, personas) | No | No | Yes |
| Frontmatter (argument-hint) | No | No | Yes |
| Purpose / When to Use | Yes | Yes | Implicit in Triggers |
| Triggers | No | Yes | Yes |
| Usage with CLI syntax | No | Yes | Yes |
| Shell Preprocessing (!backtick) | No | No | Yes |
| Behavioral Flow (multi-phase) | No | Yes (5 phases) | Yes (5 phases) |
| Mandatory First Output | No | Yes | No |
| MCP Integration section | No | Yes | Yes |
| Tool Coordination section | No | Yes | Yes |
| Key Patterns section | No | No | Yes |
| Examples section | No | Yes | Yes |
| Boundaries (Will/Will Not) | No | Yes | Yes |
| Critical Boundaries | No | No | Yes |
| Success Criteria | No | Yes | No |
| Configuration References | No | Yes | No |

### 10.3 Key Design Principles Extracted

1. **Every skill has a `SKILL.md`** -- this is the single required file. The frontmatter `name` and `description` fields are mandatory.

2. **`__init__.py` is present in every skill directory** -- this makes skills importable as Python packages.

3. **Complexity determines structure** -- simple skills are self-contained in SKILL.md; medium skills add tool/MCP/phase coordination within SKILL.md; complex skills decompose into `rules/`, `templates/`, and optionally `scripts/` or `refs/` subdirectories.

4. **Rules files define agent behavioral contracts** -- they specify goals, guiding questions, classification taxonomies, verification protocols, evidence standards, and operational constraints.

5. **Template files define output contracts** -- they specify the exact markdown structure subagents must produce, including mandatory sections, field names, and transparency requirements.

6. **Tool access is tiered** -- simple skills mention tools inline; medium skills organize tools by phase; complex skills restrict tool access per actor and parameterize Bash access.

7. **MCP integration scales with complexity** -- simple skills reference MCP inline; medium skills declare MCP requirements by tier; complex skills declare MCP in frontmatter and detail usage in a dedicated section with constraints (e.g., "MCP tools are unavailable to background subagents").

8. **Boundaries get stricter with complexity** -- simple skills have no boundary section; medium skills have Will/Will Not; complex skills add Critical Boundaries with explicit prohibitions.

9. **Shell preprocessing (`!` backtick syntax)** appears only in complex skills that need dynamic repository context at load time.

10. **Naming convention**: Skills prefixed with `sc-` are SuperClaude framework commands exposed as slash commands. Non-prefixed skills (e.g., `confidence-check`) are utility skills used internally by other skills or commands.
