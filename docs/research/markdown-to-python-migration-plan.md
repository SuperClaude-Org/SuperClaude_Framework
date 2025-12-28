# Markdown → Python Migration Plan

**Date**: 2025-10-20
**Problem**: Markdown modes consume 41,000 tokens every session with no enforcement
**Solution**: Python-first implementation with Skills API migration path

## Current Token Waste

### Markdown Files Loaded Every Session

**Top Token Consumers**:
```
pm-agent.md                    16,201 bytes  (4,050 tokens)
rules.md (framework)           16,138 bytes  (4,034 tokens)
socratic-mentor.md             12,061 bytes  (3,015 tokens)
MODE_Business_Panel.md         11,761 bytes  (2,940 tokens)
business-panel-experts.md       9,822 bytes  (2,455 tokens)
config.md (research)            9,607 bytes  (2,401 tokens)
examples.md (business)          8,253 bytes  (2,063 tokens)
symbols.md (business)           7,653 bytes  (1,913 tokens)
flags.md (framework)            5,457 bytes  (1,364 tokens)
MODE_Task_Management.md         3,574 bytes    (893 tokens)

Total: ~164KB = ~41,000 tokens PER SESSION
```

**Annual Cost** (200 sessions/year):
- Tokens: 8,200,000 tokens/year
- Cost: ~$20-40/year just reading docs

## Migration Strategy

### Phase 1: Validators (Already Done ✅)

**Implemented**:
```python
superclaude/validators/
├── security_roughcheck.py  # Hardcoded secret detection
├── context_contract.py     # Project rule enforcement
├── dep_sanity.py           # Dependency validation
├── runtime_policy.py       # Runtime version checks
└── test_runner.py          # Test execution
```

**Benefits**:
- ✅ Python enforcement (not just docs)
- ✅ 26 tests prove correctness
- ✅ Pre-execution validation gates

### Phase 2: Mode Enforcement (Next)

**Current Problem**:
```markdown
# MODE_Orchestration.md (2,759 bytes)
- Tool selection matrix
- Resource management
- Parallel execution triggers
= 毎回読む、強制力なし
```

**Python Solution**:
```python
# superclaude/modes/orchestration.py

from enum import Enum
from typing import Literal, Optional
from functools import wraps

class ResourceZone(Enum):
    GREEN = "0-75%"   # Full capabilities
    YELLOW = "75-85%" # Efficiency mode
    RED = "85%+"      # Essential only

class OrchestrationMode:
    """Intelligent tool selection and resource management"""

    @staticmethod
    def select_tool(task_type: str, context_usage: float) -> str:
        """
        Tool Selection Matrix (enforced at runtime)

        BEFORE (Markdown): "Use Magic MCP for UI components" (no enforcement)
        AFTER (Python): Automatically routes to Magic MCP when task_type="ui"
        """
        if context_usage > 0.85:
            # RED ZONE: Essential only
            return "native"

        tool_matrix = {
            "ui_components": "magic_mcp",
            "deep_analysis": "sequential_mcp",
            "pattern_edits": "morphllm_mcp",
            "documentation": "context7_mcp",
            "multi_file_edits": "multiedit",
        }

        return tool_matrix.get(task_type, "native")

    @staticmethod
    def enforce_parallel(files: list) -> bool:
        """
        Auto-trigger parallel execution

        BEFORE (Markdown): "3+ files should use parallel"
        AFTER (Python): Automatically enforces parallel for 3+ files
        """
        return len(files) >= 3

# Decorator for mode activation
def with_orchestration(func):
    """Apply orchestration mode to function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Enforce orchestration rules
        mode = OrchestrationMode()
        # ... enforcement logic ...
        return func(*args, **kwargs)
    return wrapper
```

**Token Savings**:
- Before: 2,759 bytes (689 tokens) every session
- After: Import only when used (~50 tokens)
- Savings: 93%

### Phase 3: PM Agent Python Implementation

**Current**:
```markdown
# pm-agent.md (16,201 bytes = 4,050 tokens)

Pre-Implementation Confidence Check
Post-Implementation Self-Check
Reflexion Pattern
Parallel-with-Reflection
```

