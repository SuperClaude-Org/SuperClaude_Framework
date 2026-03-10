# Batch 4 - Source Commands (Part 2): task-unified.md & validate-tests.md

## Rollback-Recreation Analysis

**Analyzed**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3`
**Compared against**: `HEAD` (commit `9060a65`)

---

## File 1: `src/superclaude/commands/task-unified.md`

### Change Magnitude

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Total lines | 567 | 106 | -461 (81% reduction) |
| Diff lines | ~499 | - | - |
| Sections removed | 15+ | - | - |
| Sections added | 2 | - | - |

This is the single largest change in the batch -- the file was reduced to roughly one-fifth of its original size.

### Full Diff (with line-number context)

```diff
--- a/src/superclaude/commands/task-unified.md
+++ b/src/superclaude/commands/task-unified.md
@@ -25,61 +25,13 @@
 **Philosophy**: "Better false positives than false negatives" ...

-## Triggers                                          # REMOVED: entire section (~48 lines)
-### Auto-Activation Patterns                         #   - table of 5 trigger types
-### Keyword Triggers                                 #   - YAML block with explicit/auto-suggest keywords
-### Context Signals                                  #   - prose list of suggestion conditions

 ## Usage                                             # KEPT but simplified
-### Strategy Flags (Orchestration Dimension)          # Renamed → "### Strategy Flags"
+### Strategy Flags                                   # Parenthetical "(Orchestration Dimension)" dropped

-### Compliance Flags (Quality Dimension)              # Renamed → "### Compliance Flags"
+### Compliance Flags                                 # Parenthetical "(Quality Dimension)" dropped

-### Verification Flags                               # REMOVED: standalone section (4-row table)
+| `--verify [critical|standard|skip|auto]` | ...    # Collapsed into Execution Control Flags table

-## Behavioral Flow                                   # REMOVED: 7-step numbered list
-## Tiered Compliance Model                           # REMOVED: entire section (~200 lines)
-  ### TIER 1: STRICT                                 #   - SMART criteria, mandatory checklist (full markdown)
-  ### TIER 2: STANDARD                               #   - SMART criteria, required checklist
-  ### TIER 3: LIGHT                                  #   - SMART criteria, guidance
-  ### TIER 4: EXEMPT                                 #   - SMART criteria, behavior note
-## Auto-Detection Algorithm                          # REMOVED: YAML spec (~60 lines)
-  ### Compound Phrase Handling                        #   - YAML compound-phrase overrides
-## MCP Integration                                   # REMOVED: server matrix + persona YAML (~45 lines)
-## Tool Coordination                                 # REMOVED: tool table + tier-specific table (~25 lines)
-## Sub-Agent Delegation Matrix                       # REMOVED: 7-row delegation table
-## Escape Hatches                                    # REMOVED: table + guidance prose
-## Success Metrics                                   # REMOVED: 7-row metrics table
-## Migration from Legacy Commands                    # REMOVED: before/after examples + deprecation
-## Version History                                   # REMOVED

