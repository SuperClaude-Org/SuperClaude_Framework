---
validation_milestones: 8
interleave_ratio: '1:1'
---

# Test Strategy: Roadmap Validation Pipeline (v2.19)

## 1. Validation Milestones Mapped to Roadmap Phases

### VM-1: ValidateConfig & Gate Definitions (Phase 1 Exit)
**Trigger**: Phase 1 deliverables complete.
**Validates**: FR-002, FR-013, FR-014
**Criteria**:
- `ValidateConfig` dataclass instantiates with all 5 fields and correct defaults (`opus:architect`, `""`, `50`, `False`)
- `REFLECT_GATE` enforces STANDARD tier, min 20 lines, 3 required frontmatter fields
- `ADVERSARIAL_MERGE_GATE` enforces STRICT tier, min 30 lines, 5 required frontmatter fields + agreement table semantic check
- `_frontmatter_values_non_empty` imported and callable from `validate_gates.py`

### VM-2: Prompt Structural Validity (Phase 2 Exit)
**Trigger**: Phase 2 deliverables complete.
**Validates**: FR-008, FR-010, FR-012
**Criteria**:
- `build_reflect_prompt()` returns string containing all 7 dimension names with correct severity labels
- `build_merge_prompt()` returns string containing BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT instructions
- Interleave ratio formula embedded literally: `unique_phases_with_deliverables / total_phases`
- False-positive reduction constraint present in prompt text

### VM-3: Alignment Checkpoint (Phase 1‖2 Join)
**Trigger**: Both Phase 1 and Phase 2 complete.
**Validates**: Cross-artifact consistency (R-ARCH mitigation)
**Criteria**:
- Frontmatter field names in prompts exactly match gate definitions (e.g., `blocking_issues_count` not `blocking_count`)
- Severity labels in prompts match gate enforcement tiers
- No field-name mismatches between `validate_gates.py` and `validate_prompts.py`

### VM-4: Single-Agent End-to-End (Phase 3 Mid)
**Trigger**: `execute_validate()` implemented for single-agent path.
**Validates**: FR-001, FR-003, FR-009, FR-011, SC-001, NFR-003
**Criteria**:
- Given a directory with valid `roadmap.md`, `test-strategy.md`, `extraction.md`: produces `validate/validation-report.md`
- Report frontmatter contains all 6 required fields with non-empty values
- `tasklist_ready` equals `true` iff `blocking_issues_count == 0`
- Missing input files produce an error before subprocess invocation

### VM-5: Multi-Agent End-to-End (Phase 3 Exit)
**Trigger**: Multi-agent path implemented.
**Validates**: FR-004, FR-012, FR-014, SC-003, NFR-005
**Criteria**:
- N agents produce N `reflect-<agent-id>.md` files + 1 `validation-report.md`
- Merged report includes Agent Agreement Analysis table
- `ADVERSARIAL_MERGE_GATE` passes on merged report
- Partial failure produces degraded report with `validation_complete: false` and warning banner

### VM-6: CLI Integration Complete (Phase 4 Exit)
**Trigger**: Phase 4 deliverables complete.
**Validates**: FR-005, FR-006, FR-007, SC-004, SC-005, SC-007, NFR-006
**Criteria**:
- `superclaude roadmap validate <dir>` works standalone
- `superclaude roadmap run spec.md` creates `validate/` directory
- `superclaude roadmap run spec.md --no-validate` does not create `validate/` directory
- `--resume` on fully-successful pipeline runs validation
- `--resume` on failed-step pipeline skips validation
- Blocking issues exit 0 with CLI warnings
- `.roadmap-state.json` contains `validation` key with `pass`/`fail`/`skipped`

### VM-7: Known-Defect Detection (Phase 5 Mid)
**Trigger**: Integration tests with known-bad inputs written.
**Validates**: FR-008, SC-006
**Criteria**:
- Duplicate D-ID → BLOCKING finding
- Missing milestone reference → BLOCKING finding
- Untraced requirement → BLOCKING finding
- Cross-file inconsistency → BLOCKING finding

