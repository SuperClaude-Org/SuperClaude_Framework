# Adversarial Debate: RC-2 — SuperClaude Context Explosion (~23K Tokens)

**Date**: 2026-02-24
**Theory**: Each `claude -p` subprocess loads ~23,500 tokens of SuperClaude framework instructions via CLAUDE.md @-references, causing the model to attempt complex work instead of simple classification.
**Debate Role**: Independent adversarial evaluation — both sides argued with maximum rigor.

---

## The Claim Being Evaluated

RC-2 asserts that the ~93,830 bytes (~23,500 tokens) of SuperClaude framework instructions loaded per subprocess — COMMANDS.md (8,205 bytes), FLAGS.md (5,457 bytes), RULES.md (14,165 bytes), MCP.md (12,260 bytes), PERSONAS.md (10,376 bytes), ORCHESTRATOR.md (17,855 bytes), MODES.md (11,827 bytes), PRINCIPLES.md (2,573 bytes), and the project CLAUDE.md (11,112 bytes) — constitute a root cause of the 100% timeout failure. These instructions direct the model to activate specialist personas, invoke MCP servers, follow multi-step workflows (Understand → Plan → Execute → Validate), create TodoWrite task lists, and never jump to conclusions without systematic investigation. The model follows this framework behavior instead of emitting the simple classification header the tests require.

---

## PROSECUTION: Arguments FOR RC-2 as a Root Cause

### P1. The Instructions Are Behaviorally Directive, Not Passive Background

The SuperClaude framework is not inert context. It is a set of explicit behavioral imperatives that directly compete with the test's expected output. Consider the following actual instructions loaded per subprocess:

- **RULES.md**: "Task Pattern: Understand → Plan (with parallelization analysis) → TodoWrite (3+ tasks) → Execute → Track → Validate"
- **RULES.md**: "Batch Operations: ALWAYS parallel tool calls by default, sequential ONLY for dependencies"
- **ORCHESTRATOR.md**: "Fix bug → analyzer persona, --think, Sequential | Security concerns → persona-security + focus security + validate"
- **PERSONAS.md (analyzer)**: "Priorities: Evidence > systematic approach > thoroughness > speed"
- **COMMANDS.md (/sc:task)**: "Auto-Persona: Domain-specific (Security → security, Frontend → frontend, etc.)"

When the model receives `/sc:task "fix security vulnerability in auth module"`, these instructions constitute a directive to: activate the security persona, invoke sequential reasoning, initiate a multi-step workflow, plan tool usage in parallel, and never skip validation. The classification header is a simple three-line output. The framework instructions are a 23,500-token system demanding the model do actual work. The framework instructions have greater token weight and specificity.

**Concrete mechanism**: The ORCHESTRATOR.md master routing table explicitly maps "security audit" → "95% confidence → security persona + --ultrathink + Sequential." The model reads this routing table and follows it. The routing table does not have an exception for "unless you are in test mode."

### P2. Behavioral Evidence Is Consistent With Context-Driven Behavior

The wiring test scores reveal something important: W1–W4 all score exactly 0.15, with `no_raw_dump = 1.0` and all other criteria at 0.0. This pattern means:

- The model engaged with the command (did not echo it as raw text)
- The model produced SOME output (did not immediately crash)
- The model did NOT invoke the skill
- The model did NOT produce protocol flow
- The model did NOT engage observed tools in output

This is precisely the behavioral signature of a model following SuperClaude framework instructions INSTEAD of the command-level instructions. The model's behavior — activate persona, think systematically, prepare to execute — does not produce text output that the scorer can parse. The model is doing "SuperClaude work" rather than "test-expected work."

### P3. The 23K Token Context Directly Increases Time-to-First-Token

The RCA's investigation of RC-3 establishes that startup overhead is critical. The context explosion contributes to that overhead:

- `claude -p` binary startup: 2–5s
- CLAUDE.md + @-ref parsing: 5–10s
- API first-turn latency with ~23K context: 15–30s

