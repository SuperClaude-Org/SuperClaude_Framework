# Diff Analysis — Strategy 2: Single-Pass Clarification Rules

**Adversarial Pipeline Step 1**
**Date**: 2026-03-04
**Subject**: Strategy 2 from `tasklist-spec-integration-strategies.md`
**Constraint set**: `sc-tasklist-command-spec-v1.0.md` + v1.0 parity requirement

---

## 1. Strategy Statement (Verbatim)

> From `taskbuilder`'s "ask once for gaps" principle, adapt to v1.0 non-interactive mode:
> - If required input is missing/ambiguous, perform one deterministic fallback resolution attempt.
> - If still unresolved, fail with a concise, structured error listing exact missing fields.

**Proposed spec changes:**
- Expand §5.4 Input Validation with: "One-pass resolution for ambiguous path/state; otherwise fail-fast with actionable diagnostics."
- Add to Boundaries (Will): "Return structured validation errors (missing roadmap/spec/output derivation failure)."

---

## 2. Current State in Spec (Baseline)

### §5.4 Input Validation (current)
```
Before invoking the skill, the command validates:
1. <roadmap-path> resolves to a readable file
2. If --spec provided, it resolves to a readable file
3. If --output provided, the parent directory exists
4. If --output not provided, derive TASKLIST_ROOT from roadmap content using §3.1 algorithm
```

### §5.6 Boundaries / Will (current)
```
Will:
- Parse and validate input arguments
- Derive TASKLIST_ROOT from roadmap content
- Invoke the skill with validated context
- Report generated file paths on completion
```

### §3 Non-Goals (current)
```
- No interactive mode or progressive generation
- No MCP-driven roadmap fetching or auto-detection
```

---

## 3. Structural Differences Introduced by Strategy 2

| Dimension | Current spec | Strategy 2 adds |
|-----------|-------------|-----------------|
| Validation failure mode | Implicit (unspecified) | Explicit: fail-fast with structured diagnostic |
| Ambiguity handling | Unspecified | One deterministic fallback attempt before failure |
| Error message format | Unspecified | Structured (lists exact missing fields) |
| Boundaries/Will | 4 items | +1: return structured validation errors |
| Interactivity | None | None (preserved) |
| Output path derivation | Already in §5.4(4) | Clarifies failure path, does not change algorithm |

---

## 4. Content Differences (What Actually Changes)

### 4a. New behaviors introduced

1. **One-pass fallback resolution**: Currently §5.4 validation either succeeds or (implicitly) fails. Strategy 2 inserts a recovery attempt between "ambiguous" detection and failure. The spec does not define what "deterministic fallback resolution" means concretely for each validation check — this is the primary implementation ambiguity.

2. **Structured error format**: Currently there is no specification of what the command emits on validation failure. Strategy 2 adds a structured error contract. This is unambiguously additive and not in tension with any non-goal.

3. **Explicit fail-fast semantics**: The spec implicitly fails fast (it either validates and proceeds, or the command cannot proceed), but does not say so. Making this explicit is a documentation improvement, not a behavior change.

### 4b. Behaviors NOT changed

- The skill algorithm (§6) is untouched.
- Output format (§6A, §6B templates) is untouched.
- Command arguments (§5.2) are untouched.
- Sprint compatibility self-check (§8) is untouched.
- The interactive mode exclusion is preserved.

---

## 5. Contradictions / Tensions Detected

### Tension 1: "One-pass fallback" semantics are underspecified

The strategy says "one deterministic fallback resolution attempt." The current spec has one ambiguity case: when `--output` is absent, §5.4(4) already runs the `§3.1 algorithm` to derive `TASKLIST_ROOT`. This IS a fallback. Is Strategy 2 adding a second fallback? Or labeling the existing §3.1 derivation as the fallback?

**Risk**: If the strategy means to add a NEW fallback step (e.g., pattern-matching a path from roadmap filename), this expands scope beyond v1.0 parity. If it means to label §3.1 as the one-pass attempt and treat its failure as the structured error trigger, this is already the intended behavior and requires only documentation.

### Tension 2: "Ambiguous" vs "missing" are different failure classes

The strategy conflates two distinct cases:
- **Missing**: `<roadmap-path>` not provided (hard failure, no recovery possible)
- **Ambiguous**: `--output` not provided (soft failure, §3.1 can resolve)

The one-pass fallback applies only to ambiguous inputs. The structured error applies to both. Strategy 2 does not distinguish between these in its proposed spec text.

### Tension 3: CI/automation operator vs interactive operator framing

The value statement says "Better operator feedback for automation and CI usage." This is entirely compatible with the spec. However, the framing "ask once for gaps" from taskbuilder is interactive-origin terminology. The adaptation must be verified to not carry interactive semantics in its implementation.

---

## 6. Unique Contributions (Not Present Anywhere in Spec)

1. **Explicit validation failure contract** — The spec currently has no section stating what the command emits on validation failure. This is a genuine gap.
2. **Structured error format** — Specific fields, format, and content of the error message are unspecified in the current spec.
3. **Named fallback protocol** — §5.4(4) is an implicit fallback; naming and formalizing it creates a clearer contract.

---

## 7. Implementation Risk Surface

| Risk | Severity | Notes |
|------|----------|-------|
| Fallback scope creep (new resolution logic vs labeling existing) | Medium | Underspecification in strategy text |
| "Ambiguous" case taxonomy incomplete | Low | Fixable with one-sentence clarification |
| Interactive contamination via taskbuilder framing | Low | Only in language, not in mechanics |
| Parity impact | None | No generator output changes |

---

## 8. Summary Assessment

Strategy 2 introduces two genuinely valuable additions (explicit fail-fast semantics and structured error output) and one ambiguous element (what constitutes a "fallback resolution attempt"). The strategy is structurally compatible with the spec. The primary risk is implementation underspecification, not architectural incompatibility.
