---
spec_source: "release-spec-accept-spec-change.md"
complexity_score: 0.65
adversarial: true
---

# Merged Roadmap: v2.24.2 Accept-Spec-Change

## Executive Summary

This release adds a **spec-hash reconciliation mechanism** to the roadmap pipeline. When a spec file changes mid-execution (triggering spec-fidelity failure), the system needs a way to acknowledge accepted deviations and update the stored hash so `--resume` can proceed. The scope is well-bounded: one new CLI command (`accept-spec-change`), one new leaf module (`spec_patch.py`), and surgical additions to `executor.py` for auto-resume detection.

**Complexity**: Moderate (0.65). The challenge lies not in breadth but in state management correctness — atomic writes, disk-reread sequences, and a recursion guard scoped to a single invocation. The highest-risk code is in failure paths and state integrity boundaries, not in the happy path.

**Key architectural decision**: `spec_patch.py` is a strict leaf module with no reverse imports. All new `executor.py` functions are private (`_` prefixed). The public API surface changes only by a single backward-compatible default parameter on `execute_roadmap()`.

**Architectural invariants** (non-negotiable):
1. All `.roadmap-state.json` mutations must be atomic (`.tmp` + `os.replace()`).
2. Abort paths must remain strictly read-only — no state mutation on user rejection or error.
3. Resume after spec-patch must consume **disk state** after mutation, never stale in-memory state.
4. `_apply_resume()` remains unchanged.
5. At most one automatic patch/resume cycle per invocation.

**Expected outcome**: Operators will be able to (a) run `accept-spec-change` to safely update only the stored spec hash after validated evidence, (b) resume roadmap execution without recomputing earlier phases, and (c) benefit from a single automatic in-process retry after spec-fidelity failure when accepted deviations and spec edits justify it.

---

## FR/AC/NFR Mapping

| Roadmap ID | Spec ID | Description |
|------------|---------|-------------|
| FR-001 | FR-2.24.2.1 | Locate state file |
| FR-002 | FR-2.24.2.2 | Recompute spec hash |
| FR-003 | FR-2.24.2.3 | Hash mismatch check |
| FR-004 | FR-2.24.2.4 | Scan deviation records |
| FR-005 | FR-2.24.2.5 | Interactive prompt |
| FR-006 | FR-2.24.2.6 | Atomic write |
| FR-007 | FR-2.24.2.7 | Confirmation output |
| FR-008 | FR-2.24.2.8 | auto_accept parameter |
| FR-009 | FR-2.24.2.9 | Post-spec-fidelity-FAIL detection |
| FR-010 | FR-2.24.2.10 | Disk-reread at resume boundary |
| FR-011 | FR-2.24.2.11 | Recursion guard |
| FR-012 | FR-2.24.2.12 | Cycle outcome logging |
| FR-013 | FR-2.24.2.13 | Normal failure on cycle exhaustion |

**Note**: AC-12, AC-13, AC-14 in the traceability matrix below map to FR-2.24.2.12 (logging), FR-2.24.2.10 (write failure), and FR-2.24.2.4 (parse errors) respectively — they are not separate spec-defined acceptance criteria. NFR-006 maps to spec §4.4 (import isolation) and NFR-008 maps to spec §4.4 (public API surface).

## Phased Implementation Plan

### Phase 1: Foundation — `spec_patch.py` Module

**Goal**: Deliver the standalone `accept-spec-change` logic as a testable, isolated leaf module.

**Milestone**: `spec_patch.py` passes unit tests for all FR-001 through FR-007.

#### 1.1 State-file discovery and hash computation
- Create `src/superclaude/cli/roadmap/spec_patch.py`
- Implement `prompt_accept_spec_change(output_dir: Path, auto_accept: bool = False) -> int`
- FR-001: Read `.roadmap-state.json` from `output_dir`, produce exact error for missing/unreadable state
- FR-002: Load `spec_file` from state, recompute SHA-256 from file bytes
- FR-003: Compare current hash to `state["spec_hash"]` using byte-exact hex equality; treat missing/null/empty `spec_hash` as mismatch; return clean idempotent success when already current