+## Activation                                        # NEW SECTION (lines 86-92)
+  MANDATORY: invoke Skill sc:task-unified-protocol
+## Behavioral Summary                                # NEW SECTION (line 94-96) - 1 paragraph
+## Boundaries                                        # KEPT but collapsed: 2 tables → 2 inline lists
+## Migration                                         # KEPT but trimmed to 1 line
```

### What Was Removed (Detailed Inventory)

1. **Triggers section** (lines 28-75 in old file)
   - Auto-Activation Patterns table (5 rows: complexity, multi-file, security, refactoring, test remediation)
   - Keyword Triggers YAML block (explicit invocation patterns + auto-suggest with confidence tiers)
   - Context Signals prose (5 bullet points)

2. **Behavioral Flow** (old lines ~110-118)
   - 7-step numbered flow: Analyze -> Classify -> Display -> Delegate -> Execute -> Verify -> Report

3. **Tiered Compliance Model** (~200 lines, old lines ~120-340)
   - TIER 1: STRICT -- SMART acceptance criteria, full pre-work checklist (6 categories, ~40 checkbox items), post-task "Did I?" checklist (6 items)
   - TIER 2: STANDARD -- SMART criteria, 6-item checklist, quick validation
   - TIER 3: LIGHT -- SMART criteria, guidance prose
   - TIER 4: EXEMPT -- SMART criteria, behavior note

4. **Auto-Detection Algorithm** (~80 lines, old lines ~340-430)
   - YAML specification with strict/exempt/light/standard trigger definitions
   - Keyword lists per tier, path patterns, file count thresholds, complexity scores
   - Priority order and fallback rules
   - Compound phrase handling YAML (light_wins + strict_wins overrides)

5. **MCP Integration** (~45 lines)
   - Server Selection Matrix table (6 servers, always-active vs conditional)
   - Persona Coordination YAML (core + domain + verification personas)

6. **Tool Coordination** (~25 lines)
   - Tool purpose/usage table (7 tools)
   - Tier-Specific Tool Usage table (required vs optional per tier)

7. **Sub-Agent Delegation Matrix** (~15 lines)
   - 7-row table mapping task types to primary + verification agents

8. **Escape Hatches** (~20 lines)
   - 4-row escape hatch table + "when to use" guidance

9. **Success Metrics** (~12 lines)
   - 7-row metrics/targets table

10. **Migration from Legacy Commands** (~20 lines)
    - Before/after examples for `/sc:task` v1.x and `/sc:task-mcp`
    - Deprecation notice with migration assistance

11. **Version History** (~4 lines)

### What Was Added

1. **Activation section** (lines 86-92 in new file)
   ```markdown
   ## Activation

   **MANDATORY**: Before executing any protocol steps, invoke:
   > Skill sc:task-unified-protocol

   Do NOT proceed with protocol execution using only this command file.
   The full behavioral specification (tier classification algorithm, compliance
   checklists, MCP integration, sub-agent delegation, verification protocol)
   is in the protocol skill.
   ```

2. **Behavioral Summary** (line 94-96) -- single paragraph condensing the removed behavioral flow + tier model into a one-sentence description.

3. **Consolidated `--verify` flag** (line 61) -- the standalone Verification Flags section was collapsed into a single row in the Execution Control Flags table:
   ```
   | `--verify [critical|standard|skip|auto]` | Verification level |
   ```

### What Was Kept (Modified)

1. **Frontmatter** (lines 1-9): Unchanged.
2. **Purpose section** (lines 11-26): Unchanged.
3. **Usage / Strategy Flags / Compliance Flags / Execution Control Flags**: Tables preserved; parenthetical labels removed from headings.
4. **Examples section**: Collapsed from 5 separate code blocks with explanatory comments into a single fenced block with inline comments.
5. **Boundaries section**: Two tables ("Will" with 8 rows, "Will Not" with 8 rows) collapsed into two inline sentences.
6. **Migration section**: Trimmed from multi-block migration guide to single deprecation line.

### WHY These Changes Were Made

The changes implement the **command-skill separation pattern** (documented in `docs/architecture/command-skill-policy.md`). The rationale:

1. **Token budget**: The old 567-line file was loaded into context on every `/sc:task` invocation. Most of that content (tier algorithms, checklists, YAML specs) is only needed during execution, not during command parsing. Moving it to a skill that is loaded on-demand saves ~460 lines of context per invocation.

2. **Single responsibility**: The command file now serves as a lightweight **interface definition** (flags, usage, examples) while the skill (`sc-task-unified-protocol/SKILL.md`) contains the **behavioral implementation** (algorithms, checklists, MCP coordination).

3. **Skill invocation pattern**: The new `## Activation` section establishes the mandatory handoff: the command file tells Claude "invoke the skill before proceeding." This prevents Claude from trying to execute the protocol using only the abbreviated command file.

4. **Consistency**: All five modified commands in this release (adversarial, cleanup-audit, roadmap, task-unified, validate-tests) follow the same pattern of extracting protocol details into `-protocol` suffixed skills.

### Structure Comparison

**Before (567 lines)**:
```
Frontmatter → Purpose → Triggers → Usage/Flags → Behavioral Flow →
Tiered Compliance (STRICT/STANDARD/LIGHT/EXEMPT with full checklists) →
Auto-Detection Algorithm (YAML) → Compound Phrases → MCP Integration →
Tool Coordination → Sub-Agent Delegation → Escape Hatches →
Success Metrics → Examples → Boundaries (Will/Will Not tables) →
Migration (with examples) → Version History
```

**After (106 lines)**:
```
Frontmatter → Purpose → Usage/Flags (simplified) → Examples (condensed) →
Activation (MANDATORY skill invocation) → Behavioral Summary (1 paragraph) →
Boundaries (inline) → Migration (1 line)
```

### Relationship to `.claude/commands/sc/task-unified.md`

The diff for `.claude/commands/sc/task-unified.md` is **identical** to the `src/superclaude/commands/task-unified.md` diff. Both files were at the same content before (index `edd398e`) and after (index `7d604e5`). This confirms `make sync-dev` was run (or both were edited in sync). The files are byte-for-byte identical.

---

## File 2: `src/superclaude/commands/validate-tests.md`

### Change Magnitude

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Total lines | 102 | 110 | +8 |
| Lines added | 10 | - | - |
| Lines modified | 2 | - | - |

