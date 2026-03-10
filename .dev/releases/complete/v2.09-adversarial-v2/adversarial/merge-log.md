# Merge Log: sc:adversarial v2.0 Roadmap

**Date**: 2026-03-04
**Base variant**: Variant 1 (opus:architect)
**Merge executor**: merge-executor agent

---

## Applied Changes

### Change 1: Three control planes framework added to Overview
- **Source**: V2/U-006, C-005 (V2 wins, 72%)
- **Before**: Overview described "layered integration" without a named organizing framework
- **After**: Overview now includes the three control planes model (Structural challenge, State reasoning, Process gating) as paragraph 2 with descriptions of each plane
- **Provenance annotation**: HTML comment before the control planes paragraph
- **Validation**: Heading hierarchy preserved. No conflict with existing Overview content. Control planes map cleanly to milestone groupings: M1+M5 (structural), M3+M4 (state reasoning), M2+M6 (process gating).
- **Status**: APPLIED

### Change 2: DA severity taxonomy added to M1
- **Source**: V2/U-009, C-007
- **Before**: D1.1 and D1.2 described DA concerns without severity classification. All unresolved concerns blocked convergence.
- **After**: D1.1 includes severity taxonomy (critical/high/medium/low) with critical-only default for convergence blocking. D1.2 updated to reference severity threshold. D1.3 includes severity level in resolution matrix. Risk Assessment updated with severity taxonomy as mitigation for false positives.
- **Provenance annotation**: Inline HTML comments in D1.1 and Risk Assessment
- **Validation**: Severity taxonomy is consistent across D1.1, D1.2, D1.3, and Risk Assessment. No contradiction with existing DA lifecycle specification.
- **Status**: APPLIED

### Change 3: D3.4 divergence detector added to M3
- **Source**: V2/U-007, S-006 (V2 wins, 73%)
- **Before**: M3 had 3 deliverables (D3.1-D3.3). Divergence detection was implicit within D3.3.
- **After**: D3.4 added as explicit deliverable for automated end-state divergence detection. D3.4 operates independently from D3.3's severity classification, providing a binary divergence signal.
- **Provenance annotation**: HTML comment before D3.4 row
- **Validation**: D3.4 does not conflict with D3.3. The separation (binary detection vs. severity classification) is clearly delineated. Milestone Summary table updated to show 4 deliverables for M3.
- **Status**: APPLIED

### Change 4: M4 v0 contract language added to D4.1
- **Source**: X-001 synthesis (V1 wins, 78%)
- **Before**: D4.1 described invariant declaration without distinguishing draft vs. final status
- **After**: D4.1 includes v0 contract language: initial declarations are v0/draft, mandatory refinement pass upgrades to final after M3 outputs are available. M4 Objective section updated with concurrency explanation. Dependency Graph note added about M4 parallelization.
- **Provenance annotation**: None (synthesis from debate resolution, not single-variant source)
- **Validation**: v0 contract is consistent with M4's M1-only dependency. Refinement protocol bridges to M3 without creating a formal dependency arc. M5 explicitly consumes only M4-final invariants.
- **Status**: APPLIED

### Change 5: M5 dependency updated to M1+M3+M4-final
- **Source**: X-002 resolution (V2 wins, 62%), S-002 (V2 wins, 62%)
- **Before**: M5 depended on M1 and M4 only
- **After**: M5 depends on M1, M3, and M4-final. Fallback provision documented: exploratory-grade mode using M1+M4-v0 if M3 is delayed, with mandatory upgrade pass. Confidence note added (62% contested).
- **Provenance annotation**: HTML comment in Dependencies section
- **Validation**: New dependency is consistent with updated Dependency Graph. Fallback provision preserves schedule flexibility. Critical path updated: M1->M2->M3->M5->M6. Milestone Summary table updated.
- **Status**: APPLIED

