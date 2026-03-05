# /sc:tasklist v1.0 — Integration Strategies from Cross-Analysis

**Date**: 2026-03-04 (Refactored: 2026-03-04 post-adversarial debate)
**Base spec analyzed**: `sc-tasklist-command-spec-v1.0.md`
**Reference analyzed**: `/config/workspace/llm-workflows/.claude/commands/rf/taskbuilder.md`
**Debate artifacts**: `debates/debate-proposal-{1..5}-*.md`

## Executive Summary

The base spec is already strong on command/skill separation, deterministic flow, and parity constraints. The best compatible integrations from `taskbuilder.md` are not feature-expanding; they are **execution-hardening patterns** that preserve v1.0 parity while reducing ambiguity, rollover risk, and validation drift.

**Post-Debate Status**: All 5 strategies underwent structured adversarial debate (Opus advocate vs Haiku critic). Results refined each proposal — no strategy was fully rejected; all received conditional acceptance with scope narrowing to respect v1.0 parity constraints.

### Debate Verdict Summary

| # | Strategy | Verdict | Key Modification |
|---|----------|---------|-----------------|
| 1 | Stage-Gated Generation Contract | **CONDITIONAL ACCEPT** | Downscoped to "Stage Completion Reporting" — TodoWrite observability, not halt-on-failure gates |
| 2 | Single-Pass Clarification Rules | **CRITIC WINS w/ conditions** | Downscoped to passive `## Generation Notes` in index + empty-file guard; full fail-fast deferred to v1.1 |
| 3 | Self-Contained Task Items | **CONDITIONAL ACCEPT** | Weakened: require specific artifacts + concrete verbs (catch worst offenders); defer full `Context:`/`Verify:` fields to v1.1 |
| 4 | Inline Verification Coupling | **CONDITIONAL ACCEPT** | Tighten existing `Acceptance Criteria`/`Validation` fields (already in §6B.2); no new fields; add quality rules |
| 5 | Pre-Write Validation Checklist | **CONDITIONAL ACCEPT** | Extend existing §8.1 with 5 new checks (13-17); clarify timing as "Pre-Write, Mandatory"; no separate new section |

---

## 5 Compatible Integration Strategies (Post-Debate Refactored)

## 1) **Stage Completion Reporting Contract** ~~Stage-Gated Generation Contract~~

> **Debate verdict**: CONDITIONAL ACCEPT — Renamed. Accept observability via TodoWrite; reject per-stage halt-on-failure gates (circular self-validation provides false confidence).

### What to integrate
Add stage completion reporting to the SKILL execution pipeline via TodoWrite:
1. Input ingest → ✅ reported
2. Parse + phase bucketing → ✅ reported
3. Task conversion → ✅ reported
4. Enrichment → ✅ reported
5. File emission → ✅ reported
6. Self-check → ✅ reported

### What was rejected (from debate)
- Per-stage halt-on-failure gates — the same model that produces output cannot reliably validate its own intermediate state (circular self-validation)
- CI/CD gate infrastructure — premature for v1.0; deferred to v2.0
- "Deterministic re-runs" framing — determinism is a property of the function, not of observing intermediate state

### Concrete spec changes
- In `sc-tasklist-command-spec-v1.0.md` §6.2, add:
  - "The skill MUST report stage completion via TodoWrite for each of the 6 pipeline stages."
  - "Stage reporting is observational (debugging/progress); it does NOT gate advancement."
- In §6.4 Tool Usage, strengthen TodoWrite row:
  - "TodoWrite: Report completion of each pipeline stage (ingest → parse → convert → enrich → emit → validate) | Throughout"
- Two-point validation preserved: input validation (command layer §5.4) + pre-write checklist (Strategy 5)

### Value
- Debugging observability: know WHERE failure occurred in 6-stage pipeline
- Progress tracking for long-running generation on large roadmaps
- Foundation for v2.0 CI/CD integration without premature infrastructure

---

## 2) **Generation Notes + Empty-File Guard** ~~Single-Pass Clarification Rules~~

> **Debate verdict**: CRITIC WINS with conditions — The parity constraint and "works with any roadmap" design intent are decisive. Full fail-fast deferred to v1.1.

### What to integrate (reduced scope)
Two minimal, parity-compatible changes:

1. **Passive Generation Notes**: Add a `## Generation Notes` section to `tasklist-index.md` that records which deterministic fallbacks activated during generation (e.g., "No phase headings detected; applied 3-bucket default")
2. **Empty-file guard**: Add to §5.4 that an empty roadmap file (0 bytes or whitespace-only) is rejected before skill invocation

