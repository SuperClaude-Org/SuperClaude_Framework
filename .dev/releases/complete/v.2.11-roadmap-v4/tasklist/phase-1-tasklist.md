# Phase 1 -- Deliverable Decomposition and Schema Extension

Implement Proposal 4 (Implement/Verify pair decomposition) and extend the deliverable schema to support metadata attachments from subsequent analytical passes. This milestone establishes the structural contract that all downstream milestones build against. No analytical logic is introduced -- only the decomposition rule and the schema surface.

---

### T01.01 -- Implement extended deliverable schema with `kind` field and `metadata` attachment point

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001, R-002 |
| Why | The schema extension adds a `kind` field (six values: implement, verify, invariant_check, fmea_test, guard_test, contract_test) and a `metadata` attachment point that subsequent analytical passes (M2-M4) attach findings to. This is the structural foundation for all downstream enhancements. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | schema, multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0001, D-0002 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0001/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0002/evidence.md

**Deliverables:**
1. Extended deliverable schema definition with all six `kind` values enumerated, `metadata` defaulting to empty dict, ValueError on unknown `kind`, and backward-compatible defaulting of pre-extension deliverables to `implement` (D-0001)
2. Test suite: unknown `kind` raises ValueError, `metadata` defaults to empty dict, pre-extension deliverables default to `implement`, round-trip serialization preserves `kind` and `metadata`, existing roadmaps parse without error (D-0002)

**Steps:**
1. **[PLANNING]** Read existing deliverable schema in `src/superclaude/cli/roadmap/` to identify extension points for `kind` and `metadata` fields
2. **[PLANNING]** Identify all consumers of the deliverable schema to assess backward-compatibility impact
3. **[EXECUTION]** Add `kind` field with enum validation (implement, verify, invariant_check, fmea_test, guard_test, contract_test) and ValueError on unknown values
4. **[EXECUTION]** Add `metadata` field defaulting to empty dict with round-trip serialization support
5. **[EXECUTION]** Add backward-compatibility logic: deliverables without `kind` default to `implement`
6. **[VERIFICATION]** Run test suite covering all five acceptance scenarios via sub-agent quality-engineer
7. **[COMPLETION]** Document schema extension in spec artifact at D-0001 path; record test evidence at D-0002 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0001/spec.md` exists documenting the extended schema with all six `kind` values, `metadata` field behavior, and backward-compatibility rules
- All six `kind` values are validated; unknown values raise ValueError; no silent acceptance of invalid kinds
- Round-trip serialization (serialize -> deserialize) preserves `kind` and `metadata` fields identically
- Pre-extension deliverables (without `kind` field) parse successfully and default to `implement` without errors

**Validation:**
- Manual check: instantiate deliverable with each of the six `kind` values and one unknown value; verify correct behavior
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0002/evidence.md`

**Dependencies:** None
**Rollback:** Remove `kind` and `metadata` fields from schema; revert to pre-extension deliverable definition
**Notes:** Schema is the integration contract for M2-M4. R-002 risk: ID suffix scheme collision mitigated by corpus validation.

---

### T01.02 -- Implement decomposition rule splitting behavioral deliverables into Implement/Verify pairs

| Field | Value |
|---|---|
| Roadmap Item IDs | R-003, R-004 |
| Why | Every behavioral deliverable D.x becomes D.x.a (Implement) and D.x.b (Verify). The Verify deliverable targets internal correctness -- input domain boundaries, operand identity, post-condition assertions on internal state -- not just external behavior. |
| Effort | M |
| Risk | Low |
| Risk Drivers | multi-file |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0003, D-0004 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0003/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0004/evidence.md

**Deliverables:**
1. Decomposition function that expands behavioral deliverables into Implement (`.a`) / Verify (`.b`) pairs with correct ID suffixes, passing non-behavioral deliverables through unchanged, and skipping already-decomposed deliverables (D-0003)
2. Test suite: 3 behavioral -> 6 output, 2 behavioral + 1 doc -> 5 output, empty -> empty, already-decomposed not re-decomposed, Verify description references Implement deliverable by ID (D-0004)

