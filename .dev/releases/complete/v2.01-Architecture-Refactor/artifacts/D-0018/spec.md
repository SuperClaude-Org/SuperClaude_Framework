# D-0018 Spec — `lint-architecture` Target Implementation

**Task:** T03.02
**Deliverable:** `lint-architecture` target in Makefile implementing 6 checks with ERROR/WARN exit behavior
**Date:** 2026-02-24

## Implemented Checks

| # | Check | Level | Description |
|---|-------|-------|-------------|
| 1 | Command → Skill link | ERROR | Commands with `## Activation` reference existing `sc-*-protocol/` skill directory |
| 2 | Skill → Command link | ERROR | Each `sc-*-protocol/` skill has a corresponding command file |
| 3 | Command size (warn) | WARN | Command file >200 lines |
| 4 | Command size (error) | ERROR | Command file >500 lines |
| 6 | Activation section present | ERROR | Paired commands (with matching `-protocol` skill) must have `## Activation` |
| 8 | Skill frontmatter complete | ERROR | SKILL.md must contain `name:`, `description:`, `allowed-tools:` fields |
| 9 | Protocol naming consistency | ERROR | SKILL.md `name:` field must end in `-protocol` |

## Deferred Checks

| # | Check | Status | Reason |
|---|-------|--------|--------|
| 5 | Inline protocol detection | NEEDS DESIGN | Requires heuristic for detecting inline YAML blocks >20 lines |
| 7 | Activation references correct skill | NEEDS DESIGN | Requires parsing `## Activation` section content |
| 10 | Sync integrity | Delegated | Already handled by `verify-sync` target |

## Exit Behavior

- Any ERROR → `exit 1` (CI failure)
- Warnings only → `exit 0` (CI pass)

## Makefile Integration

- `.PHONY` includes `lint-architecture`
- `help` target describes: `make lint-architecture - Enforce architecture policy (6 of 10 checks)`

## Modification Note (Phase 3)

Check 3/4 was adjusted to match the sprint-spec exactly:
- Removed non-spec `350 paired command ERROR` threshold
- Spec defines: Check 3 = WARN >200, Check 4 = ERROR >500 (universal)
