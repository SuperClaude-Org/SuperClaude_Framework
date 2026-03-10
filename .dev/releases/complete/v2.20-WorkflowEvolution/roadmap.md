---
spec_source: "spec-workflow-evolution-merged.md"
complexity_score: 0.72
adversarial: true
base_variant: "A (Opus-Architect)"
variant_scores: "A:82 B:63"
convergence_score: 0.72
rounds_completed: 3
---

# v2.20 WorkflowEvolution — Final Merged Roadmap

## 1. Executive Summary

This roadmap implements **fidelity validation** across the SuperClaude pipeline: a spec-fidelity gate validating roadmaps against specifications, a tasklist-fidelity gate validating tasklists against roadmaps, fixes to existing broken gates (REFLECT_GATE, cross-reference resolution), and retrospective-aware extraction. The work spans 5 domains (pipeline, CLI, gate engine, prompt engineering, state management) across 41 requirements (31 functional, 10 non-functional), delivered in 6 phases.

**Architectural thesis**: All new validation is layered — each artifact checks against its immediate upstream only, reuses the existing pipeline/gate framework without new abstractions, and produces structured markdown with YAML frontmatter consistent with existing artifacts.

**Risk concentration**: Disproportionate risk is concentrated in LLM-output consistency (severity classification drift), gate strictness rollouts (artifact regression), and cross-reference validation regressions. The implementation therefore prioritizes deterministic validation surfaces, regression protection, and rollout safety over feature breadth.

**Validation philosophy** (cross-cutting principle): Anything not backed by a test, benchmark, or artifact replay should not be considered done.

**Estimated effort**: 6 phases, ~6 weeks for a single developer familiar with the codebase.

### Scope Summary

| Metric | Value |
|--------|-------|
| Functional requirements | 31 |
| Non-functional requirements | 10 |
| Total requirements | 41 |
| Complexity | Moderate (0.72) |
| Domains | 5 |
| Risks | 8 |
| Dependencies | 9 |
| Success criteria | 14 |

---

## 2. Pre-Implementation Decisions (Days 1–3)

All 8 open questions **must be resolved before implementation begins**. Strong recommendations are provided; 2–3 days with documented decisions in a decision log is sufficient.

### Decisions with Concrete Recommendations

1. **OQ-001 — Cross-reference strictness rollout**: Warning-first for one release, then blocking. De-risks RSK-003.
2. **OQ-004 — Fidelity vs. reflect step ordering**: Spec-fidelity runs *after* reflect. Reflect validates structural quality; fidelity validates content accuracy. Complementary, not redundant.
3. **OQ-006 — Deviation table schema**: 7-column FR-051.4 schema with generic `Upstream Quote`/`Downstream Quote` names. Drop `Source Pair` column; encode it in frontmatter. Publish as a single canonical contract.
4. **OQ-007 — Multi-agent mode**: Defer multi-agent severity resolution (FR-012) to v2.21. Document the conservative merge protocol (highest severity wins). No partial implementation.
5. **OQ-002 — Module placement**: `cli/tasklist/` as a new module — keeps tasklist validation cleanly separated from roadmap generation, follows AC-006. Affects import paths and CLI registration.
6. **OQ-003 — Count cross-validation**: Implement frontmatter-vs-table-row count cross-validation as a warning log, not a gate blocker, to reduce silent LLM inconsistencies.
7. **OQ-005 — MEDIUM severity blocking policy**: Only HIGH-severity deviations block in v2.20. MEDIUM severity is logged but non-blocking. Revisit MEDIUM-blocks policy in v2.21.
8. **OQ-008 — Step timeout vs. NFR mismatch**: 120s is the p95 performance target for NFR measurement; 600s is the hard timeout. Document this distinction explicitly. Measure during implementation phases (Phases 3–4), not only at the end.

### Exit Criteria

- [ ] Decision log published with all 8 resolutions
- [ ] Canonical deviation report schema documented
- [ ] No unresolved blockers for prompt, gate, or CLI design

---

## 3. Phased Implementation Plan

### Phase 1: Foundation — Gate Fixes, Deviation Format, Semantic Checks (Days 4–8)

**Goal**: Fix broken gates, define the canonical deviation report format, establish the testing baseline. Addresses the two highest-impact risks (RSK-003, RSK-006) before building new features.

**Milestone**: All existing tests pass with fixed gates; deviation format documented and unit-tested.

#### Deliverables

