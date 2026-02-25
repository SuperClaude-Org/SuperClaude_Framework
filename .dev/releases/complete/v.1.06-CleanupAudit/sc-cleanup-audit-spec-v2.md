# `/sc:cleanup-audit` — Refactored Specification v2.0

**Version**: 2.0
**Generated**: 2026-02-19
**Derived from**: sc-repo-audit-command-spec-merged.md (v1.1)
**Architecture**: SuperClaude Skill + Custom Subagents (Hybrid)
**Research Basis**: Agent 1 (40 structural rules), Agent 2 (22 ranked capabilities), Custom Command Guide

---

## 1. Architecture Overview

### Implementation Type: Skill + Custom Subagents

Based on research findings, this command is implemented as a **skill** (not a single command file) with **custom subagent definitions** for worker agents:

```
.claude/skills/sc-cleanup-audit/          # Orchestrator (skill)
├── SKILL.md                              # Main orchestration (<500 lines)
├── rules/
│   ├── pass1-surface-scan.md            # Pass 1 criteria and methodology
│   ├── pass2-structural-audit.md        # Pass 2 per-file profiling rules
│   ├── pass3-cross-cutting.md           # Pass 3 comparison methodology
│   ├── verification-protocol.md         # Universal evidence requirements
│   └── dynamic-use-checklist.md         # Dynamic loading patterns to check
├── templates/
│   ├── batch-report.md                  # Per-agent batch output template
│   ├── pass-summary.md                  # Per-pass consolidated summary
│   ├── final-report.md                  # Final consolidated report
│   └── finding-profile.md              # Per-file finding profile
└── scripts/
    └── repo-inventory.sh               # File enumeration and batching

.claude/agents/                           # Worker agents (subagents)
├── audit-scanner.md                     # Pass 1 (Haiku, read-only, fast)
├── audit-analyzer.md                    # Pass 2 (Sonnet, read-only, deep)
├── audit-comparator.md                  # Pass 3 (Sonnet, read-only, cross-cutting)
├── audit-consolidator.md               # Report merger (Sonnet, Write-enabled)
└── audit-validator.md                   # Spot-check validator (Sonnet, read-only)
```

**Rationale**:
- Skill enables supporting files (rules, templates, scripts) — essential for separation of concerns
- Progressive disclosure: only description in startup context, full content loads on invocation
- `disable-model-invocation: true` prevents auto-triggering of this resource-intensive command
- Custom subagents enable per-pass model selection, tool restriction, and behavioral specialization
- Hybrid approach: skill orchestrates, subagents execute (subagents cannot spawn sub-subagents)

---

## 2. SKILL.md Specification

### 2.1 Frontmatter

```yaml
---
name: cleanup-audit
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"
---
```

**Field Rationale**:
| Field | Value | Why |
|-------|-------|-----|
| `category` | `utility` | Read-only analysis, does not modify code |
| `complexity` | `high` | Full MCP, multi-persona, Task delegation, wave-eligible |
| `disable-model-invocation` | `true` | Resource-intensive; user-invoked only |
| `allowed-tools` | Restricted set | Read-only tools + controlled Bash + Write (reports only) + orchestration |
| `mcp-servers` | Sequential, Serena, Context7 | Analysis depth, import chains, framework validation |
| `personas` | 5 specialists | Domain coverage across infrastructure, code, tests, docs, duplication |

### 2.2 Title and Triggers

```markdown
# /sc:cleanup-audit - Multi-Pass Repository Audit

## Triggers
- Repository maintenance or cleanup planning before major releases
- Technical debt assessment or dead code identification needs
- Post-migration or post-refactor validation of repository state
- CI/CD pipeline audit or infrastructure configuration review
- Cross-cutting duplication analysis for monorepo consolidation
```

### 2.3 Usage

```markdown
## Usage
```
/sc:cleanup-audit [target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]
```

**Arguments**:
- `target-path`: Directory to audit (default: `.` for entire repo)
- `--pass`: Which audit pass to run (default: `all`)
  - `surface`: Pass 1 — quick junk detection with DELETE/REVIEW/KEEP
  - `structural`: Pass 2 — deep per-file profiling with mandatory evidence
  - `cross-cutting`: Pass 3 — duplication, sprawl, and consolidation analysis
  - `all`: Run all 3 passes sequentially with quality gates between
- `--batch-size`: Files per agent batch (default: 50 for surface, 25 for structural/cross-cutting)
- `--focus`: Domain focus for cross-cutting pass (default: `all`)
```

### 2.4 Behavioral Flow

