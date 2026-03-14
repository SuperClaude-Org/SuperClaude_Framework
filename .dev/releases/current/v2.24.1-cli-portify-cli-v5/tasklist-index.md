# TASKLIST INDEX -- v2.24.1 CLI Portify v5 Target Resolution

## Metadata & Artifact Paths

| Field | Value |
|---|---|
| Sprint Name | v2.24.1 CLI Portify v5 Target Resolution |
| Generator Version | Roadmap->Tasklist Generator v4.0 |
| Generated | 2026-03-13 |
| TASKLIST_ROOT | .dev/releases/current/v2.24.1-cli-portify-cli-v5/ |
| Total Phases | 3 |
| Total Tasks | 22 |
| Total Deliverables | 38 |
| Complexity Class | MEDIUM |
| Primary Persona | backend |
| Consulting Personas | architect, analyzer, qa |

**Artifact Paths**

| Asset | Path |
|---|---|
| This file | .dev/releases/current/v2.24.1-cli-portify-cli-v5/tasklist-index.md |
| Phase 1 Tasklist | .dev/releases/current/v2.24.1-cli-portify-cli-v5/phase-1-tasklist.md |
| Phase 2 Tasklist | .dev/releases/current/v2.24.1-cli-portify-cli-v5/phase-2-tasklist.md |
| Phase 3 Tasklist | .dev/releases/current/v2.24.1-cli-portify-cli-v5/phase-3-tasklist.md |
| Execution Log | .dev/releases/current/v2.24.1-cli-portify-cli-v5/execution-log.md |
| Checkpoint Reports | .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/ |
| Evidence Directory | .dev/releases/current/v2.24.1-cli-portify-cli-v5/evidence/ |
| Artifacts Directory | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/ |
| Validation Reports | .dev/releases/current/v2.24.1-cli-portify-cli-v5/validation/ |
| Feedback Log | .dev/releases/current/v2.24.1-cli-portify-cli-v5/feedback-log.md |

## Phase Files

| Phase | File | Phase Name | Task IDs | Tier Distribution |
|---|---|---|---|---|
| 1 | phase-1-tasklist.md | Foundation -- Pre-work, Models & Resolution Core | T01.01-T01.09 | STRICT: 5, STANDARD: 3, EXEMPT: 1 |
| 2 | phase-2-tasklist.md | Integration -- Discovery, Process, CLI | T02.01-T02.06 | STRICT: 4, STANDARD: 2 |
| 3 | phase-3-tasklist.md | Validation, Artifacts & Compatibility Proof | T03.01-T03.07 | STRICT: 3, STANDARD: 3, EXEMPT: 1 |

## Source Snapshot

- Extends CLI Portify pipeline with unified target resolution system replacing single skill-directory input with 6 input forms
- Core addition is `resolution.py` (~350-450 lines) plus additive modifications to 6 existing modules
- Architecture constrained to synchronous, backward-compatible changes with zero modifications to `pipeline/` or `sprint/` base modules
- 3 functional requirements with 18 acceptance-criteria bullets, 5 non-functional requirements
- 4 domains: resolution, discovery, CLI, validation; ~37 new tests
- 3 phases across 3 sessions, 19-28 hours estimated

## Deterministic Rules Applied

- Phase buckets derived from explicit Phase 1/2/3 labels in roadmap; milestones mapped to tasks within phases
- Task IDs assigned as T<PP>.<TT> zero-padded, appearance order preserved within phases
- Checkpoint cadence: every 5 tasks plus mandatory end-of-phase checkpoint
- Clarification tasks inserted when information is missing (none needed for this roadmap)
- Deliverable IDs assigned as D-0001 through D-0038 in global appearance order
- Effort computed from text length, split status, domain keywords, and dependency words
- Risk computed from security, migration, auth, performance, and cross-cutting keywords
- Tier classification uses keyword matching with context boosters for multi-file and model/schema paths
- Verification routing: STRICT -> sub-agent, STANDARD -> direct test, LIGHT -> sanity check, EXEMPT -> skip
- MCP requirements assigned per tier (STRICT requires Sequential + Serena)
- Traceability matrix links R-### to T<PP>.<TT> to D-#### with tier and confidence
- Multi-file output: 1 index + 3 phase files

