

---
total_diff_points: 12
shared_assumptions_count: 14
---

# Diff Analysis: Opus-Architect vs Haiku-Architect Roadmaps

## 1. Shared Assumptions and Agreements

Both variants agree on:

1. **Complexity score**: 0.65 (moderate)
2. **`spec_patch.py` as leaf module**: No reverse imports, stdlib + PyYAML only
3. **`_apply_resume()` remains unchanged**
4. **`execute_roadmap(auto_accept: bool = False)` as the only public API change**
5. **Atomic writes via `.tmp` + `os.replace()`**
6. **All new executor functions use `_` prefix (private)**
7. **FR-010 six-step disk-reread sequence** as mandatory
8. **Recursion guard**: local variable, max 1 cycle per invocation
9. **PyYAML ≥6.0 as new dependency** (both flag need to verify transitive status)
10. **TOCTOU is a documented limitation**, not solved in this release
11. **Non-interactive detection** via `sys.stdin.isatty()`
12. **Zero optional flags** on the CLI command
13. **Click `Path(exists=True)`** for `output_dir` validation
14. **Same set of files created/modified** (spec_patch.py, commands.py, executor.py, pyproject.toml, test files)

---

## 2. Divergence Points

### D-1: Phase Count and Structure

- **Opus**: 5 phases (P1–P5), no Phase 0. Jumps straight into implementation.
- **Haiku**: 6 phases (P0–P5), includes an explicit "Architecture confirmation and requirement traceability" phase before code.
- **Impact**: Haiku's P0 adds 0.5 days but reduces ambiguity risk. Opus implicitly assumes open questions are resolved during P1–P2, which could cause rework if assumptions prove wrong.

### D-2: Phase Granularity for Executor Work

- **Opus**: Combines auto-accept threading and retry cycle into a single Phase 3 (6 subtasks, ~3-4 hours).
- **Haiku**: Splits this into Phase 3 (signature/threading, 1 day) and Phase 4 (retry cycle, 1.5 days) — treating them as distinct milestones.
- **Impact**: Haiku's split provides a clearer checkpoint between "API compatibility verified" and "retry correctness verified." Opus's monolithic phase risks conflating two distinct risk profiles.

### D-3: Total Timeline Estimate

- **Opus**: 10–13 hours (~1.5–2 days of focused work).
- **Haiku**: 4.5–5.0 days of engineering effort, 6.0 days elapsed.
- **Impact**: Significant divergence. Opus's estimate is aggressive and assumes high developer familiarity. Haiku's estimate accounts for QA effort, open question resolution, and checkpoint reviews. Haiku is likely more realistic for a team context; Opus may be accurate for a single experienced developer working without interruption.

### D-4: Milestone Checkpoints

- **Opus**: No explicit checkpoints beyond phase completion.
- **Haiku**: 4 named checkpoints (A–D) with explicit go/no-go decisions.
- **Impact**: Haiku provides better governance and risk management. Opus assumes continuous progress without formal review gates.

### D-5: Risk Count and Depth

- **Opus**: 6 risks (RISK-001 through RISK-005 + PyYAML dep), table format with severity/probability.
- **Haiku**: 7 risks with detailed narrative per risk, including "Residual concern" annotations.
- **Impact**: Haiku identifies one additional risk (Risk 2: stale in-memory state) as a standalone item, which Opus covers only implicitly in the FR-010 implementation. Haiku's residual concerns are valuable for future maintainers.

### D-6: `started_at` Fallback Strategy

