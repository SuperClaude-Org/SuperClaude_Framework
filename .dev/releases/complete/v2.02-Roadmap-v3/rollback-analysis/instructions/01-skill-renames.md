# Instruction Set 01: Skill Directory Renames

**Purpose**: Step-by-step executable guide for recreating all 5 skill directory renames after a git rollback to commit `5733e32` ("Phase 5 complete").

**Scope**: Skill directory renames + SKILL.md frontmatter updates + roadmap SKILL.md body expansion + allowed-tools bug fix + dev copy sync.

**Does NOT cover**: Command file `## Activation` sections, Makefile changes, task-unified.md content extraction. Those are separate instruction sets.

**Working directory**: `/config/workspace/SuperClaude_Framework`

**Governing policy**: `docs/architecture/command-skill-policy.md` (v1.0.0, 2026-02-23)

---

## Prerequisites

Before starting, verify ALL of these conditions:

### 1. Clean git state on the correct branch

```bash
cd /config/workspace/SuperClaude_Framework
git branch --show-current
# Expected: feature/v2.01-Roadmap-V3 (or your working branch)

git status --short
# Expected: no uncommitted changes in src/superclaude/skills/
```

### 2. Pre-rename skill directories exist

```bash
ls -d src/superclaude/skills/sc-adversarial/
ls -d src/superclaude/skills/sc-cleanup-audit/
ls -d src/superclaude/skills/sc-roadmap/
ls -d src/superclaude/skills/sc-task-unified/
ls -d src/superclaude/skills/sc-validate-tests/
# All 5 must exist. If any is missing, the rollback was incomplete.
```

### 3. No `-protocol` directories exist yet

```bash
ls -d src/superclaude/skills/sc-*-protocol/ 2>/dev/null
# Expected: no output (no matches). If any exist, remove them first.
```

### 4. Architecture policy document exists

```bash
ls docs/architecture/command-skill-policy.md
# Must exist. If missing, this is a separate prerequisite (create it first).
```

### 5. Old SKILL.md frontmatter values (for reference)

These are the values you will be replacing. Verify they match before editing:

| Skill | Old `name:` value | Old `allowed-tools:` value |
|-------|-------------------|---------------------------|
| sc-adversarial | `sc:adversarial` | `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` |
| sc-cleanup-audit | `cleanup-audit` | `Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write` |
| sc-roadmap | `sc:roadmap` | `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` |
| sc-task-unified | `sc-task-unified` | `Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` |
| sc-validate-tests | `sc-validate-tests` | `Read, Glob, Grep, TodoWrite` |

---

## Phase 1: Directory Renames (5 git mv operations)

All 5 renames are independent of each other. Execute all 5:

```bash
cd /config/workspace/SuperClaude_Framework

git mv src/superclaude/skills/sc-adversarial src/superclaude/skills/sc-adversarial-protocol
git mv src/superclaude/skills/sc-cleanup-audit src/superclaude/skills/sc-cleanup-audit-protocol
git mv src/superclaude/skills/sc-roadmap src/superclaude/skills/sc-roadmap-protocol
git mv src/superclaude/skills/sc-task-unified src/superclaude/skills/sc-task-unified-protocol
git mv src/superclaude/skills/sc-validate-tests src/superclaude/skills/sc-validate-tests-protocol
```

### Phase 1 Verification

```bash
# Verify all 5 new directories exist
ls -d src/superclaude/skills/sc-adversarial-protocol/
ls -d src/superclaude/skills/sc-cleanup-audit-protocol/
ls -d src/superclaude/skills/sc-roadmap-protocol/
ls -d src/superclaude/skills/sc-task-unified-protocol/
ls -d src/superclaude/skills/sc-validate-tests-protocol/

# Verify no old directories remain
ls -d src/superclaude/skills/sc-adversarial/ 2>/dev/null && echo "ERROR: old dir still exists" || echo "OK"
ls -d src/superclaude/skills/sc-cleanup-audit/ 2>/dev/null && echo "ERROR: old dir still exists" || echo "OK"
ls -d src/superclaude/skills/sc-roadmap/ 2>/dev/null && echo "ERROR: old dir still exists" || echo "OK"
ls -d src/superclaude/skills/sc-task-unified/ 2>/dev/null && echo "ERROR: old dir still exists" || echo "OK"
ls -d src/superclaude/skills/sc-validate-tests/ 2>/dev/null && echo "ERROR: old dir still exists" || echo "OK"

# Verify git tracked the renames
git status --short src/superclaude/skills/
# Expected: 30 renamed files (R  or RM status)
```

