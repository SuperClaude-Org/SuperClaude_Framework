# Base Selection: Per-Phase vs Per-Task Subprocess Granularity

## Quantitative Scoring (50% weight)

| Metric | Weight | Variant A (Per-Phase) | Variant B (Per-Task) |
|--------|--------|----------------------|---------------------|
| Requirement Coverage (RC) | 0.30 | 0.90 (4.5/5 requirements) | **1.00** (5/5 requirements) |
| Internal Consistency (IC) | 0.25 | 0.95 | 0.95 |
| Specificity Ratio (SR) | 0.15 | **0.89** (25/28 concrete) | 0.875 (28/32 concrete) |
| Dependency Completeness (DC) | 0.15 | 0.90 | **0.92** |
| Section Coverage (SC) | 0.15 | 0.875 (7/8 sections) | **1.00** (8/8 sections) |
| **Quantitative Score** | | **0.907** | **0.957** |

**RC detail**: Both address detection, classification, surfacing, and recovery. Variant B fully addresses "prevent the gap" (per-task budget prevents starvation); Variant A only partially prevents (bigger budget reduces probability).

**SR detail**: Both highly specific. Variant A has slightly better ratio (fewer vague statements per concrete) but Variant B has more total concrete statements.

---

## Qualitative Scoring (50% weight) — Additive Binary Rubric

### Completeness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Covers all explicit requirements | MET — addresses all 5 solution criteria | MET — addresses all 5 solution criteria |
| 2 | Edge cases and failure scenarios | MET — three-axis mitigation covers edge cases | MET — 6 weaknesses with detailed scenarios |
| 3 | Dependencies and prerequisites | MET — cites MonitorState, OutputMonitor, NDJSON | MET — 4-layer isolation, tasklist parser explicit |
| 4 | Success/completion criteria | MET — implementation table with effort/risk | MET — implementation table with 10-component breakdown |
| 5 | Out of scope defined | NOT MET | NOT MET |

**Completeness**: A = 4/5, B = 4/5

### Correctness (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | No factual errors | MET — cites real codebase, real sprint data | MET — cites dev.to analysis, cleanup-audit data |
| 2 | Technical feasibility | MET — additive to existing architecture | MET — standard task queue pattern |
| 3 | Terminology consistent | MET | MET |
| 4 | No internal contradictions | MET | MET |
| 5 | Claims supported by evidence | MET — MonitorState fields, NDJSON events | MET — token numbers, component line counts |

**Correctness**: A = 5/5, B = 5/5

### Structure (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Logical section ordering | MET | MET |
| 2 | Consistent hierarchy depth | MET | MET |
| 3 | Clear separation of concerns | MET | MET |
| 4 | Navigation aids | NOT MET | NOT MET |
| 5 | Follows artifact conventions | MET | MET |

**Structure**: A = 4/5, B = 4/5

### Clarity (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | Unambiguous language | MET | MET |
| 2 | Concrete rather than abstract | MET — worked example with numbers | MET — worked example with numbers |
| 3 | Clear purpose per section | MET | MET |
| 4 | Terms defined | MET — TurnLedger defined inline | MET — 4-layer isolation defined |
| 5 | Actionable next steps | MET — implementation table | MET — implementation table + component list |

**Clarity**: A = 5/5, B = 5/5

### Risk Coverage (5 criteria)

| # | Criterion | Variant A | Variant B |
|---|-----------|-----------|-----------|
| 1 | ≥3 risks with assessment | MET — 4 weaknesses with severity | MET — 6 weaknesses with severity |
| 2 | Mitigation per risk | MET — each weakness has mitigation | MET — each weakness has mitigation |
| 3 | Failure modes and recovery | MET — three-axis mitigation | MET — runner-owns-report |
| 4 | External dependencies | NOT MET — doesn't discuss Claude Code platform changes | MET — API rate limiting, platform isolation |
| 5 | Monitoring/validation mechanism | MET — NDJSON monitoring | MET — runner-level tracking |

**Risk Coverage**: A = 4/5, B = 5/5

---

## Position-Bias Mitigation

**Pass 1** (A first, B second): A = 22/25, B = 23/25
**Pass 2** (B first, A second): A = 22/25, B = 23/25
**Agreement**: Full agreement on all criteria. No re-evaluation needed.
**Disagreements found**: 0

---

## Combined Scoring

| Component | Weight | Variant A | Variant B |
|-----------|--------|-----------|-----------|
| Quantitative | 0.50 | 0.907 | 0.957 |
| Qualitative | 0.50 | 0.880 (22/25) | 0.920 (23/25) |
| **Combined** | | **0.894** | **0.939** |

**Margin**: 4.5% (within 5% tiebreaker threshold)

### Tiebreaker Applied: Level 1 — Debate Performance

| Metric | Variant A | Variant B |
|--------|-----------|-----------|
| Diff points won | 3 (C-003, X-001, X-002) | **5** (C-001, C-002, C-004, C-005, X-003) |
| Split points | 2 (C-006, X-004) | 2 |

**Tiebreaker result**: Variant B wins on debate performance (5 vs 3 points won).

---

## Selected Base: Variant B (Per-Task Subprocess)

### Selection Rationale

Variant B wins on combined scoring (0.939 vs 0.894) and debate performance (5 vs 3 points). The margin is narrow (4.5%), reflecting the genuine quality of both proposals. The decisive factors:

1. **Structural elimination > probabilistic mitigation** (C-002): The MaxTurn problem already materialized in production (Phase 5 of cleanup-audit-v2). "Improbable" was insufficient in practice.
2. **Requirement coverage** (RC): Variant B fully addresses all 5 solution criteria including prevention; Variant A only partially prevents the failure mode.
3. **Debate performance**: Variant B won 5 of 8 resolved diff points, with particularly strong showings on C-002 (Completion Protocol) and C-004 (failure blast radius).

### Strengths to Preserve from Base (Variant B)

- Per-task subprocess spawning with runner-owned task inventory
- Runner-constructed phase reports (no agent self-reporting dependency)
- 1:1 gate-task alignment for reimbursement
- 4-layer subprocess isolation as mandatory prerequisite
- Component-level implementation breakdown (10 independently testable units)

### Strengths to Incorporate from Variant A

1. **U-002: error_max_turns detection** — orthogonal defense-in-depth mechanism; valuable regardless of subprocess granularity
2. **Staged adoption strategy** — Phase 1: TurnLedger + error_max_turns (1 week), Phase 2: per-task migration (3-4 weeks)
3. **U-001: Turn reservation** — reserve budget headroom per task as optional enhancement
4. **Intra-phase checkpointing** as a migration stepping stone (from A's Round 2 new evidence)
5. **Context preservation emphasis** — strengthen context injection design to address A's legitimate concern
