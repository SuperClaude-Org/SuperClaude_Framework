# `/sc:repo-audit` — Multi-Pass Repository Cleanup Audit Command

## Command Specification (Custom Command PRD)

**Version**: 1.0
**Derived From**: Analysis of a 3-pass audit methodology applied to a ~1,458-file monorepo (FastAPI + Next.js + Terraform + Docker)
**Effectiveness Score**: 75/100 (see Phase 3 below)

---

## 1. Command Name & Purpose

```
/sc:repo-audit [target] [--pass 1|2|3|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]
```

**Purpose**: Systematically audit a repository for dead code, organizational debt, configuration sprawl, duplication, and broken references through a multi-pass escalation model. Each pass increases in depth and cross-cutting scope, producing actionable per-file profiles with evidence-backed recommendations.

**Category**: Quality / Maintenance
**Wave-Enabled**: Yes (complexity ≥ 0.7 auto-triggers multi-agent orchestration)
**Performance Profile**: Complex

---

## 2. Objectives (Generic)

1. **Identify dead code and orphaned files** across all file types (source, config, scripts, docs, assets, IaC)
2. **Detect organizational debt** — files in wrong locations, naming inconsistencies, stale documentation
3. **Find cross-cutting duplication** — competing config patterns, overlapping deploy scripts, near-duplicate files
4. **Produce evidence-backed recommendations** — every DELETE/MOVE/FLAG has verifiable proof, not assumptions
5. **Maintain safety** — read-only operation, conservative bias, incremental saves, no false-positive deletions

---

## 3. Multi-Pass Architecture

The core innovation is a **3-pass escalation model** where each pass increases in analytical depth and cross-cutting scope.

### Pass 1: Surface Scan (Junk Detection)

**Goal**: Quickly identify obvious waste — test artifacts, runtime files committed by accident, empty placeholders, files nothing references.

**Question Each File Must Answer**: "Is this file junk?"

**Classification Taxonomy (3-tier)**:
| Category | Meaning | Action |
|----------|---------|--------|
| **DELETE** | No references, no value, clearly obsolete | Safe to remove |
| **REVIEW** | Uncertain — may be needed, needs human judgment | Escalate to human |
| **KEEP** | Actively referenced, part of build/runtime/CI | Leave in place |

**Verification Protocol**:
1. Read first 20-30 lines to understand purpose
2. Grep for filename across repo (exclude `.git/`, `node_modules/`, build artifacts)
3. Check if imported/sourced by other files
4. Categorize with brief justification

**Output Schema**: Checklist format
```markdown
## Safe to Delete
- [ ] `filename` — reason

## Need Decision
- [ ] `filename` — what it is, why uncertain

## Keep (verified legitimate)
- `filename` — why needed

## Add to .gitignore
- `pattern` — reason
```

**Agent Batch Size**: 25-50 files per agent
**Expected Depth**: Light (5-10 min per batch of 25 files)
**Expected Coverage**: 100% of repo files at surface level

---

### Pass 2: Structural Audit (Organizational Integrity)

**Goal**: Find problems the surface scan missed — misplaced files, stale documentation, broken references, structural inconsistencies. This pass READS files and VERIFIES claims.

**Question Each File Must Answer**: "Is this file in the right place, correctly documented, and structurally sound?"

**Classification Taxonomy (5-tier)**:
| Category | Meaning | Action |
|----------|---------|--------|
| **DELETE** | Confirmed dead with evidence | Remove |
| **MOVE** | Valid but wrong location | Relocate |
| **FLAG** | Needs code changes, not just file ops | Developer action |
| **KEEP** | Verified correct with evidence | Leave in place |
| **BROKEN REF** | References non-existent paths/files | Fix reference |

**Verification Protocol (Mandatory Per-File Profile)**:

Every file audited MUST have a structured profile with these fields:

| Field | Requirement |
|-------|-------------|
| **What it does** | 1-2 sentence plain-English explanation |
| **References** | Who/what references this file? Grep results with files + line numbers. "None found" is valid. |
| **Superseded?** | Is there a newer/better version? Check for `_v2`, `_enhanced`, `_new` variants |
| **Nature** | Classify: `script`, `test`, `doc`, `config`, `source code`, `data`, `asset`, `migration`, `one-time artifact` |
| **CI/CD usage** | Called by ANY automation? Check workflows, compose files, Makefile, package.json, Dockerfiles |
| **Duplicate coverage?** | (tests/docs only) Does another file cover the same thing? |
| **Recommendation** | DELETE / MOVE (where) / FLAG (what) / KEEP (evidence) |

**Extra Rules by File Type**:
- **Tests**: Check discovery (is it in a test-discovered path?), check patterns (pytest vs manual), check if it would actually pass
- **Scripts**: Check if functionality is handled by a canonical script, check schema/field names are current
- **Documentation**: Verify 3-5 technical claims against implementation. Don't just check "do referenced files exist" — verify described architecture matches reality
- **Config**: Compare with similar configs, check if values match current architecture

**Scope**: Only files marked KEEP or REVIEW from Pass 1 (skip already-deleted files)
**Agent Batch Size**: 20-30 files per agent (deeper analysis = fewer files)
**Expected Depth**: Deep (20-40 min per batch)

---

### Pass 3: Cross-Cutting Sweep (Systemic Patterns)

**Goal**: Find duplication, sprawl, and broken references that span directory boundaries — problems per-directory audits inherently miss.

**Question Each File Must Answer**: "Does this file duplicate or conflict with another file elsewhere in the repo?"

**Classification Taxonomy (6-tier, adds CONSOLIDATE)**:
| Category | Meaning | Action |
|----------|---------|--------|
| **DELETE** | Confirmed dead | Remove |
| **CONSOLIDATE** | Merge with identified similar file | Keep one, merge unique parts |
| **MOVE** | Valid but wrong location | Relocate |
| **FLAG** | Needs code changes | Developer action |
| **KEEP** | Verified unique purpose with evidence | Leave in place |
| **BROKEN REF** | References non-existent paths | Fix reference |

**Verification Protocol (Per-File Profile)**:

| Field | Requirement |
|-------|-------------|
| **What it does** | 1-2 sentence explanation |
| **Nature** | File type classification |
| **References** | Grep results with files + line numbers |
| **Similar files** | Other files serving same/overlapping purpose. If found, quantify % overlap or key differences |
| **Superseded?** | Newer/better version exists? |
| **Currently used?** | Referenced by running app, CI/CD, build? Evidence required. |
| **Recommendation** | DELETE / CONSOLIDATE (with what) / MOVE / FLAG / KEEP |

**Critical Differentiators from Pass 2**:
1. **Compare, don't just catalog** — when you find similar files, DIFF them and quantify overlap
2. **Group audit** — audit similar files together (all docker-compose files, all deploy scripts, all playwright configs)
3. **Already-known issues list** — Pass 3 prompt includes all findings from Passes 1-2 to prevent re-flagging
4. **Auto-KEEP for previously audited source** — don't re-audit files already deep-profiled in Pass 2
5. **Directory-level assessments** for 50+ file directories (strategic sampling)

**Focus Areas**:
- Multiple docker-compose / Dockerfile / deploy scripts
- Config and .env file proliferation
- Root-level clutter
- Cross-directory duplication (same file type in multiple dirs)
- Stale artifacts from old architecture

**Agent Batch Size**: 20-50 files per agent (varies by file type density)
**Expected Depth**: Medium-deep with comparison focus

---

## 4. Classification Taxonomy (Unified)

Across all passes, recommendations use this priority-ordered taxonomy:

| Priority | Category | Reversibility | Actor |
|----------|----------|---------------|-------|
| 1 | **DELETE** | Git recoverable | Any developer |
| 2 | **CONSOLIDATE** | Git recoverable | Developer with domain knowledge |
| 3 | **MOVE** | Git recoverable | Any developer |
| 4 | **FLAG** | Requires code changes | Developer with context |
| 5 | **KEEP** | No action | N/A |
| 6 | **BROKEN REF** | Varies | Developer with context |

