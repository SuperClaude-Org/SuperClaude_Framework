---
spec_source: v2.25.7-phase8-sprint-context-resilience-prd.md
generated: "2026-03-16T00:00:00Z"
generator: requirements-extraction-agent-v1
functional_requirements: 22
nonfunctional_requirements: 5
total_requirements: 27
complexity_score: 0.62
complexity_class: moderate
domains_detected: 5
risks_identified: 6
dependencies_identified: 8
success_criteria_count: 5
extraction_mode: full
pipeline_diagnostics: {elapsed_seconds: 97.0, started_at: "2026-03-16T02:07:02.441590+00:00", finished_at: "2026-03-16T02:08:39.459832+00:00"}
---

## Functional Requirements

**S3-A: Isolation Wiring**

- **FR-001** (S3-R01): Before spawning each phase subprocess in `execute_sprint()`, create a per-phase isolation directory at `config.results_dir / ".isolation" / f"phase-{phase.number}"` and copy only the phase file into it using `shutil.copy2()`. Priority: P0.
- **FR-002** (S3-R02): Pass the per-phase isolation directory as `scoped_work_dir` to `ClaudeProcess` so the subprocess cannot resolve `tasklist-index.md` or other phase files via `@` references. Priority: P0.
- **FR-003** (S3-R03): In the `finally` block of the phase execution loop, remove the per-phase isolation directory using `shutil.rmtree(phase_isolation_dir, ignore_errors=True)`. Priority: P0.

**S3-B: ClaudeProcess `env_vars` Support**

- **FR-004** (S3-R07): Add keyword-only parameter `env_vars: dict[str, str] | None = None` to `ClaudeProcess.__init__()` in `src/superclaude/cli/sprint/process.py`. Store as `self._extra_env_vars` and pass through to pipeline base class or merge into environment at subprocess spawn. Priority: P0.
- **FR-005** (S3-R08): Add keyword-only parameter `env_vars: dict[str, str] | None = None` to `build_env()` in `src/superclaude/cli/pipeline/process.py`. When not None, merge the provided dict into the returned environment after `os.environ.copy()`, before return. Priority: P0.

**S3-C: Startup Orphan Cleanup**

- **FR-006** (S3-R04): At the start of `execute_sprint()`, before the phase loop begins, check for and remove any existing `.isolation/` directory under `config.results_dir` using `shutil.rmtree(isolation_base, ignore_errors=True)` where `isolation_base = config.results_dir / ".isolation"`. Priority: P1.

**S3-D: `build_prompt()` Summary Header**

- **FR-007** (S3-R05): Add a `## Sprint Context` section to `build_prompt()` output containing: sprint name (from `config.release_name` or release dir name), phase number and total phases, artifact root path (`config.release_dir`), results directory (`config.results_dir`), and prior-phase artifact directories (list of `artifacts/phase-{N}/` for all N < current phase). Priority: P0.
- **FR-008** (S3-R06): Add the instruction `"All task details are in the phase file. Do not seek additional index files."` within the `## Sprint Context` section of `build_prompt()`. Priority: P1.

**S2-D: `detect_prompt_too_long()` Error Path Extension**

- **FR-009** (S2-R08): Add keyword-only parameter `error_path: Path | None = None` to `detect_prompt_too_long()`. When `error_path` is not None, scan it for `PROMPT_TOO_LONG_PATTERN` using the same last-10-lines logic applied to `output_path`. Return `True` if the pattern is found in either file. Priority: P1.

**S2-E: `_determine_phase_status()` Error File Plumbing**

- **FR-010** (S2-R08b): Add keyword-only parameter `error_file: Path | None = None` to `_determine_phase_status()` with default `None`. Priority: P1.
- **FR-011** (S2-R08c): At the call site in `execute_sprint()`, pass `error_file=config.error_file(phase)` to `_determine_phase_status()`. Priority: P1.
- **FR-012** (S2-R08d): Inside `_determine_phase_status()`, pass `error_path=error_file` to `detect_prompt_too_long()` when `error_file` is not None. Priority: P1.

**FIX-1: Logger `PASS_RECOVERED` Routing**

- **FR-013** (FIX-1-R01): In `SprintLogger.write_phase_result()`, add `PhaseStatus.PASS_RECOVERED` to the screen INFO routing branch alongside `PhaseStatus.PASS` and `PhaseStatus.PASS_NO_REPORT` at line 136. Priority: P1.

**FIX-2: `FailureClassifier` Output File Path**

