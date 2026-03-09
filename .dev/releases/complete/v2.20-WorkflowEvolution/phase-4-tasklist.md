# Phase 4 -- Tasklist Fidelity and CLI

Implement tasklist validation as a standalone CLI subcommand with its own fidelity gate. The `superclaude tasklist validate` command must catch fabricated traceability IDs and missing deliverables, validating tasklists against their upstream roadmap only.

### T04.01 -- Build Tasklist-Fidelity Prompt Builder

| Field | Value |
|---|---|
| Roadmap Item IDs | R-028 |
| Why | FR-013/FR-014 require a prompt builder that checks deliverable coverage, signature preservation, traceability ID validity, and dependency chain correctness against roadmap. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0029/evidence.md

**Deliverables:**
- build_tasklist_fidelity_prompt() function with validation layering guard (roadmap-only, NOT spec)

**Steps:**
1. **[PLANNING]** Read build_spec_fidelity_prompt() from T03.01 for pattern reuse
2. **[PLANNING]** Review FR-013/FR-014: deliverable coverage, signature preservation, traceability ID validity
3. **[EXECUTION]** Implement build_tasklist_fidelity_prompt() reusing deviation report format
4. **[EXECUTION]** Enforce validation layering guard: checks roadmap→tasklist only, NOT spec→tasklist
5. **[EXECUTION]** Add test_tasklist_validates_against_roadmap_not_spec to enforce layering
6. **[VERIFICATION]** `uv run pytest tests/tasklist/ -k tasklist_fidelity_prompt -v` exits 0
7. **[COMPLETION]** Document prompt template and layering constraint

**Acceptance Criteria:**
- `uv run pytest tests/tasklist/ -k tasklist_fidelity_prompt -v` exits 0
- Prompt checks: deliverable coverage, signature preservation, traceability ID validity, dependency chains
- test_tasklist_validates_against_roadmap_not_spec passes (validation layering guard)
- Prompt reuses deviation report format from Phase 2

**Validation:**
- `uv run pytest tests/tasklist/ -k tasklist_fidelity_prompt -v` — tests pass
- Evidence: test output confirming layering guard enforcement

**Dependencies:** T02.04 (deviation format), T03.01 (prompt pattern)
**Rollback:** Remove build_tasklist_fidelity_prompt()

---

### T04.02 -- Implement TASKLIST_FIDELITY_GATE

| Field | Value |
|---|---|
| Roadmap Item IDs | R-029 |
| Why | FR-015 requires STRICT enforcement that blocks on high_severity_count > 0, reusing semantic checks from Phase 2. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0030/evidence.md

**Deliverables:**
- TASKLIST_FIDELITY_GATE implementation reusing _high_severity_count_zero() and _tasklist_ready_consistent()

**Steps:**
1. **[PLANNING]** Read SPEC_FIDELITY_GATE implementation from T03.02 for pattern reuse
2. **[PLANNING]** Confirm reuse of _high_severity_count_zero() and _tasklist_ready_consistent()
3. **[EXECUTION]** Implement TASKLIST_FIDELITY_GATE with STRICT enforcement
4. **[EXECUTION]** Add tests: blocks on high severity, passes on clean tasklist
5. **[VERIFICATION]** `uv run pytest tests/tasklist/ -k tasklist_fidelity_gate -v` exits 0
6. **[COMPLETION]** Document gate behavior and semantic check reuse

**Acceptance Criteria:**
- `uv run pytest tests/tasklist/ -k tasklist_fidelity_gate -v` exits 0
- Gate blocks when high_severity_count > 0 (STRICT enforcement)
- Gate reuses _high_severity_count_zero() and _tasklist_ready_consistent() from Phase 2
- Gate passes on clean tasklist with no deviations

**Validation:**
- `uv run pytest tests/tasklist/ -k tasklist_fidelity_gate -v` — tests pass
- Evidence: test output showing block and pass behaviors

**Dependencies:** T02.07, T02.08 (semantic checks), T03.02 (gate pattern)
**Rollback:** Remove TASKLIST_FIDELITY_GATE

---

### T04.03 -- Implement CLI Subcommand superclaude tasklist validate

| Field | Value |
|---|---|
| Roadmap Item IDs | R-030 |
| Why | FR-016/FR-017 require a standalone CLI subcommand with options for roadmap file, tasklist dir, model, max-turns, debug. Must exit 1 on HIGH deviations. |
| Effort | S |
| Risk | Low |
| Risk Drivers | multi-file scope (new module with 5 files) |
| Tier | STRICT |
| Confidence | [███████░░░] 73% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0031, D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0031/evidence.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0032/evidence.md

**Deliverables:**
- CLI module src/superclaude/cli/tasklist/ with __init__.py, commands.py, executor.py, gates.py, prompts.py
- Registered subcommand `superclaude tasklist validate` with help text

