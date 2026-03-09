# Phase 5 -- Retrospective and Hardening

Wire retrospective context into extraction, harden integration across the full pipeline, finalize documentation, and validate rollout safety. This phase ensures the complete pipeline runs end-to-end with all new gates active and all documentation is production-ready.

### T05.01 -- Wire Retrospective Parameter into Extraction Prompt

| Field | Value |
|---|---|
| Roadmap Item IDs | R-034 |
| Why | FR-027 through FR-029 require retrospective content to reach the extraction prompt as advisory context, with CLI flag and config support. |
| Effort | S |
| Risk | Low |
| Risk Drivers | multi-file scope (prompts.py, models.py, commands.py) |
| Tier | STRICT |
| Confidence | [███████░░░] 73% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0035, D-0036, D-0037 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0035/evidence.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0036/evidence.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0037/evidence.md

**Deliverables:**
- build_extract_prompt() in src/superclaude/cli/roadmap/prompts.py accepts retrospective_content: str | None
- RoadmapConfig in src/superclaude/cli/roadmap/models.py extended with retrospective_file: Path | None
- CLI flag --retrospective added to `roadmap run` command in src/superclaude/cli/roadmap/commands.py

**Steps:**
1. **[PLANNING]** Read build_extract_prompt() in src/superclaude/cli/roadmap/prompts.py
2. **[PLANNING]** Read RoadmapConfig in src/superclaude/cli/roadmap/models.py
3. **[EXECUTION]** Add retrospective_content parameter to build_extract_prompt()
4. **[EXECUTION]** Frame retrospective as "areas to watch" not requirements (RSK-004 mitigation)
5. **[EXECUTION]** Extend RoadmapConfig with retrospective_file: Path | None
6. **[EXECUTION]** Add --retrospective flag to roadmap run CLI command; missing file proceeds normally
7. **[VERIFICATION]** `uv run pytest tests/roadmap/ -k retrospective -v` exits 0
8. **[COMPLETION]** Document retrospective parameter behavior and missing-file handling

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -k retrospective -v` exits 0 (SC-006)
- build_extract_prompt() accepts retrospective_content and frames it as advisory
- Missing retrospective file does not cause error (extraction proceeds normally)
- Prompt frames retrospective as "areas to watch" not requirements

**Validation:**
- `uv run pytest tests/roadmap/ -k retrospective -v` — tests pass
- Evidence: test output showing advisory framing and missing-file handling

**Dependencies:** Phase 3 complete (pipeline step infrastructure)
**Rollback:** Remove retrospective parameter from all 3 files

---

### T05.02 -- Document Multi-Agent Severity Resolution Protocol

| Field | Value |
|---|---|
| Roadmap Item IDs | R-035 |
| Why | FR-012 is deferred to v2.21, but the conservative merge protocol must be documented now for future implementation. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0038 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0038/spec.md

**Deliverables:**
- Documentation of conservative merge protocol: highest severity wins, validation_complete=false if any agent fails

**Steps:**
1. **[PLANNING]** Review OQ-007 decision from T01.04 for deferral scope
2. **[PLANNING]** Identify merge protocol rules from roadmap
3. **[EXECUTION]** Document conservative merge protocol in specification format
4. **[EXECUTION]** Include: highest severity wins rule, validation_complete semantics, failure handling
5. **[VERIFICATION]** Confirm document is consistent with OQ-007 decision
6. **[COMPLETION]** Mark FR-012 as deferred to v2.21 with reference to this document

**Acceptance Criteria:**
- Protocol document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0038/spec.md exists
- Document specifies "highest severity wins" merge rule
- Document specifies validation_complete=false when any agent fails
- Document explicitly notes FR-012 full implementation deferred to v2.21

**Validation:**
- Manual check: document contains merge rules and deferral notice
- Evidence: linkable artifact produced (protocol specification)

**Dependencies:** T01.04 (OQ-007 deferral decision)
**Rollback:** TBD

---

### T05.03 -- Execute Full Pipeline Integration Run

| Field | Value |
|---|---|
| Roadmap Item IDs | R-036 |
| Why | Validates that the complete pipeline with all new gates runs end-to-end against real specs without regressions. |
| Effort | M |
| Risk | Low |
| Risk Drivers | cross-cutting (end-to-end pipeline) |
| Tier | EXEMPT |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0039 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0039/evidence.md

**Deliverables:**
- Integration run results documenting pass/fail per spec for 3+ specs from .dev/releases/complete/

**Steps:**
1. **[PLANNING]** Identify 3+ existing specs from .dev/releases/complete/ for testing
2. **[PLANNING]** Prepare pipeline run configuration with all gates enabled
3. **[EXECUTION]** Run full pipeline against each selected spec
4. **[EXECUTION]** Record pass/fail results, gate outcomes, and timing per spec
5. **[VERIFICATION]** Confirm no unexpected failures from new gates
6. **[COMPLETION]** Document results with per-spec breakdown

**Acceptance Criteria:**
- Integration results at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0039/evidence.md exist
- Results cover 3+ specs from .dev/releases/complete/
- Each spec has documented pass/fail status with gate-level detail
- No regressions from Phase 4 hardening

**Validation:**
- Manual check: results cover 3+ specs with per-gate outcomes
- Evidence: linkable artifact produced (integration run results)

**Dependencies:** Phase 3, Phase 4 complete
**Rollback:** TBD

---

### T05.04 -- Verify Cross-Reference Warning Mode

| Field | Value |
|---|---|
| Roadmap Item IDs | R-037 |
| Why | Confirms warning mode works without blocking and does not produce false-positive blocks on existing artifacts. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0040 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0040/evidence.md

**Deliverables:**
- Verification results confirming warning-only mode for cross-references

**Steps:**
1. **[PLANNING]** Identify existing artifacts that may contain cross-references
2. **[PLANNING]** Review T02.02 warning-only implementation
3. **[EXECUTION]** Run cross-reference validation against existing artifacts
4. **[EXECUTION]** Confirm warnings are emitted but pipeline is not blocked
5. **[VERIFICATION]** No false-positive blocks on existing artifacts
6. **[COMPLETION]** Document warning output examples

**Acceptance Criteria:**
- Verification results at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0040/evidence.md exist
- Warning mode emits warnings for invalid cross-references without blocking
- No false-positive blocks on existing artifacts in .dev/releases/complete/
- Warning output is actionable and identifies specific invalid references

**Validation:**
- Manual check: pipeline runs to completion with warnings (not blocks) for invalid refs
- Evidence: linkable artifact produced (verification results)

**Dependencies:** T02.02 (cross-reference fix)
**Rollback:** TBD

---

### T05.05 -- Measure Pipeline Performance Delta

| Field | Value |
|---|---|
| Roadmap Item IDs | R-038 |
| Why | SC-012 requires total pipeline time overhead <=5% excluding new spec-fidelity step. |
| Effort | M |
| Risk | Low |
| Risk Drivers | performance, pipeline |
| Tier | EXEMPT |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0041 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0041/notes.md

**Deliverables:**
- Pipeline performance delta report comparing before/after new gates

**Steps:**
1. **[PLANNING]** Establish baseline pipeline time (before v2.20 changes)
2. **[PLANNING]** Define measurement methodology excluding new spec-fidelity step
3. **[EXECUTION]** Run pipeline with new gates and measure total time
4. **[EXECUTION]** Calculate delta excluding spec-fidelity step time
5. **[VERIFICATION]** Verify overhead <=5% (SC-012)
6. **[COMPLETION]** Document baseline, measured, and delta values

**Acceptance Criteria:**
- Delta report at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0041/notes.md exists
- Report shows baseline time, new total time, and computed delta percentage
- Delta <=5% excluding spec-fidelity step (SC-012)
- Measurement methodology documented

**Validation:**
- Manual check: delta percentage calculated and compared against 5% threshold
- Evidence: linkable artifact produced (performance delta report)

**Dependencies:** T05.03 (integration run for timing data)
**Rollback:** TBD

---

### Checkpoint: Phase 5 / Tasks T05.01-T05.05

**Purpose:** Verify retrospective wiring and performance measurements are complete before documentation tasks.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P05-T01-T05.md

**Verification:**
- Retrospective parameter wiring passes all tests (SC-006)
- Full pipeline integration run succeeds against 3+ specs
- Pipeline performance delta <=5% excluding new step

**Exit Criteria:**
- D-0035 through D-0041 artifacts created
- No regressions in full test suite
- Cross-reference warning mode verified

---

### T05.06 -- Verify --no-validate Behavior for Fidelity Step

| Field | Value |
|---|---|
| Roadmap Item IDs | R-039 |
| Why | SC-014 requires that --no-validate does NOT skip the fidelity step. Expected behavior for all flag combinations must be documented. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0042 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0042/evidence.md

**Deliverables:**
- Verification results confirming --no-validate does not skip fidelity step

**Steps:**
1. **[PLANNING]** Review T03.03 pipeline step integration for --no-validate handling
2. **[PLANNING]** Identify all skip/validate flag combinations
3. **[EXECUTION]** Test pipeline with --no-validate flag; confirm fidelity step executes
4. **[EXECUTION]** Document expected behavior for all flag combinations
5. **[VERIFICATION]** SC-014 verified: fidelity step runs despite --no-validate
6. **[COMPLETION]** Record flag combination matrix

**Acceptance Criteria:**
- Verification results at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0042/evidence.md exist
- --no-validate flag does NOT skip spec-fidelity step (SC-014)
- Flag combination matrix documents all skip/validate scenarios
- Behavior is consistent across repeated runs

**Validation:**
- Manual check: pipeline with --no-validate includes fidelity step in execution
- Evidence: linkable artifact produced (flag behavior verification)

**Dependencies:** T03.03 (pipeline step integration)
**Rollback:** TBD

---

### T05.07 -- Replay Historical Artifacts Against Stricter Gates

| Field | Value |
|---|---|
| Roadmap Item IDs | R-040 |
| Why | NFR-004/NFR-006 require replaying historical artifacts to validate that stricter gates do not cause unexpected regressions before production rollout. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | migration (historical artifact replay) |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0043 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0043/evidence.md

**Deliverables:**
- Historical artifact replay results with failure reasons per artifact for migration planning

**Steps:**
1. **[PLANNING]** Identify all historical artifacts in .dev/releases/complete/
2. **[PLANNING]** Configure stricter gates (STRICT REFLECT_GATE, cross-reference validation)
3. **[EXECUTION]** Replay each artifact against new gate configurations
4. **[EXECUTION]** Document failure reasons per artifact with specific gate and check that failed
5. **[VERIFICATION]** Categorize failures: expected (artifact quality issue) vs unexpected (gate bug)
6. **[COMPLETION]** Produce migration planning recommendations

**Acceptance Criteria:**
- Replay results at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0043/evidence.md exist
- Each artifact has pass/fail status with specific failure reason if applicable
- Failures categorized as expected vs unexpected
- Migration planning recommendations included

**Validation:**
- Manual check: all artifacts in .dev/releases/complete/ covered in replay
- Evidence: linkable artifact produced (replay results with failure analysis)

**Dependencies:** T02.01 (REFLECT_GATE promotion), T02.02 (cross-reference fix)
**Rollback:** TBD

---

### T05.08 -- Document Degraded-State Semantics

| Field | Value |
|---|---|
| Roadmap Item IDs | R-041 |
| Why | Team must distinguish clean pass, fail, skipped, and degraded states to correctly interpret pipeline output. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [█████████░] 90% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0044 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0044/spec.md

**Deliverables:**
- Document defining failure-state semantics for all fidelity status values

**Steps:**
1. **[PLANNING]** Review T03.04 state persistence implementation for status values
2. **[PLANNING]** Identify all status values: pass, fail, skipped, degraded
3. **[EXECUTION]** Document each status with definition, trigger conditions, and user action
4. **[EXECUTION]** Include examples of each state from real pipeline scenarios
5. **[VERIFICATION]** Confirm all states are distinguishable by inspection
6. **[COMPLETION]** Cross-reference with operational guidance (T05.13)

**Acceptance Criteria:**
- Semantics document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0044/spec.md exists
- All 4 status values (pass, fail, skipped, degraded) defined with trigger conditions
- Each status includes recommended user action
- States are visually distinguishable in pipeline output

**Validation:**
- Manual check: 4 status values defined with clear distinctions
- Evidence: linkable artifact produced (semantics document)

**Dependencies:** T03.04 (state persistence implementation)
**Rollback:** TBD

---

### T05.09 -- Define Monitoring Metrics and Rollback Triggers

| Field | Value |
|---|---|
| Roadmap Item IDs | R-042, R-043 |
| Why | Production rollout requires defined monitoring metrics and rollback triggers to detect and recover from gate strictness regressions. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | rollback, pipeline |
| Tier | EXEMPT |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0045, D-0046 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0045/spec.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0046/spec.md

**Deliverables:**
- Monitoring metrics definition: false positive rate, degraded-run frequency, pipeline time drift, LLM severity drift
- Rollback plan with trigger thresholds, drill procedure, and evidence capture for gate strictness changes

**Steps:**
1. **[PLANNING]** Review roadmap risk register for monitoring-relevant risks
2. **[PLANNING]** Identify rollback scenarios from RSK-003, RSK-006, RSK-007
3. **[EXECUTION]** Define monitoring metrics with measurement methods and alert thresholds
4. **[EXECUTION]** Write rollback plan with step-by-step procedure for gate strictness reversion
5. **[EXECUTION]** Define rollback trigger thresholds and execute a rollback drill or dry-run simulation
6. **[EXECUTION]** Record expected vs observed rollback results and store evidence artifact paths
7. **[VERIFICATION]** Confirm rollback plan covers all new gates introduced in v2.20 and is exercised in drill/simulation
8. **[COMPLETION]** Cross-reference with operational guidance document

**Acceptance Criteria:**
- Metrics document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0045/spec.md defines 4 metrics
- Rollback plan at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0046/spec.md has step-by-step procedure
- Rollback triggers have numeric thresholds (e.g., false positive rate > X%)
- Rollback procedure is exercised in a drill or dry-run simulation with results documented
- Evidence paths for rollback drill outputs are recorded
- Plan covers REFLECT_GATE, SPEC_FIDELITY_GATE, and TASKLIST_FIDELITY_GATE

**Validation:**
- Manual check: 4 metrics defined; rollback plan has numbered steps; rollback drill or dry-run results are documented
- Evidence: linkable artifacts produced (metrics definition, rollback plan, and rollback drill evidence)

**Dependencies:** T05.03 (integration run baseline data), T05.07 (replay results)
**Rollback:** TBD

---

### T05.10 -- Update PLANNING.md Pipeline Documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-044 |
| Why | PLANNING.md must reflect new pipeline step documentation including spec-fidelity step and gate ordering. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0047 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0047/notes.md

**Deliverables:**
- Updated PLANNING.md with new pipeline step documentation

**Steps:**
1. **[PLANNING]** Read current PLANNING.md pipeline section
2. **[PLANNING]** Identify sections needing update for spec-fidelity step
3. **[EXECUTION]** Add spec-fidelity step to pipeline documentation with gate ordering
4. **[EXECUTION]** Document step position (after reflect), timeout (600s), and --no-validate behavior
5. **[VERIFICATION]** Confirm documentation matches implementation
6. **[COMPLETION]** Record changes made

**Acceptance Criteria:**
- PLANNING.md contains documentation for spec-fidelity pipeline step
- Step ordering documented: reflect → spec-fidelity
- Timeout (600s) and retry behavior documented
- --no-validate behavior documented

**Validation:**
- Manual check: PLANNING.md pipeline section includes spec-fidelity step
- Evidence: linkable artifact noting changes made

**Dependencies:** Phase 3 complete (pipeline step implemented)
**Rollback:** Revert PLANNING.md changes

---

### Checkpoint: Phase 5 / Tasks T05.06-T05.10

**Purpose:** Verify verification tasks and documentation updates are complete before remaining documentation.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P05-T06-T10.md

**Verification:**
- --no-validate behavior verified (SC-014)
- Historical artifact replay completed with categorized results
- Monitoring metrics and rollback plan documented

**Exit Criteria:**
- D-0042 through D-0047 artifacts created
- PLANNING.md updated with pipeline documentation
- Rollback plan covers all 3 new gates

---

### T05.11 -- Update CLI Help Text for New Subcommands

| Field | Value |
|---|---|
| Roadmap Item IDs | R-045 |
| Why | New CLI subcommands and flags need accurate help text for user discoverability. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | STANDARD |
| Confidence | [███████░░░] 70% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0048 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0048/evidence.md

**Deliverables:**
- Updated CLI help text for tasklist validate and roadmap run --retrospective

**Steps:**
1. **[PLANNING]** Review current CLI help text structure
2. **[PLANNING]** Identify all new subcommands and flags from Phases 3-4
3. **[EXECUTION]** Update help text for `superclaude tasklist validate` with all options
4. **[EXECUTION]** Update help text for `superclaude roadmap run --retrospective`
5. **[VERIFICATION]** `superclaude tasklist validate --help` and `superclaude roadmap run --help` render correctly
6. **[COMPLETION]** Verify help text matches implementation

**Acceptance Criteria:**
- `superclaude tasklist validate --help` renders with all options documented
- `superclaude roadmap run --help` includes --retrospective flag
- Help text descriptions match actual command behavior
- No missing or outdated option descriptions

**Validation:**
- `superclaude tasklist validate --help` — renders correctly
- Evidence: help text output captured

**Dependencies:** T04.03 (CLI subcommand), T05.01 (retrospective flag)
**Rollback:** Revert help text changes

---

### T05.12 -- Finalize Deviation Format Reference Document

| Field | Value |
|---|---|
| Roadmap Item IDs | R-046 |
| Why | FR-026 requires the deviation format reference document to be finalized and reviewed as the canonical contract. |
| Effort | XS |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0049 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0049/spec.md

**Deliverables:**
- Finalized docs/reference/deviation-report-format.md after review

**Steps:**
1. **[PLANNING]** Read current docs/reference/deviation-report-format.md from T02.04
2. **[PLANNING]** Compare against FidelityDeviation dataclass from T02.06 for consistency
3. **[EXECUTION]** Update document with any corrections from implementation experience
4. **[EXECUTION]** Add version tag and review status
5. **[VERIFICATION]** Confirm 7-column schema matches dataclass fields exactly
6. **[COMPLETION]** Mark document as finalized

**Acceptance Criteria:**
- docs/reference/deviation-report-format.md is updated and marked as finalized
- Schema matches FidelityDeviation dataclass fields exactly
- Document has version tag and review date
- All downstream consumers reference this as canonical contract

**Validation:**
- Manual check: schema columns match dataclass fields 1:1
- Evidence: linkable artifact noting finalization status

**Dependencies:** T02.04 (initial format spec), T02.06 (dataclass implementation)
**Rollback:** TBD

---

### T05.13 -- Write Operational Guidance Documentation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-047 |
| Why | Users need to understand fidelity status meanings, expected output artifacts, and how to interpret pipeline results. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [█████████░] 88% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0050 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0050/spec.md

**Deliverables:**
- Operational guidance document with fidelity status meanings, artifact descriptions, and state examples

**Steps:**
1. **[PLANNING]** Review T05.08 degraded-state semantics document
2. **[PLANNING]** Identify all output artifacts produced by new pipeline steps
3. **[EXECUTION]** Write operational guidance covering status meanings and expected artifacts
4. **[EXECUTION]** Include examples of each fidelity status state (pass, fail, skipped, degraded)
5. **[VERIFICATION]** Confirm guidance is consistent with implementation behavior
6. **[COMPLETION]** Cross-reference with PLANNING.md updates

**Acceptance Criteria:**
- Operational guidance at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0050/spec.md exists
- All fidelity status values documented with examples
- Expected output artifacts listed with locations
- Guidance is actionable for users unfamiliar with v2.20 changes

**Validation:**
- Manual check: document covers all 4 status states with examples
- Evidence: linkable artifact produced (operational guidance)

**Dependencies:** T05.08 (degraded-state semantics)
**Rollback:** TBD

---

### T05.14 -- Execute Output Phase 5 Validation Suite

| Field | Value |
|---|---|
| Roadmap Item IDs | R-048, R-049 |
| Why | SC-006, SC-010, SC-012 must be verified. All 14 success criteria must be passing. No test regressions. |
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
| Deliverable IDs | D-0051 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0051/evidence.md

**Deliverables:**
- Phase 5 test results verifying SC-006, SC-010, SC-012 and all 14 success criteria

**Steps:**
1. **[PLANNING]** List all 14 SC criteria and their test mappings
2. **[PLANNING]** Prepare test data for retrospective wiring tests
3. **[EXECUTION]** Run `uv run pytest tests/ -v` for full suite
4. **[EXECUTION]** Verify SC-006 (retrospective reaches extraction), SC-010 (no regression), SC-012 (pipeline overhead)
5. **[EXECUTION]** Walk through all 14 SC criteria with pass/fail evidence
6. **[VERIFICATION]** `uv run pytest tests/ -v` exits 0 with 0 failures
7. **[COMPLETION]** Record SC verification matrix with all 14 criteria

**Acceptance Criteria:**
- `uv run pytest tests/ -v` exits 0 with 0 failures
- SC-006, SC-010, SC-012 individually verified with evidence
- All 14 success criteria have pass/fail status documented
- No test regressions across entire suite

**Validation:**
- `uv run pytest tests/ -v` — 0 failures
- Evidence: complete SC verification matrix

**Dependencies:** T05.01-T05.13 (all Phase 5 tasks)
**Rollback:** TBD

---

### Checkpoint: End of Phase 5

**Purpose:** Confirm all integration hardening, documentation, and success criteria are complete before release readiness.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P05-END.md

**Verification:**
- All 14 SC criteria passing with documented evidence
- All documentation updated (PLANNING.md, CLI help, operational guidance, deviation format)
- Historical artifact replay completed with migration plan

**Exit Criteria:**
- All D-0035 through D-0051 artifacts created
- Monitoring metrics defined and rollback plan documented and tested
- Team can distinguish clean pass, fail, skipped, and degraded states
