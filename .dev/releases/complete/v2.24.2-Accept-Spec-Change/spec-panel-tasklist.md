# Spec-Panel Review: Improvement Tasklist
# Source: /sc:spec-panel critique on brainstorm-accept-spec-change.md
# Experts: Wiegers, Adzic, Nygard, Fowler, Whittaker (2 iterations)
# Date: 2026-03-13

## Legend
- Priority: CRITICAL (blocks impl) | MAJOR (before code review) | MINOR (before acceptance testing)
- Target: The spec document that needs updating
- Source: Finding ID from panel review

---

## CRITICAL — Must fix before implementation begins

### TASK-01: Define `dev-*-accepted-deviation.md` frontmatter schema
**Priority**: CRITICAL
**Source**: WIEGERS-2, ADZIC-1, WHITTAKER-1 (partial), WHITTAKER-3
**Target**: `brainstorm-accept-spec-change.md` — FR-4
**Work**:
- Embed a canonical example frontmatter block inline in FR-4, e.g.:
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
- Specify `spec_update_required` is a YAML **boolean** (`true`/`false`), NOT a string (`"true"`).
- Specify `disposition` comparison is case-insensitive string match.
- Add: if frontmatter is absent or unparseable on a file, emit a warning and skip the file (do not abort, do not silently count as matching).
- Add: if a required field (`disposition`, `spec_update_required`) is absent, treat as its negative default (`disposition` = not ACCEPTED, `spec_update_required` = false).
- Reference or link to the canonical deviation record spec if one exists elsewhere.

---

### TASK-02: Clarify FR-10 state sequencing — `_apply_resume()` must use post-write disk state
**Priority**: CRITICAL
**Source**: WHITTAKER-IT2-1
**Target**: `brainstorm-accept-spec-change.md` — FR-10
**Work**:
- Add an explicit numbered sequence to FR-10 making clear that `_apply_resume()` is called with state re-read from disk AFTER the atomic write in Step C:
  1. Re-read `.roadmap-state.json` from disk → `fresh_state`
  2. Recompute `new_hash = sha256(config.spec_file)`
  3. Write `new_hash` into `fresh_state["spec_hash"]`, write atomically to disk
  4. Re-read `.roadmap-state.json` from disk again → `post_write_state` (this is what `_apply_resume()` uses)
  5. Rebuild steps list via `_build_steps(config)`
  6. Call `_apply_resume(post_write_state, steps)` — NOT with `fresh_state` from Step 1
- Add the explicit note: "Do NOT pass the in-memory state object from Step 1 to `_apply_resume()`. Always re-read from disk after the atomic write to guarantee `_apply_resume()` sees the updated `spec_hash`."

---

### TASK-03: Define `initial_spec_hash` capture point in `execute_roadmap()`
**Priority**: CRITICAL
**Source**: NYGARD-3
**Target**: `brainstorm-accept-spec-change.md` — FR-9 Condition 3
**Work**:
- Add to `execute_roadmap()` description: "At the top of `execute_roadmap()`, before calling `execute_pipeline()`, capture `initial_spec_hash = sha256(config.spec_file.read_bytes())` as a local variable."
- Amend FR-9 Condition 3 to reference `initial_spec_hash` explicitly: "Has `sha256(config.spec_file.read_bytes())` changed since run started? Compare current hash to `initial_spec_hash` captured at function entry. If equal, condition is false. `state['spec_hash']` is NOT used for this comparison."

---

### TASK-04: Specify mtime comparison operator and tie-case behavior in FR-9 Condition 2
**Priority**: CRITICAL
**Source**: ADZIC-2, WHITTAKER-2
**Amended by**: sc:reflect validation (TASK-04 type mismatch correction)
**Target**: `brainstorm-accept-spec-change.md` — FR-9
**Work**:
- Replace the prose description of Condition 2 with an explicit comparison:
  "A file qualifies if `os.path.getmtime(file) > datetime.fromisoformat(state['steps']['spec-fidelity']['started_at']).timestamp()`."
