# Adversarial Defense: sc:task vs sc:task-unified Analysis Reports

**Date**: 2026-02-22
**Role**: Adversarial Defender
**Branch**: feature/v2.0-Roadmap-v2
**Reports Defended**:
1. `task-vs-task-unified-framework.md`
2. `task-vs-task-unified-crossrefs.md`
3. `task-vs-task-unified-trigger-risks.md`
4. `task-vs-task-unified-risk-assessment.md`

---

## Defense Summary

All four reports converge on three claims: (1) the duplicate `name: task` frontmatter is a HIGH-risk defect, (2) `task-unified.md` was designed to replace `task.md` as an incomplete migration, and (3) the fix is to replace `task.md` with `task-unified.md`. After independent verification of the source files, installer code, framework documentation, and skill definitions, I confirm all three claims are correct and well-supported. Below I counter the five most likely challenges with primary-source evidence.

---

## Defense 1: Name Collision Evidence (Exact Frontmatter Quoted)

**Challenge**: "Maybe the name fields aren't actually the same."

**Verdict**: They are identical. Verified by direct file reads.

### Exact Frontmatter Blocks

**File**: `src/superclaude/commands/task.md` (lines 1-8)
```yaml
---
name: task
description: "Execute complex tasks with intelligent workflow management and delegation"
category: special
complexity: advanced
mcp-servers: [sequential, context7, magic, playwright, morphllm, serena]
personas: [architect, analyzer, frontend, backend, security, devops, project-manager]
---
```

**File**: `src/superclaude/commands/task-unified.md` (lines 1-9)
```yaml
---
name: task
description: "Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation"
category: special
complexity: advanced
mcp-servers: [sequential, context7, serena, playwright, magic, morphllm]
personas: [architect, analyzer, qa, refactorer, frontend, backend, security, devops, python-expert, quality-engineer]
version: "2.0.0"
---
```

**Both files declare `name: task`**. This is not a matter of interpretation. The YAML frontmatter value is character-for-character identical: `name: task`.

### Installed Copies Confirm the Same

A grep across `.claude/commands/sc/` for `name:\s*task\b` returns:

```
.claude/commands/sc/task.md:2:name: task
.claude/commands/sc/task-unified.md:2:name: task
.claude/commands/sc/task-mcp.md:2:name: task-mcp
```

Two files claim the same `name: task` in the active installation directory. The `task-mcp.md` file correctly uses a distinct name (`task-mcp`).

---

## Defense 2: Migration Intent Evidence (Quotes from task-unified.md)

**Challenge**: "Maybe they're intentionally separate commands."

**Verdict**: `task-unified.md` contains explicit migration documentation, version history referencing `task.md` as its v1.x predecessor, and a deprecation chain from `task-mcp.md`. The intent to replace is stated, not implied.

### Evidence A: Migration Section (task-unified.md, lines 537-560)

```markdown
## Migration from Legacy Commands

### From `/sc:task` (v1.x)
```bash
# Old
/sc:task create "feature" --strategy systematic

# New (equivalent)
/sc:task "feature" --strategy systematic --compliance auto
```

### From `/sc:task-mcp`
```bash
# Old
/sc:task-mcp "fix tests" --tier strict

# New (equivalent)
/sc:task "fix tests" --compliance strict
```

### Deprecation Notice

`/sc:task-mcp` is deprecated. Use `/sc:task --compliance [tier]` instead.
```

This section explicitly labels the old `task.md` command as "v1.x" and provides migration instructions FROM it TO the unified command. Commands that are "intentionally separate" do not include migration guides from one to the other.

### Evidence B: Version History (task-unified.md, lines 564-567)

```markdown
## Version History

- **v2.0.0** - Unified command merging sc:task and sc:task-mcp
- **v1.0.0** - Original sc:task orchestration command
```

The version history explicitly states v2.0.0 "merges" sc:task and sc:task-mcp. The word "merging" is unambiguous: the two prior commands were intended to be absorbed into one.

### Evidence C: task-mcp.md Deprecation Chain (task-mcp.md, lines 1-17)

