# Test Strategy: v3.0-roadmap-gen

> **Source Roadmap**: `.dev/plans/v3.0_Roadmaps/v3.0-roadmap-gen/roadmap.md`
> **Generated**: 2026-01-06
> **Generator Version**: v2.0

## Test Environment

- **Location**: `.dev/tests/`
- **Fixtures**: `.dev/fixtures/roadmap-gen/`
- **Mock Services**: `.dev/mocks/crossLLM/`
- **Test Runner**: Native agent execution with Bash validation

---

## Test Categories

### 1. Unit Tests
Test individual functions/phases in isolation with mocked dependencies.

**Location**: `.dev/tests/unit/roadmap-gen/`

### 2. Integration Tests
Test interaction between phases and external systems (crossLLM).

**Location**: `.dev/tests/integration/roadmap-gen/`

### 3. Regression Tests
Verify existing functionality not broken by changes.

**Location**: `.dev/tests/regression/roadmap-gen/`

### 4. Acceptance Tests
Directly verify acceptance criteria from specification.

**Location**: `.dev/tests/acceptance/roadmap-gen/`

---

## Test Matrix

| Deliverable ID | Unit Tests | Integration Tests | Acceptance Tests | Regression Tests |
|----------------|------------|-------------------|------------------|------------------|
| REQ-001 | UT-001: Syntax parsing | IT-M1-01: Command routing | ACC-001: Valid invocation | REG-CMD |
| REQ-002 | UT-002: Phase structure | IT-M1-01: Full pipeline | ACC-002: 9 phases callable | REG-ORCH |
| REQ-003 | UT-003: Validation rules | IT-M1-02: Invalid input | ACC-003: Missing file error | REG-VALID |
| REQ-004 | UT-004: ID assignment | IT-M1-03: Extraction | ACC-004: Schema compliance | REG-EXTRACT |
| REQ-005 | UT-005: Persona logic | IT-M1-04: Domain calc | ACC-005: >40% selection | REG-PERSONA |
| REQ-006 | UT-006: Template scoring | IT-M2-01: Template eval | ACC-006: ≥80% selection | REG-TEMPLATE |
| REQ-007 | UT-007: Scorer algorithm | IT-M2-02: Score accuracy | ACC-007: Correct ranking | REG-SCORER |
| DOC-001 | UT-008: Template structure | - | ACC-008: Feature sections | - |
| DOC-002 | UT-009: Template structure | - | ACC-009: Quality sections | - |
| DOC-003 | UT-010: Template structure | - | ACC-010: Docs sections | - |
| REQ-008 | UT-011: Milestone formation | IT-M3-01: Roadmap gen | ACC-011: Traceability | REG-ROADMAP |
| REQ-009 | UT-012: Test matrix | IT-M3-02: Test strategy | ACC-012: Coverage matrix | REG-TESTSTRAT |
| REQ-010 | UT-013: Prompt sections | IT-M3-03: Exec prompt | ACC-013: Valid paths | REG-EXECPROMPT |
| REQ-011 | UT-014: Validation rules | IT-M3-04: Self-validation | ACC-014: Discrepancy detect | REG-SELFVAL |
| REQ-012 | UT-015: Protocol steps | IT-M4-01: crossLLM invoke | ACC-015: PASS handling | REG-CROSSLLM |
| REQ-013 | UT-016: Parallel logic | IT-M4-02: Parallel exec | ACC-016: Concurrent run | REG-PARALLEL |
| REQ-014 | UT-017: Copy logic | IT-M4-03: Draft preserve | ACC-017: .draft.md exists | REG-DRAFT |
| REQ-015 | UT-018: Threshold calc | IT-M4-04: Circuit breaker | ACC-018: ≥50% trigger | REG-CIRCUIT |
| REQ-016 | UT-019: Log format | IT-M4-05: Upgrade log | ACC-019: Log schema | REG-UPGLOG |
| REQ-017 | UT-020: Consistency checks | IT-M4-06: Phase 7.5 | ACC-020: ID integrity | REG-CONSIST |
| REQ-018 | UT-021: Report format | IT-M4-06: Phase 7.5 | ACC-021: Report schema | REG-CONRPT |
| REQ-019 | UT-022: Chain cycling | IT-M5-01: Multi-iter | ACC-022: Chain sequence | REG-MULTIITER |
| REQ-020 | UT-023: Folder creation | IT-M4-07: Version mgmt | ACC-023: v1/v2/v3 structure | REG-VERSIONS |
| IMP-001 | UT-024: Chain parsing | IT-M5-02: --chain | ACC-024: Override works | REG-FLAGS |
| IMP-002 | UT-025: Threshold parsing | IT-M5-03: --threshold | ACC-025: Custom threshold | REG-FLAGS |
| IMP-003 | UT-026: Artifact list | IT-M5-04: --upgrade-only | ACC-026: Selective upgrade | REG-FLAGS |
| IMP-004 | UT-027: Sequential mode | IT-M5-05: --sequential | ACC-027: Non-parallel | REG-FLAGS |
| IMP-005 | UT-028: Output parsing | IT-M1-05: --output | ACC-028: Custom dir | REG-FLAGS |
| DOC-004 | - | IT-M6-01: Docs accuracy | ACC-029: User can invoke | - |
| DOC-005 | - | IT-M6-02: Tech accuracy | ACC-030: Dev understands | - |
| REF-001 | - | IT-M6-03: Protocol reuse | ACC-031: Standalone works | - |

