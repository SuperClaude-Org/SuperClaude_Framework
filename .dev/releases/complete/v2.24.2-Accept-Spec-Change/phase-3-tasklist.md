# Phase 3 -- Auto-Resume Integration

Add post-spec-fidelity-FAIL detection and single in-process resume cycle to `executor.py`. Pipeline auto-detects accepted deviations after spec-fidelity failure and resumes exactly once.

---

### T03.01 -- Thread auto_accept parameter through execute_roadmap()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | FR-008 requires `auto_accept: bool = False` on `execute_roadmap()` to enable programmatic callers (sprint runner) to bypass interactive prompt during auto-resume. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema (API signature change), multi-file (executor call chain) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0009/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0009/evidence.md

**Deliverables:**
- `auto_accept: bool = False` parameter added to `execute_roadmap()` in `src/superclaude/cli/roadmap/executor.py`, threaded through call chain to `_apply_resume_after_spec_patch()`

**Steps:**
1. **[PLANNING]** Read `executor.py` to identify `execute_roadmap()` signature and all call sites
2. **[PLANNING]** Trace call chain to identify where `auto_accept` must be threaded
3. **[EXECUTION]** Add `auto_accept: bool = False` as last parameter to `execute_roadmap()` signature
4. **[EXECUTION]** Thread `auto_accept` through internal call chain to `_apply_resume_after_spec_patch()`
5. **[VERIFICATION]** Run `uv run pytest tests/roadmap/ -v -k "auto_accept or backward"` to verify AC-10 (call without `auto_accept` -> no error)
6. **[COMPLETION]** Verify backward compatibility: existing callers without `auto_accept` continue to work

**Acceptance Criteria:**
- `execute_roadmap()` in `executor.py` accepts `auto_accept: bool = False` as a keyword argument
- Calling `execute_roadmap()` without `auto_accept` argument produces no error (AC-10 backward compatibility)
- `auto_accept` parameter is threaded to `_apply_resume_after_spec_patch()` (not dropped mid-chain)
- No new public symbols added beyond the `execute_roadmap()` parameter (NFR-008)

**Validation:**
- `uv run pytest tests/roadmap/ -v -k "auto_accept or backward"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T03.01-test-output.log

**Dependencies:** T01.03, T02.04 (Phase 2 complete, open questions resolved)
**Rollback:** Remove `auto_accept` parameter from `execute_roadmap()` and call chain

---

### T03.02 -- Implement three-condition detection gate for post-spec-fidelity-FAIL

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | FR-009 requires evaluating three conditions after spec-fidelity FAIL before triggering auto-resume: recursion guard, qualifying deviation mtime, and spec hash diff. |
| Effort | L |
| Risk | High |
| Risk Drivers | data (mtime comparison), schema (state integrity), security (state mutation gating) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0010/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0010/evidence.md

**Deliverables:**
- Three-condition detection gate in `executor.py`: (1) `_spec_patch_cycle_count == 0`, (2) qualifying deviation files with mtime strictly greater than `started_at` (absent `started_at` -> condition not met -> fail-closed), (3) current spec hash differs from `initial_spec_hash` captured at `execute_roadmap()` entry

**Steps:**
1. **[PLANNING]** Identify where spec-fidelity FAIL is detected in `executor.py`
2. **[PLANNING]** Design `initial_spec_hash` capture at `execute_roadmap()` entry as local variable
3. **[EXECUTION]** Capture `initial_spec_hash` from state at `execute_roadmap()` entry
4. **[EXECUTION]** Implement `_find_qualifying_deviation_files()` private function: glob + mtime filter (strict `>` against `started_at`)
5. **[EXECUTION]** Implement three-condition gate after spec-fidelity FAIL: guard check, deviation mtime check, hash diff check
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "detection or gate or condition"` to verify AC-5a, AC-5b
7. **[COMPLETION]** Record evidence that all three conditions are independently testable

**Acceptance Criteria:**
- Detection gate evaluates exactly three conditions in order: recursion guard, deviation mtime, hash diff
- Missing `started_at` in state causes condition 2 to evaluate as not-met (fail-closed, no retry)
- `initial_spec_hash` captured at `execute_roadmap()` entry as local variable (not re-read from state)
- All three conditions individually testable via `tests/roadmap/test_spec_patch_cycle.py`

**Validation:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "detection or gate or condition"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T03.02-test-output.log

**Dependencies:** T03.01
**Rollback:** Remove detection gate code from `executor.py`
**Notes:** Strict `>` for mtime comparison (not `>=`) per RISK-002 mitigation. `started_at` absence -> fail-closed per Phase 2 open question resolution.

---

### T03.03 -- Implement six-step disk-reread sequence (FR-010)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | FR-010 requires a precise six-step reread/write/reread sequence to ensure resume uses disk state (not stale in-memory state) after spec-hash mutation. |
| Effort | L |
| Risk | High |
| Risk Drivers | data (state mutation), schema (disk-reread ordering), breaking (stale state if incorrect) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0011/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0011/evidence.md

