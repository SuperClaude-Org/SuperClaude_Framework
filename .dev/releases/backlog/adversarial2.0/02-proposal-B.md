# Proposal B: Recursive Pipeline

## Overview

This proposal makes the existing 5-step adversarial pipeline **self-referential**. Rather than adding a new orchestration layer above the pipeline, the pipeline itself gains the ability to accept previous pipeline outputs as variant inputs and to invoke itself recursively. A "debate of debates" is not a special mode -- it is simply another pipeline invocation where the variants happen to be merged outputs from prior invocations.

The key insight: **the pipeline already operates on "N artifacts in, 1 merged artifact out."** If we generalize how those N artifacts are sourced, the pipeline naturally composes with itself. A `PipelineVariantProvider` treats a completed pipeline run's merged output as just another variant file, and a recursive invocation is just a pipeline whose variants come from child pipelines.

**Design philosophy**: Reuse the 5-step protocol logic (diff, debate, score, plan, merge) at every recursion level. No duplication, no special-casing. The only new code is the recursion controller, variant provider abstraction, and namespace isolation.

---

## Architecture

### Conceptual Model

```
                    ┌──────────────────────────┐
                    │   Recursive Controller    │
                    │  (depth limit, termination│
                    │   conditions, model map)  │
                    └─────────┬────────────────┘
                              │
                    ┌─────────▼────────────────┐
                    │  VariantProvider Router   │
                    │  resolves variant source  │
                    │  per recursion level      │
                    └─────────┬────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼──────┐ ┌─────▼───────┐ ┌─────▼───────┐
     │ FileProvider   │ │ Generative  │ │ Pipeline    │
     │ (Mode A)       │ │ Provider    │ │ Provider    │
     │ reads files    │ │ (Mode B)    │ │ (recursive) │
     │                │ │ dispatches  │ │ invokes     │
     │                │ │ agents      │ │ child       │
     │                │ │             │ │ pipelines   │
     └────────┬──────┘ └─────┬───────┘ └─────┬───────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                    ┌─────────▼────────────────┐
                    │  5-Step Protocol Engine   │
                    │  (unchanged core logic)   │
                    │  diff → debate → score    │
                    │  → plan → merge           │
                    └──────────────────────────┘
```

### Component Inventory

| Component | Status | Responsibility |
|-----------|--------|----------------|
| 5-Step Protocol Engine | **Unchanged** | diff, debate, score, plan, merge |
| Input Mode Parser | **Modified** | Recognizes `--recursive` flag, relaxes mode exclusivity for recursive specs |
| VariantProvider (abstract) | **New** | Uniform interface for sourcing variants |
| FileVariantProvider | **Extracted** | Current Mode A logic, extracted to provider |
| GenerativeVariantProvider | **Extracted** | Current Mode B logic, extracted to provider |
| PipelineVariantProvider | **New** | Invokes child pipeline, returns merged output as variant |
| RecursiveController | **New** | Manages recursion depth, termination, model assignment |
| NamespaceAllocator | **New** | Assigns phase-scoped artifact directories |
| RecursionState | **New** | Tracks context across recursive calls |

---

## Recursion Model

### How the Pipeline Calls Itself

The pipeline does not literally "call itself" in a function-call sense (Claude Code skills are prompt-driven, not callable functions). Instead, the `PipelineVariantProvider` **re-enters the 5-step protocol** with a scoped configuration:

```yaml
recursion_model:
  mechanism: "Provider-driven re-entry"
  description: |
    When a PipelineVariantProvider is encountered during variant resolution,
    the RecursiveController:
      1. Allocates a child namespace (see Namespace Isolation)
      2. Pushes current state onto the recursion stack
      3. Executes the child pipeline's full 5-step protocol
      4. Captures the child's merged_output_path as the variant file
      5. Pops state and continues the parent pipeline

  execution_model: "Depth-first, left-to-right"
  rationale: |
    Each child pipeline must complete before the parent can proceed,
    because the parent needs the child's merged output as a variant.
    Children at the same level are independent and could run in parallel
    (but serial execution is safer for state management).

  depth_limit:
    hard_max: 4
    default: 3
    configurable: "--max-depth N (range 1-4)"
    rationale: |
      Level 0: Leaf pipelines (direct file/generative providers)
      Level 1: First meta-debate (compares Level 0 outputs)
      Level 2: Second meta-debate (compares Level 1 outputs)
      Level 3: Final synthesis (compares Level 2 outputs, rare)
      Beyond 3 levels yields diminishing returns and exponential token cost.

  depth_enforcement:
    at_limit: "PipelineVariantProvider is forbidden; only File/Generative providers allowed"
    error: "STOP: 'Recursion depth {current} would exceed max-depth {limit}. Use FileVariantProvider or GenerativeVariantProvider at this level.'"
```

