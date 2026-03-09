---
base_variant: "A (Opus-Architect)"
variant_scores: "A:82 B:63"
---

# Base Selection Report: v2.20 WorkflowEvolution Roadmap

## 1. Scoring Criteria (Derived from Debate)

Ten criteria extracted from the 14 debate points (D-01 through D-14) and 3 rounds of argumentation:

| # | Criterion | Weight | Source Debate Points |
|---|-----------|--------|---------------------|
| 1 | Phase Structure Proportionality | 10% | D-01 |
| 2 | Gate Fix Ordering Correctness | 10% | D-02 |
| 3 | Decision Handling Adequacy | 10% | D-03 |
| 4 | Implementation Specificity | 10% | D-08, D-09 |
| 5 | Risk Analysis Depth | 10% | Cross-cutting |
| 6 | Timeline Realism | 10% | D-05 |
| 7 | Testing Strategy Quality | 10% | D-06 |
| 8 | Rollout Safety | 10% | D-07 |
| 9 | Architectural Clarity | 10% | Cross-cutting |
| 10 | Actionability | 10% | Cross-cutting |

---

## 2. Per-Criterion Scores

### Criterion 1: Phase Structure Proportionality (D-01)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 8/10 | 4 phases + pre-impl day. Each phase is a coherent delivery unit with clear exit criteria. Proportionate to 0.72-complexity, single-developer context. |
| B | 5/10 | 7 phases creates granularity disproportionate to scope. B conceded Phase 0 can compress and Phase 6 may be disproportionate — effectively admitting 2 of 7 phases are over-engineered. |

**Evidence**: B's Round 3 concession: "A full week for decision closure is conservative" and "A dedicated rollout phase may be disproportionate."

### Criterion 2: Gate Fix Ordering Correctness (D-02)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 9/10 | Phase 1 fixes gates (REFLECT_GATE, cross-refs) before Phase 2 builds spec-fidelity. Architecturally sound: fix foundations before building on them. |
| B | 4/10 | Phase 2 (spec-fidelity) precedes Phase 3 (gate fixes). B conceded this ordering was incorrect in Round 3: "Gate fixes should precede spec-fidelity, not follow it." |

**Evidence**: B's Round 3 concession: "The architectural argument is sound: building new validation on known-broken infrastructure creates ambiguity about which results to trust."

### Criterion 3: Decision Handling Adequacy (D-03)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 7/10 | Addresses 4 key decisions (OQ-001, OQ-004, OQ-006, OQ-007) with concrete recommendations. However, A conceded OQ-002 and OQ-003 also need explicit resolution before Phase 3. |
| B | 8/10 | Addresses all 8 open questions with exit criteria. Over-scoped at 1 week but the coverage is more thorough. B correctly identified that OQ-002 (module placement) affects file organization. |

**Evidence**: A's Round 3 concession: "OQ-002 and OQ-003 deserve explicit decisions before Phase 3. Module placement does affect import paths and CLI registration."

### Criterion 4: Implementation Specificity (D-08, D-09)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 9/10 | Names 22 unit tests, 8 integration tests, 4 E2E tests with specific function names. Lists exact new files and modified files. Provides concrete dataclass field definitions, exact module paths. |
| B | 6/10 | Describes "key actions" and validation strategies at category level. B conceded in Round 3: "Test function naming at roadmap level is useful... mapping tests to criteria by name provides traceability." |

**Evidence**: A lists `test_cross_refs_resolve_valid`, `test_spec_fidelity_gate_blocks_high`, etc. B describes "unit tests for cross-reference resolution" without naming them. B's concession validates A's approach.

### Criterion 5: Risk Analysis Depth

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 7/10 | Clean risk table with 8 risks, severity, phase, mitigation, residual risk. Practical and concise. |
| B | 9/10 | Same 8 risks but with per-risk "Analyzer Recommendation" annotations providing actionable judgment. Priority ordering section adds strategic value. Numbered mitigation steps are more structured. |

