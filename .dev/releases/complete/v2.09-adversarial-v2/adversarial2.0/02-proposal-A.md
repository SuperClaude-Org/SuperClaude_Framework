# Proposal A: Meta-Orchestrator Layer

## Overview

This proposal adds a thin **meta-orchestration layer** above the existing 5-step adversarial pipeline. The core pipeline (diff, debate, score, plan, merge) remains completely unchanged. A new orchestration envelope accepts a phase definition, chains multiple pipeline invocations together, routes artifacts between phases, and returns a unified result.

The key insight: every phase in the user's workflow is itself a complete adversarial pipeline invocation. The meta-orchestrator's only job is to sequence them, feed outputs forward, and collect results. It does not participate in any pipeline step.

---

## Architecture

### Layered Design

```
┌─────────────────────────────────────────────────────┐
│              Meta-Orchestrator Layer                  │
│  (phase sequencing, artifact routing, error control) │
├─────────────────────────────────────────────────────┤
│         Phase Executor (per-phase wrapper)            │
│  (translates phase config → pipeline invocation)     │
├─────────────────────────────────────────────────────┤
│           Existing 5-Step Pipeline                    │
│  (diff → debate → score → plan → merge)              │
│  *** UNCHANGED ***                                    │
└─────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Does NOT |
|-----------|---------------|----------|
| **Meta-Orchestrator** | Parse `--pipeline` definition, build DAG, sequence phases, route artifacts, aggregate results, handle phase-level errors | Touch any pipeline step, make debate decisions, select bases |
| **Phase Executor** | Translate a single phase config into a Mode A or Mode B pipeline invocation, collect that invocation's return contract | Manage cross-phase state, know about other phases |
| **5-Step Pipeline** | Execute diff/debate/score/plan/merge exactly as today | Know it is inside a meta-pipeline; behaves identically to standalone invocation |

### Separation Principle

The meta-orchestrator interacts with the pipeline exclusively through:
1. **Input**: The same flags the pipeline accepts today (`--compare`, `--source`, `--generate`, `--agents`, `--depth`, etc.)
2. **Output**: The existing `return_contract` (path, score, artifacts dir, status, unresolved conflicts)

No internal pipeline API is exposed to the orchestrator. This is a **black-box composition** pattern.

---

## Interface Design

### New Flag: `--pipeline`

A single new top-level flag triggers meta-orchestration mode:

```bash
/sc:adversarial --pipeline <phase-definition> [--pipeline-options]
```

The `--pipeline` flag accepts a phase definition in one of two forms:

#### Form 1: Inline Phase Chain (simple cases)

```bash
/sc:adversarial --pipeline "generate:opus,haiku -> compare" \
  --source spec.md --generate roadmap --depth standard
```

Shorthand syntax: `<phase-type>:<params> -> <phase-type>:<params> -> ...`

#### Form 2: Phase Definition File (complex cases)

```bash
/sc:adversarial --pipeline @pipeline.yaml
```

Where `pipeline.yaml` contains the full phase definition schema (see below).

### Pipeline-Level Options

| Flag | Default | Description |
|------|---------|-------------|
| `--pipeline` | (none) | Phase definition (inline or @file) |
| `--pipeline-halt-on-failure` | `true` | Stop all phases if any fails |
| `--pipeline-output` | Auto-derived | Root output directory for all phases |
| `--pipeline-interactive` | `false` | Pause between phases for user review |
| `--pipeline-parallel` | `auto` | Parallel execution of independent phases |

### Backward Compatibility Gate

The mode parser is extended with a **third mode**:

```yaml
input_mode_parsing:
  step_0_pipeline_check:
    pipeline_signal: "--pipeline flag present"
    action: "Enter meta-orchestration mode; skip Mode A / Mode B detection"
    note: "The meta-orchestrator will invoke Mode A or Mode B per-phase internally"

  step_1_detect_mode:
    # UNCHANGED — only reached if --pipeline is absent
    mode_a_signal: "--compare flag present"
    mode_b_signal: "--source AND --generate AND --agents flags present"
    conflict: "If both Mode A and Mode B flags present → STOP with error"
    neither: "If neither mode detected → STOP with error"
