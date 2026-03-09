# Phase 1 -- Parser and Scaffold Module

Create a self-contained `src/superclaude/cli/sprint/scaffold.py` module that parses task metadata from phase tasklist files and generates scaffold result files. This module has zero dependencies on executor, process, or monitor code and is testable in isolation. Blocked by v2.13 M1 (characterization tests must be in place first).

### T01.01 -- Implement `TaskMeta` dataclass in `scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | The scaffold needs a structured representation of task metadata extracted from phase files |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0001/evidence.md`

**Deliverables:**
- `TaskMeta` dataclass in `src/superclaude/cli/sprint/scaffold.py` with fields `id: str`, `title: str`, `tier: str` and tier defaulting to `"UNKNOWN"`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/models.py` to understand existing dataclass patterns in the sprint module
2. **[PLANNING]** Verify `src/superclaude/cli/sprint/scaffold.py` does not already exist
3. **[EXECUTION]** Create `src/superclaude/cli/sprint/scaffold.py` with module docstring and imports (`dataclasses`, `Path`, `re`)
4. **[EXECUTION]** Define `TaskMeta` dataclass with `id: str`, `title: str`, `tier: str = "UNKNOWN"`
5. **[VERIFICATION]** Verify the dataclass instantiates correctly: `TaskMeta(id="T01.01", title="Test", tier="STRICT")` and `TaskMeta(id="T01.01", title="Test")` defaults tier to `"UNKNOWN"`
6. **[COMPLETION]** Record deliverable D-0001 in execution log

**Acceptance Criteria:**
- `TaskMeta(id="T01.01", title="Test task", tier="STRICT")` creates an instance with all three fields accessible as attributes
- Tier defaults to `"UNKNOWN"` when not provided: `TaskMeta(id="T01.01", title="Test task").tier == "UNKNOWN"`
- Dataclass follows the `@dataclass` pattern used in `models.py` (frozen not required; simple mutable dataclass)
- File `src/superclaude/cli/sprint/scaffold.py` exists and is importable: `from superclaude.cli.sprint.scaffold import TaskMeta`

**Validation:**
- `uv run python -c "from superclaude.cli.sprint.scaffold import TaskMeta; t = TaskMeta(id='T01.01', title='Test', tier='STRICT'); assert t.tier == 'STRICT'; t2 = TaskMeta(id='T01.01', title='Test'); assert t2.tier == 'UNKNOWN'; print('PASS')"`
- Evidence: `scaffold.py` exists at `src/superclaude/cli/sprint/scaffold.py` with `TaskMeta` importable

**Dependencies:** None (first task in first phase)
**Rollback:** Delete `src/superclaude/cli/sprint/scaffold.py`
**Notes:** This is the foundation for all subsequent scaffold work.

---

### T01.02 -- Implement `parse_phase_tasks()` function in `scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | The scaffold needs to extract task IDs, titles, and tiers from phase tasklist files to populate the scaffold table |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Deliverables:**
- `parse_phase_tasks(phase_file: Path) -> list[TaskMeta]` function in `src/superclaude/cli/sprint/scaffold.py`

**Steps:**
1. **[PLANNING]** Read a real phase tasklist file (e.g., `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/tasklist/phase-1-tasklist.md`) to understand the exact heading and metadata table format
2. **[PLANNING]** Confirm task heading regex `^###\s+(T\d{2}\.\d{2})\s+--\s+(.+)$` matches real headings and tier regex `^\|\s*Tier\s*\|\s*(STRICT|STANDARD|LIGHT|EXEMPT)\s*\|` matches real metadata rows
3. **[EXECUTION]** Implement `parse_phase_tasks()` with: (a) file read using `errors="replace"`, (b) heading regex scan with `re.MULTILINE`, (c) per-heading text block extraction, (d) tier regex search within each block, (e) `"UNKNOWN"` default for missing tiers
4. **[EXECUTION]** Add `OSError` try/except returning `[]` for missing/unreadable files
5. **[VERIFICATION]** Test against a synthetic 3-task file with mixed tiers (STRICT, STANDARD, LIGHT) and verify all fields extracted correctly
6. **[COMPLETION]** Record deliverable D-0002 in execution log

**Acceptance Criteria:**
- `parse_phase_tasks()` returns a list of `TaskMeta` with correct `id`, `title`, and `tier` for files matching the `### T01.01 -- Title` heading format
- Returns `[]` on missing file (`OSError`), empty file, or file with no matching headings
- Tier defaults to `"UNKNOWN"` when the `| Tier | ... |` metadata row is absent from a task's block
- Handles all four tier values: `parse_phase_tasks()` correctly extracts STRICT, STANDARD, LIGHT, and EXEMPT

**Validation:**
- `uv run pytest tests/sprint/test_scaffold.py::TestParsePhaseTasks -v` (once tests exist in T03.01)
- Evidence: function is importable and processes real phase file content correctly

**Dependencies:** T01.01 (TaskMeta dataclass must exist)
**Rollback:** Remove `parse_phase_tasks()` from `scaffold.py`
**Notes:** Regex validated against real tasklist content from v2.13 phase files.

---

### T01.03 -- Implement `SCAFFOLD_TEMPLATE` constant in `scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | Single source of truth for the scaffold file format ensures consistency between scaffold creation and status classification |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0003/evidence.md`

