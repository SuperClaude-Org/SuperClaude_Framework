---
spec_source: "spec-roadmap-validate.md"
complexity_score: 0.65
adversarial: true
---

# Roadmap: Roadmap Validation Pipeline (v2.19) — Final Merged

## Executive Summary

This roadmap implements a validation subsystem for the SuperClaude roadmap pipeline, adding a `superclaude roadmap validate <output-dir>` subcommand that validates pipeline outputs across 7 dimensions, supports single-agent and multi-agent (adversarial) modes, and auto-invokes after successful pipeline runs.

**Scope**: 3 new files (`validate_gates.py`, `validate_prompts.py`, `validate_executor.py`), 3 modified files (`models.py`, `commands.py`, `executor.py`) across 4 domains (CLI, subprocess orchestration, prompt engineering, structured validation). The design is purely additive with no breaking changes, reusing existing pipeline infrastructure (`execute_pipeline`, `ClaudeProcess`, gate system).

**Key Architectural Decisions**:
- Validation runs as an isolated subprocess to prevent confirmation bias from the generation context.
- `validate_*` modules depend on `pipeline/*` and `gates.py` but never vice versa (unidirectional dependency).
- All 4 open questions are resolved upfront (see Section 6) to prevent late-stage instability.
- Degraded validation reports from partial agent failures are explicitly marked with `validation_complete: false` frontmatter and a warning banner.

**Merge Provenance**: Base is Variant A (Opus-Architect, score 76/100). Incorporates 6 specific improvements from Variant B (Haiku-Analyzer, score 72/100) as identified through 3-round adversarial debate (convergence: 0.78).

## Phased Implementation Plan

### Phase 1: Data Models & Gate Infrastructure
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur.

- Lorem ipsum bullet point one
- Consectetur adipiscing elit item two
- Sed do eiusmod tempor incididunt three
### Phase 2: Prompt Engineering

**Milestone**: Reflection and merge prompts produce structurally valid reports.

**Parallel execution**: Phase 2 can run concurrently with Phase 1, with a **30-minute alignment checkpoint** before Phase 3 to verify field-name consistency between gate definitions and prompt templates (mitigates `blocking_count` vs `blocking_issues_count` class of errors).

**Deliverables**:
1. Create `validate_prompts.py` with:
   - `build_reflect_prompt(roadmap, test_strategy, extraction)` — single-agent reflection prompt covering all 7 validation dimensions
   - `build_merge_prompt(reflect_reports: list)` — adversarial merge prompt with BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categorization instructions
2. Embed validation dimension definitions with severity classifications:
   - **BLOCKING**: Schema, Structure, Traceability, Cross-file consistency, Parseability
   - **WARNING**: Interleave ratio, Decomposition
3. Embed concrete interleave ratio formula: `interleave_ratio = unique_phases_with_deliverables / total_phases` (marked as "initial, subject to refinement" — see Open Questions)
4. Include false-positive reduction constraint in prompt text

**Validation**: Manual smoke test with sample inputs; gate criteria from Phase 1 applied to outputs.

**Estimated effort**: 2-3 hours

### Phase 3: Validation Executor

**Milestone**: End-to-end validation works standalone in both single-agent and multi-agent modes.

**Deliverables**:
1. Create `validate_executor.py` with `execute_validate(config: ValidateConfig)`:
   - Read 3 input files from `output_dir` (`roadmap.md`, `test-strategy.md`, `extraction.md`)
   - Validate file presence before proceeding
   - Route by agent count (conditional, not separate infrastructure):
     - 1 agent → sequential reflection → gate check → write `validate/validation-report.md`
     - N agents → N parallel reflections → gate each → sequential adversarial merge → STRICT gate → write merged report
2. Reuse `execute_pipeline` and `ClaudeProcess` for subprocess management
3. Create `validate/` subdirectory for all outputs
4. Return structured result with blocking/warning/info counts
5. **Partial failure handling**: If agent A succeeds and agent B fails after retry, write agent A's reflection file and produce a degraded validation report with `validation_complete: false` in frontmatter and a prominent warning banner noting the incomplete analysis

**Dependencies**: Phase 1 (gate criteria), Phase 2 (prompts), existing `execute_pipeline` and `ClaudeProcess`

