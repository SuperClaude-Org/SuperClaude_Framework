# Extraction: Custom Commands / Skills / Agents Guidance (Roadmap V2 Spec)

**Source file**: `/config/workspace/SuperClaude_Framework/.dev/releases/current/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md`

This document extracts **all information in the source spec that pertains to developing custom commands, skills, or agents** for the SuperClaude framework.

---

## 1) Command + Skill Packaging Model (Command file vs SKILL.md)

### 1.1 Lean command file + full skill behavior split

Exact quote (command/skill split principle):

> "| `commands/roadmap.md` | `src/superclaude/commands/` | Claude Code command definition: triggers, flags, usage examples, behavioral summary, boundaries | ~80 lines |"
>
> "| `SKILL.md` | `src/superclaude/skills/sc-roadmap/` | Full behavioral instructions: wave flow, decision logic, ref loading triggers, adversarial mode orchestration | ~400 lines |"

Exact quote (separation principle + install targets):

> "**Separation principle**: The command file tells Claude Code WHEN to activate and WHAT the command does (surface-level). The SKILL.md tells Claude HOW to execute (behavioral detail). The command file is installed to `~/.claude/commands/sc/` and is loaded when the user types `/sc:roadmap`. The SKILL.md is installed to `~/.claude/skills/` and is loaded by the command file's activation."

### 1.2 Command interface shape (usage + flags)

The spec defines how a custom command should present:

- A canonical **usage block** with multiple modes.
- A **flags table** (required/default/description).
- Multiple **examples** demonstrating non-trivial flag combinations.

Usage block (verbatim):

```bash
# Standard single-spec
/sc:roadmap <spec-file-path> [options]

# Multi-spec consolidation
/sc:roadmap --specs <spec1.md,spec2.md,...> [options]

# Multi-roadmap generation
/sc:roadmap <spec-file-path> --multi-roadmap --agents <agent-spec>[,...] [options]

# Combined mode
/sc:roadmap --specs <spec1.md,spec2.md> --multi-roadmap --agents <agent-spec>[,...] [options]
```

Flags table excerpt (verbatim):

> "| `--output` | `-o` | No | `.dev/releases/current/<spec-name>/` | Output directory |"
>
> "| `--depth` | `-d` | No | `standard` | Analysis depth: quick, standard, deep |"
>
> "| `--agents` | `-a` | With --multi-roadmap | - | Agent specs: `model[:persona[:\"instruction\"]]`. Persona is optional — if omitted, uses the auto-detected primary persona from Wave 1B for all agents. Examples: `opus,sonnet,gpt52` (model-only), `opus:architect,sonnet` (mixed), `opus:architect:\"prioritize scalability\"` (full) |"

---

## 2) Skill Design Pattern: Lean SKILL.md + `refs/` directory

### 2.1 Why split SKILL.md into behavior vs references

Exact quote (problem statement + solution):

> "A monolithic SKILL.md containing behavioral instructions mixed with YAML pseudocode algorithms, scoring formulas, agent prompts, and templates causes Claude to lose track of the high-level intent and produce inconsistent results. The solution separates concerns into a behavioral layer and a reference layer."

Exact quote (what goes where):

> "**SKILL.md** (~400 lines): Contains ONLY intent, flow, behavioral guidance, and decision boundaries. Tells Claude WHAT to do and WHEN, not HOW to compute scores."
>
> "**refs/ directory**: Contains the HOW — algorithms, formulas, prompts, and templates that SKILL.md references by name when needed."

Directory layout for a skill package (verbatim):

```text
src/superclaude/skills/sc-roadmap/
├── SKILL.md                        (~400 lines) Behavioral instructions
└── refs/
    ├── extraction-pipeline.md      Requirements extraction algorithm, domain keywords, ID assignment
    ├── scoring.md                  Complexity scoring formula, template compatibility scoring
    ├── validation.md               quality-engineer prompt, self-review prompt, score aggregation
    ├── templates.md                Milestone templates per domain, inline generation fallback
    └── adversarial-integration.md  Multi-spec/multi-roadmap invocation patterns, mode detection
```

### 2.2 SKILL.md outline and “do not include” rules

SKILL.md content outline (verbatim):

