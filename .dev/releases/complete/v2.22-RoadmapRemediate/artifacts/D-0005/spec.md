# D-0005: State Schema Shape for .roadmap-state.json

## Overview

Additive extension to `.roadmap-state.json` introducing `remediate` and `certify` step entries. No existing fields are renamed, removed, or modified. Schema version remains `1` (additive-only change per D-0001 review: "new keys can be added additively without breaking backward compatibility").

---

## Current Schema (unchanged)

```json
{
  "schema_version": 1,
  "spec_file": "<path>",
  "spec_hash": "<sha256>",
  "agents": [{"model": "...", "persona": "..."}],
  "depth": "quick|standard|deep",
  "last_run": "<ISO 8601>",
  "steps": {
    "extract": {"status": "PASS|FAIL|TIMEOUT|CANCELLED|SKIPPED", "attempt": 1, "output_file": "...", "started_at": "...", "completed_at": "..."},
    "generate-<agent-id>": { "..." },
    "...": "..."
  },
  "fidelity_status": "pass|fail"
}
```

---

## New: `remediate` Step Entry Shape

Added as a new key under `steps`. Follows the same `status`/`attempt`/`output_file`/`started_at`/`completed_at` pattern as existing step entries, with additional summary fields.

```json
{
  "steps": {
    "remediate": {
      "status": "PASS|FAIL|TIMEOUT|CANCELLED|SKIPPED",
      "attempt": 1,
      "output_file": "<path to remediation-tasklist.md>",
      "started_at": "<ISO 8601>",
      "completed_at": "<ISO 8601>",
      "scope": "all|blocking|blocking_warning",
      "findings_total": 14,
      "findings_actionable": 11,
      "findings_fixed": 8,
      "findings_failed": 2,
      "findings_skipped": 3,
      "agents_spawned": 4,
      "tasklist_file": "<path to remediation-tasklist.md>"
    }
  }
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| status | str | StepStatus value (PASS/FAIL/TIMEOUT/CANCELLED/SKIPPED) |
| attempt | int | Attempt number (1-based) |
| output_file | str | Path to primary output artifact |
| started_at | str | ISO 8601 timestamp |
| completed_at | str | ISO 8601 timestamp |
| scope | str | User-selected remediation scope: "all", "blocking", "blocking_warning" |
| findings_total | int | Total findings parsed from validation report |
| findings_actionable | int | Findings remaining after scope filtering (total - skipped) |
| findings_fixed | int | Findings with status FIXED after remediation |
| findings_failed | int | Findings with status FAILED after remediation |
| findings_skipped | int | Findings with status SKIPPED (filtered or no-action-required) |
| agents_spawned | int | Number of remediation agent processes launched |
| tasklist_file | str | Path to remediation-tasklist.md with per-finding detail |

---

## New: `certify` Step Entry Shape

Added as a new key under `steps`. Follows the same base pattern.

```json
{
  "steps": {
    "certify": {
      "status": "PASS|FAIL|TIMEOUT|CANCELLED|SKIPPED",
      "attempt": 1,
      "output_file": "<path to certification-report.md>",
      "started_at": "<ISO 8601>",
      "completed_at": "<ISO 8601>",
      "findings_verified": 8,
      "findings_passed": 7,
      "findings_failed": 1,
      "certified": true,
      "report_file": "<path to certification-report.md>"
    }
  }
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| status | str | StepStatus value (PASS/FAIL/TIMEOUT/CANCELLED/SKIPPED) |
| attempt | int | Attempt number (1-based) |
| output_file | str | Path to primary output artifact |
| started_at | str | ISO 8601 timestamp |
| completed_at | str | ISO 8601 timestamp |
| findings_verified | int | Number of FIXED findings that were re-verified |
| findings_passed | int | Findings that passed certification verification |
| findings_failed | int | Findings that failed certification verification |
| certified | bool | Overall certification result (true if all verified findings passed) |
| report_file | str | Path to certification report artifact |

---

## Validation Status Lifecycle Values

New top-level key `validation_status` to track the overall pipeline state:

| Value | Description | Trigger |
|-------|-------------|---------|
| `validated-with-issues` | Validation found issues; remediation not yet run or skipped | After validate step, if blocking issues found |
| `remediated` | Remediation completed (may have failures) | After remediate step completes |
| `certified` | All FIXED findings passed certification | After certify step with 100% pass rate |
| `certified-with-caveats` | Certification completed but some findings FAILED | After certify step with <100% pass rate |

```json
{
  "validation_status": "validated-with-issues|remediated|certified|certified-with-caveats"
}
```

---

## Backward Compatibility Checklist

- [x] No existing fields renamed
- [x] No existing fields removed
- [x] No existing field types changed
- [x] `schema_version` remains `1` (additive extension)
- [x] Existing `_save_state()` preserves unknown keys (confirmed in D-0001 §2)
- [x] New keys are optional -- existing consumers ignore them
- [x] `steps.remediate` and `steps.certify` follow the same `StepStatus`-based pattern as all other step entries

---

## Integration with `_save_state()` Pattern

Per D-0001 review, `_save_state()` in `roadmap/executor.py` already preserves existing keys across rewrites. The new `remediate` and `certify` step entries will be written by new step-specific code (Phases 3-5) using the same `_save_state()` pattern. No changes to the existing save logic are required at this stage.
