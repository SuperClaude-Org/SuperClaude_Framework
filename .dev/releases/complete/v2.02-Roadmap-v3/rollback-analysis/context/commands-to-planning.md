# Context Linking: Framework Command Changes to Dev Planning & Artifact Origins

**Analysis Date:** 2026-02-24
**Branch:** `feature/v2.01-Roadmap-V3`
**Baseline Commit:** `9060a65`
**Scope:** All 5 modified command files (10 copies: 5 in `src/superclaude/commands/`, 5 in `.claude/commands/sc/`)

---

## Methodology

Each command file change is traced to:
1. **Tasklist task(s)** from `tasklist-P6.md` (the canonical tasklist)
2. **Decision artifact(s)** (D-xxxx series) from the `artifacts/` directory
3. **Architecture policy section(s)** from `docs/architecture/command-skill-policy.md`
4. **Evidence record(s)** from the `evidence/` directory
5. **Acceptance criteria** quoted from the tasklist
6. **Discrepancies** between plan and implementation

All file paths are relative to the repository root unless prefixed with `TASKLIST_ROOT`, which expands to `.dev/releases/current/v2.01-Roadmap-v3/`.

---

## 1. `adversarial.md`

**Files:**
- `src/superclaude/commands/adversarial.md`
- `.claude/commands/sc/adversarial.md`

**Change Summary:** +8 lines. New `## Activation` section inserted (lines 50-57) directing `Skill sc:adversarial-protocol` invocation. No content removed.

### 1.1 Tasklist Tasks

| Task ID | Roadmap Item | Phase | Description | Tasklist Location |
|---------|-------------|-------|-------------|-------------------|
| *No dedicated task* | *N/A* | *N/A* | The adversarial command's `## Activation` addition is not explicitly listed as a standalone task in the tasklist | `tasklist-P6.md` -- absent |

**Note:** The tasklist (`tasklist-P6.md`) focuses on the `sc:roadmap` adversarial pipeline remediation. The adversarial command's `## Activation` section was added as part of the broader command-skill decoupling mandate from the architecture policy, not from a specific tasklist task. The closest tasks are:
- **T02.01** (R-004): `Skill` in allowed-tools for `roadmap.md` -- but this targets the roadmap command, not adversarial
- **T02.02** (R-005): `Skill` in allowed-tools for SKILL.md -- targets the roadmap skill

The adversarial command modification was driven directly by the architecture policy, outside the tasklist's sprint scope.

### 1.2 Decision Artifacts

| Artifact | Relevance | Path |
|----------|-----------|------|
| *None directly* | No D-xxxx artifact specifically mandates the adversarial command's `## Activation` section | N/A |

The architecture policy (Section "Migration Checklist, Phase 2") is the sole authority mandating this change.

### 1.3 Architecture Policy Sections

| Section | Lines | Governing Rule | Quote |
|---------|-------|----------------|-------|
| **Command File Contract (Tier 0)** | policy lines 69-128 | Template and hard constraints | "MUST have `## Activation` section if a protocol skill exists" |
| **Naming Convention** | policy lines 52-66 | `-protocol` suffix rule | "Protocol skills MUST end in `-protocol`" |
| **Migration Checklist, Phase 2** | policy lines 289-296 | Operational step | "Add `## Activation` section with `Skill sc:<name>-protocol` directive" |
| **CI Enforcement, Check 6** | policy line 262 | Lint enforcement | "Command with matching `-protocol` skill directory missing `## Activation` section" = ERROR |

### 1.4 Evidence Records

| Evidence | Path | Result |
|----------|------|--------|
| *None* | N/A | No evidence record exists for the adversarial command's `## Activation` addition |

### 1.5 Acceptance Criteria

No acceptance criteria exist in the tasklist for this specific command change. The architecture policy's hard constraints serve as the de facto acceptance criteria:
- `## Activation` section present
- References `Skill sc:adversarial-protocol`
- Includes "Do NOT proceed" warning
- Command remains within line limits

