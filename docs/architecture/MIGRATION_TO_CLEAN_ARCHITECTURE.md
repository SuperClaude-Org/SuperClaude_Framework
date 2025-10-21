# Migration to Clean Plugin Architecture

**Date**: 2025-10-21
**Status**: Planning → Implementation
**Goal**: Zero-footprint pytest plugin + Optional skills system

---

## 🎯 Design Philosophy

### Before (Polluting Design)
```yaml
Problem:
  - Installs to ~/.claude/superclaude/ (pollutes Claude Code)
  - Complex Component/Installer infrastructure (468-line base class)
  - Skills vs Commands混在 (2つのメカニズム)
  - setup.py packaging (deprecated)

Impact:
  - Claude Code directory pollution
  - Difficult to maintain
  - Not pip-installable cleanly
  - Confusing for users
```

### After (Clean Design)
```yaml
Solution:
  - Python package in site-packages/ only
  - pytest plugin via entry points (auto-discovery)
  - Optional Skills (user choice to install)
  - PEP 517 src/ layout (modern packaging)

Benefits:
  ✅ Zero ~/.claude/ pollution (unless user wants skills)
  ✅ pip install superclaude → pytest auto-loads
  ✅ Standard pytest plugin architecture
  ✅ Clear separation: core vs user config
  ✅ Tests stay in project root (not installed)
```

---

## 📂 New Directory Structure

```
superclaude/
├── src/                           # PEP 517 source layout
│   └── superclaude/              # Actual package
│       ├── __init__.py           # Package metadata
│       ├── __version__.py        # Version info
│       ├── pytest_plugin.py      # ⭐ pytest entry point
│       │
│       ├── pm_agent/             # PM Agent core logic
│       │   ├── __init__.py
│       │   ├── confidence.py     # Pre-execution confidence check
│       │   ├── self_check.py     # Post-implementation validation
│       │   ├── reflexion.py      # Error learning pattern
│       │   ├── token_budget.py   # Budget-aware operations
│       │   └── parallel.py       # Parallel-with-reflection
│       │
│       ├── cli/                  # CLI commands
│       │   ├── __init__.py
│       │   ├── main.py           # Entry point
│       │   ├── install_skill.py  # superclaude install-skill
│       │   └── doctor.py         # superclaude doctor
│       │
│       └── skills/               # Skill templates (not installed by default)
│           └── pm/               # PM Agent skill
│               ├── implementation.md
│               └── modules/
│                   ├── git-status.md
│                   ├── token-counter.md
│                   └── pm-formatter.md
│
├── tests/                        # Test suite (NOT installed)
│   ├── conftest.py              # pytest config + fixtures
│   ├── test_confidence_check.py
│   ├── test_self_check_protocol.py
│   ├── test_token_budget.py
│   ├── test_reflexion_pattern.py
│   └── test_pytest_plugin.py    # Plugin integration tests
│
├── docs/                         # Documentation
│   ├── architecture/
│   │   └── MIGRATION_TO_CLEAN_ARCHITECTURE.md (this file)
│   └── research/
│
├── scripts/                      # Utility scripts (not installed)
│   ├── analyze_workflow_metrics.py
│   └── ab_test_workflows.py
│
├── pyproject.toml               # ⭐ PEP 517 packaging + entry points
├── README.md
└── LICENSE
```

---

## 🔧 Entry Points Configuration

### pyproject.toml (New)

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "superclaude"
version = "0.4.0"
description = "AI-enhanced development framework for Claude Code"
readme = "README.md"
license = {file = "LICENSE"}
authors = [
    {name = "Kazuki Nakai"}
]
requires-python = ">=3.10"
dependencies = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest-benchmark>=4.0.0",
    "scipy>=1.10.0",  # For A/B testing
]

# ⭐ pytest plugin auto-discovery
[project.entry-points.pytest11]
superclaude = "superclaude.pytest_plugin"

# ⭐ CLI commands
[project.entry-points.console_scripts]
superclaude = "superclaude.cli.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "hallucination: Hallucination detection tests",
    "performance: Performance benchmark tests",
]

