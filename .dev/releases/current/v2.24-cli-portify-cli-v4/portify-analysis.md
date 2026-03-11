---
source_skill: sc-cli-portify-protocol
source_command: cli-portify
step_count: 12
parallel_groups: 0
gate_count: 10
agent_count: 0
complexity: high
---

# Portification Analysis: cli-portify

## Source Components

| Component | Path | Lines | Purpose |
|-----------|------|-------|---------|
| Command | `.claude/commands/sc/cli-portify.md` | 119 | Input validation, name derivation, skill dispatch |
| Skill (Protocol) | `src/superclaude/skills/sc-cli-portify-protocol/SKILL.md` | 562 | Full 4-phase behavioral protocol |
| Ref: analysis-protocol | `refs/analysis-protocol.md` | 215 | Phase 1 discovery checklist, step decomposition algorithm |
| Ref: pipeline-spec | `refs/pipeline-spec.md` | 600 | Phase 2 step/model/gate/executor design patterns |
| Ref: code-templates | `refs/code-templates.md` | 605 | INACTIVE -- historical reference only, not loaded |
| Base: pipeline/models.py | `src/superclaude/cli/pipeline/models.py` | 180 | PipelineConfig, Step, StepResult, GateCriteria, GateMode |
| Base: pipeline/gates.py | `src/superclaude/cli/pipeline/gates.py` | 109 | gate_passed() validation engine |
| Base: sprint/models.py | `src/superclaude/cli/sprint/models.py` | ~500 | TurnLedger, GateDisplayState, TaskEntry |
| Base: sprint/process.py | `src/superclaude/cli/sprint/process.py` | ~200 | ClaudeProcess, SignalHandler |
| Template | `src/superclaude/examples/release-spec-template.md` | 265 | Release spec with SC_PLACEHOLDER sentinels |

## Step Graph

### Step 0: Input Validation & Config Construction
- **Type**: pure-programmatic
- **Inputs**: [CLI args: --workflow, --name, --output, --dry-run]
- **Output**: validated config object (in-memory, no artifact)
- **Gate**: exempt
- **Agent**: none
- **Parallel**: no
- **Timeout**: N/A (instant)
- **Retry**: 0
- **Notes**: Resolves workflow path, derives CLI name, validates output directory. Emits error and exits on validation failure. Currently performed by the command `.md` before skill dispatch.

### Step 1: Component Discovery
- **Type**: hybrid (programmatic file discovery + Claude reads/summarizes)
- **Inputs**: [workflow path]
- **Output**: component-inventory.md (paths, line counts, purposes)
- **Gate**: standard (frontmatter: source_skill, component_count; min_lines: 10)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 120s
- **Retry**: 1
- **Notes**: Find command .md, SKILL.md, refs/, rules/, templates/, scripts/, agents. Line counts are programmatic (`wc -l`), purpose summaries require Claude.

### Step 2: Protocol Mapping
- **Type**: claude-assisted
- **Inputs**: [component-inventory.md, SKILL.md, all refs/]
- **Output**: protocol-map.md (step-by-step behavioral flow, wave/phase boundaries, agent delegation, conditional paths, data flow)
- **Gate**: standard (frontmatter: step_count, phase_count; min_lines: 50)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 300s
- **Retry**: 1
- **Notes**: Extracts the implicit behavioral flow from the skill protocol. Core analytical step requiring reading and understanding of natural language protocol.

### Step 3: Step Identification & Classification
- **Type**: claude-assisted
- **Inputs**: [protocol-map.md]
- **Output**: step-classification.md (step boundaries, programmatic spectrum ratings, dependency map, parallel groups)
- **Gate**: strict (frontmatter: step_count, programmatic_count, claude_count, hybrid_count; min_lines: 80; semantic: all steps classified, no orphan dependencies)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 300s
- **Retry**: 1
- **Notes**: Applies the classification rubric from analysis-protocol.md. Produces the step graph with types, dependency edges, and parallel group assignments.

