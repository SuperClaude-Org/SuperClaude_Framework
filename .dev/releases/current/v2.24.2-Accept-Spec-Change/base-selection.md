---
base_variant: "Opus (Variant A)"
variant_scores: "A:81 B:74"
---

## 1. Scoring Criteria (Derived from Debate)

The debate surfaced seven substantive divergence points. I derive eight evaluation criteria from these, weighted by their architectural and delivery impact:

| # | Criterion | Weight | Source |
|---|-----------|--------|--------|
| C1 | Implementation specificity & actionability | 15% | D-1, D-3, D-4 |
| C2 | Phase structure & overhead calibration | 15% | D-1, D-4 |
| C3 | Timeline realism | 10% | D-3 |
| C4 | Risk identification depth | 15% | D-6, D-10 |
| C5 | Validation traceability | 15% | D-7 |
| C6 | Defensive design stance | 10% | D-6, D-10 |
| C7 | Architectural clarity & constraint enforcement | 10% | Core convergence areas |
| C8 | Operational completeness (edge cases, open questions) | 10% | D-6, D-10, Phase 4 |

## 2. Per-Criterion Scores

| Criterion | Variant A (Opus) | Variant B (Haiku) | Rationale |
|-----------|-----------------|-------------------|-----------|
| **C1: Implementation specificity** | **9/10** | 7/10 | Opus provides numbered sub-tasks with explicit function names, file paths, and FR/AC mappings per step. Haiku's actions are descriptive but less granular — e.g., Phase 1 lists 6 broad "key actions" vs Opus's 4 tightly scoped sub-phases with specific test targets. |
| **C2: Phase structure** | **8/10** | 6/10 | Opus's 5 phases map cleanly to deliverable boundaries. Haiku's Phase 0 adds 0.5 days for artifacts (design note, trace matrix) that the debate showed are largely resolvable by code inspection. Haiku's split of Phase 3 (executor threading) and Phase 4 (retry cycle) separates tightly coupled work — the debate's convergence assessment notes these are a single logical unit. |
| **C3: Timeline realism** | 7/10 | **8/10** | Haiku's rebuttal correctly identified that Opus's ~3-4 hours for Phase 3 (six-step disk-reread, recursion guard, detection gate, logging, all private functions) is optimistic. However, Haiku's 6-day elapsed estimate embeds team coordination overhead. Haiku scores slightly higher for acknowledging QA as first-class effort. |
| **C4: Risk identification** | 7/10 | **9/10** | Haiku identifies 7 risks vs Opus's 6, and critically elevates "stale in-memory state at resume boundary" (Risk 2) as a named top-level risk — this is the most architecturally consequential failure mode. Opus subsumes it under Phase 3 implementation notes. Haiku's Risk 7 (timestamp ambiguity) is also more precisely articulated. |
| **C5: Validation traceability** | **9/10** | 8/10 | Opus provides a complete AC-1 through AC-14 table with test approach and automation status per row — immediate auditability. Haiku's 5-layer pyramid provides better *structural* guidance for test organization but requires cross-referencing to verify AC coverage. The debate's convergence assessment recommends combining both approaches. |
| **C6: Defensive design** | 6/10 | **9/10** | Haiku's fail-closed stance on `started_at` fallback is stronger on safety grounds, as the debate acknowledged. Haiku's insistence on intentional documentation of YAML boolean coercion (vs Opus's implicit acceptance) is strictly more correct. Haiku's recommendation to treat missing `started_at` as "retry condition not met" is the safer default for an optimization path. |
| **C7: Architectural clarity** | **8/10** | 8/10 | Both are equivalent on core architecture (leaf module, private functions, `auto_accept` parameter). Haiku's "Architectural priorities" section at the top is slightly more explicit about invariants, but Opus's "Key architectural decision" paragraph is equally clear. Tie. |
| **C8: Operational completeness** | 7/10 | **8/10** | Haiku's "Architect recommendations" section (6 items) and "Acceptance gate for release" (6 criteria) provide clearer operational guardrails. Opus's open questions section is well-structured but defers more decisions to "before Phase 3" without specifying fallback behavior as precisely. |

## 3. Overall Scores

### Variant A (Opus): **81/100**

**Strengths**: Superior implementation specificity — a developer could start coding from this roadmap with minimal interpretation. The flat AC table provides immediate audit traceability. The 5-phase structure is lean and maps directly to deliverables. File lists, function names, and verification commands are concrete.

**Weaknesses**: Underestimates Phase 3 effort. Fails-open on `started_at` which the debate showed is the weaker safety position. Treats YAML boolean coercion as implicit rather than intentional.

### Variant B (Haiku): **74/100**

**Strengths**: Superior risk analysis, particularly around stale in-memory state and timestamp ambiguity. Stronger defensive design stance. Better structural guidance for test organization. The "Architect recommendations" section provides valuable implementation guardrails.

**Weaknesses**: Phase 0 is overhead for this complexity level (debate showed most questions are code-inspectable). Splitting executor integration and retry cycle into separate phases (3 and 4) creates an artificial boundary in tightly coupled work. The 3-role staffing model inflates the timeline without matching the single-developer reality of this codebase. Actions within phases are less granular and less immediately actionable.

## 4. Base Variant Selection Rationale

**Opus (Variant A)** is selected as the base because:

1. **Actionability**: The roadmap's primary consumer is the implementing developer. Opus's sub-task granularity, explicit function names, file paths, and per-phase verification commands make it immediately executable. Haiku requires more interpretation before coding can begin.

2. **Phase efficiency**: Opus's 5-phase structure eliminates Phase 0 overhead and keeps the executor work (Haiku's Phases 3+4) as a single coherent phase. The debate's own convergence assessment validated that Phase 0's questions are mostly resolvable by code inspection.

