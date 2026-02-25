# Tasklist Phases — sc:roadmap Adversarial Failure Diagnostic

**Format**: sc:task-unified (STRICT compliance)
**Total Tasks**: 17 across 4 phases

---

## Phase 1: Root Cause Investigation

### T01.01 — Invocation Wiring Gap Analysis

**Status**: pending
**Depends On**: —
**Agent**: root-cause-analyst
**Skill**: /sc:troubleshoot
**Output**: `diagnostics/root-cause-01-invocation-wiring.md`

**Description**:
Investigate whether Claude Code's skill system supports one skill invoking another skill at runtime. Specifically: can `sc:roadmap` (a skill loaded via slash command) invoke `sc:adversarial` (another skill) mid-execution?

**Analytical Lens**: Invocation wiring — is there a mechanism for skill-to-skill invocation, or must all skill invocations originate from user input?

**Investigation Steps**:
1. Read `src/superclaude/skills/sc-roadmap/SKILL.md` lines 130-143 (Wave 2 behavioral instructions)
2. Read `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` "Invocation Patterns" section
3. Search for evidence of skill-to-skill invocation in the codebase (any skill that successfully invokes another)
4. Examine Claude Code's Skill tool documentation — does it support programmatic invocation from within a skill?
5. Check if there's a difference between "invoke sc:adversarial" (natural language instruction in SKILL.md) and actually triggering the Skill tool

**Evidence Requirements**:
- Concrete code/config evidence of whether skill-to-skill invocation is supported
- If not supported: what mechanism was the SKILL.md author assuming would work?
- Likelihood score (0.0-1.0) with justification

---

### T01.02 — Specification-Execution Gap Analysis

**Status**: pending
**Depends On**: —
**Agent**: root-cause-analyst
**Skill**: /sc:troubleshoot
**Output**: `diagnostics/root-cause-02-spec-execution-gap.md`

**Description**:
Analyze the specificity gap between Wave 2's behavioral instructions (which successfully invoke adversarial) and the actual execution. Compare Wave 2 instructions (lines 130-143) with Wave 4 validation instructions (which work correctly).

**Analytical Lens**: Specification precision — are the Wave 2 instructions specific enough that Claude can deterministically follow them?

**Investigation Steps**:
1. Read Wave 2 instructions in `src/superclaude/skills/sc-roadmap/SKILL.md` (lines 130-143)
2. Read Wave 4 instructions in the same file (validation wave that works)
3. Compare instruction specificity: Wave 2 says "Invoke sc:adversarial" — Wave 4 says what exactly?
4. Identify ambiguity in Wave 2 step 3: "Invoke sc:adversarial for multi-roadmap generation per refs/adversarial-integration.md" — is this a Skill tool call, a Task agent spawn, or a natural language instruction?
5. Check whether `refs/adversarial-integration.md` invocation patterns use pseudo-code or actual tool-call syntax

**Evidence Requirements**:
- Side-by-side comparison of Wave 2 vs Wave 4 instruction specificity
- Identification of specific ambiguous phrases in Wave 2 step 3
- Assessment of whether a language model could reasonably interpret the instructions as "spawn Task agents directly"
- Likelihood score (0.0-1.0) with justification

---

### T01.03 — Agent Dispatch Mechanism Analysis

**Status**: pending
**Depends On**: —
**Agent**: root-cause-analyst
**Skill**: /sc:troubleshoot
**Output**: `diagnostics/root-cause-03-agent-dispatch.md`

**Description**:
Investigate why `system-architect` agents were spawned instead of `debate-orchestrator`. What mechanism maps skill invocations to agent types?

**Analytical Lens**: Agent dispatch — what determines which agent type is spawned when a skill or command is executed?

**Investigation Steps**:
1. Read `src/superclaude/agents/debate-orchestrator.md` — what triggers this agent?
2. Search for agent selection logic: how does Claude Code decide which subagent_type to use in Task tool calls?
3. Read `src/superclaude/skills/sc-adversarial/SKILL.md` — does it specify that debate-orchestrator should be used?
4. Check if `system-architect` is a default/fallback agent type
5. Examine whether the `--agents opus,haiku` spec was interpreted as "use these models as system-architect agents" rather than "pass these to sc:adversarial for variant generation"

