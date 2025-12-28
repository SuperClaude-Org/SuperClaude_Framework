# Complete Python + Skills Migration Plan

**Date**: 2025-10-20
**Goal**: 全部Python化 + Skills API移行で98%トークン削減
**Timeline**: 3週間で完了

## Current Waste (毎セッション)

```
Markdown読み込み: 41,000 tokens
PM Agent (最大): 4,050 tokens
モード全部: 6,679 tokens
エージェント: 30,000+ tokens

= 毎回41,000トークン無駄
```

## 3-Week Migration Plan

### Week 1: PM Agent Python化 + インテリジェント判断

#### Day 1-2: PM Agent Core Python実装

**File**: `superclaude/agents/pm_agent.py`

```python
"""
PM Agent - Python Implementation
Intelligent orchestration with automatic optimization
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import subprocess
import sys

@dataclass
class IndexStatus:
    """Repository index status"""
    exists: bool
    age_days: int
    needs_update: bool
    reason: str

@dataclass
class ConfidenceScore:
    """Pre-execution confidence assessment"""
    requirement_clarity: float  # 0-1
    context_loaded: bool
    similar_mistakes: list
    confidence: float  # Overall 0-1

    def should_proceed(self) -> bool:
        """Only proceed if >70% confidence"""
        return self.confidence > 0.7

class PMAgent:
    """
    Project Manager Agent - Python Implementation

    Intelligent behaviors:
    - Auto-checks index freshness
    - Updates index only when needed
    - Pre-execution confidence check
    - Post-execution validation
    - Reflexion learning
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.index_path = repo_path / "PROJECT_INDEX.md"
        self.index_threshold_days = 7

    def session_start(self) -> Dict[str, Any]:
        """
        Session initialization with intelligent optimization

        Returns context loading strategy
        """
        print("🤖 PM Agent: Session start")

        # 1. Check index status
        index_status = self.check_index_status()

        # 2. Intelligent decision
        if index_status.needs_update:
            print(f"🔄 {index_status.reason}")
            self.update_index()
        else:
            print(f"✅ Index is fresh ({index_status.age_days} days old)")

        # 3. Load index for context
        context = self.load_context_from_index()

        # 4. Load reflexion memory
        mistakes = self.load_reflexion_memory()

        return {
            "index_status": index_status,
            "context": context,
            "mistakes": mistakes,
            "token_usage": len(context) // 4,  # Rough estimate
        }

    def check_index_status(self) -> IndexStatus:
        """
        Intelligent index freshness check

        Decision logic:
        - No index: needs_update=True
        - >7 days: needs_update=True
        - Recent git activity (>20 files): needs_update=True
        - Otherwise: needs_update=False
        """
        if not self.index_path.exists():
            return IndexStatus(
                exists=False,
                age_days=999,
                needs_update=True,
                reason="Index doesn't exist - creating"
            )

        # Check age
        mtime = datetime.fromtimestamp(self.index_path.stat().st_mtime)
        age = datetime.now() - mtime
        age_days = age.days

        if age_days > self.index_threshold_days:
            return IndexStatus(
                exists=True,
                age_days=age_days,
                needs_update=True,
                reason=f"Index is {age_days} days old (>7) - updating"
            )

        # Check recent git activity
        if self.has_significant_changes():
            return IndexStatus(
                exists=True,
                age_days=age_days,
                needs_update=True,
                reason="Significant changes detected (>20 files) - updating"
            )

        # Index is fresh
        return IndexStatus(
            exists=True,
            age_days=age_days,
            needs_update=False,
            reason="Index is up to date"
        )

    def has_significant_changes(self) -> bool:
        """Check if >20 files changed since last index"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                changed_files = [line for line in result.stdout.splitlines() if line.strip()]
                return len(changed_files) > 20

        except Exception:
            pass

        return False

    def update_index(self) -> bool:
        """Run parallel repository indexer"""
        indexer_script = self.repo_path / "superclaude" / "indexing" / "parallel_repository_indexer.py"

        if not indexer_script.exists():
            print(f"⚠️ Indexer not found: {indexer_script}")
            return False

        try:
            print("📊 Running parallel indexing...")
            result = subprocess.run(
                [sys.executable, str(indexer_script)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print("✅ Index updated successfully")
                return True
            else:
                print(f"❌ Indexing failed: {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print("⚠️ Indexing timed out (>5min)")
            return False
        except Exception as e:
            print(f"⚠️ Indexing error: {e}")
            return False

    def load_context_from_index(self) -> str:
        """Load project context from index (3,000 tokens vs 50,000)"""
        if self.index_path.exists():
            return self.index_path.read_text()
        return ""

    def load_reflexion_memory(self) -> list:
        """Load past mistakes for learning"""
        from superclaude.memory import ReflexionMemory

        memory = ReflexionMemory(self.repo_path)
        data = memory.load()
        return data.get("recent_mistakes", [])

    def check_confidence(self, task: str) -> ConfidenceScore:
        """
        Pre-execution confidence check

        ENFORCED: Stop if confidence <70%
        """
        # Load context
        context = self.load_context_from_index()
        context_loaded = len(context) > 100

        # Check for similar past mistakes
        mistakes = self.load_reflexion_memory()
        similar = [m for m in mistakes if task.lower() in m.get("task", "").lower()]

        # Calculate clarity (simplified - would use LLM in real impl)
        has_specifics = any(word in task.lower() for word in ["create", "fix", "add", "update", "delete"])
        clarity = 0.8 if has_specifics else 0.4

        # Overall confidence
        confidence = clarity * 0.7 + (0.3 if context_loaded else 0)

        return ConfidenceScore(
            requirement_clarity=clarity,
            context_loaded=context_loaded,
            similar_mistakes=similar,
            confidence=confidence
        )

    def execute_with_validation(self, task: str) -> Dict[str, Any]:
        """
        4-Phase workflow (ENFORCED)

        PLANNING → TASKLIST → DO → REFLECT
        """
        print("\n" + "="*80)
        print("🤖 PM Agent: 4-Phase Execution")
        print("="*80)

        # PHASE 1: PLANNING (with confidence check)
        print("\n📋 PHASE 1: PLANNING")
        confidence = self.check_confidence(task)
        print(f"   Confidence: {confidence.confidence:.0%}")

        if not confidence.should_proceed():
            return {
                "phase": "PLANNING",
                "status": "BLOCKED",
                "reason": f"Low confidence ({confidence.confidence:.0%}) - need clarification",
                "suggestions": [
                    "Provide more specific requirements",
                    "Clarify expected outcomes",
                    "Break down into smaller tasks"
                ]
            }

        # PHASE 2: TASKLIST
        print("\n📝 PHASE 2: TASKLIST")
        tasks = self.decompose_task(task)
        print(f"   Decomposed into {len(tasks)} subtasks")

        # PHASE 3: DO (with validation gates)
        print("\n⚙️ PHASE 3: DO")
        from superclaude.validators import ValidationGate

        validator = ValidationGate()
        results = []

        for i, subtask in enumerate(tasks, 1):
            print(f"   [{i}/{len(tasks)}] {subtask['description']}")

            # Validate before execution
            validation = validator.validate_all(subtask)
            if not validation.all_passed():
                print(f"      ❌ Validation failed: {validation.errors}")
                return {
                    "phase": "DO",
                    "status": "VALIDATION_FAILED",
                    "subtask": subtask,
                    "errors": validation.errors
                }

            # Execute (placeholder - real implementation would call actual execution)
            result = {"subtask": subtask, "status": "success"}
            results.append(result)
            print(f"      ✅ Completed")

        # PHASE 4: REFLECT
        print("\n🔍 PHASE 4: REFLECT")
        self.learn_from_execution(task, tasks, results)
        print("   📚 Learning captured")

        print("\n" + "="*80)
        print("✅ Task completed successfully")
        print("="*80 + "\n")

        return {
            "phase": "REFLECT",
            "status": "SUCCESS",
            "tasks_completed": len(tasks),
            "learning_captured": True
        }

    def decompose_task(self, task: str) -> list:
        """Decompose task into subtasks (simplified)"""
        # Real implementation would use LLM
        return [
            {"description": "Analyze requirements", "type": "analysis"},
            {"description": "Implement changes", "type": "implementation"},
            {"description": "Run tests", "type": "validation"},
        ]

    def learn_from_execution(self, task: str, tasks: list, results: list) -> None:
        """Capture learning in reflexion memory"""
        from superclaude.memory import ReflexionMemory, ReflexionEntry

        memory = ReflexionMemory(self.repo_path)

        # Check for mistakes in execution
        mistakes = [r for r in results if r.get("status") != "success"]

        if mistakes:
            for mistake in mistakes:
                entry = ReflexionEntry(
                    task=task,
                    mistake=mistake.get("error", "Unknown error"),
                    evidence=str(mistake),
                    rule=f"Prevent: {mistake.get('error')}",
                    fix="Add validation before similar operations",
                    tests=[],
                )
                memory.add_entry(entry)


# Singleton instance
_pm_agent: Optional[PMAgent] = None

def get_pm_agent(repo_path: Optional[Path] = None) -> PMAgent:
    """Get or create PM agent singleton"""
    global _pm_agent

    if _pm_agent is None:
        if repo_path is None:
            repo_path = Path.cwd()
        _pm_agent = PMAgent(repo_path)

    return _pm_agent


# Session start hook (called automatically)
def pm_session_start() -> Dict[str, Any]:
    """
    Called automatically at session start

    Intelligent behaviors:
    - Check index freshness
    - Update if needed
    - Load context efficiently
    """
    agent = get_pm_agent()
    return agent.session_start()
```