```markdown
## Behavioral Flow

1. **Discover**: Enumerate repository contents via shell preprocessing and Glob.
   Calculate file inventory, type distribution, and scope metrics using `repo-inventory.sh`.
   Create batch plan with domain-based grouping and priority ordering.
   Load previous pass results if running a subsequent pass.

2. **Configure**: Select pass type from $ARGUMENTS (surface|structural|cross-cutting|all).
   Load pass-specific rules from `rules/` supporting files.
   Create TodoWrite tasks for each batch and quality gate.
   Initialize output directory (`.claude-audit/${CLAUDE_SESSION_ID}/`) and progress checkpoint file.

3. **Orchestrate**: Spawn parallel audit subagents per batch via Task tool.
   Pass 1 uses `audit-scanner` (Haiku, batches of 50).
   Pass 2 uses `audit-analyzer` (Sonnet, batches of 25).
   Pass 3 uses `audit-comparator` (Sonnet, batches of 25-50 by file type).
   Agents write results to disk incrementally after each sub-batch.
   Run in waves of 7-8 concurrent agents. Update TodoWrite between waves.

4. **Validate**: After all batches for a pass complete, spawn `audit-validator` to spot-check
   10% of findings (5 per 50 files). Verify evidence quality: grep proof for DELETE,
   reference citations for KEEP, overlap quantification for CONSOLIDATE.
   Quality gate: all batch reports present + required sections complete + coverage threshold met.
   For cross-cutting pass, verify duplication matrix completeness.

5. **Report**: Spawn `audit-consolidator` to merge batch reports into pass summary using
   `templates/pass-summary.md`. If --pass all, consolidate all summaries into final report
   using `templates/final-report.md` with ultrathink depth for cross-cutting pattern synthesis.
   Produce executive summary with action priority, cross-cutting findings, and discovered issues registry.
   Output to `.claude-audit/${CLAUDE_SESSION_ID}/`.

Key behaviors:
- Read-only operation enforced at platform level via `allowed-tools` and subagent `tools` restrictions
- Haiku-first escalation: Pass 1 uses fast/cheap model, only flagged files get Sonnet-depth analysis
- Incremental disk saves after every sub-batch prevent context-window data loss
- File-based coordination: subagents write to disk, orchestrator reads and synthesizes
- Conservative bias: when uncertain, FLAG rather than DELETE; zero-reference proof required for DELETE
```

### 2.5 MCP Integration

```markdown
## MCP Integration

- **Sequential MCP**: Auto-activated for cross-cutting pattern synthesis in Pass 3 and final report generation.
  Provides structured multi-step reasoning for identifying systemic patterns across batch results.
- **Serena MCP**: Auto-activated during orchestrator's discovery phase for semantic understanding of
  import chains and symbol relationships beyond string-based grep.
- **Context7 MCP**: Auto-activated for framework-specific configuration validation.
  Verifies flagged configurations against current framework conventions and best practices.
- **Persona Coordination**: analyzer (primary, all passes) + architect (infrastructure batches) +
  devops (CI/deploy batches) + qa (test file batches) + refactorer (duplication findings in Pass 3).

**MCP Constraint**: MCP tools are available to the orchestrator (SKILL.md) ONLY, not to background
subagents. All MCP-dependent analysis occurs in Step 1 (Discover) and Step 5 (Report).
```

### 2.6 Tool Coordination

```markdown
## Tool Coordination

- **Read/Grep/Glob**: Core audit tools available to all subagents. Read file contents for analysis,
  Grep for reference tracing across repo, Glob for file enumeration and batch creation.
- **Bash(git/wc/find/du)**: Controlled shell access for orchestrator only. Repository metadata
  collection (git ls-files, git log), metrics (wc, du), inventory (find). No destructive commands.
- **Write**: Report generation. Batch reports, pass summaries, final consolidated report.
  Audit consolidator writes to `.claude-audit/` directory exclusively.
- **TodoWrite**: Progress tracking. Each batch is a tracked task (pending → in_progress → completed).
  Quality gates tracked as blocked tasks until prerequisites complete. Coverage metrics updated in real-time.
- **Task**: Sub-agent delegation for parallel batch processing. Spawns custom audit subagents:
  audit-scanner (Pass 1), audit-analyzer (Pass 2), audit-comparator (Pass 3),
  audit-consolidator (merging), audit-validator (spot-checking).
```

### 2.7 Key Patterns

```markdown
## Key Patterns

- **Haiku-First Escalation**: All files → Haiku surface scan → flagged subset → Sonnet deep analysis → 50-70% cost reduction vs scanning everything with Sonnet
- **Evidence-Gated Classification**: File → grep for references → check dynamic loading patterns → classify with proof → every recommendation has verifiable evidence chain
- **Incremental Checkpoint**: Batch completes → write results to disk → update progress.json → resume-safe at any interruption point
- **Fan-Out/Fan-In Orchestration**: File inventory → domain batches → parallel agents (waves of 7-8) → collect disk results → merge and deduplicate → cross-cutting synthesis
- **Conservative Escalation**: DELETE only with zero-reference proof + dynamic-use check → FLAG when uncertain → KEEP when any reference found → safety always wins
```

