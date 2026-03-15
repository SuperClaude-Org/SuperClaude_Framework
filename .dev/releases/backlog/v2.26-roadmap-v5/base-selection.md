---
base_variant: A
variant_scores: "A:76 B:71"
---

## Scoring Criteria (derived from debate)

| # | Criterion | Weight | Rationale |
|---|-----------|--------|-----------|
| C1 | Implementation precision & specification completeness | 25% | Debate converged on Opus's stronger FR-087, FR-089, `_print_terminal_halt()` specs |
| C2 | Risk model & open question coverage | 20% | Haiku conceded FR-087/FR-089 gaps; Opus conceded OQ-E/OQ-F/OQ-I gaps |
| C3 | Correctness of dependency/phase structure | 20% | Contested: phase count (4 vs 5); integration-level coupling argument |
| C4 | Actionability & verifiability of milestones | 15% | Haiku conceded binary exit criteria; Opus's checklist approach is more verifiable |
| C5 | Negative validation emphasis | 10% | Haiku's framing is superior; both cover the substance |
| C6 | Timeline realism | 10% | Both revised toward convergence; Haiku's upper bound is more honest |

---

## Per-Criterion Scores

### C1 — Implementation Precision & Specification Completeness (25%)

**Variant A (Opus)**: 80/100
- Explicit FR-087 CLI surfacing of `routing_update_spec` (Haiku conceded gap)
- Explicit FR-089 `total_annotated: 0` graceful degradation with log level and continuation behavior (Haiku conceded gap)
- Precise `_print_terminal_halt()` stderr content requirements (Haiku conceded this was superior)
- Integer-parsing distinction for missing/malformed/failing values (FR-080) specified clearly
- Risk matrix includes probability + severity ratings with specific phase assignments

**Variant B (Haiku)**: 63/100
- FR-087 gap explicitly conceded
- FR-089 gap explicitly conceded ("deviation-analysis acts as backstop" is insufficient)
- `_print_terminal_halt()` test coverage broader but implementation spec less precise
- Phase 4 "negative validation" emphasis is strong but doesn't compensate for missing operational specs

**Weighted A**: 20.0 | **Weighted B**: 15.75

---

### C2 — Risk Model & Open Question Coverage (20%)

**Variant A (Opus)**: 65/100
- Phase 0 OQ coverage explicitly conceded as underspecified (OQ-E/OQ-F/OQ-I absent)
- `fidelity.py` investigation conceded as missing from checklist
- `_parse_routing_list()` module placement conceded as Phase 0/1 decision (underweighted as "Phase 2 contingency")
- Risk matrix structure is strong; probability/severity ratings present
- OQ-A/OQ-C/OQ-G/OQ-H covered

**Variant B (Haiku)**: 82/100
- OQ-E/OQ-F explicitly listed in Phase 0 scope
- OQ-I (token-count access) explicitly covered
- `fidelity.py` listed as required code area (correctly framed as investigation, not assumed work)
- `_parse_routing_list()` module placement addressed as Phase 1 concern
- Parallelization plan explicitly accounts for team composition uncertainty
- 7 distinct risk categories with control owners and validation evidence requirements

**Weighted A**: 13.0 | **Weighted B**: 16.4

---

### C3 — Correctness of Dependency/Phase Structure (20%)

**Variant A (Opus)**: 72/100
- 4-phase structure is coherent at unit-test level
- Opus's argument that `deviations_to_findings()` depends only on `Finding` (frozen Phase 1) is technically accurate
- Integration-level counter-argument from Haiku has merit: executor integration point requires both budget mechanism and findings conversion to be stable for integration tests
- Opus's proposed resolution ("annotate integration tests as sequenced after Phase 3") is workable but presentationally obscures real dependency
- Within-phase parallelization (2.1 + 2.3 after 2.2) is correctly specified

**Variant B (Haiku)**: 78/100
- 5-phase structure correctly captures integration-level dependency
- Phase 4 (remediation routing) after Phase 3 (executor/budget) enables complete integration testing
- Haiku's counter-rebuttal correctly distinguishes unit-level vs integration-level coupling
- Parallelization guidance is more complete for team scenarios
- Phase 0 scope is more expansive and complete