### What was rejected (from debate)
- Structured error format for ambiguous content — this is new feature work, not parity
- Content quality heuristics (min headings, min bullet count) — duplicates the generator's own parsing logic
- Failing on ambiguous input — violates the design intent that the generator handles "unstructured or structured" input
- `--spec` conflict resolution semantics — separate problem, should not be conflated

### Concrete spec changes
- In §5.4 Input Validation, add:
  - "Reject roadmap files that are empty (0 bytes) or contain only whitespace."
- In §6A Index File Template, add optional section:
  - "`## Generation Notes` — Lists any fallback behaviors activated during generation (e.g., default phase bucketing, missing metadata inference). This section is informational; it does not affect Sprint CLI compatibility."
- Do NOT expand Boundaries (Will) with structured error claims — that's v1.1 scope

### Value
- Empty-file guard prevents the most obvious input error
- Generation Notes provide passive transparency without breaking deterministic output
- Preserves "works with any roadmap" promise

---

## 3) **Minimum Task Specificity Rule** ~~Self-Contained Task Item Quality Gate~~

> **Debate verdict**: CONDITIONAL ACCEPT (weakened) — Require specific artifacts + concrete action verbs; defer full self-containment (`Context:`/`Verify:` fields) to v1.1.

### What to integrate (reduced scope)
A lightweight quality rule that catches the worst offenders — vague tasks with no target artifact — while preserving conciseness and DRY within phases:

- Every task MUST name at least one specific target (file, module, endpoint, component)
- Every task MUST use a concrete action verb (implement, create, configure, migrate, test — not "handle", "address", "work on")

### What was rejected (from debate)
- Full self-contained prose paragraphs per task — too verbose, breaks TUI rendering
- Embedded `Context:` and `Verify:` fields per task — schema expansion belongs in v1.1
- "No task requires conversational context" criterion — subjective, cannot be mechanically verified in a deterministic pipeline
- DRY violation: repeated context across co-located tasks within the same phase

### Key debate insight
The Advocate correctly identified a real inter-phase problem (context loss across sessions). The Critic correctly identified that the full solution is too broad for v1.0 parity. The v1.0 rule catches the worst offenders; v1.1 adds the full field-level enforcement.

### Concrete spec changes
- In §7 Style Rules, add:
  - "Every task description MUST reference at least one specific artifact (file path, module name, API endpoint, or component identifier)."
  - "Every task MUST begin with a concrete action verb. Prohibited verbs: 'handle', 'address', 'deal with', 'work on', 'look into'."
- In §8 Self-Check, add check:
  - "Reject tasks that contain no specific artifact reference."
- Do NOT add new task fields (`Context:`, `Verify:`, `Blocked-Until:`) — deferred to v1.1

### Value
- Catches the worst vagueness offenders at near-zero cost
- No schema changes, no additional token cost per task
- Paves the way for full self-containment in v1.1

---

## 4) **Acceptance Criteria Quality Rules** ~~Inline Verification Coupling~~

> **Debate verdict**: CONDITIONAL ACCEPT — Tighten existing fields rather than adding new ones. Critical discovery: v3.0 task format ALREADY has `Acceptance Criteria` (4 bullets) and `Validation` (2 bullets) fields per task in §6B.2.

### What to integrate
Quality enforcement on existing acceptance criteria fields — not new fields:

- Require that `Acceptance Criteria` bullets reference specific artifacts (not generic "tests pass")
- Require at least one executable/verifiable criterion per task
- Apply tier-proportional enforcement (STRICT = full, STANDARD = moderate, LIGHT = minimal, EXEMPT = none)

### What was rejected (from debate)
- New `Verify:` field — redundant with existing `Acceptance Criteria` + `Validation` fields
- Completion gate sentences ("This item cannot be marked done until...") — too verbose for Sprint CLI format
- Generator-produced implementation-specific criteria — hallucination risk when generating from roadmap text alone

### Concrete spec changes
- Add `§5.7 Acceptance Criteria Quality Rules`:
  - "At least one criterion per task MUST reference a specific artifact (file, test, endpoint, config)."
  - "Generic criteria ('code works', 'tests pass', 'properly formatted') MUST be replaced with specific equivalents ('unit tests in test_auth.py pass', 'API returns 200 for valid input')."
  - "Criteria specificity is tier-proportional: STRICT tasks require all criteria to be artifact-referencing; STANDARD requires ≥1; LIGHT and EXEMPT have no minimum."
