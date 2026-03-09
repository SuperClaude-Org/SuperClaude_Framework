---
title: "v2.14 — Sprint Report Scaffolding"
version: "2.14"
status: backlog
origin: "spec-panel review of scaffold brainstorm plan"
origin_plan: ".claude/plans/nifty-swimming-scott.md"
decision_source: ".dev/releases/current/v2.13-CLIRunner-PipelineUnification/merged-pipeline-decision.md"
generated_by: "/sc:spec-panel"
generated_date: "2026-03-06"
expert_panel: ["Wiegers", "Fowler", "Nygard", "Crispin", "Adzic"]
scope: "src/superclaude/cli/sprint/"
complexity_class: LOW
domain_distribution:
  backend: 85
  testing: 15
primary_persona: backend
consulting_personas: [qa, refactorer]
dependency: "v2.13 M1 (characterization tests must exist before scaffold changes land)"
---

# v2.14 Release Spec: Sprint Report Scaffolding

## 1. Executive Summary

When sprint phases hit the `max_turns` limit, the Claude agent never writes the `phase-N-result.md` file because report writing is the last action in the Completion Protocol. This caused 3 of 5 phases in a recent sprint to finish as `pass_no_report` — the sprint continued but no structured per-task report existed.

This release adds a two-layer defense:

1. **Layer 1 (Guaranteed)**: The sprint runner creates a scaffold result file BEFORE launching the agent subprocess. This is deterministic Python code — zero reliance on agent behavior.
2. **Layer 2 (Best-effort)**: The prompt instructs the agent to update the scaffold incrementally. If the agent completes normally, it overwrites the scaffold with a full report. If it hits `max_turns`, the scaffold (possibly partially updated) remains as a structured artifact.

**Key design property**: No changes to `_determine_phase_status()`, `PhaseStatus` enum, or the execution log format. The scaffold naturally maps to the existing `PASS_NO_SIGNAL` status (which is `is_success=True`).

**Non-Goals**:
- Changes to the sprint executor's poll loop, TUI, or monitoring subsystems
- New PhaseStatus enum values or changes to status classification logic
- Executor-level unification with pipeline (deferred per v2.13 decision record)
- Retry or parallel execution features

## 2. Background

### Problem Evidence

From the `cleanup-audit-v2-UNIFIED-SPEC` sprint execution (2026-03-05):

| Phase | Tasks | Duration | Status | Stop Reason |
|-------|-------|----------|--------|-------------|
| 1 | 10 | 9m 13s | `pass_no_report` | `error_max_turns` (turn 51) |
| 2 | 6 | 7m 59s | `pass_no_report` | `error_max_turns` (turn 51) |
| 3 | 10 | 13m 7s | `pass` | Normal completion |
| 4 | 13 | 15m 51s | `pass` | Normal completion |
| 5 | 9 | 18m 22s | `pass_no_report` | `error_max_turns` (turn 51) |

Phase 2's output shows `"Write phase 2 completion report"` was `in_progress` as a TodoWrite item when the session terminated — the agent was literally about to write the report.

### Root Cause

The current Completion Protocol instructs the agent to write the report as a single monolithic action after ALL tasks complete. Report writing is always the first casualty when turns run out.

### Relationship to v2.13

v2.13 implements Option 3 (Targeted Fixes) from the adversarial pipeline architecture decision. Its scope is explicitly: process hook migration, dead code removal, file-passing fix, and characterization tests. v2.13 declares "No new features for sprint or roadmap" as a non-goal.

This release (v2.14) is a new feature for sprint. It is sequenced AFTER v2.13 to:
- Avoid merge conflicts on `sprint/process.py` (v2.13 heavily reworks it)
- Ensure v2.13's characterization tests are in place as a safety net
- Respect v2.13's decision record scope boundary

## 3. Deliverables

### D1: Task Metadata Parser (Priority: P0)

**Problem**: To create a scaffold, we need to extract task IDs, titles, and tiers from phase tasklist files. No parser for this format currently exists.

**Solution**: Add `parse_phase_tasks()` as a public function in a new module `src/superclaude/cli/sprint/scaffold.py`. This isolates scaffold concerns from both `executor.py` (orchestration) and `config.py` (discovery/configuration).

**Rationale for module placement** (per Fowler review): `executor.py` manages subprocesses and poll loops — parsing markdown is a different concern. `config.py` parses `tasklist-index.md` for phase discovery, but task-level metadata parsing is scaffold-specific. A dedicated `scaffold.py` owns the full scaffold lifecycle: parsing, creation, and format definition.

