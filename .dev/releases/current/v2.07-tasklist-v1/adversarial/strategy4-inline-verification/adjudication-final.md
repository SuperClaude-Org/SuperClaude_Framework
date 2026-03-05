# Final Adjudication — Strategy 4: Inline Verification Coupling

**Pipeline Step**: 5 of 5 (Merge)
**Date**: 2026-03-04
**Input**: diff-analysis.md, debate-transcript.md, base-selection.md, refactor-plan.md
**Combined Score**: 0.780 / 1.00
**Decision**: ADOPT — Modified Scope

---

## Deliverable 1: Strongest Arguments FOR Adoption

### Argument 1: Real Executor Reliability Gap

v3.0 §6B places completion signals structurally far from action content. A task block in v3.0 has this layout:

```
### T<PP>.<TT> — <Title>
[metadata table: 16 rows]
Why: ...
Steps: (3-8 items)
Acceptance Criteria: (4 bullets)  ← completion signal lives here
Validation: (2 bullets)
```

In a 25-45 line task block, the completion signal is at the bottom. Sprint CLI executes tasks as discrete agent invocations with bounded context windows. In token-constrained execution, the completion signal may fall outside the active context window when the agent starts processing the action. The executor then either re-reads the full block (expensive) or proceeds without a clear "done" definition (unreliable).

Near-field placement of the primary completion signal addresses this at the spec level, not the executor level — the correct place to fix it.

### Argument 2: Zero Schema Expansion Required (Scoped Correctly)

The strategy's claim "no schema expansion required" is accurate when scoped to semantic constraint rather than structural addition. The §6B task format already mandates Acceptance Criteria. Requiring that the first bullet name a specific verifiable output is a content quality rule, not a schema change. The final output contains the same fields with better-specified content. This is the appropriate v1.0 scope.

### Argument 3: §8 Self-Check Upgrade Closes a Known Gap at Near-Zero Cost

The eight existing §8 checks are all structural (file existence, ID format, heading format). None verify semantic content quality. A generator can produce four vague Acceptance Criteria bullets and pass all eight checks. Adding item 9 — reject tasks where all bullets use non-specific language — makes the self-check semantically useful at the cost of one spec sentence plus a quantifying definition. The ROI is high.

### Argument 4: Aligns with Existing §0 Non-Invention Rules

The strategy's non-invention constraint (completion criteria must derive from roadmap content) directly aligns with §0's prohibition on invented context. This is not a new rule — it is an application of an existing hard rule to a new specific case. The strategy reinforces coherence rather than introducing new constraints.

### Argument 5: Sprint CLI Is the Primary Consumer and Benefits Directly

The entire tasklist generation pipeline exists to produce Sprint CLI-executable artifacts. Sprint CLI's per-phase task execution is the end consumer. If Sprint CLI agents fail to reliably identify completion state during execution, the entire pipeline value degrades. Strategy 4 directly addresses the quality of the execution signal that Sprint CLI depends on.

---

## Deliverable 2: Strongest Arguments AGAINST / Risks

### Risk 1: "Near-Field" Was Undefined and Remains Ambiguous Without Spec Patch

The strategy source (integration-strategies §4) uses "near-field completion criterion" without defining what structural position satisfies it. If the spec patch does not commit to a specific definition — "first Acceptance Criteria bullet must name a specific verifiable output" — implementors will interpret "near-field" differently on each run. The strategy has zero value without this definition committed to the spec.

This is not a reason to reject but a condition that must be satisfied before implementation.

### Risk 2: Generator Padding

A generator implementing the §8 item 9 self-check will, under pressure to pass the check, add invented specifics to Acceptance Criteria bullets:
- "uv run pytest tests/" (not implied by roadmap, not a relevant test)
- "File exists at artifacts/D-0001/spec.md" (always true per §5.1 placeholder paths — trivially satisfies the rule)
- "Manual check: X" (fallback form — always satisfies the rule but may be meaningless)