> "1. **Purpose & Identity** (~30 lines): What sc:roadmap does, key differentiator, pipeline position"
>
> "2. **Required Input** (~20 lines): Mandatory spec file, supported formats, validation rules"
>
> "3. **Flags & Options** (~40 lines): All flags including adversarial mode flags"
>
> "4. **Wave Architecture** (~150 lines): Wave 0-4 flow with behavioral descriptions (not algorithms)"
>
> "   - Each wave: purpose, entry criteria, behavioral instructions, exit criteria"
>
> "   - References to refs/ files for algorithmic details: \"Score complexity using the formula in `refs/scoring.md`\""
>
> "5. **Adversarial Modes** (~50 lines): When and how to invoke sc:adversarial (references `refs/adversarial-integration.md` for details)"
>
> "6. **Output Artifacts** (~40 lines): 3 artifacts defined with frontmatter schema"
>
> "7. **MCP Integration** (~20 lines): Server preferences and circuit breaker behavior"
>
> "8. **Boundaries** (~30 lines): Will do / will not do"
>
> "9. **Compliance** (~20 lines): Tier classification rules"

SKILL.md exclusions (verbatim):

> "**What SKILL.md does NOT contain**:"
>
> "- YAML pseudocode blocks"
>
> "- Scoring formulas or weight tables"
>
> "- Domain keyword dictionaries"
>
> "- Agent prompt templates"
>
> "- Template discovery search paths"
>
> "- Extraction pipeline step-by-step details"

### 2.3 Hard constraints (NFR) for skill authoring

Exact quote (line-count and content constraints):

> "### NFR-002: SKILL.md Size"
>
> "- SKILL.md must not exceed 500 lines"
>
> "- No YAML pseudocode blocks in SKILL.md"
>
> "- All algorithms, formulas, and agent prompts in refs/ files"
>
> "- refs/ files have no individual size limit but should be focused on a single concern"

---

## 3) Ref Loading Protocol (context management for skills)

The spec treats ref files as **on-demand context** rather than always-loaded.

### 3.1 Load refs per wave (not at activation)

Exact quote (primary rule):

> "Refs are loaded **on-demand per wave**, not pre-loaded at skill activation. This prevents context bloat and ensures Claude focuses on the current wave's concerns."

Wave → refs mapping (verbatim):

```markdown
| Wave | Refs Loaded | Rationale |
|------|------------|-----------|
| Wave 0 | None | Prerequisites use only native tools |
| Wave 1A | `refs/adversarial-integration.md` (if `--specs`) | Needed for sc:adversarial invocation |
| Wave 1B | `refs/extraction-pipeline.md` + `refs/scoring.md` | Extraction and complexity scoring |
| Wave 2 | `refs/templates.md` (+ `refs/adversarial-integration.md` if `--multi-roadmap`) | Template selection or adversarial invocation |
| Wave 3 | None (uses Wave 1B/2 context already loaded) | Generation uses already-loaded extraction and template data |
| Wave 4 | `refs/validation.md` | Agent prompts and scoring thresholds |
```

Limits and how the skill triggers ref reads (verbatim):

> "**Maximum refs loaded at any point**: 2-3. SKILL.md triggers loading via explicit instruction: \"Read `refs/scoring.md` and apply the complexity scoring formula.\""

### 3.2 How to test ref-loading behavior

The spec explicitly requires “ref loading tests”:

> "**Ref Loading Tests**:"
>
> "- Verify each ref file is loaded only when its wave executes"
>
> "- Wave 0: no Read calls to refs/"
>
> "- Wave 1B: Read calls to refs/extraction-pipeline.md and refs/scoring.md only"
>
> "- Wave 2: Read calls to refs/templates.md only (or refs/adversarial-integration.md if adversarial)"
>
> "- Wave 4: Read calls to refs/validation.md only"

---

## 4) Multi-Agent Concepts (developing/using “agents” inside skills)

This spec uses multiple agent roles as part of Wave execution; it also describes a “orchestrator agent” concept for adversarial scaling.

### 4.1 Dual-agent validation (quality-engineer + self-review)

Exact quote (multi-agent validation wave):

> "#### Wave 4: Validation (Multi-Agent)"
>
> "- Dispatch quality-engineer agent: completeness, consistency, traceability checks. Additionally validates test-strategy.md against:"
>
> "  - Interleave ratio matches complexity class (LOW→1:3, MEDIUM→1:2, HIGH→1:1)"
>
> "  - Every validation milestone references a real work milestone from roadmap.md"
>
> "  - Continuous parallel validation philosophy is explicitly encoded (not generic boilerplate)"
>
> "  - Stop-and-fix thresholds are defined for each severity level"
>
> "- Dispatch self-review agent: 4-question validation protocol"
>
> "- Score aggregation: PASS (≥85%) | REVISE (70-84%) | REJECT (<70%)"

