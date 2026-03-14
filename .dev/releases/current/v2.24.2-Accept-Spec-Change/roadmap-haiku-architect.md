---
spec_source: "release-spec-accept-spec-change.md"
complexity_score: 0.65
primary_persona: architect
---

## 1. Executive summary

This roadmap delivers a controlled enhancement to the roadmap execution system so accepted specification changes can be acknowledged safely and resumed without rerunning the full pipeline. Architecturally, the work is moderate in complexity because it combines CLI behavior, state mutation, hash-based change detection, in-process control flow, and failure-path correctness across multiple modules.

### Architectural priorities
1. **State integrity first**
   - All `.roadmap-state.json` mutations must be atomic.
   - Abort paths must remain strictly read-only.
   - Resume behavior must consume disk state after mutation, not stale in-memory state.

2. **Constrained integration surface**
   - Keep `spec_patch.py` isolated as a leaf module.
   - Preserve `_apply_resume()` unchanged.
   - Limit public API change to a backward-compatible `execute_roadmap(auto_accept: bool = False)` addition.

3. **Deterministic control flow**
   - Detect spec-patch retry conditions precisely.
   - Allow at most one automatic patch/resume cycle per invocation.
   - Fall through to the existing halt path after exhaustion.

4. **Operator safety and recoverability**
   - Require accepted deviation evidence before state mutation.
   - Preserve existing state keys verbatim except `spec_hash`.
   - Make repeated execution idempotent.

### Scope summary
- **Functional requirements**: 13
- **Non-functional requirements**: 8
- **Technical domains**: 4
- **Risks to mitigate**: 5
- **Dependencies to plan around**: 4
- **Success criteria to validate**: 15

### Expected outcome
At completion, operators will be able to:
1. Run an `accept-spec-change` flow that safely updates only the stored spec hash after validated evidence.
2. Resume roadmap execution without recomputing earlier phases unnecessarily.
3. Benefit from a single automatic in-process retry after spec-fidelity failure when accepted deviations and spec edits justify it.

---

## 2. Phased implementation plan with milestones

## Phase 0. Architecture confirmation and requirement traceability

### Objective
Translate extraction requirements into an implementation contract and reduce ambiguity before code changes.

### Key actions
1. Build a requirement-to-module map:
   - `spec_patch.py`
   - `executor.py`
   - `commands.py`
   - tests for CLI, state mutation, and retry flow

2. Confirm architectural invariants:
   - `spec_patch.py` remains leaf-only
   - no `_apply_resume()` modification
   - only `execute_roadmap()` public signature changes
   - no subprocess pipeline execution in spec patch logic

3. Resolve or explicitly document open questions:
   - source of deviation `severity`
   - handling of missing `started_at`
   - intended lifecycle of accepted deviation files
   - batching semantics for multiple deviation records

### Milestone
- Approved implementation design with requirement mapping for FR-001 to FR-013 and NFR-001 to NFR-008.

### Deliverables
- Short design note
- requirement trace matrix
- test matrix draft

### Timeline estimate
- **0.5 day**

---

## Phase 1. Spec patch module foundation

### Objective
Implement the isolated spec-change acceptance mechanics in a leaf module with safe state handling.

### Key actions
1. Implement state-file discovery and validation
   - Read `.roadmap-state.json` from `output_dir`
   - Produce exact error behavior for missing/unreadable state
   - Load `spec_file` from state and recompute SHA-256 from file bytes

2. Implement hash-comparison logic
   - Compare current hash to `state["spec_hash"]` using byte-exact hex equality
   - Treat missing/null/empty `spec_hash` as mismatch
   - Return clean idempotent success when already current

3. Implement accepted deviation evidence scanning
   - Glob `dev-*-accepted-deviation.md`
   - Parse YAML frontmatter
   - Select only:
     - `disposition: ACCEPTED` case-insensitive
     - `spec_update_required: true` as YAML boolean
   - Warn-and-skip malformed files

