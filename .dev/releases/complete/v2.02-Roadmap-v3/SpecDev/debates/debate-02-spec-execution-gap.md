# Debate 02: Specification-Execution Gap Fix (RC2, Rank 3)

**Solution under review**: Solution 02 — Decompose Wave 2 step 3 into atomic sub-steps with explicit tool-call syntax, add a verb-to-tool glossary, and rewrite adversarial-integration.md invocation patterns.

**Root cause**: RC2 — The verb "Invoke" has no defined tool-call mapping; five sub-operations are compressed into a single step; critical execution details are deferred to cross-references that use pseudo-CLI syntax rather than tool-call instructions.

**Debate date**: 2026-02-22
**Debate orchestrator**: claude-sonnet-4-6

---

## Advocate FOR

### Position: Solution 02 is the correct fix and should be prioritized alongside Solution 01.

**Argument 1: The Wave 4 parity principle is analytically sound.**

The solution's central claim is that Wave 4 works because it follows three structural principles — atomic steps, explicit tool binding, and inline prompts — and that Wave 2 step 3 violates all three. This is not an opinion; it is verifiable by inspection. Wave 4 step 1 says "Dispatch quality-engineer agent using the prompt from refs/validation.md." Every element is resolvable: verb → Task tool, agent → quality-engineer, input → a specific section of a specific ref file, output → validation report JSON. Wave 2 step 3 says "Invoke sc:adversarial for multi-roadmap generation per refs/adversarial-integration.md." The verb maps to nothing, the agent is ambiguous (a skill is not an agent), the input is scattered, and the output is implicit. The structural difference is not subtle — it is a binary distinction between a resolvable instruction and an unresolvable one.

**Argument 2: Option B (expanded sub-steps) is the minimal correct change.**

The solution correctly rejects Option A (Skill tool syntax only) as insufficient because it fixes the verb while leaving the five-operation compression intact. It correctly rejects Option C (decision tree with fallback paths) as over-engineered. It correctly rejects Option D (Wave 2A/2B split) as architecturally disproportionate. Option B applies the smallest change that eliminates the ambiguity: decomposing one compressed step into six atomic sub-steps, each with one verb, one tool, one output. The proposed sub-steps (3a through 3f) are concrete, follow the Wave 4 pattern, and cover the complete logical sequence — parse, expand, add orchestrator, invoke, consume return contract, replace template generation.

**Argument 3: The verb-to-tool glossary is a system-level quality improvement.**

Change 1 (adding a verb-to-tool glossary before Wave 0) is not just a local fix — it is a preventive measure that makes the entire SKILL.md self-documenting. Without the glossary, the next developer who adds a wave instruction must guess which verbs are valid. With it, there is a single authoritative mapping. This is the correct architectural response to a verb-ambiguity failure: define the vocabulary, then enforce it.

**Argument 4: Proactive Wave 1A fix prevents a known latent defect.**

Change 3 (decomposing Wave 1A step 2) addresses the same "Invoke" ambiguity in the `--specs` path. The solution correctly notes that this was not the observed failure point (because `--specs` was not used in the test case), but fixing it now costs ~10 additional lines and prevents an identical future failure. This is the correct cost-benefit calculation: fix cheap now versus debug expensive later.

**Argument 5: The adversarial-integration.md rewrite eliminates the pseudo-CLI confusion.**

Change 5 (rewriting invocation patterns from pseudo-CLI syntax to Skill tool call specifications) addresses the root of the cross-reference problem. When Claude follows the cross-reference and finds `sc:adversarial --compare <spec-files> --depth <roadmap-depth>`, it sees a terminal command and cannot resolve it to a tool call. When it finds a Skill tool call specification with `skill` and `args` fields, it has an executable instruction. The rewrite is surgical: it changes the syntax of the invocation patterns without altering their semantic content.

**Argument 6: The fallback path in step 3d is correctly scoped.**