### Step 4: Gate Extraction & Mode Assignment
- **Type**: hybrid (Claude identifies gates from protocol, programmatic validation of gate structure)
- **Inputs**: [step-classification.md, SKILL.md]
- **Output**: gate-definitions.md (gate tiers, frontmatter fields, semantic checks, gate modes)
- **Gate**: standard (frontmatter: gate_count; min_lines: 30)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 180s
- **Retry**: 1
- **Notes**: Maps validation expectations from the original workflow to GateCriteria + GateMode assignments.

### Step 5: Analysis Report Assembly
- **Type**: claude-assisted
- **Inputs**: [component-inventory.md, protocol-map.md, step-classification.md, gate-definitions.md]
- **Output**: portify-analysis.md (complete Phase 1 output following analysis-protocol template)
- **Gate**: strict (frontmatter: source_skill, step_count, parallel_groups, gate_count, complexity; min_lines: 100; semantic: has required sections, data flow diagram present)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 300s
- **Retry**: 1
- **Notes**: Synthesizes all Phase 1 sub-outputs into the canonical analysis document. USER REVIEW GATE after this step.

### Step 6: Pipeline Specification
- **Type**: claude-assisted
- **Inputs**: [portify-analysis.md, refs/pipeline-spec.md]
- **Output**: portify-spec.md (+ optional portify-prompts.md)
- **Gate**: strict (frontmatter: step_mapping_count, model_count, gate_definition_count; min_lines: 200; semantic: step_mapping entries present, all steps have gate definitions, pure-programmatic steps have implementation code)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Converts analysis into code-ready specifications: Step graph design, model definitions, prompt builders, gate designs, pure-programmatic implementations, executor design, integration plan. USER REVIEW GATE after this step. If `--dry-run`, pipeline stops here.

### Step 7: Template Instantiation
- **Type**: pure-programmatic
- **Inputs**: [release-spec-template.md]
- **Output**: portify-release-spec.md (working copy of template)
- **Gate**: light (file exists, non-empty)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 10s
- **Retry**: 0
- **Notes**: Copies template to working directory. Phase 2->3 entry gate checked before this step.

### Step 8: Content Population
- **Type**: claude-assisted
- **Inputs**: [portify-release-spec.md (template), portify-analysis.md, portify-spec.md]
- **Output**: portify-release-spec.md (populated, overwrites template copy)
- **Gate**: strict (semantic: zero remaining SC_PLACEHOLDER sentinels, all FR sections present, frontmatter complete)
- **Agent**: none
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Fills all template sections from Phase 1 and Phase 2 outputs per the mapping table. SC-003 self-validation: grep for remaining placeholders.

### Step 9: Automated Brainstorm Pass
- **Type**: claude-assisted (invokes /sc:brainstorm skill)
- **Inputs**: [portify-release-spec.md (populated)]
- **Output**: portify-release-spec.md (with Section 12 appended)
- **Gate**: standard (semantic: Section 12 heading present, gap analysis table present or zero-gap summary present)
- **Agent**: none (delegates to /sc:brainstorm which handles multi-persona orchestration internally)
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Claude subprocess invokes the existing `/sc:brainstorm` skill rather than reimplementing brainstorm behavioral patterns. The skill provides multi-persona orchestration (architect, analyzer, backend, etc.), MCP integrations (Sequential, Auggie), and structured output. Post-processing formats findings and incorporates gaps into spec.

### Step 10: Spec Panel Focus Pass
- **Type**: claude-assisted (invokes /sc:spec-panel skill)
- **Inputs**: [portify-release-spec.md]
- **Output**: focus-findings.md (structured findings from 4 experts)
- **Gate**: standard (frontmatter: finding_count, expert_count; min_lines: 30)
- **Agent**: none (delegates to /sc:spec-panel which handles expert panel internally)
- **Parallel**: no
- **Timeout**: 600s
- **Retry**: 1
- **Notes**: Claude subprocess invokes the existing `/sc:spec-panel --focus correctness,architecture` skill. Leverages its built-in expert panel (Fowler, Nygard, Whittaker, Crispin), quality scoring, and structured finding output.

