# Extraction: SC-ROADMAP V2 SPEC — Command, Skill, and Agent Development Patterns

**Source**: `/config/workspace/SuperClaude_Framework/.dev/releases/current/v2.0-roadmap-v2/SC-ROADMAP-V2-SPEC.md`
**Extracted**: 2026-02-21
**Spec Version**: 2.0.0 (Draft)
**Focus**: Architectural decisions, patterns, and extension points for developing custom commands, skills, and agents within SuperClaude

---

## 1. SKILL.md Architecture: The Lean Behavioral Split

The spec introduces a fundamental architectural pattern for how skills should be structured. This is arguably the most important design decision for anyone building custom skills.

### 1.1 Design Rationale

> "A monolithic SKILL.md containing behavioral instructions mixed with YAML pseudocode algorithms, scoring formulas, agent prompts, and templates causes Claude to lose track of the high-level intent and produce inconsistent results. The solution separates concerns into a behavioral layer and a reference layer." (Section 3.1)

### 1.2 Two-Layer Architecture

**SKILL.md** (~400 lines max): Contains ONLY intent, flow, behavioral guidance, and decision boundaries. Tells Claude WHAT to do and WHEN, not HOW to compute scores.

**refs/ directory**: Contains the HOW -- algorithms, formulas, prompts, and templates that SKILL.md references by name when needed.

Canonical directory structure:

```
src/superclaude/skills/sc-roadmap/
├── SKILL.md                        (~400 lines) Behavioral instructions
└── refs/
    ├── extraction-pipeline.md      Requirements extraction algorithm, domain keywords, ID assignment
    ├── scoring.md                  Complexity scoring formula, template compatibility scoring
    ├── validation.md               quality-engineer prompt, self-review prompt, score aggregation
    ├── templates.md                Milestone templates per domain, inline generation fallback
    └── adversarial-integration.md  Multi-spec/multi-roadmap invocation patterns, mode detection
```

### 1.3 What SKILL.md Must NOT Contain

> "What SKILL.md does NOT contain:
> - YAML pseudocode blocks
> - Scoring formulas or weight tables
> - Domain keyword dictionaries
> - Agent prompt templates
> - Template discovery search paths
> - Extraction pipeline step-by-step details" (Section 3.4)

### 1.4 SKILL.md Content Outline (Canonical Sections)

The spec prescribes 9 sections for the lean SKILL.md:

1. **Purpose & Identity** (~30 lines): What the skill does, key differentiator, pipeline position
2. **Required Input** (~20 lines): Mandatory inputs, supported formats, validation rules
3. **Flags & Options** (~40 lines): All flags including mode-specific flags
4. **Wave Architecture** (~150 lines): Wave flow with behavioral descriptions (not algorithms). Each wave: purpose, entry criteria, behavioral instructions, exit criteria. References to refs/ files: "Score complexity using the formula in `refs/scoring.md`"
5. **Mode Descriptions** (~50 lines): When and how to invoke sub-pipelines
6. **Output Artifacts** (~40 lines): Artifacts defined with frontmatter schema
7. **MCP Integration** (~20 lines): Server preferences and circuit breaker behavior
8. **Boundaries** (~30 lines): Will do / will not do
9. **Compliance** (~20 lines): Tier classification rules

### 1.5 Non-Functional Size Constraint

> "SKILL.md must not exceed 500 lines" (NFR-002)
> "No YAML pseudocode blocks in SKILL.md" (NFR-002)
> "All algorithms, formulas, and agent prompts in refs/ files" (NFR-002)
> "refs/ files have no individual size limit but should be focused on a single concern" (NFR-002)

---

## 2. Ref Loading Protocol (On-Demand Context Management)

A key performance pattern: refs are loaded on-demand per wave, NOT pre-loaded at skill activation. This prevents context bloat.

### 2.1 Loading Rules

> "Refs are loaded on-demand per wave, not pre-loaded at skill activation. This prevents context bloat and ensures Claude focuses on the current wave's concerns." (Section 3.3)

| Wave | Refs Loaded | Rationale |
|------|------------|-----------|
| Wave 0 | None | Prerequisites use only native tools |
| Wave 1A | `refs/adversarial-integration.md` (if conditional mode) | Needed for sub-pipeline invocation |
| Wave 1B | `refs/extraction-pipeline.md` + `refs/scoring.md` | Extraction and complexity scoring |
| Wave 2 | `refs/templates.md` (+ `refs/adversarial-integration.md` if conditional) | Template selection or sub-pipeline invocation |
| Wave 3 | None (uses Wave 1B/2 context already loaded) | Generation uses already-loaded data |
| Wave 4 | `refs/validation.md` | Agent prompts and scoring thresholds |