**Token Savings**:
- Before: 4,050 tokens (pm-agent.md 毎回読む)
- After: ~100 tokens (import header のみ)
- **Savings: 97%**

#### Day 3-4: PM Agent統合とテスト

**File**: `tests/agents/test_pm_agent.py`

```python
"""Tests for PM Agent Python implementation"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from superclaude.agents.pm_agent import PMAgent, IndexStatus, ConfidenceScore

class TestPMAgent:
    """Test PM Agent intelligent behaviors"""

    def test_index_check_missing(self, tmp_path):
        """Test index check when index doesn't exist"""
        agent = PMAgent(tmp_path)
        status = agent.check_index_status()

        assert status.exists is False
        assert status.needs_update is True
        assert "doesn't exist" in status.reason

    def test_index_check_old(self, tmp_path):
        """Test index check when index is >7 days old"""
        index_path = tmp_path / "PROJECT_INDEX.md"
        index_path.write_text("Old index")

        # Set mtime to 10 days ago
        old_time = (datetime.now() - timedelta(days=10)).timestamp()
        import os
        os.utime(index_path, (old_time, old_time))

        agent = PMAgent(tmp_path)
        status = agent.check_index_status()

        assert status.exists is True
        assert status.age_days >= 10
        assert status.needs_update is True

    def test_index_check_fresh(self, tmp_path):
        """Test index check when index is fresh (<7 days)"""
        index_path = tmp_path / "PROJECT_INDEX.md"
        index_path.write_text("Fresh index")

        agent = PMAgent(tmp_path)
        status = agent.check_index_status()

        assert status.exists is True
        assert status.age_days < 7
        assert status.needs_update is False

    def test_confidence_check_high(self, tmp_path):
        """Test confidence check with clear requirements"""
        # Create index
        (tmp_path / "PROJECT_INDEX.md").write_text("Context loaded")

        agent = PMAgent(tmp_path)
        confidence = agent.check_confidence("Create new validator for security checks")

        assert confidence.confidence > 0.7
        assert confidence.should_proceed() is True

    def test_confidence_check_low(self, tmp_path):
        """Test confidence check with vague requirements"""
        agent = PMAgent(tmp_path)
        confidence = agent.check_confidence("Do something")

        assert confidence.confidence < 0.7
        assert confidence.should_proceed() is False

    def test_session_start_creates_index(self, tmp_path):
        """Test session start creates index if missing"""
        # Create minimal structure for indexer
        (tmp_path / "superclaude").mkdir()
        (tmp_path / "superclaude" / "indexing").mkdir()

        agent = PMAgent(tmp_path)
        # Would test session_start() but requires full indexer setup

        status = agent.check_index_status()
        assert status.needs_update is True
```

