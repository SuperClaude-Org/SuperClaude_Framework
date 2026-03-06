# Refactoring Plan

## Overview
- **Base Variant**: Variant B (Backlog) -- `.dev/releases/backlog/v2.13-CLIRunner-PipelineUnification/tasklist/tasklist-index.md`
- **Incorporated Variants**: Variant A (Current) -- selective improvements
- **Total Planned Changes**: 3
- **Total Rejected Changes**: 4
- **Overall Risk**: Low

## Planned Changes

### Change #1: Resolve Phase 4 Compliance Tier (X-002)

- **Source**: Debate Round 2 -- both advocates partially conceded
- **Target Location**: Phase 4 task entries (T04.01-T04.06) in base
- **Rationale**: Both advocates agreed the truth lies between STANDARD and EXEMPT. Phase 4 tasks run commands (`uv run pytest`, `git diff --stat`, `grep`) but don't modify source code. The framework's read-only context booster (+0.4) applies because no code is modified. However, tasks T04.01 (full test suite) and T04.02 (coverage report) execute code and should arguably be STANDARD for the first two, with remaining read-only checks as EXEMPT. **Resolution**: Keep T04.01 and T04.02 as STANDARD (they run pytest, which executes code), keep T04.03-T04.06 as EXEMPT (they run git diff and grep -- truly read-only). This split reflects the actual nature of each task.
- **Integration Approach**: Modify tier and verification method fields for T04.01 and T04.02 in Phase 4 tasklist and deliverable registry
- **Risk Level**: Low (metadata change only)

### Change #2: Add Visual Confidence Indicators to Traceability Matrix

- **Source**: Variant A, Traceability Matrix format
- **Target Location**: Traceability Matrix section in base
- **Rationale**: Variant A's `[████████--] 80%` format is more scannable at a glance than bare `85%`. Debate did not contest this -- it's an unambiguous UI improvement.
- **Integration Approach**: Replace bare percentages with visual bar + percentage format
- **Risk Level**: Low (cosmetic formatting change)

### Change #3: Strengthen Source Snapshot with Strategic Context

- **Source**: Variant A, R-003 ("Executor unification remains a hypothesis to validate in future phases")
- **Target Location**: Source Snapshot section in base
- **Rationale**: Variant A's advocate made a valid point that "executor unification is a non-goal" is load-bearing strategic context. Variant B already captures this in Source Snapshot bullet 4 ("Executor-level unification is an explicit non-goal"). The existing text is adequate but could be strengthened. **Resolution**: Keep B's existing text but add explicit "deferred as hypothesis for future validation" language from Variant A to emphasize this is not merely a current non-goal but a deliberate future-phase decision.
- **Integration Approach**: Modify Source Snapshot bullet 4 wording
- **Risk Level**: Low (text clarification)

## Changes NOT Being Made

### Rejected #1: Adopt Phase 1 Sequential Dependencies (from Variant A)
- **Diff Point**: X-001, C-011
- **Variant A Approach**: T01.01 -> T01.02 -> T01.03 -> T01.04 sequential chain
- **Rationale**: Variant A's advocate **conceded** in Round 2 that these dependencies are fabricated. The roadmap specifies no intra-M1 dependencies. The 4 subsystems target different executor line ranges. Sequential deps are rejected. (Debate evidence: Round 2 Variant A Rebuttal, concession on X-001)

### Rejected #2: Adopt 3-File Artifact Set (from Variant A)
- **Diff Point**: S-002
- **Variant A Approach**: spec.md + notes.md + evidence.md for every deliverable
- **Rationale**: For a LOW-complexity sprint with many XS/S tasks, producing 60 artifacts (20 deliverables x 3 files) is disproportionate overhead. Variant B's tier-conditional approach (spec.md only for STRICT, evidence.md for all) is more efficient. (Debate evidence: Scoring matrix S-002, Variant B wins at 70% confidence)

### Rejected #3: Adopt Hardcoded Absolute Paths (from Variant A)
- **Diff Point**: S-001, S-004
- **Variant A Approach**: Full absolute paths in every artifact reference
- **Rationale**: TASKLIST_ROOT-relative paths are standard engineering practice, more maintainable, and require only a single-line change on relocation. (Debate evidence: S-001, S-004 both won by Variant B at 85% confidence)

### Rejected #4: Adopt Preamble Roadmap Items R-001 to R-003 (from Variant A)
- **Diff Point**: C-009
- **Variant A Approach**: Map roadmap overview paragraphs as roadmap items
- **Rationale**: These are context paragraphs, not deliverables. R-003's strategic content is captured in the Source Snapshot (and strengthened by Change #3). The 1:1 deliverable-to-task mapping is cleaner without non-deliverable registry entries. (Debate evidence: C-009, Variant B wins at 72% confidence; X-003 demonstrates R-003 mapping error)

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Phase 4 tier split | Low | Metadata only; 2 tasks change from EXEMPT to STANDARD | Revert tier fields |
| #2 Visual confidence bars | Low | Formatting only | Revert to bare percentages |
| #3 Source Snapshot wording | Low | Text clarification | Revert to original text |

## Review Status
- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-05T00:00:00Z
