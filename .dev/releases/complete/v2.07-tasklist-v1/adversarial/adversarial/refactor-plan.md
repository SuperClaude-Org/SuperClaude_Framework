# Refactoring Plan — Unified Tasklist v1.0 Refactor Plan

**Base**: Variant A (`refactor-plan-merged.md`) — Score: 0.784
**Non-base**: Variant B (`tasklist-spec-integration-strategies.md`) — Score: 0.691
**Date**: 2026-03-04
**Approval**: auto-approved (non-interactive mode)

---

## Overview

The merged artifact unifies Variant A's implementation-ready patch text with Variant B's post-debate calibration, unified structure, and decision provenance. 10 planned changes address all base-selection "Strengths to Incorporate" items, correcting Variant A's correctness failures (pre-debate names, check numbering collisions) and structural weaknesses (concatenated format) while preserving its completeness, risk coverage, and patch-level specificity.

**Changes planned**: 10
**Changes rejected**: 4
**Overall risk**: Low (all changes are restructuring, renaming, or additive)

---

## Planned Changes

### Change #1: Restructure from concatenated plans to unified document
- **Source**: Variant B, overall document structure (lines 1-10, 191-225)
- **Target**: Entire base document — replace 5 separate H1-rooted plans with single unified document
- **Integration approach**: restructure
- **Rationale**: B's unified structure won S-001 (72% confidence). A's concatenation is an artifact of per-strategy generation, not intentional design. Debate transcript S-001.
- **Risk**: Low — content preserved, only organization changes

### Change #2: Replace pre-debate strategy names with post-debate names
- **Source**: Variant B, lines 28, 61, 91, 125, 156 (renamed strategy titles with strikethrough)
- **Target**: All strategy section headings and internal references
- **Integration approach**: replace
- **Rationale**: Corrects A's Correctness-1 and Correctness-3 failures. B won S-003 (80% confidence). Post-debate names reflect actual debate outcomes.
- **Risk**: Low — naming only
- **Mapping**:
  - "Stage-Gated Generation Contract" → "Stage Completion Reporting Contract"
  - "Single-Pass Clarification Rules" → "Generation Notes + Empty-File Guard"
  - "Self-Contained Task Item Quality Gate" → "Minimum Task Specificity Rule"
  - "Inline Verification Coupling" → "Acceptance Criteria Quality Rules"
  - "Pre-Write Structural Validation Checklist" → "Extended Pre-Write Validation"

### Change #3: Integrate debate verdicts and rejection rationale per strategy
- **Source**: Variant B, debate verdict blocks per strategy (lines 18, 30, 63, 93, 127, 158)
- **Target**: Add debate verdict + "What was rejected" subsection to each strategy
- **Integration approach**: insert (add after each strategy header)
- **Rationale**: B won S-004 (85% confidence). Decision provenance is essential for future implementers.
- **Risk**: Low — additive