4. Implement prompt and non-interactive behavior
   - Summarize accepted deviation records
   - Accept only single-character `y` or `Y`
   - In non-interactive mode with `auto_accept=False`, exit safely with `Aborted.` and no state mutation

5. Implement atomic state update
   - Write `.roadmap-state.json.tmp`
   - overwrite tmp if present
   - `os.replace()` into final path
   - modify only `spec_hash`

6. Implement confirmation output
   - old/new truncated hashes
   - accepted deviation IDs
   - instruction to run `roadmap run --resume`

### Architectural focus
- Keep parsing, prompting, hashing, and writing responsibilities cohesive but internal.
- Avoid importing execution-layer code into the patch module.
- Ensure all error messages are stable and testable.

### Milestone
- `accept-spec-change` core logic implemented and isolated.

### Deliverables
- `spec_patch.py`
- unit tests for hash, parsing, prompting, and atomic write behavior

### Timeline estimate
- **1.5 days**

---

## Phase 2. CLI command integration

### Objective
Expose the feature through the existing Click command system without widening public API unnecessarily.

### Key actions
1. Add a new CLI command:
   - `accept-spec-change`
   - `output_dir` via `click.Path(exists=True)`
   - zero optional flags

2. Wire command to leaf-module functionality
   - no executor imports into `spec_patch.py`
   - CLI layer may depend on patch module, not vice versa

3. Preserve current CLI behavior and compatibility
   - no changes to existing commands beyond registration
   - consistent exit code behavior

### Architectural focus
- Maintain clear dependency direction: `commands.py -> spec_patch.py`
- Keep CLI wrapper thin and behavior-driven.

### Milestone
- User-invokable `accept-spec-change` command available and stable.

### Deliverables
- CLI registration and command handler
- CLI behavior tests

### Timeline estimate
- **0.5 day**

---

## Phase 3. Executor integration and auto-accept threading

### Objective
Introduce controlled in-process spec-patch support into roadmap execution while preserving backward compatibility.

### Key actions
1. Extend `execute_roadmap()` signature
   - add `auto_accept: bool = False`
   - preserve all existing callers

2. Thread parameter through call chain
   - `execute_roadmap()`
   - `_apply_resume_after_spec_patch()`
   - prompt/accept helper

3. Capture entry-time `initial_spec_hash`
   - use local variable at `execute_roadmap()` entry
   - do not rely on mutable state-file hash for FR-009 condition 3

4. Add helper functions with private naming
   - detection of qualifying deviation files
   - retry orchestration
   - disk reread and state refresh logic

### Architectural focus
- Minimize executor changes to orchestration-only code.
- Preserve existing behavior when the new path is not triggered.
- Keep new helpers private per NFR-008.

### Milestone
- Executor accepts the new feature without breaking existing workflows.

### Deliverables
- updated executor flow
- compatibility tests
- signature regression tests

### Timeline estimate
- **1 day**

---

## Phase 4. Post-spec-fidelity failure retry cycle

### Objective
Implement the single automatic patch/resume cycle with precise gating and safe disk boundaries.

### Key actions
1. Implement three-condition detection after spec-fidelity fail
   - recursion guard not yet fired
   - qualifying deviation files with mtime strictly greater than spec-fidelity `started_at`
   - current spec hash differs from `initial_spec_hash`

2. Implement local recursion guard
   - `_spec_patch_cycle_count = 0` within `execute_roadmap()`
   - increment before entering retry
   - block any second cycle in same invocation

3. Implement mandated six-step disk-reread sequence
   1. reread state from disk
   2. recompute spec hash
   3. atomically write new hash
   4. reread state from disk again
   5. rebuild steps with `_build_steps(config)`
   6. call `_apply_resume(post_write_state, steps)`

4. Implement failure-path behavior
   - on atomic write failure, log error to stderr and fall through to normal halt path
   - if second run still fails spec-fidelity, use second-run results for halt output
   - no second retry

5. Implement lifecycle logging
   - entry: deviation count and `cycle 1/1`
   - completion message
   - suppression message when guard blocks retry
   - all prefixed with `[roadmap]`

