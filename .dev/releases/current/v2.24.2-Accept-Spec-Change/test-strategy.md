

---
validation_milestones: 5
interleave_ratio: '1:1'
---

# Test Strategy: v2.24.2 Accept-Spec-Change

## 1. Validation Milestones Mapped to Roadmap Phases

### Milestone 1: `spec_patch.py` Unit Validation (Phase 1 gate)
**Exit criteria**: All isolated behaviors of the leaf module verified.

| Test | AC | Layer | What to test |
|------|----|-------|-------------|
| `test_missing_state_file` | AC-1 | L1 | Exit 1 + message when `.roadmap-state.json` absent |
| `test_unreadable_state_file` | AC-1 | L1 | Exit 1 on permission error |
| `test_missing_spec_file` | — | L1 | Exit 1 + "Spec file not found" when `spec_file` path invalid |
| `test_hash_already_current` | AC-3 | L1 | Exit 0 + "nothing to do" when hashes match |
| `test_absent_null_empty_hash_treated_as_mismatch` | AC-5a | L1 | `None`, `""`, missing key all trigger mismatch path |
| `test_no_qualifying_deviations` | AC-1 | L1 | Exit 1 when glob finds files but none match disposition+spec_update_required |
| `test_yaml_parse_error_skipped` | AC-14 | L1 | Malformed frontmatter → stderr warning, file skipped, processing continues |
| `test_string_true_rejected` | — | L1 | `spec_update_required: "true"` (quoted string) does NOT qualify |
| `test_yaml_boolean_coercion_variants` | — | L1 | `yes`, `on`, `1`, `True`, `TRUE` all accepted as boolean true |
| `test_disposition_case_insensitive` | — | L1 | `accepted`, `Accepted`, `ACCEPTED` all match |
| `test_prompt_y_confirms` | AC-5a | L1 | `y` and `Y` proceed to write |
| `test_prompt_n_readonly` | AC-4 | L3 | Answer `N` → mtime unchanged, no state mutation |
| `test_prompt_other_input_treated_as_n` | AC-4 | L1 | `yes`, empty, `maybe` all treated as rejection |
| `test_non_interactive_aborts` | AC-11 | L2 | `isatty()=False` + `auto_accept=False` → "Aborted." + exit 0 + no mutation |
| `test_atomic_write_only_changes_spec_hash` | AC-2 | L3 | All non-`spec_hash` keys byte-identical before/after |
| `test_atomic_write_overwrites_existing_tmp` | — | L1 | Pre-existing `.tmp` file is replaced without error |
| `test_idempotent_second_run` | AC-3 | L3 | Run twice → second exits 0 cleanly |
| `test_confirmation_output_format` | AC-5a | L1 | Old/new hashes truncated to 12 chars, deviation IDs listed |

### Milestone 2: CLI Command Validation (Phase 2 gate)
**Exit criteria**: Click command works end-to-end from terminal invocation.

| Test | AC | Layer | What to test |
|------|----|-------|-------------|
| `test_cli_invocation_happy_path` | — | L2 | `superclaude accept-spec-change <dir>` exits 0 with valid fixtures |
| `test_cli_nonexistent_dir` | — | L2 | Click rejects nonexistent path before reaching `spec_patch` |
| `test_cli_exit_codes` | AC-1 | L2 | Exit 1 for missing state, missing spec, no deviations |
| `test_no_optional_flags` | — | L2 | Command accepts only positional `output_dir`, no extra flags |
| `test_dependency_direction` | NFR-006 | L2 | `spec_patch.py` has zero imports from `executor.py` or `commands.py` (static analysis) |

### Milestone 3: Auto-Resume Integration Validation (Phase 3 gate)
**Exit criteria**: Executor correctly detects, patches, and resumes exactly once.

| Test | AC | Layer | What to test |
|------|----|-------|-------------|
| `test_auto_resume_happy_path` | AC-5b | L4 | Spec-fidelity FAIL → detection gate passes → patch → resume skips upstream phases |
| `test_backward_compatible_signature` | AC-10 | L4 | `execute_roadmap()` callable without `auto_accept` kwarg |
| `test_auto_accept_true_skips_prompt` | AC-9 | L4 | `auto_accept=True` proceeds without interactive confirmation |
| `test_auto_accept_false_prompts` | AC-9 | L4 | `auto_accept=False` requires user confirmation |
| `test_recursion_guard_blocks_second` | AC-6 | L4 | Trigger condition twice → only one cycle fires, suppression message logged |
| `test_disk_reread_not_in_memory` | AC-7 | L4 | State object passed to `_apply_resume()` matches post-write disk content, not pre-write in-memory |
| `test_log_prefixes` | AC-12 | L4 | Entry, completion, suppression messages all have `[roadmap]` prefix |
| `test_detection_gate_condition1_recursion` | — | L4 | Guard already fired → skip |
| `test_detection_gate_condition2_no_qualifying_files` | — | L4 | No deviation files with mtime > started_at → skip |
| `test_detection_gate_condition2_missing_started_at` | — | L4 | Absent `started_at` → condition not met → normal failure (fail-closed) |
| `test_detection_gate_condition3_hash_unchanged` | — | L4 | Spec hash equals initial_spec_hash → skip |
| `test_initial_spec_hash_is_local_var` | — | L4 | Comparison uses entry-time hash, not `state["spec_hash"]` |