**Python**:
```python
# superclaude/agents/pm.py

from dataclasses import dataclass
from typing import Optional
from superclaude.memory import ReflexionMemory
from superclaude.validators import ValidationGate

@dataclass
class ConfidenceCheck:
    """Pre-implementation confidence verification"""
    requirement_clarity: float  # 0-1
    context_loaded: bool
    similar_mistakes: list

    def should_proceed(self) -> bool:
        """ENFORCED: Only proceed if confidence >70%"""
        return self.requirement_clarity > 0.7 and self.context_loaded

class PMAgent:
    """Project Manager Agent with enforced workflow"""

    def __init__(self, repo_path: Path):
        self.memory = ReflexionMemory(repo_path)
        self.validators = ValidationGate()

    def execute_task(self, task: str) -> Result:
        """
        4-Phase workflow (ENFORCED, not documented)
        """
        # PHASE 1: PLANNING (with confidence check)
        confidence = self.check_confidence(task)
        if not confidence.should_proceed():
            return Result.error("Low confidence - need clarification")

        # PHASE 2: TASKLIST
        tasks = self.decompose(task)

        # PHASE 3: DO (with validation gates)
        for subtask in tasks:
            if not self.validators.validate(subtask):
                return Result.error(f"Validation failed: {subtask}")
            self.execute(subtask)

        # PHASE 4: REFLECT
        self.memory.learn_from_execution(task, tasks)

        return Result.success()
```

**Token Savings**:
- Before: 16,201 bytes (4,050 tokens) every session
- After: Import only when `/sc:pm` used (~100 tokens)
- Savings: 97%

### Phase 4: Skills API Migration (Future)

**Lazy-Loaded Skills**:
```
skills/pm-mode/
  SKILL.md (200 bytes)     # Title + description only
  agent.py (16KB)          # Full implementation
  memory.py (5KB)          # Reflexion memory
  validators.py (8KB)      # Validation gates

Session start: 200 bytes loaded
/sc:pm used: Full 29KB loaded on-demand
Never used: Forever 200 bytes
```

**Token Comparison**:
```
Current Markdown: 16,201 bytes every session = 4,050 tokens
Python Import:    Import header only = 100 tokens
Skills API:       Lazy-load on use = 50 tokens (description only)

Savings: 98.8% with Skills API
```

## Implementation Priority

### Immediate (This Week)

1. ✅ **Index Command** (`/sc:index-repo`)
   - Already created
   - Auto-runs on setup
   - 94% token savings

2. ✅ **Setup Auto-Indexing**
   - Integrated into `knowledge_base.py`
   - Runs during installation
   - Creates PROJECT_INDEX.md

### Short-Term (2-4 Weeks)

3. **Orchestration Mode Python**
   - `superclaude/modes/orchestration.py`
   - Tool selection matrix (enforced)
   - Resource management (automated)
   - **Savings**: 689 tokens → 50 tokens (93%)

4. **PM Agent Python Core**
   - `superclaude/agents/pm.py`
   - Confidence check (enforced)
   - 4-phase workflow (automated)
   - **Savings**: 4,050 tokens → 100 tokens (97%)

### Medium-Term (1-2 Months)

5. **All Modes → Python**
   - Brainstorming, Introspection, Task Management
   - **Total Savings**: ~10,000 tokens → ~500 tokens (95%)

