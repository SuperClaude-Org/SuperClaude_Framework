# Phase 4 -- Remediation Orchestrator

Highest-complexity phase: agent orchestration with transactional rollback. Build in strict dependency order: prompt builder → grouping → snapshots → agent spawning → parallel execution → rollback/success → tasklist update → step registration.

---

### T04.01 -- Build Remediation Prompt Builder (remediate_prompts.py)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-020 |
| Why | Pure function producing agent prompts with target file, finding details, and constraints per spec §2.3.4 template. First in implementation sequence — testable in isolation. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0014/spec.md`

**Deliverables:**
- `remediate_prompts.py` module with `build_remediation_prompt(target_file: str, findings: list[Finding]) -> str` producing agent prompt per spec §2.3.4 template

**Steps:**
1. **[PLANNING]** Read spec §2.3.4 agent prompt template verbatim: "You are a remediation specialist..." with Target File, Findings to Fix, Constraints sections
2. **[PLANNING]** Design function signature: `build_remediation_prompt(target_file: str, findings: list[Finding]) -> str`
3. **[EXECUTION]** Implement prompt builder producing exact template structure from spec §2.3.4
4. **[EXECUTION]** Include per-finding blocks: ID, severity, description, location, evidence, fix_guidance
5. **[EXECUTION]** Include constraints section: edit-only target file, apply-only listed fixes, preserve YAML/headings
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_prompts.py` to verify prompt structure
7. **[COMPLETION]** Document prompt template in `D-0014/spec.md`

**Acceptance Criteria:**
- `build_remediation_prompt()` is a pure function (no I/O, no subprocess, no side effects per NFR-004)
- Output matches spec §2.3.4 template structure: header, target file, findings section, constraints section
- Each finding block contains all 6 detail fields (ID, severity, description, location, evidence, fix_guidance)
- Constraints section enforces edit-only-target-file and preserve-structure rules

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_prompts.py` exits 0
- Evidence: linkable artifact produced at `D-0014/spec.md`

**Dependencies:** T02.01 (Finding dataclass)
**Rollback:** N/A (new module, no existing code modified)

---

### T04.02 -- Implement File-Level Grouping and Cross-File Finding Handler

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018, R-019 |
| Why | Batch actionable findings by primary target file to eliminate concurrent same-file edits. Cross-file findings included in both agents' prompts with scoped guidance per spec §2.3.4. |
| Effort | S |
| Risk | Low |
| Risk Drivers | cross-cutting |
| Tier | STRICT |
| Confidence | `[███████---]` 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0015/spec.md`

**Deliverables:**
- `group_findings_by_file(findings: list[Finding]) -> dict[str, list[Finding]]` grouping function
- Cross-file finding handler: produces scoped prompt fragments with "Fix Guidance (YOUR FILE):" and "Note:" fields per spec §2.3.4

**Steps:**
1. **[PLANNING]** Design grouping: primary target = first entry in `files_affected`, group all findings by primary target
2. **[PLANNING]** Design cross-file handling: findings with len(files_affected) > 1 appear in multiple groups with scoped guidance
3. **[EXECUTION]** Implement `group_findings_by_file()` as pure function
4. **[EXECUTION]** Implement cross-file prompt scoping: per-agent prompt fragment includes "Fix Guidance (YOUR FILE):" for local scope and "Note: The <other_file> side is handled by a separate agent."
5. **[EXECUTION]** Verify no finding is orphaned (every finding appears in at least one group)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_prompts.py -k "grouping or cross_file"` to verify
7. **[COMPLETION]** Document grouping and cross-file logic in `D-0015/spec.md`

**Acceptance Criteria:**
- `group_findings_by_file()` produces `dict[str, list[Finding]]` with no concurrent same-file groups
- Cross-file findings appear in all relevant file groups with scoped guidance
- Prompt fragments include "Fix Guidance (YOUR FILE):" and "Note:" fields per spec §2.3.4
- No findings orphaned — every actionable finding appears in at least one group

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_prompts.py -k "grouping or cross_file"` exits 0
- Evidence: linkable artifact produced at `D-0015/spec.md`

**Dependencies:** T02.01 (Finding dataclass), T04.01 (prompt builder)
**Rollback:** N/A (pure functions, new module)
**Notes:** Tier STRICT due to multi-file scope and cross-cutting concerns.

