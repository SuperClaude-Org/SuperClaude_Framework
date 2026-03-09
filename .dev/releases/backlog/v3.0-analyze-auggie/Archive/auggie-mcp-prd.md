# PRD: Auggie MCP Framework-Wide Integration

**Version**: 1.0.0
**Date**: 2026-02-20
**Status**: Draft - Pending Review
**Authors**: System Architect (Wave 1 Analysis Synthesis)
**Supersedes**: v1.2-analyze-auggie backlog (single-command scope)
**Wave 1 Analysis**: `docs/generated/auggie-mcp-wave1-consolidated.md`

---

## 1. Executive Summary

This specification defines the framework-wide integration of Auggie MCP (`mcp__auggie-mcp__codebase-retrieval`) across SuperClaude's command, agent, and skill ecosystem. Wave 1 analysis evaluated 59 components and found that only 3 reference Auggie today -- all with CRITICAL defects (wrong tool name, missing required parameters, absent frontmatter). Meanwhile, 17 additional HIGH-priority components would gain substantial capability from semantic code search but have no integration at all. This PRD replaces the narrow v1.2 backlog (which targeted only `/sc:analyze`) with a phased rollout across 6 milestones: fixing existing defects, filling zero-MCP-server gaps, extending to code quality and implementation commands, integrating 9 HIGH-benefit agents, and standardizing cross-cutting patterns (circuit breaker, fallback chain, frontmatter conventions) framework-wide.

---

## 2. Problem Statement

### 2.1 Current State

SuperClaude Framework v4.2.0 contains approximately 65 instructional components (30 commands, 25+ agents, 5 skills) that orchestrate Claude Code's behavior. Auggie MCP -- a semantic code search engine with real-time codebase indexing -- is available as an MCP server but is effectively unused:

| Metric | Value |
|--------|-------|
| Components referencing Auggie | 3 of ~65 (4.6%) |
| Components with correct invocation | 0 of 3 (0%) |
| Components listing `auggie-mcp` in frontmatter | 0 of 30 commands |
| Commands with zero MCP servers at all | 4 (`analyze`, `troubleshoot`, `document`, `design`) |

### 2.2 Defects in Existing Uses

All three components that reference Auggie (`task-unified.md`, `task-mcp.md`, `sc-task-unified/SKILL.md`) share identical defects:

| Defect | Severity | Detail |
|--------|----------|--------|
| Wrong tool name | CRITICAL | Uses `codebase-retrieval` instead of `mcp__auggie-mcp__codebase-retrieval` |
| Missing `directory_path` | CRITICAL | Required parameter never specified |
| Missing `information_request` guidance | HIGH | No query templates or domain-specific guidance |
| Not in `mcp-servers:` frontmatter | HIGH | `auggie-mcp` absent; Claude Code cannot select the server |
| No fallback behavior | MEDIUM | No degradation path when Auggie is unavailable |
| Fabricated syntax | MEDIUM | `codebase-retrieval/view` (task-unified L170) does not exist |

### 2.3 Capability Gaps

Four commands (`analyze`, `troubleshoot`, `document`, `design`) have **zero MCP servers** in their frontmatter and would benefit most from semantic search. These represent the largest capability gaps in the framework: commands that perform codebase analysis or need codebase understanding but have no tool integration to support that work.

### 2.4 Why This Matters

Semantic code search fundamentally changes what instructional components can accomplish. Pattern-based tools (Grep, Glob) require the author to anticipate exact strings. Auggie's embedding-based retrieval finds functionally related code even when naming conventions vary, catches dynamic loading patterns that static grep misses, and maps cross-module dependencies that require multi-hop reasoning. Without it, commands like `/sc:analyze` rely on Claude's native reasoning over raw file reads -- effective for small codebases but brittle at scale.

---

## 3. Solution Overview

### 3.1 Architecture Principle: Progressive Enhancement

Every integration follows: **works without Auggie, works BETTER with it.** No component shall require Auggie for basic functionality. This aligns with MCP.md's "preferred not required" principle and the v1.2 backlog's progressive enhancement design.

### 3.2 Integration Pattern

```
mcp__auggie-mcp__codebase-retrieval (semantic discovery)
  --> mcp__serena__find_symbol + find_referencing_symbols (structural verification)
  --> Grep + Glob (pattern confirmation)
  --> Read + manual guidance (last resort)
```

