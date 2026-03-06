# sc:cleanup-audit v2 — Product Requirements Document

**Version**: 2.0
**Date**: 2026-02-20
**Status**: DRAFT — Pending Implementation
**Input Sources**:
- `cleanup-audit-improvement-findings.md` (15 findings from 4-agent analysis)
- `cleanup-audit-improvement-proposals.md` (12 proposals from 4-agent debate)
- `cleanup-audit-reflection-validation.md` (5-dimension validation, 8 critical corrections)
- `/config/.claude/commands/sc/cleanup-audit.md` (current v1 spec)

**Expert Panel**: Karl Wiegers (Requirements), Martin Fowler (Architecture), Michael Nygard (Production Systems), Lisa Crispin (Quality)

---

## 1. Executive Summary

### Problem Statement

The current `sc:cleanup-audit` v1 produces **44x fewer per-file profiles** (12 vs 527+), **misses credential files**, **has no batch decomposition**, and **lacks cross-boundary dead code detection** compared to the manual prompts it replaced. Additionally, the v1 spec already defines features (5 categories, coverage tracking, checkpointing, evidence-gated classification) that were **never implemented**.

### Solution

sc:cleanup-audit v2 is a 5-phase read-only repository audit that:
1. **Enforces the existing spec** — implements all v1 promises before adding new capabilities
2. **Adds structured batch decomposition** — domain-aware scanning with explicit file assignments
3. **Requires evidence for all classifications** — tiered evidence requirements based on file risk
4. **Detects cross-boundary dead code** — dependency graph synthesis after parallel scanning
5. **Controls costs** — hard budget ceiling with proportional phase allocation

### Key Metrics (Target vs Current)

| Metric | v1 Current | v2 Target |
|--------|-----------|-----------|
| Files individually profiled | 12 | 200-700+ (tiered) |
| Coverage tracking | None | Per-tier manifest with percentages |
| Cross-boundary detection | None | Dependency graph with confidence scoring |
| Credential scanning | Wrong answer | Correct (read actual .env content) |
| Recommendation categories | 3 (DELETE/REVIEW/KEEP) | 4 primary + qualifiers |
| Checkpointing | None | Per-phase disk persistence |
| Known-issue deduplication | None | Post-hoc consolidator dedup |
| Budget controls | None | `--budget` flag with proportional allocation |

---

## 2. Current State Assessment

### Spec-Implementation Gap (CRITICAL)

The v1 spec at `/config/.claude/commands/sc/cleanup-audit.md` already promises these features that **were not implemented**:

| Spec Promise | Implementation Status |
|-------------|---------------------|
| 5 categories: DELETE/CONSOLIDATE/MOVE/FLAG/KEEP | NOT IMPLEMENTED — only DELETE/REVIEW/KEEP used |
| Coverage tracking: "transparently report what was and was not audited" | NOT IMPLEMENTED — no coverage metrics |
| Checkpointing: "resume-from-checkpoint on session interruption" | NOT IMPLEMENTED — no progress.json written |
| Evidence-gated classification: "requiring grep proof for every recommendation" | PARTIAL — DELETE has evidence; KEEP has none |
| Spot-check validation: "10%" | NOT IMPLEMENTED — no validation pass |

**v2 Requirement**: All v1 spec promises MUST be implemented before any new features are added. This is Phase 0.

### Root Cause Analysis

The gap exists because v1 scanners were generic (6 unnamed parallel scanners) with no structured output schema, no batch file assignments, and no inter-pass coordination. The architecture didn't enforce the spec's requirements.

---

## 3. Architecture

### Subagent System

| Agent | Model | Role | Phase |
|-------|-------|------|-------|
| **audit-profiler** | Haiku | Repository profiling, domain detection, tier assignment | 0 |
| **audit-scanner** | Haiku | Surface classification with evidence | 1 |
| **audit-analyzer** | Sonnet | Deep structural analysis with 8-field profiles | 2 |
| **audit-comparator** | Sonnet | Cross-reference synthesis, dependency graphs | 3 |
| **audit-consolidator** | Sonnet | Report consolidation, deduplication | 4 |
| **audit-validator** | Sonnet | Spot-check re-verification (10% sample) | 4 |

### Execution Flow