- **FR-014** (FIX-2-R01): In `FailureClassifier.classify()` at line 183, replace the hardcoded path expression `bundle.phase_result.phase.file.parent.parent / "results" / f"phase-{bundle.phase_result.phase.number}-output.txt"` with `bundle.config.output_file(bundle.phase_result.phase)`. Priority: P1.
- **FR-015** (FIX-2-R02): If `bundle` does not carry a `config` reference, add `config: SprintConfig` as a field to `DiagnosticBundle` (or pass it as a parameter to `classify()`) with a `None` default for backward compatibility. Priority: P1.

**Test Requirements (T04 Suite)**

- **FR-016** (T04.01): `test_isolation_dir_created_before_subprocess` — per-phase isolation dir exists with exactly one file matching `phase.file.name` at subprocess launch.
- **FR-017** (T04.02): `test_isolation_dir_cleaned_after_phase_completes` — isolation dir removed after phase completes with `exit_code=0`.
- **FR-018** (T04.03): `test_isolation_dir_cleaned_after_phase_fails` — isolation dir removed after phase fails with `exit_code=1` (finally block).
- **FR-019** (T04.04): `test_orphaned_isolation_dirs_cleaned_on_startup` — pre-existing `.isolation/` removed before phase loop.
- **FR-020** (T04.05): `test_summary_header_in_prompt` — returned string contains `## Sprint Context`, phase number, and `"Do not seek additional index files"`.
- **FR-021** (T04.06): `test_detect_prompt_too_long_scans_error_file` — returns `True` when pattern is in last 10 lines of `error_path` and output file is clean.
- **FR-022** (T04.07): `test_detect_prompt_too_long_error_path_none` — behavior identical to current implementation when `error_path=None`, no exception raised.

---

## Non-Functional Requirements

- **NFR-001** (NF-01): All pre-existing tests must continue to pass (≥629 tests). No existing test signatures may be broken by any change introduced in this phase.
- **NFR-002** (NF-02): All new parameters must be keyword-only with `None` (or appropriate sentinel) defaults, ensuring backward-compatible call sites throughout the codebase.
- **NFR-003** (NF-03): Zero `ruff check` and `ruff format --check` errors on all 7 modified files. Static analysis clean state must be maintained.
- **NFR-004** (NF-04): No imports outside already-used stdlib modules. `shutil`, `os`, `re`, `pathlib`, `datetime` are pre-approved. No new third-party dependencies introduced.
- **NFR-005** (NF-05): `PASS_RECOVERED` handling must be consistent — any code path that switches on `PhaseStatus` success values must include `PASS_RECOVERED` to prevent silent omission in future additions.

---

## Complexity Assessment

**complexity_score: 0.62**
**complexity_class: moderate**

**Scoring Rationale**:

| Factor | Weight | Score | Contribution |
|---|---|---|---|
| Number of files modified (7) | High | 0.6 | +0.15 |
| Cross-cutting concern (isolation lifecycle wires executor→process→pipeline) | High | 0.7 | +0.14 |
| Subprocess environment propagation (env_vars chain) | Medium | 0.5 | +0.08 |
| Backward-compatibility constraints (keyword-only, None defaults) | Medium | 0.5 | +0.07 |
| Test surface (9 new tests, 3 classes, mocking required) | Medium | 0.5 | +0.07 |
| Domain count (5 distinct sub-systems) | Medium | 0.5 | +0.06 |
| Change type (targeted patches, no architectural redesign) | Low | 0.3 | −0.05 (mitigator) |
| Out-of-scope items well-bounded (S4 deferred) | Low | 0.3 | −0.10 (mitigator) |

**Rationale narrative**: The work spans 7 files across 5 subsystems (executor, process, pipeline, monitor, logging/diagnostics) with non-trivial lifecycle coordination (isolation create → subprocess → finally-cleanup). However, each individual change is small and well-scoped (XS or S effort ratings), there is no API surface change, all new parameters carry backward-compatible defaults, and the out-of-scope boundary is clearly drawn. The test suite additions are straightforward unit tests with mocking. This places the work solidly in **moderate** rather than complex territory.

---

## Architectural Constraints

