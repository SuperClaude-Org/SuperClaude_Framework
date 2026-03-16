---
validation_milestones: 16
interleave_ratio: "1:2"
---

# Test Strategy: Sprint Context Resilience (v2.25.7-phase8)

## 1. Validation Milestones Mapped to Roadmap Phases

Each roadmap milestone has a corresponding validation gate. Gates are cumulative — a phase's gate must pass before the next phase begins.

| Milestone | Phase | Description | Gate Type | Blocking? |
|-----------|-------|-------------|-----------|-----------|
| **VM-1.0** | Phase 1 | OQ-006 mechanism confirmed | Manual verification + documented decision | Yes |
| **VM-1.1** | Phase 1 | `env_vars` on `ClaudeProcess.__init__()` | Unit test + call-site grep | Yes |
| **VM-1.2** | Phase 1 | `env_vars` on `build_env()` with merge semantics | Unit test | Yes |
| **VM-1.3** | Phase 1 | End-to-end env propagation chain traceable | Integration test + existing suite pass | Yes |
| **VM-2.1** | Phase 2 | Orphan cleanup executes before phase loop | Unit test (T04.04) | Yes |
| **VM-2.2** | Phase 2 | Isolation dir created with exactly one file | Unit test (T04.01) | Yes |
| **VM-2.3** | Phase 2 | Isolation dir removed on success and failure | Unit tests (T04.02, T04.03) | Yes |
| **VM-2.4** | Phase 2 | Subprocess file resolution constrained per M1.0 mechanism | Integration test | Yes |
| **VM-3.1** | Phase 3 | `## Sprint Context` section in `build_prompt()` | Unit test (T04.05) | Yes |
| **VM-3.2** | Phase 3 | `detect_prompt_too_long()` scans `error_path` | Unit tests (T04.06, T04.07) | Yes |
| **VM-3.3** | Phase 3 | `_determine_phase_status()` plumbs `error_file` | Unit test (T04.10) | Yes |
| **VM-4.1** | Phase 4 | `PASS_RECOVERED` routes to INFO branch | Unit test (T04.08) | Yes |
| **VM-4.2** | Phase 4 | `FailureClassifier` uses config-driven path | Unit test (T04.09) | Yes |
| **VM-4.3** | Phase 4 | M4.4 grep audit complete — zero open `PASS_RECOVERED` parity gaps | Manual grep audit | Yes |
| **VM-5**   | Phase 5 | Full suite: 10 new tests pass, zero regressions, ruff clean | `uv run pytest` + ruff | Yes |
| **VM-6.1** | Phase 6 | `PASS_RECOVERED` visible in manual smoke output | Manual smoke (SC-004) | Yes (hard gate) |
| **VM-6.2** | Phase 6 | `tasklist-index.md` unreachable in isolated subprocess | Manual smoke (SC-005) | Yes (hard gate) |

> VM-6.1 and VM-6.2 are hard blocking gates per the roadmap's architectural ruling. The branch does not merge until both pass, regardless of schedule pressure.

---

## 2. Test Categories

### 2.1 Unit Tests

**Scope**: Single function or method in isolation, using mocks for filesystem and subprocess boundaries.

**Placement**: All unit tests for Phase 8 land in `tests/sprint/test_phase8_halt_fix.py` as three test classes.