- Specify the operator is strict `>` (greater-than), not `>=`.
- Add a tie-case note: "On filesystems with 1-second mtime resolution (e.g., HFS+, some network mounts), files written in the same second as `started_at` will NOT satisfy Condition 2. This is a known limitation. Implementations may optionally use `>=` with a documented rationale, but the default is `>`."
- Specify `started_at` type: "`started_at` is stored in `.roadmap-state.json` as an ISO 8601 string
  (e.g., `"2026-03-13T10:00:00.123456+00:00"`) written by `datetime.now(timezone.utc).isoformat()`.
  `os.path.getmtime()` returns a Unix timestamp float. These types are NOT directly comparable.
  Convert with `datetime.fromisoformat(started_at).timestamp()` before the comparison.
  Do NOT compare the raw string to the float — this will always evaluate False in Python."

---

### TASK-05: Specify FR-10 Step C (atomic write) failure path
**Priority**: CRITICAL
**Source**: WHITTAKER-4
**Target**: `brainstorm-accept-spec-change.md` — FR-10
**Work**:
- Add a failure-path clause to FR-10: "If the atomic write in Step C fails (e.g., disk full, permission error), abort the auto-resume cycle and surface the failure as a pipeline error: `[roadmap] ERROR: Failed to update spec_hash during auto-resume cycle: <error>. Falling through to normal failure.`"
- Specify that on Step C failure, `_apply_resume()` is NOT called — the pipeline falls through to `_format_halt_output` / `sys.exit(1)`.
- Document that the state file is guaranteed unmodified if Step C fails (atomic write semantics).

---

## MAJOR — Fix before code review / PR

### TASK-06: Add complete state trace for FR-9 + FR-10 interaction
**Priority**: MAJOR
**Source**: ADZIC-IT2-2
**Target**: `brainstorm-accept-spec-change.md` — new subsection after FR-10
**Work**:
- Add a "State Trace: Auto-Resume Cycle" subsection showing before/after state for the happy path:
  ```
  Before auto-resume cycle (after first spec-fidelity FAIL):
    state["steps"]["spec-fidelity"]["status"] = "FAIL"
    state["spec_hash"] = "<old_hash>"  (stale — does not match current spec file)
    _spec_patch_cycle_count = 0

  After FR-10 Step C (atomic write):
    state["spec_hash"] = "<new_hash>"  (on disk)
    All other keys unchanged

  After FR-10 Step D + E (_apply_resume() called with post-write disk state):
    _apply_resume() sees:
      state["spec_hash"] == sha256(spec_file) → hashes match → no force_extract
      state["steps"]["spec-fidelity"]["status"] = "FAIL" → will be re-run
      All upstream steps (extract, generate, diff, debate, score, merge, test-strategy) = PASS → skipped
    Result: pipeline resumes from spec-fidelity
  ```

---

### TASK-07: Define non-interactive detection mechanism for FR-5 and FR-8
**Priority**: MAJOR
**Source**: WIEGERS-3
**Target**: `brainstorm-accept-spec-change.md` — FR-5
**Work**:
- Add to FR-5: "Non-interactive mode is detected by `not sys.stdin.isatty()`. If non-interactive and `auto_accept=False`, treat user input as N and exit 0 with 'Aborted.' The state file is not touched."
- Cross-reference with FR-8: "When `auto_accept=False` (default) and non-interactive, `_apply_resume_after_spec_patch()` does NOT prompt and does NOT proceed with the cycle. It falls through to normal failure handling."

---

### TASK-08: Add log message for suppressed auto-resume cycle (FR-12 extension)
**Priority**: MAJOR
**Source**: NYGARD-IT2-1
**Target**: `brainstorm-accept-spec-change.md` — FR-12
**Work**:
- Add a third log message to FR-12 for the guard-suppressed case: "If FR-11 guard fires (count >= 1) and the cycle is suppressed, print: `[roadmap] Spec-patch cycle already exhausted (cycle_count=1). Proceeding to normal failure.`"
- Position this message immediately before falling through to `_format_halt_output`.