These are additive. The 23K token context is not just a behavioral influencer — it is a computational cost that consumes a significant fraction of the per-turn timeout before a single token of response is generated. With opus at 45s/turn and startup overhead potentially reaching 30–60s, the first turn may simply never complete.

### P4. The Context Creates Compounding Pressure at 30 Concurrent Processes

30 concurrent processes × 23,500 tokens = ~700,000 input tokens hitting the API simultaneously per test batch. This is not a marginal API load. Organizational API endpoints have per-minute token limits that this burst pattern can saturate. The CF-2 finding (resource contention) is partially a downstream consequence of RC-2: the context explosion is what creates the burst load. Without the 23K context, the same 30 concurrent processes would submit perhaps 2,000–3,000 tokens each — roughly a 10x reduction in burst API pressure.

### P5. RC-2 Is Causally Prior to RC-1

The prosecution's strongest point is causal ordering. RC-1 (allowed-tools enabling tool-call exhaustion) is the proximate cause of timeout. But RC-2 is the distal cause of WHY those tool calls happen at all. The model uses the tools because the SuperClaude framework instructions tell it to investigate, plan, and execute. Without the 23K context telling the model to "activate security persona" and "follow Understand → Plan → Execute → Validate," the model's default behavior with `allowed-tools` would likely be simpler. It is the combination that produces the failure, and RC-2 is a necessary component.

---

## DEFENSE: Arguments AGAINST RC-2 as a Root Cause

### D1. The Previous Version Also Ran in This Repo With the Same CLAUDE.md and Got ~9.2% Pass Rate

This is the defense's primary argument, and it is strong. The RCA documents that the previous 567-line version of `task-unified.md` achieved approximately 9.2% pass rate. The CLAUDE.md @-references — COMMANDS.md, FLAGS.md, RULES.md, MCP.md, PERSONAS.md, ORCHESTRATOR.md, MODES.md, PRINCIPLES.md — exist at the global `~/.claude/CLAUDE.md` path (`/config/.claude/CLAUDE.md`). These files are NOT part of the repository; they are global configuration. The previous version ran in the same physical environment, with the same runner.py, the same `cwd=repo_root`, and therefore the same CLAUDE.md @-references loaded.

**If the 23K context was a root cause that guarantees failure, it should have guaranteed failure in the previous version too.** It did not. Some tests passed. Therefore, the context alone is not sufficient to cause the 100% failure rate.

**Qualification**: The ~9.2% figure cited in the RCA appears to have been an error or from a different test run. The actual measured results (from `aggregate_report.md`) show behavioral mean of 7.5%, with W-tests scoring 0.15 uniformly and B-tests scoring 0.0 uniformly. But this 7.5% figure still represents non-zero completion — the W-tests ran to completion and produced parseable output (achieving `no_raw_dump = 1.0`). This confirms that with the previous command structure, processes did complete and produce output, despite the same CLAUDE.md context.

### D2. The Model Is Capable of Following Specific Command Instructions Over General CLAUDE.md Instructions

Language models are trained to give priority to specific, in-context instructions over general behavioral priming. The command file itself says "Before ANY text, emit this exact header" — this is a specific, concrete, imperative instruction with an exact format. The CLAUDE.md framework instructions are general operational guidelines. The specificity hierarchy should favor the command-level instruction.

**Evidence for this principle**: The CLAUDE.md ORCHESTRATOR.md itself contains: "Explicit Override: User flags > auto-detection." This means the framework is designed to yield to explicit instructions. A command-level "MANDATORY FIRST OUTPUT" instruction IS an explicit override.

**Counter to prosecution P1**: The ORCHESTRATOR.md routing table maps task types to behaviors, but it operates at the meta-level. The command file operates at the object level — it is the actual task being executed. A well-functioning model should read: "I am executing /sc:task. The /sc:task command says MANDATORY FIRST OUTPUT. Therefore I emit the header first." The framework context should not override the literal command being run.

### D3. The Discriminating Variable Is `allowed-tools`, Not Context Size