The solution includes a fallback for when the Skill tool is unavailable, but it places the fallback inside the sub-step rather than promoting it to a full decision tree (Option C). This is the right structural choice: the fallback is a contingency within a step, not an alternative wave architecture. The fallback — read sc:adversarial's SKILL.md, then dispatch a Task agent with the adversarial behavioral instructions embedded in the prompt — is both concrete and executable.

---

## Advocate AGAINST

### Position: Solution 02 addresses symptoms of RC2 but overstates RC2's independence from RC1. Its feasibility depends on assumptions that may not hold, and its completeness has exploitable gaps.

**Argument 1: RC2 is a compounding factor, not a primary cause. Fixing it alone does not fix the failure.**

The ranked-root-causes document explicitly validates this: "The specification ambiguity is real, but it is a CONTRIBUTING FACTOR to the wiring gap, not an independent cause. If the Skill tool were in allowed-tools AND the instructions were ambiguous, Claude would likely still attempt invocation (it recognizes sc:adversarial as a skill name)." This means Solution 02 is addressing a secondary problem. If RC1 (Skill tool absent from allowed-tools) is fixed without fixing RC2, Claude will likely still invoke sc:adversarial because it recognizes the skill name — the instruction ambiguity matters most in the absence of the infrastructure. Conversely, if RC1 is not fixed, rewriting the Wave 2 step 3 instructions produces a beautifully formatted step 3d that says "Use the Skill tool" in a context where the Skill tool is not available. The fallback path then runs, which is no better than the current degraded behavior — it just makes the degradation more intentional.

**Argument 2: Step 3e (consume return contract) depends on Solution 04, which is not implemented.**

Sub-step 3e specifies detailed routing on the `status` field of the return contract: success paths, partial paths with convergence thresholds, and failure abort paths. But as the solution itself acknowledges in its dependency notes: "Step 3e's return contract requires Solution 04 (transport mechanism). Without these, the fallback path in 3d handles the Skill tool case, but 3e remains partially unresolved." This is a significant incompleteness. The most complex and failure-prone sub-step — the one that consumes structured data from a cross-skill invocation — cannot be fully implemented until RC4 is addressed. In the interim, step 3e describes a contract consumption protocol for a contract whose transport mechanism does not exist. This is specification debt shifting, not specification debt elimination.

**Argument 3: The verb-to-tool glossary introduces a new maintenance burden without enforcement.**

The glossary is a documentation artifact, not a runtime constraint. There is no mechanism in the framework that validates new wave instructions against the glossary. The glossary says "Invoke skill → Skill tool," but the next developer writing a wave instruction can ignore the glossary entirely without triggering any failure. The glossary prevents ambiguity only if developers read it and comply with it. Given that the current ambiguity exists despite Wave 4's unambiguous example being three paragraphs away in the same file, there is evidence that proximity of correct examples does not guarantee adherence. A glossary without enforcement is optimistic documentation.

**Argument 4: Sub-step 3d's Skill tool call may trigger the "already running" constraint.**

Solution 01 raised this concern explicitly: the Skill tool documentation states "Do not invoke a skill that is already running." When sc:roadmap (a skill) attempts to invoke sc:adversarial (another skill), does this trigger the constraint? Solution 02 includes a fallback for when "the Skill tool is unavailable (not in allowed-tools or returns an error indicating the skill cannot be found)," but the "already running" constraint is distinct from "unavailable." The Skill tool may be in allowed-tools and findable, but still refuse to invoke sc:adversarial because sc:roadmap is currently running. The fallback condition in step 3d does not match this failure mode: "returns an error indicating the skill cannot be found" is a different error than "refused because a skill is already running." This is a gap in the fallback logic.

**Argument 5: The six sub-steps increase instruction density without reducing cognitive load.**

The current Wave 2 step 3 is a single compressed sentence. The proposed replacement is six numbered sub-steps with inline tool specifications, conditional branching in step 3c, multi-path routing in step 3e, and a skip instruction in step 3f. The total instruction volume increases roughly 8x. While each individual sub-step is simpler than the original, the sequence as a whole is more complex. Claude must now track six sequential actions, two conditionals (3c and 3e), one branching return contract router (3e), and one skip instruction (3f). The risk of a different failure mode — Claude losing track of the sequence or misapplying step 3e's branching logic — increases with instruction density.

