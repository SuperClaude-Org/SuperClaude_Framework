---
spec_source: v2.25.1-release-spec.md
complexity_score: 0.5
primary_persona: analyzer
---

# Project Roadmap: v2.25.1 Release Fixes

## 1. Executive summary

This roadmap covers a moderate-complexity release with two tightly scoped implementation tracks:

1. **Tool schema discovery fix**
   - Add `--tools default` to `ClaudeProcess.build_command()`.
   - Preserve all existing command assembly behavior.
   - Update and extend pipeline tests.

2. **ARG_MAX / embed-size guard fix**
   - Replace the hardcoded 200 KB embed limit with explicit kernel-derived constants.
   - Measure the full composed prompt payload, not embedded content alone.
   - Add regression coverage for exact-limit and composed-string overflow behavior.

### Analyzer assessment

- **Primary delivery risk** is not coding complexity; it is **incorrect assumptions about CLI behavior**, especially the Phase 0 `--file` gate.
- **Primary sequencing constraint** is that **Phase 0 must complete before code changes are finalized**, and `process.py` must be updated before combined suite runs.
- **Primary validation focus** should be:
  1. proving `--file` behavior empirically,
  2. proving command list invariants did not regress,
  3. proving large-input fallback behavior works at the real composed-string boundary.

### Scope summary

- **18 total requirements**
  - 12 functional
  - 6 non-functional
- **4 technical domains**
  - CLI process construction
  - roadmap executor behavior
  - test coverage
  - release validation
- **8 identified risks**
- **7 dependencies**
- **14 success criteria**

### Recommended delivery posture

- Treat this as a **gated corrective release**, not a refactor.
- Keep changes **surgical, local, and additive**.
- Use **evidence checkpoints** between phases; do not batch all edits before validation.

---

## 2. Phased implementation plan with milestones

## Phase 0 — Blocking empirical validation

### Objective
Determine whether the current `claude --file` fallback path is valid before implementation proceeds.

### Actions
1. Execute the required validation command sequence:
   - `echo "The secret answer is PINEAPPLE." > /tmp/file-test.md`
   - `claude --print -p "What is the secret answer?" --file /tmp/file-test.md`
2. Record outcome as one of:
   - **WORKING**: response includes `PINEAPPLE`
   - **BROKEN**: response does not include `PINEAPPLE`
3. Inspect `claude --help` for `--file` format expectations.
4. Capture the decision in release notes / generated artifact for traceability.

### Deliverables
- A recorded Phase 0 result.
- A go/no-go decision for Phase 1.5 contingency scope.

### Milestone M0
**CLI fallback behavior verified and documented.**

### Exit criteria
- Phase 0 result is recorded before code-change completion.
- Team knows whether Phase 1.5 is activated.

### Analyzer emphasis
This is the highest-risk uncertainty in the release. Do not treat it as optional or informal validation.

---

## Phase 1 — Tool schema discovery fix

### Objective
Ensure all `ClaudeProcess`-based subprocess invocations include `--tools default` without breaking existing flag behavior.

### Actions
1. Inspect `ClaudeProcess.build_command()` and all subclasses for override behavior.
2. Confirm no subclass bypasses `super()` in a way that would drop the new flags.
3. Modify `src/superclaude/cli/pipeline/process.py` so returned command list includes:
   - `--tools`
   - `default`
4. Preserve placement:
   - after `--no-session-persistence`
   - before `--max-turns`
5. Preserve:
   - `--print`
   - `--verbose`
   - `--no-session-persistence`
   - `--max-turns`
   - `--output-format`
   - `-p`
6. Preserve `extra_args` passthrough ordering after `--model`.
7. Preserve conditional `--model` behavior.

### Deliverables
- Updated `ClaudeProcess.build_command()`
- No changes to subclasses unless override verification disproves assumptions

### Milestone M1
**All inherited process-based commands include `--tools default` with no assembly regressions.**

### Exit criteria
- Command structure satisfies FR-001 through FR-004.
- Subclass review confirms architectural constraint holds.

### Analyzer emphasis
This phase is low implementation risk but medium regression risk because list-order assertions are brittle.

---

## Phase 1.5 — Conditional fallback remediation

### Trigger
Activate **only if Phase 0 result is BROKEN**.

### Objective
Replace broken `--file`-based fallback paths with inline embedding or equivalent safe path across affected executors.

### Actions
1. Assess affected files:
   - `src/superclaude/cli/roadmap/remediate_executor.py`
   - `src/superclaude/cli/roadmap/executor.py`
   - `src/superclaude/cli/roadmap/validate_executor.py`
   - `src/superclaude/cli/tasklist/executor.py`
