# D-0006: Sentinel Collision Validation

## Test

Command: `grep -n 'SC_PLACEHOLDER' release-spec-template.md | grep -v '{{SC_PLACEHOLDER:'`

Result: **0 collisions** -- all occurrences of `SC_PLACEHOLDER` in the template use the `{{SC_PLACEHOLDER:name}}` format.

## Sentinel Inventory

- Total intentional sentinels: 57
- Collisions with prose: 0
- Self-references in usage block: 2 (documentation about the sentinel format, not actual placeholders)

## Validation Method

1. Searched for `SC_PLACEHOLDER` outside the `{{SC_PLACEHOLDER:` pattern
2. Found zero matches -- all sentinels are properly formatted
3. The usage block references `{{SC_PLACEHOLDER:*}}` as documentation, which correctly uses the sentinel format for self-description
