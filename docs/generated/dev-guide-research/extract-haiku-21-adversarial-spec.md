# Extraction — v1.7 Adversarial Spec/Roadmap (Command/Skill/Agent Development)

## Sources (read completely)
- `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`
- `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`

---

## 1) What this feature is (as a framework command)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "`/sc:adversarial` is a generic, reusable command that implements a structured adversarial debate, comparison, and merge pipeline." (Exec Summary)

> "It is designed as a generic framework tool that any SuperClaude command can invoke." (Key Differentiator)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "This is a foundational infrastructure command — once built, it can be invoked by sc:roadmap, sc:design, sc:implement, sc:spec-panel, sc:improve, and sc:test." (Exec Summary)

---

## 2) Custom command interface design (usage, flags, examples)

### 2.1 Dual input modes

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "The command supports two primary input modes:" (FR-001)

**Mode A: compare existing files**
```bash
/sc:adversarial --compare file1.md,file2.md[,file3.md,...,file10.md]
```

**Mode B: generate variants from a source, then compare**
```bash
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,<agent-spec>,...]
```

### 2.2 Agent specification string format (for dynamic advocates)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "**Agent specification format** (hybrid model + optional persona + optional instruction):" (FR-001)

```text
<model>                              # e.g., opus
<model>:<persona>                    # e.g., opus:architect
<model>:<persona>:"<instruction>"    # e.g., opus:architect:"focus on scalability"
```

Also:

> "**Supported models**: Any model available in the environment (opus, sonnet, haiku, or configured aliases)." (FR-001)

> "**Agent count**: 2-10 agents. Minimum 2 required for adversarial comparison." (FR-001)

### 2.3 CLI flags (command contract)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### 6.2 Flags" (Command Interface)

```markdown
| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `--compare` | `-c` | Mode A | - | Comma-separated file paths (2-10) |
| `--source` | `-s` | Mode B | - | Source file for variant generation |
| `--generate` | `-g` | Mode B | - | Type of artifact to generate (roadmap, spec, etc.) |
| `--agents` | `-a` | Mode B | - | Agent specs: model[:persona[:"instruction"]] |
| `--depth` | `-d` | No | `standard` | Debate depth: quick, standard, deep |
| `--convergence` | | No | `0.80` | Alignment threshold (0.50-0.99) |
| `--interactive` | `-i` | No | `false` | Pause for user input at decision points |
| `--output` | `-o` | No | Auto | Output directory |
| `--focus` | `-f` | No | All | Debate focus areas (comma-separated) |
```

### 2.4 Command examples

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

```bash
# Compare two roadmap drafts
/sc:adversarial --compare draft-a.md,draft-b.md --depth standard

# Generate 3 roadmap variants from a spec using different models/personas
/sc:adversarial --source auth-spec.md --generate roadmap \
  --agents opus:architect,sonnet:security,opus:analyzer \
  --depth deep --convergence 0.85

# Compare 5 specs with interactive mode
/sc:adversarial --compare spec1.md,spec2.md,spec3.md,spec4.md,spec5.md \
  --interactive --depth deep

# Quick comparison with focused debate
/sc:adversarial --compare plan-a.md,plan-b.md \
  --depth quick --focus structure,completeness

# Full pipeline with custom output
/sc:adversarial --source migration-plan.md --generate roadmap \
  --agents opus:architect:"prioritize backward compatibility",sonnet:security:"zero-trust" \
  --depth deep --output .dev/releases/current/migration-v2/
```

---

## 3) Where to place new SuperClaude components (commands, skills, agents)

### 3.1 Canonical file locations for a new command/skill/agents

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "## 12. File Structure" (explicit file structure for implementation)

```text
src/superclaude/commands/
└── adversarial.md              Command definition (~80-100 lines)

src/superclaude/skills/sc-adversarial/
├── SKILL.md                    Behavioral instructions (~400-500 lines)
└── refs/
    ├── debate-protocol.md      5-step protocol details, convergence detection
    ├── scoring-protocol.md     Hybrid quant-qual scoring algorithm (from Appendix A)
    ├── agent-specs.md          Agent specification format, advocate behavior
    └── artifact-templates.md   Output format specifications

src/superclaude/agents/
├── debate-orchestrator.md      Process coordinator agent
└── merge-executor.md           Refactoring plan executor agent
```

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "### M0: Scaffolding" / file manifest (explicit file list)

