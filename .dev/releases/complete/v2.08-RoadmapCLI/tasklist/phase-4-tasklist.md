# Phase 4 -- CLI Interface & UX

Implement user-facing CLI features: `--resume` with stale spec detection, `--dry-run` preview, progress display, state file management, HALT output formatting, and depth-to-prompt mapping. These features wrap the core roadmap executor built in Phase 3.

### T04.01 -- Implement `--resume` with stale spec SHA-256 detection and skip-completed-steps logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | Resume enables restarting from the first failing step without re-running completed steps; stale spec detection prevents using outdated context (FR-006, FR-029). |
| Effort | L |
| Risk | Medium |
| Risk Drivers | security keyword (SHA-256 hash verification); schema keyword (state file) |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0022/spec.md`
- `TASKLIST_ROOT/artifacts/D-0022/evidence.md`

**Deliverables:**
- `--resume` implementation in `roadmap/commands.py` and `roadmap/executor.py`: reads `.roadmap-state.json`, compares spec SHA-256 hash, skips steps whose gates pass, forces extract re-run on hash mismatch with user warning, runs from first failing step onward

**Steps:**
1. **[PLANNING]** Read spec FR-006 and FR-029 for resume behavior: state file reading, hash comparison, skip logic
2. **[PLANNING]** Identify state file schema: schema_version, spec_hash, agents, depth, per-step status with timestamps
3. **[EXECUTION]** Implement spec file SHA-256 hash computation and comparison against stored hash
4. **[EXECUTION]** Implement step-skip logic: for each step, check if output file exists and gate passes; skip if so
5. **[EXECUTION]** On hash mismatch: print warning to stderr, force extract step re-run, continue from extract onward
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_resume.py` with scenarios: clean resume (skip completed), stale spec (re-run extract), no state file (full run)
7. **[COMPLETION]** Record evidence of FR-006 and FR-029 compliance

**Acceptance Criteria:**
- `--resume` reads `.roadmap-state.json` and skips steps whose output gates pass
- Spec SHA-256 hash compared; mismatch triggers extract re-run with stderr warning
- First failing step and all subsequent steps execute normally
- `tests/roadmap/test_resume.py` covers: clean resume, stale spec, missing state file

**Validation:**
- `uv run pytest tests/roadmap/test_resume.py -v` exits 0
- Evidence: test output showing skip behavior and stale spec detection

**Dependencies:** T03.05 (executor), T04.04 (state file management)
**Rollback:** Remove resume logic; `--resume` flag becomes no-op with warning

---

### T04.02 -- Implement `--dry-run` that prints 7 step entries and exits 0 with no file writes

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Dry-run enables preview of the pipeline plan without executing subprocesses or writing files (FR-007). |
| Effort | S |
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
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0023/spec.md`
- `TASKLIST_ROOT/artifacts/D-0023/evidence.md`

**Deliverables:**
- `--dry-run` implementation: prints 7 step entries (ID, output file, gate criteria, timeout) to stdout; exits 0; no subprocess invocations; no file writes

**Steps:**
1. **[PLANNING]** Read spec FR-007 for dry-run output format: step ID, output file, gate criteria summary, timeout
2. **[PLANNING]** Identify where to intercept execution: before `execute_pipeline()` call
3. **[EXECUTION]** In `roadmap/commands.py`, check `--dry-run` flag before calling `execute_roadmap()`
4. **[EXECUTION]** Print formatted table: 7 rows (one per step), columns: Step ID, Output File, Gate Tier, Timeout
5. **[EXECUTION]** Exit with code 0 after printing; no subprocess invocations, no file writes
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_dry_run.py` using CliRunner to capture stdout and verify 7 entries, exit 0, no file creation
7. **[COMPLETION]** Record dry-run output format

**Acceptance Criteria:**
- `superclaude roadmap spec.md --dry-run` prints 7 step entries to stdout and exits 0
- Each entry includes: step ID, output file path, gate criteria tier, timeout value
- No subprocess invocations occur during dry-run
- No files written to disk during dry-run

**Validation:**
- `uv run pytest tests/roadmap/test_dry_run.py -v` exits 0
- Evidence: CliRunner output showing 7 step entries with correct format

**Dependencies:** T03.01 (CLI entry point), T03.04 (gate criteria for display)
**Rollback:** Remove dry-run check; flag becomes no-op

---

### T04.03 -- Implement progress display with 5-second update interval and parallel step visualization

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | Progress display provides real-time execution feedback to the user during pipeline runs (FR-013). |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance keyword (update interval) |
| Tier | STANDARD |
| Confidence | `[██████░░░░] 75%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0024/spec.md`
- `TASKLIST_ROOT/artifacts/D-0024/evidence.md`

**Deliverables:**
- Progress display callbacks for `execute_pipeline()`: stdout output updated every 5 seconds during step execution; parallel step display shows both steps; completion line with PASS/FAIL, attempt count, elapsed time

