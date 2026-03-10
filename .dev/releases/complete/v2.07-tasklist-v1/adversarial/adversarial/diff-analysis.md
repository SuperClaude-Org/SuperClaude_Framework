# Diff Analysis: Tasklist v1.0 Refactor Plan Comparison

## Metadata
- Generated: 2026-03-04T12:00:00Z
- Variants compared: 2
- Variant A: `refactor-plan-merged.md` (5 individual refactor plans merged, ~980 lines)
- Variant B: `tasklist-spec-integration-strategies.md` (post-debate integration strategies, ~226 lines)
- Total differences found: 28
- Categories: structural (6), content (10), contradictions (5), unique (7)
- Focus areas: overlap, contradictions, correctness, completeness, merge

---

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Document organization model | 5 separate refactor plan documents concatenated sequentially, each self-contained with own headers, risk tables, implementation orders | Single unified document with 5 numbered strategy sections under common Executive Summary and shared patch order | **High** |
| S-002 | Heading depth | Max depth H3 within each strategy section; H1 per strategy boundary | Max depth H3; single H1 for entire document | **Medium** |
| S-003 | Strategy naming convention | Uses original pre-debate names in titles (e.g., "Stage-Gated Generation Contract", "Self-Contained Task Item Quality Gate") with modifications noted in body | Uses post-debate renamed titles (e.g., "Stage Completion Reporting Contract", "Minimum Task Specificity Rule") with strikethrough of originals | **Medium** |
| S-004 | Debate context placement | Debate context absent from individual plans; each plan assumes verdict is known | Debate verdicts, rejected items, and key insights inline with each strategy | **Medium** |
| S-005 | Patch order section | Each strategy has its own implementation order; no unified cross-strategy sequence | Single "Revised Spec Patch Order" section at bottom ordering all 5 strategies with time estimates | **Low** |
| S-006 | v1.1 deferral tracking | Per-strategy deferral notes scattered across individual plans | Consolidated "v1.1 Deferred Items" table with source debate references | **Low** |

