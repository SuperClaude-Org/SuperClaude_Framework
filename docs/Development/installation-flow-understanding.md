# SuperClaude Installation Flow - Complete Understanding

> **Learning content**: Complete understanding of how the installer places files in `~/.claude/`

---

## Installation Flow Overview

### User Operations
```bash
# Step 1: Package installation
pipx install SuperClaude
# or
npm install -g @bifrost_inc/superclaude

# Step 2: Run setup
SuperClaude install
```

### Internal Processing Flow

```yaml
1. Entry Point:
   File: superclaude/__main__.py → main()

2. CLI Parser:
   File: superclaude/__main__.py → create_parser()
   Command: "install" subcommand registration

3. Component Manager:
   File: setup/cli/install.py
   Role: Coordination of install components

4. Commands Component:
   File: setup/components/commands.py → CommandsComponent
   Role: Installation of slash commands

5. Source Files:
   Location: superclaude/commands/*.md
   Content: pm.md, implement.md, test.md, etc.

6. Destination:
   Location: ~/.claude/commands/sc/*.md
   Result: Placed in user environment
```

---

## CommandsComponent Details

### Class Structure
```python
class CommandsComponent(Component):
    """
    Role: Installation and management of slash commands
    Parent: setup/core/base.py → Component
    Install Path: ~/.claude/commands/sc/
    """
```

### Key Methods

#### 1. `__init__()`
```python
def __init__(self, install_dir: Optional[Path] = None):
    super().__init__(install_dir, Path("commands/sc"))
```
**Understanding**:
- `install_dir`: `~/.claude/` (user environment)
- `Path("commands/sc")`: Subdirectory specification
- Result: Installs to `~/.claude/commands/sc/`

#### 2. `_get_source_dir()`
```python
def _get_source_dir(self) -> Path:
    # Calculated from the location of setup/components/commands.py
    project_root = Path(__file__).parent.parent.parent
    # → ~/github/SuperClaude_Framework/

    return project_root / "superclaude" / "commands"
    # → ~/github/SuperClaude_Framework/superclaude/commands/
```

**Understanding**:
```
Source: ~/github/SuperClaude_Framework/superclaude/commands/*.md
Target: ~/.claude/commands/sc/*.md

In other words:
superclaude/commands/pm.md
  ↓ copy
~/.claude/commands/sc/pm.md
```

#### 3. `_install()` - Installation Execution
```python
def _install(self, config: Dict[str, Any]) -> bool:
    self.logger.info("Installing SuperClaude command definitions...")

    # Migration of existing commands
    self._migrate_existing_commands()

    # Execute parent class installation
    return super()._install(config)
```

**Understanding**:
1. Log output
2. Migration processing from old version
3. Actual file copy (executed by parent class)

#### 4. `_migrate_existing_commands()` - Migration
```python
def _migrate_existing_commands(self) -> None:
    """
    Old Location: ~/.claude/commands/*.md
    New Location: ~/.claude/commands/sc/*.md

    Processing for V3 → V4 migration
    """
    old_commands_dir = self.install_dir / "commands"
    new_commands_dir = self.install_dir / "commands" / "sc"

    # Detect files from old location
    # Copy to new location
    # Delete from old location
```

**Understanding**:
- V3: `/analyze` → V4: `/sc:analyze`
- `/sc:` prefix to prevent namespace collisions

#### 5. `_post_install()` - Metadata Update
```python
def _post_install(self) -> bool:
    # Metadata update
    metadata_mods = self.get_metadata_modifications()
    self.settings_manager.update_metadata(metadata_mods)

    # Component registration
    self.settings_manager.add_component_registration(
        "commands",
        {
            "version": __version__,
            "category": "commands",
            "files_count": len(self.component_files),
        },
    )
```

**Understanding**:
- Updates `~/.claude/.superclaude.json`
- Records installed components
- Version management

---

## Actual File Mapping

### Source (this project)
```
~/github/SuperClaude_Framework/superclaude/commands/
├── pm.md                  # PM Agent definition
├── implement.md           # Implement command
├── test.md                # Test command
├── analyze.md             # Analyze command
├── research.md            # Research command
├── ... (26 commands total)
```

### Destination (user environment)
```
~/.claude/commands/sc/
├── pm.md                  # → Executable via /sc:pm
├── implement.md           # → Executable via /sc:implement
├── test.md                # → Executable via /sc:test
├── analyze.md             # → Executable via /sc:analyze
├── research.md            # → Executable via /sc:research
├── ... (26 commands total)
```

