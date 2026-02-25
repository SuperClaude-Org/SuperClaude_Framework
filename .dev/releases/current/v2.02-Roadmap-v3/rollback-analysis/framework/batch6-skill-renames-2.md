# Batch 6: Skill Directory Renames (Part 2) - sc-task-unified & sc-validate-tests

## Analysis Date: 2026-02-24
## Branch: feature/v2.01-Roadmap-V3

---

## Overview

This batch covers the remaining two skill directory renames that include content modifications (R099). Both follow the same `-protocol` suffix rename pattern as batch 5.

---

## File 1: sc-task-unified SKILL.md

### Rename Pattern
```
src/superclaude/skills/sc-task-unified/SKILL.md
  -> src/superclaude/skills/sc-task-unified-protocol/SKILL.md
```

**Git Status**: `R099` (rename with 99% similarity -- content modified)

### Content Modification

The ONLY change is in the YAML frontmatter `name` field (line 2):

| Field | Old Value | New Value |
|-------|-----------|-----------|
| `name` | `sc-task-unified` | `sc:task-unified-protocol` |

Key observations:
- The `name` field changed from hyphenated (`sc-task-unified`) to colon-prefixed with `-protocol` suffix (`sc:task-unified-protocol`)
- Note the inconsistency: the directory uses a hyphen (`sc-task-unified-protocol`) but the frontmatter name uses a colon (`sc:task-unified-protocol`)
- The `description` field is unchanged
- The `allowed-tools` field is unchanged
- All body content (308 lines) is identical

### Companion Files (Pure Renames)

| Status | Old Path | New Path |
|--------|----------|----------|
| R100 | `src/superclaude/skills/sc-task-unified/__init__.py` | `src/superclaude/skills/sc-task-unified-protocol/__init__.py` |

**Total files in skill**: 2 (1 modified SKILL.md + 1 pure-rename `__init__.py`)

---

## File 2: sc-validate-tests SKILL.md

### Rename Pattern
```
src/superclaude/skills/sc-validate-tests/SKILL.md
  -> src/superclaude/skills/sc-validate-tests-protocol/SKILL.md
```

**Git Status**: `R099` (rename with 99% similarity -- content modified)

### Content Modification

The ONLY change is in the YAML frontmatter `name` field (line 2):

| Field | Old Value | New Value |
|-------|-----------|-----------|
| `name` | `sc-validate-tests` | `sc:validate-tests-protocol` |

Key observations:
- Same pattern as sc-task-unified: hyphenated name changed to colon-prefixed with `-protocol` suffix
- Same directory-vs-frontmatter inconsistency (directory uses hyphen, frontmatter uses colon)
- The `description` field is unchanged
- The `allowed-tools` field is unchanged
- All body content (438 lines) is identical

### Companion Files (Pure Renames)

| Status | Old Path | New Path |
|--------|----------|----------|
| R100 | `src/superclaude/skills/sc-validate-tests/__init__.py` | `src/superclaude/skills/sc-validate-tests-protocol/__init__.py` |
| R100 | `src/superclaude/skills/sc-validate-tests/classification-algorithm.yaml` | `src/superclaude/skills/sc-validate-tests-protocol/classification-algorithm.yaml` |

**Total files in skill**: 3 (1 modified SKILL.md + 2 pure-rename companion files)

---

## Complete R100 (Pure Rename) Inventory Across ALL Skills

All 25 pure-rename files from the entire skill rename operation:

### sc-adversarial -> sc-adversarial-protocol (5 files)
| Old Path | New Path |
|----------|----------|
| `sc-adversarial/__init__.py` | `sc-adversarial-protocol/__init__.py` |
| `sc-adversarial/refs/agent-specs.md` | `sc-adversarial-protocol/refs/agent-specs.md` |
| `sc-adversarial/refs/artifact-templates.md` | `sc-adversarial-protocol/refs/artifact-templates.md` |
| `sc-adversarial/refs/debate-protocol.md` | `sc-adversarial-protocol/refs/debate-protocol.md` |
| `sc-adversarial/refs/scoring-protocol.md` | `sc-adversarial-protocol/refs/scoring-protocol.md` |