1. **REFLECT_GATE tier promotion** (FR-018)
   - Change enforcement tier from STANDARD to STRICT in `validate_gates.py`
   - Run against existing validation artifacts in `.dev/releases/complete/` to assess blast radius (RSK-006)
   - Update existing tests for STRICT behavior
   - **Analyst recommendation**: Require baseline artifact audit before enabling blocking behavior

2. **Cross-reference resolution fix** (FR-019)
   - Replace always-True stub in `_cross_refs_resolve()` with actual heading-anchor validation
   - Implement as warning-only initially (per OQ-001 resolution)
   - Add unit tests for valid and invalid cross-references (FR-020)

3. **Deviation report format specification** (FR-021, FR-026)
   - Create `docs/reference/deviation-report-format.md` documenting the 7-column schema
   - Publish as canonical contract for all downstream consumers

4. **Severity classification definition** (FR-022, FR-023)
   - Define severity classification (HIGH/MEDIUM/LOW) with concrete examples
   - Include boundary cases and classification rationale

5. **`FidelityDeviation` dataclass** (FR-031)
   - Create dataclass in new `roadmap/fidelity.py` module
   - Implements the 7-column schema programmatically

6. **Semantic check functions** (FR-024, FR-025)
   - Implement `_high_severity_count_zero()` in `roadmap/gates.py`
   - Implement `_tasklist_ready_consistent()` in `roadmap/gates.py`
   - Unit tests for both with edge cases (missing fields, malformed frontmatter)

7. **Resolve OQ-002/OQ-003 as exit criteria** (AC-006, NFR-006): Confirm `cli/tasklist/` module placement; confirm count cross-validation as warning log.

#### Tests (Phase 1)

- Unit: `test_cross_refs_resolve_valid`, `test_cross_refs_resolve_invalid`, `test_cross_refs_resolve_no_refs`, `test_reflect_gate_is_strict`, `test_reflect_gate_semantic_checks_execute`, `test_high_severity_count_zero_pass`, `test_high_severity_count_zero_fail`, `test_high_severity_count_zero_missing_field`, `test_tasklist_ready_consistent_pass`, `test_tasklist_ready_consistent_fail`, `test_fidelity_deviation_dataclass`
- Integration: `test_cross_refs_resolve_in_merge_gate`
- Regression: `uv run pytest tests/roadmap/` — 0 failures (SC-010)

#### Exit Criteria

- [ ] All existing tests pass (NFR-004)
- [ ] `_cross_refs_resolve()` correctly rejects dangling references
- [ ] Semantic check functions have 100% branch coverage
- [ ] Deviation format reference doc exists
- [ ] OQ-002 and OQ-003 documented in decision log
- [ ] No new executor/process framework introduced (NFR-006 — verified by code review)

---

### Phase 2: Spec-Fidelity Gate (Days 9–15)

**Goal**: Implement the spec-fidelity prompt, gate, pipeline step, and state persistence.

**Milestone**: Pipeline blocks on HIGH-severity spec-vs-roadmap deviations; degraded mode handles agent failure gracefully.

#### Deliverables

1. **Spec-fidelity prompt builder** (FR-001, FR-002, FR-003, FR-004)
   - `build_spec_fidelity_prompt()` in `roadmap/prompts.py`
   - Prompt instructs comparison of signatures, data models, gates, CLI options, NFRs
   - Requires quoting both spec and roadmap text for each deviation
   - Structured YAML frontmatter output with severity counts and `tasklist_ready`
   - Explicit severity definitions embedded in prompt to reduce LLM classification drift (RSK-007)

2. **SPEC_FIDELITY_GATE** (FR-005, FR-006, FR-007)
   - New gate in `roadmap/gates.py` with STRICT enforcement
   - Blocking logic: `high_severity_count > 0` → block
   - Degraded pass-through: `validation_complete: false` AND `fidelity_check_attempted: true` → warn, continue

3. **Pipeline step integration** (FR-008, FR-009, FR-010)
   - New `spec-fidelity` step in `_build_steps()` in `roadmap/executor.py`
   - Positioned after test-strategy (per OQ-004 resolution: after reflect)
   - Timeout: 600s, retry_limit: 1, output: `{output_dir}/spec-fidelity.md`
   - `--no-validate` does NOT skip this step (FR-010, AC-005)

