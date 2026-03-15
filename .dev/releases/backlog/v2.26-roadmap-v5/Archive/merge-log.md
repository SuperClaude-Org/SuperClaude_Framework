# Merge Log: v2.25 Deviation-Aware Pipeline Spec

**Merge date**: 2026-03-13
**Base variant**: `variant-1-opus-architect-A.md` (Variant A, Incremental Refactor)
**Refactoring plan**: `refactor-plan.md` (6 planned changes from Variant B)
**Output**: `v2.25-spec-merged.md`

---

## Summary

| Metric | Value |
|--------|-------|
| Total planned changes | 6 |
| Applied | 6 |
| Skipped | 0 |
| Failed | 0 |

---

## Change Log

### Change #1: Adopt "UNCLASSIFIED" default for Finding.deviation_class

- **Status**: APPLIED
- **Source**: Variant B, Section 7.1
- **Target section**: 7.1 (Finding Model Extension)
- **Before**: `deviation_class: str = ""` with `VALID_DEVIATION_CLASSES = {"SLIP", "INTENTIONAL", "AMBIGUOUS", "PRE_APPROVED", ""}`. `__post_init__` used conditional `if self.deviation_class and` check. Docstring referenced `""` as valid.
- **After**: `deviation_class: str = "UNCLASSIFIED"` with `VALID_DEVIATION_CLASSES = {"SLIP", "INTENTIONAL", "AMBIGUOUS", "PRE_APPROVED", "UNCLASSIFIED"}`. `__post_init__` always validates (no conditional). Docstring updated. Section 14.1 backward compatibility text updated to reference `"UNCLASSIFIED"`. Risk R-8 description updated.
- **Validation**: `UNCLASSIFIED` appears in `VALID_DEVIATION_CLASSES`, `__post_init__` unconditionally validates, Finding docstring updated, Section 14.1 references `"UNCLASSIFIED"`.

### Change #2: Add backward compatibility section depth

- **Status**: APPLIED
- **Source**: Variant B, Section 13 (Backward Compatibility)
- **Target section**: 14 (Backward Compatibility)
- **Before**: Section 14 had 4 subsections (14.1-14.4).
- **After**: Section 14 has 6 subsections (14.1-14.6). Added 14.5 (Sprint Pipeline) confirming sprint pipeline is unaffected, and 14.6 (Pipeline Executor) confirming generic pipeline layer is unchanged.
- **Validation**: Both subsections present with correct content. No structural breaks in heading hierarchy.

### Change #3: Add appendices for quick reference

- **Status**: APPLIED
- **Source**: Variant B, Appendices A-C
- **Target section**: After Section 15
- **Before**: Document ended at Section 15.2 (Non-Functional success criteria).
- **After**: Three appendices added: Appendix A (Type Signature Summary with Finding model, gate definitions, prompt builders, semantic checks, utility functions), Appendix B (Gate Definitions Summary table with all 12 gates), Appendix C (Code References with source files, potentially modified files, and test files). Appendix A reflects the `"UNCLASSIFIED"` default from Change #1. Appendix B reflects the `validation_complete_true` check from Change #6.
- **Validation**: All three appendices present. Content is consistent with spec body sections.

### Change #4: Improve terminal halt formatting

- **Status**: APPLIED
- **Source**: Variant B, Section 6.4
- **Target section**: 8.5 (Terminal Halt Output)
- **Before**: `_print_terminal_halt()` had a generic format without per-finding details. It listed failed count but did not enumerate individual unfixed findings.
- **After**: `_print_terminal_halt()` now reads `unfixed_details` from certify state and prints per-finding ID and description in a bulleted list under "Unfixed findings:".
- **Validation**: Function signature unchanged. New lines for `unfixed_details` iteration present. Output format is more actionable.

### Change #5: Note LoopStep as v2.26 consideration

- **Status**: APPLIED
- **Source**: Variant B, Section 5 (LoopStep Primitive)
- **Target section**: 13 (Open Questions Resolved), "Open Questions Deferred" table
- **Before**: Deferred table had 3 entries (OQ-8, OQ-9, OQ-10).
- **After**: Deferred table has 4 entries. Added OQ-11: "Should a LoopStep primitive replace `--resume` for remediate-certify? Deferred to v2.26." with reference to Variant B and the specific files (`pipeline/models.py`, `pipeline/executor.py`).
- **Validation**: OQ-11 present in deferred table. Content references Variant B explicitly. Does not commit to implementation.

### Change #6: Add `_validation_complete_true` to DEVIATION_ANALYSIS_GATE

- **Status**: APPLIED
- **Source**: Variant B, Section 4.5
- **Target section**: 5.5 (Gate Definition), 5.4 (Output Format)
- **Before**: `DEVIATION_ANALYSIS_GATE` had 6 required frontmatter fields and 1 semantic check (`no_ambiguous_deviations`). Output format in 5.4 did not include `validation_complete`.
- **After**: Gate has 7 required frontmatter fields (added `"validation_complete"`). New `_validation_complete_true()` function added. Gate has 2 semantic checks (`no_ambiguous_deviations` + `validation_complete_true`). Section 5.4 output format now includes `validation_complete: true` in frontmatter example.
- **Validation**: `validation_complete` in required fields list. `_validation_complete_true` function present with correct logic. SemanticCheck entry present with failure message. Output format updated.

---

## Provenance Annotations

HTML comment provenance tags were added throughout the merged document:

| Tag | Sections |
|-----|----------|
| `<!-- Source: Base (original) -->` | 1, 2, 3, 4, 6, 8 (partial), 9, 10, 11, 12, 15 |
| `<!-- Source: Variant B, Change #1 -->` | 7.1, 14.1 |
| `<!-- Source: Variant B, Change #2 -->` | 14.5, 14.6 |
| `<!-- Source: Variant B, Change #3 -->` | Appendices A, B, C |
| `<!-- Source: Variant B, Change #4 -->` | 8.5 |
| `<!-- Source: Variant B, Change #5 -->` | 13 (OQ-11 row) |
| `<!-- Source: Variant B, Change #6 -->` | 5.4, 5.5 |

---

## Structural Integrity Check

- [x] Heading hierarchy: H1 > H2 > H3 maintained throughout
- [x] Section numbering: 1-15 + Appendices A-C, sequential, no gaps
- [x] Internal cross-references: Section references in body text resolve correctly
- [x] Code block consistency: All Python code blocks use ```python fencing
- [x] Table formatting: All tables have header separator rows
- [x] Frontmatter: YAML frontmatter updated with `version: "2.25.0-merged"`, `variant: merged`

## Contradiction Re-scan

- [x] R-8 description updated to match Change #1 (`"UNCLASSIFIED"` default, not empty string)
- [x] Section 14.1 updated to match Change #1 (references `"UNCLASSIFIED"`)
- [x] Appendix A Finding model reflects `"UNCLASSIFIED"` default
- [x] Appendix B gate table reflects `validation_complete_true` check from Change #6
- [x] No contradictions found between base content and incorporated changes