---

### T04.03 -- Implement Pre-Remediate File Snapshots

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | Before spawning remediation agents, snapshot all target files as file.pre-remediate for rollback capability per spec §2.3.8. |
| Effort | XS |
| Risk | Medium |
| Risk Drivers | rollback |
| Tier | STANDARD |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0016/spec.md`

**Deliverables:**
- Snapshot function: `create_snapshots(target_files: list[str]) -> list[str]` copying each file to `<file>.pre-remediate`

**Steps:**
1. **[PLANNING]** Define snapshot naming convention: `<filename>.pre-remediate`
2. **[PLANNING]** Identify target files from file groups (T04.02 output)
3. **[EXECUTION]** Implement `create_snapshots()` using atomic copy (read + tmp + os.replace per NFR-005)
4. **[EXECUTION]** Return list of snapshot paths for rollback reference
5. **[EXECUTION]** Verify snapshot creation before any agent spawning begins
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "snapshot"` to verify snapshot creation and content integrity
7. **[COMPLETION]** Document snapshot mechanism in `D-0016/spec.md`

**Acceptance Criteria:**
- `create_snapshots()` creates `.pre-remediate` copies for all target files before agent spawning
- Snapshots use atomic write pattern (tmp + os.replace per NFR-005)
- Snapshot content is byte-identical to original file
- Function returns snapshot paths for rollback reference

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "snapshot"` exits 0
- Evidence: linkable artifact produced at `D-0016/spec.md`

**Dependencies:** T04.02 (file groups identify target files)
**Rollback:** Delete `.pre-remediate` files

---

### T04.04 -- Implement File Allowlist Enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | Remediation agents may ONLY edit roadmap.md, extraction.md, test-strategy.md per spec §2.3.5. Findings referencing non-allowlist files must be SKIPPED with WARNING. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[███████---]` 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0017/spec.md`

**Deliverables:**
- Allowlist constant: `EDITABLE_FILES = {"roadmap.md", "extraction.md", "test-strategy.md"}`
- Enforcement function: `enforce_allowlist(findings: list[Finding]) -> tuple[list[Finding], list[Finding]]` returning (allowed, rejected)

**Steps:**
1. **[PLANNING]** Define allowlist constant per spec §2.3.5
2. **[PLANNING]** Design enforcement: check `files_affected` against allowlist
3. **[EXECUTION]** Implement `enforce_allowlist()` — findings with all files in allowlist → allowed; findings with any file outside allowlist → SKIPPED with WARNING per OQ-004
4. **[EXECUTION]** Log WARNING for rejected findings per roadmap OQ-004 default
5. **[EXECUTION]** Include rejected findings in tasklist as SKIPPED with reason
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "allowlist"` to verify enforcement
7. **[COMPLETION]** Document allowlist rules in `D-0017/spec.md`

**Acceptance Criteria:**
- `EDITABLE_FILES` contains exactly: roadmap.md, extraction.md, test-strategy.md
- Findings referencing only allowlisted files pass through
- Findings referencing any non-allowlisted file are SKIPPED with WARNING log
- Rejected findings included in tasklist as SKIPPED with reason

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "allowlist"` exits 0
- Evidence: linkable artifact produced at `D-0017/spec.md`

**Dependencies:** T02.01 (Finding dataclass)
**Rollback:** N/A (enforcement function, isolated)

---

### Checkpoint: Phase 4 / Tasks T04.01-T04.04

**Purpose:** Verify pure functions (prompt builder, grouping, allowlist) and snapshot mechanism are ready before agent orchestration begins.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P04-T01-T04.md`
**Verification:**
- Prompt builder produces spec-compliant agent prompts with cross-file scoping
- File grouping eliminates concurrent same-file edits with no orphaned findings
- Snapshot mechanism creates byte-identical copies using atomic writes
**Exit Criteria:**
- All pure functions verified: no I/O in prompt builder, grouping, allowlist enforcement
- Snapshot creation and integrity tests pass
- Allowlist enforcement correctly rejects non-allowlisted files

---

