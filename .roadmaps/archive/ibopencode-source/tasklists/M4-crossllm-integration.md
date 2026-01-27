# Tasklist: Milestone 4 - crossLLM Integration

> **Source Roadmap**: `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/roadmap.md`
> **Milestone**: M4 - crossLLM Integration
> **Generated**: 2026-01-06
> **Generator Version**: Tasklist-Generator v2.1

---

## Milestone Overview

| Attribute | Value |
|-----------|-------|
| **Objective** | Implement upgrade pipeline with crossLLM and consistency validation |
| **Dependencies** | M3 (Core generation complete) |
| **Complexity** | High |
| **Total Deliverables** | 8 |
| **Total Tasks** | 20 |

---

## Deliverable Mapping

| Roadmap ID | Description | Tasks | Est. Effort |
|------------|-------------|-------|-------------|
| REQ-014 | Draft preservation | T04.01-T04.02 | M |
| REQ-012 | crossLLM integration (Phase 7) | T04.03-T04.05 | L |
| REQ-013 | Parallel upgrade execution | T04.06-T04.08 | L |
| REQ-015 | Circuit breaker | T04.09-T04.11 | M |
| REQ-016 | Upgrade log generation | T04.12-T04.13 | S |
| REQ-020 | Version folder management | T04.14-T04.15 | M |
| REQ-017 | Phase 7.5 consistency validation | T04.16-T04.18 | L |
| REQ-018 | Consistency report generation | T04.19-T04.20 | S |

---

## Task List

### Phase 7 Foundation

#### T04.01 - Implement draft preservation logic
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-001 (REQ-014) |
| **Type** | Implementation |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | M3 complete |

**Description**: Implement logic to copy each artifact to `.draft.md` before upgrade attempt. Include file copy error handling and rollback capability on failure.

**Acceptance Criteria**:
- [ ] `.draft.md` copy created BEFORE crossLLM invocation
- [ ] Original file permissions preserved
- [ ] Copy operation is atomic (no partial copies)
- [ ] Failure triggers draft restoration
- [ ] Draft preserved on crossLLM FAIL result

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (draft preservation section)

---

#### T04.02 - QA: Verify draft preservation behavior
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-001 (REQ-014) |
| **Type** | QA/Verification |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.01 |

**Description**: Verify draft preservation works correctly in success and failure scenarios.

**Verification Checklist**:
- [ ] Draft created before upgrade (timestamp verification)
- [ ] Draft restored on crossLLM FAIL
- [ ] Draft preserved when circuit breaker triggers
- [ ] No draft file left behind on PASS
- [ ] File permissions correct after restore

---

#### T04.03 - Implement crossLLM Phase 7 integration
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-002 (REQ-012) |
| **Type** | Implementation |
| **Effort** | L |
| **Risk** | High |
| **Dependencies** | T04.01 |

**Description**: Implement Phase 7 crossLLM integration following the Integration Protocol. Invoke `/rf:crossLLM v2 <artifact> <chain>` for each upgradeable artifact (roadmap.md, test-strategy.md, execution-prompt.md).

**Acceptance Criteria**:
- [ ] crossLLM invoked via command, NOT direct integration
- [ ] Correct chain passed to each invocation
- [ ] Result parsing handles PASS/FAIL correctly
- [ ] Improvement percentage extracted from response
- [ ] Phase logs entry/exit with artifact count

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (Phase 7 section)

**Reference**: `docs/generated/crossLLM-Integration-Protocol.md`

---

#### T04.04 - QA: Verify crossLLM invocation
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-002 (REQ-012) |
| **Type** | QA/Verification |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | T04.03 |

**Description**: Verify crossLLM integration follows protocol and handles all result types.

**Verification Checklist**:
- [ ] Command format matches `/rf:crossLLM v2 <file> <chain>`
- [ ] Default chain is `claude>gpt`
- [ ] PASS result replaces original with upgraded version
- [ ] FAIL result preserves draft
- [ ] Improvement percentage parsed correctly
- [ ] Threshold filtering works (default 25%)