### 1.6 Discrepancies

| # | Discrepancy | Severity | Detail |
|---|-------------|----------|--------|
| 1 | **No tasklist task** | MEDIUM | The adversarial command change has no corresponding task in `tasklist-P6.md`. It was executed as a side-effect of the architecture policy, not as a planned sprint task. |
| 2 | **`Skill` not in allowed-tools** | HIGH | The command's frontmatter `allowed-tools` does not exist (the adversarial command uses `mcp-servers` instead). However, the `## Activation` section mandates `Skill` tool invocation. If Claude Code enforces frontmatter tool whitelists, this is a latent bug. The policy Check 8 requires `allowed-tools` in SKILL.md but does not mandate it in the command frontmatter. |
| 3 | **No evidence artifact** | LOW | No D-xxxx artifact or evidence record validates this change. The architecture policy's lint checks (`make lint-architecture` Check 4) are the intended validation mechanism, but Phase 3 (Build System) was not completed. |

---

## 2. `cleanup-audit.md`

**Files:**
- `src/superclaude/commands/cleanup-audit.md`
- `.claude/commands/sc/cleanup-audit.md`

**Change Summary:** +8 lines. New `## Activation` section inserted (lines 35-41) directing `Skill sc:cleanup-audit-protocol` invocation. No content removed.

### 2.1 Tasklist Tasks

| Task ID | Roadmap Item | Phase | Description | Tasklist Location |
|---------|-------------|-------|-------------|-------------------|
| *No dedicated task* | *N/A* | *N/A* | Not explicitly listed in the tasklist | `tasklist-P6.md` -- absent |

Same situation as `adversarial.md`: the cleanup-audit command modification was driven by the architecture policy, not by a tasklist task. The sprint scope was limited to the `sc:roadmap` adversarial pipeline.

### 2.2 Decision Artifacts

| Artifact | Relevance | Path |
|----------|-----------|------|
| *None directly* | No D-xxxx artifact targets the cleanup-audit command | N/A |

### 2.3 Architecture Policy Sections

| Section | Lines | Governing Rule | Quote |
|---------|-------|----------------|-------|
| **Command File Contract (Tier 0)** | policy lines 69-128 | Template and hard constraints | "MUST have `## Activation` section if a protocol skill exists" |
| **Migration Checklist, Phase 2** | policy lines 289-296 | Operational step | "Add `## Activation` section with `Skill sc:<name>-protocol` directive" |
| **CI Enforcement, Check 6** | policy line 262 | Lint enforcement | ERROR if `## Activation` missing |

### 2.4 Evidence Records

| Evidence | Path | Result |
|----------|------|--------|
| *None* | N/A | No evidence record exists for this change |

### 2.5 Acceptance Criteria

No tasklist acceptance criteria. Architecture policy hard constraints apply (same as adversarial.md).

### 2.6 Discrepancies

| # | Discrepancy | Severity | Detail |
|---|-------------|----------|--------|
| 1 | **No tasklist task** | MEDIUM | Same as adversarial.md -- no sprint task covers this change. |
| 2 | **`Skill` not in allowed-tools** | HIGH | The cleanup-audit command uses `mcp-servers: [sequential, serena, context7]` in frontmatter but has no `allowed-tools` field. The `## Activation` section requires `Skill` tool invocation. Same latent bug risk as adversarial.md. |
| 3 | **Frontmatter inconsistency** | LOW | The cleanup-audit command uses `mcp-servers` and `personas` fields while the architecture policy template specifies `allowed-tools`. The command frontmatter schema differs from the policy template. |

---

## 3. `roadmap.md`

**Files:**
- `src/superclaude/commands/roadmap.md`
- `.claude/commands/sc/roadmap.md`

