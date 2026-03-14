# D-0027: SC-003 Sentinel Scan Self-Validation

## Deliverable

Sentinel scan and retry logic within `synthesize_spec` step.

## Implementation

- `scan_sentinels(artifact_path)`: Scans for `{{SC_PLACEHOLDER:*}}` sentinels using compiled regex
- Retry loop: up to 2 retries with `build_retry()` augmentation including specific placeholder names
- Resume policy: prefer re-running `synthesize-spec` over trusting partially gated output
- On exhausted retries with remaining sentinels: returns FAIL with `PARTIAL_ARTIFACT` classification

## Verification

- `TestSentinelScan::test_clean_output_has_no_sentinels`
- `TestSentinelScan::test_partial_output_has_sentinels`
- `TestSynthesizeSpecFailures::test_sentinels_exhaust_retries`
