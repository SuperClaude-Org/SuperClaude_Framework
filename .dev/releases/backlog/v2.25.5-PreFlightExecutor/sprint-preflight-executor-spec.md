```yaml
---
title: "Sprint Pre-Flight Python Executor"
version: "1.0.0"
status: draft
feature_id: FR-PREFLIGHT
parent_feature: null
spec_type: new_feature
complexity_score: 0.55
complexity_class: moderate
target_release: v2.26
authors: [user, claude]
created: 2026-03-15
quality_scores:
  clarity: 9.0
  completeness: 8.5
  testability: 9.0
  consistency: 9.0
  overall: 8.9
---
```

## 1. Problem Statement

The sprint runner (`superclaude sprint run`) spawns a Claude subprocess per phase. When phase tasks instruct the agent to execute `claude` CLI commands (e.g., `claude --print -p "hello" --max-turns 1`), the nested `claude` process deadlocks. The outer agent polls the hung subprocess indefinitely until timeout or manual interrupt, wasting the entire phase budget and stalling the sprint.

More broadly, any phase whose tasks consist entirely of deterministic shell commands and simple conditional logic does not require an LLM agent. Delegating these tasks to Claude wastes API tokens, introduces non-determinism, and — in the case of nested `claude` invocations — causes hard failures.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| Phase 1 ran 857s, exit code 143 (SIGTERM), zero phases completed | `.dev/releases/current/v2.24.5/execution-log.jsonl` | Complete sprint stall; manual intervention required |
| Nested `claude --print -p "hello"` (PID 283918) hung with 0 bytes output for 14+ minutes | `results/phase-1-output.txt` stream-json analysis | Agent consumed 6 `TaskOutput` polling cycles, all timeout |
| Agent's `Task` tool spawned `claude` inside the outer `claude` subprocess | `ps aux` output captured in phase-1-output.txt | Recursive `claude` nesting deadlocks due to API contention / session detection |
| All 5 Phase 1 tasks are EXEMPT tier with no code changes | `phase-1-tasklist.md` tier distribution | Phase is pure validation — no LLM reasoning needed |

### 1.2 Scope Boundary

**In scope**:
- Annotation-based execution mode for phases (`python`, `claude`, `skip`)
- Pre-sprint Python executor for `python`-mode phases
- Structured `**Command:**` field and `| Classifier |` metadata for tasks
- Classifier registry with named Python functions
- Result file generation compatible with `_determine_phase_status()`
- Evidence artifact writing for preflight tasks

**Out of scope**:
- Tasklist generator (`/sc:tasklist`) auto-detection of python-eligible phases
- Per-task execution mode (only phase-level)
- Conditional phase activation logic (future `condition` field)
- Changes to the Claude-mode execution path
- TUI display changes for preflight phases (can use existing `SKIPPED` display)

## 2. Solution Overview

Add a pre-sprint execution hook that identifies phases annotated with `execution_mode: python` in the tasklist index, parses their tasks, extracts shell commands from structured `**Command:**` fields, executes them via `subprocess.run()`, applies named Python classifiers, writes evidence artifacts and result files, then marks those phases as complete before the main Claude-subprocess loop begins. Phases annotated `skip` are bypassed entirely.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Execution scope | Any shell command | Claude-only nesting guard; entire-phase detection | Generality: any deterministic shell task benefits, not just `claude` nesting |
| Guard location | Pre-sprint hook in `execute_sprint()` | Per-phase guard in loop; prompt modification | Pre-sprint is cleanest: all preflight work completes before any Claude subprocess launches |
| Detection method | Annotation-based (`execution_mode` column) | Tier-based; content-based regex; hybrid | Explicit > heuristic. Manual annotation prevents false positives (score: 7.77/10) |
| Task lifecycle scope | Full mini-executor (B3) | Shell-only (B1); shell+artifacts (B2) | Deterministic Python beats LLM interpretation. Zero API calls. Existing `_subprocess_factory` + `AggregatedPhaseReport` designed for this pattern (score: 8.15/10) |
| Post-preflight handling | Skip entirely — Python writes result file | Claude verify; configurable | `AggregatedPhaseReport.to_markdown()` already produces exact format `_determine_phase_status()` parses. Zero tokens (score: 8.40/10) |
| Annotation location | Index-level column in Phase Files table | Phase file YAML frontmatter; per-task field; dual-level | `discover_phases()` already reads the index — zero additional I/O. ~10 lines of parser change (score: 0.960) |
| Annotation values | `claude \| python \| skip` | python-gate; hybrid; dry-run; manual | Three values. Execution mode = mechanism only. Gating semantics belong in a separate field |
| Command extraction | Structured `**Command:**` field | Regex from backticks; both | Unambiguous, trivial to parse. One regex pattern |
| Conditional logic | Hardcoded Python classifiers via `\| Classifier \|` | Inline DSL; structured assertion block | Zero parsing fragility. Codebase already classifies outputs in Python (`FailureClassifier`, `TrailingGatePolicy`). ~30 LOC (score: 9.19/10) |

