# Base Selection: Adversarial Scoring

## Quantitative Scoring (50% weight)

| Metric | Weight | V1 (opus:architect) | V2 (haiku:architect) |
|--------|--------|---------------------|----------------------|
| Requirement Coverage (RC) | 0.30 | 0.95 | 0.88 |
| Internal Consistency (IC) | 0.25 | 0.92 | 0.95 |
| Specificity Ratio (SR) | 0.15 | 0.78 | 0.65 |
| Dependency Completeness (DC) | 0.15 | 0.98 | 0.92 |
| Section Coverage (SC) | 0.15 | 1.00 | 0.75 |
| **Quant Score** | | **0.929** | **0.851** |

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| Criterion | V1 Verdict | V1 Evidence | V2 Verdict | V2 Evidence |
|-----------|-----------|------------|-----------|------------|
| Covers all explicit requirements from source | MET | All 10 FRs covered with specific deliverables | MET | All FRs addressed, but at higher abstraction in M4 |
| Addresses edge cases and failure scenarios | MET | D3.1a enumerates 9 input domains including degenerate | MET | M2 FMEA pass addresses edge cases |
| Includes dependencies and prerequisites | MET | All D#.#a have corresponding D#.#b; milestone deps explicit | MET | Dependency notes in each milestone |
| Defines success/completion criteria | MET | Success Criteria table with 5 SC entries | MET | Exit gates per milestone in summary table |
| Specifies what is explicitly out of scope | NOT MET | No out-of-scope section | NOT MET | No out-of-scope section |

V1 Completeness: 4/5 | V2 Completeness: 4/5

### Correctness (5 criteria)

| Criterion | V1 Verdict | V2 Verdict |
|-----------|-----------|-----------|
| No factual errors or hallucinated claims | MET | MET |
| Technical approaches are feasible with stated constraints | MET | MET |
| Terminology used consistently | MET | MET |
| No internal contradictions | MET | MET |
| Claims supported by evidence | MET | MET |

V1 Correctness: 5/5 | V2 Correctness: 5/5

### Structure (5 criteria)

| Criterion | V1 Verdict | V1 Evidence | V2 Verdict | V2 Evidence |
|-----------|-----------|------------|-----------|------------|
| Logical section ordering | MET | M1→M2→M3→M4 with explicit dependency rationale | MET | Same ordering; dependency notes present |
| Consistent hierarchy depth | MET | H2 milestones, H3 subsections throughout | MET | Same |
| Clear separation of concerns | MET | Each milestone has single proposal focus | MET | M2 bundles P1+P2 (intentional; rationale given) |
| Navigation aids present | MET | Milestone Summary table + Dependency Graph + Risk Register | MET | Same sections present |
| Follows artifact type conventions | MET | Roadmap template followed; all required sections present | NOT MET | Missing Pipeline Execution Order section |

V1 Structure: 5/5 | V2 Structure: 4/5

### Clarity (5 criteria)

| Criterion | V1 Verdict | V1 Evidence | V2 Verdict | V2 Evidence |
|-----------|-----------|------------|-----------|------------|
| Unambiguous language | MET | Specific thresholds (cap at 5, 8 domains, 60% confidence, 6 milestones) | MET | Similar specificity at milestone level |
| Concrete rather than abstract | MET | Numbered test assertions in acceptance criteria (e.g., "3 behavioral deliverables → 6 output") | NOT MET | Acceptance criteria vaguer (e.g., "100% of behavioral deliverables appear as paired items" — testable but less detailed) |
| Each section has clear purpose | MET | Yes | MET | Yes |
| Acronyms defined on first use | MET | FMEA defined, kind values enumerated | MET | Terms defined |
| Actionable next steps clear | NOT MET | Pipeline section present but no "start here" instruction | MET | Exit gates per milestone + release gating philosophy are operational |

V1 Clarity: 4/5 | V2 Clarity: 4/5

### Risk Coverage (5 criteria)

| Criterion | V1 Verdict | V2 Verdict |
|-----------|-----------|-----------|
| Identifies ≥3 risks with probability and impact | MET (14 risks) | MET (7 risks) |
| Mitigation strategy for each risk | MET | MET |
| Addresses failure modes and recovery | MET | MET |
| Considers external dependencies | MET | MET |
| Monitoring/validation mechanism | NOT MET | MET (release gating = monitoring mechanism) |

V1 Risk Coverage: 4/5 | V2 Risk Coverage: 5/5

### Qualitative Summary

| Dimension | V1 Score | V2 Score |
|-----------|----------|----------|
| Completeness | 4/5 | 4/5 |
| Correctness | 5/5 | 5/5 |
| Structure | 5/5 | 4/5 |
| Clarity | 4/5 | 4/5 |
| Risk Coverage | 4/5 | 5/5 |
| **Total** | **22/25 = 0.880** | **22/25 = 0.880** |

Note: Tie on qualitative score. Position bias check: Pass 1 (V1→V2) and Pass 2 (V2→V1) both yield 22/22. Tie confirmed.

## Combined Scoring

| Variant | Quant (50%) | Qual (50%) | Combined Score |
|---------|------------|-----------|----------------|
| V1 (opus:architect) | 0.929 × 0.50 = 0.465 | 0.880 × 0.50 = 0.440 | **0.905** |
| V2 (haiku:architect) | 0.851 × 0.50 = 0.426 | 0.880 × 0.50 = 0.440 | **0.866** |

Margin: 4.5% — within 5% tiebreaker threshold. Applying tiebreaker Level 1.

**Tiebreaker Level 1 (Debate performance)**: V1 won 11/18 diff points outright; V2 won 4/18; 3/18 merged. V1 wins tiebreaker.

## Selected Base: Variant 1 (opus:architect)

**Selection rationale**: Higher quantitative score (0.929 vs 0.851) driven by more specific acceptance criteria, higher section coverage, and better dependency completeness. Qualitative scores tied at 22/25. V1 wins debate performance tiebreaker.

**Strengths to preserve from V1**:
- .a/.b deliverable scheme applied internally (self-consistency)
- Constrained invariant predicate grammar with validation
- Dual FMEA detection signal (independent of M2 completeness)
- Pipeline Execution Order section with ASCII diagram
- Detailed integration tests with specific numeric assertions

**Strengths to incorporate from V2**:
- **Release gating philosophy** (U-003) — block downstream expansion on unresolved high-severity findings; mandatory owner assignment
- **M2 grouping = P1+P2** (V2's grouping — adopted by V1 in Round 3)
- **M4 pilot deliverable** (D4.4) — go/no-go decision before general enablement
- **Release gate warning** for unresolved guard ambiguity with mandatory owner (M3)