### Recursion Stack

```yaml
recursion_stack:
  structure: "Array of RecursionFrame objects, LIFO"

  frame_schema:
    level: "integer (0 = leaf, incrementing upward)"
    phase_id: "string (e.g., 'L0-opus', 'L0-haiku', 'L1-meta')"
    namespace: "string (artifact directory path)"
    provider_type: "FileVariantProvider | GenerativeVariantProvider | PipelineVariantProvider"
    config: "pipeline configuration for this level"
    model_assignment: "which model runs debate-orchestrator at this level"
    parent_phase_id: "string | null (null for root)"
    status: "pending | running | completed | failed"
    result: "null | {merged_output_path, convergence_score, artifacts_dir}"

  max_stack_depth: 4
  overflow_behavior: "STOP with error before pushing"
```

---

## Variant Provider Abstraction

### Interface

Every provider implements the same contract. The 5-step protocol engine never knows or cares where its variants came from:

```yaml
variant_provider_interface:
  name: "VariantProvider"

  contract:
    input:
      config: "Provider-specific configuration"
      namespace: "Target artifact directory for this provider's outputs"
    output:
      variants: "List of {variant_id, file_path, metadata}"
      count: "integer (2-10)"
    errors:
      insufficient_variants: "Fewer than 2 variants produced"
      provider_failure: "Provider-specific error with context"

  implementations:
    FileVariantProvider:
      description: "Reads existing files (current Mode A behavior)"
      config:
        files: "List of file paths"
      behavior: |
        1. Validate all files exist and are readable
        2. Copy each to namespace as variant-N-original.md
        3. Return variant list with metadata
      unchanged_from: "SKILL.md:494-504 (mode_a_loading)"

    GenerativeVariantProvider:
      description: "Dispatches Task agents (current Mode B behavior)"
      config:
        source: "Source file path"
        generate: "Artifact type"
        agents: "List of agent specs [{model, persona?, instruction?}]"
      behavior: |
        1. Parse agent specs per SKILL.md:444-459
        2. Dispatch parallel Task agents
        3. Collect outputs as variant-N-<model>-<persona>.md
        4. Return variant list with metadata
      unchanged_from: "SKILL.md:506-512 (mode_b_loading)"

    PipelineVariantProvider:
      description: "Invokes a child pipeline and returns its merged output"
      config:
        child_pipeline:
          provider: "VariantProvider config (can itself be Pipeline, File, or Generative)"
          depth: "--depth for child pipeline"
          convergence: "--convergence for child pipeline"
          model: "Model for child's debate-orchestrator"
          focus: "Optional focus areas for child"
      behavior: |
        1. Verify recursion depth limit not exceeded
        2. Allocate child namespace via NamespaceAllocator
        3. Resolve child's own variant provider (recursive!)
        4. Execute full 5-step protocol in child namespace
        5. Return child's merged_output_path as single variant file
        6. Attach child's return_contract as variant metadata
      new_code: true

  routing_logic:
    decision: |
      The RecursiveController examines the user's specification to determine
      which provider type to instantiate at each level:
        - Explicit file paths → FileVariantProvider
        - Agent specs (model:persona) → GenerativeVariantProvider
        - Reference to another pipeline output → PipelineVariantProvider
        - --recursive flag with child definitions → PipelineVariantProvider wrapping children
```

### Provider Composition Example

The user's 8-step workflow expressed as provider composition:

```yaml
# User's workflow:
# 1. Opus generates 3 variants of spec → debate → merge-opus.md
# 2. Haiku generates 3 variants of spec → debate → merge-haiku.md
# 3. Compare merge-opus.md vs merge-haiku.md → final merge

root_pipeline:
  level: 1
  provider: PipelineVariantProvider
  children:
    - phase_id: "L0-opus"
      provider: GenerativeVariantProvider
      config:
        source: "spec.md"
        generate: "roadmap"
        agents:
          - "opus:architect"
          - "opus:backend"
          - "opus:security"
        depth: "standard"
      model: "opus"  # debate-orchestrator model for this child

    - phase_id: "L0-haiku"
      provider: GenerativeVariantProvider
      config:
        source: "spec.md"
        generate: "roadmap"
        agents:
          - "haiku:architect"
          - "haiku:backend"
          - "haiku:security"
        depth: "standard"
      model: "haiku"  # debate-orchestrator model for this child

  # Root level compares the two children's merged outputs
  depth: "deep"
  convergence: 0.85
  model: "opus"  # debate-orchestrator for meta-debate
```

---

## Auto-Detection: When Is Recursion Needed?

