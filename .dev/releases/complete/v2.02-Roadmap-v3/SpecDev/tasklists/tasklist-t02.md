# Tasklist: T02 Synthesis Amendments to sprint-spec.md

> **Source**: T02-synthesis.md (Adversarial Debate Results — Sprint-Spec vs Root Causes)
> **Target**: sprint-spec.md
> **Generated**: 2026-02-23
> **Scope**: All gaps G1–G11 (Critical + Important) from T02-synthesis.md §5

---

## Task 1: Fix missing-file guard contradiction (G1)

**Source reference**: T02-synthesis.md §5, Critical gap G1
**Location in sprint-spec.md**: Epic 2, Task 2.2 (line 113), specifically the step 3e description
**Also touches**: Epic 3, Task 3.2 (line 130), the missing-file guard text

**Change**: Task 2.2 step 3e currently reads:

> step 3e includes guard for missing return-contract.yaml ("If not found, treat as status: partial with convergence_score: 0.0")

BEFORE (in Task 2.2 acceptance criteria, line 113):
```
step 3e includes guard for missing return-contract.yaml ("If not found, treat as status: partial with convergence_score: 0.0")
```

AFTER:
```
step 3e includes guard for missing return-contract.yaml ("If not found, treat as status: failed with failure_stage: 'transport'")
```

Additionally, in Task 3.2 (line 130), the Guard clause currently reads:

BEFORE:
```
Guard: "If return-contract.yaml does not exist, treat as status: failed with failure_stage: 'transport'."
```

This is already consistent with the G1 fix. No change needed to Task 3.2 — the contradiction is only in Task 2.2 step 3e. Verify both are aligned after edit.

Also update the Definition of Done line 207 to match:

BEFORE (line 207):
```
Return contract read instruction and status routing exist in `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md` with missing-file guard, convergence threshold, and `fallback_mode` differentiated warning
```

No change needed here — this line does not specify the status value. The fix is confined to Task 2.2 step 3e's parenthetical.

---

## Task 2: Add fallback protocol validation test (G2)

**Source reference**: T02-synthesis.md §5, Critical gap G2
**Location in sprint-spec.md**: Verification Plan section, after Test 5 (insert before the closing `---` at line 297)

**Change**: Insert a new Verification Test 6 after Test 5 (line 295).

INSERT AFTER the Test 5 section (after line 295, before the `---` at line 297):

```markdown
### Test 6: Fallback Protocol Validation

**Purpose**: Confirm the fallback protocol (F1-F5) produces valid output and a well-formed return-contract.yaml.

**Method**: Run the fallback protocol on a test input with Skill tool deliberately unavailable (or simulate error).

1. Provide a minimal spec file and 2 agent specifications as input
2. Execute F1-F5 sequentially
3. Verify each step produces its expected output artifact
4. Verify `return-contract.yaml` is written with `status: partial`, `fallback_mode: true`, and valid schema
5. Verify a failure mid-pipeline (e.g., abort at F3) produces `return-contract.yaml` with `status: failed` and correct `failure_stage`

**Expected**: All 5 fallback steps produce artifacts; return-contract.yaml has valid schema on both success and mid-pipeline failure paths.
```

Also add a corresponding DoD checkbox. INSERT after line 223:

```
- [ ] Verification Test 6 passes (fallback protocol validation)
```

**Potential conflict**: T04-synthesis.md Optimization 4 proposes conditionally deferring this test (replace full G2 with lightweight smoke test if Task 0.0 returns "primary path viable"). Resolve during execution: if Opt 4 is adopted, replace Test 6 with the smoke test variant specified in T04-synthesis.md §Optimization 4.

---

## Task 3: Add fallback-only sprint variant (G3)

**Source reference**: T02-synthesis.md §5, Critical gap G3
**Location in sprint-spec.md**: After Task 0.0 section (insert after line 81, before Epic 1)

**Change**: Insert a new section documenting task modifications when primary path is confirmed non-viable.

