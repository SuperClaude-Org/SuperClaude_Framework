---
spec_source: v2.25.7-phase8-sprint-context-resilience-prd.md
complexity_score: 0.62
adversarial: true
---

# Sprint Context Resilience (v2.25.7-phase8) — Final Merged Roadmap

## Executive Summary

This roadmap delivers Phase 8 sprint context resilience through a controlled, moderate-complexity change set (complexity score: 0.62) spanning executor, process, pipeline, monitor, logging, diagnostics, and tests. The implementation addresses 27 requirements (22 functional, 5 non-functional) across 7 modified files with 9+ new tests and zero new dependencies.

**Core problem**: Phase subprocesses can resolve `tasklist-index.md` via `@` references, wasting ~14K tokens per phase and contributing to context exhaustion failures. The solution introduces per-phase filesystem isolation, environment variable propagation, a sprint context header to orient phases without index files, and targeted bug fixes for `PASS_RECOVERED` routing and `FailureClassifier` path resolution.

**Key architectural ruling from adversarial debate**: The isolation failure mode is *silent* — the sprint can merge, pass CI, and ship while `tasklist-index.md` remains fully accessible. This elevates the enforcement risk to High severity and mandates that Phase 6 smoke validation is a hard blocking gate, not a release-readiness check that can be deferred under schedule pressure.

**Debate synthesis outcome**: Variant B (Haiku) selected as base for its explicit architectural priorities, gated OQ-006 resolution, verifiable milestones, and high-severity framing for silent failures. Five specific improvements from Variant A (Opus) are incorporated: requirement-to-phase mapping table, T04.10 as a named test, `CLAUDE_WORK_DIR` as a named hypothesis, deprecation warning on `DiagnosticBundle.config=None`, and explicit Phase 6 blocking criteria.

**Scope**: 7 files modified, 1 new test file, zero new third-party dependencies. All changes are backward-compatible via keyword-only parameters with `None` defaults. S4-scale artifact batching remains explicitly out of scope.

**Timeline**: 4.5 working days, contingent on OQ-006 resolution confirming the env var mechanism.

---

## Architectural Priorities

1. **Enforce isolation at the subprocess boundary, not just in prompt wording.** Per-phase scoping must be mechanically enforced. Prompt instructions alone are insufficient.

2. **Preserve compatibility while extending orchestration plumbing.** All new parameters are keyword-only with safe `None` defaults. Internal path resolution consolidates around `SprintConfig`.

3. **Harden lifecycle correctness.** Cleanup is guaranteed on success, failure, and startup recovery. Recovery statuses surface consistently, especially `PASS_RECOVERED`.

4. **Keep the implementation bounded.** No new third-party dependencies. No architectural redesign beyond targeted resilience fixes. S4-scale batching remains out of scope.

---

## Phased Implementation Plan

### Phase 1: OQ-006 Verification Gate and Environment Plumbing

#### Goals

Resolve the mechanism question that all isolation work depends on, then establish the env_vars propagation chain.

**This phase cannot be shortened.** OQ-006 — whether `CLAUDE_WORK_DIR` env var or subprocess `cwd` controls `@` resolution scope — must be answered before Phase 2 isolation code is written. If OQ-006 reveals `cwd` is the correct lever, Phase 2 implementation changes significantly and the timeline must be re-estimated before coding begins.

#### Step 1: OQ-006 Verification (Phase Gate — M1.0)

1. Trace `execute_sprint()` → `ClaudeProcess` → subprocess launch boundary
2. Identify where `@` reference resolution occurs
3. Test `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` as the candidate mechanism
4. Confirm or falsify; document subprocess `cwd` as the explicit fallback if env var is ineffective
5. Validate current interfaces: `ClaudeProcess.__init__()`, `build_env()`, `execute_sprint()`
6. Perform codebase grep for all `PhaseStatus.PASS` handling sites to identify `PASS_RECOVERED` parity gaps (feeds Phase 5)

**Milestone M1.0**: OQ-006 resolved to a concrete implementation decision with explicit defaults. `CLAUDE_WORK_DIR` confirmed or `cwd` fallback named. If timeline impact is material, re-estimate Phase 2 before proceeding.

#### Step 2: Environment Propagation Implementation

**Requirements**: FR-004, FR-005

