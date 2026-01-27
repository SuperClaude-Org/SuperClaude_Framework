# Feature Specification: /sc:roadmap Command

**Version**: 1.1.0
**Author**: SuperClaude Spec Panel
**Date**: 2026-01-26
**Status**: Refactored with Adversarial Debate Proposals
**Review Score**: 78/100 → 82% avg confidence (4 debate rounds)
**Changes in v1.1.0**: Added Sections 3.3.1, 3.7; Enhanced 3.4, 9.1 with proposals P1-P4

---

## Executive Summary

The `/sc:roadmap` command is a SuperClaude skill that generates comprehensive, structured release roadmaps from specification documents. It transforms project requirements, feature descriptions, or PRD files into actionable milestone-based roadmaps with integrated multi-agent validation.

**Key Differentiator**: Unlike general planning tools, `/sc:roadmap` **requires** a specification file as mandatory input, ensuring roadmaps are grounded in documented requirements rather than ad-hoc descriptions.

---

## 1. Command Interface

### 1.1 Syntax

```bash
/sc:roadmap <spec-file-path> [options]
```

### 1.2 Required Input

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `<spec-file-path>` | File path | Path to specification document (required) | Must exist, must be readable |

**Supported Input Formats**:
- Markdown (`.md`) - Primary format
- Text (`.txt`) - Plain text specifications
- YAML (`.yaml`, `.yml`) - Structured requirements
- JSON (`.json`) - API/schema specifications

### 1.3 Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--template <type>` | `-t` | Template type: `feature`, `quality`, `docs`, `security`, `performance`, `migration` | Auto-detect |
| `--output <dir>` | `-o` | Output directory for roadmap artifacts | `.roadmaps/<spec-name>/` |
| `--depth <level>` | `-d` | Analysis depth: `quick`, `standard`, `deep` | `standard` |
| `--validate` | `-v` | Enable multi-agent validation (STRICT tier) | `true` |
| `--no-validate` | | Skip validation phase | `false` |
| `--compliance <tier>` | `-c` | Force compliance tier: `strict`, `standard`, `light` | Auto-detect |
| `--persona <name>` | `-p` | Override primary persona | Auto-select |
| `--dry-run` | | Preview without generating files | `false` |

### 1.4 Usage Examples

```bash
# Basic usage - specification file required
/sc:roadmap path/to/feature-spec.md

# With specific template
/sc:roadmap specs/auth-system.md --template security

# Custom output location
/sc:roadmap requirements/v2.0-prd.md --output .roadmaps/v2.0-release/

# Deep analysis with strict validation
/sc:roadmap specs/migration-plan.md --depth deep --compliance strict

# Quick preview without file generation
/sc:roadmap specs/quick-fix.md --dry-run

# Override persona selection
/sc:roadmap specs/api-design.md --persona backend
```

---

## 2. Specification File Requirements

### 2.1 Minimum Viable Specification

The input specification file **MUST** contain:

```markdown
# <Project/Feature Name>

## Overview
[Brief description of what is being built]

## Requirements
[At least 3 functional requirements with clear acceptance criteria]

## Scope
[What is included and excluded]
```

### 2.2 Recommended Specification Structure

```markdown
# <Project/Feature Name>

## Overview
[2-3 sentence description]

## Problem Statement
[What problem does this solve?]

## Requirements

### Functional Requirements
- FR-001: [Requirement description]
- FR-002: [Requirement description]

### Non-Functional Requirements
- NFR-001: [Performance/Security/Scalability requirement]

## Scope

### In Scope
- [Feature/capability included]

### Out of Scope
- [Feature/capability explicitly excluded]

## Dependencies
- [External systems, APIs, libraries]

## Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk description] | High/Medium/Low | [Mitigation strategy] |
```

### 2.3 Specification Validation Rules

| Rule | Validation | Error Action |
|------|------------|--------------|
| File exists | `Read` tool access | STOP with clear error |
| File readable | Content length > 0 | STOP with "Empty spec file" |
| Has title | H1 heading present | WARN and extract from filename |
| Has requirements | `## Requirements` or keywords | STOP with "No requirements found" |
| Minimum content | > 100 characters | WARN and proceed with caution |

---

## 3. 5-Wave Orchestration Architecture

### 3.1 Wave Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ Wave 1: DETECTION & ANALYSIS                                        │
│ ├── Parse specification file                                        │
│ ├── Extract requirements, scope, dependencies                       │
│ ├── Score complexity (0.0-1.0)                                     │
│ └── Activate personas based on domain distribution                  │
├─────────────────────────────────────────────────────────────────────┤
│ Wave 2: PLANNING & TEMPLATE SELECTION                               │
│ ├── Template discovery: local → user → plugin → inline             │
│ ├── Score template compatibility                                    │
│ ├── Create task breakdown via TodoWrite                            │
│ └── Establish milestone structure                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Wave 3: GENERATION                                                  │
│ ├── Generate roadmap.md with milestone hierarchy                   │
│ ├── Generate tasklist files per milestone                          │
│ ├── Generate test-strategy.md                                      │
│ └── Generate supporting artifacts                                   │
├─────────────────────────────────────────────────────────────────────┤
│ Wave 4: VALIDATION (Multi-Agent)                                    │
│ ├── Task with quality-engineer prompt: Completeness, consistency   │
│ ├── Task with self-review prompt: 4-question validation protocol  │
│ ├── Score aggregation                                              │
│ └── Decision: PASS (≥85%) | REVISE (70-84%) | REJECT (<70%)        │
├─────────────────────────────────────────────────────────────────────┤
│ Wave 5: COMPLETION                                                  │
│ ├── think_about_whether_you_are_done()                             │
│ ├── Memory persistence via Serena                                  │
│ ├── Git operations (if requested)                                  │
│ └── Final output summary                                           │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Wave 1: Detection & Analysis

