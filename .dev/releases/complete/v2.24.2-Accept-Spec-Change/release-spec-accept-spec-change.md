```yaml
---
title: "accept-spec-change Command + Auto-Resume on Spec Patch"
version: "1.0.0"
status: complete
feature_id: FR-2.24.2
parent_feature: v2.24-cli-portify-cli-v4
spec_type: new_feature
complexity_score: 0.65
complexity_class: moderate
target_release: "2.24.2"
authors: [user, claude]
created: 2026-03-13
quality_scores:
  clarity: 8.0
  completeness: 8.5
  testability: 9.0
  consistency: 8.0
  overall: 8.5
---
```

## 1. Problem Statement

When the spec file is edited to formalize an accepted deviation (a documentation sync, not a
functional change), the stored `spec_hash` in `.roadmap-state.json` goes stale. `--resume`
treats the hash mismatch as a functional spec change, sets `force_extract = True`, and
cascades a full 28-minute pipeline re-run. This discards all valid upstream outputs
(roadmap files, debate transcript, diff, etc.) unnecessarily.

The root cause: `_apply_resume()` has no way to distinguish a "spec updated to match
accepted roadmap architecture" edit from a "spec requirements genuinely changed" edit.

### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| `_apply_resume()` sets `force_extract = True` on any spec hash mismatch | `executor.py:1068-1079` | Full 28-min re-run on documentation-only changes |
| No mechanism to acknowledge non-functional spec edits | `executor.py:822` (missing `auto_accept` param) | User must re-run entire pipeline or manually edit state JSON |
| Sprint runner cannot proceed non-interactively after deviation acceptance | Pipeline design gap | Automated pipeline halts on accepted deviations |

### 1.2 Scope Boundary

**In scope**: Deviations where `spec_update_required: true` in the accepted deviation
record. Two deliverables: (1) `superclaude roadmap accept-spec-change` CLI command,
(2) auto-resume cycle inside `execute_roadmap()` when a Claude subprocess patches the spec.

**Out of scope**: Deviations where `spec_update_required: false` — they require a different
mechanism (gate override records, not spec hash acknowledgement).

## 2. Solution Overview

Two components that together eliminate unnecessary pipeline re-runs after spec documentation
syncs:

1. **CLI command `accept-spec-change`**: A manual, evidence-gated command that updates
   `spec_hash` in `.roadmap-state.json` when the spec edit is a documentation sync (not a
   functional change). Requires at least one `dev-*-accepted-deviation.md` file with
   `disposition: ACCEPTED` and `spec_update_required: true` as evidence.

2. **Auto-resume cycle in `execute_roadmap()`**: When a Claude subprocess patches the spec
   during pipeline execution, `execute_roadmap()` detects the deviation evidence and
   automatically triggers a spec-hash sync + resume without requiring a separate manual step.

Neither component modifies the existing `_apply_resume()` function. The changes are additive:
a new module (`spec_patch.py`), a new CLI command, and two new private functions in
`executor.py`. The `execute_roadmap()` signature gains one keyword argument (`auto_accept`)
with a backward-compatible default.

### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Process architecture | Same-process control flow | Separate subprocess call to `accept-spec-change` | Avoids race conditions; disk-reread provides safety |
| State freshness | Disk-reread at resume boundary | Reuse in-memory state | Prevents stale state bugs; guarantees `_apply_resume()` sees updated `spec_hash` |
| Non-interactive control | `auto_accept` parameter on `execute_roadmap()` | CLI flag `--auto-accept` | Internal parameter keeps CLI surface clean; sprint runner passes `True` directly |
| Recursion guard | Local counter, max 1 cycle | Persistent state-based guard | Per-invocation scope prevents cross-run interference |
| CLI surface | No flags on `accept-spec-change` | `--force`, `--yes` flags | Evidence-based design: deviation records ARE the authorization |
| Module isolation | `spec_patch.py` imports only stdlib + PyYAML | Import `read_state`/`write_state` from `executor.py` | Prevents circular dependency risk |

### 2.2 Workflow / Data Flow

