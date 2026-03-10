# D-0009: decisions.yaml Content Specification

**Task**: T01.09
**Roadmap Items**: R-014, R-015
**Date**: 2026-03-08

## File Location

`src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml`

## Schema

```yaml
schema_version: "1.0"
decisions:
  <OQ-ID>:
    title: <string>
    blocking: <boolean>
    resolution: <string>
    evidence: <string>
    impact: <string>
```

## Entries

6 blocking OQ entries:

| OQ | Title | Key Decision |
|----|-------|-------------|
| OQ-002 | TurnLedger in pipeline API | Not in pipeline API; import from sprint.models |
| OQ-003 | dry-run behavior | Phases 0-2 only, no code generation |
| OQ-004 | Integration schema | 4 boolean fields + standard header |
| OQ-007 | Approval gate mechanism | TodoWrite checkpoint pattern |
| OQ-008 | Default output path | `src/superclaude/cli/<derived_name>/` |
| OQ-010 | Step boundary algorithm | Already in analysis-protocol.md |

## Verification

- All 6 blocking OQs have non-empty resolution fields ✅
- Schema version present ✅
- Each entry has: title, blocking, resolution, evidence, impact ✅
