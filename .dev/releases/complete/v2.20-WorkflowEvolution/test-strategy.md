---
validation_milestones: 6
interleave_ratio: 0.83
---

# v2.20 WorkflowEvolution — Comprehensive Test Strategy

## 1. Validation Milestones Mapped to Roadmap Phases

### Milestone 0: Pre-Implementation Decision Validation (Days 1–3)
**Gate**: All 8 open questions resolved with documented rationale.

| Validation Item | Method | Acceptance Criteria |
|-----------------|--------|---------------------|
| Decision log completeness | Manual review | All 8 OQs have written resolutions with rationale |
| Deviation report schema finalized | Document review | Single canonical 7-column schema published |
| Module placement confirmed | Document review | `cli/tasklist/` decision recorded |
| Timeout semantics documented | Document review | 120s p95 vs 600s hard timeout distinction explicit |

### Milestone 1: Foundation Verified (Day 8)
**Gate**: Existing tests green + new gate fixes validated + deviation format unit-tested.

| SC Criteria | Test Name | Type | Automated |
|-------------|-----------|------|-----------|
| SC-003 | `test_cross_refs_resolve_valid` | Unit | Yes |
| SC-003 | `test_cross_refs_resolve_invalid` | Unit | Yes |
| SC-004 | `test_reflect_gate_semantic_checks_execute` | Unit | Yes |
| SC-009 | `test_tasklist_ready_consistent_pass` | Unit | Yes |
| SC-009 | `test_tasklist_ready_consistent_fail` | Unit | Yes |
| SC-013 | `test_fidelity_deviation_dataclass` | Unit | Yes |
| SC-010 | `uv run pytest tests/roadmap/` | Regression | Yes |

### Milestone 2: Spec-Fidelity Gate Operational (Day 15)
**Gate**: Pipeline blocks on HIGH deviations; degraded mode works; state persists.

| SC Criteria | Test Name | Type | Automated |
|-------------|-----------|------|-----------|
| SC-001 | `test_spec_fidelity_blocks_on_high_deviation` | Integration | Yes |
| SC-002 | `test_spec_fidelity_passes_clean_roadmap` | Integration | Yes |
| SC-007 | `test_degraded_fidelity_pipeline_continues` | Integration | Yes |
| SC-008 | `test_state_persistence_writes_fidelity_status` | Integration | Yes |
| SC-014 | `test_pipeline_includes_spec_fidelity_step` | Integration | Yes |
| SC-011 | Spec-fidelity benchmark ≤120s | Performance | Semi |
| SC-010 | Full regression suite | Regression | Yes |

### Milestone 3: Tasklist CLI Functional (Day 22)
**Gate**: CLI subcommand works; catches fabricated traceability; validates against roadmap only.

| SC Criteria | Test Name | Type | Automated |
|-------------|-----------|------|-----------|
| SC-005 | `test_tasklist_validate_catches_fabricated_traceability` | E2E | Yes |
| NFR-010 | `test_tasklist_validates_against_roadmap_not_spec` | Unit | Yes |
| — | `test_tasklist_validate_cli_options` | Integration | Yes |
| — | `test_tasklist_validate_exit_code_on_high` | Integration | Yes |
| SC-011 | Tasklist validation benchmark ≤120s | Performance | Semi |
| SC-013 | `test_tasklist_fidelity_report_parseable` | Unit | Yes |
| SC-010 | Full regression suite | Regression | Yes |

### Milestone 4: Retrospective & Integration Hardened (Day 28)
**Gate**: Full pipeline E2E with all gates active; retrospective wiring verified; rollout safety confirmed.

| SC Criteria | Test Name | Type | Automated |
|-------------|-----------|------|-----------|
| SC-006 | `test_extract_prompt_with_retrospective` | Unit | Yes |
| — | `test_extract_prompt_without_retrospective` | Unit | Yes |
| — | `test_extract_prompt_retrospective_as_advisory` | Unit | Yes |
| — | `test_retrospective_flag_missing_file_no_error` | Integration | Yes |
| SC-012 | Pipeline overhead ≤5% baseline comparison | Performance | Semi |
| — | `test_full_pipeline_with_fidelity` | E2E | Yes |
| SC-010 | Full regression suite | Regression | Yes |

### Milestone 5: Release Readiness (Day 28+)
**Gate**: All 14 success criteria pass; documentation complete; rollback plan tested.