#### Day 5: PM Command統合

**Update**: `plugins/superclaude/commands/pm.md`

```markdown
---
name: pm
description: "PM Agent with intelligent optimization (Python-powered)"
---

⏺ PM ready (Python-powered)

**Intelligent Behaviors** (自動):
- ✅ Index freshness check (自動判断)
- ✅ Smart index updates (必要時のみ)
- ✅ Pre-execution confidence check (>70%)
- ✅ Post-execution validation
- ✅ Reflexion learning

**Token Efficiency**:
- Before: 4,050 tokens (Markdown毎回)
- After: ~100 tokens (Python import)
- Savings: 97%

**Session Start** (自動実行):
```python
from superclaude.agents.pm_agent import pm_session_start

# Automatically called
result = pm_session_start()
# - Checks index freshness
# - Updates if >7 days or >20 file changes
# - Loads context efficiently
```

**4-Phase Execution** (enforced):
```python
agent = get_pm_agent()
result = agent.execute_with_validation(task)
# PLANNING → confidence check
# TASKLIST → decompose
# DO → validation gates
# REFLECT → learning capture
```

---

**Implementation**: `superclaude/agents/pm_agent.py`
**Tests**: `tests/agents/test_pm_agent.py`
**Token Savings**: 97% (4,050 → 100 tokens)
```

