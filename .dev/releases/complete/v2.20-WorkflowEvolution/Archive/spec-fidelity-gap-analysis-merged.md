<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant B (spec-fidelity-gap-analysis.md) -->
<!-- Merge date: 2026-03-09 -->

# Spec-Fidelity Gap Analysis: Pipeline Validation Deficiency

**Date**: 2026-03-09
**Context**: v2.19-roadmap-validate sprint post-mortem
**Status**: Problem identified, solutions proposed, not yet implemented

---

## 1. Problem Statement

<!-- Source: Base (original) -->
The SuperClaude pipeline (spec → roadmap → tasklist → sprint execution) has **no spec-fidelity validation gate** at any boundary. Every existing gate checks structural properties (file exists, has frontmatter, meets minimum length) but none asks: "Does this output faithfully represent the input?"

This was discovered when a post-sprint validation of v2.19-roadmap-validate found 4 implementation deviations from the spec. Root cause analysis traced **3 of 4 deviations back to the roadmap generation step** — the roadmap simplified, renamed, and dropped spec details, and those errors propagated unchecked through the tasklist and into the implementation.

### The Core Irony

The `sc:roadmap-protocol` skill docs already contain explicit spec-fidelity prompts (e.g., "Does the roadmap faithfully represent the spec?"), but these are **documented in skill reference files, not wired into the CLI executor**. The validation infrastructure exists conceptually; it's just not connected.

### Correct Validation Layering Principle

<!-- Source: Variant A (GPT briefing), lines 36-47 — merged per Change #1 -->
The intended validation model should be:

- Roadmap validated against spec
- Tasklist validated against roadmap
- Execution validated against tasklist

**Not:**
- Tasklist validated against original spec
- Execution validated against original spec

That distinction is central. Each artifact is validated against its immediate upstream source of truth. If the roadmap deviates from the spec, that is caught at the roadmap gate — not by having the sprint runner compare its output against the original spec. This preserves clean layering and prevents validation-layer coupling.

---

## 2. Evidence: The v2.19 Case Study

### 2.1 What Was Built

<!-- Source: Base (original) -->
FR-050: `superclaude roadmap validate` — a post-pipeline validation subcommand checking roadmap artifacts across 7 dimensions.

**Spec**: `.dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md`

### 2.2 Implementation Deviations Found

| # | Deviation | Severity | Origin |
|---|-----------|----------|--------|
| 1 | `ValidateConfig` missing 4 path fields (`validate_dir`, `roadmap_file`, `test_strategy_file`, `extraction_file`) | LOW | **Roadmap** |
| 2 | `build_reflect_prompt` missing `agent` param, takes `str` not `Path` | MEDIUM | **Roadmap** |
| 3 | `build_adversarial_merge_prompt` renamed to `build_merge_prompt`, `roadmap_file` dropped | LOW | **Roadmap** |
| 4 | `_build_validate_steps` split into two functions instead of one dispatcher | LOW | **Implementation** |

**75% of deviations originated at the roadmap level.** The tasklist faithfully propagated the roadmap's errors, and the sprint executor faithfully implemented the tasklist's instructions.

### 2.3 Adversarial Debate Verdicts

Each deviation was debated (spec-side vs implementation-side):

| Deviation | Verdict | Action |
|-----------|---------|--------|
| Missing config fields | **Hybrid** | Add as `@property` derived from `output_dir` |
| Missing `agent` param | **Amend spec + fix code** | Add `agent` back and actually USE it in prompt text for persona-specific validation |
| Renamed merge function | **Amend spec** | `build_merge_prompt` is justified; module context eliminates ambiguity |
| Split builder function | **Amend spec** | Two functions win on testability and SRP |

**Critical finding from debate**: `build_reflect_prompt` accepts 3 parameters that are **never interpolated into the prompt text** — they are dead code. Multi-agent validation currently runs identical prompts on different models, reducing adversarial value to merely "multi-model" comparison.

### 2.4 Full Deviation Counts Across Pipeline

| Boundary | Deviations Found | HIGH | MEDIUM | LOW |
|----------|-----------------|------|--------|-----|
| Spec → Roadmap | 29 | 5 | 12 | 12 |
| Roadmap → Tasklist | 15 | 3 | 6 | 6 |
| Tasklist → Implementation | 1 | 0 | 0 | 1 |

