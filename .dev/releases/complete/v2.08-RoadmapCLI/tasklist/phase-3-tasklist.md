# Phase 3 -- Roadmap Command Implementation

Build the `superclaude roadmap` command on the `pipeline/` foundation. Implement the 8-step pipeline with context isolation, parallel generate steps, gate enforcement, and retry-then-halt failure policy. This is the largest phase with 10 tasks covering the core roadmap execution engine.

### T03.01 -- Create `roadmap/commands.py` Click CLI entry point with all flags registered in main.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | The CLI entry point is required for `superclaude roadmap <spec-file>` invocation with all specified flags (FR-009). |
| Effort | L |
| Risk | Medium |
| Risk Drivers | deploy/pipeline keyword (CLI registration); multi-file scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0012/spec.md`
- `TASKLIST_ROOT/artifacts/D-0012/evidence.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/commands.py` with Click command accepting `<spec-file>` positional arg and `--agents`, `--output`, `--depth`, `--resume`, `--dry-run`, `--model`, `--max-turns`, `--debug` flags; registered in `src/superclaude/cli/main.py`

**Steps:**
1. **[PLANNING]** Read spec FR-009 for complete flag specifications and defaults; read existing `sprint/commands.py` for Click pattern reference
2. **[PLANNING]** Identify main.py registration pattern for new command groups
3. **[EXECUTION]** Create `src/superclaude/cli/roadmap/` directory with `__init__.py`
4. **[EXECUTION]** Implement `commands.py` with `@click.command("roadmap")` accepting spec-file as `click.Path(exists=True)` and all 8 flags with defaults
5. **[EXECUTION]** Register roadmap command group in `src/superclaude/cli/main.py`
6. **[VERIFICATION]** Run `superclaude roadmap --help` to verify all flags appear with correct types and defaults
7. **[COMPLETION]** Record CLI help output as evidence

**Acceptance Criteria:**
- `superclaude roadmap <spec-file>` registered in main.py and accessible from CLI
- All 8 flags accepted: `--agents` (str), `--output` (path), `--depth` (choice: quick/standard/deep), `--resume` (flag), `--dry-run` (flag), `--model` (str), `--max-turns` (int), `--debug` (flag)
- `superclaude roadmap --help` displays all flags with descriptions and defaults
- Command module has no imports from `sprint/`

**Validation:**
- `uv run superclaude roadmap --help` exits 0 and lists all 8 flags
- Evidence: captured help output showing flag names, types, and defaults

**Dependencies:** T01.06 (pipeline public API for imports)
**Rollback:** Remove roadmap command registration from main.py; delete `roadmap/` directory

---

### T03.02 -- Create `roadmap/models.py` with RoadmapConfig extending PipelineConfig and AgentSpec dataclass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | RoadmapConfig holds roadmap-specific configuration; AgentSpec enables `model:persona` parsing for multi-agent dispatch. |
| Effort | M |
| Risk | Low |
| Risk Drivers | model/schema keyword |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0013/spec.md`
- `TASKLIST_ROOT/artifacts/D-0013/evidence.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/models.py` containing `RoadmapConfig` (extends `PipelineConfig` with spec_file, agents, depth, output_dir fields) and `AgentSpec` dataclass with `parse()` classmethod handling `model:persona` format; default agents: `opus:architect,haiku:architect`

