# Tasklist: Refactor Spec to Release Spec Template + Pre-Roadmap Fixes
# Target: .dev/releases/current/2.24.2-Accept-Spec-Change/brainstorm-accept-spec-change.md
# Template: src/superclaude/examples/release-spec-template.md
# Date: 2026-03-13

## Context for executing agent

You are restructuring an existing brainstorm-format specification into the canonical
release spec template. The content is already complete and panel-hardened (21 expert
findings resolved). Your job is to reorganize, reformat, and fill structural gaps —
NOT to rewrite or alter any functional requirements.

### Files you need

| File | Role | Read first? |
|---|---|---|
| `src/superclaude/examples/release-spec-template.md` | Template to conform to | YES |
| `.dev/releases/current/2.24.2-Accept-Spec-Change/brainstorm-accept-spec-change.md` | Source spec (your edit target) | YES |
| `.dev/releases/current/2.24.2-Accept-Spec-Change/design-accept-spec-change.md` | Design doc (content to pull from) | YES for tasks that reference it |
| `.dev/releases/current/2.24.2-Accept-Spec-Change/spec-panel-tasklist.md` | Panel findings (reference only) | NO unless TASK-R17 |
| `pyproject.toml` | Project dependencies (for TASK-R01) | YES for TASK-R01 only |

### Rules

1. **Do NOT change any functional requirement text** in FR-1 through FR-13, NFR-1 through
   NFR-5, or AC-1 through AC-11. These are panel-hardened. Move them into template
   structure but preserve their exact wording.
2. **The output file remains** `brainstorm-accept-spec-change.md` — rename it to
   `release-spec-accept-spec-change.md` after all tasks complete (TASK-R19).
3. **Spec type is `new_feature`**. Applicable conditional sections: 4.5 (Data Models),
   5.1 (CLI Surface), 9 (Migration & Rollout). Remove/skip: 4.3 (Removed Files),
   5.2 (Gate Criteria), 5.3 (Phase Contracts), 8.3 (Manual/E2E Tests).

---

## Phase 0: Pre-Roadmap Blockers (fix before any restructuring)

### TASK-R01: Add PyYAML dependency to pyproject.toml
**Priority**: BLOCKER
**File**: `pyproject.toml`
**Instruction**:
Find the `dependencies` list (line 34-38). Add `"pyyaml>=6.0"` after `"rich>=13.0.0"`.

Before:
```toml
dependencies = [
    "pytest>=7.0.0",
    "click>=8.0.0",
    "rich>=13.0.0",
]
```

After:
```toml
dependencies = [
    "pytest>=7.0.0",
    "click>=8.0.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
]
```

**Verification**: `grep pyyaml pyproject.toml` returns the new line.

---

### TASK-R02: Add YAML boolean coercion note to design doc
**Priority**: BLOCKER
**File**: `design-accept-spec-change.md`
**Instruction**:
In section 2.3, after the `_coerce_spec_update_required` code block and before
section 2.4, add:

```markdown
**YAML boolean note**: PyYAML `safe_load` treats `yes`, `on`, `1` as boolean `True`
per YAML 1.1 spec. This is intentional — all YAML boolean forms are accepted for
`spec_update_required`. The `_coerce_spec_update_required` guard (`value is True`)
accepts any Python `True` regardless of which YAML literal produced it.
```

**Verification**: Read the design doc and confirm the note appears between §2.3 and §2.4.

---

## Phase 1: YAML Frontmatter (template lines 19-39)

### TASK-R03: Add YAML frontmatter block
**Priority**: HIGH
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Replace the current header (lines 1-8):
```
# Requirements Spec: accept-spec-change Command + Auto-Resume on Spec Patch
# Brainstorm output — v2.24-cli-portify-cli-v4

**Date**: 2026-03-13
**Status**: Requirements complete — ready for /sc:design
**Scope**: Two deliverables:
  1. `superclaude roadmap accept-spec-change` CLI command
  2. Auto-resume cycle inside `execute_roadmap()` when a Claude subprocess patches the spec
```

