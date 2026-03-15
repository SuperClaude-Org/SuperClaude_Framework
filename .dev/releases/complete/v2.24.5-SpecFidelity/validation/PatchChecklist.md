# Patch Checklist
Generated: 2026-03-15
Total edits: 2 across 1 file

## File-by-file edit checklist

- phase-1-tasklist.md
  - [ ] Add renumbering context note to T01.05 Notes field (from finding M1)
  - [ ] Amend T01.04 first acceptance criterion to emphasize exit-code-0 gating (from finding L1)

## Cross-file consistency sweep
- [ ] No cross-file edits needed (findings are localized to phase-1-tasklist.md)

---

## Precise diff plan

### 1) phase-1-tasklist.md

#### Section/heading to change
- T01.05 Notes section
- T01.04 Acceptance Criteria

#### Planned edits

**A. Add renumbering context to T01.05 Notes (M1)**
Current issue: Notes field says "Roadmap estimates ~80% probability of BROKEN. Phase 5 should be treated as likely."
Change: Append renumbering context
Diff intent:
- Before: `**Notes:** Roadmap estimates ~80% probability of BROKEN. Phase 5 should be treated as likely.`
- After: `**Notes:** Roadmap estimates ~80% probability of BROKEN. Phase 5 should be treated as likely. Roadmap "Phase 1.5" = tasklist Phase 5 (renumbered for contiguous sequencing).`

**B. Amend T01.04 first acceptance criterion (L1)**
Current issue: First criterion says "Result is exactly one of: WORKING, BROKEN, or CLI FAILURE"
Change: Add exit-code-0 gating clarification
Diff intent:
- Before: `- Result is exactly one of: WORKING, BROKEN, or CLI FAILURE`
- After: `- Result is exactly one of: WORKING, BROKEN, or CLI FAILURE — where WORKING and BROKEN apply only when exit code is 0`
