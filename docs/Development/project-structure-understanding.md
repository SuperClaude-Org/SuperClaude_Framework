# SuperClaude Framework - Project Structure Understanding

> **Critical Understanding**: The relationship between this project and the post-install environment

---

## Distinguishing the Two Worlds

### 1. This Project (Git-managed / Development Environment)

**Location**: `~/github/SuperClaude_Framework/`

**Role**: Source code, development, and testing

```
SuperClaude_Framework/
├── setup/                  # Installer logic
│   ├── components/         # Component definitions (what to install)
│   ├── data/              # Configuration data (JSON/YAML)
│   ├── cli/               # CLI interface
│   ├── utils/             # Utility functions
│   └── services/          # Service logic
│
├── superclaude/           # Runtime logic (execution behavior)
│   ├── core/             # Core functionality
│   ├── modes/            # Behavioral modes
│   ├── agents/           # Agent definitions
│   ├── mcp/              # MCP server integration
│   └── commands/         # Command implementations
│
├── tests/                # Test code
├── docs/                 # Developer documentation
├── pyproject.toml        # Python configuration
└── package.json          # npm configuration
```

**Operations**:
- ✅ Source code changes
- ✅ Git commits and PRs
- ✅ Test execution
- ✅ Documentation creation
- ✅ Version management

---

### 2. Post-Install (User Environment / Outside Git Management)

**Location**: `~/.claude/`

**Role**: Configuration and commands that actually run (user environment)

```
~/.claude/
├── commands/
│   └── sc/              # Slash commands (post-install)
│       ├── pm.md
│       ├── implement.md
│       ├── test.md
│       └── ... (26 commands)
│
├── CLAUDE.md            # Global configuration (post-install)
├── *.md                 # Mode definitions (post-install)
│   ├── MODE_Brainstorming.md
│   ├── MODE_Orchestration.md
│   └── ...
│
└── .claude.json         # Claude Code configuration
```

**Operations**:
- ✅ **Read only** (for understanding and verification)
- ✅ Behavior verification
- ⚠️ Temporary changes only during testing (**must always be restored!**)
- ❌ Permanent changes prohibited (cannot be Git-tracked)

---

## Installation Flow

### User Operations
```bash
# 1. Install
pipx install SuperClaude
# or
npm install -g @bifrost_inc/superclaude

# 2. Run setup
SuperClaude install
```

### Internal Processing (executed by setup/)
```python
# setup/components/*.py is executed

1. Create ~/.claude/ directory
2. Place slash commands in commands/sc/
3. Place CLAUDE.md and various *.md files
4. Update .claude.json
5. MCP server configuration
```

