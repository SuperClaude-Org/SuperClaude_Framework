# Tasklist: Spec Panel Amendments to sprint-spec.md

**Source document**: `spec-panel-roadmap-v2-review.md` (7 changes with exact BEFORE/AFTER blocks)
**Target document**: `sprint-spec.md`
**Generated**: 2026-02-23
**Apply order**: Change 1 through Change 7 (sequential, as specified in source document priority ordering)

---

## Pre-Implementation Notes

- All BEFORE/AFTER text blocks are defined in `spec-panel-roadmap-v2-review.md`. Do NOT paraphrase or reformat them. Apply verbatim using string-match replacement.
- Each task references a section in the source document by `Change N`. Open the source document and use the exact text from the BEFORE/AFTER blocks under that heading.
- BEFORE blocks have been verified against the current `sprint-spec.md` content as of 2026-02-23. All 7 changes match cleanly with no conflicts.

---

## Task 1: Amend Task 3.1 to Include Dead Code Removal

**Source**: See `spec-panel-roadmap-v2-review.md` Change 1

**What changes**: Two cell replacements in the Epic 3 task table, Task 3.1 row:
1. The "Change" column text (the long cell describing the Return Contract MANDATORY section)
2. The "Acceptance Criteria" column text

**Location in sprint-spec.md**: Line 129 — the `| 3.1 |` row in the Epic 3 task table.

**Instructions**:
1. Locate the Task 3.1 row in the Epic 3 task table.
2. In the "Change" column: find the BEFORE text from `spec-panel-roadmap-v2-review.md` Change 1, first BEFORE/AFTER pair. Replace with the corresponding AFTER text verbatim. The AFTER appends a "Dead code removal (appended scope)" paragraph to the end of the existing Change column text.
3. In the "Acceptance Criteria" column: find the BEFORE text from `spec-panel-roadmap-v2-review.md` Change 1, second BEFORE/AFTER pair. Replace with the corresponding AFTER text verbatim. The AFTER appends `; zero subagent_type lines remain in the file (confirm via: grep -c "subagent_type" src/superclaude/skills/sc-adversarial/SKILL.md returns 0)`.

**Conflict check**: PASSED — both BEFORE texts exist exactly as specified in the current sprint-spec.md line 129.

---

## Task 2: Add Maintenance Errata Section

**Source**: See `spec-panel-roadmap-v2-review.md` Change 2

**What changes**: Insert a new top-level section (pure addition, no text replacement).

**Location in sprint-spec.md**: Between the "Future Work: Deterministic Verification Layer (DVL)" section (ends at line 193) and the "Definition of Done" section (starts at line 196).

**Instructions**:
1. Locate the `---` separator that appears after the DVL section and before "## Definition of Done".
2. Insert the full AFTER block from `spec-panel-roadmap-v2-review.md` Change 2 at that position. The new section heading is "## Maintenance Errata: agents/README.md Incorrect Path Reference".
3. The AFTER block in the source document includes its own leading `---` separator. Ensure you do not create a duplicate separator.

**Conflict check**: PASSED — this is a pure addition. The insertion point (between DVL and DoD sections) exists cleanly.

---

## Task 3: Add Epic 3 Scope Clarification Note

**Source**: See `spec-panel-roadmap-v2-review.md` Change 3

**What changes**: Replace the Epic 3 header block (3 lines of header + goal + dependency) with an expanded version that adds a "Scope note" paragraph.

**Location in sprint-spec.md**: Lines 119-123 — the `## Epic 3` heading through the "Dependency" line.

**Instructions**:
1. Locate the Epic 3 header block starting with `## Epic 3: Return Contract Transport Mechanism (RC4 + S04)`.
2. Find the exact BEFORE text from `spec-panel-roadmap-v2-review.md` Change 3 (the 5-line block: heading, blank line, Goal, blank line, Dependency).
3. Replace with the AFTER text verbatim. The AFTER adds two lines: a blank line and a `**Scope note**:` paragraph after the Dependency line.

**Conflict check**: PASSED — the BEFORE text matches sprint-spec.md lines 119-123 exactly.

---

## Task 4: Add New Task 3.5 to Epic 3 Task Table

**Source**: See `spec-panel-roadmap-v2-review.md` Change 4

**What changes**: Replace the final two rows of the Epic 3 task table (Task 3.4 and struck-through 3.5) with three rows (Task 3.4, new Task 3.5, renumbered struck-through 3.6).

**Location in sprint-spec.md**: Lines 132-133 — the `| 3.4 |` and `| ~~3.5~~ |` rows.

**Instructions**:
1. Locate the final two rows of the Epic 3 task table (Task 3.4 row and the struck-through ~~3.5~~ Sync row).
2. Find the exact BEFORE text from `spec-panel-roadmap-v2-review.md` Change 4 (the two pipe-delimited rows).
3. Replace with the AFTER text verbatim. The AFTER contains three rows: the original 3.4 row (unchanged), the new Task 3.5 row (Tier 1 artifact existence quality gate), and the renumbered ~~3.6~~ Sync row.

**Conflict check**: PASSED — the BEFORE text matches sprint-spec.md lines 132-133 exactly.

