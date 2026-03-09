# Phase 2 -- Foundation

Fix broken gates, define the canonical deviation report format, and establish the testing baseline. This phase addresses the two highest-impact risks (RSK-003 cross-reference breakage, RSK-006 REFLECT_GATE promotion breakage) before building new features. All existing tests must pass before and after changes.

### T02.01 -- Promote REFLECT_GATE from STANDARD to STRICT

| Field | Value |
|---|---|
| Roadmap Item IDs | R-010 |
| Why | REFLECT_GATE currently runs at STANDARD tier, allowing structural validation failures to pass. Promoting to STRICT ensures semantic checks execute and block on failure. |
| Effort | S |
| Risk | Medium |
| Risk Drivers | breaking (blast radius on existing artifacts per RSK-006) |
| Tier | STANDARD |
| Confidence | [███████░░░] 72% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0011, D-0012 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0011/evidence.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0012/notes.md

**Deliverables:**
- REFLECT_GATE enforcement tier changed to STRICT in src/superclaude/cli/roadmap/validate_gates.py
- Blast radius assessment report from running against .dev/releases/complete/ artifacts

**Steps:**
1. **[PLANNING]** Read current REFLECT_GATE configuration in src/superclaude/cli/roadmap/validate_gates.py
2. **[PLANNING]** Identify all tests referencing REFLECT_GATE behavior
3. **[EXECUTION]** Run pre-change regression baseline against existing roadmap tests and record results before modifying gate enforcement
4. **[EXECUTION]** Change REFLECT_GATE enforcement tier from STANDARD to STRICT
5. **[EXECUTION]** Run gate against existing validation artifacts in .dev/releases/complete/ to assess blast radius
6. **[EXECUTION]** Update existing tests to expect STRICT behavior
7. **[VERIFICATION]** `uv run pytest tests/roadmap/ -v` exits 0
8. **[COMPLETION]** Document baseline results, blast radius findings, and any artifact failures

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_gates.py -k "test_reflect_gate_is_strict or test_reflect_gate_semantic_checks_execute" -v` exits 0 with named roadmap REFLECT tests passing
- Pre-change regression baseline for `uv run pytest tests/roadmap/ -v` is recorded before tier modification
- Blast radius assessment documents which existing artifacts pass/fail under STRICT
- No regressions in existing test suite (`uv run pytest tests/roadmap/` exits 0)
- Evidence document records exact failure count and artifact names

**Validation:**
- `uv run pytest tests/roadmap/ -v` — 0 failures
- Evidence: blast radius assessment report produced

**Dependencies:** T01.09 (decision log complete)
**Rollback:** Revert validate_gates.py tier change from STRICT back to STANDARD
**Notes:** RSK-006 mitigation: test against .dev/releases/complete/ artifacts before merging.

---

### T02.02 -- Fix Cross-Reference Resolution in _cross_refs_resolve()

| Field | Value |
|---|---|
| Roadmap Item IDs | R-011 |
| Why | _cross_refs_resolve() currently contains an always-True stub that never validates heading anchors, allowing dangling references to pass undetected. |
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
| Deliverable IDs | D-0013 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0013/evidence.md

**Deliverables:**
- Replacement implementation of _cross_refs_resolve() with actual heading-anchor validation, warning-only mode

**Steps:**
1. **[PLANNING]** Read current _cross_refs_resolve() stub in src/superclaude/cli/roadmap/ module
2. **[PLANNING]** Review OQ-001 decision (warning-only initially per T01.01)
3. **[EXECUTION]** Replace always-True stub with heading-anchor validation logic
4. **[EXECUTION]** Implement as warning-only (log invalid references, do not block)
5. **[VERIFICATION]** `uv run pytest tests/roadmap/test_gates.py -k cross_ref` exits 0
6. **[COMPLETION]** Document implementation approach and warning behavior

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_gates.py -k cross_ref` exits 0 with validation tests passing
- _cross_refs_resolve() correctly rejects dangling references (returns False or warning)
- Warning-only mode: invalid cross-references log warnings but do not block pipeline
- No regressions in existing test suite

**Validation:**
- `uv run pytest tests/roadmap/ -v` — 0 failures
- Evidence: test output showing warning-only behavior for invalid cross-references

**Dependencies:** T01.01 (OQ-001 decision for warning-only mode)
**Rollback:** Revert _cross_refs_resolve() to previous stub

---

### T02.03 -- Add Cross-Reference Unit Tests

| Field | Value |
|---|---|
| Roadmap Item IDs | R-012 |
| Why | FR-020 requires unit tests covering valid references, invalid references, and documents with no references. |
| Effort | XS |
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
| Deliverable IDs | D-0014 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0014/evidence.md

