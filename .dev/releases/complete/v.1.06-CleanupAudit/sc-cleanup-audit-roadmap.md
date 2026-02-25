# Release Roadmap: v1.06-CleanupAudit — `/sc:cleanup-audit` Skill

## Metadata
- **Source Specification**: `sc-cleanup-audit-spec-v2.md` (v2.0, 2026-02-19)
- **Generated**: 2026-02-19
- **Generator**: SuperClaude Roadmap Generator v1.0 (adapted)
- **Compliance Tier**: STRICT (multi-file, security-adjacent read-only enforcement, multi-agent orchestration)
- **Strategy**: Systematic (comprehensive, methodical execution)
- **Item Count**: 22 deliverables, 6 milestones, 82 tasks

### Persona Assignment
- **Primary**: Analyzer — 40% of items are audit methodology and evidence-based analysis work
- **Consulting**: Architect (system design, orchestration patterns), DevOps (CI/deploy audit rules), QA (validation agents, quality gates), Refactorer (duplication detection rules)
- **Scribe**: Documentation templates and report formatting

### Dependency Constraints (from Research)
- Subagents CANNOT spawn sub-subagents — all orchestration in SKILL.md
- MCP tools unavailable in background subagents — MCP-dependent work in orchestrator only
- ~7-10 concurrent subagent practical limit — wave sizing must respect this
- ~20K token overhead per subagent invocation — batch sizing optimization critical
- TodoWrite has 3 states only: `pending`, `in_progress`, `completed`
- Agent type embedded in Task prompt (no `subagent_type` API parameter)

---

## Executive Summary

The `/sc:cleanup-audit` skill is a multi-pass, read-only repository audit command that spawns parallel subagents to analyze files in batches, producing evidence-backed cleanup recommendations (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP). It implements a 3-pass escalation model (surface scan → structural audit → cross-cutting sweep) with Haiku-first cost optimization, incremental checkpointing, and spot-check validation.

The implementation requires 16 primary files across a skill directory (SKILL.md + 5 rules + 4 templates + 1 script) and 5 custom subagent definitions, plus 3 framework integration updates. The systematic strategy delivers these across 6 milestones with clear dependency gates.

---

## Milestones Overview

| Milestone | Name | Deliverables | Dependencies | Risk Level | Est. Complexity |
|-----------|------|-------------|--------------|------------|-----------------|
| M1 | Foundation & Orchestration | SKILL.md, repo-inventory.sh | None | Medium | High |
| M2 | Rules Engine | 5 rules files | M1 (SKILL.md references rules) | Low | Medium |
| M3 | Output Templates | 4 template files + finding profile | M1 (SKILL.md references templates) | Low | Medium |
| M4 | Subagent Definitions | 5 custom subagent .md files | M1 (SKILL.md spawns agents), M2 (agents reference rules) | Medium | Medium |
| M5 | Framework Integration | COMMANDS.md, ORCHESTRATOR.md, PERSONAS.md | M1-M4 complete | Low | Low |
| M6 | Validation & Testing | Functional testing, output validation | M1-M5 complete | High | High |

---

## Milestone 1: Foundation & Orchestration

**Objective**: Create the core SKILL.md orchestration file and the repo-inventory shell script. These are the backbone that all other files reference and depend on.

**Dependencies**: None (first milestone)
**Estimated Complexity**: High
**Primary Persona**: Architect + Analyzer

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| M1-D1 | FEATURE | SKILL.md orchestration file | All 13 sections present per SuperClaude template, <500 lines | `.claude/skills/sc-cleanup-audit/SKILL.md` |
| M1-D2 | FEATURE | Repository inventory script | Produces file list, type distribution, batch assignments | `.claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh` |

### Tasks

#### T1.1: Create Skill Directory Structure
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/`, `rules/`, `templates/`, `scripts/`

**Steps**:
1. Create directory tree: `.claude/skills/sc-cleanup-audit/{rules,templates,scripts}`
2. Create directory: `.claude/agents/` (if not exists)
3. Verify directory permissions are correct

**Acceptance Criteria**:
- [ ] All directories exist and are writable
- [ ] Directory structure matches spec §1 Architecture Overview

**Verification**:
```bash
ls -la .claude/skills/sc-cleanup-audit/{rules,templates,scripts}
ls -la .claude/agents/
```

---

#### T1.2: Write SKILL.md Frontmatter & Header
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write YAML frontmatter with all required fields:
   - `name: cleanup-audit`
   - `description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"`
   - `category: utility`
   - `complexity: high`
   - `mcp-servers: [sequential, serena, context7]`
   - `personas: [analyzer, architect, devops, qa, refactorer]`
   - `disable-model-invocation: true`
   - `allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write`
   - `argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"`
2. Write H1 title: `# /sc:cleanup-audit - Multi-Pass Repository Audit`
3. Write Triggers section (5 bullet points from spec §2.2)
4. Write Usage section with argument descriptions from spec §2.3

**Acceptance Criteria**:
- [ ] Frontmatter has all 6 SuperClaude required fields + platform fields
- [ ] Field values match spec §2.1 exactly
- [ ] Triggers section has 5 activation scenarios
- [ ] Usage section shows all flags with pipe-separated options

---

