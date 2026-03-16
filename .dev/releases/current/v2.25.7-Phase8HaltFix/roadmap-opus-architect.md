

---
spec_source: v2.25.7-phase8-sprint-context-resilience-prd.md
complexity_score: 0.62
primary_persona: architect
---

# Project Roadmap: Sprint Context Resilience (v2.25.7-phase8)

## 1. Executive Summary

This roadmap addresses **27 requirements** (22 functional, 5 non-functional) across 5 subsystems to harden the sprint executor's context resilience. The core problem: phase subprocesses can resolve `tasklist-index.md` via `@` references, wasting ~14K tokens per phase and contributing to context exhaustion failures.

The solution introduces **filesystem isolation** (per-phase scoped directories), **environment variable propagation** for subprocess control, a **sprint context header** to orient phases without index files, and **bug fixes** for `PASS_RECOVERED` routing and `FailureClassifier` path resolution.

**Scope**: 7 files modified, 9 new tests, zero new dependencies. All changes are backward-compatible via keyword-only parameters with `None` defaults.

**Key architectural decision**: Isolation via directory scoping (copy phase file into temporary directory, pass as working context) rather than file-level filtering or prompt rewriting. This is the correct approach — it's simple, hermetic, and testable.

## 2. Phased Implementation Plan

### Phase 1: Foundation & Environment Plumbing (P0 Critical Path)

**Goal**: Establish the env_vars propagation chain that all isolation work depends on.

**Requirements**: FR-004, FR-005

**Tasks**:
1. Add `env_vars: dict[str, str] | None = None` keyword-only parameter to `ClaudeProcess.__init__()` in `src/superclaude/cli/sprint/process.py`
2. Store as `self._extra_env_vars` and wire through to `build_env()` call
3. Add `env_vars: dict[str, str] | None = None` keyword-only parameter to `build_env()` in `src/superclaude/cli/pipeline/process.py`
4. Implement merge semantics: `env.update(env_vars)` after `os.environ.copy()` (override, not add-if-missing — see OQ-003 resolution below)
5. Verify all existing call sites remain valid (keyword-only with `None` default = no breakage)

**Milestone**: `build_env()` can accept and propagate arbitrary environment variables to subprocesses.

**Risk gate**: Run `uv run pytest tests/` — zero regressions (NFR-001).

### Phase 2: Isolation Wiring (P0 Critical Path)

**Goal**: Create per-phase isolation directories and pass them to subprocesses.

**Requirements**: FR-001, FR-002, FR-003

**Tasks**:
1. In `execute_sprint()`, before spawning each phase subprocess:
   - Create `config.results_dir / ".isolation" / f"phase-{phase.number}"`
   - Copy phase file via `shutil.copy2(phase.file, isolation_dir / phase.file.name)`