INSERT AFTER line 81 (after Task 0.0's closing `---`), BEFORE Epic 1 heading:

```markdown
## Fallback-Only Sprint Variant

**Trigger**: Task 0.0 decision gate returns "primary path blocked" (Skill tool cannot invoke a second skill while one is running, or Skill tool not accessible to Task agents and main agent also fails).

**Task modifications when fallback is the ONLY invocation mechanism**:

| Task | Modification |
|------|-------------|
| 1.1 | Keep — `Skill` in allowed-tools is still needed for future enablement |
| 1.2 | Keep — same rationale |
| 1.3 | **Remove** — primary Skill invocation path is non-functional |
| 1.4 | **Promote to primary** — fallback protocol becomes the only invocation mechanism; remove "fallback" framing, rename to "Inline Adversarial Execution" |
| 2.1 | Keep — glossary still applies to fallback verbs |
| 2.2 | **Simplify** — sub-steps 3a-3c remain; 3d becomes the inline execution (no Skill tool call); 3e-3f remain |
| 2.3 | **Simplify** — Wave 1A step 2 uses inline execution, no Skill tool call |
| 2.4 | Keep — pseudo-CLI conversion still needed |
| 3.1 | Keep — return contract still needed (fallback writes it too) |
| 3.2 | **Adjust** — missing-file guard remains; `fallback_mode` will always be `true` |
| 3.3, 3.4 | Keep |

**Acceptance Criteria**: Sprint plan updated within 30 minutes of Task 0.0 decision. All "Remove" and "Simplify" modifications applied before implementation begins.
```

**Potential conflict**: T04-synthesis.md Optimization 4 also addresses probe-result-dependent behavior. Resolve during execution: G3 provides the structural variant plan, Opt 4 governs what validation is deferred. Both can coexist.

---

## Task 4: Clarify step 3c tool-call specification (G4)

**Source reference**: T02-synthesis.md §5, Important gap G4
**Location in sprint-spec.md**: Epic 2, Task 2.2 (line 113), sub-step 3c description

**Change**: The current sub-step 3c text is:

BEFORE (within Task 2.2 Change column, line 113):
```
(3c) If agents list length >= 3, add debate-orchestrator to coordination role
```

AFTER:
```
(3c) If agents list length >= 3, add debate-orchestrator to coordination role (design-time decision: the orchestrating agent reads `sc-adversarial/refs/debate-orchestrator.md` as behavioral context; this is NOT a separate Task agent dispatch or an args flag — it is a context-loading instruction for the agent that executes step 3d)
```

---

## Task 5: Add convergence sentinel for fallback mode (G5)

**Source reference**: T02-synthesis.md §5, Important gap G5
**Location in sprint-spec.md**: Two locations — Epic 1 Task 1.4 (line 97) and Epic 2 Task 2.2 step 3e (line 113)

**Change 5a**: In Task 1.4 (line 97), the F5 step currently specifies:

BEFORE (within Task 1.4, F5 description):
```
`status: partial, fallback_mode: true`
```

AFTER:
```
`status: partial, fallback_mode: true, convergence_score: 0.5` (fixed sentinel — estimated, not measured; single-round debate cannot produce meaningful convergence)
```

**Change 5b**: In Task 2.2 step 3e (line 113), add a note about fallback convergence:

INSERT into step 3e description after "partial -> warn and proceed if convergence >= 0.6":
```
(Note: fallback mode returns convergence_score: 0.5 as a fixed sentinel. This is below the 0.6 threshold, so fallback-mode partial results will trigger the warn-and-proceed path only if the threshold is adjusted or the consumer explicitly accepts fallback output regardless of convergence.)
```

**Implementation note**: This sentinel value means fallback output will NOT pass the 0.6 convergence gate by default. The implementer must decide: (a) lower the threshold for fallback mode, (b) add a separate fallback-mode routing branch in step 3e, or (c) accept that fallback output always triggers the "abort" path. Per T02-synthesis.md, option (b) is recommended — route on `fallback_mode: true` before checking convergence.

---

## Task 6: Add glossary scope statement (G6)

**Source reference**: T02-synthesis.md §5, Important gap G6
**Location in sprint-spec.md**: Epic 2, Task 2.1 (line 112)

**Change**: Task 2.1 currently describes the glossary as:

BEFORE (line 112, Task 2.1 Change column):
```
Insert a new "Execution Vocabulary" section before Wave 0 containing a mapping table: "Invoke skill" = Skill tool call, "Dispatch agent" = Task tool call, "Read ref" = Read tool call on refs/ path, "Write artifact" = Write tool call.
```

AFTER:
```
Insert a new "Execution Vocabulary" section before Wave 0 containing a mapping table: "Invoke skill" = Skill tool call, "Dispatch agent" = Task tool call, "Read ref" = Read tool call on refs/ path, "Write artifact" = Write tool call. **Scope**: This glossary covers tool-call verbs used in pipeline orchestration steps (Wave 0-4). It does NOT cover prose descriptions, comments, or documentation references — only actionable step instructions that the executing agent must interpret as tool operations.
```

---

## Task 7: Extend glossary consistency to fallback protocol (G7)

**Source reference**: T02-synthesis.md §5, Important gap G7
**Location in sprint-spec.md**: Quality Gates section, Definition of Done (lines 215-217)

**Change**: Add a new DoD checkbox after line 217.

INSERT after line 217 ("Fallback trigger covers three error types..."):
```
- [ ] Fallback steps F1-F5 use glossary-consistent verbs (each step's action verb appears in the Execution Vocabulary glossary)
```

Also add to Task 2.1 acceptance criteria (line 112), append to the existing AC:

BEFORE (end of Task 2.1 AC):
```
glossary appears before Wave 0
```

AFTER:
```
glossary appears before Wave 0; glossary verbs are also used in fallback protocol steps F1-F5
```

---

## Task 8: Add minimum quality threshold for fallback output (G8)

**Source reference**: T02-synthesis.md §5, Important gap G8
**Location in sprint-spec.md**: Epic 1, Task 1.4 (line 97), within the fallback protocol description

**Change**: INSERT a quality threshold statement at the end of the Task 1.4 fallback description, before the acceptance criteria sentence.

INSERT before "Fallback covers all three Skill tool error types" (the AC sentence at end of line 97):
```
**Minimum fallback quality threshold**: A successful fallback execution (F1-F5 all pass) MUST produce at minimum: 2 roadmap variants (F1), 1 diff analysis document (F2), 1 debate transcript with scoring (F3), 1 base selection with rationale (F4), and 1 merged output (F5). If any artifact is empty or trivially short (<100 words for analysis artifacts), treat as step failure and abort with appropriate `failure_stage`.
```

---

## Task 9: Add debate-orchestrator bootstrap instruction (G9)

**Source reference**: T02-synthesis.md §5, Important gap G9
**Location in sprint-spec.md**: Two locations

**Change 9a**: In Epic 2, Task 2.2 (line 113), sub-step 3c, add bootstrap instruction. This builds on the Task 4 change above.

Append to the revised 3c text (from Task 4 of this tasklist):
```
The executing agent MUST Read `src/superclaude/skills/sc-adversarial/refs/debate-orchestrator.md` before dispatching adversarial steps. This file provides the behavioral context for multi-agent debate coordination.
```

**Change 9b**: Add a note to the Definition of Done. INSERT after the "Verb-to-tool glossary exists" checkbox (line 202):
```
- [ ] Sub-step 3c includes debate-orchestrator bootstrap read instruction (Read tool call on refs/debate-orchestrator.md)
```

---

## Task 10: Add behavioral anchoring for F2/F3 fallback agents (G9a)

**Source reference**: T02-synthesis.md §5, Important gap G9a
**Location in sprint-spec.md**: Epic 1, Task 1.4 (line 97), within F2 and F3 descriptions

**Change**: In Task 1.4 line 97, modify the F2 and F3 step descriptions.

BEFORE (F2 in Task 1.4):
```
**F2 Diff Analysis** — dispatch Task agent to compare all variants. Input: all variant files. Output: `<output>/adversarial/diff-analysis.md`. Failure: abort, `failure_stage: diff_analysis`.
```

AFTER:
```
**F2 Diff Analysis** — dispatch Task agent to compare all variants. Agent prompt preamble: "You are performing Step 2 of the sc:adversarial pipeline in fallback mode. Your output MUST follow the diff-analysis format defined in sc:adversarial SKILL.md Step 2." Input: all variant files. Output: `<output>/adversarial/diff-analysis.md`. Failure: abort, `failure_stage: diff_analysis`.
```

BEFORE (F3 in Task 1.4):
```
**F3 Single-Round Debate** — dispatch Task agent for one round of advocate statements + scoring. Input: variants + diff-analysis. Output: `<output>/adversarial/debate-transcript.md`. Failure: abort, `failure_stage: debate`.
```

AFTER:
```
**F3 Single-Round Debate** — dispatch Task agent for one round of advocate statements + scoring. Agent prompt preamble: "You are performing a simplified Step 3 of the sc:adversarial pipeline in fallback mode. Your output MUST follow the debate transcript format defined in sc:adversarial SKILL.md Step 3, but limited to a single round." Input: variants + diff-analysis. Output: `<output>/adversarial/debate-transcript.md`. Failure: abort, `failure_stage: debate`.
```

**Potential conflict**: T04-synthesis.md Optimization 3 proposes merging F2+F3 into a single step (F2/3). If Opt 3 is adopted, the behavioral anchoring preambles from this task must be preserved in the merged step's prompt. Resolve during execution.

---

## Task 11: Add convergence threshold rationale (G10)

**Source reference**: T02-synthesis.md §5, Important gap G10
**Location in sprint-spec.md**: Epic 2, Task 2.2 (line 113), step 3e description

**Change**: The convergence threshold 0.6 is mentioned but not justified.

BEFORE (within step 3e, line 113):
```
partial -> warn and proceed if convergence >= 0.6
```

AFTER:
```
partial -> warn and proceed if convergence >= 0.6 (rationale: 0.6 represents majority agreement across variants — below this threshold, disagreements are too significant to produce a reliable merged output; this threshold is a tunable parameter and may be adjusted based on empirical results)
```

---

## Task 12: Add YAML example block to consumer specification (G11)

**Source reference**: T02-synthesis.md §5, Important gap G11
**Location in sprint-spec.md**: Epic 3, Task 3.2 (line 130)

**Change**: Task 3.2 does not require a YAML example in its current acceptance criteria.

BEFORE (end of Task 3.2 AC, line 130):
```
`fallback_mode` routing with differentiated user warning
```

AFTER:
```
`fallback_mode` routing with differentiated user warning; includes example YAML block showing a successful return contract and a failed return contract for implementer reference
```

---

## Completeness Verification

### All T02 gaps accounted for:

| Gap | Task | Status |
|-----|------|--------|
| G1 (Critical) | Task 1 | Covered — missing-file guard contradiction resolved |
| G2 (Critical) | Task 2 | Covered — fallback validation test added |
| G3 (Critical) | Task 3 | Covered — fallback-only sprint variant added |
| G4 (Important) | Task 4 | Covered — step 3c tool-call ambiguity clarified |
| G5 (Important) | Task 5 | Covered — convergence sentinel in fallback |
| G6 (Important) | Task 6 | Covered — glossary scope statement |
| G7 (Important) | Task 7 | Covered — fallback glossary consistency |
| G8 (Important) | Task 8 | Covered — fallback quality threshold |
| G9 (Important) | Task 9 | Covered — debate-orchestrator bootstrap |
| G9a (Important) | Task 10 | Covered — F2/F3 behavioral anchoring |
| G10 (Important) | Task 11 | Covered — convergence threshold rationale |
| G11 (Important) | Task 12 | Covered — YAML example block |
| G12 (Deferred) | N/A | Correctly deferred per T02-synthesis.md |
| G13 (Deferred) | N/A | Correctly deferred per T02-synthesis.md |
| G14 (Deferred) | N/A | Correctly deferred per T02-synthesis.md |
| G15 (Deferred) | N/A | Correctly deferred per T02-synthesis.md |

### Location verification in sprint-spec.md:

| Sprint-spec location | Referenced by tasks | Verified exists |
|----------------------|--------------------|----|
| Task 2.2 step 3e (line 113) | Tasks 1, 5b, 11 | Yes |
| Task 1.4 fallback F1-F5 (line 97) | Tasks 5a, 8, 10 | Yes |
| Task 2.1 (line 112) | Tasks 6, 7 | Yes |
| Task 3.2 (line 130) | Tasks 1 (cross-check), 12 | Yes |
| Verification Plan (after line 295) | Task 2 | Yes |
| Definition of Done (lines 200-224) | Tasks 2, 7, 9 | Yes |
| After Task 0.0 (after line 81) | Task 3 | Yes |
| Quality Gates (lines 213-217) | Task 7 | Yes |

### Potential conflicts with other review documents:

| Task | Conflict source | Nature | Resolution guidance |
|------|----------------|--------|-------------------|
| Task 2 (G2) | T04-synthesis.md Opt 4 | Opt 4 proposes conditionally deferring full G2 validation, replacing with smoke test if primary path viable | Apply G2 first; if Opt 4 is adopted later, downgrade Test 6 to smoke test variant |
| Task 3 (G3) | T04-synthesis.md Opt 4 | Both address probe-dependent behavior | Complementary, not conflicting — G3 is structural variant, Opt 4 is validation deferral |
| Task 10 (G9a) | T04-synthesis.md Opt 3 | Opt 3 merges F2+F3 into single step | Preserve behavioral anchoring preambles in merged step |
| Tasks 4, 9 (G4, G9) | reflection-final.md IMP-02 | IMP-02 proposes direct Skill invocation (no Task agent), which changes step 3c/3d semantics | If IMP-02 is adopted, 3c bootstrap instruction still applies but "coordination role" framing changes |
| Task 1 (G1) | reflection-final.md IMP-06 | IMP-06 notes `unresolved_conflicts` type inconsistency — tangential to G1 but affects same consumer section | No direct conflict; IMP-06 is a separate type-resolution concern |
| Task 8 (G8) | T04-synthesis.md Opt 3 | Opt 3 reduces fallback to 3 steps, changing which artifacts are "minimum" | If Opt 3 adopted, adjust minimum artifact list in G8 threshold to match 3-step structure |

---

*Tasklist generated 2026-02-23. All 12 tasks (covering G1-G11 + G9a) reference T02-synthesis.md sections by gap number. Deferred gaps G12-G15 excluded per source document guidance.*