| Validation Item | Method | Acceptance Criteria |
|-----------------|--------|---------------------|
| All 14 SC criteria | Automated + semi-automated | 14/14 pass |
| Historical artifact replay | Manual + scripted | No regressions against `.dev/releases/complete/` |
| Documentation review | Manual | PLANNING.md, CLI help, deviation format doc updated |
| Rollback plan | Documented procedure | Gate strictness can revert to warning-only |

---

## 2. Test Categories

### 2.1 Unit Tests (24 tests)

Tests for individual functions in isolation. Mock LLM outputs and file I/O.

#### Phase 1 — Gate Fixes & Foundations (9 tests)

| Test | Target | Input | Expected | Risk Coverage |
|------|--------|-------|----------|---------------|
| `test_cross_refs_resolve_valid` | `_cross_refs_resolve()` | Markdown with valid heading anchors | `True` | RSK-003 |
| `test_cross_refs_resolve_invalid` | `_cross_refs_resolve()` | Markdown with dangling `[ref](#missing)` | `False` | RSK-003 |
| `test_cross_refs_resolve_empty` | `_cross_refs_resolve()` | Markdown with no cross-references | `True` | RSK-003 |
| `test_reflect_gate_semantic_checks_execute` | REFLECT_GATE at STRICT | Valid validation report | Semantic checks run (not skipped) | RSK-006 |
| `test_high_severity_count_zero_pass` | `_high_severity_count_zero()` | Frontmatter: `high_severity_count: 0` | `True` | — |
| `test_high_severity_count_zero_fail` | `_high_severity_count_zero()` | Frontmatter: `high_severity_count: 3` | `False` | — |
| `test_high_severity_count_zero_missing_field` | `_high_severity_count_zero()` | Frontmatter without field | `False` | RSK-001 |
| `test_tasklist_ready_consistent_pass` | `_tasklist_ready_consistent()` | `tasklist_ready: true`, `high_severity_count: 0`, `validation_complete: true` | `True` | — |
| `test_tasklist_ready_consistent_fail` | `_tasklist_ready_consistent()` | `tasklist_ready: true`, `high_severity_count: 2` | `False` | NFR-008 |

#### Phase 2 — Spec-Fidelity (6 tests)

| Test | Target | Input | Expected | Risk Coverage |
|------|--------|-------|----------|---------------|
| `test_fidelity_deviation_dataclass` | `FidelityDeviation` | Valid field values | Dataclass creates, serializes | — |
| `test_fidelity_deviation_invalid_severity` | `FidelityDeviation` | `severity="CRITICAL"` | Validation error | RSK-007 |
| `test_build_spec_fidelity_prompt_includes_severity_defs` | `build_spec_fidelity_prompt()` | Spec + roadmap strings | Output contains HIGH/MEDIUM/LOW definitions | RSK-007 |
| `test_build_spec_fidelity_prompt_requires_quotes` | `build_spec_fidelity_prompt()` | Spec + roadmap strings | Output instructs quoting both sources | FR-002 |
| `test_build_spec_fidelity_prompt_structured_output` | `build_spec_fidelity_prompt()` | Spec + roadmap strings | Output requests YAML frontmatter fields | FR-003 |
| `test_state_persistence_writes_fidelity_status` | State writer | Fidelity result | `.roadmap-state.json` contains `fidelity_status` | RSK-008 |

#### Phase 3 — Tasklist Fidelity (5 tests)

| Test | Target | Input | Expected | Risk Coverage |
|------|--------|-------|----------|---------------|
| `test_build_tasklist_fidelity_prompt_covers_deliverables` | `build_tasklist_fidelity_prompt()` | Roadmap + tasklist strings | Prompt checks deliverable coverage | FR-013 |
| `test_build_tasklist_fidelity_prompt_checks_traceability` | `build_tasklist_fidelity_prompt()` | Roadmap + tasklist strings | Prompt validates traceability IDs | FR-013 |
| `test_tasklist_fidelity_gate_blocks_high` | `TASKLIST_FIDELITY_GATE` | Report with `high_severity_count: 1` | Gate blocks | FR-015 |
| `test_tasklist_fidelity_gate_passes_clean` | `TASKLIST_FIDELITY_GATE` | Report with `high_severity_count: 0` | Gate passes | FR-015 |
| `test_tasklist_validates_against_roadmap_not_spec` | `build_tasklist_fidelity_prompt()` | Roadmap + tasklist (no spec) | Prompt references roadmap as upstream, not spec | NFR-010 |

