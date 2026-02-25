# Batch 7: Makefile Analysis

**File**: `Makefile`
**Status**: MODIFIED
**Diff size**: ~125 lines changed (113 added, 9 removed, 3 modified)
**Branch**: `feature/v2.01-Roadmap-V3`
**Baseline commit**: `9060a65`

---

## Summary of Changes

Three distinct change categories:

1. **New target**: `lint-architecture` (113 lines) -- enforces the command/skill naming policy
2. **Removed logic**: skill-skip heuristic removed from `sync-dev` and `verify-sync` (9 lines deleted)
3. **Housekeeping**: `.PHONY` declaration updated, `help` target updated

---

## Change 1: `.PHONY` Declaration

### Diff

```diff
-.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync uninstall-legacy help
+.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync lint-architecture uninstall-legacy help
```

### Analysis

- **Added**: `lint-architecture` to the `.PHONY` list
- **Position**: inserted between `verify-sync` and `uninstall-legacy`
- **Impact**: Declares the new target as phony (always runs, never matches a file)

---

## Change 2: `sync-dev` Target -- Removed Skill-Skip Heuristic

### Diff (lines removed)

```diff
 	@for skill_dir in src/superclaude/skills/*/; do \
 		skill_name=$$(basename "$$skill_dir"); \
 		case "$$skill_name" in __*) continue;; esac; \
-		cmd_name=$${skill_name#sc-}; \
-		if [ "$$cmd_name" != "$$skill_name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
-			continue; \
-		fi; \
 		if [ -f "$$skill_dir/SKILL.md" ] || [ -f "$$skill_dir/skill.md" ]; then \
```

### What Was Removed

A 4-line block that **skipped syncing a skill directory** if a matching command file existed. The logic was:

1. Strip the `sc-` prefix from the skill directory name (e.g., `sc-adversarial` -> `adversarial`)
2. Check if `src/superclaude/commands/<stripped-name>.md` exists
3. If it does, `continue` (skip syncing that skill entirely)

### Why It Was Removed

Under the old naming convention (`sc-adversarial`), skills that had a corresponding command file were treated as "served by the command" and did not need to be synced to `.claude/skills/`. The new `-protocol` suffix naming convention (`sc-adversarial-protocol`) changes this relationship:

- **Old model**: command `adversarial.md` *replaces* skill `sc-adversarial/` -- no sync needed
- **New model**: command `adversarial.md` is a lightweight entry point that *activates* skill `sc-adversarial-protocol/` -- both must be synced

With the `-protocol` suffix, the strip-and-match heuristic (`sc-adversarial` -> `adversarial` -> `adversarial.md` exists -> skip) would no longer match anyway (`sc-adversarial-protocol` -> `adversarial-protocol` -> no file `adversarial-protocol.md`). But removing the logic entirely is the correct cleanup because:

1. It eliminates dead logic that would never trigger for `-protocol` skills
2. It ensures ALL skill directories (including protocol skills) are synced to `.claude/skills/`
3. It simplifies the sync loop

### Rollback Impact

If rolling back to the old skill names (`sc-adversarial` etc.), this heuristic must be **restored** or those skills will be synced to `.claude/skills/` redundantly alongside their commands. The old behavior intentionally avoided this duplication.

---

## Change 3: `verify-sync` Target -- Removed Same Skill-Skip Heuristic

### Diff (lines removed)

```diff
 	for skill_dir in src/superclaude/skills/*/; do \
 		name=$$(basename "$$skill_dir"); \
 		case "$$name" in __*) continue;; esac; \
-		cmd_name=$${name#sc-}; \
-		if [ "$$cmd_name" != "$$name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
-			echo "  ⏭️  $$name (served by /sc:$$cmd_name command)"; \
-			continue; \
-		fi; \
 		if [ ! -d ".claude/skills/$$name" ]; then \
```

### What Was Removed

A 5-line block (same heuristic as `sync-dev`, plus a user-facing skip message). The logic:

1. Strip `sc-` prefix from skill name
2. Check if matching command exists
3. If so, print `⏭️  <name> (served by /sc:<cmd> command)` and skip verification

### Why It Was Removed

Same rationale as `sync-dev`. Under the new `-protocol` model, protocol skills MUST exist in `.claude/skills/` and must be verified. The skip message "served by /sc:X command" no longer applies because the command now delegates TO the skill rather than replacing it.

### Rollback Impact

Same as `sync-dev` -- must be restored if reverting to old naming convention.

---

## Change 4: New Target `lint-architecture` (113 lines)

### Full Target Structure

```
lint-architecture:
    Check 1: Bidirectional links (command -> skill)
    Check 2: Bidirectional links (skill -> command)
    Check 3: Command size limits
    Check 4: Activation section for commands with protocol skills
    Check 5: Skill frontmatter validation
    Check 6: Protocol skill naming consistency
    Summary: error/warning counts, exit 1 on errors
```

### Check-by-Check Breakdown

#### Check 1: Command -> Skill Links

```bash
for cmd in src/superclaude/commands/*.md; do
    # Skip README
    # If command has "## Activation" section:
    #   Extract skill reference from "Skill sc:<name>" pattern
    #   Verify src/superclaude/skills/sc-<name>/ directory exists
```

- **What it validates**: Every command that declares an `## Activation` section must reference a skill directory that actually exists
- **Pattern matched**: `Skill sc:<name>` in the command file
- **Expected directory**: `src/superclaude/skills/sc-<name>/`
- **Failure mode**: ERROR if referenced skill directory is missing

#### Check 2: Skill -> Command Links

```bash
for skill_dir in src/superclaude/skills/sc-*-protocol/; do
    # Extract command name: strip "sc-" prefix and "-protocol" suffix
    # Verify src/superclaude/commands/<cmd_name>.md exists
```

- **What it validates**: Every `-protocol` skill directory must have a corresponding command file
- **Name derivation**: `sc-adversarial-protocol/` -> strip `sc-` and `-protocol` -> `adversarial` -> `adversarial.md`
- **Only targets**: Directories matching `sc-*-protocol/` glob (not plain skills)
- **Failure mode**: ERROR if command file is missing

#### Check 3: Command Size Limits

```bash
for cmd in src/superclaude/commands/*.md; do
    lines=$(wc -l < "$cmd")
    # >500 lines: ERROR
    # >200 lines: WARNING (consider splitting into command + protocol skill)
```

- **What it validates**: Commands should be lightweight entry points
- **Thresholds**: >500 = error, >200 = warning
- **Rationale**: Large commands should be split into a slim command + protocol skill
- **Directly supports**: The command/skill split pattern this rename introduces

#### Check 4: Activation Section Enforcement

```bash
for skill_dir in src/superclaude/skills/sc-*-protocol/; do
    # Derive command name (same as Check 2)
    # If command file exists, verify it contains "## Activation"
```

- **What it validates**: Commands paired with protocol skills MUST have an `## Activation` section
- **Rationale**: The `## Activation` section is how the command tells Claude Code to load the skill
- **Failure mode**: ERROR if `## Activation` is missing from a paired command

#### Check 5: Skill Frontmatter Validation

```bash
for skill_dir in src/superclaude/skills/*/; do
    # Check SKILL.md (or skill.md) for required frontmatter fields:
    #   - name:
    #   - description:
    #   - allowed-tools:
```

- **What it validates**: ALL skills (not just protocol skills) have proper SKILL.md frontmatter
- **Required fields**: `name:`, `description:`, `allowed-tools:`
- **Scope**: Every skill directory, not just `-protocol` ones
- **Failure mode**: ERROR listing which fields are missing

#### Check 6: Protocol Skill Naming Consistency

```bash
for skill_dir in src/superclaude/skills/sc-*-protocol/; do
    # Read "name:" field from SKILL.md
    # Verify the name value ends in "-protocol"
```

