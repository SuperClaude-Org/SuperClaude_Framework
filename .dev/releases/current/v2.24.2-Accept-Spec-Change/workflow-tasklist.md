# Workflow Tasklist: v2.24.2 Accept-Spec-Change

> Generated from spec-fidelity findings + spec + roadmap analysis.
> All tasks designed for `/sc:task-unified` execution.

---

## Pre-Implementation: Roadmap Document Fixes

These tasks fix the spec-fidelity deviations in the roadmap document itself,
unblocking tasklist generation and ensuring implementers have correct guidance.

### TASK-000: Fix HIGH severity path deviations in roadmap (DEV-001, DEV-002, DEV-003)

- **Compliance**: LIGHT
- **Priority**: BLOCKING
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: Find-replace all `src/superclaude/cli/cli_portify/` references to `src/superclaude/cli/roadmap/` for the three affected files:
  - `spec_patch.py`: `cli_portify/spec_patch.py` → `roadmap/spec_patch.py`
  - `executor.py`: `cli_portify/executor.py` → `roadmap/executor.py`
  - `commands.py`: `cli_portify/commands.py` → `roadmap/commands.py`
- **Acceptance**: All file path references in roadmap match the spec's `src/superclaude/cli/roadmap/` package.
- **Traces**: DEV-001, DEV-002, DEV-003

### TASK-001: Fix test file paths in roadmap (DEV-004)

- **Compliance**: LIGHT
- **Priority**: BLOCKING
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: Update roadmap test file references to match the spec:
  - `tests/cli_portify/test_spec_patch.py` → `tests/roadmap/test_accept_spec_change.py`
  - `tests/cli_portify/test_auto_resume.py` → `tests/roadmap/test_spec_patch_cycle.py`
- Also update the "Files Created" table and all verification commands.
- **Acceptance**: Test paths in roadmap match spec §4.1.
- **Traces**: DEV-004

### TASK-002: Fix CLI command hierarchy in roadmap (DEV-009)

- **Compliance**: LIGHT
- **Priority**: BLOCKING
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: Change Phase 2 milestone from `superclaude accept-spec-change <output_dir>` to `superclaude roadmap accept-spec-change <output_dir>`. The command must be registered as a subcommand of `roadmap_group` in `commands.py`, not as a top-level Click command.
- **Acceptance**: All CLI invocation references in roadmap use `superclaude roadmap accept-spec-change`.
- **Traces**: DEV-009

### TASK-003: Fix FR numbering in roadmap (DEV-006)

- **Compliance**: LIGHT
- **Priority**: LOW
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: Either:
  - (a) Replace `FR-001` through `FR-013` with spec's `FR-2.24.2.1` through `FR-2.24.2.13`, OR
  - (b) Add a mapping table at the top of the roadmap: `FR-001 = FR-2.24.2.1`, etc.
- Option (b) is recommended for readability.
- **Acceptance**: Unambiguous traceability between roadmap FR references and spec FR IDs.
- **Traces**: DEV-006

### TASK-004: Remove or align invented AC/NFR numbers (DEV-005, DEV-007)

- **Compliance**: LIGHT
- **Priority**: LOW
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**:
  - AC-12, AC-13, AC-14: Map these to their underlying FR requirements (FR-2.24.2.12 logging, FR-2.24.2.10 write failure, FR-2.24.2.4 parse errors) instead of inventing new AC numbers.
  - NFR-006, NFR-008: Replace with spec section references (§4.4 for import isolation, §4.4 for public API surface).
- **Acceptance**: No AC or NFR IDs in roadmap that don't exist in the spec. All references trace to spec sections.
- **Traces**: DEV-005, DEV-007

### TASK-005: Add `started_at` fallback policy to spec (DEV-010)

