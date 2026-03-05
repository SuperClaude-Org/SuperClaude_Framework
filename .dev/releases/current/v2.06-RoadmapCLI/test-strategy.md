---
spec_source: ".dev/releases/current/v2.06-RoadmapCLI/merged-spec.md"
generated: "2026-03-04T00:00:00Z"
generator: sc:roadmap
validation_philosophy: continuous-parallel
validation_milestones: 2
work_milestones: 5
interleave_ratio: "1:2"
major_issue_policy: stop-and-fix
complexity_class: MEDIUM
---

# Test Strategy: Continuous Parallel Validation

## Validation Philosophy

This test strategy implements **continuous parallel validation** — the assumption that work has deviated from the plan, is incomplete, or contains errors until validation proves otherwise.

**Core Principles**:
1. A validation agent runs in parallel behind the work agent, checking completed work against requirements
2. Major issues trigger a stop — work pauses for refactor/fix before continuing
3. Validation milestones are interleaved between work milestones (not batched at the end)
4. Minor issues are logged and addressed in the next validation pass
5. The interleave ratio is 1:2 (one validation milestone per 2 work milestones), derived from complexity class MEDIUM (score: 0.522)

## Validation Milestones

| ID | After Work Milestone | Validates | Stop Criteria |
|----|---------------------|-----------|---------------|
| V1 | M2 (Sprint Migration to Pipeline) | M1 deliverables (pipeline models, gates, executor, parallel dispatch) + M2 deliverables (SprintConfig inheritance, re-exports, regression) | Sprint test suite fails (`uv run pytest tests/sprint/` non-zero exit); pipeline/ imports from sprint/ or roadmap/ detected; gate_passed() spawns subprocess |
| V2 | M4 (CLI Interface & UX) | M3 deliverables (command registration, prompts, gates data, executor, parallel generate, context isolation, gate enforcement, semantic checks) + M4 deliverables (resume, dry-run, progress, state file, HALT output, depth mapping, agents parsing) | Any AC (AC-01 through AC-07) fails; NFR violation detected; semantic check produces false positives on valid output; state file schema invalid |

**Placement rule**: Validation milestones are placed after every 2 work milestones per the 1:2 interleave ratio. Each validation milestone references the specific work milestones it validates by M# ID.

## Issue Classification

| Severity | Action | Threshold | Example |
|----------|--------|-----------|---------|
| Critical | Stop work immediately, fix before any further progress | Any occurrence | Sprint regression (test failure after migration); `pipeline/` imports from `sprint/` or `roadmap/` (NFR-007 violation); `gate_passed()` invokes subprocess (NFR-003 violation) |
| Major | Stop work, refactor/fix before next milestone | >1 occurrence OR blocking | Missing required frontmatter field in gate criteria; prompt builder performs I/O (NFR-004 violation); cross-cancellation race condition in parallel steps |
| Minor | Log, address in next validation pass | Accumulated count > 5 triggers review | Inconsistent error message format; progress display timing drift; missing edge case in gate tier enforcement |
| Info | Log only, no action required | N/A | Alternative approach for state file atomicity; optimization opportunity in prompt builder; additional semantic check candidate |

## Acceptance Gates

Per-milestone acceptance criteria derived from spec requirements and mapped to deliverables.

| Milestone | Gate Criteria | Pass Condition |
|-----------|--------------|----------------|
| M1 | Pipeline models match spec §3.2; gate_passed() implements 4 tiers; execute_pipeline() handles sequential + parallel; no sprint/roadmap imports in pipeline/ | All D1.1-D1.7 ACs met; `uv run pytest tests/pipeline/` exits 0; no Critical/Major issues |
| M2 | SprintConfig inherits PipelineConfig; release_dir property works; ClaudeProcess re-exported; sprint tests pass | All D2.1-D2.4 ACs met; `uv run pytest tests/sprint/` exits 0 (AC-06); no test file modifications |
| M3 | Click command registered; 7 prompt builders return str; gate criteria match spec §4; parallel generate works; context isolation enforced; retry-then-halt works | All D3.1-D3.10 ACs met; no Critical/Major issues |
| M4 | --resume skips/re-runs correctly; --dry-run prints plan; progress updates every 5s; state file atomic; HALT output matches §6.2; depth mapping correct; --agents parsing works | All D4.1-D4.7 ACs met; AC-01, AC-03, AC-04, AC-05, AC-07 pass; no Critical/Major issues |
| M5 | All test suites pass; all ACs validated; all NFRs verified | All D5.1-D5.5 ACs met; full `uv run pytest` exits 0 |