The spec must guard against this by (a) referencing the non-invention rule, (b) providing rejected-form examples that catch trivial padding.

The fallback form ("Manual check: <specific behavior>") is a legitimate pressure release valve — it always satisfies the rule — but "Manual check: task complete" does not satisfy it. The spec must define that the Manual check's description must also be specific and roadmap-derived.

### Risk 3: Semi-Deterministic Self-Check

"Explicit completion condition" evaluation is inherently natural-language-dependent. Whether "API returns 200" is sufficiently specific (yes) versus "API works correctly" (no) is clear. The boundary cases ("tests pass for happy path", "no TypeScript errors") are not. Two generator runs on the same input may judge borderline cases differently, producing non-deterministic self-check behavior.

This is the strategy's deepest structural risk. It is mitigable (bounded definition + examples) but not eliminable. The spec must acknowledge that borderline cases use the Manual check fallback rather than requiring the generator to make a judgment.

### Risk 4: Overlap With Existing §4.7 Mandates

§4.7 already mandates exactly 4 Acceptance Criteria bullets and specifies their content types. Adding a specificity constraint to bullet (1) layers a new rule on top of an existing one. The spec must be clear that this is an additional constraint on bullet (1), not a replacement of the bullet (1) definition ("functional completion criterion"). If the layering is not explicit, a generator may satisfy one rule while violating the other.

### Risk 5: Deferred Structural Variant Creates a Permanent Half-Measure

If the structural `Verify:` field (true near-field co-location) is the better long-term solution, the v1.0 semantic constraint is a compromise that future maintainers may find inadequate. If v1.1 adds the `Verify:` field and the semantic constraint on bullet (1) is not retired, two overlapping specifications will govern the same concern. The spec must include a clear forward note and a retirement plan for the semantic constraint when the structural variant is adopted.

---

## Deliverable 3: Compatibility with Strict v1.0 Parity Constraint

**Parity constraint definition** (from `sc-tasklist-command-spec-v1.0.md` §2 and Acceptance Criterion 7):
> "Achieves **exact functional parity** with the current v3.0 generator — no new features."
> "Functional parity: output is identical to running the v3.0 generator prompt manually."

### Assessment

| Sub-component | Parity Impact | Compatible? |
|---|---|---|
| S4a: Semantic constraint on first Acceptance Criteria bullet | No new fields. No structural format change. Content in existing fields is more specific. Schema is identical to v3.0. | YES — if "parity" means schema-compatible, not byte-identical |
| S4b: §8 self-check item 9 | No output format change. Generator process changes (may regenerate drafts until check passes). Final output schema unchanged. | YES |
| Deferred: New `Verify:` field | Adds a field not present in v3.0 schema. | NO — correctly deferred to v1.1 |
| Deferred: Content repositioning | Changes structural order of existing content. | NO — correctly deferred to v1.1 |

**Conclusion**: Strategy 4 as scoped (S4a semantic constraint + S4b self-check) is parity-compatible under the operative definition of parity (functional and structural equivalence, not byte-identical content).

**Caveat**: If the project defines parity as "a generator running against the same roadmap input produces byte-identical output to v3.0," then S4a fails: the same roadmap will produce different Acceptance Criteria bullet content as the generator applies the specificity rule. The project should clarify this definition. The more useful definition — and the one consistent with the parity statement's purpose (preventing feature creep) — is schema-structural, not byte-identical.

**Recommended clarification** for the spec: "Parity means schema-compatible output with identical fields, not identical field content. Higher-quality content within the same schema is parity-compatible."

---

## Deliverable 4: Final Adjudication

### Verdict: ADOPT — Modified Scope

**Score**: 0.780 (threshold: 0.65)

**What to adopt for v1.0:**

