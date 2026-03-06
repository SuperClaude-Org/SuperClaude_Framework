# TASKLIST INDEX — /sc:tasklist Command + Skill v1.0

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | `/sc:tasklist` Command + Skill v1.0 |
| Generator Version | Roadmap→Tasklist Generator v3.0 |
| Generated | 2026-03-05T03:00:00Z |
| TASKLIST_ROOT | `.dev/releases/current/v2.07-tasklist-v1/tasklist/` |
| Total Phases | 4 |
| Total Tasks | 39 |
| Total Deliverables | 39 |
| Complexity Class | MEDIUM |
| Primary Persona | architect |
| Consulting Personas | analyzer, scribe |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | `TASKLIST_ROOT/tasklist-index.md` |
| Phase 1 Tasklist | `TASKLIST_ROOT/phase-1-tasklist.md` |
| Phase 2 Tasklist | `TASKLIST_ROOT/phase-2-tasklist.md` |
| Phase 3 Tasklist | `TASKLIST_ROOT/phase-3-tasklist.md` |
| Phase 4 Tasklist | `TASKLIST_ROOT/phase-4-tasklist.md` |
| Execution Log | `TASKLIST_ROOT/execution-log.md` |
| Checkpoint Reports | `TASKLIST_ROOT/checkpoints/` |
| Evidence Directory | `TASKLIST_ROOT/evidence/` |
| Artifacts Directory | `TASKLIST_ROOT/artifacts/` |
| Feedback Log | `TASKLIST_ROOT/feedback-log.md` |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation & Architecture Setup | T01.01–T01.04 | STANDARD: 3, LIGHT: 1 |
| 2 | phase-2-tasklist.md | Command & Skill Implementation | T02.01–T02.16 | STRICT: 4, STANDARD: 11, LIGHT: 1 |
| 3 | phase-3-tasklist.md | Integration & Tooling | T03.01–T03.09 | STRICT: 2, STANDARD: 6, LIGHT: 1 |
| 4 | phase-4-tasklist.md | Validation & Acceptance | T04.01–T04.10 | STRICT: 3, STANDARD: 5, EXEMPT: 2 |

## Source Snapshot

- Packages existing Tasklist Generator v3.0 as a proper SuperClaude command/skill pair
- Pure packaging exercise with exact functional parity — no new features
- 5 work milestones (M1–M5) and 2 validation checkpoints (V1, V2)
- M2 (Command Layer) and M3 (Skill Layer) are parallelizable after M1 completes
- Primary risk is algorithm drift during v3.0-to-SKILL.md reformatting (RISK-001)
- Complexity score 0.571 (MEDIUM), 39 total deliverables across 7 milestones

## Deterministic Rules Applied

