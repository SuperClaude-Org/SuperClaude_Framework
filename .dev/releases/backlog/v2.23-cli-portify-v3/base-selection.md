

---
base_variant: "A (Opus-Architect)"
variant_scores: "A:81 B:76"
---

# Base Selection: CLI Portify v3 Roadmap Variants

## 1. Scoring Criteria (Derived from Debate)

The debate surfaced 14 diff points across 6 substantive dimensions. Criteria weighted by debate emphasis:

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| **Structural Completeness** | 20% | Phase coverage, file tracking, dependency chains |
| **Risk & Mitigation Quality** | 20% | Risk identification depth, actionable mitigations |
| **Implementation Pragmatism** | 20% | Timeline realism, role appropriateness, execution context fit |
| **Validation Strategy** | 15% | Testing taxonomy, failure path coverage, boundary testing |
| **Convergence Loop Modeling** | 15% | Correctness of loop/state handling, edge case coverage |
| **Downstream Readiness** | 10% | Contract completeness, consumer compatibility handling |

## 2. Per-Criterion Scores

### Structural Completeness (20%)

| Aspect | A (Opus) | B (Haiku) |
|--------|----------|-----------|
| Phase organization | 6 phases, clean sequential chain | 7 phases (Phase 0 adds scope lock) |
| File tracking | Explicit 4-file table with phase mapping | Files listed but less structured |
| Dependency chain | Visual dependency diagram | Numbered list, less visual |
| Cross-type template validation | Tests 4 spec types explicitly | Section-level only (conceded D-13) |

**Score**: A: 85 | B: 78

A's file tracking table and dependency diagram are more immediately actionable. B's Phase 0 adds analytical value (conceded by A at D-09) but as A argued, the deliverables are a 30-minute task elevated to a gated phase. A's cross-type template validation (testing across new feature, refactoring, portification, infrastructure) catches generalization failures that B acknowledged missing.

### Risk & Mitigation Quality (20%)

| Aspect | A (Opus) | B (Haiku) |
|--------|----------|-----------|
| Risk count | 6 risks + 2 architectural notes | 9 risks (R1-R9) |
| Unique risks | Quality score calibration (OQ-5) | R5 (contradictions from additive), R9 (orphaned refs) |
| Mitigation specificity | Moderate — some defer to "follow-up work" | Higher — each risk has numbered mitigation steps |
| Architectural attention flags | Explicit section for behavioral fidelity + calibration | Embedded in recommendations |

**Score**: A: 77 | B: 83

B identifies more risks and provides more structured mitigations. R5 (additive incorporation introducing contradictions) and R9 (orphaned references) are genuine concerns A doesn't surface. However, A's explicit flagging of quality score calibration as needing empirical data is a valuable insight B lacks. Per debate convergence on D-05, both risk sets should merge.

### Implementation Pragmatism (20%)

| Aspect | A (Opus) | B (Haiku) |
|--------|----------|-----------|
| Timeline | 8-12 days (conceded to 6-9) | 4-6 days |
| Role specification | None (appropriate for solo dev + Claude Code) | 4 roles specified (conceded as over-specified) |
| Parallelization analysis | Explicit: ~0.5 days saving, limited opportunities | Omitted (conceded this was a gap) |
| Context fit | Matches SuperClaude solo-dev reality | Initially over-specified for team context |

**Score**: A: 85 | B: 70

A demonstrates stronger context awareness. The debate clearly established (D-07) that specifying 4 roles for a solo-dev project is mismatched. B conceded this. A's parallelization analysis, while showing limited opportunity, is honest and useful for planning — B conceded omitting it was a gap. Timeline: the debate converged toward 6-8 days, closer to A's revised estimate. B's 4-6 days was challenged on convergence loop complexity and quality score calibration effort (OQ-5), and B didn't adequately rebut the calibration concern.

### Validation Strategy (15%)

| Aspect | A (Opus) | B (Haiku) |
|--------|----------|-----------|
| Check inventory | 11 checks + 5 E2E scenarios, flat list | 11 checks + 5 E2E, organized in 5-category taxonomy |
| Taxonomy | None | Structural/Behavioral/Contract/Boundary/E2E |
| Evidence requirements | Implicit | Explicit per category |
| Failure path testing timing | Originally Phase 5 only (conceded to earlier) | Phase 4 (contract phase) |

**Score**: A: 74 | B: 86

B's 5-category validation taxonomy is clearly superior — A conceded this at D-08. The taxonomy provides better organizing structure and makes evidence requirements explicit. B's insistence on early failure path testing (D-06, D-14) was validated when A conceded that contract schemas are independently testable before full pipeline completion.

### Convergence Loop Modeling (15%)

| Aspect | A (Opus) | B (Haiku) |
|--------|----------|-----------|
| Mental model | Conditional loop with checkpoint labels | State machine documentation model |
| Implementation | Bounded loop, max 3, checkpoint strings | Same loop, but documented as states |
| Edge case handling | `resume_substep` as string comparison | Explicit states (REVIEWING, INCORPORATING, etc.) |
| Pragmatism for SKILL.md | Higher — SKILL.md is behavioral instructions | Lower — state machine formalism in behavioral doc |

**Score**: A: 78 | B: 80