**Evidence Requirements**:
- The specific code/config that maps skill invocations to agent types
- Why `system-architect` was chosen over `debate-orchestrator`
- Whether `debate-orchestrator` is registered as an available subagent_type in the Task tool
- Likelihood score (0.0-1.0) with justification

---

### T01.04 — Return Contract Data Flow Analysis

**Status**: pending
**Depends On**: —
**Agent**: root-cause-analyst
**Skill**: /sc:troubleshoot
**Output**: `diagnostics/root-cause-04-return-contract.md`

**Description**:
Investigate whether there is a structured mechanism for one skill to receive a return contract from another. The adversarial integration ref defines a return contract (status, merged_output_path, convergence_score, etc.) but is there an actual data pipeline?

**Analytical Lens**: Return contract data flow — can structured data be returned from a skill invocation to the calling skill?

**Investigation Steps**:
1. Read `refs/adversarial-integration.md` "Return Contract Consumption" section
2. Read `src/superclaude/skills/sc-adversarial/SKILL.md` — does it produce a return contract in a parseable format?
3. Search for any skill in the codebase that successfully consumes output from another skill
4. Examine how Task agent results are returned — is the result a string, or structured data?
5. Check if the return contract pattern relies on file-based communication (write to file, read from file) vs. in-memory return values

**Evidence Requirements**:
- Whether any structured return mechanism exists between skills
- If file-based: whether the file paths are deterministic enough for the caller to find them
- Whether the lack of a return mechanism could cause Claude to "shortcut" by doing the work inline
- Likelihood score (0.0-1.0) with justification

---

### T01.05 — Claude Behavioral Interpretation Analysis

**Status**: pending
**Depends On**: —
**Agent**: root-cause-analyst
**Skill**: /sc:troubleshoot
**Output**: `diagnostics/root-cause-05-claude-behavior.md`

**Description**:
Analyze whether Claude's decision to spawn two system-architect agents and manually synthesize was a rational interpretation of the instructions, given the constraints it faced.

**Analytical Lens**: Behavioral interpretation — was this a sensible fallback given ambiguous instructions and missing infrastructure?

**Investigation Steps**:
1. Re-read Wave 2 step 3 from Claude's perspective: what would a language model do with "Invoke sc:adversarial"?
2. Consider: if Claude determined that skill-to-skill invocation wasn't possible, spawning Task agents to generate competing variants is the closest approximation
3. Analyze whether the manual synthesis was an attempt to approximate the adversarial merge step
4. Check if Claude has access to the Skill tool within a skill execution context
5. Evaluate: did Claude fail to follow instructions, or did it correctly identify that the instructions were unimplementable and chose the best available fallback?

**Evidence Requirements**:
- Assessment of whether the observed behavior was a reasonable interpretation
- Whether Claude logged or emitted any indication of falling back from the intended path
- Comparison of the actual output quality vs what the adversarial pipeline would have produced
- Likelihood score (0.0-1.0) with justification — specifically, likelihood that this root cause ALONE explains the failure

---

### T01.06 — Adversarial Root Cause Ranking

**Status**: pending
**Depends On**: T01.01, T01.02, T01.03, T01.04, T01.05
**Agent**: debate-orchestrator (via /sc:adversarial)
**Skill**: /sc:adversarial --compare
**Output**: `diagnostics/ranked-root-causes.md` + `diagnostics/adversarial/`

**Description**:
Invoke `/sc:adversarial --compare` on the 5 root cause documents to rank them by likelihood and impact. The adversarial pipeline debates which root causes are most credible and which have the highest explanatory power.

**Invocation**:
```
/sc:adversarial --compare diagnostics/root-cause-01-invocation-wiring.md,diagnostics/root-cause-02-spec-execution-gap.md,diagnostics/root-cause-03-agent-dispatch.md,diagnostics/root-cause-04-return-contract.md,diagnostics/root-cause-05-claude-behavior.md --depth standard --output diagnostics/
```