**Steps:**
1. **[PLANNING]** Design callback functions for `on_step_start`, `on_step_complete`, `on_state_update`
2. **[PLANNING]** Determine progress format: `[Step N/7] <step_name>... (elapsed Xs)` with 5s update
3. **[EXECUTION]** Implement `on_step_start` callback printing step name and start indicator
4. **[EXECUTION]** Implement `on_state_update` callback printing elapsed time every 5 seconds
5. **[EXECUTION]** Implement `on_step_complete` callback printing PASS/FAIL with attempt count and elapsed time
6. **[EXECUTION]** Handle parallel steps: display both step names with individual progress
7. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_executor.py -k progress` with mock executor capturing stdout output
8. **[COMPLETION]** Record progress display format

**Acceptance Criteria:**
- Progress output updates every 5 seconds during step execution with elapsed time
- Parallel step display shows both generate-A and generate-B with individual status
- Completion line includes PASS/FAIL status, attempt count (1 or 2), and elapsed time
- Progress callbacks compatible with `execute_pipeline()` callback protocol

**Validation:**
- `uv run pytest tests/roadmap/test_executor.py -k progress -v` exits 0
- Evidence: captured stdout showing progress format with 5s intervals

**Dependencies:** T03.05 (executor callbacks)
**Rollback:** Remove progress callbacks; execution runs silently

---

### T04.04 -- Implement `.roadmap-state.json` atomic write management with schema_version and per-step status

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | State file enables `--resume` by recording pipeline progress; atomic writes prevent corruption (FR-012, FR-028). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema keyword; data keyword (state persistence) |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0025 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0025/spec.md`
- `TASKLIST_ROOT/artifacts/D-0025/evidence.md`

**Deliverables:**
- `.roadmap-state.json` management module: atomic write via tmp file + `os.replace()`; updated after each step; schema includes schema_version, spec_hash, agents, depth, per-step status with timestamps

**Steps:**
1. **[PLANNING]** Read spec FR-012 and FR-028 for state file schema and atomic write requirement
2. **[PLANNING]** Define JSON schema: `{"schema_version": 1, "spec_hash": "sha256:...", "agents": [...], "depth": "...", "steps": {"step_id": {"status": "...", "started_at": "...", "completed_at": "..."}}}`
3. **[EXECUTION]** Implement `write_state(state: dict, path: Path)` using tmp file + `os.replace()` for POSIX atomicity
4. **[EXECUTION]** Implement `read_state(path: Path) -> dict | None` with graceful recovery on malformed/missing file
5. **[EXECUTION]** Hook state update into executor `on_step_complete` callback to persist after each step
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_state.py` verifying atomic write, read recovery, and per-step status tracking
7. **[COMPLETION]** Record evidence of FR-012 and FR-028 compliance

**Acceptance Criteria:**
- State file written atomically via tmp file + `os.replace()` after each step completion
- Schema includes: schema_version, spec_hash (SHA-256), agents, depth, per-step status with ISO-8601 timestamps
- `read_state()` recovers gracefully from missing, empty, or malformed state files
- `tests/roadmap/test_state.py` covers: atomic write, read valid state, read missing file, read malformed file

**Validation:**
- `uv run pytest tests/roadmap/test_state.py -v` exits 0
- Evidence: test output showing atomic write and recovery scenarios

**Dependencies:** T03.05 (executor callbacks for hooking state updates)
**Rollback:** Remove state management; `--resume` becomes unavailable
**Notes:** Risk R-005 from roadmap applies: tmp + `os.replace()` is atomic on POSIX; add graceful recovery on read.

---

### T04.05 -- Implement HALT output formatting to stderr per spec section 6.2

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | HALT output provides actionable diagnostics when pipeline fails, enabling users to understand and retry (FR-033). |
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
| Deliverable IDs | D-0026 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0026/spec.md`
- `TASKLIST_ROOT/artifacts/D-0026/evidence.md`

**Deliverables:**
- HALT output formatter producing stderr output per spec section 6.2: step name, gate failure reason, file details, completed/failed/skipped summary, retry command

**Steps:**
1. **[PLANNING]** Read spec section 6.2 for exact HALT output format
2. **[PLANNING]** Identify all data sources: step name from Step, gate reason from gate_passed(), file details from StepResult, summary from pipeline state
3. **[EXECUTION]** Implement `format_halt_output(step, gate_reason, pipeline_state) -> str` producing the spec format
4. **[EXECUTION]** Write HALT output to stderr (not stdout) to preserve stdout for machine-parseable output
5. **[EXECUTION]** Include retry command: `superclaude roadmap <spec-file> --resume`
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_executor.py -k halt_format` capturing stderr output
7. **[COMPLETION]** Record HALT output format compliance

**Acceptance Criteria:**
- HALT output written to stderr (not stdout) per spec section 6.2
- Output includes: step name, gate failure reason, file path details, completed/failed/skipped counts
- Retry command `superclaude roadmap <spec-file> --resume` included in output
- `tests/roadmap/test_executor.py -k halt_format` verifies stderr content format

**Validation:**
- `uv run pytest tests/roadmap/test_executor.py -k halt_format -v` exits 0
- Evidence: captured stderr showing spec section 6.2 compliant HALT format

**Dependencies:** T03.09 (retry-then-halt policy)
**Rollback:** Remove formatted output; HALT prints raw error message

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Validate resume, dry-run, progress, state management, and HALT formatting before depth mapping and agent routing.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-T01-T05.md`
**Verification:**
- `--resume` correctly skips completed steps and detects stale specs
- `--dry-run` prints 7 entries and exits 0 with no side effects
- State file atomic writes verified with recovery scenarios

