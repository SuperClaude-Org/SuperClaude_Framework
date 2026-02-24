---
name: sc:roadmap-protocol
description: "Full behavioral protocol for sc:roadmap — roadmap generation from specifications with adversarial integration"
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
argument-hint: "<spec-file-path> [--specs ...] [--multi-roadmap --agents ...] [--depth quick|standard|deep] [--output dir]"
---

# /sc:roadmap — Roadmap Generator

<!-- Extended metadata (for documentation, not parsed):
category: planning
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, scribe, analyzer]
version: 2.0.0
spec: SC-ROADMAP-V2-SPEC.md
-->

## Triggers

sc:roadmap-protocol is invoked ONLY by the `sc:roadmap` command via `Skill sc:roadmap-protocol` in the `## Activation` section. It is never invoked directly by users.

Activation conditions:
- User runs `/sc:roadmap <spec-file>` in Claude Code
- Any `--specs`, `--multi-roadmap`, or `--agents` flags are passed through from the command

Do NOT invoke this skill directly. Use the `sc:roadmap` command.

## 1. Purpose & Identity

Generate deterministic release roadmap packages from specification documents with integrated multi-agent validation. sc:roadmap transforms project requirements, feature descriptions, or PRD files into structured, milestone-based roadmaps.

**Key Differentiator**: Requires a specification file as mandatory input — roadmaps are grounded in documented requirements, not ad-hoc descriptions.

**Pipeline Position**: `spec(s) → sc:roadmap → roadmap artifacts → (user triggers) → future tasklist command → (user triggers) → sc:task-unified`

The roadmap is a **planning artifact**. sc:roadmap does not trigger downstream commands. The user manually initiates subsequent stages.

**Core Capabilities**:
- **Single-spec roadmap generation**: Parse one spec, extract requirements, generate a milestone-based roadmap
- **Multi-spec consolidation**: Merge multiple specs into a unified spec via `sc:adversarial` before roadmap generation
- **Multi-roadmap generation**: Generate competing roadmap variants using different model/persona configurations, merge the best elements via `sc:adversarial`

**Output Artifacts** (3 files):
1. `roadmap.md` — Master roadmap with milestones, dependencies, risk register, decision summary
2. `extraction.md` — Structured extraction of all requirements, domain analysis, complexity scoring
3. `test-strategy.md` — Continuous parallel validation philosophy and strategy

All artifacts include YAML frontmatter for machine parseability.

## 2. Required Input

**MANDATORY**: A specification file path OR `--specs` flag with multiple paths.

```
/sc:roadmap <spec-file-path>
/sc:roadmap --specs <spec1.md,spec2.md,...>
```

**Supported Formats**: `.md` (primary), `.txt`, `.yaml`/`.yml`, `.json`

## 3. Flags & Options

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `<spec-file-path>` | | Yes (single-spec) | - | Path to specification document |
| `--specs` | | Yes (multi-spec) | - | Comma-separated spec file paths (2-10) |
| `--template` | `-t` | No | Auto-detect | Template type: feature, quality, docs, security, performance, migration |
| `--output` | `-o` | No | `.dev/releases/current/<spec-name>/` | Output directory |
| `--depth` | `-d` | No | `standard` | Analysis depth: quick, standard, deep. Maps to sc:adversarial --depth when adversarial modes active |
| `--multi-roadmap` | | No | `false` | Enable multi-roadmap adversarial generation |
| `--agents` | `-a` | With --multi-roadmap | - | Agent specs: `model[:persona[:"instruction"]]`. If persona omitted, uses auto-detected primary persona. Examples: `opus,sonnet,gpt52` or `opus:architect,sonnet:security` |
| `--interactive` | `-i` | No | `false` | User approval at adversarial decision points |
| `--validate` | `-v` | No | `true` | Enable multi-agent validation (Wave 4) |
| `--no-validate` | | No | `false` | Skip validation. Sets `validation_status: SKIPPED` and `validation_score: 0.0` in frontmatter |
| `--compliance` | `-c` | No | Auto-detect | Force compliance tier: strict, standard, light |
| `--persona` | `-p` | No | Auto-select | Override primary persona |
| `--dry-run` | | No | `false` | Execute Waves 0-2, skip Waves 3-4, output structured preview to console. No files written, no session persistence |