2. Replace broken `--file` fallback behavior with inline embedding logic consistent with release spec.
3. Reassess whether these independent executors also need `--tools default`.
4. Add or update tests for fallback replacement behavior.
5. Validate that large-input workflows still complete without returning to the broken path.

### Deliverables
- Updated non-inheriting executors, if required
- Conditional tests covering inline replacement

### Milestone M1.5
**Fallback path no longer depends on a broken CLI mechanism.**

### Exit criteria
- BROKEN outcome has a forward-path remediation in all relevant executors.
- Conditional success criteria SC-011 are met.

### Analyzer emphasis
If Phase 0 is BROKEN, this phase becomes risk-critical because prior assumptions about large-file handling are invalid.

---

## Phase 2 — Embed guard correction

### Objective
Align executor guard logic with Linux `MAX_ARG_STRLEN` constraints and actual composed prompt size.

### Actions
1. Update `src/superclaude/cli/roadmap/executor.py` constants:
   - `_MAX_ARG_STRLEN = 128 * 1024`
   - `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`
   - `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD`
2. Add inline derivation comments for each constant.
3. Add module-level assertion:
   - `_PROMPT_TEMPLATE_OVERHEAD >= 4096`
   - with required rationale in error message
4. Remove stale comments and avoid adding imports.
5. Update embed guard to evaluate:
   - `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT`
   - where `composed = step.prompt + "\n\n" + embedded`
6. Update warning log text to mention:
   - `composed prompt`
   - actual byte count
7. Add or revise nearby code comment clarifying:
   - `<=` is intentional
   - `120 KB` remains below `128 KB`

### Deliverables
- Corrected constants
- Runtime assertion
- Correct guard behavior
- Updated log messaging

### Milestone M2
**Embed/fallback decision is based on actual composed argument size and auditable OS-limit constants.**

### Exit criteria
- FR-007 through FR-009 satisfied
- No hardcoded 200 KB value remains
- No new imports added

### Analyzer emphasis
This phase addresses the root cause of the `Argument list too long` failure mode. It is the core correctness fix in the release.

---

## Phase 3 — Test suite alignment and regression coverage

### Objective
Bring test coverage in line with new command assembly and embed-guard semantics.

### Actions
1. Update `tests/pipeline/test_process.py`:
   - add `test_tools_default_in_command`
   - update `test_required_flags`
   - update `test_stream_json_matches_sprint_flags`
2. Update roadmap file-passing tests:
   - rename `test_100kb_guard_fallback` to `test_embed_size_guard_fallback`
   - update docstring references
   - import `_EMBED_SIZE_LIMIT`
3. Add `TestComposedStringGuard`:
   - file at 90% of `_EMBED_SIZE_LIMIT`
   - prompt large enough to exceed composed limit
   - assert fallback fired
   - assert file content absent from prompt
   - assert `--file` flags present in `extra_args` if Phase 0 says WORKING
   - if Phase 1.5 activated, adapt expected behavior to inline remediation path
4. Verify exact-limit behavior:
   - composed length equal to `_EMBED_SIZE_LIMIT` should still embed inline
5. Run targeted tests first, then broader grouped suite.

### Deliverables
- Updated unit and integration-level regression coverage
- Tests coupled to constants, not stale size literals

### Milestone M3
**Regression suite encodes the new invariants and catches future drift.**

### Exit criteria
- SC-003, SC-008, SC-009 satisfied
- Conditional tests aligned to Phase 0 outcome

### Analyzer emphasis
Tests are not just validation; they are the durable control that prevents reintroduction of both bugs.

---

## Phase 4 — End-to-end validation and release readiness

### Objective
Confirm release-level behavior across affected flows before finalizing.

### Actions
1. Run targeted suites:
   - `uv run pytest tests/pipeline/test_process.py -v`
   - `uv run pytest tests/sprint/ tests/roadmap/ tests/pipeline/ -v`
2. Run smoke validation:
   - `superclaude sprint run ... --dry-run`
3. Validate large-spec behavior:
   - confirm `spec-fidelity` step does not fail with `OSError: [Errno 7] Argument list too long`
4. Confirm no added dependencies, no unexpected file changes, and no non-specified behavior drift.
5. Record validation outcomes against the 14 success criteria.

### Deliverables
- Test evidence
- Smoke-test evidence
- Release validation checklist

### Milestone M4
**Release candidate validated against functional, non-functional, and operational success criteria.**

### Exit criteria
- All required tests pass
- Dry-run succeeds
- Large-spec scenario succeeds
- Success criteria checklist complete

