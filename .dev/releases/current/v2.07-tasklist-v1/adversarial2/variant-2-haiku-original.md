# Tasklist Generator Refactor Notes for Sprint CLI + /sc:task-unified

## Context
Requested analysis target:
- Sprint CLI (`superclaude sprint run`)
- `/sc:task-unified` command/protocol
- Existing generator prompt: `Tasklist-Generator-Prompt-v2.1-unified.md`

Goal: refactor generator output so it is best suited for Sprint CLI execution and `/sc:task-unified` behavior.

---

## Ground-Truth Contracts (Code-Evidenced)

1. Sprint execution is index-driven and phase-file based
- `src/superclaude/cli/sprint/commands.py:19`
- `src/superclaude/cli/sprint/commands.py:124`

2. Phase discovery requires canonical filename patterns (prefer `phase-<n>-tasklist.md`)
- `src/superclaude/cli/sprint/config.py:17`
- `src/superclaude/cli/sprint/config.py:38`

3. Phase display name is extracted from first heading in each phase file
- `src/superclaude/cli/sprint/config.py:60`

4. Sprint subprocess prompts `/sc:task-unified` per phase and expects completion report with `EXIT_RECOMMENDATION: CONTINUE|HALT`
- `src/superclaude/cli/sprint/process.py:46`
- `src/superclaude/cli/sprint/process.py:64`

5. Output monitor expects task IDs in `TNN.NN` format
- `src/superclaude/cli/sprint/monitor.py:23`

6. `/sc:task-unified` depends on strict tier semantics and classification/execution protocol
- `src/superclaude/commands/task-unified.md:46`
- `src/superclaude/skills/sc-task-unified-protocol/SKILL.md:114`

---

## Current Prompt Mismatch

`Tasklist-Generator-Prompt-v2.1-unified.md` enforces one single markdown output (`tasklist.md`) only.

Evidence:
- Single-document template requirement: `.../Tasklist-Generator-Prompt-v2.1-unified.md:388`
- Final output one-document constraint: `.../Tasklist-Generator-Prompt-v2.1-unified.md:640`

This conflicts with Sprint CLI’s phase file orchestration model (`tasklist-index.md` + phase files).

---

## Required Refactor (Priority Order)

## 1) Change output contract from single-file to multi-file bundle
Replace “output one markdown only” with deterministic multi-file generation:
- `TASKLIST_ROOT/tasklist-index.md`
- `TASKLIST_ROOT/phase-1-tasklist.md` … `phase-N-tasklist.md`
- Optional: `TASKLIST_ROOT/tasklist.md` as human summary only

## 2) Make generated index Sprint-discoverable
Ensure index includes literal references to phase files:
- `phase-1-tasklist.md`
- `phase-2-tasklist.md`
- etc.

Avoid placeholder-only references that may not resolve to concrete filenames.

## 3) Standardize filename policy
Enforce generator output naming to canonical Sprint primary convention:
- `phase-<n>-tasklist.md`

(Do not emit mixed aliases unless explicitly requested.)

## 4) Preserve sequential/no-gap phase numbering
Keep deterministic renumbering and no gaps (`Phase 1..N`) so execution order is unambiguous.

## 5) Enforce phase heading format
Each phase file should begin with:
- `# Phase N — <Phase Name>`

This supports clean phase name extraction and TUI display.

## 6) Preserve task ID format compatible with monitor
Keep task IDs exactly:
- `T<PP>.<TT>` (e.g., `T01.01`)

## 7) Embed `/sc:task-unified` metadata in each task
Per task include execution metadata fields aligned to protocol:
- Tier (`STRICT|STANDARD|LIGHT|EXEMPT`)
- Verification Method
- MCP Requirements
- Fallback Allowed
- Dependencies

## 8) Add explicit phase completion protocol in every phase file
Include deterministic completion instruction requiring phase result report with:
- YAML status frontmatter
- task status table
- files modified
- blockers
- `EXIT_RECOMMENDATION: CONTINUE|HALT`

## 9) Move heavy cross-phase metadata to index
Keep Deliverable Registry, Traceability Matrix, and global templates in `tasklist-index.md`.
Keep phase files execution-focused to reduce prompt payload per phase run.

## 10) Add generator self-check gate (“Sprint Compatibility Check”)
Before final output, validate:
1. index exists
2. all referenced phase files exist
3. phase numbers contiguous
4. all task IDs valid `TNN.NN`
5. phase headings follow `# Phase N — ...`

---

## Recommended Target Layout

```text
TASKLIST_ROOT/
  tasklist-index.md
  phase-1-tasklist.md
  phase-2-tasklist.md
  ...
  phase-N-tasklist.md
  artifacts/
  evidence/
  checkpoints/
  execution-log.md
  feedback-log.md
```

---

## Suggested Prompt Section Changes

1. Replace Section 1/6/12 single-document constraints with multi-file deliverable contract.
2. Add a new section: “File Emission Rules (Deterministic)” describing index + per-phase file generation.
3. Update “Tasklist Index” section so it is explicitly the contents of `tasklist-index.md` (not just a section inside a monolith).
4. Add “Phase File Template” section used to render each `phase-N-tasklist.md`.
5. Keep deterministic tiering/verification logic; relocate where needed so each phase file carries only task-execution essentials.

---

## Outcome
Implementing these refactors will align generator output directly with:
- Sprint CLI discovery/execution model
- `/sc:task-unified` tiered execution model
- existing runtime monitor/logging assumptions

while preserving deterministic and traceable tasklist generation.