# Proposal C: Phase Configuration DSL

## Overview

This proposal introduces a declarative Phase Configuration DSL that enables multi-phase adversarial workflows through composable pipeline definitions. Rather than modifying the existing 5-step protocol internals, the DSL sits above it as a **pipeline composition layer** -- a DAG scheduler that treats each 5-step pipeline invocation as an atomic unit of work.

The core insight: the user's 8-step workflow is not a single pipeline with more steps. It is a **directed acyclic graph of pipeline invocations** where outputs from upstream pipelines become inputs to downstream pipelines. The DSL makes this graph explicit, inspectable, and reusable.

**Design Principles**:
1. The 5-step pipeline is a black box -- the DSL composes pipelines, never reaches inside them
2. Both inline flags and external YAML files express the same underlying graph model
3. Common workflows ship as named presets; custom workflows use the same syntax
4. The DSL is validated and dry-runnable before any pipeline executes
5. Steelman requirements and position bias mitigation are inherited properties of each pipeline invocation, not DSL-level concerns

---

## Architecture

### Layered Execution Model

```
┌─────────────────────────────────────────────────┐
│  User Interface Layer                            │
│  (inline flags OR YAML file OR preset name)      │
├─────────────────────────────────────────────────┤
│  DSL Parser + Validator                          │
│  Parses → validates → resolves variables →       │
│  builds execution DAG                            │
├─────────────────────────────────────────────────┤
│  Phase Orchestrator                              │
│  Topological sort → execute phases →             │
│  artifact handoff → error propagation            │
├─────────────────────────────────────────────────┤
│  Pipeline Executor (existing)                    │
│  5-step protocol per phase invocation            │
│  (unchanged from current SKILL.md)               │
├─────────────────────────────────────────────────┤
│  Artifact Store                                  │
│  Phase-scoped directories + manifest.json        │
└─────────────────────────────────────────────────┘
```

### Component Responsibilities

**DSL Parser**: Accepts inline flags, YAML file path, or preset name. Produces a normalized `PipelineGraph` -- a set of phase definitions with typed edges representing data dependencies.

**Validator**: Before execution begins, checks: all referenced phases exist, dependency graph is acyclic, variable references resolve to declared outputs, model/persona specs are valid, file paths exist (for Mode A phases).

**Phase Orchestrator**: Performs topological sort on the `PipelineGraph`. Executes phases in dependency order. Phases with no mutual dependencies may execute concurrently (future optimization). Manages artifact handoff between phases through the Artifact Store.

**Pipeline Executor**: The existing 5-step protocol, invoked once per phase. Receives a `PhaseConfig` (mode, parameters, input paths) and returns a `PhaseResult` (status, output paths, convergence score). No modifications to the 5-step logic itself.

**Artifact Store**: Phase-scoped directory layout with a `manifest.json` tracking all phases, their configurations, outputs, and lineage.

### New Flag Surface

```
/sc:adversarial --pipeline <preset-or-yaml-path> [--dry-run] [global-overrides...]
```

| Flag | Purpose | Example |
|------|---------|---------|
| `--pipeline` | Activate multi-phase mode (preset name or YAML path) | `--pipeline meta-debate` |
| `--pipeline-file` | Explicit YAML file path (alternative to auto-detect) | `--pipeline-file ./my-workflow.yaml` |
| `--dry-run` | Validate and display execution plan without running | `--dry-run` |
| `--phase-output` | Root output directory for all phases | `--phase-output ./results/` |

When `--pipeline` is present, the existing mode mutual exclusivity check (SKILL.md:422-423) is bypassed. Each phase within the pipeline declares its own mode independently.

---

## DSL Syntax

### YAML File Format (Full)

```yaml
# adversarial-pipeline.yaml
version: "1.0"
name: "cross-model-meta-debate"
description: "Generate debates from multiple models, then compare the merged outputs"

# Global defaults applied to all phases unless overridden
defaults:
  depth: standard
  convergence: 0.80
  output_root: "./adversarial-output"

# Phase definitions -- each is one 5-step pipeline invocation
phases:
  opus-debate:
    type: generate
    source: "./spec.md"
    generate: roadmap
    agents:
      - opus:architect:"focus on scalability and long-term maintainability"
      - opus:security:"focus on threat modeling and compliance"
      - opus:performance:"focus on optimization and resource efficiency"
    depth: deep
    output: "{{output_root}}/phase-opus"

  haiku-debate:
    type: generate
    source: "./spec.md"
    generate: roadmap
    agents:
      - haiku:architect:"focus on pragmatic simplicity"
      - haiku:backend:"focus on implementation feasibility"
      - haiku:analyzer:"focus on risk identification"
    depth: standard
    output: "{{output_root}}/phase-haiku"

  meta-compare:
    type: compare
    depends_on:
      - opus-debate
      - haiku-debate
    compare:
      - "{{opus-debate.merged_output_path}}"
      - "{{haiku-debate.merged_output_path}}"
    depth: deep
    convergence: 0.85
    output: "{{output_root}}/phase-meta"
```