#### 1.2 Deviation file scanning
- Data model: Use the `DeviationRecord` frozen dataclass from spec §4.5 (7 fields: id, disposition, spec_update_required, affects_spec_sections, acceptance_rationale, source_file, mtime) with invariants (uppercase disposition, bool spec_update_required, float mtime)
- FR-004: Glob for `dev-*-accepted-deviation.md`, parse YAML frontmatter
- Select only records matching `disposition: ACCEPTED` (case-insensitive) **and** `spec_update_required: true` (YAML boolean, not string)
- Warn-and-skip on parse errors (RISK-004 mitigation)
- YAML 1.1 boolean coercion (`yes`, `on`, `1`) is **intentionally accepted** — document in operator-facing docs and test explicitly (see §Architect Recommendations)

#### 1.3 Interactive prompt and atomic write
- FR-005: Evidence summary display, single-char `y/Y` confirmation
- Non-interactive detection via `sys.stdin.isatty()`: when non-interactive and `auto_accept=False`, exit with `Aborted.` and zero state mutation
- FR-006: Atomic write via `.tmp` + `os.replace()` (overwrite pre-existing `.tmp`)
- Modify only `spec_hash`; preserve all other state keys verbatim
- FR-007: Confirmation output with truncated hashes, accepted deviation IDs, resume instruction

#### 1.4 Unit tests
- Idempotency: run twice → second exits 0 (AC-3)
- Read-only on abort: answer N → mtime unchanged (AC-4)
- Missing file errors (AC-1)
- YAML parse error resilience: malformed frontmatter → warning + skip (AC-14)
- Non-interactive behavior (AC-11)
- Atomic write preserves non-`spec_hash` keys (AC-2)
- String `"true"` rejection for `spec_update_required`
- Intentional coercion coverage: `yes`, `on`, `1`, `True`, `TRUE` all accepted as boolean true

**Verification**: `uv run pytest tests/roadmap/test_accept_spec_change.py -v` — all green, no imports from `executor.py` or `commands.py`.

---

### Phase 2: CLI Command Registration

**Goal**: Wire `accept-spec-change` into the Click CLI and resolve remaining open questions.

**Milestone**: `superclaude roadmap accept-spec-change <output_dir>` works end-to-end from terminal. Open questions resolved.

#### 2.1 Click command registration
- Add Click command in `commands.py`
- `click.Path(exists=True)` for `output_dir`
- Zero optional flags (per spec)
- Import only from `spec_patch.py` — dependency direction: `commands.py → spec_patch.py`, never reverse

#### 2.2 Dependency management
- Add `pyyaml>=6.0` to `pyproject.toml` dependencies
- First verify transitive status: `uv pip list | grep -i yaml`

#### 2.3 Integration test
- CLI invocation with real file fixtures
- Exit codes for all error paths

#### 2.4 Resolve open questions (Phase 3 exit criteria)
The following must be resolved before Phase 3 begins:

1. **Severity field source**: Inspect existing deviation file frontmatter (`grep -r "severity" .dev/releases/`). If not an existing field, remove from prompt output template.
2. **`started_at` fallback** → **fail-closed**: If `started_at` is absent, treat Condition 2 (mtime check) as **not met**. The retry cycle does not fire. The operator retains `accept-spec-change` as the explicit CLI fallback. This is the safer default for an optimization path — an optimization that doesn't fire is preferable to one that fires incorrectly.
3. **Post-acceptance file lifecycle**: Leave deviation files in place as immutable audit trail. They become inert after hash update (idempotency handles re-runs).
4. **Multiple deviation batches**: Show all qualifying records in a single prompt.

**Verification**: Manual smoke test + integration test. All four open questions documented with decisions.

---

### Phase 3: Auto-Resume Integration in `executor.py`

**Goal**: Add post-spec-fidelity-FAIL detection and single in-process resume cycle.

**Milestone**: Pipeline auto-detects accepted deviations after spec-fidelity failure and resumes exactly once.

#### 3.1 `auto_accept` parameter threading
- FR-008: Add `auto_accept: bool = False` to `execute_roadmap()` signature — backward-compatible (AC-10)
- Thread through call chain to `_apply_resume_after_spec_patch()`

#### 3.2 Three-condition detection gate
- FR-009: After spec-fidelity FAIL, evaluate:
  1. Recursion guard: `_spec_patch_cycle_count == 0`
  2. Qualifying deviation files exist with mtime **strictly greater than** `started_at` (if `started_at` absent → condition not met → fall through to normal failure)
  3. Current spec hash differs from `initial_spec_hash` (captured at `execute_roadmap()` entry as local var)

