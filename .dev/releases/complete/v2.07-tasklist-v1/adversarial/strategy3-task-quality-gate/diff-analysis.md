# Diff Analysis — Strategy 3: Self-Contained Task Item Quality Gate

**Pipeline**: sc:adversarial — Step 1 of 5
**Date**: 2026-03-04
**Subject**: Strategy 3 from `tasklist-spec-integration-strategies.md`
**Base spec analyzed**: `sc-tasklist-command-spec-v1.0.md`
**Cross-reference**: `taskbuilder-integration-proposals.md` Proposal 1 (the detailed expansion of Strategy 3)

---

## 1. What Strategy 3 Proposes (Exact Text)

From `tasklist-spec-integration-strategies.md §3`:

> **What to integrate**: Borrow `taskbuilder`'s strongest pattern: each checklist item should be executable on its own. For `/sc:tasklist`, enforce that each generated task includes enough context to execute without external chat history.
>
> **Concrete spec changes**:
> - In §7 Style Rules (or §8 Self-Check mapping), add gate: "Each task description must be standalone and action-oriented (explicit artifact/target)."
> - In §9 Acceptance Criteria, add: "No task requires conversational context outside the generated files to understand execution intent."
>
> **Value**: Safer for delegation, async execution, and session rollover. Improves practical usability of generated bundles.

---

## 2. Structural Differences: Current v1.0 vs. Strategy 3 Adopted

### 2.1 Current State (v1.0 baseline)

**Task format in `§6B` phase template** (from `sc-tasklist-command-spec-v1.0.md`):
```
- [ ] T<PP>.<TT> · <Title>
  - Effort: <XS|S|M|L|XL> | Risk: <low|moderate|high> | Tier: <tier>
  - Dependencies: <comma-separated T-IDs or "none">
  - Deliverables: <D-### IDs if applicable>
```

**§7 Style Rules** (as specified): Verbatim from v3.0 generator — no explicit standalone-task rule.

**§8 Sprint Compatibility Self-Check** (as specified): Validates structural correctness (file existence, heading format, ID format, contiguous numbering). Does NOT validate whether task descriptions are action-oriented or self-contained.

**§9 Acceptance Criteria** (from `sc-tasklist-command-spec-v1.0.md`):
1. Discoverable in Claude Code
2. Produces correct file bundle with correct naming
3. `make lint-architecture` passes
4. Sprint CLI discovers all phase files
5. Phase files are lean (no registries/traceability/templates)
6. Sprint Compatibility Self-Check runs before output
7. Functional parity: output identical to v3.0 manual run

No criterion addresses per-task content quality.

### 2.2 Proposed State (Strategy 3 adopted)

**§7 Style Rules** gains: "Each task description must be standalone and action-oriented (explicit artifact/target)."

**§9 Acceptance Criteria** gains: "No task requires conversational context outside the generated files to understand execution intent."

**Implied but not explicitly stated in Strategy 3**: Whether new task *fields* (`Context:`, `Verify:`) are added, or whether the constraint is enforced purely through generation rule without schema change.

---

## 3. Content Differences

### 3.1 What Changes
| Location | Current | With Strategy 3 |
|----------|---------|----------------|
| §7 Style Rules | No standalone-task rule | Rule added: standalone + action-oriented |
| §9 Acceptance Criteria | 7 criteria, none address task content quality | 8th criterion: no task requires external conversational context |
| §8 Self-Check | Structural checks only | May gain semantic check if S3 implies enforcement |
| §6B task format | 4 fields: title, metadata, dependencies, deliverables | Unchanged by literal Strategy 3 text; expanded by Proposal 1 interpretation |

### 3.2 What Does NOT Change (per literal Strategy 3 text)
- Task ID format (`T<PP>.<TT>`)
- Phase file structure (heading format, numbering)
- Command layer (`tasklist.md`)
- Input/output contract (roadmap in, bundle out)
- Installation behavior
- `make lint-architecture` checks

---

## 4. Contradictions and Tensions