The system can detect recursion opportunities, but **never auto-activates recursion** without explicit user intent. Recursion is expensive (multiplicative token cost) and should be a deliberate choice.

```yaml
auto_detection:
  policy: "Suggest, never auto-activate"

  detection_signals:
    multi_model_agents:
      condition: "Agent specs in --agents use 2+ distinct models"
      example: "--agents opus:architect,opus:backend,haiku:architect,haiku:backend"
      suggestion: |
        "Detected agents using multiple models (opus, haiku).
         Consider --recursive to run separate debates per model,
         then meta-debate the results. This improves cross-model
         validation but costs ~3x tokens."
      auto_activate: false

    explicit_recursive_flag:
      condition: "--recursive flag present"
      behavior: "Parse child pipeline definitions from flag value"
      auto_activate: true

    pipeline_spec_file:
      condition: "--pipeline-spec <file.yaml> flag present"
      behavior: "Load recursive pipeline definition from YAML file"
      auto_activate: true

    compare_with_generate:
      condition: "Both --compare and --generate flags present (currently an error)"
      suggestion: |
        "You provided both --compare and --generate. Did you mean:
         (a) --recursive: generate variants, then compare the merged outputs
         (b) Choose one mode: --compare OR --generate"
      auto_activate: false

  suggestion_format:
    display: |
      ┌─ Recursion Opportunity Detected ─────────────────────────┐
      │ {signal_description}                                      │
      │                                                           │
      │ Suggested: /sc:adversarial --recursive \                  │
      │   --children "L0-opus:opus:architect,opus:backend" \      │
      │   --children "L0-haiku:haiku:architect,haiku:backend" \   │
      │   --source spec.md --generate roadmap                     │
      │                                                           │
      │ Estimated cost: ~{N}x single pipeline tokens              │
      │ Proceed with recursion? [y/N]                             │
      └──────────────────────────────────────────────────────────┘
    interactive_only: true
    non_interactive: "Log suggestion, proceed without recursion"
```

---

## State Management in Recursion

### RecursionState Object

```yaml
recursion_state:
  description: |
    A single state object threaded through all recursive calls.
    Each level reads parent state and appends its own results.
    The state object is the sole mechanism for cross-level communication.

  schema:
    pipeline_id: "Unique ID for the entire recursive invocation (UUID)"
    initiated_at: "ISO timestamp"
    max_depth: "Configured maximum recursion depth"
    current_depth: "Current recursion level being executed"

    phases:
      type: "ordered list of PhaseRecord"
      description: "Append-only log of all pipeline executions"

    phase_record:
      phase_id: "string (e.g., 'L0-opus')"
      level: "integer"
      parent_phase_id: "string | null"
      provider_type: "File | Generative | Pipeline"
      config_snapshot: "frozen copy of pipeline config used"
      model: "model running debate-orchestrator"
      namespace: "artifact directory path"
      status: "pending | running | completed | failed"
      started_at: "ISO timestamp | null"
      completed_at: "ISO timestamp | null"
      return_contract:
        merged_output_path: "string | null"
        convergence_score: "float | null"
        artifacts_dir: "string | null"
        status: "success | partial | failed | null"
        unresolved_conflicts: "list | null"
      error: "string | null (if failed)"

    execution_order:
      type: "list of phase_ids in execution order"
      description: "Records actual execution sequence for debugging"

    token_usage:
      per_phase: "{phase_id: estimated_tokens}"
      total: "sum of all phases"
      budget: "configured token budget (if any)"

    manifest_path: "path to persisted manifest.json"

  persistence:
    format: "JSON"
    location: "<output-dir>/adversarial/manifest.json"
    write_events:
      - "On phase start (status: running)"
      - "On phase completion (status: completed, return_contract populated)"
      - "On phase failure (status: failed, error populated)"
      - "On pipeline completion (final summary)"
    crash_recovery: |
      If the pipeline crashes mid-execution, the manifest records which
      phases completed. A re-invocation can skip completed phases by
      detecting existing manifest.json with completed phase records.
```

### Context Propagation

```yaml
context_propagation:
  what_flows_down:
    - "Source file (--source) — same source at all levels unless overridden"
    - "Generate type (--generate) — same type at all levels"
    - "Focus areas (--focus) — inherited unless child overrides"
    - "Interactive flag — inherited (pauses apply at every level)"
    - "RecursionState reference — always propagated"
    - "NamespaceAllocator reference — always propagated"

  what_does_NOT_flow_down:
    - "Depth (--depth) — each level can have its own depth"
    - "Convergence (--convergence) — each level can have its own threshold"
    - "Model assignment — explicitly specified per level"
    - "Agent specs — each level has its own agents"
    - "Artifact paths — namespaced per level (see Namespace Isolation)"

  what_flows_up:
    - "Return contract (merged_output_path, convergence_score, etc.)"
    - "Phase status (completed/failed)"
    - "Token usage estimate"
    - "Unresolved conflicts list"
```

