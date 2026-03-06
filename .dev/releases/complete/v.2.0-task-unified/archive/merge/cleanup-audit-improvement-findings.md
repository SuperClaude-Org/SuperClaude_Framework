# sc:cleanup-audit Improvement Findings

**Date**: 2026-02-20
**Method**: 4-agent parallel analysis of old manual prompts vs new sc:cleanup-audit output
**Scope**: CLEANUP-audit-prompt.md (1-4) vs .claude-audit/ and .claude-audit-2/ outputs

---

## Executive Summary

Four parallel analysis agents examined the old manual cleanup prompts against the new `sc:cleanup-audit` automated output across four dimensions: (1) architecture/structure, (2) profiling/evidence, (3) batch strategy/coverage, and (4) verification/quality. The old approach produced **44x more per-file profiles** (527+ vs 12), caught **critical security issues** the new version missed, and used sophisticated batch engineering that the new version entirely lacks.

### Quantified Gap

| Metric | Old Manual | New Automated | Ratio |
|--------|-----------|--------------|-------|
| Total passes | 4 | 3 | 0.75x |
| Files individually profiled | 527+ | 12 | 0.02x |
| Batch reports produced | 27 | 3 | 0.11x |
| Known issues tracked | 34 | 0 | N/A |
| File-type-specific rule sets | 8 | 0 | N/A |
| Documentation files audited | ~250 | 0 | N/A |
| Claim spot-checks performed | ~750 | 0 | N/A |
| Total output volume (est.) | 5,000-8,000 lines | ~640 lines | 0.08-0.13x |
| Broken references found | 34+ | 1 | 0.03x |

---

## Finding 1: Missing Pass 4 (Documentation Audit)

**Source**: Agent 1 (Architecture), Agent 2 (Profiling), Agent 4 (Verification)
**Severity**: CRITICAL
**Impact**: ~250 documentation files receive zero content verification

The old approach had a dedicated 4th pass for documentation quality with:
- **Claim spot-checking**: 3-5 technical claims per document verified against codebase
- **Temporal artifact classification**: Distinguishing "living reference" vs "temporal artifact"
- **Content overlap groups**: Grouping docs by topic to find duplication
- **ARCHIVE as a recommendation category**: For historically valuable but currently misleading documents
- **13 dedicated batch files** for documentation audit

The new version treats documentation as binary exists/doesn't-exist. Example gap: `docs/DOCUMENTATION_INDEX.md` references 4 non-existent directories -- old approach caught this, new missed it entirely.

**Recommendation**: Add Pass 4 with documentation-specific auditing methodology, claim spot-checking, and freshness scoring.

---

## Finding 2: Evidence-Mandatory KEEP Decisions Absent

**Source**: Agent 1, Agent 2, Agent 4
**Severity**: CRITICAL
**Impact**: ~5,780 files classified KEEP without any evidence

Old rule (verbatim): *"KEEP criteria -- ALL of these must be verified (not assumed)"* and *"Evidence for KEEP is mandatory. Don't just say 'looks legitimate.' Cite specific references."*

The new Pass 2 only profiles DELETE/REVIEW candidates. Anything classified KEEP in Pass 1 is never examined again. The old system's most valuable finding -- that `frontend/src/` is actively imported by Next.js `app/` and must NOT be deleted -- came from profiling a KEEP file.

**Recommendation**: Require at minimum a 3-field lightweight check for KEEP files: (1) references found?, (2) currently used evidence, (3) any hidden issues noted.

---

## Finding 3: No Batch Decomposition Strategy

**Source**: Agent 3 (Batch Strategy)
**Severity**: CRITICAL
**Impact**: 5,857 files handled monolithically instead of in manageable batches

The old approach split work into 26 targeted batches (Pass 3) + 13 doc batches (Pass 4) with:
- Explicit file lists per batch (every file assigned exactly once)
- Domain-calibrated depth (deep for source, grep-only for binary assets)
- Priority ordering (HIGH 1-4, MEDIUM 5-18, LOW 19-26)
- Cross-reference instructions between batches

The new approach uses 6 unnamed parallel scanners with no documented file assignments, depth calibration, or coverage guarantees. Result: 44x fewer per-file profiles.

**Recommendation**: Implement batch file list generation with domain-calibrated depth levels and explicit cross-reference instructions.

---

## Finding 4: No File-Type-Specific Verification Rules

