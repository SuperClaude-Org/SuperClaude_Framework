---
name: sc:adversarial-protocol
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
---

# /sc:adversarial - Adversarial Debate & Merge Pipeline

<!-- Extended metadata (for documentation, not parsed):
category: analysis
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, analyzer, scribe]
-->

## Purpose

Generic, reusable command implementing a structured adversarial debate, comparison, and merge pipeline. Accepts multiple artifacts (files or generated variants), identifies differences and contradictions, orchestrates structured debate between agents, selects the strongest base via hybrid scoring, produces a refactoring plan, and executes it to produce a unified output.

**Core Objective**: Verify and validate accuracy of statements in generated artifacts, weeding out hallucinations and sycophantic agreement through structured adversarial pressure using steelman debate strategy.

**Key Differentiator**: Uses multi-model adversarial reasoning (10-15% accuracy gains, 30%+ factual error reduction) as a generic framework tool invocable by any SuperClaude command.

## Required Input

**MANDATORY**: Either `--compare` (Mode A), `--source`+`--generate`+`--agents` (Mode B), or `--pipeline` (Pipeline Mode) must be provided.

```
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]
/sc:adversarial --source <file> --generate <type> --agents <spec>[,...] [options]
/sc:adversarial --pipeline "<shorthand>" [options]
/sc:adversarial --pipeline @pipeline.yaml [options]
```

## Triggers

- Explicit: `/sc:adversarial --compare ...` or `/sc:adversarial --source ...`
- Keywords: "adversarial debate", "compare variants", "merge best of"
- Integration: Called by `/sc:roadmap` in multi-spec/multi-roadmap modes

## Dual Input Modes

### Mode A: Compare Existing Files (FR-001)

```bash
/sc:adversarial --compare file1.md,file2.md[,...,file10.md]
```

- Accepts 2-10 existing files for comparison, debate, and merge
- Files are copied to `<output>/adversarial/variant-N-original.md`
- Validation: All files must exist and be readable; 2-10 file count enforced

### Mode B: Generate + Compare from Source (FR-001)

```bash
/sc:adversarial --source source.md --generate <type> --agents <agent-spec>[,...]
```

- Generates variant artifacts from source using specified agents in parallel
- Agent specification format: `<model>[:persona[:"instruction"]]`
  - `opus` — model only
  - `opus:architect` — model + persona
  - `opus:architect:"focus on scalability"` — model + persona + instruction
- Supported models: Any available (opus, sonnet, haiku, configured aliases)
- Agent count: 2-10 (minimum 2 required for adversarial comparison)
- Variants written to `<output>/adversarial/variant-N-<model>-<persona>.md`

## 5-Step Adversarial Protocol (FR-002)

The core pipeline executes 5 sequential steps. Each step produces a documented artifact.

### Step 1: Diff Analysis

**Input**: All variant artifacts
**Delegation**: Analytical agent (or /sc:analyze equivalent)
**Process**:

```yaml
diff_analysis:
  structural_diff:
    action: "Compare section ordering, hierarchy depth, heading structure across variants"
    output: "Structural differences with severity ratings (Low/Medium/High)"

  content_diff:
    action: "Compare approaches topic-by-topic, identify coverage differences"
    output: "Content differences with approach summaries per variant"

  contradiction_detection:
    action: "Structured scan per contradiction detection protocol"
    categories:
      - "Opposing claims about the same subject"
      - "Requirement-constraint conflicts"
      - "Impossible timeline/dependency sequences"
    rule: "Claims must be specific enough to be falsifiable"

  unique_contribution_extraction:
    action: "Identify ideas present in only one variant"
    output: "Unique contributions with value assessment (Low/Medium/High)"

  shared_assumption_extraction:
    action: "Identify agreement points across variants and extract implicit shared assumptions (AD-2)"
    process:
      - "Scan all diff categories for agreement points (where all variants converge)"
      - "For each agreement point, enumerate underlying preconditions"
      - "Classify each precondition as STATED/UNSTATED/CONTRADICTED"
    output: "Shared assumptions with classification and A-NNN identifiers"
    promotion: "UNSTATED preconditions become synthetic [SHARED-ASSUMPTION] diff points"
```

**Output**: `adversarial/diff-analysis.md` — organized by category with severity ratings, plus Shared Assumptions section
**Template**: See `refs/artifact-templates.md` Section 1

### Step 2: Adversarial Debate

**Input**: All variants + diff-analysis.md
**Delegation**: debate-orchestrator agent coordinates; advocate agents participate
**Process**:

```yaml
adversarial_debate:
  debate_topic_taxonomy:
    purpose: "Three-level taxonomy (AD-5) ensuring state-mechanics-level debate cannot be bypassed"
    levels:
      L1_surface:
        description: "Surface-level differences: naming, formatting, style, wording choices"
        auto_tag_signals:
          - "naming convention"
          - "formatting"
          - "wording"
          - "style choice"
          - "cosmetic"
          - "presentation"
        examples: "Variable naming, markdown formatting, section ordering preferences"

      L2_structural:
        description: "Structural differences: architecture, organization, API design, component boundaries"
        auto_tag_signals:
          - "architecture"
          - "API design"
          - "component"
          - "module"
          - "interface"
          - "dependency"
          - "organization"
        examples: "Module decomposition, API endpoint design, data flow patterns"

      L3_state_mechanics:
        description: "State-mechanics-level: state management, guard conditions, boundary validation, concurrency"
        auto_tag_signals:
          - "state"
          - "guard"
          - "boundary"
          - "invariant"
          - "concurrency"
          - "race condition"
          - "validation rule"
          - "transition"
        examples: "State machine transitions, input validation guards, concurrency controls"

    auto_tagging:
      action: "Scan each diff point text for level-specific signal terms"
      priority: "L3 > L2 > L1 (if signals match multiple levels, assign highest)"
      shared_assumption_rule: "A-NNN points containing state/guard/boundary terms auto-tag as L3 (AC-AD5-3)"
      fallback: "If no signals match, assign L2 (structural) as default"
      mutual_exclusivity: "Each diff point receives exactly one taxonomy level"

  advocate_instantiation:
    action: "Parse model[:persona[:\"instruction\"]] spec for each variant"
    creation: "Task agents with advocate prompts including variant + all others + diff-analysis"

  round_1_parallel:
    action: "Each advocate presents strengths and critiques others"
    execution: "Parallel Task calls — all advocates run simultaneously"
    steelman_requirement: "Advocates MUST construct strongest version of opposing positions before critiquing"

  round_2_sequential:
    condition: "--depth standard OR --depth deep"
    action: "Rebuttals — each advocate addresses criticisms from Round 1"
    execution: "Sequential — each receives all Round 1 transcripts"

  round_3_conditional:
    condition: "--depth deep AND convergence < threshold"
    action: "Final arguments after considering all rebuttals"

  convergence_detection:
    metric: "Percentage of diff points where agents agree on superior approach"
    threshold: "Configurable via --convergence (default 0.80)"
    tracking: "Per-point agreement tracking across rounds"

  scoring_matrix:
    action: "For each diff point, record winner, confidence, evidence summary"
    output: "Per-point scoring matrix table"
```

**Output**: `adversarial/debate-transcript.md` — full debate with per-point scoring
**Template**: See `refs/artifact-templates.md` Section 2

### Step 3: Hybrid Scoring & Base Selection

**Input**: All variants + debate-transcript.md
**Delegation**: debate-orchestrator agent
**Process**:

```yaml
base_selection:
  quantitative_layer:
    weight: 0.50
    metrics:
      requirement_coverage:
        weight: 0.30
        computation: "grep-match source requirements in variant / total requirements"
      internal_consistency:
        weight: 0.25
        computation: "1 - (contradictions / total claims)"
      specificity_ratio:
        weight: 0.15
        computation: "concrete statements / total substantive statements"
      dependency_completeness:
        weight: 0.15
        computation: "resolved internal references / total internal references"
      section_coverage:
        weight: 0.15
        computation: "variant sections / max(sections across all variants)"
    formula: "quant_score = (RC×0.30) + (IC×0.25) + (SR×0.15) + (DC×0.15) + (SC×0.15)"

  qualitative_layer:
    weight: 0.50
    rubric: "30-criterion additive binary rubric across 6 dimensions"
    dimensions:
      - "Completeness (5 criteria)"
      - "Correctness (5 criteria)"
      - "Structure (5 criteria)"
      - "Clarity (5 criteria)"
      - "Risk Coverage (5 criteria)"
      - "Invariant & Edge Case Coverage (5 criteria)"
    evidence_protocol: "Claim-Evidence-Verdict (CEV) for every criterion"
    formula: "qual_score = total_criteria_met / 30"
    edge_case_floor:
      threshold: "1/5"
      rule: "Variants scoring <1/5 on Invariant & Edge Case Coverage are ineligible as base variant"
      suspension: "When all variants score 0/5, suspend floor with warning"

  position_bias_mitigation:
    pass_1: "Evaluate variants in input order (A, B, C, ...)"
    pass_2: "Evaluate variants in reverse order (C, B, A, ...)"
    agreement: "Use agreed verdict"
    disagreement: "Re-evaluate with explicit comparison prompt citing both passes"

  combined_scoring:
    formula: "variant_score = (0.50 × quant_score) + (0.50 × qual_score)"

  tiebreaker_protocol:
    condition: "Top two variants within 5% of each other"
    level_1: "Debate performance (points won in Step 2)"
    level_2: "Higher correctness criteria count"
    level_3: "Input order (arbitrary but deterministic)"
```

**Output**: `adversarial/base-selection.md` — full scoring breakdown with evidence
**Template**: See `refs/artifact-templates.md` Section 3
**Reference**: See `refs/scoring-protocol.md` for complete algorithm

### Step 4: Refactoring Plan

**Input**: Selected base + all other variants + debate-transcript.md
**Delegation**: debate-orchestrator drafts, analytical agent reviews
**Process**:

```yaml
refactoring_plan:
  for_each_non_base_strength:
    action: "Generate improvement description + integration point"
    fields:
      - "Source variant and section"
      - "Target location in base"
      - "Rationale (citing debate evidence)"
      - "Integration approach"
      - "Risk level"

  for_each_base_weakness:
    action: "Reference which non-base variant addresses it better"
    fields:
      - "Issue description"
      - "Better variant reference"
      - "Fix approach"

  changes_not_being_made:
    action: "Document differences where base approach was determined superior"
    rationale: "Transparency — show what was considered and rejected"

  review:
    default: "Auto-approved"
    interactive: "User-approved when --interactive flag set"
```

**Output**: `adversarial/refactor-plan.md` — actionable merge plan with integration points
**Template**: See `refs/artifact-templates.md` Section 4

### Step 5: Merge Execution

**Input**: Base variant + refactor-plan.md
**Delegation**: merge-executor agent (dedicated specialist)
**Process**:

```yaml
merge_execution:
  step_1: "Read base variant and refactoring plan"
  step_2: "Apply each planned change methodically"
  step_3: "Maintain structural integrity during merge"
  step_4: "Add provenance annotations (source attribution per section)"
  step_5: "Validate merged output — structural integrity, internal references, contradiction re-scan"
  step_6: "Produce merge-log.md documenting each applied change"
```

**Output**: Unified merged artifact + `adversarial/merge-log.md`
**Template**: See `refs/artifact-templates.md` Section 5

## Configurable Parameters (FR-003)

| Parameter | Flag | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| Depth | `--depth` | `standard` | quick/standard/deep | Controls debate rounds (1/2/3) |
| Convergence | `--convergence` | `0.80` | 0.50-0.99 | Alignment threshold for deep mode |
| Interactive | `--interactive` | `false` | true/false | User approval at decision points |
| Output dir | `--output` | Auto-derived | Any path | Where artifacts are written |
| Focus areas | `--focus` | All | Comma-separated | Debate focus areas |
| Pipeline | `--pipeline` | (none) | Inline shorthand or @path.yaml | Routes to Meta-Orchestrator; mutually exclusive with --compare/--source |
| Pipeline Parallel | `--pipeline-parallel` | 3 | 1-10 | Max concurrent phases per level |
| Pipeline Resume | `--pipeline-resume` | false | flag | Resume from manifest checkpoint |
| Pipeline Error | `--pipeline-on-error` | halt | halt, continue | Error policy for failed phases |
| Blind Mode | `--blind` | false | flag | Strip model names from artifacts before compare |
| Auto Stop | `--auto-stop-plateau` | false | flag | Halt on convergence plateau (<5% delta, 2 consecutive) |

## Interactive Mode (FR-004)

When `--interactive` is specified, the pipeline pauses for user input at:

```yaml
interactive_checkpoints:
  after_diff_analysis:
    pause: "User can highlight priority areas for debate"
    default_action: "Auto-proceed with all diff points"

  after_debate:
    pause: "User can override convergence assessment"
    default_action: "Accept computed convergence"

  after_base_selection:
    pause: "User can override the selected base"
    default_action: "Accept highest-scoring variant"

  after_refactoring_plan:
    pause: "User can modify the plan before execution"
    default_action: "Auto-approve and execute"
```

Default (non-interactive): All decisions auto-resolved with rationale documented.

## Artifact Output Structure (FR-005)

```
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

**Naming conventions**:
- Mode A: `variant-N-original.md` (copies of input files)
- Mode B: `variant-N-<model>-<persona>.md`

## Error Handling Matrix (FR-006)

```yaml
error_handling:
  agent_failure:
    behavior: "Retry once, then proceed with N-1 variants"
    constraint: "Minimum 2 variants required"
    fallback: "If only 1 variant survives, abort and return it with warning"

  variants_too_similar:
    threshold: "<10% diff"
    behavior: "Skip debate, select either as base"
    log: "variants substantially identical"

  no_convergence:
    condition: "Max rounds reached without meeting threshold"
    behavior: "Force-select by score, document non-convergence"
    flag: "Flag for user review"

  merge_failure:
    behavior: "Preserve all artifacts, flag failure"
    recovery: "Provide refactor-plan.md for manual execution"

  single_variant_remaining:
    behavior: "Abort adversarial process"
    return: "Surviving variant as-is with warning"
