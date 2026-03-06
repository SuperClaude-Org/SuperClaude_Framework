# Phase 1 -- Foundation: Pipeline Module

Extract a shared `pipeline/` module from `sprint/` containing generic step sequencing, gate validation, parallel dispatch, and data models. Establish one-directional dependency: `pipeline/` has no imports from `sprint/` or `roadmap/` (NFR-007). This phase is the sole prerequisite for all subsequent work.

### T01.01 -- Create `pipeline/models.py` with PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck dataclasses

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | The pipeline module requires data models that both sprint and roadmap consume without sprint-specific coupling. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, model (data keywords); multi-file scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0001/spec.md`
- `TASKLIST_ROOT/artifacts/D-0001/evidence.md`

**Deliverables:**
- `src/superclaude/cli/pipeline/models.py` containing `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `SemanticCheck` dataclasses with all fields matching spec section 3.2

**Steps:**
1. **[PLANNING]** Read spec section 3.2 to identify all required fields for each dataclass; read existing `sprint/models.py` to understand current field set
2. **[PLANNING]** Identify which fields are sprint-specific (must NOT appear in pipeline models) vs generic (must appear)
3. **[EXECUTION]** Create `src/superclaude/cli/pipeline/` directory and `__init__.py` stub
4. **[EXECUTION]** Implement `models.py` with all 6 dataclasses; `Step.gate` as `Optional[GateCriteria]`; `Step.model` field for per-step override
5. **[EXECUTION]** Verify zero imports from `sprint/` or `roadmap/` in the new module
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_models.py` to validate dataclass instantiation, field defaults, and type constraints
7. **[COMPLETION]** Record evidence of NFR-006 (no sprint-specific fields) and NFR-007 (no sprint/roadmap imports)

**Acceptance Criteria:**
- File `src/superclaude/cli/pipeline/models.py` exists and exports all 6 dataclasses: `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `SemanticCheck`
- Zero imports from `superclaude.cli.sprint` or `superclaude.cli.roadmap` in any file under `src/superclaude/cli/pipeline/`
- All fields match spec section 3.2 definitions; `Step.gate` typed as `Optional[GateCriteria]`; `Step.model` field present
- Dataclass instantiation and field access verified by `tests/pipeline/test_models.py`

**Validation:**
- `uv run pytest tests/pipeline/test_models.py -v` exits 0
- Evidence: `grep -r "from superclaude.cli.sprint\|from superclaude.cli.roadmap" src/superclaude/cli/pipeline/` returns empty

**Dependencies:** None
**Rollback:** `git revert` the commit adding `pipeline/` directory
**Notes:** Critical Path Override applied due to `models/` path pattern.

---

### T01.02 -- Implement `pipeline/gates.py` with `gate_passed()` function supporting 4-tier enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | Gate validation is the core mechanism preventing pipeline advancement without conforming output; must be pure Python with no subprocess calls. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (gate criteria data); multi-file scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0002/spec.md`
- `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Deliverables:**
- `src/superclaude/cli/pipeline/gates.py` containing `gate_passed()` returning `(bool, str | None)` with EXEMPT/LIGHT/STANDARD/STRICT tier enforcement

**Steps:**
1. **[PLANNING]** Read spec section 3.2 for gate format and 4-tier enforcement rules (EXEMPT/LIGHT/STANDARD/STRICT)
2. **[PLANNING]** Identify all gate criteria fields: file existence, min_lines, frontmatter fields, semantic checks
3. **[EXECUTION]** Implement `gate_passed(step_result: StepResult, criteria: GateCriteria) -> tuple[bool, str | None]`
4. **[EXECUTION]** Implement tier-proportional validation: EXEMPT skips all checks, LIGHT checks file existence, STANDARD adds min_lines and frontmatter, STRICT adds semantic checks
5. **[EXECUTION]** Ensure failure messages match spec section 3.2 format with step name, criterion failed, actual vs expected
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_gates.py` covering all 4 tiers and edge cases (empty files, malformed YAML, missing frontmatter)
7. **[COMPLETION]** Record evidence of NFR-003 (pure Python, no subprocess)

**Acceptance Criteria:**
- `gate_passed()` in `src/superclaude/cli/pipeline/gates.py` returns `(bool, str | None)` for all 4 enforcement tiers
- No `subprocess` import in `gates.py` (NFR-003 compliance)
- Failure messages include step name, criterion failed, and actual vs expected values per spec section 3.2
- `tests/pipeline/test_gates.py` covers EXEMPT, LIGHT, STANDARD, STRICT tiers including edge cases (0-byte file, malformed YAML)

