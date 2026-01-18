# PLANNING.md

**Architecture, Design Principles, and Absolute Rules for SuperClaude Framework**

> This document is read by Claude Code at session start to ensure consistent, high-quality development aligned with project standards.

---

## 🎯 **Project Vision**

SuperClaude Framework transforms Claude Code into a structured development platform through:
- **Behavioral instruction injection** via CLAUDE.md
- **Component orchestration** via pytest plugin + slash commands
- **Systematic workflow automation** via PM Agent patterns

**Core Mission**: Enhance AI-assisted development with:
- Pre-execution confidence checking (prevent wrong-direction work)
- Post-implementation validation (prevent hallucinations)
- Cross-session learning (reflexion pattern)
- Token-efficient parallel execution (3.5x speedup)

---

## 🏗️ **Architecture Overview**

### **Current State (v4.2.0)**

SuperClaude is a **Python package** with:
- Pytest plugin (auto-loaded via entry points)
- CLI tools (superclaude command)
- PM Agent patterns (confidence, self-check, reflexion)
- Parallel execution framework
- Optional slash commands (installed to ~/.claude/commands/)

```
SuperClaude Framework v4.2.0
│
├── Core Package (src/superclaude/)
│   ├── pytest_plugin.py          # Auto-loaded by pytest
│   ├── pm_agent/                  # Pre/post implementation patterns
│   │   ├── confidence.py          # Pre-execution confidence check
│   │   ├── self_check.py          # Post-implementation validation
│   │   ├── reflexion.py           # Error learning
│   │   └── token_budget.py        # Token allocation
│   ├── execution/                 # Parallel execution
│   │   ├── parallel.py            # Wave→Checkpoint→Wave
│   │   ├── reflection.py          # Meta-reasoning
│   │   └── self_correction.py     # Error recovery
│   └── cli/                       # Command-line interface
│       ├── main.py                # superclaude command
│       ├── doctor.py              # Health checks
│       └── install_skill.py       # Skill installation
│
├── Plugin Source (plugins/superclaude/)  # v5.0 - NOT ACTIVE YET
│   ├── agents/                    # Agent definitions
│   ├── commands/                  # Command definitions
│   ├── hooks/                     # Hook configurations
│   ├── scripts/                   # Shell scripts
│   └── skills/                    # Skill implementations
│
├── Tests (tests/)
│   ├── unit/                      # Component unit tests
│   └── integration/               # Plugin integration tests
│
└── Documentation (docs/)
    ├── architecture/              # Architecture decisions
    ├── developer-guide/           # Development guides
    ├── reference/                 # API reference
    ├── research/                  # Research findings
    └── user-guide/                # User documentation
```

### **Future State (v5.0 - Planned)**