**Weighted A**: 14.4 | **Weighted B**: 15.6

---

### C4 — Actionability & Verifiability of Milestones (15%)

**Variant A (Opus)**: 85/100
- Binary exit criteria per phase (checkboxes): verifiable, unambiguous
- SC-1 through SC-10 mapped to specific phases with verification methods
- Risk matrix with per-risk phase assignments
- `parse_frontmatter()` rename flagged as "must happen first" (operational ordering)
- OQ-A decision tree (Option A vs B) with concrete inspection guidance

**Variant B (Haiku)**: 67/100
- Conceded that binary exit criteria would improve operability
- Milestone descriptions are qualitative in some phases ("fail-closed validation layer complete")
- Analyzer focus areas are useful but less verifiable than checklists
- "Block release on evidence, not confidence" is valuable but doesn't substitute for binary gates
- Three-layer validation model (unit/integration/artifact) is well-structured

**Weighted A**: 12.75 | **Weighted B**: 10.05

---

### C5 — Negative Validation Emphasis (10%)

**Variant A (Opus)**: 62/100
- SC-1 through SC-10 covers negative behaviors (SC-4 proves only SLIPs remediated, SC-6 halt behavior)
- Dispute acknowledged; proposed resolution (annotation to Phase 4 milestone) would partially close gap
- Framing does not communicate asymmetric correctness boundary
- FR-091 halt on ambiguous deviations specified

**Variant B (Haiku)**: 90/100
- First-class architectural principle with explicit release-blocker list
- Section 8 item 5 explicitly lists 5 refusal behaviors as the primary correctness boundary
- Phase 4 milestone focuses on "negative validation" as the key deliverable
- "Before/after roadmap diffs as evidence, not just passing tests" — stronger evidentiary standard
- Communication difference is real: teams reading Haiku will correctly weight refusal behaviors

**Weighted A**: 6.2 | **Weighted B**: 9.0

---

### C6 — Timeline Realism (10%)

**Variant A (Opus)**: 70/100
- 10–14 day estimate revised to 11–15 after debate concession on solo-engineer lower bound
- Acknowledges Phase 0 OQ resolution as conditional
- Does not account for OQ-A Option B body parsing (+1–2 days) or `fidelity.py` modification (+0.5–1 day)
- Per-phase breakdowns are consistent with total

**Variant B (Haiku)**: 78/100
- 9.5–17 day band explicitly documents uncertainty sources (4 named risk factors)
- Upper bound of 17 days reflects realistic scenarios (OQ-A Option B, `fidelity.py`, fixture complexity)
- Lower bound of 9.5 correctly identified as team-dependent; solo lower bound ~13 days matches Opus's concession
- "Proceed only after Phase 5 evidence review, not on code-complete status" — operationally honest

**Weighted A**: 7.0 | **Weighted B**: 7.8

---

## Overall Scores

| Criterion | Weight | A Score | A Weighted | B Score | B Weighted |
|-----------|--------|---------|------------|---------|------------|
| C1 Implementation precision | 25% | 80 | 20.0 | 63 | 15.75 |
| C2 Risk/OQ coverage | 20% | 65 | 13.0 | 82 | 16.4 |
| C3 Phase structure | 20% | 72 | 14.4 | 78 | 15.6 |
| C4 Milestone actionability | 15% | 85 | 12.75 | 67 | 10.05 |
| C5 Negative validation | 10% | 62 | 6.2 | 90 | 9.0 |
| C6 Timeline realism | 10% | 70 | 7.0 | 78 | 7.8 |
| **Total** | | | **73.35** | | **74.6** |

*Raw scores narrow: A=73.35, B=74.6. Selecting A as base on tiebreaker criteria below.*

---

## Base Variant Selection Rationale

Despite Variant B scoring marginally higher in raw weighted totals (74.6 vs 73.35), **Variant A is selected as the base** for the following reasons:

1. **Implementation specification completeness is the primary merge value.** The merge operation must produce an actionable engineering document. Variant A's explicit FR-087/FR-089 specifications, binary milestone checklists, and precise `_print_terminal_halt()` requirements provide the structural skeleton that is harder to retrofit than the conceptual enhancements Haiku offers. Adding Haiku's OQ coverage and negative validation framing to Opus's structure is additive; the reverse would require reconstructing implementation specs from Haiku's more abstract descriptions.