**Source**: Agent 2, Agent 4
**Severity**: HIGH
**Impact**: Test files, scripts, compose files, and docs all receive identical shallow treatment

The old approach had 5+ specialized rule sets:

| File Type | Old Rules | New Treatment |
|-----------|-----------|---------------|
| **Test files** | Check pytest patterns, discovery path, skip markers, `input()` calls, duplicate helpers | Generic scan |
| **Scripts** | Check ports against network spec, flag destructive ops (`DROP ALL`, `rm -rf`), verify referenced files | Generic scan |
| **Docker/Compose** | Compare service definitions, verify Dockerfile references, check volume paths | Service count only |
| **Documentation** | Verify 3-5 claims, check architecture accuracy, assess freshness | Not performed |
| **Config/Env** | Check for committed secrets, compare across configs, verify references | Partial |

Example impact: Old approach found `deploy-prod-simple.sh` had port 8000 (should be 8102) AND contained `DROP ALL` Python -- both missed by new.

**Recommendation**: Add file-type-specific rule sets that trigger based on file extension/path patterns.

---

## Finding 5: No Known-Issue Tracking Between Passes

**Source**: Agent 1, Agent 4
**Severity**: HIGH
**Impact**: Redundant re-analysis and potential contradictory recommendations

The old Pass 3 prompt included a **34-item numbered list** of already-discovered issues with instruction: *"Do NOT flag these again."* Each subsequent pass acknowledged prior findings explicitly.

The new version has no inter-pass deduplication. Without this, later passes waste tokens re-analyzing known problems and may reach different conclusions about the same file.

**Recommendation**: Implement a known-issue registry (`known-issues.yml`) loaded at audit start, updated at audit end, with cross-pass deduplication.

---

## Finding 6: Security Content Scanning Too Shallow

**Source**: Agent 2, Agent 4
**Severity**: HIGH
**Impact**: Real credentials in `.env.production` misidentified as template values

The old approach READ the actual `.env.production` file and found 6 real credentials (API keys, DB passwords, JWT secrets, GitHub runner tokens). The new audit stated "CHANGE_ME_* placeholders (no real secrets)" -- it appears to have confused the template file with the actual file.

**Recommendation**: For any `.env*` file, credential file, or file containing patterns like `sk-`, `password`, `secret`, `token` -- read actual contents and flag real credentials vs templates.

---

## Finding 7: No Incremental Save Workflow

**Source**: Agent 1
**Severity**: MEDIUM
**Impact**: Context window exhaustion risk and crash recovery gap

The old approach mandated save-every-5-10-files with context refresh:
1. Create output file BEFORE auditing
2. Work in batches of 5-10 files, save after each
3. Never accumulate more than 10 unwritten results
4. Re-read output file before each save to refresh memory

The new version writes output once at completion with no checkpointing.

**Recommendation**: Implement save-and-checkpoint pattern for subagents, especially for large batches.

---

## Finding 8: Missing Cross-Reference Resolution Phase

**Source**: Agent 3
**Severity**: HIGH
**Impact**: Cross-boundary dead code undetectable

The old approach included explicit cross-reference instructions:
- "Cross-reference docker-compose files in root with Dockerfiles in infrastructure/"
- "Check if API endpoints are called from any frontend code"
- "Cross-reference manifest entries against files on disk"

The new parallel scanners cannot detect cross-boundary issues because each scanner operates in isolation.

**Recommendation**: Add a synthesis phase after domain scanners complete that traces cross-boundary dependencies.

---

## Finding 9: No Anti-Lazy-Agent Enforcement

**Source**: Agent 4
**Severity**: HIGH
**Impact**: Subagents can rubber-stamp files without reading them

Old rule (verbatim): *"Lazy agents who mark files KEEP without evidence will be caught"* and *"Actually verify claims. Don't just list directory contents. READ files, GREP for references, CHECK if described structures match reality."*

The new version has no enforcement mechanisms to prevent shallow analysis.

**Recommendation**: Add minimum tool-call requirements per profile, evidence audit trails, and random spot-check validation (10-20% of profiles re-verified by consolidation agent).

---

## Finding 10: Missing Recommendation Categories

**Source**: Agent 1, Agent 2
**Severity**: MEDIUM
**Impact**: Nuanced disposition decisions forced into binary DELETE/KEEP