**Deliverables:**
- Unit tests: test_cross_refs_resolve_valid, test_cross_refs_resolve_invalid, test_cross_refs_resolve_no_refs

**Steps:**
1. **[PLANNING]** Review _cross_refs_resolve() interface from T02.02
2. **[PLANNING]** Design test cases for valid, invalid, and no-reference scenarios
3. **[EXECUTION]** Write test_cross_refs_resolve_valid in tests/roadmap/test_gates.py
4. **[EXECUTION]** Write test_cross_refs_resolve_invalid and test_cross_refs_resolve_no_refs
5. **[VERIFICATION]** `uv run pytest tests/roadmap/test_gates.py -k cross_refs_resolve -v` exits 0
6. **[COMPLETION]** Verify all 3 test functions pass

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_gates.py -k cross_refs_resolve -v` exits 0 with 3 tests passing
- Tests cover: valid heading anchors (pass), dangling references (warning), no references (pass)
- Test names match roadmap specification exactly
- Tests are in tests/roadmap/test_gates.py

**Validation:**
- `uv run pytest tests/roadmap/test_gates.py -k cross_refs_resolve -v` — 3 tests pass
- Evidence: test output log

**Dependencies:** T02.02 (_cross_refs_resolve() implementation)
**Rollback:** Remove added test functions

---

### T02.04 -- Create Deviation Report Format Specification

| Field | Value |
|---|---|
| Roadmap Item IDs | R-013 |
| Why | FR-021/FR-026 require a canonical format specification document for the 7-column deviation report consumed by all downstream gates and CLI. |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0015 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0015/spec.md

**Deliverables:**
- docs/reference/deviation-report-format.md documenting the 7-column schema as canonical contract

**Steps:**
1. **[PLANNING]** Review OQ-006 decision from T01.03 for schema details
2. **[PLANNING]** Identify all downstream consumers (gates, CLI, reports)
3. **[EXECUTION]** Create docs/reference/deviation-report-format.md with 7-column schema definition
4. **[EXECUTION]** Include column names, types, constraints, and example rows
5. **[VERIFICATION]** Confirm schema matches OQ-006 decision exactly
6. **[COMPLETION]** Cross-reference with FidelityDeviation dataclass (T02.06)

**Acceptance Criteria:**
- File docs/reference/deviation-report-format.md exists with 7-column schema
- Schema uses generic Upstream Quote/Downstream Quote column names per OQ-006
- Document includes column definitions, data types, and at least one example row
- Document is marked as canonical contract for all consumers

**Validation:**
- Manual check: document has exactly 7 columns matching OQ-006 schema decision
- Evidence: linkable artifact produced (format specification document)

**Dependencies:** T01.03 (OQ-006 schema decision)
**Rollback:** Remove docs/reference/deviation-report-format.md

---

### T02.05 -- Define Severity Classification with Examples

| Field | Value |
|---|---|
| Roadmap Item IDs | R-014 |
| Why | FR-022/FR-023 require concrete severity classification definitions with boundary cases to reduce LLM classification drift (RSK-007). |
| Effort | S |
| Risk | Low |
| Risk Drivers | none |
| Tier | EXEMPT |
| Confidence | [████████░░] 82% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Skip verification |
| MCP Requirements | None |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0016 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0016/spec.md

**Deliverables:**
- Severity classification document defining HIGH/MEDIUM/LOW with concrete examples and boundary cases

**Steps:**
1. **[PLANNING]** Review FR-022, FR-023, and RSK-007 requirements
2. **[PLANNING]** Identify boundary cases between severity levels
3. **[EXECUTION]** Define HIGH severity: missing functional requirements, broken contracts, security gaps
4. **[EXECUTION]** Define MEDIUM and LOW severities with examples; document boundary cases
5. **[VERIFICATION]** Confirm examples are unambiguous and cover typical LLM output patterns
6. **[COMPLETION]** Cross-reference with prompt builder requirements (T03.01)

**Acceptance Criteria:**
- Severity document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0016/spec.md exists
- Each severity level (HIGH/MEDIUM/LOW) has at least 2 concrete examples
- Boundary cases between adjacent levels are explicitly addressed
- Classification rationale is embedded for prompt reuse per RSK-007

**Validation:**
- Manual check: 3 severity levels defined with examples and boundary cases
- Evidence: linkable artifact produced (severity classification document)

**Dependencies:** T01.07 (OQ-005 MEDIUM severity blocking policy)
**Rollback:** Remove severity classification document

---

### Checkpoint: Phase 2 / Tasks T02.01-T02.05

**Purpose:** Verify gate fixes and specification documents are complete before implementing code artifacts.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P02-T02-01-T02-05.md

**Verification:**
- REFLECT_GATE promotion and cross-reference fix pass all tests
- Deviation report format and severity classification documents exist and are consistent
- No test regressions from gate modifications

**Exit Criteria:**
- `uv run pytest tests/roadmap/ -v` exits 0 with no regressions
- D-0011 through D-0016 artifacts created
- Blast radius assessment for REFLECT_GATE promotion documented

---

### T02.06 -- Create FidelityDeviation Dataclass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-015 |
| Why | FR-031 requires a programmatic representation of the 7-column deviation schema for use in gates, prompts, and CLI output. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | data (schema, dataclass, model) |
| Tier | STRICT |
| Confidence | [████████░░] 78% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0017 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0017/evidence.md

**Deliverables:**
- FidelityDeviation dataclass in src/superclaude/cli/roadmap/fidelity.py implementing 7-column schema

**Steps:**
1. **[PLANNING]** Read deviation report format specification from T02.04
2. **[PLANNING]** Identify Python dataclass field types for each of the 7 columns
3. **[EXECUTION]** Create src/superclaude/cli/roadmap/fidelity.py with FidelityDeviation dataclass
4. **[EXECUTION]** Implement validation logic (severity enum, required fields, type constraints)
5. **[EXECUTION]** Add unit test test_fidelity_deviation_dataclass in tests/roadmap/test_fidelity.py
6. **[VERIFICATION]** `uv run pytest tests/roadmap/test_fidelity.py -v` exits 0
7. **[COMPLETION]** Document dataclass fields and usage patterns

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_fidelity.py -k fidelity_deviation -v` exits 0
- FidelityDeviation dataclass has fields matching all 7 columns of the canonical schema
- Invalid severity values raise validation errors (test_fidelity_deviation_invalid_severity)
- Dataclass is importable from src/superclaude/cli/roadmap/fidelity module

