# Reflection: Sprint Specification for sc:roadmap Adversarial Pipeline Remediation

**Date**: 2026-02-23
**Reviewer**: claude-opus-4-6 (self-review agent)
**Input**: sprint-spec.md, 22 diagnostic artifacts, 4 source files

---

## 1. Prioritized Improvements

### HIGH Impact x LOW Effort

**IMP-01: Add prerequisite validation task (Task 0.1) before all 15 tasks**

The sprint's entire primary path depends on an unvalidated assumption: that the Skill tool can be invoked from within a running skill context. The Skill tool's own description states it is for invoking "a skill within the main conversation." There is no evidence that a Task agent (subagent) can access the Skill tool, and no precedent in the codebase for cross-skill invocation.

Risk R1 acknowledges this (probability 0.40) and proposes an "empirical test before full implementation" -- but this test is not a sprint task. It lives only in the mitigation column of the risk register. If R1 materializes, the primary path in Epic 1 Task 1.3 becomes dead code, and the entire sprint pivots to the fallback protocol (Task 1.4).

**Specific change to sprint-spec.md**: Add a new Task 0.1 before Epic 1:

```
## Task 0.1: Prerequisite Validation — Skill Tool Cross-Invocation Test

**Goal**: Determine whether the Skill tool can be called from within a running skill.

**Method**:
1. In a Claude Code session, invoke any installed skill (e.g., sc:adversarial with minimal args)
2. During that skill's execution, attempt to call the Skill tool with `skill: "sc:adversarial"`
   (or any other skill)
3. Record: Does the Skill tool execute? Does it return an error? Which error?
4. Additionally test: Can the MAIN agent (not a Task subagent) call the Skill tool
   to invoke sc:adversarial while sc:roadmap is executing?

**Decision gate**:
- If Skill tool works from main agent context: primary path is viable; proceed with Epic 1 as written
- If Skill tool works only from main agent (not Task agents): rewrite Task 1.3 to use
  direct Skill tool call instead of Task-agent-mediated call
- If Skill tool cannot invoke a second skill while one is running: PIVOT — promote the
  fallback protocol (Task 1.4) to primary path, demote Skill-based invocation to aspirational

**Time cost**: <15 minutes
**Blocks**: All of Epic 1
```

### HIGH Impact x MEDIUM Effort

**IMP-02: Consider direct Skill tool invocation instead of Task-agent-mediated invocation**

The sprint assumes: sc:roadmap -> Task agent -> Skill tool -> sc:adversarial. But there is a simpler path: sc:roadmap -> Skill tool -> sc:adversarial (direct call from the main agent, no Task agent intermediary). This eliminates the R1 risk entirely because the main agent definitionally has access to all tools, including Skill.

The reason the sprint uses Task agents is not stated. If the intent is parallel execution or context isolation, that rationale should be documented. If there is no specific reason, the simpler direct-call path should be the primary approach.

**Specific change**: In Epic 1 Task 1.3, add an alternative path:

```
Option A (preferred if Task 0.1 confirms): Direct Skill tool call from main agent
  - In Wave 2 step 3d, the main sc:roadmap agent calls the Skill tool directly:
    skill: "sc:adversarial", args: "--source <spec> --generate roadmap --agents <agents> ..."
  - No Task agent intermediary needed
  - sc:adversarial runs as a sub-skill, returns control to sc:roadmap when complete
  - Return contract consumed via file read after Skill tool returns

Option B (fallback): Task-agent-mediated invocation
  - As currently specified in Task 1.3
```

**IMP-03: Resolve the pseudo-CLI paradox in Epic 2 Task 2.4**

Task 2.4 calls for eliminating all `sc:adversarial --compare ...` pseudo-CLI syntax from `adversarial-integration.md` and converting to Skill tool call format. But the Skill tool's `args` parameter IS a string that looks like CLI arguments. The "Invocation Patterns" section of adversarial-integration.md shows:

```
sc:adversarial --compare spec1.md,spec2.md --depth standard --output .dev/releases/current/auth-system/
```

If the fix is to convert this to:

```yaml
skill: "sc:adversarial"
args: "--compare spec1.md,spec2.md --depth standard --output .dev/releases/current/auth-system/"
```

Then the pseudo-CLI syntax is preserved INSIDE the args string -- which is correct and expected. The task as written may cause the implementer to over-convert, removing the flag-based argument format that the Skill tool actually requires.

**Specific change**: Rewrite Task 2.4 acceptance criteria:

```
Before: "Zero instances of `sc:adversarial --` pseudo-CLI syntax remain in the file"
After:  "All standalone invocation examples (outside of Skill tool `args` context) are
         wrapped in Skill tool call format. The args string within Skill tool calls
         MAY contain `--flag` syntax as this is the correct argument passing mechanism."
```

### HIGH Impact x HIGH Effort

**IMP-04: The fallback protocol (Task 1.4) should be the primary implementation target**

Given R1's 0.40 probability (and my assessment that it's higher -- closer to 0.60 based on the "skill already running" constraint and Task agent tool access limitations), the fallback protocol is the path most likely to actually execute in production. Yet it receives less specification detail than the primary path.

Task 1.4 specifies "5 sequential Task agents for each pipeline step" but does not specify the prompts, the inter-agent data passing mechanism, or how the 5 agents map to sc:adversarial's 5-step protocol (diff analysis, debate, scoring, refactoring, merge). This is the same level of under-specification that caused the original failure.

**Specific change**: Expand Task 1.4 with the same level of detail as sc:adversarial's SKILL.md Step 1-5 definitions. Each of the 5 fallback Task agents needs: prompt template, input data specification, output artifact path, and pass/fail criteria.

### MEDIUM Impact x LOW Effort

**IMP-05: Add cross-reference validation between Epic 2 and Epic 3 schemas**

Epic 2 Task 2.2 step 3e references the return contract fields (status, convergence_score) and routing logic. Epic 3 Task 3.1 defines the canonical schema (8 fields including failure_stage). These must be consistent. The current spec relies on the implementer to maintain consistency across epics.

**Specific change**: Add a verification step after both epics complete:

```
Verification Test 3.5: Cross-reference the field list in Wave 2 step 3e (consumer)
against the field list in sc:adversarial Return Contract section (producer).
All fields referenced by the consumer must exist in the producer schema.
The convergence threshold in step 3e (0.6) must match the threshold in
adversarial-integration.md status routing (60%).
```

**IMP-06: The `unresolved_conflicts` type is inconsistent**

In sc:adversarial SKILL.md (line 349), `unresolved_conflicts` is typed as `list[string]` (a list of conflict descriptions). In the sprint spec Task 3.1, it is typed as `integer`. In adversarial-integration.md (line 151), it is typed as `integer`. The producer says list, the consumers say integer.

**Specific change**: Resolve the type. Recommend: change sc:adversarial SKILL.md to `integer` (count of unresolved conflicts) for simplicity, since neither consumer uses the list contents. Or change both consumers to `list[string]` if the descriptions are valuable. Document the decision in Task 3.1.

### MEDIUM Impact x MEDIUM Effort

**IMP-07: Reorder implementation for faster validation**

Current order: Epic 1 (wiring) -> Epic 2 (spec rewrite) -> Epic 3 (return contract).

Proposed order: Task 0.1 (prerequisite test) -> Epic 1 Tasks 1.1-1.2 (add Skill to allowed-tools) -> Epic 3 (return contract) -> Epic 1 Tasks 1.3-1.4 + Epic 2 (spec rewrite as unified effort).

Rationale: Epic 3 is independent and defines the contract that Epic 2 references. Implementing Epic 3 first means the Epic 2 implementer has a concrete schema to reference instead of a forward reference.

