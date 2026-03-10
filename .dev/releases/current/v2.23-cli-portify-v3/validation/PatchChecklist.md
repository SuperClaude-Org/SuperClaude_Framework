# Patch Checklist

Generated: 2026-03-09
Total edits: 4 across 2 files

## File-by-file edit checklist

- phase-1-tasklist.md
  - [ ] Amend T01.02 acceptance criterion 1 to include "mapping 1:1 to the section-to-source mapping table" (from finding L1)

- phase-5-tasklist.md
  - [ ] Add acceptance criterion to T05.05 for brainstorm timeout contract fields (from finding M2)
  - [ ] Amend T05.03 acceptance to scope resume substep check to resumable failures only (from finding L2)

## Cross-file consistency sweep

- [ ] Verify M1 (T01.01 reviewed spec artifact trace) — re-read T01.01 to confirm whether the text already includes this before patching

---

## Precise diff plan

### 1) phase-1-tasklist.md

#### Section: T01.02 Acceptance Criteria

**A. Add 1:1 mapping table check (L1)**
Current issue: Acceptance criterion 1 says "all 12 named sections" without mapping table verification
Change: Append mapping requirement to criterion 1
Diff intent:
- Before: "File `src/superclaude/examples/release-spec-template.md` exists with frontmatter schema and all 12 named sections"
- After: "File `src/superclaude/examples/release-spec-template.md` exists with frontmatter schema and all 12 named sections mapping 1:1 to the section-to-source mapping table from the spec"

### 2) phase-5-tasklist.md

#### Section: T05.05 Acceptance Criteria

**B. Add brainstorm timeout contract field check (M2)**
Current issue: Acceptance criteria don't verify failure_type and resume_substep for brainstorm timeout
Change: Add new acceptance criterion after the 4th bullet (or replace the 4th which is evidence-focused to make room, moving evidence to validation)
Diff intent:
- Add: "Brainstorm timeout scenario produces contract with `failure_type=brainstorm_failed` and `resume_substep=3c`"
- Note: Protocol requires exactly 4 acceptance criteria. Fold into existing criterion 4 if needed.

#### Section: T05.03 Acceptance Criteria

**C. Scope resume substep to resumable failures (L2)**
Current issue: Resume substep check doesn't specify "on resumable failures" qualifier
Change: Amend the resume substep criterion
Diff intent:
- Before: Check verifies resume_substep populated
- After: Check specifies "Resume substep populated on resumable failures (brainstorm_failed → resume_substep=3c, focus_failed → resume_substep=4a); non-resumable failures have empty resume_substep"

## Suggested execution order

1. phase-1-tasklist.md (L1 — low severity, single edit)
2. phase-5-tasklist.md (M2 + L2 — medium + low severity, two edits)
