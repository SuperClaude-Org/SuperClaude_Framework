# Phase 2 -- Process Duplication Elimination

Eliminate ~94 lines of duplicated process method overrides in sprint via lifecycle hooks in the pipeline base class, and remove confirmed dead code from roadmap executor. Split into 3 independent sub-steps (M2a: wait deletion, M2b: hook migration, M2c: dead code removal) to minimize blast radius per commit.

### T02.01 -- Delete sprint's wait() override from sprint/process.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | Sprint's wait() override is a pure no-op duplication of the pipeline base class implementation; removing it reduces maintenance surface with zero behavioral change. |
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
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0005/evidence.md

**Deliverables:**
- sprint/process.py with wait() override removed; all existing tests pass unchanged

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/process.py` and identify the wait() method override
2. **[PLANNING]** Confirm wait() override is a no-op duplication by comparing with pipeline base class wait()
3. **[EXECUTION]** Delete the wait() method definition from sprint/process.py
4. **[EXECUTION]** Run `uv run pytest tests/sprint/ -v` to confirm no behavioral change
5. **[VERIFICATION]** Run `uv run pytest -v` (full suite) to confirm zero regressions
6. **[COMPLETION]** Record test output and diff in TASKLIST_ROOT/artifacts/D-0005/evidence.md

**Acceptance Criteria:**
- `sprint/process.py` no longer defines a wait() method (verified by `grep -n "def wait" src/superclaude/cli/sprint/process.py` returning 0 results)
- `uv run pytest tests/sprint/ -v` exits 0 with all existing tests passing unchanged
- No behavioral change in sprint execution (characterization tests from Phase 1 still pass)
- Change committed as isolated commit for minimal blast radius

**Validation:**
- `uv run pytest -v`
- Evidence: `grep -n "def wait" src/superclaude/cli/sprint/process.py` output + full test log in TASKLIST_ROOT/artifacts/D-0005/evidence.md

**Dependencies:** T01.01, T01.02, T01.03, T01.04 (all Phase 1 characterization tests must pass)
**Rollback:** `git revert` the commit that removed wait()
**Notes:** M2a sub-step; pure deletion with no replacement logic needed.

---

### T02.02 -- Add on_spawn, on_signal, on_exit hook params to pipeline ClaudeProcess.__init__

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Lifecycle hooks enable sprint to inject behavior without overriding start()/terminate()/wait(), eliminating process method duplication while preserving NFR-007 (no cross-module imports). |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0006/spec.md
- TASKLIST_ROOT/artifacts/D-0006/evidence.md

**Deliverables:**
- 3 new optional params (on_spawn, on_signal, on_exit) with None defaults in pipeline ClaudeProcess.__init__; hook call sites in start(), terminate(), wait(); unit tests in tests/pipeline/test_process_hooks.py

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/pipeline/process.py` ClaudeProcess.__init__ signature and start()/terminate()/wait() methods
2. **[PLANNING]** Design hook signatures: on_spawn(pid), on_signal(pid, signal), on_exit(pid, returncode)
3. **[EXECUTION]** Add on_spawn, on_signal, on_exit optional params (default=None) to ClaudeProcess.__init__; store as instance attributes
4. **[EXECUTION]** Add hook call sites: on_spawn in start() after process creation, on_signal in terminate() before signal send, on_exit in wait() before _close_handles()
5. **[EXECUTION]** Create `tests/pipeline/test_process_hooks.py` with tests verifying each hook fires with correct arguments
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_process_hooks.py -v` and `uv run pytest -v` for full regression check
7. **[COMPLETION]** Record hook API spec in TASKLIST_ROOT/artifacts/D-0006/spec.md and test output in TASKLIST_ROOT/artifacts/D-0006/evidence.md

**Acceptance Criteria:**
- `tests/pipeline/test_process_hooks.py` exists and all tests pass via `uv run pytest tests/pipeline/test_process_hooks.py -v`
- ClaudeProcess.__init__ accepts on_spawn, on_signal, on_exit with None defaults (no breaking change to existing callers)
- Hook call sites present in start(), terminate(), and wait() methods (verified by reading source)
- Full test suite passes with zero regressions: `uv run pytest -v` exits 0

**Validation:**
- `uv run pytest tests/pipeline/test_process_hooks.py -v`
- Evidence: hook API spec + test output in TASKLIST_ROOT/artifacts/D-0006/evidence.md

**Dependencies:** T02.01
**Rollback:** Revert commit adding hook params; existing callers unaffected due to None defaults
**Notes:** Tier conflict: "refactor" (STRICT) present in roadmap context for this deliverable; resolved to STRICT by priority rule. Hook contract: hooks must not raise; hooks receive primitives only (per R-005 risk mitigation).

---

### T02.03 -- Add on_exit hook call to wait() success path

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | The on_exit hook must fire on both normal wait() completion and terminate()-initiated exit to ensure sprint can log process lifecycle events consistently. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [███████░░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0007/spec.md
- TASKLIST_ROOT/artifacts/D-0007/evidence.md

**Deliverables:**
- wait() calls on_exit(pid, returncode) before _close_handles() on normal exit; unit test confirms hook fires on both wait() and terminate() paths

**Steps:**
1. **[PLANNING]** Read pipeline ClaudeProcess.wait() to identify the success path before _close_handles()
2. **[PLANNING]** Identify the terminate() path to ensure on_exit also fires there (or document if already covered by T02.02)
3. **[EXECUTION]** Add on_exit(self._process.pid, returncode) call in wait() immediately before _close_handles() on normal exit
4. **[EXECUTION]** Add unit test in `tests/pipeline/test_process_hooks.py` verifying on_exit fires with (pid, returncode) on both wait() and terminate() paths
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/test_process_hooks.py -v` and full suite
6. **[COMPLETION]** Document on_exit call placement in TASKLIST_ROOT/artifacts/D-0007/spec.md