**Agent spec format**: `model[:persona[:"instruction"]]` — model is required; persona and instruction are optional. Split on `,` for agent list, then `:` per agent (max 3 segments). Agent count: 2-10.

## 4. Wave Architecture

> **Verb → Tool Mapping**: "Invoke Skill" = `Skill` tool (valid from both command context AND skill context per D-0001 reversal). "Dispatch Task agent" = `Task` tool (used for parallelization, not for skill invocation). "Load ref" = Read tool. Never use bare "Invoke" without a tool binding.

sc:roadmap executes in 5 waves (0-4). Each wave has entry criteria, behavioral instructions, and exit criteria. Refs are loaded **on-demand per wave** to prevent context bloat.

### Wave 0: Prerequisites

**Purpose**: Validate environment before main workflow.

**Entry Criteria**: Specification file path provided, Claude Code session active.

**Behavioral Instructions**:
1. Validate all spec file(s) exist and are readable (Read tool). Edge cases: if file is empty (0 bytes), abort with `"Specification file is empty. Provide a non-empty spec."`. If file has <5 lines, warn but proceed.
2. Validate output directory is writable; create if needed
3. **Output collision check**: If output directory already contains roadmap artifacts (roadmap.md, extraction.md, test-strategy.md), append `-N` suffix to all output filenames (e.g., `roadmap-2.md`). Increment until no collision.
4. Check template directory availability (4-tier: local → user → plugin → inline generation)
5. If `--specs` or `--multi-roadmap` flags present: verify `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` exists. If not, abort: `"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags. Install via: superclaude install"`
6. If `--multi-roadmap`: validate all model identifiers in `--agents` are recognized. Abort on unknown models.
7. Log all fallback decisions

**Exit Criteria**: All prerequisites validated. Trigger `sc:save` with current session state. Emit: `"Wave 0 complete: prerequisites validated."`

### Wave 1A: Spec Consolidation (conditional)

**Trigger**: Only when `--specs` flag is present.

**Refs Loaded**: Read `refs/adversarial-integration.md` and follow the invocation patterns for multi-spec mode.

**Behavioral Instructions**:
1. Parse agent specs (if combined mode) using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section
2. Invoke `sc:adversarial-protocol` directly for multi-spec consolidation:
   - **2a**: Build adversarial invocation arguments: `--compare <spec-list>` (comma-separated), propagate `--interactive` if set, propagate `--depth` mapping per Wave 0 decision
   - **2b**: Invoke: `Skill sc:adversarial-protocol` with arguments built in 2a
   - **2c**: Read return contract inline from Skill response. If response is empty or unparseable, use fallback `convergence_score: 0.5`
   - **2d**: Parse return contract fields from inline Skill response (no file read required)
   - **2e**: Route per return contract `status` field and `convergence_score`:
     - `status: success` → proceed with `merged_output_path` as spec input for Wave 1B
     - `status: partial` + score ≥ 0.6 → proceed with warning logged in extraction.md
     - `status: partial` + score < 0.6 → if `--interactive`, prompt user; otherwise abort
     - `status: failed` → abort roadmap generation
   - **2f**: Apply divergent-specs heuristic: if `convergence_score` < 0.5 → emit warning to user

**Error propagation (combined mode)**: If Wave 1A fails (status: failed or aborted), do NOT proceed to Wave 2's multi-roadmap generation. Abort entirely — no partial combined mode.

**Exit Criteria**: Unified spec available. Trigger `sc:save` with adversarial results. Emit: `"Wave 1A complete: spec consolidation finished (convergence: XX%)."`

### Wave 1B: Detection & Analysis

**Refs Loaded**: Read `refs/extraction-pipeline.md` and apply the 8-step extraction pipeline. Read `refs/scoring.md` and apply the complexity scoring formula.

