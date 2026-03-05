<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant A (refactor-plan-merged.md) — Score: 0.784 -->
<!-- Non-base: Variant B (tasklist-spec-integration-strategies.md) — Score: 0.691 -->
<!-- Merge date: 2026-03-04 -->

# Unified Refactor Plan — sc-tasklist v1.0 Spec Improvements

**Date**: 2026-03-04
**Target spec**: `sc-tasklist-command-spec-v1.0.md`
**Target skill**: `sc-tasklist-protocol/SKILL.md`
**Status**: All 5 strategies post-debate, implementation-ready

---

<!-- Source: Variant B, Executive Summary — merged per Change #3 -->
## Executive Summary

The base spec is already strong on command/skill separation, deterministic flow, and parity constraints. The best compatible integrations from `taskbuilder.md` are **execution-hardening patterns** that preserve v1.0 parity while reducing ambiguity, rollover risk, and validation drift.

All 5 strategies underwent structured adversarial debate (Opus advocate vs Haiku critic, followed by cross-variant adversarial comparison). Results refined each proposal — no strategy was fully rejected; all received conditional acceptance with scope narrowing to respect v1.0 parity constraints.

### Debate Verdict Summary

| # | Strategy | Verdict | Key Modification |
|---|----------|---------|-----------------|
| 1 | Stage Completion Reporting Contract | **CONDITIONAL ACCEPT** | Hybrid approach: structural gates for deterministic checks + TodoWrite observability for semantic |
| 2 | Generation Notes + Empty-File Guard | **CRITIC WINS w/ conditions** | Reduced to passive Generation Notes + empty-file guard + 2-field error format; full error taxonomy deferred to v1.1 |
| 3 | Minimum Task Specificity Rule | **CONDITIONAL ACCEPT** | 3 criteria (artifact reference + concrete verb + no cross-task dependency); session-start executability deferred to v1.1 |
| 4 | Acceptance Criteria Quality Rules | **CONDITIONAL ACCEPT** | Tighten existing fields with tier-proportional enforcement + non-invention constraint; no new fields |
| 5 | Extended Pre-Write Validation | **CONDITIONAL ACCEPT** | Unified checks 9-17 (semantic 9-12 + structural 13-17) + atomic write declaration |

---

<!-- Source: Base (original, modified) — restructured per Change #1, renamed per Change #2 -->
## Strategy 1: Stage Completion Reporting Contract

<!-- Source: Variant B, Strategy 1 verdict — merged per Change #3 -->
> **Debate verdict**: CONDITIONAL ACCEPT — Hybrid approach adopted. Accept structural gating for deterministic predicates + TodoWrite observability for semantic checks. Pure halt-on-failure rejected as circular self-validation; pure observability-only rejected as insufficient for cost-effective error detection.

**Decision**: ADOPT with modifications
**Token cost**: ~200 additional tokens in SKILL.md

### What was rejected (from debate)
<!-- Source: Variant B, Strategy 1 rejections — merged per Change #3 -->
- Per-stage halt-on-failure for semantic properties — the same model that produces output cannot reliably validate its own semantic correctness (circular self-validation)
- CI/CD gate infrastructure — premature for v1.0; deferred to v2.0
- "Deterministic re-runs" framing — determinism is a property of the function, not of observing intermediate state

### Modification Inventory

| ID | Modification | Target Section | Risk | Order |
|----|-------------|---------------|------|-------|
| M1 | Reword "halts" to hybrid gating language | §9 Acceptance Criteria | Low | 1 |
| M2 | Add per-stage validation criteria table | §6.2 (new subsection) | Low | 2 |
| M3 | Canonicalize 6-stage names in §4.3 | §4.3 Invocation Flow | Low | 3 |
| M4 | Add parity clarification note | §6.2 Content | Very Low | 4 |
| M5 | Update §9 Criterion 6 to cover stage reporting | §9 Acceptance Criteria | Low | 1 (with M1) |

### Integration Point 1: §4.3 Invocation Flow (M3)

<!-- Source: Base (original, modified) — hybrid gating per Change #4 -->
#### Current text (conceptual — 8-step numbered list)
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

