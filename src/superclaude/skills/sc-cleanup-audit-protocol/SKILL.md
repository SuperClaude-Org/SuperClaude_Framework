---
name: cleanup-audit
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"
---

# /sc:cleanup-audit - Multi-Pass Repository Audit

## Triggers
- Large repository with accumulated technical debt, dead code, or config sprawl
- Post-migration or post-refactor cleanup requiring systematic verification
- Periodic repo hygiene audit to maintain organizational integrity
- Pre-release cleanup to reduce attack surface and deployment weight
- New team member onboarding requiring codebase understanding and cleanup

## Usage
```
/sc:cleanup-audit [target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]
```

### Arguments
- **target-path**: Directory to audit (default: `.` for entire repo)
- **--pass**: Audit pass to run (`surface` = Pass 1, `structural` = Pass 2, `cross-cutting` = Pass 3, `all` = sequential 3-pass)
- **--batch-size**: Files per agent batch (default: 50 for surface, 25 for structural, 30 for cross-cutting)
- **--focus**: Domain filter for targeted auditing (`infrastructure`, `frontend`, `backend`, `all`)

## Repository Context
- Total files: !`git ls-files | wc -l`
- File breakdown: !`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15`
- Repo size: !`du -sh . --exclude=.git --exclude=node_modules 2>/dev/null`
- Current branch: !`git branch --show-current`
- Last commit: !`git log --oneline -1`

## Target Scope
- Target: $ARGUMENTS
- Files in scope: !`find ${0:-.} -type f -not -path '*/.git/*' -not -path '*/node_modules/*' | wc -l`
- File types: !`find ${0:-.} -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10`

## Behavioral Flow
1. **Discover**: Enumerate repository files via shell preprocessing and `repo-inventory.sh`. Build file inventory with domain grouping, type distribution, and batch assignments. Compute total scope and coverage targets.
2. **Configure**: Parse `$ARGUMENTS` for pass selection and focus area. Load pass-specific rules from `rules/` supporting files. Create TodoWrite tasks for each batch. Initialize output directory at `.claude-audit/`.
3. **Orchestrate**: Spawn parallel subagents via Task tool in waves of 7-8 concurrent agents. Pass 1 uses `audit-scanner` (Haiku), Pass 2 uses `audit-analyzer` (Sonnet), Pass 3 uses `audit-comparator` (Sonnet). Each agent writes batch reports incrementally to disk. Track progress via TodoWrite.
4. **Validate**: Spawn `audit-validator` for 10% spot-check sampling (5 findings per 50 files). Verify grep claims match actual results. Enforce quality gates: all batch reports must have required sections and mandatory per-file profiles. Failed reports trigger regeneration.
5. **Report**: Spawn `audit-consolidator` to merge batch reports into pass summaries. For `--pass all`, produce final report with executive summary, prioritized action items, cross-cutting findings, and discovered issues registry. Apply ultrathink synthesis for cross-pass pattern extraction.

Key behaviors:
- **Haiku-first cost optimization**: Pass 1 uses Haiku agents for 50-70% cost reduction; Sonnet reserved for deep analysis in Passes 2-3
- **Evidence-gated classification**: Every DELETE requires grep proof; every KEEP requires reference citation; every CONSOLIDATE requires overlap quantification
- **Incremental checkpointing**: Agents save after every 5-10 files; progress.json enables resume-from-checkpoint on session interruption
- **Conservative escalation**: When uncertain, agents classify as REVIEW/FLAG rather than DELETE — false negatives are cheaper than false positives
- **Fan-out/fan-in orchestration**: Orchestrator divides work → spawns N parallel agents → agents write to disk → orchestrator reads and merges

## MCP Integration
- **Sequential MCP**: Cross-cutting synthesis during Step 5 report consolidation; ultrathink analysis for systemic pattern detection across all passes
- **Serena MCP**: Import chain tracing during Step 1 discovery phase; symbol-level understanding for verifying dynamic loading patterns
- **Context7 MCP**: Framework-specific configuration validation; verifying library usage patterns against official documentation
- **Persona Coordination**: Analyzer leads all passes; Architect activated for infrastructure batches; DevOps for Docker/CI/deploy; QA for test file batches; Refactorer for duplication findings
- **MCP Constraint**: MCP tools are unavailable to background subagents — all MCP-dependent work (ultrathink synthesis, import chain tracing) executes in the orchestrator only