---

### TASK-09: Specify module dependency direction for `spec_patch.py`
**Priority**: MAJOR
**Source**: FOWLER-1, FOWLER-IT2-1
**Target**: `brainstorm-accept-spec-change.md` — "Files to create/modify" section
**Work**:
- Add a dependency diagram or prose rule to the module table:
  ```
  Dependency direction (strict — no cycles):
    commands.py  →  spec_patch.py  (accept-spec-change command body)
    executor.py  →  spec_patch.py  (calls update_spec_hash, scan_accepted_deviation_records)
    spec_patch.py → (no imports from executor.py or commands.py)
  ```
- Explicitly state: "`_apply_resume_after_spec_patch()` lives in `executor.py` and orchestrates the full cycle. It calls into `spec_patch.py` for hash and scanning logic, not the reverse."
- Mark all new functions in `executor.py` as private (leading underscore): `_apply_resume_after_spec_patch()`, confirm naming convention.

---

### TASK-10: Clarify `_apply_resume()` prompt parameter threading (FR-2, FR-10 interaction)
**Priority**: MAJOR
**Source**: FOWLER-2
**Target**: `brainstorm-accept-spec-change.md` — FR-8 / FR-10
**Work**:
- Add a note to FR-8 or FR-10: "`auto_accept` is passed through the call chain: `execute_roadmap(auto_accept) → _apply_resume_after_spec_patch(auto_accept) → prompt_accept_spec_change(auto_accept)`. No other mechanism controls interactivity. The `auto_accept` parameter is the single source of truth for whether the prompt is displayed."

---

### TASK-11: Specify parse-error warning behavior in FR-4 (YAML parse failure)
**Priority**: MAJOR
**Source**: Fowler Pipeline Dimensional Analysis (Quantity Flow Diagram finding)
**Target**: `brainstorm-accept-spec-change.md` — FR-4
**Work**:
- Add: "If YAML frontmatter parsing raises an exception on any `dev-*-accepted-deviation.md` file, emit a warning to stderr: `[roadmap] WARNING: Could not parse frontmatter in <filename>. Skipping.` and continue processing remaining files."
- Specify: "A parse warning does not change the exit code. The command proceeds with successfully parsed records only."
- Add: "If all files fail to parse, the effective matching count is zero, and FR-4's 'zero records found' path applies."

---

### TASK-12: Specify FR-7 output hash truncation format for old hash
**Priority**: MINOR (but blocks consistent implementation)
**Source**: WIEGERS-4
**Target**: `brainstorm-accept-spec-change.md` — FR-7
**Work**:
- Normalize FR-7 output to use `<hash[:12]>...` for BOTH old and new hash:
  ```
  [roadmap] spec_hash updated.
    Old: <old_hash[:12]>...
    New: <new_hash[:12]>...
    Accepted deviations: DEV-001, DEV-NNN
  Run `superclaude roadmap run <spec_file> --resume` to continue from the failing step.
  ```
- Remove the inconsistency where the example shows `3d1a6d158...` (appears to be full 9-char display) but the template says `[:12]` only for the new hash.

---

### TASK-13: Clarify FR-3 hash equality edge cases
**Priority**: MAJOR
**Source**: WIEGERS-1, Guard Condition Boundary Table (GAP — empty hash, sentinel)
**Target**: `brainstorm-accept-spec-change.md` — FR-3
**Work**:
- Add a clarifying note: "Hash equality (FR-3) covers two legitimate cases: (a) `accept-spec-change` was previously run successfully for this change — correct idempotent behavior; (b) the spec file was reverted to match the stored hash — the command cannot distinguish this case and treats it as 'nothing to do'."
- Add: "If `state['spec_hash']` is absent, null, or empty, treat as a mismatch and proceed to FR-4."
- Add: "Hash comparison uses byte-exact string equality on the hex digest. No normalization (e.g., case folding) is applied."

---

