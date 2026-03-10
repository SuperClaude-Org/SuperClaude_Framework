# Refactor Plan: sc-repo-audit-command-spec → SuperClaude Skill

**Generated**: 2026-02-19
**Input**: `sc-repo-audit-command-spec-merged.md` (690 lines, analytical specification)
**Output**: Complete skill package ready for roadmap generation and implementation
**Methodology**: Informed by Agent 1 (40 structural rules), Agent 2 (22 ranked capabilities), Toolbox Inventory, and Custom Command Guide

---

## Executive Summary

The current spec is a well-researched analytical document describing WHAT the cleanup-audit command should do. The refactor transforms it into a properly structured SuperClaude skill package that specifies HOW it should work as an actual executable command, leveraging all platform capabilities while maintaining strict consistency with existing /sc:* commands.

### Key Architectural Decision: Skill + Custom Subagents (Hybrid Approach)

Based on research findings (Agent 2, Part 3):
- **Skill** (`.claude/skills/sc-cleanup-audit/`) for orchestration — supporting files are essential for rules, templates
- **Custom Subagents** (`.claude/agents/`) for worker agents — different models, tools, and behaviors per pass type
- **NOT a single command file** — too complex for a single .md, needs separation of concerns

---

## Phase 1: File Architecture

### 1.1 Deliverable: Skill Directory Structure

Create this file tree:

```
.claude/skills/sc-cleanup-audit/
├── SKILL.md                              # Main orchestration (<500 lines)
├── rules/
│   ├── pass1-surface-scan.md            # Pass 1 criteria, file-type rules, classification
│   ├── pass2-structural-audit.md        # Pass 2 per-file profile fields, verification protocol
│   ├── pass3-cross-cutting.md           # Pass 3 comparison methodology, duplication matrix
│   ├── verification-protocol.md         # Universal evidence requirements (DELETE/KEEP/CONSOLIDATE/FLAG/MOVE)
│   └── dynamic-use-checklist.md         # Dynamic loading patterns to check before DELETE
├── templates/
│   ├── batch-report.md                  # Per-agent batch output template
│   ├── pass-summary.md                  # Per-pass consolidated summary template
│   ├── final-report.md                  # Consolidated final report template
│   └── finding-profile.md              # Per-file finding profile template
└── scripts/
    └── repo-inventory.sh               # Shell script: file enumeration, type counting, batching

.claude/agents/
├── audit-scanner.md                     # Pass 1 worker (Haiku, read-only, fast)
├── audit-analyzer.md                    # Pass 2 worker (Sonnet, read-only, deep)
├── audit-comparator.md                  # Pass 3 worker (Sonnet, read-only, cross-cutting)
├── audit-consolidator.md               # Report merger (Sonnet, Write-enabled)
└── audit-validator.md                   # Spot-check validator (Sonnet, read-only)
```

### 1.2 Content Extraction Map

How content from the current spec maps to the new file structure:

| Spec Section | Target File | Transformation |
|-------------|-------------|----------------|
| §1 Command Name & Purpose | SKILL.md frontmatter + §Triggers + §Usage | Reformat to SuperClaude template |
| §2 Objectives | SKILL.md §Behavioral Flow Key behaviors | Distill into behavioral characteristics |
| §3 Pass 1 details | rules/pass1-surface-scan.md | Extract criteria, taxonomy, verification protocol |
| §3 Pass 2 details | rules/pass2-structural-audit.md | Extract per-file profile, extra rules by type |
| §3 Pass 3 details | rules/pass3-cross-cutting.md | Extract comparison methodology, matrix requirement |
| §4 Classification Taxonomy | rules/verification-protocol.md header | Unified taxonomy table |
| §5 Verification Protocol | rules/verification-protocol.md | Evidence requirements, cross-reference checklist |
| §6 Agent Orchestration | SKILL.md §Behavioral Flow + §Tool Coordination | Reformat to orchestration instructions |
| §7 Output Schema | templates/*.md | Split into per-use templates |
| §8 Safety Rails | SKILL.md §Boundaries + §Critical Boundaries | SuperClaude boundary format |
| §9 Quality Gates | SKILL.md §Behavioral Flow step 4 + gates section | Integrate into verification step |
| §10 Effectiveness Score | EXCLUDE — instance-specific data | Not part of the command definition |
| §11 Improvements | INTEGRATE — apply improvements to the spec itself | Improvements become features |
| §12 Integration Notes | SKILL.md §MCP Integration + §Persona Coordination | SuperClaude format |
| §13 Reusable Principles | rules/verification-protocol.md footer | Guiding principles section |
| Appendix (Traceability) | EXCLUDE — meta-document, not command content | Archive separately |

---

## Phase 2: SKILL.md Design (SuperClaude Convention Compliance)

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

**Rationale**:
- `category: utility` — read-only analysis, does not modify code (per Agent 1 BP#11)
- `complexity: high` — full MCP, multi-persona, Task delegation, wave-eligible (per Agent 1 BP#10)
- `disable-model-invocation: true` — resource-intensive, user-invoked only (Agent 2, ranked #9)
- `allowed-tools` — read-only tools + controlled Bash + TodoWrite + Task + Write (for reports only)
- MCP: Sequential (complex analysis), Serena (import chain tracing), Context7 (framework patterns)
- Personas: analyzer (primary), architect (infra), devops (CI/deploy), qa (tests), refactorer (duplication)

### 2.2 Behavioral Flow (5 Steps)

```markdown
## Behavioral Flow
1. **Discover**: Enumerate repository contents via shell preprocessing and Glob.
   Calculate file inventory, type distribution, and scope metrics.
   Create batch plan with domain-based grouping and priority ordering.

2. **Configure**: Select pass type from $ARGUMENTS (surface|structural|cross-cutting|all).
   Load pass-specific rules from supporting files.
   Create TodoWrite tasks for each batch and quality gate.
   Initialize output directory and progress checkpoint file.

3. **Orchestrate**: Spawn parallel audit subagents per batch via Task tool.
   Pass 1 uses audit-scanner (Haiku), Pass 2 uses audit-analyzer (Sonnet),
   Pass 3 uses audit-comparator (Sonnet). Agents write results to disk incrementally.
   Run in waves of 7-8 concurrent agents. Quality gate between waves.

4. **Validate**: After each pass, run audit-validator to spot-check 10% of findings.
   Verify evidence quality (grep proof for DELETE, reference citations for KEEP).
   Quality gate: all batch reports present + required sections complete + coverage threshold met.
   For cross-cutting pass, verify duplication matrix completeness.

5. **Report**: Run audit-consolidator to merge batch reports into pass summary.
   If --pass all, consolidate all pass summaries into final report.
   Produce executive summary with action priority, cross-cutting findings, and discovered issues registry.
   Output to `.claude-audit/<session-id>/` directory.
```

### 2.3 MCP Integration

```markdown
## MCP Integration
- **Sequential MCP**: Auto-activated for cross-cutting analysis in Pass 3 and final synthesis (ultrathink).
  Provides structured reasoning for identifying systemic patterns across batch results.
- **Serena MCP**: Auto-activated for import chain tracing during Pass 2 structural audit.
  Enables semantic understanding of file dependencies beyond string-based grep.
- **Context7 MCP**: Auto-activated for framework-specific pattern validation.
  Validates that flagged configurations match current framework conventions.
- **Augment MCP** (optional): Semantic codebase search for discovery phase.
  Supplements Grep with embedding-based retrieval for finding non-obvious file relationships.
- **Persona Coordination**: analyzer (primary, all passes) + architect (infrastructure batches) +
  devops (CI/deploy batches) + qa (test file batches) + refactorer (duplication findings in Pass 3)
- **MCP Constraint**: MCP tools are available to the orchestrator ONLY, not to background subagents.
  All MCP-dependent analysis happens in Step 1 (Discover) and Step 5 (Report).
```

### 2.4 Tool Coordination

```markdown
## Tool Coordination
- **Read/Grep/Glob**: Core audit tools. Read file contents, search for references across repo,
  enumerate files for batching. These are the ONLY tools available to audit subagents.
- **Bash(git/wc/find/du)**: Controlled shell access for repository metadata collection.
  git log, git ls-files for inventory. wc/find/du for metrics. No destructive commands.
- **Write**: Report generation only. Batch reports, pass summaries, final consolidated report.
  Audit agents write to `.claude-audit/` directory exclusively.
- **TodoWrite**: Progress tracking across batches, passes, and quality gates.
  Each batch is a tracked task. Coverage metrics updated in real-time.
- **Task**: Sub-agent delegation for parallel batch processing.
  Spawns custom audit subagents (scanner, analyzer, comparator, consolidator, validator).
```

### 2.5 Key Patterns

```markdown
## Key Patterns
- **Haiku-First Escalation**: All files scanned cheaply (Haiku) → flagged subset analyzed deeply (Sonnet) → 50-70% cost reduction
- **Evidence-Gated Classification**: File → grep for references → check dynamic loading patterns → classify with proof → every recommendation has verifiable evidence
- **Incremental Checkpoint**: Batch completes → write results to disk → update progress file → resume-safe at any point
- **Fan-Out/Fan-In Orchestration**: Divide files into batches → spawn parallel agents → collect results → merge and deduplicate → synthesize cross-cutting patterns
- **Conservative Escalation**: DELETE only with zero-reference proof → FLAG when uncertain → KEEP when any reference found → safety over thoroughness
```

### 2.6 Examples

```markdown
## Examples

### Full Repository Surface Scan
\```
/sc:cleanup-audit .
# Runs Pass 1 on entire repo
# Spawns Haiku agents in batches of 50 files
# Produces DELETE/REVIEW/KEEP classification for every file
# Output: .claude-audit/<session>/pass1-summary.md
\```

### Structural Audit on Specific Directory
\```
/sc:cleanup-audit src/ --pass structural --batch-size 25
# Runs Pass 2 on src/ directory only
# Uses Sonnet agents for deep per-file profiling
# Mandatory per-file profile with 8 required fields
# Output: .claude-audit/<session>/pass2-summary.md
\```

### Infrastructure-Focused Cross-Cutting Sweep
\```
/sc:cleanup-audit . --pass cross-cutting --focus infrastructure
# Runs Pass 3 focused on Docker, CI/CD, deploy scripts, configs
# Produces duplication matrix for compose/deploy/test configs
# Quantifies overlap percentages between similar files
# Output: .claude-audit/<session>/pass3-infra-summary.md
\```

### Complete 3-Pass Audit
\```
/sc:cleanup-audit . --pass all --batch-size 40
# Runs all 3 passes sequentially with quality gates between
# Pass 1 (Haiku) → Gate → Pass 2 (Sonnet, flagged files) → Gate → Pass 3 (Sonnet, cross-cutting)
# Final consolidated report with executive summary and action items
# Output: .claude-audit/<session>/final-report.md
\```
```

### 2.7 Boundaries

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

**Output**: Audit reports written to `.claude-audit/<session-id>/` containing:
- Per-pass batch reports with per-file profiles
- Pass summary with findings counts and coverage metrics
- Consolidated final report with executive summary and prioritized action items
- Discovered issues registry with cross-cutting patterns

**Next Step**: Use `/sc:cleanup` to execute safe recommendations from the audit report,
then `/sc:test` to verify no regressions, then `/sc:git` to commit cleanup changes.
```

---

## Phase 3: Supporting Files Design

### 3.1 rules/pass1-surface-scan.md
**Source**: Spec §3 Pass 1
**Content**:
- Goal statement and guiding question
- 3-tier classification taxonomy (DELETE/REVIEW/KEEP)
- Verification protocol (read 20-30 lines, grep filename, check imports, categorize)
- Output format template
- Batch size guidance (25-50 files)
- Binary asset handling rules

### 3.2 rules/pass2-structural-audit.md
**Source**: Spec §3 Pass 2
**Content**:
- Goal statement and guiding question
- 5 finding types (MISPLACED/STALE/STRUCTURAL ISSUE/BROKEN REFS/VERIFIED OK)
- 4 action recommendations (KEEP/DELETE/MOVE/FLAG)
- Mandatory per-file profile (8 required fields)
- Extra rules by file type (tests, scripts, documentation, config)
- Failure criterion for reports missing profiles
- Scope limitation (only KEEP/REVIEW from Pass 1)

### 3.3 rules/pass3-cross-cutting.md
**Source**: Spec §3 Pass 3
**Content**:
- Goal statement and guiding question
- Extended taxonomy (adds CONSOLIDATE, BROKEN REF)
- Per-file profile fields (7 fields including similarity analysis)
- 6 critical differentiators from Pass 2
- Focus areas (compose files, configs, root clutter, cross-directory duplication)
- Mandatory duplication matrix requirement
- Tiered depth strategy (deep/medium/light by file category)

### 3.4 rules/verification-protocol.md
**Source**: Spec §4 + §5 + §13
**Content**:
- Unified classification taxonomy (priority-ordered, 6 categories)
- Per-recommendation evidence requirements (DELETE/KEEP/CONSOLIDATE/FLAG/MOVE)
- Cross-reference checklist (7 reference sources)
- Documentation claim verification protocol
- Dynamic-use checklist (5 dynamic loading patterns)
- 16 reusable cleanup principles

### 3.5 rules/dynamic-use-checklist.md
**Source**: Spec §11 item 4
**Content**:
- Environment variable-based module loading patterns
- String-based import loaders
- Plugin registries
- Glob-based file discovery
- Config-driven loading patterns
- Per-language examples (JavaScript, Python, Go, Ruby)

### 3.6 templates/batch-report.md
**Source**: Spec §7 Per-Agent Output
**Content**: Complete markdown template with sections for DELETE/CONSOLIDATE/MOVE/FLAG/BROKEN REFS/KEEP/Remaining/Summary

### 3.7 templates/pass-summary.md
**Source**: Spec §7 (new, addressing improvement #6)
**Content**: Consolidated pass summary with deduplication, cross-agent pattern extraction, executive summary

### 3.8 templates/final-report.md
**Source**: Spec §7 Consolidated Final Report
**Content**: Executive summary, action items by priority, cross-cutting findings, discovered issues registry

### 3.9 templates/finding-profile.md
**Source**: Spec §3 Pass 2 mandatory fields
**Content**: Template for the 8-field per-file profile used in Pass 2+

### 3.10 scripts/repo-inventory.sh
**Source**: Spec §11 items 1-3, Agent 2 shell preprocessing patterns
**Content**:
- `git ls-files` based file enumeration (portable, respects .gitignore)
- File type distribution calculation
- Exclusion of .git/, node_modules/, build outputs
- Batch creation by domain (infrastructure, frontend, backend, docs, tests)
- Coverage tracking (files_audited / total)

---

## Phase 4: Custom Subagent Definitions

### 4.1 audit-scanner.md (Pass 1 Worker)
```yaml
---
name: audit-scanner
description: "Fast read-only surface scanner for Pass 1 repository audit"
tools: Read, Grep, Glob
model: haiku
maxTurns: 20
permissionMode: plan
---
```
System prompt: Surface scan methodology, 3-tier taxonomy, verification protocol, output format.

### 4.2 audit-analyzer.md (Pass 2 Worker)
```yaml
---
name: audit-analyzer
description: "Deep structural auditor for Pass 2 per-file profiling"
tools: Read, Grep, Glob
model: sonnet
maxTurns: 35
permissionMode: plan
---
```
System prompt: Structural audit methodology, mandatory 8-field profile, extra rules by file type, evidence standards.

### 4.3 audit-comparator.md (Pass 3 Worker)
```yaml
---
name: audit-comparator
description: "Cross-cutting comparator for Pass 3 duplication and sprawl detection"
tools: Read, Grep, Glob
model: sonnet
maxTurns: 35
permissionMode: plan
---
```
System prompt: Comparison methodology, CONSOLIDATE classification, duplication matrix, overlap quantification.

### 4.4 audit-consolidator.md (Report Merger)
```yaml
---
name: audit-consolidator
description: "Consolidates batch reports into pass summaries and final reports"
tools: Read, Grep, Glob, Write
model: sonnet
maxTurns: 40
permissionMode: plan
---
```
System prompt: Merge logic, deduplication, cross-agent pattern extraction, report templates.

### 4.5 audit-validator.md (Quality Checker)
```yaml
---
name: audit-validator
description: "Spot-check validator that verifies audit finding accuracy"
tools: Read, Grep, Glob
model: sonnet
maxTurns: 25
permissionMode: plan
---
```
System prompt: Validation protocol, spot-check sampling (5 per 50), re-grep verification, false positive/negative detection.

---

## Phase 5: Spec Improvements Integration

The 10 improvements from Spec §11 are integrated as follows:

| Improvement | Integration Point | How |
|------------|------------------|-----|
| 1. Full-Coverage Pass 1 | scripts/repo-inventory.sh + SKILL.md §Configure | git ls-files based enumeration, mandatory 100% coverage |
| 2. Coverage Tracking | SKILL.md §Validate + templates/batch-report.md | Every report states files_audited/total = coverage% |
| 3. Automated Pre-Scan | scripts/repo-inventory.sh + shell preprocessing | Pre-scan hints injected into Pass 1 agent prompts |
| 4. Dynamic-Use Checklist | rules/dynamic-use-checklist.md | Dedicated rules file, checked before DELETE |
| 5. Shared Findings Channel | SKILL.md §Orchestrate | Between-pass: findings file. Within-pass: discovered issues doc |
| 6. Output Consolidation | audit-consolidator.md + templates/pass-summary.md | Dedicated consolidation agent + template |
| 7. Duplication Matrix | rules/pass3-cross-cutting.md | Mandatory section in Pass 3 output |
| 8. Workflow-to-Config Mapping | rules/pass2-structural-audit.md | Required in CI/test file profiles |
| 9. Validation Meta-Agent | audit-validator.md | Dedicated validation subagent |
| 10. Portable Output Paths | All templates | $REPO_ROOT + relative paths only |

---

## Phase 6: Framework Integration Updates

### 6.1 COMMANDS.md Entry
```markdown
**`/sc:cleanup-audit [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]`**
— Multi-pass read-only repository audit (wave-enabled, complex profile)
- **Auto-Persona**: Analyzer, Architect, DevOps, QA, Refactorer
- **MCP**: Sequential (analysis), Serena (import chains), Context7 (framework patterns)
- **Tools**: [Read, Grep, Glob, Bash, TodoWrite, Task, Write]
```

### 6.2 ORCHESTRATOR.md Routing Entry
```markdown
| "cleanup audit" / "repo audit" | complex | quality/maintenance | analyzer + architect + devops + qa + refactorer, --ultrathink, Sequential + Serena | 95% |
```

### 6.3 Persona Trigger Updates
Add "audit", "cleanup-audit", "dead code", "orphan files" to analyzer persona triggers.

---

## Deliverables Summary

| # | Deliverable | Type | Lines (est.) |
|---|------------|------|-------------|
| 1 | SKILL.md | Orchestration file | 400-500 |
| 2 | rules/pass1-surface-scan.md | Rules file | 80-100 |
| 3 | rules/pass2-structural-audit.md | Rules file | 120-150 |
| 4 | rules/pass3-cross-cutting.md | Rules file | 120-150 |
| 5 | rules/verification-protocol.md | Rules file | 150-180 |
| 6 | rules/dynamic-use-checklist.md | Rules file | 60-80 |
| 7 | templates/batch-report.md | Template | 60-80 |
| 8 | templates/pass-summary.md | Template | 40-60 |
| 9 | templates/final-report.md | Template | 60-80 |
| 10 | templates/finding-profile.md | Template | 30-40 |
| 11 | scripts/repo-inventory.sh | Shell script | 60-80 |
| 12 | agents/audit-scanner.md | Subagent def | 80-100 |
| 13 | agents/audit-analyzer.md | Subagent def | 100-120 |
| 14 | agents/audit-comparator.md | Subagent def | 100-120 |
| 15 | agents/audit-consolidator.md | Subagent def | 80-100 |
| 16 | agents/audit-validator.md | Subagent def | 60-80 |
| **Total** | | **16 files** | **~1,400-1,700** |

---

## Implementation Order

1. **Foundation**: SKILL.md + scripts/repo-inventory.sh
2. **Rules**: All 5 rules files (can be done in parallel)
3. **Templates**: All 4 templates (can be done in parallel with rules)
4. **Agents**: All 5 subagent definitions (can be done in parallel)
5. **Integration**: COMMANDS.md + ORCHESTRATOR.md + PERSONAS.md updates
6. **Validation**: Test with a small repo scope
