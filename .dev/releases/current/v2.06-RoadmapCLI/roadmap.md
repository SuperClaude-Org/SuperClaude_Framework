---
spec_source: ".dev/releases/current/v2.06-RoadmapCLI/merged-spec.md"
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
complexity_score: 0.522
complexity_class: MEDIUM
domain_distribution:
  backend: 95
  documentation: 5
primary_persona: architect
consulting_personas: [backend]
milestone_count: 5
milestone_index:
  - id: M1
    title: "Foundation: Pipeline Module"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 7
    risk_level: Low
  - id: M2
    title: "Sprint Migration to Pipeline"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 4
    risk_level: Medium
  - id: M3
    title: "Roadmap Command Implementation"
    type: FEATURE
    priority: P1
    dependencies: [M1]
    deliverable_count: 10
    risk_level: Medium
  - id: M4
    title: "CLI Interface & UX"
    type: FEATURE
    priority: P1
    dependencies: [M3]
    deliverable_count: 7
    risk_level: Low
  - id: M5
    title: "Validation & Acceptance Testing"
    type: TEST
    priority: P1
    dependencies: [M2, M4]
    deliverable_count: 5
    risk_level: Low
total_deliverables: 33
total_risks: 6
estimated_phases: 7
validation_score: 0.9473
validation_status: PASS
---

# Roadmap: `superclaude roadmap` CLI Command

## Overview

This roadmap covers implementation of the `superclaude roadmap` CLI command — an external conductor that calls Claude as a subprocess per pipeline step with deterministic file-on-disk gates between steps. The architecture eliminates fabrication risk by preventing Claude from advancing to step N+1 without producing gate-passing output files.

The implementation follows a bottom-up approach: extract a shared `pipeline/` module from the existing `sprint/` code, migrate sprint to use it (validating zero regression), then build the `roadmap/` command on top of the proven pipeline base. This ordering minimizes risk by establishing the shared foundation before either consumer depends on it.

Key architectural decision: composition via callable `StepRunner` injection rather than inheritance or template method, because sprint's tightly-coupled orchestration (TUI, tmux, stall detection) cannot be meaningfully abstracted into hooks without creating a leaky abstraction.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation: Pipeline Module | FEATURE | P0 | M | None | 7 | Low |
| M2 | Sprint Migration to Pipeline | FEATURE | P0 | S | M1 | 4 | Medium |
| M3 | Roadmap Command Implementation | FEATURE | P1 | XL | M1 | 10 | Medium |
| M4 | CLI Interface & UX | FEATURE | P1 | M | M3 | 7 | Low |
| M5 | Validation & Acceptance Testing | TEST | P1 | S | M2, M4 | 5 | Low |

## Dependency Graph

```
M1 → M2 → M5
M1 → M3 → M4 → M5
```

M1 (Foundation) is the sole prerequisite for both M2 (Sprint Migration) and M3 (Roadmap Implementation). M2 and M3 can proceed in parallel after M1 completes. M5 (Validation) requires both M2 and M4 to be complete, ensuring sprint regression is verified alongside roadmap functionality.

---

## M1: Foundation: Pipeline Module

### Objective