**Behavioral Instructions**:
1. Parse specification file (single spec or unified spec from Wave 1A). If spec contains YAML frontmatter, validate it parses correctly. If malformed YAML, abort with `"Invalid YAML frontmatter in spec at line <N>: <parse error>. Fix the YAML syntax and retry."`
2. If spec exceeds 500 lines: activate chunked extraction protocol from `refs/extraction-pipeline.md`
3. Run the 8-step extraction pipeline from `refs/extraction-pipeline.md`
4. **Write extraction.md** to output directory immediately (enables resumability, provides early user value)
5. Score complexity using the 5-factor formula from `refs/scoring.md`
6. Classify domains using the domain keyword dictionaries from `refs/extraction-pipeline.md`
7. Activate personas based on domain distribution thresholds from `refs/scoring.md`
8. If `--persona` flag provided, override auto-detected primary persona
9. If `--interactive`: display auto-detected persona with confidence score, prompt user to confirm or override. If not `--interactive`: use auto-detected persona silently
10. Edge case: if extraction produces 0 actionable requirements, abort with `"No actionable requirements found in specification. Verify the spec contains functional or non-functional requirements."`

**Exit Criteria**: extraction.md written, complexity scored, personas activated. Trigger `sc:save` with extraction results. Emit: `"Wave 1B complete: extraction finished (XX requirements, complexity: X.XX). extraction.md written."`

### Wave 2: Planning & Template Selection

**Refs Loaded**: Read `refs/templates.md` for template discovery and milestone structure. If `--multi-roadmap`, also read `refs/adversarial-integration.md`.

**Behavioral Instructions**:
1. Run 4-tier template discovery from `refs/templates.md`: local → user → plugin [future: v5.0] → inline generation
2. Score template compatibility using the algorithm from `refs/scoring.md`. If `--interactive`: display compatibility scores for all candidate templates, prompt user to confirm or select. If not `--interactive`: use highest-scoring template silently
3. If `--multi-roadmap`: execute the SKILL-DIRECT adversarial invocation protocol (sub-steps 3a–3f):
   - **3a**: Parse agent specs from `--agents` flag using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Output: agent list with model, persona, instruction per agent.
   - **3b**: Expand model-only agent specs: apply the primary persona auto-detected in Wave 1B to any agent spec that has no explicit persona. Output: fully-specified variant configurations.
   - **3c**: If `agent_count >= 3`: add `debate-orchestrator` agent to coordinate debate rounds and prevent combinatorial explosion. Threshold: 3 (not 5). Output: final agent list with optional orchestrator.
   - **3d**: Invoke `sc:adversarial-protocol` directly via Skill tool:
     - Build arguments: `--source <unified-spec> --generate roadmap --agents <expanded-agent-list>`, propagate `--depth` and `--interactive`
     - Invoke: `Skill sc:adversarial-protocol` with the above arguments
     - sc:adversarial-protocol executes F1 (variant generation) → F2/3 (diff + debate) → F4/5 (base selection + merge)
     - Output: structured return contract returned inline as Skill response
   - **3e**: Consume return contract (inline Skill return value):
     - **Empty/malformed response guard**: If Skill response is empty or unparseable → use fallback `convergence_score: 0.5` (Partial path by design)
     - **3-status routing**:
       - IF `convergence_score >= 0.6` → PASS: use `merged_output_path` as roadmap source; the adversarial output replaces template-based generation
       - ELIF `convergence_score >= 0.5` → PARTIAL: use `merged_output_path` with warning in roadmap.md frontmatter (`adversarial_status: partial`)
       - ELSE (`convergence_score < 0.5`) → FAIL: abort with `"Adversarial pipeline failed (convergence: X.XX). Cannot produce reliable roadmap from divergent variants."`
   - **3f**: SKILL-DIRECT is the primary path. The adversarial output from 3d is the roadmap source. No secondary template fallback applies; if 3d/3e return FAIL, abort roadmap generation entirely.
