# D-0017: Verification Deliverable Emitter Specification

## Module
`src/superclaude/cli/pipeline/verification_emitter.py`

## Emitter Logic
For each mutation site (up to cap), generates one `kind=invariant_check` deliverable:
1. ID follows `D{milestone}.{seq}.inv` pattern
2. Description includes invariant predicate, mutation reference, edge cases
3. Each deliverable contains a state assertion (`assert <predicate>`)
4. Metadata includes variable_name, scope, predicate, mutation_deliverable_id, edge_cases

## ID Scheme
`D{milestone}.{seq}.inv` where:
- `milestone` = extracted from mutation site's deliverable_id
- `seq` = sequential counter per variable (1-based)

## Edge Cases Generated
- zero value
- empty collection
- boundary minimum

## R-005 Cap
- Default: 5 invariant_check deliverables per variable
- Configurable via `max_checks_per_variable` parameter (maps to `--max-invariant-checks`)

## Release Gate Rule 3 Compliance
Each generated deliverable contains `assert <predicate>` in description.
