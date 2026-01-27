# Execution Instructions: v1.0-mcp-installer - JSON-Based MCP Installation

## Context Loading (READ THESE FIRST)

1. **Source specification**: `/config/workspace/SuperClaude/docs/specs/MCP-INSTALLER-SPEC.md`
2. **This roadmap**: `/config/workspace/SuperClaude/.roadmaps/v1.0-mcp-installer/roadmap.md`
3. **Test strategy**: `/config/workspace/SuperClaude/.roadmaps/v1.0-mcp-installer/test-strategy.md`
4. **Extraction**: `/config/workspace/SuperClaude/.roadmaps/v1.0-mcp-installer/extraction.md`

### Codebase Overview

| Directory | Purpose |
|-----------|---------|
| `src/superclaude/mcp/` | New module for JSON-based MCP config (to be created) |
| `src/superclaude/cli/install_mcp.py` | Existing CLI installer (to be refactored) |
| `tests/mcp/` | Test suite for MCP functionality (to be created) |
| `docs/specs/MCP-INSTALLER-SPEC.md` | Authoritative specification |

### Key Files to Create

```
src/superclaude/mcp/
├── __init__.py          # Module exports
├── config.py            # Core config operations (load, save, atomic)
├── servers.py           # Server registration logic
├── schema.py            # JSON schema validation
├── exceptions.py        # Error codes E001-E008
└── health.py            # SSE health checks
```

---

## Execution Rules

1. **Work through milestones IN ORDER** (M1 → M2 → M3 → M4 → M5 → M6)
2. **Within milestones, respect dependency order** (see roadmap.md Dependency Graph)
3. **Complete ALL deliverables** before the milestone checkpoint
4. **Run verification checkpoint** before proceeding to next milestone
5. **If verification fails** → STOP and create an issue report

---

## Task Execution Pattern (for each deliverable)

### 1. READ
- Read acceptance criteria from roadmap.md
- Read related specifications from MCP-INSTALLER-SPEC.md
- Identify affected files

### 2. PLAN
- List specific file changes needed
- Identify imports and dependencies
- Check for conflicts with existing code

### 3. IMPLEMENT
- Make changes clearly (avoid unrelated refactors)
- Follow existing code style (see CLAUDE.md)
- Use type hints for all public functions
- Add docstrings with examples

### 4. TEST
- Write tests per test-strategy.md BEFORE or alongside implementation
- Use pytest fixtures from `tests/fixtures/mcp/`
- Run and verify all tests pass:
  ```bash
  uv run pytest tests/mcp/unit/ -v -k "<deliverable_id>"
  ```

### 5. VERIFY
- Check acceptance criteria explicitly
- Cross-reference with specification
- Verify no regressions:
  ```bash
  uv run pytest tests/mcp/ -v
  ```

### 6. DOCUMENT
- Update docstrings if behavior changed
- Add inline comments for complex logic
- Update CHANGELOG.md if user-facing

### 7. COMMIT (if applicable)
- Logical commit referencing the deliverable ID
- Format: `feat(mcp): implement <description> [REQ-XXX]`

---

## Milestone Execution Guide

### Milestone 1: Foundation

**Start with these files:**

1. Create `src/superclaude/mcp/__init__.py`:
   ```python
   """MCP Server Configuration Module for SuperClaude."""
   from .config import (
       get_config_file_path,
       load_config,
       save_config,
       check_server_installed,
   )
   from .exceptions import MCPConfigError

   __all__ = [
       "get_config_file_path",
       "load_config",
       "save_config",
       "check_server_installed",
       "MCPConfigError",
   ]
   ```

2. Create `src/superclaude/mcp/config.py` with:
   - `get_config_file_path()` → REQ-001, REQ-014
   - `load_config()` → REQ-015
   - `_ensure_directory()` → REQ-002, IMP-006
   - `check_server_installed()` → REQ-012

3. Create `src/superclaude/mcp/exceptions.py` with:
   - `MCPConfigError(code, message)` base class

4. Create test fixtures in `tests/fixtures/mcp/`

5. Create unit tests in `tests/mcp/unit/test_config.py`

**Verification Checkpoint M1:**
```bash
# All M1 tests must pass
uv run pytest tests/mcp/unit/test_config.py -v

# Verify cross-platform (mock-based)
uv run pytest tests/mcp/unit/test_config.py -v -k "path"
```

---

### Milestone 2: Core Config Operations

**Extend `src/superclaude/mcp/config.py`:**

1. Add `save_config()` with atomic write → REQ-004, REQ-016
2. Add `_atomic_write()` helper with temp file pattern
3. Add `_acquire_lock()` / `_release_lock()` → IMP-004
4. Implement preservation logic → REQ-003

**Key Implementation Pattern (atomic write):**
```python
import tempfile
import os

def save_config(config: dict) -> None:
    config_path = get_config_file_path()
    _ensure_directory(config_path.parent)

    # Write to temp file first
    fd, temp_path = tempfile.mkstemp(
        dir=config_path.parent,
        prefix=".mcp_",
        suffix=".tmp"
    )
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(config, f, indent=2)
        # Atomic rename
        os.replace(temp_path, config_path)
        # Set permissions
        os.chmod(config_path, 0o600)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
```

