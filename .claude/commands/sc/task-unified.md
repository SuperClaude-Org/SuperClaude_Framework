---
name: task
description: "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation"
category: special
complexity: advanced
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

### Auto-Activation Patterns

| Trigger Type | Condition | Confidence |
|--------------|-----------|------------|
| **Complexity Score** | Task complexity >0.6 with code modifications | 90% |
| **Multi-file Scope** | Estimated affected files >2 | 85% |
| **Security Domain** | Paths contain `auth/`, `security/`, `crypto/` | 95% |
| **Refactoring Scope** | Keywords: refactor, remediate, multi-file | 90% |
| **Test Remediation** | Keywords: fix tests, test failures | 88% |

### Context Signals

The command should be suggested when:
- User describes a multi-step implementation task
- Task involves code modifications with downstream impacts
- Security or data integrity domains are involved
- User explicitly requests compliance workflow

## Usage

```bash
/sc:task [operation] [target] [flags]
```

### Strategy Flags (Orchestration Dimension)

| Flag | Description | Use Case |
|------|-------------|----------|
| `--strategy systematic` | Comprehensive, methodical execution | Large features, multi-domain work |
| `--strategy agile` | Iterative, sprint-oriented execution | Feature backlog, incremental delivery |
| `--strategy enterprise` | Governance-focused, compliance-heavy | Regulated environments, audit trails |
| `--strategy auto` | Auto-detect based on scope (default) | Most tasks |

### Compliance Flags (Quality Dimension)

| Flag | Description | Use Case |
|------|-------------|----------|
| `--compliance strict` | Full MCP workflow enforcement | Multi-file, security, refactoring |
| `--compliance standard` | Core rules enforcement | Single-file code changes |
| `--compliance light` | Awareness only | Minor fixes, formatting |
| `--compliance exempt` | No enforcement | Questions, exploration, docs |
| `--compliance auto` | Auto-detect based on task (default) | Most tasks |

### Execution Control Flags

| Flag | Description |
|------|-------------|
| `--skip-compliance` | Escape hatch - skip all compliance enforcement |
| `--force-strict` | Override auto-detection to STRICT |
| `--parallel` | Enable parallel sub-agent execution |
| `--delegate` | Enable sub-agent delegation |
| `--reason "..."` | Required justification for tier override |

### Verification Flags

| Flag | Description |
|------|-------------|
| `--verify critical` | Full sub-agent verification |
| `--verify standard` | Direct test execution only |
| `--verify skip` | Skip verification (use with caution) |
| `--verify auto` | Auto-select based on compliance tier (default) |

## Behavioral Summary

Automatically classifies tasks into 4 compliance tiers (STRICT/STANDARD/LIGHT/EXEMPT) using keyword detection, compound phrase analysis, and context boosters, then enforces tier-appropriate verification checklists. STRICT tier requires full pre-work context loading, downstream impact analysis, verification agent spawning, and adversarial review. STANDARD enforces core rules with manual verification acceptable. LIGHT and EXEMPT minimize or eliminate process overhead for trivial and read-only tasks respectively.

## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:task-unified-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.

## Examples

### Systematic Feature Implementation
```bash
/sc:task "implement user authentication system" --strategy systematic --compliance strict
# Auto-detects: STRICT (authentication keyword, multi-file expected)
# Activates: architect, security, backend personas
# Enforces: Full checklist, verification agent, adversarial review
```

### Standard Code Update
```bash
/sc:task "add input validation to user endpoint"
# Auto-detects: STANDARD (add keyword, single component)
# Enforces: Core rules, basic validation
```

### Quick Fix
```bash
/sc:task "fix typo in error message" --compliance light
# Explicit LIGHT tier
# Enforces: Awareness only, proceed with judgment
```

### Exploration
```bash
/sc:task "explain how the auth middleware works"
# Auto-detects: EXEMPT (explain keyword, read-only)
# No enforcement, proceeds normally
```

### Override Examples
```bash
/sc:task "update logging format" --force-strict
# Forces STRICT even if auto-detected as STANDARD

/sc:task "experimental change" --skip-compliance
# Skips all compliance enforcement (escape hatch)
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

## Migration from Legacy Commands

| Old Command | New Equivalent |
|-------------|----------------|
| `/sc:task create "feature" --strategy systematic` | `/sc:task "feature" --strategy systematic --compliance auto` |
| `/sc:task-mcp "fix tests" --tier strict` | `/sc:task "fix tests" --compliance strict` |

`/sc:task-mcp` is deprecated. Use `/sc:task --compliance [tier]` instead.