- **Compliance**: LIGHT
- **Priority**: MEDIUM
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/release-spec-accept-spec-change.md`
- **Description**: Add to FR-2.24.2.9 Condition 2: "If `started_at` is absent from the step state, treat Condition 2 as not met (fail-closed). The auto-resume cycle does not fire; the operator retains `accept-spec-change` as the explicit CLI fallback."
- **Acceptance**: FR-2.24.2.9 explicitly defines behavior when `started_at` is absent.
- **Traces**: DEV-010

### TASK-006: Align function signature documentation (DEV-011)

- **Compliance**: LIGHT
- **Priority**: LOW
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: Update Phase 1.1 function signature from `prompt_accept_spec_change(output_dir: Path, auto_accept: bool = False) -> int` to match the spec's §2.1 call chain. The `output_dir` comes from the CLI layer (commands.py), while `auto_accept` threads from `execute_roadmap()`. Clarify that `prompt_accept_spec_change` receives both parameters as the spec's §5.1 implies.
- **Acceptance**: Function signature in roadmap is consistent with spec §2.1 and §5.1.
- **Traces**: DEV-011

### TASK-007: Add DeviationRecord reference to roadmap (DEV-012)

- **Compliance**: LIGHT
- **Priority**: LOW
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: Add a reference in Phase 1.2 to the spec's §4.5 `DeviationRecord` frozen dataclass with its 7 fields and invariants. This is the required data model for parsed deviation records.
- **Acceptance**: Roadmap Phase 1.2 references `DeviationRecord` from spec §4.5.
- **Traces**: DEV-012

### TASK-008: Note `_find_qualifying_deviation_files()` as implementation detail (DEV-008)

- **Compliance**: LIGHT
- **Priority**: LOW
- **Files Modified**: `.dev/releases/current/2.24.2-Accept-Spec-Change/roadmap.md`
- **Description**: In Phase 3.6, add a note that `_find_qualifying_deviation_files()` is an implementation-level helper not specified in the spec. Alternatively, add it to the spec's §4.4 module dependency graph.
- **Acceptance**: Roadmap clearly distinguishes spec-mandated vs implementation-detail functions.
- **Traces**: DEV-008

---

## Implementation Tasks

These tasks implement the actual feature after roadmap fixes are applied.
They follow the spec's §4.6 Implementation Order.

### TASK-100: Create `spec_patch.py` — DeviationRecord + scan + parse (Phase 1.1-1.2)

- **Compliance**: STANDARD
- **Priority**: HIGH — critical path
- **Files Created**: `src/superclaude/cli/roadmap/spec_patch.py`
- **Dependencies**: None (leaf module)
- **Description**: Implement the `spec_patch.py` leaf module with:
  1. `DeviationRecord` frozen dataclass (spec §4.5): 7 fields, invariants (uppercase disposition, bool spec_update_required, float mtime)
  2. `scan_accepted_deviation_records(output_dir: Path) -> list[DeviationRecord]`: Glob `dev-*-accepted-deviation.md`, parse YAML frontmatter, filter `disposition: ACCEPTED` (case-insensitive) + `spec_update_required: true` (YAML boolean). Warn-and-skip on parse errors. String `"true"` MUST be rejected.
  3. `update_spec_hash(state_path: Path, new_hash: str) -> None`: Atomic write via `.tmp` + `os.replace()`. Only modifies `spec_hash`, preserves all other keys verbatim.
  4. `prompt_accept_spec_change(output_dir: Path, auto_accept: bool = False) -> int`: Full interactive flow per FR-2.24.2.1 through FR-2.24.2.7.
- **Constraints**:
  - Imports ONLY stdlib + PyYAML (NFR-4, §4.4 leaf module isolation)
  - No imports from `executor.py` or `commands.py`
  - No `ClaudeProcess` or subprocess invocation
- **Acceptance Criteria**: FR-2.24.2.1 through FR-2.24.2.7, AC-1 through AC-5a, AC-11
- **Traces**: Spec §4.1, §4.5, §4.6 steps 1-2

### TASK-101: Register `accept-spec-change` CLI command (Phase 2)

- **Compliance**: STANDARD
- **Priority**: HIGH — critical path
- **Files Modified**: `src/superclaude/cli/roadmap/commands.py`
- **Dependencies**: TASK-100
- **Description**: Add `accept-spec-change` as a subcommand of the existing `roadmap_group` Click group:
  - `@roadmap_group.command("accept-spec-change")`
  - Single positional argument: `output_dir` as `click.Path(exists=True)`
  - Zero optional flags (spec §5.1 — evidence records serve as authorization)
  - Import only from `spec_patch.py` (dependency: `commands.py → spec_patch.py`)
  - Call `prompt_accept_spec_change(Path(output_dir))` and `sys.exit()` with return code
- **Acceptance Criteria**: `superclaude roadmap accept-spec-change <output_dir>` works end-to-end
- **Traces**: Spec §5.1, DEV-009 fix

### TASK-102: Add PyYAML dependency (Phase 2)

- **Compliance**: LIGHT
- **Priority**: HIGH
- **Files Modified**: `pyproject.toml`
- **Dependencies**: None (can parallel with TASK-100)
- **Description**:
  1. Check if PyYAML is already a transitive dependency: `uv pip list | grep -i yaml`
  2. If not present, add `pyyaml>=6.0` to `[project.dependencies]` in `pyproject.toml`
  3. Run `uv pip install -e .` to verify resolution
- **Acceptance Criteria**: `import yaml` succeeds in the project environment
- **Traces**: Spec §4.2

### TASK-103: Extend `execute_roadmap()` signature + capture initial hash (Phase 3a)

- **Compliance**: STANDARD
- **Priority**: HIGH — critical path
- **Files Modified**: `src/superclaude/cli/roadmap/executor.py`
- **Dependencies**: TASK-100
- **Description**:
  1. Add `auto_accept: bool = False` parameter to `execute_roadmap()` (backward-compatible default, AC-10)
  2. At the top of `execute_roadmap()`, before `execute_pipeline()` is called, capture:
     ```python
     initial_spec_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
     ```
  3. Initialize local variable `_spec_patch_cycle_count = 0` (FR-2.24.2.11 recursion guard — MUST be local, not module/class/global)
- **Acceptance Criteria**: AC-10 (backward compat), FR-2.24.2.8, FR-2.24.2.11
- **Traces**: Spec §5.2, §4.6 step 4

### TASK-104: Implement `_apply_resume_after_spec_patch()` + detection (Phase 3b)

- **Compliance**: STRICT
- **Priority**: HIGH — most complex requirement, highest risk
- **Files Modified**: `src/superclaude/cli/roadmap/executor.py`
- **Dependencies**: TASK-100, TASK-103
- **Description**: Implement the auto-resume cycle after spec-fidelity FAIL:

  **Detection gate (FR-2.24.2.9)** — after `execute_pipeline()` returns with spec-fidelity FAIL:
  1. Check `_spec_patch_cycle_count >= 1` → skip (log suppression message per FR-2.24.2.12)
  2. Check qualifying deviation files exist with `mtime > datetime.fromisoformat(state["steps"]["spec-fidelity"]["started_at"]).timestamp()` — CRITICAL: proper type conversion. If `started_at` absent → condition not met (fail-closed, TASK-005).
  3. Check `hashlib.sha256(config.spec_file.read_bytes()).hexdigest() != initial_spec_hash` — use local var, NOT `state["spec_hash"]`

  **Disk-reread sequence (FR-2.24.2.10)** — six steps, no shortcuts:
  1. `fresh_state = read_state(output_dir)` (disk reread)
  2. `new_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()`
  3. Atomic write `new_hash` into `fresh_state["spec_hash"]` (`.tmp` + `os.replace()`)
     - On write failure: abort cycle, print `[roadmap] ERROR: ...` to stderr, fall through to normal halt
  4. `post_write_state = read_state(output_dir)` (second disk reread — THIS is what _apply_resume gets)
  5. `steps = _build_steps(config)`
  6. `_apply_resume(post_write_state, steps)`

  **Cycle logging (FR-2.24.2.12)**:
  - Entry: `[roadmap] Spec patched by subprocess. Found N accepted deviation record(s).`
  - Entry: `[roadmap] Triggering spec-hash sync and resume (cycle 1/1).`
  - Completion: `[roadmap] Spec-patch resume cycle complete.`
  - Suppression: `[roadmap] Spec-patch cycle already exhausted (cycle_count=1). Proceeding to normal failure.`

  **Cycle exhaustion (FR-2.24.2.13)**: If spec-fidelity still fails after resume, fall through to `_format_halt_output()` + `sys.exit(1)` using second-run results only.

- **Constraints**:
  - No modification to existing `_apply_resume()` logic
  - No new public symbols (all new functions are `_` prefixed)
  - Increment `_spec_patch_cycle_count` before entering cycle
- **Acceptance Criteria**: AC-5a, AC-5b, AC-6, AC-7, AC-8, AC-9, AC-12, AC-13
- **Traces**: Spec FR-2.24.2.9 through FR-2.24.2.13, §4.6 step 5

### TASK-105: Unit tests — `test_accept_spec_change.py` (Phase 1.4 + Phase 4)

- **Compliance**: STANDARD
- **Priority**: HIGH
- **Files Created**: `tests/roadmap/test_accept_spec_change.py`
- **Dependencies**: TASK-100, TASK-101
- **Description**: Implement unit tests covering spec §8.1:
  1. `TestLocateStateFile`: Missing/unreadable state file → exit 1 (FR-1, AC-1)
  2. `TestRecomputeHash`: Missing spec file → exit 1 (FR-2)
  3. `TestHashMismatchCheck`: Hash equality → exit 0; idempotency (FR-3, AC-3)
  4. `TestScanDeviationRecords`: Glob, parse, filter, zero-records exit (FR-4, AC-1)
     - Malformed YAML → warning + skip (AC-14)
     - String `"true"` rejection for `spec_update_required`
     - YAML 1.1 boolean coercion: `yes`, `on`, `1`, `True`, `TRUE` all accepted
  5. `TestPromptBehavior`: Input normalization (only y/Y confirms), non-interactive detection (FR-5, AC-4, AC-11)
  6. `TestAtomicWrite`: Only `spec_hash` changed, all other keys preserved (FR-6, AC-2)
     - Pre-existing `.tmp` file overwritten
  7. `TestConfirmationOutput`: Both hashes truncated to 12 chars (FR-7)
  8. `TestIdempotency`: Run twice → second exits 0 (AC-3)
  9. `TestAbortReadOnly`: Answer N → mtime unchanged (AC-4)
- **Acceptance Criteria**: All unit AC (AC-1 through AC-5a, AC-11, AC-14) covered
- **Traces**: Spec §8.1

### TASK-106: Integration tests — `test_spec_patch_cycle.py` (Phase 3 + Phase 4)

- **Compliance**: STRICT
- **Priority**: HIGH
- **Files Created**: `tests/roadmap/test_spec_patch_cycle.py`
- **Dependencies**: TASK-103, TASK-104
- **Description**: Implement integration tests covering spec §8.2:
  1. `TestCycleGuard`: Cycle fires at most once per invocation (FR-11, AC-6)
  2. `TestDiskReread`: `_apply_resume()` uses post-write disk state, not pre-write (FR-10, AC-7)
  3. `TestConditionChecks`: All three conditions required; mtime type conversion; `initial_spec_hash` used not `state["spec_hash"]` (FR-9)
     - Missing `started_at` → condition not met → normal failure
  4. `TestAutoAccept`: `auto_accept=True` skips prompt; `False` prompts (FR-8, AC-9)
  5. `TestBackwardCompat`: `execute_roadmap()` callable without `auto_accept` (AC-10)
  6. `TestCycleExhaustion`: Second fidelity fail → exit 1, no loop (FR-13, AC-8)
  7. `TestWriteFailure`: Atomic write failure → cycle abort → normal halt (FR-10 Step 3, AC-13)
  8. `TestLogging`: Entry, completion, suppression messages with `[roadmap]` prefix (FR-12, AC-12)
- **Acceptance Criteria**: All integration AC (AC-5b through AC-10, AC-12, AC-13) covered
- **Traces**: Spec §8.2

---

## Validation Tasks

### TASK-200: Module isolation verification (Phase 5.2)

- **Compliance**: STANDARD
- **Priority**: MEDIUM
- **Dependencies**: TASK-100, TASK-104
- **Description**:
  1. Verify `spec_patch.py` imports only stdlib + PyYAML: `grep "^import\|^from" src/superclaude/cli/roadmap/spec_patch.py`
  2. Verify no circular dependencies: `spec_patch.py` must not import from `executor.py` or `commands.py`
  3. Verify no new public symbols in `executor.py` beyond `execute_roadmap()` parameter
  4. Verify no `ClaudeProcess` usage in `spec_patch.py`
- **Acceptance Criteria**: NFR-4, NFR-6 (mapped to §4.4), NFR-8 (mapped to §4.4)
- **Traces**: Spec §4.4, NFR-1 through NFR-5

### TASK-201: Full AC matrix validation (Phase 5.1)

- **Compliance**: STANDARD
- **Priority**: MEDIUM
- **Dependencies**: TASK-105, TASK-106
- **Description**: Run full test suite and verify every AC is covered:
  ```bash
  uv run pytest tests/roadmap/test_accept_spec_change.py tests/roadmap/test_spec_patch_cycle.py -v
  ```
  Map each AC (AC-1 through AC-14) to at least one passing test. Report any gaps.
- **Acceptance Criteria**: All 14 ACs mapped to passing automated tests
- **Traces**: Spec §8.1, §8.2

### TASK-202: Documentation updates (Phase 5.3)

- **Compliance**: LIGHT
- **Priority**: LOW
- **Dependencies**: TASK-101, TASK-104
- **Description**:
  1. CLI help text for `accept-spec-change` (Click docstring)
  2. Docstring on `_apply_resume_after_spec_patch()` documenting single-writer assumption (NFR-5, R6)
  3. Docstring on `spec_patch.py` module noting YAML 1.1 boolean coercion contract (R8)
  4. Code comments on mtime comparison documenting strict `>` and HFS+/NFS limitation (R7)
- **Acceptance Criteria**: All documentation items from spec §7 risks are addressed in code
- **Traces**: Spec NFR-5, Risk R1, R6, R7, R8

### TASK-203: Release gate verification (Phase 5.4-5.5)

- **Compliance**: STANDARD
- **Priority**: MEDIUM
- **Dependencies**: TASK-200, TASK-201, TASK-202
- **Description**: Final verification checklist:
  1. All acceptance criteria mapped to automated tests (14 AC + 5 NFR)
  2. No circular dependency introduced
  3. No new public API beyond the defaulted `execute_roadmap()` parameter
  4. No subprocess invocation in `spec_patch.py`
  5. Resume behavior skips upstream phases after accepted spec change (AC-5b demonstrated)
  6. At least one full happy-path AND one exhausted-retry path demonstrated
  7. Run: `make sync-dev && make verify-sync && make test && make lint`
- **Acceptance Criteria**: All 7 gate checks pass
- **Traces**: Spec §8, roadmap Phase 5.4

---

## Execution Order and Dependencies

```
TASK-000 ─┐
TASK-001 ─┤
TASK-002 ─┼── Roadmap fixes (parallel, all LIGHT) ──┐
TASK-003 ─┤                                          │
TASK-004 ─┤                                          │
TASK-005 ─┤                                          │
TASK-006 ─┤                                          │
TASK-007 ─┤                                          │
TASK-008 ─┘                                          │
                                                     v
