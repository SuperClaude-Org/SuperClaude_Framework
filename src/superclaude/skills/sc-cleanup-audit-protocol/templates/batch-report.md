# {Scope Description} Audit (Pass {N})

**Status**: In Progress / Complete
**Files audited**: X / Y total
**Date**: YYYY-MM-DD
**Agent**: {agent-type}
**Batch**: {batch-number}

---

## Files to DELETE
### `filepath`
- **What it does**: {1-2 sentence description}
- **Nature**: {script / test / doc / config / source code / data / asset / migration / one-time artifact}
- **References**: {grep results — pattern used, match count, zero-result confirmation}
- **Dynamic loading check**: {checked all 5 patterns — none apply}
- **CI/CD usage**: {not referenced by any automation}
- **Evidence**: Why this should be deleted — {grep pattern + count + zero-result}
- **Recommendation**: DELETE — {reason}

---

## Files to CONSOLIDATE (Pass 3 only)
### `filepath` → merge with `other/filepath`
- **What it does**: {description of both files}
- **Overlap**: {quantified — % identical or key sections that match}
- **Key differences**: {what's unique in each}
- **Recommendation**: CONSOLIDATE — keep {canonical}, merge unique parts from {other}

---

## Files to MOVE
### `filepath` → `new/path`
- **What it does**: {description}
- **Why move**: {current location incorrect because...}
- **Target rationale**: {new location is correct because...}
- **References to update**: {list of files referencing this path}
- **Recommendation**: MOVE — {reason}

---

## Files to FLAG
### `filepath`
- **Finding type**: {MISPLACED / STALE / STRUCTURAL ISSUE / BROKEN REFS}
- **What it does**: {description}
- **Issue**: {what needs handling}
- **Required action**: {specific enough to execute}
- **Impact scope**: {which files/systems affected}
- **Verification checklist**: {what evidence would settle this?}
- **Recommendation**: FLAG — {reason}

---

## Broken References Found
- [ ] `source-filepath:line` → references `missing/path` — {context}

---

## Files to KEEP (verified legitimate)
- `filepath` — Nature: {type}. References: {specific citations with file:line}. Verification: {what was checked}

---

## Remaining / Not Audited
<!-- MANDATORY if scope was not completed — transparency beats pretending completeness -->
- `filepath` — not reached (reason: {batch limit / time constraint / error})

---

## Summary
- **Total files audited**: X / Y assigned
- **DELETE**: N | **CONSOLIDATE**: N | **MOVE**: N | **FLAG**: N | **KEEP**: N
- **Broken references found**: N
- **Coverage**: X/Y = {percentage}%

## Notes
{Cross-cutting observations, patterns, recommendations for other agents/passes}