```yaml
---
name: task-mcp
deprecated: true
deprecated_by: "task-unified"
migration_guide: "Use /sc:task --compliance [tier] instead"
---

> **DEPRECATION NOTICE**: This command is deprecated as of v2.0.0.
> Use `/sc:task --compliance [tier]` instead.
```

`task-mcp.md` is already properly deprecated with `deprecated_by: "task-unified"`. This establishes the deprecation pattern. The same pattern should have been applied to `task.md` but was not -- confirming an incomplete migration, not intentional coexistence.

### Evidence D: SKILL.md Purpose Statement (sc-task-unified/SKILL.md, line 26)

```markdown
- Single command replaces confusion between `sc:task` and `sc:task-mcp`
```

The skill itself states its purpose is to "replace confusion between" the two prior commands. This is an explicit design goal, not accidental overlap.

---

## Defense 3: Routing Behavior Evidence (How Claude Code Handles This)

**Challenge**: "Claude Code uses filenames not frontmatter for routing."

**Verdict**: Even if Claude Code primarily uses filenames for command dispatch (making `/sc:task` resolve to `task.md` and `/sc:task-unified` resolve to `task-unified.md`), this does NOT eliminate the problem. It actually makes things worse for the intended architecture.

### Observation 1: Both Files Are Installed

The `.claude/commands/sc/` directory contains all three files:

```
task-mcp.md
task.md
task-unified.md
```

All three are installed by `install_commands.py`, which performs a blind `glob("*.md")` copy with no filtering, no frontmatter parsing, and no conflict detection (confirmed by reading the installer code at `src/superclaude/cli/install_commands.py`, lines 37-60).

### Observation 2: Filename-Based Routing Routes `/sc:task` to the Wrong File

If Claude Code resolves by filename:
- `/sc:task` resolves to `task.md` (the OLD, legacy v1.x command)
- `/sc:task-unified` resolves to `task-unified.md` (the NEW v2.0 command)

But the SKILL.md for `sc-task-unified` tells users to invoke `/sc:task`:

> **SKILL.md line 34**: `Use /sc:task when:`

And all 5 examples in the SKILL.md (lines 233-275) use `/sc:task` syntax:

```
/sc:task "implement user authentication with JWT"
/sc:task "add pagination to user list"
/sc:task "fix typo in README"
/sc:task "explain how the auth flow works"
/sc:task "update config file" --compliance strict
```

This means: the skill documentation directs users to type `/sc:task`, but filename-based routing would send them to the OLD command that has NO compliance tier system. Users following the SKILL.md instructions would never reach the unified command.

### Observation 3: Framework Docs Describe Unified Behavior Under `/sc:task` Name

The core `COMMANDS.md` (line 81) describes the unified task command under the `/sc:task` name:

```markdown
**`/sc:task [description] [flags]`** -- Unified task execution with tiered compliance
```

The `ORCHESTRATOR.md` (line 153) routes `/sc:task` to compliance tiers:

```markdown
**Purpose**: Route `/sc:task` commands to appropriate compliance tier based on task characteristics.
```

Neither file references `task-unified` as a separate entity. The framework documentation treats `/sc:task` AS the unified command. But the filesystem routes `/sc:task` to the legacy file.

### Observation 4: No `sc-task` Skill Directory Exists

```
$ ls src/superclaude/skills/ | grep task
sc-task-unified
```

Only `sc-task-unified` exists. There is no `sc-task` skill directory. The old `task.md` command has no backing skill. The unified skill is the only skill implementation, but filename routing sends `/sc:task` to the file that cannot use it.

### Conclusion for Defense 3

Whether routing is filename-based or frontmatter-based, there is a defect:
- **Filename-based**: `/sc:task` goes to the legacy command, contradicting SKILL.md, COMMANDS.md, and ORCHESTRATOR.md which all assume `/sc:task` IS the unified command.
- **Frontmatter-based**: Two files claim `name: task`, creating non-deterministic resolution.

Either way, the current state is broken. The fix (replacing `task.md` with `task-unified.md`) resolves both scenarios.

---

## Defense 4: Feature Superset Proof (task.md Features -> task-unified.md Coverage)

