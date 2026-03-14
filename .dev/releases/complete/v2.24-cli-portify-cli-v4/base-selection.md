

---
base_variant: "B (Haiku-Architect)"
variant_scores: "A:74 B:81"
---

# Base Selection: CLI-Portify v2.24 Roadmap Evaluation

## 1. Scoring Criteria (Derived from Debate)

The debate surfaced 5 key architectural tensions. Combined with general roadmap quality, I use these 8 criteria:

| # | Criterion | Weight | Rationale |
|---|-----------|--------|-----------|
| C1 | Risk management / front-loading decisions | 15% | D-1 debate: Phase 0 necessity |
| C2 | Dependency sequencing correctness | 15% | D-3/D-4 debate: infrastructure parallelization safety |
| C3 | Validation approach completeness | 12% | D-8 debate: matrix vs layers |
| C4 | Timeline actionability | 10% | D-9 debate: qualitative vs quantitative |
| C5 | Signal/vocabulary resolution strategy | 8% | D-5 debate: upfront vs emergent |
| C6 | Implementation granularity & clarity | 15% | Phase decomposition, milestone definition |
| C7 | Failure handling & resume design | 15% | Contract emission, resume semantics, operational resilience |
| C8 | Architectural recommendations quality | 10% | Actionability of final guidance |

## 2. Per-Criterion Scores

### C1: Risk Management / Front-Loading Decisions (15%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 6/10 | No Phase 0. Open questions listed in Section 7 with blocking annotations, but resolution is deferred to just-in-time. Debate Round 2 showed A's "generic `timeout_seconds: int`" argument was weakened by B's point about needing two separate fields. |
| B (Haiku) | 9/10 | Explicit Phase 0 with 3 work items, decision triage into must-resolve/safe-defaults/defer. Directly addresses the debate's convergence toward "lightweight Phase 0." Decision record artifact is concrete and auditable. |

**Rationale**: The debate reached partial convergence favoring a lightweight Phase 0. B implements this directly; A omits it entirely.

### C2: Dependency Sequencing Correctness (15%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 6/10 | Phase 5 (infrastructure) runs parallel with Phase 2+. Critical path diagram shows fork. A's Round 2 rebuttal that `PortifyProcess` inherits stable API was countered by B's point that the *extension surface* (`--add-dir`, timeout state, diagnostics) is the actual risk. |
| B (Haiku) | 9/10 | Phase 3 (subprocess orchestration core) is a prerequisite gate before content steps. "Build the platform, stabilize it, then build on it." Milestone M3 explicitly gates Phase 4. For a first implementation, this is the safer ordering. |

**Rationale**: This was the sharpest unresolved debate point. B's position that extension-surface instability creates hidden integration costs is more defensible for a v1 implementation. A's parallelization is a valid optimization for future releases.

### C3: Validation Approach Completeness (12%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 8/10 | SC-001 through SC-014 automated validation matrix with direct criterion-to-test traceability. Clean, auditable table. Missing the layer-based organization for test execution. |
| B (Haiku) | 8/10 | Layer-based test organization (unit → integration → compliance → architectural). Evidence package concept for release readiness. Missing the direct SC-criterion traceability matrix. |

**Rationale**: The debate converged strongly here — both approaches are complementary, not competing. Both score equally; the merge should combine them.

### C4: Timeline Actionability (10%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 5/10 | S/M/L qualitative sizing only. No temporal reference frame. A's rebuttal that the 10.5-18 day range "communicates the same thing as S/M/L with more digits" was countered by B's point that it establishes a 2-3 week project scope. |
| B (Haiku) | 8/10 | Per-phase day ranges (0.5-3 days), total 10.5-18 days, 3-week cadence with weekly milestone checkpoints. Ranges acknowledge uncertainty while enabling planning. |

**Rationale**: B's week-by-week cadence creates natural progress checkpoints. A provides no temporal reference frame for measuring slippage.

### C5: Signal/Vocabulary Resolution Strategy (8%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 7/10 | GAP-008 listed as blocking for Phase 5. Correctly identifies that ad-hoc signal naming leads to inconsistency. But "blocking" framing is stronger than needed per debate convergence. |
| B (Haiku) | 7/10 | Signal extraction implemented as part of Phase 3 monitoring work. Debate convergence: define minimal constants early, extend during implementation. B's approach is slightly under-specified on initial vocabulary. |

**Rationale**: Both converged to essentially the same position. Neither fully captured the agreed resolution (minimal vocabulary in Phase 1, extend in Phase 3).

### C6: Implementation Granularity & Clarity (15%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 7/10 | 5 phases, clear milestone structure. Phase 1-4 well-defined. Phase 5 is a catch-all for cross-cutting concerns — monitor, resume, diagnostics, gates bundled together without clear sequencing. |
| B (Haiku) | 9/10 | 8 phases (0-7) with finer decomposition. Phase 3 (subprocess orchestration) separated from Phase 4 (content generation) — this separation directly addresses the D-3/D-4 debate. Phase 6 (UX/resume/hardening) and Phase 7 (validation/release) are distinct operational concerns. Each phase has explicit exit criteria. |