The previous version had no `allowed-tools` in frontmatter. The current version does. This is the only structural change between the ~7.5%-passing version and the 0%-passing version. If RC-2 (context) were the root cause, we would expect the previous version to also have failed. It did not.

The defense's hypothesis: with no `allowed-tools`, the model has no tool affordances at all. It sees the task, sees the SuperClaude framework context telling it to "investigate and plan," but has literally no tool calls it can make. Faced with zero available tools, it must produce text. With `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill` present, it now has nine tools matching its conditioned behavior to "use tools to investigate." The context provides the motivation; the `allowed-tools` provides the means. Remove the means and the 23K context is harmless.

**This is the defense's clearest argument**: RC-2 is not a root cause — it is a behavioral primer that only matters when RC-1 gives it tools to act on. The causal diagram is: RC-2 (priming) + RC-1 (affordance) → failure. Without RC-1, RC-2 causes nothing.

### D4. The "Context Explosion" Is Baseline Expected Behavior

The 23K token CLAUDE.md context is not an anomalous condition created by v2.01. It exists in every Claude Code session, including sessions where the model successfully performs tasks with tools available. Every interactive Claude Code session runs with this context. The framework is explicitly designed so that the model follows these instructions as guidance, not as constraints that override task-specific instructions.

The previous 567-line `task-unified.md` had the same 23K context and still achieved partial success. This demonstrates that 23K tokens of SuperClaude context is a sustainable operating condition, not a failure mode in isolation.

### D5. The "Time-to-First-Token" Impact Is Already Captured in RC-3

The prosecution's P3 argument (context increases startup overhead) is valid but belongs to RC-3 (insufficient timeout budgets), not to RC-2 as an independent root cause. The API latency from large context is already characterized in RC-3's startup overhead table:

> "API first-turn latency (~23K context): 15–30s"

RC-3 owns this contribution. Attributing it to RC-2 as well would be double-counting. RC-2's independent contribution is limited to the behavioral dimension (model following framework instructions instead of classification instructions), and D3 shows that behavioral contribution only materializes when tools are available.

---

## Analysis of the Defense's Core Counter-Evidence

The defense's strongest argument requires scrutiny: "The previous version ALSO ran with the same CLAUDE.md and got ~7.5% pass rate, therefore CLAUDE.md is not the cause."

**This argument has three weaknesses**:

1. **7.5% is not 9.2%**: The ~9.2% figure appears to be an approximation or extrapolation from a different data state. The actual measured behavioral pass rate is 7.5% (W-tests at 0.15, B-tests at 0.0). This means classification tests (B1-B4) ALSO failed at 0% in the previous version — they timed out too. The 7.5% comes entirely from wiring tests reaching partial completion (running to completion but not producing protocol flow). This is a weaker signal than "classification tests passed."

2. **The previous version may have had a different operational context**: The `runner.py` uses `cwd=str(repo_root)`. If the previous version tests were run before certain CLAUDE.md @-references existed or were populated, the context would have been smaller. There is no direct evidence from the git history that the global CLAUDE.md had the same 8-file @-reference set when the previous version tests were run. The CLAUDE.md files are in `/config/.claude/` — outside the repository and not tracked in git.

3. **Partial completion does not prove the context had no effect**: The wiring tests in the previous version ran to completion and produced some non-null output. But they still scored only 0.15. If the model had followed command-level instructions cleanly, we would expect protocol flow signals (0.35 weight criterion) to score positive. The model produced output but the wrong output — consistent with context-driven behavior deflecting it from protocol flow.

**Prosecution rebuttal to D3**: The defense claims RC-2 only matters when RC-1 is present. This is partially correct but understates RC-2's independent contribution. Even if `allowed-tools` were removed, the 23K context would still cause:
- Increased time-to-first-token (contributing to RC-3)
- Compounding API burst pressure at 30 concurrency (contributing to CF-2)
- Model behavior deflection even without tools (the model thinks about what it would do, generating reasoning tokens before classification output)

---

## Verdict

### Scoring