## Tool Coordination
- **Read/Grep/Glob**: Core audit tools available to all subagents — file content reading, reference tracing via regex, file inventory via pattern matching
- **Bash(git/wc/find/du)**: Controlled shell access for orchestrator only — `git ls-files` for inventory, `wc` for counting, `find` for scope calculation, `du` for size metrics
- **Write**: Report generation restricted to `.claude-audit/` output directory — batch reports, pass summaries, final report, progress tracking files
- **TodoWrite**: Progress tracking with per-batch tasks — create tasks during Configure, update during Orchestrate, verify completion during Validate
- **Task**: Subagent delegation with 5 specialized agent types — audit-scanner (Haiku, Pass 1), audit-analyzer (Sonnet, Pass 2), audit-comparator (Sonnet, Pass 3), audit-consolidator (Sonnet, reports), audit-validator (Sonnet, spot-check)

## Key Patterns
- **Haiku-First Escalation**: All files → Haiku surface scan → flagged subset → Sonnet deep analysis
- **Evidence-Gated Classification**: File content → grep references + import check → evidence-backed recommendation
- **Incremental Checkpoint**: Batch complete → write to disk → update progress.json → resume-safe state
- **Fan-Out/Fan-In Orchestration**: File inventory → parallel agent waves (7-8) → disk-based results → consolidated report
- **Conservative Escalation**: Uncertain classification → FLAG/REVIEW (never DELETE) → human review gate

## Examples

### Full Repository Surface Scan
```
/sc:cleanup-audit
```
Runs Pass 1 surface scan on the entire repository. Uses Haiku agents to classify every file as DELETE/REVIEW/KEEP. Produces per-batch reports and a consolidated summary at `.claude-audit/pass1-summary.md`.

### Structural Audit of Source Directory
```
/sc:cleanup-audit src/ --pass structural --batch-size 25
```
Runs Pass 2 structural audit on `src/` directory only. Produces mandatory 8-field profiles for each file. Requires Pass 1 results as input context. Validates per-file evidence quality.

### Infrastructure Cross-Cutting Sweep
```
/sc:cleanup-audit --pass cross-cutting --focus infrastructure
```
Runs Pass 3 cross-cutting comparison on infrastructure files (Docker, CI/CD, deploy scripts, configs). Produces duplication matrix with overlap percentages. Groups similar files for comparative analysis.

### Complete 3-Pass Audit
```
/sc:cleanup-audit --pass all --focus all
```
Runs all 3 passes sequentially with quality gates between each pass. Pass 1 inventory feeds Pass 2 deep audit, which feeds Pass 3 cross-cutting sweep. Produces final consolidated report with executive summary, prioritized action items, and discovered issues registry.

## Boundaries

**Will:**
- Analyze every file in scope with evidence-backed classification (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP)
- Produce machine-checkable reports with mandatory per-file profiles and verifiable grep citations
- Track coverage metrics and transparently report what was and was not audited

**Will Not:**
- Modify, delete, move, or rename any repository file during the audit
- Make assumptions from filenames alone — every classification requires reading content and tracing references
- Mark files as DELETE without grep proof of zero references and confirmed absence of dynamic loading

## CRITICAL BOUNDARIES

**READ-ONLY AUDIT — NO REPOSITORY MODIFICATIONS**

**Explicitly Will NOT**:
- Edit, delete, move, or rename any existing repository file
- Execute cleanup recommendations — human review gate is mandatory
- Modify CI/CD pipelines, configs, or any operational infrastructure
- Make speculative deletions based on filename patterns without evidence

**Output**: Audit reports written to `.claude-audit/` directory only:
- Per-batch reports (one per agent invocation)
- Per-pass summary reports (consolidated findings)
- Final report (executive summary + prioritized actions)
- progress.json (checkpoint state for resume capability)

**Next Step**: Use `/sc:cleanup` to execute safe recommendations, then `/sc:test` to verify no regressions, then `/sc:git` to commit changes.