```

## Return Contract (MANDATORY)

**This is the final pipeline step.** sc:adversarial MUST write this return contract on every invocation, including failures. When a field's value cannot be determined (pipeline aborted before reaching that step), use `null`.

When invoked by another command, sc:adversarial returns:

```yaml
return_contract:
  merged_output_path: "<path to merged file>"       # null if merge not reached
  convergence_score: 0.75                            # float 0.0-1.0, null if debate not reached
  artifacts_dir: "<path to adversarial/ directory>"  # always set (created at pipeline start)
  status: "success"                                  # success | partial | failed
  base_variant: "opus:architect"                     # model:persona that won debate, null if not reached
  unresolved_conflicts: 2                            # integer count of unresolved diff points, 0 on success
  fallback_mode: false                               # true if pipeline used fallback path
  failure_stage: null                                # null on success; "variant_generation" | "debate" | "merge" | "validation" | "transport"
  invocation_method: "skill-direct"                  # "skill-direct" | "task-agent" | "manual"
  unaddressed_invariants: []                         # list of HIGH-severity UNADDRESSED items from invariant probe; empty on success
```

**Write-on-failure**: If the pipeline aborts at any stage, sc:adversarial MUST still write the return contract with `status: "failed"`, the `failure_stage` set to the step that failed, and all unreached fields set to `null`. This ensures the caller can always consume the contract.

**Field definitions**:

| Field | Type | Description |
|-------|------|-------------|
| `merged_output_path` | `string\|null` | Path to merged output file; null if merge not reached |
| `convergence_score` | `float\|null` | Final convergence score 0.0-1.0; null if debate not reached |
| `artifacts_dir` | `string` | Path to adversarial/ directory (always set) |
| `status` | `enum` | `success` (all steps pass), `partial` (completed with warnings), `failed` (aborted) |
| `base_variant` | `string\|null` | Model:persona that won adversarial debate; null if debate not reached |
| `unresolved_conflicts` | `integer` | Count of unresolved diff points; 0 on full success |
| `fallback_mode` | `boolean` | True if pipeline used any fallback path |
| `failure_stage` | `string\|null` | Null on success; identifies the stage that caused failure |
| `invocation_method` | `enum` | How this invocation was triggered: `skill-direct`, `task-agent`, or `manual` |
| `unaddressed_invariants` | `list` | HIGH-severity UNADDRESSED items from invariant probe; empty list `[]` when no HIGH items remain or when Round 2.5 was skipped; populated with `[{id, category, assumption, severity}]` when HIGH items exist |

## Agent Delegation

### debate-orchestrator Agent
- **Role**: Coordinates the entire pipeline without participating in debates
- **Model**: Highest-capability (opus preferred)
- **Tools**: Task, Read, Write, Glob, Grep, Bash
- **Responsibilities**: Parse inputs, dispatch variants, coordinate 5-step protocol, track convergence, make base selection, compile return contract
- **Does NOT**: Generate variants, participate in debates, execute merges

### merge-executor Agent
- **Role**: Executes refactoring plans to produce unified merged artifacts
- **Model**: High-capability (opus or sonnet)
- **Tools**: Read, Write, Edit, Grep
- **Responsibilities**: Read base + plan, apply changes, maintain integrity, add provenance, validate output, produce merge-log
- **Does NOT**: Make strategic decisions, override plan, participate in debates

### Advocate Agents (Dynamic)
- **Role**: Argue for their variant's strengths in structured debate
- **Instantiation**: Dynamic from `--agents` specification
- **Behavior**: Shaped by model + persona + instruction; steelman opposing positions before critiquing

## MCP Integration

| Server | Usage | Steps |
|--------|-------|-------|
| Sequential | Debate scoring, convergence analysis, refactoring plan logic | Steps 2-4 |
| Serena | Memory persistence of adversarial outcomes | Step 5 |
| Context7 | Domain pattern validation during merge | Step 5 |

**Circuit breaker**: If Sequential unavailable, fall back to native Claude reasoning with depth reduction (deep → standard, standard → quick).

## Compliance Tier Classification

Default tier: **STRICT** — adversarial debate involves multi-file operations, multi-agent coordination, and complex scoring.

Automatic escalation triggers:
- Always STRICT when operating (multi-file by nature)
- Multi-agent delegation inherently complex

## Boundaries

### Will Do
- Compare 2-10 artifacts through structured adversarial debate
- Generate variant artifacts using different model/persona configurations
- Produce transparent, documented merge decisions
- Execute refactoring plans to produce unified outputs
- Support configurable depth, convergence thresholds, and focus areas
- Work as a generic tool invocable by any SuperClaude command

### Will Not Do
- Validate domain-specific correctness of merged output (calling command's responsibility)
- Execute the merged output (planning tool, not execution tool)
- Manage git operations or version control
- Make decisions without documented rationale
- Operate with fewer than 2 variants (minimum for adversarial comparison)
- Override user decisions in interactive mode

---

## Implementation Details — Step 1: Diff Analysis Engine

### Input Mode Parsing Protocol

Before any pipeline work begins, parse and validate the input mode:

```yaml
input_mode_parsing:
  step_0_pipeline_guard:
    description: "Check for --pipeline flag before any Mode A/B parsing"
    pipeline_signal: "--pipeline flag present (inline shorthand or @path.yaml)"
    action: |
      If --pipeline flag is present:
        1. Set pipeline_mode = true
        2. Skip step_1 through step_4 (Mode A/B parsing not applicable in pipeline mode)
        3. Route to Meta-Orchestrator section for pipeline definition parsing and DAG execution
      If --pipeline flag is absent:
        1. Set pipeline_mode = false
        2. Proceed to step_1_detect_mode (existing Mode A/B behavior unchanged)
    conflict_with_modes: |
      If --pipeline is present alongside --compare or --source/--generate/--agents:
        STOP with error: 'Cannot use --pipeline with --compare or --source/--generate/--agents. Pipeline mode defines its own phases.'
    validation: "Flag value must be either an inline shorthand string or a @-prefixed YAML file path"

  step_1_detect_mode:
    condition: "pipeline_mode == false"
    mode_a_signal: "--compare flag present"
    mode_b_signal: "--source AND --generate AND --agents flags present"
    conflict: "If both Mode A and Mode B flags present → STOP with error: 'Cannot use --compare with --source/--generate/--agents'"
    neither: "If neither mode detected → STOP with error: 'Must provide --compare (Mode A), --source + --generate + --agents (Mode B), or --pipeline (Pipeline Mode)'"

  step_2_mode_a_parsing:
    action: "Split --compare value on commas to get file paths"
    validation:
      count_check: "2 ≤ file_count ≤ 10; reject with error if outside range"
      existence_check: "For each path, verify file exists and is readable"
      type_check: "Warn if file is not markdown (.md); proceed but log warning"
    error_messages:
      too_few: "STOP: 'Adversarial comparison requires at least 2 files, got <N>'"
      too_many: "STOP: 'Maximum 10 files supported, got <N>'"
      missing_file: "STOP: 'File not found: <path>'"
    output: "List of validated file paths (2-10)"

  step_3_mode_b_parsing:
    required_flags:
      source: "Path to source file (must exist)"
      generate: "Artifact type to generate (e.g., roadmap, spec, design)"
      agents: "Comma-separated agent specifications"
    missing_flag_error: "STOP: 'Mode B requires all three flags: --source, --generate, --agents. Missing: <list>'"

    agent_spec_parsing:
      format: "<model>[:persona[:\"instruction\"]]"
      separator: ":"
      instruction_delimiter: '"'
      validation:
        model: "Must be a recognized model name (opus, sonnet, haiku) or configured alias"
        persona: "If provided, should match a SuperClaude persona; WARN if unknown"
        instruction: "If provided, must be enclosed in double quotes"
      count_check: "2 ≤ agent_count ≤ 10"
      error_messages:
        invalid_model: "STOP: 'Unknown model: <model>'"
        invalid_persona: "WARN: 'Unknown persona <persona>, using model defaults'"
        missing_quotes: "STOP: 'Instruction must be quoted: <spec>'"
        too_few_agents: "STOP: 'Adversarial comparison requires at least 2 agents, got <N>'"
        too_many_agents: "STOP: 'Maximum 10 agents supported, got <N>'"
      output: "List of parsed agent specs [{model, persona?, instruction?}, ...]"

  step_4_common_flags:
    depth:
      values: ["quick", "standard", "deep"]
      default: "standard"
      invalid: "WARN: 'Unknown depth <value>, using standard'"
    convergence:
      range: "0.50 to 0.99"
      default: 0.80
      invalid: "WARN: 'Convergence <value> out of range [0.50, 0.99], using 0.80'"
    interactive:
      default: false
    output:
      default: "Auto-derived from input file directory"
    focus:
      format: "Comma-separated list of focus areas"
      default: "All (no filtering)"
```

### Variant File Loading and Normalization

After input mode parsing, load and normalize variants:

```yaml
variant_loading:
  output_directory:
    creation: "Create <output-dir>/adversarial/ if it does not exist"
    structure: |
      <output-dir>/
      └── adversarial/
          ├── variant-1-<suffix>.md
          ├── variant-2-<suffix>.md
          └── ...

  mode_a_loading:
    action: "Read each input file and copy to adversarial directory"
    naming: "variant-N-original.md (N = 1-based index in input order)"
    process:
      - "For file_index, file_path in enumerate(input_files, start=1):"
      - "  Read file content"
      - "  Write to <output-dir>/adversarial/variant-{file_index}-original.md"
    normalization:
      - "Strip trailing whitespace from each line"
      - "Ensure file ends with single newline"
      - "Preserve original heading structure exactly"

  mode_b_loading:
    action: "Placeholder — variant generation handled in Phase 6 (T06.02)"
    naming: "variant-N-<model>-<persona>.md"
    stub_behavior: |
      Mode B variant generation is wired in Phase 6.
      When reached, dispatch Task agents per --agents spec.
      Each agent generates an artifact from --source using --generate type.
      Results written to adversarial/ with naming convention above.

  variant_metadata:
    track_per_variant:
      - "variant_id: N (1-based)"
      - "source_path: original file path (Mode A) or 'generated' (Mode B)"
      - "agent_spec: agent specification (Mode B only)"
      - "heading_count: number of top-level sections"
      - "line_count: total lines"
      - "word_count: approximate word count"
```

### Structural Diff Engine

Compare heading hierarchies, section ordering, and structural organization:

```yaml
structural_diff:
  heading_extraction:
    process:
      - "Scan each variant for markdown heading lines (^#{1,6} )"
      - "Build heading tree: level, text, line number, children"
      - "Record: max_depth, heading_count_per_level, section_sequence"
    heading_levels:
      H1: "# (document title)"
      H2: "## (top-level sections)"
      H3: "### (subsections)"
      H4_plus: "#### and deeper (detail sections)"

  comparison_dimensions:
    section_ordering:
      action: "Compare sequence of H2 headings across variants"
      match: "Fuzzy match section names (≥80% word overlap = same topic)"
      output: "Ordered list of sections per variant, highlighting order differences"
      severity:
        Low: "Same sections, different order (cosmetic preference)"
        Medium: "Different grouping or categorization of topics"
        High: "Incompatible organizational models (e.g., chronological vs. categorical)"

    hierarchy_depth:
      action: "Compare max nesting level per variant"
      output: "Max depth per variant, per-section depth comparison"
      severity:
        Low: "Depth differs by 1 level"
        Medium: "Depth differs by 2+ levels"
        High: "One variant uses flat structure, other uses deep nesting"

    heading_structure:
      action: "Compare heading count and distribution across levels"
      output: "Heading count per level per variant"
      severity:
        Low: "Minor differences in subsection count"
        Medium: "Significant differences in section granularity"
        High: "Fundamentally different document organization"

  output_format:
    id_scheme: "S-NNN (sequential, starting at S-001)"
    table_columns: ["#", "Area", "Variant A", "Variant B", "...", "Severity"]
    scaling: "For >2 variants, expand table horizontally with one column per variant"
```

### Content Diff Engine

Compare approaches topic-by-topic across variants:

```yaml
content_diff:
  topic_extraction:
    process:
      - "For each variant, extract topics from H2/H3 section headings"
      - "Build topic inventory: {topic_name, variant_id, section_ref, content_summary}"
      - "Match topics across variants using fuzzy name matching (≥60% word overlap)"
    categorize:
      shared_topics: "Topics present in 2+ variants"
      variant_only_topics: "Topics in exactly one variant (→ feeds unique contributions)"

  approach_comparison:
    for_shared_topics:
      action: "For each matched topic, compare how variants address it"
      dimensions:
        - "Coverage depth: how thoroughly the topic is addressed"
        - "Approach: what strategy or method is proposed"
        - "Detail level: specificity of recommendations or requirements"
        - "Emphasis: what aspects are prioritized"
      output: "Per-topic comparison with approach summaries per variant"

    coverage_gaps:
      action: "Identify topics covered by some variants but not others"
      output: "Gap matrix showing which topics are missing from which variants"

  severity_assignment:
    Low: "Same conclusion via different wording or emphasis"
    Medium: "Materially different approaches to the same topic"
    High: "Fundamentally incompatible strategies for the same topic"

  output_format:
    id_scheme: "C-NNN (sequential, starting at C-001)"
    table_columns: ["#", "Topic", "Variant A Approach", "Variant B Approach", "...", "Severity"]