```
Manual path:
  roadmap run → spec-fidelity FAIL → human reviews → human edits spec
  → human writes dev-NNN-accepted-deviation.md
  → accept-spec-change <output_dir>  [prompts y/N, updates hash]
  → roadmap run --resume  [skips to spec-fidelity]

Automatic path:
  roadmap run → spec-fidelity FAIL → remediation subprocess runs
  → subprocess patches spec + writes deviation record
  → execute_roadmap() detects conditions (FR-9)
  → disk-reread + spec_hash update (FR-10)
  → _apply_resume() skips to spec-fidelity → re-run
  → PASS: pipeline continues | FAIL: normal failure (no second cycle)
```

## 3. Functional Requirements

### FR-2.24.2.1: Locate state file

**Description**: Read `.roadmap-state.json` from `output_dir`. If absent or unreadable,
exit with a clear error: "No .roadmap-state.json found in <output_dir>. Run `roadmap run` first."

**Acceptance Criteria**:
- [ ] Command exits 1 with clear message when state file is missing

**Dependencies**: None

### FR-2.24.2.2: Recompute current spec hash

**Description**: Load `spec_file` path from the state file. Recompute `sha256(spec_file.read_bytes())`.
If the file is missing, exit with error: "Spec file not found: <path>".

**Acceptance Criteria**:
- [ ] Command exits 1 with clear message when spec file is missing

**Dependencies**: FR-2.24.2.1

### FR-2.24.2.3: Check for hash mismatch

**Description**: If `current_hash == state["spec_hash"]`, print:
"Spec hash is already current. Nothing to do." and exit 0.

**Hash equality edge cases**:
- If `state["spec_hash"]` is absent, null, or empty string, treat as a mismatch and
  proceed to FR-2.24.2.4 (do not exit 0).
- Hash comparison uses byte-exact string equality on the hex digest. No normalization
  (e.g., case folding) is applied.
- Hash equality covers two legitimate cases that the command cannot distinguish:
  (a) `accept-spec-change` was previously run successfully for this change — correct
  idempotent behavior; (b) the spec file was reverted to match the stored hash — treated
  the same as (a), "nothing to do."

**Acceptance Criteria**:
- [ ] AC-3: `accept-spec-change` is idempotent — running twice does not corrupt state

**Dependencies**: FR-2.24.2.1, FR-2.24.2.2

### FR-2.24.2.4: Scan for accepted deviation evidence

**Description**: Glob `output_dir` for files matching `dev-*-accepted-deviation.md`.
Parse the YAML frontmatter of each file. Collect records where:
  - `disposition: ACCEPTED` (case-insensitive string match)
  - `spec_update_required: true` (YAML boolean `true`, NOT the string `"true"`)

**Frontmatter schema** — canonical example:
```yaml
---
id: DEV-001
disposition: ACCEPTED
spec_update_required: true
affects_spec_sections:
  - "4.1"
  - "4.4"
acceptance_rationale: debate-consensus
---
```

**Field defaults and parse-error handling**:
- If `disposition` is absent, treat as not-ACCEPTED (record does not match).
- If `spec_update_required` is absent, treat as `false` (record does not match).
- `spec_update_required` MUST be a YAML boolean (`true`/`false`). The string `"true"` does
  NOT match — YAML parsers return a Python `str`, not `bool`, for quoted values.
- If YAML frontmatter parsing raises an exception on any file, emit a warning to stderr:
  `[roadmap] WARNING: Could not parse frontmatter in <filename>. Skipping.`
  Continue processing remaining files. A parse warning does not change the exit code.
- If all files fail to parse, the effective matching count is zero and the zero-records
  path below applies.

If zero such records are found, refuse to update and exit 1 with message:
"Spec file has changed but no accepted deviation records with spec_update_required: true
were found in <output_dir>. If this is a functional spec change, run `roadmap run` without
--resume. If it is a documentation sync, create a dev-NNN-accepted-deviation.md record
with spec_update_required: true before running this command."

**Acceptance Criteria**:
- [ ] AC-1: `accept-spec-change` exits 1 with clear message when no accepted deviation records are found

**Dependencies**: FR-2.24.2.1, FR-2.24.2.2

### FR-2.24.2.5: Display evidence summary and prompt (interactive mode)

