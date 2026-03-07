# Diff Analysis: Per-Phase vs Per-Task Subprocess Granularity

## Metadata
- Generated: 2026-03-06
- Variants compared: 2
- Total differences found: 14
- Categories: structural (2), content (6), contradictions (4), unique (6)

---

## Structural Differences

| # | Area | Variant A (Per-Phase) | Variant B (Per-Task) | Severity |
|---|------|----------------------|---------------------|----------|
| S-001 | Top-level sections | 7 sections (Problem through Implementation) | 8 sections (adds Section 8: Context Fragmentation Trade-Off) | Low |
| S-002 | Acknowledged weaknesses | 4 weaknesses (5.1-5.4) | 6 weaknesses (5.1-5.6) with deeper self-critique | Medium |

---

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Subprocess granularity | One subprocess per phase (5-6 spawns per sprint). Runner delegates entire phase to one autonomous agent. | One subprocess per task (40-60 spawns per sprint). Runner orchestrates each task individually. | **High** |
| C-002 | Completion Protocol strategy | Mitigate via three axes: budget health (reimbursement), detection (error_max_turns → INCOMPLETE), reservation (budget - 5). Failure becomes "improbable." | Structurally eliminate: runner owns task inventory, tracks execution, constructs phase reports. Agent self-reporting becomes optional. | **High** |
| C-003 | Implementation complexity | ~1 week, Low risk. ~50 lines TurnLedger + ~30 lines integration. Additive to existing architecture. | ~3-4 weeks, Medium risk. ~865 lines new code. New orchestration layer, tasklist parser, context injection, result aggregation. | **High** |
| C-004 | Failure blast radius | Phase-level: if phase gate fails, all tasks' turns lost. A 13-task phase where task 10 fails wastes tasks 1-9's budget. | Task-level: only the failed task's turns are lost. Tasks 1-9 are independently reimbursable. | Medium |
| C-005 | Reimbursement granularity | Phase-level (all-or-nothing per phase). Can't reimburse "tasks 1-7 passed but 8-10 failed." | Task-level (individual per task). Each task independently evaluated and reimbursed. | Medium |
| C-006 | Runner's role | Passive: monitors NDJSON stream, tracks turns, manages ledger. Existing executor loop unchanged. | Active: owns task sequencing, context injection, dependency management, result aggregation. New executor architecture. | Medium |

---

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Context fragmentation severity | "Context preservation is not a minor benefit. Interdependent tasks within a phase are the norm." (Section 4.2). Claims context loss is a fundamental problem. | "Context injection provides 80-90% of the continuity benefit" and "the runner's structured summary may actually be MORE reliable than an agent's degrading memory in a long session" (Section 5.1 mitigation, Section 8). Claims context loss is manageable. | **High** |
| X-002 | Cold-start overhead impact | Cites 250K-2.5M tokens for per-task as evidence of prohibitive overhead: "This overhead is NOT reimbursable — it's infrastructure cost" (Section 4.3). | Acknowledges same numbers but with isolation (mandatory): "~230K tokens of overhead" and "~46 turns of overhead (manageable)" (Section 5.2). Claims isolation makes it viable. | **High** |
| X-003 | Completion Protocol residual risk | "The Completion Protocol problem is not structurally eliminated, but it is mitigated on three independent axes, making failure improbable" (Section 6). Accepts residual risk as acceptable. | "This is not a mitigation. It is a structural elimination of the failure mode" (Section 4.1). Frames residual risk in per-phase as unacceptable. | Medium |
| X-004 | Definition of "simpler recovery" | "Re-run phase 5 = one subprocess spawn with the same tasklist file" is simpler (Section 4.6). Fewer moving parts. | "Retry T03.04 spawns one subprocess for one task. No wasted re-execution of already-passed tasks" is more precise (Section 3.3). Less waste. | Medium |

---

## Unique Contributions

| # | Variant | Contribution | Value |
|---|---------|-------------|-------|
| U-001 | A | **Turn reservation**: Set `--max-turns` to `budget - 5` to reserve headroom for Completion Protocol report. Simple arithmetic that reduces exhaustion probability. | Medium |
| U-002 | A | **error_max_turns reclassification**: Detect the event in NDJSON stream and reclassify PASS_NO_REPORT as INCOMPLETE. Orthogonal to reimbursement, zero extra turn cost. | **High** |
| U-003 | A | **Per-task evaluation within phase gate**: Trailing gate could evaluate individual tasks within a phase, enabling partial reimbursement — hybrid approach. | **High** |
| U-004 | B | **4-layer subprocess isolation as mandatory requirement**: Identifies that per-task viability depends on reducing cold-start from 50K to 5K tokens. Without it, overhead is prohibitive. | **High** |
| U-005 | B | **Runner-constructed phase reports**: Runner aggregates task results into phase reports, eliminating dependence on agent self-assessment entirely. | **High** |
| U-006 | B | **Section 8 trade-off framework**: Explicit, balanced analysis of whether context fragmentation is worth the visibility gain. Frames the central tension directly. | Medium |

---

## Summary
- Total structural differences: 2
- Total content differences: 6
- Total contradictions: 4
- Total unique contributions: 6
- Highest-severity items: C-001, C-002, C-003, X-001, X-002, U-002, U-003, U-004, U-005