### Schema Definition

```yaml
# Pipeline DSL Schema v1.0
pipeline_schema:
  version:
    type: string
    required: true
    pattern: "^\\d+\\.\\d+$"

  name:
    type: string
    required: true
    max_length: 80

  description:
    type: string
    required: false

  defaults:
    type: object
    required: false
    properties:
      depth:
        type: enum
        values: [quick, standard, deep]
        default: standard
      convergence:
        type: float
        range: [0.50, 0.99]
        default: 0.80
      output_root:
        type: string
        default: "./adversarial-output"
      interactive:
        type: boolean
        default: false
      focus:
        type: string
        default: null

  phases:
    type: map
    required: true
    min_entries: 1
    max_entries: 20
    key_pattern: "^[a-z][a-z0-9_-]{0,39}$"
    value_schema: phase_definition

phase_definition:
  type:
    type: enum
    values: [generate, compare, meta-compare]
    required: true

  # Required for type: generate
  source:
    type: string
    required_when: "type == generate"
  generate:
    type: string
    required_when: "type == generate"
  agents:
    type: list
    items: agent_spec
    min_items: 2
    max_items: 10
    required_when: "type == generate"

  # Required for type: compare and meta-compare
  compare:
    type: list
    items: string  # file paths or variable references
    min_items: 2
    max_items: 10
    required_when: "type in [compare, meta-compare]"

  # Dependency declaration
  depends_on:
    type: list
    items: string  # phase names
    required: false
    default: []

  # Per-phase parameter overrides
  depth:
    type: enum
    values: [quick, standard, deep]
    required: false
    inherit: defaults.depth
  convergence:
    type: float
    range: [0.50, 0.99]
    required: false
    inherit: defaults.convergence
  interactive:
    type: boolean
    required: false
    inherit: defaults.interactive
  focus:
    type: string
    required: false
    inherit: defaults.focus
  output:
    type: string
    required: false
    default: "{{output_root}}/{{phase_name}}"

agent_spec:
  type: string
  pattern: "^[a-z]+(:([a-z]+)(:\\\"[^\\\"]+\\\")?)?$"
  description: "model[:persona[:\"instruction\"]] -- same format as existing --agents"
```

### Inline Flag Format (Compact)

For simpler workflows, the entire pipeline can be expressed inline without a YAML file. The syntax uses semicolons to separate phases and arrows to declare dependencies.

```bash
# Inline syntax: --pipeline "phase1_name:type:params; phase2_name:type:params <- phase1_name"
/sc:adversarial --pipeline "inline" \
  --phase "opus:generate:./spec.md:roadmap:opus:architect,opus:security,opus:performance --depth deep" \
  --phase "haiku:generate:./spec.md:roadmap:haiku:architect,haiku:backend,haiku:analyzer" \
  --phase "meta:compare:{{opus.merged}},{{haiku.merged}} <- opus,haiku --depth deep --convergence 0.85"
```

Breakdown of `--phase` syntax:

```
--phase "<name>:<type>:<type-specific-args> [<- dep1,dep2] [--flag value ...]"
```

| Segment | Description | Example |
|---------|-------------|---------|
| `name` | Phase identifier | `opus` |
| `type` | Phase type | `generate` or `compare` |
| Type args (generate) | `source:generate_type:agent1,agent2,...` | `./spec.md:roadmap:opus:arch,opus:sec` |
| Type args (compare) | `path1,path2,...` | `{{opus.merged}},{{haiku.merged}}` |
| `<- deps` | Dependency list (optional) | `<- opus,haiku` |
| `--flag value` | Per-phase overrides | `--depth deep` |

### Preset Invocation

Named presets provide a single-token shorthand for common workflows:

```bash
# Use a built-in preset
/sc:adversarial --pipeline meta-debate --source ./spec.md --generate roadmap

# Use a preset with overrides
/sc:adversarial --pipeline meta-debate --source ./spec.md --generate roadmap --depth deep
```

---

## Phase Types

### `generate`

Invokes the existing Mode B pipeline: dispatches agents against a source file, runs the 5-step protocol on the generated variants, produces a merged output.

```yaml
phase_name:
  type: generate
  source: "<path>"           # --source equivalent
  generate: "<artifact_type>" # --generate equivalent
  agents:                    # --agents equivalent
    - "<model>[:persona[:\"instruction\"]]"
    - "<model>[:persona[:\"instruction\"]]"
```

**Mapping to existing protocol**: This phase translates directly to a single invocation of the current Mode B path. The Phase Orchestrator constructs the equivalent of:

```
/sc:adversarial --source <source> --generate <type> --agents <agents> [--depth ...] [--convergence ...]
```

**Outputs exposed to downstream phases**:
- `merged_output_path`: Path to the final merged artifact
- `convergence_score`: Final convergence percentage
- `artifacts_dir`: Path to the phase's `adversarial/` directory
- `status`: success | partial | failed
- `variants`: Map of variant names to their file paths

### `compare`

Invokes the existing Mode A pipeline: takes 2-10 existing files, runs the 5-step protocol to debate and merge them.

```yaml
phase_name:
  type: compare
  compare:
    - "<path_or_variable_ref>"
    - "<path_or_variable_ref>"
  depends_on:
    - "<upstream_phase_name>"
```

**Mapping to existing protocol**: Translates to a single Mode A invocation:

```
/sc:adversarial --compare <resolved_path1>,<resolved_path2>[,...] [--depth ...] [--convergence ...]
```

**Outputs**: Same schema as `generate`.

### `meta-compare`

Semantically identical to `compare`, but signals intent: the inputs are themselves outputs of prior adversarial pipelines. This distinction serves two purposes:

1. **Documentation**: Makes the pipeline's meta-level structure legible
2. **Validation**: The validator enforces that all `compare` entries in a `meta-compare` phase reference outputs of other phases (not raw files)

```yaml
phase_name:
  type: meta-compare
  compare:
    - "{{phase_a.merged_output_path}}"
    - "{{phase_b.merged_output_path}}"
  depends_on:
    - phase_a
    - phase_b
```

At execution time, `meta-compare` and `compare` are handled identically by the Pipeline Executor. The type distinction is purely a DSL-level semantic constraint.

### Future Extension: `custom`

Reserved for user-defined phase types that execute arbitrary scripts or tools. Not in scope for initial implementation, but the schema reserves the type name:

```yaml
phase_name:
  type: custom
  command: "uv run python analyze.py {{prev.artifacts_dir}}"
  outputs:
    result_path: "./custom-output.md"
```

---

## Dependency Graph

### Declaration

Dependencies are declared explicitly via `depends_on`:

```yaml
phases:
  a:
    type: generate
    # ... (no depends_on -- root node)

  b:
    type: generate
    # ... (no depends_on -- root node, parallel with a)

  c:
    type: compare
    depends_on: [a, b]   # waits for both a and b
    compare:
      - "{{a.merged_output_path}}"
      - "{{b.merged_output_path}}"

  d:
    type: meta-compare
    depends_on: [c]      # waits for c only
    compare:
      - "{{c.merged_output_path}}"
      - "./external-baseline.md"
```

### Implicit Dependency Inference

When a phase references another phase's output via variable interpolation (e.g., `{{a.merged_output_path}}`) but omits `depends_on`, the validator **infers** the dependency and adds it automatically. This is a convenience -- explicit `depends_on` is preferred for clarity.

```yaml
# These two are equivalent:
# Explicit:
c:
  depends_on: [a, b]
  compare: ["{{a.merged_output_path}}", "{{b.merged_output_path}}"]

# Implicit (inferred from variable refs):
c:
  compare: ["{{a.merged_output_path}}", "{{b.merged_output_path}}"]
```

### Resolution Algorithm

```
1. Parse all phase definitions
2. For each phase, collect:
   a. Explicit depends_on entries
   b. Variable references ({{phase_name.field}}) → extract phase_name
3. Union (a) and (b) to produce the full dependency set per phase
4. Build adjacency list representation of the DAG
5. Run cycle detection (Kahn's algorithm or DFS-based)
   - If cycle detected → STOP with error listing the cycle path
6. Topological sort → produce execution order
7. Identify parallelism opportunities:
   - Phases with identical resolved dependency sets can execute concurrently
   - Example: phases a and b both have no dependencies → parallel
```

### Execution Semantics

```
Given topological order [a, b, c, d]:
  Level 0: {a, b}  -- no dependencies, execute in parallel (or sequentially)
  Level 1: {c}     -- depends on a, b; waits for both
  Level 2: {d}     -- depends on c; waits for c
```

Phase execution is currently sequential (one pipeline at a time) in the initial implementation. Parallel phase execution is a future optimization that requires no DSL changes -- only the Phase Orchestrator needs modification.

### Error Propagation

When a phase fails:

```yaml
error_propagation:
  phase_failure:
    action: "Mark phase as FAILED in manifest"
    downstream: "All phases that depend_on this phase are marked BLOCKED"
    independent: "Phases with no dependency path to the failed phase continue"

  partial_success:
    condition: "Phase returns status: partial"
    action: "Warn but allow dependent phases to proceed"
    flag: "Dependent phases receive a warning annotation"

  abort:
    condition: "Root phase fails OR all leaf phases blocked"
    action: "Terminate pipeline, produce partial manifest"
```

