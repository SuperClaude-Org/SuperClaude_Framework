---
base_variant: roadmap-opus-architect
variant_scores: 'A:81 B:81'
---

# Base Selection Analysis

## 1. Scoring Criteria (Derived from Debate)

Six criteria extracted from the six debate divergence points, weighted by impact on implementation success:

| Criterion | Weight | Rationale (Debate Source) |
|-----------|--------|--------------------------|
| Requirement Coverage & Traceability | 20% | Both variants claim spec coverage; granularity matters for downstream tasklist generation |
| Architectural Soundness | 20% | Orchestrator explicitness and adversarial placement disputes center on architecture |
| Risk Management | 15% | Both identify risks; depth vs breadth was debated |
| Implementation Practicality | 15% | Timeline honesty, parallelization, and actionability disputes |
| Validation Strategy | 15% | Mode-combination vs 4-layer model was a core disagreement |
| Schema/Contract Discipline | 15% | Phase 0 necessity debate is fundamentally about contract stability |

## 2. Per-Criterion Scores

### Requirement Coverage & Traceability

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | **88** | Every milestone cites specific SC-*, FR-*, NFR-* IDs. Checkpoint table maps milestones to criteria. Validation section lists 8 concrete checkpoints with methods. |
| B (Haiku) | 75 | Success criteria referenced in Layers A-D but per-milestone mapping to specific requirement IDs is sparse. Phase milestones describe behavior without consistent SC-* citations. |

**Justification**: Opus's granular traceability (e.g., "Milestone 1.2 validates SC-011, SC-020, FR-014, FR-015") is directly actionable for implementation tracking. Haiku's layer model validates categories of requirements but doesn't make it easy to verify "which milestone delivers SC-018?"

### Architectural Soundness

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 78 | Clean 6-phase structure with clear dependency graph. Strategy pattern noted for adversarial. But orchestrator logic is implicit — scattered across phase milestones. No explicit abstraction point for template-vs-adversarial routing (debate Round 2 rebuttal: Haiku correctly noted "replacing" language in M4.3 implies retrofit). |
| B (Haiku) | **82** | Explicit wave runner as Phase 1 deliverable (M1.1). Mode-aware routing designed into Phase 3 planning layer. 7-phase structure adds overhead but the orchestrator component addresses the 7 behavioral concerns convincingly. |

**Justification**: Haiku's rebuttal on orchestrator complexity was persuasive — REVISE loop + mode-aware resume + dry-run cutoff + state persistence interactions are non-trivial. The debate transcript shows Opus reduced each concern to a primitive (`if`, `for`, `try/catch`) but ignored their interaction, which Haiku correctly identified as "where bugs live."

### Risk Management

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | **83** | 12 risks with structured probability/impact/mitigation/phase table. Includes architectural risks (RISK-010 through 012) that Haiku omits. Broader coverage provides better risk surface visibility. |
| B (Haiku) | 80 | 9 risks with deeper narrative on top 4. Mitigation strategies are more detailed per risk. But narrower coverage misses template scoring inconsistency (Opus RISK-011), SKILL.md line overflow (RISK-010), and REVISE UX (RISK-012). |

**Justification**: Opus's broader risk identification is marginally more valuable than Haiku's deeper narratives on fewer risks. The debate didn't resolve this — the synthesis recommendation suggested combining both approaches.

### Implementation Practicality

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | **85** | 14-23 day range with explicit critical path analysis. Open questions have recommended resolutions with blocking-phase mapping. Milestones have concrete deliverables. Parallelization opportunities identified without mandating them. |
| B (Haiku) | 78 | 20-31 day range is more honest for single-engineer. Phase 0 adds 2-3 days upfront. Engineering roles defined (4 roles). But some milestones are less concrete (e.g., M0.3 "Resolve design-blocking open questions" is process, not implementation). |

**Justification**: Opus's rebuttal was effective — the parallelization analysis is "strictly additive" information. Haiku's Round 2 point about misleading timelines has merit, but Opus explicitly states both critical path (10-16) and total path (14-23). The information is more useful, not less honest.

### Validation Strategy

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 75 | Mode-combination test matrix is directly executable as a test plan. Checkpoint table provides traceability. But organized by user-facing behavior, not by coverage domain — gaps possible in contract fields or failure modes. |
| B (Haiku) | **88** | 4-layer model (Contract → Flow → Dependency/Failure → Quality) ensures systematic coverage. Gate structure (4 gates) provides clear release criteria. Layer model catches gaps that mode-combination testing misses — per Haiku's persuasive rebuttal in Round 2. |

**Justification**: Haiku's Round 2 rebuttal was the strongest point in the entire debate: "A unit test can validate a contract, a flow, or a failure path. The layer model ensures coverage completeness." Mode-combination tests can pass for the wrong reasons if individual contract fields aren't independently tested.

