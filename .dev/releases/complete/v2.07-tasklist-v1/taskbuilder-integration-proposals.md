# Taskbuilder Integration Proposals for `/sc:tasklist` v1.1

**Date**: 2026-03-04
**Source Analysis**: Cross-framework extraction from `llm-workflows/rf:taskbuilder_v2` into `sc-tasklist-command-spec-v1.0.md`
**Method**: Parallel analysis of both specs → brainstorm → 5 compatible strategies

---

## Context

**Our Base**: `/sc:tasklist` v1.0 — a deterministic roadmap-to-tasklist generator packaged as a SuperClaude command/skill pair. Produces Sprint CLI-compatible multi-file bundles (`tasklist-index.md` + `phase-N-tasklist.md`). Currently batch-only, no interactive mode, no output quality validation beyond structural self-check.

**External Reference**: `rf:taskbuilder_v2` (Rigorflow/MDTM) — a mature task builder with session-rollover-safe self-contained checklist items, 3-stage interview, pre-write validation, and completion gates. Production-tested in a headless agent execution context similar to Sprint CLI.

**Selection Criteria**: Strategies were chosen for (1) compatibility with existing v1.0 architecture, (2) addressability without architectural breaks, (3) direct impact on Sprint CLI execution quality.

---

## Proposal 1: Self-Contained Task Items with Embedded Context

### Problem It Solves
Current v1.0 tasks contain `Dependencies` fields but no mechanism to verify those dependencies are met before execution. Sprint CLI executes tasks across sessions — context loaded in one session may be gone by the time a dependent task runs. Tasks like "configure X" or "implement Y" without embedded context are incomplete execution units.

### Strategy from Taskbuilder
Every checklist item is a single, complete execution prompt containing:
1. **Action + WHY** — what to do and why
2. **Context reference** — which files to read (with paths) and why that context is needed
3. **Output specification** — exact file path, format, and content requirements
4. **Verification clause** — `"ensuring..."` inline acceptance criteria
5. **Completion gate** — explicit assertion that the item cannot be marked done until fully complete

### Adaptation for `/sc:tasklist`

**What changes in the spec**:
- Add a new section to `SKILL.md`: `§4.7 Task Self-Containment Rules`
- Each task in `phase-N-tasklist.md` gets enriched with:
  - `Context:` field — files/artifacts the executor must read before starting
  - `Verify:` field — inline acceptance criteria (replaces reliance on separate QA passes)
  - `Blocked-Until:` field — prerequisite task IDs that must be complete
- The `§8 Sprint Compatibility Self-Check` gains a new check: "Every task has non-empty Context and Verify fields"

**What does NOT change**:
- Task ID format (`T<PP>.<TT>`) unchanged
- Phase file structure unchanged
- Command layer (`tasklist.md`) unchanged

**Example before/after**:

```markdown
# Before (v1.0)
- [ ] T01.03 · Implement rate limiting middleware
  - Effort: M | Risk: moderate | Tier: STANDARD
  - Dependencies: T01.01, T01.02

# After (v1.1 with self-containment)
- [ ] T01.03 · Implement rate limiting middleware
  - Effort: M | Risk: moderate | Tier: STANDARD
  - Dependencies: T01.01, T01.02
  - Context: Read `src/middleware/auth.ts` for existing middleware patterns; read `docs/api-spec.md §3.2` for rate limit requirements
  - Verify: Middleware exports a configurable `rateLimit()` function, tests pass for 429 response on exceeded limit, no regression in existing middleware chain
  - Blocked-Until: T01.01 ✅, T01.02 ✅
```

### Effort Estimate
- Spec update: ~2 hours (add §4.7, update §6B template, extend §8 self-check)
- No command layer changes required

---

## Proposal 2: Pre-Write Validation Checklist (Silent Quality Gate)

### Problem It Solves
The v1.0 Sprint Compatibility Self-Check (§8) validates structural correctness (file existence, heading format, contiguous numbering) but not semantic quality. There is no check for: globally unique Deliverable IDs, non-empty task descriptions, minimum tasks per phase, well-formed Clarification Tasks, or confidence bar format consistency.

### Strategy from Taskbuilder
A 12-point silent validation checklist runs before `Write()` is called. If ANY check fails, the generator fixes the issue before writing. The checklist covers both structural rules (checkbox format, section order) and semantic rules (self-containment, atomicity, no prohibited patterns).

### Adaptation for `/sc:tasklist`

**Add to SKILL.md as `§7.5 Pre-Write Quality Validation`** (between Style Rules and Self-Check):

```markdown
## §7.5 Pre-Write Quality Validation (Silent, Mandatory)

Before writing any output file, validate internally:

### Structural Checks
1. ✓ All phases have contiguous numbering (no gaps)
2. ✓ Every phase file has ≥1 task and ≤25 tasks
3. ✓ All task IDs follow T<PP>.<TT> format with no duplicates across phases
4. ✓ Phase heading uses `# Phase N — <Name>` with em-dash separator
5. ✓ End-of-phase checkpoint exists as final item

