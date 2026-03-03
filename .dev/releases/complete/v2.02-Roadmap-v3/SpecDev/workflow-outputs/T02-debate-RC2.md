# Adversarial Debate: RC2 Mitigation Effectiveness

**Debate Question**: Does the sprint specification effectively mitigate RC2 (Specification-Execution Gap)?

**RC2 Summary**: The verb "Invoke" is undefined in tool-call terms. Wave 4 uses "Dispatch" (maps to Task agents) while Wave 2 uses "Invoke" (maps to nothing). The `allowed-tools` list excludes `Skill`. Five sub-operations are compressed into a single step, and critical invocation details are deferred to cross-references. Likelihood: 0.75, Impact: 0.80, Combined Score: 0.770.

**Sprint Spec Tasks Addressing RC2**:
- Epic 2 Task 2.1: Verb-to-tool glossary before Wave 0
- Epic 2 Task 2.2: Decompose Wave 2 step 3 into 6 atomic sub-steps (3a-3f)
- Epic 2 Task 2.3: Fix Wave 1A step 2 "Invoke" ambiguity
- Epic 2 Task 2.4: Rewrite adversarial-integration.md invocation patterns

---

## FOR Position (Advocate)

### Argument 1: The glossary directly eliminates the core vocabulary ambiguity

RC2's primary symptom is that "Invoke" has no tool-call mapping while "Dispatch" does. Task 2.1 creates an "Execution Vocabulary" section before Wave 0 that defines exactly four verb-to-tool mappings:

- "Invoke skill" = Skill tool call
- "Dispatch agent" = Task tool call
- "Read ref" = Read tool call on refs/ path
- "Write artifact" = Write tool call

The acceptance criteria require that **every verb used in Wave 0-4** appears in the glossary. This is not a partial fix -- it is a completeness constraint. After implementation, no Wave instruction can use a verb that lacks a tool-call definition. The quality gate in the Definition of Done (line 215-216) reinforces this: "Every verb in Wave 0-4 appears in the glossary table" and "Every sub-step in Wave 2 step 3 uses exactly one verb from the glossary." This is a structural guarantee, not a best-effort suggestion.

### Argument 2: The 6-step decomposition eliminates the compressed-step problem

RC2 identified that "five sub-operations are compressed into a single step." Task 2.2 decomposes Wave 2 step 3 into sub-steps 3a through 3f, each with exactly one verb and one explicit output:

| Sub-step | Action | Output |
|----------|--------|--------|
| 3a | Parse `--agents` list | Individual agent specs |
| 3b | Expand agents into variant generation parameters | Variant parameters |
| 3c | Add debate-orchestrator if agents >= 3 | Coordination role assignment |
| 3d | Skill tool invocation OR fallback | sc:adversarial execution or fallback pipeline |
| 3e | Consume return-contract.yaml with status routing | Routing decision (proceed/warn/abort) |
| 3f | Skip template generation if adversarial succeeded | Output source selection |

This is a direct, precise response to the "compressed into a single step" complaint. Each sub-step is atomic: one verb, one output, one responsibility. The acceptance criteria enforce this granularity.

### Argument 3: Wave 1A is not forgotten

RC2 focused on Wave 2, but the verb ambiguity existed in Wave 1A step 2 as well. Task 2.3 explicitly addresses this: "Replace 'Invoke sc:adversarial' in Wave 1A step 2 (the `--specs` path) with the same Skill tool call pattern used in step 3d. Add the same fallback protocol." This demonstrates that the sprint spec did not narrowly target the most-discussed instance but performed a sweep for all instances of the undefined verb.

### Argument 4: Cross-reference deferral is addressed

RC2 identified that "critical invocation details are deferred to cross-references rather than inlined." Task 2.4 rewrites adversarial-integration.md to convert all standalone pseudo-CLI syntax into Skill tool call format. The Definition of Done (line 205) requires: "Zero standalone `sc:adversarial --` pseudo-CLI syntax remains in adversarial-integration.md." This means the cross-referenced document itself becomes executable, not just the primary SKILL.md.

### Argument 5: Verification tests provide enforcement

Verification Test 2 (Wave 2 Step 3 Structural Audit) is a 7-point manual checklist that validates the decomposition. Verification Test 4 (Pseudo-CLI Elimination) uses `grep` to confirm zero residual pseudo-CLI patterns. These are not aspirational -- they are concrete pass/fail gates.