**Steps:**
1. **[PLANNING]** Read spec for RoadmapConfig fields: spec_file, agents, depth, output_dir; AgentSpec.parse() format
2. **[PLANNING]** Verify PipelineConfig base class provides work_dir, steps, and other shared fields
3. **[EXECUTION]** Implement `AgentSpec` dataclass with `model: str`, `persona: str` fields and `@classmethod parse(spec: str) -> AgentSpec` handling `model:persona` format
4. **[EXECUTION]** Implement `RoadmapConfig` extending `PipelineConfig` with spec_file, agents (list[AgentSpec]), depth, output_dir
5. **[EXECUTION]** Set default agents to `[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")]`
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_models.py` verifying AgentSpec.parse() and RoadmapConfig instantiation
7. **[COMPLETION]** Record evidence of correct inheritance and default values

**Acceptance Criteria:**
- `AgentSpec.parse("opus:architect")` returns `AgentSpec(model="opus", persona="architect")`
- `RoadmapConfig` extends `PipelineConfig` with spec_file, agents, depth, output_dir fields
- Default agents are `opus:architect,haiku:architect`
- `tests/roadmap/test_models.py` validates parsing and config instantiation

**Validation:**
- `uv run pytest tests/roadmap/test_models.py -v` exits 0
- Evidence: test output showing AgentSpec.parse() with various input formats

**Dependencies:** T01.01 (PipelineConfig)
**Rollback:** Delete `roadmap/models.py`
**Notes:** Critical Path Override applied due to `models/` path pattern.

---

### T03.03 -- Implement `roadmap/prompts.py` with 7 prompt builder pure functions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Prompt builders generate the exact prompts passed to Claude subprocesses per pipeline step; must be pure functions with no I/O (NFR-004). |
| Effort | M |
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
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0014/spec.md`
- `TASKLIST_ROOT/artifacts/D-0014/evidence.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/prompts.py` containing 7 pure functions: `build_extract_prompt()`, `build_generate_prompt()`, `build_diff_prompt()`, `build_debate_prompt()`, `build_score_prompt()`, `build_merge_prompt()`, `build_test_strategy_prompt()`; all return `str`; no I/O

**Steps:**
1. **[PLANNING]** Read spec section 4 for each step's prompt requirements and expected output format
2. **[PLANNING]** Identify inputs for each prompt builder: spec text, previous step outputs, depth configuration
3. **[EXECUTION]** Implement all 7 functions as pure `str`-returning functions with no file I/O, no subprocess calls
4. **[EXECUTION]** `build_debate_prompt()` embeds depth-dependent round instructions via `_DEPTH_INSTRUCTIONS` dict
5. **[EXECUTION]** Each function includes structured output format instructions matching gate criteria expectations
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_prompts.py` verifying each function returns non-empty str, contains expected keywords, and has no I/O side effects
7. **[COMPLETION]** Record evidence of NFR-004 (pure functions, no I/O)

**Acceptance Criteria:**
- All 7 functions in `roadmap/prompts.py` return `str` with no file I/O or subprocess calls
- `build_debate_prompt()` includes depth-dependent round instructions (quick=1, standard=2, deep=3)
- Each prompt includes structured output format instructions matching its corresponding gate criteria
- `tests/roadmap/test_prompts.py` verifies all 7 functions produce non-empty, well-structured prompts

**Validation:**
- `uv run pytest tests/roadmap/test_prompts.py -v` exits 0
- Evidence: `grep -r "open(\|subprocess\|os.path" src/superclaude/cli/roadmap/prompts.py` returns empty (NFR-004)

**Dependencies:** T03.02 (RoadmapConfig for depth field reference)
**Rollback:** Delete `roadmap/prompts.py`

---

### T03.04 -- Create `roadmap/gates.py` with 7 GateCriteria instances matching spec section 4 step definitions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Gate criteria data definitions drive tier-proportional validation for each pipeline step; must be separated from gate logic (NFR-005). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema keyword (gate criteria as data); multi-file scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0015/spec.md`
- `TASKLIST_ROOT/artifacts/D-0015/evidence.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/gates.py` containing 7 `GateCriteria` instances as module-level constants with correct enforcement tiers (STRICT for generate/debate/merge, STANDARD for others), frontmatter fields, and min_lines per step

