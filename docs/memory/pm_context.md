# PM Agent Context

**Project**: SuperClaude_Framework
**Type**: AI Agent Framework
**Tech Stack**: Claude Code, MCP Servers, Markdown-based configuration
**Current Focus**: Removing Serena MCP dependency from PM Agent

## Project Overview

SuperClaude is a comprehensive framework for Claude Code that provides:
- Persona-based specialized agents (frontend, backend, security, etc.)
- MCP server integrations (Context7, Magic, Morphllm, Sequential, etc.)
- Slash command system for workflow automation
- Self-improvement workflow with PDCA cycle

## Architecture

- `superclaude/agents/` - Agent persona definitions
- `superclaude/commands/` - Slash command definitions
- `docs/` - Documentation and patterns
- `docs/memory/` - PM Agent session state (local files)
- `docs/pdca/` - PDCA cycle documentation per feature

## Active Patterns

- **Repository-Scoped Memory**: Local file-based memory in `docs/memory/`
- **PDCA Cycle**: Plan → Do → Check → Act documentation workflow
- **Self-Evaluation Checklists**: Replace Serena MCP `think_about_*` functions

## Known Issues

None currently.

## Last Updated

2025-10-16
