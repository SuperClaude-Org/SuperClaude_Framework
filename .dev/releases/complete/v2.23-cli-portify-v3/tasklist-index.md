# TASKLIST INDEX -- CLI Portify v3: Release Spec Synthesis & Panel Review

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | CLI Portify v3: Release Spec Synthesis & Panel Review |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-09 |
| TASKLIST_ROOT | .dev/releases/backlog/v2.23-cli-portify-v3/ |
| Total Phases | 6 |
| Total Tasks | 28 |
| Total Deliverables | 42 |
| Complexity Class | MEDIUM |
| Primary Persona | architect |
| Consulting Personas | analyzer, backend, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | TASKLIST_ROOT/tasklist-index.md |
| Phase 1 Tasklist | TASKLIST_ROOT/phase-1-tasklist.md |
| Phase 2 Tasklist | TASKLIST_ROOT/phase-2-tasklist.md |
| Phase 3 Tasklist | TASKLIST_ROOT/phase-3-tasklist.md |
| Phase 4 Tasklist | TASKLIST_ROOT/phase-4-tasklist.md |
| Phase 5 Tasklist | TASKLIST_ROOT/phase-5-tasklist.md |
| Phase 6 Tasklist | TASKLIST_ROOT/phase-6-tasklist.md |
| Execution Log | TASKLIST_ROOT/execution-log.md |
| Checkpoint Reports | TASKLIST_ROOT/checkpoints/ |
| Evidence Directory | TASKLIST_ROOT/evidence/ |
| Artifacts Directory | TASKLIST_ROOT/artifacts/ |
| Validation Reports | TASKLIST_ROOT/validation/ |
| Feedback Log | TASKLIST_ROOT/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Template Foundation | T01.01-T01.03 | STRICT: 0, STANDARD: 2, LIGHT: 0, EXEMPT: 1 |
| 2 | phase-2-tasklist.md | Spec Synthesis Rewrite | T02.01-T02.04 | STRICT: 1, STANDARD: 3, LIGHT: 0, EXEMPT: 0 |
| 3 | phase-3-tasklist.md | Panel Review Rewrite | T03.01-T03.07 | STRICT: 1, STANDARD: 6, LIGHT: 0, EXEMPT: 0 |
| 4 | phase-4-tasklist.md | Contract & Command Surface | T04.01-T04.05 | STRICT: 3, STANDARD: 2, LIGHT: 0, EXEMPT: 0 |
| 5 | phase-5-tasklist.md | Validation & Testing | T05.01-T05.05 | STRICT: 0, STANDARD: 5, LIGHT: 0, EXEMPT: 0 |
| 6 | phase-6-tasklist.md | Sync & Documentation | T06.01-T06.04 | STRICT: 0, STANDARD: 1, LIGHT: 1, EXEMPT: 2 |

## Source Snapshot

- Evolves `sc:cli-portify` from code-generation pipeline to release specification synthesis and review pipeline
- Replaces Phases 3-4 (code generation + integration) with Phase 3 (spec synthesis with embedded brainstorm) and Phase 4 (spec-panel review with convergence loop)
- 26 requirements (17 functional, 9 non-functional) across 5 domains, modifying ~4 files with 1 new template
- Behavioral patterns from `sc:brainstorm` and `sc:spec-panel` are embedded inline (not invoked as commands)
- Convergence loop uses state machine model: REVIEWING → INCORPORATING → SCORING → CONVERGED|ESCALATED
- Planning estimate: 6-8 working days, fully sequential critical path

## Deterministic Rules Applied

