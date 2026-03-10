# Workflow: sc:roadmap Architecture Refactor (v2.01)

**Generated**: 2026-02-24
**Spec**: `.dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md`
**Branch**: `feature/v2.01-Roadmap-V3`
**Scope**: sc:roadmap command + skill + refs + adversarial dependency + Makefile enforcement

---

## Problem Statement

`sc:roadmap` fails to reliably invoke the adversarial pipeline (`sc:adversarial`) because:
1. **BUG-006**: `roadmap.md` `## Activation` points to old file path instead of `Skill sc:roadmap-protocol`
2. **BUG-001**: `roadmap.md` missing `Skill` in `allowed-tools` — Skill tool invocation blocked
3. **T02.03**: Wave 2 Step 3 says "Invoke sc:adversarial" (vague prose, no tool binding) — agents skip the step
4. **BUG-005**: Wave 0 Step 5 references stale `sc-adversarial/SKILL.md` path (pre-rename)
5. **BUG-003**: Orchestrator threshold inconsistent (Section 5 says ≥5; spec/3c says ≥3)
6. **Makefile skip heuristic (preventive)**: `sync-dev` and `verify-sync` contain a heuristic that strips the `sc-` prefix to derive a command name, then skips syncing if a matching command file exists. For `-protocol` skills, this does NOT currently trigger: stripping `sc-` from `sc-roadmap-protocol` yields `roadmap-protocol`, which has no matching `commands/roadmap-protocol.md`. The actual reason `.claude/skills/sc-roadmap-protocol/` is empty: `make sync-dev` was never run after the rogue-agent renamed the skill directories. Makefile changes (Tasks 4.1–4.2) are still required as preventive cleanup for future-proofing, but are NOT a blocking dependency for the sync. *(D-0001 reversal does not affect this — Makefile heuristic is a build system issue independent of Skill tool availability.)*

---

## Scope Map

| File | Change Type | Bug/Task |
|------|-------------|----------|
| `src/superclaude/commands/roadmap.md` | Rewrite `## Activation` + add `Skill` to frontmatter | BUG-001, BUG-006 |
| `.claude/commands/sc/roadmap.md` | Same as above (sync copy, atomic with src/) | BUG-001, BUG-006 |
| `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | Add `Skill` to frontmatter; fix Wave 0 path; rewrite Wave 2 Step 3 (3a–3f); fix orchestrator threshold; add `## Return Contract` section | BUG-001, BUG-003, BUG-005, T02.03 |
| `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md` | Fix stale `sc-adversarial/SKILL.md` path in Prerequisite check section | BUG-005 (ref) |
| `Makefile` (sync-dev) | Remove 3-line skill-skip heuristic (lines 114–117) | T03.01 |
| `Makefile` (verify-sync) | Remove 3-line skill-skip heuristic (lines 153–157) | T03.01 |
| `Makefile` (lint-architecture) | Add new target with 6 designed policy checks | T03.02 |
| `Makefile` (.PHONY + help) | Add lint-architecture to .PHONY and help text | T03.02 |
| `.claude/skills/sc-roadmap-protocol/` | Populate from src/ via `make sync-dev` | T03.01 |

**Workflow Phase → Sprint-Spec Phase Mapping** (for cross-referencing during implementation):

| Workflow Phase | Sprint-Spec Phase | Tasks Covered |
|---------------|-------------------|---------------|
| Phase 1 (Pre-flight) | Phase 1 | T01.01 probe, T01.02 audit |
| Phase 2 (SKILL.md Fixes) | Phase 2 | T02.01–T02.04 + Wave 1A (by analogy) |
| Phase 3 (Command Files) | Phase 2 | T02.01 command-side changes |
| Phase 4 (Makefile) | Phase 3 | T03.01–T03.03 |
| Phase 5 (Sync + Verify) | Phase 3 | T03.01 sync execution |
| Phase 6 (Integration Tests) | Phase 4 | T04.01–T04.03 |
| Phase 7 (Polish) | Phase 5 | T05.01–T05.03 |

**Not in scope for this tasklist** (other sprint phases):
- sc:adversarial, sc:cleanup-audit, sc:task-unified, sc:validate-tests skill renames — separate Phase 6 tasks
- `task-unified.md` extraction (T06.03) — separate work
- BUG-002 (validate-tests stale path), BUG-004 (architecture duplication) — separate Phase 6

---

## Dependencies (DAG)

```
[Phase 1: Pre-flight]
       |
       v
[Phase 2: SKILL.md Fixes]         ← BUG-001, BUG-003, BUG-005, T02.03
       |
       v
[Phase 3: Command File Fixes]     ← BUG-001, BUG-006 (depends on Phase 2 naming)
       |
       v
[Phase 4: Makefile Enforcement]   ← T03.01, T03.02 (MUST precede Phase 5, Rule 7.5)
       |
       v
[Phase 5: Sync + Verify]          ← make sync-dev, make verify-sync
       |
       v
[Phase 6: Integration Tests]      ← T04.01–T04.03
       |
       v
[Phase 7: Polish]                 ← T05.01–T05.03
```

---

## Phase 1: Pre-flight Verification

**Purpose**: Establish current truth before writing a single line. Prevent rogue-agent drift.

### Task 1.1 — Day-1 State Verification

```bash
# From repo root
git status                          # Check for staged/unstaged changes (treat all as untrusted baseline)
git log --oneline -5                # Confirm on commit 9060a65 or later
ls docs/architecture/command-skill-policy.md   # MUST exist
grep -l "## Activation" src/superclaude/commands/*.md   # Should return ONLY roadmap.md
grep "allowed-tools" src/superclaude/commands/roadmap.md   # Should show: no "Skill" (BUG-001 confirmed)
grep "Activation" src/superclaude/commands/roadmap.md      # Should show old path (BUG-006 confirmed)
```

**Expected findings**:
- `roadmap.md` is the only command with `## Activation`
- `roadmap.md` `## Activation` says `sc-roadmap/SKILL.md` (old path) — BUG-006 confirmed
- No commands have `Skill` in `allowed-tools` — BUG-001 confirmed
- `sc-roadmap-protocol/SKILL.md` exists in `src/`

### Task 1.2 — Skill Content Audit

```bash
# Confirm SKILL.md has the Wave architecture (should be 334 lines from prior rewrite)
wc -l src/superclaude/skills/sc-roadmap-protocol/SKILL.md

# Confirm frontmatter name: field
head -10 src/superclaude/skills/sc-roadmap-protocol/SKILL.md

# Confirm stale path bug (BUG-005)
grep "sc-adversarial/" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
grep "sc-adversarial/" src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md

# Confirm orchestrator bug (BUG-003)
grep -n ">=5\|≥5\|>= 5\|agent_count" src/superclaude/skills/sc-roadmap-protocol/SKILL.md

# Check if Wave 2 Step 3 still has vague "Invoke" (T02.03 needed)
grep -n "Invoke sc:adversarial\|invoke sc:adversarial" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
```

**Expected findings**:
- `name: sc:roadmap` in frontmatter (still the old name — needs update)
- Stale `sc-adversarial/` paths found (BUG-005)
- `>=5` or similar in Section 5 / agent count context (BUG-003)
- "Invoke sc:adversarial" found in Wave 1A and Wave 2 (T02.03 required)

### Task 1.3 — Makefile Skill-Skip Audit

