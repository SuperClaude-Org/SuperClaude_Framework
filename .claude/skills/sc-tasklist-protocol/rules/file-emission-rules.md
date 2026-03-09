# File Emission Rules

Read-only reference extracted from SKILL.md Section 3.3. This file exists for human review; the skill uses its own inline copy.

---

## File Count

The generator produces exactly **N+1 files** during generation (Stages 1-6) where N = number of phases. Stages 7-10 produce up to 2 additional validation artifacts in `TASKLIST_ROOT/validation/`:

1. **`tasklist-index.md`** -- Contains: metadata, artifact paths, source snapshot, deterministic rules, registries, traceability matrix, templates, glossary
2. **`phase-1-tasklist.md`** through **`phase-N-tasklist.md`** -- Contains: phase heading, phase goal, tasks (in order), inline checkpoints, end-of-phase checkpoint

---

## Naming Convention

Phase files MUST use the `phase-N-tasklist.md` convention (canonical Sprint CLI convention). Do not emit mixed aliases unless explicitly requested.

---

## Phase Heading Format

MUST be `# Phase N -- <Name>` (level 1 heading, em-dash separator, name <= 50 chars).

This format is required for Sprint CLI TUI display name extraction.

---

## Index References

The "Phase Files" table in the index MUST contain **literal filenames** (e.g., `phase-1-tasklist.md`), not path-prefixed references, so the Sprint CLI regex can discover them.

---

## Content Boundary

Phase files contain ONLY tasks belonging to that phase. No cross-phase metadata, no registries, no global templates.

---

## Target Directory Layout

The generator output must conform to this structure:

```text
TASKLIST_ROOT/
  tasklist-index.md
  phase-1-tasklist.md
  phase-2-tasklist.md
  ...
  phase-N-tasklist.md
  artifacts/
  evidence/
  checkpoints/
  validation/
  execution-log.md
  feedback-log.md
```