3. **Traceability**: The flat AC table is the more immediately useful validation artifact. Haiku's pyramid can be incorporated as test directory structure without replacing the traceability table.

4. **Debate alignment**: The debate's convergence summary recommends "Opus's implementation specificity and AC traceability with Haiku's risk depth, validation layering, and defensive design stance" — this is best achieved by starting from Opus and merging in Haiku's strengths, not vice versa.

## 5. Specific Improvements to Incorporate from Haiku (Variant B)

### Must-incorporate (high impact):

1. **`started_at` fallback → fail-closed** (Risk 7, D-6): Replace Opus's P4.2 recommendation ("skip mtime check if no timestamp") with Haiku's stance: treat missing `started_at` as retry condition not met, fall through to normal failure path. The operator retains the explicit `accept-spec-change` CLI command as fallback. This is the stronger safety position for an optimization path.

2. **Stale in-memory state as named risk** (Haiku Risk 2): Add as a top-level risk in Opus's risk table. This is the most architecturally consequential failure mode and deserves explicit visibility, not burial in implementation notes.

3. **YAML boolean coercion: intentional documentation** (D-10): Modify Opus's P4.1 to require that accepted YAML 1.1 coercions (`yes`, `on`, `1`) are explicitly documented in operator-facing docs and tested intentionally, not merely accepted by library default. Add a test for string `"true"` rejection.

4. **Architect recommendations section**: Append Haiku's 6 recommendations (especially #1: disk reread as non-negotiable invariant, #4: test-first for abort/failure paths) as implementation guidance in the merged roadmap.

### Should-incorporate (moderate impact):

5. **Test directory structure from 5-layer pyramid**: Use Haiku's Layer 3 (state integrity) and Layer 5 (failure-path) as named test categories within the test files, ensuring proportional attention to failure paths rather than happy-path bias.

6. **Acceptance gate for release** (Haiku §5): Add as Phase 5 exit criteria — the 6-point checklist (no circular deps, no new public API, no subprocess in patch module, etc.) is a concrete quality gate.

7. **Resolve open questions as Phase 2 exit criteria** (debate recommendation): Instead of Opus's "before Phase 3" loose guidance, make `started_at` fallback and severity field source explicit Phase 2 exit criteria.

### Skip (low value or counterproductive):

8. **Phase 0**: Do not incorporate. The debate showed its deliverables are either trivially producible (trace matrix ≈ the roadmap itself) or resolvable by code inspection (severity field source).

9. **3-role staffing model**: Do not incorporate. This is a single-developer task in this codebase context.

10. **Phase 3/4 split**: Do not incorporate. Keep executor integration as a single phase — the retry cycle cannot be meaningfully tested without the threading and detection gate.
