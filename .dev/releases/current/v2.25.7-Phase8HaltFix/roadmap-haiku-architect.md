---
spec_source: v2.25.7-phase8-sprint-context-resilience-prd.md
complexity_score: 0.62
primary_persona: architect
---

# 1. Executive summary

This roadmap delivers Phase 8 sprint context resilience through a controlled, moderate-complexity change set spanning executor, process, pipeline, monitor, logging, diagnostics, and tests. The architectural objective is to reduce prompt-context waste, improve subprocess isolation, preserve backward compatibility, and strengthen recovery behavior without expanding the dependency surface or redesigning the sprint system.

## Architectural priorities

1. **Contain prompt scope at execution boundaries**
   - Enforce per-phase isolation so subprocesses only see the active phase file.
   - Prevent accidental `@` resolution of `tasklist-index.md` and unrelated artifacts.

2. **Preserve compatibility while extending orchestration plumbing**
   - All new parameters remain keyword-only with safe defaults.
   - Internal path resolution must consolidate around `SprintConfig`.

3. **Harden lifecycle correctness**
   - Cleanup must be guaranteed on success, failure, and startup recovery.
   - Recovery statuses must be surfaced consistently, especially `PASS_RECOVERED`.

4. **Keep the implementation bounded**
   - No new third-party dependencies.
   - No architectural redesign beyond targeted resilience fixes.
   - S4-scale batching remains explicitly out of scope.

## Expected outcomes

- Per-phase token baseline reduced by blocking access to the large index artifact.
- Prompt-too-long recovery classification becomes more accurate.
- Screen-visible execution results correctly report recovered passes.
- All changes remain compliant with strict backward-compatibility and existing test expectations.

---

# 2. Phased implementation plan with milestones

## Phase 0. Discovery, design validation, and open-question resolution

### Goals
Establish implementation certainty before modifying execution-critical code.

### Key actions
1. Validate current interfaces and call paths for:
   - `execute_sprint()`
   - `ClaudeProcess.__init__()`
   - `build_env()`
   - `detect_prompt_too_long()`
   - `_determine_phase_status()`
   - `FailureClassifier.classify()`
   - `SprintLogger.write_phase_result()`

2. Resolve open questions that affect architecture:
   - Whether `scoped_work_dir` already exists and how it is enforced.
   - Whether isolation is passed as `cwd`, env var, or both.
   - Whether `config.release_name` exists and what fallback logic is needed.
   - Fallback behavior when `DiagnosticBundle.config is None`.

3. Perform codebase grep for `PhaseStatus.PASS` handling to identify any additional parity gaps for `PASS_RECOVERED`.

4. Confirm test placement:
   - All new tests live in `tests/sprint/test_phase8_halt_fix.py`.

### Milestones
- **M0.1**: Execution-path map documented.
- **M0.2**: Open questions reduced to implementation decisions with explicit defaults.
- **M0.3**: Success-state switch sites inventoried.

### Architect notes
This phase prevents drift and avoids partial wiring, which is the main architectural failure mode for this sprint.

### Timeline estimate
- **0.5 day**

---

## Phase 1. Isolation lifecycle implementation

### Goals
Introduce strict per-phase workspace isolation with deterministic cleanup.

### Key actions
1. In `execute_sprint()`:
   - Remove orphaned `config.results_dir / ".isolation"` at startup with `shutil.rmtree(..., ignore_errors=True)`.
   - Before each phase subprocess launch:
     - Create `config.results_dir / ".isolation" / f"phase-{phase.number}"`.
     - Copy only `phase.file` into that directory using `shutil.copy2()`.

2. Pass the isolation path into the subprocess boundary:
   - Use `scoped_work_dir` if already supported.
   - If not, add the minimum viable plumbing required to ensure the subprocess resolves files only against the isolated directory.

3. In the per-phase `finally` block:
   - Always remove the phase isolation directory with `shutil.rmtree(..., ignore_errors=True)`.

### Milestones
- **M1.1**: Orphan cleanup executes before phase loop.
- **M1.2**: Isolation directory created per phase with exactly one copied file.
- **M1.3**: Isolation directory removed on both success and failure paths.
- **M1.4**: Subprocess file resolution is constrained to isolated input.

### Deliverables
- Executor changes implementing create → use → cleanup lifecycle.
- Supporting process plumbing if required for scoped execution.

### Architect notes
This is the highest-value architectural change because it enforces boundary control at the process edge rather than relying on prompt instruction alone.