### T04.05 -- Implement Parallel Agent Execution with ClaudeProcess

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023, R-029, R-030 |
| Why | Spawn one ClaudeProcess per file group in parallel via threading. Agents receive only prompt + --file inputs (no --continue, --session, --resume per NFR-003). Model inherited from pipeline config (NFR-010). |
| Effort | M |
| Risk | Low |
| Risk Drivers | None |
| Tier | STRICT |
| Confidence | `[███████---]` 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0018/spec.md`

**Deliverables:**
- Parallel execution coordinator in `remediate_executor.py` using `ClaudeProcess` (not `execute_pipeline()` per FR-019) with threading-based parallelism across file groups

**Steps:**
1. **[PLANNING]** Review `validate_executor.py` ClaudeProcess usage pattern from T01.01 notes
2. **[PLANNING]** Design execution coordinator: one thread per file group, ClaudeProcess per thread
3. **[EXECUTION]** Implement agent spawning: `ClaudeProcess(prompt=build_remediation_prompt(...), files=[target_file])`
4. **[EXECUTION]** Enforce context isolation: no `--continue`, `--session`, `--resume` flags (NFR-003)
5. **[EXECUTION]** Inherit model from parent pipeline config (NFR-010)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "parallel or execution"` to verify parallel execution
7. **[COMPLETION]** Document execution coordinator in `D-0018/spec.md`

**Acceptance Criteria:**
- Agents spawned via `ClaudeProcess` matching `validate_executor.py` pattern (FR-012, FR-019)
- Parallel execution: agents touching different files run concurrently via threading
- Context isolation: agents receive only prompt + `--file`, no session flags (NFR-003)
- Model inherited from parent pipeline config (NFR-010)

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "parallel or execution"` exits 0
- Evidence: linkable artifact produced at `D-0018/spec.md`

**Dependencies:** T04.01 (prompt builder), T04.02 (file groups), T04.03 (snapshots created first)
**Rollback:** Restore from `.pre-remediate` snapshots

---

### T04.06 -- Implement Timeout Enforcement and Retry Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | Each remediation agent has a 300-second timeout with a single retry on failure per NFR-001 and NFR-002. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0019/spec.md`

**Deliverables:**
- Timeout wrapper: 300s per agent with 1 retry on non-zero exit or timeout

**Steps:**
1. **[PLANNING]** Review existing timeout patterns in pipeline infrastructure
2. **[PLANNING]** Define retry semantics: restore from snapshot before retry
3. **[EXECUTION]** Implement 300s timeout on ClaudeProcess execution
4. **[EXECUTION]** Implement single retry: on failure, restore snapshot, re-run agent once
5. **[EXECUTION]** On second failure: mark as FAILED, trigger failure handler (T04.07)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "timeout or retry"` to verify
7. **[COMPLETION]** Document timeout/retry behavior in `D-0019/spec.md`

**Acceptance Criteria:**
- 300-second timeout enforced per agent execution
- Single retry on failure: snapshot restored before retry attempt
- Second failure triggers FAILED status without further retries
- Timeout and retry behavior consistent with pipeline norms

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "timeout or retry"` exits 0
- Evidence: linkable artifact produced at `D-0019/spec.md`

**Dependencies:** T04.05 (agent execution), T04.03 (snapshots for retry restoration)
**Rollback:** Restore from `.pre-remediate` snapshots

---

### T04.07 -- Implement Failure Handling with Full Rollback

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | If ANY remediation agent exits non-zero or times out (after retry): halt remaining agents, rollback ALL files from .pre-remediate snapshots, mark FAILED per spec §2.3.8. |
| Effort | S |
| Risk | High |
| Risk Drivers | rollback, breaking |
| Tier | STRICT |
| Confidence | `[█████████-]` 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0020/spec.md`

**Deliverables:**
- Failure handler implementing spec §2.3.8: halt agents, rollback all files, mark all findings for failed agent as FAILED, mark cross-file findings involving failed file as FAILED, set remediate step to FAIL

**Steps:**
1. **[PLANNING]** Map spec §2.3.8 failure semantics: 5-step procedure (halt, rollback, mark failed agent findings, mark cross-file findings, set step FAIL)
2. **[PLANNING]** Design rollback: `os.replace()` from `.pre-remediate` snapshots for atomicity
3. **[EXECUTION]** Implement halt: cancel/terminate remaining running agents
4. **[EXECUTION]** Implement rollback: restore ALL target files from `.pre-remediate` snapshots using `os.replace()`
5. **[EXECUTION]** Implement failure marking: mark all findings for failed agent as FAILED, mark cross-file findings as FAILED even if other agent succeeded
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "failure or rollback"` to verify rollback after first-agent-success + second-agent-failure
7. **[COMPLETION]** Document failure handling in `D-0020/spec.md`