---

## 5. Verification Protocol (Universal)

### Mandatory Evidence for Every Recommendation

**For DELETE**:
- [ ] Grep confirms zero active references (cite the grep command and results)
- [ ] File is not dynamically loaded (check for dynamic imports, glob patterns, config-driven loading)
- [ ] No CI/CD pipeline references it
- [ ] A successor/replacement exists OR the functionality is no longer needed

**For KEEP**:
- [ ] At least one active reference found (cite file + line number)
- [ ] File is in a sensible location for its type
- [ ] File naming follows project conventions
- [ ] For configs: referenced by build/CI/runtime system
- [ ] For tests: in a test-runner-discovered path with proper patterns

**For CONSOLIDATE**:
- [ ] Both files identified with paths
- [ ] Overlap quantified (% identical, key differences listed)
- [ ] Recommendation for which to keep and what unique parts to merge

**For FLAG**:
- [ ] The issue is clearly described
- [ ] The required action is specific enough to execute
- [ ] Impact scope is estimated (which files/systems affected)

### Cross-Reference Checklist

Every file audit MUST check these reference sources:
- [ ] Source code imports/requires (`grep -r "filename" --include="*.{ts,tsx,py,js,jsx}"`)
- [ ] CI/CD workflows (`.github/workflows/*.yml`)
- [ ] Docker/Compose files (`docker-compose*.yml`, `Dockerfile*`)
- [ ] Package managers (`package.json`, `requirements.txt`, `pyproject.toml`)
- [ ] Build systems (`Makefile`, `*.sh`, `*.ps1`, `Justfile`)
- [ ] Documentation (`*.md`, `docs/`)

---

## 6. Agent Orchestration

### Batch Strategy

**Principles**:
1. **Domain-based batching**: Group files by functional domain (infrastructure, frontend components, backend services) not alphabetically
2. **Size limits**: 20-50 files per agent batch. Deeper passes use smaller batches.
3. **Priority ordering**: Infrastructure and cross-cutting configs first (HIGH), source code second (MEDIUM), assets last (LOW)
4. **Binary assets**: Grep-only audits (reference checking without reading content). Larger batches OK (50-100 files).
5. **Similar file grouping**: Agent batches should group similar files together so the agent can compare them directly

**Priority Tiers**:
| Tier | Targets | Rationale |
|------|---------|-----------|
| HIGH | Root loose files, infrastructure configs, deploy scripts, CI workflows | Cross-cutting sprawl is highest value |
| MEDIUM | Backend source, frontend source, test suites | Code correctness already enforced by linters/tests |
| LOW | Assets, documentation, wizard/UI components | Lowest risk, often already well-organized |

**Parallelization**:
- All agents within a priority tier can run in parallel
- Pass N+1 should not start until Pass N is reviewed and acted on
- Within a pass, agents are independent (no cross-agent data dependencies)

### Recommended Batch Plan Template

For a monorepo with ~1,500 files:
- **Pass 1**: 8-12 agents, 50 files each, complete in 1-2 hours
- **Pass 2**: 12-16 agents, 20-30 files each, complete in 3-5 hours
- **Pass 3**: 20-26 agents, 20-50 files each (varies), complete in 4-8 hours

---

## 7. Output Schema

### Per-Agent Output (Markdown)

```markdown
# {Scope Description} Audit (Pass {N})

{Pass-specific description}

**Status**: In Progress / Complete
**Files audited**: X / Y total
**Date**: YYYY-MM-DD

---

## Files to DELETE
### `filepath`
- **What it does**: ...
- **Nature**: ...
- **References**: ...
- **Evidence**: Why this should be deleted
- **Recommendation**: DELETE — {reason}

---

## Files to CONSOLIDATE (Pass 3 only)
### `filepath` → merge with `other/filepath`
- **Overlap**: {quantified}
- **Recommendation**: CONSOLIDATE — keep X, merge unique parts from Y

---

## Files to MOVE
### `filepath` → `new/path`
- **Why move**: ...

---

## Files to FLAG
### `filepath`
- **Issue**: What needs handling
- **Recommendation**: FLAG — {specific action needed}

---

## Broken References Found
- [ ] `filepath:line` → references `missing/path`

---

## Files to KEEP (verified legitimate)
- `filepath` — Nature: X. Evidence: {specific references}

---

## Summary
- **Total files audited**: X / Y
- **DELETE**: N | **CONSOLIDATE**: N | **MOVE**: N | **FLAG**: N | **KEEP**: N
- **Broken references found**: N

## Notes
Cross-cutting observations, patterns, recommendations.
```