**Challenge**: "The fix might lose task.md functionality."

**Verdict**: `task-unified.md` is a strict superset of `task.md` with one minor exception (the `project-manager` persona). Every feature in `task.md` is present in `task-unified.md`, plus substantial additions.

### Feature-by-Feature Comparison

| Feature in task.md (v1.x) | Present in task-unified.md (v2.0)? | Evidence |
|---|---|---|
| `--strategy systematic\|agile\|enterprise` flag | YES + added `auto` option | task-unified.md line 18 |
| `--parallel` flag | YES | task-unified.md flag table |
| `--delegate` flag | YES | task-unified.md flag table |
| Multi-persona coordination | YES (expanded from 7 to 10 personas) | task-unified.md line 7 |
| Sequential MCP integration | YES (always active) | task-unified.md line 355 |
| Context7 MCP integration | YES (always active) | task-unified.md line 356 |
| Magic MCP integration | YES (conditional) | task-unified.md line 359 |
| Playwright MCP integration | YES (conditional) | task-unified.md line 358 |
| Morphllm MCP integration | YES (conditional) | task-unified.md line 360 |
| Serena MCP integration | YES (always active) | task-unified.md line 357 |
| TodoWrite hierarchical task breakdown | YES | task-unified.md line 394 |
| Task delegation for sub-agents | YES | task-unified.md flag table |
| 5-step behavioral flow | YES (expanded to 7 steps) | task-unified.md behavioral flow section |
| Analyze step | YES (step 1) | task-unified.md |
| Delegate step | YES (step 4) | task-unified.md |
| Coordinate/Execute step | YES (step 5) | task-unified.md |
| Validate step | YES (step 6, verification) | task-unified.md |
| Optimize step | YES (step 7, report) | task-unified.md |
| architect persona | YES | task-unified.md line 7 |
| analyzer persona | YES | task-unified.md line 7 |
| frontend persona | YES | task-unified.md line 7 |
| backend persona | YES | task-unified.md line 7 |
| security persona | YES | task-unified.md line 7 |
| devops persona | YES | task-unified.md line 7 |
| **project-manager persona** | **NO** (not listed) | Only persona missing |

### The One Missing Persona

The `project-manager` persona from `task.md` is not listed in `task-unified.md`'s persona array. However:

1. The `project-manager` persona is not defined anywhere in the SuperClaude persona system (it does not appear in `PERSONAS.md` which defines the 11 official personas).
2. It appears to be a phantom reference -- a persona name in a frontmatter list with no backing implementation.
3. The unified command adds 3 real, implemented personas instead: `qa`, `refactorer`, `python-expert`, and `quality-engineer` (4 additions for 1 phantom loss).

### Features ONLY in task-unified.md

The unified command adds the following capabilities that do not exist in `task.md`:

1. 4-tier compliance model (STRICT/STANDARD/LIGHT/EXEMPT)
2. Auto-classification algorithm with confidence scoring
3. Compound phrase detection for tier disambiguation
4. `--compliance` flag with 5 options
5. `--verify` flag with 4 options
6. `--skip-compliance` escape hatch
7. `--force-strict` override
8. `--reason` justification flag
9. Machine-readable telemetry classification header
10. SMART acceptance criteria per tier
11. Circuit breaker integration
12. Adversarial review step for STRICT tier
13. Post-task "Did I?" checklist
14. Memory persistence via `write_memory`
15. Feedback collection for calibration
16. 4 additional personas (qa, refactorer, python-expert, quality-engineer)

### Verdict

Replacing `task.md` with `task-unified.md` loses zero implemented functionality. The `project-manager` persona has no backing definition in the framework. Every other feature is preserved and expanded.

---

## Defense 5: Additional Evidence Found

### 5A: Plugin Directory Contains Only the Legacy task.md

The `plugins/superclaude/commands/` directory (the fallback source for the installer) contains `task.md` but does NOT contain `task-unified.md`:

```
plugins/superclaude/commands/task.md  (name: task, legacy v1.x)
```

