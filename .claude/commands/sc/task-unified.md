---
name: task
description: "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation"
category: special
complexity: advanced
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
mcp-servers: [sequential, context7, serena, playwright, magic, morphllm]
personas: [architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer]
version: "2.0.0"
---

# /sc:task - Unified Task Command

## Purpose

A unified command with **orthogonal dimensions** that merges orchestration capabilities with MCP compliance enforcement:

```
/sc:task [operation] --strategy [systematic|agile|enterprise] --compliance [strict|standard|light|exempt]
```

| Dimension | Purpose | Options |
|-----------|---------|---------|
| **Strategy** | HOW to coordinate work | systematic, agile, enterprise, auto |
| **Compliance** | HOW strictly to enforce quality | strict, standard, light, exempt, auto |

**Philosophy**: "Better false positives than false negatives" - when uncertain, escalate to higher compliance tier.

## Triggers

| Trigger Type | Condition | Confidence |
|--------------|-----------|------------|
| **Complexity Score** | Task complexity >0.6 with code modifications | 90% |
| **Multi-file Scope** | Estimated affected files >2 | 85% |
| **Security Domain** | Paths contain `auth/`, `security/`, `crypto/` | 95% |
| **Refactoring Scope** | Keywords: refactor, remediate, multi-file | 90% |

## Usage

```bash
/sc:task [operation] [target] [flags]
```

Key flags: `--strategy`, `--compliance`, `--verify`, `--skip-compliance`, `--force-strict`, `--parallel`, `--delegate`. See protocol skill for full flag reference.

## Classification (MANDATORY FIRST OUTPUT)

**CRITICAL: Classification is TEXT-ONLY. Do NOT invoke ANY tools (Skill, Read, Grep, etc.) to perform classification. Emit the header below based SOLELY on the keyword rules in this section. Tool invocation begins AFTER classification.**

Before ANY other text, emit this exact header:
```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
KEYWORDS: [matched keywords or "none"]
OVERRIDE: [true|false]
RATIONALE: [one-line reason]
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

**Tier rules** (check in priority order; first matching tier wins; check --compliance override first):

1. **STRICT** (Priority 1 — safety-critical):
   - Keywords: security, authentication, authorization, database, migration, refactor, breaking change, encrypt, token, session, oauth
   - Context boosters: >2 estimated files (+0.3), security paths like auth/, security/, crypto/ (+0.4)
   - Compound phrases: "fix security", "add authentication", "update database", "change api"
   - Note: "quick security" → still STRICT (security always wins); "minor auth change" → still STRICT

2. **EXEMPT** (Priority 2 — non-code operations):
   - Keywords: explain, search, commit, push, plan, discuss, brainstorm, what, how, why
   - Context boosters: is_read_only (+0.4), is_git_operation (+0.5), all doc files (+0.5)
   - Patterns: starts with "what/how/why/explain", docs-only paths (*.md, docs/)

3. **LIGHT** (Priority 3 — trivial changes):
   - Keywords: typo, comment, whitespace, lint, docstring, formatting, spacing, minor
   - Context boosters: single file (+0.1), <=50 lines estimated
   - Compound phrases: "quick fix", "minor change", "fix typo", "refactor comment"

4. **STANDARD** (Priority 4 — default development):
   - Keywords: implement, add, create, update, fix, build, modify, change
   - Default tier when no higher-priority tier matches

If confidence <0.70, prompt user: "Override with `--compliance [tier]`"

## Execution

After emitting the classification header as text, proceed based on tier:

- **EXEMPT**: Execute immediately — answer the question or perform the read-only operation. No Skill invocation needed.
- **LIGHT**: Execute the change directly. No Skill invocation needed for trivial changes.
- **STANDARD / STRICT**: Invoke the full protocol for tier-appropriate workflow:
  > Skill sc:task-unified-protocol

## Examples

```bash
# STRICT: security-critical implementation
/sc:task "implement user authentication system" --strategy systematic --compliance strict

# STANDARD: typical feature work
/sc:task "add input validation to user endpoint"

# LIGHT: trivial change
/sc:task "fix typo in error message" --compliance light

# EXEMPT: read-only exploration
/sc:task "explain how the auth middleware works"

# Override: force strict on auto-detected standard
/sc:task "update logging format" --force-strict
```

## Boundaries

**Will:**
- Classify tasks into appropriate compliance tiers with confidence scoring
- Enforce tier-appropriate verification requirements
- Spawn verification agents for STRICT tier tasks
- Support user overrides with documented justification
- Coordinate MCP servers based on tier requirements

**Will Not:**
- Skip safety-critical verification for STRICT tasks
- Apply STRICT overhead to genuinely trivial changes
- Override user's explicit compliance choice
- Proceed with <70% confidence without user confirmation
- Execute unbounded batches (max 15 changes per batch)
- Use deprecated `/sc:task-mcp` (use `--compliance [tier]` instead)
