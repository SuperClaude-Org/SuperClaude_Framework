# Extraction — Custom Commands, Skills, and Agents Development

**Source file**: `/config/workspace/SuperClaude_Framework/docs/research/complete-python-skills-migration.md`

This document extracts **all information pertaining to developing custom commands, skills, or agents** for the SuperClaude framework, preserving exact quotes and code blocks.

---

## 1) Slash Commands / Custom Commands (command docs + integration points)

### 1.1 PM command integration (example command markdown)

The migration plan describes integrating a Python agent implementation into a slash command definition.

**Quote**:

> "#### Day 5: PM Command統合"

**Target file to update (as stated)**:

> "**Update**: `plugins/superclaude/commands/pm.md`"

**Exact command markdown example**:

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

#### 1.2 How the command calls into Python

The command markdown includes Python snippets demonstrating the integration contract.

**Exact code blocks (as shown)**:

```python
from superclaude.agents.pm_agent import pm_session_start

# Automatically called
result = pm_session_start()
# - Checks index freshness
# - Updates if >7 days or >20 file changes
# - Loads context efficiently
```

```python
agent = get_pm_agent()
result = agent.execute_with_validation(task)
# PLANNING → confidence check
# TASKLIST → decompose
# DO → validation gates
# REFLECT → learning capture
```

---

## 2) Agents (Python implementations + hooks + behavior contracts)

### 2.1 PM Agent Python implementation (agent architecture)

**Quote (file location)**:

> "**File**: `superclaude/agents/pm_agent.py`"

**Agent core concepts (quotes)**:

> "PM Agent - Python Implementation"

> "Intelligent orchestration with automatic optimization"

> "Intelligent behaviors:
> - Auto-checks index freshness
> - Updates index only when needed
> - Pre-execution confidence check
> - Post-execution validation
> - Reflexion learning"

#### 2.1.1 Dataclasses used by the agent

**Exact code block excerpt**:

```python
from dataclasses import dataclass

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
```

#### 2.1.2 Agent class responsibilities

**Exact code block excerpt (docstring highlights)**:

```python
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
```

#### 2.1.3 Session start hook

The plan describes a session-start entrypoint function used by the command.

**Quote**:

> "# Session start hook (called automatically)"

**Exact code block excerpt**:

```python
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

#### 2.1.4 Execution workflow enforced by the agent

The agent’s “execute_with_validation” method defines a 4-phase workflow.

**Quote**:

> "4-Phase workflow (ENFORCED)"

> "PLANNING → TASKLIST → DO → REFLECT"

**Exact code block excerpt (phase labeling)**:

```python
def execute_with_validation(self, task: str) -> Dict[str, Any]:
    """
    4-Phase workflow (ENFORCED)

    PLANNING → TASKLIST → DO → REFLECT
    """
```

#### 2.1.5 Validation gates integration point

The agent references a `ValidationGate` object used before executing each subtask.

**Exact code block excerpt**:

```python
from superclaude.validators import ValidationGate

validator = ValidationGate()
...
validation = validator.validate_all(subtask)
if not validation.all_passed():
    print(f"      ❌ Validation failed: {validation.errors}")
    return {
        "phase": "DO",
        "status": "VALIDATION_FAILED",
        "subtask": subtask,
        "errors": validation.errors
    }
```

#### 2.1.6 Reflexion memory integration point

The plan uses a `ReflexionMemory` and `ReflexionEntry` for learning.

**Exact code block excerpt**:

```python
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
```

#### 2.1.7 Indexing / context loading behavior (agent-side)

The agent’s index behavior defines decision logic and calls an indexer script.

**Quote (decision logic)**:

> "Decision logic:
> - No index: needs_update=True
> - >7 days: needs_update=True
> - Recent git activity (>20 files): needs_update=True
> - Otherwise: needs_update=False"

**Exact code block excerpt (indexer path + invocation)**:

```python
indexer_script = self.repo_path / "superclaude" / "indexing" / "parallel_repository_indexer.py"

if not indexer_script.exists():
    print(f"⚠️ Indexer not found: {indexer_script}")
    return False

result = subprocess.run(
    [sys.executable, str(indexer_script)],
    cwd=self.repo_path,
    capture_output=True,
    text=True,
    timeout=300
)
```

**Exact code block excerpt (context load)**:

```python
def load_context_from_index(self) -> str:
    """Load project context from index (3,000 tokens vs 50,000)"""
    if self.index_path.exists():
        return self.index_path.read_text()
    return ""
```

---

## 3) Skills (Skill API structure, SKILL.md contract, configuration, migration steps)

### 3.1 Skills directory structure

**Quote**:

> "#### Day 11-13: Skills Structure Setup"

> "**Directory**: `skills/`"

**Exact directory tree (as shown)**:

```text
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