#### Replacement text (M3 applied — named stage contract with hybrid gating)
```
SKILL execution — Stage Completion Reporting Contract:

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

  Stage reporting: Report completed stages in order using TodoWrite as each
  stage passes. Stage reporting is observational (debugging/progress tracking).

  Structural gates: For deterministic, structurally verifiable properties
  (non-empty output, valid ID format, field presence), the skill checks
  minimal viability before advancing. For semantic properties (content
  quality, prose adequacy), validation is advisory — logged but not blocking.
```

#### Risk: Low
No output schema change. No command layer change. Replaces implicit ordering with explicit reporting contract.

### Integration Point 2: §6.2 Content (M2 + M4)

<!-- Source: Base (original) -->
#### Current text (relevant sentence)
```
The SKILL.md body is the full v3.0 generator prompt — sections §0 through §9 plus the
Appendix — reformatted into skill convention but functionally identical.
```

#### Additional text to append (M4 parity note + M2 reference)
```
Note on stage completion reporting (skill packaging addition): The stage
completion reporting contract (§4.3) is a reliability mechanism added during
skill packaging. It constrains execution behavior without altering the
generation algorithm, task schema, or output structure. The v3.0 generator
did not include per-stage validation semantics; this is intentional hardening
for automated sprint execution contexts.

The following per-stage validation criteria are used for structural gating
and observational reporting:

| Stage | Name | Validation Criteria |
|-------|------|---------------------|
| 1 | Input Ingest | Roadmap text non-empty; required sections (phases/items) present; file read succeeded |
| 2 | Parse + Phase Bucketing | Every roadmap item assigned to exactly one phase; no ambiguous assignments remain unresolved; phase count ≥ 1 |
| 3 | Task Conversion | All roadmap items converted to task stubs; T<PP>.<TT> IDs assigned with no collisions; task titles non-empty |
| 4 | Enrichment | All tasks have non-empty: Effort (XS/S/M/L/XL), Risk (low/moderate/high), Tier (STANDARD/STRICT/EXEMPT/LIGHT), Confidence score |
| 5 | File Emission | tasklist-index.md written; all phase files referenced in index exist on disk; no extra phase files written |
| 6 | Self-Check | All Sprint Compatibility Self-Check assertions (§8) pass; no blocking failures |

Structural gate behavior: If a stage's structurally verifiable criteria are
not satisfied (e.g., empty output, missing required fields, ID collisions),
the skill reports the failed criterion and attempts correction before
advancing. Semantic criteria are reported via TodoWrite but do not block
advancement.
```

#### Risk: Low
Additive only. Does not change any existing content.

### Integration Point 3: §9 Acceptance Criteria (M1 + M5)

<!-- Source: Base (original, modified) — hybrid language per Change #4 -->
#### Current Criterion 6
```
6. The Sprint Compatibility Self-Check (§8) runs before output is finalized
```

#### Replacement (M1 + M5 applied — hybrid gating)
```
6. Generation executes in stage order (Ingest → Parse/Bucket → Convert → Enrich →
   Emit → Self-Check). Each stage reports completion via TodoWrite. Structurally
   verifiable criteria (field presence, ID format, file existence) are checked
   before advancing; semantic criteria are logged as advisory. Completed stages
   are reported in order.
```

#### New Criterion 10 (appended)
```
10. No output files are written unless Stage 1 through Stage 4 structural
    validations have passed. Stage 5 (File Emission) is only entered after
    all pre-write stages report completion.
```

#### Risk: Low
Updates one criterion text. Adds one criterion to strengthen the pre-write gate.

### Non-Modified Sections
<!-- Source: Base (original) -->
- `tasklist.md` command file (command layer entirely unchanged)
- §5.4 Input Validation (command-layer validation; skill-layer validation is separate)
- §8 Sprint Compatibility Self-Check content (unchanged; now positioned as Stage 6)
- §6A Index File Template (output schema unchanged)
- §6B Phase File Template (output schema unchanged)
- §7 Style Rules (unchanged by this strategy)
- All `rules/` and `templates/` extracted reference files (unchanged)

### Risk Assessment
<!-- Source: Base (original) -->

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Structural gate false positives | Medium | Low | Gates check minimal viability only (non-empty, valid format), not content quality |
| TodoWrite reporting overhead | Low | Low | Reporting is lightweight; 6 status updates per generation |
| Hybrid gating confusion | Low | Medium | Clear documentation of which checks gate vs. observe |

### Validation After Implementation