---

#### T04.05 - Integration test: crossLLM Phase 7 pipeline
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-002 (REQ-012) |
| **Type** | Integration Test |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | T04.04 |

**Description**: Run end-to-end test of Phase 7 with mock crossLLM responses.

**Test Scenarios**:
- [ ] IT-M4-01: crossLLM PASS → artifact replaced
- [ ] IT-M4-02: crossLLM FAIL → draft preserved
- [ ] Mock response parsing correct
- [ ] Log output matches expected format

---

### Parallel Execution

#### T04.06 - Implement parallel upgrade execution
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-003 (REQ-013) |
| **Type** | Implementation |
| **Effort** | L |
| **Risk** | High |
| **Dependencies** | T04.03 |

**Description**: Enable concurrent execution of crossLLM upgrades for all 3 artifacts. Implement proper synchronization and result aggregation.

**Acceptance Criteria**:
- [ ] All 3 artifacts upgraded concurrently (NOT sequentially)
- [ ] Results aggregated correctly
- [ ] Partial failures handled gracefully
- [ ] Resource usage within limits
- [ ] Log preserves per-artifact detail

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (parallel execution section)

---

#### T04.07 - QA: Verify parallel execution
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-003 (REQ-013) |
| **Type** | QA/Verification |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | T04.06 |

**Description**: Verify parallel execution is truly concurrent and handles edge cases.

**Verification Checklist**:
- [ ] Execution timing confirms concurrency (not sequential)
- [ ] Mixed PASS/FAIL results handled correctly
- [ ] Result order is deterministic in aggregation
- [ ] No race conditions in file operations
- [ ] Memory usage acceptable

---

#### T04.08 - Integration test: Parallel execution
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-003 (REQ-013) |
| **Type** | Integration Test |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.07 |

**Description**: Test parallel execution with various result combinations.

**Test Scenarios**:
- [ ] IT-M4-03: 3 concurrent upgrades complete successfully
- [ ] Mixed PASS/FAIL results aggregated correctly
- [ ] Timing confirms concurrent execution

---

### Circuit Breaker

#### T04.09 - Implement circuit breaker logic
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-004 (REQ-015) |
| **Type** | Implementation |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | T04.06 |

**Description**: Implement circuit breaker that stops remaining upgrades when ≥50% of artifacts fail. Preserve drafts for stopped artifacts.

**Acceptance Criteria**:
- [ ] Circuit breaker triggers at ≥50% failure rate
- [ ] Remaining upgrades stopped immediately
- [ ] Drafts preserved for stopped artifacts
- [ ] Partial results logged
- [ ] User-friendly message explains circuit breaker activation

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (circuit breaker section)

---

#### T04.10 - QA: Verify circuit breaker behavior
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-004 (REQ-015) |
| **Type** | QA/Verification |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.09 |

**Description**: Verify circuit breaker triggers correctly at threshold.

**Verification Checklist**:
- [ ] 0/3 failures → continues (0% < 50%)
- [ ] 1/3 failures → continues (33% < 50%)
- [ ] 2/3 failures → triggers (66% ≥ 50%)
- [ ] Stopped artifacts have drafts preserved
- [ ] Log clearly indicates circuit breaker activation

---

#### T04.11 - Integration test: Circuit breaker
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-004 (REQ-015) |
| **Type** | Integration Test |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.10 |

**Description**: Test circuit breaker with mock failure scenarios.

**Test Scenarios**:
- [ ] IT-M4-04: Circuit breaker triggers at ≥50% failures
- [ ] Partial completion preserves successful upgrades
- [ ] Draft files exist for all stopped artifacts

---

### Upgrade Logging

#### T04.12 - Implement upgrade log generation
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-005 (REQ-016) |
| **Type** | Implementation |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.06 |

**Description**: Generate `upgrade-log.md` with configuration, per-artifact results, and summary statistics.

