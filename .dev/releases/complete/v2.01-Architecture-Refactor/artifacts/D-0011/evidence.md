# D-0011 — Evidence: `## Activation` Section Rewrite (BUG-006 Fix)

**Task**: T02.04
**Date**: 2026-02-24
**Status**: PASS

## Evidence

`src/superclaude/commands/roadmap.md` lines 68–74:
```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:roadmap-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.
```

`.claude/commands/sc/roadmap.md` — identical content confirmed.

## Acceptance Criteria Verification

- [x] `## Activation` contains exact string `Skill sc:roadmap-protocol`
- [x] "Do NOT proceed" warning present
- [x] Both `src/` and `.claude/` copies updated identically
- [x] Old path reference to `sc-roadmap/SKILL.md` completely removed

*Artifact produced by T02.04*
