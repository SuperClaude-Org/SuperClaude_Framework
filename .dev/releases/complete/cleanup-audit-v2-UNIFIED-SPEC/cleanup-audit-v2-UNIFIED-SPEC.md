# sc:cleanup-audit v2 -- Unified Specification

**Version**: 2.0-UNIFIED
**Date**: 2026-02-20
**Status**: FINAL DRAFT -- Ready for Implementation Planning
**Lineage**: Synthesized from two independent analysis runs (Set A: single-agent gap analysis + PRD; Set B: multi-agent findings/proposals/reflection/PRD) via a 4-wave adversarial merge process (coverage matrix, strength ranking, flaw analysis, conflict resolution, advocate debate, devil's advocate attack, synthesis judge verdicts).

---

## Table of Contents

1. [Executive Summary with Lineage](#1-executive-summary-with-lineage)
2. [Problem Statement](#2-problem-statement)
3. [Goals, Non-Goals, Target Users](#3-goals-non-goals-target-users)
4. [Architecture](#4-architecture)
5. [Unified Classification System](#5-unified-classification-system)
6. [Phase Specifications](#6-phase-specifications)
7. [Budget and Resource Controls](#7-budget-and-resource-controls)
8. [CLI Interface](#8-cli-interface)
9. [Output Specification](#9-output-specification)
10. [Quality Gates](#10-quality-gates)
11. [Known-Issues System](#11-known-issues-system)
12. [Cold-Start and Configuration](#12-cold-start-and-configuration)
13. [Risk Mitigation](#13-risk-mitigation)
14. [Implementation Roadmap](#14-implementation-roadmap)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [Rejected Alternatives Appendix](#16-rejected-alternatives-appendix)
17. [Known Risks and Limitations](#17-known-risks-and-limitations)
18. [Expert Panel Consensus](#18-expert-panel-consensus)

---

## 1. Executive Summary with Lineage

### Derivation

This specification is the product of two independent analysis runs examining the same problem -- the quality gap between the legacy manual cleanup-audit prompts and the current automated `sc:cleanup-audit` v1. The two analysis sets were merged through a structured adversarial process:

- **Set A** (single-agent, 2 documents): Gap analysis comparing old prompt outputs to new audit output, plus a vNext PRD with Pass 4 docs audit, known-issues registry, and output schema hardening. Average composite score: 7.70/10.
- **Set B** (multi-agent, 4 documents): 15 findings from 4-agent parallel analysis, 12 debated proposals, 5-dimension reflection/validation, and a v2 PRD with 5-phase architecture. Average composite score: 8.55/10.
- **Merge process**: Wave 1 (coverage matrix, strength rankings, flaw analysis, conflict register) identified 45 topics, 22 conflicts, and 43 flaws. Wave 2 (advocate debate, devil's advocate attack, synthesis judge verdicts) resolved all 22 conflicts: 14 Set B, 7 HYBRID, 0 Set A.

### Decision Lineage Summary

| Decision | Source | Reference |
|----------|--------|-----------|
| 5-phase architecture | Set B ss3, modified per Verdict C-01 | Phase 0 Profile + Phase 4 Consolidation bookend scanning |
| Two-tier classification | Set B ss4, modified per Verdict C-03 | 4 primary + qualifiers with INVESTIGATE:human-review-needed added |
| Default budget 500K | Set B ss6, increased per Verdict C-08 | Original 300K deemed insufficient by flaw analysis F-B-02 |
| Minimal docs in core flow | HYBRID per Verdict C-02 | Broken refs + temporal in Phase 3; full docs opt-in via --pass-docs |
| Cross-ref with static tools | HYBRID per Verdict C-10 | 3-tier detection: static tools > grep > LLM |
| Target users and non-goals | Set A ss2-3 | Set B lacked these structural PRD elements |
| Known-issues registry | HYBRID per Verdict C-04 | Within-run dedup (Set B Phase 4) + cross-run registry (Set A, Phase 5) |
| Credential scanning | Set B ss5 Phase 1 | Non-negotiable correctness fix, unanimous agreement |
| Implementation ordering | Set B ss12, per Verdict C-05 | Dependency-aware 5-phase roadmap |

### Key Metrics

| Metric | v1 Current | v2 Target | Source |
|--------|-----------|-----------|--------|
| Files individually profiled | 12 | Budget-relative (not raw count) | [Source: FLAW F-B-01] |
| Coverage tracking | None | Per-tier manifest with PASS/WARN/FAIL | [Source: Set B ss4] |
| Cross-boundary detection | None | 3-tier dependency analysis | [Source: HYBRID C-10] |
| Credential scanning | Wrong answer (.env.production misidentified) | Correct (read actual content, pattern-match) | [Source: Set B Finding 6] |
| Classification categories | 3 (DELETE/REVIEW/KEEP) | 4 primary + 14 qualifiers | [Source: Set B ss4, modified C-03] |
| Checkpointing | None | Per-batch disk persistence with --resume | [Source: Set B ss5] |
| Known-issue dedup | None | Within-run (Phase 4) + cross-run (Phase 5, opt-in) | [Source: HYBRID C-04] |
| Budget controls | None | --budget flag, 500K default, graceful degradation | [Source: Set B ss6, modified C-08] |
| Documentation audit | None | Minimal in core; full opt-in via --pass-docs | [Source: HYBRID C-02] |

---

## 2. Problem Statement

### The Spec-Implementation Gap [Source: Set B ss2]

The current `sc:cleanup-audit` v1 spec at `/config/.claude/commands/sc/cleanup-audit.md` already promises features that were never implemented. This is the single most important structural finding from the analysis -- identified by Set B's reflection validation (B3, Dimension 2) and rated CRITICAL:

| Spec Promise | Implementation Status |
|-------------|---------------------|
| 5 categories: DELETE/CONSOLIDATE/MOVE/FLAG/KEEP | NOT IMPLEMENTED -- only DELETE/REVIEW/KEEP used |
| Coverage tracking: "transparently report what was and was not audited" | NOT IMPLEMENTED -- no coverage metrics |
| Checkpointing: "resume-from-checkpoint on session interruption" | NOT IMPLEMENTED -- no progress.json written |
| Evidence-gated classification: "requiring grep proof for every recommendation" | PARTIAL -- DELETE has evidence; KEEP has none |
| Spot-check validation: "10%" | NOT IMPLEMENTED -- no validation pass |

**Root cause**: v1 scanners were generic (6 unnamed parallel scanners) with no structured output schema, no batch file assignments, and no inter-pass coordination. The architecture could not enforce the spec's requirements. [Source: Set B ss2]

**v2 requirement**: All v1 spec promises MUST be implemented before any new features are added. This is Implementation Phase 0.

### The Quantified Quality Gap [Source: Set B Finding 2]

The v1 audit produced 12 per-file profiles out of 5,857 files -- a 99.8% miss rate. The legacy manual approach, using 27 targeted batch reports across 4 passes with human curation, produced 527+ profiles. While these numbers are not directly comparable (the manual approach involved 10-20 hours of human-guided work vs a single automated run) [Source: FLAW F-B-01], normalizing by effort still reveals a substantial gap in per-file analysis depth. The v2 spec targets budget-relative profile counts, not raw numbers.

### The User-Facing Gap [Source: Set A ss1]

From the user's perspective, the v1 output is "often insightful at the repo level but less engineer-executable for documentation and for long-lived cleanup programs." Specifically:

1. **No documentation quality assessment** -- the audit has "near-zero signal about documentation correctness" [Source: Set A ss1]
2. **No known-issues suppression** -- repeated audits rediscover the same 34+ known issues each time [Source: Set A ss4.4]
3. **Weak broken-reference reporting** -- format and systematic sweep are inadequate, especially for docs [Source: Set A ss1 Pass 1]
4. **No ARCHIVE-vs-DELETE guidance** for temporal documentation artifacts [Source: Set A ss1]
5. **Credential scanning produces wrong answers** -- real credentials in `.env.production` misidentified as template values [Source: Set B Finding 6]

---

## 3. Goals, Non-Goals, Target Users

### Goals

**Structural goals** (fix the foundation) [Source: Set B ss1]:
1. Enforce the existing v1 spec -- implement all unimplemented promises before adding new capabilities
2. Add structured batch decomposition -- domain-aware scanning with explicit file assignments
3. Require evidence for all classifications -- tiered evidence requirements based on file risk
4. Detect cross-boundary dead code -- dependency analysis after parallel scanning using static tools where available
5. Control costs -- hard budget ceiling with proportional phase allocation and graceful degradation

**User-facing goals** (fill the output gaps) [Source: Set A ss2]:
- G1. Provide a minimal documentation audit (broken references + temporal artifact classification) in the core flow, with a full docs quality pass available via --pass-docs
- G2. Support a known-issues mechanism so repeated findings are suppressed with attribution rather than re-flagged each run
- G3. Harden output schemas so critical buckets (BROKEN_REFERENCES, ARCHIVE, FLAG, coverage accounting) are consistently emitted
- G4. Preserve the current system's strengths: evidence-backed triage, duplication matrices, conservative deletion
- G5. Maintain cost control: avoid unbounded analysis and keep outputs scannable

### Non-Goals [Source: Set A ss2]

- **N1**: This is not a "cleanup executor." v2 remains read-only. No automated delete/move operations. [Source: Set A N1]
- **N2**: This is not a full semantic doc correctness checker. The docs audit focuses on structural correctness (paths, referenced files, ports, scripts), plus overlap detection and link integrity. [Source: Set A N2]
- **N3**: No attempt to eliminate human judgment; archive/delete decisions remain recommendations. [Source: Set A N3]
- **N4**: This is not a security audit substitute. Credential scanning provides basic pattern detection only. Users should use truffleHog/detect-secrets for comprehensive scanning. [Source: Set B ss5 Phase 1 disclaimer]

### Target Users [Source: Set A ss3]

| Persona | Need | Primary Use Case |
|---------|------|-----------------|
| **Repo maintainers** | Periodic audits to keep repo size, CI, and onboarding sane | U1: "Run audit and get an action list I can execute immediately" |
| **Onboarding authors** | Ensure docs don't point to dead scripts, wrong paths, or stale architectures | U3: "Find broken doc links and stale release artifacts without reading the entire docs tree" |
| **DevOps owners** | Track deploy/config drift and prevent "competing systems sprawl" | U2: "Run audit weekly without re-discovering known issues" |

---

## 4. Architecture

### 5-Phase Execution Model [Source: Set B ss3, Verdict C-01]

sc:cleanup-audit v2 is a 5-phase read-only repository audit. Phase 0 (Profile & Plan) and Phase 4 (Consolidation & Validation) bookend the core scanning phases, providing the infrastructure enforcement layer that was absent in v1.

```
Phase 0: Profile & Plan (Haiku, 30-60s)
    |
    +-- Detect domains (infrastructure, source, assets, docs)
    +-- Classify files into risk tiers (1-4)
    +-- Generate batch manifest (JSON)
    +-- Run static analysis tools where available (madge, pydeps)  [Source: DA Attack 1, HYBRID C-10]
    +-- Auto-generate config if absent
    |
    v
Phase 1: Surface Scan (Haiku scanners, parallel)
    |
    +-- Domain-aware batches with explicit file lists
    +-- Classify: DELETE / KEEP / MODIFY / INVESTIGATE
    +-- Credential file scanning (read actual content)
    +-- Gitignore consistency check
    |
    v
Phase 2: Structural Audit (Sonnet analyzers, parallel)
    |
    +-- 8-field profiles for DELETE/INVESTIGATE candidates + Tier 1-2 KEEP
    +-- File-type-specific verification rules
    +-- Signal-triggered depth escalation
    +-- Full docs audit if --pass-docs activated  [Source: HYBRID C-02]
    |
    v
Phase 3: Cross-Reference Synthesis (Sonnet comparator)
    |
    +-- Build dependency graph using 3-tier detection  [Source: HYBRID C-10]
    +-- Detect cross-boundary dead code
    +-- Produce duplication matrices
    +-- Minimal docs audit: broken references + temporal classification  [Source: HYBRID C-02]
    +-- Resolve INVESTIGATE classifications
    +-- Post-hoc deduplication  [Source: Set B Proposal 10]
    |
    v
Phase 4: Consolidation & Validation (Sonnet)
    |
    +-- Consolidate all findings, deduplicate across phases
    +-- Spot-check 10% of classifications (consistency rate)
    +-- Generate coverage report per tier
    +-- Directory-level assessment blocks for 50+ file dirs  [Source: Set A unique #3]
    +-- Write FINAL-REPORT.md
    |
    v
Output: .claude-audit/run-{timestamp}/
```

### Subagent System [Source: Set B ss3, HYBRID C-06]

**Target architecture** is Set B's 6-agent system. **Implementation starts** with Set A's conservative approach (reuse existing scanners for Phase 0-1), adding specialized agents incrementally in Phase 2+. [Source: HYBRID C-06]

| Agent | Model | Role | Phase |
|-------|-------|------|-------|
| **audit-profiler** | Haiku | Repository profiling, domain detection, tier assignment, static tool orchestration | 0 |
| **audit-scanner** | Haiku | Surface classification with evidence (simplified schema) | 1 |
| **audit-analyzer** | Sonnet | Deep structural analysis with 8-field profiles | 2 |
| **audit-comparator** | Sonnet | Cross-reference synthesis, dependency graphs | 3 |
| **audit-consolidator** | Sonnet | Report consolidation, deduplication, directory assessment | 4 |
| **audit-validator** | Sonnet | Spot-check re-verification (10% sample) | 4 |

**Schema split rationale** [Source: FLAW F-B-06]: The Phase 1 Haiku schema is simplified to essential fields only (path, classification, primary_action, qualifier, confidence, evidence_text). Complex structured fields (import_references arrays, export_targets arrays, external_dependencies) move to Phase 2 Sonnet analyzers. This reduces Haiku malformation risk while preserving the dependency graph data pipeline.

### Standardized Scanner Output Schema [Source: Set B ss3, scored 9.3 -- highest in either set]

**Phase 1 Schema (Haiku -- simplified):**

```json
{
  "scanner_id": "string",
  "domain": "string",
  "batch_id": "string",
  "files_assigned": "integer",
  "files_examined": "integer",
  "files": [{
    "path": "string",
    "risk_tier": "1|2|3|4",
    "classification": {
      "primary": "DELETE|KEEP|MODIFY|INVESTIGATE",
      "qualifier": "string",
      "confidence": "0.0-1.0"
    },
    "evidence_text": "string (free-text summary of evidence: grep commands run, results, rationale)",
    "credential_scan": "null|{has_real_credentials: bool, disclaimer: string}"
  }]
}
```

**Phase 2 Schema (Sonnet -- full 8-field profile):**

```json
{
  "file_path": "string",
  "classification": "Primary:Qualifier",
  "size_bytes": "integer",
  "evidence": {
    "import_references": ["list of files that import/reference this file"],
    "grep_command": "exact grep command used",
    "grep_result_count": "integer",
    "last_commit_date": "ISO date",
    "last_commit_author": "string",
    "test_file_exists": "boolean",
    "dynamic_import_check": "none_found|possible_dynamic:[pattern]"
  },
  "risk_tier": "1-4",
  "rationale": "2-3 sentence explanation",
  "confidence": "0.0-1.0",
  "related_files": ["files that should be considered together"]
}
```

Note: The `test_coverage` field from Set B's original schema is replaced with `test_file_exists` (a boolean checking whether a corresponding test file exists), because determining actual test coverage requires running tests with instrumentation, which is infeasible in this context. [Source: FLAW F-B-21]

**Schema validation**: Scanners that produce output not conforming to the schema trigger a validation error. The orchestrator retries the batch once, then marks it as FAILED in the coverage manifest. [Source: Set B ss3]

### The Hybrid Architecture: Static Tools + LLM Judgment [Source: DA Attack 1, HYBRID C-10]

The devil's advocate analysis identified the single largest architectural blind spot in both original analysis sets: neither proposed combining static analysis tools with LLM judgment. This unified spec addresses that gap directly.

**Principle**: Ground truth must come from deterministic tools where possible. LLMs provide judgment, classification, and reporting -- not data gathering. [Source: DA Guard Rail 1]

**Implementation**: Phase 0 runs available static analysis tools and feeds their output into the scanning pipeline:

| Tool | Language | Purpose | Confidence |
|------|----------|---------|------------|
| `madge --orphans` | JS/TS | Orphan file detection | Tier A (high) |
| `pydeps` | Python | Dependency graph | Tier A (high) |
| `ts-prune` | TypeScript | Unused exports | Tier A (high) |
| `cargo-deps` | Rust | Dependency graph | Tier A (high) |
| `grep -rL` patterns | Any | Reference counting | Tier B (medium) |
| `git log --diff-filter=A` | Any | File creation dates | Tier A (high) |
| LLM inference from file reading | Any | Relationship inference | Tier C (low) |

Static tool availability is detected in Phase 0. If a tool is not installed, the system falls back to the next tier. All dependency graph edges carry a confidence tier label (A/B/C). [Source: HYBRID C-10]

---

## 5. Unified Classification System [Source: Set B ss4, Verdict C-03]

### Two-Tier System

**Primary Action** (what to do):
- `DELETE` -- Remove the file
- `KEEP` -- No action needed
- `MODIFY` -- Keep but change something
- `INVESTIGATE` -- Insufficient evidence for automated classification; requires human input

**Secondary Qualifier** (specifics):

| Primary | Qualifier | Meaning |
|---------|-----------|---------|
| DELETE | `standard` | Safe to delete, zero references confirmed |
| DELETE | `archive-first` | Delete but preserve in archive (historically valuable). Report must include suggested destination path. [Source: Set A C-09 requirement] |
| KEEP | `verified` | Evidence confirms active use (Tier 1-2 evidence) |
| KEEP | `unverified` | No evidence checked (Tier 3-4 pattern match only) |
| KEEP | `monitor` | Active but shows warning signals (stale, low usage) |
| MODIFY | `consolidate-with:[target]` | Merge with another file |
| MODIFY | `fix-references` | Has broken references that need repair |
| MODIFY | `update-content` | Content is outdated or incorrect |
| MODIFY | `move-to:[destination]` | Should be relocated |
| MODIFY | `flag:[issue]` | Has specific issue needing attention (e.g., flag:gitignore-inconsistency) |
| INVESTIGATE | `cross-boundary` | Referenced across domain boundaries, unclear ownership |
| INVESTIGATE | `insufficient-evidence` | Evidence gathering failed or was inconclusive |
| INVESTIGATE | `dynamic-import` | May be loaded via dynamic import/require patterns |
| INVESTIGATE | `human-review-needed` | Genuinely ambiguous file requiring human judgment (not an evidence failure) [Source: FLAW F-B-19 mitigation] |

**INVESTIGATE cap**: If INVESTIGATE exceeds 15% of examined files, trigger a re-analysis pass on those files with elevated budget. This prevents INVESTIGATE from becoming a dumping ground for lazy classification. [Source: FLAW F-B-11 mitigation, Verdict C-03]

### Backward Compatibility Mapping [Source: Set B ss4]

| v1 Category | v2 Mapping | Notes |
|-------------|-----------|-------|
| DELETE | DELETE:standard | Direct mapping |
| CONSOLIDATE | MODIFY:consolidate-with:[target] | Qualifier captures merge target |
| MOVE | MODIFY:move-to:[destination] | Qualifier captures destination |
| FLAG | MODIFY:flag:[issue] | Qualifier captures specific issue |
| KEEP | KEEP:verified or KEEP:unverified | Depends on evidence depth achieved |
| REVIEW | INVESTIGATE:human-review-needed | Corrected from original mapping (Set B mapped to insufficient-evidence, but REVIEW's semantic intent is "human should look at this," not "evidence gathering failed") [Source: FLAW F-B-19] |

### File Risk Tiers [Source: Set B ss4]

| Tier | File Types | Coverage Target | Evidence Requirement | Read Depth |
|------|-----------|----------------|---------------------|------------|
| **1 (Critical)** | Deploy scripts, CI/CD, migrations, .env*, security configs | >= 100% | Full 3-field (references + recency + test_file_exists) | Full file |
| **2 (High)** | Source code, API routes, DB models, Docker/compose configs | >= 90% | 1-field mandatory, 2-field target [Source: FLAW F-B-08 relaxation] | 100 lines + signal-triggered full |
| **3 (Standard)** | Tests, utilities, build scripts, documentation | >= 70% | Relational (annotated with what they serve) | 50 lines |
| **4 (Low)** | Assets, generated files, vendor code, binaries | >= 50% | Pattern-match (exists + extension + path) | Metadata only |

Coverage targets are labeled **"initial estimates -- validate on benchmark repository before finalizing."** [Source: FLAW F-B-07]

**Evidence aspiration** [Source: Set A principle]: "All KEEP decisions should have evidence. Tiering determines depth of evidence, not whether evidence exists." Even Tier 3-4 KEEP decisions should include at minimum a one-line evidence annotation (e.g., "listed in package.json," "referenced by 3 test files").

---

## 6. Phase Specifications

### Phase 0: Profile & Plan [Source: Set B ss5]

**Agent**: audit-profiler (Haiku)
**Duration**: 30-60 seconds
**Budget**: 5% of total

**Inputs**: Repository root path, `audit.config.yaml` (if exists)

**Process**:
1. Run `git ls-files | wc -l` to count tracked files
2. Detect domains by scanning top-level and second-level directories
3. Classify each domain: infrastructure, source, assets, docs, tests, config
4. Assign risk tiers to all files based on path patterns (from config or auto-detected defaults)
5. Generate batch manifest: group files by domain, assign to scanner batches
6. **Run static analysis tools where available** [Source: HYBRID C-10, DA Attack 1]:
   - Check for `madge` (JS/TS): if installed, run `madge --orphans --json src/` and cache output
   - Check for `pydeps` (Python): if installed, run and cache output
   - Check for `ts-prune` (TS): if installed, run and cache output
   - Always run: `git log --diff-filter=A --format='%aI' --name-only` for file creation dates
   - Always run: `find . -name '.gitignore'` to collect gitignore patterns
7. If `audit.config.yaml` absent, auto-generate with detected defaults:
   - Detect framework from `package.json`, `requirements.txt`, `Cargo.toml`
   - Detect ports from `docker-compose*.yml`, `Dockerfile`
   - Detect CI/CD from `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`
8. **Monorepo detection** [Source: FLAW F-B-10]: If workspace file detected (`package.json` workspaces, `Cargo.toml` workspace, `nx.json`, `pnpm-workspace.yaml`), treat each workspace as a semi-independent unit for profiling and scanning. Batch decomposition respects workspace boundaries.

**Outputs**:
- `.claude-audit/run-{timestamp}/phase0/scan-profile.json` -- domain detection results + static tool results
- `.claude-audit/run-{timestamp}/phase0/file-manifest.json` -- every file with tier assignment
- `.claude-audit/run-{timestamp}/phase0/batch-manifest.json` -- scanner batch assignments
- `.claude-audit/run-{timestamp}/auto-config.yaml` -- auto-generated config (if absent; placed in audit output dir, NOT repo root) [Source: Set B ss10]

**Quality Gate**: Manifest must account for 100% of `git ls-files` output. Any file not assigned to a batch triggers a warning. [Source: Set B ss9]

### Phase 1: Surface Scan [Source: Set B ss5]

**Agent**: audit-scanner (Haiku, parallel instances)
**Duration**: 3-8 minutes (depends on file count and batch parallelism)
**Budget**: 25% of total

**Inputs**: batch-manifest.json from Phase 0, static analysis results from Phase 0

**Process per batch**:
1. Read batch assignment from manifest
2. For each file in batch:
   - Read file according to tier read-depth rules
   - Classify as DELETE/KEEP/MODIFY/INVESTIGATE using simplified schema
   - For DELETE: require `grep -r` proof of zero references
   - For KEEP (Tier 1-2): require at minimum import reference count
   - For KEEP (Tier 3-4): pattern-match classification
   - For credential files (`.env*`): apply credential scanning rules
3. Produce structured JSON output per Phase 1 scanner schema
4. Write batch report to disk
5. Update progress.json checkpoint

**Credential Scanning Rules** [Source: Set B Finding 6, scored 8.5]:
- Priority-ordered enumeration: `.env.production` -> `.env.prod` -> `.env` -> `.env.local` -> `.env.staging` -> `.env.test`
- Skip templates: `.env.example`, `.env.template`, `.env.sample`
- Real credential patterns: `sk-*`, `ghp_*`, `AKIA*`, `sk-ant-*`, base64 >40 chars, `BEGIN RSA PRIVATE KEY`, `BEGIN PRIVATE KEY`
- Template patterns: `CHANGE_ME_*`, `YOUR_*_HERE`, `<placeholder>`, `xxx`, `TODO`
- **NEVER print credential values** -- only confirm presence/absence
- Include disclaimer: "This is not a security audit. Use truffleHog/detect-secrets for comprehensive scanning."
- Credential pattern list is configurable via `audit.config.yaml` to accommodate new formats [Source: DA Attack on C-19]

**Gitignore Consistency Check** [Source: Set B Finding 15]:
- Compare `git ls-files` output against `.gitignore` patterns
- Flag files that are tracked despite being in `.gitignore`
- Output as `MODIFY:flag:gitignore-inconsistency`

**Outputs per batch**:
- `.claude-audit/run-{timestamp}/phase1/batch-{NN}-{domain}.json`
- `.claude-audit/run-{timestamp}/phase1/pass1-summary.json`

**Checkpointing**: After each batch completes, update `progress.json` with current_phase, batches_completed, batches_total, files_examined, files_total, token_usage, token_budget, timestamp. [Source: Set B ss5, Verdict C-21]

### Phase 2: Structural Audit [Source: Set B ss5]

**Agent**: audit-analyzer (Sonnet, parallel instances)
**Duration**: 5-12 minutes
**Budget**: 35% of total

**Inputs**: pass1-summary.json, file-manifest.json, static analysis results from Phase 0

**Process**:
1. Collect all DELETE, INVESTIGATE, and MODIFY candidates from Phase 1
2. Collect all Tier 1-2 KEEP files for evidence verification
3. For each candidate, produce mandatory 8-field profile (per Phase 2 schema above)
4. Apply file-type-specific rules:

| File Type | Additional Checks | Source |
|-----------|------------------|--------|
| Test files | pytest patterns, skip markers, `input()` calls, duplicate helpers | [Source: Set B ss5] |
| Deploy scripts | Port validation against network spec, destructive ops (`DROP`, `rm -rf`) | [Source: Set B ss5] |
| Docker/Compose | Service definition comparison, Dockerfile references, volume paths | [Source: Set B ss5] |
| Documentation | Check 3 structural claims against codebase (for Tier 1-2 docs only) | [Source: Set B ss5] |
| Config/Env | Real vs template detection, cross-config comparison | [Source: Set B ss5] |

5. **Signal-triggered depth escalation** [Source: Set B Proposal 12]:
   - Default read: 50 lines
   - Triggers for full-file read: credential-adjacent imports (`dotenv`, `config`, `secrets`); `TODO`/`FIXME`/`HACK` in first 50 lines; complex conditional logic (>3 nested conditions); `eval`, `exec`, `dangerouslySetInnerHTML`; file size > 300 lines
   - Trigger patterns configurable via `audit.config.yaml`

6. **.env key-presence matrix** (if multiple `.env*` files detected) [Source: Set A unique #5]:
   - Extract keys across `.env*` templates
   - Output a key-presence matrix showing which keys exist in which files
   - Cheap check (~2K tokens) that reveals configuration drift

7. **Full docs audit** (if `--pass-docs` flag is active) [Source: HYBRID C-02]:
   - Execute Set A's 5-section output schema (see Section 6.7 below)
   - Budget capped at 20% of total

**Outputs**:
- `.claude-audit/run-{timestamp}/phase2/profiles-batch-{NN}.json`
- `.claude-audit/run-{timestamp}/phase2/pass2-summary.json`
- `.claude-audit/run-{timestamp}/phase2/env-key-matrix.json` (if applicable)

### Phase 3: Cross-Reference Synthesis [Source: Set B ss5, HYBRID C-10]

**Agent**: audit-comparator (Sonnet)
**Duration**: 3-6 minutes
**Budget**: 20% of total

**Inputs**: All Phase 1 batch outputs, Phase 2 profiles, Phase 0 static analysis results

**3-Tier Detection Strategy** [Source: HYBRID C-10, DA Attack 1]:

| Tier | Method | Confidence | Dead Code Action |
|------|--------|------------|-----------------|
| **A (high)** | Static analysis tools (madge, pydeps, ts-prune output from Phase 0) | High | DELETE recommendation eligible |
| **B (medium)** | grep-based import/require/include pattern scanning from Phase 1 scanner output | Medium | DELETE recommendation eligible |
| **C (low)** | LLM-inferred relationships from Phase 2 analysis | Low | INVESTIGATE:cross-boundary only |

All edges in the dependency graph carry a confidence tier label (A/B/C).

**Process**:
1. Build directed dependency graph:
   - Nodes: all files in scope
   - Edges: import/export relationships from static tools (Tier A), grep patterns (Tier B), LLM inference (Tier C)
2. Identify orphan nodes (no incoming edges) -- cross-boundary dead code candidates
3. Apply confidence-tiered classification:
   - 0 incoming edges AND Tier A/B evidence AND no dynamic import patterns -> `DELETE:standard` candidate
   - 0 incoming edges BUT only Tier C evidence -> `INVESTIGATE:cross-boundary`
   - >3 hops from entry points -> `INVESTIGATE:cross-boundary`
   - 1-3 hops -> `MODIFY:flag:low-connectivity`
4. Build duplication matrices:
   - Group files by similarity (content hash, function overlap)
   - Calculate overlap percentages for each group
   - Recommend consolidation for >70% overlap
5. **Minimal docs audit (core flow)** [Source: HYBRID C-02]:
   - Broken reference sweep: extract all relative links from `.md` files, verify targets exist
   - Output in checklist format: `- [ ] filepath:line -> missing/path` [Source: Set A A-7, scored 7.5]
   - Temporal artifact classification: label docs as KEEP / DELETE:archive-first / DELETE:standard based on directory path patterns and last-modified date
   - Budget: 5-8% of total
6. Resolve INVESTIGATE classifications from Phase 1:
   - Cross-reference with graph data
   - Upgrade to DELETE/KEEP/MODIFY where evidence is now sufficient
   - Leave as INVESTIGATE where still unclear
7. Post-hoc deduplication [Source: Set B Proposal 10]:
   - Group findings by file path
   - Cluster within-file findings by issue category
   - Keep highest-severity instance of duplicates
   - Mark cross-phase-confirmed findings as "high confidence"
   - Cost: ~500 tokens

**Dynamic Import Detection** [Source: Set B ss5, FLAW F-B-23]:
Scan for patterns (configurable via `audit.config.yaml`):
- `import(` (ESM dynamic)
- `require(` (CJS dynamic)
- `React.lazy`
- `next/dynamic`
- `importlib.import_module` (Python)
- `__import__()` (Python)
- `import.meta.glob` (Vite)
- `jest.mock()`, `jest.requireActual()` (test frameworks)

Files referenced only via dynamic import -> `KEEP:monitor` (not DELETE)

**Outputs**:
- `.claude-audit/run-{timestamp}/phase3/dependency-graph.json`
- `.claude-audit/run-{timestamp}/phase3/duplication-matrix.json`
- `.claude-audit/run-{timestamp}/phase3/broken-references.json` (minimal docs audit)
- `.claude-audit/run-{timestamp}/phase3/pass3-summary.json`

### Phase 4: Consolidation & Validation [Source: Set B ss5]

**Agent**: audit-consolidator (Sonnet) + audit-validator (Sonnet)
**Duration**: 3-5 minutes
**Budget**: 15% of total

**Consolidation Process**:
1. Merge all phase summaries into unified findings list
2. Deduplicate across phases (keep highest-severity)
3. Sort by: primary classification -> risk tier -> confidence
4. Generate coverage report per tier (JSON)
5. **Directory-level assessment blocks** for directories with 50+ files [Source: Set A unique #3]:
   - Sample list (10 representative files)
   - Assessment label: `actively-maintained` | `stale` | `bulk-dump` | `mixed`
   - Recommendation
6. Generate executive summary with top 3-5 critical issues
7. Write FINAL-REPORT.md at configured report depth

**Validation Process (10% spot-check)** [Source: Set B ss5, modified per FLAW F-B-05]:
1. Random sample 10% of all classifications (stratified by tier)
2. For each sampled file: re-run evidence gathering independently, compare classification with original
3. If disagreement: flag as "disputed" with both classifications
4. Calculate **consistency rate** (NOT "agreement rate") [Source: DA Attack on C-11]
5. If ground-truth calibration files exist (3-5 manually curated files with known-correct classifications), also calculate **calibration accuracy** separately
6. If consistency rate < 85%: add warning banner to report
7. If calibration accuracy < 80%: add CRITICAL warning to report
8. Report both metrics with honest framing: "Consistency rate measures model-to-model agreement on the same inputs, not ground-truth accuracy. See Limitations section." [Source: FLAW F-B-05]

**Coverage Report Format** [Source: Set B ss5]:
```json
{
  "total_files": 5857,
  "files_examined": 5200,
  "overall_coverage": "88.8%",
  "per_tier": {
    "tier_1_critical": { "total": 45, "examined": 45, "coverage": "100%", "target": "100%", "status": "PASS" },
    "tier_2_high": { "total": 1200, "examined": 1080, "coverage": "90.0%", "target": "90%", "status": "PASS" },
    "tier_3_standard": { "total": 2100, "examined": 1470, "coverage": "70.0%", "target": "70%", "status": "PASS" },
    "tier_4_low": { "total": 2512, "examined": 1256, "coverage": "50.0%", "target": "50%", "status": "PASS" }
  },
  "evidence_depth_achieved": {
    "tier_1": "3-field average",
    "tier_2": "1.6-field average",
    "tier_3": "relational",
    "tier_4": "pattern-match"
  },
  "unexamined_files": {
    "count": 657,
    "classification": "INVESTIGATE:insufficient-evidence",
    "reason": "Budget exhausted before examination"
  }
}
```

**Outputs**:
- `.claude-audit/run-{timestamp}/FINAL-REPORT.md`
- `.claude-audit/run-{timestamp}/coverage-report.json`
- `.claude-audit/run-{timestamp}/validation-results.json`
- `.claude-audit/run-{timestamp}/progress.json` (final)

### Phase 5 (Extension): Full Documentation Audit [Source: HYBRID C-02, Set A ss4.3 scored 8.8]

Activated via `--pass-docs`. Executes as a Phase 2 extension. Budget capped at 20% of total.

**Output sections** (Set A's 5-section format -- the most complete specification of a new pass in either set) [Source: Set A A-1, scored 8.8]:

1. **SCOPE**: Directories/files scanned, sampling policy used, total doc count vs sampled count

2. **CONTENT_OVERLAP_GROUPS** [Source: Set A unique #4]:
   - Cluster by topic
   - For each group: canonical doc recommendation, superseded candidates, short rationale
   - Output format: `Group: [topic] | Canonical: path/to/doc.md | Superseded: [list] | Rationale: [text]`

3. **BROKEN_REFERENCES**:
   - Checklist format: `- [ ] filepath:line -> missing/relative/path - context` [Source: Set A A-7]
   - Scoped to relative links by default
   - Capped output with total count

4. **CLAIM_SPOT_CHECKS** [Source: HYBRID C-22]:
   - 3 claims per doc (Set B's count for cost control)
   - Applied to API-reference, setup-guide, AND architecture docs (broader than Set B, narrower than Set A's "all sampled docs")
   - Claim types with binary pass/fail criteria [Source: FLAW F-A-05 mitigation]:
     - Referenced file exists: check if path resolves to a real file
     - Referenced script/command is executable: check if script file exists in repo
     - Referenced port appears in a config file: search docker-compose/Dockerfile for port number
   - Claims that cannot be verified programmatically are explicitly labeled as requiring human review

5. **TEMPORAL_ARTIFACTS**:
   - Label docs as: KEEP / DELETE:archive-first / DELETE:standard
   - For DELETE:archive-first: include suggested destination path
   - Canonical archive destinations: `docs/archive/` for documentation, `.dev/archive/` for development artifacts, `releases/archive/` for release-related files [Source: FLAW F-A-12 mitigation]

---

## 7. Budget and Resource Controls [Source: Set B ss6, Verdict C-08]

### Token Budget System

**CLI Flag**: `--budget <tokens>` (default: **500000**) [Source: Verdict C-08 -- increased from Set B's 300K based on flaw analysis evidence that 300K is insufficient]

**CRITICAL NOTICE**: All token estimates in this specification are **UNVALIDATED -- they require empirical measurement on real repositories before being treated as reliable.** The devil's advocate analysis demonstrated that even Set B's "corrected" estimates may be 4-7x too low for comprehensive coverage. [Source: DA Part 2 budget arithmetic, FLAW F-B-02]

**Recommendation**: Run `--dry-run` on your target repository before planning. Add a 50% margin to all estimates. [Source: DA Guard Rail 2]

### Phase Allocation (Advisory, Not Hard-Wired)

| Phase | Target Allocation | Notes |
|-------|------------------|-------|
| Phase 0 | 5% | Profiling + static tool runs |
| Phase 1 | 25% | Surface scanning (Haiku) |
| Phase 2 | 35% | Structural audit (Sonnet) |
| Phase 3 | 20% | Cross-reference synthesis |
| Phase 4 | 15% | Consolidation + validation |

Phases can borrow from underutilized phases. These are target allocations, not hard partitions. [Source: Verdict C-08]

### Graceful Degradation [Source: Set B ss6]

When budget pressure activates (phase reaches 90% of allocation):

1. **First cut**: Skip Tier 4 (Low) files entirely -- report as "unexamined"
2. **Second cut**: Reduce Tier 3 (Standard) evidence to pattern-match only
3. **Third cut**: Skip Phase 3 cross-reference synthesis -- report "cross-references not generated"
4. **Fourth cut**: Reduce Phase 2 to DELETE/INVESTIGATE candidates only (skip KEEP verification)
5. **Never cut**: Phase 0 profiling, Phase 1 Tier 1-2 scanning, Phase 4 consolidation

Degradation order is configurable via `--degrade-priority` flag. For example, `--degrade-priority cross-ref-last` preserves Phase 3 at the cost of Phase 2 depth. [Source: FLAW F-B-09 mitigation]

### Budget Arithmetic Honesty [Source: DA Part 2]

The devil's advocate analysis provided detailed arithmetic showing that for a 6,000-file repo:
- Phase 0 alone may need 25-40K tokens (file list ingestion)
- Phase 1 at 23 tokens/file is physically impossible for meaningful scanning
- Phase 2 at 75 tokens/file is insufficient for 8-field profiles
- Subagent spawn overhead (~70-120K tokens) is not accounted for in phase allocations

**Response**: This spec does not claim the budget arithmetic is solved. The `--dry-run` flag exists precisely to give users per-repo cost estimates before committing. The default budget of 500K (increased from Set B's 300K) provides more headroom, but users should expect to use 800K-1M+ tokens for comprehensive coverage of a 6,000-file repo. The "Standard" scenario should be understood as "best-effort within budget," not "complete coverage." [Source: DA Guard Rails 1-2]

### Realistic Scenarios (UNVALIDATED)

| Scenario | Budget | Expected Coverage | Estimated Runtime |
|----------|--------|------------------|------------------|
| **Minimal** | 100K | Tier 1-2 only | ~8 min |
| **Standard** | 500K | Tier 1-3, partial Tier 4 | ~20-30 min |
| **Comprehensive** | 800K | All tiers | ~35-45 min |
| **Deep** | 1.5M | All tiers + full evidence + full docs audit | ~60+ min |

---

## 8. CLI Interface [Source: Set B ss7, enriched]

### Updated Command Signature

```
/sc:cleanup-audit [target-path] [flags]
```

### Flags

| Flag | Values | Default | Description | Source |
|------|--------|---------|-------------|--------|
| `--pass` | `surface\|structural\|cross-cutting\|all` | `all` | Which core pass to run | Set B |
| `--pass-docs` | (no value) | off | Include full documentation audit (Tier 2 docs) | HYBRID C-02 |
| `--batch-size` | Integer | Auto (from Phase 0 profile) | Files per scanner batch | Set B |
| `--focus` | `infrastructure\|frontend\|backend\|docs\|all` | `all` | Domain filter | Set B |
| `--budget` | Integer (tokens) | `500000` | Hard token ceiling | Set B + C-08 |
| `--report-depth` | `summary\|standard\|detailed` | `standard` | Report verbosity | Set B |
| `--tier` | `1\|2\|3\|4\|all` | `all` | Minimum risk tier to examine | Set B |
| `--resume` | (no value) | -- | Resume from last checkpoint | Set B |
| `--config` | File path | `audit.config.yaml` | Custom config file | Set B |
| `--dry-run` | (no value) | -- | Run Phase 0 only; report estimated costs | Set B ss14 |
| `--known-issues` | File path | -- | Load cross-run known-issues registry | HYBRID C-04 |
| `--degrade-priority` | `default\|cross-ref-last\|depth-first` | `default` | Control graceful degradation order | FLAW F-B-09 |

### Report Depth Levels [Source: Set B ss7]

| Level | Content | Lines |
|-------|---------|-------|
| **summary** | Executive summary, top 5 issues, coverage percentages, action counts | ~50 |
| **standard** | Summary + per-category file lists with evidence snippets + duplication matrix + coverage per tier | ~200-400 |
| **detailed** | Standard + full 8-field profiles for all examined files + dependency graph visualization + validation results | ~500-2000 |

---

## 9. Output Specification [Source: Set B ss8, enriched]

### Directory Structure

```
.claude-audit/
+-- run-{timestamp}/                    # Run isolation per F-B-16
    +-- auto-config.yaml               # Auto-generated config (if generated)
    +-- progress.json                   # Checkpoint state (updated after each batch)
    +-- FINAL-REPORT.md                # Human-readable consolidated report
    +-- coverage-report.json           # Coverage metrics per tier
    +-- validation-results.json        # Spot-check validation results
    +-- phase0/
    |   +-- scan-profile.json          # Domain detection + static tool results
    |   +-- file-manifest.json         # Every file with tier assignment
    |   +-- batch-manifest.json        # Scanner batch assignments
    |   +-- static-analysis/           # Cached output from madge, pydeps, etc.
    +-- phase1/
    |   +-- batch-01-infrastructure.json
    |   +-- batch-02-frontend-source.json
    |   +-- batch-NN-*.json
    |   +-- pass1-summary.json
    +-- phase2/
    |   +-- profiles-batch-01.json
    |   +-- profiles-batch-NN.json
    |   +-- pass2-summary.json
    |   +-- env-key-matrix.json        # If multiple .env* files detected [Source: Set A]
    |   +-- docs-audit/                # If --pass-docs activated [Source: Set A]
    |       +-- docs-quality-report.json
    +-- phase3/
    |   +-- dependency-graph.json
    |   +-- duplication-matrix.json
    |   +-- broken-references.json     # Minimal docs audit (core flow)
    |   +-- pass3-summary.json
    +-- phase4/
        +-- consolidation-log.json
        +-- directory-assessments.json  # Large-dir assessment blocks [Source: Set A]
```

### FINAL-REPORT.md Structure [Source: Set B ss8, enriched with Set A output formats]

```markdown
# Repository Cleanup Audit -- Final Report

## Audit Metadata
- Date, branch, commit, file count, budget used/total, runtime
- Config source: auto-generated | user-provided | hybrid
- Static tools used: [list of tools run in Phase 0]

## Limitations  [Source: DA Guard Rail 5]
- Which files were examined vs skipped
- Which evidence is from deterministic tools (grep, git, static analysis) vs LLM judgment
- Confidence scores are NOT calibrated probabilities
- Dependency graph may miss dynamic imports (confidence tier noted per edge)
- Actual token cost and budget utilization

## Coverage Summary
- Per-tier coverage table with PASS/WARN/FAIL status
- Evidence depth achieved per tier

## Validation Summary
- Consistency rate: X% (across random sample)
- Calibration accuracy: Y% (against known-correct files, if available)
- Disputed classifications count

## Executive Summary
- Top 3-5 critical issues
- Action counts: N DELETE, N KEEP (M unverified), N MODIFY, N INVESTIGATE

## Critical Issues (INVESTIGATE items)
- Files requiring human decision with evidence summary

## DELETE Recommendations
- DELETE:standard -- grouped by domain, each with evidence and confidence
- DELETE:archive-first -- separate subsection titled "Archive Before Deletion" with destination paths

## MODIFY Recommendations
- Grouped by qualifier (consolidate, fix-references, move, flag)

## KEEP Summary
- Verified vs unverified counts
- Monitor items (low-confidence KEEP)

## Broken References  [Source: Set A checklist format]
- Checklist: `- [ ] filepath:line -> missing/path`
- Total count

## Duplication Matrix
- Top N duplication groups with overlap percentages

## Directory Assessments  [Source: Set A unique #3]
- For each 50+ file directory: sample, assessment label, recommendation

## Unexamined Files
- List of files not examined with reason (budget, exclusion, error)

## Appendix: Verification Commands
- Reproducible bash commands to verify key claims
```

### JSON Schemas

All intermediate phase outputs use JSON for machine parseability. The FINAL-REPORT.md is generated by the consolidator from these JSON artifacts, ensuring consistency. [Source: Verdict C-17]

---

## 10. Quality Gates [Source: Set B ss9, modified]

### Per-Phase Quality Gates

| Gate | Phase | Criteria | On Failure |
|------|-------|----------|------------|
| **Manifest Completeness** | 0->1 | 100% of git-tracked files assigned to batches | Block Phase 1 |
| **Scanner Schema Compliance** | 1 | All batch outputs conform to Phase 1 scanner schema | Retry batch once, then mark FAILED |
| **Evidence Sufficiency** | 1->2 | DELETE candidates have grep proof | Block promotion to Phase 2 |
| **Profile Completeness** | 2->3 | All 8 fields populated for profiled files | Warn in report, continue |
| **Coverage Threshold** | 2->3 | Tier 1 >= 100%, Tier 2 >= 90% (initial estimates) | Warn if below, never block |
| **Cross-Ref Graph Valid** | 3->4 | Dependency graph has no orphan batches | Warn in report, continue |
| **Consistency Rate** | 4 | >= 85% consistency rate on 10% spot-check | Add warning banner to report |
| **INVESTIGATE Cap** | 4 | <= 15% of examined files classified INVESTIGATE | Trigger re-analysis of excess INVESTIGATE items [Source: FLAW F-B-11] |

### Anti-Lazy Enforcement [Source: Set B ss9, scored 8.3]

Scanners are validated by structured output, not tool-call counts:

1. **Required output fields**: Every file must have `classification`, `evidence_text`, `confidence`
2. **Evidence non-emptiness**: DELETE must have grep evidence with result count of 0; Tier 1-2 KEEP must have import reference information
3. **Confidence distribution**: If >90% of files in a batch have identical confidence values, flag batch for re-review
4. **Cross-batch consistency**: If two scanners classify the same file differently, trigger targeted re-review

### Subagent Failure Handling [Source: FLAW CS-04]

- **Per-subagent timeout**: 120 seconds
- **Max retries**: 2 (with exponential backoff)
- **On persistent failure**: Mark batch as FAILED, continue with remaining batches
- **Cascading failure detection**: If 3 consecutive batches fail, pause execution, report the failure, and generate a minimum viable report from completed batches
- **Minimum viable report**: Requires 50%+ of batches to have completed successfully. Below 50%, emit an error report explaining what went wrong.

### Validation Naming Convention [Source: DA Attack on C-11, FLAW F-B-05]

The spot-check validation measures **consistency** (do two model runs agree?), not **correctness** (is the classification right?). This distinction is critical:

- The metric is called "consistency rate," not "agreement rate" or "accuracy"
- The report explicitly states: "Two LLM instances can consistently agree on wrong answers. This metric catches systematic scanner failures but does not guarantee ground-truth accuracy."
- Where feasible, include 3-5 calibration files with human-verified correct classifications as ground-truth anchors [Source: DA Guard Rail 5]

---

## 11. Known-Issues System [Source: HYBRID C-04]

### Within-Run: Post-Hoc Deduplication (Phase 4) [Source: Set B Proposal 10]

The consolidator agent in Phase 4 performs within-run deduplication:
1. Group findings by file path
2. Cluster within-file findings by issue category
3. Keep highest-severity instance
4. Mark cross-phase-confirmed findings as "high confidence"
5. Remove remaining duplicates

Cost: ~500 tokens in consolidator prompt. Zero runtime overhead during scanning. Zero parallelism loss.

### Cross-Run: Optional JSON Registry (Phase 5 Extension) [Source: Set A ss4.4, scored 8.5]

Activated via `--known-issues <path>` flag. The registry enables the weekly-audit use case (U2): "Run audit weekly without re-discovering known issues."

**Schema** [Source: Set A ss4.4]:

```json
{
  "version": "1.0",
  "entries": [{
    "id": "string (unique identifier)",
    "signature": "string (content-based, not path-based -- survives renames)",
    "category": "DELETE|KEEP|MODIFY|INVESTIGATE",
    "qualifier": "string",
    "created_at": "ISO date",
    "ttl_days": 90,
    "status": "open|closed|monitor",
    "reference": "string (link to tracking issue or PR)"
  }],
  "max_entries": 200
}
```

**Lifecycle rules** [Source: FLAW F-A-04 mitigation]:
- TTL per entry: default 90 days. Entries older than TTL are auto-expired.
- Auto-prune: if the referenced file no longer exists in the repo, mark entry as "stale" and do not suppress
- Max entries: 200 with LRU (least-recently-used) eviction
- The registry is loaded as **read-only context for the consolidator** (not injected into scanner prompts), preserving scanning parallelism

**Matching**: Signature-based, not path-based. If a file is renamed but the content signature matches, the suppression still applies. [Source: Set A ss4.4]

**Output**: Findings matching a known issue are reported in an `ALREADY_TRACKED` section of FINAL-REPORT.md with attribution to the registry entry.

---

## 12. Cold-Start and Configuration [Source: Set B ss10]

### First-Run Experience

When `audit.config.yaml` is absent:

1. Phase 0 profiler auto-generates a default config based on:
   - Framework detection: `package.json` -> Node.js patterns; `requirements.txt` -> Python patterns; `Cargo.toml` -> Rust patterns
   - Port detection: scan `docker-compose*.yml` for port mappings
   - CI/CD detection: check `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`
   - Static tool detection: check if `madge`, `pydeps`, `ts-prune` are available
2. Generated config is written to `.claude-audit/run-{timestamp}/auto-config.yaml` (NOT repo root)
3. Report header notes: "AUTO-DETECTED -- review for accuracy. Customize at audit.config.yaml for future runs."
4. If auto-detection confidence is below 70% for any field, the field is set to a conservative default and flagged in the report. [Source: Verdict C-12]
5. **Never fail on missing config** -- always generate sensible defaults [Source: Set B ss10]

### --dry-run Integration

`--dry-run` runs Phase 0 only and displays:
- Detected domains and file counts
- Generated tier assignments summary
- Available static analysis tools
- Estimated token budget per phase (UNVALIDATED)
- Generated batch manifest preview
- Auto-generated config preview

This gives users visibility into audit scope before committing resources. [Source: Set B ss14]

### Calibration Files

Deferred to Phase 5 implementation. Both analysis sets agree that calibration files are valuable but impractical on cold-start (no known-good/bad files exist for a new repo). The recommended approach is to use v2 first-run results as a calibration baseline for subsequent runs. [Source: Set B ss10]

---

## 13. Risk Mitigation

### Risk Register

| # | Risk | Severity | Mitigation | Source |
|---|------|----------|------------|--------|
| R1 | Token budget overrun | HIGH | `--budget` flag with graceful degradation. Default raised to 500K. `--dry-run` for cost preview. | [Source: Set B ss11, FLAW F-B-02] |
| R2 | Config cold-start failure | HIGH | Auto-generate defaults from project structure detection. Never fail on missing config. | [Source: Set B ss11] |
| R3 | Dynamic import false positives | HIGH | Configurable pattern list. Files referenced only via dynamic import -> KEEP:monitor not DELETE. | [Source: Set B ss11, FLAW F-B-23] |
| R4 | LLM output schema non-compliance | MEDIUM | Schema validation post-processing. Retry once on malformed output. Simplified Phase 1 schema for Haiku. | [Source: FLAW F-B-06] |
| R5 | Report overwhelming | MEDIUM | `--report-depth` flag with 3 levels. | [Source: Set B ss11] |
| R6 | Monorepo scaling (50K+ files) | HIGH | Monorepo detection in Phase 0. Per-workspace treatment. Per-directory coverage tracking above 10K files. System does NOT scale linearly past ~10K files. | [Source: FLAW F-B-10, DA Part 3] |
| R7 | Spec-implementation gap recurrence | CRITICAL | Every spec promise has an acceptance test. Traceability matrix in roadmap. | [Source: Set B ss11, FLAW F-B-13] |
| R8 | Credential value exposure | CRITICAL | Scanner prompts explicitly prohibit printing credential values. | [Source: Set B ss11] |
| R9 | Phase 0 auto-config correctness | HIGH | Config written as visible artifact. --dry-run shows config. User config overrides. Low-confidence fields use conservative defaults. | [Source: FLAW F-B-04] |
| R10 | LLM-on-LLM validation limitations | HIGH | Renamed to "consistency rate." Calibration files recommended. Honest limitations in report. | [Source: FLAW F-B-05] |
| R11 | Non-English documentation | MEDIUM | Acknowledged limitation. UTF-8 handling required. Full multilingual support out of scope for v2. | [Source: FLAW CS-01] |
| R12 | Non-markdown documentation formats | MEDIUM | v2 supports `.md` first-class, `.rst` best-effort. Other formats out of scope. | [Source: FLAW CS-02] |
| R13 | Concurrent audit runs | LOW | Run-ID isolation via `.claude-audit/run-{timestamp}/`. True distributed coordination out of scope. | [Source: FLAW F-B-16] |
| R14 | GFxAI over-fitting | MEDIUM | Separate universal audit features from project-specific rule examples. All project-specific rules loadable from config. | [Source: FLAW CS-05] |
| R15 | Implementation effort underestimate | HIGH | Effort estimates in roadmap are 3-5x too low per devil's advocate analysis. Benchmark by implementing one feature before planning sprints. | [Source: FLAW F-B-14, DA Guard Rail 8] |
| R16 | Run-to-run non-determinism | MEDIUM | LLM outputs are inherently non-deterministic. Grounding in static analysis output (madge, grep, git) reduces variance. Diff between two runs is unreliable for trend tracking. | [Source: DA Part 6 blind spot 2] |
| R17 | Context window filling | HIGH | Phase 3 and Phase 4 require reading large volumes of prior phase output. Write-to-disk architecture helps but re-reading costs tokens. Account for this in budget. | [Source: DA Part 3] |
| R18 | "Clean repo" output | LOW | Define a "clean report" template that positively confirms repo health when there are zero significant findings. | [Source: FLAW CS-03] |

---

## 14. Implementation Roadmap [Source: Set B ss12, Verdict C-05]

### Phase 0: Enforce Existing Spec (CRITICAL)

Implement all v1 spec promises:
1. 5-category classification (via two-tier system backward compatibility)
2. Coverage tracking with per-tier reporting
3. Checkpointing via progress.json after each batch
4. Evidence-gated classification (grep proof for DELETE, import info for Tier 1-2 KEEP)
5. 10% spot-check validation pass (labeled as "consistency rate")

**Estimated effort**: UNVALIDATED -- benchmark by implementing checkpointing first, then extrapolate
**Dependencies**: None

### Phase 1: Correctness Fixes

1. Credential file scanning (read actual .env content) [Source: Set B ss12]
2. Gitignore consistency check [Source: Set B ss12]
3. Standardized scanner output schema (Phase 1 simplified version) [Source: Set B ss12]

**Estimated effort**: UNVALIDATED
**Dependencies**: Roadmap Phase 0

### Phase 2: Infrastructure

1. Repository profiling (Phase 0 audit-profiler agent) [Source: Set B ss12]
2. Dynamic batch decomposition with domain-aware assignments [Source: Set B ss12]
3. Coverage manifest with tier tracking [Source: Set B ss12]
4. Unified classification system (two-tier with backward compat mapping) [Source: Set B ss12]
5. .env key-presence matrix [Source: Set A unique, inserted here]

**Estimated effort**: UNVALIDATED
**Dependencies**: Roadmap Phase 1

### Phase 3: Depth Improvements

1. Evidence-mandatory KEEP for Tier 1-2 files [Source: Set B ss12]
2. Cross-reference synthesis with 3-tier detection strategy (static tools integration) [Source: HYBRID C-10]
3. File-type-specific verification rules [Source: Set B ss12]
4. Signal-triggered depth escalation [Source: Set B ss12]
5. Budget controls with graceful degradation [Source: Set B ss12]
6. Minimal docs audit (broken refs + temporal classification) in Phase 3 core flow [Source: HYBRID C-02]
7. Directory-level assessment blocks for large directories [Source: Set A unique, inserted here]

**Estimated effort**: UNVALIDATED
**Dependencies**: Roadmap Phase 2

### Phase 4: Quality & Polish

1. Post-hoc deduplication in consolidator [Source: Set B ss12]
2. Report depth control (`--report-depth`) [Source: Set B ss12]
3. Resume from checkpoint (`--resume`) [Source: Set B ss12]
4. Anti-lazy enforcement validation [Source: Set B ss12]

**Estimated effort**: UNVALIDATED
**Dependencies**: Roadmap Phase 3

### Phase 5: Extensions (Future)

1. Full documentation audit pass (`--pass-docs`) with Set A's 5-section output format [Source: HYBRID C-02]
2. Cross-run known-issues registry (`--known-issues`) [Source: HYBRID C-04]
3. Anti-lazy calibration files (using prior run as baseline) [Source: Set B ss12]
4. Progressive agent specialization (6-agent target from existing generic start) [Source: HYBRID C-06]
5. Content overlap group output specification [Source: Set A unique #4]

**Estimated effort**: UNVALIDATED
**Dependencies**: Roadmap Phase 4 + at least one prior audit run for calibration

---

## 15. Acceptance Criteria [Source: Set B ss13 + Set A ss7]

### Per-Requirement Acceptance Tests

| # | Requirement | Acceptance Test | Source |
|---|-------------|----------------|--------|
| AC1 | 5-category classification | FINAL-REPORT.md contains at least 2 of: DELETE, KEEP, MODIFY, INVESTIGATE | Set B |
| AC2 | Coverage tracking | coverage-report.json exists with per-tier percentages | Set B |
| AC3 | Checkpointing | progress.json updated after every batch; `--resume` recovers from interrupted state | Set B |
| AC4 | Evidence for DELETE | Every DELETE entry has non-empty grep evidence with result count of 0 | Set B |
| AC5 | Evidence for Tier 1-2 KEEP | Every Tier 1-2 KEEP has non-empty import reference information | Set B |
| AC6 | Spot-check validation | validation-results.json exists with >= 10% sample size | Set B |
| AC7 | Credential scanning | `.env.production` correctly identified: real credentials flagged, template values not flagged | Set B |
| AC8 | Gitignore check | Files tracked despite .gitignore rules are flagged as MODIFY:flag:gitignore-inconsistency | Set B |
| AC9 | Budget control | Audit completes within `--budget` +/- 10% without crashing | Set B |
| AC10 | Report depth | `--report-depth summary` produces <100 lines; `detailed` includes 8-field profiles | Set B |
| AC11 | Scanner schema | All Phase 1 batch outputs validate against Phase 1 scanner schema | Set B |
| AC12 | Cross-reference | Phase 3 produces dependency-graph.json with node count > 0 | Set B |
| AC13 | Cold-start | Audit succeeds on first run without pre-existing config file | Set B |
| AC14 | Broken references (minimal docs) | Phase 3 output includes broken-references.json with checklist format | HYBRID C-02 |
| AC15 | Backward compat | v2 output can be mapped to v1 categories using the mapping table | Set B |
| AC16 | Directory assessment | Directories with 50+ files have assessment labels in FINAL-REPORT.md | Set A |
| AC17 | INVESTIGATE cap | If INVESTIGATE > 15% of examined files, re-analysis is triggered | FLAW F-B-11 |
| AC18 | Subagent failure handling | 3 consecutive batch failures trigger pause + minimum viable report | FLAW CS-04 |
| AC19 | --dry-run | Running with --dry-run produces cost estimates without executing scans | Set B ss14 |
| AC20 | Run isolation | Two concurrent audit runs produce separate output directories | FLAW F-B-16 |

### Test Tiers [Source: FLAW CS-06 mitigation]

1. **Structural tests**: Output files exist, JSON is valid, required sections present in FINAL-REPORT.md, schema fields populated
2. **Property tests**: Coverage percentages within range, no credential values appear in any output file, all Tier 1 files examined, INVESTIGATE <= 15%
3. **Benchmark tests**: Run against 2-3 real repositories with known characteristics (one small, one medium, one with known dead code). Verify that known dead code files are flagged. Measure token consumption per phase.

---

## 16. Rejected Alternatives Appendix

This section documents positions that were considered and rejected during the merge process, preserving institutional knowledge and preventing re-litigation.

### RA-1: 4-Pass Additive Architecture (Set A Position on C-01)

**Position**: Keep the existing 3-pass structure and add a 4th Pass for Docs Quality. Additive design with minimal disruption.

**Why rejected**: The conflict register and flaw analysis demonstrated that the existing 3-pass architecture is not merely incomplete but structurally incapable of delivering on its own promises (12 profiles from 5,857 files). Adding a 4th pass to a system that already fails to enforce its spec would repeat the v1 failure pattern. F-A-03 further showed that Pass 4 would depend on infrastructure (structured inter-pass data) that the existing passes do not provide.

**What was preserved**: Set A's insight that the docs audit addresses the primary user complaint is preserved via the HYBRID C-02 verdict (minimal docs in core flow + full docs opt-in).

### RA-2: Flat Classification Categories (Set A Position on C-03)

**Position**: 5+ flat output buckets (DELETE, KEEP, ARCHIVE, FLAG, BROKEN_REFERENCES) with named sections for each action type.

**Why rejected**: Flat categories cannot express compound states (e.g., "delete this file but first archive it"). The two-tier system subsumes all of Set A's categories via qualifiers while being extensible (new qualifiers can be added without schema changes). Set B's backward compatibility mapping further ensures v1 interoperability.

**What was preserved**: Set A's concern about report scanability is addressed by rendering qualifier groupings as visually distinct sections in FINAL-REPORT.md. Engineers see an "Archive Before Deletion" section, not raw `DELETE:archive-first` labels.

### RA-3: Docs Audit as P0 Must-Have (Set A Position on C-02)

**Position**: Pass 4 Docs Quality is mandatory when `--pass all` is used. Classified as P0 (must-have).

**Why rejected**: Token cost analysis (B3, Dimension 3) showed that a full docs audit at 175K-585K additional tokens would blow the budget. Mandating it without a cost model (F-A-01) is irresponsible. Additionally, infrastructure fixes (credential scanning, coverage tracking, batch decomposition) have higher ROI because they catch correctness failures, not just depth gaps.

**What was preserved**: A minimal docs audit (broken references + temporal classification) is included in the core Phase 3 flow. The full docs audit is available via `--pass-docs` with a 20% budget cap.

### RA-4: Uniform Evidence for All KEEP (Set A Position on C-07)

**Position**: Evidence is mandatory for all KEEP decisions without tiering by risk.

**Why rejected**: The token cost for uniform full evidence across ~5,800 files is 175K-585K additional tokens (potentially tripling the audit cost). This is infeasible within any reasonable budget. The tiered approach delivers full evidence for the 10-20% of files where misclassification has the highest consequence.

**What was preserved**: Set A's principle ("All KEEP decisions should have evidence") is retained as an aspiration. Even Tier 3-4 files get at minimum a one-line evidence annotation. Tiering determines evidence depth, not whether evidence exists.

### RA-5: Known-Issues Registry as Primary Dedup Mechanism (Set A Position on C-04)

**Position**: Sequential JSON registry loaded before passes, with signature-based suppression during scanning.

**Why rejected for within-run use**: A sequential registry creates a serialization bottleneck in a parallel scanning architecture. Post-hoc dedup in the consolidator is cheaper (500 tokens) and preserves parallelism.

**What was preserved**: The registry is adopted for cross-run suppression (the use case Set B did not address) as a Phase 5 opt-in extension. It is loaded as read-only consolidator context, not injected into scanner prompts.

### RA-6: LLM-Only Dependency Graph (Set B Original Position on Phase 3)

**Position**: Build directed dependency graph entirely from LLM-read file snippets (50-100 lines per file) including import_references, export_targets, and external_dependencies arrays.

**Why rejected as the sole approach**: F-B-03 (CRITICAL) demonstrated that LLM-based import graph construction is unreliable across languages (dynamic imports, barrel re-exports, webpack aliases defeat LLM extraction). The devil's advocate further showed that static analysis tools like `madge` produce 100% accurate graphs for static imports in seconds at zero token cost.

**What replaced it**: The 3-tier detection strategy (static tools > grep > LLM) uses each approach where it is strongest. LLM inference is retained as Tier C (low confidence) for cases where no better option exists, but DELETE recommendations only come from Tier A/B evidence.

### RA-7: Conservative Agent Reuse (Set A Position on C-06)

**Position**: Reuse existing generic agents. Only add specialized agents if quality is consistently poor.

**Why rejected as the permanent approach**: The existing generic scanners produced 12 profiles from 5,857 files -- a documented failure attributable to lack of specialization, structured output, and domain awareness.

**What was preserved**: Set A's conservative approach is adopted as the starting point for implementation (Phase 0-1 uses existing agents). Progressive specialization toward Set B's 6-agent target happens in Phase 2+.

---

## 17. Known Risks and Limitations

### LLM Fundamental Limitations [Source: DA Parts 1-4]

1. **Confidence scores are not calibrated probabilities.** An LLM saying "confidence: 0.92" means it generated that token sequence, not that there is a 92% chance the classification is correct. The unified spec retains confidence scores as relative ordering signals but the report explicitly states this limitation. [Source: DA Attack 2]

2. **Evidence-gated classification has circular elements.** The LLM gathers evidence (runs grep), interprets the evidence, makes a classification, and assigns a confidence score. At no point does a ground-truth oracle enter the picture for most files. The hybrid architecture (static tools for ground truth) partially addresses this, but LLM judgment remains the final classifier. [Source: DA Attack 2]

3. **Run-to-run consistency is not guaranteed.** Two runs on the same repo without changes may produce different results because LLM outputs are non-deterministic. This means diff-based trend tracking ("are we improving?") is unreliable. Grounding in static analysis output reduces but does not eliminate variance. [Source: DA Part 6 blind spot 2]

4. **The system does not scale linearly past ~10,000 files.** File list ingestion, batch manifest size, and subagent spawn overhead all grow with file count. For monorepos exceeding 50,000 files, the system's current design is impractical. [Source: DA Part 3]

### The Hybrid Architecture Gap

This spec calls for integrating static analysis tools (madge, pydeps, ts-prune) in Phase 0. This integration is not fully designed:
- Tool installation detection needs specification
- Output parsing for each tool needs implementation
- Fallback behavior when tools are unavailable needs testing
- The interaction between static tool output and LLM classification needs prompt engineering

This gap is acknowledged. The 3-tier detection strategy provides the framework; the implementation details require engineering effort. [Source: DA Part 6 blind spot 1]

### Unvalidated Budget Arithmetic

The devil's advocate analysis demonstrated that token budget estimates in this spec may be 4-7x too low for comprehensive coverage. The `--dry-run` flag and the `UNVALIDATED` labels throughout the budget section are mitigations, not solutions. Real benchmarking on representative repositories is a prerequisite for reliable budget defaults. [Source: DA Part 2]

### Maintenance Surface Area [Source: DA Part 6 blind spot 5]

The system as specified has a significant maintenance surface:
- 6 system prompts to maintain (one per agent)
- Credential pattern lists to update as new services launch
- Dynamic import pattern lists to update as frameworks evolve
- Token budget estimates to recalibrate as models change
- `audit.config.yaml` defaults to update as conventions shift

This maintenance burden is acknowledged but not addressed in the v2 spec beyond making pattern lists configurable.

### User Feedback Loop Missing [Source: DA Part 6 blind spot 3]

This spec designs a one-shot tool. It does not include:
- User correction mechanisms ("you classified X as DELETE but it is actually used")
- Learning from prior runs ("last time you flagged 50 files and the user kept 48")
- Incremental audit ("only scan files changed since last audit")

These are desirable features for a future version but are explicitly out of scope for v2.

---

## 18. Expert Panel Consensus

**Framing note**: The following is a self-assessment using named analytical frameworks, not an actual external expert review. [Source: FLAW F-B-22 mitigation]

### Karl Wiegers (Requirements Quality)

Are the requirements testable? **Assessment**: Yes. Every v1 spec promise and every v2 addition has a corresponding acceptance test (Section 15). The traceability from problem statement -> goals -> phase specifications -> acceptance criteria is complete. The addition of the spec-implementation gap table (Section 2) ensures v2 does not repeat v1's pattern of untestable promises.

**Remaining concern**: Several acceptance tests are structural ("file exists with content") rather than behavioral ("produces correct classification"). Property tests and benchmark tests (Section 15 test tiers) partially address this but ground-truth evaluation remains limited.

### Martin Fowler (Evolutionary Architecture)

Is the design evolutionary? **Assessment**: Yes, with caveats. The progressive agent specialization approach (start with existing agents, specialize incrementally) follows evolutionary architecture principles. The composable two-tier classification system allows adding qualifiers without schema changes. The configurable pattern lists and config-driven tier assignments support project-specific adaptation.

**Remaining concern**: The 5-phase pipeline with sequential dependencies is not easily decomposable. If Phase 0 produces incorrect tier assignments, every downstream phase inherits the error. An evolutionary approach would allow phases to be independently improved and replaced.

### Michael Nygard (Production Systems)

Are failure modes handled? **Assessment**: Substantially. The graceful degradation sequence, subagent failure handling (timeout + retry + FAILED marking), minimum viable report threshold, and "never block on quality gate failure" design all show production thinking. The `--dry-run` flag for cost estimation before commitment is a direct response to Nygard's Release It! patterns.

**Remaining concern**: The cascading failure scenario (Phase 0 misclassifies -> all downstream phases produce wrong results) needs more explicit detection. A post-Phase-1 sanity check ("did the distribution of classifications match expectations for this repo type?") would help.

### Lisa Crispin (Quality Strategy)

Is the quality strategy sound? **Assessment**: Yes, with honest limitations. The three-tier test strategy (structural + property + benchmark) provides layered quality assurance. The consistency rate (not "agreement rate") naming is honest about what LLM-on-LLM validation actually measures. The 15% INVESTIGATE cap prevents quality erosion through lazy classification.

**Remaining concern**: The benchmark test tier requires real repositories with known characteristics, which requires manual curation effort. Without this investment, only the structural and property test tiers will be active, which may miss classification accuracy issues.

---

*Unified specification generated 2026-02-20 via 4-wave adversarial merge process.*
*Input: 6 source documents (2 Set A + 4 Set B), 4 Wave 1 analysis documents, 4 Wave 2 debate documents.*
*Quality targets: Specificity >= 9.0, Evidence Quality >= 8.5, Implementability >= 8.5, Architectural Soundness >= 8.5, Composite >= 8.6.*
*All token budget estimates are UNVALIDATED and require empirical benchmarking before use.*
