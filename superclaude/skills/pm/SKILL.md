---
name: pm
description: Project Manager Agent - Self-improvement workflow executor that documents implementations, analyzes mistakes, and maintains knowledge base continuously
version: 1.0.0
author: SuperClaude
category: meta
migrated: true
---

# PM Agent (Project Manager Agent)

Skills-based on-demand loading implementation.

**Token Efficiency**:
- Startup: 0 tokens (not loaded)
- Description: ~100 tokens (this file)
- Full load: ~2,500 tokens (loaded when /sc:pm is invoked)

**Activation**:
- `/sc:pm` command
- Session start (auto-activation)
- Post-implementation documentation needs
- Mistake detection and analysis

**Implementation**: See `implementation.md` for full protocol

**Modules**: Support files in `modules/` directory
- `token-counter.md` - Dynamic token calculation
- `git-status.md` - Git repository state detection
- `pm-formatter.md` - Output structure and formatting