### Consolidated Final Report

After all passes, produce a unified report:
```markdown
# Repository Audit — Final Report

## Executive Summary
- Total files audited: X / Y (coverage %)
- Actions identified: DELETE N, CONSOLIDATE N, MOVE N, FLAG N
- Broken references: N
- Estimated cleanup effort: {hours}

## Action Items by Priority
### Immediate (safe, no dependencies)
### Requires Decision (needs human judgment)
### Requires Code Changes (FLAG items)

## Cross-Cutting Findings
### {Pattern 1}: {Description}
### {Pattern 2}: {Description}

## Discovered Issues Registry
Numbered list of all systemic issues found, for tracking.
```

---

## 8. Safety Rails

### Read-Only Enforcement

**CRITICAL**: Audit agents MUST NOT modify any repository file. The ONLY file an agent may write is its own output report.

Enforcement mechanisms:
1. Prompt-level instruction: "DO NOT edit, delete, move, or modify ANY existing file. Violation = task failure."
2. Agent tool restrictions: If possible, restrict agent to Read + Grep + Glob + Write (single output file only)
3. Review gate: All recommendations are reviewed by a human before any action is taken

### Conservative Bias

- **Err on KEEP**: When uncertain, mark REVIEW/FLAG, never DELETE
- **Evidence required for DELETE**: Zero-reference grep result + no dynamic loading patterns + identified successor
- **No assumptions from filenames**: A file named `old-deploy.sh` might still be actively used. VERIFY.
- **Flag over delete for shared code**: If a file is imported by even one consumer, FLAG for refactoring rather than DELETE

### Incremental Save Protocol

Agents MUST follow this workflow to prevent context-window data loss:
1. Create output file with header template BEFORE auditing any files
2. Work in batches of 5-10 files
3. After each batch, IMMEDIATELY save/update the output file
4. Never accumulate more than 10 unwritten results
5. Each save includes ALL results so far (full rewrite)

### Known-Issues Deduplication

- Pass 2 prompt should reference Pass 1 findings to avoid re-flagging
- Pass 3 prompt MUST include a numbered list of all findings from Passes 1-2
- Agents encountering known issues note "Already tracked as issue #N" and move on

---

## 9. Quality Gates

### Minimum Evidence Thresholds

| Recommendation | Required Evidence |
|---------------|-------------------|
| DELETE | Zero references in grep + no CI/CD usage + no dynamic loading + successor identified OR functionality confirmed unnecessary |
| CONSOLIDATE | Both files read + overlap quantified (% or specific sections) + recommendation for canonical version |
| MOVE | Current location assessed as incorrect + target location justified |
| FLAG | Issue clearly described + action specific enough to execute without further research |
| KEEP | At least one active reference cited OR file is part of active build/runtime chain |

### Agent Output Validation

Before accepting an agent's output, verify:
- [ ] Every file in scope has a profile (completeness)
- [ ] DELETE recommendations cite grep evidence (not "probably unused")
- [ ] KEEP recommendations cite at least one reference (not "looks legitimate")
- [ ] Cross-references were actually checked (CI/CD, imports, compose files)
- [ ] Documentation files had claims verified (not just "referenced files exist")

### Spot-Check Protocol

For every 50 files audited, randomly select 5 and verify:
- Does the agent's grep claim match actual grep results?
- Did the agent actually read the file or just guess from the filename?
- Are KEEP recommendations genuine (file is truly referenced)?
- Are DELETE recommendations safe (file is truly unreferenced)?

