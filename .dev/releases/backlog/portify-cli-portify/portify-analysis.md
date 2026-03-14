---
source_skill: sc-cli-portify-protocol
source_command: cli-portify
step_count: 12
parallel_groups: 1
gate_count: 10
agent_count: 0
complexity: high
---

# Portification Analysis: cli-portify

## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Command | `.claude/commands/sc/cli-portify.md` | 120 | Input validation, name derivation, protocol skill invocation |
| Skill | `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | 563 | Full 4-phase portification protocol with convergence loop |
| Ref: analysis-protocol | `refs/analysis-protocol.md` | 216 | Phase 1 discovery checklist, step decomposition algorithm |
| Ref: pipeline-spec | `refs/pipeline-spec.md` | 601 | Phase 2 step/model/gate/executor design patterns |
| Ref: code-templates | `refs/code-templates.md` | 606 | INACTIVE historical reference (v2.23) |
| Decisions | `decisions.yaml` | 124 | Blocking OQ resolutions + v2.23 ADRs |

**Note**: No dedicated agents. The skill references persona patterns (architect, analyzer, backend) that are embedded inline during Phase 3c brainstorm and Phase 4 panel review — per ADR-C01 (no inter-skill command invocation).

## Step Graph

### Step 0: Input Validation & Config Construction
- **Type**: pure-programmatic
- **Inputs**: CLI arguments (--workflow, --name, --output, --dry-run)
- **Output**: `portify-config.yaml` (resolved paths, derived names, validated config)
- **Gate**: STANDARD (config YAML valid, all paths resolve, no collisions)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 30s
- **Retry**: 0
- **Notes**: 6 validation checks from command spec. Fail-fast on any error. Resolves skill directory, derives CLI name, checks collision.

### Step 1: Component Discovery
- **Type**: pure-programmatic
- **Inputs**: `portify-config.yaml` (workflow path)
- **Output**: `component-inventory.yaml`
- **Gate**: STANDARD (YAML valid, >=1 component listed, SKILL.md found)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 60s
- **Retry**: 0
- **Notes**: Glob for command .md, SKILL.md, refs/, rules/, templates/, scripts/, agents. Count lines per file. Pure file-system operation.

### Step 2: Workflow Protocol Mapping
- **Type**: claude-assisted
- **Inputs**: `component-inventory.yaml`, all source files listed in inventory
- **Output**: `protocol-map.md`
- **Gate**: STRICT (frontmatter: status, step_count, parallel_groups; sections: Step Graph, Data Flow, Classifications; semantic: all steps have type classification)
- **Agent**: none (inline Claude subprocess)
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Extract behavioral flow, identify step boundaries, classify programmatic spectrum, map dependencies & parallel groups, extract gates, assign gate modes. This is the core analysis step.

### Step 3: Analysis Report Synthesis
- **Type**: claude-assisted
- **Inputs**: `protocol-map.md`, `component-inventory.yaml`
- **Output**: `portify-analysis-report.md`
- **Gate**: STRICT (frontmatter: source_skill, step_count, gate_count; min_lines: 100; sections: Source Components, Step Graph, Parallel Groups, Gates Summary, Data Flow Diagram, Classification Summary, Recommendations)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Synthesizes inventory + protocol map into the structured analysis format from refs/analysis-protocol.md. This is the Phase 1 deliverable.

### Step 4: User Review Gate (Phase 1→2)
- **Type**: pure-programmatic
- **Inputs**: `portify-analysis-report.md`
- **Output**: `phase1-approval.yaml` (status: approved|rejected, timestamp)
- **Gate**: STANDARD (approval status present)
- **Agent**: none
- **Parallel**: no
- **Timeout**: N/A (user interaction — pipeline pauses)
- **Retry**: 0
- **Notes**: Pipeline emits analysis report and pauses for user review. Per ADR OQ-007, uses TodoWrite checkpoint pattern. Resume continues to Phase 2.

### Step 5: Step Graph Design
- **Type**: claude-assisted
- **Inputs**: `portify-analysis-report.md`, refs/pipeline-spec.md
- **Output**: `step-graph-spec.md`
- **Gate**: STRICT (frontmatter: step_count, step_mapping; sections: Step Definitions, Parallel Groups, Dependencies; semantic: each step has id/prompt/output_file/gate/timeout)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Maps each workflow step to pipeline Step objects. Designs batched parallel groups. Defines build_steps() for dynamic step counts.

### Step 6: Model & Gate Design
- **Type**: claude-assisted
- **Inputs**: `step-graph-spec.md`, `portify-analysis-report.md`
- **Output**: `models-gates-spec.md`
- **Gate**: STRICT (frontmatter: model_count, gate_count; sections: Config Model, Status Enum, Result Model, Monitor State, Gate Criteria, Semantic Checks; semantic: all gate check functions have tuple[bool,str] signature description)
- **Agent**: none
- **Parallel**: no (depends on step 5)
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Designs domain dataclasses extending PipelineConfig/Step/StepResult. Designs GateCriteria per step. Writes semantic check function specs. Includes TurnLedger integration design.

### Step 7: Prompt & Executor Design
- **Type**: claude-assisted
- **Inputs**: `step-graph-spec.md`, `models-gates-spec.md`
- **Output**: `prompts-executor-spec.md`
- **Gate**: STRICT (frontmatter: prompt_count, executor_style; sections: Prompt Builders, Executor Design, Pure-Programmatic Implementations, Integration Plan; semantic: each prompt specifies output format + EXIT_RECOMMENDATION marker)
- **Agent**: none
- **Parallel**: no (depends on step 6)
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Writes prompt builders for Claude-assisted steps. Designs sprint-style synchronous supervisor. Implements pure-programmatic steps as Python code. Plans Click command group and main.py integration.

### Step 8: Pipeline Spec Assembly
- **Type**: hybrid (programmatic assembly + Claude synthesis)
- **Inputs**: `step-graph-spec.md`, `models-gates-spec.md`, `prompts-executor-spec.md`
- **Output**: `portify-spec.md` (+ optional `portify-prompts.md` if >300 lines)
- **Gate**: STRICT (frontmatter: status, step_mapping, module_plan, gate_definitions; min_lines: 200; sections: Step Graph, Models, Gates, Prompts, Executor, Integration; semantic: step_mapping count matches step_count)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Merges the three Phase 2 sub-specs into the consolidated pipeline specification. This is the Phase 2 deliverable.

### Step 9: User Review Gate (Phase 2→3)
- **Type**: pure-programmatic
- **Inputs**: `portify-spec.md`
- **Output**: `phase2-approval.yaml` (status: approved|rejected, timestamp)
- **Gate**: STANDARD (approval status present)
- **Agent**: none
- **Parallel**: no
- **Timeout**: N/A (user interaction)
- **Retry**: 0
- **Notes**: Pipeline emits spec and pauses for user approval. Phase 2→3 entry gate: spec status completed, all blocking checks passed, step_mapping >=1 entry.

### Step 10: Release Spec Synthesis (Phase 3)
- **Type**: claude-assisted
- **Inputs**: `portify-analysis-report.md`, `portify-spec.md`, release-spec-template.md
- **Output**: `portify-release-spec.md`
- **Gate**: STRICT (frontmatter: title, status, quality_scores; min_lines: 300; semantic: zero {{SC_PLACEHOLDER:*}} sentinels remaining, Section 12 brainstorm gap analysis present)
- **Agent**: none (embeds architect/analyzer/backend persona patterns inline per ADR-C01)
- **Parallel**: no
- **Timeout**: 900s
- **Retry**: 1
- **Notes**: Sub-steps: 3a template instantiation, 3b content population (13 section mappings), 3c automated brainstorm pass (3 personas), 3d gap incorporation. NFR-001 advisory: <10 min wall clock.

### Step 11: Spec Panel Review (Phase 4)
- **Type**: claude-assisted (convergence loop)
- **Inputs**: `portify-release-spec.md`
- **Output**: `portify-release-spec.md` (updated in place), `panel-report.md`
- **Gate**: STRICT (frontmatter: quality_scores with all 4 dimensions + overall; semantic: all CRITICAL findings addressed or dismissed with justification)
- **Agent**: none (embeds Fowler/Nygard/Whittaker/Crispin expert patterns inline per ADR-C01)
- **Parallel**: no
- **Timeout**: 1200s
- **Retry**: 0 (convergence loop handles retries internally)
- **Notes**: Sub-steps: 4a focus pass (correctness+architecture), 4b focus incorporation, 4c critique pass, 4d scoring. Convergence loop: max 3 iterations. States: REVIEWING→INCORPORATING→SCORING→CONVERGED|ESCALATED. Downstream ready gate: overall >= 7.0. NFR-002 advisory: <15 min.

## Parallel Groups

| Group | Steps | Rationale |
|-------|-------|-----------|
| 1 | step-5, step-6 could partially overlap | Step 6 depends on step 5 output, so NOT parallel. All Phase 2 sub-steps are sequential due to data dependencies. |

**Net parallel groups**: 0 true parallel groups. The pipeline is fully sequential due to strong inter-step data dependencies. Each step consumes the output of the prior step.

**Potential future parallelism**: If Phase 3c brainstorm personas were split into independent Claude subprocesses (one per persona), they could run in parallel. Currently specified as sequential inline analysis within a single step.

## Gates Summary

| Step | Tier | Mode | Frontmatter | Min Lines | Semantic Checks |
|------|------|------|-------------|-----------|-----------------|
| 0: Config | STANDARD | BLOCKING | config_valid | 0 | paths_resolve, no_collision |
| 1: Discovery | STANDARD | BLOCKING | component_count | 0 | skill_md_found |
| 2: Protocol Map | STRICT | BLOCKING | status, step_count, parallel_groups | 50 | all_steps_classified |
| 3: Analysis Report | STRICT | BLOCKING | source_skill, step_count, gate_count | 100 | required_sections_present |
| 4: User Review P1 | STANDARD | BLOCKING | approval_status | 0 | — |
| 5: Step Graph | STRICT | BLOCKING | step_count, step_mapping | 50 | steps_have_required_fields |
| 6: Models/Gates | STRICT | BLOCKING | model_count, gate_count | 80 | gate_signatures_valid |
| 7: Prompts/Executor | STRICT | BLOCKING | prompt_count, executor_style | 80 | prompts_have_exit_markers |
| 8: Pipeline Spec | STRICT | BLOCKING | status, step_mapping, module_plan | 200 | step_count_matches_mapping |
| 9: User Review P2 | STANDARD | BLOCKING | approval_status | 0 | — |
| 10: Release Spec | STRICT | BLOCKING | title, status, quality_scores | 300 | zero_placeholders, brainstorm_section_present |
| 11: Panel Review | STRICT | BLOCKING | quality_scores (4+overall) | — | criticals_addressed |

All gates are BLOCKING — every step output feeds downstream. No TRAILING gates.

## Agent Delegation Map

No agent delegation. All steps run as either:
- Pure-programmatic Python functions (steps 0, 1, 4, 9)
- Claude subprocesses with prompt contracts (steps 2, 3, 5, 6, 7, 8, 10, 11)

The skill embeds persona behavioral patterns inline (ADR-C01) rather than delegating to named agents.

## Data Flow Diagram

```
[CLI args] → step-0 (validate) → [portify-config.yaml]
                                        ↓
                                   step-1 (discover) → [component-inventory.yaml]
                                        ↓
                              step-2 (protocol map) → [protocol-map.md]
                                        ↓
                              step-3 (synthesize) → [portify-analysis-report.md]
                                        ↓
                              step-4 (user review) → [phase1-approval.yaml]
                                        ↓
                              step-5 (step graph) → [step-graph-spec.md]
                                        ↓
                              step-6 (models/gates) → [models-gates-spec.md]
                                        ↓
                              step-7 (prompts/exec) → [prompts-executor-spec.md]
                                        ↓
                              step-8 (assemble) → [portify-spec.md]
                                        ↓
                              step-9 (user review) → [phase2-approval.yaml]
                                        ↓
                              step-10 (release spec) → [portify-release-spec.md]
                                        ↓
                              step-11 (panel review) → [portify-release-spec.md (updated)]
                                                       [panel-report.md]
