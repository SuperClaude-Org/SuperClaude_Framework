# Repository Audit — Final Report

**Repository**: {repo name}
**Date**: YYYY-MM-DD
**Passes Completed**: {1, 2, 3 or subset}
**Audit Duration**: {total time}

---

## Executive Summary

- **Total files in repo**: {from git ls-files}
- **Total files audited**: {sum across all passes} ({coverage}%)
- **Actions identified**: DELETE {N}, CONSOLIDATE {N}, MOVE {N}, FLAG {N}
- **Broken references**: {N}
- **Files verified KEEP**: {N}
- **Estimated cleanup effort**: {hours} (DELETE: {h}, CONSOLIDATE: {h}, MOVE: {h}, FLAG: {h})

---

## Action Items by Priority

### Immediate (safe, no dependencies)
<!-- DELETE items with zero references confirmed, MOVE items with clear targets -->
1. [ ] DELETE `filepath` — {reason} (grep: 0 refs)
2. [ ] MOVE `filepath` → `new/path` — {reason}

### Requires Decision (needs human judgment)
<!-- REVIEW items, CONSOLIDATE items needing merge strategy -->
1. [ ] CONSOLIDATE `fileA` + `fileB` — {overlap}%, recommendation: keep {canonical}
2. [ ] REVIEW `filepath` — {why uncertain}

### Requires Code Changes (FLAG items)
<!-- Items needing developer intervention -->
1. [ ] FLAG `filepath` — {issue}: {required action}
2. [ ] BROKEN REF `source:line` → `missing/path` — {fix needed}

---

## Cross-Cutting Findings

### Finding 1: {Pattern Name}
- **Scope**: {how many files/directories affected}
- **Description**: {what the pattern is}
- **Impact**: {why it matters}
- **Recommendation**: {suggested action}

### Finding 2: {Pattern Name}
- **Scope**: {affected scope}
- **Description**: {pattern description}

---

## Discovered Issues Registry

Numbered list of all systemic issues found across all passes:

1. **{Issue title}** — {description}. Affects: {scope}. Severity: {high/medium/low}
2. **{Issue title}** — {description}. Affects: {scope}. Severity: {high/medium/low}

---

## Duplication Matrix (from Pass 3)

| File A | File B | Overlap % | Key Differences | Recommendation |
|--------|--------|-----------|-----------------|----------------|
| {path} | {path} | {N}% | {differences} | {action} |

---

## Audit Methodology

### Passes Executed
- **Pass 1 (Surface Scan)**: {file count} files, {batch count} batches, Haiku agents
- **Pass 2 (Structural Audit)**: {file count} files, {batch count} batches, Sonnet agents
- **Pass 3 (Cross-Cutting Sweep)**: {file count} files, {batch count} batches, Sonnet agents

### Quality Assurance
- **Spot-check rate**: 10% (5 findings per 50 files)
- **Validation pass rate**: {percentage}%
- **Failed reports regenerated**: {count}

### Exclusions
- Directories excluded: `.git/`, `node_modules/`, build outputs, caches, vendor
- Files not audited: {count} ({reason})

---

## Recommendations

### Process Improvements
1. {Recommendation for future audits}
2. {Recommendation for preventing recurrence}

### Suggested Workflow
1. Execute **Immediate** action items (safe DELETEs and MOVEs)
2. Review **Requires Decision** items with team
3. Schedule **Requires Code Changes** items into sprint backlog
4. Run `/sc:test` to verify no regressions after cleanup
5. Commit via `/sc:git` with audit reference

---

## Appendix: Pass Summaries

- [Pass 1 Summary](.claude-audit/pass1-summary.md)
- [Pass 2 Summary](.claude-audit/pass2-summary.md)
- [Pass 3 Summary](.claude-audit/pass3-summary.md)
