

---
total_diff_points: 14
shared_assumptions_count: 18
---

# Diff Analysis: Opus Architect vs Haiku Analyzer Roadmaps

## 1. Shared Assumptions and Agreements

Both variants agree on the following 18 points:

1. **Complexity score**: 0.92, enterprise-grade effort
2. **Requirement count**: 70 requirements (52 functional, 18 non-functional) across 7 domains
3. **Command/protocol split** as the foundational architectural change
4. **Ref file staleness (RISK-002)** as the highest-priority remediation item
5. **Live API snapshotting** with hash verification as the drift mitigation strategy
6. **5-phase portification pipeline** (Phase 0–4) as the core workflow
7. **Contract-driven phase boundaries** using YAML schemas
8. **Resume semantics** — read latest contract, validate, skip completed phases
9. **12 Python files** generated in strict dependency order
10. **Atomic generation** — halt on first failure, no partial output
11. **AST validation** (`ast.parse()`) as a blocking per-file check
12. **Circular import detection** as a blocking cross-file check
13. **4 golden fixtures** (simple, batched, adversarial, unsupported)
14. **Unsupported pattern early abort** in Phase 0
15. **Non-portified code is never overwritten** (NFR-013)
16. **`main.py` collision always aborts**
17. **7 supported patterns only** — explicit boundary
18. **Human review gates** after analysis and design phases are intentional safety, not overhead

## 2. Divergence Points

### D-01: Phase Structure and Naming

- **Opus Architect**: 5 roadmap phases (Phase 1–5), mapping roughly to pipeline Phases 0–4 plus validation. Uses "Phase 1" for foundation, "Phase 2" for pipeline Phases 0–1, etc.
- **Haiku Analyzer**: 8 roadmap phases (A–H), each with a narrower scope. Separates contract framework (B) from prerequisites engine (C), and separates code generation (F) from integration (G).
- **Impact**: Haiku's finer granularity provides clearer milestone boundaries and more natural parallelization points. Opus's coarser phases reduce overhead but bundle unrelated concerns (e.g., Phase 2 covers both contract infrastructure and Phase 0/1 implementation).

### D-02: Timeline Units and Estimates

- **Opus Architect**: Estimates in "working sessions" (14–19 total). Does not define session duration.
- **Haiku Analyzer**: Estimates in "working days" (26–41 total). Provides optimistic/likely/conservative ranges.
- **Impact**: Haiku's day-based estimates are more actionable for project planning. Opus's session-based estimates are ambiguous — a session could be 2 hours or 8 hours. Haiku's conservative estimate (41 days) is significantly longer, suggesting either more realistic scoping or less confidence in execution speed.

### D-03: Contract Framework Separation

- **Opus Architect**: Contract infrastructure is Milestone 2.1 within Phase 2, bundled with Phase 0 and Phase 1 implementation.
- **Haiku Analyzer**: Contract framework is an entire standalone phase (Phase B), completed before any pipeline phase implementation.
- **Impact**: Haiku's approach ensures contracts are fully tested before any phase depends on them. Opus risks discovering contract design issues while simultaneously implementing Phase 0/1. Haiku is architecturally safer here.

### D-04: Open Question Resolution Timing

- **Opus Architect**: All 10 OQs resolved in Phase 1, Milestone 1.3. Blocking OQs identified (002, 003, 004, 007, 010). Resolution must complete before Phase 2.
- **Haiku Analyzer**: OQs categorized into must-resolve-before-Phase-1, before-Phase-2, before-Phase-3. Recommends resolution during Phases A–B. Lists blocking OQs as 002, 003, 004, 008, 009, 010.
- **Impact**: Opus attempts to resolve all OQs in one batch (more decisive but may rush decisions). Haiku allows progressive resolution (more flexible but risks late discovery). They disagree on which OQs are blocking — Opus flags OQ-007 (approval gate mechanism); Haiku flags OQ-008 (default output) and OQ-009 (test placement) instead.

### D-05: Legacy Directory Removal Timing

- **Opus Architect**: Explicitly defers `sc-cli-portify/` removal to Phase 5 (M5.4), after all validation passes.
- **Haiku Analyzer**: States "Remove deprecated legacy directory after migration validation" in Phase A, implying earlier removal.
- **Impact**: Opus is safer — keeping the old directory until validation is complete allows rollback. Haiku's early removal creates a one-way door before the new structure is proven.

### D-06: Resource/Role Definition

- **Opus Architect**: Does not define team roles. Treats execution as a single-agent workflow.
- **Haiku Analyzer**: Defines 5 explicit roles (Analyzer Lead, CLI Engineer, Contract Engineer, QA Engineer, Maintainer/Reviewer) with responsibility assignments.
- **Impact**: Haiku's role definitions are useful for multi-person teams but may be over-specified for a single-agent Claude Code execution context. Opus is more realistic about the actual execution model.

### D-07: Macro-Track Strategy

- **Opus Architect**: Strictly sequential critical path with identified parallelization opportunities within phases.
- **Haiku Analyzer**: Explicitly proposes two macro-tracks (Track A: Foundation hardening, Track B: Portification engine) and three parallel compression tracks.
- **Impact**: Haiku's two-track model provides a clearer mental model for separating infrastructure from feature work. Opus's parallelization is more tactical (within-phase), while Haiku's is more strategic (across-phases).

### D-08: MCP Degradation Testing Scope

- **Opus Architect**: Phase 5, Milestone 5.2 — tests each MCP server individually, verifies advisory warnings, verifies no hard blocks.
- **Haiku Analyzer**: Mentioned as a line item under Phase H ("verify MCP degradation warnings are advisory, not blocking") but not a dedicated milestone.
- **Impact**: Opus provides more thorough MCP degradation coverage. Haiku treats it as a checklist item rather than a structured test milestone.