### Week 2: 全モードPython化

#### Day 6-7: Orchestration Mode Python

**File**: `superclaude/modes/orchestration.py`

```python
"""
Orchestration Mode - Python Implementation
Intelligent tool selection and resource management
"""

from enum import Enum
from typing import Literal, Optional, Dict, Any
from functools import wraps

class ResourceZone(Enum):
    """Resource usage zones with automatic behavior adjustment"""
    GREEN = (0, 75)    # Full capabilities
    YELLOW = (75, 85)  # Efficiency mode
    RED = (85, 100)    # Essential only

    def contains(self, usage: float) -> bool:
        """Check if usage falls in this zone"""
        return self.value[0] <= usage < self.value[1]

class OrchestrationMode:
    """
    Intelligent tool selection and resource management

    ENFORCED behaviors (not just documented):
    - Tool selection matrix
    - Parallel execution triggers
    - Resource-aware optimization
    """

    # Tool selection matrix (ENFORCED)
    TOOL_MATRIX: Dict[str, str] = {
        "ui_components": "magic_mcp",
        "deep_analysis": "sequential_mcp",
        "symbol_operations": "serena_mcp",
        "pattern_edits": "morphllm_mcp",
        "documentation": "context7_mcp",
        "browser_testing": "playwright_mcp",
        "multi_file_edits": "multiedit",
        "code_search": "grep",
    }

    def __init__(self, context_usage: float = 0.0):
        self.context_usage = context_usage
        self.zone = self._detect_zone()

    def _detect_zone(self) -> ResourceZone:
        """Detect current resource zone"""
        for zone in ResourceZone:
            if zone.contains(self.context_usage):
                return zone
        return ResourceZone.GREEN

    def select_tool(self, task_type: str) -> str:
        """
        Select optimal tool based on task type and resources

        ENFORCED: Returns correct tool, not just recommendation
        """
        # RED ZONE: Override to essential tools only
        if self.zone == ResourceZone.RED:
            return "native"  # Use native tools only

        # YELLOW ZONE: Prefer efficient tools
        if self.zone == ResourceZone.YELLOW:
            efficient_tools = {"grep", "native", "multiedit"}
            selected = self.TOOL_MATRIX.get(task_type, "native")
            if selected not in efficient_tools:
                return "native"  # Downgrade to native

        # GREEN ZONE: Use optimal tool
        return self.TOOL_MATRIX.get(task_type, "native")

    @staticmethod
    def should_parallelize(files: list) -> bool:
        """
        Auto-trigger parallel execution

        ENFORCED: Returns True for 3+ files
        """
        return len(files) >= 3

    @staticmethod
    def should_delegate(complexity: Dict[str, Any]) -> bool:
        """
        Auto-trigger agent delegation

        ENFORCED: Returns True for:
        - >7 directories
        - >50 files
        - complexity score >0.8
        """
        dirs = complexity.get("directories", 0)
        files = complexity.get("files", 0)
        score = complexity.get("score", 0.0)

        return dirs > 7 or files > 50 or score > 0.8

    def optimize_execution(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize execution based on context and resources

        Returns execution strategy
        """
        task_type = operation.get("type", "unknown")
        files = operation.get("files", [])

        strategy = {
            "tool": self.select_tool(task_type),
            "parallel": self.should_parallelize(files),
            "zone": self.zone.name,
            "context_usage": self.context_usage,
        }

        # Add resource-specific optimizations
        if self.zone == ResourceZone.YELLOW:
            strategy["verbosity"] = "reduced"
            strategy["defer_non_critical"] = True
        elif self.zone == ResourceZone.RED:
            strategy["verbosity"] = "minimal"
            strategy["essential_only"] = True

        return strategy


# Decorator for automatic orchestration
def with_orchestration(func):
    """Apply orchestration mode to function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get context usage from environment
        context_usage = kwargs.pop("context_usage", 0.0)

        # Create orchestration mode
        mode = OrchestrationMode(context_usage)

        # Add mode to kwargs
        kwargs["orchestration"] = mode

        return func(*args, **kwargs)
    return wrapper


# Singleton instance
_orchestration_mode: Optional[OrchestrationMode] = None

def get_orchestration_mode(context_usage: float = 0.0) -> OrchestrationMode:
    """Get or create orchestration mode"""
    global _orchestration_mode

    if _orchestration_mode is None:
        _orchestration_mode = OrchestrationMode(context_usage)
    else:
        _orchestration_mode.context_usage = context_usage
        _orchestration_mode.zone = _orchestration_mode._detect_zone()

    return _orchestration_mode
```