```

### Contradiction Detection Protocol

Structured scan for contradictions across and within variants:

```yaml
contradiction_detection:
  claim_extraction:
    process:
      - "Scan each variant for specific, falsifiable statements"
      - "A claim is falsifiable if it can be definitively proven true or false"
      - "EXCLUDE vague statements: 'as appropriate', 'as needed', 'best practices' (without citation)"
      - "EXCLUDE subjective preferences without criteria"
    claim_types:
      factual: "Assertions about facts, numbers, dates, technologies"
      requirement: "Statements of what must/shall/should be done"
      constraint: "Limitations, thresholds, boundaries"
      dependency: "Sequential requirements, prerequisites, timelines"

  contradiction_categories:
    opposing_claims:
      description: "Two statements assert opposite or incompatible things about the same subject"
      detection: "For each claim, search other claims for negation or incompatible assertion about the same entity"
      example: "Variant A: 'Use PostgreSQL' vs Variant B: 'Use MongoDB for the same data store'"
      scope: "Both cross-variant and intra-variant (within same document)"

    requirement_constraint_conflicts:
      description: "A stated requirement conflicts with a stated constraint"
      detection: "Match requirement statements against constraint statements; flag where satisfying one violates the other"
      example: "'Must support 10K concurrent users' vs 'Single-threaded architecture required'"

    impossible_sequences:
      description: "Timeline or dependency creates an impossible execution order"
      detection: "Build dependency graph from stated prerequisites; detect cycles or impossible orderings"
      example: "'Module A depends on Module B' AND 'Module B depends on Module A'"

  severity_assignment:
    Low: "Minor wording conflict, does not affect implementation"
    Medium: "Substantive disagreement that affects design decisions"
    High: "Fundamental incompatibility that must be resolved before merge"

  output_format:
    id_scheme: "X-NNN (sequential, starting at X-001)"
    table_columns: ["#", "Point of Conflict", "Variant A Position", "Variant B Position", "...", "Impact"]
    evidence_requirement: "Each contradiction must cite specific text from both variants"
```

### Unique Contribution Extraction

Identify ideas present in only one variant:

```yaml
unique_contribution_extraction:
  detection:
    process:
      - "For each section/idea in each variant, check if ANY other variant covers the same topic"
      - "Use topic matching from content diff engine (≥60% word overlap = covered)"
      - "Ideas with NO match in any other variant = unique contribution"
    granularity: "Section-level (H2 or H3) — not individual sentences"
    exclusions:
      - "Boilerplate sections common to the artifact type (table of contents, metadata)"
      - "Minor formatting or stylistic choices"
      - "Restatements of input requirements (not original contributions)"

  value_assessment:
    High: "Addresses a gap no other variant covers; high impact on completeness or correctness"
    Medium: "Useful addition that improves quality but is not critical"
    Low: "Nice to have; minimal impact on overall artifact quality"

  assessment_criteria:
    - "Does this address a requirement not covered elsewhere?"
    - "Does this add risk mitigation not present in other variants?"
    - "Does this improve clarity or usability significantly?"
    - "Is this a novel approach that could strengthen the merged output?"

  output_format:
    id_scheme: "U-NNN (sequential, starting at U-001)"
    table_columns: ["#", "Variant", "Contribution", "Value Assessment"]
```

### Shared Assumption Extraction Engine (AD-2)

Addresses the "agreement = no scrutiny" blind spot by extracting implicit shared assumptions from variant agreement points:

```yaml
shared_assumption_extraction:
  purpose: "Surface hidden preconditions that all variants assume without stating (AD-2)"
  integration_point: "Runs after unique_contribution_extraction, before diff-analysis.md assembly"

  agreement_identification:
    action: "Scan all diff categories (S-NNN, C-NNN, X-NNN, U-NNN) for convergence"
    convergence_definition: |
      An agreement point exists when:
      - All variants take the same approach to a topic (content diff)
      - All variants use the same structure for a concept (structural diff)
      - No contradiction exists between variants on a subject (absence from X-NNN)
    output: "List of agreement points with category and description"

  assumption_enumeration:
    action: "For each agreement point, enumerate underlying preconditions"
    technique: |
      Ask: 'What must be true for this agreement to be valid?'
      Categories of assumptions:
      - Domain assumptions: 'The system uses X architecture'
      - Scale assumptions: 'Traffic will not exceed Y'
      - Dependency assumptions: 'Library Z will be available'
      - Business assumptions: 'Requirement R is correctly understood'
      - Technical assumptions: 'Pattern P is applicable here'
    output: "List of preconditions per agreement point"

  classification:
    STATED: "Precondition is explicitly mentioned in at least one variant"
    UNSTATED: "Precondition is implicit — no variant states it, but all depend on it"
    CONTRADICTED: "Precondition is inconsistent — variants depend on it but evidence contradicts it"

  promotion_to_diff_points:
    condition: "classification == UNSTATED"
    action: "Promote to synthetic [SHARED-ASSUMPTION] diff point"
    id_scheme: "A-NNN (sequential, starting at A-001 per debate session)"
    tag: "[SHARED-ASSUMPTION]"
    inclusion: "Added to diff-analysis.md Shared Assumptions section"
    convergence_impact: "A-NNN points are included in total_diff_points denominator"

  output_format:
    id_scheme: "A-NNN (sequential, starting at A-001)"
    table_columns: ["#", "Agreement Source", "Assumption", "Classification", "Promoted"]
    promoted_table_columns: ["#", "Assumption", "Impact", "Status"]

  AC_AD2_1:
    test: "3 variants assuming 1:1 event-widget mapping"
    expected: "UNSTATED precondition '1:1 event-widget mapping' is surfaced"
    verdict: "A-001 created with classification UNSTATED"
```

### diff-analysis.md Artifact Assembly

Combine all diff components into the final Step 1 artifact:

```yaml
diff_analysis_assembly:
  output_path: "<output-dir>/adversarial/diff-analysis.md"

  assembly_order:
    1_metadata:
      content: |
        # Diff Analysis: <artifact-type> Comparison
        ## Metadata
        - Generated: <ISO-8601 timestamp>
        - Variants compared: <count>
        - Total differences found: <count>
        - Categories: structural (<N>), content (<N>), contradictions (<N>), unique (<N>), shared assumptions (<N>)

    2_structural_differences:
      source: "Structural diff engine output"
      section: "## Structural Differences"
      format: "Table with S-NNN IDs per structural_diff.output_format"

    3_content_differences:
      source: "Content diff engine output"
      section: "## Content Differences"
      format: "Table with C-NNN IDs per content_diff.output_format"

    4_contradictions:
      source: "Contradiction detection output"
      section: "## Contradictions"
      format: "Table with X-NNN IDs per contradiction_detection.output_format"

    5_unique_contributions:
      source: "Unique contribution extraction output"
      section: "## Unique Contributions"
      format: "Table with U-NNN IDs per unique_contribution_extraction.output_format"

    6_shared_assumptions:
      source: "Shared assumption extraction engine output (AD-2)"
      section: "## Shared Assumptions"
      format: "Table with A-NNN IDs per shared_assumption_extraction.output_format"
      content: |
        Only UNSTATED preconditions promoted to [SHARED-ASSUMPTION] diff points appear here.
        STATED assumptions are documented but not promoted.
        CONTRADICTED assumptions are flagged for debate attention.
      table_columns: ["A-NNN", "Assumption", "Source Agreement", "Impact", "Status"]

    7_summary:
      content: |
        ## Summary
        - Total structural differences: <N>
        - Total content differences: <N>
        - Total contradictions: <N>
        - Total unique contributions: <N>
        - Total shared assumptions surfaced: <N> (UNSTATED: <N>, STATED: <N>, CONTRADICTED: <N>)
        - Highest-severity items: <list of IDs with High severity>

  validation:
    - "All 5 sections present and non-empty (warn if a section has 0 items)"
    - "All ID sequences are contiguous (no gaps: S-NNN, C-NNN, X-NNN, U-NNN, A-NNN)"
    - "Metadata counts match actual table row counts"
    - "Severity/impact ratings present for every entry"
    - "A-NNN IDs are sequential starting from A-001 with no gaps"

  similarity_check:
    threshold: "10% — if total differences < 10% of total comparable items"
    action: "Log 'variants substantially identical' per FR-006 error handling"
    behavior: "Skip debate (Steps 2-3), select either variant as base, proceed to merge"
```

## Implementation Details — Step 2: Adversarial Debate Protocol

### Advocate Agent Instantiation (T03.01)

Dynamically create advocate agents from the `--agents` specification:

```yaml
advocate_instantiation:
  per_agent_spec:
    parse:
      - "Extract model (required): first segment before ':'"
      - "Extract persona (optional): second segment before ':' or '\"'"
      - "Extract instruction (optional): quoted string after second ':'"
    validate:
      model: "Must be recognized: opus, sonnet, haiku, or configured alias"
      persona: "If provided, map to SuperClaude persona (architect, security, analyzer, etc.)"
      instruction: "If provided, must be enclosed in double quotes"

  prompt_generation:
    template: |
      You are an advocate agent in a structured adversarial debate.
      Your variant: {variant_name}
      Model: {model}
      Persona: {persona or 'default'}
      Custom instruction: {instruction or 'none'}

      RULES:
      1. Argue for your variant's strengths with EVIDENCE (cite sections, quotes)
      2. STEELMAN opposing variants BEFORE critiquing them
      3. Cite specific sections, quotes, or content as evidence for every claim
      4. Acknowledge genuine weaknesses in your variant honestly
      5. Focus on these areas: {focus_areas or 'All'}
      6. For each [SHARED-ASSUMPTION] point (A-NNN), respond with ACCEPT/REJECT/QUALIFY

    shared_assumption_handling: |
      SHARED ASSUMPTION RESPONSE (MANDATORY):
      The diff analysis identified the following shared assumptions (A-NNN).
      For EACH assumption listed, you MUST respond with exactly one of:
        - ACCEPT: You agree this assumption is valid and should remain implicit
        - REJECT: You believe this assumption is incorrect; provide counter-evidence
        - QUALIFY: The assumption is partially valid; state the conditions under which it holds

      Shared assumptions to address:
      {shared_assumptions_list}

      WARNING: Omitting a response for any A-NNN point will be flagged in the transcript.

    omission_detection: |
      After advocate response is collected:
      1. Extract all A-NNN IDs from the shared_assumptions_list in the prompt
      2. Scan advocate response for each A-NNN ID with ACCEPT/REJECT/QUALIFY
      3. For any A-NNN ID not addressed:
         - Flag in transcript: "[OMISSION] Advocate {variant_name} did not address {A-NNN}"
         - Count omissions for quality scoring

    steelman_injection: |
      STEELMAN PROTOCOL (MANDATORY):
      Before critiquing any opposing variant, you MUST:
      1. State the strongest possible version of their argument
      2. Identify what their approach genuinely gets right
      3. Only THEN present your critique with counter-evidence

    persona_activation: |
      When persona is specified, activate the corresponding SuperClaude persona behavior:
      - architect → focus on structure, dependencies, long-term impact
      - security → focus on vulnerabilities, attack surface, compliance
      - analyzer → focus on evidence quality, logical consistency
      - frontend → focus on user experience, accessibility
      - backend → focus on data integrity, scalability, fault tolerance
      - performance → focus on efficiency, bottlenecks, resource usage
      - qa → focus on edge cases, test coverage, failure scenarios

  task_dispatch_config:
    model: "{parsed_model}"
    max_turns: 5
    prompt: "{generated_prompt}"
    input_data:
      own_variant: "Full text of advocate's variant"
      other_variants: "Full text of all other variants"
      diff_analysis: "Full text of diff-analysis.md"

  mode_a_assignment:
    rule: "One advocate per input file; agent spec defaults to current model if --agents not specified"
    naming: "Advocate for Variant 1, Advocate for Variant 2, etc."

  mode_b_assignment:
    rule: "Each --agents spec generates one variant AND provides one advocate"
    naming: "Advocate inherits agent spec identity"

  count_validation:
    minimum: 2
    maximum: 10
    too_few: "STOP: 'Adversarial comparison requires at least 2 variants'"
    too_many: "STOP: 'Maximum 10 variants supported'"
```

### Round 1: Parallel Advocate Statements (T03.02)

```yaml
round_1_parallel:
  condition: "Always executes (all depth levels)"
  execution: "PARALLEL — all advocates run simultaneously via Task tool"

  dispatch:
    action: "For each advocate, spawn Task agent with advocate prompt + variant data"
    parallelism: "All Task calls issued in a SINGLE message block (true parallel)"
    collection: "Wait for all agents to complete; collect responses"

  advocate_output_format:
    required_sections:
      position_summary: "1-3 sentence summary of overall argument for their variant"
      steelman: "For EACH opposing variant: strongest version of their argument"
      strengths_claimed: "Numbered list with evidence citations from their variant"
      weaknesses_identified: "Numbered list with evidence citations from other variants"
      concessions: "Any genuine weaknesses acknowledged in own variant"

  failure_handling:
    single_failure:
      action: "Retry the failed agent once"
      retry_failure: "Proceed with N-1 advocates (log warning)"
      minimum_check: "If fewer than 2 advocates remain → ABORT debate"
    multiple_failures:
      action: "If fewer than 2 advocates succeed → ABORT debate entirely"
      fallback: "Return available variants as-is with warning"
    timeout:
      behavior: "Inherits from Task tool defaults"
```

### Round 2: Sequential Rebuttals (T03.03)

```yaml
round_2_sequential:
  condition: "--depth standard OR --depth deep"
  skip_condition: "--depth quick → skip Round 2 entirely (log: 'Round 2 skipped: depth=quick')"
  execution: "SEQUENTIAL — each advocate sees all previous rebuttals"

  dispatch:
    order: "Input order (Variant 1 advocate first, then Variant 2, etc.)"
    per_advocate_input:
      - "All Round 1 transcripts (every advocate's statement)"
      - "Specific criticisms raised against their variant (extracted from Round 1)"
    per_advocate_output:
      response_to_criticisms: "Address each criticism with counter-evidence or concession"
      updated_assessment: "Revised view of other variants after seeing their defenses"
      new_evidence: "Any additional evidence not presented in Round 1"

  post_round_2:
    convergence_check: "Run convergence detection (see below)"
    taxonomy_coverage_check: "Run taxonomy coverage gate — if any level has zero coverage, trigger forced round"
    invariant_probe: "Run Round 2.5 invariant probe (if --depth standard or --depth deep)"
    if_converged: "Log convergence achieved, proceed to scoring"
    if_blocked_by_taxonomy: "Execute forced round for uncovered level, then re-check convergence"
    if_blocked_by_invariants: "HIGH-severity UNADDRESSED items block convergence (see Round 2.5)"
    if_not_converged: "Continue to Round 3 if --depth deep"
