

---
spec_source: "spec-workflow-evolution-merged.md"
complexity_score: 0.72
primary_persona: architect
---

# v2.20 WorkflowEvolution — Project Roadmap

## 1. Executive Summary

This roadmap covers the implementation of **fidelity validation** across the SuperClaude pipeline: a spec-fidelity gate that validates roadmaps against specifications, a tasklist-fidelity gate that validates tasklists against roadmaps, fixes to existing broken gates (REFLECT_GATE, cross-reference resolution), and retrospective-aware extraction. The work spans 5 domains (pipeline, CLI, gate engine, prompt engineering, state management) across 41 requirements (31 functional, 10 non-functional).

**Architectural thesis**: All new validation is layered — each artifact checks against its immediate upstream only, reuses the existing pipeline/gate framework without new abstractions, and produces structured markdown with YAML frontmatter consistent with existing artifacts.

**Key risks**: LLM non-determinism in deviation classification (RSK-007), REFLECT_GATE promotion breaking existing reports (RSK-006), and cross-reference fix breaking existing roadmaps (RSK-003). All are mitigable with artifact regression testing before deployment.

**Estimated effort**: 4 phases, ~3–4 weeks for a single developer familiar with the codebase.

---

## 2. Pre-Implementation Decisions

These open questions **must be resolved before implementation begins**:

1. **OQ-001 — Cross-reference strictness rollout**: Recommend warning-first for one release, then blocking. This de-risks RSK-003.
2. **OQ-004 — Fidelity vs. reflect step ordering**: Recommend spec-fidelity runs *after* reflect. Reflect validates structural quality; fidelity validates content accuracy. They are complementary, not redundant.
3. **OQ-006 — Deviation table schema**: Recommend the 7-column FR-051.4 schema with generic `Upstream Quote`/`Downstream Quote` names (works for both spec→roadmap and roadmap→tasklist). Drop `Source Pair` column; encode it in frontmatter instead.
4. **OQ-007 — Multi-agent mode**: Recommend deferring multi-agent severity resolution (FR-012) to a follow-up. Implement single-agent fidelity first. Document the merge protocol but don't build it in Phase 1–4.

---

## 3. Phased Implementation Plan

### Phase 1: Foundation — Gate Fixes & Deviation Format (Days 1–4)

**Goal**: Fix broken gates, define the canonical deviation report format, establish the testing baseline.

**Milestone**: All existing tests pass with fixed gates; deviation format documented and unit-tested.

#### Deliverables

1. **REFLECT_GATE tier promotion** (FR-018)
   - Change enforcement tier from STANDARD to STRICT in `validate_gates.py`
   - Run against existing validation artifacts in `.dev/releases/complete/` to assess blast radius (RSK-006)
   - Update existing tests for STRICT behavior

2. **Cross-reference resolution fix** (FR-019)
   - Replace always-True stub in `_cross_refs_resolve()` with actual heading-anchor validation
   - Implement as warning-only initially (per OQ-001 resolution)
   - Add unit tests for valid and invalid cross-references (FR-020)

3. **Deviation report format definition** (FR-021, FR-022, FR-023, FR-026)
   - Create `docs/reference/deviation-report-format.md` documenting the 7-column schema
   - Define severity classification (HIGH/MEDIUM/LOW) with concrete examples
   - Create `FidelityDeviation` dataclass (FR-031) in a new `roadmap/fidelity.py` module

4. **Semantic check functions** (FR-024, FR-025)
   - Implement `_high_severity_count_zero()` in `roadmap/gates.py`
   - Implement `_tasklist_ready_consistent()` in `roadmap/gates.py`
   - Unit tests for both with edge cases (missing fields, malformed frontmatter)

#### Tests (Phase 1)
- Unit: `test_cross_refs_resolve_valid`, `test_cross_refs_resolve_invalid`, `test_reflect_gate_semantic_checks_execute`, `test_high_severity_count_zero_*`, `test_tasklist_ready_consistent_*`, `test_fidelity_deviation_dataclass`
- Regression: `uv run pytest tests/roadmap/` — 0 failures (SC-010)

