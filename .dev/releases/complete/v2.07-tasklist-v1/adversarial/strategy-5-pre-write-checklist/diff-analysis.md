# Diff Analysis — Strategy 5: Pre-Write Structural Validation Checklist

**Pipeline Step**: 1 of 5
**Date**: 2026-03-04
**Subject**: Strategy 5 from `tasklist-spec-integration-strategies.md`
**Base spec**: `sc-tasklist-command-spec-v1.0.md` (PRD) + `Tasklist-Generator-Prompt-v2.1-unified.md` (v3.0 generator)
**Proposal source**: `taskbuilder-integration-proposals.md` (Proposal 2)

---

## 1. What Strategy 5 Proposes

Strategy 5 (from `tasklist-spec-integration-strategies.md` §5) proposes adding a **pre-write structural validation checklist** as a hard gate before any `Write()` call is issued during tasklist bundle generation.

The integration strategies document specifies these checklist items:
1. Index exists and references literal phase filenames
2. Every referenced phase file is generated
3. Task IDs follow `T<PP>.<TT>`
4. Required metadata/tier fields present
5. No forbidden sections in phase files (registries/traceability/template noise)

The `taskbuilder-integration-proposals.md` (Proposal 2) expands this into a 13-point checklist covering:
- **Structural checks** (5 items): contiguous phase numbering, task count bounds per phase (≥1, ≤25), task ID format/uniqueness, phase heading format, end-of-phase checkpoint existence
- **Semantic checks** (5 items): non-empty task descriptions, Clarification Task positioning, globally unique Deliverable IDs, confidence bar format consistency, no XL tasks without subtask splits
- **Prohibited patterns** (3 items): no empty shells, no cross-phase contamination, no circular dependencies

The proposed spec location is a new section `§7.5 Pre-Write Quality Validation` between Style Rules (§7) and Sprint Compatibility Self-Check (§8), or alternatively a dedicated subsection under §6 or §8.

---

## 2. Structural Differences

### 2.1 What exists in v3.0 today (the baseline)

**§8 Sprint Compatibility Self-Check** (existing) — 8 checks, all structural:

| # | Existing Check | Type |
|---|---|---|
| 1 | `tasklist-index.md` exists and contains a "Phase Files" table | Structural |
| 2 | Every referenced phase file exists in the output bundle | Structural |
| 3 | Phase numbers are contiguous with no gaps | Structural |
| 4 | All task IDs match `T<PP>.<TT>` format | Structural |
| 5 | Every phase file starts with `# Phase N — <Name>` | Structural |
| 6 | Every phase file ends with end-of-phase checkpoint | Structural |
| 7 | No phase file contains Deliverable Registry, Traceability Matrix, or template sections | Structural |
| 8 | Index contains literal phase filenames in at least one table cell | Structural |

**Position in pipeline**: Post-generation, pre-return. "If any check fails, fix it before returning the output."

**Gap**: §8 triggers AFTER generation is complete. It catches structural errors but does not prevent the generator from writing files in an invalid intermediate state.

### 2.2 What Strategy 5 would add

| Delta | Nature | Target |
|---|---|---|
| New gate positioned BEFORE any `Write()` call | Temporal (earlier in pipeline) | Execution ordering |
| 5 checks in integration-strategies.md version | Content (structural) | Index + phase files |
| 13 checks in taskbuilder-proposals.md version | Content (structural + semantic) | Tasks + phases + index |
| Semantic quality checks (empty descriptions, Deliverable ID uniqueness, etc.) | Qualitatively new category | Task content |
| `§7.5` as new numbered section (between §7 and §8) | Document structure | SKILL.md |

---

## 3. Content Differences

### 3.1 Overlap with existing §8

Of the 5 checks in the integration-strategies version of Strategy 5:

| Proposed Check | Overlap with §8? | Delta |
|---|---|---|
| Index exists and references literal phase filenames | YES — §8 checks 1 and 8 | Exact duplicate if positioned same |
| Every referenced phase file is generated | YES — §8 check 2 | Exact duplicate |
| Task IDs follow `T<PP>.<TT>` | YES — §8 check 4 | Exact duplicate |
| Required metadata/tier fields present | PARTIAL — §8 has no metadata field check | NEW semantic check |
| No forbidden sections in phase files | YES — §8 check 7 | Exact duplicate |

Conclusion: 4 of 5 proposed checks in the integration-strategies version duplicate §8 exactly. Only the metadata/tier field completeness check is genuinely new content.