```

## Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | 4 | step-0 (config), step-1 (discovery), step-4 (review gate), step-9 (review gate) |
| Claude-Assisted | 7 | step-2, step-3, step-5, step-6, step-7, step-10, step-11 |
| Hybrid | 1 | step-8 (programmatic assembly + Claude synthesis) |
| Pure Inference | 0 | — |

## Recommendations

1. **Steps 0 and 1 should definitely be programmatic** — Config validation is `Path.exists()` + string manipulation. Component discovery is `glob` + `wc -l`. No judgment needed.

2. **User review gates (steps 4, 9) need pipeline pause/resume** — These require the executor to write a checkpoint and exit cleanly, with a `--resume` flag to continue from the approval point. The sprint resume pattern applies.

3. **Step 11 convergence loop is the most complex step** — It contains an internal state machine (REVIEWING→INCORPORATING→SCORING→CONVERGED|ESCALATED) with up to 3 iterations. The executor needs to model this as a single step with internal loop logic, not as 3 separate steps.

4. **Consider splitting Phase 2 sub-steps (5, 6, 7) into a single Claude subprocess** — The current decomposition creates 3 sequential Claude calls where one longer call with structured output sections might be more token-efficient. Trade-off: finer gates vs. fewer subprocess launches.

5. **Phase 3 brainstorm personas could be parallelized** — Three independent persona analyses (architect, analyzer, backend) have no data dependencies between them. Currently sequential within step 10.

6. **Template loading (step 10, sub-step 3a) is programmatic** — File copy from `src/superclaude/examples/release-spec-template.md` to work_dir. Should be extracted as a pre-step or inline function.

7. **Dry-run stops after step 9** — When `--dry-run` is active, the pipeline should execute steps 0-8 (Phases 0-2), emit contracts, and exit without Phase 3 or Phase 4.
