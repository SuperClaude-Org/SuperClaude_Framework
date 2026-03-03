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

**CRITICAL RULES:**
1. **TEXT-ONLY**: Do NOT invoke ANY tools (Skill, Read, Grep, etc.) for classification. Tool invocation begins AFTER classification.
2. **EXACT FORMAT**: Use the HTML comment block below EXACTLY. Do NOT use `**CLASSIFICATION: ...**` or any other format.
3. **VALID TIERS ONLY**: The ONLY valid TIER values are: `STRICT`, `STANDARD`, `LIGHT`, `EXEMPT`. Values like "ITERATIVE", "SIMPLE", "IMPLEMENT", "COMPLEX" are INVALID and MUST NOT be used.
4. **FIRST OUTPUT**: This header MUST be your very first output, before any other text.

Emit this EXACT header format (replace bracketed values only):
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

## Classification Output Examples

**The ONLY valid tier values are: STRICT, STANDARD, LIGHT, EXEMPT. Do NOT invent other labels (e.g., "ITERATIVE", "IMPLEMENT", "SIMPLE" are INVALID).**

For `/sc:task "fix security vulnerability in auth module"`:
```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: STRICT
CONFIDENCE: 0.95
KEYWORDS: security, vulnerability, auth
OVERRIDE: false
RATIONALE: Security-critical change in authentication module
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

For `/sc:task "explain how the routing middleware works"`:
```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: EXEMPT
CONFIDENCE: 0.92
KEYWORDS: explain, how
OVERRIDE: false
RATIONALE: Read-only explanation request, no code changes
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

For `/sc:task "fix typo in error message"`:
```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: LIGHT
CONFIDENCE: 0.95
KEYWORDS: typo, fix
OVERRIDE: false
RATIONALE: Trivial single-string correction
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

For `/sc:task "add pagination to user list endpoint"`:
```
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: STANDARD
CONFIDENCE: 0.85
KEYWORDS: add, endpoint
OVERRIDE: false
RATIONALE: Typical feature addition, moderate scope
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
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