---

## AGAINST Position (Challenger)

### Argument 1: The glossary's completeness claim is untestable as specified

Task 2.1's acceptance criteria state "every verb used in Wave 0-4 is present in the glossary." But the spec defines only four verbs (Invoke skill, Dispatch agent, Read ref, Write artifact). What about other actions that appear in the Waves? For example:

- Does "Parse" (step 3a) map to a tool? It is not in the glossary.
- Does "Expand" (step 3b) map to a tool? It is not in the glossary.
- Does "Add" (step 3c, adding debate-orchestrator) map to a tool? Not in the glossary.
- Does "Consume" (step 3e) map to Read, or is it a new verb?
- Does "Skip" (step 3f) map to anything?

The four-verb glossary covers tool-call verbs, but the six sub-steps introduce at least three additional operational verbs (Parse, Expand, Add/Skip) that have no glossary entry. If the acceptance criteria are taken literally ("every verb used in Wave 0-4"), these must be in the glossary too. If they are not tool-call verbs but "cognitive" verbs, the glossary needs a category for non-tool operations -- otherwise the same ambiguity class persists at a lower level.

### Argument 2: The decomposition may introduce new ambiguity in step 3c

Step 3c says: "If agents list length >= 3, add debate-orchestrator to coordination role." This is itself an underspecified instruction. What does "add to coordination role" mean in tool-call terms? Is this a Task dispatch? A configuration change? An argument to the Skill tool call? The original RC2 complaint was that instructions are not executable -- step 3c appears to be exactly the kind of natural-language instruction that RC2 flagged. The acceptance criterion ("each sub-step has exactly one verb from the glossary") would require 3c to use one of the four glossary verbs, but "add" is not among them. Either 3c violates the acceptance criteria, or the glossary must be expanded, or 3c is a design-time decision rather than a runtime instruction -- but the spec does not clarify which.

### Argument 3: The fallback protocol is specified in Epic 1, not Epic 2

The sprint spec's Task 2.2 says it "integrates with Epic 1 tasks 1.3 and 1.4." The fallback protocol (5 steps F1-F5) is defined in Task 1.4, which belongs to Epic 1 (Invocation Wiring), not Epic 2 (Specification Rewrite). From an RC2 perspective, the question is: does the SPECIFICATION of the fallback use glossary-consistent verbs and atomic sub-steps? Task 1.4's fallback steps use "dispatch Task agents" and "dispatch Task agent" -- which maps to the "Dispatch agent" glossary entry. This is good. But the fallback steps also use verbs like "abort" and "write" that would need glossary coverage. The spec does not explicitly confirm that the fallback steps themselves undergo the same glossary-consistency check as the primary path. The quality gate says "Every sub-step in Wave 2 step 3 uses exactly one verb from the glossary" -- do the F1-F5 fallback sub-steps count as sub-steps of step 3? If not, the fallback could remain specification-ambiguous even after Epic 2 is complete.

### Argument 4: adversarial-integration.md rewrite scope is unclear on edge cases

Task 2.4 states: "Only convert standalone invocation examples that are not wrapped in Skill tool call format." The acceptance criterion clarifies that "args strings within Skill tool calls MAY contain `--flag` syntax." This is a sensible distinction. However, the spec does not address what happens if adversarial-integration.md contains other ambiguous verbs beyond the pseudo-CLI syntax. If the document says "Run the adversarial pipeline" or "Execute the debate," those are also specification-execution gaps, just expressed differently than `sc:adversarial --compare`. Task 2.4 is scoped to pseudo-CLI syntax elimination, not to full verb-consistency of the reference document. This leaves a residual gap.

### Argument 5: No automated enforcement of glossary consistency post-sprint

The DVL verification scripts are listed as "implement if time permits." The spec's `validate_wave2_spec.py` (estimated 2 hours) would validate Epic 2's acceptance criteria programmatically, but it is optional. Without it, glossary consistency degrades over time as future edits to SKILL.md add new instructions without updating the glossary. The spec fixes the current state but does not install a guard against regression. RC2 is a class of problem (specification ambiguity), not a single instance -- fixing the current instances without preventing future ones is incomplete mitigation.

