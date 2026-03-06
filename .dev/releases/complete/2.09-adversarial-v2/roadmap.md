---
spec_sources:
  - .dev/releases/current/2.09-adversarial-v2/05-adversarial2.0-final-refactor-spec.md
  - .dev/releases/current/2.09-adversarial-v2/adversarial-release-spec.md
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.690
complexity_class: MEDIUM
domain_distribution:
  architecture: 50
  quality: 30
  backend: 20
  frontend: 0
  documentation: 0
primary_persona: architect
consulting_personas:
  - analyzer
  - qa
milestone_count: 6
milestone_index:
  - id: M1
    title: Foundation & Backward Compatibility Guard
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    risk_level: Medium
  - id: M2
    title: Meta-Orchestrator Architecture — Pipeline Flag + DAG Builder
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 6
    risk_level: High
  - id: M3
    title: Protocol Quality Phase 1 — Shared Assumption Extraction + Taxonomy
    type: IMPROVEMENT
    priority: P1
    dependencies: [M1]
    deliverable_count: 6
    risk_level: Medium
  - id: V1
    title: Validation — M2/M3 Integration & Regression
    type: TEST
    priority: P3
    dependencies: [M2, M3]
    deliverable_count: 3
    risk_level: Low
  - id: M4
    title: Phase Execution Engine — Executor + Artifact Routing + Parallelism + Enhancements
    type: FEATURE
    priority: P1
    dependencies: [M2]
    deliverable_count: 8
    risk_level: High
  - id: M5
    title: Protocol Quality Phase 2 — Invariant Probe + Edge Case Scoring + Return Contract
    type: IMPROVEMENT
    priority: P2
    dependencies: [M3, M4]
    deliverable_count: 6
    risk_level: Medium
  - id: V2
    title: Validation — End-to-End Pipeline & Protocol Completeness
    type: TEST
    priority: P3
    dependencies: [M4, M5]
    deliverable_count: 4
    risk_level: Low
total_deliverables: 37
total_risks: 8
estimated_phases: 4
validation_score: 0.0
validation_status: SKIPPED
adversarial:
  mode: combined
  agents:
    - opus:architect
    - haiku:architect
  convergence_score: 0.80
  base_variant: opus:architect
  artifacts_dir: .dev/releases/current/2.09-adversarial-v2/adversarial/
  consolidation_convergence: 0.85
---

# Roadmap: /sc:adversarial v2.09 — Dual Release

## Overview

This roadmap covers the complete v2.09 release of the `/sc:adversarial` command, which comprises two complementary tracks developed in parallel:

**Track A (Architectural)**: The Meta-Orchestrator Layer (`--pipeline` flag) transforms the existing single-phase adversarial command into a multi-phase DAG-orchestrated pipeline. Users can compose arbitrarily complex debate workflows using either inline shorthand or YAML files, with native parallelism, artifact routing between phases, dry-run inspection, blind evaluation, and checkpoint-based resume. The existing 5-step pipeline and Mode A/B code paths receive zero changes — the Meta-Orchestrator is a purely additive wrapper.

**Track B (Protocol)**: Four incremental improvements address the "agreement = no scrutiny" structural blind spot: Consensus Assumption Extraction (AD-2) surfaces implicit shared assumptions as debatable diff points; Debate Topic Taxonomy (AD-5) guarantees state-mechanics-level debate cannot be bypassed; the Invariant Probe Round (AD-1) applies a systematic boundary-condition checklist to the emerging consensus; and Edge Case Scoring (AD-3) creates scoring incentives for invariant coverage.

The two tracks converge in SKILL.md: Track A adds the meta-orchestrator protocol section (~400-600 lines), Track B modifies the existing debate protocol sections. The primary coordination risk is SKILL.md merge order — this roadmap sequences Track B's foundation work (M3) in parallel with Track A's architecture work (M2) before the integration point (M4, M5).

This roadmap uses **adversarial multi-roadmap generation** (agents: opus:architect + haiku:architect) with **spec consolidation** of two complementary specifications. The opus perspective drove milestone granularity and risk register depth; the haiku perspective drove the parallel workstream structure and validation interleaving.