**Validation:**
- `uv run pytest tests/pipeline/test_gates.py -v` exits 0
- Evidence: `grep -r "subprocess" src/superclaude/cli/pipeline/gates.py` returns empty

**Dependencies:** T01.01 (models.py provides GateCriteria, StepResult)
**Rollback:** `git revert` the gates.py commit

---

### T01.03 -- Implement `pipeline/executor.py` with `execute_pipeline()` accepting StepRunner protocol and callbacks

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | The generic executor is the composition-via-callable core: it accepts a StepRunner and callbacks, enabling both sprint and roadmap to inject their own subprocess lifecycle. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | multi-file scope; pipeline/deploy keywords; dependency on models and gates |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0003/spec.md`
- `TASKLIST_ROOT/artifacts/D-0003/evidence.md`

**Deliverables:**
- `src/superclaude/cli/pipeline/executor.py` containing `execute_pipeline()` with `StepRunner` protocol, `on_step_start`/`on_step_complete`/`on_state_update`/`cancel_check` callbacks, sequential and parallel step group handling, per-step retry logic

**Steps:**
1. **[PLANNING]** Read spec section 13.5 for composition-via-callable design; identify StepRunner protocol signature
2. **[PLANNING]** Map callback signatures: `on_step_start(step)`, `on_step_complete(step, result)`, `on_state_update(state)`, `cancel_check() -> bool`
3. **[EXECUTION]** Define `StepRunner` as a `Protocol` class with `__call__(step: Step) -> StepResult` signature
4. **[EXECUTION]** Implement `execute_pipeline()` that iterates steps, calls StepRunner, invokes `gate_passed()` after each step, handles retry per `step.retry_limit`
5. **[EXECUTION]** Add parallel step group detection: when a step is a `list[Step]`, dispatch via `_run_parallel_steps()`
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_executor.py` with mock StepRunner verifying sequential flow, retry, and callback invocation
7. **[COMPLETION]** Document StepRunner protocol and callback contracts

**Acceptance Criteria:**
- `execute_pipeline()` in `src/superclaude/cli/pipeline/executor.py` accepts `StepRunner` protocol and all 4 callback types
- Sequential steps execute in order; parallel step groups dispatch via `_run_parallel_steps()`
- Per-step retry logic respects `step.retry_limit`; `gate_passed()` called after each step completion
- `tests/pipeline/test_executor.py` passes with mock StepRunner verifying sequential flow, retry on gate failure, and callback invocation order

**Validation:**
- `uv run pytest tests/pipeline/test_executor.py -v` exits 0
- Evidence: mock StepRunner test demonstrates callback invocation sequence

**Dependencies:** T01.01 (models), T01.02 (gates)
**Rollback:** `git revert` the executor.py commit

---

### T01.04 -- Extract `ClaudeProcess` to `pipeline/process.py` with `output_format` parameterization

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | ClaudeProcess is consumed by both sprint and roadmap; extracting it to pipeline enables shared subprocess management without duplication. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | migration keyword; breaking change potential; multi-file scope |
| Tier | STRICT |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0004/spec.md`
- `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Deliverables:**
- `src/superclaude/cli/pipeline/process.py` containing `ClaudeProcess` extracted from sprint with `output_format` parameter (default: `stream-json` for sprint backward-compat; `text` for roadmap gate-compatible output)

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/process.py` to identify the full `ClaudeProcess` class and its dependencies
2. **[PLANNING]** Identify all import paths that reference `sprint.process.ClaudeProcess` across the codebase
3. **[EXECUTION]** Copy `ClaudeProcess` class to `src/superclaude/cli/pipeline/process.py`; add `output_format: str = "stream-json"` parameter; replace all `debug_log()` calls with stdlib `logging` (NFR-007 prohibits pipeline/ from importing sprint modules)
4. **[EXECUTION]** Update `sprint/process.py` to re-export from pipeline: `from superclaude.cli.pipeline.process import ClaudeProcess`
5. **[EXECUTION]** Verify all existing import paths resolve correctly via the re-export
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_process.py` to confirm zero regression on existing sprint process tests
7. **[COMPLETION]** Record evidence of backward-compatible import path preservation