Auggie narrows the search space semantically. Downstream tools verify and refine. This funnel pattern applies to every integration point.

### 3.3 Standard Tool Invocation

All integrations must use the exact tool specification:

```yaml
tool: mcp__auggie-mcp__codebase-retrieval
parameters:
  directory_path: "{project_root}"       # REQUIRED - absolute path
  information_request: "{domain_query}"  # REQUIRED - natural language query
```

### 3.4 Circuit Breaker Standard

3 consecutive failures causes OPEN state (30s timeout). After timeout, HALF_OPEN (single test call). Success returns to CLOSED. Consistent with MCP.md circuit breaker configuration.

### 3.5 Relationship to v1.2 Backlog

The existing v1.2-analyze-auggie backlog produced a comprehensive feature spec, debate transcript, and 6 milestone task lists -- all targeting only `/sc:analyze`. None of this has been implemented in code. This PRD incorporates that work directly into M2 (`analyze` command integration) and reuses the following assets framework-wide:

| Backlog Asset | Reuse in This PRD |
|---------------|-------------------|
| Circuit breaker template | Cross-cutting standard (Section 5.1) |
| Progressive enhancement principle | Architecture principle (Section 3.1) |
| Degradation feedback pattern | Fallback behavior standard (Section 5.2) |
| `/sc:analyze` feature spec | Incorporated into M2 deliverables |
| M1-foundation.md checklist | Basis for M6 onboarding documentation |

---

## 4. Milestones

### M1: Fix Existing Uses

**Objective**: Correct all CRITICAL and HIGH defects in the 3 components that already reference Auggie.

**Scope**: `task-unified.md`, `sc-task-unified/SKILL.md`. (`task-mcp.md` is deprecated and excluded.)

#### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 1.1 | Tool name correction | Replace all instances of `codebase-retrieval` with `mcp__auggie-mcp__codebase-retrieval` |
| 1.2 | Required parameters | Add `directory_path` and `information_request` to every invocation site |
| 1.3 | Frontmatter update | Add `auggie-mcp` to `mcp-servers:` in command frontmatter |
| 1.4 | Fabricated syntax removal | Remove `codebase-retrieval/view` reference (task-unified L170) |
| 1.5 | Fallback behavior | Add circuit breaker + fallback chain (Auggie -> Serena -> Grep -> Read) |
| 1.6 | Query templates | Add domain-specific `information_request` templates for task workflows |

#### Acceptance Criteria

- [ ] Zero instances of bare `codebase-retrieval` remain in `task-unified.md` or `sc-task-unified/SKILL.md`
- [ ] Every Auggie invocation includes both `directory_path` and `information_request`
- [ ] `auggie-mcp` appears in `mcp-servers:` frontmatter of `task-unified.md`
- [ ] Fallback chain is documented and activates when Auggie is unavailable
- [ ] `codebase-retrieval/view` syntax is removed
- [ ] `task-mcp.md` is not modified (deprecated)

#### Dependencies

- None (standalone fix)

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Behavioral regression in task workflow | Low | Medium | Test with and without Auggie available |
| Frontmatter format incompatibility | Low | Low | Validate against existing command frontmatter patterns |

---

### M2: Zero-MCP-Server Commands

**Objective**: Integrate Auggie into the 4 commands that currently have no MCP servers and HIGH benefit ratings.

**Scope**: `analyze.md`, `troubleshoot.md`, `design.md`, `document.md`

**Predecessor**: The v1.2 backlog's `/sc:analyze` feature spec (v2.0.0) is directly incorporated here. Its 10 prioritized enhancements, tier specifications, and evidence chain structure apply to the `analyze` command deliverable.

**Implementation Guide**: Deliverable 2.1 (`analyze.md` integration) SHALL use `.dev/releases/backlog/v1.2-analyze-auggie/sc-analyze-auggie-feature-spec.md` as its detailed implementation guide, incorporating:
- **FR-3** depth tier specifications (time/token budgets per quick/deep/comprehensive)
- **FR-10** tier-to-analysis mapping (STRICT→aggressive+deep, STANDARD→balanced+deep, LIGHT→minimal+quick, EXEMPT→minimal+quick)
- **FR-11** language-aware query templates (Python, JS/TS, Go, Java security/quality/performance)
- **AT-1 through AT-8** Gherkin acceptance tests as formal test specifications
- **NFR-1 through NFR-6** as measurable success criteria for the analyze command specifically
- **AD-2** phase-based pipeline structure (Classify→Discover→Analyze→Synthesize→Report)