[tool.hatch.build.targets.wheel]
packages = ["src/superclaude"]
```

---

## 🎨 Core Components

### 1. pytest Plugin Entry Point

**File**: `src/superclaude/pytest_plugin.py`

```python
"""
SuperClaude pytest plugin

Auto-loaded when superclaude is installed.
Provides PM Agent fixtures and hooks for enhanced testing.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from .pm_agent.confidence import ConfidenceChecker
from .pm_agent.self_check import SelfCheckProtocol
from .pm_agent.reflexion import ReflexionPattern
from .pm_agent.token_budget import TokenBudgetManager


def pytest_configure(config):
    """Register SuperClaude plugin and markers"""
    config.addinivalue_line(
        "markers",
        "confidence_check: Pre-execution confidence assessment"
    )
    config.addinivalue_line(
        "markers",
        "self_check: Post-implementation validation"
    )
    config.addinivalue_line(
        "markers",
        "reflexion: Error learning and prevention"
    )


@pytest.fixture
def confidence_checker():
    """Fixture for confidence checking"""
    return ConfidenceChecker()


@pytest.fixture
def self_check_protocol():
    """Fixture for self-check protocol"""
    return SelfCheckProtocol()


@pytest.fixture
def reflexion_pattern():
    """Fixture for reflexion pattern"""
    return ReflexionPattern()


@pytest.fixture
def token_budget(request):
    """Fixture for token budget management"""
    # Get test complexity from marker
    marker = request.node.get_closest_marker("complexity")
    complexity = marker.args[0] if marker else "medium"
    return TokenBudgetManager(complexity=complexity)


@pytest.fixture
def pm_context(tmp_path):
    """
    Fixture providing PM Agent context for testing

    Creates temporary memory directory structure:
    - docs/memory/pm_context.md
    - docs/memory/last_session.md
    - docs/memory/next_actions.md
    """
    memory_dir = tmp_path / "docs" / "memory"
    memory_dir.mkdir(parents=True)

    return {
        "memory_dir": memory_dir,
        "pm_context": memory_dir / "pm_context.md",
        "last_session": memory_dir / "last_session.md",
        "next_actions": memory_dir / "next_actions.md",
    }


def pytest_runtest_setup(item):
    """
    Pre-test hook for confidence checking

    If test is marked with @pytest.mark.confidence_check,
    run pre-execution confidence assessment.
    """
    marker = item.get_closest_marker("confidence_check")
    if marker:
        checker = ConfidenceChecker()
        confidence = checker.assess(item)

        if confidence < 0.7:
            pytest.skip(f"Confidence too low: {confidence:.0%}")


def pytest_runtest_makereport(item, call):
    """
    Post-test hook for self-check and reflexion

    Records test outcomes for reflexion learning.
    """
    if call.when == "call":
        marker = item.get_closest_marker("reflexion")
        if marker and call.excinfo is not None:
            # Test failed - apply reflexion pattern
            reflexion = ReflexionPattern()
            reflexion.record_error(
                test_name=item.name,
                error=call.excinfo.value,
                traceback=call.excinfo.traceback
            )
```

### 2. PM Agent Core Modules

**File**: `src/superclaude/pm_agent/confidence.py`

```python
"""
Pre-execution confidence check

Prevents wrong-direction execution by assessing confidence BEFORE starting.
"""

from typing import Dict, Any


class ConfidenceChecker:
    """
    Pre-implementation confidence assessment

    Usage:
        checker = ConfidenceChecker()
        confidence = checker.assess(context)

        if confidence >= 0.9:
            # High confidence - proceed
        elif confidence >= 0.7:
            # Medium confidence - present options
        else:
            # Low confidence - stop and request clarification
    """

    def assess(self, context: Any) -> float:
        """
        Assess confidence level (0.0 - 1.0)

        Checks:
        - Official documentation verified?
        - Existing patterns identified?
        - Implementation path clear?

        Returns:
            float: Confidence score (0.0 = no confidence, 1.0 = absolute)
        """
        score = 0.0
        checks = []

        # Check 1: Documentation verified (40%)
        if self._has_official_docs(context):
            score += 0.4
            checks.append("✅ Official documentation")
        else:
            checks.append("❌ Missing documentation")

        # Check 2: Existing patterns (30%)
        if self._has_existing_patterns(context):
            score += 0.3
            checks.append("✅ Existing patterns found")
        else:
            checks.append("❌ No existing patterns")

        # Check 3: Clear implementation path (30%)
        if self._has_clear_path(context):
            score += 0.3
            checks.append("✅ Implementation path clear")
        else:
            checks.append("❌ Implementation unclear")

        return score

    def _has_official_docs(self, context: Any) -> bool:
        """Check if official documentation exists"""
        # Placeholder - implement actual check
        return True

    def _has_existing_patterns(self, context: Any) -> bool:
        """Check if existing patterns can be followed"""
        # Placeholder - implement actual check
        return True

    def _has_clear_path(self, context: Any) -> bool:
        """Check if implementation path is clear"""
        # Placeholder - implement actual check
        return True
```

**File**: `src/superclaude/pm_agent/self_check.py`

```python
"""
Post-implementation self-check protocol

