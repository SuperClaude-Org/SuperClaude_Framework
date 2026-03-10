---
name: brainstorm
description: "Interactive requirements discovery through Socratic dialogue and systematic exploration"
category: orchestration
complexity: advanced
mcp-servers: [sequential, context7, magic, playwright, morphllm, serena, auggie-mcp]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
---

# /sc:brainstorm - Interactive Requirements Discovery

> **Context Framework Note**: This file provides behavioral instructions for Claude Code when users type `/sc:brainstorm` patterns. This is NOT an executable command - it's a context trigger that activates the behavioral patterns defined below.

## Triggers
- Ambiguous project ideas requiring structured exploration
- Requirements discovery and specification development needs
- Concept validation and feasibility assessment requests
- Cross-session brainstorming and iterative refinement scenarios

## Context Trigger Pattern
```
/sc:brainstorm [topic/idea] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel] [--codebase] [--no-codebase]
```
**Usage**: Type this pattern in your Claude Code conversation to activate brainstorming behavioral mode with systematic exploration and multi-persona coordination.

## Behavioral Flow
0. **Codebase Context**: Detect code-relevance of topic → load codebase context via Auggie MCP → present upfront briefing
1. **Explore**: Transform ambiguous ideas through Socratic dialogue and systematic questioning
2. **Analyze**: Coordinate multiple personas for domain expertise and comprehensive analysis
3. **Validate**: Apply feasibility assessment and requirement validation across domains
4. **Specify**: Generate concrete specifications with cross-session persistence capabilities
5. **Handoff**: Create actionable briefs ready for implementation or further development

Key behaviors:
- Automatic codebase awareness for code-related topics via smart detection and Auggie MCP
- Multi-persona orchestration across architecture, analysis, frontend, backend, security domains
- Advanced MCP coordination with intelligent routing for specialized analysis
- Systematic execution with progressive dialogue enhancement and parallel exploration
- Cross-session persistence with comprehensive requirements discovery documentation

## MCP Integration
- **Auggie MCP**: Semantic codebase retrieval for code-related topic awareness and project structure understanding
- **Sequential MCP**: Complex multi-step reasoning for systematic exploration and validation
- **Context7 MCP**: Framework-specific feasibility assessment and pattern analysis
- **Magic MCP**: UI/UX feasibility and design system integration analysis
- **Playwright MCP**: User experience validation and interaction pattern testing
- **Morphllm MCP**: Large-scale content analysis and pattern-based transformation
- **Serena MCP**: Cross-session persistence, memory management, and project context enhancement

## Tool Coordination
- **codebase-retrieval**: Semantic codebase search for relevant code, architecture, and integration points
- **Read/Write/Edit**: Requirements documentation and specification generation
- **TodoWrite**: Progress tracking for complex multi-phase exploration
- **Task**: Advanced delegation for parallel exploration paths and multi-agent coordination
- **WebSearch**: Market research, competitive analysis, and technology validation
- **sequentialthinking**: Structured reasoning for complex requirements analysis

## Key Patterns
- **Codebase-Aware Discovery**: Smart detection → Auggie retrieval → context-informed Socratic dialogue
- **Socratic Dialogue**: Question-driven exploration → systematic requirements discovery
- **Multi-Domain Analysis**: Cross-functional expertise → comprehensive feasibility assessment
- **Progressive Coordination**: Systematic exploration → iterative refinement and validation
- **Specification Generation**: Concrete requirements → actionable implementation briefs

## Codebase Awareness (Phase 0)

When a brainstorm topic is code-related, automatically load relevant codebase context before beginning Socratic dialogue. This grounds the requirements discovery in what actually exists in the project.

### Code-Relevance Detection

Evaluate the brainstorm topic against three signal categories. If **any one** matches, trigger codebase context loading.

**Signal A — Code Entity References**: Topic mentions file paths, extensions (`.py`, `.ts`), or programming constructs (function, class, method, module, component, endpoint, API, route, handler, model, schema, interface, service, controller, middleware, hook, plugin, database, cache, queue, server, pipeline).

**Signal B — Development Action Verbs**: Topic contains code-work verbs: implement, build, create, add, generate, refactor, optimize, improve, update, migrate, upgrade, extend, modify, fix, debug, resolve, patch.