**Purpose**: Parse input specification and establish execution context

**Inputs**:
- Specification file path (required)
- User-provided flags (optional)

**Process**:
```yaml
step_1_file_validation:
  action: Read specification file
  validate:
    - File exists
    - File is readable
    - Content meets minimum requirements
  on_failure: STOP with actionable error message

step_2_content_extraction:
  action: Parse specification structure
  extract:
    - Title and description
    - Functional requirements (FR-XXX)
    - Non-functional requirements (NFR-XXX)
    - Scope boundaries
    - Dependencies
    - Success criteria
    - Risks and mitigations

step_3_domain_analysis:
  action: Classify specification domains
  domains:
    - frontend: UI, components, UX, accessibility
    - backend: API, database, services, infrastructure
    - security: auth, encryption, compliance, vulnerabilities
    - performance: optimization, caching, scaling
    - documentation: guides, references, migration
  output: domain_distribution percentages

step_4_complexity_scoring:
  action: Calculate complexity score (0.0-1.0)
  factors:
    - requirement_count: weight 0.25
    - dependency_depth: weight 0.25
    - domain_spread: weight 0.20
    - risk_severity: weight 0.15
    - scope_size: weight 0.15

step_5_persona_activation:
  action: Select personas based on domain distribution
  rules:
    - Primary: Domain with ≥40% coverage, confidence ≥85%
    - Consulting: Domains with ≥15% coverage, confidence ≥70%
    - Fallback: architect for system-wide concerns
```

**Outputs**:
- `extraction.md`: Structured extraction of all specification elements
- Domain distribution analysis
- Complexity score
- Persona assignment

### 3.3 Wave 2: Planning & Template Selection

**Purpose**: Select appropriate template and establish roadmap structure

**Process**:
```yaml
step_1_template_discovery:
  search_order:
    1. Local: ./templates/roadmaps/
    2. User: ~/.claude/templates/roadmaps/
    3. Plugin: plugins/superclaude/templates/roadmaps/
    4. Inline: Generate variant from domain analysis

step_2_template_scoring:
  factors:
    - domain_alignment: 40%
    - structure_fit: 30%
    - complexity_match: 20%
    - optional_section_relevance: 10%
  threshold:
    - ≥80%: Select template directly
    - <80%: Create variant with adjustments

step_3_milestone_planning:
  action: Create milestone structure
  constraints:
    - Minimum: 3 milestones
    - Maximum: 8 milestones
    - Each milestone: 3-10 tasks

step_4_todo_initialization:
  action: Initialize TodoWrite with generation tasks
  states: [pending, in_progress, completed]
  # NOTE: No "blocked" state - use "[BLOCKED: reason]" prefix in content
```

**Outputs**:
- Template selection with rationale
- Milestone structure outline
- TodoWrite task list initialized

### 3.3.1 Inline Template Generation Algorithm

When no matching template is found (step 4 of template discovery falls back to inline generation):

```yaml
milestone_count_formula:
  complexity_low:
    condition: complexity < 0.4
    range: 3-4 milestones
    base_names: [Foundation, Implementation, Validation]
  complexity_medium:
    condition: complexity 0.4-0.7
    range: 4-6 milestones
    base_names: [Foundation, Design, Implementation, Testing, Deployment]
  complexity_high:
    condition: complexity > 0.7
    range: 5-8 milestones
    base_names: [Analysis, Design, Foundation, Core Implementation, Integration, Validation, Deployment]

  count_selection:
    method: "Interpolate within range based on requirement_count and domain_spread"
    formula: "base_count + floor((requirement_count - 5) / 5) + (1 if domain_spread > 2 else 0)"
    clamp: "Always within range bounds"

domain_mapping:
  single_primary: "Add 1 domain-specific milestone"
  multi_primary_resolution:
    condition: "Multiple domains >= 40%"
    action: "Add milestones in order of coverage percentage (highest first)"
    limit: "Maximum 2 domain-specific milestones"
    ordering: "Insert before final Deployment/Validation milestone"
  no_primary_fallback:
    condition: "No domain >= 40%"
    action: "Use generic milestones without domain-specific additions"
    logging: "WARN: No primary domain detected"

  domain_milestones:
    frontend_primary: "UX Validation"
    backend_primary: "API Specification"
    security_primary: "Security Audit"

required_sections_per_milestone:
  - Objective: "1-2 sentences describing the milestone goal"
  - Type: "FEATURE | IMPROVEMENT | DOC | TEST | REFACTOR"
  - Priority: "P0-Critical | P1-High | P2-Medium | P3-Low"
  - Deliverables: "Bulleted list with IDs, minimum 1"
  - Dependencies: "List of milestone IDs or 'None'"
  - Acceptance_Criteria: "Testable statements, minimum 1"
  - Risk_Level: "High | Medium | Low"
  - Files_Affected: "List of predicted paths, or 'TBD' if unknown"

minimum_requirements:
  - template_must_include: "At least 1 milestone"
  - milestone_must_include: "At least 1 deliverable"
  - extraction_must_include: "At least 3 requirements"

input_clarification:
  complexity_score:
    source: "Output of step_4_complexity_scoring (Section 3.2)"
    scale: "0.0-1.0 (normalized)"
    conversion_rule: "If consuming from 0-100 scale, divide by 100"
```