```bash
# Confirm the skip heuristic exists
sed -n '108,128p' Makefile   # sync-dev section
sed -n '146,165p' Makefile   # verify-sync section

# Confirm .claude/ protocol skills are empty
ls .claude/skills/ 2>/dev/null || echo "No .claude/skills/"
ls .claude/skills/sc-roadmap-protocol/ 2>/dev/null || echo "EMPTY — confirms skip heuristic is active"
```

**Expected findings**: `.claude/skills/sc-roadmap-protocol/` is missing or empty. **Root cause**: `make sync-dev` was never run after the rogue-agent renamed the directories — NOT the heuristic. The heuristic computes `cmd_name=roadmap-protocol` (strips `sc-` only, not `-protocol`) and checks for `commands/roadmap-protocol.md` which does not exist, so all 5 `-protocol` skills would sync correctly right now. Makefile changes (Tasks 4.1–4.2) are still required as preventive cleanup (heuristic is conceptually incompatible with v2.01 architecture), but running `make sync-dev` immediately would already populate `.claude/skills/sc-roadmap-protocol/` without any Makefile changes.

### Task 1.4 — T01.01: Skill Tool Probe (Variant Decision Gate)

**Purpose**: The entire sprint variant (SKILL-DIRECT vs Task agent fallback) depends on whether skill-to-skill `Skill` tool invocations are available. D-0001 has been reversed — `AVAILABLE` is the confirmed result. Verify this holds in the current environment before committing to Tasks 2.5–2.6 design.

```bash
# From within an active Claude Code session executing sc:roadmap:
# Attempt to invoke Skill sc:adversarial-protocol from inside skill execution context
# Document result:
#   AVAILABLE          → SKILL-DIRECT confirmed (D-0001 reversal holds); Tasks 2.5–2.6 as written
#   TOOL_NOT_AVAILABLE → Design must revert to Task agent dispatch (unexpected regression)
```

**Decision tree**:
- `AVAILABLE` (confirmed per D-0001 reversal): Proceed with SKILL-DIRECT variant. Tasks 2.5 and 2.6 as written use direct `Invoke Skill sc:adversarial-protocol` — correct.
- `TOOL_NOT_AVAILABLE` (unexpected regression): The Wave 2 Step 3 sub-steps in Task 2.6 must change — replace `Invoke Skill sc:adversarial-protocol` with `Dispatch Task agent` fallback. Revise Task 2.6 before executing Phase 2.

### Task 1.5 — sc:adversarial-protocol Dependency Verification

**Purpose**: Confirm the `sc:adversarial-protocol` skill (invoked by Wave 2 Step 3d) is in a functional state. If the rogue-agent's rename of sc:adversarial is also corrupted, the Wave 2 Skill invocation would call a broken skill.

```bash
# Verify sc:adversarial-protocol frontmatter
head -6 src/superclaude/skills/sc-adversarial-protocol/SKILL.md
# Expected: name: sc:adversarial-protocol

# Verify Skill is in allowed-tools
grep "allowed-tools" src/superclaude/skills/sc-adversarial-protocol/SKILL.md
# Expected: contains "Skill"

# Verify non-trivial content
wc -l src/superclaude/skills/sc-adversarial-protocol/SKILL.md
# Expected: > 50 lines
```

**Expected findings**: `name: sc:adversarial-protocol` in frontmatter; `Skill` in `allowed-tools`; line count > 50. If frontmatter is wrong or `Skill` is absent, flag for separate repair before testing Wave 2 (the Task agent dispatch in Step 3d would invoke a broken skill).

**Phase 1 Exit Criteria**: All bugs confirmed, state documented. T01.01 probe result recorded (SKILL-DIRECT vs AVAILABLE). sc:adversarial-protocol dependency verified as functional. No changes made yet.

---

## Phase 2: SKILL.md Fixes

**Compliance**: STRICT (per D-T01.03 — SKILL.md is code, not documentation)

### Task 2.1 — Fix SKILL.md Frontmatter

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Change the frontmatter block (lines 1–5) from:
```yaml
---
name: sc:roadmap
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

To:
```yaml
---
name: sc:roadmap-protocol
description: "Full behavioral protocol for sc:roadmap — roadmap generation from specifications with adversarial integration"
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
argument-hint: "<spec-file-path> [--specs ...] [--multi-roadmap --agents ...] [--depth quick|standard|deep] [--output dir]"
---
```

**Changes**:
- `name:` updated from `sc:roadmap` → `sc:roadmap-protocol` (satisfies naming convention + CI Check 9)
- `Skill` added to `allowed-tools` (fixes BUG-001 for SKILL.md side)
- `description:` made explicit (satisfies CI Check 8)
- `argument-hint:` added (optional but good practice)

### Task 2.2 — Fix BUG-005: Stale Path in Wave 0 Step 5

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Find the Wave 0 Step 5 instruction (currently references `sc-adversarial/SKILL.md`):
```
5. If `--specs` or `--multi-roadmap` flags present: verify `src/superclaude/skills/sc-adversarial/SKILL.md` exists.
```

Replace with:
```
5. If `--specs` or `--multi-roadmap` flags present: verify `src/superclaude/skills/sc-adversarial-protocol/SKILL.md` exists. If not, abort: `"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags. Install via: superclaude install"`
```

### Task 2.3 — Fix BUG-005: Stale Path in refs/adversarial-integration.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md`

Find the Prerequisite check section (line 25 area):
```
...verify `src/superclaude/skills/sc-adversarial/SKILL.md` exists. If not found, abort: `"sc:adversarial skill not installed...
```

Replace `sc-adversarial/SKILL.md` with `sc-adversarial-protocol/SKILL.md`.

### Task 2.4 — Fix BUG-003: Orchestrator Threshold Alignment

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Find all references to orchestrator threshold in Section 5 (Adversarial Modes) and Wave 2 Step 3:

- Change: `If agent count ≥5, orchestrator is added automatically`
- To: `If agent count ≥3, orchestrator is added automatically`
- Change: `With >= 5 agents: add orchestrator agent`
- To: `With >= 3 agents: add orchestrator agent`

Authoritative source: Step 3c of the fallback protocol (§9 of sprint-spec): `agent_count >= 3`.

### Task 2.5 — T02.03: Rewrite Wave 1A Step 2 (Task Agent Dispatch)

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

> **Note**: Sub-steps 2a–2f below mirror the §9 protocol sub-steps 3a–3f. Both Wave 1A Step 2 and Wave 2 Step 3 use direct SKILL-DIRECT invocation via `Invoke Skill sc:adversarial-protocol`. Apply as written.

Find Wave 1A Step 2 (currently contains vague "Invoke sc:adversarial"):
```
2. Invoke sc:adversarial with `--compare` mode per `refs/adversarial-integration.md` "Multi-Spec Consolidation" invocation pattern. Propagate `--interactive` flag if set...
```

Replace with the SKILL-DIRECT invocation pattern:
```markdown
2. Invoke `sc:adversarial-protocol` directly for multi-spec consolidation:
   - **2a**: Build adversarial invocation arguments: `--compare <spec-list>` (comma-separated), propagate `--interactive` if set, propagate `--depth` mapping per Wave 0 decision
   - **2b**: Invoke: `Skill sc:adversarial-protocol` with arguments built in 2a
   - **2c**: Read return contract inline from Skill response. If response is empty or unparseable, use fallback `convergence_score: 0.5`
   - **2d**: Parse return contract fields from inline Skill response (no file read required)
   - **2e**: Route per return contract `status` field and `convergence_score`:
     - `status: success` → proceed with `merged_output_path` as spec input for Wave 1B
     - `status: partial` + score ≥ 0.6 → proceed with warning logged in extraction.md
     - `status: partial` + score < 0.6 → if `--interactive`, prompt user; otherwise abort
     - `status: failed` → abort roadmap generation
   - **2f**: Apply divergent-specs heuristic: if `convergence_score` < 0.5 → emit warning to user