- Phase numbering preserves roadmap's explicit 6-phase structure with contiguous numbering (1-6)
- Task IDs use `T<PP>.<TT>` zero-padded format per appearance order within each phase
- Roadmap Item IDs assigned as `R-001` through `R-051` in appearance order
- Deliverable IDs assigned as `D-0001` through `D-0042` in global task-then-deliverable order
- Checkpoints inserted after every 5 tasks and at end of each phase
- Clarification tasks inserted where roadmap leaves decisions unresolved (none needed -- roadmap is fully specified)
- Effort/Risk computed deterministically from keyword scoring per Sections 5.2.1 and 5.2.2
- Tier classification uses compound phrase overrides, keyword matching, and context boosters per Section 5.3
- Verification routing maps tier to method per Section 4.10
- MCP requirements and sub-agent delegation computed per Sections 5.5 and 5.6
- Multi-file output: 1 index + 6 phase files = 7 files total
- Gates (A-D) from roadmap converted to end-of-phase checkpoints with roadmap exit criteria preserved

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | 1 | Pre-Implementation Verification Checklist |
| R-002 | 1 | Change inventory: Confirm the 4 files to be modified and 1 file to be created |
| R-003 | 1 | Dependency trace: Trace all downstream consumers of the return contract (specifically sc:roadmap and sc:tasklist) |
| R-004 | 1 | Regression checklist: Confirm Phases 0-2 behavior is unchanged and no phase references old Phase 3/4 |
| R-005 | 1 | Sync requirement: Confirm src/superclaude/ changes must be followed by make sync-dev |
| R-006 | 1 | Template Creation |
| R-007 | 1 | Create src/superclaude/examples/release-spec-template.md (FR-017) with frontmatter schema, 12 template sections, sentinel format |
| R-008 | 1 | Validate sentinel format doesn't collide with template content (Open Question 3) |
| R-009 | 1 | Write self-validation check: regex scan for remaining sentinels (SC-003) |
| R-010 | 1 | Mark conditional sections clearly (FR-060.7) — sections only required for specific spec types |
| R-011 | 1 | Gate A: Template file exists, zero sentinel collisions, sections map 1:1, dependency trace complete |
| R-012 | 2 | Phase 2→3 Entry Gate: Phase 2 contract status completed, all blocking checks passed |
| R-013 | 2 | Rewrite Phase 3 in SKILL.md (FR-013) |
| R-014 | 2 | 3a Template instantiation: load template, create working copy at {work_dir}/portify-release-spec.md |
| R-015 | 2 | 3b Content population: map Phase 1 + Phase 2 outputs to template sections per mapping |
| R-016 | 2 | 3c Embedded brainstorm pass (FR-004, FR-005, FR-006): Multi-persona non-interactive analysis with structured output |
| R-017 | 2 | 3d Gap incorporation: actionable findings into spec body, unresolvable to Section 11 |
| R-018 | 2 | Remove all code generation instructions from SKILL.md (FR-013) |
| R-019 | 2 | Preserve refs/code-templates.md as reference-only, ensure no phase loads it (R-006) |
| R-020 | 2 | Add phase timing instrumentation for phase_3_seconds (SC-013) |
| R-021 | 2 | Gate B: Every step_mapping entry produces FR, brainstorm section present, zero sentinels, timing target |
| R-022 | 3 | Rewrite Phase 4 in SKILL.md (FR-014) |
| R-023 | 3 | 4a Focus pass with --focus correctness,architecture (FR-008): Embed sc:spec-panel behavioral patterns inline |
| R-024 | 3 | 4b Focus incorporation (FR-009): CRITICAL address, MAJOR incorporate, MINOR append, additive-only |
| R-025 | 3 | 4c Critique pass with --mode critique (FR-010): Quality scores clarity completeness testability consistency |
| R-026 | 3 | 4d Critique incorporation and scoring (FR-011): Record quality scores, compute overall mean, append panel |
| R-027 | 3 | Convergence Loop: States REVIEWING INCORPORATING SCORING CONVERGED ESCALATED, max 3 iterations, terminal states |
| R-028 | 3 | Remove old Phase 4 instructions: main.py patching, import verification, structural tests, summary writing |
| R-029 | 3 | Add phase timing instrumentation for phase_4_seconds (SC-013) |
| R-030 | 3 | Implement downstream_ready gate: overall >= 7.0 true, else false (Constraint 8, SC-012) |
| R-031 | 3 | Exit Criteria: Focus pass findings, critique scores, no unaddressed CRITICALs, 15-minute target |
| R-032 | 4 | Update return contract (FR-015): Add fields contract_version spec_file panel_report quality_scores convergence_iterations |
| R-033 | 4 | Resume behavior semantics: Phase 3 resume preserves populated spec, Phase 4 resume preserves draft |
| R-034 | 4 | Update --dry-run behavior (FR-016): Execute Phases 0-2 only, emit Phase 0-2 contracts only |
| R-035 | 4 | Remove --skip-integration flag from cli-portify.md (SC-014) |
| R-036 | 4 | Update refs/pipeline-spec.md for Phase 2→3 bridge (D-008) |
| R-037 | 4 | Validate contract failure paths: quality scores 0.0 on failure, downstream_ready false, schema complete |
| R-038 | 4 | Gate C: Contract emitted on success/failure/dry-run, flag rejected, quality formula verified, failure defaults |
| R-039 | 5 | Structural Validation: SC-003 zero sentinels, SC-004 step mapping FR count, SC-005 brainstorm exists |
| R-040 | 5 | Behavioral Validation: SC-006 focus findings, SC-007 quality scores, brainstorm schema, zero-gap path |
| R-041 | 5 | Contract Validation: SC-009 contract all paths, SC-010 quality formula, SC-013 timing, SC-014 flag |
| R-042 | 5 | Boundary Validation: SC-012 threshold 7.0/6.9, SC-008 CRITICALs <=3 iterations, mid-panel failure scores |
| R-043 | 5 | End-to-End Validation: SC-001 full run, SC-002 dry run, SC-011 downstream handoff, convergence loop |
| R-044 | 5 | Validation evidence required: Test output logs, contract snapshots, generated spec sample, panel report |
| R-045 | 6 | Run make sync-dev (Constraint 10) |
| R-046 | 6 | Run make verify-sync to confirm src/ and .claude/ match |
| R-047 | 6 | Update decisions.yaml with architectural decisions from this work (mandatory) |
| R-048 | 6 | Update SKILL.md internal documentation references |
| R-049 | 6 | Verify refs/code-templates.md is preserved but unloaded |
| R-050 | 6 | Mark refs/code-templates.md as inactive reference-only (debate R9 mitigation) |
| R-051 | 6 | Gate D: All changes synced, decisions.yaml updated, quality threshold validated, no CRITICALs |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-002 | Change inventory document listing 4 modified + 1 created files | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0001/evidence.md | XS | Low |
| D-0002 | T01.01 | R-003 | Dependency trace of return contract consumers (sc:roadmap, sc:tasklist) | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0002/evidence.md | XS | Low |
| D-0003 | T01.01 | R-004 | Regression checklist confirming Phases 0-2 unchanged | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0003/evidence.md | XS | Low |
| D-0004 | T01.01 | R-005 | Sync requirement confirmation for make sync-dev | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0004/notes.md | XS | Low |
| D-0005 | T01.02 | R-007 | Release spec template at src/superclaude/examples/release-spec-template.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0005/spec.md | S | Low |
| D-0006 | T01.02 | R-008 | Sentinel collision validation results | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0006/evidence.md | S | Low |
| D-0007 | T01.02 | R-010 | Conditional section markers in template | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0007/evidence.md | S | Low |
| D-0008 | T01.03 | R-009 | Regex-based sentinel self-validation check (SC-003) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0008/spec.md | XS | Low |
| D-0009 | T02.01 | R-013, R-014 | Phase 3 step 3a (template instantiation) in SKILL.md | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0009/spec.md | S | Low |
| D-0010 | T02.01 | R-015 | Phase 3 step 3b (content population) in SKILL.md | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0010/spec.md | S | Low |
| D-0011 | T02.02 | R-016 | Phase 3 step 3c (embedded brainstorm pass) in SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0011/spec.md | M | Low |
| D-0012 | T02.02 | R-017 | Phase 3 step 3d (gap incorporation) in SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0012/notes.md | M | Low |
| D-0013 | T02.03 | R-018 | Code generation instructions removed from SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0013/evidence.md | S | Medium |
| D-0014 | T02.03 | R-019 | refs/code-templates.md preserved as reference-only, no phase loads it | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0014/evidence.md | S | Medium |
| D-0015 | T02.04 | R-020 | Phase 3 timing instrumentation (phase_3_seconds field) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0015/evidence.md | XS | Low |
| D-0016 | T03.01 | R-022, R-023 | Phase 4 step 4a (focus pass) in SKILL.md with expert analysis | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0016/spec.md | M | Low |
| D-0017 | T03.02 | R-024 | Phase 4 step 4b (focus incorporation) in SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0017/spec.md | S | Medium |
| D-0018 | T03.03 | R-025 | Phase 4 step 4c (critique pass) in SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0018/spec.md | S | Low |
| D-0019 | T03.04 | R-026 | Phase 4 step 4d (critique incorporation and scoring) in SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0019/spec.md | S | Low |
| D-0020 | T03.05 | R-027 | Convergence loop implementation with state machine in SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0020/notes.md | S | Low |
| D-0021 | T03.06 | R-028 | Old Phase 4 instructions removed from SKILL.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0021/evidence.md | S | Medium |
| D-0022 | T03.07 | R-029 | Phase 4 timing instrumentation (phase_4_seconds field) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0022/evidence.md | S | Low |
| D-0023 | T03.07 | R-030 | downstream_ready gate logic (overall >= 7.0) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0023/evidence.md | S | Low |
| D-0024 | T04.01 | R-032 | Updated return contract schema with all new fields | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0024/spec.md | L | Medium |
| D-0025 | T04.01 | R-033 | Resume behavior semantics for Phase 3 and Phase 4 | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0025/spec.md | L | Medium |
| D-0026 | T04.02 | R-034 | Updated --dry-run behavior in cli-portify.md | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0026/spec.md | XS | Low |
| D-0027 | T04.03 | R-035 | --skip-integration flag removed from cli-portify.md | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0027/notes.md | XS | Medium |
| D-0028 | T04.04 | R-036 | refs/pipeline-spec.md updated for Phase 2→3 bridge | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0028/spec.md | XS | Low |
| D-0029 | T04.05 | R-037 | Contract failure path validation results | STRICT | Sub-agent (quality-engineer) | TASKLIST_ROOT/artifacts/D-0029/evidence.md | M | Medium |
| D-0030 | T05.01 | R-039 | Structural validation results (SC-003, SC-004, SC-005) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0030/evidence.md | S | Low |
| D-0031 | T05.02 | R-040 | Behavioral validation results (SC-006, SC-007) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0031/evidence.md | S | Low |
| D-0032 | T05.03 | R-041 | Contract validation results (SC-009, SC-010, SC-013, SC-014) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0032/evidence.md | M | Medium |
| D-0033 | T05.04 | R-042 | Boundary validation results (SC-012, SC-008) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0033/evidence.md | S | Medium |
| D-0034 | T05.05 | R-043, R-044 | End-to-end validation results (SC-001, SC-002, SC-011) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0034/evidence.md | M | Medium |
| D-0035 | T05.05 | R-044 | Validation evidence package (logs, contract snapshots, spec sample, panel report) | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0035/evidence.md | M | Medium |
| D-0036 | T06.01 | R-045 | make sync-dev execution confirmation | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0036/evidence.md | XS | Low |
| D-0037 | T06.01 | R-046 | make verify-sync passing confirmation | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0037/evidence.md | XS | Low |
| D-0038 | T06.02 | R-047 | Updated decisions.yaml with architectural decisions | STANDARD | Direct test execution | TASKLIST_ROOT/artifacts/D-0038/spec.md | S | Low |
| D-0039 | T06.03 | R-048 | Updated SKILL.md documentation references | LIGHT | Quick sanity check | TASKLIST_ROOT/artifacts/D-0039/notes.md | XS | Low |
| D-0040 | T06.04 | R-049 | refs/code-templates.md verified preserved and unloaded | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0040/evidence.md | XS | Low |
| D-0041 | T06.04 | R-050 | refs/code-templates.md marked as inactive reference-only | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0041/evidence.md | XS | Low |
| D-0042 | T06.04 | R-050 | Verification that no workflow phase loads refs/code-templates.md | EXEMPT | Skip verification | TASKLIST_ROOT/artifacts/D-0042/evidence.md | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001, D-0002, D-0003, D-0004 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0001/evidence.md, TASKLIST_ROOT/artifacts/D-0002/evidence.md, TASKLIST_ROOT/artifacts/D-0003/evidence.md, TASKLIST_ROOT/artifacts/D-0004/notes.md |
| R-002 | T01.01 | D-0001 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0001/evidence.md |
| R-003 | T01.01 | D-0002 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0002/evidence.md |
| R-004 | T01.01 | D-0003 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0003/evidence.md |
| R-005 | T01.01 | D-0004 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0004/notes.md |
| R-006 | T01.02 | D-0005, D-0006, D-0007 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0005/spec.md, TASKLIST_ROOT/artifacts/D-0006/evidence.md, TASKLIST_ROOT/artifacts/D-0007/evidence.md |
| R-007 | T01.02 | D-0005 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0005/spec.md |
| R-008 | T01.02 | D-0006 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0006/evidence.md |
| R-010 | T01.02 | D-0007 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0007/evidence.md |
| R-009 | T01.03 | D-0008 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0008/spec.md |
| R-011 | Checkpoint CP-P01-END | — | EXEMPT | 80% | TASKLIST_ROOT/checkpoints/CP-P01-END.md |
| R-013, R-014 | T02.01 | D-0009 | STRICT | 85% | TASKLIST_ROOT/artifacts/D-0009/spec.md |
| R-015 | T02.01 | D-0010 | STRICT | 85% | TASKLIST_ROOT/artifacts/D-0010/spec.md |
| R-016 | T02.02 | D-0011 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0011/spec.md |
| R-017 | T02.02 | D-0012 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0012/notes.md |
| R-018 | T02.03 | D-0013 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0013/evidence.md |
| R-019 | T02.03 | D-0014 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0014/evidence.md |
| R-020 | T02.04 | D-0015 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0015/evidence.md |
| R-022, R-023 | T03.01 | D-0016 | STRICT | 80% | TASKLIST_ROOT/artifacts/D-0016/spec.md |
| R-024 | T03.02 | D-0017 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0017/spec.md |
| R-025 | T03.03 | D-0018 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0018/spec.md |
| R-026 | T03.04 | D-0019 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0019/spec.md |
| R-027 | T03.05 | D-0020 | STANDARD | 70% | TASKLIST_ROOT/artifacts/D-0020/notes.md |
| R-028 | T03.06 | D-0021 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0021/evidence.md |
| R-029 | T03.07 | D-0022 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0022/evidence.md |
| R-030 | T03.07 | D-0023 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0023/evidence.md |
| R-032 | T04.01 | D-0024 | STRICT | 85% | TASKLIST_ROOT/artifacts/D-0024/spec.md |
| R-033 | T04.01 | D-0025 | STRICT | 85% | TASKLIST_ROOT/artifacts/D-0025/spec.md |
| R-034 | T04.02 | D-0026 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0026/spec.md |
| R-035 | T04.03 | D-0027 | STRICT | 80% | TASKLIST_ROOT/artifacts/D-0027/notes.md |
| R-036 | T04.04 | D-0028 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0028/spec.md |
| R-037 | T04.05 | D-0029 | STRICT | 70% | TASKLIST_ROOT/artifacts/D-0029/evidence.md |
| R-039 | T05.01 | D-0030 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0030/evidence.md |
| R-040 | T05.02 | D-0031 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0031/evidence.md |
| R-041 | T05.03 | D-0032 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0032/evidence.md |
| R-042 | T05.04 | D-0033 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0033/evidence.md |
| R-043, R-044 | T05.05 | D-0034, D-0035 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0034/evidence.md, TASKLIST_ROOT/artifacts/D-0035/evidence.md |
| R-045 | T06.01 | D-0036 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0036/evidence.md |
| R-046 | T06.01 | D-0037 | EXEMPT | 85% | TASKLIST_ROOT/artifacts/D-0037/evidence.md |
| R-047 | T06.02 | D-0038 | STANDARD | 75% | TASKLIST_ROOT/artifacts/D-0038/spec.md |
| R-048 | T06.03 | D-0039 | LIGHT | 75% | TASKLIST_ROOT/artifacts/D-0039/notes.md |
| R-049 | T06.04 | D-0040 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0040/evidence.md |
| R-050 | T06.04 | D-0041, D-0042 | EXEMPT | 80% | TASKLIST_ROOT/artifacts/D-0041/evidence.md, TASKLIST_ROOT/artifacts/D-0042/evidence.md |
| R-051 | Checkpoint CP-P06-END | — | EXEMPT | 80% | TASKLIST_ROOT/checkpoints/CP-P06-END.md |

## Execution Log Template

**Intended Path:** TASKLIST_ROOT/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|

## Checkpoint Report Template

**Template:**

```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md
**Scope:** <tasks covered>
## Status
Overall: Pass | Fail | TBD
## Verification Results
- <bullet 1>
- <bullet 2>
- <bullet 3>
## Exit Criteria Assessment
- <bullet 1>
- <bullet 2>
- <bullet 3>
## Issues & Follow-ups
- <list blocking issues with T<PP>.<TT> and D-#### references>
## Evidence
- <bullet list of intended evidence paths under TASKLIST_ROOT/evidence/>
```

## Feedback Collection Template

**Intended Path:** TASKLIST_ROOT/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|

## Generation Notes

- TASKLIST_ROOT derived from command-provided output directory (`.dev/releases/backlog/v2.23-cli-portify-v3/`) since roadmap text contained no `.dev/releases/current/<segment>/` substring and no `v<digits>(.<digits>)+` version token
- Roadmap gates (A, B, C, D) converted to end-of-phase checkpoints preserving original exit criteria
- Phase 2→3 entry gate (R-012) incorporated as dependency on T01.01-T01.03 rather than separate task
- No Clarification Tasks needed -- roadmap is fully specified with all decisions resolved