### 3.4 Wave 3: Generation

**Purpose**: Generate all roadmap artifacts

**Artifacts Generated**:

| Artifact | Location | Description |
|----------|----------|-------------|
| `roadmap.md` | `<output>/roadmap.md` | Master roadmap document |
| `extraction.md` | `<output>/extraction.md` | Extracted requirements summary |
| `tasklists/M{N}-*.md` | `<output>/tasklists/` | Per-milestone task files |
| `test-strategy.md` | `<output>/test-strategy.md` | Testing and validation approach |
| `execution-prompt.md` | `<output>/execution-prompt.md` | Implementation instructions |

**Dependency Model** (implements RULES.md "Batch Operations" - Priority: CRITICAL):
```yaml
wave_3_dependencies:
  step_1_generate_roadmap:
    action: "Generate roadmap.md with milestone hierarchy"
    depends_on: [wave_2.milestone_structure]

  step_2_generate_tasklists:
    action: "Generate tasklists/M{N}-*.md per milestone"
    depends_on: [step_1_generate_roadmap]

  step_3_generate_test_strategy:
    action: "Generate test-strategy.md"
    depends_on: [step_2_generate_tasklists]
    concurrent_with: [step_4_generate_execution_prompt]

  step_4_generate_execution_prompt:
    action: "Generate execution-prompt.md"
    depends_on: [step_2_generate_tasklists]
    concurrent_with: [step_3_generate_test_strategy]

execution_semantics:
  parallel_eligible: "Steps with concurrent_with can execute together"
  error_behavior: "Fail-isolated with rollback capability"
```

**Roadmap.md Structure**:
```markdown
# Release Roadmap: <Project Name>

## Metadata
- Source Specification: <spec-file-path>
- Generated: <timestamp>
- Generator: /sc:roadmap v1.0
- Item Count: <X> requirements, <Y> milestones, <Z> tasks

### Persona Assignment
**Primary**: <persona> — <X>% of items are <DOMAIN> work
**Consulting**: <list of consulting personas>

---

## Executive Summary
<2-3 sentences summarizing the roadmap>

---

## Milestones Overview
| Milestone | Name | Deliverables | Dependencies | Risk Level |
|-----------|------|--------------|--------------|------------|
| M1 | <name> | <count> | <deps> | <High/Medium/Low> |

---

### Milestone 1: <Name>
**Objective**: <Clear goal>
**Dependencies**: <List or None>

#### Deliverables
| ID | Type | Description | Acceptance Criteria | Files Affected |
|----|------|-------------|---------------------|----------------|
| D1.1 | <type> | <description> | <criteria> | <files> |

---

## Dependency Graph
<ASCII or mermaid diagram>

---

## Risk Register
| Risk ID | Description | Probability | Impact | Mitigation |
|---------|-------------|-------------|--------|------------|

---

## Success Criteria
- [ ] <Measurable criterion from spec>
```

**Tasklist File Structure** (`M{N}-<name>.md`):
```markdown
# Tasklist: M{N} - <Milestone Name>

## Metadata
- Milestone: M{N}
- Dependencies: <List>
- Complexity: <Low/Medium/High>

## Tasks

### T{M}.{N}: <Task Name>
**Type**: FEATURE | IMPROVEMENT | DOC | TEST
**Priority**: P0-Critical | P1-High | P2-Medium | P3-Low
**Files Affected**: <list of paths>

#### Steps
1. <Step with specific action>
2. <Step with specific action>

#### Acceptance Criteria
- [ ] <Testable criterion>

#### Verification
```bash
# Commands to verify completion
```
```

### 3.5 Wave 4: Validation (Multi-Agent)

**Purpose**: Quality assurance through multi-agent review

**IMPORTANT**: The Task tool does NOT have a `subagent_type` parameter. Agent specialization must be embedded in the Task prompt itself.