### 2.2 Workflow / Data Flow

```
superclaude sprint run tasklist-index.md
    |
    v
load_sprint_config()
    |-- discover_phases()  <-- now parses Execution Mode column
    |
    v
execute_sprint(config)
    |
    |-- [PRE-SPRINT HOOK] execute_preflight_phases(config)
    |       |
    |       |-- for phase in active_phases where execution_mode == "python":
    |       |       |-- parse_tasklist(phase.file)
    |       |       |-- for task in tasks:
    |       |       |       |-- extract **Command:** field
    |       |       |       |-- subprocess.run(command, capture_output=True)
    |       |       |       |-- apply classifier (if | Classifier | present)
    |       |       |       |-- write artifacts/D-NNNN/evidence.md
    |       |       |       |-- build TaskResult
    |       |       |-- aggregate_task_results() -> AggregatedPhaseReport
    |       |       |-- report.to_markdown() -> results/phase-N-result.md
    |       |       |-- build PhaseResult(status=PREFLIGHT_PASS)
    |       |
    |       |-- return list[PhaseResult]
    |
    |-- sprint_result.phase_results.extend(preflight_results)
    |
    |-- for phase in active_phases:       <-- MAIN LOOP (unchanged)
    |       |-- if phase.execution_mode != "claude": continue
    |       |-- ClaudeProcess(config, phase).start()
    |       |-- ... existing poll/monitor/status logic ...
    |
    v
  sprint complete
```

## 3. Functional Requirements

### FR-PREFLIGHT.1: Execution Mode Annotation Parsing

**Description**: The sprint runner reads an `Execution Mode` column from the Phase Files table in `tasklist-index.md` and stores the value on each `Phase` object.

**Acceptance Criteria**:
- [ ] `Phase` dataclass has an `execution_mode: str` field defaulting to `"claude"`
- [ ] `discover_phases()` parses the `Execution Mode` column from the Phase Files markdown table
- [ ] Recognized values: `claude`, `python`, `skip` (case-insensitive)
- [ ] Unrecognized values raise `click.ClickException` with the invalid value and phase number
- [ ] Missing column defaults all phases to `"claude"`

**Dependencies**: None

### FR-PREFLIGHT.2: Pre-Sprint Preflight Executor

**Description**: A new `execute_preflight_phases()` function executes all `python`-mode phases before the main Claude loop, using `subprocess.run()` for shell commands.

**Acceptance Criteria**:
- [ ] Called at the top of `execute_sprint()`, before the phase loop
- [ ] Iterates `config.active_phases` where `execution_mode == "python"`
- [ ] Parses tasks from each phase file via existing `parse_tasklist()`
- [ ] For each task, extracts the shell command from the `**Command:**` markdown field
- [ ] Executes each command via `subprocess.run(shell=False, capture_output=True, timeout=120)`
- [ ] Captures stdout, stderr, exit code, and wall-clock duration per task
- [ ] Builds `TaskResult` per task with appropriate `TaskStatus` (PASS if exit_code==0, FAIL otherwise)
- [ ] Returns `list[PhaseResult]` for integration into `sprint_result`

**Dependencies**: FR-PREFLIGHT.1

### FR-PREFLIGHT.3: Command Field Extraction

**Description**: `parse_tasklist()` is extended to extract a `**Command:**` field from task blocks into a new `command` attribute on `TaskEntry`.

**Acceptance Criteria**:
- [ ] `TaskEntry` dataclass gains `command: str = ""` field
- [ ] `parse_tasklist()` extracts the value from `` **Command:** `<shell command>` `` lines
- [ ] Backtick delimiters are stripped; the raw command string is stored
- [ ] Tasks without a `**Command:**` field have `command == ""`
- [ ] Commands with pipes, redirects, and quoted arguments are preserved verbatim