| Check | Method | Pass Criteria |
|-------|--------|--------------|
| §4.3 alignment with §6.2 | Manual review | 6 stage names match in both sections |
| §9 Criterion 6 covers reporting | Manual review | Criterion text references stage reporting |
| Parity note clarity | Manual review | Note clearly states "skill packaging addition" |
| Per-stage table completeness | Manual review | All 6 stages have validation criteria |

---

<!-- Source: Base (original, modified) — scope reduced per Change #5 -->
## Strategy 2: Generation Notes + Empty-File Guard

<!-- Source: Variant B, Strategy 2 verdict — merged per Change #3 -->
> **Debate verdict**: CRITIC WINS with conditions — The parity constraint and "works with any roadmap" design intent are decisive. Full fail-fast error taxonomy deferred to v1.1. v1.0 scope: empty-file guard + passive Generation Notes + 2-field error format.

**Decision**: ADOPT (reduced scope)
**Token cost**: ~100 additional tokens in SKILL.md

### What was rejected (from debate)
<!-- Source: Variant B, Strategy 2 rejections — merged per Change #3 -->
- Full 5-patch structured error format — over-prescriptive for v1.0; deferred to v1.1
- Content quality heuristics (min headings, min bullet count) — duplicates the generator's own parsing logic
- Failing on ambiguous input — violates "works with any roadmap" design intent
- `--spec` conflict resolution semantics — separate problem

### Integration Point 1: §5.4 Input Validation

#### Current text
```markdown
Before invoking the skill, the command validates:

1. `<roadmap-path>` resolves to a readable file
2. If `--spec` provided, it resolves to a readable file
3. If `--output` provided, the parent directory exists
4. If `--output` not provided, derive `TASKLIST_ROOT` from roadmap content using the §3.1 algorithm
```

#### Replacement text
```markdown
Before invoking the skill, the command validates:

1. `<roadmap-path>` resolves to a readable, non-empty file (reject 0-byte or whitespace-only files)
2. If `--spec` provided, it resolves to a readable file
3. If `--output` provided, the parent directory exists
4. If `--output` not provided, derive `TASKLIST_ROOT` from roadmap content using the §3.1 algorithm

On validation failure, emit a 2-field error to stderr:

    error_code: <category string, e.g., "EMPTY_INPUT", "MISSING_FILE", "DERIVATION_FAILED">
    message: <human-readable description of what failed and corrective action>

The command exits without invoking the skill. No partial output is written.
```

### Integration Point 2: §6A Index File Template

#### Addition (new optional section)
```markdown
`## Generation Notes` — Lists any fallback behaviors activated during generation
(e.g., default phase bucketing, missing metadata inference). This section is
informational; it does not affect Sprint CLI compatibility.
```

### Non-Modified Sections
- §5.6 Boundaries — no changes to Will/Will Not (structured error claims deferred to v1.1)
- §6B Phase File Template — no output format changes
- Full two-class failure taxonomy with deterministic error blocks — deferred to v1.1

### Risk Assessment

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Empty-file guard insufficient for complex input errors | Medium | Low | Foundation for v1.1 expansion; catches most obvious failure |
| Generation Notes section ignored by consumers | Low | Low | Optional and informational; no dependency |

---

<!-- Source: Base (original, modified) — reduced to 3 criteria per Change #6 -->
## Strategy 3: Minimum Task Specificity Rule

<!-- Source: Variant B, Strategy 3 verdict — merged per Change #3 -->
> **Debate verdict**: CONDITIONAL ACCEPT (reduced) — 3 criteria adopted. Session-start executability deferred to v1.1 as over-constraining for v1.0 parity.

**Decision**: ADOPT (3-criterion version)
**Token cost**: ~0 additional tokens per task (quality rule, not field expansion)

### What was rejected (from debate)
<!-- Source: Variant B, Strategy 3 rejections — merged per Change #3 -->
- "Session-start executable" criterion — may over-constrain legitimate tasks; deferred to v1.1
- Full self-contained prose paragraphs per task — too verbose, breaks TUI rendering
- Embedded `Context:` and `Verify:` fields per task — schema expansion belongs in v1.1
- "No task requires conversational context" criterion — subjective, cannot be mechanically verified

### Integration Point 1: §7 Style Rules — Add Specificity Rule

<!-- Source: Base (original, modified) — criterion 2 removed per Change #6 -->
**Patch text** (add as §7.N):

```markdown
### §7.N Minimum Task Specificity Rule

Each generated task description must satisfy ALL of the following:

1. **Named artifact or target**: The description names the specific file,
   function, endpoint, or component being operated on. Generic phrases
   like "implement the feature" or "update the system" are prohibited.

2. **Action verb + explicit object**: Imperative verb + specific target.
   Acceptable: "Add `rateLimit()` middleware to `src/middleware/auth.ts`".
   Prohibited: "Add the middleware we talked about".

3. **No cross-task prose dependency**: The task description must not
   reference information available only in another task's description.
   Shared context belongs in a roadmap-referenced file, not in task prose.

**Enforcement**: Before emitting each task, confirm it satisfies all three
criteria. If it does not, revise the description until it does.
Do NOT emit non-conforming tasks.
```

### Integration Point 2: §8 Self-Check — Add Specificity Gate

**Patch text** (add as check in §8.1):

```markdown
Task Specificity Check (Generation-Time):

During task emission, verify for each task:

- [ ] Description names at least one specific artifact, file, function,
      or component (not generic "the feature" or "the component")
- [ ] No pronoun/reference to external conversation ("as discussed",
      "the above", "we agreed", "from our earlier session")
- [ ] Description contains an imperative verb with an explicit direct object

If any check fails: revise the task description before proceeding
to the next task.

Note: This check is generation-discipline (enforced during generation),
not a structural parse check.
```

### Integration Point 3: §9 Acceptance Criteria

Add as new criterion:
```markdown
N. Every generated task description is standalone per §7.N: names a
   specific artifact or target, contains no external-context references,
   and uses a concrete action verb with explicit object.
```

### Risk Assessment

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Generator inconsistency on "specificity" interpretation | Medium | Low | 3 specific criteria minimize interpretation variance |
| Scope creep into full standalone fields | Medium | Medium | v1.1 deferral note documents boundary explicitly |

### v1.1 Deferral: Full Self-Contained Task Schema
<!-- Source: Base (original) + Variant B governance — merged per Change #3 -->
The full implementation — adding `Context:`, `Verify:`, and `Blocked-Until:` fields per task — is deferred to v1.1. v1.0 adopts the generation rule and acceptance criterion only. The v1.1 schema expansion completes the enforcement chain with structural field-level verifiability.

---

<!-- Source: Base (original) — preserved with non-invention constraint per R-3 -->
## Strategy 4: Acceptance Criteria Quality Rules

<!-- Source: Variant B, Strategy 4 verdict — merged per Change #3 -->
> **Debate verdict**: CONDITIONAL ACCEPT — Tighten existing fields rather than adding new ones. Critical discovery: v3.0 task format ALREADY has `Acceptance Criteria` (4 bullets) and `Validation` (2 bullets) fields per task in §6B.2. Apply tier-proportional enforcement + non-invention constraint.

**Decision**: ADOPT (modified)
**Token cost**: ~0 additional (quality enforcement on existing fields)

### What was rejected (from debate)
<!-- Source: Variant B, Strategy 4 rejections — merged per Change #3 -->
- New `Verify:` field — redundant with existing Acceptance Criteria + Validation
- Completion gate sentences ("This item cannot be marked done until...") — too verbose
- Generator-produced implementation-specific criteria — hallucination risk

### Integration Point 1: §6B Task Format — Near-Field Completion Criterion

<!-- Source: Base (original) — A's unique contribution U-003 preserved -->
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

Non-invention constraint: Completion criteria must be derived from roadmap content.
Do not invent test commands, file paths, or acceptance states not implied by the roadmap.
If the roadmap provides no verifiable output signal, use:
"Manual check: <specific observable behavior described in roadmap> verified by reviewer."
```

### Integration Point 2: Tier-Proportional Enforcement

<!-- Source: Variant B, Strategy 4 approach — merged per Change #3 -->
```markdown
**Acceptance Criteria Specificity Rules:**
- At least one criterion per task MUST reference a specific artifact (file, test, endpoint, config)
- Generic criteria ("code works", "tests pass", "properly formatted") MUST be replaced with
  specific equivalents ("unit tests in test_auth.py pass", "API returns 200 for valid input")
- Tier-proportional enforcement:
  - STRICT tasks: ALL criteria must be artifact-referencing
  - STANDARD tasks: ≥1 criterion must be artifact-referencing
  - LIGHT and EXEMPT tasks: no minimum
```

### Integration Point 3: §8 Self-Check