| Test ID | Function | File | What It Verifies |
|---------|----------|------|------------------|
| T-ENV-01 | `ClaudeProcess.__init__()` | `sprint/process.py` | `env_vars` kwarg stored as `_extra_env_vars`; `None` default leaves behavior unchanged |
| T-ENV-02 | `build_env()` | `pipeline/process.py` | `env_vars` dict merged after `os.environ.copy()` with override semantics; `None` = no change |
| T-ENV-03 | `build_env()` | `pipeline/process.py` | Existing positional call sites remain valid with no signature break |
| T04.01 | `execute_sprint()` | `executor.py` | Isolation dir exists at subprocess launch; contains exactly one file matching `phase.file.name` |
| T04.02 | `execute_sprint()` | `executor.py` | Isolation dir removed after phase completes with exit_code=0 |
| T04.03 | `execute_sprint()` | `executor.py` | Isolation dir removed after phase fails with exit_code=1 (`finally` block confirmed) |
| T04.04 | `execute_sprint()` | `executor.py` | Pre-existing `.isolation/` base removed before phase loop starts |
| T04.05 | `build_prompt()` | `prompt.py` | Output contains `## Sprint Context`, phase number, `"Do not seek additional index files"` |
| T04.06 | `detect_prompt_too_long()` | `monitor.py` | Returns `True` when pattern found in last 10 lines of `error_path`; output file is clean |
| T04.07 | `detect_prompt_too_long()` | `monitor.py` | `error_path=None` behavior identical to current implementation; no exception raised |
| T04.08 | `SprintLogger.write_phase_result()` | `logger.py` | `PASS_RECOVERED` routes to INFO branch; captured log level is INFO not ERROR |
| T04.09 | `FailureClassifier.classify()` | `diagnostics.py` | Calls `bundle.config.output_file(phase)` (mock assertion); no hardcoded path string constructed |
| T04.10 | `_determine_phase_status()` | `executor.py` | Passes `error_path=error_file` to `detect_prompt_too_long()` when `error_file` is not None |
| T-DIAG-01 | `DiagnosticBundle` | `diagnostics.py` | `config=None` default: existing call sites compile; deprecation warning logged when `config is None` |
| T-DIAG-02 | `DiagnosticBundle` | `diagnostics.py` | `config` supplied: `FailureClassifier` uses config-driven path with no deprecation warning |

**Mocking requirements for all unit tests**:
- `shutil.copy2`, `shutil.rmtree` — verify call arguments without filesystem side effects
- `ClaudeProcess` subprocess launch — assert `env` / `cwd` values without spawning processes
- `SprintLogger` screen output — capture log records to assert level (INFO vs ERROR)

### 2.2 Integration Tests

**Scope**: Multiple components wired together; filesystem operations use real `tmp_path` dirs (no subprocess spawning).

**Placement**: `tests/sprint/test_phase8_integration.py`

| Test ID | Components | What It Verifies |
|---------|-----------|------------------|
| T-INT-01 | `ClaudeProcess` + `build_env()` | `env_vars` value set in constructor is present in `build_env()` output dict; no value dropped in propagation chain |
| T-INT-02 | `execute_sprint()` + isolation dirs | Real `tmp_path`; isolation dir at `results_dir/.isolation/phase-N/`; orphan cleanup runs before phase loop on real filesystem |
| T-INT-03 | `execute_sprint()` + `_determine_phase_status()` + `detect_prompt_too_long()` | `error_file` path plumbed end-to-end; pattern in error file produces `PROMPT_TOO_LONG` status |
| T-INT-04 | `build_prompt()` + `SprintConfig` | No `AttributeError` when `config.release_name` is None; fallback to `release_dir.name` used |
| T-INT-05 | `FailureClassifier` + `DiagnosticBundle` + `SprintConfig` | Config-driven `output_file()` path matches expected; `None` config falls back with deprecation warning |

**Integration test environment**: `pytest`'s `tmp_path` fixture for real paths; subprocess spawn boundary patched; `uv run pytest tests/sprint/ -v -m integration`.

### 2.3 End-to-End (E2E) Tests

**Scope**: Full `execute_sprint()` flow with synthetic sprint config and stubbed subprocess. No live API calls.

**Placement**: `tests/sprint/test_phase8_e2e.py`

