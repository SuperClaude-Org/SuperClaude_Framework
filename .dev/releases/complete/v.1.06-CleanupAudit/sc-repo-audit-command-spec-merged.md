# `/sc:cleanup-audit` — Multi-Pass Repository Cleanup Audit Command

**Merged Specification**
**Version**: 1.1 (merged)
**Generated**: 2026-02-19
**Derived from**: sc-repo-audit-command-spec-opus.md (Source A) + sc-repo-audit-command-spec-gpt.md (Source B)
**Traceability**: See Appendix — all sections mapped to CMP IDs from `sc-repo-audit-command-spec-comparison.md`
**Adjudication authority**: `sc-repo-audit-command-spec-comparison.md` Phase 3

---

## 1. Command Name & Purpose

**[CMP-001, CMP-002]**

```
/sc:cleanup-audit [target] [--pass 1|2|3|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]
```

**Purpose**: Read-only, evidence-backed, multi-pass repository audit covering dead code, organizational debt, configuration sprawl, cross-cutting duplication, and broken references. Produces an executable cleanup plan (DELETE / MOVE / CONSOLIDATE / FLAG / KEEP) with per-recommendation verifiable citations.

**Category**: Quality / Maintenance
**Wave-Enabled**: Yes (complexity ≥ 0.7 auto-triggers multi-agent orchestration)
**Performance Profile**: Complex

---

## 2. Objectives

**[CMP-002, CMP-016]**

1. Identify **safe deletions** — true orphans, obsolete artifacts, redundant configs, dead tests.
2. Identify **misplacements** — files in wrong directory structure.
3. Identify **stale or lying documentation** — docs referencing non-existent files or incorrect behavior.
4. Identify **broken references** across code, docs, config, CI, and scripts.
5. Identify **cross-cutting duplication and sprawl** — near-duplicate compose files, deploy scripts, test configs.
6. Produce **evidence-backed recommendations** — every DELETE/MOVE/FLAG has verifiable proof, not assumptions.
7. Maintain **safety** — read-only operation, conservative bias, incremental saves, human review gate.

---

## 3. Multi-Pass Architecture

**[CMP-003, CMP-004, CMP-005, CMP-007, CMP-008]**

The core design is a **3-pass escalation model** where each pass increases analytical depth and cross-cutting scope.

### Pass 1: Surface Scan (Junk Detection)

**Goal**: Quickly identify obvious waste — test artifacts, runtime files committed by accident, empty placeholders, files nothing references.

**Question each file must answer**: "Is this file junk?"

**Classification taxonomy (3-tier)**:

| Category | Meaning | Action |
|---|---|---|
| DELETE | No references, no value, clearly obsolete | Safe to remove |
| REVIEW | Uncertain — may be needed, needs human judgment | Escalate to human |
| KEEP | Actively referenced, part of build/runtime/CI | Leave in place |

**Verification protocol**:
1. Read first 20-30 lines to understand purpose.
2. Grep for filename across repo (exclude `.git/`, `node_modules/`, build artifacts).
3. Check if imported/sourced by other files.
4. Categorize with brief justification.

**Output**:
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

**Batch size**: 25-50 files per agent
**Depth**: Light (5-10 min per batch)
**Expected coverage**: 100% of repo files at surface level

---

### Pass 2: Structural Audit (Organizational Integrity)

**Goal**: Validate placement, staleness, broken references, and structural issues — things that "look fine" but aren't. Requires per-file proof.

**Question each file must answer**: "Is this file in the right place, correctly documented, and structurally sound?"

**Finding types (diagnostic)**:

| Finding Type | Meaning |
|---|---|
| MISPLACED | Valid content in wrong location |
| STALE | Outdated or no longer accurate |
| STRUCTURAL ISSUE | Internal problems requiring code changes |
| BROKEN REFS | References to non-existent paths or files |
| VERIFIED OK | Confirmed correct with evidence |

**Action recommendations (prescriptive)**:

| Action | Meaning |
|---|---|
| KEEP | Verified; has evidence of active use |
| DELETE | Confirmed dead with evidence |
| MOVE | Valid but wrong location |
| FLAG | Needs code changes or human decision |

**Mandatory per-file profile (all fields required)**:

| Field | Requirement |
|---|---|
| What it does | 1-2 sentence plain-English explanation |
| Nature | Classify: script / test / doc / config / source code / data / asset / migration / one-time artifact |
| References | Who/what references this file? Grep results with files + line numbers. "None found" is valid but must be stated explicitly. |
| CI/CD usage | Called by any automation? Check workflows, compose files, Makefile, package.json, Dockerfiles. |
| Superseded by / duplicates | Is there a newer/better version? Check for `_v2`, `_enhanced`, `_new` variants. |
| Risk notes | Runtime/CI/test/doc impact if removed or moved. |
| Recommendation | KEEP / MOVE / DELETE / FLAG with finding type where applicable. |
| Verification notes | Explicit list of what was checked (prevents lazy KEEP). |

**Extra rules by file type**:
- **Tests**: Check test runner discovery (is it in a test-discovered path?), check patterns (pytest vs manual), verify it would actually pass.
- **Scripts**: Check if functionality is handled by a canonical script; check schema/field names are current.
- **Documentation**: Verify 3-5 technical claims against actual implementation — not just whether referenced files exist.
- **Config**: Compare with similar configs; check if values match current architecture.

**Failure criterion**: Reports missing mandatory per-file profiles are **failed** and must be regenerated.

**Scope**: Only files marked KEEP or REVIEW from Pass 1.
**Batch size**: 20-30 files per agent.
**Depth**: Deep (20-40 min per batch).

---

### Pass 3: Cross-Cutting Sweep (Sprawl, Duplication, Consolidation)

**Goal**: Find duplication, sprawl, and broken references spanning directory boundaries — problems per-directory audits inherently miss. Requires diff/overlap quantification.

**Question each file must answer**: "Does this file duplicate or conflict with another file elsewhere in the repo?"

**Classification taxonomy (adds CONSOLIDATE)**:

| Category | Meaning | Action |
|---|---|---|
| DELETE | Confirmed dead | Remove |
| CONSOLIDATE | Merge with identified similar file | Keep canonical, merge unique parts |
| MOVE | Valid but wrong location | Relocate |
| FLAG | Needs code changes | Developer action |
| KEEP | Verified unique purpose with evidence | Leave in place |
| BROKEN REF | References non-existent paths | Fix reference |

**Per-file profile fields (Pass 3)**:

| Field | Requirement |
|---|---|
| What it does | 1-2 sentence explanation |
| Nature | File type classification |
| References | Grep results with files + line numbers |
| Similar files | Other files serving same/overlapping purpose; quantify % overlap or key differences |
| Superseded? | Newer/better version exists? |
| Currently used? | Referenced by running app, CI/CD, build? Evidence required. |
| Recommendation | DELETE / CONSOLIDATE (with what) / MOVE / FLAG / KEEP |

**Critical differentiators from Pass 2**:
1. **Compare, don't just catalog** — when similar files found, DIFF them and quantify overlap.
2. **Group audit** — audit similar files together (all docker-compose files, all deploy scripts, all playwright configs).
3. **Mandatory duplication matrix** — produce a matrix for compose/deploy/tests/configs with overlap percentages.
4. **Already-known issues list** — Pass 3 prompt includes all findings from Passes 1-2; agents note "Already tracked as issue #N" and move on.
5. **Auto-KEEP for previously audited source** — don't re-audit files already deep-profiled in Pass 2.
6. **Directory-level assessments** for 50+ file directories (strategic sampling).

**Focus areas**:
- Multiple docker-compose / Dockerfile / deploy scripts
- Config and .env file proliferation
- Root-level clutter
- Cross-directory duplication (same file type in multiple directories)
- Stale artifacts from old architecture

**Batch size**: 20-50 files per agent (varies by file type density)
**Depth**: Medium-deep with comparison focus

---

## 4. Classification Taxonomy (Unified)

**[CMP-005, CMP-007]**

Across all passes, recommendations use this priority-ordered taxonomy:

| Priority | Category | Reversibility | Actor |
|---|---|---|---|
| 1 | DELETE | Git recoverable | Any developer |
| 2 | CONSOLIDATE | Git recoverable | Developer with domain knowledge |
| 3 | MOVE | Git recoverable | Any developer |
| 4 | FLAG | Requires code changes | Developer with context |
| 5 | KEEP | No action | N/A |
| 6 | BROKEN REF | Varies | Developer with context |

