# Adversarial 2.0: Final Refactor Specification

## Winner: Proposal A — Meta-Orchestrator Layer

### Consensus Score

| Debate Agent | Persona | Proposal A | Proposal B | Proposal C |
|-------------|---------|-----------|-----------|-----------|
| Agent A | Architect | **83.6** | 72.25 | 73.0 |
| Agent B | QA Engineer | **80.25** | 72.13 | 66.63 |
| Agent C | Performance | **81.0** | 65.63 | 69.25 |
| **Average** | | **81.6** | **70.0** | **69.6** |

**Result**: Proposal A wins unanimously with an 11.6-point margin over the nearest competitor. No tiebreaker needed.

**Consensus rationale**: Zero pipeline coupling, DAG-native parallelism, strongest error recovery, lowest migration risk, and cleanest separation of concerns. All three perspectives independently ranked A first.

---

## Compatibility Merge: Adopted Enhancements from B and C

Three features from the losing proposals are **non-conflicting and complementary** to Proposal A's architecture. They are adopted into the final spec.

### Merge 1: Blind Evaluation (from Proposal B)

**Source**: Proposal B, §Cross-Model Support, `blind_evaluation` (lines 621-626)

**What**: When a compare phase receives outputs from model-specific generate phases, strip model-identifying metadata before passing to the debate-orchestrator. Variants are presented as "Variant 1" and "Variant 2", not "Opus output" and "Haiku output".

**Why it's compatible**: Proposal A's Phase Executor already translates phase config into pipeline invocations. Adding metadata stripping between "collect phase outputs" and "pass to next phase" is a 1-step addition to the artifact routing layer. It does not change the pipeline, the DAG scheduler, or the return contract.

**Integration point**: In Proposal A's artifact routing, add a `blind_mode` phase config option:
```yaml
compare_phase:
  type: compare
  compare: ["{{opus_debate.merged_output}}", "{{haiku_debate.merged_output}}"]
  blind: true  # Strip model metadata from variant filenames and content headers
  depth: deep
```

**Estimated addition**: ~30 lines (metadata stripping function + config option)

**Verification**: Validate that merged output contains no model-name references in provenance annotations.

---

### Merge 2: Dry-Run Mode (from Proposal C)

**Source**: Proposal C, §Dry-Run Mode (lines ~66, detailed section)

**What**: `--dry-run` flag that validates the pipeline definition, displays the execution plan (phase order, parallelism levels, estimated artifact layout, token budget), and exits without executing any pipeline invocations.

**Why it's compatible**: Proposal A already requires DAG building and validation before execution. Dry-run simply stops after validation and renders the DAG instead of executing it. No architectural change — it's a boolean gate after the existing validation step.

**Integration point**: In Proposal A's Meta-Orchestrator, after DAG construction and validation:
```yaml
dry_run:
  trigger: "--dry-run flag present"
  action:
    - "Build and validate DAG (same as normal execution)"
    - "Render execution plan to stdout or file"
    - "Exit without executing any phases"
  output_format:
    execution_levels: "Phase groupings by dependency level"
    artifact_map: "Projected file layout under output directory"
    token_estimate: "Estimated total token cost based on phase count × depth × variant count"
    parallelism_plan: "Which phases run in parallel at each level"
```

**Estimated addition**: ~60 lines (render function + flag handling)

**Verification**: Dry-run output matches actual execution plan for the canonical 8-step workflow.

---

### Merge 3: Convergence Plateau Detection (from Proposal B)

**Source**: Proposal B, §Termination Conditions, `soft_stops` (lines 524-538)

**What**: When a meta-compare phase's convergence improvement over its input phases is < 5% for 2 consecutive levels, suggest termination. This prevents wasteful additional debate rounds when quality has plateaued.

**Why it's compatible**: Proposal A's Meta-Orchestrator already collects `convergence_score` from each phase's return contract. Adding a cross-phase convergence comparison between parent and child phases is a lightweight post-phase check. It does not change the pipeline's internal convergence detection — it adds a meta-level convergence assessment.

