# Phase 4 -- CLI Integration & State Persistence

Wire the validation executor into the CLI surface: add `roadmap validate` subcommand, integrate auto-invocation after successful `roadmap run`, implement `--no-validate` skip flag, and persist validation status in `.roadmap-state.json` for resume awareness.

---

### T04.01 -- Confirm Tier Classifications for Phase 4 Tasks

| Field | Value |
|---|---|
| Roadmap Item IDs | -- |
| Why | Tier classifications for Phase 4 tasks have confidence < 0.70. Multiple tasks modify shared state files, warranting tier confirmation. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0012 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0012/notes.md`

**Deliverables:**
- Confirmed tier assignments for T04.02 (STANDARD), T04.03 (STRICT), T04.04 (STRICT), T04.05 (STANDARD), T04.06 (STANDARD)

**Steps:**
1. **[PLANNING]** Review tier assignments for T04.02 through T04.06
2. **[PLANNING]** Assess T04.03 (STRICT due to multi-file modification) and T04.04 (STRICT due to state persistence)
3. **[EXECUTION]** Record confirmed or overridden tier for each task
4. **[EXECUTION]** Document override reasoning if any tier is changed
5. **[VERIFICATION]** Verify all five tasks have confirmed tiers
6. **[COMPLETION]** Write decision artifact to D-0012/notes.md

**Acceptance Criteria:**
- File `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0012/notes.md` exists with confirmed tiers for T04.02 through T04.06
- Each tier decision includes a one-line justification
- Override reasons documented if any tier differs from computed assignment
- Traceability maintained (task IDs referenced in decision artifact)

**Validation:**
- Manual check: all Phase 4 tasks have a confirmed tier recorded in D-0012/notes.md
- Evidence: linkable artifact produced (D-0012/notes.md)

**Dependencies:** None
**Rollback:** TBD
**Notes:** Clarification task for batch tier confirmation.

---

### T04.02 -- Add `validate` Subcommand and `--no-validate` Flag to `commands.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016, R-017 |
| Why | The CLI surface must expose standalone validation and a skip flag for users who want to run the pipeline without post-validation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0013/spec.md`

**Deliverables:**
- `validate` subcommand added to the `roadmap` Click group in `src/superclaude/cli/roadmap/commands.py` with `--agents`, `--model`, `--max-turns`, `--debug` options; `--no-validate` flag added to `roadmap run`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/commands.py` to understand existing Click group structure and option patterns
2. **[PLANNING]** Identify where to add the `validate` subcommand and `--no-validate` flag
3. **[EXECUTION]** Add `validate` subcommand under the `roadmap` Click group with `--agents` (default per roadmap: single for standalone), `--model`, `--max-turns`, `--debug` options
4. **[EXECUTION]** Add `--no-validate` boolean flag to the existing `roadmap run` command
5. **[EXECUTION]** Wire `validate` subcommand to call `execute_validate()` with constructed `ValidateConfig`
6. **[VERIFICATION]** Run `superclaude roadmap validate --help` to verify CLI surface
7. **[COMPLETION]** Record CLI specification in D-0013/spec.md

**Acceptance Criteria:**
- `superclaude roadmap validate --help` displays usage with `--agents`, `--model`, `--max-turns`, `--debug` options
- `superclaude roadmap run --help` displays `--no-validate` flag
- `validate` subcommand constructs `ValidateConfig` from CLI arguments and calls `execute_validate`
- Default agent count for standalone `validate` is 1 (single-agent for cost efficiency per OQ-1)

**Validation:**
- `superclaude roadmap validate --help` exits 0 and shows expected options
- Evidence: linkable artifact produced (D-0013/spec.md)

**Dependencies:** T03.02, T04.01
**Rollback:** TBD
**Notes:** None

---

