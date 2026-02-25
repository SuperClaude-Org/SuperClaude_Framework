# D-0018 Evidence — `lint-architecture` Target Verification

**Task:** T03.02
**Date:** 2026-02-24

## Verification

`make lint-architecture` target exists, is executable, and produces expected output for all 6 implemented checks.

### Check Coverage

- Check 1 (Command→Skill): 8 bidirectional links verified
- Check 2 (Skill→Command): 8 reverse links verified
- Check 3 (Size WARN): Correctly warns on spec-panel.md (435 lines) and task-mcp.md (375 lines)
- Check 4 (Size ERROR): No commands exceed 500-line hard limit
- Check 6 (Activation present): All 8 paired commands have `## Activation`
- Check 8 (Frontmatter): All 8 protocol skills have complete frontmatter
- Check 9 (Naming): All 8 protocol skills have `-protocol` suffix in `name:` field
- Checks 5/7: Correctly reported as NEEDS DESIGN (skipped)

### Discoverability

```
$ make help | grep lint
  make lint-architecture - Enforce architecture policy (6 of 10 checks)
```

## Acceptance Criteria

- [x] `lint-architecture` target exists in Makefile and is executable
- [x] All 6 checks (#1, #2, #3, #4, #6, #8, #9) implemented per §11 specifications
- [x] Any ERROR → `exit 1` (CI failure); warnings only → `exit 0`
- [x] Target discoverable via `make help`
