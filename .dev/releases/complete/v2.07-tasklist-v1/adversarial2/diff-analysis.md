# Diff Analysis: Tasklist Generator Refactor Proposals

## Metadata
- Generated: 2026-03-04
- Variants compared: 2
- Variant A: `tasklist-generator-v3-refactor-proposal.md` (opus, ~450 lines)
- Variant B: `tasklist-generator-refactor-notes-for-sprint-and-task-unified.md` (haiku, ~150 lines)
- Total differences found: 19
- Categories: structural (4), content (7), contradictions (1), unique contributions (7)

---

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Document organization | 8 parts with hierarchical numbering (Part 1-8), deep nesting (H2→H3→H4) | Flat structure: 6 H2 sections with numbered lists inside | Medium |
| S-002 | Heading depth | Max depth H4 (e.g., `### 1.1 Phase File Discovery`) | Max depth H2 (all content in numbered lists under H2) | Low |
| S-003 | Section ordering | Contract-first: Sprint CLI contract → sc:task-unified contract → Gap analysis → Refactoring spec → Migration path | Problem-first: Ground-truth contracts → Current mismatch → Required refactor → Target layout → Prompt changes | Medium |
| S-004 | Document length | ~450 lines with code blocks, tables, templates | ~150 lines, concise bullet-point style | Medium |

---

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Sprint CLI contract depth | Deep code-level analysis: regex patterns quoted verbatim, discovery strategy detailed, prompt template reproduced, result parsing priority chain, monitor regex patterns | Brief code references: 6 line citations pointing to source files without quoting code | High |
| C-002 | sc:task-unified analysis | Dedicated Part 2 covering classification layer, execution layer, field taxonomy (required/important/metadata) | Not addressed — focuses solely on Sprint CLI alignment and basic tier mention in item 7 | High |
| C-003 | Gap identification | 7 explicitly named and severity-rated gaps (GAP-01 through GAP-07) with CRITICAL/HIGH/MEDIUM ratings | 10 numbered refactor items without severity ratings — gaps implied by refactor items | Medium |
| C-004 | Template specifications | Complete Index File Template and Phase File Template with full markdown examples | "Recommended Target Layout" showing directory tree only, no file content templates | High |
| C-005 | Refactoring specificity | 6 named specs (R-01 through R-06) mapping to exact generator prompt sections (§1, §3, §6, §12) | 5 "Suggested Prompt Section Changes" referencing Section 1/6/12 without exact replacement text | Medium |
| C-006 | Migration path | 3-phase migration plan with effort estimates (40%/30%/15%) and testing strategy | No migration path or phasing — presented as a flat list of changes | Medium |
| C-007 | Compatibility matrix | Explicit table comparing v2.1/v2.2 vs v3.0 vs Sprint CLI vs sc:task-unified across 11 features | No compatibility analysis | Medium |

---

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Completion protocol in phase files | "Phase files should NOT include completion instructions (they'd be redundant)" — executor injects its own protocol | Item 8: "Add explicit phase completion protocol in every phase file" including YAML status, task table, EXIT_RECOMMENDATION | High |

**Analysis**: This is the only genuine contradiction. Variant A argues the executor already injects the completion protocol via `build_prompt()`, so embedding it in phase files is redundant and could conflict. Variant B proposes each phase file should include its own completion instructions. The Sprint CLI code (`process.py:build_prompt`) confirms the executor does inject completion protocol — supporting Variant A's position. However, Variant B's intent may be about ensuring Claude knows what output format is expected regardless of how the prompt is assembled.

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | **Result parsing priority chain** (7-level status determination from executor.py) — documents how the executor reads phase results, which informs what phase files must enable Claude to produce | High |
| U-002 | A | **Monitor expectations** (task ID regex, tool patterns, file change patterns) — documents runtime signals the TUI tracks | Medium |
| U-003 | A | **sc:task-unified field taxonomy** — categorizes all task fields as required/important/metadata based on what actually drives execution behavior | High |
| U-004 | A | **Open Questions section** — raises 4 unresolved design questions (single invocation vs iterative, inline checkpoints, full task summary in index, cross-phase dependencies) | Medium |
| U-005 | A | **Compatibility matrix** — side-by-side feature comparison showing which features are required/compatible/missing | Medium |
| U-006 | B | **Sprint Compatibility Self-Check gate** — proposes a validation checklist the generator runs before finalizing output (8 checks: index exists, phase files exist, contiguous numbering, valid task IDs, heading format, end-of-phase checkpoint, no registries in phase files, literal filenames in index) | High |
| U-007 | B | **Conciseness as a design virtue** — the entire document is ~150 lines, proving that the refactoring spec can be communicated efficiently without verbose templates | Low |

---

## Summary
- Total structural differences: 4
- Total content differences: 7
- Total contradictions: 1
- Total unique contributions: 7
- Highest-severity items: C-001 (Sprint CLI depth), C-002 (sc:task-unified coverage), C-004 (templates), X-001 (completion protocol)
