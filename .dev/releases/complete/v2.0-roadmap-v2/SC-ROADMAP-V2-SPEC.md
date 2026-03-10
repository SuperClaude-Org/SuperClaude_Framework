# SC-ROADMAP SPEC: Roadmap Generator with Adversarial Multi-Spec/Multi-Roadmap Support

## Metadata
- **Version**: 2.0.0 (spec iteration 1.3.0)
- **Status**: Draft (P0 review complete)
- **Author**: Brainstorm session (sc:roadmap requirements discovery)
- **Date**: 2026-02-21
- **Dependencies**: sc:adversarial v1.1.0 (multi-spec and multi-roadmap modes)
- **Dependents**: Future tasklist generator command (consumes roadmap.md output)
- **Priority**: P1

---

## 1. Executive Summary

`/sc:roadmap` generates deterministic release roadmap packages from specification documents. The architecture uses a lean SKILL.md (~400 lines) focused on intent, flow, and behavioral guidance, with all algorithms, scoring formulas, agent prompts, and templates in a `refs/` directory.

**Core capabilities**:
- **Single-spec roadmap generation**: Parse a specification, extract requirements, generate a milestone-based roadmap
- **Multi-spec consolidation**: Merge multiple specification documents into a unified spec via `/sc:adversarial` before roadmap generation
- **Multi-roadmap generation**: Generate competing roadmap variants using different model/persona configurations and merge the best elements via `/sc:adversarial`

The roadmap is a planning artifact — the user manually triggers the next stage (tasklist generation, then task execution). No downstream handoff.

**Pipeline Position**: `spec(s) → sc:roadmap → roadmap artifacts → (user triggers) → future tasklist command → (user triggers) → sc:task-unified`

---

## 2. Scope

### 2.1 In Scope

- Single-spec roadmap generation
- Multi-spec consolidation via sc:adversarial `--compare` mode
- Multi-roadmap generation via sc:adversarial `--source --generate roadmap --agents` mode
- Combined mode (multi-spec → multi-roadmap)
- YAML frontmatter on all output artifacts for machine parseability
- Continuous parallel validation philosophy for test-strategy.md
- 5-wave architecture (Wave 0-4)
- SKILL.md restructure: lean behavioral file + refs/ directory
- Dual-agent validation (quality-engineer + self-review)
- Serena memory persistence for cross-session state

### 2.2 Out of Scope