4. **State persistence and degraded reporting** (FR-011, FR-030, FR-051.6)
   - Write `fidelity_status: pass|fail|skipped|degraded` to `.roadmap-state.json`
   - On agent failure after retry exhaustion: produce degraded report with `validation_complete: false`
   - Degraded reports must explicitly name the failed agent(s) and reason (timeout / API error / malformed output)
   - Include agent error summary in degraded report body
   - Treat state persistence as part of contract, not incidental metadata

5. **Performance measurement**: Measure step execution time against 120s p95 target during this phase, not deferred.

#### Tests (Phase 2)

- Unit: `test_build_spec_fidelity_prompt_includes_severity_defs`, `test_build_spec_fidelity_prompt_requires_quotes`, `test_build_spec_fidelity_prompt_structured_output`, `test_spec_fidelity_gate_criteria`, `test_spec_fidelity_gate_blocks_high`, `test_spec_fidelity_gate_passes_clean`, `test_spec_fidelity_gate_degraded_passthrough`, `test_spec_fidelity_step_inputs`, `test_fidelity_deviation_invalid_severity`, `test_state_persistence_writes_fidelity_status`, `test_degraded_report_not_clean_pass` (NFR-007)
- Integration: `test_spec_fidelity_blocks_on_high_deviation` (SC-001), `test_spec_fidelity_passes_clean_roadmap` (SC-002), `test_degraded_fidelity_pipeline_continues` (SC-007), `test_pipeline_includes_spec_fidelity_step` (SC-014)
- Performance: Measure step execution time against 120s target (SC-011)

#### Exit Criteria

- [ ] SC-001, SC-002, SC-007, SC-008, SC-014 verified
- [ ] Spec-fidelity step runs within 120s on representative spec (NFR-001)
- [ ] Pipeline time overhead ≤5% excluding new step (SC-012)
- [ ] All Phase 1 tests still pass
- [ ] Degraded reports distinguishable from clean passes (NFR-007)

---

### Phase 3: Tasklist Fidelity & CLI (Days 16–22)

**Goal**: Implement tasklist validation as a standalone CLI subcommand with its own fidelity gate.

**Milestone**: `superclaude tasklist validate` catches fabricated traceability IDs and missing deliverables.

#### Deliverables

1. **Tasklist-fidelity prompt builder** (FR-013, FR-014)
   - `build_tasklist_fidelity_prompt()` — checks deliverable coverage, signature preservation, traceability ID validity, dependency chain correctness
   - Reuses deviation report format from Phase 1
   - **Validation layering guard**: Prompt and tests must enforce immediate-upstream-only checks (roadmap→tasklist, NOT spec→tasklist)

2. **TASKLIST_FIDELITY_GATE** (FR-015)
   - STRICT enforcement, blocks on `high_severity_count > 0`
   - Reuses `_high_severity_count_zero()` and `_tasklist_ready_consistent()` from Phase 1

3. **CLI subcommand** (FR-016, FR-017)
   - `superclaude tasklist validate <output-dir>` with options: `--roadmap-file`, `--tasklist-dir`, `--model`, `--max-turns`, `--debug`
   - Exit code 1 on HIGH-severity deviations
   - Output: `{output_dir}/tasklist-fidelity.md`
   - Standalone-invocable (not pipeline-coupled)
   - Module: `src/superclaude/cli/tasklist/` (per OQ-002 resolution)

4. **Performance measurement**: Tasklist validation timed against 120s target during this phase.

#### Tests (Phase 3)

- Unit: `test_build_tasklist_fidelity_prompt_covers_deliverables`, `test_build_tasklist_fidelity_prompt_checks_traceability`, `test_tasklist_fidelity_gate_blocks_high`, `test_tasklist_fidelity_gate_passes_clean`, `test_tasklist_validates_against_roadmap_not_spec`
- Integration: `test_tasklist_validate_cli_options`, `test_tasklist_validate_exit_code_on_high`
- E2E: `test_tasklist_validate_catches_fabricated_traceability` against v2.19 artifacts (SC-005)
- Performance: Tasklist validation within 120s (NFR-002, SC-011)

#### Exit Criteria

- [ ] SC-005, SC-009, SC-013 verified
- [ ] CLI subcommand registered and help text renders
- [ ] Deviation reports 100% parseable (NFR-005)
- [ ] `test_tasklist_validates_against_roadmap_not_spec` passes (validation layering guard)
- [ ] All Phase 1–2 tests still pass

---

### Phase 4: Retrospective Wiring, Integration Hardening & Rollout Validation (Days 23–28)

**Goal**: Wire retrospective context into extraction, harden integration, finalize documentation, validate rollout safety.

