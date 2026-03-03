# Extract: Skills Migration Patterns and Development Guide

**Source**: `/config/workspace/SuperClaude_Framework/docs/research/complete-python-skills-migration.md`
**Extracted by**: Opus 4.6
**Date**: 2026-02-21
**Focus**: Custom commands, skills, and agents development for the SuperClaude framework

---

## 1. Skills Directory Organization

The Skills API uses a directory-per-skill convention under a top-level `skills/` directory. Each skill is a self-contained package with a `SKILL.md` manifest and supporting Python modules.

### Canonical Directory Structure

From the source document:

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

Key points:
- Each skill lives in its own directory under `skills/`.
- Directory naming convention uses kebab-case (e.g., `pm-mode`, `orchestration-mode`, `brainstorming-mode`).
- Every skill directory must contain a `SKILL.md` file.
- Python modules within each skill provide the actual implementation.

---

## 2. SKILL.md Structure and Requirements

The `SKILL.md` file serves as a lightweight manifest and lazy-load trigger. It uses YAML frontmatter followed by a brief Markdown description.

### Example SKILL.md (pm-mode)

Exact content from the source:

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

### SKILL.md Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill identifier (kebab-case, matches directory name) |
| `description` | Yes | One-line description of the skill's purpose |
| `version` | Yes | Semantic version (e.g., `1.0.0`) |
| `author` | Yes | Author name |

### SKILL.md Body Sections

- **Title**: `# Skill Name` heading
- **Description**: Brief prose description of the skill
- **Capabilities**: Bulleted list of what the skill provides
- **Activation**: How to invoke the skill (slash command or auto-detect trigger)
- **Resources**: List of Python files that implement the skill

### Token Cost Model

The document explicitly states:

> - Description only: ~50 tokens
> - Full load (when used): ~2,000 tokens
> - Never used: Forever 50 tokens

The SKILL.md is deliberately kept small (~200 bytes) to serve as a "lazy-load trigger" -- only the description is loaded at session start. Full Python code loads on demand.

---

## 3. How Skills Are Loaded and Executed

### Loading Strategy: Lazy-Load

The Skills API uses a lazy-loading architecture. From the configuration example:

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

Key configuration fields:
- `enabled`: Toggle skills system on/off
- `path`: Where skills are installed (`~/.claude/skills`)
- `auto_load`: Set to `false` -- skills are NOT loaded into context at session start
- `lazy_load`: Set to `true` -- skills load only when invoked

### Execution Flow

1. **Session start**: Only `SKILL.md` description text is loaded (~50 tokens per skill). Full Python code is NOT loaded.
2. **On invocation**: When a skill is triggered (via slash command or auto-detection), the full Python implementation loads (~2,000 tokens for pm-mode).
3. **Never used**: If a skill is never invoked during a session, it costs only its ~50-token description forever.

### Token Budget at Session Start

From the "After Skills Migration" section:

```
After Skills Migration:
├── Session start: 3,500 tokens
│   ├── INDEX.md: 3,000 tokens
│   ├── Skill descriptions: 300 tokens
│   └── Other: 200 tokens
├── When PM used: +2,000 tokens (first time)
└── Savings: 91% (unused), 86% (used)
```

---

## 4. Skill Migration Patterns (Old Markdown to New Skills Format)

### Migration from Markdown-Based Agents/Modes to Python Skills

The document describes a three-phase migration strategy:

#### Phase 1 (Week 1): Python-ize the Agent

Convert a Markdown-based agent definition into a Python class.

**Before**: Large Markdown file read into context every session (e.g., `pm-agent.md` at 4,050 tokens)
**After**: Python module with import header only (~100 tokens)

> "Token Savings:
> - Before: 4,050 tokens (pm-agent.md read every session)
> - After: ~100 tokens (import header only)
> - Savings: 97%"

Example Python implementation pattern (from the PM Agent):

```python
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

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
        # ...
```

Key patterns:
- Use `@dataclass` for structured data types
- Use class-based design for the agent itself
- Provide a singleton accessor function
- Provide a session hook function

Singleton and hook pattern:

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
    """Called automatically at session start"""
    agent = get_pm_agent()
    return agent.session_start()
