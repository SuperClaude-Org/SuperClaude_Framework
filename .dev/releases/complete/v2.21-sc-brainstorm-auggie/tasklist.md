# v2.21 — Auggie MCP Integration into sc:brainstorm

**Release**: v2.21-sc-brainstorm-auggie
**Branch**: `feature/brainstorm-auggie-mcp`
**Status**: Planning Complete
**Created**: 2026-03-09

---

## Overview

Integrate Auggie MCP (`codebase-retrieval`) into the `sc:brainstorm` command to provide automatic codebase awareness during code-related brainstorming sessions. Also document Auggie as a first-class MCP server in the framework's MCP.md reference.

## Design Decisions (from brainstorm + design phases)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trigger mode | Smart detection (not always-on) | Avoids token waste on business/strategy brainstorms |
| Context depth | Topic query + architecture scan (2 queries) | Balanced awareness without excessive token cost |
| Scope | Brainstorm command + MCP.md docs | Sets the pattern for other commands to follow |
| Detection signals | Code entities + dev verbs + project terms | Three complementary signal categories |
| Fallback | Serena + native tools (Grep/Glob) | Partial coverage better than none |
| Context presentation | Upfront structured briefing | User sees context before Socratic questions begin |

---

## Task List

### Phase 1: Update brainstorm.md (Source of Truth)

**Target file**: `src/superclaude/commands/brainstorm.md`

#### Task 1.1: Update frontmatter
- **Action**: Add `auggie-mcp` to `mcp-servers` list
- **Change**: `mcp-servers: [sequential, context7, magic, playwright, morphllm, serena]`
  → `mcp-servers: [sequential, context7, magic, playwright, morphllm, serena, auggie-mcp]`
- **Effort**: Trivial

#### Task 1.2: Update Behavioral Flow section
- **Action**: Change from 5-phase to 6-phase flow, inserting Phase 0 (Codebase Context)
- **Details**:
  - Add `0. **Codebase Context**: Detect code-relevance → load codebase context via Auggie MCP → present upfront briefing` before existing step 1
  - Add key behavior: `Automatic codebase awareness for code-related topics via smart detection and Auggie MCP`
- **Effort**: Small

#### Task 1.3: Add Auggie to MCP Integration section
- **Action**: Add Auggie MCP entry to existing MCP Integration list
- **Content**:
  ```
  - **Auggie MCP**: Semantic codebase retrieval for code-related topic awareness and project structure understanding
  ```
- **Effort**: Trivial

#### Task 1.4: Add codebase-retrieval to Tool Coordination section
- **Action**: Add tool entry
- **Content**:
  ```
  - **codebase-retrieval**: Semantic codebase search for relevant code, architecture, and integration points
  ```
- **Effort**: Trivial

#### Task 1.5: Add Codebase Awareness section
- **Action**: Insert new `## Codebase Awareness` section after Tool Coordination
- **Content**: Full detection algorithm, Phase 0 flow, query templates, briefing format, fallback strategy
- **Details**: See design spec `design-spec.md` Section 2-4 for exact content
- **Effort**: Medium (largest single change)

#### Task 1.6: Add new flags to Context Trigger Pattern
- **Action**: Update usage pattern to include `--codebase` and `--no-codebase` flags
- **Change**:
  ```
  /sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel] [--codebase] [--no-codebase]
  ```
- **Effort**: Trivial

#### Task 1.7: Add codebase-aware example
- **Action**: Add new example showing codebase-aware brainstorming
- **Content**:
  ```
  ### Codebase-Aware Feature Discovery
  /sc:brainstorm "add caching to the API layer" --depth deep
  # Auggie MCP detects code-related topic → loads relevant API code and architecture
  # Socratic dialogue informed by existing implementation patterns and constraints
  ```
- **Effort**: Small

---

### Phase 2: Update MCP.md (Framework Reference)

**Target file**: `src/superclaude/core/MCP.md`

#### Task 2.1: Add Auggie MCP Integration section
- **Action**: Insert new `## Auggie MCP Integration (Codebase Intelligence)` section after Playwright Integration (line 149) and before MCP Server Use Cases (line 150)
- **Content**: Purpose, activation patterns, workflow process, integration commands, error recovery
- **Pattern**: Follow exact structure of Context7/Sequential/Magic/Playwright sections
- **Effort**: Medium

#### Task 2.2: Add Auggie to circuit breaker table
- **Action**: Add row to Per-Server Settings & Fallbacks table (line 213-220)
- **Content**: `| Auggie | 3 failures | 45s | Serena + Grep/Glob | Reduced codebase awareness |`
- **Effort**: Trivial

#### Task 2.3: Add Auggie to caching strategies
- **Action**: Add line to Caching Strategies section (line 197-203)
- **Content**: `- Auggie Cache: Codebase retrieval results with working-directory-scoped caching`
- **Effort**: Trivial

#### Task 2.4: Add Auggie to command category use cases
- **Action**: Update MCP Server Use Cases by Command Category (line 150+)
- **Changes**:
  - **Analysis Commands**: Add `Auggie: Codebase context and pattern discovery`
  - **Planning Commands**: Add `Auggie: Existing implementation awareness`
  - **Development Commands**: Add `Auggie: Pre-implementation codebase context`
- **Effort**: Small

---

### Phase 3: Sync and Verify

#### Task 3.1: Sync dev copies
- **Action**: Run `make sync-dev` to copy `src/superclaude/commands/brainstorm.md` → `.claude/commands/sc/brainstorm.md`
- **Verify**: Run `make verify-sync` to confirm both sides match
- **Effort**: Trivial

#### Task 3.2: Manual verification of .claude copy
- **Action**: Confirm `.claude/commands/sc/brainstorm.md` matches source
- **Note**: MCP.md in `.claude/` is the global user config copy, NOT managed by sync-dev. The project-level `src/superclaude/core/MCP.md` is what gets installed by `superclaude install`.
- **Effort**: Trivial

#### Task 3.3: Validate no breaking changes
- **Action**: Run `uv run pytest` to ensure no existing tests break
- **Effort**: Trivial

---

## Execution Order

```
Phase 1 (Tasks 1.1-1.7) — all sequential, single file
    │
    ▼
Phase 2 (Tasks 2.1-2.4) — all sequential, single file
    │
    ▼
Phase 3 (Tasks 3.1-3.3) — sequential (sync depends on edits)
```

**Parallelization**: Phase 1 and Phase 2 are independent and could run in parallel if separate agents are used. Phase 3 depends on both completing.

## Token Budget Estimate

| Phase | Estimated Tokens | Notes |
|-------|-----------------|-------|
| Phase 1 | ~2,000 | 7 edits to single file |
| Phase 2 | ~1,500 | 4 edits to single file |
| Phase 3 | ~300 | Commands only |
| **Total** | **~3,800** | Well within single-session budget |

## Files Modified

| File | Action | Phase |
|------|--------|-------|
| `src/superclaude/commands/brainstorm.md` | Edit (7 changes) | 1 |
| `src/superclaude/core/MCP.md` | Edit (4 changes) | 2 |
| `.claude/commands/sc/brainstorm.md` | Sync (automated) | 3 |

## Success Criteria

- [ ] `brainstorm.md` frontmatter includes `auggie-mcp`
- [ ] Phase 0 (Codebase Context) documented with detection algorithm
- [ ] `--codebase` / `--no-codebase` flags documented
- [ ] Fallback strategy (Serena + native tools) documented
- [ ] MCP.md has Auggie section following existing server pattern
- [ ] Circuit breaker table includes Auggie entry
- [ ] `make verify-sync` passes
- [ ] `uv run pytest` passes (no regressions)