```
Phase 0: Profile & Plan (Haiku, 30-60s)
    │
    ├── Detect domains (infrastructure, source, assets, docs)
    ├── Classify files into risk tiers (1-4)
    ├── Generate batch manifest (JSON)
    ├── Auto-generate config if absent
    │
    ▼
Phase 1: Surface Scan (Haiku scanners, parallel)
    │
    ├── Domain-aware batches with explicit file lists
    ├── Classify: DELETE / KEEP / MODIFY / INVESTIGATE
    ├── Credential file scanning (read actual content)
    ├── Gitignore consistency check
    │
    ▼
Phase 2: Structural Audit (Sonnet analyzers, parallel)
    │
    ├── 8-field profiles for DELETE/INVESTIGATE candidates
    ├── Evidence-mandatory KEEP for Tier 1-2 files
    ├── File-type-specific verification rules
    ├── Signal-triggered depth escalation
    │
    ▼
Phase 3: Cross-Reference Synthesis (Sonnet comparator)
    │
    ├── Build dependency graph from structured scanner output
    ├── Detect cross-boundary dead code
    ├── Produce duplication matrices
    ├── Resolve INVESTIGATE classifications
    │
    ▼
Phase 4: Consolidation & Validation (Sonnet)
    │
    ├── Consolidate all findings, deduplicate
    ├── Spot-check 10% of classifications
    ├── Generate coverage report per tier
    ├── Write FINAL-REPORT.md
    │
    ▼
Output: .claude-audit/
```

### Standardized Scanner Output Schema

All scanners in Phase 1 MUST produce output conforming to this schema:

```json
{
  "scanner_id": "frontend-components",
  "domain": "frontend/components/",
  "batch_id": "batch-07",
  "files_assigned": 42,
  "files_examined": 42,
  "files": [{
    "path": "frontend/components/Button.tsx",
    "risk_tier": 2,
    "classification": {
      "primary": "KEEP",
      "qualifier": "verified",
      "confidence": 0.92
    },
    "evidence": {
      "import_references": ["frontend/app/wizard/components/ui/WizardButton.tsx:3"],
      "grep_command": "grep -r 'Button' --include='*.tsx' -l",
      "grep_result_count": 14,
      "last_commit_days": 7
    },
    "external_dependencies": ["frontend/hooks/useTheme.ts"],
    "export_targets": ["frontend/components/index.ts"]
  }]
}
```

**Requirement**: Scanners that produce output not conforming to this schema trigger a validation error. The orchestrator retries the batch once, then marks it as FAILED in the coverage manifest.

### Dependency Chain

```
Phase 0 (Profile) → Phase 1 (Surface Scan) → Phase 2 (Structural) → Phase 3 (Cross-Ref) → Phase 4 (Consolidation)
```

Each phase depends on the prior phase's output. No phase can start until the prior phase completes and writes its checkpoint.

---

## 4. Unified Classification System

### File Risk Tiers

Files are classified into 4 risk tiers during Phase 0. Tier determines coverage requirement, evidence depth, and read depth.

| Tier | File Types | Coverage Req | Evidence Req | Read Depth |
|------|-----------|-------------|-------------|------------|
| **1 (Critical)** | Deploy scripts, CI/CD, migrations, .env*, security configs | 100% | Full 3-field (references + recency + test coverage) | Full file |
| **2 (High)** | Source code, API routes, DB models, Docker/compose configs | 95% | 2-field (references + one of: recency OR tests) | 100 lines + signal-triggered full |
| **3 (Standard)** | Tests, utilities, build scripts, documentation | 80% | Relational (annotated with what they serve) | 50 lines |
| **4 (Low)** | Assets, generated files, vendor code, binaries | 60% | Pattern-match (exists + extension + path) | Metadata only |

**Tier assignment rules** (loaded from `audit.config.yaml` or auto-generated defaults):

```yaml
# Auto-generated if absent; user can customize
risk_tiers:
  critical:
    path_patterns:
      - "**/deploy*.sh"
      - "**/.github/workflows/*.yml"
      - "**/migrations/*.sql"
      - "**/.env*"
      - "**/Dockerfile*"
    checks: [references, commit_recency, test_coverage, secret_patterns, destructive_ops]
  high:
    path_patterns:
      - "**/*.py"
      - "**/*.ts"
      - "**/*.tsx"
      - "**/docker-compose*.yml"
      - "**/api/**"
    checks: [references, commit_recency_or_tests]
  standard:
    path_patterns:
      - "**/tests/**"
      - "**/scripts/**"
      - "**/*.md"
    checks: [relational_annotation]
  low:
    path_patterns:
      - "**/assets/**"
      - "**/public/**/*.{png,jpg,svg,webm,mp4}"
      - "**/generated/**"
      - "**/vendor/**"
    checks: [pattern_match]
```