#### Exit Criteria
- [ ] All existing tests pass (NFR-004)
- [ ] `_cross_refs_resolve()` correctly rejects dangling references
- [ ] Semantic check functions have 100% branch coverage
- [ ] Deviation format reference doc exists

---

### Phase 2: Spec-Fidelity Gate (Days 5–10)

**Goal**: Implement the spec-fidelity prompt, gate, pipeline step, and state persistence.

**Milestone**: Pipeline blocks on HIGH-severity spec-vs-roadmap deviations; degraded mode handles agent failure gracefully.

#### Deliverables

1. **Spec-fidelity prompt builder** (FR-001, FR-002, FR-003, FR-004)
   - `build_spec_fidelity_prompt()` in `roadmap/prompts.py`
   - Prompt instructs comparison of signatures, data models, gates, CLI options, NFRs
   - Requires quoting both spec and roadmap text for each deviation
   - Structured YAML frontmatter output with severity counts and `tasklist_ready`

2. **SPEC_FIDELITY_GATE** (FR-005, FR-006, FR-007)
   - New gate in `roadmap/gates.py` with STRICT enforcement
   - Blocking logic: `high_severity_count > 0` → block
   - Degraded pass-through: `validation_complete: false` AND `fidelity_check_attempted: true` → warn, continue

3. **Pipeline step integration** (FR-008, FR-009, FR-010)
   - New `spec-fidelity` step in `_build_steps()` in `roadmap/executor.py`
   - Positioned after test-strategy (per OQ-004 resolution: after reflect)
   - Timeout: 600s, retry_limit: 1, output: `{output_dir}/spec-fidelity.md`
   - `--no-validate` does NOT skip this step (FR-010, AC-005)

4. **State persistence** (FR-011, FR-030)
   - Write `fidelity_status: pass|fail|skipped|degraded` to `.roadmap-state.json`
   - On agent failure after retry exhaustion: produce degraded report with `validation_complete: false`

5. **Resolve OQ-003 during implementation**: Decide whether to cross-validate frontmatter counts against table rows. Recommend implementing as a warning log, not a gate blocker.

6. **Resolve OQ-005 during implementation**: Start with HIGH-only blocking. MEDIUM blocking can be added via gate configuration in a future release.

7. **Resolve OQ-008 during implementation**: Treat 120s as p95 target for NFR measurement, 600s as hard timeout. Document this distinction.

#### Tests (Phase 2)
- Unit: `test_build_spec_fidelity_prompt_*`, `test_spec_fidelity_gate_blocks_high`, `test_spec_fidelity_gate_passes_clean`, `test_spec_fidelity_gate_degraded_passthrough`, `test_state_persistence_writes_fidelity_status`
- Integration: `test_spec_fidelity_blocks_on_high_deviation` (SC-001), `test_spec_fidelity_passes_clean_roadmap` (SC-002), `test_degraded_fidelity_pipeline_continues` (SC-007), `test_pipeline_includes_spec_fidelity_step` (SC-014)
- Performance: Measure step execution time against 120s target (SC-011)

#### Exit Criteria
- [ ] SC-001, SC-002, SC-007, SC-008, SC-014 verified
- [ ] Spec-fidelity step runs within 120s on representative spec (NFR-001)
- [ ] Pipeline time overhead ≤5% excluding new step (SC-012)
- [ ] All Phase 1 tests still pass

---

### Phase 3: Tasklist Fidelity & CLI (Days 11–16)

**Goal**: Implement tasklist validation as a standalone CLI subcommand with its own fidelity gate.

**Milestone**: `superclaude tasklist validate` catches fabricated traceability IDs and missing deliverables.

#### Deliverables

1. **Tasklist-fidelity prompt builder** (FR-013, FR-014)
   - `build_tasklist_fidelity_prompt()` — checks deliverable coverage, signature preservation, traceability ID validity, dependency chain correctness
   - Reuses deviation report format from Phase 1

2. **TASKLIST_FIDELITY_GATE** (FR-015)
   - STRICT enforcement, blocks on `high_severity_count > 0`
   - Reuses `_high_severity_count_zero()` and `_tasklist_ready_consistent()` from Phase 1