The following v1.2 features are deferred to M6.9: FR-7 (cross-session memory), FR-9 (--aggressiveness flag), FR-12 (iterative refinement), FR-13 (hybrid validation), FR-14 (quality scoring), AD-4 (progressive disclosure implementation), AD-5 (hybrid validation pipeline).

#### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 2.1 | `analyze.md` integration | Full Auggie integration per v1.2 feature spec: semantic discovery, multi-domain analysis, depth-tiered execution (quick/deep/comprehensive), progressive disclosure, circuit breaker, language-aware query templates |
| 2.2 | `troubleshoot.md` integration | Semantic code path tracing for root cause analysis; query templates for error propagation, exception handling flows, state mutation tracking |
| 2.3 | `design.md` integration | Existing system mapping before architectural design; query templates for component boundaries, dependency graphs, interaction patterns |
| 2.4 | `document.md` integration | Code understanding for documentation accuracy; query templates for API surface discovery, usage patterns, internal contracts |
| 2.5 | Frontmatter additions | Add `auggie-mcp` (and appropriate secondary servers) to `mcp-servers:` for all 4 commands |
| 2.6 | Fallback behavior | Consistent circuit breaker + fallback chain across all 4 commands |

#### Acceptance Criteria

- [ ] All 4 commands list `auggie-mcp` in `mcp-servers:` frontmatter
- [ ] Each command has at least 3 domain-specific `information_request` query templates
- [ ] Each command functions correctly when Auggie is unavailable (progressive enhancement)
- [ ] `analyze.md` implements the v1.2 feature spec's depth-tiered execution model (FR-3)
- [ ] `analyze.md` includes tier-to-analysis mapping per FR-10 (STRICT/STANDARD/LIGHT/EXEMPT → aggressiveness/depth)
- [ ] `analyze.md` includes language-aware query templates per FR-11 (Python, JS/TS, Go, Java)
- [ ] `analyze.md` passes AT-1 through AT-8 acceptance tests from v1.2 feature spec
- [ ] `analyze.md` meets NFR targets: ≥85% precision, ≥90% recall, p95 latency <30s (quick) / <90s (deep)
- [ ] `troubleshoot.md` includes semantic code path tracing workflow
- [ ] `design.md` includes existing system mapping step before design proposals
- [ ] `document.md` includes code understanding step before documentation generation
- [ ] Circuit breaker behavior is identical across all 4 commands

#### Dependencies

- M1 (establishes patterns for tool name, parameters, frontmatter, fallback)

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep from v1.2 feature spec | Medium | Medium | Implement core integration first; P2/P3 enhancements (cross-session memory, iterative refinement) deferred to M6 |
| Query template quality | Medium | Low | Start with 3 templates per command; iterate based on usage |
| Token budget overrun with Auggie calls | Low | Medium | Apply v1.2's adaptive token budgeting: quick=1-2 calls, deep=5-10, comprehensive=15-25 |
| Latency targets missed without parallelism | Low | Medium | Implement FR-6 (parallel query execution) for independent focus areas; 50% latency improvement expected |

---

### M3: Code Quality Commands + Confidence-Check Skill

**Objective**: Integrate Auggie into commands and skills focused on code quality assessment, where semantic search has the highest precision advantage over pattern matching.

**Scope**: `cleanup.md`, `cleanup-audit.md`, `improve.md`, `confidence-check` skill, `sc-cleanup-audit` skill

#### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 3.1 | `cleanup.md` integration | Dead code detection via semantic search (catches dynamically loaded modules, convention-variant names); query templates for unused exports, orphaned utilities, dead feature flags |
| 3.2 | `cleanup-audit.md` integration | Enhance existing 3-pass audit pipeline: semantic duplicate detection in structural pass, dynamic loading pattern detection in surface scan, cross-cutting dependency analysis |
| 3.3 | `improve.md` integration | Dependency-aware improvement discovery; query templates for coupling analysis, abstraction opportunities, pattern violations |
| 3.4 | `confidence-check` skill | Auggie integration for Check 1 (duplicate detection, 25% of confidence score): find functional equivalents that grep misses due to naming variation |
| 3.5 | `sc-cleanup-audit` skill | Auggie integration in audit rules: reduce false DELETE findings by verifying dynamic usage, detect semantic duplicates across modules |
| 3.6 | Frontmatter + fallback | Consistent `mcp-servers:` additions and circuit breaker across all components |