### sc-cleanup-audit -> sc-cleanup-audit-protocol (10 files)
| Old Path | New Path |
|----------|----------|
| `sc-cleanup-audit/__init__.py` | `sc-cleanup-audit-protocol/__init__.py` |
| `sc-cleanup-audit/rules/dynamic-use-checklist.md` | `sc-cleanup-audit-protocol/rules/dynamic-use-checklist.md` |
| `sc-cleanup-audit/rules/pass1-surface-scan.md` | `sc-cleanup-audit-protocol/rules/pass1-surface-scan.md` |
| `sc-cleanup-audit/rules/pass2-structural-audit.md` | `sc-cleanup-audit-protocol/rules/pass2-structural-audit.md` |
| `sc-cleanup-audit/rules/pass3-cross-cutting.md` | `sc-cleanup-audit-protocol/rules/pass3-cross-cutting.md` |
| `sc-cleanup-audit/rules/verification-protocol.md` | `sc-cleanup-audit-protocol/rules/verification-protocol.md` |
| `sc-cleanup-audit/scripts/repo-inventory.sh` | `sc-cleanup-audit-protocol/scripts/repo-inventory.sh` |
| `sc-cleanup-audit/templates/batch-report.md` | `sc-cleanup-audit-protocol/templates/batch-report.md` |
| `sc-cleanup-audit/templates/final-report.md` | `sc-cleanup-audit-protocol/templates/final-report.md` |
| `sc-cleanup-audit/templates/finding-profile.md` | `sc-cleanup-audit-protocol/templates/finding-profile.md` |
| `sc-cleanup-audit/templates/pass-summary.md` | `sc-cleanup-audit-protocol/templates/pass-summary.md` |

### sc-roadmap -> sc-roadmap-protocol (5 files)
| Old Path | New Path |
|----------|----------|
| `sc-roadmap/__init__.py` | `sc-roadmap-protocol/__init__.py` |
| `sc-roadmap/refs/adversarial-integration.md` | `sc-roadmap-protocol/refs/adversarial-integration.md` |
| `sc-roadmap/refs/extraction-pipeline.md` | `sc-roadmap-protocol/refs/extraction-pipeline.md` |
| `sc-roadmap/refs/scoring.md` | `sc-roadmap-protocol/refs/scoring.md` |
| `sc-roadmap/refs/templates.md` | `sc-roadmap-protocol/refs/templates.md` |
| `sc-roadmap/refs/validation.md` | `sc-roadmap-protocol/refs/validation.md` |

### sc-task-unified -> sc-task-unified-protocol (1 file)
| Old Path | New Path |
|----------|----------|
| `sc-task-unified/__init__.py` | `sc-task-unified-protocol/__init__.py` |

### sc-validate-tests -> sc-validate-tests-protocol (2 files)
| Old Path | New Path |
|----------|----------|
| `sc-validate-tests/__init__.py` | `sc-validate-tests-protocol/__init__.py` |
| `sc-validate-tests/classification-algorithm.yaml` | `sc-validate-tests-protocol/classification-algorithm.yaml` |

**All paths relative to `src/superclaude/skills/`**

---

## Rollback Instructions

### To Rollback sc-task-unified
```bash
# Move directory back
git mv src/superclaude/skills/sc-task-unified-protocol src/superclaude/skills/sc-task-unified

# Restore frontmatter name field in SKILL.md
# Change line 2: `name: sc:task-unified-protocol` -> `name: sc-task-unified`
```

### To Rollback sc-validate-tests
```bash
# Move directory back
git mv src/superclaude/skills/sc-validate-tests-protocol src/superclaude/skills/sc-validate-tests

# Restore frontmatter name field in SKILL.md
# Change line 2: `name: sc:validate-tests-protocol` -> `name: sc-validate-tests`
```

---

## Summary

| Skill | Git Status | Content Change | Companion Files (R100) | Total Files |
|-------|------------|----------------|------------------------|-------------|
| sc-task-unified | R099 | Frontmatter `name` only | 1 | 2 |
| sc-validate-tests | R099 | Frontmatter `name` only | 2 | 3 |

**Cross-batch total (all 5 skills)**: 5 modified SKILL.md files (R099) + 25 pure-rename companion files (R100) = 30 files renamed

### Modification Pattern (Consistent Across All 5 Skills)
- Directory: `sc-{name}` -> `sc-{name}-protocol` (hyphenated)
- Frontmatter `name`: `sc-{name}` -> `sc:{name}-protocol` (colon-prefixed)
- Body content: No changes in any skill
