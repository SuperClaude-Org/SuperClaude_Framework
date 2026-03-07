# Agent Handoff: v2.01 Release Validation Investigation

**Date**: 2026-02-24
**Branch**: `feature/v2.01-Architecture-Refactor`
**Repo**: `/config/workspace/SuperClaude_Framework`

---

## 1. Problem Statement

The v2.01 release validation suite runs behavioral tests against `/sc:task` (a Claude Code slash command that classifies tasks into compliance tiers). The test harness spawns `claude -p` subprocesses with prompts like `/sc:task "fix security vulnerability in auth module"` and checks whether the output contains a structured classification header.

**Timeline**:
- Initial run: 9.2% behavioral pass rate. Most tests returned `Error: Reached max turns (3)`. One test (B2 sonnet) scored 1.0.
- After 4 fixes (increased max_turns 3→5, model-specific timeouts, W2 command separator, inlined classification logic): 0.0% behavioral pass rate. Every test now returns `TIMEOUT after NNNs`.

The investigation was asked to determine why the pass rate dropped from 9.2% to 0.0%.

---

## 2. What Was Done

### Phase 1: Parallel Root Cause Investigation
Three specialist agents investigated the problem from different angles:
- **Agent 1 (Harness)**: Test runner mechanics, timeout calculations, resource contention, CLAUDECODE nesting
- **Agent 2 (Protocol)**: Command file restructuring, `allowed-tools` addition, Skill invocation cascade
- **Agent 3 (Environment)**: CLAUDE.md context size, MCP server init, API rate limiting, container constraints

### Phase 2: Merge
All three reports were merged into a unified RCA document with deduplication.

### Phase 3: Verification (Two Passes)
Three verification agents cross-checked each source report against the unified document. Corrections were applied for missing theories, misrepresentations, and factual errors (e.g., MCP server count 2 vs 6).

### Phase 4: Adversarial Scoring
Nine debate agents evaluated each theory adversarially, scoring on evidence strength, root cause likelihood, fix impact, and fix feasibility.

### Phase 5: Experiments
Two experiments were run in parallel to isolate the contribution of specific factors:
- **Experiment 1**: Removed `allowed-tools` from frontmatter, max_turns=2, concurrency=1, `env -u CLAUDECODE`
- **Experiment 5**: Kept `allowed-tools`, max_turns=1, concurrency=1, `env -u CLAUDECODE`

---

## 3. What Was Found

### Experiment Results (Factual)

Both experiments produced identical behavioral patterns:

| Experiment | allowed-tools | max_turns | All 4 B-test results | Duration range |
|------------|--------------|-----------|----------------------|----------------|
| Exp 1 | Absent | 2 | `Error: Reached max turns (2)` | 10-14s |
| Exp 5 | Present (9 tools) | 1 | `Error: Reached max turns (1)` | 7-16s |

- Zero classification headers produced in either experiment
- All tests completed (no timeouts) with exit code 0
- Output was 28 bytes in every case (just the error message)

### Observations

1. **`allowed-tools` does not change the behavior**: The model exhausts all available turns with tool calls regardless of whether `allowed-tools` is present or absent. The pre-experiment hypothesis (RC-1) that `allowed-tools` was the discriminating variable between 9.2% and 0% was not supported by the experimental data.

2. **The model always makes tool calls when processing `/sc:task`**: With max_turns=1, the model uses its single turn for a tool call. With max_turns=2, it uses both turns for tool calls. No text classification output is produced in either case.

3. **Per-turn duration is 7-16s at concurrency=1**: Under isolated conditions with `env -u CLAUDECODE`, each turn completes in 7-16 seconds. The original failing runs (at concurrency=30) showed durations matching the computed timeout ceiling (225-600s), implying per-turn times of ~45-60s under load.

4. **The original 9.2% pass rate also showed "Reached max turns" for most tests**: The prior run was not "working" in the sense that classification was reliably produced. Most tests failed with the same tool-call exhaustion; one test (B2 sonnet) happened to produce classification output.

### Open Questions (Unresolved)

- **What tool(s) does the model call on its first turn?** The experiments captured only the final error message, not intermediate tool calls. Examining `claude -p` verbose output or logs would reveal whether it's the Skill tool, Read, Grep, or something else.
- **Does the `allowed-tools` frontmatter field restrict to ONLY those tools, or does its absence mean ALL tools are available?** The experiment results are consistent with "absence = all tools," but this has not been verified against Claude Code documentation.
- **Why did B2 sonnet score 1.0 in the original run?** This was the only test that produced classification output. Whether this was due to the specific prompt ("explain how the routing middleware works"), the model (sonnet), or random variation is unknown.
- **What is the exact per-turn time under concurrency=30?** The 3-4x amplification (10-15s → 45-60s) is inferred from the timeout ceiling matches but not directly measured.
- **Was the original failing run executed with or without `CLAUDECODE=1`?** If run from within a Claude Code session without `env -u CLAUDECODE`, the behavior may differ from what the experiments tested.
- **Does `--max-turns` have documented semantics in `claude -p` mode?** It is not listed in `claude -p --help` (v2.1.55) but is silently accepted.

---

## 4. File Index

