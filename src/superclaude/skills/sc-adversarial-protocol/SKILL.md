---
name: sc:adversarial
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
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

**MANDATORY**: Either `--compare` (Mode A) or `--source`+`--generate`+`--agents` (Mode B) must be provided.

```
/sc:adversarial --compare file1.md,file2.md[,...,fileN.md] [options]
/sc:adversarial --source <file> --generate <type> --agents <spec>[,...] [options]
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
```

**Output**: `adversarial/diff-analysis.md` — organized by category with severity ratings
**Template**: See `refs/artifact-templates.md` Section 1

### Step 2: Adversarial Debate

**Input**: All variants + diff-analysis.md
**Delegation**: debate-orchestrator agent coordinates; advocate agents participate
**Process**:

```yaml
adversarial_debate:
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
    rubric: "25-criterion additive binary rubric across 5 dimensions"
    dimensions:
      - "Completeness (5 criteria)"
      - "Correctness (5 criteria)"
      - "Structure (5 criteria)"
      - "Clarity (5 criteria)"
      - "Risk Coverage (5 criteria)"
    evidence_protocol: "Claim-Evidence-Verdict (CEV) for every criterion"
    formula: "qual_score = total_criteria_met / 25"

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

## Return Contract (FR-007)

When invoked by another command, sc:adversarial returns:

```yaml
return_contract:
  merged_output_path: "<path to merged file>"
  convergence_score: "<final convergence percentage>"
  artifacts_dir: "<path to adversarial/ directory>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list of unresolved items>"]
```

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
  step_1_detect_mode:
    mode_a_signal: "--compare flag present"
    mode_b_signal: "--source AND --generate AND --agents flags present"
    conflict: "If both Mode A and Mode B flags present → STOP with error: 'Cannot use --compare with --source/--generate/--agents'"
    neither: "If neither mode detected → STOP with error: 'Must provide --compare (Mode A) or --source + --generate + --agents (Mode B)'"

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
        - Categories: structural (<N>), content (<N>), contradictions (<N>), unique (<N>)

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

    6_summary:
      content: |
        ## Summary
        - Total structural differences: <N>
        - Total content differences: <N>
        - Total contradictions: <N>
        - Total unique contributions: <N>
        - Highest-severity items: <list of IDs with High severity>

  validation:
    - "All 4 sections present and non-empty (warn if a section has 0 items)"
    - "All ID sequences are contiguous (no gaps)"
    - "Metadata counts match actual table row counts"
    - "Severity/impact ratings present for every entry"

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
    subagent_type: "general-purpose"
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
    if_converged: "Log convergence achieved, proceed to scoring"
    if_not_converged: "Continue to Round 3 if --depth deep"
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
  threshold:
    default: 0.80
    configurable: "--convergence flag (range 0.50-0.99)"
    validation: "If value outside range, warn and use default 0.80"

  per_point_tracking:
    data_structure:
      point_id: "Diff point ID (S-NNN, C-NNN, X-NNN)"
      round_1_positions: "{variant_id: position}"
      round_2_positions: "{variant_id: position}"
      round_3_positions: "{variant_id: position}"
      agreed: "true/false"
      winner: "variant_id or null"

  agreement_determination:
    unanimous: "All advocates agree on same winner → agreed=true"
    majority: "≥2/3 of advocates agree → agreed=true (winner = majority choice)"
    split: "No majority → agreed=false (point remains unresolved)"

  early_termination_conditions:
    unanimous_agreement:
      condition: "All points have unanimous agreement"
      action: "Terminate debate immediately"
      log: "Convergence: 100% (unanimous)"

    stable_majority:
      condition: "≥threshold agreement maintained for 2 consecutive rounds"
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

  status_output:
    CONVERGED: "Agreement ≥ threshold"
    NOT_CONVERGED: "Agreement < threshold after max rounds"
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

25-criterion additive binary rubric with mandatory evidence citation:

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

  formula: "qual_score = total_criteria_met / 25"
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
        - "### Qualitative Summary — dimension subtotals per variant"

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
    subagent_type: "general-purpose"
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
      Any command can invoke sc:adversarial and consume the return contract:
      1. Call sc:adversarial with appropriate flags
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

*Skill definition for SuperClaude Framework v4.2.0+*
*Based on SC-ADVERSARIAL-SPEC.md v1.0.0*