```text
src/superclaude/commands/adversarial.md                    # ~80-100 lines
src/superclaude/skills/sc-adversarial/SKILL.md             # ~400-500 lines
src/superclaude/skills/sc-adversarial/__init__.py           # Package marker
src/superclaude/skills/sc-adversarial/refs/debate-protocol.md    # 5-step protocol detail
src/superclaude/skills/sc-adversarial/refs/scoring-protocol.md   # Appendix A algorithm
src/superclaude/skills/sc-adversarial/refs/agent-specs.md        # Agent spec format
src/superclaude/skills/sc-adversarial/refs/artifact-templates.md # Output templates
src/superclaude/agents/debate-orchestrator.md               # ~60-80 lines
src/superclaude/agents/merge-executor.md                    # ~40-60 lines
```

### 3.2 Framework registration / metadata updates

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "T5.4: Framework registration (COMMANDS.md, FLAGS.md, ORCHESTRATOR.md updates)"

and:

```text
COMMANDS.md      # Add sc:adversarial entry
FLAGS.md         # Add --adversarial flags if needed
ORCHESTRATOR.md  # Add routing rules for adversarial pattern
```

---

## 4) How to define new agents (responsibilities, tools, model preferences)

### 4.1 `debate-orchestrator` agent

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### 5.1 debate-orchestrator (NEW)"

**Purpose**

> "Coordinates the entire adversarial pipeline. Does NOT participate in debates - it manages the process."

**Responsibilities**

> "- Parse input mode and validate parameters
> - Dispatch variant generation (Mode B) in parallel
> - Coordinate the 5-step protocol
> - Track convergence scoring across debate rounds
> - Make base selection using scoring algorithm
> - Hand off to merge-executor for step 5
> - Compile final return contract"

**Model preference**

> "Highest-capability model available (opus preferred) - the orchestrator needs strong reasoning for scoring and coordination."

**Tools**

> "Task (for delegation), Read, Write, Glob, Grep, Bash (for file operations)"

**Explicit non-responsibilities**

> "Does NOT:
> - Generate variants (delegates to specified agents)
> - Participate in debates (delegates to advocate agents)
> - Execute merges (delegates to merge-executor)"

### 4.2 `merge-executor` agent

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### 5.2 merge-executor (NEW)"

**Purpose**

> "Executes refactoring plans to produce unified merged artifacts. Specialist in document integration."

**Responsibilities**

> "- Read the base variant and refactoring plan
> - Apply each planned change methodically
> - Maintain structural integrity during merge
> - Add provenance annotations
> - Validate the merged output for consistency
> - Produce merge-log.md documenting each applied change"

**Model preference**

> "High-capability model (opus or sonnet) - needs strong writing and structural reasoning."

**Tools**

> "Read, Write, Edit, Grep (for content verification)"

**Explicit non-responsibilities**

> "Does NOT:
> - Make strategic decisions about what to merge (follows the plan)
> - Override the refactoring plan without escalation
> - Participate in debates or scoring"

### 4.3 Dynamic advocate agents (instantiated from `--agents`)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### 5.3 Advocate Agents (Dynamic)"

> "These are NOT pre-defined agents. They are instantiated dynamically from the `--agents` specification. Each advocate:
> - Receives their variant + all other variants + diff-analysis.md
> - Argues for their variant's strengths in the specified focus areas
> - Critiques weaknesses in other variants with evidence
> - Responds to rebuttals in subsequent rounds"

> "The advocate's behavior is shaped by:
> - The model specified (opus, sonnet, haiku)
> - The persona specified (architect, security, analyzer, etc.)
> - The custom instruction (if provided)"

---

## 5) How to define a new skill (SKILL.md + refs) to drive behavior