### 2.8 Examples

```markdown
## Examples

### Full Repository Surface Scan
```
/sc:cleanup-audit .
# Runs Pass 1 on entire repository
# Spawns Haiku agents in batches of 50 files
# Produces DELETE/REVIEW/KEEP classification for every file
# Output: .claude-audit/<session>/pass1-summary.md
```

### Structural Audit of Source Directory
```
/sc:cleanup-audit src/ --pass structural --batch-size 25
# Runs Pass 2 on src/ directory only
# Deep per-file profiling with 8 mandatory evidence fields
# Checks imports, CI/CD usage, supersession, risk notes
# Output: .claude-audit/<session>/pass2-summary.md
```

### Infrastructure Cross-Cutting Sweep
```
/sc:cleanup-audit . --pass cross-cutting --focus infrastructure
# Runs Pass 3 focused on Docker, CI/CD, deploy scripts, configs
# Produces mandatory duplication matrix with overlap percentages
# Groups similar files (all compose, all deploy scripts) for comparison
# Output: .claude-audit/<session>/pass3-infra-summary.md
```

### Complete 3-Pass Audit
```
/sc:cleanup-audit . --pass all --batch-size 40
# Runs all 3 passes sequentially: surface → structural → cross-cutting
# Quality gates between passes (validation + coverage check)
# Haiku (Pass 1) → Sonnet (Pass 2, flagged files only) → Sonnet (Pass 3)
# Consolidated final report with executive summary and action items
# Output: .claude-audit/<session>/final-report.md
```
```

### 2.9 Boundaries

```markdown
## Boundaries

**Will:**
- Produce evidence-backed recommendations with verifiable grep proof for every classification
- Track progress via TodoWrite and checkpoint files enabling resume from interruption
- Generate structured reports following consistent templates with mandatory per-file profiles

**Will Not:**
- Modify, delete, move, or edit any repository file (read-only operation)
- Make assumptions from filenames without reading content and tracing references
- Classify as DELETE without zero-reference grep proof and dynamic loading check

## CRITICAL BOUNDARIES

**READ-ONLY AUDIT — NO REPOSITORY MODIFICATIONS**

This command produces audit reports ONLY. It does not execute any cleanup actions.

**Explicitly Will NOT**:
- Edit, delete, move, or rename any existing file in the repository
- Execute cleanup recommendations automatically
- Modify configuration files, CI pipelines, or build scripts
- Skip evidence requirements for any classification

**Output**: Audit reports written to `.claude-audit/${CLAUDE_SESSION_ID}/` containing:
- Per-pass batch reports with per-file profiles and evidence citations
- Pass summary with findings counts, coverage metrics, and cross-agent patterns
- Consolidated final report with executive summary and prioritized action items
- Discovered issues registry with numbered systemic findings

**Next Step**: Use `/sc:cleanup` to execute safe recommendations from the audit report,
then `/sc:test` to verify no regressions, then `/sc:git` to commit cleanup changes.
```

---

## 3. Multi-Pass Architecture

### 3.1 Pass 1: Surface Scan (Junk Detection)

**Worker Agent**: `audit-scanner` (Haiku, maxTurns: 20, tools: Read/Grep/Glob)
**Batch Size**: 50 files (100 for binary/asset directories)
**Depth**: Light (5-10 min per batch)
**Coverage Target**: 100% of repo files

**Goal**: Quickly identify obvious waste — test artifacts, runtime files committed by accident, empty placeholders, unreferenced files.

**Guiding Question**: "Is this file junk?"

**Classification Taxonomy (3-tier)**:

| Category | Meaning | Action |
|----------|---------|--------|
| DELETE | No references, no value, clearly obsolete | Safe to remove |
| REVIEW | Uncertain — may be needed, needs human judgment | Escalate to human |
| KEEP | Actively referenced, part of build/runtime/CI | Leave in place |

**Verification Protocol** (per file):
1. Read first 20-30 lines to understand purpose
2. Grep for filename across repo (exclude `.git/`, `node_modules/`, build artifacts)
3. Check if imported/sourced by other files
4. Categorize with brief justification

**Rules File**: `rules/pass1-surface-scan.md` — contains full criteria, file-type-specific rules, binary asset handling, and output format.

---

### 3.2 Pass 2: Structural Audit (Organizational Integrity)

**Worker Agent**: `audit-analyzer` (Sonnet, maxTurns: 35, tools: Read/Grep/Glob)
**Batch Size**: 25 files
**Scope**: Only files marked KEEP or REVIEW from Pass 1
**Depth**: Deep (20-40 min per batch)