#### Phase 4 — Retrospective (4 tests)

| Test | Target | Input | Expected | Risk Coverage |
|------|--------|-------|----------|---------------|
| `test_extract_prompt_with_retrospective` | `build_extract_prompt()` | `retrospective_content="known issue X"` | Prompt contains "Known Issues from Prior Releases" | RSK-004 |
| `test_extract_prompt_without_retrospective` | `build_extract_prompt()` | `retrospective_content=None` | No retrospective section in prompt | — |
| `test_extract_prompt_retrospective_as_advisory` | `build_extract_prompt()` | `retrospective_content="issue Y"` | Prompt frames as "areas to watch" not requirements | RSK-004 |
| `test_roadmap_config_retrospective_field` | `RoadmapConfig` | `retrospective_file=Path("retro.md")` | Field stored, accessible | FR-028 |

### 2.2 Integration Tests (8 tests)

Tests crossing module boundaries: pipeline step execution, CLI invocation, gate-to-executor interaction. Use fixture-based LLM output stubs (pre-recorded responses, not live API calls).

| Test | Modules Crossed | Phase | Fixture Strategy |
|------|----------------|-------|------------------|
| `test_spec_fidelity_blocks_on_high_deviation` | prompts → executor → gates | 2 | Stub agent output with HIGH deviations |
| `test_spec_fidelity_passes_clean_roadmap` | prompts → executor → gates | 2 | Stub agent output with 0 deviations |
| `test_degraded_fidelity_pipeline_continues` | executor → gates → state | 2 | Stub agent timeout/failure |
| `test_pipeline_includes_spec_fidelity_step` | executor (`_build_steps`) | 2 | Inspect step list with `--no-validate` |
| `test_tasklist_validate_cli_options` | CLI → tasklist module | 3 | Click test runner with `--help` and valid args |
| `test_tasklist_validate_exit_code_on_high` | CLI → gates | 3 | Stub agent output with HIGH deviations |
| `test_retrospective_flag_missing_file_no_error` | CLI → config → executor | 4 | Pass non-existent path |
| `test_full_pipeline_with_fidelity` | Full pipeline | 4 | Stub all agent outputs, run E2E |

### 2.3 E2E Tests (4 tests)

Full pipeline or CLI execution against real or representative artifacts. Require Claude API access (or recorded responses for CI).

| Test | Artifact Source | Phase | Timeout |
|------|----------------|-------|---------|
| `test_spec_fidelity_against_v219_spec` | `.dev/releases/complete/v2.19/` | 2 | 600s |
| `test_tasklist_validate_catches_fabricated_traceability` | v2.19 artifacts with injected fabricated IDs | 3 | 600s |
| `test_full_pipeline_no_regression` | Representative spec from `.dev/releases/complete/` | 4 | 1200s |
| `test_historical_artifact_replay` | 3+ specs from `.dev/releases/complete/` | 4 | 1800s |

### 2.4 Acceptance Tests (mapped to SC criteria)

Each SC criterion maps to one or more automated tests. Acceptance is defined as all 14 SC criteria passing:

| SC | Acceptance Condition | Test Type |
|----|---------------------|-----------|
| SC-001 | Pipeline halts on HIGH | Integration |
| SC-002 | Pipeline continues on clean | Integration |
| SC-003 | Cross-refs reject dangling | Unit |
| SC-004 | REFLECT_GATE semantic checks run | Unit |
| SC-005 | Fabricated traceability caught | E2E |
| SC-006 | Retrospective reaches extraction prompt | Unit |
| SC-007 | Degraded report non-blocking | Integration |
| SC-008 | State file records fidelity | Integration |
| SC-009 | tasklist_ready consistency enforced | Unit |
| SC-010 | 0 regressions in existing tests | Regression |
| SC-011 | ≤120s execution time | Performance benchmark |
| SC-012 | ≤5% pipeline overhead | Performance benchmark |
| SC-013 | 100% report parseability | Unit |
| SC-014 | --no-validate doesn't skip fidelity | Integration |

---

## 3. Test-Implementation Interleaving Strategy

**Ratio**: 1:2 (one test cycle for every two implementation deliverables)

### Interleaving Pattern per Phase

