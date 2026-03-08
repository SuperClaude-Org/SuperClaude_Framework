

---
spec_source: "spec-roadmap-validate.md"
complexity_score: 0.65
primary_persona: architect
---

# Roadmap: Roadmap Validation Pipeline (v2.19)

## 1. Executive Summary

This roadmap covers the implementation of a validation subsystem for the SuperClaude roadmap pipeline. The feature adds a `superclaude roadmap validate` subcommand that validates roadmap pipeline outputs across 7 dimensions, supports single-agent and multi-agent (adversarial) modes, and auto-invokes after successful pipeline runs.

**Scope**: 3 new files, 3 modified files across 4 domains (CLI, subprocess orchestration, prompt engineering, structured validation). The design is purely additive with no breaking changes, reusing existing pipeline infrastructure (`execute_pipeline`, `ClaudeProcess`, gate system).

**Key Architectural Decision**: Validation runs as an isolated subprocess to prevent confirmation bias from the generation context. The `validate_*` module tree depends on `pipeline/*` and `gates.py` but never vice versa (unidirectional dependency).

## 2. Phased Implementation Plan

### Phase 1: Data Models & Gate Infrastructure
**Milestone**: ValidateConfig and gate criteria defined and unit-testable

**Deliverables**:
1. Extend `models.py` with `ValidateConfig` dataclass (fields: `output_dir`, `agents`, `model`, `max_turns`, `debug`)
2. Create `validate_gates.py` with:
   - `REFLECT_GATE`: STANDARD enforcement, min 20 lines, required frontmatter (`blocking_issues_count`, `warnings_count`, `tasklist_ready`), semantic check for non-empty values
   - `ADVERSARIAL_MERGE_GATE`: STRICT enforcement, min 30 lines, extended frontmatter (`validation_mode`, `validation_agents`), agreement table semantic check
3. Import `_frontmatter_values_non_empty`, `GateCriteria`, `SemanticCheck` from `roadmap/gates.py`

**Validation**: Unit tests for gate criteria construction, frontmatter parsing, semantic checks

**Estimated effort**: Small — well-bounded data definitions with clear spec

### Phase 2: Prompt Engineering
**Milestone**: Reflection and merge prompts produce structurally valid reports

**Deliverables** (can run in parallel with Phase 1 gate work):
1. Create `validate_prompts.py` with:
   - `build_reflect_prompt(roadmap, test_strategy, extraction)` — single-agent reflection prompt covering all 7 validation dimensions
   - `build_merge_prompt(reflect_reports: list)` — adversarial merge prompt with BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categorization instructions
2. Embed validation dimension definitions: Schema (BLOCKING), Structure (BLOCKING), Traceability (BLOCKING), Cross-file consistency (BLOCKING), Interleave ratio (WARNING), Decomposition (WARNING), Parseability (BLOCKING)
3. Include false-positive reduction constraint in prompt text

**Validation**: Manual smoke test with sample inputs; gate criteria from Phase 1 applied to outputs

**Estimated effort**: Medium — prompt quality is critical for validation accuracy (R-001)

### Phase 3: Validation Executor
**Milestone**: End-to-end validation works standalone

**Deliverables**:
1. Create `validate_executor.py` with `execute_validate(config: ValidateConfig)`:
   - Read 3 input files from `output_dir` (roadmap.md, test-strategy.md, extraction.md)
   - Validate file presence before proceeding
   - Single-agent path: 1 reflection step → gate check → write `validate/validation-report.md`
   - Multi-agent path: N parallel reflection steps → gate each → sequential adversarial merge → STRICT gate → write merged report
2. Reuse `execute_pipeline` and `ClaudeProcess` for subprocess management
3. Create `validate/` subdirectory for all outputs
4. Return structured result with blocking/warning/info counts

**Dependencies**: Phase 1 (gate criteria), Phase 2 (prompts), existing `execute_pipeline` and `ClaudeProcess`

**Validation**: Integration test — run against known-good and known-bad pipeline outputs

**Estimated effort**: Medium — core logic is moderate but multi-agent parallelism needs care (R-004)

### Phase 4: CLI Integration
**Milestone**: Full CLI surface area complete with auto-invocation

**Deliverables**:
1. Modify `commands.py`:
   - Add `validate` subcommand under `roadmap` group with `--agents`, `--model`, `--max-turns`, `--debug` options
   - Add `--no-validate` flag to `roadmap run`
2. Modify `executor.py`:
   - Call `execute_validate()` from `execute_roadmap()` after 8-step pipeline success
   - Inherit `--agents`, `--model`, `--max-turns`, `--debug` from parent invocation
   - Skip validation when `--no-validate` is set
   - Skip validation when `--resume` pipeline halts on a failed step (only run on complete success)
3. CLI output: surface blocking issues as warnings, always exit 0 (NFR-006)

**Dependencies**: Phase 3 (executor)

**Validation**: Integration tests for all CLI paths (standalone, auto-invoke, `--no-validate`, `--resume`)

**Estimated effort**: Small — mostly wiring existing pieces together

### Phase 5: Verification & Hardening
**Milestone**: All success criteria met, all tests pass