1. **UV-only Python execution**: All Python operations must use `uv run`. No direct `python`, `python -m`, or `pip install` invocations permitted.
2. **Keyword-only parameters with None defaults**: All new function/method parameters introduced in this phase must be keyword-only (`*`, param_name) with `None` or appropriate sentinel defaults to preserve call-site backward compatibility across the codebase.
3. **No new third-party dependencies**: Only stdlib modules already imported in target files are permitted (`shutil`, `os`, `re`, `pathlib`, `datetime`). This preserves the lightweight dependency graph.
4. **`SprintConfig.output_file(phase)` as canonical path resolver**: The `FailureClassifier` must use `config.output_file(phase)` rather than constructing paths inline. All output file path resolution must flow through `SprintConfig`.
5. **`PASS_RECOVERED` parity with `PASS`**: Any switch/conditional on `PhaseStatus` success variants must treat `PASS_RECOVERED` identically to `PASS` and `PASS_NO_REPORT`. This is a recurring architectural invariant.
6. **`finally` block for isolation cleanup**: Isolation directory teardown must occur in a `finally` block to guarantee cleanup on both success and failure paths.
7. **Isolation at `config.results_dir / ".isolation" / f"phase-{N}"`**: The directory layout for isolation is fixed. The startup orphan cleanup path is `config.results_dir / ".isolation"` (the base), not a per-phase subdirectory.
8. **Test file placement**: All new tests for this phase must be added to `tests/sprint/test_phase8_halt_fix.py`, not scattered to other test files.
9. **Compliance tier: STRICT**: This is a multi-file orchestration subsystem change requiring full MCP workflow enforcement.
10. **Branch constraint**: All work targets `v2.25.7-phase8` branch, not `master` or `integration`.

---

## Risk Inventory

1. **RISK-001 — Isolation cleanup failure leaves stale directories** (Severity: Medium)
   - *Description*: If `shutil.rmtree` is called without `ignore_errors=True`, an OS-level error (permissions, locked file) could raise an exception in the `finally` block, masking the original phase outcome.
   - *Mitigation*: Mandate `ignore_errors=True` on all `shutil.rmtree` calls for isolation dirs (explicitly specified in S3-R03 and S3-R04).

2. **RISK-002 — env_vars propagation gap** (Severity: Medium)
   - *Description*: The `env_vars` dict added to `ClaudeProcess.__init__()` must be forwarded through to the pipeline's `build_env()`. If the wiring is incomplete (e.g., stored but not passed), the scoped working directory is never set in the subprocess environment, making isolation ineffective.
   - *Mitigation*: Test T04.01 implicitly validates this by asserting the subprocess cannot resolve `tasklist-index.md`. Explicit unit test for env propagation is not listed but should be considered.

3. **RISK-003 — PASS_RECOVERED omission in other switch sites** (Severity: Low)
   - *Description*: FIX-1 addresses one specific switch in `write_phase_result()`. Other code paths switching on `PhaseStatus` success values may also omit `PASS_RECOVERED`, silently degrading behavior.
   - *Mitigation*: NFR-005 mandates a consistent policy. A codebase-wide grep for `PhaseStatus.PASS` usages is recommended before merging.

4. **RISK-004 — DiagnosticBundle config field backward compatibility** (Severity: Low)
   - *Description*: FIX-2-R02 requires adding `config: SprintConfig` to `DiagnosticBundle`. Existing instantiation sites that do not pass `config` will break unless the field has a `None` default.
   - *Mitigation*: NFR-002 mandates `None` defaults for all new fields. The requirement itself notes "with a `None` default for backward compatibility."

5. **RISK-005 — Test suite regression from signature changes** (Severity: Medium)
   - *Description*: Adding keyword-only parameters to `detect_prompt_too_long()`, `_determine_phase_status()`, and `build_env()` could break existing test call sites that pass positional arguments.
   - *Mitigation*: NFR-002 mandates keyword-only with None defaults. All existing positional call sites remain valid since new params are appended after existing ones.

6. **RISK-006 — Context exhaustion recurrence before S4 is implemented** (Severity: High)
   - *Description*: S3 reduces token waste from `tasklist-index.md` (~14K tokens) and adds an orientation header, but does not eliminate context exhaustion for phases with very large deliverable sets. S4 (artifact batching) is deferred.
   - *Mitigation*: The PRD acknowledges this explicitly; S4 is triggered by a second exhaustion occurrence or >8 deliverables/phase. Operators should monitor phase token usage and keep deliverables ≤8 per phase in the interim.

---

## Dependency Inventory

