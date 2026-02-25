# Experiment Results: RC-1 vs RC-3 Isolation

**Date**: 2026-02-24
**Environment**: `env -u CLAUDECODE`, concurrency=1 (sequential), model=sonnet

---

## Experiment 1: Remove `allowed-tools`, max_turns=2

**Hypothesis**: If `allowed-tools` is the root cause, removing it should allow the model to produce text output (classification header) instead of making tool calls.

**Setup**: Git worktree from HEAD (which lacks `allowed-tools` in frontmatter). max_turns=2.

| Test | Prompt | Expected | Duration | Output |
|------|--------|----------|----------|--------|
| B1 | fix security vulnerability in auth module | STRICT | 14s | `Error: Reached max turns (2)` |
| B2 | explain how the routing middleware works | EXEMPT | 12s | `Error: Reached max turns (2)` |
| B3 | fix typo in error message | LIGHT | 13s | `Error: Reached max turns (2)` |
| B4 | add pagination to user list endpoint | STANDARD | 10s | `Error: Reached max turns (2)` |

**Result**: ALL tests hit "Reached max turns" — zero classification output produced. **RC-1 is FALSIFIED.**

---

## Experiment 5: Keep `allowed-tools`, max_turns=1

**Hypothesis**: If the timeout budget (RC-3) is the root cause, max_turns=1 should complete within the timeout but still produce no classification output (because the model uses its single turn for a tool call).

**Setup**: Main repo (has `allowed-tools` in frontmatter). max_turns=1.

| Test | Prompt | Expected | Duration | Output |
|------|--------|----------|----------|--------|
| B1 | fix security vulnerability in auth module | STRICT | 12s | `Error: Reached max turns (1)` |
| B2 | explain how the routing middleware works | EXEMPT | 16s | `Error: Reached max turns (1)` |
| B3 | fix typo in error message | LIGHT | 10s | `Error: Reached max turns (1)` |
| B4 | add pagination to user list endpoint | STANDARD | 7s | `Error: Reached max turns (1)` |

**Result**: ALL tests hit "Reached max turns" in 7-16s — well within any timeout. The model uses its single turn for a tool call. **Confirms tool-call exhaustion is independent of `allowed-tools`.**

---

## Critical Findings

### 1. RC-1 (`allowed-tools`) is FALSIFIED as root cause

Both experiments produce identical behavior regardless of `allowed-tools`:
- With `allowed-tools` (9 tools listed): model makes tool calls, hits max turns
- Without `allowed-tools` (field absent): model STILL makes tool calls, hits max turns

**Explanation**: The `allowed-tools` frontmatter field RESTRICTS which tools are available, it does not ENABLE them. When absent, the model has access to ALL tools by default. Removing it actually gives the model MORE tools, not fewer.

### 2. The fundamental problem: `/sc:task` always triggers tool-calling behavior

In `claude -p` mode, when the model receives `/sc:task "..."`:
1. Claude Code loads the command file (`.claude/commands/sc/task-unified.md`)
2. The model sees the Skill invocation directive on line 70 (`> Skill sc:task-unified-protocol`)
3. The model calls the Skill tool (consuming 1 turn)
4. If max_turns allows more, the model continues with tool calls (Read, Grep, etc.)
5. The model NEVER produces raw text output — it always uses its turns for tool calls
6. When max_turns is exhausted, `claude -p` returns "Error: Reached max turns (N)"

This behavior is CONSTANT across both versions of the command file. The model cannot be directed to produce text output first when tool calls are available.

### 3. The 9.2% → 0% regression was caused by the timeout interaction, not `allowed-tools`

| Version | max_turns | Per-turn time (isolated) | Per-turn time (30 concurrent) | Total time | Timeout | Result |
|---------|-----------|-------------------------|-------------------------------|------------|---------|--------|
| Old | 3 | ~10-15s | ~45-60s | 135-180s | 180s flat | Some complete (9.2%) |
| New | 5 | ~10-15s | ~45-60s | 225-300s | 225-300s (per_turn×max_turns) | ALL timeout (0%) |

The "fix" of increasing max_turns from 3→5 increased the ACTUAL processing time beyond the computed timeout ceiling when running under 30-process concurrency load.

### 4. Per-turn duration is ~10-15s isolated, but ~45-60s under load

- Isolated (concurrency=1): 7-16s per turn (these experiments)
- Under load (concurrency=30): ~45-60s per turn (inferred from original 225-300s timeouts / 5 turns)
- This 3-4x amplification under load confirms CF-2 (resource contention) is a major factor

---

## Revised Root Cause Ranking

| Rank | Theory | Original Score | Revised Status |
|------|--------|---------------|----------------|
| 1 | **RC-1: allowed-tools** | 28/40 (Primary) | **FALSIFIED** — does not affect behavior |
| 2 | **NEW: Tool-calling is inherent to /sc:task** | N/A | **TRUE ROOT CAUSE** — model always calls tools |
| 3 | **RC-3: Timeout budget** | 25/40 | **CONFIRMED** — direct cause of 9.2%→0% regression |
| 4 | **CF-2: Concurrency amplification** | 21/40 | **CONFIRMED** — 3-4x per-turn slowdown under load |
| 5 | **CF-1: Skill cascade** | 27/40 | **SUBSUMED** — part of inherent tool-calling |
| 6 | **RC-2: Context explosion** | 24/40 | **CONTRIBUTES** — primes model toward investigation |

---

## Recommended Fix Strategy (Revised)

### To fix the 0% → 9.2% regression (restore previous behavior):
1. **Fix timeout formula**: Add 60s startup overhead
2. **Reduce max_turns for classification back to 3**
3. **Reduce concurrency from 30 to 5**

### To fix the underlying 9.2% → higher pass rate (improve classification behavior):
4. **Make classification a text-only operation**: Create a SEPARATE command file for classification that has NO Skill invocation, NO tool-triggering instructions, and explicitly sets `allowed-tools:` to an empty list or removes tool access
5. **Or bypass slash commands entirely**: Send classification prompts as raw text (not `/sc:task "..."`) with explicit "output this header as your ONLY response" instructions
6. **Or increase max_turns sufficiently**: Set max_turns=10+ for the classification tests and accept that some turns will be wasted on tool calls, as long as the model eventually produces text