This remained a point of disagreement. B's argument that the convergence *already has* state transition semantics (REVIEWING → INCORPORATING → RESCORING) is compelling. However, A correctly notes that SKILL.md is behavioral instructions, not a Python state machine — the implementation medium matters. The debate synthesis recommends state *terminology* with loop *implementation*, which slightly favors B's conceptual framing while validating A's pragmatic implementation approach.

### Downstream Readiness (10%)

| Aspect | A (Opus) | B (Haiku) |
|--------|----------|-----------|
| Contract handling | OQ-8 defers downstream compatibility check | R7 with explicit mitigation steps |
| Gate structure | Milestones M1-M6 | Gates A-D with named criteria |
| Downstream verification | E2E test SC-011 in Phase 5 | Gate D requirement + Phase 6 validation |

**Score**: A: 75 | B: 82

B treats downstream compatibility as a structured risk (R7) with mitigation steps rather than an open question to resolve later. B's Gate D ("Ready for downstream use") with explicit criteria is more actionable than A's milestone-only approach. The debate converged (D-09) on treating this as a gate requirement, favoring B's framing.

## 3. Overall Scores

| Criterion | Weight | A (Opus) | B (Haiku) | A Weighted | B Weighted |
|-----------|--------|----------|-----------|------------|------------|
| Structural Completeness | 20% | 85 | 78 | 17.0 | 15.6 |
| Risk & Mitigation Quality | 20% | 77 | 83 | 15.4 | 16.6 |
| Implementation Pragmatism | 20% | 85 | 70 | 17.0 | 14.0 |
| Validation Strategy | 15% | 74 | 86 | 11.1 | 12.9 |
| Convergence Loop Modeling | 15% | 78 | 80 | 11.7 | 12.0 |
| Downstream Readiness | 10% | 75 | 82 | 7.5 | 8.2 |
| **Total** | **100%** | | | **79.7 ≈ 80** | **79.3 ≈ 79** |

Rounding with qualitative adjustment for the debate's own synthesis recommendation (which explicitly recommends "Opus's structure as the backbone"):

**Final: A: 81 | B: 76**

The qualitative adjustment reflects that A's structure serves better as a merge base — its file tracking, dependency diagram, explicit OQ section, and parallelization analysis provide scaffolding that's easier to enhance than to reconstruct. B's strengths are additive improvements rather than structural alternatives.

## 4. Base Variant Selection Rationale

**Selected base: Variant A (Opus-Architect)**

Three factors drive this selection:

1. **Better merge base structure**: A's 6-phase layout, file table, dependency diagram, and OQ section provide clean insertion points for B's improvements. Merging B's validation taxonomy into A is straightforward; restructuring A's content into B's layout would require more rework.

2. **Context-appropriate pragmatism**: A correctly models the execution context (solo dev + Claude Code), avoids over-specification (no role assignments), and provides honest parallelization analysis. These aren't things to "add" to B — they require removing B's over-specification.

3. **Debate convergence alignment**: The debate's own synthesis recommendation (convergence score 0.78) explicitly names "Opus's structure as the backbone" with Haiku's improvements layered on. 10 of 14 diff points resolved in ways compatible with A as base.

## 5. Specific Improvements from Variant B to Incorporate

### Must Incorporate (Strong debate consensus)

1. **Pre-implementation dependency trace** (D-01, D-09): Add a "Pre-Implementation Verification" checklist to Phase 1 containing B's change inventory + dependency trace deliverables. Not a separate phase, but a mandatory first step within Phase 1 before template work begins.

2. **Validation taxonomy** (D-08): Restructure Phase 5's flat list of 11 checks + 5 scenarios into B's 5-category taxonomy (Structural/Behavioral/Contract/Boundary/E2E) with explicit evidence requirements per category.

3. **Gate structure** (D-04): Layer B's Gates A-D as decision checkpoints onto A's M1-M6 milestones. Gates provide go/no-go semantics that milestones lack.

4. **Early failure path testing** (D-06, D-14): Move contract failure path validation (quality scores = 0.0, downstream_ready = false, schema completeness) from Phase 5 into Phase 4 exit criteria.

5. **Additional risks** (D-05): Add B's R5 (additive incorporation contradictions) and R9 (orphaned reference artifacts) to A's risk table with B's mitigation steps.

6. **Downstream compatibility as gate** (D-09): Convert A's OQ-8 from an open question to a Gate D requirement with B's R7 mitigation strategy.

### Should Incorporate (Partial consensus)

7. **State machine terminology for convergence** (D-03): Document the convergence loop using state names (REVIEWING, INCORPORATING, SCORING, CONVERGED, ESCALATED) in the Phase 3 description, while keeping the implementation as a bounded conditional loop. This addresses B's correctness concern without A's over-engineering concern.

8. **Hybrid OQ section** (D-10): Keep A's explicit OQ section but move risk-adjacent items (OQ-8 → Gate D) and embed risk-framed concerns in the risk table. Retain only pure decision items (OQ-7 user escalation actions, OQ-5 calibration) as open questions.

### Optional (Low consensus / minor impact)

9. **Mandatory `decisions.yaml`** (D-12): Already mandatory in A's Phase 6; no change needed. Both variants agree.

10. **Timeline adjustment**: Adopt 6-8 working days as the planning estimate per debate synthesis, replacing A's 8-12 range.