---

## Test Fixtures

### Specification Fixtures
| Fixture | Description | Location |
|---------|-------------|----------|
| `simple-feature.md` | Single-feature spec for basic testing | `.dev/fixtures/roadmap-gen/simple-feature.md` |
| `complex-release.md` | Multi-domain spec (20+ items) | `.dev/fixtures/roadmap-gen/complex-release.md` |
| `quality-focused.md` | QA/performance spec for template matching | `.dev/fixtures/roadmap-gen/quality-focused.md` |
| `docs-refactor.md` | Documentation refactor spec | `.dev/fixtures/roadmap-gen/docs-refactor.md` |
| `empty-spec.md` | Empty/placeholder spec for validation | `.dev/fixtures/roadmap-gen/empty-spec.md` |
| `invalid-format.txt` | Non-markdown file for error testing | `.dev/fixtures/roadmap-gen/invalid-format.txt` |

### Mock Responses
| Mock | Description | Location |
|------|-------------|----------|
| `crossLLM-pass.md` | Simulated PASS response | `.dev/mocks/crossLLM/pass-response/` |
| `crossLLM-fail.md` | Simulated FAIL response | `.dev/mocks/crossLLM/fail-response/` |
| `crossLLM-timeout.md` | Simulated timeout scenario | `.dev/mocks/crossLLM/timeout-response/` |

---

## Test Execution Order

1. **Unit Tests** (fast, isolated)
   - Run all UT-* tests
   - Mock all external dependencies
   - Target: <30 seconds

2. **Integration Tests** (milestone scope)
   - Run IT-M1-* through IT-M6-*
   - Use fixtures, not production data
   - Target: <5 minutes per milestone

3. **Acceptance Tests** (criteria verification)
   - Run all ACC-* tests
   - Verify Gherkin criteria from spec
   - Target: <10 minutes total

4. **Regression Tests** (full suite)
   - Run all REG-* tests
   - Ensure no existing functionality broken
   - Target: <5 minutes

---

## Test Constraints (Mandatory)

- **NO writes outside `.dev/` or `.roadmaps/` during tests**
- **NO external API calls to production systems**
- **NO destructive operations on any data**
- **ALL tests must be idempotent (safe to re-run)**
- **Mock crossLLM responses for deterministic testing**

---

## Coverage Targets

