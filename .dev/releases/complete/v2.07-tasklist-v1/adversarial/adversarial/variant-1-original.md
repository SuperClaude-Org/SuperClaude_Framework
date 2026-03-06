

# Source: /config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy1-stage-gated-contract/refactor-plan.md

# Step 4: Refactoring Plan — Strategy 1: Stage-Gated Generation Contract

**Date**: 2026-03-04
**Decision**: ADOPT with modifications M1-M5
**Target spec**: `sc-tasklist-command-spec-v1.0.md`

---

## Modification Inventory

| ID | Modification | Target Section | Risk | Order |
|----|-------------|---------------|------|-------|
| M1 | Reword "halts" to instruction-appropriate language | §9 Acceptance Criteria | Low | 1 |
| M2 | Add per-stage validation criteria table | §6.2 (new subsection) | Low | 2 |
| M3 | Canonicalize 6-stage names in §4.3, retire numbered-step duplication | §4.3 Invocation Flow | Low | 3 |
| M4 | Add parity clarification note | §6.2 Content | Very Low | 4 |
| M5 | Update §9 Criterion 6 to cover all stage gates, not only §8 | §9 Acceptance Criteria | Low | 1 (with M1) |

---

## Integration Point 1: §4.3 Invocation Flow (M3)

### Current text (conceptual — 8-step numbered list)
```
SKILL execution:
  1. Read roadmap text (§2)
  2. Parse roadmap items (§4.1)
  3. Determine phase buckets (§4.2-4.3)
  4. Convert items to tasks (§4.4-4.5)
  5. Enrich: effort/risk/tier/confidence (§5)
  6. Generate multi-file bundle (§6):
     - Write tasklist-index.md (§6A)
     - Write phase-N-tasklist.md per phase (§6B)
  7. Run Sprint Compatibility Self-Check (§8)
  8. Return file paths
```

### Replacement text (M3 applied — named stage contract)
```
SKILL execution — Stage-Gated Contract:

  Stage 1: Input Ingest
    - Read roadmap text (§2 Input Contract)
    - Read spec/context if provided
    Validation: roadmap text is non-empty; required sections present

  Stage 2: Parse + Phase Bucketing
    - Parse roadmap items (§4.1)
    - Assign items to phase buckets (§4.2-4.3)
    Validation: all items assigned to exactly one phase; no items dropped

  Stage 3: Task Conversion
    - Convert phase items to task format (§4.4-4.5)
    Validation: all items produce valid task stubs with T<PP>.<TT> IDs; no ID collisions

  Stage 4: Enrichment
    - Assign effort/risk/tier/confidence to each task (§5)
    Validation: all tasks have non-empty effort, risk, tier, confidence fields

  Stage 5: File Emission
    - Write tasklist-index.md (§6A)
    - Write phase-N-tasklist.md per phase (§6B)
    Validation: all declared phase files exist on disk; index Phase Files table matches actual filenames

  Stage 6: Self-Check
    - Run Sprint Compatibility Self-Check (§8)
    Validation: all §8 checks pass; no check failures

  Stage progression rule: each stage must complete and pass its validation
  before advancing to the next stage. Do not proceed to Stage N+1 if Stage N
  validation criteria are not satisfied. Report completed stages in order
  using TodoWrite as each stage passes.
```

### Risk: Low
No output schema change. No command layer change. Replaces an implicit ordering with an explicit one.

---

## Integration Point 2: §6.2 Content (M2 + M4)

### Current text (relevant sentence)
```
The SKILL.md body is the full v3.0 generator prompt — sections §0 through §9 plus the
Appendix — reformatted into skill convention but functionally identical.
```

### Additional text to append after that sentence (M4 parity note + M2 reference)
```
Note on stage-gated execution (skill packaging addition): The stage-gated
generation contract (§4.3) is a reliability mechanism added during skill
packaging. It constrains execution behavior without altering the generation
algorithm, task schema, or output structure. The v3.0 generator did not
include per-stage validation semantics; this is intentional hardening for
automated sprint execution contexts.

The following per-stage validation criteria govern stage advancement:

| Stage | Name | Validation Criteria |
|-------|------|---------------------|
| 1 | Input Ingest | Roadmap text non-empty; required sections (phases/items) present; file read succeeded |
| 2 | Parse + Phase Bucketing | Every roadmap item assigned to exactly one phase; no ambiguous assignments remain unresolved; phase count ≥ 1 |
| 3 | Task Conversion | All roadmap items converted to task stubs; T<PP>.<TT> IDs assigned with no collisions; task titles non-empty |
| 4 | Enrichment | All tasks have non-empty: Effort (XS/S/M/L/XL), Risk (low/moderate/high), Tier (STANDARD/STRICT/EXEMPT/LIGHT), Confidence score |
| 5 | File Emission | tasklist-index.md written; all phase files referenced in index exist on disk; no extra phase files written |
| 6 | Self-Check | All Sprint Compatibility Self-Check assertions (§8) pass; no blocking failures |

If any stage validation criterion is not satisfied, the skill must not advance
to the next stage. Instead, report the failed criterion and the corrective
action taken (or, if correction is not possible, report the blocking error).
```