3. **CLI subcommand** (FR-016, FR-017)
   - `superclaude tasklist validate <output-dir>` with options: `--roadmap-file`, `--tasklist-dir`, `--model`, `--max-turns`, `--debug`
   - Exit code 1 on HIGH-severity deviations
   - Output: `{output_dir}/tasklist-fidelity.md`
   - Standalone-invocable (not pipeline-coupled)

4. **Resolve OQ-002**: Recommend `cli/tasklist/` as a new module — keeps tasklist validation cleanly separated from roadmap generation, follows AC-006.

#### Tests (Phase 3)
- Unit: `test_build_tasklist_fidelity_prompt_*`, `test_tasklist_fidelity_gate_*`
- Integration: `test_tasklist_validate_cli_options`, `test_tasklist_validate_exit_code_on_high`
- E2E: `test_tasklist_validate_catches_fabricated_traceability` against v2.19 artifacts (SC-005)
- Performance: Tasklist validation within 120s (NFR-002, SC-011)

#### Exit Criteria
- [ ] SC-005, SC-009, SC-013 verified
- [ ] CLI subcommand registered and help text renders
- [ ] Deviation reports 100% parseable (NFR-005)
- [ ] All Phase 1–2 tests still pass

---

### Phase 4: Retrospective Wiring & Integration Hardening (Days 17–21)

**Goal**: Wire retrospective context into extraction, harden integration, finalize documentation.

**Milestone**: Full pipeline runs end-to-end with all new gates active; retrospective content influences extraction.

#### Deliverables

1. **Retrospective parameter wiring** (FR-027, FR-028, FR-029)
   - `build_extract_prompt()` accepts `retrospective_content: str | None`
   - `RoadmapConfig` extended with `retrospective_file: Path | None`
   - CLI `roadmap run --retrospective <path>` flag
   - Missing file → extraction proceeds normally (no error)

2. **Multi-agent severity resolution** (FR-012) — **Documentation only**
   - Document the conservative merge protocol (highest severity wins, `validation_complete: false` if any agent fails)
   - Stub the merge function with `NotImplementedError` gated behind a `--multi-agent` flag
   - Full implementation deferred to v2.21

3. **Integration hardening**
   - Run full pipeline against 3+ existing specs from `.dev/releases/complete/`
   - Verify cross-reference warning mode works without blocking
   - Measure total pipeline time delta (SC-012)
   - Verify `--no-validate` behavior (SC-014)

4. **Documentation updates**
   - Update `PLANNING.md` with new pipeline step documentation
   - Update CLI help text for new subcommands and flags
   - Deviation format reference doc finalized (FR-026)

#### Tests (Phase 4)
- Unit: `test_extract_prompt_with_retrospective` (SC-006), `test_extract_prompt_without_retrospective`
- Integration: `test_retrospective_flag_missing_file_no_error`, `test_full_pipeline_with_fidelity`
- E2E: Full pipeline run against existing specs — no regressions

#### Exit Criteria
- [ ] SC-006, SC-010, SC-012 verified
- [ ] All 14 success criteria passing
- [ ] Documentation updated
- [ ] No test regressions across entire suite

---

## 4. Risk Assessment & Mitigation

| Risk | Severity | Phase | Mitigation | Residual Risk |
|------|----------|-------|------------|---------------|
| RSK-003: Cross-ref fix breaks existing roadmaps | Medium | 1 | Warning-only mode first; test against existing artifacts | Low — warning mode is non-blocking |
| RSK-006: REFLECT_GATE promotion breaks reports | Medium | 1 | Test against `.dev/releases/complete/` artifacts before merging | Low — known artifact corpus |
| RSK-007: LLM severity classification drift | Medium | 2 | Explicit severity definitions in prompt (FR-023); deterministic gate checks on frontmatter | Medium — inherent to LLM-as-judge |
| RSK-001: LLM count inconsistency | Medium | 2 | Gate checks frontmatter only; `_tasklist_ready_consistent` cross-validates | Low — frontmatter is authoritative |
| RSK-005: Tasklist token cost | Medium | 3 | Concatenate index + 2 most relevant phases; limit input size | Low — bounded input |
| RSK-004: Retrospective bias | Low | 4 | Prompt frames as "areas to watch" not requirements | Low — prompt engineering |
| RSK-002: Large spec pipeline time | Low | 2 | 600s timeout; future summarization for >100KB specs | Low — timeout is safety net |
| RSK-008: State file corruption | Low | 2 | Additive writes; single-process execution assumption | Low — acceptable for current architecture |

