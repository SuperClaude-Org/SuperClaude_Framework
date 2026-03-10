# Auggie MCP Phase 3: Implementation Specification

> **Generated**: 2026-02-20
> **Input**: Wave 1 Consolidated Results (`auggie-mcp-wave1-consolidated.md`)
> **Scope**: All Tier 1 (detailed) + Tier 2 (summary) validated candidates
> **Architecture Decisions**: A1-A5 from Wave 1 report

---

## Cross-Cutting Standards

These standards apply to EVERY integration point in this document. Individual component specs inherit and may extend but never contradict them.

### S1: Canonical Tool Invocation

```
Tool:  mcp__auggie-mcp__codebase-retrieval
Params:
  information_request: string (REQUIRED) - domain-specific query with {variable} placeholders
  directory_path: string (REQUIRED) - absolute path to project root
```

**Never** use bare `codebase-retrieval` or fabricated sub-commands like `codebase-retrieval/view`.

### S2: directory_path Resolution Strategy

All components MUST resolve `directory_path` using this cascade:

```
1. Explicit user argument     → /sc:analyze /absolute/path/to/project
2. Git root detection         → $(git rev-parse --show-toplevel)
3. Current working directory  → $PWD (from env context)
4. Serena project root        → mcp__serena__get_current_config → active project path
5. Fail with guidance         → "Cannot determine project root. Provide --path or run from project directory."
```

Template variable: `{project_root}` resolves via this cascade at runtime.

### S3: Fallback Chain

Every Auggie call site MUST implement this ordered degradation:

```
Level 0: mcp__auggie-mcp__codebase-retrieval  (semantic discovery)
Level 1: mcp__serena__find_symbol + find_referencing_symbols  (structural/symbolic)
Level 2: Grep + Glob  (pattern matching)
Level 3: Read + manual file enumeration  (last resort)
```

**Transition rules**:
- Level 0 failure (timeout, error, circuit open) -> skip to Level 1
- Level 1 failure -> skip to Level 2
- Level 2 always succeeds (it is grep/glob)
- Include degradation notice in output: `[Note: Using pattern search — semantic search unavailable]`

### S4: Circuit Breaker Configuration

```yaml
auggie-mcp-circuit-breaker:
  failure_threshold: 3          # consecutive failures to trip
  state_after_trip: OPEN
  open_duration_seconds: 30
  half_open_test: single query with 5s timeout
  reset_on_success: true        # HALF_OPEN success -> CLOSED
  reset_on_failure: true        # HALF_OPEN failure -> OPEN (extend 30s)
  scope: per-session            # resets on new conversation
```

This is consistent with MCP.md circuit breaker configuration for other servers.

### S5: Progressive Enhancement Contract

```
WITHOUT Auggie: Command MUST function using Grep+Glob+Read. All workflows complete.
WITH Auggie:    Command functions BETTER — faster discovery, semantic matching, fewer false negatives.
```

No command or agent may gate its core functionality on Auggie availability. Auggie is always PREFERRED, never REQUIRED (except where explicitly noted for STRICT tier compliance in task-unified).

### S6: Query Template Standard

Every `information_request` must be:
- Domain-specific (not generic "load context")
- Parameterized with `{variable}` placeholders
- Actionable (the response directly feeds the next workflow step)

---

## Tier 1: Detailed Implementation Proposals

---

### T1-FIX-1: `src/superclaude/commands/task-unified.md`

**Current state**: Lines 6, 160, 170, 219 reference `codebase-retrieval` with wrong tool name, missing parameters, fabricated sub-commands. `auggie-mcp` absent from `mcp-servers` frontmatter.

#### Change 1: Frontmatter (line 6)

```yaml
# BEFORE
mcp-servers: [sequential, context7, serena, playwright, magic, morphllm]

# AFTER
mcp-servers: [sequential, context7, serena, auggie-mcp, playwright, magic, morphllm]
```

Position `auggie-mcp` after `serena` (both are codebase-understanding tools; group logically).

#### Change 2: Line 160 — Pre-work checklist

```markdown
# BEFORE (line 160)
[ ] Context loaded for task area? (codebase-retrieval)

# AFTER
[ ] Context loaded for task area? (mcp__auggie-mcp__codebase-retrieval)
    Query: "Show all modules, classes, and functions related to {task_area} including imports, dependencies, and test coverage"
    directory_path: {project_root}
    Fallback: Grep for {task_area} keywords → Glob for related files → Read key files
```