**Acceptance Criteria:**
- Agent failure triggers rollback of ALL target files (not just the failed agent's file) per spec §2.3.8 rationale
- Rollback uses `os.replace()` for atomicity (NFR-005)
- Cross-file findings involving the failed file are marked FAILED even if the other agent succeeded
- Remediate step status set to FAIL, pipeline halts
- File contents after rollback match `.pre-remediate` snapshots byte-for-byte

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "failure or rollback"` exits 0 — specifically testing first-agent-success + second-agent-timeout scenario
- Evidence: linkable artifact produced at `D-0020/spec.md`

**Dependencies:** T04.05 (agent execution), T04.03 (snapshots)
**Rollback:** Snapshots are the rollback mechanism itself
**Notes:** Tier STRICT + Risk High due to rollback and breaking-change keywords. This is the highest-value test investment per roadmap risk reduction strategy.

---

### T04.08 -- Implement Success Handling with Snapshot Cleanup

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026 |
| Why | On full success (all agents exit 0): delete .pre-remediate snapshots and mark all agent-targeted findings as FIXED per spec §2.3.8. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0021/spec.md`

**Deliverables:**
- Success handler: delete `.pre-remediate` snapshots, set all agent-targeted findings to FIXED

**Steps:**
1. **[PLANNING]** Define success condition: all agents exited 0 (no timeouts, no retries exhausted)
2. **[PLANNING]** List cleanup actions: delete snapshots, update finding statuses
3. **[EXECUTION]** Implement snapshot deletion: remove all `.pre-remediate` files
4. **[EXECUTION]** Update finding statuses: set all agent-targeted findings to FIXED
5. **[EXECUTION]** Verify no orphaned snapshots remain
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "success"` to verify cleanup
7. **[COMPLETION]** Document success handling in `D-0021/spec.md`

**Acceptance Criteria:**
- All `.pre-remediate` snapshots deleted after full success
- All agent-targeted findings set to FIXED status
- SKIPPED findings (those rejected by allowlist enforcement in T04.04) remain in SKIPPED status and are not modified by the success handler
- No orphaned snapshot files remain after cleanup
- Success handler only runs when ALL agents succeed (not partial)

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "success"` exits 0
- Evidence: linkable artifact produced at `D-0021/spec.md`

**Dependencies:** T04.05 (agent execution), T04.03 (snapshots)
**Rollback:** N/A (success path)

---

### T04.09 -- Implement Tasklist Outcome Writer (Two-Write Model)

| Field | Value |
|---|---|
| Roadmap Item IDs | R-027 |
| Why | After agent execution, update the existing remediation-tasklist.md with per-finding outcomes (FIXED/FAILED/SKIPPED). This is the second write of the two-write model (first write in T03.04). |
| Effort | XS |
| Risk | Low |
| Risk Drivers | None |
| Tier | STANDARD |
| Confidence | `[████████--]` 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0022/spec.md`

**Deliverables:**
- Tasklist updater: reads existing `remediation-tasklist.md`, updates finding statuses and checkboxes, writes back using atomic write

**Steps:**
1. **[PLANNING]** Define update format: `- [x] F-XX | file | FIXED — description` for success, `- [ ] F-XX | file | FAILED — description` for failure
2. **[PLANNING]** Design atomic update: read → modify → tmp write → os.replace()
3. **[EXECUTION]** Implement `update_remediation_tasklist(tasklist_path: str, findings: list[Finding]) -> None`
4. **[EXECUTION]** Update YAML frontmatter counts based on final statuses
5. **[EXECUTION]** Use atomic write (tmp + os.replace) per NFR-005
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "tasklist_update"` to verify round-trip (parse → emit → re-parse)
7. **[COMPLETION]** Document two-write model in `D-0022/spec.md`

**Acceptance Criteria:**
- Updated tasklist passes `REMEDIATE_GATE` validation with outcome statuses
- YAML frontmatter counts (actionable, skipped) reflect final finding states
- Write uses atomic pattern (tmp + os.replace per NFR-005)
- Round-trip: parse → update → re-parse produces consistent Finding objects (SC-007)

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "tasklist_update"` exits 0
- Evidence: linkable artifact produced at `D-0022/spec.md`

**Dependencies:** T03.04 (first write creates the tasklist), T04.07/T04.08 (provide final finding statuses)
**Rollback:** Restore from pre-update backup. If atomic write (tmp + os.replace per NFR-005) is used, failure leaves the original intact — no separate backup file needed. If a pre-write copy is desired, create `remediation-tasklist.md.pre-outcomes` before writing and restore from it on failure.

---

### T04.10 -- Register Remediate Step with REMEDIATE_GATE and YAML Preservation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028, R-031 |
| Why | Register remediate as a single Step to execute_pipeline() while internal orchestration uses ClaudeProcess directly. Ensure agents preserve YAML frontmatter and heading hierarchy. This task modifies executor.py (shared pipeline infrastructure) — unit tests cover correctness but E2E validation in T07.01 is required before marking complete. |
| Effort | S |
| Risk | Low |
| Risk Drivers | pipeline |
| Tier | STANDARD |
| Confidence | `[████████--]` 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- `.dev/releases/current/v2.22-RoadmapRemediate/artifacts/D-0023/spec.md`

**Deliverables:**
- Remediate step registration in `_build_steps()` with `REMEDIATE_GATE` and output_file pointing to `remediation-tasklist.md`
- YAML/heading preservation constraint in agent prompt templates (NFR-013)

**Steps:**
1. **[PLANNING]** Review `_build_steps()` in `executor.py` to understand step registration pattern
2. **[PLANNING]** Design dual-nature: outer step presents to pipeline, inner uses ClaudeProcess
3. **[EXECUTION]** Add remediate step to `_build_steps()` with step_id="remediate", gate=REMEDIATE_GATE, output_file="remediation-tasklist.md"
4. **[EXECUTION]** Wire remediate_executor.execute() as the step's executor function
5. **[EXECUTION]** Verify YAML/heading preservation constraints are in all agent prompts (NFR-013)
6. **[VERIFICATION]** Run `uv run pytest tests/roadmap/test_remediate_executor.py -k "registration or step"` to verify step is discoverable by pipeline
7. **[VERIFICATION]** Capture wall-clock timing of steps 10-11 execution and assert ≤30% overhead vs steps 1-9 baseline (NFR-008). Record timing in D-0023/spec.md under "Performance Notes" section.
8. **[COMPLETION]** Document step registration in `D-0023/spec.md`

**Acceptance Criteria:**
- Remediate step registered in `_build_steps()` and discoverable by `execute_pipeline()`
- Step exposes remediate as single step to outer pipeline while internal orchestration uses ClaudeProcess directly
- `REMEDIATE_GATE` applied to step output validation
- Agent prompts include YAML frontmatter and heading preservation constraints (NFR-013)
- Steps 10-11 wall-clock overhead is ≤30% vs steps 1-9 baseline per NFR-008 (timing recorded in D-0023/spec.md)
- executor.py step registration does not break existing steps 1-9 (validated by T07.01 E2E test, not unit tests alone)

**Validation:**
- `uv run pytest tests/roadmap/test_remediate_executor.py -k "registration or step"` exits 0
- Evidence: linkable artifact produced at `D-0023/spec.md`

**Dependencies:** T03.05 (REMEDIATE_GATE), T04.05 (agent execution coordinator)
**Rollback:** `git checkout -- src/superclaude/cli/roadmap/executor.py`
**Notes:** Dual-nature clarification: step registration exposes remediate to outer execute_pipeline() while internal dispatch uses ClaudeProcess directly (see T04.05).

---

### Checkpoint: End of Phase 4

**Purpose:** Verify complete remediation orchestrator is operational with parallel execution, rollback, and step registration.
**Checkpoint Report Path:** `.dev/releases/current/v2.22-RoadmapRemediate/checkpoints/CP-P04-END.md`
**Verification:**
- Parallel agents execute against different files concurrently without same-file conflicts
- Agent failure triggers full rollback (file contents match snapshots byte-for-byte)
- Updated remediation-tasklist.md passes REMEDIATE_GATE validation with outcome statuses
**Exit Criteria:**
- No files outside allowlist modified during remediation
- Rollback tested: first-agent-success + second-agent-failure scenario verified
- Wall-clock overhead ≤30% vs steps 1-9 baseline (NFR-008)
