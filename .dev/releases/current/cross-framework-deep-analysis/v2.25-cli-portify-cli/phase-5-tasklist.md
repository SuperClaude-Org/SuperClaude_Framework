# Phase 5 -- Analysis Pipeline

Implement Claude-assisted analysis artifact generation and first user review checkpoint. Requires Phase 3 observability baseline and Phase 4 gate system. Corresponds to spec Phase 1 steps 2-3.

### T05.01 -- Implement Protocol-Mapping Prompt Builder and EXIT_RECOMMENDATION Enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-055, R-056 |
| Why | FR-013 requires protocol-mapping step generating protocol-map.md with required YAML frontmatter. FR-014 requires EXIT_RECOMMENDATION marker enforcement. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | depends (Claude subprocess behavior) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0027 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0027/spec.md

**Deliverables:**
- Protocol-mapping prompt builder in `prompts.py` and step execution function generating `protocol-map.md` with YAML frontmatter and EXIT_RECOMMENDATION marker enforcement

**Steps:**
1. **[PLANNING]** Define protocol-map.md required YAML frontmatter fields from roadmap FR-013
2. **[PLANNING]** Review prompt builder patterns from existing SuperClaude prompt infrastructure
3. **[EXECUTION]** Implement `build_protocol_mapping_prompt()` in `prompts.py` assembling component inventory and skill content into Claude prompt
4. **[EXECUTION]** Implement protocol-mapping step execution: invoke Claude subprocess, capture output to protocol-map.md
5. **[EXECUTION]** Enforce EXIT_RECOMMENDATION marker presence in output; trigger PASS_NO_SIGNAL if absent
6. **[VERIFICATION]** Write integration test: protocol-mapping produces protocol-map.md passing G-002
7. **[COMPLETION]** Document prompt builder and marker enforcement in D-0027/spec.md

**Acceptance Criteria:**
- `build_protocol_mapping_prompt()` in `prompts.py` produces a structured prompt from component inventory
- Protocol-mapping step generates `protocol-map.md` with required YAML frontmatter (FR-013)
- EXIT_RECOMMENDATION marker enforced; absent marker triggers PASS_NO_SIGNAL status and retry
- Integration test confirms G-002 gate passes for generated protocol-map.md

**Validation:**
- `uv run pytest tests/ -k "test_protocol_mapping"` exits 0
- Evidence: linkable artifact produced at D-0027/spec.md

**Dependencies:** T04.03 (gate system), T03.11 (observability baseline)
**Rollback:** TBD (if not specified in roadmap)

---

### T05.02 -- Implement Analysis-Synthesis Prompt Builder and EXIT_RECOMMENDATION Enforcement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-057, R-058 |
| Why | FR-016 requires analysis-synthesis step generating portify-analysis-report.md with required sections. FR-017 requires EXIT_RECOMMENDATION enforcement. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | depends (Claude subprocess behavior) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0028 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0028/spec.md

**Deliverables:**
- Analysis-synthesis prompt builder in `prompts.py` and step execution function generating `portify-analysis-report.md` with required sections and EXIT_RECOMMENDATION enforcement

**Steps:**
1. **[PLANNING]** Define portify-analysis-report.md required sections: Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow, Classifications, Recommendations
2. **[PLANNING]** Review protocol-map.md output from T05.01 as input context
3. **[EXECUTION]** Implement `build_analysis_synthesis_prompt()` in `prompts.py` incorporating protocol map and component inventory
4. **[EXECUTION]** Implement analysis-synthesis step execution: invoke Claude subprocess, capture output to portify-analysis-report.md
5. **[EXECUTION]** Enforce EXIT_RECOMMENDATION marker and required section presence
6. **[VERIFICATION]** Write integration test: analysis-synthesis produces report passing G-003 (EXIT_RECOMMENDATION + required sections)
7. **[COMPLETION]** Document prompt builder and section requirements in D-0028/spec.md

**Acceptance Criteria:**
- `build_analysis_synthesis_prompt()` produces structured prompt from protocol map and inventory
- Analysis-synthesis step generates `portify-analysis-report.md` with all 7 required sections (FR-016)
- EXIT_RECOMMENDATION marker enforced; G-003 validates marker and has_required_analysis_sections
- Integration test confirms G-003 gate passes for generated report

