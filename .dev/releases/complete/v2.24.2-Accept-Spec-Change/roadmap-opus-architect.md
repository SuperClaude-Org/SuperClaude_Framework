

---
spec_source: "release-spec-accept-spec-change.md"
complexity_score: 0.65
primary_persona: architect
---

# Roadmap: v2.24.2 Accept-Spec-Change

## Executive Summary

This release adds a **spec-hash reconciliation mechanism** to the roadmap pipeline. When a spec file changes mid-execution (triggering spec-fidelity failure), the system needs a way to acknowledge accepted deviations and update the stored hash so `--resume` can proceed. The scope is well-bounded: one new CLI command (`accept-spec-change`), one new leaf module (`spec_patch.py`), and surgical additions to `executor.py` for auto-resume detection.

**Complexity**: Moderate (0.65). The challenge lies not in breadth but in state management correctness — atomic writes, disk-reread sequences, and a recursion guard that must be scoped precisely.

**Key architectural decision**: `spec_patch.py` is a strict leaf module with no reverse imports. All new `executor.py` functions are private. This keeps the dependency graph clean and the public API surface unchanged.

---

## Phased Implementation Plan

### Phase 1: Foundation — `spec_patch.py` Module (Core Logic)

**Goal**: Deliver the standalone `accept-spec-change` logic as a testable, isolated module.

**Milestone**: `spec_patch.py` passes unit tests for all FR-001 through FR-007.

1. **1.1** Create `src/superclaude/cli/cli_portify/spec_patch.py` (or appropriate location within CLI structure)
   - Implement `prompt_accept_spec_change(output_dir: Path) -> int`
   - FR-001: State file location and missing-file error path
   - FR-002: Spec hash recomputation via `hashlib.sha256`
   - FR-003: Hash comparison with idempotent early-exit
2. **1.2** Implement deviation file scanning
   - FR-004: Glob for `dev-*-accepted-deviation.md`, YAML frontmatter parsing
   - Handle `disposition: ACCEPTED` (case-insensitive) + `spec_update_required: true` (boolean, not string)
   - Warn-and-skip on parse errors (RISK-004 mitigation)
3. **1.3** Implement interactive prompt and atomic write
   - FR-005: Evidence summary display, single-char `y/Y` confirmation, non-interactive detection
   - FR-006: Atomic write via `.tmp` + `os.replace()`
   - FR-007: Confirmation output with truncated hashes
4. **1.4** Unit tests for `spec_patch.py`
   - Idempotency (AC-3), read-only on abort (AC-4), missing file errors (AC-1)
   - YAML parse error resilience (AC-14), non-interactive behavior (AC-11)
   - Atomic write preserves non-`spec_hash` keys (AC-2)

**Verification**: `uv run pytest tests/cli_portify/test_spec_patch.py -v` — all green, no imports from `executor.py` or `commands.py`.

---

### Phase 2: CLI Command Registration

**Goal**: Wire `accept-spec-change` into the Click CLI.

**Milestone**: `superclaude accept-spec-change <output_dir>` works end-to-end from terminal.

1. **2.1** Add Click command in `commands.py` (or appropriate CLI entry point)
   - `click.Path(exists=True)` for `output_dir`
   - Zero optional flags (per spec)
   - Import only from `spec_patch.py`
2. **2.2** Add `pyyaml>=6.0` to `pyproject.toml` dependencies
   - Verify it's not already an indirect dependency (Open Question #2)
3. **2.3** Integration test: CLI invocation with real file fixtures

**Verification**: Manual smoke test + integration test with mock state file and deviation records.

---

### Phase 3: Auto-Resume Integration in `executor.py`

**Goal**: Add post-spec-fidelity-FAIL detection and in-process resume cycle.

**Milestone**: Pipeline auto-detects accepted deviations after spec-fidelity failure and resumes once.

1. **3.1** Add `auto_accept` parameter to `execute_roadmap()` signature
   - FR-008: `auto_accept: bool = False`, backward-compatible (AC-10)
   - Thread through call chain to `prompt_accept_spec_change()`
2. **3.2** Implement three-condition detection gate
   - FR-009: Recursion guard check, qualifying deviation mtime check, hash mismatch check
   - Capture `initial_spec_hash` at `execute_roadmap()` entry (local var, not state)