#### Change 3: Line 170 — Fabricated sub-command

```markdown
# BEFORE (line 170)
1. [ ] View current code state (codebase-retrieval/view)

# AFTER
1. [ ] View current code state:
   - Primary: mcp__auggie-mcp__codebase-retrieval
     Query: "Show the current implementation of {target_symbol} including its signature, body, callers, and callees"
     directory_path: {project_root}
   - Fallback: Read {primary_file} directly
```

#### Change 4: Line 219 — SMART criteria

```markdown
# BEFORE (line 219)
- **M**easurable: >=1 codebase-retrieval call, >=1 downstream impact search

# AFTER
- **M**easurable: >=1 mcp__auggie-mcp__codebase-retrieval call (or fallback equivalent), >=1 downstream impact search via find_referencing_symbols or Grep
```

#### New Section: Add after line 206 (Post-Task checklist)

```markdown
### Auggie MCP Integration

**Circuit Breaker**: 3 failures -> OPEN(30s) -> HALF_OPEN -> CLOSED (per S4).

**Query Templates by Tier**:

| Tier | Phase | information_request Template |
|------|-------|----------------------------|
| STRICT | Context Load | "All modules, classes, functions, imports, and test files related to {task_description} in this project" |
| STRICT | Impact Analysis | "All files that import, reference, or depend on {changed_symbol} including transitive dependencies" |
| STRICT | Verification | "Test files and test functions that exercise {changed_file} functionality" |
| STANDARD | Context Load | "Key files and entry points related to {task_description}" |
| STANDARD | Impact Search | "Files that directly reference {changed_symbol}" |
| LIGHT | (none) | N/A — Auggie not required |
| EXEMPT | (none) | N/A — Auggie not required |

**Fallback Behavior by Tier**:

| Tier | Auggie Unavailable | Action |
|------|-------------------|--------|
| STRICT | BLOCK if no fallback succeeds | Serena find_symbol -> Grep -> BLOCK with explanation |
| STANDARD | CONTINUE with degradation notice | Grep + Glob with notice |
| LIGHT | CONTINUE silently | No MCP needed |
| EXEMPT | CONTINUE silently | No MCP needed |
```

---

### T1-FIX-2: `src/superclaude/skills/sc-task-unified/SKILL.md`

**Current state**: Lines 147, 158, 212 reference bare `codebase-retrieval` without full tool name or parameters. No `auggie-mcp` in allowed-tools or integration sections.

#### Change 1: Line 147 — STRICT execution step 3

```markdown
# BEFORE (line 147)
3. Load codebase context (codebase-retrieval)

# AFTER
3. Load codebase context:
   Tool: mcp__auggie-mcp__codebase-retrieval
   information_request: "All modules, classes, functions, and test files related to {task_description}. Include import chains and dependency relationships."
   directory_path: {project_root}
   Fallback: mcp__serena__find_symbol + Grep for task keywords
```

#### Change 2: Line 158 — STANDARD execution step 1

```markdown
# BEFORE (line 158)
1. Load context via codebase-retrieval

# AFTER
1. Load context:
   Tool: mcp__auggie-mcp__codebase-retrieval
   information_request: "Key files, entry points, and interfaces related to {task_description}"
   directory_path: {project_root}
   Fallback: Grep for task keywords → Glob for related file patterns
```

#### Change 3: Line 212 — Tool Coordination / Planning Phase

```markdown
# BEFORE (line 212)
2. codebase-retrieval: Load context

# AFTER
2. mcp__auggie-mcp__codebase-retrieval: Load semantic context
   information_request: "{phase_specific_query}"
   directory_path: {project_root}
   Circuit breaker: S4 standard (3 failures -> OPEN 30s)
   Fallback: Serena symbols -> Grep+Glob
```

#### New Section: Add to MCP Integration section (after line 206)

```markdown
### Auggie MCP Queries by Phase

| Phase | information_request | Fallback |
|-------|-------------------|----------|
| Planning | "Project structure, entry points, and modules related to {task_description}" | Glob **/*.{ext} + Read key files |
| Context Load | "Implementation details, imports, and dependencies for {target_files}" | Read files directly |
| Impact Analysis | "All references to {changed_symbols} including transitive callers" | mcp__serena__find_referencing_symbols |
| Verification | "Test files covering {changed_modules} and their assertion patterns" | Glob tests/**/*{module}* |
```