**Validation**: Integration test against known-good and known-bad pipeline outputs.

**Estimated effort**: 3-4 hours

### Phase 4: CLI Integration & State Persistence

**Milestone**: Full CLI surface area complete with auto-invocation and resume awareness.

**Deliverables**:
1. Modify `commands.py`:
   - Add `validate` subcommand under `roadmap` group with `--agents`, `--model`, `--max-turns`, `--debug` options
   - Add `--no-validate` flag to `roadmap run`
2. Modify `executor.py`:
   - Call `execute_validate()` from `execute_roadmap()` after 8-step pipeline success
   - Inherit `--agents`, `--model`, `--max-turns`, `--debug` from parent invocation
   - Skip validation when `--no-validate` is set
   - Skip validation when `--resume` pipeline halts on a failed step (only run on complete success)
3. Record validation completion status (`pass`/`fail`/`skipped`) in `.roadmap-state.json` under a `validation` key — enables `--resume` to skip re-validation of already-validated artifacts
4. CLI output: surface blocking issues as warnings, always exit 0 (NFR-006)

**Dependencies**: Phase 3 (executor)

**Validation**: Integration tests for all CLI paths.

**Estimated effort**: 1-2 hours

### Phase 5: Verification, Testing & Documentation

**Milestone**: All success criteria met, all tests pass, operational documentation delivered.

**Deliverables**:

#### Unit Tests
- Gate validation: missing frontmatter fields, empty semantic values, line count thresholds, agreement table enforcement
- Config parsing: agent parsing, default handling
- Report semantics: `tasklist_ready == (blocking_issues_count == 0)`

#### Integration Tests
1. Standalone single-agent validation (SC-001)
2. Standalone multi-agent validation (SC-003)
3. `roadmap run` auto-invokes validation (SC-004)
4. `roadmap run --no-validate` skips validation (SC-005)
5. `--resume` success path runs validation
6. `--resume` failed-step path skips validation

#### Known-Defect Detection Tests
- Duplicate D-ID detection
- Missing milestone reference detection
- Untraced requirement detection
- Cross-file inconsistency detection

