# Skill development extraction (custom skills) — Haiku-12

## Sources (read completely)
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-task-unified/SKILL.md`
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-cleanup-audit/SKILL.md`
- `/config/workspace/SuperClaude_Framework/src/superclaude/skills/confidence-check/SKILL.md`

---

## 1) Skill spec file structure (reusable template)

All three skills are specified as a single `SKILL.md` document, typically with **YAML front matter** describing metadata and tool access constraints.

### 1.1 Front matter fields (observed)

**Minimal pattern (from `sc-task-unified`)**:
```yaml
---
name: sc-task-unified
description: Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation. Merges orchestration capabilities with MCP compliance into a single coherent interface.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**High-complexity utility skill pattern (from `sc-cleanup-audit`)**:
```yaml
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
```

**No-tools listed pattern (from `confidence-check`)**:
```yaml
---
name: Confidence Check
description: Pre-implementation confidence assessment (≥90% required). Use before starting any implementation to verify readiness with duplicate check, architecture compliance, official docs verification, OSS references, and root cause identification.
---
```

**Reusable patterns from these fields**
- `name`: user-facing identifier (must be stable; used as the skill/command name).
- `description`: should be explicit about intent + safety constraints + success criteria.
- `allowed-tools`: enforce capability boundaries (e.g., read-only skills should not list `Edit`).
- Optional governance fields to make complex skills safer and more discoverable:
  - `category`, `complexity`
  - `mcp-servers` + `personas` (declares orchestration intent)
  - `argument-hint` (improves invocation ergonomics)

---

## 2) Pattern: tool allowlisting as the primary safety boundary

### 2.1 Principle
Skills explicitly declare which tools can be used. This is a concrete mechanism to keep a skill within scope.

- `sc-task-unified` allows editing and orchestration tools:
  - Quote:
    > `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task`

- `cleanup-audit` is designed for a controlled shell subset and read-only repo behavior:
  - Quote:
    > `allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write`

**Reusable implementation idea**: For safety-critical skills, restrict Bash to specific command families (as shown by `Bash(git *)`, `Bash(wc *)`, etc.). For audit/report-only skills, omit `Edit` and explicitly scope `Write` output to a dedicated directory.

---

## 3) Pattern: mandatory machine-readable headers (telemetry & automation)

`sc-task-unified` hard-requires a machine-readable header *as the first output*, regardless of whether the skill will ask clarifying questions.

### 3.1 The exact header format (required)
Quote:
> **"⚠️ MANDATORY FIRST OUTPUT**: You MUST output the classification header block below as your VERY FIRST output, before ANY text, questions, or analysis. This is NON-NEGOTIABLE for telemetry."*

Exact block:
```md
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
KEYWORDS: [comma-separated keywords or "none"]
OVERRIDE: [true|false]
RATIONALE: [one-line reason]
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

### 3.2 Behavioral rules for mandatory headers
Quote (rules list):
> "1. Output this header IMMEDIATELY as your first action"
> "2. Output it BEFORE asking clarifying questions"
> "3. Output it BEFORE any explanations or analysis"
> "4. Output it even if you will ask questions afterward"
> "5. Use the HTML comment wrapper for machine parsing"
> "6. Never skip this header - it enables A/B testing and telemetry"

**Reusable pattern**: If your skill needs structured automation (classification, routing, validation gates), define a **machine-parseable header** that is always first. Use an HTML comment wrapper for robust parsing.

---

## 4) Pattern: tiering / compliance classification to scale process by risk

`sc-task-unified` encodes a full compliance tiering system and a deterministic priority order:

### 4.1 Tier priority
Quote:
> "Classify task into compliance tier using priority order: STRICT > EXEMPT > LIGHT > STANDARD"

### 4.2 Tier definitions and triggers (quoted)

**STRICT** (Priority 1):
- Quote:
  > "Security, data integrity, system-wide changes"
- Quote (keywords):
  > "authentication, database, migration, refactor, breaking change, security, encrypt, token, session, oauth"
- Quote (context/compound phrases):
  > "Context: >2 files, security paths, API contracts"
  > "Compound phrases: \"fix security\", \"add authentication\", \"update database\", \"change api\""

**EXEMPT** (Priority 2):
- Quote:
  > "Read-only, documentation, git operations"
- Quote (patterns):
  > "Patterns: \"^what (is|are|does)\", \"^how (do|does|can|should)\", \"^explain\""

**LIGHT** (Priority 3):
- Quote:
  > "Trivial changes, formatting"
- Quote:
  > "Context: <=2 files, <=50 lines"