**Description**: Print a summary of each matching accepted deviation record:
```
Spec file changed. Found N accepted deviation record(s) with spec_update_required: true:

  DEV-001  HIGH  affects_spec_sections: 4.1, 4.4
           acceptance_rationale: debate-consensus
  DEV-NNN  ...

Updating spec_hash in .roadmap-state.json will allow --resume to skip the full cascade.
Accept this spec change as a documentation sync? [y/N]:
```

**Input normalization**: Only `y` or `Y` (case-insensitive single character) confirms.
Any other input — including `yes`, `YES`, empty string (Enter only), or any other string —
is treated as N (abort).

**Non-interactive detection**: Non-interactive mode is detected by `not sys.stdin.isatty()`.
If non-interactive and `auto_accept=False`, treat user input as N and exit 0 with
"Aborted." The state file is not touched.

If user answers N (or non-interactive and no auto_accept), exit 0 with "Aborted."

**Acceptance Criteria**:
- [ ] AC-4: `accept-spec-change` never touches state file if user answers N
- [ ] AC-11: When `auto_accept=False` and stdin is not a tty (non-interactive environment such as CI), `accept-spec-change` exits 0 with "Aborted." and does not modify `.roadmap-state.json`

**Dependencies**: FR-2.24.2.4

### FR-2.24.2.6: Update spec_hash atomically

**Description**: On confirmation, write updated state to `.roadmap-state.json` using the atomic write
pattern: write to `.roadmap-state.json.tmp` (on the same filesystem), then `os.replace()`.
If `.tmp` already exists on entry (e.g., from a previous crash), overwrite it.
`os.replace()` is atomic on POSIX when source and destination are on the same filesystem.
Only `spec_hash` is modified. All other keys (`steps`, `fidelity_status`, `validation`,
`remediate`, `certify`, `agents`, `depth`, `last_run`) are preserved verbatim.

**Acceptance Criteria**:
- [ ] AC-2: `accept-spec-change` updates only `spec_hash` in state file — all other keys preserved
- [ ] AC-5a: `accept-spec-change` updates `spec_hash` to the value that `_apply_resume()` will compare against `sha256(spec_file)`, allowing it to skip upstream steps

**Dependencies**: FR-2.24.2.5

### FR-2.24.2.7: Confirmation output

**Description**: Print:
```
[roadmap] spec_hash updated.
  Old: <old_hash[:12]>...
  New: <new_hash[:12]>...
  Accepted deviations: DEV-001, DEV-NNN
Run `superclaude roadmap run <spec_file> --resume` to continue from the failing step.
```
Exit 0.

**Acceptance Criteria**:
- [ ] Both hashes truncated to 12 chars in output
- [ ] AC-5b (integration): After `accept-spec-change` runs, executing `roadmap run <spec_file> --resume` proceeds from spec-fidelity without re-running extract, generate, diff, debate, score, merge, or test-strategy steps

**Dependencies**: FR-2.24.2.6

### FR-2.24.2.8: auto_accept parameter

**Description**: `execute_roadmap(config, resume=False, no_validate=False, auto_accept=False)`
When `auto_accept=True`, the spec-patch resume cycle skips the interactive prompt and
proceeds automatically if evidence is found. When `auto_accept=False` (default), the
cycle still runs but prompts the user (same as FR-2.24.2.5 above).

**Call chain**: `auto_accept` is threaded through the entire call chain as the single
source of truth for whether the prompt is displayed:
```
execute_roadmap(auto_accept)
  → _apply_resume_after_spec_patch(auto_accept)
    → prompt_accept_spec_change(auto_accept)
```
No other mechanism controls interactivity. When `auto_accept=False` and
`not sys.stdin.isatty()` (non-interactive environment), `_apply_resume_after_spec_patch()`
does NOT prompt and does NOT proceed with the cycle — it falls through to normal failure
handling.

**Acceptance Criteria**:
- [ ] AC-9: `auto_accept=True` skips prompt; `auto_accept=False` (default) prompts user
- [ ] AC-10: `execute_roadmap()` signature remains backward-compatible (`auto_accept` defaults to False)

**Dependencies**: None (executor-side)

### FR-2.24.2.9: Post-spec-fidelity-FAIL detection

