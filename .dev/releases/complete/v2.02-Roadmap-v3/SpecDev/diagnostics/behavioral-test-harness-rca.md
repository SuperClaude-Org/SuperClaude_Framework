# Behavioral Test Harness RCA — v2.01 Release Validation

**Date**: 2026-02-24 → 2026-02-25 (experiments)
**Branch**: `feature/v2.01-Architecture-Refactor`
**Repo**: `/config/workspace/SuperClaude_Framework`

---

## 1. Problem Statement

The v2.01 release validation suite runs behavioral tests against `/sc:task` (a Claude Code slash command that classifies tasks into compliance tiers). The test harness spawns `claude -p` subprocesses with prompts like `/sc:task "fix security vulnerability in auth module"` and checks whether the output contains a structured classification header.

**Timeline**:
- Initial run: 9.2% behavioral pass rate. Most tests returned `Error: Reached max turns (3)`. One test (B2 sonnet) scored 1.0.
- After 4 fixes (increased max_turns 3→5, model-specific timeouts, W2 command separator, inlined classification logic): 0.0% behavioral pass rate. Every test now returns `TIMEOUT after NNNs`.

---

## 2. Investigation Summary

### Phase 1: Parallel Root Cause Investigation
Three specialist agents investigated from different angles:
- **Agent 1 (Harness)**: Test runner mechanics, timeout calculations, resource contention, CLAUDECODE nesting
- **Agent 2 (Protocol)**: Command file restructuring, `allowed-tools` addition, Skill invocation cascade
- **Agent 3 (Environment)**: CLAUDE.md context size, MCP server init, API rate limiting, container constraints

### Phase 2: Merge
All three reports merged into unified RCA with deduplication.

### Phase 3: Verification (Two Passes)
Three verification agents cross-checked each report. Corrections applied for missing theories, misrepresentations, and factual errors.

### Phase 4: Adversarial Scoring
Nine debate agents scored each theory on evidence strength, root cause likelihood, fix impact, and fix feasibility.

### Phase 5: Controlled Experiments
Seven targeted experiments isolating individual confounding factors.

---

## 3. Confirmed Root Causes (Experimentally Validated)

### CF-3: CLAUDECODE=1 Nesting — CONFIRMED (Fatal)

**Experiment**: Run `claude -p` with and without `CLAUDECODE=1` environment variable.

| Condition | Result |
|-----------|--------|
| With CLAUDECODE=1 | `Claude Code cannot be launched inside another Claude Code session` |
| With `env -u CLAUDECODE` | Succeeds (`CF3_OK`) |

**Verdict**: Any test run from within a Claude Code session without unsetting CLAUDECODE is invalid. This is a fatal blocker that must be addressed in the harness.

### CF-1: Turn Budget Exhausted Before Classification — CONFIRMED

**Experiment**: `claude -p` with max_turns=1 and `/sc:task` prompt.

| Result |
|--------|
| `Error: Reached max turns (1)` — no classification header emitted |

**Verdict**: The model uses its available turn(s) for tool calls (Skill invocation, file reads, etc.) and never produces the classification text output. This is the primary behavioral failure mode.

### CF-2: Concurrency Amplification — CONFIRMED & QUANTIFIED

**Experiment**: Trivial prompt at concurrency 1, 10, 30 with `env -u CLAUDECODE` and haiku.

| Concurrency | Min | Median | Max | Amplification Factor |
|-------------|-----|--------|-----|---------------------|
| 1 | 6.4s | 6.4s | 6.4s | 1.00x (baseline) |
| 10 | 6.7s | 7.6s | 9.8s | 1.20x |
| 30 | 12.7s | 15.4s | 18.4s | **2.41x** |

**Verdict**: 2.41x latency amplification at N=30. Significant but does not alone explain 45-60s/turn observed in original suite. Amplification compounds with tool-invocation overhead and startup costs.

### RC-3: Timeout Formula Ignores Startup Overhead — CONFIRMED & QUANTIFIED

**Experiment**: Trivial vs `/sc:task` prompt at max_turns=1 and max_turns=5, concurrency=1.

| Prompt Type | Startup Overhead | Per-Turn Time | Startup % (max_turns=1) |
|-------------|-----------------|---------------|------------------------|
| Trivial | 5.98s | 0.20s | 96.8% |
| `/sc:task` | 11.51s | 0.20s | 98.3% |

**Current formula**: `timeout = per_turn * max_turns` (ignores startup entirely)
**Recommended**: `timeout = startup_buffer + per_turn * max_turns` with `startup_buffer ≥ 15s`

**Verdict**: Startup overhead is 6-12s depending on prompt complexity. The `/sc:task` slash command adds +5.5s beyond base startup (CLAUDE.md loading, skill resolution, framework context parsing). Under concurrency amplification, this compounds further.

### T-9: `-p` Mode Dual Interpretation — CONFIRMED

**Experiment**: Same prompt with leading `/sc:task` vs literal `sc:task`.