**Acceptance Criteria**:
- [ ] Log includes: timestamp, chain used, threshold
- [ ] Per-artifact: filename, result (PASS/FAIL), improvement %
- [ ] Summary: total, passed, failed, skipped
- [ ] Circuit breaker status noted if triggered
- [ ] Log follows required schema

**Artifacts**:
- `upgrade-log.md` (output artifact)

---

#### T04.13 - QA: Verify upgrade log schema
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-005 (REQ-016) |
| **Type** | QA/Verification |
| **Effort** | XS |
| **Risk** | Low |
| **Dependencies** | T04.12 |

**Description**: Verify upgrade log follows required schema and contains all fields.

**Verification Checklist**:
- [ ] IT-M4-05: Log schema compliance
- [ ] All required sections present
- [ ] Timestamps in ISO 8601 format
- [ ] Improvement percentages correctly formatted
- [ ] Summary statistics accurate

---

### Checkpoint: T04.01-T04.13
**Status**: [ ] Complete
**Blockers**: ___
**Notes**: ___

---

### Version Management

#### T04.14 - Implement version folder management
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-006 (REQ-020) |
| **Type** | Implementation |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | T04.03 |

**Description**: Create version folders (v1/, v2/, v3/...) for draft and each upgrade iteration. v1 contains initial draft, subsequent folders contain iteration results.

**Acceptance Criteria**:
- [ ] v1/ created with initial draft artifacts
- [ ] v2/, v3/... created per iteration
- [ ] Folder structure mirrors base output structure
- [ ] Version metadata in each folder
- [ ] --version N creates exactly N folders

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (version folder section)

---

#### T04.15 - QA: Verify version folder structure
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-006 (REQ-020) |
| **Type** | QA/Verification |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.14 |

**Description**: Verify version folders created correctly for various --version values.

**Verification Checklist**:
- [ ] IT-M4-07: v1/, v2/ folders created correctly
- [ ] --version 1 creates only v1/ (draft, no upgrade)
- [ ] --version 3 creates v1/, v2/, v3/
- [ ] Each folder has complete artifact set
- [ ] Folder naming consistent

---

### Phase 7.5 Consistency Validation

#### T04.16 - Implement Phase 7.5 consistency validation
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-007 (REQ-017) |
| **Type** | Implementation |
| **Effort** | L |
| **Risk** | High |
| **Dependencies** | T04.06 |

**Description**: Implement Phase 7.5 cross-artifact consistency validation after parallel upgrades complete. Verify ID reference integrity, coverage completeness, structural alignment, and naming consistency.

**Acceptance Criteria**:
- [ ] ID reference integrity: All IDs in one artifact exist in others
- [ ] Coverage completeness: All extraction items appear in roadmap
- [ ] Structural alignment: Milestone structure consistent
- [ ] Naming consistency: Same IDs use same descriptions
- [ ] Detects intentionally introduced inconsistencies

**Artifacts**:
- `.opencode/agent/rf-roadmap-gen-orchestrator.md` (Phase 7.5 section)

---

#### T04.17 - QA: Verify consistency validation logic
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-007 (REQ-017) |
| **Type** | QA/Verification |
| **Effort** | M |
| **Risk** | Medium |
| **Dependencies** | T04.16 |

**Description**: Verify consistency validation catches all types of inconsistencies.

**Verification Checklist**:
- [ ] Missing ID reference detected
- [ ] Orphaned ID in one artifact detected
- [ ] Name mismatch for same ID detected
- [ ] Structural divergence detected
- [ ] Coverage gap detected

---

#### T04.18 - Integration test: Phase 7.5
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-007 (REQ-017) |
| **Type** | Integration Test |
| **Effort** | M |
| **Risk** | Low |
| **Dependencies** | T04.17 |

**Description**: Test Phase 7.5 with intentionally inconsistent artifacts.

**Test Scenarios**:
- [ ] IT-M4-06: Consistency validation detects mismatch
- [ ] Clean artifacts pass validation
- [ ] Report generated for inconsistencies