1. **Semantic completion criterion constraint on §4.7 Acceptance Criteria bullet (1)**: The first Acceptance Criteria bullet of every task MUST name a specific, objectively verifiable output — a named file or artifact path, a test command with expected result, or an observable system state. This constraint must reference the §0 non-invention rule: specifics must be derived from roadmap content. The fallback form for roadmaps with no specific output signals is: "Manual check: `<observable behavior from roadmap>` confirmed by reviewer."

2. **§8 self-check item 9**: "Every task has at least one Acceptance Criteria bullet that names a specific, verifiable output (named file path, test command with exit code, or observable state). Tasks where all Acceptance Criteria bullets use only non-specific language must be regenerated before output is written. Non-invention constraint applies: derive from roadmap; use Manual check fallback if no specific output is implied."

**What to defer to v1.1:**
- New `Verify:` field in task schema
- `Done-When:` field
- Content repositioning (Acceptance Criteria before metadata table)
- `§5.5 Verification Clause Generation` enrichment stage

**Conditions on adoption (all must be satisfied in spec patch):**
- C1: "Near-field" is defined precisely as specified above. The term itself does not appear in the spec text — the definition appears as the rule.
- C2: Accepted and rejected examples are provided (minimum 2 of each) for the self-check.
- C3: Non-invention constraint is explicitly referenced in the §8 item 9 text.
- C4: Fallback form is specified and bounded: "Manual check: <specific description from roadmap> confirmed by reviewer" — the description must be specific, not "task complete."
- C5: A v1.1 forward note is added to the spec noting the structural variant and the retirement plan for the semantic constraint.

---

## Deliverable 5: Refactored Strategy Text (Tight, Implementation-Ready)

### Strategy 4 (v1.0 scope) — Inline Completion Criterion Requirement

**What**: Add a specificity constraint to the first Acceptance Criteria bullet in every generated task. Add a semantic self-check gate before output is written.

**Scope**: Two additions to SKILL.md (or the generator prompt it embeds): one content rule in §4.7, one self-check item in §8. No new fields. No template restructuring. No command layer changes.

**Rule for §4.7 Acceptance Criteria:**

The functional completion criterion (bullet 1 of exactly 4 Acceptance Criteria bullets) MUST take one of these forms:
- Named artifact: "File `<TASKLIST_ROOT/artifacts/D-####/...>` exists and contains `<what>`."
- Test command: "`<command>` exits 0 / passes / returns `<expected>`."
- Observable state: "`<system component>` exhibits `<specific behavior from roadmap>`."
- Fallback (when roadmap provides no specific signal): "Manual check: `<description of observable state from roadmap>` confirmed by reviewer."

Content MUST be derived from roadmap input (§0 non-invention rule). Do not invent test commands, file paths, or acceptance states not implied or stated in the roadmap.

**Rule for §8 Self-Check (item 9):**

Before writing output, verify: every task has at least one Acceptance Criteria bullet whose content satisfies the completion criterion form above. A bullet satisfies the check if it names a specific file path, a specific test command with an expected result, or a specific observable state. A bullet fails the check if it contains only non-specific language: "complete," "working correctly," "tests pass" (without naming which), "documented" (without naming what), "reviewed" (without naming what was reviewed).

If any task fails this check, regenerate the task's Acceptance Criteria before writing output.

**Deferred (v1.1):** Structural `Verify:` field co-located with task action in §6B template. When adopted in v1.1, retire the §4.7 bullet (1) specificity constraint — the `Verify:` field supersedes it.

---

## Deliverable 6: Specific Spec Patch Locations and Wording

### Patch Location 1: `Tasklist-Generator-Prompt-v2.1-unified.md` §4.7

**Insert after** (line ~191, after "4. Documentation/traceability criterion"):

```markdown
**Completion Criterion Specificity Rule:**
Bullet (1) — the functional completion criterion — MUST name a specific, verifiable output.

Accepted forms:
- "File `TASKLIST_ROOT/artifacts/D-####/spec.md` exists and documents the `<X>` contract."
- "`uv run pytest tests/sprint/ -v` exits 0 with all tests passing."
- "API endpoint `POST /api/v1/auth/token` returns HTTP 200 with JWT body for valid credentials."
- "Manual check: rate limiter returns 429 after 60 requests/min threshold confirmed in staging."

