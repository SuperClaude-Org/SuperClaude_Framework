# Sprint Variant Decision

**VARIANT: PRIMARY_VARIANT**

---

**Task**: T01.04
**Date**: 2026-02-25
**Roadmap Item IDs**: R-002, R-006

---

## Decision Inputs

| Source | Artifact | Value |
|---|---|---|
| T01.01 Probe | `probe-results.md` | **PRIMARY_PATH_VIABLE** |
| T01.02 Semantics | `probe-results.md` § Constraint Semantics | **SAME_NAME_BLOCKED** |
| T01.03 Prerequisites | `prereq-validation.md` | **PREREQS_PASS** (6/6) |

## Decision Logic

```
IF probe_result == PRIMARY_PATH_VIABLE AND prereqs_result == PREREQS_PASS
THEN → PRIMARY_VARIANT
```

Both conditions are satisfied:
1. **Probe**: Task agent successfully invoked `sc:adversarial-protocol` via the Skill tool — cross-skill invocation works
2. **Constraint**: SAME_NAME_BLOCKED — the naming convention (`-protocol` suffix) ensures `sc:roadmap-protocol` can invoke `sc:adversarial-protocol` without triggering the constraint
3. **Prerequisites**: All 6 dependencies verified present and functional

## Rationale

The primary implementation path is empirically viable. The Skill tool is accessible from Task agent contexts, cross-skill invocation succeeds, the "skill already running" constraint only blocks same-name re-entry (which the architecture avoids by design), and all prerequisite files and make targets exist.

---

## Phase 2 Routing Instructions

### T02.01 — Allowed-Tools Updates
- **Action**: Add `Skill` to `allowed-tools` in both target files
- **Files**:
  - `src/superclaude/commands/roadmap.md` (if Skill is not already present)
  - `src/superclaude/skills/sc-roadmap-protocol/SKILL.md` (if Skill is not already present)
- **Note**: Check current state first — the `sc-adversarial-protocol/SKILL.md` already has `Skill` in allowed-tools (line 4). Verify whether roadmap files already do too.

### T02.02 — Wave 2 Step 3 Rewrite
- **Variant**: PRIMARY_VARIANT — implement sub-steps 3a through 3f with Skill tool as the primary invocation mechanism
- **Sub-steps to implement**: 3a (validate prerequisites), 3b (construct invocation), 3c (invoke via Skill tool), 3d (fallback protocol — defense-in-depth), 3e (return contract routing), 3f (result integration)
- **Fallback levels to activate**: F1 (Skill tool error), F2/F3 (invocation failure), F4/F5 (result parsing failure)
- **Fallback framing**: The fallback protocol is defense-in-depth, NOT the primary mechanism. Primary path uses Skill tool invocation.
- **Constraint handling**: Step 3d should list "skill already running" as one of three error types that trigger fallback, but note that the naming convention makes this error type unlikely in practice.

---

## Confirmation Required

**This decision requires user acknowledgment before Phase 2 begins.**

Awaiting confirmation to proceed to Phase 2.
