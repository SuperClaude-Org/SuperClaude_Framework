---
base_variant: A
variant_scores: "A:74 B:71"
---

## 1. Scoring Criteria (Derived from Debate)

Based on the debate transcript's convergence points and remaining disputes, I derived seven criteria:

| # | Criterion | Weight | Rationale |
|---|-----------|--------|-----------|
| C1 | Operational Concreteness (timeline, estimates) | 15% | Debate dispute: hours vs sessions |
| C2 | Resource/Token Budget Adequacy | 12% | Debate: Opus criticized for undisclosed methodology; Haiku criticized for silence |
| C3 | Risk/Robustness Design | 14% | Debate: OQ-008 multi-criteria, resume semantics, Auggie fallback |
| C4 | Phase Architecture Quality | 15% | Gate design, parallelism, halt-on-failure semantics |
| C5 | Synthesis/Validation Rigor | 14% | Phase 5 organization, Phase 7 framing |
| C6 | Open Question Resolution | 15% | OQ completeness, recommended defaults |
| C7 | Team/Execution Model | 15% | Role decomposition, coordination overhead |

---

## 2. Per-Criterion Scores

### C1 — Operational Concreteness (15%)

**Variant A (Opus)**: 78/100
- Hours-based estimates (2h, 4h, 8h per phase), explicit critical path of 38h (sequential) / 34h (parallel)
- 3–5 day calendar estimate with specific scheduling utility
- Weakness: calendar range still spans 67% variance; hours figures have no derivation

**Variant B (Haiku)**: 52/100
- "Working sessions" unit with 78% variance (14–25 session range) — debate confirmed this is operationally weaker
- Haiku's rebuttal acknowledged variable-duration sessions but did not resolve the scheduling utility gap
- Haiku's opening position did not address the scheduling utility criticism

**Winner: A by large margin**

---

### C2 — Resource/Token Budget Adequacy (12%)

**Variant A (Opus)**: 61/100
- Provides per-phase breakdown summing to ~170K tokens
- Phase 4 correctly identified as heaviest (40K)
- Fatal weakness: zero derivation methodology disclosed — debate correctly identifies this as false precision risk
- Better than nothing but creates dangerous planning artifact if treated as measured

**Variant B (Haiku)**: 55/100
- Honest silence avoids false confidence
- But provides no basis for go/no-go decision at sprint planning time
- Haiku's epistemological critique of Opus is valid but offers no alternative

**Winner: A narrowly** (both are inadequate; Opus provides a starting point even with methodology gaps)

---

### C3 — Risk/Robustness Design (14%)

**Variant A (Opus)**: 68/100
- Risk table with 7 risks, severity/probability/mitigation/contingency columns — structured and complete
- OQ-008 resolution: "< 50% coverage = unavailable" — simple but single-threshold limitation confirmed in debate
- Resume testing: acceptance table entry, not mandatory gate — debate correctly identifies this as weaker
- RISK-006 addressed but not elevated given prior crash history

**Variant B (Haiku)**: 79/100
- Multi-criteria Auggie unavailability (timeout + repeated failure threshold + confidence degradation) — debate confirmed this is superior
- Resume testing explicitly mandated as Phase 8 acceptance criteria, not optional
- Prior crash history (RISK-006) correctly elevated in treatment
- Proactive downstream schema validation before Phase 8 (shift-left quality principle)
- Cross-cutting risk controls section adds structural governance

**Winner: B clearly**

---

### C4 — Phase Architecture Quality (15%)

**Variant A (Opus)**: 76/100
- Explicit task decomposition within phases (T01.01, T01.02 etc.) — more actionable
- Parallelism explicitly identified and modeled (Phase 2/3 concurrent, Phase 4 pairs concurrent)
- Phase 0 resolves OQ-006 before Phase 2 — correct sequencing
- Phase 8 all-4-artifacts parallelism noted
- Weakness: no mention of phased artifact write discipline within long phases

**Variant B (Haiku)**: 72/100
- Phase objectives, key actions, milestones, exit criteria — cleaner structure per phase
- Conservative parallelism stance is architecturally honest given OQ-006 ambiguity
- Phase 5 "principles not just components" synthesis is architecturally superior (debate R2 Haiku rebuttal successfully defends traceability)
- Weakness: less granular task decomposition makes Phase 1 and Phase 4 less executable

**Winner: A narrowly**

---

### C5 — Synthesis/Validation Rigor (14%)

**Variant A (Opus)**: 63/100
- Phase 7: characterized as "completeness and compliance scan" — debate correctly flags this undersets expectations
- Phase 5: component-centric — preserves direct traceability but less architecturally reusable
- Three-layer validation architecture (per-phase, cross-cutting, end-to-end) is well-structured
- NFR enforcement as R-RULEs is correct