4. Otherwise: create milestone structure based on complexity class and domain distribution using the milestone count formula, domain mapping, and priority assignment rules from `refs/templates.md`
5. Map dependencies between milestones using the dependency mapping rules from `refs/templates.md`. Validate the dependency graph is acyclic (DAG). If circular dependency detected, abort with `"Circular dependency detected in milestone plan: M<X> → M<Y> → ... → M<X>. Review milestone dependencies."`
6. Compute effort estimates for each milestone using the effort estimation algorithm from `refs/templates.md`
7. Record template selection decision in Decision Summary (template name or "inline", compatibility scores, rationale)

**Exit Criteria**: Milestone structure with effort estimates determined. Trigger `sc:save` with milestone structure. Emit: `"Wave 2 complete: N milestones planned."` If `--dry-run`: output structured console preview (FR-018 format — spec info, complexity, persona, template, milestone structure with dependencies, domain distribution, estimated deliverables/risks, output paths) and STOP. Skip Waves 3-4. No files written, no session persistence.

### Wave 3: Generation

**Skip condition**: If `--dry-run`, this wave is skipped entirely (preview was output at end of Wave 2).

**Refs Loaded**: None (uses context already loaded from Waves 1B and 2). The body templates and frontmatter schemas are in `refs/templates.md` (loaded in Wave 2).

**Behavioral Instructions**:
1. **Step 1**: Generate `roadmap.md` using the YAML frontmatter schema from `refs/templates.md` "roadmap.md Frontmatter" section + body from `refs/templates.md` "roadmap.md Body Template" section. Required body sections: Overview, Milestone Summary table (with Effort column), Dependency Graph, per-milestone details (Objective, Deliverables, Dependencies, Risk Assessment), Risk Register, Decision Summary, Success Criteria. Apply effort estimation algorithm from `refs/templates.md` "Effort Estimation" section.
2. **Step 2** (after roadmap.md is complete): Generate `test-strategy.md` using the YAML frontmatter schema from `refs/templates.md` "test-strategy.md Frontmatter" section + body from `refs/templates.md` "test-strategy.md Body Template" section:
   - Compute interleave ratio from complexity class (LOW→1:3, MEDIUM→1:2, HIGH→1:1)
   - Reference concrete milestone names from the just-generated roadmap.md
   - Encode continuous parallel validation philosophy
   - Define stop-and-fix thresholds per severity level
3. **Step 3**: Generate `extraction.md` YAML frontmatter using the schema from `refs/templates.md` "extraction.md Frontmatter" section (body was written in Wave 1B; this step adds/updates frontmatter only)
4. **Sequencing constraint**: roadmap.md MUST be fully generated before test-strategy.md begins (test-strategy.md references specific milestone IDs)

**Frontmatter rules** (enforced across all 3 artifacts):
- Single-spec: use `spec_source: <path>` (never `spec_sources`)
- Multi-spec: use `spec_sources: [<path1>, <path2>]` (never `spec_source`)
- Exactly one of these fields present, never both, never neither

**Exit Criteria**: roadmap.md + test-strategy.md written, extraction.md frontmatter updated. Trigger `sc:save` with generation state. Emit: `"Wave 3 complete: roadmap.md + test-strategy.md generated."`

### Wave 4: Validation (Multi-Agent)

**Skip condition**: If `--dry-run`, this wave is skipped entirely. If `--no-validate`, skip per step 8 below.

**Refs Loaded**: Read `refs/validation.md` for agent prompts and scoring thresholds.

