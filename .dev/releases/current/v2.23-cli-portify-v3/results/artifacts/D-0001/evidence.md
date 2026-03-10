# D-0001: Change Inventory

## Files to be Modified (4)

| # | File | Change Description |
|---|------|--------------------|
| 1 | `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | Replace Phase 3 (Code Generation) with Release Spec Synthesis; Replace Phase 4 (Integration) with Spec Panel Review; Update return contract; Update boundaries |
| 2 | `src/superclaude/skills/sc-cli-portify-protocol/refs/pipeline-spec.md` | Add section on how Phase 2 output feeds into spec template population |
| 3 | `src/superclaude/commands/cli-portify.md` | Update description to reflect spec-output (not code-output); Remove `--skip-integration` flag |
| 4 | `src/superclaude/skills/sc-cli-portify-protocol/decisions.yaml` | Add decisions for brainstorm integration model, panel configuration, template scope |

## Files to be Created (1)

| # | File | Purpose |
|---|------|---------|
| 1 | `src/superclaude/examples/release-spec-template.md` | General-purpose release spec template (FR-017) |

**Note**: `release-spec-template.md` already exists at the canonical location. It was created in a prior session. This task validates its content matches spec requirements.

## Verification

- Total: 4 modified + 1 created = 5 files (matches roadmap spec Section 4.1 and 4.2)
- Source: spec-cli-portify-workflow-evolution.md Sections 4.1, 4.2
