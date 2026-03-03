# Ranked Root Causes -- sc:roadmap Adversarial Failure

## Executive Summary

The `--multi-roadmap --agents opus,haiku` feature failed because the sc:roadmap skill instructs Claude to "Invoke sc:adversarial" but provides no executable mechanism to do so: the `Skill` tool is absent from `allowed-tools`, the verb "Invoke" has no defined tool-call mapping, and no skill-to-skill invocation precedent exists in the framework. Claude rationally fell back to spawning generic Task agents (system-architect) for a simplified variant-generation-and-merge, forfeiting the adversarial pipeline's 5-step structured debate, scoring, and contradiction detection. The return contract was never produced because the pipeline never ran.

## Ranked Root Causes

### Rank 1: Invocation Wiring Gap (RC1)

- **Likelihood**: 0.95 (self-reported) -> 0.90 (validated)
- **Impact**: 1.00 (self-reported) -> 0.90 (validated)
- **Combined Score**: 0.90
- **Key Evidence**: The `Skill` tool is absent from `allowed-tools` in both `roadmap.md` (command) and `SKILL.md` (skill). The Skill tool description says "Do not invoke a skill that is already running," confirming skill-to-skill chaining was never designed. Zero precedents for cross-skill invocation exist anywhere in the codebase.
- **Validation Notes**: Likelihood held up well -- the evidence chain is concrete and verifiable, not inferential. However, impact was reduced from 1.0 to 0.9 because this root cause explains WHY invocation failed but does not alone account for the specific degraded behavior (wrong agent selection, missing return data). Fixing this alone would not resolve the downstream issues (RC3, RC4) that would surface once invocation is attempted. The self-reported 1.0 impact contains slight confirmation bias -- treating the most fundamental cause as the complete explanation.

### Rank 2: Claude Behavioral Interpretation (RC5)

- **Likelihood**: 0.85 (self-reported) -> 0.85 (validated)
- **Impact**: 0.70 (self-reported) -> 0.70 (validated)
- **Combined Score**: 0.79
- **Key Evidence**: Claude's fallback decision chain is reconstructable: (1) instruction says "invoke," (2) Skill tool unavailable, (3) approximate using Task agents, (4) spawn system-architect agents for variant generation, (5) manually synthesize. The approximation preserved ~20% of the adversarial pipeline's functionality (variant generation + rough merge) while skipping 80% (diff analysis, debate, scoring, refactoring plan, provenance).
- **Validation Notes**: Scores held up. This is the most honestly self-assessed of the five reports. It explicitly acknowledges compound causation and dependency on other root causes. The 0.70 impact correctly bounds the damage -- variants were still generated, so the output was not entirely uninformed. The report's recommendation for a fallback protocol is the most pragmatically valuable across all five analyses.

### Rank 3: Specification-Execution Gap (RC2)

- **Likelihood**: 0.85 (self-reported) -> 0.75 (validated)
- **Impact**: 0.90 (self-reported) -> 0.80 (validated)
- **Combined Score**: 0.77
- **Key Evidence**: The verb "Invoke" is undefined in tool-call terms. Wave 4 uses "Dispatch" (maps to Task agents) while Wave 2 uses "Invoke" (maps to nothing). The `allowed-tools` list excludes `Skill`. Five sub-operations are compressed into a single step, and critical invocation details are deferred to cross-references rather than inlined.
- **Validation Notes**: Likelihood reduced because this root cause overlaps substantially with RC1. The specification ambiguity is real, but it is a CONTRIBUTING FACTOR to the wiring gap, not an independent cause. If the Skill tool were in allowed-tools AND the instructions were ambiguous, Claude would likely still attempt invocation (it would recognize `sc:adversarial` as a skill name). The ambiguity matters most in the absence of the tool -- making this a compounding factor, not a primary cause. Impact reduced because the Wave 2 vs Wave 4 comparison, while insightful, overstates the specification's causal role relative to the infrastructure gap. The 0.90 self-reported impact contains moderate score inflation by treating the specification as the blocking factor when the infrastructure gap (RC1) is the actual blocker.

### Rank 4: Return Contract Data Flow (RC4)

