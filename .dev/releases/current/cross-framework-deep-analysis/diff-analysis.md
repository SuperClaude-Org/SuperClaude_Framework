---
total_diff_points: 18
shared_assumptions_count: 14
---

## Shared Assumptions and Agreements

Both variants share the following foundational assumptions:

1. **8-phase sequential structure** with Phase 0 (setup) through Phase 8 (consolidation), identical phase names and purposes.
2. **Auggie MCP as primary evidence tool** with Serena + Grep/Glob as fallback; fallback usage must be annotated.
3. **Strict phase-gate enforcement** with halt-on-failure semantics — no downstream phase consumes unvalidated input.
4. **Three cross-cutting invariants**: anti-sycophancy (strength/weakness pairing), evidence-only claims (file:line), and adopt-patterns-not-mass.
5. **Output directory isolation** — all artifacts confined to `artifacts/` directory.
6. **Resume capability** via `--start`/`--end` flags treated as a core reliability feature.
7. **8 IronClaude component groups** and **11 llm-workflows components** as inventory targets.
8. **8 adversarial comparison pairs** in Phase 4.
9. **≥35 total artifacts** as the measurable completion target.
10. **Anti-sycophancy enforcement**: every strength claim must be paired with a weakness.
11. **OQ-004 resolution**: "discard both" verdicts → IC-native improvement items (not omissions).
12. **Phase 7 adversarial validation** as an independent re-challenge layer.
13. **`improvement-backlog.md` schema** must be compatible with `/sc:roadmap` ingestion.
14. **End-to-end traceability chain**: inventory → strategy → comparison → merged strategy → improvement plan → backlog.

---

## Divergence Points

### 1. Token Budget Specificity
- **Opus**: Provides explicit per-phase token estimates totaling ~170K tokens. Phase 4 identified as most expensive (40K).
- **Haiku**: No token budget at all — treats resource planning as implicit.
- **Impact**: Opus enables proactive resource management and risk detection before hitting limits. Haiku leaves teams blind to cost until execution.

### 2. Timeline Unit and Granularity
- **Opus**: Estimates in **hours** (Phase 0: 2h, Phase 1: 4h, total critical path: 38h → 3–5 working days).
- **Haiku**: Estimates in **working sessions** (Phase 1: 2–3 sessions, total: 14–25 sessions).
- **Impact**: Opus gives concrete calendar estimates; Haiku's "session" unit is ambiguous but conservative. Haiku's total range (14–25 sessions) is notably wider than Opus's (3–5 days), suggesting Haiku is more pessimistic or more cautious about variability.

### 3. Phase 2/3 Parallelism Posture
- **Opus**: Actively recommends running Phase 2 and 3 concurrently if executor supports it; calculates 4-hour savings on critical path.
- **Haiku**: Recommends sequencing Phase 2 and 3 **conservatively** if executor parallelism is unclear; warns not to "design concurrency the runner cannot honor."
- **Impact**: Opus optimizes for throughput; Haiku prioritizes correctness over speed. Haiku's caution is justified given the unresolved OQ-006.

### 4. Phase 6 Parallelism for Per-Component Plans
- **Opus**: Explicitly states per-component improvement plans can run in parallel; master plan is sequential after all components complete.
- **Haiku**: No parallelism guidance given for Phase 6; implicit sequential execution.
- **Impact**: Minor — Opus extracts additional efficiency; Haiku is silent rather than contradictory.

### 5. Phase 8 Artifact Parallelism
- **Opus**: Explicitly states all 4 final artifacts (artifact-index, rigor-assessment, backlog, sprint-summary) can be produced concurrently.
- **Haiku**: No such guidance.
- **Impact**: Same as above — Opus is more execution-optimized.

### 6. Roles / Team Model
- **Opus**: No role decomposition — treats execution as single-actor.
- **Haiku**: Defines 4 explicit roles: Architect lead, Analysis operator, Validation reviewer, optional Human reviewer.
- **Impact**: Haiku accommodates team-based execution; Opus assumes solo execution. Haiku's model is more realistic for larger organizations.

### 7. OQ-006 Resolution Stance
- **Opus**: Recommends testing parallelism in Phase 0; if unsupported, run Phase 2 then Phase 3 sequentially.
- **Haiku**: Flags OQ-006 as a blocking decision requiring resolution before execution begins; recommends conservative default of sequential.
- **Impact**: Opus is pragmatic (test and decide); Haiku is more cautious (decide before committing). Haiku reduces risk of mid-sprint redesign.

### 8. OQ-008 Auggie "Unavailable" Definition
- **Opus**: Recommends defining threshold as "<50% query coverage" = unavailable; partial results should be annotated.
- **Haiku**: Recommends establishing a "binary rule" covering timeout, repeated failure threshold, or incomplete result confidence — more nuanced.
- **Impact**: Haiku's multi-criteria approach is more operationally robust. Opus's 50% threshold is simpler and easier to implement.

### 9. OQ-005 (Schema Validator) Resolution
- **Opus**: Explicitly recommends producing a lightweight validation script; calls out that manual validation of 35+ artifacts is error-prone; estimates "50-line script pays for itself immediately."
- **Haiku**: Recommends automation "if low effort"; otherwise document manual protocol and failure modes — conditional rather than prescriptive.
- **Impact**: Opus takes a stronger position; Haiku is more hedged. Opus's stance is more actionable.

### 10. OQ-007 (Fixed vs Dynamic Comparison Pairs)
- **Opus**: Explicitly recommends capping at 8 pairs unless Phase 1 reveals a critical gap.
- **Haiku**: Silent on this open question — no recommendation given.
- **Impact**: Opus provides clearer scope control guidance.