**Rationale**: B's finer decomposition produces clearer dependency boundaries and more actionable milestones. A's Phase 5 bundles too many concerns.

### C7: Failure Handling & Resume Design (15%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 7/10 | Resume commands for resumable failures (SC-014). R-7 addresses partial synthesize-spec. Contract emission on all exit paths. But resume semantics are deferred to open questions rather than designed. |
| B (Haiku) | 9/10 | Dedicated Phase 6 for resume semantics, comprehensive failure-path enumeration (7 specific failure types listed), explicit resumability matrix concept, "prefer re-running `synthesize-spec` over trusting partially gated output" — a concrete architectural decision rather than a deferred question. |

**Rationale**: B makes concrete resume design decisions where A defers them. B's enumeration of 7 failure types and dedicated hardening phase shows deeper operational thinking.

### C8: Architectural Recommendations Quality (10%)

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 8/10 | 6 specific recommendations. #3 (test harness for Claude subprocess mocking) and #6 (convergence loop as standalone component) are high-value, actionable insights not present in B. |
| B (Haiku) | 8/10 | 5 final recommendations. #2 (contracts/gates/artifacts as real system boundary) and #3 (explicit state machines) are architectural principles that guide implementation decisions. |

**Rationale**: Both provide strong recommendations with different strengths. A's are more tactical (test harness, standalone convergence engine); B's are more principled (system boundaries, state machines).

## 3. Overall Scores

| Criterion | Weight | A (Opus) | B (Haiku) | A Weighted | B Weighted |
|-----------|--------|----------|-----------|------------|------------|
| C1: Risk management | 15% | 6 | 9 | 0.90 | 1.35 |
| C2: Dependency sequencing | 15% | 6 | 9 | 0.90 | 1.35 |
| C3: Validation completeness | 12% | 8 | 8 | 0.96 | 0.96 |
| C4: Timeline actionability | 10% | 5 | 8 | 0.50 | 0.80 |
| C5: Signal vocabulary | 8% | 7 | 7 | 0.56 | 0.56 |
| C6: Implementation granularity | 15% | 7 | 9 | 1.05 | 1.35 |
| C7: Failure/resume design | 15% | 7 | 9 | 1.05 | 1.35 |
| C8: Recommendations | 10% | 8 | 8 | 0.80 | 0.80 |
| **Total** | **100%** | | | **6.72→74** | **7.52→81** |

**Variant A (Opus): 74/100**
**Variant B (Haiku): 81/100**

## 4. Base Variant Selection Rationale

**Selected base: Variant B (Haiku-Architect)**

B wins on the three highest-weighted criteria: risk management (Phase 0), dependency sequencing (subprocess platform as prerequisite gate), and failure/resume design (dedicated hardening phase with concrete decisions). These are not stylistic differences — they represent fundamentally safer architectural choices for a first implementation of a complex 7-step pipeline.

B's finer phase decomposition (8 phases vs 5) produces clearer dependency boundaries and more actionable milestones without adding unnecessary complexity. Each additional phase represents a genuine architectural separation (subprocess platform vs content generation, operational hardening vs validation).

A's key advantage — infrastructure parallelization — is a valid optimization that should be noted for v2.25+ but is correctly deferred in a v1 implementation where the extension surface is unproven.

## 5. Specific Improvements from Variant A to Incorporate in Merge

### Must incorporate:

1. **SC-001 through SC-014 validation matrix** (A, Section 5): Add as a traceability cross-reference index alongside B's layer-based test organization. The debate explicitly converged on "use both." Each SC criterion maps to test type and validation method.

2. **Recommendation #3: Claude subprocess mock harness** (A, Section 8): "Build a test harness for Claude subprocess mocking early" — high-value tactical recommendation absent from B. Add to Phase 3 deliverables.

3. **Recommendation #6: Standalone convergence engine** (A, Section 8): "Design the convergence loop as a standalone, testable component" — architecturally sound advice for the highest-complexity subsystem. Add to B's Phase 5 work items.

4. **Pre-implementation validation checklist** (A, Section 4): The 5-item checklist (import test, template verification, claude binary, skills, pyproject.toml) is more concrete than B's equivalent. Replace B's dependency management recommendations with A's checklist.

5. **Qualitative sizing as cross-check** (A, Section 6): Add S/M/L labels alongside B's day ranges per the debate's partial convergence on timeline format.

### Consider incorporating:

6. **Explicit critical path diagram** (A, Section 6): The `Phase 1 → Phase 2 → Phase 3 → Phase 4` notation with parallel fork is a useful visual. Adapt it to B's 8-phase structure.

7. **Risk R-9 self-portification** (both mention it, A's framing is slightly cleaner): Retain B's placement but use A's concise mitigation language.

8. **Section 7 blocking annotations** (A): A's per-question blocking-phase annotations (`[Blocking Phase 4]`, `[Advisory]`) are more actionable than B's Phase 0 triage approach. Merge A's annotation style into B's open questions handling.