**Steps:**
1. **[PLANNING]** Load deliverable schema from T01.01 output to use `kind` field for Implement/Verify pair marking
2. **[PLANNING]** Identify behavioral detection interface (consumed from T01.03) to determine split candidates
3. **[EXECUTION]** Implement decomposition function: for each behavioral deliverable D.x, emit D.x.a (kind=implement) and D.x.b (kind=verify)
4. **[EXECUTION]** Add idempotency guard: deliverables with IDs ending in `.a` or `.b` are not re-decomposed
5. **[EXECUTION]** Ensure Verify description cross-references the corresponding Implement deliverable by ID
6. **[VERIFICATION]** Run five-scenario test suite via sub-agent quality-engineer
7. **[COMPLETION]** Document decomposition rule in spec artifact at D-0003 path; record test evidence at D-0004 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0003/spec.md` exists documenting the decomposition function signature, ID suffix rules, and idempotency behavior
- 3 behavioral deliverables produce exactly 6 output deliverables (3 Implement + 3 Verify pairs) with correct `.a`/`.b` ID suffixes
- Already-decomposed deliverables (IDs ending in `.a` or `.b`) pass through without re-decomposition
- Non-behavioral deliverables pass through unchanged with original IDs preserved

**Validation:**
- Manual check: pass 3 behavioral + 1 doc deliverable to decomposition function; verify 7 outputs with correct IDs
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0004/evidence.md`

**Dependencies:** T01.01
**Rollback:** Remove decomposition function; deliverables pass through unsplit
**Notes:** Depends on behavioral detection heuristic (T01.03) for identifying split candidates; can stub detection during development.

---

### T01.03 -- Implement behavioral detection heuristic for deliverable descriptions

| Field | Value |
|---|---|
| Roadmap Item IDs | R-005, R-006 |
| Why | The heuristic classifies deliverable descriptions as behavioral or non-behavioral by detecting computational verbs, state mutation patterns, and conditional logic patterns. This drives decomposition into Implement/Verify pairs. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential, Context7 |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0005, D-0006 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0005/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0006/evidence.md

**Deliverables:**
1. `is_behavioral(description: str) -> bool` function detecting: computational verbs (compute, extract, filter, count, calculate, determine, select, track, increment, update, replace, introduce), state mutation patterns (`self._*`, counter/offset/cursor), conditional logic patterns (guard, sentinel, flag, early return), with negative signal suppression for doc-specific verbs (document, describe, explain, list) (D-0005)
2. Test suite: "Replace boolean with int offset" -> behavioral, "Document API endpoint" -> not behavioral, "Add type definition for GateResult" -> not behavioral, "Implement retry with bounded attempts" -> behavioral, "Update README" -> not behavioral, empty description -> false (D-0006)