**Token Savings**:
- Before: 689 tokens (MODE_Orchestration.md)
- After: ~50 tokens (import only)
- **Savings: 93%**

#### Day 8-10: 残りのモードPython化

**Files to create**:
- `superclaude/modes/brainstorming.py` (533 tokens → 50)
- `superclaude/modes/introspection.py` (465 tokens → 50)
- `superclaude/modes/task_management.py` (893 tokens → 50)
- `superclaude/modes/token_efficiency.py` (757 tokens → 50)
- `superclaude/modes/deep_research.py` (400 tokens → 50)
- `superclaude/modes/business_panel.py` (2,940 tokens → 100)

**Total Savings**: 6,677 tokens → 400 tokens = **94% reduction**

### Week 3: Skills API Migration

#### Day 11-13: Skills Structure Setup

**Directory**: `skills/`

```
skills/
├── pm-mode/
│   ├── SKILL.md              # 200 bytes (lazy-load trigger)
│   ├── agent.py              # Full PM implementation
│   ├── memory.py             # Reflexion memory
│   └── validators.py         # Validation gates
│
├── orchestration-mode/
│   ├── SKILL.md
│   └── mode.py
│
├── brainstorming-mode/
│   ├── SKILL.md
│   └── mode.py
│
└── ...
```

**Example**: `skills/pm-mode/SKILL.md`

```markdown
---
name: pm-mode
description: Project Manager Agent with intelligent optimization
version: 1.0.0
author: SuperClaude
---

# PM Mode

Intelligent project management with automatic optimization.

**Capabilities**:
- Index freshness checking
- Pre-execution confidence
- Post-execution validation
- Reflexion learning

**Activation**: `/sc:pm` or auto-detect complex tasks

**Resources**: agent.py, memory.py, validators.py
```

**Token Cost**:
- Description only: ~50 tokens
- Full load (when used): ~2,000 tokens
- Never used: Forever 50 tokens

#### Day 14-15: Skills Integration

**Update**: Claude Code config to use Skills

```json
{
  "skills": {
    "enabled": true,
    "path": "~/.claude/skills",
    "auto_load": false,
    "lazy_load": true
  }
}
```

**Migration**:
```bash
# Copy Python implementations to skills/
cp -r superclaude/agents/pm_agent.py skills/pm-mode/agent.py
cp -r superclaude/modes/*.py skills/*/mode.py

# Create SKILL.md for each
for dir in skills/*/; do
  create_skill_md "$dir"
done
```

#### Day 16-17: Testing & Benchmarking

**Benchmark script**: `tests/performance/test_skills_efficiency.py`

