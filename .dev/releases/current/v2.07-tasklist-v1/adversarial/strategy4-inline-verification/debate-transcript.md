# Debate Transcript — Strategy 4: Inline Verification Coupling

**Pipeline Step**: 2 of 5
**Date**: 2026-03-04
**Format**: Advocate-A (Pro-adoption) vs. Advocate-B (Anti-adoption/Risk)
**Convergence threshold**: ≥80% per-point agreement to close

---

## Debate Context

Strategy 4 proposes two changes to `sc-tasklist-command-spec-v1.0.md`:
- **Sub-component S4a**: Add near-field completion criterion to each task block in §6B phase template.
- **Sub-component S4b**: Add §8 self-check: "Reject tasks lacking explicit completion condition."

These are evaluated independently per the diff-analysis finding that they carry different risk profiles.

---

## Round 1: Opening Positions

### Advocate-A (Pro-adoption)

**On S4a (near-field format change):**

The core problem is executor search distance. An automated Sprint CLI executor processes each task in a bounded context window. Under v3.0, the completion signal (Acceptance Criteria + Validation) appears after the task title, metadata table (16 rows), Why, Steps (3-8 items), and Acceptance Criteria header. In a typical task, the distance between the action statement and its completion signal is 25-40 lines. At that distance, in a token-constrained agent context, the completion signal may not even be in the active context window when the executor begins work.

Near-field placement is not cosmetic. It is an execution reliability pattern. Taskbuilder v2's `"ensuring..."` clause — co-located with the action verb — was specifically designed for headless agent execution where context window compression is real. The same constraint applies to Sprint CLI phase execution.

The claim that "no schema expansion required" is technically true if we treat near-field as the first Acceptance Criteria bullet promoted to a `Completion:` row in the metadata table. The row exists; we are assigning it a specific purpose and required content standard. That is a semantic constraint, not a schema addition.

**On S4b (self-check upgrade):**

The §8 self-check currently validates format only. It does not verify that a task has a non-empty, substantive completion condition. A generator can produce a task with `Acceptance Criteria:` followed by four vague bullets ("Implementation complete", "Tests pass", "Documented", "Reviewed") and pass all eight current checks. These bullets are formally present but semantically empty.

Adding "Reject tasks lacking explicit completion condition" to §8 closes this gap with zero format change required. It is a pure semantic gate on existing content. Risk: near-zero. Value: direct.

**On parity constraint:**

S4b is trivially parity-compatible — it is a generator internal constraint that makes output stricter without changing output format. S4a, if implemented as a semantic constraint on existing `Validation` fields rather than a new field, is also parity-compatible (same fields, higher content quality standard).

---

### Advocate-B (Anti-adoption)

**On S4a (near-field format change):**

"Near-field" is undefined. Strategy 4 uses the term without specifying what structural position satisfies it. The integration-strategies document says "near task content" — the taskbuilder-integration-proposals says "co-located with the action." These are not equivalent:

- If near-field means "within the metadata table": The metadata table already has `Verification Method`. Adding a `Completion:` row creates two completion-adjacent signals in the same table, creating executor confusion about which governs.
- If near-field means "immediately after the task title, before the metadata table": This requires restructuring the task block order — a breaking format change.
- If near-field means "the first Acceptance Criteria bullet must be a completion gate": This is a semantic content rule, not a structural change — but it requires every Acceptance Criteria bullet 1 to follow a specific format, which is not currently specified.

The claim "no schema expansion required if mapped to existing metadata conventions" is only valid for one specific interpretation (semantic constraint on existing fields). The strategy does not commit to that interpretation. Without a committed interpretation, this is an underspecified proposal.

**On S4b (self-check upgrade):**

"Reject tasks lacking explicit completion condition" introduces a semantic judgment call into what is currently a deterministic mechanical check. The eight existing §8 checks are all binary: file exists / does not exist, ID matches regex / does not match, heading format matches / does not match.

"Explicit completion condition" is not binary. It requires evaluating whether Acceptance Criteria bullet content is sufficiently explicit. That evaluation is subjective. A generator implementing this check must apply natural language understanding to its own output — a qualitatively different operation from regex matching.

This risks:
1. **False passes**: Generator judges its own vague output as "explicit enough."
2. **False failures**: Generator over-applies the rule and requires rewrites of legitimately complete tasks.
3. **Non-determinism**: Different generator runs on the same input produce different self-check outcomes because the "explicit enough" threshold is not quantified.

The value is real but the mechanism as specified is not deterministic.

**On parity constraint:**

Any format change to the §6B task template breaks parity. The parity constraint is not just functional equivalence — the spec explicitly states "output is identical to running the v3.0 generator prompt manually" (Acceptance Criterion 7). If S4a adds a new field or repositions existing content, the output differs structurally.

---

## Round 2: Responses

### Advocate-A responds to Advocate-B

**On "near-field" being undefined:**