---

## 5. Verification Protocol (Universal)

**[CMP-018, CMP-019, CMP-020]**

### Mandatory Evidence for Every Recommendation

**For DELETE**:
- [ ] Grep confirms zero active references (cite the grep command and results with pattern + count).
- [ ] File is not dynamically loaded (check for dynamic imports, glob patterns, env-var-based loaders, config-driven loading, plugin registries).
- [ ] No CI/CD pipeline references it.
- [ ] A successor/replacement exists, OR the functionality is no longer needed, OR the file is a transient artifact (cache/log/tmp/demo) — transient artifact type eliminates the successor requirement.

**For KEEP**:
- [ ] At least one active reference found (cite file + line number).
- [ ] File is in a sensible location for its type.
- [ ] File naming follows project conventions.
- [ ] For configs: referenced by build/CI/runtime system.
- [ ] For tests: in a test-runner-discovered path with proper patterns.

**For CONSOLIDATE**:
- [ ] Both files identified with paths.
- [ ] Overlap quantified (% identical, key differences listed).
- [ ] Recommendation for which to keep and what unique parts to merge.

**For FLAG**:
- [ ] The issue is clearly described.
- [ ] The required action is specific enough to execute.
- [ ] Impact scope is estimated (which files/systems affected).
- [ ] A minimal verification checklist states: "what evidence would settle this?"

**For MOVE**:
- [ ] Clear target location rationale.
- [ ] List of references to update.

### Cross-Reference Checklist

Every file audit must check these reference sources:
- [ ] Source code imports/requires (`grep -r "filename" --include="*.{ts,tsx,py,js,jsx}"`)
- [ ] CI/CD workflows (`.github/workflows/*.yml`)
- [ ] Docker/Compose files (`docker-compose*.yml`, `Dockerfile*`)
- [ ] Package managers (`package.json`, `requirements.txt`, `pyproject.toml`)
- [ ] Build systems (`Makefile`, `*.sh`, `*.ps1`, `Justfile`)
- [ ] Documentation (`*.md`, `docs/`)
- [ ] Kubernetes/Helm/Terraform manifests (if present)

### Documentation Claim Verification

For documentation files, verify 3-5 technical claims against actual implementation — not just whether referenced files exist. The highest-value finding class is "this README/doc describes things that don't exist."

---

## 6. Agent Orchestration

**[CMP-004, CMP-013]**

### Batch Strategy

**Principles**:
1. **Domain-based batching**: Group files by functional domain (infrastructure, frontend, backend), not alphabetically.
2. **Size limits**: 20-50 files per agent batch. Deeper passes use smaller batches.
3. **Priority ordering** (4 levels):
   - (1) Cross-cutting infra / CI / deploy / compose sprawl [highest — cross-cutting issues yield highest cleanup value]
   - (2) Runtime-critical config [high — config errors break production]
   - (3) Tests and tooling [medium — prevent false-green CI]
   - (4) Source code [medium]
   - (5) Docs and ancillary assets [lowest — lowest risk]
4. **Binary assets**: Grep-only audits (reference checking without reading content). Larger batches OK (50-100 files).
5. **Similar file grouping**: Batch similar files together so agents can compare them directly.

**Exclusions**: `.git/`, `node_modules/`, build outputs, caches, vendor directories — excluded from all passes.

**Parallelization**:
- All agents within a priority tier can run in parallel.
- Pass N+1 should not start until Pass N is reviewed and acted on.
- Within a pass, agents are independent (no cross-agent data dependencies).

### Recommended Batch Plan Template

For a monorepo with ~1,500 files:
- **Pass 1**: 8-12 agents, 50 files each, complete in 1-2 hours
- **Pass 2**: 12-16 agents, 20-30 files each, complete in 3-5 hours
- **Pass 3**: 20-26 agents, 20-50 files each (varies), complete in 4-8 hours

For large repos, use **tiered P3 depth**:
- **Deep** (per-file profile): Root configs, infrastructure, CI/CD, deploy scripts (~200 files)
- **Medium** (directory assessment + sampling): Source code directories (~800 files)
- **Light** (reference-grep only): Assets, documentation, generated files (~400 files)

---

## 7. Output Schema