**Acceptance Criteria:**
- `uv run pytest tests/pipeline/test_process_hooks.py -v` includes tests for on_exit on both wait() and terminate() paths, all passing
- on_exit(pid, returncode) called before _close_handles() on normal wait() completion (verified by reading source)
- on_exit fires with correct (pid, returncode) tuple on both code paths (verified by mock assertions in test)
- Full test suite passes: `uv run pytest -v` exits 0

**Validation:**
- `uv run pytest tests/pipeline/test_process_hooks.py -v`
- Evidence: test output in TASKLIST_ROOT/artifacts/D-0007/evidence.md

**Dependencies:** T02.02
**Rollback:** Revert on_exit call addition; hooks are no-op when None
**Notes:** Confidence 75% due to ambiguity on whether terminate() path on_exit was fully addressed in T02.02; implementation may merge with T02.02 hook call sites.

---

### T02.04 -- Add hook factory functions to sprint/process.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | Hook factories (_make_spawn_hook, _make_signal_hook, _make_exit_hook) encapsulate sprint-specific debug_log calls as closures, keeping sprint/process.py self-contained without importing pipeline internals. |
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
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0008/evidence.md

**Deliverables:**
- 3 factory functions in sprint/process.py: _make_spawn_hook, _make_signal_hook, _make_exit_hook; each captures phase/config context and produces closures calling debug_log with correct event names and kwargs

