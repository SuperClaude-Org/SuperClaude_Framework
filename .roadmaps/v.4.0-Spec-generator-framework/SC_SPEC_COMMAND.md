# /sc:spec Command Specification

> **Version**: 1.0.0 | **Status**: DRAFT | **Date**: 2026-01-21
> **Integration**: SuperClaude Framework Skill

---

## Command Overview

```yaml
command: "/sc:spec"
category: "Planning & Documentation"
purpose: "AI-powered specification generator with intelligent elicitation"
wave-enabled: true
performance-profile: "standard"
```

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **Complexity Routing** | Auto-detect Quick/Standard/Enterprise track |
| **Intelligent Elicitation** | 3-phase question framework with 95% confidence threshold |
| **Template Rendering** | Modular 4-layer template architecture |
| **Quality Validation** | 8-dimension scoring with 80% minimum threshold |
| **AI Optimization** | EARS notation, context blocks, structured output |

---

## Syntax

```bash
/sc:spec [description] [@input-file] [--options]
```

### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `description` | String | Feature/task description (triggers elicitation) |
| `@input-file` | Path | Existing document to enhance/convert |

### Options

| Option | Short | Values | Default | Description |
|--------|-------|--------|---------|-------------|
| `--track` | `-t` | quick\|standard\|enterprise | auto | Force track selection |
| `--interactive` | `-i` | - | - | Full question flow regardless of confidence |
| `--quick` | `-q` | - | - | Minimal questions, sensible defaults |
| `--output` | `-o` | path | specs/{name}.spec.md | Output file path |
| `--format` | `-f` | md\|yaml\|both | both | Output format |
| `--validate` | `-v` | - | - | Validate existing spec only |
| `--score` | `-s` | - | true | Show quality score |
| `--dry-run` | `-d` | - | - | Preview without writing files |
| `--template` | - | path | default | Custom template path |

---

## Usage Examples

### Basic Usage

```bash
# Simple feature specification
/sc:spec "User authentication with OAuth2"

# With track override
/sc:spec "Bug fix for login timeout" --track quick

# From existing document
/sc:spec @feature-brief.md --track standard

# Interactive mode (full question flow)
/sc:spec "Payment processing system" --interactive

# Quick mode (minimal questions)
/sc:spec "Add loading spinner" --quick
```

### Advanced Usage

```bash
# Enterprise specification with custom output
/sc:spec "GDPR compliance data export" --track enterprise --output specs/compliance/gdpr-export.spec.md

# Validate existing specification
/sc:spec @existing-spec.md --validate

# Dry run to preview
/sc:spec "API rate limiting" --dry-run

# Custom template
/sc:spec "Internal tool" --template .spec-generator/templates/internal.md
```

---

## Workflow Modes

### 1. Guided Mode (`--interactive`)

**Trigger**: `--interactive` flag or complex/ambiguous input

**Behavior**:
- Executes full 3-phase question framework
- Phase 1: Discovery (5 questions)
- Phase 2: Validation (conditional, based on complexity)
- Phase 3: Completion (gap analysis, JTBD)

**Output**: Comprehensive specification with all sections populated

### 2. Smart Mode (Default)

**Trigger**: Default behavior

**Behavior**:
- Analyzes input for confidence scoring
- Questions asked only when confidence < 95%
- Auto-fills high-confidence sections
- Asks for confirmation on key decisions

**Output**: Balanced specification with targeted questions

### 3. Quick Mode (`--quick`)

**Trigger**: `--quick` flag or simple input detected

**Behavior**:
- Minimal questions (0-3)
- Uses sensible defaults extensively
- States assumptions explicitly
- Fast completion

**Output**: Minimal viable specification

### 4. Validate Mode (`--validate`)

**Trigger**: `--validate` flag with existing spec

**Behavior**:
- Parses existing specification
- Applies 8-dimension scoring
- Generates validation report
- Suggests improvements

**Output**: Quality score and recommendations

---

## Question Framework Integration

### Phase 1: Discovery