1. **`shutil` (stdlib)** — Used for `shutil.copy2()` (isolation dir file copy) and `shutil.rmtree()` (cleanup). Already imported in `executor.py`.
2. **`pathlib.Path` (stdlib)** — Used for isolation directory path construction (`config.results_dir / ".isolation" / f"phase-{N}"`). Already imported in relevant files.
3. **`os.environ` (stdlib)** — Used in `build_env()` via `os.environ.copy()`. Already imported in `pipeline/process.py`.
4. **`re` (stdlib)** — Used for `PROMPT_TOO_LONG_PATTERN` matching in `detect_prompt_too_long()`. Already imported in `monitor.py`.
5. **`SprintConfig.output_file(phase)`** — Internal API method. `FailureClassifier` depends on this being accessible via `bundle.config`. If `DiagnosticBundle` does not carry a `config` reference, `SprintConfig` must be passed as a parameter.
6. **`SprintConfig.error_file(phase)`** — Internal API method. `execute_sprint()` depends on this to pass the error file path to `_determine_phase_status()`. Must exist and return a valid `Path`.
7. **`PhaseStatus.PASS_RECOVERED` enum value** — Already implemented per out-of-scope notes. `write_phase_result()` and all other `PhaseStatus` switch sites depend on this existing enum member.
8. **`uv` toolchain** — All test execution and linting commands are run via `uv run`. Required for DoD verification (`uv run pytest`, `uv run ruff check`, `uv run ruff format --check`).

---

## Success Criteria

1. **SC-001 (DoD-1)**: All 9 new tests pass: `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` exits with code 0, reporting 9 passed (T04.01–T04.09).
2. **SC-002 (DoD-2)**: Full test suite passes with zero regressions: `uv run pytest tests/ -v --tb=short` exits with code 0, reporting ≥629 tests passed.
3. **SC-003 (DoD-3 + DoD-4)**: Static analysis clean: `uv run ruff check` and `uv run ruff format --check` both exit 0 on all 7 modified files with no violations reported.
4. **SC-004 (DoD-5)**: Manual smoke test passes — a sprint phase that exhausts its context window recovers with status `PASS_RECOVERED` (not `ERROR`) and the recovered status is visible in screen output.
5. **SC-005 (token reduction)**: The `tasklist-index.md` file (~14K tokens) is not accessible to phase subprocesses via `@` file resolution when isolation wiring is active, reducing per-phase token baseline by approximately 14K tokens.

---

## Open Questions

1. **OQ-001**: Does `ClaudeProcess` accept a `scoped_work_dir` parameter today, or does this need to be added alongside `env_vars`? The PRD references passing `scoped_work_dir` to `ClaudeProcess` (S3-R02) but the S3-R07 requirement only explicitly adds `env_vars`. The relationship between `scoped_work_dir` and `env_vars` (i.e., whether the isolation dir is set as a working directory env var or as a subprocess `cwd`) is not fully specified.

2. **OQ-002**: S3-R05 references `config.release_name` — does this attribute exist on `SprintConfig`? If the release name is derived from the release directory name as a fallback, what is the exact fallback logic and is it already implemented?

3. **OQ-003**: The `env_vars` chain (S3-R07 → S3-R08) describes merging into the environment "after the `os.environ.copy()` call." Is the intent to *set* env vars that override the system environment, or to *add* vars only if not already present? Precedence semantics should be clarified.

4. **OQ-004**: FIX-2-R02 states "add `config: SprintConfig` as a field to `DiagnosticBundle` ... with a `None` default for backward compatibility." If `config` is `None` at runtime (legacy call sites), does `FailureClassifier.classify()` fall back to the old hardcoded path, raise an error, or skip path resolution entirely? The fallback behavior for `None` config is unspecified.

5. **OQ-005**: T04.08 (`test_logger_pass_recovered_screen_output`) and T04.09 (`test_classifier_uses_config_output_file`) are listed in the test requirements but do not appear in the `TestFixesAndDiagnostics` class table with a full `test_determine_phase_status_passes_error_file` entry for S2-E. The S2-E plumbing (FR-010–FR-012) lacks a dedicated test case. Should a T04.10 be added?

6. **OQ-006**: The PRD specifies the isolation directory contains "exactly one file matching `phase.file.name`" (T04.01). Does the subprocess receive the isolation dir as its working directory (`cwd`), as a `CLAUDE_WORK_DIR` env var, or through another mechanism? The exact propagation path determines whether `shutil.copy2()` alone is sufficient or whether additional symlinking/path rewriting is needed.

7. **OQ-007**: S3-C removes the `.isolation/` base directory at startup unconditionally. If two sprint runs are operating concurrently on the same `config.results_dir` (e.g., parallel worktree sessions), this cleanup would corrupt the sibling run. Is concurrent execution on the same results directory a supported scenario, and if so, should the orphan cleanup be made conditional (e.g., only remove dirs older than N seconds)?
