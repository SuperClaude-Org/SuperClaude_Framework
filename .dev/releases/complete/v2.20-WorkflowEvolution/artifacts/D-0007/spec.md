# Decision D-0007: MEDIUM Severity Blocking Policy

| Field | Value |
|---|---|
| Decision ID | D-0007 |
| Open Question | OQ-005 |
| Related Requirements | (none directly; informs gate design in Phase 3) |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

Should MEDIUM-severity deviations block the pipeline in v2.20, or only HIGH-severity?

## Decision

**Only HIGH-severity deviations block the pipeline in v2.20. MEDIUM-severity deviations are logged as non-blocking.**

### Blocking Policy

| Severity | v2.20 Behavior | Gate Effect |
|---|---|---|
| HIGH | **Blocking** | `_high_severity_count_zero()` returns `False` → pipeline halts |
| MEDIUM | Non-blocking | Logged in deviation report; pipeline continues |
| LOW | Non-blocking | Logged in deviation report; pipeline continues |

### v2.21 Revisit

The MEDIUM-blocks policy will be revisited in v2.21 with the following evaluation criteria:

- Frequency of MEDIUM-severity deviations in v2.20 production runs
- False-positive rate for MEDIUM classifications
- User feedback on whether MEDIUM deviations caused downstream issues
- Whether specific MEDIUM categories (e.g., fabricated traceability IDs per Gap Analysis TD-001) warrant selective blocking

## Rationale

- **Conservative rollout**: HIGH-only blocking provides strong safety guarantees without over-constraining the pipeline during initial deployment.
- **Data collection**: Running MEDIUM as non-blocking in v2.20 generates real-world data on MEDIUM deviation frequency and impact, informing the v2.21 policy decision.
- **Consistency with D-0001**: The warning-first approach for cross-references (OQ-001) establishes a pattern of graduated enforcement that this decision follows.
- **Gate simplicity**: The existing `_high_severity_count_zero()` gate check is sufficient; no new gate logic needed for v2.20.

## Impacts

- **Gate design (Phase 3)**: Only `_high_severity_count_zero()` is a blocking gate. No `_medium_severity_count_zero()` gate in v2.20.
- **Deviation reports**: MEDIUM deviations appear in reports but do not affect `tasklist_ready` status (which depends only on `high_severity_count == 0`).
- **v2.21 scope**: MEDIUM-blocking policy review is a planned decision item.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-005 | HIGH=blocking, MEDIUM=non-blocking in v2.20; revisit in v2.21 | (gate design) |
