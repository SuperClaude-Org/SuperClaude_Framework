# SuperClaude Framework Flags

Behavioral flags for Claude Code to enable specific execution modes and tool selection patterns.

## Mode Activation Flags

**--brainstorm**
- Trigger: Vague project requests, exploration keywords ("maybe", "thinking about", "not sure")
- Behavior: Activate collaborative discovery mindset, ask probing questions, guide requirement elicitation

**--introspect**
- Trigger: Self-analysis requests, error recovery, complex problem solving requiring meta-cognition
- Behavior: Expose thinking process with transparency markers (🤔, 🎯, ⚡, 📊, 💡)

**--task-manage**
- Trigger: Multi-step operations (>3 steps), complex scope (>2 directories OR >3 files)
- Behavior: Orchestrate through delegation, progressive enhancement, systematic organization

**--orchestrate**
- Trigger: Multi-tool operations, performance constraints, parallel execution opportunities
- Behavior: Optimize tool selection matrix, enable parallel thinking, adapt to resource constraints

**--token-efficient**
- Trigger: Context usage >75%, large-scale operations, --uc flag
- Behavior: Symbol-enhanced communication, 30-50% token reduction while preserving clarity

## MCP Server Flags

**--c7 / --context7**
- Trigger: Library imports, framework questions, official documentation needs
- Behavior: Enable Context7 for curated documentation lookup and pattern guidance

**--seq / --sequential**
- Trigger: Complex debugging, system design, multi-component analysis
- Behavior: Enable Sequential for structured multi-step reasoning and hypothesis testing

**--magic**
- Trigger: UI component requests (/ui, /21), design system queries, frontend development
- Behavior: Enable Magic for modern UI generation from 21st.dev patterns

**--morph / --morphllm**
- Trigger: Bulk code transformations, pattern-based edits, style enforcement
- Behavior: Enable Morphllm for efficient multi-file pattern application

**--serena**
- Trigger: Symbol operations, project memory needs, large codebase navigation
- Behavior: Enable Serena for semantic understanding and session persistence

**--play / --playwright**
- Trigger: Browser testing, E2E scenarios, visual validation, accessibility testing
- Behavior: Enable Playwright for real browser automation and testing

**--chrome / --devtools**
- Trigger: Performance auditing, debugging, layout issues, network analysis, console errors
- Behavior: Enable Chrome DevTools for real-time browser inspection and performance analysis

**--tavily**
- Trigger: Web search requests, real-time information needs, research queries, current events
- Behavior: Enable Tavily for web search and real-time information gathering

**--frontend-verify**
- Trigger: UI testing requests, frontend debugging, layout validation, component verification
- Behavior: Enable Playwright + Chrome DevTools + Serena for comprehensive frontend verification and debugging

**--all-mcp**
- Trigger: Maximum complexity scenarios, multi-domain problems
- Behavior: Enable all MCP servers for comprehensive capability

**--no-mcp**
- Trigger: Native-only execution needs, performance priority
- Behavior: Disable all MCP servers, use native tools with WebSearch fallback

## Analysis Depth Flags

**--think**
- Trigger: Multi-component analysis needs, moderate complexity
- Behavior: Standard structured analysis (~4K tokens), enables Sequential

**--think-hard**
- Trigger: Architectural analysis, system-wide dependencies
- Behavior: Deep analysis (~10K tokens), enables Sequential + Context7

**--ultrathink**
- Trigger: Critical system redesign, legacy modernization, complex debugging
- Behavior: Maximum depth analysis (~32K tokens), enables all MCP servers

## Execution Control Flags

**--delegate [auto|files|folders]**
- Trigger: >7 directories OR >50 files OR complexity >0.8
- Behavior: Enable sub-agent parallel processing with intelligent routing

**--concurrency [n]**
- Trigger: Resource optimization needs, parallel operation control
- Behavior: Control max concurrent operations (range: 1-15)

**--loop**
- Trigger: Improvement keywords (polish, refine, enhance, improve)
- Behavior: Enable iterative improvement cycles with validation gates

**--iterations [n]**
- Trigger: Specific improvement cycle requirements
- Behavior: Set improvement cycle count (range: 1-10)

**--validate**
- Trigger: Risk score >0.7, resource usage >75%, production environment
- Behavior: Pre-execution risk assessment and validation gates

**--safe-mode**
- Trigger: Resource usage >85%, production environment, critical operations
- Behavior: Maximum validation, conservative execution, auto-enable --uc

## Output Optimization Flags

**--uc / --ultracompressed**
- Trigger: Context pressure, efficiency requirements, large operations
- Behavior: Symbol communication system, 30-50% token reduction

**--scope [file|module|project|system]**
- Trigger: Analysis boundary needs
- Behavior: Define operational scope and analysis depth

**--focus [performance|security|quality|architecture|accessibility|testing]**
- Trigger: Domain-specific optimization needs
- Behavior: Target specific analysis domain and expertise application

## Flag Priority Rules

**Safety First**: --safe-mode > --validate > optimization flags
**Explicit Override**: User flags > auto-detection
**Depth Hierarchy**: --ultrathink > --think-hard > --think  
**MCP Control**: --no-mcp overrides all individual MCP flags
**Scope Precedence**: system > project > module > file