**Change Summary:** +5 lines, -2 lines (net +3). `Skill` added to `allowed-tools` frontmatter (line 4). `## Activation` section rewritten from file-path loading to skill invocation (lines 70-74). Frontmatter already used `allowed-tools` format.

### 3.1 Tasklist Tasks

| Task ID | Roadmap Item | Phase | Description | Tasklist Location |
|---------|-------------|-------|-------------|-------------------|
| **T02.01** | R-004 | Phase 2: Invocation Wiring | `Skill` in allowed-tools -- roadmap command (Task 1.1) | `tasklist-P6.md` Deliverable Registry line 79 |
| **T02.02** | R-005 | Phase 2: Invocation Wiring | `Skill` in allowed-tools -- SKILL.md (Task 1.2) | `tasklist-P6.md` Deliverable Registry line 80 |

**T02.01** is the primary task mandating the `roadmap.md` command file change. T02.02 targets the skill file (SKILL.md), not the command.

**From the Tasklist Index (line 106):**
> "Phase 2: Invocation Wiring Restoration | T02.01-T02.03 | Skill tool in allowed-tools; Wave 2 step 3 rewritten with invocation + fallback | STRICT: 1, STANDARD: 0, LIGHT: 2, EXEMPT: 0"

### 3.2 Decision Artifacts

| Artifact | Task | Path | Key Content |
|----------|------|------|-------------|
| **D-0004** | T02.01 | `TASKLIST_ROOT/tasklist/artifacts/D-0004/evidence.md` | Single-line `, Skill` addition to roadmap.md allowed-tools list. Tier: LIGHT. |
| **D-0005** | T02.02 | `TASKLIST_ROOT/tasklist/artifacts/D-0005/evidence.md` | Same addition in SKILL.md file. Tier: LIGHT. |

### 3.3 Architecture Policy Sections

| Section | Lines | Governing Rule | Quote |
|---------|-------|----------------|-------|
| **Command File Contract (Tier 0)** | policy lines 69-128 | `## Activation` template | "`## Activation` MUST name the exact skill: `sc:<name>-protocol`" |
| **Tiered Loading Architecture** | policy lines 22-44 | Loading flow | "Agent calls Skill tool -> sc:adversarial-protocol/SKILL.md loaded" |
| **Why Separate Names?** | policy lines 46-48 | Re-entry avoidance | "Using `sc:adversarial-protocol` as the skill name avoids [the re-entry block] entirely" |
| **Migration Checklist, Phase 2** | policy lines 289-296 | Operational step | "Trim to <=150 lines; Add `## Activation` section" |
| **CI Enforcement, Check 7** | policy line 263 | Activation reference | "`## Activation` section does not contain `Skill sc:<name>-protocol`" = ERROR |

### 3.4 Evidence Records

| Evidence | Path | Result |
|----------|------|--------|
| **T02.01 evidence** | `TASKLIST_ROOT/tasklist/evidence/T02.01/result.md` | PASS -- grep verification confirmed `Skill` present in roadmap.md allowed-tools |
| **T02.02 evidence** | `TASKLIST_ROOT/tasklist/evidence/T02.02/result.md` | PASS -- grep verification confirmed `Skill` present in SKILL.md allowed-tools |

**Checkpoint confirmation:** CP-P02-END.md states: "PASS -- grep verification returned PASS for both files. `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` confirmed in both."

### 3.5 Acceptance Criteria

**From the Deliverable Registry (tasklist-P6.md line 79):**
- D-0004: "Skill in allowed-tools (roadmap.md)" -- Tier LIGHT, Verification: Sanity check

**From the Execution Log Template (tasklist-P6.md line 392):**
- Validation command: `grep -q "Skill" src/superclaude/commands/roadmap.md`

**From CP-P02-END Exit Criteria:**
> "Both grep verification tests return PASS: PASS -- T02.01 PASS, T02.02 PASS."

### 3.6 Discrepancies