**Verification Checkpoint M2:**
```bash
uv run pytest tests/mcp/unit/test_config.py -v -k "save or atomic or lock"
uv run pytest tests/mcp/integration/test_concurrent_access.py -v
```

---

### Milestone 3: Server Installation

**Create `src/superclaude/mcp/servers.py`:**

1. `register_server(name, config, overwrite=False)` → REQ-017
2. `_build_npm_config(command)` → REQ-005
3. `_build_uvx_config(command)` → REQ-006
4. `_build_sse_config(url)` → REQ-007
5. `_mask_api_key(key)` → IMP-005

**Refactor `src/superclaude/cli/install_mcp.py`:**
- Remove all `claude mcp add` subprocess calls → REF-001
- Import and use `register_server()` from mcp module
- Keep CLI interface, change implementation

**Verification Checkpoint M3:**
```bash
# No CLI calls in codebase
grep -r "claude mcp add" src/ --include="*.py" && echo "FAIL: CLI calls found" || echo "PASS: No CLI calls"

# All server type tests
uv run pytest tests/mcp/unit/test_servers.py -v
uv run pytest tests/mcp/acceptance/ -v
uv run pytest tests/mcp/regression/test_no_cli_calls.py -v
```

---

### Milestone 4: Server Management

**Extend modules:**

1. Add `unregister_server()` to config.py → REQ-010, REQ-011, REQ-018
2. Create `src/superclaude/mcp/health.py` → REQ-013
3. Unify interface in servers.py → REF-002

**Verification Checkpoint M4:**
```bash
uv run pytest tests/mcp/ -v -k "uninstall or unregister or health"
```

---

### Milestone 5: Public API & Quality

**Finalize:**

1. Create `src/superclaude/mcp/schema.py` → REQ-020
2. Complete error codes in exceptions.py → REQ-021
3. Performance validation → IMP-001

**Verification Checkpoint M5:**
```bash
uv run pytest tests/mcp/ -v --cov=src/superclaude/mcp --cov-report=term-missing

# Coverage must be >80%
```

---

### Milestone 6: Documentation & Polish

**Create documentation:**

1. `docs/reference/mcp-api.md` → DOC-001
2. `docs/user-guide/mcp-migration.md` → DOC-002
3. `docs/troubleshooting/mcp-installation.md` → DOC-003

**Update existing docs:**
- README.md: Update installation section
- CHANGELOG.md: Add v1.0-mcp-installer section

**Verification Checkpoint M6:**
```bash
# Documentation exists
ls docs/reference/mcp-api.md docs/user-guide/mcp-migration.md docs/troubleshooting/mcp-installation.md

# Full test suite
uv run pytest tests/mcp/ -v
```

---

## Verification Checkpoints (After Each Milestone)

- [ ] All deliverables code-complete
- [ ] All tests passing (unit + integration)
- [ ] No linting/type errors:
  ```bash
  uv run ruff check src/superclaude/mcp/
  ```
- [ ] Documentation current
- [ ] CHANGELOG updated if user-facing changes

---

## Stop Conditions

**HALT execution and report if:**

1. **Any test fails** after a reasonable fix attempt (2 tries)
2. **Unexpected dependency discovered** not in roadmap
3. **Security concern identified** (e.g., API key exposure risk)
4. **Scope creep detected** (work not in roadmap)
5. **Platform compatibility issue** that requires design change

---

## Issue Reporting Template

If you must stop, create an issue report:

```markdown
# Issue Report: [DELIVERABLE_ID]

## Summary
[One line description]

## Current State
- Milestone: M[X]
- Deliverable: [ID]
- Tests passing: [X/Y]

## Issue Details
[What went wrong]

## Root Cause Analysis
[Why it happened]

## Proposed Resolution
[How to fix]

## Impact
- Blocked deliverables: [IDs]
- Estimated delay: [time]
```

Save to: `.roadmaps/v1.0-mcp-installer/issues/ISSUE-XXX.md`

---

## Rollback Procedure

If critical issue discovered:

1. **Document issue** in `.roadmaps/v1.0-mcp-installer/issues/`
2. **Identify last known-good state**:
   ```bash
   git log --oneline -10
   ```
3. **Create rollback branch**:
   ```bash
   git checkout -b rollback/mcp-installer
   ```
4. **Report to human** with:
   - Issue summary
   - Affected milestones
   - Recommended action

---

## Success Criteria

Release is complete when:

- [ ] All 6 milestones verified
- [ ] All 32 deliverables implemented
- [ ] Test coverage >80%
- [ ] No regressions in existing functionality
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Ready for PR review

---

## Quick Reference

| Milestone | Key Deliverables | Critical Tests |
|-----------|------------------|----------------|
| M1 | REQ-001, REQ-002, REQ-014, REQ-015 | test_config.py |
| M2 | REQ-004, IMP-003, IMP-004 | test_concurrent_access.py |
| M3 | REQ-005-008, REF-001 | test_no_cli_calls.py |
| M4 | REQ-010, REQ-011, REQ-013 | test_uninstall.py |
| M5 | REQ-020, REQ-021 | test_schema.py, test_exceptions.py |
| M6 | DOC-001, DOC-002, DOC-003 | Documentation review |