### VM-8: Full Verification (Phase 5 Exit)
**Trigger**: All tests pass, architecture verified.
**Validates**: SC-002, SC-008, SC-009, NFR-001, NFR-002, NFR-004
**Criteria**:
- `uv run pytest` passes all unit + integration tests
- Single-agent validation ≤2 min wall time
- `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty
- No new subprocess abstractions introduced (only `execute_pipeline`, `ClaudeProcess` used)

---

## 2. Test Categories

### 2.1 Unit Tests (7 tests)

| ID | Test | FR/NFR | File Under Test | Phase |
|----|------|--------|-----------------|-------|
| UT-01 | `ValidateConfig` defaults and field validation | FR-002 | `models.py` | 1 |
| UT-02 | `REFLECT_GATE` rejects missing frontmatter fields | FR-013 | `validate_gates.py` | 1 |
| UT-03 | `REFLECT_GATE` rejects empty frontmatter values | FR-013 | `validate_gates.py` | 1 |
| UT-04 | `REFLECT_GATE` rejects <20 line reports | FR-013 | `validate_gates.py` | 1 |
| UT-05 | `ADVERSARIAL_MERGE_GATE` rejects missing agreement table | FR-014 | `validate_gates.py` | 1 |
| UT-06 | `ADVERSARIAL_MERGE_GATE` enforces STRICT (min 30 lines) | FR-014 | `validate_gates.py` | 1 |
| UT-07 | `tasklist_ready` == `(blocking_issues_count == 0)` in report semantics | FR-011 | `validate_executor.py` | 3 |

### 2.2 Integration Tests (6 tests)

| ID | Test | SC | Subprocess Required | Phase |
|----|------|----|---------------------|-------|
| IT-01 | Standalone single-agent validation against valid inputs | SC-001 | Yes | 3 |
| IT-02 | Standalone multi-agent validation with per-agent files + merged report | SC-003 | Yes | 3 |
| IT-03 | `roadmap run` auto-invokes validation | SC-004 | Yes | 4 |
| IT-04 | `roadmap run --no-validate` skips validation | SC-005 | Yes | 4 |
| IT-05 | `--resume` success path runs validation | FR-007 | Yes | 4 |
| IT-06 | `--resume` failed-step path skips validation | FR-007 | Yes | 4 |

### 2.3 E2E / Known-Defect Detection Tests (4 tests)

| ID | Test | Defect Injected | Expected Result | Phase |
|----|------|-----------------|-----------------|-------|
| E2E-01 | Duplicate D-ID in roadmap | D-0001 appears twice | BLOCKING finding referencing duplicate | 5 |
| E2E-02 | Missing milestone reference | Phase references non-existent milestone | BLOCKING finding with location | 5 |
| E2E-03 | Untraced requirement | FR-099 has no deliverable mapping | BLOCKING finding citing FR-099 | 5 |
| E2E-04 | Cross-file inconsistency | Extraction lists FR not in roadmap | BLOCKING finding with both file refs | 5 |

### 2.4 Architecture & Acceptance Tests (3 tests)

| ID | Test | NFR | Method | Phase |
|----|------|-----|--------|-------|
| AT-01 | No reverse imports in `pipeline/` | NFR-002, SC-009 | `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` | 5 |
| AT-02 | Single-agent wall time ≤2 min | NFR-001, SC-002 | Timed execution | 5 |
| AT-03 | No new subprocess abstractions | NFR-004 | Manual code review + grep for new class definitions | 5 |

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1:1 — each implementation deliverable has a corresponding test written in the same phase or immediately after.

### Interleaving Schedule

```
Phase 1: Implement ValidateConfig     → Write UT-01
         Implement REFLECT_GATE       → Write UT-02, UT-03, UT-04
         Implement MERGE_GATE         → Write UT-05, UT-06
         ── Run: uv run pytest tests/roadmap/test_validate_gates.py ──

Phase 2: Implement build_reflect_prompt  → Manual smoke test (prompt output inspection)
         Implement build_merge_prompt    → Manual smoke test (prompt output inspection)
         ── VM-3: Alignment checkpoint (field-name cross-check) ──

Phase 3: Implement single-agent path  → Write IT-01, UT-07
         Implement multi-agent path    → Write IT-02
         Implement partial failure     → Write test for degraded report
         ── Run: uv run pytest tests/roadmap/ ──

Phase 4: Implement CLI validate cmd   → Write IT-03, IT-04
         Implement --no-validate       → (covered by IT-04)
         Implement --resume logic      → Write IT-05, IT-06
         Implement state persistence   → Verify .roadmap-state.json in IT-05/IT-06
         ── Run: uv run pytest tests/roadmap/ ──

