# 03 -- Makefile Updates (Step-by-Step Recreation Guide)

**Branch**: `feature/v2.01-Roadmap-V3`
**Scope**: 3 categories of changes, +114 lines / -9 lines, net +105
**Source diff**: `git diff HEAD -- Makefile` (baseline: commit `5733e32`)
**Policy driver**: `docs/architecture/command-skill-policy.md`

---

## Prerequisites

These Makefile changes depend on prior work being complete:

1. **Skill directory renames** (instruction 01) -- All 5 skill directories must already be renamed to `sc-{name}-protocol` in `src/superclaude/skills/`. The `lint-architecture` target's Check 2 and Check 6 glob for `sc-*-protocol/` directories.

2. **Command file updates** (instruction 02) -- All 5 command files must already have `## Activation` sections containing `Skill sc:{name}-protocol` invocations. The `lint-architecture` target's Check 1 and Check 4 scan commands for these patterns.

3. **SKILL.md frontmatter updates** (instruction 01) -- All SKILL.md `name:` fields must end in `-protocol`. Check 6 validates this.

If these prerequisites are not met, `make lint-architecture` will report errors even though the Makefile changes themselves are correct.

---

## Change 1: Update `.PHONY` Declaration (Line 1)

### Location

Line 1 of the Makefile.

### Before (exact)

```makefile
.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync uninstall-legacy help
```

### After (exact)

```makefile
.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync lint-architecture uninstall-legacy help
```

### What changed

`lint-architecture` was inserted between `verify-sync` and `uninstall-legacy`. This is a single-word insertion within the space-separated list.

### Execution

Replace the entire `.PHONY` line. The old string `verify-sync uninstall-legacy` becomes `verify-sync lint-architecture uninstall-legacy`.

---

## Change 2: Remove Skill-Skip Heuristic from `sync-dev` Target

### Location

Inside the `sync-dev` target, in the `for skill_dir in src/superclaude/skills/*/` loop body. The 4 lines to remove appear immediately after the `case "$$skill_name" in __*) continue;; esac;` line and immediately before the `if [ -f "$$skill_dir/SKILL.md" ]` line.

### Lines to REMOVE (exact, with tabs)

```makefile
		cmd_name=$${skill_name#sc-}; \
		if [ "$$cmd_name" != "$$skill_name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			continue; \
		fi; \
```

