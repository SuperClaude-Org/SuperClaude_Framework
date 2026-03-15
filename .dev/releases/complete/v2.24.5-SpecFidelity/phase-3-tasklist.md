# Phase 3 -- FIX-ARG-TOO-LONG Constants and Guard

This phase replaces the hardcoded 200 KB embed limit with derived constants based on Linux kernel `MAX_ARG_STRLEN` (128 KB) and fixes the guard to measure the composed string (prompt + embedded). This is the primary critical path fix addressing an active hard-crash `OSError`.

### T03.01 -- Replace embed constants in `executor.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002, R-014 |
| Why | The hardcoded `_EMBED_SIZE_LIMIT = 200 * 1024` exceeds Linux kernel `MAX_ARG_STRLEN` (128 KB), causing `OSError: [Errno 7] Argument list too long` for large spec files. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (constant value reduction from 200 KB to 120 KB) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0012/evidence.md

**Deliverables:**
- Modified `src/superclaude/cli/roadmap/executor.py` with three named constants replacing `_EMBED_SIZE_LIMIT = 200 * 1024`: (1) `_MAX_ARG_STRLEN = 128 * 1024`, (2) `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024`, (3) `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/executor.py` and locate `_EMBED_SIZE_LIMIT` constant
2. **[PLANNING]** Verify no `import resource` exists (must not be added per roadmap)
3. **[EXECUTION]** Remove `_EMBED_SIZE_LIMIT = 200 * 1024` and any stale `# 100 KB` comment
4. **[EXECUTION]** Add three constants with required inline comments: `_MAX_ARG_STRLEN = 128 * 1024` (Linux kernel compile-time constant), `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024` (2.3x safety factor, measured template peak ~3.4 KB), `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` (derivation and resulting 120 KB = 122,880 bytes)
5. **[VERIFICATION]** Sub-agent confirms: three constants present, comments match spec, no `import resource`, stale comments removed
6. **[COMPLETION]** Record diff and verification in D-0012/evidence.md

**Acceptance Criteria:**
- `_MAX_ARG_STRLEN = 128 * 1024` with inline comment stating Linux kernel compile-time constant
- `_PROMPT_TEMPLATE_OVERHEAD = 8 * 1024` with inline comment noting 2.3x safety factor and measured template peak (~3.4 KB)
- `_EMBED_SIZE_LIMIT = _MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` with inline comment noting derivation and resulting value (120 KB = 122,880 bytes)
- No `import resource` statement in `executor.py`; no stale `# 100 KB` comment remains

**Validation:**
- Manual check: three constants with specified comments present in `executor.py`; old constant removed
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0012/evidence.md

**Dependencies:** T01.05 (Phase 1 must complete first)
**Rollback:** `git checkout src/superclaude/cli/roadmap/executor.py`
**Notes:** Primary critical path item. RISK-006 (template growth exceeds 8 KB) mitigated by 2.3x safety factor and assertion in T03.02.

---

### T03.02 -- Add module-level overhead assertion in `executor.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | Mandatory FR-ATL.1 deliverable: assertion tripwire fires on every import if `_PROMPT_TEMPLATE_OVERHEAD` drops below safe threshold. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0013/evidence.md

**Deliverables:**
- Module-level assertion `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` immediately after the three constant definitions in `executor.py`, with error message stating kernel margin rationale and measured template peak (~3.4 KB)

**Steps:**
1. **[PLANNING]** Locate the three constant definitions from T03.01 in `executor.py`
2. **[PLANNING]** Determine assertion placement: immediately after the three constants
3. **[EXECUTION]** Add `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096, "<error message>"` with message stating kernel margin rationale and measured template peak (~3.4 KB)
4. **[EXECUTION]** Verify assertion fires on `import executor` (module-level)
5. **[VERIFICATION]** Sub-agent confirms assertion present, correctly placed, error message matches spec
6. **[COMPLETION]** Record code and verification in D-0013/evidence.md

**Acceptance Criteria:**
- `assert _PROMPT_TEMPLATE_OVERHEAD >= 4096` appears immediately after the three constant definitions
- Error message states the kernel margin rationale and the measured template peak (~3.4 KB)
- Assertion fires on every `import executor` call (module-level, not inside a function)
- Assertion is a mandatory FR-ATL.1 deliverable, not an open question

**Validation:**
- Manual check: `python -c "from superclaude.cli.roadmap import executor"` succeeds (assertion passes)
- Evidence: assertion code in .dev/releases/current/v2.24.5/artifacts/D-0013/evidence.md

**Dependencies:** T03.01
**Rollback:** `git checkout src/superclaude/cli/roadmap/executor.py`
**Notes:** None.

---

### T03.03 -- Fix embed guard to measure composed string

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | Current guard measures only the embedded file size, not the composed string (prompt + embedded), which can still exceed `MAX_ARG_STRLEN` when prompt is large. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | breaking change (guard now measures composed string, may trigger fallback more often) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0014/evidence.md

**Deliverables:**
- Fixed embed guard in `executor.py`: evaluates `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` where `composed = step.prompt + "\n\n" + embedded`, with `<=` operator and verbatim code comment