### Risk: Low
Additive only. Does not change any existing content.

---

## Integration Point 3: §9 Acceptance Criteria (M1 + M5)

### Current Criterion 6
```
6. The Sprint Compatibility Self-Check (§8) runs before output is finalized
```

### Replacement (M1 + M5 applied)
```
6. Generation executes in stage order (Ingest → Parse/Bucket → Convert → Enrich →
   Emit → Self-Check). Each stage must satisfy its validation criteria before the
   next stage begins. If a stage's validation criteria are not satisfied, the skill
   must not proceed to the next stage. Completed stages are reported in order via
   TodoWrite.
```

### New Criterion 10 (appended after existing criteria)
```
10. No output files are written unless Stage 1 through Stage 4 validations have
    passed. Stage 5 (File Emission) is only entered after all pre-write stages
    are validated.
```

### Risk: Low
Updates one criterion text (does not remove the §8 self-check requirement — it is now Stage 6). Adds one criterion to strengthen the pre-write gate.

---

## Non-Modified Sections

The following sections are explicitly NOT modified by this plan:
- `tasklist.md` command file (command layer entirely unchanged)
- §5.4 Input Validation (command-layer validation; skill-layer validation is separate)
- §8 Sprint Compatibility Self-Check (content unchanged; now positioned as Stage 6)
- §6A Index File Template (output schema unchanged)
- §6B Phase File Template (output schema unchanged)
- §7 Style Rules (unchanged)
- §7.1-§7.3 Lint-architecture checks (unchanged)
- All `rules/` and `templates/` extracted reference files (unchanged)

---

## Implementation Order

1. Apply M1 + M5 simultaneously to §9 (acceptance criteria update — one edit block)
2. Apply M2 + M4 simultaneously to §6.2 (parity note + per-stage criteria table — one edit block)
3. Apply M3 to §4.3 (replace 8-step list with 6-stage named contract)
4. Verify: `make lint-architecture` still passes (no structural changes that would affect checks)
5. Verify: manual read-through of SKILL.md flow confirms stage names align across §4.3 and §6.2

---

## Validation After Implementation

| Check | Method | Pass Criteria |
|-------|--------|--------------|
| Lint-architecture | `make lint-architecture` | No errors |
| §4.3 alignment with §6.2 | Manual review | 6 stage names match in both sections |
| §9 Criterion 6 covers §8 | Manual review | Criterion text references Stage 6 (Self-Check) |
| Parity note clarity | Manual review | Note clearly states "skill packaging addition" |
| Per-stage table completeness | Manual review | All 6 stages have validation criteria |


# Source: /config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy2-clarification-rules/refactor-plan.md

# Refactor Plan — Strategy 2: Single-Pass Clarification Rules

**Adversarial Pipeline Steps 4 & 5**
**Date**: 2026-03-04

---

## 1. Refactored Strategy Text (Implementation-Ready)

**Original strategy statement (from `tasklist-spec-integration-strategies.md`):**
> From `taskbuilder`'s "ask once for gaps" principle, adapt to v1.0 non-interactive mode:
> - If required input is missing/ambiguous, perform one deterministic fallback resolution attempt.
> - If still unresolved, fail with a concise, structured error listing exact missing fields.

**Refactored strategy statement:**