**Description**: After `execute_pipeline()` returns with spec-fidelity in FAIL status, check:
  1. Has `_spec_patch_cycle_count` already fired once? If yes, skip cycle (surface failure normally).
  2. Does `output_dir` contain `dev-*-accepted-deviation.md` files with
     `disposition: ACCEPTED` AND `spec_update_required: true` that were written AFTER
     the spec-fidelity step started?

     A file qualifies if:
     ```python
     os.path.getmtime(file) > datetime.fromisoformat(
         state["steps"]["spec-fidelity"]["started_at"]
     ).timestamp()
     ```
     The operator is strict `>` (not `>=`).

     **Absent `started_at` handling**: If `started_at` is absent from the step state
     (e.g., the step was never started, or the state was created by an older version),
     treat Condition 2 as **not met** (fail-closed). The auto-resume cycle does not fire;
     the operator retains `accept-spec-change` as the explicit CLI fallback. An optimization
     that doesn't fire is preferable to one that fires incorrectly.

     **Type note**: `started_at` is stored as an ISO 8601 string written by
     `datetime.now(timezone.utc).isoformat()` (e.g., `"2026-03-13T10:00:00.123456+00:00"`).
     `os.path.getmtime()` returns a Unix timestamp float. These types are NOT directly
     comparable in Python. Always convert via
     `datetime.fromisoformat(started_at).timestamp()` before the comparison. Comparing
     the raw string to the float will always evaluate False.

     **Known limitation**: On filesystems with 1-second mtime resolution (e.g., HFS+,
     some network mounts), files written in the same second as `started_at` will NOT
     satisfy Condition 2. Implementations may use `>=` with a documented rationale,
     but the default is `>`.
  3. Has the spec file hash changed since the run started (compare current sha256 to
     `config.spec_file` hash at run start)?

  The "hash at run start" is captured into a local variable `initial_spec_hash` at the
  top of `execute_roadmap()`, before `execute_pipeline()` is called:
  ```python
  initial_spec_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()
  ```
  Condition 3 evaluates: `hashlib.sha256(config.spec_file.read_bytes()).hexdigest() != initial_spec_hash`.
  `state["spec_hash"]` is NOT used for this comparison — it may reflect a prior run's hash,
  not the hash at the start of the current invocation.

  All three conditions must be true to trigger the cycle. If any is false, fall through
  to normal failure handling.

**Acceptance Criteria**:
- [ ] All three conditions must be true to trigger cycle
- [ ] mtime comparison uses proper type conversion (ISO string → timestamp float)
- [ ] `initial_spec_hash` (local var) used for Condition 3, not `state["spec_hash"]`

**Dependencies**: FR-2.24.2.8, FR-2.24.2.11

### FR-2.24.2.10: Disk-reread at resume boundary

**Description**: Before re-running `_apply_resume()`, execute the following steps in order:

  1. Re-read `.roadmap-state.json` from disk → `fresh_state`
     (do not reuse `results` or any in-memory state from the failed run)
  2. Recompute `new_hash = hashlib.sha256(config.spec_file.read_bytes()).hexdigest()`
  3. Write `new_hash` into `fresh_state["spec_hash"]`, write atomically to disk
     (same pattern as FR-2.24.2.6: write to `.roadmap-state.json.tmp`, then `os.replace()`)
     **Failure path**: If the atomic write in Step 3 fails (e.g., disk full, permission
     error), abort the auto-resume cycle immediately. Print to stderr:
     `[roadmap] ERROR: Failed to update spec_hash during auto-resume cycle: <error>. Falling through to normal failure.`
     Do NOT call `_apply_resume()`. Fall through to `_format_halt_output` / `sys.exit(1)`.
     The state file is guaranteed unmodified if Step 3 fails (atomic write semantics).
  4. Re-read `.roadmap-state.json` from disk again → `post_write_state`
     **This is the state object passed to `_apply_resume()`.** Do NOT use `fresh_state`
     from Step 1 — it does not yet reflect the updated `spec_hash`.
  5. Rebuild the steps list from scratch via `_build_steps(config)`
  6. Call `_apply_resume(post_write_state, steps)` using the Step 4 state

**Concurrency constraint**: The auto-resume cycle assumes no concurrent writer modifies
`.roadmap-state.json` between Steps 1 and 3. Concurrent modification is not protected
against (no file locking). The roadmap pipeline must not be running concurrently.