**Steps:**
1. **[PLANNING]** Read `executor.py` and locate the existing embed guard logic
2. **[PLANNING]** Identify where `composed = step.prompt + "\n\n" + embedded` should be constructed
3. **[EXECUTION]** Replace guard with `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT`
4. **[EXECUTION]** Add verbatim comment: `# <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB`
5. **[EXECUTION]** Update warning log to report "composed prompt" and byte count
6. **[VERIFICATION]** Sub-agent confirms: `<=` operator (not `<`), composed string measurement, verbatim comment present
7. **[COMPLETION]** Record diff and verification in D-0014/evidence.md

**Acceptance Criteria:**
- Guard evaluates `len(composed.encode("utf-8")) <= _EMBED_SIZE_LIMIT` (not `<`)
- `composed = step.prompt + "\n\n" + embedded` used as measurement target
- Verbatim code comment `# <= is intentional; _EMBED_SIZE_LIMIT = 120 KB is safely below MAX_ARG_STRLEN = 128 KB` present adjacent to guard
- Warning log reports "composed prompt" and byte count (not just file size)

**Validation:**
- `uv run pytest tests/roadmap/test_file_passing.py -v` exits 0
- Evidence: diff in .dev/releases/current/v2.24.5/artifacts/D-0014/evidence.md

**Dependencies:** T03.01, T03.02
**Rollback:** `git checkout src/superclaude/cli/roadmap/executor.py`
**Notes:** Boundary semantics: `<=` means at-limit inputs embed inline, not trigger fallback. RISK-005 accepted.

---

### T03.04 -- Update renamed `test_embed_size_guard_fallback` class

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | The renamed test class (from Phase 4) must import `_EMBED_SIZE_LIMIT` from `executor` and use it in assertions to auto-adapt to the new value. |
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
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0015/evidence.md

**Deliverables:**
- Updated `test_embed_size_guard_fallback` class in `tests/roadmap/test_file_passing.py`: docstring references `_EMBED_SIZE_LIMIT`, test imports and uses `_EMBED_SIZE_LIMIT` from `executor` (no hardcoded byte counts)

**Steps:**
1. **[PLANNING]** Read `tests/roadmap/test_file_passing.py` and locate the renamed test class
2. **[PLANNING]** Identify all hardcoded byte counts that should reference `_EMBED_SIZE_LIMIT`
3. **[EXECUTION]** Add `from superclaude.cli.roadmap.executor import _EMBED_SIZE_LIMIT` import
4. **[EXECUTION]** Replace hardcoded byte counts with `_EMBED_SIZE_LIMIT` references; update docstring
5. **[VERIFICATION]** `uv run pytest tests/roadmap/test_file_passing.py::test_embed_size_guard_fallback -v` exits 0
6. **[COMPLETION]** Record test diff and output in D-0015/evidence.md

**Acceptance Criteria:**
- Test class imports `_EMBED_SIZE_LIMIT` from `superclaude.cli.roadmap.executor`
- No hardcoded byte counts remain in test class assertions
- Docstring references `_EMBED_SIZE_LIMIT` (not the old 100 KB or 200 KB values)
- Test passes with `uv run pytest tests/roadmap/test_file_passing.py::test_embed_size_guard_fallback -v`

**Validation:**
- `uv run pytest tests/roadmap/test_file_passing.py::test_embed_size_guard_fallback -v` exits 0
- Evidence: test diff in .dev/releases/current/v2.24.5/artifacts/D-0015/evidence.md

**Dependencies:** T03.01, T04.01 (rename must happen first or concurrently)
**Rollback:** `git checkout tests/roadmap/test_file_passing.py`
**Notes:** None.

---

### Checkpoint: Phase 3 / Tasks T03.01-T03.05

**Purpose:** Verify embed guard constants and composed-string measurement are correct before boundary testing.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P03-T01-T05.md

**Verification:**
- Three named constants present in `executor.py` with required inline comments
- Module-level assertion present immediately after constants
- Guard measures composed string with `<=` operator and verbatim comment

**Exit Criteria:**
- SC-004 through SC-008 success criteria met (embed guard constants and behavior)
- `executor.py` modifications verified by sub-agent
- Test class updated with dynamic `_EMBED_SIZE_LIMIT` reference

---

### T03.05 -- Add `TestComposedStringGuard` test class

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | Per spec Section 4.2 and Section 8.1 test inventory: need test verifying that file at 90% of `_EMBED_SIZE_LIMIT` + large prompt exceeding composed limit triggers fallback correctly. |
| Effort | M |
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
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0016/evidence.md

**Deliverables:**
- New `TestComposedStringGuard` class in `tests/roadmap/test_file_passing.py` with test method `test_prompt_plus_embedded_exceeds_limit`