#### 3.3 Disk-reread sequence (FR-010)
Six-step sequence — the most complex single requirement:
1. Reread state from disk
2. Recompute spec hash from current spec file
3. Atomically write new hash (`.tmp` + `os.replace()`)
4. Reread state from disk again (**critical**: this is the state passed to resume)
5. Rebuild steps with `_build_steps(config)`
6. Call `_apply_resume(post_write_state, steps)`

Abort entire cycle on atomic write failure → log error to stderr → fall through to normal halt path (AC-13).

#### 3.4 Recursion guard
- FR-011: `_spec_patch_cycle_count` as local variable within `execute_roadmap()`, initialized to 0, max 1 cycle
- FR-013: On exhaustion, fall through to `_format_halt_output()` + `sys.exit(1)` using **second-run** results (AC-8)

#### 3.5 Cycle outcome logging
- FR-012: All messages prefixed with `[roadmap]` (AC-12)
- Entry: deviation count and `cycle 1/1`
- Completion: success message
- Suppression: message when guard blocks second retry

#### 3.6 Private function naming
- `_apply_resume_after_spec_patch()` (spec §4.4), `_find_qualifying_deviation_files()` (implementation detail, not in spec), etc.
- No modification to existing `_apply_resume()` logic
- No new public symbols beyond `execute_roadmap()` parameter (NFR-008)

**Verification**: Integration tests covering AC-5a, AC-5b, AC-6, AC-7, AC-8, AC-9 in `tests/roadmap/test_spec_patch_cycle.py`.

---

### Phase 4: Edge Cases and Hardening

**Goal**: Address all identified risks, adversarial inputs, and operational edge cases.

**Milestone**: Full AC matrix passes including adversarial and failure-path scenarios.

#### 4.1 Edge case tests
- Absent/null/empty `spec_hash` in state file (FR-003 mismatch behavior)
- `.tmp` file pre-existence (FR-006 overwrite)
- YAML 1.1 boolean coercion variants — intentionally tested and documented
- Missing `started_at` field → retry condition not met → normal failure path (fail-closed)

#### 4.2 Failure-path tests (elevated priority per Haiku Layer 5)
- Atomic write failure → cycle abort → normal halt path
- Persistent spec-fidelity failure after retry → exit through standard halt with second-run results
- Recursion guard blocks second retry → suppression log → exit
- State integrity after abort: all keys preserved, mtime unchanged

#### 4.3 TOCTOU and filesystem documentation
- RISK-001: Add docstring documenting single-writer assumption prominently
- NFR-005: Add note to operator-facing docs about exclusive access
- RISK-002: Document mtime-resolution limitation (HFS+/NFS) in code comments; use strict `>` comparison with rationale

#### 4.4 State integrity validation (elevated from Haiku Layer 3)
- Verify only `spec_hash` changes across all mutation paths
- Verify abort path leaves file mtime unchanged
- Verify disk-reread state (not in-memory state) is what `_apply_resume()` receives

**Verification**: Full test suite including adversarial fixtures. Proportional attention to failure paths — at least as many failure-path tests as happy-path tests.

---

### Phase 5: Validation and Release

**Goal**: All success criteria verified, documentation complete, release gate passed.

**Milestone**: Merge-ready PR with full AC coverage and release gate checklist satisfied.

#### 5.1 AC matrix validation
- Verify all acceptance criteria (AC-1 through AC-14) are mapped to automated tests
- Verify NFR-001 through NFR-008

#### 5.2 Module isolation verification
- NFR-006: `spec_patch.py` imports only stdlib + PyYAML
- NFR-008: No new public symbols beyond `execute_roadmap()` parameter
- No circular dependencies introduced
- No subprocess pipeline execution in patch module

#### 5.3 Documentation updates
- CLI help text for `accept-spec-change`
- Developer guide entry for auto-resume behavior
- Operator documentation of intentionally accepted YAML boolean coercions
- Document single-writer assumption and mtime limitations
- Release notes

#### 5.4 Release gate checklist
The following must all be true before merge:

1. All acceptance criteria mapped to automated tests (14 AC + 8 NFR)
2. No circular dependency introduced (verify with import analysis)
3. No new public API beyond the defaulted `execute_roadmap()` parameter
4. No subprocess invocation in `spec_patch.py`
5. Resume behavior skips upstream phases after accepted spec change (AC-5b demonstrated)
6. At least one full end-to-end happy-path **and** one exhausted-retry path demonstrated

#### 5.5 Final verification
```bash
make sync-dev && make verify-sync && make test && make lint
```