---

### T1-NEW-1: `src/superclaude/commands/analyze.md`

**Current state**: `mcp-servers: []` (empty), `personas: []` (empty). No MCP integration at all.

#### Change 1: Frontmatter

```yaml
# BEFORE
mcp-servers: []
personas: []

# AFTER
mcp-servers: [auggie-mcp, sequential, context7]
personas: [analyzer, architect, security]
```

Rationale: `auggie-mcp` is PRIMARY for analyze (semantic codebase understanding is the core use case). `sequential` for structured multi-step analysis. `context7` for framework-specific patterns.

#### Change 2: New section after "Tool Coordination" (after line 41)

```markdown
## MCP Integration

### Auggie MCP (Primary — Semantic Discovery)

Used in Steps 1 (Discover) and 2 (Scan) of Behavioral Flow.

**Step 1 — Discovery Query**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "Project structure overview: entry points, module boundaries, dependency graph, and architectural layers for {target_path}"
directory_path: {project_root}
```

**Step 2 — Domain-Specific Scan Queries**:

| --focus | information_request |
|---------|-------------------|
| quality | "Code quality indicators in {target_path}: complex functions (cyclomatic >10), long files (>500 lines), deep nesting (>4), duplicated logic, and violations of SOLID principles" |
| security | "Security-sensitive code in {target_path}: authentication flows, authorization checks, input validation, cryptographic usage, secret handling, SQL queries, and external API calls" |
| performance | "Performance-critical paths in {target_path}: database queries, loops over collections, memory allocations, I/O operations, caching patterns, and algorithmic complexity hotspots" |
| architecture | "Architectural structure of {target_path}: module boundaries, dependency directions, coupling between components, layering violations, and circular dependencies" |

**Circuit Breaker**: S4 standard.

**Fallback**:
- Discovery: `Glob **/*.{ext}` + `Read` key files (package.json, pyproject.toml, etc.)
- Scan: `Grep` for domain-specific patterns (e.g., `eval(`, `exec(` for security; `SELECT.*FROM` for performance)

### Sequential MCP (Analysis Depth)

Used in Step 3 (Evaluate) for structured multi-step reasoning when `--depth deep` is specified.

### Context7 MCP (Pattern Reference)

Used in Step 4 (Recommend) for framework-specific best practices and improvement patterns.
```

---

### T1-NEW-2: `src/superclaude/commands/troubleshoot.md`

**Current state**: `mcp-servers: []`, `personas: []`. No MCP integration.

#### Change 1: Frontmatter

```yaml
# BEFORE
mcp-servers: []
personas: []

# AFTER
mcp-servers: [auggie-mcp, sequential]
personas: [analyzer, architect]
```

Rationale: `auggie-mcp` for semantic code path tracing (root cause requires understanding call chains). `sequential` for hypothesis-driven debugging.

#### Change 2: New section after "Tool Coordination" (after line 40)

```markdown
## MCP Integration

### Auggie MCP (Primary — Code Path Tracing)

Used in Steps 1 (Analyze) and 2 (Investigate) of Behavioral Flow.

**Step 1 — Error Context Query**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "All code paths, error handlers, and control flow related to {error_description}. Include function call chains, try/catch blocks, and logging statements that could produce this error."
directory_path: {project_root}
```

**Step 2 — Root Cause Investigation Queries**:

| --type | information_request |
|--------|-------------------|
| bug | "Implementation of {suspected_function}, its callers, data flow through parameters, and edge cases in validation logic" |
| build | "Build configuration files, dependency declarations, compilation settings, and recent changes to build-related files" |
| performance | "Hot paths related to {slow_operation}: database queries, loop structures, memory allocations, and caching layers" |
| deployment | "Deployment configuration, environment variable usage, service dependencies, and infrastructure definitions" |

**Circuit Breaker**: S4 standard.

**Fallback**:
- Error context: `Grep` for error message strings and exception types
- Root cause: `Grep` for function names + `Read` stack trace files

### Sequential MCP (Hypothesis Testing)

Used in Step 3 (Debug) for structured hypothesis generation and systematic elimination.
```

---

### T1-NEW-3: `src/superclaude/commands/design.md`