- **Likelihood**: 0.85 (self-reported) -> 0.75 (validated)
- **Impact**: 0.80 (self-reported) -> 0.75 (validated)
- **Combined Score**: 0.75
- **Key Evidence**: The return contract specifies 6 structured fields (status, convergence_score, merged_output_path, artifacts_dir, unresolved_conflicts, base_variant) but defines no transport mechanism. The only inter-agent data flow precedent (sc:cleanup-audit) uses explicit file-based fan-out/fan-in, which the adversarial return contract does not adopt. Task agents return unstructured text, not typed structs.
- **Validation Notes**: Scores slightly reduced. The analysis is technically sound, but this is a TERTIARY cause -- it only matters if RC1 and RC2 are resolved and invocation is actually attempted. As an independent root cause, it never had a chance to manifest in the observed failure. The 0.85 self-reported likelihood treats a latent defect as an active cause. The honest self-assessment ("this alone does not explain the full failure") partially compensates for this inflation. The report's recommendation (file-based return-contract.yaml) is the correct fix regardless of ranking.

### Rank 5: Agent Dispatch Mechanism (RC3)

- **Likelihood**: 0.95 (self-reported) -> 0.70 (validated)
- **Impact**: 0.90 (self-reported) -> 0.75 (validated)
- **Combined Score**: 0.72
- **Key Evidence**: No programmatic binding exists between `sc:adversarial` and `debate-orchestrator`. The Task tool has no `subagent_type` parameter. Agent `.md` files are passive documentation never programmatically loaded. The stale agents README lists 3 of 30 agents.
- **Validation Notes**: Both scores significantly reduced. The 0.95 self-reported likelihood is the most inflated across all five reports. The report's core claim -- that system-architect was selected due to keyword affinity instead of debate-orchestrator -- is plausible BUT is a consequence of RC1/RC5, not an independent cause. System-architect was selected because Claude was operating OUTSIDE sc:adversarial (it never invoked it), using its general heuristics. The agent dispatch mechanism within sc:adversarial was never tested. If sc:adversarial had been properly invoked, its SKILL.md does reference debate-orchestrator in delegation notes, which would provide Claude with the context to select it. The 0.90 impact is inflated because the report claims cascading effects (no 5-step protocol, no scoring, no merge coordination) that are actually consequences of RC1 (no invocation), not RC3 (wrong agent). The evidence about `subagent_type: "general-purpose"` in dispatch configs is genuinely concerning but is a latent defect, not an active cause of the observed failure.

## Dependency Chain Analysis

The five root causes form a clear causal cascade, not five independent failures:

```
RC1 (No invocation mechanism) ─────┐
                                    ├──> RC5 (Claude falls back to approximation)
RC2 (Ambiguous spec language) ──────┘         │
                                              ├──> RC3 (Wrong agent selected for approximation)
                                              │
                                              └──> RC4 (No return contract produced)
```