**Validation:**
- `uv run pytest tests/ -k "test_analysis_synthesis"` exits 0
- Evidence: linkable artifact produced at D-0028/spec.md

**Dependencies:** T05.01
**Rollback:** TBD (if not specified in roadmap)

---

### T05.03 -- Enforce 600s Timeout for Analysis Steps

| Field | Value |
|---|---|
| Roadmap Item IDs | R-059 |
| Why | NFR-001 requires 600s timeout for both protocol-mapping and analysis-synthesis steps to prevent hung Claude subprocesses. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (timeout) |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0029 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0029/evidence.md

**Deliverables:**
- 600s timeout enforcement for protocol-mapping and analysis-synthesis steps

**Steps:**
1. **[PLANNING]** Confirm timeout value: 600s for both analysis steps per NFR-001
2. **[PLANNING]** Review executor timeout mechanism from T03.06
3. **[EXECUTION]** Configure protocol-mapping step with 600s timeout
4. **[EXECUTION]** Configure analysis-synthesis step with 600s timeout
5. **[VERIFICATION]** Verify timeout configuration matches NFR-001 specification
6. **[COMPLETION]** Document timeout settings in D-0029/evidence.md

**Acceptance Criteria:**
- Protocol-mapping step enforces 600s timeout per NFR-001
- Analysis-synthesis step enforces 600s timeout per NFR-001
- Timeout expiry triggers TIMEOUT status classification (exit code 124 path from T03.06)
- Timeout configuration documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0029/evidence.md

**Validation:**
- Manual check: step timeout configuration verified at 600s for both steps
- Evidence: linkable artifact produced at D-0029/evidence.md

**Dependencies:** T05.01, T05.02
**Rollback:** TBD (if not specified in roadmap)

---

### T05.04 -- Implement User-Review-P1 Gate with phase1-approval.yaml

| Field | Value |
|---|---|
| Roadmap Item IDs | R-060 |
| Why | FR-018 requires user-review-p1 gate that writes phase1-approval.yaml with status: pending, prints resume instructions, and exits cleanly. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | end-to-end (pause/resume flow) |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0030 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0030/spec.md

**Deliverables:**
- User-review-p1 step that writes `phase1-approval.yaml` with `status: pending`, prints resume instructions, and exits cleanly

**Steps:**
1. **[PLANNING]** Define phase1-approval.yaml schema: status (pending/approved/rejected), reviewer, timestamp
2. **[PLANNING]** Define resume instructions message format with exact CLI command
3. **[EXECUTION]** Implement user-review-p1 step: write phase1-approval.yaml with status: pending
4. **[EXECUTION]** Print formatted resume instructions to console including resume command from T03.10
5. **[EXECUTION]** Exit cleanly with appropriate outcome (paused, not failed)
6. **[VERIFICATION]** Write unit test: review step produces phase1-approval.yaml with status: pending (SC-006)
7. **[COMPLETION]** Document review gate behavior in D-0030/spec.md

**Acceptance Criteria:**
- User-review-p1 writes `phase1-approval.yaml` in workdir with `status: pending` (SC-006)
- Resume instructions printed to console with exact CLI command for resumption
- Pipeline exits cleanly (not error status) after writing approval file
- Review gate documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0030/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_review_p1"` exits 0
- Evidence: linkable artifact produced at D-0030/spec.md

**Dependencies:** T05.02, T03.10
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.04

**Purpose:** Verify analysis pipeline produces artifacts passing gates and review checkpoint pauses correctly.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P05-T01-T04.md

**Verification:**
- Protocol-mapping produces protocol-map.md passing G-002 (EXIT_RECOMMENDATION present)
- Analysis-synthesis produces portify-analysis-report.md passing G-003 (EXIT_RECOMMENDATION + required sections)
- User-review-p1 writes phase1-approval.yaml with status: pending and exits cleanly

**Exit Criteria:**
- SC-003 (G-002 passes) and SC-004 (G-003 passes) validated
- SC-006 (review gates write pending approval) validated
- 600s timeout enforced on both analysis steps