- **What it validates**: The `name:` frontmatter inside SKILL.md must match the directory convention
- **Example**: Directory `sc-adversarial-protocol/` -> SKILL.md `name:` must end in `-protocol`
- **Rationale**: Prevents directory named `*-protocol` but SKILL.md still using old name
- **Failure mode**: ERROR if name field doesn't end in `-protocol`

### Exit Behavior

- Any errors -> `exit 1` (CI/CD failure)
- Warnings only -> `exit 0` with warning message
- Clean -> `exit 0` with success message
- References `docs/architecture/command-skill-policy.md` for policy documentation

---

## Change 5: `help` Target Updated

### Diff

```diff
 	@echo "🔄 Component Sync:"
 	@echo "  make sync-dev        - Sync src/ → .claude/ for local development"
 	@echo "  make verify-sync     - Check src/ and .claude/ are in sync (CI-friendly)"
+	@echo "  make lint-architecture - Enforce command/skill architecture policy"
```

- Adds `lint-architecture` to the help text under "Component Sync" section

---

## Target Dependency Map

```
                    install
                       |
                    verify
                       |
    +---------+--------+--------+---------+
    |         |        |        |         |
   test  test-plugin  lint   format    doctor

    sync-dev ──→ verify-sync ──→ lint-architecture
    (copy)       (diff check)    (policy check)

    build-plugin ──→ sync-plugin-repo
```

Key relationships:
- `lint-architecture` is independent -- no Make-level dependencies on other targets
- Logically, `lint-architecture` should run AFTER `sync-dev` and `verify-sync` in a CI pipeline
- `sync-plugin-repo` depends on `build-plugin` (declared dependency)
- All other targets are independent

---

## Relationship to Skill Rename Pattern

This Makefile change is the **build-system enforcement layer** for the `sc-*` -> `sc-*-protocol` rename:

| Aspect | Old Convention | New Convention | Makefile Impact |
|--------|---------------|----------------|-----------------|
| Skill naming | `sc-adversarial` | `sc-adversarial-protocol` | Check 6 enforces `-protocol` suffix |
| Command/skill relationship | Command replaces skill | Command activates skill | Check 1/2 enforce bidirectional links |
| Sync behavior | Skip skills with matching commands | Sync all skills | Removed skip heuristic |
| Command size | No limit | 500 max (200 warn) | Check 3 enforces splitting |
| Activation section | Not required | Required for paired commands | Check 4 enforces presence |
| SKILL.md frontmatter | Informal | Required fields | Check 5 enforces schema |

---

## Rollback Considerations

### To fully roll back these Makefile changes:

1. **Restore the skip heuristic in `sync-dev`** (4 lines after `case "$$skill_name" in __*) continue;; esac;`)
2. **Restore the skip heuristic in `verify-sync`** (5 lines after `case "$$name" in __*) continue;; esac;`)
3. **Remove `lint-architecture` target entirely** (113 lines)
4. **Remove `lint-architecture` from `.PHONY`**
5. **Remove `lint-architecture` from `help` target**

### Risks if only partially rolled back:

- If skill directories are renamed back but `lint-architecture` is kept, Check 2 and Check 6 will fail (they expect `-protocol` suffix)
- If skip heuristic is not restored but skills are renamed back, `sync-dev` will create redundant `.claude/skills/sc-*` directories alongside the commands that already serve them
- If `verify-sync` skip heuristic is not restored, the verify step will report drift for skills that should be skipped

### Safe rollback order:

1. Remove `lint-architecture` target and references (independent, no other targets depend on it)
2. Restore skip heuristic in both `sync-dev` and `verify-sync` (must be done together)

---

## Raw Diff