| # | Discrepancy | Severity | Detail |
|---|-------------|----------|--------|
| 1 | **Activation section rewrite not explicitly tasked** | LOW | T02.01 mandates adding `Skill` to allowed-tools. The rewrite of the `## Activation` section from file-path loading (`Load and execute from src/superclaude/skills/sc-roadmap/SKILL.md`) to skill invocation (`Skill sc:roadmap-protocol`) was driven by the architecture policy, not a specific tasklist task. However, this is consistent with the policy's Phase 2 migration step. |
| 2 | **Roadmap command is the only command with `allowed-tools` frontmatter** | LOW | The other 4 commands use `mcp-servers` instead. This pre-existing inconsistency means D-0004's grep validation only works for roadmap.md. |

---

## 4. `task-unified.md`

**Files:**
- `src/superclaude/commands/task-unified.md`
- `.claude/commands/sc/task-unified.md`

**Change Summary:** +24 lines, -485 lines (net -461). **81% content extraction.** The command was reduced from 567 lines to 106 lines. Entire tier classification engine, compliance checklists, MCP integration matrix, sub-agent delegation tables, escape hatches, and metrics were removed and the command was reduced to: frontmatter, flag tables, examples, `## Activation` section (lines 86-92), behavioral summary, and boundaries.

### 4.1 Tasklist Tasks

| Task ID | Roadmap Item | Phase | Description | Tasklist Location |
|---------|-------------|-------|-------------|-------------------|
| *No dedicated task* | *N/A* | *N/A* | The task-unified command's massive content extraction is not explicitly listed as a standalone task in the tasklist | `tasklist-P6.md` -- absent |

**Critical context:** The tasklist's Source Snapshot (line 18) states the sprint "modifies 4 files across 3 skill packages (`sc-roadmap`, `sc-adversarial`, `roadmap` command)." The `task-unified` command is NOT listed as a modified file in the sprint scope. The 81% content extraction was driven entirely by the architecture policy's migration mandate, executed as ancillary work outside the sprint's defined scope.

The architecture policy's backlog section (line 318) explicitly lists: "Split `task-unified.md` command (567L) | Low | Already has protocol skill" -- indicating this was recognized as needed but classified as LOW priority backlog work.

### 4.2 Decision Artifacts

| Artifact | Relevance | Path |
|----------|-----------|------|
| *None directly* | No D-xxxx artifact mandates or specifies the task-unified content extraction | N/A |

### 4.3 Architecture Policy Sections

| Section | Lines | Governing Rule | Quote |
|---------|-------|----------------|-------|
| **Command File Contract, Hard Constraints** | policy lines 113-121 | Line limit enforcement | "<=150 lines total; NO protocol YAML blocks, step definitions, or scoring algorithms" |
| **Command-Only Files** | policy lines 122-128 | Size thresholds | "WARN at 200 lines, ERROR at 500 lines; Commands exceeding 500 lines MUST be split" |
| **Migration Checklist, Phase 2** | policy lines 289-296 | Operational steps | "Trim to <=150 lines; Add `## Activation` section; Remove any inline protocol YAML; Keep: metadata, usage, arguments, examples, behavioral summary, boundaries" |
| **Backlog** | policy line 318 | Priority assignment | "Split `task-unified.md` command (567L) | Low | Already has protocol skill" |
| **CI Enforcement, Check 3/4** | policy lines 259-260 | Size enforcement | "Command file >200 lines" = WARN; "Command file >500 lines" = ERROR |

### 4.4 Evidence Records

| Evidence | Path | Result |
|----------|------|--------|
| *None* | N/A | No evidence record validates the task-unified content extraction |

### 4.5 Acceptance Criteria

No tasklist acceptance criteria. Architecture policy hard constraints serve as de facto criteria:
- Command <= 150 lines (achieved: 106 lines)
- No protocol YAML blocks
- `## Activation` section present referencing `sc:task-unified-protocol`
- Includes "Do NOT proceed" warning
- Behavioral summary <= 5 sentences

