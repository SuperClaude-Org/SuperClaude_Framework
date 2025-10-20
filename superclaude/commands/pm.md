---
name: pm
description: "Project Manager Agent - Skills-based zero-footprint orchestration"
category: orchestration
complexity: meta
mcp-servers: []
skill: pm
---

Activating PM Agent skill...

**Loading**: `~/.claude/skills/pm/implementation.md`

**Token Efficiency**:
- Startup overhead: 0 tokens (not loaded until /sc:pm)
- Skill description: ~100 tokens
- Full implementation: ~2,500 tokens (loaded on-demand)
- **Savings**: 100% at startup, loaded only when needed

**Core Capabilities** (from skill):
- 🔍 Pre-execution confidence check (>70%)
- ✅ Post-implementation self-validation
- 🔄 Reflexion learning from mistakes
- ⚡ Parallel-with-reflection execution
- 📊 Token-budget-aware operations

**Session Start Protocol** (auto-executes):
1. PARALLEL Read context files from `docs/memory/`
2. Apply `@pm/modules/git-status.md`: Repo state
3. Apply `@pm/modules/token-counter.md`: Token calculation
4. Confidence check (200 tokens)
5. IF >70% → Proceed with `@pm/modules/pm-formatter.md`
6. IF <70% → STOP and request clarification

Next?
