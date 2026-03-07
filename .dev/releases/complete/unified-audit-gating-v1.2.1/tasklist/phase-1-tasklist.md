# Phase 1 -- Foundation — TurnLedger & Detection

Implement the TurnLedger economic model and error_max_turns detection to immediately detect silent incompletion. This milestone delivers detection value without requiring per-task subprocess migration, enabling the runner to identify budget-exhausted subprocesses that exit with code 0.

### T01.01 -- Implement TurnLedger Dataclass in sprint/models.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | The TurnLedger dataclass provides the budget arithmetic foundation for all subsequent subprocess budget tracking and reimbursement logic. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | model (models.py), data (budget state) |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0001/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0001/evidence.md

**Deliverables:**
- TurnLedger dataclass (~50 lines) in `src/superclaude/cli/sprint/models.py` with fields: initial_budget, consumed, reimbursed, reimbursement_rate, minimum_allocation, minimum_remediation_budget; methods: debit(), credit(), can_launch(), can_remediate(), available()

**Steps:**
1. **[PLANNING]** Read existing `src/superclaude/cli/sprint/models.py` to identify dataclass conventions and import patterns
2. **[PLANNING]** Verify no existing TurnLedger or budget-related dataclass exists to avoid duplication
3. **[EXECUTION]** Implement TurnLedger dataclass with all specified fields and arithmetic methods
4. **[EXECUTION]** Implement budget monotonicity invariant: consumed can only increase, available() = initial_budget - consumed + reimbursed
5. **[EXECUTION]** Implement can_launch() returning False when available() < minimum_allocation
6. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k turnledger -v` to validate arithmetic correctness
7. **[COMPLETION]** Record deliverable evidence in D-0001/evidence.md

**Acceptance Criteria:**
- `uv run pytest tests/sprint/test_models.py -k TurnLedger` exits 0 with all TurnLedger arithmetic tests passing (debit, credit, can_launch, can_remediate, available)
- Budget monotonicity invariant holds: consumed never decreases, available() = initial_budget - consumed + reimbursed
- can_launch() returns False when available() < minimum_allocation; can_remediate() returns False when available() < minimum_remediation_budget
- TurnLedger dataclass added to sprint/models.py following existing dataclass conventions in the file

**Validation:**
- `uv run pytest tests/sprint/test_models.py -k TurnLedger -v`
- Evidence: linkable artifact produced at D-0001/evidence.md

**Dependencies:** None
**Rollback:** Revert TurnLedger addition from sprint/models.py
**Notes:** STRICT tier due to "model" keyword (models.py target file) and budget state management.

---

### T01.02 -- Add error_max_turns NDJSON Detection in sprint/monitor.py

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | Detecting error_max_turns in subprocess NDJSON output is the first line of defense against silent incompletion — without detection, exhausted subprocesses are reported as successes. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0002/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0002/evidence.md

**Deliverables:**
- Regex-based detection (~15 lines) in `src/superclaude/cli/sprint/monitor.py` that scans the last NDJSON line for `"subtype":"error_max_turns"`

**Steps:**
1. **[PLANNING]** Read `src/superclaude/cli/sprint/monitor.py` to identify where NDJSON output is parsed
2. **[PLANNING]** Review existing NDJSON parsing patterns to align detection approach
3. **[EXECUTION]** Implement regex detection on last NDJSON line for `"subtype":"error_max_turns"` pattern
4. **[EXECUTION]** Return detection result as a boolean flag consumable by the status reclassification logic (T01.03)
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k error_max_turns -v` against synthetic NDJSON payloads
6. **[COMPLETION]** Record deliverable evidence in D-0002/evidence.md

**Acceptance Criteria:**
- Detection function in `sprint/monitor.py` returns True when last NDJSON line contains `"subtype":"error_max_turns"`
- No false positives when tested against normal NDJSON output (success, failure, other error subtypes)
- Detection handles edge cases: empty output, truncated NDJSON, multiple NDJSON lines
- Function signature and return type documented with inline docstring