**Evidence**: B's RSK-003 mitigation includes "Analyzer recommendation: Require baseline artifact audit before enabling blocking behavior" — this is actionable guidance A lacks. B's priority ordering ("Ambiguity elimination > Gate correctness > Regression containment...") provides strategic framing.

### Criterion 6: Timeline Realism (D-05)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 8/10 | 22 working days (~5 weeks after concession), parallelization noted with caveats. Honest after concession. |
| B | 7/10 | 5.0-6.5 weeks risk-adjusted. More conservative but B's own Phase 0 (0.5-1.0 week) and Phase 6 (0.5 week) inflate the estimate with work B later conceded was disproportionate. |

**Evidence**: After Round 3 concessions, A converged to ~5 weeks and B to 5.5-6.0 weeks — a 0.5-1.0 week gap reflecting "genuinely different assumptions about regression discovery rate" per the debate summary.

### Criterion 7: Testing Strategy Quality (D-06)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 9/10 | Per-phase test lists with named functions, validation matrix mapping all 14 success criteria to specific methods and phases. Coverage targets stated (22 unit, 8 integration, 4 E2E). |
| B | 7/10 | Validation strategy categorized (A-E: unit, integration, E2E, performance, rollout) which is good for comprehensiveness. But lacks the traceability of named tests. Phase 5 dedicated testing is work A already does in Phase 4. |

**Evidence**: A's validation matrix explicitly maps SC-001 through SC-014 to test methods and phases. B's approach is more abstract — "Validate with integration test simulating `high_severity_count > 0`" without naming the test function.

### Criterion 8: Rollout Safety (D-07)

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 7/10 | Warning-first cross-refs (OQ-001), artifact regression testing before deployment. Safety embedded in implementation phases rather than a separate phase. |
| B | 7/10 | Dedicated Phase 6 with monitoring metrics, rollback triggers, failure-state documentation. More thorough but B conceded it may be disproportionate for the current user base. |

**Evidence**: Tie. Both achieve rollout safety through different structures. B's rollout concerns are valid but A's approach of embedding them as exit criteria is sufficient.

### Criterion 9: Architectural Clarity

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 9/10 | Section 5 lists all new files (`src/superclaude/cli/roadmap/fidelity.py`, `src/superclaude/cli/tasklist/`, etc.) and all modified files with specific changes per file. Clear dependency table. |
| B | 5/10 | Resource requirements section is role-based ("Pipeline/gate engineer", "Prompt/validation engineer") rather than file-based. Useful for team staffing but not for a single-developer implementation plan. Dependencies listed but without file-level specificity. |

**Evidence**: A's "New Files Created" and "Modified Files" subsections give a developer an exact file map. B's "Technical Dependencies" lists modules but doesn't specify what changes where.

### Criterion 10: Actionability

| Variant | Score | Justification |
|---------|-------|---------------|
| A | 9/10 | A developer can start Phase 1 immediately: fix REFLECT_GATE tier in `validate_gates.py`, replace stub in `_cross_refs_resolve()`, create `FidelityDeviation` in `roadmap/fidelity.py`. Every deliverable has a concrete location and test. |
| B | 5/10 | Requires Phase 0 completion before any code. Phase 1 deliverables are described abstractly ("Introduce `FidelityDeviation` dataclass" without specifying which file). Key actions lack the precision needed to start immediately. |

**Evidence**: Compare Phase 1 deliverables — A specifies "Change enforcement tier from STANDARD to STRICT in `validate_gates.py`"; B says "Promote `REFLECT_GATE` from `STANDARD` to `STRICT`" without the file path.

---

## 3. Overall Scores

| Variant | Score | Breakdown |
|---------|-------|-----------|
| **A (Opus-Architect)** | **82/100** | 8+9+7+9+7+8+9+7+9+9 |
| **B (Haiku-Analyzer)** | **63/100** | 5+4+8+6+9+7+7+7+5+5 |

### Score Justification

**Variant A wins on**: gate fix ordering (B conceded), implementation specificity (B conceded named tests are useful), architectural clarity, actionability, phase structure proportionality, and testing strategy. These are the criteria most critical for a single-developer implementation plan.

