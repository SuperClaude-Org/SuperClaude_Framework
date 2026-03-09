# Auggie MCP Framework-Wide Integration — Wave 1 Consolidated Results

> **Generated**: 2026-02-20
> **Phase Coverage**: Phase 0 (Backlog Alignment) + Phase 1 (Existing Uses) + Phase 2 (New Candidates)
> **Agents Executed**: 7 parallel agents

---

## Phase 0: Backlog Alignment Summary

**Net new work**: ~87% of Phase 1-4 work is genuinely new.

| Metric | Value |
|--------|-------|
| Backlog eliminates directly | ~5% |
| Backlog accelerates (templates/patterns) | ~8% |
| Genuinely new analysis | ~87% |

**Key reusable assets from v1.2 backlog**:
- Circuit breaker configuration template (3 failures → OPEN, 30s timeout)
- "Preferred not required" progressive enhancement principle
- Degradation feedback system pattern
- M1-foundation.md as framework-wide MCP onboarding checklist
- `/sc:analyze` proposal can be directly incorporated into Phase 3

---

## Phase 1: Existing Auggie MCP Uses Analysis

### Common Findings Across All 3 Components

All three components (`task-unified.md`, `task-mcp.md`, `sc-task-unified/SKILL.md`) share **identical defects**:

| Defect | Severity | Detail |
|--------|----------|--------|
| Wrong tool name | CRITICAL | Uses `codebase-retrieval` instead of `mcp__auggie-mcp__codebase-retrieval` |
| Missing `directory_path` | CRITICAL | Required parameter never mentioned |
| Missing `information_request` | HIGH | No query guidance provided |
| Not in MCP frontmatter | HIGH | `auggie-mcp` absent from `mcp-servers:` |
| No fallback behavior | MEDIUM | No degradation path when Auggie unavailable |
| Fabricated syntax | MEDIUM | `codebase-retrieval/view` on task-unified L170 doesn't exist |

### Consensus Top 3 Improvements (All Components Agree)

| Priority | Improvement | Composite Score Range | All 3 Agree? |
|----------|------------|----------------------|---------------|
| 1 | Fix tool name + add required parameters | 8.75-9.30 | YES |
| 2 | Add `auggie-mcp` to MCP frontmatter | 8.55 | YES |
| 3 | Add fallback/circuit breaker OR query templates | 7.40-7.60 | Split (resilience vs precision) |

**Note**: `task-mcp.md` is **deprecated** (deprecated_by: task-unified). Fixes should prioritize `task-unified.md` and `SKILL.md`.

---

## Phase 2: New Auggie MCP Candidate Evaluation

### Commands Evaluation (29 commands assessed)

#### HIGH Benefit (9 commands)

| Rank | Command | Current MCP Servers | Integration Mode | Key Rationale |
|------|---------|-------------------|-----------------|---------------|
| 1 | `analyze` | [] (empty!) | MANDATORY | Core semantic search use case; v1.2 backlog target |
| 2 | `troubleshoot` | [] (empty!) | MANDATORY | Root cause analysis requires semantic code tracing |
| 3 | `cleanup` | [sequential, context7] | MANDATORY | Dead code detection is a semantic problem |
| 4 | `cleanup-audit` | [sequential, serena, context7] | PREFERRED | Enhances existing 3-pass pipeline |
| 5 | `implement` | [context7, sequential, magic, playwright] | PREFERRED | Finding integration points + existing patterns |
| 6 | `improve` | [sequential, context7] | PREFERRED | Dependency-aware improvement discovery |
| 7 | `explain` | [sequential, context7] | PREFERRED | System-level context for explanations |
| 8 | `document` | [] (empty!) | PREFERRED | Documentation accuracy requires code understanding |
| 9 | `design` | [] (empty!) | PREFERRED | Architecture design needs existing system map |

**Priority insight**: Commands with **zero MCP servers** AND **high benefit** (troubleshoot, document, design) represent the largest capability gaps.

#### MEDIUM Benefit (9 commands)

estimate, index, test, workflow, task, spawn, brainstorm, spec-panel, roadmap

#### LOW/NO Benefit (11 commands)

build, select-tool, pm, review-translation, research, recommend, reflect, help, git, load, save

---

### Agents Evaluation (25 agents assessed)

#### HIGH Benefit (9 agents)

| Rank | Agent | Key Rationale |
|------|-------|---------------|
| 1 | audit-analyzer | Deep structural auditing requires semantic file understanding |
| 2 | audit-comparator | Cross-cutting duplication detection is inherently semantic |
| 3 | audit-scanner | Dynamic loading pattern detection exceeds grep capability |
| 4 | audit-validator | Independent verification needs different search approach |
| 5 | root-cause-analyst | Bug tracing requires semantic code path understanding |
| 6 | refactoring-expert | Duplication detection + coupling analysis are semantic |
| 7 | security-engineer | Finding auth flows, data paths across inconsistent naming |
| 8 | system-architect | Dependency mapping + component boundary analysis |
| 9 | repo-index | Entire purpose is codebase understanding |