This is a minor additive change -- no content was removed, only added and updated.

### Full Diff (with line numbers)

```diff
--- a/src/superclaude/commands/validate-tests.md
+++ b/src/superclaude/commands/validate-tests.md
@@ -95,8 +95,16 @@ BY CATEGORY
   ...
 ```

+## Activation                                         # NEW: lines 98-104
+
+**MANDATORY**: Before executing any protocol steps, invoke:
+> Skill sc:validate-tests-protocol
+
+Do NOT proceed with protocol execution using only this command file.
+The full behavioral specification (classification algorithm, test execution
+protocol, report generation) is in the protocol skill.
+
 ## See Also

 - `/sc:task` - Unified task command
-- `skills/sc-task-unified/SKILL.md` - Task skill definition
-- `skills/sc-validate-tests/SKILL.md` - Full validation skill spec
+- `skills/sc-task-unified-protocol/SKILL.md` - Task skill definition     # path updated
+- `skills/sc-validate-tests-protocol/SKILL.md` - Full validation skill spec  # path updated
```

### What Changed

1. **New `## Activation` section** inserted between `Report Format` and `See Also` (lines 98-104):
   - Identical pattern to the other four modified commands
   - Points to `sc:validate-tests-protocol` skill
   - Lists the behavioral content that lives in the skill: classification algorithm, test execution protocol, report generation

2. **Updated `## See Also` cross-references** (lines 108-110):
   - `skills/sc-task-unified/SKILL.md` changed to `skills/sc-task-unified-protocol/SKILL.md`
   - `skills/sc-validate-tests/SKILL.md` changed to `skills/sc-validate-tests-protocol/SKILL.md`

### What Was NOT Changed

The entire existing content (lines 1-96) is preserved:
- Usage, Arguments, Flags tables
- Examples block
- Behavior steps (Load/Execute/Compare/Report)
- Test Categories table (7 categories, 300 total tests)
- Classification Algorithm reference and phases
- Report Format example block

### WHY These Changes Were Made

1. **Skill invocation directive**: The `## Activation` section ensures Claude loads the full protocol skill before attempting to run test validation. Without this, Claude might try to execute the classification algorithm described in the command file without loading the detailed YAML specification from the skill.

2. **Path updates for skill renames**: The skills were renamed from `sc-task-unified` to `sc-task-unified-protocol` and from `sc-validate-tests` to `sc-validate-tests-protocol` as part of the broader `-protocol` suffix convention. The See Also references needed to track these renames.

3. **Minimal disruption**: Unlike `task-unified.md` which had massive protocol content to extract, `validate-tests.md` was already relatively lean (102 lines). The protocol details were already mostly in the skill. Only the activation directive and path updates were needed.

### Relationship to `.claude/commands/sc/validate-tests.md`

The diff for `.claude/commands/sc/validate-tests.md` is **identical** to the source version. Both files moved from index `0ef1bb3` to `4d99f33`. They are byte-for-byte identical, confirming sync.

---

## Cross-File Analysis

### Pattern: Command-Skill Separation

Both files implement the same architectural pattern but at very different scales:

| Aspect | task-unified.md | validate-tests.md |
|--------|----------------|-------------------|
| Content extracted to skill | ~461 lines (81%) | 0 lines (already extracted) |
| New activation section | Yes | Yes |
| Path references updated | N/A (no cross-refs) | 2 paths updated |
| Net line change | -461 | +8 |
| Structural disruption | Major rewrite | Minor addition |

### Rollback Considerations

**task-unified.md**: Rolling back restores 461 lines of inline protocol content. The skill `sc-task-unified-protocol/SKILL.md` would need to be checked -- if it duplicates this content, both copies would exist. If the skill was created from the extracted content, rolling back would mean the content exists in both the command file AND the skill, creating a maintenance burden.

**validate-tests.md**: Rolling back removes the activation directive and reverts the skill paths to non-`-protocol` suffixed names. This would cause broken cross-references if the skill directories have already been renamed (which they have, per the git status showing `R` renames).

### Dependency Chain

```
src/superclaude/commands/task-unified.md
  ├── references → skills/sc-task-unified-protocol/SKILL.md (via Activation)
  └── synced to → .claude/commands/sc/task-unified.md (identical)

src/superclaude/commands/validate-tests.md
  ├── references → skills/sc-validate-tests-protocol/SKILL.md (via Activation)
  ├── references → skills/sc-task-unified-protocol/SKILL.md (via See Also)
  └── synced to → .claude/commands/sc/validate-tests.md (identical)
```

Rolling back either file without also rolling back the skill renames (`sc-*` to `sc-*-protocol`) would produce broken references.