> Single-Pass Clarification Rules for Missing/Ambiguous Inputs (Non-Interactive Mode)
>
> The command layer distinguishes two failure classes at validation time:
>
> **Class 1 — Unrecoverable missing inputs** (Checks 1-3): If `<roadmap-path>` does not resolve to a readable file, if `--spec` is provided but does not resolve, or if the `--output` parent directory does not exist, fail immediately with a structured validation error. No fallback attempt is made.
>
> **Class 2 — Ambiguous/derivable inputs** (Check 4): If `--output` is absent, execute exactly one deterministic TASKLIST_ROOT derivation pass using the §3.1 algorithm. If derivation succeeds, proceed normally. If derivation fails (no TASKLIST_ROOT marker found, ambiguous path pattern, or conflicting markers), fail with a structured validation error.
>
> In all failure cases, the command emits a deterministic structured error block — not LLM-generated prose — in the following format:
>
> ```
> TASKLIST VALIDATION ERROR
> Check: <check number and name>
> Expected: <what was required>
> Received: <what was found, or "absent">
> Fallback attempted: <yes|no>
> Fallback result: <success|failed: <reason>>
> Action: <what the operator should do>
> ```
>
> The command exits without invoking the skill. No partial output is written.

**Rationale for each element:**

- "Two failure classes" — resolves the debate ambiguity: fallback applies only where algorithmic recovery is possible
- "Exactly one" — preserves the one-pass constraint; prevents retry loops
- "Deterministic structured error block — not LLM-generated prose" — addresses the debate's requirement for determinism (pipeline PRD FR-3)
- "The command exits without invoking the skill. No partial output is written." — makes the fail-fast guarantee explicit

---

## 2. Compatibility Confirmation

| Constraint | Status |
|-----------|--------|
| No interactive mode | Confirmed: no user prompt, no input request |
| No new generator features | Confirmed: skill layer untouched |
| Exact functional parity (valid inputs) | Confirmed: behavior on valid inputs unchanged |
| Fail-fast (pipeline PRD NFR) | Confirmed: explicit |
| Deterministic output (pipeline PRD FR-3) | Confirmed: error format specified, not free text |

---

## 3. Strongest Arguments FOR (Final Summary)

**F1 — Closes a genuine spec gap**
The spec currently has no defined behavior for validation failure. This gap produces variable, unreliable output in CI environments. Closing it is a correctness improvement, not a feature addition.

**F2 — Strictly non-interactive**
The taskbuilder "ask once for gaps" pattern has been correctly de-interactivized. The one-pass fallback is a deterministic algorithm. The structured error is output, not a user prompt. The non-interactive invariant is fully preserved.

**F3 — CI/automation value is concrete**
A structured, deterministic error block with named fields (check, expected, received, action) is directly parseable by CI log processors, monitoring tools, and operators reading a tty. This is a meaningful quality improvement over LLM-generated prose that varies between invocations.

**F4 — Aligns with pipeline PRD**
The pipeline PRD (FR-3, NFR Reliability, NFR Operator Clarity) already requires deterministic, fail-fast behavior at the pipeline level. Strategy 2 extends this requirement down to the command validation layer, making the system consistent with its own stated NFRs.

**F5 — Zero generator output risk**
The change is confined to the command layer pre-flight. Under no circumstances does it affect the skill execution, output templates, self-check, or any artifact content.

---

## 4. Strongest Arguments AGAINST / Risks (Final Summary)

**A1 — As-written, underspecified (mitigated by refactored text)**
The original strategy text is too vague to implement deterministically. "One deterministic fallback resolution attempt" applied uniformly to all four validation checks is incorrect — only Check 4 has a meaningful fallback. The refactored text resolves this by explicitly distinguishing failure classes.

**A2 — Format must be deterministic, not LLM prose (mitigated by refactored text)**
Without a specified error format, the structured error becomes LLM-generated free text, violating the pipeline PRD's determinism requirement. The refactored text specifies the exact format.

**A3 — Risk of implementer scope creep**
Once a "fallback resolution" mechanism is in the spec, future implementers may add additional fallback attempts or heuristics. The "exactly one" constraint and the two-class taxonomy are the primary safeguards. These should be treated as absolute constraints in implementation review.

**Residual risk (low)**: The error format specified is a text block embedded in command output. If the command outputs this block to stdout (mixed with normal output), CI parsers may have difficulty distinguishing error output from informational output. Recommendation: this block should go to stderr. This is a detail that should be noted in implementation but does not require a spec change at this level.

---

## 5. Specific Spec Patch Locations and Wording

### Patch 1: §5.4 Input Validation (primary patch)

**File**: `src/superclaude/commands/tasklist.md`
**Section**: `## Input Validation`
**Action**: Replace the current four-item list with the expanded version below.