| Test ID | Scenario | Assertion |
|---------|----------|-----------|
| T-E2E-01 | Single phase, success | Isolation dir created → subprocess spawned with correct env → dir removed; status is `PASS` |
| T-E2E-02 | Single phase, context exhaustion | Subprocess writes `PROMPT_TOO_LONG_PATTERN` to error file → status is `PASS_RECOVERED`; isolation dir removed; screen output shows INFO-level status |
| T-E2E-03 | Single phase, failure | Subprocess returns exit_code=1 → isolation dir removed in `finally`; status is `FAIL` |
| T-E2E-04 | Multi-phase sprint with stale `.isolation/` present | Orphan cleanup runs → all phases execute → no `.isolation/` tree remains at completion |
| T-E2E-05 | `tasklist-index.md` inaccessible in isolation | Subprocess environment or `cwd` scoped to isolation dir; `@tasklist-index.md` reference cannot resolve (mechanism per VM-1.0) |

> **T-E2E-05 is mechanism-dependent.** The test can only be fully specified after VM-1.0 (OQ-006) is resolved. If isolation uses `CLAUDE_WORK_DIR`, this is an env-dict assertion. If isolation uses subprocess `cwd`, it requires spawning a safe real subprocess.

### 2.4 Acceptance Tests

**Scope**: Behavioral verification against the five documented success criteria. SC-004 and SC-005 are manual.

| Test ID | Criterion | Method | Pass Condition |
|---------|-----------|--------|----------------|
| T-ACC-01 | SC-001: 10 new tests pass | `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` | Exit 0, 10 passed |
| T-ACC-02 | SC-002: Zero regressions | `uv run pytest tests/ -v --tb=short` | Exit 0, ≥638 passed |
| T-ACC-03 | SC-003: Static analysis clean | `uv run ruff check && uv run ruff format --check` | Exit 0, zero violations |
| T-ACC-04 | SC-004: `PASS_RECOVERED` screen-visible | Manual: trigger context exhaustion on a phase approaching prompt limits | `PASS_RECOVERED` (not `ERROR`) visible in operator screen output |
| T-ACC-05 | SC-005: ~14K token reduction per phase | Manual: verify `tasklist-index.md` unreachable in isolated subprocess | File not accessible via `@` reference; per-phase token baseline reduced by ~14K |

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1 test written per 2 implementation steps (1:2). Tests for each component are written immediately after that component is implemented — not deferred to Phase 5.

```
Phase 1: OQ-006 Gate + env_vars
  Step 1: Investigate OQ-006 (no test — verification only; document decision)
  Step 2: Implement env_vars on ClaudeProcess.__init__()
    → Write T-ENV-01 immediately after
  Step 3: Implement env_vars on build_env()
    → Write T-ENV-02, T-ENV-03 immediately after
  Step 4: Trace end-to-end propagation chain
    → Write T-INT-01 to confirm chain
  Gate G1: Run all Phase 1 tests before Phase 2 begins

Phase 2: Isolation Lifecycle
  Step 1: Implement orphan cleanup (startup shutil.rmtree)
    → Write T04.04 immediately after
  Step 2: Implement per-phase isolation dir + shutil.copy2
    → Write T04.01 immediately after
  Step 3: Implement finally-block teardown
    → Write T04.02, T04.03 immediately after
  Step 4: Wire isolation mechanism to subprocess (cwd or env per VM-1.0)
    → Write T-INT-02 immediately after
  Gate G2: Run all Phase 1+2 tests; Phase 3 and Phase 4 may now run in parallel

Phase 3: Prompt Resilience + Context Header   [parallel with Phase 4]
  Step 1: Implement ## Sprint Context in build_prompt()
    → Write T04.05, T-INT-04 immediately after
  Step 2: Implement error_path on detect_prompt_too_long()
    → Write T04.06, T04.07 immediately after
  Step 3: Implement error_file plumbing in _determine_phase_status()
    → Write T04.10, T-INT-03 immediately after
  Gate G3: Run all Phase 3 tests

Phase 4: Diagnostics + Status Fixes          [parallel with Phase 3]
  Step 1: Add PASS_RECOVERED to INFO branch in write_phase_result()
    → Write T04.08 immediately after
  Step 2: Add config field to DiagnosticBundle
    → Write T-DIAG-01, T-DIAG-02 immediately after
  Step 3: Update FailureClassifier to use config-driven path
    → Write T04.09, T-INT-05 immediately after
  Step 4: Run M4.4 grep audit; document all PASS_RECOVERED parity gaps
  Gate G4: Run all Phase 4 tests; confirm M4.4 audit complete

Phase 5: Full Suite Validation
  Consolidate all tests into test_phase8_halt_fix.py
  Write T-E2E-01 through T-E2E-05 in test_phase8_e2e.py
  Run acceptance gates T-ACC-01 through T-ACC-03
  Gate G5: All pass before Phase 6 begins

Phase 6: Smoke + Hard Gate
  Execute T-ACC-04, T-ACC-05 manually
  Document go/no-go with evidence
  Gate G6: Both pass before merge
```

