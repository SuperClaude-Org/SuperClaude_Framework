# Patch Checklist

Generated: 2026-03-16
Total edits: 10 across 5 files

## File-by-file edit checklist

- phase-4-tasklist.md
  - [ ] H1: Replace `src/superclaude/cli/sprint/logger.py` with `src/superclaude/cli/sprint/logging_.py` in T04.01 (deliverable D-0013 description, Steps 1-2, acceptance criteria)
  - [ ] M1: Add Phase 5 blocking note to T04.03 Notes and add M1.0 reference for audit scope
  - [ ] L1: Replace "exempted with rationale" with "documented with rationale" in T04.03 acceptance
  - [ ] L3: Standardize deprecation warning mechanism in T04.02 steps 4 and 6

- phase-2-tasklist.md
  - [ ] H2: Update T02.03 acceptance criterion 1 with conditional Primary/Fallback mechanism detail
  - [ ] M3a: Add "before subprocess launch" timing to T02.02 acceptance criterion 1

- phase-5-tasklist.md
  - [ ] M3b: Add "before subprocess launch" timing to T05.01 T04.01 test description

- phase-6-tasklist.md
  - [ ] M2: Change T06.03 acceptance from "all 8 files" to "all 7 modified files + 1 new test file"
  - [ ] L2: Remove "or estimated based on file size" from T06.02 acceptance criterion

- tasklist-index.md
  - [ ] H1-index: Update Deliverable Registry D-0013 description to reference `logging_.py` instead of `logger.py`

## Cross-file consistency sweep

- [ ] Verify no other references to `logger.py` remain in any phase file (search all phase-*-tasklist.md)
- [ ] Verify T04.03 blocking relationship is reflected in Phase 5 checkpoint entry

---

## Precise diff plan

### 1) phase-4-tasklist.md

#### Section: T04.01

**A. Fix file path (H1)**
Current issue: References `src/superclaude/cli/sprint/logger.py`
Change: Replace with `src/superclaude/cli/sprint/logging_.py`
Diff intent: All 5 occurrences of `logger.py` in T04.01 become `logging_.py`

#### Section: T04.02

**B. Standardize deprecation mechanism (L3)**
Current issue: Step 4 says `warnings.warn(...)` and step 6 says "log deprecation warning"
Change: Clarify both use `warnings.warn("...", DeprecationWarning, stacklevel=2)`
Diff intent: Step 6 changes from "log deprecation warning" to "emit deprecation warning via `warnings.warn()`"

#### Section: T04.03

**C. Add Phase 5 blocking note (M1)**
Current issue: Notes do not mention Phase 5 blocking
Change: Append to Notes: "This deliverable gates Phase 5 entry per roadmap. Phase 5 tasks must not begin until T04.03 is accepted. Audit scope is the PhaseStatus.PASS switch sites identified in M1.0 (D-0002)."
Diff intent: Notes field expanded with blocking and scope info

**D. Fix disposition options (L1)**
Current issue: Acceptance says "parity confirmed / gap resolved / exempted with rationale"
Change: Replace "exempted with rationale" with "documented with rationale"
Diff intent: "exempted" -> "documented" in acceptance criterion 3

### 2) phase-2-tasklist.md

#### Section: T02.03

**E. Add Primary/Fallback mechanism detail (H2)**
Current issue: Acceptance criterion 1 says "Subprocess launch uses M1.0-confirmed mechanism to constrain file resolution"
Change: Replace with "If OQ-006 confirms env var support, subprocess receives isolation path via `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}`; if env var is ineffective, subprocess receives isolation path via `cwd=isolation_dir`. Implementation follows the mechanism documented in D-0001."
Diff intent: Generic "M1.0 mechanism" replaced with explicit conditional

#### Section: T02.02

**F. Add timing constraint (M3a)**
Current issue: Acceptance criterion 1 says "Isolation directory created at ..."
Change: Add "**before subprocess launch**" after "created at"
Diff intent: "Isolation directory created at ..." -> "Isolation directory created **before subprocess launch** at ..."

### 3) phase-5-tasklist.md

#### Section: T05.01

**G. Add timing constraint to test description (M3b)**
Current issue: T04.01 description says "Isolation directory created before subprocess launch; contains exactly one file" (in deliverables) but the Steps/acceptance paraphrase drops "before subprocess launch"
Change: Ensure acceptance criterion says "Tests verify isolation directory lifecycle: creation **before subprocess launch**, single-file content, success cleanup, failure cleanup, orphan cleanup"
Diff intent: Add "before subprocess launch" to acceptance criterion 3

### 4) phase-6-tasklist.md

#### Section: T06.03

**H. Fix file count (M2)**
Current issue: Acceptance says "all 8 files reviewed"
Change: Replace with "all 7 modified files + 1 new test file (8 total) reviewed"
Diff intent: "all 8 files" -> "all 7 modified files + 1 new test file (8 total)"

#### Section: T06.02

**I. Remove estimation alternative (L2)**
Current issue: Acceptance says "~14K token reduction per phase confirmed or estimated based on file size"
Change: Remove "or estimated based on file size"
Diff intent: "confirmed or estimated based on file size" -> "confirmed"

### 5) tasklist-index.md

#### Section: Deliverable Registry

**J. Fix D-0013 file reference (H1-index)**
Current issue: D-0013 row references `logger.py`
Change: Replace `logger.py` with `logging_.py`
Diff intent: "SprintLogger.write_phase_result() in ... logger.py" -> "... logging_.py"

## Suggested execution order

1. phase-4-tasklist.md (4 edits: H1, M1, L1, L3 — highest impact)
2. phase-2-tasklist.md (2 edits: H2, M3a)
3. tasklist-index.md (1 edit: H1-index)
4. phase-5-tasklist.md (1 edit: M3b)
5. phase-6-tasklist.md (2 edits: M2, L2)
