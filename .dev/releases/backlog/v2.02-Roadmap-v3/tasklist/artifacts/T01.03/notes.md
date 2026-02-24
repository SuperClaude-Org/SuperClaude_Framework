# T01.03 — Tier Classification Policy for Executable Specification Files

**Task ID:** T01.03
**Roadmap Item ID:** R-001 (systemic)
**Timestamp:** 2026-02-23T00:00:00Z
**Tier:** EXEMPT

## Decision

**The `*.md` path booster (+0.5 toward EXEMPT) does NOT apply to executable specification files.**

### Rationale

The `*.md` EXEMPT booster in the `/sc:task-unified` algorithm was designed for human-readable documentation files (READMEs, guides, changelogs). The following files in this sprint function as **executable code** — Claude Code interprets them as behavioral instructions that directly affect agent execution:

| File | Role | Classification |
|---|---|---|
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Adversarial pipeline execution spec | Executable specification |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | Roadmap skill execution spec | Executable specification |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | Integration wiring instructions | Executable specification |
| `src/superclaude/commands/roadmap.md` | Command allowed-tools list | Executable specification |

### Tie-Breaker Applied

Per tasklist deterministic rule 8 and tie-breaker rule 3 (reversibility): treating executable spec files as documentation would incorrectly lower verification requirements for changes that can break agent behavior. The more conservative interpretation (no EXEMPT booster) is applied.

## Impact on Task Tiers

Tasks **NOT** receiving the EXEMPT booster (tiers computed without it):

| Task | File Modified | Tier Without Booster |
|---|---|---|
| T02.01 | roadmap.md | LIGHT |
| T02.02 | sc-roadmap/SKILL.md | LIGHT |
| T02.03 | sc-roadmap/SKILL.md | STRICT |
| T04.01 | sc-adversarial/SKILL.md | STRICT |
| T04.02 | adversarial-integration.md | STRICT |
| T04.03 | adversarial-integration.md | STANDARD |
| T05.01 | adversarial-integration.md | STANDARD |
| T05.02 | sc-roadmap/SKILL.md | STANDARD |
| T05.03 | adversarial-integration.md | STANDARD |

If the booster were applied: T02.01, T02.02, T04.03, T05.01–T05.03 would shift toward EXEMPT (lower verification).

## Policy Statement for Future Sprints

> **Executable Specification files** — any `.md` file that Claude Code reads and interprets as behavioral instructions (SKILL.md, command .md files, ref .md files consumed by skill execution logic) — are classified as **code** for tier purposes. The `*.md` documentation EXEMPT booster does NOT apply to them.

## Evidence Path

`TASKLIST_ROOT/tasklist/evidence/T01.03/`
