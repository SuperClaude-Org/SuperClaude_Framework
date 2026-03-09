# Decision D-0008: Step Timeout vs NFR Mismatch

| Field | Value |
|---|---|
| Decision ID | D-0008 |
| Open Question | OQ-008 |
| Related Requirements | NFR-001, NFR-002, NFR-009 |
| Date | 2026-03-09 |
| Status | RESOLVED |

## Question

FR-051.1 AC-11 specifies a step timeout of 600 seconds, but NFR-051.1 requires the step to complete within 120 seconds. Should the timeout be reduced, or does the NFR represent a p95 target while 600s is the hard cutoff?

## Decision

**120s is the p95 performance target for NFR measurement. 600s is the hard timeout. These are distinct values serving different purposes.**

### Value Definitions

| Value | Purpose | Enforcement | Action on Breach |
|---|---|---|---|
| 120s | p95 performance target | NFR measurement during Phases 3-4 | Performance warning; tracked as NFR compliance metric |
| 600s | Hard timeout | Runtime enforcement in step executor | Step termination; pipeline error with `retry_limit: 1` |

### Measurement Timing

Performance measurement against the 120s target occurs **during implementation Phases 3-4**, not only at the end of development:

- **Phase 3**: Initial implementation — measure baseline step execution times
- **Phase 4**: Integration — measure under realistic pipeline conditions
- **Phase 5**: End-to-end — confirm p95 compliance across full test suite

### Configuration

```yaml
spec_fidelity_step:
  timeout_hard: 600       # seconds — step killed if exceeded
  timeout_target_p95: 120 # seconds — NFR performance target
  retry_limit: 1          # retries on timeout
```

## Rationale

- **Distinct purposes**: The p95 target (120s) is a quality metric for optimization. The hard timeout (600s) is a safety mechanism preventing runaway LLM calls from blocking the pipeline indefinitely.
- **LLM variability**: LLM response times have high variance. A 120s hard timeout would cause frequent false failures on valid runs that happen to be slow. The 5x headroom (600s) accommodates tail latency.
- **Early measurement**: Measuring during Phases 3-4 (not only at the end) enables iterative optimization. If p95 exceeds 120s during Phase 3, prompt or model changes can be made before Phase 4.
- **Consistency**: Both values are referenced in the roadmap (NFR-001/002 for 120s, NFR-009 for 600s). This decision resolves the apparent contradiction.

## Impacts

- **Step executor**: Implements 600s hard timeout with retry_limit=1.
- **NFR measurement**: Performance tests track p95 against 120s target.
- **Monitoring**: Steps exceeding 120s but under 600s are logged as performance warnings (not errors).
- **Phase 3-4 scope**: Performance measurement is an explicit deliverable, not deferred to end-of-project.

## Decision Log Entry

| OQ | Decision | Impacted FRs |
|---|---|---|
| OQ-008 | 120s = p95 target, 600s = hard timeout; measure during Phases 3-4 | NFR-001, NFR-002, NFR-009 |