**Validation Pipeline**:
```yaml
agent_1_quality_engineer:
  # CORRECT: Embed agent type in prompt, not as parameter
  task_invocation: |
    Task tool call:
      description: "Validate roadmap artifacts for quality"
      prompt: |
        You are a quality-engineer agent performing roadmap validation.

        Focus areas:
        1. **Completeness**: Are all spec requirements covered in the roadmap?
        2. **Correctness**: Is milestone ordering logical and achievable?
        3. **Consistency**: Are IDs traceable across all generated documents?
        4. **Compliance**: Do all paths and patterns follow SuperClaude conventions?

        Review the following artifacts: [roadmap.md, extraction.md, tasklists/]

        Output a JSON score object:
        {"quality_score": 0-100, "issues": [...], "rationale": "..."}
  output: quality_score (0-100)

agent_2_self_review:
  # CORRECT: Embed review protocol in prompt
  task_invocation: |
    Task tool call:
      description: "Self-review validation protocol"
      prompt: |
        You are performing a self-review of the roadmap generation process.

        Answer these 4 validation questions with evidence:
        1. "Did I read the entire specification before generating?"
           → Cite specific sections from the spec
        2. "Are all paths using correct SuperClaude conventions?"
           → Verify: .claude/skills/, plugins/superclaude/agents/, etc.
        3. "Did I avoid the critical mistakes (see section 6)?"
           → Check: No subagent_type param, TodoWrite has 3 states only
        4. "Is every claim traceable to the input specification?"
           → Map each roadmap item to spec requirement

        Output: {"review_score": 0-100, "evidence": {...}, "gaps": [...]}
  output: review_score (0-100)

score_aggregation:
  weights:
    quality_engineer: 0.6
    self_review: 0.4
  thresholds:
    PASS: ≥85%
    REVISE: 70-84%
    REJECT: <70%

decision_actions:
  PASS:
    - Proceed to Wave 5
    - Mark artifacts as validated
  REVISE:
    - Generate improvement suggestions
    - Allow user to proceed or iterate
  REJECT:
    - Preserve drafts with .draft extension
    - Report specific failures
    - Suggest spec improvements
```

### 3.6 Wave 5: Completion

**Purpose**: Finalize outputs and persist session state

**Process**:
```yaml
step_1_completion_check:
  action: think_about_whether_you_are_done()
  verify:
    - All 5 artifacts generated
    - Validation passed or acknowledged
    - No unresolved issues

step_2_memory_persistence:
  action: write_memory via Serena MCP
  content:
    session_id: <unique>
    spec_path: <input file>
    output_path: <output directory>
    validation_score: <score>
    completion_status: <success/partial/failed>
    artifacts_generated: [list]

step_3_git_operations:
  condition: User requested or --commit flag
  actions:
    - Stage generated files
    - Create commit with structured message
    - Optional: Create branch for roadmap

step_4_output_summary:
  format: |
    ## Generation Complete

    **Artifacts Created**:
    - [x] roadmap.md
    - [x] extraction.md
    - [x] tasklists/M1-M{N}
    - [x] test-strategy.md
    - [x] execution-prompt.md

    **Validation Score**: <X>/100
    **Output Location**: <path>
    **Next Steps**: Execute tasklists M1 → M{N}
```

### 3.7 Parallelization Strategy

This section consolidates parallel execution opportunities across all waves (implements RULES.md requirements).

```yaml
wave_1_detection:
  parallel:
    - Content extraction (FR, NFR, scope, dependencies can extract simultaneously)
    - Domain analysis calculations (independent scoring)
  sequential:
    - File validation MUST complete before extraction
    - Persona activation depends on domain analysis results

wave_2_planning:
  parallel:
    - Template discovery paths can be searched simultaneously
    - Scoring factors can be calculated in parallel
  sequential:
    - Template selection depends on discovery completion
    - Task breakdown depends on template selection

wave_3_generation:
  step_dependencies: "roadmap → tasklists → [test-strategy, execution-prompt]"
  concurrent_eligible:
    - test-strategy.md and execution-prompt.md (both depend only on tasklists)

wave_4_validation:
  mode: sequential
  rationale: "Task tool AWAIT semantics require sequential agent calls"
  operations: [quality_engineer_assessment, self_review_validation]

wave_5_completion:
  parallel: [memory_persistence, git_operations_if_enabled]
  sequential: [completion_check MUST be final operation]

performance_expectation:
  without_parallelization: "3-5 minutes"
  with_parallelization: "1.5-3 minutes (30-45% reduction)"
  wave_4_note: "Sequential validation adds 30-60s fixed overhead"

error_handling:
  parallel_failure: "If any parallel operation fails, abort group and report first error"
  partial_success: "Parallel groups are atomic - all succeed or all retry"

notation_guide:
  parallel: "Operations with no data dependencies, can start simultaneously"
  sequential: "Operations requiring output from previous step"
  concurrent_eligible: "Operations that CAN run together if executor supports it"

framework_reference: |
  Implements RULES.md requirements:
  - "Parallel Everything: Execute independent operations in parallel" (Priority: RECOMMENDED)
  - "Parallelization Analysis: During planning, explicitly identify operations" (Priority: CRITICAL)
  - "Efficiency Metrics: Plan should specify expected parallelization gains" (Priority: CRITICAL)
```

---

## 4. Persona Integration

### 4.1 Auto-Activation Rules

| Spec Domain | Primary Persona | Consulting Personas |
|-------------|-----------------|---------------------|
| Feature development | architect | backend, frontend |
| Security release | security | architect, backend |
| Performance optimization | performance | backend, architect |
| Documentation | scribe | mentor, architect |
| Quality/Testing | qa | analyzer, architect |
| Infrastructure | devops | backend, security |

### 4.2 Persona Confidence Thresholds

```yaml
activation_thresholds:
  primary: confidence >= 85%
  consulting: confidence >= 70%
  fallback: architect (always available)

scoring_factors:
  keyword_matching: 30%
  context_analysis: 40%
  user_history: 20%
  performance_metrics: 10%
```

