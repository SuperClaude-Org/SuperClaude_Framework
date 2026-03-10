# D-0027 — Spec: Verb-to-Tool Glossary

**Task**: T05.01
**Date**: 2026-02-24
**Status**: COMPLETE
**Tier**: STANDARD

## Purpose

Disambiguate invocation verbs used across sprint-spec and SKILL.md files to prevent implementers from using the wrong tool for each operation. This glossary resolves the inconsistent usage of "Invoke", "Dispatch", and "Load" identified in sprint-spec §8.

## Verb-to-Tool Glossary

| Verb | Tool Binding | Context | Example |
|------|-------------|---------|---------|
| **Invoke** (Skill) | `Skill` tool | Load a protocol skill into current agent context | `Invoke Skill sc:adversarial-protocol` |
| **Dispatch** (Agent) | `Task` tool | Spawn a fresh sub-agent for parallel/isolated execution | `Dispatch quality-engineer agent` |
| **Load** (File) | `Read` tool | Read file content into current context | `Load refs/scoring.md` |
| **Load** (MCP) | MCP tool call | Query an MCP server for external data | `Load context7 for patterns` |

### Disambiguation Rules

1. **"Invoke"** always maps to the **Skill tool**. It means: load a SKILL.md protocol into the current agent's context via the Skill tool. Never use bare "Invoke" without specifying the Skill tool.
2. **"Dispatch"** always maps to the **Task tool**. It means: spawn a new agent in a fresh context to execute work independently. The Task agent returns a prose response; any structured output (e.g., return contracts) is written to disk.
3. **"Load"** maps to the **Read tool** when referencing files (refs, configs, specs). It maps to an MCP tool call when referencing external data (Context7 documentation, Serena memory). Context determines which.
4. **Never use "Invoke" for agent dispatch** — that is "Dispatch".
5. **Never use "Dispatch" for skill loading** — that is "Invoke".
6. **Never use bare verbs without tool binding** — every invocation verb must include its target tool.

### Canonical Patterns

```
# Skill invocation (Tier 0 → Tier 1)
Invoke Skill sc:<name>-protocol [with arguments]

# Agent dispatch (parallel execution, validation)
Dispatch <agent-type> agent [using Task tool]

# File loading (Tier 1 → Tier 2, or any file read)
Load <file-path> [via Read tool]

# MCP server query
Load <server-name> for <purpose>
```

## Cross-Reference: Verb Usage Across SKILL.md Files

### sc-roadmap-protocol/SKILL.md
| Line | Verb Usage | Status |
|------|-----------|--------|
| 84 | Inline glossary: "Invoke Skill" = Skill tool, "Dispatch Task agent" = Task tool, "Load ref" = Read tool | **Compliant** |
| 113 | "Invoke `sc:adversarial-protocol` directly" | Needs tool binding — should be "Invoke Skill sc:adversarial-protocol" |
| 115 | "Invoke: `Skill sc:adversarial-protocol`" | **Compliant** |
| 158 | "Invoke `sc:adversarial-protocol` directly via Skill tool" | **Compliant** |
| 160 | "Invoke: `Skill sc:adversarial-protocol`" | **Compliant** |
| 207 | "Dispatch quality-engineer agent" | **Compliant** |
| 208 | "Dispatch self-review agent" | **Compliant** |
| 252 | "invokes `Skill sc:adversarial-protocol`" | **Compliant** |
| 255 | "invokes `Skill sc:adversarial-protocol`" | **Compliant** |
| 335 | "Invoke `Skill sc:adversarial-protocol`" | **Compliant** |
| 383-384 | "`Invoke Skill sc:adversarial-protocol`" | **Compliant** |

### sc-adversarial-protocol/SKILL.md
| Line | Verb Usage | Status |
|------|-----------|--------|
| 341 | "When invoked by another command" | Generic — acceptable (describes being called, not calling) |
| 358 | "dispatch variants" | Lowercase, contextual — acceptable (describes internal behavior) |
| 511 | "dispatch Task agents per --agents spec" | **Compliant** (references Task tool) |
| 801, 833, 866, 892 | `dispatch:` YAML config blocks | **Compliant** (structured config, not prose) |
| 1404, 1408 | "Merge Executor Dispatch" / `dispatch:` | **Compliant** |
| 1582 | "Any command can invoke sc:adversarial and consume the return contract" | Needs tool binding — should specify Skill tool |
| 1647-1649 | `parallel_dispatch:` / "ALL agents dispatched simultaneously" | **Compliant** (YAML config) |

### sc-validate-tests-protocol/SKILL.md
| Line | Verb Usage | Status |
|------|-----------|--------|
| 68 | "Load Test Specifications" | Section heading — acceptable (not an invocation instruction) |

### sc-task-unified-protocol/SKILL.md
| Line | Verb Usage | Status |
|------|-----------|--------|
| 147 | "Load codebase context (codebase-retrieval)" | **Compliant** (describes Read-based retrieval) |
| 158 | "Load context via codebase-retrieval" | **Compliant** |
| 212 | "codebase-retrieval: Load context" | **Compliant** |

### sc-pm-protocol/SKILL.md
| Line | Verb Usage | Status |
|------|-----------|--------|
| 65 | "Load context7 for patterns" | **Compliant** (MCP Load variant) |
| 164 | "Dynamic Loading: Load tools only when needed" | Generic — acceptable (design principle, not invocation) |

### sc-cleanup-audit-protocol/SKILL.md
| Line | Verb Usage | Status |
|------|-----------|--------|
| 46 | "Load pass-specific rules from `rules/`" | **Compliant** (file Load) |

### sc-recommend-protocol/SKILL.md, sc-review-translation-protocol/SKILL.md
| Verb Usage | Status |
|-----------|--------|
| "invoked ONLY by the `sc:X` command via `Skill sc:X-protocol`" | **Compliant** |
| "Do NOT invoke this skill directly" | Generic — acceptable (user-facing warning) |

## Issues Found

Two non-compliant patterns identified (to be fixed in T05.03):

1. **sc-roadmap-protocol/SKILL.md line 113**: `"Invoke sc:adversarial-protocol directly"` — missing explicit Skill tool binding
2. **sc-adversarial-protocol/SKILL.md line 1582**: `"Any command can invoke sc:adversarial"` — missing explicit Skill tool binding

## Consistency with Sprint-Spec §8

The glossary is consistent with sprint-spec §8's "Task Agent vs Skill Tool vs claude -p" table (lines 515-528):
- Skill tool = "Invoke skill directly in current context" ✓
- Task tool = "Delegate to sub-agent in fresh context" ✓
- claude -p = "Inject ref/detail into current context" (not a verb in SKILL.md files — refs are loaded via Read tool in the D-0001 reversal variant)
- claude -p script = Unfinalized strategy (§8 lines 530-550) — not used in any SKILL.md

*Artifact produced by T05.01*