#### Architecture & Performance Verification
- Verify unidirectional dependency: `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty (SC-009)
- Performance: single-agent ≤2 min (NFR-001, SC-002)
- Verify infrastructure reuse (no new subprocess abstractions)

#### Operational Documentation
- Standalone `validate` usage and options
- Multi-agent trade-offs (cost vs rigor)
- `--no-validate` and `--resume` interaction semantics
- Default agent count asymmetry rationale (standalone: single-agent for cost efficiency; `roadmap run`: dual-agent for rigor)

**Estimated effort**: 2-3 hours

## Risk Assessment

### High Priority

| ID | Risk | Likelihood | Mitigation |
|----|------|------------|------------|
| R-004 | Adversarial merge produces inconsistent or misleading findings | Medium | Stricter gate on merged report than reflections; explicit agreement table required; severity escalation on disagreements; integration tests with intentionally conflicting inputs |
| R-005 | `--resume` validates incomplete artifacts | Medium | Gate validation invocation on final pipeline success only; explicit tests for resumed-success and resumed-failure branches; validation state tracked in `.roadmap-state.json` |
| R-ARCH | Architectural drift violates unidirectional dependency rule | Medium | Implement files in specified order; CI grep-based architecture test (`grep -r "from.*validate" pipeline/`); restrict validate modules to importing shared primitives only |

### Medium Priority

| ID | Risk | Likelihood | Mitigation |
|----|------|------------|------------|
| R-001 | False positive BLOCKING findings waste user time | Medium | Prompt constraint "false positives waste user time"; adversarial merge deduplication; prefer evidence-linked findings with concrete location and fix guidance; tune prompts iteratively post-launch |
| R-002 | Multi-agent token cost exceeds budget | Low-Medium | Single-agent default for standalone; NFR-001 ≤2 min target as proxy for cost; measure and report overhead |

### Low Priority

| ID | Risk | Likelihood | Mitigation |
|----|------|------------|------------|
| R-003 | Gate min 20 lines too lenient (shallow reports pass) | Medium | Semantic checks for non-empty frontmatter provide content-level validation beyond line count; add negative tests for minimal-but-useless reports |
| R-006 | Shared helper coupling (`_frontmatter_values_non_empty`) becomes brittle | Low | Pure function with no side effects; acceptable per unidirectional constraint; document acceptable coupling boundary |

## Resource Requirements

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
| `src/superclaude/cli/roadmap/executor.py` | Modify (auto-invocation + state) | 4 |

### Infrastructure Constraints
1. No new orchestration framework or subprocess abstraction
2. No reverse imports into `pipeline/*`
3. Validation runs as isolated Claude subprocess
4. Outputs reside under `<output-dir>/validate/`

## Success Criteria & Validation Approach

| Criterion | Validation Method | Phase |
|-----------|-------------------|-------|
| SC-001: Standalone validate produces valid report | Integration test: run against sample dir, parse frontmatter | 3 |
| SC-002: Single-agent ≤2 min | Timed integration test | 5 |
| SC-003: Multi-agent produces per-agent + merged reports | Integration test: verify file count and agreement table | 3 |
| SC-004: Auto-invocation after pipeline success | Integration test: run `roadmap run`, check `validate/` exists | 4 |
| SC-005: `--no-validate` skips validation | Integration test: run with flag, check `validate/` absent | 4 |
| SC-006: Known issues detected as BLOCKING | Integration test with known-bad inputs (duplicate D-IDs, missing milestones, untraced requirements) | 5 |
| SC-007: Exit code 0 even with blocking issues | Integration test: assert exit code | 4 |
| SC-008: All tests pass (unit + integration) | `uv run pytest` | 5 |
| SC-009: No reverse imports | `grep -r "from.*validate" src/superclaude/cli/roadmap/pipeline/` returns empty | 5 |

## Timeline Estimates

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| 1 | Data Models & Gate Infrastructure | 1-2 hours | None |
| 2 | Prompt Engineering | 2-3 hours | None (parallel with Phase 1) |
| — | Alignment checkpoint (gates ↔ prompts) | 30 min | Phases 1, 2 |
| 3 | Validation Executor | 3-4 hours | Phases 1, 2 |
| 4 | CLI Integration & State Persistence | 1-2 hours | Phase 3 |
| 5 | Verification, Testing & Documentation | 2-3 hours | Phase 4 |
| **Total** | | **8-12 hours** (wall time, accounting for Phase 1‖2 parallelism) | |

### Dependency Graph

```
Phase 1 ──────┐
              ├── [alignment checkpoint] ── Phase 3 ── Phase 4 ── Phase 5
Phase 2 ──────┘
```

### Schedule Risks
1. **Merge semantics ambiguity** — could extend Phase 3 if agreement categorization needs prompt iteration
2. **Resume edge-case discovery** — could extend Phase 4 if current pipeline state handling is less explicit than assumed
3. **Prompt iteration cycles** — Phase 2 estimate assumes 1-2 iteration rounds; poor initial prompt quality may extend this

## Open Questions — Resolved Recommendations

### OQ-1: Default Agent Count Asymmetry
**Decision**: Keep the asymmetry as specified. Standalone validation is a diagnostic tool where cost efficiency matters; `roadmap run` benefits from dual-agent rigor as part of the full pipeline. Document the rationale in CLI help text and operational documentation.

### OQ-2: Retry Failure Semantics
**Decision**: Surface partial results with explicit degradation marking. If agent A succeeds and agent B fails after retry, write agent A's reflection file and produce a degraded validation report with:
- `validation_complete: false` in YAML frontmatter
- Prominent warning banner noting the incomplete analysis and which agent(s) failed
- Silent degradation is unacceptable — the report must be unmistakably marked as incomplete.

### OQ-3: Interleave Ratio Formula
**Decision**: Define before Phase 2 prompt work. Initial formula: `interleave_ratio = unique_phases_with_deliverables / total_phases`. Embed in the reflection prompt to ensure consistency across agents. Mark as "initial, subject to refinement during hardening" — but all agents must use the same formula for merge categorization to be meaningful.

### OQ-4: State Persistence
**Decision**: Record validation completion status (`pass`/`fail`/`skipped`) in `.roadmap-state.json` under a `validation` key. This enables `--resume` to skip re-validation of already-validated artifacts and handles edge cases that artifact-on-disk checks cannot (e.g., validation completed with warnings, user resumes — system knows validation already ran). Implement in Phase 4.
