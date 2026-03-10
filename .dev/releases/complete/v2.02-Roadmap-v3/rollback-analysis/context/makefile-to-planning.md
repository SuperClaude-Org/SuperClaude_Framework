# Context Linking: Makefile Changes to Dev Planning & Architecture Policy Origins

**Branch**: `feature/v2.01-Roadmap-V3`
**Analysis Date**: 2026-02-24
**Purpose**: Trace every Makefile change back to the policy section, tasklist task, or architecture decision that mandated it.

---

## 1. Change-to-Policy Origin Map

### 1.1 Removed: Skill-Skip Heuristic in `sync-dev` (-4 lines)

**What was removed**: Logic that stripped the `sc-` prefix from skill directory names and skipped syncing the skill if a matching command file existed. Specifically:

```bash
# REMOVED from sync-dev:
cmd_name=${skill_name#sc-};
if [ "$cmd_name" != "$skill_name" ] && [ -f "src/superclaude/commands/$cmd_name.md" ]; then
    continue;
fi;
```

**Policy origin**: `docs/architecture/command-skill-policy.md`, Section "Core Principle" and "Tiered Loading Architecture"

The policy establishes that commands and skills are complementary layers, not substitutes:

> "Commands are doors. Skills are rooms. Refs are drawers."

Under the old model, a skill like `sc-adversarial` was considered "served by" the `adversarial.md` command, so syncing the skill to `.claude/` was unnecessary. Under the new tiered model, commands are thin dispatchers (Tier 0) that explicitly delegate to protocol skills (Tier 1). Both must exist in `.claude/` for the activation chain to function.

**Policy section that obsoleted it**: "Tiered Loading Architecture" table (Tier 0 and Tier 1 are distinct components with separate loading mechanisms) and "Migration Checklist > Phase 3: Update Build System", which states:

> "1. Remove skip logic from `sync-dev` (Makefile lines 114-117)"

**Tasklist link**: This falls under Phase 3 of the `tasklist-P6.md` execution plan. The tasklist's "Source Snapshot" references the Makefile's `sync-dev` and `verify-sync` targets as prerequisites (checked in T01.02, R-002). The Phase 3 build system updates are driven by `command-skill-policy.md` but Phase 3 tasks were not individually decomposed in the tasklist (the tasklist focuses on the adversarial pipeline remediation sprint, not the build system changes).

---

### 1.2 Removed: Skill-Skip Heuristic in `verify-sync` (-5 lines)

**What was removed**: Same skip logic plus a user-facing skip message:

```bash
# REMOVED from verify-sync:
cmd_name=${name#sc-};
if [ "$cmd_name" != "$name" ] && [ -f "src/superclaude/commands/$cmd_name.md" ]; then
    echo "  ⏭️  $name (served by /sc:$cmd_name command)";
    continue;
fi;
```

**Policy origin**: Same as 1.1. Additionally, the policy's "CI Enforcement" section under `make verify-sync` explicitly states:

> "Updated to: Remove the 'served by command' skip message. Always check skill directories against `.claude/skills/`. Validate `-protocol` naming convention."

**Tasklist link**: Same as 1.1 (Phase 3, build system updates).

---

### 1.3 Added: `lint-architecture` Target (+113 lines)

**Policy origin**: `docs/architecture/command-skill-policy.md`, Section "CI Enforcement > `make lint-architecture`"

The policy mandates a `make lint-architecture` target and defines 10 specific checks. The Makefile implements 6 of those 10 (see Section 3 below for the gap analysis).

**Policy quote**:

> "Enforced by: `make lint-architecture` (CI)" -- document header

**Tasklist link**: `tasklist-P6.md` Phase 3 ("Update Build System") and Phase 4 ("Validate"). Specifically:
- T06.05 (R-022) references `make sync-dev && make verify-sync` as quality gates but does NOT reference `make lint-architecture` directly, which is a minor gap.
- The `command-skill-policy.md` Migration Checklist Phase 3 step 2 states: "Add `lint-architecture` target"
- The `command-skill-policy.md` Migration Checklist Phase 4 step 3 states: "`make lint-architecture` -- all 10 checks pass"

---

### 1.4 Added: `.PHONY` Update

**What changed**: `lint-architecture` added to the `.PHONY` declaration list.

**Policy origin**: Standard Makefile hygiene -- not explicitly mandated by the policy document, but required for correct Make behavior when adding a new target.

---

### 1.5 Added: `help` Target Update (+1 line)

**What changed**: `lint-architecture` added to the help text under "Component Sync" section.

**Policy origin**: Implicit -- the policy does not mandate help text, but the existing Makefile convention includes all targets in the help output.

---

## 2. The 6 Implemented Lint Checks: Policy Requirement Mapping

