# Phase 6 -- Specification Pipeline

Implement Claude-assisted design/spec generation and second user review checkpoint. Corresponds to spec Phase 2 steps 5-8.

### T06.01 -- Implement Step-Graph-Design Prompt Builder

| Field | Value |
|---|---|
| Roadmap Item IDs | R-068 |
| Why | FR-020 requires step-graph-design prompt builder generating step-graph-spec.md as input to pipeline spec assembly. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | depends (Claude subprocess) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0033 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0033/spec.md

**Deliverables:**
- `build_step_graph_design_prompt()` in `prompts.py` generating `step-graph-spec.md` from analysis report

**Steps:**
1. **[PLANNING]** Review portify-analysis-report.md output structure for step graph input data
2. **[PLANNING]** Define step-graph-spec.md expected structure and EXIT_RECOMMENDATION requirements
3. **[EXECUTION]** Implement `build_step_graph_design_prompt()` in `prompts.py` Phase 2 section
4. **[EXECUTION]** Implement step-graph-design execution: invoke Claude subprocess, capture to step-graph-spec.md
5. **[EXECUTION]** Enforce EXIT_RECOMMENDATION marker in output
6. **[VERIFICATION]** Write test: step-graph-design produces spec with EXIT_RECOMMENDATION marker
7. **[COMPLETION]** Document prompt builder in D-0033/spec.md

**Acceptance Criteria:**
- `build_step_graph_design_prompt()` produces structured prompt from analysis report data
- Step-graph-design step generates `step-graph-spec.md` in workdir
- EXIT_RECOMMENDATION marker present in output (enforced by gate G-005)
- Prompt builder documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0033/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_step_graph"` exits 0
- Evidence: linkable artifact produced at D-0033/spec.md

**Dependencies:** T05.06 (Phase 1 complete)
**Rollback:** TBD (if not specified in roadmap)

---

### T06.02 -- Implement Models-Gates-Design Prompt Builder

| Field | Value |
|---|---|
| Roadmap Item IDs | R-069 |
| Why | FR-021 requires models-gates-design prompt builder generating models-gates-spec.md for pipeline spec assembly. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | model, schema |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | Yes |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0034 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0034/spec.md

**Deliverables:**
- `build_models_gates_design_prompt()` in `prompts.py` generating `models-gates-spec.md`

**Steps:**
1. **[PLANNING]** Review domain models and gate system outputs for input context
2. **[PLANNING]** Define models-gates-spec.md expected structure
3. **[EXECUTION]** Implement `build_models_gates_design_prompt()` in `prompts.py`
4. **[EXECUTION]** Implement step execution generating models-gates-spec.md
5. **[VERIFICATION]** Write test: models-gates-design produces spec with EXIT_RECOMMENDATION
6. **[COMPLETION]** Document prompt builder in D-0034/spec.md

**Acceptance Criteria:**
- `build_models_gates_design_prompt()` produces structured prompt incorporating model and gate specifications
- Models-gates-design step generates `models-gates-spec.md` in workdir
- EXIT_RECOMMENDATION marker present in output
- Prompt builder documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0034/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_models_gates_design"` exits 0
- Evidence: linkable artifact produced at D-0034/spec.md

**Dependencies:** T06.01
**Rollback:** TBD (if not specified in roadmap)

---

### T06.03 -- Implement Prompts-Executor-Design Prompt Builder

| Field | Value |
|---|---|
| Roadmap Item IDs | R-070 |
| Why | FR-022 requires prompts-executor-design prompt builder generating prompts-executor-spec.md for pipeline spec assembly. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | depends (Claude subprocess) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0035 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0035/spec.md

**Deliverables:**
- `build_prompts_executor_design_prompt()` in `prompts.py` generating `prompts-executor-spec.md`

**Steps:**
1. **[PLANNING]** Review executor architecture from Phase 3 for prompt and executor design context
2. **[PLANNING]** Define prompts-executor-spec.md expected structure
3. **[EXECUTION]** Implement `build_prompts_executor_design_prompt()` in `prompts.py`
4. **[EXECUTION]** Implement step execution generating prompts-executor-spec.md
5. **[VERIFICATION]** Write test: prompts-executor-design produces spec with EXIT_RECOMMENDATION
6. **[COMPLETION]** Document prompt builder in D-0035/spec.md

**Acceptance Criteria:**
- `build_prompts_executor_design_prompt()` produces structured prompt for executor design specification
- Prompts-executor-design step generates `prompts-executor-spec.md` in workdir
- EXIT_RECOMMENDATION marker present in output
- Prompt builder documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0035/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_prompts_executor_design"` exits 0
- Evidence: linkable artifact produced at D-0035/spec.md

**Dependencies:** T06.01
**Rollback:** TBD (if not specified in roadmap)

---