Extract a shared `pipeline/` module from `sprint/` containing the generic step sequencing, gate validation, parallel dispatch, and data models that both sprint and roadmap consume. Establish one-directional dependency: `pipeline/` has no imports from `sprint/` or `roadmap/` (NFR-007).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | `pipeline/models.py` — `PipelineConfig`, `Step`, `StepResult`, `StepStatus`, `GateCriteria`, `SemanticCheck` dataclasses | All fields match spec §3.2; no sprint-specific fields (NFR-006); `Step.gate` is `Optional[GateCriteria]`; `Step.model` field for per-step override |
| D1.2 | `pipeline/gates.py` — `gate_passed()` function | Returns `(bool, str\|None)`; implements 4-tier enforcement (EXEMPT/LIGHT/STANDARD/STRICT); pure Python, no subprocess (NFR-003); failure messages match spec §3.2 format |
| D1.3 | `pipeline/executor.py` — `execute_pipeline()` generic executor | Accepts `StepRunner` protocol, `on_step_start`, `on_step_complete`, `on_state_update`, `cancel_check` callbacks; handles sequential and parallel step groups; implements retry logic per step retry_limit |
| D1.4 | `pipeline/process.py` — `ClaudeProcess` moved from sprint | Identical class, new location; sprint re-exports from this module |
| D1.5 | `pipeline/_run_parallel_steps()` — parallel step execution | `threading.Thread` + shared `threading.Event` for cross-cancellation; each thread enforces its own timeout; `cancel_event.set()` on failure triggers sibling termination |
| D1.6 | `pipeline/__init__.py` — public API exports | Exports: PipelineConfig, Step, StepResult, StepStatus, GateCriteria, SemanticCheck, execute_pipeline, gate_passed, ClaudeProcess |
| D1.7 | `tests/pipeline/` — unit test suite | test_models.py, test_gates.py, test_executor.py, test_process.py, test_parallel.py; all pass with `uv run pytest tests/pipeline/` |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API design too coupled to sprint patterns | Low | Medium | Follow spec's composition-via-callable design; validate pipeline/ has zero sprint imports |
| Gate validation edge cases (empty files, malformed YAML) | Low | Low | Comprehensive test fixtures covering all gate tiers and failure modes |

---

## M2: Sprint Migration to Pipeline

### Objective

Migrate `sprint/` to consume the `pipeline/` module for `ClaudeProcess`, `PipelineConfig`, and related types. Sprint's external CLI API must remain identical (NFR-001). All 14 existing sprint test files must pass without modification (NFR-002).

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | `sprint/config.py` — `SprintConfig` inherits from `PipelineConfig` | `release_dir` property aliases `work_dir`; existing code using `config.release_dir` works unchanged; sprint-specific fields (index_path, phases, stall_timeout, etc.) remain in SprintConfig only |
| D2.2 | `sprint/models.py` — types inherit from pipeline models | `SprintStep` extends `Step`; `PhaseResult` extends `StepResult`; import paths resolve correctly |
| D2.3 | `sprint/process.py` — re-exports `ClaudeProcess` from `pipeline.process` | `from superclaude.cli.sprint.process import ClaudeProcess` continues to work (canary for import stability) |
| D2.4 | Sprint regression validation | `uv run pytest tests/sprint/` exits 0 with all 14 test files passing; no test file modifications |

### Dependencies

- M1: Pipeline module must be complete and tested

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-001: Sprint regression during extraction | Medium | High | Run full sprint test suite after each migration step; commit after each passing test run; `release_dir` property alias preserves backward compatibility |
| Import chain breakage | Low | Medium | Sprint's `process.py` re-export pattern ensures old import paths resolve; test canary detects breaks immediately |

---

## M3: Roadmap Command Implementation

### Objective

Build the `superclaude roadmap` command on the `pipeline/` foundation. Implement the 8-step pipeline with context isolation, parallel generate steps, gate enforcement, and retry-then-halt failure policy.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | `roadmap/commands.py` — Click CLI entry point | `superclaude roadmap <spec-file>` registered in main.py (FR-009); accepts --agents, --output, --depth, --resume, --dry-run, --model, --max-turns, --debug flags |
| D3.2 | `roadmap/models.py` — `RoadmapConfig` extends `PipelineConfig`; `AgentSpec` dataclass | `AgentSpec.parse()` handles `model:persona` format; default agents: `opus:architect,haiku:architect`; `RoadmapConfig` adds spec_file, agents, depth, output_dir |
| D3.3 | `roadmap/prompts.py` — 7 prompt builder pure functions | extract, generate, diff, debate, score, merge, test-strategy prompts; all return str; no I/O (NFR-004); debate prompt embeds depth-dependent round instructions |
| D3.4 | `roadmap/gates.py` — gate criteria definitions as data | 7 GateCriteria instances matching spec §4 step definitions; correct enforcement tiers (STRICT for generate/debate/merge, STANDARD for others); frontmatter fields and min_lines per step |
| D3.5 | `roadmap/executor.py` — `execute_roadmap()` wrapping `execute_pipeline()` | Builds step list with parallel generate group; `roadmap_run_step` builds subprocess argv per spec §13.3; `--file` injection for inputs; per-step model override for generate steps |
| D3.6 | Parallel generate implementation | Steps generate-A and generate-B as `list[Step]` passed to `execute_pipeline()`; cross-cancellation on failure; CANCELLED status for sibling when one fails |
| D3.7 | Context isolation enforcement | Each step's subprocess argv contains only `step.prompt` + `--file <input>` for each input; no `--continue`, no session ID, no shared memory between steps (FR-003, FR-023) |
| D3.8 | Gate enforcement integration | `gate_passed()` called after each subprocess; tier-proportional validation; human-readable failure messages; retry on gate failure per step retry_limit |
| D3.9 | Failure policy: retry-then-halt | On gate failure: retry once (same prompt, fresh subprocess); on second failure: HALT with diagnostic output per spec §6.2 format |
| D3.10 | Semantic checks for STRICT-tier steps | merge: no_heading_gaps, cross_refs_resolve, no_duplicate_headings; generate: frontmatter_values_non_empty, has_actionable_content; debate: convergence_score_valid |