### Semantic Checks
6. ✓ Every task has non-empty description (no "TBD" or placeholder text)
7. ✓ Every Clarification Task (⚠️) appears immediately before the blocked task
8. ✓ All Deliverable IDs (D-###) are globally unique across the bundle
9. ✓ Confidence bars are formatted consistently (e.g., `██░░░ 40%`)
10. ✓ No task has EFFORT=XL without being split into subtasks

### Prohibited Patterns
11. ✓ No tasks with only a title and no metadata (empty shells)
12. ✓ No phase files containing content from another phase (cross-contamination)
13. ✓ No circular dependencies in task dependency chains

If ANY check fails → fix before writing. Do NOT write invalid output.
```

### Effort Estimate
- Spec update: ~1.5 hours (new section, enumerate checks)
- Extends existing §8 self-check rather than replacing it

---

## Proposal 3: Prohibited Patterns List (Negative Constraint Set)

### Problem It Solves
The v1.0 spec defines what the generator SHOULD produce but does not explicitly enumerate what it must NOT produce. Generators naturally drift toward prohibited patterns because they are structurally simpler. Without a negative constraint set, quality degrades silently.

### Strategy from Taskbuilder
Explicit `PROHIBITED PATTERNS (DO NOT USE)` section with examples:
- Standalone context reads without output
- Separate verification items (must be inline)
- Vague actions ("implement the feature")
- Nested checkboxes (flat structure only)
- Multi-line bulleted lists within a single item
- Missing completion gates

### Adaptation for `/sc:tasklist`

**Add to SKILL.md as `§7.3 Prohibited Output Patterns`**:

```markdown
## §7.3 Prohibited Output Patterns

The generator MUST NOT produce any of the following. These are checked
during §7.5 Pre-Write Validation.

### Task-Level Prohibitions
- ❌ **Vague tasks**: "Set up infrastructure" without specific deliverables
- ❌ **Mega-tasks**: Single task covering >2 days of work (split required)
- ❌ **Orphan dependencies**: Task references dependency ID that doesn't exist
- ❌ **Circular dependencies**: A→B→C→A chains
- ❌ **Empty metadata**: Task with title only, no effort/risk/tier

### Phase-Level Prohibitions
- ❌ **Single-task phases**: Phase with only 1 task (merge with adjacent phase)
- ❌ **Cross-contamination**: Phase file contains tasks belonging to another phase
- ❌ **Missing checkpoint**: Phase without end-of-phase checkpoint as final item
- ❌ **Non-contiguous numbering**: Phase 1, Phase 2, Phase 4 (gap)

### Index-Level Prohibitions
- ❌ **Path-prefixed filenames**: `tasks/phase-1-tasklist.md` instead of `phase-1-tasklist.md`
- ❌ **Duplicate phase names**: Two phases with identical names
- ❌ **Missing Phase Files table**: Index without the literal filename table

### Content Prohibitions
- ❌ **Invented context**: Claims about files/APIs not in the roadmap input
- ❌ **Embedded instructions**: Meta-prompts or "note to executor" comments
- ❌ **Traceability matrices**: Registries or cross-reference tables (lean output only)
```

### Effort Estimate
- Spec update: ~1 hour (enumerate, cross-reference with §7.5 validation)
- Purely additive — no existing content changes

---

## Proposal 4: Decomposition Time-Boxing Rule

### Problem It Solves
The v1.0 generator converts roadmap items to tasks (§4.4-4.5) with a splitting heuristic, but the heuristic is not bounded by execution time or complexity. This can produce undifferentiated large tasks that are hard to track, parallelize, or estimate.

### Strategy from Taskbuilder
Explicit rule: "If a step could take >30 minutes → split it into multiple self-contained items." Combined with: "If a step does multiple things → separate into multiple items." Every item must be objectively verifiable.

### Adaptation for `/sc:tasklist`

**Enhance SKILL.md `§4.5 Task Splitting` with explicit bounds**:

```markdown
## §4.5 Task Splitting (Enhanced)

### Splitting Triggers (apply in order)
1. **Effort threshold**: Any task scored EFFORT ≥ L (Large) MUST be evaluated for splitting
2. **Multi-action detection**: If task description contains >2 distinct verbs
   (e.g., "configure, implement, and test") → split into separate tasks
3. **Multi-output detection**: If task produces >1 distinct deliverable → split per deliverable
4. **Time-box rule**: No single task should represent >4 hours of focused work.
   Tasks exceeding this are split at natural boundaries (setup → implement → verify)

### Splitting Output
- Parent task becomes a summary/coordination task with Effort: XS
- Child tasks inherit the parent's phase and get sequential IDs: T<PP>.<TT>a, T<PP>.<TT>b
- Dependencies flow: children depend on parent; downstream tasks depend on last child

### Iterative Pattern (for batch/list tasks)
When a roadmap item implies processing N similar items (e.g., "migrate all endpoints"):
1. **Enumerate**: One task to inventory all items → produces checklist artifact
2. **Per-item**: One task per item (self-contained with own context/verify)
3. **Consolidate**: One task to verify all items complete → produces summary

This prevents the generator from emitting a single "do it for all of them" task.
```

### Effort Estimate
- Spec update: ~2 hours (revise §4.5, add iterative pattern, update examples)
- Touches existing section but is backward-compatible

---

## Proposal 5: Inline Verification Clause Co-location

### Problem It Solves
v1.0 tasks have no per-task acceptance criteria. Verification is deferred entirely to (a) the Sprint Compatibility Self-Check (structural only) and (b) the Sprint CLI executor's own quality gates (if any). An automated executor processing a task has no embedded signal for "how do I know this is done correctly."

### Strategy from Taskbuilder
Every checklist item includes an `"ensuring..."` clause that co-locates acceptance criteria with the action. This means the executor's context window contains the criteria at the exact moment they are relevant — no need to look up a separate "Definition of Done" section.

### Adaptation for `/sc:tasklist`

**Add `Verify:` field to the phase file task format (§6B)**:

```markdown
## Enhanced Task Format (§6B)

- [ ] T<PP>.<TT> · <Title>
  - Effort: <XS|S|M|L|XL> | Risk: <low|moderate|high> | Tier: <tier>
  - Why: <1-sentence rationale from roadmap>
  - Dependencies: <comma-separated T-IDs or "none">
  - Context: <files/artifacts to read before starting>
  - Verify: <inline acceptance criteria — what "done" looks like>
  - Deliverables: <D-### IDs if applicable>
```

**Verification clause generation rules** (add to `§5 Enrichment`):

```markdown
### §5.5 Verification Clause Generation

For each task, generate a `Verify:` field containing 1-3 concrete, testable criteria:

1. **Output existence**: "File X exists at path Y" or "Function X is exported"
2. **Behavioral correctness**: "Tests pass for scenario Z" or "API returns 200 for valid input"
3. **Quality constraint**: "No TypeScript errors" or "Coverage ≥80% for new code"

Rules:
- Criteria must be objectively verifiable (no "works correctly" or "is good")
- Prefer executable checks (test commands, lint passes) over subjective review
- Inherit verification patterns from roadmap acceptance criteria where available
- Clarification Tasks (⚠️) use: "Verify: Clarification response received and documented"
```

### Effort Estimate
- Spec update: ~2 hours (new §5.5, update §6B template, update §8 self-check)
- Backward-compatible — adds fields without removing any

---

## Summary Matrix

| # | Proposal | Addresses Gap | Spec Sections Modified | Breaking Change | Effort |
|---|----------|---------------|------------------------|-----------------|--------|
| 1 | Self-Contained Task Items | Session rollover, dependency validation | §4.7 (new), §6B, §8 | No | ~2h |
| 2 | Pre-Write Validation Checklist | Semantic quality gate missing | §7.5 (new) | No | ~1.5h |
| 3 | Prohibited Patterns List | No negative constraints | §7.3 (new) | No | ~1h |
| 4 | Decomposition Time-Boxing | Unbounded task size, no iterative pattern | §4.5 (enhanced) | No | ~2h |
| 5 | Inline Verification Clauses | No per-task acceptance criteria | §5.5 (new), §6B | No | ~2h |

**Total estimated spec update effort**: ~8.5 hours

**Recommended implementation order**: 3 → 2 → 5 → 1 → 4
- Start with Prohibited Patterns (cheapest, highest signal-to-noise ratio)
- Then Pre-Write Validation (enforcement mechanism for all other proposals)
- Then Verification Clauses (most impactful for Sprint CLI execution quality)
- Then Self-Contained Items (builds on verification clauses)
- Finally Decomposition Rules (refines splitting heuristic with concrete bounds)

---

## Appendix: Strategies Considered But Not Selected

| Strategy | Reason for Exclusion |
|----------|---------------------|
| **3-Stage Interview Process** | v1.0 non-goal explicitly excludes interactive mode. The interview is a fundamentally different input acquisition model (interactive wizard vs. batch roadmap parsing). Better suited for a separate `/sc:tasklist --interview` mode in v2.0. |
| **Interview Notes File** | Unnecessary for batch generation from roadmap input. The roadmap IS the structured input. Notes files solve the problem of capturing unstructured user responses — not applicable here. |
| **Completion Gate Sentences** | Too verbose for Sprint CLI task format. The `Verify:` field (Proposal 5) achieves the same goal more concisely. Sprint CLI tasks are consumed by agents, not humans reading prose paragraphs. |
| **TOML Frontmatter** | SuperClaude uses YAML frontmatter. Switching to TOML would break `make lint-architecture` and all existing parsers. |
| **Template Discovery (Fallback Paths)** | v1.0 already has templates extracted to `templates/`. The fallback-path discovery pattern solves a problem (missing templates) that doesn't exist when templates are bundled with the skill. |
