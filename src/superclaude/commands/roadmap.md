---
name: sc:roadmap
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
---

# /sc:roadmap — Roadmap Generator

## Trigger

When the user requests roadmap generation from a specification file. Requires a specification file path as mandatory input.

## Usage

```
/sc:roadmap <spec-file-path> [options]
/sc:roadmap --specs <spec1.md,spec2.md,...> [options]
/sc:roadmap <spec-file-path> --multi-roadmap --agents <agent-specs> [options]
```

## Flags

| Flag | Short | Required | Default | Description |
|------|-------|----------|---------|-------------|
| `<spec-file-path>` | | Yes (single-spec) | - | Path to specification document |
| `--specs` | | Yes (multi-spec) | - | Comma-separated spec file paths (2-10) |
| `--template` | `-t` | No | Auto-detect | Template type: feature, quality, docs, security, performance, migration |
| `--output` | `-o` | No | `.dev/releases/current/<spec-name>/` | Output directory |
| `--depth` | `-d` | No | `standard` | Analysis depth: quick, standard, deep |
| `--multi-roadmap` | | No | `false` | Enable multi-roadmap adversarial generation |
| `--agents` | `-a` | No | - | Agent specs: `model[:persona[:"instruction"]]`. Implies `--multi-roadmap` when present. |
| `--interactive` | `-i` | No | `false` | User approval at adversarial decision points |
| `--validate` | `-v` | No | `true` | Enable multi-agent validation (Wave 4) |
| `--no-validate` | | No | `false` | Skip validation. Sets validation_status: SKIPPED |
| `--compliance` | `-c` | No | Auto-detect | Compliance tier: strict, standard, light |
| `--persona` | `-p` | No | Auto-select | Override primary persona |
| `--dry-run` | | No | `false` | Preview structure without writing files |

## Examples

```bash
# Basic single-spec
/sc:roadmap specs/auth-system.md

# Deep analysis with security template
/sc:roadmap specs/migration-plan.md --template security --depth deep

# Consolidate 3 specs into one roadmap
/sc:roadmap --specs specs/frontend.md,specs/backend.md,specs/security.md

# Generate 3 competing roadmaps (model-only — all use auto-detected persona)
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus,sonnet,gpt52

# Generate with explicit personas
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus:architect,sonnet:security,opus:analyzer

# Mixed: some with persona, some model-only
/sc:roadmap specs/v2-prd.md --multi-roadmap --agents opus:architect,sonnet,gpt52:security

# Full combined mode with interactive approval
/sc:roadmap --specs specs/v2-prd.md,specs/v2-addendum.md \
  --multi-roadmap --agents opus:architect,sonnet:security --interactive --depth deep

# Custom output directory
/sc:roadmap specs/auth.md --output .dev/releases/current/v2.0-auth/

# Shorthand: --agents implies --multi-roadmap
/sc:roadmap specs/v2-prd.md --agents opus:architect,haiku:analyzer --depth deep
```

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:roadmap-protocol

Pass all user-provided arguments (spec file path, flags) verbatim to the Skill invocation via the `args` parameter.

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Boundaries

**Will do**: Generate structured roadmaps from spec files; invoke sc:adversarial for multi-spec/multi-roadmap; apply multi-agent validation; create milestone-based roadmaps with dependency graphs and risk registers; persist session state for cross-session resumability.

**Will not do**: Generate tasklists or execution prompts; execute implementation; trigger downstream commands automatically; generate roadmaps without spec input; write outside designated output directories; modify source specifications.