- Quote (compound phrases):
  > "\"quick fix\", \"minor change\", \"fix typo\", \"refactor comment\""

**STANDARD** (Priority 4):
- Quote:
  > "Default for typical development"

### 4.3 Human-readable tier display pattern
After the mandatory header, `sc-task-unified` specifies a compact explanation block:
```md
**Tier: STANDARD** [████████░░] 80%

Classified as STANDARD:
- Keywords matched: add, implement
- Confidence score: 0.78
- Considered alternatives: STRICT (0.35)
```

Low-confidence UX requirement:
- Quote:
  > "If confidence <70%, add prompt: \"⚠️ Low confidence. Override with: `--compliance [strict|standard|light|exempt]`\""

**Reusable pattern**: Define *both* machine-readable output (for tooling/telemetry) and a human-friendly explanation (for trust and override workflows).

---

## 5) Pattern: explicit execution flows by complexity tier

`sc-task-unified` prescribes tier-specific workflows. This is an explicit skill authoring pattern: **write the skill as a state machine**.

### 5.1 STRICT execution workflow (quoted steps)
Quote:
> "STRICT Execution:"
> "1. Activate project (mcp__serena__activate_project)"
> "2. Verify git working directory clean (git status)"
> "3. Load codebase context (codebase-retrieval)"
> "4. Check relevant memories (list_memories -> read_memory)"
> "5. Identify all affected files and test files"
> "6. Make changes with full checklist"
> "7. Identify all files that import changed code"
> "8. Update all affected files"
> "9. Spawn verification agent (quality-engineer)"
> "10. Run comprehensive tests: `pytest [path] -v`"
> "11. Answer adversarial questions"

### 5.2 STANDARD / LIGHT / EXEMPT execution workflow (quoted)
Quote:
> "STANDARD Execution:"
> "1. Load context via codebase-retrieval"
> "2. Search downstream impacts (find_referencing_symbols OR grep)"
> "3. Make changes"
> "4. Run affected tests OR document manual verification"
> "5. Verify basic functionality"

Quote:
> "LIGHT Execution:"
> "1. Quick scope check (files/lines within bounds)"
> "2. Make changes"
> "3. Quick sanity check (syntax valid, no obvious errors)"
> "4. Proceed with judgment"

Quote:
> "EXEMPT Execution:"
> "1. Execute immediately"
> "2. No verification overhead"

**Reusable pattern**: For custom skills with varied risk profiles, encode explicit flowcharts per tier and couple them to tool availability + verification gates.

---

## 6) Pattern: verification routing, plus path-based overrides

`sc-task-unified` includes a verification table and *override rules* that supersede tier selection.

### 6.1 Verification routing table (exact)
```md
| Compliance Tier | Verification Method | Token Cost | Timeout |
|-----------------|---------------------|------------|---------|
| STRICT | Sub-agent (quality-engineer) | 3-5K | 60s |
| STANDARD | Direct test execution | 300-500 | 30s |
| LIGHT | Skip verification | 0 | 0s |
| EXEMPT | Skip verification | 0 | 0s |
```

### 6.2 Critical path overrides (quoted)
Quote:
> "Critical Path Override: Paths matching `auth/`, `security/`, `crypto/`, `models/`, `migrations/` always trigger CRITICAL verification regardless of compliance tier."

Quote:
> "Trivial Path Override: Paths matching `*.md`, `docs/`, `*test*.py` may skip verification."

**Reusable pattern**: Encode *tier-level* verification and *path-level* overrides. This helps custom skills remain safe even when classification is imperfect.

---

## 7) Pattern: MCP integration declared as part of the skill contract

### 7.1 Required servers by tier (sc-task-unified)
Quote:
> "Required Servers by Tier:"
> "- STRICT: Sequential, Serena (fallback not allowed)"
> "- STANDARD: Sequential, Context7 (fallback allowed)"
> "- LIGHT: None required (fallback allowed)"
> "- EXEMPT: None required"

### 7.2 Circuit breaker behavior (sc-task-unified)
Quote:
> "If required servers unavailable for STRICT tier, block task execution"

### 7.3 MCP role partitioning (cleanup-audit)
`cleanup-audit` declares MCP usage *and* a critical operational limitation about subagents:

Quote:
> "MCP Constraint: MCP tools are unavailable to background subagents — all MCP-dependent work (ultrathink synthesis, import chain tracing) executes in the orchestrator only"

**Reusable pattern**:
- Declare MCP server dependencies explicitly.
- State fallback policy per tier.
- If using subagents, explicitly document which work must remain in the orchestrator due to tool availability constraints.