---

## CROSS-EXAMINATION

### Advocate challenges Challenger's Argument 1

**Advocate**: The glossary's purpose is to map verbs to TOOL CALLS, not to catalog every English verb in the specification. "Parse," "Expand," and "Skip" are not tool-call verbs -- they describe logical operations Claude performs internally. The acceptance criteria "every verb used in Wave 0-4 is present in the glossary" should be read as "every verb that maps to an external tool invocation." RC2's core complaint was that "Invoke" maps to nothing in the tool ecosystem, not that every natural language word needs a formal definition. Steps 3a, 3b, 3c, and 3f describe what Claude should THINK, while steps 3d and 3e describe what Claude should DO with external tools. This distinction is well-understood in LLM instruction design.

**Challenger response**: The distinction between "cognitive verbs" and "tool-call verbs" is exactly the kind of implicit knowledge that RC2 identified as problematic. If the glossary only covers tool-call verbs, it should say so explicitly. The current acceptance criteria -- "every verb used in Wave 0-4" -- do not make this distinction. An implementer reading the spec literally would either (a) try to add Parse/Expand/Skip to the glossary (creating absurd entries) or (b) judge the glossary incomplete. The fix is simple -- add a sentence like "This glossary covers verbs that map to external tool invocations. Internal reasoning operations (parse, evaluate, decide) do not require tool mappings." -- but the spec does not include it.

### Challenger challenges Advocate's Argument 2

**Challenger**: You claim the 6-step decomposition eliminates the compressed-step problem. But has the compression merely been redistributed? Step 3d is described as "Use Skill tool to invoke sc:adversarial with specified arguments OR execute fallback." The "OR execute fallback" clause packs the entire 5-step F1-F5 fallback protocol into step 3d. If the original RC2 complaint was "five sub-operations compressed into a single step," step 3d now contains "one primary operation OR five fallback operations" in a single step. Is this not the same structural problem at a different level of nesting?

**Advocate response**: The compression in step 3d is qualitatively different from the original RC2 problem. The original step 3 compressed five SEQUENTIAL operations with no branching logic into one instruction. Step 3d presents a single DECISION POINT: try the primary path, and if it fails, follow the fallback. The fallback itself (F1-F5) is fully decomposed in Task 1.4 with defined inputs, outputs, and failure actions for each sub-step. The structure is: one atomic primary action with a conditional branch to a fully specified fallback sequence. This is standard control flow, not compression. The original RC2 problem was that Claude had to infer the sub-operations from a vague instruction; here, every sub-operation is explicitly enumerated.

---

## SCORING

### Dimension 1: Root Cause Coverage (0.82)

The spec addresses all four identified aspects of RC2:
- Undefined "Invoke" verb: **Addressed** by Task 2.1 (glossary) and Task 2.3 (Wave 1A fix)
- Wave 2 vs Wave 4 verb inconsistency: **Addressed** by Task 2.1 (glossary normalizes all verbs)
- Five compressed sub-operations: **Addressed** by Task 2.2 (6 atomic sub-steps)
- Critical details deferred to cross-references: **Addressed** by Task 2.4 (rewrite adversarial-integration.md)

Deduction: The glossary scope (tool-call verbs vs all verbs) is not explicitly clarified, leaving a minor ambiguity in the fix itself. The fallback protocol's glossary consistency is not explicitly required. Score: **0.82**

### Dimension 2: Completeness (0.72)

The spec fixes all KNOWN instances of the specification-execution gap. Gaps identified:

1. Glossary does not distinguish tool-call verbs from cognitive verbs (-0.05)
2. Step 3c ("add debate-orchestrator to coordination role") is underspecified (-0.08)
3. Fallback steps F1-F5 are not explicitly subject to glossary-consistency quality gate (-0.05)
4. adversarial-integration.md rewrite is scoped to pseudo-CLI syntax only, not to all ambiguous verbs (-0.05)
5. No automated regression prevention for glossary consistency (-0.05)

These are minor gaps, not fundamental omissions. The core decomposition and glossary are solid. Score: **0.72**

### Dimension 3: Feasibility (0.88)