### 3.2 SKILL.md format and contents (example)

**Quote**:

> "**Example**: `skills/pm-mode/SKILL.md`"

**Exact example**:

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

### 3.3 Skills configuration (Claude Code config)

**Quote**:

> "#### Day 14-15: Skills Integration"

> "**Update**: Claude Code config to use Skills"

**Exact JSON block**:

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

### 3.4 Skills migration commands / steps

The plan includes shell commands to move Python implementations into the Skills layout and generate SKILL.md.

**Quote**:

> "**Migration**:"

**Exact commands**:

```bash
# Copy Python implementations to skills/
cp -r superclaude/agents/pm_agent.py skills/pm-mode/agent.py
cp -r superclaude/modes/*.py skills/*/mode.py

# Create SKILL.md for each
for dir in skills/*/; do
  create_skill_md "$dir"
done
```

### 3.5 Skills token model (lazy-load rationale)

This section explains why skills are structured with a small SKILL.md plus heavier code files.

**Exact quotes**:

> "**Token Cost**:
> - Description only: ~50 tokens
> - Full load (when used): ~2,000 tokens
> - Never used: Forever 50 tokens"

---

## 4) Modes as skill components (example: orchestration mode implementation)

Although “modes” are not exactly “commands”, this plan treats them as code modules and later migrates them into `skills/*/mode.py`.

### 4.1 Orchestration mode: tool selection & delegation triggers

**Quote (file location)**:

> "**File**: `superclaude/modes/orchestration.py`"

**Tool selection matrix (exact code)**:

```python
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
```

**Parallelization trigger (exact code)**:

```python
@staticmethod
def should_parallelize(files: list) -> bool:
    """
    Auto-trigger parallel execution

    ENFORCED: Returns True for 3+ files
    """
    return len(files) >= 3
```

**Delegation trigger (exact code)**:

```python
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
```

### 4.2 Planned conversion of modes into skills

**Quote (files to create)**:

> "**Files to create**:
> - `superclaude/modes/brainstorming.py` (533 tokens → 50)
> - `superclaude/modes/introspection.py` (465 tokens → 50)
> - `superclaude/modes/task_management.py` (893 tokens → 50)
> - `superclaude/modes/token_efficiency.py` (757 tokens → 50)
> - `superclaude/modes/deep_research.py` (400 tokens → 50)
> - `superclaude/modes/business_panel.py` (2,940 tokens → 100)"

**Quote (migration destination mapping)**:

> "cp -r superclaude/modes/*.py skills/*/mode.py"

---

## 5) Testing guidance for agents/skills (tests + benchmarks)

### 5.1 PM agent tests

**Quote (test file)**:

> "**File**: `tests/agents/test_pm_agent.py`"

**Exact test import snippet**:

```python
from superclaude.agents.pm_agent import PMAgent, IndexStatus, ConfidenceScore
```

The tests assert behavior relevant to agent development, including index freshness logic and confidence thresholds.

**Examples (exact assertions as shown)**:

```python
assert status.exists is False
assert status.needs_update is True
assert "doesn't exist" in status.reason
```

```python
confidence = agent.check_confidence("Create new validator for security checks")
assert confidence.confidence > 0.7
assert confidence.should_proceed() is True
```

```python
confidence = agent.check_confidence("Do something")
assert confidence.confidence < 0.7
assert confidence.should_proceed() is False
```

### 5.2 Skills efficiency benchmark test

**Quote (benchmark script)**:

> "**Benchmark script**: `tests/performance/test_skills_efficiency.py`"

**Exact benchmark test**:

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

---

## 6) Development/maintenance notes that impact command/skill/agent work

### 6.1 Docs to update after skills migration

These targets are relevant when adding skills and custom command systems.

**Exact quotes**:

> "**Update all docs**:
> - README.md - Skills説明追加
> - CONTRIBUTING.md - Skills開発ガイド
> - docs/user-guide/skills.md - ユーザーガイド"

### 6.2 Cleanup strategy (archive old markdown)

**Exact quote**:

> "**Cleanup**:
> - Markdownファイルをarchive/に移動（削除しない）
> - Python実装をメイン化
> - Skills実装を推奨パスに"

### 6.3 Risk mitigation relevant to changes in skills/commands/agents

**Exact quotes**:

> "**Risk 1**: Breaking changes
> - Keep Markdown in archive/ for fallback
> - Gradual rollout (PM → Modes → Skills)"

> "**Risk 2**: Skills API instability
> - Python-first works independently
> - Skills as optional enhancement"

> "**Risk 3**: Performance regression
> - Comprehensive benchmarks before/after
> - Rollback plan if <80% savings"