```

### Task 2.6 — T02.03: Rewrite Wave 2 Step 3 (Sub-steps 3a–3f)

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Find Wave 2 Step 3 (currently the long sentence with vague "Invoke sc:adversarial"):
```
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Expand model-only agents with the primary persona from Wave 1B. If agent count ≥5, orchestrator is added automatically. Invoke sc:adversarial for multi-roadmap generation per `refs/adversarial-integration.md` "Multi-Roadmap Generation" invocation pattern. Handle return contract per `refs/adversarial-integration.md` "Return Contract Consumption" section. The adversarial output replaces template-based generation.
```

Replace with:
```markdown
3. If `--multi-roadmap`: execute the SKILL-DIRECT adversarial invocation protocol (sub-steps 3a–3f):
   - **3a**: Parse agent specs from `--agents` flag using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Output: agent list with model, persona, instruction per agent.
   - **3b**: Expand model-only agent specs: apply the primary persona auto-detected in Wave 1B to any agent spec that has no explicit persona. Output: fully-specified variant configurations.
   - **3c**: If `agent_count >= 3`: add `debate-orchestrator` agent to coordinate debate rounds and prevent combinatorial explosion. Threshold: 3 (not 5). Output: final agent list with optional orchestrator.
   - **3d**: Invoke `sc:adversarial-protocol` directly via Skill tool:
     - Build arguments: `--source <unified-spec> --generate roadmap --agents <expanded-agent-list>`, propagate `--depth` and `--interactive`
     - Invoke: `Skill sc:adversarial-protocol` with the above arguments
     - sc:adversarial-protocol executes F1 (variant generation) → F2/3 (diff + debate) → F4/5 (base selection + merge)
     - Output: structured return contract returned inline as Skill response
   - **3e**: Consume return contract (inline Skill return value):
     - **Empty/malformed response guard**: If Skill response is empty or unparseable → use fallback `convergence_score: 0.5` (Partial path by design)
     - **3-status routing**:
       - IF `convergence_score >= 0.6` → PASS: use `merged_output_path` as roadmap source; the adversarial output replaces template-based generation
       - ELIF `convergence_score >= 0.5` → PARTIAL: use `merged_output_path` with warning in roadmap.md frontmatter (`adversarial_status: partial`)
       - ELSE (`convergence_score < 0.5`) → FAIL: abort with `"Adversarial pipeline failed (convergence: X.XX). Cannot produce reliable roadmap from divergent variants."`
   - **3f**: SKILL-DIRECT is the primary path. The adversarial output from 3d is the roadmap source. No secondary template fallback applies; if 3d/3e return FAIL, abort roadmap generation entirely.
```

### Task 2.7 — Add `## Return Contract` Section to SKILL.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Every protocol SKILL.md must have a `## Return Contract` section (per §10 of sprint-spec). Add after the `## Boundaries` section:

```markdown
## Return Contract

sc:roadmap produces no machine-readable return contract file (it is a terminal command, not a sub-agent). When sc:roadmap invokes sc:adversarial-protocol via direct Skill invocation (SKILL-DIRECT), the return contract is received as the **inline return value** of the Skill call — not a file on disk.

**Return contract transport**: Inline Skill response (structured data returned directly by `sc:adversarial-protocol` upon completion).

**Fields consumed by sc:roadmap** (from sc:adversarial-protocol inline return value):

| Field | Type | Used In | Action |
|-------|------|---------|--------|
| `status` | `success\|partial\|failed` | Wave 1A Step 2e, Wave 2 Step 3e | Primary routing decision |
| `convergence_score` | `float 0.0-1.0` | Wave 1A Step 2e, Wave 2 Step 3e | Secondary routing threshold (≥0.6 PASS, ≥0.5 PARTIAL, <0.5 FAIL) |
| `merged_output_path` | `path\|null` | Wave 1A Step 2e, Wave 2 Step 3e | Path to consolidated spec or roadmap |
| `fallback_mode` | `bool` | Wave 1A, Wave 2 logging | Logged in extraction.md |
| `invocation_method` | `enum` | Wave 1A, Wave 2 logging | Logged for observability |
| `unresolved_conflicts` | `list[string]` | Wave 1A, Wave 2 | Listed in roadmap.md decision summary if non-empty |

**Consumer defaults** (if field absent):
```yaml
convergence_score: 0.5    # Forces Partial path
status: "failed"          # Triggers abort
merged_output_path: null  # No output available
```
```

### Task 2.8 — Add `## Triggers` Section to SKILL.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Per §5 SKILL template, `## Triggers` is a required section. Add immediately after the frontmatter block (before `## 1. Purpose & Identity`):

```markdown
## Triggers

sc:roadmap-protocol is invoked ONLY by the `sc:roadmap` command via `Skill sc:roadmap-protocol` in the `## Activation` section. It is never invoked directly by users.

Activation conditions:
- User runs `/sc:roadmap <spec-file>` in Claude Code
- Any `--specs`, `--multi-roadmap`, or `--agents` flags are passed through from the command

Do NOT invoke this skill directly. Use the `sc:roadmap` command.
```

### Task 2.9 — Add `## Agent Delegation` Section to SKILL.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Per §5 SKILL template, `## Agent Delegation` is a required section. Add after `## Return Contract`:

```markdown
## Agent Delegation

sc:roadmap-protocol delegates to sc:adversarial-protocol via direct Skill invocation (SKILL-DIRECT per D-0001 reversal):

| Delegation Point | Target Skill | Invocation Method | Output Contract |
|-----------------|--------------|-------------------|-----------------|
| Wave 1A Step 2 (multi-spec) | sc:adversarial-protocol | `Invoke Skill sc:adversarial-protocol --compare <specs>` | Inline Skill return value |
| Wave 2 Step 3d (multi-roadmap) | sc:adversarial-protocol | `Invoke Skill sc:adversarial-protocol --source <spec> --generate roadmap --agents <list>` | Inline Skill return value |

**SKILL-DIRECT**: Direct `Skill` tool invocation is the primary method. Skill-to-skill invocation is confirmed available (AVAILABLE per D-0001 reversal). No Task agent wrapper required.
```

### Task 2.10 — Add `## Error Handling` Section to SKILL.md

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

Per §5 SKILL template, `## Error Handling` is a required section. Add after `## Agent Delegation`:

```markdown
## Error Handling

| Error Condition | Wave | Detection | Action |
|----------------|------|-----------|--------|
| Spec file not found | Wave 0 | File read fails | Abort: `"Spec file not found: <path>"` |
| sc:adversarial-protocol not installed | Wave 0 Step 5 | SKILL.md missing | Abort: `"sc:adversarial skill not installed. Required for --specs/--multi-roadmap flags."` |
| Skill response empty or unparseable | Wave 1A Step 2c, Wave 2 Step 3e | Inline return parse fails | Use fallback `convergence_score: 0.5` (Partial path) |
| Skill sc:adversarial-protocol invocation fails (tool error) | Wave 1A Step 2b, Wave 2 Step 3d | Skill tool returns error | Abort: `"sc:adversarial-protocol Skill invocation failed. Adversarial pipeline aborted."` |
| convergence_score < 0.5 | Wave 1A Step 2e, Wave 2 Step 3e | Score comparison | Abort: `"Adversarial pipeline failed (convergence: X.XX)"` |
| Template not found | Wave 3 | File read fails | Use generic template; log warning |
| Output directory not writable | Wave 0/3 | Write fails | Abort: `"Cannot write to output directory: <path>"` |
```

**Phase 2 Exit Criteria**:
- `name: sc:roadmap-protocol` in SKILL.md frontmatter
- `Skill` in SKILL.md `allowed-tools`
- All `sc-adversarial/` references replaced with `sc-adversarial-protocol/`
- Orchestrator threshold unified at `>=3`
- Wave 1A Step 2 and Wave 2 Step 3 use direct `Invoke Skill sc:adversarial-protocol` (SKILL-DIRECT, no Task agent wrapper)
- `## Return Contract` section present in SKILL.md
- `## Triggers`, `## Agent Delegation`, `## Error Handling` sections present in SKILL.md

---

## Phase 3: Command File Fixes

**Compliance**: LIGHT for frontmatter changes; STRICT for Activation rewrite

**⚠️ ATOMIC UNIT**: Both `src/` and `.claude/` copies must be changed in the same commit.

### Task 3.1 — Fix BUG-001 + BUG-006 in roadmap.md

**File**: `src/superclaude/commands/roadmap.md`

**Change 1 — frontmatter** (line 4):
```yaml
# FROM:
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task

# TO:
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

**Change 2 — `## Activation` section** (lines 68–71):
```markdown
# FROM:
## Activation

Load and execute the full behavioral instructions from `src/superclaude/skills/sc-roadmap/SKILL.md`.

# TO:
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:roadmap-protocol

Do NOT proceed with protocol execution using only this command file.
The full behavioral specification is in the protocol skill.
```

> **Format note (Minor Issue 3)**: The `> Skill sc:roadmap-protocol` blockquote format matches the §5 template exactly and is intentional. Prior Activation sections used plain prose — this is a spec-compliant change. Verify the Skill tool recognizes blockquote-formatted directives when loading the command file.

**Verify command file line count after change** (target ≤150, hard limit ≤350):
```bash
wc -l src/superclaude/commands/roadmap.md   # Expect ~78 lines — well within limit
```

### Task 3.2 — Apply Same Fixes to .claude/ Copy (Atomic)

```bash
cp src/superclaude/commands/roadmap.md .claude/commands/sc/roadmap.md
```

Verify:
```bash
diff src/superclaude/commands/roadmap.md .claude/commands/sc/roadmap.md   # Must be identical
```

**Phase 3 Exit Criteria**:
- `Skill` in `allowed-tools` in both command file copies
- `## Activation` section says `Skill sc:roadmap-protocol` (not old file path)
- `## Activation` includes "Do NOT proceed" warning
- Both `src/` and `.claude/` copies are identical

---

## Phase 4: Makefile Enforcement

**Compliance**: STANDARD
**Rule 7.5 from sprint-spec**: Enforcement infrastructure MUST be in place before Phase 5 (sync).

### Task 4.1 — Remove Skill-Skip Heuristic from sync-dev

**File**: `Makefile`

Find the `sync-dev` section (lines ~111–117). Remove the 4-line heuristic that skips skills with matching commands:

```makefile
# REMOVE these 4 lines:
		cmd_name=$${skill_name#sc-}; \
		if [ "$$cmd_name" != "$$skill_name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			continue; \
		fi; \
```

**Result**: `sync-dev` will now sync ALL skills including `sc-*-protocol/` directories, even when a matching command exists.

### Task 4.2 — Remove Skill-Skip Heuristic from verify-sync

**File**: `Makefile`

Find the `verify-sync` section (lines ~151–157). Remove the 4-line heuristic:

```makefile
# REMOVE these 5 lines:
		cmd_name=$${name#sc-}; \
		if [ "$$cmd_name" != "$$name" ] && [ -f "src/superclaude/commands/$$cmd_name.md" ]; then \
			echo "  ⏭️  $$name (served by /sc:$$cmd_name command)"; \
			continue; \
		fi; \
```

**Result**: `verify-sync` will now check ALL skills for drift, including `-protocol` directories.

### Task 4.3 — Add lint-architecture Target to Makefile

**File**: `Makefile`

Add the following new target after `verify-sync`. This implements 6 of 10 designed policy checks from §11 of the sprint-spec (Checks 5 and 7 are NEEDS DESIGN):