**Steps:**
1. **[PLANNING]** Read existing sprint/process.py start() and terminate() overrides to extract debug_log call patterns and event names
2. **[PLANNING]** Identify phase and config context variables that closures must capture
3. **[EXECUTION]** Implement _make_spawn_hook(phase, config) returning closure that calls debug_log with spawn event
4. **[EXECUTION]** Implement _make_signal_hook(phase, config) and _make_exit_hook(phase, config) following same pattern
5. **[EXECUTION]** Add unit tests verifying each factory returns a callable that invokes debug_log with expected event name and kwargs
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -v` to confirm factories work correctly
7. **[COMPLETION]** Record factory signatures and test output in TASKLIST_ROOT/artifacts/D-0008/evidence.md

**Acceptance Criteria:**
- `grep -n "_make_spawn_hook\|_make_signal_hook\|_make_exit_hook" src/superclaude/cli/sprint/process.py` returns 3 function definitions
- Each factory captures phase/config context and produces a closure calling debug_log with correct event names
- Unit tests verify factory output closures invoke debug_log with expected arguments
- No imports from pipeline module added to sprint/process.py (NFR-007 preserved)

**Validation:**
- `uv run pytest tests/sprint/ -v`
- Evidence: factory signatures + test output in TASKLIST_ROOT/artifacts/D-0008/evidence.md

**Dependencies:** T02.02, T02.03
**Rollback:** Delete factory functions; sprint/process.py reverts to pre-factory state
**Notes:** —

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.05

**Purpose:** Verify hook infrastructure (base class hooks + factory functions) is complete and all characterization tests still pass before wiring hooks and deleting overrides.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P02-T01-T05.md
**Verification:**
- `uv run pytest tests/pipeline/test_process_hooks.py -v` passes (hook infrastructure tests)
- `uv run pytest tests/sprint/ -v` passes (all characterization + factory tests)
- `uv run pytest -v` passes (full suite, zero regressions)
**Exit Criteria:**
- Hook params (on_spawn, on_signal, on_exit) present in pipeline ClaudeProcess.__init__
- Factory functions (_make_spawn_hook, _make_signal_hook, _make_exit_hook) present in sprint/process.py
- No cross-module imports between sprint and pipeline (NFR-007)

---

### T02.05 -- Wire hooks in sprint ClaudeProcess.__init__ and delete start()/terminate() overrides

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | This is the core refactoring step: sprint ClaudeProcess wires hook factories in __init__ and removes start()/terminate() overrides, eliminating ~58 lines of duplication while preserving identical runtime behavior. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (override deletion changes class interface) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0009/spec.md
- TASKLIST_ROOT/artifacts/D-0009/evidence.md

**Deliverables:**
- Sprint ClaudeProcess defines only __init__ and build_prompt; start() and terminate() overrides deleted; all Phase 1 characterization tests pass before AND after the change

**Steps:**
1. **[PLANNING]** Read sprint ClaudeProcess.__init__, start(), terminate(), and build_prompt to map all override logic
2. **[PLANNING]** Run `uv run pytest tests/sprint/ -v` to capture baseline (all characterization tests pass BEFORE change)
3. **[EXECUTION]** Modify sprint ClaudeProcess.__init__ to wire hook factories: on_spawn=_make_spawn_hook(...), on_signal=_make_signal_hook(...), on_exit=_make_exit_hook(...)
4. **[EXECUTION]** Delete start() and terminate() method overrides from sprint ClaudeProcess
5. **[EXECUTION]** Run `uv run pytest tests/sprint/ -v` to confirm characterization tests pass AFTER change
6. **[VERIFICATION]** Run `uv run pytest -v` (full suite) to confirm zero regressions; compare before/after test counts
7. **[COMPLETION]** Record before/after diff and test output in TASKLIST_ROOT/artifacts/D-0009/evidence.md

**Acceptance Criteria:**
- `grep -n "def start\|def terminate" src/superclaude/cli/sprint/process.py` returns 0 results (overrides deleted)
- Sprint ClaudeProcess defines only __init__ and build_prompt (verified by reading class definition)
- All Phase 1 characterization tests pass both before AND after the change (before/after test output recorded)
- `uv run pytest -v` exits 0 with zero regressions

**Validation:**
- `uv run pytest -v`
- Evidence: before/after diff + test logs in TASKLIST_ROOT/artifacts/D-0009/evidence.md

**Dependencies:** T02.04 (factory functions must exist before wiring)
**Rollback:** `git revert` the wiring commit; restore start()/terminate() overrides
**Notes:** Tier conflict: "restructure" (STRICT) vs "delete" (STANDARD) -> resolved to STRICT by priority rule. Highest-risk task in Phase 2; R-001 mitigation (characterization tests) is the safety net.

---

### T02.06 -- Verify NFR-007 compliance (zero cross-module imports)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | NFR-007 requires no cross-module imports between sprint and roadmap in the pipeline package; this verification confirms the hook migration did not introduce violations. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0010/evidence.md

**Deliverables:**
- Grep verification output confirming `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 results