### Classification Categories (Two-Tier)

**Primary Action** (what to do):
- `DELETE` — Remove the file
- `KEEP` — No action needed
- `MODIFY` — Keep but change something
- `INVESTIGATE` — Insufficient evidence for classification; requires human review

**Secondary Qualifier** (specifics):

| Primary | Qualifier | Meaning |
|---------|-----------|---------|
| DELETE | `standard` | Safe to delete, zero references confirmed |
| DELETE | `archive-first` | Delete but preserve in archive (historically valuable) |
| KEEP | `verified` | Evidence confirms active use (Tier 1-2 evidence) |
| KEEP | `unverified` | No evidence checked (Tier 3-4 pattern match only) |
| KEEP | `monitor` | Active but shows warning signals (stale, low usage) |
| MODIFY | `consolidate-with:[target]` | Merge with another file |
| MODIFY | `fix-references` | Has broken references that need repair |
| MODIFY | `update-content` | Content is outdated or incorrect |
| MODIFY | `move-to:[destination]` | Should be relocated |
| MODIFY | `flag:[issue]` | Has specific issue needing attention |
| INVESTIGATE | `cross-boundary` | Referenced across domain boundaries, unclear ownership |
| INVESTIGATE | `insufficient-evidence` | Evidence gathering failed or was inconclusive |
| INVESTIGATE | `dynamic-import` | May be loaded via dynamic import/require patterns |

**Backward Compatibility**: The v1 categories map as follows:
- v1 `DELETE` → v2 `DELETE:standard`
- v1 `CONSOLIDATE` → v2 `MODIFY:consolidate-with:[target]`
- v1 `MOVE` → v2 `MODIFY:move-to:[destination]`
- v1 `FLAG` → v2 `MODIFY:flag:[issue]`
- v1 `KEEP` → v2 `KEEP:verified` or `KEEP:unverified` (depending on evidence)
- v1 `REVIEW` → v2 `INVESTIGATE:insufficient-evidence`

---

## 5. Phase Specifications

### Phase 0: Profile & Plan

**Agent**: audit-profiler (Haiku)
**Duration**: 30-60 seconds
**Budget**: 5% of total (5-10K tokens)

**Inputs**: Repository root path, `audit.config.yaml` (if exists)

**Process**:
1. Run `git ls-files | wc -l` to count tracked files
2. Detect domains by scanning top-level and second-level directories
3. Classify each domain: infrastructure, source, assets, docs, tests, config
4. Assign risk tiers to all files based on path patterns
5. Generate batch manifest: group files by domain, assign to scanner batches
6. If `audit.config.yaml` absent, auto-generate with detected defaults:
   - Detect framework from `package.json`, `requirements.txt`, `Cargo.toml`
   - Detect ports from `docker-compose*.yml`, `Dockerfile`
   - Detect CI/CD from `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`

**Outputs**:
- `.claude-audit/phase0/scan-profile.json` — domain detection results
- `.claude-audit/phase0/file-manifest.json` — every file with tier assignment
- `.claude-audit/phase0/batch-manifest.json` — scanner batch assignments
- `.claude-audit/audit.config.yaml` — auto-generated config (if absent; placed in audit output dir, not repo root)

**Quality Gate**: Manifest must account for 100% of `git ls-files` output. Any file not assigned to a batch triggers a warning.

### Phase 1: Surface Scan

**Agent**: audit-scanner (Haiku, parallel instances)
**Duration**: 3-8 minutes (depends on file count and batch parallelism)
**Budget**: 25% of total (60-100K tokens)

**Inputs**: batch-manifest.json from Phase 0

**Process per batch**:
1. Read batch assignment from manifest
2. For each file in batch:
   - Read file according to tier read-depth rules
   - Classify as DELETE/KEEP/MODIFY/INVESTIGATE
   - For DELETE: require `grep -r` proof of zero references
   - For KEEP (Tier 1-2): require at minimum import reference count
   - For KEEP (Tier 3-4): pattern-match classification
   - For credential files (`.env*`): read actual content, detect real vs template credentials