### 4.3 Manual Override

```bash
# Force specific persona
/sc:roadmap spec.md --persona security

# Multi-persona override
/sc:roadmap spec.md --persona "architect,security"
```

---

## 5. MCP Server Integration

### 5.1 Server Assignments

| Wave | Primary MCP | Secondary MCP | Purpose |
|------|-------------|---------------|---------|
| Wave 1 | Sequential | Serena | Complex analysis, project context |
| Wave 2 | Context7 | Sequential | Template patterns, structured planning |
| Wave 3 | Serena | Context7 | Session persistence, pattern lookup |
| Wave 4 | Sequential | - | Multi-step validation reasoning |
| Wave 5 | Serena | - | Memory persistence |

### 5.2 Circuit Breaker Configuration

```yaml
circuit_breakers:
  sequential:
    failure_threshold: 3
    timeout: 30s
    fallback: "Native Claude reasoning"
    impact: "Reduced analysis depth"

  serena:
    failure_threshold: 4
    timeout: 45s
    fallback: "Basic file operations"
    impact: "No session persistence"

  context7:
    failure_threshold: 5
    timeout: 60s
    fallback: "WebSearch for patterns"
    impact: "Less curated results"
```

---

## 6. Critical Implementation Rules

### 6.1 Mandatory Corrections (MUST Follow)

| # | Incorrect Pattern | Correct Pattern |
|---|-------------------|-----------------|
| 1 | `subagent_type` as Task API parameter | Embed agent type in Task prompt text (see Section 3.5) |
| 2 | Templates exist by default | **CREATE** `plugins/superclaude/templates/roadmaps/` (see Section 6.4) |
| 3 | Compliance tiers in RULES.md | Compliance tiers are in **ORCHESTRATOR.md** |
| 4 | TodoWrite has "blocked" state | Only 3 states: `pending`, `in_progress`, `completed` |
| 5 | Wave-enabled command count mismatch | ORCHESTRATOR.md lists 6, COMMANDS.md lists 7 (includes `/workflow`) |
| 6 | /sc:git has tag, diff, log | These subcommands **don't exist** |

### 6.2 Path Conventions

```yaml
skills:
  definition: .claude/skills/{skill-name}/SKILL.md
  example: .claude/skills/sc-roadmap/SKILL.md

agents:
  definition: plugins/superclaude/agents/{name}.md
  example: plugins/superclaude/agents/roadmap-orchestrator.md

templates:
  location: plugins/superclaude/templates/roadmaps/
  types:
    - feature-release.md
    - quality-release.md
    - documentation-release.md
    - security-release.md
    - performance-release.md
    - migration-release.md

outputs:
  roadmaps: .roadmaps/<spec-name>/
  artifacts: .roadmaps/<spec-name>/artifacts/
  tasklists: .roadmaps/<spec-name>/tasklists/
```

### 6.3 TodoWrite Blocked Items Workaround

Since `blocked` state doesn't exist, use this pattern:

```yaml
# WRONG - Will fail
status: blocked
content: "Waiting for API docs"

# CORRECT - Use pending with prefix in TodoWrite
todos:
  - content: "[BLOCKED: waiting for API docs] Implement authentication"
    status: pending
    activeForm: "Implementing authentication (blocked on API docs)"
```

### 6.4 Template Creation Prerequisites

**CRITICAL**: The template directory does NOT exist by default. Before `/sc:roadmap` can function, create:

```bash
# Create template directory
mkdir -p plugins/superclaude/templates/roadmaps/variants/

# Required template files to create:
plugins/superclaude/templates/roadmaps/
├── feature-release.md        # For new features
├── quality-release.md        # For quality/testing improvements
├── documentation-release.md  # For documentation efforts
├── security-release.md       # For security hardening
├── performance-release.md    # For performance optimization
└── migration-release.md      # For migrations/upgrades
```

**Implementation Task**: The `/sc:roadmap` skill MUST include a Wave 0 (Prerequisites) step that:
1. Checks if template directory exists
2. If missing, generates inline variant from domain analysis
3. Logs warning: "Template directory not found, using inline generation"

---

## 7. Output Specifications

### 7.1 Required Artifacts (5 Total)

| # | Artifact | Location | Required |
|---|----------|----------|----------|
| 1 | `roadmap.md` | `<output>/roadmap.md` | Yes |
| 2 | `extraction.md` | `<output>/extraction.md` | Yes |
| 3 | `tasklists/` | `<output>/tasklists/M{N}-*.md` | Yes |
| 4 | `test-strategy.md` | `<output>/test-strategy.md` | Yes |
| 5 | `execution-prompt.md` | `<output>/execution-prompt.md` | Yes |

### 7.2 Optional Artifacts

| Artifact | Condition | Location |
|----------|-----------|----------|
| `validation-report.md` | When --validate enabled | `<output>/validation-report.md` |
| `quality-scorecard.md` | After multi-agent review | `<output>/quality-scorecard.md` |
| `dependency-graph.mmd` | Complex dependencies | `<output>/dependency-graph.mmd` |

### 7.3 Output Directory Structure