---

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation & Backward Compatibility Guard | FEATURE | P0 | S | None | 4 | Medium |
| M2 | Meta-Orchestrator Architecture — Pipeline Flag + DAG Builder | FEATURE | P1 | L | M1 | 6 | High |
| M3 | Protocol Quality Phase 1 — Shared Assumption Extraction + Taxonomy | IMPROVEMENT | P1 | M | M1 | 6 | Medium |
| V1 | Validation — M2/M3 Integration & Regression | TEST | P3 | S | M2, M3 | 3 | Low |
| M4 | Phase Execution Engine — Executor + Artifact Routing + Parallelism + Enhancements | FEATURE | P1 | L | M2 | 8 | High |
| M5 | Protocol Quality Phase 2 — Invariant Probe + Edge Case Scoring + Return Contract | IMPROVEMENT | P2 | M | M3, M4 | 6 | Medium |
| V2 | Validation — End-to-End Pipeline & Protocol Completeness | TEST | P3 | M | M4, M5 | 4 | Low |

---

## Dependency Graph

```
M1 (Foundation)
├── M2 (Meta-Orchestrator Architecture)  ──→  M4 (Phase Execution Engine)  ──→  V2
│                                                                                 ↑
└── M3 (Protocol Quality Phase 1)  ──→  V1  ──[unblocks via M4]──→  M5  ────────┘
                                                                    ↑
                                              M3 ─────────────────→ M5
```

**Linear reading**: `M1 → {M2 ∥ M3} → V1 → M4 → M5 → V2`

M2 and M3 are parallelizable after M1. V1 gates only after both M2 and M3 are complete. M4 depends only on M2 (can start after V1 or immediately after M2 if V1 is fast-tracked). M5 depends on both M3 and M4. V2 closes the release.

---

## M1: Foundation & Backward Compatibility Guard

### Objective

Establish the structural baseline for the v2.09 release: confirm backward compatibility contract, document the SKILL.md integration plan for both tracks, set up testing scaffolding, and write the `--pipeline` flag detection stub (step_0 guard) that gates all pipeline mode logic.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | SKILL.md `--pipeline` flag detection stub (step_0 guard before existing mode parsing) | Flag presence routes to meta-orchestrator section; absence routes to existing Mode A/B behavior unchanged |
| D1.2 | Backward compatibility regression baseline: document all existing Mode A/B invocation patterns and their expected outputs | At least 5 canonical invocations documented with expected return contract values |
| D1.3 | SKILL.md integration sequencing plan: specify the order of Track A (meta-orchestrator) and Track B (protocol) modifications to prevent merge conflicts | Plan reviewed and conflicts enumerated; no blocking conflicts remain at milestone exit |
| D1.4 | Test scaffolding for SC-001 through SC-010 acceptance criteria | All 10 success criteria have test case stubs with input/expected-output pairs |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SKILL.md merge conflict between Track A and Track B sections | Medium | High | Integration sequencing plan (D1.3) maps all modification sites before any changes begin |
| step_0 guard breaks existing CLI parsing | Low | High | Comprehensive regression baseline (D1.2) catches regressions before M2/M3 work begins |

---

## M2: Meta-Orchestrator Architecture — Pipeline Flag + DAG Builder

### Objective

Implement the complete pipeline definition and DAG construction layer: inline shorthand parser, YAML pipeline file loader, DAG builder with cycle detection, and full schema validation. This delivers the structural foundation that the Phase Executor (M4) builds on.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Inline shorthand parser: `phase1 -> phase2 \| phase3` with `generate:<agents>` and `compare` phase types | Parses all examples from Spec1 Section "Inline Shorthand"; returns structured phase list |
| D2.2 | YAML pipeline file loader (`--pipeline @path.yaml`) with phase schema validation | Loads the 3-phase example YAML from Spec1 without errors; rejects YAML with unknown fields or missing required fields |
| D2.3 | DAG builder: constructs directed acyclic graph from phase definitions | Correctly identifies parallel phases (same dependency level) and sequential gates (dependency edges) |
| D2.4 | Cycle detection: aborts with descriptive error on circular dependency | Test case: `A → B → A` produces `"Circular dependency detected: A → B → A"` |
| D2.5 | Reference integrity validation: all `depends_on` phase IDs must exist in the phase list | Unknown phase ID in `depends_on` produces `"Unknown phase reference: <id>"` |
| D2.6 | Dry-run render: validate DAG, output execution plan to console/file, exit without executing phases | Dry-run output matches actual execution plan for 3-phase canonical workflow (SC-002) |