---

## Risk Assessment

| # | Risk | Severity | Probability | Mitigation | Phase |
|---|------|----------|-------------|------------|-------|
| R1 | **State corruption during write** — partial/interrupted write corrupts `.roadmap-state.json` | High | Low | Enforce `.tmp` + `os.replace()` for every mutation. Never write directly to final path. Tests validate only `spec_hash` changes. POSIX primary; Windows best-effort. | P1, P4 |
| R2 | **Stale in-memory state at resume boundary** — retry resumes with pre-mutation state, causing inconsistent behavior | High | Medium | Enforce six-step reread/write/reread sequence exactly. Second disk read is the object passed to `_apply_resume()`. Integration tests assert post-write disk state equals resumed state. | P3, P4 |
| R3 | **Infinite or repeated retry loop** — spec-fidelity failure repeatedly triggers patch cycles | High | Low | `_spec_patch_cycle_count` local to `execute_roadmap()`, max 1. Log suppression on guard block. Second failure falls through to halt. Future retry mechanisms must use separate guards. | P3 |
| R4 | **Malformed YAML in deviation files** — crashes or false positives from bad frontmatter | Medium | Medium | Parse defensively. Warn-and-skip malformed files. Require boolean `true` (not string). Test string `"true"` rejection. | P1 |
| R5 | **Unsafe non-interactive behavior** — CI/piped execution modifies state without confirmation | Medium | Low | Detect `not sys.stdin.isatty()`. When `auto_accept=False`, exit with `Aborted.` and zero state mutation. `auto_accept` not CLI-exposed. | P1 |
| R6 | **TOCTOU on concurrent state access** — another process mutates state between read and replace | Medium | Low | Document single-writer assumption prominently. No partial mitigation that implies concurrency safety. Locking is a separate future feature. | P4 |
| R7 | **Timestamp ambiguity** — missing `started_at` or low mtime resolution causes incorrect gating | Low–Medium | Medium | Missing `started_at` → fail-closed (retry condition not met). Strict `>` comparison. Document mtime-resolution limitations (HFS+/NFS). | P3, P4 |
| R8 | **YAML boolean coercion drift** — future PyYAML/YAML 1.2 changes break operator files | Low | Low | Intentionally document and test accepted coercions (`yes`, `on`, `1`). Surface in operator docs so coercion is a contract, not an accident. | P1, P5 |
| R9 | **PyYAML as new dependency** — version conflict or unexpected transitive presence | Low | Medium | Verify transitive status before adding. Pin `>=6.0`. | P2 |
| R10 | **Accidental `auto_accept=True`** — programmatic caller enables auto-accept without operator intent | High impact | Low | Parameter is private, not CLI-exposed. Only sprint runner uses it. Document intended callers. | P3 |

---

## Resource Requirements

### External Dependencies
| Dependency | Status | Action |
|------------|--------|--------|
| **PyYAML ≥6.0** | Verify transitive | Add to `pyproject.toml` if not already present |
| **Click ≥8.0.0** | Already present | No changes |
| **hashlib** | Stdlib | No concerns |

### Internal Dependencies (Consumed, Not Modified)
- `execute_roadmap()` — signature extended with default parameter
- `_apply_resume()` — called but **not modified**
- `_build_steps()` — called but not modified
- `_format_halt_output()` — called on cycle exhaustion
- `_save_state()` / `read_state()` — used for disk I/O

### Files Created
| File | Purpose |
|------|---------|
| `src/superclaude/cli/roadmap/spec_patch.py` | New leaf module — core acceptance logic |
| `tests/roadmap/test_accept_spec_change.py` | Unit tests (Phases 1, 4) |
| `tests/roadmap/test_spec_patch_cycle.py` | Integration tests for executor retry (Phase 3) |

### Files Modified
| File | Change |
|------|--------|
| `src/superclaude/cli/roadmap/executor.py` | Add `auto_accept` param, private helper functions |
| `src/superclaude/cli/roadmap/commands.py` | Register `accept-spec-change` CLI command |
| `pyproject.toml` | Add `pyyaml>=6.0` dependency (if needed) |

---

## Success Criteria and Validation Approach

### Validation Strategy

