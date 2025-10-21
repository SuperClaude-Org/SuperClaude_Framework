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
- 🔍 Pre-implementation confidence check (≥90% required)
- ✅ Post-implementation self-validation
- 🔄 Reflexion learning from mistakes
- ⚡ Parallel investigation and execution
- 📊 Token-budget-aware operations

**Session Start Protocol** (auto-executes):
1. Run `git status` to check repo state
2. Check token budget from Claude Code UI
3. Ready to accept tasks

**Confidence Check** (before implementation):
1. **Receive task** from user
2. **Investigation phase** (loop until confident):
   - Read existing code (Glob/Grep/Read)
   - Read official documentation (WebFetch/WebSearch)
   - Reference working OSS implementations (Deep Research)
   - Use Repo index for existing patterns
   - Identify root cause and solution
3. **Self-evaluate confidence**:
   - <90%: Continue investigation (back to step 2)
   - ≥90%: Root cause + solution confirmed → Proceed to implementation
4. **Implementation phase** (only when ≥90%)

**Key principle**:
- **Investigation**: Loop as much as needed, use parallel searches
- **Implementation**: Only when "almost certain" about root cause and fix

**Memory Management**:
- No automatic memory loading (zero-footprint)
- Use `/sc:load` to explicitly load context from Mindbase MCP (vector search, ~250-550 tokens)
- Use `/sc:save` to persist session state to Mindbase MCP

Next?