```

### Round 2.5: Invariant Probe (AD-1)

```yaml
round_2_5_invariant_probe:
  purpose: "Systematic fault-finding against emerging consensus using 5-category boundary-condition checklist"
  condition: "--depth standard OR --depth deep"
  skip_condition: "--depth quick → skip (log: 'Round 2.5 (invariant probe) skipped: --depth quick')"
  execution: "SINGLE AGENT — fault-finder agent probes consensus independently"
  insertion_point: "Between Round 2 and Round 3 (after post_round_2 convergence check)"

  fault_finder_agent:
    role: "Independent fault-finder — NOT an advocate for any variant"
    input:
      - "Emerging consensus: per-point tracking from convergence detection (agreed points + winners)"
      - "All Round 1 and Round 2 transcripts"
      - "diff-analysis.md (structural + content diffs, contradictions, shared assumptions)"
    output: "Structured findings per category with ID, assumption, status, severity"

  five_category_checklist:
    state_variables:
      description: "Variables that must maintain specific values or relationships across operations"
      probing_questions:
        - "What state is implicitly assumed to persist between operations?"
        - "Are there initialization assumptions that could be violated?"
        - "Do any agreed approaches assume state that the other variant manages differently?"
      detection_targets:
        - "Uninitialized state dependencies"
        - "State mutation ordering assumptions"
        - "Cross-component state coupling"

    guard_conditions:
      description: "Preconditions, postconditions, and assertions that protect correctness"
      probing_questions:
        - "What preconditions does the consensus implicitly rely on?"
        - "Are there missing null/empty/boundary checks in the agreed approach?"
        - "Do guard conditions from one variant contradict assumptions in another?"
      detection_targets:
        - "Missing input validation"
        - "Unguarded type assumptions"
        - "Silently swallowed error conditions"

    count_divergence:
      description: "Off-by-one errors, loop bounds, index calculations, and quantity assumptions"
      probing_questions:
        - "Are loop bounds inclusive or exclusive — and is this consistent?"
        - "Do count calculations agree between the consensus and variant implementations?"
        - "Are there fence-post or off-by-one risks in the agreed approach?"
      detection_targets:
        - "Inclusive vs exclusive range disagreements"
        - "Length vs index confusion"
        - "Iteration count mismatches"

    collection_boundaries:
      description: "Empty collections, single-element cases, maximum size, and ordering assumptions"
      probing_questions:
        - "What happens when a collection is empty in the agreed approach?"
        - "Does the consensus handle single-element edge cases correctly?"
        - "Are there implicit ordering assumptions (sorted, unique, non-null elements)?"
      detection_targets:
        - "Empty collection crashes or silent failures"
        - "Single-element degenerate cases"
        - "Implicit sort/uniqueness assumptions"

    interaction_effects:
      description: "Emergent behaviors when multiple components or features combine"
      probing_questions:
        - "Do any two agreed-upon changes interact in ways not individually tested?"
        - "Are there ordering dependencies between separately agreed changes?"
        - "Could the combination of changes from different variants create conflicts?"
      detection_targets:
        - "Feature interaction conflicts"
        - "Ordering-dependent side effects"
        - "Sentinel value collisions across components"

  prompt_template: |
    ROUND 2.5: INVARIANT PROBE — FAULT-FINDER AGENT

    You are an independent fault-finder. Your job is NOT to advocate for any variant.
    Your job is to find invariant violations, boundary-condition errors, and hidden
    assumptions in the EMERGING CONSENSUS from the debate.

    EMERGING CONSENSUS:
    {consensus_summary}

    DEBATE TRANSCRIPTS (Round 1 + Round 2):
    {debate_transcripts}

    DIFF ANALYSIS:
    {diff_analysis}

    INSTRUCTIONS:
    Systematically probe each of the 5 categories below. For each category,
    identify specific assumptions in the consensus that could be violated.

    CATEGORY 1: STATE VARIABLES
    - What state is implicitly assumed to persist between operations?
    - Are there initialization assumptions that could be violated?
    - Do agreed approaches assume state managed differently by variants?

    CATEGORY 2: GUARD CONDITIONS
    - What preconditions does the consensus implicitly rely on?
    - Are there missing null/empty/boundary checks?
    - Do guard conditions contradict assumptions elsewhere?

    CATEGORY 3: COUNT DIVERGENCE
    - Are loop bounds inclusive/exclusive consistently?
    - Do count calculations agree across consensus points?
    - Are there off-by-one risks?

    CATEGORY 4: COLLECTION BOUNDARIES
    - What happens when collections are empty?
    - Are single-element edge cases handled?
    - Are there implicit ordering/uniqueness assumptions?

    CATEGORY 5: INTERACTION EFFECTS
    - Do any two agreed changes interact in untested ways?
    - Are there ordering dependencies between changes?
    - Could combined changes from different variants conflict?

    OUTPUT FORMAT (one entry per finding):
    ID: INV-NNN
    CATEGORY: [state_variables|guard_conditions|count_divergence|collection_boundaries|interaction_effects]
    ASSUMPTION: [The specific assumption being probed]
    STATUS: [ADDRESSED|UNADDRESSED]
    SEVERITY: [HIGH|MEDIUM|LOW]
    EVIDENCE: [Specific reference to debate transcript or diff analysis supporting this finding]

  output_format:
    per_finding:
      id: "INV-NNN (sequential, starting from INV-001)"
      category: "One of: state_variables, guard_conditions, count_divergence, collection_boundaries, interaction_effects"
      assumption: "The specific invariant or assumption being probed"
      status: "ADDRESSED (consensus handles it) or UNADDRESSED (consensus does not handle it)"
      severity: "HIGH (correctness risk), MEDIUM (robustness risk), LOW (style/preference risk)"
      evidence: "Specific transcript/diff reference supporting the finding"

  acceptance_tests:
    AC_AD1_1:
      scenario: "Consensus has filter divergence (one variant filters before processing, other after)"
      expected: "Fault-finder identifies via state_variables or guard_conditions category"
    AC_AD1_2:
      scenario: "Consensus uses sentinel values that collide across components"
      expected: "Fault-finder identifies via collection_boundaries or interaction_effects category"
```

### invariant-probe.md Artifact Assembly (AD-1, D-0030)

```yaml
invariant_probe_assembly:
  output_path: "<output-dir>/adversarial/invariant-probe.md"
  trigger: "After Round 2.5 fault-finder agent completes (skipped if Round 2.5 skipped)"

  table_schema:
    columns:
      - name: "ID"
        format: "INV-NNN (sequential, starting from INV-001)"
        example: "INV-001"
      - name: "Category"
        format: "One of: state_variables, guard_conditions, count_divergence, collection_boundaries, interaction_effects"
        example: "state_variables"
      - name: "Assumption"
        format: "Free-text description of the probed invariant"
        example: "Filter is applied before data reaches processing stage"
      - name: "Status"
        format: "ADDRESSED or UNADDRESSED (exactly these values)"
        example: "UNADDRESSED"
      - name: "Severity"
        format: "HIGH, MEDIUM, or LOW (exactly these values)"
        example: "HIGH"
      - name: "Evidence"
        format: "Reference to debate transcript or diff analysis"
        example: "Round 2, Advocate-A rebuttal: no filter ordering discussed"

  assembly_algorithm:
    step_1: "Parse fault-finder agent output (structured INV-NNN findings)"
    step_2: "Validate each finding has all 6 fields (ID, Category, Assumption, Status, Severity, Evidence)"
    step_3: "Assign sequential IDs if agent output uses non-sequential numbering"
    step_4: "Validate Status values are exactly ADDRESSED or UNADDRESSED"
    step_5: "Validate Severity values are exactly HIGH, MEDIUM, or LOW"
    step_6: "Assemble markdown table with header row and one row per finding"
    step_7: "Append summary: total findings, counts by status, counts by severity"

  markdown_template: |
    # Invariant Probe Results

    ## Round 2.5 — Fault-Finder Analysis

    | ID | Category | Assumption | Status | Severity | Evidence |
    |----|----------|------------|--------|----------|----------|
    | INV-001 | {category} | {assumption} | {status} | {severity} | {evidence} |
    ...

    ## Summary

    - **Total findings**: {total}
    - **ADDRESSED**: {addressed_count}
    - **UNADDRESSED**: {unaddressed_count}
      - HIGH: {high_unaddressed}
      - MEDIUM: {medium_unaddressed}
      - LOW: {low_unaddressed}

  empty_probe_behavior: |
    If fault-finder finds zero violations:
    1. Create invariant-probe.md with empty table (header only)
    2. Summary: "Total findings: 0"
    3. This is a valid outcome — not all debates have invariant violations
```

### Round 3: Conditional Final Arguments (T03.04)

```yaml
round_3_conditional:
  condition: "--depth deep AND convergence < configured_threshold after Round 2"
  skip_conditions:
    not_deep: "--depth quick OR --depth standard → skip (log: 'Round 3 skipped: depth={depth}')"
    already_converged: "convergence ≥ threshold → skip (log: 'Round 3 skipped: convergence {N}% ≥ {threshold}%')"
  execution: "SEQUENTIAL — same order as Round 2"

  dispatch:
    per_advocate_input:
      - "All Round 1 and Round 2 transcripts"
      - "List of remaining unresolved disagreements"
    per_advocate_output:
      final_position: "Updated position incorporating all prior rounds"
      remaining_disagreements: "Points where advocate still disagrees, with final evidence"
      final_concessions: "Any additional concessions after full debate"

  post_round_3:
    convergence_check: "Final convergence measurement"
    if_not_converged: "Proceed with non-convergence → force-select by score (per FR-006)"
```

### Convergence Detection (T03.05)

```yaml
convergence_detection:
  metric: "Percentage of diff points where advocates agree on superior approach"
  formula: "convergence = agreed_points / total_diff_points"
  total_diff_points_calculation: |
    total_diff_points = count(S-NNN) + count(C-NNN) + count(X-NNN) + count(A-NNN)
    Note: A-NNN (shared assumption) points are included in the denominator (AD-2, D-0012).
    Debates without shared assumptions produce identical convergence scores (backward compatible).
  threshold:
    default: 0.80
    configurable: "--convergence flag (range 0.50-0.99)"
    validation: "If value outside range, warn and use default 0.80"

  per_point_tracking:
    data_structure:
      point_id: "Diff point ID (S-NNN, C-NNN, X-NNN, A-NNN)"
      taxonomy_level: "L1 | L2 | L3 (from debate_topic_taxonomy auto-tagging)"
      round_1_positions: "{variant_id: position}"
      round_2_positions: "{variant_id: position}"
      round_3_positions: "{variant_id: position}"
      agreed: "true/false"
      winner: "variant_id or null"

  taxonomy_coverage_gate:
    purpose: "AD-5: Ensure state-mechanics-level debate cannot be bypassed"
    check_timing: "After each debate round, before convergence assessment"
    algorithm: |
      1. Count diff points per taxonomy level: L1_count, L2_count, L3_count
      2. Check coverage: all three levels must have > 0 points addressed
      3. If any level has zero coverage:
         a. Block convergence regardless of score
         b. Trigger forced round for uncovered level
    gate_condition: "convergence requires: (all_levels_covered == true) AND (score >= threshold) AND (no_high_unaddressed_invariants == true)"
    forced_round_trigger:
      condition: "Any taxonomy level has zero coverage after a debate round"
      action: |
        1. Identify uncovered level(s)
        2. Dispatch forced debate round targeting the uncovered level
        3. Forced round uses level-specific prompt focusing on that level's concerns
        4. Still triggers at depth=quick when coverage is zero (AC-AD5-4)
      prompt_template: |
        FORCED ROUND: Taxonomy Level {level} has zero coverage.
        The debate has not addressed any {level_description} concerns.
        Please identify and debate at least one {level} issue from the diff analysis.
        Focus on: {level_auto_tag_signals}
      log: "Forced round triggered: {level} has zero coverage (AC-AD5-1)"

  agreement_determination:
    unanimous: "All advocates agree on same winner → agreed=true"
    majority: "≥2/3 of advocates agree → agreed=true (winner = majority choice)"
    split: "No majority → agreed=false (point remains unresolved)"

  early_termination_conditions:
    unanimous_agreement:
      condition: "All points have unanimous agreement AND all taxonomy levels covered"
      action: "Terminate debate immediately"
      log: "Convergence: 100% (unanimous)"

    stable_majority:
      condition: "≥threshold agreement maintained for 2 consecutive rounds AND all taxonomy levels covered"
      action: "Terminate debate"
      log: "Convergence: {N}% (stable majority over 2 rounds)"

    max_rounds:
      condition: "Maximum rounds reached for configured depth"
      action: "Terminate debate"
      log: "Convergence: {N}% (max rounds reached)"

    oscillation_detection:
      condition: "Same points flip winner between rounds without resolving"
      action: "Terminate debate with flag"
      log: "Convergence: {N}% (oscillation detected on points: {list})"

  invariant_probe_gate:
    purpose: "AD-1: Block convergence when HIGH-severity invariant violations remain unaddressed"
    check_timing: "After Round 2.5 invariant probe completes (skipped if Round 2.5 was skipped)"
    input: "invariant-probe.md table"
    algorithm: |
      1. Parse invariant-probe.md table
      2. Filter rows where Status == UNADDRESSED AND Severity == HIGH
      3. If count(HIGH + UNADDRESSED) > 0:
         a. Block convergence regardless of diff-point agreement score
         b. Report blocking items by INV-NNN ID
      4. Filter rows where Status == UNADDRESSED AND Severity == MEDIUM
      5. Log MEDIUM items as warnings (do NOT block convergence)
      6. LOW items: no action
    gate_condition: "convergence requires: count(HIGH + UNADDRESSED invariants) == 0"
    block_message: |
      CONVERGENCE BLOCKED: {count} HIGH-severity UNADDRESSED invariant(s) detected
      Blocking items: {inv_id_list}
      These invariant violations must be resolved before convergence can be declared.
      Action: Address the flagged items in a subsequent debate round or acknowledge as accepted risk.
    warning_message: |
      WARNING: {count} MEDIUM-severity UNADDRESSED invariant(s) detected
      Items: {inv_id_list}
      These items do not block convergence but should be reviewed.
    skipped_behavior: |
      When Round 2.5 is skipped (--depth quick):
      - Invariant probe gate is not applied
      - Convergence uses only diff-point and taxonomy gates

    acceptance_tests:
      AC_AD1_3:
        scenario: "90% diff-point agreement with 2 HIGH-severity UNADDRESSED items"
        expected: "Convergence BLOCKED — gate identifies both INV-NNN items as blocking"
      example_output: |
        CONVERGENCE BLOCKED: 2 HIGH-severity UNADDRESSED invariant(s) detected
        Blocking items: INV-003, INV-007
        These invariant violations must be resolved before convergence can be declared.

  status_output:
    CONVERGED: "Agreement ≥ threshold AND all taxonomy levels covered AND no HIGH unaddressed invariants"
    NOT_CONVERGED: "Agreement < threshold after max rounds"
    BLOCKED_BY_TAXONOMY: "Agreement ≥ threshold BUT taxonomy level {level} has zero coverage"
    BLOCKED_BY_INVARIANTS: "Agreement ≥ threshold AND taxonomy covered BUT HIGH-severity UNADDRESSED invariants exist"