#### T1.3: Write Behavioral Flow (5-Step)
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write Step 1 **Discover**: Repo enumeration via shell preprocessing + Glob, file inventory, batch plan creation
2. Write Step 2 **Configure**: Pass selection from $ARGUMENTS, load rules from supporting files, TodoWrite task creation, output directory initialization
3. Write Step 3 **Orchestrate**: Parallel subagent spawning via Task (scanner/analyzer/comparator), waves of 7-8, incremental disk saves
4. Write Step 4 **Validate**: Spawn audit-validator for 10% spot-check, evidence quality verification, quality gate enforcement
5. Write Step 5 **Report**: Spawn audit-consolidator, merge batch reports, ultrathink synthesis, final report with executive summary
6. Write "Key behaviors:" section with 5 distinctive characteristics

**Acceptance Criteria**:
- [ ] Exactly 5 steps with single-verb bold labels
- [ ] Steps follow Assess → Prepare → Execute → Verify → Output arc
- [ ] Key behaviors section has 5 bullets
- [ ] References correct subagent names (audit-scanner, audit-analyzer, audit-comparator, audit-validator, audit-consolidator)

---

#### T1.4: Write MCP Integration Section
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write Sequential MCP bullet (cross-cutting synthesis, ultrathink)
2. Write Serena MCP bullet (import chain tracing during discovery)
3. Write Context7 MCP bullet (framework-specific config validation)
4. Write Persona Coordination bullet (which personas for which batches)
5. Write MCP Constraint note (MCP unavailable to background subagents)

**Acceptance Criteria**:
- [ ] Each declared MCP server has a corresponding bullet with activation trigger and purpose
- [ ] Persona-MCP alignment is documented
- [ ] MCP constraint for subagents is explicitly stated

---

#### T1.5: Write Tool Coordination Section
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write Read/Grep/Glob bullet (core audit tools, available to all subagents)
2. Write Bash(git/wc/find/du) bullet (controlled shell, orchestrator only)
3. Write Write bullet (report generation to `.claude-audit/` only)
4. Write TodoWrite bullet (progress tracking, per-batch tasks, coverage metrics)
5. Write Task bullet (subagent delegation, list all 5 agent types)

**Acceptance Criteria**:
- [ ] Tools grouped by category per SuperClaude convention
- [ ] Only tools from `allowed-tools` frontmatter are listed
- [ ] Tool restrictions per agent type are clear

---

#### T1.6: Write Key Patterns Section
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write 5 key patterns using arrow notation from spec §2.7:
   - Haiku-First Escalation
   - Evidence-Gated Classification
   - Incremental Checkpoint
   - Fan-Out/Fan-In Orchestration
   - Conservative Escalation

**Acceptance Criteria**:
- [ ] 5 patterns with arrow notation (input → transformation → output)
- [ ] Pattern names in Title Case, 2-3 words

---

#### T1.7: Write Examples Section
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write Example 1: Full Repository Surface Scan (basic, no flags)
2. Write Example 2: Structural Audit of Source Directory (--pass structural --batch-size 25)
3. Write Example 3: Infrastructure Cross-Cutting Sweep (--pass cross-cutting --focus infrastructure)
4. Write Example 4: Complete 3-Pass Audit (--pass all, advanced)
5. Each example: fenced code block + 3-4 comment lines explaining behavior

**Acceptance Criteria**:
- [ ] 4 examples progressing simple → complex
- [ ] Each has code block + comment lines
- [ ] Examples match spec §2.8 content

---

#### T1.8: Write Boundaries and Critical Boundaries
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Write "Will:" with 3 positive capabilities
2. Write "Will Not:" with 3 negative constraints
3. Write "CRITICAL BOUNDARIES" section with:
   - Bold STOP directive: **READ-ONLY AUDIT — NO REPOSITORY MODIFICATIONS**
   - "Explicitly Will NOT" list (4 items)
   - "Output" specification (4 output types)
   - "Next Step" recommendation: `/sc:cleanup` → `/sc:test` → `/sc:git`

**Acceptance Criteria**:
- [ ] Will/Will Not each have exactly 3 bullets
- [ ] Critical Boundaries has STOP directive in bold caps
- [ ] Next Step chains to specific /sc:* commands
- [ ] Read-only constraint is unambiguous

---

#### T1.9: Write Shell Preprocessing Context Block
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Add repository context block using `!`cmd`` preprocessing:
   - Total files: `!`git ls-files | wc -l``
   - File breakdown: `!`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15``
   - Repo size: `!`du -sh . --exclude=.git --exclude=node_modules 2>/dev/null``
   - Current branch: `!`git branch --show-current``
   - Last commit: `!`git log --oneline -1``
2. Add target scope block using `$ARGUMENTS`

**Acceptance Criteria**:
- [ ] Shell preprocessing uses correct `!`cmd`` syntax
- [ ] $ARGUMENTS correctly references user-provided target path
- [ ] Preprocessing provides enough context for batch planning

---