**Current state**: `mcp-servers: []`, `personas: []`. No MCP integration.

#### Change 1: Frontmatter

```yaml
# BEFORE
mcp-servers: []
personas: []

# AFTER
mcp-servers: [auggie-mcp, sequential, context7]
personas: [architect, frontend, backend]
```

#### Change 2: New section after "Tool Coordination" (after line 40)

```markdown
## MCP Integration

### Auggie MCP (Primary — Existing System Map)

Used in Step 1 (Analyze) to understand the system being designed against.

**Existing System Discovery Query**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "Current system architecture related to {design_target}: existing components, their interfaces, data models, dependency relationships, and integration points"
directory_path: {project_root}
```

**Design-Type-Specific Queries**:

| --type | information_request |
|--------|-------------------|
| architecture | "All top-level modules, their public interfaces, dependency directions, and communication patterns in {target_scope}" |
| api | "Existing API endpoints, request/response schemas, authentication patterns, and middleware chain in {target_scope}" |
| component | "Existing component hierarchy, prop interfaces, state management patterns, and shared utilities in {target_scope}" |
| database | "Current data models, relationships, migration history, and query patterns in {target_scope}" |

**Circuit Breaker**: S4 standard.

**Fallback**: Glob for structure files + Read key interfaces + Grep for patterns.

### Sequential MCP (Design Reasoning)

Used in Steps 2-4 for structured design trade-off analysis.

### Context7 MCP (Pattern Library)

Used in Step 3 for industry-standard design patterns and framework conventions.
```

---

### T1-NEW-4: `src/superclaude/commands/document.md`

**Current state**: `mcp-servers: []`, `personas: []`. No MCP integration.

#### Change 1: Frontmatter

```yaml
# BEFORE
mcp-servers: []
personas: []

# AFTER
mcp-servers: [auggie-mcp, context7]
personas: [scribe, architect]
```

#### Change 2: New section after "Tool Coordination" (after line 41)

```markdown
## MCP Integration

### Auggie MCP (Primary — Code Understanding for Accurate Docs)

Used in Step 1 (Analyze) to build accurate understanding before writing documentation.

**Component Analysis Query**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "Complete interface of {target_component}: public methods with signatures, parameters with types, return values, class hierarchy, usage examples in tests, and existing documentation comments"
directory_path: {project_root}
```

**Documentation-Type-Specific Queries**:

| --type | information_request |
|--------|-------------------|
| inline | "Function signatures, parameter types, return types, side effects, and existing docstrings for all public symbols in {target_file}" |
| api | "All API endpoints in {target_path}: HTTP methods, URL patterns, request/response schemas, authentication requirements, and error responses" |
| guide | "User-facing features in {target_scope}: entry points, configuration options, common workflows, and error handling patterns" |
| external | "Module overview of {target_path}: purpose, public API surface, dependencies, integration patterns, and configuration" |

**Circuit Breaker**: S4 standard.

**Fallback**: Read target files directly + Grep for export/public patterns.

### Context7 MCP (Documentation Standards)

Used in Step 3 for language-specific documentation conventions (JSDoc, docstrings, etc.).
```

---

### T1-NEW-5: `src/superclaude/commands/cleanup.md`

**Current state**: `mcp-servers: [sequential, context7]`, `personas: [architect, quality, security]`. Has some MCP integration but no Auggie.

#### Change 1: Frontmatter (line 6)

```yaml
# BEFORE
mcp-servers: [sequential, context7]

# AFTER
mcp-servers: [auggie-mcp, sequential, context7]
```

Position `auggie-mcp` first — it is the primary tool for dead code detection (a semantic problem).

#### Change 2: Extend existing "MCP Integration" section (after line 39)

Add before the existing Sequential/Context7 entries:

```markdown
### Auggie MCP (Primary — Semantic Dead Code Detection)

Used in Steps 1 (Analyze) and 3 (Execute) of Behavioral Flow.

**Step 1 — Dead Code Discovery**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "Unused exports, unreferenced functions, dead code paths, and orphaned files in {target_path}. Include functions defined but never called, exports never imported, and files not referenced by any other file."
directory_path: {project_root}
```

**Cleanup-Type-Specific Queries**:

