# Gap Analysis: sc:adversarial Single-Command Multi-Phase Orchestration

## Executive Summary

The current `sc:adversarial` protocol (SKILL.md, ~1100 lines) is a well-architected 5-step pipeline that handles **single-phase** adversarial debate and merge. However, it fundamentally **cannot** execute the 8-step cross-model meta-debate workflow described in the user's use case as a single atomic command. This analysis identifies 4 structural gaps that block true multi-phase orchestration.

---

## Gap 1: Mode Mutual Exclusivity (Hard Block)

### Current Constraint
**SKILL.md:422-423** — Input mode parsing enforces strict mutual exclusivity:

```yaml
conflict: "If both Mode A and Mode B flags present → STOP with error:
  'Cannot use --compare with --source/--generate/--agents'"
```

### What This Blocks
The user's workflow requires **both modes in sequence within one invocation**:
1. **Phase 1** (Mode B × N): Generate debate artifacts using different models
2. **Phase 2** (Mode A): Compare the generated debate outputs

The current architecture forces these into separate chat sessions because a single invocation can only be Mode A **or** Mode B, never a pipeline of B→A.

### Refactor Target
- `input_mode_parsing.step_1_detect_mode` — must support a **pipeline mode** where Mode B feeds into Mode A
- New flag needed: e.g., `--pipeline` or `--meta` to signal multi-phase intent
- The conflict check must be relaxed for pipeline mode while remaining strict for direct invocations

### Severity: **CRITICAL** — This is the primary architectural blocker.

---

## Gap 2: No Phase Orchestration Layer (Hard Block)

### Current Architecture
The 5-step protocol is **flat and single-pass**:

```
Step 1 (Diff) → Step 2 (Debate) → Step 3 (Score) → Step 4 (Plan) → Step 5 (Merge)
```

Each step assumes a single set of variants flowing through one pipeline instance. There is no concept of:
- Running the full 5-step pipeline multiple times with different configurations
- Feeding the output of one pipeline run as input to another
- Coordinating multiple parallel pipeline instances

### What This Blocks
The user's workflow needs:
1. **Pipeline Instance 1**: Opus model generates debate → produces `debate-A.md`
2. **Pipeline Instance 2**: Haiku model generates debate → produces `debate-B.md`
3. **Pipeline Instance 3**: Compare `debate-A.md` and `debate-B.md` → final verdict

This is a **DAG of pipeline invocations**, not a single pipeline.

### Refactor Target
- New **meta-orchestration layer** above the 5-step protocol
- Phase definition schema: `phases: [{mode, config, depends_on}]`
- Artifact handoff mechanism between phases
- Phase-level error handling (if Phase 1 fails, Phase 2 cannot proceed)

### Severity: **CRITICAL** — Without this, multi-phase is impossible in one command.

---

## Gap 3: No Artifact State Persistence Between Phases (Medium Block)

### Current Architecture
Artifacts are written to a flat `adversarial/` directory (SKILL.md:292-304):

```
<output-dir>/
├── <merged-output>.md
└── adversarial/
    ├── variant-N-<agent>.md
    ├── diff-analysis.md
    ├── debate-transcript.md
    ├── base-selection.md
    ├── refactor-plan.md
    └── merge-log.md
```

The return contract (SKILL.md:344-350) provides paths but no **phase awareness**:

```yaml
return_contract:
  merged_output_path: "<path>"
  convergence_score: "<percentage>"
  artifacts_dir: "<path>"
  status: "success | partial | failed"
  unresolved_conflicts: ["<list>"]
```

### What This Blocks
- Phase 2 cannot discover Phase 1's outputs without hardcoded path knowledge
- Multiple pipeline instances would **collide** on the same artifact filenames (`diff-analysis.md`, `debate-transcript.md`, etc.)
- No metadata connects a Phase 2 input back to its Phase 1 origin

### Refactor Target
- **Phase-scoped artifact directories**: `adversarial/phase-1/`, `adversarial/phase-2/`, `adversarial/phase-3/`
- **Extended return contract** with phase metadata:
  ```yaml
  phase_id: "phase-1"
  phase_type: "generate" | "compare" | "meta-compare"
  parent_phases: []
  outputs: {merged: "<path>", artifacts_dir: "<path>"}
  ```
- **Manifest file** (`adversarial/manifest.json`) tracking all phases, their configs, dependencies, and outputs