With:
```yaml
---
title: "accept-spec-change Command + Auto-Resume on Spec Patch"
version: "1.0.0"
status: complete
feature_id: FR-2.24.2
parent_feature: v2.24-cli-portify-cli-v4
spec_type: new_feature
complexity_score: 0.65
complexity_class: moderate
target_release: "2.24.2"
authors: [user, claude]
created: 2026-03-13
quality_scores:
  clarity: 8.0
  completeness: 8.5
  testability: 9.0
  consistency: 8.0
  overall: 8.5
---
```

The quality scores come from the spec-panel review iteration 2 synthesis:
clarity=7.0→8.0 (after 21 fixes), completeness=6.5→8.5, testability=6.0→9.0,
correctness=5.5→8.5 (averaged into overall), consistency=8.0.

**Verification**: `grep -c '{{SC_PLACEHOLDER:' brainstorm-accept-spec-change.md` returns 0.

---

## Phase 2: Section 1 — Problem Statement (template lines 41-61)

### TASK-R04: Restructure Problem Statement with Evidence and Scope subsections
**Priority**: HIGH
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
The current spec has `## Problem Statement` (lines 12-21) and a separate
`## Scope Boundary` (lines 25-29). Restructure into template format:

Replace the `## Problem Statement` section and `## Scope Boundary` section with:

```markdown
## 1. Problem Statement

When the spec file is edited to formalize an accepted deviation (a documentation sync, not a
functional change), the stored `spec_hash` in `.roadmap-state.json` goes stale. `--resume`
treats the hash mismatch as a functional spec change, sets `force_extract = True`, and
cascades a full 28-minute pipeline re-run. This discards all valid upstream outputs
(roadmap files, debate transcript, diff, etc.) unnecessarily.

The root cause: `_apply_resume()` has no way to distinguish a "spec updated to match
accepted roadmap architecture" edit from a "spec requirements genuinely changed" edit.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| `_apply_resume()` sets `force_extract = True` on any spec hash mismatch | `executor.py:1068-1079` | Full 28-min re-run on documentation-only changes |
| No mechanism to acknowledge non-functional spec edits | `executor.py:822` (missing `auto_accept` param) | User must re-run entire pipeline or manually edit state JSON |
| Sprint runner cannot proceed non-interactively after deviation acceptance | Pipeline design gap | Automated pipeline halts on accepted deviations |

### 1.2 Scope Boundary

**In scope**: Deviations where `spec_update_required: true` in the accepted deviation
record. Two deliverables: (1) `superclaude roadmap accept-spec-change` CLI command,
(2) auto-resume cycle inside `execute_roadmap()` when a Claude subprocess patches the spec.

**Out of scope**: Deviations where `spec_update_required: false` — they require a different
mechanism (gate override records, not spec hash acknowledgement).
```

**Verification**: The spec now has `## 1. Problem Statement`, `### 1.1 Evidence` with
a 3-row table, and `### 1.2 Scope Boundary` with **In scope** / **Out of scope**.

---

## Phase 3: Section 2 — Solution Overview (template lines 63-83)

### TASK-R05: Add Solution Overview section
**Priority**: HIGH
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Insert a new `## 2. Solution Overview` section AFTER `### 1.2 Scope Boundary` and
BEFORE the first deliverable section. This section does not currently exist in the spec.

Content to insert:

```markdown
## 2. Solution Overview

Two components that together eliminate unnecessary pipeline re-runs after spec documentation
syncs:

1. **CLI command `accept-spec-change`**: A manual, evidence-gated command that updates
   `spec_hash` in `.roadmap-state.json` when the spec edit is a documentation sync (not a
   functional change). Requires at least one `dev-*-accepted-deviation.md` file with
   `disposition: ACCEPTED` and `spec_update_required: true` as evidence.

2. **Auto-resume cycle in `execute_roadmap()`**: When a Claude subprocess patches the spec
   during pipeline execution, `execute_roadmap()` detects the deviation evidence and
   automatically triggers a spec-hash sync + resume without requiring a separate manual step.

Neither component modifies the existing `_apply_resume()` function. The changes are additive:
a new module (`spec_patch.py`), a new CLI command, and two new private functions in
`executor.py`. The `execute_roadmap()` signature gains one keyword argument (`auto_accept`)
with a backward-compatible default.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Process architecture | Same-process control flow | Separate subprocess call to `accept-spec-change` | Avoids race conditions; disk-reread provides safety |
| State freshness | Disk-reread at resume boundary | Reuse in-memory state | Prevents stale state bugs; guarantees `_apply_resume()` sees updated `spec_hash` |
| Non-interactive control | `auto_accept` parameter on `execute_roadmap()` | CLI flag `--auto-accept` | Internal parameter keeps CLI surface clean; sprint runner passes `True` directly |
| Recursion guard | Local counter, max 1 cycle | Persistent state-based guard | Per-invocation scope prevents cross-run interference |
| CLI surface | No flags on `accept-spec-change` | `--force`, `--yes` flags | Evidence-based design: deviation records ARE the authorization |
| Module isolation | `spec_patch.py` imports only stdlib + PyYAML | Import `read_state`/`write_state` from `executor.py` | Prevents circular dependency risk |

### 2.2 Workflow / Data Flow

```
Manual path:
  roadmap run → spec-fidelity FAIL → human reviews → human edits spec
  → human writes dev-NNN-accepted-deviation.md
  → accept-spec-change <output_dir>  [prompts y/N, updates hash]
  → roadmap run --resume  [skips to spec-fidelity]

Automatic path:
  roadmap run → spec-fidelity FAIL → remediation subprocess runs
  → subprocess patches spec + writes deviation record
  → execute_roadmap() detects conditions (FR-9)
  → disk-reread + spec_hash update (FR-10)
  → _apply_resume() skips to spec-fidelity → re-run
  → PASS: pipeline continues | FAIL: normal failure (no second cycle)
```
```

**Verification**: The spec now has `## 2. Solution Overview`, `### 2.1 Key Design Decisions`
with a 6-row table, and `### 2.2 Workflow / Data Flow`.

---

## Phase 4: Section 3 — Functional Requirements (template lines 85-101)

### TASK-R06: Reformat FRs with inline Acceptance Criteria and Dependencies
**Priority**: HIGH
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Rename the current headings and restructure each FR to include inline acceptance criteria
and dependencies. The template requires this format per FR:

```markdown
### FR-2.24.2.N: Title
**Description**: ...
**Acceptance Criteria**:
- [ ] criterion
**Dependencies**: ...
```

Restructure the existing `### Functional requirements` section under `## Deliverable 1`
and `## Deliverable 2` into a single `## 3. Functional Requirements` section. Number
each FR with the feature ID prefix: `FR-2.24.2.1` through `FR-2.24.2.13`.

For each FR, distribute the acceptance criteria from the current AC table (lines 392-405):
- FR-1 through FR-7 get ACs from Deliverable 1 (AC-1 through AC-5b, AC-11)
- FR-8 through FR-13 get ACs from Deliverable 2 (AC-6 through AC-10)

**Example** for FR-1:
```markdown
### FR-2.24.2.1: Locate state file

**Description**: Read `.roadmap-state.json` from `output_dir`. If absent or unreadable,
exit with a clear error: "No .roadmap-state.json found in <output_dir>. Run `roadmap run` first."

**Acceptance Criteria**:
- [ ] Command exits 1 with clear message when state file is missing

**Dependencies**: None
```

**Example** for FR-4 (which has multiple ACs):
```markdown
### FR-2.24.2.4: Scan for accepted deviation evidence

**Description**: [existing FR-4 text, including frontmatter schema and parse-error handling]

**Acceptance Criteria**:
- [ ] AC-1: `accept-spec-change` exits 1 with clear message when no accepted deviation records are found

**Dependencies**: FR-2.24.2.1 (state file must be located), FR-2.24.2.2 (spec hash must be computed)
```

Preserve ALL existing FR text exactly. Only add the template structure around it.

Move the current `## Acceptance Criteria` table (lines 390-405) content inline to each FR.
Delete the standalone `## Acceptance Criteria` section after all ACs are distributed.

**Critical**: Do NOT alter any FR prose. Move text, don't rewrite it.

**Verification**: `grep -c '### FR-2.24.2' brainstorm-accept-spec-change.md` returns 13.
The standalone `## Acceptance Criteria` section no longer exists.

---

## Phase 5: Section 4 — Architecture (template lines 103-152)

