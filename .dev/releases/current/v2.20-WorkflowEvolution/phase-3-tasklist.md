# Phase 3 -- Spec-Fidelity Gate

Implement the spec-fidelity prompt, gate, pipeline step, and state persistence. The pipeline must block on HIGH-severity spec-vs-roadmap deviations and handle agent failure gracefully through degraded mode.

### T03.01 -- Build Spec-Fidelity Prompt Builder

| Field | Value |
|---|---|
| Roadmap Item IDs | R-021 |
| Why | FR-001 through FR-004 require a prompt builder that instructs the LLM to compare spec against roadmap, quote both documents, and produce structured YAML frontmatter output. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | No alternate dependency fallback; degraded pipeline behavior applies after failure |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0022 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0022/evidence.md

**Deliverables:**
- build_spec_fidelity_prompt() function in src/superclaude/cli/roadmap/prompts.py

**Steps:**
1. **[PLANNING]** Read current src/superclaude/cli/roadmap/prompts.py structure and existing prompt builders
2. **[PLANNING]** Review severity classification from T02.05 for embedding in prompt
3. **[EXECUTION]** Implement build_spec_fidelity_prompt() that compares signatures, data models, gates, CLI options, NFRs
4. **[EXECUTION]** Embed explicit severity definitions in prompt to reduce LLM classification drift (RSK-007)
5. **[EXECUTION]** Require structured YAML frontmatter output with severity counts and tasklist_ready field
6. **[VERIFICATION]** `uv run pytest tests/roadmap/ -k spec_fidelity_prompt -v` exits 0
7. **[COMPLETION]** Document prompt template and expected output format

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -k spec_fidelity_prompt -v` exits 0 with all prompt builder tests passing
- Prompt includes explicit severity definitions (HIGH/MEDIUM/LOW) embedded in template
- Prompt requires quoting both spec and roadmap text for each deviation
- Output format specifies YAML frontmatter with severity_counts and tasklist_ready fields

**Validation:**
- `uv run pytest tests/roadmap/ -k spec_fidelity_prompt -v` — tests pass
- Evidence: test output showing prompt structure validation

**Dependencies:** T02.05 (severity classification), T02.04 (deviation format)
**Rollback:** Remove build_spec_fidelity_prompt() from prompts.py; degraded reporting remains the only post-failure behavior, not an alternate dependency path

---

### T03.02 -- Implement SPEC_FIDELITY_GATE

| Field | Value |
|---|---|
| Roadmap Item IDs | R-022 |
| Why | FR-005 through FR-007 require a new gate with STRICT enforcement that blocks on high_severity_count > 0 and supports degraded pass-through. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | No alternate dependency fallback; degraded pipeline behavior applies after failure |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0023 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0023/evidence.md

**Deliverables:**
- SPEC_FIDELITY_GATE implementation in src/superclaude/cli/roadmap/gates.py

**Steps:**
1. **[PLANNING]** Read current gate implementation patterns in src/superclaude/cli/roadmap/gates.py
2. **[PLANNING]** Review T02.07 (_high_severity_count_zero) and T02.08 (_tasklist_ready_consistent) for reuse
3. **[EXECUTION]** Add SPEC_FIDELITY_GATE with STRICT enforcement tier
4. **[EXECUTION]** Implement blocking logic: high_severity_count > 0 triggers block
5. **[EXECUTION]** Implement degraded pass-through: validation_complete=false AND fidelity_check_attempted=true triggers warn-and-continue
6. **[VERIFICATION]** `uv run pytest tests/roadmap/test_gates.py -k spec_fidelity_gate -v` exits 0
7. **[COMPLETION]** Document gate behavior for all three states: pass, block, degraded

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_gates.py -k spec_fidelity_gate -v` exits 0 with gate tests passing
- Gate blocks when high_severity_count > 0
- Gate passes through in degraded mode (validation_complete=false, fidelity_check_attempted=true)
- Gate reuses _high_severity_count_zero() and _tasklist_ready_consistent() from Phase 2