### Severity: **MEDIUM** — Solvable with directory conventions, but needs design.

---

## Gap 4: Compare/Generate Pipeline Unification (Medium Block)

### Current Architecture
Mode A (compare) and Mode B (generate) are completely separate code paths:
- Mode A: Loads existing files → copies to `variant-N-original.md` → enters 5-step pipeline
- Mode B: Parses agent specs → dispatches Task agents → writes `variant-N-<model>-<persona>.md` → enters 5-step pipeline

After initial loading/generation, both converge into the same 5-step pipeline. But there is **no unified abstraction** that treats "get me N variants" as a single operation regardless of source.

### What This Blocks
- A meta-orchestrator cannot uniformly compose phases because "produce variants" has two completely different interfaces
- Pipeline mode needs to express: "Phase 1 generates via Mode B; Phase 2 compares Phase 1's merged outputs via Mode A" — but these are incompatible parameter sets

### Refactor Target
- **Variant Provider abstraction**: A unified interface that produces N variants regardless of source
  - `FileVariantProvider`: Reads existing files (current Mode A)
  - `GenerativeVariantProvider`: Dispatches agents (current Mode B)
  - `PipelineVariantProvider`: Takes outputs from previous phases
- The 5-step pipeline takes `VariantProvider` as input, not raw mode flags
- Meta-orchestrator composes providers and pipelines

### Severity: **MEDIUM** — Clean abstraction needed but doesn't block a quick implementation.

---

## Architectural Dependency Graph

```
Gap 1 (Mode Exclusivity) ──────┐
                                ├──→ Gap 2 (Phase Orchestration) ──→ Gap 3 (State Persistence)
Gap 4 (Pipeline Unification) ──┘
```

- Gaps 1 & 4 are **prerequisites** for Gap 2
- Gap 3 is a **consequence** of Gap 2 (once you have phases, you need state)
- All 4 gaps must be addressed for full single-command orchestration

---

## Current Strengths to Preserve

| Strength | Location | Why It Matters |
|----------|----------|----------------|
| 5-step protocol rigor | SKILL.md:66-254 | Core debate quality — do not weaken |
| Steelman requirement | SKILL.md:117, 784-789 | Key differentiator from naive comparison |
| Hybrid scoring (quant+qual) | SKILL.md:141-198 | Evidence-based selection — keep intact |
| Position bias mitigation | SKILL.md:182-186 | Anti-ordering-bias — critical for fairness |
| Convergence detection | SKILL.md:906-955 | Smart debate termination — preserve |
| Agent delegation model | SKILL.md:352-371 | Clean separation of concerns |
| Error handling matrix | SKILL.md:311-337 | Robust failure modes — extend for phases |
| Return contract | SKILL.md:339-350 | Machine-readable — extend, don't replace |

---

## Proposed Solution Space (High-Level)

Three viable approaches emerge from this analysis:

### Approach A: Meta-Orchestrator Layer
Add a thin orchestration layer **above** the existing 5-step pipeline. The pipeline itself stays unchanged. A new `--pipeline` flag accepts a phase definition that chains multiple pipeline invocations.

**Pros**: Minimal changes to proven pipeline, clean separation
**Cons**: New abstraction layer, potential complexity

### Approach B: Recursive Pipeline
Allow the 5-step pipeline to accept other pipeline outputs as variants. The pipeline becomes self-referential — a "debate of debates" is just another pipeline invocation where variants happen to be previous merge outputs.

**Pros**: Elegant, single abstraction
**Cons**: Recursive complexity, harder to debug, phase state management in recursion

### Approach C: Phase Configuration DSL
Define a YAML/inline DSL for multi-phase workflows that the existing skill interprets. Each phase is a pipeline invocation with explicit inputs, outputs, and dependencies.

**Pros**: Declarative, composable, inspectable
**Cons**: DSL design complexity, learning curve, parsing overhead

---

## Validation Gate: S1 Complete

- [x] Mode-coupling limits identified (Gap 1)
- [x] Phase orchestration boundaries mapped (Gap 2)
- [x] Artifact handoff/state persistence gaps documented (Gap 3)
- [x] Compare/generate pipeline unification gaps analyzed (Gap 4)
- [x] Dependency graph between gaps established
- [x] Current strengths catalogued for preservation
- [x] Solution space sketched (3 approaches for S2 brainstorm)