Add to §8.1:
```markdown
Acceptance criteria completeness: Every task has at least one Acceptance Criteria
bullet that names a specific, objectively verifiable output. Tasks where ALL
Acceptance Criteria bullets use only non-specific language ("complete", "working",
"pass", "done") MUST be regenerated before output is written.
```

### Risk Assessment

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Generator pads bullet (1) with invented test commands | Medium | Low | Non-invention constraint; manual validation during acceptance |
| Borderline cases in self-check | Medium | Low | Accepted/rejected examples bound the check |
| Self-check causes spurious regeneration | Low | Low | Fallback form ("Manual check:...") always satisfies the rule |

---

<!-- Source: Base (original, modified) — check numbering unified per Change #7 -->
## Strategy 5: Extended Pre-Write Validation

<!-- Source: Variant B, Strategy 5 verdict — merged per Change #3 -->
> **Debate verdict**: CONDITIONAL ACCEPT — Extend existing §8 with unified checks 9-17. Clarify timing as "Pre-Write, Mandatory". Add atomic write declaration.

**Decision**: ADOPT (unified check registry)
**Token cost**: ~150 additional tokens in SKILL.md

### What was rejected (from debate)
<!-- Source: Variant B, Strategy 5 rejections — merged per Change #3 -->
- Creating a separate §7.5 section — duplicates existing §8 structure
- Moving existing checks from §8 to new location — reorganization without value

### Unified Pre-Write Check Registry

<!-- Source: Base (original) checks 9-12 + Variant B checks 13-17 — merged per Change #7 -->

In §8 header, clarify timing:
- Change: "Sprint Compatibility Self-Check" → "Sprint Compatibility Self-Check (Pre-Write, Mandatory)"
- Add: "All checks in this section MUST pass before any `Write()` call. Invalid output is never written."

**Existing checks 1-8**: UNCHANGED.

#### §8.1 Semantic Quality Gate (Pre-Write, Mandatory)

Before issuing any Write() call, additionally verify:

| # | Check | Rationale |
|---|-------|-----------|
| 9 | Every task has non-empty values for: Effort, Risk, Tier, Confidence, and Verification Method | Prevents incomplete metadata in output |
| 10 | All Deliverable IDs (D-####) are globally unique across the entire bundle | Prevents duplicate identifiers across phases |
| 11 | No task has a placeholder or empty description (reject "TBD", "TODO", or title-only) | Prevents incomplete output |
| 12 | Every task has at least one assigned Roadmap Item ID (R-###) | Prevents orphan tasks without traceability |

#### §8.2 Structural Quality Gate (Pre-Write, Mandatory)

| # | Check | Rationale |
|---|-------|-----------|
| 13 | Task count bounds: every phase has ≥1 and ≤25 tasks | Prevents empty phases and unwieldy mega-phases |
| 14 | Clarification Task adjacency: ⚠️ tasks appear immediately before their blocked task | Prevents orphaned clarification items |
| 15 | Circular dependency detection: no A→B→C→A chains | Prevents unexecutable dependency graphs |
| 16 | XL splitting enforcement: EFFORT=XL tasks must have subtasks | Enforces decomposition time-boxing |
| 17 | Confidence bar format consistency: all use `██░░░ N%` pattern | Prevents format drift across phases |

If any check 1–17 fails, fix it before writing any output file.

### Atomic Write Declaration

<!-- Source: Base (original) — preserved per R-4 -->
Add to §9 Final Output Constraint:
```markdown
**Write atomicity**: The generator validates the complete in-memory bundle
against §8 (including §8.1 and §8.2) before issuing any Write() call.
All files are written only after the full bundle passes validation.
No partial bundle writes are permitted.
```

### §9 Acceptance Criteria Addition

```markdown
N. Pre-write semantic and structural quality gates (§8.1, §8.2) pass before
   any file is written: all tasks have complete metadata fields, all
   Deliverable IDs are globally unique, no placeholder descriptions exist,
   every task has traceability, phase sizes are bounded, no circular
   dependencies, and bundle write is atomic.
```

### §10 Open Questions Resolution
<!-- Source: Base (original) -->
```markdown
N. **Should Write() calls be atomic (all files after validation) or incremental (file by file)?**
   Resolution: Atomic. The §8.1/§8.2 Quality Gates validate the full in-memory bundle
   before any Write() call. Incremental writing is prohibited to prevent partial bundle states.
```

### Risk Assessment

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|------------|
| Check overlap with generator invariants | Low | Low | Checks verify; generator produces. Defense in depth. |
| §8.2 checks too strict for edge cases | Low | Medium | Task count bounds (1-25) are generous; circular dep check is objective |

### What This Does NOT Change
- §8 checks 1-8 remain verbatim
- §7 Style Rules unchanged by this strategy
- §6A, §6B template content unchanged
- §5 Enrichment algorithm unchanged
- No new top-level section created

---

<!-- Source: Variant B, lines 191-213 — merged per Change #8 -->
## Additional Context

### Keep as-is (high value in base spec)
- Command/skill separation is correct and should remain untouched
- Deterministic algorithm framing is strong and compatible with sprint automation
- Non-goals are appropriately scoped for v1.0 parity

### Risks to address while integrating
1. **Installer coupling ambiguity** (`_has_corresponding_command`) should be validated with one real install test
2. **"Identical output" parity criterion** needs explicit normalization rules (or golden fixtures) to avoid false mismatches
3. **Self-contained vs extracted refs** should be resolved clearly: execution must not depend on optional reference files

---

<!-- Source: Variant B, lines 203-213 — merged per Change #8 -->
## v1.1 Deferred Items

These items were validated as valuable but explicitly scoped out of v1.0 parity:

| Item | Source Debate | Reason for Deferral |
|------|--------------|---------------------|
| Full self-contained task items with `Context:`/`Verify:` fields | Strategy 3 debate | Schema expansion; too broad for parity |
| Per-stage halt-on-failure for semantic properties | Strategy 1 debate | Circular self-validation; needs external validator |
| Full structured error format (5-field deterministic block) | Strategy 2 debate | New feature, not parity; 2-field format adopted for v1.0 |
| Content quality heuristics for roadmap input | Strategy 2 debate | Duplicates parser logic |
| CI/CD gate infrastructure | Strategy 1 debate | Premature; needs v2.0 pipeline architecture |
| `--spec` conflict resolution semantics | Strategy 2 debate | Separate problem requiring own spec |
| Session-start executability criterion | Strategy 3 debate | Over-constraining; needs precise definition of assumed session state |

---

<!-- Source: Variant B, lines 215-225 — merged per Change #9 -->
## Implementation Sequence (Unified Patch Order)

1. **Extend §8 Pre-Write Validation** (Strategy 5) — foundation for all others
   - Add §8.1 checks 9-12 + §8.2 checks 13-17 + atomic write declaration
   - Estimated: ~45 min

2. **Add Stage Completion Reporting** (Strategy 1) — TodoWrite observability + structural gates
   - Modify §4.3, §6.2, §9
   - Estimated: ~30 min

3. **Add Acceptance Criteria Quality Rules** (Strategy 4) — tighten existing fields
   - Add near-field completion criterion + tier-proportional enforcement + non-invention constraint
   - Estimated: ~1 hr

4. **Add Minimum Task Specificity Rule** (Strategy 3) — catch vague tasks
   - Add §7.N rule + §8.1 check
   - Estimated: ~30 min

5. **Add Generation Notes + Empty-File Guard** (Strategy 2) — passive transparency
   - Modify §5.4 + add §6A section
   - Estimated: ~30 min

**Total estimated effort**: ~3 hours

This order is: enforcement mechanism first → observability → content quality → input guard. Each step builds on the previous without depending on deferred v1.1 work.

---

## Protocol Compliance Checklist

| Required Section | Status |
|-----------------|--------|
| All 5 strategies with patch text | **PASS** |
| Post-debate strategy names (Change #2) | **PASS** |
| Debate verdicts per strategy (Change #3) | **PASS** |
| Unified document structure (Change #1) | **PASS** |
| Hybrid gating for Strategy 1 (Change #4) | **PASS** |
| Reduced scope for Strategy 2 (Change #5) | **PASS** |
| 3-criterion Strategy 3 (Change #6) | **PASS** |
| Unified check numbering 9-17 (Change #7) | **PASS** |
| Consolidated v1.1 deferral table (Change #8) | **PASS** |
| Unified patch order (Change #9) | **PASS** |
| Token cost annotations (Change #10) | **PASS** |
| Provenance annotations | **PASS** |
| Risk assessments per strategy | **PASS** |
| Non-modified sections documented | **PASS** |
