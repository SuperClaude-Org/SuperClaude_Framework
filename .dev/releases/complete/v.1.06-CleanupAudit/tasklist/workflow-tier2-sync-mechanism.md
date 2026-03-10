# Workflow: Tier 2 — Component Sync Mechanism

**Generated**: 2026-02-19
**Objective**: Add Makefile targets to prevent src/ vs .claude/ drift for skills and agents
**Scope**: 5 tasks, 1 phase
**Compliance**: STANDARD

---

## Tasks

### T1 — Add `sync-dev` target to Makefile
**Action**: Add a Makefile target that copies skills and agents from `src/superclaude/` → `.claude/`
**Logic**:
- For skills: `rsync -a --exclude='__init__.py' --exclude='__pycache__' src/superclaude/skills/ .claude/skills/` (but only dirs containing SKILL.md)
- For agents: copy `*.md` files excluding README.md from `src/superclaude/agents/` → `.claude/agents/`
- Create target dirs if missing
**Acceptance**: `make sync-dev` runs without error and populates .claude/ from src/

### T2 — Add `verify-sync` target to Makefile
**Action**: Add a Makefile target that checks bidirectional sync state
**Logic**:
- Compare skills: find dirs in each location, report missing, diff matching contents
- Compare agents: find .md files in each location, report missing, diff matching
- Exclude __init__.py, __pycache__, README.md from comparison
- Print clear report, exit 1 on any drift
**Acceptance**: `make verify-sync` exits 0 when in sync, exits 1 with clear report when drifted

### T3 — Update help target and .PHONY
**Action**: Add sync-dev and verify-sync to .PHONY list and help output
**Acceptance**: `make help` shows the new targets

### T4 — Update CLAUDE.md with sync documentation
**Action**: Add a "Component Sync" section to CLAUDE.md explaining:
- src/superclaude/ is source of truth for distribution
- .claude/{skills,agents} are dev copies read by Claude Code
- `make sync-dev` to propagate changes
- `make verify-sync` to check for drift
**Acceptance**: Documentation is clear and actionable

### T5 — Test and verify
**Action**:
1. Run `make verify-sync` — should pass (currently in sync from Tier 1)
2. Add a temp line to `.claude/skills/sc-cleanup-audit/SKILL.md` — verify-sync should FAIL
3. Revert the change — verify-sync should pass again
4. Run `make sync-dev` — verify agents fully populated in .claude/
**Acceptance**: All 4 checks pass
