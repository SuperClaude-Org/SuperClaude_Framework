# Refactoring Plan: Merged Architectural Analysis

## Overview
- **Base variant**: Variant B (analysis-agent-beta, skeptical-counterargument)
- **Incorporated from**: Variant A (analysis-agent-alpha, pro-inline)
- **Planned changes**: 6
- **Changes rejected**: 3
- **Overall risk**: Low (additive changes to base; no structural reorganization)

## Planned Changes

### Change #1: Add verified code evidence to challenges
- **Source**: Variant A, Sections 1-3 (code snippets with file:line citations)
- **Target**: Each of B's Challenge sections — embed actual source code as evidence
- **Integration approach**: Append code blocks under each challenge with ground-truth annotations
- **Rationale**: Debate Round 1, S-003 — A's code citations scored higher for evidential weight (65% confidence)
- **Risk**: Low (additive — adds evidence without changing B's conclusions)

### Change #2: Incorporate reframed implementation proposal
- **Source**: Variant A, Section 5 (implementation plan) + Round 3 reframing
- **Target**: New section after B's Summary — "Recommended Implementation (Post-Verification)"
- **Integration approach**: Insert A's 5-step plan, reframed per Round 3 consensus as "Python-side reading + prompt embedding" (not "adopt sprint's pattern")
- **Rationale**: U-001 scored High value; both advocates agreed on the reframing in Round 3
- **Risk**: Low (additive — new section, doesn't modify existing B content)

### Change #3: Add ground-truth verification results
- **Source**: Debate ground-truth investigation (codebase analysis performed during pipeline)
- **Target**: Each challenge's "Required verification" section — add findings
- **Integration approach**: For each verification item in B's checklist, add VERIFIED/REFUTED/PENDING status with evidence
- **Rationale**: X-002 (dead code claim) was definitively resolved; other claims partially resolved
- **Risk**: Low (additive — enriches B's verification framework with actual results)

### Change #4: Incorporate debuggability argument
- **Source**: Variant A, Section 4c (debuggability) + Round 2 consensus
- **Target**: New subsection under B's analysis — "Consensus Points from Debate"
- **Integration approach**: Document the 5 consensus points from the debate (both advocates agreed)
- **Rationale**: Debuggability argument was conceded by both sides; should be preserved
- **Risk**: Low (additive)

### Change #5: Add prompt injection mitigation design
- **Source**: Variant B, Challenge 6.1 (prompt injection risk) + A's Round 2 rebuttal (mitigation proposal)
- **Target**: Expand B's Challenge 6 with a "Proposed Mitigations" subsection
- **Integration approach**: Combine B's risk identification with A's mitigation proposals (`<file>` XML tags, content sanitization)
- **Rationale**: U-003 scored High value; A's rebuttal provided concrete mitigations
- **Risk**: Low (additive)

### Change #6: Replace weighted scoring with debate-validated assessment
- **Source**: Debate scoring matrix + base-selection.md combined scores
- **Target**: Replace A's Section 6 (self-assigned scoring) with debate-validated scoring
- **Integration approach**: New section referencing the adversarial scoring results rather than A's self-assigned weights
- **Rationale**: C-005 — both advocates agreed A's weights were self-referential; debate scoring is externally validated
- **Risk**: Medium (replaces A's framework with a different one — but A's framework was identified as biased)

## Changes NOT Being Made

### Rejected #1: Sprint pattern adoption language
- **Diff point**: C-003, C-004
- **Non-base approach**: A framed the proposal as "adopt sprint's @file pattern"
- **Rationale**: Debate Round 2-3 established that sprint's mechanism (LLM file discovery) is fundamentally different from what roadmap needs (deterministic content injection). The merged document uses the reframed "Python-side reading + prompt embedding" language instead.

### Rejected #2: `_build_subprocess_argv` deletion recommendation
- **Diff point**: X-002
- **Non-base approach**: A proposed deleting `_build_subprocess_argv` as dead code (Section 5, step 5)
- **Rationale**: Ground-truth proves it has 7+ test callsites. The function IS architecturally redundant with `ClaudeProcess.build_command()`, but deletion requires test refactoring first — not a simple delete.

### Rejected #3: A's weighted scoring table as-is
- **Diff point**: C-005
- **Non-base approach**: A's 80/90 vs 25/90 scoring with self-assigned weights
- **Rationale**: Both advocates agreed the weights favor inline's strengths. The debate-validated scoring (base-selection.md) provides a more rigorous assessment.

## Risk Summary

| Change | Risk | Impact if Wrong | Rollback |
|--------|------|----------------|----------|
| #1 Code evidence | Low | Slightly longer document | Remove code blocks |
| #2 Implementation plan | Low | Premature action | Remove section |
| #3 Ground-truth results | Low | Incorrect verification | Update findings |
| #4 Debuggability consensus | Low | Redundant content | Remove subsection |
| #5 Prompt injection mitigations | Low | Incomplete mitigations | Expand later |
| #6 Scoring replacement | Medium | Lose A's framework perspective | Restore A's table |

## Review Status
- **Approval**: Pending user review (interactive mode)