**Post-Processing**:
After adversarial debate completes, produce `diagnostics/ranked-root-causes.md` with:
1. Ranked list of root causes by `(likelihood * 0.6) + (impact * 0.4)`
2. Each root cause's likelihood and impact scores from the debate
3. Key evidence citations from each root cause document
4. Inter-dependency analysis: which root causes compound each other?
5. Assignment: root cause → solution task mapping (T02.01–T02.05)

**Checkpoint**: CP-P1-END — verify all outputs exist.

---

## Phase 2: Solution Proposals

### T02.01 — Solution: Invocation Wiring Fix

**Status**: pending
**Depends On**: T01.06
**Agent**: self-review
**Skill**: /sc:reflect
**Output**: `solutions/solution-01-invocation-wiring.md`

**Description**:
Propose a solution for root cause #1 (invocation wiring gap). Use `/sc:reflect` to validate the proposal against the codebase.

**Approach**:
1. Read `diagnostics/ranked-root-causes.md` for the final assessment of root cause #1
2. Design a mechanism for skill-to-skill invocation (or a workaround)
3. Options to consider:
   - A: Skill tool available within skill execution → just document the correct invocation
   - B: File-based protocol → skill writes invocation request to file, orchestrator picks it up
   - C: Task agent wrapper → skill spawns a Task agent that invokes the target skill
   - D: Inline embedding → embed the adversarial protocol directly in sc:roadmap's SKILL.md
4. Evaluate each option against feasibility, blast radius, and architectural coherence
5. Use `/sc:reflect` to validate that the chosen option works with the existing codebase

**Output Format**:
- Problem summary (from ranked root causes)
- Proposed solution with implementation details
- Files to modify (with specific line ranges)
- Blast radius assessment
- Confidence score (0.0-1.0)

---

### T02.02 — Solution: Spec-Execution Gap Fix

**Status**: pending
**Depends On**: T01.06
**Agent**: self-review
**Skill**: /sc:reflect
**Output**: `solutions/solution-02-spec-execution-gap.md`

**Description**:
Propose a solution for root cause #2 (specification-execution gap). Use `/sc:reflect` to validate.

**Approach**:
1. Read `diagnostics/ranked-root-causes.md` for the final assessment of root cause #2
2. Design more precise behavioral instructions for Wave 2 step 3
3. Options to consider:
   - A: Explicit tool-call syntax in SKILL.md (e.g., "Use the Skill tool with skill='sc:adversarial' and args='...'")
   - B: Pseudo-code with exact parameter mapping
   - C: Decision tree with fallback paths if primary invocation fails
   - D: Separate the "invoke adversarial" step into its own sub-wave with explicit entry/exit criteria
4. Compare with Wave 4's instruction style (which works) to identify the minimum specificity needed
5. Use `/sc:reflect` to validate the proposed instructions would be unambiguous

**Output Format**: Same as T02.01.

---

### T02.03 — Solution: Agent Dispatch Fix

**Status**: pending
**Depends On**: T01.06
**Agent**: system-architect
**Skill**: /sc:design
**Output**: `solutions/solution-03-agent-dispatch.md`

**Description**:
Design a fix for root cause #3 (agent dispatch mechanism). Use `/sc:design` to produce a specification.

**Approach**:
1. Read `diagnostics/ranked-root-causes.md` for the final assessment of root cause #3
2. Design the correct agent dispatch chain: sc:roadmap → sc:adversarial → debate-orchestrator
3. Options to consider:
   - A: Register debate-orchestrator as the handler for sc:adversarial skill invocations
   - B: Make sc:adversarial SKILL.md explicitly specify "spawn debate-orchestrator via Task tool"
   - C: Add agent routing metadata to skill definitions
   - D: Modify the agent selection heuristic to prefer debate-orchestrator for adversarial/debate contexts