### D-09: Negative/Failure Fixture Coverage

- **Opus Architect**: 4 golden fixtures (1 negative: unsupported skill). MCP degradation and resume tested separately.
- **Haiku Analyzer**: 4 golden fixtures plus explicit negative-path fixtures (stale ref, API drift, name collision, non-portified collision) as a distinct validation category.
- **Impact**: Haiku's broader negative-path fixture suite provides more comprehensive failure coverage. Opus covers the same scenarios but distributes them across different milestones rather than treating them as a cohesive negative-testing strategy.

### D-10: TurnLedger Resolution Approach

- **Opus Architect**: OQ-002 resolution: "Inspect codebase for TurnLedger. If absent from pipeline API, remove from spec."
- **Haiku Analyzer**: OQ-002 mentioned but defers to "clarify" without a concrete resolution strategy. Phase E says "TurnLedger integration once clarified."
- **Impact**: Opus provides a concrete decision rule (inspect → decide). Haiku leaves it open-ended, which could delay Phase E if not resolved in Phase A.

### D-11: Determinism Validation Specificity

- **Opus Architect**: SC-002 validated through "repeat fixture runs, diff output" in Phase 5.
- **Haiku Analyzer**: Explicitly enumerates what must be identical: `source_step_registry`, `step_mapping`, `module_plan`, and `contract outputs where expected`.
- **Impact**: Haiku's enumeration is more precise and testable. Opus's "diff output" is vague about which outputs must be deterministic.

### D-12: Contract Schema Versioning

- **Opus Architect**: Does not address contract schema versioning.
- **Haiku Analyzer**: Lists "Define contract schema versioning policy" as a recommended non-code prerequisite.
- **Impact**: Haiku anticipates schema evolution needs. Opus assumes schemas will be stable, which may cause issues if contracts need backward-compatible changes during development.

### D-13: `--dry-run` and `--skip-integration` Treatment

- **Opus Architect**: OQ-003 resolution defined: `--dry-run` = execute Phases 0–2 only, emit contracts, no code generation. `--skip-integration` = skip Phase 4.
- **Haiku Analyzer**: Lists these as unresolved ambiguities to be clarified in Phase A.
- **Impact**: Opus makes a concrete design decision in the roadmap. Haiku defers the decision. Opus's approach is more actionable but assumes the decision is correct without debate.

### D-14: Acceptance Gate Framing

- **Opus Architect**: Success criteria presented as a validation matrix mapping criteria to phases and methods.
- **Haiku Analyzer**: Presents a "Recommended acceptance gate" as a 6-item checklist that must all pass before declaring completion, plus a strategic recommendation that the project be managed as a "strict, gated delivery program."
- **Impact**: Haiku's framing is more operationally directive. Opus's matrix is more traceable but less prescriptive about the overall delivery discipline.

## 3. Areas Where One Variant Is Clearly Stronger

### Opus Architect is stronger in:
- **Concrete decision-making**: Provides specific resolutions for OQs (003, 005, 007, 008, 009) rather than deferring
- **Requirement traceability**: Every milestone explicitly lists FR/NFR/SC/RISK coverage
- **Parallelization specifics**: Identifies exact milestone pairs that can run concurrently
- **MCP degradation testing**: Dedicates a full milestone with structured verification
- **Legacy removal safety**: Explicitly defers old directory removal until after validation

### Haiku Analyzer is stronger in:
- **Phase granularity**: 8 phases with clearer single-responsibility boundaries
- **Risk narrative quality**: More detailed probability/severity reasoning with ownership assignments
- **Negative-path testing**: Broader fixture coverage for failure scenarios
- **Determinism specificity**: Enumerates exactly which artifacts must be identical
- **Timeline realism**: Day-based estimates with optimistic/likely/conservative ranges
- **Contract framework isolation**: Treats contracts as a prerequisite, not bundled with feature work
- **Strategic framing**: Two-track delivery model and "strict gated delivery program" recommendation
- **Forward-looking concerns**: Schema versioning, non-code prerequisites

## 4. Areas Requiring Debate to Resolve

1. **Phase granularity (D-01)**: Should the roadmap use 5 coarser phases or 8 finer ones? The 8-phase model is safer for gating but adds coordination overhead.

2. **Contract framework timing (D-03)**: Should contracts be built as a standalone phase before any pipeline work, or can they be developed alongside Phase 0/1 implementation? This is a risk-vs-speed tradeoff.

3. **OQ blocking classification (D-04)**: OQ-007 (approval gate mechanism) vs OQ-008/OQ-009 (output defaults, test placement) — which are truly blocking for Phase 2? Both roadmaps should converge on a single blocking set.

4. **Legacy directory removal timing (D-05)**: Early removal (Haiku) vs deferred removal (Opus). Needs agreement on whether the old directory serves as a rollback path.

5. **Timeline units (D-02)**: "Sessions" vs "days" — the merged roadmap needs a single unit. Days are more plannable; sessions may better reflect the actual Claude Code execution model.

6. **Negative fixture scope (D-09)**: Should stale-ref, API-drift, and collision fixtures be part of the golden fixture suite or tested separately? Haiku's unified negative-path testing is more thorough but increases Phase H scope.

7. **Role definitions (D-06)**: Are explicit role assignments useful in a single-agent context, or do they add unnecessary abstraction? If multi-session parallel execution is planned, roles help; otherwise, they're noise.