**Steps:**
1. **[PLANNING]** Review R-001 risk R-001 (false positives on documentation deliverables) to incorporate negative signal suppression
2. **[PLANNING]** Compile computational verb list and state mutation patterns from roadmap specification
3. **[EXECUTION]** Implement `is_behavioral()` function with three detection categories: computational verbs, state mutation patterns, conditional logic patterns
4. **[EXECUTION]** Add negative signal suppression for documentation verbs to reduce false positives
5. **[VERIFICATION]** Run six-scenario test suite with exact expected outcomes
6. **[COMPLETION]** Document heuristic patterns and thresholds in spec artifact at D-0005 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0005/spec.md` exists documenting the `is_behavioral()` function with all detection patterns and suppression rules
- "Replace boolean with int offset" returns true; "Document API endpoint" returns false
- Empty description returns false without errors
- Negative signal suppression prevents false positives on documentation deliverables containing verbs like "document", "describe", "explain", "list"

**Validation:**
- Manual check: call `is_behavioral()` with all six test cases and verify boolean outputs match expected values
- Evidence: linkable test log artifact produced at `TASKLIST_ROOT/artifacts/D-0006/evidence.md`

**Dependencies:** None
**Rollback:** Remove heuristic function; decomposition falls back to treating all deliverables as behavioral
**Notes:** R-001 mitigation: negative signal suppression for doc-specific verbs. Tunable threshold for future refinement.

---

### T01.04 -- Integrate decomposition into roadmap generator pipeline as post-generation pass

| Field | Value |
|---|---|
| Roadmap Item IDs | R-007, R-008 |
| Why | The decomposition pass must run after deliverable generation but before output formatting. It must be idempotent (running twice produces identical results) and preserve deliverable ordering within each milestone. This is the integration point that makes M1 deliverables available to M2-M4. |
| Effort | M |
| Risk | Medium |
| Risk Drivers | multi-file, pipeline |
| Tier | STRICT |
| Confidence | [████████--] 85% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Sub-agent (quality-engineer) |
| MCP Requirements | Required: Sequential, Serena | Preferred: Context7 |
| Fallback Allowed | No |
| Sub-Agent Delegation | Recommended |
| Deliverable IDs | D-0007, D-0008 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0007/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0008/evidence.md

**Deliverables:**
1. Pipeline integration: decomposition pass registered in roadmap generator pipeline after deliverable generation, before output formatting, with idempotency guarantee and milestone-order preservation (D-0007)
2. Integration test: known spec input produces output containing Implement/Verify pairs for all behavioral deliverables, non-behavioral deliverables unchanged, milestone structure preserved, Release Gate Rule 3 satisfied (D-0008)

**Steps:**
1. **[PLANNING]** Read roadmap generator pipeline in `src/superclaude/cli/roadmap/` to identify the insertion point between deliverable generation and output formatting
2. **[PLANNING]** Verify T01.01 schema extension and T01.02 decomposition function are available as dependencies
3. **[EXECUTION]** Register decomposition pass in pipeline at correct position (after generation, before formatting)
4. **[EXECUTION]** Add idempotency guard: pass detects already-decomposed deliverables and skips re-decomposition
5. **[EXECUTION]** Ensure milestone-internal ordering is preserved after decomposition
6. **[VERIFICATION]** Run integration test with known spec input via sub-agent quality-engineer; verify Implement/Verify pairs, non-behavioral pass-through, and Release Gate Rule 3 compliance
7. **[COMPLETION]** Document pipeline integration point and execution order in spec artifact at D-0007 path

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0007/spec.md` exists documenting the pipeline insertion point, execution order, and idempotency guarantees
- Integration test with known spec produces correct Implement/Verify pairs for all behavioral deliverables and passes non-behavioral deliverables unchanged
- Running the pipeline twice on the same input produces byte-identical output (idempotency)
- All `.b` verify deliverables contain at least one state assertion or boundary case (Release Gate Rule 3)

**Validation:**
- Manual check: run pipeline on known spec twice; diff outputs to verify idempotency; inspect .b deliverables for state assertions
- Evidence: linkable integration test log artifact produced at `TASKLIST_ROOT/artifacts/D-0008/evidence.md`

**Dependencies:** T01.01, T01.02, T01.03
**Rollback:** Remove pipeline registration; generator produces original undecoded deliverables
**Notes:** This is the critical integration task for Phase 1. All M2-M4 passes attach to this pipeline position.

---

### Checkpoint: Phase 1 / Tasks T01.01-T01.04

**Purpose:** Verify core schema extension and decomposition pipeline are functional before proceeding to exit criteria validation.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P01-T01-T04.md
**Verification:**
- Extended deliverable schema accepts all six `kind` values and rejects unknown values with ValueError
- Decomposition function correctly splits behavioral deliverables into Implement/Verify pairs and passes non-behavioral deliverables unchanged
- Pipeline integration produces idempotent output with correct ordering
**Exit Criteria:**
- All four tasks (T01.01-T01.04) have passing test suites with evidence artifacts
- No known regressions in existing roadmap parsing (backward compatibility confirmed)
- Behavioral detection heuristic has zero false positives on documentation deliverables in test corpus