### Claude Code Behavior
```
User: /sc:pm "Build authentication"

Claude Code:
  1. Reads ~/.claude/commands/sc/pm.md
  2. Parses YAML frontmatter
  3. Expands Markdown body
  4. Executes as PM Agent
```

---

## Other Components

### Modes Component
```python
File: setup/components/modes.py
Source: superclaude/modes/*.md
Target: ~/.claude/*.md

Example:
  superclaude/modes/MODE_Brainstorming.md
    ↓
  ~/.claude/MODE_Brainstorming.md
```

### Agents Component
```python
File: setup/components/agents.py
Source: superclaude/agents/*.md
Target: ~/.claude/agents/*.md (or integration target)
```

### Core Component
```python
File: setup/components/core.py
Source: superclaude/core/CLAUDE.md
Target: ~/.claude/CLAUDE.md

This is the global configuration!
```

---

## Development Notes

### Correct Way to Make Changes
```bash
# 1. Modify source files (Git-managed)
cd ~/github/SuperClaude_Framework
vim superclaude/commands/pm.md

# 2. Add tests
Write tests/test_pm_command.py

# 3. Run tests
pytest tests/test_pm_command.py -v

# 4. Commit
git add superclaude/commands/pm.md tests/
git commit -m "feat: enhance PM command"

# 5. Development install
pip install -e .
# or
SuperClaude install --dev

# 6. Verify behavior
claude
/sc:pm "test"
```

### Incorrect Way to Make Changes
```bash
# Don't do this! Directly modifying files outside Git management
vim ~/.claude/commands/sc/pm.md

# Changes will be overwritten on next install
SuperClaude install  # ← Changes are lost!
```

---

## Correct Flow for PM Mode Improvement

### Phase 1: Understanding (we are here!)
```bash
✅ Understanding of setup/components/commands.py complete
✅ Verification of superclaude/commands/*.md existence complete
✅ Installation flow understanding complete
```

### Phase 2: Review Current Specification
```bash
# Review source (Git-managed)
Read superclaude/commands/pm.md

# Review post-install (for reference)
Read ~/.claude/commands/sc/pm.md

# "I see, so this is the current specification"
```

### Phase 3: Create Improvement Proposal
```bash
# Within this project (Git-managed)
Write docs/Development/hypothesis-pm-enhancement-2025-10-14.md

Content:
- Current problems (too documentation-oriented, insufficient PMO functionality)
- Improvement proposals (autonomous PDCA, self-evaluation)
- Implementation approach
- Expected outcomes
```

### Phase 4: Implementation
```bash
# Modify source files
Edit superclaude/commands/pm.md

Change examples:
- Strengthen automatic PDCA execution
- Make docs/ directory usage explicit
- Add self-evaluation steps
- Add error re-learning flow
```

### Phase 5: Testing and Verification
```bash
# Add tests
Write tests/test_pm_enhanced.py

# Run tests
pytest tests/test_pm_enhanced.py -v

# Development install
SuperClaude install --dev

# Try it out
claude
/sc:pm "test enhanced workflow"
```

### Phase 6: Learning Records
```bash
# Record success patterns
Write docs/patterns/pm-autonomous-workflow.md

# Record failures if any
Write docs/mistakes/mistake-2025-10-14.md
```

---

## Inter-Component Dependencies

```yaml
Commands Component:
  depends_on: ["core"]

Core Component:
  provides:
    - ~/.claude/CLAUDE.md (global configuration)
    - Basic directory structure

Modes Component:
  depends_on: ["core"]
  provides:
    - ~/.claude/MODE_*.md

Agents Component:
  depends_on: ["core"]
  provides:
    - Agent definitions

MCP Component:
  depends_on: ["core"]
  provides:
    - MCP server configuration
```

---

## Next Actions

Understanding complete! Next steps:

1. ✅ Review current specification of `superclaude/commands/pm.md`
2. ✅ Create improvement proposal document
3. ✅ Implementation modifications (strengthen PDCA, add PMO functionality)
4. ✅ Add and run tests
5. ✅ Verify behavior
6. ✅ Record learnings

This document itself serves as a **complete record of installation flow understanding**.
Reading it in the next session avoids repeating the same explanations.