---

## 10. Effectiveness Score: 75/100

### Scoring Breakdown

| Dimension | Weight | Score | Weighted | Justification |
|-----------|--------|-------|----------|---------------|
| Coverage Breadth | 20% | 5/10 | 1.00 | ~20% of repo deep-profiled in P2. P3 planned for full coverage but not yet executed. P1 was broader but shallower. |
| Evidence Quality | 25% | 9/10 | 2.25 | Outstanding. Per-file profiles consistently cite line numbers, grep results, cross-references. Hallucinated READMEs caught by actually reading content. |
| False Positive Rate | 15% | 9/10 | 1.35 | Near-zero. Every DELETE recommendation was backed by evidence. Conservative approach (FLAG over DELETE) prevents premature removals. |
| False Negative Rate | 15% | 5/10 | 0.75 | Significant repo portions unaudited (entire backend, root loose files, infrastructure Docker configs). P3 plan addresses this but wasn't executed. |
| Actionability | 15% | 9/10 | 1.35 | Excellent. Checklist format with specific file paths, line numbers, and clear next-actions. Developer can execute without further research. |
| Escalation Effectiveness | 10% | 8/10 | 0.80 | P2 genuinely found structural issues P1 missed (AI-hallucinated READMEs, dual routing architecture, port mismatches, deployment path conflicts). |

### What the Approach Does Well

1. **Evidence rigor**: The mandatory per-file profile forces agents to actually investigate rather than guess. This is the single most important design decision.

2. **Escalation model**: Surface → Structural → Cross-Cutting naturally catches different issue classes. P2 found organizational debt (misplaced files, stale docs) that P1's "is it junk?" framing couldn't detect.

3. **Safety**: Conservative bias + read-only + incremental saves + human review gate makes this safe to run on production repos.

4. **Actionability**: Checklist output with evidence means developers can execute cleanup without re-investigating each file.

5. **Per-file profiles for KEEP items**: Documenting WHY kept files are legitimate creates institutional knowledge and prevents re-auditing.

### Where It Falls Short

1. **Coverage gap**: P1 and P2 audited selected directories, not the full repo. Cross-cutting issues (the primary value of cleanup) require full coverage. The P3 batch plan addresses this but introduces 26 separate agents — a significant coordination overhead.

2. **No automated pre-scan**: All detection is manual agent work. Running automated tools first (unused import detectors, dead code analyzers, reference graph builders) would give agents a stronger starting point and reduce false negatives.

3. **Agent isolation**: P2 agents operated independently per directory. Agent A's finding about a dual routing system was invisible to Agent B auditing components that depend on the router. A shared findings channel would improve cross-agent awareness.

4. **Output fragmentation**: 15 separate P2 files make holistic analysis difficult. A consolidation step that merges all outputs into a unified actionable report is missing.

5. **No validation loop**: There's no mechanism to spot-check agent work or catch lazy KEEP recommendations. A meta-agent that validates 10% of KEEP items would improve confidence.

6. **Scope creep in P3**: The 26-batch P3 plan tries to audit 1,458 files in deep-profile format. At 20-50 files per agent with 5-10 minute per-file investigation, this is 25-50+ hours of agent time. Strategic sampling or tiered depth would be more practical.

---

## 11. Improvement Recommendations

### Priority 1: Full-Coverage P1

**Problem**: P1 only covered selected directories, leaving gaps for P2/P3.
**Fix**: P1 should scan 100% of repo files with light-touch assessment (filename + grep, no deep reading). This creates a complete inventory that P2 can strategically deep-dive into.

### Priority 2: Automated Pre-Scan

**Problem**: All detection is manual, missing issues that tools catch trivially.
**Fix**: Before agent passes, run:
- `ts-prune` / `knip` for unused TypeScript exports
- `vulture` / `autoflake` for dead Python code
- Custom script: grep all filenames, flag zero-reference files
- `madge` for circular dependency detection
- Dockerfile linter (`hadolint`), compose linter (`docker-compose config`)

