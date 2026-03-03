# Spec Panel Review: sc:roadmap Adversarial Pipeline Remediation

**Sprint Spec Reviewed**: `sprint-spec.md` (2026-02-22)
**Panel Date**: 2026-02-23
**Reviewers**: Fred Brooks, Leslie Lamport, Nancy Leveson, Gerald Weinberg

---

## Individual Expert Reviews

---

### Fred Brooks (Software Engineering, Complexity, Conceptual Integrity)

#### Top Concern: Second-System Effect in the DVL

The sprint specification exhibits a textbook second-system effect. The core problem is straightforward: a missing tool in an allowed-tools list, ambiguous natural-language instructions, and no file-based return mechanism. The fix for these three issues touches 4 files with well-scoped edits. This is a one-day sprint.

Yet the specification devotes 55% of its text (lines 142-449) to a "Deterministic Verification Layer" proposing 10 scripts, 3 tiers, 6 anti-hallucination strategies, a sentinel file convention, and a generalized framework applicable to "any multi-agent workflow in SuperClaude." This is not a brainstorm addendum -- it is a gravitational attractor that will pull implementation effort away from the actual fixes. The label "BRAINSTORM ONLY" is insufficient protection against scope creep when the brainstorm is more detailed than the sprint itself.

The DVL also contains a conceptual integrity violation: it proposes deterministic scripts to verify the behavior of a non-deterministic system (an LLM interpreting markdown instructions). Scripts like `validate_wave2_spec.py` can verify that the string `skill: "sc:adversarial"` appears in step 3d, but they cannot verify that Claude will actually use the Skill tool when encountering that string. The specification conflates structural compliance with behavioral compliance.

#### Specific Improvements

1. **Move the DVL to a separate document.** It is a future initiative, not a sprint deliverable. Its presence in the sprint spec creates ambiguity about scope. Create `.dev/releases/backlog/dvl-verification-layer/DVL-SPEC.md` and reference it from the sprint spec with a single line: "Future work: see DVL-SPEC.md."

2. **Collapse Epics 1 and 2 into a single epic.** The spec itself acknowledges (line 124) that tasks 1.3, 1.4, and 2.2 must be "implemented as a single atomic rewrite by one author." If three tasks across two epics must be done atomically by one person, they are one epic. The artificial separation creates coordination overhead for zero benefit.

3. **Remove the "combined ranking" formula apparatus.** Lines 9-43 contain three separate ranking tables with weighted formulas (`problem_score = (likelihood * 0.6) + (impact * 0.4)`, etc.). This is false precision. The problem ranking is obvious from the diagnostics: the Skill tool is missing, the spec is ambiguous, the return contract has no transport. The formula apparatus adds ceremony without changing the outcome and wastes reader attention.

#### What I Would Cut

- The entire DVL section (lines 142-449) from the sprint spec. Relocate to backlog.
- The triple-ranking-formula apparatus (lines 9-43). Replace with a simple ordered list with one-sentence rationale per item.
- Tasks 1.5, 2.5, and 3.5 (`make sync-dev`). These are not tasks -- they are a mechanical step after editing. List them once in a "Post-Edit Checklist" section instead of inflating the task count by 20%.

---

### Leslie Lamport (Specification Precision, State Machines, Temporal Properties)

#### Top Concern: The Specification Does Not Define the State Machine for the Fallback Path

The sprint spec describes two invocation paths: the primary path (Skill tool works) and the fallback path (Skill tool fails). Risk R1 assigns a 40% probability to the primary path failing. This means the fallback is not an edge case -- it is a coin flip.

Yet the fallback protocol in Task 1.4 is specified at a fundamentally lower level of rigor than the primary path. The primary path says "use the Skill tool to invoke sc:adversarial" -- a single, atomic operation with clear success/failure semantics. The fallback says "dispatch 5 sequential Task agents for each pipeline step." This is a 5-step sequential state machine with no defined transitions, no error handling per step, no specification of what happens when Task agent 3 of 5 fails, and no definition of what "variant generation, diff analysis, single-round debate, base selection with scoring, merge with provenance" means in operational terms.

The spec says the fallback produces `return-contract.yaml` with `status: partial` and `fallback_mode: true`. But `fallback_mode` is not in the return contract schema defined in Epic 3 (Task 3.1 defines 8 fields; `fallback_mode` is not among them). This is a specification inconsistency that would manifest as either a runtime error or a silently dropped field.

