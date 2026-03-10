

---
base_variant: A
variant_scores: "A:74 B:71"
---

# Base Selection: v2.22 RoadmapRemediate Roadmap Variants

## 1. Scoring Criteria (Derived from Debate)

The debate surfaced 12 dispute points (D-001 through D-012). I derive 8 scoring criteria from the substantive disagreements and convergence areas:

| # | Criterion | Weight | Rationale |
|---|-----------|--------|-----------|
| 1 | Phase Structure & Risk Reduction | 15% | D-001: Phase 0 debate; structural soundness |
| 2 | Timeline Realism | 10% | D-002: 7-9 vs 17-24 days; credibility of estimates |
| 3 | Dependency Sequencing | 15% | D-003, D-004, D-005: state schema, tasklist, gate timing |
| 4 | Implementation Detail & Actionability | 15% | D-006, D-011, D-012: module naming, critical path, internal sequencing |
| 5 | Risk Assessment Depth | 10% | D-007: risk identification and mitigation specificity |
| 6 | Open Question Strategy | 10% | D-009: resolution vs default approach |
| 7 | Validation & Testing Strategy | 15% | D-010: test taxonomy, coverage strategy |
| 8 | Spec Traceability | 10% | FR/NFR/SC coverage completeness |

## 2. Per-Criterion Scores

### C1: Phase Structure & Risk Reduction (15%)

**Variant A: 7/10** — Clean 6-phase structure maps to deliverable milestones. No Phase 0 means faster start, but the debate showed this is a genuine risk for unfamiliar engineers. Variant A conceded nothing here, but Variant B's argument about structurally-impactful open questions (SIGINT affecting Phase 3 code, hash affecting Phase 1 schema) was not adequately refuted.

**Variant B: 8/10** — Phase 0 adds 0.5-1 day but addresses a real category of rework risk. The debate's convergence assessment agreed Phase 0 is valuable when team familiarity is uncertain. The layered approach (parsing → filtering → orchestration → certification → resume) is well-reasoned.

### C2: Timeline Realism (10%)

**Variant A: 6/10** — 17-24 days is defensible for a cautious delivery but the debate narrowed the realistic range to 10-14 days. Variant A's per-phase padding (e.g., 2-3 days for Phase 2's terminal prompt + filter functions) was effectively challenged by Variant B's enumeration of actual deliverables.

**Variant B: 7/10** — 7-9 days is aggressive but better calibrated to the spec's precision. The debate's convergence at 10-14 days validates that Variant B's baseline is closer to reality. However, the 1.5-2 day estimate for Phase 3 was challenged by Variant A's enumeration of 15 distinct deliverables with concurrency concerns.

### C3: Dependency Sequencing (15%)

**Variant A: 8/10** — State schema in Phase 1 alongside data model is architecturally coherent. The debate's compromise (shape in P1, field details in P5) validated Variant A's instinct. Tasklist timing was Variant A's weakest point — they conceded Variant B's two-write model is superior.

**Variant B: 7/10** — Tasklist-before-orchestration sequencing won the debate (Variant A conceded). State schema in Phase 5 was partially conceded by Variant B themselves (shape in P1 is reasonable). Gate placement logic is sound.

### C4: Implementation Detail & Actionability (15%)

**Variant A: 9/10** — Concrete module names (`remediate_prompts.py`, `certify_prompts.py`, `remediate_executor.py`) with import dependency table. 8-step internal Phase 3 build order. Critical path analysis (P1→P3→P4→P6) with parallel opportunity mapping. Variant B conceded all three of these as valuable additions.

**Variant B: 6/10** — Abstract descriptions ("pure prompt functions", "parallel dispatch and collection flow") without concrete module naming. No critical path analysis. No internal phase sequencing for the highest-risk phase. Variant B conceded these gaps explicitly in Round 3.

### C5: Risk Assessment Depth (10%)

**Variant A: 7/10** — 7 risks with severity/probability matrix and phase-addressed mapping. Identifies R-NEW-001 (atomic write race) and R-NEW-002 (ClaudeProcess drift). Lacks the "stale resume causing invalid certification" risk that Variant B highlighted.

**Variant B: 8/10** — 8 risks with stronger failure-mode focus. Explicitly calls out "stale resume causing invalid certification" and "certification false passes" as high-priority — both were acknowledged by Variant A as underweighted in their concessions.

### C6: Open Question Strategy (10%)

**Variant A: 7/10** — Provides 7 concrete recommended defaults. Pragmatic approach prevents blocking. However, the debate showed that at least 2 questions (SIGINT, hash algorithm) affect code structure and shouldn't be deferred.