```

### Per-Point Scoring Matrix (T03.06)

```yaml
scoring_matrix:
  purpose: "Record debate outcomes per diff point for base selection in Step 3"

  per_point_entry:
    diff_point_id: "From diff-analysis.md (S-NNN, C-NNN, X-NNN)"
    winner: "Variant whose approach is determined superior"
    confidence: "Percentage confidence in winner determination (calibrated, not all 50% or 100%)"
    evidence_summary: "Key evidence supporting the winner determination (≤2 sentences)"

  winner_determination:
    from_debate: "Extract from advocate positions, rebuttals, and concessions"
    unanimous: "If all advocates agree → winner with 90-100% confidence"
    majority: "If majority agrees → winner with 60-89% confidence"
    split: "If no majority → mark as unresolved with 50% confidence"
    concession_boost: "If losing advocate conceded the point → +10% confidence"

  confidence_calibration:
    rules:
      - "Never assign 100% unless ALL advocates explicitly conceded"
      - "Never assign <50% (that would indicate the other variant should win)"
      - "Scale with strength of evidence and degree of agreement"
    ranges:
      "90-100%": "Unanimous agreement with strong evidence"
      "70-89%": "Clear majority with supporting evidence"
      "50-69%": "Contested point with slight edge"

  output_format:
    table: |
      | Diff Point | Winner | Confidence | Evidence Summary |
      |------------|--------|------------|-----------------|
      | S-001 | Variant A | 85% | Stronger section hierarchy per Round 1 evidence |
      | C-001 | Variant B | 72% | More thorough coverage; Variant A advocate conceded |
```

### debate-transcript.md Artifact Assembly (T03.07)

```yaml
debate_transcript_assembly:
  output_path: "<output-dir>/adversarial/debate-transcript.md"

  assembly_order:
    1_metadata:
      content: |
        # Adversarial Debate Transcript
        ## Metadata
        - Depth: {configured_depth}
        - Rounds completed: {actual_rounds}
        - Convergence achieved: {convergence_percentage}%
        - Convergence threshold: {configured_threshold}%
        - Focus areas: {focus_areas or "All"}
        - Advocate count: {advocate_count}

    2_round_1:
      section: "## Round 1: Advocate Statements"
      content: "Full advocate statements per advocate_output_format"
      subsections: "### Variant N Advocate (<agent-spec>) for each advocate"

    3_round_2:
      condition: "Include only if Round 2 executed"
      section: "## Round 2: Rebuttals"
      content: "Full rebuttal content per round_2 output format"

    4_round_3:
      condition: "Include only if Round 3 executed"
      section: "## Round 3: Final Arguments"
      content: "Final positions per round_3 output format"

    5_scoring_matrix:
      section: "## Scoring Matrix"
      content: "Per-point scoring table from scoring_matrix output"

    6_convergence_assessment:
      section: "## Convergence Assessment"
      content: |
        - Points resolved: {resolved} of {total}
        - Alignment: {convergence_percentage}%
        - Threshold: {configured_threshold}%
        - Status: {CONVERGED | NOT_CONVERGED}
        - Unresolved points: {list of unresolved point IDs}

  validation:
    - "Metadata accurately reflects configured depth and actual rounds"
    - "All executed rounds have corresponding transcript sections"
    - "Scoring matrix covers every diff point from diff-analysis.md"
    - "Convergence assessment is mathematically consistent"
```

---

## Implementation Details — Step 3: Hybrid Scoring & Base Selection

### Quantitative Scoring Layer (T04.01)

5 deterministic metrics computed from artifact text (no LLM judgment):

```yaml
quantitative_scoring:
  metrics:
    requirement_coverage:
      symbol: "RC"
      weight: 0.30
      computation:
        step_1: "Extract requirement IDs from source input (FR-XXX, NFR-XXX, R-XXX patterns)"
        step_2: "For each requirement ID, grep-search the variant for matches"
        step_3: "Also keyword-match requirement descriptions (≥3 consecutive words = fuzzy match)"
        step_4: "RC = matched_requirements / total_source_requirements"
      edge_case: "If source has no formal requirement IDs, use section-level topic matching"

    internal_consistency:
      symbol: "IC"
      weight: 0.25
      computation:
        step_1: "Extract all scorable claims (specific, falsifiable statements)"
        step_2: "For each claim, search for contradicting claims within same variant"
        step_3: "Contradiction categories: opposing claims, requirement-constraint conflicts, impossible sequences"
        step_4: "IC = 1 - (contradiction_count / total_claims)"
      rule: "Vague statements ('as appropriate', 'as needed') are NOT scorable claims"
      reuse: "Leverages contradiction detection from Step 1 (T02.05)"

    specificity_ratio:
      symbol: "SR"
      weight: 0.15
      computation:
        concrete_indicators:
          - "Numbers and quantities ('5 milestones', '80% threshold')"
          - "Dates and timeframes ('2-week sprint', 'by Q3')"
          - "Named entities ('PostgreSQL', 'OAuth2', 'WCAG 2.1')"
          - "Specific thresholds ('<200ms', '≥99.9%')"
          - "Measurable criteria ('zero critical vulnerabilities')"
        vague_indicators:
          - "'appropriate', 'as needed', 'properly', 'adequate'"
          - "'should consider', 'might', 'various', 'etc.'"
          - "'best practices', 'industry standard' (without citation)"
        excluded: "Headings, boilerplate, metadata lines"
        formula: "SR = concrete_count / (concrete_count + vague_count)"

    dependency_completeness:
      symbol: "DC"
      weight: 0.15
      computation:
        step_1: "Scan for internal references (section refs, milestone refs, component refs)"
        step_2: "For each reference, check if the referenced item is defined elsewhere in the document"
        step_3: "DC = resolved_references / total_references"
      reference_patterns:
        - "Section X.Y references"
        - "Milestone M{N} references"
        - "Deliverable D{M}.{N} references"
        - "'See [section name]' cross-references"
      edge_case: "External references (URLs, other documents) are EXCLUDED"

    section_coverage:
      symbol: "SC"
      weight: 0.15
      computation:
        step_1: "Count top-level sections (H2 headings) in each variant"
        step_2: "Find max section count across all variants"
        step_3: "SC = variant_section_count / max_section_count"
      note: "Normalized so at least one variant always scores 1.0"

  formula: "quant_score = (RC × 0.30) + (IC × 0.25) + (SR × 0.15) + (DC × 0.15) + (SC × 0.15)"
  range: "[0.0, 1.0]"
  determinism: "Running twice on same input MUST produce identical scores"
```

### Qualitative Scoring Layer (T04.02)

30-criterion additive binary rubric with mandatory evidence citation across 6 dimensions:

```yaml
qualitative_scoring:
  rubric:
    completeness:
      criteria:
        1: "Covers all explicit requirements from source input"
        2: "Addresses edge cases and failure scenarios"
        3: "Includes dependencies and prerequisites"
        4: "Defines success/completion criteria"
        5: "Specifies what is explicitly out of scope"

    correctness:
      criteria:
        1: "No factual errors or hallucinated claims"
        2: "Technical approaches are feasible with stated constraints"
        3: "Terminology used consistently and accurately throughout"
        4: "No internal contradictions (cross-validated with IC metric)"
        5: "Claims supported by evidence or rationale within the document"

    structure:
      criteria:
        1: "Logical section ordering (prerequisites before dependents)"
        2: "Consistent hierarchy depth (no orphaned subsections)"
        3: "Clear separation of concerns between sections"
        4: "Navigation aids present (table of contents, cross-references, or index)"
        5: "Follows conventions of the artifact type"

    clarity:
      criteria:
        1: "Unambiguous language (no 'should consider', 'might', 'as appropriate')"
        2: "Concrete rather than abstract (specific actions, not general principles)"
        3: "Each section has a clear purpose or can be summarized in one sentence"
        4: "Acronyms and domain terms defined on first use"
        5: "Actionable next steps or decision points clearly identified"

    risk_coverage:
      criteria:
        1: "Identifies at least 3 risks with probability and impact assessment"
        2: "Provides mitigation strategy for each identified risk"
        3: "Addresses failure modes and recovery procedures"
        4: "Considers external dependencies and their failure scenarios"
        5: "Includes monitoring or validation mechanism for risk detection"

    invariant_edge_case_coverage:
      criteria:
        1: "Addresses boundary conditions for collections (empty, single-element, maximum size)"
        2: "Handles state variable interactions across component boundaries"
        3: "Identifies guard condition gaps (missing validation, unguarded type assumptions)"
        4: "Covers count divergence scenarios (off-by-one, inclusive/exclusive ranges)"
        5: "Considers interaction effects when features or components combine"
      floor_rule:
        threshold: "1/5"
        enforcement: "Variants scoring <1/5 on this dimension are ineligible as base variant"
        suspension: "When ALL variants score 0/5, suspend floor with warning: 'Edge case floor suspended: no variant meets minimum coverage'"
        rationale: "Prevents selecting a base variant with zero invariant awareness"

  evidence_protocol:
    name: "Claim-Evidence-Verdict (CEV)"
    format: |
      CLAIM:    "[Criterion description] is met/not met in Variant X"
      EVIDENCE: "[Direct quote or section reference from the variant]"
                OR "No evidence found — searched sections [list]"
      VERDICT:  MET (1 point) | NOT MET (0 points)
    rules:
      - "No partial credit: each criterion is 1 (MET) or 0 (NOT MET)"
      - "If evaluator cannot cite specific evidence for MET → defaults to NOT MET"
      - "This prevents hallucinated quality assessments"
      - "Every MET verdict MUST include a specific evidence citation"

  formula: "qual_score = total_criteria_met / 30"
  range: "[0.0, 1.0]"
```

### Position-Bias Mitigation (T04.03)

```yaml
position_bias_mitigation:
  purpose: "Eliminate systematic position bias in LLM-as-judge evaluation"

  dual_pass_execution:
    pass_1:
      order: "Evaluate variants in input order (A, B, C, ...)"
      evaluation: "Full 25-criterion qualitative rubric with CEV"
    pass_2:
      order: "Evaluate variants in REVERSE order (..., C, B, A)"
      evaluation: "Same 25-criterion rubric with CEV (independent evaluation)"
    parallelism: "Pass 1 and Pass 2 CAN execute in parallel for efficiency"

  disagreement_resolution:
    per_criterion_per_variant:
      both_agree: "Use the agreed verdict (MET or NOT MET)"
      passes_disagree:
        action: "Re-evaluate with explicit comparison prompt"
        prompt: |
          Two independent evaluations disagree on this criterion for this variant.
          Pass 1 evidence: {pass_1_evidence}
          Pass 1 verdict: {pass_1_verdict}
          Pass 2 evidence: {pass_2_evidence}
          Pass 2 verdict: {pass_2_verdict}

          Re-evaluate this criterion with both pieces of evidence.
          Your verdict is FINAL.
        verdict: "Re-evaluation result is the final verdict (no further appeals)"

  output:
    log_format: |
      | Criterion | Variant | Pass 1 | Pass 2 | Agreement | Final |
      |-----------|---------|--------|--------|-----------|-------|
    metrics:
      disagreements_found: "Count of criterion-variant pairs where passes disagreed"
      verdicts_changed: "Count where re-evaluation changed the verdict from either pass"
```

### Combined Scoring & Tiebreaker (T04.04, T04.05)

```yaml
combined_scoring:
  formula: "variant_score = (0.50 × quant_score) + (0.50 × qual_score)"
  range: "[0.0, 1.0]"
  ranking: "Sort variants by combined score, highest first"
  base_selection: "Highest-scoring variant is selected as base"

tiebreaker_protocol:
  trigger: "|score_A - score_B| < 0.05 for top two variants"

  level_1_debate_performance:
    metric: "Count of diff points won in Step 2 scoring matrix"
    winner: "Variant with more diff points won"
    tie_check: "If also within 5% of each other → proceed to Level 2"

  level_2_correctness_count:
    metric: "Number of correctness criteria scored MET in qualitative layer"
    winner: "Variant with higher correctness count"
    rationale: "Correctness is most valuable for hallucination detection"
    tie_check: "If identical → proceed to Level 3"

  level_3_input_order:
    rule: "Variant presented first in input order is selected"
    rationale: "Arbitrary but deterministic — ensures reproducible results"

  output:
    margin: "Score difference as percentage"
    tiebreaker_applied: "Yes (level N) or No"
    evidence: "Which metric determined the winner"
