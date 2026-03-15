# Phase 2 -- FIX-001 Add --tools default

This phase adds `--tools default` to `ClaudeProcess.build_command()` so all subprocess invocations include tool access that interactive mode provides automatically. Must complete before any combined test suite run (Phase 6) to avoid index-based assertion failures from flag position shifts.

### T02.01 -- Verify no subclass overrides of `build_command()`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | Must confirm no `ClaudeProcess` subclass overrides `build_command()` without calling `super()`, which would silently drop the new `--tools default` flag. Implements RISK-002 mitigation. |
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
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0006/evidence.md

**Deliverables:**
- Audit report listing all `ClaudeProcess` subclasses and confirming none override `build_command()` without `super()` call

**Steps:**
1. **[PLANNING]** Identify all files importing or subclassing `ClaudeProcess`
2. **[PLANNING]** Enumerate subclasses and their method overrides
3. **[EXECUTION]** Read each subclass source and check for `build_command()` override
4. **[EXECUTION]** For any override found, verify `super().build_command()` is called
5. **[VERIFICATION]** Confirm zero subclasses override without `super()` — sub-agent verification
6. **[COMPLETION]** Record subclass audit results in D-0006/evidence.md

**Acceptance Criteria:**
- All `ClaudeProcess` subclasses enumerated with file paths in audit report
- Zero subclasses override `build_command()` without calling `super()`
- Audit covers `src/superclaude/cli/` directory tree exhaustively
- Report recorded in .dev/releases/current/v2.24.5/artifacts/D-0006/evidence.md

**Validation:**
- Manual check: grep for `class.*ClaudeProcess` and `def build_command` across `src/superclaude/cli/`
- Evidence: subclass audit in .dev/releases/current/v2.24.5/artifacts/D-0006/evidence.md

**Dependencies:** T01.05 (Phase 1 must complete first)
**Rollback:** N/A (read-only audit)
**Notes:** Roadmap addition implementing RISK-002 mitigation (OQ-6); not in spec Section 11.

---

### T02.02 -- Add `--tools default` to `process.py` `build_command()`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | `ClaudeProcess.build_command()` omits `--tools default`, causing subprocess invocations to lack tool access that interactive mode provides automatically. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | multi-file scope (process.py + downstream tests) |
| Tier | STRICT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0007/evidence.md