1. Add `env_vars: dict[str, str] | None = None` keyword-only parameter to `ClaudeProcess.__init__()` in `src/superclaude/cli/sprint/process.py`
2. Store as `self._extra_env_vars`, wire through to `build_env()` call
3. Add `env_vars: dict[str, str] | None = None` keyword-only parameter to `build_env()` in `src/superclaude/cli/pipeline/process.py`
4. Implement merge semantics: `env.update(env_vars)` after `os.environ.copy()` (override semantics — OQ-003 resolved)
5. Verify all existing call sites remain valid (keyword-only with `None` default = no breakage)

#### Milestones

- **M1.0**: OQ-006 resolved; implementation mechanism confirmed; timeline re-evaluated if needed
- **M1.1**: `env_vars` supported at process constructor
- **M1.2**: `env_vars` supported at environment builder
- **M1.3**: End-to-end propagation chain traceable; existing call sites unaffected

#### Timeline

**0.75 day** (0.25 for OQ-006 verification + 0.5 for env plumbing)

---

### Phase 2: Isolation Lifecycle Implementation

#### Goals

Create per-phase isolation directories and pass them to subprocesses with deterministic cleanup.

**Requirements**: FR-001, FR-002, FR-003, FR-006

**Dependency**: Phase 1 complete with M1.0 confirmed — isolation mechanism known before any Phase 2 code is written.

#### Key Actions

1. In `execute_sprint()`, add startup orphan cleanup before the phase loop:
   - `shutil.rmtree(config.results_dir / ".isolation", ignore_errors=True)`
2. Before each phase subprocess launch:
   - Create `config.results_dir / ".isolation" / f"phase-{phase.number}"`
   - Copy only `phase.file` via `shutil.copy2(phase.file, isolation_dir / phase.file.name)`
3. Pass the isolation path into the subprocess boundary using the mechanism confirmed in M1.0:
   - Primary: `env_vars={"CLAUDE_WORK_DIR": str(isolation_dir)}` if OQ-006 confirms env var controls `@` resolution
   - Fallback: subprocess `cwd=isolation_dir` if env var is ineffective
4. In per-phase `finally` block: `shutil.rmtree(isolation_dir, ignore_errors=True)`

#### Milestones

- **M2.1**: Orphan cleanup executes before phase loop
- **M2.2**: Isolation directory created per phase containing exactly one copied phase file
- **M2.3**: Isolation directory removed on both success and failure paths
- **M2.4**: Subprocess file resolution mechanically constrained to isolated input (verified against M1.0 mechanism)

#### Timeline

**1.0 day**

---

### Phase 3: Prompt Resilience and Context Header

#### Goals

Provide subprocess orientation without index file access; extend prompt-too-long detection to stderr.

**Requirements**: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012

**Parallelization**: Can proceed concurrently with Phase 4 after Phase 1 completes. No dependency on Phase 2.

#### Key Actions

1. Update `build_prompt()` to add `## Sprint Context` section containing:
   - Sprint name (`config.release_name or config.release_dir.name` — OQ-002 resolved with safe fallback)
   - Current phase N of M
   - Artifact root path and results directory
   - Prior-phase artifact directories
   - Instruction: `"All task details are in the phase file. Do not seek additional index files."`
2. Extend `detect_prompt_too_long()` with `error_path: Path | None = None`; scan `error_path` using the same last-10-lines logic; return `True` if pattern found in either file
3. Extend `_determine_phase_status()` with `error_file: Path | None = None`; forward to `detect_prompt_too_long(error_path=error_file)`
4. Update `execute_sprint()` call site to pass `config.error_file(phase)`

#### Milestones

- **M3.1**: Prompt contains `## Sprint Context` block
- **M3.2**: `detect_prompt_too_long()` accepts and scans `error_path` alongside output path
- **M3.3**: `_determine_phase_status()` passes `error_file` through to detection logic

#### Timeline

**0.5 day**

---

### Phase 4: Diagnostics and Status Consistency Fixes

#### Goals

Make outcome handling architecturally consistent across logging and diagnostics.

**Requirements**: FR-013, FR-014, FR-015

**Parallelization**: Can proceed concurrently with Phase 3 after Phase 1 completes.

#### Key Actions

1. Update `SprintLogger.write_phase_result()`:
   - Add `PhaseStatus.PASS_RECOVERED` to the INFO routing branch (same branch as `PASS` and `PASS_NO_REPORT`)
2. Add `config: SprintConfig | None = None` keyword-only parameter to `DiagnosticBundle` with `None` default
3. Update `FailureClassifier.classify()`:
   - Replace hardcoded output-file path construction with `bundle.config.output_file(bundle.phase_result.phase)`
   - If `config is None`: use existing hardcoded path as fallback **and** log a deprecation warning (adopted from Variant A — adds long-term migration value at zero cost)