3. Produce structured JSON output per scanner output schema
4. Write batch report to disk

**Credential Scanning Rules**:
- Enumerate: `.env.production` → `.env.prod` → `.env` → `.env.local` → `.env.staging` → `.env.test`
- Skip templates: `.env.example`, `.env.template`, `.env.sample`
- Real credential patterns: `sk-*`, `ghp_*`, `AKIA*`, base64 >40 chars, `BEGIN RSA PRIVATE KEY`
- Template patterns: `CHANGE_ME_*`, `YOUR_*_HERE`, `<placeholder>`, `xxx`, `TODO`
- **NEVER print credential values** — only confirm presence/absence
- Include disclaimer: "This is not a security audit. Use truffleHog/detect-secrets for comprehensive scanning."

**Gitignore Consistency Check**:
- Compare `git ls-files` output against `.gitignore` patterns
- Flag files that are tracked despite being in `.gitignore`
- Output as `MODIFY:flag:gitignore-inconsistency`

**Outputs per batch**:
- `.claude-audit/phase1/batch-{NN}-{domain}.json` — structured scanner output
- `.claude-audit/phase1/pass1-summary.json` — consolidated pass 1 results

**Checkpointing**: After each batch completes, update `progress.json`:
```json
{
  "current_phase": 1,
  "batches_completed": 4,
  "batches_total": 12,
  "files_examined": 240,
  "files_total": 5857,
  "token_usage": 45000,
  "token_budget": 300000,
  "timestamp": "2026-02-20T14:30:00Z"
}
```

### Phase 2: Structural Audit

**Agent**: audit-analyzer (Sonnet, parallel instances)
**Duration**: 5-12 minutes
**Budget**: 35% of total (90-150K tokens)

**Inputs**: pass1-summary.json, file-manifest.json

**Process**:
1. Collect all DELETE, INVESTIGATE, and MODIFY candidates from Phase 1
2. Collect all Tier 1-2 KEEP files for evidence verification
3. For each candidate, produce mandatory 8-field profile:

```
1. file_path: Absolute path
2. classification: Primary:Qualifier
3. size_bytes: File size
4. evidence: {
     import_references: [list of files that import/reference this file],
     grep_command: exact grep command used,
     grep_result_count: number of references found,
     last_commit_date: ISO date,
     last_commit_author: string,
     test_coverage: "covered" | "uncovered" | "unknown",
     dynamic_import_check: "none_found" | "possible_dynamic:[pattern]"
   }
5. risk_tier: 1-4
6. rationale: 2-3 sentence explanation
7. confidence: 0.0-1.0
8. related_files: [files that should be considered together]
```

**File-Type-Specific Rules** (applied per tier config):

| File Type | Additional Checks |
|-----------|------------------|
| Test files | pytest patterns, skip markers, `input()` calls, duplicate helpers |
| Deploy scripts | Port validation against network spec, destructive ops (`DROP`, `rm -rf`) |
| Docker/Compose | Service definition comparison, Dockerfile references, volume paths |
| Documentation | Check 3 claims against codebase (for Tier 1-2 docs only) |
| Config/Env | Real vs template detection, cross-config comparison |

**Signal-Triggered Depth Escalation**:
Default read: 50 lines. Triggers for full-file read:
- Credential-adjacent imports (`dotenv`, `config`, `secrets`)
- `TODO`/`FIXME`/`HACK` in first 50 lines
- Complex conditional logic (>3 nested conditions)
- `eval`, `exec`, `dangerouslySetInnerHTML`
- File size > 300 lines

**Outputs**:
- `.claude-audit/phase2/profiles-batch-{NN}.json` — 8-field profiles
- `.claude-audit/phase2/pass2-summary.json` — consolidated profiles

### Phase 3: Cross-Reference Synthesis

**Agent**: audit-comparator (Sonnet)
**Duration**: 3-6 minutes
**Budget**: 20% of total (40-60K tokens)

**Inputs**: All Phase 1 batch outputs (with `external_dependencies` and `export_targets` fields), Phase 2 profiles

**Process**:
1. Build directed dependency graph:
   - Nodes: all files in scope
   - Edges: import/export relationships from scanner output
