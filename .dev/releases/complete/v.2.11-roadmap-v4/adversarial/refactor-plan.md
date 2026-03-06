# Refactoring Plan: Merging V1 (base) with V2 Strengths

## Overview
- Base variant: variant-1-opus-architect.md
- Incorporating from: variant-2-haiku-architect.md
- Changes planned: 5
- Changes rejected: 1
- Risk level: Low overall (all changes are additive or restructuring within M2)
- Review status: auto-approved

---

## Planned Changes

### Change 1: Restructure M2 to include both P1 (Invariant Registry) and P2 (FMEA)
- **Source**: V2 grouping decision (M2={P1,P2}); converged upon in Round 3 by both advocates
- **Target location**: M2 milestone — rename to "State Variable Invariant Registry + FMEA Pass"; add FMEA deliverables D2.6a/D2.6b/D2.7a/D2.7b/D2.8a/D2.8b
- **Integration approach**: restructure — M2 expands to include D2.6-D2.8 (FMEA deliverables from V1's M3); M3 restructures to Guard Analysis only (P3)
- **Rationale**: Round 3 convergence — both advocates agreed P1+P2 share detection infrastructure and both are prerequisites for P3. Debate evidence: V1 advocate withdrew original M2={P1} position explicitly.
- **Risk**: Low — additive restructuring; no deletion of content

### Change 2: Add Release Gating Philosophy section
- **Source**: V2 unique contribution U-003; V1 advocate fully conceded in Round 1
- **Target location**: New standalone section after Dependency Graph, before M1
- **Integration approach**: insert — "## Release Gating" section
- **Content**: High-severity silent-corruption findings and unresolved guard ambiguity block downstream milestone progression. All findings require explicit owner assignment and documented acceptance rationale before proceeding.
- **Rationale**: C-006 verdict 95% for V2; operational enforcement is what makes the detection methodology actionable
- **Risk**: Low — additive; no conflict with existing content

### Change 3: Add M4 Pilot Deliverable
- **Source**: V2 unique contribution U-004; V1 conceded in Round 2
- **Target location**: M4 milestone — add D4.6a/D4.6b as pilot execution deliverables
- **Integration approach**: append to M4 deliverables table
- **Content**: D4.6a: pilot execution on one high-complexity roadmap with measurement of overhead vs defects prevented; D4.6b: verify go/no-go decision is recorded with evidence before general enablement
- **Rationale**: C-007 verdict 90% for V2; pilot-first is risk-appropriate for highest-cost proposal
- **Risk**: Low — additive

### Change 4: Add Release Gate Warning to M3 Guard Analysis
- **Source**: V2 M3 Risk R-005: "Make unresolved ambiguity a release gate warning with mandatory owner"
- **Target location**: M3 Risk Assessment table — update R-008 mitigation; add to D3.4a and D3.5a acceptance criteria
- **Integration approach**: modify existing — strengthen D3.4a AC to include: "Unresolved ambiguities produce release gate warning with mandatory owner field and review date"
- **Rationale**: U-003 and C-006 convergence; guard analysis without enforcement is detection without consequence
- **Risk**: Low — strengthens acceptance criteria only

### Change 5: Add standalone Release Gating to Risk Register
- **Source**: V2 R-001 "Verify deliverables become checklist theater" — V2's naming of this risk is more prominent
- **Target location**: Risk Register — add R-015 for checklist theater risk
- **Integration approach**: append
- **Content**: R-015: Verify deliverables become checklist theater (Medium probability, High impact) — mitigation: gate exit criteria require at least one state assertion or boundary case per `.b` deliverable, not generic "tests pass"
- **Rationale**: V2 named this risk explicitly; V1 addressed it structurally but did not call it out in the Risk Register
- **Risk**: Low — additive

---

## Changes NOT Being Made

### Rejected: Replace V1's .a/.b deliverable scheme with V2's flat IDs
- **Diff point**: S-004
- **V2 approach**: Flat IDs (D1.1, D1.2) without internal .a/.b splitting
- **Rationale for rejection**: V1 wins S-001 (85% confidence). V1's .a/.b scheme is self-consistent with Proposal 4 — the roadmap applies its own methodology to itself. V2's flat IDs describe the scheme without applying it, which is a weaker demonstration. The base variant's scheme is retained.

---

## Risk Summary

| Change | Risk | Impact | Rollback |
|--------|------|--------|---------|
| 1 (M2 restructure) | Low — restructuring, not deletion | Milestone count stays 4; deliverable count increases in M2/M3 | Revert to M2={P1}, M3={P2+P3} original V1 structure |
| 2 (Release Gating section) | Low — additive | None | Delete section |
| 3 (M4 pilot) | Low — additive | None | Delete D4.6a/D4.6b |
| 4 (Gate warning in M3) | Low — strengthens ACs | None | Relax AC wording |
| 5 (Risk Register R-015) | Low — additive | None | Delete row |

---

## Merged M2 Deliverable Structure (Change 1)

After restructuring, M2 becomes:

**M2: State Variable Invariant Registry + FMEA Pass**
- D2.1a/D2.1b: Invariant registry data structure (from V1 M2)
- D2.2a/D2.2b: State variable detector (from V1 M2)
- D2.3a/D2.3b: Mutation inventory generator (from V1 M2)
- D2.4a/D2.4b: Verification deliverable emitter (from V1 M2)
- D2.5a/D2.5b: Registry pipeline integration (from V1 M2)
- D2.6a/D2.6b: FMEA input domain enumerator (relocated from V1 M3 D3.1)
- D2.7a/D2.7b: FMEA failure mode classifier with dual detection signal (relocated from V1 M3 D3.2)
- D2.8a/D2.8b: FMEA deliverable promotion (relocated from V1 M3 D3.3)
- D2.9a/D2.9b: FMEA + Invariant Registry combined pipeline integration

**M3 after restructuring: Guard Analysis** (formerly part of M3, now M3's sole focus)
- D3.1a/D3.1b: Guard and sentinel analyzer (formerly D3.4)
- D3.2a/D3.2b: Guard resolution requirement + release gate warning (formerly D3.5; strengthened per Change 4)
- D3.3a/D3.3b: Guard analysis pipeline integration (formerly D3.6)

M3 dependency: M1 + M2 (both invariant predicates AND FMEA output required for guard severity classification).
