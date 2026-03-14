# D-0006: Tiered Component Entry Dataclasses Evidence

- CommandEntry (tier=0), SkillEntry (tier=1), AgentEntry (tier=2) defined
- Each has: tier, name, path, line_count, source_dir fields
- Import succeeds, 505 existing tests pass