2. Identify orphan nodes (no incoming edges) — cross-boundary dead code candidates
3. Apply confidence scoring:
   - >3 hops from entry points → `INVESTIGATE:cross-boundary` (not DELETE)
   - 1-3 hops → `MODIFY:flag:low-connectivity`
   - 0 incoming edges AND no dynamic import patterns → `DELETE:standard` candidate
4. Build duplication matrices:
   - Group files by similarity (content hash, function overlap)
   - Calculate overlap percentages for each group
   - Recommend consolidation for >70% overlap
5. Resolve INVESTIGATE classifications:
   - Cross-reference Phase 1 INVESTIGATE items with graph data
   - Upgrade to DELETE/KEEP/MODIFY where evidence is now sufficient
   - Leave as INVESTIGATE:insufficient-evidence where still unclear
6. Post-hoc deduplication:
   - Group findings by file path
   - Cluster within-file findings by issue category
   - Keep highest-severity instance of duplicates
   - Mark cross-pass-confirmed findings as "high confidence"

**Dynamic Import Detection**:
Scan for patterns: `import(`, `require(`, `React.lazy`, `next/dynamic`, `importlib.import_module`
Files referenced only via dynamic import → `KEEP:monitor` (not DELETE)

**Outputs**:
- `.claude-audit/phase3/dependency-graph.json`
- `.claude-audit/phase3/duplication-matrix.json`
- `.claude-audit/phase3/pass3-summary.json`

### Phase 4: Consolidation & Validation

**Agent**: audit-consolidator (Sonnet) + audit-validator (Sonnet)
**Duration**: 3-5 minutes
**Budget**: 15% of total (30-50K tokens)

**Consolidation Process**:
1. Merge all pass summaries into unified findings list
2. Deduplicate across passes (keep highest-severity)
3. Sort by: primary classification → risk tier → confidence
4. Generate coverage report per tier
5. Generate executive summary with top 3-5 critical issues
6. Write FINAL-REPORT.md at configured report depth

**Validation Process** (10% spot-check):
1. Random sample 10% of all classifications (stratified by tier)
2. For each sampled file:
   - Re-run evidence gathering independently
   - Compare classification with original
   - If disagreement: flag as "disputed" with both classifications
3. Calculate agreement rate
4. If agreement rate < 85%: add warning to report header

**Coverage Report Format**:
```json
{
  "total_files": 5857,
  "files_examined": 5200,
  "overall_coverage": "88.8%",
  "per_tier": {
    "tier_1_critical": { "total": 45, "examined": 45, "coverage": "100%", "target": "100%", "status": "PASS" },
    "tier_2_high": { "total": 1200, "examined": 1150, "coverage": "95.8%", "target": "95%", "status": "PASS" },
    "tier_3_standard": { "total": 2100, "examined": 1700, "coverage": "81.0%", "target": "80%", "status": "PASS" },
    "tier_4_low": { "total": 2512, "examined": 1505, "coverage": "59.9%", "target": "60%", "status": "WARN" }
  },
  "unexamined_files": {
    "count": 657,
    "classification": "INVESTIGATE:insufficient-evidence",
    "reason": "Budget exhausted before examination"
  }
}
```

**Outputs**:
- `.claude-audit/FINAL-REPORT.md` — human-readable report
- `.claude-audit/coverage-report.json` — coverage metrics
- `.claude-audit/validation-results.json` — spot-check results
- `.claude-audit/progress.json` — final checkpoint state

---

## 6. Budget & Resource Controls

### Token Budget System

**CLI Flag**: `--budget <tokens>` (default: 300000)

**Allocation Strategy**:

| Phase | Allocation | Hard Ceiling |
|-------|-----------|-------------|
| Phase 0 | 5% | 15K tokens |
| Phase 1 | 25% | 75K tokens |
| Phase 2 | 35% | 105K tokens |
| Phase 3 | 20% | 60K tokens |
| Phase 4 | 15% | 45K tokens |

**Budget Enforcement**:
1. Orchestrator monitors cumulative token usage after each batch/operation
2. When a phase reaches 90% of its allocation: switch to abbreviated mode (skip Tier 4 files, reduce read depth)
3. When a phase reaches 100% of its allocation: complete current batch, then stop phase
4. Unexamined files auto-classified as `INVESTIGATE:insufficient-evidence`
5. Budget overrun reported in coverage report with clear explanation