### 2.5 HIGH-Severity Roadmap Deviations (RD)

| ID | Description | Downstream Impact |
|----|-------------|-------------------|
| RD-001 | `ValidateConfig` fields reduced, missing 4 path fields | Implementation missing typed path accessors |
| RD-002 | `PipelineConfig` inheritance not mentioned | Could cause standalone dataclass (mitigated by implementor) |
| RD-003 | `build_reflect_prompt` missing `agent` param | Multi-agent prompts are identical — no persona differentiation |
| RD-004 | Merge function renamed, `roadmap_file` dropped | Name mismatch, merge can't cross-reference roadmap |
| RD-010 | State persistence in `.roadmap-state.json` **added** despite spec saying "unchanged" | Direct spec contradiction |

### 2.6 HIGH-Severity Tasklist Deviations (TD)

| ID | Description | Impact |
|----|-------------|--------|
| TD-001 | R-xxx traceability IDs are fabricated — don't exist in roadmap | Traceability field is meaningless |
| TD-006 | T03.02 dependency list skips T02.03 (alignment checkpoint) | Can start Phase 3 before checkpoint completes |
| TD-007 | Phase 3 integration tests don't cover multi-agent mode | Phase 3 milestone left unverified |

---

## 3. Current Validation Gate Inventory

### 3.1 Pipeline Gate Engine

<!-- Source: Base (original) -->
**File**: `src/superclaude/cli/pipeline/gates.py`

`gate_passed()` enforces 4 tiers:
- `EXEMPT`: always pass
- `LIGHT`: file exists + non-empty
- `STANDARD`: + min line count + required YAML frontmatter fields
- `STRICT`: + semantic check callbacks

**What it checks**: structural/schema properties only.
**What it does NOT check**: spec fidelity, semantic accuracy, cross-artifact consistency.

### 3.2 Roadmap Pipeline Gates

**File**: `src/superclaude/cli/roadmap/gates.py`

| Gate | Checks | Does NOT Check |
|------|--------|----------------|
| `EXTRACT_GATE` | Frontmatter fields, min 50 lines | Whether extracted FRs match spec content |
| `GENERATE_A/B_GATE` | Frontmatter, min 100 lines, has actionable content | Whether roadmap covers all requirements |
| `DIFF_GATE` | `total_diff_points`, min 30 lines | Semantic accuracy of diff |
| `DEBATE_GATE` | `convergence_score` in [0,1], min 50 lines | Whether debate addressed real issues |
| `SCORE_GATE` | `base_variant`, min 20 lines | Whether scoring criteria are valid |
| `MERGE_GATE` | No heading gaps, cross-refs (currently always passes), min 150 lines | Whether merged roadmap preserves spec intent |
| `TEST_STRATEGY_GATE` | `validation_milestones`, `interleave_ratio`, min 40 lines | Whether milestones match roadmap |

**Key finding**: `_cross_refs_resolve()` in MERGE_GATE currently **always returns True** — the cross-reference check is non-enforcing.

### 3.3 Validate Pipeline Gates

**File**: `src/superclaude/cli/roadmap/validate_gates.py`

| Gate | Checks |
|------|--------|
| `REFLECT_GATE` | Frontmatter (blocking_issues_count, warnings_count, tasklist_ready), min 20 lines |
| `ADVERSARIAL_MERGE_GATE` | Above + validation_mode, validation_agents, agreement table present, min 30 lines |

### 3.4 Validate Pipeline Prompt (Best Existing Cross-Artifact Check)

**File**: `src/superclaude/cli/roadmap/validate_prompts.py`

The reflect prompt checks 7 dimensions:
- Schema, Structure, Traceability (deliverable↔requirement), Cross-file consistency, Parseability (all BLOCKING)
- Interleave, Decomposition (WARNING)

**This is the strongest existing validation** but it compares roadmap against `extraction.md`, not the raw spec. If extraction loses information, the check passes anyway.

### 3.5 Sprint Runner

**File**: `src/superclaude/cli/sprint/executor.py`

Checks: subprocess exit code, phase result report parsing, halt/continue markers.
Does NOT check: whether task outputs match tasklist deliverables, acceptance criteria, roadmap, or spec.

### 3.6 Documented But Not Wired

**File**: `src/superclaude/skills/sc-roadmap-protocol/refs/validation.md`