**File count per directory**:
- `sc-adversarial-protocol/`: 6 files (SKILL.md, `__init__.py`, 4 refs)
- `sc-cleanup-audit-protocol/`: 12 files (SKILL.md, `__init__.py`, 5 rules, 1 script, 4 templates)
- `sc-roadmap-protocol/`: 7 files (SKILL.md, `__init__.py`, 5 refs)
- `sc-task-unified-protocol/`: 2 files (SKILL.md, `__init__.py`)
- `sc-validate-tests-protocol/`: 3 files (SKILL.md, `__init__.py`, classification-algorithm.yaml)

---

## Phase 2: SKILL.md Frontmatter Updates (5 edits)

### 2.1 sc-adversarial-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`

**Change**: Replace `name:` value only. No body changes.

**Old frontmatter** (lines 1-5):
```yaml
---
name: sc:adversarial
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**New frontmatter** (lines 1-5):
```yaml
---
name: sc:adversarial-protocol
description: Structured adversarial debate, comparison, and merge pipeline for 2-10 artifacts
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**Exact edit**: Change line 2 from `name: sc:adversarial` to `name: sc:adversarial-protocol`

**Verification**:
```bash
head -5 src/superclaude/skills/sc-adversarial-protocol/SKILL.md
# Line 2 must read: name: sc:adversarial-protocol
```

---

### 2.2 sc-cleanup-audit-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md`

**Change**: Replace `name:` value. This also fixes a pre-existing inconsistency (old name lacked `sc:` prefix). No body changes.

**Old frontmatter** (lines 1-10):
```yaml
---
name: cleanup-audit
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"
---
```

**New frontmatter** (lines 1-10):
```yaml
---
name: sc:cleanup-audit-protocol
description: "Multi-pass read-only repository audit producing evidence-backed cleanup recommendations"
category: utility
complexity: high
mcp-servers: [sequential, serena, context7]
personas: [analyzer, architect, devops, qa, refactorer]
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
argument-hint: "[target-path] [--pass surface|structural|cross-cutting|all] [--batch-size N] [--focus infrastructure|frontend|backend|all]"
---
```

**Exact edit**: Change line 2 from `name: cleanup-audit` to `name: sc:cleanup-audit-protocol`

**Verification**:
```bash
head -10 src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md
# Line 2 must read: name: sc:cleanup-audit-protocol
```

---

### 2.3 sc-roadmap-protocol/SKILL.md (COMPLEX -- frontmatter + body changes)

**File**: `src/superclaude/skills/sc-roadmap-protocol/SKILL.md`

This is the ONLY skill with body changes beyond frontmatter. It has THREE changes:
1. Frontmatter `name:` update
2. Frontmatter `allowed-tools:` addition of `Skill`
3. Wave 2 Step 3 body expansion (+17 lines replacing 1 line)

#### 2.3a Frontmatter changes