| --type | information_request |
|--------|-------------------|
| code | "Functions, classes, and variables in {target_path} that are defined but never referenced elsewhere in the project" |
| imports | "Import statements in {target_path} where the imported symbol is never used in the importing file" |
| files | "Files in {target_path} that are not imported, required, or referenced by any other file in the project" |
| all | "Complete dead code analysis of {target_path}: unused functions, orphaned files, unused imports, unreachable code branches, and deprecated code still present" |

**Step 3 — Safe Removal Verification**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "All references to {symbol_to_remove} including dynamic imports and string-based references like reflection, eval, or configuration files"
directory_path: {project_root}
```

**Circuit Breaker**: S4 standard.

**Fallback**:
- Dead code discovery: Grep for function/class definitions → cross-reference with Grep for usages
- Safe removal: mcp__serena__find_referencing_symbols → Grep for string references
```

---

### T1-NEW-6: `src/superclaude/skills/confidence-check/SKILL.md`

**Current state**: Check 1 (Duplicate Detection, 25% of score) uses `Grep` and `Glob` for duplicate search. No semantic search capability.

#### Change: Extend Check 1 section (lines 32-42)

Replace the existing Check 1 implementation guidance:

```markdown
### 1. No Duplicate Implementations? (25%)

**Check**: Search codebase for existing functionality that overlaps with the proposed implementation.

**Primary — Semantic Duplicate Detection**:
```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "Existing implementations that provide functionality similar to {proposed_feature}: functions, classes, modules, or libraries that handle {feature_description}. Include partial matches and alternative approaches."
directory_path: {project_root}
```

**Fallback — Pattern-Based Detection**:
```bash
# Use Grep to search for similar function names and signatures
# Use Glob to find modules in related directories
# Use Serena find_symbol for structural matches
```

**Evaluation Criteria**:
- Auggie returns semantically similar code -> investigate before proceeding
- Grep finds exact name matches -> likely duplicate, FAIL
- No matches from any source -> PASS

Why semantic search matters: Grep finds `validateEmail()` but misses `checkEmailFormat()` which does the same thing. Auggie finds both because it understands intent, not just text patterns.

**Circuit Breaker**: S4 standard. If Auggie unavailable, fall back to Grep+Glob (reduced detection of semantic duplicates is acceptable — note limitation in confidence output).
```

---

## Tier 2: Summary Proposals

Each Tier 2 component follows the same S1-S6 standards. Below are condensed specifications.

---

### T2-1: `src/superclaude/commands/cleanup-audit.md`

**Current frontmatter**: `mcp-servers: [sequential, serena, context7]`
**New frontmatter**: `mcp-servers: [sequential, serena, context7, auggie-mcp]`

**Integration points** (3 new query sites):
1. **Pass 1 (Surface Scan)**: Before batch assignment, use Auggie to identify dynamic loading patterns that grep misses: `"Files that are loaded dynamically via import(), require(), or configuration-driven loading in {target_path}"`
2. **Pass 2 (Structural Audit)**: Augment reference checking: `"All references to {file_under_audit} including indirect references through re-exports, barrel files, and configuration"`
3. **Pass 3 (Cross-Cutting)**: Semantic duplicate detection across file groups: `"Functional overlap between {file_a} and {file_b}: shared logic, duplicated algorithms, or equivalent implementations with different names"`

**Fallback**: Serena symbols (already available) -> Grep+Glob (existing pipeline continues).

---

### T2-2: `src/superclaude/commands/implement.md`

**Current frontmatter**: `mcp-servers: [context7, sequential, magic, playwright]`
**New frontmatter**: `mcp-servers: [context7, sequential, auggie-mcp, magic, playwright]`

**Integration points** (2 new query sites):
1. **Step 1 (Analyze)**: Find integration points: `"Where to integrate {feature_name}: existing module boundaries, similar features, relevant interfaces, and test patterns in {target_scope}"`
2. **Step 2 (Plan)**: Discover existing patterns: `"Implementation patterns used for similar features in this codebase: naming conventions, file organization, error handling, and testing approaches"`

**Fallback**: Context7 for framework patterns -> Grep for conventions.

---

### T2-3: `src/superclaude/commands/improve.md`

**Current frontmatter**: `mcp-servers: [sequential, context7]`
**New frontmatter**: `mcp-servers: [auggie-mcp, sequential, context7]`