```
.roadmaps/<spec-name>/
├── roadmap.md                    # Master roadmap
├── extraction.md                 # Extracted requirements
├── test-strategy.md              # Testing approach
├── execution-prompt.md           # Implementation guide
├── tasklists/
│   ├── M1-foundation.md
│   ├── M2-implementation.md
│   ├── M3-testing.md
│   └── M{N}-finalization.md
├── artifacts/                    # Supporting documents
│   ├── dependency-graph.mmd
│   └── risk-matrix.md
└── validation/                   # Validation outputs
    ├── quality-scorecard.md
    └── validation-report.md
```

---

## 8. Error Handling

### 8.1 Specification Errors

| Error | Detection | Action |
|-------|-----------|--------|
| File not found | Read tool fails | STOP: "Specification file not found: <path>" |
| Empty file | Content length = 0 | STOP: "Specification file is empty" |
| No requirements | Missing requirements section | STOP: "No requirements found in specification" |
| Invalid format | Parsing failure | WARN: "Could not parse <section>, proceeding with available content" |

### 8.2 Generation Errors

| Error | Detection | Action |
|-------|-----------|--------|
| Template not found | Discovery returns empty | WARN: "No template found, generating inline variant" |
| Write failure | Write tool error | STOP: "Cannot write to output directory: <path>" |
| Validation failure | Score < 70% | WARN: "Validation failed, artifacts saved as drafts" |

### 8.3 Recovery Strategies

```yaml
recovery_patterns:
  specification_incomplete:
    action: "Generate partial roadmap with explicit gaps noted"
    output: "roadmap.partial.md with [INCOMPLETE] markers"

  validation_failed:
    action: "Preserve drafts, provide improvement suggestions"
    output: "*.draft.md files in output directory"

  mcp_unavailable:
    action: "Use native Claude reasoning with reduced depth"
    notification: "MCP server unavailable, analysis depth reduced"
```

---

## 9. Compliance Tier Classification

### 9.1 Auto-Classification Rules

| Tier | Triggers | Verification |
|------|----------|--------------|
| **STRICT** | security, auth, migration, refactor, multi-file | Sub-agent (quality-engineer) |
| **STANDARD** | implement, add, create, update, feature | Direct test execution |
| **LIGHT** | typo, comment, formatting, minor | Quick sanity check |
| **EXEMPT** | explain, search, brainstorm, question | No verification |

**Classification Pipeline** (for disambiguation):
```yaml
tier_classification_pipeline:
  step_1: "Check user override (--compliance flag)"
  step_2: "Check compound phrase detection (ORCHESTRATOR.md 'Compound Phrase Overrides')"
  step_3: "Check EXEMPT pattern matching (regex patterns for read-only verbs)"
  step_4: "Score keywords by tier"
  step_5: "Apply context boosters (file count, security paths)"
  step_6: "Resolve conflicts using tier priority: STRICT > EXEMPT > LIGHT > STANDARD"

reference_note: |
  Compound phrase definitions and conflict resolution examples are maintained in
  ORCHESTRATOR.md to ensure single source of truth. Key rules:
  - "quick fix" → LIGHT (compound overrides "fix")
  - "fix security" → STRICT (security always escalates)
  - "explain [pattern]" → EXEMPT (read-only verbs bypass scoring)
```

### 9.2 Roadmap Default Tier

The `/sc:roadmap` command defaults to **STANDARD** tier with automatic escalation to **STRICT** when:
- Complexity score > 0.8
- Security-related requirements detected
- Multi-domain scope (>3 domains)
- User specifies `--compliance strict`

---

## 10. Integration Points

### 10.1 Related Commands

| Command | Integration | Usage |
|---------|-------------|-------|
| `/sc:task` | Execute roadmap tasks | `/sc:task "Implement M1 tasks"` |
| `/sc:implement` | Build roadmap features | `/sc:implement @roadmap.md M1.1` |
| `/sc:analyze` | Review roadmap quality | `/sc:analyze @roadmap.md --focus quality` |
| `/sc:improve` | Enhance roadmap | `/sc:improve @roadmap.md` |

### 10.2 Workflow Integration

```bash
# Full workflow example
/sc:roadmap specs/feature-v2.md                    # Generate roadmap
/sc:task "Execute M1: Foundation" @roadmap.md      # Start execution
/sc:implement "M1.1: Setup infrastructure"         # Implement tasks
/sc:analyze @.roadmaps/feature-v2/ --comprehensive # Review progress
/sc:improve @roadmap.md --based-on-feedback        # Iterate
```

---

## 11. Success Metrics

### 11.1 Generation Quality

| Metric | Target | Measurement |
|--------|--------|-------------|
| Requirement coverage | 100% | All FR/NFR from spec appear in roadmap |
| ID traceability | 100% | All IDs traceable across artifacts |
| Validation score | ≥85% | Multi-agent validation average |
| Template fit | ≥80% | Template compatibility score |

### 11.2 Performance Targets

| Metric | Target |
|--------|--------|
| Wave 1 completion | < 30 seconds |
| Full generation (standard) | < 2 minutes |
| Full generation (deep) | < 5 minutes |
| Validation phase | < 60 seconds |

---

## 12. Boundaries

### 12.1 Will Do