**Steps:**
1. **[PLANNING]** Read `tests/roadmap/test_file_passing.py` to understand test patterns and fixtures
2. **[PLANNING]** Design test scenario: file at 90% of `_EMBED_SIZE_LIMIT` + prompt large enough to exceed composed limit
3. **[EXECUTION]** Add `TestComposedStringGuard` class with `test_prompt_plus_embedded_exceeds_limit` method
4. **[EXECUTION]** Assert: fallback fires (file content absent from prompt), `--file` present in `extra_args`
5. **[VERIFICATION]** `uv run pytest tests/roadmap/test_file_passing.py::TestComposedStringGuard -v` exits 0
6. **[COMPLETION]** Record test code and output in D-0016/evidence.md

**Acceptance Criteria:**
- `TestComposedStringGuard` class exists in `tests/roadmap/test_file_passing.py`
- Test method named `test_prompt_plus_embedded_exceeds_limit` per spec Section 8.1
- Scenario: file at 90% of `_EMBED_SIZE_LIMIT` + prompt large enough to exceed composed limit
- Assertions: fallback fires, file content absent from prompt, `--file` in `extra_args`

**Validation:**
- `uv run pytest tests/roadmap/test_file_passing.py::TestComposedStringGuard -v` exits 0
- Evidence: test code in .dev/releases/current/v2.24.5/artifacts/D-0016/evidence.md

**Dependencies:** T03.03
**Rollback:** `git checkout tests/roadmap/test_file_passing.py`
**Notes:** Per spec Section 4.2 and Section 8.1 test inventory.

---

### T03.06 -- Add exact-limit boundary test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019 |
| Why | Boundary inclusion verification: composed length exactly equal to `_EMBED_SIZE_LIMIT` must still embed inline (`<=` is intentional). |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0017/evidence.md

**Deliverables:**
- Boundary test verifying composed length exactly equal to `_EMBED_SIZE_LIMIT` embeds inline (does not trigger fallback)

**Steps:**
1. **[PLANNING]** Calculate exact byte counts for prompt + "\n\n" + embedded to reach `_EMBED_SIZE_LIMIT` exactly
2. **[PLANNING]** Design test with controlled prompt and file content sizes
3. **[EXECUTION]** Add boundary test in `tests/roadmap/test_file_passing.py`
4. **[EXECUTION]** Assert: inline embedding occurs (no fallback), content present in prompt
5. **[VERIFICATION]** Sub-agent confirms boundary semantics correct (`<=` means at-limit embeds)
6. **[COMPLETION]** Record test code and output in D-0017/evidence.md

**Acceptance Criteria:**
- Composed length exactly `_EMBED_SIZE_LIMIT` bytes embeds inline (no fallback triggered)
- Test validates `<=` boundary semantics as specified in T03.03
- Composed length `_EMBED_SIZE_LIMIT + 1` bytes triggers fallback (over-limit case)
- Test code recorded in .dev/releases/current/v2.24.5/artifacts/D-0017/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/test_file_passing.py -v` exits 0 (boundary test included)
- Evidence: test code in .dev/releases/current/v2.24.5/artifacts/D-0017/evidence.md

**Dependencies:** T03.03
**Rollback:** `git checkout tests/roadmap/test_file_passing.py`
**Notes:** `<=` is intentional per roadmap Task 1.2.3 and Task 1.2.6.

---

### T03.07 -- Run roadmap tests for Phase 3 validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | Full roadmap test file must pass with 0 failures to confirm FIX-ARG-TOO-LONG introduces no regressions. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0018/evidence.md

**Deliverables:**
- `uv run pytest tests/roadmap/test_file_passing.py -v` output showing 0 failures

**Steps:**
1. **[PLANNING]** Confirm all Phase 3 code and test changes are saved
2. **[PLANNING]** Verify no uncommitted changes outside Phase 3 scope
3. **[EXECUTION]** Run `uv run pytest tests/roadmap/test_file_passing.py -v`
4. **[EXECUTION]** Capture full test output including pass/fail counts
5. **[VERIFICATION]** Confirm 0 failures in output
6. **[COMPLETION]** Record full test output in D-0018/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_file_passing.py -v` exits with code 0
- Output shows 0 failures across all roadmap file-passing tests
- No test skips that mask failures
- Full test output recorded in .dev/releases/current/v2.24.5/artifacts/D-0018/evidence.md

**Validation:**
- `uv run pytest tests/roadmap/test_file_passing.py -v` exits 0
- Evidence: complete test output in .dev/releases/current/v2.24.5/artifacts/D-0018/evidence.md

**Dependencies:** T03.04, T03.05, T03.06
**Rollback:** N/A (test execution only)
**Notes:** Senior review should concentrate on embed guard constants, composed-size measurement, and large-input boundary tests.

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm FIX-ARG-TOO-LONG is fully implemented with all constants, guard logic, and tests passing before integration.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P03-END.md

**Verification:**
- `_EMBED_SIZE_LIMIT` derived from `_MAX_ARG_STRLEN - _PROMPT_TEMPLATE_OVERHEAD` (120 KB = 122,880 bytes)
- Module-level assertion fires on import; guard measures composed string with `<=`
- `uv run pytest tests/roadmap/test_file_passing.py -v` shows 0 failures

**Exit Criteria:**
- SC-004 through SC-009 success criteria met (embed guard)
- All boundary tests pass (exact limit, composed overflow)
- No regressions in existing roadmap tests