### 11. Phase 5 Synthesis Organization Principle
- **Opus**: Synthesizes around component areas; "rigor without bloat" section as primary deliverable.
- **Haiku**: Explicitly recommends organizing synthesis around **principles** (evidence integrity, deterministic gates, restartability, bounded complexity, scalable quality enforcement) rather than only components.
- **Impact**: Haiku's principle-centric synthesis is architecturally stronger — produces more transferable guidance. Opus's component-centric approach is more directly traceable.

### 12. Phase 6 Priority Guidance
- **Opus**: Generic priority guidance (P0/P1/P2/P3 + effort tags).
- **Haiku**: Provides explicit ordering of what to prioritize structurally: gate integrity → evidence verification → restartability/resume semantics → traceability automation → artifact schema reliability.
- **Impact**: Haiku provides more actionable implementation sequencing guidance for Phase 6.

### 13. Phase 7 Characterization
- **Opus**: Treats Phase 7 primarily as a completeness and compliance scan.
- **Haiku**: Explicitly characterizes Phase 7 as a **formal architecture review gate**, with specific disqualifying conditions (unverifiable evidence, copied mass, broken lineage, drift into implementation scope).
- **Impact**: Haiku sets a higher bar and clearer failure conditions. More rigorous but also higher overhead.

### 14. Validation Domain Structure (Phase 8 / Success Criteria)
- **Opus**: Presents success criteria as a flat table of measurable acceptance criteria.
- **Haiku**: Organizes validation into 5 formal **domains**: Coverage, Evidence, Rule Compliance, Flow/Traceability, Operability — each with explicit validation methods.
- **Impact**: Haiku's domain structure is more auditable and systematic. Opus's flat table is simpler to check but less comprehensive.

### 15. Resume Testing as Acceptance Criteria
- **Opus**: Mentions resume as a desirable behavior; includes in acceptance criteria table.
- **Haiku**: Explicitly states resume testing must be part of **Phase 8 acceptance** — not optional QA.
- **Impact**: Haiku treats restartability as a first-class deliverable, not a nice-to-have.

### 16. Inventory Incompleteness Treatment
- **Opus**: Gaps annotated in sprint summary; backlog marked incomplete.
- **Haiku**: Recommends treating inventory incompleteness as **architecture debt** and surfacing it in `rigor-assessment.md`.
- **Impact**: Haiku's framing elevates inventory quality to an architectural concern rather than a documentation note.

### 17. Downstream Tooling Dependencies
- **Opus**: Lists `/sc:roadmap` and `/sc:tasklist` as post-sprint consumers.
- **Haiku**: Adds the same, but also explicitly calls out validating downstream schema expectations **before Phase 8 finalization** — a proactive integration check.
- **Impact**: Haiku reduces the risk of Phase 8 producing a backlog that fails ingestion at the last step.

### 18. Architect's Notes Section Framing
- **Opus**: Provides a balanced self-critique (Strengths/Weaknesses/Recommendations) with quantified trade-offs (single gate failure blocks 4 phases, Auggie as single point of failure).
- **Haiku**: Frames recommendations as prioritized imperatives (P0/P1/P2) with a "Final Architectural Stance" positioning the sprint as a "high-discipline analysis pipeline, not a loose research exercise."
- **Impact**: Opus is more analytically honest about risks; Haiku is more directive and easier to act on.

---

## Areas Where One Variant is Clearly Stronger

**Opus is stronger in:**
- **Token budget planning** — the only variant with concrete cost estimates; essential for runtime risk management
- **Parallelism extraction** — identifies and quantifies specific time savings from concurrent execution
- **OQ-005/OQ-007 resolution** — provides clear, actionable defaults where Haiku is silent or hedged
- **Calendar concreteness** — hours-based estimates enable actual project scheduling

**Haiku is stronger in:**
- **Team model** — role decomposition makes this executable by more than one person
- **Phase 5 synthesis architecture** — principle-centric organization produces more reusable strategic output
- **Phase 6 prioritization** — explicit structural ordering of what to improve first
- **Phase 7 rigor** — formal architecture review framing with explicit failure conditions
- **Validation domain structure** — 5-domain framework is more auditable than a flat table
- **Resume as first-class deliverable** — treats restartability as acceptance criteria, not optional
- **OQ-008 nuance** — multi-criteria "unavailable" definition is more operationally robust
- **Proactive downstream integration check** — validates `/sc:roadmap` schema before Phase 8, not after

---

## Areas Requiring Debate to Resolve

1. **Timeline unit and total range**: Opus's 3–5 days vs. Haiku's 14–25 sessions cannot both be correct without clarifying what a "session" is. Teams need to align on this before scheduling.

2. **Phase 2/3 parallelism default**: Opus defaults to "parallelize if possible"; Haiku defaults to "sequence conservatively." The right answer depends on OQ-006 resolution, but teams should pick one default posture before Phase 0 to avoid mid-sprint confusion.

3. **Phase 5 organization principle**: Component-centric (Opus) vs. principle-centric (Haiku) synthesis produces meaningfully different `merged-strategy.md` documents. This is a design decision with downstream effects on Phase 6 plan structure.

4. **OQ-008 threshold**: Opus's 50% coverage threshold vs. Haiku's multi-criteria approach. Both are reasonable; the merged answer should specify a concrete binary rule combining both (e.g., timeout OR failure count threshold OR <50% coverage).

5. **Phase 7 gate height**: Haiku's formal architecture review characterization imposes higher overhead than Opus's compliance scan framing. If schedule is tight, teams may need to pick between thoroughness and velocity here.