## Roadmap Item Registry

| Roadmap Item ID | Phase Bucket | Original Text (<= 20 words) |
|---|---|---|
| R-001 | Phase 1 | Change map: Enumerate impacted files -- models.py, new resolution.py, discover_components.py, process.py, cli.py, config.py, validate_config.py, tests |
| R-002 | Phase 1 | Compatibility checklist: Explicit confirmation of constraints -- no pipeline/sprint edits, no async code, existing skill-directory behavior unchanged |
| R-003 | Phase 1 | Test matrix outline: Catalog existing tests and identify coverage gaps for new resolution paths |
| R-004 | Phase 1 | Define TargetInputType enum with the 5 spec-defined values: COMMAND_NAME, COMMAND_PATH, SKILL_DIR, SKILL_NAME, SKILL_FILE |
| R-005 | Phase 1 | Define ResolvedTarget dataclass with all spec-required fields: input_form, input_type, command_path, skill_dir, project_root, commands_dir, skills_dir, agents_dir |
| R-006 | Phase 1 | Define CommandEntry (Tier 0), SkillEntry (Tier 1), AgentEntry (Tier 2) dataclasses |
| R-007 | Phase 1 | Define ComponentTree with command, skill, agents fields plus component_count, total_lines, all_source_dirs computed properties |
| R-008 | Phase 1 | Extend PortifyConfig with the spec-required fields: target_input, target_type, command_path, commands_dir, skills_dir, agents_dir, project_root |
| R-009 | Phase 1 | Augment derive_cli_name() to prefer the resolved command name when available, while retaining backward-compatible fallback |
| R-010 | Phase 1 | Implement to_flat_inventory() backward-compatible ComponentInventory conversion (Path to str at boundary) |
| R-011 | Phase 1 | Implement to_manifest_markdown() human-readable Markdown output |
| R-012 | Phase 1 | Add error code constants: ERR_TARGET_NOT_FOUND, ERR_AMBIGUOUS_TARGET, ERR_BROKEN_ACTIVATION, WARN_MISSING_AGENTS |
| R-013 | Phase 1 | Validation gate: Unit tests for all dataclass construction, to_flat_inventory() round-trip, error code values |
| R-014 | Phase 1 | Implement resolve_target(target, ...) with time.monotonic() timing (FR-PORTIFY-WORKFLOW.1, NFR-001) |
| R-015 | Phase 1 | Implement input classification: detect which of 6 forms the input matches |
| R-016 | Phase 1 | Implement sc: prefix stripping with empty-after-strip guard -> ERR_TARGET_NOT_FOUND |
| R-017 | Phase 1 | Implement empty/whitespace/None guard -> ERR_TARGET_NOT_FOUND |
| R-018 | Phase 1 | Implement ambiguity detection -> ERR_AMBIGUOUS_TARGET with command-first policy |
| R-019 | Phase 1 | Implement command -> skill link via Activation parsing with Skill sc:name-protocol pattern |
| R-020 | Phase 1 | Implement skill -> command backward-resolution via sc-/-protocol stripping heuristic |
| R-021 | Phase 1 | Handle edge cases: standalone command, standalone skill, multi-skill commands (primary only, secondaries warned) |
| R-022 | Phase 1 | Tests for all 6 input forms, all error codes, edge cases. Resolution completes <1s |
| R-023 | Phase 2 | Implement agent extraction from SKILL.md using 6 spec-defined AGENT_PATTERNS |
| R-024 | Phase 2 | Build ComponentTree from resolved target |
| R-025 | Phase 2 | Handle missing agents: found=False, emit warnings, continue |
| R-026 | Phase 2 | Implement --include-agent deduplication with referenced_in=cli-override precedence |
| R-027 | Phase 2 | Add additional_dirs parameter to PortifyProcess |
| R-028 | Phase 2 | Build --add-dir args from ComponentTree.all_source_dirs with deduplication |
| R-029 | Phase 2 | Implement directory cap at 10 with two-tier consolidation |
| R-030 | Phase 2 | Record consolidation decisions in resolution_log |
| R-031 | Phase 2 | Verify additional_dirs=None preserves exact v2.24 behavior (SC-11) |
| R-032 | Phase 2 | Change CLI argument from WORKFLOW_PATH to TARGET |
| R-033 | Phase 2 | Add --commands-dir, --skills-dir, --agents-dir override options |
| R-034 | Phase 2 | Add --include-agent option with empty-string filtering |
| R-035 | Phase 2 | Add --save-manifest option |
| R-036 | Phase 2 | Extend load_portify_config() with new parameter passthrough |
| R-037 | Phase 2 | Extend ValidateConfigResult with command_path, skill_dir, target_type, agent_count, warnings fields |
| R-038 | Phase 3 | Add check 5: command -> skill link validity |
| R-039 | Phase 3 | Add check 6: referenced agent existence |
| R-040 | Phase 3 | Extend to_dict() with all new fields including warnings, command_path, skill_dir, target_type, agent_count |
| R-041 | Phase 3 | Enrich component-inventory.md with Command section, Agents table, Cross-Tier Data Flow, Resolution Log |
| R-042 | Phase 3 | Stream A -- Unit Validation: Resolver tests for all 6 input forms, model conversion, regex extraction, directory consolidation |
| R-043 | Phase 3 | Stream B -- Integration Validation: CLI invocation, validation result shape, manifest/inventory artifacts, process invocation |
| R-044 | Phase 3 | Stream C -- Regression Validation: Existing suite unchanged, old skill-directory flows match, no pipeline/sprint changes |