TASK-102 ─────────────────────────────────────── (parallel with TASK-100)
                                                     │
TASK-100 ── spec_patch.py ───────────────────────────┤
    │                                                 │
    ├── TASK-101 ── commands.py ──────────────────────┤
    │       │                                         │
    │       └── TASK-105 ── unit tests ───────────────┤
    │                                                 │
    └── TASK-103 ── executor signature ───────────────┤
            │                                         │
            └── TASK-104 ── auto-resume cycle ────────┤
                    │                                 │
                    └── TASK-106 ── integration tests ┤
                                                      │
                                                      v
                              TASK-200 ── module isolation ──┐
                              TASK-201 ── AC matrix ─────────┼── TASK-203 (release gate)
                              TASK-202 ── documentation ─────┘
```

## Summary

| Category | Count | Compliance |
|----------|-------|------------|
| Roadmap document fixes | 9 (TASK-000 through TASK-008) | LIGHT |
| Implementation | 5 (TASK-100 through TASK-104) | STANDARD/STRICT |
| Test authoring | 2 (TASK-105, TASK-106) | STANDARD/STRICT |
| Validation | 4 (TASK-200 through TASK-203) | STANDARD/LIGHT |
| **Total** | **20 tasks** | |

**Critical path**: TASK-000/001/002 → TASK-100 → TASK-103 → TASK-104 → TASK-106 → TASK-201 → TASK-203

**Highest risk task**: TASK-104 (`_apply_resume_after_spec_patch`) — the six-step disk-reread sequence and three-condition detection gate are the most complex requirements with the most subtle correctness constraints (type conversion, state freshness, atomicity).