```

### base-selection.md Artifact Assembly (T04.06)

```yaml
base_selection_assembly:
  output_path: "<output-dir>/adversarial/base-selection.md"

  assembly_order:
    1_quantitative_scoring:
      section: "## Quantitative Scoring (50% weight)"
      content: "Per-metric scores with computation details per variant"
      format: "Table with metric, weight, and score per variant"

    2_qualitative_scoring:
      section: "## Qualitative Scoring (50% weight) — Additive Binary Rubric"
      subsections:
        - "### Completeness (5 criteria) — per-variant CEV table"
        - "### Correctness (5 criteria)"
        - "### Structure (5 criteria)"
        - "### Clarity (5 criteria)"
        - "### Risk Coverage (5 criteria)"
        - "### Invariant & Edge Case Coverage (5 criteria)"
        - "### Qualitative Summary — dimension subtotals per variant"
        - "### Edge Case Floor Check — per-variant eligibility status"

    3_position_bias:
      section: "## Position-Bias Mitigation"
      content: "Dual-pass results with disagreement resolution log"

    4_combined_scoring:
      section: "## Combined Scoring"
      content: "Quant weighted + qual weighted + final score + tiebreaker per variant"
      includes: "Margin analysis and tiebreaker application status"

    5_selected_base:
      section: "## Selected Base: Variant <X> (<agent-spec>)"
      content:
        selection_rationale: "Evidence-based explanation of why this variant won"
        strengths_to_preserve: "Strengths to keep from base variant"
        strengths_to_incorporate: "Specific strengths from non-base variants to merge"
```

---

## Implementation Details — Steps 4-5: Refactoring Plan & Merge Execution

### Refactoring Plan Generation (T05.01)

```yaml
refactoring_plan:
  input:
    base_variant: "Selected base from Step 3"
    non_base_variants: "All other variants"
    debate_transcript: "debate-transcript.md for evidence"
    base_selection: "base-selection.md for identified strengths/weaknesses"

  plan_generation:
    for_each_non_base_strength:
      source: "base-selection.md 'Strengths to Incorporate' section"
      per_strength:
        title: "Descriptive title for the change"
        source_variant: "Which variant and section contains the strength"
        target_location: "Where it integrates into the base (section ref)"
        integration_approach: "replace | append | insert | restructure"
        rationale: "Debate evidence supporting incorporation (cite round, point, confidence)"
        risk_level: "Low (additive) | Medium (modifies existing) | High (restructures)"

    for_each_base_weakness:
      source: "Debate criticisms where base lost the point"
      per_weakness:
        issue: "What was identified as weak in the base"
        better_variant: "Which non-base variant addresses it"
        fix_approach: "How to address the weakness"

    changes_not_being_made:
      purpose: "Transparency — document what was considered and rejected"
      per_rejected_change:
        diff_point: "Which diff point ID"
        non_base_approach: "What the non-base variant proposed"
        rationale: "Why the base approach was determined superior (cite debate evidence)"

  review:
    default: "Auto-approved (pipeline continues immediately)"
    interactive: "When --interactive: pause for user review via AskUserQuestion"
    approval_status: "auto-approved | user-approved"
    timestamp: "ISO-8601 approval timestamp"
```

### Interactive Mode Checkpoints (T05.02)

```yaml
interactive_checkpoints:
  activation: "--interactive flag must be set"
  default_behavior: "Non-interactive — all decisions auto-resolved with rationale documented"

  checkpoint_1_after_diff_analysis:
    trigger: "diff-analysis.md produced"
    pause_action: |
      Present diff-analysis summary to user via AskUserQuestion:
      "Diff analysis complete. {N} structural, {N} content, {N} contradictions, {N} unique contributions found.
       Would you like to highlight priority areas for debate?"
    options:
      proceed: "Continue with all diff points"
      prioritize: "User specifies focus areas → filter debate to selected points"
    default: "Auto-proceed with all diff points"

  checkpoint_2_after_debate:
    trigger: "debate-transcript.md produced"
    pause_action: |
      Present convergence summary via AskUserQuestion:
      "Debate complete. Convergence: {N}%. {resolved}/{total} points resolved.
       Would you like to override the convergence assessment?"
    options:
      accept: "Accept computed convergence"
      override: "User adjusts convergence or marks specific points as resolved"
    default: "Accept computed convergence"

  checkpoint_3_after_base_selection:
    trigger: "base-selection.md produced"
    pause_action: |
      Present selection via AskUserQuestion:
      "Base selected: Variant {X} ({spec}) with score {score}.
       Runner-up: Variant {Y} ({spec}) with score {score}. Margin: {N}%.
       Would you like to override the base selection?"
    options:
      accept: "Accept selected base"
      override: "User selects a different base"
    default: "Accept highest-scoring variant"

  checkpoint_4_after_refactoring_plan:
    trigger: "refactor-plan.md produced"
    pause_action: |
      Present plan summary via AskUserQuestion:
      "Refactoring plan: {N} changes planned, {N} rejected.
       Risk: {Low/Medium/High} overall.
       Would you like to modify the plan before execution?"
    options:
      approve: "Execute plan as-is"
      modify: "User adds/removes/modifies planned changes"
    default: "Auto-approve and execute"

  override_documentation:
    rule: "ALL user overrides are documented in the relevant output artifact"
    format: "Approval: user-overridden | Auto-approved"
```

### Merge Executor Dispatch (T05.03)

```yaml
merge_execution:
  dispatch:
    agent: "merge-executor (defined in agents/merge-executor.md)"
    via: "Task tool"
    model: "opus or sonnet (highest available)"
    input:
      base_variant: "Full text of selected base variant"
      refactoring_plan: "Full text of refactor-plan.md"
    max_turns: 10

  executor_process:
    step_1: "Read base variant and refactoring plan"
    step_2: "Apply each planned change in plan order"
    step_3: "Maintain structural integrity (heading hierarchy, section flow)"
    step_4: "Add provenance annotations per provenance_system"
    step_5: "Run post-merge validation checks"
    step_6: "Produce merge-log.md documenting each applied change"

  output_collection:
    merged_document: "Unified merged artifact"
    merge_log: "Per-change execution log"
    validation_results: "Structural integrity, references, contradictions"

  failure_handling:
    executor_failure:
      action: "Preserve all artifacts (base + plan + partial merge if any)"
      status: "Return status='failed' in return contract"
      recovery: "Provide refactor-plan.md for manual execution"
```

### Provenance Annotation System (T05.04)

```yaml
provenance_system:
  purpose: "Track which source contributed each section of merged output"

  document_header:
    format: |
      <!-- Provenance: This document was produced by /sc:adversarial -->
      <!-- Base: Variant {X} ({agent-spec}) -->
      <!-- Merge date: {ISO-8601 timestamp} -->

  per_section_tags:
    base_original: "<!-- Source: Base (original) -->"
    base_modified: "<!-- Source: Base (original, modified) — {reason} -->"
    incorporated: "<!-- Source: Variant {N} ({agent-spec}), Section {ref} — merged per Change #{N} -->"

  rules:
    - "Every section or significant block includes a <!-- Source: ... --> tag"
    - "Tags identify the variant, section reference, and change number (if applicable)"
    - "Original base content tagged as 'Base (original)'"
    - "Modified base content tagged as 'Base (original, modified)' with reason"
    - "Incorporated content tagged with source variant and change reference"
    - "Annotations are HTML comments — invisible in rendered markdown"
```

### Post-Merge Consistency Validation (T05.05)

```yaml
post_merge_validation:
  checks:
    structural_integrity:
      action: "Validate heading hierarchy is consistent"
      rules:
        - "No heading level gaps (e.g., H2 → H4 without H3)"
        - "No orphaned subsections (H3 without parent H2)"
        - "Document starts with H1 or H2"
        - "Section ordering is logical (prerequisites before dependents)"
      output: "✅ Pass or ❌ Fail with details"

    internal_references:
      action: "Validate all cross-references resolve"
      process:
        - "Scan for 'See [section]', 'Section X.Y', 'Milestone M{N}' references"
        - "For each reference, verify the target exists in the merged document"
        - "Count total, resolved, and broken references"
      output: "Total: {N}, Resolved: {N}, Broken: {N} [list if any]"

    contradiction_rescan:
      action: "Scan merged document for NEW contradictions introduced by merge"
      process:
        - "Run contradiction detection (same logic as T02.05) on merged document"
        - "Compare against pre-merge contradiction list"
        - "Flag only NEW contradictions not present in original variants"
      output: "New contradictions introduced: {N} [details if any]"

  failure_handling:
    any_check_fails:
      action: "Preserve all artifacts, flag failure in merge-log.md"
      status: "Return status='partial' in return contract"
      recovery: "Merged output available but flagged; user should review"
```

### Artifact Assembly — refactor-plan.md & merge-log.md (T05.06)

```yaml
artifact_assembly_step_5:
  refactor_plan:
    output_path: "<output-dir>/adversarial/refactor-plan.md"
    template: "See refs/artifact-templates.md Section 4"
    sections:
      - "## Overview (base variant, incorporated variants, change count, risk)"
      - "## Planned Changes (per-change entries with source, target, rationale, risk)"
      - "## Changes NOT Being Made (rejected alternatives with rationale)"
      - "## Risk Summary (per-change risk with impact and rollback)"
      - "## Review Status (auto-approved or user-approved)"

  merge_log:
    output_path: "<output-dir>/adversarial/merge-log.md"
    template: "See refs/artifact-templates.md Section 5"
    sections:
      - "## Metadata (base, executor, changes applied, status, timestamp)"
      - "## Changes Applied (per-change: status, before/after, provenance tag, validation)"
      - "## Post-Merge Validation (structural, references, contradictions)"
      - "## Summary (planned vs applied vs failed vs skipped)"
```

### Return Contract (T05.07)

```yaml
return_contract:
  purpose: "Enable programmatic integration with other commands (sc:roadmap, sc:design)"

  fields:
    merged_output_path:
      type: "string"
      content: "Absolute or relative path to the merged output file"

    convergence_score:
      type: "float"
      content: "Final convergence percentage from debate (0.0-1.0)"

    artifacts_dir:
      type: "string"
      content: "Path to the adversarial/ directory containing all process artifacts"

    status:
      type: "enum"
      values:
        success: "All 5 steps completed, post-merge validation passed"
        partial: "Pipeline completed but with warnings or validation failures"
        failed: "Pipeline aborted — check artifacts for recovery"

    unresolved_conflicts:
      type: "list[string]"
      content: "List of diff point IDs where no resolution was reached"
      empty_when: "status == 'success' and convergence ≥ threshold"

  status_determination:
    success: "All steps complete AND post-merge validation passes AND no critical errors"
    partial: "Steps completed but validation failures OR non-convergence OR skipped debate"
    failed: "Pipeline aborted (insufficient variants, agent failures, merge failure)"

  integration_pattern:
    sc_roadmap_v2:
      multi_spec: |
        Multiple spec documents → generate one roadmap per spec via different agents → adversarial merge.
        Invocation: /sc:adversarial --compare roadmap-from-spec1.md,roadmap-from-spec2.md --depth standard
        Use case: Compare roadmaps derived from different source specifications.
        Return: merged_output_path contains the best-of-breed roadmap.

      multi_roadmap: |
        One spec → generate multiple roadmap variants via different agent configurations → adversarial merge.
        Invocation: /sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security,haiku:analyzer
        Use case: Get diverse perspectives on a single spec, merge the strongest elements.
        Return: merged_output_path contains the consensus roadmap; convergence_score indicates agreement level.

      combined: |
        Multiple specs + multiple agents → full adversarial pipeline.
        Workflow: For each spec, generate variants via --agents. Then adversarial-merge all variants.
        Invocation: Run Mode B for each spec, collect outputs, then run Mode A on all outputs.
        Return: Final merged_output_path is the comprehensive, multi-perspective roadmap.

    generic_integration: |
      Any command can invoke Skill sc:adversarial-protocol and consume the return contract:
      1. Invoke Skill sc:adversarial-protocol with appropriate flags
      2. Read return contract fields: merged_output_path, convergence_score, status
      3. If status == 'success': use merged_output_path as the final artifact
      4. If status == 'partial': use merged_output_path but flag unresolved_conflicts for review
      5. If status == 'failed': fall back to manual selection from artifacts_dir contents
```

---

## Implementation Details — Step 6: Integration, Polish & Validation

### Error Handling Matrix (T06.01)

```yaml
error_handling_matrix:
  agent_failure:
    detection: "Task agent returns error or times out"
    behavior:
      step_1: "Retry failed agent once with same inputs"
      step_2: "If retry fails, proceed with N-1 advocates"
      step_3: "If fewer than 2 advocates remain → ABORT debate"
    constraint: "Minimum 2 variants required at all times"
    log: "Agent failure logged in debate-transcript.md metadata"

  variants_too_similar:
    detection: "diff-analysis.md total differences < 10% of total comparable items"
    behavior:
      step_1: "Log 'variants substantially identical'"
      step_2: "Skip debate (Steps 2-3)"
      step_3: "Select either variant as base (first in input order)"
      step_4: "Proceed directly to merge (Steps 4-5) with minimal changes"
    log: "Similarity skip logged in merge-log.md"

  no_convergence:
    detection: "Max rounds reached without meeting convergence threshold"
    behavior:
      step_1: "Force-select by combined score"
      step_2: "Document non-convergence in debate-transcript.md"
      step_3: "Flag for user review (include in return contract unresolved_conflicts)"
    status: "Return status='partial'"

  merge_failure:
    detection: "Merge executor fails or produces invalid output"
    behavior:
      step_1: "Preserve ALL artifacts (base, plan, partial merge if any)"
      step_2: "Set return status='failed'"
      step_3: "Provide refactor-plan.md for manual execution"
    recovery: "User can manually apply refactor-plan.md to base variant"

  single_variant_remaining:
    detection: "Only 1 variant available (after failures or invalid input)"
    behavior:
      step_1: "Abort adversarial process entirely"
      step_2: "Return surviving variant as-is"
      step_3: "Log warning: 'Adversarial comparison requires minimum 2 variants'"
    status: "Return status='failed' with warning"
