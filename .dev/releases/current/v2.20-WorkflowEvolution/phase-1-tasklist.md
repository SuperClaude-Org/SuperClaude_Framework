# Phase 1 -- Pre-Implementation Decisions

Resolve all 8 open questions before implementation begins. Each decision must be documented with rationale, impacts, and explicit downstream implementation implications. The roadmap provides concrete recommendations for each question; this phase validates and records those decisions in a canonical decision log.

### T01.01 -- Resolve OQ-001 Cross-Reference Strictness Rollout

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | Cross-reference enforcement strategy determines whether invalid cross-references block the pipeline or warn. Warning-first de-risks RSK-003. |
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
| Deliverable IDs | D-0001 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0001/spec.md

**Deliverables:**
- Written decision documenting warning-first rollout for one release, then blocking enforcement

**Steps:**
1. **[PLANNING]** Review OQ-001 description and RSK-003 risk entry in roadmap
2. **[PLANNING]** Identify downstream impacts on existing artifacts in .dev/releases/complete/
3. **[EXECUTION]** Document decision: warning-first for one release, then blocking
4. **[EXECUTION]** Record rationale and link to RSK-003 mitigation
5. **[VERIFICATION]** Confirm decision is unambiguous and actionable
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0001/spec.md exists with rollout strategy
- Decision specifies warning-first duration (one release cycle)
- Decision is consistent with RSK-003 mitigation strategy in roadmap
- Decision log entry references OQ-001 and FR-019

**Validation:**
- Manual check: decision document contains explicit rollout phases (warning → blocking)
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD
**Notes:** Roadmap recommends warning-first for one release, then blocking.

---

### T01.02 -- Resolve OQ-004 Fidelity vs Reflect Step Ordering

| Field | Value |
|---|---|
| Roadmap Item IDs | R-002 |
| Why | Determines pipeline step ordering: whether spec-fidelity runs before or after reflect. Ordering affects validation semantics. |
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
| Deliverable IDs | D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0002/spec.md

**Deliverables:**
- Written decision documenting spec-fidelity runs after reflect step

**Steps:**
1. **[PLANNING]** Review OQ-004 description and pipeline step sequence in roadmap
2. **[PLANNING]** Assess whether reflect and fidelity are complementary or redundant
3. **[EXECUTION]** Document decision: spec-fidelity runs after reflect
4. **[EXECUTION]** Record rationale: reflect validates structural quality, fidelity validates content accuracy
5. **[VERIFICATION]** Confirm ordering is consistent with pipeline executor design
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0002/spec.md exists with step ordering
- Decision explicitly states reflect → spec-fidelity ordering
- Rationale distinguishes structural validation from content validation
- Decision log entry references OQ-004 and FR-008

**Validation:**
- Manual check: decision document specifies unambiguous pipeline step order
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD

---

### T01.03 -- Resolve OQ-006 Deviation Table Schema

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003 |
| Why | Defines the canonical 7-column deviation report schema used by all downstream consumers including gates and CLI. |
| Effort | S |
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
| Deliverable IDs | D-0003 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0003/spec.md

**Deliverables:**
- Written decision documenting 7-column FR-051.4 schema with generic column names

**Steps:**
1. **[PLANNING]** Review OQ-006 and FR-051.4 schema requirements
2. **[PLANNING]** Confirm column names: generic Upstream Quote/Downstream Quote
3. **[EXECUTION]** Document decision: 7-column schema, drop Source Pair column, encode in frontmatter
4. **[EXECUTION]** Specify column definitions and data types for each column
5. **[VERIFICATION]** Confirm schema is parseable and unambiguous
6. **[COMPLETION]** Add entry to decision log; cross-reference with FR-051.4 as the schema anchor and FR-026 for downstream finalization consistency

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0003/spec.md exists with 7-column schema
- Schema uses generic Upstream Quote/Downstream Quote column names
- Source Pair column explicitly excluded with frontmatter encoding noted
- Decision log entry references OQ-006, FR-051.4, and FR-026

**Validation:**
- Manual check: schema definition has exactly 7 columns with names and types
- Evidence: linkable artifact produced (schema specification document)

**Dependencies:** None
**Rollback:** TBD

---

### T01.04 -- Resolve OQ-007 Multi-Agent Mode Deferral

