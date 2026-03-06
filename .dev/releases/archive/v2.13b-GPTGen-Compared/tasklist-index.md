# TASKLIST INDEX -- v2.13 CLIRunner Pipeline Targeted Fixes

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.13 CLIRunner Pipeline Targeted Fixes |
| Generator Version | Roadmap->Tasklist Generator v3.0 |
| Generated | 2026-03-05T00:00:00Z |
| TASKLIST_ROOT | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/ |
| Total Phases | 4 |
| Total Tasks | 13 |
| Total Deliverables | 13 |
| Complexity Class | LOW |
| Primary Persona | refactorer |
| Consulting Personas | architect, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/phase-3-tasklist.md |
| Phase 4 Tasklist | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/phase-4-tasklist.md |
| Execution Log | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/ |
| Feedback Log | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Sprint Executor Tests | T01.01-T01.04 | STRICT: 0, STANDARD: 4, LIGHT: 0, EXEMPT: 0 |
| 2 | phase-2-tasklist.md | Duplication Elimination | T02.01-T02.04 | STRICT: 2, STANDARD: 2, LIGHT: 0, EXEMPT: 0 |
| 3 | phase-3-tasklist.md | Roadmap File Passing | T03.01-T03.02 | STRICT: 0, STANDARD: 2, LIGHT: 0, EXEMPT: 0 |
| 4 | phase-4-tasklist.md | Validation and Acceptance | T04.01-T04.03 | STRICT: 0, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |

## Source Snapshot
- The roadmap selects Option 3 targeted fixes and avoids restructuring sprint's execution model.
- The strategy is explicitly test-first: characterization tests precede refactoring.
- Process duplication removal is split into wait deletion, hook migration, and dead code removal.
- Roadmap file passing changes from `--file` usage to inline embedding with a 100KB guard.
- Validation requires full-suite regression checks, coverage >= 70%, NFR-007 verification, and no new dependencies.