### TASK-14: Add concurrency constraint documentation
**Priority**: MAJOR
**Source**: NYGARD-1
**Target**: `brainstorm-accept-spec-change.md` — Non-functional requirements or new "Constraints" section
**Work**:
- Add NFR-5: "Concurrency: `accept-spec-change` assumes exclusive write access to `.roadmap-state.json` during execution. Running `accept-spec-change` concurrently with `roadmap run` or another `accept-spec-change` invocation is not supported. No file locking is implemented; the operator is responsible for preventing concurrent access."
- Similarly add to `execute_roadmap()` FR-10: "The auto-resume cycle assumes no concurrent writer modifies `.roadmap-state.json` between the reread and the atomic write in FR-10 Step C."

---

## MINOR — Fix before acceptance testing

### TASK-15: Specify interactive prompt input normalization
**Priority**: MINOR
**Source**: ADZIC-3
**Target**: `brainstorm-accept-spec-change.md` — FR-5
**Work**:
- Add to FR-5: "Only `y` or `Y` (case-insensitive single character) confirms. Any other input — including `yes`, `YES`, empty string (Enter only), or any other string — is treated as N (abort)."

---

### TASK-16: Add Windows atomicity caveat to NFR-1
**Priority**: MINOR
**Source**: NYGARD-4
**Target**: `brainstorm-accept-spec-change.md` — NFR-1
**Work**:
- Amend NFR-1: "`os.replace()` provides atomic rename on POSIX (Linux, macOS) when source and destination are on the same filesystem. On Windows, `os.replace()` is atomic only on the same volume; behavior on cross-volume writes is undefined. The primary deployment target is POSIX. Windows support is best-effort."

---

### TASK-17: Emphasize per-invocation scope of `_spec_patch_cycle_count`
**Priority**: MINOR
**Source**: WHITTAKER-5
**Target**: `brainstorm-accept-spec-change.md` — FR-11
**Work**:
- Add emphasis: "`_spec_patch_cycle_count` MUST be a **local variable** declared inside `execute_roadmap()`. It MUST NOT be a module-level, class-level, or global variable. Each call to `execute_roadmap()` gets its own independent counter initialized to 0."
- Add: "Two successive calls to `execute_roadmap()` in the same process each get their own cycle counter. The guard is per-invocation, not per-process."

---

### TASK-18: Add AC-11 for non-interactive `auto_accept=False` path
**Priority**: MINOR
**Source**: WIEGERS-IT2-2
**Target**: `brainstorm-accept-spec-change.md` — Acceptance Criteria
**Work**:
- Add: "AC-11: When `auto_accept=False` and stdin is not a tty (non-interactive environment such as CI), `accept-spec-change` exits 0 with 'Aborted.' and does not modify `.roadmap-state.json`."

---

### TASK-19: Split AC-5 into unit and integration criteria
**Priority**: MINOR
**Source**: WIEGERS-IT2-1
**Target**: `brainstorm-accept-spec-change.md` — Acceptance Criteria
**Work**:
- Replace AC-5 with:
  - AC-5a: "`accept-spec-change` updates `spec_hash` to the value that `_apply_resume()` will compare against `sha256(spec_file)`, allowing it to skip upstream steps."
  - AC-5b (integration test): "After `accept-spec-change` runs, executing `roadmap run <spec_file> --resume` proceeds from spec-fidelity without re-running extract, generate, diff, debate, score, merge, or test-strategy steps."

---

### TASK-20: Add FR-13 output clarification (post-resume vs first-run diagnostics)
**Priority**: MINOR
**Source**: NYGARD-IT2-2
**Target**: `brainstorm-accept-spec-change.md` — FR-13
**Work**:
- Add: "`_format_halt_output` is called with the pipeline results from the post-resume execution (the second spec-fidelity run). The spec-fidelity FAIL results from the first run are not included in the final output. Operators inspecting the halt output will see only the post-resume failure diagnostics."

---

