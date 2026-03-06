# Phase 1 -- Foundation & Source Defaults

Apply all 7 Tier 1 Python source default changes to establish the new `max_turns=100` and `reimbursement_rate=0.8` baseline across pipeline and sprint configuration layers. These edits form the foundation that all subsequent phases validate against.

---

### T01.01 -- Set PipelineConfig.max_turns default to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | `PipelineConfig.max_turns` defaults to 50, limiting phase execution headroom and contributing to `pass_no_report` outcomes |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[██████████] 75%` |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0001/evidence.md`

**Deliverables:**
- `PipelineConfig.max_turns` default changed from `50` to `100` at `src/superclaude/cli/pipeline/models.py:175`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/pipeline/models.py` and locate line 175 containing `max_turns: int = 50`
2. **[PLANNING]** Confirm no other references to this default value in the same file that would need coordinated changes
3. **[EXECUTION]** Edit `src/superclaude/cli/pipeline/models.py:175` to read `max_turns: int = 100`
4. **[VERIFICATION]** Run `grep -n 'max_turns.*=.*50' src/superclaude/cli/pipeline/models.py` and confirm zero matches
5. **[VERIFICATION]** Run `grep -n 'max_turns.*=.*100' src/superclaude/cli/pipeline/models.py` and confirm line 175 matches
6. **[COMPLETION]** Record evidence in D-0001 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/pipeline/models.py` line 175 reads `max_turns: int = 100`
- No other `max_turns` default values in `pipeline/models.py` remain at 50
- Edit is a single-value replacement with no structural changes to the file
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0001/evidence.md`

**Validation:**
- Manual check: `grep -n 'max_turns' src/superclaude/cli/pipeline/models.py` shows `100` at line 175
- Evidence: grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** Revert line 175 to `max_turns: int = 50`
**Notes:** Critical path override applied due to models/ path. FR-001 traceability.

---

### T01.02 -- Set SprintConfig.max_turns default to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | `SprintConfig.max_turns` must match the base `PipelineConfig` default to prevent layer mismatch |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[██████████] 75%` |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0002/evidence.md`

**Deliverables:**
- `SprintConfig.max_turns` default changed from `50` to `100` at `src/superclaude/cli/sprint/models.py:285`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/models.py` and locate line 285 containing `max_turns: int = 50`
2. **[PLANNING]** Confirm this is the `SprintConfig` class default, not `TurnLedger` or other class
3. **[EXECUTION]** Edit `src/superclaude/cli/sprint/models.py:285` to read `max_turns: int = 100`
4. **[VERIFICATION]** Run `grep -n 'max_turns.*=.*50' src/superclaude/cli/sprint/models.py` and confirm only Tier 3 explicit fixtures remain
5. **[VERIFICATION]** Run `grep -n 'max_turns.*=.*100' src/superclaude/cli/sprint/models.py` and confirm line 285 matches
6. **[COMPLETION]** Record evidence in D-0002 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/sprint/models.py` line 285 reads `max_turns: int = 100`
- No unintended changes to `TurnLedger` or other classes in the same file
- Edit is a single-value replacement with no structural changes
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0002/evidence.md`

**Validation:**
- Manual check: `grep -n 'max_turns' src/superclaude/cli/sprint/models.py` shows `100` at line 285
- Evidence: grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** Revert line 285 to `max_turns: int = 50`
**Notes:** Critical path override applied due to models/ path. FR-002 traceability.

---

### T01.03 -- Set CLI --max-turns default to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | The CLI entry point `--max-turns` option must match `PipelineConfig`/`SprintConfig` defaults to prevent user confusion |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0003/evidence.md`