#### T1.10: Write repo-inventory.sh Script
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh`

**Steps**:
1. Write file enumeration using `git ls-files` (respects .gitignore)
2. Write exclusion logic for `.git/`, `node_modules/`, build outputs, caches, vendor
3. Write file type distribution calculation
4. Write domain-based grouping (infrastructure, frontend, backend, docs, tests)
5. Write batch creation logic with configurable batch size
6. Write coverage tracking (files_audited / total)
7. Make executable (`chmod +x`)

**Acceptance Criteria**:
- [ ] Uses `git ls-files` for portable, .gitignore-respecting enumeration
- [ ] All exclusion patterns from spec §7.1 are applied
- [ ] Output is machine-parseable (one file per line, grouped by domain)
- [ ] Script is POSIX-compatible (no bash-isms)
- [ ] Script is executable

**Verification**:
```bash
chmod +x .claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh
.claude/skills/sc-cleanup-audit/scripts/repo-inventory.sh . 50
```

---

#### T1.11: SKILL.md Line Count Validation
**Type**: IMPROVEMENT | **Priority**: P2-Medium
**Files**: `.claude/skills/sc-cleanup-audit/SKILL.md`

**Steps**:
1. Count total lines in SKILL.md
2. If >500 lines, identify content to move to supporting files
3. Ensure orchestration logic is in SKILL.md, domain rules are in rules/

**Acceptance Criteria**:
- [ ] SKILL.md is under 500 lines
- [ ] All domain-specific rules are in `rules/` files, not inline

**Verification**:
```bash
wc -l .claude/skills/sc-cleanup-audit/SKILL.md
```

---

## Milestone 2: Rules Engine

**Objective**: Create the 5 rules files that define audit methodology, evidence standards, and per-pass criteria. These are loaded by subagents as supporting files.

**Dependencies**: M1 (SKILL.md references rules files via markdown links)
**Estimated Complexity**: Medium
**Primary Persona**: Analyzer + QA

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| M2-D1 | FEATURE | Pass 1 surface scan rules | Classification taxonomy, verification protocol, output format | `rules/pass1-surface-scan.md` |
| M2-D2 | FEATURE | Pass 2 structural audit rules | 8-field per-file profile, extra rules by file type, failure criterion | `rules/pass2-structural-audit.md` |
| M2-D3 | FEATURE | Pass 3 cross-cutting rules | Comparison methodology, duplication matrix, tiered depth | `rules/pass3-cross-cutting.md` |
| M2-D4 | FEATURE | Universal verification protocol | Evidence requirements per recommendation, cross-reference checklist | `rules/verification-protocol.md` |
| M2-D5 | FEATURE | Dynamic-use checklist | 5 dynamic loading patterns with per-language examples | `rules/dynamic-use-checklist.md` |

### Tasks

#### T2.1: Write Pass 1 Surface Scan Rules
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/rules/pass1-surface-scan.md`

**Steps**:
1. Write goal statement and guiding question ("Is this file junk?")
2. Write 3-tier classification taxonomy table (DELETE/REVIEW/KEEP) from spec §3.1
3. Write verification protocol (4-step: read → grep → check imports → categorize)
4. Write output format template (Safe to Delete, Need Decision, Keep, Add to .gitignore)
5. Write batch size guidance (25-50 normal, 50-100 binary/assets)
6. Write binary asset handling rules (grep-only, no content reading)
7. Add section on what "zero references" means (grep pattern + count + zero-result confirmation)

**Acceptance Criteria**:
- [ ] 3-tier taxonomy matches spec §3.1 exactly
- [ ] Verification protocol has all 4 steps
- [ ] Output format includes all 4 sections (Delete, Decision, Keep, Gitignore)
- [ ] Binary asset rules are explicit
- [ ] Evidence standard for DELETE is clear (grep proof required)

---

#### T2.2: Write Pass 2 Structural Audit Rules
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/rules/pass2-structural-audit.md`

**Steps**:
1. Write goal statement and guiding question ("Is this file in the right place, correctly documented, and structurally sound?")
2. Write 5 finding types table (MISPLACED/STALE/STRUCTURAL ISSUE/BROKEN REFS/VERIFIED OK)
3. Write 4 action recommendations table (KEEP/DELETE/MOVE/FLAG)
4. Write mandatory per-file profile with all 8 fields from spec §3.2
5. Write extra rules by file type (tests, scripts, documentation, config)
6. Write failure criterion: "Reports missing mandatory per-file profiles are FAILED"
7. Write scope limitation: "Only files marked KEEP or REVIEW from Pass 1"
8. Add documentation claim verification rule (verify 3-5 claims per doc file)

**Acceptance Criteria**:
- [ ] All 8 mandatory per-file profile fields present with requirement descriptions
- [ ] Extra rules for 4 file types (tests, scripts, docs, config)
- [ ] Failure criterion is explicit and unambiguous
- [ ] Scope limitation references Pass 1 output

---

#### T2.3: Write Pass 3 Cross-Cutting Rules
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/rules/pass3-cross-cutting.md`