**Signal C — Project-Specific Terms**: Topic references the project name, known package names (from `package.json`, `pyproject.toml`), languages/frameworks matching the project stack, or known module/directory names.

**Decision**: `IF signal_A OR signal_B OR signal_C → Trigger Phase 0 | ELSE → Skip to Phase 1`

**Override Flags**:
- `--codebase`: Force codebase context loading regardless of detection
- `--no-codebase`: Skip codebase context loading regardless of detection

**Edge case**: If uncertain whether topic is code-related, do NOT trigger. False negatives are preferred over wasting tokens on business/strategy brainstorms.

### Context Loading (Two Parallel Queries)

**Primary tool**: `mcp__auggie-mcp__codebase-retrieval`

**Query 1 — Topic-Specific** (parallel):
```
information_request: "{brainstorm_topic} - find relevant code, existing implementations,
                      related components, and integration points"
directory_path: "{current_working_directory}"
```

**Query 2 — Architecture Scan** (parallel):
```
information_request: "Project architecture, structure, patterns, and conventions
                      related to {topic_domain_area}"
directory_path: "{current_working_directory}"
```

### Context Briefing Output

Present findings as a structured block before beginning Socratic dialogue:

```
## Codebase Context

**Relevant Existing Code:**
- [file:line] — brief description of what exists

**Architecture & Patterns:**
- Pattern/convention observed in the project

**Integration Points:**
- Where new work would connect to existing code

**Constraints Identified:**
- Technical constraints from existing implementation
```

Token budget for briefing: ~500-800 tokens max.

### Fallback (Auggie Unavailable)

If `codebase-retrieval` is unavailable, fall back to:
1. **Serena**: `get_symbols_overview` on relevant directories (depth: 1)
2. **Native tools**: Glob for file matching + Grep for keyword search

Prefix the briefing with:
> Note: Limited codebase awareness (Auggie MCP unavailable, using Serena + native tools)

## Examples

### Codebase-Aware Feature Discovery
```
/sc:brainstorm "add caching to the API layer" --depth deep
# Auggie MCP detects code-related topic → loads relevant API code and architecture
# Socratic dialogue informed by existing implementation patterns and constraints
# Example: "I see you have a CacheService in src/services/. Are you extending this or building new?"
```

### Systematic Product Discovery
```
/sc:brainstorm "AI-powered project management tool" --strategy systematic --depth deep
# Multi-persona analysis: architect (system design), analyzer (feasibility), project-manager (requirements)
# Sequential MCP provides structured exploration framework
```

### Agile Feature Exploration
```
/sc:brainstorm "real-time collaboration features" --strategy agile --parallel
# Parallel exploration paths with frontend, backend, and security personas
# Context7 and Magic MCP for framework and UI pattern analysis
```

### Enterprise Solution Validation
```
/sc:brainstorm "enterprise data analytics platform" --strategy enterprise --validate
# Comprehensive validation with security, devops, and architect personas
# Serena MCP for cross-session persistence and enterprise requirements tracking
```

### Cross-Session Refinement
```
/sc:brainstorm "mobile app monetization strategy" --depth normal
# Serena MCP manages cross-session context and iterative refinement
# Progressive dialogue enhancement with memory-driven insights
```

## Boundaries

**Will:**
- Transform ambiguous ideas into concrete specifications through systematic exploration
- Coordinate multiple personas and MCP servers for comprehensive analysis
- Provide cross-session persistence and progressive dialogue enhancement

**Will Not:**
- Make implementation decisions without proper requirements discovery
- Override user vision with prescriptive solutions during exploration phase
- Bypass systematic exploration for complex multi-domain projects

## CRITICAL BOUNDARIES

**STOP AFTER REQUIREMENTS DISCOVERY**

This command produces a REQUIREMENTS SPECIFICATION ONLY.

**Explicitly Will NOT**:
- Create architecture diagrams or system designs (use `/sc:design`)
- Generate implementation code (use `/sc:implement`)
- Make architectural decisions
- Design database schemas or API contracts
- Create technical specifications beyond requirements

**Output**: Requirements document with:
- Clarified user goals
- Functional requirements
- Non-functional requirements
- User stories / acceptance criteria
- Open questions for user

**Next Step**: After brainstorm completes, use `/sc:design` for architecture or `/sc:workflow` for implementation planning.