**Behavioral Instructions**:
1. Dispatch quality-engineer agent using the prompt from `refs/validation.md`: completeness, consistency, traceability checks. Additionally validates test-strategy.md against interleave ratio, milestone references, and stop-and-fix thresholds.
2. Dispatch self-review agent using the 4-question protocol from `refs/validation.md`
3. Both agents run in **parallel** (independent read-only validators)
4. Aggregate scores using the formula from `refs/validation.md` "Score Aggregation" section: quality-engineer (0.55) + self-review (0.45). Apply thresholds from `refs/validation.md` "Decision Thresholds" section: PASS (>=85%) | REVISE (70-84%) | REJECT (<70%)
5. If adversarial mode was used: missing adversarial artifacts → REJECT; missing convergence score → REVISE
6. Write validation score to roadmap.md frontmatter
7. **REVISE loop** (per FR-017): If 70-84%, follow the REVISE loop protocol from `refs/validation.md` "REVISE Loop" section: collect improvement recommendations from both agents, re-run Wave 3 → Wave 4 with recommendations as input. Max 2 iterations. If still REVISE after iteration 2: set `validation_status: PASS_WITH_WARNINGS`
8. If `--no-validate`: skip entirely per `refs/validation.md` "No-Validate Behavior" section. Set `validation_status: SKIPPED` and `validation_score: 0.0`. No agents are dispatched. Emit: `"Wave 4 skipped: --no-validate flag set."`

**Exit Criteria**: Validation complete. Trigger `sc:save` with validation results (final). Emit: `"Wave 4 complete: validation score X.XX (STATUS)."` (or skip message if `--no-validate`)

### Post-Wave: Completion

After Wave 4, perform completion steps:
1. Verify all 3 artifacts exist and are non-empty
2. Persist session state to Serena memory (key: `sc-roadmap:<spec-name>:<timestamp>`)
3. If Serena unavailable: write to `<output_dir>/.session-memory.md` as fallback
4. Trigger `sc:save` for cross-session resumability
5. Emit final output summary with artifact locations and next steps
6. **Final message** (per FR-008): State artifacts written, recommend user review before proceeding. No references to downstream commands.

### Ref Loading Summary

| Wave | Refs Loaded | Max Loaded |
|------|------------|------------|
| Wave 0 | None | 0 |
| Wave 1A | `refs/adversarial-integration.md` (if `--specs`) | 1 |
| Wave 1B | `refs/extraction-pipeline.md` + `refs/scoring.md` | 2 |
| Wave 2 | `refs/templates.md` (+ `refs/adversarial-integration.md` if `--multi-roadmap`) | 1-2 |
| Wave 3 | None (uses already-loaded context) | 0 |
| Wave 4 | `refs/validation.md` | 1 |

## 5. Adversarial Modes

sc:roadmap supports three adversarial modes via sc:adversarial integration. Full invocation patterns, return contract handling, and error routing are documented in `refs/adversarial-integration.md`.

### Mode Detection

| Mode | Trigger | Wave |
|------|---------|------|
| Multi-spec consolidation | `--specs spec1.md,spec2.md,...` | Wave 1A |
| Multi-roadmap generation | `--multi-roadmap --agents ...` | Wave 2 |
| Combined | Both flags together | Wave 1A then Wave 2 |

### Multi-Spec Flow
`--specs` → Wave 0 validates all files → Wave 1A invokes `Skill sc:adversarial-protocol` with `--compare` → unified spec → Wave 1B extracts from unified spec → Waves 2-4 standard

### Multi-Roadmap Flow
`--multi-roadmap --agents` → Waves 0-1B standard → Wave 2 expands model-only agents with auto-detected persona → invokes `Skill sc:adversarial-protocol` with `--source --generate roadmap --agents` → unified roadmap → Waves 3-4 validate

### Combined Flow
Both flags → Wave 1A consolidates specs → Wave 1B extracts → Wave 2 generates competing roadmaps → Waves 3-4 validate. Combined mode reports both adversarial pass completions: Wave 1A emits consolidation progress, Wave 2 emits multi-roadmap progress. If Wave 1A fails, Wave 2 is not attempted (error propagation — see Wave 1A exit criteria).

### Agent Count Rules
- Range: 2-10 agents
- With >= 3 agents: add orchestrator agent to coordinate debate rounds and prevent combinatorial explosion

### Depth Mapping
`--depth quick` → 1 debate round | `--depth standard` → 2 rounds | `--depth deep` → 3 rounds

## 6. Output Artifacts

### Artifact Table