| Field | Value |
|---|---|
| Roadmap Item IDs | R-004 |
| Why | Determines whether multi-agent severity resolution is implemented in v2.20 or deferred. Affects scope and complexity. |
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
| Deliverable IDs | D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0004/spec.md

**Deliverables:**
- Written decision deferring FR-012 multi-agent implementation to v2.21

**Steps:**
1. **[PLANNING]** Review OQ-007 and FR-012 requirements
2. **[PLANNING]** Assess impact of deferral on v2.20 scope
3. **[EXECUTION]** Document decision: defer to v2.21, document conservative merge protocol only
4. **[EXECUTION]** Record protocol: highest severity wins, validation_complete: false if any agent fails
5. **[VERIFICATION]** Confirm no partial implementation leaks into v2.20
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0004/spec.md exists with deferral decision
- Conservative merge protocol documented (highest severity wins)
- Explicit statement that no FR-012 implementation occurs in v2.20
- Decision log entry references OQ-007 and FR-012

**Validation:**
- Manual check: decision explicitly states "deferred to v2.21"
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD

---

### T01.05 -- Resolve OQ-002 Module Placement

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005 |
| Why | Determines where tasklist validation code lives. Affects import paths, CLI registration, and module boundaries. |
| Effort | S |
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
| Deliverable IDs | D-0005 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0005/spec.md

**Deliverables:**
- Written decision establishing cli/tasklist/ as the new module location

**Steps:**
1. **[PLANNING]** Review OQ-002 and AC-006 requirements
2. **[PLANNING]** Assess import path and CLI registration implications
3. **[EXECUTION]** Document decision: src/superclaude/cli/tasklist/ as new module
4. **[EXECUTION]** Specify expected files: __init__.py, commands.py, executor.py, gates.py, prompts.py
5. **[VERIFICATION]** Confirm module path is consistent with existing cli/ structure
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0005/spec.md exists with module placement
- Module path src/superclaude/cli/tasklist/ specified with file listing
- Import path implications documented
- Decision log entry references OQ-002 and AC-006

**Validation:**
- Manual check: module path follows existing cli/ directory conventions
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.05

**Purpose:** Verify first 5 decision tasks are documented and consistent.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P01-T01-T05.md

**Verification:**
- All 5 decision documents exist with non-empty content
- No contradictions between decisions (e.g., module placement vs schema location)
- Each decision references its OQ identifier and relevant FR/AC codes

**Exit Criteria:**
- D-0001 through D-0005 artifacts created
- Decision log contains entries for OQ-001, OQ-004, OQ-006, OQ-007, OQ-002
- No unresolved cross-references between decisions

---

### T01.06 -- Resolve OQ-003 Count Cross-Validation Policy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-006 |
| Why | Determines whether frontmatter-vs-table-row count mismatches block the pipeline or log warnings. |
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
| Deliverable IDs | D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0006/spec.md

**Deliverables:**
- Written decision implementing count cross-validation as warning log, not gate blocker

**Steps:**
1. **[PLANNING]** Review OQ-003 and NFR-006 requirements
2. **[PLANNING]** Assess impact on LLM inconsistency tracking
3. **[EXECUTION]** Document decision: warning log for count mismatches, not blocking
4. **[EXECUTION]** Record rationale: reduces silent LLM inconsistencies without false-positive blocks
5. **[VERIFICATION]** Confirm decision is consistent with existing gate framework
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0006/spec.md exists
- Decision specifies warning-only behavior for count mismatches
- Rationale links to LLM inconsistency reduction goal
- Decision log entry references OQ-003

**Validation:**
- Manual check: decision states "warning log" not "gate blocker"
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD

---

### T01.07 -- Resolve OQ-005 MEDIUM Severity Blocking Policy

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007 |
| Why | Determines whether MEDIUM-severity deviations block the pipeline in v2.20 or only HIGH-severity. |
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
| Deliverable IDs | D-0007 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0007/spec.md

**Deliverables:**
- Written decision: only HIGH-severity blocks in v2.20; MEDIUM logged non-blocking

