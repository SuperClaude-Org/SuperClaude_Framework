# Strategy: LW Component — Task Builder

**Component**: Task Builder (rf:taskbuilder_v2)
**Source**: `.claude/commands/rf/taskbuilder.md`
**Path Verified**: true
**Strategy Analyzable**: true
**Generated**: 2026-03-14

---

## 1. What Is Rigorous About This Component

The task builder is a structured 3-stage interview system that produces MDTM task files with self-contained checklist items designed to survive session rollovers.

**Core rigor mechanisms:**

- **Self-contained checklist items**: Every checklist item is a single, complete paragraph containing: action + WHY, integrated verification ("ensuring..." clause), output specification, error handling instruction, and completion gate. `taskbuilder.md:184-264`
- **Session rollover protection by design**: The v2 distinction over v1 is explicit — context loaded in batch 1 will NOT be available in batch 3+. Therefore every checklist item embeds all context it needs rather than referencing shared context. This is a structural solution to context window limitations. `taskbuilder.md:182`
- **Mandatory completion gate**: Every checklist item ends with "This item cannot be marked as done until the actions are completed in their entirety exactly as described." `taskbuilder.md:270-272`
- **Pre-write silent validation checklist**: 7 checks before writing any task file, including YAML validity, section order, no nested checkboxes, self-contained check, integrated verification check, no standalone reads. `taskbuilder.md:315-324`
- **No standalone context-reading items**: Prohibited. Context must be embedded in action items. A standalone "read context" item is useless because that context is lost before it can be used. `taskbuilder.md:182, 356-358`
- **3-stage structured interview**: Stage 1 (core intent: goal, why, outputs, context), Stage 2 (phases and steps), Stage 3 (guardrails). Each stage has fixed wording to minimize cognitive load and prevent omissions. `taskbuilder.md:47-130`
- **Agent memory file**: `rf-task-builder/MEMORY.md` captures learned patterns (documentation tasks, planning tasks, batch size recommendations) that accumulate across conversations. `rf-task-builder/MEMORY.md:1-57`

**Rigor verdict**: Self-contained checklist items are a significant innovation. The standard pattern (context item → action item → verification item) fails at scale because context from batch 1 is lost by batch 5. Embedding context in every action item eliminates this failure mode, at the cost of verbosity.

---

## 2. What Is Bloated / Slow / Expensive

**Complexity overhead:**
- The 3-stage interview generates significant pre-task dialogue. For experienced users who know exactly what they want, the fixed interview structure adds friction.
- The synthesis rules ("each step from Stage 2 → expand to 1-3 self-contained checkboxes") can produce task files with dozens of items for moderate tasks, each with full embedded context. A 30-item task file may contain 30 copies of the same context references.

**Operational drag:**
- The completion gate ("This item cannot be marked as done until...") in every item adds redundant text. In a 30-item task file, this phrase appears 30 times.
- "Ensuring..." verification clauses add a sentence to every item. Valuable but verbose at scale.
- Agent memory persistence means the task builder accumulates institutional knowledge but also accumulates potentially stale patterns that may not apply to new task types.

**Token/runtime expense:**
- Self-contained items consume significantly more tokens than reference-based items. A task with 20 items where each item embeds 100 words of context = 2000 words of context duplication in the task file itself.
- The 3-stage interview, note appending between stages, and template reading before writing all add to task creation time.

**Maintenance burden:**
- The template (`.gfdoc/templates/01_mdtm_template_generic_task.md`) is a large document (700+ lines). The builder must read it before writing every task file. `taskbuilder.md:400-410`
- Two templates exist (generic `01` and complex `02`), with different patterns. The builder must select between them. Selecting the wrong template produces a structurally incorrect task file.
- The MEMORY.md file grows over time without a pruning mechanism. Stale patterns accumulate.

---

## 3. Execution Model

The task builder operates as an **interactive task specification system**:

1. User invokes `/rf:taskbuilder_v2 [optional output path]`
2. Stage 1 interview: 4 fixed questions (goal, why, outputs, context) + optional single follow-up
3. Append Stage 1 notes to staging file before Stage 2
4. Stage 2 interview: phases (3-6) + steps per phase
5. Append Stage 2 notes before Stage 3
6. Stage 3 interview: 6 guardrail questions
7. Silent pre-write validation (7 checks)
8. Read template → expand stages into self-contained checklist items → write task file
9. Broadcast TASK_READY when complete

**Quality enforcement**: Pre-write validation checklist ensures structural correctness before any file is written. The builder does NOT execute the task — it only creates the specification.

**Extension points**:
- Stage 3 guardrails can be customized per task type
- Template selection (`01` generic vs `02` complex) based on task characteristics
- MEMORY.md captures and reuses optimal patterns for specific task types
- `RECOMMENDED_BATCH_SIZE` is included in TASK_READY message based on task complexity

---

## 4. Pattern Categorization

**Directly Adoptable:**
- Self-contained checklist items (embed all context + action + verification + completion gate in a single item) is directly adoptable for SuperClaude sprint tasklist generation. This solves a real problem in multi-session sprint execution.
- The "no standalone context-reading items" rule is directly adoptable.
- The pre-write validation checklist is directly adoptable for SuperClaude's `/sc:tasklist` command output validation.

**Conditionally Adoptable:**
- The 3-stage structured interview is conditionally adoptable for SuperClaude's `/sc:brainstorm` → `/sc:tasklist` workflow. The stages map to discovery → structure → constraints.
- The MEMORY.md pattern accumulation is conditionally adoptable — valuable for persistent agent memory, but requires pruning discipline.

**Reject:**
- The mandatory 30-item completion gate repetition. A single completion gate policy in the task specification header is sufficient without repeating it in every item.
- The verbose template-reading requirement before every file creation. A cached template representation would reduce friction.
