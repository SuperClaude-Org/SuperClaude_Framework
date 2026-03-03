# Probe Results — Skill Tool Cross-Skill Invocation

**Task**: T01.01
**Date**: 2026-02-25

---

## Binary Decision

**DECISION: PRIMARY_PATH_VIABLE**

---

## Evidence Summary

A Task agent (sonnet) successfully invoked `sc:adversarial-protocol` via the Skill tool from a clean subagent context. No errors, no constraint fires. The Skill tool resolved the skill by name and delivered full SKILL.md content.

| Field | Value |
|---|---|
| TOOL_AVAILABILITY | yes |
| INVOCATION_ATTEMPT | succeeded |
| ERROR_MESSAGE | none |
| CONSTRAINT_OBSERVED | no |

---

## Constraint Semantics

**Task**: T01.02
**Date**: 2026-02-25

### Semantic Label

**SAME_NAME_BLOCKED**

### Evidence

Three independent evidence sources converge on the same conclusion:

**Source 1 — Skill Tool Description (verbatim)**:
> "Do not invoke a skill that is already running"

This is a behavioral instruction to Claude — the constraint applies to invoking a skill **with the same name** as one currently active. It is not a programmatic runtime check but an instruction-following constraint.

**Source 2 — Command/Skill Architecture Policy** (`rollback-analysis/framework/command-skill-policy.md:46-48`):
> "The command and skill MUST have different names to avoid the 'skill already running' re-entry block. When `/sc:adversarial` triggers, the skill `sc:adversarial` is marked as running. If the command tried to invoke `Skill sc:adversarial`, it would be blocked. Using `sc:adversarial-protocol` as the skill name avoids this entirely."

This confirms the constraint is **name-based**: invoking a skill with a different name (e.g., `sc:adversarial-protocol` while `sc:roadmap-protocol` is running) is permitted.

**Source 3 — T01.01 Probe Result**:
The Task agent successfully invoked `sc:adversarial-protocol` from a clean context. No constraint fired because no skill with the same name was already running.

### Implications for T02.02

- The fallback protocol must handle the error type "skill already running" but this error should **never fire** in the normal path because:
  - `sc:roadmap-protocol` invokes `sc:adversarial-protocol` — different names
  - The architecture was specifically designed to avoid this via the `-protocol` suffix naming convention
- The constraint is NOT `ANY_SKILL_BLOCKED` — multiple different-named skills can coexist
- The constraint is NOT `SAME_INSTANCE_BLOCKED` — it is name-based, not instance-based
- The fallback protocol in T02.02 step 3d should still include "skill already running" as one of three error types to handle (defense-in-depth), but the primary path is not at risk from this constraint