**Integration point**: In Proposal A's phase completion handler:
```yaml
convergence_plateau_detection:
  trigger: "Phase type is 'compare' AND depends_on phases also have convergence scores"
  computation:
    - "delta = current_phase.convergence - max(dependent_phases.convergence)"
    - "if delta < 0.05 AND previous_meta_compare.delta < 0.05:"
    - "  WARN: 'Convergence plateau detected ({delta}%). Further debate may not improve quality.'"
  behavior:
    default: "Log warning, continue execution"
    with_flag: "--auto-stop-plateau → halt remaining phases, return current best"
```

**Estimated addition**: ~25 lines (convergence comparison + warning logic)

**Verification**: Test with synthetic phases where convergence scores plateau.

---

## Features Explicitly NOT Adopted

| Feature | Source | Reason for Rejection |
|---------|--------|---------------------|
| VariantProvider abstraction | Proposal B | Requires refactoring existing Mode A/B code paths. Proposal A's black-box approach achieves the same result without touching pipeline internals. |
| Recursive self-invocation | Proposal B | Adds debugging complexity and serial-by-default execution. Proposal A's flat DAG achieves equivalent depth with better parallelism and inspectability. |
| Full DSL with variable interpolation | Proposal C | Cognitive overhead and Claude parsing reliability risk outweigh benefits. Proposal A's inline shorthand + YAML covers the same use cases with simpler syntax. |
| Preset system | Proposal C | Nice-to-have but adds maintenance burden. Can be added later as a thin layer over YAML templates. Not needed for v2.0. |
| Auto-detection of recursion need | Proposal B | Suggest-only policy adds complexity. Users who need multi-phase know they need it. |
| Model escalation (`--model-escalation`) | Proposal B | Too opinionated. Users can specify models per phase in the pipeline config. |

---

## Final Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  User Interface                          │
│  --pipeline "inline"  OR  --pipeline @file.yaml         │
│  [--dry-run]  [--blind]  [--auto-stop-plateau]          │
├─────────────────────────────────────────────────────────┤
│                Meta-Orchestrator Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │ DAG      │  │ Phase    │  │ Artifact     │          │
│  │ Builder  │→ │ Executor │→ │ Router       │          │
│  │ +Valid.  │  │          │  │ (+blind mode)│          │
│  └──────────┘  └──────────┘  └──────────────┘          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │ Manifest │  │ Error    │  │ Convergence  │          │
│  │ Manager  │  │ Handler  │  │ Monitor      │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────┤
│         Phase Executor (per-phase wrapper)                │
│  Translates phase config → Mode A or Mode B invocation   │
├─────────────────────────────────────────────────────────┤
│           Existing 5-Step Pipeline                        │
│  (diff → debate → score → plan → merge)                  │
│  *** ZERO CHANGES ***                                    │
└─────────────────────────────────────────────────────────┘
```

---

## Interface Specification

### New Flags

| Flag | Purpose | Mutual Exclusivity |
|------|---------|-------------------|
| `--pipeline <inline\|@path>` | Activate multi-phase mode | Exclusive with `--compare`, `--source`, `--generate`, `--agents` |
| `--dry-run` | Validate and display plan | Only with `--pipeline` |
| `--blind` | Strip model metadata in compare phases | Only with `--pipeline` |
| `--auto-stop-plateau` | Halt on convergence plateau | Only with `--pipeline` |
| `--pipeline-parallel <N>` | Max concurrent phases (default: 3) | Only with `--pipeline` |
| `--pipeline-resume` | Resume from manifest checkpoint | Only with `--pipeline` |

### Inline Shorthand

```bash
# The user's 8-step workflow in one command:
/sc:adversarial --pipeline "generate:opus:architect,opus:backend,opus:security -> generate:haiku:architect,haiku:backend,haiku:security -> compare" \
  --source ./spec.md --generate roadmap --depth deep --blind
```

**Parsing rules**:
- `->` separates phases (sequential dependency)
- `|` separates parallel phases at the same level
- `generate:<agents>` → Mode B phase with specified agents
- `compare` → Mode A phase using outputs of its dependencies
- `compare:<file1>,<file2>` → Mode A phase with explicit files

### YAML Format

```yaml
# adversarial-pipeline.yaml
version: "1.0"
defaults:
  depth: deep
  convergence: 0.80