### Analyzer emphasis
The release should not ship based only on unit coverage; the CLI smoke test and large-input path are required evidence.

---

## 3. Risk assessment and mitigation strategies

## High-priority risks

### 1. Broken `--file` fallback path
- **Risk**: CLI may ignore bare-path `--file`, invalidating existing fallback logic.
- **Severity**: High
- **Mitigation**:
  1. Make Phase 0 mandatory.
  2. Inspect `claude --help` before deciding remediation.
  3. If BROKEN, activate Phase 1.5 immediately.
- **Contingency**:
  - Replace broken fallback path across all affected executors in the same release cycle.

### 2. Large-input guard still underestimates real arg length
- **Risk**: Measuring only embedded content can still overflow `execve()` limits.
- **Severity**: High
- **Mitigation**:
  1. Measure `step.prompt + "\n\n" + embedded`
  2. Add exact-limit and overflow tests
  3. Keep explicit overhead margin and runtime assertion
- **Contingency**:
  - If residual failures appear, tighten overhead constant and re-run boundary tests.

## Medium-priority risks

### 3. Independent executors diverge from inherited process fix
- **Risk**: Non-`ClaudeProcess` executors may still miss `--tools default`.
- **Severity**: Medium
- **Mitigation**:
  1. Review all independent command builders during Phase 1.5 assessment
  2. Patch in same release if they are in active path
- **Contingency**:
  - Add follow-up hardening task if not required for v2.25.1 scope.

### 4. Future prompt-template growth erodes safe embed margin
- **Risk**: 8 KB overhead becomes insufficient over time.
- **Severity**: Medium
- **Mitigation**:
  1. Use named constants with derivation comments
  2. Maintain import-time assertion
  3. Keep tests based on composed-size behavior, not assumptions
- **Contingency**:
  - Revise overhead constant in a future maintenance release if prompt templates expand.

### 5. Cross-platform command-line limits differ
- **Risk**: Windows constraints may behave differently than Linux assumptions.
- **Severity**: Medium
- **Mitigation**:
  1. Keep release explicitly Linux-first
  2. Avoid unnecessary command bloat
  3. Document platform boundary if needed
- **Contingency**:
  - Open separate platform-compatibility task rather than expanding this release.

## Low-priority risks

### 6. Index-sensitive tests fail after flag insertion
- **Risk**: Existing assertions may assume old flag offsets.
- **Severity**: Low
- **Mitigation**:
  1. Update tests in the same work stream as command change
  2. Prefer presence/adjacency assertions over brittle index assumptions

### 7. Unexpected model behavior from enabling default tools
- **Risk**: Subprocess behavior changes subtly.
- **Severity**: Low
- **Mitigation**:
  1. Keep default toolset aligned with interactive baseline
  2. Use smoke tests to detect behavioral regressions

### 8. Unnecessary fallback for near-limit inputs
- **Risk**: Conservative overhead may trigger fallback earlier than needed.
- **Severity**: Low
- **Mitigation**:
  1. Accept conservative behavior as functionally correct
  2. Prioritize correctness over maximizing inline size

---

## 4. Resource requirements and dependencies

## Engineering resources

1. **Primary implementation owner**
   - Python CLI engineer familiar with command assembly and roadmap executor flow

2. **Validation owner**
   - QA-focused engineer or same owner performing evidence-based verification

3. **Review focus**
   - Command construction correctness
   - Boundary-condition testing
   - Conditional path review if Phase 1.5 activates

## Required tools and runtime dependencies

1. **`claude` CLI**
   - Installed
   - Authenticated
   - Capable of simple `--print` execution

2. **`uv`**
   - Required for all Python test and script operations

3. **Repository code targets**
   - `src/superclaude/cli/pipeline/process.py`
   - `src/superclaude/cli/roadmap/executor.py`
   - conditional:
     - `src/superclaude/cli/roadmap/remediate_executor.py`
     - `src/superclaude/cli/roadmap/validate_executor.py`
     - `src/superclaude/cli/tasklist/executor.py`

4. **Reference artifacts**
   - Generated specs and tasklists in `docs/generated/`

## Dependency handling plan

1. **External dependency gating**
   - Verify `claude --print` basic health before Phase 0.
   - Verify `uv` environment before any test execution.

2. **Architectural dependency handling**
   - Confirm inheritance assumptions before changing `build_command()`.
   - Confirm non-inheriting executors only enter scope if Phase 0 activates contingency.