> "Maximum refs loaded at any point: 2-3. SKILL.md triggers loading via explicit instruction: 'Read `refs/scoring.md` and apply the complexity scoring formula.'" (Section 3.3)

---

## 3. Command File vs SKILL.md Relationship

The spec formalizes the separation between the command definition file and the skill implementation file.

### 3.1 Separation Principle

| File | Location | Purpose | Size |
|------|----------|---------|------|
| `commands/roadmap.md` | `src/superclaude/commands/` | Claude Code command definition: triggers, flags, usage examples, behavioral summary, boundaries | ~80 lines |
| `SKILL.md` | `src/superclaude/skills/sc-roadmap/` | Full behavioral instructions: wave flow, decision logic, ref loading triggers, mode orchestration | ~400 lines |

> "The command file tells Claude Code WHEN to activate and WHAT the command does (surface-level). The SKILL.md tells Claude HOW to execute (behavioral detail). The command file is installed to `~/.claude/commands/sc/` and is loaded when the user types `/sc:roadmap`. The SKILL.md is installed to `~/.claude/skills/` and is loaded by the command file's activation." (Section 3.5)

### 3.2 Installation Targets

- Commands install to: `~/.claude/commands/sc/`
- Skills install to: `~/.claude/skills/`

---

## 4. Agent Architecture and Patterns

### 4.1 Multi-Agent Validation (Dual-Agent Pattern)

The spec uses a dual-agent validation pattern in Wave 4:

- **quality-engineer agent**: Completeness, consistency, traceability checks. Validates test-strategy.md against specific criteria.
- **self-review agent**: 4-question validation protocol.

Agent prompts are stored in `refs/validation.md`, not in the SKILL.md.

> "Dispatch quality-engineer agent: completeness, consistency, traceability checks."
> "Dispatch self-review agent: 4-question validation protocol" (Wave 4, Section FR-006)

### 4.2 Score Aggregation

> "Score aggregation: PASS (>=85%) | REVISE (70-84%) | REJECT (<70%)" (Wave 4)

### 4.3 Agent Spec Format (for Multi-Agent Invocations)

The spec defines a formal agent specification format for the `--agents` flag:

> "Agent spec format: `model[:persona[:"instruction"]]`
> - **model** (required): Model identifier (e.g., `opus`, `sonnet`, `gpt52`, `gemini`)
> - **persona** (optional): If omitted, the agent uses the primary persona auto-detected from Wave 1B
> - **instruction** (optional): Quoted custom instruction string passed to the agent" (FR-004)

**Parsing rule**:

> "Split on `,` for agent list, then split each agent on `:` (max 3 segments). First segment is always model. If second segment is quoted, it's an instruction (no persona). If unquoted, it's a persona." (FR-004)

### 4.4 Orchestrator Agent for Large Agent Counts

> "With >=5 agents, sc:roadmap adds an orchestrator agent that coordinates the adversarial debate rounds to prevent combinatorial explosion. The orchestrator groups similar variants and runs elimination rounds before the final merge." (FR-004)

### 4.5 Agent Count Constraints

> "Agent count: 2-10 agents (inherits sc:adversarial's range)." (FR-004)

### 4.6 SKILL.md vs Agent Authoring Decision

The spec explicitly documents when SKILL.md should author content directly vs delegating to an agent:

> "SKILL.md authors test-strategy.md (not a separate agent) because it has full context, correct timing (Wave 3, before validation), and zero coordination overhead. The quality-engineer in Wave 4 validates test-strategy.md against explicit criteria but does not author it." (Wave 3 in FR-006)

---

## 5. Wave Architecture Pattern

### 5.1 5-Wave Structure

The spec uses a 5-wave architecture (Wave 0-4) as the execution model. This is a reusable pattern for complex skills:

- **Wave 0**: Prerequisites and validation (input exists, dependencies installed, output collision check)
- **Wave 1A**: Conditional sub-pipeline (only runs when specific flags present)
- **Wave 1B**: Detection and analysis (extraction, scoring, classification)
- **Wave 2**: Planning and template selection
- **Wave 3**: Generation (actual artifact creation)
- **Wave 4**: Multi-agent validation

### 5.2 Wave Entry/Exit Criteria Pattern

Each wave has:
- Purpose
- Entry criteria
- Behavioral instructions
- Exit criteria
- Progress emission: `"Wave N complete: <summary>."`

### 5.3 Progress Reporting

> "sc:roadmap emits progress messages at each wave boundary. These messages include:
> - Wave number and name
> - Completion status
> - Key decisions made
> - Next wave to execute" (FR-013)

---

## 6. Integration Patterns Between Components