phases:
  opus-debate:
    type: generate
    source: "./spec.md"
    generate: roadmap
    agents: ["opus:architect", "opus:backend", "opus:security"]

  haiku-debate:
    type: generate
    source: "./spec.md"
    generate: roadmap
    agents: ["haiku:architect", "haiku:backend", "haiku:security"]

  meta-compare:
    type: compare
    depends_on: ["opus-debate", "haiku-debate"]
    compare_artifacts: "merged_output"  # Takes merged output from each dependency
    depth: deep
    blind: true
```

**Invocation**: `/sc:adversarial --pipeline @adversarial-pipeline.yaml`

---

## Phase Schema

```yaml
phase_definition:
  id:
    type: string
    required: true
    validation: "unique within pipeline, alphanumeric + hyphens"

  type:
    type: enum
    values: ["generate", "compare"]
    required: true

  depends_on:
    type: list[string]
    default: []
    validation: "all referenced phase IDs must exist; no cycles"

  # Generate-specific (Mode B)
  source:
    type: string
    condition: "required when type=generate"
  generate:
    type: string
    condition: "required when type=generate"
  agents:
    type: list[string]
    condition: "required when type=generate"
    validation: "2-10 agents, format: model[:persona[:instruction]]"

  # Compare-specific (Mode A)
  compare_artifacts:
    type: enum
    values: ["merged_output", "all_variants"]
    default: "merged_output"
    description: "Which artifacts from dependency phases to compare"
  compare_files:
    type: list[string]
    condition: "optional for type=compare when comparing explicit files"

  # Common overrides
  depth:
    type: enum
    values: ["quick", "standard", "deep"]
    default: "inherit from pipeline defaults"
  convergence:
    type: float
    range: [0.50, 0.99]
    default: "inherit from pipeline defaults"
  blind:
    type: boolean
    default: false
  output_suffix:
    type: string
    default: "auto-derived from phase id"
```

---

## Artifact Output Structure

```
<output-dir>/
├── pipeline-manifest.yaml              # Phase registry + return contracts
├── phase--opus-debate/                 # Phase 1 output
│   ├── merged-output.md
│   └── adversarial/
│       ├── variant-1-opus-architect.md
│       ├── variant-2-opus-backend.md
│       ├── variant-3-opus-security.md
│       ├── diff-analysis.md
│       ├── debate-transcript.md
│       ├── base-selection.md
│       ├── refactor-plan.md
│       └── merge-log.md
├── phase--haiku-debate/                # Phase 2 output (parallel with Phase 1)
│   ├── merged-output.md
│   └── adversarial/
│       └── ... (same structure)
├── phase--meta-compare/                # Phase 3 output (depends on 1+2)
│   ├── merged-output.md
│   └── adversarial/
│       ├── variant-1-opus-debate.md    # Blind: no model name if --blind
│       ├── variant-2-haiku-debate.md
│       └── ... (same structure)
└── final-output.md                     # Symlink/copy of last phase's merged output
```

---

## Pipeline Return Contract

```yaml
pipeline_return_contract:
  version: "2.0"
  pipeline_status: "success | partial | failed"
  final_output_path: "<path to last phase's merged output>"
  final_convergence: "<last phase's convergence score>"
  total_phases: 3
  completed_phases: 3
  execution_time_estimate: "~45K tokens for standard depth"

  phase_results:
    - phase_id: "opus-debate"
      status: "success"
      merged_output_path: "<path>"
      convergence_score: 0.87
      artifacts_dir: "<path>"
      unresolved_conflicts: []

    - phase_id: "haiku-debate"
      status: "success"
      merged_output_path: "<path>"
      convergence_score: 0.82
      artifacts_dir: "<path>"
      unresolved_conflicts: []

    - phase_id: "meta-compare"
      status: "success"
      merged_output_path: "<path>"
      convergence_score: 0.91
      artifacts_dir: "<path>"
      unresolved_conflicts: []

  convergence_trend:
    - {phase: "opus-debate", score: 0.87}
    - {phase: "haiku-debate", score: 0.82}
    - {phase: "meta-compare", score: 0.91}
    plateau_detected: false

  # Standard per-phase contract preserved for backward compatibility
  per_phase_contracts: "Each phase returns FR-007 return_contract unchanged"
