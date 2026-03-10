# D-0039 — Evidence: Stale Reference Scan Results

**Task**: T06.08
**Date**: 2026-02-24
**Status**: COMPLETE

## Scan Methodology

Searched for all 5 old skill directory names across `src/`, `.claude/`, and `docs/`:
- Pattern: `sc-adversarial/`, `sc-cleanup-audit/`, `sc-roadmap/`, `sc-task-unified/`, `sc-validate-tests/`
- Exclusions: Tasklist files (self-referential), `.dev/` planning artifacts

## Results: `src/` and `.claude/` (Source Code)

### `sc-adversarial/` — Zero matches
### `sc-cleanup-audit/` — Zero matches
### `sc-roadmap/` — Zero matches
### `sc-validate-tests/` — Zero matches (fixed in T06.06, BUG-002)

### `sc-task-unified/` — Contextual matches (not stale skill references)

Found in `validate-tests.md` and `sc-validate-tests-protocol/SKILL.md`:
```
tests/sc-task-unified/   (test directory path, not skill directory)
```

**Assessment**: These reference `tests/sc-task-unified/` — a test directory for the task-unified command's behavioral test specs. Test directories use command names (e.g., `tests/sc-roadmap/` exists), not skill names with `-protocol` suffix. These are **not stale skill directory references**.

Evidence: `tests/sc-roadmap/` (without `-protocol`) is the existing test directory for the roadmap command, confirming test directories follow command naming.

## Results: `docs/` (Documentation)

### `docs/generated/` — Historical research artifacts

Found references to old skill names in generated documentation research extracts:
- `docs/generated/SuperClaude-Developer-Guide-Commands-Skills-Agents.md`
- `docs/generated/dev-guide-research/extract-*.md` (multiple files)

**Assessment**: These are historical research artifacts generated during prior documentation sprints. They capture point-in-time snapshots of the codebase structure. The old names are accurate for the time they were generated. These files are in `docs/generated/` which contains auto-generated content.

## Summary

| Old Name | `src/` | `.claude/` | `docs/` | Status |
|----------|--------|-----------|---------|--------|
| `sc-adversarial/` | 0 | 0 | Historical only | **PASS** |
| `sc-cleanup-audit/` | 0 | 0 | Historical only | **PASS** |
| `sc-roadmap/` | 0 | 0 | Historical only | **PASS** |
| `sc-task-unified/` | 0 (test dir refs only) | 0 (test dir refs only) | Historical only | **PASS** |
| `sc-validate-tests/` | 0 | 0 | 0 | **PASS** |

**SC-009**: Zero stale references to old skill directory names in source code — **PASS**

## Scan Methodology for Future Regression

```bash
# Run from repo root. Should return empty for each pattern.
for name in sc-adversarial sc-cleanup-audit sc-roadmap sc-task-unified sc-validate-tests; do
  echo "=== $name/ ==="
  grep -rn "skills/$name/" src/ .claude/ --include="*.md" || echo "(clean)"
done
```

Note: Use `skills/$name/` pattern (not bare `$name/`) to exclude legitimate test directory references like `tests/sc-task-unified/`.

*Artifact produced by T06.08*