**Variant B: 7/10** — Front-loads resolution but doesn't specify *what* the answers should be, only that they should be resolved. Less actionable as a planning document. The debate's compromise (resolve structural questions before P1, defer behavioral ones with defaults) splits the difference.

### C7: Validation & Testing Strategy (15%)

**Variant A: 6/10** — Two-layer approach (unit + integration) with per-phase exit criteria. Adequate but lacks the granularity that the debate proved valuable. Variant A conceded Variant B's 5-layer taxonomy is superior.

**Variant B: 9/10** — 5-layer taxonomy (unit, integration, contract, performance, failure-path) with explicit test targets per layer. SC-001 through SC-008 mapped to specific validation approaches. Failure-path tests as first-class category. This was a clear win acknowledged by both sides.

### C8: Spec Traceability (10%)

**Variant A: 8/10** — FR/NFR/SC references inline with deliverables. Module-to-phase mapping table. Token/cost estimates section. Clear traceability from spec requirements to phase deliverables.

**Variant B: 7/10** — SC mapping table is thorough. "Analyzer Priorities" sections add interpretive value. But FR/NFR references are less systematic within phase descriptions.

## 3. Overall Scores

| Criterion | Weight | Variant A | Variant B |
|-----------|--------|-----------|-----------|
| C1: Phase Structure | 15% | 7 | 8 |
| C2: Timeline Realism | 10% | 6 | 7 |
| C3: Dependency Sequencing | 15% | 8 | 7 |
| C4: Implementation Detail | 15% | 9 | 6 |
| C5: Risk Depth | 10% | 7 | 8 |
| C6: Open Questions | 10% | 7 | 7 |
| C7: Validation Strategy | 15% | 6 | 9 |
| C8: Spec Traceability | 10% | 8 | 7 |
| **Weighted Total** | **100%** | **7.35 → 74** | **7.15 → 71** |

**Variant A: 74/100** | **Variant B: 71/100**

## 4. Base Variant Selection Rationale

**Selected base: Variant A (Opus-Architect)**

The margin is narrow (3 points), and the selection is driven by structural factors:

1. **Implementation actionability** (C4) is the largest single differentiator (+3 points, 15% weight). Variant A's concrete module names, import dependency graphs, critical path analysis, and internal Phase 3 sequencing provide the scaffolding a downstream tasklist generator needs. Variant B conceded all three of these elements.

2. **Dependency sequencing** (C3) favors Variant A's state-schema-in-P1 approach, validated by the debate's compromise position.

3. **Spec traceability** (C8) is stronger in Variant A — FR/NFR references are inline with deliverables, making the roadmap self-documenting for compliance checking.

4. Variant A's weaknesses (timeline inflation, thin validation strategy) are easier to fix by incorporating Variant B's content than the reverse. Adding Phase 0 and a 5-layer test taxonomy to Variant A's structure is additive. Retrofitting concrete module names, critical path analysis, and internal phase sequencing into Variant B's structure would require restructuring.

## 5. Specific Improvements from Variant B to Incorporate in Merge

### Must incorporate (debate-settled convergence):

1. **Phase 0 (0.5 day)**: Add a scoped discovery phase resolving SIGINT handling, hash algorithm, and step wiring confirmation. Scope to structural questions only; defer behavioral defaults per Variant A's approach. *(From D-001, convergence assessment)*

2. **Tasklist two-write model**: Move tasklist initial generation to Phase 2 (plan artifact), update with outcomes post-Phase 3 execution. *(Variant A conceded D-004)*

3. **5-layer validation taxonomy**: Replace Variant A's 2-layer approach with Variant B's unit/integration/contract/performance/failure-path structure. Map to specific test targets. *(Variant A conceded D-010)*

4. **Risk additions**: Add "stale resume causing invalid certification" (R-NEW-003) and "certification false passes" (R-NEW-004) as high-priority risks with Variant B's mitigation strategies. *(Variant A conceded D-007)*

### Should incorporate (strengthening):

5. **Timeline adjustment**: Revise to 10-14 working days per the debate's convergence range. Compress Phase 2 to 1-1.5 days (from 2-3), keep Phase 3 at 4-6 days (slight reduction from 5-7 acknowledging Variant B's focused-engineering argument).

6. **"Analyzer Priorities" sections**: Add per-phase priority callouts from Variant B highlighting what matters most in each phase (e.g., "parser resilience is a critical dependency," "rollback logic must be tested before parallel execution is complete").

7. **State schema compromise**: Explicitly note two-stage approach — define schema shape in Phase 1, finalize metadata fields at Phase 4-5 boundary based on implementation evidence.

8. **Final recommendations section**: Incorporate Variant B's "Final Analyzer Recommendations" as a summary checklist (don't start with orchestration, treat rollback as release gate, optimize for correctness before speed).