---

## 8) Pattern: orchestration & delegation (fan-out/fan-in)

`cleanup-audit` is a full example of an orchestrated, high-complexity skill with batching, specialized subagents, checkpointing, and consolidation.

### 8.1 Multi-pass “pipeline” design
Quote:
> "Multi-pass read-only repository audit"

Quote (pass selection):
> "--pass: Audit pass to run (`surface` = Pass 1, `structural` = Pass 2, `cross-cutting` = Pass 3, `all` = sequential 3-pass)"

### 8.2 Behavioral flow (the five-stage orchestrator loop)
Quote:
> "1. **Discover**: Enumerate repository files via shell preprocessing and `repo-inventory.sh`. Build file inventory with domain grouping, type distribution, and batch assignments. Compute total scope and coverage targets."
> "2. **Configure**: Parse `$ARGUMENTS` for pass selection and focus area. Load pass-specific rules from `rules/` supporting files. Create TodoWrite tasks for each batch. Initialize output directory at `.claude-audit/`."
> "3. **Orchestrate**: Spawn parallel subagents via Task tool in waves of 7-8 concurrent agents. Pass 1 uses `audit-scanner` (Haiku), Pass 2 uses `audit-analyzer` (Sonnet), Pass 3 uses `audit-comparator` (Sonnet). Each agent writes batch reports incrementally to disk. Track progress via TodoWrite."
> "4. **Validate**: Spawn `audit-validator` for 10% spot-check sampling (5 findings per 50 files). Verify grep claims match actual results. Enforce quality gates: all batch reports must have required sections and mandatory per-file profiles. Failed reports trigger regeneration."
> "5. **Report**: Spawn `audit-consolidator` to merge batch reports into pass summaries. For `--pass all`, produce final report with executive summary, prioritized action items, cross-cutting findings, and discovered issues registry. Apply ultrathink synthesis for cross-pass pattern extraction."

### 8.3 Cost-aware model routing (Haiku-first)
Quote:
> "Haiku-first cost optimization: Pass 1 uses Haiku agents for 50-70% cost reduction; Sonnet reserved for deep analysis in Passes 2-3"

### 8.4 Evidence gates as a design primitive
Quote:
> "Evidence-gated classification: Every DELETE requires grep proof; every KEEP requires reference citation; every CONSOLIDATE requires overlap quantification"

### 8.5 Checkpointing/resumability
Quote:
> "Incremental checkpointing: Agents save after every 5-10 files; progress.json enables resume-from-checkpoint on session interruption"

### 8.6 Conservative escalation (avoid false deletions)
Quote:
> "Conservative escalation: When uncertain, agents classify as REVIEW/FLAG rather than DELETE — false negatives are cheaper than false positives"

### 8.7 Fan-out / fan-in as the default scaling architecture
Quote:
> "Fan-out/fan-in orchestration: Orchestrator divides work → spawns N parallel agents → agents write to disk → orchestrator reads and merges"

**Reusable pattern**: For complex custom skills, explicitly specify:
- batching strategy (`--batch-size`), concurrency strategy (waves), agent roles
- what each role outputs and where
- validation/spot-check stage with objective criteria
- consolidation stage (merge outputs) and final report structure

---

## 9) Pattern: explicit boundaries (“will” vs “will not”) and critical constraints

Both `sc-task-unified` and `cleanup-audit` define boundaries. `cleanup-audit` is especially explicit.

### 9.1 “Will / Will Not” contract sections

`sc-task-unified` boundaries (quoted):
- Will:
  > "Classify tasks into appropriate compliance tiers"
  > "Enforce tier-appropriate verification requirements"
  > "Provide confidence scoring with rationale"
  > "Track feedback for continuous calibration"
  > "Support user overrides with justification"
- Will Not:
  > "Skip safety-critical verification for STRICT tasks"
  > "Apply STRICT overhead to genuinely trivial changes"
  > "Override user's explicit compliance choice"
  > "Proceed with <70% confidence without user confirmation"

`cleanup-audit` boundaries (quoted):
- Will Not:
  > "Modify, delete, move, or rename any repository file during the audit"
  > "Make assumptions from filenames alone — every classification requires reading content and tracing references"
  > "Mark files as DELETE without grep proof of zero references and confirmed absence of dynamic loading"

### 9.2 “CRITICAL BOUNDARIES” for read-only skills
Quote:
> "READ-ONLY AUDIT — NO REPOSITORY MODIFICATIONS"

