# Test Prompt: Failure-Injection via --resume-from

**Sprint**: v2.02-Roadmap-v3 (QA Remediation — Fix 2)
**Date**: 2026-03-03
**Purpose**: Validate sc:roadmap consumer error handling against 5 data corruption fixtures

---

## Prerequisites

1. The v2.02 fix changes are applied (T-FIX1.1 through T-FIX2.4)
2. `make sync-dev && make verify-sync` has been run
3. DC fixture directories exist at `.dev/releases/current/v2.02-Roadmap-v3/test-fixtures/`

## Setup

Create a minimal valid spec file for testing:

```
Write .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md with:

---
name: Failure Injection Test Spec
version: 1.0.0
---

# Test Specification

## Requirements

### Functional Requirements
- FR-001: The system SHALL accept user input via a REST API endpoint
- FR-002: The system SHALL validate input against a JSON schema
- FR-003: The system SHALL return structured error responses on validation failure

### Non-Functional Requirements
- NFR-001: API response time SHALL be under 200ms at P95
- NFR-002: The system SHALL log all validation failures

## Success Criteria
- SC-001: All 3 functional requirements implemented and tested
- SC-002: P95 latency meets NFR-001 threshold
```

---

## Test Execution

Run each fixture test sequentially. For each, invoke sc:roadmap with `--resume-from` pointing to the fixture directory.

### DC-1: Missing Fields (Consumer Defaults)

```
/sc:roadmap .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md --multi-roadmap --agents opus,sonnet --resume-from .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/DC-1-missing-fields/
```

**Expected behavior**:
- sc:roadmap reads return-contract.yaml from DC-1 directory
- `status` field is absent → consumer default `"failed"` applied → abort
- `convergence_score` field is absent → consumer default `0.5` applied
- extraction.md `pipeline_diagnostics.contract_validation.fields_defaulted` should list `["status", "convergence_score"]`

**PASS criteria**:
- [ ] Abort occurs (status defaults to "failed")
- [ ] Warning logged for each missing field
- [ ] If extraction.md was written before abort, `fields_defaulted` lists both fields

---

### DC-2: Null Values (Null Routing Semantics)

```
/sc:roadmap .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md --multi-roadmap --agents opus,sonnet --resume-from .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/DC-2-null-values/
```

**Expected behavior**:
- sc:roadmap reads return-contract.yaml from DC-2 directory
- `status: "success"` but `merged_output_path: null` → missing-file guard triggers
- `convergence_score: null` → consumer default `0.5` applied (Partial path)
- Null `base_variant` recorded as-is in frontmatter

**PASS criteria**:
- [ ] `convergence_score` defaults to 0.5
- [ ] Missing-file guard triggers (null merged_output_path)
- [ ] Appropriate error handling for null values

---

### DC-3: Missing Referenced File (File Guard)

```
/sc:roadmap .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md --multi-roadmap --agents opus,sonnet --resume-from .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/DC-3-missing-referenced-file/
```

**Expected behavior**:
- sc:roadmap reads return-contract.yaml from DC-3 directory
- `merged_output_path: "./does-not-exist.md"` → file existence check fails
- Treated as `status: failed, failure_stage: transport, convergence_score: 0.0`
- Log: `"merged_output_path './does-not-exist.md' does not exist on disk."`

**PASS criteria**:
- [ ] Missing-file guard triggers
- [ ] Status overridden to `failed`
- [ ] `failure_stage` set to `transport`
- [ ] Error message includes the path that doesn't exist
- [ ] `pipeline_diagnostics.contract_validation.file_guard_passed: false`

---

### DC-4: Malformed YAML (Parse Error Handler)

```
/sc:roadmap .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md --multi-roadmap --agents opus,sonnet --resume-from .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/DC-4-malformed-yaml/
```

**Expected behavior**:
- sc:roadmap reads return-contract.yaml from DC-4 directory
- Content `{invalid: yaml: [` fails YAML parsing
- Treated as `status: failed, failure_stage: transport`
- Parse error logged verbatim

**PASS criteria**:
- [ ] YAML parse error detected
- [ ] Status set to `failed`
- [ ] `failure_stage` set to `transport`
- [ ] Parse error message logged verbatim
- [ ] Roadmap generation aborted

---

### DC-5: Fallback Mode Warning

```
/sc:roadmap .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md --multi-roadmap --agents opus,sonnet --resume-from .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/DC-5-fallback-mode/
```

**Expected behavior**:
- sc:roadmap reads return-contract.yaml from DC-5 directory
- Valid contract with `fallback_mode: true` and `convergence_score: 0.75`
- Status routing: `convergence_score >= 0.6` → PASS path
- Differentiated fallback warning emitted: "Adversarial result was produced via fallback path..."
- Warning logged in extraction.md

**PASS criteria**:
- [ ] Fallback warning emitted with differentiated message text
- [ ] Warning logged in extraction.md
- [ ] Roadmap generation proceeds (not aborted)
- [ ] `pipeline_diagnostics.fallback_activated: true` in extraction.md
- [ ] `invocation_method: "file-fallback"` recorded

---

## Scoring Summary

| Fixture | QA Criterion | Result |
|---------|-------------|--------|
| DC-1 | 5 (Consumer defaults evidence) | PASS / FAIL |
| DC-2 | 5 (Consumer defaults) + 8 (Missing-file guard) | PASS / FAIL |
| DC-3 | 8 (Missing-file guard evidence) | PASS / FAIL |
| DC-4 | 11 (YAML parse error tested) | PASS / FAIL |
| DC-5 | 10 (fallback_mode warning tested) | PASS / FAIL |

**Aggregate**: For Fix 2 criteria to pass, DC-1/DC-3 must demonstrate consumer defaults and file guard behavior, DC-4 must demonstrate YAML error handling, DC-5 must demonstrate fallback warning.

---

## Cleanup

After testing, remove generated artifacts:
```bash
rm -rf .dev/releases/current/v2.02-Roadmap-v3/test-fixtures/test-spec.md
# Keep fixture directories for future re-testing
```