**Milestone**: Full pipeline runs end-to-end with all new gates active; retrospective content influences extraction; rollout concerns verified.

#### Deliverables

1. **Retrospective parameter wiring** (FR-027, FR-028, FR-029)
   - `build_extract_prompt()` accepts `retrospective_content: str | None`
   - `RoadmapConfig` extended with `retrospective_file: Path | None`
   - CLI `roadmap run --retrospective <path>` flag
   - Missing file → extraction proceeds normally (no error)
   - Prompt frames retrospective as "areas to watch" not requirements (RSK-004 mitigation)

2. **Multi-agent severity resolution** (FR-012) — **Documentation only**
   - Document the conservative merge protocol (highest severity wins, `validation_complete: false` if any agent fails)
   - Full implementation deferred to v2.21

3. **Full pipeline integration run**
   - Run full pipeline against 3+ existing specs from `.dev/releases/complete/`
   - Document pass/fail results per spec

4. **Cross-reference warning mode verification**
   - Verify cross-reference warning mode works without blocking
   - Confirm no false-positive blocks on existing artifacts

5. **Pipeline performance measurement** (SC-012)
   - Measure total pipeline time delta before/after new gates
   - Verify ≤5% overhead excluding new step

6. **`--no-validate` behavior verification** (SC-014)
   - Verify `--no-validate` does NOT skip fidelity step
   - Document expected behavior for all skip/validate flag combinations

7. **Historical artifact replay validation** (NFR-004, NFR-006)
   - Replay historical artifacts from `.dev/releases/complete/` against stricter gates
   - Document failure reasons per artifact for migration planning

8. **Degraded-state semantics documentation**
   - Document failure-state semantics for degraded reports
   - Ensure team can distinguish clean pass, fail, skipped, and degraded states

9. **Monitoring metrics definition**
   - Define monitoring metrics: false positive rate, degraded-run frequency, pipeline time drift, LLM severity drift
   - Define rollback trigger thresholds for gate strictness

10. **Rollback plan**
    - Prepare rollback plan if regressions appear in stored artifacts
    - Document rollback procedure for gate strictness changes

11. **PLANNING.md pipeline documentation update**
    - Update `PLANNING.md` with new pipeline step documentation

12. **CLI help text update**
    - Update CLI help text for new subcommands and flags

13. **Deviation format reference finalization** (FR-026)
    - Deviation format reference doc finalized and reviewed

14. **Operational guidance documentation**
    - Document fidelity status meanings and expected output artifacts
    - Include examples of each status state

#### Tests (Phase 4)

- Unit: `test_extract_prompt_with_retrospective` (SC-006), `test_extract_prompt_without_retrospective`, `test_extract_prompt_retrospective_as_advisory`, `test_roadmap_config_retrospective_field`
- Integration: `test_retrospective_flag_missing_file_no_error`, `test_full_pipeline_with_fidelity`
- E2E: Full pipeline run against existing specs — no regressions

#### Exit Criteria

- [ ] SC-006, SC-010, SC-012 verified
- [ ] All 14 success criteria passing
- [ ] Documentation updated
- [ ] No test regressions across entire suite
- [ ] Historical artifact replay completed with results documented
- [ ] Rollback plan documented and tested
- [ ] Monitoring metrics defined
- [ ] Team can distinguish clean pass, fail, skipped, and degraded states

---

### Phase 5: Release Readiness Validation (Days 29–30)

**Goal**: Final validation that all gates pass, artifacts are consistent, and release criteria are met.

**Milestone**: All success criteria verified; pipeline artifacts archived; release sign-off complete.

#### Deliverables

1. **Full pipeline validation run with all gates active**
   - Execute complete pipeline against representative specs with all new and existing gates enabled
   - Confirm no regressions from Phase 4 hardening
   - Verify gate interaction ordering (reflect → spec-fidelity → tasklist-fidelity)

2. **Release artifact archive**
   - Verify all `.dev/releases/` outputs are present and well-formed
   - Archive final validation results alongside release artifacts
   - Confirm deviation reports, state files, and documentation are complete and consistent

3. **Release sign-off checklist completion**
   - Walk through all 14 success criteria with passing evidence
   - Document any known limitations or deferred items (e.g., FR-012 multi-agent deferred to v2.21)
   - Record final pipeline timing baselines for future regression comparison

#### Tests (Phase 5)

- Full suite: `uv run pytest` — 0 failures across all test directories
- E2E: Full pipeline run with all gates active — clean pass on representative spec
- Validation: All 14 SC-* criteria independently verified with evidence

