# D-0012 — Spec: 5 Skill Directory Renames

**Task**: T02.05
**Date**: 2026-02-24
**Status**: COMPLETE

## Rename Summary

| Old Directory | New Directory | name: Field | Status |
|---------------|---------------|-------------|--------|
| `sc-adversarial/` | `sc-adversarial-protocol/` | `sc:adversarial-protocol` | RENAMED |
| `sc-cleanup-audit/` | `sc-cleanup-audit-protocol/` | `sc:cleanup-audit-protocol` | RENAMED |
| `sc-roadmap/` | `sc-roadmap-protocol/` | `sc:roadmap-protocol` | RENAMED |
| `sc-task-unified/` | `sc-task-unified-protocol/` | `sc:task-unified-protocol` | RENAMED |
| `sc-validate-tests/` | `sc-validate-tests-protocol/` | `sc:validate-tests-protocol` | RENAMED |

## Changes Applied in This Phase

Directories were already renamed to `-protocol` suffix (from prior work). This phase updated:
1. `sc-adversarial-protocol/SKILL.md`: `name: sc:adversarial` → `name: sc:adversarial-protocol` + added `Skill` to `allowed-tools`
2. `sc-cleanup-audit-protocol/SKILL.md`: `name: cleanup-audit` → `name: sc:cleanup-audit-protocol` (also fixed missing `sc:` prefix)
3. `sc-task-unified-protocol/SKILL.md`: `name: sc-task-unified` → `name: sc:task-unified-protocol`
4. `sc-validate-tests-protocol/SKILL.md`: `name: sc-validate-tests` → `name: sc:validate-tests-protocol`

## Verification

```bash
ls src/superclaude/skills/sc-*-protocol/  # All 5 directories present
make sync-dev && make verify-sync         # All components in sync
```

*Artifact produced by T02.05*