**Current text:**
```markdown
Before invoking the skill, the command validates:

1. `<roadmap-path>` resolves to a readable file
2. If `--spec` provided, it resolves to a readable file
3. If `--output` provided, the parent directory exists
4. If `--output` not provided, derive `TASKLIST_ROOT` from roadmap content using the §3.1 algorithm
```

**Replacement text:**
```markdown
Before invoking the skill, the command validates inputs in two failure classes:

**Class 1 — Unrecoverable (fail immediately):**
1. `<roadmap-path>` resolves to a readable file — if not, fail with `TASKLIST VALIDATION ERROR` (Check 1)
2. If `--spec` provided, it resolves to a readable file — if not, fail with `TASKLIST VALIDATION ERROR` (Check 2)
3. If `--output` provided, the parent directory exists — if not, fail with `TASKLIST VALIDATION ERROR` (Check 3)

**Class 2 — Derivable (one-pass fallback allowed):**
4. If `--output` not provided: execute exactly one TASKLIST_ROOT derivation pass using the §3.1 algorithm.
   - If derivation succeeds: proceed with derived path.
   - If derivation fails (no marker found, ambiguous result, or conflicting markers): fail with `TASKLIST VALIDATION ERROR` (Check 4). No retry.

**Validation error format** (all checks, deterministic, emitted to stderr):
```
TASKLIST VALIDATION ERROR
Check: <N> — <check name>
Expected: <what was required>
Received: <what was found, or "absent">
Fallback attempted: <yes|no>
Fallback result: <success|failed: <reason>> (omit if Fallback attempted: no)
Action: <what the operator should do to resolve>
```
On any validation failure, the command exits without invoking the skill. No partial output is written.
```

---

### Patch 2: §5.6 Boundaries — Will (additive patch)

**File**: `src/superclaude/commands/tasklist.md`
**Section**: `## Boundaries` → `**Will:**`
**Action**: Add one item to the existing Will list.

**Current Will list:**
```markdown
**Will:**
- Parse and validate input arguments
- Derive TASKLIST_ROOT from roadmap content
- Invoke the skill with validated context
- Report generated file paths on completion
```

**Replacement Will list:**
```markdown
**Will:**
- Parse and validate input arguments
- Derive TASKLIST_ROOT from roadmap content (one attempt; fail-fast if unresolvable)
- Emit deterministic structured validation errors to stderr on any validation failure
- Invoke the skill with validated context (only on full validation pass)
- Report generated file paths on completion
```

---

### Patch 3: `sc-tasklist-command-spec-v1.0.md` §5.4 (spec document patch)

**File**: `.dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md`
**Section**: `### 5.4 Input Validation (Command Layer)`
**Action**: Expand with failure class taxonomy and error format. Wording mirrors Patch 1 above, adapted to prose spec style.

**Replacement text:**
```markdown
### 5.4 Input Validation (Command Layer)

Before invoking the skill, the command validates inputs and classifies failures into two classes.

**Class 1 — Unrecoverable**: Fail immediately without recovery attempt.
1. `<roadmap-path>` resolves to a readable file
2. If `--spec` provided, it resolves to a readable file
3. If `--output` provided, the parent directory exists

**Class 2 — Derivable**: One deterministic fallback attempt permitted; fail-fast on failure.
4. If `--output` not provided: execute exactly one TASKLIST_ROOT derivation pass using the §3.1 algorithm. If derivation fails, fail-fast.

All validation failures emit a deterministic structured error to stderr in the following format:

```
TASKLIST VALIDATION ERROR
Check: <N> — <check name>
Expected: <what was required>
Received: <what was found, or "absent">
Fallback attempted: <yes|no>
Fallback result: <success|failed: <reason>>
Action: <corrective action for the operator>
```

On validation failure the command exits without invoking the skill and without writing any output files.
```

---

### Patch 4: `sc-tasklist-command-spec-v1.0.md` §5.6 Boundaries (spec document patch)

**File**: `.dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md`
**Section**: `### 5.6 Boundaries` → Will list
**Action**: Update the Derive line and add structured error line.

**Replacement:**
```markdown
**Will:**
- Parse and validate input arguments
- Derive TASKLIST_ROOT from roadmap content (exactly one attempt; fail-fast if unresolvable)
- Emit deterministic structured validation errors to stderr on any validation failure
- Invoke the skill with validated context
- Report generated file paths on completion
```

---

