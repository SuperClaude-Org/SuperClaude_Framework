# Root Cause #2: Specification-Execution Gap

## Summary

Wave 2's instruction to "Invoke sc:adversarial" uses an undefined verb ("Invoke") with pseudo-CLI syntax that does not map to any specific Claude Code tool call, while Wave 4's "Dispatch ... agent" instructions map clearly to Task agent spawning. This ambiguity creates a gap where Claude can reasonably interpret Wave 2 as "approximate the adversarial pipeline using Task agents" rather than "call the Skill tool with skill='sc:adversarial'."

## Evidence

### Wave 2 Instructions (verbatim)

From `src/superclaude/skills/sc-roadmap/SKILL.md`, lines 130-143:

```markdown
### Wave 2: Planning & Template Selection

**Refs Loaded**: Read `refs/templates.md` for template discovery and milestone structure. If `--multi-roadmap`, also read `refs/adversarial-integration.md`.

**Behavioral Instructions**:
1. Run 4-tier template discovery from `refs/templates.md`: local → user → plugin [future: v5.0] → inline generation
2. Score template compatibility using the algorithm from `refs/scoring.md`. If `--interactive`: display compatibility scores for all candidate templates, prompt user to confirm or select. If not `--interactive`: use highest-scoring template silently
3. If `--multi-roadmap`: parse agent specs using the parsing algorithm from `refs/adversarial-integration.md` "Agent Specification Parsing" section. Expand model-only agents with the primary persona from Wave 1B. If agent count ≥5, orchestrator is added automatically. Invoke sc:adversarial for multi-roadmap generation per `refs/adversarial-integration.md` "Multi-Roadmap Generation" invocation pattern. Handle return contract per `refs/adversarial-integration.md` "Return Contract Consumption" section. The adversarial output replaces template-based generation.
4. Otherwise: create milestone structure based on complexity class and domain distribution using the milestone count formula, domain mapping, and priority assignment rules from `refs/templates.md`
5. Map dependencies between milestones using the dependency mapping rules from `refs/templates.md`. Validate the dependency graph is acyclic (DAG). If circular dependency detected, abort with `"Circular dependency detected in milestone plan: M<X> → M<Y> → ... → M<X>. Review milestone dependencies."`
6. Compute effort estimates for each milestone using the effort estimation algorithm from `refs/templates.md`
7. Record template selection decision in Decision Summary (template name or "inline", compatibility scores, rationale)
```

The critical sentence in step 3 is: **"Invoke sc:adversarial for multi-roadmap generation per `refs/adversarial-integration.md` "Multi-Roadmap Generation" invocation pattern."**

### Wave 4 Instructions (verbatim, for comparison)

From `src/superclaude/skills/sc-roadmap/SKILL.md`, lines 168-184:

```markdown
### Wave 4: Validation (Multi-Agent)

**Skip condition**: If `--dry-run`, this wave is skipped entirely. If `--no-validate`, skip per step 8 below.

**Refs Loaded**: Read `refs/validation.md` for agent prompts and scoring thresholds.

**Behavioral Instructions**:
1. Dispatch quality-engineer agent using the prompt from `refs/validation.md`: completeness, consistency, traceability checks. Additionally validates test-strategy.md against interleave ratio, milestone references, and stop-and-fix thresholds.
2. Dispatch self-review agent using the 4-question protocol from `refs/validation.md`
3. Both agents run in **parallel** (independent read-only validators)
4. Aggregate scores using the formula from `refs/validation.md` "Score Aggregation" section: quality-engineer (0.55) + self-review (0.45). Apply thresholds from `refs/validation.md` "Decision Thresholds" section: PASS (>=85%) | REVISE (70-84%) | REJECT (<70%)
5. If adversarial mode was used: missing adversarial artifacts → REJECT; missing convergence score → REVISE
6. Write validation score to roadmap.md frontmatter
7. **REVISE loop** (per FR-017): If 70-84%, follow the REVISE loop protocol from `refs/validation.md` "REVISE Loop" section: collect improvement recommendations from both agents, re-run Wave 3 → Wave 4 with recommendations as input. Max 2 iterations. If still REVISE after iteration 2: set `validation_status: PASS_WITH_WARNINGS`
8. If `--no-validate`: skip entirely per `refs/validation.md` "No-Validate Behavior" section. Set `validation_status: SKIPPED` and `validation_score: 0.0`. No agents are dispatched. Emit: `"Wave 4 skipped: --no-validate flag set."`
```

### Adversarial Integration Ref (invocation pattern)

From `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`, lines 104-126 (Multi-Roadmap Generation section):