#### Exit Criteria

- [ ] All 14 success criteria passing
- [ ] No test regressions across entire suite
- [ ] All artifacts archived in `.dev/releases/`
- [ ] Release sign-off documented with evidence for each criterion

---
## 4. Risk Assessment & Mitigation

### Risk Priority Order

1. **Ambiguity elimination** — resolve schema and open questions before code
2. **Gate correctness** — fix broken gates before building new ones
3. **Regression containment** — artifact replay before strict enforcement
4. **Deterministic output parsing** — semantic guardrails over prompt-only trust
5. **Performance overhead control** — measure during implementation, not after
6. **Rollout safety** — warning-first enforcement with monitoring

### Risk Register

| ID | Risk | Severity | Phase | Mitigation | Residual | Analyst Recommendation |
|----|------|----------|-------|------------|----------|----------------------|
| RSK-003 | Cross-ref fix breaks existing roadmaps | Medium | 1 | Warning-only mode first; test against existing artifacts | Low | Require baseline artifact audit before enabling blocking behavior |
| RSK-006 | REFLECT_GATE promotion breaks reports | Medium | 1 | Test against `.dev/releases/complete/` artifacts before merging | Low | Replay strict gates against known corpus; log exact failure reasons for migration |
| RSK-007 | LLM severity classification drift | Medium | 2 | Explicit severity definitions in prompt; deterministic gate checks on frontmatter | Medium | Prioritize deterministic parser and semantic guardrails over prompt-only trust |
| RSK-001 | LLM count inconsistency (frontmatter vs table) | Medium | 2 | Gate checks frontmatter only; `_tasklist_ready_consistent` cross-validates; warning log for count mismatches | Low | Add count/table cross-validation as warning to track disagreement frequency |
| RSK-005 | Tasklist token cost exceeds budget | Medium | 3 | Concatenate index + 2 most relevant phases; limit input size | Low | Bounded input prevents runaway costs |
| RSK-004 | Retrospective content biases extraction | Low | 4 | Prompt frames as "areas to watch" not requirements; test prompt composition explicitly | Low | Keep extraction independent; retrospective sharpens scrutiny, not scope |
| RSK-002 | Large spec pipeline time exceeds timeout | Low | 2 | 600s timeout; future summarization for >100KB specs | Low | Timeout is safety net; measure continuously |
| RSK-008 | State file corruption or ambiguous status | Low | 2 | Additive writes; single-process execution assumption; validate allowed status enum values | Low | Treat state persistence as part of contract, not incidental metadata |

---

## 5. Resource Requirements & Dependencies

### External Dependencies

| Dependency | Phase | Risk if Unavailable |
|------------|-------|---------------------|
| Claude API (DEP-006) | 2, 3 | Blocks fidelity validation entirely — no fallback |
| Click ≥8.0.0 (DEP-003) | 3 | Already in project deps — no risk |
| Python ≥3.10 (AC-007) | All | Already required — no risk |

### Internal Dependencies

| Dependency | Phase | Notes |
|------------|-------|-------|
| Pipeline framework (DEP-001) | 2 | Read-only usage; no modifications |
| Roadmap module (DEP-002) | 1–4 | Modified in-place; most changes additive |
| Existing test suite (DEP-007) | 1 | Regression baseline; must pass before and after |
| Existing pipeline artifacts (DEP-009) | 1, 4 | Used for regression testing gate fixes |
| `.roadmap-state.json` (DEP-008) | 2 | Additive field only |

### New Files Created

- `src/superclaude/cli/roadmap/fidelity.py` — `FidelityDeviation` dataclass, fidelity utility functions
- `src/superclaude/cli/tasklist/` — new module (`__init__.py`, `commands.py`, `executor.py`, `gates.py`, `prompts.py`)
- `docs/reference/deviation-report-format.md` — canonical format specification
- `tests/roadmap/test_fidelity.py` — fidelity-specific tests
- `tests/tasklist/test_validate.py` — tasklist validation tests

### Modified Files

- `src/superclaude/cli/roadmap/gates.py` — add semantic checks, SPEC_FIDELITY_GATE
- `src/superclaude/cli/roadmap/validate_gates.py` — REFLECT_GATE tier promotion
- `src/superclaude/cli/roadmap/executor.py` — add spec-fidelity step
- `src/superclaude/cli/roadmap/prompts.py` — add fidelity and retrospective prompts
- `src/superclaude/cli/roadmap/models.py` — extend RoadmapConfig
- `src/superclaude/cli/roadmap/commands.py` — add `--retrospective` flag
- `src/superclaude/cli/main.py` — register `tasklist` command group
- `tests/roadmap/test_gates.py` — update for STRICT REFLECT_GATE, add cross-ref tests