**Integration points** (2 new query sites):
1. **Step 1 (Analyze)**: Dependency-aware improvement discovery: `"Improvement opportunities in {target_path}: complex functions, duplicated logic, outdated patterns, and their dependency chains"`
2. **Step 4 (Validate)**: Impact verification: `"All dependents of {improved_symbol} that may need updates after signature or behavior changes"`

**Fallback**: Sequential for analysis -> Grep for dependents.

---

### T2-4: `src/superclaude/commands/explain.md`

**Current frontmatter**: `mcp-servers: [sequential, context7]`
**New frontmatter**: `mcp-servers: [auggie-mcp, sequential, context7]`

**Integration points** (1 new query site):
1. **Step 1 (Analyze)**: System-level context: `"How {target_concept} works in this codebase: implementation details, data flow, integration with other components, and configuration that affects behavior"`

**Fallback**: Read target files + Sequential for reasoning.

---

### T2-5 through T2-13: Agent Definitions

All 9 HIGH-benefit agents follow a uniform integration pattern. Agents do not have `mcp-servers` frontmatter (they use `tools:` instead), so the integration is via workflow instructions rather than frontmatter changes.

#### Uniform Agent Integration Template

For each agent, add a new section titled `## Auggie MCP Integration` with:

```markdown
## Auggie MCP Integration

**When available**, use semantic codebase search as your FIRST discovery tool:

```
Tool: mcp__auggie-mcp__codebase-retrieval
information_request: "{agent_specific_query}"
directory_path: {project_root}
```

**Fallback**: If Auggie is unavailable, use your existing tools (Read, Grep, Glob) with the same search intent. Note reduced semantic matching capability in your output.

**Circuit Breaker**: 3 consecutive failures -> skip Auggie for remainder of this agent run.
```

#### Per-Agent Query Templates

| Agent | File | Primary Query Template |
|-------|------|----------------------|
| **audit-analyzer** | `agents/audit-analyzer.md` | "Structural analysis of {file_path}: imports, exports, internal dependencies, staleness indicators, and test coverage" |
| **audit-comparator** | `agents/audit-comparator.md` | "Functional overlap between {file_a} and {file_b}: shared algorithms, duplicated logic, equivalent implementations with different names, and consolidation opportunities" |
| **audit-scanner** | `agents/audit-scanner.md` | "Usage analysis for {file_path}: is this file imported anywhere, referenced in configuration, loaded dynamically, or used in build scripts?" |
| **audit-validator** | `agents/audit-validator.md` | "Independent verification: all references to {file_path} in the codebase, including indirect references through barrel files, re-exports, and dynamic loading" |
| **root-cause-analyst** | `agents/root-cause-analyst.md` | "Code paths that could produce {error_symptom}: control flow, error handlers, edge cases, and data validation related to the failing behavior" |
| **refactoring-expert** | `agents/refactoring-expert.md` | "Refactoring targets in {scope}: duplicated logic, high-coupling symbols, SOLID violations, and the dependency chain for each candidate" |
| **security-engineer** | `agents/security-engineer.md` | "Security-sensitive code paths in {scope}: authentication flows, authorization checks, input validation boundaries, cryptographic operations, and secret handling" |
| **system-architect** | `agents/system-architect.md` | "System architecture of {scope}: component boundaries, dependency graph, communication patterns, data flow, and coupling metrics" |
| **repo-index** | `agents/repo-index.md` | "Repository overview: top-level modules, entry points, service boundaries, configuration files, test directories, and documentation locations" |

**Note on agent `tools:` field**: Agents currently declare `tools: Read, Grep, Glob`. Auggie is an MCP tool invoked via `mcp__auggie-mcp__codebase-retrieval` within the agent's workflow instructions — it does not need to be listed in `tools:` (MCP tools are globally available to agents).

---

## Implementation Order

### Phase 3A: Fix Existing (Day 1)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| 1 | T1-FIX-1: task-unified.md | Small (4 edits) | Low — fixing bugs |
| 2 | T1-FIX-2: sc-task-unified SKILL.md | Small (3 edits + 1 new section) | Low — fixing bugs |

### Phase 3B: Zero-MCP Commands (Day 1-2)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| 3 | T1-NEW-1: analyze.md | Medium (frontmatter + new section) | Low — additive |
| 4 | T1-NEW-2: troubleshoot.md | Medium (frontmatter + new section) | Low — additive |
| 5 | T1-NEW-3: design.md | Medium (frontmatter + new section) | Low — additive |
| 6 | T1-NEW-4: document.md | Medium (frontmatter + new section) | Low — additive |