### TASK-21: Add executable test scenarios for AC-1 through AC-10
**Priority**: MINOR (but important for test spec quality)
**Source**: ADZIC-IT2-1
**Target**: `tests/roadmap/test_accept_spec_change.py` and `tests/roadmap/test_spec_patch_cycle.py`
**Work**:
- For each AC-1 through AC-11, add a 3-line scenario comment in the test file headers:
  ```python
  # AC-1: No accepted deviation records → exit 1
  # Given: output_dir with .roadmap-state.json (spec hash stale), zero dev-* files
  # When: accept-spec-change output_dir
  # Then: exit code 1, stderr contains "no accepted deviation records"
  ```
- Cover degenerate inputs for each AC: empty dir, malformed JSON state, missing spec_file.

---

## Intra-Group Dependencies

These dependencies exist within the MAJOR priority tier. If `sc:task-unified` executes
tasks in parallel, edits land in different spec sections so there is no write conflict.
If executing sequentially, respect this order:

| Execute First | Then Execute | Reason |
|---|---|---|
| TASK-02 (FR-10 corrected 6-step sequence) | TASK-06 (state trace) | The state trace must reference the corrected step numbering from TASK-02; writing the trace before the sequence is fixed produces a dangling reference |
| TASK-10 (auto_accept call chain in FR-8/FR-10) | TASK-07 (non-interactive detection in FR-5) | TASK-07 adds a cross-reference to FR-8 behavior; that cross-reference is only accurate after TASK-10 has defined the call chain |
| TASK-07 (non-interactive detection mechanism) | TASK-18 (AC-11 for non-interactive path) | AC-11 cites the `sys.stdin.isatty()` mechanism; the AC text should be written after the mechanism is specified in FR-5 |

**For parallel execution**: all three dependency pairs target different sections of the spec
(FR-10, FR-5, FR-8, Acceptance Criteria) — no section is written by more than one task.
Parallel execution is safe; the dependencies only matter for review coherence, not for
file-level conflicts.

---

## Summary Table

| Task | Priority | Source Finding(s) | Target Section |
|------|----------|-------------------|----------------|
| TASK-01 | CRITICAL | WIEGERS-2, ADZIC-1, WHITTAKER-1/3 | FR-4 |
| TASK-02 | CRITICAL | WHITTAKER-IT2-1 | FR-10 |
| TASK-03 | CRITICAL | NYGARD-3 | FR-9 Cond.3 |
| TASK-04 | CRITICAL | ADZIC-2, WHITTAKER-2 | FR-9 Cond.2 |
| TASK-05 | CRITICAL | WHITTAKER-4 | FR-10 Step C |
| TASK-06 | MAJOR | ADZIC-IT2-2 | New subsection after FR-10 |
| TASK-07 | MAJOR | WIEGERS-3 | FR-5 |
| TASK-08 | MAJOR | NYGARD-IT2-1 | FR-12 |
| TASK-09 | MAJOR | FOWLER-1, FOWLER-IT2-1 | Files table |
| TASK-10 | MAJOR | FOWLER-2 | FR-8 / FR-10 |
| TASK-11 | MAJOR | Pipeline Dimensional Analysis | FR-4 |
| TASK-12 | MINOR | WIEGERS-4 | FR-7 |
| TASK-13 | MAJOR | WIEGERS-1, Boundary Table GAPs | FR-3 |
| TASK-14 | MAJOR | NYGARD-1 | NFR / new Constraints |
| TASK-15 | MINOR | ADZIC-3 | FR-5 |
| TASK-16 | MINOR | NYGARD-4 | NFR-1 |
| TASK-17 | MINOR | WHITTAKER-5 | FR-11 |
| TASK-18 | MINOR | WIEGERS-IT2-2 | Acceptance Criteria |
| TASK-19 | MINOR | WIEGERS-IT2-1 | AC-5 |
| TASK-20 | MINOR | NYGARD-IT2-2 | FR-13 |
| TASK-21 | MINOR | ADZIC-IT2-1 | test files |

**Total**: 5 CRITICAL, 10 MAJOR, 6 MINOR = 21 tasks
