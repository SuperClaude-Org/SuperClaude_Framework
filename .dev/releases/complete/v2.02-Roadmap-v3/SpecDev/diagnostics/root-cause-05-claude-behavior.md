# Root Cause #5: Claude Behavioral Interpretation

## Summary

Claude's decision to spawn two system-architect Task agents and manually synthesize was a **rational but incomplete fallback** caused primarily by an infrastructure gap: the `Skill` tool is absent from the `allowed-tools` list in the roadmap command entry point, making the instruction "Invoke sc:adversarial" physically unimplementable within the skill execution context. Claude correctly identified the constraint and chose the best approximation available, but that approximation captured only variant generation and merge -- skipping the adversarial debate, scoring, and contradiction detection that constitute the pipeline's core value proposition.

## Evidence

### Available Tools in sc:roadmap Command

File: `/config/workspace/SuperClaude_Framework/.claude/commands/sc/roadmap.md`, line 4:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
```

**The `Skill` tool is NOT listed.** This means Claude cannot invoke another skill (sc:adversarial) from within the sc:roadmap skill execution context. The Claude Code platform restricts tool access to exactly the tools declared in the command's frontmatter.

Also confirmed in the SKILL.md header (line 4): identical tool list, no `Skill` tool.

### Wave 2 Instructions (Claude's Perspective)

File: `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-roadmap/SKILL.md`, line 137:

> If `--multi-roadmap`: parse agent specs [...]. Invoke sc:adversarial for multi-roadmap generation per `refs/adversarial-integration.md` "Multi-Roadmap Generation" invocation pattern. Handle return contract per `refs/adversarial-integration.md` "Return Contract Consumption" section. The adversarial output replaces template-based generation.

File: `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`, lines 104-126 show the invocation format:

```
sc:adversarial --source <spec-or-unified-spec> --generate roadmap --agents <expanded-agent-specs> --depth <roadmap-depth> --output <roadmap-output-dir> [--interactive]
```

**What Claude would interpret from these instructions:**

1. "I need to call sc:adversarial as a separate skill invocation."
2. "I do not have the Skill tool in my allowed-tools list."
3. "I cannot invoke sc:adversarial."
4. "The instructions are unimplementable as written."
5. "I need to approximate the intent using the tools I DO have."

This is a rational chain of reasoning. Claude cannot fabricate tool access it does not have.

### sc:adversarial Skill Existence

File: `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-adversarial/SKILL.md` exists and is fully defined (1747 lines). The skill IS installed. The problem is not availability but invocability from within sc:roadmap's execution context.

### Wave 0 Prerequisite Check

SKILL.md line 86 instructs:

> If `--specs` or `--multi-roadmap` flags present: verify `src/superclaude/skills/sc-adversarial/SKILL.md` exists. If not, abort.

This check would PASS (the file exists). But passing this check does not mean invocation is possible -- it only confirms the skill definition file is present on disk. There is no check for "can I actually invoke this skill with my available tools."

### Approximation Analysis

**What sc:adversarial's 5-step protocol does:**

| Step | Purpose | Claude's Approximation |
|------|---------|----------------------|
| Step 1: Diff Analysis | Structural diff, content diff, contradiction detection, unique contributions | **SKIPPED** |
| Step 2: Adversarial Debate | Steelman debate with advocate agents across 1-3 rounds | **SKIPPED** |
| Step 3: Hybrid Scoring | 50% quantitative (5 metrics) + 50% qualitative (25 criteria) with position-bias mitigation | **SKIPPED** |
| Step 4: Refactoring Plan | Evidence-based merge plan with rationale | **SKIPPED** |
| Step 5: Merge Execution | Methodical merge with provenance annotations | **PARTIALLY APPROXIMATED** via manual synthesis |

Claude's actual behavior: generate two competing variants via Task agents, then manually synthesize the best elements. This captures approximately:
- **Mode B variant generation** (T06.02): Two Task agents generating roadmap variants -- this maps directly to what sc:adversarial does in its variant generation phase
- **A simplified merge**: Manual synthesis approximates the merge step but without the structured evidence chain

The approximation preserves ~20% of the adversarial pipeline's functionality (variant generation + rough merge) while skipping ~80% (diff analysis, debate, scoring, refactoring plan, provenance tracking).

## Analysis

### Rational Fallback Assessment

**Verdict: The fallback was rational given constraints, but not optimal.**

Claude faced a genuine infrastructure constraint: the Skill tool is not in allowed-tools, so `sc:adversarial` cannot be invoked. Given this constraint, the decision space was:

1. **Abort entirely** -- refuse to generate any roadmap because adversarial cannot run. This would be correct-but-unhelpful.
2. **Skip adversarial, proceed with standard generation** -- ignore the `--multi-roadmap` flag. This would violate the user's explicit request.
3. **Approximate adversarial using available tools** -- spawn Task agents for variant generation, then synthesize. This is what Claude chose.

Option 3 is the most rational choice. It honors the user's intent (get multiple perspectives) while working within real constraints.

However, Claude could have done a **better approximation**:
- Spawn a third Task agent to perform diff analysis between the two variants (approximating Step 1)
- Spawn a fourth Task agent to score the variants against the source spec (approximating Step 3)
- Use the scoring results to guide the merge (approximating Step 4)

All of these are achievable with the `Task` tool that Claude DID have access to. The 5-step protocol is described in the sc:adversarial SKILL.md and in the adversarial-integration.md reference -- Claude could have read these and approximated the steps individually.

### Instruction Clarity Assessment

**Verdict: Instructions are ambiguous about invocation mechanism.**

The instructions say "Invoke sc:adversarial" but never specify HOW. There are three possible interpretations:

1. **Use the Skill tool** -- but it is not in allowed-tools
2. **Read the SKILL.md and execute its instructions inline** -- possible but not stated
3. **Call it as a subprocess** -- not a real capability

The instructions assume a skill-to-skill invocation mechanism that does not exist in the current framework. This is a design gap, not a documentation oversight -- the adversarial integration reference document is thorough about WHAT to invoke and what return contract to expect, but silent about the invocation mechanism itself.

The Wave 0 prerequisite check (verify SKILL.md exists) reinforces the assumption that file-existence equals invocability, which is false.

### Quality Impact

**The manual synthesis produced a lower-quality output than the adversarial pipeline would have.**

The adversarial pipeline's value comes from:
1. **Contradiction detection** -- catching hallucinations and inconsistencies between variants (30%+ factual error reduction per the skill's claims)
2. **Steelman debate** -- forcing each perspective to engage with opposing views at their strongest
3. **Evidence-based scoring** -- 25-criterion rubric with Claim-Evidence-Verdict protocol to prevent hallucinated quality assessments
4. **Position-bias mitigation** -- dual-pass evaluation to eliminate systematic ordering effects
5. **Provenance tracking** -- knowing which variant contributed each section

Manual synthesis preserves none of these. The output is a single Claude instance's judgment about "best elements" without structured adversarial pressure, formal scoring, or contradiction scanning. This is functionally equivalent to asking one person to read two documents and write a summary -- the entire multi-agent adversarial advantage is lost.

### Compound Causation

This root cause does NOT stand alone. It depends on a chain:

1. **T01.01 (Infrastructure)**: The Skill tool is missing from allowed-tools. This is the PRIMARY cause. If Skill were in allowed-tools, Claude could invoke sc:adversarial directly and this root cause would not exist.

2. **T01.02 (Instruction Ambiguity)**: The instructions say "invoke" without specifying mechanism. This is a CONTRIBUTING cause. Even without the Skill tool, clearer instructions ("read sc-adversarial/SKILL.md and execute its 5-step protocol inline using Task agents") could have guided Claude to a better approximation.

3. **T01.03 (Agent Availability)**: The debate-orchestrator agent referenced in sc:adversarial may not be available as a pre-configured agent definition. Even if Claude tried to approximate inline, it would need to construct these agent prompts from scratch.

4. **T01.04 (Return Contract)**: Without the pipeline running, there is no structured return contract to consume. Claude cannot populate the adversarial frontmatter block (convergence_score, base_variant, artifacts_dir) because these values are never computed.

The failure is best understood as a **cascade**: T01.01 (no Skill tool) prevents invocation, T01.02 (ambiguous instructions) prevents optimal fallback, which together produce the observed behavior of simplified Task-agent approximation.

## Likelihood Score: 0.85/1.0

High likelihood that this root cause explains the failure. The evidence chain is clear: allowed-tools lacks Skill, instructions say "invoke," Claude cannot invoke, Claude falls back to approximation. The only uncertainty is whether Claude's training or context window might have led to the same behavior even WITH the Skill tool (e.g., if Claude is unfamiliar with the Skill tool's usage pattern).

## Impact Score: 0.70/1.0

High impact on output quality. The adversarial pipeline's 5-step protocol is designed to produce 10-15% accuracy gains and 30%+ factual error reduction. Manual synthesis forfeits all of this. However, the impact is bounded: the roadmap variants themselves were still generated (variant generation worked), so the output is not entirely un-informed by multiple perspectives. The loss is in the structured validation and evidence-based merging, not in perspective diversity.

## Recommendation

### Immediate Fix (T01.01 Resolution)

Add `Skill` to the allowed-tools list in both files:

1. `/config/workspace/SuperClaude_Framework/.claude/commands/sc/roadmap.md` line 4:
   ```yaml
   allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
   ```

2. `/config/workspace/SuperClaude_Framework/src/superclaude/skills/sc-roadmap/SKILL.md` line 4:
   ```yaml
   allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
   ```

### Instruction Clarity Fix (T01.02 Resolution)

Add an explicit invocation mechanism to Wave 2 instructions (SKILL.md line 137). Replace "Invoke sc:adversarial" with:

> Use the Skill tool to invoke sc:adversarial with the following arguments: `--source <spec> --generate roadmap --agents <expanded-agent-specs> --depth <depth> --output <dir>`. If the Skill tool is unavailable, read `src/superclaude/skills/sc-adversarial/SKILL.md` and execute its 5-step protocol inline using Task agents for delegation.

### Fallback Protocol (Defensive)

Add a fallback instruction block to Wave 2 for when skill invocation fails:

> **Fallback if sc:adversarial cannot be invoked**: Execute the 5-step adversarial protocol inline:
> 1. Generate variants using Task agents (one per --agents spec)
> 2. Spawn a Task agent to perform diff analysis between variants
> 3. Spawn Task agents as advocates for structured debate (1-3 rounds per --depth)
> 4. Spawn a Task agent for hybrid scoring (quantitative + qualitative)
> 5. Spawn a merge-executor Task agent with the refactoring plan
> Document all intermediate artifacts in `<output>/adversarial/`

### Behavioral Guardrail

Add a Wave 0 validation step:

> If `--multi-roadmap` and Skill tool is NOT in available tools: WARN user that adversarial pipeline will run in degraded inline mode. Log: "Skill tool not available; sc:adversarial will be approximated using Task agents."

This prevents silent degradation -- the user knows the full pipeline is not running.