**Argument 6: The adversarial-integration.md rewrite is incomplete as specified.**

Change 5 specifies rewriting "both the Multi-Spec Consolidation and Multi-Roadmap Generation invocation pattern subsections," but the solution does not specify whether other sections of adversarial-integration.md (agent specification parsing format examples, return contract consumption protocol, interactive flag propagation) also need updating to reflect the new tool-call syntax. If those sections still use pseudo-CLI conventions, the cross-reference fix is partial: Claude follows the link, finds the corrected invocation pattern, but encounters the same pseudo-CLI syntax in adjacent sections that provide essential context for the invocation.

---

## Rebuttal

### FOR rebuts AGAINST's Arguments 1 and 2 (dependency concerns)

AGAINST correctly notes that RC2 is a compounding factor, not a primary cause. But this is not an argument against fixing RC2 — it is an argument for fixing RC1 first and RC2 second, which is exactly the solution ordering in the solution task assignments. The ranked-root-causes document's minimal fix set explicitly treats Fix 2 (rewriting Wave 2 step 3) as complementary to Fix 1 (adding Skill to allowed-tools). Solution 02 acknowledges its dependency on Solution 01 explicitly. The debate question is whether Solution 02 should be implemented, not whether it should be implemented in isolation. Given that Fix 2 addresses RC2, RC3, and RC5 (fallback protocol), it carries disproportionate value relative to its implementation cost.

On step 3e's dependency on Solution 04: the solution correctly flags this in its dependency notes. The interim state — step 3e described but not fully resolvable without return-contract.yaml — is still an improvement over the current state, where step 3 provides no guidance on return contract consumption at all. A partially specified step 3e is better than a completely absent one, provided the partial specification does not mislead Claude into assuming a transport mechanism that does not exist. This is addressable by adding a conditional guard in step 3e: "If return-contract.yaml is found, route on status field; if not found, treat as status: partial and proceed."

### AGAINST rebuts FOR's Argument 3 (glossary enforcement)

FOR's response to the enforcement concern is that a glossary is better than no glossary, even without enforcement. This is true but understates the risk. The glossary creates a false impression of constraint — it signals "these are the valid verbs" without preventing invalid verbs. The risk is not that the glossary is ignored, but that its presence reduces the perceived urgency of enforcement. A stronger countermeasure would be to add the glossary as a machine-readable YAML block (e.g., in the frontmatter) that could, in principle, be linted against. That format change is not proposed in Solution 02.

### FOR rebuts AGAINST's Argument 4 ("already running" constraint)

AGAINST's concern about the "already running" constraint is valid and is the same concern raised in Solution 01's Option A analysis. The fallback condition in step 3d does address this partially: "If the Skill tool is unavailable (not in allowed-tools or returns an error indicating the skill cannot be found)" is admittedly imprecise. The fix is to add "or returns an error indicating a skill is already running" to the fallback trigger condition. This is a one-sentence amendment to step 3d, not a structural flaw in the solution.

### AGAINST concedes on Argument 5 (instruction density)

The instruction density argument is legitimate but does not outweigh the clarity benefit. The original single sentence is dense AND ambiguous. Six sub-steps are dense but each is individually resolvable. The cognitive load trade-off favors the sub-steps because each step produces a verifiable intermediate output — parsed agent list, expanded agent list, orchestrator decision, Skill tool call, return contract status, generation skip. These checkpoints enable error localization in a way the original sentence does not. Claude can fail at step 3c and have a clear error message; with the original, Claude fails at the entire step 3 with no localization.

### Unresolved after rebuttal

- The "already running" fallback condition gap (AGAINST Argument 4) requires a one-line amendment but is not resolved by the current solution text.
- The adversarial-integration.md rewrite scope (AGAINST Argument 6) is underspecified. The solution should enumerate all sections requiring pseudo-CLI to tool-call conversion, not just the two invocation pattern subsections.
- Step 3e's dependency on Solution 04 creates a window where step 3e's return contract routing is specified but unexecutable. A guard condition should be added to handle the absent return-contract.yaml case.

