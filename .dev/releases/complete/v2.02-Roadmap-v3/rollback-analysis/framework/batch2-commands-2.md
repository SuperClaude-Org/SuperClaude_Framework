# Batch 2 - Commands Analysis (Part 2): task-unified.md & validate-tests.md

**Analysis Date**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3`
**Scope**: Slash command files under `.claude/commands/sc/` and `src/superclaude/commands/`

---

## File 1: `.claude/commands/sc/task-unified.md`

### Change Summary

| Metric | Value |
|--------|-------|
| Diff lines | 556 |
| Original line count | 567 |
| New line count | 106 |
| Net lines removed | 461 |
| Classification | **MAJOR REWRITE** - content extraction to skill protocol |

### Nature of Change

This is the single largest content removal in the command set. The file was reduced from 567 lines to 106 lines (an 81% reduction). The vast majority of the behavioral specification was extracted out of the command file and relocated to the new `sc-task-unified-protocol` skill.

### Exact Diff

```diff
@@ Lines 25-85 (REMOVED): Triggers Section @@
 -## Triggers
 -### Auto-Activation Patterns
 -  (table: Complexity Score, Multi-file Scope, Security Domain, Refactoring Scope, Test Remediation)
 -### Keyword Triggers
 -  (yaml block: explicit_invocation, auto_suggest_keywords with high/moderate confidence lists)
 -### Context Signals
 -  (bulleted list of 5 when-to-suggest conditions)

@@ Lines 87-91 (MODIFIED): Strategy Flags heading @@
 -### Strategy Flags (Orchestration Dimension)
 +### Strategy Flags

@@ Lines 93-97 (MODIFIED): Compliance Flags heading @@
 -### Compliance Flags (Quality Dimension)
 +### Compliance Flags

@@ Lines 106-114 (MODIFIED): Verification Flags @@
 -### Verification Flags
 -(separate table with 4 rows: critical, standard, skip, auto)
 +| `--verify [critical\|standard\|skip\|auto]` | Verification level |
   (collapsed into single row in Execution Control table)

@@ Lines 116-530 (REMOVED): Entire behavioral specification @@
 -## Behavioral Flow (7-step pipeline)
 -## Tiered Compliance Model
 -  ### TIER 1: STRICT (Full Workflow Enforcement)
 -    - Auto-Triggers list
 -    - SMART Acceptance Criteria
 -    - Mandatory Checklist (PRE-WORK, TASK EXECUTION, DOWNSTREAM IMPACT,
 -      VERIFICATION, ADVERSARIAL REVIEW, COMPLETION CRITERIA)
 -    - Post-Task "Did I?" Checklist
 -  ### TIER 2: STANDARD (Core Rules Enforcement)
 -    - Auto-Triggers, SMART Criteria, Required Checklist, Quick Validation
 -  ### TIER 3: LIGHT (Awareness Only)
 -    - Auto-Triggers, SMART Criteria, Guidance
 -  ### TIER 4: EXEMPT (No Enforcement)
 -    - Auto-Triggers, SMART Criteria, Behavior
 -## Auto-Detection Algorithm
 -  (full yaml: tier_detection with strict/exempt/light/standard triggers,
 -   priority_order, fallback, ambiguity_handling)
 -  ### Compound Phrase Handling (yaml: light_wins, strict_wins)
 -## MCP Integration
 -  ### Server Selection Matrix (table: Sequential, Context7, Serena, Playwright, Magic, Morphllm)
 -  ### Persona Coordination (yaml: core personas, domain personas, verification personas)
 -## Tool Coordination
 -  (table: TodoWrite, Read, Edit/Write, Glob, Grep, Bash, Task)
 -  ### Tier-Specific Tool Usage (table by tier)
 -## Sub-Agent Delegation Matrix (STRICT Tier)
 -  (table: 7 task types with primary/verification agent mappings)
 -## Escape Hatches
 -  (table + "When to Use" guidance)
 -## Success Metrics
 -  (table: 7 metrics with targets and measurements)
 -## Migration from Legacy Commands (detailed examples)
 -## Version History

@@ Lines 531-end (REPLACED): New compact sections @@
 +## Examples
 +  (6 compact inline examples replacing verbose per-example blocks)
 +
 +## Activation
 +  **MANDATORY**: Before executing any protocol steps, invoke:
 +  > Skill sc:task-unified-protocol
 +  Do NOT proceed with protocol execution using only this command file.
 +
 +## Behavioral Summary
 +  (single paragraph summarizing the full behavioral flow)
 +
 +## Boundaries
 +  **Will:** (single line, 7 capabilities)
 +  **Will Not:** (single line, 6 restrictions)
 +
 +## Migration
 +  (single line: `/sc:task-mcp` is deprecated)
