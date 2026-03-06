# D-0025: FMEA Deliverable Promotion Specification

## Module
`src/superclaude/cli/pipeline/fmea_promotion.py`

## Promotion Logic
- Failure modes at/above `wrong_state` severity → promoted to `fmea_test` deliverable
- Below threshold → recorded as accepted risk in metadata with rationale
- Silent corruption findings → trigger Release Gate Rule 1

## Promotion Threshold
- Default: `wrong_state` (rank 3+)
- Configurable via `promotion_threshold` parameter (maps to `--fmea-threshold`)
- Severity ranking: cosmetic(1) < degraded(2) < wrong_state(3) < data_loss(4)

## Release Gate Rule 1
- Triggered by: `detection_difficulty == SILENT`
- Blocks: downstream milestone progression
- Resolution requires: named owner + documented rationale (non-empty strings enforced)
- `accept_violation()` validates non-empty strings for both fields

## Generated Deliverable Format
- ID: `D{milestone}.{seq}.fmea`
- Kind: `fmea_test`
- Metadata includes: source_deliverable_id, domain_description, detection_difficulty, severity, signal_source, invariant_predicate

## R-008 Mitigation
Release Gate Rule 1 ensures FMEA findings with silent corruption are acted on.
Silent corruption = blocking condition that requires explicit acceptance.