```makefile
# Enforce architecture policy: commands, skills, naming conventions
lint-architecture:
	@echo "🔍 Checking architecture policy compliance..."
	@errors=0; \
	warnings=0; \
	\
	echo ""; \
	echo "=== Check 1/2: Bidirectional Command ↔ Skill Links ==="; \
	for f in src/superclaude/commands/*.md; do \
		name=$$(basename "$$f" .md); \
		case "$$name" in README) continue;; esac; \
		if grep -q "## Activation" "$$f"; then \
			skill_name="sc-$$name-protocol"; \
			if [ ! -d "src/superclaude/skills/$$skill_name" ]; then \
				echo "  ❌ ERROR [Check 1]: $$f has ## Activation but no matching skill directory: $$skill_name"; \
				errors=$$((errors+1)); \
			else \
				echo "  ✅ [Check 1]: $$name → $$skill_name"; \
			fi; \
		fi; \
	done; \
	for d in src/superclaude/skills/sc-*-protocol/; do \
		skill_base=$$(basename "$$d"); \
		cmd_name=$$(echo "$$skill_base" | sed 's/^sc-//' | sed 's/-protocol$$//'); \
		cmd_file="src/superclaude/commands/$$cmd_name.md"; \
		if [ ! -f "$$cmd_file" ]; then \
			echo "  ❌ ERROR [Check 2]: Skill $$skill_base has no matching command: $$cmd_file"; \
			errors=$$((errors+1)); \
		else \
			echo "  ✅ [Check 2]: $$skill_base ← $$cmd_name.md"; \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Check 3/4: Command Size Limits ==="; \
	for f in src/superclaude/commands/*.md; do \
		name=$$(basename "$$f"); \
		case "$$name" in README.md) continue;; esac; \
		lines=$$(wc -l < "$$f"); \
		if [ "$$lines" -gt 500 ]; then \
			echo "  ❌ ERROR [Check 4]: $$name ($$lines lines, hard limit 500)"; \
			errors=$$((errors+1)); \
		elif [ "$$lines" -gt 350 ] && grep -q "## Activation" "$$f"; then \
			echo "  ❌ ERROR [Check 4]: $$name ($$lines lines, max ≤350 for paired commands)"; \
			errors=$$((errors+1)); \
		elif [ "$$lines" -gt 200 ]; then \
			echo "  ⚠️  WARN [Check 3]: $$name ($$lines lines, warn threshold 200)"; \
			warnings=$$((warnings+1)); \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Check 6: Activation Section Present (for paired commands) ==="; \
	for d in src/superclaude/skills/sc-*-protocol/; do \
		skill_base=$$(basename "$$d"); \
		cmd_name=$$(echo "$$skill_base" | sed 's/^sc-//' | sed 's/-protocol$$//'); \
		cmd_file="src/superclaude/commands/$$cmd_name.md"; \
		if [ -f "$$cmd_file" ]; then \
			if grep -q "## Activation" "$$cmd_file"; then \
				echo "  ✅ [Check 6]: $$cmd_name.md has ## Activation"; \
			else \
				echo "  ❌ ERROR [Check 6]: $$cmd_name.md missing ## Activation (paired with $$skill_base)"; \
				errors=$$((errors+1)); \
			fi; \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Check 8: Skill Frontmatter Completeness ==="; \
	for skill_md in src/superclaude/skills/sc-*-protocol/SKILL.md; do \
		for field in "name:" "description:" "allowed-tools:"; do \
			if ! grep -q "^$$field" "$$skill_md"; then \
				echo "  ❌ ERROR [Check 8]: $$skill_md missing frontmatter field: $$field"; \
				errors=$$((errors+1)); \
			fi; \
		done; \
		echo "  ✅ [Check 8]: $$(dirname $$skill_md | xargs basename) frontmatter complete"; \
	done; \
	\
	echo ""; \
	echo "=== Check 9: Protocol Naming Consistency ==="; \
	for skill_md in src/superclaude/skills/sc-*-protocol/SKILL.md; do \
		name_field=$$(grep "^name:" "$$skill_md" | head -1 | cut -d: -f2 | tr -d ' '); \
		if echo "$$name_field" | grep -q ".*-protocol$$"; then \
			echo "  ✅ [Check 9]: $$name_field ends in -protocol"; \
		else \
			echo "  ❌ ERROR [Check 9]: $$(dirname $$skill_md | xargs basename) SKILL.md name field '$$name_field' does not end in -protocol"; \
			errors=$$((errors+1)); \
		fi; \
	done; \
	\
	echo ""; \
	echo "=== Checks 5/7: NEEDS DESIGN (skipped) ==="; \
	echo "  ℹ️  Check 5 (inline protocol detection) — pending design"; \
	echo "  ℹ️  Check 7 (activation references correct skill) — pending design"; \
	\
	echo ""; \
	echo "=== Summary ==="; \
	echo "  Errors:   $$errors"; \
	echo "  Warnings: $$warnings"; \
	if [ "$$errors" -gt 0 ]; then \
		echo "  ❌ FAIL — $$errors error(s) found. Fix before proceeding."; \
		exit 1; \
	else \
		echo "  ✅ PASS — architecture policy compliant ($$warnings warning(s))"; \
		exit 0; \
	fi
```

**Also update** `.PHONY` line at top of Makefile:
```makefile
# FROM:
.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync uninstall-legacy help

# TO:
.PHONY: install test test-plugin doctor verify clean lint format build-plugin sync-plugin-repo sync-dev verify-sync lint-architecture uninstall-legacy help
```

**Also update** `help` target to include lint-architecture:
```makefile
# Add to help output:
	@echo "  make lint-architecture - Enforce architecture policy (6 of 10 checks)"
```

**Phase 4 Exit Criteria**:
```bash
make lint-architecture   # Must exit 0 (errors=0) before Phase 5
```

If it fails: fix the reported errors before continuing.

---

## Phase 5: Sync and Verify

### Task 5.1 — Sync src/ to .claude/

```bash
make sync-dev
```

**Expected output**: All 6 skill directories populated in `.claude/skills/`, including `sc-roadmap-protocol/` with all 7 files.

### Task 5.2 — Verify Sync Parity

```bash
make verify-sync
```

**Expected outcome**: All skills show ✅. No ⏭️ skips. No ❌ drifts.

### Task 5.3 — Run Full Lint Pass

```bash
make lint-architecture
```

**Expected outcome**: `exit 0`. All Check 1/2/6/8/9 pass for sc-roadmap-protocol.

**Phase 5 Exit Criteria**: `make sync-dev && make verify-sync && make lint-architecture` all pass.

---

## Phase 6: Integration Validation

**Compliance**: STRICT

### Task 6.1 — 8-Point Wave 2 Step 3 Audit

Verify the rewritten Wave 2 Step 3 satisfies the 8-point audit from §9 of sprint-spec:

| Point | Check | Expected |
|-------|-------|----------|
| 1 | Tool binding present | `"Invoke Skill sc:adversarial-protocol"` (not bare "Invoke", not "Dispatch Task agent") |
| 2 | Sub-steps 3a–3f present | All 6 sub-steps labeled |
| 3 | Agent spec parsing (3a) | References adversarial-integration.md parsing algorithm |
| 4 | Agent expansion (3b) | Persona inheritance from Wave 1B |
| 5 | Orchestrator threshold (3c) | `>= 3` (not >= 5) |
| 6 | Return contract transport (3d/3e) | Inline Skill return value (no file write in SKILL-DIRECT mode) |
| 7 | Empty/malformed response guard (3e) | Falls back to `convergence_score: 0.5` (Partial path) |
| 8 | 3-status routing (3e) | ≥0.6 PASS, ≥0.5 PARTIAL, <0.5 FAIL |

**Note on panel A5**: The spec panel (CC-5) recommended reclassifying the missing-file case from SKIP to FAIL. If you want to apply this fix now, change Step 3e missing-file guard from "route as SKIP" to "abort with FAIL" — this prevents silent adversarial bypass.

### Task 6.2 — Return Contract Consumer Routing Validation

Manually verify Step 3e routing logic by tracing through these 5 test cases:

| Input | Expected Route |
|-------|---------------|
| Skill response empty or unparseable | Partial (convergence_score: 0.5 fallback) |
| Skill tool error (invocation fails) | FAIL → abort |
| status: success, score: 0.73 | PASS |
| status: partial, score: 0.58 | PARTIAL (score ≥ 0.5) |
| status: failed, score: 0.3 | FAIL |

### Task 6.3 — Invocation Chain End-to-End Check

Verify the complete chain is wired:
1. `roadmap.md` `## Activation` → `Skill sc:roadmap-protocol`
2. `sc-roadmap-protocol/SKILL.md` has `name: sc:roadmap-protocol` (different from command name = no re-entry deadlock)
3. Wave 1A and Wave 2 use `Invoke Skill sc:adversarial-protocol` directly (SKILL-DIRECT — skill-to-skill invocation confirmed available per D-0001 reversal)
4. No Task agent wrapper required; re-entry deadlock prevented by distinct skill names: `sc:roadmap-protocol` ≠ `sc:adversarial-protocol`

**Phase 6 Exit Criteria**: 8-point audit passes. Routing logic verified. Invocation chain is non-circular.

---

## Phase 7: Polish

**Compliance**: STANDARD

### Task 7.1 — Verb-to-Tool Glossary (T05.01)

In `sc-roadmap-protocol/SKILL.md`, add (or verify) a "Verb Glossary" note at the top of the Wave Architecture section:

```markdown
> **Verb → Tool Mapping**: "Invoke Skill" = `Skill` tool (valid from both command context AND skill context per D-0001 reversal). "Dispatch Task agent" = `Task` tool (used for parallelization, not for skill invocation). "Load ref" = Read tool. Never use bare "Invoke" without a tool binding.
```