Contains explicit spec-fidelity prompts:
- "Does the roadmap faithfully represent the spec?"
- "Are all spec requirements represented in the roadmap?"
- "Are any spec requirements distorted, merged incorrectly, or misinterpreted?"

Also contains a quality-engineer prompt checking completeness (every FR/NFR in extraction has deliverable), consistency, traceability, and test strategy quality.

**This is not wired into the CLI executor.** The actual auto-validation path is `execute_roadmap()` → `_auto_invoke_validate()` → `execute_validate()` → `build_reflect_prompt()` from `validate_prompts.py`, which is lighter than what the skill docs describe.

<!-- Source: Variant A (GPT briefing), lines 348-363 — merged per Change #4 -->
**Root cause of the gap**: The tasklist protocol (`src/superclaude/skills/sc-tasklist-protocol/SKILL.md`, lines 864-868) explicitly treats **semantic gates as advisory** while **structural gates are blocking**. This is the policy-level explanation for why semantically wrong but structurally valid artifacts continue downstream. The gate infrastructure is architecturally sound — the issue is that semantic conformance is classified as advisory, not blocking.

### 3.7 Manual-Only Tools

| Tool | File | Purpose | Wired Into Pipeline? |
|------|------|---------|---------------------|
| `sc:reflect` | `src/superclaude/commands/reflect.md` | Task/session reflection | No |
| `sc:validate-tests` | `src/superclaude/skills/sc-validate-tests-protocol/SKILL.md` | Tier classification testing | No |
| Reflection engine | `src/superclaude/execution/reflection.py` | Requirement clarity, context sufficiency | No |

---

## 4. Gap Map

<!-- Source: Base (original) -->
```
SPEC ──────────────────────────────────────────────────────────
  ↓ [extraction]
  Gate: EXTRACT_GATE (structural)
  Missing: ❌ "Does extraction capture all spec FRs/NFRs?"

EXTRACTION ────────────────────────────────────────────────────
  ↓ [roadmap generation ×2, diff, debate, score, merge]
  Gates: GENERATE/DIFF/DEBATE/SCORE/MERGE (all structural)
  Missing: ❌ "Does roadmap preserve spec signatures, fields, constraints?"
  ← THIS IS WHERE 75% OF DEVIATIONS ORIGINATED

ROADMAP (merged) ──────────────────────────────────────────────
  ↓ [validate pipeline]
  Gate: REFLECT_GATE (prompt-driven 7 dimensions)
  Has: ✅ Traceability (deliverable↔requirement via extraction)
  Missing: ❌ Does NOT read raw spec — only compares vs extraction

ROADMAP ───────────────────────────────────────────────────────
  ↓ [sc:tasklist generation]
  Gate: None in code (skill protocol describes self-checks)
  Missing: ❌ No runtime validator for tasklist↔roadmap fidelity

TASKLIST ──────────────────────────────────────────────────────
  ↓ [sprint execution]
  Gate: Exit code + phase result parsing
  Missing: ❌ No output↔tasklist acceptance criteria check
```

*Note: Per the validation layering principle (Section 1), the sprint runner correctly validates against the tasklist, not the original spec. The gap at this layer is output↔tasklist, not output↔spec.*

---

## 5. Proposed Solutions

<!-- Source: Variant A (GPT briefing), lines 418-431 — merged per Change #3 -->
**Harness definition**: A harness in this context is a repeatable, automated, read-only validation wrapper around an artifact-producing step. It takes an upstream source-of-truth artifact, takes a generated downstream artifact, runs reflective/adversarial semantic review, emits normalized structured deviation findings, and decides pass/warn/block. The solutions below implement harnesses at specific pipeline boundaries.

### 5.1 Solution A: Post-Roadmap Spec-Fidelity Step (HIGHEST ROI)

<!-- Source: Base (original) -->
**Injection point**: After merge step (step 6), before or alongside validate.

**Mechanism**: One additional `Step` in the roadmap pipeline that receives `spec.md` + `roadmap.md` and asks:

> "For every function signature, data model definition, gate criteria specification, CLI option, and NFR in the spec, verify the roadmap preserves it exactly. List any omissions, simplifications, reinterpretations, or additions. Quote both spec and roadmap text for each deviation."