**Goal**: Validate placement, staleness, broken references, and structural issues. Requires per-file proof.

**Guiding Question**: "Is this file in the right place, correctly documented, and structurally sound?"

**Finding Types (diagnostic)**:

| Finding Type | Meaning |
|-------------|---------|
| MISPLACED | Valid content in wrong location |
| STALE | Outdated or no longer accurate |
| STRUCTURAL ISSUE | Internal problems requiring code changes |
| BROKEN REFS | References to non-existent paths or files |
| VERIFIED OK | Confirmed correct with evidence |

**Action Recommendations (prescriptive)**:

| Action | Meaning |
|--------|---------|
| KEEP | Verified; has evidence of active use |
| DELETE | Confirmed dead with evidence |
| MOVE | Valid but wrong location |
| FLAG | Needs code changes or human decision |

**Mandatory Per-File Profile** (all 8 fields required):

| Field | Requirement |
|-------|-------------|
| What it does | 1-2 sentence plain-English explanation |
| Nature | Classify: script / test / doc / config / source code / data / asset / migration / one-time artifact |
| References | Who/what references this file? Grep results with files + line numbers. "None found" is valid but must be stated. |
| CI/CD usage | Called by any automation? Check workflows, compose files, Makefile, package.json, Dockerfiles. |
| Superseded by / duplicates | Is there a newer/better version? Check for `_v2`, `_enhanced`, `_new` variants. |
| Risk notes | Runtime/CI/test/doc impact if removed or moved. |
| Recommendation | KEEP / MOVE / DELETE / FLAG with finding type. |
| Verification notes | Explicit list of what was checked (prevents lazy KEEP). |

**Extra Rules by File Type**:
- **Tests**: Check test runner discovery path, check patterns (pytest vs manual), verify would actually pass
- **Scripts**: Check if functionality handled by canonical script, check schema/field names are current
- **Documentation**: Verify 3-5 technical claims against actual implementation
- **Config**: Compare with similar configs, check values match current architecture

**Failure Criterion**: Reports missing mandatory per-file profiles are FAILED and must be regenerated.

**Rules File**: `rules/pass2-structural-audit.md`

---

### 3.3 Pass 3: Cross-Cutting Sweep (Sprawl, Duplication, Consolidation)

**Worker Agent**: `audit-comparator` (Sonnet, maxTurns: 35, tools: Read/Grep/Glob)
**Batch Size**: 25-50 (varies by file type density)
**Depth**: Medium-deep with comparison focus

**Goal**: Find duplication, sprawl, and broken references spanning directory boundaries — problems per-directory audits inherently miss.

**Guiding Question**: "Does this file duplicate or conflict with another file elsewhere in the repo?"

**Extended Classification Taxonomy**:

| Category | Meaning | Action |
|----------|---------|--------|
| DELETE | Confirmed dead | Remove |
| CONSOLIDATE | Merge with identified similar file | Keep canonical, merge unique parts |
| MOVE | Valid but wrong location | Relocate |
| FLAG | Needs code changes | Developer action |
| KEEP | Verified unique purpose with evidence | Leave in place |
| BROKEN REF | References non-existent paths | Fix reference |

**Per-File Profile Fields (Pass 3)**:

| Field | Requirement |
|-------|-------------|
| What it does | 1-2 sentence explanation |
| Nature | File type classification |
| References | Grep results with files + line numbers |
| Similar files | Other files serving same/overlapping purpose; quantify % overlap or key differences |
| Superseded? | Newer/better version exists? |
| Currently used? | Referenced by running app, CI/CD, build? Evidence required. |
| Recommendation | DELETE / CONSOLIDATE (with what) / MOVE / FLAG / KEEP |

**Critical Differentiators from Pass 2**:
1. **Compare, don't just catalog**: When similar files found, DIFF them and quantify overlap
2. **Group audit**: Audit similar files together (all docker-compose, all deploy scripts, all playwright configs)
3. **Mandatory duplication matrix**: Produce matrix for compose/deploy/tests/configs with overlap percentages
4. **Already-known issues list**: Pass 3 prompt includes all findings from Passes 1-2; note "Already tracked as issue #N"
5. **Auto-KEEP for previously audited source**: Don't re-audit files already deep-profiled in Pass 2
6. **Directory-level assessments**: For 50+ file directories, use strategic sampling

**Focus Areas**:
- Multiple docker-compose / Dockerfile / deploy scripts
- Config and .env file proliferation
- Root-level clutter
- Cross-directory duplication (same file type in multiple directories)
- Stale artifacts from old architecture

**Tiered P3 Depth** (for large repos):
- **Deep** (per-file profile): Root configs, infrastructure, CI/CD, deploy scripts (~200 files)
- **Medium** (directory assessment + sampling): Source code directories (~800 files)
- **Light** (reference-grep only): Assets, documentation, generated files (~400 files)