**Steps:**
1. **[PLANNING]** Identify the NFR-007 compliance command from roadmap: `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/`
2. **[PLANNING]** Confirm command scope covers all pipeline module files
3. **[EXECUTION]** Run `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/`
4. **[EXECUTION]** Record output (expected: empty / exit code 1 for no matches)
5. **[VERIFICATION]** Confirm 0 results returned
6. **[COMPLETION]** Record grep output in TASKLIST_ROOT/artifacts/D-0010/evidence.md

**Acceptance Criteria:**
- `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 results
- No cross-module imports exist between sprint/roadmap in pipeline package
- Verification is read-only (no code changes in this task)
- Grep output recorded as evidence

**Validation:**
- `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/`
- Evidence: grep output in TASKLIST_ROOT/artifacts/D-0010/evidence.md

**Dependencies:** T02.05
**Rollback:** N/A (read-only verification)
**Notes:** Read-only verification task; classified EXEMPT per read-only operation context booster (+0.4).

---

### T02.07 -- Delete _FORBIDDEN_FLAGS and _build_subprocess_argv from roadmap/executor.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | _FORBIDDEN_FLAGS and _build_subprocess_argv are confirmed dead code in roadmap/executor.py with zero call sites; removing them reduces maintenance surface. |
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
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- TASKLIST_ROOT/artifacts/D-0011/evidence.md

**Deliverables:**
- roadmap/executor.py with _FORBIDDEN_FLAGS constant and _build_subprocess_argv function deleted; grep verification confirming zero remaining references

**Steps:**
1. **[PLANNING]** Run `grep -rn "_build_subprocess_argv" src/` and `grep -rn "_FORBIDDEN_FLAGS" src/` to confirm zero call sites before deletion
2. **[PLANNING]** Read roadmap/executor.py to locate _FORBIDDEN_FLAGS and _build_subprocess_argv definitions
3. **[EXECUTION]** Delete _FORBIDDEN_FLAGS constant definition from roadmap/executor.py
4. **[EXECUTION]** Delete _build_subprocess_argv function definition from roadmap/executor.py
5. **[VERIFICATION]** Run `grep -rn "_build_subprocess_argv" src/` and `grep -rn "_FORBIDDEN_FLAGS" src/` to confirm 0 results; run `uv run pytest -v` for full regression check
6. **[COMPLETION]** Record grep output and test results in TASKLIST_ROOT/artifacts/D-0011/evidence.md

**Acceptance Criteria:**
- `grep -rn "_build_subprocess_argv" src/` returns 0 results
- `grep -rn "_FORBIDDEN_FLAGS" src/` returns 0 results
- `uv run pytest -v` exits 0 with all tests passing
- Dead code removal committed as isolated commit

**Validation:**
- `grep -rn "_build_subprocess_argv\|_FORBIDDEN_FLAGS" src/`
- Evidence: grep output + test log in TASKLIST_ROOT/artifacts/D-0011/evidence.md

**Dependencies:** T02.05 (dead code removal after hook migration cleans up roadmap/executor.py)
**Rollback:** `git revert` the deletion commit
**Notes:** M2c sub-step; confirmed zero call sites per roadmap risk assessment R-002.

---

### Checkpoint: End of Phase 2

**Purpose:** Verify all process duplication has been eliminated, dead code removed, and zero regressions across the full test suite.
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/CP-P02-END.md
**Verification:**
- `uv run pytest -v` exits 0 with all tests passing (full suite)
- `grep -n "def start\|def terminate\|def wait" src/superclaude/cli/sprint/process.py` returns only __init__ and build_prompt
- `grep -r "from.*sprint\|from.*roadmap" src/superclaude/cli/pipeline/` returns 0 results (NFR-007)
**Exit Criteria:**
- Sprint ClaudeProcess defines only __init__ and build_prompt (overrides deleted)
- _FORBIDDEN_FLAGS and _build_subprocess_argv removed from roadmap/executor.py
- All Phase 1 characterization tests still pass after refactoring
