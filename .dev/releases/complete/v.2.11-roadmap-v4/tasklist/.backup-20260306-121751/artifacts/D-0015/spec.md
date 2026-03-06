# D-0015: Mutation Inventory Generator Specification

## Module
`src/superclaude/cli/pipeline/mutation_inventory.py`

## Algorithm
1. For each detected state variable, create a birth-site MutationSite
2. Scan ALL deliverable descriptions across the full roadmap
3. Check if description references the variable name
4. Match against definite mutation indicators (update, increment, reset, set-to, advance-by, clear, modify, assign, assignment operators)
5. Match against ambiguous patterns (change, adjust, tweak) -> flagged separately
6. Return MutationInventoryResult per variable with mutation_sites and ambiguous_sites

## Mutation Indicators
| Indicator | Example | Type |
|-----------|---------|------|
| update X | "Update offset after processing" | definite |
| increment X | "Increment offset by step" | definite |
| reset X | "Reset offset to zero" | definite |
| set X to | "Set counter to initial value" | definite |
| advance X by | "Advance cursor by batch_size" | definite |
| clear X | "Clear the flag" | definite |
| change X | "Change offset based on input" | ambiguous |
| adjust X | "Adjust counter for edge case" | ambiguous |

## Cross-Reference Behavior
Scans ALL roadmap deliverables, not just those in the introducing milestone. This catches mutations that happen far from the variable's birth.
