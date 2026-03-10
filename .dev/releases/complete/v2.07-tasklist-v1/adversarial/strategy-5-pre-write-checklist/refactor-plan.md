# Refactor Plan — Strategy 5: Pre-Write Structural Validation Checklist

**Pipeline Step**: 4 of 5
**Date**: 2026-03-04
**Decision**: Adopt modified (checks 9–12 added to §8; atomic write declaration added to §9)
**Target files**:
- `sc-tasklist-command-spec-v1.0.md` (PRD) — Acceptance Criteria §9, Open Questions §10
- `Tasklist-Generator-Prompt-v2.1-unified.md` (v3.0 generator) — §8, §9

---

## Integration Points

### File 1: `Tasklist-Generator-Prompt-v2.1-unified.md`

**Location**: `/config/workspace/SuperClaude_Framework/.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md`

This is the canonical v3.0 generator. It is the source-of-truth that will be reformatted into `SKILL.md`. Changes here must be carried forward into SKILL.md.

#### Integration Point 1A: §8 Sprint Compatibility Self-Check — add 4 new checks

**Current §8 (lines 695–708):**
```markdown
## 8) Sprint Compatibility Self-Check (Mandatory)

Before finalizing output, verify all of the following:

1. `tasklist-index.md` exists and contains a "Phase Files" table
2. Every phase file referenced in the index exists in the output bundle
3. Phase numbers are contiguous (1, 2, 3, ..., N) with no gaps
4. All task IDs match `T<PP>.<TT>` format (zero-padded, 2-digit)
5. Every phase file starts with `# Phase N — <Name>` (level 1 heading, em-dash separator)
6. Every phase file ends with an end-of-phase checkpoint section
7. No phase file contains Deliverable Registry, Traceability Matrix, or template sections
8. The index contains literal phase filenames (e.g., `phase-1-tasklist.md`) in at least one table cell

If any check fails, fix it before returning the output.
```

**Target state (after patch):**
```markdown
## 8) Sprint Compatibility Self-Check (Mandatory)

Before finalizing output, verify all of the following:

1. `tasklist-index.md` exists and contains a "Phase Files" table
2. Every phase file referenced in the index exists in the output bundle
3. Phase numbers are contiguous (1, 2, 3, ..., N) with no gaps
4. All task IDs match `T<PP>.<TT>` format (zero-padded, 2-digit)
5. Every phase file starts with `# Phase N — <Name>` (level 1 heading, em-dash separator)
6. Every phase file ends with an end-of-phase checkpoint section
7. No phase file contains Deliverable Registry, Traceability Matrix, or template sections
8. The index contains literal phase filenames (e.g., `phase-1-tasklist.md`) in at least one table cell

### 8.1 Semantic Quality Gate (Pre-Write, Mandatory)

Before issuing any Write() call, additionally verify:

9. Every task in every phase file has non-empty values for: Effort, Risk, Tier, Confidence, and Verification Method.
10. All Deliverable IDs (D-####) are globally unique across the entire bundle — no duplicate D-#### values across different phases or tasks.
11. No task has a placeholder or empty description. Reject any task with description text of "TBD", "TODO", or a title-only entry with no body.
12. Every task has at least one assigned Roadmap Item ID (R-###). No orphan tasks without traceability.

If any check 1–12 fails, fix it before writing any output file.
```

**Risk level**: Low. Adds 4 checks as a named subsection of §8. Does not modify existing check text. The new subsection header `### 8.1 Semantic Quality Gate` provides CI-testability anchor.

**Diff size**: +12 lines

---

#### Integration Point 1B: §9 Final Output Constraint — add atomic write declaration

**Current §9 (lines 712–714):**
```markdown
## 9) Final Output Constraint

Return **only** the generated multi-file bundle (`tasklist-index.md` + `phase-N-tasklist.md` files). No preamble, no analysis, no mention of hidden proposals, no debate references. Write each file to its path under `TASKLIST_ROOT/`.
```

**Target state (after patch):**
```markdown
## 9) Final Output Constraint

Return **only** the generated multi-file bundle (`tasklist-index.md` + `phase-N-tasklist.md` files). No preamble, no analysis, no mention of hidden proposals, no debate references. Write each file to its path under `TASKLIST_ROOT/`.

**Write atomicity**: The generator validates the complete in-memory bundle against §8 (including §8.1) before issuing any Write() call. All files are written only after the full bundle passes validation. No partial bundle writes are permitted.
```

**Risk level**: Low. Additive declaration. Does not change any existing text. Commits to atomic write semantics explicitly.

**Diff size**: +3 lines

---

### File 2: `sc-tasklist-command-spec-v1.0.md` (PRD)

**Location**: `/config/workspace/SuperClaude_Framework/.dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md`

#### Integration Point 2A: §9 Acceptance Criteria — add criterion for semantic gate

**Current §9 Acceptance Criteria (last item is #7):**
```markdown
7. Functional parity: output is identical to running the v3.0 generator prompt manually
```

**Target state (add item 8):**
```markdown
7. Functional parity: output is identical to running the v3.0 generator prompt manually
8. Pre-write semantic quality gate passes before any file is written: all tasks have complete metadata fields, all Deliverable IDs are globally unique, no placeholder descriptions exist, and every task has at least one R-### reference.
```

**Risk level**: Low. Additive acceptance criterion. Does not modify existing criteria.

**Diff size**: +2 lines

---

#### Integration Point 2B: §10 Open Questions — resolve atomicity question

**Current §10 Open Questions** — no question about write atomicity exists today.

**Target state (add new question/resolution):**
```markdown
4. **Should Write() calls be atomic (all files after validation) or incremental (file by file)?**
   Resolution: Atomic. The §8.1 Semantic Quality Gate validates the full in-memory bundle before any Write() call. Incremental writing is prohibited to prevent partial bundle states.
```

**Risk level**: Low. Documents a design decision that affects future implementations.

**Diff size**: +4 lines

---

## Integration Sequence

Execute in this order to maintain consistency:

1. Patch `Tasklist-Generator-Prompt-v2.1-unified.md` §8 (add §8.1 checks 9–12)
2. Patch `Tasklist-Generator-Prompt-v2.1-unified.md` §9 (add atomic write declaration)
3. Patch `sc-tasklist-command-spec-v1.0.md` §9 (add acceptance criterion 8)
4. Patch `sc-tasklist-command-spec-v1.0.md` §10 (add atomicity resolution)
5. When SKILL.md is authored from the v3.0 generator, carry forward §8.1 and §9 atomic write declaration verbatim into SKILL.md §8 and §9.

---

## What NOT to change

- §8 checks 1–8 remain verbatim. No reordering, no wording changes.
- §7 Style Rules unchanged.
- §6A, §6B template content unchanged.
- §5 Enrichment algorithm unchanged (no behavioral generation changes).
- §4.5 Task Splitting algorithm unchanged (behavioral changes deferred to v1.1).
- No new top-level section (§7.5) created — §8.1 subsection is sufficient.

---

## Validation of this refactor plan

After applying the four patches, the following must be true:

| Verification | Method |
|---|---|
| §8 checks 1–8 unchanged | Text diff against original |
| §8.1 contains exactly checks 9–12 | Text diff |
| §9 contains atomic write declaration | Text diff |
| PRD §9 contains criterion 8 | Text diff |
| No check in §8.1 duplicates any check in §8 checks 1–8 | Manual review of diff-analysis.md overlap table |
| Semantic checks 9–12 do not include behavioral generation constraints | Verify against exclusion list in base-selection.md §4.2 |
| SKILL.md (when authored) carries forward §8.1 verbatim | Structural mapping table in sc-tasklist-command-spec-v1.0.md §6.2 |