4. Use `/sc:design` to produce a system architecture specification for the dispatch chain

**Output Format**: Same as T02.01 + system design diagram.

---

### T02.04 — Solution: Return Contract Fix

**Status**: pending
**Depends On**: T01.06
**Agent**: system-architect
**Skill**: /sc:design
**Output**: `solutions/solution-04-return-contract.md`

**Description**:
Design a fix for root cause #4 (return contract data flow). Use `/sc:design` to produce a specification.

**Approach**:
1. Read `diagnostics/ranked-root-causes.md` for the final assessment of root cause #4
2. Design a reliable inter-skill data flow mechanism
3. Options to consider:
   - A: File-based contract — adversarial writes `return-contract.json` to output dir, caller reads it
   - B: Structured file format — adversarial writes a YAML frontmatter block that caller can parse
   - C: Task agent result parsing — have the calling skill parse Task agent results for contract fields
   - D: Convention-based — define naming conventions so caller knows where to find outputs
4. Use `/sc:design` to produce a data flow specification

**Output Format**: Same as T02.01 + data flow diagram.

---

### T02.05 — Solution: Claude Behavioral Mitigation

**Status**: pending
**Depends On**: T01.06
**Agent**: general-purpose
**Skill**: (raw analysis — no skill invocation)
**Output**: `solutions/solution-05-claude-behavior.md`

**Description**:
Propose mitigations for root cause #5 (Claude behavioral interpretation). No skill invocation — raw analysis.

**Approach**:
1. Read `diagnostics/ranked-root-causes.md` for the final assessment of root cause #5
2. If Claude's behavior was a rational fallback, design guardrails to prevent it:
   - A: Explicit "DO NOT spawn Task agents directly" prohibition in SKILL.md
   - B: Pre-flight check that verifies the adversarial skill is reachable before Wave 2
   - C: Structured error emission if skill invocation fails (instead of silent fallback)
   - D: Checklist-style instructions with verification steps after each Wave 2 sub-step
3. If Claude's behavior was irrational, identify what instruction patterns prevent this class of error
4. Consider: is the fix "make the instructions clearer" (T02.02) sufficient, or do we need behavioral guardrails too?

**Output Format**: Same as T02.01.

**Checkpoint**: CP-P2-END — verify all 5 solution files exist and reference their assigned root cause.

---

## Phase 3: Solution Debate

### T03.01 — Debate: Invocation Wiring Fix

**Status**: pending
**Depends On**: T02.01, T02.02, T02.03, T02.04, T02.05
**Agent**: debate-orchestrator (via /sc:adversarial)
**Skill**: /sc:adversarial
**Output**: `debates/debate-01-invocation-wiring/` (directory with adversarial artifacts)

**Description**:
Invoke `/sc:adversarial` to debate the merits and flaws of Solution #1 (invocation wiring fix). The adversarial pipeline creates advocate agents for and against the solution.

**Invocation**:
```
/sc:adversarial --compare solutions/solution-01-invocation-wiring.md --depth standard --output debates/debate-01-invocation-wiring/
```

Note: Since this is a single-document debate (merits vs flaws), the adversarial pipeline operates in critique mode rather than comparison mode. Each advocate takes a position on the solution's viability.

**Scoring Dimensions** (applied by debate agents):
| Dimension | Weight | Question |
|-----------|--------|----------|
| Root cause coverage | 0.25 | Does this fix address the root cause completely? |
| Completeness | 0.20 | Does it handle edge cases and error paths? |
| Feasibility | 0.25 | Can it be implemented without major refactoring? |
| Blast radius | 0.15 | How many other skills/commands are affected? |
| Confidence | 0.15 | How confident are we this fix works? |

**Output**: Debate transcript, scoring matrix, fix_likelihood composite score.

---

### T03.02 — Debate: Spec-Execution Gap Fix

**Status**: pending
**Depends On**: T02.01, T02.02, T02.03, T02.04, T02.05
**Agent**: debate-orchestrator (via /sc:adversarial)
**Skill**: /sc:adversarial
**Output**: `debates/debate-02-spec-execution-gap/`