**Validation:**
- `uv run pytest tests/roadmap/test_fidelity.py -v` — all tests pass
- Evidence: test output and code review notes

**Dependencies:** T02.04 (deviation format specification)
**Rollback:** Remove src/superclaude/cli/roadmap/fidelity.py and tests/roadmap/test_fidelity.py

---

### T02.07 -- Implement _high_severity_count_zero() Semantic Check

| Field | Value |
|---|---|
| Roadmap Item IDs | R-016 |
| Why | FR-024 requires a semantic check function that validates high_severity_count equals zero in fidelity report frontmatter. |
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
| Deliverable IDs | D-0018 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0018/evidence.md

**Deliverables:**
- _high_severity_count_zero() function in src/superclaude/cli/roadmap/gates.py with unit tests

**Steps:**
1. **[PLANNING]** Read current src/superclaude/cli/roadmap/gates.py structure
2. **[PLANNING]** Design function signature: accepts parsed frontmatter dict, returns bool
3. **[EXECUTION]** Implement _high_severity_count_zero() in roadmap/gates.py
4. **[EXECUTION]** Add tests: pass (count=0), fail (count>0), missing field
5. **[VERIFICATION]** `uv run pytest tests/roadmap/test_gates.py -k high_severity -v` exits 0
6. **[COMPLETION]** Document edge case handling (missing field, non-integer value)

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_gates.py -k high_severity -v` exits 0 with 3 tests passing
- Tests cover: count=0 (pass), count>0 (fail), missing high_severity_count field
- Function handles edge cases: missing field returns False, non-integer raises TypeError
- 100% branch coverage for _high_severity_count_zero()

**Validation:**
- `uv run pytest tests/roadmap/test_gates.py -k high_severity -v` — 3 tests pass
- Evidence: test output with branch coverage report

**Dependencies:** None (standalone utility function)
**Rollback:** Remove function and tests

---

### T02.08 -- Implement _tasklist_ready_consistent() Semantic Check

| Field | Value |
|---|---|
| Roadmap Item IDs | R-017 |
| Why | FR-025 requires a semantic check that validates tasklist_ready field is consistent with severity counts in fidelity report frontmatter. |
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
| Deliverable IDs | D-0019 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0019/evidence.md

**Deliverables:**
- _tasklist_ready_consistent() function in src/superclaude/cli/roadmap/gates.py with unit tests

**Steps:**
1. **[PLANNING]** Read _high_severity_count_zero() implementation for pattern consistency
2. **[PLANNING]** Design consistency logic: tasklist_ready=true requires high_severity_count=0
3. **[EXECUTION]** Implement _tasklist_ready_consistent() in roadmap/gates.py
4. **[EXECUTION]** Add tests: consistent (pass), inconsistent (fail), missing fields
5. **[VERIFICATION]** `uv run pytest tests/roadmap/test_gates.py -k tasklist_ready -v` exits 0
6. **[COMPLETION]** Document consistency rules

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/test_gates.py -k tasklist_ready -v` exits 0 with pass/fail tests
- Function detects inconsistency: tasklist_ready=true but high_severity_count>0
- Edge cases handled: missing tasklist_ready field, missing severity count
- 100% branch coverage for _tasklist_ready_consistent()