The temporal ordering is also underspecified. Task 2.2 sub-step 3e says: "If return-contract.yaml not found, treat as status: partial with convergence_score: 0.0." But sub-step 3d's fallback protocol is supposed to produce that file. If the fallback runs and succeeds but writes the file to the wrong path (a plausible failure mode with 5 Task agents operating in sequence), the guard condition in 3e fires and masks the successful fallback as a failure with convergence 0.0.

#### Specific Improvements

1. **Add `fallback_mode` to the return contract schema in Task 3.1.** Currently 8 fields are defined. Add `fallback_mode` as field 9 (type: boolean, default: false). Update Task 3.2 consumer expectations to route on this field. Without this, the primary and fallback paths produce incompatible contracts.

2. **Specify the fallback state machine explicitly.** For Task 1.4, define: (a) the 5 states and their transitions, (b) what each Task agent receives as input and produces as output, (c) what happens when any intermediate step fails (abort the whole fallback? skip the step? produce partial output?), (d) the file path where return-contract.yaml is written (must match the path 3e checks).

3. **Add an invariant for return-contract.yaml path resolution.** Define a single, deterministic rule for where the file is written: `<output-dir>/adversarial/return-contract.yaml`. Both the primary path (sc:adversarial writes it) and the fallback path (the 5th Task agent writes it) must use this exact path. Sub-step 3e must check this exact path.

4. **Resolve the R1 probability estimate.** The spec says R1 probability is "HIGH (0.40)" but never proposes a way to empirically determine whether the Skill tool works in Task agents BEFORE implementing the full sprint. Add a Task 0.0: "Dispatch a minimal Task agent that uses the Skill tool to load `sc:adversarial`. Record success/failure. If failure, mark the primary path as non-viable and implement only the fallback." This collapses the uncertainty from 40% to 0% or 100% before any other work begins.

#### What I Would Cut

- The verb-to-tool glossary (Task 2.1) is solving a problem that does not exist once the instructions use explicit tool-call syntax. If step 3d says `Skill tool call with skill: "sc:adversarial"`, the glossary entry "Invoke skill = Skill tool call" is redundant. The glossary adds a layer of indirection: readers must look up the glossary to understand the instructions, then look at the instructions themselves. Just write the instructions in tool-call syntax directly.

---

### Nancy Leveson (System Safety, STAMP, Hazard Analysis)

#### Top Concern: No Hazard Analysis for the Fallback-to-Primary Interaction

The specification treats the primary path and fallback path as independent alternatives. In reality, they form a control structure with hazardous interaction modes that are not analyzed:

**Hazard H1: Fallback activates when primary would have succeeded.** The fallback trigger in step 3d is "If the Skill tool returns any error." But the Skill tool documentation says "Do not invoke a skill that is already running." If sc:roadmap IS the running skill (it is -- it was loaded via the Skill tool), then invoking sc:adversarial via the Skill tool from within sc:roadmap may trigger the "skill already running" constraint on the CALLING skill, not the called one. The spec acknowledges this in Risk R2 but does not analyze whether the "already running" check applies to the caller, the callee, or both. If it applies to the caller, the primary path NEVER works (not 60% as implied by the complement of R1's 40%), and the entire design is a fallback-only system masquerading as a primary-with-fallback system.

**Hazard H2: Partial fallback output consumed as full pipeline output.** The fallback produces `status: partial` with reduced quality (single-round debate instead of multi-round, no position-bias mitigation, no convergence detection). But step 3e routes `status: partial` with `convergence_score >= 0.6` to the same "proceed with warning" path as a genuine partial from the full pipeline. The user warning does not distinguish between "the full pipeline ran but didn't converge" and "a degraded fallback approximation ran." These are qualitatively different situations requiring different user responses.

**Hazard H3: Blast radius of the specification rewrite.** The spec modifies 4 files across 2 skills. The sc-adversarial SKILL.md is 1747 lines of detailed behavioral instructions. Adding a "Return Contract (MANDATORY)" section as the "final pipeline step" (Task 3.1) means every execution of sc:adversarial -- not just those invoked by sc:roadmap -- must now produce this file. If the return contract section introduces a subtle instruction conflict with the existing 5-step protocol, all standalone uses of sc:adversarial are affected. The spec does not analyze this blast radius.

#### Specific Improvements

1. **Add a "Skill tool constraint probe" as the first task.** Before any implementation, empirically determine: (a) Can a Task agent use the Skill tool at all? (b) Does the "already running" constraint apply when sc:roadmap (the current skill) invokes sc:adversarial (a different skill)? (c) What exact error message is returned? This probe resolves H1 and determines whether the sprint is building a primary+fallback system or a fallback-only system.

2. **Differentiate fallback partial from pipeline partial in the return contract.** Add a `pipeline_mode` field (values: `full`, `fallback`) to the return contract. In step 3e, route differently: `pipeline_mode: full` + `status: partial` + `convergence >= 0.6` = proceed with warning. `pipeline_mode: fallback` + `status: partial` = always warn with explicit text: "Output produced by degraded fallback (single-round debate, no convergence tracking). Quality is substantially reduced compared to full adversarial pipeline."

3. **Add a standalone-invocation regression test to Epic 3.** After adding the return contract section to sc:adversarial SKILL.md, verify that standalone invocations (not from sc:roadmap) still work correctly. Acceptance criteria: "Invoking `sc:adversarial --compare file1.md,file2.md` produces the same pipeline behavior as before, plus a return-contract.yaml file." This bounds H3.

4. **Analyze the "already running" constraint semantics.** The spec must determine whether `Skill` tool's "Do not invoke a skill that is already running" means: (a) the exact same skill name, (b) any skill, or (c) the same skill instance. If (b), the primary path is impossible by design and should be removed from the spec rather than carried as a 60% viable path.

#### What I Would Cut

- The anti-hallucination strategies (AH-1 through AH-6) in the DVL. These are research topics, not sprint deliverables, and they create a false sense of safety. "Fuzzy-matches the quoted text against real content (Levenshtein distance <= 5%)" sounds precise but solves the wrong problem: the failure being remediated was not a hallucination (Claude did not fabricate file paths or scores). The failure was a rational degraded behavior in the absence of tooling. Deterministic scripts do not prevent rational degradation.

---

### Gerald Weinberg (Psychology of Programming, Human Factors, Cognitive Load)

#### Top Concern: The Spec Is Written for the Analyst, Not the Implementer

This sprint spec is a diagnostic artifact that has been extended into an implementation plan without changing its cognitive orientation. The first 43 lines are ranking tables with formulas. The next 100 lines are implementation tasks. The next 300 lines are a brainstorm addendum. The final 100 lines are verification tests. The implementer must mentally reconstruct the actual edit list from a mixture of diagnostic commentary, ranked alternatives, implementation instructions, and aspirational future work.

The cognitive load pattern is: "Here is why the problem exists (with evidence), here is how we scored the solutions (with formulas), here is what to do (buried in tables), here is what we dreamed about doing someday (in more detail than the actual work), here is how to check (partially automated, partially manual)."

An implementer reading this spec will ask: "What files do I edit, and what do I change in each one?" The answer requires extracting information from 5 tables across 3 epics, mentally deduplicating tasks 1.3, 1.4, and 2.2 (which the spec says are "a single coherent rewrite"), and ignoring the DVL section entirely. This is an error-prone pattern.

The spec also has a human-factors blind spot regarding who reads the modified files. The sc-roadmap SKILL.md is read by Claude, not by humans. The verb glossary (Task 2.1) and atomic sub-steps (Task 2.2) are instructions for an LLM. But the spec designs these instructions as if the reader is a human programmer who understands glossaries and cross-references. LLMs do not reliably follow indirection ("look up verb X in the glossary, then apply the tool mapping"). They follow inline instructions better than cross-referenced ones. The glossary may actually reduce Claude's compliance by adding a lookup step.

#### Specific Improvements

1. **Create an "Implementer's Summary" at the top of the spec.** Before any ranking tables, add a section titled "What To Do" with exactly this structure:
   ```
   File 1: src/superclaude/commands/roadmap.md
     Change: Add "Skill" to allowed-tools line

   File 2: src/superclaude/skills/sc-roadmap/SKILL.md
     Change A: Add "Skill" to allowed-tools line
     Change B: Add execution vocabulary section before Wave 0
     Change C: Rewrite Wave 2 step 3 as sub-steps 3a-3f with inline tool-call syntax and fallback
     Change D: Rewrite Wave 1A step 2 with same pattern

   File 3: src/superclaude/skills/sc-adversarial/SKILL.md
     Change: Add "Return Contract (MANDATORY)" section as final pipeline step

   File 4: src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md
     Change A: Convert pseudo-CLI syntax to Skill tool call format
     Change B: Add "Return Contract Consumption" section

   Post-edit: make sync-dev && make verify-sync
   ```
   This gives the implementer a complete picture in 15 lines.

2. **Inline the tool-call syntax instead of cross-referencing the glossary.** Instead of "Use Skill tool to invoke sc:adversarial (see glossary for verb mapping)," write the actual instruction Claude will see:
   ```
   3d. Use the Skill tool: skill: "sc:adversarial", args: "--source <spec> --generate roadmap --agents <expanded-agents> --depth <depth> --output <output-dir>"
   ```
   This eliminates a cognitive hop for both the implementer and Claude.

3. **Distinguish "Task 1.4 fallback" from "Task 2.2 fallback."** The spec creates the fallback protocol in Task 1.4 and references it again in Task 2.2. But Task 2.2 is supposed to be the "single coherent rewrite" that includes 1.3 and 1.4. The implementer must decide: do I implement 1.4 first and then merge into 2.2, or do I skip 1.4 and do it all in 2.2? The answer (do it all in 2.2) should be stated explicitly, with Task 1.4 marked as "specification only -- implemented as part of Task 2.2."

4. **Remove confidence scores from the risk register.** Risk R1 says "HIGH (0.40)." Is 0.40 high? The threshold is not defined. More importantly, these are fabricated precision on unknowns. Replace with qualitative assessments: "Risk R1: Task agents may not have access to the Skill tool. Mitigation: test before implementing. Fallback: use Task-agent-based inline pipeline."

#### What I Would Cut

- The solution ranking table (lines 19-29). The implementer does not need to know that S04 scored 0.806 and S02 scored 0.781. They need to know what to build.
- The "Excluded pairs" paragraph (line 43). Decisions about what NOT to build belong in a decision log, not in implementation instructions.
- All three sync tasks (1.5, 2.5, 3.5). One post-edit checklist.

---

## Panel Synthesis

### Consensus Improvements (All 4 Experts Agree)

1. **Add an empirical Skill tool probe as the very first task.** All four experts identified Risk R1 (Skill tool unavailability) as the make-or-break unknown. Brooks calls it the prerequisite; Lamport wants it to collapse uncertainty; Leveson identifies it as a safety-critical probe; Weinberg notes the 40% figure is fabricated precision. **Concrete change**: Add Task 0.0 -- dispatch a minimal Task agent that runs `Skill tool with skill: "sc:adversarial"` and record the result. If it fails, redesign the sprint around the fallback path only.

2. **Remove the DVL from the sprint spec.** All four experts agree the DVL is out of scope. Brooks calls it second-system effect. Lamport notes it conflates structural and behavioral compliance. Leveson says it creates false safety. Weinberg says it doubles the cognitive load of the document. **Concrete change**: Move lines 142-449 to a separate backlog document. Add one line in the sprint spec: "Future work: Deterministic Verification Layer (see backlog/dvl-spec.md)."

3. **Fix the `fallback_mode` schema inconsistency.** The sprint spec references `fallback_mode: true` in the return contract (Task 1.4) but does not include it in the schema definition (Task 3.1). **Concrete change**: Add `fallback_mode` (boolean, default false) as field 9 in Task 3.1. Update Task 3.2 to route on this field.

4. **Add an implementer's summary at the top.** All experts noted the spec is organized for analysis, not implementation. **Concrete change**: Add a "What To Do" section before the ranking tables listing the 4 files, the specific changes per file, and the post-edit checklist.

### Contested Points

**Glossary (Task 2.1): Keep or cut?**

- **Lamport and Weinberg say cut.** Lamport argues it adds indirection without value when instructions use explicit tool-call syntax. Weinberg argues LLMs follow inline instructions better than cross-referenced glossaries.
- **Brooks and Leveson say keep (but simplify).** Brooks sees conceptual integrity value in a consistent vocabulary across waves. Leveson notes that a glossary creates a reviewable contract between spec author and spec consumer.
- **Resolution**: Keep the glossary but make it a compact inline reference (4 rows, no separate section header). Ensure all instructions ALSO use inline tool-call syntax so the glossary is documentation, not a required lookup.

**Epic structure: Merge 1+2 or keep separate?**

- **Brooks says merge.** The atomic-rewrite constraint means they are one work unit.
- **Lamport says keep separate** with explicit ordering. Separation clarifies dependencies even when one author does both.
- **Leveson and Weinberg are neutral** -- they care about the probe task being first, not the internal epic structure.
- **Resolution**: Keep as separate epics for dependency clarity, but add explicit note: "Tasks 1.3, 1.4, and 2.2 are implemented as a single atomic edit. Task 2.2 is the implementation vehicle; 1.3 and 1.4 are specification inputs to 2.2."

### Final Recommendations

Ordered by `(impact * likelihood_of_success) / effort`:

| Rank | Recommendation | Impact | Success Likelihood | Effort | Score |
|------|---------------|--------|-------------------|--------|-------|
| 1 | Add Task 0.0: Skill tool probe | 0.95 | 0.95 | Low (1 Task agent dispatch) | 0.90 |
| 2 | Fix `fallback_mode` schema gap | 0.80 | 1.00 | Trivial (add 1 field) | 0.80 |
| 3 | Add implementer's summary | 0.70 | 1.00 | Low (15 lines) | 0.70 |
| 4 | Remove DVL from sprint spec | 0.65 | 0.90 | Low (move text) | 0.59 |
| 5 | Specify fallback state machine | 0.85 | 0.70 | Medium (define 5 states) | 0.60 |
| 6 | Differentiate fallback-partial from pipeline-partial | 0.75 | 0.85 | Low (add 1 field + routing) | 0.64 |
| 7 | Inline tool-call syntax (reduce glossary dependency) | 0.50 | 0.90 | Low (rewrite 6 sub-steps) | 0.45 |
| 8 | Add standalone sc:adversarial regression check | 0.60 | 0.80 | Low (1 test) | 0.48 |

### Confidence Votes

Each expert's confidence (0-100%) that the sprint, **as currently specified**, will fix the original failure:

| Expert | Confidence | Reasoning |
|--------|-----------|-----------|
| **Fred Brooks** | 55% | "The three core fixes are correct and sufficient. But the 40% Skill-tool-unavailability risk is unresolved, and the fallback path is underspecified. If the Skill tool works in Task agents, confidence rises to 85%. If it does not, the fallback path as specified has a 50/50 chance of producing correct output." |
| **Leslie Lamport** | 40% | "The specification contains an internal inconsistency (`fallback_mode` referenced but undefined) and the fallback state machine is not specified. These are the kinds of errors that cause silent failures in distributed systems. The primary-path probability is genuinely unknown, making the overall success probability hard to bound." |
| **Nancy Leveson** | 45% | "The 'already running' constraint is not analyzed. If it blocks the primary path, 100% of invocations go through an underspecified fallback. The blast radius analysis for sc:adversarial modifications is missing. Safety margins are inadequate for a system that fails silently." |
| **Gerald Weinberg** | 60% | "The implementer will likely figure out what to do despite the spec's organizational issues. The core changes are simple file edits. The risk is not that the edits are wrong, but that the implementer misses the coordination requirement between tasks 1.3/1.4/2.2 or implements the fallback protocol incorrectly due to underspecification." |

**Panel average**: 50% confidence.

**Primary confidence gap**: The unknown Skill tool behavior in Task agents. Resolving this single question would shift the panel average to 65-75%.

---

## Top 5 Changes to Make Before Implementation

### 1. Add Task 0.0: Empirical Skill Tool Probe

**Location**: Insert before Epic 1 in sprint-spec.md.

**Specific text to add**:

```markdown
## Task 0.0: Skill Tool Probe (Pre-Implementation Gate)

**Goal**: Empirically determine whether Task agents can use the Skill tool to invoke a named skill.

**Method**: Dispatch a single Task agent with this prompt: "Use the Skill tool with skill: 'sc:adversarial'. Report the exact result: success, error message, or tool not available."

**Decision gate**:
- If success: Primary path is viable. Proceed with Epic 1 as specified.
- If error "skill already running": Primary path blocked by caller constraint. Remove primary path from Epic 1. Implement fallback as the ONLY path. Update Task 1.4 to remove "fallback" framing -- it is the primary (and only) mechanism.
- If error "tool not available": Skill tool not accessible to Task agents. Same as above.
- If error "skill not found": sc:adversarial not installed. Fix installation, re-probe.

**Acceptance Criteria**: Decision gate result documented. Sprint plan updated if primary path non-viable.
```

### 2. Fix the `fallback_mode` Schema Inconsistency

**Location**: Task 3.1 in sprint-spec.md, field list.

**Current text** (line 93): "Define 7 fields: `schema_version: "1.0"`, `status` (...), `convergence_score` (...), `merged_output_path` (...), `artifacts_dir` (...), `unresolved_conflicts` (...), `base_variant` (...). ... Add `failure_stage` field... "

**Change to**: Add `fallback_mode` (boolean, default: false, set to true when pipeline was executed via inline Task agents instead of sc:adversarial skill invocation). Update field count from "8 fields (7 + failure_stage)" to "9 fields (7 + failure_stage + fallback_mode)".

**Also update**: Task 1.4 acceptance criteria to reference `fallback_mode: true` as a defined schema field (not an ad-hoc addition).

### 3. Add Implementer's Summary Section

**Location**: Insert immediately after the "Sprint Goal" section (before the Problem Ranking tables).

**Specific text to add**:

```markdown
## Implementer's Quick Reference

**4 files to edit, 1 post-edit step:**

| File | Changes |
|------|---------|
| `src/superclaude/commands/roadmap.md` | Add `Skill` to `allowed-tools` line |
| `src/superclaude/skills/sc-roadmap/SKILL.md` | (1) Add `Skill` to `allowed-tools`, (2) Add execution vocabulary before Wave 0, (3) Rewrite Wave 2 step 3 as sub-steps 3a-3f with Skill tool call + fallback + return contract routing, (4) Rewrite Wave 1A step 2 with same Skill tool pattern |
| `src/superclaude/skills/sc-adversarial/SKILL.md` | Add "Return Contract (MANDATORY)" section as final pipeline step with 9 fields |
| `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` | (1) Convert all pseudo-CLI syntax to Skill tool call format, (2) Add "Return Contract Consumption" section with status routing and missing-file guard |

**Post-edit**: `make sync-dev && make verify-sync`

**Critical coordination**: Tasks 1.3, 1.4, and 2.2 modify the same text (Wave 2 step 3). Implement as a single atomic edit via Task 2.2.
```

### 4. Relocate DVL to Separate Document

**Location**: Lines 142-449 of sprint-spec.md.

**Change**: Move the entire "Deterministic Verification Layer (DVL) -- Brainstorm Addendum" section to `.dev/releases/backlog/dvl-verification-layer/DVL-BRAINSTORM.md`.

**Replace with**:

```markdown
## Future Work: Deterministic Verification Layer

A brainstorm for programmatic verification scripts (10 scripts, 3 tiers) was produced during this diagnostic workflow. It is out of scope for this sprint.

See: `.dev/releases/backlog/dvl-verification-layer/DVL-BRAINSTORM.md`
```

### 5. Specify the Fallback Path State Machine

**Location**: Task 1.4 description in sprint-spec.md.

**Current text** (line 60): "Fallback: read `src/superclaude/skills/sc-adversarial/SKILL.md`, dispatch 5 sequential Task agents for each pipeline step (variant generation, diff analysis, single-round debate, base selection with scoring, merge with provenance)."

**Change to**:

```markdown
Fallback state machine (5 steps, sequential, hard-stop on any failure):

| Step | Task Agent Prompt Summary | Input | Output | Failure Action |
|------|--------------------------|-------|--------|----------------|
| F1: Variant Generation | Generate roadmap variants from spec using agent specs | Spec file + agent specs from `--agents` | `<output>/adversarial/variant-N-*.md` (one per agent) | Abort fallback. Return `status: failed, failure_stage: variant_generation` |
| F2: Diff Analysis | Compare all variants, produce diff-analysis.md | All variant files | `<output>/adversarial/diff-analysis.md` | Abort. `status: failed, failure_stage: diff_analysis` |
| F3: Single-Round Debate | One round of advocate statements + scoring matrix | Variants + diff-analysis.md | `<output>/adversarial/debate-transcript.md` | Abort. `status: failed, failure_stage: debate` |
| F4: Base Selection | Score variants, select base | Variants + debate-transcript.md | `<output>/adversarial/base-selection.md` | Abort. `status: failed, failure_stage: base_selection` |
| F5: Merge + Contract | Merge best elements, write return-contract.yaml | Base + all variants + base-selection.md | `<output>/adversarial/merged-output.md` + `<output>/adversarial/return-contract.yaml` with `status: partial, fallback_mode: true` | Abort. `status: failed, failure_stage: merge` |

Return-contract.yaml path: `<output-dir>/adversarial/return-contract.yaml` (must match the path checked in step 3e).
```

---

*Panel review generated 2026-02-23. Methodology: Independent expert analysis followed by structured synthesis with consensus/dissent tracking.*
