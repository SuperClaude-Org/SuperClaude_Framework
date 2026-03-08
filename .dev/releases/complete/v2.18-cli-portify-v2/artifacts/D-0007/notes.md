# D-0007: Notes — sc-cli-portify Deprecation

**Task**: T01.06
**Roadmap Items**: R-013
**Date**: 2026-03-08

## Action Taken

Added deprecation notice to `src/superclaude/skills/sc-cli-portify/SKILL.md` immediately after frontmatter:

```markdown
> **DEPRECATED**: This skill has been replaced by `sc-cli-portify-protocol/`.
> The protocol skill contains the full behavioral protocol with updated API-aligned refs.
> This directory is scheduled for removal after Phase 5 validation.
> Do NOT use this skill for new work — use `Skill sc:cli-portify-protocol` instead.
```

## Verification

- Notice is the first non-frontmatter content in the file
- References `sc-cli-portify-protocol/` as replacement
- Indicates Phase 5 removal timeline
- Old extended metadata comment block removed (now promoted to protocol SKILL.md frontmatter)