### Dependencies

- M1: `--pipeline` flag detection stub (D1.1); backward compatibility baseline (D1.2); integration plan (D1.3)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Multi-phase pipeline token costs significantly exceed estimates | Medium | High | Dry-run mode (D2.6) provides token cost previews before execution; `--pipeline-parallel N` cap limits concurrent phases |
| Inline shorthand parsing ambiguity at edge cases | Low | Medium | Parser test suite covers all syntax variants from Spec1; ambiguous cases abort with descriptive error |

---

## M3: Protocol Quality Phase 1 — Shared Assumption Extraction + Taxonomy

### Objective

Implement the two highest-priority protocol improvements (Phase 1 from Spec 2): Shared Assumption Extraction (AD-2) and Debate Topic Taxonomy (AD-5). These address the primary structural blind spot and are designed to work together — AD-2 generates `[SHARED-ASSUMPTION]` diff points that AD-5 auto-tags as L3 (State Mechanics).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Shared assumption extraction sub-phase in Step 1: agreement identification, assumption enumeration, classification (STATED/UNSTATED/CONTRADICTED) | AC-AD2-1 passes: 3 variants assuming 1:1 event-widget mapping → UNSTATED precondition surfaced |
| D3.2 | UNSTATED preconditions promoted to synthetic `[SHARED-ASSUMPTION]` diff points (A-NNN scheme); added to diff-analysis.md Shared Assumptions section | AC-AD2-3 passes: convergence denominator includes A-NNN points |
| D3.3 | Advocate prompt template updated: ACCEPT/REJECT/QUALIFY requirement for each `[SHARED-ASSUMPTION]` point | AC-AD2-4 passes: omitted shared assumption responses flagged in transcript |
| D3.4 | Three-level taxonomy (L1/L2/L3) defined in SKILL.md with auto-tag signals per level | Each level has ≥5 auto-tag signals documented; A-NNN points with state/guard/boundary terms auto-tagged L3 (AC-AD5-3) |
| D3.5 | Post-round taxonomy coverage check + forced round trigger for uncovered levels | AC-AD5-1 passes: 87% convergence blocked when L3 has zero coverage; forced L3 round triggered |
| D3.6 | Convergence formula updated: includes taxonomy gate AND A-NNN points in total_diff_points denominator | AC-AD5-4 passes: forced round still triggers at depth=quick when L3 has zero coverage |

### Dependencies

- M1: Integration sequencing plan (D1.3) to prevent SKILL.md conflicts with Track A

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shared assumption extraction produces formulaic output | Medium | High | Taxonomy forced round (D3.5) provides independent catch path for L3 content; defense in depth |
| Forced taxonomy rounds produce shallow analysis | Low | Medium | AD-2 shared assumption output provides concrete L3 diff points for the forced round to target (D3.2 + D3.4 interaction) |
| Step 1 overhead exceeds 10% threshold (NFR-004) | Low | Medium | Structured table format (D3.2) minimizes token consumption; overhead measured in V1 |

---

## V1: Validation — M2/M3 Integration & Regression

### Objective

Verify that Track A (DAG builder) and Track B Phase 1 (protocol improvements) work correctly independently and that backward compatibility is preserved. Gate before proceeding to the more complex Phase Execution Engine (M4).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| V1.1 | Backward compatibility regression: run all D1.2 baseline invocations; verify Mode A and Mode B outputs are unchanged | 100% of baseline invocations produce output matching the documented baseline (0 regressions) |
| V1.2 | Protocol correctness: run SC-005 (v0.04 variant replay) and SC-006/SC-007 acceptance scenarios | Both v0.04 bug classes caught by AD-2 or AD-5 (SC-005 passes); at least 6 of 8 AC assertions pass |
| V1.3 | Overhead measurement for M3 additions: measure Step 1 overhead delta with shared assumption extraction enabled | Measured overhead ≤10% (NFR-004 compliance) |

