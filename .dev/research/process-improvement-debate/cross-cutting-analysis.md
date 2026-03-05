# Cross-Cutting Analysis: Proposal Interactions Across Commands

**Date**: 2026-03-04
**Scope**: Analysis of synergies, conflicts, redundancies, and dependencies across all 15 proposals from 3 commands (spec-panel, adversarial, roadmap)

---

## 1. Thematic Clusters

Three clusters of proposals address the same underlying problem from different pipeline stages.

### Cluster A: "Force Invariant Reasoning About State"

| Proposal | Command | Mechanism | Pipeline Stage |
|----------|---------|-----------|----------------|
| SP-1: Correctness Focus Pass | spec-panel | Expert lens shift | Spec review |
| SP-3: Guard Boundary Table | spec-panel | Mandatory artifact | Spec review |
| AD-1: Invariant Probe Round | adversarial | Fault-finder agent + checklist | Debate |
| RM-1: State Invariant Analysis Section | roadmap | Template section | Roadmap generation |
| RM-4: Invariant Boundary Agent | roadmap | Validation agent | Roadmap validation |

**Synergy**: These proposals form a pipeline of invariant reasoning. SP-1/SP-3 enumerate state variables and boundary conditions during spec review. AD-1 probes them during debate. RM-1 carries the inventory into the roadmap. RM-4 validates the design against boundaries. Each stage reinforces the prior stage's output.

**Redundancy risk**: If all five are implemented, there is potential for repeated enumeration of the same state variables at each stage. Mitigation: later stages should consume and verify prior stages' artifacts rather than re-deriving from scratch. RM-1's table should be initialized from SP-3's boundary table, and RM-4's agent should validate RM-1's entries rather than independently enumerating.

**Recommendation**: Implement as a chain where each stage adds verification, not re-enumeration.

### Cluster B: "Surface Hidden Assumptions and Shared Blind Spots"

| Proposal | Command | Mechanism | Pipeline Stage |
|----------|---------|-----------|----------------|
| AD-2: Consensus Assumption Extraction | adversarial | Shared assumption surfacing | Debate diff analysis |
| AD-5: Debate Topic Taxonomy | adversarial | Coverage guarantee for state mechanics | Debate round structure |
| SP-2: Adversarial Tester Persona | spec-panel | Destructive mindset | Spec review |

**Synergy**: AD-2 surfaces the assumptions. AD-5 guarantees they are debated. SP-2 provides the destructive mindset to challenge them. The three proposals form a complete chain: surface -> require debate -> attack.

**Redundancy risk**: Minimal. Each addresses a different aspect of the blind spot problem.

**Recommendation**: AD-2 and AD-5 are the minimum viable pair (as noted in the adversarial brainstorm). SP-2 amplifies the value of both by providing a dedicated attacker at the spec review stage.

### Cluster C: "Trace State Across Component Boundaries"

| Proposal | Command | Mechanism | Pipeline Stage |
|----------|---------|-----------|----------------|
| SP-4: Pipeline Dimensional Analysis | spec-panel | Quantity flow heuristic | Spec review |
| AD-4: Post-Merge Interaction Stress Test | adversarial | Merge interaction tracing | Debate merge |
| RM-3: Cross-Component State Flow Tracing | roadmap | Interaction boundary analysis | Roadmap extraction |

**Synergy**: All three target cross-component interaction bugs, but at different granularities. SP-4 targets dimensional mismatches in pipelines. RM-3 traces state variables across component boundaries. AD-4 examines emergent interactions from merging independently-designed components.

**Redundancy risk**: Moderate. SP-4 and RM-3 overlap on cross-component state tracing. If both are implemented, RM-3's Component Interaction Analysis table should reference SP-4's quantity flow annotations rather than re-deriving them.

**Recommendation**: SP-4 (narrower, cheaper) should be implemented first. RM-3 extends the analysis to non-pipeline interactions. AD-4 is the most expensive and should be deferred unless merge-emergent bugs become a recurrent pattern.

---

