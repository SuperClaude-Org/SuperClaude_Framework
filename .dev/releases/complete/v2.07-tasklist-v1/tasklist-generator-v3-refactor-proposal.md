# Tasklist Generator v3 Refactor Proposal
## Sprint CLI + /sc:task-unified Alignment

**Date**: 2026-03-04
**Status**: Proposal
**Source Analysis**: Sprint CLI source code, sc:task-unified skill/command, existing v2.02 & v2.05 tasklist outputs, prior refactor notes

---

## Executive Summary

The current Tasklist Generator Prompt (v2.1-unified / v2.2) produces a **single monolithic markdown document**. The Sprint CLI (`superclaude sprint run`) requires a **tasklist-index.md + per-phase `phase-N-tasklist.md` files**. This is the fundamental mismatch. The prior refactor notes (`tasklist-generator-refactor-notes-for-sprint-and-task-unified.md`) correctly identified 10 required changes. This document deepens that analysis with code-level evidence, concrete template specifications, and a prioritized refactoring plan.

---

## Part 1: Sprint CLI Contract (Code-Evidenced)

### 1.1 Phase File Discovery — The Hard Constraint

The Sprint CLI discovers phase files via regex in `config.py:17-25`:

```python
PHASE_FILE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:phase-(\d+)-tasklist\.md"
    r"|p(\d+)-tasklist\.md"
    r"|phase_(\d+)_tasklist\.md"
    r"|tasklist-p(\d+)\.md)(?![A-Za-z0-9])",
    re.IGNORECASE,
)
```

**Four accepted naming conventions** (case-insensitive):
| Convention | Example |
|---|---|
| `phase-N-tasklist.md` | `phase-1-tasklist.md` (preferred) |
| `pN-tasklist.md` | `p3-tasklist.md` |
| `phase_N_tasklist.md` | `phase_2_tasklist.md` |
| `tasklist-pN.md` | `tasklist-p4.md` |

**Rejected near-misses** (confirmed by tests): `phase1-tasklist.md`, `phase-1_tasklist.md`, `tasklist_phase_1.md`, `phase-1-tasklist-extra.md`.

**Discovery strategy** (`config.py:discover_phases`):
1. Regex-scan the index file text for phase filename references
2. Only files that actually exist on disk are added
3. Fallback: scan index directory for matching files
4. Deduplicate by phase number, sort ascending

**Generator requirement**: Emit files named `phase-N-tasklist.md` (canonical convention). The index must contain literal filename references, not TASKLIST_ROOT-relative placeholders that won't match the regex.

### 1.2 Phase Name Extraction — TUI Display

From `config.py:_extract_phase_name`:
```python
# Reads first # heading, strips "Phase N [-:—]" prefix, truncates to 50 chars
```

**Generator requirement**: Each phase file must begin with `# Phase N — <Name>` (or `: ` separator). Name portion ≤ 50 characters.

### 1.3 Prompt Construction — What Claude Receives Per Phase

From `process.py:build_prompt`:
```
/sc:task-unified Execute all tasks in @{phase_file} --compliance strict --strategy systematic

## Execution Rules
- Execute tasks in order (T{pn:02d}XX.01, T{pn:02d}XX.02, etc.)
- For STRICT tier tasks: use Sequential MCP for analysis, run quality verification
- For STANDARD tier tasks: run direct test execution per acceptance criteria
- For LIGHT tier tasks: quick sanity check only
- For EXEMPT tier tasks: skip formal verification
- If a STRICT-tier task fails, STOP and report -- do not continue to next task
- For all other tier failures, log the failure and continue

## Completion Protocol
When ALL tasks in this phase are complete (or halted on STRICT failure):
1. Write a phase completion report to {result_file} containing:
   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), tasks_total, tasks_passed, tasks_failed
   - Per-task status table: Task ID, Title, Tier, Status (pass/fail/skip), Evidence
   - Files modified (list all paths)
   - Blockers for next phase (if any)
   - The literal string EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT
```