---

## Namespace Isolation

### Directory Structure

Each recursive invocation gets its own scoped directory. No filename collisions are possible because every artifact path includes the phase ID.

```yaml
namespace_isolation:
  strategy: "Phase-ID-prefixed subdirectories under adversarial/"

  directory_structure:
    template: |
      <output-dir>/
      ├── <final-merged-output>.md           # Root pipeline's merged output
      ├── adversarial/
      │   ├── manifest.json                  # RecursionState persistence
      │   │
      │   ├── L0-opus/                       # Child pipeline 1 namespace
      │   │   ├── variant-1-opus-architect.md
      │   │   ├── variant-2-opus-backend.md
      │   │   ├── variant-3-opus-security.md
      │   │   ├── diff-analysis.md
      │   │   ├── debate-transcript.md
      │   │   ├── base-selection.md
      │   │   ├── refactor-plan.md
      │   │   ├── merge-log.md
      │   │   └── merged.md                  # This child's merged output
      │   │
      │   ├── L0-haiku/                      # Child pipeline 2 namespace
      │   │   ├── variant-1-haiku-architect.md
      │   │   ├── variant-2-haiku-backend.md
      │   │   ├── variant-3-haiku-security.md
      │   │   ├── diff-analysis.md
      │   │   ├── debate-transcript.md
      │   │   ├── base-selection.md
      │   │   ├── refactor-plan.md
      │   │   ├── merge-log.md
      │   │   └── merged.md                  # This child's merged output
      │   │
      │   └── root/                          # Root pipeline namespace
      │       ├── variant-1-L0-opus.md       # Symlink or copy of L0-opus/merged.md
      │       ├── variant-2-L0-haiku.md      # Symlink or copy of L0-haiku/merged.md
      │       ├── diff-analysis.md
      │       ├── debate-transcript.md
      │       ├── base-selection.md
      │       ├── refactor-plan.md
      │       └── merge-log.md

  namespace_allocator:
    algorithm: |
      1. Take phase_id (e.g., "L0-opus")
      2. Sanitize: lowercase, replace non-alphanumeric with hyphen
      3. Path = <output-dir>/adversarial/<sanitized-phase-id>/
      4. Create directory if it does not exist
      5. Verify no existing directory with same name (error if collision)

    collision_prevention:
      rule: "Phase IDs must be unique within a pipeline invocation"
      enforcement: "RecursiveController validates uniqueness before allocation"
      error: "STOP: 'Duplicate phase_id: {id}. Each child pipeline must have a unique phase_id.'"

  artifact_naming_within_namespace:
    unchanged: |
      Within each namespace, artifacts use the standard naming from SKILL.md:292-309.
      No changes to diff-analysis.md, debate-transcript.md, etc.
      The namespace directory provides isolation, not the filename.

  variant_naming_for_pipeline_provider:
    pattern: "variant-N-<child-phase-id>.md"
    example: "variant-1-L0-opus.md (copy of L0-opus/merged.md)"
    rationale: "Names the variant after its source pipeline, making provenance clear"
```

### Three-Level Example

```
adversarial/
├── manifest.json
├── L0-opus-arch/          # Level 0: Opus architect variants
│   └── (standard artifacts)
├── L0-opus-sec/           # Level 0: Opus security variants
│   └── (standard artifacts)
├── L1-opus-meta/          # Level 1: Meta-debate of opus children
│   ├── variant-1-L0-opus-arch.md
│   ├── variant-2-L0-opus-sec.md
│   └── (standard artifacts)
├── L0-haiku-arch/         # Level 0: Haiku architect variants
│   └── (standard artifacts)
├── L0-haiku-sec/          # Level 0: Haiku security variants
│   └── (standard artifacts)
├── L1-haiku-meta/         # Level 1: Meta-debate of haiku children
│   ├── variant-1-L0-haiku-arch.md
│   ├── variant-2-L0-haiku-sec.md
│   └── (standard artifacts)
└── root/                  # Level 2: Final meta-meta-debate
    ├── variant-1-L1-opus-meta.md
    ├── variant-2-L1-haiku-meta.md
    └── (standard artifacts)
```

---

## Termination Conditions

Recursion terminates when any of the following conditions are met:

```yaml
termination_conditions:
  hard_stops:
    depth_limit_reached:
      condition: "current_depth >= max_depth"
      behavior: "Refuse to create PipelineVariantProvider; only File/Generative allowed"
      error_if_forced: "STOP: 'Cannot recurse beyond depth {max_depth}'"

    token_budget_exhausted:
      condition: "estimated_remaining_tokens < minimum_phase_cost"
      minimum_phase_cost: 5000  # tokens — rough minimum for a single pipeline run
      behavior: "STOP current phase, return best partial result"
      manifest_update: "Record phase as 'failed' with error 'token_budget_exhausted'"

    all_children_failed:
      condition: "All child PipelineVariantProviders returned status: failed"
      behavior: "Parent pipeline cannot proceed (no variants). Return failed status."
      manifest_update: "Record parent as 'failed' with error 'all_children_failed'"

  soft_stops:
    convergence_already_high:
      condition: "Child pipeline achieved convergence >= 0.95"
      behavior: |
        Suggest skipping further recursion levels for this branch.
        Log: "Child {phase_id} achieved {convergence}% convergence.
              Further debate unlikely to improve. Proceeding as variant."
      override: "User can force continued recursion with --force-recurse"

    diminishing_returns:
      condition: "Parent convergence - child convergence < 0.05 for 2 consecutive levels"
      behavior: |
        Suggest termination: "Convergence improvement plateaued
        ({parent}% vs {child}%). Consider stopping recursion."
      override: "User can force with --force-recurse"

    single_variant_at_level:
      condition: "Only 1 child pipeline completed (others failed)"
      behavior: "Skip debate at this level, pass the single output upward as-is"
      log: "Only one variant available at level {N}. Skipping debate."

  natural_completion:
    condition: "Root pipeline completes its 5-step protocol"
    behavior: "Write final merged output, finalize manifest, return root return_contract"
```

---

## Cross-Model Support

### Model Assignment Strategy

Different models serve different purposes at different recursion levels. The design supports explicit per-level model assignment:

```yaml
cross_model_support:
  assignment_levels:
    variant_generation:
      description: "Models used by GenerativeVariantProvider to create variants"
      specified_via: "--agents flag (per-agent model spec)"
      example: "opus:architect, haiku:backend"
      unchanged_from: "Current SKILL.md agent spec parsing"

    debate_orchestration:
      description: "Model running the debate-orchestrator agent at each level"
      specified_via: "--model flag per child pipeline definition"
      default: "opus (highest capability for scoring/judging)"
      rationale: |
        The debate-orchestrator must evaluate arguments fairly.
        Using a high-capability model here is critical for quality.
        Lower levels (leaf pipelines) can use cheaper models if the
        variants themselves were generated by specific models.

    meta_debate_orchestration:
      description: "Model for the root/parent pipeline's debate-orchestrator"
      specified_via: "--meta-model flag (defaults to opus)"
      rationale: |
        The final synthesis should use the highest-capability model
        available, since it judges the quality of merged outputs
        that already went through one round of adversarial validation.

  model_escalation_pattern:
    description: |
      A common and recommended pattern: use cheaper models at leaf levels
      and escalate to more capable models at higher recursion levels.
    example:
      level_0: "haiku for variant generation (fast, cheap, diverse)"
      level_1: "sonnet for first meta-debate (good judgment, moderate cost)"
      level_2: "opus for final synthesis (highest quality, most expensive)"
    flag_syntax: "--model-escalation haiku,sonnet,opus"
    behavior: |
      Model at level N = escalation_list[min(N, len(escalation_list)-1)]
      If list is shorter than depth, last model is used for all deeper levels.

  model_map_explicit:
    description: "Full control over model assignment per phase"
    syntax: |
      --model-map L0-opus:opus,L0-haiku:haiku,root:opus
    behavior: "Each phase_id gets its specified model for debate-orchestrator"
    fallback: "Phases not in map use --meta-model (default: opus)"
```

### Cross-Model Bias Considerations

```yaml
cross_model_bias:
  concern: |
    When a higher-capability model judges outputs from a lower-capability
    model, there is risk of systematic bias (favoring outputs that match
    the judge model's style or reasoning patterns).

  mitigations:
    position_bias_preserved:
      description: "Existing position bias mitigation (SKILL.md:182-186) applies"
      mechanism: "Forward + reverse evaluation passes"
      effective_for: "Ordering bias, but not model-affinity bias"

    blind_evaluation:
      description: "Variant source model is NOT revealed to the debate-orchestrator"
      mechanism: |
        Variants are presented as "Variant 1" and "Variant 2", not as
        "Opus merge output" and "Haiku merge output". The debate-
        orchestrator evaluates on content quality, not model reputation.
      implementation: |
        PipelineVariantProvider strips model-identifying metadata from
        variant files before presenting them to the parent pipeline.

    model_diversity_in_advocates:
      description: "At meta-debate levels, advocates can use different models"
      mechanism: |
        Root pipeline's advocate agents can be assigned different models
        to prevent groupthink. E.g., one opus advocate, one sonnet advocate.
      optional: true
```