### 6.1 Skill-to-Skill Invocation (sc:roadmap -> sc:adversarial)

The spec defines how one skill invokes another as a sub-pipeline:

**Multi-spec invocation**:
```
sc:adversarial --compare <spec-files> --depth <roadmap-depth> --output <roadmap-output-dir>
```

**Multi-roadmap invocation**:
```
sc:adversarial --source <spec-or-unified-spec> --generate roadmap --agents <agent-specs> --depth <roadmap-depth> --output <roadmap-output-dir>
```

### 6.2 Return Contract Pattern

Skills communicate via a return contract with defined fields:

> "Return contract consumption:
> - `status: success` -> use `merged_output_path` as input for subsequent waves
> - `status: partial` -> convergence >=60%: proceed with warning; convergence <60%: prompt user or abort
> - `status: failed` -> abort with error
> - `merged_output_path`: Use as input for subsequent waves
> - `convergence_score`: Record in frontmatter for traceability
> - `artifacts_dir`: Record in frontmatter for traceability
> - `unresolved_conflicts`: If >0, log warning" (Section 7.1)

### 6.3 Dependency Checking at Wave 0

> "If `--specs` or `--multi-roadmap` flags present: check that `src/superclaude/skills/sc-adversarial/SKILL.md` exists (or installed equivalent). If not found, abort with error: 'sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags. Install via: superclaude install'" (Wave 0, FR-006)

### 6.4 Downstream Contract (Frontmatter as API)

The roadmap.md YAML frontmatter is designed as a contract for the future tasklist generator:

> "Key fields the tasklist generator will consume:
> - `milestone_index`: Direct mapping to task phases
> - `complexity_score` / `complexity_class`: Informs effort estimation
> - `domain_distribution`: Informs specialist assignment
> - `total_deliverables`: Validates task count against roadmap scope
> - `validation_status`: Gates tasklist generation (REJECT blocks it)
> - `adversarial.convergence_score`: Confidence signal" (Section 7.2)

### 6.5 Frontmatter Stability Contract

> "Frontmatter schema is a contract with the future tasklist generator. Fields may be added but not removed or renamed after initial release. New optional fields are backward-compatible; new required fields require a major version bump." (NFR-003)

---

## 7. Session Persistence and Resumability

### 7.1 Save Points at Wave Boundaries

> "sc:roadmap triggers `sc:save` automatically at each wave boundary" (Section 7.3)

Each wave boundary saves specific state:
- After Wave 0: prerequisite validation state (spec paths, output dir, flags, collision suffix)
- After Wave 1A: adversarial results (unified spec path, convergence score)
- After Wave 1B: extraction results, complexity score, persona selection
- After Wave 2: template selection, milestone structure, dependency graph
- After Wave 3: generation state (artifacts written to disk)
- After Wave 4: validation results (final)

### 7.2 Serena Memory Key Format

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

Memory key format: `sc-roadmap:<spec-name>:<timestamp>`

### 7.3 Resume Protocol

> "When `sc:roadmap` is invoked and Serena memory contains a matching session (same spec path + output dir):
> 1. Prompt user: 'Found incomplete roadmap session (last completed: Wave X). Resume? [Y/n]'
> 2. If yes: skip to the wave after `last_completed_wave`, reload artifacts from disk
> 3. If no: start fresh (existing artifacts get `-N` suffix per collision protocol)" (Section 7.3)

### 7.4 Stale Data Detection

> "If the spec file has been modified since the save point, sc:roadmap detects the mismatch (via file hash stored in memory) and warns: 'Spec file has changed since last session. Starting fresh to avoid stale extraction.'" (Section 7.3)

---

## 8. MCP Server Integration Pattern

### 8.1 Per-Phase MCP Assignment

| Server | Usage | Phase |
|--------|-------|-------|
| Sequential | Wave analysis, validation reasoning, complexity assessment | Waves 1-4 |
| Context7 | Template patterns, domain best practices, framework documentation | Waves 1-2 |
| Serena | Session persistence, memory, cross-session state | Wave 0, Wave 4 |

### 8.2 Circuit Breaker Fallbacks

> "Sequential unavailable -> native Claude reasoning with reduced analysis depth"
> "Context7 unavailable -> WebSearch for documentation, note limitations"
> "Serena unavailable -> proceed without persistence, warn user" (Section 11)

---

## 9. Template Discovery Pattern (4-Tier)

The spec defines a 4-tier template discovery system for milestone templates:

1. **Local**: Project-local templates
2. **User**: User-level templates
3. **Plugin**: Future v5.0 plugin marketplace (noted as `[future: plugin tier]`)
4. **Inline generation**: Fallback algorithm when tiers 1-3 produce no match