Tests are organized into five categories (adapted from Haiku's layered approach) with direct AC traceability:

**Layer 1 — Unit validation** (`test_spec_patch.py`): Isolated behaviors of `spec_patch.py` — hashing, parsing, prompting, atomic writes.

**Layer 2 — CLI validation** (`test_spec_patch.py`): Command invocation, exit codes, error messages.

**Layer 3 — State integrity validation** (`test_spec_patch.py`, `test_auto_resume.py`): Persistence guarantees — only `spec_hash` changes, abort preserves mtime, idempotent re-runs.

**Layer 4 — Executor integration validation** (`test_auto_resume.py`): Auto-resume orchestration — detection gate, disk-reread sequence, recursion guard.

**Layer 5 — Failure-path validation** (`test_auto_resume.py`): Architectural safety under failure — write failure abort, retry exhaustion, stale-state prevention.

### AC Traceability Matrix

| AC | Description | Test Layer | Automated |
|----|------------|------------|-----------|
| AC-1 | CLI with no deviation files → exit 1 | L2 | Yes |
| AC-2 | Write state → run → diff non-hash keys preserved | L3 | Yes |
| AC-3 | Run twice → second exits 0 (idempotent) | L3 | Yes |
| AC-4 | Answer N → mtime unchanged | L3 | Yes |
| AC-5a | Hash equality post-accept | L1 | Yes |
| AC-5b | `--resume` skips upstream steps | L4 | Yes |
| AC-6 | Trigger condition twice → single cycle only | L4 | Yes |
| AC-7 | Disk-read state (not in-memory) used for resume | L4 | Yes |
| AC-8 | Fail after cycle → `sys.exit(1)` with second-run results | L5 | Yes |
| AC-9 | Both `auto_accept` values tested | L4 | Yes |
| AC-10 | Call without `auto_accept` → no error | L4 | Yes |
| AC-11 | Non-interactive + `False` → `Aborted.` | L2 | Yes |
| AC-12 | Log output has `[roadmap]` prefixes | L4 | Yes |
| AC-13 | Write failure → abort + stderr | L5 | Yes |
| AC-14 | Malformed YAML → warning + skip | L1 | Yes |

---

## Timeline Estimates

| Phase | Description | Estimated Effort | Dependencies |
|-------|-------------|-----------------|--------------|
| **P1** | `spec_patch.py` core logic + unit tests | ~4–5 hours | None |
| **P2** | CLI registration + dependency + open question resolution | ~1–2 hours | P1 |
| **P3** | Auto-resume integration in `executor.py` | ~4–5 hours | P1, P2 |
| **P4** | Edge cases, failure paths, hardening | ~2–3 hours | P3 |
| **P5** | Validation, documentation, release gate | ~1–2 hours | P4 |
| **Total** | | **~12–17 hours focused effort** | |

**Critical path**: P1 → P2 → P3 → P4 → P5 (fully sequential — each phase depends on the prior).

**Parallelization opportunities**: P1.4 (unit tests) can be drafted in parallel with P1.1–P1.3 using TDD. P4 failure-path tests can be drafted during P3 implementation.

**Note on timeline framing**: The estimate above reflects focused single-developer effort. If coordination overhead, code review cycles, or context-switching are factors, add 30–50% buffer. QA effort is embedded in each phase (test-first for failure paths per Architect Recommendation #4), not deferred to a separate phase.

---

## Architect Recommendations

These recommendations are implementation guidance, not phase-gated deliverables:

1. **Treat disk-reread semantics as a non-negotiable invariant.** This is the architectural boundary that prevents subtle state-drift bugs. The six-step sequence in Phase 3.3 must be implemented exactly — no shortcuts that reuse in-memory state after a write.

2. **Keep retry logic narrow and explicit.** Do not generalize the spec-patch retry into a reusable failure-recovery framework in this release. Future retry mechanisms for other failure classes must use separate guards.

3. **Require test-first for abort and failure paths.** The highest-risk defects are not in the happy path — they are in no-touch aborts, retry exhaustion, and stale-state resume boundaries. Write failure-path tests before or alongside the implementation, not after.

4. **Document the single-writer assumption prominently.** The absence of locking is acceptable only if operationally explicit. Add to both code docstrings and operator-facing documentation.

5. **Make YAML boolean coercion intentional.** Test `yes`, `on`, `1`, `True`, `TRUE` explicitly. Document in operator-facing docs that these are accepted. Test that string `"true"` (quoted) is rejected. This converts an implicit library behavior into an explicit contract.

6. **Avoid expanding CLI scope.** Zero optional flags is the correct design choice for this release. Additional override controls would increase operator risk and test surface without clear value.
