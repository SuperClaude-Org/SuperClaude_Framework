# Patch Checklist
Generated: 2026-03-13
Total edits: 2 across 1 file

## File-by-file edit checklist

- phase-3-tasklist.md
  - [ ] Add mandatory completeness note to T03.02 (from finding M1)
  - [ ] Update T03.06 acceptance criterion with time.monotonic() (from finding M2)

## Cross-file consistency sweep
- [ ] No cross-file edits needed (both findings are in phase-3-tasklist.md)

---

## Precise diff plan

### 1) phase-3-tasklist.md

#### Section/heading to change: T03.02

**A. Add mandatory completeness note**
Current issue: T03.02 does not convey the mandatory/contract-strength completeness requirement from the roadmap.
Change: Add a Notes line after the existing Rollback line in T03.02.
Diff intent:
- Before: `**Rollback:** git checkout -- src/superclaude/cli/cli_portify/validate_config.py`
- After: `**Rollback:** git checkout -- src/superclaude/cli/cli_portify/validate_config.py` followed by `**Notes:** Completeness is mandatory per spec -- incomplete serialization would cause downstream contract/resume telemetry to lose data silently. Missing fields must be treated as a contract violation, not best-effort.`

#### Section/heading to change: T03.06

**B. Add time.monotonic() to acceptance criterion**
Current issue: T03.06 acceptance criterion says "Resolution timing test completes in <1 second" without specifying measurement method.
Change: Update the fourth acceptance criterion bullet in T03.06.
Diff intent:
- Before: `- Resolution timing test completes in <1 second`
- After: `- Resolution timing test using time.monotonic() assertions completes in <1 second (NFR-001)`