**Dependencies**: None

### FR-PREFLIGHT.4: Classifier Registry

**Description**: A registry of named Python functions that classify task output (stdout, stderr, exit_code) into labeled outcomes.

**Acceptance Criteria**:
- [ ] New module `src/superclaude/cli/sprint/classifiers.py` with a `CLASSIFIERS` dict
- [ ] Each classifier is a callable with signature `(exit_code: int, stdout: str, stderr: str) -> str`
- [ ] Return value is a classification label string (e.g., `"WORKING"`, `"BROKEN"`, `"CLI FAILURE"`)
- [ ] `parse_tasklist()` extracts `| Classifier |` from task metadata tables into `TaskEntry.classifier: str = ""`
- [ ] `execute_preflight_phases()` looks up classifiers by name; missing classifier raises `KeyError` with task ID and classifier name
- [ ] At least one built-in classifier: `empirical_gate_v1`

**Dependencies**: FR-PREFLIGHT.2, FR-PREFLIGHT.3

### FR-PREFLIGHT.5: Evidence Artifact Writing

**Description**: The preflight executor writes structured evidence files for each task into the artifact directory tree.

**Acceptance Criteria**:
- [ ] For each task, writes to `artifacts/D-NNNN/evidence.md` (path from deliverable registry, or `artifacts/<task_id>/evidence.md` if no registry entry)
- [ ] Evidence file contains: command executed, exit code, stdout (truncated to 10KB), stderr (truncated to 2KB), wall-clock duration, classification label (if classifier applied)
- [ ] Artifact directories are created with `mkdir(parents=True, exist_ok=True)`

**Dependencies**: FR-PREFLIGHT.2

### FR-PREFLIGHT.6: Result File Generation

**Description**: The preflight executor writes a `phase-N-result.md` file compatible with `_determine_phase_status()`.

**Acceptance Criteria**:
- [ ] Uses `AggregatedPhaseReport.to_markdown()` to generate the result file content
- [ ] Result file written to `config.result_file(phase)`
- [ ] YAML frontmatter includes `source: preflight` for auditability
- [ ] Contains `EXIT_RECOMMENDATION: CONTINUE` (all tasks pass) or `EXIT_RECOMMENDATION: HALT` (any task fails)
- [ ] `_determine_phase_status()` correctly parses the generated file without modification

**Dependencies**: FR-PREFLIGHT.2

### FR-PREFLIGHT.7: Main Loop Phase Skipping

**Description**: The main `execute_sprint()` phase loop skips phases already handled by preflight or annotated as `skip`.

**Acceptance Criteria**:
- [ ] Phases with `execution_mode == "python"` are skipped in the main loop (already executed in preflight)
- [ ] Phases with `execution_mode == "skip"` are skipped with `PhaseStatus.SKIPPED`
- [ ] Skipped phases produce a `PhaseResult` with appropriate status
- [ ] Sprint outcome correctly reflects preflight + main loop results combined

**Dependencies**: FR-PREFLIGHT.1, FR-PREFLIGHT.2

### FR-PREFLIGHT.8: PhaseStatus.PREFLIGHT_PASS Enum Value

**Description**: Add a new `PhaseStatus` enum value to distinguish preflight-executed phases from Claude-executed phases.

**Acceptance Criteria**:
- [ ] `PhaseStatus.PREFLIGHT_PASS = "preflight_pass"` added to the enum
- [ ] `is_success` property returns `True` for `PREFLIGHT_PASS`
- [ ] `is_failure` property returns `False` for `PREFLIGHT_PASS`
- [ ] Logger and TUI handle the new status without errors

**Dependencies**: None

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/cli/sprint/classifiers.py` | Classifier registry — named Python functions for output classification | None |
| `tests/sprint/test_preflight.py` | Unit/integration tests for preflight executor | `executor.py`, `config.py`, `classifiers.py` |
| `tests/sprint/test_classifiers.py` | Unit tests for classifier functions | `classifiers.py` |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/sprint/models.py` | Add `execution_mode: str` to `Phase`; add `command: str`, `classifier: str` to `TaskEntry`; add `PREFLIGHT_PASS` to `PhaseStatus` | Data model support for preflight |
| `src/superclaude/cli/sprint/config.py` | Extend `discover_phases()` to parse Execution Mode column; extend `parse_tasklist()` to extract `**Command:**` and `| Classifier |` | Discovery and parsing of new fields |
| `src/superclaude/cli/sprint/executor.py` | Add `execute_preflight_phases()` function; modify `execute_sprint()` to call preflight and skip non-claude phases | Core preflight execution logic |