### Dependencies

- M2: DAG builder and dry-run complete (regression baseline runnable)
- M3: Protocol Phase 1 complete (SC-005/SC-006/SC-007 runnable)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| V0.04 variant replay data not available | Low | Medium | Acceptance criteria test cases (AC-AD2-1 through AC-AD5-4) are synthetic and always available |

---

## M4: Phase Execution Engine — Executor + Artifact Routing + Parallelism + Enhancements

### Objective

Implement the runtime execution layer of the Meta-Orchestrator: Phase Executor (Mode A/B invocation translation), artifact routing between phases (resolving `merged_output` paths), parallel phase scheduling (topological sort), pipeline manifest management, and the three adopted enhancements (blind evaluation, convergence plateau detection, pipeline resume).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | Phase Executor: translates phase config → Mode A (compare) or Mode B (generate) invocation; scoped to phase output directory | Single-phase pipeline (`--pipeline "generate:opus:architect"`) produces identical output to direct Mode B invocation |
| D4.2 | Artifact routing: resolves `merged_output` and `all_variants` paths between dependent phases; passes artifacts as inputs to consuming phases | 2-phase pipeline (`generate → compare`) correctly passes phase 1 merged output as phase 2 variant input |
| D4.3 | Parallel phase scheduler: topological sort for execution ordering; concurrent execution up to `--pipeline-parallel N` | 2-phase parallel `generate → compare` produces correct artifacts; no race conditions in artifact routing |
| D4.4 | Pipeline manifest: `pipeline-manifest.yaml` created at pipeline start; updated after each phase with return contract and checksums | Manifest contains all phase results, statuses, and convergence scores after 3-phase execution |
| D4.5 | `--pipeline-resume`: reads manifest, validates checksums, re-executes from first incomplete phase | Resume from phase 2 of 3 skips phase 1 (checksum valid) and re-executes phases 2-3 |
| D4.6 | Blind evaluation (`--blind`): metadata stripping in artifact routing before compare phase receives variants | SC-003 passes: merged output contains zero model-name references after `--blind` pipeline |
| D4.7 | Convergence plateau detection (`--auto-stop-plateau`): delta <5% for 2 consecutive compare phases triggers halt | SC-004 passes: synthetic 3-phase pipeline with plateau triggers warning and halt on phase 3 |
| D4.8 | Error policies: halt-on-failure (default) and `--pipeline-on-error continue`; minimum variant constraint (compare phase needs ≥2 inputs) | Failed phase marks dependents as skipped in manifest; `continue` mode leaves parallel branches running |

### Dependencies

- M2: DAG builder (D2.1-D2.6) must be complete; Phase Executor builds on DAG output

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Parallel phase execution introduces state contamination | Low | High | Each phase gets an isolated output directory (D4.1); manifest tracks phase-scoped artifacts only |
| Token cost for full 8-step pipeline exceeds practical limits | Medium | High | `--pipeline-parallel N` cap (default 3) limits concurrent execution; `--dry-run` (M2/D2.6) allows pre-flight cost estimation |
| Resume checkpoint validation produces false invalidations | Low | Medium | Checksum validation covers artifact files only (not SKILL.md or system state); clear validation logic documented |

---

## M5: Protocol Quality Phase 2 — Invariant Probe + Edge Case Scoring + Return Contract

### Objective