The old approach used 5 categories: DELETE, FLAG, CONSOLIDATE, ARCHIVE, KEEP. The new version uses 3: DELETE, REVIEW, KEEP.

- **FLAG** (179 findings in old output): Files with specific issues needing human attention but NOT deletion candidates
- **CONSOLIDATE**: Multiple files that should be merged (e.g., 6 Playwright configs → 2)
- **ARCHIVE**: Historically valuable but currently misleading documents

**Recommendation**: Add FLAG, CONSOLIDATE, and ARCHIVE categories with clear criteria for each.

---

## Finding 11: Missing Progressive Depth Escalation

**Source**: Agent 1
**Severity**: MEDIUM
**Impact**: All files receive the same shallow depth regardless of pass number

Old depth progression:
| Pass | Read Depth | Verification |
|------|-----------|-------------|
| 1 (Surface) | First 20-30 lines | Filename grep only |
| 2 (Structural) | First 30-50 lines | 8-field mandatory profile |
| 3 (Cross-cutting) | 30-50 lines, full for configs | Cross-file comparison |
| 4 (Documentation) | 50-80 lines, full for short docs | 3-5 claim spot-checks |

**Recommendation**: Each pass should read progressively deeper into files, with later passes applying more intensive verification.

---

## Finding 12: Subagent Specialization Needed

**Source**: Agent 3
**Severity**: MEDIUM
**Impact**: Generic scanners miss domain-specific patterns

Recommended 5 specialized subagent types:
1. **infrastructure_auditor** (Sonnet): Docker/K8s/deploy validation, service cross-reference
2. **source_code_auditor** (Sonnet): Import/export tracing, dead route detection
3. **asset_auditor** (Haiku): Grep-only binary reference checking, 200 files/batch
4. **documentation_auditor** (Sonnet): Content comparison, claim verification
5. **cross_reference_synthesizer** (Sonnet): Post-scan synthesis, conflict resolution, confidence scoring

**Recommendation**: Replace 6 unnamed scanners with these 5 specialized types with documented capabilities and constraints.

---

## Finding 13: No Coverage Guarantee

**Source**: Agent 3, Agent 4
**Severity**: HIGH
**Impact**: Files may be skipped or double-counted without detection

The old approach guaranteed every file was examined exactly once via explicit file lists. The new approach has no mechanism to detect gaps or overlaps in scanner coverage.

**Recommendation**: Add coverage gate requiring 80%+ of files in scope to have at least one verification, with unexamined files auto-flagged as REVIEW.

---

## Finding 14: Broken Reference Collection Not Consolidated

**Source**: Agent 2
**Severity**: LOW
**Impact**: Broken references mentioned inline but not actionable as a group

The old approach produced a dedicated "Broken References Found" section with checkbox items. The new approach notes broken references inline but does not collect them.

**Recommendation**: Add a consolidated broken-references section in the final report.

---

## Finding 15: No Gitignore Consistency Checking

**Source**: Agent 4
**Severity**: MEDIUM
**Impact**: Files tracked despite .gitignore rules go undetected

Example: `test-ui-screenshot.png` was explicitly listed in .gitignore line 110 but still tracked by git. The old approach found this; the new approach did not.

**Recommendation**: Add a gitignore consistency check comparing `git ls-files` against `.gitignore` patterns.

---

## Priority Matrix for Incorporation

### Tier 1: Critical (Must Have)
1. **Finding 2**: Evidence-mandatory KEEP decisions
2. **Finding 3**: Batch decomposition strategy
3. **Finding 13**: Coverage guarantee

### Tier 2: High (Should Have)
4. **Finding 1**: Pass 4 documentation audit
5. **Finding 4**: File-type-specific verification rules
6. **Finding 5**: Known-issue tracking
7. **Finding 6**: Security content scanning depth
8. **Finding 8**: Cross-reference resolution phase
9. **Finding 9**: Anti-lazy-agent enforcement

### Tier 3: Medium (Nice to Have)
10. **Finding 7**: Incremental save workflow
11. **Finding 10**: Additional recommendation categories
12. **Finding 11**: Progressive depth escalation
13. **Finding 12**: Subagent specialization
14. **Finding 15**: Gitignore consistency checking

### Tier 4: Low (Enhancement)
15. **Finding 14**: Broken reference consolidation

---

*Generated by 4-agent parallel analysis | 2026-02-20*