```

### What Was Removed (Detailed Inventory)

The following self-contained sections were removed from the command file entirely:

| Section | Lines Removed | Content Description |
|---------|---------------|---------------------|
| **Triggers** | ~60 | Auto-activation patterns table, keyword triggers YAML, context signals list |
| **Behavioral Flow** | ~8 | 7-step execution pipeline (Analyze, Classify, Display, Delegate, Execute, Verify, Report) |
| **Tier 1: STRICT** | ~65 | Full mandatory checklist with 6 categories, SMART criteria, post-task "Did I?" checklist |
| **Tier 2: STANDARD** | ~25 | Core rules checklist, SMART criteria, quick validation checklist |
| **Tier 3: LIGHT** | ~18 | Guidance notes, SMART criteria |
| **Tier 4: EXEMPT** | ~14 | Behavior description, SMART criteria |
| **Auto-Detection Algorithm** | ~55 | Full YAML tier_detection config with keyword lists, path patterns, file count thresholds, priority ordering, compound phrase handling |
| **MCP Integration** | ~35 | Server selection matrix table, persona coordination YAML (core/domain/verification) |
| **Tool Coordination** | ~20 | Tool-purpose table, tier-specific tool usage matrix |
| **Sub-Agent Delegation** | ~12 | 7-row delegation matrix with primary/verification agent pairings |
| **Escape Hatches** | ~18 | Escape hatch table, usage guidance |
| **Success Metrics** | ~12 | 7 metrics with targets and measurement methods |
| **Migration Details** | ~20 | Detailed v1.x and task-mcp migration examples |
| **Version History** | ~4 | Version changelog |
| **Verification Flags** (separate section) | ~8 | Collapsed into single row in execution control table |

### What Replaced It

| New Section | Lines | Purpose |
|-------------|-------|---------|
| **Activation** | 5 | Mandatory skill invocation directive pointing to `sc:task-unified-protocol` |
| **Behavioral Summary** | 2 | Single-paragraph summary of the full behavioral flow |
| **Compact Examples** | 12 | 6 usage examples collapsed from verbose multi-block format |
| **Compact Boundaries** | 4 | Will/Will Not collapsed from two tables to two lines |
| **Compact Migration** | 1 | Single deprecation notice line |

### Why This Changed

This is the **command-to-skill extraction pattern** applied at maximum scale. The rationale:

1. **Separation of concerns**: The command file (slash command definition) was carrying the entire protocol specification. This violated the emerging architecture where commands are lightweight invocation points and skills contain the behavioral protocol.

2. **Token efficiency**: A 567-line command file consumes significant context when loaded. The new 106-line version loads quickly and defers the heavy protocol to the skill, which is loaded on-demand.

3. **Skill protocol pattern**: The new `## Activation` section establishes a mandatory handoff: the command file provides syntax/flags/examples, then explicitly invokes the `sc:task-unified-protocol` skill for execution. This matches the pattern applied to all other rewritten commands (adversarial, cleanup-audit, roadmap, validate-tests).

4. **Flag table consolidation**: The separate `### Verification Flags` table was collapsed into a single row (`--verify [critical|standard|skip|auto]`) in the Execution Control Flags table, reducing redundancy.

5. **Heading simplification**: `"Strategy Flags (Orchestration Dimension)"` became `"Strategy Flags"` and `"Compliance Flags (Quality Dimension)"` became `"Compliance Flags"` -- removing parenthetical jargon.

### Breaking Changes and Behavioral Shifts

| Change | Impact | Severity |
|--------|--------|----------|
| Entire tier classification algorithm removed from command | Claude must now load the skill to know HOW to classify tiers | **HIGH** - if skill fails to load, command has no behavioral spec |
| All checklists removed | STRICT/STANDARD checklists no longer inline | **HIGH** - protocol execution depends entirely on skill |
| MCP server selection matrix removed | Server routing logic no longer in command | **MEDIUM** - global COMMANDS.md still has some routing info |
| Sub-agent delegation matrix removed | Agent selection no longer in command | **MEDIUM** - must come from skill |
| Escape hatch guidance removed | Users lose inline "when to use" guidance | **LOW** - flags still listed, just no explanatory text |
| Success metrics removed | No inline quality targets | **LOW** - operational detail, not user-facing |
| Mandatory skill invocation added | New `## Activation` section requires skill load | **ARCHITECTURAL** - establishes hard dependency on skill system |

### Relationship to `src/superclaude/commands/task-unified.md`

The `src/superclaude/commands/task-unified.md` file has **identical changes** (same diff). Both files are index `edd398e..7d604e5`. This confirms the sync rule: `.claude/commands/sc/` and `src/superclaude/commands/` contain the same content, with `src/` being the source of truth.

### Relationship to Skill: `src/superclaude/skills/sc-task-unified-protocol/`

The skill directory was **renamed** from `sc-task-unified` to `sc-task-unified-protocol` (visible in git status as `RM` rename+modify). The skill's `SKILL.md` is the new home for all the extracted content (tier classification algorithm, compliance checklists, MCP integration matrix, sub-agent delegation, verification protocol). The skill directory contains:

- `SKILL.md` - Full behavioral protocol (modified during rename)
- `__init__.py` - Python package marker

---

## File 2: `.claude/commands/sc/validate-tests.md`

### Change Summary

| Metric | Value |
|--------|-------|
| Diff lines | 22 |
| Lines added | 10 |
| Lines modified | 2 |
| Classification | **MINOR ADDITION** - skill activation directive + path updates |

