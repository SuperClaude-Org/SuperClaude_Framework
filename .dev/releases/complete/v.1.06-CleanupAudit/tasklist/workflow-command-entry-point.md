# Workflow: Command Entry Point + Orphan Rescue + Sync Extension

**Generated**: 2026-02-19
**Objective**: Add `/sc:cleanup-audit` command entry point, rescue 3 orphaned commands into `src/`, extend sync mechanism to cover commands, update documentation
**Root Cause**: Spec framed "skill vs command" when platform requires both; 3 other commands also exist only in `~/.claude/commands/sc/` without source copies
**Scope**: 16 tasks, 5 phases
**Compliance**: STRICT

---

## Context

### Architecture
Claude Code has TWO systems that must both be present for `/sc:cleanup-audit` to work:
1. **Command** (`commands/sc/cleanup-audit.md`): Entry point registered as `/sc:cleanup-audit` slash command. Loaded as prompt on invocation.
2. **Skill** (`skills/sc-cleanup-audit/SKILL.md`): Orchestration engine with supporting files (rules/, templates/, scripts/). Loaded via skill system for deep behavioral context.

### Design Pattern: "validate-tests" (thin command + rich skill)
- Command `.md` = concise entry point (~70 lines): frontmatter, shell preprocessing, usage, behavioral summary, examples, boundaries
- SKILL.md = full orchestration spec: 5-step flow, MCP integration, tool coordination, key patterns, plus rules/templates/scripts
- The command triggers the skill. NO duplication of detailed behavioral content.

### Anti-Pattern: "task-unified" (fat command duplicating skill)
- 567-line command `.md` that duplicates SKILL.md content → maintenance drift guaranteed

### Command Frontmatter Convention (from existing commands)
```yaml
---
name: <command-name>           # No sc- prefix
description: "<verb phrase>"   # Quoted
category: <utility|workflow|special|reference>
complexity: <basic|standard|enhanced|advanced|high>
mcp-servers: [<servers>]       # Array
personas: [<personas>]         # Array
---
```
**NOT used in commands** (skill-only fields): `disable-model-invocation`, `allowed-tools`, `argument-hint`

### Orphaned Commands (same class of bug)
| Command | `~/.claude/commands/sc/` | `src/superclaude/commands/` | Lines |
|---------|--------------------------|------------------------------|-------|
| task-unified.md | EXISTS | MISSING | 567 |
| task-mcp.md | EXISTS | MISSING | 375 |
| validate-tests.md | EXISTS | MISSING | 102 |
| cleanup-audit.md | MISSING | MISSING | N/A |

### Sync Mechanism Gap
`make verify-sync` currently checks skills and agents only. Commands are not verified.
`make sync-dev` currently syncs skills and agents only. Commands are not synced.

---

## Phase 1: Create Command Entry Point (P0)

### T1 — Create `cleanup-audit.md` in `src/superclaude/commands/`

**Action**: Create the command entry point file following the validate-tests pattern (thin command, ~70 lines)

**Content Structure** (in this exact order):
1. **Frontmatter** (YAML):
   ```yaml
   ---
   name: cleanup-audit
   description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
   category: utility
   complexity: high
   mcp-servers: [sequential, serena, context7]
   personas: [analyzer, architect, devops, qa, refactorer]
   ---
   ```
   - `name`: `cleanup-audit` (no `sc-` prefix — matches `cleanup`, `analyze`, `spawn`)
   - `category`: `utility` (matches existing SKILL.md)
   - `complexity`: `high` (matches existing SKILL.md)
   - NO `disable-model-invocation`, NO `allowed-tools`, NO `argument-hint` — those are skill-only

2. **Title**: `# /sc:cleanup-audit - Multi-Pass Repository Audit`

