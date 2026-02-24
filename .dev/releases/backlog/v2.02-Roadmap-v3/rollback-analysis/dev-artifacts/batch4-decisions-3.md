# Batch 4 — Dev Artifact Analysis (Decisions Batch 3)

**Analyzed:** 2026-02-24
**Files:** D-0007/spec.md, D-0008/spec.md, T01.03/notes.md

---

## 1. D-0007/spec.md — Fallback Protocol (F1, F2/3, F4/5)

**Path:** `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0007/spec.md`
**Task ID:** T02.03 | **Roadmap Item:** R-007 | **Tier:** STRICT

### Summary

Specifies the complete fallback protocol for the adversarial pipeline when the Skill tool is unavailable. The protocol is implemented in Wave 2 step 3d of `src/superclaude/skills/sc-roadmap/SKILL.md`.

The fallback is a state machine with three consolidated stages:

| Stage | Action | Output |
|-------|--------|--------|
| F1 — Variant Generation | Task tool dispatches N agents to produce variant files | >= 2 variant-\<model\>-\<persona\>.md files, each >= 100 words per analysis section |
| F2/3 — Diff Analysis + Debate (merged) | Task tool produces diff-analysis.md with per-variant sections, conflict summary, recommendation | diff-analysis.md (>= 100 words) |
| F4/5 — Base Selection + Merge + Contract (merged) | Task tool produces base selection, merged output, and return contract | base-selection.md, merged-output.md, return-contract.yaml |

Three error types trigger the fallback: (1) Skill not in allowed-tools, (2) Skill not found, (3) Skill already running. In the fallback-only variant, the fallback executes unconditionally without attempting the primary path.

The return contract under fallback mode sets `fallback_mode: true` and `convergence_score: 0.5` (estimated, not measured). Status can be `success`, `partial`, or `failed`.

### Cross-References

- **Target file:** `src/superclaude/skills/sc-roadmap/SKILL.md` (Wave 2, step 3d)
- **D-0008:** Consumes the return-contract.yaml produced by this fallback in step 3e routing
- **T02.03:** Parent task for both D-0007 and D-0008
- **R-007:** Roadmap item this delivers against

---

## 2. D-0008/spec.md — Return Contract Routing in Step 3e

**Path:** `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/D-0008/spec.md`
**Task ID:** T02.03 | **Roadmap Item:** R-008 | **Tier:** STRICT

### Summary

Specifies how the roadmap skill consumes and routes on the return-contract.yaml produced by the adversarial pipeline (or its fallback). Implemented in Wave 2 step 3e of `src/superclaude/skills/sc-roadmap/SKILL.md`.

Four components:

1. **Missing-File Guard** — If return-contract.yaml does not exist after adversarial execution, emit an error message and treat as `status: failed`.

2. **YAML Parse Error Handling** — If return-contract.yaml is malformed, catch the error and treat as `status: failed`.

3. **Three-Status Routing** (convergence threshold: 0.6):

| status | convergence | action |
|--------|-------------|--------|
| success | any | Use merged_output_path; record scores; proceed to 3f |
| partial | >= 0.6 | Proceed with warning in extraction.md; proceed to 3f |
| partial | < 0.6, --interactive | Prompt user Y/n; Y proceeds, N aborts |
| partial | < 0.6, no --interactive | Abort with threshold message |
| failed | any | Abort with failure message |

4. **Canonical Schema Comment** — Documents the seven fields of return-contract.yaml: status, merged_output_path, convergence_score, fallback_mode, artifacts_dir, unresolved_conflicts, base_variant.

The spec confirms no status value falls through unhandled and the convergence threshold is consistently 0.6.

### Cross-References

- **Target file:** `src/superclaude/skills/sc-roadmap/SKILL.md` (Wave 2, step 3e)
- **D-0007:** Produces the return-contract.yaml that this spec routes on (including fallback variant with convergence_score 0.5, which is < 0.6 threshold)
- **T02.03:** Parent task for both D-0007 and D-0008
- **R-008:** Roadmap item this delivers against

---

## 3. T01.03/notes.md — Tier Classification Policy for Executable Specification Files

**Path:** `.dev/releases/current/v2.01-Roadmap-v3/tasklist/artifacts/T01.03/notes.md`
**Task ID:** T01.03 | **Roadmap Item:** R-001 (systemic) | **Tier:** EXEMPT

### Summary

A policy decision that the `*.md` path booster (+0.5 toward EXEMPT) in the `/sc:task-unified` tier classification algorithm does **not** apply to executable specification files. This is a sprint-wide classification ruling.

**Rationale:** The EXEMPT booster was designed for human-readable documentation (READMEs, guides, changelogs). Files like SKILL.md, command .md files, and ref .md files are interpreted by Claude Code as behavioral instructions that directly affect agent execution. They function as executable code, not documentation.

**Affected executable specification files in this sprint:**

- `src/superclaude/skills/sc-adversarial/SKILL.md`
- `src/superclaude/skills/sc-roadmap/SKILL.md`
- `src/superclaude/skills/sc-roadmap/refs/adversarial-integration.md`
- `src/superclaude/commands/roadmap.md`

**Impact on task tiers (without the booster):**

| Task | Tier |
|------|------|
| T02.01 | LIGHT |
| T02.02 | LIGHT |
| T02.03 | STRICT |
| T04.01 | STRICT |
| T04.02 | STRICT |
| T04.03 | STANDARD |
| T05.01 | STANDARD |
| T05.02 | STANDARD |
| T05.03 | STANDARD |

If the booster were incorrectly applied, T02.01, T02.02, T04.03, and T05.01-T05.03 would shift toward EXEMPT, reducing verification requirements for code-affecting changes.

The tie-breaker applied is tasklist deterministic rule 8 / tie-breaker rule 3 (reversibility): the more conservative interpretation is used because incorrectly lowering verification could allow behavior-breaking changes to pass unchecked.

**Policy statement for future sprints:** Any `.md` file that Claude Code reads and interprets as behavioral instructions is classified as code for tier purposes.

### Cross-References

- **R-001:** Systemic roadmap item (affects all tasks)
- **Tasklist deterministic rule 8, tie-breaker rule 3:** Source of the conservative-interpretation principle
- **`/sc:task-unified` algorithm:** The tier classification system this policy modifies
- **All tasks T02.01 through T05.03:** Affected by this classification decision
- **Evidence path:** `TASKLIST_ROOT/tasklist/evidence/T01.03/`

---

## Cross-Reference Summary

```
D-0007 (Fallback Protocol) ──produces──→ return-contract.yaml ──consumed-by──→ D-0008 (Contract Routing)
    │                                                                              │
    └── both under T02.03 (STRICT) ────────────────────────────────────────────────┘

T01.03 (Tier Policy) ──sets tier for──→ T02.03 as STRICT (no EXEMPT booster)
                      ──sets tier for──→ T04.01, T04.02 as STRICT
                      ──sets tier for──→ T02.01, T02.02 as LIGHT
                      ──sets tier for──→ T04.03, T05.01-T05.03 as STANDARD
```

**Key dependency chain:** T01.03 policy decision justifies T02.03 being STRICT tier, which governs D-0007 and D-0008 deliverables. The fallback convergence_score of 0.5 (D-0007) is deliberately below the 0.6 threshold (D-0008), meaning fallback results always trigger the partial/low-convergence path unless the user explicitly accepts via `--interactive`.