REVISE loop behavior (verbatim):

> "- **REVISE loop**: If score is 70-84%:"
>
> "  1. Validation agents provide specific improvement recommendations"
>
> "  2. Wave 3 re-runs generation with improvement recommendations as additional input"
>
> "  3. Wave 4 re-validates (iteration 2)"
>
> "  4. If still REVISE after 2 iterations: accept with warning, set `validation_status: PASS_WITH_WARNINGS` in frontmatter"

### 4.2 Orchestrator agent for many competing variants (adversarial scaling)

Exact quote (orchestrator agent added at ≥5 agents):

> "With ≥5 agents, sc:roadmap adds an orchestrator agent that coordinates the adversarial debate rounds to prevent combinatorial explosion. The orchestrator groups similar variants and runs elimination rounds before the final merge."

### 4.3 Agent specification grammar (for multi-roadmap generation)

Agent spec format + semantics (verbatim):

> "**Agent spec format**: `model[:persona[:\"instruction\"]]`"
>
> "- **model** (required): Model identifier (e.g., `opus`, `sonnet`, `gpt52`, `gemini`)"
>
> "- **persona** (optional): If omitted, the agent uses the primary persona auto-detected from Wave 1B (domain analysis)."
>
> "- **instruction** (optional): Quoted custom instruction string passed to the agent"

Parsing rule (verbatim):

> "**Parsing rule**: Split on `,` for agent list, then split each agent on `:` (max 3 segments). First segment is always model. If second segment is quoted, it's an instruction (no persona). If unquoted, it's a persona."

Validation rule for models in agent specs (verbatim):

> "If `--multi-roadmap` flag present: validate all model identifiers in `--agents` are recognized models. Unrecognized models trigger abort with error: `\"Unknown model '<model>' in --agents. Available models: opus, sonnet, haiku, gpt52, gemini, ...\"`"

---

## 5) Skill Execution Architecture: Wave-based flow (Wave 0–4)

This spec codifies a generalizable pattern for complex skills: explicit waves, entry/exit criteria, progress messages, and state checkpoints.

### 5.1 Explicit wave requirements

In-scope bullet (verbatim):

> "- 5-wave architecture (Wave 0-4)"

Wave boundary progress reporting requirement (verbatim):

> "sc:roadmap emits progress messages at each wave boundary. These messages include:"
>
> "- Wave number and name"
>
> "- Completion status"
>
> "- Key decisions made"
>
> "- Next wave to execute"

### 5.2 Wave 0 prerequisites include skill dependency checks

The spec includes a pattern for commands/skills that depend on another skill (here: `sc:adversarial`).

Exact quote (dependency check + install guidance):

> "If `--specs` or `--multi-roadmap` flags present: check that `src/superclaude/skills/sc-adversarial/SKILL.md` exists (or installed equivalent). If not found, abort with error: \"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags. Install via: superclaude install\""

### 5.3 Output collision policy (non-overwrite)

Exact quote (collision strategy):

> "**Output collision check**: If output directory already contains roadmap artifacts (roadmap.md, extraction.md, test-strategy.md), do NOT overwrite. Instead, append `-2` suffix to all output filenames (e.g., `roadmap-2.md`, `extraction-2.md`, `test-strategy-2.md`). If `-2` also exists, increment to `-3`, etc. Log: `\"Output collision detected: writing to <filename>-N.md\"`"

### 5.4 Sequencing constraints inside a wave

Example: Wave 3 requires ordering (roadmap before test-strategy) because artifacts reference each other.

Exact quote:

> "**Sequencing constraint**: roadmap.md MUST be fully generated before test-strategy.md begins, because test-strategy.md references specific milestone IDs"

---

## 6) Skill Resumability + Cross-session Memory (Serena)

The spec defines a repeatable approach for session persistence and resumable wave pipelines.

### 6.1 Save points at wave boundaries

Exact quote:

> "Save points: sc:roadmap triggers `sc:save` automatically at each wave boundary:"
>
> "- After Wave 0: Save prerequisite validation state (spec paths, output dir, flags, collision suffix)"
>
> "- After Wave 1A: Save adversarial results (unified spec path, convergence score)"
>
> "- After Wave 1B: Save extraction results (extraction.md already written to disk), complexity score, persona selection"
>
> "- After Wave 2: Save template selection, milestone structure, dependency graph"
>
> "- After Wave 3: Save generation state (roadmap.md, test-strategy.md written to disk)"
>
> "- After Wave 4: Save validation results (final)"