3. **3.3** Implement disk-reread sequence
   - FR-010: Six-step sequence — reread → recompute → atomic write → reread → rebuild steps → resume
   - Abort cycle on write failure (AC-13)
4. **3.4** Implement recursion guard
   - FR-011: `_spec_patch_cycle_count` as local variable, initialized to 0, max 1 cycle
   - FR-013: Fall through to `_format_halt_output` + `sys.exit(1)` on exhaustion (AC-8)
5. **3.5** Add cycle outcome logging
   - FR-012: `[roadmap]` prefixed messages for entry, completion, suppression (AC-12)
6. **3.6** All new functions use `_` prefix
   - `_apply_resume_after_spec_patch()`, `_find_qualifying_deviation_files()`
   - No modification to existing `_apply_resume()` logic

**Verification**: Integration tests covering AC-5a, AC-5b, AC-6, AC-7, AC-8, AC-9.

---

### Phase 4: Edge Cases and Hardening

**Goal**: Address all identified risks and open questions.

**Milestone**: Full AC matrix passes, including adversarial inputs.

1. **4.1** Edge case tests
   - Absent/null/empty `spec_hash` in state file (FR-003 mismatch behavior)
   - `.tmp` file pre-existence (FR-006 overwrite)
   - YAML 1.1 boolean coercion (`yes`/`on`/`1` accepted — RISK-003)
   - Missing `started_at` field (Open Question #5 — define fallback: skip condition 2 or treat as satisfied)
2. **4.2** Resolve open questions
   - #1 (severity field): Inspect existing deviation files, decide source
   - #3 (file cleanup): Document decision — recommend leaving files in place (immutable audit trail)
   - #5 (`started_at` absence): Implement conservative fallback (skip mtime check if no timestamp)
3. **4.3** TOCTOU documentation
   - RISK-001: Add docstring/comment documenting single-writer assumption
   - NFR-005: Add note to user-facing docs about exclusive access
4. **4.4** Filesystem mtime edge case
   - RISK-002: Document limitation in code comments
   - Consider `>=` with rationale comment if stakeholder approves

**Verification**: Full test suite including adversarial fixtures.

---

### Phase 5: Validation and Release

**Goal**: All 14 success criteria verified, documentation complete.

**Milestone**: Merge-ready PR with full AC coverage.

1. **5.1** Run full AC matrix validation
   - Verify all 14 acceptance criteria (AC-1 through AC-14)
   - Verify NFR-001 through NFR-008
2. **5.2** Verify module isolation
   - NFR-006: `spec_patch.py` imports only stdlib + PyYAML
   - NFR-008: No new public symbols beyond `execute_roadmap()`
3. **5.3** Documentation updates
   - CLI help text for `accept-spec-change`
   - Developer guide entry for auto-resume behavior
   - Release notes
4. **5.4** `make sync-dev && make verify-sync && make test && make lint`

---

## Risk Assessment and Mitigation

| Risk | Severity | Probability | Mitigation | Phase |
|------|----------|-------------|------------|-------|
| **RISK-001**: TOCTOU on state file | Medium | Low | Document single-writer constraint; no concurrent `roadmap run` | P4 |
| **RISK-002**: mtime resolution (HFS+/NFS) | Low | Medium | Document limitation; consider `>=` with rationale | P4 |
| **RISK-003**: PyYAML boolean coercion | Low | Low | Intentional per spec; document accepted coercions | P4 |
| **RISK-004**: Malformed YAML in deviation files | Medium | Medium | Warn-and-skip (FR-004); tested in P1 | P1 |
| **RISK-005**: Accidental `auto_accept=True` | High impact, Low prob | Low | Parameter is private, not CLI-exposed; only sprint runner uses it | P3 |
| **NEW: PyYAML as new dep** | Low | Medium | Verify transitive dependency status before adding | P2 |

**Architect's note**: The most consequential risk is the state management correctness in Phase 3. The six-step disk-reread sequence (FR-010) is the most complex single requirement. I recommend implementing it with explicit logging at each step during development, then reducing log verbosity for production.

---

## Resource Requirements and Dependencies

### External Dependencies
- **PyYAML ≥6.0**: New explicit dependency. Verify current transitive status before adding to `pyproject.toml`.
- **Click ≥8.0.0**: Already present. No changes needed.
- **hashlib**: Stdlib. No concerns.

### Internal Dependencies (Consumed, Not Modified)
- `execute_roadmap()` — signature extended with default parameter
- `_apply_resume()` — called but not modified
- `_build_steps()` — called but not modified
- `_format_halt_output()` — called on cycle exhaustion
- `_save_state()` / `read_state()` — used for disk I/O

### Files Created
1. `src/superclaude/cli/cli_portify/spec_patch.py` — new leaf module
2. `tests/cli_portify/test_spec_patch.py` — unit tests
3. `tests/cli_portify/test_auto_resume.py` — integration tests for Phase 3

### Files Modified
1. `src/superclaude/cli/cli_portify/executor.py` — add `auto_accept` param, private functions
2. `src/superclaude/cli/cli_portify/commands.py` — register `accept-spec-change` CLI command
3. `pyproject.toml` — add `pyyaml>=6.0` dependency

---

## Success Criteria and Validation Approach

### Validation Strategy

**Unit tests** (Phase 1, 4): Test `spec_patch.py` in isolation with fixture files. Cover all error paths, idempotency, atomic writes, YAML parsing edge cases.

**Integration tests** (Phase 3): Test auto-resume cycle end-to-end within `execute_roadmap()`. Use mock spec-fidelity results to trigger the detection gate.

**AC Matrix** (Phase 5): Explicit test per acceptance criterion:

| AC | Test Approach | Automated? |
|----|--------------|------------|
| AC-1 | CLI test with no deviation files → assert exit 1 | Yes |
| AC-2 | Write state → run command → diff non-hash keys | Yes |
| AC-3 | Run twice → assert second exits 0 | Yes |
| AC-4 | Answer N → assert mtime unchanged | Yes |
| AC-5a | Assert hash equality post-accept | Yes |
| AC-5b | Run `--resume` → assert upstream steps skipped | Yes |
| AC-6 | Trigger condition twice → assert single cycle | Yes |
| AC-7 | Mock disk state → assert disk-read state used | Yes |
| AC-8 | Fail after cycle → assert `sys.exit(1)` | Yes |
| AC-9 | Test both `auto_accept` values | Yes |
| AC-10 | Call without `auto_accept` → assert no error | Yes |
| AC-11 | Non-interactive + `False` → assert "Aborted." | Yes |
| AC-12 | Capture log output → assert `[roadmap]` prefixes | Yes |
| AC-13 | Mock write failure → assert abort + stderr | Yes |
| AC-14 | Malformed YAML file → assert warning + skip | Yes |

---

## Timeline Estimates per Phase

| Phase | Description | Estimated Effort | Dependencies |
|-------|-------------|-----------------|--------------|
| **P1** | `spec_patch.py` core logic + unit tests | ~3-4 hours | None |
| **P2** | CLI command registration + PyYAML dep | ~1 hour | P1 |
| **P3** | Auto-resume integration in `executor.py` | ~3-4 hours | P1, P2 |
| **P4** | Edge cases and hardening | ~2 hours | P3 |
| **P5** | Validation and release | ~1-2 hours | P4 |
| **Total** | | ~10-13 hours | |

**Critical path**: P1 → P2 → P3 → P4 → P5 (fully sequential — each phase depends on the prior).

**Parallelization opportunity**: P1.4 (unit tests) can be drafted in parallel with P1.1-P1.3 using TDD. P4 edge case tests can be drafted during P3 implementation.

---

## Open Questions Requiring Resolution

These should be resolved **before Phase 3** begins:

1. **Severity field source** — Inspect existing deviation file frontmatter to determine if `severity` is an existing field. If not, either add it to the `DeviationRecord` spec or remove from the prompt output template.
2. **PyYAML status** — Run `uv pip list | grep -i yaml` to check if already present transitively.
3. **`started_at` fallback** — Recommend: if `started_at` is absent, treat Condition 2 as satisfied (conservative: allow cycle to proceed). Document this decision.
4. **Multiple deviation batches** — Confirm with stakeholders that showing all qualifying records in a single prompt is the intended UX.
5. **Post-acceptance file lifecycle** — Recommend: leave deviation files in place as audit trail. They become inert after hash update (idempotency handles re-runs).