---

## Variable Interpolation

### Syntax

Variables use double-brace syntax: `{{phase_name.field_name}}`

### Available Fields Per Phase

Every completed phase exposes these fields for downstream reference:

| Field | Type | Description |
|-------|------|-------------|
| `merged_output_path` | string | Absolute path to the merged output file |
| `convergence_score` | float | Final convergence percentage (0.0-1.0) |
| `artifacts_dir` | string | Absolute path to the phase's adversarial/ directory |
| `status` | string | "success", "partial", or "failed" |
| `variants.N` | string | Path to variant N (1-indexed) |
| `diff_analysis_path` | string | Path to diff-analysis.md |
| `debate_transcript_path` | string | Path to debate-transcript.md |
| `base_selection_path` | string | Path to base-selection.md |
| `refactor_plan_path` | string | Path to refactor-plan.md |
| `merge_log_path` | string | Path to merge-log.md |

### Built-in Variables

| Variable | Description |
|----------|-------------|
| `{{output_root}}` | The root output directory (from defaults or --phase-output) |
| `{{phase_name}}` | The current phase's name (for use in output path templates) |
| `{{timestamp}}` | ISO 8601 timestamp at pipeline start |

### Resolution Rules

1. Variables are resolved **lazily** -- at the point a phase begins execution, not at parse time
2. If a variable references a phase that has not yet completed, execution halts with an error (this should never happen if the dependency graph is correct, but serves as a safety net)
3. If a variable references a field on a FAILED phase, execution of the dependent phase is blocked
4. String interpolation is recursive up to 3 levels (a variable's value may contain another variable reference)
5. Unresolvable variables after 3 passes produce a validation error

### Example Resolution

```yaml
phases:
  opus:
    type: generate
    source: "./spec.md"
    generate: roadmap
    agents: [opus:architect, opus:security]
    output: "{{output_root}}/opus-debate"
    # After execution:
    # opus.merged_output_path = "./adversarial-output/opus-debate/roadmap.md"
    # opus.artifacts_dir = "./adversarial-output/opus-debate/adversarial/"

  meta:
    type: compare
    depends_on: [opus, haiku]
    compare:
      - "{{opus.merged_output_path}}"   # resolves to "./adversarial-output/opus-debate/roadmap.md"
      - "{{haiku.merged_output_path}}"  # resolves to "./adversarial-output/haiku-debate/roadmap.md"
```

---

## Preset Workflows

### Preset Definition Format

Presets are pipeline YAML files with parameterized placeholders, shipped as part of the skill:

```yaml
# presets/meta-debate.yaml
version: "1.0"
name: "meta-debate"
description: "Cross-model adversarial meta-debate: two model cohorts debate independently, then their merged outputs are compared"

parameters:
  source:
    required: true
    description: "Source file to generate from"
    flag: "--source"
  generate:
    required: true
    description: "Artifact type to generate"
    flag: "--generate"
  model_a:
    default: "opus"
    description: "Primary model"
  model_b:
    default: "haiku"
    description: "Secondary model"
  personas_a:
    default: ["architect", "security", "performance"]
    description: "Persona set for model A"
  personas_b:
    default: ["architect", "backend", "analyzer"]
    description: "Persona set for model B"

defaults:
  depth: standard
  convergence: 0.80

phases:
  model-a-debate:
    type: generate
    source: "{{params.source}}"
    generate: "{{params.generate}}"
    agents: "{{params.model_a}}:{{personas_a[0]}},{{params.model_a}}:{{personas_a[1]}},{{params.model_a}}:{{personas_a[2]}}"
    depth: deep

  model-b-debate:
    type: generate
    source: "{{params.source}}"
    generate: "{{params.generate}}"
    agents: "{{params.model_b}}:{{personas_b[0]}},{{params.model_b}}:{{personas_b[1]}},{{params.model_b}}:{{personas_b[2]}}"

  meta-compare:
    type: meta-compare
    depends_on: [model-a-debate, model-b-debate]
    compare:
      - "{{model-a-debate.merged_output_path}}"
      - "{{model-b-debate.merged_output_path}}"
    depth: deep
    convergence: 0.85
```

### Built-in Presets

| Preset Name | Phases | Description |
|-------------|--------|-------------|
| `meta-debate` | 3 | Two model cohorts generate independently, merged outputs compared |
| `triple-debate` | 4 | Three model cohorts, then 3-way meta-compare |
| `iterative-refine` | 2 | Generate once, then compare merged output against original source |
| `cascade` | N | Progressive refinement: each phase compares previous merge with new generation |
| `tournament` | log2(N)+1 | Tournament bracket: N generators, pairwise comparisons, finals |

### The User's 8-Step Workflow as a Preset

The motivating use case from the gap analysis maps directly:

```yaml
# presets/meta-debate.yaml (concrete instance)
version: "1.0"
name: "cross-model-roadmap"

phases:
  # Steps 1-5: Opus generates 3 variants → 5-step pipeline → merged opus roadmap
  opus-debate:
    type: generate
    source: "./project-spec.md"
    generate: roadmap
    agents:
      - opus:architect:"focus on scalability and long-term maintainability"
      - opus:security:"focus on threat modeling and compliance"
      - opus:performance:"focus on optimization and resource efficiency"
    depth: deep

  # Steps 1-5 (again): Haiku generates 3 variants → 5-step pipeline → merged haiku roadmap
  haiku-debate:
    type: generate
    source: "./project-spec.md"
    generate: roadmap
    agents:
      - haiku:architect:"focus on pragmatic simplicity"
      - haiku:backend:"focus on implementation feasibility"
      - haiku:analyzer:"focus on risk identification"

  # Steps 6-8: Compare the two merged roadmaps → final verdict
  meta-compare:
    type: meta-compare
    depends_on: [opus-debate, haiku-debate]
    compare:
      - "{{opus-debate.merged_output_path}}"
      - "{{haiku-debate.merged_output_path}}"
    depth: deep
    convergence: 0.85
```

**Invocation**:

```bash
# Using the preset with parameters
/sc:adversarial --pipeline meta-debate --source ./project-spec.md --generate roadmap

# Using a YAML file directly
/sc:adversarial --pipeline-file ./cross-model-roadmap.yaml

# Using inline phases (equivalent but verbose)
/sc:adversarial --pipeline inline \
  --phase "opus:generate:./project-spec.md:roadmap:opus:architect,opus:security,opus:performance --depth deep" \
  --phase "haiku:generate:./project-spec.md:roadmap:haiku:architect,haiku:backend,haiku:analyzer" \
  --phase "meta:compare:{{opus.merged}},{{haiku.merged}} <- opus,haiku --depth deep --convergence 0.85"
```

---

## Validation

### Pre-Execution Validation Pipeline

Before any phase executes, the entire pipeline definition passes through a multi-stage validator:

```yaml
validation_pipeline:
  stage_1_syntax:
    description: "YAML/inline syntax is well-formed"
    checks:
      - "YAML parses without errors"
      - "All required fields present per schema"
      - "Field types match schema expectations"
      - "Phase names match pattern ^[a-z][a-z0-9_-]{0,39}$"
      - "Agent specs match pattern model[:persona[:\"instruction\"]]"
    failure: "STOP with parse error and line number"

  stage_2_graph:
    description: "Dependency graph is valid"
    checks:
      - "All depends_on references point to declared phase names"
      - "No cycles in dependency graph (topological sort succeeds)"
      - "No self-references (phase depends on itself)"
      - "At least one root phase (no dependencies) exists"
      - "At least one leaf phase (nothing depends on it) exists"
    failure: "STOP with graph error and cycle path if applicable"

  stage_3_variables:
    description: "All variable references are resolvable"
    checks:
      - "All {{phase.field}} references point to declared phases"
      - "Referenced fields are valid output fields (merged_output_path, etc.)"
      - "Variable references only target upstream phases (per dependency order)"
      - "No circular variable references"
      - "Built-in variables (output_root, phase_name, timestamp) always resolve"
    failure: "STOP with unresolvable variable error"

  stage_4_semantics:
    description: "Phase configurations are semantically valid"
    checks:
      - "generate phases have source, generate, agents"
      - "compare/meta-compare phases have compare list with 2-10 entries"
      - "meta-compare compare entries all reference phase outputs (not raw files)"
      - "Agent count per generate phase: 2-10"
      - "Depth values in {quick, standard, deep}"
      - "Convergence values in [0.50, 0.99]"
      - "Source files exist (for generate phases with literal paths)"
    failure: "STOP with semantic error"

  stage_5_resource:
    description: "Resource feasibility check"
    checks:
      - "Total phase count <= 20"
      - "Estimated token budget within limits"
      - "Output directory is writable"
    failure: "WARN (soft) or STOP if critical"
```

### Validation Output

```
Pipeline Validation Report
==========================
Syntax:     PASS (3 phases, 6 agents, 1 preset parameter)
Graph:      PASS (DAG with 2 roots, 1 leaf, depth=2)
Variables:  PASS (4 variable references, all resolvable)
Semantics:  PASS (2 generate phases, 1 meta-compare phase)
Resources:  PASS (estimated 3 pipeline invocations, ~45K tokens)

Pipeline is valid. Ready to execute.
```

---

## Dry-Run Mode

Activated via `--dry-run`, this mode runs the full validation pipeline plus generates a human-readable execution plan without invoking any pipeline.

### Dry-Run Output Format

```
/sc:adversarial --pipeline meta-debate --source ./spec.md --generate roadmap --dry-run
```

Produces:

```
=== Adversarial Pipeline: Dry Run ===

Pipeline: meta-debate (cross-model adversarial meta-debate)
Source: ./spec.md (exists, 2,847 lines, 38KB)
Output root: ./adversarial-output/

--- Execution Plan ---

Level 0 (parallel-eligible):
  [1] opus-debate (generate)
      Source: ./spec.md
      Generate: roadmap
      Agents: opus:architect, opus:security, opus:performance
      Depth: deep | Convergence: 0.80
      Output: ./adversarial-output/opus-debate/
      Estimated: 3 variants → 5-step pipeline → merged output

  [2] haiku-debate (generate)
      Source: ./spec.md
      Generate: roadmap
      Agents: haiku:architect, haiku:backend, haiku:analyzer
      Depth: standard | Convergence: 0.80
      Output: ./adversarial-output/haiku-debate/
      Estimated: 3 variants → 5-step pipeline → merged output

Level 1:
  [3] meta-compare (meta-compare)
      Inputs: {{opus-debate.merged_output_path}}, {{haiku-debate.merged_output_path}}
      Depends on: [1] opus-debate, [2] haiku-debate
      Depth: deep | Convergence: 0.85
      Output: ./adversarial-output/meta-compare/
      Estimated: 2 variants → 5-step pipeline → final merged output

--- Summary ---
Total phases: 3
Total pipeline invocations: 3
Estimated agents spawned: 6 (generate) + 3x debate orchestrators
Dependency depth: 2 levels
Parallelism opportunities: Level 0 (2 phases)

--- Artifact Layout (projected) ---
./adversarial-output/
├── manifest.json
├── opus-debate/
│   ├── roadmap.md (merged)
│   └── adversarial/
│       ├── variant-1-opus-architect.md
│       ├── variant-2-opus-security.md
│       ├── variant-3-opus-performance.md
│       ├── diff-analysis.md
│       ├── debate-transcript.md
│       ├── base-selection.md
│       ├── refactor-plan.md
│       └── merge-log.md
├── haiku-debate/
│   ├── roadmap.md (merged)
│   └── adversarial/
│       ├── variant-1-haiku-architect.md
│       ├── variant-2-haiku-backend.md
│       ├── variant-3-haiku-analyzer.md
│       ├── diff-analysis.md
│       ├── debate-transcript.md
│       ├── base-selection.md
│       ├── refactor-plan.md
│       └── merge-log.md
└── meta-compare/
    ├── final-roadmap.md (merged)
    └── adversarial/
        ├── variant-1-original.md (opus merged)
        ├── variant-2-original.md (haiku merged)
        ├── diff-analysis.md
        ├── debate-transcript.md
        ├── base-selection.md
        ├── refactor-plan.md
        └── merge-log.md

Validation: PASS
Status: Ready to execute (remove --dry-run to proceed)
```

### Dry-Run as Debugging Tool

The dry-run output serves multiple purposes:
1. **User confidence**: See exactly what will happen before committing tokens
2. **Debugging**: Verify variable resolution, dependency ordering, agent configurations
3. **Documentation**: The dry-run output can be saved as a record of intended execution
4. **Cost estimation**: Rough token budget projection before execution

---

## Artifact Store

### Phase-Scoped Directory Layout

```
<output_root>/
├── manifest.json                    # Pipeline-level metadata and phase registry
├── <phase-1-name>/
│   ├── <merged-output>.md           # Final merged artifact for this phase
│   └── adversarial/
│       ├── variant-N-<suffix>.md    # Variant files (same as current)
│       ├── diff-analysis.md
│       ├── debate-transcript.md
│       ├── base-selection.md
│       ├── refactor-plan.md
│       └── merge-log.md
├── <phase-2-name>/
│   └── ...
└── <phase-N-name>/
    └── ...
```

### Manifest Schema

```yaml
# manifest.json
{
  "pipeline": {
    "name": "cross-model-roadmap",
    "version": "1.0",
    "started_at": "2026-03-03T14:30:00Z",
    "completed_at": "2026-03-03T14:47:23Z",
    "status": "success"
  },
  "phases": {
    "opus-debate": {
      "type": "generate",
      "status": "success",
      "started_at": "2026-03-03T14:30:01Z",
      "completed_at": "2026-03-03T14:38:12Z",
      "config": {
        "source": "./spec.md",
        "generate": "roadmap",
        "agents": ["opus:architect", "opus:security", "opus:performance"],
        "depth": "deep",
        "convergence": 0.80
      },
      "outputs": {
        "merged_output_path": "./adversarial-output/opus-debate/roadmap.md",
        "convergence_score": 0.87,
        "artifacts_dir": "./adversarial-output/opus-debate/adversarial/",
        "status": "success",
        "unresolved_conflicts": []
      },
      "depends_on": [],
      "depended_by": ["meta-compare"]
    },
    "haiku-debate": {
      "type": "generate",
      "status": "success",
      "started_at": "2026-03-03T14:30:01Z",
      "completed_at": "2026-03-03T14:35:44Z",
      "config": { "..." : "..." },
      "outputs": { "..." : "..." },
      "depends_on": [],
      "depended_by": ["meta-compare"]
    },
    "meta-compare": {
      "type": "meta-compare",
      "status": "success",
      "started_at": "2026-03-03T14:38:13Z",
      "completed_at": "2026-03-03T14:47:23Z",
      "config": {
        "compare": [
          "./adversarial-output/opus-debate/roadmap.md",
          "./adversarial-output/haiku-debate/roadmap.md"
        ],
        "depth": "deep",
        "convergence": 0.85
      },
      "outputs": {
        "merged_output_path": "./adversarial-output/meta-compare/final-roadmap.md",
        "convergence_score": 0.91,
        "artifacts_dir": "./adversarial-output/meta-compare/adversarial/",
        "status": "success",
        "unresolved_conflicts": []
      },
      "depends_on": ["opus-debate", "haiku-debate"],
      "depended_by": []
    }
  },
  "execution_order": [
    ["opus-debate", "haiku-debate"],
    ["meta-compare"]
  ]
}
```

### Return Contract Extension

The existing return contract (SKILL.md:344-350) is extended for pipeline mode:

```yaml
pipeline_return_contract:
  # Existing fields (preserved)
  merged_output_path: "<path to final phase's merged output>"
  convergence_score: "<final phase's convergence>"
  artifacts_dir: "<final phase's artifacts directory>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list>"]

  # New pipeline-specific fields
  pipeline:
    manifest_path: "<path to manifest.json>"
    phase_count: N
    phases_succeeded: N
    phases_failed: N
    total_agents_spawned: N
    execution_time_seconds: N
```

---

## Implementation Complexity Assessment

### Component Breakdown

| Component | Complexity | Lines (est.) | Dependencies |
|-----------|-----------|-------------|--------------|
| DSL Parser (YAML) | Medium | 150-200 | PyYAML or manual YAML parsing via Claude |
| DSL Parser (inline) | Medium | 100-150 | String parsing, regex |
| Schema Validator | Medium | 200-250 | Custom validation logic |
| Graph Builder + Cycle Detection | Low | 80-100 | Kahn's algorithm |
| Variable Interpolator | Medium | 100-120 | Regex + lazy resolution |
| Phase Orchestrator | High | 200-250 | DAG scheduler, error propagation |
| Artifact Store + Manifest | Low | 80-100 | JSON write, directory management |
| Dry-Run Renderer | Low | 100-120 | String formatting |
| Preset Loader | Low | 60-80 | YAML load + parameter substitution |
| Pipeline flag integration | Low | 40-60 | Flag parsing modification |
| **Total** | **Medium-High** | **~1100-1400** | |

### Key Consideration: This is a Prompt-Based System

The existing `sc:adversarial` skill is not traditional code -- it is a SKILL.md prompt that Claude interprets. The DSL implementation therefore has two possible paths:

**Path 1: DSL-as-prompt-extension** -- The DSL schema, validation rules, and orchestration logic are added as new sections in SKILL.md. Claude interprets the DSL at runtime using the prompt instructions. No Python code needed.

- **Pro**: Consistent with existing architecture, no build step, zero runtime dependencies
- **Con**: Relies on Claude to correctly parse YAML, validate graphs, and maintain state across phases. Error-prone for complex DAGs. No compile-time guarantees.
- **Estimate**: +400-600 lines added to SKILL.md

**Path 2: DSL-as-Python-preprocessor** -- A Python module parses and validates the DSL, produces a normalized execution plan, then invokes the existing SKILL.md pipeline N times with the correct parameters per phase.

- **Pro**: Deterministic parsing, reliable graph validation, real cycle detection
- **Con**: Introduces Python dependency for what is currently a pure-prompt skill. Requires integration with the `superclaude` CLI.
- **Estimate**: ~800-1000 lines of Python + ~200 lines added to SKILL.md

**Recommended path**: Path 1 (prompt-extension) for initial release, with validation logic expressed as structured YAML instructions that Claude follows. Path 2 as a hardening step if reliability issues emerge with complex pipelines.

### Implementation Phases

**Phase 1 (MVP)**: Pipeline flag + YAML parser + sequential phase execution + manifest
- Supports: `--pipeline-file` with YAML, linear and simple DAG workflows
- Duration estimate: 2-3 sessions

**Phase 2 (Presets)**: Built-in presets + parameter substitution + `--pipeline <name>`
- Supports: Named presets with overridable parameters
- Duration estimate: 1-2 sessions

**Phase 3 (Inline)**: Inline `--phase` flag syntax + dry-run mode
- Supports: Full inline DSL, `--dry-run` output
- Duration estimate: 1-2 sessions

**Phase 4 (Hardening)**: Advanced validation, error propagation, partial pipeline resume
- Supports: Robust error handling, resume from failed phase
- Duration estimate: 1-2 sessions

---

## Risk Analysis

### Risk 1: DSL Complexity Overhead (Severity: HIGH)

**Description**: The DSL introduces a non-trivial learning curve. Users must understand YAML syntax, phase types, variable interpolation, and dependency declaration before they can compose custom pipelines.

**Mitigation**: Presets cover the most common workflows (especially `meta-debate`). Users who only need the 8-step workflow never write YAML -- they use `--pipeline meta-debate`. Custom DSL is an advanced feature.

**Residual risk**: Medium. Power users will encounter DSL debugging friction.

### Risk 2: Claude Parsing Reliability (Severity: HIGH)

**Description**: If implemented as Path 1 (prompt-extension), Claude must reliably parse YAML, validate DAGs, track variable state, and orchestrate multi-phase execution purely from prompt instructions. LLMs are not deterministic parsers.

**Mitigation**:
- Constrain YAML to a strict subset (no anchors, no merge keys, no multi-document)
- Provide explicit parsing algorithms as step-by-step YAML instructions
- Use the existing TodoWrite system to track phase execution state
- Dry-run mode catches most issues before execution

**Residual risk**: High for complex DAGs (>5 phases). Medium for the common 3-phase meta-debate.

### Risk 3: Artifact Collision (Severity: MEDIUM)

**Description**: Multiple phases writing to the same output root could collide if phase names are not unique or if directory creation races.

**Mitigation**: Phase names are validated as unique during schema validation. Directory creation is sequential (phases execute in topological order). Manifest tracks all paths.

**Residual risk**: Low.

### Risk 4: Token Budget Explosion (Severity: HIGH)

**Description**: A 3-phase pipeline invokes the 5-step protocol 3 times. Each invocation involves multiple agent dispatches. The total token consumption could be 3-5x a single invocation.

**Mitigation**:
- Dry-run mode provides estimated token budget before execution
- Resource feasibility check in validation stage
- Per-phase depth control allows mixing `deep` and `quick` phases
- `quick` depth for meta-compare phases reduces redundant debate depth

**Residual risk**: Medium. Users need awareness that multi-phase is expensive.

### Risk 5: State Loss Between Phases (Severity: MEDIUM)

**Description**: In the prompt-based architecture, Claude's context window must hold state across multiple sequential pipeline invocations. Long pipelines could exceed context limits.

**Mitigation**:
- Manifest.json provides persistent state external to Claude's context
- Each phase reads its inputs from disk, not from memory
- Phase results are written to manifest immediately on completion
- The orchestrator can re-read manifest if context is lost

**Residual risk**: Low for 3-phase pipelines. Medium for 5+ phases.

### Risk 6: Backward Compatibility (Severity: LOW)

**Description**: The `--pipeline` flag is entirely additive. Existing `--compare` and `--source` invocations are unchanged. The mode mutual exclusivity check only relaxes when `--pipeline` is present.

**Mitigation**: No existing behavior changes. The DSL is a new code path triggered only by new flags.

**Residual risk**: Negligible.

### Risk 7: Steelman and Position Bias Preservation (Severity: LOW)

**Description**: The steelman requirement (SKILL.md:117) and position bias mitigation (SKILL.md:182-186) are properties of the 5-step pipeline, not the orchestration layer. Since the DSL composes pipeline invocations without modifying them, these properties are automatically preserved.

**Mitigation**: None needed -- architectural choice ensures preservation by construction.

**Residual risk**: Negligible.

---

## Summary

Proposal C introduces a declarative Phase Configuration DSL that composes adversarial pipeline invocations into multi-phase workflows. The design preserves all existing pipeline strengths (steelman, position bias mitigation, hybrid scoring) by treating the 5-step protocol as an opaque building block. The DSL addresses all four gaps identified in the gap analysis:

| Gap | How Addressed |
|-----|---------------|
| Gap 1 (Mode Exclusivity) | `--pipeline` flag bypasses mutual exclusivity; each phase declares its own mode |
| Gap 2 (Phase Orchestration) | DAG-based phase orchestrator executes phases in topological order |
| Gap 3 (Artifact Persistence) | Phase-scoped directories + manifest.json provide full lineage tracking |
| Gap 4 (Pipeline Unification) | Phase types (`generate`, `compare`, `meta-compare`) provide a uniform abstraction |

The primary trade-off is **design complexity for composability**. The DSL is more powerful than a simple `--meta` flag (Approach A) but requires more design investment. Presets reduce the learning curve for common workflows, and dry-run mode provides confidence before execution.