### LOW Impact x LOW Effort

**IMP-08: Add `schema_version` to the sprint spec's return contract example**

The ranked-root-causes.md "Fix 3" example YAML block shows 6 fields but omits `schema_version`. Sprint spec Task 3.1 correctly specifies 8 fields (7 + failure_stage). No change needed to sprint-spec.md, but the ranked-root-causes.md example could confuse implementers who reference both documents.

---

## 2. Kill List — Simplify or Remove

### DVL Scripts to Cut or Defer

| Script | Verdict | Rationale |
|--------|---------|-----------|
| `verify_allowed_tools.py` | KEEP | Highest value, simplest implementation, directly validates Epic 1 |
| `validate_return_contract.py` | KEEP | Highest value, validates Epic 3 acceptance criteria |
| `validate_wave2_spec.py` | KEEP | Validates Epic 2 structural compliance |
| `verify_pipeline_completeness.sh` | DEFER | Only useful after end-to-end test; not needed during sprint |
| `dependency_gate.sh` | DEFER | Overkill for 3 epics with clear human-managed ordering |
| `content_hash_tracker.py` | CUT | Risk R5 (concurrent modification) is mitigated by single-author constraint; hash tracking is redundant |
| `verify_numeric_scores.py` | CUT | No numeric scoring occurs in this sprint's deliverables |
| `check_file_references.py` | DEFER | Useful for general quality but not sprint-critical |
| `generate_checkpoint.py` | DEFER | Checkpoints are a workflow improvement, not a fix for the adversarial pipeline |
| `context_rot_canary.py` | CUT | Task fingerprint echoing is novel but untested; high implementation effort for speculative benefit |

**Summary**: Keep 3 scripts, defer 4, cut 3. This reduces DVL from 10 scripts to 3 for the sprint, with 4 candidates for a follow-up sprint.

### Anti-Hallucination Techniques to Defer

All 6 AH techniques (AH-1 through AH-6) should be deferred. They are design patterns for future DVL scripts, not deliverables for this sprint. The sprint-spec.md already marks the DVL as "BRAINSTORM ONLY" which is correct, but the 6 AH techniques add 50+ lines of specification to a brainstorm addendum. They should be moved to a separate `dvl-design-notes.md` to reduce sprint-spec.md cognitive load.

### Sprint Sync Tasks

Tasks 1.5, 2.5, and 3.5 (all `make sync-dev`) are mechanical. They should be a single post-sprint task, not three separate tasks. Running sync after each epic risks merge issues if epics are implemented in parallel (as the spec allows for Epic 2 and Epic 3).

**Recommendation**: Replace Tasks 1.5, 2.5, 3.5 with a single Task 4.1: "Run `make sync-dev && make verify-sync` after all code changes are complete."

This reduces the task count from 15 to 13 (minus 3 sync tasks, plus Task 0.1, plus consolidated Task 4.1).

---

## 3. DVL Feasibility Assessment — Top 3 Scripts by Value/Effort Ratio

### Tier 1: `verify_allowed_tools.py`

**Feasibility**: HIGH. Parsing frontmatter from markdown is trivial (regex for `^allowed-tools:` line, split on comma, check membership). Pure Python stdlib, zero dependencies.

**Value**: Directly validates the acceptance criteria for Epic 1 Tasks 1.1 and 1.2. Catches regression if allowed-tools is accidentally modified later.

**Effort**: ~30 minutes to implement and test. ~20 lines of Python.

**Verdict**: Implement during sprint.

### Tier 2: `validate_return_contract.py`

**Feasibility**: HIGH. YAML parsing requires PyYAML (noted as available). Schema validation is straightforward field-presence + type checking.

**Value**: Directly validates Epic 3 acceptance criteria. Reusable for every future sc:adversarial invocation. Catches the exact class of error (malformed/missing return contract) that caused silent degradation in the original failure.