```
Phase N:
  ├─ Implement deliverable 1
  ├─ Implement deliverable 2
  ├─ TEST CHECKPOINT: Unit tests for deliverables 1–2
  ├─ Implement deliverable 3
  ├─ Implement deliverable 4
  ├─ TEST CHECKPOINT: Unit tests for deliverables 3–4
  ├─ Integration tests for phase
  ├─ REGRESSION GATE: `uv run pytest tests/roadmap/` — 0 failures
  └─ MILESTONE GATE: Phase exit criteria verified
```

### Concrete Interleaving Schedule

**Phase 1 (Days 4–8)**:
- Days 4–5: Implement REFLECT_GATE promotion + cross-ref fix → unit tests for both
- Days 6–7: Implement deviation format + semantic checks → unit tests for both
- Day 8: Phase 1 integration pass, regression gate

**Phase 2 (Days 9–15)**:
- Days 9–10: Implement FidelityDeviation dataclass + prompt builder → unit tests
- Days 11–12: Implement SPEC_FIDELITY_GATE + pipeline step → unit tests + integration tests
- Days 13–14: Implement state persistence + degraded mode → integration tests
- Day 15: Performance benchmark, regression gate, milestone gate

**Phase 3 (Days 16–22)**:
- Days 16–17: Implement tasklist prompt builder → unit tests (including layering guard)
- Days 18–19: Implement TASKLIST_FIDELITY_GATE + CLI subcommand → unit + integration tests
- Days 20–21: E2E test against v2.19 artifacts
- Day 22: Performance benchmark, regression gate, milestone gate

**Phase 4 (Days 23–28)**:
- Days 23–24: Implement retrospective wiring → unit tests
- Days 25–26: Integration hardening → E2E pipeline runs
- Days 27–28: Historical artifact replay, documentation verification, rollout validation

---

## 4. Risk-Based Test Prioritization

Tests are prioritized by the risk they mitigate. Higher-risk tests run first within each phase.

### Priority 1 — Critical (Run first, block on failure)

| Test | Risk | Rationale |
|------|------|-----------|
| `uv run pytest tests/roadmap/` (regression) | RSK-003, RSK-006 | Broken gates are the highest-impact risk; must verify before any new code |
| `test_cross_refs_resolve_invalid` | RSK-003 | Cross-ref fix is the most likely source of regressions |
| `test_reflect_gate_semantic_checks_execute` | RSK-006 | REFLECT_GATE promotion could break existing reports |
| `test_spec_fidelity_blocks_on_high_deviation` | SC-001 | Core safety property of the entire feature |
| `test_tasklist_validates_against_roadmap_not_spec` | NFR-010 | Validation layering is an architectural invariant |

### Priority 2 — High (Run early, investigate on failure)

| Test | Risk | Rationale |
|------|------|-----------|
| `test_build_spec_fidelity_prompt_includes_severity_defs` | RSK-007 | LLM severity drift is medium-severity, ongoing |
| `test_degraded_fidelity_pipeline_continues` | SC-007 | Degraded mode prevents pipeline lockup |
| `test_high_severity_count_zero_missing_field` | RSK-001 | LLM output inconsistency is a known risk |
| `test_tasklist_validate_catches_fabricated_traceability` | SC-005 | Primary motivating use case for tasklist validation |
| `test_historical_artifact_replay` | RSK-003, RSK-006 | Rollout safety depends on no regressions against stored artifacts |

### Priority 3 — Medium (Run in normal cycle)

| Test | Risk | Rationale |
|------|------|-----------|
| `test_extract_prompt_retrospective_as_advisory` | RSK-004 | Low-severity risk, but important for prompt correctness |
| `test_state_persistence_writes_fidelity_status` | RSK-008 | Low-severity, but contract compliance |
| Performance benchmarks (SC-011, SC-012) | RSK-002 | Low severity, measured during implementation |
| `test_fidelity_deviation_dataclass` | — | Structural correctness, low risk |

### Priority 4 — Low (Run in full suite)

| Test | Risk | Rationale |
|------|------|-----------|
| `test_cross_refs_resolve_empty` | RSK-003 | Edge case, low probability |
| `test_extract_prompt_without_retrospective` | — | Default behavior, unlikely to break |
| `test_tasklist_validate_cli_options` | — | CLI plumbing, standard Click testing |
| `test_roadmap_config_retrospective_field` | — | Simple dataclass extension |

---

## 5. Acceptance Criteria per Milestone