**Rules File**: `rules/pass3-cross-cutting.md`

---

## 4. Unified Classification Taxonomy

Priority-ordered across all passes:

| Priority | Category | Reversibility | Actor | Required Evidence |
|----------|----------|--------------|-------|-------------------|
| 1 | DELETE | Git recoverable | Any developer | Zero references (grep proof) + no dynamic loading + successor OR transient artifact |
| 2 | CONSOLIDATE | Git recoverable | Developer with domain knowledge | Both files read + overlap quantified + canonical chosen + migration notes |
| 3 | MOVE | Git recoverable | Any developer | Current location incorrect + target justified + refs to update listed |
| 4 | FLAG | Requires code changes | Developer with context | Issue described + action specific + verification checklist |
| 5 | KEEP | No action | N/A | At least one active reference cited + verification notes |
| 6 | BROKEN REF | Varies | Developer with context | Source file:line → missing target path |

---

## 5. Verification Protocol (Universal)

### Evidence Requirements Per Recommendation

**For DELETE**:
- [ ] Grep confirms zero active references (cite grep pattern + count + zero-result)
- [ ] File is not dynamically loaded (check patterns in `rules/dynamic-use-checklist.md`)
- [ ] No CI/CD pipeline references it
- [ ] Successor/replacement exists, OR functionality no longer needed, OR transient artifact confirmed

**For KEEP**:
- [ ] At least one active reference found (cite file + line number)
- [ ] File is in sensible location for its type
- [ ] File naming follows project conventions
- [ ] For configs: referenced by build/CI/runtime system
- [ ] For tests: in test-runner-discovered path with proper patterns

**For CONSOLIDATE**:
- [ ] Both files identified with paths
- [ ] Overlap quantified (% identical, key differences listed)
- [ ] Recommendation for which to keep and what unique parts to merge

**For FLAG**:
- [ ] Issue clearly described
- [ ] Required action specific enough to execute
- [ ] Impact scope estimated (which files/systems affected)
- [ ] Minimal verification checklist: "what evidence would settle this?"

**For MOVE**:
- [ ] Clear target location rationale
- [ ] List of references to update

### Cross-Reference Checklist

Every file audit MUST check these reference sources:
- [ ] Source code imports/requires (`grep -r "filename" --include="*.{ts,tsx,py,js,jsx}"`)
- [ ] CI/CD workflows (`.github/workflows/*.yml`)
- [ ] Docker/Compose files (`docker-compose*.yml`, `Dockerfile*`)
- [ ] Package managers (`package.json`, `requirements.txt`, `pyproject.toml`)
- [ ] Build systems (`Makefile`, `*.sh`, `*.ps1`, `Justfile`)
- [ ] Documentation (`*.md`, `docs/`)
- [ ] Kubernetes/Helm/Terraform manifests (if present)

### Dynamic-Use Checklist

Before classifying as DELETE, check for these dynamic loading patterns:
- Environment variable-based module loading (`process.env.MODULE`, `os.getenv()`)
- String-based import loaders (`importlib.import_module()`, `require(variable)`)
- Plugin registries (entry points, plugin manifests)
- Glob-based file discovery (`glob('*.config.js')`, `pathlib.Path.glob()`)
- Config-driven loading (paths in YAML/JSON/TOML config files)

**Rules File**: `rules/verification-protocol.md` + `rules/dynamic-use-checklist.md`

---

## 6. Custom Subagent Specifications

### 6.1 audit-scanner (Pass 1 Worker)

```yaml
---
name: audit-scanner
description: "Fast read-only surface scanner for repository audit Pass 1. Classifies files as DELETE/REVIEW/KEEP with grep evidence."
tools: Read, Grep, Glob
model: haiku
maxTurns: 20
permissionMode: plan
---
```

**System Prompt Content**:
- Role: Read-only file scanner performing surface-level junk detection
- Input: Batch file list + Pass 1 rules
- Methodology: Read first 20-30 lines → grep for references → classify with evidence
- Output format: Batch report following `templates/batch-report.md`
- Safety: DO NOT modify any file. Write only your output report.
- Incremental save: Write findings after every 5-10 files analyzed

### 6.2 audit-analyzer (Pass 2 Worker)

```yaml
---
name: audit-analyzer
description: "Deep structural auditor for repository audit Pass 2. Produces mandatory 8-field per-file profiles with evidence."
tools: Read, Grep, Glob
model: sonnet
maxTurns: 35
permissionMode: plan
---
```