**Effort**: ~1 hour. ~60 lines of Python.

**Verdict**: Implement during sprint.

### Tier 3: `validate_wave2_spec.py`

**Feasibility**: MEDIUM. Parsing markdown for "Wave 2 step 3" sub-steps requires structural assumptions about heading format. The verb glossary extraction is fragile -- it depends on a specific table format. Changes to the SKILL.md structure could break the validator.

**Value**: Validates Epic 2 Task 2.2 acceptance criteria. Catches spec drift. But this validator has a shorter useful life than the other two because it validates a document that changes infrequently after the sprint.

**Effort**: ~2 hours. ~100 lines of Python with regex-heavy parsing.

**Verdict**: Implement if time permits; a manual checklist (already in Verification Test 2) is an acceptable substitute.

---

## 4. Integration Blind Spots

### Epic 2 / Epic 3 Boundary

Epic 2 Task 2.2 step 3e specifies return contract routing logic that references fields defined in Epic 3 Task 3.1. The step 3e text includes:

- `status` field routing (success/partial/failed)
- `convergence_score` threshold (0.6)
- Missing-file guard

Epic 3 Task 3.1 defines the canonical schema with 8 fields. The boundary risk: if Epic 3 changes the field names, types, or adds conditional fields, Epic 2's routing logic becomes stale.

**Current mitigation**: Cross-reference comments (Tasks 3.3 and 3.4). This is necessary but not sufficient. The comments are passive -- they require a human to notice and act on divergence.

**Recommended additional mitigation**: Add a single-line comment in Wave 2 step 3e: `# Contract schema: see src/superclaude/skills/sc-adversarial/SKILL.md, Return Contract section`. This makes the dependency explicit in the consuming code, not just in the reference document.

### Epic 1 / Epic 2 Overlap

The sprint correctly identifies that Tasks 1.3, 1.4, and 2.2 all modify Wave 2 step 3 and must be a single atomic rewrite. But the task numbering (1.3 in Epic 1, 2.2 in Epic 2) implies sequential implementation by potentially different authors. The "Critical coordination point" note in the Implementation Order section addresses this, but it is buried at the bottom of the section.

**Recommendation**: Merge Tasks 1.3, 1.4, and 2.2 into a single task ("Task 1.3: Rewrite Wave 2 step 3 with Skill invocation, fallback, atomic sub-steps, and glossary verbs") owned by one author. This eliminates the coordination risk entirely.

### adversarial-integration.md Dual Role

`adversarial-integration.md` is modified by both Epic 2 (Task 2.4: pseudo-CLI conversion) and Epic 3 (Task 3.2: return contract consumption section). If implemented in parallel, these changes could conflict.

**Recommendation**: Sequence Task 3.2 before Task 2.4, since Task 3.2 adds a new section (no conflict risk) while Task 2.4 modifies existing sections.

---

## 5. Prerequisite Test

**The single cheapest experiment that validates or invalidates the entire approach:**

Open a Claude Code session. Invoke any installed skill (for example, if sc:adversarial is installed, invoke it with minimal args -- even if it fails due to missing required flags, the test is whether the Skill tool ACCEPTS the call). Then, within the same session, while the first skill is conceptually "active" (or after it completes), attempt to invoke a second skill via the Skill tool.

Specifically:

```
Step 1: /sc:adversarial --compare nonexistent1.md,nonexistent2.md
   (This will fail, but the Skill tool call itself should succeed or produce
   a specific error about files not found -- NOT about Skill tool unavailability)

Step 2: From within a skill execution context, attempt:
   Skill tool call: skill: "sc:adversarial", args: "--compare test1.md,test2.md"

   Observe: Does the Skill tool execute? Or does it return:
   a) "Do not invoke a skill that is already running"
   b) "Tool not available"
   c) Success (skill starts executing)
```

**Time cost**: 5-10 minutes.

