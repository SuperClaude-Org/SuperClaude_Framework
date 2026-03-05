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
