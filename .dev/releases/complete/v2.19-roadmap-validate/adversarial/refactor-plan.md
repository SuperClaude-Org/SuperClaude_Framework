# Refactoring Plan

## Overview
- **Base**: Variant B (spec-fidelity-gap-analysis.md)
- **Incorporated from**: Variant A (spec-fidelity-gap-analysis-gpt.md)
- **Changes planned**: 5
- **Changes rejected**: 2
- **Overall risk**: Low

## Planned Changes

### Change #1: Add Validation Layering Principle Section
- **Source**: Variant A, lines 36-47 ("Correct validation layering")
- **Target**: Insert as new Section 1.1 under "Problem Statement" in base
- **Rationale**: Debate point X-002 — Variant A won at 85% confidence. Both advocates agreed A articulates this principle more clearly. The explicit "Not:" counter-pattern prevents misinterpretation of the gap map's sprint runner entries.
- **Integration approach**: Insert new H3 subsection with the layered validation model and anti-pattern
- **Risk**: Low (additive — clarifies existing content, does not modify)

### Change #2: Add Normalized Output Contract
- **Source**: Variant A, lines 512-528 ("Suggested normalized output contract")
- **Target**: Insert as new Section 5.5 "Normalized Deviation Report Contract" after Solution D
- **Rationale**: Debate point X-003 — Variant A won at 80% confidence. B's advocate conceded this is "a concrete, reusable schema that Variant B does not propose." Without a shared output format, each gate produces ad-hoc output.
- **Integration approach**: Insert 6-field schema (source_pair, severity, deviation, evidence, likely_impact, recommended_correction) as a specification subsection
- **Risk**: Low (additive)

### Change #3: Add Harness Definition
- **Source**: Variant A, lines 418-431 ("Harness: how it should be understood here")
- **Target**: Insert as introductory paragraph in Section 5 "Proposed Solutions"
- **Rationale**: Unique contribution U-001 (Medium value). B's advocate conceded "the harness definition could frame B's solutions." Provides conceptual grounding for the 4 solutions.
- **Integration approach**: Insert 2-paragraph definition at start of Solutions section
- **Risk**: Low (additive framing)

### Change #4: Add Advisory-vs-Blocking Root Cause Insight
- **Source**: Variant A, lines 348-363 (citing SKILL.md:864-868)
- **Target**: Integrate into Section 3.6 "Documented But Not Wired" or as new subsection
- **Rationale**: B's advocate conceded this is "a sharper framing of the root cause than Variant B's more distributed treatment." The specific citation that semantic gates are advisory while structural gates are blocking directly explains WHY the existing documented validation doesn't catch drift.
- **Integration approach**: Add paragraph with SKILL.md:864-868 citation to Section 3.6
- **Risk**: Low (strengthens existing section)

### Change #5: Add Future Agent Onboarding Questions
- **Source**: Variant A, lines 607-619 ("Questions a future agent should start with")
- **Target**: Insert as new Section 8 "Diagnostic Questions for Follow-Up"
- **Rationale**: Unique contribution U-004 (Medium value). While B answers most of these questions, explicitly listing them as a checklist provides a structured entry point for agents picking up this work. The questions are diagnostic, not redundant with B's answers.
- **Integration approach**: Insert numbered question list as final section
- **Risk**: Low (additive)

## Changes NOT Being Made

### Rejected: Replace B's gap map sprint runner entry
- **Diff point**: X-002 (partially)
- **Non-base approach**: A would remove "No output↔spec check" from the gap map
- **Rationale**: Rather than modifying B's gap map, Change #1 adds the layering principle which contextualizes the gap map correctly. The gap map documents what is absent (completeness); the principle clarifies what should be built (architecture). Both can coexist.

### Rejected: Replace B's deviation list with A's qualitative high-signal deviations
- **Diff point**: C-001
- **Non-base approach**: A presents 5 qualitative deviations (A-E) with file/line references
- **Rationale**: B's quantified deviation inventory (29/15/1 with severity tiers) won at 90% confidence. A's advocate explicitly conceded B's counts are "more rigorous." A's qualitative approach is a subset of B's comprehensive treatment.

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Validation layering | Low | Adds architectural principle | Remove section |
| #2 Output contract | Low | Adds reusable schema | Remove section |
| #3 Harness definition | Low | Adds conceptual framing | Remove paragraphs |
| #4 Advisory-vs-blocking | Low | Strengthens root cause analysis | Remove paragraph |
| #5 Onboarding questions | Low | Adds follow-up structure | Remove section |

## Review Status
- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-09