- Phase bucketing: Milestones mapped to 4 sequential phases by dependency graph (M1 → Phase 1; M2+M3 → Phase 2; V1+M4 → Phase 3; M5+V2 → Phase 4)
- Phase numbering: Sequential 1–4 with no gaps per §4.3
- Task IDs: `T<PP>.<TT>` zero-padded format per §4.5
- Checkpoint cadence: After every 5 tasks within a phase + end-of-phase checkpoint per §4.8
- Clarification tasks: Inserted where roadmap identifies undefined criteria (RISK-008: pre-write quality gate definitions)
- Deliverable registry: Global `D-####` IDs in task order per §5.1
- Effort/risk mappings: Computed deterministically from roadmap item text per §5.2
- Tier classification: `/sc:task-unified` algorithm per §5.3 with compound phrase overrides
- Verification routing: Tier-based method assignment per §4.10
- MCP requirements: Per-tier tool dependencies per §5.5
- Traceability matrix: R-### → T<PP>.<TT> → D-#### linkage per §5.7
- Multi-file output: N+1 files (1 index + 4 phase files) per §3.3

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (≤ 20 words) |
|---|---|---|
| R-001 | M1 | Create directory `src/superclaude/skills/sc-tasklist-protocol/` with subdirs `rules/` and `templates/` |
| R-002 | M1 | Create empty `src/superclaude/skills/sc-tasklist-protocol/__init__.py` |
| R-003 | M1 | Create placeholder `src/superclaude/commands/tasklist.md` with valid YAML frontmatter only |
| R-004 | M1 | Create placeholder `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` with valid frontmatter only |
| R-005 | M2 | Implement YAML frontmatter per §5.1: name, description, category, complexity, allowed-tools, mcp-servers, personas, version |
| R-006 | M2 | Implement all 8 required sections per §5.3 |
| R-007 | M2 | Implement argument spec per §5.2: required `<roadmap-path>`, optional `--spec`, optional `--output` |
| R-008 | M2 | Implement input validation per §5.4: 4 validation checks + 2-field error format |
| R-009 | M2 | Implement `## Activation` section per §5.5: mandatory `Skill sc:tasklist-protocol` invocation |
| R-010 | M2 | Implement `## Boundaries` per §5.6: Will/Will-Not contract |
| R-011 | M2 | Emit STRICT tier classification header before skill invocation per §4.3 |
| R-012 | M2 | Report generated file paths on completion; implement TASKLIST_ROOT auto-derivation per §3.1 |
| R-013 | M3 | Implement SKILL.md frontmatter per §6.1 |
| R-014 | M3 | Reformat v3.0 §0–§9 + Appendix into SKILL.md body per §6.2 structural mapping |
| R-015 | M3 | Add stage completion reporting contract (§4.3) to SKILL.md |
| R-016 | M3 | Extract `rules/tier-classification.md` from SKILL.md §5.3 + Appendix |
| R-017 | M3 | Extract `rules/file-emission-rules.md` from SKILL.md §3.3 |
| R-018 | M3 | Extract `templates/index-template.md` from SKILL.md §6A |
| R-019 | M3 | Extract `templates/phase-template.md` from SKILL.md §6B |
| R-020 | M3 | Document Tool Usage (§6.4) and MCP Usage (§6.5) sections in SKILL.md |
| R-021 | V1 | Verify command `## Activation` correctly references `sc:tasklist-protocol` and skill directory exists |
| R-022 | V1 | Verify bidirectional pairing: skill dir exists → command file exists |
| R-023 | V1 | Verify SKILL.md frontmatter passes lint checks #8 and #9 |
| R-024 | M4 | `make sync-dev` copies command and skill to `.claude/` directories |
| R-025 | M4 | `make verify-sync` confirms source and `.claude/` copies are identical |
| R-026 | M4 | `make lint-architecture` passes with zero errors for the new pair |
| R-027 | M4 | `superclaude install` installs `tasklist.md` to `~/.claude/commands/sc/tasklist.md` |
| R-028 | M4 | `superclaude install` does NOT install `sc-tasklist-protocol/` to `~/.claude/skills/` |
| R-029 | M4 | Verify source files unmodified after all work completes |
| R-030 | M5 | Manual test: `/sc:tasklist @<roadmap>` produces valid output bundle |
| R-031 | M5 | Sprint compatibility test: `superclaude sprint run <generated-index>` discovers all phase files |
| R-032 | M5 | Functional parity test: diff v3.0 generator output vs. `/sc:tasklist` output |
| R-033 | M5 | Leanness check: phase files contain no registries, traceability matrices, or embedded templates |
| R-034 | M5 | Task description quality: every task description is standalone per §7.N |
| R-035 | V2 | SC-001 through SC-005 verified: discoverability, output format, lint |
| R-036 | V2 | SC-006 through SC-009 verified: Sprint compatibility, lean output, stage order, v3.0 parity |
| R-037 | V2 | SC-010 through SC-012 verified: quality gates, atomic output |
| R-038 | V2 | SC-013 verified: task descriptions standalone |
| R-039 | V2 | Verify manual TasklistGenPrompt.md workflow is superseded |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Directory tree `sc-tasklist-protocol/` with `rules/` and `templates/` subdirs | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0001/evidence.md` | XS | Low |
| D-0002 | T01.02 | R-002 | Empty `__init__.py` file | LIGHT | Quick sanity check | `TASKLIST_ROOT/artifacts/D-0002/evidence.md` | XS | Low |
| D-0003 | T01.03 | R-003 | Placeholder `tasklist.md` with valid YAML frontmatter | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0003/evidence.md` | XS | Low |
| D-0004 | T01.04 | R-004 | Placeholder `SKILL.md` with valid YAML frontmatter | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0004/evidence.md` | XS | Low |
| D-0005 | T02.01 | R-005 | Command frontmatter with all 8 fields matching spec §5.1 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0005/spec.md` | S | Low |
| D-0006 | T02.02 | R-006 | All 8 required sections with correct headings per §5.3 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0006/spec.md` | M | Low |
| D-0007 | T02.03 | R-007 | Arguments table matching spec §5.2 with `@file` and explicit path support | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0007/spec.md` | S | Low |
| D-0008 | T02.04 | R-008 | Input validation with 4 checks, 2-field error format, exit-without-invoke behavior | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0008/spec.md` | S | Low |
| D-0009 | T02.05 | R-009 | Activation section with exact `Skill sc:tasklist-protocol` invocation | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0009/spec.md` | XS | Low |
| D-0010 | T02.06 | R-010 | Boundaries section with Will/Will-Not lists matching spec §5.6 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0010/spec.md` | XS | Low |
| D-0011 | T02.07 | R-011 | STRICT tier classification header emitted before skill invocation | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0011/spec.md` | S | Low |
| D-0012 | T02.08 | R-012 | File path reporting on completion; TASKLIST_ROOT derivation logic per §3.1 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0012/spec.md` | M | Medium |
| D-0013 | T02.09 | R-013 | SKILL.md frontmatter with all fields per §6.1, `name:` ending in `-protocol` | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0013/spec.md` | S | Low |
| D-0014 | T02.10 | R-014 | v3.0 §0–§9 + Appendix content reformatted into SKILL.md body per §6.2 mapping | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0014/spec.md` | L | High |
| D-0015 | T02.11 | R-015 | 6-stage completion reporting contract with validation criteria and TodoWrite integration | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0015/spec.md` | M | Medium |
| D-0016 | T02.12 | R-016 | `rules/tier-classification.md` extracted from §5.3 + Appendix | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0016/spec.md` | S | Low |
| D-0017 | T02.13 | R-017 | `rules/file-emission-rules.md` extracted from §3.3 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0017/spec.md` | S | Low |
| D-0018 | T02.14 | R-018 | `templates/index-template.md` extracted from §6A | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0018/spec.md` | S | Low |
| D-0019 | T02.15 | R-019 | `templates/phase-template.md` extracted from §6B | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0019/spec.md` | S | Low |
| D-0020 | T02.16 | R-020 | Tool Usage and MCP Usage sections in SKILL.md per §6.4 and §6.5 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0020/spec.md` | S | Low |
| D-0021 | T03.01 | R-021 | Lint check #1 passes: `## Activation` → `sc-tasklist-protocol/` exists | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0021/evidence.md` | XS | Low |
| D-0022 | T03.02 | R-022 | Lint check #2 passes: bidirectional pairing verified | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0022/evidence.md` | XS | Low |
| D-0023 | T03.03 | R-023 | SKILL.md frontmatter passes lint checks #8 and #9 | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0023/evidence.md` | XS | Low |
| D-0024 | T03.04 | R-024 | `tasklist.md` exists in `.claude/commands/sc/` and `sc-tasklist-protocol/` exists in `.claude/skills/` after sync | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0024/evidence.md` | S | Low |
| D-0025 | T03.05 | R-025 | No diff between `src/superclaude/` and `.claude/` copies | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0025/evidence.md` | XS | Low |
| D-0026 | T03.06 | R-026 | All 6 lint checks pass with zero errors | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0026/evidence.md` | S | Medium |
| D-0027 | T03.07 | R-027 | `tasklist.md` exists at `~/.claude/commands/sc/tasklist.md` after install | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0027/evidence.md` | S | Low |
| D-0028 | T03.08 | R-028 | `sc-tasklist-protocol/` absent from `~/.claude/skills/` after install | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0028/evidence.md` | S | Medium |
| D-0029 | T03.09 | R-029 | `git diff` confirms v3.0 source files unchanged | LIGHT | Quick sanity check | `TASKLIST_ROOT/artifacts/D-0029/evidence.md` | XS | Low |
| D-0030 | T04.01 | R-030 | Valid `tasklist-index.md` + `phase-N-tasklist.md` files produced from test roadmap | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0030/evidence.md` | M | Medium |
| D-0031 | T04.02 | R-031 | Sprint CLI finds and lists all phase files from generated index | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0031/evidence.md` | M | High |
| D-0032 | T04.03 | R-032 | Output structurally identical to v3.0 generator; any delta is non-functional formatting only | STRICT | Sub-agent (quality-engineer) | `TASKLIST_ROOT/artifacts/D-0032/evidence.md` | M | High |
| D-0033 | T04.04 | R-033 | Phase files contain only task content per Sprint format — no registries, matrices, or templates | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0033/evidence.md` | S | Low |
| D-0034 | T04.05 | R-034 | 100% of tasks pass §7.N standalone description criteria | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0034/evidence.md` | S | Low |
| D-0035 | T04.06 | R-035 | SC-001 through SC-005 all pass | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0035/evidence.md` | S | Low |
| D-0036 | T04.07 | R-036 | SC-006 through SC-009 all pass | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0036/evidence.md` | S | Low |
| D-0037 | T04.08 | R-037 | SC-010 through SC-012 all pass: pre-write gates enforced, no files on failure | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0037/evidence.md` | S | Low |
| D-0038 | T04.09 | R-038 | SC-013 passes: every task description standalone | STANDARD | Direct test execution | `TASKLIST_ROOT/artifacts/D-0038/evidence.md` | S | Low |
| D-0039 | T04.10 | R-039 | `/sc:tasklist` provides equivalent functionality; internal docs reference `/sc:tasklist` | EXEMPT | Skip verification | `TASKLIST_ROOT/artifacts/D-0039/evidence.md` | XS | Low |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0001/` |
| R-002 | T01.02 | D-0002 | LIGHT | [████████░░] 85% | `TASKLIST_ROOT/artifacts/D-0002/` |
| R-003 | T01.03 | D-0003 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0003/` |
| R-004 | T01.04 | D-0004 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0004/` |
| R-005 | T02.01 | D-0005 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0005/` |
| R-006 | T02.02 | D-0006 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0006/` |
| R-007 | T02.03 | D-0007 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0007/` |
| R-008 | T02.04 | D-0008 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0008/` |
| R-009 | T02.05 | D-0009 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0009/` |
| R-010 | T02.06 | D-0010 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0010/` |
| R-011 | T02.07 | D-0011 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0011/` |
| R-012 | T02.08 | D-0012 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0012/` |
| R-013 | T02.09 | D-0013 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0013/` |
| R-014 | T02.10 | D-0014 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0014/` |
| R-015 | T02.11 | D-0015 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0015/` |
| R-016 | T02.12 | D-0016 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0016/` |
| R-017 | T02.13 | D-0017 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0017/` |
| R-018 | T02.14 | D-0018 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0018/` |
| R-019 | T02.15 | D-0019 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0019/` |
| R-020 | T02.16 | D-0020 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0020/` |
| R-021 | T03.01 | D-0021 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0021/` |
| R-022 | T03.02 | D-0022 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0022/` |
| R-023 | T03.03 | D-0023 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0023/` |
| R-024 | T03.04 | D-0024 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0024/` |
| R-025 | T03.05 | D-0025 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0025/` |
| R-026 | T03.06 | D-0026 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0026/` |
| R-027 | T03.07 | D-0027 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0027/` |
| R-028 | T03.08 | D-0028 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0028/` |
| R-029 | T03.09 | D-0029 | LIGHT | [████████░░] 85% | `TASKLIST_ROOT/artifacts/D-0029/` |
| R-030 | T04.01 | D-0030 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0030/` |
| R-031 | T04.02 | D-0031 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0031/` |
| R-032 | T04.03 | D-0032 | STRICT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0032/` |
| R-033 | T04.04 | D-0033 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0033/` |
| R-034 | T04.05 | D-0034 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0034/` |
| R-035 | T04.06 | D-0035 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0035/` |
| R-036 | T04.07 | D-0036 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0036/` |
| R-037 | T04.08 | D-0037 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0037/` |
| R-038 | T04.09 | D-0038 | STANDARD | [████████░░] 80% | `TASKLIST_ROOT/artifacts/D-0038/` |
| R-039 | T04.10 | D-0039 | EXEMPT | [█████████░] 90% | `TASKLIST_ROOT/artifacts/D-0039/` |

## Execution Log Template

**Intended Path:** `TASKLIST_ROOT/execution-log.md`

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (≤ 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|

## Checkpoint Report Template

For each checkpoint created under Section 4.8, execution must produce one report using this template (do not fabricate contents).

**Template:**
- `# Checkpoint Report — <Checkpoint Title>`
- `**Checkpoint Report Path:** TASKLIST_ROOT/checkpoints/<deterministic-name>.md`
- `**Scope:** <tasks covered>`
- `## Status`
  - `Overall: Pass | Fail | TBD`