**Exit Criteria:**
- Resume + state management integration working end-to-end
- HALT output matches spec section 6.2 format
- Progress display updates at 5-second intervals

---

### T04.06 -- Implement depth-to-prompt mapping: quick=1 round, standard=2 rounds, deep=3 rounds

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | Depth controls debate thoroughness: quick for fast iteration, deep for comprehensive adversarial review (FR-032). |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0027/spec.md`
- `TASKLIST_ROOT/artifacts/D-0027/evidence.md`

**Deliverables:**
- `_DEPTH_INSTRUCTIONS` dict in `roadmap/prompts.py` mapping depth values to round counts: `{"quick": 1, "standard": 2, "deep": 3}`; integrated into `build_debate_prompt()`

**Steps:**
1. **[PLANNING]** Read spec FR-032 for depth-to-round mapping
2. **[PLANNING]** Identify `build_debate_prompt()` injection point for round instructions
3. **[EXECUTION]** Add `_DEPTH_INSTRUCTIONS = {"quick": "Conduct 1 debate round.", "standard": "Conduct 2 debate rounds.", "deep": "Conduct 3 debate rounds with comprehensive coverage."}`
4. **[EXECUTION]** Modify `build_debate_prompt()` to embed depth-specific round instructions from `_DEPTH_INSTRUCTIONS[depth]`
5. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_prompts.py -k depth` verifying each depth value produces correct round count in prompt
6. **[COMPLETION]** Record evidence of FR-032 compliance

**Acceptance Criteria:**
- `_DEPTH_INSTRUCTIONS` dict maps quick=1, standard=2, deep=3 debate rounds
- `build_debate_prompt(depth="quick")` includes "1 round" instruction
- `build_debate_prompt(depth="deep")` includes "3 rounds" instruction
- `tests/roadmap/test_prompts.py -k depth` verifies all 3 depth values

**Validation:**
- `uv run pytest tests/roadmap/test_prompts.py -k depth -v` exits 0
- Evidence: prompt output for each depth showing correct round instructions

**Dependencies:** T03.03 (prompts.py)
**Rollback:** Remove depth integration; debate uses default 2 rounds

---

### T04.07 -- Implement `--agents` parsing of comma-separated model:persona specs and model routing to subprocess

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | Agent routing enables multi-model adversarial generation: different models produce competing roadmap variants (FR-015, FR-024). |
| Effort | M |
| Risk | Low |
| Risk Drivers | model keyword |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0028/spec.md`
- `TASKLIST_ROOT/artifacts/D-0028/evidence.md`

**Deliverables:**
- `--agents` parsing in `roadmap/commands.py`: parses comma-separated `model:persona` specs via `AgentSpec.parse()`; model value passed directly to `claude -p --model` in subprocess argv (FR-015, FR-024)

**Steps:**
1. **[PLANNING]** Read spec FR-015 and FR-024 for agent format and routing behavior
2. **[PLANNING]** Verify `AgentSpec.parse()` from T03.02 handles comma-separated input
3. **[EXECUTION]** In `commands.py`, parse `--agents` string: split on comma, call `AgentSpec.parse()` for each
4. **[EXECUTION]** Pass parsed agents to `RoadmapConfig`; executor routes model to `--model` flag in subprocess argv
5. **[EXECUTION]** Generate-A uses first agent's model; generate-B uses second agent's model
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_cli_contract.py -k agents` verifying parsing and model routing in argv
7. **[COMPLETION]** Record evidence of FR-015 and FR-024 compliance

**Acceptance Criteria:**
- `--agents "opus:architect,haiku:architect"` parsed into 2 `AgentSpec` instances
- Generate-A subprocess argv includes `--model opus`; generate-B includes `--model haiku`
- Default agents (`opus:architect,haiku:architect`) used when `--agents` not provided
- `tests/roadmap/test_cli_contract.py -k agents` verifies parsing and argv routing

**Validation:**
- `uv run pytest tests/roadmap/test_cli_contract.py -k agents -v` exits 0
- Evidence: test output showing parsed AgentSpec instances and constructed argv per agent

**Dependencies:** T03.02 (AgentSpec.parse()), T03.05 (executor model routing)
**Rollback:** Remove agent parsing; use hardcoded default agents
**Notes:** Critical Path Override applied due to `models/` pattern in model routing.

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm all CLI UX features are complete and integrated with the roadmap executor before validation testing.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P04-END.md`
**Verification:**
- `--resume` with stale spec detection and skip logic works
- `--dry-run` produces correct output format
- `--agents` parsing and model routing verified

**Exit Criteria:**
- All 7 CLI UX features implemented and individually tested
- State file management with atomic writes operational
- Depth-to-prompt and agent routing integrated into executor