The spec/roadmap define a skill package for this command.

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "src/superclaude/skills/sc-adversarial/
> ├── SKILL.md                    Behavioral instructions (~400-500 lines)
> └── refs/ ..." (File Structure)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "T0.2 | `src/superclaude/skills/sc-adversarial/SKILL.md` | Behavioral instructions (~400-500 lines): 5-step protocol, convergence, error handling"

> "T0.4 | `src/superclaude/skills/sc-adversarial/refs/` | Reference docs: `debate-protocol.md`, `scoring-protocol.md`, `agent-specs.md`, `artifact-templates.md`"

Also (skill is a Python package directory):

> "src/superclaude/skills/sc-adversarial/__init__.py           # Package marker" (File Manifest)

---

## 6) Custom command behavior: structured output artifacts + directory conventions

### 6.1 Required output directory structure

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### FR-005: Artifact Output Structure"

```text
<output-dir>/
├── <merged-output>.md          # Final unified artifact
└── adversarial/
    ├── variant-1-<agent>.md    # Agent 1's generated variant (Mode B) or input file copy (Mode A)
    ├── variant-2-<agent>.md    # Agent 2's generated variant
    ├── ...                     # Up to 10 variants
    ├── diff-analysis.md        # Step 1 output
    ├── debate-transcript.md    # Step 2 output
    ├── base-selection.md       # Step 3 output
    ├── refactor-plan.md        # Step 4 output
    └── merge-log.md            # Step 5 execution log
```

> "Naming conventions for variants:
> - Mode A (compare): `variant-1-original.md`, `variant-2-original.md` (copies of input files)
> - Mode B (generate): `variant-1-<model>-<persona>.md`, e.g., `variant-1-opus-architect.md`"

### 6.2 Artifact templates to codify in skill refs

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

The spec provides concrete markdown templates for the key artifacts, intended to be used by the skill (refs/artifact-templates.md) and/or by the orchestrator logic.

**`diff-analysis.md` template**
```markdown
# Diff Analysis: <artifact-type> Comparison

## Metadata
- Generated: <timestamp>
- Variants compared: <count>
- Total differences found: <count>
- Categories: structural (<N>), content (<N>), contradictions (<N>), unique (<N>)

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Section ordering | Auth before API | API before Auth | Low |
| S-002 | Hierarchy depth | 3-level milestones | 2-level milestones | Medium |

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Auth strategy | JWT with refresh tokens | OAuth2 with PKCE | High |

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Database choice | PostgreSQL required | MongoDB preferred | High |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | Rollback strategy for each milestone | High |
| U-002 | B | Performance budget per component | Medium |
```

**`debate-transcript.md` template**
```markdown
# Adversarial Debate Transcript

## Metadata
- Depth: <quick|standard|deep>
- Rounds completed: <N>
- Convergence achieved: <percentage>%
- Focus areas: <list>

## Round 1: Advocate Statements

### Variant A Advocate (opus:architect)
**Position**: [Summary of argument for Variant A]
**Key strengths claimed**:
1. [Strength with evidence]
2. [Strength with evidence]
**Weaknesses identified in Variant B**:
1. [Critique with evidence]

### Variant B Advocate (sonnet:security)
**Position**: [Summary of argument for Variant B]
**Key strengths claimed**:
1. [Strength with evidence]
**Weaknesses identified in Variant A**:
1. [Critique with evidence]

## Round 2: Rebuttals (if --depth standard or deep)

### Variant A Rebuttal
[Response to Variant B's critiques with counter-evidence]

### Variant B Rebuttal
[Response to Variant A's critiques with counter-evidence]

## Round 3: Final Arguments (if --depth deep and convergence < threshold)

[Final positions after considering rebuttals]

## Scoring Matrix

| Diff Point | Winner | Confidence | Evidence Summary |
|------------|--------|------------|-----------------|
| S-001 | A | 85% | Better dependency flow |
| C-001 | B | 72% | Stronger security model |
| X-001 | A | 60% | More practical for team |

## Convergence Assessment
- Points resolved: <N> of <total>
- Alignment: <percentage>%
- Threshold: <configured>%
- Status: <CONVERGED|NOT_CONVERGED>
```