### Timeline estimate
- **1.0 day**

---

## Phase 2. Environment propagation and subprocess plumbing

### Goals
Support resilient process configuration without breaking existing callers.

### Key actions
1. Extend `ClaudeProcess.__init__()` with:
   - `env_vars: dict[str, str] | None = None`
   - Store on the instance in a backward-compatible way.

2. Extend `build_env()` with:
   - `env_vars: dict[str, str] | None = None`
   - Merge after `os.environ.copy()`.

3. Ensure propagation chain is complete:
   - `execute_sprint()` / caller
   - `ClaudeProcess`
   - subprocess spawn environment builder

4. Define precedence explicitly:
   - Recommended: provided `env_vars` override inherited environment values for deterministic execution.

### Milestones
- **M2.1**: `env_vars` supported at process constructor.
- **M2.2**: `env_vars` supported at environment builder.
- **M2.3**: End-to-end propagation verified in tests or mocks.

### Deliverables
- Process and pipeline changes for environment injection.
- Verified compatibility with existing call sites.

### Architect notes
This phase is structurally important because incomplete propagation would create a false sense of isolation while leaving subprocess behavior unchanged.

### Timeline estimate
- **0.5 day**

---

## Phase 3. Prompt resilience and context header enhancements

### Goals
Improve prompt observability and recovery classification accuracy.

### Key actions
1. Update `build_prompt()` to add `## Sprint Context` containing:
   - Sprint name
   - Current phase number / total phases
   - Artifact root path
   - Results directory
   - Prior-phase artifact directories
   - Instruction: `"All task details are in the phase file. Do not seek additional index files."`

2. Extend `detect_prompt_too_long()` with:
   - `error_path: Path | None = None`
   - Check both output and error files using the same last-10-lines logic.

3. Extend `_determine_phase_status()` with:
   - `error_file: Path | None = None`
   - Pass through to `detect_prompt_too_long()`.

4. Update `execute_sprint()` call site to pass:
   - `config.error_file(phase)`

### Milestones
- **M3.1**: Prompt contains the new sprint context block.
- **M3.2**: Prompt-too-long detection works from stderr path as well as stdout path.
- **M3.3**: Phase-status determination correctly uses error-file context.

### Deliverables
- Prompt builder update.
- Monitor and status-determination plumbing update.

### Architect notes
This phase addresses a systemic observability gap: failures caused by prompt length can surface in different files, so recovery detection must not assume a single-channel log source.

### Timeline estimate
- **0.5 day**

---

## Phase 4. Diagnostics and status-consistency fixes

### Goals
Make outcome handling architecturally consistent across logging and diagnostics.

### Key actions
1. Update `SprintLogger.write_phase_result()`:
   - Route `PhaseStatus.PASS_RECOVERED` through the same INFO branch as `PASS` and `PASS_NO_REPORT`.

2. Update `FailureClassifier.classify()`:
   - Replace hardcoded output-file construction with `bundle.config.output_file(...)`.

3. If necessary, extend `DiagnosticBundle`:
   - Add `config: SprintConfig | None = None`
   - Preserve backward compatibility.

4. If `config is None`, define controlled fallback behavior:
   - Preferred: explicit guarded fallback to legacy path logic only if needed.
   - Avoid silent failure or ambiguous behavior.

### Milestones
- **M4.1**: `PASS_RECOVERED` is screen-visible as a success-class result.
- **M4.2**: Failure classifier uses canonical config-driven path resolution.
- **M4.3**: Diagnostic bundle remains backward compatible.

### Deliverables
- Logger and classifier corrections.
- Optional `DiagnosticBundle` schema update.

### Architect notes
Canonical path ownership belongs in `SprintConfig`; duplicating path construction in diagnostics is an architectural debt source and should be eliminated now.

### Timeline estimate
- **0.5 day**

---

## Phase 5. Test implementation, regression protection, and quality gates

### Goals
Prove lifecycle correctness, compatibility safety, and recovery behavior.

### Key actions
1. Add the required test cases in `tests/sprint/test_phase8_halt_fix.py`:
   - Isolation creation before subprocess
   - Isolation cleanup after success
   - Isolation cleanup after failure
   - Startup orphan cleanup
   - Prompt summary header presence
   - Prompt-too-long detection via error file
   - `error_path=None` compatibility behavior
   - `PASS_RECOVERED` screen output
   - Config-driven classifier output path

2. Add one more coverage check if missing:
   - `_determine_phase_status()` passing `error_file` through to detection logic