### 4.4 Module Dependency Graph

```
classifiers.py (NEW)         models.py (MODIFIED)
      |                         |
      v                         v
executor.py (MODIFIED) <--- config.py (MODIFIED)
      |
      v
  execute_sprint()
      |
      |-- execute_preflight_phases()  [NEW]
      |       |-- parse_tasklist()    [EXTENDED]
      |       |-- CLASSIFIERS[name]   [NEW]
      |       |-- AggregatedPhaseReport.to_markdown()  [EXISTING]
      |       |-- subprocess.run()    [stdlib]
      |
      |-- main phase loop             [EXISTING, with skip guard]
```

### 4.5 Data Models

```python
# models.py — Phase (extended)
@dataclass
class Phase:
    number: int
    file: Path
    name: str = ""
    execution_mode: str = "claude"  # NEW: "claude" | "python" | "skip"

# models.py — TaskEntry (extended)
@dataclass
class TaskEntry:
    task_id: str
    title: str
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    command: str = ""       # NEW: shell command from **Command:** field
    classifier: str = ""    # NEW: classifier name from | Classifier | row

# models.py — PhaseStatus (extended)
class PhaseStatus(Enum):
    # ... existing values ...
    PREFLIGHT_PASS = "preflight_pass"  # NEW

# classifiers.py — Classifier registry
ClassifierFn = Callable[[int, str, str], str]  # (exit_code, stdout, stderr) -> label

CLASSIFIERS: dict[str, ClassifierFn] = {
    "empirical_gate_v1": lambda exit_code, stdout, stderr: (
        "CLI FAILURE" if exit_code != 0
        else "WORKING" if "PINEAPPLE" in stdout
        else "BROKEN"
    ),
}
```

### 4.6 Implementation Order

```
1. Phase + TaskEntry model changes     -- no dependencies, enables all other work
   PhaseStatus.PREFLIGHT_PASS          -- [parallel with step 1]
2. classifiers.py module               -- depends on model types only
3. config.py parser extensions         -- depends on step 1 (new fields on models)
   test_classifiers.py                 -- [parallel with step 3]
4. execute_preflight_phases()          -- depends on steps 1, 2, 3
5. execute_sprint() integration        -- depends on step 4
6. test_preflight.py                   -- depends on steps 4, 5
7. Tasklist format documentation       -- parallel with any step
```

## 5. Interface Contracts

### 5.1 Tasklist Format Changes

**Phase Files table in `tasklist-index.md`** (new column):

```markdown
| Phase | File | Phase Name | Task IDs | Tier Distribution | Execution Mode |
|---|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Empirical Gate | T01.01-T01.05 | EXEMPT: 5 | python |
| 2 | phase-2-tasklist.md | FIX-001 | T02.01-T02.06 | STRICT: 2, STANDARD: 3 | claude |
| 5 | phase-5-tasklist.md | Conditional Fallback | T05.01-T05.07 | STRICT: 4 | skip |
```

**Per-task metadata table** (new optional rows):

```markdown
| Classifier | empirical_gate_v1 |
```

**Per-task new field** (in task body):

```markdown
**Command:** `claude --print -p "hello" --max-turns 1`
```

### 5.2 Classifier Function Signature

```python
def classifier_name(exit_code: int, stdout: str, stderr: str) -> str:
    """Classify task output into a labeled outcome.

    Args:
        exit_code: Process exit code (0 = success).
        stdout: Captured standard output (full content).
        stderr: Captured standard error (full content).

    Returns:
        Classification label string (e.g., "WORKING", "BROKEN").
        Empty string means no classification (just pass/fail from exit code).
    """
```

### 5.3 Evidence File Format