**Validation:**
- `uv run pytest tests/roadmap/test_gates.py -k spec_fidelity_gate -v` — tests pass
- Evidence: test output showing block, pass, and degraded behaviors

**Dependencies:** T02.07, T02.08 (semantic check functions)
**Rollback:** Remove SPEC_FIDELITY_GATE from gates.py

---

### T03.03 -- Integrate Spec-Fidelity Step into Pipeline Executor

| Field | Value |
|---|---|
| Roadmap Item IDs | R-023 |
| Why | FR-008 through FR-010 require a new pipeline step positioned after test-strategy that runs spec-fidelity validation with 600s timeout. |
| Effort | M |
| Risk | Low |
| Risk Drivers | pipeline |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | No alternate dependency fallback; degraded pipeline behavior applies after failure |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0024 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0024/evidence.md

**Deliverables:**
- spec-fidelity step added to _build_steps() in src/superclaude/cli/roadmap/executor.py

**Steps:**
1. **[PLANNING]** Read _build_steps() in src/superclaude/cli/roadmap/executor.py to identify insertion point
2. **[PLANNING]** Confirm step positioning: after test-strategy, per OQ-004 decision (after reflect)
3. **[EXECUTION]** Add spec-fidelity step with timeout=600s, retry_limit=1
4. **[EXECUTION]** Set output path to {output_dir}/spec-fidelity.md
5. **[EXECUTION]** Ensure --no-validate does NOT skip this step (FR-010, AC-005)
6. **[VERIFICATION]** `uv run pytest tests/roadmap/ -k "pipeline and spec_fidelity" -v` exits 0
7. **[COMPLETION]** Document step configuration and --no-validate behavior

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -k "pipeline and spec_fidelity" -v` exits 0 (SC-014)
- Step is positioned after test-strategy in pipeline execution order
- Step has timeout=600s, retry_limit=1, output={output_dir}/spec-fidelity.md
- --no-validate flag does NOT skip spec-fidelity step

**Validation:**
- `uv run pytest tests/roadmap/ -k "pipeline and spec_fidelity" -v` — tests pass
- Evidence: test output confirming step order and --no-validate behavior

**Dependencies:** T03.01 (prompt builder), T03.02 (gate)
**Rollback:** Remove spec-fidelity step from _build_steps()

---

### T03.04 -- Implement State Persistence and Degraded Reporting

| Field | Value |
|---|---|
| Roadmap Item IDs | R-024 |
| Why | FR-011, FR-030, FR-051.6 require fidelity status persistence in .roadmap-state.json and degraded reports that name failed agents. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | No alternate dependency fallback; degraded pipeline behavior applies after failure |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0025, D-0026 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0025/evidence.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0026/evidence.md

**Deliverables:**
- State persistence writing fidelity_status (pass|fail|skipped|degraded) to .roadmap-state.json
- Degraded reporting logic: on agent failure after retry exhaustion, produce report with validation_complete=false

**Steps:**
1. **[PLANNING]** Read current .roadmap-state.json structure and write patterns
2. **[PLANNING]** Design degraded report format: must name failed agent(s) and reason
3. **[EXECUTION]** Implement fidelity_status write to .roadmap-state.json (additive field)
4. **[EXECUTION]** Implement degraded report generation: validation_complete=false, agent error summary in body
5. **[EXECUTION]** Ensure degraded reports are distinguishable from clean passes (NFR-007)
6. **[VERIFICATION]** `uv run pytest tests/roadmap/ -k "state_persistence or degraded" -v` exits 0
7. **[COMPLETION]** Document state persistence contract and degraded report format

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -k state_persistence -v` exits 0 (SC-008)
- fidelity_status field written to .roadmap-state.json with valid enum values
- Degraded reports include validation_complete=false and agent failure details
- Degraded reports are distinguishable from clean passes per NFR-007

**Validation:**
- `uv run pytest tests/roadmap/ -k "state_persistence or degraded" -v` — tests pass
- Evidence: test output showing state file writes and degraded report distinction