- `## Verification Results` (exactly 3 bullets)
- `## Exit Criteria Assessment` (exactly 3 bullets)
- `## Issues & Follow-ups`
  - List blocking issues; reference `T<PP>.<TT>` and `D-####`
- `## Evidence`
  - Bullet list of intended evidence paths under `TASKLIST_ROOT/evidence/`

## Feedback Collection Template

**Intended Path:** `TASKLIST_ROOT/feedback-log.md`

| Task ID | Original Tier | Override Tier | Override Reason (≤ 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|

**Field definitions:**
- `Override Tier`: Leave blank if no override; else the user-selected tier
- `Override Reason`: Brief justification
- `Completion Status`: `clean | minor-issues | major-issues | failed`
- `Quality Signal`: `pass | partial | rework-needed`
- `Time Variance`: `under-estimate | on-target | over-estimate`

## Generation Notes

- Phase bucketing: 7 roadmap milestones (M1–M5, V1, V2) mapped to 4 phases by dependency graph collapse
- M2 (Command Layer) and M3 (Skill Layer) merged into Phase 2 since both depend only on M1 and are parallelizable
- V1 (Integration Checkpoint) and M4 (Tooling) merged into Phase 3 since V1 gates M4
- M5 (Output Validation) and V2 (Final Acceptance) merged into Phase 4 as the validation sweep
- TASKLIST_ROOT derived from roadmap `spec_source` path containing `.dev/releases/current/v2.07-tasklist-v1/`