Phase 5: Write E2E-01 through E2E-04  → Run against known-bad fixtures
         Write AT-01, AT-02, AT-03    → Run architecture verification
         ── Run: uv run pytest (full suite) ──
```

### Test Fixture Strategy

**Known-Good Fixtures** (for IT-01, IT-02):
- Directory with valid `roadmap.md`, `test-strategy.md`, `extraction.md` from a real pipeline run
- Minimal valid versions with correct frontmatter and structure

**Known-Bad Fixtures** (for E2E-01 through E2E-04):
- Each fixture is a copy of the known-good set with a single defect injected
- Defects are documented in fixture README for maintainability

**Mock Strategy**:
- Unit tests mock `ClaudeProcess` and `execute_pipeline` to avoid subprocess invocation
- Integration tests use real subprocesses against fixture directories
- E2E tests use real subprocesses with intentionally defective inputs

---

## 4. Risk-Based Test Prioritization

### Priority 1 — Critical (implement first, block release)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-ARCH: Architectural drift | AT-01 | Unidirectional dependency is a hard architectural constraint. Violation creates coupling that is expensive to unwind. Write the grep test early and run in CI. |
| R-004: Adversarial merge quality | IT-02, E2E-01–04 | If the merge step produces misleading findings, the entire validation subsystem loses trust. Test with intentionally conflicting inputs. |
| R-005: `--resume` edge cases | IT-05, IT-06 | Resume interacting with validation incorrectly could re-validate stale artifacts or skip validation of fresh ones. Both paths must be explicitly tested. |

### Priority 2 — High (implement in-phase, block milestone)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-001: False positives | E2E-01–04 (negative direction) | Run known-good inputs through validation and assert zero BLOCKING findings. False positives erode user trust. |
| Gate leniency (R-003) | UT-02–06 | Ensure gates reject shallow/incomplete reports. A gate that passes everything provides no value. |
| FR-011 semantics | UT-07 | `tasklist_ready` logic error would greenlight defective roadmaps. |

### Priority 3 — Standard (implement in Phase 5)

| Risk | Tests | Rationale |
|------|-------|-----------|
| R-002: Token cost | AT-02 | Wall time is a proxy for token cost. Measure but don't block on it — optimize post-launch if needed. |
| R-006: Helper coupling | AT-03 | Low risk since `_frontmatter_values_non_empty` is a pure function. Verify no additional coupling introduced. |
| NFR-005: Code path unity | Code review | Single vs multi path sharing is a design quality concern, not a correctness concern. |

---

## 5. Acceptance Criteria Per Milestone

### VM-1 Acceptance (Phase 1 Exit Gate)
- [ ] `ValidateConfig(output_dir="x")` uses all correct defaults
- [ ] UT-01 through UT-06 pass
- [ ] `validate_gates.py` imports only from `roadmap/gates.py` (no pipeline imports)

### VM-2 Acceptance (Phase 2 Exit Gate)
- [ ] `build_reflect_prompt("r", "t", "e")` returns non-empty string with all 7 dimension names
- [ ] `build_merge_prompt(["report_a", "report_b"])` returns string with agreement categories
- [ ] Manual inspection confirms no hallucinated frontmatter field names

### VM-3 Acceptance (Alignment Checkpoint)
- [ ] Field names in `validate_prompts.py` exactly match `validate_gates.py` definitions
- [ ] No `blocking_count` vs `blocking_issues_count` class of mismatch exists
- [ ] Severity labels (BLOCKING/WARNING) consistent across prompts and gates

### VM-4 Acceptance (Single-Agent E2E)
- [ ] IT-01 passes: valid report with correct frontmatter from known-good inputs
- [ ] UT-07 passes: `tasklist_ready` semantics correct
- [ ] Missing-file error path tested (no subprocess launched for incomplete directories)

### VM-5 Acceptance (Multi-Agent E2E)
- [ ] IT-02 passes: N reflection files + 1 merged report
- [ ] Merged report contains Agent Agreement Analysis table
- [ ] Partial failure test: degraded report has `validation_complete: false` + warning banner

### VM-6 Acceptance (CLI Complete)
- [ ] IT-03 through IT-06 pass
- [ ] `superclaude roadmap validate --help` shows all options
- [ ] `.roadmap-state.json` correctly records `pass`/`fail`/`skipped`
- [ ] Exit code is 0 even with blocking issues

### VM-7 Acceptance (Known-Defect Detection)
- [ ] E2E-01 through E2E-04 pass: each injected defect detected as BLOCKING
- [ ] Known-good inputs produce zero BLOCKING findings (false-positive guard)

### VM-8 Acceptance (Full Verification)
- [ ] `uv run pytest` all green (20 tests: 7 unit + 6 integration + 4 E2E + 3 architecture)
- [ ] AT-01 passes: no reverse imports
- [ ] AT-02 passes: single-agent ≤2 min
- [ ] AT-03 passes: no new subprocess abstractions

---

## 6. Quality Gates Between Phases

### Gate G1: Phase 1 → Phase 3
**Condition**: All unit tests (UT-01–06) pass.
**Enforcement**: Run `uv run pytest tests/roadmap/test_validate_gates.py -v` and require 0 failures.
**Blocks**: Phase 3 cannot start if gate definitions are untested or broken.

### Gate G2: Phase 2 → Phase 3
**Condition**: Prompt smoke tests pass manual review.
**Enforcement**: Developer confirms prompts contain correct dimension names, severity labels, and agreement categories.
**Blocks**: Phase 3 cannot start if prompts reference wrong field names.

### Gate G3: Phase 1‖2 → Phase 3 (Alignment Checkpoint)
**Condition**: Field-name cross-check between gates and prompts passes.
**Enforcement**: Automated string comparison of frontmatter field names in `validate_gates.py` vs `validate_prompts.py`. Write a dedicated test (`test_gate_prompt_alignment.py`) that imports both modules and asserts field-name consistency.
**Blocks**: Phase 3 implementation will wire wrong fields if this fails.

### Gate G4: Phase 3 → Phase 4
**Condition**: IT-01 and IT-02 pass (standalone validation works in both modes).
**Enforcement**: Run `uv run pytest tests/roadmap/test_validate_executor.py -v` and require 0 failures.
**Blocks**: CLI integration should not begin until the executor it wraps is verified.

### Gate G5: Phase 4 → Phase 5
**Condition**: IT-03 through IT-06 pass (all CLI paths verified).
**Enforcement**: Run full integration test suite.
**Blocks**: Verification phase assumes CLI is stable; unstable CLI wastes verification effort.

### Gate G6: Phase 5 → Release
**Condition**: All 20 tests pass + architecture verification + performance target met.
**Enforcement**: `uv run pytest && grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty.
**Blocks**: Release. Any failing test or architectural violation must be resolved.