3. **Shell Preprocessing Context** (copy from SKILL.md lines 29-38):
   ```markdown
   ## Repository Context
   - Total files: !`git ls-files | wc -l`
   - File breakdown: !`git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15`
   - Repo size: !`du -sh . --exclude=.git --exclude=node_modules 2>/dev/null`
   - Current branch: !`git branch --show-current`
   - Last commit: !`git log --oneline -1`

   ## Target Scope
   - Target: $ARGUMENTS
   - Files in scope: !`find ${0:-.} -type f -not -path '*/.git/*' -not -path '*/node_modules/*' | wc -l`
   ```

4. **Usage block** (copy from SKILL.md lines 18-26):
   ```markdown
   ## Usage
   /sc:cleanup-audit [target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]
   ```
   Include the Arguments subsection with the 4 bullet points.

5. **Behavioral Summary** — ONE concise paragraph, NOT the full 5-step flow:
   ```markdown
   ## Behavioral Summary
   Spawns parallel subagents in 3 escalating passes: Pass 1 (Haiku surface scan → DELETE/REVIEW/KEEP), Pass 2 (Sonnet structural audit → 8-field per-file profiles), Pass 3 (Sonnet cross-cutting comparison → duplication matrix). Each pass uses evidence-gated classification with grep proof. Quality validated via spot-check sampling. Reports written to `.claude-audit/`.
   ```

6. **Examples** — Copy the 4 examples from SKILL.md (lines 75-104)

7. **Boundaries + Critical Boundaries** — Copy from SKILL.md (lines 101-134)

**What to EXCLUDE** (lives in SKILL.md only):
- Full "Behavioral Flow" 5-step section with "Key behaviors" bullets
- "MCP Integration" section
- "Tool Coordination" section
- "Key Patterns" section

**Acceptance Criteria**:
- [ ] File exists at `src/superclaude/commands/cleanup-audit.md`
- [ ] Frontmatter has exactly 6 fields matching command convention (name, description, category, complexity, mcp-servers, personas)
- [ ] NO skill-only fields (disable-model-invocation, allowed-tools, argument-hint)
- [ ] Shell preprocessing uses `!`cmd`` syntax
- [ ] $ARGUMENTS reference present
- [ ] Behavioral summary is ONE paragraph, not duplicated 5-step flow
- [ ] 4 examples present
- [ ] Boundaries + Critical Boundaries present with READ-ONLY directive
- [ ] Total file length: 60-80 lines
- [ ] Next Step reference present

---

### T2 — QA Review: Command Conventions Compliance

**Action**: Verify the new command file against 3 reference commands

**Steps**:
1. Compare frontmatter fields against `cleanup.md`, `analyze.md`, `spawn.md` — must have exactly the same field set (name, description, category, complexity, mcp-servers, personas)
2. Verify H1 title follows pattern: `# /sc:<name> - <Short Title>`
3. Verify no content from SKILL.md's "MCP Integration", "Tool Coordination", or "Key Patterns" sections leaked into the command
4. Verify the behavioral summary is genuinely concise (1 paragraph, not a reformatted 5-step flow)
5. Verify examples use `/sc:cleanup-audit` not `/cleanup-audit`
6. Grep the command for `disable-model-invocation` — must return zero matches
7. Grep the command for `allowed-tools` — must return zero matches

**Acceptance Criteria**:
- [ ] All 7 checks pass
- [ ] No convention violations found

---

### T3 — Sync command to project-local `.claude/commands/sc/`

**Action**: Copy the new command to the project-local `.claude/commands/sc/` directory for immediate availability

**Steps**:
1. Create `.claude/commands/sc/` directory if it doesn't exist
2. Copy `src/superclaude/commands/cleanup-audit.md` → `.claude/commands/sc/cleanup-audit.md`
3. Verify the file exists and content matches

**Acceptance Criteria**:
- [ ] `.claude/commands/sc/cleanup-audit.md` exists in the project
- [ ] Content is identical to `src/superclaude/commands/cleanup-audit.md`

---