| Artifact | Location | Content | Consumed By |
|----------|----------|---------|-------------|
| `roadmap.md` | `<output>/roadmap.md` | YAML frontmatter + milestones, dependencies, risk register, decision summary | User review, future tasklist generator |
| `extraction.md` | `<output>/extraction.md` | YAML frontmatter + extracted requirements, domain analysis, complexity scoring | Roadmap generation (internal), user reference |
| `test-strategy.md` | `<output>/test-strategy.md` | YAML frontmatter + continuous parallel validation philosophy | Future tasklist generator (validation milestones) |

### Frontmatter Schemas

All frontmatter follows the schemas defined in spec Section FR-002. Key rules:
- Exactly one of `spec_source` (scalar) or `spec_sources` (list) — never both
- `adversarial` block present only when adversarial mode was used
- `validation_score` and `validation_status` always present (SKIPPED if `--no-validate`)
- All fields documented with types; fields may be added but never removed (contract stability)

### ID Schema

| Entity | Format | Example |
|--------|--------|---------|
| Milestones | `M{digit}` | M1, M2, M9 |
| Deliverables | `D{milestone}.{seq}` | D1.1, D2.3 |
| Tasks | `T{milestone}.{seq}` | T1.1, T3.2 |
| Risks | `R-{3digits}` | R-001, R-012 |
| Dependencies | `DEP-{3digits}` | DEP-001 |
| Success Criteria | `SC-{3digits}` | SC-001 |

## 7. MCP Integration

| Server | Usage | Waves |
|--------|-------|-------|
| Sequential | Wave analysis, validation reasoning, complexity assessment | 1-4 |
| Context7 | Template patterns, domain best practices, framework documentation | 1-2 |
| Serena | Session persistence, memory, cross-session state | 0, 4, completion |

**Circuit Breaker Fallbacks**:
- Sequential unavailable → native Claude reasoning with reduced analysis depth
- Context7 unavailable → WebSearch for documentation, note limitations
- Serena unavailable → proceed without persistence, write to `<output_dir>/.session-memory.md`

### Session Persistence & Resumability

sc:roadmap triggers `sc:save` at each wave boundary for cross-session resumability.

**Save points**: After each wave completion, persist session state to Serena memory using key `sc-roadmap:<spec-name>:<timestamp>`. State accumulates progressively:
- After Wave 0: spec paths, output dir, flags, collision suffix
- After Wave 1A: adversarial results (unified spec path, convergence score)
- After Wave 1B: extraction results, complexity score, persona selection
- After Wave 2: template selection, milestone structure, dependency graph
- After Wave 3: generation state (roadmap.md, test-strategy.md written)
- After Wave 4: validation results (final)

**Session schema** (`roadmap_session`): `spec_source`, `output_dir`, `flags`, `last_completed_wave` (0|1A|1B|2|3|4), `extraction_complete`, `complexity_score`, `primary_persona`, `template_selected`, `milestone_count`, `adversarial_results`, `validation_score`, plus spec file hash for mismatch detection.

**Resume protocol**: When sc:roadmap is invoked and Serena memory contains a matching session (same `spec_source` + `output_dir`):
1. Prompt user: `"Found incomplete roadmap session (last completed: Wave X). Resume? [Y/n]"`
2. If yes: validate spec file hash — if mismatch, warn `"Spec file has changed since last session. Starting fresh to avoid stale extraction."` and start fresh (existing artifacts get `-N` suffix per collision protocol)
3. If yes and hash matches: skip to wave after `last_completed_wave`, reload artifacts from disk
4. If no: start fresh (existing artifacts get `-N` suffix per collision protocol)

**Graceful degradation**: If Serena unavailable, proceed without persistence and write session state to `<output_dir>/.session-memory.md` as fallback. Warn user that cross-session resume is unavailable.

## 8. Boundaries

### Will Do
- Generate structured roadmaps from specification files (single or multiple)
- Invoke `Skill sc:adversarial-protocol` for multi-spec consolidation and multi-roadmap generation
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

## Return Contract

