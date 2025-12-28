# PM Agent Mode Integration Guide

**Last Updated**: 2025-10-14
**Target Version**: 4.2.0
**Status**: Implementation Guide

---

## 📋 Overview

This guide provides step-by-step procedures for integrating PM Agent mode as SuperClaude's always-active meta-layer with session lifecycle management, PDCA self-evaluation, and systematic knowledge management.

---

## 🎯 Integration Goals

1. **Session Lifecycle**: Auto-activation at session start with context restoration
2. **PDCA Engine**: Automated Plan-Do-Check-Act cycle execution
3. **Memory Operations**: Serena MCP integration for session persistence
4. **Documentation Strategy**: Systematic knowledge evolution

---

## 📐 Architecture Integration

### PM Agent Position

```
┌──────────────────────────────────────────┐
│    PM Agent Mode (Meta-Layer)            │
│    • Always Active                        │
│    • Session Management                   │
│    • PDCA Self-Evaluation                 │
└──────────────┬───────────────────────────┘
               ↓
    [Specialist Agents Layer]
               ↓
    [Commands & Modes Layer]
               ↓
    [MCP Tool Layer]
```

See: [ARCHITECTURE.md](./ARCHITECTURE.md) for full system architecture

---

## 🔧 Phase 2: Core Implementation

### File Structure

```
superclaude/
├── Commands/
│   └── pm.md                           # ✅ Already updated
├── Agents/
│   └── pm-agent.md                     # ✅ Already updated
└── Core/
    ├── __init__.py                     # Module initialization
    ├── session_lifecycle.py            # 🆕 Session management
    ├── pdca_engine.py                  # 🆕 PDCA automation
    └── memory_ops.py                   # 🆕 Memory operations
```

### Implementation Order

1. `memory_ops.py` - Serena MCP wrapper (foundation)
2. `session_lifecycle.py` - Session management (depends on memory_ops)
3. `pdca_engine.py` - PDCA automation (depends on memory_ops)

---

## 1️⃣ memory_ops.py Implementation

### Purpose
Wrapper for Serena MCP memory operations with error handling and fallback.

### Key Functions

```python
# superclaude/Core/memory_ops.py

class MemoryOperations:
    """Serena MCP memory operations wrapper"""

    def list_memories() -> List[str]:
        """List all available memories"""

    def read_memory(key: str) -> Optional[Dict]:
        """Read memory by key"""

    def write_memory(key: str, value: Dict) -> bool:
        """Write memory with key"""

    def delete_memory(key: str) -> bool:
        """Delete memory by key"""
```

### Integration Points
- Connect to Serena MCP server
- Handle connection errors gracefully
- Provide fallback for offline mode
- Validate memory structure

### Testing
```bash
pytest tests/test_memory_ops.py -v
```

---

## 2️⃣ session_lifecycle.py Implementation

### Purpose
Auto-activation at session start, context restoration, user report generation.

### Key Functions

```python
# superclaude/Core/session_lifecycle.py

class SessionLifecycle:
    """Session lifecycle management"""

    def on_session_start():
        """Hook for session start (auto-activation)"""
        # 1. list_memories()
        # 2. read_memory("pm_context")
        # 3. read_memory("last_session")
        # 4. read_memory("next_actions")
        # 5. generate_user_report()

    def generate_user_report() -> str:
        """Generate user report (前回/進捗/今回/課題)"""

    def on_session_end():
        """Hook for session end (checkpoint save)"""
        # 1. write_memory("last_session", summary)
        # 2. write_memory("next_actions", todos)
        # 3. write_memory("pm_context", complete_state)
```

### User Report Format
```
前回: [last session summary]
進捗: [current progress status]
今回: [planned next actions]
課題: [blockers or issues]
```

### Integration Points
- Hook into Claude Code session start
- Read memories using memory_ops
- Generate human-readable report
- Handle missing or corrupted memory