```

#### Phase 2 (Week 2): Python-ize All Modes

Convert each Markdown mode file to a Python module:

| Mode | Before (tokens) | After (tokens) | Savings |
|------|-----------------|----------------|---------|
| Orchestration | 689 | ~50 | 93% |
| Brainstorming | 533 | ~50 | 91% |
| Introspection | 465 | ~50 | 89% |
| Task Management | 893 | ~50 | 94% |
| Token Efficiency | 757 | ~50 | 93% |
| Deep Research | 400 | ~50 | 88% |
| Business Panel | 2,940 | ~100 | 97% |
| **Total** | **6,677** | **400** | **94%** |

#### Phase 3 (Week 3): Package as Skills

Move Python implementations into the skills directory structure:

```bash
# Copy Python implementations to skills/
cp -r superclaude/agents/pm_agent.py skills/pm-mode/agent.py
cp -r superclaude/modes/*.py skills/*/mode.py

# Create SKILL.md for each
for dir in skills/*/; do
  create_skill_md "$dir"
done
```

### Migration Safety / Risk Mitigation

From the document:

> **Risk 1**: Breaking changes
> - Keep Markdown in archive/ for fallback
> - Gradual rollout (PM -> Modes -> Skills)
>
> **Risk 2**: Skills API instability
> - Python-first works independently
> - Skills as optional enhancement
>
> **Risk 3**: Performance regression
> - Comprehensive benchmarks before/after
> - Rollback plan if <80% savings

Key safety principles:
- Never delete old Markdown files -- move them to `archive/`
- Python implementation works standalone even if Skills API is unavailable
- Skills layer is an optional enhancement on top of the Python implementation
- Gradual rollout order: PM Agent first, then Modes, then full Skills packaging

---

## 5. Command Integration Pattern

When a Python-backed skill replaces a Markdown command, the command file is updated to reference the Python implementation. Example from the PM command update:

```markdown
---
name: pm
description: "PM Agent with intelligent optimization (Python-powered)"
---

⏺ PM ready (Python-powered)

**Intelligent Behaviors** (automatic):
- Index freshness check (automatic decision)
- Smart index updates (only when needed)
- Pre-execution confidence check (>70%)
- Post-execution validation
- Reflexion learning

**Token Efficiency**:
- Before: 4,050 tokens (Markdown every time)
- After: ~100 tokens (Python import)
- Savings: 97%

**Session Start** (auto-executed):
```python
from superclaude.agents.pm_agent import pm_session_start

# Automatically called
result = pm_session_start()
```

**4-Phase Execution** (enforced):
```python
agent = get_pm_agent()
result = agent.execute_with_validation(task)
# PLANNING -> confidence check
# TASKLIST -> decompose
# DO -> validation gates
# REFLECT -> learning capture
```
```

The command `.md` file becomes a thin wrapper that:
1. Provides frontmatter metadata (`name`, `description`)
2. Documents capabilities for the user
3. References the Python implementation via import statements
4. Specifies the execution entry points

---

## 6. Testing Skills

### Test Structure

Tests for migrated skills live in a parallel test directory:

```
tests/agents/test_pm_agent.py    # For PM agent skill
tests/performance/test_skills_efficiency.py  # For benchmarking
```

### Benchmark Pattern

The document provides a benchmark test pattern for validating skill token efficiency:

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

    # Target: >95% savings vs current Markdown
    current_markdown = 41000
    savings = (current_markdown - skills_loaded) / current_markdown
    assert savings > 0.95  # >95% savings
```

### Success Criteria

From the document:

> - Token reduction: >90% vs current
> - Enforcement: Python behaviors testable
> - Skills working: Lazy-load verified
> - Tests passing: 100% coverage
> - Upstream value: Issue #441 contribution ready

---

## 7. Overall Token Savings Summary

### Per-Session Comparison

```
Current (Markdown):
├── Session start: 41,000 tokens
├── PM Agent: 4,050 tokens
├── Modes: 6,677 tokens
└── Total: ~41,000 tokens/session

After Python Migration:
├── Session start: 4,500 tokens
│   ├── INDEX.md: 3,000 tokens
│   ├── PM import: 100 tokens
│   ├── Mode imports: 400 tokens
│   └── Other: 1,000 tokens
└── Savings: 89%

After Skills Migration:
├── Session start: 3,500 tokens
│   ├── INDEX.md: 3,000 tokens
│   ├── Skill descriptions: 300 tokens
│   └── Other: 200 tokens
├── When PM used: +2,000 tokens (first time)
└── Savings: 91% (unused), 86% (used)
```

### Annual Projection (200 sessions/year)

```
Current:      8,200,000 tokens/year (~$16-32/year)
After Python:   900,000 tokens/year (~$2-4/year)   -- 89% savings
After Skills:   700,000 tokens/year (~$1.40-2.80/year) -- 91% savings
```