3. **Operational dependency handling**
   - Run targeted tests before grouped suite to reduce diagnosis cost.
   - Preserve no-new-imports and no-new-abstractions constraints.

---

## 5. Success criteria and validation approach

## Validation strategy

Use a layered validation model:

1. **Empirical CLI validation**
   - Phase 0 `--file` proof
2. **Unit-level command validation**
   - command list structure and invariants
3. **Boundary-condition validation**
   - exact limit, near limit, composed overflow
4. **Workflow-level validation**
   - sprint dry-run
   - large spec execution path

## Success criteria grouping

### A. Command assembly success
1. `--tools` present in built command
2. `default` adjacent to `--tools`
3. legacy flags preserved
4. `extra_args` ordering preserved
5. conditional `--model` behavior preserved

### B. Embed guard success
1. `_EMBED_SIZE_LIMIT` derived from named constants
2. import-time assertion present
3. guard evaluates composed byte length
4. exact-limit case embeds inline
5. overflow case falls back correctly

### C. Test success
1. pipeline tests pass
2. renamed guard test passes
3. composed-string regression test passes
4. grouped sprint/roadmap/pipeline suite passes

### D. Operational success
1. Phase 0 result recorded
2. sprint dry-run passes
3. large spec file completes without `Argument list too long`
4. if Phase 0 is BROKEN, fallback remediation tests pass

## Evidence collection checklist

- [ ] Phase 0 result captured
- [ ] subclass review completed
- [ ] constants updated and audited
- [ ] no new imports added
- [ ] targeted tests green
- [ ] grouped tests green
- [ ] dry-run green
- [ ] large-input scenario green

### Analyzer recommendation
Do not mark the release complete until all four validation layers have evidence. Passing only unit tests is insufficient for this change set.

---

## 6. Timeline estimates per phase

Due to the project rule against speculative duration commitments, the roadmap uses **relative effort and sequencing estimates** rather than calendar promises.

## Phase effort profile

1. **Phase 0 — Blocking empirical validation**
   - **Relative effort**: Very low
   - **Sequence position**: First, mandatory
   - **Dependency profile**: Blocks all downstream certainty

2. **Phase 1 — Tool schema discovery fix**
   - **Relative effort**: Low
   - **Sequence position**: Early
   - **Dependency profile**: Should complete before grouped test execution

3. **Phase 1.5 — Conditional fallback remediation**
   - **Relative effort**: Medium
   - **Sequence position**: Conditional after Phase 0
   - **Dependency profile**: Only required if `--file` is BROKEN; expands scope materially

4. **Phase 2 — Embed guard correction**
   - **Relative effort**: Low to medium
   - **Sequence position**: After Phase 0, in parallel planning with Phase 1 but validated separately
   - **Dependency profile**: Core correctness phase for large-input behavior

5. **Phase 3 — Test suite alignment and regression coverage**
   - **Relative effort**: Medium
   - **Sequence position**: After implementation changes
   - **Dependency profile**: Depends on completed code edits and known Phase 0 outcome

6. **Phase 4 — End-to-end validation and release readiness**
   - **Relative effort**: Medium
   - **Sequence position**: Final
   - **Dependency profile**: Requires all prior phases complete

## Recommended execution cadence

1. **Wave 1**
   - Phase 0
   - Phase 1 design verification
   - Phase 2 design verification

2. **Wave 2**
   - Phase 1 implementation
   - Phase 2 implementation
   - Phase 1.5 implementation only if triggered

3. **Wave 3**
   - Phase 3 test completion
   - Phase 4 release validation

## Critical path

The likely critical path is:

1. Phase 0 validation
2. Phase 2 embed guard correctness
3. Phase 3 boundary/regression tests
4. Phase 4 large-input validation

If Phase 0 returns **BROKEN**, then the critical path expands to include **Phase 1.5**, which becomes release-blocking.

---

## Recommended milestone summary

1. **M0** — `--file` behavior verified
2. **M1** — `ClaudeProcess` emits `--tools default`
3. **M1.5** — conditional fallback remediation complete if needed
4. **M2** — embed guard aligned to composed-byte reality
5. **M3** — regression suite updated and passing
6. **M4** — release candidate validated and ready

---

## Final analyzer recommendation

Proceed with a **gated, evidence-first execution plan**:

1. Resolve the Phase 0 uncertainty first.
2. Keep implementation changes minimal and local.
3. Prioritize composed-size correctness over convenience.
4. Treat non-inheriting executors as a conditional risk cluster.
5. Require end-to-end proof for large-input workflows before release closure.

This release is manageable, but only if the team maintains strict sequencing and does not skip empirical validation.