### Milestone 4: Failure Path and Hardening Validation (Phase 4 gate)
**Exit criteria**: All failure and adversarial scenarios handled correctly.

| Test | AC | Layer | What to test |
|------|----|-------|-------------|
| `test_atomic_write_failure_aborts_cycle` | AC-13 | L5 | OSError on `.tmp` write → stderr error → cycle aborts → normal halt path |
| `test_retry_exhaustion_exits_1` | AC-8 | L5 | Spec-fidelity fails after retry → `sys.exit(1)` with second-run results |
| `test_retry_exhaustion_uses_second_run_results` | AC-8 | L5 | Halt output contains post-retry results, not first-run results |
| `test_recursion_guard_suppression_log` | AC-6, AC-12 | L5 | Guard blocks → suppression message logged with `[roadmap]` prefix |
| `test_state_integrity_after_abort` | AC-4 | L5 | All keys preserved, mtime unchanged after any abort path |
| `test_six_step_sequence_exact` | AC-7 | L5 | Mock disk I/O to verify: read → hash → write → read again → build → resume (in that order) |
| `test_toctou_documented` | NFR-005 | L5 | Verify docstring on `spec_patch.py` mentions single-writer assumption |
| `test_no_subprocess_in_spec_patch` | NFR-004 | L5 | Static analysis: no `subprocess`, `ClaudeProcess`, `os.system` in `spec_patch.py` |
| `test_no_new_public_symbols` | NFR-008 | L5 | `executor.py` public API unchanged except `execute_roadmap()` default param |

### Milestone 5: Release Gate Validation (Phase 5 gate)
**Exit criteria**: Full AC matrix passes, release checklist satisfied.

| Validation | Criteria | Method |
|-----------|----------|--------|
| AC coverage | All 14 ACs have ≥1 automated test | AC traceability matrix review |
| NFR coverage | All 8 NFRs verified | Mix of automated tests + static analysis |
| No circular deps | `spec_patch.py` imports only stdlib + PyYAML | `grep -n "^from\|^import" spec_patch.py` |
| Module isolation | No reverse imports | Static analysis |
| Happy path E2E | Full flow: create deviation → accept → resume | Integration test |
| Exhausted retry E2E | Full flow: accept → resume → second failure → exit 1 | Integration test |
| Lint + type check | `make lint` clean | CI gate |
| Full suite | `make test` green | CI gate |

---

## 2. Test Categories

### Unit Tests (`tests/cli_portify/test_spec_patch.py`)
**Scope**: `spec_patch.py` in isolation. No executor, no CLI framework.
**Fixtures**: Temporary directories with synthetic `.roadmap-state.json`, spec files, deviation files.
**Mocking**: `sys.stdin.isatty()`, `builtins.input()`, filesystem errors via `unittest.mock.patch`.
**Count**: ~18 tests (Milestone 1).

### Integration Tests (`tests/cli_portify/test_auto_resume.py`)
**Scope**: `executor.py` auto-resume orchestration with real `spec_patch.py` but mocked pipeline steps.
**Fixtures**: Full state files with step results, deviation files with various mtimes.
**Mocking**: Pipeline subprocess calls (Claude processes), `sys.exit` capture, filesystem for write-failure simulation.
**Count**: ~16 tests (Milestones 3–4).

### CLI Tests (within `test_spec_patch.py`)
**Scope**: Click command invocation via `CliRunner`.
**Count**: ~5 tests (Milestone 2).

### Static Analysis (Milestone 5)
**Scope**: Import graph validation, public API surface, subprocess absence.
**Method**: Grep-based assertions in test functions or standalone checks.
**Count**: ~4 checks.

### E2E Acceptance (Milestone 5)
**Scope**: Two full scenarios exercising the entire flow with real file I/O.
**Count**: 2 tests (happy path + exhausted retry).

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1:1 — tests written alongside or before implementation at each sub-phase.