**Deliverables:**
- `_apply_resume_after_spec_patch()` implementing exact six-step sequence: (1) reread state from disk, (2) recompute spec hash from current spec file, (3) atomically write new hash via `.tmp` + `os.replace()`, (4) reread state from disk again, (5) rebuild steps with `_build_steps(config)`, (6) call `_apply_resume(post_write_state, steps)` -- abort entire cycle on atomic write failure -> log to stderr -> fall through to normal halt

**Steps:**
1. **[PLANNING]** Verify `_apply_resume()` and `_build_steps()` signatures and expected inputs
2. **[PLANNING]** Map the six steps to specific function calls in `executor.py`
3. **[EXECUTION]** Implement `_apply_resume_after_spec_patch()` with steps 1-3 (reread, recompute, atomic write)
4. **[EXECUTION]** Implement steps 4-6 (second reread, rebuild steps, call `_apply_resume()`) with the second-read state object
5. **[EXECUTION]** Add atomic write failure handler: log error to stderr, abort cycle, fall through to normal halt path (AC-13)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "reread or disk_state or resume"` to verify AC-7 (disk state used for resume)
7. **[COMPLETION]** Verify `_apply_resume()` is called with post-write disk state (not pre-write in-memory state)

**Acceptance Criteria:**
- `_apply_resume_after_spec_patch()` executes exactly six steps in documented order
- Step 4 (second disk reread) produces the state object passed to `_apply_resume()` -- in-memory state from step 1 is not reused (AC-7)
- Atomic write failure in step 3 aborts entire cycle with error logged to stderr (AC-13)
- `_apply_resume()` is called but NOT modified (architectural invariant #4)

**Validation:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "reread or disk_state or resume"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T03.03-test-output.log

**Dependencies:** T03.01, T03.02
**Rollback:** Remove `_apply_resume_after_spec_patch()` from `executor.py`
**Notes:** This is the most complex single requirement. Architect Recommendation #1: disk-reread semantics are a non-negotiable invariant.

---

### T03.04 -- Implement recursion guard with max-1 cycle enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | FR-011/FR-013 require `_spec_patch_cycle_count` as a local variable limiting auto-resume to exactly one cycle, with standard halt on exhaustion. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (recursion prevention), schema (cycle state) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0012/spec.md
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0012/evidence.md

**Deliverables:**
- `_spec_patch_cycle_count` local variable in `execute_roadmap()`, initialized to 0, incremented on cycle entry, max 1 -- on exhaustion, fall through to `_format_halt_output()` + `sys.exit(1)` with second-run results (AC-8)

**Steps:**
1. **[PLANNING]** Identify where `_spec_patch_cycle_count` should be declared within `execute_roadmap()` scope
2. **[PLANNING]** Trace the path from cycle exhaustion to `_format_halt_output()` + `sys.exit(1)`
3. **[EXECUTION]** Add `_spec_patch_cycle_count = 0` at `execute_roadmap()` entry
4. **[EXECUTION]** Increment guard on cycle entry; check `_spec_patch_cycle_count >= 1` before allowing retry
5. **[EXECUTION]** On guard block: fall through to `_format_halt_output()` with second-run results + `sys.exit(1)` (AC-8)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "guard or recursion or exhaustion"` to verify AC-6 (single cycle) and AC-8 (halt with second-run results)
7. **[COMPLETION]** Verify guard is scoped to single `execute_roadmap()` invocation (local variable, not class/module state)

**Acceptance Criteria:**
- `_spec_patch_cycle_count` is a local variable within `execute_roadmap()` (not class or module level)
- Triggering spec-fidelity FAIL twice in one invocation results in exactly one retry cycle (AC-6)
- After cycle exhaustion, `sys.exit(1)` is called with second-run results passed to `_format_halt_output()` (AC-8)
- Guard variable is initialized to 0 and max value is 1

**Validation:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "guard or recursion or exhaustion"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T03.04-test-output.log

**Dependencies:** T03.02, T03.03
**Rollback:** Remove `_spec_patch_cycle_count` and guard logic from `execute_roadmap()`
**Notes:** Architect Recommendation #2: do not generalize into reusable retry framework. Future retry mechanisms must use separate guards.

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.05

**Purpose:** Verify core auto-resume integration is functional before logging and naming tasks.
**Checkpoint Report Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/CP-P03-T01-T05.md