### Change #4: Apply debate convergence to Strategy 1 (hybrid gating)
- **Source**: Debate transcript Round 3 convergence on X-001
- **Target**: Strategy 1 — §4.3 replacement text and §9 criteria
- **Integration approach**: replace
- **Rationale**: Both advocates converged: structural gates for deterministic predicates + observability for semantic checks. A's original halt-on-failure was overly aggressive; B's observability-only was insufficient. Debate X-001 (88% confidence).
- **Changes**:
  - Rename from "Stage-Gated Generation Contract" to "Stage Completion Reporting Contract"
  - Keep per-stage validation criteria table (A's unique contribution, U-001, 85%)
  - Change "must not advance" language to "reports completion via TodoWrite; structural gates check minimal viability"
  - Keep §9 criterion update but reword to reflect hybrid approach
- **Risk**: Low — scope narrowing, not expansion

### Change #5: Apply debate convergence to Strategy 2 (reduced scope + 2-field error)
- **Source**: Variant B lines 61-87 (reduced scope) + debate convergence X-002
- **Target**: Strategy 2 — replace full 5-patch implementation
- **Integration approach**: replace
- **Rationale**: Both converged on 2-field error format. B's reduced scope (empty-file guard + Generation Notes) correct for v1.0. A conceded 5-patch was over-prescriptive. Debate X-002 (92% confidence).
- **Changes**:
  - Replace 5-patch implementation with B's 2-change scope (empty-file guard + Generation Notes)
  - Add 2-field error format (error_code + message) as the v1.0 error contract
  - Keep A's exact patch text style but with B's reduced content
  - Defer full error taxonomy to v1.1
- **Risk**: Low — scope reduction

### Change #6: Apply debate convergence to Strategy 3 (3 criteria)
- **Source**: Debate convergence X-003
- **Target**: Strategy 3 — §7.N standalone requirement and §8.N check
- **Integration approach**: replace
- **Rationale**: Both converged at 3 criteria. A conceded session-start over-constrains; B conceded 2 is too minimal. Debate X-003 (90% confidence).
- **Changes**:
  - Reduce from 4 criteria to 3: (1) named artifact/target, (2) concrete action verb + explicit object, (3) no cross-task prose dependency
  - Remove "session-start executable" criterion (A's concession)
  - Update §8.N check to match 3 criteria
- **Risk**: Low — scope narrowing

### Change #7: Resolve check numbering collisions
- **Source**: Variant A's internal contradiction (IC analysis) + Variant B's checks 13-17
- **Target**: All §8 self-check references across strategies
- **Integration approach**: restructure
- **Rationale**: A has three conflicting numbering schemes (§8.N, item 9, checks 9-12). B's checks 13-17 assume gap. Resolution: unified numbering 9-17 combining both sets.
- **Changes**:
  - §8.1 Semantic Quality Gate (checks 9-12 from A Strategy 5):
    - 9: Required metadata fields non-empty (Effort, Risk, Tier, Confidence, Verification Method)
    - 10: Global Deliverable ID uniqueness (D-####) across entire bundle
    - 11: No placeholder descriptions (TBD, TODO, title-only)
    - 12: Every task has ≥1 roadmap reference (R-###)
  - §8.2 Structural Quality Gate (checks 13-17 from B Strategy 5):
    - 13: Phase task count bounds (≥1 and ≤25 per phase)
    - 14: Clarification task adjacency (⚠️ tasks before their blocked task)
    - 15: No circular dependency chains (A→B→C→A)
    - 16: XL splitting enforcement (EFFORT=XL must have subtasks)
    - 17: Confidence bar format consistency (all use `██░░░ N%` pattern)
  - Strategy 4's near-field completion check integrated as check 12.5 or folded into check 9
  - Strategy 3's standalone check integrated as check 11.5 or folded into check 11
- **Risk**: Medium — requires careful cross-reference alignment

### Change #8: Add consolidated v1.1 deferral table
- **Source**: Variant B, lines 203-213
- **Target**: New section at end of unified document
- **Integration approach**: append
- **Rationale**: B won U-005 (80% confidence). Consolidated table replaces A's scattered per-strategy deferrals.
- **Risk**: Low — additive

### Change #9: Add unified patch order with time estimates
- **Source**: Variant B, lines 215-225
- **Target**: New "Implementation Sequence" section
- **Integration approach**: append
- **Rationale**: B won S-005 (78% confidence) and C-009 (70% confidence). Unified ordering more implementable than per-strategy orders.
- **Risk**: Low — additive

### Change #10: Add token cost annotations
- **Source**: Variant B, scattered throughout strategies
- **Target**: Per-strategy metadata
- **Integration approach**: insert
- **Rationale**: B won U-007 (55% confidence). Low priority but useful for LLM-based tool specs.
- **Risk**: Low — additive

---

## Changes NOT Being Made

### Rejected Change R-1: Remove A's exact patch text in favor of B's directive style
- **Diff point**: C-003, U-001
- **Non-base approach**: Variant B uses high-level directives without full current/replacement blocks
- **Rationale**: A's exact patch text won U-001 (85% confidence) as uniquely valuable for implementation. Removing it would lose A's primary advantage.

### Rejected Change R-2: Remove A's risk assessment tables
- **Diff point**: U-002
- **Non-base approach**: Variant B has no per-strategy risk tables
- **Rationale**: Risk tables won U-002 (60% confidence). Useful for implementation planning.

### Rejected Change R-3: Remove A's non-invention constraint (Strategy 4)
- **Diff point**: U-003
- **Non-base approach**: Variant B has no non-invention constraint
- **Rationale**: Non-invention constraint won U-003 (82% confidence). Addresses real hallucination risk.

### Rejected Change R-4: Remove A's atomic write declaration (Strategy 5)
- **Diff point**: U-004
- **Non-base approach**: Variant B has no atomic write concept
- **Rationale**: Atomic write guarantee (not mechanism) is spec-level per debate concession. Won U-004 (62% confidence).

---

## Risk Summary

| Change | Risk | Impact if Wrong | Rollback |
|--------|------|-----------------|----------|
| #1 Restructure | Low | Navigation confusion | Revert to original concatenated format |
| #2 Rename | Low | Stale references | Find-and-replace |
| #3 Add verdicts | Low | Clutter | Remove verdict blocks |
| #4 Hybrid gating | Low | Scope debate reopens | Revert to either pure approach |
| #5 Reduced Strategy 2 | Low | Missing error format | Expand to full 5-patch |
| #6 3 criteria | Low | Gap in task quality | Add 4th criterion back |
| #7 Check numbering | **Medium** | Broken cross-references | Requires careful review |
| #8 Deferral table | Low | Redundancy | Remove section |
| #9 Patch order | Low | Implementation confusion | Revert to per-strategy orders |
| #10 Token costs | Low | Minor clutter | Remove annotations |

---

## Review Status
- **Approval**: auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-04T12:00:00Z