This means pipx-installed users who get commands from the plugins directory will ONLY get the legacy command. The unified command exists only in `src/superclaude/commands/`. This is another vector of the incomplete migration.

### 5B: User Guide Documents Only Legacy Behavior

The user guide (`docs/user-guide/commands.md`) references `/sc:task` in 15+ locations and describes ONLY the legacy command's behavior (strategy flags, no compliance tiers). Excerpts:

```
├── task.md            # /sc:task - Task Management
```

```
| [`/sc:task`](#sctask---enhanced-task-management) | Execution with MCP coordination | `task.md` |
```

```
/sc:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]
```

The user guide has zero references to `task-unified`, zero mentions of compliance tiers for the task command, and zero mentions of `--compliance` or `--verify` flags. This confirms the user-facing documentation is still pointing to the v1.x command.

### 5C: COMMANDS.md and ORCHESTRATOR.md Describe Unified Features Under `/sc:task`

As noted in Defense 3, the core framework files describe the unified command's compliance-tier behavior under the `/sc:task` name. This creates an internal contradiction:

- **COMMANDS.md line 81**: `/sc:task [description] [flags]` -- Unified task execution with tiered compliance
- **ORCHESTRATOR.md line 153**: Route `/sc:task` commands to appropriate compliance tier

The framework documentation has ALREADY been updated to treat `/sc:task` as the unified command. Only the filesystem (where `task.md` still occupies the `task` filename) lags behind.

### 5D: No Tests Reference Either Command

A search for `sc:task` across the `tests/` directory returned zero results. No tests validate either the legacy or unified command behavior. This means the replacement carries no test-breakage risk.

### 5E: The Deprecation Pattern Already Exists

`task-mcp.md` provides a working template for deprecation:

```yaml
deprecated: true
deprecated_by: "task-unified"
migration_guide: "Use /sc:task --compliance [tier] instead"
```

This pattern was applied to `task-mcp.md` but NOT to `task.md`, despite both being superseded by the same unified command. The inconsistency is the defect.

### 5F: SKILL.md Internal Inconsistency Confirms Naming Confusion

The SKILL.md for `sc-task-unified` is internally inconsistent:
- **Usage section (line 48)**: `/sc:task-unified [description]`
- **Triggers section (line 34)**: `Use /sc:task when:`
- **Examples section (lines 233-275)**: All 5 examples use `/sc:task`

This inconsistency only makes sense if the SKILL.md was written with the expectation that `task-unified.md` would eventually be renamed to `task.md`, at which point `/sc:task` would resolve to the unified command. The migration was planned but not executed.

---

## Strengthened Conclusion

The four analysis reports are correct in their consensus findings. The evidence, drawn directly from primary source files, is unambiguous:

1. **The name collision is real**: Both `task.md` and `task-unified.md` declare `name: task` in YAML frontmatter. This is a verifiable fact, not an interpretation.

2. **The migration intent is explicit**: `task-unified.md` contains a "Migration from Legacy Commands" section, a version history stating "v2.0.0 - Unified command merging sc:task and sc:task-mcp", and the SKILL.md states its purpose is to "replace confusion between sc:task and sc:task-mcp".

3. **The replacement is safe**: `task-unified.md` is a strict superset of `task.md`. The only missing persona (`project-manager`) has no backing implementation in the framework. No tests would break.

4. **Additional risks exist beyond what the reports identified**:
   - The `plugins/` directory lacks `task-unified.md` entirely
   - The user guide documents only the legacy command
   - The framework's own COMMANDS.md and ORCHESTRATOR.md already treat `/sc:task` as the unified command, contradicting the filesystem state

**Recommended fix** (reinforcing all four reports): Rename `task-unified.md` to `task.md` (overwriting the legacy file), update the plugins directory, and update the user guide. This aligns the filesystem with the already-updated framework documentation and completes the migration that was started but never finished.

**Risk of inaction**: Every user who types `/sc:task` (following the SKILL.md instructions, the COMMANDS.md documentation, or the ORCHESTRATOR.md routing rules) gets the wrong command. The compliance-tier system -- the primary feature of v2.0.0 -- is silently bypassed.