### Task 7.2 — Wave 1A Step 2 Semantic Fix (T05.02)

The Wave 1A semantic alignment: Verify the rewritten Step 2 uses `Invoke Skill sc:adversarial-protocol` directly (not `Dispatch Task agent`) — skill-to-skill `Skill` tool invocation is confirmed AVAILABLE per D-0001 reversal. The Task agent wrapper is NOT needed and should not be present; it adds unnecessary indirection and context overhead.

### Task 7.3 — Pseudo-CLI Conversion (T05.03)

Scan SKILL.md and refs/ for any remaining pseudo-CLI patterns like:
```
sc:adversarial --compare file1.md,file2.md
```
Replace with direct Skill invocation pattern:
```
Invoke Skill sc:adversarial-protocol with arguments: --compare file1.md,file2.md
```

**Phase 7 Exit Criteria**: No bare "Invoke" verbs without tool binding. No pseudo-CLI patterns. Verb glossary present.

---

## Summary: Files Changed

| File | Phase | Changes |
|------|-------|---------|
| `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` | 2 | Frontmatter (name, allowed-tools); BUG-005 Wave 0 path; BUG-003 orchestrator threshold; T02.03 Wave 1A + Wave 2 Step 3; Return Contract section; add ## Triggers, ## Agent Delegation, ## Error Handling sections |
| `src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md` | 2 | BUG-005 stale path in Prerequisite check |
| `src/superclaude/commands/roadmap.md` | 3 | BUG-001 allowed-tools; BUG-006 Activation section |
| `.claude/commands/sc/roadmap.md` | 3 | Identical (atomic sync with src/) |
| `Makefile` | 4 | Remove skip heuristics (sync-dev, verify-sync); add lint-architecture |
| `.claude/skills/sc-roadmap-protocol/` | 5 | Populated via make sync-dev |

**Total files**: 6 changed + 1 directory populated.

---

---

# Test Suite: sc:roadmap Refactor Effectiveness

**Purpose**: Verify the v2.01 architectural refactor of `sc:roadmap` solved the root causes.
**Designed to run 10 times** — all Suite A/B tests are fully deterministic (same pass/fail every run).
**Measures**: Whether the architectural changes are present, consistent, and structurally correct.

Save as: `tests/test_sc_roadmap_refactor.sh`