**Graceful Degradation** (when budget is tight):
1. First cut: Skip Tier 4 (Low) files entirely — report as "unexamined"
2. Second cut: Reduce Tier 3 (Standard) evidence to pattern-match only
3. Third cut: Skip Phase 3 cross-reference synthesis — report "cross-references not generated"
4. Fourth cut: Reduce Phase 2 to DELETE/INVESTIGATE candidates only (skip KEEP verification)
5. **Never cut**: Phase 0 profiling, Phase 1 Tier 1-2 scanning, Phase 4 consolidation

### Realistic Token Estimates

For a repository of ~6,000 tracked files:

| Scenario | Budget | Coverage | Runtime |
|----------|--------|----------|---------|
| **Minimal** | 100K tokens | Tier 1-2 only (~1,200 files) | ~8 min |
| **Standard** | 300K tokens | Tier 1-3 (~3,300 files) | ~18 min |
| **Comprehensive** | 500K tokens | All tiers (~5,800 files) | ~30 min |
| **Deep** | 800K tokens | All tiers + full evidence | ~45 min |

---

## 7. CLI Interface

### Updated Command Signature

```
/sc:cleanup-audit [target-path] [flags]
```

### Flags

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--pass` | `surface\|structural\|cross-cutting\|all` | `all` | Which pass to run |
| `--batch-size` | Integer | Auto (based on profile) | Files per scanner batch |
| `--focus` | `infrastructure\|frontend\|backend\|docs\|all` | `all` | Domain filter |
| `--budget` | Integer (tokens) | `300000` | Hard token ceiling |
| `--report-depth` | `summary\|standard\|detailed` | `standard` | Report verbosity |
| `--tier` | `1\|2\|3\|4\|all` | `all` | Minimum risk tier to examine |
| `--resume` | (no value) | — | Resume from last checkpoint |
| `--config` | File path | `audit.config.yaml` | Custom config file |
| `--pass-docs` | (no value) | — | Include documentation audit (opt-in) |

### Report Depth Levels

| Level | Content |
|-------|---------|
| **summary** | Executive summary, top 5 issues, coverage percentages, action counts. ~50 lines. |
| **standard** | Summary + per-category file lists with evidence snippets + duplication matrix + coverage per tier. ~200-400 lines. |
| **detailed** | Standard + full 8-field profiles for all examined files + dependency graph visualization + validation results. ~500-2000 lines. |

---

## 8. Output Specification

### Directory Structure

```
.claude-audit/
├── audit.config.yaml           # Auto-generated or user config (if generated)
├── progress.json               # Checkpoint state (updated after each batch)
├── FINAL-REPORT.md             # Human-readable consolidated report
├── coverage-report.json        # Coverage metrics per tier
├── validation-results.json     # Spot-check validation results
├── phase0/
│   ├── scan-profile.json       # Domain detection
│   ├── file-manifest.json      # Every file with tier assignment
│   └── batch-manifest.json     # Scanner batch assignments
├── phase1/
│   ├── batch-01-infrastructure.json
│   ├── batch-02-frontend-source.json
│   ├── batch-NN-*.json
│   └── pass1-summary.json
├── phase2/
│   ├── profiles-batch-01.json
│   ├── profiles-batch-NN.json
│   └── pass2-summary.json
├── phase3/
│   ├── dependency-graph.json
│   ├── duplication-matrix.json
│   └── pass3-summary.json
└── phase4/
    ├── consolidation-log.json
    └── known-issues.json       # Deduplicated issue registry
```

### FINAL-REPORT.md Structure

```markdown
# Repository Cleanup Audit — Final Report

## Audit Metadata
- Date, branch, commit, file count, budget used/total, runtime

## Coverage Summary
- Per-tier coverage table with PASS/WARN/FAIL status

## Validation Summary
- Spot-check agreement rate, disputed classifications count

## Executive Summary
- Top 3-5 critical issues
- Action counts: N DELETE, N KEEP (M unverified), N MODIFY, N INVESTIGATE

## Critical Issues (INVESTIGATE items)
- Files requiring human decision with evidence summary

## DELETE Recommendations
- Grouped by domain, each with evidence and confidence

## MODIFY Recommendations
- Grouped by qualifier (consolidate, fix-references, move, flag)