### Schema/Contract Discipline

| Variant | Score | Evidence |
|---------|-------|----------|
| A (Opus) | 74 | Versioned frontmatter, additions-only policy (NFR-003). But schema emerges from implementation — Opus's position that "implementation IS contract freezing" conflates individual interpretation with reviewed decision (per Haiku's Round 2 rebuttal). |
| B (Haiku) | **86** | Dedicated Phase 0 with M0.1 schema freeze, M0.2 wave architecture freeze, M0.3 open question resolution. Contract tests as acceptance criteria. Interface decision record as deliverable. |

**Justification**: Haiku's Round 2 rebuttal was convincing: "Implementation freezes one interpretation — the one the implementer happened to choose." The spec leaves unresolved edge cases (optional vs required semantics per mode, null vs absent validation fields) that benefit from explicit review before code depends on them.

## 3. Overall Scores

| Variant | Weighted Score | Strengths | Weaknesses |
|---------|---------------|-----------|------------|
| A (Opus) | **81** | Traceability (88), Practicality (85), Risk breadth (83) | Schema discipline (74), Validation coverage (75) |
| B (Haiku) | **81** | Validation strategy (88), Schema discipline (86), Architecture (82) | Traceability (75), Practicality (78) |

The variants score identically overall but excel in complementary domains.

## 4. Base Variant Selection Rationale

**Selected base: Variant A (Opus Architect)**

Despite identical overall scores, Opus is the stronger base for merge because:

1. **Traceability is harder to retrofit**: Opus's per-milestone SC-*/FR-*/NFR-* citations represent granular work that cannot be easily added to Haiku's structure. Haiku's strengths (contract freeze, layered validation, orchestrator) are *additive* — they can be incorporated as enhancements to Opus's existing milestones.

2. **Phase structure is more implementation-ready**: Opus's 6 phases map directly to implementation sprints with concrete deliverables. Haiku's Phase 0 can be condensed and prepended. Haiku's phase reordering (adversarial in Phase 3 instead of Phase 4) requires restructuring Opus less than the reverse.

3. **Critical path analysis adds value**: The parallelization identification is useful information regardless of team size. It's easier to ignore parallelization opportunities than to add them after the fact.

4. **Open question resolutions are actionable**: Opus provides recommended resolutions with blocking-phase mapping. Haiku defers to Phase 0 process, which is correct in principle but less immediately useful as a roadmap artifact.

## 5. Specific Improvements from Haiku to Incorporate in Merge

### Must Incorporate (High Impact)

1. **Condensed Contract Freeze** (from Haiku Phase 0): Add a 1-2 day Phase 0 (not 2-3) with schema freeze for frontmatter fields, mutual exclusivity rules, and optional/required semantics per mode. Produce an interface decision record. This addresses Opus's weakest score (74 on schema discipline).

2. **4-Layer Validation Model** (from Haiku Section 5): Restructure Opus's validation approach to use Haiku's Layer A-D organization *populated with* Opus's mode-combination test cases. This combines the best of both: coverage completeness from layers, actionable test cases from mode combinations.

3. **Explicit Orchestrator Component** (from Haiku M1.1): Add a tightly-scoped wave runner deliverable to Opus's Phase 1. Not a heavyweight engine, but an explicit component that encapsulates: conditional Wave 1A, sequencing constraints, REVISE loop, dry-run cutoff, state persistence hooks, and resume logic. This addresses the interaction complexity Haiku identified.

4. **Release Readiness Gate** (from Haiku Phase 6): Add explicit release-readiness criteria as a Phase 6 gate, including: 100% pass on schema contract tests, 100% pass on adversarial routing tests, 100% pass on chunked extraction verification, 100% pass on resume/collision safety tests.

### Should Incorporate (Medium Impact)

5. **Adversarial Routing Abstraction Point**: Add an explicit abstraction point in Phase 2 where template-based and adversarial generation paths diverge. This prevents the "replacing" retrofit Haiku identified in Opus M4.3. A simple interface/strategy pattern stub in Phase 2 costs little and prevents rework.

6. **Engineering Role Identification** (from Haiku Section 4): Add Haiku's 4-role identification (primary implementer, validation/test owner, architecture reviewer, documentation owner) to Opus's resource requirements section.

7. **Deeper Narrative on Top 4 Risks**: Supplement Opus's risk table with Haiku's narrative depth on risks 1-4 (schema breakage, adversarial degradation, extraction failure, stale resume). Keep Opus's broader 12-risk identification.

### Optional (Low Impact)

8. **Negative-Path Test Matrix** (from Haiku M6.3): Haiku's explicit negative-path test list is useful but can be derived from Opus's existing checkpoint table. Include if space permits.

9. **Schedule Risk Adjustments** (from Haiku Section 6): Add Haiku's contingency conditions as a note to Opus's timeline summary.