- **Opus**: Recommends "skip mtime check if no timestamp" (conservative: allow cycle to proceed).
- **Haiku**: Recommends "treat as retry condition not met and proceed to normal failure path" (conservative: block cycle).
- **Impact**: Opposite approaches. Opus favors permissiveness (retry when uncertain), Haiku favors safety (don't retry when uncertain). This is a genuine design disagreement with correctness implications.

### D-7: Validation Organization

- **Opus**: AC matrix as a flat table (14 rows) with test approach per criterion.
- **Haiku**: 5-layer validation pyramid (unit → CLI → state integrity → executor integration → failure-path) with AC criteria grouped by theme.
- **Impact**: Haiku's layered approach provides better test architecture guidance. Opus's flat table is more directly traceable to spec but doesn't guide test organization.

### D-8: Acceptance Criteria Count

- **Opus**: References 14 acceptance criteria (AC-1 through AC-14).
- **Haiku**: References 15 success criteria (mentions "all 15" multiple times).
- **Impact**: Haiku may be counting an additional criterion not present in Opus's enumeration (possibly AC-15 or an NFR promoted to AC status). This discrepancy needs clarification against the source spec.

### D-9: Resource/Staffing Model

- **Opus**: Implicitly single-developer execution. No role breakdown.
- **Haiku**: Explicitly identifies 3 roles (architect/lead, backend engineer, QA/test engineer).
- **Impact**: Haiku's staffing model explains its longer timeline and is more appropriate for team planning. Opus's model works for solo execution.

### D-10: YAML Boolean Coercion Stance

- **Opus**: Lists YAML 1.1 boolean coercion (`yes`/`on`/`1`) as accepted behavior in edge case tests.
- **Haiku**: Requires `spec_update_required: true` as boolean, explicitly mentions testing for string `"true"` rejection.
- **Impact**: Potentially contradictory. Opus accepts broader YAML coercion; Haiku wants stricter type checking. The spec should be the tiebreaker — if it says "boolean, not string," Haiku's interpretation is more faithful.

### D-11: Architect Recommendations Format

- **Opus**: Scattered throughout as inline "Architect's note" annotations.
- **Haiku**: Dedicated section (§ Architect recommendations) with 6 numbered items.
- **Impact**: Haiku's consolidated recommendations are easier to review and act on. Opus's inline notes provide better locality but risk being missed.

### D-12: Operational Constraints Documentation

- **Opus**: Mentions TOCTOU documentation as a Phase 4 task.
- **Haiku**: Lists 5 explicit operational constraints as a standalone section, plus recommends prominent documentation of single-writer assumption.
- **Impact**: Haiku is more thorough in surfacing constraints that affect operators, not just developers.

---

## 3. Areas Where One Variant Is Clearly Stronger

### Opus is stronger in:

- **AC traceability**: The flat AC-to-test table provides immediate, auditable mapping from spec to verification. Every AC has a clear "Yes/No automated" answer.
- **Implementation specificity**: Subtasks reference exact function names, exact parameter signatures, and exact file paths. Less room for interpretation.
- **Parallelization notes**: Explicitly identifies TDD parallelization opportunities (P1.4 can run alongside P1.1–P1.3).
- **Conciseness**: ~40% fewer words while covering the same functional scope. Less cognitive overhead for implementers.

### Haiku is stronger in:

- **Risk management depth**: Residual concern annotations prevent future developers from assuming risks are fully mitigated. Risk 2 (stale in-memory state) as a standalone item is valuable.
- **Governance structure**: Named checkpoints with go/no-go decisions, explicit staffing model, and Phase 0 pre-work provide better project management scaffolding.
- **Validation architecture**: The 5-layer test pyramid is a better guide for organizing test code than a flat table.
- **Operational documentation**: Explicit operational constraints section ensures non-developer stakeholders understand limitations.
- **Defensive design stance**: Consistently favors safety over permissiveness (e.g., `started_at` fallback, boolean coercion strictness).

---

## 4. Areas Requiring Debate to Resolve

1. **`started_at` fallback behavior (D-6)**: This is a correctness-impacting disagreement. Opus says "allow retry when uncertain," Haiku says "block retry when uncertain." The spec should arbitrate — if FR-009 lists `started_at` comparison as a required condition, Haiku's safer interpretation is more faithful. If the condition is advisory, Opus's approach avoids false negatives.

2. **YAML boolean coercion scope (D-10)**: Should `spec_update_required: "true"` (string) be accepted? Opus says yes (via YAML 1.1 coercion), Haiku says no (strict boolean only). This affects operator UX when hand-editing deviation files.

3. **Timeline realism (D-3)**: The 3–4x gap between estimates needs reconciliation. If this is solo work by a developer familiar with the codebase, Opus's 10–13 hours may be accurate. If this involves code review, QA handoff, and open question resolution meetings, Haiku's 5 days is more realistic.

4. **Phase 0 necessity (D-1)**: Is a formal architecture confirmation phase worth 0.5 days? If open questions (#1, #3, #5 from the spec) are already resolved, Phase 0 is overhead. If they're genuinely unresolved, skipping it risks rework in Phase 3.

5. **AC count discrepancy (D-8)**: The difference between 14 and 15 acceptance criteria must be resolved against the source spec before implementation begins.