- ✅ Generate structured roadmaps from specification files
- ✅ Apply multi-agent validation for quality assurance
- ✅ Create milestone-based task breakdowns
- ✅ Integrate with SuperClaude persona and MCP systems
- ✅ Persist session state via Serena memory
- ✅ Support multiple template types

### 12.2 Will Not Do

- ❌ Execute implementation tasks (use `/sc:task` or `/sc:implement`)
- ❌ Make business prioritization decisions
- ❌ Generate roadmaps without specification input
- ❌ Override compliance tier verification without justification
- ❌ Skip validation for STRICT tier operations
- ❌ Write outside designated output directories

---

## 13. Skill Definition (SKILL.md)

**Location**: `.claude/skills/sc-roadmap/SKILL.md`

> **NOTE**: The frontmatter below uses ONLY standard fields that match existing skills in the codebase.
> Extended fields (category, complexity, mcp-servers, personas) are documented in comments but not in frontmatter.

```markdown
---
name: sc:roadmap
description: Generate comprehensive project roadmaps from specification documents
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, TodoWrite, Task
---

# /sc:roadmap - Roadmap Generator

<!-- Extended metadata (for documentation, not parsed):
category: planning
complexity: advanced
mcp-servers: [sequential, context7, serena]
personas: [architect, scribe, analyzer]
-->

## Purpose
Generate deterministic release roadmap packages from specification documents with integrated multi-agent validation.

## Required Input
**MANDATORY**: A specification file path must be provided. The command will not execute without it.

```
/sc:roadmap <spec-file-path>
```

## Triggers
- Explicit: `/sc:roadmap path/to/spec.md`
- Keywords: "generate roadmap", "create roadmap from spec", "roadmap for"

## Usage
```bash
/sc:roadmap path/to/spec.md                     # Basic generation
/sc:roadmap spec.md --template security         # Security-focused
/sc:roadmap spec.md --depth deep --validate     # Comprehensive
/sc:roadmap spec.md --output .roadmaps/v2/      # Custom output
```

## Behavioral Flow
5-wave orchestration:
1. **Wave 1**: Detection & Analysis - Parse spec, activate personas
2. **Wave 2**: Planning & Template Selection - Select template, create task breakdown
3. **Wave 3**: Generation - Generate roadmap.md, tasklists, artifacts
4. **Wave 4**: Validation - Multi-agent quality review (embed agent type in Task prompt)
5. **Wave 5**: Completion - Persist state, finalize outputs

## MCP Integration
- **Sequential**: Wave analysis and validation reasoning
- **Context7**: Template patterns and best practices
- **Serena**: Session persistence and memory

## Outputs
- `roadmap.md` - Master roadmap document
- `extraction.md` - Extracted requirements summary
- `tasklists/M{N}-*.md` - Per-milestone task files
- `test-strategy.md` - Testing approach
- `execution-prompt.md` - Implementation guide

## Boundaries
**Will:**
- Generate structured roadmaps from specification files
- Apply multi-agent validation for quality
- Create milestone-based task breakdowns
- Persist session state via Serena

**Will Not:**
- Execute implementation tasks (use `/sc:task`)
- Generate roadmaps without specification input
- Make business prioritization decisions
- Skip validation for STRICT tier operations
```

---

## Appendix A: Template Structure

### A.1 Feature Release Template

```markdown
---
template: feature-release
version: 1.0
applicable: [new-feature, enhancement, expansion]
personas: [architect, backend, frontend]
estimated-milestones: 4-6
---

# Feature Release Roadmap Template

## Phase 1: Analysis & Design
### Milestone 1.1: Requirements Gathering
### Milestone 1.2: Architecture Design

## Phase 2: Implementation
### Milestone 2.1: Core Development
### Milestone 2.2: Integration

## Phase 3: Testing & Validation
### Milestone 3.1: Unit & Integration Tests
### Milestone 3.2: E2E Validation

## Phase 4: Release & Documentation
### Milestone 4.1: Documentation
### Milestone 4.2: Release Preparation
```

---

## Appendix B: Validation Checklist

### B.1 Pre-Generation Checklist

- [ ] Specification file exists and is readable
- [ ] Specification contains requirements section
- [ ] Output directory is writable
- [ ] Required MCP servers available (fallbacks ready)

### B.2 Post-Generation Checklist

- [ ] All 5 required artifacts generated
- [ ] All spec requirements appear in roadmap
- [ ] All IDs unique and traceable
- [ ] Milestone dependencies are acyclic
- [ ] Validation score ≥ 85%

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| Wave | A distinct phase in the 5-wave orchestration pipeline |
| Extraction | The process of parsing requirements from specification |
| Milestone | A major deliverable grouping in the roadmap |
| Task | An atomic work item within a milestone |
| Compliance Tier | Quality enforcement level (STRICT/STANDARD/LIGHT/EXEMPT) |
| Persona | Specialized behavioral mode from PERSONAS.md |

---

## Appendix D: Implementation-Ready Examples

### D.1 Complete Task Tool Invocation (Correct Pattern)