**System Prompt Content**:
- Role: Deep structural auditor performing per-file profiling
- Input: Batch file list + Pass 2 rules + Pass 1 findings (for context)
- Methodology: Full 8-field profile per file, extra rules by file type
- Output format: Batch report with mandatory per-file profiles
- Safety: DO NOT modify any file. Reports missing mandatory fields are FAILED.
- Evidence standard: Every KEEP needs reference citation. Every DELETE needs grep proof.

### 6.3 audit-comparator (Pass 3 Worker)

```yaml
---
name: audit-comparator
description: "Cross-cutting comparator for repository audit Pass 3. Detects duplication, sprawl, and consolidation opportunities."
tools: Read, Grep, Glob
model: sonnet
maxTurns: 35
permissionMode: plan
---
```

**System Prompt Content**:
- Role: Cross-cutting duplication and sprawl detector
- Input: Batch of similar files grouped by type + Pass 1-2 findings
- Methodology: Compare files, quantify overlap %, produce duplication matrix
- Output format: Batch report with CONSOLIDATE recommendations + duplication matrix
- Already-known issues: Note "Already tracked as issue #N" and move on
- Critical rule: DIFF files and quantify overlap, don't just catalog

### 6.4 audit-consolidator (Report Merger)

```yaml
---
name: audit-consolidator
description: "Consolidates audit batch reports into pass summaries and final reports with deduplication."
tools: Read, Grep, Glob, Write
model: sonnet
maxTurns: 40
permissionMode: plan
---
```

**System Prompt Content**:
- Role: Report merger and synthesizer
- Input: All batch reports for a pass + pass summary template
- Methodology: Merge reports → deduplicate findings → extract cross-agent patterns → produce summary
- Output format: Pass summary or final report following templates
- Quality: Must include summary counts, coverage metrics, and remaining/not-audited sections

### 6.5 audit-validator (Quality Checker)

```yaml
---
name: audit-validator
description: "Spot-check validator verifying audit finding accuracy by re-testing claims independently."
tools: Read, Grep, Glob
model: sonnet
maxTurns: 25
permissionMode: plan
---
```

**System Prompt Content**:
- Role: Independent validator performing spot-check verification
- Input: Randomly sampled 5 findings per 50 files audited
- Methodology: For each sampled finding:
  1. Re-run the grep claim independently
  2. Verify the agent actually read the file (not guessed from filename)
  3. Check if KEEP recommendations are genuine (file truly referenced)
  4. Check if DELETE recommendations are safe (file truly unreferenced)
- Output: Validation report with discrepancies flagged

---

## 7. Agent Orchestration

### 7.1 Batch Strategy

**Principles**:
1. **Domain-based batching**: Group files by functional domain (infrastructure, frontend, backend), not alphabetically
2. **Size limits**: 25-50 files per agent batch; deeper passes use smaller batches
3. **Priority ordering** (5 levels):
   - P1: Cross-cutting infra / CI / deploy / compose sprawl (highest cleanup value)
   - P2: Runtime-critical config (config errors break production)
   - P3: Tests and tooling (prevent false-green CI)
   - P4: Source code
   - P5: Docs and ancillary assets (lowest risk)
4. **Binary assets**: Grep-only audits (reference checking without reading content), larger batches OK (50-100)
5. **Similar file grouping**: Batch similar files together so agents can compare directly

**Exclusions**: `.git/`, `node_modules/`, build outputs, caches, vendor directories — excluded from all passes.

### 7.2 Parallelization

- All agents within a priority tier run in parallel
- Maximum 7-8 concurrent agents per wave
- Pass N+1 does not start until Pass N is reviewed and validated
- Within a pass, agents are independent (no cross-agent data dependencies during execution)

### 7.3 Recommended Batch Plan (Scaling)

For a monorepo with ~1,500 files:
- **Pass 1**: 8-12 agents (Haiku), 50 files each, ~1-2 hours
- **Pass 2**: 12-16 agents (Sonnet), 20-30 files each, ~3-5 hours
- **Pass 3**: 20-26 agents (Sonnet), 20-50 files each, ~4-8 hours

For large repos, use **tiered P3 depth**:
- **Deep** (per-file profile): Root configs, infrastructure, CI/CD, deploy scripts (~200 files)
- **Medium** (directory assessment + sampling): Source code directories (~800 files)
- **Light** (reference-grep only): Assets, documentation, generated files (~400 files)

---

## 8. Output Specifications

### 8.1 Output Directory Structure

```
.claude-audit/${CLAUDE_SESSION_ID}/
├── progress.json                        # Checkpoint/resume state
├── pass1/
│   ├── batch-01-infra.md               # Per-agent batch reports
│   ├── batch-02-frontend.md
│   ├── ...
│   ├── pass1-summary.md                # Consolidated pass summary
│   └── validation-report.md            # Spot-check results
├── pass2/
│   ├── batch-01-*.md
│   ├── ...
│   ├── pass2-summary.md
│   └── validation-report.md
├── pass3/
│   ├── batch-01-*.md
│   ├── ...
│   ├── duplication-matrix.md           # Mandatory for Pass 3
│   ├── pass3-summary.md
│   └── validation-report.md
├── discovered-issues.md                 # Cross-pass shared findings
└── final-report.md                      # Consolidated final report
```