4. **Named task M4.4** — PASS_RECOVERED grep audit: grep all `PhaseStatus.PASS` switch sites identified in M1.0 for `PASS_RECOVERED` parity; treat as a blocking deliverable for Phase 5

#### Milestones

- **M4.1**: `PASS_RECOVERED` routes through INFO branch and is screen-visible as a success-class result
- **M4.2**: `FailureClassifier` uses `SprintConfig`-canonical path resolution
- **M4.3**: `DiagnosticBundle` backward-compatible with `None` default; `config=None` path logs deprecation warning
- **M4.4**: PASS_RECOVERED grep audit complete; all parity gaps documented or resolved

#### Timeline

**0.5 day**

---

### Phase 5: Test Suite and Quality Gates

#### Goals

Prove lifecycle correctness, compatibility safety, and recovery behavior. Lock down guarantees for all Phase 8 requirements.

**Requirements**: FR-016–FR-022, NFR-001–NFR-005

**Dependency**: Phases 1–4 complete.

#### Key Actions

1. Create `tests/sprint/test_phase8_halt_fix.py` with three test classes:

   **`TestIsolationWiring`** (T04.01–T04.04):
   - T04.01: Isolation directory created before subprocess launch; contains exactly one file
   - T04.02: Isolation directory removed after successful phase
   - T04.03: Isolation directory removed after failed phase (finally block)
   - T04.04: Startup orphan cleanup removes stale `.isolation/` tree

   **`TestPromptAndContext`** (T04.05–T04.07):
   - T04.05: `build_prompt()` output contains `## Sprint Context` header
   - T04.06: `detect_prompt_too_long()` returns `True` when pattern found in `error_path`
   - T04.07: `error_path=None` maintains backward-compatible behavior

   **`TestFixesAndDiagnostics`** (T04.08–T04.10):
   - T04.08: `PASS_RECOVERED` appears in screen output (INFO routing)
   - T04.09: `FailureClassifier` uses config-driven path via `SprintConfig.output_file()`
   - **T04.10** (named, explicit — adopted from Variant A): `_determine_phase_status()` passes `error_file` through to `detect_prompt_too_long()` — covers FR-010–FR-012 which otherwise lack dedicated test coverage

2. Run validation sequence:
   - `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` — 10 tests pass
   - `uv run pytest tests/ -v --tb=short` — ≥638 passed (629 baseline + 10 new), exit 0
   - `uv run ruff check` — exit 0, zero violations
   - `uv run ruff format --check` — exit 0

#### Milestones

- **M5.1**: 10 new targeted tests pass
- **M5.2**: Full regression suite passes with zero regressions
- **M5.3**: Ruff lint and format checks clean

#### Timeline

**1.0 day**

---

### Phase 6: Smoke Validation and Release Gate

#### Goals

Validate operational behavior under realistic execution conditions. This phase is a **hard blocking gate** — not a release-readiness check that can be skipped under schedule pressure. SC-004 and SC-005 are blocking criteria; the branch does not merge until both are verified.

**Requirements**: SC-004, SC-005

**Dependency**: Phase 5 complete.

#### Key Actions

1. Manual smoke test: trigger context exhaustion on a phase approaching prompt limits
2. Verify `PASS_RECOVERED` appears in operator screen output (not `ERROR`)
3. Verify `tasklist-index.md` is not resolvable by the isolated subprocess — this is the primary system objective of the sprint
4. Verify no stale `.isolation/phase-*` directories remain after execution
5. Final diff review against all 7 modified files
6. Document release-ready conclusion

#### Milestones

- **M6.1**: Recovery status `PASS_RECOVERED` visible in operator output
- **M6.2**: Isolation verified — `tasklist-index.md` unreachable in practical execution; ~14K token reduction per phase confirmed
- **M6.3**: Go/no-go documented; branch ready for merge to `v2.25.7-phase8`

#### Timeline

**0.5 day**

---

## Risk Assessment

### High-Priority Risks

#### Risk H1: Context Exhaustion Recurs on Large Phases

- **Severity**: High
- **Failure mode**: Sprint recovery incomplete for oversized deliverable sets; this roadmap reduces but does not eliminate exhaustion
- **Mitigation**:
  1. Enforce isolation immediately to remove unnecessary token load (~14K/phase)
  2. Monitor phase token usage post-merge
  3. S4 trigger conditions: second exhaustion recurrence OR more than 8 deliverables per phase
  4. Keep deliverables per phase bounded until S4