Of the 13 checks in the taskbuilder-proposals.md version:

| Category | Genuinely new vs. §8? |
|---|---|
| Structural checks 1–5 | Structural checks 1, 2, 3, 4, 5 all have partial or full overlap with §8 |
| Semantic checks 6–10 | ALL genuinely new — §8 has zero semantic checks |
| Prohibited pattern checks 11–13 | Checks 11, 12 overlap with §8 check 7; check 13 (circular deps) is genuinely new |

Net genuinely new checks (taskbuilder version): approximately 6 of 13.

### 3.2 Temporal difference: pre-write vs. post-generation

This is the most significant structural delta. The current §8 fires AFTER the internal generation is complete — conceptually, after all tasks have been built in memory. Strategy 5 proposes a gate that fires BEFORE `Write()` is called on any file.

In practice, for an LLM-executed generator, this distinction matters:
- **Current §8**: "Check your output, fix before returning" — the LLM can fix in-place before emission
- **Proposed pre-write gate**: "Validate in-memory representation before committing to disk" — conceptually earlier, but in LLM execution this is functionally identical to §8 unless the generator writes files incrementally (write phase 1, then phase 2, etc.)

The meaningful difference only materializes if the generator writes files INCREMENTALLY (one at a time), in which case a pre-write check per file prevents partial bundle writes. The current spec does not specify whether Write() is atomic (all at once) or incremental.

---

## 4. Contradictions

### 4.1 Integration-strategies.md vs. taskbuilder-proposals.md scope

The integration-strategies.md version of Strategy 5 proposes "structural" validation only. The taskbuilder-proposals.md Proposal 2 (which the integration-strategies document identifies as the source) adds 5 semantic checks and 3 prohibited-pattern checks that are not mentioned in the integration-strategies summary.

This creates ambiguity: which version is authoritative? The integration-strategies.md is the higher-level synthesis document (explicitly labeled "Compatible Integration Strategies"). The taskbuilder-proposals.md is the detailed expansion. They are not contradictory but are at different specification depths.

### 4.2 Proposed placement vs. existing §8

Placing the checks at §7.5 (between Style Rules and Self-Check) creates a logical gap: §8 (Sprint Compatibility Self-Check) already says "fix before returning." If §7.5 is also a "fix before writing" gate, the spec will have two overlapping fix-before-proceed clauses with different check sets. Without explicit statement of which supersedes which, both must be maintained, creating maintenance burden.

### 4.3 "Required metadata/tier fields present" check not in §8

The metadata completeness check (proposed) is absent from §8, but §8 does require Sprint CLI compatibility (by implication, requiring all fields Sprint CLI needs). This is a latent contradiction: §8 claims Sprint compatibility but does not explicitly check metadata field completeness. Strategy 5 would surface this gap.

---

## 5. Unique Contributions

Strategy 5's genuinely unique contributions (not covered anywhere in v3.0):

1. **Metadata/tier field completeness check** — verifies required fields (Effort, Risk, Tier, Confidence) are present in every task before write
2. **Globally unique Deliverable ID check** (taskbuilder version) — D-### uniqueness across the full bundle, not just within one phase
3. **Circular dependency detection** (taskbuilder version) — catches A→B→C→A chains that §8 does not check
4. **Task count bounds per phase** (taskbuilder version) — ≥1 task and ≤25 tasks per phase
5. **Pre-write temporal position** — earlier execution point that could prevent partial bundle writes in incremental execution mode
6. **Non-empty task description check** — prevents "TBD" or placeholder shells from being written to disk
7. **Confidence bar format consistency** — enforces visual format uniformity across all tasks

---

## 6. Risk Signals

| Risk | Severity | Basis |
|---|---|---|
| High overlap with §8 creates dual-maintenance problem | Medium | 4/5 (integration-strategies) or 7/13 (taskbuilder) checks duplicate §8 |
| Incremental vs. atomic write ambiguity makes temporal positioning unclear | Medium | Spec §6 does not specify write atomicity |
| "Fix before writing" + "Fix before returning" creates ambiguous correction scope | Low-Medium | Both gates use fix-in-place semantics without clear precedence |
| Taskbuilder's 13-check version significantly increases generator complexity | Low | Well-defined checks, but each adds cognitive overhead to the generation prompt |
| v1.0 parity constraint: semantic checks add new behavior beyond v3.0 | High | Integration-strategies.md explicitly states "no new features" for v1.0 |

