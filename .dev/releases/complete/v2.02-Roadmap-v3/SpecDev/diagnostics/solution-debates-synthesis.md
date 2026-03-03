# Solution Debates Synthesis — Behavioral Test Harness Failures

**Date**: 2026-02-25
**Method**: 5 parallel adversarial debates (Advocate/Critic/Judge format)
**Model**: claude-sonnet-4-6 (debaters), claude-opus-4-6 (synthesis)
**Scoring**: coverage (0.30), sufficiency (0.25), confidence (0.20), feasibility (0.15), blast_radius (0.10)

---

## Confirmed Root Causes (Input)

| ID | Description | Severity | Domain |
|----|-------------|----------|--------|
| CF-3 | CLAUDECODE=1 nesting blocks subprocess execution | Fatal | Harness |
| CF-1 | Model exhausts turns on tool calls, never emits classification | Primary behavioral | Model |
| CF-2 | 2.41x latency amplification at concurrency=30 | Amplifier | Harness |
| RC-3 | Timeout formula ignores 6-12s startup overhead | Formula defect | Harness |
| T-9 | `-p` mode may not invoke slash commands via leading `/` | Invocation | Protocol |

---

## Debate Scoreboard

| Rank | ID | Solution | Score | Coverage | Sufficiency | Confidence | Feasibility | Blast |
|------|----|----------|-------|----------|-------------|------------|-------------|-------|
| 1 | S5 | Bypass `-p` mode (direct API) | **6.90** | 7 | 5 | 7 | 9 | 8 |
| 2 | S4 | Concurrency throttle + adaptive timeout | **6.15** | 6 | 4 | 6 | 9 | 8 |
| 3 | S1 | Harness fix (env + startup buffer) | **5.40** | 4 | 3 | 6 | 9 | 9 |
| 4 | S3 | Inline classification protocol | **4.90** | 3 | 3 | 5 | 9 | 9 |
| 5 | S2 | Classification-first rewrite | **4.35** | 3 | 2 | 4 | 9 | 8 |

---

## Structural Finding: Two Independent Failure Domains

All five debates converged on the same conclusion: the root causes split into two independent domains that no single solution bridges.

```
HARNESS DOMAIN                    MODEL/PROTOCOL DOMAIN
─────────────────                 ─────────────────────
CF-3 (fatal nesting)              CF-1 (turn exhaustion)
CF-2 (concurrency amplification)  T-9  (slash command invocation)
RC-3 (timeout formula)
```

- S1, S4 fix the harness domain but leave model behavior untouched
- S2, S3 fix model behavior but are blocked by the fatal CF-3
- S5 sidesteps both domains by changing the test target (coverage by excision, not repair)

---

## Recommended Compound Strategy

### Tier 1: Harness Infrastructure (Implement Immediately)

**Apply S4** — Subsumes S1 with additional concurrency throttle.

Changes to `runner.py` and `orchestrator.py`:
1. `env -u CLAUDECODE` on all subprocess invocations → resolves CF-3
2. `timeout = 15 + per_turn * max_turns * (1.0 + concurrency / 50)` → resolves RC-3
3. Cap concurrency at 10 → mitigates CF-2 (1.20x vs 2.41x)

**Expected outcome**: Tests execute to completion. Failures now reflect model behavior (CF-1, T-9), not harness defects. Pass rate moves from 0% to unknown-but-diagnosable.

### Tier 2: Model Behavior (Implement After Tier 1)

**Apply S3** — Subsumes S2 with stronger architectural guarantee.

Changes to `task-unified.md` and `sc-task-unified-protocol/SKILL.md`:
1. Inline tier-classification logic (keyword tables, compound phrases, confidence scoring) into command file
2. Classification emitted as pure text before any tool invocation
3. Skill invocation deferred to execution phase only

**Expected outcome**: Classification header always appears in output. CF-1 eliminated for classification phase. T-9 partially neutralized (classification logic in command text, not dependent on slash command dispatch).

### Tier 3: Validation Scaffold (Parallel Track)

**Apply S5** — As a complementary test suite, not a replacement.

New test module using direct Anthropic API calls:
1. System prompt = task-unified.md content + relevant CLAUDE.md context
2. User message = task description
3. No tools provided → forces text classification output
4. Validates classification logic correctness independent of Claude Code integration

**Expected outcome**: Fast, deterministic classification correctness tests. Catches regressions in keyword tables, compound phrases, and scoring logic. Does NOT validate integration behavior.

### Combined Coverage Matrix

| Root Cause | S4 (Tier 1) | S3 (Tier 2) | S5 (Tier 3) | Combined |
|------------|-------------|-------------|-------------|----------|
| CF-3 | FIXED | — | BYPASSED | FIXED |
| CF-1 | — | FIXED | BYPASSED | FIXED |
| CF-2 | MITIGATED | — | BYPASSED | MITIGATED |
| RC-3 | FIXED | — | BYPASSED | FIXED |
| T-9 | — | PARTIAL | BYPASSED | PARTIAL |

**T-9 residual risk**: T-9 remains partially unresolved for the execution phase. If `-p` mode does not invoke slash commands, the full Skill execution (post-classification) may not trigger. This requires separate investigation — either confirming `-p` mode slash command behavior via Claude Code documentation or implementing a workaround (e.g., embedding command content in the prompt rather than relying on slash command dispatch).

---

## Implementation Order

```
Week 1: S4 (harness) → re-run suite → observe new failure distribution
Week 1: S5 (API scaffold) → establish classification correctness baseline
Week 2: S3 (inline protocol) → re-run suite → measure pass rate improvement
Week 2: T-9 investigation → determine if `-p` slash command behavior is fixable
```

---

## Debate Artifacts

Individual debate transcripts available in agent task outputs:
- S1: Harness fix debate
- S2: Classification-first debate
- S3: Inline protocol debate
- S4: Adaptive timeout debate
- S5: Bypass `-p` mode debate

---

*Synthesis performed 2026-02-25. Analyst: claude-opus-4-6.*
*Method: 5 parallel adversarial debates (sonnet debaters) → opus synthesis with compound strategy design.*
