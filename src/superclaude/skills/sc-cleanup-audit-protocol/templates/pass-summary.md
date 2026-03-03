# Pass {N} Summary — {Pass Name}

**Date Range**: YYYY-MM-DD to YYYY-MM-DD
**Total Batches**: {N}
**Total Files Audited**: {X} / {Y} in scope
**Coverage**: {percentage}%

---

## Aggregate Summary

| Category | Count | % of Total |
|----------|-------|-----------|
| DELETE | N | % |
| CONSOLIDATE | N | % |
| MOVE | N | % |
| FLAG | N | % |
| KEEP | N | % |
| BROKEN REF | N | % |
| **Total** | **N** | **100%** |

---

## Coverage Metrics

- **Files in scope**: {total from repo-inventory.sh}
- **Files audited**: {sum across all batches}
- **Coverage percentage**: {audited / in_scope * 100}%
- **Files not reached**: {list or count}
- **Exclusions applied**: {.git, node_modules, build outputs, caches, vendor}

---

## Cross-Agent Patterns

Systemic findings detected across multiple batches:

### Pattern 1: {Name}
- **Observed in**: Batches {list}
- **Description**: {what the pattern is}
- **Impact**: {scope of the pattern}
- **Recommendation**: {suggested action}

### Pattern 2: {Name}
- **Observed in**: Batches {list}
- **Description**: {what the pattern is}

---

## Validation Results (Spot-Check)

- **Files spot-checked**: {N} (10% of total audited)
- **Discrepancies found**: {N}
- **Discrepancy details**:
  - `filepath`: Agent claimed {X}, verification found {Y}
- **Validation status**: PASS / FAIL

---

## Deduplication Notes

Findings appearing in multiple batches (consolidated here):

- **{Finding}**: Originally flagged in Batches {A, B}. Consolidated as single finding #{N}
- **{Finding}**: Originally flagged in Batches {C, D}. Consolidated as single finding #{N}

---

## Quality Gate Status

| Gate | Status | Evidence |
|------|--------|---------|
| All batches complete | PASS/FAIL | {N}/{M} batches completed |
| Required sections present | PASS/FAIL | {sections present in all reports} |
| Mandatory profiles complete | PASS/FAIL | {profile completion rate}% |
| Spot-check validation | PASS/FAIL | {discrepancy count} |
| Coverage threshold met | PASS/FAIL | {actual}% vs {target}% |

**Overall Pass Status**: PASS / FAIL

---

## Batch Reports Index

| Batch | Agent | Files | Status | Report Path |
|-------|-------|-------|--------|-------------|
| 1 | {type} | N | Complete | `.claude-audit/pass{N}/batch-01.md` |
| 2 | {type} | N | Complete | `.claude-audit/pass{N}/batch-02.md` |

---

## Notes for Next Pass

{Observations and context to carry forward to Pass N+1}