### Architectural focus
- This is the highest-risk phase because it touches the execution state machine.
- The critical design principle is **fresh-state resumption**: mutate disk, reread disk, then resume.
- Avoid implicit coupling between first-run and second-run in-memory objects.

### Milestone
- Single safe auto-resume cycle operational with normal failure fallback.

### Deliverables
- executor retry path
- integration tests covering first-fail/second-pass and first-fail/second-fail

### Timeline estimate
- **1.5 days**

---

## Phase 5. Validation, hardening, and release readiness

### Objective
Prove compliance with success criteria and guard against regression in state integrity and control flow.

### Key actions
1. Validate all acceptance criteria
   - AC-1 through AC-14 mapped to tests
   - explicit coverage for idempotency, no-touch aborts, and recursion guard

2. Run focused regression testing
   - roadmap resume behavior
   - CLI command wiring
   - state preservation across updates

3. Review dependency and packaging impacts
   - confirm `PyYAML >= 6.0`
   - verify no circular imports
   - confirm zero `ClaudeProcess` usage

4. Document operational constraints
   - exclusive access assumption
   - best-effort Windows semantics
   - mtime-resolution caveat
   - non-interactive behavior

### Milestone
- Feature verified against functional, non-functional, and architectural requirements.

### Deliverables
- passing test suite
- release note/update note
- operator guidance for accepted-spec workflow

### Timeline estimate
- **1 day**

---

## 3. Risk assessment and mitigation strategies

## Risk 1. State corruption during write
**Severity**: High  
**Relevant requirements**: FR-006, FR-010, NFR-001

### Risk
A partial or interrupted write could corrupt `.roadmap-state.json`, breaking resume behavior.

### Mitigation
1. Enforce temp-file plus `os.replace()` for every state mutation.
2. Never write directly to the final state path.
3. Add tests validating:
   - only `spec_hash` changes
   - tmp overwrite is safe
   - abort paths leave file untouched

### Residual concern
- Atomicity guarantee is strongest on POSIX same-filesystem replacements; Windows remains best-effort.

---

## Risk 2. Stale in-memory state at resume boundary
**Severity**: High  
**Relevant requirements**: FR-010, AC-7

### Risk
The retry cycle could resume using stale state rather than the disk-mutated state, causing inconsistent behavior.

### Mitigation
1. Enforce the six-step reread/write/reread sequence exactly.
2. Use the second disk read as the object passed into `_apply_resume()`.
3. Add integration tests that assert post-write disk state is the resumed state.

### Residual concern
- Any future refactor of executor resume flow must preserve this explicit boundary.

---

## Risk 3. Infinite or repeated retry loop
**Severity**: High  
**Relevant requirements**: FR-011, FR-013, AC-6, AC-8

### Risk
Spec-fidelity failure could repeatedly trigger patch cycles.

### Mitigation
1. Keep `_spec_patch_cycle_count` local to `execute_roadmap()`.
2. Allow at most one retry per invocation.
3. Log suppression when the guard blocks a second attempt.
4. Ensure second failure falls through to normal halt formatting and exit.

### Residual concern
- Future retries for other failure classes must not reuse this mechanism without separate guards.

---

## Risk 4. Invalid deviation evidence causing crashes or false positives
**Severity**: Medium  
**Relevant requirements**: FR-004, AC-14

### Risk
Malformed YAML or loosely typed frontmatter could either crash processing or incorrectly qualify evidence.

### Mitigation
1. Parse frontmatter defensively.
2. Warn to stderr and skip malformed files.
3. Require:
   - `disposition: ACCEPTED` case-insensitive
   - `spec_update_required: true` as boolean
4. Add tests for string `"true"` rejection and YAML parsing failures.

### Residual concern
- YAML 1.1 coercion semantics should be documented and accepted intentionally.

---

## Risk 5. Unsafe non-interactive behavior
**Severity**: Medium  
**Relevant requirements**: FR-005, FR-008, NFR-002, AC-11

### Risk
CI or piped execution could modify state without an explicit human confirmation.