## 2. Cross-Command Dependency Map

```
spec-panel                adversarial              roadmap
==========                ===========              =======

SP-2 (Adversarial ------> AD-5 (Taxonomy)          RM-5 (Risk Categories)
  Tester)                   |                         |
    |                       v                         v
    v                   AD-2 (Assumptions) ------> RM-1 (State Invariant
SP-3 (Guard Table)         |                         Section)
    |                      v                          |
    v                   AD-1 (Invariant Probe)        v
SP-1 (Correctness         |                      RM-2 (Negative ACs)
  Focus)                   v                          |
    |                   AD-3 (Scoring Dimension)      v
    v                      |                      RM-3 (Interaction
SP-4 (Pipeline Dim.)       v                         Boundary)
    |                   AD-4 (Stress Test)            |
    v                                                 v
SP-5 (Challenge                                   RM-4 (Boundary Agent)
  Protocol)
```

**Key Dependencies**:
1. **SP-2 enables SP-5**: The cross-expert challenge protocol is most valuable when the adversarial tester is available as a challenger.
2. **AD-2 feeds AD-1**: Shared assumptions surface the input for invariant probing.
3. **SP-3 feeds RM-1**: Guard boundary tables from spec review should propagate to roadmap state invariant analysis.
4. **RM-1 + RM-3 feed RM-4**: The invariant boundary agent is most effective when consuming structured data from prior proposals.

---

## 3. Conflict Analysis

### Potential Conflicts

**Overhead accumulation**: If all 15 proposals are implemented, the cumulative overhead across the pipeline could be substantial. Individually, most proposals add 5-15% overhead to their respective command. Cumulatively across spec-panel + adversarial + roadmap, the full pipeline could slow by 30-50%. This conflicts with the design principle of "adding 15-20 minutes of focused analysis, not doubling the review time."

**Mitigation**: Implement proposals in tiers. Tier 1 (immediate) adds < 10% overhead per command. Tier 2 (next cycle) adds another 10-15%. Tier 3 (future) is deferred until Tier 1-2 value is validated.

**Context window competition**: Several proposals require consuming prior stages' output (SP-3's boundary table, AD-2's assumptions, RM-1's invariant table). Each artifact competes for context window space. If a spec review produces a 500-token boundary table and a 300-token quantity flow diagram, the adversarial debate must load these in addition to the variants, consuming context that could be used for deeper analysis.

**Mitigation**: Artifacts should be concise and structured (tables, not prose). Downstream stages should consume summary versions, not full artifacts.

**Forcing function fatigue**: Multiple forcing functions (boundary table + quantity flow + assumption extraction + invariant analysis + negative ACs) could cause "checklist fatigue" where the generator produces formulaic, low-quality entries to satisfy structural requirements. This is the "correctness theater" risk identified in the SP-1 debate.

**Mitigation**: Quality validation at each stage (Wave 4 agents, challenge rounds, convergence gates) filters low-quality output. But the validators themselves have limited capacity to distinguish genuine from formulaic analysis.

### No Conflicts Between Proposals

No two proposals are mutually contradictory. All proposals are additive to the existing pipeline. The conflicts are resource-based (overhead, context, fatigue), not structural.

---

## 4. Minimum Viable Improvement Sets

Based on the cross-cutting analysis, three minimum viable improvement (MVI) sets are identified:

### MVI-1: "Catch-Both-Bugs" Set (4 proposals)

The smallest set that would have caught both v0.04 bugs with high probability:

| Proposal | Score | Rationale |
|----------|-------|-----------|
| AD-2: Consensus Assumption Extraction | 82.5 | Surfaces "events produce widgets" and "tail is non-empty" |
| AD-5: Debate Topic Taxonomy | 77.5 | Forces debate on state mechanics level |
| SP-2: Adversarial Tester Persona | 78.0 | Attacks guard conditions and degenerate inputs |
| RM-5: Risk Register Categories | 72.5 | Forces consideration of STATE and XCOMP risk categories |