All four tasks are straightforward text edits to markdown files:
- Task 2.1: Insert a glossary table (trivial)
- Task 2.2: Rewrite one step into six sub-steps (moderate, but well-specified)
- Task 2.3: Apply the same pattern to a second location (trivial)
- Task 2.4: Search-and-replace pseudo-CLI patterns (straightforward)

The main feasibility risk is Task 2.2's coordination with Epic 1 Tasks 1.3 and 1.4 (same text, single atomic rewrite). The spec explicitly calls this out and assigns a single author. The DVL scripts are optional and do not affect the core feasibility. Score: **0.88**

### Dimension 4: Blast Radius (0.80)

The fix modifies specification language in two files (SKILL.md, adversarial-integration.md). Potential new problems:

1. The glossary could become a maintenance burden if not kept in sync with new Wave instructions (-0.05)
2. The 6-step decomposition is more verbose, increasing the token cost of processing SKILL.md (-0.05)
3. Step 3c's underspecification could introduce a NEW ambiguity that did not exist before (-0.05)
4. Converting adversarial-integration.md to Skill tool call format assumes the Skill tool's args syntax is stable (-0.05)

None of these are high-severity. The glossary is a net positive even if it requires maintenance. The verbosity increase is justified by the clarity gain. Score: **0.80**

### Dimension 5: Confidence (0.78)

The fix is well-targeted and directly addresses each element of RC2. Confidence reducers:

1. The glossary's scope ambiguity (tool-call verbs vs all verbs) could cause confusion during implementation (-0.07)
2. No automated regression test means the fix could erode over time (-0.05)
3. The cross-examination revealed that step 3c is genuinely underspecified, which is a new instance of the same class of problem RC2 describes (-0.05)
4. The fallback protocol's glossary compliance is assumed but not verified (-0.05)

Confidence is moderate-to-high. The fix addresses the root cause's primary manifestations but does not fully prevent the class of problem from recurring. Score: **0.78**

---

## SCORING SUMMARY

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Root Cause Coverage | 0.82 | 0.25 | 0.205 |
| Completeness | 0.72 | 0.25 | 0.180 |
| Feasibility | 0.88 | 0.20 | 0.176 |
| Blast Radius | 0.80 | 0.15 | 0.120 |
| Confidence | 0.78 | 0.15 | 0.117 |
| **Weighted Average** | | | **0.798** |

---

## VERDICT: NEEDS AMENDMENTS

**Score: 0.798** -- Above the INSUFFICIENT threshold (0.60) but below SUFFICIENT (0.85).

### Required Amendments

1. **Clarify glossary scope**: Add explicit language to Task 2.1 that the glossary covers "verbs that map to external tool invocations" and that internal reasoning operations (parse, evaluate, decide, skip) do not require glossary entries. This resolves the Challenger's Argument 1 and the Advocate's cross-examination defense by making the implicit distinction explicit.

2. **Specify step 3c in tool-call terms**: Clarify whether "add debate-orchestrator to coordination role" means (a) appending `--orchestrator debate-orchestrator` to the Skill tool args, (b) dispatching a separate Task agent with debate-orchestrator instructions, or (c) a design-time decision that affects how step 3d is parameterized. The current phrasing is the same class of ambiguity RC2 was meant to fix.

3. **Extend glossary-consistency quality gate to fallback steps**: Add to the Definition of Done: "Every sub-step in the fallback protocol (F1-F5) uses glossary-consistent verbs for tool-call operations." This ensures the fallback path receives the same specification rigor as the primary path.

4. **Scope adversarial-integration.md rewrite to include non-CLI ambiguous verbs**: Expand Task 2.4's scope (or add a Task 2.5) to audit adversarial-integration.md for any remaining ambiguous action verbs beyond pseudo-CLI syntax, ensuring the entire reference document uses glossary-consistent language.

### Optional (Recommended) Amendment

5. **Prioritize `validate_wave2_spec.py`**: Move the DVL script from "if time permits" to a sprint task. A 2-hour investment in automated glossary/sub-step validation prevents regression and strengthens long-term mitigation of the specification-execution gap as a class of problem.

---

*Debate conducted 2026-02-23. Analyst: claude-opus-4-6 (adversarial debate mode).*
*Inputs: sprint-spec.md, ranked-root-causes.md.*
*Method: Structured FOR/AGAINST positions with cross-examination, 5-dimension scoring.*