**Description**:
Same structure as T03.01 but for Solution #2 (spec-execution gap fix).

**Invocation**:
```
/sc:adversarial --compare solutions/solution-02-spec-execution-gap.md --depth standard --output debates/debate-02-spec-execution-gap/
```

**Scoring**: Same 5 dimensions as T03.01.

---

### T03.03 — Debate: Agent Dispatch Fix

**Status**: pending
**Depends On**: T02.01, T02.02, T02.03, T02.04, T02.05
**Agent**: debate-orchestrator (via /sc:adversarial)
**Skill**: /sc:adversarial
**Output**: `debates/debate-03-agent-dispatch/`

**Description**:
Same structure as T03.01 but for Solution #3 (agent dispatch fix).

**Invocation**:
```
/sc:adversarial --compare solutions/solution-03-agent-dispatch.md --depth standard --output debates/debate-03-agent-dispatch/
```

**Scoring**: Same 5 dimensions as T03.01.

---

### T03.04 — Debate: Return Contract Fix

**Status**: pending
**Depends On**: T02.01, T02.02, T02.03, T02.04, T02.05
**Agent**: debate-orchestrator (via /sc:adversarial)
**Skill**: /sc:adversarial
**Output**: `debates/debate-04-return-contract/`

**Description**:
Same structure as T03.01 but for Solution #4 (return contract fix).

**Invocation**:
```
/sc:adversarial --compare solutions/solution-04-return-contract.md --depth standard --output debates/debate-04-return-contract/
```

**Scoring**: Same 5 dimensions as T03.01.

---

### T03.05 — Debate: Claude Behavioral Fix

**Status**: pending
**Depends On**: T02.01, T02.02, T02.03, T02.04, T02.05
**Agent**: debate-orchestrator (via /sc:adversarial)
**Skill**: /sc:adversarial
**Output**: `debates/debate-05-claude-behavior/`

**Description**:
Same structure as T03.01 but for Solution #5 (Claude behavioral mitigation).

**Invocation**:
```
/sc:adversarial --compare solutions/solution-05-claude-behavior.md --depth standard --output debates/debate-05-claude-behavior/
```

**Scoring**: Same 5 dimensions as T03.01.

**Checkpoint**: CP-P3-END — verify all 5 debate directories exist with scoring artifacts.

---

## Phase 4: Ranking & Sprint Design

### T04.01 — Final Ranking & Sprint Specification

**Status**: pending
**Depends On**: T03.01, T03.02, T03.03, T03.04, T03.05
**Agent**: system-architect
**Skill**: /sc:spec-panel
**Output**: `sprint-spec.md`

**Description**:
Rank all problems and solutions, then design a release sprint for the top 3 problem-solution pairs.

**Step 1: Problem Ranking**:
Read `diagnostics/ranked-root-causes.md` and compute final problem scores:
```
problem_score = (likelihood * 0.6) + (impact * 0.4)
```
Produce a ranked list of all 5 root causes.

**Step 2: Solution Ranking**:
Read all 5 debate results from `debates/` and extract fix_likelihood scores. Compute:
```
solution_score = (fix_likelihood * 0.5) + (feasibility * 0.3) + (low_blast_radius * 0.2)
```
Produce a ranked list of all 5 solutions.

**Step 3: Problem-Solution Pairing**:
Create a matrix of problem_score × solution_score. Select the top 3 pairs by combined score:
```
combined = (problem_score * 0.5) + (solution_score * 0.5)
```

**Step 4: Sprint Specification**:
Invoke `/sc:spec-panel` on the top 3 problem-solution pairs to produce a release sprint with:
- Sprint goal
- 3 epics (one per problem-solution pair)
- Tasks within each epic
- Acceptance criteria per task
- Risk register
- Estimated effort
- Definition of Done

**Output**: `sprint-spec.md` in the release directory root.

**Checkpoint**: CP-P4-END — verify sprint-spec.md exists with all required sections.
