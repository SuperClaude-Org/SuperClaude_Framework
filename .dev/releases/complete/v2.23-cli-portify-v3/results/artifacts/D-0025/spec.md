# D-0025: Resume Behavior Semantics

## Summary
Documented resume behavior semantics for Phase 3 and Phase 4 in the Return Contract Schema section of SKILL.md.

## Phase 3 Resume (`resume_substep=3c`)
- Preserves populated spec from Step 3b (template instantiation + content population)
- Brainstorm pass (Step 3c) re-runs from scratch against preserved draft
- Gap incorporation (Step 3d) re-runs after brainstorm completes
- All Phase 1 and Phase 2 artifacts preserved unchanged

## Phase 4 Resume (`resume_substep=4a`)
- Preserves complete draft spec from Phase 3 (including brainstorm findings)
- Focus pass (Step 4a) re-runs from scratch against preserved spec
- All subsequent steps (4b, 4c, 4d) re-run in sequence
- Convergence loop resets iteration counter to 1
- All Phase 1, Phase 2, and Phase 3 artifacts preserved unchanged

## Resumable Failure Types
| Failure Type | Resume Point |
|---|---|
| `brainstorm_failed` | `3c` |
| `brainstorm_timeout` | `3c` |
| `focus_failed` | `4a` |
| `critique_failed` | `4a` |

## Non-Resumable Failure Types
- `template_failed`, `convergence_exhausted`, `user_rejected`, `prerequisite_failed`

## File Modified
- `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
