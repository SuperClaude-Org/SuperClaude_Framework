# D-0026: FMEA Deliverable Promotion Test Evidence

## Test Execution
- **File**: `tests/pipeline/test_fmea_promotion.py`
- **Tests**: 11 passed, 0 failed
- **Duration**: 0.04s

## Scenario Results

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| Silent corruption promoted + gate triggered | fmea_test + violation | fmea_test + violation | PASS |
| Cosmetic → accepted risk | accepted_risks entry | accepted_risks entry | PASS |
| Promoted includes detection mechanism | description contains mechanism | contains mechanism | PASS |
| Configurable threshold | degraded promoted at lower threshold | promoted correctly | PASS |
| Zero above-threshold | no entries at all | empty lists | PASS |
| Blocking until accepted | has_blocking_violations True | True | PASS |
| Acceptance requires named owner | ValueError on empty | ValueError raised | PASS |
| Acceptance requires rationale | ValueError on empty | ValueError raised | PASS |
| Accepted violation no longer blocking | has_blocking False after accept | False | PASS |
| Section contains headings | FMEA + Rule 1 headings | present | PASS |
| Empty section | "No failure modes detected" | present | PASS |
