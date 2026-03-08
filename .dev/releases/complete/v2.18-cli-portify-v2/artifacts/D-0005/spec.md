# D-0005: Specification — cli-portify.md Command Shim

**Task**: T01.04
**Roadmap Items**: R-010
**Date**: 2026-03-08

## File Location

`src/superclaude/commands/cli-portify.md`

## Structural Compliance

Follows the same pattern as `tasklist.md` command:
- YAML frontmatter with all required fields
- Usage section with argument table
- Input validation with error codes
- Activation section delegating to protocol skill
- Boundaries section (Will/Will Not)

## Arguments

| Argument | Type | Required | Default |
|----------|------|----------|---------|
| `--workflow` | path/name | Yes | -- |
| `--name` | string | No | Derived |
| `--output` | path | No | `src/superclaude/cli/<name>/` |
| `--dry-run` | flag | No | false |
| `--skip-integration` | flag | No | false |

## Error Codes

| Code | Trigger |
|------|---------|
| MISSING_WORKFLOW | `--workflow` not provided |
| INVALID_PATH | Path doesn't resolve to skill with SKILL.md |
| AMBIGUOUS_PATH | Multiple candidates match |
| OUTPUT_NOT_WRITABLE | Output parent not writable |
| NAME_COLLISION | Existing non-portified module at target |
| DERIVATION_FAILED | Cannot derive CLI name |

## Delegation

Delegates to `Skill sc:cli-portify-protocol` with validated context.