---

## Concrete Example: The User's 8-Step Workflow

The gap analysis describes an 8-step workflow. Here is how it maps to the recursive pipeline model:

### Original 8 Steps (Manual)

1. Opus generates variant A of spec
2. Opus generates variant B of spec
3. Opus generates variant C of spec
4. Compare A, B, C via adversarial debate -> merge-opus.md
5. Haiku generates variant D of spec
6. Haiku generates variant E of spec
7. Haiku generates variant F of spec
8. Compare merge-opus.md, merge-haiku.md via adversarial debate -> final.md

### Recursive Pipeline Expression (Single Command)

```bash
/sc:adversarial \
  --recursive \
  --source spec.md \
  --generate roadmap \
  --children "L0-opus:opus:architect,opus:backend,opus:security" \
  --children "L0-haiku:haiku:architect,haiku:backend,haiku:security" \
  --depth standard \
  --meta-depth deep \
  --meta-model opus \
  --output ./output/
```

### Execution Trace

```yaml
execution_trace:
  step_1_parse:
    action: "RecursiveController parses --recursive with --children specs"
    result:
      root_pipeline:
        level: 1
        model: "opus (--meta-model)"
        depth: "deep (--meta-depth)"
        children:
          - phase_id: "L0-opus"
            provider: GenerativeVariantProvider
            agents: ["opus:architect", "opus:backend", "opus:security"]
            depth: "standard"
            model: "opus"
          - phase_id: "L0-haiku"
            provider: GenerativeVariantProvider
            agents: ["haiku:architect", "haiku:backend", "haiku:security"]
            depth: "standard"
            model: "haiku"

  step_2_allocate_namespaces:
    action: "NamespaceAllocator creates directories"
    result:
      - "./output/adversarial/L0-opus/"
      - "./output/adversarial/L0-haiku/"
      - "./output/adversarial/root/"
      - "./output/adversarial/manifest.json (initialized)"

  step_3_execute_child_L0_opus:
    action: "GenerativeVariantProvider dispatches 3 opus agents"
    sub_steps:
      - "Dispatch opus:architect → variant-1-opus-architect.md"
      - "Dispatch opus:backend → variant-2-opus-backend.md"
      - "Dispatch opus:security → variant-3-opus-security.md"
      - "5-step protocol: diff → debate → score → plan → merge"
    output: "./output/adversarial/L0-opus/merged.md"
    manifest_update: "L0-opus: completed, convergence: 82%"

  step_4_execute_child_L0_haiku:
    action: "GenerativeVariantProvider dispatches 3 haiku agents"
    sub_steps:
      - "Dispatch haiku:architect → variant-1-haiku-architect.md"
      - "Dispatch haiku:backend → variant-2-haiku-backend.md"
      - "Dispatch haiku:security → variant-3-haiku-security.md"
      - "5-step protocol: diff → debate → score → plan → merge"
    output: "./output/adversarial/L0-haiku/merged.md"
    manifest_update: "L0-haiku: completed, convergence: 78%"

  step_5_prepare_root_variants:
    action: "PipelineVariantProvider collects child outputs"
    sub_steps:
      - "Copy L0-opus/merged.md → root/variant-1-L0-opus.md"
      - "Copy L0-haiku/merged.md → root/variant-2-L0-haiku.md"
      - "Strip model-identifying metadata (blind evaluation)"

  step_6_execute_root_pipeline:
    action: "5-step protocol on root variants (deep depth, opus orchestrator)"
    sub_steps:
      - "Step 1: Diff analysis of opus-merge vs haiku-merge"
      - "Step 2: Deep adversarial debate (up to 3 rounds)"
      - "Step 3: Hybrid scoring with position bias mitigation"
      - "Step 4: Refactoring plan"
      - "Step 5: Merge execution"
    output: "./output/final-merged-roadmap.md"
    manifest_update: "root: completed, convergence: 88%"

  step_7_finalize:
    action: "Write final manifest, return root return_contract"
    return_contract:
      merged_output_path: "./output/final-merged-roadmap.md"
      convergence_score: "88%"
      artifacts_dir: "./output/adversarial/"
      status: "success"
      unresolved_conflicts: ["performance-vs-security tradeoff in Section 4"]
      recursion_metadata:
        total_phases: 3
        depth_reached: 1
        child_convergence_scores:
          L0-opus: "82%"
          L0-haiku: "78%"
```

---

## Flag Syntax for Recursive Mode

### New Flags