#### Acceptance Criteria

- [ ] `cleanup.md` includes semantic dead code detection workflow
- [ ] `cleanup-audit.md` enhances each of its 3 passes with Auggie query templates
- [ ] `improve.md` uses Auggie for dependency analysis before suggesting improvements
- [ ] `confidence-check` skill's Check 1 uses Auggie for functional duplicate detection
- [ ] `sc-cleanup-audit` skill's DELETE classification verifies dynamic usage via Auggie
- [ ] All components function correctly without Auggie (progressive enhancement)
- [ ] False positive rate for dead code detection is measurably lower with Auggie enabled

#### Dependencies

- M1 (patterns), M2 (validates integration approach at scale)

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Dead code false negatives (Auggie misses dynamic loads) | Medium | High | Auggie narrows candidates; Grep/Read verify before DELETE recommendation |
| Confidence-check scoring disruption | Low | Medium | Auggie result is additive to existing checks, not replacing |
| Audit pipeline performance with added Auggie calls | Medium | Medium | Budget 2-3 Auggie calls per audit pass; use caching for repeated queries |

---

### M4: Implementation Commands + Tier 2 Commands

**Objective**: Extend Auggie to commands focused on code creation and explanation, plus MEDIUM-benefit Tier 2 candidates.

**Scope**: `implement.md`, `explain.md`, plus Tier 2 candidates: `estimate.md`, `index.md`, `test.md`, `workflow.md`

#### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 4.1 | `implement.md` integration | Finding integration points and existing patterns before implementation; query templates for similar implementations, API contracts, convention discovery |
| 4.2 | `explain.md` integration | System-level context for explanations; query templates for related components, usage patterns, dependency chains |
| 4.3 | `estimate.md` integration (MEDIUM) | Codebase complexity assessment for effort estimation; query templates for similar past implementations, affected component count |
| 4.4 | `index.md` integration (MEDIUM) | Semantic codebase indexing for command catalog browsing |
| 4.5 | `test.md` integration (MEDIUM) | Finding existing test patterns and coverage gaps; query templates for untested code paths, test utility discovery |
| 4.6 | `workflow.md` integration (MEDIUM) | Workflow step discovery and dependency mapping |
| 4.7 | Frontmatter + fallback | Consistent integration across all components |

#### Acceptance Criteria

- [ ] `implement.md` includes pattern discovery step before code generation
- [ ] `explain.md` includes related component discovery for contextual explanations
- [ ] All Tier 2 commands have `auggie-mcp` in frontmatter with `optional` designation
- [ ] All components function correctly without Auggie
- [ ] Each command has at least 2 domain-specific query templates

#### Dependencies

- M2 (validates zero-MCP-server integration), M3 (validates quality-domain patterns)

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Diminishing returns on MEDIUM candidates | Medium | Low | MEDIUM integrations are optional; track usage to validate benefit |
| `implement.md` over-reliance on Auggie for pattern discovery | Low | Medium | Auggie provides suggestions; implementation decisions remain with the developer |
| Scope expansion pressure from remaining commands | Low | Low | Remaining commands explicitly excluded; revisit in future release |

---

### M5: Agent Integrations

**Objective**: Integrate Auggie into the 9 HIGH-benefit agent definitions, prioritizing the 5 audit agents as highest ROI.

**Scope**: `audit-analyzer.md`, `audit-comparator.md`, `audit-scanner.md`, `audit-validator.md`, `audit-consolidator.md` (added as MEDIUM with audit affinity), `root-cause-analyst.md`, `refactoring-expert.md`, `security-engineer.md`, `system-architect.md`, `repo-index.md`

#### Deliverables