**Dependencies:** T03.03 (pipeline step integration)
**Rollback:** Remove fidelity_status field from state writes; remove degraded report logic

---

### T03.05 -- Measure Spec-Fidelity Step Performance

| Field | Value |
|---|---|
| Roadmap Item IDs | R-025 |
| Why | NFR-001 requires spec-fidelity step execution within 120s p95. Performance must be measured during implementation, not deferred. |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance |
| Tier | EXEMPT |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | No alternate dependency fallback; degraded pipeline behavior applies after failure |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0027/notes.md

**Deliverables:**
- Performance measurement results for spec-fidelity step against 120s p95 target

**Steps:**
1. **[PLANNING]** Identify representative spec file for benchmarking
2. **[PLANNING]** Define measurement methodology (repeated runs, timing collection)
3. **[EXECUTION]** Run spec-fidelity step against representative spec with timing
4. **[EXECUTION]** Record execution times and compute p95
5. **[VERIFICATION]** Compare p95 against 120s target (SC-011)
6. **[COMPLETION]** Document results and any optimization recommendations

**Acceptance Criteria:**
- Performance report at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0027/notes.md exists
- Report includes measured p95 execution time against 120s target
- Measurement uses representative spec from project
- If p95 > 120s, optimization recommendations documented

**Validation:**
- Manual check: performance report contains numeric timing data and p95 calculation
- Evidence: linkable artifact produced (performance measurement report)

**Dependencies:** T03.03, T03.04 (complete spec-fidelity step)
**Rollback:** TBD

---

### T03.06 -- Execute Phase 3 Test Suite

| Field | Value |
|---|---|
| Roadmap Item IDs | R-026, R-027 |
| Why | All Phase 3 success criteria (SC-001, SC-002, SC-007, SC-008, SC-014) must be verified. Pipeline overhead must be <=5% excluding new step. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [████████░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | No alternate dependency fallback; degraded pipeline behavior applies after failure |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0028/evidence.md

**Deliverables:**
- Phase 3 test results verifying SC-001, SC-002, SC-007, SC-008, SC-014

**Steps:**
1. **[PLANNING]** List all tests added in Phase 3 and their SC criterion mappings
2. **[PLANNING]** Prepare integration test data for spec-fidelity scenarios
3. **[EXECUTION]** Run `uv run pytest tests/roadmap/ -v` and capture full output
4. **[EXECUTION]** Verify SC-001 (blocks HIGH), SC-002 (passes clean), SC-007 (degraded non-blocking)
5. **[EXECUTION]** Verify SC-008 (state records fidelity), SC-014 (--no-validate keeps fidelity)
6. **[VERIFICATION]** `uv run pytest tests/roadmap/ -v` exits 0 with 0 failures
7. **[COMPLETION]** Record SC verification matrix with pass/fail per criterion

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -v` exits 0 with 0 failures
- SC-001, SC-002, SC-007, SC-008, SC-014 individually verified with test evidence
- Pipeline time overhead <=5% excluding new spec-fidelity step (SC-012)
- All prior output phases remain green (regression check)

**Validation:**
- `uv run pytest tests/roadmap/ -v` — 0 failures
- Evidence: SC criterion verification matrix

**Dependencies:** T03.01-T03.05 (all Phase 3 tasks)
**Rollback:** TBD

---

### Checkpoint: End of Phase 3

**Purpose:** Confirm spec-fidelity gate is fully operational with all success criteria verified.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P03-END.md

**Verification:**
- SC-001, SC-002, SC-007, SC-008, SC-014 all pass with test evidence
- Spec-fidelity step runs within 120s on representative spec (NFR-001)
- Pipeline overhead <=5% excluding new step

**Exit Criteria:**
- All D-0022 through D-0028 artifacts created
- `uv run pytest tests/roadmap/ -v` exits 0 with no regressions
- Degraded reports distinguishable from clean passes (NFR-007 verified)