## Deterministic Rules Applied
- Output phases were assigned sequentially by roadmap bucket appearance with no numbering gaps.
- Task IDs use the `T<PP>.<TT>` zero-padded format.
- Deliverable IDs use global `D-####` ordering across all phases.
- One task was created per independently deliverable roadmap item.
- Checkpoints were added at each phase end because no phase exceeded five tasks.
- Effort and risk labels were assigned using keyword-based deterministic mappings.
- Compliance tiers were assigned using compound phrases, keyword scores, and context boosters.
- Verification routing follows tier mapping only: STANDARD tasks use direct test execution.
- MCP requirements were attached from the computed tier table.
- Traceability links every roadmap item to at least one task and deliverable.

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | This roadmap implements Option 3 (Targeted Fixes) from the adversarial-debated pipeline architecture decision (convergence 0.72). |
| R-002 | Phase 1 | The strategy is test-first: characterization tests are written before any refactoring begins, establishing a safety net. |
| R-003 | Phase 1 | Executor unification remains a hypothesis to validate in future phases, not a decision earned by current evidence. |
| R-004 | Phase 1 | Establish a characterization test safety net for sprint's executor by covering the 6 untested subsystems. |
| R-005 | Phase 1 | Watchdog/stall detection tests (3 cases: kill action, warn action, reset on resume). |
| R-006 | Phase 1 | Multi-phase sequencing tests (2 cases: 3-phase happy path, halt at phase 3). |
| R-007 | Phase 1 | TUI/monitor/tmux integration tests (4 cases: TUI updates, TUI error resilience, monitor lifecycle, tmux tail pane). |
| R-008 | Phase 1 | Diagnostics tests (2 cases: failure triggers collector, collection failure is non-fatal). |
| R-009 | Phase 2 | Eliminate ~94 lines of duplicated process method overrides and remove confirmed dead code from roadmap executor. |
| R-010 | Phase 2 | Delete sprint's wait() override (pure no-op duplication). |
| R-011 | Phase 2 | Add on_spawn, on_signal, on_exit hook params and add on_exit call to wait() success path. |
| R-012 | Phase 2 | Add hook factory functions, wire hooks in sprint ClaudeProcess.__init__, and verify NFR-007 compliance. |
| R-013 | Phase 2 | Delete _FORBIDDEN_FLAGS and _build_subprocess_argv from roadmap/executor.py. |
| R-014 | Phase 3 | Fix the unreliable --file flag approach by embedding input file contents inline with a size guard. |
| R-015 | Phase 3 | Integration test for file-passing verifies embedded content, spaced paths, and 100KB fallback. |
| R-016 | Phase 4 | Full test suite passes, sprint executor coverage >= 70%, and diff-based removal goals are met. |
| R-017 | Phase 4 | NFR-007 zero violations and no new Python package dependencies are required. |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-004, R-005 | Watchdog and stall characterization plan | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/evidence.md | M | Low |
| D-0002 | T01.02 | R-004, R-006 | Multi-phase sequencing characterization plan | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/evidence.md | M | Low |
| D-0003 | T01.03 | R-004, R-007 | TUI monitor tmux characterization plan | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/evidence.md | M | Low |
| D-0004 | T01.04 | R-004, R-008 | Diagnostics characterization plan | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/evidence.md | M | Low |
| D-0005 | T02.01 | R-009, R-010 | wait() override removal record | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/evidence.md | M | Low |
| D-0006 | T02.02 | R-009, R-011 | ClaudeProcess lifecycle hook design | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/evidence.md | L | Medium |
| D-0007 | T02.03 | R-009, R-012 | Sprint hook migration and NFR-007 record | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/evidence.md | L | Medium |
| D-0008 | T02.04 | R-009, R-013 | Roadmap executor dead-code removal record | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/evidence.md | S | Low |
| D-0009 | T03.01 | R-014 | Inline input embedding design | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/evidence.md | M | Low |
| D-0010 | T03.02 | R-015 | File-passing integration test record | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/evidence.md | M | Low |
| D-0011 | T04.01 | R-016 | Full-suite and coverage validation record | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/evidence.md | M | Low |
| D-0012 | T04.02 | R-016, R-017 | Diff and NFR-007 validation record | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/evidence.md | M | Low |
| D-0013 | T04.03 | R-017 | Dependency validation record | STANDARD | Direct test execution | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/spec.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/notes.md; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/evidence.md | S | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/ |
| R-002 | T01.01, T01.02 | D-0001, D-0002 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/ |
| R-003 | T02.03 | D-0007 | STRICT | [████████--] 85% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/ |
| R-004 | T01.01, T01.02, T01.03, T01.04 | D-0001, D-0002, D-0003, D-0004 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/ |
| R-005 | T01.01 | D-0001 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0001/ |
| R-006 | T01.02 | D-0002 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0002/ |
| R-007 | T01.03 | D-0003 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0003/ |
| R-008 | T01.04 | D-0004 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0004/ |
| R-009 | T02.01, T02.02, T02.03, T02.04 | D-0005, D-0006, D-0007, D-0008 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/ |
| R-010 | T02.01 | D-0005 | STANDARD | [████████--] 75% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0005/ |
| R-011 | T02.02 | D-0006 | STRICT | [████████--] 85% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0006/ |
| R-012 | T02.03 | D-0007 | STRICT | [████████--] 85% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0007/ |
| R-013 | T02.04 | D-0008 | STANDARD | [████████--] 75% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0008/ |
| R-014 | T03.01 | D-0009 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0009/ |
| R-015 | T03.02 | D-0010 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0010/ |
| R-016 | T04.01, T04.02 | D-0011, D-0012 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0011/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/ |
| R-017 | T04.02, T04.03 | D-0012, D-0013 | STANDARD | [████████--] 80% | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0012/; .dev/releases/current/v2.13-CLIRunner-PipelineUnification/artifacts/D-0013/ |

## Execution Log Template

**Intended Path:** `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|
|  |  |  |  |  | Manual | TBD | .dev/releases/current/v2.13-CLIRunner-PipelineUnification/evidence/ |

## Checkpoint Report Template

For each checkpoint created under Section 4.8, execution must produce one report using this template.

- `# Checkpoint Report -- <Checkpoint Title>`
- `**Checkpoint Report Path:** .dev/releases/current/v2.13-CLIRunner-PipelineUnification/checkpoints/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status`
  - `Overall: Pass | Fail | TBD`
- `## Verification Results`
  - Align to the three checkpoint verification bullets
- `## Exit Criteria Assessment`
  - Align to the three checkpoint exit-criteria bullets
- `## Issues & Follow-ups`
  - Reference `T<PP>.<TT>` and `D-####`
- `## Evidence`
  - Intended evidence paths under `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/evidence/`

## Feedback Collection Template

**Intended Path:** `.dev/releases/current/v2.13-CLIRunner-PipelineUnification/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Generation Notes
- Phase buckets were derived from explicit milestone headings M1 through M4.
- No clarification tasks were inserted because each task retained a confidence score >= 0.70.
- The roadmap already supplied the release path used as `TASKLIST_ROOT`.