| # | Deliverable | Sub-group | Description |
|---|-------------|-----------|-------------|
| 5.1 | `audit-analyzer.md` | Audit | Add Auggie as primary discovery tool for deep structural auditing; query templates for architectural pattern detection, dependency analysis |
| 5.2 | `audit-comparator.md` | Audit | Semantic duplicate detection across modules; query templates for functional equivalence, shared responsibility detection |
| 5.3 | `audit-scanner.md` | Audit | Dynamic loading pattern detection; query templates for runtime imports, convention-variant naming, metaprogramming patterns |
| 5.4 | `audit-validator.md` | Audit | Independent verification via different search approach; query templates for cross-referencing audit findings |
| 5.5 | `audit-consolidator.md` | Audit | Cross-audit synthesis with semantic grouping of related findings |
| 5.6 | `root-cause-analyst.md` | Analysis | Semantic code path tracing for bug investigation; query templates for error propagation, state mutation chains |
| 5.7 | `refactoring-expert.md` | Quality | Duplication detection and coupling analysis; query templates for functional equivalents, abstraction candidates |
| 5.8 | `security-engineer.md` | Security | Auth flow and data path discovery across inconsistent naming; query templates for authentication chains, data sanitization paths, privilege escalation vectors |
| 5.9 | `system-architect.md` | Architecture | Dependency mapping and component boundary analysis; query templates for module interfaces, coupling metrics, boundary violations |
| 5.10 | `repo-index.md` | Discovery | Full codebase understanding (entire purpose is codebase analysis); query templates for project structure, technology stack, entry points |

#### Acceptance Criteria

- [ ] All 10 agent definitions include Auggie as a listed tool with correct invocation syntax
- [ ] Each agent has at least 3 domain-specific `information_request` query templates
- [ ] Agent definitions include fallback instructions when Auggie is unavailable
- [ ] Audit agents (5.1-5.5) form a coherent pipeline where Auggie queries are complementary, not redundant
- [ ] `repo-index.md` uses Auggie as its primary discovery mechanism
- [ ] Agent definitions do not require Auggie for basic functionality

#### Dependencies

- M1-M3 (establishes all patterns; agents reference commands that should already be integrated)

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Agent tool list bloat | Medium | Low | Auggie replaces some Grep/Read usage; net tool count should remain stable |
| Inconsistent query patterns across audit agents | Medium | Medium | Define shared query template library for audit domain in M6 |
| Agent performance with added MCP calls | Low | Medium | Agents already use Sequential/Serena; Auggie adds 1-3 calls per invocation |

---

### M6: Cross-Cutting Standardization

**Objective**: Ensure consistency, documentation, and maintainability of all Auggie integrations across the framework.

**Scope**: Framework-wide standards, documentation, query template libraries, testing, and monitoring.

#### Deliverables

| # | Deliverable | Description |
|---|-------------|-------------|
| 6.1 | Circuit breaker standard | Document and verify consistent circuit breaker behavior (3 failures -> OPEN 30s) across all integrated components |
| 6.2 | Fallback chain standard | Document and verify consistent fallback chain (Auggie -> Serena -> Grep -> Read) across all integrated components |
| 6.3 | `mcp-servers:` frontmatter conventions | Document standard for how `auggie-mcp` appears in frontmatter: position, optional/preferred/mandatory designation, interaction with other servers |
| 6.4 | Query template library | Consolidated library of domain-specific `information_request` templates organized by command domain (analysis, quality, security, implementation, documentation, architecture) |
| 6.5 | Token budget guidelines | Per-component Auggie call budgets: quick operations (1-2 calls), standard (3-5), comprehensive (10-25). Document budget multipliers for codebase size. |
| 6.6 | MCP.md updates | Add Auggie MCP section to MCP.md consistent with existing server documentation (activation patterns, workflow process, integration commands, error recovery) |
| 6.7 | ORCHESTRATOR.md updates | Update routing tables, tool selection logic, and auto-activation triggers to include Auggie MCP |
| 6.8 | Compliance audit | Verify all M1-M5 deliverables against standards defined in 6.1-6.5; produce compliance report |
| 6.9 | v1.2 backlog P2/P3 enhancements | Implement deferred v1.2 features where applicable framework-wide. Source: `.dev/releases/backlog/v1.2-analyze-auggie/sc-analyze-auggie-feature-spec.md`. Deferred items: FR-7 cross-session memory via Serena (ROI 6.71), FR-9 --aggressiveness flag (ROI 6.10), FR-12 iterative query refinement (ROI 6.23), FR-13 hybrid validation pipeline (ROI 6.11), FR-14 quality scoring (ROI 5.53), AD-4 progressive disclosure implementation (ROI 7.01), AD-5 hybrid validation pipeline design (ROI 6.11) |