### Result
- **Files from this project** → **Copied to ~/.claude/**
- User launches Claude → Settings from `~/.claude/` are loaded
- Execute `/sc:pm` → `~/.claude/commands/sc/pm.md` is expanded

---

## Development Workflow

### Incorrect Approach
```bash
# Directly modifying files outside Git management
vim ~/.claude/commands/sc/pm.md  # ← Don't do this! History can't be tracked

# Test changes
claude  # Verify behavior

# Changes remain in ~/.claude/
# → Forget to revert
# → Configuration becomes messy
# → Cannot be tracked with Git
```

### Correct Approach

#### Step 1: Understand Existing Implementation
```bash
cd ~/github/SuperClaude_Framework

# Review install logic
Read setup/components/commands.py    # How commands are installed
Read setup/components/modes.py       # How modes are installed
Read setup/data/commands.json        # Command definition data

# Review post-install state (for understanding)
ls ~/.claude/commands/sc/
cat ~/.claude/commands/sc/pm.md      # Review current specification

# "I see, so setup/components/commands.py processes it like this,
#  and it gets placed in ~/.claude/commands/sc/"
```

#### Step 2: Document Improvement Proposals
```bash
cd ~/github/SuperClaude_Framework

# Within this Git-managed project
Write docs/Development/hypothesis-pm-improvement-YYYY-MM-DD.md

# Example content:
# - Current problems
# - Improvement proposals
# - Implementation approach
# - Expected outcomes
```

#### Step 3: When Testing is Needed
```bash
# Create backup (required!)
cp ~/.claude/commands/sc/pm.md ~/.claude/commands/sc/pm.md.backup

# Experimental changes
vim ~/.claude/commands/sc/pm.md

# Launch Claude and verify
claude
# ... verify behavior ...

# After testing, always restore!!
mv ~/.claude/commands/sc/pm.md.backup ~/.claude/commands/sc/pm.md
```

#### Step 4: Actual Implementation
```bash
cd ~/github/SuperClaude_Framework

# Make changes on the source code side
Edit setup/components/commands.py    # Modify install logic
Edit setup/data/commands/pm.md       # Modify command specification

# Add tests
Write tests/test_pm_command.py

# Run tests
pytest tests/test_pm_command.py -v

# Commit (recorded in Git history)
git add setup/ tests/
git commit -m "feat: enhance PM command with autonomous workflow"
```

#### Step 5: Verify Behavior
```bash
# Development install
cd ~/github/SuperClaude_Framework
pip install -e .

# or
SuperClaude install --dev

# Test in actual environment
claude
/sc:pm "test request"
```

---

## Important Rules

### Rule 1: Respect the Git Management Boundary
- **Changes**: Only within this project
- **Verification**: `~/.claude/` is read-only
- **Testing**: Backup → Change → Restore

### Rule 2: Always Restore After Testing
```bash
# Before testing
cp original backup

# Testing
# ... experiment ...

# After testing (required!)
mv backup original
```

### Rule 3: Document-Driven Development
1. Understanding → Record in docs/Development/
2. Hypothesis → docs/Development/hypothesis-*.md
3. Experiment → docs/Development/experiment-*.md
4. Success → docs/patterns/
5. Failure → docs/mistakes/

---

## Files to Understand

### Installer Side (setup/)
```python
# Priority: High
setup/components/commands.py    # Command installation
setup/components/modes.py       # Mode installation
setup/components/agents.py      # Agent definitions
setup/data/commands/*.md        # Command specifications (source)
setup/data/modes/*.md           # Mode specifications (source)

# These are what get placed in ~/.claude/
```

### Runtime Side (superclaude/)
```python
# Priority: Medium
superclaude/__main__.py         # CLI entry point
superclaude/core/              # Core functionality implementation
superclaude/agents/            # Agent logic
```

### Post-Install (~/.claude/)
```markdown
# Priority: For understanding only (do not modify)
~/.claude/commands/sc/pm.md    # Actual running PM specification
~/.claude/MODE_*.md            # Actual running mode specifications
~/.claude/CLAUDE.md            # Actual loaded global configuration
```

---

## Debugging Methods

### Verify Installation
```bash
# Check installed components
SuperClaude install --list-components

# Check installation destination
ls -la ~/.claude/commands/sc/
ls -la ~/.claude/*.md
```

### Verify Behavior
```bash
# Launch Claude
claude

# Execute command
/sc:pm "test"

# Check logs (as needed)
tail -f ~/.claude/logs/*.log
```

### Troubleshooting
```bash
# If configuration is broken
SuperClaude install --force    # Reinstall

# Switch to development version
cd ~/github/SuperClaude_Framework
pip install -e .

# Return to production version
pip uninstall superclaude
pipx install SuperClaude
```

---

## Common Mistakes

### Mistake 1: Modifying Files Outside Git Management
```bash
# WRONG
vim ~/.claude/commands/sc/pm.md
git add ~/.claude/  # ← Can't do this! Outside Git management
```

### Mistake 2: Testing Without Backup
```bash
# WRONG
vim ~/.claude/commands/sc/pm.md
# Testing...
# Forget to revert → Configuration becomes messy
```

### Mistake 3: Making Changes Without Reviewing Source
```bash
# WRONG
"I want to fix PM mode"
→ Immediately modify ~/.claude/
→ Don't understand the source code
→ Gets overwritten on reinstall
```

### Correct Approach
```bash
# CORRECT
1. Understand logic in setup/components/
2. Record improvement proposals in docs/Development/
3. Make changes and test in setup/ side
4. Git commit
5. Verify behavior with SuperClaude install --dev
```

---

## Next Steps

After understanding this document:

1. **Read setup/components/**
   - Understand installation logic
   - What gets placed where

2. **Understand existing specifications**
   - Review `~/.claude/commands/sc/pm.md` (read-only)
   - Understand current behavior

3. **Create improvement proposals**
   - Create `docs/Development/hypothesis-*.md`
   - User review

4. **Implement and test**
   - Make changes in `setup/` side
   - Add tests in `tests/`
   - Develop under Git management

This way, **we won't need to repeat the same explanation hundreds of times**.