## Phase 2: Rescue Orphaned Commands (P1)

### T4 — Copy `task-unified.md` to `src/superclaude/commands/`

**Action**: Copy the orphaned command from `~/.claude/commands/sc/task-unified.md` to `src/superclaude/commands/task-unified.md`

**Steps**:
1. Read `~/.claude/commands/sc/task-unified.md`
2. Verify it has valid command frontmatter (name, description, category, complexity, mcp-servers, personas)
3. Copy to `src/superclaude/commands/task-unified.md`
4. Verify the copy exists and content matches

**Acceptance Criteria**:
- [ ] File exists at `src/superclaude/commands/task-unified.md`
- [ ] Content matches `~/.claude/commands/sc/task-unified.md`
- [ ] Frontmatter is valid command format

---

### T5 — Copy `task-mcp.md` to `src/superclaude/commands/`

**Action**: Same as T4 but for `task-mcp.md`

**Steps**:
1. Read `~/.claude/commands/sc/task-mcp.md`
2. Verify valid command frontmatter
3. Copy to `src/superclaude/commands/task-mcp.md`
4. Verify the copy

**Acceptance Criteria**:
- [ ] File exists at `src/superclaude/commands/task-mcp.md`
- [ ] Content matches source
- [ ] Frontmatter is valid

---

### T6 — Copy `validate-tests.md` to `src/superclaude/commands/`

**Action**: Same as T4 but for `validate-tests.md`

**Steps**:
1. Read `~/.claude/commands/sc/validate-tests.md`
2. Verify valid command frontmatter
3. Copy to `src/superclaude/commands/validate-tests.md`
4. Verify the copy

**Acceptance Criteria**:
- [ ] File exists at `src/superclaude/commands/validate-tests.md`
- [ ] Content matches source
- [ ] Frontmatter is valid

---

### T7 — QA Review: Orphaned Commands Audit

**Action**: Verify all 3 rescued commands have consistent frontmatter and no stale content

**Steps**:
1. For each of {task-unified.md, task-mcp.md, validate-tests.md}:
   a. Verify frontmatter has the 6 standard fields
   b. Verify H1 title follows `/sc:<name>` pattern
   c. Check for any hardcoded paths that reference `~/.claude/` (should be relative)
2. Run `ls src/superclaude/commands/*.md | wc -l` — should now be 35 (was 32 + cleanup-audit + 3 orphans)
3. Cross-reference against `~/.claude/commands/sc/` to identify any OTHER orphans we might have missed

**Acceptance Criteria**:
- [ ] All 3 files pass frontmatter validation
- [ ] No hardcoded absolute paths
- [ ] Total command count in src/ matches expected (35)
- [ ] No additional orphans discovered (or documented if found)

---

## Phase 3: Extend Sync Mechanism (P1)

### T8 — Add commands section to `make verify-sync`

**Action**: Extend the `verify-sync` Makefile target to also check commands between `src/superclaude/commands/` and `~/.claude/commands/sc/`

**Implementation Details**:
- Add a third section `=== Commands ===` after the existing Skills and Agents sections
- Compare `src/superclaude/commands/*.md` against `~/.claude/commands/sc/*.md`
- Exclude `README.md` and `__init__.py` (same as agents)
- For each `.md` in `src/superclaude/commands/`: check if same-named file exists in `~/.claude/commands/sc/`
- For each `.md` in `~/.claude/commands/sc/`: check if same-named file exists in `src/superclaude/commands/` (orphan detection)
- Report MISSING, DIFFERS, or ✅ for each
- Set `drift=1` on any mismatch

**Important difference from skills/agents**: Commands compare against GLOBAL `~/.claude/commands/sc/`, not project-local `.claude/commands/sc/`. This is because commands are installed globally.