### Phase 3C: Augment Existing MCP (Day 2)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| 7 | T1-NEW-5: cleanup.md | Small (frontmatter + extend section) | Low — additive |
| 8 | T1-NEW-6: confidence-check SKILL.md | Small (extend Check 1) | Low — additive |

### Phase 3D: Tier 2 Commands (Day 3)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| 9 | T2-1: cleanup-audit.md | Medium | Low |
| 10 | T2-2: implement.md | Small | Low |
| 11 | T2-3: improve.md | Small | Low |
| 12 | T2-4: explain.md | Small | Low |

### Phase 3E: Tier 2 Agents (Day 3-4)

| Priority | Component | Effort | Risk |
|----------|-----------|--------|------|
| 13-17 | Audit agents (5) | Small each | Low |
| 18-21 | Other agents (4) | Small each | Low |

---

## Validation Criteria

### Per-Component Validation

Each implemented component MUST pass:

1. **Frontmatter correctness**: `auggie-mcp` present in `mcp-servers` array
2. **Tool name correctness**: All references use `mcp__auggie-mcp__codebase-retrieval` (never bare `codebase-retrieval`)
3. **Parameter completeness**: Every call site specifies both `information_request` and `directory_path`
4. **Query specificity**: No generic queries; all use domain-specific templates with `{variable}` placeholders
5. **Fallback presence**: Every Auggie call site has an explicit fallback path
6. **Progressive enhancement**: Command/skill functions correctly if Auggie section is mentally removed
7. **Circuit breaker reference**: Each component references S4 or includes inline circuit breaker spec

### Integration Validation

After all components are implemented:

1. **Grep audit**: `grep -r "codebase-retrieval" src/superclaude/` should return ZERO bare references (all must be `mcp__auggie-mcp__codebase-retrieval`)
2. **Frontmatter audit**: All commands with `auggie-mcp` in their workflow MUST have it in `mcp-servers`
3. **Sync verification**: `make verify-sync` passes after copying to `.claude/`

---

## Appendix A: Complete Query Template Registry

For reference and consistency, all query templates across all components:

```yaml
query-templates:
  # Discovery / Context Loading
  project-overview: "Project structure overview: entry points, module boundaries, dependency graph, and architectural layers for {target_path}"
  module-context: "All modules, classes, functions, imports, and test files related to {task_description} in this project"
  key-files: "Key files, entry points, and interfaces related to {task_description}"
  repo-overview: "Repository overview: top-level modules, entry points, service boundaries, configuration files, test directories, and documentation locations"

  # Impact Analysis
  downstream-full: "All files that import, reference, or depend on {changed_symbol} including transitive dependencies"
  downstream-direct: "Files that directly reference {changed_symbol}"
  dependents-after-change: "All dependents of {improved_symbol} that may need updates after signature or behavior changes"

  # Dead Code / Cleanup
  dead-code-full: "Complete dead code analysis of {target_path}: unused functions, orphaned files, unused imports, unreachable code branches, and deprecated code still present"
  dead-functions: "Functions, classes, and variables in {target_path} that are defined but never referenced elsewhere in the project"
  dead-imports: "Import statements in {target_path} where the imported symbol is never used in the importing file"
  dead-files: "Files in {target_path} that are not imported, required, or referenced by any other file in the project"
  dynamic-loading: "Files that are loaded dynamically via import(), require(), or configuration-driven loading in {target_path}"
  safe-removal: "All references to {symbol_to_remove} including dynamic imports and string-based references like reflection, eval, or configuration files"

  # Duplicate Detection
  semantic-duplicates: "Existing implementations that provide functionality similar to {proposed_feature}: functions, classes, modules, or libraries that handle {feature_description}"
  file-overlap: "Functional overlap between {file_a} and {file_b}: shared algorithms, duplicated logic, equivalent implementations with different names"
  refactoring-targets: "Refactoring targets in {scope}: duplicated logic, high-coupling symbols, SOLID violations, and the dependency chain for each candidate"

  # Troubleshooting
  error-context: "All code paths, error handlers, and control flow related to {error_description}. Include function call chains, try/catch blocks, and logging statements."
  bug-trace: "Implementation of {suspected_function}, its callers, data flow through parameters, and edge cases in validation logic"
  performance-hotspot: "Hot paths related to {slow_operation}: database queries, loop structures, memory allocations, and caching layers"

  # Security
  security-surface: "Security-sensitive code paths in {scope}: authentication flows, authorization checks, input validation boundaries, cryptographic operations, and secret handling"

  # Architecture / Design
  system-architecture: "System architecture of {scope}: component boundaries, dependency graph, communication patterns, data flow, and coupling metrics"
  existing-patterns: "Implementation patterns used for similar features in this codebase: naming conventions, file organization, error handling, and testing approaches"
  integration-points: "Where to integrate {feature_name}: existing module boundaries, similar features, relevant interfaces, and test patterns in {target_scope}"

  # Documentation
  component-interface: "Complete interface of {target_component}: public methods with signatures, parameters with types, return values, class hierarchy, usage examples in tests, and existing documentation comments"
  api-surface: "All API endpoints in {target_path}: HTTP methods, URL patterns, request/response schemas, authentication requirements, and error responses"

  # Testing
  test-coverage: "Test files and test functions that exercise {changed_file} functionality"
  usage-verification: "Usage analysis for {file_path}: is this file imported anywhere, referenced in configuration, loaded dynamically, or used in build scripts?"

  # Audit
  structural-analysis: "Structural analysis of {file_path}: imports, exports, internal dependencies, staleness indicators, and test coverage"
  reference-verification: "Independent verification: all references to {file_path} in the codebase, including indirect references through barrel files, re-exports, and dynamic loading"
  system-explanation: "How {target_concept} works in this codebase: implementation details, data flow, integration with other components, and configuration that affects behavior"
```