| Phase | Implementation Step | Corresponding Test Step |
|-------|-------------------|----------------------|
| P1.1 | State discovery + hash computation | `test_missing_state_file`, `test_missing_spec_file`, `test_hash_already_current`, `test_absent_null_empty_hash` |
| P1.2 | Deviation scanning | `test_no_qualifying_deviations`, `test_yaml_parse_error`, `test_string_true_rejected`, `test_boolean_coercion`, `test_disposition_case` |
| P1.3 | Prompt + atomic write | `test_prompt_*`, `test_non_interactive`, `test_atomic_write_*`, `test_idempotent` |
| P1.4 | — | Run full unit suite, fill gaps |
| P2.1 | Click command | `test_cli_*` (CliRunner) |
| P2.2 | Dependency check | Verify `uv pip list \| grep yaml` |
| P3.1–P3.2 | `auto_accept` threading + detection gate | `test_backward_compatible_signature`, `test_detection_gate_*` |
| P3.3 | Disk-reread sequence | `test_disk_reread_not_in_memory`, `test_six_step_sequence_exact` |
| P3.4–P3.6 | Recursion guard + logging | `test_recursion_guard_*`, `test_log_prefixes` |
| P4.1–P4.4 | Edge cases + failure paths | All L5 tests — **write these first** (TDD for failure paths per Architect Rec #3) |
| P5 | Final validation | Run full suite, verify AC matrix, static analysis |

**Key principle**: Failure-path tests (L5) are written *before* their implementation in P4, following TDD. This is the highest-risk code and benefits most from test-first discipline.

---

## 4. Risk-Based Test Prioritization

Tests ordered by risk severity × probability (highest first):

| Priority | Risk | Tests | Rationale |
|----------|------|-------|-----------|
| **P0 — Critical** | R2: Stale in-memory state | `test_disk_reread_not_in_memory`, `test_six_step_sequence_exact` | Subtle state-drift bug; hardest to debug if missed |
| **P0 — Critical** | R1: State corruption | `test_atomic_write_only_changes_spec_hash`, `test_atomic_write_failure_aborts_cycle`, `test_state_integrity_after_abort` | Data loss risk |
| **P0 — Critical** | R3: Infinite retry | `test_recursion_guard_blocks_second`, `test_retry_exhaustion_exits_1` | Runaway process risk |
| **P1 — High** | R5: Accidental auto_accept | `test_auto_accept_true_skips_prompt`, `test_non_interactive_aborts` | Unintended state mutation |
| **P1 — High** | R4: Malformed YAML | `test_yaml_parse_error_skipped`, `test_string_true_rejected` | Silent data corruption |
| **P2 — Medium** | R6: TOCTOU | `test_toctou_documented` | Documented risk, low probability |
| **P2 — Medium** | R7: Timestamp ambiguity | `test_detection_gate_condition2_missing_started_at` | Edge case, fail-closed mitigates |
| **P3 — Low** | R8: YAML coercion drift | `test_yaml_boolean_coercion_variants` | Intentional contract, low churn risk |
| **P3 — Low** | R9: PyYAML dependency | P2.2 manual check | One-time verification |

---

## 5. Acceptance Criteria per Milestone

### Milestone 1 — `spec_patch.py` Core
- All 18 unit tests pass
- `spec_patch.py` has zero imports from `executor.py` or `commands.py`
- Coverage ≥95% of `spec_patch.py` lines
- No `subprocess` or `ClaudeProcess` usage

### Milestone 2 — CLI Command
- `superclaude accept-spec-change <dir>` works via CliRunner
- Exit codes correct for all error paths
- `pyproject.toml` updated if PyYAML needed
- All 4 open questions documented with decisions

### Milestone 3 — Auto-Resume Integration
- Detection gate evaluates all 3 conditions correctly
- Exactly one retry cycle fires (never zero when conditions met, never two)
- `_apply_resume()` receives post-write disk state
- All log messages have `[roadmap]` prefix
- `execute_roadmap()` backward-compatible without `auto_accept`

### Milestone 4 — Hardening
- Failure-path test count ≥ happy-path test count
- Atomic write failure aborts cleanly (no partial state)
- Retry exhaustion uses second-run results
- Single-writer assumption documented in code
- mtime limitation documented in code

### Milestone 5 — Release Gate
- All 14 ACs mapped to automated tests (verified by matrix)
- All 8 NFRs verified
- `make sync-dev && make verify-sync && make test && make lint` passes
- At least 1 happy-path E2E and 1 exhausted-retry E2E demonstrated
- No new public symbols beyond `execute_roadmap()` default parameter

---

## 6. Quality Gates Between Phases

| Gate | Between | Required | Blocking? |
|------|---------|----------|-----------|
| **G1: Unit Isolation** | P1 → P2 | All unit tests green; `spec_patch.py` import graph verified; zero `executor.py` imports | Yes |
| **G2: CLI + Dependencies** | P2 → P3 | CLI smoke test passes; PyYAML resolved; open questions documented | Yes |
| **G3: Integration Safety** | P3 → P4 | All L4 tests green; recursion guard verified; disk-reread sequence verified; backward compat confirmed | Yes |
| **G4: Failure Hardening** | P4 → P5 | All L5 tests green; failure-path tests ≥ happy-path tests; static analysis checks pass | Yes |
| **G5: Release** | P5 → Merge | Full AC matrix verified; `make test && make lint` green; E2E scenarios demonstrated; docs updated | Yes |

**Gate enforcement**: Each gate is **blocking** — no phase may begin until the prior gate passes. This is the critical path (`P1 → P2 → P3 → P4 → P5`); no phase skipping is permitted.

**Gate verification command**:
```bash
# G1
uv run pytest tests/cli_portify/test_spec_patch.py -v && \
  ! grep -E "^(from|import).*executor|^(from|import).*commands" src/superclaude/cli/cli_portify/spec_patch.py

# G2
uv run pytest tests/cli_portify/test_spec_patch.py -v -k "cli"

# G3
uv run pytest tests/cli_portify/test_auto_resume.py -v

# G4
uv run pytest tests/cli_portify/ -v

# G5
make sync-dev && make verify-sync && make test && make lint
```