### Testing
```bash
pytest tests/test_session_lifecycle.py -v
```

---

## 3️⃣ pdca_engine.py Implementation

### Purpose
Automate PDCA cycle execution with documentation generation.

### Key Functions

```python
# superclaude/Core/pdca_engine.py

class PDCAEngine:
    """PDCA cycle automation"""

    def plan_phase(goal: str):
        """Generate hypothesis (仮説)"""
        # 1. write_memory("plan", goal)
        # 2. Create docs/temp/hypothesis-YYYY-MM-DD.md

    def do_phase():
        """Track experimentation (実験)"""
        # 1. TodoWrite tracking
        # 2. write_memory("checkpoint", progress) every 30min
        # 3. Update docs/temp/experiment-YYYY-MM-DD.md

    def check_phase():
        """Self-evaluation (評価)"""
        # 1. think_about_task_adherence()
        # 2. think_about_whether_you_are_done()
        # 3. Create docs/temp/lessons-YYYY-MM-DD.md

    def act_phase():
        """Knowledge extraction (改善)"""
        # 1. Success → docs/patterns/[pattern-name].md
        # 2. Failure → docs/mistakes/mistake-YYYY-MM-DD.md
        # 3. Update CLAUDE.md if global pattern
```

### Documentation Templates

**hypothesis-template.md**:
```markdown
# Hypothesis: [Goal Description]

Date: YYYY-MM-DD
Status: Planning

## Goal
What are we trying to accomplish?

## Approach
How will we implement this?

## Success Criteria
How do we know when we're done?

## Potential Risks
What could go wrong?
```

**experiment-template.md**:
```markdown
# Experiment Log: [Implementation Name]

Date: YYYY-MM-DD
Status: In Progress

## Implementation Steps
- [ ] Step 1
- [ ] Step 2

## Errors Encountered
- Error 1: Description, solution

## Solutions Applied
- Solution 1: Description, result

## Checkpoint Saves
- 10:00: [progress snapshot]
- 10:30: [progress snapshot]
```

### Integration Points
- Create docs/ directory templates
- Integrate with TodoWrite
- Call Serena MCP think operations
- Generate documentation files

### Testing
```bash
pytest tests/test_pdca_engine.py -v
```

---

## 🔌 Phase 3: Serena MCP Integration

### Prerequisites
```bash
# Install Serena MCP server
# See: docs/troubleshooting/serena-installation.md
```

### Configuration
```json
// ~/.claude/.claude.json
{
  "mcpServers": {
    "serena": {
      "command": "uv",
      "args": ["run", "serena-mcp"]
    }
  }
}
```

### Memory Structure
```json
{
  "pm_context": {
    "project": "SuperClaude_Framework",
    "current_phase": "Phase 2",
    "architecture": "Context-Oriented Configuration",
    "patterns": ["PDCA Cycle", "Session Lifecycle"]
  },
  "last_session": {
    "date": "2025-10-14",
    "accomplished": ["Phase 1 complete"],
    "issues": ["Serena MCP not configured"],
    "learned": ["Session Lifecycle pattern"]
  },
  "next_actions": [
    "Implement session_lifecycle.py",
    "Configure Serena MCP",
    "Test memory operations"
  ]
}
```

### Testing Serena Connection
```bash
# Test memory operations
python -m SuperClaude.Core.memory_ops --test
```

---

## 📁 Phase 4: Documentation Strategy

### Directory Structure
```
docs/
├── temp/                # Temporary (7-day lifecycle)
│   ├── hypothesis-YYYY-MM-DD.md
│   ├── experiment-YYYY-MM-DD.md
│   └── lessons-YYYY-MM-DD.md
├── patterns/           # Formal patterns (永久保存)
│   └── [pattern-name].md
└── mistakes/          # Mistake records (永久保存)
    └── mistake-YYYY-MM-DD.md
```

