# Base Selection Report: Unified Audit Gating System v1.2.1

**Pipeline**: Adversarial 3-variant comparison
**Timestamp**: 2026-03-03T00:00:00Z
**Scoring method**: Hybrid quantitative (50%) + qualitative (50%)
**Position-bias mitigation**: Variants scored in randomized order per dimension

---

## Quantitative Scoring (50% weight)

### Requirement Coverage (RC, weight 0.30)

Assessed against the spec's 34 functional requirements and 10 non-functional requirements.

| Variant | Approach | Estimated Coverage | RC Score |
|---------|----------|-------------------|----------|
| V1 (Architect) | Explicit per-deliverable mapping to FR/NFR IDs. Nearly all 34 FRs and 10 NFRs traceable to specific deliverables. Missing: some rollout-specific FRs are at high abstraction. | ~85% | 0.85 |
| V2 (QA) | Requirements referenced in acceptance gates and success criteria. Coverage is high but mapping is at test-level rather than deliverable-level. Some FRs covered implicitly through test assertions rather than explicit mapping. | ~80% | 0.80 |
| V3 (Analyzer) | Requirements covered conceptually at the reliability/risk level. No explicit FR/NFR ID references. Coverage is at the highest abstraction level. | ~75% | 0.75 |

### Internal Consistency (IC, weight 0.25)

Measured as absence of internal contradictions.

| Variant | Issues Found | IC Score |
|---------|-------------|----------|
| V1 (Architect) | Minor: Blocker closure deferred to M6 but contracts-first ethos implies governance should precede implementation. M1 defines schemas with no finalized values, then M2-M5 test against undefined thresholds. | 0.90 |
| V2 (QA) | No internal contradictions found. All blockers close in M1; all downstream milestones reference M1 decisions; dependency chain is consistent throughout. | 0.95 |
| V3 (Analyzer) | No internal contradictions found. Risk-first ordering is consistent: governance (M1) before contracts (M2) before reliability (M3) before rollout (M4-M6). | 0.95 |

### Specificity Ratio (SR, weight 0.15)

Concrete, testable statements vs. abstract statements.

| Variant | Assessment | SR Score |
|---------|-----------|----------|
| V1 (Architect) | Strong field-level schema definitions, specific test file names, exact field counts. Some acceptance criteria are at the "verify X works" level. | 0.80 |
| V2 (QA) | Highest specificity. Exact test counts (17 legal, 6 illegal, 9 determinism, 11+ field-absence). Numbered deliverables with testable acceptance criteria. Specific field names in every override test. | 0.90 |
| V3 (Analyzer) | Most abstract. Acceptance criteria use phrases like "meets pass threshold", "deterministic timing tests", "pass rate meets release threshold" without specifying numbers. | 0.70 |

### Dependency Completeness (DC, weight 0.15)

Internal references resolved correctly.

| Variant | Assessment | DC Score |
|---------|-----------|----------|
| V1 (Architect) | All milestone dependencies explicitly stated. M3 depends on M1+M2, M4 depends on M1+M2+M3. Clear. | 0.90 |
| V2 (QA) | All dependencies explicitly stated with specific deliverable IDs (e.g., "M1-D2 retry values needed for M4-D1"). Most precise. | 0.90 |
| V3 (Analyzer) | Dependencies stated at milestone level only (e.g., "M2 depends on M1"). Less granular but internally consistent. | 0.85 |

### Section Coverage (SC, weight 0.15)

Presence of all required roadmap sections.

| Variant | Assessment | SC Score |
|---------|-----------|----------|
| V1 (Architect) | All sections present: Overview, Milestone Summary, Dependency Graph, 6x (Objective, Deliverables, Dependencies, Risk Assessment), Risk Register, Decision Summary, Success Criteria | 1.0 |
| V2 (QA) | All sections present (same set) | 1.0 |
| V3 (Analyzer) | All sections present (same set) | 1.0 |

### Quantitative Composite

| Variant | RC (0.30) | IC (0.25) | SR (0.15) | DC (0.15) | SC (0.15) | **Weighted Total** |
|---------|-----------|-----------|-----------|-----------|-----------|-------------------|
| V1 (Architect) | 0.255 | 0.225 | 0.120 | 0.135 | 0.150 | **0.885** |
| V2 (QA) | 0.240 | 0.2375 | 0.135 | 0.135 | 0.150 | **0.8975** |
| V3 (Analyzer) | 0.225 | 0.2375 | 0.105 | 0.1275 | 0.150 | **0.845** |

---

## Qualitative Scoring (50% weight)

### 25-Criterion Binary Rubric (5 dimensions x 5 criteria)

#### Completeness (5 criteria)

| # | Criterion | V1 | V2 | V3 |
|---|-----------|:--:|:--:|:--:|
| 1 | All 6 milestones present with distinct objectives | 1 | 1 | 1 |
| 2 | All 4 data contracts addressed (GateResult, OverrideRecord, GateTransitionEvent, GateCheckEvent) | 1 | 1 | 1 |
| 3 | Three-phase rollout (shadow/soft/full) fully specified | 1 | 1 | 1 |
| 4 | Override governance with release-scope prohibition | 1 | 1 | 1 |
| 5 | All 4 GO blockers addressed with resolution mechanism | 1 | 1 | 1 |
| | **Subtotal** | **5** | **5** | **5** |

#### Correctness (5 criteria)

| # | Criterion | V1 | V2 | V3 |
|---|-----------|:--:|:--:|:--:|
| 6 | State machine transitions match spec section 4.1/4.2 | 1 | 1 | 1 |
| 7 | Illegal transitions explicitly enumerated (minimum 6 classes) | 1 | 1 | 1 |
| 8 | Fail-safe default to unknown/failed correctly specified | 1 | 1 | 1 |
| 9 | Blocker resolution precedes implementation work | 0 | 1 | 1 |
| 10 | KPI promotion gates match spec section 7.2 criteria | 1 | 1 | 1 |
| | **Subtotal** | **4** | **5** | **5** |