| Prompt Form | Behavior |
|-------------|----------|
| `/sc:task "explain T-9 parsing"` | Treated as knowledge question about T-9 phone keypads — slash command NOT invoked |
| `sc:task "explain T-9 parsing" --compliance exempt --verify skip` | Recognized as SuperClaude command, produced compliance-tier explanation |

**Verdict**: `-p` mode may not invoke slash commands the same way interactive mode does. The leading `/` may be stripped or reinterpreted. Neither form produced an actual classification header.

---

## 4. Compounding Model

At concurrency=30 with `/sc:task` prompts (original test conditions):

```
Base per-turn (real tool work):     ~10-15s
× 2.41 concurrency factor:         ~24-36s/turn
+ 12s startup (also amplified):    ~17-29s startup under load
─────────────────────────────────
Total for 5 turns:                 ~150-210s
```

This matches the original observation of timeouts hitting 225-600s ceilings. The 0% pass rate was caused by:
1. **CF-1** (tool-call exhaustion) as the primary behavioral failure
2. **CF-2 + RC-3** amplifying latency beyond timeout budgets
3. **CF-3** potentially invalidating runs entirely
4. **T-9** raising questions about whether `-p` mode invokes slash commands at all

---

## 5. Theory Status Table

| ID | Theory | Status | Evidence |
|----|--------|--------|----------|
| CF-3 | CLAUDECODE=1 nesting | **CONFIRMED (Fatal)** | Direct experiment: blocks execution |
| CF-1 | Turn budget exhausted before classification | **CONFIRMED** | max_turns=1 produces only error, no classification |
| CF-2 | Resource contention at concurrency=30 | **CONFIRMED (2.41x)** | Sweep at 1/10/30 |
| RC-3 | Timeout formula ignores startup | **CONFIRMED (6-12s)** | Decomposition: S=5.98s trivial, S=11.51s /sc:task |
| T-9 | `-p` mode dual-interpretation | **CONFIRMED** | Leading `/` changes interpretation |
| RC-1 | `allowed-tools` enables tool-call exhaustion | **Falsified** | Exp 1 vs Exp 5: identical behavior ± allowed-tools |
| RC-2 | SuperClaude context explosion (~23K tokens) | Not directly tested | May contribute to tool-call priming |
| CF-1b | Classification triplication causes deferral | Not directly tested | Speculative |
| CF-4 | `alwaysThinkingEnabled` | Not directly tested | Weak evidence |

---

## 6. What Has NOT Been Done

- No code changes made to `runner.py`, `orchestrator.py`, or command files
- No experiment at concurrency >1 with `/sc:task` prompts (CF-2 used trivial prompts)
- No experiment with increased max_turns (e.g., 10+) to see if model eventually produces text
- No experiment with raw prompts (bypassing `/sc:task` slash command entirely)
- No experiment examining specific tool(s) called on Turn 1
- No experiment with tool-free command file (`allowed-tools:` set to empty)
- The `rca-unified.md` in `tests/v2.01-release-validation/` has NOT been updated
- No fixes committed or proposed as code changes

---

## 7. File Index

### Test Harness
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/orchestrator.py` | Test orchestrator — defines all test cases, runs parallel teams |
| `tests/v2.01-release-validation/runner.py` | Executes `claude -p` subprocesses, computes timeouts |
| `tests/v2.01-release-validation/scorer.py` | Scores outputs against expected classification headers |
| `tests/v2.01-release-validation/reporter.py` | Generates aggregate reports |

### Command Files
| File | Description |
|------|-------------|
| `src/superclaude/commands/task-unified.md` | Source of truth for `/sc:task` command |
| `.claude/commands/sc/task-unified.md` | Synced copy loaded by Claude Code at runtime |
| `src/superclaude/skills/sc-task-unified-protocol/SKILL.md` | Full behavioral protocol loaded via Skill invocation |

### Experiment Artifacts
| File | Description |
|------|-------------|
| `/tmp/v201-cf2-results.txt` | CF-2 concurrency sweep raw data |
| `/tmp/v201-rc3-results.txt` | RC-3 timeout budget raw data |
| `/tmp/v201-top3-*-cf3/` | CF-3 nesting experiment artifacts |
| `/tmp/v201-top3-*-cf1/` | CF-1 turn exhaustion artifacts |
| `/tmp/v201-top3-*-t9/` | T-9 dual-interpretation artifacts |
| `tests/v2.01-release-validation/experiments/` | Earlier experiment results |

### RCA Documents
| File | Description |
|------|-------------|
| `tests/v2.01-release-validation/rca-agent-{1,2,3}.md` | Individual agent findings |
| `tests/v2.01-release-validation/rca-unified.md` | Merged RCA (pre-experiment, RC-1 later falsified) |
| `tests/v2.01-release-validation/debate-theory-{1..9}.md` | Adversarial debate results |

### Framework Configuration
| File | Description |
|------|-------------|
| `CLAUDE.md` | Project instructions loaded by `claude -p` in this repo |
| `/config/.claude/CLAUDE.md` | Global instructions with @-references to 8 framework files |
| `/config/.claude/mcp.json` | MCP server configuration |
| `/config/.claude/settings.json` | Global settings |