---

## Scoring Matrix

| Dimension | Weight | Score | Rationale |
|-----------|--------|-------|-----------|
| Root cause coverage | 0.25 | 0.70 | RC2 is directly addressed by all five changes. However, RC2 is a compounding factor (Rank 3), not the primary blocker. The solution does not independently resolve the failure — it depends on Solution 01 (RC1) for the Skill tool wiring and Solution 04 (RC4) for step 3e's return contract routing. Coverage of RC2 itself is high (0.85), but discounted for dependency on other solutions to achieve full effect. |
| Completeness | 0.20 | 0.68 | Sub-steps 3a-3f are logically complete for the happy path. Step 3e has an unresolved dependency on Solution 04 (no transport mechanism for return contract). The fallback in step 3d has an imprecise trigger condition for the "already running" constraint. The adversarial-integration.md rewrite scope is underspecified — only two subsections are targeted; other pseudo-CLI sections may remain. Wave 1A step 2 fix is included, which is a completeness gain. |
| Feasibility | 0.25 | 0.82 | The core changes (decompose step 3, add glossary, rewrite invocation patterns) are pure documentation edits requiring no code changes, no architecture changes, and no new dependencies. The changes are additive — they add detail rather than removing or restructuring existing instructions. The only feasibility risk is the "already running" constraint in step 3d, which may require behavioral testing. Implementation effort is estimated at ~50 lines of SKILL.md edits and ~30 lines of adversarial-integration.md edits. |
| Blast radius | 0.15 | 0.80 | Changes are confined to two files: `src/superclaude/skills/sc-roadmap/SKILL.md` and `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`. No other skills, commands, or agents are modified. The Change 4 (add Skill to allowed-tools) is shared with Solution 01 and should be implemented once. The glossary addition is a new subsection that does not modify existing wave instructions. Low blast radius. |
| Confidence | 0.15 | 0.75 | The Wave 4 parity argument is structurally sound and verifiable by inspection. The sub-step decomposition directly mirrors the pattern that works. The glossary is a sound preventive measure. Confidence is discounted for: (1) the unverified Skill tool nesting behavior in step 3d's primary path, (2) step 3e's partial dependency on Solution 04, and (3) the possibility that the adversarial-integration.md rewrite is incomplete. Solution 02's own confidence self-assessment of 0.85 is slightly optimistic given these unresolved concerns. |

---

## Fix Likelihood

**Weighted score computation**:

| Dimension | Weight | Score | Contribution |
|-----------|--------|-------|-------------|
| Root cause coverage | 0.25 | 0.70 | 0.175 |
| Completeness | 0.20 | 0.68 | 0.136 |
| Feasibility | 0.25 | 0.82 | 0.205 |
| Blast radius | 0.15 | 0.80 | 0.120 |
| Confidence | 0.15 | 0.75 | 0.1125 |

**Fix likelihood: 0.749** (rounded to 0.75)

**Interpretation**: Solution 02 has a 75% probability of eliminating the specification-execution gap as a contributing factor to the adversarial invocation failure. It is not sufficient on its own to restore full adversarial pipeline functionality (that requires Solutions 01 and 04), but it is a necessary complement to Solution 01 and raises the combined fix likelihood for the complete failure significantly above either solution alone.

**Comparison to solution's own assessment**: Solution 02 self-reported an overall confidence of 0.85. The debate scoring produces 0.75. The 0.10 gap is explained by the ranked-root-causes validator's finding that RC2's likelihood should be reduced from 0.85 to 0.75 (compounding factor, not independent cause), and by the three unresolved concerns identified in rebuttal.

---

## Unresolved Concerns

### UC-02-01: Fallback trigger condition is imprecise for "already running" constraint (HIGH)

