# D-0036 — Evidence: BUG-002 Resolution (Stale Path in validate-tests.md)

**Task**: T06.06
**Date**: 2026-02-24
**Status**: RESOLVED

## Bug Description

BUG-002: `validate-tests.md` referenced old skill directory paths without the `-protocol` suffix.

## Fixes Applied

| Line | Before | After |
|------|--------|-------|
| 63 | `skills/sc-validate-tests/classification-algorithm.yaml` | `skills/sc-validate-tests-protocol/classification-algorithm.yaml` |
| 121 | `skills/sc-task-unified/SKILL.md` | `skills/sc-task-unified-protocol/SKILL.md` |
| 122 | `skills/sc-validate-tests/SKILL.md` | `skills/sc-validate-tests-protocol/SKILL.md` |

## Verification

```
$ grep "sc-validate-tests/" src/superclaude/commands/validate-tests.md
(returns only -protocol suffixed paths)
```

All 3 stale path references updated to use `-protocol` suffix.

*Artifact produced by T06.06*