**Deliverables:**
- `SCAFFOLD_TEMPLATE` string constant in `src/superclaude/cli/sprint/scaffold.py` with YAML frontmatter placeholders and markdown table structure

**Steps:**
1. **[PLANNING]** Read the spec's scaffold format example (release-spec.md Section D2) to capture the exact template structure
2. **[PLANNING]** Verify template has NO `status:` field and NO `EXIT_RECOMMENDATION` string anywhere
3. **[EXECUTION]** Add `SCAFFOLD_TEMPLATE` constant with placeholders: `{phase_number}`, `{tasks_total}`, `{phase_name}`, `{task_rows}`
4. **[EXECUTION]** YAML frontmatter includes: `phase`, `tasks_total`, `tasks_passed: 0`, `tasks_failed: 0` — nothing else
5. **[VERIFICATION]** Assert `"status:" not in SCAFFOLD_TEMPLATE` and `"EXIT_RECOMMENDATION" not in SCAFFOLD_TEMPLATE`
6. **[COMPLETION]** Record deliverable D-0003 in execution log

**Acceptance Criteria:**
- `SCAFFOLD_TEMPLATE` contains YAML frontmatter with `phase:`, `tasks_total:`, `tasks_passed: 0`, `tasks_failed: 0` placeholders
- `"status:" not in SCAFFOLD_TEMPLATE` — no status field present in the template
- `"EXIT_RECOMMENDATION" not in SCAFFOLD_TEMPLATE` — no exit recommendation token present
- Template is importable: `from superclaude.cli.sprint.scaffold import SCAFFOLD_TEMPLATE`

**Validation:**
- `uv run python -c "from superclaude.cli.sprint.scaffold import SCAFFOLD_TEMPLATE; assert 'status:' not in SCAFFOLD_TEMPLATE; assert 'EXIT_RECOMMENDATION' not in SCAFFOLD_TEMPLATE; assert '{phase_number}' in SCAFFOLD_TEMPLATE; print('PASS')"`
- Evidence: template string verified against critical design properties

**Dependencies:** T01.01 (module must exist)
**Rollback:** Remove `SCAFFOLD_TEMPLATE` from `scaffold.py`
**Notes:** Template format is a subset of the final report format — any valid final report can overwrite it.

---

### T01.04 -- Implement `scaffold_result_file()` function in `scaffold.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | This is Layer 1 of the two-layer defense: creates a deterministic result file before the agent launches |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Deliverables:**
- `scaffold_result_file(result_path, phase_number, phase_name, tasks)` function in `src/superclaude/cli/sprint/scaffold.py`

**Steps:**
1. **[PLANNING]** Review `SCAFFOLD_TEMPLATE` and `TaskMeta` from T01.01/T01.03
2. **[PLANNING]** Review `_determine_phase_status()` in `executor.py` to confirm scaffold file will map to `PASS_NO_SIGNAL`
3. **[EXECUTION]** Implement `scaffold_result_file()`: create parent dirs with `result_path.parent.mkdir(parents=True, exist_ok=True)`, format task rows as `| {id} | {title} | {tier} | pending | --- |`, format template, write with `encoding="utf-8"`
4. **[EXECUTION]** Handle empty tasks list (tasks_total=0, no rows in table)
5. **[VERIFICATION]** Create a scaffold file in a temp directory, read it back, verify YAML frontmatter fields and task table content
6. **[COMPLETION]** Record deliverable D-0004 in execution log

**Acceptance Criteria:**
- `scaffold_result_file()` creates a file at `result_path` with valid YAML frontmatter containing `phase`, `tasks_total`, `tasks_passed: 0`, `tasks_failed: 0`
- All input `TaskMeta` objects appear in the markdown table with `pending` status and `---` evidence
- `result_path.parent` directories are created if they don't exist (`mkdir(parents=True, exist_ok=True)`)
- Calling `scaffold_result_file()` on an existing file overwrites it completely

**Validation:**
- `uv run pytest tests/sprint/test_scaffold.py::TestScaffoldResultFile -v` (once tests exist in T03.02)
- Evidence: scaffold file content matches expected format when inspected

**Dependencies:** T01.01 (TaskMeta), T01.03 (SCAFFOLD_TEMPLATE)
**Rollback:** Remove `scaffold_result_file()` from `scaffold.py`
**Notes:** Uses encoding="utf-8" explicitly per architecture review finding A-1.

---

### Checkpoint: End of Phase 1

**Purpose:** Verify the scaffold module is self-contained, importable, and functionally correct before integrating into the executor.

**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`

**Verification:**
- `from superclaude.cli.sprint.scaffold import TaskMeta, parse_phase_tasks, scaffold_result_file, SCAFFOLD_TEMPLATE` succeeds without import errors
- `SCAFFOLD_TEMPLATE` contains no `status:` field and no `EXIT_RECOMMENDATION` token
- `scaffold_result_file()` creates a file that `_determine_phase_status(exit_code=0, result_file=<scaffold>, output_file=<exists>)` classifies as `PASS_NO_SIGNAL`

**Exit Criteria:**
- All 4 deliverables (D-0001 through D-0004) are implemented and importable
- `scaffold.py` has zero imports from `executor.py`, `process.py`, `monitor.py`, or `tui.py` (self-contained module)
- No regressions in existing sprint tests: `uv run pytest tests/sprint/ -v` passes