## Deliverable Registry

| Deliverable ID | Task ID | Roadmap Item ID(s) | Deliverable (short) | Tier | Verification | Intended Artifact Paths | Effort | Risk |
|---:|---:|---:|---|---|---|---|---|---|
| D-0001 | T01.01 | R-001 | Change map listing all impacted files | EXEMPT | Skip verification | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0001/spec.md | XS | Low |
| D-0002 | T01.01 | R-002 | Compatibility checklist confirming constraints | EXEMPT | Skip verification | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0002/spec.md | XS | Low |
| D-0003 | T01.01 | R-003 | Test matrix outline with coverage gaps | EXEMPT | Skip verification | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0003/spec.md | XS | Low |
| D-0004 | T01.02 | R-004 | TargetInputType enum in models.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0004/evidence.md | S | Low |
| D-0005 | T01.02 | R-005 | ResolvedTarget dataclass in models.py | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0005/evidence.md | S | Low |
| D-0006 | T01.03 | R-006 | CommandEntry, SkillEntry, AgentEntry dataclasses | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0006/evidence.md | S | Low |
| D-0007 | T01.03 | R-007 | ComponentTree with computed properties | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0007/evidence.md | S | Low |
| D-0008 | T01.04 | R-008 | Extended PortifyConfig with new fields | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0008/evidence.md | M | Medium |
| D-0009 | T01.04 | R-009 | Updated derive_cli_name() with backward compat | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0009/evidence.md | M | Medium |
| D-0010 | T01.05 | R-010 | to_flat_inventory() Path-to-str conversion | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0010/evidence.md | S | Medium |
| D-0011 | T01.05 | R-011 | to_manifest_markdown() output function | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0011/evidence.md | S | Medium |
| D-0012 | T01.05 | R-012 | Error code constants module-level | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0012/evidence.md | S | Medium |
| D-0013 | T01.06 | R-013 | Unit tests for dataclass construction and round-trip | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0013/evidence.md | S | Low |
| D-0014 | T01.07 | R-014, R-015 | resolve_target() function with input classification | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0014/evidence.md | M | Medium |
| D-0015 | T01.07 | R-016, R-017 | Input guards (sc: prefix strip, empty/whitespace/None) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0015/evidence.md | M | Medium |
| D-0016 | T01.08 | R-018 | Ambiguity detection with command-first policy | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0016/evidence.md | M | Medium |
| D-0017 | T01.08 | R-019 | Command-to-skill link via Activation parsing | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0017/evidence.md | M | Medium |
| D-0018 | T01.08 | R-020 | Skill-to-command backward resolution heuristic | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0018/evidence.md | M | Medium |
| D-0019 | T01.09 | R-021 | Edge case handling (standalone, multi-skill) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0019/evidence.md | S | Medium |
| D-0020 | T01.09 | R-022 | Resolution tests for all 6 forms + error codes + timing | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0020/evidence.md | S | Medium |
| D-0021 | T02.01 | R-023 | Agent extraction with 6 AGENT_PATTERNS | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0021/evidence.md | M | Medium |
| D-0022 | T02.01 | R-024 | ComponentTree builder from resolved target | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0022/evidence.md | M | Medium |
| D-0023 | T02.02 | R-025 | Missing agent warning handler (found=False, non-fatal) | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0023/evidence.md | S | Low |
| D-0024 | T02.02 | R-026 | --include-agent dedup with cli-override precedence | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0024/evidence.md | S | Low |
| D-0025 | T02.03 | R-027, R-028 | additional_dirs parameter with --add-dir arg builder | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0025/evidence.md | M | Medium |
| D-0026 | T02.03 | R-029, R-030 | Directory cap (10) with two-tier consolidation + log | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0026/evidence.md | M | Medium |
| D-0027 | T02.04 | R-031 | Backward-compat test: additional_dirs=None == v2.24 | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0027/evidence.md | S | Medium |
| D-0028 | T02.05 | R-032, R-033 | CLI TARGET argument + directory override options | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0028/evidence.md | M | Medium |
| D-0029 | T02.05 | R-034, R-035 | --include-agent and --save-manifest CLI options | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0029/evidence.md | M | Medium |
| D-0030 | T02.06 | R-036 | Extended load_portify_config() with new params | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0030/evidence.md | S | Low |
| D-0031 | T02.06 | R-037 | Extended ValidateConfigResult with new fields | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0031/evidence.md | S | Low |
| D-0032 | T03.01 | R-038 | Validation check 5: command-skill link validity | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0032/evidence.md | S | Low |
| D-0033 | T03.01 | R-039 | Validation check 6: referenced agent existence | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0033/evidence.md | S | Low |
| D-0034 | T03.02 | R-040 | Extended to_dict() with all new fields | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0034/evidence.md | S | Low |
| D-0035 | T03.03 | R-041 | Enriched component-inventory.md artifact | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0035/evidence.md | M | Low |
| D-0036 | T03.04 | R-042 | Stream A unit tests (resolver, models, regex, consolidation) | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0036/evidence.md | M | Low |
| D-0037 | T03.05 | R-043 | Stream B integration tests (CLI, validation, manifest, process) | STANDARD | Direct test execution | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0037/evidence.md | M | Low |
| D-0038 | T03.06 | R-044 | Stream C regression proof + Stream D NFR verification | STRICT | Sub-agent (quality-engineer) | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0038/evidence.md | M | Medium |