#### Acceptance Criteria

- [ ] Every component integrated in M1-M5 passes compliance audit against 6.1-6.5 standards
- [ ] MCP.md contains a complete Auggie MCP section with activation patterns, workflow, fallbacks, and circuit breaker config
- [ ] ORCHESTRATOR.md routing tables include Auggie in tool selection logic and auto-activation triggers
- [ ] Query template library contains at least 30 templates across 6 domains
- [ ] Token budget guidelines cover all integrated commands and agents
- [ ] Frontmatter convention is documented and consistently applied

#### Dependencies

- M1-M5 (all integrations must be complete before standardization audit)

#### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Standardization reveals inconsistencies requiring M1-M5 rework | High | Medium | Build compliance checks into M1-M5 acceptance criteria to minimize rework |
| Documentation scope creep | Medium | Low | Scope to Auggie-specific documentation only; do not refactor unrelated MCP.md sections |
| v1.2 P2/P3 features add complexity | Medium | Medium | Implement only where framework-wide benefit is validated; defer single-command enhancements |

---

## 5. Cross-Cutting Concerns

### 5.1 Circuit Breaker Standardization

All Auggie integrations must implement the same circuit breaker pattern, consistent with MCP.md's existing per-server configuration:

```yaml
circuit_breaker:
  server: auggie-mcp
  threshold: 3          # consecutive failures to trigger OPEN
  timeout: 30s          # duration in OPEN state before testing
  states:
    CLOSED: "Normal operation - all Auggie calls proceed"
    OPEN: "Auggie unavailable - fallback chain active"
    HALF_OPEN: "Single test call to check recovery"
  transitions:
    CLOSED_to_OPEN: "failures >= 3"
    OPEN_to_HALF_OPEN: "timeout elapsed (30s)"
    HALF_OPEN_to_CLOSED: "test call succeeds"
    HALF_OPEN_to_OPEN: "test call fails (extend timeout)"
```

### 5.2 Fallback Behavior Consistency

Every integration point must implement the same 4-tier fallback chain:

| Tier | Tool | Type | When Used |
|------|------|------|-----------|
| 1 | `mcp__auggie-mcp__codebase-retrieval` | Semantic | Primary - circuit breaker CLOSED |
| 2 | `mcp__serena__find_symbol` + `find_referencing_symbols` | Structural | Auggie unavailable, symbol-based query |
| 3 | `Grep` + `Glob` | Pattern | Auggie + Serena unavailable |
| 4 | `Read` + manual guidance | Last resort | All MCP servers unavailable |

Components must not silently degrade. When operating in fallback mode, the component should indicate reduced capability:

- Tier 2 fallback: Note that semantic search is unavailable; structural search may miss non-obvious relationships
- Tier 3 fallback: Note that pattern matching requires exact strings; may miss convention-variant code
- Tier 4 fallback: Note that manual file reading is active; results limited to explicitly specified paths

### 5.3 Token Budget Framework

| Operation Type | Auggie Calls | Token Overhead | Justification |
|----------------|-------------|----------------|---------------|
| Quick/smoke | 1-2 | ~500-1K | Narrow discovery for fast feedback |
| Standard | 3-5 | ~1.5-3K | Balanced discovery + verification |
| Deep/comprehensive | 10-25 | ~5-15K | Exhaustive discovery for audit-grade analysis |

**Codebase size multipliers** (from v1.2 feature spec):
- Small (<100 files): 0.5x budget
- Medium (100-500 files): 1.0x budget
- Large (500-2000 files): 1.5x budget
- Enterprise (2000+ files): 2.0x budget

### 5.4 `mcp-servers:` Frontmatter Conventions

Standard format for including Auggie in command frontmatter:

```yaml
mcp-servers:
  - auggie-mcp          # Semantic code search (preferred)
  - sequential          # Structured analysis
  - context7            # Documentation lookup
```

Designation levels for instructional text within the command:
- **MANDATORY**: Command workflow explicitly requires Auggie call; abort analysis tier if unavailable
- **PREFERRED**: Command workflow includes Auggie call; proceed with fallback if unavailable
- **OPTIONAL**: Auggie available for enhanced results; no workflow change if unavailable