| Makefile Check | Policy Check # | Policy Rule | Severity |
|---|---|---|---|
| **Check 1**: Command -> Skill bidirectional link | Policy #1 | "Command with `## Activation` referencing a skill -> that skill directory MUST exist" | ERROR |
| **Check 2**: Skill -> Command bidirectional link | Policy #2 | "Skill directory matching `sc-*-protocol` -> command `<name>.md` MUST exist (strip `sc-` prefix and `-protocol` suffix)" | ERROR |
| **Check 3**: Command size limits (>500 = error, >200 = warn) | Policy #3 + #4 (combined) | "#3: Command file >200 lines" (WARN) and "#4: Command file >500 lines" (ERROR) | ERROR/WARN |
| **Check 4**: Activation section present | Policy #6 | "Command with matching `-protocol` skill directory missing `## Activation` section" | ERROR |
| **Check 5**: Skill frontmatter validation | Policy #8 | "SKILL.md missing `name`, `description`, or `allowed-tools` in frontmatter" | ERROR |
| **Check 6**: Protocol naming consistency | Policy #9 | "Skill directory `sc-*-protocol/` but SKILL.md `name` field doesn't end in `-protocol`" | ERROR |

**Policy source**: `docs/architecture/command-skill-policy.md`, Section "CI Enforcement > `make lint-architecture`", table rows #1 through #9.

---

## 3. Gap Analysis: Policy (10 Checks) vs Implementation (6 Checks)

The policy defines 10 CI checks. The Makefile implements 6. Four checks from the policy are NOT present in the Makefile:

| Policy # | Check Description | Severity | Why Missing | Status |
|---|---|---|---|---|
| **#5** | Inline protocol in command: command with matching `-protocol` skill contains YAML code blocks >20 lines | ERROR | Requires YAML block detection in markdown files -- more complex to implement in shell than simple grep/wc checks | NOT IMPLEMENTED |
| **#7** | Activation references correct skill: `## Activation` section does not contain `Skill sc:<name>-protocol` | ERROR | Partially covered by Check 1 (which extracts the skill reference), but Check 1 validates the directory exists, not that the reference matches the expected naming pattern | NOT IMPLEMENTED |
| **#10** | Sync integrity: files in `src/` not matching `.claude/` | ERROR | Already covered by the separate `make verify-sync` target. The policy labels this as a `lint-architecture` check, but the Makefile keeps it as a standalone target | DELEGATED to `verify-sync` |
| (implicit) | Policy #3 vs #4 are listed as two separate checks (WARN at 200, ERROR at 500), but the Makefile implements them as a single Check 3 with two thresholds | -- | Implementation combines two policy rows into one Makefile check | COMBINED |