```

When `--pipeline` is present, Mode A/B conflict checking is bypassed at the top level. Each phase internally invokes Mode A or Mode B through the existing validation path.

---

## Phase Schema

### Full Schema Definition

```yaml
# pipeline.yaml — Phase Definition Schema v1.0
pipeline:
  version: "1.0"
  name: "Cross-model adversarial comparison"   # Human-readable label
  description: "Generate roadmaps from two models, then meta-debate the results"

  # Global defaults — inherited by all phases unless overridden
  defaults:
    depth: "standard"
    convergence: 0.80
    output_root: "./adversarial-pipeline"       # Root dir for all phase artifacts

  # Phase definitions — executed in dependency order
  phases:
    - id: "generate-opus"
      type: "generate"                          # Maps to Mode B
      config:
        source: "spec.md"
        generate: "roadmap"
        agents:
          - "opus:architect"
          - "opus:backend"
          - "opus:security"
        depth: "deep"                           # Override global default
      depends_on: []                            # No dependencies — can run immediately

    - id: "generate-haiku"
      type: "generate"                          # Maps to Mode B
      config:
        source: "spec.md"
        generate: "roadmap"
        agents:
          - "haiku:architect"
          - "haiku:backend"
          - "haiku:security"
      depends_on: []                            # Independent — parallel with generate-opus

    - id: "meta-compare"
      type: "compare"                           # Maps to Mode A
      config:
        inputs:                                 # Artifact references from previous phases
          - phase: "generate-opus"
            artifact: "merged_output"           # References return_contract.merged_output_path
          - phase: "generate-haiku"
            artifact: "merged_output"
        depth: "deep"
      depends_on:                               # Explicit dependency declaration
        - "generate-opus"
        - "generate-haiku"
```

### Phase Types

| Type | Maps To | Required Config | Description |
|------|---------|----------------|-------------|
| `generate` | Mode B | `source`, `generate`, `agents` | Generate variants from source using agents |
| `compare` | Mode A | `inputs` (list of artifact refs) | Compare artifacts from prior phases or files |
| `compare-files` | Mode A | `files` (list of file paths) | Compare existing files (no phase dependency) |

### Artifact Reference Syntax

Phases reference outputs from earlier phases using structured references:

```yaml
inputs:
  - phase: "<phase-id>"
    artifact: "merged_output"          # The final merged file
  - phase: "<phase-id>"
    artifact: "debate_transcript"      # The debate transcript
  - phase: "<phase-id>"
    artifact: "variant:<N>"            # A specific variant (1-indexed)
```

Valid artifact keys map directly to the existing return contract and artifact directory:

| Artifact Key | Resolves To |
|-------------|-------------|
| `merged_output` | `return_contract.merged_output_path` |
| `debate_transcript` | `<artifacts_dir>/debate-transcript.md` |
| `diff_analysis` | `<artifacts_dir>/diff-analysis.md` |
| `base_selection` | `<artifacts_dir>/base-selection.md` |
| `refactor_plan` | `<artifacts_dir>/refactor-plan.md` |
| `merge_log` | `<artifacts_dir>/merge-log.md` |
| `variant:<N>` | `<artifacts_dir>/variant-<N>-*.md` |

---

## Artifact Routing

### Phase-Scoped Output Directories

Each phase writes to an isolated subdirectory. No filename collisions are possible.

```
<pipeline-output>/
├── manifest.yaml                          # Pipeline manifest (see below)
├── phase-1--generate-opus/
│   ├── merged-roadmap.md                  # Phase 1 merged output
│   └── adversarial/
│       ├── variant-1-opus-architect.md
│       ├── variant-2-opus-backend.md
│       ├── variant-3-opus-security.md
│       ├── diff-analysis.md
│       ├── debate-transcript.md
│       ├── base-selection.md
│       ├── refactor-plan.md
│       └── merge-log.md
├── phase-2--generate-haiku/
│   ├── merged-roadmap.md                  # Phase 2 merged output
│   └── adversarial/
│       ├── variant-1-haiku-architect.md
│       ├── ...
│       └── merge-log.md
├── phase-3--meta-compare/
│   ├── merged-roadmap.md                  # FINAL merged output
│   └── adversarial/
│       ├── variant-1-original.md          # Copy of phase-1 merged output
│       ├── variant-2-original.md          # Copy of phase-2 merged output
│       ├── ...
│       └── merge-log.md
└── final-output.md                        # Symlink/copy of last phase's merged output
```

### Directory Naming Convention

Phase directories use the pattern: `phase-<N>--<phase-id>/`

Where `<N>` is the 1-indexed execution order and `<phase-id>` is the user-defined ID from the phase schema. The numeric prefix ensures lexicographic ordering matches execution order.

### Artifact Resolution Algorithm

When Phase N references an artifact from Phase M:

```yaml
artifact_resolution:
  step_1: "Look up Phase M's return contract from the pipeline manifest"
  step_2: "Resolve artifact key to file path using the artifact key mapping table"
  step_3: "Verify file exists and is readable"
  step_4: "If artifact is 'merged_output', use return_contract.merged_output_path"
  step_5: "If artifact is a named artifact, resolve from return_contract.artifacts_dir"
  step_6: "If artifact is 'variant:<N>', glob for variant-<N>-*.md in artifacts_dir"
  error: "If resolution fails, halt pipeline with: 'Cannot resolve artifact <key> from phase <id>: file not found at <expected-path>'"
