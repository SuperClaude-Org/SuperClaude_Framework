# Refactoring Plan: Merged Tasklist Generator Refactor Proposal

## Overview
- **Base variant**: Variant A (tasklist-generator-v3-refactor-proposal.md)
- **Incorporated from**: Variant B (tasklist-generator-refactor-notes-for-sprint-and-task-unified.md)
- **Planned changes**: 4
- **Risk**: Low (all changes are additive or editorial)

---

## Planned Changes

### Change #1: Add Target Directory Layout
- **Source**: Variant B, lines 118-130 ("Recommended Target Layout")
- **Target location**: Variant A, after Part 4 R-05 (File Emission Rules), before R-06
- **Integration approach**: Insert new subsection "Target Directory Layout" with B's directory tree
- **Rationale**: A's templates specify file contents but lack a holistic directory view. B's tree diagram provides at-a-glance structural understanding. Debate evidence: A advocate conceded "Missing directory-level context" in Round 1 concessions.
- **Risk**: Low (purely additive)

### Change #2: Strengthen Canonical Naming Directive
- **Source**: Variant B, lines 67-72 (item 3, "Standardize filename policy")
- **Target location**: Variant A, Part 4 R-05 (File Emission Rules), naming subsection
- **Integration approach**: Add B's explicit anti-alias language: "Do not emit mixed aliases unless explicitly requested"
- **Rationale**: A documents 4 accepted conventions (Part 1.1) but the generator should output only the canonical one. B's directive is sharper. Debate evidence: A advocate accepted this as reasonable in Round 2.
- **Risk**: Low (editorial strengthening)

### Change #3: Tighten Self-Check Gate Language
- **Source**: Variant B, lines 107-113 (item 10, "Sprint Compatibility Check")
- **Target location**: Variant A, Part 4 R-06 (Sprint Compatibility Self-Check)
- **Integration approach**: Review B's 5-check phrasing against A's 8 checks; adopt any crisper wording while keeping A's additional checks
- **Rationale**: B's check phrasing is slightly more direct. A's additional checks (items 7-8: no registries in phase files, literal filenames in index) should be preserved. Debate evidence: Both advocates rated U-006 as a draw.
- **Risk**: Low (editorial refinement)

### Change #4: Conciseness Editorial Pass
- **Source**: Variant B overall style (U-007)
- **Target location**: Variant A throughout
- **Integration approach**: Reduce verbosity in Part 1 code evidence sections — keep code excerpts but tighten surrounding prose. Remove redundant explanations where the code/table speaks for itself.
- **Rationale**: Both advocates agreed A could benefit from tighter language. The opus advocate conceded "Length as liability" and suggested "add an index, not remove content." The haiku advocate proposed "layered format."
- **Risk**: Low (editorial — no content removal, only prose tightening)

---

## Changes NOT Being Made

### Rejected: Use Variant B as base
- **Diff point**: Base selection
- **Variant B approach**: Start from B's 150-line concise format and graft A's depth
- **Rationale**: A advocate correctly argued that starting from the more complete document and trimming is safer than backfilling. Variant A contains all of B's content plus templates, field taxonomies, migration plan, and compatibility matrix. B's approach would require recreating these from scratch, risking omission errors. Combined score margin of 25.4% confirms A as base.

### Rejected: Embed completion protocol in phase files (B item 8)
- **Diff point**: X-001
- **Variant B approach**: Add explicit phase completion protocol in every phase file
- **Rationale**: Sprint CLI executor (`process.py:build_prompt`) already injects a complete completion protocol. B advocate conceded this is a contradiction (Major concession #3). Embedding a second copy creates duplication and potential conflicts.

### Rejected: Flatten document structure (S-001 through S-003)
- **Diff point**: S-001, S-002, S-003
- **Variant B approach**: Flat H2 structure with numbered lists
- **Rationale**: A's hierarchical structure (8 parts, H3/H4 subsections) is appropriate for a process specification document of this depth. The haiku advocate's structural wins are for "execution ergonomics" of shorter documents; at A's depth, hierarchy aids navigation.

---

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Target layout | Low | Additive section | Remove section |
| #2 Naming directive | Low | 1-2 sentence edit | Revert sentence |
| #3 Self-check language | Low | Wording refinement | Revert wording |
| #4 Conciseness pass | Low | Prose tightening | Git diff revert |

---

## Review Status
- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-04