```yaml
discovery_questions:
  - id: Q1
    question: "Who is the primary user/customer?"
    format: open_with_examples
    confidence_impact: high
    default: "End user of the application"

  - id: Q2
    question: "What specific problem are they facing?"
    format: story
    prompt: "Describe a recent situation where this was a problem"
    confidence_impact: critical

  - id: Q3
    question: "What does success look like?"
    format: measurable_criteria
    confidence_impact: high

  - id: Q4
    question: "What are the key features needed?"
    format: priority_list
    confidence_impact: high

  - id: Q5
    question: "What is explicitly out of scope?"
    format: exclusion_list
    confidence_impact: medium
```

### Phase 2: Validation

```yaml
validation_triggers:
  - unstated_assumption_detected
  - single_stakeholder_perspective
  - claims_without_evidence
  - high_complexity_detected

validation_questions:
  - type: probing_assumptions
    template: "You mentioned {assumption}. What evidence supports this?"

  - type: viewpoint_shift
    template: "How would {stakeholder_role} view this requirement?"

  - type: rabbit_holes
    template: "What parts of this could become unexpectedly complex?"
```

### Phase 3: Completion

```yaml
completion_questions:
  - type: gap_analysis
    questions:
      - "What happens when {edge_case}?"
      - "What error conditions haven't we addressed?"

  - type: jtbd_validation
    questions:
      - "Does this fully address the user's job-to-be-done?"
      - "What current solutions are being 'fired'?"

  - type: meta_review
    questions:
      - "What questions haven't we asked that we should?"
```

---

## Template Selection

### Track Auto-Detection

```yaml
complexity_scoring:
  factors:
    effort_estimate:
      weight: 0.25
      keywords:
        quick: ["bug", "fix", "typo", "update", "minor"]
        standard: ["feature", "integrate", "refactor", "add"]
        enterprise: ["architecture", "compliance", "migration", "security"]

    scope_indicators:
      weight: 0.25
      file_mentions:
        quick: 1-3
        standard: 4-15
        enterprise: 16+

    stakeholder_mentions:
      weight: 0.20
      count:
        quick: 1-2
        standard: 3-5
        enterprise: 6+

    risk_indicators:
      weight: 0.30
      keywords:
        low: ["internal", "non-critical", "experiment"]
        medium: ["customer-facing", "data", "user"]
        high: ["security", "compliance", "production", "critical"]

  thresholds:
    quick: 0-30
    standard: 31-65
    enterprise: 66-100
```

### Template Mapping

| Track | Template | Sections |
|-------|----------|----------|
| Quick | `quick.md` | 5-8 |
| Standard | `standard.md` | 10-12 |
| Enterprise | `enterprise.md` | 15+ |

---

## Output Artifacts

### Primary Output: Specification Document

```
specs/{feature-name}.spec.md

Structure:
├── Metadata header
├── Problem Statement
├── Goals and Non-Goals (standard+)
├── Requirements (EARS format)
├── Solution Design (standard+)
├── Alternatives Considered (standard+)
├── Risk Assessment
├── Success Criteria
├── Tasks (optional)
├── Open Questions
└── AI Context Block
```

### Secondary Output: AI Context

```
specs/{feature-name}.context.yaml

Contents:
├── domain
├── complexity
├── technology
├── agent_profile
├── quality_gates
├── confidence_thresholds
└── parsing_hints
```

### Tertiary Output: Validation Report

```
specs/{feature-name}.score.json

Contents:
├── overall_score
├── dimension_scores (8)
├── warnings
├── recommendations
└── quality_gate_status
```

---

## Quality Validation

### Scoring Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Completeness | 20% | All required sections present |
| Technical Accuracy | 20% | Correct patterns, feasible approach |
| Clarity | 10% | Clear prose, good organization |
| Testability | 15% | EARS format, acceptance criteria |
| Implementability | 15% | Sufficient detail, no ambiguity |
| Resilience | 10% | Error handling, edge cases |
| Security | 5% | Threats addressed |
| Operability | 5% | Monitoring, deployment |

