# Phase 2 -- Sprint Migration to Pipeline

Migrate `sprint/` to consume the `pipeline/` module for `ClaudeProcess`, `PipelineConfig`, and related types. Sprint's external CLI API must remain identical (NFR-001). All sprint test files passing at extraction start must continue to pass with no sprint test modifications during pipeline/ migration (NFR-002). Note: v2.07 modified 9 of the original 14 test files; the baseline is the post-v2.07 state.

### T02.01 -- Modify `sprint/config.py` so SprintConfig inherits from PipelineConfig with release_dir property alias

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | SprintConfig must extend PipelineConfig so sprint consumes the shared pipeline foundation; `release_dir` property alias preserves backward compatibility. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | migration keyword; schema/model change; breaking change potential |
| Tier | STRICT |
| Confidence | `[████████░░] 85%` |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0008/spec.md`
- `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Deliverables:**
- `src/superclaude/cli/sprint/config.py` modified so `SprintConfig` inherits from `PipelineConfig`; `release_dir` property aliases `work_dir`; sprint-specific fields remain in SprintConfig only

**Steps:**
1. **[PLANNING]** Read current `sprint/config.py` to identify all fields; compare with `PipelineConfig` to determine which fields move to parent
2. **[PLANNING]** Identify all code paths referencing `config.release_dir` to verify alias coverage
3. **[EXECUTION]** Modify `SprintConfig` to inherit from `PipelineConfig`; add `@property release_dir` that returns `self.work_dir`
4. **[EXECUTION]** Keep sprint-specific fields (index_path, phases, stall_timeout, etc.) in SprintConfig only
5. **[EXECUTION]** Verify `config.release_dir` usage across sprint codebase resolves correctly
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_config.py -v` to confirm zero regression
7. **[COMPLETION]** Record evidence of backward-compatible property alias

**Acceptance Criteria:**
- `SprintConfig` in `src/superclaude/cli/sprint/config.py` inherits from `PipelineConfig`
- `config.release_dir` returns same value as `config.work_dir` via property alias
- All SprintConfig computed properties that depend on release_dir (debug_log_path, results_dir, execution_log_jsonl, execution_log_md, output_file, error_file, result_file) resolve correctly through the release_dir->work_dir alias chain
- Sprint-specific fields (index_path, phases, stall_timeout) remain in SprintConfig, not PipelineConfig
- `uv run pytest tests/sprint/test_config.py` exits 0 with no test file modifications

**Validation:**
- `uv run pytest tests/sprint/test_config.py -v` exits 0
- Evidence: `python -c "from superclaude.cli.sprint.config import SprintConfig; c = SprintConfig(...); assert c.release_dir == c.work_dir"` succeeds

**Dependencies:** T01.01 (PipelineConfig must exist)
**Rollback:** Revert `sprint/config.py` to pre-migration version
**Notes:** Critical Path Override applied due to `models/` pattern in config inheritance chain. Risk R-001 from roadmap applies: commit after each passing test run.

---

### T02.02 -- Modify `sprint/models.py` so SprintStep extends Step and PhaseResult extends StepResult

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | Sprint model types must inherit from pipeline types to enable shared executor consumption without duplicating type hierarchies. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | migration keyword; schema/model change |
| Tier | STRICT |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0009/spec.md`
- `TASKLIST_ROOT/artifacts/D-0009/evidence.md`

**Deliverables:**
- `src/superclaude/cli/sprint/models.py` modified so `SprintStep` extends `Step` and `PhaseResult` extends `StepResult` from pipeline

**Steps:**
1. **[PLANNING]** Read current `sprint/models.py` to identify all types and their field sets
2. **[PLANNING]** Determine which fields are already in pipeline `Step`/`StepResult` vs sprint-specific additions
3. **[EXECUTION]** Modify `SprintStep` to extend `pipeline.Step`; add sprint-specific fields as extensions
4. **[EXECUTION]** Modify `PhaseResult` to extend `pipeline.StepResult`; preserve sprint-specific fields
5. **[EXECUTION]** Update import paths within sprint modules that reference these types
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_models.py -v` to confirm zero regression
7. **[COMPLETION]** Record evidence of correct inheritance chain

**Acceptance Criteria:**
- `SprintStep` in `sprint/models.py` extends `pipeline.Step` with correct MRO (method resolution order)
- `PhaseResult` in `sprint/models.py` extends `pipeline.StepResult`
- All existing sprint code using `SprintStep` and `PhaseResult` fields continues to work without modification
- `uv run pytest tests/sprint/test_models.py` exits 0 with no test file modifications

**Validation:**
- `uv run pytest tests/sprint/test_models.py -v` exits 0
- Evidence: `python -c "from superclaude.cli.sprint.models import SprintStep; from superclaude.cli.pipeline import Step; assert issubclass(SprintStep, Step)"` succeeds

**Dependencies:** T01.01 (pipeline models), T02.01 (SprintConfig inheritance established)
**Rollback:** Revert `sprint/models.py` to pre-migration version
**Notes:** Critical Path Override applied due to `models/` path pattern.

---

### T02.03 -- Modify `sprint/process.py` to re-export ClaudeProcess from `pipeline.process`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | Import stability canary: ensures `from superclaude.cli.sprint.process import ClaudeProcess` continues to resolve after extraction. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | migration keyword; breaking change potential on import paths |
| Tier | STRICT |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0010/spec.md`
- `TASKLIST_ROOT/artifacts/D-0010/evidence.md`

