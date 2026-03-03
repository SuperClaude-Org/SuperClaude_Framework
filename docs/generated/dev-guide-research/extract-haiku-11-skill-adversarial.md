# Extraction — Developing Custom Skills Pattern (sc-adversarial)

**Sources (read completely):**
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/SKILL.md`
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/refs/agent-specs.md`
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/refs/scoring-protocol.md`

This extraction captures **all information in the above sources that pertains to developing custom skills** for the SuperClaude framework, using `/sc:adversarial` as the worked example. It is organized as a **reusable pattern**: what a skill definition must contain, how it specifies I/O contracts, how it delegates to agents, and how it documents deterministic + LLM-driven evaluation protocols.

---

## 1) Skill file: required structure (frontmatter + body)

### 1.1 YAML frontmatter (parsed metadata)

From `/src/superclaude/skills/sc-adversarial/SKILL.md`, the skill begins with YAML frontmatter that defines the command’s identity and tool access:

```yaml
---
name: sc:adversarial
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**Reusable pattern:**
- Every custom skill should start with `---` frontmatter containing at least:
  - `name:` (slash command name)
  - `description:` (short, user-facing summary)
  - `allowed-tools:` (explicit tool allowlist)

### 1.2 Extended metadata comment (documentation-only)

The skill also includes an *unparsed* metadata block for humans/docs:

> `<!-- Extended metadata (for documentation, not parsed):`

Example (verbatim):

```md
<!-- Extended metadata (for documentation, not parsed):
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
-->
```

**Reusable pattern:**
- Use an HTML comment to store extended descriptors (category, complexity, MCP servers, personas). Treat as documentation only.

---

## 2) Define what the skill does (purpose + constraints)

A skill should clearly declare its scope, why it exists, and what it will/won’t do.

### 2.1 Purpose and “Core Objective”

From `SKILL.md`:
- Purpose statement explains the command is a reusable pipeline.
- It explicitly calls out a correctness goal and anti-hallucination goal.

Key quotes:
- > “Generic, reusable command implementing a structured adversarial debate, comparison, and merge pipeline.”
- > “**Core Objective**: Verify and validate accuracy of statements in generated artifacts, weeding out hallucinations and sycophantic agreement through structured adversarial pressure using steelman debate strategy.”

**Reusable pattern:**
- Put a short Purpose section near the top.
- If the skill is designed as a framework primitive, explicitly state that (e.g., “invocable by any SuperClaude command”).

### 2.2 Boundaries: “Will Do” / “Will Not Do”

From `SKILL.md` (verbatim headings and examples):

```md
### Will Do
- Compare 2-10 artifacts through structured adversarial debate
...

### Will Not Do
- Validate domain-specific correctness of merged output (calling command's responsibility)
- Execute the merged output (planning tool, not execution tool)
- Manage git operations or version control
...
```

**Reusable pattern:**
- Include explicit boundaries to prevent scope creep.
- If correctness validation is delegated to the caller, say so.

---

## 3) Input contract patterns (modes + flags + validation)

### 3.1 Mandatory input mode gating

From `SKILL.md`:

> “**MANDATORY**: Either `--compare` (Mode A) or `--source`+`--generate`+`--agents` (Mode B) must be provided.”

The skill documents both syntaxes:

```text
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]
/sc:adversarial --source <file> --generate <type> --agents <spec>[,...] [options]
```

**Reusable pattern:**
- If a skill supports multiple input modes, enforce mutual exclusivity and document it early.

### 3.2 Dual input mode pattern (Mode A vs Mode B)

From `SKILL.md`:
- **Mode A: Compare Existing Files (FR-001)**
  - Accepts “2-10 existing files”
  - Copies them into a standardized output structure
- **Mode B: Generate + Compare from Source (FR-001)**
  - Generates variants from a source using multiple “agent specs”
  - Agent spec format: `"<model>[:persona[:\"instruction\"]]"`

Quote:
- > “Agent count: 2-10 (minimum 2 required for adversarial comparison)”

**Reusable pattern:**
- Provide both user-facing usage examples and hard constraints (min/max counts).
- If you generate derived artifacts, define deterministic naming and output paths.

### 3.3 Common flag documentation (configurable parameters)