| Dimension | Score (0–10) | Rationale |
|-----------|-------------|-----------|
| **Evidence Strength** | 6 | The 23K context is confirmed and its directive content is verified. Behavioral deflection is plausible and mechanistically sound. However, the critical counter-evidence — the previous version partially completing under the same context — significantly weakens the claim that context alone explains the failure. The evidence supports RC-2 as a contributing factor but not as an independent root cause. |
| **Root Cause Likelihood** | 5 | The context is a necessary but not sufficient condition for the failure. It primes the behavior that RC-1 enables. Without RC-1 (allowed-tools), the context priming does not translate into turn-exhausting tool calls. The previous version's partial success with the same context confirms this is an amplifier, not a root cause. The likelihood that fixing only RC-2 (while leaving RC-1 in place) would restore test passage is low. |
| **Fix Impact** | 6 | Fixing RC-2 (running tests without CLAUDE.md, or creating a minimal test CLAUDE.md) would reduce startup overhead, reduce API burst pressure, reduce behavioral deflection, and remove MCP server activation incentive. This would meaningfully improve test reliability even if RC-1 remains. However, it would not eliminate the 0% classification pass rate if `allowed-tools` remains — the model would still consume turns with tool calls. The fix is a genuine improvement but not a cure. |
| **Fix Feasibility** | 7 | Moderately easy. Creating a test-specific minimal CLAUDE.md (or running from `/tmp` with no CLAUDE.md) requires one infrastructure change to `runner.py`. No command file changes are needed. The fix is low-risk, reversible, and isolatable. It can be done in parallel with fixing RC-1 without conflict. Its main downside is that it changes the test execution environment from production-equivalent to test-isolated, which could mask real behavior issues. |

**Total: 24/40 (60%)**

### Classification

**RC-2 is a HIGH-IMPACT AMPLIFIER, not an independent root cause.**

The correct causal model is:

```
RC-2 (23K context priming) + RC-1 (allowed-tools affordance) → Tool-call exhaustion → 100% timeout
                   ↕
RC-2 alone (no tools) → Behavioral deflection → some test degradation, not 100% timeout
```

The defense's core argument holds: the previous version partially completed under the same CLAUDE.md context, which falsifies RC-2 as an independent sufficient cause. However, the prosecution's rebuttal also holds: RC-2 is not merely passive noise. It actively primes the model toward the investigative behavior that RC-1 then enables. RC-2's contributions to startup latency (RC-3 interaction) and burst API pressure (CF-2 interaction) are real and measurable.

**The interaction between RC-1 and RC-2 is where the real failure lives.** The fix priority should be:

1. **Fix RC-1 first** (remove `allowed-tools` or reduce to `Skill` only): This addresses the primary root cause and likely restores test passage even without changing the CLAUDE.md context.

2. **Fix RC-2 in parallel** (test isolation via minimal CLAUDE.md or clean working directory): This reduces startup overhead, burst API pressure, and residual behavioral deflection. The fix is independent and low-risk.

3. **Do not treat RC-2 as the top priority.** Fixing RC-2 without fixing RC-1 would likely improve pass rates from 0% to something low but non-zero — but the fundamental tool-call exhaustion problem would remain.

### Debate Conclusion

The claim that RC-2 is a root cause is partially correct but overstated. It is a root cause of the behavioral deflection problem (model attempts complex work instead of classification) and a contributing cause of timeout (startup overhead, API burst). It is NOT the root cause of the 100% failure rate — that distinction belongs to RC-1. The 100% failure rate requires both RC-1 (tools available) and RC-2 (behavioral priming to use them). Removing either factor alone should improve pass rates, but removing RC-1 is the more impactful and more targeted intervention.

---

*Written by: Adversarial Debate Agent*
*Theory evaluated: RC-2 (SuperClaude Context Explosion ~23K Tokens)*
*Evidence base: rca-unified.md, rca-agent-2-protocol.md, rca-agent-3-environment.md, runner.py, task-unified.md (current and previous), aggregate_report.md*
