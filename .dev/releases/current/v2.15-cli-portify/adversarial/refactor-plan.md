# Refactoring Plan

## Overview

- **Base variant**: Variant B (haiku:analyzer) -- score 0.877
- **Incorporated from**: Variant A (opus:architect)
- **Total planned changes**: 7
- **Risk summary**: 2 Low, 4 Medium, 1 High

---

## Planned Changes

### Change #1: Add Traceability Matrix
- **Source**: Variant A, Section 11.3
- **Target**: Insert as new section before Appendix A in base
- **Rationale**: B advocate fully conceded this gap in Round 2. Traceability matrix maps Spec Finding -> Root Cause -> Solution -> PR, providing end-to-end requirement traceability. Rated as "most valuable single artifact for implementers" by both advocates.
- **Integration approach**: Insert — add as new "Appendix D: Traceability Matrix" (renamed from A's section 11.3)
- **Risk**: Low (additive, no existing content modified)

### Change #2: Add Critical Code Locations Table
- **Source**: Variant A, Section 11.2
- **Target**: Integrate into base's Appendix C (File Reference Index)
- **Rationale**: A's consolidated RC -> File:Line -> Code Pattern table provides compact implementation reference. A advocate demonstrated its value for quick navigation during implementation. Complements B's more detailed per-file line ranges.
- **Integration approach**: Append — add as subsection within Appendix C
- **Risk**: Low (additive, enhances existing content)

### Change #3: Fix 4-PR/3-PR Inconsistency
- **Source**: Both advocates agreed this is a factual error in B
- **Target**: Base Section 1 (Abstract) — change "four-PR" to "three-PR" (with two deferred solutions)
- **Rationale**: B advocate conceded in Round 2. Abstract says "four-PR remediation sequence" but body defines 3 PRs + Deferred. Use A's consistent framing.
- **Integration approach**: Replace — correct the abstract wording
- **Risk**: Low (editorial fix)

### Change #4: Add Release Directory References
- **Source**: Variant A, Section 10.1
- **Target**: Integrate into base's Section 6.2 (PR Implementation Sequence)
- **Rationale**: A's operational context — pre-created directories with version labels — provides immediate implementation scaffolding. B omits this actionable workspace information.
- **Integration approach**: Append — add directory references to each PR entry
- **Risk**: Low (additive)

### Change #5: Resolve Ranking/Sequencing Tension
- **Source**: Debate evidence (Round 2, A advocate new evidence point 3)
- **Target**: Base Section 5.5.2 (Solution Consensus) and Section 6.2 (PR Sequence)
- **Rationale**: S6 ranked #1 but placed in PR2, not PR1. Need explicit justification. The pragmatist debater's argument (Sec 5.4.3) provides the rationale: quick wins ship first because they're low-effort, high-impact, and collectively address 70-80% of failures; S6 follows because it requires careful testing.
- **Integration approach**: Restructure — add a "Sequencing Rationale" paragraph explaining why implementation order differs from severity ranking
- **Risk**: Medium (modifies narrative logic)

### Change #6: Add Scope Provenance for SV Registry and GAP Table
- **Source**: Debate evidence (Round 2, B advocate concession on criticism 1)
- **Target**: Base Section 3.5 and Section 3.6 headers
- **Rationale**: B advocate conceded the provenance gap — SV registry and GAP table are not listed in the 5-workstream timeline. Add a brief provenance note explaining these are synthesis artifacts derived from WS-1 findings, not independent workstreams.
- **Integration approach**: Insert — add provenance note at top of each section
- **Risk**: Medium (modifies existing section framing)

### Change #7: Add Invariant Probe Warnings to Remediation Plan
- **Source**: Invariant probe findings (INV-002, INV-006, INV-007)
- **Target**: Base Section 6.2 (PR Implementation Sequence)
- **Rationale**: Three MEDIUM-severity implementation considerations identified during adversarial debate that neither variant addressed: sanitizer/horizontal-rule ambiguity, S4+S2 interaction effect, and S6 cwd/path interaction.
- **Integration approach**: Insert — add "Implementation Considerations" subsection after PR sequence
- **Risk**: Medium (new content not from either variant)

---

## Changes NOT Being Made

| Diff Point | Non-base Approach (Variant A) | Rationale for Keeping Base (Variant B) |
|------------|------------------------------|---------------------------------------|
| S-001 (organization) | Flat numbered sections | B's Part-based grouping provides better thematic organization; flat structure advantage is for consolidation (which this merge completes) |
| S-002 (opening) | Executive Summary narrative | B's Abstract + Timeline provides richer context; both advocates considered B slightly superior here |
| C-007 (debate structure) | "4 analysis agents" generic description | B's named debater positions (Architect, Reliability Engineer, Pragmatist) provide clearer debate lineage; A advocate conceded this |
| C-008 (solution depth) | Shorter code snippets | B's fuller code examples are more useful for implementation; the "premature commitment" concern applies only to ~40% per B advocate's Round 2 counter |
| C-009 (PR labels) | Version-labeled PRs (v2.15, etc.) | Changed approach: incorporate A's version labels into B's PR entries (covered by Change #4) |
| C-011 (check count) | 30 checks | Unresolved (30 vs 29) — neither variant provided definitive evidence. Keeping B's 29 as-is with a note that counting may vary by methodology |

---

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|----------|
| #1 Add traceability matrix | Low | Additive only | Remove appendix |
| #2 Add code locations table | Low | Additive only | Remove subsection |
| #3 Fix 4-PR/3-PR | Low | Single word change | Revert word |
| #4 Add release directories | Low | Additive only | Remove references |
| #5 Resolve ranking/sequencing | Medium | Modifies narrative coherence | Remove paragraph |
| #6 Add provenance notes | Medium | Modifies section framing | Remove notes |
| #7 Add invariant warnings | Medium | New content from debate | Remove subsection |

---

## Review Status

- **Approval**: Auto-approved (non-interactive mode)
- **Timestamp**: 2026-03-06
