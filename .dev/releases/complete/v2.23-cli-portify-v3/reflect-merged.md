---
source: spec-fidelity.md
target: roadmap.md
remediation_date: "2026-03-09"
total_deviations: 15
fixed: 15
remaining: 0
tasklist_ready: true
---

# Spec-Fidelity Remediation Status

## Summary

All 15 deviations identified in `spec-fidelity.md` have been remediated in `roadmap.md`.

| Severity | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| HIGH     | 4     | 4     | 0         |
| MEDIUM   | 8     | 8     | 0         |
| LOW      | 3     | 3     | 0         |

## Deviation Fix Status

### HIGH Severity

| ID | Deviation | Status | Fix Applied |
|----|-----------|--------|-------------|
| DEV-001 | Return contract missing 9 fields | **FIXED** | Added `output_directory`, `failure_phase`, `failure_type`, `source_step_count`, `spec_fr_count`, `api_snapshot_hash`, `resume_command`, `resume_phase`, `phase_contracts` to Phase 4 Contract Updates. Added `failure_type` 7-value enumeration. |
| DEV-002 | User rejection options treated as open question | **FIXED** | Resolved OQ-7 with spec §5.2 defined options (edit-and-re-review, regenerate, abandon). Separated convergence exhaustion from user rejection. Removed invalid `status: forced`. |
| DEV-003 | Phase 3 entry criteria missing | **FIXED** | Added Phase 2→3 Entry Gate verifying: contract `status: completed`, all blocking checks passed, `step_mapping` ≥1 entry. |
| DEV-004 | Focus pass expert panel not specified | **FIXED** | Added Fowler (architecture), Nygard (reliability/failure modes), Whittaker (adversarial), Crispin (testing) to Phase 3 item 4a. |

### MEDIUM Severity

| ID | Deviation | Status | Fix Applied |
|----|-----------|--------|-------------|
| DEV-005 | Parallelization opportunity not reflected | **FIXED** | Updated parallelization text to reference spec §4.7 parallel execution allowance with documented rationale for sequential choice. |
| DEV-006 | Resume behavior semantics not specified | **FIXED** | Added resume behavior semantics sub-section: Phase 3 resume (3c preserves populated spec), Phase 4 resume (4a preserves draft spec), artifact preservation rules. |
| DEV-007 | Quality score range not specified | **FIXED** | Added `(0-10 range)` to quality score specification in Phase 3 critique pass. |
| DEV-008 | `decisions.yaml` missing from Files Modified | **FIXED** | Added `decisions.yaml` row to Files Modified table with Phase 6. |
| DEV-009 | Two E2E test scenarios missing | **FIXED** | Added "Low-quality spec recovery" and "Phase 3 brainstorm timeout" scenarios to Phase 5 End-to-End Validation. |
| DEV-010 | `status: complete` vs spec's `status: success` | **FIXED** | Changed `status: complete` to `status: success` in convergence loop CONVERGED state. |
| DEV-011 | NFR-001 blocking in Gate B | **FIXED** | Marked NFR-001 as `non-blocking advisory` in Gate B conditions. |
| DEV-012 | Conditional sections requirement missing | **FIXED** | Added FR-060.7 conditional sections requirement to Phase 1 Template Creation. |

### LOW Severity

| ID | Deviation | Status | Fix Applied |
|----|-----------|--------|-------------|
| DEV-013 | Renumbered requirement IDs lack traceability | **FIXED** | Added Requirement Traceability table mapping roadmap IDs (FR-001–017, NFR-001–009) to spec IDs (FR-060.x, NFR-060.x). |
| DEV-014 | Constraint references undefined | **FIXED** | Added Constraints Reference table defining Constraints 1–10 with source references to spec §2.1. |
| DEV-015 | Spec Open Items not carried forward | **FIXED** | Added OQ-8 (progress observability, Hightower) and OQ-9 (brainstorm enrichment mapping, Hohpe) to Open Questions. |