**Deliverables**:
1. Run all 7 unit tests from spec section 10
2. Run all 4 integration tests from spec section 10
3. Verify SC-001 through SC-009 systematically
4. Verify unidirectional dependency constraint (SC-009): `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty
5. Performance verification: single-agent ≤2 min (NFR-001, SC-002)
6. Address any edge cases from open questions (see Section 3)

**Estimated effort**: Small — verification of completed work

## 3. Risk Assessment & Mitigation

| ID | Risk | Severity | Probability | Mitigation |
|----|------|----------|-------------|------------|
| R-001 | False positive BLOCKING findings waste user time | Medium | Medium | Prompt constraint "false positives waste user time"; adversarial merge deduplication; tune prompt iteratively post-launch |
| R-002 | Multi-agent token cost exceeds budget | Medium | Low | Single-agent default for standalone; NFR-001 ≤2 min target as proxy for cost; monitor in practice |
| R-003 | Gate min 20 lines too lenient | Low | Low | Semantic checks for non-empty frontmatter provide content-level validation beyond line count |
| R-004 | Adversarial merge incorrectly categorizes findings | Medium | Medium | Explicit BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categories in prompt; STRICT gate on merged output; manual review of early outputs |
| R-005 | `--resume` with partial artifacts produces misleading validation | Low | Low | Validation only runs after all pipeline gates pass per spec |
| R-006 | Import coupling via `_frontmatter_values_non_empty` | Low | Low | Pure function, no side effects; acceptable per unidirectional constraint |

**Architectural risk note**: The interleave ratio calculation (Open Question 3) is undefined in the spec and left to prompt interpretation. This should be resolved before Phase 2 prompt work begins — recommend defining a concrete formula (e.g., count of phase transitions / total deliverables) and embedding it in the prompt.

## 4. Resource Requirements & Dependencies

### External Dependencies
- `click` — already in project dependencies, no changes needed
- `ClaudeProcess`, `AgentSpec` — existing infrastructure, no modifications
- `execute_pipeline` — reused as-is
- `GateCriteria`, `SemanticCheck`, `_frontmatter_values_non_empty` — imported from `gates.py`

### Files Modified
| File | Change Type | Phase |
|------|-------------|-------|
| `src/superclaude/cli/roadmap/models.py` | Extend (add `ValidateConfig`) | 1 |
| `src/superclaude/cli/roadmap/validate_gates.py` | **New** | 1 |
| `src/superclaude/cli/roadmap/validate_prompts.py` | **New** | 2 |
| `src/superclaude/cli/roadmap/validate_executor.py` | **New** | 3 |
| `src/superclaude/cli/roadmap/commands.py` | Modify (add subcommand + flag) | 4 |
| `src/superclaude/cli/roadmap/executor.py` | Modify (auto-invocation) | 4 |

### Parallelization Opportunities
- Phase 1 gate work and Phase 2 prompt work can proceed in parallel (no dependency between them)
- Phase 3 depends on both Phase 1 and Phase 2
- Phase 4 depends on Phase 3
- Phase 5 depends on Phase 4

## 5. Success Criteria & Validation Approach

| Criterion | Validation Method | Phase |
|-----------|-------------------|-------|
| SC-001: Standalone validate produces valid report | Integration test: run against sample dir, parse frontmatter | 3 |
| SC-002: Single-agent ≤2 min | Timed integration test | 5 |
| SC-003: Multi-agent produces per-agent + merged reports | Integration test: verify file count and agreement table | 3 |
| SC-004: Auto-invocation after pipeline success | Integration test: run `roadmap run`, check `validate/` exists | 4 |
| SC-005: `--no-validate` skips validation | Integration test: run with flag, check `validate/` absent | 4 |
| SC-006: Known issues detected as BLOCKING | Integration test with known-bad inputs | 3 |
| SC-007: Exit code 0 even with blocking issues | Integration test: assert exit code | 4 |
| SC-008: All 11 tests pass (7 unit + 4 integration) | `uv run pytest` | 5 |
| SC-009: No reverse imports | `grep -r` verification | 5 |

## 6. Timeline Estimates

| Phase | Description | Estimated Duration | Dependencies |
|-------|-------------|--------------------|--------------|
| 1 | Data Models & Gate Infrastructure | 1-2 hours | None |
| 2 | Prompt Engineering | 2-3 hours | None (parallel with Phase 1) |
| 3 | Validation Executor | 3-4 hours | Phases 1, 2 |
| 4 | CLI Integration | 1-2 hours | Phase 3 |
| 5 | Verification & Hardening | 1-2 hours | Phase 4 |
| **Total** | | **6-9 hours** (wall time, accounting for Phase 1‖2 parallelism) | |

## 7. Open Questions — Architect Recommendations

1. **Default agent asymmetry**: Keep the asymmetry as specified. Standalone validation is a diagnostic tool where cost efficiency matters; `roadmap run` benefits from dual-agent rigor as part of the full pipeline. Document the rationale in the CLI help text.

2. **Retry failure semantics**: Surface partial results. If agent A succeeds and agent B fails after retry, write agent A's reflection file and produce a degraded validation report noting the incomplete analysis. This is more useful than failing entirely.

3. **Interleave ratio formula**: Define before Phase 2. Recommended: `interleave_ratio = unique_phases_with_deliverables / total_phases`. Embed the formula in the reflection prompt to ensure consistency across agents.

4. **State persistence**: Record validation completion status (pass/fail/skipped) in `.roadmap-state.json` under a `validation` key. This enables `--resume` to skip re-validation of already-validated artifacts. Implement in Phase 4 alongside executor integration.