Conceded. This is the weakest point in Strategy 4 as written. The remediation is to define "near-field" precisely in the spec patch. The correct interpretation — based on the taskbuilder source and Sprint CLI execution context — is: "The primary completion signal must appear within the metadata table row `Verification Method` or as the first bullet of the `Acceptance Criteria` section, with a required format: one objectively testable criterion."

This does not add a new field. It constrains the content of an existing field. That is the parity-safe path.

**On S4b non-determinism:**

Conceded in part. "Explicit completion condition" needs quantification. The spec must define what counts as explicit:
- "At minimum one Acceptance Criteria bullet must be objectively verifiable (not 'implementation complete' or 'working correctly')."
- Objectively verifiable = names a specific output, command, or test result.

With that definition, the check becomes semi-deterministic: the generator can evaluate "does this bullet name a specific artifact, command, or test result?" That is still a natural language judgment, but it is bounded and checkable.

**On parity:**

S4b with the quantified definition above does not change output format — it only rejects outputs that would also fail quality inspection. This is parity-safe.

S4a interpreted as semantic constraint on existing fields is parity-safe. S4a interpreted as new field is not parity-safe and should be deferred to v1.1.

---

### Advocate-B responds to Advocate-A

**On "near-field" defined as existing field constraint:**

If "near-field" is resolved to "first Acceptance Criteria bullet must name a specific output, command, or test result," then S4a is no longer a structural change — it is a content quality rule. I accept this as the correct scope for v1.0. The strategy title ("inline verification coupling") remains accurate, though misleadingly suggests a structural addition.

**On S4b with quantified definition:**

The proposed quantification ("names a specific artifact, command, or test result") is better but still requires the generator to distinguish:
- "Tests pass" (vague, fails)
- "uv run pytest tests/sprint/ passes with 0 failures" (specific, passes)
- "Function exports correctly" (borderline)

Borderline cases will exist. The spec must include at least 2 example pairs (pass/fail) to calibrate the generator's judgment. Without examples, the rule will be applied inconsistently.

This is a spec authoring requirement, not a reason to reject the strategy.

**On parity for S4b:**

If S4b is purely a generator internal self-check that rejects drafts and forces regeneration until the condition is met — and the final output always has non-empty Acceptance Criteria (which it must per existing §4.7) — then the final output format is unchanged. The self-check changes the generation process, not the output schema. Parity-compatible with the quantified definition.

**Remaining concern:**

The risk that a generator applying this self-check will produce more verbose, padded Acceptance Criteria to satisfy the rule ("uv run pytest" added to every task whether or not it is meaningful) is real. The spec must guard against padding by requiring criteria to be derived from roadmap content, not invented.

---

## Round 3: Convergence Assessment

### Per-Point Scoring Matrix

| Point | A Position | B Position | Agreement % | Closed? |
|---|---|---|---|---|
| P1: Real gap — proximity problem exists | Strongly for | Accepts gap exists | 90% | Yes |
| P2: S4a structural format change | Required for value | Unnecessary, parity risk | 55% | No |
| P3: S4a semantic constraint on existing fields | Achieves near-field goal parity-safely | Accepts if "near-field" precisely defined | 85% | Yes |
| P4: S4b adds value | Yes | Yes, with quantification | 80% | Yes |
| P5: S4b needs quantified definition of "explicit" | Yes | Yes (stronger position) | 90% | Yes |
| P6: S4b needs examples in spec | A: helpful | B: required | 75% | Partial |
| P7: Padding risk from S4b | Acknowledged | Real concern | 80% | Yes |
| P8: Parity constraint — S4a field addition breaks parity | Avoidable | Confirmed | 90% | Yes |
| P9: Parity constraint — S4b self-check is parity-safe | Yes | Yes with quantification | 85% | Yes |
| P10: "Near-field" must be defined precisely before adoption | Yes | Strongly yes | 95% | Yes |

**Overall convergence**: 82.5% — above threshold.

**Unresolved**: P2 (structural format change value), P6 (examples: helpful vs. required).

---

## Convergence Summary

**Agreed positions:**
1. A real proximity gap exists in v3.0: completion signals are structurally far-field.
2. S4a as structural format change (new field or position shift) breaks parity and should be deferred to v1.1.
3. S4a as semantic constraint on existing Acceptance Criteria fields achieves the near-field goal and is parity-compatible.
4. S4b adds genuine value by making the self-check semantic rather than purely structural.
5. S4b requires a quantified definition of "explicit completion condition" to be implementable deterministically.
6. S4b requires the non-invention rule: criteria must derive from roadmap content, not be padded.
7. "Near-field" must be defined precisely in the spec text before implementation.

**Unresolved:**
- U1: Whether the structural format change (new `Verify:` or `Done-When:` field) should be explicitly deferred to v1.1 with a forward note, or simply excluded from v1.0 scope.
- U2: Whether at least 2 example pass/fail pairs are required in the spec or optional guidance.

These unresolved points are low-risk and do not block adjudication.