**Acceptance Criteria:**
- `ClaudeProcess` class exists in `src/superclaude/cli/pipeline/process.py` with `output_format` parameter; default `"stream-json"` preserves identical behavior to original sprint version; `"text"` produces gate-compatible plain-text output
- `ClaudeProcess(output_format="stream-json")` produces byte-identical subprocess arguments to the original sprint `ClaudeProcess`
- `pipeline/process.py` contains zero imports from `superclaude.cli.sprint` (NFR-007); all `debug_log()` calls replaced with stdlib logging or removed
- `from superclaude.cli.sprint.process import ClaudeProcess` continues to resolve correctly via re-export
- `uv run pytest tests/sprint/test_process.py` exits 0 with no test modifications
- No duplicate implementation: sprint's `process.py` contains only the re-export

**Validation:**
- `uv run pytest tests/sprint/test_process.py -v` exits 0
- `grep -r "from superclaude.cli.sprint" src/superclaude/cli/pipeline/process.py` returns empty (NFR-007)
- Evidence: `python -c "from superclaude.cli.sprint.process import ClaudeProcess; print('OK')"` prints OK

**Dependencies:** T01.01 (models for type references)
**Rollback:** `git revert` and restore original sprint/process.py

---

### T01.05 -- Implement `pipeline/_run_parallel_steps()` with threading.Thread and cross-cancellation Event

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | Parallel step execution enables concurrent generate-A/generate-B dispatch with thread-safe cross-cancellation on failure. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | performance keyword; cross-cutting scope (system-wide threading) |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0005/spec.md`
- `TASKLIST_ROOT/artifacts/D-0005/evidence.md`

**Deliverables:**
- `_run_parallel_steps()` function in `src/superclaude/cli/pipeline/executor.py` using `threading.Thread` + shared `threading.Event` for cross-cancellation with per-thread timeout via `time.monotonic()`

**Steps:**
1. **[PLANNING]** Review spec section 13.2 for threading model: `threading.Thread` + `threading.Event` for cross-cancellation
2. **[PLANNING]** Identify timeout enforcement: each thread uses `time.monotonic()` independently; `cancel_event.set()` on failure triggers sibling termination
3. **[EXECUTION]** Implement `_run_parallel_steps(steps: list[Step], runner: StepRunner, cancel_event: threading.Event) -> list[StepResult]`
4. **[EXECUTION]** Each thread: run step, check gate, set `cancel_event` on failure, return StepResult with CANCELLED status for siblings
5. **[EXECUTION]** Explicit `thread.join()` for all threads before aggregating results
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_parallel.py` with scenarios: both succeed, one fails (other cancelled), both fail, timeout
7. **[COMPLETION]** Document threading model and cross-cancellation contract

**Acceptance Criteria:**
- `_run_parallel_steps()` dispatches steps on `threading.Thread` with shared `threading.Event` for cross-cancellation
- Failed step sets `cancel_event`; sibling threads check event and return `StepStatus.CANCELLED`
- Explicit `thread.join()` before result aggregation; per-thread timeout via `time.monotonic()`
- `tests/pipeline/test_parallel.py` covers: both succeed, one fails (sibling cancelled), both fail, timeout scenarios

**Validation:**
- `uv run pytest tests/pipeline/test_parallel.py -v` exits 0
- Evidence: test output showing CANCELLED status for sibling on single failure

**Dependencies:** T01.03 (executor framework), T01.01 (models for StepResult, StepStatus)
**Rollback:** Revert parallel implementation; executor falls back to sequential-only

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.05

**Purpose:** Validate core pipeline module components (models, gates, executor, process, parallel) before proceeding to exports and tests.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-T01-T05.md`
**Verification:**
- All 5 source files exist under `src/superclaude/cli/pipeline/`
- `uv run pytest tests/pipeline/` runs without import errors
- Zero imports from `sprint/` or `roadmap/` in pipeline module

**Exit Criteria:**
- `gate_passed()` handles all 4 enforcement tiers correctly
- `execute_pipeline()` invokes StepRunner and callbacks in correct order
- `_run_parallel_steps()` cross-cancellation works with threading.Event

---

### T01.06 -- Create `pipeline/__init__.py` with public API exports

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | A clean public API surface ensures consumers import from `pipeline` directly, not internal submodules. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████░░░░] 75%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0006/spec.md`
- `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Deliverables:**
- `src/superclaude/cli/pipeline/__init__.py` exporting: `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `SemanticCheck`, `execute_pipeline`, `gate_passed`, `ClaudeProcess`

