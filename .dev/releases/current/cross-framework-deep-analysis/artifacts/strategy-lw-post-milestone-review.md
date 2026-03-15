# Strategy: LW Component — Post-Milestone Review Protocol

**Component**: Post-Milestone Review Protocol
**Source**: `.dev/taskplanning/POST_MILESTONE_REVIEW_PROTOCOL.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The post-milestone review protocol is a 7-stage structured retrospective with forward propagation — it not only analyzes what happened in the completed milestone but actively amends the next milestone specification to prevent issue recurrence.

**Core rigor mechanisms:**

- **4-condition completion checkpoint**: Stage 1 requires all of: tasks marked complete, QA validation checks passed, deliverables verified and approved, milestone success criteria met — before retrospective begins. `POST_MILESTONE_REVIEW_PROTOCOL.md:22-31`
- **Structured 5-dimension reflection** (Stage 2): Task execution analysis (QA pass rates, blocker frequency, estimation accuracy, batch size effectiveness), quality assessment, process efficiency, knowledge gaps, and innovation/learnings. Each dimension has specific sub-questions. `POST_MILESTONE_REVIEW_PROTOCOL.md:52-84`
- **Priority-tiered findings** (P1-P4): Critical (blocks next milestone or data loss) → High (significant quality/efficiency) → Medium (process optimization) → Low (nice-to-haves). `POST_MILESTONE_REVIEW_PROTOCOL.md:84-101`
- **User decision point** (Stage 3): After findings are presented, user explicitly selects which priority levels to address (1 = P1 only, 2 = P1+P2, 3 = P1+P2+P3, 4 = All, none = skip). No silent automatic escalation. `POST_MILESTONE_REVIEW_PROTOCOL.md:116-153`
- **Interim milestone creation** (Stages 4-5): For P1/P2 items, a formal M-X.5 milestone is designed and executed before M-X+1 begins. `POST_MILESTONE_REVIEW_PROTOCOL.md:164-272`
- **Forward propagation light review** (Stage 6): Applies P1/P2 learnings from M-X to M-X+1 specification via a quick scan for pattern matches. Produces required vs. recommended amendments. `POST_MILESTONE_REVIEW_PROTOCOL.md:276-332`
- **Measurable success metrics**: Issue recurrence rate (<10% target), estimation accuracy (±20% by M3+), QA efficiency (decreasing trend), M-X.5 frequency (decreasing), time to improvement (<3 days for P1/P2). `POST_MILESTONE_REVIEW_PROTOCOL.md:449-465`

**Rigor verdict**: The forward propagation step (Stage 6) is the most rigorous element — it turns retrospectives from documentation exercises into active prevention. Applying P1/P2 learnings to the next milestone specification before execution begins addresses the most common failure mode in retrospective processes (findings are documented but not acted on).

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- 7 stages with multiple sub-steps each creates a heavyweight retrospective process. For small milestones or low-risk projects, the overhead may exceed the benefit.
- Stages 4-5 (interim M-X.5 creation) add a full milestone cycle for improvements. The effort estimate for M-X.5 can approach 25% of the original milestone.
- Three separate `/sc:reflect` invocations (Stage 2 deep, Stage 6 light) plus `/sc:design` (Stage 4) plus `/rf:taskbuilder` (Stage 5) plus `/rf:task` (Stage 7a+7b) = 6+ command invocations for full protocol execution.

**Operational drag:**
- "Current Limitation: Claude Code slash commands cannot automatically trigger other slash commands." Each stage requires manual user invocation. The protocol is aspirationally automated but practically manual. `POST_MILESTONE_REVIEW_PROTOCOL.md:371-374`
- The M-X.5 interim milestone must complete before M-X+1 can begin (if P1/P2 items). This serializes milestone execution and adds calendar time.
- Stage 3 decision point requires human judgment about which priority levels to address. This is intentional but adds latency to automated pipelines.

**Token/runtime expense:**
- The Stage 2 reflection prompt template is 60+ lines with 5 analysis dimensions and 4 priority tiers. Each `/sc:reflect` invocation with this prompt is expensive.
- The M-X.5 task creation (Stage 5) goes through the full taskbuilder interview process, adding a full task-building session before the actual improvement work begins.

**Maintenance burden:**
- The protocol document itself (500 lines) is a complex operational procedure. Users must understand all 7 stages to apply it correctly.
- The "Future Enhancement" section describes automation that doesn't exist yet. The gap between the documented protocol and the actual manual process creates risk of incomplete execution.
- Success metrics are defined but not automatically measured. Calculating "issue recurrence rate" requires manual comparison of M-X and M-X+1 retrospectives.

---

## 3. Execution Model

The protocol is a **human-in-the-loop retrospective pipeline**:

1. **Stage 1**: Verify all completion conditions met
2. **Stage 2**: `/sc:reflect` with deep analysis prompt → structured findings by priority
3. **Stage 3**: Present to user → user selects priority levels to address
4. **Stage 4** (if applicable): `/sc:design` → M-X.5 specification document
5. **Stage 5** (if applicable): `/rf:taskbuilder` → M-X.5 task file
6. **Stage 6**: `/sc:reflect` light review → M-X+1 amendments (required vs. recommended)
7. **Stage 7a** (if applicable): `/rf:task` M-X.5 → await completion
8. **Stage 7b**: `/rf:task` M-X+1 → begin next milestone

**Quality enforcement**: The protocol enforces quality by requiring explicit documentation of failures, user-controlled scope of remediation, and mandatory forward propagation to prevent recurrence.

**Extension points**:
- Stage 6 review depth adjustable (light/deep/skip)
- M-X.5 effort cap (suggested: 25% of original milestone)
- Priority thresholds adjustable per project risk tolerance

---

## 4. Pattern Categorization

**Directly Adoptable:**
- Forward propagation (applying learnings from M-X to M-X+1 spec before execution) is directly adoptable as a standard step in SuperClaude's sprint workflow. This is the highest-value element.
- The 4-condition completion checkpoint (tasks done + QA passed + deliverables verified + success criteria met) is directly adoptable as SuperClaude's sprint exit gate.
- Priority-tiered findings (P1-P4) with explicit effort estimates per tier is directly adoptable for sprint retrospective reporting.

**Conditionally Adoptable:**
- The interim milestone concept (M-X.5) is conditionally adoptable for large sprint projects. For small sprints, inline fixes to the backlog are sufficient.
- The user decision point at Stage 3 is conditionally adoptable — appropriate for human-supervised workflows, but would need automation for fully programmatic pipelines.

**Reject:**
- The 7-stage full process for every milestone. A compressed version (completion gate → key learnings → forward propagation) captures 80% of the value at 20% of the cost.
- The requirement for separate M-X.5 task creation (full taskbuilder interview) for minor improvements. Direct specification amendments are sufficient for P3/P4 items.
- The manual multi-command invocation model. The entire protocol should be automatable as a single SuperClaude sprint post-phase hook.
