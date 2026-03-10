# Refactor Plan: sc:adversarial v2.0 Roadmap Merge

**Date**: 2026-03-04
**Base variant**: Variant 1 (opus:architect)
**Target**: Merged roadmap.md

---

## Planned Changes

### Change 1: Add three control planes framework to Overview
- **Source**: V2/U-006, C-005 (V2 wins, 72%)
- **Integration point**: Overview section, paragraph 2
- **Operation**: Additive -- insert the three control planes model (Structural challenge, State reasoning, Process gating) as an organizing framework
- **Risk level**: Low -- additive framing, no structural conflict with existing Overview content
- **Provenance**: Variant 2 (haiku:architect)

### Change 2: Add D3.4 divergence detector deliverable to M3
- **Source**: V2/U-007, S-006 (V2 wins, 73%)
- **Integration point**: M3 Deliverables table, after D3.3
- **Operation**: Additive -- new row in deliverables table
- **Risk level**: Low -- new deliverable does not conflict with existing D3.1-D3.3
- **Provenance**: Variant 2 (haiku:architect)

### Change 3: Update M5 dependency to M1+M3+M4-final with fallback
- **Source**: X-002 resolution (V2 wins, 62%), S-002 (V2 wins, 62%)
- **Integration point**: M5 Dependencies section; also M5 row in Milestone Summary table
- **Operation**: Replacement -- M5 dependencies change from "M1, M4" to "M1, M3, M4-final"
- **Risk level**: Medium -- contested at 62% confidence; document fallback as risk-accepted variant
- **Provenance**: Variant 2 (haiku:architect), with fallback synthesis from debate resolution

### Change 4: Add D6.4 provenance tagging deliverable to M6
- **Source**: V2/U-008, S-006 (V2 wins, 73%), C-003 (V1 wins on deps, V2 wins on deliverable)
- **Integration point**: M6 Deliverables table, after D6.3
- **Operation**: Additive -- new row in deliverables table; includes lightweight cross-artifact consistency check
- **Risk level**: Low -- additive deliverable within existing M6 structure
- **Provenance**: Variant 2 (haiku:architect)

### Change 5: Add DA severity taxonomy to M1
- **Source**: V2/U-009, C-007
- **Integration point**: M1 D1.1 and D1.2 acceptance criteria; also M1 Risk Assessment table
- **Operation**: Additive -- severity taxonomy (critical-only default for convergence blocking) integrated into DA role specification and blocker wiring
- **Risk level**: Low -- refines existing DA behavior without structural change
- **Provenance**: Variant 2 (haiku:architect)

### Change 6: Add R8 adoption friction to Risk Register
- **Source**: V2/U-010, C-008
- **Integration point**: Risk Register table, new row R8
- **Operation**: Additive -- new risk entry (renumbered from V2's R6 to avoid conflict with V1's R6)
- **Risk level**: Low -- additive row
- **Provenance**: Variant 2 (haiku:architect)

### Change 7: Add S9 operational sustainability to Success Criteria
- **Source**: V2/U-011
- **Integration point**: Success Criteria table, Process Health subsection
- **Operation**: Additive -- new success criterion row
- **Risk level**: Low -- additive criterion
- **Provenance**: Variant 2 (haiku:architect)

### Change 8: Update M4 D4.1 with v0 contract language
- **Source**: X-001 synthesis (V1 wins, 78%)
- **Integration point**: M4 D4.1 acceptance criteria; M4 Dependencies section
- **Operation**: Replacement -- D4.1 adds v0 invariant contract language; mandatory refinement protocol v0->final after M3 outputs available
- **Risk level**: Low -- enriches existing V1 structure without changing dependency topology
- **Provenance**: Debate synthesis (both variants contributed)

### Change 9: Split Success Criteria into Output Quality + Process Health subsections
- **Source**: C-004 (Merged, 77%)
- **Integration point**: Success Criteria section header structure
- **Operation**: Structural reorganization -- existing SC1-SC8 become Output Quality; new S9 + framing become Process Health
- **Risk level**: Low -- reorganization only, no content removal
- **Provenance**: Debate synthesis (both variants contributed)

---

## Changes NOT Being Made

These decisions were resolved in favor of Variant 1 and are preserved in the base:

1. **M4 does NOT get M3 dependency** -- V1 wins X-001 (78%). M4 depends on M1 only. Invariant declaration begins concurrently with M3, producing v0 invariants that are refined after M3 completes.

2. **M6 does NOT get M4 dependency** -- V1 wins X-003 (71%). M6 depends on M3+M5. M4 inputs reach M6 transitively through M5.

3. **Serialized M1->M2->M3->M6 critical path preserved** -- V1 wins S-004 (75%). M4 branch runs in parallel and does not gate M6 directly.

4. **DA lifecycle remains stateless within single run** -- V1 wins C-001 (85%). No cross-run state.

5. **Quantitative SC targets preserved** -- V1 wins on SC style. Token budget <=40%, convergence rate >=80%, etc.

---

## Execution Order

Changes will be applied in the following sequence to maintain structural integrity:

1. Change 1 (Overview) -- standalone section, no dependencies
2. Change 5 (DA severity taxonomy in M1) -- modifies M1 before downstream refs
3. Change 2 (D3.4 in M3) -- modifies M3 before M5/M6 refs
4. Change 8 (M4 v0 contract) -- modifies M4 before M5 refs
5. Change 3 (M5 dependency update) -- depends on M3 and M4 being finalized
6. Change 4 (D6.4 in M6) -- modifies M6, depends on M5 structure
7. Change 6 (R8 risk) -- standalone addition to Risk Register
8. Change 9 (SC section split) -- structural reorganization
9. Change 7 (S9 criterion) -- inserted into newly created Process Health subsection