### Step 11: Spec Panel Critique, Scoring & Convergence
- **Type**: claude-assisted (invokes /sc:spec-panel skill, convergence loop)
- **Inputs**: [portify-release-spec.md, focus-findings.md]
- **Output**: portify-release-spec.md (final), panel-report.md
- **Gate**: strict (frontmatter: quality_scores with 4 dimensions + overall; semantic: overall is arithmetic mean of 4 dimensions, no unaddressed CRITICALs unless ESCALATED)
- **Agent**: none (delegates to /sc:spec-panel which handles expert panel internally)
- **Parallel**: no
- **Timeout**: 900s (covers up to 3 convergence iterations)
- **Retry**: 0 (convergence loop is internal)
- **Notes**: Each convergence iteration launches a Claude subprocess invoking `/sc:spec-panel --mode critique`. The executor (Python) controls the convergence loop, checks for unaddressed CRITICALs, and decides whether to iterate. Max 3 iterations. USER REVIEW GATE at end.

## Parallel Groups

| Group | Steps | Rationale |
|-------|-------|-----------|
| (none) | -- | All steps are sequential. Each step depends on the output of the previous step. No independent operations identified. |

## Gates Summary

| Step | Tier | Mode | Frontmatter | Min Lines | Semantic Checks |
|------|------|------|-------------|-----------|-----------------|
| Step 0 | EXEMPT | -- | -- | -- | -- |
| Step 1 | STANDARD | BLOCKING | source_skill, component_count | 10 | -- |
| Step 2 | STANDARD | BLOCKING | step_count, phase_count | 50 | -- |
| Step 3 | STRICT | BLOCKING | step_count, programmatic_count, claude_count, hybrid_count | 80 | all_steps_classified, no_orphan_deps |
| Step 4 | STANDARD | BLOCKING | gate_count | 30 | -- |
| Step 5 | STRICT | BLOCKING | source_skill, step_count, parallel_groups, gate_count, complexity | 100 | has_required_sections, data_flow_present |
| Step 6 | STRICT | BLOCKING | step_mapping_count, model_count, gate_definition_count | 200 | step_mappings_present, all_gates_defined, programmatic_code_present |
| Step 7 | LIGHT | BLOCKING | -- | 0 | -- |
| Step 8 | STRICT | BLOCKING | -- | -- | zero_placeholders, all_frs_present, frontmatter_complete |
| Step 9 | STANDARD | BLOCKING | -- | -- | section_12_present, gap_table_or_summary |
| Step 10 | STANDARD | BLOCKING | finding_count, expert_count | 30 | -- |
| Step 11 | STRICT | BLOCKING | clarity, completeness, testability, consistency, overall | -- | overall_is_mean, no_unaddressed_criticals |

## Agent Delegation Map

| Agent | Used In Steps | Parallel | Contract |
|-------|--------------|----------|----------|
| (none) | -- | -- | The cli-portify protocol does not delegate to named agents. All Claude-assisted steps use inline prompt contracts. |

## Data Flow Diagram

```
[CLI args] --> Step 0: Input Validation
                    |
                    v
[workflow path] --> Step 1: Component Discovery --> [component-inventory.md]
                                                         |
                    +------------------------------------+
                    |                                    |
                    v                                    v
[SKILL.md, refs/] --> Step 2: Protocol Mapping --> [protocol-map.md]
                                                         |
                                                         v
                      Step 3: Step Identification --> [step-classification.md]
                                                         |
                    +------------------------------------+
                    |                                    |
                    v                                    v
              Step 4: Gate Extraction --> [gate-definitions.md]
                    |                          |
                    v                          v
              Step 5: Analysis Assembly --> [portify-analysis.md]
                                                  |
                    USER REVIEW                   |
                                                  v
         [refs/pipeline-spec.md] --> Step 6: Pipeline Spec --> [portify-spec.md]
                                                                  |
                    USER REVIEW                                   |
                    (--dry-run stops here)                         |
                                                                  v
         [release-spec-template.md] --> Step 7: Template Copy --> [portify-release-spec.md]
                                                                       |
         [portify-analysis.md] ----+                                   |
         [portify-spec.md] --------+--> Step 8: Content Population --> [portify-release-spec.md]
                                                                       |
                                   Step 9: Brainstorm Pass ----------> [portify-release-spec.md + S12]
                                                                       |
                                   Step 10: Focus Pass --------------> [focus-findings.md]
                                        |                              |
                                        v                              v
                                   Step 11: Critique + Convergence --> [portify-release-spec.md (final)]
                                        |                              [panel-report.md]
                                        v
                                   USER REVIEW
                                        |
                                   [RETURN CONTRACT]
```