#### Risk H2: Isolation Appears Implemented but Is Not Enforced (Silent Failure)

- **Severity**: High — elevated from the debate's convergence that *discoverability* is a legitimate severity factor
- **Failure mode**: Sprint merges and passes CI while `tasklist-index.md` remains accessible; token waste continues unchanged; no alarm fires
- **Mitigation**:
  1. Phase 1 M1.0 gates: verify the actual subprocess resolution mechanism before writing isolation code
  2. T04.01 locks down: exactly one file exists in isolation directory at subprocess launch
  3. Phase 6 smoke test is a **hard blocking gate** (not optional): verify `tasklist-index.md` is mechanically unreachable
  4. Note: T04.01 is only reliable if written against the correct mechanism — this is the circular dependency that makes M1.0 non-negotiable

### Medium-Priority Risks

#### Risk M1: Cleanup Failures Mask Primary Phase Errors

- **Severity**: Medium
- **Mitigation**: `ignore_errors=True` on all `shutil.rmtree` calls; cleanup always in `finally`; cleanup exceptions never raised over execution results

#### Risk M2: `env_vars` Plumbing Partially Connected

- **Severity**: Medium
- **Failure mode**: Execution behavior diverges from design; isolation appears wired but subprocess inherits unmodified environment
- **Mitigation**: Trace end-to-end propagation in Phase 1; T04.01 validates end-to-end; keep design explicit — one source, one builder, one spawn boundary

#### Risk M3: Signature Changes Break Existing Callers

- **Severity**: Medium
- **Mitigation**: All new params keyword-only after `*`; `None` defaults throughout; full suite run after each phase; existing positional calls unaffected

#### Risk M4: Concurrent Sprint Runs Share `.isolation` Base Directory

- **Severity**: Low-Medium
- **Failure mode**: Startup orphan cleanup in one run could remove the active isolation directory of another concurrent run on the same `results_dir`
- **Mitigation**: Document same-`results_dir` concurrency as unsupported; defer PID-stamped isolation roots to S4 (not justified by current usage patterns)

### Low-Priority Risks

#### Risk L1: `PASS_RECOVERED` Parity Gaps Remain Elsewhere

- **Severity**: Low
- **Mitigation**: M1.0 grep audit inventories all `PhaseStatus.PASS` switch sites; M4.4 closes identified gaps; treat `PASS_RECOVERED` as a policy invariant going forward

#### Risk L2: `DiagnosticBundle.config` Introduces Compatibility Ambiguity

- **Severity**: Low
- **Mitigation**: Default to `None`; guarded fallback to legacy path logic with deprecation warning; migrate toward always-supplied config over time

---

## Resource Requirements

### Files Modified (7 total)

| File | Changes | Phase |
|------|---------|-------|
| `src/superclaude/cli/sprint/process.py` | `env_vars` parameter on `ClaudeProcess.__init__()` | 1 |
| `src/superclaude/cli/pipeline/process.py` | `env_vars` parameter on `build_env()` | 1 |
| `src/superclaude/cli/sprint/executor.py` | Isolation lifecycle, orphan cleanup, `error_file` plumbing | 2, 3 |
| `src/superclaude/cli/sprint/prompt.py` | `## Sprint Context` header in `build_prompt()` | 3 |
| `src/superclaude/cli/sprint/monitor.py` | `error_path` parameter on `detect_prompt_too_long()` | 3 |
| `src/superclaude/cli/sprint/logger.py` | `PASS_RECOVERED` routing to INFO branch | 4 |
| `src/superclaude/cli/sprint/diagnostics.py` | `FailureClassifier` config-driven path, `DiagnosticBundle.config`, deprecation warning | 4 |

### New Files (1)

| File | Purpose | Phase |
|------|---------|-------|
| `tests/sprint/test_phase8_halt_fix.py` | 10 test cases covering all Phase 8 requirements | 5 |

### Requirement-to-Phase Mapping

| Requirement | File | Change Type | Phase |
|-------------|------|-------------|-------|
| FR-001–FR-003 | `executor.py` | Isolation create/copy/gate | 2 |
| FR-004–FR-005 | `process.py`, `pipeline/process.py` | `env_vars` param addition | 1 |
| FR-006 | `executor.py` | Startup orphan cleanup | 2 |
| FR-007–FR-008 | `prompt.py` | Sprint context header | 3 |
| FR-009 | `monitor.py` | `error_path` extension | 3 |
| FR-010–FR-012 | `executor.py`, `monitor.py` | `error_file` plumbing | 3 |
| FR-013 | `logger.py` | `PASS_RECOVERED` INFO routing | 4 |
| FR-014–FR-015 | `diagnostics.py` | Config-driven path, `DiagnosticBundle` extension | 4 |
| FR-016–FR-022 | `test_phase8_halt_fix.py` | New test cases T04.01–T04.10 | 5 |
| NFR-001–NFR-005 | All | Keyword-only params, `None` defaults, ruff compliance, parity audit | 1–5 |