### T06.04 -- Implement Pipeline-Spec-Assembly with Programmatic Pre-Assembly and Claude Synthesis

| Field | Value |
|---|---|
| Roadmap Item IDs | R-071 |
| Why | FR-023 requires pipeline-spec-assembly combining programmatic pre-assembly (concatenation, dedup) with Claude synthesis to produce portify-spec.md. |
| Effort | L |
| Risk | Medium |
| Risk Drivers | end-to-end, depends |
| Tier | STRICT |
| Confidence | [████████░░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Required |
| Deliverable IDs | D-0036 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0036/spec.md

**Deliverables:**
- Pipeline-spec-assembly logic: programmatic pre-assembly (concatenation of step-graph-spec.md, models-gates-spec.md, prompts-executor-spec.md with deduplication) followed by Claude synthesis producing `portify-spec.md`

**Steps:**
1. **[PLANNING]** Define pre-assembly algorithm: concatenation order, deduplication rules
2. **[PLANNING]** Define portify-spec.md expected structure with frontmatter and step_mapping
3. **[EXECUTION]** Implement programmatic pre-assembly: concatenate design specs, remove duplicate sections
4. **[EXECUTION]** Implement Claude synthesis step: feed pre-assembled content to Claude for unified spec production
5. **[EXECUTION]** Enforce EXIT_RECOMMENDATION marker and step_mapping consistency in output
6. **[VERIFICATION]** Write integration test: pipeline-spec-assembly produces portify-spec.md passing G-008 (EXIT_RECOMMENDATION + step-count consistency)
7. **[COMPLETION]** Document assembly algorithm in D-0036/spec.md

**Acceptance Criteria:**
- Programmatic pre-assembly concatenates design specs and removes duplicates before Claude synthesis
- Pipeline-spec-assembly produces `portify-spec.md` with frontmatter and step_mapping field
- G-008 validates: EXIT_RECOMMENDATION present and step_mapping count matches declared steps (SC-005)
- Assembly algorithm documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0036/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_spec_assembly"` exits 0
- Evidence: linkable artifact produced at D-0036/spec.md

**Dependencies:** T06.01, T06.02, T06.03
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: Phase 6 / Tasks T06.01-T06.04

**Purpose:** Verify all three design prompt builders produce specs and pipeline-spec-assembly produces unified portify-spec.md passing G-008.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P06-T01-T04.md

**Verification:**
- All three design prompt builders produce spec artifacts with EXIT_RECOMMENDATION markers
- Pipeline-spec-assembly produces portify-spec.md with valid frontmatter and step_mapping
- G-008 passes: EXIT_RECOMMENDATION present and step-count consistency verified

**Exit Criteria:**
- SC-005 (G-008 passes for portify-spec.md) validated
- All design spec artifacts generated in workdir
- Pre-assembly deduplication logic verified

---

### T06.05 -- Enforce EXIT_RECOMMENDATION Markers and 600s Timeout for Phase 2 Steps

| Field | Value |
|---|---|
| Roadmap Item IDs | R-072, R-073 |
| Why | FR-024 requires EXIT_RECOMMENDATION markers on all Phase 2 Claude steps. NFR-001 requires 600s timeout per step. |
| Effort | S |
| Risk | Low |
| Risk Drivers | performance (timeout) |
| Tier | STRICT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0037/evidence.md

**Deliverables:**
- EXIT_RECOMMENDATION enforcement and 600s timeout configuration for all Phase 2 Claude-assisted steps

**Steps:**
1. **[PLANNING]** Enumerate all Phase 2 Claude steps: step-graph-design, models-gates-design, prompts-executor-design, pipeline-spec-assembly
2. **[PLANNING]** Confirm timeout value: 600s per step per NFR-001
3. **[EXECUTION]** Verify EXIT_RECOMMENDATION enforcement is active for all 4 Phase 2 steps
4. **[EXECUTION]** Configure 600s timeout for each Phase 2 step
5. **[VERIFICATION]** Write tests: marker enforcement triggers PASS_NO_SIGNAL on absence; timeout triggers TIMEOUT status
6. **[COMPLETION]** Document enforcement configuration in D-0037/evidence.md

**Acceptance Criteria:**
- EXIT_RECOMMENDATION marker enforced on all 4 Phase 2 Claude steps (FR-024)
- 600s timeout configured for each Phase 2 step per NFR-001
- Missing marker triggers PASS_NO_SIGNAL status and retry per T03.07 mechanism
- Enforcement documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0037/evidence.md

**Validation:**
- `uv run pytest tests/ -k "test_phase2_enforcement"` exits 0
- Evidence: linkable artifact produced at D-0037/evidence.md

**Dependencies:** T06.04
**Rollback:** TBD (if not specified in roadmap)

---

### T06.06 -- Implement User-Review-P2 Validation and phase2-approval.yaml Resume

| Field | Value |
|---|---|
| Roadmap Item IDs | R-074, R-075 |
| Why | FR-025 requires user-review-p2 validation checking status: completed, all blocking gates passed, step_mapping has entries. FR-026 requires phase2-approval.yaml resume with YAML parse validation. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (YAML parse), end-to-end |
| Tier | STANDARD |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0038/spec.md

**Deliverables:**
- User-review-p2 step validating `status: completed` with gate pass verification and step_mapping entry check; `phase2-approval.yaml` resume enforcement with YAML parse validation

**Steps:**
1. **[PLANNING]** Define user-review-p2 validation criteria: status completed, blocking gates passed, step_mapping non-empty
2. **[PLANNING]** Reuse YAML parse validation pattern from T05.05
3. **[EXECUTION]** Implement user-review-p2 step: write phase2-approval.yaml with status: pending, validate gate results
4. **[EXECUTION]** Implement resume enforcement: YAML parse + schema validation for phase2-approval.yaml (reuse pattern from T05.05)
5. **[VERIFICATION]** Write integration test: review-p2 validates and blocks correctly; resume requires approved status
6. **[COMPLETION]** Document review-p2 behavior in D-0038/spec.md

**Acceptance Criteria:**
- User-review-p2 validates: status completed, all blocking gates passed, step_mapping has entries (FR-025)
- `phase2-approval.yaml` resume uses YAML parse + schema validation (not raw string matching) per FR-026
- Pipeline blocks resume when validation criteria not met with clear error
- Review-p2 documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0038/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_review_p2"` exits 0
- Evidence: linkable artifact produced at D-0038/spec.md

**Dependencies:** T06.04, T05.05
**Rollback:** TBD (if not specified in roadmap)

---

### T06.07 -- Assemble Phase 2 Deliverable Artifacts

| Field | Value |
|---|---|
| Roadmap Item IDs | R-076, R-077, R-078, R-079, R-080, R-081 |
| Why | Phase 2 deliverables must be consolidated: prompt builders in prompts.py, spec assembly logic, portify-spec.md, review flow, phase2-approval.yaml, and intermediate spec artifacts. |
| Effort | M |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [███████░░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0039/spec.md

**Deliverables:**
- Consolidated Phase 2 prompt builders in `prompts.py`, spec assembly logic, `portify-spec.md`, second review pause/resume flow, `phase2-approval.yaml`, and intermediate specs (step-graph-spec.md, models-gates-spec.md, prompts-executor-spec.md)

**Steps:**
1. **[PLANNING]** Inventory all Phase 2 deliverables and verify completeness
2. **[PLANNING]** Confirm all intermediate spec files are generated in workdir
3. **[EXECUTION]** Consolidate Phase 2 prompt builders into prompts.py Phase 2 section
4. **[EXECUTION]** Verify end-to-end Phase 2 flow: design steps → assembly → review-p2 → resume
5. **[VERIFICATION]** Run full Phase 2 integration test including resume across review boundary (SC-007)
6. **[COMPLETION]** Document Phase 2 deliverable organization in D-0039/spec.md

**Acceptance Criteria:**
- `prompts.py` contains all Phase 2 prompt builders (step-graph, models-gates, prompts-executor, assembly)
- Full Phase 2 flow executes: design → assembly → review-p2 → resume across boundary
- SC-007 (resume skips completed steps) validated across Phase 2 review boundary
- Deliverable organization documented in .dev/releases/current/v2.25-cli-portify-cli/artifacts/D-0039/spec.md

**Validation:**
- `uv run pytest tests/ -k "test_phase2_flow"` exits 0
- Evidence: linkable artifact produced at D-0039/spec.md

**Dependencies:** T06.04, T06.05, T06.06
**Rollback:** TBD (if not specified in roadmap)

---

### Checkpoint: End of Phase 6

**Purpose:** Verify Phase 2 produces a valid unified pipeline spec passing G-008; user-review-p2 validates and blocks correctly.

**Checkpoint Report Path:** .dev/releases/current/v2.25-cli-portify-cli/checkpoints/CP-P06-END.md

**Verification:**
- SC-005 (G-008 passes for portify-spec.md) validated: frontmatter + step_mapping consistency
- SC-006 (review gates write pending approval) validated for phase2-approval.yaml
- SC-007 (resume skips completed steps) validated across Phase 2 review boundary

**Exit Criteria:**
- Milestone M5 satisfied: Phase 2 produces valid unified spec; user-review-p2 validates correctly
- All 7 tasks (T06.01-T06.07) completed with deliverables D-0033 through D-0039 produced
- Super-milestone B (Pipeline Generation): roadmap Phases 4-6 / tasklist Phases 5-7 artifacts ready for synthesis