Hallucination prevention through evidence-based validation.
"""

from typing import Dict, List, Tuple


class SelfCheckProtocol:
    """
    Post-implementation validation

    The Four Questions:
    1. テストは全てpassしてる？
    2. 要件を全て満たしてる？
    3. 思い込みで実装してない？
    4. 証拠はある？
    """

    def validate(self, implementation: Dict) -> Tuple[bool, List[str]]:
        """
        Run self-check validation

        Args:
            implementation: Implementation details

        Returns:
            Tuple of (passed: bool, issues: List[str])
        """
        issues = []

        # Question 1: Tests passing?
        if not self._check_tests_passing(implementation):
            issues.append("❌ Tests not passing")

        # Question 2: Requirements met?
        if not self._check_requirements_met(implementation):
            issues.append("❌ Requirements not fully met")

        # Question 3: Assumptions verified?
        if not self._check_assumptions_verified(implementation):
            issues.append("❌ Unverified assumptions detected")

        # Question 4: Evidence provided?
        if not self._check_evidence_exists(implementation):
            issues.append("❌ Missing evidence")

        return len(issues) == 0, issues

    def _check_tests_passing(self, impl: Dict) -> bool:
        """Verify all tests pass"""
        # Placeholder - check test results
        return impl.get("tests_passed", False)

    def _check_requirements_met(self, impl: Dict) -> bool:
        """Verify all requirements satisfied"""
        # Placeholder - check requirements
        return impl.get("requirements_met", False)

    def _check_assumptions_verified(self, impl: Dict) -> bool:
        """Verify assumptions checked against docs"""
        # Placeholder - check assumptions
        return impl.get("assumptions_verified", True)

    def _check_evidence_exists(self, impl: Dict) -> bool:
        """Verify evidence provided"""
        # Placeholder - check evidence
        return impl.get("evidence_provided", False)
```

### 3. CLI Commands

**File**: `src/superclaude/cli/main.py`

```python
"""
SuperClaude CLI

Commands:
  superclaude install-skill pm-agent  # Install PM Agent skill to ~/.claude/skills/
  superclaude doctor                   # Check installation health