### 4.6 Discrepancies

| # | Discrepancy | Severity | Detail |
|---|-------------|----------|--------|
| 1 | **No tasklist task -- highest-risk change has no sprint mandate** | HIGH | The task-unified 81% content extraction is the single largest and riskiest change in the release (per framework-synthesis-A Section 7.2). Yet it has no tasklist task, no D-xxxx artifact, no evidence record, and no acceptance criteria. It was executed as ancillary policy-compliance work outside the sprint's defined scope of "4 files across 3 skill packages." |
| 2 | **Backlog item executed prematurely** | MEDIUM | The architecture policy explicitly placed this as a "Low" priority backlog item with trigger "Already has protocol skill." The extraction was executed during this sprint despite not being in the sprint scope. |
| 3 | **No verification of extracted content landing in skill** | HIGH | The 461 lines removed from the command must exist in `sc-task-unified-protocol/SKILL.md` for the system to function. No evidence record verifies that the skill contains the full extracted content. If the skill is incomplete, the command becomes a syntax reference with no behavioral guidance. |
| 4 | **Frontmatter `name` field is `task`, not `task-unified`** | LOW | The command frontmatter reads `name: task` (line 2) while the architecture policy expects the command name to match the skill name pattern. The skill is `sc:task-unified-protocol`, but the command name is `task`. This is a pre-existing inconsistency not introduced by this change. |

---

## 5. `validate-tests.md`

**Files:**
- `src/superclaude/commands/validate-tests.md`
- `.claude/commands/sc/validate-tests.md`

**Change Summary:** +10 lines, -2 lines (net +8). New `## Activation` section inserted (lines 98-104). `## See Also` paths updated from `skills/sc-validate-tests/` to `skills/sc-validate-tests-protocol/` (lines 109-110).

### 5.1 Tasklist Tasks

| Task ID | Roadmap Item | Phase | Description | Tasklist Location |
|---------|-------------|-------|-------------|-------------------|
| *No dedicated task* | *N/A* | *N/A* | Not explicitly listed in the tasklist | `tasklist-P6.md` -- absent |

Same situation as adversarial.md and cleanup-audit.md: driven by the architecture policy, outside the sprint scope.

### 5.2 Decision Artifacts

| Artifact | Relevance | Path |
|----------|-----------|------|
| *None directly* | No D-xxxx artifact targets the validate-tests command | N/A |

### 5.3 Architecture Policy Sections

| Section | Lines | Governing Rule | Quote |
|---------|-------|----------------|-------|
| **Command File Contract (Tier 0)** | policy lines 69-128 | Template and hard constraints | "MUST have `## Activation` section if a protocol skill exists" |
| **Migration Checklist, Phase 2** | policy lines 289-296 | Operational step | "Add `## Activation` section" |
| **CI Enforcement, Check 6** | policy line 262 | Lint enforcement | ERROR if `## Activation` missing |

### 5.4 Evidence Records

| Evidence | Path | Result |
|----------|------|--------|
| *None* | N/A | No evidence record exists for this change |

### 5.5 Acceptance Criteria

No tasklist acceptance criteria. Architecture policy hard constraints apply.

### 5.6 Discrepancies

| # | Discrepancy | Severity | Detail |
|---|-------------|----------|--------|
| 1 | **No tasklist task** | MEDIUM | Same pattern as adversarial.md and cleanup-audit.md. |
| 2 | **See Also path updated but `## Classification Algorithm` path NOT updated** | MEDIUM | Line 63 reads `Reference: skills/sc-validate-tests/classification-algorithm.yaml` using the OLD directory name. The See Also section (lines 109-110) was updated to `-protocol` but this reference was missed. If this path is resolved at runtime, it will fail. |
| 3 | **No frontmatter** | LOW | The validate-tests command has no YAML frontmatter at all (no `name`, `description`, `allowed-tools`, etc.). The architecture policy template requires frontmatter. This is a pre-existing gap not introduced by this change, but it means `make lint-architecture` Check 5 (frontmatter validation) would flag an issue on the command file if it checks commands too (currently Check 5 targets SKILL.md files only). |