**Steps:**
1. **[PLANNING]** Read spec section 4 to extract gate criteria per step: enforcement tier, required frontmatter fields, min_lines, semantic checks
2. **[PLANNING]** Categorize: generate-A, generate-B, debate, merge get STRICT tier; extract, diff, score, test-strategy get STANDARD
3. **[EXECUTION]** Define 7 `GateCriteria` instances: `EXTRACT_GATE`, `GENERATE_A_GATE`, `GENERATE_B_GATE`, `DIFF_GATE`, `DEBATE_GATE`, `SCORE_GATE`, `MERGE_GATE`, `TEST_STRATEGY_GATE`
4. **[EXECUTION]** Set frontmatter fields, min_lines, semantic checks per spec; STRICT gates include semantic check definitions
5. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_gates_data.py` verifying tier assignments, frontmatter fields, and min_lines values
6. **[COMPLETION]** Record evidence of NFR-005 (gate data separation from logic)

**Acceptance Criteria:**
- 7 `GateCriteria` instances defined as module-level constants in `roadmap/gates.py`
- Generate and debate/merge steps use STRICT tier; extract, diff, score, test-strategy use STANDARD tier
- Each gate specifies correct frontmatter fields and min_lines matching spec section 4
- Gate data is pure data (no logic, no imports from `pipeline/gates.py` enforcement code)

**Validation:**
- `uv run pytest tests/roadmap/test_gates_data.py -v` exits 0
- Evidence: test output confirming tier assignments and field values per gate

**Dependencies:** T01.01 (GateCriteria dataclass from pipeline models)
**Rollback:** Delete `roadmap/gates.py`

---

### T03.05 -- Implement `roadmap/executor.py` with `execute_roadmap()` wrapping `execute_pipeline()`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | The roadmap executor builds the step list, defines `roadmap_run_step` as the StepRunner, and delegates to the generic pipeline executor. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | pipeline keyword; multi-file scope; dependency on pipeline executor |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0016/spec.md`
- `TASKLIST_ROOT/artifacts/D-0016/evidence.md`

**Deliverables:**
- `src/superclaude/cli/roadmap/executor.py` containing `execute_roadmap(config: RoadmapConfig)` that builds step list with parallel generate group, defines `roadmap_run_step` building subprocess argv per spec section 13.3, and calls `execute_pipeline()`

**Steps:**
1. **[PLANNING]** Read spec section 13.3 for subprocess argv format: `claude -p <prompt> --file <input> --model <model>`
2. **[PLANNING]** Map 8 pipeline steps to Step instances; group generate-A and generate-B as parallel `list[Step]`
3. **[EXECUTION]** Implement `roadmap_run_step(step: Step) -> StepResult` building subprocess argv with `--file` injection for inputs and per-step model override for generate steps
4. **[EXECUTION]** Build step list: extract, [generate-A, generate-B] (parallel), diff, debate, score, merge, test-strategy
5. **[EXECUTION]** Call `execute_pipeline(steps, roadmap_run_step, callbacks)` with appropriate callbacks
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_executor.py` with mock subprocess verifying step ordering, parallel group, and argv construction
7. **[COMPLETION]** Document subprocess argv format and parallel group structure

**Acceptance Criteria:**
- `execute_roadmap()` builds 8-step pipeline with generate-A/generate-B as parallel group
- `roadmap_run_step` constructs subprocess argv with `--file` for inputs and `--model` for per-step override
- Delegates to `execute_pipeline()` from pipeline module (no reimplementation of sequencing logic)
- `tests/roadmap/test_executor.py` verifies step ordering, parallel group detection, and argv construction with mock subprocess

**Validation:**
- `uv run pytest tests/roadmap/test_executor.py -v` exits 0
- Evidence: test output showing constructed argv for each step

**Dependencies:** T01.03 (execute_pipeline), T03.02 (RoadmapConfig), T03.03 (prompts), T03.04 (gate criteria)
**Rollback:** Delete `roadmap/executor.py`

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.05

**Purpose:** Validate roadmap command structure, models, prompts, gates, and executor before proceeding to parallel execution and policy implementation.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-T01-T05.md`
**Verification:**
- `superclaude roadmap --help` displays all flags
- All 7 prompt builders return non-empty strings
- `execute_roadmap()` builds correct step list with parallel generate group