Quote (explicitly will NOT):
> "Edit, delete, move, or rename any existing repository file"
> "Execute cleanup recommendations — human review gate is mandatory"
> "Modify CI/CD pipelines, configs, or any operational infrastructure"
> "Make speculative deletions based on filename patterns without evidence"

**Reusable pattern**: If a skill is read-only, place a prominent critical section stating that no repository modifications are allowed and that outputs are written only to a constrained directory.

---

## 10) Pattern: define outputs and restrict writes to a known directory

`cleanup-audit` restricts outputs to `.claude-audit/`.

Quote:
> "Write: Report generation restricted to `.claude-audit/` output directory — batch reports, pass summaries, final report, progress tracking files"

Quote:
> "Output: Audit reports written to `.claude-audit/` directory only:"
> "- Per-batch reports (one per agent invocation)"
> "- Per-pass summary reports (consolidated findings)"
> "- Final report (executive summary + prioritized actions)"
> "- progress.json (checkpoint state for resume capability)"

**Reusable pattern**: For any skill that writes files, define:
- a single output root directory
- a list of expected artifacts (for predictability)
- the rule that non-output directories are not modified

---

## 11) Pattern: argument design for skills (flags, defaults, discoverability)

`cleanup-audit` demonstrates a strong CLI-like interface design:
- single positional scope argument: `target-path` with `.` default
- enums via flags: `--pass surface|structural|cross-cutting|all`
- tunable `--batch-size`
- domain filters via `--focus infrastructure|frontend|backend|all`

Quote (usage line):
```md
/sc:cleanup-audit [target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]
```

`sc-task-unified` demonstrates override flags and “escape hatch” design:
```bash
/sc:task-unified [description] --compliance strict
/sc:task-unified [description] --skip-compliance
/sc:task-unified [description] --verify auto
```

**Reusable patterns**:
- Provide explicit enumerated values in usage docs.
- Provide safe defaults.
- Include override/escape hatch flags, but document when they should be used.

---

## 12) Pattern: embed “repository context” probes for audit-style skills

`cleanup-audit` includes a “Repository Context” section with shell probes. (These appear as inline command expansions.)

Quotes:
> "Total files: !`git ls-files | wc -l`"
> "File breakdown: !`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15`"
> "Repo size: !`du -sh . --exclude=.git --exclude=node_modules 2>/dev/null`"
> "Current branch: !`git branch --show-current`"
> "Last commit: !`git log --oneline -1`"

Also “Target Scope” probes:
> "Files in scope: !`find ${0:-.} -type f -not -path '*/.git/*' -not -path '*/node_modules/*' | wc -l`"

**Reusable pattern**: Audit/report skills can include a standard “context snapshot” prelude so the final report is anchored in measurable repo state.

---

## 13) Pattern: pre-implementation gating as a standalone skill (confidence-check)

The `confidence-check` skill is a reusable “pre-flight checklist” intended to run **before** implementation.

### 13.1 Hard threshold rule
Quote:
> "Requirement: ≥90% confidence to proceed with implementation."

### 13.2 Scoring rubric (weights and checks)
Quote:
> "Calculate confidence score (0.0 - 1.0) based on 5 checks:"

Weights and checks (quoted headings):
- "### 1. No Duplicate Implementations? (25%)"
- "### 2. Architecture Compliance? (25%)"
- "### 3. Official Documentation Verified? (20%)"
- "### 4. Working OSS Implementations Referenced? (15%)"
- "### 5. Root Cause Identified? (15%)"

Confidence computation (exact):
```md
Total = Check1 (25%) + Check2 (25%) + Check3 (20%) + Check4 (15%) + Check5 (15%)

If Total >= 0.90:  ✅ Proceed with implementation
If Total >= 0.70:  ⚠️  Present alternatives, ask questions
If Total < 0.70:   ❌ STOP - Request more context
```

### 13.3 Tool guidance embedded in the rubric
Duplicate search suggests codebase discovery tooling:
```bash
# Use Grep to search for similar functions
# Use Glob to find related modules
```

Architecture compliance requires reading local governance docs:
- Quote:
  > "Read `CLAUDE.md`, `PLANNING.md`"

Official docs verification suggests MCP usage:
- Quote:
  > "Use Context7 MCP for official docs"
  > "Use WebFetch for documentation URLs"
  > "Verify API compatibility"

OSS reference suggests web search:
- Quote:
  > "Use Tavily MCP or WebSearch"
  > "Search GitHub for examples"