---

## Cross-Cutting Analysis

### A. Coverage Gap: 4 of 5 Commands Have No Sprint Task

| Command | Has Tasklist Task? | Has D-xxxx Artifact? | Has Evidence Record? |
|---------|-------------------|---------------------|---------------------|
| `adversarial.md` | NO | NO | NO |
| `cleanup-audit.md` | NO | NO | NO |
| `roadmap.md` | YES (T02.01, T02.02) | YES (D-0004, D-0005) | YES (T02.01, T02.02) |
| `task-unified.md` | NO | NO | NO |
| `validate-tests.md` | NO | NO | NO |

Only `roadmap.md` has full traceability through the sprint's formal planning chain. The other 4 commands were modified as ancillary work driven by the architecture policy's migration mandate, executed during the sprint but outside its formal scope.

### B. Architecture Policy as Sole Authority

For 4 of 5 commands, the **sole governing authority** for the change is `docs/architecture/command-skill-policy.md`:

- **Section "Migration Checklist, Phase 2"** (lines 289-296) mandates all 5 command modifications
- **Section "Command File Contract"** (lines 69-128) defines the template and constraints
- **Section "CI Enforcement"** (lines 253-266) defines the automated validation checks

The tasklist (`tasklist-P6.md`) and its decision artifacts (D-0001 through D-0008) only cover the `roadmap.md` modifications within the context of the adversarial pipeline remediation sprint.

### C. Planned vs. Implemented: Scope Comparison

**Planned (tasklist-P6.md Source Snapshot, line 18):**
> "Sprint modifies 4 files across 3 skill packages (`sc-roadmap`, `sc-adversarial`, `roadmap` command)."

**Implemented (framework-synthesis-A Section 2):**
- 10 command files modified (5 commands x 2 locations)
- 30 skill files renamed
- 1 Makefile modified
- 2 documentation files created
- 25 new `.claude/skills/` dev copies

**Scope expansion:** The sprint expanded from 4 planned file modifications to 68 files changed. The planned scope covered only the roadmap-adversarial integration wiring; the implemented scope includes the full command-skill decoupling migration across all 5 paired commands.

### D. Validation Gap

The architecture policy defines 10 CI enforcement checks via `make lint-architecture`. However:

1. **Phase 3 (Build System) was not completed** -- the `lint-architecture` target was added to the Makefile but was part of the unplanned scope expansion
2. **No checkpoint exists for Phases 3-6** -- CP-P03-END through CP-P06-END have not been produced
3. **The lint-architecture target has not been run** against the modified commands as a formal validation step
4. **4 of 5 commands have zero validation evidence** -- only roadmap.md has grep-verified evidence records

### E. Skill Directory Rename Traceability

The 5 skill directory renames (`sc-{name}` to `sc-{name}-protocol`) are governed by:

| Governing Document | Section | Mandate |
|-------------------|---------|---------|
| `command-skill-policy.md` | Migration Checklist, Phase 1 (lines 279-287) | Directory rename table with old/new names and SKILL.md name fields |
| `command-skill-policy.md` | Naming Convention (lines 52-66) | "Protocol skills MUST end in `-protocol`; Protocol skill directories MUST be prefixed with `sc-` and suffixed with `-protocol`" |
| `command-skill-policy.md` | CI Enforcement, Check 9 (line 265) | "Skill directory `sc-*-protocol/` but SKILL.md `name` field doesn't end in `-protocol`" = ERROR |

The renames were executed as Phase 1 of the policy migration. Evidence of execution is in the git status (`RM` operations) and CP-P01-END.md prerequisite checks, but no dedicated D-xxxx artifact documents the rename execution itself.