```yaml
new_flags:
  recursive:
    flag: "--recursive"
    type: "boolean"
    default: false
    description: "Enable recursive pipeline mode"
    effect: "Activates RecursiveController, relaxes mode exclusivity"

  children:
    flag: "--children"
    type: "string (repeatable)"
    format: "<phase-id>:<agent-spec>[,<agent-spec>,...]"
    description: "Define a child pipeline with its phase ID and agent specifications"
    example: '--children "L0-opus:opus:architect,opus:backend"'
    repeatable: true
    minimum: 2  # Need at least 2 children for adversarial comparison at root

  max_depth:
    flag: "--max-depth"
    type: "integer"
    default: 3
    range: "1-4"
    description: "Maximum recursion depth"

  meta_depth:
    flag: "--meta-depth"
    type: "string"
    values: ["quick", "standard", "deep"]
    default: "deep"
    description: "Debate depth for the root (meta) pipeline"

  meta_model:
    flag: "--meta-model"
    type: "string"
    default: "opus"
    description: "Model for root pipeline's debate-orchestrator"

  model_escalation:
    flag: "--model-escalation"
    type: "string (comma-separated)"
    example: "haiku,sonnet,opus"
    description: "Automatic model escalation by recursion level"
    mutual_exclusion: "--model-map"

  model_map:
    flag: "--model-map"
    type: "string (comma-separated key:value)"
    example: "L0-opus:opus,L0-haiku:haiku,root:opus"
    description: "Explicit per-phase model assignment"
    mutual_exclusion: "--model-escalation"

  force_recurse:
    flag: "--force-recurse"
    type: "boolean"
    default: false
    description: "Override soft termination conditions"

  pipeline_spec:
    flag: "--pipeline-spec"
    type: "file path"
    description: "Load recursive pipeline definition from YAML file"
    alternative_to: "--children (for complex configurations)"
```

### Backward Compatibility

```yaml
backward_compatibility:
  non_recursive_invocations:
    behavior: "Completely unchanged"
    reasoning: |
      Without --recursive flag, the pipeline operates exactly as today.
      FileVariantProvider and GenerativeVariantProvider are just extractions
      of existing Mode A and Mode B logic into a cleaner interface.
      The 5-step protocol engine is untouched.

  mode_exclusivity:
    without_recursive: "Mode A/B conflict check remains strict (SKILL.md:422)"
    with_recursive: "Conflict check is bypassed — RecursiveController handles mode composition"

  return_contract:
    extended_fields:
      recursion_metadata:
        presence: "Only present when --recursive was used"
        schema:
          total_phases: "integer"
          depth_reached: "integer"
          child_convergence_scores: "{phase_id: score}"
    existing_fields: "Unchanged — merged_output_path, convergence_score, artifacts_dir, status, unresolved_conflicts"
```

---

## Implementation Complexity Assessment

### Component Sizing

| Component | Lines (est.) | Complexity | Dependencies |
|-----------|-------------|------------|--------------|
| VariantProvider interface | 30-40 | Low | None (abstract contract) |
| FileVariantProvider | 50-60 | Low | Extract from existing Mode A |
| GenerativeVariantProvider | 60-80 | Low | Extract from existing Mode B |
| PipelineVariantProvider | 100-150 | Medium | RecursiveController, NamespaceAllocator |
| RecursiveController | 150-200 | High | All providers, state management |
| NamespaceAllocator | 40-60 | Low | Filesystem operations |
| RecursionState + Manifest | 80-120 | Medium | JSON serialization |
| Flag parsing extensions | 60-80 | Medium | Existing parser modifications |
| Blind evaluation (metadata strip) | 20-30 | Low | String processing |
| **Total new/modified** | **~590-820** | **Medium-High** | |

### Implementation Phases

```yaml
implementation_phases:
  phase_1_extract_providers:
    effort: "Small"
    description: "Extract FileVariantProvider and GenerativeVariantProvider from existing code"
    risk: "Low — pure refactoring, no behavior change"
    test: "Existing Mode A and Mode B tests pass unchanged"

  phase_2_namespace_and_state:
    effort: "Small-Medium"
    description: "Implement NamespaceAllocator and RecursionState"
    risk: "Low — isolated new components"
    test: "Unit tests for directory creation and manifest serialization"

  phase_3_pipeline_provider:
    effort: "Medium"
    description: "Implement PipelineVariantProvider with recursive invocation"
    risk: "Medium — recursion logic, depth enforcement"
    test: "Integration test with 2-level recursion"

  phase_4_recursive_controller:
    effort: "Medium-High"
    description: "Implement RecursiveController with flag parsing and orchestration"
    risk: "Medium — coordination complexity"
    test: "Full 8-step workflow end-to-end test"

  phase_5_cross_model_and_polish:
    effort: "Small"
    description: "Model escalation, blind evaluation, auto-detection suggestions"
    risk: "Low — additive features"
    test: "Model assignment verification, metadata stripping test"
```