**Description**: Step 3d's fallback triggers on "Skill tool is unavailable (not in allowed-tools or returns an error indicating the skill cannot be found)." The "already running" constraint would produce a different error — one indicating that invocation is refused because a skill is currently executing, not that the skill cannot be found. Claude may not engage the fallback if it encounters this specific error type.

**Risk**: If sc:roadmap (running) attempts to invoke sc:adversarial and receives "skill already running" rather than "skill not found," the fallback path is not triggered and execution hangs or errors out without a recovery path.

**Resolution**: Amend step 3d's fallback trigger to: "If the Skill tool returns any error (including: tool not in allowed-tools, skill not found, or skill already running), execute the fallback."

**Blocking**: No (amendable in implementation).

### UC-02-02: Step 3e is partially unexecutable without Solution 04 (MEDIUM)

**Description**: Step 3e specifies routing on the `status` field of the return contract, but Solution 04 (file-based return-contract.yaml) has not been implemented. When step 3e executes, the return-contract.yaml file may not exist, and the routing logic fails at its first action.

**Risk**: Claude attempts to read a return contract that does not exist, encounters a missing file, and has no specified recovery. This could produce either a silent failure (no output) or an unhandled error.

**Resolution**: Add a guard condition to step 3e: "First, check if `<output-dir>/adversarial/return-contract.yaml` exists. If not found, treat as `status: partial` with convergence_score 0.0 and log a warning in extraction.md."

**Blocking**: No (amendable in implementation, or resolved by implementing Solution 04 first).

### UC-02-03: adversarial-integration.md rewrite scope is underspecified (LOW)

**Description**: Change 5 specifies rewriting only the "Multi-Spec Consolidation" and "Multi-Roadmap Generation" invocation pattern subsections. Other sections of adversarial-integration.md — agent specification parsing examples, return contract field descriptions, interactive flag propagation notes — may also contain pseudo-CLI syntax that would confuse Claude if it reads those sections as context.

**Risk**: Claude follows the corrected invocation pattern, proceeds to read adjacent sections for context, and encounters pseudo-CLI syntax that contradicts the tool-call instruction format just provided.

**Resolution**: Conduct a full audit of adversarial-integration.md for pseudo-CLI syntax patterns (`sc:adversarial --*`) and convert all occurrences to tool-call specifications or explanatory prose.

**Blocking**: No (low-severity, addressable as a follow-up audit task).

### UC-02-04: Glossary has no enforcement mechanism (INFORMATIONAL)

**Description**: The verb-to-tool glossary is a documentation artifact. No linting, validation, or CI check enforces adherence. The failure mode that RC2 represents — a developer writing "Invoke" without checking the glossary — can recur.

**Risk**: Future wave instructions introduce new undefined verbs, reproducing RC2 in a different wave.

**Resolution**: Consider adding the glossary as a machine-readable YAML block in the SKILL.md frontmatter, enabling future linting. Alternatively, add a pre-commit check that scans SKILL.md for unlisted verbs against the glossary table.

**Blocking**: No (informational, long-term improvement outside scope of current fix).

---

## Verdict

Solution 02 is **recommended for implementation with amendments**, conditional on Solution 01 being implemented in the same release.

- **Implement**: Changes 1, 2, 3, 4, 5 as specified.
- **Amend**: Change 2 step 3d's fallback trigger to cover the "already running" error (UC-02-01).
- **Amend**: Change 2 step 3e to add a guard for missing return-contract.yaml (UC-02-02).
- **Follow-up**: Full pseudo-CLI audit of adversarial-integration.md beyond the two targeted subsections (UC-02-03).
- **Do not block on**: Glossary enforcement mechanism (UC-02-04, long-term improvement).

**Implementation order**: Solution 01 (add Skill to allowed-tools) → Solution 02 (rewrite Wave 2 step 3) → Solution 04 (return-contract.yaml convention). This ordering ensures that each layer is in place before the next layer depends on it.

---

*Debate conducted 2026-02-22. Orchestrator: claude-sonnet-4-6.*
*Root cause reference: ranked-root-causes.md, RC2 (Rank 3, validated score 0.77).*
*Solution reference: solution-02-spec-execution-gap.md.*