## Validation Coverage Matrix

| Requirement | Validated By | Milestone | Method |
|-------------|-------------|-----------|--------|
| FR-001 | V2 | M3 | CLI contract test: command invocation triggers pipeline execution |
| FR-002 | V2 | M3 | Parallel test: both generate steps launched; cross-cancel on failure |
| FR-003 | V2 | M3 | Prompt builder assertion: argv contains only --file for inputs list |
| FR-004 | V1 | M1 | Gate unit tests: pre-written files with valid/invalid frontmatter |
| FR-005 | V2 | M3 | Executor test: mock StepRunner returns FAIL; verify retry then halt |
| FR-006 | V2 | M4 | Resume test: pre-create state file + output files; verify skip logic |
| FR-007 | V2 | M4 | Dry-run test: CliRunner; assert stdout contains 7 entries; no subprocess |
| FR-008 | V2 | M3 | Config test: default output_dir is spec_file.parent |
| FR-009 | V2 | M3 | CLI contract test: CliRunner invokes `superclaude roadmap` |
| FR-010 | V1 | M2 | Sprint regression: `uv run pytest tests/sprint/` exits 0 |
| FR-011 | V1 | M1 | Gate test: assert return type is tuple[bool, str\|None] |
| FR-012 | V2 | M4 | State test: verify .roadmap-state.json written with required fields |
| FR-013 | V2 | M4 | Progress test: mock time; verify stdout updates |
| FR-014 | V2 | M3 | Executor test: verify timeout enforcement per step |
| FR-015 | V2 | M4 | CLI test: --agents value passed through to subprocess argv |
| FR-016 | V1 | M1 | Module existence: pipeline/__init__.py exports all public types |
| FR-017 | V1 | M1 | Model test: PipelineConfig construction with all fields |
| FR-018 | V1 | M1 | Model test: Step construction; gate is Optional |
| FR-019 | V1 | M1 | Model test: StepResult with all status values |
| FR-020 | V1 | M1 | Model test: GateCriteria with all enforcement tiers |
| FR-021 | V1 | M1 | Model test: SemanticCheck callable invocation |
| FR-022 | V1 | M1 | Gate test: 4 tiers produce expected check levels |
| FR-023 | V2 | M3 | Executor test: subprocess argv has no --continue or session flags |
| FR-024 | V2 | M3 | Model test: AgentSpec.parse("opus:architect") → correct fields |
| FR-025 | V1 | M1 | Executor test: StepRunner protocol called correctly |
| FR-026 | V2 | M3 | Parallel test: threading.Thread launched; Event shared |
| FR-027 | V2 | M3 | Prompt test: all 7 functions return str; contain required phrases |
| FR-028 | V2 | M4 | State test: JSON schema matches spec §13.4; atomic write verified |
| FR-029 | V2 | M4 | Resume test: hash comparison; skip/re-run decisions correct |
| FR-030 | V1 | M2 | Config test: SprintConfig.release_dir returns work_dir |
| FR-031 | V2 | M3 | Gate test: semantic checks registered on correct steps |
| FR-032 | V2 | M4 | Prompt test: depth parameter produces correct round count |
| FR-033 | V2 | M3 | Executor test: HALT output contains step name, reason, file path |
| NFR-001 | V1 | M2 | Sprint tests pass unchanged (canary) |
| NFR-002 | V1 | M2 | `uv run pytest tests/sprint/` exits 0 |
| NFR-003 | V1 | M1 | Gate test: assert no subprocess.Popen in gate_passed() call |
| NFR-004 | V2 | M3 | Import test: prompts.py module has no I/O imports |
| NFR-005 | V2 | M3 | Gate data test: GateCriteria instances readable without executor |
| NFR-006 | V1 | M1 | Model test: PipelineConfig has no sprint-specific fields |
| NFR-007 | V1 | M1 | Import test: pipeline/ __init__.py has no sprint/roadmap references |