```

### Pipeline Manifest

The meta-orchestrator maintains a manifest file tracking all phases:

```yaml
# manifest.yaml — auto-generated, updated after each phase completes
pipeline_manifest:
  version: "1.0"
  pipeline_name: "Cross-model adversarial comparison"
  started_at: "2026-03-03T14:00:00Z"
  status: "in_progress"                          # running | completed | failed | partial

  phases:
    - id: "generate-opus"
      sequence: 1
      type: "generate"
      status: "completed"
      started_at: "2026-03-03T14:00:00Z"
      completed_at: "2026-03-03T14:12:00Z"
      output_dir: "phase-1--generate-opus/"
      return_contract:
        merged_output_path: "phase-1--generate-opus/merged-roadmap.md"
        convergence_score: "87%"
        artifacts_dir: "phase-1--generate-opus/adversarial/"
        status: "success"
        unresolved_conflicts: []

    - id: "generate-haiku"
      sequence: 2
      type: "generate"
      status: "completed"
      # ... same structure ...

    - id: "meta-compare"
      sequence: 3
      type: "compare"
      status: "pending"
      depends_on: ["generate-opus", "generate-haiku"]
      # ... return_contract populated after completion ...

  completed_at: null
  final_output: null                             # Set to last phase's merged output on completion
```

---

## Error Handling

### Phase-Level Error Model

Each phase can produce one of four statuses from the existing return contract:

| Phase Status | Meaning | Pipeline Behavior |
|-------------|---------|-------------------|
| `success` | Phase completed normally | Continue to dependent phases |
| `partial` | Phase completed with unresolved conflicts | Continue with warning (dependent phases proceed) |
| `failed` | Phase could not produce a merged output | Trigger failure policy |
| `timeout` | Phase exceeded time budget | Trigger failure policy |

### Failure Policies

```yaml
failure_handling:
  # Default: halt entire pipeline on first failure
  halt_on_failure:
    behavior: "Stop all pending phases immediately"
    completed_phases: "Preserved — all artifacts remain on disk"
    manifest: "Updated with failed status and error details"
    return: "Pipeline return contract with status='failed', partial_results populated"
    user_message: |
      Pipeline halted: Phase '<phase-id>' failed.
      Completed phases: <list>
      Artifacts preserved at: <pipeline-output>/
      Re-run with --pipeline-resume to continue from failure point.

  # Optional: continue past failures
  continue_on_failure:
    activation: "--pipeline-halt-on-failure false"
    behavior: "Skip dependent phases, continue independent phases"
    dependency_check: "If phase X fails and phase Y depends on X, skip Y with status='skipped'"
    independent_phases: "Continue execution"
    return: "Pipeline return contract with status='partial'"

  # Resume from failure
  resume:
    activation: "--pipeline-resume <pipeline-output>"
    behavior: "Read manifest, skip completed phases, retry failed/pending phases"
    validation: "Verify completed phase artifacts still exist on disk"
    reconfig: "Allow reconfiguring failed phase parameters before retry"