```markdown
### Multi-Roadmap Generation (Wave 2)

**Invocation format**:

sc:adversarial --source <spec-or-unified-spec> --generate roadmap --agents <expanded-agent-specs> --depth <roadmap-depth> --output <roadmap-output-dir> [--interactive]

**Parameter mapping**:
- `<spec-or-unified-spec>`: Single spec file path, or unified spec from Wave 1A (if combined mode)
- `--generate roadmap`: Fixed value — tells sc:adversarial what artifact type to generate
- `<expanded-agent-specs>`: Agent specs after expansion (model-only agents filled with primary persona)
- `<roadmap-depth>`: Value of sc:roadmap's `--depth` flag
- `<roadmap-output-dir>`: sc:roadmap's resolved output directory
- `--interactive`: Present only when sc:roadmap's `--interactive` flag is set

**Example invocations**:

# 3 agents, standard depth (after persona expansion to "security")
sc:adversarial --source spec.md --generate roadmap --agents opus:security,sonnet:security,gpt52:security --depth standard --output .dev/releases/current/auth-system/

# 5+ agents triggers orchestrator (orchestrator added automatically by sc:adversarial)
sc:adversarial --source spec.md --generate roadmap --agents opus:architect,sonnet:security,gpt52:backend,haiku:frontend,gemini:performance --depth deep --output .dev/releases/current/platform/ --interactive
```

## Analysis

### Ambiguity Points

1. **Undefined verb "Invoke"**: The SKILL.md uses "Invoke sc:adversarial" but never defines what "invoke" means in tool-call terms. Is it a `Skill` tool call? A `Task` agent spawn? A `Bash` command? The word "invoke" has no specific mapping to any Claude Code tool.

2. **Pseudo-CLI syntax without tool-call mapping**: The `refs/adversarial-integration.md` presents invocation patterns using CLI-style syntax (`sc:adversarial --source <spec> --generate roadmap --agents ...`). This looks like a command-line invocation, but sc:adversarial is a Skill, not a CLI tool. The document never states: "Use the Skill tool with skill='sc:adversarial' and args='--source ... --generate ...'"

3. **Five sub-operations compressed into one step**: Wave 2 step 3 packs five distinct operations into a single sentence: (a) parse agent specs, (b) expand model-only agents, (c) add orchestrator if needed, (d) invoke sc:adversarial, (e) handle return contract. This density increases the probability of any single sub-operation being skipped or misinterpreted.

4. **Cross-reference indirection**: Step 3 references `refs/adversarial-integration.md` three times for three different sections ("Agent Specification Parsing", "Multi-Roadmap Generation", "Return Contract Consumption"). Claude must load, parse, and correlate material across these sections while executing a multi-step procedure, increasing cognitive load and error probability.

5. **No explicit tool name**: Neither SKILL.md nor `refs/adversarial-integration.md` contains the literal string "Skill tool" or specifies the tool_name parameter. The SKILL.md frontmatter declares `allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task` -- notably, `Skill` is not in this list, which could signal to Claude that skill invocation is not an available mechanism.

6. **"The adversarial output replaces template-based generation"**: This trailing clause describes the EFFECT but not the MECHANISM. It tells Claude what should happen after invocation, not how to perform the invocation.

### Specificity Comparison (Wave 2 vs Wave 4)

| Dimension | Wave 2 (Multi-Roadmap) | Wave 4 (Validation) |
|-----------|------------------------|---------------------|
| **Verb used** | "Invoke" (undefined) | "Dispatch" (maps to Task spawning) |
| **Target** | "sc:adversarial" (a Skill) | "quality-engineer agent" / "self-review agent" (Task agents) |
| **Tool implied** | Unclear -- Skill tool? Task? Bash? | Task tool (agent dispatch is a known Task pattern) |
| **Invocation detail** | "per refs/adversarial-integration.md" (deferred to cross-reference) | "using the prompt from refs/validation.md" (direct inline) |
| **Parallelism instruction** | Not specified | "Both agents run in **parallel**" (explicit) |
| **Operations per step** | 5 sub-operations in one sentence | 1 operation per step (steps 1-3) |
| **Error handling** | "Handle return contract per refs/..." (deferred) | Inline thresholds: PASS/REVISE/REJECT with percentages |
| **Determinism** | Low -- requires interpretation of cross-references | High -- each step is self-contained and actionable |

Wave 4 uses a pattern Claude knows well: "Dispatch X agent using Y prompt" maps directly to spawning a Task agent with a specific system prompt. Each step does exactly one thing. Error handling is inline.

Wave 2 uses a pattern Claude has never been explicitly taught: "Invoke sc:adversarial" does not map to any documented tool-call pattern. The step does five things. Error handling is deferred to a cross-reference.

### Reasonable Misinterpretation

**Yes, Claude could reasonably interpret Wave 2's instructions as "spawn Task agents directly to approximate the adversarial pipeline."** Here is the reasoning chain Claude would follow:

1. Claude reads "Invoke sc:adversarial for multi-roadmap generation" but finds no explicit tool-call instruction.
2. Claude sees that the `allowed-tools` in SKILL.md frontmatter lists `Task` but not `Skill`.
3. Claude knows from Wave 4 that "Dispatch agent" means spawning Task agents.
4. Claude generalizes: "multi-roadmap generation requires multiple agents debating" can be approximated by spawning Task agents with different persona prompts.
5. Claude spawns Task agents directly (opus agent, haiku agent) to generate competing roadmap variants, then merges them inline -- effectively reimplementing a simplified version of sc:adversarial's pipeline without actually invoking sc:adversarial.

This interpretation is internally consistent with Claude's training and the document's own patterns. Wave 4 teaches Claude that multi-agent work = Task agents. Wave 2 asks for multi-agent work but does not explicitly redirect to a different mechanism (Skill tool).

**Contributing factor**: The `refs/adversarial-integration.md` invocation patterns use pseudo-CLI syntax (`sc:adversarial --source ...`) that looks like a user-facing slash command, not a tool call. Claude may interpret these as "this is how a user would invoke it" rather than "this is what I should invoke programmatically."

## Likelihood Score: 0.85/1.0

**Justification**: The specification-execution gap is well-documented and structural. The verb "Invoke" is genuinely undefined in tool-call terms. The `allowed-tools` list excludes `Skill`. The cross-reference indirection and step density compound the ambiguity. Wave 4 demonstrates that Claude CAN follow multi-agent instructions when they are specific (verb="Dispatch", target="agent", tool=Task), proving the issue is specification quality, not Claude capability. The only reason this is not 1.0 is that a sufficiently context-aware Claude session might recognize `sc:adversarial` as a skill name and infer the Skill tool call -- but this requires inference that the spec does not support.

## Impact Score: 0.90/1.0

**Justification**: This ambiguity directly explains the observed failure mode. If Claude interprets "Invoke sc:adversarial" as "spawn Task agents to approximate the pipeline," the result is:
- No actual sc:adversarial skill invocation (the core failure)
- Task agents generating roadmap variants without structured adversarial debate (reduced quality)
- No return contract to consume (missing convergence scores, artifacts directory)
- No proper frontmatter population (missing adversarial block fields)

The gap between "invoke a Skill" and "spawn Task agents" is the exact gap between the intended behavior and the observed behavior. This is the primary specification deficiency that would cause the failure.

## Recommendation

### Immediate Fix: Make Wave 2 step 3 deterministic

Replace the current compressed step 3 with explicit, per-step instructions matching Wave 4's specificity pattern:

```markdown
3a. If `--multi-roadmap`: parse agent specs using the parsing algorithm from
    `refs/adversarial-integration.md` "Agent Specification Parsing" section.
    Expand model-only agents with the primary persona from Wave 1B.
    If agent count >= 5, orchestrator is added automatically.

3b. **Invoke sc:adversarial using the Skill tool**: Call the Skill tool with
    `skill: "sc:adversarial"` and `args` constructed per the invocation format
    in `refs/adversarial-integration.md` "Multi-Roadmap Generation" section:
    `--source <spec-path> --generate roadmap --agents <expanded-specs>
    --depth <depth> --output <output-dir> [--interactive]`

3c. Consume the return contract from sc:adversarial per
    `refs/adversarial-integration.md` "Return Contract Consumption" section:
    - status == "success" -> use merged_output_path, proceed
    - status == "partial" + convergence >= 60% -> proceed with warning
    - status == "partial" + convergence < 60% -> abort (or prompt if --interactive)
    - status == "failed" -> abort roadmap generation

3d. The adversarial output replaces template-based generation.
    Skip steps 4-6 (milestone structure is provided by sc:adversarial output).
```

### Structural Fix: Standardize invocation vocabulary across all waves

Define a glossary in the SKILL.md preamble:

```markdown
**Invocation vocabulary**:
- "Dispatch agent" = Spawn a Task agent (Task tool) with specified prompt
- "Invoke skill" = Call the Skill tool with the named skill and arguments
- "Execute step" = Perform inline within current context (no tool delegation)
```

### Cross-Reference Fix: Inline critical invocation syntax

The `refs/adversarial-integration.md` invocation patterns should include explicit tool-call syntax alongside the pseudo-CLI format:

```markdown
**Tool call**:
Skill tool: skill="sc:adversarial", args="--source spec.md --generate roadmap --agents opus:security,sonnet:security --depth standard --output .dev/releases/current/auth-system/"
```

### Allowed-Tools Fix: Add Skill to allowed-tools

The SKILL.md frontmatter `allowed-tools` list should include `Skill` if the skill is expected to invoke other skills:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

---

*Root cause analysis performed 2026-02-22. Evidence sourced from SKILL.md (lines 130-184), refs/adversarial-integration.md (lines 104-126), and sc:adversarial SKILL.md frontmatter.*