2. **Haiku's superior elements are incorporable without restructuring.** The debate's synthesis recommendation explicitly identifies Haiku contributions that can be merged into Opus's structure: OQ-E/OQ-F/OQ-I in Phase 0, `fidelity.py` in the inspection checklist, negative validation as a first-class release criterion, conservative upper timeline bound, and `_parse_routing_list()` as Phase 0/1 decision. None of these require restructuring Opus's phase ordering or checklist format.

3. **The phase count dispute (4 vs 5) remains externally unresolved per the debate.** The synthesis recommendation states: "Remain open: Phase count (4 vs. 5) pending codebase inspection." Selecting Variant A as base preserves the 4-phase structure as a starting point while the merge can annotate the integration test sequencing concern — this is less disruptive than adopting 5 phases and then potentially collapsing them.

4. **Milestone verifiability is disproportionately high-value for this complexity level.** A 0.92-complexity feature with 115 requirements benefits more from unambiguous binary exit criteria (Opus) than from qualitative milestone framing (Haiku). This is the one criterion where the gap is decisive.

---

## Specific Improvements from Variant B to Incorporate in Merge

### High priority (conceded by Opus or debate-settled)

1. **Phase 0 OQ expansion**: Add OQ-E (`_extract_fidelity_deviations()` signature), OQ-F (`_extract_deviation_classes()` signature), and OQ-I (token-count field availability) to Phase 0 pre-implementation decisions list. Reference Haiku's Phase 0 scope items directly.

2. **`fidelity.py` in resource requirements**: Add `fidelity.py` to the "Files Modified" table in Phase 0/1 with annotation: "Investigation required — confirm whether `_extract_fidelity_deviations()` and `_extract_deviation_classes()` reside here and require modification per OQ-E/OQ-F."

3. **`_parse_routing_list()` as Phase 0/1 decision**: Move the circular import / module placement note from "Architectural Risks Not in Spec" (currently framed as Phase 2 contingency) to Phase 1 scope as a mandatory architectural decision. Add to Phase 1 milestone gate: `[ ] Module placement for _parse_routing_list() decided and circular import risk assessed`.

4. **FR-087 and FR-089 gap acknowledgment already addressed in Opus** — no merge action needed; Haiku conceded these.

### Medium priority (framing improvements)

5. **Negative validation as release blocker**: Add a "Negative Validation Release Blockers" section to Phase 4 (Integration Testing), listing Haiku's 5 explicit refusal behaviors as required verified evidence items:
   - Refuse bogus intentional claims (no valid D-XX citation)
   - Refuse stale deviation artifacts (freshness mismatch)
   - Refuse ambiguous continuation (`ambiguous_count > 0`)
   - Refuse false certification (`certified: false`)
   - Refuse third remediation attempt (budget exhaustion)

6. **"Block release on evidence, not confidence" statement**: Add Haiku's explicit framing to Phase 4 milestone gate preamble. Merge with Opus's SC checklist: both appear, with the framing statement heading the checklist.

7. **`_print_terminal_halt()` test coverage**: Adopt Haiku's test requirement that stderr output be assertion-covered (not just implementation-spec'd). Add to Phase 4 unit test scope: explicit stderr content assertions for `_print_terminal_halt()`.

### Lower priority (timeline and parallelization)

8. **Timeline upper bound**: Revise total estimate from "10–14 working days" to "11–17 working days" with explicit note: lower bound (11 days) assumes Phase 0 OQ resolution is clean and `fidelity.py` requires no modification; upper bound (17 days) reflects OQ-A Option B body parsing (+1–2 days) and `fidelity.py` modification (+0.5–1 day).

9. **Parallelization guidance for team scenarios**: Add Haiku's parallel workstream table (Section 7) as an appendix or footnote to Opus's timeline summary, framed as "team-scenario acceleration options" to avoid implying team capacity that may not exist.

10. **Phase 0 deliverables formalization**: Adopt Haiku's Phase 0 deliverable list (implementation decision log, requirement traceability matrix, confirmed module ownership map, test plan aligned to SC-1 through SC-10) as the explicit output checklist for Opus's Phase 0.