**Verification:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v` exits 0 with detection gate, reread sequence, and recursion guard tests passing
- `execute_roadmap()` signature includes `auto_accept: bool = False` with backward compatibility
- `_apply_resume()` function body is unmodified (diff check against Phase 2 baseline)

**Exit Criteria:**
- Three-condition detection gate correctly evaluates all three conditions independently
- Six-step disk-reread sequence passes integration test asserting post-write disk state used for resume
- Recursion guard limits auto-resume to exactly one cycle per invocation

---

### T03.05 -- Add [roadmap]-prefixed cycle outcome logging

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | FR-012 requires all auto-resume messages to be prefixed with `[roadmap]` for log parsing, with entry, completion, and suppression messages. |
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
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0013/spec.md

**Deliverables:**
- `[roadmap]`-prefixed log messages:
  - Entry message (content: `[roadmap]` prefix + qualifying deviation count + "cycle 1/1" identifier)
  - Completion message (content: `[roadmap]` prefix + cycle success indication)
  - Suppression message (content: `[roadmap]` prefix + indication that guard blocked retry)

**Steps:**
1. **[PLANNING]** Identify log output points: cycle entry, cycle completion, guard suppression
2. **[PLANNING]** Confirm `[roadmap]` prefix format matches existing logging conventions
3. **[EXECUTION]** Add entry log with `[roadmap]` prefix, deviation count, and "cycle 1/1" identifier
4. **[EXECUTION]** Add completion log with `[roadmap]` prefix and success indication
5. **[EXECUTION]** Add suppression log with `[roadmap]` prefix and guard-blocked indication
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "log or prefix"` to verify AC-12 (`[roadmap]` prefix)
7. **[COMPLETION]** Verify all three message variants appear in test coverage

**Acceptance Criteria:**
- All auto-resume log messages contain `[roadmap]` prefix (AC-12)
- Entry message includes deviation count and `cycle 1/1` identifier
- Suppression message appears when recursion guard blocks second retry
- Log messages are printed to stdout with `[roadmap]` prefix and are capturable by test frameworks via stdout capture (e.g., `capsys.readouterr().out`)

**Validation:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v -k "log or prefix"`
- Evidence: test output at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T03.05-test-output.log

**Dependencies:** T03.04
**Rollback:** Remove log statements from executor retry path

---

### T03.06 -- Enforce private function naming and public API surface

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | Spec section 4.4 requires `_apply_resume_after_spec_patch()` naming and NFR-008 prohibits new public symbols beyond the `execute_roadmap()` parameter. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.2-Accept-Spec-Change/artifacts/D-0014/spec.md

**Deliverables:**
- All new `executor.py` functions prefixed with `_` (private): `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`, etc. No modification to existing `_apply_resume()` logic. No new public symbols beyond `execute_roadmap()` parameter.

**Steps:**
1. **[PLANNING]** Enumerate all new functions added to `executor.py` in Phase 3
2. **[PLANNING]** Verify `_apply_resume()` is unchanged (diff against pre-Phase-3 baseline)
3. **[EXECUTION]** Verify all new functions have `_` prefix in their names
4. **[EXECUTION]** Run `grep -n "^def [^_]" src/superclaude/cli/roadmap/executor.py` to check for unintended public functions
5. **[VERIFICATION]** Run import analysis: `python -c "from superclaude.cli.roadmap.executor import *; print(dir())"` to verify no new public names
6. **[COMPLETION]** Record public API surface evidence

**Acceptance Criteria:**
- All new functions in `executor.py` have `_` prefix (private naming convention)
- `_apply_resume()` function body is identical to pre-Phase-3 state (no modifications)
- `grep -n "^def [^_]" src/superclaude/cli/roadmap/executor.py` shows only pre-existing public functions plus `execute_roadmap`
- No new public symbols exported from `executor.py` beyond the `auto_accept` parameter on `execute_roadmap()`

**Validation:**
- `grep -n "^def [^_]" src/superclaude/cli/roadmap/executor.py`
- Evidence: public API analysis at .dev/releases/current/v2.24.2-Accept-Spec-Change/evidence/T03.06-api-surface.txt

**Dependencies:** T03.01, T03.02, T03.03, T03.04, T03.05
**Rollback:** Rename any non-prefixed functions to `_` prefixed
**Notes:** NFR-008 enforcement. `_apply_resume()` is called but never modified (architectural invariant #4).

---

### Checkpoint: End of Phase 3

**Purpose:** Verify complete auto-resume integration is functional, tested, and API-compliant before hardening.
**Checkpoint Report Path:** .dev/releases/current/v2.24.2-Accept-Spec-Change/checkpoints/CP-P03-END.md

**Verification:**
- `uv run pytest tests/roadmap/test_spec_patch_cycle.py -v` exits 0 with all integration tests passing (AC-5a/5b/6/7/8/9)
- `_apply_resume()` is unchanged from pre-Phase-3 baseline
- No new public symbols in `executor.py` beyond `auto_accept` parameter

**Exit Criteria:**
- Pipeline auto-detects accepted deviations after spec-fidelity FAIL
- Resume fires exactly once per invocation (recursion guard enforced)
- All log messages prefixed with `[roadmap]`