### External Dependencies

All dependencies are stdlib (`shutil`, `pathlib`, `os`, `re`, `datetime`) — already imported in target files. No new third-party packages. `uv` toolchain required for all execution.

### Internal Dependency Chain (Critical Path)

```
Phase 1: OQ-006 gate + env_vars
    │
    ├──→ Phase 2: Isolation lifecycle (sequential — subprocess boundary dependency)
    │
    ├──→ Phase 3: Prompt + error detection (parallelizable with Phase 4)
    │
    └──→ Phase 4: Diagnostics + status fixes (parallelizable with Phase 3)

Phases 2–4 complete
    │
    └──→ Phase 5: Tests + quality gates
                │
                └──→ Phase 6: Smoke validation (hard gate — blocks merge)
```

**Not recommended for parallelization**: Phase 1 → Phase 2 (isolation lifecycle and env propagation share the subprocess boundary; incorrect sequencing creates false isolation).

---

## Success Criteria and Validation

### Automated Validation

| Criterion | Validation Command | Expected |
|-----------|-------------------|----------|
| **SC-001**: 10 new tests pass | `uv run pytest tests/sprint/test_phase8_halt_fix.py -v` | 10 passed, exit 0 |
| **SC-002**: Zero regressions | `uv run pytest tests/ -v --tb=short` | ≥638 passed, exit 0 |
| **SC-003**: Static analysis clean | `uv run ruff check && uv run ruff format --check` | Exit 0, zero violations |

### Behavioral Validation

| Criterion | Verification Method | Blocking? |
|-----------|---------------------|-----------|
| **SC-004**: `PASS_RECOVERED` visible | Manual smoke: trigger context exhaustion; verify status in screen output | Yes |
| **SC-005**: Token reduction achieved | Verify `tasklist-index.md` unreachable in isolated subprocess; ~14K reduction per phase | Yes |
| Isolation lifecycle correctness | Confirm exactly one file in isolation dir at launch; dir removed after success and failure | Yes |
| Prompt context header present | Inspect `build_prompt()` output; confirm `## Sprint Context` section | Yes |

### Architectural Validation

| Criterion | Verification |
|-----------|-------------|
| All new params keyword-only | Code review: `*` before new params in all signatures |
| All defaults backward-compatible | `None` defaults on all new parameters; existing call sites compile unchanged |
| Canonical path ownership in `SprintConfig` | `FailureClassifier` references `bundle.config.output_file()`; no hardcoded path construction |
| `PASS_RECOVERED` parity complete | M4.4 grep audit documented; no remaining switch sites that handle `PASS` but omit `PASS_RECOVERED` |

**Validation sequence**: Run automated gates after each phase (not only at Phase 5). This catches regressions early and maintains a tight feedback loop.

---

## Timeline Estimates

| Phase | Description | Estimate | Dependencies | Parallelizable |
|-------|-------------|----------|-------------|----------------|
| 1 | OQ-006 gate + environment plumbing | 0.75 day | None | — |
| 2 | Isolation lifecycle | 1.0 day | Phase 1 (M1.0 required) | No |
| 3 | Prompt resilience + context header | 0.5 day | Phase 1 complete | Yes (with Phase 4) |
| 4 | Diagnostics + status consistency | 0.5 day | Phase 1 complete | Yes (with Phase 3) |
| 5 | Test suite + quality gates | 1.0 day | Phases 2–4 complete | — |
| 6 | Smoke validation (hard gate) | 0.5 day | Phase 5 complete | — |
| **Total** | | **4.25–4.5 days** | | |

**Contingency**: The 4.5-day estimate is contingent on M1.0 confirming `CLAUDE_WORK_DIR` as the isolation mechanism. If OQ-006 resolution reveals subprocess `cwd` is the correct lever, re-estimate Phase 2 before beginning Phase 2 implementation. The timeline should not be treated as fixed until M1.0 is complete.

**Critical path**: Phase 1 (M1.0) → Phase 2 → Phase 5 → Phase 6

**Parallel opportunity**: Phases 3 and 4 can proceed concurrently after Phase 1 completes; Phase 3 has no dependency on Phase 2.
