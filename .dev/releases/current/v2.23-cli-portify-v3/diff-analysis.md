

---
total_diff_points: 14
shared_assumptions_count: 12
---

# Diff Analysis: Opus-Architect vs Haiku-Analyzer Roadmaps

## 1. Shared Assumptions and Agreements

1. **Spec source and complexity**: Both cite `spec-cli-portify-workflow-evolution.md` with complexity 0.65
2. **Core transformation**: Replace code-generation Phase 3 + integration Phase 4 with spec synthesis + panel review
3. **Phases 0-2 immutability**: Both treat existing Phases 0-2 as untouched
4. **Template location**: `src/superclaude/examples/release-spec-template.md` with `{{SC_PLACEHOLDER:name}}` sentinels
5. **Brainstorm embedding**: Inline multi-persona (architect + analyzer + backend), non-interactive
6. **Panel review structure**: Focus pass (correctness, architecture) → critique pass (4 quality dimensions) → convergence loop (max 3 iterations)
7. **Additive-only constraint**: Incorporation of findings must not rewrite existing content
8. **Quality threshold**: `overall >= 7.0` gates `downstream_ready`
9. **Return contract completeness**: Must emit on success, failure, and dry-run with the same schema
10. **Failure defaults**: Quality scores = `0.0` (not null), `downstream_ready = false`
11. **`--skip-integration` removal**: Both agree this flag must be removed
12. **Sync requirement**: `make sync-dev` + `make verify-sync` after all changes

## 2. Divergence Points

### D-01: Phase Count and Granularity
- **Opus-Architect**: 6 phases (Template → Phase 3 Rewrite → Phase 4 Rewrite → Contract & Command → Validation → Sync & Docs)
- **Haiku-Analyzer**: 7 phases (adds Phase 0: Baseline Verification and Boundary Lock; splits CLI Surface from Contract work)
- **Impact**: Haiku's Phase 0 adds a formal scope-lock gate that reduces risk of accidental edits to immutable phases. Opus assumes this verification is implicit. Haiku's split of contract (Phase 4) from CLI surface (Phase 5) allows independent validation of each concern.

### D-02: Timeline Estimates
- **Opus-Architect**: 8-12 working days
- **Haiku-Analyzer**: 4-6 working days
- **Impact**: Nearly 2x difference. Opus allocates 2-3 days each for Phase 3 and Phase 4 rewrites; Haiku allocates 1-1.5 days each. Opus may be more realistic for a cautious implementation; Haiku may underestimate the complexity of convergence loop implementation.

### D-03: Explicit Phase 0 Baseline Verification
- **Opus-Architect**: No explicit baseline phase; jumps straight to template creation
- **Haiku-Analyzer**: Dedicated Phase 0 with dependency trace, change inventory, regression checklist
- **Impact**: Haiku's approach provides a formal "measure twice" gate. Opus relies on the implementer to verify boundaries informally during Phase 1.

### D-04: Milestone Gate Structure
- **Opus-Architect**: Milestones M1-M6 with exit criteria per phase
- **Haiku-Analyzer**: Milestones M0-M6 plus 4 named gates (A-D) with explicit "must have" checklists
- **Impact**: Haiku's dual-layer (milestones + gates) provides more decision points for go/no-go. Opus's exit criteria are embedded inline, which is simpler but less auditable as separate checkpoints.

### D-05: Risk Identification Scope
- **Opus-Architect**: 6 risks (R-003 through R-009, selective from spec), plus 2 architectural attention items
- **Haiku-Analyzer**: 9 risks (R1-R9) with explicit priority tiers (high/medium/lower)
- **Impact**: Haiku identifies risks Opus omits: additive incorporation introducing contradictions (R5), orphaned reference artifacts (R9). Opus uniquely calls out quality score calibration as an open architectural concern.

### D-06: Convergence Loop Characterization
- **Opus-Architect**: Describes convergence as a conditional loop with escalation path
- **Haiku-Analyzer**: Explicitly recommends treating convergence as a "controlled-state machine, not an informal retry loop"
- **Impact**: Haiku's framing is more rigorous and implementation-guiding. A state machine model naturally handles edge cases (interrupted mid-loop, resume semantics) better than a conditional loop mental model.

### D-07: Resource/People Requirements
- **Opus-Architect**: Does not specify people or roles; implicitly assumes a single implementer
- **Haiku-Analyzer**: Specifies 4 roles (analyzer lead, architect reviewer, backend/protocol maintainer, QA/quality engineer)
- **Impact**: Haiku's role specification is more realistic for a team environment but may be over-specified for a solo developer workflow. Opus's omission is simpler but less actionable for resource planning.

### D-08: Validation Taxonomy
- **Opus-Architect**: Lists 11 self-validation checks + 5 E2E scenarios in a single validation phase
- **Haiku-Analyzer**: Categorizes validation into 5 types (Structural, Behavioral, Contract, Boundary, E2E) with explicit evidence requirements
- **Impact**: Haiku's taxonomy makes it easier to trace which validation category covers which risk. Opus's flat list is complete but harder to audit for coverage gaps.