**Old frontmatter** (lines 1-5):
```yaml
---
name: sc:roadmap
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**New frontmatter** (lines 1-5):
```yaml
---
name: sc:roadmap-protocol
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
---
```

**Exact edits**:
- Line 2: Change `name: sc:roadmap` to `name: sc:roadmap-protocol`
- Line 4: Change `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` to `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill`

#### 2.3b Wave 2 Step 2 update

In the Wave 2 "Behavioral Instructions" section, find step 2. The old text reads:

```
2. Score template compatibility using the algorithm from `refs/scoring.md`
```

Replace with:

```
2. Score template compatibility using the algorithm from `refs/scoring.md`. If `--interactive`: display compatibility scores for all candidate templates, prompt user to confirm or select. If not `--interactive`: use highest-scoring template silently
```

#### 2.3c Wave 2 Step 3 body expansion

This is the major change. In the Wave 2 "Behavioral Instructions" section, find the old step 3. It is a single multi-clause line:

**OLD step 3** (1 line):
```
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Expand model-only agents with the primary persona from Wave 1B. If agent count ≥5, orchestrator is added automatically. Invoke sc:adversarial for multi-roadmap generation per `refs/adversarial-integration.md` "Multi-Roadmap Generation" invocation pattern. Handle return contract per `refs/adversarial-integration.md` "Return Contract Consumption" section. The adversarial output replaces template-based generation.
```

**NEW step 3** (replace the entire old step 3 with this multi-line content):
```
3. If `--multi-roadmap`:
   - **3a [Parse agents]**: Call `Read` tool on `refs/adversarial-integration.md`. Apply the "Agent Specification Parsing" algorithm: split `--agents` value on `,`; for each spec parse `model[:persona[:"instruction"]]` (max 3 segments); validate agent count is 2–10 (abort if out of range per validation rules in the ref).
   - **3b [Expand variants]**: Expand model-only agents (no explicit persona) by assigning the primary persona auto-detected from Wave 1B domain analysis. Record the final expanded agent list.
   - **3c [Add orchestrator if needed]**: If expanded agent count ≥ 3, add a debate-orchestrator agent to coordinate debate rounds and prevent combinatorial explosion. The orchestrator is infrastructure, not a competing variant, and is not counted toward the 2–10 agent limit.
   - **3d [Execute fallback protocol]**: The primary Skill tool invocation path is unavailable in this environment. Fallback protocol executes unconditionally as the sole invocation mechanism. Emit WARNING before proceeding: `"sc:adversarial Skill tool unavailable — executing fallback protocol (fallback_mode: true)"`. Note: this fallback also activates when the Skill tool returns one of three error types: (1) `Skill` not in allowed-tools, (2) skill not found, (3) skill already running.
     - **F1 [Variant generation]**: Use `Task` tool to dispatch one generation agent per expanded agent spec. Each agent receives: source spec file path, assigned model and persona, and instruction to generate a complete roadmap variant. Each variant must contain ≥100 words in its analysis sections. Write each variant to `<output_dir>/variant-<model>-<persona>.md`. F1 must produce ≥2 variant files (agent count ≥ 2 is guaranteed by validation in step 3a).
     - **F2/3 [Diff analysis + single-round debate — merged]**: Use `Task` tool with prompt: `"Read all variant-*.md files in <output_dir>. Write <output_dir>/diff-analysis.md with: (a) a section per variant summarizing its key choices, labeled with the variant filename, and (b) a conflict summary section listing disagreements across variants. Then conduct one debate round identifying which variant best satisfies the source spec requirements and record your recommendation with rationale in diff-analysis.md."` Minimum quality threshold: diff-analysis.md must contain ≥100 words.
     - **F4/5 [Base selection + merge + contract — merged]**: Use `Task` tool with prompt: `"Read <output_dir>/diff-analysis.md and all variant-*.md files. (a) Write <output_dir>/base-selection.md identifying the winning base variant with rationale. (b) Write <output_dir>/merged-output.md incorporating the best elements from all variants into a unified roadmap. (c) Write <output_dir>/return-contract.yaml with exactly these fields: status (success, or partial if unresolved conflicts remain), merged_output_path (<output_dir>/merged-output.md), convergence_score (0.5 # estimated, not measured), fallback_mode (true), artifacts_dir (<output_dir>), unresolved_conflicts (0, or count of unresolved), base_variant (<winning-model:persona>). If merging fails partially, set status: partial and record unresolved_conflicts count. If all steps fail, write return-contract.yaml with status: failed."`
   - **3e [Consume return contract]**: Read `<output_dir>/return-contract.yaml`:
     - **Missing-file guard**: If `return-contract.yaml` does not exist → emit `"return-contract.yaml not found after adversarial execution"` → treat as `status: failed`
     - **YAML parse error**: If file is malformed → catch error → treat as `status: failed`
     - **Status routing** (convergence threshold: 0.6):
       - `status: success` → use `merged_output_path` as roadmap source; record `convergence_score` and `artifacts_dir` in frontmatter; proceed to step 3f
       - `status: partial` AND `convergence_score ≥ 0.6` → proceed with warning logged in extraction.md: `"Adversarial consolidation partial (convergence: XX%). Some conflicts unresolved."`; record `convergence_score` and `artifacts_dir` in frontmatter; proceed to step 3f
       - `status: partial` AND `convergence_score < 0.6` → if `--interactive`: prompt user `"Adversarial convergence is XX% (below 60% threshold). Proceed anyway? [Y/n]"` (Y → proceed as ≥0.6 path; N → abort); if not `--interactive`: abort with `"Adversarial convergence XX% is below 60% threshold. Use --interactive to approve low-convergence results, or revise agents."`
       - `status: failed` → abort roadmap generation: `"sc:adversarial failed. Roadmap generation aborted."` with `artifacts_dir` for debugging if present
     - Canonical schema comment: `# return-contract.yaml fields: status, merged_output_path, convergence_score, fallback_mode, artifacts_dir, unresolved_conflicts, base_variant`
   - **3f [Skip template]**: If step 3e routing reached success or partial-proceed path, skip steps 4–6 of this wave (template-based milestone generation). The adversarial `merged_output_path` content is used as the roadmap source for Waves 3–4. Proceed directly to Wave 2 exit criteria.