**Acceptance Criteria**:
- [ ] `make verify-sync` now shows a `=== Commands ===` section
- [ ] Files in `src/` not in `~/.claude/commands/sc/` are flagged as MISSING
- [ ] Files in `~/.claude/commands/sc/` not in `src/` are flagged as orphans
- [ ] Content differences are reported
- [ ] Exit code 1 on any drift

---

### T9 — Add commands to `make sync-dev`

**Action**: Extend `sync-dev` to also copy commands from `src/superclaude/commands/` to `.claude/commands/sc/` (project-local)

**Implementation Details**:
- Add a third section after skills and agents
- Create `.claude/commands/sc/` directory if it doesn't exist
- Copy all `*.md` files from `src/superclaude/commands/` to `.claude/commands/sc/`
- Exclude `__init__.py` and `README.md`
- Update the summary line at the end to include command count

**Acceptance Criteria**:
- [ ] `make sync-dev` creates `.claude/commands/sc/` and populates it
- [ ] All `.md` files from `src/superclaude/commands/` appear in `.claude/commands/sc/`
- [ ] Summary output shows command count

---

### T10 — Test sync mechanism end-to-end

**Action**: Verify both sync targets work correctly

**Steps**:
1. Run `make sync-dev` — should complete without error, show command count
2. Run `make verify-sync` — should show all green (Skills ✅, Agents ✅, Commands ✅)
3. Introduce deliberate drift: add a temporary line to `.claude/commands/sc/cleanup-audit.md`
4. Run `make verify-sync` — should FAIL with DIFFERS on cleanup-audit.md
5. Revert the change
6. Run `make verify-sync` — should pass again

**Acceptance Criteria**:
- [ ] sync-dev completes with command count in output
- [ ] verify-sync shows Commands section with all green
- [ ] Deliberate drift is caught by verify-sync
- [ ] Revert restores green state

---

## Phase 4: Documentation (P2)

### T11 — Update `custom-command-guide.md` with Command + Skill Hybrid pattern

**Action**: Add a fourth pattern to Section 1 of the custom command guide

**File**: `.dev/.releases/current/v.1.06-CleanupAudit/research/custom-command-guide.md`

**Content to add** after "Recommended: Hybrid Approach" (line 27-37):

```markdown
### Command + Skill Hybrid (for slash-command registration)
When using a Skill for supporting files, you MUST ALSO create a Command `.md`
entry point in `src/superclaude/commands/`. The skill provides the orchestration
engine; the command provides the `/sc:name` registration.

```
src/superclaude/commands/<name>.md    # Entry point (thin, ~70 lines)
src/superclaude/skills/sc-<name>/     # Orchestration engine (full spec)
├── SKILL.md
├── rules/
├── templates/
└── scripts/
src/superclaude/agents/<worker>.md    # Worker agents (if needed)
```

**Pattern**: Command = concise (frontmatter + usage + summary + examples + boundaries).
Skill = comprehensive (full behavioral flow + MCP + tools + patterns + supporting files).
Do NOT duplicate detailed behavioral content in both.
```

**Acceptance Criteria**:
- [ ] Section added to custom-command-guide.md
- [ ] Clearly states MUST create both command and skill
- [ ] Shows file tree with both components
- [ ] States the DRY principle (no duplication between command and skill)

---

## Phase 5: Install, Verify, Validate (P0)

### T12 — Reinstall via pipx

**Action**: `pipx install . --force` from the SuperClaude_Framework repo root

**Acceptance Criteria**:
- [ ] pipx install completes without error
- [ ] `superclaude --version` returns 4.2.0

---

### T13 — Run `superclaude install --force`

**Action**: Reinstall all components to global `~/.claude/`

**Verification**:
1. Output shows "Installed N commands" — count should include `cleanup-audit`
2. Output shows "Installed 5 skills" — includes `sc-cleanup-audit`
3. Output shows "Installed 25 agents"
4. Run `superclaude install --list` — verify `cleanup-audit` appears in commands list

