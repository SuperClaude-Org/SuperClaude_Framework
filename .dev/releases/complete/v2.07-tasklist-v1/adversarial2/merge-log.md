# Merge Log: Tasklist Generator Refactor Proposal

**Merge date**: 2026-03-04
**Base variant**: Variant A (`variant-1-opus-original.md`)
**Source variant**: Variant B (`variant-2-haiku-original.md`)
**Plan**: `refactor-plan.md` (4 planned changes)

---

## Change #1: Add Target Directory Layout

- **Status**: Applied
- **Source**: Variant B, lines 118-130 ("Recommended Target Layout")
- **Location in merged document**: After R-05 (File Emission Rules), as a new subsection "Target Directory Layout"
- **Before**: R-05 ended with the "Content boundary" rule; R-06 followed immediately
- **After**: A new `#### Target Directory Layout` subsection with the `TASKLIST_ROOT/` directory tree is inserted between R-05 and R-06
- **Provenance annotation**: `<!-- Source: Variant B, lines 118-130 — merged per Change #1 -->`
- **Validation**: Directory tree matches Variant B exactly. Subsection integrates cleanly under R-05 without disrupting heading hierarchy.

---

## Change #2: Strengthen Canonical Naming Directive

- **Status**: Applied
- **Source**: Variant B, lines 67-72 (item 3, "Standardize filename policy")
- **Location in merged document**: R-05 "File Emission Rules", within the **Naming** paragraph
- **Before**: "Phase files MUST use the `phase-N-tasklist.md` convention (primary Sprint CLI convention)."
- **After**: "Phase files MUST use the `phase-N-tasklist.md` convention (primary Sprint CLI convention). Do not emit mixed aliases unless explicitly requested."
- **Provenance annotation**: `<!-- Source: Variant B, item 3, lines 67-72 — merged per Change #2 -->`
- **Validation**: Single sentence addition. No conflict with existing content. Strengthens the directive without removing any accepted conventions documented in Part 1.1.

---

## Change #3: Tighten Self-Check Gate Language

- **Status**: Applied
- **Source**: Variant B, lines 107-113 (item 10) used as editorial reference; base checks preserved
- **Location in merged document**: R-06 "Sprint Compatibility Self-Check"
- **Before** (selected wording changes):
  - Item 4: "All task IDs match `T<PP>.<TT>` format (2-digit zero-padded)"
  - Item 5: "Every phase file starts with `# Phase N — <Name>` (level 1 heading)"
  - Item 6: "Every phase file has an end-of-phase checkpoint"
  - Opening: "Before finalizing output, verify:"
- **After**:
  - Item 4: "All task IDs match `T<PP>.<TT>` format (zero-padded, 2-digit)" -- reordered for directness
  - Item 5: "Every phase file starts with `# Phase N — <Name>` (level 1 heading, em-dash separator)" -- added explicit separator mention
  - Item 6: "Every phase file ends with an end-of-phase checkpoint section" -- more precise location language
  - Opening: "Before finalizing output, verify all of the following:" -- stronger directive
- **All 8 checks preserved**: Items 1-8 all present in merged output
- **Provenance annotation**: `<!-- Source: Base (original, modified) — wording refined per Change #3 -->`
- **Validation**: All 8 checks present. Wording is tighter. No checks removed or reordered.

---

## Change #4: Conciseness Editorial Pass

- **Status**: Applied
- **Source**: Variant B overall style (U-007 from debate scoring)
- **Location in merged document**: Throughout, primarily Parts 1-3
- **Changes applied**:
  - Part 1.1: Removed "TASKLIST_ROOT-relative placeholders that won't match the regex" (redundant given the regex is shown)
  - Part 1.2: Condensed "**Generator requirement**:" paragraph into two direct sentences
  - Part 1.3: Changed "**Critical implications for generator**" to "**Implications for the generator**" and tightened bullet prose
  - Part 1.5: Condensed the generator requirement into a single direct sentence
  - Part 3 (Gap Analysis): Removed "**Current**" label repetition where obvious from context; tightened impact statements
  - Part 6 (Compatibility Matrix): Replaced checkmark/cross symbols with "Yes/No/Required/Compatible" for consistency
  - Part 8: Changed "they're useful" to "they are useful" for consistency; minor prose tightening
- **Substantive content preserved**: All code excerpts, tables, templates, task field taxonomies, migration plan, compatibility matrix, and open questions remain intact
- **Provenance annotation**: `<!-- Source: Base (original, modified) — conciseness pass per Change #4 -->` (placed at Part 1 opening)
- **Validation**: No substantive content removed. All code blocks, tables, and templates present. Document reads more directly without losing information.

---

## Summary

| Change | Status | Risk Realized | Notes |
|--------|--------|---------------|-------|
| #1 Target Directory Layout | Applied | None | Clean additive insertion |
| #2 Canonical Naming Directive | Applied | None | Single sentence addition |
| #3 Self-Check Gate Language | Applied | None | 8/8 checks preserved, wording tightened |
| #4 Conciseness Editorial Pass | Applied | None | Prose tightened, no content removed |

**Overall merge result**: All 4 planned changes applied successfully. No changes were skipped or escalated. Structural integrity of the base document is preserved (8 parts, heading hierarchy, all templates and code excerpts intact).