```

### Mode B Variant Generation (T06.02)

```yaml
mode_b_generation:
  activation: "Mode B detected (--source + --generate + --agents)"

  parallel_dispatch:
    action: "For each agent spec, spawn Task agent to generate variant"
    parallelism: "ALL agents dispatched simultaneously (true parallel)"
    per_agent:
      input:
        source_file: "Content of --source file"
        generation_type: "Value of --generate flag (e.g., roadmap, spec, design)"
        agent_spec: "Parsed agent specification (model, persona, instruction)"
      prompt: |
        Generate a {generation_type} artifact from the following source material.
        Use your expertise as {persona or 'a general-purpose analyst'} to produce
        the highest-quality {generation_type} possible.
        {instruction or ''}

        Source material:
        {source_file_content}

  result_collection:
    naming: "variant-{N}-{model}-{persona or 'default'}.md"
    storage: "<output-dir>/adversarial/"
    validation:
      - "Each variant is non-empty"
      - "Each variant is valid markdown"
      - "At least 2 variants successfully generated"

  pipeline_wiring:
    action: "Feed generated variants into the Step 1 diff analysis pipeline"
    entry_point: "Same as Mode A after variant loading (T02.02+)"
```

### MCP Integration Layer (T06.03)

```yaml
mcp_integration:
  sequential:
    usage: "Debate scoring, convergence analysis, refactoring plan logic"
    steps: "Steps 2-4"
    circuit_breaker:
      failure_threshold: 3
      timeout: "30s"
      fallback: "Native Claude reasoning with depth reduction"
      depth_reduction: "deep → standard, standard → quick"

  serena:
    usage: "Memory persistence of adversarial outcomes"
    steps: "Step 5 (post-merge)"
    data_persisted:
      - "Pipeline configuration and outcome summary"
      - "Scoring results for cross-session learning"
      - "Error patterns for improvement"
    circuit_breaker:
      failure_threshold: 4
      timeout: "45s"
      fallback: "Skip persistence, log warning"

  context7:
    usage: "Domain pattern validation during merge"
    steps: "Step 5 (merge validation)"
    validation_areas:
      - "Artifact type conventions (e.g., roadmap structure patterns)"
      - "Best practices for the generation type"
    circuit_breaker:
      failure_threshold: 5
      timeout: "60s"
      fallback: "Skip domain validation, rely on structural checks only"
```

### Framework Registration (T06.04)

Update framework configuration files for routing and auto-activation:

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

    additional_entries:
      - pattern: "compare variants"
        auto_activates: "analyzer persona, --think-hard, Sequential"
        confidence: "90%"
      - pattern: "merge best of"
        auto_activates: "architect persona, --think, Sequential"
        confidence: "85%"
```

---

## Meta-Orchestrator: Pipeline Mode

<!-- Meta-Orchestrator: Pipeline definition parsing, DAG construction, phase execution, artifact routing, and pipeline control.
     This section is the routing target for step_0_pipeline_guard when --pipeline flag is detected.
     Track A deliverables: D-0005 through D-0010 (M2), D-0020 through D-0027 (M4). -->

When `--pipeline` is detected by `step_0_pipeline_guard`, execution routes here. The Meta-Orchestrator parses the pipeline definition (inline shorthand or YAML file), builds a DAG, validates it, and either renders a dry-run plan or executes phases sequentially/in-parallel.

### Pipeline Definition Parsing

Two input formats are supported. Both produce the same structured phase list output.

#### Inline Shorthand Parser (D-0005)

Parses `--pipeline "<shorthand>"` syntax into a structured phase list.

```yaml
inline_shorthand_parser:
  grammar:
    tokens:
      ARROW: "->"           # Sequential dependency (left must complete before right)
      PIPE: "|"             # Parallel grouping (phases at same dependency level)
      GENERATE: "generate:" # Generate phase type, followed by agent spec list
      COMPARE: "compare"    # Compare phase type (no agents required)
      AGENT_LIST: "<agent_spec>[,<agent_spec>,...]"  # Comma-separated agent specs
      PHASE_ID: "[a-zA-Z_][a-zA-Z0-9_]*"  # Alphanumeric identifier for a phase

    syntax: |
      pipeline     ::= phase_group ( '->' phase_group )*
      phase_group  ::= phase ( '|' phase )*
      phase        ::= PHASE_ID ':' phase_type
                      | phase_type
      phase_type   ::= 'generate:' AGENT_LIST
                      | 'compare'

    examples:
      simple_3phase: |
        generate:opus:architect,haiku:architect -> generate:opus:security,haiku:security -> compare
        # Phase 1: generate with opus:architect and haiku:architect
        # Phase 2: generate with opus:security and haiku:security (depends on Phase 1)
        # Phase 3: compare (depends on Phase 2)

      parallel_generate: |
        generate:opus:architect,haiku:architect | generate:opus:security,haiku:security -> compare
        # Phase 1a: generate with opus:architect,haiku:architect (parallel with 1b)
        # Phase 1b: generate with opus:security,haiku:security (parallel with 1a)
        # Phase 2: compare (depends on both 1a and 1b)

      named_phases: |
        arch:generate:opus:architect,haiku:architect -> sec:generate:opus:security -> final:compare
        # Named phases for readability and depends_on references

  tokenizer:
    step_1: "Split input on whitespace-padded '->' to get phase groups"
    step_2: "Split each phase group on whitespace-padded '|' to get parallel phases"
    step_3: "For each phase, extract optional name (before ':'), phase type, and agent list"
    step_4: "Validate each token against grammar rules"

  parser_output:
    format: "Structured phase list (identical to YAML loader output)"
    schema:
      phases:
        - id: "Auto-assigned (phase_1, phase_2, ...) or user-named"
          type: "generate | compare"
          agents: ["agent_spec_1", "agent_spec_2"]  # Empty for compare
          depends_on: ["phase_id_1", ...]            # Derived from '->' ordering
          parallel_group: 0                           # Phases with same group run concurrently

  error_handling:
    missing_arrow: "STOP: 'Malformed shorthand: expected -> between phase groups, got: <token>'"
    unmatched_pipe: "STOP: 'Malformed shorthand: unmatched | in phase group: <group>'"
    unknown_type: "STOP: 'Unknown phase type: <type>. Expected generate:<agents> or compare'"
    empty_agents: "STOP: 'generate phase requires at least one agent: generate:<agent_spec>'"
    duplicate_name: "STOP: 'Duplicate phase name: <name>. Each phase must have a unique identifier'"
```

#### YAML Pipeline File Loader (D-0006)

Parses `--pipeline @path.yaml` into the same structured phase list.

```yaml
yaml_pipeline_loader:
  trigger: "--pipeline value starts with '@'"
  file_resolution: "Strip leading '@', resolve path relative to working directory"

  schema:
    required_top_level:
      phases: "Array of phase definitions (required)"

    per_phase_fields:
      required:
        type: "string — 'generate' or 'compare'"
      optional:
        id: "string — unique phase identifier (auto-assigned if absent)"
        agents: "array of strings — agent specs (required for generate, forbidden for compare)"
        depends_on: "array of strings — phase IDs this phase depends on"
        config: "object — phase-specific configuration overrides"

    config_fields:
      depth: "string — quick/standard/deep (overrides global --depth for this phase)"
      convergence: "number — 0.50-0.99 (overrides global --convergence)"
      output: "string — output path override for this phase"

  schema_validation:
    unknown_fields: "STOP: 'Unknown field in phase definition: <field>. Allowed: id, type, agents, depends_on, config'"
    missing_required: "STOP: 'Missing required field in phase definition: type'"
    type_invalid: "STOP: 'Invalid phase type: <value>. Must be generate or compare'"
    agents_on_compare: "STOP: 'compare phase must not specify agents'"
    no_agents_on_generate: "STOP: 'generate phase requires agents field with at least one agent spec'"
    empty_phases: "STOP: 'Pipeline must contain at least one phase'"

  example_yaml: |
    # 3-phase canonical pipeline
    phases:
      - id: arch_gen
        type: generate
        agents: ["opus:architect", "haiku:architect"]
      - id: sec_gen
        type: generate
        agents: ["opus:security", "haiku:security"]
        depends_on: ["arch_gen"]
      - id: final_compare
        type: compare
        depends_on: ["sec_gen"]

  output: "Structured phase list (identical schema to inline parser output)"
```

### DAG Builder (D-0007)

Constructs a directed acyclic graph from the structured phase list, identifying parallel phase groups and sequential gates.

```yaml
dag_builder:
  input: "Structured phase list from inline parser or YAML loader"

  construction:
    step_1_create_nodes:
      action: "Create one node per phase definition"
      node_schema:
        id: "Phase ID (auto-assigned or user-named)"
        type: "generate | compare"
        agents: "Agent spec list (empty for compare)"
        config: "Phase-specific configuration overrides"
        level: "Dependency level (assigned in step 3)"

    step_2_create_edges:
      action: "Create directed edges from depends_on references"
      edge_schema:
        from: "Dependency phase ID (must complete first)"
        to: "Dependent phase ID (waits for from)"
      implicit_edges: |
        If no explicit depends_on and phases are separated by '->':
        each phase group depends on the previous group.

    step_3_assign_levels:
      action: "Topological sort to assign dependency levels"
      algorithm: "Kahn's algorithm (BFS-based topological sort)"
      level_assignment: |
        Phases with no dependencies: level 0
        Phases depending only on level-N phases: level N+1
      parallelization: "Phases at the same level can execute concurrently"

  validation:
    cycle_detection: "See Cycle Detection section below"
    reference_integrity: "See Reference Integrity Validation section below"

  output_schema:
    nodes: "Array of phase nodes with assigned levels"
    edges: "Array of directed edges (from -> to)"
    levels: "Array of arrays — phases grouped by dependency level"
    execution_order: "Flattened topological order for sequential execution"

  serialization:
    format: "YAML-compatible structure for dry-run output and manifest consumption"
    example: |
      dag:
        nodes:
          - {id: arch_gen, type: generate, level: 0}
          - {id: sec_gen, type: generate, level: 1}
          - {id: final_compare, type: compare, level: 2}
        edges:
          - {from: arch_gen, to: sec_gen}
          - {from: sec_gen, to: final_compare}
        levels:
          - [arch_gen]
          - [sec_gen]
          - [final_compare]
```

### Cycle Detection (D-0008)

Detects circular dependencies during DAG construction and reports the exact cycle path.

```yaml
cycle_detection:
  integration_point: "Runs during dag_builder.step_3_assign_levels, before level assignment"
  algorithm: "DFS-based cycle detection with path tracking"

  implementation:
    step_1: "Initialize all nodes as UNVISITED"
    step_2: "For each UNVISITED node, start DFS traversal"
    step_3: "Mark entering node as IN_PROGRESS"
    step_4: "For each neighbor (depends_on target), check state:"
    step_4a: "  IN_PROGRESS → cycle detected, extract cycle path"
    step_4b: "  UNVISITED → recurse"
    step_4c: "  VISITED → skip (already processed)"
    step_5: "Mark exiting node as VISITED"

  error_reporting:
    format: "Circular dependency detected: {path}"
    example_short: "Circular dependency detected: A -> B -> A"
    example_long: "Circular dependency detected: A -> B -> C -> A"
    action: "STOP pipeline execution immediately — no phases are executed"

  timing: "Must complete before any phase execution begins"
```

### Reference Integrity Validation (D-0009)

Validates that all `depends_on` phase IDs reference existing phases in the phase list.

```yaml
reference_integrity:
  integration_point: "Runs during dag_builder.step_2_create_edges, before cycle detection"
  algorithm: "Collect all phase IDs into a set, then check each depends_on reference"

  implementation:
    step_1: "Build set of all defined phase IDs from structured phase list"
    step_2: "For each phase, check each depends_on entry against the ID set"
    step_3: "Collect ALL invalid references (do not fail-fast on first)"
    step_4: "If any invalid references found, report all in a single error"

  error_reporting:
    single: "Unknown phase reference: <id>"
    multiple: "Unknown phase references: <id1>, <id2>"
    action: "STOP pipeline execution — report all invalid references before stopping"

  valid_pass: "Phases with correct depends_on references pass without error output"
```

### Dry-Run Render (D-0010)

Validates the DAG and outputs the execution plan without executing any phases.

```yaml
dry_run:
  trigger: "--dry-run flag present (in combination with --pipeline)"
  alias: "--pipeline-dry-run"

  implementation:
    step_1: "Parse pipeline definition (inline or YAML)"
    step_2: "Build DAG (includes cycle detection and reference integrity)"
    step_3: "Render execution plan to output"
    step_4: "Exit without executing any phases"

  output_format:
    sections:
      pipeline_summary:
        content: |
          # Pipeline Execution Plan (Dry Run)
          - Total phases: <N>
          - Parallel groups: <N>
          - Estimated execution levels: <N>

      phase_table:
        columns: ["Phase ID", "Type", "Agents", "Depends On", "Level", "Parallel Group"]
        content: "One row per phase from DAG nodes"

      execution_order:
        content: |
          ## Execution Order
          Level 0: <phase_ids> (parallel)
          Level 1: <phase_ids> (parallel)
          ...

      estimated_costs:
        content: |
          ## Estimated Token Costs
          - generate phases: ~<N> tokens each (based on agent count and depth)
          - compare phases: ~<N> tokens each (based on variant count)
          - Total estimated: ~<N> tokens

  output_routing:
    default: "Console (stdout)"
    file: "--output <path> writes to file instead of console"

  validation_guarantee: |
    If dry-run completes without error, the pipeline definition is valid:
    - All phase types are recognized
    - All depends_on references are valid
    - No circular dependencies exist
    - DAG can be constructed and topologically sorted
```

### Phase Execution Engine (M4)

Phase Executor, artifact routing, parallel scheduling, pipeline manifest, resume, blind evaluation, plateau detection, and error policies.

#### Phase Executor (D-0020)

Translates each phase configuration into a Mode A (compare) or Mode B (generate) invocation, scoped to an isolated phase output directory.