### 8.2 Per-Agent Batch Report Template

See `templates/batch-report.md` for full template. Required sections:
- Scope definition (directories/files covered; exclusions stated)
- Files to DELETE (with evidence)
- Files to CONSOLIDATE (Pass 3 only, with overlap %)
- Files to MOVE (with target and refs to update)
- Files to FLAG (with finding type and verification checklist)
- Broken References Found
- Files to KEEP (verified legitimate with citations)
- Remaining / Not Audited (mandatory if scope incomplete)
- Summary counts

### 8.3 Consolidated Final Report Template

See `templates/final-report.md` for full template. Required sections:
- Executive Summary (total files, coverage %, action counts, effort estimate)
- Action Items by Priority (Immediate / Requires Decision / Requires Code Changes)
- Cross-Cutting Findings (systemic patterns)
- Discovered Issues Registry (numbered list)

### 8.4 Global Required Sections (All Reports)

Every report MUST include:
- Scope definition (directories/files covered; exclusions stated explicitly)
- Summary counts (DELETE / MOVE / FLAG / CONSOLIDATE / KEEP / BROKEN REFS)
- **Remaining / Not Audited** section (mandatory if scope incomplete — transparency beats pretending completeness)
- **Already-known issues not re-flagged** (Pass 3 only)

---

## 9. Safety Rails

### 9.1 Read-Only Enforcement (3 Layers)

| Layer | Mechanism | Enforcement Level |
|-------|-----------|-------------------|
| Platform | `allowed-tools` in SKILL.md frontmatter | Cannot be bypassed by prompt |
| Subagent | `tools: Read, Grep, Glob` in agent definitions | Agent-level restriction |
| Prompt | "DO NOT edit, delete, move, or modify ANY existing file" | Instruction-level |

### 9.2 Conservative Bias Rules

- **Err on KEEP**: When uncertain, mark REVIEW/FLAG, never DELETE
- **Evidence required for DELETE**: Zero-reference grep + no dynamic loading + successor identified (or transient artifact)
- **No assumptions from filenames**: Read content and trace references before classifying
- **Flag over delete for shared code**: If imported by even one consumer, FLAG for refactoring, not DELETE
- **No speculative deletions**: Every DELETE must be evidence-backed

### 9.3 Incremental Save Protocol

Agents MUST follow this workflow:
1. Create output file with header template before auditing any files
2. Work in sub-batches of 5-10 files
3. After each sub-batch, immediately save/update the output file
4. Never accumulate more than 10 unwritten results
5. Each save includes all results so far (full rewrite or append)

### 9.4 Known-Issues Deduplication

- Pass 2 prompt includes Pass 1 findings to avoid re-flagging
- Pass 3 prompt includes numbered list of all findings from Passes 1-2
- Agents encountering known issues note "Already tracked as issue #N" and move on

### 9.5 Resume Protocol

State tracked in `progress.json`:
```json
{
  "session_id": "<session-id>",
  "started_at": "<timestamp>",
  "current_pass": 1,
  "total_passes": 3,
  "batches": [
    {"id": 1, "status": "complete", "files": 50, "findings": 12},
    {"id": 2, "status": "in_progress", "files": 50, "findings": null}
  ],
  "coverage": {"audited": 100, "total": 1500, "percent": 6.7}
}
```

On invocation, check for existing state file. If found, offer to resume.

---

## 10. Quality Gates

### 10.1 Evidence Thresholds

| Recommendation | Required Evidence |
|---------------|-------------------|
| DELETE | Zero references (grep pattern + count) + no CI/CD + no dynamic loading + successor OR transient |
| CONSOLIDATE | Both files read + overlap quantified (% or sections) + canonical chosen + migration notes |
| MOVE | Location assessed incorrect + target justified + refs to update listed |
| FLAG | Issue described + action specific + verification checklist |
| KEEP | At least one active reference cited + explicit verification notes |

### 10.2 Pass Completion Gates

Before advancing from Pass N to Pass N+1:
1. All batch tasks marked complete in TodoWrite
2. All batch reports contain required sections (validate programmatically where possible)
3. Coverage % meets minimum threshold (100% for Pass 1, scope-defined for Pass 2-3)
4. Validation agent has spot-checked 10% of findings
5. No FAILED reports (missing mandatory profiles)

### 10.3 Spot-Check Protocol

