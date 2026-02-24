# D-0021 Evidence — Negative Lint Test

**Task:** T03.05
**Date:** 2026-02-24

## Test Methodology

1. Backed up `src/superclaude/commands/adversarial.md`
2. Removed `## Activation` section from `adversarial.md`
3. Ran `make lint-architecture`
4. Captured output and exit code
5. Restored `adversarial.md` from backup
6. Verified lint passes again after restoration

## Violation Introduced

Removed the `## Activation` section (6 lines) from `adversarial.md`, which is paired with `sc-adversarial-protocol/`.

## Result with Violation

Exit code: **1** (non-zero, as expected)

### Error Output
```
  ❌ ERROR [Check 6]: adversarial.md missing ## Activation (paired with sc-adversarial-protocol)
```

### Summary Line
```
  Errors:   1
  Warnings: 2
  ❌ FAIL — 1 error(s) found. Fix before proceeding.
```

## Restoration Verification

After restoring `adversarial.md`:
```
  Errors:   0
  Warnings: 2
  ✅ PASS — architecture policy compliant (2 warning(s))
```

Exit code: **0**

## Acceptance Criteria

- [x] `make lint-architecture` exits 1 when `## Activation` is absent from a paired command
- [x] Error message clearly identifies the violation (file name: `adversarial.md`, check number: Check 6)
- [x] Tree is restored to compliant state after negative test
- [x] Test methodology documented for reproducibility
