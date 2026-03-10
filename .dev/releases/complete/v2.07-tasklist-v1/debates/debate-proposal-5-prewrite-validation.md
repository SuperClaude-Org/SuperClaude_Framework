# Adversarial Debate: Integration Strategy 5 — Pre-Write Structural Validation Checklist

**Date**: 2026-03-04
**Proposal**: Add a dedicated pre-write schema validation checklist as a hard blocking gate before any file Write
**Spec Under Review**: `sc-tasklist-command-spec-v1.0.md`
**Reference**: `tasklist-spec-integration-strategies.md` (Strategy 5), `taskbuilder-integration-proposals.md` (Proposal 2)
**Agents**: Opus (Advocate), Haiku (Critic)

---

## Current State of the Spec

### What exists today (v3.0 / proposed v1.0)

**Section 8 — Sprint Compatibility Self-Check (Mandatory)**:
8 structural checks that run "before finalizing output":
1. Index exists with Phase Files table
2. Every referenced phase file exists in the bundle
3. Phase numbers are contiguous
4. Task IDs match `T<PP>.<TT>` format
5. Phase headings use `# Phase N — <Name>` format
6. Every phase file ends with end-of-phase checkpoint
7. No phase file contains registries/traceability/templates
8. Index contains literal phase filenames in table cells