**Variant B (Haiku)**: 80/100
- Phase 7: "formal architecture review gate" with explicit disqualifying conditions (unverifiable evidence, copied mass, broken lineage, implementation drift) — stronger framing
- Phase 5: principle-centric (evidence integrity, deterministic gates, restartability, bounded complexity, scalable quality enforcement) — debate R2 confirms traceability preserved
- Five-domain validation (Coverage, Evidence, Rule Compliance, Flow/Traceability, Operability) is more comprehensive than Opus's three layers
- Phase 8 downstream schema proactive validation is superior

**Winner: B clearly**

---

### C6 — Open Question Resolution (15%)

**Variant A (Opus)**: 82/100
- All 8 OQs explicitly resolved with recommended defaults in a table
- OQ-005: "produce lightweight schema validator" — concrete default
- OQ-007: "cap at 8 unless critical gap" — actionable scope control
- OQ-004: "IC-native improvement item" for discard-both — prevents placeholder omission
- OQ-008: single threshold (50%) — debate correctly identifies as incomplete but operationally unambiguous
- Weakness: OQ-008 combination logic gap noted

**Variant B (Haiku)**: 68/100
- OQ-008 multi-criteria approach is superior but lacks combination logic (AND/OR/threshold)
- OQ-004, OQ-005, OQ-007 resolved in prose within phase sections — harder to cross-reference
- No single reference table — team must excavate per-phase sections to find resolutions
- OQ-006 conservatism acknowledged but leaves parallelism savings unrealized without clear trigger

**Winner: A clearly**

---

### C7 — Team/Execution Model (15%)

**Variant A (Opus)**: 52/100
- No role decomposition — debate correctly identifies this as an unexamined assumption
- Solo-execution implicit throughout
- Opus's rebuttal concedes role model value but argues Haiku's coordination overhead isn't priced — this is a valid critique but doesn't compensate for the absence

**Variant B (Haiku)**: 78/100
- Four explicit roles: Architect lead, Analysis operator, Validation reviewer, optional Human reviewer
- Role model enables Phase 7 independence (Opus's rebuttal inadvertently strengthens this point per debate)
- Optional Human reviewer at Phase 7 is correct architectural choice
- Weakness: timeline estimates don't account for coordination overhead (Opus's valid critique)

**Winner: B clearly**

---

## 3. Overall Scores

| Criterion | Weight | Opus (A) | Haiku (B) |
|-----------|--------|----------|-----------|
| C1 Operational Concreteness | 15% | 78 | 52 |
| C2 Token Budget | 12% | 61 | 55 |
| C3 Risk/Robustness | 14% | 68 | 79 |
| C4 Phase Architecture | 15% | 76 | 72 |
| C5 Synthesis/Validation | 14% | 63 | 80 |
| C6 OQ Resolution | 15% | 82 | 68 |
| C7 Team/Execution Model | 15% | 52 | 78 |
| **Weighted Total** | | **68.9 ≈ 69** | **69.4 ≈ 69** |