**Steps**:
1. Write goal and guiding question ("Does this file duplicate or conflict with another file elsewhere?")
2. Write extended taxonomy with CONSOLIDATE and BROKEN REF additions
3. Write 7-field per-file profile for Pass 3
4. Write 6 critical differentiators from Pass 2 (compare don't catalog, group audit, duplication matrix, known issues, auto-KEEP, directory-level assessments)
5. Write focus areas list (compose files, configs, root clutter, cross-directory duplication, stale artifacts)
6. Write tiered P3 depth strategy (deep/medium/light by category)
7. Write mandatory duplication matrix requirement with format specification

**Acceptance Criteria**:
- [ ] Extended taxonomy includes CONSOLIDATE and BROKEN REF
- [ ] All 6 differentiators from spec §3.3 are present
- [ ] Duplication matrix is mandatory with explicit format
- [ ] Tiered depth strategy with file count estimates

---

#### T2.4: Write Universal Verification Protocol
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/rules/verification-protocol.md`

**Steps**:
1. Write unified classification taxonomy (priority-ordered, 6 categories) from spec §4
2. Write evidence requirements for each recommendation type from spec §5:
   - DELETE: 4 checklist items
   - KEEP: 5 checklist items
   - CONSOLIDATE: 3 checklist items
   - FLAG: 4 checklist items
   - MOVE: 2 checklist items
3. Write cross-reference checklist (7 reference sources) from spec §5
4. Write documentation claim verification protocol
5. Write 16 reusable cleanup principles from spec §11

**Acceptance Criteria**:
- [ ] All 5 recommendation types have explicit checklist evidence requirements
- [ ] Cross-reference checklist has all 7 source types
- [ ] All 16 cleanup principles are present and ordered by dependency
- [ ] Evidence requirements use checkbox format for verifiability

---

#### T2.5: Write Dynamic-Use Checklist
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/rules/dynamic-use-checklist.md`

**Steps**:
1. Write 5 dynamic loading patterns from spec §5:
   - Environment variable-based module loading
   - String-based import loaders
   - Plugin registries
   - Glob-based file discovery
   - Config-driven loading patterns
2. For each pattern, provide per-language examples (JavaScript, Python, Go, Ruby where applicable)
3. Write instruction: "Check ALL patterns before classifying as DELETE"

**Acceptance Criteria**:
- [ ] All 5 patterns documented with descriptions
- [ ] Per-language examples for at least JavaScript and Python
- [ ] Clear instruction on when to apply (before any DELETE classification)

---

## Milestone 3: Output Templates

**Objective**: Create the 4 report templates and finding profile template that enforce structured, consistent output from all subagents.

**Dependencies**: M1 (SKILL.md references templates)
**Estimated Complexity**: Medium
**Primary Persona**: Scribe + Analyzer

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| M3-D1 | FEATURE | Batch report template | Per-agent output format with all required sections | `templates/batch-report.md` |
| M3-D2 | FEATURE | Pass summary template | Consolidated pass summary with dedup and patterns | `templates/pass-summary.md` |
| M3-D3 | FEATURE | Final report template | Executive summary, action items, discovered issues | `templates/final-report.md` |
| M3-D4 | FEATURE | Finding profile template | Per-file finding profile with all mandatory fields | `templates/finding-profile.md` |

### Tasks

#### T3.1: Write Batch Report Template
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/skills/sc-cleanup-audit/templates/batch-report.md`

**Steps**:
1. Write header section (scope description, pass number, status, files audited, date)
2. Write "Files to DELETE" section with evidence fields
3. Write "Files to CONSOLIDATE" section (Pass 3 only) with overlap quantification
4. Write "Files to MOVE" section with target and refs to update
5. Write "Files to FLAG" section with finding type, issue, required action, verification checklist
6. Write "Broken References Found" section with file:line → missing path format
7. Write "Files to KEEP" section with nature, references, verification notes
8. Write "Remaining / Not Audited" section (mandatory if scope incomplete)
9. Write Summary section with counts
10. Write Notes section for cross-cutting observations

**Acceptance Criteria**:
- [ ] All 8 content sections present (DELETE, CONSOLIDATE, MOVE, FLAG, BROKEN REFS, KEEP, Remaining, Summary)
- [ ] Header has status, files audited count, date
- [ ] Remaining section explicitly marked as mandatory for incomplete scope
- [ ] Template matches spec §8.2 Per-Agent Batch Report format

---

#### T3.2: Write Pass Summary Template
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/templates/pass-summary.md`

**Steps**:
1. Write header (pass number, total batches, total files, date range)
2. Write aggregate summary counts (DELETE/CONSOLIDATE/MOVE/FLAG/KEEP/BROKEN REFS)
3. Write coverage metrics section (files_audited / total = %)
4. Write cross-agent patterns section (systemic findings from multiple batches)
5. Write validation results section (spot-check outcomes)
6. Write deduplication notes (findings appearing in multiple batches)
7. Write quality gate status (pass/fail with evidence)

**Acceptance Criteria**:
- [ ] Coverage metrics are mandatory
- [ ] Cross-agent pattern extraction section present
- [ ] Quality gate status with pass/fail
- [ ] Deduplication notes present

---

#### T3.3: Write Final Report Template
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/templates/final-report.md`

**Steps**:
1. Write Executive Summary section (total files, coverage %, action counts, effort estimate)
2. Write "Action Items by Priority" with 3 subsections:
   - Immediate (safe, no dependencies)
   - Requires Decision (needs human judgment)
   - Requires Code Changes (FLAG items)
3. Write "Cross-Cutting Findings" section for systemic patterns
4. Write "Discovered Issues Registry" as numbered list
5. Write "Audit Methodology" section summarizing what was checked and how
6. Write "Recommendations" section for process improvements

**Acceptance Criteria**:
- [ ] Executive Summary has all 4 required metrics
- [ ] Action items split into 3 priority tiers
- [ ] Discovered Issues Registry is numbered
- [ ] Template matches spec §8.3

---

#### T3.4: Write Finding Profile Template
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/skills/sc-cleanup-audit/templates/finding-profile.md`

**Steps**:
1. Write Pass 2 profile format (8 mandatory fields from spec §3.2):
   - What it does, Nature, References, CI/CD usage, Superseded by/duplicates, Risk notes, Recommendation, Verification notes
2. Write Pass 3 profile format (7 fields from spec §3.3):
   - What it does, Nature, References, Similar files, Superseded?, Currently used?, Recommendation
3. Add clear instructions: "ALL fields are MANDATORY. Reports with missing fields are FAILED."

**Acceptance Criteria**:
- [ ] Pass 2 template has all 8 fields
- [ ] Pass 3 template has all 7 fields
- [ ] Mandatory instruction is explicit

---

## Milestone 4: Subagent Definitions

**Objective**: Create the 5 custom subagent definition files that define specialized worker behaviors for each audit phase.

**Dependencies**: M1 (SKILL.md spawns agents), M2 (agents reference rules for methodology)
**Estimated Complexity**: Medium
**Primary Persona**: Architect + Analyzer

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| M4-D1 | FEATURE | Pass 1 scanner agent | Haiku, read-only, surface scan methodology | `.claude/agents/audit-scanner.md` |
| M4-D2 | FEATURE | Pass 2 analyzer agent | Sonnet, read-only, deep structural profiling | `.claude/agents/audit-analyzer.md` |
| M4-D3 | FEATURE | Pass 3 comparator agent | Sonnet, read-only, cross-cutting comparison | `.claude/agents/audit-comparator.md` |
| M4-D4 | FEATURE | Report consolidator agent | Sonnet, Write-enabled, report merging | `.claude/agents/audit-consolidator.md` |
| M4-D5 | FEATURE | Spot-check validator agent | Sonnet, read-only, finding verification | `.claude/agents/audit-validator.md` |

### Tasks

#### T4.1: Write audit-scanner.md (Pass 1 Worker)
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/agents/audit-scanner.md`

**Steps**:
1. Write frontmatter:
   - `name: audit-scanner`
   - `description: "Fast read-only surface scanner for repository audit Pass 1. Classifies files as DELETE/REVIEW/KEEP with grep evidence."`
   - `tools: Read, Grep, Glob`
   - `model: haiku`
   - `maxTurns: 20`
   - `permissionMode: plan`
2. Write system prompt covering:
   - Role description (read-only surface scanner)
   - Input specification (batch file list)
   - Methodology (read 20-30 lines → grep for references → classify)
   - Classification taxonomy (DELETE/REVIEW/KEEP)
   - Output format (following batch-report template)
   - Safety instruction: "DO NOT modify any file"
   - Incremental save instruction: "Write findings after every 5-10 files"
3. Embed Pass 1 rules inline or reference `rules/pass1-surface-scan.md`

**Acceptance Criteria**:
- [ ] Frontmatter has all required fields
- [ ] `model: haiku` (cost optimization)
- [ ] `tools: Read, Grep, Glob` (read-only enforced)
- [ ] System prompt covers methodology, output format, and safety
- [ ] `maxTurns: 20` prevents runaway

---

#### T4.2: Write audit-analyzer.md (Pass 2 Worker)
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/agents/audit-analyzer.md`

**Steps**:
1. Write frontmatter:
   - `name: audit-analyzer`
   - `description: "Deep structural auditor for repository audit Pass 2. Produces mandatory 8-field per-file profiles with evidence."`
   - `tools: Read, Grep, Glob`
   - `model: sonnet`
   - `maxTurns: 35`
   - `permissionMode: plan`
2. Write system prompt covering:
   - Role (deep structural auditor)
   - Input (batch file list + Pass 1 findings for context)
   - Methodology (full 8-field profile per file)
   - Finding types (MISPLACED/STALE/STRUCTURAL ISSUE/BROKEN REFS/VERIFIED OK)
   - Extra rules by file type (tests, scripts, docs, config)
   - Evidence standard (every KEEP needs citation, every DELETE needs grep proof)
   - Failure criterion: "Reports missing mandatory fields are FAILED"
   - Incremental save instruction

**Acceptance Criteria**:
- [ ] `model: sonnet` (deeper analysis than Pass 1)
- [ ] System prompt requires all 8 profile fields
- [ ] Extra rules for 4 file types are included
- [ ] Failure criterion is stated

---

#### T4.3: Write audit-comparator.md (Pass 3 Worker)
**Type**: FEATURE | **Priority**: P0-Critical
**Files**: `.claude/agents/audit-comparator.md`

**Steps**:
1. Write frontmatter:
   - `name: audit-comparator`
   - `description: "Cross-cutting comparator for repository audit Pass 3. Detects duplication, sprawl, and consolidation opportunities."`
   - `tools: Read, Grep, Glob`
   - `model: sonnet`
   - `maxTurns: 35`
   - `permissionMode: plan`
2. Write system prompt covering:
   - Role (cross-cutting duplication and sprawl detector)
   - Input (batch of similar files grouped by type + Pass 1-2 findings)
   - Methodology (compare files, quantify overlap %, produce duplication matrix)
   - Extended taxonomy (CONSOLIDATE, BROKEN REF additions)
   - 6 critical differentiators from Pass 2
   - Known-issues deduplication instruction
   - Auto-KEEP for previously audited files

**Acceptance Criteria**:
- [ ] CONSOLIDATE classification is defined with overlap quantification requirement
- [ ] Duplication matrix requirement is mandatory
- [ ] Known-issues dedup instruction present
- [ ] 6 differentiators from spec §3.3 are included

---

#### T4.4: Write audit-consolidator.md (Report Merger)
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/agents/audit-consolidator.md`

**Steps**:
1. Write frontmatter:
   - `name: audit-consolidator`
   - `description: "Consolidates audit batch reports into pass summaries and final reports with deduplication."`
   - `tools: Read, Grep, Glob, Write`
   - `model: sonnet`
   - `maxTurns: 40`
   - `permissionMode: plan`
2. Write system prompt covering:
   - Role (report merger and synthesizer)
   - Input (all batch reports for a pass + template)
   - Methodology (merge → deduplicate → extract cross-agent patterns → summarize)
   - Output format (following pass-summary or final-report template)
   - Quality requirements (summary counts, coverage metrics, remaining/not-audited)

**Acceptance Criteria**:
- [ ] `tools` includes `Write` (only agent that can write reports)
- [ ] Deduplication methodology is explicit
- [ ] Cross-agent pattern extraction is required
- [ ] Coverage metrics are mandatory in output

---

#### T4.5: Write audit-validator.md (Quality Checker)
**Type**: FEATURE | **Priority**: P1-High
**Files**: `.claude/agents/audit-validator.md`

**Steps**:
1. Write frontmatter:
   - `name: audit-validator`
   - `description: "Spot-check validator verifying audit finding accuracy by re-testing claims independently."`
   - `tools: Read, Grep, Glob`
   - `model: sonnet`
   - `maxTurns: 25`
   - `permissionMode: plan`
2. Write system prompt covering:
   - Role (independent validator)
   - Input (randomly sampled 5 findings per 50 files)
   - Methodology: re-grep claims, verify file was read, check KEEP/DELETE accuracy
   - Output: validation report with discrepancies flagged
   - Independence instruction: "Do NOT assume prior agent was correct. Verify from scratch."

**Acceptance Criteria**:
- [ ] Sampling rate is explicit (5 per 50 files = 10%)
- [ ] 4 verification checks from spec §10.3 are present
- [ ] Independence instruction prevents confirmation bias

---

## Milestone 5: Framework Integration

**Objective**: Register the new command in SuperClaude's framework files so it appears in routing tables, persona triggers, and command catalogs.

**Dependencies**: M1-M4 complete (command must be fully defined before registration)
**Estimated Complexity**: Low
**Primary Persona**: Architect + Scribe

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| M5-D1 | DOC | COMMANDS.md entry | Command listed with auto-persona, MCP, tools | `COMMANDS.md` (in `~/.claude/` or repo) |
| M5-D2 | DOC | ORCHESTRATOR.md routing entry | Pattern matching and confidence score | `ORCHESTRATOR.md` |
| M5-D3 | DOC | PERSONAS.md trigger updates | New trigger keywords for analyzer persona | `PERSONAS.md` |

### Tasks

#### T5.1: Add COMMANDS.md Entry
**Type**: DOC | **Priority**: P1-High
**Files**: Framework COMMANDS.md

**Steps**:
1. Add entry under "Quality Commands" section:
```markdown
**`/sc:cleanup-audit [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]`**
— Multi-pass read-only repository audit (wave-enabled, complex profile)
- **Auto-Persona**: Analyzer, Architect, DevOps, QA, Refactorer
- **MCP**: Sequential (cross-cutting synthesis), Serena (import chains), Context7 (framework patterns)
- **Tools**: [Read, Grep, Glob, Bash, TodoWrite, Task, Write]
```

**Acceptance Criteria**:
- [ ] Entry follows existing command entry format exactly
- [ ] Listed under correct category (Quality Commands)
- [ ] Auto-Persona, MCP, Tools all specified

---

#### T5.2: Add ORCHESTRATOR.md Routing Entry
**Type**: DOC | **Priority**: P1-High
**Files**: Framework ORCHESTRATOR.md

**Steps**:
1. Add to Master Routing Table:
```markdown
| "cleanup audit" / "repo audit" / "dead code" | complex | quality/maintenance | analyzer + architect + devops + qa + refactorer, --ultrathink, Sequential + Serena + Context7 | 95% |
```
2. Add to Wave-Enabled Commands list if applicable

**Acceptance Criteria**:
- [ ] Routing entry matches table format
- [ ] Confidence score is realistic (95%)
- [ ] Complexity correctly set to "complex"

---

#### T5.3: Update PERSONAS.md Trigger Keywords
**Type**: DOC | **Priority**: P2-Medium
**Files**: Framework PERSONAS.md

**Steps**:
1. Add to analyzer persona triggers: "audit", "cleanup-audit", "dead code", "orphan files", "repo cleanup"
2. Verify these keywords don't conflict with existing persona triggers

**Acceptance Criteria**:
- [ ] New keywords added to analyzer persona
- [ ] No conflicts with existing triggers
- [ ] Keywords are specific enough to avoid false positives

---

## Milestone 6: Validation & Testing

**Objective**: Validate the complete skill package works correctly by testing against real repositories at different scales.

**Dependencies**: M1-M5 complete
**Estimated Complexity**: High
**Primary Persona**: QA + Analyzer

### Deliverables

| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| M6-D1 | TEST | Small-scope validation | Single directory audit completes with valid output | Test results |
| M6-D2 | TEST | Full 3-pass validation | All passes complete with quality gates | Test results |
| M6-D3 | TEST | Output format compliance | All reports match templates | Test results |
| M6-D4 | DOC | Validation report | Documented test results and findings | `.dev/.releases/current/v.1.06-CleanupAudit/validation-report.md` |

### Tasks

#### T6.1: Validate Skill Loading
**Type**: TEST | **Priority**: P0-Critical

**Steps**:
1. Verify skill is discoverable: check `/sc:cleanup-audit` appears in command list
2. Verify frontmatter is parsed correctly
3. Verify `disable-model-invocation: true` prevents auto-triggering
4. Verify `allowed-tools` restriction is enforced
5. Verify shell preprocessing executes correctly

**Acceptance Criteria**:
- [ ] Skill appears in `/` autocomplete
- [ ] Description displays correctly
- [ ] Tool restrictions are active

**Verification**:
```bash
# In Claude Code session:
# Type /sc:cleanup-audit and verify autocomplete shows it
# Check argument-hint displays
```

---

#### T6.2: Test Pass 1 on Small Directory
**Type**: TEST | **Priority**: P0-Critical

**Steps**:
1. Run `/sc:cleanup-audit tests/ --pass surface --batch-size 10`
2. Verify subagent spawning works (audit-scanner launched)
3. Verify batch report is written to `.claude-audit/<session>/`
4. Verify report follows batch-report template
5. Verify every file in scope is classified (DELETE/REVIEW/KEEP)
6. Verify evidence is provided for DELETE recommendations (grep proof)
7. Verify coverage metrics are present

**Acceptance Criteria**:
- [ ] Subagent spawns and completes
- [ ] Report file exists at expected path
- [ ] Report has all required sections
- [ ] 100% file coverage within scope
- [ ] DELETE findings have grep evidence

---

#### T6.3: Test Pass 2 on Small Directory
**Type**: TEST | **Priority**: P1-High

**Steps**:
1. Run `/sc:cleanup-audit tests/ --pass structural --batch-size 10`
2. Verify audit-analyzer agent is spawned (Sonnet model)
3. Verify per-file profiles have all 8 mandatory fields
4. Verify extra rules are applied by file type
5. Verify scope is limited to KEEP/REVIEW from Pass 1 (if prior Pass 1 exists)

**Acceptance Criteria**:
- [ ] All 8 profile fields present per file
- [ ] File type-specific rules applied
- [ ] Report follows template

---

#### T6.4: Test Pass 3 Cross-Cutting
**Type**: TEST | **Priority**: P1-High

**Steps**:
1. Run `/sc:cleanup-audit . --pass cross-cutting --focus infrastructure`
2. Verify audit-comparator agent is spawned
3. Verify duplication matrix is produced
4. Verify overlap percentages are quantified
5. Verify known-issues deduplication works (if prior pass results exist)

**Acceptance Criteria**:
- [ ] Duplication matrix present in output
- [ ] Overlap percentages are numeric (not vague)
- [ ] CONSOLIDATE recommendations have both file paths

---

#### T6.5: Test Quality Gate Enforcement
**Type**: TEST | **Priority**: P1-High

**Steps**:
1. Verify audit-validator is spawned after pass completion
2. Verify spot-check samples are selected (5 per 50)
3. Verify validation report identifies any discrepancies
4. Verify quality gate blocks pass advancement on failure (if applicable)

**Acceptance Criteria**:
- [ ] Validator runs after each pass
- [ ] Validation report exists with spot-check results
- [ ] Discrepancies are clearly flagged

---

#### T6.6: Test Full 3-Pass Audit
**Type**: TEST | **Priority**: P1-High

**Steps**:
1. Run `/sc:cleanup-audit . --pass all --batch-size 25`
2. Verify all 3 passes execute in order
3. Verify quality gates run between passes
4. Verify final consolidated report is produced
5. Verify executive summary has action counts and coverage %
6. Verify incremental saves occurred (check for batch files on disk)
7. Verify progress.json was created and updated

**Acceptance Criteria**:
- [ ] All 3 passes complete
- [ ] Quality gates ran between passes
- [ ] Final report exists with executive summary
- [ ] Batch report files exist on disk (incremental saves worked)
- [ ] progress.json tracks completion state

---

#### T6.7: Test Resume-from-Checkpoint
**Type**: TEST | **Priority**: P2-Medium

**Steps**:
1. Start a multi-batch audit
2. After some batches complete, interrupt the session
3. Re-invoke the same command
4. Verify progress.json is detected
5. Verify completed batches are skipped
6. Verify audit resumes from last incomplete batch

**Acceptance Criteria**:
- [ ] Previous state detected on re-invocation
- [ ] Completed batches not re-processed
- [ ] Audit continues from interruption point

---

#### T6.8: Write Validation Report
**Type**: DOC | **Priority**: P1-High
**Files**: `.dev/.releases/current/v.1.06-CleanupAudit/validation-report.md`

**Steps**:
1. Document results of all test tasks (T6.1-T6.7)
2. Record pass/fail status for each acceptance criterion
3. Document any issues found and resolutions
4. Calculate overall validation score
5. Record coverage metrics and performance observations

**Acceptance Criteria**:
- [ ] All test results documented
- [ ] Issues and resolutions recorded
- [ ] Overall validation score calculated
- [ ] Performance observations noted

---

## Dependency Graph

```
M1 (Foundation)
├── T1.1 Directory Structure
├── T1.2-T1.9 SKILL.md sections (sequential within, parallel possible for independent sections)
└── T1.10 repo-inventory.sh

M2 (Rules) ──depends on──> M1
├── T2.1 Pass 1 rules ─┐
├── T2.2 Pass 2 rules  │ (all parallel)
├── T2.3 Pass 3 rules  │
├── T2.4 Verification  │
└── T2.5 Dynamic-use  ─┘

M3 (Templates) ──depends on──> M1
├── T3.1 Batch report  ─┐
├── T3.2 Pass summary   │ (all parallel)
├── T3.3 Final report   │
└── T3.4 Finding profile─┘

M4 (Agents) ──depends on──> M1, M2
├── T4.1 audit-scanner    ─┐
├── T4.2 audit-analyzer    │ (all parallel)
├── T4.3 audit-comparator  │
├── T4.4 audit-consolidator│
└── T4.5 audit-validator  ─┘

M5 (Integration) ──depends on──> M1, M2, M3, M4
├── T5.1 COMMANDS.md   ─┐
├── T5.2 ORCHESTRATOR.md│ (all parallel)
└── T5.3 PERSONAS.md   ─┘

M6 (Validation) ──depends on──> M5
├── T6.1 Skill loading (first)
├── T6.2 Pass 1 test ──> T6.3 Pass 2 test ──> T6.4 Pass 3 test
├── T6.5 Quality gate test
├── T6.6 Full 3-pass test (depends on T6.2-T6.4)
├── T6.7 Resume test
└── T6.8 Validation report (last)
```

**Parallelization Opportunities**:
- M2 and M3 can run in parallel (both depend only on M1)
- All tasks within M2 are independent (parallel)
- All tasks within M3 are independent (parallel)
- All tasks within M4 are independent (parallel)
- All tasks within M5 are independent (parallel)
- M6 tests are mostly sequential (each pass test builds on the prior)

---

## Risk Register

| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|
| R1 | SKILL.md exceeds 500 line limit | Medium | Low | Move detailed rules to supporting files; T1.11 validates |
| R2 | Subagent model availability (Haiku/Sonnet) | Low | High | Fallback to `inherit` if model unavailable |
| R3 | Concurrent subagent limit causes timeouts | Medium | Medium | Wave sizing limited to 7-8; configurable via --batch-size |
| R4 | Large repos exhaust orchestrator context window | Medium | High | Incremental saves, checkpoint/resume, aggressive compaction |
| R5 | Shell preprocessing fails on non-git repos | Low | Medium | Fallback to `find` if `git ls-files` fails |
| R6 | Subagent output format inconsistency | Medium | Medium | Template enforcement in agent prompts; validator spot-checks |
| R7 | MCP server unavailability during orchestration | Low | Medium | MCP only used in orchestrator Steps 1 and 5; graceful fallback |
| R8 | Token cost overrun on large repos | Medium | Low | Haiku-first, maxTurns limits, configurable batch-size |

---

## Success Criteria

- [ ] Skill invocable via `/sc:cleanup-audit` with correct autocomplete hint
- [ ] Pass 1 spawns Haiku audit-scanner agents in parallel batches
- [ ] Pass 2 spawns Sonnet audit-analyzer agents with mandatory 8-field profiles
- [ ] Pass 3 spawns Sonnet audit-comparator agents producing duplication matrices
- [ ] Quality gates enforce validation between passes
- [ ] Spot-check validator catches deliberate false findings in test
- [ ] Consolidated final report produced with executive summary
- [ ] Incremental saves prevent data loss on session interruption
- [ ] Resume-from-checkpoint works across sessions
- [ ] All output follows templates (verifiable by section headings)
- [ ] Read-only enforcement verified (no file modifications during audit)
- [ ] Framework integration entries in COMMANDS.md, ORCHESTRATOR.md, PERSONAS.md
- [ ] Total SKILL.md under 500 lines

---

## Task Summary Statistics

| Milestone | Tasks | P0-Critical | P1-High | P2-Medium | P3-Low |
|-----------|-------|-------------|---------|-----------|--------|
| M1: Foundation | 11 | 4 | 6 | 1 | 0 |
| M2: Rules | 5 | 4 | 1 | 0 | 0 |
| M3: Templates | 4 | 1 | 3 | 0 | 0 |
| M4: Agents | 5 | 3 | 2 | 0 | 0 |
| M5: Integration | 3 | 0 | 2 | 1 | 0 |
| M6: Validation | 8 | 2 | 4 | 1 | 1 |
| **Total** | **36** | **14** | **18** | **3** | **1** |

**Execution Order**: M1 → (M2 ∥ M3) → M4 → M5 → M6
**Estimated Parallelization Gain**: M2 and M3 in parallel saves ~40% of their combined time.
Within each milestone, parallel tasks save additional ~50-60%.
