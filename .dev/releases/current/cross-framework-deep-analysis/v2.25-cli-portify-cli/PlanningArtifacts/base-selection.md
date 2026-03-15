---
base_variant: B
variant_scores: "A:74 B:81"
---

## 1. Scoring Criteria (Derived from Debate)

The debate identified seven consequential divergence points. Scoring weights reflect the severity of each point as argued:

| Criterion | Weight | Basis |
|---|---|---|
| **C1** Phase structure clarity & implementation guidance | 15% | Round 1–3 dispute on 6 vs 11 phases; resolved in favor of 11 |
| **C2** Pre-implementation risk gate (Phase 0) | 15% | Both conceded Phase 0 is warranted; quality of OQ handling matters |
| **C3** Timeline & planning actionability | 12% | Both sides conceded estimates matter; qualitative vs quantitative |
| **C4** Risk completeness & roadmap response linkage | 13% | 12 risks with roadmap-response vs 9 risks without |
| **C5** Gate specification completeness | 12% | Both conceded inline gate mapping should be included |
| **C6** Validation traceability (SC-to-phase + sequence) | 13% | Both conceded both table + sequence are needed |
| **C7** Observability placement (structural vs advisory) | 10% | Both conceded structural enforcement is superior |
| **C8** Approval file safety | 10% | Variant A conceded; firm YAML validation is correct |

---

## 2. Per-Criterion Scores

### C1 — Phase Structure Clarity (15%)

**Variant A (6 phases):**  
Coarser phases reduce cognitive overhead but group heterogeneous concerns (e.g., Phase B: gates + executor + observability). The parallelization opportunity notes within phases argue implicitly for finer decomposition. Score: **60/100**

**Variant B (11 phases):**  
Single-responsibility phases with clear scope sections. The final synthesis position from both variants is 11 implementation phases + 3 super-milestones. Variant B is structurally aligned with this conclusion. Phase ordering issue (observability at Phase 8) is a conceded weakness, mitigable by reordering. Score: **82/100**

---

### C2 — Pre-Implementation Risk Gate (15%)

**Variant A:**  
Distributes OQ resolution "before respective phases." Has all 14 OQs enumerated. Does not have a formal Phase 0. The debate established this creates mid-sprint context-switching risk on contract-critical modules. Score: **55/100**

**Variant B:**  
Explicit Phase 0 with 5 blocking OQs as exit criterion. Accepts Variant A's 14 OQs as completeness input (Round 3 concession). The OQ scope dispute (5 vs 14 exit criterion) is a medium-stakes residual; Variant B's "blocking OQs resolved" exit criterion is the correct design. Score: **80/100**

---

### C3 — Timeline & Planning Actionability (12%)

**Variant A:**  
Qualitative effort descriptors ("Medium," "Large") for 6 phases. Acknowledged as insufficient in Round 3 concession. Provides no sprint planning anchor. Score: **38/100**

**Variant B:**  
Per-phase day ranges (0.5–22.5 days total), super-milestone groupings with cumulative estimates, effort split recommendations (40/25/20/15%). Provides sprint planning baseline even with acknowledged 50% spread. Score: **88/100**

---

### C4 — Risk Completeness & Roadmap Response (13%)

**Variant A:**  
9 risks across two tables + 1 unlisted architectural risk callout (Framework Base Type Stability). Mitigations are detailed. No "roadmap response" field linking risk to delivery phase. Score: **68/100**

**Variant B:**  
12 numbered risks with severity ratings, mitigations, and explicit "Roadmap response" fields. Missing Framework Base Type Stability risk (conceded in Round 3). The roadmap-response linkage is the meaningful differentiator for delivery planning. Score: **79/100** (−5 for missing base type stability, which must be added in merge)

---

### C5 — Gate Specification Completeness (12%)

**Variant A:**  
Milestone B1 provides the full gate-to-check mapping inline: `EXIT_RECOMMENDATION` for specific gate IDs, `has_zero_placeholders` for G-010, step-count consistency for G-008, return type pattern for G-006. Directly actionable. Score: **90/100**

**Variant B:**  
Phase 3 lists gate categories without per-gate check mapping. Variant B conceded in Round 3 that the mapping should be included. The content exists in Variant A and can be incorporated in merge. Score: **60/100** (gap is real but fillable)

---

### C6 — Validation Traceability (13%)

**Variant A:**  
14-row SC-to-phase validation matrix with phase assignment and test type. Clear 1:1 SC traceability. Missing 9-stage execution sequence. Score: **75/100**

**Variant B:**  
Three-category structure (structural/behavioral/operational) plus 9-stage recommended sequence. SC mapping exists in Section 5C but not in table form. Variant B conceded the SC-to-phase table should be included. Score: **72/100**

*Both variants are deficient relative to the merged target; gap is small.*

---

### C7 — Observability Placement (10%)

**Variant A:**  
Observability in Phase B alongside executor core — structurally enforced as an early implementation concern. Cannot be skipped or reordered without redefining Phase B. Score: **85/100**

**Variant B:**  
Phase 8 in position 8; advisory "recommended execution order" section suggests partial Phase 8 before Phase 4. Variant B conceded this is a structural defect. Score: **55/100** (the merge must reorder observability as a formal prerequisite to Phase 4)

---

### C8 — Approval File Safety (10%)

**Variant A:**  
R-008 notes "consider adding YAML parse validation" — framed as optional. Variant A conceded this in Round 2. Score: **52/100**