Implement the remaining two protocol improvements (Phase 2 from Spec 2): the Invariant Probe Round (AD-1, Round 2.5) and Edge Case Coverage scoring dimension (AD-3). Extend the return contract with `unaddressed_invariants`. These complete the "invariant coverage" workstream and provide the scoring incentives for future variant quality.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | Round 2.5 fault-finder agent prompt: boundary-condition checklist (5 categories: state_variables, guard_conditions, count_divergence, collection_boundaries, interaction_effects) | AC-AD1-1 passes: filter divergence found; AC-AD1-2 passes: sentinel collision found |
| D5.2 | Round 2.5 dispatch logic: condition on `--depth standard/deep`; skip at `--depth quick` (logged) | AC-AD1-4 passes: Round 2.5 skipped at depth=quick |
| D5.3 | `invariant-probe.md` artifact assembly: structured table (ID, Category, Assumption, Status, Severity, Evidence) | AC-AD1-3 passes: 2 HIGH-severity UNADDRESSED items block convergence |
| D5.4 | Convergence gate for invariant probe: HIGH-severity UNADDRESSED items block convergence; MEDIUM logged as warnings | AC-AD1-3 passes: 90% diff-point agreement with 2 HIGH UNADDRESSED → convergence blocked |
| D5.5 | 6th qualitative dimension "Invariant & Edge Case Coverage" (5 CEV criteria, /30 formula, floor=1/5 for base eligibility) | AC-AD3-1 passes: 24/25 variant with 0/5 edge case floor ineligible as base; AC-AD3-2 passes: scoring differentiates 4/5 from 1/5 |
| D5.6 | Return contract extended: `unaddressed_invariants` field lists HIGH-severity UNADDRESSED items; existing fields unchanged (NFR-003) | Return contract contains `unaddressed_invariants: []` on success; populated list when HIGH items remain |

### Dependencies

- M3: Protocol Phase 1 complete (D5.1 builds on AD-2 output from D3.2 as richer probe input)
- M4: Phase Execution Engine complete (artifact structure used by M5 is established in M4)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Invariant checklist becomes stale over time | Low | High | NFR-009 requires extensible checklist structure; checklist categories are addable without protocol changes (D5.1) |
| Context window competition from new artifacts | Low | Medium | Structured table format (NFR-008) used throughout D5.1-D5.4; downstream steps consume summary counts not full artifact |
| Edge case floor requirement rejects all variants (all score 0/5) | Very Low | Medium | Floor suspended when all variants score 0/5 with warning; AC-AD3-1 suspension rule verified |

---

## V2: Validation — End-to-End Pipeline & Protocol Completeness

### Objective

End-to-end validation of the complete v2.09 release: canonical 8-step workflow, protocol regression with all four improvements active, overhead measurement against the 40% ceiling, and completeness verification that no backward-compatible contract was broken.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| V2.1 | Canonical end-to-end: SC-001 (8-step pipeline with `--blind`) executes successfully | Pipeline completes all 3 phases; final output is a merged roadmap with no model-name references (SC-003) |
| V2.2 | Full protocol stack: SC-005 through SC-009 (all acceptance scenario suites) pass with all improvements active simultaneously | ≥9 of 10 success criteria pass; no more than 1 SC at WARN level |
| V2.3 | Overhead measurement: SC-010 — measure total overhead delta with all improvements enabled | Measured total overhead ≤40% (NFR-007) |
| V2.4 | Backward compatibility final check: all D1.2 baseline invocations produce unchanged output with v2.09 SKILL.md | 100% of baseline invocations pass (0 regressions) |

### Dependencies