```

#### 2.3d Wave 2 Step 5 update

In the Wave 2 "Behavioral Instructions" section, the old step 5 reads:

```
5. Map dependencies between milestones using the dependency mapping rules from `refs/templates.md`. Verify no circular dependencies.
```

Replace with:

```
5. Map dependencies between milestones using the dependency mapping rules from `refs/templates.md`. Validate the dependency graph is acyclic (DAG). If circular dependency detected, abort with `"Circular dependency detected in milestone plan: M<X> → M<Y> → ... → M<X>. Review milestone dependencies."`
```

#### 2.3e Wave 2 Exit Criteria update

The old exit criteria reads:

```
**Exit Criteria**: Milestone structure with effort estimates determined. Emit: `"Wave 2 complete: N milestones planned."`
```

Replace with:

```
**Exit Criteria**: Milestone structure with effort estimates determined. Trigger `sc:save` with milestone structure. Emit: `"Wave 2 complete: N milestones planned."` If `--dry-run`: output structured console preview (FR-018 format — spec info, complexity, persona, template, milestone structure with dependencies, domain distribution, estimated deliverables/risks, output paths) and STOP. Skip Waves 3-4. No files written, no session persistence.
```

#### 2.3 Verification

```bash
# Verify frontmatter
head -5 src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Line 2 must read: name: sc:roadmap-protocol
# Line 4 must contain: Skill (at end of allowed-tools list)

# Verify Wave 2 Step 3 expansion exists
grep -c "\*\*3a \[Parse agents\]" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 1

grep -c "\*\*3f \[Skip template\]" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 1

grep -c "F1 \[Variant generation\]" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 1

grep -c "F4/5 \[Base selection" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 1

# Verify convergence threshold
grep "convergence threshold: 0.6" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 1 match

# Verify fallback WARNING emission
grep "sc:adversarial Skill tool unavailable" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 1 match
```

---

### 2.4 sc-task-unified-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-task-unified-protocol/SKILL.md`

**Change**: Replace `name:` value only. No body changes.

**Old frontmatter** (lines 1-5):
```yaml
---
name: sc-task-unified
description: Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation. Merges orchestration capabilities with MCP compliance into a single coherent interface.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**New frontmatter** (lines 1-5):
```yaml
---
name: sc:task-unified-protocol
description: Unified task execution with intelligent workflow management, MCP compliance enforcement, and multi-agent delegation. Merges orchestration capabilities with MCP compliance into a single coherent interface.
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---
```

**Exact edit**: Change line 2 from `name: sc-task-unified` to `name: sc:task-unified-protocol`

Note: the old name used a hyphen (`sc-task-unified`). The new name uses a colon (`sc:task-unified-protocol`).

**Verification**:
```bash
head -5 src/superclaude/skills/sc-task-unified-protocol/SKILL.md
# Line 2 must read: name: sc:task-unified-protocol
```

---

### 2.5 sc-validate-tests-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-validate-tests-protocol/SKILL.md`

**Change**: Replace `name:` value only. No body changes.

**Old frontmatter** (lines 1-5):
```yaml
---
name: sc-validate-tests
description: Validate tier classification behavior against YAML test specifications. Self-validation skill for /sc-task-unified command testing.
allowed-tools: Read, Glob, Grep, TodoWrite
---
```

**New frontmatter** (lines 1-5):
```yaml
---
name: sc:validate-tests-protocol
description: Validate tier classification behavior against YAML test specifications. Self-validation skill for /sc-task-unified command testing.
allowed-tools: Read, Glob, Grep, TodoWrite
---
```

**Exact edit**: Change line 2 from `name: sc-validate-tests` to `name: sc:validate-tests-protocol`

