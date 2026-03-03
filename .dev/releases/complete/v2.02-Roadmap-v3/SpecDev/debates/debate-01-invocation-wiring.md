# Debate: Solution #1 — Invocation Wiring Fix

*Conducted 2026-02-22. Debate orchestrator: claude-sonnet-4-6.*
*Solution under review: Option B (Task Agent Wrapper) with Option C fallback.*
*Root cause addressed: RC1 (Invocation Wiring Gap, rank 1, combined score 0.90).*

---

## Advocate FOR

### Argument 1: The root cause is correctly identified and this fix addresses it directly

The ranked-root-causes analysis is unambiguous: the Skill tool is provably absent from `allowed-tools` in both `roadmap.md` and `SKILL.md`. This is a verifiable, concrete gap — not an inferred or probabilistic failure. The fix adds the Skill tool to those lists and establishes a clear delegation chain. There is no interpretation required; the absence is the failure, and the addition is the fix.

### Argument 2: Task agent delegation is an established pattern in this codebase

sc:roadmap already dispatches Task agents in Wave 4 for quality-engineer and self-review roles. The fix does not introduce a new pattern — it extends an existing, working one. The fan-out/fan-in file-based data exchange is also precedented by sc:cleanup-audit. The solution's architectural choices are grounded in observed behavior, not speculation.

### Argument 3: The fallback protocol eliminates the single-point-of-failure risk

The most credible objection to this solution is the unverified assumption that Task agents can access the Skill tool. The solution authors anticipated this and designed a full degraded-mode fallback: if the Skill tool is unavailable to the Task agent, sc:roadmap reads sc:adversarial's SKILL.md directly and dispatches five individual Task agents for each pipeline step. This means the feature cannot be completely broken by the primary path failing — it degrades gracefully.

### Argument 4: The return contract transport problem is solved architecturally

One of the secondary root causes (RC4) was the absence of a structured data transport between sc:adversarial and its caller. The solution directly defines a file-based `return-contract.yaml` convention with six typed fields, a write step in sc:adversarial, and a corresponding read step in sc:roadmap. This is not bolted on — it follows the fan-in pattern used elsewhere in the framework.

### Argument 5: Blast radius is minimal and risk is bounded

Five files are modified. Four of the five changes are additive (frontmatter line, new section in adversarial-integration.md, new subsection in sc:adversarial). Only one change is a rewrite (Wave 2 step 3). Waves 0, 1A, 1B, 3, and 4 of sc:roadmap are untouched. All other skills and commands are unaffected. The surface area of potential regression is among the smallest possible for a fix addressing the primary root cause.

---

## Advocate AGAINST

### Argument 1: The Task agent's access to the Skill tool is an unverified assumption that underpins the entire primary path

The solution document acknowledges this explicitly: "Whether Task agents can access the Skill tool has not been empirically verified." The Skill tool description says "Do not invoke a skill that is already running" — but it does not confirm that Task agents inherit the full tool set of their parent conversation. If Task agents operate with a restricted tool set (which is common in agent sandbox models), the primary path fails immediately, and the fix degrades to Option C without ever testing Option B. A solution where the first path is unknowable without testing is not a validated fix — it is a hypothesis.

### Argument 2: The fallback (Option C) introduces the duplication problem the solution claims to avoid

The solution argues against Option C as a primary path because it "duplicates ~1700 lines of adversarial protocol logic." Yet the fallback protocol does exactly this: it instructs sc:roadmap to "read sc:adversarial's SKILL.md directly and dispatch Task agents to execute each of the 5 adversarial steps inline." If the primary path is unreliable (unverified Skill tool access), the fallback will be the actual execution path in production. The solution effectively ships Option C with Option B as an aspirational wrapper. The maintenance burden of duplication is not eliminated — it is made conditional on an unverified runtime assumption.

### Argument 3: The return-contract.yaml write step requires sc:adversarial to detect its invocation context

Change 5 in the implementation details states that sc:adversarial should write the return contract "when invoked by another command (detected by the presence of a calling context)." This detection mechanism is undefined. How does sc:adversarial know it is being invoked by sc:roadmap versus being run standalone? If standalone invocations always write return-contract.yaml, this creates unnecessary file artifacts. If the detection logic is absent, the file is never written, and sc:roadmap reads a missing file and falls back — possibly silently.

### Argument 4: Timeout and resource constraints for deep adversarial debates are not addressed

The solution raises the concern about Task agent timeouts for "deep adversarial debates with 5+ agents (3 debate rounds, 5 pipeline steps, each with sub-agent delegation)" but dismisses it by stating timeouts are "configurable." No timeout value is specified. No evidence is provided that the default or configured timeout is sufficient for a nested execution chain of: sc:roadmap Task dispatch -> Task agent -> Skill invocation -> sc:adversarial -> 5-step pipeline -> sub-agent delegations. This is a compounding latency problem that could cause silent failures where the Task agent times out mid-pipeline, sc:roadmap finds an incomplete return-contract.yaml, and the fallback activates without the user knowing why.

