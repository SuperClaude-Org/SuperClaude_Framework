# Phase 7 -- Remediation, Conflict & Diagnostics

Implement the complete failure recovery pipeline: unified retry + remediation model, conflict review for file-level overlap detection, and diagnostic chain for intelligent failure analysis. This is the most complex phase with 7 deliverables.

### T07.01 -- Implement TrailingGatePolicy Protocol Definition

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | TrailingGatePolicy defines the consumer-owned hooks that the sprint runner implements to build remediation steps and detect file changes, decoupling gate infrastructure from sprint-specific logic. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (protocol contract) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0027/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0027/evidence.md

**Deliverables:**
- TrailingGatePolicy protocol (Python Protocol class) with methods: `build_remediation_step(gate_result) -> Step` and `files_changed(step_result) -> set[Path]`; sprint consumer provides concrete implementation

**Steps:**
1. **[PLANNING]** Read existing protocol patterns in the pipeline module for interface conventions
2. **[PLANNING]** Define protocol method signatures: build_remediation_step() and files_changed()
3. **[EXECUTION]** Implement TrailingGatePolicy as a Python Protocol class with the two required methods
4. **[EXECUTION]** Implement concrete sprint consumer that satisfies the protocol contract
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k trailing_gate_policy -v` verifying protocol compliance
6. **[COMPLETION]** Record deliverable evidence in D-0027/evidence.md

**Acceptance Criteria:**
- TrailingGatePolicy is a Python Protocol class with `build_remediation_step()` and `files_changed()` methods
- Sprint consumer provides concrete implementation satisfying the protocol
- Protocol is type-checkable: mypy/pyright validates consumer against protocol
- `uv run pytest tests/pipeline/ -k trailing_gate_policy` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k trailing_gate_policy -v`
- Evidence: linkable artifact produced at D-0027/evidence.md

**Dependencies:** T05.01 (TrailingGateRunner), T05.03 (DeferredRemediationLog)
**Rollback:** Remove protocol; remediation logic inlined in gate runner

---

### T07.02 -- Implement Remediation Subprocess Prompt Construction

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | Remediation subprocesses must receive focused prompts containing the specific gate failure reason and acceptance criteria to target the exact issue rather than re-executing the entire task. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (prompt construction) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0028/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0028/evidence.md

**Deliverables:**
- Remediation prompt constructor that builds a focused subprocess prompt from: gate failure reason, original acceptance criteria, file paths involved, and remediation-specific instructions

**Steps:**
1. **[PLANNING]** Define remediation prompt template: failure context, acceptance criteria, target files, instructions
2. **[PLANNING]** Identify inputs from TrailingGateResult and original Step definition
3. **[EXECUTION]** Implement `build_remediation_prompt()` that assembles focused prompt from gate failure data
4. **[EXECUTION]** Include original acceptance criteria so remediation can verify its own fix
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k remediation_prompt -v` with varied failure scenarios
6. **[COMPLETION]** Record deliverable evidence in D-0028/evidence.md

**Acceptance Criteria:**
- Remediation prompt includes: gate failure reason, original acceptance criteria, file paths from gate result
- Prompt is scoped to the specific failure (not a re-execution of the full task)
- Prompt template produces deterministic output for identical inputs
- `uv run pytest tests/pipeline/ -k remediation_prompt` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k remediation_prompt -v`
- Evidence: linkable artifact produced at D-0028/evidence.md

**Dependencies:** T07.01 (TrailingGatePolicy provides build_remediation_step)
**Rollback:** Remove prompt constructor; remediation uses generic re-run prompt

---

### T07.03 -- Implement Remediation Retry with TurnLedger Integration

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | Remediation retry economics must be correct: retry once on failure with budget from TurnLedger, drain both attempts' turns on persistent failure to prevent infinite retry loops. |
| Effort | M |
| Risk | High |
| Risk Drivers | data (budget economics), breaking (retry semantics), system-wide (retry state machine) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0029/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0029/evidence.md

**Deliverables:**
- Remediation retry logic (~60 lines): attempt remediation once; on persistent failure, both attempts' turns lost from TurnLedger (no reimbursement for failed remediation)

**Steps:**
1. **[PLANNING]** Define retry state machine: PENDING → ATTEMPT_1 → (pass → DONE | fail → ATTEMPT_2) → (pass → DONE | fail → PERSISTENT_FAILURE)
2. **[PLANNING]** Define budget economics: both attempts debited from ledger; no reimbursement on persistent failure
3. **[EXECUTION]** Implement retry logic with TurnLedger debit for each attempt
4. **[EXECUTION]** Implement persistent failure handling: both attempts' turns marked as consumed (lost from budget)
5. **[EXECUTION]** Add `ledger.can_remediate()` pre-check before each attempt (Gap 1 mitigation)
6. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k remediation_retry -v` covering all state transitions
7. **[COMPLETION]** Record deliverable evidence in D-0029/evidence.md

**Acceptance Criteria:**
- Retry state machine covers: pass-first-attempt, fail-then-pass, persistent-failure transitions
- Budget economics verified: both attempts' turns debited on persistent failure, single attempt on first-pass success
- `ledger.can_remediate()` checked before each attempt (no remediation spawn when budget insufficient)
- `uv run pytest tests/pipeline/ -k remediation_retry` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k remediation_retry -v`
- Evidence: linkable artifact produced at D-0029/evidence.md