**Exit Criteria:**
- CLI entry point registered and accessible
- Gate criteria match spec section 4 tier assignments
- Executor delegates to pipeline `execute_pipeline()` correctly

---

### T03.06 -- Implement parallel generate-A/generate-B step execution with cross-cancellation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | Generate steps A and B run concurrently via separate Claude subprocesses; cross-cancellation ensures failure of one triggers CANCELLED status for the other. |
| Effort | M |
| Risk | High |
| Risk Drivers | performance keyword; system-wide threading; cross-cutting scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0017/spec.md`
- `TASKLIST_ROOT/artifacts/D-0017/evidence.md`

**Deliverables:**
- Parallel generate dispatch in `roadmap/executor.py`: Steps generate-A and generate-B as `list[Step]` passed to `execute_pipeline()`; cross-cancellation on failure; CANCELLED status for sibling when one fails

**Steps:**
1. **[PLANNING]** Review T01.05 `_run_parallel_steps()` API to understand threading contract
2. **[PLANNING]** Identify generate-A and generate-B step configurations: different model assignments per agent spec
3. **[EXECUTION]** Configure generate-A and generate-B as `list[Step]` in the step list with per-agent model override
4. **[EXECUTION]** Verify cross-cancellation: when generate-A subprocess fails, generate-B receives CANCELLED status (and vice versa)
5. **[EXECUTION]** Ensure explicit `thread.join()` before checking gate results for both generate outputs
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_parallel.py` with mock subprocesses: both succeed, A fails (B cancelled), B fails (A cancelled), both fail
7. **[COMPLETION]** Record evidence of cross-cancellation behavior with CANCELLED status

**Acceptance Criteria:**
- Generate-A and generate-B configured as parallel `list[Step]` in executor step list
- Per-agent model override applied: generate-A uses first agent's model, generate-B uses second agent's model
- Cross-cancellation produces CANCELLED StepStatus for sibling on failure
- `tests/roadmap/test_parallel.py` covers all 4 scenarios: both succeed, A fail, B fail, both fail

**Validation:**
- `uv run pytest tests/roadmap/test_parallel.py -v` exits 0
- Evidence: test output showing CANCELLED status assignment on single failure

**Dependencies:** T01.05 (parallel dispatch), T03.05 (executor with step list)
**Rollback:** Convert parallel generate to sequential execution (degraded but functional)
**Notes:** Risk R-003 from roadmap applies: `threading.Event` is thread-safe; independent per-thread timeouts; explicit `join()` before result aggregation.

---

### T03.07 -- Implement context isolation: each subprocess receives only step prompt and --file inputs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Context isolation prevents information leakage between pipeline steps; each subprocess must be a fresh Claude invocation with no shared session (FR-003, FR-023). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | security keyword (isolation); session keyword (no shared session) |
| Tier | STRICT |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0018/spec.md`
- `TASKLIST_ROOT/artifacts/D-0018/evidence.md`

**Deliverables:**
- Context isolation enforcement in `roadmap_run_step`: subprocess argv contains only `step.prompt` + `--file <input>` per input; no `--continue`, no session ID, no shared memory between steps

**Steps:**
1. **[PLANNING]** Read spec FR-003 and FR-023 for context isolation requirements
2. **[PLANNING]** Audit `roadmap_run_step` argv construction to identify any session-sharing flags
3. **[EXECUTION]** Ensure argv construction in `roadmap_run_step` uses only: `claude`, `-p`, `<prompt>`, `--file`, `<input_path>`, `--model`, `<model>`
4. **[EXECUTION]** Add explicit assertion/guard: no `--continue`, `--session`, `--resume` flags in constructed argv
5. **[EXECUTION]** Verify each step starts a fresh subprocess with no environment variable session leakage
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_executor.py -k context_isolation` verifying argv contains no session flags
7. **[COMPLETION]** Record evidence of FR-003 and FR-023 compliance