Rejected forms (will fail §8 item 9 and require regeneration):
- "Implementation is complete."
- "The feature works correctly."
- "Tests pass."
- "Documented."

Non-invention constraint (§0): derive specifics from roadmap content. If no specific output is
stated or implied, use the Manual check fallback with a description derived from roadmap text.
```

### Patch Location 2: `Tasklist-Generator-Prompt-v2.1-unified.md` §8

**Append after** current item 8 ("The index contains literal phase filenames..."):

```markdown
9. Every task has at least one Acceptance Criteria bullet that names a specific, verifiable output
   (named artifact path, test command with expected result, or observable system state). Tasks where
   all Acceptance Criteria bullets contain only non-specific language ("complete", "working", "pass",
   "done", "documented" without specifics) MUST be regenerated before output is written.
   Non-invention constraint applies (§0): derive specifics from roadmap. Use Manual check fallback
   when roadmap provides no specific output signal.
```

### Patch Location 3: `sc-tasklist-command-spec-v1.0.md` §6B

**Insert** under the `## Acceptance Criteria` guidance paragraph (within the §6B Phase File Template description):

```markdown
**Near-Field Completion Criterion Rule (v1.0):**
The first Acceptance Criteria bullet must satisfy the completion criterion specificity rule
(see SKILL.md §4.7). This is the primary per-task completion signal for Sprint CLI executors.
It must be objectively verifiable and derived from roadmap content.
```

### Patch Location 4: `sc-tasklist-command-spec-v1.0.md` §9 Acceptance Criteria

**Add** as item 8:

```markdown
8. Every task in every generated phase file has at least one Acceptance Criteria bullet that
   names a specific, verifiable output (artifact path, test command, or observable state).
   No task passes the Sprint Compatibility Self-Check (§8 item 9) with only non-specific
   completion language.
```

### Patch Location 5: `sc-tasklist-command-spec-v1.0.md` §10 Open Questions (or §3 Non-Goals)

**Add** forward note:

```markdown
**v1.1 Candidate — Structural Inline Verification Field:**
A structural `Verify:` field co-located with the task action (before the metadata table) is the
preferred long-term form of inline verification coupling. It is deferred from v1.0 to preserve
strict output parity with the v3.0 generator. When adopted in v1.1, the §4.7 completion criterion
specificity rule and §8 item 9 will be retired and superseded by the `Verify:` field schema
requirement.
```

---

## Artifact Summary

| Artifact | Path |
|---|---|
| Diff analysis | `/config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy4-inline-verification/diff-analysis.md` |
| Debate transcript | `/config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy4-inline-verification/debate-transcript.md` |
| Base selection & scoring | `/config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy4-inline-verification/base-selection.md` |
| Refactor plan | `/config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy4-inline-verification/refactor-plan.md` |
| Final adjudication (this file) | `/config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy4-inline-verification/adjudication-final.md` |

---

## Unresolved Conflicts

| ID | Description | Resolution Path |
|---|---|---|
| U1 | Whether to explicitly defer `Verify:` field with forward note vs. silently exclude | Resolved: forward note required (Deliverable 6, Patch Location 5) |
| U2 | Whether 2 example pairs in §8 item 9 are required vs. optional | Resolved: required — included in Patch Location 2 above |
| U3 | Parity definition: schema-compatible vs. byte-identical | Unresolved — requires project-level clarification. Recommendation: codify as schema-compatible in §2 of `sc-tasklist-command-spec-v1.0.md`. |

U3 is a definitional question, not a blocker for implementation.

---

## Convergence Score

**Overall pipeline convergence**: 82.5% (above 80% threshold)
**Combined adoption score**: 0.780 (above 0.65 threshold)
**Status**: COMPLETE
