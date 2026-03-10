# D-0030: Finalized State Schema Specification

## Overview

State schema fields finalized based on Phases 2-5 implementation evidence.
The `.roadmap-state.json` now supports complete remediate and certify metadata.

## Schema §3.1: State Entry Fields

### Remediate Entry (`state.remediate`)

| Field | Type | Description |
|-------|------|-------------|
| status | string | "PASS" or "FAIL" |
| scope | string | RemediationScope value: "blocking_only", "blocking_warning", "all" |
| findings_total | int | Total findings from validation report |
| findings_actionable | int | Findings targeted for remediation |
| findings_fixed | int | Findings successfully remediated |
| findings_failed | int | Findings that failed remediation |
| findings_skipped | int | Findings skipped (auto-skip or out-of-scope) |
| agents_spawned | int | Number of parallel remediation agents launched |
| tasklist_file | string | Path to remediation-tasklist.md |
| timestamp | string | ISO-8601 UTC timestamp |

### Certify Entry (`state.certify`)

| Field | Type | Description |
|-------|------|-------------|
| status | string | "certified" or "certified-with-caveats" |
| findings_verified | int | Total findings verified by certification agent |
| findings_passed | int | Findings that passed certification |
| findings_failed | int | Findings that failed certification |
| certified | bool | true if all findings passed |
| report_file | string | Path to certification-report.md |
| timestamp | string | ISO-8601 UTC timestamp |

## State Transitions

```
post-validate:  validated | validated-with-issues
post-remediate: remediated
post-certify:   certified | certified-with-caveats
```

`derive_pipeline_status(state)` returns the correct status based on which
metadata entries are present, checking certify -> remediate -> validation
in reverse pipeline order.

## Additive Schema Extension (SC-008)

- New `remediate` and `certify` keys are additive-only
- Old state files without these keys handled gracefully (missing = "step not run")
- Existing consumers (`fidelity_status`, `steps.validate`) unaffected
- `_save_state()` preserves existing remediate/certify data across rewrites

## Implementation

- `build_remediate_metadata()` in executor.py
- `build_certify_metadata()` in executor.py
- `derive_pipeline_status()` in executor.py
- `_save_state()` extended with optional `remediate_metadata` and `certify_metadata` params