```

### Error Propagation Rules

```yaml
error_propagation:
  phase_fails_no_dependents:
    action: "Record failure, check for other runnable phases"
    pipeline_status: "partial (if other phases succeed) or failed (if all fail)"

  phase_fails_with_dependents:
    halt_mode: "Stop everything immediately"
    continue_mode: "Mark all transitive dependents as 'skipped'"

  partial_phase_result:
    action: "Propagate partial output to dependents with warning flag"
    dependent_phases: "Receive the partial artifact but log: 'Input from phase <id> was partial — unresolved conflicts: <list>'"

  all_phases_succeed:
    pipeline_status: "success"

  mixed_results:
    pipeline_status: "partial"
    detail: "Per-phase status in manifest"
```

---

## Concurrency Model

### Dependency-Driven Parallelism

The meta-orchestrator builds a DAG from phase `depends_on` declarations and executes phases with maximum parallelism:

```yaml
concurrency:
  dag_construction:
    step_1: "Parse all phase definitions"
    step_2: "Build directed acyclic graph from depends_on edges"
    step_3: "Validate: no cycles (STOP with error if cycle detected)"
    step_4: "Compute execution levels (topological sort)"

  execution_strategy:
    level_0: "All phases with no dependencies — run in parallel"
    level_N: "All phases whose dependencies are all in levels 0..N-1 — run in parallel once level N-1 completes"

  parallel_execution:
    mechanism: "Task agent delegation — one Task agent per phase"
    max_concurrent: 3                        # Default; configurable via --pipeline-parallel <N>
    resource_note: "Each phase is a full pipeline invocation — 3 concurrent is a reasonable default"

  sequential_fallback:
    activation: "--pipeline-parallel 1"
    behavior: "Execute phases one at a time in topological order"
```

### Concrete Example: User's 8-Step Workflow

The user's workflow maps to a 3-phase pipeline with this execution plan:

```
Execution Level 0 (parallel):
  ├── Phase: generate-opus    (Mode B, 3 agents)
  └── Phase: generate-haiku   (Mode B, 3 agents)

Execution Level 1 (after Level 0 completes):
  └── Phase: meta-compare     (Mode A, 2 inputs from Level 0)
```

Level 0 phases run simultaneously via parallel Task agents. Level 1 waits for both to complete, then runs.

### DAG Validation

```yaml
dag_validation:
  cycle_detection:
    algorithm: "Topological sort — if sort fails, cycle exists"
    error: "STOP: 'Pipeline has circular dependency: <phase-a> → <phase-b> → ... → <phase-a>'"

  missing_dependency:
    check: "Every depends_on reference must match a declared phase id"
    error: "STOP: 'Phase <id> depends on unknown phase: <missing-id>'"

  orphan_detection:
    check: "Warn if any phase has no dependents and is not the terminal phase"
    severity: "WARN (not blocking)"
```

---

## Backward Compatibility

### Compatibility Matrix

| Invocation Style | Behavior | Changed? |
|-----------------|----------|----------|
| `/sc:adversarial --compare a.md,b.md` | Mode A, single pipeline | **No change** |
| `/sc:adversarial --source s.md --generate roadmap --agents opus,haiku` | Mode B, single pipeline | **No change** |
| `/sc:adversarial --compare a.md,b.md --source s.md ...` | Error: mode conflict | **No change** |
| `/sc:adversarial --pipeline "..."` | **NEW**: Meta-orchestration mode | New capability |
| `/sc:adversarial --pipeline "..." --compare ...` | Error: `--pipeline` is exclusive | New validation |

### Isolation Guarantees

1. **No existing flag semantics change**: `--compare`, `--source`, `--generate`, `--agents` behave identically when `--pipeline` is absent.
2. **No pipeline internals leak**: The 5-step protocol has zero awareness of being inside a meta-pipeline. It receives the same inputs and produces the same outputs.
3. **No artifact directory changes for standalone mode**: Single-invocation mode still writes to `adversarial/` directly. Phase-scoped directories only apply in pipeline mode.
4. **Return contract is extended, not modified**: The existing return contract fields remain. Pipeline mode adds additional fields in a wrapper (see Return Contract section).

### Flag Exclusivity Rule

```yaml
pipeline_exclusivity:
  rule: "--pipeline flag is mutually exclusive with --compare, --source, --generate, --agents"
  rationale: "Pipeline mode defines its own phases internally. Top-level mode flags are meaningless."
  exception: "Global defaults (--depth, --convergence, --output, --interactive, --focus) are allowed and applied as pipeline-level defaults"
  error: "STOP: '--pipeline cannot be combined with --compare/--source/--generate/--agents. Define modes within pipeline phases.'"