## Classification Summary

| Category | Count | Steps |
|----------|-------|-------|
| Pure Programmatic | 2 | Step 0 (input validation), Step 7 (template copy) |
| Claude-Assisted | 8 | Steps 2, 3, 5, 6, 8, 9, 10, 11 |
| Hybrid | 2 | Step 1 (discovery), Step 4 (gate extraction) |
| Pure Inference | 0 | -- |

## Recommendations

### Step Consolidation Mapping

For the pipeline, the 12 logical steps consolidate to 7 pipeline steps:

| Pipeline Step | Logical Steps Consolidated | Rationale |
|--------------|---------------------------|-----------|
| `validate-config` | Step 0 | 1:1 mapping, pure programmatic |
| `discover-components` | Step 1 | 1:1 mapping, pure programmatic |
| `analyze-workflow` | Steps 2, 3, 4, 5 | All feed into single `portify-analysis.md` artifact; one Claude subprocess with comprehensive prompt reduces overhead while preserving gate coverage at the output boundary |
| `design-pipeline` | Step 6 | 1:1 mapping, produces `portify-spec.md` |
| `synthesize-spec` | Steps 7, 8 | Template copy is programmatic setup for content population; single Claude call handles both |
| `brainstorm-gaps` | Step 9 | 1:1 mapping, invokes existing `/sc:brainstorm` skill |
| `panel-review` | Steps 10, 11 | Focus + critique are both spec-panel operations; convergence loop handled by executor, each iteration invokes existing `/sc:spec-panel` skill |

### Programmatic Opportunities
1. **Step 1 (Component Discovery)**: File enumeration via `glob`/`Path.rglob()` and `wc -l` are fully programmatic. Only purpose extraction needs Claude. Consider splitting into: (a) programmatic file inventory, (b) Claude purpose annotation -- but the Claude step is cheap, so hybrid is acceptable.

2. **Steps 1-5 could be merged**: Steps 1 through 5 are all feeding into the single `portify-analysis.md` artifact. In the pipeline, these could be collapsed into fewer steps with a single comprehensive Claude prompt for analysis, reducing subprocess overhead. However, keeping them separate gives better gate coverage and failure isolation.

3. **Step 8 placeholder validation**: The SC-003 self-validation (zero remaining `{{SC_PLACEHOLDER:*}}`) is a pure-programmatic gate check, not a step. Model as a semantic check on Step 8's gate.

4. **Step 11 convergence loop**: The convergence loop (max 3 iterations of steps 4a-4d) is the most complex orchestration pattern. In the pipeline, this maps to a `while` loop in the executor with iteration tracking. The loop body is a single Claude subprocess per iteration (focus + incorporation + critique + scoring in one pass).

### Risk Areas
1. **Single-threaded execution**: All 12 steps are sequential with no parallelism. This is inherent to the workflow -- each step depends on the prior. Pipeline overhead is low but wall-clock time may be significant (~30-60 min for full execution).

2. **Large context windows**: Steps 8 and 11 need to ingest the full spec (potentially 500+ lines) plus prior artifacts. Prompt design must manage context carefully.

3. **Convergence non-termination**: The convergence loop has a hard cap of 3 iterations, but each iteration is expensive (600s timeout). Total Phase 4 timeout of 900s may be tight for 3 full iterations.

4. **User review gates**: Steps 5, 6, and 11 have user review gates. In a fully automated pipeline, these become approval prompts or are bypassed with a `--no-review` flag.

### Consolidation Recommendations
For the pipeline, recommend consolidating:
- **Steps 1-5 into 2 steps**: (a) Programmatic discovery + (b) Claude analysis producing portify-analysis.md
- **Steps 7-9 into 2 steps**: (a) Programmatic template copy + (b) Claude population + brainstorm
- **Steps 10-11 into 1 step**: Spec panel with convergence loop

This yields **7 pipeline steps** from the original 12, reducing subprocess launches while preserving gate coverage at the critical boundaries.