Note: the old name used a hyphen (`sc-validate-tests`). The new name uses a colon (`sc:validate-tests-protocol`).

**Verification**:
```bash
head -5 src/superclaude/skills/sc-validate-tests-protocol/SKILL.md
# Line 2 must read: name: sc:validate-tests-protocol
```

---

## Phase 3: Bug Fix -- Add `Skill` to All 5 SKILL.md `allowed-tools`

**Context**: BUG-001 from the original implementation. Only `sc-roadmap-protocol/SKILL.md` had `Skill` added to its `allowed-tools`. The other 4 SKILL.md files are missing it. Since all 5 skills may need to invoke other skills (cross-skill invocation), all should include `Skill` in their `allowed-tools`.

### 3.1 sc-adversarial-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-adversarial-protocol/SKILL.md`

**Old line 4**:
```
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
```

**New line 4**:
```
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

### 3.2 sc-cleanup-audit-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-cleanup-audit-protocol/SKILL.md`

**Old line 8**:
```
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write
```

**New line 8**:
```
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(wc *), Bash(find *), Bash(du *), TodoWrite, Task, Write, Skill
```

### 3.3 sc-roadmap-protocol/SKILL.md

Already has `Skill` from Phase 2.3a. No change needed.

### 3.4 sc-task-unified-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-task-unified-protocol/SKILL.md`

**Old line 4**:
```
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
```

**New line 4**:
```
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

### 3.5 sc-validate-tests-protocol/SKILL.md

**File**: `src/superclaude/skills/sc-validate-tests-protocol/SKILL.md`

**Old line 4**:
```
allowed-tools: Read, Glob, Grep, TodoWrite
```

**New line 4**:
```
allowed-tools: Read, Glob, Grep, TodoWrite, Skill
```

### Phase 3 Verification

```bash
# Verify all 5 SKILL.md files contain Skill in allowed-tools
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  echo -n "$skill: "
  grep -c "Skill" src/superclaude/skills/$skill/SKILL.md
done
# Expected: each line shows 1 (or more for roadmap which references Skill in body too)

# More precise check: verify allowed-tools line contains ", Skill"
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  echo -n "$skill: "
  grep "allowed-tools:.*Skill" src/superclaude/skills/$skill/SKILL.md | head -1
done
# Expected: each line shows the allowed-tools line with Skill at the end
```

---

## Phase 4: Dev Copy Sync

After all `src/` changes are complete, sync to `.claude/`:

```bash
cd /config/workspace/SuperClaude_Framework
make sync-dev
```

### Phase 4 Verification

```bash
# Verify all 5 .claude/skills/ directories exist
ls -d .claude/skills/sc-adversarial-protocol/
ls -d .claude/skills/sc-cleanup-audit-protocol/
ls -d .claude/skills/sc-roadmap-protocol/
ls -d .claude/skills/sc-task-unified-protocol/
ls -d .claude/skills/sc-validate-tests-protocol/

# Verify no old .claude/skills/ directories remain
ls -d .claude/skills/sc-adversarial/ 2>/dev/null && echo "ERROR: old dir exists" || echo "OK"
ls -d .claude/skills/sc-cleanup-audit/ 2>/dev/null && echo "ERROR: old dir exists" || echo "OK"
ls -d .claude/skills/sc-roadmap/ 2>/dev/null && echo "ERROR: old dir exists" || echo "OK"
ls -d .claude/skills/sc-task-unified/ 2>/dev/null && echo "ERROR: old dir exists" || echo "OK"
ls -d .claude/skills/sc-validate-tests/ 2>/dev/null && echo "ERROR: old dir exists" || echo "OK"

# Verify content parity (src/ minus __init__.py should equal .claude/)
make verify-sync
# Expected: PASS (no drift detected)

# Verify SKILL.md name fields match in .claude/ copies
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  echo "=== $skill ==="
  grep "^name:" .claude/skills/$skill/SKILL.md
done
# Expected:
# sc-adversarial-protocol:    name: sc:adversarial-protocol
# sc-cleanup-audit-protocol:  name: sc:cleanup-audit-protocol
# sc-roadmap-protocol:        name: sc:roadmap-protocol
# sc-task-unified-protocol:   name: sc:task-unified-protocol
# sc-validate-tests-protocol: name: sc:validate-tests-protocol
```

---

## Phase 5: Final Comprehensive Verification

Run all checks to confirm the entire skill rename operation is correct:

```bash
cd /config/workspace/SuperClaude_Framework