- Add §8.1 Check #13:
  - "Reject tasks where ALL acceptance criteria are generic (no artifact references)."

### Value
- Zero new fields, zero schema changes, zero additional token cost
- Enforces quality on fields that already exist but are currently unconstrained
- Tier-proportional enforcement avoids over-constraining simple tasks

---

## 5) **Extended Pre-Write Validation** ~~Pre-Write Structural Validation Checklist~~

> **Debate verdict**: CONDITIONAL ACCEPT — Extend existing §8.1 with 5 new checks; clarify timing as "Pre-Write, Mandatory". Do NOT create a separate new section.

### What to integrate
Extend the existing §8 / §8.1 self-check with genuinely new semantic checks not currently covered:

### New checks to add (13-17)
| # | Check | Rationale |
|---|-------|-----------|
| 13 | Task count bounds: every phase has ≥1 and ≤25 tasks | Prevents empty phases and unwieldy mega-phases |
| 14 | Clarification Task adjacency: ⚠️ tasks appear immediately before their blocked task | Prevents orphaned clarification items |
| 15 | Circular dependency detection: no A→B→C→A chains | Prevents unexecutable dependency graphs |
| 16 | XL splitting enforcement: EFFORT=XL tasks must have subtasks | Enforces decomposition time-boxing |
| 17 | Confidence bar format consistency: all use `██░░░ N%` pattern | Prevents format drift across phases |

### What was rejected (from debate)
- Creating a separate `§7.5 Pre-Write Quality Validation` section — duplicates existing §8 structure
- Moving existing checks from §8 to a new location — reorganization without value
- Framing this as "new capability" — it's incremental extension of existing validation

### Concrete spec changes
- In §8 header, clarify timing:
  - Change: "Sprint Compatibility Self-Check" → "Sprint Compatibility Self-Check (Pre-Write, Mandatory)"
  - Add: "All checks in this section MUST pass before any `Write()` call. Invalid output is never written."
- Add checks 13-17 to §8.1 checklist (see table above)
- Estimated token cost: ~150 additional tokens in SKILL.md

### Value
- Catches semantic errors that structural checks miss
- Foundation for all other strategies (enforcement mechanism)
- Minimal implementation effort (~45 minutes)

---

## Additional Valuable Context for Refactor/Add Decisions

### Keep as-is (high value in base spec)
- Command/skill separation is correct and should remain untouched
- Deterministic algorithm framing is strong and compatible with sprint automation
- Non-goals are appropriately scoped for v1.0 parity

### Risks to address while integrating above
1. **Installer coupling ambiguity** (`_has_corresponding_command`) should be validated with one real install test
2. **"Identical output" parity criterion** needs explicit normalization rules (or golden fixtures) to avoid false mismatches
3. **Self-contained vs extracted refs** should be resolved clearly: execution must not depend on optional reference files

### v1.1 Deferred Items (from debate outcomes)
These items were validated as valuable but explicitly scoped out of v1.0 parity:

| Item | Source Debate | Reason for Deferral |
|------|--------------|---------------------|
| Full self-contained task items with `Context:`/`Verify:` fields | Debate 3 | Schema expansion; too broad for parity |
| Per-stage halt-on-failure gates | Debate 1 | Circular self-validation; needs external validator |
| Structured error format for input validation | Debate 2 | New feature, not parity |
| Content quality heuristics for roadmap input | Debate 2 | Duplicates parser logic |
| CI/CD gate infrastructure | Debate 1 | Premature; needs v2.0 pipeline architecture |
| `--spec` conflict resolution semantics | Debate 2 | Separate problem requiring own spec |

## Revised Spec Patch Order (Post-Debate)

1. **Extend §8 Pre-Write Validation** (Strategy 5) — foundation for all others; ~45 min
2. **Add Stage Completion Reporting** (Strategy 1) — TodoWrite observability; ~30 min
3. **Add Acceptance Criteria Quality Rules** (Strategy 4) — tighten existing fields; ~1 hr
4. **Add Minimum Task Specificity Rule** (Strategy 3) — catch vague tasks; ~30 min
5. **Add Generation Notes + Empty-File Guard** (Strategy 2) — passive transparency; ~30 min

**Total estimated effort**: ~3 hours (down from ~8.5 hours pre-debate)

This order is: enforcement mechanism first → observability → content quality → input guard. Each step builds on the previous without depending on deferred v1.1 work.
