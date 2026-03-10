# D-0004: Sync Requirement Confirmation

## Requirement

After modifying files under `src/superclaude/`, the command `make sync-dev` must be run to copy changes to `.claude/` for Claude Code to pick up during development.

## Affected Files in This Release

All 4 modified files and 1 created file are under `src/superclaude/`:

1. `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
2. `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md`
3. `src/superclaude/commands/cli-portify.md`
4. `src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml`
5. `src/superclaude/examples/release-spec-template.md`

## Sync Commands

```bash
make sync-dev        # Copy src/superclaude/{skills,agents} -> .claude/
make verify-sync     # Confirm src/ and .claude/ are in sync (CI-friendly)
```

## Confirmation

`make sync-dev` is required after each phase that modifies `src/superclaude/` files.

Source: CLAUDE.md "Component Sync" section.
