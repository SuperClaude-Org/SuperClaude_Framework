# Refactor Plan

## Overview
- Base variant: Variant 2 (`variant-2-original.md`)
- Incorporated variants: Variant 1 (`variant-1-original.md`)
- Planned changes: 4
- Rejected alternatives documented: 3
- Overall risk: Low-Medium
- Review status: auto-approved
- Approval timestamp: 2026-03-05T00:00:00Z

## Planned Changes

### Change 1 — Add verified duplication inventory
- Source variant and section: Variant 1, `## 2. Evidence: The Current Architecture`
- Target location in base: New section after Challenge 1
- Integration approach: insert
- Rationale: Debate agreed Variant 1 is stronger at enumerating concrete duplication and dead-code evidence; see U-001 and S-002.
- Risk level: Low

### Change 2 — Preserve dead-code/process-hook evidence
- Source variant and section: Variant 1, sections `2e` and `2f`
- Target location in base: Challenge 6 targeted fixes table and surrounding rationale
- Integration approach: append/replace
- Rationale: These are code-verified points and improve evidence density for the targeted-fix path.
- Risk level: Low

### Change 3 — Add a phased recommendation instead of binary choice
- Source variant and section: Variant 1, `## 3. Proposed Unified Architecture`
- Target location in base: Final recommendation section
- Integration approach: restructure
- Rationale: Debate favored Variant 2's caution, but Variant 1 contributes a useful long-term direction. Merge should recommend phased extraction rather than immediate total unification.
- Risk level: Medium

### Change 4 — Add explicit verified/unverified labeling
- Source variant and section: Derived from debate and scoring artifacts
- Target location in base: Throughout merged output
- Integration approach: insert annotations
- Rationale: Prevents the merged document from repeating unverified historical-origin claims as fact.
- Risk level: Low

## Base Weaknesses Being Addressed

| Issue in Base | Better Variant | Fix Approach |
|---|---|---|
| Under-describes concrete duplication already visible in repo | Variant 1 | Add verified duplication inventory section |
| Too binary between targeted fixes and no unification | Variant 1 | Add phased extraction recommendation |
| Does not foreground dead roadmap helper and process override duplication enough | Variant 1 | Carry over specific verified evidence |

## Changes NOT Being Made

| Diff Point | Non-base Approach | Why Not Adopted |
|---|---|---|
| X-001 | "Sprint must adopt execute_pipeline() as the single orchestration point" | Debate found this overcommits beyond evidence; no concrete design was shown that removes rather than relocates sprint's live poll loop. |
| C-003 | Sprint gets retry and parallelism benefits from shared executor | Verified executor features exist, but debate found they do not transfer cleanly to sprint's side-effectful phases. |
| Historical framing | "Half-completed extraction from sprint" | Local code search verifies present structure, not original intent. Claim remains unverified with available history. |

## Risk Summary

| Change | Risk | Impact | Rollback |
|---|---|---|---|
| 1 | Low | Adds evidence only | Remove inserted section |
| 2 | Low | Tightens targeted-fix rationale | Revert appended evidence |
| 3 | Medium | Alters decision framing | Restore binary challenge framing |
| 4 | Low | Improves epistemic clarity | Remove labels |