---

## Appendix B: Deprecated Component — task-mcp.md

`src/superclaude/commands/task-mcp.md` is deprecated (replaced by `task-unified.md`). Per Wave 1 analysis, it contains the same defects as `task-unified.md`.

**Recommendation**: Do NOT invest in fixing `task-mcp.md`. Add a deprecation notice pointing to `task-unified.md` if one does not already exist. If the file is removed in a future cleanup, no Auggie integration is lost.

---

## Appendix C: Verification Script

After implementation, run this validation:

```bash
#!/usr/bin/env bash
# auggie-mcp-integration-verify.sh
set -euo pipefail

ERRORS=0

echo "=== Auggie MCP Integration Verification ==="

# Check 1: No bare codebase-retrieval references
echo -n "Check 1: No bare codebase-retrieval references... "
BARE=$(grep -rn "codebase-retrieval" src/superclaude/ --include="*.md" | grep -v "mcp__auggie-mcp__codebase-retrieval" | grep -v "deprecated" | grep -v "BEFORE" || true)
if [ -z "$BARE" ]; then
  echo "PASS"
else
  echo "FAIL"
  echo "$BARE"
  ERRORS=$((ERRORS + 1))
fi

# Check 2: All Tier 1 commands have auggie-mcp in frontmatter
echo -n "Check 2: Tier 1 commands have auggie-mcp in mcp-servers... "
for cmd in analyze troubleshoot design document cleanup task-unified; do
  if ! grep -q "auggie-mcp" "src/superclaude/commands/${cmd}.md"; then
    echo "FAIL: ${cmd}.md missing auggie-mcp"
    ERRORS=$((ERRORS + 1))
  fi
done
echo "PASS"

# Check 3: All Auggie call sites have directory_path
echo -n "Check 3: directory_path mentioned at all call sites... "
# This is a heuristic check
AUGGIE_REFS=$(grep -c "mcp__auggie-mcp__codebase-retrieval" src/superclaude/commands/*.md src/superclaude/skills/*/SKILL.md 2>/dev/null || echo 0)
DIR_REFS=$(grep -c "directory_path" src/superclaude/commands/*.md src/superclaude/skills/*/SKILL.md 2>/dev/null || echo 0)
echo "Auggie refs: $AUGGIE_REFS, directory_path refs: $DIR_REFS"

# Check 4: Sync verification
echo -n "Check 4: Source and .claude/ in sync... "
make verify-sync 2>/dev/null && echo "PASS" || echo "FAIL (run make sync-dev)"

echo ""
echo "=== Results: $ERRORS errors ==="
exit $ERRORS
```