```

---

## Return Contract

### Pipeline Return Contract

The meta-orchestrator returns an extended contract that wraps per-phase contracts:

```yaml
pipeline_return_contract:
  # Top-level summary
  pipeline_name: "<name from definition>"
  pipeline_status: "success | partial | failed"
  total_phases: <N>
  completed_phases: <N>
  failed_phases: <N>
  skipped_phases: <N>

  # Final output (convenience — points to terminal phase's merged output)
  final_output_path: "<path to terminal phase merged output>"
  final_convergence_score: "<terminal phase convergence>"

  # Pipeline-level artifacts
  pipeline_output_dir: "<root pipeline output directory>"
  manifest_path: "<path to manifest.yaml>"

  # Per-phase results (ordered by execution sequence)
  phase_results:
    - phase_id: "<id>"
      phase_type: "generate | compare | compare-files"
      status: "success | partial | failed | skipped"
      return_contract:
        # Standard per-phase return contract (unchanged from existing)
        merged_output_path: "<path>"
        convergence_score: "<percentage>"
        artifacts_dir: "<path>"
        status: "success | partial | failed"
        unresolved_conflicts: ["<list>"]
      execution_time_seconds: <N>
      error_message: null                    # Populated on failure

    - phase_id: "<id>"
      # ... same structure per phase ...

  # Aggregate metrics
  total_execution_time_seconds: <N>
  total_variants_generated: <N>
  total_debate_rounds: <N>
```

### Contract Compatibility

When `--pipeline` is not used, the return contract is exactly the existing one. No wrapper. No extra fields. The pipeline return contract only appears in pipeline mode.

When another command invokes `sc:adversarial` with `--pipeline`, it can:
1. Read `final_output_path` for the end result (simple case)
2. Iterate `phase_results` for per-phase inspection (advanced case)
3. Use `manifest_path` for full audit trail

---

## Concrete Example: User's 8-Step Workflow

The gap analysis describes an 8-step user workflow. Here is how it maps to the meta-orchestrator:

### Original 8 Steps (Manual)

1. Opus generates roadmap with 3 architect/backend/security agents
2. Adversarial debate among opus variants
3. Opus variants merged into best-of roadmap
4. Haiku generates roadmap with same 3 agent roles
5. Adversarial debate among haiku variants
6. Haiku variants merged into best-of roadmap
7. Cross-model comparison: opus-merged vs haiku-merged
8. Final meta-debate produces unified roadmap

### Single-Command Expression

```bash
/sc:adversarial --pipeline @cross-model.yaml \
  --depth deep --convergence 0.85 \
  --pipeline-output ./release/adversarial
```

With `cross-model.yaml`:

```yaml
pipeline:
  version: "1.0"
  name: "Cross-model roadmap adversarial"
  description: "Generate roadmaps with opus and haiku, then meta-debate the results"

  defaults:
    depth: "standard"
    convergence: 0.80

  phases:
    - id: "opus-debate"
      type: "generate"
      config:
        source: "spec.md"
        generate: "roadmap"
        agents:
          - "opus:architect"
          - "opus:backend"
          - "opus:security"
        depth: "deep"
      depends_on: []

    - id: "haiku-debate"
      type: "generate"
      config:
        source: "spec.md"
        generate: "roadmap"
        agents:
          - "haiku:architect"
          - "haiku:backend"
          - "haiku:security"
        depth: "deep"
      depends_on: []

    - id: "cross-model-meta"
      type: "compare"
      config:
        inputs:
          - phase: "opus-debate"
            artifact: "merged_output"
          - phase: "haiku-debate"
            artifact: "merged_output"
        depth: "deep"
        convergence: 0.85
      depends_on:
        - "opus-debate"
        - "haiku-debate"