**Risk-ordered implementation**: Phase 1 addresses the two highest-impact risks (RSK-003, RSK-006) first, before building new features on top.

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
- `src/superclaude/cli/tasklist/` — new module (commands.py, gates.py, prompts.py)
- `docs/reference/deviation-report-format.md` — format specification
- `tests/roadmap/test_fidelity.py` — fidelity-specific tests
- `tests/tasklist/test_validate.py` — tasklist validation tests

### Modified Files
- `src/superclaude/cli/roadmap/gates.py` — add semantic checks, SPEC_FIDELITY_GATE
- `src/superclaude/cli/roadmap/validate_gates.py` — REFLECT_GATE tier promotion
- `src/superclaude/cli/roadmap/executor.py` — add spec-fidelity step
- `src/superclaude/cli/roadmap/prompts.py` — add fidelity and retrospective prompts
- `src/superclaude/cli/roadmap/models.py` — extend RoadmapConfig
- `src/superclaude/cli/roadmap/commands.py` — add --retrospective flag
- `tests/roadmap/test_gates.py` — update for STRICT REFLECT_GATE, add cross-ref tests

---

## 6. Success Criteria & Validation Approach

### Validation Matrix

| Criterion | Method | Phase | Automated |
|-----------|--------|-------|-----------|
| SC-001: Fidelity blocks HIGH | Integration test | 2 | Yes |
| SC-002: Fidelity passes clean | Integration test | 2 | Yes |
| SC-003: Cross-ref enforced | Unit test | 1 | Yes |
| SC-004: REFLECT_GATE executes | Unit test | 1 | Yes |
| SC-005: Tasklist catches fabrication | E2E test (v2.19 artifacts) | 3 | Yes |
| SC-006: Retrospective reaches extraction | Unit test | 4 | Yes |
| SC-007: Degraded non-blocking | Integration test | 2 | Yes |
| SC-008: State records fidelity | Integration test | 2 | Yes |
| SC-009: tasklist_ready consistent | Unit test | 1 | Yes |
| SC-010: No test regression | `uv run pytest tests/roadmap/` | All | Yes |
| SC-011: Execution time ≤120s | Timed test execution | 2, 3 | Semi |
| SC-012: Pipeline overhead ≤5% | Baseline comparison | 4 | Semi |
| SC-013: Reports 100% parseable | Unit test with varied formats | 1 | Yes |
| SC-014: --no-validate doesn't skip fidelity | Integration test | 2 | Yes |

### Test Coverage Targets
- **Unit tests**: 22 (covering all semantic checks, dataclasses, prompt builders, gate logic)
- **Integration tests**: 8 (covering pipeline step behavior, CLI subcommand, state persistence)
- **E2E tests**: 4 (covering full pipeline runs, tasklist validation against real artifacts)
- **Regression**: 100% existing test pass rate maintained at every phase boundary

---

## 7. Timeline Summary

| Phase | Duration | Key Deliverable | Dependencies |
|-------|----------|----------------|--------------|
| Pre-impl decisions | 1 day | OQ-001, OQ-004, OQ-006, OQ-007 resolved | Stakeholder input |
| Phase 1: Foundation | 4 days | Gate fixes, deviation format, semantic checks | None |
| Phase 2: Spec-Fidelity | 6 days | Pipeline fidelity gate, state persistence | Phase 1 |
| Phase 3: Tasklist CLI | 6 days | CLI subcommand, tasklist fidelity gate | Phase 1 (format reuse) |
| Phase 4: Retrospective & Hardening | 5 days | Retrospective wiring, integration tests, docs | Phase 2, Phase 3 |

**Total**: ~22 working days (single developer). Phases 2 and 3 can partially overlap since they share the foundation from Phase 1 but operate on different modules (roadmap vs. tasklist). With parallelization, total could compress to ~17 days.

**Critical path**: Pre-impl decisions → Phase 1 → Phase 2 → Phase 4. Phase 3 branches from Phase 1 independently.