### Change 6: D6.4 provenance tagging added to M6
- **Source**: V2/U-008, S-006 (V2 wins, 73%), X-003 synthesis
- **Before**: M6 had 3 deliverables (D6.1-D6.3). No provenance tracking.
- **After**: D6.4 added with provenance tagging (trace attribution to originating milestones) and lightweight cross-artifact consistency check. M5 added as M6 dependency (was M3-only in V1 base) to support D6.4's cross-reference against failure mode entries.
- **Provenance annotation**: HTML comment before D6.4 row
- **Validation**: D6.4 is consistent with M6's post-merge validation role. Cross-artifact consistency check validates transitive M4 path through M5. Milestone Summary table updated to show 4 deliverables and M3+M5 dependencies for M6. Risk Assessment updated with provenance overhead risk.
- **Status**: APPLIED

### Change 7: R8 adoption friction added to Risk Register
- **Source**: V2/U-010, C-008
- **Before**: Risk Register had 7 risks (R1-R7), all technical/process risks
- **After**: R8 added addressing adoption friction from scoring changes and mandatory phases. Mitigation includes transparent score breakdown, phased rollout, and documentation.
- **Provenance annotation**: HTML comment before R8 row
- **Validation**: R8 does not conflict with existing risks. Renumbered from V2's R6 to avoid collision with V1's R6 (merge-artifact re-debate). Total risks: 8.
- **Status**: APPLIED

### Change 8: Success Criteria split into Output Quality + Process Health
- **Source**: C-004 (Merged, 77%)
- **Before**: Single flat Success Criteria section with SC1-SC8 (quantitative targets from V1)
- **After**: Two subsections: Output Quality Criteria (SC1-SC8, preserved from V1) and Process Health Criteria (new subsection with S9)
- **Provenance annotation**: HTML comment before Process Health subsection
- **Validation**: All existing SC1-SC8 criteria preserved without modification. Subsection headers maintain heading hierarchy (### under ##).
- **Status**: APPLIED

### Change 9: S9 operational sustainability added to Success Criteria
- **Source**: V2/U-011
- **Before**: No operational sustainability criterion
- **After**: S9 added to Process Health subsection. Criterion: median pipeline runtime at --depth standard remains within 2x v1.0 median after tuning period (first 10 runs excluded).
- **Provenance annotation**: Covered by Change 8 annotation
- **Validation**: S9 is consistent with SC7 (token budget) but measures a different dimension (wall-clock runtime vs. token count). No contradiction.
- **Status**: APPLIED

---

## Post-Merge Validation

### Structural Integrity
- [PASS] Heading hierarchy: ## -> ### throughout, no level skips
- [PASS] Milestone Summary table: 6 rows, deliverable counts match per-milestone sections (3+3+4+3+3+4 = 20)
- [PASS] Dependency Graph: consistent with per-milestone Dependencies sections
- [PASS] YAML frontmatter: milestone_index matches body content, total_deliverables = 20, total_risks = 8

### Internal Reference Consistency
- [PASS] All deliverable IDs (D1.1-D1.3, D2.1-D2.3, D3.1-D3.4, D4.1-D4.3, D5.1-D5.3, D6.1-D6.4) referenced correctly
- [PASS] Risk IDs R1-R8 are sequential with no gaps or collisions
- [PASS] Success criteria SC1-SC8 + S9 are sequential; SC prefix used for Output Quality, S prefix used for Process Health
- [PASS] Cross-milestone references (M5->M3, M5->M4-final, M6->M3, M6->M5) are bidirectionally consistent

### Contradiction Re-scan
- [PASS] M4 dependency: M1 only (V1 position preserved). v0 contract bridges to M3 without formal dependency.
- [PASS] M5 dependency: M1+M3+M4-final (V2 position integrated). Fallback documented.
- [PASS] M6 dependency: M3+M5 (V1 structure preserved). D6.4 provenance validates transitive M4 path.
- [PASS] DA lifecycle: Stateless across debates, persistent within run (V1 position preserved).
- [PASS] SC style: Both adopted -- Output Quality (quantitative) + Process Health (operational).
- [PASS] No content added that was not specified in the refactoring plan.

### Provenance Completeness
- [PASS] All V2-sourced sections have HTML comment provenance annotations
- [PASS] Debate synthesis sections (v0 contract, M5 fallback) are annotated with resolution references
- [PASS] No V1-base sections were modified without documentation in this merge log