## KEEP Summary
- Verified vs unverified counts
- Monitor items (low-confidence KEEP)

## Duplication Matrix
- Top N duplication groups with overlap percentages

## Unexamined Files
- List of files not examined with reason (budget, exclusion, error)

## Appendix: Verification Commands
- Reproducible bash commands to verify key claims
```

---

## 9. Quality Gates

### Per-Phase Quality Gates

| Gate | Phase | Criteria | On Failure |
|------|-------|----------|------------|
| **Manifest Completeness** | 0→1 | 100% of git-tracked files assigned to batches | Block Phase 1 |
| **Scanner Schema Compliance** | 1 | All batch outputs conform to scanner output schema | Retry batch once, then mark FAILED |
| **Evidence Sufficiency** | 1→2 | DELETE candidates have grep proof | Block promotion to Phase 2 |
| **Profile Completeness** | 2→3 | All 8 fields populated for profiled files | Warn in report, continue |
| **Coverage Threshold** | 2→3 | Tier 1 ≥ 100%, Tier 2 ≥ 90% | Warn if below, never block |
| **Cross-Ref Graph Valid** | 3→4 | Dependency graph has no orphan batches | Warn in report, continue |
| **Spot-Check Agreement** | 4 | ≥ 85% agreement rate | Add warning banner to report |

### Anti-Lazy Enforcement

Scanners are validated by structured output, not tool-call counts:

1. **Required output fields**: Every file must have `classification`, `evidence`, `confidence`
2. **Evidence non-emptiness**: DELETE must have `grep_command` + `grep_result_count`; Tier 1-2 KEEP must have `import_references`
3. **Confidence distribution**: If >90% of files in a batch have identical confidence values, flag batch for re-review
4. **Cross-batch consistency**: If two scanners classify the same file differently, trigger targeted re-review

---

## 10. Cold-Start & Configuration

### First-Run Experience

When `audit.config.yaml` is absent:

1. Phase 0 profiler auto-generates a default config based on:
   - Framework detection: `package.json` → Node.js patterns; `requirements.txt` → Python patterns
   - Port detection: scan `docker-compose*.yml` for port mappings
   - CI/CD detection: check `.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`
2. Generated config is written to `.claude-audit/audit.config.yaml` (NOT repo root)
3. Report header notes: "Auto-generated config used. Customize at .claude-audit/audit.config.yaml for future runs."
4. **Never fail on missing config** — always generate sensible defaults

### Calibration Files (Deferred to Phase 5)

Anti-lazy calibration via known-good/known-bad files is deferred because:
- No known-good/bad files exist on cold-start
- Synthetic calibration adds complexity with uncertain benefit
- Better approach: use v2 first-run results as calibration baseline for second run

---

## 11. Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Token budget overrun | HIGH | `--budget` flag with proportional allocation and graceful degradation |
| Config cold-start failure | HIGH | Auto-generate defaults from project structure detection |
| Dynamic import false positives | HIGH | Dynamic import pattern detection: `import(`, `require(`, `React.lazy`, `next/dynamic` |
| LLM output schema non-compliance | MEDIUM | Schema validation post-processing; retry once on malformed output |
| Report overwhelming | MEDIUM | `--report-depth` flag with 3 levels (summary/standard/detailed) |
| Manifest size scaling (50K+ files) | MEDIUM | Switch to per-directory coverage tracking above 10,000 files |
| Spec-implementation gap recurrence | CRITICAL | Every spec promise has a corresponding acceptance test (see Section 12) |
| Credential value exposure | CRITICAL | Scanner prompts explicitly prohibit printing credential values |

---

## 12. Implementation Roadmap

### Phase 0: Enforce Existing Spec (Priority: CRITICAL)

Implement all v1 spec promises:
1. 5-category classification (via two-tier system backward compatibility)
2. Coverage tracking with per-tier reporting
3. Checkpointing via `progress.json` after each batch
4. Evidence-gated classification (grep proof for DELETE, import proof for Tier 1-2 KEEP)
5. 10% spot-check validation pass

**Estimated effort**: 4-6 hours
**Dependencies**: None

### Phase 1: Correctness Fixes

1. Credential file scanning (read actual .env content)
2. Gitignore consistency check
3. Standardized scanner output schema

**Estimated effort**: 2-3 hours
**Dependencies**: Phase 0

### Phase 2: Infrastructure

1. Repository profiling (Phase 0 audit-profiler agent)
2. Dynamic batch decomposition with domain-aware assignments
3. Coverage manifest with tier tracking
4. Unified classification system (two-tier)

**Estimated effort**: 6-8 hours
**Dependencies**: Phase 1

### Phase 3: Depth Improvements

1. Evidence-mandatory KEEP for Tier 1-2 files
2. Cross-reference synthesis (dependency graph)
3. File-type-specific verification rules
4. Signal-triggered depth escalation
5. Budget controls with graceful degradation

**Estimated effort**: 8-12 hours
**Dependencies**: Phase 2

### Phase 4: Quality & Polish

1. Post-hoc deduplication in consolidator
2. Report depth control (`--report-depth`)
3. Resume from checkpoint (`--resume`)
4. Known-issue registry for cross-pass dedup

**Estimated effort**: 4-6 hours
**Dependencies**: Phase 3

### Phase 5: Extensions (Future)

1. Documentation audit pass (`--pass-docs`)
2. Anti-lazy calibration files (using prior run as baseline)
3. Model assignment by domain (Haiku for mechanical, Sonnet for semantic)

**Estimated effort**: 6-10 hours
**Dependencies**: Phase 4, at least one prior audit run for calibration

---

## 13. Acceptance Criteria

Every requirement has a testable acceptance criterion:

| Requirement | Acceptance Test |
|-------------|----------------|
| 5-category classification | FINAL-REPORT.md contains at least 2 of: DELETE, KEEP, MODIFY, INVESTIGATE |
| Coverage tracking | coverage-report.json exists with per-tier percentages |
| Checkpointing | progress.json updated after every batch; `--resume` recovers from interrupted state |
| Evidence for DELETE | Every DELETE entry has non-empty `grep_command` and `grep_result_count: 0` |
| Evidence for Tier 1-2 KEEP | Every Tier 1-2 KEEP has non-empty `import_references` |
| Spot-check validation | validation-results.json exists with ≥10% sample size |
| Credential scanning | `.env.production` correctly identified as template vs real credentials |
| Gitignore check | Files tracked despite .gitignore rules are flagged |
| Budget control | Audit completes within `--budget` ± 10% without crashing |
| Report depth | `--report-depth summary` produces <100 lines; `detailed` includes 8-field profiles |
| Scanner schema | All Phase 1 batch outputs validate against scanner output schema |
| Cross-reference | Phase 3 produces dependency-graph.json with node count > 0 |
| Cold-start | Audit succeeds on first run without pre-existing config |

---

## 14. Expert Panel Consensus

### Karl Wiegers (Requirements)
"The PRD addresses the critical spec-implementation gap I identified. Every v1 promise now has a testable acceptance criterion. The tiered evidence requirements are properly measurable. I recommend adding user journey tests: cold-start → first audit → second audit with config customization."

### Martin Fowler (Architecture)
"The dependency chain is now correct — Phase 0 profiling enables Phase 1 domain-aware scanning, which produces structured output for Phase 3 cross-reference synthesis. The standardized scanner output schema is the key architectural decision that makes everything else possible. The two-tier classification system cleanly maps the v1 categories while adding the INVESTIGATE escape hatch."

### Michael Nygard (Production Systems)
"The budget system with graceful degradation is the right pattern. Token costs are realistically estimated at 2-3x the original proposals. The cold-start handling (auto-generate config, never fail) follows the principle of least surprise. I'd add one thing: a `--dry-run` flag that runs Phase 0 only and reports estimated budget requirements."

### Lisa Crispin (Quality)
"The quality gates between phases prevent cascading failures. The anti-lazy enforcement through structured output (not tool-call counts) is the right approach. The 10% spot-check with 85% agreement threshold provides a meaningful quality signal. The coverage manifest is the foundation — without it, we can't trust anything else."

### Consensus Additions
Based on panel discussion, one addition recommended:

**`--dry-run` flag**: Runs Phase 0 only. Reports:
- Detected domains and file counts
- Estimated token budget per phase
- Generated batch manifest (without executing scans)
- Auto-generated config preview

This gives users visibility into audit scope before committing resources.

---

*PRD designed by expert panel simulation | 2026-02-20*
*Input: 15 findings, 12 proposals, 5-dimension validation (5.6/10 → addressed all 8 corrections)*