Feed results into P1 agents as "pre-scan hints" to investigate.

### Priority 3: Shared Findings Channel

**Problem**: Agent A finds "dual routing system" but Agent B doesn't know this when auditing router-dependent components.
**Fix**: After each agent completes, extract key findings into a shared "Discovered Issues" document. Subsequent agents receive this document as context. P3 already does this (issues #1-34), but the mechanism should be formalized and applied within passes, not just between them.

### Priority 4: Output Consolidation Step

**Problem**: 15+ separate output files are hard to reason about holistically.
**Fix**: After each pass, run a consolidation agent that:
1. Merges all per-agent outputs into a single report
2. Deduplicates findings
3. Identifies cross-agent patterns
4. Produces an executive summary with action priority

### Priority 5: Validation Meta-Agent

**Problem**: No mechanism to catch lazy KEEP or wrong DELETE.
**Fix**: After P2, randomly sample 10% of KEEP recommendations. A validation agent:
1. Re-greps for references
2. Verifies the original agent actually read the file
3. Checks if the classification seems correct
4. Reports discrepancies

### Priority 6: Tiered P3 Depth

**Problem**: P3 tries to deep-profile all 1,458 files, which is impractical.
**Fix**: P3 should use tiered depth:
- **Deep** (per-file profile): Root configs, infrastructure, CI/CD, deploy scripts (~200 files)
- **Medium** (directory assessment + sampling): Source code directories (~800 files)
- **Light** (reference-grep only): Assets, documentation, generated files (~400 files)

---

## Integration Notes

### Auto-Persona Activation
- **analyzer**: Primary persona for all passes
- **architect**: Activated for infrastructure and cross-cutting analysis
- **devops**: Activated for Docker/CI/deploy script batches
- **qa**: Activated for test file batches
- **refactorer**: Activated for code duplication findings

### MCP Server Usage
- **Sequential**: Complex reasoning during cross-cutting analysis
- **Serena**: Symbol-level code understanding for import chain tracing
- **Context7**: Framework-specific pattern validation

### Suggested Usage Flow
```
/sc:repo-audit --pass 1                    # Surface scan, full repo
# Review P1 output, execute safe DELETEs
/sc:repo-audit --pass 2                    # Structural audit on P1 KEEPs
# Review P2 output, execute recommendations
/sc:repo-audit --pass 3 --focus infra      # Cross-cutting, infrastructure first
/sc:repo-audit --pass 3 --focus source     # Cross-cutting, source code
# Consolidate and produce final report
```

---

## Appendix: Reusable Cleanup Principles

These principles generalize across any monorepo cleanup:

1. **Evidence over assumption**: Every recommendation must cite specific grep results, line numbers, or config references. "Probably unused" is not evidence.

2. **Conservative default**: When in doubt, FLAG rather than DELETE. A false negative (missed dead code) is cheaper than a false positive (deleted active code).

3. **Read before judging**: A file named `old-deploy.sh` might be the only deploy script that works. Actually read files and trace their references.

4. **Escalating depth**: Start broad and shallow, then narrow and deep. Surface scans cover ground; structural audits catch subtlety; cross-cutting sweeps find systemic patterns.

5. **Profile everything**: Even KEEP items get profiles. This prevents re-auditing and creates institutional knowledge about why files exist.

6. **Incremental saves**: Context windows are finite. Save every 5-10 files. Never risk losing work.

7. **Batch by domain, not alphabet**: Files in the same domain (all streaming components, all deploy scripts) should be audited together so the agent can compare them.

8. **Dedup across passes**: Each pass receives a list of known issues from previous passes. Re-flagging wastes reviewer time.

9. **Verify documentation claims**: The highest-value finding class is "this README/doc describes things that don't exist." Actually verify 3-5 claims per documentation file.

10. **Check the test infrastructure**: Tests that target dead code, use wrong paths, or are permanently skipped are a common source of hidden debt. Trace test configs to verify tests are actually discovered and runnable.