# 1. Verify git sees 30 renamed files in src/superclaude/skills/
git status --short src/superclaude/skills/ | wc -l
# Expected: 30

# 2. Verify all SKILL.md name fields end in -protocol
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  name=$(grep "^name:" src/superclaude/skills/$skill/SKILL.md | sed 's/name: //')
  echo "$skill -> $name"
  echo "$name" | grep -q "\-protocol$" && echo "  PASS" || echo "  FAIL: name does not end in -protocol"
done

# 3. Verify all SKILL.md name fields use sc: prefix (not sc- or bare)
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  name=$(grep "^name:" src/superclaude/skills/$skill/SKILL.md | sed 's/name: //')
  echo "$name" | grep -q "^sc:" && echo "$skill: PASS (sc: prefix)" || echo "$skill: FAIL (missing sc: prefix)"
done

# 4. Verify roadmap SKILL.md has Skill in allowed-tools and Wave 2 Step 3 expansion
grep "allowed-tools:.*Skill" src/superclaude/skills/sc-roadmap-protocol/SKILL.md | head -1
grep "3a \[Parse agents\]" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
grep "3f \[Skip template\]" src/superclaude/skills/sc-roadmap-protocol/SKILL.md
# Expected: 3 matches (1 per grep)

# 5. Verify all 5 SKILL.md files have Skill in allowed-tools (bug fix)
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  grep -q "allowed-tools:.*Skill" src/superclaude/skills/$skill/SKILL.md && echo "$skill: PASS" || echo "$skill: FAIL"
done
# Expected: 5 PASS lines

# 6. File counts per directory
for skill in sc-adversarial-protocol sc-cleanup-audit-protocol sc-roadmap-protocol sc-task-unified-protocol sc-validate-tests-protocol; do
  count=$(find src/superclaude/skills/$skill/ -type f | wc -l)
  echo "$skill: $count files"
done
# Expected:
# sc-adversarial-protocol: 6
# sc-cleanup-audit-protocol: 12
# sc-roadmap-protocol: 7
# sc-task-unified-protocol: 2
# sc-validate-tests-protocol: 3
```

---

## Rollback Procedure

If something goes wrong during any phase, use this procedure to undo all changes and return to the pre-rename state.

### Option A: Full git rollback (recommended if no other work is intermixed)

```bash
cd /config/workspace/SuperClaude_Framework

# Undo all staged and unstaged changes in skills/
git checkout HEAD -- src/superclaude/skills/

# Remove any .claude/skills/ directories that were created
rm -rf .claude/skills/sc-adversarial-protocol
rm -rf .claude/skills/sc-cleanup-audit-protocol
rm -rf .claude/skills/sc-roadmap-protocol
rm -rf .claude/skills/sc-task-unified-protocol
rm -rf .claude/skills/sc-validate-tests-protocol

# Re-sync .claude/ from restored src/
make sync-dev

# Verify
ls -d src/superclaude/skills/sc-adversarial/
ls -d src/superclaude/skills/sc-cleanup-audit/
ls -d src/superclaude/skills/sc-roadmap/
ls -d src/superclaude/skills/sc-task-unified/
ls -d src/superclaude/skills/sc-validate-tests/
```

### Option B: Manual reverse (if you need to preserve other changes)

```bash
cd /config/workspace/SuperClaude_Framework

# Step 1: Reverse the git mv operations
git mv src/superclaude/skills/sc-adversarial-protocol src/superclaude/skills/sc-adversarial
git mv src/superclaude/skills/sc-cleanup-audit-protocol src/superclaude/skills/sc-cleanup-audit
git mv src/superclaude/skills/sc-roadmap-protocol src/superclaude/skills/sc-roadmap
git mv src/superclaude/skills/sc-task-unified-protocol src/superclaude/skills/sc-task-unified
git mv src/superclaude/skills/sc-validate-tests-protocol src/superclaude/skills/sc-validate-tests