These are 4 lines. Each line is indented with **two tabs** (the first two lines and last line) or **three tabs** (the `continue;` line). All lines end with ` \` (space-backslash) for Makefile line continuation.

### Before context (10 lines showing position)

```makefile
	@for skill_dir in src/superclaude/skills/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		case "$$skill_name" in __*) continue;; esac; \
		cmd_name=$${skill_name#sc-}; \
		if [ "$$cmd_name" != "$$skill_name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			continue; \
		fi; \
		if [ -f "$$skill_dir/SKILL.md" ] || [ -f "$$skill_dir/skill.md" ]; then \
			mkdir -p ".claude/skills/$$skill_name"; \
```

### After context (what it looks like with lines removed)

```makefile
	@for skill_dir in src/superclaude/skills/*/; do \
		skill_name=$$(basename "$$skill_dir"); \
		case "$$skill_name" in __*) continue;; esac; \
		if [ -f "$$skill_dir/SKILL.md" ] || [ -f "$$skill_dir/skill.md" ]; then \
			mkdir -p ".claude/skills/$$skill_name"; \
```

### What this does

Removes the heuristic that stripped the `sc-` prefix from skill directory names and skipped syncing if a matching command file existed. Under the old model, `sc-adversarial` would be skipped because `adversarial.md` existed. Under the new architecture, commands delegate TO skills, so all skills must be synced.

---

## Change 3: Remove Skill-Skip Heuristic from `verify-sync` Target

### Location

Inside the `verify-sync` target, in the first `for skill_dir in src/superclaude/skills/*/` loop body. The 5 lines to remove appear immediately after the `case "$$name" in __*) continue;; esac;` line and immediately before the `if [ ! -d ".claude/skills/$$name" ];` line.

### Lines to REMOVE (exact, with tabs)

```makefile
		cmd_name=$${name#sc-}; \
		if [ "$$cmd_name" != "$$name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			echo "  ⏭️  $$name (served by /sc:$$cmd_name command)"; \
			continue; \
		fi; \
```

These are 5 lines (one more than `sync-dev` because of the `echo` message). Each line is indented with **two tabs** (first two and last) or **three tabs** (echo and continue). All lines end with ` \`.

### Before context (10 lines showing position)

```makefile
	for skill_dir in src/superclaude/skills/*/; do \
		name=$$(basename "$$skill_dir"); \
		case "$$name" in __*) continue;; esac; \
		cmd_name=$${name#sc-}; \
		if [ "$$cmd_name" != "$$name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			echo "  ⏭️  $$name (served by /sc:$$cmd_name command)"; \
			continue; \
		fi; \
		if [ ! -d ".claude/skills/$$name" ]; then \
			echo "  ❌ MISSING in .claude/skills/: $$name"; \
```

### After context (what it looks like with lines removed)

```makefile
	for skill_dir in src/superclaude/skills/*/; do \
		name=$$(basename "$$skill_dir"); \
		case "$$name" in __*) continue;; esac; \
		if [ ! -d ".claude/skills/$$name" ]; then \
			echo "  ❌ MISSING in .claude/skills/: $$name"; \
```

### What this does

Same conceptual change as Change 2, plus removes the user-facing skip message (`"served by /sc:$cmd_name command"`). Without this removal, `make verify-sync` would report protocol skills as "served by" their commands instead of checking them for sync drift.

---

## Change 4: Add `lint-architecture` Target (113 Lines)

### Insertion Point

Insert AFTER the last line of the `verify-sync` target and BEFORE the `# Show help` comment that begins the `help` target. In the current (pre-change) Makefile, this is after the `fi` that closes the `verify-sync` target.

Specifically, insert after this exact line:

```makefile
	fi
```

(the final `fi` of `verify-sync`, which is the last line before a blank line and then `# Show help`)

There should be a blank line between the end of `verify-sync` and the new target, and a blank line between the new target and the `# Show help` comment.

### COMPLETE Target Content to Insert (113 lines, exact)

```makefile
# Architecture lint: enforce command/skill policy (see docs/architecture/command-skill-policy.md)
lint-architecture:
	@echo "🏗️  Linting command/skill architecture..."
	@errors=0; warns=0; \
	echo ""; \
	echo "=== Check 1: Bidirectional links (command → skill) ==="; \
	for cmd in src/superclaude/commands/*.md; do \
		name=$$(basename "$$cmd" .md); \
		case "$$name" in README) continue;; esac; \
		if grep -q '## Activation' "$$cmd" 2>/dev/null; then \
			skill_ref=$$(grep -oP 'Skill sc:\K[a-z0-9-]+' "$$cmd" 2>/dev/null | head -1); \
			if [ -n "$$skill_ref" ]; then \
				skill_dir="src/superclaude/skills/sc-$$skill_ref"; \
				if [ ! -d "$$skill_dir" ]; then \
					echo "  ❌ $$name.md references sc:$$skill_ref but $$skill_dir/ does not exist"; \
					errors=$$((errors + 1)); \
				else \
					echo "  ✅ $$name.md → sc:$$skill_ref"; \
				fi; \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "=== Check 2: Bidirectional links (skill → command) ==="; \
	for skill_dir in src/superclaude/skills/sc-*-protocol/; do \
		[ -d "$$skill_dir" ] || continue; \
		name=$$(basename "$$skill_dir"); \
		cmd_name=$$(echo "$$name" | sed 's/^sc-//; s/-protocol$$//'); \
		if [ ! -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			echo "  ❌ $$name/ exists but commands/$$cmd_name.md does not"; \
			errors=$$((errors + 1)); \
		else \
			echo "  ✅ $$name/ → $$cmd_name.md"; \
		fi; \
	done; \
	echo ""; \
	echo "=== Check 3: Command size limits ==="; \
	for cmd in src/superclaude/commands/*.md; do \
		name=$$(basename "$$cmd"); \
		case "$$name" in README.md) continue;; esac; \
		lines=$$(wc -l < "$$cmd"); \
		if [ "$$lines" -gt 500 ]; then \
			echo "  ❌ $$name: $$lines lines (max 500)"; \
			errors=$$((errors + 1)); \
		elif [ "$$lines" -gt 200 ]; then \
			echo "  ⚠️  $$name: $$lines lines (consider splitting into command + protocol skill)"; \
			warns=$$((warns + 1)); \
		fi; \
	done; \
	echo ""; \
	echo "=== Check 4: Activation section for commands with protocol skills ==="; \
	for skill_dir in src/superclaude/skills/sc-*-protocol/; do \
		[ -d "$$skill_dir" ] || continue; \
		name=$$(basename "$$skill_dir"); \
		cmd_name=$$(echo "$$name" | sed 's/^sc-//; s/-protocol$$//'); \
		cmd_file="src/superclaude/commands/$$cmd_name.md"; \
		if [ -f "$$cmd_file" ]; then \
			if ! grep -q '## Activation' "$$cmd_file" 2>/dev/null; then \
				echo "  ❌ $$cmd_name.md missing ## Activation section (has protocol skill $$name/)"; \
				errors=$$((errors + 1)); \
			else \
				echo "  ✅ $$cmd_name.md has ## Activation"; \
			fi; \
		fi; \
	done; \
	echo ""; \
	echo "=== Check 5: Skill frontmatter validation ==="; \
	for skill_dir in src/superclaude/skills/*/; do \
		name=$$(basename "$$skill_dir"); \
		case "$$name" in __*) continue;; esac; \
		skill_file="$$skill_dir/SKILL.md"; \
		[ -f "$$skill_file" ] || skill_file="$$skill_dir/skill.md"; \
		[ -f "$$skill_file" ] || continue; \
		missing=""; \
		grep -q '^name:' "$$skill_file" || missing="$$missing name"; \
		grep -q '^description:' "$$skill_file" || missing="$$missing description"; \
		grep -q '^allowed-tools:' "$$skill_file" || missing="$$missing allowed-tools"; \
		if [ -n "$$missing" ]; then \
			echo "  ❌ $$name/SKILL.md missing frontmatter:$$missing"; \
			errors=$$((errors + 1)); \
		else \
			echo "  ✅ $$name/SKILL.md frontmatter complete"; \
		fi; \
	done; \
	echo ""; \
	echo "=== Check 6: Protocol skill naming consistency ==="; \
	for skill_dir in src/superclaude/skills/sc-*-protocol/; do \
		[ -d "$$skill_dir" ] || continue; \
		dir_name=$$(basename "$$skill_dir"); \
		skill_file="$$skill_dir/SKILL.md"; \
		[ -f "$$skill_file" ] || continue; \
		file_name=$$(grep '^name:' "$$skill_file" | head -1 | sed 's/^name: *//; s/"//g'); \
		if ! echo "$$file_name" | grep -q '\-protocol$$'; then \
			echo "  ❌ $$dir_name/SKILL.md name '$$file_name' does not end in -protocol"; \
			errors=$$((errors + 1)); \
		else \
			echo "  ✅ $$dir_name/SKILL.md name '$$file_name' matches convention"; \
		fi; \
	done; \
	echo ""; \
	echo "=== Summary ==="; \
	echo "  Errors: $$errors"; \
	echo "  Warnings: $$warns"; \
	if [ "$$errors" -gt 0 ]; then \
		echo "❌ Architecture lint failed with $$errors error(s)."; \
		echo "   See docs/architecture/command-skill-policy.md for policy details."; \
		exit 1; \
	elif [ "$$warns" -gt 0 ]; then \
		echo "⚠️  Architecture lint passed with $$warns warning(s)."; \
	else \
		echo "✅ Architecture lint passed."; \
	fi
```

### Critical formatting notes

- The target label `lint-architecture:` has NO leading whitespace.
- The first `@echo` line is indented with ONE TAB (not spaces).
- The `@errors=0; warns=0; \` line is indented with ONE TAB.
- All continuation lines within the shell block are indented with ONE TAB followed by zero or more additional TABs for nesting.
- Every continuation line ends with ` \` (space-backslash) EXCEPT the last line (`fi`).
- The `grep -oP` in Check 1 uses Perl-compatible regex (`-P` flag), which requires GNU grep.
- The `sed 's/^sc-//; s/-protocol$//'` in Checks 2 and 4 strips both prefix and suffix.

### Check descriptions

| Check | Name | What it validates | Failure mode |
|-------|------|-------------------|--------------|
| 1 | Command -> Skill links | Commands with `## Activation` that reference `Skill sc:X` have a corresponding `src/superclaude/skills/sc-X/` directory | ERROR |
| 2 | Skill -> Command links | Each `sc-*-protocol/` skill directory has a corresponding `{name}.md` command (after stripping `sc-` and `-protocol`) | ERROR |
| 3 | Command size limits | Commands exceeding 500 lines = ERROR; exceeding 200 lines = WARNING | ERROR/WARN |
| 4 | Activation section present | Commands that have a matching `-protocol` skill must contain `## Activation` | ERROR |
| 5 | Skill frontmatter | All SKILL.md files must have `name:`, `description:`, and `allowed-tools:` fields | ERROR |
| 6 | Naming consistency | `-protocol` skill directories must have a SKILL.md `name:` field ending in `-protocol` | ERROR |

### Exit behavior

- Any errors (errors > 0): prints failure message referencing policy doc, exits with code 1
- Warnings only (warns > 0, errors = 0): prints warning message, exits with code 0
- Clean (both 0): prints success message, exits with code 0

---

## Change 5: Update `help` Target

### Location

Inside the `help` target, under the "Component Sync" section. Insert after the `verify-sync` line and before the blank echo line.

### Before (exact, 3 lines)

```makefile
	@echo "  make sync-dev        - Sync src/ → .claude/ for local development"
	@echo "  make verify-sync     - Check src/ and .claude/ are in sync (CI-friendly)"
	@echo ""
```

### After (exact, 4 lines)

```makefile
	@echo "  make sync-dev        - Sync src/ → .claude/ for local development"
	@echo "  make verify-sync     - Check src/ and .claude/ are in sync (CI-friendly)"
	@echo "  make lint-architecture - Enforce command/skill architecture policy"
	@echo ""
```

### Line to INSERT (exact)

```makefile
	@echo "  make lint-architecture - Enforce command/skill architecture policy"
```

Indented with ONE TAB. Inserted between the `verify-sync` line and the `@echo ""` line.

---

## Execution Order

Apply changes in this order to avoid intermediate broken states:

1. **Change 1**: Update `.PHONY` (line 1) -- add `lint-architecture`
2. **Change 2**: Remove 4-line heuristic from `sync-dev`
3. **Change 3**: Remove 5-line heuristic from `verify-sync`
4. **Change 4**: Insert 113-line `lint-architecture` target after `verify-sync`
5. **Change 5**: Add help text line for `lint-architecture`

Changes 2 and 3 can be done in either order. Change 4 must come after Change 3 (since they're in adjacent areas and line numbers shift). Change 5 is independent.

---

## Verification

After applying all changes, run:

```bash
# Step 1: Verify sync still works (heuristic removal should cause all -protocol skills to sync)
make sync-dev

# Step 2: Verify sync check passes
make verify-sync

# Step 3: Run architecture lint -- all 6 checks should pass
make lint-architecture

# Step 4: Verify help includes the new entry
make help | grep lint-architecture
```

### Expected `make lint-architecture` output (with all prerequisites complete)

```
🏗️  Linting command/skill architecture...

=== Check 1: Bidirectional links (command → skill) ===
  ✅ adversarial.md → sc:adversarial-protocol
  ✅ cleanup-audit.md → sc:cleanup-audit-protocol
  ✅ roadmap.md → sc:roadmap-protocol
  ✅ task-unified.md → sc:task-unified-protocol
  ✅ validate-tests.md → sc:validate-tests-protocol

=== Check 2: Bidirectional links (skill → command) ===
  ✅ sc-adversarial-protocol/ → adversarial.md
  ✅ sc-cleanup-audit-protocol/ → cleanup-audit.md
  ✅ sc-roadmap-protocol/ → roadmap.md
  ✅ sc-task-unified-protocol/ → task-unified.md
  ✅ sc-validate-tests-protocol/ → validate-tests.md

=== Check 3: Command size limits ===
(no output if all commands are under 200 lines)

=== Check 4: Activation section for commands with protocol skills ===
  ✅ adversarial.md has ## Activation
  ✅ cleanup-audit.md has ## Activation
  ✅ roadmap.md has ## Activation
  ✅ task-unified.md has ## Activation
  ✅ validate-tests.md has ## Activation

=== Check 5: Skill frontmatter validation ===
  ✅ sc-adversarial-protocol/SKILL.md frontmatter complete
  ✅ sc-cleanup-audit-protocol/SKILL.md frontmatter complete
  ✅ sc-roadmap-protocol/SKILL.md frontmatter complete
  ✅ sc-task-unified-protocol/SKILL.md frontmatter complete
  ✅ sc-validate-tests-protocol/SKILL.md frontmatter complete

=== Check 6: Protocol skill naming consistency ===
  ✅ sc-adversarial-protocol/SKILL.md name 'sc:adversarial-protocol' matches convention
  ✅ sc-cleanup-audit-protocol/SKILL.md name 'sc:cleanup-audit-protocol' matches convention
  ✅ sc-roadmap-protocol/SKILL.md name 'sc:roadmap-protocol' matches convention
  ✅ sc-task-unified-protocol/SKILL.md name 'sc:task-unified-protocol' matches convention
  ✅ sc-validate-tests-protocol/SKILL.md name 'sc:validate-tests-protocol' matches convention

=== Summary ===
  Errors: 0
  Warnings: 0
✅ Architecture lint passed.
```

---

## Known Gaps: Policy vs Implementation

The policy document (`docs/architecture/command-skill-policy.md`) defines **10** CI checks. The Makefile implements **6** explicit checks covering **8** of those 10 policy requirements. Two checks are genuinely missing:

### Missing Check #5: Inline Protocol Detection

**Policy requirement**: "Command with matching `-protocol` skill contains YAML code blocks >20 lines" (ERROR)

**What it would catch**: Commands that still embed protocol YAML inline instead of delegating to the skill.

**Why not implemented**: Requires YAML code block boundary detection in markdown files (matching triple-backtick fences with `yaml` language tags, counting lines between them). This is significantly more complex than the simple `grep`/`wc` patterns used by the other checks.

**Impact of absence**: If a command re-accumulates inline protocol content over time, this lint would not catch it. The command size limit (Check 3, >200 lines warning / >500 lines error) provides a partial safety net.

### Missing Check #7: Activation Reference Correctness

**Policy requirement**: "`## Activation` section does not contain `Skill sc:<name>-protocol`" (ERROR)

**What it would catch**: Commands that have an `## Activation` section but reference the wrong skill name (e.g., `Skill sc:adversarial` instead of `Skill sc:adversarial-protocol`).

**Why not implemented**: Check 1 already extracts the skill reference from the activation section and validates that the referenced skill directory exists. However, Check 1 does NOT verify that the reference matches the *expected* naming pattern derived from the command's own name. A command `foo.md` could reference `sc:bar-protocol` and Check 1 would pass (as long as `sc-bar-protocol/` exists) even though the expected reference is `sc:foo-protocol`.

**Impact of absence**: Cross-wired command-skill references would not be caught. In practice, this is low risk because Check 2 (skill -> command) would flag the orphaned skill, but the mismatch itself would not produce an error.

### Check #10: Delegated to `verify-sync`

**Policy requirement**: "Files in `src/` not matching `.claude/`" (ERROR)

**Implementation**: Covered by the existing `make verify-sync` target. The policy labels it as a `lint-architecture` check, but the Makefile keeps it as a standalone target. This is a design decision, not a gap.

### Checks #3 and #4: Combined

The policy lists line count thresholds as two separate checks (WARN at 200, ERROR at 500). The Makefile implements them as a single Check 3 with two threshold branches. This is an implementation simplification, not a gap.

---

## Byte-for-Byte Verification

To confirm the Makefile changes match the original implementation exactly:

```bash
# After applying all changes, this diff should be empty
git diff HEAD -- Makefile
```

If the diff is not empty, compare the output against the diff captured at analysis time:

```bash
# Captured reference diff (should produce identical output to your changes)
git diff 5733e32..9060a65 -- Makefile
```

---

## Summary of Changes

| Change | Type | Lines Affected | Location |
|--------|------|---------------|----------|
| 1. `.PHONY` update | Modify | 1 line modified | Line 1 |
| 2. `sync-dev` heuristic removal | Delete | 4 lines removed | Inside `sync-dev` skill loop |
| 3. `verify-sync` heuristic removal | Delete | 5 lines removed | Inside `verify-sync` skill loop |
| 4. `lint-architecture` target | Insert | 113 lines added | After `verify-sync`, before `help` |
| 5. `help` text update | Insert | 1 line added | Inside `help` target, Component Sync section |
| **Total** | | **+114 / -9 = net +105** | |
