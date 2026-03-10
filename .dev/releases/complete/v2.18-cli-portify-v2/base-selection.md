

---
base_variant: A
variant_scores: "A:81 B:74"
---

# Base Selection: Opus Architect (A) vs Haiku Analyzer (B)

## Scoring Criteria

Derived from debate convergence points and persistent disagreements:

1. **Structural Coherence** (20%) — Phase organization, milestone clarity, dependency flow
2. **Execution Realism** (20%) — Honest estimation, actionable planning, single-agent context fit
3. **Safety & Risk Coverage** (20%) — Risk mitigation placement, failure handling, rollback strategy
4. **Requirement Traceability** (15%) — FR/NFR/SC mapping completeness and specificity
5. **Decisiveness** (15%) — Concrete resolutions vs deferred ambiguity
6. **Negative-Path Coverage** (10%) — Failure fixtures, degradation testing, edge cases

## Per-Criterion Scores

| Criterion | A (Opus) | B (Haiku) | Rationale |
|---|---:|---:|---|
| Structural Coherence | 17/20 | 14/20 | A's 5-phase/14-milestone structure balances granularity with coordination cost. B's 8 phases create real overhead at 0.92 complexity — more contracts, more boundary validations, more handoff points. Debate Round 2: A correctly identifies that B's Phase B (isolated contract testing with synthetic data) is weaker than testing contracts with real consumers. |
| Execution Realism | 16/20 | 13/20 | A's session-based estimates are honest about the single-agent execution model. B's day-based estimates (26-41 days, 58% spread on the conservative end) provide false precision — "working days" implies human staffing that doesn't exist here. A's 36% spread (14-19 sessions) is tighter. B's 5 named roles (Analyzer Lead, CLI Engineer, etc.) are noise in a single-agent context — B conceded this in Round 3. |
| Safety & Risk Coverage | 16/20 | 17/20 | B edges ahead: broader negative fixture suite (stale-ref, API-drift, name collision, non-portified collision as first-class fixtures), schema versioning as a prerequisite (A conceded this gap), and OQ-008 blocking classification (A conceded). B's dedicated Phase H for validation is conceptually cleaner, though A's distributed approach within Phase 5 is workable. |
| Requirement Traceability | 14/15 | 12/15 | A maps every milestone to specific FR/NFR/SC identifiers with inline references. B groups requirements by phase scope but is less precise about which milestone covers which requirement. A's Success Criteria Validation Matrix (§end) is a direct traceability artifact B lacks. |
| Decisiveness | 14/15 | 9/15 | A resolves `--dry-run` (Phases 0-2 only), `--skip-integration` (skip Phase 4), OQ-002 (inspect TurnLedger, remove if absent), OQ-007 (TodoWrite checkpoint pattern), and output defaults concretely. B defers most of these to "Phase A resolution." B conceded in Round 3 that A's `--dry-run` resolution is sound. A's position — "concrete decisions can be wrong, but they're debuggable; ambiguity is not" — is the stronger engineering stance. |
| Negative-Path Coverage | 4/10 | 9/10 | B is materially stronger here. Enumerated determinism artifacts (`source_step_registry`, `step_mapping`, `module_plan`) are more testable than A's "diff output." B's negative fixture suite treats failure scenarios as first-class test domain. A conceded both points in Round 3. |

## Overall Scores

| Variant | Score | Justification |
|---|---:|---|
| **A (Opus)** | **81/100** | Superior structure, honest execution model, decisive OQ resolution, strong traceability. Weaker on negative-path specificity and schema versioning (both conceded). |
| **B (Haiku)** | **74/100** | Stronger safety coverage and negative testing. Weaker on structural overhead (8 phases), false precision (day estimates), deferred decisions, and single-agent context fit (roles, progressive OQ resolution). |

## Base Variant Selection Rationale

**Variant A (Opus Architect)** is the base because:

1. **5-phase structure is the right granularity.** At 0.92 complexity, coordination overhead matters. A's 14 internal milestones provide equivalent failure isolation to B's 8 phases without the boundary tax. The debate showed B couldn't demonstrate material safety gain from finer phases — its strongest argument was "clearer failure signals," but A's milestone-level exit criteria achieve the same.

2. **Decisiveness reduces execution risk.** A resolves 7 of 10 OQs with concrete decisions. B defers most to "Phase A." In a single-agent context where the agent executes the roadmap, deferred decisions become implicit assumptions. A's approach of making debuggable decisions upfront is more practical.

3. **Session-based estimation is honest.** This is a Claude Code project. Sessions are the real execution unit. Converting to days adds a misleading layer of precision.

4. **Contract-with-consumers is sound engineering.** A's approach of building contracts alongside Phase 0/1 (real consumers) produces better-tested infrastructure than B's isolated Phase B with synthetic data. B's database-migration analogy doesn't hold — migrations are tested against schema, not synthetic queries.

5. **Traceability is built-in.** A's per-milestone requirement mapping and SC validation matrix mean compliance is verifiable at each checkpoint.

## Improvements to Incorporate from Variant B

The merge should adopt these specific elements from B:

1. **Schema versioning policy** (D-12) — Add to A's Milestone 2.1 as a prerequisite sub-task. Define backward-compatibility rules for contract schema changes during development. A conceded this gap.

2. **Determinism artifact enumeration** (D-11) — Replace A's "diff output" in Milestone 5.1 with B's specific list: `source_step_registry`, `step_mapping`, `module_plan`. These are concrete, diffable artifacts.

3. **Broader negative fixture suite** (D-09) — Add to A's Milestone 5.1: stale-ref fixture, API-drift fixture, non-portified collision fixture alongside the existing 4 golden fixtures. Keep them within Phase 5, not as a separate phase.

4. **OQ-008 as blocking** (D-04) — Reclassify in A's Milestone 1.3. Default output path affects contract emission and should be resolved before Phase 2.

5. **Day-based timeline as secondary annotation** (D-02) — Add day estimates alongside session counts in A's Timeline Summary table. Use sessions as primary, days as secondary for stakeholder communication.

6. **Legacy removal phrasing** (D-05) — Keep A's Phase 5 timing but adopt B's clearer language: "Deprecate in Phase 1; remove in Phase 5 after all validation passes."

7. **Contract schema testing with synthetic failures** — While A's consumer-driven testing is primary, add a sub-task in Milestone 2.1 to validate resume semantics with a synthetic failure before Phase 0 runs. This is a lightweight version of B's Phase B that doesn't require a separate phase.
