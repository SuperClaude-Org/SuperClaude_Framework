# D-0007: ComponentTree Dataclass Evidence

- ComponentTree with command, skill, agents fields
- component_count: returns 2 for command+skill, 0 for empty tree
- total_lines: sums across all tiers
- all_source_dirs: returns deduplicated list of Path objects
- Import succeeds, 505 existing tests pass