### T04.03 -- Integrate Auto-Invocation and Skip Logic in `executor.py`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018, R-019, R-020, R-021 |
| Why | Validation must auto-invoke after successful pipeline runs and respect skip conditions (`--no-validate`, failed `--resume`). |
| Effort | M |
| Risk | Medium |
| Risk Drivers | cross-cutting (modifies executor.py which orchestrates the entire pipeline) |
| Tier | STRICT |
| Confidence | [█████░░░░░] 50% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0014/spec.md`

**Deliverables:**
- Auto-invocation of `execute_validate()` from `execute_roadmap()` in `src/superclaude/cli/roadmap/executor.py` with option inheritance and skip conditions

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/roadmap/executor.py` to understand `execute_roadmap()` flow, success detection, and `--resume` handling
2. **[PLANNING]** Map the 4 skip/invoke conditions: invoke after 8-step success, skip on `--no-validate`, skip on resumed-failure, inherit options from parent
3. **[EXECUTION]** Add `execute_validate()` call at the end of `execute_roadmap()` after all 8 pipeline steps succeed
4. **[EXECUTION]** Inherit `--agents` (default 2 for `roadmap run` per OQ-1), `--model`, `--max-turns`, `--debug` from parent invocation
5. **[EXECUTION]** Add conditional: skip validation when `--no-validate` flag is set
6. **[EXECUTION]** Add conditional: skip validation when `--resume` pipeline halts on a failed step (only invoke on complete success)
7. **[VERIFICATION]** Verify all 4 code paths with targeted unit tests
8. **[COMPLETION]** Record integration specification in D-0014/spec.md

**Acceptance Criteria:**
- `execute_roadmap()` calls `execute_validate()` after all 8 pipeline steps complete successfully
- `--agents` defaults to 2 for `roadmap run` invocation (dual-agent for rigor per OQ-1); `--model`, `--max-turns`, `--debug` inherited from parent
- Validation skipped when `--no-validate` is set (no `validate/` directory created)
- Validation skipped when `--resume` pipeline halts on a failed step (validation only on full success)

**Validation:**
- Manual check: trace all 4 code paths (success+invoke, no-validate+skip, resume-success+invoke, resume-failure+skip)
- Evidence: linkable artifact produced (D-0014/spec.md)

**Dependencies:** T03.02, T04.02
**Rollback:** TBD
**Notes:** Tier is STRICT due to multi-file modification (executor.py + commands.py interaction) and cross-cutting scope (+0.3 booster). Default agent count asymmetry: standalone=1 (cost), roadmap run=2 (rigor) per OQ-1.

---

### T04.04 -- Record Validation Status in `.roadmap-state.json`

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | State persistence enables `--resume` to skip re-validation of already-validated artifacts and handles edge cases that artifact-on-disk checks cannot. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | data (state file modification), schema (new JSON key) |
| Tier | STRICT |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0015/spec.md`

**Deliverables:**
- Validation status recording (`pass`/`fail`/`skipped`) in `.roadmap-state.json` under a `validation` key

**Steps:**
1. **[PLANNING]** Read `.roadmap-state.json` schema and existing state persistence patterns in `executor.py`
2. **[PLANNING]** Define `validation` key structure: `{status: "pass"|"fail"|"skipped", timestamp: ISO8601}`
3. **[EXECUTION]** After `execute_validate()` completes, write validation status to `.roadmap-state.json` under `validation` key
4. **[EXECUTION]** Write `"skipped"` status when validation is skipped (--no-validate or resume-failure)
5. **[EXECUTION]** Handle `--resume` path: check `validation` key in state file, skip re-validation if already completed
6. **[VERIFICATION]** Verify state file is written correctly after validation pass, fail, and skip scenarios
7. **[COMPLETION]** Record specification in D-0015/spec.md

**Acceptance Criteria:**
- After validation, `.roadmap-state.json` contains `"validation": {"status": "pass"|"fail"|"skipped"}` key
- `--resume` reads `validation` status and skips re-validation if already completed
- State file schema is backward-compatible (new key added, no existing keys modified)
- D-0015/spec.md documents the state schema and resume interaction

**Validation:**
- Manual check: run validation, inspect `.roadmap-state.json` for `validation` key with correct status
- Evidence: linkable artifact produced (D-0015/spec.md)

**Dependencies:** T04.03
**Rollback:** TBD
**Notes:** Tier is STRICT due to "schema" keyword match (state file schema change) and data persistence concerns.

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.05

**Purpose:** Verify CLI subcommand registration and auto-invocation logic before completing integration tests.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P04-T01-T05.md`