**Deliverables:**
- `src/superclaude/cli/sprint/process.py` re-exports `ClaudeProcess` from `superclaude.cli.pipeline.process`

**Steps:**
1. **[PLANNING]** Confirm T01.04 completed: `ClaudeProcess` exists in `pipeline/process.py`
2. **[PLANNING]** Identify all import sites: `from superclaude.cli.sprint.process import ClaudeProcess`
3. **[EXECUTION]** Replace sprint's `process.py` body with: `from superclaude.cli.pipeline.process import ClaudeProcess  # re-export`
4. **[EXECUTION]** Verify re-export resolves correctly at runtime
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/test_process.py -v` as import stability canary
6. **[COMPLETION]** Record evidence of preserved import path

**Acceptance Criteria:**
- `sprint/process.py` contains only the re-export statement from `pipeline.process`
- `from superclaude.cli.sprint.process import ClaudeProcess` resolves correctly at runtime
- `uv run pytest tests/sprint/test_process.py` exits 0 with no test file modifications
- No duplicate `ClaudeProcess` implementation in sprint module

**Validation:**
- `uv run pytest tests/sprint/test_process.py -v` exits 0
- Evidence: `python -c "from superclaude.cli.sprint.process import ClaudeProcess; print(ClaudeProcess.__module__)"` shows `superclaude.cli.pipeline.process`

**Dependencies:** T01.04 (ClaudeProcess in pipeline/process.py)
**Rollback:** Restore original `sprint/process.py` with full ClaudeProcess implementation

---

### T02.04 -- Run full sprint regression: all sprint test files pass with zero modifications during pipeline migration

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | NFR-002 requires all sprint test files passing at extraction start remain passing with no sprint test modifications during pipeline/ migration, validating zero regression. Baseline is the post-v2.07 state. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | migration keyword; system-wide scope (all sprint tests) |
| Tier | STANDARD |
| Confidence | `[████████░░] 80%` |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- `TASKLIST_ROOT/artifacts/D-0011/spec.md`
- `TASKLIST_ROOT/artifacts/D-0011/evidence.md`

**Deliverables:**
- Sprint regression report: `uv run pytest tests/sprint/` exits 0 with all sprint test files passing and zero test file modifications during pipeline/ migration

**Steps:**
1. **[PLANNING]** Enumerate all sprint test files to establish baseline (post-v2.07 state)
2. **[PLANNING]** Verify no sprint test files were modified during T02.01-T02.03 (git diff check)
3. **[EXECUTION]** Run `uv run pytest tests/sprint/ -v --tb=long` to execute full regression suite
4. **[EXECUTION]** If any failures: investigate root cause in migration changes (T02.01-T02.03), fix pipeline/sprint code (NOT test code)
5. **[VERIFICATION]** Confirm `uv run pytest tests/sprint/` exits 0 with all sprint test files collected
6. **[COMPLETION]** Record test output as evidence; record git diff showing zero test file changes

**Acceptance Criteria:**
- `uv run pytest tests/sprint/ -v` exits 0 with all sprint test files discovered and passing
- `git diff tests/sprint/` shows zero modifications to test files
- All sprint CLI external behavior preserved (NFR-001)
- Stall watchdog behavior (--stall-timeout, --stall-action) exercised by existing sprint tests continues to pass post-migration
- Regression report captured with full test output

**Validation:**
- `uv run pytest tests/sprint/ -v` exits 0
- Evidence: `git diff --name-only tests/sprint/` returns empty (no test modifications)

**Dependencies:** T02.01-T02.03 (all migration tasks)
**Rollback:** Revert all Phase 2 changes if regression cannot be resolved without test modifications

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm sprint migration is complete with zero regression before proceeding to roadmap implementation.
**Checkpoint Report Path:** `TASKLIST_ROOT/checkpoints/CP-P02-END.md`
**Verification:**
- `uv run pytest tests/sprint/` exits 0 with all sprint test files passing
- `SprintConfig` inherits from `PipelineConfig` with working `release_dir` alias
- `ClaudeProcess` import from sprint resolves to pipeline module

**Exit Criteria:**
- NFR-001 (sprint CLI API unchanged) verified by full regression suite
- NFR-002 (no test modifications) verified by git diff
- Sprint-to-pipeline inheritance chain correct for config, models, and process