### Dependencies

- M1: Pipeline module must be complete (executor, gates, models, parallel dispatch)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-002: Claude subprocess produces non-conforming output | High | Medium | Retry-once policy provides automatic recovery; gate criteria calibrated via testing with real Claude output |
| RISK-003: Parallel subprocess race conditions | Low | High | Cross-cancellation uses `threading.Event` (thread-safe boolean); each thread has independent timeout via `time.monotonic()`; explicit join before result aggregation |
| RISK-004: Gate calibration too strict/lenient | Medium | Medium | STRICT tier semantic checks target structural issues (heading gaps, cross-refs) not content quality; min_lines set conservatively based on expected output sizes |

---

## M4: CLI Interface & UX

### Objective

Implement the user-facing CLI features: `--resume` with stale spec detection, `--dry-run` preview, progress display, state file management, HALT output formatting, and depth-to-prompt mapping.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | `--resume` implementation | Reads `.roadmap-state.json`; compares spec SHA-256 hash; skips steps whose gates pass; forces extract re-run on hash mismatch with user warning; runs from first failing step onward (FR-006, FR-029) |
| D4.2 | `--dry-run` implementation | Prints 7 step entries (ID, output file, gate criteria, timeout) to stdout; exits 0; no subprocess invocations; no file writes (FR-007) |
| D4.3 | Progress display | Stdout output during step execution updated every 5 seconds; parallel step display shows both steps; completion line with PASS/FAIL, attempt count, elapsed time (FR-013) |
| D4.4 | `.roadmap-state.json` management | Written atomically (tmp + `os.replace`); updated after each step; schema_version, spec_hash, agents, depth, per-step status with timestamps (FR-012, FR-028) |
| D4.5 | HALT output formatting | stderr output per spec §6.2: step name, gate failure reason, file details, completed/failed/skipped summary, retry command (FR-033) |
| D4.6 | Depth-to-prompt mapping | quick=1 round, standard=2 rounds, deep=3 rounds; embedded in `build_debate_prompt()` via `_DEPTH_INSTRUCTIONS` dict (FR-032) |
| D4.7 | `--agents` parsing and model routing | Parse comma-separated `model:persona` specs; pass model directly to `claude -p --model`; no resolution needed (FR-015, FR-024) |

### Dependencies

- M3: Roadmap command must be functional before CLI UX features can be integrated

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| RISK-005: State file corruption during atomic write | Low | Medium | Use tmp file + `os.replace()` (atomic on POSIX); add recovery logic to read stale state gracefully |
| RISK-006: Timeout values insufficient for complex specs | Medium | Low | Timeouts are configurable via `--max-turns`; generate step has generous 900s (15 min); log elapsed time for observability |

---

## M5: Validation & Acceptance Testing

### Objective