**Rationale for 1:2 ratio**: Each change is XS or S in isolation (per extraction complexity assessment). Inline test writing is low-friction and catches wiring gaps immediately. Deferring all tests to Phase 5 risks integration surprises where debugging cost is higher.

---

## 4. Risk-Based Test Prioritization

Ordered by severity × discoverability. Silent failures rank higher than loud ones.

### P0 — Write First, Block on Failure

| Risk | Test(s) | Why Critical |
|------|---------|-------------|
| **H2: Silent isolation failure** | T04.01, T-E2E-05 | Sprint can merge while `tasklist-index.md` remains accessible with no alarm; this is the primary system objective |
| **H1: Context exhaustion recurrence** | T-E2E-02, T04.06 | Primary functional objective; prompt-too-long detection on error path is the recovery mechanism |
| **M2: env_vars propagation gap** | T-ENV-02, T-INT-01 | Isolation wiring is silently ineffective if the env chain is broken mid-pipeline |

### P1 — Write During Phase Implementation

| Risk | Test(s) | Why Important |
|------|---------|--------------|
| **M1: Cleanup failure masks phase errors** | T04.02, T04.03 | `finally` block correctness; stale dirs degrade subsequent runs silently |
| **M3: Signature changes break callers** | T-ENV-03, T04.07, T-DIAG-01 | Keyword-only `None` defaults must not break existing positional call sites |
| **L1: PASS_RECOVERED parity gaps** | T04.08, M4.4 grep audit | Policy invariant; gaps cause silent INFO→ERROR reclassification in logs |

### P2 — Write Before Phase 5 Gate

| Risk | Test(s) | Why Deferrable |
|------|---------|---------------|
| **L2: DiagnosticBundle config ambiguity** | T-DIAG-02, T04.09 | Fallback path with deprecation warning is specified; failure is visible (not silent) |
| **M4: Concurrent sprint run corruption** | None (unsupported scenario) | Not a supported use case; defer PID-stamped isolation roots to S4 |

---

## 5. Acceptance Criteria Per Milestone

### VM-1.0 (OQ-006 Resolved)
- Written decision document: `CLAUDE_WORK_DIR` confirmed OR subprocess `cwd` named as the isolation mechanism
- If `cwd` is the mechanism: Phase 2 timeline re-estimated before any Phase 2 code is written
- T04.01 test skeleton written against the confirmed mechanism

### VM-1.1 / VM-1.2 (env_vars Plumbing)
- `ClaudeProcess.__init__()` signature: `*, env_vars: dict[str, str] | None = None`
- `build_env()` signature: `*, env_vars: dict[str, str] | None = None`
- T-ENV-01, T-ENV-02, T-ENV-03 all pass
- `uv run pytest tests/ -x` exits 0 (all existing call sites compile unchanged)

### VM-1.3 (End-to-End Propagation)
- T-INT-01 passes: value set in constructor is present in `build_env()` output dict
- `uv run pytest tests/` exits 0 with zero new failures