```bash
#!/usr/bin/env bash
# =============================================================================
# tests/test_sc_roadmap_refactor.sh
# v2.01 Architecture Refactor — sc:roadmap Effectiveness Test Suite
#
# Run from repo root: bash tests/test_sc_roadmap_refactor.sh
# Safe to run 10x — all deterministic structural checks, no writes.
# =============================================================================

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

PASS=0; FAIL=0; WARN=0
RUN_ID=$(date +%Y%m%d-%H%M%S)
LOGFILE="claudedocs/test-results-${RUN_ID}.log"
mkdir -p claudedocs

log() { echo "$@" | tee -a "$LOGFILE"; }
pass() { PASS=$((PASS+1)); log "  ✅ PASS: $1"; }
fail() { FAIL=$((FAIL+1)); log "  ❌ FAIL: $1"; }
warn() { WARN=$((WARN+1)); log "  ⚠️  WARN: $1"; }
section() { log ""; log "=== $1 ==="; }

log "sc:roadmap Refactor Test Suite"
log "Run ID: $RUN_ID"
log "Date:   $(date)"
log "Commit: $(git log --oneline -1)"
log ""

# =============================================================================
# SUITE A: Invocation Wiring (RC1 fix verification)
# Tests that BUG-001 and BUG-006 are resolved
# =============================================================================
section "SUITE A: Invocation Wiring (RC1 — BUG-001 + BUG-006)"

# A1: roadmap.md has Activation section
if grep -q "## Activation" src/superclaude/commands/roadmap.md; then
  pass "A1: roadmap.md has ## Activation section"
else
  fail "A1: roadmap.md MISSING ## Activation section (BUG-006 not fixed)"
fi

# A2: Activation section references Skill sc:roadmap-protocol (not old file path)
if grep -A5 "## Activation" src/superclaude/commands/roadmap.md | grep -q "Skill sc:roadmap-protocol"; then
  pass "A2: ## Activation references 'Skill sc:roadmap-protocol'"
else
  fail "A2: ## Activation does NOT reference 'Skill sc:roadmap-protocol' — invocation chain broken (BUG-006)"
fi

# A3: Activation section has "Do NOT proceed" warning
if grep -A10 "## Activation" src/superclaude/commands/roadmap.md | grep -qi "do not proceed"; then
  pass "A3: ## Activation has 'Do NOT proceed' warning"
else
  warn "A3: ## Activation missing 'Do NOT proceed' warning (per spec template §5)"
fi

# A4: roadmap.md allowed-tools includes Skill
if grep "allowed-tools" src/superclaude/commands/roadmap.md | grep -q "Skill"; then
  pass "A4: roadmap.md allowed-tools includes 'Skill' (BUG-001 fixed for command)"
else
  fail "A4: roadmap.md allowed-tools MISSING 'Skill' — skill invocation will be blocked (BUG-001)"
fi

# A5: .claude/ copy matches src/ (atomic change requirement)
if diff -q src/superclaude/commands/roadmap.md .claude/commands/sc/roadmap.md >/dev/null 2>&1; then
  pass "A5: .claude/commands/sc/roadmap.md matches src/ (atomic sync verified)"
else
  fail "A5: .claude/commands/sc/roadmap.md DIFFERS from src/ — atomic change group incomplete"
fi

# =============================================================================
# SUITE B: Skill Naming Convention (RC6 fix verification)
# Tests that -protocol naming convention is enforced
# =============================================================================
section "SUITE B: Skill Naming Convention (RC6 + CI Check 9)"

# B1: SKILL.md frontmatter name ends in -protocol
SKILL_NAME=$(grep "^name:" src/superclaude/skills/sc-roadmap-protocol/SKILL.md 2>/dev/null | head -1 | cut -d: -f2 | tr -d ' ')
if echo "$SKILL_NAME" | grep -q ".*-protocol$"; then
  pass "B1: SKILL.md name field ends in '-protocol': $SKILL_NAME"
else
  fail "B1: SKILL.md name field '$SKILL_NAME' does NOT end in '-protocol' (re-entry deadlock risk)"
fi

# B2: Skill name ≠ command name (anti-deadlock)
CMD_NAME="sc:roadmap"
if [ "$SKILL_NAME" != "$CMD_NAME" ]; then
  pass "B2: Skill name ('$SKILL_NAME') ≠ command name ('$CMD_NAME') — no re-entry deadlock"
else
  fail "B2: Skill name EQUALS command name '$SKILL_NAME' — Skill tool will deadlock (re-entry block)"
fi

# B3: SKILL.md has required frontmatter fields
for field in "name:" "description:" "allowed-tools:"; do
  if grep -q "^${field}" src/superclaude/skills/sc-roadmap-protocol/SKILL.md; then
    pass "B3: SKILL.md has required frontmatter field: $field"
  else
    fail "B3: SKILL.md MISSING required frontmatter field: $field (CI Check 8 will fail)"
  fi
done

# B4: SKILL.md allowed-tools includes Skill
if grep "allowed-tools" src/superclaude/skills/sc-roadmap-protocol/SKILL.md | grep -q "Skill"; then
  pass "B4: sc-roadmap-protocol SKILL.md allowed-tools includes 'Skill' (BUG-001 fixed for skill)"
else
  fail "B4: sc-roadmap-protocol SKILL.md allowed-tools MISSING 'Skill' (BUG-001 partial fix incomplete)"
fi

# =============================================================================
# SUITE C: Spec Execution Gap (RC2 fix verification — T02.03)
# Tests that Wave 2 Step 3 has explicit tool binding
# =============================================================================
section "SUITE C: Spec Execution Gap (RC2 — T02.03)"

# C1: Wave 2 Step 3 has sub-steps 3a-3f (not vague "Invoke" prose)
SKILL_FILE="src/superclaude/skills/sc-roadmap-protocol/SKILL.md"
STEPCOUNT=0
for step in "3a" "3b" "3c" "3d" "3e" "3f"; do
  if grep -q "\*\*${step}\*\*\|**${step}:**\|- \*\*${step}" "$SKILL_FILE"; then
    STEPCOUNT=$((STEPCOUNT+1))
  fi
done
if [ $STEPCOUNT -ge 6 ]; then
  pass "C1: Wave 2 Step 3 has all 6 sub-steps 3a-3f present"
elif [ $STEPCOUNT -ge 3 ]; then
  warn "C1: Wave 2 Step 3 has only $STEPCOUNT/6 sub-steps — partial T02.03 implementation"
else
  fail "C1: Wave 2 Step 3 is MISSING sub-steps 3a-3f — still using vague 'Invoke' prose (T02.03 not done)"
fi

# C2: Wave 2 Step 3 uses direct "Invoke Skill sc:adversarial-protocol" (SKILL-DIRECT, not Task agent)
if grep -A50 "### Wave 2" "$SKILL_FILE" | grep -q "Invoke Skill sc:adversarial-protocol\|Invoke.*sc:adversarial-protocol"; then
  pass "C2: Wave 2 uses 'Invoke Skill sc:adversarial-protocol' pattern (SKILL-DIRECT)"
else
  if grep -A50 "### Wave 2" "$SKILL_FILE" | grep -q "Dispatch.*Task\|Task agent"; then
    fail "C2: Wave 2 uses Task agent dispatch — SKILL-DIRECT not applied (D-0001 reversal not reflected)"
  else
    fail "C2: Wave 2 has no tool binding for adversarial dispatch"
  fi
fi

# C3: Wave 1A also uses direct Skill invocation (SKILL-DIRECT, not Task agent or bare prose)
if grep -A30 "Wave 1A" "$SKILL_FILE" | grep -q "Invoke Skill sc:adversarial-protocol\|Invoke.*sc:adversarial-protocol"; then
  pass "C3: Wave 1A uses 'Invoke Skill sc:adversarial-protocol' pattern (SKILL-DIRECT)"
else
  if grep -A30 "Wave 1A" "$SKILL_FILE" | grep -q "Dispatch.*Task\|Task agent"; then
    fail "C3: Wave 1A uses Task agent dispatch — SKILL-DIRECT not applied (D-0001 reversal not reflected)"
  elif grep -A30 "Wave 1A" "$SKILL_FILE" | grep -qi "invoke sc:adversarial[^-]"; then
    fail "C3: Wave 1A still contains bare 'Invoke sc:adversarial' prose — T02.03 incomplete"
  else
    warn "C3: Cannot confirm Wave 1A SKILL-DIRECT pattern"
  fi
fi

# C3.5: Wave 1A has no stale sc-adversarial/ references (only sc-adversarial-protocol)
if grep -A30 "Wave 1A" "$SKILL_FILE" | grep "sc-adversarial" | grep -v "sc-adversarial-protocol" | grep -q .; then
  fail "C3.5: Wave 1A still has stale 'sc-adversarial/' reference (BUG-005 not fully fixed in Wave 1A)"
else
  pass "C3.5: Wave 1A uses 'sc-adversarial-protocol' (no stale sc-adversarial/ paths)"
fi

# C4: Return contract consumption present in SKILL.md (Step 3e)
if grep -q "return-contract.yaml" "$SKILL_FILE"; then
  pass "C4: SKILL.md references return-contract.yaml (return contract routing present)"
else
  fail "C4: SKILL.md has NO reference to return-contract.yaml — RC4 not addressed (return contract routing missing)"
fi

# C5: 3-status routing present (convergence 0.6/0.5 thresholds)
if grep -q "0\.6\|convergence_score" "$SKILL_FILE"; then
  pass "C5: SKILL.md contains convergence threshold routing (0.6 PASS gate)"
else
  warn "C5: No convergence_score routing found in SKILL.md"
fi

# =============================================================================
# SUITE D: Bug Elimination
# =============================================================================
section "SUITE D: Bug Elimination (BUG-003, BUG-005)"

# D1: BUG-005 — No stale sc-adversarial/ paths in SKILL.md
if grep "sc-adversarial" "$SKILL_FILE" | grep -v "sc-adversarial-protocol" | grep -q .; then
  fail "D1: SKILL.md still contains stale 'sc-adversarial/' reference (BUG-005 not fixed)"
else
  pass "D1: No stale 'sc-adversarial/' paths in SKILL.md (BUG-005 fixed)"
fi

# D2: BUG-005 — No stale sc-adversarial/ paths in adversarial-integration.md ref
REF_FILE="src/superclaude/skills/sc-roadmap-protocol/refs/adversarial-integration.md"
if grep "sc-adversarial" "$REF_FILE" | grep -v "sc-adversarial-protocol" | grep -q .; then
  fail "D2: adversarial-integration.md ref still has stale 'sc-adversarial/' path (BUG-005 ref)"
else
  pass "D2: No stale 'sc-adversarial/' paths in adversarial-integration.md ref (BUG-005 ref fixed)"
fi

# D3: BUG-003 — Orchestrator threshold is >=3 (not >=5)
if grep -q ">=.5\|≥.5\|>= 5\| >=5" "$SKILL_FILE"; then
  fail "D3: SKILL.md still has '>=5' orchestrator threshold (BUG-003 not fixed)"
else
  if grep -q ">=.3\|≥.3\|>= 3\|>=3" "$SKILL_FILE"; then
    pass "D3: Orchestrator threshold is >=3 in SKILL.md (BUG-003 fixed)"
  else
    warn "D3: Cannot confirm orchestrator threshold in SKILL.md (grep inconclusive)"
  fi
fi

# D4: Return Contract section exists in SKILL.md
if grep -q "## Return Contract" "$SKILL_FILE"; then
  pass "D4: SKILL.md has '## Return Contract' section (required per §10 of sprint-spec)"
else
  fail "D4: SKILL.md MISSING '## Return Contract' section (every protocol skill must have this)"
fi

# =============================================================================
# SUITE E: Build System (RC7 fix verification)
# =============================================================================
section "SUITE E: Build System (RC7 — lint-architecture)"

# E1: lint-architecture target exists in Makefile
if grep -q "^lint-architecture:" Makefile; then
  pass "E1: lint-architecture target present in Makefile"
else
  fail "E1: lint-architecture target MISSING from Makefile — RC7 not addressed"
fi

# E2: lint-architecture is in .PHONY
if grep "^\.PHONY" Makefile | grep -q "lint-architecture"; then
  pass "E2: lint-architecture is in Makefile .PHONY"
else
  warn "E2: lint-architecture not in .PHONY (non-blocking but sloppy)"
fi

# E3: sync-dev skip heuristic removed
# The heuristic was: cmd_name=${skill_name#sc-} && if cmd exists, continue
# After fix, sc-roadmap-protocol should NOT be skipped when sc-roadmap command exists
if grep -A20 "^sync-dev:" Makefile | grep -q "served by\|cmd_name.*sc-\b.*continue"; then
  fail "E3: Makefile sync-dev STILL has skill-skip heuristic — sc-roadmap-protocol will not sync"
else
  pass "E3: Makefile sync-dev skill-skip heuristic removed"
fi

# E4: verify-sync skip heuristic removed
if grep -A30 "^verify-sync:" Makefile | grep -q "served by.*command"; then
  fail "E4: Makefile verify-sync STILL has 'served by command' skip heuristic"
else
  pass "E4: Makefile verify-sync skill-skip heuristic removed"
fi

# E5: Run lint-architecture and check exit code
log ""
log "  Running: make lint-architecture"
if make lint-architecture >> "$LOGFILE" 2>&1; then
  pass "E5: make lint-architecture exits 0 (architecture policy compliant)"
else
  fail "E5: make lint-architecture FAILED — architecture policy violations exist"
fi

# =============================================================================
# SUITE F: Dev Copy Sync
# =============================================================================
section "SUITE F: Dev Copy Sync (.claude/ parity)"

# F1: .claude/skills/sc-roadmap-protocol/ exists and is non-empty
if [ -d ".claude/skills/sc-roadmap-protocol" ]; then
  FILE_COUNT=$(find .claude/skills/sc-roadmap-protocol -type f | wc -l)
  if [ "$FILE_COUNT" -gt 0 ]; then
    pass "F1: .claude/skills/sc-roadmap-protocol/ exists with $FILE_COUNT files"
  else
    fail "F1: .claude/skills/sc-roadmap-protocol/ exists but is EMPTY — make sync-dev not run"
  fi
else
  fail "F1: .claude/skills/sc-roadmap-protocol/ MISSING from .claude/ — make sync-dev not run"
fi

# F2: SKILL.md is present in .claude/ copy
if [ -f ".claude/skills/sc-roadmap-protocol/SKILL.md" ]; then
  pass "F2: .claude/skills/sc-roadmap-protocol/SKILL.md exists"
else
  fail "F2: .claude/skills/sc-roadmap-protocol/SKILL.md MISSING from .claude/ copy"
fi

# F3: .claude/ SKILL.md matches src/ SKILL.md
if diff -q src/superclaude/skills/sc-roadmap-protocol/SKILL.md .claude/skills/sc-roadmap-protocol/SKILL.md >/dev/null 2>&1; then
  pass "F3: .claude/ SKILL.md matches src/ SKILL.md (no drift)"
else
  fail "F3: .claude/ SKILL.md DIFFERS from src/ — make sync-dev needed or failed"
fi

# F4: All 5 ref files present in .claude/ copy
for ref in extraction-pipeline.md templates.md adversarial-integration.md scoring.md validation.md; do
  if [ -f ".claude/skills/sc-roadmap-protocol/refs/$ref" ]; then
    pass "F4: .claude/refs/$ref exists"
  else
    fail "F4: .claude/refs/$ref MISSING"
  fi
done

# =============================================================================
# SUITE G: Command Line Count (Size constraint)
# =============================================================================
section "SUITE G: Command File Size Compliance"

CMD_LINES=$(wc -l < src/superclaude/commands/roadmap.md)
if [ "$CMD_LINES" -le 150 ]; then
  pass "G1: roadmap.md is $CMD_LINES lines (within ≤150 target)"
elif [ "$CMD_LINES" -le 350 ]; then
  warn "G1: roadmap.md is $CMD_LINES lines (over 150 target but within ≤350 hard limit)"
else
  fail "G1: roadmap.md is $CMD_LINES lines (exceeds ≤350 hard limit — spec violation)"
fi

# =============================================================================
# RESULTS
# =============================================================================
section "RESULTS SUMMARY"
log ""
log "  Run ID:   $RUN_ID"
log "  Total:    $((PASS + FAIL + WARN)) checks"
log "  PASS:     $PASS"
log "  FAIL:     $FAIL"
log "  WARN:     $WARN"
log ""

if [ $FAIL -eq 0 ]; then
  log "  🏆 ALL CHECKS PASSED — sc:roadmap refactor is architecturally correct"
  log "  The v2.01 root causes (RC1, RC2, RC4, RC6, RC7) are addressed for sc:roadmap."
  log ""
  log "  Results saved to: $LOGFILE"
  exit 0
else
  log "  ❌ $FAIL CHECK(S) FAILED — refactor incomplete"
  log "  Review failures above and consult sprint-spec §12–13 for fix guidance."
  log ""
  log "  Results saved to: $LOGFILE"
  exit 1
fi
```