**[CMP-006, CMP-021]**

### Global Required Sections (All Passes)

Every report must include:
- Scope definition (directories/files covered; exclusions stated explicitly)
- Summary counts (DELETE / MOVE / FLAG / CONSOLIDATE / KEEP / BROKEN REFS)
- **Remaining / Not Audited** section (mandatory if scope was not completed — transparency beats pretending completeness)
- **Already-known issues not re-flagged** (Pass 3 only)

### Per-Agent Output (Markdown)

```markdown
# {Scope Description} Audit (Pass {N})

**Status**: In Progress / Complete
**Files audited**: X / Y total
**Date**: YYYY-MM-DD

---

## Files to DELETE
### `filepath`
- **What it does**: ...
- **Nature**: ...
- **References**: ...
- **Evidence**: Why this should be deleted (grep pattern + count + zero-result)
- **Recommendation**: DELETE — {reason}

---

## Files to CONSOLIDATE (Pass 3 only)
### `filepath` → merge with `other/filepath`
- **Overlap**: {quantified — % or key sections}
- **Recommendation**: CONSOLIDATE — keep X, merge unique parts from Y

---

## Files to MOVE
### `filepath` → `new/path`
- **Why move**: ...
- **References to update**: ...

---

## Files to FLAG
### `filepath`
- **Finding type**: MISPLACED / STALE / STRUCTURAL ISSUE / BROKEN REFS
- **Issue**: What needs handling
- **Required action**: Specific enough to execute
- **Verification checklist**: What evidence would settle this?

---

## Broken References Found
- [ ] `filepath:line` → references `missing/path`

---

## Files to KEEP (verified legitimate)
- `filepath` — Nature: X. References: {specific citations}. Verification: {what was checked}

---

## Remaining / Not Audited
- List files not reached if scope was incomplete.

---

## Summary
- **Total files audited**: X / Y
- **DELETE**: N | **CONSOLIDATE**: N | **MOVE**: N | **FLAG**: N | **KEEP**: N
- **Broken references found**: N

## Notes
Cross-cutting observations, patterns, recommendations.
```

### Consolidated Final Report

After all passes:
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