### Argument 5: The solution partially addresses RC2 but the instruction language remains ambiguous in one critical place

The solution rewrites Wave 2 step 3 with explicit sub-steps and a Task agent prompt. However, the instructions to the Task agent itself contain natural language ("Use the Skill tool to invoke sc:adversarial with these arguments") without specifying the exact Skill tool call syntax. The ranked root cause analysis identified undefined verbs as a primary compounding factor. The fix's Task agent prompt reproduces this ambiguity one level down — Claude must now interpret "use the Skill tool" inside the Task agent, which is the same interpretation problem the fix was meant to solve, relocated to a different execution context.

---

## Rebuttal (FOR responds to AGAINST)

### Rebuttal to Argument 1 (Unverified Skill tool access)

The unverified assumption is real, but the fallback protocol converts this from a blocking risk to a graceful degradation. The question is not "does the primary path work?" but "does the feature work?" — and the answer is yes in both cases. Empirical verification is deferred, not dismissed. The confidence score of 0.80 already accounts for this uncertainty. The solution is not presented as proven; it is presented as the architecturally sound path with a tested fallback.

### Rebuttal to Argument 2 (Fallback duplicates Option C)

The duplication concern is valid in theory but mischaracterizes the maintenance burden in practice. Option C as a primary path means maintaining two copies of the adversarial protocol as a design invariant, with no mechanism to detect drift. The fallback path in this solution is a last-resort degraded mode, not a parallel maintenance target. If Option B's primary path is confirmed to work, the fallback becomes dormant code. The maintenance burden exists only while the primary path is unverified — which is a transient state, not a permanent architecture.

### Rebuttal to Argument 3 (Invocation context detection)

The against argument identifies a genuine gap: sc:adversarial has no defined mechanism to detect whether it is being called by sc:roadmap or run standalone. This is a legitimate implementation gap. However, the simplest resolution — always write return-contract.yaml as the final step, regardless of invocation context — eliminates the detection problem entirely. Idempotent output files do not require caller detection. The artifact is either consumed or ignored. This is a straightforward fix to a real but narrow gap.

### Rebuttal to Argument 4 (Timeout concerns)

The timeout concern is real but was already partially mitigated before this debate. The solution notes that Task agent timeouts are "configurable." What strengthens the FOR position is that the fallback path (inline execution via five sequential Task agents) has smaller individual timeout requirements than a single Task agent running the full sc:adversarial pipeline. If the primary path times out, the fallback naturally decomposes the workload. The timeout problem is real for the primary path; it is partially self-resolving for the fallback.

### Rebuttal to Argument 5 (Ambiguous instruction language in Task prompt)

This is the strongest objection in the AGAINST case. The Task agent prompt uses natural language where it should use explicit syntax. However, the Skill tool's invocation syntax is well-documented in Claude's context ("Use this tool with the skill name and optional args") and the prompt does name the specific skill (`sc:adversarial`) with explicit arguments. The ambiguity is lower than the original "Invoke sc:adversarial" because: (1) the tool name is specified ("Use the Skill tool"), (2) the arguments are enumerated, and (3) the Task agent context is narrower (sole job is to invoke sc:adversarial). This is an improvement over the status quo, though not a complete resolution of the RC2 specification gap.

---

## Scoring Matrix

| Dimension | Weight | Score | Justification |
|-----------|--------|-------|---------------|
| Root cause coverage | 0.25 | 0.80 | Directly addresses RC1 (Skill tool absent from allowed-tools) and partially addresses RC2 (rewritten instructions), RC4 (return-contract.yaml convention), and RC5 (fallback protocol). Does not address RC3 (agent dispatch mechanism within sc:adversarial) as a primary target. The fix covers the ranked #1 root cause completely and three of the four remaining causes partially. Score reduced from potential 0.90 because RC3 is acknowledged but deferred. |
| Completeness | 0.20 | 0.65 | The solution handles the happy path and defines a fallback. However, three edge cases are unresolved: (1) the invocation context detection problem in sc:adversarial (when to write return-contract.yaml), (2) partial/incomplete return-contract.yaml handling when a Task agent times out mid-pipeline, and (3) the Task agent prompt's natural-language Skill tool instruction (Argument 5). These are not fatal gaps but they are gaps. The fallback itself is complete; the primary path has identifiable holes. |
| Feasibility | 0.25 | 0.75 | The file changes are minimal and all use established patterns. The primary blocker (Task agent access to Skill tool) is unverified but architecturally plausible. The fallback ensures the feature ships regardless. Implementation requires 5 file edits, no new infrastructure, and no Python code changes. The `make sync-dev` step is a known requirement. Reduced from 0.85 because the Skill tool access assumption introduces meaningful implementation uncertainty that cannot be resolved without a test run. |
| Blast radius | 0.15 | 0.85 | Five files affected, four additively. Waves 0, 1A, 1B, 3, and 4 of sc:roadmap are untouched. All other skills and commands are unaffected. The only structural change is the Wave 2 step 3 rewrite, which is self-contained. The `Skill` addition to allowed-tools is non-breaking (it does not remove any existing capability). Score is high because the surface area is genuinely narrow; reduced from 1.0 because the Wave 2 step 3 rewrite does change behavior for the `--multi-roadmap` path, which is the critical path under repair. |
| Confidence | 0.15 | 0.72 | The solution authors' self-reported confidence is 0.80. Debate analysis reduces this slightly to 0.72 for three reasons: (1) the Task agent Skill tool access assumption is unverified and cannot be resolved without empirical testing, (2) the invocation context detection gap in sc:adversarial is a genuine unresolved implementation detail, and (3) the Task agent prompt's ambiguous language partially reproduces the RC2 specification problem. The fallback protocol prevents the confidence penalty from being larger — without it, confidence would be closer to 0.60. |