**Net accounting**: Policy defines 10 checks. Makefile implements 6 explicit checks covering 8 of the 10 policy requirements (Checks #3/#4 are combined into one; Check #10 is delegated to `verify-sync`). Two policy checks (#5 inline YAML detection, #7 activation reference correctness) are genuinely missing.

**Implication for recreation**: If recreating from the policy spec, implementers should be aware that checks #5 and #7 were intentionally or inadvertently deferred. The policy's Migration Checklist Phase 4 expects "all 10 checks pass," which cannot be validated against a 6-check implementation.

---

## 4. Agent Analysis Discrepancy: `lint-architecture` "Not Yet Implemented"

The `dev-planning-synthesis-A.md` (Section 4, "CI Enforcement") states:

> "10 automated checks are defined under a `make lint-architecture` target (not yet implemented in the Makefile)."

And further in Section 4 ("Migration Status"):

> "Phase 3 (Build system): NOT STARTED -- `lint-architecture` target does not exist yet"

**This assessment is incorrect.** The git diff from commit `5733e32` to HEAD clearly shows the `lint-architecture` target was added (+113 lines). The target IS present in the current Makefile (lines 233-343).

**Explanation for the discrepancy**: The dev-planning synthesis was produced by analysis agents reading the `command-skill-policy.md` policy document and the tasklist, NOT the actual Makefile diff. The policy document's own "Migration Status" section (if it was written before the Makefile changes were committed) would correctly state "NOT STARTED" at the time of authoring. The analysis agents appear to have trusted the policy document's self-reported migration status rather than verifying against the actual branch state.

The framework-synthesis documents (`framework-synthesis-A.md` and `framework-synthesis-B.md`) correctly identify the `lint-architecture` target as present, with full check-by-check documentation. This is because those syntheses were produced from the actual file diff batches, not from the planning documents.

---

## 5. Tasklist Tasks Requiring Makefile Changes

### Direct Makefile Dependencies

| Task | Roadmap Item | Makefile Relevance |
|---|---|---|
| **T01.02** (Prerequisite Validation) | R-002 | Verifies `make sync-dev` and `make verify-sync` targets exist and function. Does not modify the Makefile. |
| **T06.05** (Sync and Quality Gates) | R-022 | Runs `make sync-dev && make verify-sync` as acceptance gate. Depends on the heuristic removal being in place for protocol skills to sync correctly. |

### Implicit Makefile Dependencies (via policy)

The entire Phase 3 of the `command-skill-policy.md` Migration Checklist drives Makefile changes, but the `tasklist-P6.md` does not decompose Phase 3 into individual tasks. Phase 3 is referenced in the policy's dependency graph:

```
command-skill-policy.md (POLICY)
    +-- Drives --> Makefile updates (Phase 3, NOT STARTED)   [per policy self-report]
    +-- Drives --> CI validation (Phase 4, BLOCKED)          [per policy self-report]
```

In practice, the Makefile changes WERE implemented (as the diff proves), but they were not tracked as tasklist tasks. This suggests the Makefile changes were either:
1. Implemented outside the formal tasklist tracking, or
2. Implemented as part of a different work stream that was not captured in `tasklist-P6.md`

---

## 6. `sync-dev` and `verify-sync` Changes and the `-protocol` Naming Convention

### The Relationship

The skill-skip heuristic in the old `sync-dev` and `verify-sync` used this logic:

```
skill directory name (e.g., "sc-adversarial")
    -> strip "sc-" prefix -> "adversarial"
    -> check if "adversarial.md" exists in commands/
    -> if yes, skip the skill (it's "served by" the command)
```

Under the `-protocol` naming convention, this logic produces different behavior:

```
skill directory name: "sc-adversarial-protocol"
    -> strip "sc-" prefix -> "adversarial-protocol"
    -> check if "adversarial-protocol.md" exists in commands/
    -> NO (command is "adversarial.md", not "adversarial-protocol.md")
    -> skill would NOT be skipped (heuristic does not trigger)
```

**Key insight**: The `-protocol` suffix in the new naming convention happens to break the old heuristic naturally -- even without removing the skip logic, the renamed skills would sync correctly because the name no longer matches any command file after prefix stripping. However, the heuristic was removed anyway because:

1. **Correctness**: The heuristic's conceptual model ("skills served by commands") is incompatible with the new architecture ("commands delegate to skills").
2. **Future-proofing**: If a skill were named `sc-foo` (without `-protocol`) and a `foo.md` command existed, the old heuristic would incorrectly skip syncing it.
3. **Policy mandate**: The `command-skill-policy.md` explicitly lists "Remove skip logic from `sync-dev`" in its Migration Checklist Phase 3.

### Cross-Reference to `-protocol` Convention Origin

The `-protocol` suffix convention is defined in `command-skill-policy.md`, Section "Naming Convention":

> "Protocol skills MUST end in `-protocol`"
> "Protocol skill directories MUST be prefixed with `sc-` and suffixed with `-protocol`"

The rationale (from the Decision Log):

> "`-protocol` suffix convention: Clear semantic signal, easy to lint, no ambiguity" (2026-02-23)

And from `framework-synthesis-A.md`, Section 4.4:

> "The suffix distinguishes skill packages that contain behavioral protocol definitions (loaded by commands via `## Activation`) from other skill types that may exist in the future. It establishes a naming convention enforced by `make lint-architecture` Check 6."

---

## 7. Summary: Complete Traceability Chain

```
docs/architecture/command-skill-policy.md
    |
    +-- Section "Core Principle" (Commands are doors, Skills are rooms)
    |       -> Obsoletes skill-skip heuristic conceptual model
    |       -> Drives removal of 9 lines from sync-dev + verify-sync
    |
    +-- Section "Naming Convention" (-protocol suffix)
    |       -> Drives lint-architecture Check 6 (naming consistency)
    |       -> Makes old heuristic behaviorally irrelevant (even before removal)
    |
    +-- Section "CI Enforcement" (10 checks defined)
    |       -> Drives lint-architecture target creation (113 lines added)
    |       -> 6 of 10 checks implemented; 2 delegated/combined; 2 deferred
    |
    +-- Section "Migration Checklist > Phase 3"
    |       -> "Remove skip logic from sync-dev"         -> DONE
    |       -> "Add lint-architecture target"             -> DONE (6/10 checks)
    |       -> "Update verify-sync to remove skip"        -> DONE
    |
    +-- Section "Migration Checklist > Phase 4"
            -> "make lint-architecture -- all 10 checks pass"  -> PARTIAL (6 checks)

tasklist-P6.md
    |
    +-- T01.02 (R-002): Prerequisite validation (reads sync-dev/verify-sync)
    +-- T06.05 (R-022): Runs sync-dev + verify-sync as quality gate
    +-- Phase 3 tasks: NOT decomposed in tasklist (Makefile changes not tracked)

dev-planning-synthesis-A.md
    |
    +-- Reports lint-architecture as "not yet implemented"  -> INCORRECT
    +-- Reports Phase 3 as "NOT STARTED"                    -> INCORRECT
    +-- (Based on policy self-report, not actual diff verification)

framework-synthesis-A.md / framework-synthesis-B.md
    |
    +-- Correctly identify all Makefile changes from diff
    +-- Document all 6 checks with pass/fail behavior
    +-- Note the 10-vs-6 check gap is implicit (not flagged)
```