### TASK-R07: Restructure Files table into New Files / Modified Files subsections
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Replace the current `## Files to create/modify` section (near end of file) with:

```markdown
## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/cli/roadmap/spec_patch.py` | Deviation record scanning, spec_hash atomic update, interactive prompt | stdlib + PyYAML only (leaf module) |
| `tests/roadmap/test_accept_spec_change.py` | Unit tests for AC-1 through AC-5b, AC-11 | spec_patch.py, pytest |
| `tests/roadmap/test_spec_patch_cycle.py` | Integration-level unit tests for AC-6 through AC-10 | executor.py, spec_patch.py, pytest |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/roadmap/commands.py` | Add `accept-spec-change` subcommand under `roadmap_group` | Deliverable 1 CLI entry point |
| `src/superclaude/cli/roadmap/executor.py` | Add `auto_accept` param to `execute_roadmap()`, add `_apply_resume_after_spec_patch()` helper, add recursion guard, capture `initial_spec_hash` at function entry | Deliverable 2 auto-resume cycle |
| `pyproject.toml` | Add `pyyaml>=6.0` to dependencies | Required for YAML frontmatter parsing in `spec_patch.py` |
```

### TASK-R08: Keep existing Module Dependency Graph as section 4.4
**Priority**: LOW
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Move the existing dependency graph text (currently at end of Files section) under
a new `### 4.4 Module Dependency Graph` heading. Preserve the graph and prose exactly.

---

### TASK-R09: Add Data Models section (4.5 — conditional for new_feature)
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
After `### 4.4 Module Dependency Graph`, add `### 4.5 Data Models`. Pull the
`DeviationRecord` dataclass from the design doc (design §2.2, lines 79-88):

```markdown
### 4.5 Data Models

```python
@dataclass(frozen=True)
class DeviationRecord:
    """Parsed and validated accepted deviation record."""
    id: str                           # e.g. "DEV-001"
    disposition: str                  # normalized to uppercase
    spec_update_required: bool        # YAML boolean only (True/False, yes/no, on/off)
    affects_spec_sections: list[str]  # may be empty list
    acceptance_rationale: str         # may be empty string
    source_file: Path                 # absolute path to the .md file
    mtime: float                      # os.path.getmtime() at scan time
```

Invariants:
- `disposition` is always stored uppercase after normalization
- `spec_update_required` is always a Python `bool` (never str). PyYAML `safe_load`
  treats `yes`, `on`, `1` as boolean `True` per YAML 1.1 spec — all forms are accepted.
- `mtime` is a Unix timestamp float, captured once at scan time
```

**Verification**: The spec now has `### 4.5 Data Models` with the DeviationRecord dataclass.

---

### TASK-R10: Add Implementation Order section (4.6)
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
After `### 4.5 Data Models`, add:

```markdown
### 4.6 Implementation Order

```
1. spec_patch.py (DeviationRecord + scan + parse)  -- leaf module, no upstream deps
2. spec_patch.py (update_spec_hash + prompt)        -- [parallel with step 1]
3. commands.py (accept-spec-change command)          -- depends on 1, 2
4. executor.py (signature + initial_spec_hash)       -- independent of 1-3
5. executor.py (_apply_resume_after_spec_patch)      -- depends on 1, 4
6. test_accept_spec_change.py                        -- depends on 1, 2, 3
7. test_spec_patch_cycle.py                          -- depends on 4, 5
```
```

---

## Phase 6: Section 5 — Interface Contracts (template lines 154-182)

### TASK-R11: Add CLI Surface section (5.1 — conditional for new_feature)
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Move the existing `### Command signature` section content into template format. Insert
after section 4:

```markdown
## 5. Interface Contracts

### 5.1 CLI Surface

```
superclaude roadmap accept-spec-change <output_dir>
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_dir` | `click.Path(exists=True)` | (required positional) | Directory containing `.roadmap-state.json` and `dev-*-accepted-deviation.md` files |

No flags. The command has zero optional arguments by design (clean CLI surface — evidence
records serve as authorization). `auto_accept` is an internal code parameter on
`execute_roadmap()`, not exposed on the CLI.

### 5.2 Internal API Surface (execute_roadmap signature change)

```python
execute_roadmap(
    config: RoadmapConfig,
    resume: bool = False,
    no_validate: bool = False,
    auto_accept: bool = False,   # NEW — AC-10: default=False preserves backward compat
) -> None
```
```