---

### T05.05 -- Implement Resume Logic with YAML Parse Validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-061 |
| Why | FR-019 requires --resume to validate status: approved in approval YAML with YAML parse + schema validation, not raw string matching. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | security (approval validation), data (YAML parse) |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0031 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0031/spec.md

**Deliverables:**
- Resume logic requiring `status: approved` in `phase1-approval.yaml` with proper YAML parse and schema validation per FR-019

**Steps:**
1. **[PLANNING]** Review Risk 8 mitigation: YAML parse + schema validation required (not raw string matching)
2. **[PLANNING]** Define validation schema: status field must be "approved" (not in comment, not partial match)
3. **[EXECUTION]** Implement YAML parser loading phase1-approval.yaml
4. **[EXECUTION]** Implement schema validation: verify status field exists and equals "approved" (reject "pending", "rejected", malformed YAML)
5. **[VERIFICATION]** Write integration tests: resume with approved status, resume with pending status (block), resume with malformed YAML (block), status in comment (block)
6. **[COMPLETION]** Document resume validation logic in D-0031/spec.md

**Acceptance Criteria:**
- Resume logic uses YAML parse + schema validation (not raw string matching) per FR-019 and Risk 8 mitigation
- Requires `status: approved` as parsed YAML field value; rejects status in comments or malformed YAML
- Pipeline blocks resume when status is "pending" or "rejected" with clear error message
- Resume validation documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0031/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_resume_validation"` exits 0
- Evidence: linkable artifact produced at D-0031/spec.md

**Dependencies:** T05.04
**Rollback:** TBD (if not specified in roadmap)

---

### T05.06 -- Assemble Phase 1 Prompt Builders, Step Functions, and Review-Gate Logic

| Field | Value |
|---|---|
| Roadmap Item IDs | R-062, R-063, R-064 |
| Why | Phase 1 deliverables must be assembled: prompts.py with Phase 1 builders, analysis step functions, and review-gate logic with YAML parse validation. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0032 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0032/spec.md

**Deliverables:**
- Consolidated `prompts.py` with Phase 1 prompt builders, analysis step function implementations, and review-gate logic module

**Steps:**
1. **[PLANNING]** Inventory all Phase 1 components: prompt builders (T05.01, T05.02), step functions, review gate (T05.04), resume logic (T05.05)
2. **[PLANNING]** Verify no duplication between individual implementations and consolidated module
3. **[EXECUTION]** Consolidate prompt builders into `prompts.py` Phase 1 section
4. **[EXECUTION]** Verify analysis step functions are correctly wired to executor step registration
5. **[VERIFICATION]** Run full Phase 1 integration test: protocol-mapping → analysis-synthesis → review-p1 → resume; include step-skipping test: mark analysis steps completed, resume, verify skipped (SC-007)
6. **[COMPLETION]** Document Phase 1 module organization in D-0032/spec.md

**Acceptance Criteria:**
- `prompts.py` contains both Phase 1 prompt builders (protocol-mapping and analysis-synthesis)
- Analysis step functions correctly wired to executor via step registration
- Full Phase 1 flow (protocol-mapping → analysis-synthesis → review-p1 → resume) executes in sequence
- Module organization documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0032/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_phase1_flow"` exits 0
- Evidence: linkable artifact produced at D-0032/spec.md

**Dependencies:** T05.01, T05.02, T05.04, T05.05
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 5

**Purpose:** Verify Phase 1 (analysis) completes reliably; review gate pauses correctly; resume validates status: approved with YAML schema check.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P05-END.md

**Verification:**
- SC-003 (G-002 passes for protocol-map.md) and SC-004 (G-003 passes for analysis-report.md) validated
- SC-006 (review gates write pending approval yaml) validated
- SC-007 (resume skips completed steps) validated across Phase 1 boundary

**Exit Criteria:**
- Milestone M4 satisfied: Phase 1 completes reliably; review gate pauses correctly; resume validates approval
- All 6 tasks (T05.01-T05.06) completed with deliverables D-0027 through D-0032 produced
- Phase 1 prompt builders, step functions, and review-gate logic assembled and tested