### 4.1 Ambiguity: Rule vs. Schema Change
Strategy 3 (integration-strategies doc) proposes only a **generation rule** (§7) and **acceptance criterion** (§9). It does not add new fields.

`taskbuilder-integration-proposals.md` Proposal 1 — the expanded version of the same concept — proposes **three new task fields**: `Context:`, `Verify:`, `Blocked-Until:`.

These are different scope levels. The adversarial debate must adjudicate:
- Does Strategy 3 mean only the generation rule + acceptance criterion?
- Or does it mean the full Proposal 1 schema expansion?

The source doc (`integration-strategies.md`) explicitly scopes it as "does not add new task fields; it is a generation quality rule." This creates a deliberate boundary that Proposal 1 crosses.

### 4.2 Tension with v1.0 Parity Constraint
The v1.0 parity constraint (§9 criterion 7) requires: "Functional parity: output is identical to running the v3.0 generator prompt manually."

If Strategy 3 adds a generation rule that changes what the generator emits (even in content rather than schema), it breaks parity. The new §7 rule instructs the generator to produce different-quality task descriptions than v3.0 currently produces.

Whether this is a "schema break" or a "generation quality improvement compatible with parity" is a key debate point.

### 4.3 Verifiability Gap
The proposed §9 criterion ("No task requires conversational context outside the generated files") is not mechanically verifiable. The Sprint Compatibility Self-Check (§8) uses deterministic structural checks (file existence, ID format). A semantic check for "conversational context dependency" is not testable by a parser.

This means the acceptance criterion would be evaluated by human review or by an LLM judge — neither of which is deterministic or CI-automatable. This creates a gap between the stated criterion and the validation infrastructure.

---

## 5. Unique Contributions

### 5.1 Positive Unique Contributions of Strategy 3
- **Session Rollover Safety**: Addresses a real Sprint CLI operational risk. Tasks executed across sessions by automated agents are vulnerable to lost context. A generation rule that forces self-contained descriptions directly mitigates this.
- **Delegation Safety**: Self-contained tasks can be safely handed to sub-agents without re-establishing session context.
- **Cheapest Possible Intervention**: A generation rule in §7 costs zero schema changes and zero output format changes. It is purely an instruction to the generating LLM about quality.
- **Alignment with Taskbuilder's Proven Pattern**: The source of the pattern (`taskbuilder_v2`) is described as "production-tested in a headless agent execution context similar to Sprint CLI."

### 5.2 Gaps Strategy 3 Leaves Open
- No enforcement mechanism: A §7 rule is an instruction, not a gate. Without a §8 self-check addition, the rule can be silently violated.
- No operationalization of "standalone": What exactly constitutes standalone? Without examples or a rubric, two generator runs may apply the rule inconsistently.
- No schema support: Without `Context:` and `Verify:` fields, a task description that embeds all context becomes arbitrarily long prose, inconsistently formatted across tasks.

---

## 6. Relationship to Other Strategies

Strategy 3 has interdependencies with:
- **Strategy 1** (Stage-Gated Contract): If Stage 4 (enrichment) is where self-containment is enforced, Strategy 1 provides the framework within which Strategy 3's gate fits.
- **Strategy 4** (Inline Verification Coupling) from `taskbuilder-integration-proposals.md` Proposal 5: Directly overlaps. Both address "does the task have enough information at point-of-execution?" Strategy 4 adds `Verify:` field; Strategy 3 is the parent principle.
- **Proposal 1 from taskbuilder-integration-proposals.md**: The full schema-expanding version of Strategy 3. Adopting Strategy 3 without Proposal 1 is a deliberate constraint; adopting it with Proposal 1 is a scope expansion.

---

## 7. Summary Classification

| Dimension | Assessment |
|-----------|-----------|
| Schema change | No (per literal S3 text) |
| Output format change | Possible (longer/denser descriptions) |
| Parity impact | Conditional (see §4.2) |
| Enforcement gap | Yes (see §4.3) |
| Sprint CLI benefit | High |
| Automation compatibility | Enforcement is not CI-automatable as written |
| Effort | Low (§7 rule + §9 criterion only) |
