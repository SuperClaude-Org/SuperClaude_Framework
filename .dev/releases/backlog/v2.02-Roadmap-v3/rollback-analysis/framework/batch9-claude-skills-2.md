# Batch 9: .claude/skills/ Protocol Directories (Part 2)

**Scope**: `sc-task-unified-protocol/` and `sc-validate-tests-protocol/`
**Status**: NEW untracked directories in `.claude/skills/`
**Analysis date**: 2026-02-24

---

## 1. `.claude/skills/sc-task-unified-protocol/`

### Files

| File | Size | Lines |
|------|------|-------|
| `SKILL.md` | 10,393 bytes | 308 |

**Total**: 1 file

### SKILL.md Header (first 20 lines)

```yaml
---
name: sc:task-unified-protocol
description: Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation. Merges orchestration capabilities with MCP compliance into a single coherent interface.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

Defines the `/sc:task-unified` skill with mandatory classification header output (TIER, CONFIDENCE, KEYWORDS, OVERRIDE, RATIONALE) as the very first output before any analysis.

### Mirror Verification against `src/superclaude/skills/sc-task-unified-protocol/`

| File | .claude/ | src/ | Match |
|------|----------|------|-------|
| `SKILL.md` | Present (10,393 B) | Present (10,393 B) | IDENTICAL |
| `__init__.py` | **Missing** | Present (32 B, `# sc-task-unified skill package`) | Expected omission |

**Verdict**: Content is identical. The `.claude/` copy correctly omits `__init__.py` (Python packaging artifact not needed by Claude Code runtime).

### Rename Context

- **Old directory**: `src/superclaude/skills/sc-task-unified/` (no longer exists)
- **New directory**: `src/superclaude/skills/sc-task-unified-protocol/`
- Git status shows: `RM src/superclaude/skills/sc-task-unified/SKILL.md -> src/superclaude/skills/sc-task-unified-protocol/SKILL.md`
- The SKILL.md was both **renamed** (directory move) and **modified** (content changes)

---

## 2. `.claude/skills/sc-validate-tests-protocol/`

### Files

| File | Size | Lines |
|------|------|-------|
| `SKILL.md` | 12,643 bytes | 438 |
| `classification-algorithm.yaml` | 11,844 bytes | 503 |

**Total**: 2 files

### SKILL.md Header (first 20 lines)

```yaml
---
name: sc:validate-tests-protocol
description: Validate tier classification behavior against YAML test specifications. Self-validation skill for /sc-task-unified command testing.
allowed-tools: Read, Glob, Grep, TodoWrite
---
```

Defines the `/sc:validate-tests` self-validation skill that tests Claude's own tier classification and behavioral compliance against YAML specification files.

### Mirror Verification against `src/superclaude/skills/sc-validate-tests-protocol/`

| File | .claude/ | src/ | Match |
|------|----------|------|-------|
| `SKILL.md` | Present (12,643 B) | Present (12,643 B) | IDENTICAL |
| `classification-algorithm.yaml` | Present (11,844 B) | Present (11,844 B) | IDENTICAL |
| `__init__.py` | **Missing** | Present (34 B, `# sc-validate-tests skill package`) | Expected omission |

**Verdict**: All distributable content is identical. The `.claude/` copy correctly omits `__init__.py`.

### Rename Context

- **Old directory**: `src/superclaude/skills/sc-validate-tests/` (no longer exists)
- **New directory**: `src/superclaude/skills/sc-validate-tests-protocol/`
- Git status shows: `RM src/superclaude/skills/sc-validate-tests/SKILL.md -> src/superclaude/skills/sc-validate-tests-protocol/SKILL.md`
- The SKILL.md was both **renamed** (directory move) and **modified** (content changes)

---

## Summary

### Relationship to `src/`

Both `.claude/skills/` directories are **dev copies** of their `src/superclaude/skills/` counterparts, consistent with the project's component sync architecture:

- **Source of truth**: `src/superclaude/skills/sc-*-protocol/`
- **Dev copies**: `.claude/skills/sc-*-protocol/` (read by Claude Code at runtime)
- **Sync mechanism**: `make sync-dev` copies src -> .claude, omitting `__init__.py`

### Rename Pattern

Both directories follow the same rename pattern applied across all 5 skill packages in this branch:

| Old Name | New Name |
|----------|----------|
| `sc-task-unified` | `sc-task-unified-protocol` |
| `sc-validate-tests` | `sc-validate-tests-protocol` |

The `-protocol` suffix was added to all skill directory names for naming consistency.

### Content Integrity

| Directory | Files in .claude/ | Content Match | Missing (expected) |
|-----------|-------------------|---------------|-------------------|
| `sc-task-unified-protocol` | 1 (SKILL.md) | All IDENTICAL | `__init__.py` |
| `sc-validate-tests-protocol` | 2 (SKILL.md, classification-algorithm.yaml) | All IDENTICAL | `__init__.py` |

### Rollback Notes

- These are **new untracked directories** -- rollback means simply deleting them
- The old `.claude/skills/sc-task-unified/` and `.claude/skills/sc-validate-tests/` directories no longer exist (were never tracked or already removed)
- To rollback, also revert the corresponding `src/superclaude/skills/` renames