3. Run validation commands:
   - `uv run pytest tests/sprint/test_phase8_halt_fix.py -v`
   - `uv run pytest tests/ -v --tb=short`
   - `uv run ruff check`
   - `uv run ruff format --check`

### Milestones
- **M5.1**: New targeted tests pass.
- **M5.2**: Full suite passes with no regressions.
- **M5.3**: Ruff and format checks are clean.

### Deliverables
- Test suite additions.
- Validation evidence for all success criteria.

### Architect notes
For this sprint, tests are not just validation artifacts; they are the mechanism that locks down lifecycle guarantees and backward compatibility across multiple subsystems.

### Timeline estimate
- **1.0 day**

---

## Phase 6. Smoke validation and release readiness

### Goals
Validate operational behavior under realistic sprint-execution conditions.

### Key actions
1. Perform a manual smoke run of a phase expected to approach prompt limits.
2. Confirm:
   - `PASS_RECOVERED` appears instead of `ERROR` when recovery occurs.
   - Isolated subprocess cannot resolve `tasklist-index.md`.
   - Cleanup leaves no stale `.isolation/phase-*` directories.
3. Document any residual exposure to S4-scale context exhaustion.

### Milestones
- **M6.1**: Recovery status visible in operator output.
- **M6.2**: Isolation verified in practical execution.
- **M6.3**: Release-ready conclusion documented.

### Deliverables
- Manual verification notes.
- Final go/no-go recommendation.

### Architect notes
This phase validates the real system boundary conditions that unit tests only approximate, especially subprocess resolution behavior.

### Timeline estimate
- **0.5 day**

---

# 3. Risk assessment and mitigation strategies

## High-priority risks

### 1. Context exhaustion still recurs on very large phases
- **Severity**: High
- **Impact**: Sprint recovery remains incomplete for oversized deliverable sets.
- **Mitigation**:
  1. Enforce isolation immediately to remove unnecessary token load.
  2. Add monitoring on phase token usage.
  3. Define S4 trigger conditions explicitly:
     - second prompt-exhaustion recurrence
     - more than 8 deliverables per phase
  4. Keep deliverables per phase bounded until S4.

### 2. Isolation appears implemented but is not actually enforced
- **Severity**: High
- **Impact**: `tasklist-index.md` remains accessible; core value of sprint is lost.
- **Mitigation**:
  1. Verify actual subprocess resolution mechanism.
  2. Test that exactly one file exists in the isolation directory at launch.
  3. Add smoke validation that index resolution fails in isolated mode.

## Medium-priority risks

### 3. Cleanup failures mask primary phase errors
- **Severity**: Medium
- **Impact**: Error diagnosis becomes misleading.
- **Mitigation**:
  1. Use `ignore_errors=True` in all `rmtree` calls.
  2. Keep cleanup in `finally`.
  3. Avoid raising cleanup exceptions over execution results.

### 4. `env_vars` plumbing is only partially connected
- **Severity**: Medium
- **Impact**: Execution behavior diverges from design.
- **Mitigation**:
  1. Trace end-to-end propagation before implementation.
  2. Add focused test coverage for propagation.
  3. Keep the design simple: one source, one builder, one spawn boundary.

### 5. Signature changes break existing callers or tests
- **Severity**: Medium
- **Impact**: Regression across the wider codebase.
- **Mitigation**:
  1. Add new args as keyword-only.
  2. Use `None` defaults consistently.
  3. Run full test suite before merge.

## Low-priority risks

### 6. `PASS_RECOVERED` parity gaps remain elsewhere
- **Severity**: Low
- **Impact**: Inconsistent UX or diagnostics in edge paths.
- **Mitigation**:
  1. Codebase grep for success-state branches.
  2. Treat `PASS_RECOVERED` as a policy invariant.
  3. Add targeted follow-up issue if more gaps are found.

### 7. `DiagnosticBundle.config` introduces compatibility ambiguity
- **Severity**: Low
- **Impact**: Some callers may instantiate without config.
- **Mitigation**:
  1. Default to `None`.
  2. Use guarded fallback behavior.
  3. Prefer migration toward always-supplied config over time.

### 8. Concurrent runs share the same `.isolation` base directory
- **Severity**: Low to Medium
- **Impact**: Startup cleanup could interfere with another run using the same results directory.
- **Mitigation**:
  1. Document same-results-dir concurrency as unsupported unless proven otherwise.
  2. If concurrency is required later, move to run-scoped isolation roots.