```

### Inline Shorthand (Same Workflow)

For users who do not want to write YAML files:

```bash
/sc:adversarial --pipeline \
  "generate:opus:architect,opus:backend,opus:security -> \
   generate:haiku:architect,haiku:backend,haiku:security -> \
   compare:@1,@2" \
  --source spec.md --generate roadmap --depth deep
```

Inline shorthand rules:
- `->` separates phases
- `generate:<agent-specs>` creates a Mode B phase
- `compare:@<N>,@<M>` creates a Mode A phase referencing phase outputs by position
- `@N` is a positional artifact reference (1-indexed, refers to Nth phase's merged output)
- Global `--source`, `--generate`, `--depth` apply as defaults to all generate phases

### Execution Trace

```
[META] Pipeline: Cross-model roadmap adversarial (3 phases)
[META] DAG: Level 0 = [opus-debate, haiku-debate], Level 1 = [cross-model-meta]
[META] Executing Level 0 (2 phases in parallel)...

  [PHASE opus-debate] Mode B: 3 agents from spec.md
    [STEP 1/5] Diff analysis across 3 opus variants...
    [STEP 2/5] Adversarial debate (deep, 3 rounds)...
    [STEP 3/5] Hybrid scoring & base selection...
    [STEP 4/5] Refactoring plan...
    [STEP 5/5] Merge execution...
  [PHASE opus-debate] COMPLETE: convergence 91%, merged → phase-1--opus-debate/merged-roadmap.md

  [PHASE haiku-debate] Mode B: 3 agents from spec.md
    [STEP 1/5] Diff analysis across 3 haiku variants...
    [STEP 2/5] Adversarial debate (deep, 3 rounds)...
    [STEP 3/5] Hybrid scoring & base selection...
    [STEP 4/5] Refactoring plan...
    [STEP 5/5] Merge execution...
  [PHASE haiku-debate] COMPLETE: convergence 84%, merged → phase-2--haiku-debate/merged-roadmap.md

[META] Level 0 complete. Executing Level 1...

  [PHASE cross-model-meta] Mode A: comparing opus-merged vs haiku-merged
    [STEP 1/5] Diff analysis across 2 merged roadmaps...
    [STEP 2/5] Adversarial debate (deep, 3 rounds)...
    [STEP 3/5] Hybrid scoring & base selection...
    [STEP 4/5] Refactoring plan...
    [STEP 5/5] Merge execution...
  [PHASE cross-model-meta] COMPLETE: convergence 88%, merged → phase-3--cross-model-meta/merged-roadmap.md