Root cause requires evidence:
- Quote:
  > "Analyze error messages"
  > "Check logs and stack traces"
  > "Identify underlying issue"

### 13.4 Output format standardization
Exact output format:
```md
📋 Confidence Checks:
   ✅ No duplicate implementations found
   ✅ Uses existing tech stack
   ✅ Official documentation verified
   ✅ Working OSS implementation found
   ✅ Root cause identified

📊 Confidence: 1.00 (100%)
✅ High confidence - Proceeding to implementation
```

### 13.5 “Implementation details” references (skill-to-code linkage)
Quote:
> "The TypeScript implementation is available in `confidence.ts` for reference, containing:"
> "- `confidenceCheck(context)` - Main assessment function"
> "- Detailed check implementations"
> "- Context interface definitions"

**Reusable pattern**: For complex behaviors, document (a) the rubric and (b) the canonical code reference (e.g., `.ts`/`.py`) that implements it.

---

## 14) Pattern: examples as executable “golden paths”

Both `sc-task-unified` and `cleanup-audit` provide example invocations tied to their behavior.

Examples from `sc-task-unified`:
```md
/sc:task "implement user authentication with JWT"

-> Classified as STRICT (security domain, authentication keyword)
-> Full 6-category checklist enforced
-> Verification agent spawned
-> Adversarial questions answered
```

```md
/sc:task "fix typo in README"

-> Classified as LIGHT (trivial keyword, documentation path)
-> Quick sanity check only
-> No verification delay
```

Examples from `cleanup-audit`:
```md
/sc:cleanup-audit src/ --pass structural --batch-size 25
```

**Reusable pattern**: Include at least one example per primary mode/flag combination, and include the expected behavioral outcome after the command.

---

## 15) Complexity-level patterns (how to design skills that scale)

### 15.1 LIGHT / EXEMPT skills (low process overhead)
Derived from `sc-task-unified`:
- LIGHT is constrained by scope:
  - Quote: "Context: <=2 files, <=50 lines"
- EXEMPT is designed for read-only/no-verification interactions.

**Design recipe**:
- Minimal toolset (often `Read`, `Grep`, `Glob`)
- Minimal output structure
- Minimal/no verification gates

### 15.2 STANDARD skills (default development)
Derived from `sc-task-unified` STANDARD execution:
- Must load context before editing:
  - Quote: "Load context via codebase-retrieval"
- Must check downstream impacts:
  - Quote: "Search downstream impacts (find_referencing_symbols OR grep)"
- Must test or document verification.

**Design recipe**:
- Declarative “execution phase” steps
- At least one validation step
- Clear stopping conditions

### 15.3 STRICT skills (safety-critical)
Derived from `sc-task-unified` STRICT workflow and server requirements:
- Must validate git state, load context, check memories, update imports, spawn verification agent, run comprehensive tests.
- Must not proceed without required MCP servers.

**Design recipe**:
- Deterministic checklist
- Hard gates when prerequisites not met
- Explicit verification routing table

### 15.4 High-complexity orchestrators (batching + subagents)
Derived from `cleanup-audit`:
- Multi-pass pipeline
- Wave-based parallel Task usage
- Checkpointing to disk
- Validator/consolidator roles
- Evidence-gated findings

**Design recipe**:
- Fan-out/fan-in architecture
- Batch size knobs
- Dedicated output directory with resumability artifacts
- Quality gates + sampling

---

## 16) Summary: skill-authoring checklist (extracted)

When developing a custom skill, these docs collectively imply the following reusable checklist:

1. **Define front matter**: `name`, `description`, `allowed-tools`; optionally add `complexity`, `mcp-servers`, `personas`, and `argument-hint`.
2. **Constrain tools** (allowlist) to enforce scope and safety.
3. If automation/telemetry matters, add a **mandatory machine-readable header** as the very first output.
4. If the skill supports varied risk levels, define a **tier system** + priority order + explicit triggers.
5. Write an explicit **behavioral flow/state machine** (Discover → Configure → Orchestrate → Validate → Report is a proven pattern for audits).
6. Provide a **verification routing table**; add **path overrides** for critical/trivial domains.
7. Document **boundaries** (“Will / Will Not”) and add **CRITICAL BOUNDARIES** for read-only skills.
8. Provide **example invocations** with expected outcomes.
9. If orchestration is involved, include **batching**, **checkpointing**, **spot-check validation**, and **consolidation** steps.
10. If the skill is a pre-flight gate, define a **scoring rubric**, a **hard threshold**, and a standard **output format**, and link to the canonical implementation (e.g., `confidence.ts`).