**Dependencies:** T01.01 (TurnLedger), T07.02 (remediation prompt), T02.06 (can_remediate)
**Rollback:** Remove retry; gate failures trigger immediate HALT

---

### T07.04 -- Implement conflict_review.py for File-Level Overlap Detection

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | Remediation may modify files that intervening tasks have also changed, creating conflicts. Conflict review detects file-level overlaps and triggers re-gate to prevent silent corruption. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (file overlap detection) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0030/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0030/evidence.md

**Deliverables:**
- `conflict_review.py` (~80 lines) in `src/superclaude/cli/pipeline/` with function that detects file-level overlap between remediation output and intervening task work; triggers re-gate on overlap, passthrough on no overlap

**Steps:**
1. **[PLANNING]** Define overlap detection: compare files_changed() from remediation with files_changed() from intervening tasks
2. **[PLANNING]** Define re-gate trigger: when overlap set is non-empty, re-evaluate gate on merged output
3. **[EXECUTION]** Implement `detect_file_overlap(remediation_files, intervening_files) -> set[Path]`
4. **[EXECUTION]** Implement re-gate trigger: if overlap detected, submit merged output to TrailingGateRunner
5. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k conflict_review -v` with overlap and no-overlap scenarios
6. **[COMPLETION]** Record deliverable evidence in D-0030/evidence.md

**Acceptance Criteria:**
- Overlapping files detected when remediation and intervening tasks modify the same file(s)
- Re-gate triggered when overlap found; passthrough when no overlap
- Empty remediation or empty intervening work handled gracefully (no false positives)
- `uv run pytest tests/pipeline/ -k conflict_review` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k conflict_review -v`
- Evidence: linkable artifact produced at D-0030/evidence.md

**Dependencies:** T07.01 (TrailingGatePolicy.files_changed()), T05.01 (TrailingGateRunner for re-gate)
**Rollback:** Remove conflict review; remediation output accepted without overlap check

---

### Checkpoint: Phase 7 / Tasks T07.01-T07.04

**Purpose:** Verify remediation core (policy, prompt, retry, conflict) before adding diagnostic chain and resume semantics.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P07-T01-T04.md

**Verification:**
- TrailingGatePolicy protocol implemented with concrete sprint consumer
- Remediation retry state machine covers all transitions with correct budget economics
- Conflict review detects overlaps and triggers re-gate

**Exit Criteria:**
- `uv run pytest tests/pipeline/ -k "trailing_gate_policy or remediation_prompt or remediation_retry or conflict_review" -v` exits 0
- Retry budget economics verified: persistent failure drains both attempts' turns
- No regressions in existing pipeline tests

---

### T07.05 -- Implement diagnostic_chain.py for Failure Analysis

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040 |
| Why | When remediation persistently fails, the diagnostic chain provides intelligent failure analysis (troubleshoot → root causes → solutions → summary) to help the user understand and resolve the issue. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | system-wide (multi-step chain) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0031/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0031/evidence.md

**Deliverables:**
- `diagnostic_chain.py` (~100 lines) in `src/superclaude/cli/pipeline/` implementing: troubleshoot → adversarial(root causes) → adversarial(solutions) → summary; runner-side execution (not TurnLedger turns); best-effort with graceful degradation

**Steps:**
1. **[PLANNING]** Define chain stages: troubleshoot, root cause adversarial, solution adversarial, summary
2. **[PLANNING]** Design graceful degradation: chain errors caught per stage, partial results returned
3. **[EXECUTION]** Implement troubleshoot stage: analyze gate failure and remediation output
4. **[EXECUTION]** Implement adversarial stages: generate root cause hypotheses, then solution proposals
5. **[EXECUTION]** Implement summary stage: compile chain output into actionable diagnostic report
6. **[EXECUTION]** Add graceful degradation: each stage catches exceptions, returns partial results
7. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k diagnostic_chain -v`
8. **[COMPLETION]** Record deliverable evidence in D-0031/evidence.md

**Acceptance Criteria:**
- Diagnostic chain fires on persistent remediation failure (after retry exhaustion)
- Chain is runner-side execution (no TurnLedger turns consumed — Gap 2 compliance)
- Each stage degrades gracefully: stage errors caught, partial results available to subsequent stages
- `uv run pytest tests/pipeline/ -k diagnostic_chain` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k diagnostic_chain -v`
- Evidence: linkable artifact produced at D-0031/evidence.md

**Dependencies:** T07.03 (persistent failure triggers chain)
**Rollback:** Remove diagnostic chain; persistent failure produces standard HALT output only
**Notes:** Budget-specific halt skips diagnostic chain per Gap 2 (R-011).

---