**Verification:**
- `superclaude roadmap validate --help` displays expected options
- `superclaude roadmap run --help` displays `--no-validate` flag
- Auto-invocation code path exists in `execute_roadmap()` with all 4 conditional branches

**Exit Criteria:**
- T04.01 through T04.05 marked completed
- CLI surface area verified manually
- State persistence schema documented

---

### T04.05 -- Implement CLI Output Behavior (Surface Warnings, Exit 0)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | Validation must surface blocking issues as warnings but always exit 0 per NFR-006, ensuring pipeline scripts don't break on validation findings. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [███░░░░░░░] 30% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0016/spec.md`

**Deliverables:**
- CLI output formatting that surfaces blocking issues as warnings and ensures exit code 0 regardless of validation findings

**Steps:**
1. **[PLANNING]** Review existing CLI output patterns in `commands.py` (click.echo, rich console usage)
2. **[PLANNING]** Define output format: blocking issues as yellow warnings, summary line with counts
3. **[EXECUTION]** Add output formatting to `validate` subcommand: print blocking issues as warnings, print summary
4. **[EXECUTION]** Ensure `sys.exit(0)` or no explicit exit (let Click handle) for all code paths including blocking findings
5. **[VERIFICATION]** Run `superclaude roadmap validate` on test input and verify exit code is 0 even with blocking issues
6. **[COMPLETION]** Record output specification in D-0016/spec.md

**Acceptance Criteria:**
- `superclaude roadmap validate` prints blocking issues as warning-level output (visible but not error-styled)
- Exit code is always 0 regardless of blocking/warning count (per NFR-006)
- Summary line shows blocking/warning/info counts
- D-0016/spec.md documents the output format

**Validation:**
- `superclaude roadmap validate <test-dir>; echo $?` outputs `0`
- Evidence: linkable artifact produced (D-0016/spec.md)

**Dependencies:** T04.02, T04.01
**Rollback:** TBD
**Notes:** None

---

### T04.06 -- Write Integration Tests for All CLI Paths

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | CLI integration tests verify the full surface area before Phase 5's comprehensive test suite. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | [████░░░░░░] 40% |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.19-roadmap-validate/artifacts/D-0017/evidence.md`

**Deliverables:**
- Integration test file covering `roadmap validate` subcommand, `--no-validate` flag, and exit code behavior

**Steps:**
1. **[PLANNING]** Review Click testing patterns in existing test files (CliRunner usage)
2. **[PLANNING]** Define test cases: validate runs successfully, --no-validate skips, exit code always 0
3. **[EXECUTION]** Create integration test file for CLI paths
4. **[EXECUTION]** Write tests using Click CliRunner for subcommand invocation
5. **[EXECUTION]** Write test for exit code 0 with blocking issues
6. **[VERIFICATION]** Run `uv run pytest <test_file> -v` and confirm all tests pass
7. **[COMPLETION]** Record test evidence in D-0017/evidence.md

**Acceptance Criteria:**
- Integration test file exists covering: `roadmap validate` invocation, `roadmap run --no-validate`, exit code verification
- Tests use Click CliRunner for consistent CLI testing
- `uv run pytest <test_file> -v` exits 0 with all tests passing
- D-0017/evidence.md records test count and pass/fail summary

**Validation:**
- `uv run pytest <test_file> -v` exits 0
- Evidence: linkable artifact produced (D-0017/evidence.md)

**Dependencies:** T04.02, T04.03, T04.04, T04.05
**Rollback:** TBD
**Notes:** None

---

### Checkpoint: End of Phase 4

**Purpose:** Verify full CLI surface area is complete, auto-invocation works, and state persistence is functional before comprehensive testing.
**Checkpoint Report Path:** `.dev/releases/current/v2.19-roadmap-validate/checkpoints/CP-P04-END.md`

**Verification:**
- `superclaude roadmap validate` subcommand registered and functional
- `roadmap run` auto-invokes validation after success; `--no-validate` skips it
- `.roadmap-state.json` records validation status correctly

**Exit Criteria:**
- All Phase 4 tasks (T04.01-T04.06) marked completed
- All CLI integration tests pass
- No reverse imports into `pipeline/` directory