**Primary chain**: RC1 blocks invocation entirely. RC2 compounds this by providing no fallback guidance. Together they trigger RC5 (Claude's rational but degraded fallback). RC5's fallback behavior exposes RC3 (agent dispatch defaults to system-architect) and RC4 (no structured return data).

**Key insight**: RC3 and RC4 are LATENT DEFECTS that would surface even if RC1 and RC2 were fixed, but they were not the ACTIVE CAUSES of the observed failure. They should be fixed proactively but should not be confused with the primary failure mechanism.

**Compound amplification**: RC1 + RC2 together are worse than either alone. If the Skill tool were available but the spec were ambiguous, Claude would likely still attempt invocation (recognizing `sc:adversarial` as a skill name). If the spec were explicit but the Skill tool were missing, Claude would at least have clear guidance for a structured fallback. Both failing simultaneously left Claude with neither mechanism nor guidance.

## Overlap Assessment

**High Overlap: RC1 + RC2** -- These describe the same problem from different angles. RC1 focuses on the infrastructure gap (Skill tool missing from allowed-tools, no skill-to-skill mechanism). RC2 focuses on the specification gap (undefined verb, ambiguous syntax, compressed steps). They are complementary analyses of why "Invoke sc:adversarial" does not work. A single fix (add Skill to allowed-tools AND rewrite the instruction) addresses both.

**High Overlap: RC3 + RC5** -- RC5's "system-architect selection" analysis subsumes RC3's "agent dispatch" analysis. RC3 provides deeper technical detail about the dispatch mechanism (or lack thereof), but RC5 correctly identifies RC3 as a downstream consequence. The system-architect selection described in RC3 is the specific manifestation of the general fallback behavior described in RC5.

**Low Overlap: RC4** -- The return contract analysis is genuinely independent. It identifies a structural deficiency (no data transport protocol) that exists regardless of whether invocation works. Even a perfectly invoked sc:adversarial would face the return contract problem. This is the most architecturally significant standalone finding.

**Redundancy assessment**: RC1 + RC2 could be merged into a single root cause ("Invocation Mechanism Gap"). RC3 + RC5 could be merged into a single root cause ("Degraded Fallback Behavior"). RC4 stands alone. This reduces 5 root causes to 3 distinct problems.

## Minimal Fix Set

Three fixes address all five root causes:

### Fix 1: Add `Skill` to allowed-tools (addresses RC1, RC5)

In both `roadmap.md` (command) and `SKILL.md` (skill), add `Skill` to the `allowed-tools` list:

```yaml
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task, Skill
```

This removes the infrastructure blocker. Claude can invoke sc:adversarial via the Skill tool.

**Resolves**: RC1 (primary), RC5 (primary cause removed)

### Fix 2: Rewrite Wave 2 step 3 with explicit tool-call syntax (addresses RC2, RC3, RC5)

Replace the compressed natural-language step with decomposed, Wave-4-style instructions:

- Define invocation vocabulary glossary ("Invoke skill" = Skill tool call, "Dispatch agent" = Task tool call)
- Decompose step 3 into sub-steps (3a: parse specs, 3b: invoke via Skill tool with explicit syntax, 3c: consume return contract, 3d: replace template generation)
- Add explicit fallback protocol: if Skill tool unavailable, execute 5-step protocol inline using Task agents with debate-orchestrator behavioral instructions
- Add agent bootstrap instruction: before delegation, read `src/superclaude/agents/debate-orchestrator.md` and embed in Task prompts

**Resolves**: RC2 (primary), RC3 (agent dispatch guidance), RC5 (fallback protocol)

### Fix 3: Define file-based return-contract.yaml convention (addresses RC4, RC1 partially)

Add to sc:adversarial SKILL.md a mandatory final step: write `<output-dir>/adversarial/return-contract.yaml` with the 6 contract fields. Add corresponding read instructions to `refs/adversarial-integration.md` for the consuming skill.

```yaml
# Written by sc:adversarial as final step
status: success
merged_output_path: ./adversarial/merged-roadmap.md
convergence_score: 0.85
artifacts_dir: ./adversarial/
unresolved_conflicts: 2
base_variant: opus:security
```

**Resolves**: RC4 (primary), RC1 (return channel concern)

### Fix coverage matrix

| Root Cause | Fix 1 | Fix 2 | Fix 3 |
|-----------|-------|-------|-------|
| RC1 Invocation Wiring | PRIMARY | -- | partial |
| RC2 Spec-Execution Gap | -- | PRIMARY | -- |
| RC3 Agent Dispatch | -- | PRIMARY | -- |
| RC4 Return Contract | -- | -- | PRIMARY |
| RC5 Claude Behavior | PRIMARY | fallback | -- |

All five root causes are addressed. No fix is redundant.

## Solution Task Assignments

| Root Cause | Rank | Solution Task | Skill | Fix # |
|-----------|------|---------------|-------|-------|
| RC1: Invocation Wiring Gap | 1 | T02.01: Add Skill to allowed-tools in roadmap.md and SKILL.md | /sc:reflect | Fix 1 |
| RC5: Claude Behavioral Interpretation | 2 | T02.02: Add fallback protocol to Wave 2 for degraded-mode execution | /sc:reflect | Fix 2 |
| RC2: Spec-Execution Gap | 3 | T02.03: Rewrite Wave 2 step 3 with explicit tool-call syntax, vocabulary glossary, and decomposed sub-steps | /sc:design | Fix 2 |
| RC4: Return Contract Data Flow | 4 | T02.04: Define file-based return-contract.yaml convention in sc:adversarial and adversarial-integration.md | /sc:design | Fix 3 |
| RC3: Agent Dispatch Mechanism | 5 | T02.05: Add agent bootstrap step to sc:adversarial SKILL.md; update stale agents README | (raw analysis) | Fix 2 |

---

*Adversarial ranking performed 2026-02-22. Analyst: claude-opus-4-6 (debate orchestrator mode).*
*Methodology: Cross-validation of self-reported scores against evidence quality, overlap detection, dependency chain analysis, and minimal fix set optimization.*