---

## How to Interpret Test Results Across 10 Runs

The test suite is **fully deterministic** — it reads files and checks structure. Running it 10 times against the same codebase produces the same result every time. Use it to:

1. **Before starting**: Run once to confirm baseline failures (expect ~15-20 FAILs)
2. **After each phase**: Run after Phase 2, 3, 4, 5 to see failures decrease
3. **After Phase 7**: Run to confirm all FAILs resolved (expect 0 FAILs)
4. **10x runs after completion**: Confirm zero FAILs on all 10 runs = deterministic correctness

### Pass Trajectory (expected)

| After Phase | Expected FAILs | Fixed By |
|-------------|---------------|----------|
| Baseline | ~18 | — |
| After Phase 2 (SKILL.md) | ~12 | Suites B, C, D (partial) |
| After Phase 3 (Command) | ~8 | Suite A |
| After Phase 4 (Makefile) | ~4 | Suite E (partial) |
| After Phase 5 (Sync) | ~1 | Suite F |
| After Phase 6 (Validation) | 0 | Suite E5 (lint-architecture) |

### What a 0-FAIL Result Means

If 10/10 runs produce 0 FAILs, the following root causes from the sprint-spec are addressed for `sc:roadmap`:

| Root Cause | Fixed By | Test Suite |
|------------|----------|------------|
| RC1: Invocation wiring gap (Skill invocation broken) | BUG-001 + BUG-006 | Suite A |
| RC2: Spec execution gap (Wave 2 Step 3 vague "Invoke") | T02.03 | Suite C |
| RC4: Return contract undefined | Wave 2 Step 3e routing | Suite C4/C5 |
| RC6: No loading order guarantee (partial) | `-protocol` naming + Activation | Suite B |
| RC7: No CI validation | lint-architecture | Suite E |
| BUG-003: Orchestrator threshold | ≥3 alignment | Suite D3 |
| BUG-005: Stale path | sc-adversarial-protocol | Suite D1/D2 |

**What remains unsolved** (out of scope for this tasklist, per sprint-spec §14):
- RC3: Agent dispatch mechanism (debate-orchestrator selection) — v2.02
- RC5: Full Claude behavioral fallback quality gate — v2.02
- Runtime scope control (the rogue-agent problem) — v2.02

---

*Workflow for sc:roadmap refactor under v2.01 Architecture Refactor sprint*
*Spec: .dev/releases/current/v2.01-Architecture-Refactor/sprint-spec.md*
*Generated: 2026-02-24*