## Traceability Matrix

| Roadmap Item ID | Task ID(s) | Deliverable ID(s) | Tier | Confidence | Artifact Paths (rooted) |
|---:|---:|---:|---|---|---|
| R-001 | T01.01 | D-0001 | EXEMPT | 90% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0001/spec.md |
| R-002 | T01.01 | D-0002 | EXEMPT | 90% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0002/spec.md |
| R-003 | T01.01 | D-0003 | EXEMPT | 90% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0003/spec.md |
| R-004 | T01.02 | D-0004 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0004/evidence.md |
| R-005 | T01.02 | D-0005 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0005/evidence.md |
| R-006 | T01.03 | D-0006 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0006/evidence.md |
| R-007 | T01.03 | D-0007 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0007/evidence.md |
| R-008 | T01.04 | D-0008 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0008/evidence.md |
| R-009 | T01.04 | D-0009 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0009/evidence.md |
| R-010 | T01.05 | D-0010 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0010/evidence.md |
| R-011 | T01.05 | D-0011 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0011/evidence.md |
| R-012 | T01.05 | D-0012 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0012/evidence.md |
| R-013 | T01.06 | D-0013 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0013/evidence.md |
| R-014, R-015 | T01.07 | D-0014, D-0015 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0014/evidence.md, .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0015/evidence.md |
| R-016, R-017 | T01.07 | D-0015 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0015/evidence.md |
| R-018 | T01.08 | D-0016 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0016/evidence.md |
| R-019 | T01.08 | D-0017 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0017/evidence.md |
| R-020 | T01.08 | D-0018 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0018/evidence.md |
| R-021 | T01.09 | D-0019 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0019/evidence.md |
| R-022 | T01.09 | D-0020 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0020/evidence.md |
| R-023 | T02.01 | D-0021 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0021/evidence.md |
| R-024 | T02.01 | D-0022 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0022/evidence.md |
| R-025 | T02.02 | D-0023 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0023/evidence.md |
| R-026 | T02.02 | D-0024 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0024/evidence.md |
| R-027, R-028 | T02.03 | D-0025 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0025/evidence.md |
| R-029, R-030 | T02.03 | D-0026 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0026/evidence.md |
| R-031 | T02.04 | D-0027 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0027/evidence.md |
| R-032, R-033 | T02.05 | D-0028 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0028/evidence.md |
| R-034, R-035 | T02.05 | D-0029 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0029/evidence.md |
| R-036 | T02.06 | D-0030 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0030/evidence.md |
| R-037 | T02.06 | D-0031 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0031/evidence.md |
| R-038 | T03.01 | D-0032 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0032/evidence.md |
| R-039 | T03.01 | D-0033 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0033/evidence.md |
| R-040 | T03.02 | D-0034 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0034/evidence.md |
| R-041 | T03.03 | D-0035 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0035/evidence.md |
| R-042 | T03.04 | D-0036 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0036/evidence.md |
| R-043 | T03.05 | D-0037 | STANDARD | 80% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0037/evidence.md |
| R-044 | T03.06 | D-0038 | STRICT | 85% | .dev/releases/current/v2.24.1-cli-portify-cli-v5/artifacts/D-0038/evidence.md |

## Execution Log Template

**Intended Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/execution-log.md

| Timestamp (ISO 8601) | Task ID | Tier | Deliverable ID(s) | Action Taken (<= 12 words) | Validation Run (verbatim cmd or "Manual") | Result (Pass/Fail/TBD) | Evidence Path |
|---|---:|---|---:|---|---|---|---|

## Checkpoint Report Template

**Template:**

```
# Checkpoint Report -- <Checkpoint Title>
**Checkpoint Report Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/checkpoints/<deterministic-name>.md
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
- <list blocking issues referencing T<PP>.<TT> and D-####>
## Evidence
- <intended evidence paths under .dev/releases/current/v2.24.1-cli-portify-cli-v5/evidence/>
```

## Feedback Collection Template

**Intended Path:** .dev/releases/current/v2.24.1-cli-portify-cli-v5/feedback-log.md

| Task ID | Original Tier | Override Tier | Override Reason (<= 15 words) | Completion Status | Quality Signal | Time Variance |
|---:|---|---|---|---|---|---|