### Milestone 0 Exit Criteria
- [ ] Decision log with all 8 OQ resolutions published
- [ ] Canonical deviation report schema (7-column) documented
- [ ] `cli/tasklist/` module placement confirmed
- [ ] Timeout semantics (120s p95 / 600s hard) documented
- [ ] No unresolved blockers for Phases 1–4

### Milestone 1 Exit Criteria
- [ ] `uv run pytest tests/roadmap/` — 0 failures (SC-010)
- [ ] `_cross_refs_resolve()` correctly rejects dangling references (SC-003)
- [ ] `_cross_refs_resolve()` passes valid references (SC-003)
- [ ] REFLECT_GATE semantic checks execute at STRICT tier (SC-004)
- [ ] `_high_severity_count_zero()` — 100% branch coverage (3 cases)
- [ ] `_tasklist_ready_consistent()` — pass and fail cases verified (SC-009)
- [ ] `FidelityDeviation` dataclass instantiates and validates severity (SC-013)
- [ ] `docs/reference/deviation-report-format.md` exists and matches 7-column schema
- [ ] OQ-002, OQ-003 documented in decision log

### Milestone 2 Exit Criteria
- [ ] SC-001: Pipeline blocks on HIGH deviations
- [ ] SC-002: Pipeline passes clean roadmaps
- [ ] SC-007: Degraded fidelity produces warning, continues pipeline
- [ ] SC-008: `.roadmap-state.json` contains `fidelity_status`
- [ ] SC-014: `--no-validate` does not skip spec-fidelity step
- [ ] SC-011: Spec-fidelity ≤120s on representative spec
- [ ] SC-010: All Phase 1 tests still pass
- [ ] Prompt contains explicit severity definitions (RSK-007 mitigation verified)

### Milestone 3 Exit Criteria
- [ ] SC-005: Fabricated traceability IDs caught in v2.19 artifacts
- [ ] SC-013: Tasklist fidelity reports 100% parseable
- [ ] NFR-010: Tasklist validates against roadmap, not spec (layering guard)
- [ ] CLI `superclaude tasklist validate --help` renders correctly
- [ ] Exit code 1 returned on HIGH-severity deviations
- [ ] SC-011: Tasklist validation ≤120s
- [ ] SC-010: All Phase 1–2 tests still pass

### Milestone 4 Exit Criteria
- [ ] SC-006: Retrospective content reaches extraction prompt
- [ ] Missing retrospective file causes no error
- [ ] Retrospective framed as advisory, not requirements (RSK-004)
- [ ] SC-012: Pipeline overhead ≤5% (excluding new step)
- [ ] Full pipeline E2E against 3+ existing specs — no regressions
- [ ] Historical artifact replay completed and documented
- [ ] Rollback plan documented
- [ ] Monitoring metrics defined (false positive rate, degraded frequency, time drift, severity drift)

### Milestone 5 (Release Readiness) Exit Criteria
- [ ] All 14 SC criteria verified (SC-001 through SC-014)
- [ ] All 24 unit tests pass
- [ ] All 8 integration tests pass
- [ ] All 4 E2E tests pass
- [ ] PLANNING.md updated with pipeline step documentation
- [ ] CLI help text updated
- [ ] Deviation format reference doc finalized
- [ ] Team can distinguish: clean pass / fail / skipped / degraded states

---

## 6. Quality Gates Between Phases

### Gate Structure

Each phase boundary enforces a mandatory quality gate before the next phase begins.

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────────┐
│  Milestone 0 │────▶│ Phase 1  │────▶│  Phase 2    │────▶│ Phase 3  │────▶│   Phase 4    │
│  Decisions   │     │Foundation│     │Spec-Fidelity│     │Tasklist  │     │  Hardening   │
└─────────────┘     └──────────┘     └─────────────┘     └──────────┘     └──────────────┘
       │                   │                  │                 │                  │
       ▼                   ▼                  ▼                 ▼                  ▼
   GATE 0              GATE 1             GATE 2            GATE 3             GATE 4
  Decision Log       Regression +       Integration +     E2E + CLI +       Full Pipeline +
  Complete           Unit Tests         Performance       Layering Guard    Artifact Replay