```yaml
phase_executor:
  purpose: "Core runtime: translate phase config to Mode A/B invocation with output isolation"

  translation_rules:
    generate_phase:
      maps_to: "Mode B invocation"
      parameters:
        source: "Inherited from --source or upstream phase merged_output"
        generate: "Inherited from pipeline config or phase-level override"
        agents: "From phase definition agents field"
        depth: "From phase config.depth or global --depth"
        convergence: "From phase config.convergence or global --convergence"
      invocation: "--source <input> --generate <type> --agents <agent_list>"

    compare_phase:
      maps_to: "Mode A invocation"
      parameters:
        compare: "All variant outputs from dependency phases (resolved by artifact routing)"
        depth: "From phase config.depth or global --depth"
        convergence: "From phase config.convergence or global --convergence"
      invocation: "--compare <variant_1>,<variant_2>[,...<variant_N>]"

  output_isolation:
    directory_structure: "<pipeline_output>/<phase_id>/"
    creation: "Directory created before phase execution begins"
    scoping: "All phase artifacts written to isolated directory"
    example: |
      pipeline_output/
        phase_1/
          variant-opus-architect.md
          variant-haiku-architect.md
          diff-analysis.md
          debate-transcript.md
          merged-output.md
        phase_2/
          variant-opus-security.md
          variant-haiku-security.md
          ...
        phase_3/
          merged-output.md

  execution_flow:
    step_1: "Read phase config (type, agents, dependencies, overrides)"
    step_2: "Resolve input artifacts from dependency phases via artifact routing"
    step_3: "Create isolated output directory: <pipeline_output>/<phase_id>/"
    step_4: "Translate phase type to Mode A or Mode B parameters"
    step_5: "Execute Mode A/B with phase-specific parameters and output directory"
    step_6: "Collect return contract from Mode A/B execution"
    step_7: "Update pipeline manifest with phase results"

  acceptance_test:
    scenario: '--pipeline "generate:opus:architect" produces identical output to direct Mode B'
    verification: "Single-phase pipeline output matches direct Mode B invocation"
```

#### Artifact Routing (D-0021)

Resolves `merged_output` and `all_variants` path references between dependent phases and passes resolved paths as inputs to consuming phases.

```yaml
artifact_routing:
  purpose: "Inter-phase data flow: resolve artifact paths from upstream phases"

  artifact_types:
    merged_output:
      produced_by: ["generate", "compare"]
      path_pattern: "<pipeline_output>/<phase_id>/merged-output.md"
      description: "Final merged artifact from a phase's Mode A/B execution"

    all_variants:
      produced_by: ["generate"]
      path_pattern: "<pipeline_output>/<phase_id>/variant-*.md"
      description: "All variant files produced by a generate phase"

  path_resolution:
    algorithm: |
      Given: consuming_phase, dependency_phase_id, artifact_type
      1. Compute base_path = <pipeline_output>/<dependency_phase_id>/
      2. If artifact_type == "merged_output":
         return base_path / "merged-output.md"
      3. If artifact_type == "all_variants":
         return glob(base_path / "variant-*.md")

  routing_logic:
    before_execution: |
      For each phase about to execute:
      1. Identify all depends_on phase IDs
      2. For each dependency:
         a. Resolve merged_output path
         b. Verify file exists (error if missing)
      3. For compare phases:
         a. Collect all_variants from all dependency phases
         b. Verify >= 2 variant files total
      4. Inject resolved paths as input parameters to Mode A/B invocation

  routing_contract:
    generate_produces: "merged_output + all_variants"
    compare_produces: "merged_output"
    compare_consumes: "all_variants from dependencies (>= 2 required)"

  error_handling:
    missing_artifact: "STOP: 'Missing dependency artifact: <phase_id>/<artifact_type> not found at <path>'"
    insufficient_variants: "STOP: 'Compare phase <id> requires >= 2 variant inputs, found <N>'"

  acceptance_test:
    scenario: "2-phase pipeline (generate -> compare) passes phase 1 merged output as phase 2 variant input"
    verification: "Artifact paths correctly resolved and passed between phases"
```

#### Parallel Phase Scheduler (D-0022)

Phases at the same dependency level execute concurrently up to `--pipeline-parallel N` limit, using topological sort for execution ordering.

```yaml
parallel_phase_scheduler:
  purpose: "Concurrent phase execution with dependency-respecting topological order"

  concurrency_model:
    grouping: "Phases at the same DAG level execute in parallel"
    limit: "--pipeline-parallel N caps concurrent phase count (default N=3)"
    synchronization: "Wait for all phases in a level to complete before advancing to next level"
    overflow: "If level has more phases than N, execute in batches of N"

  algorithm:
    step_1: "Receive DAG with assigned levels from dag_builder"
    step_2: "Group phases by level: level_0 = [phases...], level_1 = [phases...], ..."
    step_3: "For each level (ascending order):"
    step_3a: "  Launch phases concurrently (up to --pipeline-parallel N)"
    step_3b: "  Wait for all phases in batch to complete"
    step_3c: "  If any phase failed: apply error policy (see Error Policies)"
    step_3d: "  Run artifact routing for completed phases"
    step_4: "Advance to next level"
    step_5: "After all levels complete: finalize pipeline manifest"

  topological_guarantee: |
    Dependent phases NEVER execute before their dependencies complete.
    This is enforced by level assignment: a phase at level N only depends
    on phases at levels 0..N-1, which are all completed before level N begins.

  configuration:
    flag: "--pipeline-parallel"
    default: 3
    range: "1-10"
    type: "integer"

  acceptance_test:
    scenario: "2-phase parallel generate -> compare produces correct artifacts with no race conditions"
    verification: "Execution order respects dependencies; artifact routing correct"
```

#### Pipeline Manifest (D-0023)

Tracks execution state: created at pipeline start, updated after each phase with return contract values and checksums.

```yaml
pipeline_manifest:
  purpose: "Execution state tracking for resume, audit, and convergence monitoring"
  filename: "pipeline-manifest.yaml"
  location: "<pipeline_output>/pipeline-manifest.yaml"

  schema:
    pipeline_id: "UUID generated at pipeline start"
    created_at: "ISO 8601 timestamp"
    pipeline_definition: "Original --pipeline value (inline or @path)"
    global_config:
      depth: "string"
      convergence_threshold: "number"
      parallel_limit: "number"
      blind_mode: "boolean"
      auto_stop_plateau: "boolean"
      error_policy: "halt-on-failure | continue"

    phases:
      - id: "Phase ID"
        type: "generate | compare"
        agents: ["agent_spec_1", ...]
        level: "integer (DAG level)"
        status: "pending | running | completed | failed | skipped"
        started_at: "ISO 8601 timestamp | null"
        finished_at: "ISO 8601 timestamp | null"
        return_contract:
          status: "success | partial | failed"
          convergence_score: "number | null"
          merged_output_path: "string | null"
          base_variant: "string | null"
          unresolved_conflicts: "integer"
        artifact_checksums:
          merged_output: "SHA-256 | null"
          variants: ["SHA-256", ...]

  lifecycle:
    creation: |
      At pipeline start:
      1. Generate pipeline_id (UUID)
      2. Record global_config
      3. List all phases with status: pending
      4. Write pipeline-manifest.yaml

    per_phase_update: |
      After each phase completes:
      1. Set phase status to completed or failed
      2. Record return_contract values from Mode A/B execution
      3. Compute SHA-256 checksums of artifact files
      4. Record started_at and finished_at timestamps
      5. Write updated pipeline-manifest.yaml

    finalization: |
      After pipeline completes:
      1. Record overall pipeline status
      2. Ensure all phases have terminal status

  acceptance_test:
    scenario: "After 3-phase execution, manifest contains all phase results, statuses, and convergence scores"
    verification: "YAML-parseable manifest with per-phase detail"
```

#### Pipeline Resume (D-0024)

`--pipeline-resume` reads the manifest, validates artifact checksums, and re-executes from the first incomplete phase.

```yaml
pipeline_resume:
  purpose: "Avoid redundant re-execution of completed phases"
  trigger: "--pipeline-resume flag present (in combination with --pipeline)"

  algorithm:
    step_1: "Read pipeline-manifest.yaml from <pipeline_output>/"
    step_2: "For each phase with status: completed"
    step_2a: "  Compute current SHA-256 of artifact files"
    step_2b: "  Compare against manifest artifact_checksums"
    step_2c: "  If match: mark phase as validated (skip re-execution)"
    step_2d: "  If mismatch: mark phase as invalidated"
    step_3: "First invalidated or incomplete phase = resume point"
    step_4: "All phases from resume point onward: re-execute"
    step_5: "All downstream phases of invalidated phases: also re-execute"

  checksum_validation:
    scope: "Artifact files only (merged-output.md, variant-*.md)"
    algorithm: "SHA-256"
    mismatch_behavior: "Re-execute the affected phase AND all downstream dependents"

  error_handling:
    missing_manifest: "STOP: 'No pipeline manifest found at <pipeline_output>/pipeline-manifest.yaml'"
    corrupt_manifest: "STOP: 'Pipeline manifest is malformed: <parse_error>'"
    checksum_file_missing: "Treat as invalidated (re-execute phase)"

  acceptance_test:
    scenario: "Resume from phase 2 of 3: phase 1 skipped (checksum valid), phases 2-3 re-execute"
    verification: "Phase 1 artifacts untouched; phases 2-3 produce fresh output"
```

#### Blind Evaluation (D-0025)

`--blind` strips model-name metadata from artifacts before compare phases receive variants, ensuring unbiased evaluation (SC-003).

```yaml
blind_evaluation:
  purpose: "Unbiased variant comparison by removing model identification"
  trigger: "--blind flag present"
  scope: "Applied only to artifacts routed to compare phases"

  stripping_rules:
    model_names:
      patterns: ["opus", "haiku", "sonnet", "claude", "gpt", "gemini"]
      replacement: "variant-{N}"
      case_insensitive: true

    file_content:
      scan_targets:
        - "Model name references in prose text"
        - "Attribution comments (e.g., '<!-- Generated by opus -->')"
        - "Metadata headers containing model identifiers"
      action: "Replace with anonymized identifier (variant-A, variant-B, ...)"

    file_names:
      original: "variant-opus-architect.md"
      anonymized: "variant-A.md"

  integration_point: |
    Applied during artifact routing (D-0021), BEFORE passing artifacts to compare phases:
    1. Copy original artifacts to blind/ subdirectory
    2. Apply stripping rules to copies
    3. Pass anonymized copies to compare phase
    4. Original artifacts preserved in phase output directory

  inactive_behavior: |
    Without --blind flag: artifacts passed to compare phases with full metadata.
    Model names and attribution preserved.

  acceptance_test:
    scenario: "SC-003: merged output after --blind pipeline contains zero model-name references"
    verification: "grep for known model names in merged output returns 0 matches"
```

#### Convergence Plateau Detection (D-0026)

`--auto-stop-plateau` halts pipeline execution when convergence delta <5% for 2 consecutive compare phases.

```yaml
convergence_plateau_detection:
  purpose: "Prevent wasteful additional rounds when convergence has plateaued"
  trigger: "--auto-stop-plateau flag present"

  algorithm:
    tracking: "After each compare phase, record convergence_score in manifest"
    delta_calculation: "delta = abs(current_score - previous_score)"
    threshold: 0.05
    consecutive_required: 2
    check_point: "After each compare phase (skip for generate phases)"

    detection_logic: |
      After compare phase N completes:
      1. Read convergence_score from return contract
      2. If N >= 2 (at least 2 compare phases completed):
         a. Compute delta = abs(score_N - score_{N-1})
         b. If delta < 0.05:
            - Increment consecutive_below_count
         c. Else:
            - Reset consecutive_below_count = 0
      3. If consecutive_below_count >= 2:
         a. Issue warning: "Convergence plateau detected"
         b. Update manifest with plateau_detected: true
         c. Halt pipeline (do not execute remaining phases)
         d. Mark remaining phases as status: skipped

  warning_format: |
    WARNING: Convergence plateau detected after phase <phase_id>
      Current delta: <delta> (threshold: 5%)
      Consecutive below-threshold comparisons: <count>
      Recommendation: Review debate quality or consider different agent configurations
      Pipeline halted. Remaining phases skipped.

  inactive_behavior: |
    Without --auto-stop-plateau: pipeline runs all phases regardless of convergence delta.

  acceptance_test:
    scenario: "SC-004: synthetic 3-phase pipeline with plateau triggers warning and halt on phase 3"
    verification: "Warning issued; phases after detection skipped; manifest records plateau_detected"
```

#### Error Policies (D-0027)

Pipeline error handling: halt-on-failure (default) marks dependents as skipped; `--pipeline-on-error continue` leaves parallel branches running.

```yaml
error_policies:
  purpose: "Configurable pipeline behavior when a phase fails"

  policies:
    halt_on_failure:
      trigger: "Default behavior (no flag required)"
      behavior: |
        When a phase fails:
        1. Mark the failed phase as status: failed in manifest
        2. Identify all phases that depend on the failed phase (direct + transitive)
        3. Mark all dependent phases as status: skipped in manifest
        4. If in parallel execution: cancel sibling phases in the same level
        5. Halt pipeline execution
        6. Report failure with skipped phase list

    continue_on_failure:
      trigger: "--pipeline-on-error continue"
      behavior: |
        When a phase fails:
        1. Mark the failed phase as status: failed in manifest
        2. Identify all phases that depend on the failed phase
        3. Mark dependent phases as status: skipped in manifest
        4. BUT: allow independent branches (no dependency on failed phase) to continue
        5. Continue executing remaining levels
        6. Report partial completion with failure and skip details

  minimum_variant_constraint:
    scope: "Compare phases only"
    requirement: ">=2 variant inputs required for meaningful comparison"
    check_timing: "Before compare phase execution begins"
    failure_behavior: |
      If compare phase has <2 variant inputs after artifact routing:
      1. Mark compare phase as status: failed
      2. Error: "Compare phase <id> requires >= 2 variant inputs, found <N>"
      3. Apply active error policy (halt or continue)

  configuration:
    flag: "--pipeline-on-error"
    values: ["halt", "continue"]
    default: "halt"

  acceptance_test:
    scenario_halt: "Failed phase marks dependents as skipped; pipeline stops"
    scenario_continue: "Failed phase marks dependents as skipped; parallel branches continue"
    verification: "Manifest accurately reflects phase statuses under both policies"
```

---

*Skill definition for SuperClaude Framework v4.2.0+*
*Based on SC-ADVERSARIAL-SPEC.md v1.0.0*