**State Trace (happy path)**:
```
Before auto-resume cycle (state after first spec-fidelity FAIL):
  state["steps"]["spec-fidelity"]["status"] = "FAIL"
  state["spec_hash"] = "<old_hash>"      ← stale, does not match current spec file
  _spec_patch_cycle_count = 0

FR-10 Step 1: Re-read state from disk → fresh_state (spec_hash still "<old_hash>")
FR-10 Step 2: new_hash = sha256(spec_file)
FR-10 Step 3: Write new_hash to .roadmap-state.json atomically
              → state on disk: spec_hash = "<new_hash>", all other keys unchanged
FR-10 Step 4: Re-read .roadmap-state.json → post_write_state
              (spec_hash = "<new_hash>")
FR-10 Step 5: steps = _build_steps(config)
FR-10 Step 6: _apply_resume(post_write_state, steps) runs with post_write_state

_apply_resume() sees:
  sha256(spec_file) == post_write_state["spec_hash"]  → hashes match → no force_extract
  post_write_state["steps"]["spec-fidelity"]["status"] = "FAIL" → will be re-run
  All upstream steps (extract, generate, diff, debate, score, merge, test-strategy) = PASS → skipped

Result: pipeline resumes from spec-fidelity only
```

**Acceptance Criteria**:
- [ ] AC-7: Auto-resume cycle re-reads state from disk — does not reuse in-memory results
- [ ] Atomic write failure aborts cycle and falls through to normal failure

**Dependencies**: FR-2.24.2.9

### FR-2.24.2.11: Recursion guard

**Description**: Increment `_spec_patch_cycle_count` before entering the cycle. On entry, if count >= 1,
skip. This is a local variable within the `execute_roadmap()` call — not persisted to
state. One `execute_roadmap()` invocation may trigger at most one spec-patch resume cycle.

`_spec_patch_cycle_count` MUST be a **local variable** declared inside `execute_roadmap()`.
It MUST NOT be a module-level, class-level, or global variable. Each call to
`execute_roadmap()` gets its own independent counter initialized to `0`. Two successive
calls to `execute_roadmap()` in the same process each get their own cycle counter. The
guard is per-invocation, not per-process.

**Acceptance Criteria**:
- [ ] AC-6: Auto-resume cycle fires at most once per `execute_roadmap()` invocation

**Dependencies**: None (executor-side)

### FR-2.24.2.12: Cycle outcome logging

**Description**: On cycle entry, print:
```
[roadmap] Spec patched by subprocess. Found N accepted deviation record(s).
[roadmap] Triggering spec-hash sync and resume (cycle 1/1).
```
On cycle completion (regardless of spec-fidelity pass/fail), print:
```
[roadmap] Spec-patch resume cycle complete.
```
If the FR-2.24.2.11 recursion guard fires (count >= 1) and the cycle is suppressed, print
immediately before falling through to `_format_halt_output`:
```
[roadmap] Spec-patch cycle already exhausted (cycle_count=1). Proceeding to normal failure.
```

**Acceptance Criteria**:
- [ ] Entry, completion, and suppression messages logged correctly

**Dependencies**: FR-2.24.2.11

### FR-2.24.2.13: Normal failure on cycle exhaustion

**Description**: If spec-fidelity still fails after the patched resume, `execute_roadmap()` falls through
to its normal failure path (`_format_halt_output`, `sys.exit(1)`). No second cycle.
`_format_halt_output` is called with the pipeline results from the post-resume execution
(the second spec-fidelity run). The spec-fidelity FAIL results from the first run are not
included in the final output. Operators inspecting the halt output will see only the
post-resume failure diagnostics.

**Acceptance Criteria**:
- [ ] AC-8: If spec-fidelity still fails after patched resume, pipeline exits 1 normally (no loop)

**Dependencies**: FR-2.24.2.10, FR-2.24.2.11

**Note on Claude subprocess responsibilities** (out of scope for this spec, noted for clarity):
The subprocess that patches the spec must:
- Write `dev-NNN-accepted-deviation.md` with `disposition: ACCEPTED` and
  `spec_update_required: true` BEFORE exiting
- Patch only the spec sections listed in `affects_spec_sections`
- Exit with status 0 on successful patch

The subprocess contract is defined in the spec-fidelity step prompt and remediation
tooling — not in this spec.

## 4. Architecture