---

### T01.05 -- Validate Release Gate Rule 3 enforcement and Phase 1 exit criteria

| Field | Value |
|---|---|
| Roadmap Item IDs | R-001 |
| Why | Release Gate Rule 3 requires that all .b verify deliverables contain at least one state assertion or boundary case. This task validates enforcement before Phase 2 begins. |
| Effort | S |
| Risk | Low |
| Risk Drivers | None matched |
| Tier | STANDARD |
| Confidence | [████████--] 80% |
| Requires Confirmation | No |
| Critical Path Override | No |
| Verification Method | Direct test execution |
| MCP Requirements | Preferred: Sequential |
| Fallback Allowed | Yes |
| Sub-Agent Delegation | None |
| Deliverable IDs | D-0009, D-0010 |

**Artifacts (Intended Paths):**
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0009/spec.md
- .dev/releases/current/v.2.11-roadmap-v4/tasklist/artifacts/D-0010/evidence.md

**Deliverables:**
1. Release Gate Rule 3 enforcement validation: confirm all `.b` verify deliverables generated by the decomposition pass contain at least one state assertion or boundary case (D-0009)
2. Phase 1 milestone exit criteria validation report: all deliverables D-0001 through D-0008 complete, all tests passing, no regressions (D-0010)

**Steps:**
1. **[PLANNING]** Collect all `.b` verify deliverables generated by the decomposition pass from T01.04 integration output
2. **[PLANNING]** Define state assertion and boundary case detection criteria per Release Gate Rule 3
3. **[EXECUTION]** Scan each `.b` deliverable description for state assertion or boundary case references
4. **[EXECUTION]** Flag any `.b` deliverables that fail Rule 3 (generic "tests pass" without state assertions)
5. **[VERIFICATION]** Verify zero Rule 3 violations in the test output
6. **[COMPLETION]** Document validation results and Phase 1 exit criteria status in evidence artifact

**Acceptance Criteria:**
- File `TASKLIST_ROOT/artifacts/D-0009/spec.md` exists documenting Rule 3 enforcement criteria and scan results
- Zero `.b` verify deliverables contain only generic "tests pass" without state assertions
- All deliverables D-0001 through D-0008 are complete with passing evidence artifacts
- No regressions detected in existing roadmap parsing functionality

**Validation:**
- Manual check: review each `.b` deliverable for presence of state assertion or boundary case reference
- Evidence: linkable validation report artifact produced at `TASKLIST_ROOT/artifacts/D-0010/evidence.md`

**Dependencies:** T01.01, T01.02, T01.03, T01.04
**Rollback:** N/A (validation task; no code changes)
**Notes:** This is a gate task. Phase 2 must not begin until this task passes.

---

### Checkpoint: End of Phase 1

**Purpose:** Gate Phase 2 entry. Confirm all Phase 1 deliverables are complete, Release Gate Rule 3 is enforced, and the decomposition pipeline is stable.
**Checkpoint Report Path:** .dev/releases/current/v.2.11-roadmap-v4/tasklist/checkpoints/CP-P01-END.md
**Verification:**
- All five tasks (T01.01-T01.05) completed with evidence artifacts at intended paths
- Extended deliverable schema is backward-compatible with existing roadmaps
- Decomposition pipeline is idempotent and produces correct Implement/Verify pairs
**Exit Criteria:**
- Release Gate Rule 3 validated: all `.b` deliverables contain state assertions or boundary cases
- No false positives from behavioral detection heuristic on documentation deliverables
- Pipeline ready for M2 passes: schema supports `invariant_check`, `fmea_test`, `guard_test`, `contract_test` kinds