Remove the old `### Command signature` section and `### Registration` section since
their content is now in §5.1. The registration detail ("Add to commands.py as
`@roadmap_group.command()`") belongs in §4.2 Modified Files (already covered in TASK-R07).

---

## Phase 7: Section 6 — Non-Functional Requirements (template lines 184-188)

### TASK-R12: Reformat NFRs into template table
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Replace the current `### Non-functional requirements` bullet list with the template table
format:

```markdown
## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1 | Atomic write — no partial state corruption on power loss mid-write | Zero data loss on POSIX systems | `os.replace()` atomicity; test with crash simulation |
| NFR-2 | Read-only on abort — state file never touched if user answers N | No writes on abort path | Unit test: assert state file mtime unchanged after N |
| NFR-3 | Idempotent — running twice with same spec change is safe | Second run exits 0 cleanly | Unit test: run twice, assert state unchanged after first |
| NFR-4 | No pipeline execution — command only reads/writes state | Zero subprocess invocations | Code review: no `ClaudeProcess` usage in `spec_patch.py` |
| NFR-5 | Exclusive access — no concurrent write protection | Documented constraint | README/docstring warning; no file locking |
```

Include the existing detail notes (Windows caveat, etc.) as prose below the table.

---

## Phase 8: Section 7 — Risk Assessment (template lines 190-194)

### TASK-R13: Add Risk Assessment section
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
This section does not exist. Add after §6:

```markdown
## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TOCTOU window: state file modified between read and atomic write | Low | Medium — stale keys overwritten | NFR-5 documents exclusive access constraint; no concurrent `roadmap run` |
| Filesystem mtime resolution: files written in same second as `started_at` not detected | Low | Medium — auto-resume cycle fails to trigger | FR-9 Condition 2 documents strict `>` limitation; implementations may use `>=` |
| PyYAML boolean coercion: `yes`/`on`/`1` accepted as `true` | Low | Low — broader acceptance is intentional | Design note documents YAML 1.1 boolean forms as accepted |
| Deviation file with valid glob name but invalid YAML | Medium | Low — file skipped with warning | FR-4 parse-error handling: warn + skip, continue processing |
| `auto_accept=True` passed accidentally by a caller | Low | High — spec hash updated without human review | Parameter is internal (not CLI flag); only sprint runner uses it |
```

---

## Phase 9: Section 8 — Test Plan (template lines 196-214)

### TASK-R14: Add Test Plan with unit and integration test tables
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Pull from design doc §9 (lines 760-822). Add after §7:

```markdown
## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `TestLocateStateFile` | `test_accept_spec_change.py` | FR-1: missing/unreadable state file exits 1 |
| `TestRecomputeHash` | `test_accept_spec_change.py` | FR-2: missing spec file exits 1 |
| `TestHashMismatchCheck` | `test_accept_spec_change.py` | FR-3: hash equality exits 0; AC-3 idempotency |
| `TestScanDeviationRecords` | `test_accept_spec_change.py` | FR-4: glob, parse, filter, zero-records exit; AC-1 |
| `TestPromptBehavior` | `test_accept_spec_change.py` | FR-5: input normalization, non-interactive; AC-4, AC-11 |
| `TestAtomicWrite` | `test_accept_spec_change.py` | FR-6: only spec_hash changed, all keys preserved; AC-2 |
| `TestConfirmationOutput` | `test_accept_spec_change.py` | FR-7: both hashes truncated to 12 chars |
| `TestIdempotency` | `test_accept_spec_change.py` | AC-3: second run exits 0 |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| `TestCycleGuard` | FR-11, AC-6: cycle fires at most once per invocation |
| `TestDiskReread` | FR-10, AC-7: `_apply_resume()` uses post-write disk state, not pre-write |
| `TestConditionChecks` | FR-9: all three conditions required; mtime type conversion; `initial_spec_hash` used (not `state["spec_hash"]`) |
| `TestAutoAccept` | FR-8, AC-9: `auto_accept=True` skips prompt; False prompts |
| `TestBackwardCompat` | AC-10: `execute_roadmap()` callable without `auto_accept` |
| `TestCycleExhaustion` | FR-13, AC-8: second fidelity fail exits 1, no loop |
| `TestWriteFailure` | FR-10 Step 3: atomic write failure falls through to normal failure |
```

---

## Phase 10: Sections 9-12 + Appendices (template lines 216-264)

### TASK-R15: Add Migration & Rollout section (9 — conditional for new_feature touching existing APIs)
**Priority**: LOW
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Add after §8:

```markdown
## 9. Migration & Rollout

- **Breaking changes**: None. `execute_roadmap()` gains `auto_accept: bool = False` with
  backward-compatible default. All existing callers continue working without modification.
- **Backwards compatibility**: AC-10 explicitly requires that the signature change is
  backward-compatible. No existing CLI flags change.
- **Rollback plan**: Revert the commit. The only state-file change (`spec_hash` update) is
  safe to revert — the next `roadmap run` will recompute hashes from scratch.
```

---

### TASK-R16: Add Downstream Inputs section (10)
**Priority**: MEDIUM
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Add after §9:

```markdown
## 10. Downstream Inputs

### For sc:roadmap
This spec produces 3 implementation themes for roadmap phasing:
1. **Phase: New module** — `spec_patch.py` (leaf module, no upstream deps)
2. **Phase: CLI command** — `accept-spec-change` in `commands.py` (depends on spec_patch)
3. **Phase: Executor integration** — `execute_roadmap()` changes + `_apply_resume_after_spec_patch()` (depends on spec_patch)

Parallelization: Phases 1 and 3 are partially independent (both depend on spec_patch but don't depend on each other). Tests follow after their respective phases.

### For sc:tasklist
Task breakdown should follow §4.6 Implementation Order. Key granularity boundaries:
- `spec_patch.py` is one task (small module, 3 public functions)
- `executor.py` changes are two tasks: (a) signature + `initial_spec_hash` capture, (b) `_apply_resume_after_spec_patch()` + `_find_qualifying_deviation_files()`
- `commands.py` is one task (single Click command)
- Each test file is one task
```

---

### TASK-R17: Restructure Open Items as section 11
**Priority**: LOW
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Rename `## Open Questions (resolved)` to `## 11. Open Items`. Reformat the existing
table to match template columns (`Item | Question | Impact | Resolution Target`).
Since all items are resolved, add "Resolved" in the Resolution Target column for each row.

---

### TASK-R18: Add Brainstorm Gap Analysis section (12) and Appendices
**Priority**: LOW
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
Add after §11:

```markdown
## 12. Brainstorm Gap Analysis

This spec was reviewed by `/sc:spec-panel --mode critique --focus requirements,correctness`
with experts Wiegers, Adzic, Nygard, Fowler, and Whittaker across 2 iterations. All 21
findings (7 critical, 8 major, 6 minor) have been resolved.

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| WHITTAKER-IT2-1 | `_apply_resume()` must use post-write disk state | Critical | FR-10 | Whittaker |
| NYGARD-3 | `initial_spec_hash` capture point undefined | Critical | FR-9 | Nygard |
| ADZIC-2 / WHITTAKER-2 | mtime comparison operator and type mismatch | Critical | FR-9 | Adzic, Whittaker |
| WIEGERS-2 / ADZIC-1 | Deviation file frontmatter schema undefined | Critical | FR-4 | Wiegers, Adzic |
| WHITTAKER-4 | Atomic write failure path in FR-10 Step 3 | Critical | FR-10 | Whittaker |

Full findings: `spec-panel-tasklist.md` in this directory.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| deviation record | A `dev-*-accepted-deviation.md` file containing YAML frontmatter with disposition and spec_update_required fields |
| spec_hash | SHA-256 hex digest of the spec file, stored in `.roadmap-state.json` to detect changes between runs |
| force_extract | Boolean flag in `_apply_resume()` that triggers full pipeline re-run when spec hash changes |
| spec-fidelity | Pipeline step 8/9 that validates the final roadmap against the original spec |
| auto_accept | Boolean parameter on `execute_roadmap()` that controls whether the spec-patch cycle prompts the user |
| initial_spec_hash | Local variable in `execute_roadmap()` capturing the spec hash at function entry, used for FR-9 Condition 3 |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `design-accept-spec-change.md` | Full architecture design with function signatures, data flow diagrams, and test architecture |
| `spec-panel-tasklist.md` | All 21 expert panel findings with resolution status |
| `src/superclaude/cli/roadmap/executor.py` | Existing codebase — `execute_roadmap()`, `_apply_resume()`, `_save_state()`, `read_state()` |
```

---

## Phase 11: Cleanup

### TASK-R19: Remove redundant sections and rename file
**Priority**: HIGH (do last)
**File**: `brainstorm-accept-spec-change.md`
**Instruction**:
After all previous tasks are complete:
1. Remove the standalone `## Acceptance Criteria` section (content now inline in §3 FRs)
2. Remove the standalone `## Workflow Integration` section (content now in §2.2)
3. Remove the standalone `## Deliverable 1` / `## Deliverable 2` wrapper headings (FRs
   are now in unified §3, architecture in §4)
4. Remove `### Command signature` and `### Registration` (now in §5.1 and §4.2)
5. Remove `## Files to create/modify` (now in §4.1 and §4.2)
6. Remove `### Design decisions` table (now in §2.1)
7. Remove `### State Trace` (keep as-is — it belongs under FR-10 in §3 or as an appendix)
8. Remove `### What the Claude subprocess is responsible for` (keep as-is — it's a scope
   note that belongs after the relevant FR in §3)
9. Rename the file: `mv brainstorm-accept-spec-change.md release-spec-accept-spec-change.md`

**Verification**:
- `ls .dev/releases/current/2.24.2-Accept-Spec-Change/release-spec-accept-spec-change.md` exists
- The file has these section headers in order: frontmatter, §1-§12, Appendix A, Appendix B
- `grep -c '## Deliverable' release-spec-accept-spec-change.md` returns 0
- `grep -c '## Acceptance Criteria' release-spec-accept-spec-change.md` returns 0
- `grep -c '{{SC_PLACEHOLDER:' release-spec-accept-spec-change.md` returns 0

---

## Summary Table

| Task | Priority | Phase | Target file | Description |
|------|----------|-------|-------------|-------------|
| TASK-R01 | BLOCKER | 0 | pyproject.toml | Add `pyyaml>=6.0` dependency |
| TASK-R02 | BLOCKER | 0 | design doc | Add YAML boolean coercion note |
| TASK-R03 | HIGH | 1 | spec | Add YAML frontmatter block |
| TASK-R04 | HIGH | 2 | spec | Restructure Problem Statement + Evidence + Scope |
| TASK-R05 | HIGH | 3 | spec | Add Solution Overview + Design Decisions + Data Flow |
| TASK-R06 | HIGH | 4 | spec | Reformat all 13 FRs with inline ACs and dependencies |
| TASK-R07 | MEDIUM | 5 | spec | Split files table into New Files / Modified Files |
| TASK-R08 | LOW | 5 | spec | Move dependency graph to §4.4 |
| TASK-R09 | MEDIUM | 5 | spec | Add Data Models section with DeviationRecord |
| TASK-R10 | MEDIUM | 5 | spec | Add Implementation Order |
| TASK-R11 | MEDIUM | 6 | spec | Add CLI Surface + Internal API Surface |
| TASK-R12 | MEDIUM | 7 | spec | Reformat NFRs into template table |
| TASK-R13 | MEDIUM | 8 | spec | Add Risk Assessment table |
| TASK-R14 | MEDIUM | 9 | spec | Add Test Plan with unit + integration tables |
| TASK-R15 | LOW | 10 | spec | Add Migration & Rollout section |
| TASK-R16 | MEDIUM | 10 | spec | Add Downstream Inputs section |
| TASK-R17 | LOW | 10 | spec | Restructure Open Items as §11 |
| TASK-R18 | LOW | 10 | spec | Add Gap Analysis + Glossary + References |
| TASK-R19 | HIGH | 11 | spec | Remove redundant sections + rename file |

**Total**: 19 tasks (2 BLOCKER, 5 HIGH, 8 MEDIUM, 4 LOW)
**Execution order**: Phases 0-11 sequentially. Within each phase, tasks are independent.