**Priority insight**: The 5 audit agents are highest ROI since they are purpose-built for codebase analysis.

#### MEDIUM Benefit (9 agents)

backend-architect, performance-engineer, quality-engineer, python-expert, frontend-architect, devops-architect, audit-consolidator, pm-agent, self-review

#### LOW/NO Benefit (7 agents)

technical-writer, learning-guide, socratic-mentor, requirements-analyst, deep-research, deep-research-agent, business-panel-experts

---

### Skills Evaluation (5 skills assessed)

| Skill | Benefit | Key Rationale |
|-------|---------|---------------|
| sc-cleanup-audit | **HIGH** | Reduces false DELETE; enables semantic duplicate detection; catches dynamic loading |
| confidence-check | **HIGH** | Check 1 (duplicate detection, 25% of score) needs semantic search for functional equivalents |
| sc-task-unified | **MEDIUM** | Already references tool; needs concrete query patterns |
| sc-roadmap | **MEDIUM** | Replaces `Files_Affected: TBD` with actual paths |
| sc-validate-tests | **NO BENEFIT** | Pure YAML rules engine; no codebase search involved |

---

## Validated Candidate List for Phase 3

### Tier 1: Implement First (Highest ROI)

| Component Type | Component | Benefit | Priority Rationale |
|---------------|-----------|---------|-------------------|
| Command | `analyze` | HIGH/MANDATORY | v1.2 backlog pre-completed; zero MCP servers |
| Command | `troubleshoot` | HIGH/MANDATORY | Zero MCP servers; largest capability gap |
| Command | `design` | HIGH/PREFERRED | Zero MCP servers; architecture needs codebase map |
| Command | `document` | HIGH/PREFERRED | Zero MCP servers; docs need code understanding |
| Command | `cleanup` | HIGH/MANDATORY | Dead code = semantic problem |
| Skill | confidence-check | HIGH/PREFERRED | 25% of score depends on duplicate detection |
| Skill | sc-cleanup-audit | HIGH/PREFERRED | Enhances multi-pass audit pipeline |
| Existing | task-unified.md | FIX | Correct tool name, params, frontmatter, fallback |
| Existing | sc-task-unified SKILL | FIX | Same fixes as command counterpart |

### Tier 2: Implement Next

| Component Type | Component | Benefit |
|---------------|-----------|---------|
| Command | cleanup-audit | HIGH/PREFERRED |
| Command | implement | HIGH/PREFERRED |
| Command | improve | HIGH/PREFERRED |
| Command | explain | HIGH/PREFERRED |
| Agent | audit-analyzer | HIGH |
| Agent | audit-comparator | HIGH |
| Agent | audit-scanner | HIGH |
| Agent | audit-validator | HIGH |
| Agent | root-cause-analyst | HIGH |
| Agent | refactoring-expert | HIGH |
| Agent | security-engineer | HIGH |
| Agent | system-architect | HIGH |
| Agent | repo-index | HIGH |

### Tier 3: Optional Enhancements

All MEDIUM candidates (9 commands, 9 agents, 2 skills) — implement as progressive enhancement with optional/preferred status.

### Excluded (No Implementation)

- 11 LOW/NO commands, 7 LOW/NO agents, 1 NO skill (sc-validate-tests)

---

## Cross-Cutting Architecture Decisions

### A1: Integration Pattern

**Auggie for discovery → Grep for verification → Read for inspection.**

This creates a funnel: semantic search narrows the space, keyword search confirms specifics, file reading provides full context.

### A2: Progressive Enhancement

All integrations MUST follow: works without Auggie, works BETTER with it. No component should REQUIRE Auggie for basic functionality.

### A3: Circuit Breaker Standard

3 consecutive failures → OPEN (30s) → HALF_OPEN (test) → CLOSED. Consistent with MCP.md and v1.2 backlog.

### A4: Fallback Chain

```
mcp__auggie-mcp__codebase-retrieval (semantic)
  → mcp__serena__find_symbol + find_referencing_symbols (structural)
  → Grep + Glob (pattern)
  → Read + manual guidance (last resort)
```

### A5: Query Template Standard

Every integration point must specify domain-specific `information_request` templates with `{variable}` placeholders. Generic "load context" is insufficient.

---

## Statistics

| Metric | Count |
|--------|-------|
| Total components evaluated | 59 (29 commands + 25 agents + 5 skills) |
| HIGH benefit candidates | 20 (9 commands + 9 agents + 2 skills) |
| MEDIUM benefit candidates | 20 (9 commands + 9 agents + 2 skills) |
| LOW/NO benefit (excluded) | 19 (11 commands + 7 agents + 1 skill) |
| Existing uses requiring fixes | 3 (task-unified, task-mcp, sc-task-unified SKILL) |
| Net new integration targets | 17+ HIGH priority components |