**Acceptance Criteria:**
- `roadmap_run_step` argv contains only `claude -p <prompt> --file <input> --model <model>` (no session flags)
- No `--continue`, `--session`, or `--resume` flags present in any constructed argv
- Each subprocess invocation is a fresh process with no shared environment state
- Test case explicitly verifies absence of session-sharing flags in constructed argv

**Validation:**
- `uv run pytest tests/roadmap/test_executor.py -k context_isolation -v` exits 0
- Evidence: test output showing constructed argv is session-flag-free

**Dependencies:** T03.05 (executor with roadmap_run_step)
**Rollback:** No rollback needed (additive enforcement)

---

### T03.08 -- Integrate gate enforcement: call gate_passed() after each subprocess with tier-proportional validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | Gate enforcement is the core determinism mechanism: steps cannot advance without gate-passing output files. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | pipeline keyword; multi-file scope |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0019/spec.md`
- `TASKLIST_ROOT/artifacts/D-0019/evidence.md`

**Deliverables:**
- Gate enforcement integration in roadmap executor: `gate_passed()` called after each subprocess completion with tier-proportional validation; human-readable failure messages; retry on gate failure per step retry_limit

**Steps:**
1. **[PLANNING]** Map each roadmap step to its GateCriteria instance from `roadmap/gates.py`
2. **[PLANNING]** Verify pipeline executor already calls `gate_passed()` or identify where to integrate
3. **[EXECUTION]** Ensure `execute_pipeline()` calls `gate_passed(step_result, step.gate)` after each step completion
4. **[EXECUTION]** Verify human-readable failure messages propagate from `gate_passed()` to executor callbacks
5. **[EXECUTION]** Confirm retry logic: on gate failure, re-run step (same prompt, fresh subprocess) up to `step.retry_limit`
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_executor.py -k gate_enforcement` verifying gate called after each step and retry on failure
7. **[COMPLETION]** Record evidence of tier-proportional gate enforcement

**Acceptance Criteria:**
- `gate_passed()` called after every subprocess completion in the pipeline execution flow
- STRICT gates validate semantic checks; STANDARD gates validate file existence, min_lines, frontmatter
- Human-readable failure messages include step name, criterion failed, actual vs expected
- Retry on gate failure re-executes with fresh subprocess up to `step.retry_limit`

**Validation:**
- `uv run pytest tests/roadmap/test_executor.py -k gate_enforcement -v` exits 0
- Evidence: test output showing gate called per step and retry triggered on failure

**Dependencies:** T01.02 (gate_passed), T03.04 (gate criteria data), T03.05 (executor)
**Rollback:** Disable gate enforcement (steps run without validation -- degraded mode)

---

### T03.09 -- Implement retry-then-halt failure policy with diagnostic output per spec section 6.2

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | The failure policy ensures deterministic behavior on gate failure: retry once with fresh subprocess, then HALT with actionable diagnostic output. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | pipeline keyword; performance keyword (retry logic) |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0020/spec.md`
- `TASKLIST_ROOT/artifacts/D-0020/evidence.md`

**Deliverables:**
- Retry-then-halt policy in roadmap executor: on gate failure, retry once (same prompt, fresh subprocess); on second failure, HALT with diagnostic output per spec section 6.2 format