### VM-2.1 (Orphan Cleanup)
- T04.04 passes: `shutil.rmtree(results_dir / ".isolation", ignore_errors=True)` called before any phase subprocess launch
- Confirmed via mock assertion on `shutil.rmtree` call order

### VM-2.2 (Isolation Dir Created)
- T04.01 passes: `results_dir/.isolation/phase-{N}/` exists at subprocess launch time
- `len(list(isolation_dir.iterdir())) == 1`; filename matches `phase.file.name`
- `shutil.copy2` called with correct source and destination (mock assertion)

### VM-2.3 (Isolation Dir Cleaned)
- T04.02 passes: isolation dir absent after exit_code=0
- T04.03 passes: isolation dir absent after exit_code=1 (via `finally`)
- `shutil.rmtree(isolation_dir, ignore_errors=True)` call confirmed in both paths

### VM-2.4 (Subprocess Constrained)
- T-INT-02 passes: subprocess spawn arguments include isolation dir via mechanism confirmed at VM-1.0
- T-E2E-05 written and passing per confirmed mechanism

### VM-3.1 (Sprint Context Header)
- T04.05 passes: `build_prompt()` output contains `## Sprint Context`, `f"Phase {N} of {M}"`, and `"Do not seek additional index files"`
- T-INT-04 passes: no `AttributeError` when `config.release_name` is None (fallback to `release_dir.name`)

### VM-3.2 (error_path Detection)
- T04.06 passes: `detect_prompt_too_long(output_path=clean_file, error_path=file_with_pattern)` returns `True`
- T04.07 passes: `detect_prompt_too_long(output_path=anything, error_path=None)` is identical to current behavior; no exception

### VM-3.3 (error_file Plumbing)
- T04.10 passes: `_determine_phase_status(error_file=some_path)` calls `detect_prompt_too_long(error_path=some_path)` (mock assertion on call keyword argument)

### VM-4.1 (PASS_RECOVERED INFO Routing)
- T04.08 passes: `write_phase_result(PhaseStatus.PASS_RECOVERED)` emits at INFO level; captured log record `levelname == "INFO"`

### VM-4.2 (FailureClassifier Config-Driven Path)
- T04.09 passes: mock confirms `bundle.config.output_file(phase)` is called; no hardcoded string path constructed
- T-DIAG-01 passes: `DiagnosticBundle(config=None)` logs deprecation warning and does not raise; falls back to legacy path

### VM-4.3 (M4.4 Grep Audit)
- `grep -r "PhaseStatus.PASS[^_]"` across all switch/conditional sites returns only results that also handle `PASS_RECOVERED`
- Audit results documented; zero open parity gaps remain

### VM-5 (Full Suite Gate)
- `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` → 10 passed, exit 0
- `uv run pytest tests/ -v --tb=short` → ≥638 passed, 0 failed, exit 0
- `uv run ruff check` → exit 0, zero violations
- `uv run ruff format --check` → exit 0
- T-E2E-01 through T-E2E-04 pass; T-E2E-05 passes per confirmed mechanism

### VM-6.1 (PASS_RECOVERED Smoke — Hard Gate)
- Manual trigger: run a sprint phase that produces `PROMPT_TOO_LONG_PATTERN` in its error file
- Screen output shows `PASS_RECOVERED` — not `ERROR` or `FAIL`
- No exception propagated to the operator

### VM-6.2 (Isolation Smoke — Hard Gate)
- Manual trigger: run a sprint with isolation active; attempt `@tasklist-index.md` reference from within a phase subprocess
- Reference fails or returns empty (file not present in isolation dir)
- No `.isolation/phase-*` directories remain after sprint completion
- Token count for phase reduced vs pre-isolation baseline by ~14K

---

## 6. Quality Gates Between Phases

Each gate is a hard stop. The next phase does not begin until all criteria pass.

### Gate G1 (End of Phase 1 → Before Phase 2)