| Category | Target | Measurement |
|----------|--------|-------------|
| Unit test coverage | 80% of new code | Line coverage on agent prompts |
| Critical path coverage | 100% | All 9 phases tested |
| Branch coverage | 75% | Decision points in pipeline |
| Error path coverage | 100% | All STOP conditions tested |

---

## Milestone-Specific Test Plans

### Milestone 1 Tests (Foundation)
| Test ID | Type | Description | Expected Result |
|---------|------|-------------|-----------------|
| IT-M1-01 | Integration | Full command routing | Orchestrator invoked |
| IT-M1-02 | Integration | Missing input file | STOP with clear error |
| IT-M1-03 | Integration | Valid extraction | extraction.md created |
| IT-M1-04 | Integration | Domain distribution | Correct percentages |
| IT-M1-05 | Integration | --output flag | Custom directory used |

### Milestone 2 Tests (Templates)
| Test ID | Type | Description | Expected Result |
|---------|------|-------------|-----------------|
| IT-M2-01 | Integration | Template selection ≥80% | Direct template use |
| IT-M2-02 | Integration | Template selection <80% | Variant created |
| IT-M2-03 | Integration | Feature-heavy spec | feature-release.md selected |
| IT-M2-04 | Integration | Quality-heavy spec | quality-release.md selected |
| IT-M2-05 | Integration | Docs-heavy spec | documentation-release.md selected |

### Milestone 3 Tests (Core Generation)
| Test ID | Type | Description | Expected Result |
|---------|------|-------------|-----------------|
| IT-M3-01 | Integration | Roadmap generation | All items in milestones |
| IT-M3-02 | Integration | Test strategy | All deliverables covered |
| IT-M3-03 | Integration | Execution prompt | Valid artifact paths |
| IT-M3-04 | Integration | Self-validation pass | No discrepancies |
| IT-M3-05 | Integration | Self-validation fail | Discrepancy logged |

### Milestone 4 Tests (crossLLM Integration)
| Test ID | Type | Description | Expected Result |
|---------|------|-------------|-----------------|
| IT-M4-01 | Integration | crossLLM PASS | Artifact replaced |
| IT-M4-02 | Integration | crossLLM FAIL | Draft preserved |
| IT-M4-03 | Integration | Parallel execution | 3 concurrent invokes |
| IT-M4-04 | Integration | Circuit breaker | Stops at 50% failures |
| IT-M4-05 | Integration | Upgrade log | Schema-compliant log |
| IT-M4-06 | Integration | Consistency validation | Detects mismatch |
| IT-M4-07 | Integration | Version folders | v1/, v2/ created |

### Milestone 5 Tests (Enhancements)
| Test ID | Type | Description | Expected Result |
|---------|------|-------------|-----------------|
| IT-M5-01 | Integration | --version 3 | 2 upgrade iterations |
| IT-M5-02 | Integration | --chain custom | First iteration uses custom |
| IT-M5-03 | Integration | --threshold 15 | Lower threshold applied |
| IT-M5-04 | Integration | --upgrade-only | Selective upgrades |
| IT-M5-05 | Integration | --sequential | Non-parallel execution |

### Milestone 6 Tests (Documentation)
| Test ID | Type | Description | Expected Result |
|---------|------|-------------|-----------------|
| IT-M6-01 | Integration | User doc accuracy | All examples work |
| IT-M6-02 | Integration | Tech doc accuracy | Architecture matches code |
| IT-M6-03 | Integration | Protocol reuse | Works with mock command |

---

## Test Reporting

### Required Reports
1. **Test Summary**: Pass/fail counts per category
2. **Coverage Report**: Line/branch coverage metrics
3. **Failure Details**: Stack traces and context for failures
4. **Performance Metrics**: Execution times per test category

### Report Location
`.dev/tests/reports/roadmap-gen/`

---

*Generated by Roadmap-Generator v2.0*
