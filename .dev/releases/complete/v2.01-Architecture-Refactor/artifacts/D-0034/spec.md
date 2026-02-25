# D-0034 — Spec: Command File Updates (Activation + BUG-001)

**Task**: T06.04
**Date**: 2026-02-24
**Status**: COMPLETE

## Changes Applied

### Per-Command Changes

| Command | `## Activation` | `allowed-tools` with `Skill` | Notes |
|---------|-----------------|------------------------------|-------|
| `adversarial.md` | Already present (refs `sc:adversarial-protocol`) | **Added** | BUG-001 fix |
| `cleanup-audit.md` | Already present (refs `sc:cleanup-audit-protocol`) | **Added** | BUG-001 fix |
| `task-unified.md` | Already present (refs `sc:task-unified-protocol`) | **Added** (in T06.03) | BUG-001 fix via extraction |
| `validate-tests.md` | Already present (refs `sc:validate-tests-protocol`) | **Added** + frontmatter created | Had no YAML frontmatter |

### Verification: All 5 Paired Commands Complete

| Command | `## Activation` | `Skill` in `allowed-tools` | Status |
|---------|-----------------|----------------------------|--------|
| `roadmap.md` | Yes (from P2) | Yes (from P2) | SC-002 + SC-003 |
| `adversarial.md` | Yes | Yes | SC-002 + SC-003 |
| `cleanup-audit.md` | Yes | Yes | SC-002 + SC-003 |
| `task-unified.md` | Yes | Yes | SC-002 + SC-003 |
| `validate-tests.md` | Yes | Yes | SC-002 + SC-003 |

**SC-002**: All 5 commands have `## Activation` sections — **PASS**
**SC-003**: All 5 commands have `Skill` in `allowed-tools` — **PASS** (BUG-001 fully resolved)

*Artifact produced by T06.04*