---

## Appendix: File Reference Quick-Lookup

### Source Documents

| Document | Full Path |
|----------|-----------|
| Canonical Tasklist | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/tasklist-P6.md` |
| Architecture Policy | `docs/architecture/command-skill-policy.md` |
| Architecture Policy (copy) | `src/superclaude/ARCHITECTURE.md` |
| Phase 1 Checkpoint | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P01-END.md` |
| Phase 2 Checkpoint | `.dev/releases/current/v2.01-Roadmap-v3/tasklist/checkpoints/CP-P02-END.md` |
| Framework Synthesis | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/framework-synthesis-A.md` |
| Dev Planning Synthesis | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/dev-planning-synthesis-A.md` |
| Dev Artifacts Synthesis | `.dev/releases/current/v2.01-Roadmap-v3/rollback-analysis/synthesis/dev-artifacts-synthesis-A.md` |

### Decision Artifacts (only D-0004 and D-0005 pertain to command changes)

| Artifact | Task | Path | Relevance to Commands |
|----------|------|------|-----------------------|
| D-0001 | T01.01 | `TASKLIST_ROOT/tasklist/artifacts/D-0001/evidence.md` | Indirect: TOOL_NOT_AVAILABLE result drives fallback-only variant |
| D-0002 | T01.01 | `TASKLIST_ROOT/tasklist/artifacts/D-0002/notes.md` | Indirect: Fallback-only variant determines command activation patterns |
| D-0003 | T01.02 | `TASKLIST_ROOT/tasklist/artifacts/D-0003/evidence.md` | Indirect: Prerequisites gate for Phase 2 changes |
| **D-0004** | **T02.01** | `TASKLIST_ROOT/tasklist/artifacts/D-0004/evidence.md` | **DIRECT: `Skill` added to roadmap.md allowed-tools** |
| **D-0005** | **T02.02** | `TASKLIST_ROOT/tasklist/artifacts/D-0005/evidence.md` | **DIRECT: `Skill` added to SKILL.md allowed-tools** |
| D-0006 | T02.03 | `TASKLIST_ROOT/tasklist/artifacts/D-0006/spec.md` | Indirect: Wave 2 step 3 sub-steps affect roadmap skill, not command |
| D-0007 | T02.03 | `TASKLIST_ROOT/tasklist/artifacts/D-0007/spec.md` | Indirect: Fallback protocol spec affects roadmap skill |
| D-0008 | T02.03 | `TASKLIST_ROOT/tasklist/artifacts/D-0008/spec.md` | Indirect: Return contract routing affects roadmap skill |

### Evidence Records (only T02.01 and T02.02 pertain to command changes)

| Evidence | Path | Relevance |
|----------|------|-----------|
| **T02.01** | `TASKLIST_ROOT/tasklist/evidence/T02.01/result.md` | **DIRECT: Validates `Skill` in roadmap.md** |
| **T02.02** | `TASKLIST_ROOT/tasklist/evidence/T02.02/result.md` | **DIRECT: Validates `Skill` in SKILL.md** |

### Modified Command Files

| Command | src/ Path | .claude/ Path | Parity |
|---------|-----------|---------------|--------|
| adversarial | `src/superclaude/commands/adversarial.md` | `.claude/commands/sc/adversarial.md` | IDENTICAL |
| cleanup-audit | `src/superclaude/commands/cleanup-audit.md` | `.claude/commands/sc/cleanup-audit.md` | IDENTICAL |
| roadmap | `src/superclaude/commands/roadmap.md` | `.claude/commands/sc/roadmap.md` | IDENTICAL |
| task-unified | `src/superclaude/commands/task-unified.md` | `.claude/commands/sc/task-unified.md` | IDENTICAL |
| validate-tests | `src/superclaude/commands/validate-tests.md` | `.claude/commands/sc/validate-tests.md` | IDENTICAL |