### Patch 5: `tasklist-spec-integration-strategies.md` Strategy 2 section (strategy document update)

**File**: `.dev/releases/current/v2.07-tasklist-v1/tasklist-spec-integration-strategies.md`
**Section**: `## 2) Add Single-Pass Clarification Rules for missing inputs (non-interactive fallback)`
**Action**: Replace the Concrete spec changes subsection with the tightened version.

**Current text:**
```markdown
### Concrete spec changes
- Expand §5.4 Input Validation with:
  - "One-pass resolution for ambiguous path/state; otherwise fail-fast with actionable diagnostics."
- Add to Boundaries (Will):
  - "Return structured validation errors (missing roadmap/spec/output derivation failure)."
```

**Replacement text:**
```markdown
### Concrete spec changes
- Replace §5.4 Input Validation with two-class failure taxonomy:
  - Class 1 (Checks 1-3): unrecoverable; fail immediately with structured error
  - Class 2 (Check 4, TASKLIST_ROOT derivation): one-pass §3.1 attempt; fail-fast on failure
- Add deterministic error format to §5.4 (see refactor-plan.md for exact wording)
- Update §5.6 Boundaries (Will) to: "Emit deterministic structured validation errors to stderr on any validation failure"
- Note: error format is deterministic text block emitted to stderr, not LLM-generated prose
```

---

## 6. Implementation Notes

### Risk level by patch
| Patch | Risk | Reason |
|-------|------|--------|
| Patch 1 | Low | Command file addition; no behavior change on valid inputs |
| Patch 2 | Low | Will list is documentation; no behavior change |
| Patch 3 | Low | Spec document; no code impact |
| Patch 4 | Low | Spec document; no code impact |
| Patch 5 | Low | Strategy document; no code impact |

### Implementation constraints (absolute)
1. Error format MUST be emitted to stderr, not stdout (recommended practice; spec does not currently specify stream — implementers should default to stderr)
2. Fallback is "exactly one" — no retry loops, no progressive resolution attempts
3. On failure, zero files written — not even a partial index file
4. Format fields are mandatory — no optional fields, no LLM prose substitution

### Testing requirement added by this strategy
- Test case: valid inputs → no error block emitted, normal output produced
- Test case: Check 1 fail → error block on stderr, exit code non-zero, no files written
- Test case: Check 4 fail (no TASKLIST_ROOT) → error block on stderr, exit code non-zero, no files written
- Test case: Check 4 success (TASKLIST_ROOT derivable) → no error block, normal output


# Source: /config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy3-task-quality-gate/refactor-plan.md

# Refactor Plan — Strategy 3: Self-Contained Task Item Quality Gate

**Pipeline**: sc:adversarial — Step 4 of 5
**Date**: 2026-03-04
**Verdict**: MODIFY (with M1-M4 modifications)
**Target spec**: `sc-tasklist-command-spec-v1.0.md`
**Target skill**: `sc-tasklist-protocol/SKILL.md` (the v3.0 generator reformatted as a skill)

---

## Integration Points

### IP-1: §7 Style Rules — Add Standalone Task Rule
**Risk**: Low
**Type**: Additive (new rule in existing section)
**Target section**: SKILL.md → `## Style Rules` (verbatim from v3.0 §7)

The existing §7 Style Rules govern formatting (checkbox syntax, ID format, metadata field order). This rule adds a content quality constraint.

**Patch text to add** (add as the last rule in §7 or as a new sub-section §7.N):

```markdown
### §7.N Standalone Task Requirement

Each generated task description must be standalone and action-oriented.
A task is standalone when it satisfies ALL of the following:

1. **Named artifact or target**: The description names the specific file,
   function, endpoint, or component being operated on. Generic phrases
   like "implement the feature" or "update the system" are prohibited.

2. **Session-start executable**: An agent beginning a fresh session
   with only the phase file can begin execution without external
   conversational context. The task must not rely on "as discussed",
   "the above approach", or implicit references from prior messages.

3. **Action verb + explicit object**: Imperative verb + specific target.
   Acceptable: "Add `rateLimit()` middleware to `src/middleware/auth.ts`".
   Prohibited: "Add the middleware we talked about".

4. **No cross-task prose dependency**: The task description must not
   reference information available only in another task's description.
   Shared context belongs in a roadmap-referenced file, not in task prose.

**Enforcement**: Before emitting each task, confirm it satisfies all four
criteria. If it does not, revise the description until it does.
Do NOT emit non-standalone tasks.
```

