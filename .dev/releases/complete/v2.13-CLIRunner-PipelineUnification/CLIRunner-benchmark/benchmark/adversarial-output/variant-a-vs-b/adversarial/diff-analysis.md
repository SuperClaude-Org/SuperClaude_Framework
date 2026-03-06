# Diff Analysis: Pipeline Unification Comparison

## Metadata
- Generated: 2026-03-05T00:00:00Z
- Variants compared: 2
- Total differences found: 11
- Categories: structural (2), content (5), contradictions (2), unique (2)
- Code-verified claims checked against:
  - `src/superclaude/cli/roadmap/executor.py:53`
  - `src/superclaude/cli/roadmap/executor.py:81`
  - `src/superclaude/cli/roadmap/executor.py:472`
  - `src/superclaude/cli/pipeline/executor.py:45`
  - `src/superclaude/cli/pipeline/process.py:24`
  - `src/superclaude/cli/sprint/process.py:25`
  - `src/superclaude/cli/sprint/executor.py:32`

## Structural Differences

| # | Area | Variant A | Variant B | Severity |
|---|---|---|---|---|
| S-001 | Document posture | Proposal with solution architecture, benefits, scope, risk | Challenge memo organized as stress-test questions and objections | Medium |
| S-002 | Actionability structure | Ends with concrete target architecture and scoped work table | Ends with decision questions and targeted-fix alternative | Medium |

## Content Differences

| # | Topic | Variant A Approach | Variant B Approach | Severity |
|---|---|---|---|---|
| C-001 | Nature of duplication | Treats sprint and pipeline as materially duplicated orchestration layers and argues for consolidation | Accepts surface overlap but argues execution semantics differ enough that consolidation may be cosmetic | High |
| C-002 | File-passing divergence | Treats `@file` vs `--file` as architectural symptom of split orchestration | Treats it as a local bug that can be fixed without broader refactor | Medium |
| C-003 | Retry/parallel benefits | Claims sprint would gain executor retry and parallel-group features if unified | Argues those features are largely inapplicable or unsafe for sprint because phases mutate shared working tree | High |
| C-004 | Scope estimate | Rates core sprint executor refactor as Medium | Rates same work as Large due to poll-loop complexity, TUI/monitor/watchdog/tmux/diagnostics integration | High |
| C-005 | State management | Proposes shared `StateManager` protocol across sprint and roadmap | Argues separate state formats are acceptable because domains differ | Medium |

## Contradictions

| # | Point of Conflict | Variant A Position | Variant B Position | Impact |
|---|---|---|---|---|
| X-001 | Executor unification feasibility | Sprint-specific runtime concerns can be pushed into callbacks/wrappers around `run_step` | Sprint's runtime concerns are intrinsically mid-execution and would force a nested poll loop, making unification mostly cosmetic | High |
| X-002 | Value of shared executor capabilities | Retry/parallel/testing-surface benefits justify consolidation | Retry/parallel are poor fit for sprint; testing surface shifts rather than shrinks | High |

## Unique Contributions

| # | Variant | Contribution | Value Assessment |
|---|---|---|---|
| U-001 | Variant A | Concrete target architecture sketch showing `execute_pipeline(... run_step=..., on_step_start=..., on_step_complete=..., on_state_update=..., cancel_check=...)` | High |
| U-002 | Variant B | Lower-blast-radius alternative plan that fixes dead code, file passing, and logging hooks without full sprint refactor | High |

## Summary
- Total structural differences: 2
- Total content differences: 5
- Total contradictions: 2
- Total unique contributions: 2
- Highest-severity items: S-001, C-001, C-003, C-004, X-001, X-002

## Verified Notes
- Verified: roadmap delegates to `execute_pipeline()` in `src/superclaude/cli/roadmap/executor.py:494`.
- Verified: `roadmap_run_step()` uses `ClaudeProcess(... extra_args=["--file", ...])` in `src/superclaude/cli/roadmap/executor.py:103`.
- Verified: `_build_subprocess_argv()` exists and appears unused from code search at `src/superclaude/cli/roadmap/executor.py:53`.
- Verified: sprint `ClaudeProcess` overrides `start`, `wait`, and `terminate` around largely duplicated base-process logic in `src/superclaude/cli/sprint/process.py:91`, `src/superclaude/cli/sprint/process.py:128`, `src/superclaude/cli/sprint/process.py:139` compared with `src/superclaude/cli/pipeline/process.py:89`, `src/superclaude/cli/pipeline/process.py:115`, `src/superclaude/cli/pipeline/process.py:126`.
- Verified: sprint poll loop contains mid-execution TUI, watchdog, signal, timeout, and monitor interactions in `src/superclaude/cli/sprint/executor.py:94`.
- Unverified: the narrative that pipeline was historically extracted from sprint rather than introduced primarily for roadmap. Available local git history was insufficient to prove origin intent.