**Acceptance Criteria**:
- [ ] All 4 install steps succeed (core, commands, agents, skills)
- [ ] `cleanup-audit` appears in commands list
- [ ] `sc-cleanup-audit` appears in skills list
- [ ] Command count increased by 4 (cleanup-audit + 3 rescued orphans)

---

### T14 — Verify `/sc:cleanup-audit` appears as available command

**Action**: Check that the slash command is registered by Claude Code

**Steps**:
1. Verify `~/.claude/commands/sc/cleanup-audit.md` exists
2. Verify the content matches `src/superclaude/commands/cleanup-audit.md`
3. Check that the skill `sc-cleanup-audit` still appears in the available skills list (frontmatter restoration in Phase 0 should not have broken this)

**Acceptance Criteria**:
- [ ] Command file installed at correct global path
- [ ] Skill still visible in skills list
- [ ] Both command AND skill coexist without conflict

---

### T15 — Run `make verify-sync` — full green

**Action**: Final sync verification across all three component types

**Expected Output**:
```
=== Skills ===
  ✅ confidence-check
  ✅ sc-cleanup-audit
  ✅ sc:roadmap
  ✅ sc-task-unified
  ✅ sc-validate-tests

=== Agents ===
  ✅ (25 agents all green)

=== Commands ===
  ✅ (35 commands all green)

✅ All components in sync.
```

**Acceptance Criteria**:
- [ ] Exit code 0
- [ ] All three sections show all green
- [ ] No MISSING or DIFFERS entries

---

### T16 — Final Validation Checklist

**Action**: Run through the complete validation matrix

| Check | Method | Expected |
|-------|--------|----------|
| Command file exists in src/ | `ls src/superclaude/commands/cleanup-audit.md` | Exists, ~70 lines |
| Command file exists in ~/.claude/ | `ls ~/.claude/commands/sc/cleanup-audit.md` | Exists, matches src/ |
| Skill SKILL.md exists in src/ | `ls src/superclaude/skills/sc-cleanup-audit/SKILL.md` | Exists, has full frontmatter |
| Skill SKILL.md exists in .claude/ | `ls .claude/skills/sc-cleanup-audit/SKILL.md` | Exists, matches src/ |
| Skill visible in skills list | Check system-reminder output | `sc-cleanup-audit` listed |
| No field duplication | grep `allowed-tools` command file | Zero matches |
| No field duplication | grep `disable-model-invocation` command file | Zero matches |
| Orphans rescued | `ls src/superclaude/commands/{task-unified,task-mcp,validate-tests}.md` | All 3 exist |
| Sync clean | `make verify-sync` | Exit 0, all green |
| Install clean | `superclaude install --list` | All components listed |

**Acceptance Criteria**:
- [ ] All 10 checks pass
- [ ] No regressions in existing functionality

---

## Dependency Graph

```
Phase 1 (Command Entry Point)
├── T1: Create cleanup-audit.md ─── T2: QA Review ─── T3: Sync to .claude/
│
Phase 2 (Rescue Orphans) — can start parallel with Phase 1
├── T4: Copy task-unified.md ─┐
├── T5: Copy task-mcp.md      ├── T7: QA Review orphans
└── T6: Copy validate-tests.md┘
│
Phase 3 (Sync Mechanism) — depends on Phase 1 + Phase 2
├── T8: Extend verify-sync ─┐
├── T9: Extend sync-dev     ├── T10: Test sync
└────────────────────────────┘
│
Phase 4 (Documentation) — can run parallel with Phase 3
└── T11: Update custom-command-guide.md
│
Phase 5 (Install & Validate) — depends on ALL above
├── T12: pipx install
├── T13: superclaude install ─── T14: Verify command + skill coexist
├── T15: make verify-sync
└── T16: Final validation checklist
```

**Parallelization**: Phase 1 ∥ Phase 2, Phase 3 ∥ Phase 4, Phase 5 sequential after all others.