**Deliverables:**
- CLI `--max-turns` option default changed from `50` to `100` at `src/superclaude/cli/sprint/commands.py:54`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/commands.py` and locate line 54 containing `default=50`
2. **[PLANNING]** Confirm this is the `--max-turns` Click option definition
3. **[EXECUTION]** Edit `src/superclaude/cli/sprint/commands.py:54` to read `default=100`
4. **[VERIFICATION]** Run `grep -n 'default=50' src/superclaude/cli/sprint/commands.py` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0003 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/sprint/commands.py` line 54 reads `default=100`
- The Click option definition for `--max-turns` is the only changed line
- Change is backwards-compatible (explicit `--max-turns=50` still works per SC-004)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0003/evidence.md`

**Validation:**
- Manual check: `grep -n 'default=' src/superclaude/cli/sprint/commands.py` shows `100` at line 54
- Evidence: grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** Revert line 54 to `default=50`

---

### T01.04 -- Update CLI --max-turns help text to "default: 100"

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | Help text must accurately reflect the new default value for user-facing documentation |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0004/evidence.md`

**Deliverables:**
- CLI `--max-turns` help string updated to reference "default: 100" at `src/superclaude/cli/sprint/commands.py:55`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/commands.py` and locate line 55 containing the help text with "default: 50"
2. **[PLANNING]** Confirm this is the help string for the `--max-turns` option (immediately follows T01.03 edit)
3. **[EXECUTION]** Edit `src/superclaude/cli/sprint/commands.py:55` to replace "default: 50" with "default: 100"
4. **[VERIFICATION]** Run `grep -n 'default: 50' src/superclaude/cli/sprint/commands.py` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0004 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/sprint/commands.py` line 55 help string reads "default: 100"
- No other help text strings in the file were modified
- String replacement is exact ("50" → "100" within help text context only)
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0004/evidence.md`

**Validation:**
- Manual check: `grep -n 'default: 100' src/superclaude/cli/sprint/commands.py` shows match at line 55
- Evidence: grep output captured in evidence artifact

**Dependencies:** T01.03 (same file; help text should match default value)
**Rollback:** Revert line 55 help text to "default: 50"

---

### T01.05 -- Set load_sprint_config max_turns default to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Function signature default must match `SprintConfig` class default to prevent override behavior |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0005/evidence.md`

**Deliverables:**
- `load_sprint_config(max_turns)` parameter default changed from `50` to `100` at `src/superclaude/cli/sprint/config.py:108`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/config.py` and locate line 108 containing `max_turns: int = 50`
2. **[PLANNING]** Confirm this is the `load_sprint_config` function signature parameter default
3. **[EXECUTION]** Edit `src/superclaude/cli/sprint/config.py:108` to read `max_turns: int = 100`
4. **[VERIFICATION]** Run `grep -n 'max_turns.*=.*50' src/superclaude/cli/sprint/config.py` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0005 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/sprint/config.py` line 108 reads `max_turns: int = 100`
- No other function signatures in `config.py` were modified
- Edit is a single-value replacement in the function signature
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0005/evidence.md`

**Validation:**
- Manual check: `grep -n 'max_turns' src/superclaude/cli/sprint/config.py` shows `100` at line 108
- Evidence: grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** Revert line 108 to `max_turns: int = 50`

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.05

**Purpose:** Verify the first 5 of 7 Phase 1 source default changes are correctly applied before proceeding.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P01-T01-T05.md`

**Verification:**
- All 5 files (`pipeline/models.py`, `sprint/models.py`, `sprint/commands.py` x2 lines, `sprint/config.py`) contain the updated value
- `grep -rn 'max_turns.*=.*50' src/superclaude/cli/` returns only Tier 3 locations (explicit test fixtures in tests/)
- No syntax errors introduced (files parse cleanly)

**Exit Criteria:**
- All 5 edits confirmed at their target file:line locations
- No residual `max_turns.*50` default patterns in edited source files
- No unintended changes to adjacent code

---