sc:roadmap produces no machine-readable return contract file (it is a terminal command, not a sub-agent). When sc:roadmap invokes sc:adversarial-protocol via direct Skill invocation (SKILL-DIRECT), the return contract is received as the **inline return value** of the Skill call — not a file on disk.

**Return contract transport**: Inline Skill response (structured data returned directly by `sc:adversarial-protocol` upon completion).

**Fields consumed by sc:roadmap** (from sc:adversarial-protocol inline return value):

| Field | Type | Used In | Action |
|-------|------|---------|--------|
| `status` | `success\|partial\|failed` | Wave 1A Step 2e, Wave 2 Step 3e | Primary routing decision |
| `convergence_score` | `float 0.0-1.0` | Wave 1A Step 2e, Wave 2 Step 3e | Secondary routing threshold (≥0.6 PASS, ≥0.5 PARTIAL, <0.5 FAIL) |
| `merged_output_path` | `path\|null` | Wave 1A Step 2e, Wave 2 Step 3e | Path to consolidated spec or roadmap |
| `fallback_mode` | `bool` | Wave 1A, Wave 2 logging | Logged in extraction.md |
| `invocation_method` | `enum` | Wave 1A, Wave 2 logging | Logged for observability |
| `unresolved_conflicts` | `list[string]` | Wave 1A, Wave 2 | Listed in roadmap.md decision summary if non-empty |

**Consumer defaults** (if field absent):
```yaml
convergence_score: 0.5    # Forces Partial path
status: "failed"          # Triggers abort
merged_output_path: null  # No output available
```

## Agent Delegation

sc:roadmap-protocol delegates to sc:adversarial-protocol via direct Skill invocation (SKILL-DIRECT per D-0001 reversal):

| Delegation Point | Target Skill | Invocation Method | Output Contract |
|-----------------|--------------|-------------------|-----------------|
| Wave 1A Step 2 (multi-spec) | sc:adversarial-protocol | `Invoke Skill sc:adversarial-protocol --compare <specs>` | Inline Skill return value |
| Wave 2 Step 3d (multi-roadmap) | sc:adversarial-protocol | `Invoke Skill sc:adversarial-protocol --source <spec> --generate roadmap --agents <list>` | Inline Skill return value |

**SKILL-DIRECT**: Direct `Skill` tool invocation is the primary method. Skill-to-skill invocation is confirmed available (AVAILABLE per D-0001 reversal). No Task agent wrapper required.

## Error Handling

| Error Condition | Wave | Detection | Action |
|----------------|------|-----------|--------|
| Spec file not found | Wave 0 | File read fails | Abort: `"Spec file not found: <path>"` |
| sc:adversarial-protocol not installed | Wave 0 Step 5 | SKILL.md missing | Abort: `"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags."` |
| Skill response empty or unparseable | Wave 1A Step 2c, Wave 2 Step 3e | Inline return parse fails | Use fallback `convergence_score: 0.5` (Partial path) |
| Skill sc:adversarial-protocol invocation fails (tool error) | Wave 1A Step 2b, Wave 2 Step 3d | Skill tool returns error | Abort: `"sc:adversarial-protocol Skill invocation failed. Adversarial pipeline aborted."` |
| convergence_score < 0.5 | Wave 1A Step 2e, Wave 2 Step 3e | Score comparison | Abort: `"Adversarial pipeline failed (convergence: X.XX)"` |
| Template not found | Wave 3 | File read fails | Use generic template; log warning |
| Output directory not writable | Wave 0/3 | Write fails | Abort: `"Cannot write to output directory: <path>"` |

## 9. Compliance

**Default tier**: STANDARD with automatic escalation to STRICT when:
- Complexity score > 0.8
- Security-related requirements detected
- Multi-domain scope (>3 domains)
- User specifies `--compliance strict`

**Compliance interaction with validation**: STRICT tier requires Wave 4 validation to pass (>=85%). STANDARD allows manual review.

---

*Skill definition for SuperClaude Framework v4.2.0+ — based on SC-ROADMAP-V2-SPEC.md v2.0.0*