```

### Gate 0: Decision → Phase 1
| Check | Blocking? | Method |
|-------|-----------|--------|
| 8 OQs resolved in decision log | Yes | Manual review |
| Deviation schema published | Yes | File existence check |
| No unresolved blockers | Yes | Manual review |

### Gate 1: Phase 1 → Phase 2
| Check | Blocking? | Method |
|-------|-----------|--------|
| `uv run pytest tests/roadmap/` — 0 failures | Yes | CI |
| 9 Phase 1 unit tests pass | Yes | CI |
| `_cross_refs_resolve()` rejects dangling refs | Yes | Unit test |
| REFLECT_GATE semantic checks execute | Yes | Unit test |
| Deviation format doc exists | Yes | File check |

### Gate 2: Phase 2 → Phase 3
| Check | Blocking? | Method |
|-------|-----------|--------|
| All Phase 1 tests still pass | Yes | CI |
| 6 Phase 2 unit tests pass | Yes | CI |
| 5 Phase 2 integration tests pass | Yes | CI |
| Spec-fidelity ≤120s benchmark | Warning | Manual |
| SC-001, SC-002, SC-007, SC-008, SC-014 verified | Yes | CI |

### Gate 3: Phase 3 → Phase 4
| Check | Blocking? | Method |
|-------|-----------|--------|
| All Phase 1–2 tests still pass | Yes | CI |
| 5 Phase 3 unit tests pass | Yes | CI |
| 2 Phase 3 integration tests pass | Yes | CI |
| SC-005 E2E test passes | Yes | CI (with API access) |
| Layering guard test passes | Yes | CI |
| CLI `--help` renders | Yes | CI |

### Gate 4: Phase 4 → Release
| Check | Blocking? | Method |
|-------|-----------|--------|
| All prior tests pass (24 unit + 8 integration + 4 E2E) | Yes | CI |
| SC-012 pipeline overhead ≤5% | Warning (investigate if >5%) | Benchmark |
| Historical artifact replay — no regressions | Yes | Scripted |
| Documentation updated (3 files minimum) | Yes | Manual review |
| Rollback plan documented | Yes | Manual review |
| All 14 SC criteria green | Yes | CI + manual |

### Regression Policy

**Mandatory at every phase boundary**: `uv run pytest tests/roadmap/` with 0 failures tolerated.

**Test addition is additive**: New tests never replace existing tests. The test count monotonically increases across phases:
- After Phase 1: baseline + 9 unit
- After Phase 2: baseline + 15 unit + 5 integration + 1 E2E
- After Phase 3: baseline + 20 unit + 7 integration + 2 E2E
- After Phase 4: baseline + 24 unit + 8 integration + 4 E2E

### Performance Regression Policy

Measured at Phase 2 and Phase 4:
- **SC-011**: Individual step ≤120s (p95). Failure = investigate, not block (timeout is 600s safety net).
- **SC-012**: Pipeline overhead ≤5%. Failure at >10% = block; 5–10% = investigate.

---

## 7. Test Infrastructure Requirements

### Fixtures Needed

| Fixture | Purpose | Location |
|---------|---------|----------|
| `sample_spec_content` | Representative spec text for prompt testing | `tests/roadmap/conftest.py` |
| `sample_roadmap_content` | Representative roadmap text | `tests/roadmap/conftest.py` |
| `sample_tasklist_content` | Representative tasklist text | `tests/tasklist/conftest.py` |
| `fidelity_report_clean` | Report with 0 HIGH deviations | `tests/roadmap/fixtures/` |
| `fidelity_report_high` | Report with HIGH deviations | `tests/roadmap/fixtures/` |
| `fidelity_report_degraded` | Report with `validation_complete: false` | `tests/roadmap/fixtures/` |
| `v219_artifacts` | Real v2.19 artifacts for E2E | `.dev/releases/complete/v2.19/` |

### CI Configuration

```yaml
test_phases:
  unit:
    command: "uv run pytest tests/ -m 'not integration and not e2e' -v"
    timeout: 120s
    required: true

  integration:
    command: "uv run pytest tests/ -m integration -v"
    timeout: 300s
    required: true

  e2e:
    command: "uv run pytest tests/ -m e2e -v"
    timeout: 1800s
    required: false  # requires API access
    env: [ANTHROPIC_API_KEY]

  regression:
    command: "uv run pytest tests/roadmap/ -v"
    timeout: 120s
    required: true
```

### Test Markers

```python
# New markers for v2.20 tests
pytest.mark.fidelity      # Fidelity-specific tests
pytest.mark.e2e            # End-to-end requiring API
pytest.mark.integration    # Cross-module tests
pytest.mark.performance    # Benchmark tests (opt-in)
pytest.mark.layering       # Validation layering invariant tests
```