## Fix Likelihood: 0.76

**Computation**:

| Dimension | Weight | Score | Weighted |
|-----------|--------|-------|----------|
| Root cause coverage | 0.25 | 0.80 | 0.200 |
| Completeness | 0.20 | 0.65 | 0.130 |
| Feasibility | 0.25 | 0.75 | 0.188 |
| Blast radius | 0.15 | 0.85 | 0.128 |
| Confidence | 0.15 | 0.72 | 0.108 |
| **Total** | **1.00** | — | **0.754** |

**Rounded fix likelihood: 0.76**

**Interpretation**: The solution has a 76% probability of resolving the adversarial pipeline invocation failure when implemented as specified. The primary uncertainty is the unverified Task agent Skill tool access assumption. With the fallback, effective feature delivery probability is higher (estimated 0.88-0.92) because Option C inline execution is a known-feasible path — but it does not deliver the same quality of output as full sc:adversarial invocation.

---

## Unresolved Concerns

### 1. Task agent Skill tool access (Critical — primary path validity)

The solution's primary execution path (Task agent invokes sc:adversarial via Skill tool) has not been empirically tested. No evidence exists in the codebase that a Task agent dispatched by a parent conversation can access the Skill tool and successfully load a named skill. This is the single highest-risk unresolved question. Recommendation: a targeted test before implementing the full solution — dispatch a Task agent with a minimal prompt that uses the Skill tool to load any named skill and confirm successful execution.

### 2. sc:adversarial invocation context detection (Medium — correctness gap)

The implementation requires sc:adversarial to write return-contract.yaml "when invoked by another command." The detection mechanism is undefined. The simplest resolution (always write the file) may produce unnecessary artifacts in standalone usage. The correct resolution (write the file only when a `--caller` flag is set, or always write idempotently) was not specified in the solution. This needs a decision before implementation.

### 3. Task agent timeout for nested adversarial pipeline (Medium — reliability gap)

A full adversarial debate (5 steps, 3 rounds, 5+ agents) running inside a Task agent that is itself dispatched from sc:roadmap creates a nested execution chain with compounding timeout risk. The solution acknowledges this but provides no concrete timeout specification or measurement baseline. Without knowing the typical duration of a full sc:adversarial run, the "configurable timeout" mitigation cannot be practically applied.

### 4. Task agent prompt Skill tool invocation syntax (Low-Medium — RC2 residual)

The Task agent prompt instructs Claude to "Use the Skill tool to invoke sc:adversarial with these arguments" using natural language. This partially reproduces the RC2 specification gap (undefined verb, ambiguous syntax) one level down in the execution hierarchy. While the narrower context and explicit argument list reduce the ambiguity, the exact Skill tool call syntax should be specified in the prompt to fully close RC2.

### 5. Drift between Option B (primary) and Option C (fallback) over time (Low — maintenance concern)

If the primary path (Option B) works, the fallback (Option C inline execution) becomes dormant code. Over time, changes to sc:adversarial's 5-step pipeline may not be reflected in the fallback instructions embedded in sc:roadmap's Wave 2 step 3d. This creates a latent drift problem where the fallback silently executes a stale version of the adversarial protocol. A maintenance protocol (periodic sync review, or a reference to sc:adversarial's SKILL.md rather than inline protocol copy) would mitigate this.

---

*Debate conducted 2026-02-22. Analyst: claude-sonnet-4-6 (debate orchestrator).*
*Input: solution-01-invocation-wiring.md + ranked-root-causes.md.*
*Fix likelihood: 0.76 (weighted). Effective feature delivery probability: ~0.88-0.92 with fallback.*