```markdown
# Evidence: T01.01 — Verify claude CLI availability

**Command:** `claude --print -p "hello" --max-turns 1`
**Exit Code:** 0
**Duration:** 2.3s
**Classification:** WORKING

## stdout
```
Hello! How can I help you today?
```

## stderr
```
(empty)
```

**Source:** preflight executor
**Timestamp:** 2026-03-15T04:45:55Z
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-PREFLIGHT.1 | Preflight phase execution time | < 30s for 5 EXEMPT tasks | Wall-clock timing in execution log |
| NFR-PREFLIGHT.2 | Zero Claude API tokens for python-mode phases | 0 tokens | No `ClaudeProcess` instantiated for python phases |
| NFR-PREFLIGHT.3 | Result file compatibility | `_determine_phase_status()` parses preflight result files identically to Claude-generated ones | Unit test with both sources |
| NFR-PREFLIGHT.4 | Single-line rollback | Removing the `execute_preflight_phases()` call reverts to all-Claude behavior | Code review |
| NFR-PREFLIGHT.5 | Command timeout | 120s per command, configurable | `subprocess.run(timeout=...)` |

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Preflight result file format drifts from Claude-generated format | Low | High — sprint halts on parse failure | Shared unit test validates both `AggregatedPhaseReport.to_markdown()` output and `_determine_phase_status()` parsing |
| Shell command requires environment not available in preflight context | Medium | Medium — task fails with unclear error | Evidence file captures full stderr; preflight logs command and environment |
| Classifier function has a bug, misclassifies output | Low | Medium — downstream phases make wrong decisions | Unit tests per classifier with known inputs/outputs |
| `**Command:**` field has quoting/escaping issues | Medium | Low — task fails, sprint halts on HALT recommendation | Parse as single string, split via `shlex.split()`, test with pipes and quotes |
| Future phases need mixed python/claude tasks | Low | Low — requires per-task annotation (out of scope) | Phase-level annotation is sufficient for known patterns; migration path to per-task is non-breaking |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `test_phase_execution_mode_default` | `tests/sprint/test_models.py` | `Phase.execution_mode` defaults to `"claude"` |
| `test_task_entry_command_field` | `tests/sprint/test_models.py` | `TaskEntry.command` and `TaskEntry.classifier` fields exist |
| `test_phase_status_preflight_pass` | `tests/sprint/test_models.py` | `PREFLIGHT_PASS.is_success == True`, `is_failure == False` |
| `test_discover_phases_execution_mode` | `tests/sprint/test_config.py` | Parses Execution Mode column from index markdown |
| `test_discover_phases_missing_column` | `tests/sprint/test_config.py` | Missing column defaults to `"claude"` |
| `test_discover_phases_invalid_mode` | `tests/sprint/test_config.py` | Invalid value raises `ClickException` |
| `test_parse_tasklist_command_field` | `tests/sprint/test_config.py` | Extracts `**Command:**` field into `TaskEntry.command` |
| `test_parse_tasklist_classifier_field` | `tests/sprint/test_config.py` | Extracts `\| Classifier \|` into `TaskEntry.classifier` |
| `test_parse_tasklist_no_command` | `tests/sprint/test_config.py` | Tasks without `**Command:**` have empty string |
| `test_empirical_gate_v1_working` | `tests/sprint/test_classifiers.py` | exit_code=0, "PINEAPPLE" in stdout -> "WORKING" |
| `test_empirical_gate_v1_broken` | `tests/sprint/test_classifiers.py` | exit_code=0, no "PINEAPPLE" -> "BROKEN" |
| `test_empirical_gate_v1_cli_failure` | `tests/sprint/test_classifiers.py` | exit_code=1 -> "CLI FAILURE" |
| `test_classifier_registry_lookup` | `tests/sprint/test_classifiers.py` | `CLASSIFIERS["empirical_gate_v1"]` is callable |
| `test_classifier_missing_raises` | `tests/sprint/test_classifiers.py` | Missing classifier key raises `KeyError` |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| `test_preflight_executes_python_phases` | `execute_preflight_phases()` runs commands, writes evidence, returns PhaseResults |
| `test_preflight_skips_claude_phases` | Only `python`-mode phases processed by preflight |
| `test_preflight_result_file_parseable` | `_determine_phase_status()` correctly parses preflight-generated result files |
| `test_preflight_halt_on_failure` | Failed command -> `EXIT_RECOMMENDATION: HALT` in result file |
| `test_execute_sprint_skips_preflight_phases` | Main loop `continue`s past `python` and `skip` phases |
| `test_execute_sprint_combined_results` | `sprint_result.phase_results` contains both preflight and main-loop results |
| `test_preflight_command_timeout` | Command exceeding timeout produces FAIL status |
| `test_preflight_classifier_applied` | Classifier output written to evidence file and available in TaskResult |

### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Full preflight sprint | Create a tasklist with Phase 1 = `python`, Phase 2 = `claude`. Run `superclaude sprint run`. | Phase 1 executes in Python (< 30s), Phase 2 launches Claude subprocess. Both results in execution log. |
| Skip-mode phase | Create a tasklist with Phase 5 = `skip`. Run sprint. | Phase 5 appears as SKIPPED in log, no subprocess launched. |
| Preflight failure halts sprint | Create a python-mode phase with a command that exits non-zero. | Sprint halts with `EXIT_RECOMMENDATION: HALT`, diagnostic report generated. |
| Nested claude prevention | Create a python-mode phase with `claude --print -p "hello"` as command. | Command executes directly via `subprocess.run()`, completes in seconds, no deadlock. |

## 10. Downstream Inputs

### For sc:roadmap
- Primary theme: "Pre-sprint Python executor for deterministic phase execution"
- Single milestone with 6 components (model changes, classifier module, parser extensions, preflight executor, main loop integration, tests)
- Estimated complexity: moderate (~400 LOC new code + ~200 LOC tests)

### For sc:tasklist
- Phase 1: Model and enum changes (3-4 tasks, LIGHT/STANDARD tier)
- Phase 2: Classifier module + parser extensions (4-5 tasks, STANDARD tier)
- Phase 3: Preflight executor function (5-6 tasks, STRICT tier)
- Phase 4: Main loop integration + skip logic (2-3 tasks, STANDARD tier)
- Phase 5: Test suite (5-6 tasks, STANDARD tier)
- Phase 6: Documentation and validation (2-3 tasks, EXEMPT tier)
- Tasklist format note: this release's own tasklist can use `execution_mode: claude` for all phases (no python-mode phases in the implementation itself)

## 11. Open Items

None. All design questions resolved through adversarial debate pipeline (Q4-Q10).

## 12. Brainstorm Gap Analysis

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-01 | Command field parsing does not specify handling of multi-line commands | Low | FR-PREFLIGHT.3 | backend |
| GAP-02 | No specification for how preflight interacts with `--dry-run` flag | Low | FR-PREFLIGHT.2 | qa |
| GAP-03 | Classifier error handling (exception in classifier function) not specified | Low | FR-PREFLIGHT.4 | backend |

GAP-01: Multi-line commands are uncommon in EXEMPT-tier validation tasks. If needed, the `**Command:**` field can use `\` continuation. Defer until a concrete use case arises.

GAP-02: `--dry-run` should list python-mode phases with "[preflight]" annotation. Trivial to add in `_print_dry_run()`. Can be addressed during implementation.

GAP-03: Classifier exceptions should be caught, logged, and treated as task failure with `TaskStatus.FAIL`. Can be specified in the roadmap as a sub-task of FR-PREFLIGHT.4.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Preflight | Pre-sprint execution of python-mode phases before any Claude subprocess launches |
| Execution mode | Phase-level annotation (`claude`, `python`, `skip`) controlling how the phase is executed |
| Classifier | Named Python function that maps (exit_code, stdout, stderr) to a classification label |
| Evidence file | Structured markdown artifact documenting command output, exit code, and classification |
| Empirical gate | A validation phase that tests CLI behavior empirically to make a binary decision |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `docs/generated/python-runner-scope-debate/` | Q4 adversarial debate: task lifecycle scope (B3 selected) |
| `docs/generated/preflight-debate/` | Q5 adversarial debate: post-preflight handling (2a selected) |
| `docs/generated/q6-execution-mode-debate/` | Q6 adversarial debate: annotation location (3a selected) |
| `docs/generated/execution-mode-debate/` | Q7 adversarial debate: annotation values (claude/python/skip) |
| `docs/generated/q8-execution-mode-debate/` | Q8 adversarial debate: auto vs manual annotation |
| `docs/generated/adversarial-assertion-engine/` | Q10 adversarial debate: conditional logic engine (Option C selected) |
| `.dev/releases/current/v2.24.5/execution-log.jsonl` | Evidence of the nested claude deadlock |
| `.dev/releases/current/v2.24.5/results/phase-1-output.txt` | Stream-json output showing the stall |
| `src/superclaude/examples/release-spec-template.md` | Template this spec conforms to |