Most integrations should use PREFERRED. Only `analyze --depth comprehensive` uses MANDATORY.

---

## 6. Success Metrics

| Metric | Baseline (Current) | Target (Post-M6) | Measurement Method |
|--------|-------------------|-------------------|-------------------|
| Components with correct Auggie integration | 0 | 20+ (all HIGH candidates) | Grep for `mcp__auggie-mcp__codebase-retrieval` with both required params |
| Components with `auggie-mcp` in frontmatter | 0 | 13+ commands | Frontmatter audit |
| Commands with zero MCP servers | 4 | 0 | Frontmatter audit |
| Existing defects (wrong name, missing params) | 6 CRITICAL/HIGH | 0 | Grep for bare `codebase-retrieval` without `mcp__auggie-mcp__` prefix |
| Circuit breaker consistency | Undefined | 100% of integrated components | Compliance audit (M6.8) |
| Fallback chain consistency | Undefined | 100% of integrated components | Compliance audit (M6.8) |
| Query template coverage | 0 | 30+ domain-specific templates | Template library count (M6.4) |
| Agent integrations | 0 | 9-10 HIGH-benefit agents | Agent definition audit |
| **Quality: analyze precision** | ~40% | ≥85% | Human review of 100 random findings (v1.2 NFR-3) |
| **Quality: analyze recall** | ~60% | ≥90% | Comparison against known issue sets (v1.2 NFR-4) |
| **Quality: analyze false positive rate** | ~50% | <10% | User dismissal tracking (v1.2 NFR-3) |
| **Performance: analyze latency (quick)** | 20-40s | p95 <30s | Wall clock time (v1.2 NFR-2) |
| **Performance: analyze latency (deep)** | 60-180s | p95 <90s | Wall clock time (v1.2 NFR-2) |
| **Efficiency: MCP overhead** | N/A | <15% | Protocol profiling (v1.2 NFR-6) |
| **Reliability: analysis completion rate** | N/A | 99% | Degradation tracking (v1.2 NFR-5) |

---

## 7. Risk Register

| ID | Risk | Probability | Impact | Mitigation | Owner | Status |
|----|------|------------|--------|------------|-------|--------|
| R1 | Auggie MCP server unavailability during rollout | Medium | High | All integrations built as progressive enhancement; fallback chain tested before each milestone | M1 | Open |
| R2 | Wrong tool name propagation (copy-paste from existing defects) | Medium | Critical | M1 fixes all existing defects first; M6 compliance audit catches any new instances | M1 | Open |
| R3 | Query template quality insufficient for real-world use | Medium | Medium | Start with 3 templates per component; iterate based on usage feedback; maintain template library | M2-M5 | Open |
| R4 | Token budget overrun from excessive Auggie calls | Low | Medium | Enforce per-operation call budgets (Section 5.3); monitor token usage during integration testing | M2 | Open |
| R5 | Inconsistent circuit breaker implementation across milestones | High | Medium | Define standard in M1; build compliance check into each milestone's acceptance criteria | M6 | Open |
| R6 | v1.2 backlog feature spec scope creep into M2 | Medium | Medium | Implement only core Auggie integration in M2; defer P2/P3 enhancements to M6.9 | M2 | Open |
| R7 | Audit agent pipeline redundancy (5 agents querying same things) | Medium | Low | Define complementary query domains per agent in M5; audit-consolidator deduplicates | M5 | Open |
| R8 | Frontmatter format changes break existing command parsing | Low | High | Validate frontmatter format against existing commands before M2; no structural changes to frontmatter schema | M2 | Open |
| R9 | `task-mcp.md` deprecated but still referenced elsewhere | Low | Low | M1 excludes task-mcp; verify no active references remain; document deprecation | M1 | Open |
| R10 | Framework documentation (MCP.md, ORCHESTRATOR.md) falls out of sync | Medium | Medium | M6 includes explicit documentation deliverables; compliance audit verifies consistency | M6 | Open |

---

## 8. Appendix: Validated Candidates from Wave 1

### A. HIGH Benefit -- Implement in M1-M5

#### Commands (9)