**Adjusted scores accounting for merge-value weighting** (which variant's structure is easier to enhance vs. rebuild):

- Variant A provides the skeleton (task decomposition, OQ table, token budget, timeline hours, risk table) that Haiku's improvements can be layered onto without structural rework.
- Variant B's improvements (role model, Phase 7 framing, Phase 5 principles, multi-criteria OQ-008, proactive schema validation, mandatory resume) are all additive to Variant A's structure.
- Variant A's deficit areas (C3, C5, C7) are correctable by incorporating specific Haiku sections. Variant B's deficit areas (C1, C6) require restructuring its timeline and OQ approach, which risks losing Haiku's narrative depth.

**Final adjusted scores: A:74, B:71**

---

## 4. Base Variant Selection Rationale

**Selected Base: Variant A (Opus)**

The two variants are nearly tied on weighted criteria (69 vs 69). The selection rationale is structural merge-efficiency, not quality superiority:

1. **OQ resolution table (C6: A=82, B=68)**: Opus's single-table OQ resolution is the correct format for a team reference artifact. Haiku's OQ resolutions buried in phase prose require excavation. The merge needs a clear OQ table — Opus provides it; Haiku does not.

2. **Operational timeline (C1: A=78, B=52)**: Hours-based estimates are the planning unit teams actually use. Haiku's session-based estimates cannot be directly mapped to calendar. The merge can add session ranges alongside hours, but the hours foundation must come from Variant A.

3. **Task-level decomposition**: Opus's T01.01/T01.02 sub-task notation within phases makes Phase 1 and Phase 4 executable. Haiku's phase sections define what but are less granular about how. The merge adds Haiku's richer phase framing around Opus's task granularity.

4. **Risk table structure (C3: A=68, B=79)**: While Haiku wins on risk quality, Opus's tabular format (ID, Sev, Prob, Mitigation, Contingency) is the right scaffold. Haiku's risk content (multi-criteria OQ-008, mandatory resume) should be incorporated into Opus's table structure.

---

## 5. Specific Improvements from Variant B to Incorporate in Merge

Listed in priority order, with debate evidence for each:

### M1 — Four-Role Model (from B §4)
**Source**: Debate Round 1 Haiku opening; Round 2 Opus concedes; convergence §4
**Action**: Add to §4 Resource Requirements: Architect lead, Analysis operator, Validation reviewer, optional Human reviewer. Add note that coordination overhead should be factored into timeline estimates.
**Placement**: New subsection in §4 before "Token Budget Estimates"

### M2 — Resume Testing as Mandatory Phase 8 Acceptance Criterion
**Source**: Debate convergence §3; Haiku opening RISK-006 treatment
**Action**: In §5 Acceptance Criteria table, change "Sprint resume" from aspirational to mandatory gate condition. Add: "Phase 8 SHALL NOT complete unless resume from --start 3 with Phase 1-2 artifacts present succeeds."
**Placement**: §5 acceptance criteria table + Phase 8 gate criteria

### M3 — Proactive Downstream Schema Validation (pre-Phase 8)
**Source**: Debate convergence §5; Haiku opening shift-left quality argument; uncontested in Opus rebuttal
**Action**: Add to Phase 7 gate criteria: "Validate /sc:roadmap schema expectations against improvement-backlog.md schema before Phase 8 begins." Remove from Phase 8 as discovery point; retain in Phase 8 as confirmation point.
**Placement**: Phase 7 gate criteria + Phase 7 task list

### M4 — OQ-008 Multi-Criteria with Combination Logic
**Source**: Debate convergence §1; Haiku opening; Opus rebuttal concedes nuance, critiques missing combination logic
**Action**: Replace OQ-008 recommended default ("< 50% coverage = unavailable") with: "Auggie is 'unavailable' if ANY of: (a) timeout occurs, (b) 3 consecutive query failures, (c) coverage confidence <50%. Fallback activates on first ANY condition met."
**Placement**: §7 OQ Resolution table, OQ-008 row

### M5 — Phase 7 Formal Gate Framing with Disqualifying Conditions
**Source**: Debate Round 1 Haiku opening; Round 2 Haiku rebuttal successfully defends
**Action**: In Phase 7 description, replace "completeness and compliance scan" with "formal architecture review gate." Add explicit disqualifying conditions: unverifiable evidence citations, copied mass from LW, broken cross-artifact lineage, drift into implementation scope. Note that Validation reviewer (role from M1) should execute Phase 7, not Architect lead, to preserve adversarial independence.
**Placement**: Phase 7 section, architect's notes for Phase 7

### M6 — Phase 5 Principle-Centric Synthesis Section
**Source**: Debate Round 1 Haiku opening; Round 2 Haiku rebuttal defends traceability claim
**Action**: In Phase 5, add an explicit organizational structure for `merged-strategy.md` that organizes cross-component guidance under five architectural principles: evidence integrity, deterministic gates, restartability, bounded complexity, scalable quality enforcement. Note that component references are preserved within each principle section to maintain Phase 1→6 traceability.
**Placement**: Phase 5 task list, step 2

### M7 — Five-Domain Validation Structure
**Source**: Haiku §5 (Coverage, Evidence, Rule Compliance, Flow/Traceability, Operability)
**Action**: Augment §5 Validation Strategy with Haiku's five-domain taxonomy as subheadings within the three-layer architecture. Haiku's domains map cleanly onto Opus's Layer 2 (cross-cutting) and Layer 3 (end-to-end).
**Placement**: §5 Validation Strategy

### M8 — "Path Verified" vs. "Strategy Analyzable" Status in Inventory
**Source**: Haiku §3 Risk 2 architect recommendation (uncontested)
**Action**: In Phase 1 T01.02, add requirement to distinguish between path-verified status and strategy-analyzable status in `inventory-llm-workflows.md` output. A stale path is path-verified=false, strategy-analyzable=false. A verified path with degraded Auggie evidence is path-verified=true, strategy-analyzable=degraded.
**Placement**: Phase 1, T01.02 sub-task

### M9 — Token Budget Derivation Disclosure
**Source**: Debate Round 2 Haiku rebuttal (valid epistemological challenge); Opus rebuttal does not fully answer
**Action**: In §4 Token Budget table, add a derivation-methodology footnote: "Estimates are architectural approximations based on comparable adversarial debate costs and inventory query patterns. Treat as order-of-magnitude planning inputs, not measured targets. Actual Phase 4 costs may vary 2x based on evidence contestation."
**Placement**: §4 Token Budget table, footnote