**Implementation approach**:
- Add a new step in `src/superclaude/cli/roadmap/executor.py` (or extend the existing validate pipeline)
- Add a prompt builder in `validate_prompts.py` (e.g., `build_spec_fidelity_prompt(spec_content, roadmap_content)`)
- Add a gate in `validate_gates.py` (e.g., `SPEC_FIDELITY_GATE`)
- The spec file path is already available in the pipeline config (`spec_file`)

**Cost**: ~30-60s per run (one LLM subprocess call).
**Value**: Would have caught all 5 HIGH-severity roadmap deviations.

### 5.2 Solution B: Post-Tasklist Roadmap-Fidelity Check (MEDIUM ROI)

**Injection point**: After `sc:tasklist` generates the bundle, before sprint.

**Mechanism**: A prompt receiving `roadmap.md` + tasklist bundle checking:
- Every roadmap deliverable appears in the tasklist
- Function signatures/dependencies preserved
- Traceability IDs are valid (not fabricated)
- Dependency chains match roadmap ordering

**Challenge**: `sc:tasklist` is currently a skill (prompt-based), not a CLI command. The harness would need to be:
- A follow-up validation step in the skill protocol, OR
- A CLI subcommand (`superclaude tasklist validate`), OR
- Wired into the sprint runner as a pre-execution check

**Value**: Would have caught TD-001, TD-006, TD-007.

### 5.3 Solution C: Wire Existing Skill Prompts Into CLI (QUICK WIN)

**What exists**: `src/superclaude/skills/sc-roadmap-protocol/refs/validation.md` already has production-quality spec-fidelity prompts.

**What's needed**: Wire these prompts into `execute_validate()` or add them as additional steps in the roadmap pipeline. This is mostly a plumbing exercise — the content exists, it just needs to be called.

### 5.4 Solution D: End-to-End Release Fidelity Audit (LOWER PRIORITY)

A final gate before merge to master that reads `spec.md` + actual source files and validates the implementation matches the spec. This is essentially what was done manually in this conversation with `/sc:spawn` + 5 validation agents.

**Cost**: High (token-intensive, reads many files).
**Value**: Catches everything, but most deviations should be caught earlier.

### 5.5 Normalized Deviation Report Contract

<!-- Source: Variant A (GPT briefing), lines 512-528 — merged per Change #2 -->
For all harnesses (Solutions A-D), emit rows with the following normalized schema:

| Field | Description |
|-------|-------------|
| `source_pair` | Which boundary (e.g., "spec→roadmap", "roadmap→tasklist") |
| `severity` | HIGH / MEDIUM / LOW |
| `deviation` | Description of the deviation |
| `evidence` | Specific quotes from both artifacts |
| `likely_impact` | Downstream consequence if uncorrected |
| `recommended_correction` | Suggested fix action |

This format enables: deduplication across gates, severity-based gating (block on HIGH), scoring and aggregation, feeding into revise loops, and audit trail generation.

---

## 6. Key File Reference

### Pipeline Infrastructure
| File | Purpose |
|------|---------|
| `src/superclaude/cli/pipeline/gates.py` | Generic gate engine (`gate_passed()`, tier enforcement) |
| `src/superclaude/cli/roadmap/gates.py` | Roadmap step gates (EXTRACT, GENERATE, DIFF, DEBATE, SCORE, MERGE, TEST_STRATEGY) |
| `src/superclaude/cli/roadmap/executor.py` | Roadmap pipeline orchestrator (`execute_roadmap()`, `_auto_invoke_validate()`) |
| `src/superclaude/cli/roadmap/prompts.py` | Roadmap generation prompts |
| `src/superclaude/cli/roadmap/models.py` | Pipeline data models (`PipelineConfig`, `ValidateConfig`, `AgentSpec`) |

### Validate Pipeline (v2.19)
| File | Purpose |
|------|---------|
| `src/superclaude/cli/roadmap/validate_executor.py` | Validate orchestrator (`execute_validate()`, step builders) |
| `src/superclaude/cli/roadmap/validate_gates.py` | Validate gates (`REFLECT_GATE`, `ADVERSARIAL_MERGE_GATE`) |
| `src/superclaude/cli/roadmap/validate_prompts.py` | Validate prompts (`build_reflect_prompt()`, `build_merge_prompt()`) |
| `src/superclaude/cli/roadmap/commands.py` | CLI surface (`roadmap validate`, `--no-validate` on `run`) |