**Deliverables:**
- Modified `src/superclaude/cli/pipeline/process.py` with `"--tools", "default"` added after `--no-session-persistence` and before `--max-turns` in `build_command()`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/pipeline/process.py` and locate `build_command()` method
2. **[PLANNING]** Identify insertion point: after `--no-session-persistence`, before `--max-turns`
3. **[EXECUTION]** Add `"--tools", "default"` at the identified insertion point
4. **[EXECUTION]** Verify no other flags or `extra_args` ordering is disrupted
5. **[VERIFICATION]** Sub-agent confirms flag presence and adjacency in built command
6. **[COMPLETION]** Record diff and verification in D-0007/evidence.md

**Acceptance Criteria:**
- `"--tools"` and `"default"` appear in `build_command()` output as adjacent elements
- Insertion is after `"--no-session-persistence"` and before `"--max-turns"`
- Legacy flags (`--print`, `--no-session-persistence`, `--max-turns`) remain present and correctly ordered
- `extra_args` ordering and conditional `--model` behavior preserved

**Validation:**
- `uv run pytest tests/pipeline/test_process.py -v` exits 0
- Evidence: diff of `process.py` in .dev/releases/current/v2.24.5/artifacts/D-0007/evidence.md

**Dependencies:** T02.01
**Rollback:** `git checkout src/superclaude/cli/pipeline/process.py`
**Notes:** 2-line addition per roadmap. RISK-001 (very low probability) mitigated by matching interactive mode baseline.

---

### T02.03 -- Update `test_required_flags` assertion

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | Existing test must verify the newly added `--tools` and `default` flags are present in the command list. |
| Effort | XS |
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
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0008/evidence.md

**Deliverables:**
- Updated `test_required_flags` in `tests/pipeline/test_process.py` asserting `--tools` and `default` present in command list

**Steps:**
1. **[PLANNING]** Read `tests/pipeline/test_process.py` and locate `test_required_flags`
2. **[PLANNING]** Identify assertion pattern used for existing flags
3. **[EXECUTION]** Add assertions: `"--tools" in cmd` and `"default" in cmd`
4. **[EXECUTION]** Ensure assertion style matches existing test patterns
5. **[VERIFICATION]** `uv run pytest tests/pipeline/test_process.py::test_required_flags -v` exits 0
6. **[COMPLETION]** Record test output in D-0008/evidence.md

**Acceptance Criteria:**
- `test_required_flags` asserts `"--tools"` present in command list
- `test_required_flags` asserts `"default"` present in command list
- Test passes with `uv run pytest tests/pipeline/test_process.py::test_required_flags -v`
- Test diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0008/evidence.md

**Validation:**
- `uv run pytest tests/pipeline/test_process.py::test_required_flags -v` exits 0
- Evidence: test output in .dev/releases/current/v2.24.5/artifacts/D-0008/evidence.md

**Dependencies:** T02.02
**Rollback:** `git checkout tests/pipeline/test_process.py`
**Notes:** None.

---

### T02.04 -- Update `test_stream_json_matches_sprint_flags` assertion

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | Second existing test must also verify `--tools` and `default` presence to maintain consistency with T02.03. |
| Effort | XS |
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
| Deliverable IDs | D-0009 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0009/evidence.md

**Deliverables:**
- Updated `test_stream_json_matches_sprint_flags` in `tests/pipeline/test_process.py` asserting `--tools` and `default` present

**Steps:**
1. **[PLANNING]** Read `tests/pipeline/test_process.py` and locate `test_stream_json_matches_sprint_flags`
2. **[PLANNING]** Identify assertion pattern for sprint flags
3. **[EXECUTION]** Add assertions: `"--tools" in cmd` and `"default" in cmd`
4. **[EXECUTION]** Verify no index-based assertions are broken by flag insertion
5. **[VERIFICATION]** `uv run pytest tests/pipeline/test_process.py::test_stream_json_matches_sprint_flags -v` exits 0
6. **[COMPLETION]** Record test output in D-0009/evidence.md

**Acceptance Criteria:**
- `test_stream_json_matches_sprint_flags` asserts `"--tools"` and `"default"` present
- No index-based assertion failures from flag position shifts (RISK-003 mitigation)
- Test passes with `uv run pytest tests/pipeline/test_process.py::test_stream_json_matches_sprint_flags -v`
- Test diff recorded in .dev/releases/current/v2.24.5/artifacts/D-0009/evidence.md

**Validation:**
- `uv run pytest tests/pipeline/test_process.py::test_stream_json_matches_sprint_flags -v` exits 0
- Evidence: test output in .dev/releases/current/v2.24.5/artifacts/D-0009/evidence.md

**Dependencies:** T02.02
**Rollback:** `git checkout tests/pipeline/test_process.py`
**Notes:** RISK-003 (index-based assertion breakage) mitigated by completing Phase 2 before Phase 6.

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.05

**Purpose:** Verify FIX-001 implementation is correct before running the adjacency test and full pipeline suite.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P02-T01-T05.md

**Verification:**
- T02.01 audit confirms zero unsafe subclass overrides
- T02.02 `process.py` contains `"--tools", "default"` at correct insertion point
- T02.03 and T02.04 test assertions updated and passing individually

**Exit Criteria:**
- Subclass audit complete with no blocking findings
- `process.py` modified with 2-line addition at correct location
- Both existing test updates pass in isolation

---

### T02.05 -- Add `test_tools_default_in_command` test

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | Need a dedicated test verifying `--tools` and `default` are adjacent in the command list (not just present). |
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
| Deliverable IDs | D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0010/evidence.md

**Deliverables:**
- New `test_tools_default_in_command` test in `tests/pipeline/test_process.py` asserting `cmd[cmd.index("--tools") + 1] == "default"`

**Steps:**
1. **[PLANNING]** Review existing test structure in `tests/pipeline/test_process.py`
2. **[PLANNING]** Design adjacency assertion: `cmd[cmd.index("--tools") + 1] == "default"`
3. **[EXECUTION]** Add new test function `test_tools_default_in_command`
4. **[EXECUTION]** Implement adjacency check per roadmap specification
5. **[VERIFICATION]** `uv run pytest tests/pipeline/test_process.py::test_tools_default_in_command -v` exits 0
6. **[COMPLETION]** Record test code and output in D-0010/evidence.md

**Acceptance Criteria:**
- Test function `test_tools_default_in_command` exists in `tests/pipeline/test_process.py`
- Assertion verifies `cmd[cmd.index("--tools") + 1] == "default"` (adjacency, not just presence)
- Test passes with `uv run pytest tests/pipeline/test_process.py::test_tools_default_in_command -v`
- Test code recorded in .dev/releases/current/v2.24.5/artifacts/D-0010/evidence.md

**Validation:**
- `uv run pytest tests/pipeline/test_process.py::test_tools_default_in_command -v` exits 0
- Evidence: test code and output in .dev/releases/current/v2.24.5/artifacts/D-0010/evidence.md

**Dependencies:** T02.02
**Rollback:** `git checkout tests/pipeline/test_process.py`
**Notes:** None.

---

### T02.06 -- Run pipeline tests for Phase 2 validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | Full pipeline test suite must pass with 0 failures to confirm FIX-001 introduces no regressions. |
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
| Deliverable IDs | D-0011 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.24.5/artifacts/D-0011/evidence.md

**Deliverables:**
- `uv run pytest tests/pipeline/test_process.py -v` output showing 0 failures

**Steps:**
1. **[PLANNING]** Confirm all Phase 2 code and test changes are saved
2. **[PLANNING]** Verify no uncommitted changes outside Phase 2 scope
3. **[EXECUTION]** Run `uv run pytest tests/pipeline/test_process.py -v`
4. **[EXECUTION]** Capture full test output including pass/fail counts
5. **[VERIFICATION]** Confirm 0 failures in output
6. **[COMPLETION]** Record full test output in D-0011/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/pipeline/test_process.py -v` exits with code 0
- Output shows 0 failures across all pipeline tests
- No test skips that mask failures
- Full test output recorded in .dev/releases/current/v2.24.5/artifacts/D-0011/evidence.md

**Validation:**
- `uv run pytest tests/pipeline/test_process.py -v` exits 0
- Evidence: complete test output in .dev/releases/current/v2.24.5/artifacts/D-0011/evidence.md

**Dependencies:** T02.03, T02.04, T02.05
**Rollback:** N/A (test execution only)
**Notes:** Ordering constraint: Phase 2 must complete before combined suite (Phase 6).

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm FIX-001 is fully implemented and validated before proceeding to FIX-ARG-TOO-LONG or integration testing.
**Checkpoint Report Path:** .dev/releases/current/v2.24.5/checkpoints/CP-P02-END.md

**Verification:**
- `--tools default` present and adjacent in `build_command()` output
- All three test updates/additions pass individually and in suite
- `uv run pytest tests/pipeline/test_process.py -v` shows 0 failures

**Exit Criteria:**
- SC-001, SC-002, SC-003 success criteria met (command assembly)
- Pipeline test suite passes with 0 failures
- No regressions in existing tests