For every 50 files audited, randomly select 5 and verify:
- Does the agent's grep claim match actual grep results?
- Did the agent actually read the file or guess from filename?
- Are KEEP recommendations genuine (file truly referenced)?
- Are DELETE recommendations safe (file truly unreferenced)?

---

## 11. Reusable Cleanup Principles

Ordered by dependency (from Spec v1.1 §13, preserved):

1. **Read-only by default**: Audit output only; no repo edits during audit
2. **Evidence over assumption**: Every recommendation must cite specific grep results, line numbers, or config references
3. **Conservative default**: When in doubt, FLAG rather than DELETE
4. **Read before judging**: A file named `old-deploy.sh` might be the only deploy script that works
5. **Proof standards rise each pass**: Pass 1 quick triage → Pass 2 per-file proof → Pass 3 cross-cutting diff/overlap
6. **Escalating depth**: Broad and shallow first, narrow and deep second
7. **Mandatory evidence**: Every KEEP/DELETE needs verifiable anchors (references + file:line)
8. **Profile everything**: Even KEEP items get profiles — prevents re-auditing and creates institutional knowledge
9. **Incremental saves**: Context windows are finite — save every 5-10 files
10. **Scope discipline**: Cap files per agent; state explicit exclusions
11. **Orchestrated batching**: Priority-first, parallel where independent, fast-path for binary/assets
12. **Noise control (dedup across passes)**: Each pass receives known issues list from previous passes
13. **Completion criteria and Remaining list**: Transparency beats pretending completeness
14. **Output schema as quality gate**: Reports must follow templates with mandatory fields
15. **Verify documentation claims**: Check 3-5 technical claims per doc file against actual implementation
16. **Check test infrastructure**: Verify test configs confirm tests are actually discovered and runnable

---

## 12. Framework Integration Entries

### 12.1 COMMANDS.md Entry

```markdown
**`/sc:cleanup-audit [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]`**
— Multi-pass read-only repository audit (wave-enabled, complex profile)
- **Auto-Persona**: Analyzer, Architect, DevOps, QA, Refactorer
- **MCP**: Sequential (cross-cutting synthesis), Serena (import chains), Context7 (framework patterns)
- **Tools**: [Read, Grep, Glob, Bash, TodoWrite, Task, Write]
```

### 12.2 ORCHESTRATOR.md Routing Entry

```markdown
| "cleanup audit" / "repo audit" / "dead code" | complex | quality/maintenance | analyzer + architect + devops + qa + refactorer, --ultrathink, Sequential + Serena + Context7 | 95% |
```

### 12.3 Persona Trigger Updates

Add to analyzer persona triggers: "audit", "cleanup-audit", "dead code", "orphan files", "repo cleanup"

---

## 13. Token Cost Estimates

| Component | Token Cost | Model |
|-----------|-----------|-------|
| Skill loading + preprocessing | ~3K | Orchestrator |
| Pass 1: Surface Scan (1000 files) | ~400-600K | Haiku |
| Pass 2: Structural Audit (~150 flagged) | ~200-400K | Sonnet |
| Pass 3: Cross-Cutting (~200 files) | ~100-200K | Sonnet |
| Validation (10% spot-checks) | ~50-100K | Sonnet |
| Consolidation + Final Report | ~50-100K | Sonnet |
| **Total Estimated** | **~800K-1.4M** | Mixed |

**Cost optimization levers**:
- Haiku for Pass 1 (reduces by ~60%)
- Larger batch sizes (reduces subagent overhead — 20K per agent)
- Skip Pass 3 for smaller repos
- maxTurns prevents runaway agents
- Incremental saves prevent re-work on session interruption

---

## 14. Implementation Roadmap (File-Level)

### Phase 1: Foundation
1. `SKILL.md` — Main orchestration file
2. `scripts/repo-inventory.sh` — File enumeration and batching

### Phase 2: Rules & Templates (Parallel)
3. `rules/pass1-surface-scan.md`
4. `rules/pass2-structural-audit.md`
5. `rules/pass3-cross-cutting.md`
6. `rules/verification-protocol.md`
7. `rules/dynamic-use-checklist.md`
8. `templates/batch-report.md`
9. `templates/pass-summary.md`
10. `templates/final-report.md`
11. `templates/finding-profile.md`

### Phase 3: Subagent Definitions (Parallel)
12. `agents/audit-scanner.md`
13. `agents/audit-analyzer.md`
14. `agents/audit-comparator.md`
15. `agents/audit-consolidator.md`
16. `agents/audit-validator.md`

### Phase 4: Integration
17. COMMANDS.md entry
18. ORCHESTRATOR.md routing entry
19. PERSONAS.md trigger updates

### Phase 5: Validation
20. Test with small repo scope (single directory)
21. Test full 3-pass audit on medium repo
22. Validate output format compliance