---

## Task 5: Add R8 to Risk Register

**Source**: See `spec-panel-roadmap-v2-review.md` Change 5

**What changes**: Replace the R7 row (final row of Risk Register) with the same R7 row plus a new R8 row appended.

**Location in sprint-spec.md**: Line 178 — the `| R7 |` row in the Risk Register table.

**Instructions**:
1. Locate the R7 row in the Risk Register table (the final row before the `---` separator).
2. Find the exact BEFORE text from `spec-panel-roadmap-v2-review.md` Change 5 (the single R7 row).
3. Replace with the AFTER text verbatim. The AFTER contains the original R7 row followed by a new R8 row about concurrency namespacing.

**Conflict check**: PASSED — the BEFORE text matches sprint-spec.md line 178 exactly.

---

## Task 6: Add Sprint 0 Process Deliverable Section

**Source**: See `spec-panel-roadmap-v2-review.md` Change 6

**What changes**: Insert a new top-level section (pure addition, no text replacement).

**Location in sprint-spec.md**: Between the end of the "Implementation Order" section (ends at line 165) and the "## Risk Register" heading (line 168).

**Instructions**:
1. Locate the `---` separator that appears after the Implementation Order section and before "## Risk Register".
2. Insert the full AFTER block from `spec-panel-roadmap-v2-review.md` Change 6 at that position. The new section heading is "## Sprint 0 Process Deliverable: Formal Debt Register Initialization".
3. The AFTER block in the source document includes its own leading `---` separator. Ensure you do not create a duplicate separator.

**Conflict check**: PASSED — this is a pure addition. The insertion point (between Implementation Order and Risk Register sections) exists cleanly.

---

## Task 7: Definition of Done Additions

**Source**: See `spec-panel-roadmap-v2-review.md` Change 7

**What changes**: Four separate edits within the Definition of Done and Verification Plan sections:
1. Code Changes subsection: replace the final three checklist items with four items (adds Tier 1 gate item before verify-sync)
2. Quality Gates subsection: replace all five checklist items with six items (adds subagent_type grep check)
3. Verification subsection: replace all four checklist items with five items (adds Test 6 reference)
4. Verification Plan section: insert new Test 6 block after Test 5

**Location in sprint-spec.md**:
- Code Changes: lines 208-210 (three items starting with `base_variant` through `make verify-sync`)
- Quality Gates: lines 213-217 (five items starting with `No existing tests` through `Fallback trigger`)
- Verification: lines 220-223 (four items starting with `Verification Test 1` through `Verification Test 4`)
- Test 6 insertion point: after the Test 5 block (ends at line 296) and before the closing footnote line (line 299)

**Instructions**:

7a. **Code Changes subsection**:
  - Find the BEFORE text from `spec-panel-roadmap-v2-review.md` Change 7, first BEFORE/AFTER pair (three checklist items: `base_variant`, `unresolved_conflicts`, `make verify-sync`).
  - Replace with the AFTER text verbatim. Adds one new item (Tier 1 gate) before the `make verify-sync` item.

7b. **Quality Gates subsection**:
  - Find the BEFORE text from `spec-panel-roadmap-v2-review.md` Change 7, second BEFORE/AFTER pair (five checklist items).
  - Replace with the AFTER text verbatim. Adds one new item (zero `subagent_type` lines) at the end.

7c. **Verification subsection**:
  - Find the BEFORE text from `spec-panel-roadmap-v2-review.md` Change 7, third BEFORE/AFTER pair (four checklist items).
  - Replace with the AFTER text verbatim. Adds one new item (Verification Test 6) at the end.

7d. **Verification Plan — new Test 6**:
  - Locate the end of the "Test 5: End-to-End Invocation" block (the **Note** paragraph ending at line 296).
  - Insert the new "### Test 6: Tier 1 Quality Gate Structure Audit" block from `spec-panel-roadmap-v2-review.md` Change 7 (the final AFTER block under "New verification test to add after Test 5").
  - Insert before the closing `---` separator and footnote lines (lines 297-302).

**Conflict check**: PASSED — all four BEFORE texts match the current sprint-spec.md content exactly.

---

## Completeness Verification

| Change | Source Section | Sprint-spec Location | BEFORE Match | Status |
|--------|--------------|---------------------|--------------|--------|
| 1 | Change 1 (Escalation 1) | Line 129, Task 3.1 row | Exact match | READY |
| 2 | Change 2 (Amendment D) | Between lines 193-196 | Pure addition | READY |
| 3 | Change 3 (Amendment A) | Lines 119-123 | Exact match | READY |
| 4 | Change 4 (Escalations 2&3) | Lines 132-133 | Exact match | READY |
| 5 | Change 5 (Amendment B) | Line 178 | Exact match | READY |
| 6 | Change 6 (Amendment C) | Between lines 165-168 | Pure addition | READY |
| 7 | Change 7 (Amendment E) | Lines 208-210, 213-217, 220-223, after 296 | Exact match (4 blocks) | READY |

All 7 changes accounted for. Zero conflicts detected. All BEFORE blocks verified against current sprint-spec.md.