---

### IP-2: §8 Sprint Compatibility Self-Check — Add Standalone Gate
**Risk**: Low
**Type**: Additive (new check in existing self-check section)
**Target section**: SKILL.md → `## Sprint Compatibility Self-Check`

The existing §8 checks are structural (file existence, heading regex, ID format, contiguous numbering). This adds a generation-discipline check.

**Patch text to add** (add as a new check item in §8):

```markdown
### §8.N Task Standalone Check (Generation-Time)

During task emission (not post-hoc), verify for each task:

- [ ] Description names at least one specific artifact, file, function,
      or component (not generic "the feature" or "the component")
- [ ] No pronoun/reference to external conversation ("as discussed",
      "the above", "we agreed", "from our earlier session")
- [ ] Description contains an imperative verb with an explicit direct object

**If any check fails**: revise the task description before proceeding
to the next task. Do not accumulate violations.

Note: This check is generation-discipline (enforced during generation),
not a structural parse check. It cannot be automated by `make lint-architecture`.
```

---

### IP-3: §9 Acceptance Criteria — Add Content Quality Criterion
**Risk**: Low
**Type**: Additive (new criterion in existing list)
**Target section**: `sc-tasklist-command-spec-v1.0.md` → `## 9. Acceptance Criteria`

Add as criterion 8 (after the existing 7):

```markdown
8. Every generated task description is standalone per §7.N: names a
   specific artifact or target, contains no external-context references,
   and is executable by an agent starting a fresh session using only
   the generated phase file.
```

---

### IP-4: §9 Parity Criterion — Add Clarifying Note
**Risk**: Low
**Type**: Clarifying annotation (does not change functional behavior)
**Target section**: `sc-tasklist-command-spec-v1.0.md` → `## 9. Acceptance Criteria` → criterion 7

Current text:
```
7. Functional parity: output is identical to running the v3.0 generator prompt manually
```

Modified text:
```
7. Functional parity: output is structurally and schematically identical to running
   the v3.0 generator prompt manually (same file format, task ID scheme, metadata
   fields, and phase file structure). Note: §7.N standalone quality rules may produce
   improved task description prose versus a raw v3.0 run; this is intentional and
   within parity scope as it does not change any schema, structural element, or
   output file format.
```

---

### IP-5: Integration Strategies Doc — Add v1.1 Deferral Note
**Risk**: None (documentation-only)
**Type**: Annotation
**Target**: `tasklist-spec-integration-strategies.md` → Strategy 3 section

Add after the existing "Concrete spec changes" block:

```markdown
### Schema expansion deferred to v1.1
The full implementation of this principle — adding `Context:`, `Verify:`, and
`Blocked-Until:` fields per task (see `taskbuilder-integration-proposals.md`
Proposal 1) — is deferred to v1.1. v1.0 adopts the generation rule and
acceptance criterion only. The v1.1 schema expansion completes the enforcement
chain with structural field-level verifiability.
```

---

## Implementation Order

| Step | Action | File | Risk | Dependency |
|------|--------|------|------|------------|
| 1 | Add §7.N Standalone Task Requirement | SKILL.md | Low | None |
| 2 | Add §8.N Task Standalone Check | SKILL.md | Low | IP-1 complete |
| 3 | Add §9 criterion 8 | command spec v1.0 | Low | IP-1, IP-2 complete |
| 4 | Modify §9 criterion 7 (parity note) | command spec v1.0 | Low | None |
| 5 | Add v1.1 deferral note | integration strategies doc | None | None |

Steps 1-2 must be sequential (§8 references §7.N). Steps 3-5 are independent of each other and can be applied in any order after steps 1-2.

---

## Risk Assessment

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Parity dispute from strict reading of criterion 7 | Medium | Medium | IP-4 resolves by explicitly scoping parity to schema/structure |
| Generator inconsistency on "standalone" interpretation | Medium | Low | IP-1 provides 4 specific criteria; minimizes LLM interpretation variance |
| §8 check perceived as unenforceable | High | Low | Check text explicitly notes it is generation-discipline, not parse-level; sets expectation correctly |
| Scope creep into Proposal 1 fields | Medium | Medium | IP-5 documents the boundary explicitly and defers schema to v1.1 |

---

## What This Does NOT Change

