# D-0010: to_flat_inventory() Evidence

- Produces ComponentInventory with all str fields (no Path leakage)
- source_skill populated from skill.name
- component_count matches tree component_count
- 505 existing tests pass