**Section 8.1 — Semantic Quality Gate (Pre-Write, Mandatory)** (recently added):
4 semantic checks that run "before issuing any Write() call":
9. Every task has non-empty Effort, Risk, Tier, Confidence, Verification Method
10. All Deliverable IDs (D-####) globally unique
11. No placeholder/empty descriptions (TBD, TODO, title-only)
12. Every task has at least one Roadmap Item ID (R-###)

**Section 9 — Final Output Constraint**:
States: "The generator validates the complete in-memory bundle against section 8 (including section 8.1) before issuing any Write() call. All files are written only after the full bundle passes validation."

### What the taskbuilder does

The `rf:taskbuilder_v2` reference implementation runs a **12-point silent validation checklist** BEFORE `Write()`. It covers both structural rules (checkbox format, section order) and semantic rules (self-containment, atomicity, no prohibited patterns). Issues are fixed silently before writing — invalid output is never emitted.

### What the proposal adds

A dedicated, consolidated pre-write validation subsection with:
- Structural checks: contiguous numbering, task count bounds (1-25 per phase), ID format, heading format, checkpoint existence
- Semantic checks: non-empty descriptions, clarification task placement, globally unique Deliverable IDs, confidence bar formatting, XL effort splitting
- Prohibited patterns: empty shells, cross-contamination, circular dependencies

---

## ADVOCATE Position (Opus)

### Argument 1: Prevention is categorically cheaper than correction

The fundamental engineering principle at stake is the **cost asymmetry between validation and repair**. In an LLM generation context, this asymmetry is extreme:

- **Validation cost**: A pre-write check is a deterministic string/structure scan over in-memory data. It costs near-zero tokens because the generator already has the full bundle in context. Checking "are all D-#### IDs unique?" is a set membership test, not a generation task.

- **Repair cost**: If an invalid bundle is written to disk, the repair path is: (1) detect the problem via post-write self-check, (2) identify which file(s) are affected, (3) re-read those files, (4) regenerate corrected content, (5) re-write. This multi-step repair loop burns 3-10x the tokens of the original write, and introduces a second failure point (the repair itself might introduce new errors).

The spec already acknowledges this principle in section 9's atomicity constraint ("All files are written only after the full bundle passes validation"). The pre-write checklist simply makes that constraint executable and auditable rather than aspirational.

### Argument 2: The existing section 8 is structurally ambiguous about timing

The original section 8 header says "before finalizing output" — but this phrase is ambiguous. Does "finalizing" mean "before Write()" or "before returning to the user"? The section 8.1 addition clarifies with "before issuing any Write() call", but now sections 8 and 8.1 have different timing semantics described in different language. Checks 1-8 could be read as post-write verification ("verify the files exist") while checks 9-12 are explicitly pre-write.

A consolidated pre-write checklist eliminates this ambiguity entirely. All validation runs at one point: after in-memory bundle construction, before any disk write. This is the only timing that makes sense for atomic writes, and making it explicit removes a class of implementer confusion.

### Argument 3: Pre-write validation enables CI-testability

A pre-write validation checklist is inherently testable in a way that post-write self-checks are not:

- **Unit-testable**: Each check can be validated against synthetic bundle fixtures. "Given this in-memory index + phase set, does check N pass?" This is a pure function with deterministic inputs/outputs.

- **Regression-catchable**: When the spec evolves (new fields, new format rules), adding a check to the pre-write list is a one-line diff. CI can run the checklist against golden fixtures to catch regressions.

- **Sprint CLI-alignable**: The Sprint CLI already performs its own validation during `--dry-run`. If the generator's pre-write checks match the Sprint CLI's expectations, format drift between generator and consumer is caught at generation time rather than at sprint execution time — when the cost of failure is much higher (interrupted sprint, partial execution state).

Post-write self-checks cannot provide this guarantee because they verify properties of files on disk, not properties of the generation logic.

### Argument 4: The checklist is the enforcement mechanism for all other proposals

The integration strategies document identifies 5 proposals. Strategy 5 (this one) is explicitly positioned as the **foundation for the other four**:

- Strategy 1 (Stage-Gated Contract): Stages need validation gates between them. The pre-write checklist IS the final gate.
- Strategy 3 (Prohibited Patterns): Prohibited patterns need enforcement. The checklist is where "reject if prohibited pattern found" lives.
- Strategy 4 (Inline Verification Coupling): "Reject tasks lacking explicit completion condition" — this is a checklist item.
- Proposal 1 from the taskbuilder doc (Self-Contained Task Items): "Every task has non-empty Context and Verify fields" — another checklist item.

Without the pre-write checklist, each of these proposals must independently define its own enforcement mechanism, leading to scattered validation logic with no single point of truth for "what gets checked."

### Argument 5: It catches format drift the generator cannot see

An LLM generator is statistically likely to produce correct output most of the time. But "most of the time" is insufficient for deterministic systems. The failure modes are:

- **Context window pressure**: As the bundle grows (8+ phases, 100+ tasks), the generator's attention to format consistency degrades. A pre-write checklist acts as a deterministic backstop that does not degrade with scale.

- **Prompt evolution drift**: When the spec changes (new fields, renamed sections), the generator may partially adopt the new format while retaining vestiges of the old. A checklist catches these partial migrations.

- **Edge cases in compound rules**: The tier classification system has compound phrase overrides, context boosters, and confidence penalties that interact in complex ways. A pre-write check like "no task has EFFORT=XL without subtasks" catches cases where the enrichment logic produces internally inconsistent results.

These are not theoretical concerns — they are the exact failure modes observed in the taskbuilder's production history, which motivated the 12-point silent validation checklist in the first place.

### Argument 6: Token cost is negligible for the value delivered

The pre-write checklist is a set of deterministic checks over data the generator already holds in context. Estimated token cost:

- Checklist execution: ~200-400 tokens (enumerate checks, report pass/fail)
- Fix-before-write loop (if triggered): ~500-1000 tokens per fix
- Expected fix rate: <5% of generations (the generator usually gets it right)
- Amortized cost per generation: ~220-450 tokens

Compare to the cost of a single invalid bundle reaching the Sprint CLI and failing at execution time: 5,000-15,000 tokens for diagnosis + regeneration + re-validation. The ROI is 10-30x.

---

## CRITIC Position (Haiku)

### Argument 1: The spec already has pre-write validation — this is renaming, not adding

Section 8.1 already exists. It is titled "Semantic Quality Gate (Pre-Write, Mandatory)." It runs before Write(). Section 9 already enforces atomic writes. The proposal is not adding new capability — it is reorganizing existing sections into a different subsection heading.

Reorganization has a cost: it increases the SKILL.md token footprint by ~300-500 tokens (the checklist enumeration itself), and it creates a second validation section that must be kept in sync with section 8. If checks are added to section 8 but not to the "pre-write checklist," or vice versa, the spec now has contradictory validation requirements.

The simpler approach is to keep section 8 as the single source of validation truth and ensure its timing semantics are clear. A one-line fix to the section 8 header — changing "before finalizing output" to "before issuing any Write() call" — achieves the same timing clarity without the overhead of a new section.

### Argument 2: The generator already produces correct output deterministically

The v3.0 generator is a deterministic algorithm. Same input produces same output. The generation rules in sections 4 and 5 are designed to produce valid output by construction:

- Task IDs follow `T<PP>.<TT>` because section 4.5 specifies exactly this format
- Phase numbers are contiguous because section 4.3 enforces renumbering
- Deliverable IDs are sequential because section 5.1 assigns them in order
- All tasks have metadata because section 5.2-5.6 compute it deterministically

If the generator follows its own rules — which it must, because it is prompt-instructed — the output is valid by definition. Pre-write validation checks properties that are already guaranteed by the generation algorithm itself.

This is analogous to adding a runtime type check after a statically typed function call: the type system already guarantees the property, so the check is pure overhead.

### Argument 3: Adding more validation increases SKILL.md complexity and token cost

The SKILL.md is already a large document (~760 lines in v3.0). Every additional section consumes tokens in the LLM's context window during generation. The pre-write checklist as proposed adds:

- ~13 enumerated checks with descriptions (~400 tokens)
- A conditional fix-before-write loop instruction (~100 tokens)
- Cross-references to other sections (~50 tokens)
- Total: ~550 tokens per invocation

In a context-constrained execution environment, these 550 tokens compete with the actual generation content. For a complex roadmap with 8+ phases and 100+ tasks, the generator is already pushing context limits. Adding validation overhead reduces the available space for the primary task.

Moreover, complex validation logic in natural language is itself a source of ambiguity. "No task has EFFORT=XL without being split into subtasks" — what constitutes "being split"? Does the generator need to retroactively split the task if it assigned XL? Or does it need to have already split it during section 4.4? The check introduces a question that the generation algorithm does not need to answer.

### Argument 4: The existing section 8 self-check already covers structural correctness

Compare the proposed pre-write checks with what section 8 already verifies:

| Proposed Check | Already in Section 8? |
|---|---|
| Contiguous phase numbering | Yes (check 3) |
| Task IDs follow T format | Yes (check 4) |
| Phase heading format | Yes (check 5) |
| End-of-phase checkpoint | Yes (check 6) |
| No registries in phase files | Yes (check 7) |
| Literal filenames in index | Yes (check 8) |
| Non-empty metadata fields | Yes (check 9, in section 8.1) |
| Globally unique D-IDs | Yes (check 10, in section 8.1) |
| No placeholder descriptions | Yes (check 11, in section 8.1) |
| Every task has R-### | Yes (check 12, in section 8.1) |

The overlap is near-total. The only genuinely new checks in the proposal are:

- Task count bounds (1-25 per phase)
- Clarification task placement (immediately before blocked task)
- Confidence bar format consistency
- XL effort → subtask splitting
- Circular dependency detection

These are valid checks, but they do not require a new section. They can be appended to the existing section 8.1 as checks 13-17.

### Argument 5: Moving checks from post-write to pre-write is cosmetic when writes are atomic

Section 9 already mandates atomic writes: "All files are written only after the full bundle passes validation." This means the generator must validate the complete in-memory bundle before writing anything. Whether you call this "pre-write validation" or "self-check before finalize," the functional behavior is identical:

1. Build the complete bundle in memory
2. Validate it
3. Write all files (or write nothing, if validation fails)

The timing distinction between "pre-write" and "post-write" only matters if writes are incremental (file-by-file). Since section 9 prohibits incremental writes, the distinction is moot. A check that says "verify the index contains a Phase Files table" is the same operation whether you describe it as "pre-write structural validation" or "self-check before finalizing."

The proposal is introducing a semantic distinction (pre-write vs. post-write) for a system that already operates in a single validation-then-write-all pattern.

### Argument 6: Validation logic in prompts is inherently unreliable

The core premise of the proposal — that a checklist prevents invalid output — assumes the LLM will reliably execute the checklist. But the same LLM that might produce invalid output is the one executing the validation checklist. If the generator can produce a duplicate D-#### ID, it can also fail to detect a duplicate D-#### ID in its own self-check.

True validation requires an external verifier:
- The Sprint CLI's `--dry-run` mode
- CI-level linting of generated files
- A separate validation agent spawned after generation

Embedding validation in the same prompt as generation creates a false sense of safety. It is defense-in-depth only if the validator is independent of the generator.

---

## REBUTTAL: Advocate Response to Critic

### On "this is renaming, not adding" (Critic Argument 1)

The critic is partially correct that section 8.1 already exists. However, the proposal does more than rename:

1. **It consolidates fragmented timing semantics.** Sections 8 (ambiguous timing), 8.1 (explicit pre-write), and 9 (atomic writes) are three different places that collectively define validation behavior. A single consolidated checklist in one location is clearer for implementers.

2. **It adds genuinely new checks** that section 8/8.1 do not cover: task count bounds, clarification task adjacency, confidence bar format, XL splitting, and circular dependency detection. These are not cosmetic.

3. **It provides enumerated, machine-parseable checks** rather than prose-described validation. "Check 7: No phase file contains registries" is more auditable than the current formulation.

### On "generator produces correct output by construction" (Critic Argument 2)

This argument fails empirically. The generator is an LLM, not a compiler. "Deterministic" in the spec means "same rules applied consistently" — it does not mean "statically guaranteed correct output." LLMs routinely:

- Drop fields under context pressure
- Produce inconsistent formatting across phases
- Assign duplicate IDs when phase counts exceed ~6
- Partially apply compound rules (e.g., applying the confidence penalty but not the compound phrase boost)

The "correct by construction" claim would hold for a traditional code generator. It does not hold for a natural-language-instructed LLM executing a 760-line prompt.

### On "validation in prompts is inherently unreliable" (Critic Argument 6)

This is the critic's strongest argument, and it is partially valid. However:

1. **Defense in depth does not require independence.** A seatbelt and an airbag are not independent systems (both rely on the car's electrical system), yet both reduce injury. Self-validation catches a meaningful class of errors even if it is not comprehensive.

2. **The self-check has a different failure mode than the generation.** Generation failures are typically attention/context failures (dropping a field, duplicating an ID). Self-check failures are typically comprehension failures (not understanding the check). These are different cognitive tasks with different failure probabilities.

3. **The proposal does not claim to replace external validation.** It complements the Sprint CLI's `--dry-run` and CI linting. It catches obvious errors early, reducing the load on external validators.

---

## REBUTTAL: Critic Response to Advocate

### On "prevention is cheaper than correction" (Advocate Argument 1)

The cost asymmetry argument assumes that invalid output is written to disk before detection. But section 9 already prevents this — atomic writes mean validation happens before ANY write. The "repair cost" scenario the advocate describes (detect, re-read, regenerate, re-write) cannot occur under the current spec because the bundle is never partially written.

The real comparison is: "validation at step 8 of the pipeline" vs. "validation at a new step 7.5 of the pipeline." The cost difference is zero — both happen before Write(), both operate on in-memory data.

### On "enables CI-testability" (Advocate Argument 3)

CI-testability of the checklist is a valid benefit, but it does not require the checklist to be in the SKILL.md. CI tests can validate generated output files against the section 8 criteria without the generator itself having an explicit checklist. The CI test suite is an external verifier (addressing Critic Argument 6) and is more reliable than self-validation.

The advocate is conflating two things: (a) having a clear list of checks (useful for CI), and (b) having the generator execute those checks itself (marginal value given atomic writes).

### On "catches format drift the generator cannot see" (Advocate Argument 5)

If the generator "cannot see" its own format drift, why would it see the drift during self-validation? The same context pressure that causes drift also affects the quality of the self-check. This argument actually supports externalizing validation rather than embedding it deeper in the prompt.

---

## SYNTHESIS

### Points of Agreement

Both sides agree on the following:

1. **Atomic writes are essential.** Section 9's mandate that no partial bundles be written is correct and should be preserved.
2. **Some form of validation must occur before Write().** The question is whether the existing section 8 + 8.1 is sufficient or needs consolidation/expansion.
3. **External validation (Sprint CLI `--dry-run`, CI linting) is the gold standard.** In-prompt validation is complementary, not a replacement.
4. **There are genuinely missing checks** not covered by section 8/8.1: task count bounds, clarification task adjacency, circular dependencies, XL splitting, confidence bar format.

### Points of Genuine Disagreement

1. **Whether consolidation into a single subsection is worth the token cost.** Advocate says clarity is worth ~550 tokens. Critic says section 8.1 already exists and can be extended.
2. **Whether LLM self-validation is reliable enough to justify prompt complexity.** Critic argues that validation by the same LLM is circular. Advocate argues defense-in-depth is still valuable.
3. **Whether "pre-write" vs. "post-write" is a meaningful distinction when writes are atomic.** Critic says it is cosmetic. Advocate says it eliminates ambiguity in section 8's original language.

### Verdict: CONDITIONAL ACCEPT

The proposal is accepted with modifications that address the critic's valid concerns:

**Accept** the following:
1. Add the 5 genuinely new checks (task count bounds 1-25, clarification task adjacency, circular dependency detection, XL effort splitting requirement, confidence bar format validation) to section 8.1 as checks 13-17.
2. Clarify the timing of section 8 checks 1-8 by changing the section 8 header to: "Sprint Compatibility Self-Check (Pre-Write, Mandatory)" — making explicit that ALL checks (1-12, plus new 13-17) run before any Write() call.
3. Retain section 9's atomic write mandate as the enforcement backstop.

**Reject** the following:
1. Creating a new, separate subsection (section 7.5 or similar) that duplicates section 8/8.1 content. The existing section 8 structure is adequate when its timing is clarified.
2. Renaming or reorganizing the existing checks. The current numbering is referenced in the integration strategies doc and should remain stable.

**Rationale**: The critic is correct that section 8.1 already provides pre-write validation and that a new section would create maintenance burden. The advocate is correct that genuinely new checks are needed and that timing ambiguity should be resolved. The compromise is to extend section 8.1 rather than create a parallel structure.

### Recommended Spec Modifications

#### Modification 1: Clarify section 8 timing

Change the section 8 header from:
```
## 8) Sprint Compatibility Self-Check (Mandatory)

Before finalizing output, verify all of the following:
```

To:
```
## 8) Sprint Compatibility Self-Check (Pre-Write, Mandatory)

Before issuing any Write() call, verify all of the following against the in-memory bundle:
```

#### Modification 2: Add new checks to section 8.1

Append to section 8.1:

```markdown
13. Every phase file contains between 1 and 25 tasks (inclusive). Phases with 0 tasks must not be emitted; phases exceeding 25 tasks must be split.
14. Every Clarification Task (marked with a "Clarify:" or "Confirm:" title prefix) appears immediately before the task it unblocks — no intervening tasks between a clarification and its dependent.
15. No circular dependencies exist in task dependency chains. If task A depends on B and B depends on A (directly or transitively), the cycle must be broken before writing.
16. No task has EFFORT=XL without having been evaluated for splitting per section 4.4/4.5. If XL persists after splitting evaluation, add a Note explaining why splitting was not applied.
17. Confidence bars use consistent format: `[` + filled blocks + empty blocks + `]` + space + percentage + `%`. No mixed bar styles across the bundle.
```

#### Modification 3: Strengthen section 9 cross-reference

In section 9, change:
```
The generator validates the complete in-memory bundle against section 8 (including section 8.1) before issuing any Write() call.
```

To:
```
The generator validates the complete in-memory bundle against all checks in section 8 (checks 1-8) and section 8.1 (checks 9-17) before issuing any Write() call.
```

### Impact Assessment

| Dimension | Assessment |
|---|---|
| Token cost increase | ~150 tokens (5 new checks + header clarification) |
| Structural change | None — extends existing section, no new sections |
| Breaking change | No |
| CI-testability | Improved — checks 13-17 are testable against fixtures |
| Sprint CLI alignment | Improved — task count bounds and dependency validation |
| Spec maintainability | Neutral — no new section to sync, but more checks to maintain |

### Priority Relative to Other Proposals

The integration strategies doc recommends Strategy 5 as the first implementation. This verdict supports that recommendation with the caveat that it should be implemented as an extension to section 8.1 rather than as a new section. Implementation effort: ~45 minutes (add 5 checks, update 2 headers, update 1 cross-reference).