### Sprint Runner
| File | Purpose |
|------|---------|
| `src/superclaude/cli/sprint/executor.py` | Sprint execution engine (phase loop, subprocess management) |
| `src/superclaude/cli/sprint/process.py` | Claude subprocess management, prompt construction |
| `src/superclaude/cli/sprint/config.py` | Sprint config, phase discovery |

### Skill Protocols (Documented But Not Wired)
| File | Purpose |
|------|---------|
| `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | Roadmap generation protocol (Wave 1-4) |
| `src/superclaude/skills/sc-roadmap-protocol/refs/validation.md` | **Contains spec-fidelity prompts not wired into CLI** |
| `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` | Tasklist generation protocol with self-checks |

### Manual Tools
| File | Purpose |
|------|---------|
| `src/superclaude/commands/reflect.md` | Manual reflection command |
| `src/superclaude/execution/reflection.py` | Python reflection engine (not pipeline-integrated) |

### v2.19 Sprint Artifacts
| File | Purpose |
|------|---------|
| `.dev/releases/complete/v2.19-roadmap-validate/spec-roadmap-validate.md` | Source spec (FR-050) |
| `.dev/releases/complete/v2.19-roadmap-validate/roadmap.md` | Generated roadmap (29 deviations from spec) |
| `.dev/releases/complete/v2.19-roadmap-validate/phase-2-tasklist.md` | Phase 2 tasklist (analyzed for deviations) |
| `.dev/releases/complete/v2.19-roadmap-validate/phase-3-tasklist.md` | Phase 3 tasklist (analyzed for deviations) |
| `.dev/releases/complete/v2.19-roadmap-validate/tasklist-index.md` | Tasklist index with traceability matrix |
| `.dev/releases/complete/v2.19-roadmap-validate/execution-log.md` | Sprint execution log (all 5 phases pass) |

### Test Files (Produced by Sprint)
| File | Tests |
|------|-------|
| `tests/roadmap/test_validate_gates.py` | 22 tests — gate criteria, semantic checks |
| `tests/roadmap/test_validate_executor.py` | 15 tests — executor, step builders, partial failure |
| `tests/roadmap/test_validate_cli.py` | 20 tests — CLI subcommand, auto-invocation, state |
| `tests/roadmap/test_validate_unit.py` | 14 tests — config, report semantics |
| `tests/roadmap/test_validate_defects.py` | 15 tests — known-defect detection |
| `tests/roadmap/test_validate_sc001_sc003.py` | 8 tests — standalone single/multi-agent |
| `tests/roadmap/test_validate_resume_failure.py` | 2 tests — resume failure path |

---

## 7. Decision Framework for Next Steps

<!-- Source: Base (original) -->
### The fundamental question:

> At which pipeline boundaries should we add spec-fidelity checks, and should they be prompt-based (LLM asks "does this match?") or deterministic (Python code compares structures)?

### Trade-offs:

| Approach | Catches | Cost | Reliability |
|----------|---------|------|-------------|
| Prompt-based (LLM reflection) | Semantic drift, reinterpretations, omissions | ~30-60s per check | Non-deterministic, may miss or hallucinate |
| Deterministic (Python parser) | Structural drift, missing fields, wrong signatures | Development effort | Deterministic, but can't catch semantic drift |
| Hybrid | Both | Both | Best coverage |

### The minimum viable fix:

Add **one prompt-based step** after roadmap merge that reads the raw spec alongside the merged roadmap and asks for deviation enumeration. This is Solution A above. It would have prevented 75% of the deviations found in v2.19 and costs ~30-60 seconds of pipeline time.

---

## 8. Diagnostic Questions for Follow-Up

<!-- Source: Variant A (GPT briefing), lines 607-619 — merged per Change #5 -->
A future agent continuing this work should start with these questions:

1. Is the documented Wave 4 roadmap validation actually invoked in the concrete execution path used to generate these artifacts?
2. If yes, why did it not block the roadmap/spec deviations identified here?
   - Scoring too soft?
   - Wrong prompt?
   - Missing required evidence extraction?
   - Non-blocking integration?
3. Does `/sc:tasklist` have any equivalent blocking semantic conformance gate for roadmap → tasklist?
4. Should semantic conformance move from advisory to blocking at artifact boundaries?
5. What is the smallest harness contract that can be reused across roadmap and tasklist generation?