Implement comprehensive test suites for pipeline, roadmap, and sprint regression. Validate all 7 acceptance criteria (AC-01 through AC-07) and all non-functional requirements.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | `tests/pipeline/` test suite | test_models.py, test_gates.py, test_executor.py, test_process.py, test_parallel.py; covers gate tier enforcement, retry logic, parallel dispatch, cross-cancellation |
| D5.2 | `tests/roadmap/` test suite | test_models.py, test_prompts.py, test_gates_data.py, test_executor.py, test_cli_contract.py, test_resume.py, test_parallel.py, test_state.py, test_dry_run.py |
| D5.3 | Sprint regression verification | `uv run pytest tests/sprint/` exits 0; all 14 existing test files pass without modification (AC-06) |
| D5.4 | Acceptance criteria validation | AC-01 (--dry-run), AC-03 (gate failure halt), AC-04 (--resume skip), AC-05 (stale spec), AC-07 (--agents routing) verified via CliRunner tests |
| D5.5 | NFR compliance verification | NFR-003 (gate_passed pure Python), NFR-004 (prompts pure functions), NFR-005 (gate data separation), NFR-006 (no sprint fields in pipeline), NFR-007 (no sprint/roadmap imports in pipeline) |

### Dependencies

- M2: Sprint migration must be complete for regression testing
- M4: CLI features must be complete for acceptance testing

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Mock strategy insufficient for subprocess testing | Low | Medium | Use `unittest.mock.patch("subprocess.Popen")` with configurable exit codes and pre-written output files; CliRunner for CLI surface testing |
| AC-02 (full E2E) requires claude binary | Medium | Low | AC-02 explicitly noted as manual validation in v1; not in automated test scope |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Sprint regression during pipeline/ extraction | M2, M5 | Medium | High | Run full sprint test suite after each migration step; commit after each passing run; `release_dir` property alias preserves backward compatibility | architect |
| R-002 | Claude subprocess produces non-conforming output requiring retries | M3, M4 | High | Medium | Retry-once policy with clear gate failure diagnostics; gate criteria calibrated via testing | backend |
| R-003 | Parallel subprocess cross-cancellation race conditions | M3 | Low | High | `threading.Event` (thread-safe); independent per-thread timeouts; explicit `join()` before result aggregation | backend |
| R-004 | Gate validation too strict/lenient | M3, M5 | Medium | Medium | Semantic checks target structural issues not content quality; min_lines set conservatively; tier-proportional enforcement prevents over-validation | architect |
| R-005 | State file corruption during atomic write | M4 | Low | Medium | tmp + `os.replace()` (POSIX atomic); graceful recovery on read | backend |
| R-006 | Timeout values insufficient for complex specs | M4 | Medium | Low | Generate step: 900s (generous); `--max-turns` configurable; elapsed time logged for observability | backend |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect | backend (confidence: 0.665) | Generalist covers the cross-cutting nature of pipeline extraction + CLI architecture; backend domain at 95% but the task is fundamentally architectural (module extraction, composition patterns) |
| Template | inline (Tier 4 fallback) | No Tier 1-3 templates found | No `.dev/templates/roadmap/` or `~/.claude/templates/roadmap/` directories exist |
| Milestone Count | 5 | Range 5-7 (MEDIUM class) | base=5 + floor(1 domain / 2) = 5; single-domain project doesn't warrant extra milestones |
| Adversarial Mode | none | N/A | Single-spec mode, no --multi-roadmap or --specs flags |
| Concurrency Model | threading.Thread + Event | asyncio, ThreadPoolExecutor | Spec §13.2: ClaudeProcess uses blocking subprocess.Popen.wait(); threads natural for I/O-bound blocking; asyncio requires invasive rewrite; ThreadPoolExecutor adds abstraction without benefit for exactly 2 threads |
| Extension Pattern | Composition via StepRunner | Inheritance, Template Method | Spec §13.5: Sprint's ~150 lines of coupled orchestration can't be meaningfully abstracted into hooks; composition lets each consumer provide its own subprocess lifecycle |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | `--dry-run` prints 7 step entries and exits 0, no files written | M4, M5 | Yes |
| SC-002 | Full run produces 8 output files in output-dir | M3, M5 | Yes |
| SC-003 | Gate failure triggers retry-then-halt with diagnostic message | M3, M5 | Yes |
| SC-004 | `--resume` with all gates passing skips steps, exits 0 | M4, M5 | Yes |
| SC-005 | `--resume` detects stale spec and re-runs extract | M4, M5 | Yes |
| SC-006 | `uv run pytest tests/sprint/` exits 0 after migration | M2, M5 | Yes |
| SC-007 | `--agents` correctly routes model values to subprocess | M4, M5 | Yes |
