# Refactor Plan — Strategy 4: Inline Verification Coupling

**Pipeline Step**: 4 of 5
**Date**: 2026-03-04
**Decision**: ADOPT (Modified)

---

## 1. Integration Points

Strategy 4 (modified scope) touches exactly three locations:

| # | Target File | Section | Change Type | Risk |
|---|---|---|---|---|
| 1 | `sc-tasklist-command-spec-v1.0.md` | §6B Phase File Template | Semantic constraint addition to task format guidance | Low |
| 2 | `sc-tasklist-command-spec-v1.0.md` | §9 Acceptance Criteria | Add criterion 8 | Low |
| 3 | `Tasklist-Generator-Prompt-v2.1-unified.md` (→ SKILL.md §4.7 + §8) | §4.7 Acceptance Criteria rules + §8 Self-Check | Semantic constraint + self-check rule addition | Low |

---

## 2. Change 1: §6B Task Format — Near-Field Completion Criterion Rule

**Target**: `sc-tasklist-command-spec-v1.0.md` §6B phase template guidance.

In the skill spec's description of phase file task format, add the following rule under the `Acceptance Criteria` guidance:

```markdown
**Near-Field Completion Criterion (Required):**
The first Acceptance Criteria bullet MUST name a specific, objectively verifiable output.
Accepted forms:
- A named file or artifact at a specific path: "File `TASKLIST_ROOT/artifacts/D-####/spec.md` exists."
- A test command outcome: "`uv run pytest tests/sprint/` exits 0 with all tests passing."
- An observable state: "API endpoint returns HTTP 200 for valid input with response schema matching `OpenAPISpec §3.2`."

Rejected forms (fail self-check):
- "Implementation is complete."
- "The feature works correctly."
- "Tests pass." (without specifying which tests or command)
- "Documented." (without specifying what document at what path)
```

**Rationale**: This does not add a new field. It constrains the content of the first Acceptance Criteria bullet — an existing mandatory element — to a specific format. The output schema is unchanged.

---

## 3. Change 2: §8 Self-Check — Semantic Completion Condition Gate

**Target**: `sc-tasklist-command-spec-v1.0.md` §8 Sprint Compatibility Self-Check.

Add item 9 to the existing self-check list (which currently has 8 items):

```markdown
9. Every task has at least one Acceptance Criteria bullet that names a specific, objectively verifiable
   output (file path, test command, or observable state). Tasks where all Acceptance Criteria bullets
   use only non-specific language ("complete", "working", "pass", "done") MUST be regenerated before
   output is written.

   Non-invention constraint: Completion criteria must be derived from roadmap content.
   Do not invent test commands, file paths, or acceptance states not implied by the roadmap.
   If the roadmap provides no verifiable output signal, use:
   "Manual check: <specific observable behavior described in roadmap> verified by reviewer."
```

**Rationale**: The non-invention constraint anchors the rule to §0 (Non-Leakage + Truthfulness Rules), preventing the generator from padding with invented specifics. The fallback form ("Manual check: ...") ensures the rule can always be satisfied without inventing content.

---

## 4. Change 3: Generator Prompt — §4.7 and §8 Alignment

**Target**: `Tasklist-Generator-Prompt-v2.1-unified.md` §4.7 and §8 (and their SKILL.md equivalents).

### 4.1 §4.7 Acceptance Criteria — Add Specificity Rule

Current §4.7 text:
> **Acceptance Criteria:** exactly **4** bullets: (1) Functional completion criterion, (2) Quality/safety criterion, (3) Determinism/repeatability criterion, (4) Documentation/traceability criterion

Add after this block:

```markdown
**Completion Criterion Specificity Rule (Near-Field Requirement):**
Bullet (1) — the functional completion criterion — MUST name a specific, verifiable output:
  - A file or artifact at a named path
  - A test command that exits with a specific result
  - An observable system state tied to roadmap acceptance criteria

Non-specific language in bullet (1) causes self-check failure (§8 item 9).
Derive specifics from roadmap text. If no specific output is implied, use:
"Manual check: <describe what must be true, derived from roadmap> confirmed by reviewer."
```

### 4.2 §8 Self-Check — Add Item 9

Append after current item 8:

```markdown
9. Every task's first Acceptance Criteria bullet names a specific, verifiable output
   (named file path, test command with exit code, or observable state). Tasks with
   non-specific bullet (1) MUST be fixed before output is written.
   Non-invention constraint applies: derive from roadmap; use Manual check fallback
   if no specific output is implied by roadmap content.
```

---

## 5. Deferred to v1.1

The following are explicitly out of scope for v1.0 and must not be implemented:

| Item | Reason |
|---|---|
| New `Verify:` field in §6B task schema | Breaks output parity — new field not in v3.0 schema |
| New `Done-When:` field in §6B task schema | Same |
| Repositioning Acceptance Criteria before metadata table | Structural format change breaks parity |
| `§5.5 Verification Clause Generation` section (from taskbuilder proposals) | Feature expansion beyond v1.0 scope |
| Inline `"ensuring..."` clause appended to action steps | Format change not present in v3.0 |

Add a forward note in `sc-tasklist-command-spec-v1.0.md` §3 Non-Goals or §10 Open Questions:

```markdown
**v1.1 Candidate**: Structural `Verify:` field co-located with task action (before metadata table).
Currently deferred to preserve v1.0 parity. Near-field semantic constraint (§4.7 + §8) achieves
the same executor guidance goal within v1.0 scope.
```

---

## 6. Implementation Order

1. Update `sc-tasklist-command-spec-v1.0.md` §6B (Change 1) — adds specificity rule to task format guidance.
2. Update `sc-tasklist-command-spec-v1.0.md` §8 (Change 2) — adds self-check item 9.
3. Update `Tasklist-Generator-Prompt-v2.1-unified.md` §4.7 and §8 (Change 3) — aligns generator algorithm.
4. Add v1.1 forward note to `sc-tasklist-command-spec-v1.0.md`.
5. Verify `make lint-architecture` still passes (no schema changes, no file layout changes).
6. Verify manual test: run generator against a sample roadmap, confirm first Acceptance Criteria bullet in each task names a specific output.

**Estimated spec update effort**: 1.5–2 hours total.
**No command layer changes required.**
**No template file changes required.**
**No new files created.**

---

## 7. Risk Summary

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Generator pads bullet (1) with invented test commands | Medium | Low (output passes but criteria are wrong) | Non-invention constraint in §0 reference; manual validation during acceptance testing |
| Borderline cases in self-check (is this specific enough?) | Medium | Low | Two example pairs in spec (see Change 2 above — accepted/rejected forms) |
| Spec change conflicts with later Strategy 5 (pre-write checklist) | Low | Low | Strategy 5 adds §7.5; Strategy 4 adds §8 item 9. No overlap. |
| Self-check item 9 causes spurious regeneration on valid tasks | Low | Low | Accepted/rejected examples bound the check; fallback form always satisfies the rule |