| Command | Current MCP Servers | Integration Mode | Milestone | Key Rationale |
|---------|-------------------|-----------------|-----------|---------------|
| `analyze` | [] (empty) | MANDATORY | M2 | Core semantic search use case; v1.2 backlog target |
| `troubleshoot` | [] (empty) | MANDATORY | M2 | Root cause analysis requires semantic code tracing |
| `cleanup` | [sequential, context7] | MANDATORY | M3 | Dead code detection is a semantic problem |
| `cleanup-audit` | [sequential, serena, context7] | PREFERRED | M3 | Enhances existing 3-pass pipeline |
| `implement` | [context7, sequential, magic, playwright] | PREFERRED | M4 | Finding integration points + existing patterns |
| `improve` | [sequential, context7] | PREFERRED | M3 | Dependency-aware improvement discovery |
| `explain` | [sequential, context7] | PREFERRED | M4 | System-level context for explanations |
| `document` | [] (empty) | PREFERRED | M2 | Documentation accuracy requires code understanding |
| `design` | [] (empty) | PREFERRED | M2 | Architecture design needs existing system map |

#### Agents (9)

| Agent | Milestone | Key Rationale |
|-------|-----------|---------------|
| `audit-analyzer` | M5 | Deep structural auditing requires semantic file understanding |
| `audit-comparator` | M5 | Cross-cutting duplication detection is inherently semantic |
| `audit-scanner` | M5 | Dynamic loading pattern detection exceeds grep capability |
| `audit-validator` | M5 | Independent verification needs different search approach |
| `root-cause-analyst` | M5 | Bug tracing requires semantic code path understanding |
| `refactoring-expert` | M5 | Duplication detection + coupling analysis are semantic |
| `security-engineer` | M5 | Finding auth flows, data paths across inconsistent naming |
| `system-architect` | M5 | Dependency mapping + component boundary analysis |
| `repo-index` | M5 | Entire purpose is codebase understanding |

#### Skills (2)

| Skill | Milestone | Key Rationale |
|-------|-----------|---------------|
| `sc-cleanup-audit` | M3 | Reduces false DELETE; semantic duplicate detection; dynamic loading |
| `confidence-check` | M3 | Check 1 (25% of score) needs semantic search for functional equivalents |

### B. MEDIUM Benefit -- Implement in M4 or Defer

#### Commands (9)

`estimate`, `index`, `test`, `workflow`, `task`, `spawn`, `brainstorm`, `spec-panel`, `roadmap`

#### Agents (9)

`backend-architect`, `performance-engineer`, `quality-engineer`, `python-expert`, `frontend-architect`, `devops-architect`, `audit-consolidator`, `pm-agent`, `self-review`

#### Skills (2)

`sc-task-unified` (already referenced; needs concrete query patterns), `sc-roadmap` (replaces TBD paths with actual file paths)

### C. Excluded -- No Implementation

#### Commands (11)

`build`, `select-tool`, `pm`, `review-translation`, `research`, `recommend`, `reflect`, `help`, `git`, `load`, `save`

#### Agents (7)

`technical-writer`, `learning-guide`, `socratic-mentor`, `requirements-analyst`, `deep-research`, `deep-research-agent`, `business-panel-experts`

#### Skills (1)

`sc-validate-tests` (pure YAML rules engine; no codebase search involved)

### D. Existing Uses -- Fix in M1

| Component | Status | Defects |
|-----------|--------|---------|
| `task-unified.md` | CRITICAL | Wrong tool name, missing params, no frontmatter, fabricated syntax, no fallback |
| `sc-task-unified/SKILL.md` | CRITICAL | Wrong tool name, missing params, no frontmatter, no fallback |
| `task-mcp.md` | DEPRECATED | Excluded from fixes (deprecated_by: task-unified) |

---

## 9. Milestone Dependency Graph

```
M1 (Fix Existing)
 |
 v
M2 (Zero-MCP Commands) ----+
 |                          |
 v                          v
M3 (Code Quality)      M4 (Implementation + Tier 2)
 |                          |
 +----------+---------------+
            |
            v
         M5 (Agents)
            |
            v
         M6 (Standardization)
```

M1 is prerequisite for all subsequent work. M2 and M3 can begin in parallel after M1. M4 depends on M2 and M3 establishing patterns. M5 depends on M1-M3. M6 depends on all prior milestones.

---

*Generated from Wave 1 consolidated analysis (7 parallel agents, 59 components evaluated). See `docs/generated/auggie-mcp-wave1-consolidated.md` for full analysis data.*