`SKILL.md` documents a stable “Configurable Parameters” table:

```md
| Parameter | Flag | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Depth | `--depth` | `standard` | quick/standard/deep | Controls debate rounds (1/2/3) |
| Convergence | `--convergence` | `0.80` | 0.50-0.99 | Alignment threshold for deep mode |
| Interactive | `--interactive` | `false` | true/false | User approval at decision points |
| Output dir | `--output` | Auto-derived | Any path | Where artifacts are written |
| Focus areas | `--focus` | All | Comma-separated | Debate focus areas |
```

**Reusable pattern:**
- Document flags as a table: flag, default, range, and effect.

### 3.4 Input parsing protocol (stop/warn rules + error messages)

The skill includes a **verifiable parsing contract** expressed in YAML. This is a reusable documentation pattern for custom skills.

Example (verbatim excerpts):

```yaml
input_mode_parsing:
  step_1_detect_mode:
    mode_a_signal: "--compare flag present"
    mode_b_signal: "--source AND --generate AND --agents flags present"
    conflict: "If both Mode A and Mode B flags present → STOP with error: 'Cannot use --compare with --source/--generate/--agents'"
    neither: "If neither mode detected → STOP with error: 'Must provide --compare (Mode A) or --source + --generate + --agents (Mode B)'"
```

Mode A validation includes explicit STOP messages:

```yaml
  step_2_mode_a_parsing:
    validation:
      count_check: "2 ≤ file_count ≤ 10; reject with error if outside range"
      existence_check: "For each path, verify file exists and is readable"
    error_messages:
      too_few: "STOP: 'Adversarial comparison requires at least 2 files, got <N>'"
      too_many: "STOP: 'Maximum 10 files supported, got <N>'"
      missing_file: "STOP: 'File not found: <path>'"
```

Mode B validation includes STOP for unknown model and missing quotes:

```yaml
  step_3_mode_b_parsing:
    agent_spec_parsing:
      error_messages:
        invalid_model: "STOP: 'Unknown model: <model>'"
        invalid_persona: "WARN: 'Unknown persona <persona>, using model defaults'"
        missing_quotes: "STOP: 'Instruction must be quoted: <spec>'"
```

**Reusable pattern:**
- Document parsing as a structured YAML “protocol” with:
  - detection logic
  - validation rules
  - explicit STOP vs WARN cases
  - user-facing error messages

---

## 4) Output contract patterns (artifact trees + naming)

### 4.1 Standardized artifact directory layout

From `SKILL.md`:

```text
<output-dir>/
├── <merged-output>.md              # Final unified artifact
└── adversarial/
    ├── variant-1-<agent>.md        # Variant 1
    ├── variant-2-<agent>.md        # Variant 2
    ├── ...                         # Up to 10 variants
    ├── diff-analysis.md            # Step 1 output
    ├── debate-transcript.md        # Step 2 output
    ├── base-selection.md           # Step 3 output
    ├── refactor-plan.md            # Step 4 output
    └── merge-log.md                # Step 5 execution log
```

Naming conventions are also explicitly spelled out:
- > “Mode A: `variant-N-original.md` (copies of input files)”
- > “Mode B: `variant-N-<model>-<persona>.md`”

**Reusable pattern:**
- Define an “artifact output structure” section for the skill.
- Use deterministic paths and filenames so other commands can integrate reliably.

### 4.2 Return contract for programmatic integration

From `SKILL.md`:

```yaml
return_contract:
  merged_output_path: "<path to merged file>"
  convergence_score: "<final convergence percentage>"
  artifacts_dir: "<path to adversarial/ directory>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list of unresolved items>"]
```

Later in `SKILL.md`, the return contract is described with types and status determination:

```yaml
return_contract:
  fields:
    merged_output_path:
      type: "string"
      content: "Absolute or relative path to the merged output file"
    convergence_score:
      type: "float"
      content: "Final convergence percentage from debate (0.0-1.0)"
    status:
      type: "enum"
      values:
        success: "All 5 steps completed, post-merge validation passed"
        partial: "Pipeline completed but with warnings or validation failures"
        failed: "Pipeline aborted — check artifacts for recovery"
```

