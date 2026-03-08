# D-0006: Evidence — YAML Frontmatter Promotion and verify-sync Coverage

**Task**: T01.05
**Roadmap Items**: R-011, R-012
**Date**: 2026-03-08

## YAML Frontmatter

`sc-cli-portify-protocol/SKILL.md` now contains all 8 required frontmatter fields:

```yaml
---
name: sc-cli-portify-protocol
description: "Full behavioral protocol for sc:cli-portify — ..."
category: development
complexity: high
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
mcp-servers: [sequential, serena, context7, auggie-mcp]
personas: [architect, analyzer, backend]
argument-hint: "--workflow <skill-name-or-path> [--name <cli-name>] [--output <dir>] [--dry-run] [--skip-integration]"
---
```

## verify-sync Coverage

`make verify-sync` output confirms `sc-cli-portify-protocol` is included:

```
=== Skills ===
  ✅ sc-cli-portify-protocol
  ✅ sc-cli-portify
  ...
```

**Note**: `make verify-sync` exits non-zero due to two pre-existing drift issues unrelated to this task:
- `sc-forensic-qa-protocol`: missing in `.claude/skills/` (exists in `src/` only)
- `skill-creator`: missing in `src/superclaude/skills/` (exists in `.claude/` only)

Our `sc-cli-portify-protocol/` directory shows ✅ in both `src/` and `.claude/` locations.
