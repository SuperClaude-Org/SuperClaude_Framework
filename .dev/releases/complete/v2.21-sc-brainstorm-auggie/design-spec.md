# Design Specification: Auggie MCP Integration into sc:brainstorm

**Version**: 1.0
**Date**: 2026-03-09
**Status**: Approved (from brainstorm + design phases)

---

## 1. System Flow

```
User Input: /sc:brainstorm "add caching to the API layer"
                    │
                    ▼
        ┌──────────────────────┐
        │  Code-Relevance      │
        │  Detection Engine    │
        │  (3 signal checks)   │
        └──────┬───────────────┘
               │
        ┌──────┴──────┐
        │ Code-related?│
        ├─── YES ─────┤─── NO ──────────────────────┐
        │              │                              │
        ▼              │                              ▼
┌───────────────┐      │              ┌──────────────────────┐
│ Phase 0:      │      │              │ Skip to Phase 1:     │
│ Codebase      │      │              │ Socratic Dialogue    │
│ Context Load  │      │              │ (no codebase context)│
│               │      │              └──────────────────────┘
│ Query 1: Topic│      │
│ Query 2: Arch │      │
└──────┬────────┘      │
       │               │
       ▼               │
┌───────────────┐      │
│ Context Brief │      │
│ (presented to │      │
│  user)        │      │
└──────┬────────┘      │
       │               │
       ▼               │
┌──────────────────────┐
│ Phase 1-5:           │
│ Normal Brainstorm    │
│ Flow (context-aware) │
└──────────────────────┘
```

## 2. Code-Relevance Detection Algorithm

Expressed as behavioral rules in the command file. Claude evaluates the brainstorm topic against three signal categories. If **any one** category matches, codebase loading triggers.

### Signal Category A: Code Entity References

Match when the topic mentions any of:
- File paths or extensions (`.py`, `.ts`, `src/`, `tests/`)
- Programming constructs: function, class, method, module, component, endpoint, API, route, handler, model, schema, interface, type, service, controller, middleware, hook, plugin
- Infrastructure terms: database, cache, queue, server, container, pipeline, deployment
- Specific named entities from the codebase (inferred from working directory context)

### Signal Category B: Development Action Verbs

Match when the topic contains verbs indicating code work:
- **Creation**: implement, build, create, add, generate, scaffold
- **Modification**: refactor, optimize, improve, update, migrate, upgrade, extend, modify
- **Repair**: fix, debug, resolve, patch, hotfix
- **Analysis**: analyze, audit, review, profile, benchmark (in code context)

### Signal Category C: Project-Specific Terms

Match when the topic references:
- The project name or known package names (inferred from `package.json`, `pyproject.toml`, directory name)
- Language/framework names matching the project's stack
- Known module or directory names from the project structure

### Decision Rule

```
IF signal_A OR signal_B OR signal_C:
    → Trigger Phase 0 (Codebase Context Loading)
ELSE:
    → Skip to Phase 1 (Standard Socratic Dialogue)
```

**Override flags**:
- `--codebase`: Force Phase 0 regardless of detection
- `--no-codebase`: Skip Phase 0 regardless of detection

**Edge case**: If uncertain, do NOT trigger. False negatives preferred over token waste.

## 3. Phase 0: Codebase Context Loading

### Step 0.1: Tool Selection

```
IF mcp__auggie-mcp__codebase-retrieval is available:
    → Use Auggie (primary path)
ELSE:
    → Use Fallback path (Section 4)
```

### Step 0.2: Topic-Specific Query (parallel with 0.3)

```
Call: mcp__auggie-mcp__codebase-retrieval
Parameters:
  information_request: "{brainstorm_topic} - find relevant code, existing implementations,
                        related components, and integration points"
  directory_path: "{current_working_directory}"
```

### Step 0.3: Architecture Scan Query (parallel with 0.2)

```
Call: mcp__auggie-mcp__codebase-retrieval
Parameters:
  information_request: "Project architecture, structure, patterns, and conventions
                        related to {topic_domain_area}"
  directory_path: "{current_working_directory}"
```

### Step 0.4: Context Briefing Output

```markdown
## Codebase Context

**Relevant Existing Code:**
- [file:line] — brief description of what exists
- [file:line] — brief description of what exists

**Architecture & Patterns:**
- Pattern/convention observed
- Structural observation

**Integration Points:**
- Where new work would connect
- Existing interfaces or extension points

**Constraints Identified:**
- Technical constraints from existing implementation
- Dependencies or coupling to be aware of
---
```

Token budget: ~500-800 tokens max.

## 4. Fallback Strategy (Auggie Unavailable)

### Fallback Step 1: Serena Symbol Overview

```
Call: mcp__serena__get_symbols_overview
Parameters:
  relative_path: "." (or best-guess subdirectory from topic)
  depth: 1
```

### Fallback Step 2: Native Search (parallel)

```
- Glob: Find files matching topic keywords (e.g., "**/*cache*", "**/*api*")
- Grep: Search for topic-relevant patterns in code files
```

### Fallback Briefing

Same format as Section 3 Step 0.4, prefixed with:
```
> Note: Limited codebase awareness (Auggie MCP unavailable, using Serena + native tools)
```

## 5. Modified Behavioral Flow

| Phase | Name | Description | Status |
|-------|------|-------------|--------|
| **0** | **Codebase Context** | Smart detection → Auggie queries → Upfront briefing | **NEW** |
| 1 | Explore | Socratic dialogue (now informed by codebase context) | **Modified** |
| 2 | Analyze | Multi-persona analysis | Unchanged |
| 3 | Validate | Feasibility assessment | Unchanged |
| 4 | Specify | Requirements specification | Unchanged |
| 5 | Handoff | Actionable briefs | Unchanged |

## 6. Token Budget Analysis

| Operation | Estimated Tokens |
|-----------|-----------------|
| Detection logic | ~50 |
| Auggie Query 1 (topic) | ~500-1500 |
| Auggie Query 2 (architecture) | ~500-1500 |
| Context briefing output | ~500-800 |
| **Total Phase 0 overhead** | **~1500-3800** |

## 7. MCP.md Auggie Section Content

```markdown
## Auggie MCP Integration (Codebase Intelligence)

**Purpose**: Semantic codebase retrieval, project structure understanding, code-aware context loading

**Activation Patterns**:
- Automatic: Code-related brainstorm topics, task execution (STRICT/STANDARD tiers), implementation planning
- Manual: `--auggie` flag
- Smart: Commands detect need for codebase awareness before code-related operations

**Workflow Process**:
1. Topic Analysis: Determine if codebase context would be valuable for the current operation
2. Query Formulation: Create natural language queries from task/topic context
3. Retrieval: Call codebase-retrieval with project directory path
4. Context Synthesis: Extract relevant findings into structured briefing
5. Integration: Feed context into downstream reasoning, dialogue, or implementation

**Integration Commands**: `/brainstorm`, `/task`, `/implement`, `/analyze`, `/troubleshoot`

**Error Recovery**:
- Server unavailable → Fallback to Serena symbol search + Grep/Glob for basic codebase awareness
- No relevant results → Proceed without codebase context, note limitation to user
- Timeout → Use partial results if available, otherwise skip with warning
- Working directory invalid → Prompt user for correct project path
```
