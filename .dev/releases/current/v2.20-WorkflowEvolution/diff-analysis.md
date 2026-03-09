

---
total_diff_points: 14
shared_assumptions_count: 12
---

# Diff Analysis: Opus-Architect vs Haiku-Analyzer Roadmaps

## 1. Shared Assumptions and Agreements

Both variants agree on these foundational points:

1. **Scope**: 41 requirements (31 functional, 10 non-functional), complexity 0.72, 5 domains
2. **Two validation boundaries**: Spec→Roadmap and Roadmap→Tasklist fidelity gates
3. **Gate fixes needed**: REFLECT_GATE promotion to STRICT, `_cross_refs_resolve()` stub replacement
4. **SPEC_FIDELITY_GATE**: STRICT enforcement, blocks on `high_severity_count > 0`
5. **Degraded mode**: `validation_complete: false` + `fidelity_check_attempted: true` → warn, continue
6. **`--no-validate` must not skip spec-fidelity** (FR-010)
7. **State persistence**: `fidelity_status` in `.roadmap-state.json` with `pass|fail|skipped|degraded`
8. **Tasklist CLI**: `superclaude tasklist validate <output-dir>` with same option set
9. **No new executor framework**: existing pipeline abstractions preserved
10. **Immediate-upstream-only validation layering** (no spec→tasklist leapfrog)
11. **Multi-agent mode should be deferred** (documentation-only in this release)
12. **Warning-first cross-reference rollout** recommended over immediate blocking

## 2. Divergence Points

### D-01: Phase Structure and Count
- **Opus-Architect**: 4 phases + pre-implementation decisions (effectively 5 stages)
- **Haiku-Analyzer**: 7 phases (Phase 0–6), with explicit Spec Reconciliation, Testing, and Rollout phases
- **Impact**: Haiku's granularity provides clearer milestones and exit criteria per concern; Opus's consolidation reduces coordination overhead but bundles testing into each phase rather than isolating it.

### D-02: Phase Ordering — Gate Fixes vs Spec-Fidelity
- **Opus-Architect**: Phase 1 combines gate fixes + deviation format + semantic checks (foundation-first)
- **Haiku-Analyzer**: Phase 1 is data model only; gate fixes are Phase 3 (after spec-fidelity in Phase 2)
- **Impact**: Opus fixes broken gates before building new ones (risk-ordered). Haiku gets the new fidelity capability online faster but leaves broken gates unfixed until Phase 3, risking false confidence in intermediate pipeline runs.

### D-03: Pre-Implementation Decision Handling
- **Opus-Architect**: Lists 4 key decisions with inline recommendations, expects 1-day resolution
- **Haiku-Analyzer**: Dedicates a full Phase 0 (0.5–1.0 weeks) to resolve all 8 open questions with formal deliverables (decision log, approved schema)
- **Impact**: Haiku treats decision closure as a first-class phase with exit criteria, reducing ambiguity risk. Opus assumes faster resolution but may leave gaps if decisions slip.

### D-04: Deviation Table Schema Recommendation
- **Opus-Architect**: Recommends 7-column schema with generic `Upstream Quote`/`Downstream Quote`, drops `Source Pair` column (encoded in frontmatter)
- **Haiku-Analyzer**: Flags the 7-vs-8-column decision as unresolved, lists both `Spec Quote/Roadmap Quote` and `Upstream Quote/Downstream Quote` as options without committing
- **Impact**: Opus provides a concrete, implementable decision. Haiku defers, which is safer if stakeholder input is genuinely needed but adds latency.

### D-05: Timeline Estimates
- **Opus-Architect**: ~22 working days (~3–4 weeks), compressible to ~17 days with parallelization
- **Haiku-Analyzer**: 5.0–6.5 weeks (risk-adjusted)
- **Impact**: ~40-65% longer estimate from Haiku. Reflects analyzer conservatism around decision latency and regression fallout. Opus's estimate assumes smoother decision resolution and tighter execution.

### D-06: Dedicated Testing Phase
- **Opus-Architect**: Tests are embedded within each phase with explicit test lists and exit criteria
- **Haiku-Analyzer**: Phase 5 is an entire dedicated testing/performance/regression phase
- **Impact**: Opus's approach catches regressions earlier (per-phase). Haiku's consolidated phase ensures comprehensive cross-phase regression analysis but delays final validation evidence.

### D-07: Dedicated Rollout Phase
- **Opus-Architect**: Rollout is implicit in Phase 4 ("Integration Hardening"), no separate monitoring/rollback plan
- **Haiku-Analyzer**: Phase 6 is explicit rollout with monitoring metrics, rollback triggers, and operational guidance
- **Impact**: Haiku provides production-readiness rigor. Opus assumes the developer deploying understands rollout risks without formal guidance.

### D-08: Retrospective Wiring Placement
- **Opus-Architect**: Phase 4 (final phase) — retrospective wiring + integration hardening
- **Haiku-Analyzer**: Not given a dedicated phase; retrospective prompt insertion is covered as a test case in Phase 5
- **Impact**: Opus explicitly implements FR-027/028/029 as deliverables. Haiku mentions retrospective in testing but doesn't clearly scope its implementation phase, creating a gap.

