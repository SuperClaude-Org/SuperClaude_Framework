# PM Agent Context

**Project**: SuperClaude_Framework
**Type**: AI Agent Framework
**Tech Stack**: Claude Code, MCP Servers, Markdown-based configuration
**Current Focus**: Token-efficient architecture with progressive context loading

## Project Overview

SuperClaude is a comprehensive framework for Claude Code that provides:
- Persona-based specialized agents (frontend, backend, security, etc.)
- MCP server integrations (Context7, Magic, Morphllm, Sequential, etc.)
- Slash command system for workflow automation
- Self-improvement workflow with PDCA cycle
- **NEW**: Token-optimized PM Agent with progressive loading

## Architecture

- `plugins/superclaude/agents/` - Agent persona definitions
- `plugins/superclaude/commands/` - Slash command definitions (pm.md: token-efficient redesign)
- `docs/` - Documentation and patterns
- `docs/memory/` - PM Agent session state (local files)
- `docs/pdca/` - PDCA cycle documentation per feature
- `docs/research/` - Research reports (llm-agent-token-efficiency-2025.md)

## Token Efficiency Architecture (2025-10-17 Redesign)

### Layer 0: Bootstrap (Always Active)
- **Token Cost**: 150 tokens (95% reduction from old 2,300 tokens)
- **Operations**: Time awareness + repo detection + session initialization
- **Philosophy**: User Request First - NO auto-loading before understanding intent

### Intent Classification System
```yaml
Ultra-Light (100-500 tokens):   "進捗", "progress", "status" → Layer 1 only
Light (500-2K tokens):          "typo", "rename", "comment" → Layer 2 (target file)
Medium (2-5K tokens):           "bug", "fix", "refactor" → Layer 3 (related files)
Heavy (5-20K tokens):           "feature", "architecture" → Layer 4 (subsystem)
Ultra-Heavy (20K+ tokens):      "redesign", "migration" → Layer 5 (full + research)
```

### Progressive Loading (5-Layer Strategy)
- **Layer 1**: Minimal context (mindbase: 500 tokens | fallback: 800 tokens)
- **Layer 2**: Target context (500-1K tokens)
- **Layer 3**: Related context (mindbase: 3-4K | fallback: 4.5K)
- **Layer 4**: System context (8-12K tokens, user confirmation)
- **Layer 5**: External research (20-50K tokens, WARNING required)

### Workflow Metrics Collection
- **File**: `docs/memory/workflow_metrics.jsonl`
- **Purpose**: Continuous A/B testing for workflow optimization
- **Data**: task_type, complexity, workflow_id, tokens_used, time_ms, success
- **Strategy**: ε-greedy (80% best workflow, 20% experimental)

### mindbase Integration Incentive
- **Layer 1**: 500 tokens (mindbase) vs 800 tokens (fallback) = **38% savings**
- **Layer 3**: 3-4K tokens (mindbase) vs 4.5K tokens (fallback) = **20% savings**
- **Total Potential**: Up to **90% token reduction** with semantic search (industry benchmark)

## Active Patterns

- **Repository-Scoped Memory**: Local file-based memory in `docs/memory/`
- **PDCA Cycle**: Plan → Do → Check → Act documentation workflow
- **Self-Evaluation Checklists**: Replace Serena MCP `think_about_*` functions
- **User Request First**: Bootstrap → Wait → Intent → Progressive Load → Execute
- **Continuous Optimization**: A/B testing via workflow_metrics.jsonl

## Recent Changes (2025-10-17)

### PM Agent Token Efficiency Redesign
- **Removed**: Auto-loading 7 files on startup (2,300 tokens wasted)
- **Added**: Layer 0 Bootstrap (150 tokens) + Intent Classification
- **Added**: Progressive Loading (5-layer) + Workflow Metrics
- **Result**:
  - Ultra-Light tasks: 2,300 → 650 tokens (72% reduction)
  - Light tasks: 3,500 → 1,200 tokens (66% reduction)
  - Medium tasks: 7,000 → 4,500 tokens (36% reduction)

### Research Integration
- **Report**: `docs/research/llm-agent-token-efficiency-2025.md`
- **Benchmarks**: Trajectory Reduction (99%), AgentDropout (21.6%), Vector DB (90%)
- **Source**: Anthropic, Microsoft AutoGen v0.4, CrewAI + Mem0, LangChain

## Known Issues

None currently.

## Last Updated

2025-10-17
