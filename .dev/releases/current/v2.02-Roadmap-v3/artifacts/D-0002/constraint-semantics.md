# D-0002 — Constraint Semantics Analysis

**Task ID**: T01.02
**Roadmap Item IDs**: R-002, R-004
**Date**: 2026-02-25

---

## Semantic Label

**SAME_NAME_BLOCKED**

---

## Definition

The "skill already running" constraint in the Skill tool blocks invocation of a skill **with the same name** as one currently active. It does NOT block invocation of a different-named skill while another skill is running.

---

## Evidence

| # | Source | Location | Finding |
|---|--------|----------|---------|
| 1 | Skill Tool description | ToolSearch output | "Do not invoke a skill that is already running" — instruction-following constraint, name-based |
| 2 | Command/Skill Architecture Policy | `rollback-analysis/framework/command-skill-policy.md:46-48` | Explicitly states naming convention exists to avoid re-entry block; different names bypass the constraint |
| 3 | T01.01 Probe | `probe-results.md` Binary Decision | Task agent invoked `sc:adversarial-protocol` with no constraint fire — different name from any running skill |

---

## Ruled-Out Alternatives

| Label | Ruled Out? | Reason |
|---|---|---|
| SAME_NAME_BLOCKED | **Selected** | All three evidence sources confirm name-based blocking |
| ANY_SKILL_BLOCKED | Yes | Architecture policy explicitly states different-named skills bypass the constraint |
| SAME_INSTANCE_BLOCKED | Yes | Constraint is name-based per policy document, not instance-based |

---

## Connection to T02.02

The SAME_NAME_BLOCKED finding means:
1. **Primary path is safe**: `sc:roadmap-protocol` can invoke `sc:adversarial-protocol` because the names differ
2. **Fallback still needed**: The fallback protocol should handle "skill already running" as one of three error types (defense-in-depth), even though the naming convention makes this error unlikely
3. **No both-interpretation documentation needed**: The finding is unambiguous — T02.02 does not need to document multiple interpretations