> "4-tier template discovery search paths (local -> user -> plugin `[future: v5.0 plugin marketplace -- plumb in here when available]` -> inline generation)" (refs/templates.md spec, Section 9.4)

---

## 10. Output Collision Protocol

A reusable pattern for skills that produce output artifacts:

> "If output directory already contains roadmap artifacts (roadmap.md, extraction.md, test-strategy.md), do NOT overwrite. Instead, append `-2` suffix to all output filenames (e.g., `roadmap-2.md`, `extraction-2.md`, `test-strategy-2.md`). If `-2` also exists, increment to `-3`, etc." (Wave 0, FR-006)

---

## 11. YAML Frontmatter as Machine-Parseable Contracts

All output artifacts use YAML frontmatter with a defined schema. This serves as a machine-parseable API between pipeline stages.

Key design rules:
- Every output artifact includes YAML frontmatter
- Exactly one of `spec_source` or `spec_sources` is present, never both (mode-dependent)
- Fields may be added but not removed or renamed (backward compatibility)
- New required fields require a major version bump

---

## 12. Pipeline Position and No-Handoff Pattern

The spec defines a strict pipeline position with manual user triggers between stages:

> "Pipeline Position: `spec(s) -> sc:roadmap -> roadmap artifacts -> (user triggers) -> future tasklist command -> (user triggers) -> sc:task-unified`" (Section 1)

> "sc:roadmap does not trigger or reference any downstream commands." (FR-008)

---

## 13. Compliance Tier Classification

Skills integrate with the SuperClaude compliance system:

> The SKILL.md includes a "Compliance" section (~20 lines) containing tier classification rules (Section 3.4, item 9).

The `--compliance` flag allows forcing a specific tier: `strict`, `standard`, `light`.

---

## 14. Future Extension Points

### 14.1 Plugin Marketplace (v5.0)

Template discovery tier 3 is explicitly reserved for a future plugin marketplace:

> "plugin `[future: v5.0 plugin marketplace -- plumb in here when available]`" (Section 9.4)

### 14.2 Future Tasklist Generator Command

The spec repeatedly references a future dedicated command that consumes roadmap.md:

> "Dependents: Future tasklist generator command (consumes roadmap.md output)" (Metadata)

The frontmatter schema is designed as the contract for this future command.

### 14.3 Refs as Extension Points

The refs/ directory structure allows individual algorithm components to be swapped, updated, or extended without modifying the core SKILL.md behavioral instructions. Each ref file is focused on a single concern and can evolve independently.

---

## 15. Validation and REVISE Loop Pattern

### 15.1 REVISE Loop

A reusable pattern for iterative quality improvement within a skill:

> "If score is 70-84%:
> 1. Validation agents provide specific improvement recommendations
> 2. Wave 3 re-runs generation with improvement recommendations as additional input
> 3. Wave 4 re-validates (iteration 2)
> 4. If still REVISE after 2 iterations: accept with warning, set `validation_status: PASS_WITH_WARNINGS` in frontmatter" (Wave 4, FR-006)

### 15.2 Validation Statuses

- `PASS` (>=85%)
- `REVISE` (70-84%) -- triggers loop
- `REJECT` (<70%)
- `PASS_WITH_WARNINGS` -- after 2 REVISE iterations
- `SKIPPED` -- when `--no-validate` flag used

---

## 16. Complete File Structure

```
src/superclaude/commands/
└── roadmap.md                          Command definition (~80 lines)

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

## 17. Key Takeaways for Custom Command/Skill Development

1. **Separate intent from algorithm**: SKILL.md describes WHAT and WHEN; refs/ describe HOW
2. **Size-limit SKILL.md**: 500 lines max, no embedded pseudocode or formulas
3. **Load refs on-demand per wave**: Never pre-load all refs at skill activation
4. **Command files are thin**: ~80 lines defining triggers, flags, and surface-level description
5. **Use YAML frontmatter as contracts**: Machine-parseable, versioned, backward-compatible
6. **Agent prompts live in refs/**: Not in SKILL.md, not in command files
7. **Wave architecture**: Prerequisites -> Analysis -> Planning -> Generation -> Validation
8. **Return contracts between skills**: status/merged_output_path/convergence_score pattern
9. **Check dependencies at Wave 0**: Fail fast with actionable error messages
10. **Save state at wave boundaries**: Enable cross-session resumability via Serena
11. **Output collision avoidance**: Append `-N` suffix, never overwrite
12. **Dual-agent validation**: Separate quality-engineer and self-review agents
13. **REVISE loop**: Max 2 iterations, then accept with warnings
14. **Progress reporting**: Emit at every wave boundary
15. **No downstream handoff**: Each skill produces artifacts; users trigger the next stage