**Steps:**
1. **[PLANNING]** Read existing CLI module structure in src/superclaude/cli/ for conventions
2. **[PLANNING]** Review OQ-002 decision from T01.05 confirming cli/tasklist/ placement
3. **[EXECUTION]** Create src/superclaude/cli/tasklist/ module with __init__.py, commands.py, executor.py, gates.py, prompts.py
4. **[EXECUTION]** Implement `superclaude tasklist validate <output-dir>` with options: --roadmap-file, --tasklist-dir, --model, --max-turns, --debug
5. **[EXECUTION]** Set exit code 1 on HIGH-severity deviations; output to {output_dir}/tasklist-fidelity.md
6. **[EXECUTION]** Register tasklist command group in src/superclaude/cli/main.py
7. **[VERIFICATION]** `uv run pytest tests/tasklist/ -v` exits 0; `superclaude tasklist validate --help` renders
8. **[COMPLETION]** Document CLI usage and all option descriptions

**Acceptance Criteria:**
- `superclaude tasklist validate --help` renders with all option descriptions
- CLI exits 1 on HIGH-severity deviations (test_tasklist_validate_exit_code_on_high)
- Output written to {output_dir}/tasklist-fidelity.md
- Module structure: src/superclaude/cli/tasklist/ contains __init__.py, commands.py, executor.py, gates.py, prompts.py

**Validation:**
- `uv run pytest tests/tasklist/ -v` — tests pass
- Evidence: CLI help output and exit code verification

**Dependencies:** T04.01 (prompt builder), T04.02 (gate), T01.05 (module placement decision)
**Rollback:** Remove src/superclaude/cli/tasklist/ module and deregister from main.py

---

### T04.04 -- Measure Tasklist Validation Performance

| Field | Value |
|---|---|
| Roadmap Item IDs | R-031 |
| Why | NFR-002 requires tasklist validation within 120s p95. Performance must be measured during implementation. |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance |
| Tier | EXEMPT |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0033/notes.md

**Deliverables:**
- Tasklist validation performance measurement results against 120s p95 target

**Steps:**
1. **[PLANNING]** Identify representative tasklist and roadmap for benchmarking
2. **[PLANNING]** Define measurement methodology (repeated runs, timing)
3. **[EXECUTION]** Run `superclaude tasklist validate` with timing against representative inputs
4. **[EXECUTION]** Record execution times and compute p95
5. **[VERIFICATION]** Compare p95 against 120s target (SC-011, NFR-002)
6. **[COMPLETION]** Document results and optimization recommendations if needed

**Acceptance Criteria:**
- Performance report at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0033/notes.md exists
- Report includes measured p95 execution time against 120s target
- Measurement uses representative inputs from project artifacts
- If p95 > 120s, optimization recommendations documented

**Validation:**
- Manual check: performance report contains numeric timing data
- Evidence: linkable artifact produced (performance report)

**Dependencies:** T04.03 (CLI subcommand operational)
**Rollback:** No code-path rollback required; remove or replace invalid benchmark evidence if tasklist validation timing data proves incorrect

---

### T04.05 -- Execute Phase 4 Test Suite

| Field | Value |
|---|---|
| Roadmap Item IDs | R-032, R-033 |
| Why | SC-005, SC-009, SC-013 must be verified. CLI must be registered. Deviation reports must be 100% parseable. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [████████░░] 75% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0034/evidence.md

**Deliverables:**
- Output Phase 4 test results verifying SC-005, SC-009, SC-013, fabricated traceability detection, validation layering guard, and regression check

**Steps:**
1. **[PLANNING]** List all tests added in Phase 4 and their SC criterion mappings
2. **[PLANNING]** Prepare E2E test data using v2.19 artifacts for fabricated traceability test
3. **[EXECUTION]** Run `uv run pytest tests/tasklist/ -v` for new tasklist tests
4. **[EXECUTION]** Run E2E: test_tasklist_validate_catches_fabricated_traceability against v2.19 artifacts (SC-005)
5. **[EXECUTION]** Verify SC-009, SC-013, and validation layering guard
6. **[VERIFICATION]** `uv run pytest tests/ -v` exits 0 with 0 failures (full regression)
7. **[COMPLETION]** Record SC verification matrix

**Acceptance Criteria:**
- `uv run pytest tests/ -v` exits 0 with 0 failures
- SC-005 (catches fabricated traceability against v2.19 artifacts), SC-009, and SC-013 individually verified
- Deviation reports 100% parseable (NFR-005)
- test_tasklist_validates_against_roadmap_not_spec passes (validation layering guard)

**Validation:**
- `uv run pytest tests/ -v` — 0 failures
- Evidence: SC criterion verification matrix

**Dependencies:** T04.01-T04.04 (all output Phase 4 tasks)
**Rollback:** Re-run the output Phase 4 verification suite after removing invalid evidence or test-matrix entries if a verification path proves incorrect

---

### Checkpoint: End of Phase 4

**Purpose:** Confirm tasklist fidelity gate and CLI subcommand are fully operational.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P04-END.md

**Verification:**
- `superclaude tasklist validate --help` renders correctly
- SC-005 (fabricated traceability detection) passes with v2.19 artifacts
- All prior output phases (Phases 1–3) still pass (full regression check)

**Exit Criteria:**
- All D-0029 through D-0034 artifacts created
- CLI subcommand registered and operational
- SC-005, SC-009, and SC-013 verified with evidence
- Validation layering guard verified by test_tasklist_validates_against_roadmap_not_spec
- Deviation reports 100% parseable (NFR-005)
- All prior output phases (Phases 1–3) still pass (full regression check)