- Task ID format (`T<PP>.<TT>`)
- Phase file naming convention
- `tasklist-index.md` structure
- `make lint-architecture` checks (none of these changes affect lintable structure)
- Installation behavior
- Command layer (`tasklist.md`)
- Input validation (§5.4)
- MCP server usage
- The extracted reference files (`rules/`, `templates/`)
- Any existing §8 structural checks (new check is additive only)

---

## v1.1 Roadmap Item (Out of Scope for This Patch)

The following is explicitly deferred and should be tracked as a v1.1 enhancement:

**v1.1: Add Self-Contained Task Schema Fields**
- Add `Context:` field to §6B task format (files/artifacts to read before starting)
- Add `Verify:` field to §6B task format (inline acceptance criteria)
- Add `Blocked-Until:` field to §6B task format (prerequisite task IDs with status)
- Extend §8 self-check to structurally validate `Context:` and `Verify:` field presence
- Update §9 acceptance criteria to include field presence validation
- Source: `taskbuilder-integration-proposals.md` Proposal 1

This v1.1 change completes the enforcement chain that Strategy 3 (modified) begins.


# Source: /config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy4-inline-verification/refactor-plan.md

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


# Source: /config/workspace/SuperClaude_Framework/docs/generated/adversarial/strategy-5-pre-write-checklist/refactor-plan.md

# Refactor Plan — Strategy 5: Pre-Write Structural Validation Checklist

**Pipeline Step**: 4 of 5
**Date**: 2026-03-04
**Decision**: Adopt modified (checks 9–12 added to §8; atomic write declaration added to §9)
**Target files**:
- `sc-tasklist-command-spec-v1.0.md` (PRD) — Acceptance Criteria §9, Open Questions §10
- `Tasklist-Generator-Prompt-v2.1-unified.md` (v3.0 generator) — §8, §9

---

## Integration Points

### File 1: `Tasklist-Generator-Prompt-v2.1-unified.md`

**Location**: `/config/workspace/SuperClaude_Framework/.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md`

This is the canonical v3.0 generator. It is the source-of-truth that will be reformatted into `SKILL.md`. Changes here must be carried forward into SKILL.md.

#### Integration Point 1A: §8 Sprint Compatibility Self-Check — add 4 new checks

**Current §8 (lines 695–708):**
```markdown
## 8) Sprint Compatibility Self-Check (Mandatory)

Before finalizing output, verify all of the following:

1. `tasklist-index.md` exists and contains a "Phase Files" table
2. Every phase file referenced in the index exists in the output bundle
3. Phase numbers are contiguous (1, 2, 3, ..., N) with no gaps
4. All task IDs match `T<PP>.<TT>` format (zero-padded, 2-digit)
5. Every phase file starts with `# Phase N — <Name>` (level 1 heading, em-dash separator)
6. Every phase file ends with an end-of-phase checkpoint section
7. No phase file contains Deliverable Registry, Traceability Matrix, or template sections
8. The index contains literal phase filenames (e.g., `phase-1-tasklist.md`) in at least one table cell

If any check fails, fix it before returning the output.
```

**Target state (after patch):**
```markdown
## 8) Sprint Compatibility Self-Check (Mandatory)

Before finalizing output, verify all of the following:

1. `tasklist-index.md` exists and contains a "Phase Files" table
2. Every phase file referenced in the index exists in the output bundle
3. Phase numbers are contiguous (1, 2, 3, ..., N) with no gaps
4. All task IDs match `T<PP>.<TT>` format (zero-padded, 2-digit)
5. Every phase file starts with `# Phase N — <Name>` (level 1 heading, em-dash separator)
6. Every phase file ends with an end-of-phase checkpoint section
7. No phase file contains Deliverable Registry, Traceability Matrix, or template sections
8. The index contains literal phase filenames (e.g., `phase-1-tasklist.md`) in at least one table cell

### 8.1 Semantic Quality Gate (Pre-Write, Mandatory)

Before issuing any Write() call, additionally verify:

9. Every task in every phase file has non-empty values for: Effort, Risk, Tier, Confidence, and Verification Method.
10. All Deliverable IDs (D-####) are globally unique across the entire bundle — no duplicate D-#### values across different phases or tasks.
11. No task has a placeholder or empty description. Reject any task with description text of "TBD", "TODO", or a title-only entry with no body.
12. Every task has at least one assigned Roadmap Item ID (R-###). No orphan tasks without traceability.

If any check 1–12 fails, fix it before writing any output file.
```

**Risk level**: Low. Adds 4 checks as a named subsection of §8. Does not modify existing check text. The new subsection header `### 8.1 Semantic Quality Gate` provides CI-testability anchor.

**Diff size**: +12 lines

---

#### Integration Point 1B: §9 Final Output Constraint — add atomic write declaration

**Current §9 (lines 712–714):**
```markdown
## 9) Final Output Constraint

Return **only** the generated multi-file bundle (`tasklist-index.md` + `phase-N-tasklist.md` files). No preamble, no analysis, no mention of hidden proposals, no debate references. Write each file to its path under `TASKLIST_ROOT/`.
```

**Target state (after patch):**
```markdown
## 9) Final Output Constraint

Return **only** the generated multi-file bundle (`tasklist-index.md` + `phase-N-tasklist.md` files). No preamble, no analysis, no mention of hidden proposals, no debate references. Write each file to its path under `TASKLIST_ROOT/`.

**Write atomicity**: The generator validates the complete in-memory bundle against §8 (including §8.1) before issuing any Write() call. All files are written only after the full bundle passes validation. No partial bundle writes are permitted.
```

**Risk level**: Low. Additive declaration. Does not change any existing text. Commits to atomic write semantics explicitly.

**Diff size**: +3 lines

---

### File 2: `sc-tasklist-command-spec-v1.0.md` (PRD)

**Location**: `/config/workspace/SuperClaude_Framework/.dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md`

#### Integration Point 2A: §9 Acceptance Criteria — add criterion for semantic gate

**Current §9 Acceptance Criteria (last item is #7):**
```markdown
7. Functional parity: output is identical to running the v3.0 generator prompt manually
```

**Target state (add item 8):**
```markdown
7. Functional parity: output is identical to running the v3.0 generator prompt manually
8. Pre-write semantic quality gate passes before any file is written: all tasks have complete metadata fields, all Deliverable IDs are globally unique, no placeholder descriptions exist, and every task has at least one R-### reference.
```

**Risk level**: Low. Additive acceptance criterion. Does not modify existing criteria.

**Diff size**: +2 lines

---

#### Integration Point 2B: §10 Open Questions — resolve atomicity question

**Current §10 Open Questions** — no question about write atomicity exists today.

**Target state (add new question/resolution):**
```markdown
4. **Should Write() calls be atomic (all files after validation) or incremental (file by file)?**
   Resolution: Atomic. The §8.1 Semantic Quality Gate validates the full in-memory bundle before any Write() call. Incremental writing is prohibited to prevent partial bundle states.
```

**Risk level**: Low. Documents a design decision that affects future implementations.

**Diff size**: +4 lines

---

## Integration Sequence

Execute in this order to maintain consistency:

1. Patch `Tasklist-Generator-Prompt-v2.1-unified.md` §8 (add §8.1 checks 9–12)
2. Patch `Tasklist-Generator-Prompt-v2.1-unified.md` §9 (add atomic write declaration)
3. Patch `sc-tasklist-command-spec-v1.0.md` §9 (add acceptance criterion 8)
4. Patch `sc-tasklist-command-spec-v1.0.md` §10 (add atomicity resolution)
5. When SKILL.md is authored from the v3.0 generator, carry forward §8.1 and §9 atomic write declaration verbatim into SKILL.md §8 and §9.

---

## What NOT to change

- §8 checks 1–8 remain verbatim. No reordering, no wording changes.
- §7 Style Rules unchanged.
- §6A, §6B template content unchanged.
- §5 Enrichment algorithm unchanged (no behavioral generation changes).
- §4.5 Task Splitting algorithm unchanged (behavioral changes deferred to v1.1).
- No new top-level section (§7.5) created — §8.1 subsection is sufficient.

---

## Validation of this refactor plan

After applying the four patches, the following must be true:

| Verification | Method |
|---|---|
| §8 checks 1–8 unchanged | Text diff against original |
| §8.1 contains exactly checks 9–12 | Text diff |
| §9 contains atomic write declaration | Text diff |
| PRD §9 contains criterion 8 | Text diff |
| No check in §8.1 duplicates any check in §8 checks 1–8 | Manual review of diff-analysis.md overlap table |
| Semantic checks 9–12 do not include behavioral generation constraints | Verify against exclusion list in base-selection.md §4.2 |
| SKILL.md (when authored) carries forward §8.1 verbatim | Structural mapping table in sc-tasklist-command-spec-v1.0.md §6.2 |