```python
"""Benchmark Skills API token efficiency"""

def test_skills_token_overhead():
    """Measure token overhead with Skills"""

    # Baseline (no skills)
    baseline = measure_session_tokens(skills_enabled=False)

    # Skills loaded but not used
    skills_loaded = measure_session_tokens(
        skills_enabled=True,
        skills_used=[]
    )

    # Skills loaded and PM mode used
    skills_used = measure_session_tokens(
        skills_enabled=True,
        skills_used=["pm-mode"]
    )

    # Assertions
    assert skills_loaded - baseline < 500  # <500 token overhead
    assert skills_used - baseline < 3000   # <3K when 1 skill used

    print(f"Baseline: {baseline} tokens")
    print(f"Skills loaded: {skills_loaded} tokens (+{skills_loaded - baseline})")
    print(f"Skills used: {skills_used} tokens (+{skills_used - baseline})")

    # Target: >95% savings vs current Markdown
    current_markdown = 41000
    savings = (current_markdown - skills_loaded) / current_markdown

    assert savings > 0.95  # >95% savings
    print(f"Savings: {savings:.1%}")
```

#### Day 18-19: Documentation & Cleanup

**Update all docs**:
- README.md - Skills説明追加
- CONTRIBUTING.md - Skills開発ガイド
- docs/user-guide/skills.md - ユーザーガイド

**Cleanup**:
- Markdownファイルをarchive/に移動（削除しない）
- Python実装をメイン化
- Skills実装を推奨パスに

#### Day 20-21: Issue #441報告 & PR準備

**Report to Issue #441**:
```markdown
## Skills Migration Prototype Results

We've successfully migrated PM Mode to Skills API with the following results:

**Token Efficiency**:
- Before (Markdown): 4,050 tokens per session
- After (Skills, unused): 50 tokens per session
- After (Skills, used): 2,100 tokens per session
- **Savings**: 98.8% when unused, 48% when used

**Implementation**:
- Python-first approach for enforcement
- Skills for lazy-loading
- Full test coverage (26 tests)

**Code**: [Link to branch]

**Benchmark**: [Link to benchmark results]

**Recommendation**: Full framework migration to Skills
```

## Expected Outcomes

### Token Usage Comparison

```
Current (Markdown):
├─ Session start: 41,000 tokens
├─ PM Agent: 4,050 tokens
├─ Modes: 6,677 tokens
└─ Total: ~41,000 tokens/session

After Python Migration:
├─ Session start: 4,500 tokens
│  ├─ INDEX.md: 3,000 tokens
│  ├─ PM import: 100 tokens
│  ├─ Mode imports: 400 tokens
│  └─ Other: 1,000 tokens
└─ Savings: 89%

After Skills Migration:
├─ Session start: 3,500 tokens
│  ├─ INDEX.md: 3,000 tokens
│  ├─ Skill descriptions: 300 tokens
│  └─ Other: 200 tokens
├─ When PM used: +2,000 tokens (first time)
└─ Savings: 91% (unused), 86% (used)
```

### Annual Savings

**200 sessions/year**:

```
Current:
41,000 × 200 = 8,200,000 tokens/year
Cost: ~$16-32/year

After Python:
4,500 × 200 = 900,000 tokens/year
Cost: ~$2-4/year
Savings: 89% tokens, 88% cost

After Skills:
3,500 × 200 = 700,000 tokens/year
Cost: ~$1.40-2.80/year
Savings: 91% tokens, 91% cost
```

## Implementation Checklist

### Week 1: PM Agent
- [ ] Day 1-2: PM Agent Python core
- [ ] Day 3-4: Tests & validation
- [ ] Day 5: Command integration

### Week 2: Modes
- [ ] Day 6-7: Orchestration Mode
- [ ] Day 8-10: All other modes
- [ ] Tests for each mode

### Week 3: Skills
- [ ] Day 11-13: Skills structure
- [ ] Day 14-15: Skills integration
- [ ] Day 16-17: Testing & benchmarking
- [ ] Day 18-19: Documentation
- [ ] Day 20-21: Issue #441 report

## Risk Mitigation

**Risk 1**: Breaking changes
- Keep Markdown in archive/ for fallback
- Gradual rollout (PM → Modes → Skills)

**Risk 2**: Skills API instability
- Python-first works independently
- Skills as optional enhancement

**Risk 3**: Performance regression
- Comprehensive benchmarks before/after
- Rollback plan if <80% savings

## Success Criteria

- ✅ **Token reduction**: >90% vs current
- ✅ **Enforcement**: Python behaviors testable
- ✅ **Skills working**: Lazy-load verified
- ✅ **Tests passing**: 100% coverage
- ✅ **Upstream value**: Issue #441 contribution ready

---

**Start**: Week of 2025-10-21
**Target Completion**: 2025-11-11 (3 weeks)
**Status**: Ready to begin