### Test Harness (System Under Test)
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/orchestrator.py` | Test orchestrator — defines all test cases, runs parallel teams |
| `tests/v2.01-release-validation/runner.py` | Executes `claude -p` subprocesses, computes timeouts |
| `tests/v2.01-release-validation/scorer.py` | Scores outputs against expected classification headers |
| `tests/v2.01-release-validation/reporter.py` | Generates aggregate reports |

### Command Files
| File | Description |
|------|-------------|
| `src/superclaude/commands/task-unified.md` | Source of truth for `/sc:task` command (107 lines) |
| `.claude/commands/sc/task-unified.md` | Synced copy loaded by Claude Code at runtime |
| `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` | Full behavioral protocol (~308 lines) loaded via Skill invocation |

### Test Results (Latest Run — All Timeouts)
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/results/aggregate_report.md` | Aggregate report showing 0% behavioral pass rate |
| `tests/v2.01-release-validation/results/all_results.json` | All 63 data points as JSON |
| `tests/v2.01-release-validation/results/run_{1,2,3}/` | Per-run output files (`B*_*_output.txt`, `W*_*_output.txt`) |

### RCA Documents (Produced by This Investigation)
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/rca-agent-1-harness.md` | Agent 1 findings: harness mechanics |
| `tests/v2.01-release-validation/rca-agent-2-protocol.md` | Agent 2 findings: protocol/command file changes |
| `tests/v2.01-release-validation/rca-agent-3-environment.md` | Agent 3 findings: environment/infrastructure |
| `tests/v2.01-release-validation/rca-unified.md` | Merged RCA (pre-experiment). NOTE: RC-1 was later falsified by experiments |

### Adversarial Debate Documents
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/debate-theory-{1..9}.md` | Individual debate results for 9 theories |

### Experiment Results
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/experiments/experiment-results.md` | Analysis of both experiments with revised root cause ranking |
| `tests/v2.01-release-validation/experiments/exp1-summary.txt` | Experiment 1 summary (no allowed-tools, max_turns=2) |
| `tests/v2.01-release-validation/experiments/exp5-summary.txt` | Experiment 5 summary (with allowed-tools, max_turns=1) |
| `tests/v2.01-release-validation/experiments/exp{1,5}-B{1..4}-output.txt` | Raw output files for each test |

### Framework Configuration
| File | Description |
|------|-------------|
| `CLAUDE.md` | Project instructions loaded by `claude -p` in this repo |
| `/config/.claude/CLAUDE.md` | Global instructions with @-references to 8 framework files |
| `/config/.claude/mcp.json` | MCP server configuration (tavily, context7) |
| `/config/.claude/settings.json` | Global settings (`alwaysThinkingEnabled: true`, `model: opus`) |

---

## 5. State of the Codebase

### Uncommitted Changes (per `git status` at session start)
- Modified (staged): `.claude/commands/sc/adversarial.md`, `cleanup-audit.md`, `task-unified.md`, `validate-tests.md` and corresponding `src/superclaude/` copies, plus two skill files
- Untracked: `.dev/releases/current/v2.01-Architecture-Refactor/artifacts/D-0022/` through `D-0040/`, checkpoint files, test integration files, and `tests/v2.01-release-validation/` (the entire test suite and all investigation artifacts)

### Files Created by This Investigation
All files under `tests/v2.01-release-validation/` prefixed with `rca-`, `debate-theory-`, and in the `experiments/` subdirectory were created during this session. None have been committed.

---

## 6. Theories and Their Current Status

| ID | Theory | Pre-Experiment Status | Post-Experiment Status |
|----|--------|----------------------|----------------------|
| RC-1 | `allowed-tools` enables tool-call exhaustion | Primary root cause (95%, 28/40 adversarial) | Falsified by Experiment 1 |
| RC-2 | SuperClaude context explosion (~23K tokens) | High-impact amplifier (95%, 24/40) | Not directly tested; may contribute to tool-call priming |
| RC-3 | Timeout budget ignores startup overhead | Formula defect (95%, 25/40) | Consistent with data; per-turn time under load matches timeout ceilings |
| CF-1 | Skill invocation cascades exceed turn budget | Secondary mechanism (85%, 27/40) | Subsumed by broader finding that all tool calls exhaust turns |
| CF-1b | Classification triplication causes deferral | Speculative (70%, 16/40 adversarial) | Not directly tested |
| CF-2 | Resource contention from 30 concurrent | Amplifier (85%, 21/40) | Consistent with 3-4x per-turn slowdown (10-15s isolated vs ~45-60s under load) |
| CF-3 | CLAUDECODE=1 nesting | Prospective risk (70%, 20/40) | Experiments used `env -u CLAUDECODE`; original run conditions unknown |
| CF-4 | `alwaysThinkingEnabled` | Weak (50%, 18/40) | Not directly tested |
| T-9 | `-p` mode dual-interpretation | Subsumed by RC-1 (14/40) | RC-1 itself falsified; dual-interpretation may still be relevant |
| NEW | Tool-calling is inherent to `/sc:task` | N/A | Observed in both experiments; the model always uses turns for tool calls regardless of `allowed-tools` |

---

## 7. What Has NOT Been Done

- No code changes have been made to `runner.py`, `orchestrator.py`, or the command files
- No experiments at concurrency >1 have been run (all experiments used concurrency=1)
- No experiment with `CLAUDECODE=1` set has been run (all used `env -u CLAUDECODE`)
- No experiment with increased max_turns (e.g., 10+) has been run to see if the model eventually produces text
- No experiment with raw prompts (bypassing `/sc:task` slash command) has been run
- No experiment examining what specific tool(s) the model calls on Turn 1 has been run
- No experiment with a tool-free command file (e.g., `allowed-tools:` set to empty) has been run
- The `rca-unified.md` document has NOT been updated to reflect the experimental falsification of RC-1
- No fixes have been committed or proposed as code changes