```

---

## Error Handling

### Phase-Level Failure Policies

```yaml
error_policies:
  halt_on_failure:
    description: "Default. If any phase fails, stop pipeline and return partial results."
    behavior: "Mark pipeline as 'partial', return completed phase results, skip dependent phases."
    manifest_update: "Record failed phase + reason, mark dependents as 'skipped'"

  continue_on_failure:
    description: "Skip failed phase's dependents, continue other branches."
    trigger: "--pipeline-on-error continue"
    behavior: "Failed phase marked, dependents skipped, parallel branches unaffected."

  resume:
    description: "Resume from last successful checkpoint."
    trigger: "--pipeline-resume"
    behavior: "Read manifest, validate checksums of completed phases, re-execute from first incomplete phase."
    validation: "If checksum mismatch on any completed phase, force re-execution from that point."
```

### Minimum Variant Constraint

If a compare phase receives fewer than 2 inputs (because dependency phases failed), the compare phase is automatically skipped with error: `"Cannot compare fewer than 2 artifacts. Phase {id} skipped."`

---

## Implementation Phases

### Phase 1: Pipeline Flag + DAG Builder (Foundation)
- Add `--pipeline` flag detection (step_0 guard before existing mode parsing)
- Implement inline shorthand parser
- Implement YAML file loader
- Build DAG from phase definitions
- Validate: cycle detection, reference integrity, type checks
- **Test**: Parse both inline and YAML formats; validate cycle detection

### Phase 2: Phase Executor + Artifact Routing
- Phase Executor: translate phase config → Mode A or Mode B pipeline invocation
- Artifact routing: resolve `merged_output` paths between phases
- Phase-scoped output directories
- Manifest creation and update after each phase
- **Test**: Single-phase pipeline (equivalent to existing behavior)

### Phase 3: DAG Scheduler + Parallelism
- Topological sort for execution ordering
- Parallel phase execution (up to `--pipeline-parallel` limit)
- Sequential gate enforcement for dependency edges
- **Test**: 2-phase parallel generate → 1-phase compare (the canonical workflow)

### Phase 4: Adopted Enhancements
- Blind evaluation (metadata stripping in artifact routing)
- Dry-run mode (validate + render + exit)
- Convergence plateau detection (cross-phase comparison)
- Resume from manifest
- **Test**: Full 8-step workflow end-to-end; dry-run accuracy; blind mode verification

### Estimated Total Addition
- **SKILL.md additions**: ~400-600 lines (meta-orchestrator protocol)
- **Separate refs/ file**: ~200-300 lines (pipeline schema, YAML format, examples)
- **Existing pipeline changes**: **Zero**
- **Existing Mode A/B changes**: **Zero**
- **Existing return contract changes**: **Zero**

---

## Validation Gate: S5 Complete

- [x] Winner selected by unanimous consensus (Proposal A, 81.6 avg)
- [x] Compatibility merge pass completed (3 features adopted from B/C)
- [x] Each merged feature verified against Proposal A architecture constraints
- [x] Rejected features documented with rationale
- [x] Final architecture diagram produced
- [x] Interface specification complete (flags, inline, YAML)
- [x] Phase schema defined
- [x] Artifact structure specified
- [x] Return contract extended (backward compatible)
- [x] Error handling defined
- [x] Implementation phases outlined with incremental testing

---

## Artifact Index

| # | File | Story | Description |
|---|------|-------|-------------|
| 01 | `01-gap-analysis.md` | S1 | 4 structural gaps identified |
| 02a | `02-proposal-A.md` | S2 | Meta-Orchestrator Layer (WINNER) |
| 02b | `02-proposal-B.md` | S2 | Recursive Pipeline |
| 02c | `02-proposal-C.md` | S2 | Phase Configuration DSL |
| 03 | `03-scoring-framework.md` | S3 | 17 sub-criteria weighted rubric |
| 04a | `04-debate-A.md` | S4 | Architect evaluation |
| 04b | `04-debate-B.md` | S4 | QA Engineer evaluation |
| 04c | `04-debate-C.md` | S4 | Performance Engineer evaluation |
| 05 | `05-adversarial2.0-final-refactor-spec.md` | S5 | This document |
