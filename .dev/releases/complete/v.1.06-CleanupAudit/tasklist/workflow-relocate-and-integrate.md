# Workflow: Relocate sc-cleanup-audit to /src + Framework Integration

**Generated**: 2026-02-19
**Objective**: Move all cleanup-audit files into `src/superclaude/` and ensure the command is installed by default via `superclaude install`
**Scope**: 2 objectives, 4 phases, 18 tasks
**Compliance**: STRICT (multi-file refactoring, installer modification, framework integration)

---

## Phase 1: Copy Source Files to `src/superclaude/` (5 tasks)

### T1.1 — Copy skill directory to `src/superclaude/skills/sc-cleanup-audit/`
**Tier**: STANDARD | **Confidence**: 0.95
**Action**: Copy entire `.claude/skills/sc-cleanup-audit/` directory tree to `src/superclaude/skills/sc-cleanup-audit/`
**Files**:
- `src/superclaude/skills/sc-cleanup-audit/SKILL.md`
- `src/superclaude/skills/sc-cleanup-audit/rules/pass1-surface-scan.md`
- `src/superclaude/skills/sc-cleanup-audit/rules/pass2-structural-audit.md`
- `src/superclaude/skills/sc-cleanup-audit/rules/pass3-cross-cutting.md`
- `src/superclaude/skills/sc-cleanup-audit/rules/verification-protocol.md`
- `src/superclaude/skills/sc-cleanup-audit/rules/dynamic-use-checklist.md`
- `src/superclaude/skills/sc-cleanup-audit/scripts/repo-inventory.sh`
- `src/superclaude/skills/sc-cleanup-audit/templates/batch-report.md`
- `src/superclaude/skills/sc-cleanup-audit/templates/pass-summary.md`
- `src/superclaude/skills/sc-cleanup-audit/templates/final-report.md`
- `src/superclaude/skills/sc-cleanup-audit/templates/finding-profile.md`
**Acceptance**: All 11 files present, identical content, `repo-inventory.sh` executable bit preserved
**Blocks**: T2.1, T2.2

### T1.2 — Create `__init__.py` for skill package
**Tier**: LIGHT | **Confidence**: 0.98
**Action**: Create `src/superclaude/skills/sc-cleanup-audit/__init__.py` (empty or minimal)
**Rationale**: Follow the pattern set by `confidence-check/` which has `__init__.py`
**Acceptance**: File exists, Python can import the package path without error

### T1.3 — Copy 5 agent definitions to `src/superclaude/agents/`
**Tier**: STANDARD | **Confidence**: 0.95
**Action**: Copy from `.claude/agents/` to `src/superclaude/agents/`:
- `audit-scanner.md`
- `audit-analyzer.md`
- `audit-comparator.md`
- `audit-consolidator.md`
- `audit-validator.md`
**Acceptance**: All 5 files present in `src/superclaude/agents/`, identical content
**Blocks**: T2.3

### T1.4 — Verify SKILL.md frontmatter `name` field
**Tier**: LIGHT | **Confidence**: 0.92
**Action**: Verify `name: cleanup-audit` in SKILL.md frontmatter is correct for skill installation. The `install_skill.py` uses the skill directory name for lookup, not the frontmatter name. Ensure directory name `sc-cleanup-audit` is what the installer expects.
**Acceptance**: `superclaude install-skill sc-cleanup-audit` would find the skill at `src/superclaude/skills/sc-cleanup-audit/`

### T1.5 — Validate no naming conflicts
**Tier**: LIGHT | **Confidence**: 0.90
**Action**: Verify no existing skill or agent has conflicting names. Check `src/superclaude/skills/` and `src/superclaude/agents/` for collisions.
**Acceptance**: No naming conflicts found

---

## Phase 2: Extend Installation Pipeline (6 tasks)

### T2.1 — Create `install_agents.py` module
**Tier**: STRICT | **Confidence**: 0.88
**Action**: Create `src/superclaude/cli/install_agents.py` following the pattern of `install_commands.py`:
- `install_agents(target_path, force)` → copies `.md` files from `src/superclaude/agents/` to `~/.claude/agents/`
- `_get_agents_source()` → resolves source directory (package vs source checkout)
- `list_available_agents()` → lists agent `.md` files
- `list_installed_agents()` → lists agents in `~/.claude/agents/`
**Pattern**: Mirror `install_commands.py` structure exactly — same error handling, same skip/force logic, same message formatting
**Acceptance**:
- [ ] Module imports successfully
- [ ] `install_agents()` copies all `.md` files from agents source to target
- [ ] `_get_agents_source()` finds `src/superclaude/agents/` in both installed and dev modes
- [ ] Excludes `README.md` and `__init__.py` from installation
**Blocks**: T2.3