- TypeScript plugin system (issue #419)
- Project-local `.claude-plugin/` detection
- Plugin marketplace distribution
- Enhanced MCP server integration

---

## ⚙️ **Design Principles**

### **1. Evidence-Based Development**

**Never guess** - always verify with official sources:
- Use Context7 MCP for official documentation
- Use WebFetch/WebSearch for research
- Check existing code with Glob/Grep before implementing
- Verify assumptions against test results

**Anti-pattern**: Implementing based on assumptions or outdated knowledge

### **2. Confidence-First Implementation**

Check confidence BEFORE starting work:
- **≥90%**: Proceed with implementation
- **70-89%**: Present alternatives, continue investigation
- **<70%**: STOP - ask questions, investigate more

**ROI**: Spend 100-200 tokens on confidence check to save 5,000-50,000 tokens on wrong direction

### **3. Parallel-First Execution**

Use **Wave → Checkpoint → Wave** pattern:
```
Wave 1: [Read file1, Read file2, Read file3] (parallel)
   ↓
Checkpoint: Analyze all files together
   ↓
Wave 2: [Edit file1, Edit file2, Edit file3] (parallel)
```

**Benefit**: 3.5x faster than sequential execution

**When to use**:
- Independent operations (reading multiple files)
- Batch transformations (editing multiple files)
- Parallel searches (grep across different directories)

**When NOT to use**:
- Operations with dependencies (must wait for previous result)
- Sequential analysis (need to build context step-by-step)

### **4. Token Efficiency**

Allocate tokens based on task complexity:
- **Simple** (typo fix): 200 tokens
- **Medium** (bug fix): 1,000 tokens
- **Complex** (feature): 2,500 tokens

**Confidence check ROI**: 25-250x token savings

### **5. No Hallucinations**

Use SelfCheckProtocol to prevent hallucinations:

**The Four Questions**:
1. Are all tests passing? (show output)
2. Are all requirements met? (list items)
3. No assumptions without verification? (show docs)
4. Is there evidence? (test results, code changes, validation)

**7 Red Flags**:
- "Tests pass" without output
- "Everything works" without evidence
- "Implementation complete" with failing tests
- Skipping error messages
- Ignoring warnings
- Hiding failures
- "Probably works" language

---

## 🚫 **Absolute Rules**

### **Python Environment**

1. **ALWAYS use UV** for Python operations:
   ```bash
   uv run pytest              # NOT: python -m pytest
   uv pip install package     # NOT: pip install package
   uv run python script.py    # NOT: python script.py
   ```

2. **Package structure**: Use src/ layout
   - `src/superclaude/` for package code
   - `tests/` for test code
   - Never mix source and tests in same directory

3. **Entry points**: Use pyproject.toml
   - CLI: `[project.scripts]`
   - Pytest plugin: `[project.entry-points.pytest11]`

### **Testing**

1. **All new features MUST have tests**
   - Unit tests for individual components
   - Integration tests for component interactions
   - Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`

2. **Use PM Agent patterns in tests**:
   ```python
   @pytest.mark.confidence_check
   def test_feature(confidence_checker):
       context = {...}
       assert confidence_checker.assess(context) >= 0.7

   @pytest.mark.self_check
   def test_implementation(self_check_protocol):
       passed, issues = self_check_protocol.validate(impl)
       assert passed
   ```

3. **Test fixtures**: Use conftest.py for shared fixtures

### **Git Workflow**

1. **Branch structure**:
   - `master`: Production-ready code
   - `integration`: Testing ground (not yet created)
   - `feature/*`, `fix/*`, `docs/*`: Feature branches

2. **Commit messages**: Use conventional commits
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance

3. **Never commit**:
   - `__pycache__/`, `*.pyc`
   - `.venv/`, `venv/`
   - Personal files (TODO.txt, CRUSH.md)
   - API keys, secrets

### **Documentation**

1. **Code documentation**:
   - All public functions need docstrings
   - Use type hints
   - Include usage examples in docstrings

2. **Project documentation**:
   - Update CLAUDE.md for Claude Code guidance
   - Update README.md for user instructions
   - Update this PLANNING.md for architecture decisions
   - Update TASK.md for current work
   - Update KNOWLEDGE.md for insights

3. **Keep docs synchronized**:
   - When code changes, update relevant docs
   - When features are added, update CHANGELOG.md
   - When architecture changes, update PLANNING.md

### **Version Management**

1. **Version sources of truth**:
   - Framework version: `VERSION` file (e.g., 4.2.0)
   - Python package version: `pyproject.toml` (e.g., 0.4.0)
   - NPM package version: `package.json` (should match VERSION)

2. **When to bump versions**:
   - Major: Breaking API changes
   - Minor: New features, backward compatible
   - Patch: Bug fixes

---

## 🔄 **Development Workflow**

### **Starting a New Feature**

1. **Investigation Phase**:
   - Read PLANNING.md, TASK.md, KNOWLEDGE.md
   - Check for duplicates (Glob/Grep existing code)
   - Read official docs (Context7 MCP, WebFetch)
   - Search for OSS implementations (WebSearch)
   - Run confidence check (should be ≥90%)

2. **Implementation Phase**:
   - Create feature branch: `git checkout -b feature/feature-name`
   - Write tests first (TDD)
   - Implement feature
   - Run tests: `uv run pytest`
   - Run linter: `make lint`
   - Format code: `make format`

3. **Validation Phase**:
   - Run self-check protocol
   - Verify all tests passing
   - Check all requirements met
   - Confirm assumptions verified
   - Provide evidence

4. **Documentation Phase**:
   - Update relevant documentation
   - Add docstrings
   - Update CHANGELOG.md
   - Update TASK.md (mark complete)

5. **Review Phase**:
   - Create pull request
   - Request review
   - Address feedback
   - Merge to integration (or master if no integration branch)

### **Fixing a Bug**

1. **Root Cause Analysis**:
   - Reproduce the bug
   - Identify root cause (not symptoms)
   - Check reflexion memory for similar patterns
   - Run confidence check

2. **Fix Implementation**:
   - Write failing test that reproduces bug
   - Implement fix
   - Verify test passes
   - Run full test suite
   - Record in reflexion memory

3. **Prevention**:
   - Add regression test
   - Update documentation if needed
   - Share learnings in KNOWLEDGE.md

---

## 📊 **Quality Metrics**

### **Code Quality**

- **Test coverage**: Aim for >80%
- **Linting**: Zero ruff errors
- **Type checking**: Use type hints, minimal mypy errors
- **Documentation**: All public APIs documented

### **PM Agent Metrics**

- **Confidence check ROI**: 25-250x token savings
- **Self-check detection**: 94% hallucination detection rate
- **Parallel execution**: 3.5x speedup vs sequential
- **Token efficiency**: 30-50% reduction with proper budgeting

### **Release Criteria**

Before releasing a new version:
- ✅ All tests passing
- ✅ Documentation updated
- ✅ CHANGELOG.md updated
- ✅ Version numbers synced
- ✅ No known critical bugs
- ✅ Security audit passed (if applicable)

---

## 🚀 **Roadmap**

### **v4.2.0 (Current)**
- ✅ Python package with pytest plugin
- ✅ PM Agent patterns (confidence, self-check, reflexion)
- ✅ Parallel execution framework
- ✅ CLI tools and slash commands
- ✅ AIRIS MCP Gateway (optional, requires Docker)
- ✅ Explicit command boundaries and handoff instructions
- ✅ Complete command reference documentation

### **v4.3.0 (Next)**
- [ ] Complete placeholder implementations in confidence.py
- [ ] Add comprehensive test coverage (>80%)
- [ ] Enhanced MCP server integration
- [ ] Improve documentation

### **v5.0 (Future)**
- [ ] TypeScript plugin system (issue #419)
- [ ] Plugin marketplace
- [ ] Project-local plugin detection
- [ ] Enhanced reflexion with mindbase integration
- [ ] Advanced parallel execution patterns

---

## 🤝 **Contributing Guidelines**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

**Key points**:
- Follow absolute rules above
- Write tests for all new code
- Use PM Agent patterns
- Document your changes
- Request reviews

---

## 📚 **Additional Resources**

- **[TASK.md](TASK.md)**: Current tasks and priorities
- **[KNOWLEDGE.md](KNOWLEDGE.md)**: Accumulated insights and best practices
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
- **[docs/](docs/)**: Comprehensive documentation

---

*This document is maintained by the SuperClaude development team and should be updated whenever architectural decisions are made.*

**Last updated**: 2025-11-12 (auto-generated during issue #466 fix)