### Token Cost Analysis

```yaml
token_cost:
  single_pipeline:
    estimate: "8K-15K tokens (depending on variant count and depth)"
    breakdown:
      variant_generation: "2K-5K (Mode B only)"
      diff_analysis: "1K-2K"
      debate: "3K-5K (depth-dependent)"
      scoring: "1K-2K"
      plan_and_merge: "1K-2K"

  two_level_recursion:
    description: "User's 8-step workflow"
    estimate: "25K-45K tokens"
    breakdown:
      child_1_pipeline: "8K-15K"
      child_2_pipeline: "8K-15K"
      root_meta_debate: "8K-15K"
    multiplier: "~3x single pipeline"

  three_level_recursion:
    estimate: "75K-135K tokens"
    multiplier: "~9x single pipeline"
    warning: "Approaching practical limits. Reserve for high-value decisions."

  cost_mitigation:
    quick_depth_for_leaves: "Use --depth quick at level 0 to reduce child cost"
    focused_debate: "Use --focus to limit debate scope at each level"
    early_termination: "High convergence at child level skips further recursion"
```

---

## Risk Analysis

### Technical Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Recursion state corruption | High | Low | Manifest checkpoint after every phase; crash recovery reads manifest |
| Token budget exhaustion mid-pipeline | High | Medium | Pre-calculate estimated cost; warn before execution; hard stop with partial results |
| Namespace collision | Medium | Low | Unique phase_id enforcement; sanitization; collision check before allocation |
| Child pipeline failure cascading | Medium | Medium | Graceful degradation: if 1 of N children fails, proceed with N-1 (minimum 2 required) |
| Context window overflow at deep recursion | High | Medium | Depth limit of 4; at each level only pass merged output upward, not full artifacts |
| Model-affinity bias in cross-model judging | Medium | Medium | Blind evaluation (strip model metadata); position bias mitigation preserved |

### Design Risks

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Abstraction leak — providers not truly uniform | Medium | Low | Strict interface contract; TypeScript-style duck typing validation |
| Flag complexity overwhelming users | Medium | Medium | Provide `--pipeline-spec` YAML for complex configs; keep simple cases simple |
| Debugging recursive failures is hard | High | Medium | Manifest.json provides full execution trace; each phase is inspectable independently |
| Diminishing quality returns at depth > 2 | Medium | High | Soft termination conditions; convergence plateau detection; user warnings |

### Compared to Approach A (Meta-Orchestrator)

| Dimension | Approach A | Approach B (This Proposal) |
|-----------|-----------|---------------------------|
| Conceptual elegance | Moderate — separate layer | High — self-similar recursion |
| Implementation complexity | Lower — thin orchestrator | Higher — recursive state management |
| Debuggability | Better — flat phase list | Harder — recursive call stack |
| Flexibility | Fixed two-level (orchestrator + pipeline) | N-level (truly recursive) |
| Code duplication | None (pipeline unchanged) | None (pipeline unchanged) |
| User mental model | "Pipeline with a coordinator on top" | "Pipelines all the way down" |
| Risk of over-engineering | Lower | Higher — users may create unnecessarily deep recursions |
| Extension path | Would need recursion eventually for 3+ levels | Naturally supports any depth |

### Recommended Safeguards

1. **Default max-depth of 3** -- prevents accidental deep recursion
2. **Token budget estimation before execution** -- show estimated cost, ask for confirmation
3. **Manifest-based crash recovery** -- never lose completed work
4. **Blind evaluation by default** -- prevent model-affinity bias
5. **Soft termination by default** -- suggest stopping when returns diminish
6. **Simple flag syntax for the common case** -- `--children` covers 90% of use cases; `--pipeline-spec` for the rest

---

## Summary

The recursive pipeline approach treats the adversarial protocol as a composable primitive. By introducing a `VariantProvider` abstraction and a `RecursiveController`, the existing 5-step protocol can invoke itself at multiple levels without code duplication. The user's 8-step cross-model workflow becomes a single command with `--recursive` and two `--children` specifications.

The primary tradeoff vs. Approach A is implementation complexity (recursive state management, deeper debugging surface) in exchange for conceptual elegance and natural extensibility to arbitrary depth. The recommended safeguards (depth limits, cost estimation, crash recovery, blind evaluation) keep the complexity manageable in practice.

**Estimated total effort**: 590-820 lines of new/modified SKILL.md protocol logic, implementable in 4-5 phases with incremental testing at each phase.