### T01.06 -- Set ClaudeProcess.__init__ max_turns default to 100

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | Constructor default must match `PipelineConfig` to prevent layer mismatch during process initialization |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | `[██████████] 55%` |
| Requires Confirmation | Yes |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0006/evidence.md`

**Deliverables:**
- `ClaudeProcess.__init__(max_turns)` parameter default changed from `50` to `100` at `src/superclaude/cli/pipeline/process.py:43`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/pipeline/process.py` and locate line 43 containing `max_turns: int = 50`
2. **[PLANNING]** Confirm this is the `ClaudeProcess.__init__` constructor parameter default
3. **[EXECUTION]** Edit `src/superclaude/cli/pipeline/process.py:43` to read `max_turns: int = 100`
4. **[VERIFICATION]** Run `grep -n 'max_turns.*=.*50' src/superclaude/cli/pipeline/process.py` and confirm zero matches
5. **[COMPLETION]** Record evidence in D-0006 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/pipeline/process.py` line 43 reads `max_turns: int = 100`
- No other constructor parameters or method signatures in `process.py` were modified
- Edit is a single-value replacement in the constructor signature
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0006/evidence.md`

**Validation:**
- Manual check: `grep -n 'max_turns' src/superclaude/cli/pipeline/process.py` shows `100` at line 43
- Evidence: grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** Revert line 43 to `max_turns: int = 50`

---

### T01.07 -- Set TurnLedger.reimbursement_rate default to 0.8

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | `reimbursement_rate=0.5` causes budget exhaustion at task ~33 in a 46-task sprint; 0.8 sustains 50 tasks with 200-turn budget |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | `[██████████] 75%` |
| Requires Confirmation | No |
| Critical Path Override | Yes (models/ path) |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0007/evidence.md`

**Deliverables:**
- `TurnLedger.reimbursement_rate` default changed from `0.5` to `0.8` at `src/superclaude/cli/sprint/models.py:476`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/models.py` and locate line 476 containing `reimbursement_rate: float = 0.5`
2. **[PLANNING]** Confirm this is the `TurnLedger` class attribute, not a local variable or test fixture
3. **[EXECUTION]** Edit `src/superclaude/cli/sprint/models.py:476` to read `reimbursement_rate: float = 0.8`
4. **[VERIFICATION]** Run `grep -n 'reimbursement_rate.*=.*0.5' src/superclaude/cli/sprint/models.py` and confirm zero matches
5. **[VERIFICATION]** Run `grep -n 'reimbursement_rate.*=.*0.8' src/superclaude/cli/sprint/models.py` and confirm line 476 matches
6. **[COMPLETION]** Record evidence in D-0007 artifact

**Acceptance Criteria:**
- File `src/superclaude/cli/sprint/models.py` line 476 reads `reimbursement_rate: float = 0.8`
- No other `reimbursement_rate` assignments in `sprint/models.py` were modified
- SC-001 enforcement (`0.0 < rate < 1.0`) is satisfied by the new value 0.8
- Evidence recorded in `.dev/releases/current/unified-audit-gating-v2/artifacts/D-0007/evidence.md`

**Validation:**
- Manual check: `grep -n 'reimbursement_rate' src/superclaude/cli/sprint/models.py` shows `0.8` at line 476
- Evidence: grep output captured in evidence artifact

**Dependencies:** None
**Rollback:** Revert line 476 to `reimbursement_rate: float = 0.5`
**Notes:** Critical path override applied due to models/ path. FR-007 traceability. This change directly addresses the budget exhaustion problem described in spec §1.1.

---

### Checkpoint: End of Phase 1

**Purpose:** Gate for Phase 2 — confirm all 7 Tier 1 Python source defaults are correctly applied before proceeding to shell/CLI alignment.
**Checkpoint Report Path:** `.dev/releases/current/unified-audit-gating-v2/checkpoints/CP-P01-END.md`

**Verification:**
- All 7 deliverables (D-0001 through D-0007) have evidence artifacts confirming the edit
- `grep -rn 'max_turns.*=.*50' src/superclaude/cli/` returns zero matches in default declarations (only explicit fixtures in tests/)
- `grep -rn 'reimbursement_rate.*=.*0.5' src/superclaude/cli/` returns zero matches in default declarations

**Exit Criteria:**
- All 6 `max_turns` locations read `100` and the 1 `reimbursement_rate` location reads `0.8`
- No syntax errors in any modified file
- Phase 2 is unblocked (M1 complete → M2 can proceed)