---

### Consistency Reporting

#### T04.19 - Implement consistency report generation
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-008 (REQ-018) |
| **Type** | Implementation |
| **Effort** | S |
| **Risk** | Low |
| **Dependencies** | T04.16 |

**Description**: Generate `consistency-report.md` documenting validation findings from Phase 7.5.

**Acceptance Criteria**:
- [ ] Report includes: validation timestamp, artifacts validated
- [ ] Findings categorized by severity (Error/Warning/Info)
- [ ] Specific file and line references where possible
- [ ] Summary with pass/fail determination
- [ ] Recommendations for manual review

**Artifacts**:
- `consistency-report.md` (output artifact)

---

#### T04.20 - QA: Verify consistency report
| Attribute | Value |
|-----------|-------|
| **Deliverable** | D-M4-008 (REQ-018) |
| **Type** | QA/Verification |
| **Effort** | XS |
| **Risk** | Low |
| **Dependencies** | T04.19 |

**Description**: Verify consistency report contains all required sections and accurate findings.

**Verification Checklist**:
- [ ] Report schema compliant
- [ ] Severity levels correctly assigned
- [ ] All findings from validation included
- [ ] Summary statistics accurate
- [ ] Actionable recommendations provided

---

### Checkpoint: T04.14-T04.20 (End of Phase)
**Status**: [ ] Complete
**Blockers**: ___
**Notes**: ___

---

## Verification Checkpoint M4

| Checkpoint Item | Status | Notes |
|-----------------|--------|-------|
| All deliverables code-complete | [ ] | |
| crossLLM invoked correctly with proper chain | [ ] | |
| Parallel execution confirmed (concurrent, not sequential) | [ ] | |
| Draft files created before upgrade | [ ] | |
| Circuit breaker triggers at correct threshold | [ ] | |
| upgrade-log.md contains all required fields | [ ] | |
| Phase 7.5 detects intentionally introduced inconsistencies | [ ] | |
| consistency-report.md generated with findings | [ ] | |

---

## Traceability Matrix

| Roadmap ID | Task IDs | Deliverable ID | Artifact Path |
|------------|----------|----------------|---------------|
| REQ-014 | T04.01, T04.02 | D-M4-001 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-012 | T04.03, T04.04, T04.05 | D-M4-002 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-013 | T04.06, T04.07, T04.08 | D-M4-003 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-015 | T04.09, T04.10, T04.11 | D-M4-004 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-016 | T04.12, T04.13 | D-M4-005 | `upgrade-log.md` |
| REQ-020 | T04.14, T04.15 | D-M4-006 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-017 | T04.16, T04.17, T04.18 | D-M4-007 | `.opencode/agent/rf-roadmap-gen-orchestrator.md` |
| REQ-018 | T04.19, T04.20 | D-M4-008 | `consistency-report.md` |

---

## Execution Log Template

| Task ID | Started | Completed | Status | Notes |
|---------|---------|-----------|--------|-------|
| T04.01 | | | ⏳ | |
| T04.02 | | | ⏳ | |
| T04.03 | | | ⏳ | |
| T04.04 | | | ⏳ | |
| T04.05 | | | ⏳ | |
| T04.06 | | | ⏳ | |
| T04.07 | | | ⏳ | |
| T04.08 | | | ⏳ | |
| T04.09 | | | ⏳ | |
| T04.10 | | | ⏳ | |
| T04.11 | | | ⏳ | |
| T04.12 | | | ⏳ | |
| T04.13 | | | ⏳ | |
| T04.14 | | | ⏳ | |
| T04.15 | | | ⏳ | |
| T04.16 | | | ⏳ | |
| T04.17 | | | ⏳ | |
| T04.18 | | | ⏳ | |
| T04.19 | | | ⏳ | |
| T04.20 | | | ⏳ | |

---

*Generated by Tasklist-Generator v2.1*
