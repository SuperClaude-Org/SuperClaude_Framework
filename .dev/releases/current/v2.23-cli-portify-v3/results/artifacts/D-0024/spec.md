# D-0024: Updated Return Contract Schema

## Summary
Added comprehensive Return Contract Schema section to SKILL.md containing all 18+ new fields as specified in R-032.

## Fields Added
1. `contract_version` — Schema version string ("2.0")
2. `spec_file` — Path to generated release spec
3. `panel_report` — Path to panel-report.md
4. `output_directory` — Working directory for artifacts
5. `quality_scores.clarity` — 0.0-10.0 float
6. `quality_scores.completeness` — 0.0-10.0 float
7. `quality_scores.testability` — 0.0-10.0 float
8. `quality_scores.consistency` — 0.0-10.0 float
9. `quality_scores.overall` — mean of 4 dimensions (SC-010)
10. `convergence_iterations` — Review loop count
11. `convergence_state` — CONVERGED | ESCALATED | NOT_STARTED
12. `phase_timing.phase_3_seconds` — Wall clock timing
13. `phase_timing.phase_4_seconds` — Wall clock timing
14. `source_step_count` — Steps from Phase 1
15. `spec_fr_count` — FRs in generated spec
16. `api_snapshot_hash` — SHA-256 of pipeline-spec.md
17. `downstream_ready` — Boolean gate (SC-012)
18. `phase_contracts` — Per-phase status map
19. `warnings` — Advisory message list
20. `status` — success | partial | failed | dry_run
21. `failure_phase` — Phase number or null
22. `failure_type` — Enumeration value or null
23. `resume_phase` — Phase to resume from
24. `resume_substep` — Substep within phase
25. `resume_command` — Full CLI resume command

## Failure Type Enumeration (7 values)
- `template_failed`
- `brainstorm_failed`
- `brainstorm_timeout`
- `focus_failed`
- `critique_failed`
- `convergence_exhausted`
- `user_rejected`
- `prerequisite_failed` (added as 8th value for entry gate failures)

## Contract Emission
Contract emits on every invocation including failures (SC-009). Failure path defaults documented per NFR-009.

## File Modified
- `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md`