---

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Strategy 1 scope: halt-on-failure vs observability | Includes per-stage halt-on-failure gates with "must not advance to next stage" language (§4.3 replacement text, lines 73-76). Stage progression rule explicitly blocks advancement on validation failure. | Explicitly rejects halt-on-failure gates as "circular self-validation provides false confidence". Renames to "Stage Completion Reporting" — TodoWrite observability only, no gating. | **High** |
| C-002 | Strategy 1 per-stage validation criteria table | Includes detailed 6-row validation criteria table (lines 103-110) with specific criteria per stage (e.g., "T<PP>.<TT> IDs assigned with no collisions") | Does not include per-stage validation criteria table; describes stage reporting as "observational (debugging/progress); it does NOT gate advancement" | **High** |
| C-003 | Strategy 2 implementation detail | Full 5-patch implementation with exact replacement text for §5.4, §5.6, spec §5.4, spec §5.6, and strategies doc (lines 282-433) | Reduced to 2 minimal changes: passive Generation Notes + empty-file guard. Full fail-fast error format deferred to v1.1. | **High** |
| C-004 | Strategy 2 structured error format | Specifies exact deterministic error format (TASKLIST VALIDATION ERROR with Check/Expected/Received/Fallback/Action fields, lines 313-321) and two-class failure taxonomy | Does not include structured error format; says "Do NOT expand Boundaries (Will) with structured error claims — that's v1.1 scope" | **High** |
| C-005 | Strategy 3 standalone task requirement | 4-criterion standalone task requirement (named artifact, session-start executable, action verb + explicit object, no cross-task prose dependency) with §8.N self-check (lines 485-539) | 2-criterion minimum specificity rule (name specific artifact + concrete action verb). Rejects session-start executability and cross-task prose checks as too broad for v1.0. | **Medium** |
| C-006 | Strategy 4 near-field completion criterion | Adds "Near-Field Completion Criterion" requiring first Acceptance Criteria bullet to name specific verifiable output, with accepted/rejected form examples and non-invention constraint (lines 683-717) | Describes tightening existing Acceptance Criteria fields with artifact references and tier-proportional enforcement (STRICT/STANDARD/LIGHT/EXEMPT) but no near-field specificity rule | **Medium** |
| C-007 | Strategy 5 check numbering | Adds checks 9-12 as §8.1 "Semantic Quality Gate" subsection (metadata completeness, D-#### uniqueness, no placeholders, R-### traceability) (lines 864-874) | Adds checks 13-17 (task count bounds, clarification adjacency, circular dependency detection, XL splitting, confidence bar format) (lines 163-171) | **High** |
| C-008 | Strategy 5 atomic write declaration | Adds explicit atomic write declaration to §9: "validates complete in-memory bundle against §8 before any Write() call" (lines 893-898) | Does not mention write atomicity | **Medium** |
| C-009 | Effort estimates | Per-strategy estimates embedded (Strategy 2: "1.5-2 hours", Strategy 4: "1.5-2 hours") but no unified total | Unified total: "~3 hours (down from ~8.5 hours pre-debate)" with per-strategy breakdown (45min, 30min, 1hr, 30min, 30min) | **Low** |
| C-010 | Token cost awareness | No mention of token cost impact | Explicitly notes "~150 additional tokens in SKILL.md" for Strategy 5 and "zero additional token cost" for Strategies 3 and 4 | **Low** |

---

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Strategy 1: Should stages gate advancement? | **YES** — "each stage must complete and pass its validation before advancing to the next stage. Do not proceed to Stage N+1 if Stage N validation criteria are not satisfied." (lines 73-76, 112-114) | **NO** — "Stage reporting is observational (debugging/progress); it does NOT gate advancement." Rejects halt-on-failure as "circular self-validation" (lines 42-44, 49) | **High** — Fundamental incompatibility: one variant blocks pipeline progression, the other explicitly prohibits it |
| X-002 | Strategy 2: Should structured error format be in v1.0? | **YES** — Full error format specified with Check/Expected/Received/Fallback/Action fields and two-class failure taxonomy (lines 299-322) | **NO** — "Do NOT expand Boundaries (Will) with structured error claims — that's v1.1 scope" (line 82). Only empty-file guard + Generation Notes for v1.0. | **High** — Variant A includes the full error format; Variant B explicitly defers it |
| X-003 | Strategy 3: How many standalone criteria? | **4 criteria** — Named artifact, session-start executable, action verb + object, no cross-task dependency (lines 488-505) | **2 criteria** — Specific artifact + concrete action verb only. Session-start and cross-task checks "too broad for v1.0 parity" (lines 98-99, 103-106) | **Medium** — Variant A is more comprehensive; Variant B is more conservative |
| X-004 | Strategy 5: Which self-check numbers? | **Checks 9-12** under §8.1 (metadata completeness, D-#### uniqueness, no placeholders, R-### traceability) (lines 864-874) | **Checks 13-17** (task count bounds, clarification adjacency, circular deps, XL splitting, confidence bar format) (lines 163-171) | **High** — Completely different check sets with different numbering. These are not conflicting checks but non-overlapping sets that need reconciliation. |
| X-005 | Strategy 4 §9 acceptance criterion numbering | Adds as "criterion 8" (line 548, 671) | Adds acceptance criteria quality rules as "§5.7" (new section, line 142) and §8.1 Check #13 (line 147) | **Medium** — Different structural placement for acceptance criteria enforcement |

---

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|-------------|-----------------|
| U-001 | A | Exact patch text with current/replacement pairs for every spec location (5 strategies × multiple patches = ~15 patch blocks) | **High** — Implementation-ready; eliminates ambiguity about what text to write |
| U-002 | A | Per-strategy risk assessment tables with Probability/Severity/Mitigation columns | **Medium** — Useful for implementation planning |
| U-003 | A | Non-invention constraint for Strategy 4 ("derive from roadmap; use Manual check fallback") preventing generator hallucination (lines 713-716) | **High** — Addresses a real hallucination risk not covered by Variant B |
| U-004 | A | Atomic write declaration for Strategy 5 with §10 Open Questions resolution (lines 893-937) | **Medium** — Design decision that affects implementation correctness |
| U-005 | B | Consolidated debate verdict summary table with all 5 strategies' outcomes (lines 16-22) | **High** — Provides decision provenance missing from Variant A |
| U-006 | B | "Additional Valuable Context" section with keep-as-is items and risks to address (lines 191-202) | **Medium** — Meta-guidance for implementers |
| U-007 | B | Token cost awareness annotations per strategy | **Low** — Useful but not critical |

---

## Summary
- Total structural differences: 6
- Total content differences: 10
- Total contradictions: 5
- Total unique contributions: 7
- Highest-severity items: X-001, X-002, X-004, C-001, C-002, C-003, C-004, C-007, S-001
- Similarity assessment: Variants share the same 5-strategy subject matter but differ fundamentally in scope (Variant A pre-debate full implementation vs Variant B post-debate narrowed scope) — well above 10% difference threshold; full debate warranted
