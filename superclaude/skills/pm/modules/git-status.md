---
name: git-status
description: Git repository state detection and formatting
category: module
---

# Git Status Module

**Purpose**: Detect and format current Git repository state for PM status output

## Input Commands

```bash
# Get current branch
git branch --show-current

# Get short status (modified, untracked, deleted)
git status --short

# Combined command (efficient)
git branch --show-current && git status --short
```

## Status Detection Logic

```yaml
Branch Name:
  Command: git branch --show-current
  Output: "refactor/docs-core-split"
  Format: 📍 [branch-name]

Modified Files:
  Pattern: Lines starting with " M " or "M  "
  Count: wc -l
  Symbol: M (Modified)

Deleted Files:
  Pattern: Lines starting with " D " or "D  "
  Count: wc -l
  Symbol: D (Deleted)

Untracked Files:
  Pattern: Lines starting with "?? "
  Count: wc -l
  Note: Count separately, display in description

Clean Workspace:
  Condition: git status --short returns empty
  Symbol: ✅

Uncommitted Changes:
  Condition: git status --short returns non-empty
  Symbol: ⚠️

Conflicts:
  Pattern: Lines starting with "UU " or "AA " or "DD "
  Symbol: 🔴
```

## Output Format Rules

```yaml
Clean Workspace:
  Format: "✅ Clean workspace"
  Condition: No modified, deleted, or untracked files

Uncommitted Changes:
  Format: "⚠️ Uncommitted changes ([n]M [n]D)"
  Condition: Modified or deleted files present
  Example: "⚠️ Uncommitted changes (2M)" (2 modified)
  Example: "⚠️ Uncommitted changes (1M 1D)" (1 modified, 1 deleted)
  Example: "⚠️ Uncommitted changes (3M, 2 untracked)" (with untracked note)

Conflicts:
  Format: "🔴 Conflicts detected ([n] files)"
  Condition: Merge conflicts present
  Priority: Highest (shows before other statuses)
```

## Implementation Pattern

```yaml
Step 1 - Execute Command:
  Bash: git branch --show-current && git status --short

Step 2 - Parse Branch:
  Extract first line as branch name
  Format: 📍 [branch-name]

Step 3 - Count File States:
  modified_count = grep "^ M " | wc -l
  deleted_count = grep "^ D " | wc -l
  untracked_count = grep "^?? " | wc -l
  conflict_count = grep "^UU \|^AA \|^DD " | wc -l

Step 4 - Determine Status Symbol:
  IF conflict_count > 0:
    → 🔴 Conflicts detected
  ELSE IF modified_count > 0 OR deleted_count > 0:
    → ⚠️ Uncommitted changes
  ELSE:
    → ✅ Clean workspace

Step 5 - Format Description:
  Build string based on counts:
    - If modified > 0: append "[n]M"
    - If deleted > 0: append "[n]D"
    - If untracked > 0: append ", [n] untracked"
```

## Status Symbol Priority

```yaml
Priority Order (highest to lowest):
  1. 🔴 Conflicts detected
  2. ⚠️ Uncommitted changes
  3. ✅ Clean workspace

Rules:
  - Only show ONE symbol per status
  - Conflicts override everything
  - Uncommitted changes override clean
  - Clean only when truly clean
```

## Examples

### Example 1: Clean Workspace
```bash
$ git status --short
(empty output)

Result:
📍 main
✅ Clean workspace
```

### Example 2: Modified Files Only
```bash
$ git status --short
 M superclaude/commands/pm.md
 M superclaude/agents/pm-agent.md

Result:
📍 refactor/docs-core-split
⚠️ Uncommitted changes (2M)
```

### Example 3: Mixed Changes
```bash
$ git status --short
 M superclaude/commands/pm.md
 D old-file.md
?? docs/memory/checkpoint.json
?? docs/memory/current_plan.json

Result:
📍 refactor/docs-core-split
⚠️ Uncommitted changes (1M 1D, 2 untracked)
```

### Example 4: Conflicts
```bash
$ git status --short
UU conflicted-file.md
 M other-file.md

Result:
📍 refactor/docs-core-split
🔴 Conflicts detected (1 file)
```

## Edge Cases

```yaml
Detached HEAD:
  git branch --show-current returns empty
  Fallback: git rev-parse --short HEAD
  Format: 📍 [commit-hash]

Not a Git Repository:
  git commands fail
  Fallback: 📍 (no git repo)
  Status: ⚠️ Not in git repository

Submodule Changes:
  Pattern: " M " in git status --short
  Treat as modified files
  Count normally
```

## Anti-Patterns (FORBIDDEN)

```yaml
❌ Explaining Git Status:
   "You have 2 modified files which are..."  # WRONG - verbose

❌ Listing All Files:
   "Modified: pm.md, pm-agent.md"  # WRONG - too detailed

❌ Action Suggestions:
   "You should commit these changes"  # WRONG - unsolicited

✅ Symbol-Only Status:
   ⚠️ Uncommitted changes (2M)  # CORRECT - concise
```

## Validation

```yaml
Self-Check Questions:
  ❓ Did I execute git commands in the correct directory?
  ❓ Are the counts accurate based on git status output?
  ❓ Did I choose the right status symbol?
  ❓ Is the format concise and symbol-based?

Command Test:
  cd [repo] && git branch --show-current && git status --short
  Verify: Output matches expected format
```

## Integration Points

**Used by**:
- `commands/pm.md` - Session start protocol
- `agents/pm-agent.md` - Status reporting
- Any command requiring repository state awareness

**Dependencies**:
- Git installed (standard dev environment)
- Repository context (run from repo directory)