[META] Pipeline COMPLETE: 3/3 phases succeeded
[META] Final output: ./release/adversarial/phase-3--cross-model-meta/merged-roadmap.md
```

---

## Implementation Complexity Assessment

### Change Impact Analysis

| Component | Change Type | Effort | Risk |
|-----------|------------|--------|------|
| Input mode parser (SKILL.md:418-477) | Add step_0 pipeline check | Low | Low — additive guard clause |
| New: Meta-orchestrator module | New code | High | Medium — new logic but no pipeline changes |
| New: Phase executor | New code | Medium | Low — thin wrapper over existing pipeline invocation |
| New: DAG builder + validator | New code | Medium | Low — standard topological sort |
| New: Artifact resolver | New code | Medium | Medium — path resolution has edge cases |
| New: Manifest manager | New code | Low | Low — YAML read/write |
| New: Pipeline return contract | Schema extension | Low | Low — additive, no breaking changes |
| Existing 5-step pipeline | **No changes** | Zero | Zero |
| Existing Mode A logic | **No changes** | Zero | Zero |
| Existing Mode B logic | **No changes** | Zero | Zero |
| Existing error handling | **No changes** | Zero | Zero |
| Existing return contract | **No changes** | Zero | Zero |

### Estimated Token Budget for Implementation

| Task | Tokens |
|------|--------|
| Meta-orchestrator core logic (SKILL.md additions) | 3,000-4,000 |
| Phase schema definition and validation | 1,500-2,000 |
| Inline shorthand parser | 1,000-1,500 |
| Artifact routing and resolution | 1,500-2,000 |
| Error handling and resume | 1,000-1,500 |
| Pipeline return contract | 500-800 |
| Manifest management | 500-800 |
| Examples and documentation | 1,000-1,500 |
| **Total SKILL.md additions** | **10,000-14,000** |

### Implementation Phases

1. **Phase 1**: Pipeline flag parsing + phase schema validation + sequential execution (MVP)
2. **Phase 2**: DAG-based parallel execution + artifact resolution
3. **Phase 3**: Inline shorthand parser + resume capability
4. **Phase 4**: Pipeline-level interactive mode + manifest management

---

## Risk Analysis

### Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|------|------------|--------|------------|
| R1 | SKILL.md size explosion (already ~1100 lines) | High | Medium | Place meta-orchestrator in a separate `refs/pipeline-protocol.md` referenced from SKILL.md. Keep SKILL.md additions to ~200 lines of phase schema + flag definition. |
| R2 | Parallel phase execution exceeds token budget | Medium | High | Default `--pipeline-parallel` to 3. Document token cost per phase (~15K for standard depth). Warn when estimated total exceeds 50K. |
| R3 | Artifact resolution fails on edge cases (variant glob patterns, special characters in paths) | Medium | Medium | Strict path sanitization. Use manifest as source of truth for paths rather than glob patterns. |
| R4 | Inline shorthand syntax ambiguity | Medium | Low | Make inline shorthand a convenience layer only. Always recommend YAML for complex pipelines. Parser rejects ambiguous input with helpful error pointing to YAML form. |
| R5 | Phase resume after failure produces inconsistent state | Low | High | Manifest records checksums of completed phase outputs. Resume validates checksums before proceeding. If mismatch, force re-run of affected phase. |
| R6 | DAG cycles from user error | Low | Low | Topological sort fails fast with clear cycle path in error message. |
| R7 | Steelman requirement weakened in meta-compare phase | Low | High | No risk — each phase invokes the full 5-step pipeline including steelman requirement. Meta-orchestrator cannot bypass pipeline steps. |
| R8 | Position bias in meta-compare (opus always variant-1) | Medium | Medium | Document recommendation: randomize input order in compare phases. Consider adding `--shuffle-inputs` flag to pipeline config. |

### Key Design Tradeoffs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|------------|-----------|
| Black-box composition | Orchestrator cannot see inside pipeline | White-box with shared state | Preserves pipeline integrity; eliminates risk of unintended side effects |
| Phase-scoped directories | Isolated dirs per phase | Shared adversarial/ dir with prefixes | Cleaner separation; no filename collision risk; easier cleanup |
| YAML + inline shorthand | Two input forms | YAML only | YAML for power, inline for convenience. Low parser cost. |
| DAG over linear chain | Full DAG support | Simple linear sequencing | DAG needed for parallel phases (user's workflow has 2 parallel generate phases). Linear would serialize unnecessarily. |
| Extend return contract (wrapper) | New pipeline_return_contract wrapping existing | Modify existing return_contract | Zero backward compatibility risk. Existing consumers see no change. |
| `--pipeline` as exclusive flag | Cannot combine with Mode A/B flags | Allow Mode A/B flags as defaults | Prevents confusion about which flags apply where. Phase configs are self-contained. |

---

## Summary

This proposal adds multi-phase orchestration to `sc:adversarial` through a clean layered architecture:

- **Zero changes to the proven 5-step pipeline** — all debate quality, steelman requirements, position bias mitigation, and convergence detection remain untouched
- **Single new flag** (`--pipeline`) with two input forms (inline shorthand and YAML file)
- **DAG-based execution** enabling parallel independent phases and sequential dependent phases
- **Phase-scoped artifact isolation** preventing filename collisions and enabling clean artifact routing
- **Extended return contract** that wraps per-phase results without modifying the existing contract
- **Incremental implementability** — MVP (sequential execution) is achievable in Phase 1, with parallelism and resume added incrementally
- **Full backward compatibility** — all existing invocations behave identically