**Steps:**
1. **[PLANNING]** Review OQ-005 and severity classification requirements
2. **[PLANNING]** Assess impact on gate blocking logic implementation
3. **[EXECUTION]** Document decision: HIGH blocks, MEDIUM logs non-blocking
4. **[EXECUTION]** Note that MEDIUM-blocks policy revisited in v2.21
5. **[VERIFICATION]** Confirm decision is consistent with gate design in Phase 3
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0007/spec.md exists
- Decision explicitly states HIGH=blocking, MEDIUM=non-blocking for v2.20
- v2.21 revisit noted as follow-up
- Decision log entry references OQ-005

**Validation:**
- Manual check: blocking policy is unambiguous (HIGH only)
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD

---

### T01.08 -- Resolve OQ-008 Step Timeout vs NFR Mismatch

| Field | Value |
|---|---|
| Roadmap Item IDs | R-008 |
| Why | Clarifies the distinction between 120s p95 performance target and 600s hard timeout to prevent implementation confusion. |
| Effort | S |
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
| Deliverable IDs | D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0008/spec.md

**Deliverables:**
- Written decision documenting 120s as p95 target and 600s as hard timeout with measurement timing

**Steps:**
1. **[PLANNING]** Review OQ-008 and NFR performance requirements
2. **[PLANNING]** Identify where 120s and 600s values are used in implementation
3. **[EXECUTION]** Document distinction: 120s = p95 performance target for NFR measurement, 600s = hard timeout
4. **[EXECUTION]** Specify measurement occurs during Phases 3-4, not only at the end
5. **[VERIFICATION]** Confirm both values are referenced consistently in roadmap
6. **[COMPLETION]** Add entry to decision log

**Acceptance Criteria:**
- Decision document at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0008/spec.md exists
- 120s and 600s values explicitly distinguished with their purposes
- Measurement timing specified (Phases 3-4)
- Decision log entry references OQ-008

**Validation:**
- Manual check: document distinguishes "performance target" from "hard timeout"
- Evidence: linkable artifact produced (decision document)

**Dependencies:** None
**Rollback:** TBD

---

### T01.09 -- Publish Decision Log and Canonical Schema

| Field | Value |
|---|---|
| Roadmap Item IDs | R-009 |
| Why | Consolidates all 8 decisions into a single decision log and publishes the canonical deviation report schema for downstream consumers. |
| Effort | S |
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
| Deliverable IDs | D-0009, D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0009/spec.md
- .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0010/spec.md

**Deliverables:**
- Published decision log containing all 8 OQ resolutions with rationale
- Canonical deviation report schema document (7-column format)

**Steps:**
1. **[PLANNING]** Collect all 8 decision documents from T01.01-T01.08
2. **[PLANNING]** Verify no contradictions or unresolved cross-references
3. **[EXECUTION]** Compile decision log with all 8 entries, each referencing its OQ and FR codes
4. **[EXECUTION]** Create canonical deviation report schema document with 7-column definition
5. **[VERIFICATION]** Confirm all 8 decisions present and schema is complete
6. **[COMPLETION]** Cross-reference decision log with the next output phase’s implementation entry and exit criteria

**Acceptance Criteria:**
- Decision log at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0009/spec.md contains all 8 OQ resolutions
- Canonical schema at .dev/releases/current/v2.20-WorkflowEvolution/artifacts/D-0010/spec.md has 7 columns defined
- No unresolved blockers remain for prompt, gate, or CLI design
- Each decision entry includes OQ ID, decision text, rationale, and impacted FRs

**Validation:**
- Manual check: decision log has exactly 8 entries; schema has exactly 7 columns
- Evidence: linkable artifacts produced (decision log and schema document)

**Dependencies:** T01.01, T01.02, T01.03, T01.04, T01.05, T01.06, T01.07, T01.08
**Rollback:** TBD

---

### Checkpoint: End of Phase 1

**Purpose:** Confirm all pre-implementation decisions are resolved and documented before code changes begin.
**Checkpoint Report Path:** .dev/releases/current/v2.20-WorkflowEvolution/checkpoints/CP-P01-END.md

**Verification:**
- Decision log contains all 8 OQ resolutions with rationale and FR cross-references
- Canonical deviation report schema is documented with 7 columns and clear definitions
- No unresolved blockers for the next output phase implementation work

**Exit Criteria:**
- All D-0001 through D-0010 artifacts exist and are non-empty
- No contradictions between decisions (verified by cross-reference audit)
- Phase 2 can begin without ambiguity in schema, module placement, or gate behavior