### T2.2 — Create `install_skills.py` (batch skill installer)
**Tier**: STRICT | **Confidence**: 0.85
**Action**: Create `src/superclaude/cli/install_skills.py` (note: plural, distinct from existing `install_skill.py`):
- `install_all_skills(target_path, force)` → iterates `src/superclaude/skills/*/` and installs each
- Reuses `_is_valid_skill_dir()` and `_get_skill_source()` from `install_skill.py`
- OR: simply call `install_skill_command()` in a loop for each discovered skill
**Rationale**: Currently skills are installed one-by-one. Need batch installation for `superclaude install` to include all skills by default.
**Acceptance**:
- [ ] Module imports successfully
- [ ] `install_all_skills()` discovers and installs all valid skill directories
- [ ] Each skill installed to `~/.claude/skills/<skill-name>/`
**Blocks**: T2.3

### T2.3 — Add agent + skill steps to `superclaude install` command
**Tier**: STRICT | **Confidence**: 0.90
**Action**: Modify `src/superclaude/cli/main.py` `install()` function to add Steps 3 and 4:
```python
# Step 3: Install agents
click.echo("📦 Installing agents to ~/.claude/agents/...")
agent_success, agent_message = install_agents(force=force)
click.echo(agent_message)

# Step 4: Install skills
click.echo("📦 Installing skills to ~/.claude/skills/...")
skill_success, skill_message = install_all_skills(force=force)
click.echo(skill_message)
```
Also update `--list` mode to show agents and skills.
Also update `update()` command to include agents and skills.
**Acceptance**:
- [ ] `superclaude install` now has 4 steps: core → commands → agents → skills
- [ ] `superclaude install --list` shows agents and skills
- [ ] `superclaude update` updates all 4 components
- [ ] Exit code reflects all 4 steps

### T2.4 — Update `doctor.py` to check agents and skills
**Tier**: STANDARD | **Confidence**: 0.85
**Action**: Add health checks for agent and skill installation to `src/superclaude/cli/doctor.py`
**Acceptance**: `superclaude doctor` reports agent/skill status

### T2.5 — Update `__init__.py` exports
**Tier**: LIGHT | **Confidence**: 0.95
**Action**: Update `src/superclaude/cli/__init__.py` to document new modules
**Acceptance**: Clean imports, no circular dependencies

### T2.6 — Update `pyproject.toml` package data
**Tier**: STANDARD | **Confidence**: 0.88
**Action**: Ensure `pyproject.toml` includes `agents/*.md`, `skills/*/` in package data so they're distributed with the pip/pipx package.
**Acceptance**: `pip install .` includes all agent and skill files in the installed package

---

## Phase 3: Framework Integration — Repo-Level Files (4 tasks)

### T3.1 — Update `src/superclaude/core/COMMANDS.md`
**Tier**: STANDARD | **Confidence**: 0.95
**Action**: Add the `/sc:cleanup-audit` entry (matching what was added to `/config/.claude/COMMANDS.md`):
```markdown
**`/sc:cleanup-audit [target] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]`** — Multi-pass read-only repository audit (wave-enabled, complex profile)
- **Auto-Persona**: Analyzer, Architect, DevOps, QA, Refactorer
- **MCP**: Sequential (cross-cutting synthesis), Serena (import chains), Context7 (framework patterns)
- **Tools**: [Read, Grep, Glob, Bash(git/wc/find/du), TodoWrite, Task, Write]
- **Subagents**: audit-scanner (Haiku), audit-analyzer (Sonnet), audit-comparator (Sonnet), audit-consolidator (Sonnet), audit-validator (Sonnet)
```
**Acceptance**: Entry present in COMMANDS.md under Quality Commands section