### 6.2 Serena memory key + schema

Exact quote:

> "**Serena memory key**: `sc-roadmap:<spec-name>:<timestamp>` — stores:"

Schema (verbatim):

```yaml
roadmap_session:
  spec_source: <path>
  output_dir: <path>
  flags: {depth: standard, multi_roadmap: false, ...}
  last_completed_wave: <0|1A|1B|2|3|4>
  extraction_complete: <bool>
  complexity_score: <float>
  primary_persona: <string>
  template_selected: <string>
  milestone_count: <int>
  adversarial_results: <object|null>
  validation_score: <float|null>
```

### 6.3 Resume protocol + stale-state detection

Resume protocol (verbatim):

> "**Resume protocol**: When `sc:roadmap` is invoked and Serena memory contains a matching session (same spec path + output dir):"
>
> "1. Prompt user: `\"Found incomplete roadmap session (last completed: Wave X). Resume? [Y/n]\"`"
>
> "2. If yes: skip to the wave after `last_completed_wave`, reload artifacts from disk"
>
> "3. If no: start fresh (existing artifacts get `-N` suffix per collision protocol)"

Stale-state guard (verbatim):

> "**Limitation**: Resume is best-effort. If the spec file has been modified since the save point, sc:roadmap detects the mismatch (via file hash stored in memory) and warns: `\"Spec file has changed since last session. Starting fresh to avoid stale extraction.\"`"

---

## 7) `refs/` file responsibilities (what belongs in refs)

The spec explicitly enumerates what each `refs/*.md` file should contain. This acts as a template for skill authoring.

### 7.1 `refs/extraction-pipeline.md`

Verbatim:

> "**Contains**:"
>
> "- 8-step extraction pipeline (title → FRs → NFRs → scope → deps → success criteria → risks → ID assignment)"
>
> "- Domain keyword dictionaries (frontend, backend, security, performance, documentation)"
>
> "- Domain classification algorithm with keyword weighting"
>
> "- ID assignment rules"
>
> "- **Chunked extraction protocol** (FR-016): activation threshold (500 lines), section indexing, chunk assembly algorithm, per-chunk extraction template, merge algorithm, deduplication rules, cross-reference resolution, global ID assignment, 4-pass completeness verification, error handling, worked example"

### 7.2 `refs/scoring.md`

Verbatim:

> "**Contains**:"
>
> "- Complexity scoring formula (5 factors: requirement_count, dependency_depth, domain_spread, risk_severity, scope_size)"
>
> "- Factor weight table (0.25, 0.25, 0.20, 0.15, 0.15)"
>
> "- Classification thresholds (LOW < 0.4, MEDIUM 0.4-0.7, HIGH > 0.7)"
>
> "- Template compatibility scoring algorithm"
>
> "- Persona confidence calculation formula"

### 7.3 `refs/validation.md`

Verbatim:

> "**Contains**:"
>
> "- quality-engineer agent prompt (completeness, consistency, traceability checks)"
>
> "- self-review agent prompt (4-question protocol)"
>
> "- Score aggregation formula"
>
> "- Decision thresholds: PASS ≥85%, REVISE 70-84%, REJECT <70%"
>
> "- REVISE loop behavior (max 2 revision iterations)"

### 7.4 `refs/templates.md`

Verbatim:

> "**Contains**:"
>
> "- 4-tier template discovery search paths (local → user → plugin `[future: v5.0 plugin marketplace — plumb in here when available]` → inline generation)"
>
> "- Version resolution rules"
>
> "- Matching criteria"
>
> "- Inline template generation fallback algorithm (used when tiers 1-3 produce no match)"
>
> "- Milestone count selection by complexity"
>
> "- Domain-specific milestone mapping"
>
> "- Required sections per milestone"

### 7.5 `refs/adversarial-integration.md`

Verbatim:

> "**Contains**:"
>
> "- Mode detection logic (which flags trigger which adversarial mode)"
>
> "- sc:adversarial invocation patterns for multi-spec and multi-roadmap"
>
> "- Return contract **consumption** logic (how sc:roadmap handles each field). Note: the return contract schema itself is defined in SC-ADVERSARIAL-SPEC.md Section FR-007. This file documents only how sc:roadmap consumes that contract."
>
> "- Error handling for adversarial failures (success/partial/failed routing)"
>
> "- Frontmatter population from adversarial results"
>
> "- Divergent-specs heuristic (convergence <50% warning)"

---