**Interface**:

```python
# src/superclaude/cli/sprint/scaffold.py

@dataclass
class TaskMeta:
    """Metadata for a single task extracted from a phase tasklist file."""
    id: str        # e.g., "T01.01"
    title: str     # e.g., "Implement two-tier classification..."
    tier: str      # e.g., "STRICT", "STANDARD", "LIGHT", "EXEMPT", "UNKNOWN"

def parse_phase_tasks(phase_file: Path) -> list[TaskMeta]:
    """Parse task metadata from a phase tasklist file.

    Extracts task ID and title from headings matching:
        ### T01.01 -- Title text here

    Extracts tier from metadata table rows matching:
        | Tier | STRICT |

    Returns empty list on OSError or if no tasks are found.
    Tier defaults to "UNKNOWN" if not found in the task's metadata block.
    """
```

**Parsing strategy**:
1. Read file content with `errors="replace"`
2. Find all task headings: `^###\s+(T\d{2}\.\d{2})\s+--\s+(.+)$` (MULTILINE)
3. For each heading, extract the text block between it and the next heading (or EOF)
4. Within that block, search for tier: `^\|\s*Tier\s*\|\s*(STRICT|STANDARD|LIGHT|EXEMPT)\s*\|` (MULTILINE, IGNORECASE)
5. Default tier to `"UNKNOWN"` if not found
6. Return list of `TaskMeta`