### D-09: Downstream Compatibility Verification
- **Opus-Architect**: Single E2E test (SC-011: spec consumed by `sc:roadmap`); defers contract compatibility to Open Question 8
- **Haiku-Analyzer**: Explicit Phase 6 action item + Gate D requirement; recommends validating actual interoperability, not just score thresholds
- **Impact**: Haiku treats downstream compatibility as a first-class validation concern rather than an open question. This is stronger for ensuring the pipeline actually works end-to-end.

### D-10: Open Questions Treatment
- **Opus-Architect**: 5 numbered open questions with explicit recommendations for each
- **Haiku-Analyzer**: No dedicated open questions section; concerns are embedded in risk mitigations and recommendations
- **Impact**: Opus's explicit OQ section is better for tracking unresolved decisions. Haiku's distributed approach risks losing track of items requiring resolution.

### D-11: Parallelization Assessment
- **Opus-Architect**: Explicitly notes limited parallelization (~0.5 day savings from overlapping Phase 4 contract work with late Phase 3)
- **Haiku-Analyzer**: Does not discuss parallelization opportunities
- **Impact**: Minor. Both roadmaps are essentially sequential. Opus's explicit acknowledgment sets realistic expectations.

### D-12: Documentation and Decisions Tracking
- **Opus-Architect**: Phase 6 includes `decisions.yaml` update and documentation reference updates
- **Haiku-Analyzer**: Mentions `decisions.yaml` update as conditional ("if required") in Phase 5
- **Impact**: Opus treats documentation as a mandatory deliverable; Haiku treats it as optional. For a protocol change of this scope, mandatory is more appropriate.

### D-13: Template Validation Depth
- **Opus-Architect**: Validates template works for 4 spec types (new feature, refactoring, portification, infrastructure)
- **Haiku-Analyzer**: Validates against 12 required sections + placeholder safety but does not explicitly test cross-type reusability
- **Impact**: Opus's cross-type validation catches template generalization failures earlier. Haiku's section-level validation is more granular but narrower in scope.

### D-14: Failure Path Testing Priority
- **Opus-Architect**: Failure/resume testing is part of Phase 5 validation alongside happy-path tests
- **Haiku-Analyzer**: Explicitly recommends "test failure paths early" (Recommendation #4) and "prioritize contract correctness before polish" (Recommendation #1)
- **Impact**: Haiku's emphasis on early failure-path testing is a stronger risk mitigation strategy. Discovering contract issues in the final validation phase is costly.

## 3. Areas Where One Variant Is Clearly Stronger

### Opus-Architect Strengths
- **Open questions tracking**: Explicit numbered OQ section with actionable recommendations
- **Timeline realism**: More conservative estimates (8-12 days) likely better reflect actual effort
- **Files modified table**: Clear mapping of which files change in which phase
- **Parallelization analysis**: Honest assessment of limited opportunities
- **Cross-type template validation**: Tests template generalization across 4 spec types

### Haiku-Analyzer Strengths
- **Phase 0 baseline verification**: Formal scope lock before any implementation begins
- **Validation taxonomy**: 5-category classification (Structural/Behavioral/Contract/Boundary/E2E) with evidence requirements
- **Risk prioritization**: Explicit high/medium/lower tiers with more comprehensive coverage
- **Convergence as state machine**: More rigorous framing for a complex control-flow concern
- **Failure-first testing philosophy**: Recommendations #1 and #4 correctly prioritize the highest-risk paths
- **Gate structure**: Named gates (A-D) provide clearer go/no-go decision points
- **Downstream verification emphasis**: Treats interoperability as a gate requirement, not an open question

## 4. Areas Requiring Debate to Resolve

1. **Timeline**: 8-12 days (Opus) vs 4-6 days (Haiku). The true estimate likely depends on whether this is a solo developer or team effort — needs calibration against actual resource availability.

2. **Phase 0 necessity**: Is a formal baseline verification phase worth 0.5 days, or is it overhead for a well-scoped change? Haiku argues it prevents scope creep; Opus argues the scope is already clear from the spec.

3. **When to test failure paths**: Opus defers all validation to Phase 5. Haiku recommends testing failure contracts as soon as they're implemented (Phase 4). The debate is about discovery cost vs. implementation flow.

4. **Convergence modeling**: Loop (Opus) vs state machine (Haiku). A state machine is more rigorous but adds implementation complexity. Is that complexity justified for a max-3-iteration loop?

5. **Role specification**: Should the roadmap prescribe team roles (Haiku) or remain role-agnostic (Opus)? Depends on whether this is a planning document or an implementation guide.

6. **Documentation as mandatory vs conditional**: Opus mandates `decisions.yaml` updates; Haiku makes them conditional. Given this is a protocol-level change, the mandatory approach seems safer, but this should be confirmed against project conventions.