**Variant B wins on**: decision handling coverage (all 8 OQs vs A's 4) and risk analysis depth (per-risk analyst recommendations with priority ordering). These are strategic strengths that should be merged into the base.

**The 19-point gap** reflects a fundamental framing difference: A is an implementation roadmap optimized for execution; B is an analysis document optimized for risk awareness. For a roadmap's primary purpose — guiding implementation — A is significantly more effective.

---

## 4. Base Variant Selection Rationale

**Selected base: Variant A (Opus-Architect)**

Reasons:

1. **Correct ordering**: A fixes broken gates before building new capabilities — B conceded this was the right approach. This is not a stylistic preference; it's an architectural correctness issue.

2. **Higher actionability**: A provides file-level specificity throughout (new files, modified files, named tests, exact module paths). A developer can start coding from this roadmap without further discovery.

3. **Proportionate structure**: 4 phases for a 0.72-complexity project executed by a single developer. B's 7 phases include two (Phase 0, Phase 6) that B itself conceded could be compressed or eliminated.

4. **Debate convergence**: The debate's own synthesis recommendation aligns with A's structure — "A's ordering", "A's implementation specificity", "A's parallelization analysis", and a 5-phase structure that maps closely to A's 4 phases plus expanded decision handling.

5. **Testing traceability**: A maps all 14 success criteria to specific test methods in a validation matrix. This is directly usable for implementation verification.

---

## 5. Improvements from Variant B to Incorporate in Merge

### Must incorporate (high-value additions):

1. **Expanded decision handling**: A's pre-implementation section should address all 8 open questions (adding OQ-002, OQ-003, OQ-005, OQ-008 with concrete recommendations), compressed to 2-3 days per B's concession. A already conceded OQ-002 and OQ-003 need explicit resolution.

2. **Per-risk analyst recommendations**: B's "Analyzer recommendation" annotations for each risk add actionable judgment that A's risk table lacks. Example: "Require baseline artifact audit before enabling blocking behavior" (RSK-003) and "Prioritize deterministic parser and semantic guardrails over prompt-only trust" (RSK-007).

3. **Risk priority ordering**: B's "Analyzer Priority Order" (ambiguity elimination > gate correctness > regression containment > deterministic parsing > performance > rollout safety) provides strategic framing absent from A.

4. **Validation philosophy as cross-cutting principle**: B's formulation — "Anything not backed by a test, benchmark, or artifact replay should not be considered done" — should be elevated to a project-level quality principle.

5. **Rollout concerns as Phase 4 exit criteria**: B's monitoring metrics (false positive rate, degraded-run frequency, pipeline time drift, LLM severity drift) and rollback trigger concepts should be embedded in A's Phase 4 exit criteria rather than creating a separate phase.

### Consider incorporating (moderate value):

6. **Analyzer assessment framing**: B's executive summary includes a risk concentration analysis ("disproportionate risk concentrated in LLM-output consistency, gate strictness rollouts, cross-reference validation regressions") that sharpens the reader's attention. Add a brief risk concentration note to A's executive summary.

7. **Validation layering guard** (NFR-010/AC-004): B explicitly calls out the risk of tasklist validation comparing against original spec instead of immediate upstream. A assumes this but doesn't flag it as a specific test target. Add a named test: `test_tasklist_validates_against_roadmap_not_spec`.

8. **Performance telemetry as acceptance criterion**: B's recommendation to "make performance telemetry part of acceptance, not post-release observation" reinforces A's SC-011/SC-012 but should be made more explicit — measure during Phases 2-3, not just Phase 4.

### Do not incorporate (low value or counterproductive):

- Phase 0 as a separate phase (B conceded compression; embed in A's pre-impl section)
- Phase 6 as a separate rollout phase (B conceded it may be disproportionate)
- Role-based resource requirements (irrelevant for single developer)
- Abstract "key actions" format (A's specificity is superior)
- Gate fix ordering after spec-fidelity (B conceded this was wrong)