**Validation:**
- `uv run pytest tests/sprint/ -k error_max_turns -v`
- Evidence: linkable artifact produced at D-0002/evidence.md

**Dependencies:** None
**Rollback:** Revert detection function from sprint/monitor.py

---

### T01.03 -- Implement INCOMPLETE Reclassification on error_max_turns

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Without reclassification, PASS_NO_REPORT status combined with error_max_turns allows budget-exhausted subprocesses to be silently counted as successes. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0003/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0003/evidence.md

**Deliverables:**
- Status reclassification logic (~10 lines) that changes PASS_NO_REPORT to INCOMPLETE when error_max_turns is detected, triggering HALT instead of silent continuation

**Steps:**
1. **[PLANNING]** Identify where subprocess result status is determined in the sprint runner
2. **[PLANNING]** Verify T01.02 detection function is available for integration
3. **[EXECUTION]** Add conditional: if status == PASS_NO_REPORT and error_max_turns_detected → set status = INCOMPLETE
4. **[EXECUTION]** Wire INCOMPLETE status to trigger HALT flow instead of proceeding to next task
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k reclassification -v` to validate status transitions
6. **[COMPLETION]** Record deliverable evidence in D-0003/evidence.md

**Acceptance Criteria:**
- When error_max_turns is detected and status is PASS_NO_REPORT, status is reclassified to INCOMPLETE
- INCOMPLETE status triggers HALT with descriptive message indicating budget exhaustion
- Normal PASS and FAIL statuses are not affected by the reclassification logic
- Status transition logic resides in the same module as existing status handling

**Validation:**
- `uv run pytest tests/sprint/ -k reclassification -v`
- Evidence: linkable artifact produced at D-0003/evidence.md

**Dependencies:** T01.02 (error_max_turns detection must exist)
**Rollback:** Revert reclassification conditional

---

### T01.04 -- Add Pre-Launch Budget Guard via can_launch()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | Without a pre-launch guard, the runner may spawn a subprocess that immediately exhausts its budget, wasting turns and producing no useful work. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STRICT |
| Confidence | [██████████] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0004/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0004/evidence.md

**Deliverables:**
- Budget check guard (~10 lines) before subprocess launch: call `ledger.can_launch()` and HALT with budget-specific message if False

**Steps:**
1. **[PLANNING]** Identify the subprocess launch point in the sprint executor
2. **[PLANNING]** Verify TurnLedger instance is accessible at the launch callsite
3. **[EXECUTION]** Add `if not ledger.can_launch(): halt_with_budget_message()` guard before subprocess spawn
4. **[EXECUTION]** Implement budget-specific HALT message including remaining budget and minimum_allocation values
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k budget_guard -v` to validate guard behavior
6. **[COMPLETION]** Record deliverable evidence in D-0004/evidence.md

**Acceptance Criteria:**
- Subprocess is not launched when `ledger.can_launch()` returns False
- HALT message includes remaining budget value and minimum_allocation threshold
- Normal launch proceeds unimpeded when budget is sufficient
- Guard is positioned immediately before the subprocess spawn call

**Validation:**
- `uv run pytest tests/sprint/ -k budget_guard -v`
- Evidence: linkable artifact produced at D-0004/evidence.md

**Dependencies:** T01.01 (TurnLedger with can_launch() must exist)
**Rollback:** Remove can_launch() guard from subprocess launch path

---

### Checkpoint: End of Phase 1

**Purpose:** Validate that TurnLedger economics and error_max_turns detection are operational before proceeding to per-task subprocess architecture.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P01-END.md

**Verification:**
- TurnLedger dataclass arithmetic is correct (debit, credit, can_launch, can_remediate, available)
- error_max_turns detection fires on synthetic NDJSON with zero false positives
- Budget guard prevents launch when budget insufficient

**Exit Criteria:**
- `uv run pytest tests/sprint/ -k "TurnLedger or error_max_turns or budget_guard" -v` exits 0
- All 4 deliverables (D-0001 through D-0004) have evidence artifacts
- No regressions in existing sprint test suite: `uv run pytest tests/sprint/ -v` exits 0