### T3.2 — Update `src/superclaude/core/ORCHESTRATOR.md`
**Tier**: STANDARD | **Confidence**: 0.95
**Action**: Add 3 routing patterns to Master Routing Table:
```
| "cleanup audit" | complex | quality | analyzer persona, --wave-mode --systematic-waves, Sequential + Serena | 95% |
| "repository audit" | complex | quality | analyzer persona, --delegate --multi-agent, 5 custom subagents | 95% |
| "dead code detection" | complex | quality | analyzer persona, --think-hard, Sequential | 90% |
```
**Acceptance**: 3 rows added to Master Routing Table

### T3.3 — Update `src/superclaude/core/PERSONAS.md`
**Tier**: STANDARD | **Confidence**: 0.95
**Action**: Update analyzer persona:
- Add `/cleanup-audit` to Commands list
- Add audit triggers: `"audit"`, `"dead code"`, `"cleanup audit"`, `"repository audit"`
**Acceptance**: Analyzer persona references cleanup-audit

### T3.4 — Sync user-level config with repo-level
**Tier**: LIGHT | **Confidence**: 0.90
**Action**: Verify `/config/.claude/COMMANDS.md`, `ORCHESTRATOR.md`, `PERSONAS.md` match `src/superclaude/core/` versions for cleanup-audit entries. If they already match (from Phase 1 of the original implementation), no changes needed.
**Acceptance**: User-level and repo-level framework files are in sync for cleanup-audit references

---

## Phase 4: Validation & Cleanup (3 tasks)

### T4.1 — End-to-end installation test
**Tier**: STRICT | **Confidence**: 0.85
**Action**: Verify the full installation pipeline works:
1. `superclaude install --list` shows cleanup-audit skill and 5 audit agents
2. `superclaude install --force` installs all components
3. Verify `~/.claude/agents/audit-*.md` files exist (5 files)
4. Verify `~/.claude/skills/sc-cleanup-audit/` directory exists with all 11 files
5. `superclaude doctor` passes all checks
**Acceptance**: All 5 verification steps pass

### T4.2 — Remove redundant `.claude/` copies
**Tier**: STANDARD | **Confidence**: 0.80
**Action**: After confirming `src/superclaude/` is the source of truth:
- `.claude/skills/sc-cleanup-audit/` can remain (repo-local config for dev mode)
- `.claude/agents/audit-*.md` can remain (repo-local config for dev mode)
- But ensure `.gitignore` or documentation clarifies which is source of truth
**Note**: This is a cleanup decision — may want to keep `.claude/` copies for local dev convenience since Claude Code reads them directly from the repo. Document the dual-location pattern.
**Acceptance**: Documentation clearly states `src/superclaude/` is source of truth, `.claude/` is dev convenience

### T4.3 — Update CLAUDE.md project documentation
**Tier**: LIGHT | **Confidence**: 0.95
**Action**: Update project `CLAUDE.md` to document:
- New `superclaude install` behavior (4 steps instead of 2)
- Agent installation path
- Skill auto-installation
- The `sc:cleanup-audit` command availability
**Acceptance**: CLAUDE.md reflects current installation pipeline

---

## Dependency Graph

```
T1.1 ──┐
T1.2 ──┤
T1.3 ──┼──→ T2.1 ──┐
T1.4 ──┤    T2.2 ──┼──→ T2.3 ──→ T2.6 ──→ T4.1 ──→ T4.2
T1.5 ──┘    T2.4 ──┘                        T4.3
            T2.5
            T3.1 (independent)
            T3.2 (independent)
            T3.3 (independent)
            T3.4 (depends on T3.1-T3.3)
```

## Execution Order

1. **Wave 1** (parallel): T1.1, T1.2, T1.3, T1.4, T1.5
2. **Wave 2** (parallel): T2.1, T2.2, T2.4, T2.5, T3.1, T3.2, T3.3
3. **Wave 3** (sequential): T2.3 (depends on T2.1 + T2.2)
4. **Wave 4** (parallel): T2.6, T3.4
5. **Wave 5** (sequential): T4.1 → T4.2, T4.3

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `pyproject.toml` package data misconfiguration | Medium | High | Test with `pip install -e .` and verify file inclusion |
| `_get_agents_source()` path resolution in installed vs dev | Low | High | Follow exact pattern from `_get_commands_source()` |
| `.claude/` vs `src/` dual copies diverging | Medium | Medium | Document source of truth, consider symlinks or build step |
| `install_all_skills()` breaking existing `install-skill` command | Low | Medium | Keep both commands, plural wraps singular |