```diff
diff --git a/Makefile b/Makefile
index 4299a15..9e5a810 100644
--- a/Makefile
+++ b/Makefile
@@ -1,4 +1,4 @@
-.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync uninstall-legacy help
+.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync lint-architecture uninstall-legacy help

 # Installation (local source, editable) - RECOMMENDED
 install:
@@ -111,10 +111,6 @@ sync-dev:
 	@for skill_dir in src/superclaude/skills/*/; do \
 		skill_name=$$(basename "$$skill_dir"); \
 		case "$$skill_name" in __*) continue;; esac; \
-		cmd_name=$${skill_name#sc-}; \
-		if [ "$$cmd_name" != "$$skill_name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
-			continue; \
-		fi; \
 		if [ -f "$$skill_dir/SKILL.md" ] || [ -f "$$skill_dir/skill.md" ]; then \
 			mkdir -p ".claude/skills/$$skill_name"; \
 			find "$$skill_dir" -type f ! -name '__init__.py' ! -path '*/__pycache__/*' -exec sh -c ' \
@@ -151,11 +147,6 @@ verify-sync:
 	for skill_dir in src/superclaude/skills/*/; do \
 		name=$$(basename "$$skill_dir"); \
 		case "$$name" in __*) continue;; esac; \
-		cmd_name=$${name#sc-}; \
-		if [ "$$cmd_name" != "$$name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
-			echo "  ⏭️  $$name (served by /sc:$$cmd_name command)"; \
-			continue; \
-		fi; \
 		if [ ! -d ".claude/skills/$$name" ]; then \
 			echo "  ❌ MISSING in .claude/skills/: $$name"; \
 			drift=1; \
@@ -238,6 +229,119 @@ verify-sync:
 		exit 1; \
 	fi

+# Architecture lint: enforce command/skill policy (see docs/architecture/command-skill-policy.md)
+lint-architecture:
+	@echo "🏗️  Linting command/skill architecture..."
+	@errors=0; warns=0; \
+	echo ""; \
+	echo "=== Check 1: Bidirectional links (command → skill) ==="; \
+	for cmd in src/superclaude/commands/*.md; do \
+		name=$$(basename "$$cmd" .md); \
+		case "$$name" in README) continue;; esac; \
+		if grep -q '## Activation' "$$cmd" 2>/dev/null; then \
+			skill_ref=$$(grep -oP 'Skill sc:\K[a-z0-9-]+' "$$cmd" 2>/dev/null | head -1); \
+			if [ -n "$$skill_ref" ]; then \
+				skill_dir="src/superclaude/skills/sc-$$skill_ref"; \
+				if [ ! -d "$$skill_dir" ]; then \
+					echo "  ❌ $$name.md references sc:$$skill_ref but $$skill_dir/ does not exist"; \
+					errors=$$((errors + 1)); \
+				else \
+					echo "  ✅ $$name.md → sc:$$skill_ref"; \
+				fi; \
+			fi; \
+		fi; \
+	done; \
+	echo ""; \
+	echo "=== Check 2: Bidirectional links (skill → command) ==="; \
+	for skill_dir in src/superclaude/skills/sc-*-protocol/; do \
+		[ -d "$$skill_dir" ] || continue; \
+		name=$$(basename "$$skill_dir"); \
+		cmd_name=$$(echo "$$name" | sed 's/^sc-//; s/-protocol$$//'); \
+		if [ ! -f "src/superclaude/commands/$$cmd_name.md" ]; then \
+			echo "  ❌ $$name/ exists but commands/$$cmd_name.md does not"; \
+			errors=$$((errors + 1)); \
+		else \
+			echo "  ✅ $$name/ → $$cmd_name.md"; \
+		fi; \
+	done; \
+	echo ""; \
+	echo "=== Check 3: Command size limits ==="; \
+	for cmd in src/superclaude/commands/*.md; do \
+		name=$$(basename "$$cmd"); \
+		case "$$name" in README.md) continue;; esac; \
+		lines=$$(wc -l < "$$cmd"); \
+		if [ "$$lines" -gt 500 ]; then \
+			echo "  ❌ $$name: $$lines lines (max 500)"; \
+			errors=$$((errors + 1)); \
+		elif [ "$$lines" -gt 200 ]; then \
+			echo "  ⚠️  $$name: $$lines lines (consider splitting into command + protocol skill)"; \
+			warns=$$((warns + 1)); \
+		fi; \
+	done; \
+	echo ""; \
+	echo "=== Check 4: Activation section for commands with protocol skills ==="; \
+	for skill_dir in src/superclaude/skills/sc-*-protocol/; do \
+		[ -d "$$skill_dir" ] || continue; \
+		name=$$(basename "$$skill_dir"); \
+		cmd_name=$$(echo "$$name" | sed 's/^sc-//; s/-protocol$$//'); \
+		cmd_file="src/superclaude/commands/$$cmd_name.md"; \
+		if [ -f "$$cmd_file" ]; then \
+			if ! grep -q '## Activation' "$$cmd_file" 2>/dev/null; then \
+				echo "  ❌ $$cmd_name.md missing ## Activation section (has protocol skill $$name/)"; \
+				errors=$$((errors + 1)); \
+			else \
+				echo "  ✅ $$cmd_name.md has ## Activation"; \
+			fi; \
+		fi; \
+	done; \
+	echo ""; \
+	echo "=== Check 5: Skill frontmatter validation ==="; \
+	for skill_dir in src/superclaude/skills/*/; do \
+		name=$$(basename "$$skill_dir"); \
+		case "$$name" in __*) continue;; esac; \
+		skill_file="$$skill_dir/SKILL.md"; \
+		[ -f "$$skill_file" ] || skill_file="$$skill_dir/skill.md"; \
+		[ -f "$$skill_file" ] || continue; \
+		missing=""; \
+		grep -q '^name:' "$$skill_file" || missing="$$missing name"; \
+		grep -q '^description:' "$$skill_file" || missing="$$missing description"; \
+		grep -q '^allowed-tools:' "$$skill_file" || missing="$$missing allowed-tools"; \
+		if [ -n "$$missing" ]; then \
+			echo "  ❌ $$name/SKILL.md missing frontmatter:$$missing"; \
+			errors=$$((errors + 1)); \
+		else \
+			echo "  ✅ $$name/SKILL.md frontmatter complete"; \
+		fi; \
+	done; \
+	echo ""; \
+	echo "=== Check 6: Protocol skill naming consistency ==="; \
+	for skill_dir in src/superclaude/skills/sc-*-protocol/; do \
+		[ -d "$$skill_dir" ] || continue; \
+		dir_name=$$(basename "$$skill_dir"); \
+		skill_file="$$skill_dir/SKILL.md"; \
+		[ -f "$$skill_file" ] || continue; \
+		file_name=$$(grep '^name:' "$$skill_file" | head -1 | sed 's/^name: *//; s/"//g'); \
+		if ! echo "$$file_name" | grep -q '\-protocol$$'; then \
+			echo "  ❌ $$dir_name/SKILL.md name '$$file_name' does not end in -protocol"; \
+			errors=$$((errors + 1)); \
+		else \
+			echo "  ✅ $$dir_name/SKILL.md name '$$file_name' matches convention"; \
+		fi; \
+	done; \
+	echo ""; \
+	echo "=== Summary ==="; \
+	echo "  Errors: $$errors"; \
+	echo "  Warnings: $$warns"; \
+	if [ "$$errors" -gt 0 ]; then \
+		echo "❌ Architecture lint failed with $$errors error(s)."; \
+		echo "   See docs/architecture/command-skill-policy.md for policy details."; \
+		exit 1; \
+	elif [ "$$warns" -gt 0 ]; then \
+		echo "⚠️  Architecture lint passed with $$warns warning(s)."; \
+	else \
+		echo "✅ Architecture lint passed."; \
+	fi
+
 # Show help
 help:
 	@echo "SuperClaude Framework - Available commands:"
@@ -257,6 +361,7 @@ help:
 	@echo "🔄 Component Sync:"
 	@echo "  make sync-dev        - Sync src/ → .claude/ for local development"
 	@echo "  make verify-sync     - Check src/ and .claude/ are in sync (CI-friendly)"
+	@echo "  make lint-architecture - Enforce command/skill architecture policy"
 	@echo ""
 	@echo "🔌 Plugin Packaging:"
 	@echo "  make build-plugin    - Build SuperClaude plugin artefacts into dist/"
```