- Tasklist generation (separate dedicated command consumes roadmap.md)
- Execution prompt generation (not roadmap's responsibility)
- Handoff to sc:task or any execution command
- Git operations (user's responsibility)
- Cost optimization or token budgeting during adversarial modes

---

## 3. Architecture: SKILL.md Split

### 3.1 Design Rationale

A monolithic SKILL.md containing behavioral instructions mixed with YAML pseudocode algorithms, scoring formulas, agent prompts, and templates causes Claude to lose track of the high-level intent and produce inconsistent results. The solution separates concerns into a behavioral layer and a reference layer.

### 3.2 Architecture: Lean SKILL.md + refs/ Directory

**SKILL.md** (~400 lines): Contains ONLY intent, flow, behavioral guidance, and decision boundaries. Tells Claude WHAT to do and WHEN, not HOW to compute scores.

**refs/ directory**: Contains the HOW — algorithms, formulas, prompts, and templates that SKILL.md references by name when needed.

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

### 3.3 Ref Loading Protocol

Refs are loaded **on-demand per wave**, not pre-loaded at skill activation. This prevents context bloat and ensures Claude focuses on the current wave's concerns.

| Wave | Refs Loaded | Rationale |
|------|------------|-----------|
| Wave 0 | None | Prerequisites use only native tools |
| Wave 1A | `refs/adversarial-integration.md` (if `--specs`) | Needed for sc:adversarial invocation |
| Wave 1B | `refs/extraction-pipeline.md` + `refs/scoring.md` | Extraction and complexity scoring |
| Wave 2 | `refs/templates.md` (+ `refs/adversarial-integration.md` if `--multi-roadmap`) | Template selection or adversarial invocation |
| Wave 3 | None (uses Wave 1B/2 context already loaded) | Generation uses already-loaded extraction and template data |
| Wave 4 | `refs/validation.md` | Agent prompts and scoring thresholds |

**Maximum refs loaded at any point**: 2-3. SKILL.md triggers loading via explicit instruction: "Read `refs/scoring.md` and apply the complexity scoring formula."

### 3.4 Command File vs SKILL.md Relationship

| File | Location | Purpose | Size |
|------|----------|---------|------|
| `commands/roadmap.md` | `src/superclaude/commands/` | Claude Code command definition: triggers, flags, usage examples, behavioral summary, boundaries | ~80 lines |
| `SKILL.md` | `src/superclaude/skills/sc-roadmap/` | Full behavioral instructions: wave flow, decision logic, ref loading triggers, adversarial mode orchestration | ~400 lines |

**Separation principle**: The command file tells Claude Code WHEN to activate and WHAT the command does (surface-level). The SKILL.md tells Claude HOW to execute (behavioral detail). The command file is installed to `~/.claude/commands/sc/` and is loaded when the user types `/sc:roadmap`. The SKILL.md is installed to `~/.claude/skills/` and is loaded by the command file's activation.

### 3.5 SKILL.md Content Outline

The lean SKILL.md contains:

1. **Purpose & Identity** (~30 lines): What sc:roadmap does, key differentiator, pipeline position
2. **Required Input** (~20 lines): Mandatory spec file, supported formats, validation rules
3. **Flags & Options** (~40 lines): All flags including adversarial mode flags
4. **Wave Architecture** (~150 lines): Wave 0-4 flow with behavioral descriptions (not algorithms)
   - Each wave: purpose, entry criteria, behavioral instructions, exit criteria
   - References to refs/ files for algorithmic details: "Score complexity using the formula in `refs/scoring.md`"
5. **Adversarial Modes** (~50 lines): When and how to invoke sc:adversarial (references `refs/adversarial-integration.md` for details)
6. **Output Artifacts** (~40 lines): 3 artifacts defined with frontmatter schema
7. **MCP Integration** (~20 lines): Server preferences and circuit breaker behavior
8. **Boundaries** (~30 lines): Will do / will not do
9. **Compliance** (~20 lines): Tier classification rules

**What SKILL.md does NOT contain**:
- YAML pseudocode blocks
- Scoring formulas or weight tables
- Domain keyword dictionaries
- Agent prompt templates
- Template discovery search paths
- Extraction pipeline step-by-step details

---

## 4. Functional Requirements

### FR-001: Output Artifacts (3 files)

sc:roadmap produces exactly 3 artifacts:

| Artifact | Purpose | Consumed By |
|----------|---------|-------------|
| `roadmap.md` | Master roadmap with milestones, dependencies, risk register | User review, future tasklist generator |
| `extraction.md` | Structured extraction of all requirements, domain analysis, complexity scoring | Roadmap generation (internal), user reference |
| `test-strategy.md` | Continuous parallel validation philosophy and strategy | Future tasklist generator (validation milestones) |

All artifacts use YAML frontmatter + human-readable body.

### FR-002: YAML Frontmatter Schema

Every output artifact includes machine-parseable YAML frontmatter optimized for ongoing project value and downstream consumption by the future tasklist generator.

**Spec source field rule**: Exactly one of `spec_source` or `spec_sources` is present, never both:
- **Single-spec mode**: `spec_source: <path>` (scalar string)
- **Multi-spec mode**: `spec_sources: [<path1>, <path2>, ...]` (list)

#### roadmap.md frontmatter

```yaml
---
spec_source: <path-to-source-spec>                  # Input traceability
spec_sources: [<path1>, <path2>]                     # Multi-spec mode
generated: <ISO-8601 timestamp>
generator: sc:roadmap
complexity_score: <0.0-1.0>
complexity_class: <LOW|MEDIUM|HIGH>
domain_distribution:
  frontend: <percentage>
  backend: <percentage>
  security: <percentage>
  performance: <percentage>
  documentation: <percentage>
primary_persona: <persona-name>
consulting_personas: [<persona1>, <persona2>]
milestone_count: <N>
milestone_index:
  - id: M1
    title: <title>
    type: <FEATURE|IMPROVEMENT|DOC|TEST|MIGRATION|SECURITY>
    priority: <P0|P1|P2|P3>
    dependencies: [<M-refs>]
    deliverable_count: <N>
    risk_level: <Low|Medium|High>
  - id: M2
    # ...
total_deliverables: <N>
total_risks: <N>
estimated_phases: <N>                                # Hint for tasklist generator
validation_score: <0.0-1.0>                          # From Wave 4
validation_status: <PASS|REVISE|REJECT>
adversarial:                                         # Present only if adversarial mode used
  mode: <multi-spec|multi-roadmap|combined>
  agents: [<agent-spec-1>, <agent-spec-2>]
  convergence_score: <0.0-1.0>
  base_variant: <model:persona>                          # e.g., "opus:architect" — identifies which agent's variant was selected as the merge base
  artifacts_dir: <path-to-adversarial-artifacts>
---
```

#### extraction.md frontmatter

```yaml
---
spec_source: <path>
generated: <ISO-8601 timestamp>
generator: sc:roadmap
functional_requirements: <count>
nonfunctional_requirements: <count>
total_requirements: <count>
domains_detected: [<domain-list>]
complexity_score: <0.0-1.0>
risks_identified: <count>
dependencies_identified: <count>
success_criteria_count: <count>
---
```

#### test-strategy.md frontmatter

```yaml
---
spec_source: <path>
generated: <ISO-8601 timestamp>
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: <count>
work_milestones: <count>
interleave_ratio: "<validation>:<work>"              # Computed from complexity class
major_issue_policy: stop-and-fix
---
```

### FR-003: Multi-Spec Consolidation Mode

When multiple specification files are provided, sc:roadmap invokes sc:adversarial to produce a unified spec before roadmap generation.

**Trigger**: `--specs spec1.md,spec2.md[,...,specN.md]` flag

**Flow**:
```
User invokes: /sc:roadmap --specs spec1.md,spec2.md,spec3.md

Wave 0: Validate all spec files exist and are readable
Wave 1A: Invoke sc:adversarial --compare spec1.md,spec2.md,spec3.md --depth <adversarial-depth>
          → Produces unified-spec.md + adversarial/ artifacts
Wave 1B: Run extraction pipeline on unified-spec.md
Waves 2-4: Standard roadmap generation from unified extraction
```

**Conflict resolution**: Auto-resolve by default (sc:adversarial default). User can add `--interactive` to approve conflict resolution decisions.

**Divergent-specs heuristic**: If sc:adversarial returns convergence <50%, emit warning: "Specifications may be too divergent for meaningful consolidation. Consider running separate roadmaps or using --interactive for manual conflict resolution."

### FR-004: Multi-Roadmap Generation Mode

When multiple agents are specified, sc:roadmap generates competing roadmap variants and merges the best elements via sc:adversarial.

**Trigger**: `--multi-roadmap --agents <agent-spec>[,<agent-spec>,...]` flag

**Agent spec format**: `model[:persona[:"instruction"]]`
- **model** (required): Model identifier (e.g., `opus`, `sonnet`, `gpt52`, `gemini`)
- **persona** (optional): If omitted, the agent uses the primary persona auto-detected from Wave 1B (domain analysis). This means `--agents opus,sonnet,gpt52` produces 3 roadmap variants all using the same persona but different models — useful for testing model diversity without persona variation.
- **instruction** (optional): Quoted custom instruction string passed to the agent

**Agent count**: 2-10 agents (inherits sc:adversarial's range). With ≥5 agents, sc:roadmap adds an orchestrator agent that coordinates the adversarial debate rounds to prevent combinatorial explosion. The orchestrator groups similar variants and runs elimination rounds before the final merge.

**Parsing rule**: Split on `,` for agent list, then split each agent on `:` (max 3 segments). First segment is always model. If second segment is quoted, it's an instruction (no persona). If unquoted, it's a persona.

**Flow**:
```
User invokes: /sc:roadmap spec.md --multi-roadmap --agents opus,sonnet,gpt52

Waves 0-1: Standard prerequisite validation and extraction
           (Wave 1B detects primary persona, e.g., "security")
Wave 2: Expand model-only agents → opus:security, sonnet:security, gpt52:security
         Invoke sc:adversarial --source spec.md --generate roadmap --agents opus:security,sonnet:security,gpt52:security
         → Produces unified-roadmap.md + adversarial/ artifacts
Waves 3-4: Standard validation on the unified roadmap
```

### FR-005: Combined Mode

When both `--specs` and `--multi-roadmap` are provided, sc:roadmap runs both adversarial pipelines sequentially.

**Trigger**: `--specs` AND `--multi-roadmap --agents` flags together

**Flow**:
```
User invokes: /sc:roadmap --specs spec1.md,spec2.md --multi-roadmap --agents opus:architect,sonnet:security

Wave 0: Validate all spec files
Wave 1A: sc:adversarial --compare spec1.md,spec2.md → unified-spec.md
Wave 1B: Extract from unified-spec.md
Wave 2: sc:adversarial --source unified-spec.md --generate roadmap --agents opus:architect,sonnet:security → unified-roadmap.md
Waves 3-4: Validation on unified roadmap
```

### FR-006: 5-Wave Architecture

#### Wave 0: Prerequisites
- Validate specification file(s) exist and are readable
- Validate output directory is writable
- **Output collision check**: If output directory already contains roadmap artifacts (roadmap.md, extraction.md, test-strategy.md), do NOT overwrite. Instead, append `-2` suffix to all output filenames (e.g., `roadmap-2.md`, `extraction-2.md`, `test-strategy-2.md`). If `-2` also exists, increment to `-3`, etc. Log: `"Output collision detected: writing to <filename>-N.md"`
- Check template directory availability (4-tier: local → user → plugin → inline generation `[future: plugin tier]`)
- Log fallback decisions
- If `--specs` or `--multi-roadmap` flags present: check that `src/superclaude/skills/sc-adversarial/SKILL.md` exists (or installed equivalent). If not found, abort with error: "sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags. Install via: superclaude install"
- If `--multi-roadmap` flag present: validate all model identifiers in `--agents` are recognized models. Unrecognized models trigger abort with error: `"Unknown model '<model>' in --agents. Available models: opus, sonnet, haiku, gpt52, gemini, ..."`
- Emit progress: `"Wave 0 complete: prerequisites validated."`

#### Wave 1A: Spec Consolidation (conditional — only when `--specs` flag present)
- Load `refs/adversarial-integration.md`
- Invoke sc:adversarial with the provided spec files
- Handle return contract:
  - `status: success` → proceed with `merged_output_path` as the spec input for Wave 1B
  - `status: partial` + convergence ≥60% → proceed with warning logged in extraction.md
  - `status: partial` + convergence <60% → if `--interactive`, prompt user for approval; otherwise abort with recommendation to use `--interactive`
  - `status: failed` → abort roadmap generation with error
- Apply divergent-specs heuristic (convergence <50% warning)
- Emit progress: `"Wave 1A complete: spec consolidation finished (convergence: XX%)."`

#### Wave 1B: Detection & Analysis
- Load `refs/extraction-pipeline.md` + `refs/scoring.md`
- Parse specification file (single spec or unified spec from Wave 1A)
- If spec exceeds 500 lines: activate chunked extraction protocol (FR-016). Otherwise: standard single-pass extraction
- Run extraction pipeline
- **Write extraction.md** to output directory (extraction is complete at this point; writing early enables resumability and provides immediate user value)
- Score complexity
- Classify domains and activate personas
- If `--persona` flag was provided, override auto-detected primary persona with user-specified persona
- Emit progress: `"Wave 1B complete: extraction finished (XX requirements, complexity: X.XX). extraction.md written."`

#### Wave 2: Planning & Template Selection
- Load `refs/templates.md` (+ `refs/adversarial-integration.md` if `--multi-roadmap`)
- Template discovery (4-tier search with scoring)
- Create milestone structure based on complexity and domain
- Map dependencies between milestones
- If `--multi-roadmap` flag: invoke sc:adversarial for multi-roadmap generation. The adversarial output replaces the template-based generation.
- Emit progress: `"Wave 2 complete: N milestones planned."`

#### Wave 3: Generation
- **Step 1**: Generate roadmap.md with YAML frontmatter + milestone hierarchy + Decision Summary
- **Step 2** (after roadmap.md is complete): Generate test-strategy.md referencing the concrete milestones from Step 1. The SKILL.md authors test-strategy.md directly using:
  - Interleave ratio computed from complexity score (available from Wave 1B)
  - Concrete milestone names from the just-generated roadmap.md
  - The continuous parallel validation philosophy (encoded in SKILL.md behavioral instructions)
  - The structural template defined in FR-007
- **Sequencing constraint**: roadmap.md MUST be fully generated before test-strategy.md begins, because test-strategy.md references specific milestone IDs
- **Authoring rationale**: SKILL.md authors test-strategy.md (not a separate agent) because it has full context, correct timing (Wave 3, before validation), and zero coordination overhead. The quality-engineer in Wave 4 validates test-strategy.md against explicit criteria but does not author it.
- Emit progress: `"Wave 3 complete: roadmap.md + test-strategy.md generated."`

#### Wave 4: Validation (Multi-Agent)
- Load `refs/validation.md`
- Dispatch quality-engineer agent: completeness, consistency, traceability checks. Additionally validates test-strategy.md against:
  - Interleave ratio matches complexity class (LOW→1:3, MEDIUM→1:2, HIGH→1:1)
  - Every validation milestone references a real work milestone from roadmap.md
  - Continuous parallel validation philosophy is explicitly encoded (not generic boilerplate)
  - Stop-and-fix thresholds are defined for each severity level
- Dispatch self-review agent: 4-question validation protocol
- Score aggregation: PASS (≥85%) | REVISE (70-84%) | REJECT (<70%)
- If adversarial mode was used:
  - Missing adversarial artifacts when adversarial mode was used → REJECT
  - Missing convergence score in frontmatter → REVISE
- Write validation score to roadmap.md frontmatter
- **REVISE loop**: If score is 70-84%:
  1. Validation agents provide specific improvement recommendations
  2. Wave 3 re-runs generation with improvement recommendations as additional input
  3. Wave 4 re-validates (iteration 2)
  4. If still REVISE after 2 iterations: accept with warning, set `validation_status: PASS_WITH_WARNINGS` in frontmatter
- Emit progress: `"Wave 4 complete: validation score X.XX (STATUS)."`

### FR-007: Test Strategy — Continuous Parallel Validation Philosophy

The `test-strategy.md` artifact encodes a specific validation philosophy:

**Core Assumption**: Work has deviated from the plan, is incomplete, or contains errors. This is the default assumption until validation proves otherwise.

**Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The ratio of validation milestones to work milestones is defined in frontmatter (`interleave_ratio`)

**test-strategy.md body structure**:
```markdown
## Validation Philosophy
[Continuous parallel validation description]

## Validation Milestones
| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M1 (Foundation) | Requirements coverage, dependency setup | Missing >20% requirements |
| V2 | M3 (Core Impl) | Functional correctness, integration points | Breaking integration |
| ...

## Issue Classification
| Severity | Action | Example |
|----------|--------|---------|
| Critical | Stop work, fix immediately | Breaking dependency, security flaw |
| Major | Stop work, refactor before next milestone | Missing core requirement |
| Minor | Log, address in next validation pass | Documentation gap, style issue |
| Info | Log only | Optimization opportunity |

## Acceptance Gates
[Per-milestone acceptance criteria derived from spec requirements]
```

### FR-008: No Downstream Handoff

sc:roadmap does not trigger or reference any downstream commands. The final output message states:
```
Roadmap generation complete. Artifacts written to <output-dir>/:
  - roadmap.md (N milestones, complexity: X.XX)
  - extraction.md (N requirements extracted)
  - test-strategy.md (continuous parallel validation)

Review the roadmap before proceeding to tasklist generation.
```

### FR-009: Depth Flag Mapping

The `--depth` flag controls both sc:roadmap's internal analysis depth and the adversarial debate depth when adversarial modes are active.

| sc:roadmap --depth | Internal behavior | sc:adversarial --depth |
|--------------------|--------------------|------------------------|
| `quick` | Reduced extraction, skip template scoring | `quick` (1 debate round) |
| `standard` | Full extraction and template scoring | `standard` (2 debate rounds) |
| `deep` | Full extraction + enhanced complexity analysis | `deep` (3 debate rounds) |

If the user needs independent control over adversarial debate depth, they should invoke sc:adversarial separately and pass the result to sc:roadmap via `--specs` with the unified output.

### FR-010: Adversarial Availability Check

If `--specs` or `--multi-roadmap` flags are present, sc:roadmap checks that sc:adversarial skill is installed and available. If not found, it aborts with a clear error message and actionable install instructions.

### FR-011: Partial Status Handling

When sc:adversarial returns `status: partial`, sc:roadmap handles it based on convergence score:
- `convergence_score ≥ 60%`: Proceed with warning logged in extraction.md
- `convergence_score < 60%`: If `--interactive`, prompt user for approval; otherwise abort with recommendation to use `--interactive`

### FR-012: Artifact Validation Consequences

If sc:adversarial returns `status: failed`, sc:roadmap aborts roadmap generation with an error message. The error includes:
- `status: failed`
- `merged_output_path` (if present)
- `unresolved_conflicts` count
- `artifacts_dir` (if present)

### FR-013: Progress Reporting

sc:roadmap emits progress messages at each wave boundary. These messages include:
- Wave number and name
- Completion status
- Key decisions made
- Next wave to execute

### FR-014: Worked Example

**Input**:
- Specification file: `auth-spec.md` (50 lines)
- Complexity: 8 functional requirements, 2 non-functional requirements, 3 risks identified
- Domains: Security (55%), Backend (35%), Performance (10%)

**Command**:
```bash
/sc:roadmap auth-spec.md --depth standard
```

**Expected Output**:
- `extraction.md`: 8 functional requirements, 2 non-functional requirements, 3 risks
- `roadmap.md`: 5 milestones, 15 deliverables, 2 validation milestones
- `test-strategy.md`: Continuous parallel validation philosophy with 2 milestones

### FR-015: Testing Section

**Golden File Tests**:
- Run sc:roadmap on 3 canonical test specs of varying complexity (LOW, MEDIUM, HIGH)
- Compare:
  - extraction.md: requirement counts, domain distribution, complexity scores
  - roadmap.md: milestone count, ordering, dependency structure
  - test-strategy.md: interleave ratio matches complexity class
- All YAML frontmatter parseable by standard YAML parser

**Ref Loading Tests**:
- Verify each ref file is loaded only when its wave executes
- Wave 0: no Read calls to refs/
- Wave 1B: Read calls to refs/extraction-pipeline.md and refs/scoring.md only
- Wave 2: Read calls to refs/templates.md only (or refs/adversarial-integration.md if adversarial)
- Wave 4: Read calls to refs/validation.md only

**Adversarial Integration Tests**:
- Multi-spec with 2 specs: verify Wave 1A produces unified-spec.md, adversarial artifacts present, convergence in frontmatter
- Multi-roadmap with 2 agents: verify Wave 2 produces unified roadmap via adversarial
- Combined mode: verify both adversarial passes chain correctly

**Frontmatter Validation Tests**:
- Parse all output frontmatter with YAML parser
- Single-spec: verify `spec_source` present, `spec_sources` absent
- Multi-spec: verify `spec_sources` present, `spec_source` absent
- Adversarial mode: verify `adversarial` block present with all required subfields

**Edge Case Tests**:
- Adversarial returns `status: partial` with convergence 55%: verify abort or user prompt
- Adversarial returns `status: failed`: verify roadmap generation aborts with clear error
- Wave 4 REVISE score: verify re-run loop (max 2 iterations)
- `--specs` without sc:adversarial installed: verify Wave 0 abort with actionable error

### FR-016: Chunked Extraction Protocol

When a specification file exceeds the context-safe threshold, sc:roadmap activates chunked extraction to process the spec in multiple passes with full completeness verification.

**Activation**: Automatic when spec file exceeds 500 lines. Below threshold, standard single-pass extraction is used.

**Algorithm overview**:
1. **Section index**: Scan spec headings (H1-H3) to build a structural map with line ranges and extraction-relevance tags (FR_BLOCK, NFR_BLOCK, SCOPE, DEPS, RISKS, SUCCESS, OTHER)
2. **Chunk assembly**: Group sections into chunks of ~400 lines (hard max 600). Never split within a section. Oversized sections split at paragraph boundaries. Title/overview section prepended as context header to every chunk.
3. **Per-chunk extraction**: Each chunk processed with the standard 8-step extraction pipeline, producing a partial result with `source_line` references back to the original spec. Global ID counters passed between chunks to prevent collisions.
4. **Merge**: Concatenate partial results by category in document order. No re-interpretation — structural combination only.
5. **Deduplication**: (a) ID collision → keep first occurrence; (b) Normalized description match → keep first, log duplicate; (c) Substring match (ratio >0.8) → keep both, flag for review.
6. **Cross-reference resolution**: Unresolved references from one chunk matched against items in other chunks. Unresolvable references logged as warnings.
7. **Global ID assignment**: Explicit IDs preserved. Implicit items assigned sequential IDs ordered by source_line for determinism.

**Completeness verification (4-pass protocol)**:
| Pass | Name | Method | Threshold |
|------|------|--------|-----------|
| 1 | Source Coverage | Grep original spec for requirement patterns; verify each appears in extraction | 100% PASS, ≥95% WARN, <95% FAIL |
| 2 | Anti-Hallucination | For each extracted item, verify `source_line` matches actual spec content | 100% (zero tolerance) |
| 3 | Section Coverage | Verify every extraction-relevant section was assigned to a chunk | 100% |
| 4 | Count Reconciliation | chunk_totals - dedup_removals = merged_totals | Exact match |

**On verification failure**: Re-process failing chunks (max 1 retry). If still failing: STOP with error. Do not produce partial extraction.

**Output**: extraction.md in identical format to single-pass extraction, plus two metadata lines: `extraction_mode: chunked (N chunks)` and verification summary.

**Full algorithm specification**: Documented in `refs/extraction-pipeline.md` under the Chunked Extraction Protocol section, including chunking pseudocode, per-chunk template, deduplication rules, cross-reference resolution, ID assignment strategy, error handling, and a worked example with a 1500-line spec.

### FR-017: REVISE Loop

If the validation score is between 70-84% (REVISE range), sc:roadmap enters a REVISE loop. The loop:
1. Validates the current roadmap against the spec
2. If issues found: dispatches validation agents to provide specific improvement recommendations
3. Re-runs Wave 3 with improvements as additional input
4. Re-validates in Wave 4
5. If still REVISE after 2 iterations: accepts with warning, sets `validation_status: PASS_WITH_WARNINGS`

### FR-018: Dry Run Mode

When `--dry-run` is specified, sc:roadmap executes Waves 0-2 (prerequisites, extraction, planning) but skips Wave 3 (generation) and Wave 4 (validation). Instead of writing files, it outputs a structured preview to console:

**Console output format**:
```
=== DRY RUN: sc:roadmap ===

Spec: <spec-file-path>
Complexity: <score> (<class>)
Primary Persona: <persona> (confidence: <score>)
Template: <template-name or "inline">

Milestone Structure:
  M1: <title> [<type>] [P<priority>] — <N> deliverables
    Dependencies: None
  M2: <title> [<type>] [P<priority>] — <N> deliverables
    Dependencies: M1
  ...

Domain Distribution: backend <N>%, frontend <N>%, security <N>%, ...
Estimated Deliverables: <N>
Estimated Risks: <N>

Output would be written to: <output-dir>/
  - roadmap.md
  - extraction.md
  - test-strategy.md

=== END DRY RUN ===
```

**Behavior**:
- Waves 0-2 execute normally (extraction and planning are computed)
- No files are written to disk
- No validation agents are dispatched
- No session persistence (sc:save not triggered)
- extraction.md data is computed internally but not written
- If `--dry-run` is combined with `--specs` or `--multi-roadmap`, the adversarial invocations in Wave 1A/2 are still executed (they are part of planning)

### FR-019: Compliance Tier Behavior

The `--compliance` flag controls the rigor of sc:roadmap's execution, mapping to extraction depth and validation behavior:

| Tier | Extraction | Template Search | Validation | Use Case |
|------|-----------|-----------------|-----------|----------|
| `strict` | Full 8-step extraction + 4-pass verification (even for specs <500 lines) | All 4 tiers searched | Full Wave 4 with REVISE loop | High-stakes roadmaps, regulated domains |
| `standard` | Standard extraction (chunked only for >500 lines) | All 4 tiers searched | Full Wave 4 | Default behavior |
| `light` | Reduced extraction (title, FRs, NFRs, risks only — skip deps, success criteria, scope) | Inline generation only (skip tiers 1-3) | Skip Wave 4, set `validation_status: LIGHT` | Quick planning, exploratory roadmaps |

**Auto-detection**: When `--compliance auto` (default), the tier is determined by the spec's characteristics:
- Spec mentions security/auth/compliance keywords → STRICT
- Spec >500 lines → STRICT
- Spec <100 lines with <5 requirements → LIGHT
- All other cases → STANDARD

### FR-020: Template Discovery and Selection

Wave 2 performs template discovery using a 4-tier search with compatibility scoring:

**4-Tier Search Order**:
1. **Local** (project-level): `.dev/templates/roadmap/` in current project
2. **User** (user-level): `~/.claude/templates/roadmap/`
3. **Plugin** (marketplace): `[future: v5.0 plugin marketplace — plumb in here when available]`
4. **Inline generation** (fallback): Generate template structure from extraction data

**Template Compatibility Scoring**: Each discovered template is scored against the extraction data:

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Domain match | 0.40 | Overlap between template's `domains` field and spec's detected domains |
| Complexity alignment | 0.30 | Closeness of template's `target_complexity` to spec's complexity score |
| Type match | 0.20 | Template `type` matches spec's dominant requirement type (feature, migration, security, etc.) |
| Version compatibility | 0.10 | Template's `min_version` ≤ current sc:roadmap version |

**Selection rule**: Use the highest-scoring template with score ≥ 0.6. If no template scores ≥ 0.6, fall back to inline generation. If `--template` flag is explicitly set, skip scoring and use the specified template type directly.

**Template file format** (expected in tiers 1-3):
```yaml
---
name: security-roadmap
type: security
domains: [security, backend]
target_complexity: 0.7
min_version: "2.0.0"
milestone_count_range: [5, 9]
---
# Template body with milestone structure placeholders
```

---

## 5. Non-Functional Requirements

### NFR-001: Performance
- Standard single-spec roadmap: <2 minutes
- Multi-spec consolidation: +sc:adversarial time (variable, see adversarial spec NFR-001)
- Multi-roadmap generation: +sc:adversarial time (variable)
- Combined mode: additive of both adversarial invocations

### NFR-002: SKILL.md Size
- SKILL.md must not exceed 500 lines
- No YAML pseudocode blocks in SKILL.md
- All algorithms, formulas, and agent prompts in refs/ files
- refs/ files have no individual size limit but should be focused on a single concern

### NFR-003: Frontmatter Stability
- Frontmatter schema is a contract with the future tasklist generator
- Fields may be added but not removed or renamed after initial release
- New optional fields are backward-compatible; new required fields require a major version bump

**v2.0 Migration Note**: The v1.x roadmap generator used `generated_by` and `generated_at` field names. v2.0 standardizes on `generator` and `generated` (ISO-8601 timestamp). This is a **breaking change** from v1.x output. The new names are canonical; any tooling consuming roadmap frontmatter must update to the new field names. The stability guarantee (additions only, no renames) applies from v2.0 forward.

---

## 6. Command Interface

### 6.1 Usage

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

### 6.2 Flags

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `<spec-file-path>` | | Yes (single-spec) | - | Path to specification document |
| `--specs` | | Yes (multi-spec) | - | Comma-separated spec file paths (2-10) |
| `--template` | `-t` | No | Auto-detect | Template type: feature, quality, docs, security, performance, migration |
| `--output` | `-o` | No | `.dev/releases/current/<spec-name>/` | Output directory |
| `--depth` | `-d` | No | `standard` | Analysis depth: quick, standard, deep |
| `--multi-roadmap` | | No | `false` | Enable multi-roadmap adversarial generation |
| `--agents` | `-a` | With --multi-roadmap | - | Agent specs: `model[:persona[:"instruction"]]`. Persona is optional — if omitted, uses the auto-detected primary persona from Wave 1B for all agents. Examples: `opus,sonnet,gpt52` (model-only), `opus:architect,sonnet` (mixed), `opus:architect:"prioritize scalability"` (full) |
| `--interactive` | `-i` | No | `false` | User approval at adversarial decision points |
| `--validate` | `-v` | No | `true` | Enable multi-agent validation (Wave 4) |
| `--no-validate` | | No | `false` | Skip validation phase. Sets `validation_score: 0.0` and `validation_status: SKIPPED` in frontmatter |
| `--compliance` | `-c` | No | Auto-detect | Force compliance tier: strict, standard, light (see FR-019) |
| `--persona` | `-p` | No | Auto-select | Override primary persona |
| `--dry-run` | | No | `false` | Preview roadmap structure without writing files (see FR-018) |

### 6.3 Examples

```bash
# Basic single-spec
/sc:roadmap specs/auth-system.md

# Deep analysis with security template
/sc:roadmap specs/migration-plan.md --template security --depth deep

# Consolidate 3 specs into one roadmap
/sc:roadmap --specs specs/frontend.md,specs/backend.md,specs/security.md

# Generate 3 competing roadmaps (model-only — all use auto-detected persona)
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus,sonnet,gpt52

# Generate 3 competing roadmaps with explicit personas
/sc:roadmap specs/v2-prd.md --multi-roadmap \
  --agents opus:architect,sonnet:security,opus:analyzer

# Mixed: some with persona, some model-only (model-only inherits primary persona)
/sc:roadmap specs/v2-prd.md --multi-roadmap \
  --agents opus:architect,sonnet,gpt52:security

# Full combined mode with interactive approval
/sc:roadmap --specs specs/v2-prd.md,specs/v2-addendum.md \
  --multi-roadmap --agents opus:architect:"prioritize scalability",sonnet:security \
  --interactive --depth deep

# Custom output
/sc:roadmap specs/auth.md --output .dev/releases/current/v2.0-auth/
```

---

## 7. Integration Points

### 7.1 sc:adversarial Integration

sc:roadmap invokes sc:adversarial as a sub-pipeline in two scenarios. The invocation pattern and return contract handling are documented in `refs/adversarial-integration.md`.

**Multi-spec invocation**:
```
sc:adversarial --compare <spec-files> --depth <roadmap-depth> --output <roadmap-output-dir>
```

**Multi-roadmap invocation**:
```
sc:adversarial --source <spec-or-unified-spec> --generate roadmap --agents <agent-specs> --depth <roadmap-depth> --output <roadmap-output-dir>
```

**Return contract consumption**:
- `status: success` → use `merged_output_path` as input for subsequent waves
- `status: partial` → convergence ≥60%: proceed with warning in extraction.md; convergence <60%: prompt user (if `--interactive`) or abort
- `status: failed` → abort roadmap generation with error
- `merged_output_path`: Use as input for subsequent waves
- `convergence_score`: Record in roadmap.md frontmatter
- `artifacts_dir`: Record in roadmap.md frontmatter for traceability
- `unresolved_conflicts`: If >0, log warning in extraction.md

### 7.2 Future Tasklist Generator Integration

The roadmap.md YAML frontmatter is designed as a contract for the future tasklist generator. Key fields the tasklist generator will consume:

- `milestone_index`: Direct mapping to task phases
- `complexity_score` / `complexity_class`: Informs effort estimation
- `domain_distribution`: Informs specialist assignment
- `total_deliverables`: Validates task count against roadmap scope
- `validation_status`: Gates tasklist generation (REJECT blocks it)
- `adversarial.convergence_score`: Confidence signal for the tasklist generator

The future tasklist generator expects roadmap items with: headings → phases, bullets → tasks, explicit IDs (M1, D1.1) → traceability. The roadmap.md body format is designed to be parseable by this convention.

### 7.3 Session Persistence & Resumability

sc:roadmap integrates with `sc:save` and `sc:load` for cross-session resumability. If a roadmap generation is interrupted mid-wave, the user can resume from the last completed wave in a new session.

**Save points**: sc:roadmap triggers `sc:save` automatically at each wave boundary:
- After Wave 0: Save prerequisite validation state (spec paths, output dir, flags, collision suffix)
- After Wave 1A: Save adversarial results (unified spec path, convergence score)
- After Wave 1B: Save extraction results (extraction.md already written to disk), complexity score, persona selection
- After Wave 2: Save template selection, milestone structure, dependency graph
- After Wave 3: Save generation state (roadmap.md, test-strategy.md written to disk)
- After Wave 4: Save validation results (final)

**Serena memory key**: `sc-roadmap:<spec-name>:<timestamp>` — stores:
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

**Resume protocol**: When `sc:roadmap` is invoked and Serena memory contains a matching session (same spec path + output dir):
1. Prompt user: `"Found incomplete roadmap session (last completed: Wave X). Resume? [Y/n]"`
2. If yes: skip to the wave after `last_completed_wave`, reload artifacts from disk
3. If no: start fresh (existing artifacts get `-N` suffix per collision protocol)

**Limitation**: Resume is best-effort. If the spec file has been modified since the save point, sc:roadmap detects the mismatch (via file hash stored in memory) and warns: `"Spec file has changed since last session. Starting fresh to avoid stale extraction."`

---

## 8. Artifact Body Templates

### 8.1 roadmap.md body (after frontmatter)

```markdown
# Roadmap: <Project Title>

## Overview
<1-3 paragraph summary of the roadmap scope, approach, and key decisions>

## Milestone Summary

| ID | Title | Type | Priority | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------------|--------------|------|
| M1 | <title> | FEATURE | P1 | None | 3 | Low |
| M2 | <title> | IMPROVEMENT | P1 | M1 | 5 | Medium |

## Dependency Graph
<Visual or textual representation of milestone dependencies>

---

## M1: <Milestone Title>

### Objective
<Clear milestone goal>

### Deliverables
| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | <deliverable> | <measurable outcome> |
| D1.2 | <deliverable> | <measurable outcome> |

### Dependencies
- None (first milestone) OR
- M{N}: <what is needed from that milestone>

### Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| <risk> | Low/Medium/High | Low/Medium/High | <mitigation> |

---

## M2: <Milestone Title>
[Same structure as M1]

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | <risk> | M1, M3 | Medium | High | <mitigation> | <persona> |

## Decision Summary

Records key decisions made during roadmap generation for auditability and downstream context.

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | <persona> | <other candidates with scores> | <highest domain % or --persona override> |
| Template | <template-name or "inline"> | <other templates with compatibility scores> | <best match or fallback reason> |
| Milestone Count | <N> | <range considered> | <complexity class → count mapping> |
| Adversarial Mode | <mode or "none"> | N/A | <flags present or absent> |
| Adversarial Base Variant | <model:persona or "N/A"> | <other variants with scores> | <highest convergence contribution> |

**Generation rule**: Every row must cite the specific data point that drove the decision (complexity score, domain %, convergence score, flag presence). No subjective justifications.

## Success Criteria
<Derived from spec success criteria, mapped to milestones>
```

### 8.2 extraction.md body (after frontmatter)

```markdown
# Extraction: <Spec Title>

## Functional Requirements

| ID | Requirement | Domain | Priority | Source Line(s) |
|----|-------------|--------|----------|----------------|
| FR-001 | <requirement description> | backend | P0 | L12-L18 |
| FR-002 | <requirement description> | security | P1 | L25-L30 |

## Non-Functional Requirements

| ID | Requirement | Category | Constraint |
|----|-------------|----------|------------|
| NFR-001 | <requirement description> | performance | <measurable threshold> |
| NFR-002 | <requirement description> | security | <compliance standard> |

## Domain Distribution

| Domain | Percentage | Key Indicators |
|--------|-----------|----------------|
| backend | 45% | API endpoints, data models, service logic |
| security | 30% | Authentication, authorization, encryption |
| frontend | 15% | UI components, user flows |
| performance | 10% | Latency requirements, caching |

## Complexity Analysis

| Factor | Raw Value | Normalized (0-1) | Weight | Weighted Score |
|--------|-----------|-------------------|--------|----------------|
| requirement_count | <N> | <0-1> | 0.25 | <score> |
| dependency_depth | <N> | <0-1> | 0.25 | <score> |
| domain_spread | <N> | <0-1> | 0.20 | <score> |
| risk_severity | <N> | <0-1> | 0.15 | <score> |
| scope_size | <N> | <0-1> | 0.15 | <score> |
| **Total** | | | | **<complexity_score>** |

**Complexity Class**: <LOW|MEDIUM|HIGH>

## Persona Assignment

| Role | Persona | Confidence | Rationale |
|------|---------|------------|-----------|
| Primary | <persona> | <0-1> | Highest domain % |
| Consulting | <persona> | <0-1> | Secondary domain |

## Dependencies

| ID | Dependency | Type | Affected Requirements |
|----|------------|------|----------------------|
| DEP-001 | <dependency description> | internal/external | FR-001, FR-003 |

## Risks

| ID | Risk | Probability | Impact | Affected Requirements |
|----|------|-------------|--------|----------------------|
| RISK-001 | <risk description> | Low/Medium/High | Low/Medium/High | FR-002 |

## Success Criteria

| ID | Criterion | Derived From | Measurable |
|----|-----------|-------------|------------|
| SC-001 | <criterion> | FR-001, NFR-001 | Yes/No |

## Warnings
<Any warnings from adversarial partial status, convergence issues, or extraction anomalies>
```

### 8.3 test-strategy.md body

See FR-007 for the complete body structure.

**Interleave ratio algorithm**:
- Complexity LOW: `1:3` (one validation milestone per three work milestones)
- Complexity MEDIUM: `1:2` (one validation milestone per two work milestones)
- Complexity HIGH: `1:1` (one validation milestone per work milestone)

---

## 9. refs/ File Specifications

### 9.1 refs/extraction-pipeline.md
**Contains**:
- 8-step extraction pipeline (title → FRs → NFRs → scope → deps → success criteria → risks → ID assignment)
- Domain keyword dictionaries (frontend, backend, security, performance, documentation)
- Domain classification algorithm with keyword weighting
- ID assignment rules
- **Chunked extraction protocol** (FR-016): activation threshold (500 lines), section indexing, chunk assembly algorithm, per-chunk extraction template, merge algorithm, deduplication rules, cross-reference resolution, global ID assignment, 4-pass completeness verification, error handling, worked example

### 9.2 refs/scoring.md
**Contains**:
- Complexity scoring formula (5 factors: requirement_count, dependency_depth, domain_spread, risk_severity, scope_size)
- Factor weight table (0.25, 0.25, 0.20, 0.15, 0.15)
- Classification thresholds (LOW < 0.4, MEDIUM 0.4-0.7, HIGH > 0.7)
- Template compatibility scoring algorithm
- Persona confidence calculation formula

### 9.3 refs/validation.md
**Contains**:
- quality-engineer agent prompt (completeness, consistency, traceability checks)
- self-review agent prompt (4-question protocol)
- Score aggregation formula
- Decision thresholds: PASS ≥85%, REVISE 70-84%, REJECT <70%
- REVISE loop behavior (max 2 revision iterations)

### 9.4 refs/templates.md
**Contains**:
- 4-tier template discovery search paths (local → user → plugin `[future: v5.0 plugin marketplace — plumb in here when available]` → inline generation)
- Version resolution rules
- Matching criteria
- Inline template generation fallback algorithm (used when tiers 1-3 produce no match)
- Milestone count selection by complexity
- Domain-specific milestone mapping
- Required sections per milestone

### 9.5 refs/adversarial-integration.md
**Contains**:
- Mode detection logic (which flags trigger which adversarial mode)
- sc:adversarial invocation patterns for multi-spec and multi-roadmap
- Return contract **consumption** logic (how sc:roadmap handles each field). Note: the return contract schema itself is defined in SC-ADVERSARIAL-SPEC.md Section FR-007. This file documents only how sc:roadmap consumes that contract.
- Error handling for adversarial failures (success/partial/failed routing)
- Frontmatter population from adversarial results
- Divergent-specs heuristic (convergence <50% warning)

---

## 10. Boundaries

### Will Do
- Generate structured roadmaps from specification files (single or multiple)
- Invoke sc:adversarial for multi-spec consolidation and multi-roadmap generation
- Apply multi-agent validation for quality assurance
- Create milestone-based roadmaps with dependency graphs and risk registers
- Produce YAML frontmatter optimized for downstream tasklist generator consumption
- Generate continuous parallel validation strategy (test-strategy.md)
- Persist session state via Serena memory
- Support multiple template types with 4-tier discovery

### Will Not Do
- Generate tasklist files (separate dedicated command)
- Generate execution prompts (not roadmap's responsibility)
- Execute implementation tasks
- Trigger downstream commands automatically
- Make business prioritization decisions
- Generate roadmaps without specification input
- Write outside designated output directories
- Modify source specification files

---

## 11. MCP Integration

| Server | Usage | Phase |
|--------|-------|-------|
| Sequential | Wave analysis, validation reasoning, complexity assessment | Waves 1-4 |
| Context7 | Template patterns, domain best practices, framework documentation | Waves 1-2 |
| Serena | Session persistence, memory, cross-session state | Wave 0, Wave 4 |

**Circuit breaker**: See MCP.md for per-server settings. Key fallbacks:
- Sequential unavailable → native Claude reasoning with reduced analysis depth
- Context7 unavailable → WebSearch for documentation, note limitations
- Serena unavailable → proceed without persistence, warn user

---

## 12. Success Criteria

### Functional
- [ ] Single-spec mode produces roadmap.md, extraction.md, test-strategy.md with valid YAML frontmatter
- [ ] `--specs` flag invokes sc:adversarial and produces unified spec before roadmap generation
- [ ] `--multi-roadmap --agents` flag invokes sc:adversarial and produces merged roadmap
- [ ] Combined mode chains both adversarial invocations correctly
- [ ] `--interactive` flag propagates to sc:adversarial invocations
- [ ] Wave 4 validation produces PASS/REVISE/REJECT with score in frontmatter
- [ ] REVISE loop re-runs Wave 3 → Wave 4 up to 2 iterations
- [ ] Adversarial `status: partial` handled with convergence-based routing
- [ ] Progress reporting emitted at each wave boundary
- [ ] No references to tasklist generation, execution prompts, or downstream command triggering
- [ ] Output collision appends `-N` suffix instead of overwriting
- [ ] `--no-validate` sets `validation_status: SKIPPED` and `validation_score: 0.0` in frontmatter
- [ ] `--persona` override propagates to model-only agents in `--agents`
- [ ] Model identifiers in `--agents` validated in Wave 0
- [ ] Agent count enforced: 2-10 range
- [ ] sc:save triggered at each wave boundary for resumability
- [ ] Resume from interrupted session detected and offered via Serena memory
- [ ] Chunked extraction activates for large specs and verifies completeness
- [ ] `--dry-run` executes Waves 0-2 and outputs structured preview without writing files
- [ ] `--compliance` tier auto-detection based on spec characteristics (keywords, size, requirement count)
- [ ] `--compliance light` skips Wave 4 and sets `validation_status: LIGHT`
- [ ] Template discovery searches 4 tiers with compatibility scoring ≥0.6 threshold
- [ ] Template scoring uses domain match (0.40), complexity alignment (0.30), type match (0.20), version (0.10)

### Architecture
- [ ] SKILL.md ≤500 lines with no YAML pseudocode
- [ ] refs/ directory contains 5 files covering all algorithms
- [ ] Every algorithm in refs/ is referenced by name from SKILL.md
- [ ] No algorithm duplication between SKILL.md and refs/ files
- [ ] Refs loaded on-demand per wave (max 2-3 at any point)

### Quality
- [ ] YAML frontmatter is parseable by standard YAML parsers
- [ ] Exactly one of spec_source or spec_sources present in frontmatter (never both)
- [ ] test-strategy.md encodes continuous parallel validation philosophy with computed interleave_ratio
- [ ] All frontmatter fields documented with types and constraints
- [ ] Adversarial metadata in frontmatter when adversarial modes used
- [ ] Every milestone has: objective, deliverables with IDs, dependencies, risk assessment
- [ ] roadmap.md body includes Decision Summary section

---

## 15. Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SKILL.md split causes Claude to miss ref files | Medium | High | SKILL.md explicitly references each ref by name; on-demand loading protocol prevents context bloat |
| sc:adversarial unavailable/not installed | Low | High | Detect at Wave 0; abort with actionable install instructions |
| Frontmatter schema breaks future tasklist generator | Medium | Medium | Schema is a versioned contract; additions only, no removals |
| Multi-spec mode produces incoherent unified spec | Medium | Medium | Adversarial debate + validation in Wave 4; divergent-specs heuristic warns at <50% convergence |
| Combined mode takes too long (two adversarial passes) | Medium | Low | No cost/time constraints per requirement; progress reporting keeps user informed |
| Adversarial partial status causes silent quality degradation | Medium | Medium | Explicit convergence thresholds: ≥60% proceed with warning, <60% abort or prompt |
| Large spec files overwhelm context window | Medium | High | Chunked extraction protocol activates above threshold; completeness verification ensures no data loss |
| Interrupted session produces partial/stale artifacts | Low | Medium | sc:save at wave boundaries; resume protocol with spec-hash mismatch detection |
| Unrecognized model in --agents causes late failure | Low | Medium | Wave 0 validates all model identifiers before starting |

---

## 16. File Structure (Complete)

```
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

## 17. Version History

- **1.0.0** (2026-02-21): Initial draft from sc:roadmap brainstorm session
- **1.1.0** (2026-02-21): Incorporated 16 spec-panel recommendations (Wave 1A/1B split, ref loading protocol, REVISE loop, testing strategy, worked example, etc.)
- **1.2.0** (2026-02-21): Incorporated 15 brainstorm answers: model-only agent shorthand, output collision protocol (-N suffix), chunked extraction protocol, session resumability via sc:save/sc:load, Decision Summary section, formalized extraction.md template, Wave 0 model validation, orchestrator for ≥5 agents, test-strategy.md authoring rationale, plugin tier future notes
- **1.3.0** (2026-02-21): P0 fixes from spec-panel review round 3: Added FR-018 (--dry-run behavior), FR-019 (--compliance tier behavior for sc:roadmap), FR-020 (template discovery and compatibility scoring). Added --dry-run to flags table. Fixed section numbering (3.3→3.4→3.5). Added NFR-003 v2.0 migration note for frontmatter field naming. Updated success criteria with new FR verification items. Total FRs: 20.

---

*Specification generated from /sc:brainstorm requirements discovery session*
*Reviewed via /sc:spec-panel (3 rounds) + brainstorm expansion*
