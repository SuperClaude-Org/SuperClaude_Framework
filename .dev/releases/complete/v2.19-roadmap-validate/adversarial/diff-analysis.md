# Diff Analysis: Spec-Fidelity Gap Analysis Comparison

## Metadata
- Generated: 2026-03-09
- Variants compared: 2
- Variant A: `spec-fidelity-gap-analysis-gpt.md` (634 lines, conversational briefing format)
- Variant B: `spec-fidelity-gap-analysis.md` (325 lines, structured markdown analysis)
- Total differences found: 26
- Categories: structural (4), content (11), contradictions (3), unique (11), shared assumptions (3 promoted)

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|------|-----------|-----------|----------|
| S-001 | Document format | Plain text with bold/indented section labels, no markdown headers | Proper markdown with ## headers, tables, code blocks, YAML-style metadata | Medium |
| S-002 | Hierarchy depth | Essentially flat (no heading hierarchy) | 3 levels (H2/H3/H4) | Medium |
| S-003 | Section ordering | problem → key insight → findings → existing mechanisms → solution directions → file refs → questions | problem → evidence (case study) → current inventory → gap map → solutions → file ref → decision framework | Low |
| S-004 | Use of tables | No tables | 8+ tables throughout | Low |

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|-------|-------------------|-------------------|----------|
| C-001 | Deviation quantification | 5 qualitative "high-signal" deviations (A-E) with file/line references | 29 total roadmap deviations (5 HIGH, 12 MEDIUM, 12 LOW) with severity breakdown + 15 tasklist + 1 implementation deviations | High |
| C-002 | Deviation tracking IDs | Letters (A-E, A-G) | Structured IDs (RD-001–RD-010, TD-001–TD-007) | Medium |
| C-003 | Adversarial debate verdicts | Not mentioned | Per-deviation verdict table with specific actions (Hybrid, Amend spec, etc.) | High |
| C-004 | Gate inventory detail | 4 files listed, ~10 lines of description | Gate-by-gate inventory with specific gate names, check/don't-check columns, `_cross_refs_resolve()` always-True finding | High |
| C-005 | Solution specificity | 3 conceptual gates (A/B/C) + normalized output contract | 4 solutions (A-D) with specific injection points, file names, function names, cost/value estimates | High |
| C-006 | Validate pipeline analysis | Brief mention of validate gates | Detailed coverage: validate gates, reflect prompt's 7 dimensions, critical observation that validation compares vs extraction.md not raw spec | High |
| C-007 | Sprint runner coverage | "Not the primary fault domain" (brief) | Specific file, checks performed, checks NOT performed | Medium |
| C-008 | Closing approach | 5 questions for future agents | Structured decision framework with trade-off table + "minimum viable fix" recommendation | Medium |
| C-009 | Root cause precision | "Lack of consistent blocking enforcement" | "Documented in skill reference files, not wired into the CLI executor" + traces actual auto-validation code path | Medium |
| C-010 | Dead code discovery | Not mentioned | `build_reflect_prompt` accepts 3 params never interpolated into prompt text | Medium |
| C-011 | Test file detail | Lists test files | Lists test files with test counts per file (22, 15, 20, 14, 15, 8, 2) | Low |

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|-------------------|-------------------|-------------------|--------|
| X-001 | Deviation count completeness | Presents 5 "high-signal" deviations as the core findings | Presents 29 total deviations, establishing the 5 as part of a much larger pattern | Medium |
| X-002 | Execution-layer spec validation | Explicitly states "Gate C: Execution validates against tasklist only" — checking against spec at this layer is wrong | Gap map includes "❌ No output↔spec check" for sprint runner, implying spec check is desirable | High |
| X-003 | Solution format | Proposes 6-field normalized output contract as the solution format | Does not propose a normalized contract; focuses on implementation approaches | Low |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---------|--------------|-----------------|
| U-001 | A | "Harness" conceptual definition section — precise definition of what a validation harness means in context | Medium |
| U-002 | A | Normalized output contract (6-field schema: source_pair, severity, deviation, evidence, likely_impact, recommended_correction) | High |
| U-003 | A | Explicit validation layering principle: "validate each artifact against its immediate upstream source of truth" | High |
| U-004 | A | 5 questions a future agent should start with | Medium |
| U-005 | B | Adversarial debate verdicts table per deviation, with specific actions taken | High |
| U-006 | B | Dead code discovery: `build_reflect_prompt` params never interpolated into prompt text | High |
| U-007 | B | `_cross_refs_resolve()` always returns True — cross-reference check is non-enforcing | High |
| U-008 | B | ASCII pipeline gap map visualization showing exactly where gaps exist | High |
| U-009 | B | Decision framework with trade-off table (prompt-based vs deterministic vs hybrid) | Medium |
| U-010 | B | Minimum viable fix recommendation section | Medium |
| U-011 | B | Cost/value assessments per solution ("~30-60s per run", "Would have caught all 5 HIGH-severity deviations") | Medium |

## Shared Assumptions

| # | Agreement Source | Assumption | Classification | Promoted |
|---|-----------------|------------|----------------|----------|
| A-001 | Both treat v2.19 case study as systemic | The v2.19-roadmap-validate deviations are representative of systemic pipeline behavior, not an isolated incident | UNSTATED | Yes |
| A-002 | Both extend existing infrastructure | Existing gate infrastructure is architecturally sound and needs extension, not replacement | UNSTATED | Yes |
| A-003 | Both propose LLM-based validation | Prompt-based (LLM) semantic validation is effective enough to reliably catch deviations at scale | UNSTATED (B) / STATED (A) | Yes |

*Non-promoted (STATED in both):*
- Correct validation model is "each artifact vs immediate upstream" (not every artifact vs spec)
- Sprint runner behavior is correct; problem is entirely upstream

## Summary
- Total structural differences: 4
- Total content differences: 11
- Total contradictions: 3
- Total unique contributions: 11
- Total shared assumptions surfaced: 5 (UNSTATED promoted: 3, STATED: 2)
- Highest-severity items: C-001, C-003, C-004, C-005, C-006, X-002