## Discovered Issues Registry
Numbered list of all systemic issues found.
```

---

## 8. Safety Rails

**[CMP-020, CMP-021]**

### Read-Only Enforcement

**Audit agents must not modify any repository file.** The only file an agent may write is its own output report.

Enforcement mechanisms:
1. Prompt-level instruction: "DO NOT edit, delete, move, or modify ANY existing file. Violation = task failure."
2. Agent tool restrictions: Restrict to Read + Grep + Glob + Write (single output file only).
3. Review gate: All recommendations reviewed by a human before any action is taken.

### Conservative Bias

- **Err on KEEP**: When uncertain, mark REVIEW/FLAG, never DELETE.
- **Evidence required for DELETE**: Zero-reference grep result + no dynamic loading patterns + identified successor (or confirmed transient artifact type).
- **No assumptions from filenames**: A file named `old-deploy.sh` might still be the only deploy script that works. Read it and trace its references.
- **Flag over delete for shared code**: If a file is imported by even one consumer, FLAG for refactoring rather than DELETE.
- **No speculative deletions**.

### Incremental Save Protocol

Agents must follow this workflow to prevent context-window data loss:
1. Create output file with header template before auditing any files.
2. Work in batches of 5-10 files.
3. After each batch, immediately save/update the output file.
4. Never accumulate more than 10 unwritten results.
5. Each save includes all results so far (full rewrite or append).

### Known-Issues Deduplication

- Pass 2 prompt should reference Pass 1 findings to avoid re-flagging.
- Pass 3 prompt must include a numbered list of all findings from Passes 1-2.
- Agents encountering known issues note "Already tracked as issue #N" and move on.

---

## 9. Quality Gates

**[CMP-022, CMP-006]**

### Minimum Evidence Thresholds

| Recommendation | Required Evidence |
|---|---|
| DELETE | Zero references (grep with pattern + count) + no CI/CD usage + no dynamic loading + successor identified OR transient artifact confirmed |
| CONSOLIDATE | Both files read + overlap quantified (% or specific sections) + canonical version chosen + migration notes |
| MOVE | Current location assessed as incorrect + target location justified + list of refs to update |
| FLAG | Issue clearly described + action specific enough to execute + verification checklist ("what evidence would settle this?") |
| KEEP | At least one active reference cited OR file is part of active build/runtime chain + explicit verification notes |

### Agent Output Validation (Spot-Check Protocol)

For every 50 files audited, randomly select 5 and verify:
- Does the agent's grep claim match actual grep results?
- Did the agent actually read the file or guess from filename?
- Are KEEP recommendations genuine (file is truly referenced)?
- Are DELETE recommendations safe (file is truly unreferenced)?

**Failed reports**: Reports missing mandatory per-file profiles in Pass 2 are failed and must be regenerated.

### Evidence Snippets for "No References"

Every DELETE recommendation must embed a short grep result summary — the pattern used, the command, and the zero-result confirmation. "No imports found" without a reproducible grep is insufficient.

---

## 10. Effectiveness Score

**[CMP-009]**

Two scores reflect different measurement baselines:

| Score | Value | Basis |
|---|---|---|
| Methodology quality | 75/100 | Design quality assessment (Source A) |
| Empirical execution quality | 63/100 | Actual P2 output artifacts; 327 files deep-profiled out of 5,942 tracked (Source B) |

### Scoring Dimensions (identical in both sources)

| Dimension | Weight | A Score | B Score | Notes |
|---|---|---|---|---|
| Coverage Breadth | 20% | 5/10 (50%) | 6/100 (6%) | B reflects actual breadth; ~20% vs ~5.5% deep-profiled |
| Evidence Quality | 25% | 9/10 (90%) | 85/100 (85%) | Strong in both; some missing grep excerpts in lower-scoring reports |
| False Positive Resistance | 15% | 9/10 (90%) | 80/100 (80%) | Both high; residual risk in dynamic-use assumptions |
| False Negative Resistance | 15% | 5/10 (50%) | 60/100 (60%) | Coverage gap and un-executed Pass 3 are limiting factors |
| Actionability | 15% | 9/10 (90%) | 85/100 (85%) | Strong concrete steps; some FLAG items lack verification checklists |
| Escalation Effectiveness | 10% | 8/10 (80%) | 70/100 (70%) | Pass 2 clearly improves on Pass 1; Pass 3 design sound but execution evidence limited |

**Interpretation**: The methodology is sound and evidence-quality is high. The primary weakness in both assessments is coverage breadth — P2 audited a small fraction of total files. Pass 3 consolidation is well-designed but not fully demonstrated by outputs evaluated.

---

## 11. Improvement Recommendations

**[CMP-010, CMP-011, CMP-012, CMP-023, CMP-024, CMP-025, CMP-033 (A's Priority 3 — Shared Findings Channel), CMP-017 (principles)]**

Ordered by expected impact:

### 1. Full-Coverage Pass 1

**Problem**: P1 may cover selected directories, leaving gaps for P2/P3.
**Fix**: P1 must scan 100% of repo files with light-touch assessment (filename + grep, no deep reading). Auto-generate scope file list via `git ls-files` and compute coverage percentage. This creates a complete inventory that P2 can strategically deep-dive into.

### 2. Coverage Tracking

**Problem**: No automated measurement of what fraction of the repo has been audited.
**Fix**: Require every report to state: files_audited / git_ls_files_total = coverage%. Track cumulatively across all reports.

### 3. Automated Pre-Scan

**Problem**: All detection is manual agent work, missing issues that static tools catch trivially.
**Fix**: Before agent passes, run:
- `ts-prune` / `knip` — unused TypeScript exports
- `vulture` / `autoflake` — dead Python code
- `madge` — circular dependency detection
- `hadolint` — Dockerfile linting
- `docker compose config` — compose file validation
- Custom script: grep all filenames, flag zero-reference files

Feed results into P1 agents as "pre-scan hints" to investigate.

### 4. Dynamic-Use Checklist

**Problem**: "No imports found" assertions can be wrong when dynamic loading is used.
**Fix**: Codify common dynamic reference patterns:
- Environment variable-based module loading
- String-based import loaders
- Plugin registries
- Glob-based file discovery
- Config-driven loading patterns

Agents must check these patterns before downgrading to DELETE.

### 5. Shared Findings Channel

**Problem**: Agent A finds "dual routing system" but Agent B auditing dependent components does not know this.
**Fix**: After each agent completes, extract key findings into a shared "Discovered Issues" document. Subsequent agents receive this document as context. Formalize this mechanism within passes, not just between them.

### 6. Output Consolidation Step

**Problem**: 15+ separate output files make holistic analysis difficult.
**Fix**: After each pass, run a consolidation agent that:
1. Merges all per-agent outputs into a single report.
2. Deduplicates findings.
3. Identifies cross-agent patterns.
4. Produces executive summary with action priority.

### 7. Pass 3 Mandatory Duplication Matrix

**Problem**: Cross-cutting duplication is the primary value of Pass 3 but may be under-enforced.
**Fix**: Require a structured duplication matrix for compose/deploy/tests/configs with overlap percentages before Pass 3 is considered complete.

### 8. Workflow-to-Config Mapping

**Problem**: CI/test findings are hard to reproduce without knowing the full dependency chain.
**Fix**: For test/CI findings, explicitly map: workflow file → command invoked → config file used. This makes test integrity claims reproducible.

### 9. Validation Meta-Agent

**Problem**: No mechanism to catch lazy KEEP or incorrect DELETE recommendations.
**Fix**: After P2, randomly sample 10% of KEEP recommendations. A validation agent:
1. Re-greps for references.
2. Verifies the original agent actually read the file.
3. Checks if the classification seems correct.
4. Reports discrepancies.

### 10. Portable Output Paths

**Problem**: Absolute machine paths in output templates are not portable across environments.
**Fix**: Eliminate absolute paths in templates. Use `$REPO_ROOT` + relative output locations for all file references.

---

## 12. Integration Notes (SuperClaude)

**[CMP-016]**

### Auto-Persona Activation

- **analyzer**: Primary persona for all passes
- **architect**: Activated for infrastructure and cross-cutting analysis
- **devops**: Activated for Docker/CI/deploy script batches
- **qa**: Activated for test file batches
- **refactorer**: Activated for code duplication findings

### MCP Server Usage

- **Auggie**: Codebase retrieval and semantic code search
- **Sequential**: Complex reasoning during cross-cutting analysis
- **Serena**: Symbol-level code understanding for import chain tracing
- **Context7**: Framework-specific pattern validation

### Suggested Usage Flow

```
/sc:cleanup-audit --pass 1                    # Surface scan, full repo
# Review P1 output, execute safe DELETEs
/sc:cleanup-audit --pass 2                    # Structural audit on P1 KEEPs
# Review P2 output, execute recommendations
/sc:cleanup-audit --pass 3 --focus infra      # Cross-cutting, infrastructure first
/sc:cleanup-audit --pass 3 --focus source     # Cross-cutting, source code
# Consolidate and produce final report
```

---

## 13. Reusable Cleanup Principles

**[CMP-017]**

Merged from both sources (A Appendix + B Phase 1 Principles). Ordered by dependency:

1. **Read-only by default**: Audit output only; no repo edits during the audit.
2. **Evidence over assumption**: Every recommendation must cite specific grep results, line numbers, or config references. "Probably unused" is not evidence.
3. **Conservative default**: When in doubt, FLAG rather than DELETE. A false negative (missed dead code) is cheaper than a false positive (deleted active code).
4. **Read before judging**: A file named `old-deploy.sh` might be the only deploy script that works. Read it and trace its references.
5. **Proof standards rise each pass**: Pass 1 quick triage → Pass 2 per-file proof → Pass 3 cross-cutting diff/overlap proof.
6. **Escalating depth**: Start broad and shallow, then narrow and deep. Surface scans cover ground; structural audits catch subtlety; cross-cutting sweeps find systemic patterns.
7. **Mandatory evidence**: Every KEEP/DELETE needs verifiable anchors (references + file:line).
8. **Profile everything**: Even KEEP items get profiles. This prevents re-auditing and creates institutional knowledge about why files exist.
9. **Incremental saves**: Context windows are finite. Save every 5-10 files. Never risk losing work.
10. **Scope discipline**: Cap files per agent; state explicit exclusions; prevent "audit the world."
11. **Orchestrated batching**: Priority-first batches, parallel where independent, special fast-path for binary/asset directories.
12. **Noise control (dedup across passes)**: Each pass receives a list of known issues from previous passes. Re-flagging wastes reviewer time.
13. **Completion criteria and Remaining list**: Transparency beats pretending completeness.
14. **Output schema as a quality gate**: Reports must be machine-checkable (consistent, mandatory fields).
15. **Verify documentation claims**: The highest-value finding class is "this README/doc describes things that don't exist." Verify 3-5 claims per documentation file.
16. **Check the test infrastructure**: Tests targeting dead code, using wrong paths, or permanently skipped are a common source of hidden debt. Verify test configs to confirm tests are actually discovered and runnable.

---

## Appendix — Traceability: Merged Sections → CMP IDs

| Merged Section | CMP IDs Incorporated |
|---|---|
| 1. Command Name & Purpose | CMP-001, CMP-002 |
| 2. Objectives | CMP-002, CMP-016 |
| 3. Multi-Pass Architecture (general) | CMP-003, CMP-004, CMP-005, CMP-007, CMP-008 |
| 3. Pass 1 details | CMP-003, CMP-004 |
| 3. Pass 2 details | CMP-005, CMP-006 |
| 3. Pass 3 details | CMP-007, CMP-008 |
| 4. Classification Taxonomy | CMP-005, CMP-007 |
| 5. Verification Protocol | CMP-018, CMP-019, CMP-020 |
| 6. Agent Orchestration | CMP-004, CMP-013 |
| 7. Output Schema | CMP-006, CMP-021 |
| 8. Safety Rails | CMP-020, CMP-021 |
| 9. Quality Gates | CMP-022, CMP-006 |
| 10. Effectiveness Score | CMP-009 |
| 11. Improvement Recommendations | CMP-010, CMP-011, CMP-012, CMP-023, CMP-024, CMP-025 |
| 12. Integration Notes | CMP-016 |
| 13. Reusable Cleanup Principles | CMP-017 |
| Port/Network claims | CMP-026 (none included — no spec-level port claims in either source) |
| API/Type claims | CMP-027 (none included — no internal interface definitions in either source) |

### All CMP IDs → Merged Section Reference

| CMP ID | Category | Merged Section | Disposition |
|---|---|---|---|
| CMP-001 | contradiction | Section 1 | Resolved: /sc:cleanup-audit wins |
| CMP-002 | overlap | Section 1, 2 | Synthesized |
| CMP-003 | overlap | Section 3 Pass 1 | Included (identical) |
| CMP-004 | overlap | Section 3, 6 | Included (B range 20-50 adopted) |
| CMP-005 | contradiction | Section 3 Pass 2, 4 | Resolved: B's two-layer approach |
| CMP-006 | overlap | Section 3 Pass 2, 7, 9 | Merged (all unique fields) |
| CMP-007 | overlap | Section 3 Pass 3, 4 | Included |
| CMP-008 | overlap | Section 3 Pass 3, 8 | Included |
| CMP-009 | contradiction | Section 10 | Resolved: both scores presented with context |
| CMP-010 | overlap | Section 11 (items 1, 2, 3) | Included |
| CMP-011 | B-only | Section 11 (item 4) | Included |
| CMP-012 | overlap | Section 11 (items 6, 10) | Included |
| CMP-013 | overlap | Section 6 | Resolved: B's 4-level ordering |
| CMP-014 | B-only | (excluded) | Meta-analysis; not normative spec content |
| CMP-015 | B-only | (excluded) | Instance-specific data; not normative spec content |
| CMP-016 | A-only | Section 12 | Included |
| CMP-017 | A-only (with B equivalent) | Section 13 | Merged (both principle sets) |
| CMP-018 | overlap | Section 5 | Included (B's artifact shortcut added) |
| CMP-019 | A-only | Section 5 | Included |
| CMP-020 | overlap | Section 8 | Included |
| CMP-021 | B-only | Section 7, 8 | Included |
| CMP-022 | B-only | Section 9 | Included |
| CMP-023 | B-only | Section 11 (item 7) | Included |
| CMP-024 | B-only | Section 11 (item 8) | Included |
| CMP-025 | A-only | Section 9, 11 (item 9) | Included |
| CMP-026 | N/A | (none) | No port claims in either source |
| CMP-027 | N/A | (none) | No interface definitions in either source |