### Mitigation
1. Detect `not sys.stdin.isatty()`.
2. When `auto_accept=False`, exit 0 with `Aborted.` and do not touch state.
3. Keep `auto_accept` internal/non-CLI exposed.
4. Verify unchanged state-file mtime in tests.

### Residual concern
- Internal callers must use `auto_accept=True` deliberately and sparingly.

---

## Risk 6. TOCTOU on concurrent state access
**Severity**: Medium  
**Relevant requirements**: NFR-005

### Risk
Another process may mutate `.roadmap-state.json` between read and replace.

### Mitigation
1. Document single-writer operational assumption clearly.
2. Avoid introducing partial mitigation that implies full concurrency safety.
3. Consider future locking only as a separate feature, not in this release.

### Residual concern
- Concurrent roadmap operations remain unsupported.

---

## Risk 7. Ambiguity in timestamp gating
**Severity**: Low to Medium  
**Relevant requirements**: FR-009

### Risk
Filesystem mtime resolution or missing `started_at` may cause legitimate deviation files to be ignored or logic to behave inconsistently.

### Mitigation
1. Standardize ISO timestamp parsing and comparison.
2. Add explicit handling for missing `started_at`:
   - recommended behavior: treat as retry condition not met and proceed to normal failure path
3. Document mtime-resolution limitations.

### Residual concern
- Same-second writes on low-resolution filesystems may remain edge-sensitive.

---

## 4. Resource requirements and dependencies

## Engineering resources

### Core roles
1. **Architect / lead implementer**
   - Owns control-flow design, invariants, and acceptance mapping.
2. **Backend engineer**
   - Implements CLI wiring, executor updates, and state mutation logic.
3. **QA / test engineer**
   - Builds acceptance and regression coverage, especially for file-state semantics.

### Estimated effort
- Total engineering effort: **4.5 to 5.0 days**
- QA and validation effort is material because correctness depends on failure paths and state integrity, not just nominal flow.

---

## Technical dependencies

1. **PyYAML >= 6.0**
   - Needed for frontmatter parsing in `spec_patch.py`
   - Must be confirmed acceptable as a direct dependency

2. **Click >= 8.0.0**
   - Existing dependency
   - Used for CLI command registration and path validation

3. **hashlib**
   - Standard library
   - Used for SHA-256 spec hash computation

4. **Executor internals**
   - Existing internal functions consumed:
     - `execute_roadmap()`
     - `_apply_resume()`
     - `_build_steps()`
     - `_format_halt_output()`
     - `_save_state()`
     - `read_state()`

---

## Implementation dependencies by phase

1. **Phase 1 depends on**
   - state-file schema understanding
   - decision on YAML parsing and frontmatter extraction approach

2. **Phase 2 depends on**
   - stable leaf-module interfaces from Phase 1

3. **Phase 3 depends on**
   - confirmed backward-compatible executor signature
   - clarified internal call chain

4. **Phase 4 depends on**
   - reliable access to spec-fidelity step metadata, especially `started_at`

5. **Phase 5 depends on**
   - full testability of file timestamps, TTY behavior, and exit codes

---

## Operational constraints

1. No concurrent write protection
2. POSIX is primary atomic-write target
3. No subprocess pipeline execution in patch module
4. No new public executor symbols
5. `_apply_resume()` remains unchanged

---

## 5. Success criteria and validation approach

## Validation strategy

The validation approach should be organized into five layers:

### Layer 1. Unit validation
Validate isolated behaviors:
1. state-file discovery errors
2. hash recomputation
3. equality and mismatch behavior
4. YAML frontmatter parsing
5. evidence filtering rules
6. prompt confirmation parsing
7. atomic temp-write/replace logic

### Layer 2. CLI validation
Validate command behavior:
1. missing state file -> exit 1 with exact message
2. missing spec file -> exit 1 with exact message
3. zero qualifying deviation records -> exit 1
4. non-interactive + `auto_accept=False` -> exit 0 `Aborted.`
5. successful acceptance -> exit 0 with old/new hashes and resume instruction