Note on criterion 9: V1 defers blocker closure to M6. This violates the spec's intent that NO-GO blockers be resolved before implementation proceeds.

#### Clarity (5 criteria)

| # | Criterion | V1 | V2 | V3 |
|---|-----------|:--:|:--:|:--:|
| 11 | Acceptance criteria are testable (not vague) | 1 | 1 | 0 |
| 12 | Deliverable descriptions specify concrete artifacts | 1 | 1 | 1 |
| 13 | Risk mitigations are actionable (not "be careful") | 1 | 1 | 1 |
| 14 | Test file names and test counts specified | 1 | 1 | 0 |
| 15 | Decisions include rationale connecting to risk | 1 | 1 | 1 |
| | **Subtotal** | **5** | **5** | **3** |

Note on criteria 11, 14: V3 uses abstract acceptance criteria ("meets pass threshold") and does not specify test file names or counts.

#### Structure (5 criteria)

| # | Criterion | V1 | V2 | V3 |
|---|-----------|:--:|:--:|:--:|
| 16 | Clear dependency graph with no cycles | 1 | 1 | 1 |
| 17 | Deliverable IDs follow consistent scheme | 1 | 1 | 1 |
| 18 | Risk IDs follow consistent scheme | 1 | 1 | 1 |
| 19 | Each milestone has all 4 required subsections | 1 | 1 | 1 |
| 20 | Effort estimates present for milestones | 1 | 1 | 1 |
| | **Subtotal** | **5** | **5** | **5** |

#### Risk Coverage (5 criteria)

| # | Criterion | V1 | V2 | V3 |
|---|-----------|:--:|:--:|:--:|
| 21 | State machine deadlock/bypass risk identified | 1 | 1 | 1 |
| 22 | Rollback from full enforcement addressed | 1 | 1 | 1 |
| 23 | Sprint CLI regression risk addressed | 0 | 1 | 0 |
| 24 | Override governance race conditions addressed | 0 | 1 | 0 |
| 25 | Heartbeat/timing test flakiness addressed | 1 | 1 | 1 |
| | **Subtotal** | **3** | **5** | **3** |

Note on criterion 23: Only V2 has a dedicated Sprint CLI regression gate. V1 mentions it in passing; V3 does not address it.
Note on criterion 24: Only V2 identifies concurrent override race condition risk (R9 in risk register).

### Qualitative Composite

| Variant | Completeness | Correctness | Clarity | Structure | Risk Coverage | **Total /25** | **Normalized** |
|---------|:------------:|:-----------:|:-------:|:---------:|:------------:|:-------------:|:--------------:|
| V1 (Architect) | 5 | 4 | 5 | 5 | 3 | **22** | **0.88** |
| V2 (QA) | 5 | 5 | 5 | 5 | 5 | **25** | **1.00** |
| V3 (Analyzer) | 5 | 5 | 3 | 5 | 3 | **21** | **0.84** |

Note: V2 achieves a perfect qualitative score. V1 loses points on blocker timing (correctness) and risk coverage (sprint CLI, override race). V3 loses points on clarity (abstract criteria) and risk coverage (same gaps as V1).

---

## Combined Scoring

**Formula**: combined = (0.50 x quantitative) + (0.50 x qualitative)

| Variant | Quantitative (50%) | Qualitative (50%) | **Combined Score** |
|---------|:-------------------:|:------------------:|:------------------:|
| V1 (Architect) | 0.4425 | 0.4400 | **0.8825** |
| **V2 (QA)** | **0.4488** | **0.5000** | **0.9488** |
| V3 (Analyzer) | 0.4225 | 0.4200 | **0.8425** |

---

## Base Selection Decision

### Selected Base: V2 (sonnet:qa)

**Combined score**: 0.9488
**Margin over V1 (Architect)**: 0.0663 (6.6 percentage points, exceeds 5% tiebreaker threshold)
**Margin over V3 (Analyzer)**: 0.1063 (10.6 percentage points)

**No tiebreaker required.** V2 wins by clear margin on both qualitative (perfect 25/25) and quantitative (highest weighted total) dimensions.

### Rationale

1. **Correctness**: V2 is the only variant that correctly places blocker resolution before implementation (criterion 9), matching the spec's intent that NO-GO criteria be resolved first.

2. **Risk coverage**: V2 is the only variant that addresses sprint CLI regression as a standalone gate (criterion 23) and identifies the concurrent override race condition (criterion 24). These are real risks that V1 and V3 miss entirely.

3. **Specificity**: V2 has the highest specificity ratio (0.90) with explicit test counts, numbered field-absence tests, and concrete acceptance criteria. This makes the roadmap auditable -- you can count whether the deliverables are complete.

4. **Internal consistency**: V2 has no internal contradictions (IC=0.95 tied with V3, vs V1's 0.90). The blocker-first ordering is consistent with the testing-interleaved philosophy.

5. **Sprint CLI regression gate**: V2's M5 is a unique and high-value contribution that addresses the shared-file regression risk (`models.py`, `tui.py`) that the other variants either underweight (V1) or ignore (V3).

### What V2 Lacks (to be incorporated from V1/V3)

- **U-001** (V1): Closed-world state machine enforcement -- add to M2
- **U-002** (V1): Compile-time release override prohibition -- add to M2
- **U-005** (V3): Fault-injection suite and deadlock-resistance formal argument -- add to M4
- **U-006** (V3): Rollout sub-phase granularity with explicit ordering -- restructure M6