---

# 4. Resource requirements and dependencies

## Engineering resources

1. **Primary implementer**
   - Python engineer familiar with sprint orchestration flow.
2. **Reviewer**
   - Architecture-aware reviewer focused on process boundaries and backward compatibility.
3. **QA/validator**
   - Executes targeted and full-suite validation, plus smoke verification.

## Code areas impacted

1. `src/superclaude/cli/sprint/` execution path
2. `src/superclaude/cli/sprint/process.py`
3. `src/superclaude/cli/pipeline/process.py`
4. Prompt builder path
5. Monitor/status determination path
6. Logger/diagnostics path
7. `tests/sprint/test_phase8_halt_fix.py`

## External and internal dependencies

1. **Stdlib**
   - `shutil`
   - `os`
   - `re`
   - `pathlib`
   - existing approved modules only

2. **Internal APIs**
   - `SprintConfig.output_file(phase)`
   - `SprintConfig.error_file(phase)`
   - `PhaseStatus.PASS_RECOVERED`
   - `ClaudeProcess`
   - `DiagnosticBundle`

3. **Toolchain**
   - `uv run` for all Python execution
   - `ruff` for lint and formatting checks
   - `pytest` for targeted and full regression validation

## Dependency management guidance

1. Do not introduce new packages.
2. Centralize path logic in `SprintConfig`.
3. Avoid adding secondary abstractions unless the current interfaces require them.
4. Keep new data flow explicit rather than implicit.

---

# 5. Success criteria and validation approach

## Success criteria

1. **Targeted test suite passes**
   - All new Phase 8 tests pass in `tests/sprint/test_phase8_halt_fix.py`.

2. **Full regression suite passes**
   - Existing test baseline remains intact.

3. **Static analysis remains clean**
   - No `ruff check` or `ruff format --check` violations.

4. **Recovered phases surface correctly**
   - Manual smoke validation shows `PASS_RECOVERED` on screen output.

5. **Isolation blocks index-file access**
   - `tasklist-index.md` is not available to isolated phase subprocesses.

## Validation approach

### Automated validation
1. Run focused tests first to validate the changed behavior.
2. Run full suite second to validate compatibility.
3. Run lint/format last to ensure merge readiness.

### Behavioral validation
1. Inspect created isolation directory during subprocess launch.
2. Confirm exactly one copied phase file exists.
3. Confirm directory is removed after both success and failure.
4. Validate prompt contains `## Sprint Context`.
5. Validate prompt-too-long detection from stderr path.

### Architectural validation
1. Confirm all new parameters are keyword-only.
2. Confirm all defaults are backward-compatible.
3. Confirm canonical file path usage flows through `SprintConfig`.
4. Confirm success-state handling includes `PASS_RECOVERED`.

---

# 6. Timeline estimates per phase

## Recommended sequencing

1. **Phase 0 — Discovery and design validation**
   - Estimate: **0.5 day**

2. **Phase 1 — Isolation lifecycle implementation**
   - Estimate: **1.0 day**

3. **Phase 2 — Environment propagation plumbing**
   - Estimate: **0.5 day**

4. **Phase 3 — Prompt resilience and context header**
   - Estimate: **0.5 day**

5. **Phase 4 — Diagnostics and status consistency**
   - Estimate: **0.5 day**

6. **Phase 5 — Tests and quality gates**
   - Estimate: **1.0 day**

7. **Phase 6 — Smoke validation and release readiness**
   - Estimate: **0.5 day**

## Total estimated implementation window
- **4.5 working days**

## Critical path
1. Discovery/open-question resolution
2. Isolation implementation
3. Environment propagation verification
4. Tests
5. Smoke validation

## Parallelization opportunities
1. **Parallel after discovery**
   - Prompt/status work can proceed in parallel with diagnostics fixes.
2. **Parallel during validation**
   - Targeted test authoring can begin while final logger/classifier fixes are reviewed.
3. **Not recommended for parallelization**
   - Isolation lifecycle and env propagation should remain sequential because they share the subprocess boundary.

---

# Recommended roadmap outcome

## Go-forward recommendation

Proceed with this sprint as a **strict, bounded resilience hardening effort** with one architectural rule above all others:

1. **Enforce isolation at the subprocess boundary, not just in prompt wording.**

If that boundary is implemented and validated correctly, the remaining work becomes a controlled set of compatibility-safe resilience fixes. If it is not, the sprint will look complete in code review while missing its primary system objective.