```yaml
# CORRECT: Embed agent specialization in the prompt parameter
# The Task tool does NOT have a subagent_type parameter

Task:
  description: "Quality validation of roadmap artifacts"
  prompt: |
    You are a quality-engineer agent. Your role is to validate the generated
    roadmap artifacts for completeness, correctness, and consistency.

    ## Artifacts to Review
    - roadmap.md: Master roadmap document
    - extraction.md: Extracted requirements
    - tasklists/: Per-milestone task files

    ## Validation Criteria
    1. **Completeness**: All requirements from spec appear in roadmap
    2. **Correctness**: Milestone ordering is logical and achievable
    3. **Consistency**: IDs are unique and traceable across documents
    4. **Compliance**: Paths follow SuperClaude conventions

    ## Output Format
    Return a JSON object:
    {
      "quality_score": <0-100>,
      "issues": [
        {"severity": "critical|important|minor", "description": "...", "location": "..."}
      ],
      "recommendation": "PASS|REVISE|REJECT",
      "rationale": "..."
    }
```

### D.2 Complete TodoWrite State Transitions

```yaml
# Wave 1: Initialize task tracking
TodoWrite:
  todos:
    - content: "Parse specification file and extract requirements"
      status: in_progress
      activeForm: "Parsing specification"
    - content: "Calculate complexity score"
      status: pending
      activeForm: "Calculating complexity"
    - content: "Activate appropriate personas"
      status: pending
      activeForm: "Activating personas"

# After Wave 1 completion:
TodoWrite:
  todos:
    - content: "Parse specification file and extract requirements"
      status: completed
      activeForm: "Parsing specification"
    - content: "Calculate complexity score"
      status: completed
      activeForm: "Calculating complexity"
    - content: "Activate appropriate personas"
      status: completed
      activeForm: "Activating personas"
    - content: "Select template and create task breakdown"
      status: in_progress
      activeForm: "Selecting template"

# If a task becomes blocked (workaround pattern):
TodoWrite:
  todos:
    - content: "[BLOCKED: waiting for template directory] Generate roadmap.md"
      status: pending
      activeForm: "Generating roadmap (blocked)"
```

### D.3 Sample extraction.md Output

```markdown
# Extraction: Feature Specification Analysis

## Metadata
- Source: specs/auth-system.md
- Generated: 2026-01-26T10:30:00Z
- Generator: /sc:roadmap v1.0

## Extracted Requirements

| ID | Type | Domain | Description | Priority |
|----|------|--------|-------------|----------|
| FR-001 | Functional | security | OAuth2 authentication flow | P0 |
| FR-002 | Functional | backend | Session management service | P1 |
| FR-003 | Functional | frontend | Login/logout UI components | P1 |
| NFR-001 | Non-Functional | security | 99.9% uptime for auth service | P0 |
| NFR-002 | Non-Functional | performance | <200ms auth response time | P1 |

## Domain Distribution
- security: 45%
- backend: 30%
- frontend: 25%

## Complexity Analysis
- Requirement count: 5 (weight: 0.25 → 0.20)
- Dependency depth: Medium (weight: 0.25 → 0.18)
- Domain spread: 3 domains (weight: 0.20 → 0.12)
- Risk severity: High (weight: 0.15 → 0.12)
- Scope size: Medium (weight: 0.15 → 0.10)
- **Total Complexity Score**: 0.72

## Persona Assignment
- **Primary**: security (45% domain coverage, confidence: 92%)
- **Consulting**: backend (30% coverage, confidence: 78%)
- **Fallback**: architect (system-wide coordination)

## Dependencies
- External: OAuth2 provider (Google, GitHub)
- Internal: Database service, Session store (Redis)

## Risks Identified
| Risk ID | Description | Impact | Mitigation |
|---------|-------------|--------|------------|
| R-001 | OAuth provider outage | High | Implement local fallback auth |
| R-002 | Session store latency | Medium | Add caching layer |
```

---

## Appendix E: ID Schema Definition

### E.1 ID Conventions

| ID Type | Pattern | Example | Scope |
|---------|---------|---------|-------|
| Functional Requirement | `FR-{3digits}` | FR-001 | Spec file |
| Non-Functional Req. | `NFR-{3digits}` | NFR-001 | Spec file |
| Milestone | `M{1digit}` | M1, M2 | Roadmap |
| Deliverable | `D{milestone}.{seq}` | D1.1, D2.3 | Milestone |
| Task | `T{milestone}.{seq}` | T1.1, T3.2 | Milestone |
| Risk | `R-{3digits}` | R-001 | Project-wide |

### E.2 ID Uniqueness Rules

- All IDs must be unique within their scope
- Cross-references between documents use fully-qualified IDs
- Format: `{doc-type}:{id}` (e.g., `roadmap:M1`, `tasklist:T1.1`)

---

## Appendix F: Compatibility Matrix

| Dependency | Minimum Version | Notes |
|------------|-----------------|-------|
| SuperClaude Framework | v4.1.9+ | Required for skill system |
| ORCHESTRATOR.md | Compliance tier v1.0 | STRICT/STANDARD/LIGHT/EXEMPT |
| PERSONAS.md | 11-persona system | 85%/70% confidence thresholds |
| MCP.md | Circuit breaker v1.0 | Sequential, Serena, Context7 |
| TodoWrite | 3-state model | pending, in_progress, completed |

---

*Specification generated by /sc:spec-panel*
*Quality Review Score: 78/100 → Issues Addressed in v1.0.1*
*Based on analysis of v.1.4-roadmap-gen documentation*
*Date: 2026-01-26*