### D-09: Test Count Specificity
- **Opus-Architect**: Specifies exact test counts — 22 unit, 8 integration, 4 E2E, with named test functions
- **Haiku-Analyzer**: Describes test categories and coverage areas but doesn't enumerate specific test functions or counts
- **Impact**: Opus provides an immediately actionable test plan. Haiku's approach is more flexible but less verifiable for completeness.

### D-10: New File/Module Organization
- **Opus-Architect**: Lists specific new files: `roadmap/fidelity.py`, `cli/tasklist/` module, `tests/roadmap/test_fidelity.py`, etc.
- **Haiku-Analyzer**: Defers module placement to Phase 0 decision (`cli/tasklist/` vs extending `cli/roadmap/`)
- **Impact**: Opus is implementation-ready. Haiku avoids premature commitment but adds a decision dependency.

### D-11: Performance Measurement Timing
- **Opus-Architect**: Performance measured per-phase (SC-011 in Phase 2, SC-012 in Phase 4)
- **Haiku-Analyzer**: Explicitly recommends "performance telemetry part of acceptance, not post-release observation" but consolidates measurement in Phase 5
- **Impact**: Contradiction in Haiku — advocates early measurement but defers it. Opus practices what Haiku preaches.

### D-12: Risk Prioritization Framing
- **Opus-Architect**: Risk table ordered by severity with phase mapping and residual risk assessment
- **Haiku-Analyzer**: Risks ordered by priority with detailed analyzer recommendations per risk, including "treat as pre-implementation blocker" guidance
- **Impact**: Haiku's risk analysis is more actionable (with explicit recommendations). Opus's is more compact and phase-linked.

### D-13: Resource/Team Description
- **Opus-Architect**: Focuses on external/internal dependency tables; assumes single developer
- **Haiku-Analyzer**: Describes 5 distinct engineering capability roles (pipeline, prompt, CLI, QA, analyzer)
- **Impact**: Haiku's role breakdown is useful for team planning. Opus's single-developer framing is more realistic for the project's likely execution context.

### D-14: Multi-Agent Deferral Specificity
- **Opus-Architect**: Stubs merge function with `NotImplementedError` behind `--multi-agent` flag, documents protocol
- **Haiku-Analyzer**: Recommends "avoid partial implementation of multi-agent semantics" — no stub, just documentation
- **Impact**: Opus leaves a hook for future work. Haiku avoids any partial implementation that could be mistakenly relied upon.

## 3. Areas Where One Variant Is Clearly Stronger

### Opus-Architect Strengths
- **Implementation specificity**: Named test functions, exact file paths, concrete schema decisions — ready to code from
- **Risk-ordered phasing**: Fixes broken gates first (Phase 1) before building new features on top
- **Parallelization analysis**: Identifies that Phases 2 and 3 can overlap, compressing the critical path
- **Retrospective implementation**: Explicitly scopes FR-027/028/029 as Phase 4 deliverables

### Haiku-Analyzer Strengths
- **Decision hygiene**: Phase 0 prevents coding against ambiguous requirements
- **Rollout safety**: Dedicated Phase 6 with monitoring, rollback triggers, and operational guidance
- **Risk analysis depth**: Per-risk analyzer recommendations with actionable severity framing
- **Validation philosophy**: "Anything not backed by a test, benchmark, or artifact replay should not be considered done"
- **Schema ambiguity as top risk**: Correctly identifies that prompt/parser/test divergence is the highest-impact early risk

## 4. Areas Requiring Debate to Resolve

1. **Gate fixes before or after spec-fidelity?** Opus's risk-first ordering (fix gates → build new) vs Haiku's capability-first ordering (build fidelity → then harden gates). The risk argument favors Opus; the velocity argument favors Haiku.

2. **Dedicated testing phase vs per-phase testing?** Opus embeds tests; Haiku consolidates. Hybrid approach (per-phase unit tests + consolidated integration/E2E phase) may be optimal.

3. **Timeline realism**: 3–4 weeks (Opus) vs 5–6.5 weeks (Haiku). The gap is ~60%. True answer depends on decision latency and regression discovery rate. If open questions resolve in 1 day (as Opus assumes), Opus's timeline is credible. If they take a week, Haiku's is more accurate.

4. **Stub vs no-stub for multi-agent**: Opus's `NotImplementedError` stub provides a future hook but risks accidental invocation. Haiku's "document only" is cleaner but loses the code-level placeholder.

5. **Retrospective implementation ownership**: Opus scopes it explicitly; Haiku treats it as a test concern without clear implementation phasing. Needs resolution to avoid it falling through the cracks.

6. **Rollout formality**: Is a dedicated rollout phase warranted for an internal pipeline tool, or is Opus's integration-hardening approach sufficient? Depends on team size and artifact corpus sensitivity.
