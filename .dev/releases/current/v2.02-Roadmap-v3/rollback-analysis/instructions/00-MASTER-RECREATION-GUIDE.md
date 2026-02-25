# 00-MASTER-RECREATION-GUIDE: Complete Rollback and Recreation Procedure

**Version**: 1.0.0
**Date**: 2026-02-24
**Branch**: `feature/v2.01-Roadmap-V3`
**Base Commit**: `9060a65` (this IS the current HEAD; all changes are uncommitted)
**Source Documents**: 6 synthesis files, 5 context-linking documents, 1 master traceability matrix

---

## Table of Contents

4. [Execution Order](#4-execution-order-phased-recreation)
5. [Known Bugs to Fix During Recreation](#5-known-bugs-to-fix-during-recreation)
6. [Post-Recreation Validation](#6-post-recreation-validation)
7. [Remaining Work](#7-remaining-work-phases-3-6)

---


---

### Phase C: Execute Skill Renames

**Purpose**: Rename 5 skill directories from `sc-{name}` to `sc-{name}-protocol` and update SKILL.md frontmatter.
**Instruction file reference**: Instruction 01 (skill renames).
**Total files affected**: 30 (5 SKILL.md modified + 25 companion pure renames).
**Dependencies**: None (foundation layer).

**Step C.1: Rename directories**

```bash
git mv src/superclaude/skills/sc-adversarial src/superclaude/skills/sc-adversarial-protocol
git mv src/superclaude/skills/sc-cleanup-audit src/superclaude/skills/sc-cleanup-audit-protocol
git mv src/superclaude/skills/sc-roadmap src/superclaude/skills/sc-roadmap-protocol
git mv src/superclaude/skills/sc-task-unified src/superclaude/skills/sc-task-unified-protocol
git mv src/superclaude/skills/sc-validate-tests src/superclaude/skills/sc-validate-tests-protocol
```

**Step C.2: Update SKILL.md frontmatter `name` fields**

| Skill | Old `name` Value | New `name` Value |
|-------|-----------------|-----------------|
| adversarial | `sc:adversarial` | `sc:adversarial-protocol` |
| cleanup-audit | `cleanup-audit` | `sc:cleanup-audit-protocol` |
| roadmap | `sc:roadmap` | `sc:roadmap-protocol` |
| task-unified | `sc-task-unified` | `sc:task-unified-protocol` |
| validate-tests | `sc-validate-tests` | `sc:validate-tests-protocol` |

Note: cleanup-audit gains the missing `sc:` prefix. task-unified and validate-tests change hyphens to colons.

**Step C.3: Roadmap SKILL.md additional changes** (the ONLY skill with body changes)

In `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`:

1. Add `Skill` to the `allowed-tools` frontmatter field
2. Expand Wave 2 Step 3 into sub-steps 3a through 3f per D-0006 specification:
   - 3a: Parse agents
   - 3b: Expand variants
   - 3c: Add orchestrator (use threshold `>= 3`, NOT `>= 5` -- see BUG-003)
   - 3d: Execute fallback protocol (F1, F2/3, F4/5 per D-0007)
   - 3e: Consume return contract (missing-file guard, YAML error handling, 3-status routing, convergence threshold 0.6 per D-0008)
   - 3f: Skip template

**Step C.4: Fix BUG-003 (orchestrator threshold) during recreation**

Ensure the orchestrator threshold is consistent throughout the SKILL.md. D-0006 specifies `>= 3`. The old Section 5 "Agent Count Rules" says `>= 5`. Align both to `>= 3` (the D-0006 value).

**Step C.5: Fix BUG-005 (stale adversarial path) during recreation**

In the roadmap SKILL.md Wave 0 step 5, update the adversarial reference path:
- OLD: `src/superclaude/skills/sc-adversarial/SKILL.md`
- NEW: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`

**Verification**:
```bash
# Confirm all 5 directories renamed
ls src/superclaude/skills/ | grep protocol
# Expected: 5 directories ending in -protocol

# Confirm no old directories remain
ls src/superclaude/skills/ | grep -v protocol | grep "^sc-"
# Expected: no output

# Confirm frontmatter names
for d in src/superclaude/skills/sc-*-protocol/SKILL.md; do
  echo "=== $d ==="
  head -5 "$d" | grep "name:"
done
# Expected: All use sc:{name}-protocol format with colon prefix
```

---

### Phase D: Execute Command Updates

**Purpose**: Add `## Activation` sections to all 5 commands, extract content from task-unified.md.
**Instruction file reference**: Instruction 02 (command updates).
**Total files affected**: 5 in `src/superclaude/commands/` (`.claude/` copies handled by Phase F).
**Dependencies**: Phase C must be complete (commands reference `-protocol` skill names).

**Step D.1: adversarial.md** (+8 lines)

Insert `## Activation` section (after Options table, before any Behavioral Summary):
```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:adversarial-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (adversarial debate protocol) is in the protocol skill.
```

**BUG-001 Fix**: Also add `Skill` to the `allowed-tools` frontmatter (or add an `allowed-tools` field if only `mcp-servers` exists).

**Step D.2: cleanup-audit.md** (+8 lines)

Insert `## Activation` section (after Arguments, before Behavioral Summary):
```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:cleanup-audit-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification (multi-pass audit protocol) is in the protocol skill.
```

**BUG-001 Fix**: Add `Skill` to `allowed-tools` (or add the field).

**Step D.3: roadmap.md** (+3 net lines)

- Add `Skill` to `allowed-tools` frontmatter (already done in original -- replicate)
- Rewrite `## Activation` section from file-path loading to skill invocation:
```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:roadmap-protocol

Do NOT proceed with protocol execution using only this command file.
```

**Step D.4: task-unified.md** (-461 net lines -- MAJOR REWRITE)

This is the largest and riskiest change. Reduce from ~567 to ~106 lines by extracting:
- Triggers section (~60 lines)
- Behavioral Flow (~8 lines)
- Tiered Compliance Model (~200 lines)
- Auto-Detection Algorithm (~80 lines)
- MCP Integration (~45 lines)
- Tool Coordination (~25 lines)
- Sub-Agent Delegation Matrix (~15 lines)
- Escape Hatches (~20 lines)
- Success Metrics (~12 lines)
- Detailed examples (~20 lines)
- Version History (~4 lines)

**Keep**: Frontmatter, flag tables (simplified), compact examples (6 inline), boundaries (2 sentences), `## Activation` section, `## Behavioral Summary` (1 paragraph).

**BUG-001 Fix**: Add `Skill` to `allowed-tools` frontmatter.

**CRITICAL VALIDATION**: After extraction, verify that the full behavioral content exists in `src/superclaude/skills/sc-task-unified-protocol/SKILL.md`. The skill must contain the complete tier classification engine, compliance checklists, and all extracted content. If the skill is incomplete, the command becomes non-functional.

**Step D.5: validate-tests.md** (+8 net lines)

- Insert `## Activation` section (before See Also)
- Update See Also paths: `sc-task-unified` -> `sc-task-unified-protocol`, `sc-validate-tests` -> `sc-validate-tests-protocol`

**BUG-001 Fix**: Add `Skill` to `allowed-tools` (or add the field).

**BUG-002 Fix**: Update the stale path on line 63:
- OLD: `Reference: skills/sc-validate-tests/classification-algorithm.yaml`
- NEW: `Reference: skills/sc-validate-tests-protocol/classification-algorithm.yaml`

**Verification**:
```bash
# Confirm all 5 commands have Activation sections
for f in src/superclaude/commands/{adversarial,cleanup-audit,roadmap,task-unified,validate-tests}.md; do
  echo "=== $f ==="
  grep -c "## Activation" "$f"
done
# Expected: 1 for each file

# Confirm task-unified.md is under 200 lines
wc -l src/superclaude/commands/task-unified.md
# Expected: ~106 lines

# Confirm all commands have Skill in allowed-tools (BUG-001 fix)
for f in src/superclaude/commands/{adversarial,cleanup-audit,roadmap,task-unified,validate-tests}.md; do
  echo "=== $f ==="
  grep -i "skill" "$f" | head -3
done
```

---

### Phase E: Execute Makefile Updates

**Purpose**: Remove old sync heuristic, add `lint-architecture` CI target.
**Instruction file reference**: Instruction 03 (Makefile changes).
**Dependencies**: Phase C naming convention must be in place.

**Step E.1: Remove skill-skip heuristic from `sync-dev`** (-4 lines)

Remove the logic that strips the `sc-` prefix and skips skills matching a command:
```bash
# REMOVE these lines from the sync-dev target:
cmd_name=${skill_name#sc-};
if [ "$cmd_name" != "$skill_name" ] && [ -f "src/superclaude/commands/$cmd_name.md" ]; then
    continue;
fi;
```

**Step E.2: Remove skill-skip heuristic from `verify-sync`** (-5 lines)

Remove the same skip logic plus the user-facing skip message:
```bash
# REMOVE these lines from the verify-sync target:
cmd_name=${name#sc-};
if [ "$cmd_name" != "$name" ] && [ -f "src/superclaude/commands/$cmd_name.md" ]; then
    echo "  ⏭️  $name (served by /sc:$cmd_name command)";
    continue;
fi;
```

**Step E.3: Add `lint-architecture` target** (+113 lines)

Add the new Makefile target implementing 6 CI checks:

| Check | Policy # | What It Validates | Severity |
|-------|----------|-------------------|----------|
| 1 | #1 | Command `## Activation` -> skill directory exists | ERROR |
| 2 | #2 | Skill `sc-*-protocol/` -> matching command exists | ERROR |
| 3 | #3 + #4 | Command size: >500 = ERROR, >200 = WARN | ERROR/WARN |
| 4 | #6 | Paired command has `## Activation` section | ERROR |
| 5 | #8 | SKILL.md has `name`, `description`, `allowed-tools` | ERROR |
| 6 | #9 | Skill directory `-protocol` matches SKILL.md `name` `-protocol` | ERROR |

**Step E.4: Add `lint-architecture` to `.PHONY` and `help`**

**Verification**:
```bash
# Confirm heuristic removed from sync-dev
grep -c "served by" Makefile
# Expected: 0

# Confirm lint-architecture target exists
grep -c "lint-architecture:" Makefile
# Expected: 1 (the target definition)

# Confirm .PHONY includes lint-architecture
grep "\.PHONY" Makefile | grep -c "lint-architecture"
# Expected: 1
```

---

### Phase F: Run `make sync-dev` + `make verify-sync`

**Purpose**: Create `.claude/` dev copies and verify parity.
**Dependencies**: Phases C, D, and E must all be complete.

```bash
# Step F.1: Sync src/ to .claude/
make sync-dev

# Step F.2: Verify parity
make verify-sync
# Expected: PASS for all 10 component pairs (5 commands + 5 skills)

# Step F.3: Verify .claude/ skills exist
ls .claude/skills/ | grep protocol
# Expected: 5 directories ending in -protocol

# Step F.4: Verify .claude/ commands are identical to src/
for cmd in adversarial cleanup-audit roadmap task-unified validate-tests; do
  diff "src/superclaude/commands/$cmd.md" ".claude/commands/sc/$cmd.md" && echo "$cmd: IDENTICAL" || echo "$cmd: MISMATCH"
done
```

---

### Phase G: Run `make lint-architecture`

**Purpose**: Validate all conventions are met.
**Dependencies**: Phase F must be complete.

```bash
make lint-architecture
# Expected: 0 errors, 0 warnings (if all bugs fixed)
# Acceptable: 0 errors, potential warnings for commands between 150-200 lines
```

**Expected check results**:

| Check | Expected Result |
|-------|-----------------|
| 1: Command -> Skill link | PASS (all 5 skills exist) |
| 2: Skill -> Command link | PASS (all 5 commands exist) |
| 3: Command size | PASS (all under 200) or WARN (if any 150-200) |
| 4: Activation section | PASS (all 5 commands have it) |
| 5: SKILL.md frontmatter | PASS (all have name, description, allowed-tools) |
| 6: Protocol naming | PASS (all directories and names use -protocol) |

---

## 5. Known Bugs to Fix During Recreation

### BUG-001: `allowed-tools` Inconsistency (4 of 5 Commands Missing `Skill`)

**Severity**: HIGH
**Found by**: Framework Synthesis A (Section 5.3), Framework Synthesis B (Section 3.1)
**Confirmed by**: Both independent analysis agents

**Description**: All 5 commands include `## Activation` sections invoking `> Skill sc:{name}-protocol`, but only `roadmap.md` added `Skill` to its `allowed-tools` frontmatter. The other 4 commands (`adversarial.md`, `cleanup-audit.md`, `task-unified.md`, `validate-tests.md`) did NOT add `Skill`.

**Affected Files** (8 total, 4 commands x 2 copies):
- `src/superclaude/commands/adversarial.md` + `.claude/commands/sc/adversarial.md`
- `src/superclaude/commands/cleanup-audit.md` + `.claude/commands/sc/cleanup-audit.md`
- `src/superclaude/commands/task-unified.md` + `.claude/commands/sc/task-unified.md`
- `src/superclaude/commands/validate-tests.md` + `.claude/commands/sc/validate-tests.md`

**Fix**: Add `Skill` to `allowed-tools` in all 4 affected command files during Phase D.

**Risk if NOT fixed**: If Claude Code enforces the `allowed-tools` whitelist strictly, 4 of 5 commands will fail to invoke their protocol skill. Note: some commands use `mcp-servers` instead of `allowed-tools`, so empirical testing is recommended.

---

### BUG-002: validate-tests.md Stale Path Reference

**Severity**: MEDIUM
**Found by**: commands-to-planning.md (Section 5.6, Discrepancy 2)

**Description**: Line 63 of `validate-tests.md` reads `Reference: skills/sc-validate-tests/classification-algorithm.yaml` using the OLD directory name without `-protocol` suffix. The See Also section (lines 109-110) was updated but this reference was missed.

**Affected File**: `src/superclaude/commands/validate-tests.md` (line 63)

**Fix**: Update during Phase D, Step D.5:
- OLD: `Reference: skills/sc-validate-tests/classification-algorithm.yaml`
- NEW: `Reference: skills/sc-validate-tests-protocol/classification-algorithm.yaml`

---

### BUG-003: Orchestrator Threshold Inconsistency (`>= 3` vs `>= 5`)

**Severity**: MEDIUM
**Found by**: adversarial-to-framework.md (Section 1.5)

**Description**: The roadmap SKILL.md contains two different thresholds for adding the debate-orchestrator agent:
- Line 140 (Wave 2, step 3c): `agent count >= 3` (from D-0006)
- Line 247 (Section 5, Agent Count Rules): `>= 5 agents` (pre-existing, not updated)

**Affected File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

**Fix**: Align both to `>= 3` (the D-0006 specified value) during Phase C, Step C.4.

---

### BUG-004: Architecture Policy Duplication

**Severity**: MEDIUM
**Found by**: Dev Planning Synthesis A (Section 4), Dev Planning Synthesis B (Issue 2)

**Description**: Two identical 337-line files exist with no indication of which is canonical:
- `docs/architecture/command-skill-policy.md`
- `src/superclaude/ARCHITECTURE.md`

No symlink, no `make sync` target, and no note in either file about the other.

**Fix during Phase A**: Choose ONE of these approaches:
1. **Preferred**: Designate `docs/architecture/command-skill-policy.md` as canonical, and replace `src/superclaude/ARCHITECTURE.md` with a one-line note pointing to the canonical location
2. **Alternative**: Add a sync rule to the Makefile `sync-dev` target
3. **Alternative**: Create a symlink (may not work on all platforms)

---

### BUG-005: Roadmap SKILL.md Stale Path to Adversarial Skill

**Severity**: MEDIUM
**Found by**: Framework Synthesis B (Section 3.2)

**Description**: The roadmap SKILL.md Wave 0 step 5 still references `src/superclaude/skills/sc-adversarial/SKILL.md` (old path without `-protocol` suffix).

**Affected File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

**Fix**: Update during Phase C, Step C.5:
- OLD: `src/superclaude/skills/sc-adversarial/SKILL.md`
- NEW: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`

---

### BUG-006: `make lint-architecture` Missing 2 Policy Checks

**Severity**: LOW
**Found by**: makefile-to-planning.md (Section 3)

**Description**: The architecture policy defines 10 CI checks, but the Makefile implements only 6 (covering 8 policy requirements via combination/delegation). Two checks are genuinely missing:
- **Policy #5**: Inline protocol detection (command with `-protocol` skill contains YAML blocks >20 lines)
- **Policy #7**: Activation reference correctness (`## Activation` contains `Skill sc:<name>-protocol`)

**Fix**: Implement during Phase E if desired, or document as deferred. The policy's Phase 4 expects "all 10 checks pass" which cannot be validated against a 6-check implementation.

---

### BUG-007: Checkpoint Artifact Existence Unverified

**Severity**: LOW
**Found by**: Dev Planning Synthesis B (Issue 6)

**Description**: Checkpoint reports reference D-0001 through D-0008 across `artifacts/` directories. Whether all referenced files actually exist on disk was not confirmed.

**Fix**: Run verification during Phase B:
```bash
find .dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/ -type f | sort
```

---

### BUG-008: Return Contract Field Count Mismatch

**Severity**: LOW (resolved in spec-v2)
**Found by**: Dev Artifacts Synthesis A (Section 6.2)

**Description**: `merged-approach.md` claims "9+1=10 fields" for the return contract, but SKILL.md FR-007 defines only 5 fields. Resolved in spec-v2 with producer/consumer ownership model.

**Status**: Historical inconsistency in artifacts only. No framework fix needed.

---

### BUG-009: Wave 2 Step 3e Architectural Divergence

**Severity**: LOW (design debt)
**Found by**: Dev Planning Synthesis A (Section 8.6)

**Description**: Step 3e inlines return contract routing directly rather than delegating to the ref section, diverging from Wave 1A's pattern of ref-delegation.

**Fix**: Document the divergence rationale in the SKILL.md or a design decision record. No code change required.

---

### BUG-010: Sprint Variant Decision Environment-Dependent

**Severity**: LOW (forward-execution risk)
**Found by**: Dev Planning Synthesis B (Issue 7)

**Description**: T01.01's `TOOL_NOT_AVAILABLE` result is environment-specific. If the Skill tool becomes available in a different Claude Code version, the fallback-only variant decision chain could be invalidated.

**Fix**: Re-validate the probe result if the execution environment changes. No immediate action needed for recreation.

---

### BUG-011: Path Inconsistencies in 24 of 25 Dev Artifacts

**Severity**: LOW (historical documents)
**Found by**: Dev Artifacts Synthesis A (Section 8.4), Dev Artifacts Synthesis B (Section 5)

**Description**: 24 of 25 dev artifacts use pre-rename paths (`sc-adversarial/`, `sc-roadmap/`). Only `specification-draft-v2.md` uses `-protocol` paths.

**Fix**: Accept as historical records (artifacts document state at creation time) OR batch-update all artifact path references. Low priority since these are design documents, not executable code.

---

### BUG-012: Tasklist Files Reference Old Paths

**Severity**: LOW (historical documents)
**Found by**: Dev Planning Synthesis A (Section 5), Dev Planning Synthesis B (Issue 1)

**Description**: `tasklist-P5.md` and `tasklist-P6.md` reference skill paths using OLD directory names (`sc-adversarial/`, `sc-roadmap/`).

**Fix**: Update path references in both tasklist files if they will continue to be used for execution. Low priority if tasklists are treated as historical records.

---

## 6. Post-Recreation Validation

Complete validation checklist to confirm successful recreation.

### 6.1 Structural Validation

```bash
# All 5 skill directories renamed
test -d src/superclaude/skills/sc-adversarial-protocol && echo "PASS" || echo "FAIL"
test -d src/superclaude/skills/sc-cleanup-audit-protocol && echo "PASS" || echo "FAIL"
test -d src/superclaude/skills/sc-roadmap-protocol && echo "PASS" || echo "FAIL"
test -d src/superclaude/skills/sc-task-unified-protocol && echo "PASS" || echo "FAIL"
test -d src/superclaude/skills/sc-validate-tests-protocol && echo "PASS" || echo "FAIL"

# No old directories remain
test ! -d src/superclaude/skills/sc-adversarial && echo "PASS" || echo "FAIL"
test ! -d src/superclaude/skills/sc-cleanup-audit && echo "PASS" || echo "FAIL"
test ! -d src/superclaude/skills/sc-roadmap && echo "PASS" || echo "FAIL"
test ! -d src/superclaude/skills/sc-task-unified && echo "PASS" || echo "FAIL"
test ! -d src/superclaude/skills/sc-validate-tests && echo "PASS" || echo "FAIL"
```

### 6.2 Naming Convention Validation

```bash
# All SKILL.md name fields use sc: prefix and -protocol suffix
for d in src/superclaude/skills/sc-*-protocol/SKILL.md; do
  name=$(grep "^name:" "$d" | head -1)
  echo "$d -> $name"
  echo "$name" | grep -q "sc:.*-protocol" && echo "  PASS" || echo "  FAIL"
done
```

### 6.3 Command Validation

```bash
# All 5 commands have ## Activation
for f in adversarial cleanup-audit roadmap task-unified validate-tests; do
  grep -q "## Activation" "src/superclaude/commands/$f.md" && echo "$f: PASS" || echo "$f: FAIL"
done

# All 5 commands reference correct skill
for f in adversarial cleanup-audit roadmap task-unified validate-tests; do
  grep -q "sc:.*-protocol" "src/superclaude/commands/$f.md" && echo "$f: PASS" || echo "$f: FAIL"
done

# task-unified.md is under 200 lines
lines=$(wc -l < src/superclaude/commands/task-unified.md)
test "$lines" -lt 200 && echo "task-unified size: PASS ($lines lines)" || echo "task-unified size: FAIL ($lines lines)"

# BUG-001: All commands have Skill in allowed-tools
for f in adversarial cleanup-audit roadmap task-unified validate-tests; do
  grep -qi "skill" "src/superclaude/commands/$f.md" | head -1
done
```

### 6.4 Sync Validation

```bash
# Full sync verification
make verify-sync
# Expected: PASS

# Command parity
for cmd in adversarial cleanup-audit roadmap task-unified validate-tests; do
  diff -q "src/superclaude/commands/$cmd.md" ".claude/commands/sc/$cmd.md" && echo "$cmd: IDENTICAL" || echo "$cmd: MISMATCH"
done
```

### 6.5 Makefile Validation

```bash
# lint-architecture target exists
make lint-architecture
# Expected: 0 errors

# Heuristic removed
grep -c "served by" Makefile
# Expected: 0

# Heuristic removed from sync-dev
grep -c "cmd_name=\${skill_name#sc-}" Makefile
# Expected: 0
```

### 6.6 Bug Fix Validation

```bash
# BUG-002: validate-tests.md path updated
grep "classification-algorithm.yaml" src/superclaude/commands/validate-tests.md
# Expected: Contains "sc-validate-tests-protocol" (not "sc-validate-tests")

# BUG-003: Orchestrator threshold consistent
grep -n "orchestrator\|>= 3\|>= 5" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: All references use >= 3 (or whichever value is chosen)

# BUG-005: Adversarial path updated in roadmap SKILL.md
grep "sc-adversarial" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: All references use "sc-adversarial-protocol" (not "sc-adversarial")
```

### 6.7 Comprehensive Checklist Summary

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | 5 skill dirs renamed | `ls src/superclaude/skills/ \| grep protocol \| wc -l` | 5 |
| 2 | 0 old skill dirs | `ls src/superclaude/skills/ \| grep -v protocol \| grep "^sc-" \| wc -l` | 0 |
| 3 | 5 commands have Activation | `grep -rl "## Activation" src/superclaude/commands/` | 5 files |
| 4 | task-unified under 200 lines | `wc -l src/superclaude/commands/task-unified.md` | < 200 |
| 5 | sync passes | `make verify-sync` | exit 0 |
| 6 | lint passes | `make lint-architecture` | 0 errors |
| 7 | BUG-001 fixed | All commands have Skill in allowed-tools | 5/5 |
| 8 | BUG-002 fixed | validate-tests.md path correct | -protocol suffix |
| 9 | BUG-003 fixed | Orchestrator threshold aligned | Single value |
| 10 | BUG-005 fixed | Roadmap SKILL.md adversarial path | -protocol suffix |

---

## 7. Remaining Work (Phases 3-6 of Sprint)

After successful recreation, 13 sprint tasks from Phases 3-6 remain pending. These are tracked in `tasklist-P6.md`.

### 7.1 Phase 3: Structural Validation (2 tasks, EXEMPT)

| Task | Description | Expected Framework Change | Status |
|------|-------------|--------------------------|--------|
| **T03.01** | Fallback structure validation | None (read-only validation) | PENDING |
| **T03.02** | Structural audit of wiring | None (read-only audit) | PENDING |

### 7.2 Phase 4: Return Contract & Artifact Gates (3 tasks, STRICT/STANDARD)

| Task | Description | Expected Framework Change | Status |
|------|-------------|--------------------------|--------|
| **T04.01** | Return contract write instruction | Edit to `sc-adversarial-protocol/SKILL.md` | PENDING |
| **T04.02** | Artifact gate specification | Edit to `refs/adversarial-integration.md` | PENDING |
| **T04.03** | Artifact gate standard | Edit to `refs/adversarial-integration.md` | PENDING |

### 7.3 Phase 5: Polish & Documentation (3 tasks, STANDARD)

| Task | Description | Expected Framework Change | Status |
|------|-------------|--------------------------|--------|
| **T05.01** | Execution Vocabulary Glossary | Documentation additions | PENDING |
| **T05.02** | Wave 1A Step 2 Fix | Edit to `sc-roadmap-protocol/SKILL.md` | PENDING |
| **T05.03** | Pseudo-CLI Conversion | Edit to `refs/adversarial-integration.md` | PENDING |

### 7.4 Phase 6: Wrap-up (5 tasks, EXEMPT/STANDARD)

| Task | Description | Expected Framework Change | Status |
|------|-------------|--------------------------|--------|
| **T06.01** | Schema consistency test | Documentation/test additions | PENDING |
| **T06.02** | Cross-reference field consistency | Validation only | PENDING |
| **T06.03** | Sprint summary document | Documentation | PENDING |
| **T06.04** | Tasklist close-out | Tasklist updates | PENDING |
| **T06.05** | Final sync + quality gates | `make sync-dev && make verify-sync` | PENDING |

### 7.5 Architecture Policy Items Not Yet Implemented

| Item | Priority | Description | Status |
|------|----------|-------------|--------|
| Complete `lint-architecture` (2 missing checks) | HIGH | Policy checks #5 (inline YAML) and #7 (activation reference) | NOT STARTED |
| `claude -p` Tier 2 ref loader | HIGH | Script to load ref files on-demand via headless CLI | NOT STARTED (design phase) |
| Cross-skill invocation patterns | HIGH | Patterns for skills to invoke other skills | NOT STARTED (design phase) |
| 6 oversized command splits | MEDIUM | Commands exceeding 150-line cap | NOT STARTED |
| Architecture policy deduplication (BUG-004) | LOW | Resolve dual-copy situation | NOT RESOLVED |

### 7.6 Missing Dev Artifacts (Referenced But Never Created)

| Artifact | Referenced By | Why Missing |
|----------|---------------|-------------|
| `refs/headless-invocation.md` | Approaches 2/3, merged-approach, specs | Infrastructure file for headless `claude -p` path (not needed for fallback-only) |
| Probe fixtures (`spec-minimal.md`, `variant-a.md`, `variant-b.md`) | Approach 1, spec-v2 | Test fixtures (not needed for fallback-only) |
| `expected-schema.yaml` / `return-contract.yaml` | Approach 1 (Appendix B) | Schema validation file |

### 7.7 Spec-v2 Items Not Yet Implemented

These are requirements from `specification-draft-v2.md` that were not implemented during Phase 2:

**HIGH Priority**:
- `unresolved_conflicts` should be `list[string]` (currently integer)
- `invocation_method` field in return contract (absent from D-0007)
- `schema_version: "1.0"` field (absent from contract)
- SKILL.md content validation (empty check + ARG_MAX)

**MEDIUM Priority**:
- 4-state artifact scan model (A/B/C/D)
- Budget ceiling (total adversarial = 2x BUDGET)
- Schema ownership model (producer/consumer)

---

## Appendix A: Quick Reference -- File Counts

| Phase | Files Affected | Description |
|-------|---------------|-------------|
| A | 2 | Policy documents |
| B | 0 | Verification only (artifacts are in .dev/) |
| C | 30 | 5 SKILL.md modified + 25 companion renames |
| D | 5 | 5 command files in src/ |
| E | 1 | Makefile |
| F | 30 | 5 command copies + 25 skill copies via sync |
| G | 0 | Validation only |
| **Total** | **~68** | Matches original change set |

## Appendix B: Source Document Index

| Document | Path | Role |
|----------|------|------|
| Master traceability | `.dev/.../rollback-analysis/context/master-traceability.md` | Complete cross-reference matrix |
| Commands to planning | `.dev/.../rollback-analysis/context/commands-to-planning.md` | Command change provenance |
| Skill renames to planning | `.dev/.../rollback-analysis/context/skill-renames-to-planning.md` | Rename provenance |
| Makefile to planning | `.dev/.../rollback-analysis/context/makefile-to-planning.md` | Build system provenance |
| Adversarial to framework | `.dev/.../rollback-analysis/context/adversarial-to-framework.md` | Spec-to-code tracing |
| Framework synthesis B | `.dev/.../rollback-analysis/synthesis/framework-synthesis-B.md` | Independent framework analysis |
| Architecture policy | `docs/architecture/command-skill-policy.md` | Governing policy document |
| Canonical tasklist | `.dev/.../tasklist/tasklist-P6.md` | Sprint task definitions |

(All `...` paths expand to `releases/current/v2.01-Roadmap-v3`)