2. Pass `scoped_work_dir=isolation_dir` to `ClaudeProcess` (resolve OQ-001: use `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` if `scoped_work_dir` doesn't exist as a parameter)
3. In `finally` block: `shutil.rmtree(phase_isolation_dir, ignore_errors=True)`
4. Add startup orphan cleanup (FR-006): `shutil.rmtree(config.results_dir / ".isolation", ignore_errors=True)` before the phase loop

**Milestone**: Phase subprocesses execute within isolated directories containing only their phase file. `tasklist-index.md` is unreachable via `@` resolution.

**Dependencies**: Phase 1 complete (env_vars chain functional).

### Phase 3: Sprint Context Header (P0/P1)

**Goal**: Provide subprocess orientation without index file access.

**Requirements**: FR-007, FR-008

**Tasks**:
1. Add `## Sprint Context` section to `build_prompt()` output containing:
   - Sprint name (`config.release_name` or fallback to `config.release_dir.name` — resolve OQ-002)
   - Phase N of M
   - Artifact root path and results directory
   - Prior-phase artifact directories list
2. Add instruction: `"All task details are in the phase file. Do not seek additional index files."`

**Milestone**: `build_prompt()` output contains complete orientation context. Test FR-020 validates.

### Phase 4: Error Path & Diagnostics Fixes (P1)

**Goal**: Fix prompt-too-long detection and failure classification paths.

**Requirements**: FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015

**Tasks**:
1. **`detect_prompt_too_long()` extension** (FR-009):
   - Add `error_path: Path | None = None` keyword-only parameter
   - Scan `error_path` for `PROMPT_TOO_LONG_PATTERN` using same last-10-lines logic
   - Return `True` if found in either file
2. **`_determine_phase_status()` plumbing** (FR-010–FR-012):
   - Add `error_file: Path | None = None` parameter
   - Pass `config.error_file(phase)` at call site
   - Forward to `detect_prompt_too_long(error_path=error_file)`
3. **Logger `PASS_RECOVERED` routing** (FR-013):
   - Add `PhaseStatus.PASS_RECOVERED` to INFO routing branch in `write_phase_result()` at line 136
   - Grep all `PhaseStatus.PASS` switch sites for completeness (NFR-005)
4. **`FailureClassifier` path fix** (FR-014–FR-015):
   - Add `config: SprintConfig | None = None` to `DiagnosticBundle` with `None` default
   - Replace hardcoded path with `bundle.config.output_file(bundle.phase_result.phase)`
   - Fallback: if `config is None`, use existing hardcoded path (resolve OQ-004)

**Milestone**: Error detection scans both output and error files. `PASS_RECOVERED` appears in screen output. `FailureClassifier` uses canonical path resolution.

### Phase 5: Test Suite & Validation (P0/P1)

**Goal**: All 9 new tests pass, full suite green, static analysis clean.

**Requirements**: FR-016–FR-022, NFR-001–NFR-005

**Tasks**:
1. Create `tests/sprint/test_phase8_halt_fix.py` with 3 test classes:
   - `TestIsolationWiring`: T04.01–T04.04
   - `TestPromptAndContext`: T04.05–T04.07
   - `TestFixesAndDiagnostics`: T04.08–T04.09 (and T04.10 if added per OQ-005)
2. Implement each test case per specification
3. Run full suite: `uv run pytest tests/ -v --tb=short` — ≥629 + 9 new = ≥638 pass
4. Run linting: `uv run ruff check` and `uv run ruff format --check` — zero violations
5. `PASS_RECOVERED` consistency audit: grep all `PhaseStatus.PASS` references, verify parity

**Milestone**: SC-001 through SC-003 satisfied. All gates green.

### Phase 6: Smoke Test & Merge Readiness

**Goal**: Manual validation and merge preparation.

**Requirements**: SC-004, SC-005

**Tasks**:
1. Manual smoke test: trigger context exhaustion on a sprint phase, verify `PASS_RECOVERED` status and screen output
2. Verify token reduction: confirm `tasklist-index.md` is not accessible in isolated subprocess
3. Final diff review against all 7 modified files
4. Prepare merge to `v2.25.7-phase8` branch

**Milestone**: SC-004 and SC-005 satisfied. Ready for merge.

## 3. Risk Assessment & Mitigation

| Risk | Severity | Phase Affected | Mitigation |
|------|----------|---------------|------------|
| **RISK-001**: Isolation cleanup failure (stale dirs) | Medium | 2 | `ignore_errors=True` on all `shutil.rmtree` calls. Startup orphan cleanup as safety net. |
| **RISK-002**: env_vars propagation gap | Medium | 1–2 | T04.01 validates end-to-end. Add explicit unit test for env propagation if not covered. |
| **RISK-003**: `PASS_RECOVERED` omission elsewhere | Low | 4 | Codebase-wide grep for `PhaseStatus.PASS` before merge. NFR-005 enforces policy. |
| **RISK-004**: DiagnosticBundle backward compat | Low | 4 | `None` default per NFR-002. Fallback to hardcoded path when `config is None`. |
| **RISK-005**: Signature change regressions | Medium | 1, 4 | All new params are keyword-only after `*`. Existing positional calls unaffected. Run full suite after each phase. |
| **RISK-006**: Context exhaustion recurrence (S4 deferred) | High | Post-merge | Monitor phase token usage. Keep deliverables ≤8/phase. S4 triggered on second exhaustion. |
| **NEW: Concurrent sprint run corruption** (OQ-007) | Medium | 2 | Document that concurrent runs on same `results_dir` are unsupported. Consider PID-stamped isolation dirs in S4. |

**Highest priority risk**: RISK-006 (context exhaustion recurrence). This roadmap reduces token waste by ~14K/phase but does not eliminate exhaustion for large phases. The team must monitor and be ready to fast-track S4 (artifact batching).

## 4. Resource Requirements & Dependencies

### Files Modified (7 total)

| File | Changes | Phase |
|------|---------|-------|
| `src/superclaude/cli/sprint/process.py` | `env_vars` parameter on `ClaudeProcess.__init__()` | 1 |
| `src/superclaude/cli/pipeline/process.py` | `env_vars` parameter on `build_env()` | 1 |
| `src/superclaude/cli/sprint/executor.py` | Isolation wiring, orphan cleanup, error_file plumbing | 2, 4 |
| `src/superclaude/cli/sprint/prompt.py` | `## Sprint Context` header in `build_prompt()` | 3 |
| `src/superclaude/cli/sprint/monitor.py` | `error_path` parameter on `detect_prompt_too_long()` | 4 |
| `src/superclaude/cli/sprint/logger.py` | `PASS_RECOVERED` routing fix | 4 |
| `src/superclaude/cli/sprint/diagnostics.py` | `FailureClassifier` path fix, `DiagnosticBundle.config` | 4 |

### New Files (1)

| File | Purpose | Phase |
|------|---------|-------|
| `tests/sprint/test_phase8_halt_fix.py` | 9+ test cases for all phase 8 requirements | 5 |

### External Dependencies

All dependencies are stdlib (`shutil`, `pathlib`, `os`, `re`, `datetime`) — already imported in target files. No new third-party packages. `uv` toolchain required for all execution.

### Internal Dependencies (Critical Path)

```
Phase 1 (env_vars) ──→ Phase 2 (isolation) ──→ Phase 5 (tests)
                                                     ↑
Phase 3 (header)  ─────────────────────────────────→ │
Phase 4 (fixes)   ─────────────────────────────────→ │
                                                     ↓
                                               Phase 6 (smoke)
```

Phases 3 and 4 are independent of each other and can be executed in parallel after Phase 1.

## 5. Success Criteria & Validation

| Criterion | Validation Command | Expected |
|-----------|-------------------|----------|
| **SC-001**: 9 new tests pass | `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` | 9 passed, exit 0 |
| **SC-002**: Zero regressions | `uv run pytest tests/ -v --tb=short` | ≥638 passed, exit 0 |
| **SC-003**: Static analysis clean | `uv run ruff check && uv run ruff format --check` | Exit 0, zero violations |
| **SC-004**: Smoke test | Manual: trigger context exhaustion | `PASS_RECOVERED` in screen output |
| **SC-005**: Token reduction | Verify `tasklist-index.md` unreachable in isolation | ~14K token reduction per phase |

**Validation approach**: Run the full validation suite after each implementation phase (not just at the end). This catches regressions early and keeps the feedback loop tight.

## 6. Timeline Estimates Per Phase

| Phase | Description | Effort | Dependencies | Parallelizable |
|-------|-------------|--------|-------------|----------------|
| 1 | Environment plumbing | XS (2 files, 2 params) | None | — |
| 2 | Isolation wiring | S (1 file, lifecycle logic) | Phase 1 | — |
| 3 | Sprint context header | XS (1 file, string formatting) | None | Yes (with Phase 4) |
| 4 | Error path & diagnostics | S (4 files, targeted patches) | None | Yes (with Phase 3) |
| 5 | Test suite | S (1 file, 9 tests with mocking) | Phases 1–4 | — |
| 6 | Smoke test & merge | XS (manual validation) | Phase 5 | — |

**Critical path**: Phase 1 → Phase 2 → Phase 5 → Phase 6

**Parallel opportunity**: Phases 3 and 4 can proceed concurrently, and both can start as soon as Phase 1 completes (Phase 3 has no dependency on Phase 1, Phase 4 has no dependency on Phase 1).

## 7. Open Questions Resolution Recommendations

| OQ | Recommendation | Rationale |
|----|---------------|-----------|
| OQ-001 | Use `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` rather than adding a separate `scoped_work_dir` param | Simpler — reuses the env_vars mechanism being built. Verify `ClaudeProcess` respects this env var for `@` resolution. |
| OQ-002 | Implement fallback: `config.release_name or config.release_dir.name` | Safe default. Check if `release_name` exists on `SprintConfig` before coding. |
| OQ-003 | Override semantics (`env.update(env_vars)`) | The purpose is to *set* isolation-specific vars that must take effect. Add-if-missing would defeat isolation. |
| OQ-004 | Fallback to hardcoded path when `config is None` | Preserves backward compat for existing call sites. Log a deprecation warning. |
| OQ-005 | Add T04.10 for `_determine_phase_status` error_file plumbing | FR-010–FR-012 lack dedicated test coverage. 10 minutes of work for meaningful coverage. |
| OQ-006 | Confirm `CLAUDE_WORK_DIR` env var controls `@` resolution scope | Must verify before Phase 2. If not, `cwd` of subprocess is the fallback mechanism. |
| OQ-007 | Document as unsupported; defer concurrent-safety to S4 | Concurrent runs on same `results_dir` is an edge case. PID-stamped dirs add complexity not justified yet. |