**Critical implications for generator**:
- Phase files are passed whole as `@file` context — they should be **lean and execution-focused**
- Heavy metadata (Deliverable Registry, Traceability Matrix, templates) bloats the prompt unnecessarily
- The completion protocol is injected by the executor, NOT the phase file — phase files should NOT include completion instructions (they'd be redundant)
- Each phase file is an independent execution unit — it must be self-contained for its tasks

### 1.4 Result Parsing — Status Determination

From `executor.py:_determine_phase_status` (7-level priority):

| Priority | Condition | Status |
|---|---|---|
| 1 | `exit_code == 124` | TIMEOUT |
| 2 | `exit_code != 0` | ERROR |
| 3 | Contains `EXIT_RECOMMENDATION: HALT` | HALT |
| 4 | Contains `EXIT_RECOMMENDATION: CONTINUE` | PASS |
| 5 | `status: PASS` (regex) | PASS |
| 6 | `status: FAIL` | HALT |
| 7 | `status: PARTIAL` | HALT |

When both CONTINUE and HALT appear, HALT wins.

### 1.5 Monitor Expectations

From `monitor.py`:
- Task ID pattern: `T\d{2}\.\d{2}` — requires exactly `TNN.NN` format
- Tool pattern: `Read|Edit|MultiEdit|Write|Grep|Glob|Bash|TodoWrite|TodoRead|Task`
- Files changed: regex for `modified|created|edited|wrote|updated` + filename

**Generator requirement**: Task IDs must be `T<PP>.<TT>` with zero-padded 2-digit phase and task numbers.

---

## Part 2: /sc:task-unified Contract

### 2.1 Classification (Command Layer)

The command (`task-unified.md`) performs text-based tier classification before execution. When a phase file is passed, the **entire session** is classified at the highest-priority tier present. Output:

```html
<!-- SC:TASK-UNIFIED:CLASSIFICATION -->
TIER: [STRICT|STANDARD|LIGHT|EXEMPT]
CONFIDENCE: [0.00-1.00]
KEYWORDS: [matched keywords or "none"]
OVERRIDE: [true|false]
RATIONALE: [one-line reason]
<!-- /SC:TASK-UNIFIED:CLASSIFICATION -->
```

### 2.2 Per-Task Execution (Skill Layer)

The skill (`sc-task-unified-protocol/SKILL.md`) reads task-level `Tier` fields and applies:

| Task Tier | MCP Required | Verification | Halt on Fail? |
|---|---|---|---|
| STRICT | Sequential + Serena | Sub-agent (quality-engineer) | Yes |
| STANDARD | Sequential + Context7 (preferred) | Direct test execution | No |
| LIGHT | None | Sanity check | No |
| EXEMPT | None | Skip | No |

### 2.3 Fields Consumed Per Task

The skill reads these fields from the task block (LLM-interpreted, not parsed):

**Required fields** (drive execution behavior):
- `Tier` — determines execution path, MCP servers, verification
- Task ID (`T<PP>.<TT>`) — ordering, monitoring, reporting
- `Steps` — execution instructions
- `Acceptance Criteria` — verification targets
- `Dependencies` — ordering constraints

**Important fields** (influence execution):
- `Confidence` + `Requires Confirmation` — may pause for user input
- `Verification Method` — specifies verification approach
- `MCP Requirements` + `Fallback Allowed` — tool availability constraints
- `Sub-Agent Delegation` — whether to spawn sub-agents
- `Critical Path Override` — forces STRICT regardless of tier
- `Deliverables` — what must be produced
- `Rollback` — recovery procedure

**Metadata fields** (traceability, not execution):
- `Roadmap Item IDs` — back-reference
- `Effort`, `Risk`, `Risk Drivers` — planning metadata
- `Deliverable IDs`, `Artifacts` — artifact tracking

---

## Part 3: Gap Analysis — Generator v2.1/v2.2 vs. Requirements

### GAP-01: Single Document vs. Multi-File (CRITICAL)

**Current**: Section 6/Section 12 mandate "output one markdown document"
**Required**: `tasklist-index.md` + `phase-N-tasklist.md` per phase
**Impact**: Sprint CLI cannot discover phases from a monolithic file

### GAP-02: Index File Not Sprint-Discoverable (CRITICAL)

**Current**: "Tasklist Index" is a section within the monolith
**Required**: Standalone `tasklist-index.md` with literal `phase-N-tasklist.md` references that match the regex pattern
**Impact**: `discover_phases()` returns empty list

### GAP-03: Phase Files Bloated with Cross-Phase Metadata (HIGH)

**Current**: All metadata (Deliverable Registry, Traceability Matrix, templates, glossary) in one document
**Required**: Phase files should contain ONLY their phase tasks + phase-level context
**Impact**: Each phase Claude session receives unnecessary tokens (entire Deliverable Registry, all other phases' tasks, etc.)

### GAP-04: Completion Protocol Redundancy (MEDIUM)

**Current**: Generator embeds Execution Log Template, Checkpoint Report Template
**Required**: The Sprint executor injects its own Completion Protocol; generator templates are redundant
**Impact**: Conflicting instructions, wasted tokens

### GAP-05: Phase Heading Format Not Standardized (MEDIUM)

**Current**: Generator uses `## Phase <P>: <Phase Name>` (level 2 heading)
**Required**: Phase files need `# Phase N — <Name>` (level 1 heading, em-dash separator)
**Impact**: `_extract_phase_name` may not extract clean names

### GAP-06: Missing Phase Checkpoint Gates (MEDIUM)

**Current**: Checkpoints embedded inline after every 5 tasks
**Required**: Each phase file should have an end-of-phase checkpoint that serves as the gate for the next phase
**Impact**: Sprint relies on result file status, but clear in-file gates help Claude produce correct EXIT_RECOMMENDATION

### GAP-07: Wrapper Prompt References Wrong Path (LOW)

**Current**: `TasklistGenPrompt.md` references `.dev/.releases/backlog/` (extra dot in `.releases`)
**Required**: Correct path to the generator prompt
**Impact**: Manual correction needed each run

---

## Part 4: Refactoring Specification

### R-01: Multi-File Output Contract

**Replace** Section 1 objective "Single-document" and Section 12 "Final Output Constraint" with:

> **Output Contract**: Generate a multi-file bundle to `TASKLIST_ROOT/`:
> 1. `tasklist-index.md` — Sprint index with metadata, registries, traceability, templates
> 2. `phase-1-tasklist.md` through `phase-N-tasklist.md` — One file per phase, execution-focused
>
> The index is the authoritative metadata document. Phase files are execution units.

### R-02: Index File Template (New)

The `tasklist-index.md` must contain:

```markdown
# TASKLIST INDEX — <Sprint Name>

## Metadata & Artifact Paths
| Field | Value |
|---|---|
| Sprint Name | ... |
| Generator Version | ... |
| Generated | <ISO date> |
| TASKLIST_ROOT | ... |
| Total Phases | N |
| Total Tasks | N |
| Total Deliverables | N |
| Complexity Class | LOW|MEDIUM|HIGH |
| Primary Persona | ... |
| Consulting Personas | ... |

## Phase Files
| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation | T01.01–T01.04 | STRICT: 1, STANDARD: 2, EXEMPT: 1 |
| 2 | phase-2-tasklist.md | Backend Core | T02.01–T02.05 | STRICT: 2, STANDARD: 3 |
| ... | ... | ... | ... | ... |

## Source Snapshot
(3-6 bullets)

## Deterministic Rules Applied
(8-12 bullets as current)

## Roadmap Item Registry
(table as current)

## Deliverable Registry
(table as current)

## Traceability Matrix
(table as current)

## Execution Log Template
(as current)

## Checkpoint Report Template
(as current)

## Feedback Collection Template
(as current)

## Glossary
(if applicable)
```

**Key**: The "Phase Files" table must contain **literal filenames** (`phase-1-tasklist.md`, not `TASKLIST_ROOT/phase-1-tasklist.md`) so the Sprint regex can discover them.

### R-03: Phase File Template (New)

Each `phase-N-tasklist.md` must follow:

```markdown
# Phase N — <Phase Name>

<Phase goal: 2-3 sentences>

---

### T<NN>.<TT> — <Task Title>

| Field | Value |
|---|---|
| Roadmap Item IDs | R-NNN, R-NNN |
| Why | <1-2 sentences> |
| Effort | XS|S|M|L|XL |
| Risk | Low|Medium|High |
| Risk Drivers | <matched keywords> |
| Tier | STRICT|STANDARD|LIGHT|EXEMPT |
| Confidence | [████████░░] NN% |
| Requires Confirmation | Yes|No |
| Critical Path Override | Yes|No |
| Verification Method | <per tier> |
| MCP Requirements | <per tier> |
| Fallback Allowed | Yes|No |
| Sub-Agent Delegation | Required|Recommended|None |
| Deliverable IDs | D-NNNN |

**Artifacts**:
- `TASKLIST_ROOT/artifacts/D-NNNN/spec.md`

**Deliverables**:
- <concrete outputs>

**Steps**:
1. [PLANNING] ...
2. [EXECUTION] ...
3. [VERIFICATION] ...
4. [COMPLETION] ...

**Acceptance Criteria**:
1. ...
2. ...
3. ...
4. ...

**Validation**:
1. ...
2. ...

**Dependencies**: <Task IDs or "None">
**Rollback**: <procedure>
**Notes**: <optional>

---

(... more tasks ...)

---

### Checkpoint: End of Phase N

**Purpose**: <1 sentence>
**Verification**: (3 bullets)
**Exit Criteria**: (3 bullets)
**Checkpoint Report Path**: `TASKLIST_ROOT/checkpoints/CP-P<NN>-END.md`
```

**Key design decisions**:
- Level 1 heading (`# Phase N — Name`) for TUI extraction
- Em-dash separator (matches `_extract_phase_name` regex)
- Task metadata as a table (matches v2.02 working convention)
- NO Deliverable Registry, Traceability Matrix, or templates — those live in the index
- End-of-phase checkpoint included (serves as gate signal)
- NO completion protocol instructions (executor injects those)

### R-04: Generator Sections to Modify

| Current Section | Change |
|---|---|
| §1 Objective | Remove "Single-document"; add "Multi-file bundle" |
| §3 Artifact Paths | Add `tasklist-index.md` and `phase-N-tasklist.md` to standard paths |
| §4.8 Checkpoints | Keep inline checkpoints; add mandatory end-of-phase checkpoint |
| §6 Output Template | Replace monolithic template with Index Template + Phase File Template |
| §6.1-6.4 | Move to Index File Template |
| §6.5-6.6 | Move to Index File Template (registries) |
| §6.7 | Becomes the "Phase Files" table in Index; replace with file reference list |
| §6.8 | Becomes the Phase File Template |
| §6.9 | Keep inline checkpoints in phase files |
| §7-8 | Move templates to Index File |
| §9 | Move Traceability Matrix to Index File |
| §10 | Move Feedback Template to Index File |
| §12 | Replace "one document" with "multi-file bundle" constraint |

### R-05: New Section — "File Emission Rules"

Add after §3 (Artifact Paths):

> ### 3.3 File Emission Rules (Deterministic)
>
> The generator produces exactly N+1 files where N = number of phases:
>
> 1. **`tasklist-index.md`** — Contains: metadata, artifact paths, source snapshot, rules, registries, traceability matrix, templates, glossary
> 2. **`phase-1-tasklist.md`** through **`phase-N-tasklist.md`** — Contains: phase heading, phase goal, tasks (in order), inline checkpoints, end-of-phase checkpoint
>
> **Naming**: Phase files MUST use the `phase-N-tasklist.md` convention (primary Sprint CLI convention).
>
> **Phase heading**: MUST be `# Phase N — <Name>` (level 1, em-dash separator, name ≤ 50 chars).
>
> **Index references**: The "Phase Files" table in the index MUST contain literal filenames (e.g., `phase-1-tasklist.md`), not path-prefixed references.
>
> **Content boundary**: Phase files contain ONLY tasks belonging to that phase. No cross-phase metadata, no registries, no global templates.

### R-06: New Section — "Sprint Compatibility Self-Check"

Add before §12 (Final Output Constraint):

> ### 11.5 Sprint Compatibility Self-Check (Mandatory)
>
> Before finalizing output, verify:
> 1. `tasklist-index.md` exists and contains a "Phase Files" table
> 2. Every phase file referenced in the index exists in the output bundle
> 3. Phase numbers are contiguous (1, 2, 3, ..., N) with no gaps
> 4. All task IDs match `T<PP>.<TT>` format (2-digit zero-padded)
> 5. Every phase file starts with `# Phase N — <Name>` (level 1 heading)
> 6. Every phase file has an end-of-phase checkpoint
> 7. No phase file contains Deliverable Registry, Traceability Matrix, or template sections
> 8. Index contains literal phase filenames in at least one table cell

---

## Part 5: Wrapper Prompt (TasklistGenPrompt.md) Updates

The wrapper prompt also needs updates:

1. **Fix path reference**: `.dev/.releases/` → `.dev/releases/`
2. **Update output instruction**: "Write the generated tasklists to:" should specify the directory, not a single file
3. **Add multi-file awareness**: Instruct that output is a file bundle, not one document
4. **Specify file list**: "Output must include `tasklist-index.md` and one `phase-N-tasklist.md` per phase"

---

## Part 6: Compatibility Matrix

| Feature | v2.1/v2.2 (current) | v3.0 (proposed) | Sprint CLI | sc:task-unified |
|---|---|---|---|---|
| Output format | Single `.md` | Index + phase files | ✅ Required | ✅ Compatible |
| Phase file naming | N/A | `phase-N-tasklist.md` | ✅ Required | N/A |
| Index with literal filenames | N/A | ✅ | ✅ Required | N/A |
| Phase heading `# Phase N —` | `## Phase N:` | `# Phase N —` | ✅ Required | ✅ Compatible |
| Task ID `T<PP>.<TT>` | ✅ | ✅ | ✅ Required | ✅ Required |
| Per-task Tier field | ✅ | ✅ | ✅ Via prompt | ✅ Required |
| Per-task metadata table | Prose format | Table format | ✅ Compatible | ✅ Preferred |
| Lean phase files | ❌ (monolith) | ✅ | ✅ Token savings | ✅ Token savings |
| End-of-phase checkpoint | ❌ (cadence only) | ✅ | ✅ Gate signal | ✅ Gate signal |
| Completion protocol in file | ❌ (templates) | ❌ (executor injects) | ✅ Correct | ✅ Correct |
| Registries in index only | ❌ (in monolith) | ✅ | ✅ Separated | ✅ Less noise |

---

## Part 7: Migration Path

### Phase 1: Core structural refactor
1. Split §6 Output Template into Index Template + Phase File Template
2. Replace §1/§12 single-document constraints
3. Add §3.3 File Emission Rules
4. Add §11.5 Sprint Compatibility Self-Check

### Phase 2: Content redistribution
5. Move registries/matrices/templates to Index Template
6. Slim Phase File Template to tasks + checkpoints only
7. Update checkpoint cadence to include mandatory end-of-phase

### Phase 3: Polish
8. Update wrapper prompt (TasklistGenPrompt.md)
9. Add worked examples showing index + phase file output
10. Update Appendix with Sprint-specific quick reference

### Effort estimate
- Core refactor: ~40% of prompt text changes (sections 1, 3, 6, 12)
- Content redistribution: ~30% (sections 5-10 restructured, not rewritten)
- Polish: ~15% (wrapper, examples)
- Testing: Run against 2-3 existing roadmaps and validate Sprint CLI can discover phases

---

## Part 8: Open Questions

1. **Should the generator be invoked once (producing all files) or iteratively (once per phase)?**
   Recommendation: Once, producing entire bundle. The Sprint CLI expects all files to exist before `sprint run`.

2. **Should inline checkpoints (every 5 tasks) remain?**
   Recommendation: Keep them — they're useful for sc:task-unified even if Sprint doesn't parse them.

3. **Should the index include the full task list (all tasks from all phases) as a summary table?**
   Recommendation: No — the Phase Files table with task ID ranges is sufficient. Full task content stays in phase files.

4. **Should phase files include cross-phase dependency declarations?**
   Recommendation: Yes — in task `Dependencies` field. The executor handles phase-level sequencing, but Claude needs to know if a task depends on a prior phase's output.