### 4.1 New Files

| File | Purpose | Dependencies |
|------|---------|-------------|
| `src/superclaude/cli/roadmap/spec_patch.py` | Deviation record scanning, spec_hash atomic update, interactive prompt | stdlib + PyYAML only (leaf module) |
| `tests/roadmap/test_accept_spec_change.py` | Unit tests for AC-1 through AC-5b, AC-11 | spec_patch.py, pytest |
| `tests/roadmap/test_spec_patch_cycle.py` | Integration-level unit tests for AC-6 through AC-10 | executor.py, spec_patch.py, pytest |

### 4.2 Modified Files

| File | Change | Rationale |
|------|--------|-----------|
| `src/superclaude/cli/roadmap/commands.py` | Add `accept-spec-change` subcommand under `roadmap_group` | Deliverable 1 CLI entry point |
| `src/superclaude/cli/roadmap/executor.py` | Add `auto_accept` param to `execute_roadmap()`, add `_apply_resume_after_spec_patch()` helper, add recursion guard, capture `initial_spec_hash` at function entry | Deliverable 2 auto-resume cycle |
| `pyproject.toml` | Add `pyyaml>=6.0` to dependencies | Required for YAML frontmatter parsing in `spec_patch.py` |

### 4.4 Module Dependency Graph

```
commands.py  →  spec_patch.py   (accept-spec-change command body calls spec_patch functions)
executor.py  →  spec_patch.py   (calls update_spec_hash, scan_accepted_deviation_records)
spec_patch.py → (no imports from executor.py or commands.py)
```

`_apply_resume_after_spec_patch()` lives in `executor.py` and orchestrates the full
auto-resume cycle. It calls into `spec_patch.py` for hash and scanning logic — not the
reverse. All new functions in `executor.py` introduced by this spec use leading underscore
convention (`_apply_resume_after_spec_patch`) to mark them as private implementation
details of `executor.py`. The public API surface of `executor.py` remains `execute_roadmap()`
only — no new public symbols are introduced.

### 4.5 Data Models

```python
@dataclass(frozen=True)
class DeviationRecord:
    """Parsed and validated accepted deviation record."""
    id: str                           # e.g. "DEV-001"
    disposition: str                  # normalized to uppercase
    spec_update_required: bool        # YAML boolean only (True/False, yes/no, on/off)
    affects_spec_sections: list[str]  # may be empty list
    acceptance_rationale: str         # may be empty string
    source_file: Path                 # absolute path to the .md file
    mtime: float                      # os.path.getmtime() at scan time
```

Invariants:
- `disposition` is always stored uppercase after normalization
- `spec_update_required` is always a Python `bool` (never str). PyYAML `safe_load`
  treats `yes`, `on`, `1` as boolean `True` per YAML 1.1 spec — all forms are accepted.
- `mtime` is a Unix timestamp float, captured once at scan time

### 4.6 Implementation Order

```
1. spec_patch.py (DeviationRecord + scan + parse)  -- leaf module, no upstream deps
2. spec_patch.py (update_spec_hash + prompt)        -- [parallel with step 1]
3. commands.py (accept-spec-change command)          -- depends on 1, 2
4. executor.py (signature + initial_spec_hash)       -- independent of 1-3
5. executor.py (_apply_resume_after_spec_patch)      -- depends on 1, 4
6. test_accept_spec_change.py                        -- depends on 1, 2, 3
7. test_spec_patch_cycle.py                          -- depends on 4, 5
```

## 5. Interface Contracts

### 5.1 CLI Surface