**`base-selection.md` template (includes scoring tables + CEV citations)**
The spec contains a long base-selection.md template including quantitative scoring, qualitative rubric, and combined scoring tables (see Spec §8.3).

**`refactor-plan.md` template**
```markdown
# Refactoring Plan: Merge into Base (Variant A)

## Overview
- Base: Variant A (opus:architect)
- Incorporating strengths from: Variant B (sonnet:security)
- Planned changes: <N>
- Risk level: <Low|Medium|High>

## Planned Changes

### Change 1: Incorporate Zero-Trust Auth Model (from Variant B)
- **Source**: Variant B, Section 3.2
- **Target**: Base, Section 3.2 (replace JWT approach)
- **Rationale**: Debate Round 2 established B's auth model as superior (72% confidence)
- **Integration point**: Replace Section 3.2 entirely, update references in Sections 4.1 and 5.3
- **Risk**: Medium - requires adjusting 3 dependent sections

### Change 2: Add Performance Budgets (from Variant B)
- **Source**: Variant B, Section 6 (unique contribution U-002)
- **Target**: Base, new Section 6.5
- **Rationale**: Unique contribution with medium value, no conflict with base
- **Integration point**: Insert as new subsection after existing Section 6.4
- **Risk**: Low - additive change, no conflicts

## Changes NOT Being Made (with rationale)
- [Difference that was debated but base approach was determined superior]

## Review Status
- [ ] Auto-approved (default) / [ ] User-approved (--interactive)
```

---

## 7) Custom command orchestration patterns (delegation, integration points)

### 7.1 Delegation pattern (how a command can call other commands/agents)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### 7.3 Delegation Pattern"

```markdown
| Step | Delegates To | Purpose |
|------|-------------|---------|
| Diff analysis | `/sc:analyze` or analytical agent | Structured comparison |
| Advocate generation | Domain agents (per --agents spec) | Generate debate arguments |
| Refactoring plan | Analytical agent | Draft the merge plan |
| Merge execution | merge-executor agent | Execute the plan |
```

### 7.2 Integration with other framework commands

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### 7.1 sc:roadmap v2 Integration"

**Multi-spec mode**
```text
sc:roadmap → sc:adversarial --compare spec1.md,spec2.md → unified-spec.md → roadmap generation
```

**Multi-roadmap mode**
```text
sc:roadmap → sc:adversarial --source spec.md --generate roadmap --agents opus,sonnet → unified-roadmap.md
```

**Combined mode**
```text
sc:roadmap → sc:adversarial --compare specs → unified-spec.md
           → sc:adversarial --source unified-spec.md --generate roadmap --agents → unified-roadmap.md
```

Also:

> "### 7.2 Future Integration Candidates" (Spec)

```markdown
| Command | Use Case |
|---------|----------|
| `/sc:design` | Compare multiple architectural designs |
| `/sc:implement` | Compare implementation approaches before committing |
| `/sc:spec-panel` | Augment expert panel with adversarial cross-review |
| `/sc:test` | Compare test strategies or coverage approaches |
| `/sc:improve` | Generate competing improvement plans, merge best of each |
```

---

## 8) MCP/tooling integration guidance for building commands/skills/agents

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "## 10. MCP Integration"

```markdown
| Server | Usage | Phase |
|--------|-------|-------|
| Sequential | Debate scoring, convergence analysis, refactoring plan logic | Steps 2-4 |
| Serena | Memory persistence of adversarial outcomes for cross-session learning | Step 5 |
| Context7 | Domain pattern validation during merge | Step 5 |
```

> "**Circuit breaker**: If Sequential is unavailable, fall back to native Claude reasoning with depth reduction (deep → standard, standard → quick)."

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "T5.3 MCP integration: Sequential for debate scoring/convergence analysis (Steps 2-4), Serena for memory persistence of outcomes (Step 5), Context7 for domain pattern validation (Step 5). Circuit breaker fallbacks."