### Layer 3. State integrity validation
Validate persistence guarantees:
1. only `spec_hash` changes
2. all other state keys preserved verbatim
3. abort path leaves file mtime unchanged
4. second identical run exits cleanly with nothing-to-do behavior

### Layer 4. Executor integration validation
Validate auto-resume orchestration:
1. `auto_accept` defaults to `False`
2. callers can omit `auto_accept`
3. retry gate requires all three FR-009 conditions
4. disk state is reread and used for `_apply_resume()`
5. recursion guard blocks second retry

### Layer 5. Failure-path validation
Validate architectural safety under failure:
1. atomic write failure aborts cycle and falls through normally
2. persistent spec-fidelity failure after retry exits through standard halt path
3. second-run results feed halt formatting
4. log lifecycle messages appear with `[roadmap]` prefix

---

## Success criteria mapping

1. **State safety**
   - AC-2, AC-4, AC-13
   - Verified by file-content comparison and mtime assertions

2. **Behavioral correctness**
   - AC-1, AC-3, AC-9, AC-10, AC-11, AC-14
   - Verified by unit and CLI tests

3. **Resume correctness**
   - AC-5a, AC-5b, AC-6, AC-7, AC-8
   - Verified by integration tests with staged failure/resume scenarios

4. **Observability**
   - AC-12
   - Verified by captured logs/stderr output

---

## Acceptance gate for release

The feature should be considered ready only when all of the following are true:

1. All 15 success criteria are mapped to automated tests or explicit documented constraints.
2. No circular dependency is introduced.
3. No new public API is added beyond the defaulted `execute_roadmap()` parameter.
4. No code in the patch module invokes pipeline subprocesses.
5. Resume behavior skips upstream phases after accepted spec change as intended.
6. At least one full end-to-end happy-path and one exhausted-retry path are demonstrated.

---

## 6. Timeline estimates per phase

## Recommended sequence

1. **Phase 0 — Architecture confirmation and traceability**
   - Duration: **0.5 day**

2. **Phase 1 — Spec patch module foundation**
   - Duration: **1.5 days**

3. **Phase 2 — CLI command integration**
   - Duration: **0.5 day**

4. **Phase 3 — Executor integration and auto-accept threading**
   - Duration: **1 day**

5. **Phase 4 — Post-spec-fidelity failure retry cycle**
   - Duration: **1.5 days**

6. **Phase 5 — Validation, hardening, and release readiness**
   - Duration: **1 day**

## Total estimate
- **6.0 days elapsed**
- **4.5 to 5.0 days of focused engineering effort**, depending on how quickly the open questions are resolved and how much existing test scaffolding can be reused

---

## Recommended milestone checkpoints

1. **Checkpoint A**
   - End of Phase 1
   - Decision: leaf-module behavior and state mutation semantics accepted

2. **Checkpoint B**
   - End of Phase 3
   - Decision: public API compatibility and executor integration accepted

3. **Checkpoint C**
   - End of Phase 4
   - Decision: retry-cycle correctness and guard behavior accepted

4. **Checkpoint D**
   - End of Phase 5
   - Decision: release readiness approved based on acceptance evidence

---

## Architect recommendations

1. **Treat disk reread semantics as a non-negotiable invariant**
   - This is the architectural boundary that prevents subtle state drift bugs.

2. **Keep retry logic narrow and explicit**
   - Do not generalize the spec-patch retry into a reusable failure-recovery framework in this release.

3. **Resolve missing `started_at` behavior before implementation completes**
   - This is a control-flow ambiguity with direct impact on retry correctness.

4. **Require a test-first approach for abort and failure paths**
   - The highest-risk defects are not in the happy path; they are in no-touch aborts, retry exhaustion, and stale-state resume boundaries.

5. **Document the single-writer assumption prominently**
   - The absence of locking is acceptable only if operationally explicit.

6. **Avoid expanding CLI scope**
   - Zero optional flags is the correct design choice for this release; additional override controls would increase operator risk and test surface without clear value.