### T07.06 -- Implement Resume Semantics with Actionable Resume Command

| Field | Value |
|---|---|
| Roadmap Item IDs | R-041 |
| Why | When a sprint HALTs, the user needs an actionable resume command that specifies exactly where to resume, what tasks remain, and what budget to allocate — not just a generic "run again" message. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (state serialization for resume) |
| Tier | STRICT |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0032/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0032/evidence.md

**Deliverables:**
- Resume semantics (~40 lines): HALT output includes actionable resume command with task ID, remaining tasks list, diagnostic output reference, and budget suggestion

**Steps:**
1. **[PLANNING]** Define resume command format: `superclaude sprint run --resume <task-id> --budget <suggested>`
2. **[PLANNING]** Identify HALT output insertion point in sprint runner
3. **[EXECUTION]** Implement resume command generation: compute next task ID, list remaining tasks, suggest budget
4. **[EXECUTION]** Include diagnostic output path reference if diagnostic chain produced results
5. **[VERIFICATION]** Run `uv run pytest tests/sprint/ -k resume_semantics -v` verifying command correctness
6. **[COMPLETION]** Record deliverable evidence in D-0032/evidence.md

**Acceptance Criteria:**
- HALT output includes: resume command with correct task ID, remaining task count, and budget suggestion
- Resume task ID matches the first uncompleted task in the sequence
- Remaining tasks listed in execution order
- `uv run pytest tests/sprint/ -k resume_semantics` exits 0

**Validation:**
- `uv run pytest tests/sprint/ -k resume_semantics -v`
- Evidence: linkable artifact produced at D-0032/evidence.md

**Dependencies:** T02.02 (task sequencing), T07.05 (diagnostic chain output)
**Rollback:** Remove resume semantics; HALT produces generic message

---

### T07.07 -- Implement Full-Flow Integration Test (4 Scenarios)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042 |
| Why | A full-flow integration test exercising all 4 scenarios (pass, fail-remediate-pass, fail-halt, low-budget-halt) validates the compound interaction between budget, gates, remediation, and context injection. |
| Effort | L |
| Risk | High |
| Risk Drivers | end-to-end (compound flow), system-wide (multi-component integration) |
| Tier | STANDARD |
| Confidence | [████████──] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0033/spec.md
- .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/artifacts/D-0033/evidence.md

**Deliverables:**
- Full-flow integration test (~200 lines) exercising 4 scenarios: (1) task passes gate, (2) task fails gate → remediation succeeds, (3) task fails gate → remediation fails → HALT, (4) low budget → skip remediation → HALT

**Steps:**
1. **[PLANNING]** Design 4 test scenarios with specific inputs, expected state transitions, and expected outputs
2. **[PLANNING]** Identify mock boundaries: mock subprocess execution, use real orchestration/budget/gate logic
3. **[EXECUTION]** Implement scenario 1: task passes gate → continue to next task
4. **[EXECUTION]** Implement scenario 2: task fails gate → remediation spawned → remediation passes → continue
5. **[EXECUTION]** Implement scenario 3: task fails gate → remediation fails → retry fails → HALT with diagnostic
6. **[EXECUTION]** Implement scenario 4: low budget → can_remediate() false → HALT with budget message
7. **[VERIFICATION]** Run `uv run pytest tests/pipeline/ -k full_flow -v` verifying all 4 scenarios
8. **[COMPLETION]** Record test output in D-0033/evidence.md

**Acceptance Criteria:**
- All 4 scenarios pass: pass, fail-remediate-pass, fail-halt, low-budget-halt
- Each scenario exercises the compound flow: budget + gate + remediation + context injection
- Budget accounting correct across all scenarios (TurnLedger state verified at each step)
- `uv run pytest tests/pipeline/ -k full_flow` exits 0

**Validation:**
- `uv run pytest tests/pipeline/ -k full_flow -v`
- Evidence: test output artifact at D-0033/evidence.md

**Dependencies:** T07.03 (retry), T07.04 (conflict review), T07.05 (diagnostic chain), T04.01 (context injection)
**Rollback:** Remove full-flow integration test
**Notes:** Gap 6 deliverable per Crispin: full-flow integration test is mandatory, not deferred.

---

### Checkpoint: End of Phase 7

**Purpose:** Confirm complete remediation pipeline (policy, retry, conflict, diagnostics, resume) and full-flow integration before TUI and hardening.
**Checkpoint Report Path:** .dev/releases/current/unified-audit-gating-v1.2.1/tasklist/checkpoints/CP-P07-END.md

**Verification:**
- TrailingGatePolicy protocol with concrete sprint consumer functional
- Remediation retry, conflict review, and diagnostic chain all operational
- Full-flow integration test passes all 4 scenarios

**Exit Criteria:**
- `uv run pytest tests/pipeline/ -v` exits 0 (full pipeline test suite)
- `uv run pytest tests/sprint/ -k resume_semantics -v` exits 0
- All 7 deliverables (D-0027 through D-0033) have evidence artifacts
- Success criterion SC-006 (full-flow integration test 4 scenarios) validated