**Steps:**
1. **[PLANNING]** Read spec section 6.2 for HALT diagnostic output format: step name, gate failure reason, file details, completed/failed/skipped summary, retry command
2. **[PLANNING]** Verify pipeline executor retry logic handles retry_limit=1 correctly
3. **[EXECUTION]** Configure all roadmap steps with `retry_limit=1` (retry once on gate failure)
4. **[EXECUTION]** Implement HALT output formatter producing spec section 6.2 format on second failure
5. **[EXECUTION]** Ensure remaining steps after HALT receive SKIPPED status
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_executor.py -k retry_halt` verifying retry-then-halt sequence
7. **[COMPLETION]** Record evidence of HALT output format compliance

**Acceptance Criteria:**
- On first gate failure: step retried with same prompt and fresh subprocess
- On second gate failure: pipeline HALTs; no further steps execute
- HALT output includes: step name, gate failure reason, file details, completed/failed/skipped count, retry command
- Remaining steps after HALT receive SKIPPED status in results

**Validation:**
- `uv run pytest tests/roadmap/test_executor.py -k retry_halt -v` exits 0
- Evidence: test output showing retry attempt followed by HALT with diagnostic message

**Dependencies:** T03.08 (gate enforcement), T03.05 (executor)
**Rollback:** Remove retry logic; steps fail immediately on gate failure (stricter but functional)

---

### Checkpoint: Phase 3 / Tasks T03.06-T03.10

**Purpose:** Validate parallel execution, context isolation, gate enforcement, and failure policy before CLI UX integration.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-T06-T10.md`
**Verification:**
- Parallel generate cross-cancellation works correctly
- Context isolation enforced (no session flags in argv)
- Retry-then-halt policy produces spec-compliant diagnostic output

**Exit Criteria:**
- All 8 pipeline steps executable with correct gate enforcement
- Parallel generate dispatch with cross-cancellation tested
- HALT diagnostic output matches spec section 6.2 format

---

### T03.10 -- Implement semantic checks for STRICT-tier steps: merge, generate, and debate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Semantic checks for STRICT-tier steps validate structural quality beyond basic file/frontmatter checks: heading gaps, cross-references, duplicate headings, actionable content, convergence scores. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema keyword (semantic validation rules); multi-file scope |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0021/spec.md`
- `TASKLIST_ROOT/artifacts/D-0021/evidence.md`

**Deliverables:**
- Semantic check implementations: merge (`no_heading_gaps`, `cross_refs_resolve`, `no_duplicate_headings`), generate (`frontmatter_values_non_empty`, `has_actionable_content`), debate (`convergence_score_valid`); integrated into GateCriteria SemanticCheck definitions

**Steps:**
1. **[PLANNING]** Read spec for semantic check definitions per STRICT step
2. **[PLANNING]** Design check functions as pure functions accepting file content and returning `(bool, str | None)`
3. **[EXECUTION]** Implement `no_heading_gaps(content)`: verify heading levels increment by 1 (no `#` to `###` skip)
4. **[EXECUTION]** Implement `cross_refs_resolve(content)`: verify all internal `[ref]` links have matching anchors
5. **[EXECUTION]** Implement `no_duplicate_headings(content)`, `frontmatter_values_non_empty(content)`, `has_actionable_content(content)`, `convergence_score_valid(content)`
6. **[EXECUTION]** Register semantic checks in corresponding GateCriteria instances in `roadmap/gates.py`
7. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_gates_data.py -k semantic` with passing and failing content samples
8. **[COMPLETION]** Record evidence of semantic check coverage per STRICT step

**Acceptance Criteria:**
- 6 semantic check functions implemented as pure functions returning `(bool, str | None)`
- Merge gate includes: `no_heading_gaps`, `cross_refs_resolve`, `no_duplicate_headings`
- Generate gates include: `frontmatter_values_non_empty`, `has_actionable_content`
- Debate gate includes: `convergence_score_valid`

**Validation:**
- `uv run pytest tests/roadmap/test_gates_data.py -k semantic -v` exits 0
- Evidence: test output with passing and deliberately failing content samples per check

**Dependencies:** T03.04 (gate criteria data), T01.02 (gate_passed SemanticCheck integration)
**Rollback:** Remove semantic checks; STRICT gates fall back to STANDARD-level validation

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm roadmap command implementation is complete and ready for CLI UX features in Phase 4.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P03-END.md`
**Verification:**
- All 10 tasks complete; `superclaude roadmap --help` works
- 8-step pipeline builds correctly with parallel generate group
- Gate enforcement, retry-then-halt, and semantic checks all functional

**Exit Criteria:**
- `execute_roadmap()` runs full 8-step pipeline with gate enforcement
- Context isolation verified (no session flags)
- Semantic checks integrated for all STRICT-tier steps