**Validation:**
- `uv run pytest tests/roadmap/test_gates.py -k tasklist_ready -v` — tests pass
- Evidence: test output with branch coverage report

**Dependencies:** T02.07 (_high_severity_count_zero pattern)
**Rollback:** Remove function and tests

---

### T02.09 -- Confirm OQ-002 and OQ-003 Resolutions as Exit Criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-018 |
| Why | AC-006 and NFR-006 require that module placement and count cross-validation decisions are formally confirmed as Phase 2 exit criteria. |
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
| Deliverable IDs | D-0020 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0020/notes.md

**Deliverables:**
- Confirmation entry in decision log recording OQ-002/OQ-003 as formally resolved

**Steps:**
1. **[PLANNING]** Review T01.05 (OQ-002) and T01.06 (OQ-003) decisions
2. **[PLANNING]** Verify decisions are still valid after Phase 2 implementation
3. **[EXECUTION]** Add confirmation entries to decision log
4. **[EXECUTION]** Record that cli/tasklist/ module path is confirmed and count cross-validation is warning-only
5. **[VERIFICATION]** Confirm no implementation contradicts these decisions
6. **[COMPLETION]** Mark OQ-002 and OQ-003 as formally closed

**Acceptance Criteria:**
- Confirmation note at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0020/notes.md exists
- OQ-002 (cli/tasklist/ module) confirmed with AC-006 reference
- OQ-003 (count cross-validation as warning) confirmed with NFR-006 reference
- Decision log updated with closure entries

**Validation:**
- Manual check: decision log has closure entries for OQ-002 and OQ-003
- Evidence: linkable artifact produced (confirmation notes)

**Dependencies:** T01.05, T01.06 (original decisions)
**Rollback:** TBD

---

### T02.10 -- Execute Phase 2 Test Suite and Regression Validation

| Field | Value |
|---|---|
| Roadmap Item IDs | R-019, R-020 |
| Why | SC-010 requires 0 regressions in existing test suite. All gate fixes and new functions must pass before proceeding. |
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
| Deliverable IDs | D-0021 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0021/evidence.md

**Deliverables:**
- Full test suite results showing 0 failures across all roadmap tests

**Steps:**
1. **[PLANNING]** Identify all test files modified or added in Phase 2
2. **[PLANNING]** Verify test markers and organization follow project conventions
3. **[EXECUTION]** Run `uv run pytest tests/roadmap/ -v` and capture output
4. **[EXECUTION]** Verify integration test test_cross_refs_resolve_in_merge_gate passes
5. **[VERIFICATION]** `uv run pytest tests/roadmap/ -v` exits 0 with 0 failures
6. **[COMPLETION]** Record test counts and any warnings in evidence document

**Acceptance Criteria:**
- `uv run pytest tests/roadmap/ -v` exits 0 with 0 failures (SC-010)
- All new tests from Phase 2 (cross-refs, semantic checks, fidelity dataclass) pass
- Integration test test_cross_refs_resolve_in_merge_gate passes
- No new test framework or executor introduced (NFR-006 compliance)

**Validation:**
- `uv run pytest tests/roadmap/ -v` — 0 failures
- Evidence: complete test output log

**Dependencies:** T02.01-T02.09 (all Phase 2 tasks)
**Rollback:** TBD

---

### Checkpoint: End of Phase 2

**Purpose:** Confirm all gate fixes, format specifications, and code artifacts are complete with full test coverage.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P02-END.md

**Verification:**
- `uv run pytest tests/roadmap/ -v` exits 0 with 0 failures
- All specification documents (deviation format, severity classification) exist and are consistent
- FidelityDeviation dataclass, _high_severity_count_zero(), and _tasklist_ready_consistent() all have tests passing

**Exit Criteria:**
- All D-0011 through D-0021 artifacts created
- All existing tests pass with no regressions from any output Phase 2 changes (SC-010)
- _cross_refs_resolve() correctly rejects dangling references
- Semantic checks have 100% branch coverage
- Deviation format reference document exists and is linkable
- OQ-002 and OQ-003 formally confirmed and closed in decision log
- No new executor or process framework introduced