- [ ] VM-1.0: OQ-006 resolved; mechanism decision documented
- [ ] VM-1.1: T-ENV-01 passes
- [ ] VM-1.2: T-ENV-02, T-ENV-03 pass
- [ ] VM-1.3: T-INT-01 passes; `uv run pytest tests/ -x` exits 0

**Rationale**: Phase 2 isolation code must be written against the confirmed mechanism. Phase 2 is explicitly gated on M1.0 in the roadmap — this gate enforces that rule.

### Gate G2 (End of Phase 2 → Enables Phase 3+4 parallel work)

- [ ] VM-2.1: T04.04 passes
- [ ] VM-2.2: T04.01 passes
- [ ] VM-2.3: T04.02, T04.03 pass
- [ ] VM-2.4: T-INT-02 passes
- [ ] `uv run pytest tests/ -x` exits 0

**Note**: Phases 3 and 4 may proceed concurrently after G2. Phase 3 has no dependency on Phase 2, but Phase 2 must be complete and passing before Phase 5.

### Gate G3 (End of Phase 3)

- [ ] VM-3.1: T04.05, T-INT-04 pass
- [ ] VM-3.2: T04.06, T04.07 pass
- [ ] VM-3.3: T04.10, T-INT-03 pass
- [ ] `uv run pytest tests/ -x` exits 0

### Gate G4 (End of Phase 4)

- [ ] VM-4.1: T04.08 passes
- [ ] VM-4.2: T04.09, T-DIAG-01, T-DIAG-02 pass
- [ ] VM-4.3: M4.4 grep audit complete; zero open `PASS_RECOVERED` parity gaps
- [ ] `uv run pytest tests/ -x` exits 0

### Gate G5 (End of Phase 5 → Before Phase 6)

- [ ] T-ACC-01: `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` → 10 passed, exit 0
- [ ] T-ACC-02: `uv run pytest tests/ -v --tb=short` → ≥638 passed, exit 0
- [ ] T-ACC-03: `uv run ruff check && uv run ruff format --check` → exit 0
- [ ] T-E2E-01 through T-E2E-05 pass

### Gate G6 (End of Phase 6 → Merge Gate — Hard Blocking)

- [ ] T-ACC-04 (SC-004): `PASS_RECOVERED` visible in manual smoke screen output
- [ ] T-ACC-05 (SC-005): `tasklist-index.md` mechanically unreachable; ~14K token reduction per phase confirmed
- [ ] Go/no-go documented with evidence
- [ ] Final diff review of all 7 modified files complete

**This gate cannot be waived under schedule pressure.** Risk H2 (silent isolation failure) means the sprint can pass CI while delivering zero isolation benefit. G6 is the only mechanism that catches this. Per the roadmap's architectural ruling: the branch does not merge until both SC-004 and SC-005 are manually verified.

---

## Appendix: Test File Structure

```
tests/sprint/
├── test_phase8_halt_fix.py          # Required by roadmap (Phase 5)
│   ├── TestIsolationWiring          # T04.01–T04.04, T-ENV-01–T-ENV-03
│   ├── TestPromptAndContext         # T04.05–T04.07
│   └── TestFixesAndDiagnostics     # T04.08–T04.10, T-DIAG-01–T-DIAG-02
│
├── test_phase8_integration.py       # Integration tests
│   └── T-INT-01 through T-INT-05
│
└── test_phase8_e2e.py               # E2E tests
    ├── T-E2E-01: success path
    ├── T-E2E-02: context exhaustion / PASS_RECOVERED
    ├── T-E2E-03: failure path
    ├── T-E2E-04: orphan cleanup multi-phase
    └── T-E2E-05: tasklist-index.md inaccessible (mechanism-dependent)
```

**Constraints**:
- All execution via `uv run pytest` (UV-only per project CLAUDE.md)
- No new third-party test dependencies (stdlib + pytest + existing fixtures only)
- All new test files target the `v2.25.7-phase8` branch
- T-E2E-05 final form is specified after VM-1.0 documents the OQ-006 resolution