"""

import click
from pathlib import Path


@click.group()
@click.version_option()
def main():
    """SuperClaude - AI-enhanced development framework"""
    pass


@main.command()
@click.argument("skill_name")
@click.option("--target", default="~/.claude/skills", help="Installation directory")
def install_skill(skill_name: str, target: str):
    """
    Install a SuperClaude skill to Claude Code

    Example:
        superclaude install-skill pm-agent
    """
    from ..skills import install_skill as install_fn

    target_path = Path(target).expanduser()
    click.echo(f"Installing skill '{skill_name}' to {target_path}...")

    if install_fn(skill_name, target_path):
        click.echo("✅ Skill installed successfully")
    else:
        click.echo("❌ Skill installation failed", err=True)


@main.command()
def doctor():
    """Check SuperClaude installation health"""
    click.echo("🔍 SuperClaude Doctor\n")

    # Check pytest plugin loaded
    import pytest
    config = pytest.Config.fromdictargs({}, [])
    plugins = config.pluginmanager.list_plugin_distinfo()

    superclaude_loaded = any(
        "superclaude" in str(plugin[0])
        for plugin in plugins
    )

    if superclaude_loaded:
        click.echo("✅ pytest plugin loaded")
    else:
        click.echo("❌ pytest plugin not loaded")

    # Check skills installed
    skills_dir = Path("~/.claude/skills").expanduser()
    if skills_dir.exists():
        skills = list(skills_dir.glob("*/implementation.md"))
        click.echo(f"✅ {len(skills)} skills installed")
    else:
        click.echo("⚠️  No skills installed (optional)")

    click.echo("\n✅ SuperClaude is healthy")


if __name__ == "__main__":
    main()
```

---

## 📋 Migration Checklist

### Phase 1: Restructure (Day 1)

- [ ] Create `src/superclaude/` directory
- [ ] Move current `superclaude/` → `src/superclaude/`
- [ ] Create `src/superclaude/pytest_plugin.py`
- [ ] Extract PM Agent logic from Skills:
  - [ ] `pm_agent/confidence.py`
  - [ ] `pm_agent/self_check.py`
  - [ ] `pm_agent/reflexion.py`
  - [ ] `pm_agent/token_budget.py`
- [ ] Create `cli/` directory:
  - [ ] `cli/main.py`
  - [ ] `cli/install_skill.py`
- [ ] Update `pyproject.toml` with entry points
- [ ] Remove old `setup.py`
- [ ] Remove `setup/` directory (Component/Installer infrastructure)

### Phase 2: Test Migration (Day 2)

- [ ] Update `tests/conftest.py` for new structure
- [ ] Migrate tests to use pytest plugin fixtures
- [ ] Add `test_pytest_plugin.py` integration tests
- [ ] Use `pytester` fixture for plugin testing
- [ ] Run: `pytest tests/ -v` → All tests pass
- [ ] Verify entry_points.txt generation

### Phase 3: Clean Installation (Day 3)

- [ ] Test: `pip install -e .` (editable mode)
- [ ] Verify: `pytest --trace-config` shows superclaude plugin
- [ ] Verify: `~/.claude/` remains clean (no pollution)
- [ ] Test: `superclaude doctor` command works
- [ ] Test: `superclaude install-skill pm-agent`
- [ ] Verify: Skill installed to `~/.claude/skills/pm/`

### Phase 4: Documentation Update (Day 4)

- [ ] Update README.md with new installation instructions
- [ ] Document pytest plugin usage
- [ ] Document CLI commands
- [ ] Update CLAUDE.md (project instructions)
- [ ] Create migration guide for users

---

## 🧪 Testing Strategy

### Unit Tests (Existing)
```bash
pytest tests/test_confidence_check.py -v
pytest tests/test_self_check_protocol.py -v
pytest tests/test_token_budget.py -v
pytest tests/test_reflexion_pattern.py -v
```

### Integration Tests (New)
```python
# tests/test_pytest_plugin.py

def test_plugin_loads(pytester):
    """Test that superclaude plugin loads correctly"""
    pytester.makeconftest("""
        pytest_plugins = ['superclaude.pytest_plugin']
    """)

    result = pytester.runpytest("--trace-config")
    result.stdout.fnmatch_lines(["*superclaude*"])


def test_confidence_checker_fixture(pytester):
    """Test confidence_checker fixture availability"""
    pytester.makepyfile("""
        def test_example(confidence_checker):
            assert confidence_checker is not None
            confidence = confidence_checker.assess({})
            assert 0.0 <= confidence <= 1.0
    """)

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
```

### Installation Tests
```bash
# Clean install
pip uninstall superclaude -y
pip install -e .

# Verify plugin loaded
pytest --trace-config | grep superclaude

# Verify CLI
superclaude --version
superclaude doctor

# Verify ~/.claude/ clean
ls ~/.claude/  # Should not have superclaude/ unless skill installed
```

---

## 🚀 Installation Instructions (New)

### For Users

```bash
# Install from PyPI (future)
pip install superclaude

# Install from source (development)
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework
pip install -e .

# Verify installation
superclaude doctor

# Optional: Install PM Agent skill
superclaude install-skill pm-agent
```

### For Developers

```bash
# Clone repository
git clone https://github.com/SuperClaude-Org/SuperClaude_Framework.git
cd SuperClaude_Framework

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Check pytest plugin
pytest --trace-config
```

---

## 📊 Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **~/.claude/ pollution** | ❌ Always polluted | ✅ Clean (unless skill installed) |
| **Packaging** | ❌ setup.py (deprecated) | ✅ PEP 517 pyproject.toml |
| **pytest integration** | ❌ Manual | ✅ Auto-discovery via entry points |
| **Installation** | ❌ Custom installer | ✅ Standard pip install |
| **Test location** | ❌ Installed to site-packages | ✅ Stays in project root |
| **Complexity** | ❌ 468-line Component base | ✅ Simple pytest plugin |
| **User choice** | ❌ Forced installation | ✅ Optional skills |

---

## 🎯 Success Criteria

- [ ] `pip install superclaude` works cleanly
- [ ] pytest auto-discovers superclaude plugin
- [ ] `~/.claude/` remains untouched after `pip install`
- [ ] All existing tests pass with new structure
- [ ] `superclaude doctor` reports healthy
- [ ] Skills install optionally: `superclaude install-skill pm-agent`
- [ ] Documentation updated and accurate

---

**Status**: Ready to implement ✅
**Next**: Phase 1 - Restructure to src/ layout