### Lifecycle Automation
```bash
# Create cleanup script
scripts/cleanup_temp_docs.sh

# Run daily via cron
0 0 * * * /path/to/scripts/cleanup_temp_docs.sh
```

### Migration Scripts
```bash
# Migrate successful experiments to patterns
python scripts/migrate_to_patterns.py

# Migrate failures to mistakes
python scripts/migrate_to_mistakes.py
```

---

## 🚀 Phase 5: Auto-Activation (Research Needed)

### Research Questions
1. How does Claude Code handle initialization?
2. Are there plugin hooks available?
3. Can we intercept session start events?

### Implementation Plan (TBD)
Once research complete, implement auto-activation hooks:

```python
# superclaude/Core/auto_activation.py (future)

def on_claude_code_start():
    """Auto-activate PM Agent at session start"""
    session_lifecycle.on_session_start()
```

---

## ✅ Implementation Checklist

### Phase 2: Core Implementation
- [ ] Implement `memory_ops.py`
- [ ] Write unit tests for memory_ops
- [ ] Implement `session_lifecycle.py`
- [ ] Write unit tests for session_lifecycle
- [ ] Implement `pdca_engine.py`
- [ ] Write unit tests for pdca_engine
- [ ] Integration testing

### Phase 3: Serena MCP
- [ ] Install Serena MCP server
- [ ] Configure `.claude.json`
- [ ] Test memory operations
- [ ] Test think operations
- [ ] Test cross-session persistence

### Phase 4: Documentation Strategy
- [ ] Create `docs/temp/` template
- [ ] Create `docs/patterns/` template
- [ ] Create `docs/mistakes/` template
- [ ] Implement lifecycle automation
- [ ] Create migration scripts

### Phase 5: Auto-Activation
- [ ] Research Claude Code hooks
- [ ] Design auto-activation system
- [ ] Implement auto-activation
- [ ] Test session start behavior

---

## 🧪 Testing Strategy

### Unit Tests
```bash
tests/
├── test_memory_ops.py       # Memory operations
├── test_session_lifecycle.py # Session management
└── test_pdca_engine.py       # PDCA automation
```

### Integration Tests
```bash
tests/integration/
├── test_pm_agent_flow.py     # End-to-end PM Agent
├── test_serena_integration.py # Serena MCP integration
└── test_cross_session.py     # Session persistence
```

### Manual Testing
1. Start new session → Verify context restoration
2. Work on task → Verify checkpoint saves
3. End session → Verify state preservation
4. Restart → Verify seamless resumption

---

## 📊 Success Criteria

### Functional
- [ ] PM Agent activates at session start
- [ ] Context restores from memory
- [ ] User report generates correctly
- [ ] PDCA cycle executes automatically
- [ ] Documentation strategy works

### Performance
- [ ] Session start delay <500ms
- [ ] Memory operations <100ms
- [ ] Context restoration reliable (>99%)

### Quality
- [ ] Test coverage >90%
- [ ] No regression in existing features
- [ ] Documentation complete

---

## 🔧 Troubleshooting

### Common Issues

**"Serena MCP not connecting"**
- Check server installation
- Verify `.claude.json` configuration
- Test connection: `claude mcp list`

**"Memory operations failing"**
- Check network connection
- Verify Serena server running
- Check error logs

**"Context not restoring"**
- Verify memory structure
- Check `pm_context` exists
- Test with fresh memory

---

## 📚 References

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [ROADMAP.md](./ROADMAP.md) - Development roadmap
- [pm-agent-implementation-status.md](../pm-agent-implementation-status.md) - Status tracking
- [Commands/pm.md](../../superclaude/Commands/pm.md) - PM Agent command
- [Agents/pm-agent.md](../../superclaude/Agents/pm-agent.md) - PM Agent persona

---

**Last Verified**: 2025-10-14
**Next Review**: 2025-10-21 (1 week)
**Version**: 4.1.5