**Total overhead**: ~15-20% across the full pipeline
**Implementation effort**: ~3-5 days total

### MVI-2: "Deep Defense" Set (7 proposals)

MVI-1 plus structural forcing functions:

| Proposal | Score | Rationale |
|----------|-------|-----------|
| *MVI-1 proposals* | | |
| SP-3: Guard Boundary Table | 75.5 | Forces boundary value reasoning for every guard |
| RM-1: State Invariant Analysis Section | 76.5 | Carries invariant inventory into roadmap |
| RM-2: Negative Acceptance Criteria | 79.5 | Algorithmically generates failure-mode tests |

**Total overhead**: ~25-35% across the full pipeline
**Implementation effort**: ~7-10 days total

### MVI-3: "Full Coverage" Set (all 15 proposals)

Complete implementation with all proposals and inter-stage artifact propagation.

**Total overhead**: ~40-55% across the full pipeline
**Implementation effort**: ~15-20 days total
**Recommendation**: Only after MVI-1 and MVI-2 are validated through at least one development cycle each.

---

## 5. Implementation Sequencing Across Commands

Given the dependencies and synergies, the optimal cross-command implementation order is:

**Wave 1 (Immediate, < 1 week)**:
1. RM-5: Risk Register Categories (template change, minutes to implement)
2. SP-2: Adversarial Tester Persona (persona definition, 1-2 hours)
3. AD-5: Debate Topic Taxonomy (taxonomy + gate, 2-4 hours)
4. AD-2: Consensus Assumption Extraction (diff-analysis sub-step, 4-8 hours)

**Wave 2 (Next cycle, 1-2 weeks)**:
5. SP-3: Guard Boundary Table (artifact template + completion criteria, 2-4 hours)
6. RM-1: State Invariant Analysis Section (template + Wave 3/4 instructions, 2-4 hours)
7. RM-2: Negative Acceptance Criteria (transform set + extraction integration, 1-2 days)
8. AD-1: Invariant Probe Round (fault-finder agent + convergence gate, 1-2 days)

**Wave 3 (Future, after validation)**:
9. SP-1: Correctness Focus Pass (5 expert behavior modifications, 2-3 days)
10. SP-4: Pipeline Dimensional Analysis (heuristic + trigger, 4-8 hours)
11. RM-3: Cross-Component State Flow (extraction step + template, 1-2 days)
12. AD-3: Edge Case Scoring Dimension (rubric update + floor, 4-8 hours)
13. SP-5: Cross-Expert Challenge Protocol (workflow restructuring, 2-3 days)
14. AD-4: Post-Merge Stress Test (full new step, 2-3 days)
15. RM-4: Invariant Boundary Agent (full new agent, 3-5 days)

---

## 6. Key Observations

1. **The highest-value proposals are the cheapest**: AD-2 (82.5, S-Tier) and RM-5 (72.5, A-Tier) are among the simplest to implement. The relationship between cost and value is inverted -- the pipeline's biggest gaps are structural omissions, not analytical depth problems.

2. **Forcing functions outperform analytical enhancements**: Proposals that make it structurally impossible to skip reasoning (boundary tables, taxonomy gates, risk categories) consistently outperform proposals that try to make the reasoning deeper (invariant agents, stress tests). This suggests the pipeline's primary failure mode is omission, not superficiality.

3. **Cross-command artifact propagation is the underexplored opportunity**: The proposals within each command are well-designed, but the inter-command connections are implicit. Explicit artifact propagation (SP-3's boundary table -> AD's debate input -> RM-1's invariant table) would multiply the value of individual proposals without adding new proposals.

4. **The adversarial debate proposals are the strongest set**: With AD-2 at S-Tier and AD-5 at high A-Tier, the adversarial debate command has the most impactful improvement opportunities. This is because the debate's structural flaw (diff-based analysis misses shared assumptions) is more fundamental than the spec-panel's flaw (missing expert lens) or the roadmap's flaw (missing template section).

---

*Cross-cutting analysis completed 2026-03-04 by Adversarial Debate Orchestrator.*