### Quality Gates

| Gate | Threshold | Action |
|------|-----------|--------|
| Draft | 60% | Warning, suggest improvements |
| Review | 70% | Flag gaps before proceeding |
| Approval | 80% | Require explicit override if below |
| Release | 90% | Enterprise track mandatory |

---

## MCP Integration

### Sequential Thinking

Used for:
- Complex question flow orchestration
- Multi-dimensional validation analysis
- Trade-off evaluation

### Context7

Used for:
- Template pattern lookup
- Best practice retrieval
- Documentation standards

### Serena

Used for:
- Session persistence
- Project context loading
- Memory-driven defaults

---

## Persona Auto-Activation

| Context | Persona | MCP |
|---------|---------|-----|
| Feature spec | Architect + Analyzer | Sequential |
| API spec | Backend + Security | Context7 |
| UI spec | Frontend + Architect | Magic + Context7 |
| Infrastructure | DevOps + Architect | Sequential |
| Compliance | Security + Analyzer | Sequential |

---

## Error Handling

### Input Validation

```yaml
validation_rules:
  description:
    min_length: 10
    max_length: 500
    required_unless: "@input-file provided"

  input_file:
    must_exist: true
    extensions: [".md", ".txt", ".yaml"]

  track:
    values: ["quick", "standard", "enterprise"]
    case_insensitive: true
```

### Recovery Strategies

| Error | Recovery |
|-------|----------|
| Input too vague | Trigger interactive mode |
| File not found | Prompt for correct path |
| Template error | Fall back to default |
| Low quality score | Offer iteration loop |
| Question timeout | State assumption, continue |

---

## Configuration

### Project Customization

```yaml
# .spec-generator/customize.yaml

version: "1.0"

defaults:
  track: standard
  output_path: "specs/"
  format: both
  variables:
    PROJECT_NAME: "MyProject"
    TEAM: "Platform"
    DEFAULT_AUTHOR: "$USER"

overrides:
  metadata/spec-header:
    source: custom/company-header.md

tracks:
  enterprise:
    variables:
      REQUIRED_APPROVERS: ["Security", "Architecture", "Legal"]
    additional_sections:
      - custom/compliance-checklist
```

### Global Settings

```yaml
# ~/.superclaude/spec-generator.yaml

question_framework:
  confidence_threshold: 0.95
  max_questions_per_batch: 5
  adaptation_enabled: true

quality:
  minimum_score: 80
  auto_iterate: true
  max_iterations: 3

output:
  include_ai_context: true
  include_tasks: false
  include_score: true
```

---

## Integration with SuperClaude Commands

### Complementary Commands

| Command | Integration |
|---------|-------------|
| `/sc:task` | Generate tasks from spec |
| `/sc:implement` | Implement from spec |
| `/sc:test` | Generate tests from spec |
| `/sc:document` | Expand spec sections |
| `/sc:workflow` | Create roadmap from spec |

### Command Chaining

```bash
# Full workflow
/sc:spec "User auth" → /sc:workflow @spec.md → /sc:task @workflow.md

# Quick implementation
/sc:spec "Fix bug" --quick → /sc:implement @spec.md

# Documentation expansion
/sc:spec @brief.md → /sc:document @spec.md --expand
```

---

## Performance Characteristics

| Metric | Target | Notes |
|--------|--------|-------|
| Quick track | < 30 seconds | Minimal questions |
| Standard track | 1-3 minutes | Smart elicitation |
| Enterprise track | 3-5 minutes | Full workflow |
| Validation only | < 10 seconds | Scoring only |

---

## Changelog

### v1.0.0 (2026-01-21)
- Initial specification
- 3-phase question framework
- 3-track complexity routing
- 4-layer template architecture
- 8-dimension quality scoring
- AI context block generation

---

*Part of the SuperClaude Framework*
*Synthesized from: BMAD-METHOD, Clavix, Kiro, Shape Up, Amazon, Google, IEEE/ISO, AI-Native Research*
