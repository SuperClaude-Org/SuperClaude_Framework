# Diff Analysis: sc:adversarial v2.0 Roadmap Comparison

## Metadata

- Generated: 2026-03-04
- Variants compared: 2
- Variant 1: opus:architect
- Variant 2: haiku:architect

---

## Structural Differences

| # | Area | Variant 1 (opus) | Variant 2 (haiku) | Severity |
|---|------|-----------------|-------------------|----------|
| S-001 | M4 dependency | M4 depends only on M1 (Devil's Advocate Agent); M3 is not a prerequisite for invariant declaration | M4 depends on M3 (Concrete Scenario Traces); invariant declaration cannot begin until scenario traces are completed | Critical |
| S-002 | M5 dependency | M5 depends on M1 AND M4; failure mode enumeration is gated by both the DA agent and the invariants it challenges | M5 depends on M1 AND M3; failure mode enumeration is gated by the DA agent and scenario traces, not by invariants | Critical |
| S-003 | M6 dependency | M6 depends only on M3; post-merge trace validation requires only the concrete scenario traces as input | M6 depends on M2 + M3 + M4 + M5 (all four preceding milestones); M6 is a full convergence point for all prior work | High |
| S-004 | Critical path topology | Critical path: M1 → M2 → M3 → M6; M4 and M5 run on a parallel branch that does not feed M6 | Critical path: M1 → M2 → M3 → M4 → M6 with M5 also required for M6; no parallel branch isolated from M6 | High |
| S-005 | M4/M5 ordering relationship | M5 is positioned after M4; invariants are declared and challenged first, then failure modes are enumerated using those invariants as input | M5 is positioned before M4 in terms of dependency; M5 (FME) depends on M3 not M4, meaning FME can run concurrently with or before invariant challenge | High |
| S-006 | Deliverable count per milestone | M3 has 3 deliverables (D3.1–D3.3); M6 has 3 deliverables (D6.1–D6.3); all other milestones have 3 deliverables | M3 has 4 deliverables (D3.1–D3.4); M6 has 4 deliverables (D6.1–D6.4); resulting in 2 additional deliverables total | Medium |
| S-007 | Parallelization opportunity | Explicit annotation: M4 is parallelizable after M1; M5 is parallelizable after M4; parallel work does not gate M6 | No explicit parallelization annotation; dependency graph implies M3 → M4 and M3 → M5 can overlap but both must complete before M6 | Low |
| S-008 | Risk register size | 7 risks (R1–R7) | 6 risks (R1–R6) | Low |

---

## Content Differences

| # | Topic | Variant 1 Approach | Variant 2 Approach | Severity |
|---|-------|-------------------|--------------------|----------|
| C-001 | DA agent lifecycle | Explicitly designed as stateless across debates but persistent within a single run; the stateless-across-debates property is a named design decision affecting memory and isolation guarantees | DA agent lifecycle not explicitly described; no equivalent design decision is documented for cross-debate memory or within-run persistence | High |
| C-002 | FME sequencing relative to invariant challenge | FME (M5) is sequenced after invariant declaration and challenge (M4); the rationale is that invariants inform failure mode enumeration — invariants serve as input to FME scope definition | FME (M5) is sequenced before or concurrent with invariant challenge (M4) because M5 depends on M3 not M4; FME proceeds from scenario traces directly, independent of declared invariants | Critical |
| C-003 | M6 scope and deliverables | M6 has 3 deliverables covering post-merge trace validation outcomes; provenance tracking is not an explicit deliverable | M6 has 4 deliverables including D6.4 (provenance tagging); provenance tagging is elevated to a first-class deliverable, enabling trace attribution back to originating milestone | High |
| C-004 | Success criteria style | 8 success criteria (SC1–SC8) with quantitative targets: token budget increase ≤40%, convergence rate ≥80%, mean invariant declaration rate ≥0.1 per session; targets are measurable and bounded | 8 success criteria (S1–S8) framed operationally and in binary or qualitative terms; fewer hard numeric thresholds; criteria describe behavioral outcomes rather than measured rates | High |
| C-005 | Overview / framing architecture | No named framing construct; integration described as layered additions to existing pipeline stages | Describes a "three control planes" framework as the conceptual organizing structure for the v2.0 additions; control planes provide a mental model for separation of concerns across the six milestones | Medium |
| C-006 | M4 dependency rationale | M4 positioned as independently executable after only M1; rationale is that invariant declaration is a capability of the DA agent and does not require scenario trace data to begin | M4 positioned as dependent on M3; rationale is that invariants should be grounded in concrete scenario evidence before they are declared and challenged | Critical |
| C-007 | DA blocker severity taxonomy | No explicit severity taxonomy for DA blocker classifications documented in the structural summary | Defines a severity taxonomy for DA blockers with a "critical-only default" setting; blockers below critical severity are suppressed by default to reduce noise | Medium |
| C-008 | Adoption friction framing | Adoption friction not surfaced as a named risk category; risk register focuses on technical and process risks | R6 explicitly addresses adoption friction arising from scoring system changes; this is a named organizational/process risk absent from Variant 1 | Medium |

---

## Contradictions

| # | Point of Conflict | Variant 1 Position | Variant 2 Position | Impact |
|---|------------------|-------------------|--------------------|--------|
| X-001 | M4 prerequisite dependency | M4 requires only M1; invariant declaration can begin as soon as the DA agent is operational, without waiting for scenario trace rounds | M4 requires M3; invariant declaration cannot begin until concrete scenario traces have been produced, as traces are needed to ground the invariants | Critical — directly determines whether M4 runs in parallel with M3 or sequentially after it; affects total schedule duration and whether invariants are evidence-grounded |
| X-002 | M5 prerequisite dependency | M5 requires M1 and M4; the invariants declared and challenged in M4 are inputs to the failure mode enumeration scope in M5 | M5 requires M1 and M3; failure mode enumeration is driven by scenario traces from M3, not by invariants from M4; M4 is not a gate for FME | Critical — determines whether FME is informed by invariants (Variant 1) or by raw scenario traces (Variant 2); this is a fundamental disagreement about what data should drive failure mode selection |
| X-003 | M6 prerequisite dependencies | M6 requires only M3; post-merge trace validation is scoped to verifying concrete scenario traces survive a merge, making M3 the only required input | M6 requires M2 + M3 + M4 + M5; post-merge trace validation is a comprehensive integration checkpoint that verifies outputs from all four preceding milestones | High — determines whether M4 and M5 outputs are ever formally validated in the pipeline; in Variant 1 they are not gated through M6, raising the question of how their correctness is verified |
| X-004 | FME ordering relative to invariant challenge | FME comes after invariant challenge; the logical sequence is: declare invariants → challenge them → enumerate failure modes using invariants as a filter | FME comes before or concurrent with invariant challenge (M5 depends on M3, M4 depends on M3, neither depends on the other); FME and invariant challenge are independent parallel workstreams after M3 | High — these are mutually exclusive sequencing choices; both cannot be simultaneously correct for a single implementation |
| X-005 | M6 risk level | M6 is assessed at Low risk | M6 is assessed at Medium-High risk | Medium — diverging risk assessments for the same milestone indicate disagreement about the complexity or failure probability of post-merge trace validation, likely driven by Variant 2's broader M6 scope (4 deliverables vs 3) |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | Variant 1 (opus) | R7: Interface stability risk — explicitly identifies phasing complexity and interface stability as a named risk in the register | High value: interface instability between milestones is a real integration hazard in a 6-milestone pipeline; naming it forces mitigation planning |
| U-002 | Variant 1 (opus) | DA agent stateless-across-debates lifecycle design decision — explicitly specifies that the DA agent does not carry memory between separate debate invocations but maintains state within a single run | High value: this is a non-obvious design choice with significant implications for reproducibility, auditability, and isolation of debate outcomes |
| U-003 | Variant 1 (opus) | Quantitative success criteria targets: token budget increase ≤40%, convergence rate ≥80%, mean invariant declaration rate ≥0.1 per session (SC1–SC8) | High value: quantitative thresholds make success criteria verifiable and support automated gate enforcement; binary/qualitative criteria are harder to enforce consistently |
| U-004 | Variant 1 (opus) | M4/M5 dependency design: invariants inform FME — the explicit rationale that invariants from M4 serve as scoping input for failure mode enumeration in M5 | High value: provides a principled basis for FME prioritization; without invariant grounding, FME scope is arbitrary or driven only by trace coverage |
| U-005 | Variant 1 (opus) | `--override-coverage` escape hatch — an explicit mechanism allowing operators to bypass the state coverage gate under defined conditions | Medium value: escape hatches are operationally necessary but carry risk; naming it explicitly ensures it is intentionally designed rather than informally used |
| U-006 | Variant 2 (haiku) | Three control planes framework — a named conceptual organizing structure for the v2.0 additions that separates concerns across milestones into distinct planes | High value: the control planes model provides a communication and reasoning scaffold; it aids onboarding, architectural review, and future extension decisions |
| U-007 | Variant 2 (haiku) | D3.4: Divergence detector as an explicit deliverable in M3 — the divergence detection capability is elevated from an implicit trace analysis behavior to a named, shippable artifact | High value: making divergence detection an explicit deliverable creates accountability for its implementation quality and makes it testable independently |
| U-008 | Variant 2 (haiku) | D6.4: Provenance tagging as a deliverable in M6 — post-merge trace validation produces provenance tags that attribute each validated trace back to its originating milestone | High value: provenance tagging enables root-cause analysis when post-merge failures occur and supports audit trails for the adversarial process |
| U-009 | Variant 2 (haiku) | Severity taxonomy for DA blockers with critical-only default — an explicit classification scheme that suppresses non-critical DA blockers by default to reduce operational noise | Medium value: reduces alert fatigue in high-frequency adversarial runs; however, the suppression default carries risk of hiding legitimate lower-severity issues |
| U-010 | Variant 2 (haiku) | R6: Adoption friction from scoring changes — names organizational resistance to scoring system modifications as an explicit risk | Medium value: adoption friction is a real delivery risk in team contexts; its absence from Variant 1 is a gap, as technical correctness alone does not ensure uptake |
| U-011 | Variant 2 (haiku) | S8: Operational sustainability success criterion — includes a criterion specifically addressing whether the v2.0 additions are sustainable to operate over time | Medium value: sustainability is often omitted from success criteria focused on feature correctness; including it surfaces operational burden as a first-class concern |

---

## Summary

- Total structural differences: **8** (S-001 through S-008)
- Total content differences: **8** (C-001 through C-008)
- Total contradictions: **5** (X-001 through X-005)
- Total unique contributions: **11** (U-001 through U-011)

**Highest-severity items:**

| ID | Type | Description |
|----|------|-------------|
| X-001 | Contradiction | M4 prerequisite: M1-only vs M3-required — mutually exclusive dependency; determines parallelization opportunity and whether invariants are evidence-grounded |
| X-002 | Contradiction | M5 prerequisite: M4-gated vs M3-gated — determines whether FME is informed by invariants or raw traces; fundamental disagreement about FME input data |
| X-003 | Contradiction | M6 prerequisite: M3-only vs all-four — determines whether M4 and M5 outputs receive formal validation in the pipeline |
| X-004 | Contradiction | FME ordering relative to invariant challenge — mutually exclusive sequencing; both cannot be correct in a single implementation |
| S-001 | Structural | M4 dependency topology — direct source of X-001; shapes the entire right half of the milestone graph |
| S-002 | Structural | M5 dependency topology — direct source of X-002; determines FME's relationship to the invariant challenge milestone |
| C-002 | Content | FME sequencing rationale — the content-level articulation of X-004; the two variants give opposite answers to what drives FME scope |
| C-006 | Content | M4 dependency rationale — the content-level articulation of X-001; both variants provide explicit but opposing rationales |