## 8) Where custom commands/skills live (file structure)

The spec’s “complete file structure” section is directly relevant to adding a new command + skill.

Verbatim:

```text
src/superclaude/commands/
└── roadmap.md                          Command definition

src/superclaude/skills/sc-roadmap/
├── SKILL.md                            Lean behavioral instructions (~400 lines)
└── refs/
    ├── extraction-pipeline.md          Requirements extraction + domain classification
    ├── scoring.md                      Complexity + template compatibility scoring
    ├── validation.md                   Agent prompts + score aggregation
    ├── templates.md                    Template discovery + inline generation
    └── adversarial-integration.md      Multi-spec/multi-roadmap invocation patterns
```

---

## 9) Testing expectations for command/skill implementations

While the spec is about `/sc:roadmap`, the test categories it lists are generalizable requirements for implementing a robust command/skill.

Golden file testing pattern (verbatim):

> "**Golden File Tests**:"
>
> "- Run sc:roadmap on 3 canonical test specs of varying complexity (LOW, MEDIUM, HIGH)"
>
> "- Compare:"
>
> "  - extraction.md: requirement counts, domain distribution, complexity scores"
>
> "  - roadmap.md: milestone count, ordering, dependency structure"
>
> "  - test-strategy.md: interleave ratio matches complexity class"
>
> "- All YAML frontmatter parseable by standard YAML parser"

Adversarial integration tests (verbatim):

> "**Adversarial Integration Tests**:"
>
> "- Multi-spec with 2 specs: verify Wave 1A produces unified-spec.md, adversarial artifacts present, convergence in frontmatter"
>
> "- Multi-roadmap with 2 agents: verify Wave 2 produces unified roadmap via adversarial"
>
> "- Combined mode: verify both adversarial passes chain correctly"

Frontmatter contract tests (verbatim):

> "**Frontmatter Validation Tests**:"
>
> "- Parse all output frontmatter with YAML parser"
>
> "- Single-spec: verify `spec_source` present, `spec_sources` absent"
>
> "- Multi-spec: verify `spec_sources` present, `spec_source` absent"
>
> "- Adversarial mode: verify `adversarial` block present with all required subfields"

Edge case tests (verbatim):

> "**Edge Case Tests**:"
>
> "- Adversarial returns `status: partial` with convergence 55%: verify abort or user prompt"
>
> "- Adversarial returns `status: failed`: verify roadmap generation aborts with clear error"
>
> "- Wave 4 REVISE score: verify re-run loop (max 2 iterations)"
>
> "- `--specs` without sc:adversarial installed: verify Wave 0 abort with actionable error"

---

## 10) MCP integration guidance for a skill (servers + fallback)

Even though this is not a “how to implement MCP”, it is a **standardized skill header** pattern that a custom skill can follow.

MCP usage table (verbatim):

```markdown
| Server | Usage | Phase |
|--------|-------|-------|
| Sequential | Wave analysis, validation reasoning, complexity assessment | Waves 1-4 |
| Context7 | Template patterns, domain best practices, framework documentation | Waves 1-2 |
| Serena | Session persistence, memory, cross-session state | Wave 0, Wave 4 |
```

Circuit breaker fallback behaviors (verbatim):

> "**Circuit breaker**: See MCP.md for per-server settings. Key fallbacks:"
>
> "- Sequential unavailable → native Claude reasoning with reduced analysis depth"
>
> "- Context7 unavailable → WebSearch for documentation, note limitations"
>
> "- Serena unavailable → proceed without persistence, warn user"

---

## 11) Output contracts as a command/skill design pattern (frontmatter schemas)

While scoped to roadmap artifacts, the spec demonstrates a general command design principle: **machine-parseable frontmatter as a contract** with downstream commands.

Exact quote (schema stability):

> "### NFR-003: Frontmatter Stability"
>
> "- Frontmatter schema is a contract with the future tasklist generator"
>
> "- Fields may be added but not removed or renamed after initial release"
>
> "- New optional fields are backward-compatible; new required fields require a major version bump"

---

## 12) Notes on developing “template” systems and plugin extension points

The spec defines a “4-tier template discovery” model and explicitly reserves a plugin tier.

Exact quote:

> "- Check template directory availability (4-tier: local → user → plugin → inline generation `[future: plugin tier]`)"

And within `refs/templates.md` responsibilities (verbatim):

> "- 4-tier template discovery search paths (local → user → plugin `[future: v5.0 plugin marketplace — plumb in here when available]` → inline generation)"