6. **Skills Prototype** (Issue #441)
   - 1-2 modes as Skills
   - Measure lazy-load efficiency
   - Report to upstream

### Long-Term (3+ Months)

7. **Full Skills Migration**
   - All modes → Skills
   - All agents → Skills
   - **Target**: 98% token reduction

## Code Examples

### Before (Markdown Mode)

```markdown
# MODE_Orchestration.md

## Tool Selection Matrix
| Task Type | Best Tool |
|-----------|-----------|
| UI | Magic MCP |
| Analysis | Sequential MCP |

## Resource Management
Green Zone (0-75%): Full capabilities
Yellow Zone (75-85%): Efficiency mode
Red Zone (85%+): Essential only
```

**Problems**:
- ❌ 689 tokens every session
- ❌ No enforcement
- ❌ Can't test if rules followed
- ❌ Heavy重複 across modes

### After (Python Enforcement)

```python
# superclaude/modes/orchestration.py

class OrchestrationMode:
    TOOL_MATRIX = {
        "ui": "magic_mcp",
        "analysis": "sequential_mcp",
    }

    @classmethod
    def select_tool(cls, task_type: str) -> str:
        return cls.TOOL_MATRIX.get(task_type, "native")

# Usage
tool = OrchestrationMode.select_tool("ui")  # "magic_mcp" (enforced)
```

**Benefits**:
- ✅ 50 tokens on import
- ✅ Enforced at runtime
- ✅ Testable with pytest
- ✅ No redundancy (DRY)

## Migration Checklist

### Per Mode Migration

- [ ] Read existing Markdown mode
- [ ] Extract rules and behaviors
- [ ] Design Python class structure
- [ ] Implement with type hints
- [ ] Write tests (>80% coverage)
- [ ] Benchmark token usage
- [ ] Update command to use Python
- [ ] Keep Markdown as documentation

### Testing Strategy

```python
# tests/modes/test_orchestration.py

def test_tool_selection():
    """Verify tool selection matrix"""
    assert OrchestrationMode.select_tool("ui") == "magic_mcp"
    assert OrchestrationMode.select_tool("analysis") == "sequential_mcp"

def test_parallel_trigger():
    """Verify parallel execution auto-triggers"""
    assert OrchestrationMode.enforce_parallel([1, 2, 3]) == True
    assert OrchestrationMode.enforce_parallel([1, 2]) == False

def test_resource_zones():
    """Verify resource management enforcement"""
    mode = OrchestrationMode(context_usage=0.9)
    assert mode.zone == ResourceZone.RED
    assert mode.select_tool("ui") == "native"  # RED zone: essential only
```

## Expected Outcomes

### Token Efficiency

**Before Migration**:
```
Per Session:
- Modes: 26,716 tokens
- Agents: 40,000+ tokens (pm-agent + others)
- Total: ~66,000 tokens/session

Annual (200 sessions):
- Total: 13,200,000 tokens
- Cost: ~$26-50/year
```

**After Python Migration**:
```
Per Session:
- Mode imports: ~500 tokens
- Agent imports: ~1,000 tokens
- PROJECT_INDEX: 3,000 tokens
- Total: ~4,500 tokens/session

Annual (200 sessions):
- Total: 900,000 tokens
- Cost: ~$2-4/year

Savings: 93% tokens, 90%+ cost
```

**After Skills Migration**:
```
Per Session:
- Skill descriptions: ~300 tokens
- PROJECT_INDEX: 3,000 tokens
- On-demand loads: varies
- Total: ~3,500 tokens/session (unused modes)

Savings: 95%+ tokens
```

### Quality Improvements

**Markdown**:
- ❌ No enforcement (just documentation)
- ❌ Can't verify compliance
- ❌ Can't test effectiveness
- ❌ Prone to drift

**Python**:
- ✅ Enforced at runtime
- ✅ 100% testable
- ✅ Type-safe with hints
- ✅ Single source of truth

## Risks and Mitigation

**Risk 1**: Breaking existing workflows
- **Mitigation**: Keep Markdown as fallback docs

**Risk 2**: Skills API immaturity
- **Mitigation**: Python-first works now, Skills later

**Risk 3**: Implementation complexity
- **Mitigation**: Incremental migration (1 mode at a time)

## Conclusion

**Recommended Path**:

1. ✅ **Done**: Index command + auto-indexing (94% savings)
2. **Next**: Orchestration mode → Python (93% savings)
3. **Then**: PM Agent → Python (97% savings)
4. **Future**: Skills prototype + full migration (98% savings)

**Total Expected Savings**: 93-98% token reduction

---

**Start Date**: 2025-10-20
**Target Completion**: 2026-01-20 (3 months for full migration)
**Quick Win**: Orchestration mode (1 week)