---

## 7. Test Infrastructure Requirements

### Fixture Files
- `tests/roadmap/fixtures/valid-output/` — known-good pipeline output (3 files)
- `tests/roadmap/fixtures/bad-duplicate-did/` — roadmap with duplicate D-0001
- `tests/roadmap/fixtures/bad-missing-milestone/` — roadmap referencing non-existent milestone
- `tests/roadmap/fixtures/bad-untraced-req/` — extraction with FR-099 not in roadmap
- `tests/roadmap/fixtures/bad-crossfile-inconsistency/` — extraction/roadmap FR mismatch

### Test Module Structure
```
tests/roadmap/
├── test_validate_gates.py          # UT-01 through UT-06
├── test_validate_executor.py       # IT-01, IT-02, UT-07
├── test_validate_cli.py            # IT-03 through IT-06
├── test_validate_defects.py        # E2E-01 through E2E-04
├── test_validate_architecture.py   # AT-01 through AT-03
├── test_gate_prompt_alignment.py   # G3 alignment checkpoint
└── fixtures/
    ├── valid-output/
    ├── bad-duplicate-did/
    ├── bad-missing-milestone/
    ├── bad-untraced-req/
    └── bad-crossfile-inconsistency/
```

### Execution Commands
```bash
# Phase 1 gate
uv run pytest tests/roadmap/test_validate_gates.py -v

# Phase 3 gate
uv run pytest tests/roadmap/test_validate_executor.py -v

# Phase 4 gate
uv run pytest tests/roadmap/test_validate_cli.py -v

# Phase 5 full suite
uv run pytest tests/roadmap/ -v --tb=short

# Architecture verification (CI)
grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/ && echo "FAIL: reverse import" && exit 1 || echo "PASS"
```