**Reusable pattern:**
- If the skill is meant to be a framework primitive, define a return contract that other commands can consume.

---

## 5) Delegation patterns: specialist agents as skill subcomponents

A key SuperClaude custom skill pattern in these sources is **delegating sub-steps to named agents**, each with explicit responsibilities and tool constraints.

### 5.1 Define dedicated agents and forbid role overlap

From `SKILL.md`:

**debate-orchestrator** (verbatim):
- > “Coordinates the entire pipeline without participating in debates”
- > “Does NOT: Generate variants, participate in debates, execute merges”

**merge-executor** (verbatim):
- > “Executes refactoring plans to produce unified merged artifacts”
- > “Does NOT: Make strategic decisions, override plan, participate in debates”

**Reusable pattern:**
- In skill docs, define sub-agents and their “Does / Does NOT” boundaries to avoid conflating responsibilities.

### 5.2 Task-based advocate instantiation (dynamic agents)

From `/refs/agent-specs.md`:
- > “Advocate agents are NOT pre-defined. They are instantiated dynamically from the `--agents` specification for each adversarial debate session.”

From `SKILL.md` Step 2:
- > “advocate_instantiation: Parse model[:persona[:\"instruction\"]] spec for each variant”
- > “Parallel Task calls — all advocates run simultaneously”

**Reusable pattern:**
- Skills can create *dynamic agents* per run, based on CLI flags.
- When parallel work is safe, specify “true parallel” dispatch.

---

## 6) Agent specification format (reusable mini-language)

`/refs/agent-specs.md` defines an agent spec mini-language used by the skill.

### 6.1 Agent spec string format

Verbatim:

```text
<model>                              # Model only
<model>:<persona>                    # Model + persona
<model>:<persona>:"<instruction>"    # Model + persona + custom instruction
```

### 6.2 Supported models + personas (and what they imply)

Models table (verbatim rows):
- `opus` “Highest capability”
- `sonnet` “Balanced capability”
- `haiku` “Fast, efficient”

Personas map to the SuperClaude persona system:

```text
architect, security, analyzer, frontend, backend, performance, qa, scribe
```

The file also states:
- > “Model aliases configured in the environment are also supported.”

**Reusable pattern:**
- If your skill takes agent parameters, define:
  - the grammar
  - the allowed values (including environment aliases)
  - the semantic intent (“persona shapes behavior”)

### 6.3 Parsing/validation rules (STOP vs WARN)

From `/refs/agent-specs.md`:

```yaml
agent_spec_parsing:
  separator: ":"
  instruction_delimiter: '"' (double quotes)
  validation:
    - "Model must be a recognized model name or alias"
    - "Persona must match a valid SuperClaude persona (if provided)"
    - "Instruction must be enclosed in double quotes (if provided)"
  error_handling:
    invalid_model: "STOP with error: 'Unknown model: <model>'"
    invalid_persona: "WARN: Unknown persona '<persona>', using model defaults"
    missing_quotes: "STOP with error: 'Instruction must be quoted: <spec>'"
```

**Reusable pattern:**
- Explicitly document error-handling behavior for malformed agent specs.

---

## 7) Advocate debate behavior as a skill component (steelman + evidence)

### 7.1 Advocate role contract

From `/refs/agent-specs.md`:

> “Each advocate: 1. **Receives**: Their variant + all other variants + diff-analysis.md 2. **Argues for**… 3. **Critiques**… 4. **Responds**…”

### 7.2 Steelman protocol (mandatory)

From `/refs/agent-specs.md` (verbatim YAML):

```yaml
steelman_protocol:
  before_critiquing:
    action: "Construct the strongest possible version of opposing positions"
    purpose: "Demonstrate understanding before disagreement"
    format: |
      ## Steelman: Variant [X]
      The strongest argument for Variant X's approach is: [steelman]
      This addresses: [what it gets right]
      However, I believe Variant [mine] improves upon this because: [critique]

  evidence_requirement:
    - "Every strength claim must cite specific section/content from the variant"
    - "Every weakness claim must cite specific evidence or absence of evidence"
    - "Speculative claims must be labeled as such"
```

**Reusable pattern:**
- If your skill needs adversarial or evaluative behavior, specify:
  - a mandatory “steelman” step
  - evidence requirements
  - a concrete output format

### 7.3 Advocate prompt template and required output format

From `/refs/agent-specs.md` (prompt template):

```yaml
advocate_prompt_template:
  system_context: |
    You are an advocate agent in a structured adversarial debate.
    Your variant: [variant name]
    Model: [model]
    Persona: [persona or 'default']
    Custom instruction: [instruction or 'none']

    RULES:
    1. Argue for your variant's strengths with evidence
    2. STEELMAN opposing variants before critiquing them
    3. Cite specific sections, quotes, or content as evidence
    4. Acknowledge genuine weaknesses in your variant honestly
    5. Focus on these areas: [focus areas from --focus flag]
```

Output format (verbatim):

```markdown
## Advocate: [Variant Name] ([agent-spec])

### Position Summary
[1-3 sentence summary of overall argument]

### Steelman: [Other Variant Name]
[Strongest version of opposing argument before critique]

### Key Strengths Claimed
1. [Strength with evidence citation]
2. [Strength with evidence citation]

### Weaknesses in [Other Variant]
1. [Critique with evidence citation]

### Concessions
- [Any genuine weaknesses acknowledged in own variant]
```

**Reusable pattern:**
- When delegating to Task agents, embed a strict template in the skill spec so outputs are parseable and consistent.

---

## 8) Stepwise pipeline pattern (sequential steps + artifacts)

The skill defines a “5-Step Adversarial Protocol (FR-002)” where each step has:
- inputs
- delegation/agent responsible
- process as structured YAML
- output artifact name + template reference

Quote:
- > “The core pipeline executes 5 sequential steps. Each step produces a documented artifact.”

### 8.1 Step YAML is used as “implementation spec”

Example snippet (Step 1 diff analysis):

```yaml
diff_analysis:
  structural_diff:
    action: "Compare section ordering, hierarchy depth, heading structure across variants"
    output: "Structural differences with severity ratings (Low/Medium/High)"
  content_diff:
    action: "Compare approaches topic-by-topic, identify coverage differences"
  contradiction_detection:
    action: "Structured scan per contradiction detection protocol"
  unique_contribution_extraction:
    action: "Identify ideas present in only one variant"
```

**Reusable pattern:**
- Write each step as a protocol object (YAML) that can serve as an executable blueprint for implementation.

---

## 9) Error handling as a documented matrix (skill-level resiliency)

A custom skill should include an explicit error-handling matrix.

From `SKILL.md`:

```yaml
error_handling:
  agent_failure:
    behavior: "Retry once, then proceed with N-1 variants"
    constraint: "Minimum 2 variants required"
    fallback: "If only 1 variant survives, abort and return it with warning"

  variants_too_similar:
    threshold: "<10% diff"
    behavior: "Skip debate, select either as base"

  no_convergence:
    behavior: "Force-select by score, document non-convergence"

  merge_failure:
    behavior: "Preserve all artifacts, flag failure"
    recovery: "Provide refactor-plan.md for manual execution"
```

**Reusable pattern:**
- Declare failures, detection conditions, and recovery behavior.
- Include minimum viability constraints (e.g., “Minimum 2 variants required”).

---

## 10) Hybrid scoring protocols as a reusable “anti-hallucination” pattern

The `/refs/scoring-protocol.md` provides a full scoring algorithm that is applicable to other skills that need base selection or evaluation.

### 10.1 Deterministic quantitative layer (no LLM judgment)

Verbatim:
- > “All quantitative metrics are computed deterministically from artifact text. No LLM judgment is involved in this layer.”

Metrics table and formula (verbatim):

```text
quant_score = (RC × 0.30) + (IC × 0.25) + (SR × 0.15) + (DC × 0.15) + (SC × 0.15)
```

And the metric definitions include grep- and pattern-based computations such as:

```yaml
requirement_coverage:
  step_1: "Extract requirement IDs from source (FR-XXX, NFR-XXX, R-XXX patterns)"
  step_2: "For each requirement ID, grep-search the variant for matches"
  step_3: "Also keyword-match requirement descriptions (fuzzy match threshold: 3+ consecutive words)"
  step_4: "RC = matched_requirements / total_source_requirements"
```

**Reusable pattern:**
- If a skill needs scoring, split into:
  - deterministic text metrics (repeatable)
  - qualitative rubric with evidence

### 10.2 Qualitative layer with Claim–Evidence–Verdict (CEV)

From `/refs/scoring-protocol.md`:

> “Uses an additive binary rubric with mandatory evidence citation (Claim-Evidence-Verdict protocol).”

CEV format (verbatim):

```text
CLAIM:    "[Criterion description] is met/not met in Variant X"
EVIDENCE: "[Direct quote or section reference from the variant]"
          OR "No evidence found — searched sections [list]"
VERDICT:  MET (1 point) | NOT MET (0 points)
```

Key rule (verbatim):
- > “If the evaluator cannot cite specific evidence for a MET verdict, the criterion defaults to NOT MET”

**Reusable pattern:**
- For any LLM-based evaluation, require evidence citations and default to “NOT MET” if evidence is missing.

### 10.3 Combined scoring + tiebreakers

From `/refs/scoring-protocol.md`:

```text
variant_score = (0.50 × quant_score) + (0.50 × qual_score)
```

Tiebreaker protocol is explicitly deterministic:
- > “If still tied, the variant presented first in input order is selected (arbitrary but deterministic)”

**Reusable pattern:**
- Include deterministic tie resolution so repeated runs are reproducible.

### 10.4 Position-bias mitigation (dual-pass evaluation)

From `/refs/scoring-protocol.md`:

> “The qualitative evaluation runs twice per variant:”

- Pass 1 in input order
- Pass 2 in reverse order
- Disagreements are re-evaluated with explicit comparison

Verbatim excerpt:

```text
- Both passes agree → Use the agreed verdict
- Passes disagree → Criterion is re-evaluated ...; the re-evaluation verdict is final
```

**Reusable pattern:**
- When using an LLM as judge, run dual-pass evaluation to mitigate ordering bias.

---

## 11) MCP integration + circuit breakers as a skill design pattern

From `SKILL.md`:

```md
## MCP Integration

| Server | Usage | Steps |
|--------|-------|-------|
| Sequential | Debate scoring, convergence analysis, refactoring plan logic | Steps 2-4 |
| Serena | Memory persistence of adversarial outcomes | Step 5 |
| Context7 | Domain pattern validation during merge | Step 5 |

**Circuit breaker**: If Sequential unavailable, fall back to native Claude reasoning with depth reduction (deep → standard, standard → quick).
```

And in “MCP Integration Layer (T06.03)” the circuit breaker is specified with thresholds/timeouts:

```yaml
sequential:
  circuit_breaker:
    failure_threshold: 3
    timeout: "30s"
    fallback: "Native Claude reasoning with depth reduction"
    depth_reduction: "deep → standard, standard → quick"
```

**Reusable pattern:**
- Document which MCP servers are used for which steps.
- Include a circuit breaker: thresholds, timeouts, and a degraded-mode fallback behavior.

---

## 12) Interactive checkpoints pattern (AskUserQuestion gates)

The skill documents “Interactive Mode (FR-004)” and lists checkpoints.

Example excerpt (verbatim):

```yaml
interactive_checkpoints:
  after_diff_analysis:
    pause: "User can highlight priority areas for debate"
    default_action: "Auto-proceed with all diff points"

  after_base_selection:
    pause: "User can override the selected base"
    default_action: "Accept highest-scoring variant"
```

Later, the checkpoints are expanded as “pause_action” prompts:
- > “Present … to user via AskUserQuestion”

**Reusable pattern:**
- For skills that can operate autonomously but benefit from user judgment, define explicit interactive gates with default actions.

---

## 13) Provenance annotations & post-merge validation (quality gates inside a skill)

### 13.1 Provenance tagging system

From `SKILL.md` “Provenance Annotation System (T05.04)” (verbatim excerpts):

```yaml
provenance_system:
  document_header:
    format: |
      <!-- Provenance: This document was produced by /sc:adversarial -->
      <!-- Base: Variant {X} ({agent-spec}) -->
      <!-- Merge date: {ISO-8601 timestamp} -->

  per_section_tags:
    base_original: "<!-- Source: Base (original) -->"
    base_modified: "<!-- Source: Base (original, modified) — {reason} -->"
    incorporated: "<!-- Source: Variant {N} ({agent-spec}), Section {ref} — merged per Change #{N} -->"
```

**Reusable pattern:**
- If a skill produces a merged artifact, include provenance annotations to preserve traceability.

### 13.2 Post-merge validation checks

From `SKILL.md` “Post-Merge Consistency Validation (T05.05)” (verbatim excerpt):

```yaml
post_merge_validation:
  checks:
    structural_integrity:
      rules:
        - "No heading level gaps (e.g., H2 → H4 without H3)"
        - "No orphaned subsections (H3 without parent H2)"
    internal_references:
      action: "Validate all cross-references resolve"
    contradiction_rescan:
      action: "Scan merged document for NEW contradictions introduced by merge"
```

**Reusable pattern:**
- Build minimal, objective validation gates into the skill output phase (structure, reference resolution, contradiction rescan).

---

## 14) Framework registration pattern (routing + command catalog)

Custom skills may require updating central framework configuration. `SKILL.md` includes a “Framework Registration (T06.04)” protocol.

Example (verbatim):

```yaml
framework_registration:
  commands_md:
    entry: |
      **`/sc:adversarial [options]`** — Structured adversarial debate, comparison, and merge pipeline (wave-enabled, complex profile)
      - **Auto-Persona**: Architect, Analyzer, Scribe
      - **MCP**: Sequential (debate scoring), Serena (persistence), Context7 (validation)
      - **Tools**: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task]

  orchestrator_md:
    routing_entry:
      pattern: "adversarial debate"
      complexity: "complex"
      domain: "analysis"
      auto_activates: "architect + analyzer personas, --ultrathink, Sequential + Serena"
      confidence: "95%"
```

**Reusable pattern:**
- When adding a new skill that should be discoverable/routable, define:
  - a command catalog entry (for `COMMANDS.md`-style docs)
  - a router pattern entry (for `ORCHESTRATOR.md`-style routing)

---

## 15) Reusable template: building a new custom skill (pattern summary)

Below is a reusable skeleton distilled from the sc-adversarial sources.

### 15.1 Minimal SKILL.md skeleton

```md
---
name: sc:your-skill
description: <one-line description>
allowed-tools: <comma-separated tool allowlist>
---

# /sc:your-skill - <Title>

<!-- Extended metadata (for documentation, not parsed):
category: <analysis|development|docs|...>
complexity: <basic|intermediate|advanced>
mcp-servers: [<sequential>, <context7>, <serena>, ...]
personas: [<architect>, <analyzer>, ...]
-->

## Purpose
<what it does>

## Required Input
<mode A/mode B + examples>

## Triggers
<keywords and integration call sites>

## Configurable Parameters
<table of flags>

## Protocol (N-step)
<Step 1..N with YAML spec + output artifacts>

## Output Structure
<tree + naming>

## Error Handling Matrix
<YAML matrix>

## Return Contract
<YAML contract>

## Agent Delegation
<dedicated agents + responsibilities + does-not>

## MCP Integration
<server usage + circuit breakers>

## Boundaries
### Will Do
### Will Not Do
```

### 15.2 Optional add-ons (as seen in sources)

- **Agent spec mini-language** for dynamic Task agents (`<model>[:persona[:"instruction"]]`).
- **Deterministic + rubric scoring** (quant + qual) with evidence-required judgments.
- **Bias mitigation** for judging outputs (dual-pass order reversal).
- **Provenance annotations** for merged outputs.
- **Post-output validation** to prevent structural regressions.
- **Interactive checkpoints** for user overrides at key decision points.

---

## 16) References inside the skill (how sc-adversarial organizes its sub-specs)

This skill uses a `refs/` folder to store reusable protocols:
- `/refs/agent-specs.md` — agent spec grammar, advocate behavior, instantiation protocol
- `/refs/scoring-protocol.md` — scoring algorithm for base selection

**Reusable pattern:**
- For complex skills, split the skill spec into:
  - a high-level SKILL.md
  - supporting reference docs for stable protocols (agent specs, scoring, templates)