### Exact Diff

```diff
@@ -95,8 +95,16 @@ BY CATEGORY
   ...
 ```

+## Activation
+
+**MANDATORY**: Before executing any protocol steps, invoke:
+> Skill sc:validate-tests-protocol
+
+Do NOT proceed with protocol execution using only this command file.
+The full behavioral specification (classification algorithm, test execution protocol, report generation) is in the protocol skill.
+
 ## See Also

 - `/sc:task` - Unified task command
-- `skills/sc-task-unified/SKILL.md` - Task skill definition
-- `skills/sc-validate-tests/SKILL.md` - Full validation skill spec
+- `skills/sc-task-unified-protocol/SKILL.md` - Task skill definition
+- `skills/sc-validate-tests-protocol/SKILL.md` - Full validation skill spec
```

### What Changed

Two discrete changes:

**1. New `## Activation` section added (lines 98-104)**

Inserted before the `## See Also` section, this adds the mandatory skill invocation directive:

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:validate-tests-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (classification algorithm, test execution protocol, report generation) is in the protocol skill.
```

**2. Skill path references updated in `## See Also` (lines 108-109)**

```
- skills/sc-task-unified/SKILL.md      -->  skills/sc-task-unified-protocol/SKILL.md
- skills/sc-validate-tests/SKILL.md    -->  skills/sc-validate-tests-protocol/SKILL.md
```

### Why This Changed

1. **Skill activation pattern**: Consistent with the pattern applied to task-unified.md and all other rewritten commands. Every command that has a corresponding protocol skill now includes the mandatory activation directive.

2. **Path rename alignment**: The skill directories were renamed from `sc-<name>` to `sc-<name>-protocol` (e.g., `sc-validate-tests` to `sc-validate-tests-protocol`). The See Also references needed to track these renames.

3. **Unlike task-unified.md, no content was removed**: The validate-tests command was already relatively lean. It did not carry inline protocol specification, so the change is purely additive (activation section) and corrective (path updates).

### Breaking Changes and Behavioral Shifts

| Change | Impact | Severity |
|--------|--------|----------|
| Activation section added | Claude now expected to invoke skill before protocol execution | **MEDIUM** - new mandatory step |
| Skill paths updated | Old `sc-validate-tests` paths would be broken references | **LOW** - only affects cross-references in See Also |

### Relationship to `src/superclaude/commands/validate-tests.md`

Identical changes. Both files show the same diff (`0ef1bb3..4d99f33`), confirming proper sync between `.claude/commands/sc/` and `src/superclaude/commands/`.

### Relationship to Skill: `src/superclaude/skills/sc-validate-tests-protocol/`

The skill directory was renamed from `sc-validate-tests` to `sc-validate-tests-protocol`. Contents:

- `SKILL.md` - Full validation skill spec (modified during rename)
- `classification-algorithm.yaml` - Test classification algorithm
- `__init__.py` - Python package marker

---

## Cross-File Analysis

### The Command-Skill Extraction Pattern

Both files participate in the same architectural refactoring pattern being applied across all commands in this release:

```
BEFORE (v2.0):
  command.md = syntax + flags + examples + FULL behavioral protocol (inline)

AFTER (v2.01):
  command.md = syntax + flags + examples + Activation directive (lightweight)
  skill/SKILL.md = FULL behavioral protocol (loaded on-demand)
```

The extraction was **asymmetric** across commands:

| Command | Content Removed | Reason |
|---------|----------------|--------|
| `task-unified.md` | 461 lines (81%) | Carried entire tier classification engine, all checklists, MCP matrix, delegation tables |
| `validate-tests.md` | 0 lines | Was already lean; only needed activation directive and path fixes |

### Skill Directory Naming Convention Change

Both files reference the new `-protocol` suffix naming convention:

| Old Name | New Name |
|----------|----------|
| `sc-task-unified` | `sc-task-unified-protocol` |
| `sc-validate-tests` | `sc-validate-tests-protocol` |

This rename is consistent across all 5 skills being modified in this release (adversarial, cleanup-audit, roadmap, task-unified, validate-tests).

### Risk Assessment

**High Risk**: `task-unified.md` has a hard dependency on the `sc-task-unified-protocol` skill. If the skill system fails to load (e.g., install issue, path mismatch, skill not found), the command becomes a syntax reference with no behavioral guidance. The removed content (461 lines of tier classification algorithm, checklists, MCP routing) is not duplicated anywhere else in the command layer.

**Low Risk**: `validate-tests.md` changes are purely additive and corrective. No existing behavior was removed. The activation directive is a new constraint but does not break existing usage if the skill fails to load (the command still has its classification output format and examples).

### Rollback Considerations

- **task-unified.md**: Rollback would restore 461 lines of inline protocol specification. The skill would still exist but would be redundant with the command content. No data loss risk -- all removed content exists in git history at commit `edd398e`.
- **validate-tests.md**: Rollback would remove the activation section and revert skill paths. Simple revert with no side effects.
- **Both files**: Rollback must be paired with corresponding `src/superclaude/commands/` files to maintain sync invariant.
