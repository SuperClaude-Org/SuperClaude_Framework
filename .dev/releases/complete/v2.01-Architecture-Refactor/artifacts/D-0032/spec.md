# D-0032 — Spec: task-unified.md Extraction Mapping

**Task**: T06.03
**Date**: 2026-02-24
**Status**: COMPLETE

## Extraction Summary

| Metric | Before | After |
|--------|--------|-------|
| `task-unified.md` line count | 167 | 95 |
| `sc-task-unified-protocol/SKILL.md` line count | 308 | 308 (unchanged) |

## What Was Removed from Command File

| Section | Lines Removed | Reason |
|---------|--------------|--------|
| Strategy Flags table | 8 | Already in protocol SKILL.md (Usage section) |
| Compliance Flags table | 8 | Already in protocol SKILL.md (Classification Phase) |
| Execution Control Flags table | 8 | Already in protocol SKILL.md |
| Verification Flags table | 8 | Already in protocol SKILL.md (Verification Phase) |
| Verbose examples (5 sections) | 30 | Consolidated to 5 inline examples |
| Migration table | 6 | Simplified to 1-line note |
| Context Signals subsection | 6 | Covered by Triggers table |

Total lines removed: ~72

## What Was Added

| Addition | Purpose |
|----------|---------|
| `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` | BUG-001 fix — Skill tool now in allowed-tools |
| Key flags summary line | Brief reference to flag names with pointer to protocol skill |

## Structure Preserved

Command file follows the 3-tier model command template:
1. Frontmatter (with `allowed-tools` including `Skill`)
2. Purpose + Triggers
3. Usage (brief)
4. Behavioral Summary
5. Activation (references `Skill sc:task-unified-protocol`)
6. Examples (consolidated)
7. Boundaries
8. Migration note

*Artifact produced by T06.03*