**Variant B:**  
Final Recommendation #4 makes YAML parse + schema validation a firm recommendation. Correctly identifies the risk that string matching on `status: approved` silently passes malformed YAML. Score: **85/100**

---

## 3. Overall Scores

| Criterion | Weight | Variant A | Variant B |
|---|---|---|---|
| C1 Phase structure | 15% | 60 | 82 |
| C2 Phase 0 gate | 15% | 55 | 80 |
| C3 Timeline actionability | 12% | 38 | 88 |
| C4 Risk completeness | 13% | 68 | 79 |
| C5 Gate specification | 12% | 90 | 60 |
| C6 Validation traceability | 13% | 75 | 72 |
| C7 Observability placement | 10% | 85 | 55 |
| C8 Approval file safety | 10% | 52 | 85 |
| **Weighted total** | | **64.9 → 74** | **75.6 → 81** |

*Scores rounded to nearest integer for display.*

**Variant A: 74 | Variant B: 81**

---

## 4. Base Variant Selection Rationale

**Selected base: Variant B**

The selection is driven by three factors where the score differential is largest and the consequences are most significant:

**C3 (Timeline, Δ=50 pts weighted):** Variant A's qualitative effort descriptors are the single largest practical deficiency. Both architects acknowledged this in Round 3. A roadmap for a 0.92-complexity system with 65 requirements must support sprint planning. Variant B's 15–22.5 day range with per-phase granularity, super-milestone groupings, and effort split percentages gives a project manager actionable input even with acknowledged uncertainty.

**C2 (Phase 0, Δ=25 pts weighted):** Variant B's mandatory pre-implementation confirmation gate directly addresses rework risk on the most-coupled modules (`models.py`, `process.py`, return contract). Both variants converged on Phase 0 being warranted. Variant B encodes it structurally; Variant A distributes OQ resolution across phases.

**C1 (Phase structure, Δ=22 pts weighted):** The final merged position from the debate is 11 implementation phases + 3 super-milestones. Variant B is this structure. Variant A's 6-phase groupings map cleanly onto Variant B's super-milestone layer (Foundations/Pipeline Generation/Quality Loop), making them fully compatible with Variant B as base.

Variant A's advantages on C5 (gate mapping, Δ=30 pts) and C7 (observability placement, Δ=30 pts) are real but additive — the content can be incorporated from Variant A into Variant B without structural surgery. The inverse is not true: retrofitting Variant B's timeline model, Phase 0, and 11-phase structure onto Variant A would require rebuilding the skeleton.

---

## 5. Specific Improvements from Variant A to Incorporate

### 5.1 Gate-to-Check Mapping (C5 gap — HIGH priority)

Incorporate Variant A's Milestone B1 inline mapping into the merged Phase 3 milestone:
- `EXIT_RECOMMENDATION` marker: gates G-002, G-003, G-005–G-008, G-010
- `has_zero_placeholders`: G-010
- Step-count consistency check: G-008
- Return type pattern check: G-006

This is the most technically specific content in either roadmap and directly reduces implementation error risk on the correctness-critical gate layer.

### 5.2 Framework Base Type Stability Risk (C4 gap — HIGH priority)

Add to Variant B's risk section as Risk 13 (or elevate to Highest-Priority tier):

> **Framework Base Type Stability**: All domain models extend `PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `GateMode`, `SemanticCheck`. A base type API change breaks all domain models.  
> **Mitigation**: Pin to current framework API. Add integration test that imports all base types. Document exact base type interface contract.  
> **Roadmap response**: Confirm in Phase 0 (architecture baseline); enforce in Phase 2 (base-type inheritance implementation).

Variant B's Round 3 concession explicitly accepted this addition.

### 5.3 SC-to-Phase Validation Matrix (C6 gap — MEDIUM priority)

Incorporate Variant A's 14-row table mapping each SC to a phase and validation method alongside Variant B's existing 9-stage validation sequence. These answer different questions (SC-X lives in which phase vs. run tests in what order) and are complementary, not redundant, as both variants agreed in Round 3.

### 5.4 Observability Structural Reordering (C7 gap — HIGH priority)

Variant B's recommended execution order correctly identifies the risk but fails to encode it structurally. The merge must make `OutputMonitor` baseline and `execution-log` infrastructure a formal Phase 2 dependency (alongside executor skeleton) rather than Phase 8. Specifically:
- Move `OutputMonitor` tracking fields, `execution-log.jsonl` skeleton, and basic stall detection into Phase 2 scope
- Phase 8 retains `PortifyTUI`, `PortifyTUI` lifecycle, and advanced diagnostics
- Add explicit dependency annotation to Phase 4: "Requires: Phase 2 observability baseline complete"

### 5.5 OQ Completeness Input for Phase 0 (C2 refinement — MEDIUM priority)

Phase 0 in the merged roadmap should reference Variant A's full 14-OQ enumeration as the completeness input for the assessment, while using Variant B's 5 contract-affecting OQs as the minimum exit criterion. This resolves the residual Round 3 dispute: Phase 0 assesses all 14, exits when blocking OQs are resolved, and documents non-blocking OQs for their respective phase.

The specific OQs to add to Phase 0's scope from Variant A's Section 4:
- OQ-009 (failure_type enum) — affects `PortifyValidationError` in Phase 1
- OQ-013 (PASS_NO_SIGNAL retry behavior) — affects executor logic in Phase 2
- OQ-002 (kill signal mechanism) — affects process.py in Phase 2

These are not in Variant B's five blocking OQs but affect contracts materially enough to resolve before coding those modules.