**Steps:**
1. **[PLANNING]** Enumerate all public symbols from models.py, gates.py, executor.py, process.py
2. **[PLANNING]** Verify export list matches spec D1.6 exactly
3. **[EXECUTION]** Write `__init__.py` with explicit imports and `__all__` list
4. **[EXECUTION]** Verify all 9 symbols are importable from `superclaude.cli.pipeline`
5. **[VERIFICATION]** Run `python -c "from superclaude.cli.pipeline import PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck, execute_pipeline, gate_passed, ClaudeProcess"` succeeds
6. **[COMPLETION]** Record the public API surface

**Acceptance Criteria:**
- `src/superclaude/cli/pipeline/__init__.py` exports exactly 9 symbols listed in spec D1.6
- `from superclaude.cli.pipeline import <symbol>` works for all 9 symbols
- `__all__` list matches the 9 exported names
- No additional symbols leaked into the public API

**Validation:**
- `uv run python -c "from superclaude.cli.pipeline import PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck, execute_pipeline, gate_passed, ClaudeProcess; print('OK')"` prints OK
- Evidence: `__all__` list in `__init__.py` contains exactly 9 entries

**Dependencies:** T01.01-T01.05 (all pipeline submodules must exist)
**Rollback:** Revert `__init__.py` changes

---

### T01.07 -- Create `tests/pipeline/` unit test suite covering models, gates, executor, process, and parallel

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | Unit tests validate each pipeline component independently before sprint migration or roadmap consumption. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0007/spec.md`
- `TASKLIST_ROOT/artifacts/D-0007/evidence.md`

**Deliverables:**
- `tests/pipeline/test_models.py`, `tests/pipeline/test_gates.py`, `tests/pipeline/test_executor.py`, `tests/pipeline/test_process.py`, `tests/pipeline/test_parallel.py`

**Steps:**
1. **[PLANNING]** Identify test scenarios per module: models (instantiation, defaults, field validation), gates (4 tiers, edge cases), executor (sequential, retry, callbacks), process (ClaudeProcess lifecycle), parallel (cross-cancellation, timeout)
2. **[PLANNING]** Create `tests/pipeline/__init__.py` and `conftest.py` with shared fixtures
3. **[EXECUTION]** Write `test_models.py`: dataclass instantiation, optional fields, type validation
4. **[EXECUTION]** Write `test_gates.py`: EXEMPT/LIGHT/STANDARD/STRICT tiers, empty file, malformed YAML, missing frontmatter
5. **[EXECUTION]** Write `test_executor.py`: mock StepRunner, sequential flow, retry on gate failure, callback order
6. **[EXECUTION]** Write `test_process.py`: ClaudeProcess default `output_format="stream-json"` matches sprint behavior; `output_format="text"` produces gate-compatible output
7. **[EXECUTION]** Write `test_parallel.py`: both succeed, one fail (cancel sibling), both fail, timeout
8. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -v` and confirm all tests pass
9. **[COMPLETION]** Record test count and coverage summary

**Acceptance Criteria:**
- `uv run pytest tests/pipeline/ -v` exits 0 with all 5 test files discovered and passing
- Gate tier tests cover all 4 enforcement levels with edge cases (0-byte file, malformed YAML)
- Executor tests verify sequential flow, retry logic, and callback invocation order using mock StepRunner
- Parallel tests verify cross-cancellation with CANCELLED status for sibling threads

**Validation:**
- `uv run pytest tests/pipeline/ -v` exits 0
- Evidence: test output showing all 5 test files collected and passed

**Dependencies:** T01.01-T01.06 (all pipeline modules must be complete)
**Rollback:** Delete `tests/pipeline/` directory

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm the pipeline module is complete, tested, and ready for consumption by sprint (Phase 2) and roadmap (Phase 3).
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P01-END.md`
**Verification:**
- `uv run pytest tests/pipeline/ -v` exits 0 with all test files passing
- All 9 public symbols importable from `superclaude.cli.pipeline`
- Zero imports from `sprint/` or `roadmap/` in any pipeline source file

**Exit Criteria:**
- Pipeline module provides complete public API: models, gates, executor, process, parallel dispatch
- NFR-006 (no sprint fields) and NFR-007 (no sprint/roadmap imports) verified
- All gate tiers (EXEMPT/LIGHT/STANDARD/STRICT) tested with edge cases
