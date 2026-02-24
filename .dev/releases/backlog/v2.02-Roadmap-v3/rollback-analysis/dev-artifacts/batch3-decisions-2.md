# Batch 3 — Decision Artifacts (D-0004, D-0005, D-0006)

**Analyzed:** 2026-02-24
**Source directory:** `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/`

---

## D-0004 — Skill in allowed-tools (roadmap.md)

**File:** `artifacts/D-0004/evidence.md`
**Task ID:** T02.01 | **Roadmap Item:** R-004 | **Tier:** LIGHT

### Summary

Documents a single-line change to `src/superclaude/commands/roadmap.md` that appends `Skill` to the `allowed-tools` list. The existing tool list (`Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task`) is preserved verbatim; `Skill` is added at the end.

### Purpose

Enable the roadmap command to invoke the `Skill` tool, which is required for the skill-based invocation workflow introduced in this release. Without this entry, the roadmap command would be blocked from calling skills by the allowed-tools policy.

### Verification

A grep-based check confirms the string `Skill` is present in the target file. Result: PASS.

### Cross-References

- **R-004**: Parent roadmap item.
- **T02.01**: Parent task in the tasklist.
- **D-0005**: Mirror change for the skill-level SKILL.md (same modification, different file).
- **Policy doc**: `docs/architecture/command-skill-policy.md` (the policy that governs allowed-tools lists).

---

## D-0005 — Skill in allowed-tools (sc-roadmap SKILL.md)

**File:** `artifacts/D-0005/evidence.md`
**Task ID:** T02.02 | **Roadmap Item:** R-005 | **Tier:** LIGHT

### Summary

Identical in nature to D-0004 but targets `src/superclaude/skills/sc-roadmap/SKILL.md` instead of the command-level file. Appends `Skill` to the same `allowed-tools` list while leaving all pre-existing entries unchanged.

### Purpose

Ensures the sc-roadmap skill definition itself also declares `Skill` as an allowed tool. Both the command file (D-0004) and the skill file (D-0005) must be updated for the tool to be usable end-to-end, because allowed-tools enforcement applies at both layers.

### Verification

Grep-based check confirms presence. Result: PASS.

### Cross-References

- **R-005**: Parent roadmap item.
- **T02.02**: Parent task in the tasklist.
- **D-0004**: The command-level counterpart of this same change.
- **D-0006**: The next deliverable in the same wave (Wave 2), which depends on the Skill tool being allowed.

---

## D-0006 — Wave 2 Step 3 Sub-Steps 3a-3f

**File:** `artifacts/D-0006/spec.md`
**Task ID:** T02.03 | **Roadmap Item:** R-006 | **Tier:** STRICT

### Summary

Specification for decomposing Wave 2 step 3 in `src/superclaude/skills/sc-roadmap/SKILL.md` into six atomic sub-steps (3a through 3f). This is the adversarial-agent invocation step, broken down to handle agent parsing, variant expansion, orchestrator injection, fallback protocol execution, return-contract consumption, and template skipping.

### Sub-Step Breakdown

| Sub-Step | Label | Tool | Verb |
|----------|-------|------|------|
| 3a | Parse agents | Read | Call |
| 3b | Expand variants | inline | Expand |
| 3c | Add orchestrator if needed | inline | Add |
| 3d | Execute fallback protocol | Task (x3) | Execute, Emit, Use |
| 3e | Consume return contract | Read | Read |
| 3f | Skip template | inline | Skip |

### Purpose

Provides the granular execution plan for adversarial agent invocation within the roadmap skill. The spec applies the "fallback-only" sprint variant (because T01.01 determined TOOL_NOT_AVAILABLE for the primary Skill tool call), meaning step 3d runs the fallback protocol (F1, F2/3, F4/5) unconditionally rather than as an error-recovery path.

### Structural Audit

All 8 structural checks passed:
- 6 sub-steps present (3a-3f)
- Fallback covers 3 error types
- Missing-file guard in 3e
- Convergence threshold 0.6 in 3e
- YAML parse error handling in 3e
- Skip-template instruction in 3f
- `fallback_mode: true` in F4/5 contract
- Sentinel 0.5 with `# estimated, not measured` comment

### Cross-References

- **R-006**: Parent roadmap item.
- **T02.03**: Parent task in the tasklist.
- **T01.01**: The prerequisite finding (TOOL_NOT_AVAILABLE) that forced the fallback-only variant.
- **D-0004, D-0005**: The allowed-tools changes that make Skill available; D-0006 depends on these being in place.
- **sc-roadmap SKILL.md**: The file where these sub-steps are (or will be) materialized.
- **refs/adversarial-integration.md**: The Agent Specification Parsing algorithm referenced by sub-step 3a.
- **refs/scoring.md**: Convergence threshold (0.6) referenced by sub-step 3e.

---

## Rollback Considerations

### D-0004 and D-0005 (LIGHT tier)
- **Rollback action**: Remove `, Skill` from the `allowed-tools` line in both `src/superclaude/commands/roadmap.md` and `src/superclaude/skills/sc-roadmap/SKILL.md` (note: the skill directory may have been renamed to `sc-roadmap-protocol` per git status).
- **Risk**: Low. These are single-token additions at end of list. Removal has no side effects on other tools.
- **Dependency**: D-0006 depends on Skill being allowed. If D-0006 is also rolled back, these can be safely reverted.

### D-0006 (STRICT tier)
- **Rollback action**: Remove or revert the 3a-3f sub-step decomposition from the SKILL.md file, restoring the original monolithic step 3.
- **Risk**: Medium. This is a structural change to the skill's execution flow. The fallback-only variant logic and all 6 sub-steps would need to be cleanly excised.
- **Dependency**: Depends on D-0004/D-0005 for the Skill tool permission. Also depends on T01.01 finding. Rolling back D-0006 without rolling back D-0004/D-0005 is safe (leaves Skill allowed but unused by step 3).