---

## 9) Development workflow hooks (syncing to `.claude/`, verifying)

The roadmap provides acceptance criteria that indicate how new commands/skills/agents should be integrated into the repo’s development flow.

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "**Acceptance**: All files created, `make sync-dev` copies to `.claude/`, `make verify-sync` passes." (M0)

Also (implementation strategy):

> "Each milestone produces testable artifacts. Validate each step's output quality before proceeding:" (Implementation Strategy)

```text
1. M0: Scaffold → `make sync-dev` → verify all files exist
2. M1: Test with 2 real markdown files → inspect diff-analysis.md quality
3. M2: Test with diff-analysis.md from M1 → inspect debate-transcript.md for genuine disagreement (not sycophantic)
4. M3: Test with debate transcript → verify scoring determinism (run twice, same quant scores)
5. M4: Test merge → verify provenance annotations, structural integrity
6. M5: Full pipeline E2E → both modes → error handling edge cases
```

---

## 10) What an agent/command must return (return contract)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### FR-007: Return Contract"

> "When invoked by another command (e.g., sc:roadmap), sc:adversarial returns:
> - Path to the merged output file
> - Final convergence score
> - Path to the adversarial/ artifacts directory
> - Success/partial/failed status
> - List of unresolved conflicts (if any)"

---

## 11) Error handling guidance (useful when implementing new commands)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### FR-006: Error Handling"

```markdown
| Scenario | Behavior |
|----------|----------|
| Agent fails to generate variant | Retry once, then proceed with N-1 variants (minimum 2 required) |
| Variants too similar (<10% diff) | Skip debate, select either as base, log "variants substantially identical" |
| Variants too divergent (no convergence after max rounds) | Force-select by score, document non-convergence, flag for user review |
| Merge execution produces invalid output | Preserve all artifacts, flag failure, provide refactor-plan.md for manual execution |
| Single variant remains after failures | Abort adversarial process, return the surviving variant as-is with warning |
```

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

> "T5.1 Error handling matrix (FR-006): agent failure retry + N-1 fallback, <10% diff skip, non-convergence force-select, invalid merge preservation, single-variant abort."

---

## 12) Concrete implementation scaffolding guidance (deliverables, file sizes, constraints)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/roadmap.md`:

The roadmap explicitly defines what content should be in each file (useful as a pattern for other new commands/skills/agents).

> "T0.1 | `src/superclaude/commands/adversarial.md` | Command definition (~80-100 lines): usage, flags, examples, boundaries"

> "T0.2 | `src/superclaude/skills/sc-adversarial/SKILL.md` | Behavioral instructions (~400-500 lines): 5-step protocol, convergence, error handling"

> "T0.3a | `src/superclaude/agents/debate-orchestrator.md` | Process coordinator: delegates but doesn't participate"

> "T0.3b | `src/superclaude/agents/merge-executor.md` | Plan executor: follows refactoring plan, provenance annotations"

> "T0.4 | `src/superclaude/skills/sc-adversarial/refs/` | Reference docs: `debate-protocol.md`, `scoring-protocol.md`, `agent-specs.md`, `artifact-templates.md`"

---

## 13) Notes on command boundaries (useful for writing command docs)

From `/config/workspace/SuperClaude_Framework/.dev/releases/archive/complete/v1.7-adversarial/SC-ADVERSARIAL-SPEC.md`:

> "### Will Do
> - Compare 2-10 artifacts through structured adversarial debate
> - Generate variant artifacts using different model/persona configurations
> - Produce transparent, documented merge decisions
> - Execute refactoring plans to produce unified outputs
> - Support configurable depth, convergence thresholds, and focus areas
> - Work as a generic tool invocable by any SuperClaude command"

> "### Will Not Do
> - Validate domain-specific correctness of merged output (calling command's responsibility)
> - Execute the merged output (planning tool, not execution tool)
> - Manage git operations or version control
> - Make decisions without documented rationale
> - Operate with fewer than 2 variants (minimum for adversarial comparison)
> - Override user decisions in interactive mode"