```
superclaude roadmap accept-spec-change <output_dir>
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `output_dir` | `click.Path(exists=True)` | (required positional) | Directory containing `.roadmap-state.json` and `dev-*-accepted-deviation.md` files |

No flags. The command has zero optional arguments by design (clean CLI surface — evidence
records serve as authorization). `auto_accept` is an internal code parameter on
`execute_roadmap()`, not exposed on the CLI.

### 5.2 Internal API Surface (execute_roadmap signature change)

```python
execute_roadmap(
    config: RoadmapConfig,
    resume: bool = False,
    no_validate: bool = False,
    auto_accept: bool = False,   # NEW — AC-10: default=False preserves backward compat
) -> None
```

## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1 | Atomic write — no partial state corruption on power loss mid-write | Zero data loss on POSIX systems | `os.replace()` atomicity; test with crash simulation |
| NFR-2 | Read-only on abort — state file never touched if user answers N | No writes on abort path | Unit test: assert state file mtime unchanged after N |
| NFR-3 | Idempotent — running twice with same spec change is safe | Second run exits 0 cleanly | Unit test: run twice, assert state unchanged after first |
| NFR-4 | No pipeline execution — command only reads/writes state | Zero subprocess invocations | Code review: no `ClaudeProcess` usage in `spec_patch.py` |
| NFR-5 | Exclusive access — no concurrent write protection | Documented constraint | README/docstring warning; no file locking |

**Platform note (NFR-1)**: `os.replace()` is atomic on POSIX (Linux, macOS) when source and
destination are on the same filesystem. On Windows, `os.replace()` is atomic only on the
same volume; behavior on cross-volume writes is undefined. The primary deployment target is
POSIX. Windows support is best-effort.

**Concurrency note (NFR-5)**: `accept-spec-change` assumes exclusive write access to
`.roadmap-state.json` during execution. Running `accept-spec-change` concurrently with
`roadmap run` or another `accept-spec-change` invocation is not supported. No file locking
is implemented; the operator is responsible for preventing concurrent access.

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| TOCTOU window: state file modified between read and atomic write | Low | Medium — stale keys overwritten | NFR-5 documents exclusive access constraint; no concurrent `roadmap run` |
| Filesystem mtime resolution: files written in same second as `started_at` not detected | Low | Medium — auto-resume cycle fails to trigger | FR-9 Condition 2 documents strict `>` limitation; implementations may use `>=` |
| PyYAML boolean coercion: `yes`/`on`/`1` accepted as `true` | Low | Low — broader acceptance is intentional | Design note documents YAML 1.1 boolean forms as accepted |
| Deviation file with valid glob name but invalid YAML | Medium | Low — file skipped with warning | FR-4 parse-error handling: warn + skip, continue processing |
| `auto_accept=True` passed accidentally by a caller | Low | High — spec hash updated without human review | Parameter is internal (not CLI flag); only sprint runner uses it |

## 8. Test Plan

### 8.1 Unit Tests

| Test | File | Validates |
|------|------|-----------|
| `TestLocateStateFile` | `test_accept_spec_change.py` | FR-1: missing/unreadable state file exits 1 |
| `TestRecomputeHash` | `test_accept_spec_change.py` | FR-2: missing spec file exits 1 |
| `TestHashMismatchCheck` | `test_accept_spec_change.py` | FR-3: hash equality exits 0; AC-3 idempotency |
| `TestScanDeviationRecords` | `test_accept_spec_change.py` | FR-4: glob, parse, filter, zero-records exit; AC-1 |
| `TestPromptBehavior` | `test_accept_spec_change.py` | FR-5: input normalization, non-interactive; AC-4, AC-11 |
| `TestAtomicWrite` | `test_accept_spec_change.py` | FR-6: only spec_hash changed, all keys preserved; AC-2 |
| `TestConfirmationOutput` | `test_accept_spec_change.py` | FR-7: both hashes truncated to 12 chars |
| `TestIdempotency` | `test_accept_spec_change.py` | AC-3: second run exits 0 |

### 8.2 Integration Tests

| Test | Validates |
|------|-----------|
| `TestCycleGuard` | FR-11, AC-6: cycle fires at most once per invocation |
| `TestDiskReread` | FR-10, AC-7: `_apply_resume()` uses post-write disk state, not pre-write |
| `TestConditionChecks` | FR-9: all three conditions required; mtime type conversion; `initial_spec_hash` used (not `state["spec_hash"]`) |
| `TestAutoAccept` | FR-8, AC-9: `auto_accept=True` skips prompt; False prompts |
| `TestBackwardCompat` | AC-10: `execute_roadmap()` callable without `auto_accept` |
| `TestCycleExhaustion` | FR-13, AC-8: second fidelity fail exits 1, no loop |
| `TestWriteFailure` | FR-10 Step 3: atomic write failure falls through to normal failure |

## 9. Migration & Rollout

- **Breaking changes**: None. `execute_roadmap()` gains `auto_accept: bool = False` with
  backward-compatible default. All existing callers continue working without modification.
- **Backwards compatibility**: AC-10 explicitly requires that the signature change is
  backward-compatible. No existing CLI flags change.
- **Rollback plan**: Revert the commit. The only state-file change (`spec_hash` update) is
  safe to revert — the next `roadmap run` will recompute hashes from scratch.

## 10. Downstream Inputs

### For sc:roadmap
This spec produces 3 implementation themes for roadmap phasing:
1. **Phase: New module** — `spec_patch.py` (leaf module, no upstream deps)
2. **Phase: CLI command** — `accept-spec-change` in `commands.py` (depends on spec_patch)
3. **Phase: Executor integration** — `execute_roadmap()` changes + `_apply_resume_after_spec_patch()` (depends on spec_patch)

Parallelization: Phases 1 and 3 are partially independent (both depend on spec_patch but don't depend on each other). Tests follow after their respective phases.

### For sc:tasklist
Task breakdown should follow §4.6 Implementation Order. Key granularity boundaries:
- `spec_patch.py` is one task (small module, 3 public functions)
- `executor.py` changes are two tasks: (a) signature + `initial_spec_hash` capture, (b) `_apply_resume_after_spec_patch()` + `_find_qualifying_deviation_files()`
- `commands.py` is one task (single Click command)
- Each test file is one task

## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| Verification level for spec change safety | Evidence-based: requires dev-*-accepted-deviation.md with spec_update_required: true | Defines core authorization mechanism | Resolved |
| Manual vs auto invocation | Manual: prompted. Auto (subprocess): auto_accept parameter, fully automatic | Determines CLI and executor integration design | Resolved |
| Scope of accepted deviations | Only spec_update_required: true | Defines scope boundary | Resolved |
| Command name | accept-spec-change | Determines CLI surface | Resolved |
| Process architecture | Same-process (A) + disk-reread safety property (B) | Core design decision | Resolved |
| CLI flag for non-interactive | No CLI flag — auto_accept is an internal code parameter | Keeps CLI surface clean | Resolved |
| Recursion limit | 1 cycle per execute_roadmap() invocation | Safety constraint | Resolved |

## 12. Brainstorm Gap Analysis

This spec was reviewed by `/sc:spec-panel --mode critique --focus requirements,correctness`
with experts Wiegers, Adzic, Nygard, Fowler, and Whittaker across 2 iterations. All 21
findings (7 critical, 8 major, 6 minor) have been resolved.

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| WHITTAKER-IT2-1 | `_apply_resume()` must use post-write disk state | Critical | FR-10 | Whittaker |
| NYGARD-3 | `initial_spec_hash` capture point undefined | Critical | FR-9 | Nygard |
| ADZIC-2 / WHITTAKER-2 | mtime comparison operator and type mismatch | Critical | FR-9 | Adzic, Whittaker |
| WIEGERS-2 / ADZIC-1 | Deviation file frontmatter schema undefined | Critical | FR-4 | Wiegers, Adzic |
| WHITTAKER-4 | Atomic write failure path in FR-10 Step 3 | Critical | FR-10 | Whittaker |

Full findings: `spec-panel-tasklist.md` in this directory.

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| deviation record | A `dev-*-accepted-deviation.md` file containing YAML frontmatter with disposition and spec_update_required fields |
| spec_hash | SHA-256 hex digest of the spec file, stored in `.roadmap-state.json` to detect changes between runs |
| force_extract | Boolean flag in `_apply_resume()` that triggers full pipeline re-run when spec hash changes |
| spec-fidelity | Pipeline step 8/9 that validates the final roadmap against the original spec |
| auto_accept | Boolean parameter on `execute_roadmap()` that controls whether the spec-patch cycle prompts the user |
| initial_spec_hash | Local variable in `execute_roadmap()` capturing the spec hash at function entry, used for FR-9 Condition 3 |

## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `design-accept-spec-change.md` | Full architecture design with function signatures, data flow diagrams, and test architecture |
| `spec-panel-tasklist.md` | All 21 expert panel findings with resolution status |
| `src/superclaude/cli/roadmap/executor.py` | Existing codebase — `execute_roadmap()`, `_apply_resume()`, `_save_state()`, `read_state()` |