- M4: Phase Execution Engine (required for end-to-end pipeline test)
- M5: Protocol Phase 2 (required for full protocol stack test)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Total overhead exceeds 40% ceiling | Medium | Medium | Phase-by-phase measurement at V1 and in M5 development provides early warning; deferral path: defer AD-3 (lowest impact) if needed |
| End-to-end canonical workflow fails due to artifact routing issue | Low | High | D4.2 artifact routing covered by unit test (2-phase pipeline); end-to-end adds phase count only |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Shared assumption extraction produces formulaic output | M3, V1 | Medium | High | Taxonomy forced round (M3/D3.5) provides independent catch path; AD-1 invariant probe (M5) provides third layer | analyst |
| R-002 | Cumulative overhead exceeds 40% ceiling | V1, V2 | Medium | Medium | Phase-by-phase overhead measurement at V1 gate; AD-3 (M5/D5.5) is deferrable if overhead is already near ceiling at V1 | qa |
| R-003 | Forced taxonomy rounds produce shallow L3 analysis | M3, V1 | Low | Medium | AD-2 shared assumption output provides concrete L3 targets; forced round prompt is specific (D3.4/D3.5) | analyst |
| R-004 | Invariant checklist becomes stale | M5 | Low | High | NFR-009 extensibility requirement built into D5.1; track post-release bugs against checklist categories | architect |
| R-005 | Context window competition from new artifacts | M5, V2 | Low | Medium | Structured table format enforced throughout (NFR-008); summary counts consumed by downstream steps | qa |
| R-006 | SKILL.md merge conflict between Track A and Track B | M1, M2, M3 | Medium | High | D1.3 integration sequencing plan maps all modification sites before changes begin; M3 and M2 run in parallel but modify different SKILL.md sections | architect |
| R-007 | Multi-phase pipeline token costs exceed estimates | M2, M4, V2 | Medium | High | Dry-run mode (D2.6) provides pre-flight cost estimation; `--pipeline-parallel N` cap limits concurrent execution; pipeline token estimate in dry-run output | architect |
| R-008 | Parallel phase execution causes state contamination | M4 | Low | High | Phase-isolated output directories (D4.1); manifest tracks phase-scoped artifacts; no shared mutable state between concurrent phases | backend |

---

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect (0.78 confidence) | analyzer (0.54), qa (0.42) | Highest domain % (architecture 50%); both tracks are design-heavy |
| Template | inline generation | No templates found in .dev/templates/ or ~/.claude/templates/ | Tier 1-3 search produced no candidates; fell back to Tier 4 inline generation |
| Milestone Count | 6 (4 work + 2 validation) | 5 (haiku:architect), 7 (opus:architect) | base(5) + floor(3/2)=1 = 6; adversarial merge chose 6 as optimal balance between opus granularity and haiku efficiency |
| Adversarial Mode | combined (multi-spec + multi-roadmap) | multi-spec only, multi-roadmap only | User passed both `--specs` and `--multi-roadmap`; combined mode ran Wave 1A consolidation then Wave 2 multi-roadmap |
| Adversarial Base Variant | opus:architect | haiku:architect (convergence: ~0.75) | Opus produced superior risk register depth and dependency graph; haiku's parallel workstream structure was adopted as merge |
| Implementation Sequencing | M2 ∥ M3 (parallel), then M4 → M5 | Sequential M2→M3→M4→M5 | AD-5 forced round threshold is ≥3; both specs target different SKILL.md sections in M2/M3; parallelism saves execution time with low merge risk given D1.3 plan |
| AD-4 deferral | Deferred (not in roadmap) | Include in M5 | Spec 2 explicitly defers AD-4 (B-Tier, 57.5/100, complexity 7/10); its coverage overlaps with AD-2+AD-1 at lower cost |

---

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | Canonical 8-step `--pipeline "generate:... -> generate:... -> compare --blind"` executes end-to-end | M2, M4, V2 | Yes |
| SC-002 | Dry-run output matches actual execution plan for canonical workflow | M2 | Yes |
| SC-003 | Blind mode: merged output contains zero model-name references | M4, V2 | Yes |
| SC-004 | Plateau detection fires when convergence delta <5% for 2 consecutive compare phases | M4 | Yes |
| SC-005 | V0.04 variant replay catches both escaped bug classes (filter divergence + sentinel collision) | M3, V1 | Yes |
| SC-006 | AC-AD2-1 through AC-AD2-4 pass (shared assumption extraction) | M3, V1 | Yes |
| SC-007 | AC-AD5-1 through AC-AD5-4 pass (taxonomy coverage gate) | M3, V1 | Yes |
| SC-008 | AC-AD1-1 through AC-AD1-4 pass (invariant probe) | M5, V2 | Yes |
| SC-009 | AC-AD3-1 through AC-AD3-3 pass (edge case scoring + floor) | M5, V2 | Yes |
| SC-010 | Total overhead ≤40% above baseline measured empirically | V2 | Yes |