**Edge cases**:
- File doesn't exist or is unreadable → return `[]` (catch `OSError`)
- No task headings found → return `[]`
- Task without Tier row → tier = `"UNKNOWN"`
- Malformed heading (e.g., `### Notes`) → ignored (regex doesn't match)

**Acceptance Criteria**:
- AC-1: `parse_phase_tasks()` correctly extracts task ID, title, and tier from phase tasklist files matching the format used by `/sc:tasklist`
- AC-2: Returns empty list on missing file, unreadable file, or file with no matching headings
- AC-3: Tier defaults to `"UNKNOWN"` when metadata table row is absent
- AC-4: Parser handles all four tier values: STRICT, STANDARD, LIGHT, EXEMPT
- AC-5: At least one test uses a fixture copied from a real phase tasklist file to validate regex against production data

**Verification**:
- Unit tests with synthetic phase files (3+ tasks, mixed tiers)
- One fixture-based test using real tasklist content
- Edge case tests (missing file, empty file, no tier row)

### D2: Scaffold Result File Creation (Priority: P0)

**Problem**: The result file doesn't exist until the agent writes it. If the agent hits `max_turns`, no file exists.

**Solution**: Add `scaffold_result_file()` to `src/superclaude/cli/sprint/scaffold.py`. This creates a parseable result file BEFORE the agent launches.

**Interface**:

```python
# src/superclaude/cli/sprint/scaffold.py

# Single source of truth for scaffold format (per Fowler review)
SCAFFOLD_TEMPLATE = """\
---
phase: {phase_number}
tasks_total: {tasks_total}
tasks_passed: 0
tasks_failed: 0
---

# Phase {phase_number} Completion Report -- {phase_name}

## Per-Task Status

| Task ID | Title | Tier | Status | Evidence |
|---------|-------|------|--------|----------|
{task_rows}

## Files Modified

_No files modified yet._

## Blockers

_None identified._
"""

def scaffold_result_file(
    result_path: Path,
    phase_number: int,
    phase_name: str,
    tasks: list[TaskMeta],
) -> None:
    """Create a scaffold result file for a sprint phase.

    The scaffold is designed to be parseable by _determine_phase_status().
    It deliberately contains NO 'status:' field and NO 'EXIT_RECOMMENDATION:'
    token, causing it to map to PASS_NO_SIGNAL if the agent never updates it.

    Creates parent directories if they don't exist.
    """
```

**Critical design properties**:
1. **No `status:` field in YAML frontmatter** — avoids false PASS/FAIL signals
2. **No `EXIT_RECOMMENDATION:` token anywhere** — avoids false continue/halt signals
3. **No `scaffolded: true` metadata** (removed per Wiegers review — no consumer exists, YAGNI)
4. **Format is a subset of the final report format** — any valid final report can overwrite the scaffold without format conflicts (per Wiegers review: full overwrite is also valid)

**Scaffold format example** (for a 3-task phase):

```markdown
---
phase: 1
tasks_total: 3
tasks_passed: 0
tasks_failed: 0
---

# Phase 1 Completion Report -- Enforce Promises and Correctness

## Per-Task Status

| Task ID | Title | Tier | Status | Evidence |
|---------|-------|------|--------|----------|
| T01.01 | Implement two-tier classification with backward mapping | STRICT | pending | --- |
| T01.02 | Implement coverage tracking with per-risk-tier metrics | STRICT | pending | --- |
| T01.03 | Implement batch-level checkpointing | STANDARD | pending | --- |

## Files Modified

_No files modified yet._

## Blockers

_None identified._
```

**Interaction with `_determine_phase_status()`**:

| Scaffold State | `status:` present? | `EXIT_RECOMMENDATION:` present? | Result |
|----------------|--------------------|---------------------------------|--------|
| Untouched scaffold | No | No | `PASS_NO_SIGNAL` |
| Agent partially updated rows | No | No | `PASS_NO_SIGNAL` |
| Agent completed + added signals | Yes (PASS) | Yes (CONTINUE) | `PASS` |
| Agent marked failure | Yes (FAIL) | Yes (HALT) | `HALT` |
| Agent overwrote entirely with full report | Yes | Yes | Normal classification |

All outcomes are correct. `PASS_NO_SIGNAL` has `is_success=True` — the sprint continues.

**Failure handling** (per Nygard review):
- Scaffold creation is wrapped in try/except
- On failure: log to both `debug_log` (JSONL telemetry) AND `stderr` (operator visibility)
- Sprint continues without scaffold — falls back to current `PASS_NO_REPORT` behavior
- This is a graceful degradation, not a hard failure

**Acceptance Criteria**:
- AC-1: `scaffold_result_file()` creates a file at the specified path
- AC-2: File contains valid YAML frontmatter with `phase`, `tasks_total`, `tasks_passed: 0`, `tasks_failed: 0`
- AC-3: YAML frontmatter does NOT contain a `status:` field
- AC-4: File does NOT contain the string `EXIT_RECOMMENDATION`
- AC-5: All tasks from the input list appear in the markdown table with `pending` status
- AC-6: `_determine_phase_status(exit_code=0, result_file=<scaffold>, output_file=<exists>)` returns `PASS_NO_SIGNAL`
- AC-7: Creates parent directories if they don't exist
- AC-8: Overwrites existing file at the same path
- AC-9: Scaffold format is a valid subset of the final report format (any valid final report can overwrite it)

**Verification**:
- Unit tests for all ACs
- Integration test: scaffold → `_determine_phase_status` → `PASS_NO_SIGNAL`

### D3: Executor Integration (Priority: P0)

**Problem**: The scaffold must be created at the right point in the sprint lifecycle.

**Solution**: Call `scaffold_result_file()` in `execute_sprint()` between `ClaudeProcess` construction and `proc_manager.start()`.

**Call site** in `src/superclaude/cli/sprint/executor.py`:

```python
proc_manager = ClaudeProcess(config, phase)

# Create scaffold result file before agent launches
try:
    from .scaffold import parse_phase_tasks, scaffold_result_file
    tasks = parse_phase_tasks(phase.file)
    scaffold_result_file(
        result_path=config.result_file(phase),
        phase_number=phase.number,
        phase_name=phase.name or f"Phase {phase.number}",
        tasks=tasks,
    )
except Exception as exc:
    import sys
    debug_log(_dbg, "scaffold_error", phase=phase.number, error=str(exc))
    print(
        f"[SCAFFOLD] Warning: could not create scaffold for phase "
        f"{phase.number}: {exc}",
        file=sys.stderr,
    )

proc_manager.start()
```

**Design rationale for placement**:
- After `ClaudeProcess` construction: phase is validated, config is resolved
- Before `proc_manager.start()`: file exists before the agent runs
- Import inside try block: scaffold module failure doesn't prevent sprint execution

**Acceptance Criteria**:
- AC-1: Scaffold file exists at `config.result_file(phase)` before `proc_manager.start()` is called
- AC-2: Scaffold creation failure does not prevent the sprint from continuing
- AC-3: Scaffold creation failure is logged to both debug log and stderr
- AC-4: Existing sprint execution behavior is unchanged when scaffold succeeds

**Verification**:
- Integration test: mock subprocess, verify result file exists before process.start()
- Failure test: simulate OSError in scaffold creation, verify sprint continues

### D4: Prompt Protocol Update (Priority: P0)

**Problem**: The current Completion Protocol instructs the agent to write a monolithic report at the end. This is the first casualty when turns run out.

**Solution**: Replace the "Completion Protocol" section in `build_prompt()` with a "Reporting Protocol" that tells the agent a scaffold already exists and instructs incremental updates.

**File**: `src/superclaude/cli/sprint/process.py`

**Before** (current, lines ~69-82 of `build_prompt()`):

```
## Completion Protocol
When ALL tasks in this phase are complete (or halted on STRICT failure):
1. Write a phase completion report to {result_file} containing:
   - YAML frontmatter with: phase, status (PASS|FAIL|PARTIAL), ...
   - Per-task status table: Task ID, Title, Tier, Status, Evidence
   - Files modified (list all paths)
   - Blockers for next phase (if any)
   - The literal string EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT
2. If any task produced file changes, list them under ## Files Modified
```

**After** (replacement):

```
## Reporting Protocol
A scaffold report already exists at {result_file} with all tasks listed as
'pending'. You may update it incrementally or overwrite it entirely.

1. AFTER completing each task, you may update {result_file}:
   - Change that task's row from 'pending' to 'pass' or 'fail'
   - Add evidence summary (test count, artifact IDs)
   - Update tasks_passed or tasks_failed counts in the YAML frontmatter

2. When ALL tasks are complete (or halted on STRICT failure), you MUST
   finalize {result_file}:
   - Add 'status: PASS' or 'status: FAIL' or 'status: PARTIAL' to the
     YAML frontmatter
   - Add the literal string EXIT_RECOMMENDATION: CONTINUE or
     EXIT_RECOMMENDATION: HALT at the end of the file
   - List all modified files under ## Files Modified
   - List any blockers for next phase under ## Blockers
```

**Key changes from original plan** (per Nygard review):
- Step 1 uses "you may" not "you must" — incremental updates are best-effort
- "You may update it incrementally or overwrite it entirely" — explicitly allows both strategies
- Step 2 uses "you MUST" — the final status and EXIT_RECOMMENDATION are required
- The existing Execution Rules and Important sections are unchanged

**Acceptance Criteria**:
- AC-1: `build_prompt()` output contains "scaffold report already exists"
- AC-2: `build_prompt()` output contains "EXIT_RECOMMENDATION: CONTINUE or EXIT_RECOMMENDATION: HALT"
- AC-3: `build_prompt()` output does NOT contain "Completion Protocol" (old section removed)
- AC-4: `build_prompt()` output contains "you MUST finalize" (mandatory final report)
- AC-5: `build_prompt()` output references the correct `result_file` path

**Verification**:
- Unit tests asserting prompt content (string containment checks)

### D5: Tests (Priority: P0)

**File created**: `tests/sprint/test_scaffold.py`
**Files modified**: `tests/sprint/test_process.py`

#### test_scaffold.py — New test module

**Class: `TestParsePhasesTasks`**

| Test | Description | Validates |
|------|-------------|-----------|
| `test_parse_extracts_ids_titles_tiers` | 3 tasks with STRICT, STANDARD, LIGHT | D1 AC-1, AC-4 |
| `test_parse_task_without_tier` | Task heading with no Tier row | D1 AC-3 |
| `test_parse_missing_file` | Non-existent path | D1 AC-2 |
| `test_parse_empty_file` | File with heading only, no tasks | D1 AC-2 |
| `test_parse_real_tasklist_fixture` | Fixture from actual phase-1-tasklist.md | D1 AC-5 |

**Class: `TestScaffoldResultFile`**

| Test | Description | Validates |
|------|-------------|-----------|
| `test_scaffold_creates_file` | File exists after call | D2 AC-1 |
| `test_scaffold_yaml_frontmatter` | Correct fields, no `status:` | D2 AC-2, AC-3 |
| `test_scaffold_task_table` | All tasks present as `pending` | D2 AC-5 |
| `test_scaffold_no_exit_recommendation` | No `EXIT_RECOMMENDATION` in content | D2 AC-4 |
| `test_scaffold_creates_parent_dirs` | Non-existent parent dirs created | D2 AC-7 |
| `test_scaffold_overwrites_existing` | Old content replaced | D2 AC-8 |
| `test_scaffold_empty_tasks` | Zero tasks → `tasks_total: 0`, valid file | D2 edge case |

**Class: `TestScaffoldStatusClassification`**

| Test | Description | Validates |
|------|-------------|-----------|
| `test_untouched_scaffold_returns_pass_no_signal` | Scaffold as-is → `PASS_NO_SIGNAL` | D2 AC-6 |
| `test_partially_updated_scaffold` | Some rows changed → `PASS_NO_SIGNAL` | D2 AC-6 |
| `test_fully_completed_scaffold` | Agent adds status + EXIT_RECOMMENDATION → `PASS` | D2 AC-9 |
| `test_scaffold_with_halt` | Agent adds `status: FAIL` + `EXIT_RECOMMENDATION: HALT` → `HALT` | D2 edge case (per Crispin review) |
| `test_scaffold_overwritten_entirely` | Agent writes completely new file → normal classification | D2 AC-9 |

**Class: `TestScaffoldPrimaryScenario`**

Primary acceptance scenario (per Adzic review):

```python
def test_max_turns_scenario(self, tmp_path):
    """
    GIVEN: A phase with 10 tasks and a scaffold result file
    WHEN: The agent completes 6 tasks, updating rows, then hits max_turns
          (simulated by not adding status: or EXIT_RECOMMENDATION:)
    THEN: result file exists with tasks_total=10
      AND: 6 tasks show 'pass', 4 show 'pending'
      AND: _determine_phase_status returns PASS_NO_SIGNAL
      AND: PASS_NO_SIGNAL.is_success is True (sprint continues)
    """
```

#### test_process.py — Additions to existing file

| Test | Description | Validates |
|------|-------------|-----------|
| `test_prompt_references_scaffold` | Contains "scaffold report already exists" | D4 AC-1 |
| `test_prompt_incremental_protocol` | Contains "you MUST finalize" | D4 AC-4 |
| `test_prompt_no_old_completion_protocol` | "Completion Protocol" absent | D4 AC-3 |

**Acceptance Criteria**:
- AC-1: All tests pass: `uv run pytest tests/sprint/test_scaffold.py tests/sprint/test_process.py -v`
- AC-2: Tests do not depend on real subprocess execution (all mocked)
- AC-3: At least one test uses fixture content from a real tasklist file

**Verification**:
- `uv run pytest tests/sprint/test_scaffold.py -v` — all scaffold tests pass
- `uv run pytest tests/sprint/test_process.py -v` — prompt tests pass
- `uv run pytest tests/sprint/ -v` — full sprint test suite regression check
- `uv run pytest tests/ -v` — full project test suite (no regressions)

## 4. Milestone Structure

### M1: Parser and Scaffold Module (P0)

**Deliverables**: D1, D2
**Dependencies**: v2.13 M1 complete (characterization tests in place)
**Rationale**: The scaffold module is self-contained and testable in isolation.

### M2: Executor Integration and Prompt Update (P0)

**Deliverables**: D3, D4
**Dependencies**: M1
**Rationale**: Requires the scaffold module to exist. Modifies `executor.py` and `process.py`.

### M3: Tests and Validation (P0)

**Deliverables**: D5
**Dependencies**: M1, M2
**Rationale**: Tests validate the complete scaffold lifecycle.

### Dependency Graph

```
v2.13 M1 (characterization tests)
    |
    v
v2.14 M1 (parser + scaffold module)
    |
    v
v2.14 M2 (executor integration + prompt update)
    |
    v
v2.14 M3 (tests + validation)
```

## 5. Non-Functional Requirements

### NFR-001: Backward Compatibility
All changes must preserve existing CLI behavior. If scaffold creation fails, sprint falls back to current behavior (`PASS_NO_REPORT`).

### NFR-002: No Status Classification Changes
`_determine_phase_status()` and `PhaseStatus` enum are not modified. The scaffold naturally maps to existing `PASS_NO_SIGNAL` status.

### NFR-003: v2.13 Test Gate
v2.13's characterization tests (D4) must pass before and after scaffold changes. This is a hard dependency.

### NFR-004: No New Dependencies
No new Python package dependencies introduced.

### NFR-005: Graceful Degradation
Scaffold creation failure must not prevent sprint execution. Failure is logged to both debug log (JSONL) and stderr (operator visibility).

## 6. Status Outcome Matrix

| Scenario | Before (no scaffold) | After (with scaffold) |
|----------|---------------------|----------------------|
| Agent completes + writes EXIT_RECOMMENDATION: CONTINUE | `PASS` | `PASS` |
| Agent partially updates, hits max_turns | `PASS_NO_REPORT` (no file) | `PASS_NO_SIGNAL` (file with partial data) |
| Agent ignores scaffold, hits max_turns | `PASS_NO_REPORT` (no file) | `PASS_NO_SIGNAL` (file with all `pending`) |
| Agent overwrites scaffold with full report | `PASS` | `PASS` |
| Agent writes EXIT_RECOMMENDATION: HALT | `HALT` | `HALT` |
| Agent writes status: FAIL + HALT | `HALT` | `HALT` |
| Timeout (exit 124) | `TIMEOUT` | `TIMEOUT` |
| Scaffold creation fails, agent completes | `PASS` | `PASS` |
| Scaffold creation fails, agent hits max_turns | `PASS_NO_REPORT` | `PASS_NO_REPORT` (graceful degradation) |

All `PASS_NO_SIGNAL` and `PASS_NO_REPORT` outcomes have `is_success=True`. Sprint continues in all non-HALT/TIMEOUT/ERROR cases.

## 7. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-001 | Agent ignores incremental update instructions | Medium | Low | Layer 2 is best-effort; scaffold (Layer 1) provides guaranteed safety net regardless |
| R-002 | Agent overwrites scaffold with incompatible format | Very Low | Low | Any valid report triggers correct status classification; scaffold format is a subset of report format |
| R-003 | Task heading regex doesn't match future tasklist formats | Low | Medium | Regex validated against real tasklist fixtures; `parse_phase_tasks` returns `[]` gracefully on no matches |
| R-004 | Scaffold creation fails (disk, permissions) | Very Low | Low | Graceful degradation to current behavior; logged to stderr |
| R-005 | Merge conflict with v2.13 on sprint/process.py | Low | Low | v2.14 is sequenced AFTER v2.13; v2.13 doesn't touch `build_prompt()` |
| R-006 | v2.13 characterization tests need updating for scaffold | Medium | Low | v2.14 M3 includes regression verification against full sprint test suite |

## 8. Files Modified

| File | Change | New/Modified |
|------|--------|-------------|
| `src/superclaude/cli/sprint/scaffold.py` | New module: `TaskMeta`, `parse_phase_tasks()`, `scaffold_result_file()`, `SCAFFOLD_TEMPLATE` | NEW |
| `src/superclaude/cli/sprint/executor.py` | Add scaffold call between ClaudeProcess construction and start() | MODIFIED |
| `src/superclaude/cli/sprint/process.py` | Replace "Completion Protocol" with "Reporting Protocol" in `build_prompt()` | MODIFIED |
| `tests/sprint/test_scaffold.py` | New test module: parser tests, scaffold tests, status classification tests, primary scenario | NEW |
| `tests/sprint/test_process.py` | Add 3 prompt content tests | MODIFIED |

**Not modified**: `models.py`, `_determine_phase_status()`, `PhaseStatus`, `SprintConfig`, `Phase`, `execution-log.jsonl` format, TUI, diagnostics, monitor, config.

## 9. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Scaffold file exists after max_turns | 100% of phases | Manual: re-run cleanup-audit sprint, verify all 5 phases have result files |
| No `PASS_NO_REPORT` status in new sprint runs | 0 occurrences | `grep pass_no_report execution-log.jsonl` returns 0 |
| All existing sprint tests pass | 100% | `uv run pytest tests/sprint/ -v` |
| Full project test suite passes | 100% | `uv run pytest tests/ -v` |
| New test count | >= 17 | Count tests in `test_scaffold.py` + new tests in `test_process.py` |

## 10. Out of Scope (Deferred)

| Item | Reason |
|------|--------|
| Layer 3 output parsing (reconstruct report from raw session output) | Complex, fragile; Layers 1+2 solve 95% of the problem |
| New `PASS_PARTIAL` status for partially-updated scaffolds | `PASS_NO_SIGNAL` already correctly handles this; new status would be a breaking change for log consumers |
| `scaffolded: true` metadata in frontmatter | No consumer exists (YAGNI); can be added later if post-hoc analysis tools need it |
| Scaffold for non-sprint consumers (roadmap) | Roadmap steps are short-lived and don't hit max_turns |