---

## 6. Success Criteria & Validation Approach

### Validation Matrix

| Criterion | Method | Phase | Test Name | Automated |
|-----------|--------|-------|-----------|-----------|
| SC-001: Fidelity blocks HIGH | Integration test | 2 | `test_spec_fidelity_blocks_on_high_deviation` | Yes |
| SC-002: Fidelity passes clean | Integration test | 2 | `test_spec_fidelity_passes_clean_roadmap` | Yes |
| SC-003: Cross-ref enforced | Unit test | 1 | `test_cross_refs_resolve_invalid` | Yes |
| SC-004: REFLECT_GATE executes | Unit test | 1 | `test_reflect_gate_semantic_checks_execute` | Yes |
| SC-005: Tasklist catches fabrication | E2E test (v2.19 artifacts) | 3 | `test_tasklist_validate_catches_fabricated_traceability` | Yes |
| SC-006: Retrospective reaches extraction | Unit test | 4 | `test_extract_prompt_with_retrospective` | Yes |
| SC-007: Degraded non-blocking | Integration test | 2 | `test_degraded_fidelity_pipeline_continues` | Yes |
| SC-008: State records fidelity | Integration test | 2 | `test_state_persistence_writes_fidelity_status` | Yes |
| SC-009: tasklist_ready consistent | Unit test | 1 | `test_tasklist_ready_consistent_pass/fail` | Yes |
| SC-010: No test regression | Full suite | All | `uv run pytest tests/roadmap/` | Yes |
| SC-011: Execution time ≤120s | Timed execution | 2, 3 | Benchmark during phase | Semi |
| SC-012: Pipeline overhead ≤5% | Baseline comparison | 4 | Before/after pipeline timing | Semi |
| SC-013: Reports 100% parseable | Unit test | 1 | `test_fidelity_deviation_dataclass` + format tests | Yes |
| SC-014: --no-validate doesn't skip fidelity | Integration test | 2 | `test_pipeline_includes_spec_fidelity_step` | Yes |

### Test Coverage Targets

- **Unit tests**: 24 (all semantic checks, dataclasses, prompt builders, gate logic, validation layering)
- **Integration tests**: 8 (pipeline step behavior, CLI subcommand, state persistence)
- **E2E tests**: 4 (full pipeline runs, tasklist validation against real artifacts)
- **Regression**: 100% existing test pass rate maintained at every phase boundary

---

## 7. Timeline Summary

| Phase | Duration | Days | Key Deliverable | Dependencies |
|-------|----------|------|----------------|--------------|
| Pre-impl decisions | 2–3 days | 1–3 | All 8 OQs resolved, decision log published | Stakeholder input |
| Phase 1: Foundation | 5 days | 4–8 | Gate fixes, deviation format, semantic checks | Decisions complete |
| Phase 2: Spec-Fidelity | 7 days | 9–15 | Pipeline fidelity gate, state persistence | Phase 1 |
| Phase 3: Tasklist CLI | 7 days | 16–22 | CLI subcommand, tasklist fidelity gate | Phase 1 (format reuse) |
| Phase 4: Retrospective & Hardening | 6 days | 23–28 | Retrospective wiring, integration tests, rollout validation, docs | Phase 2, Phase 3 |
| Phase 5: Release Readiness | 2 days | 29–30 | Full validation run, artifact archive, release sign-off | Phase 4 |

**Total**: ~30 working days (~6 weeks single developer).

**Critical path**: Pre-impl decisions → Phase 1 → Phase 2 → Phase 4 → Phase 5.

**Parallelization opportunity**: Phases 2 and 3 branch independently from Phase 1 but share `roadmap/gates.py`. Limited parallelism is possible on non-overlapping modules (prompt builders, CLI wiring), but context-switching overhead for a single developer reduces the benefit. With disciplined module separation, total could compress to ~26 days (~5 weeks).

**Schedule risk**: The largest schedule risk is not implementation volume but decision latency on open questions and unexpected regressions from stricter gate enforcement. If cross-reference or REFLECT strictness causes broad artifact failures, the rollout portion of Phase 4 should split into: (1) implementation complete, (2) warning-first observation window, (3) blocking enforcement activation.