# Step 2: Restore original SKILL.md frontmatter from commit 5733e32
git checkout 5733e32 -- src/superclaude/skills/sc-adversarial/SKILL.md
git checkout 5733e32 -- src/superclaude/skills/sc-cleanup-audit/SKILL.md
git checkout 5733e32 -- src/superclaude/skills/sc-roadmap/SKILL.md
git checkout 5733e32 -- src/superclaude/skills/sc-task-unified/SKILL.md
git checkout 5733e32 -- src/superclaude/skills/sc-validate-tests/SKILL.md

# Step 3: Remove .claude/ protocol directories
rm -rf .claude/skills/sc-adversarial-protocol
rm -rf .claude/skills/sc-cleanup-audit-protocol
rm -rf .claude/skills/sc-roadmap-protocol
rm -rf .claude/skills/sc-task-unified-protocol
rm -rf .claude/skills/sc-validate-tests-protocol

# Step 4: Re-sync
make sync-dev
make verify-sync
```

### Rollback verification

```bash
# Confirm old directories are back
ls -d src/superclaude/skills/sc-adversarial/
ls -d src/superclaude/skills/sc-cleanup-audit/
ls -d src/superclaude/skills/sc-roadmap/
ls -d src/superclaude/skills/sc-task-unified/
ls -d src/superclaude/skills/sc-validate-tests/

# Confirm no -protocol directories exist
ls -d src/superclaude/skills/sc-*-protocol/ 2>/dev/null
# Expected: no output

# Confirm old name values restored
grep "^name:" src/superclaude/skills/sc-adversarial/SKILL.md
# Expected: name: sc:adversarial

grep "^name:" src/superclaude/skills/sc-cleanup-audit/SKILL.md
# Expected: name: cleanup-audit

grep "^name:" src/superclaude/skills/sc-roadmap/SKILL.md
# Expected: name: sc:roadmap

grep "^name:" src/superclaude/skills/sc-task-unified/SKILL.md
# Expected: name: sc-task-unified

grep "^name:" src/superclaude/skills/sc-validate-tests/SKILL.md
# Expected: name: sc-validate-tests
```

---

## Summary of All Changes

| Skill | Directory Rename | `name:` Field Change | `allowed-tools:` Change | Body Changes |
|-------|-----------------|---------------------|------------------------|-------------|
| adversarial | `sc-adversarial` -> `sc-adversarial-protocol` | `sc:adversarial` -> `sc:adversarial-protocol` | Add `, Skill` (bug fix) | None |
| cleanup-audit | `sc-cleanup-audit` -> `sc-cleanup-audit-protocol` | `cleanup-audit` -> `sc:cleanup-audit-protocol` | Add `, Skill` (bug fix) | None |
| roadmap | `sc-roadmap` -> `sc-roadmap-protocol` | `sc:roadmap` -> `sc:roadmap-protocol` | Add `, Skill` (per design) | Wave 2 Steps 2, 3 (expansion to 3a-3f), 5, exit criteria |
| task-unified | `sc-task-unified` -> `sc-task-unified-protocol` | `sc-task-unified` -> `sc:task-unified-protocol` | Add `, Skill` (bug fix) | None |
| validate-tests | `sc-validate-tests` -> `sc-validate-tests-protocol` | `sc-validate-tests` -> `sc:validate-tests-protocol` | Add `, Skill` (bug fix) | None |

**Total files affected**: 30 renamed + 5 SKILL.md content edits = 30 files touched in `src/superclaude/skills/`.

**Design artifacts specifying the roadmap body changes**:
- `D-0006` (`artifacts/D-0006/spec.md`): Sub-step decomposition (3a-3f)
- `D-0007` (`artifacts/D-0007/spec.md`): Fallback protocol state machine (F1, F2/3, F4/5)
- `D-0008` (`artifacts/D-0008/spec.md`): Return contract routing logic (step 3e)

All artifact paths are relative to `.dev/releases/current/v2.01-Roadmap-v3/tasklist/`.

---

## Cross-References

| Document | Path | Relevance |
|----------|------|-----------|
| Architecture policy | `docs/architecture/command-skill-policy.md` | Mandates naming convention and migration checklist |
| Context: skill renames to planning | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/context/skill-renames-to-planning.md` | Traces each rename to its planning origins |
| Framework synthesis A | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/framework-synthesis-A.md` | Complete change inventory and atomic groups |
| Framework synthesis B | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/framework-synthesis-B.md` | Bug report (BUG-001: allowed-tools gap) |
| Master traceability | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/context/master-traceability.md` | Decision-to-implementation matrix |