**Decision impact**:
- If (c): The primary path works. Proceed with sprint as written.
- If (a): The "skill already running" constraint blocks cross-skill invocation. The fallback protocol becomes the ONLY viable path. Eliminate Tasks 1.1, 1.2, 1.3 (Skill tool in allowed-tools is irrelevant). Rewrite the sprint around the fallback protocol as the primary mechanism.
- If (b): Task agents cannot access the Skill tool. Test whether the MAIN agent can call Skill directly (without Task agent intermediary). If yes, rewrite Task 1.3 for direct invocation. If no, same as (a).

---

## 6. Failure Modes NOT Covered

1. **sc:adversarial execution timeout**: The adversarial pipeline involves multiple debate rounds with multiple agents. A 3-agent, 3-round deep debate could take 10+ minutes. The sprint spec has no timeout handling for the Skill tool call to sc:adversarial. If the skill times out mid-execution, the return contract may not be written (contradicting the "write even on failure" instruction).

2. **Context window exhaustion during sc:adversarial**: The adversarial pipeline is context-heavy (multiple full-text variants loaded simultaneously). If sc:adversarial exhausts its context window mid-pipeline, the behavior is undefined. The return contract "write on failure" instruction may not execute if the agent cannot process any more tokens.

3. **Partial file writes**: If sc:adversarial writes return-contract.yaml but crashes before completing the write, the file may be malformed YAML. `validate_return_contract.py` catches this, but only if it runs. The sprint's fallback routing (step 3e) reads the file directly -- it should attempt YAML parsing and treat parse errors as `status: failed`.

4. **Recursive skill invocation**: If a user invokes `sc:roadmap` which invokes `sc:adversarial` which (for some reason) attempts to invoke another skill, the chain could hit platform limits. The sprint does not address invocation depth limits.

5. **Deferred root causes surfacing**: RC3 (agent dispatch) and RC5 (Claude behavioral interpretation) are deferred. If the primary path works but Claude still selects the wrong agent WITHIN sc:adversarial (debate-orchestrator vs. system-architect), the pipeline could produce degraded output despite all three epics being complete. This is a second-order failure that the sprint explicitly defers but does not flag as a post-sprint monitoring item.

---

## 7. Confidence Assessment

**Probability that the sprint as specified will fix the original failure on first attempt: 45%**

Breakdown:

| Factor | Probability | Rationale |
|--------|------------|-----------|
| Skill tool cross-invocation works | 0.40 | No precedent; "already running" constraint unclear; Task agent tool access unknown |
| Fallback protocol adequate if primary fails | 0.75 | Well-designed but under-specified (no agent prompts) |
| Return contract written correctly by sc:adversarial | 0.70 | "MANDATORY" language helps but LLM compliance with write-on-failure is uncertain |
| Spec rewrite eliminates ambiguity | 0.85 | Glossary + atomic sub-steps is a strong approach |
| End-to-end pipeline produces correct output | 0.55 | Compound probability of all components working together |

**Composite**: The sprint addresses the right problems in the right order. The diagnostic work is thorough and the root cause analysis is sound. The primary risk is that the foundational assumption (Skill tool cross-invocation) has not been tested, and 40% of the sprint's effort (Epic 1 primary path, Epic 2 Skill tool references) depends on it. If the prerequisite test (Section 5) is performed first and the sprint is adapted based on results, confidence rises to **70%**.

**With prerequisite test + fallback-first implementation + the 3 recommended DVL scripts**: **75%**.

The remaining 25% gap comes from:
- LLM behavioral compliance with write-on-failure instructions (~10%)
- Untested interaction between sc:roadmap and sc:adversarial context windows (~8%)
- Deferred root causes RC3/RC5 surfacing as second-order failures (~7%)

---

*Reflection performed 2026-02-23. Analyst: claude-opus-4-6 (self-review agent).*
*Method: Source file analysis, sprint-spec structural review, prerequisite validation, DVL feasibility assessment.*
