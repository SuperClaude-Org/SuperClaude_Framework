---
name: sc-roadmap
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

Generate deterministic release roadmap packages from specification documents with integrated multi-agent validation. Transforms project requirements, feature descriptions, or PRD files into actionable milestone-based roadmaps.

**Key Differentiator**: Unlike general planning tools, `/sc:roadmap` **requires** a specification file as mandatory input, ensuring roadmaps are grounded in documented requirements rather than ad-hoc descriptions.

## Required Input

**MANDATORY**: A specification file path must be provided. The command will not execute without it.

```
/sc:roadmap <spec-file-path>
```

**Supported Input Formats**:
- Markdown (`.md`) - Primary format
- Text (`.txt`) - Plain text specifications
- YAML (`.yaml`, `.yml`) - Structured requirements
- JSON (`.json`) - API/schema specifications

## Triggers

- Explicit: `/sc:roadmap path/to/spec.md`
- Keywords: "generate roadmap", "create roadmap from spec", "roadmap for"

## Usage

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

## Options

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

## Behavioral Flow

5-wave orchestration architecture:

### Wave 1: Detection & Analysis
- Parse specification file
- Extract requirements, scope, dependencies
- Score complexity (0.0-1.0)
- Activate personas based on domain distribution

### Wave 2: Planning & Template Selection
- Template discovery: local → user → plugin → inline
- Score template compatibility
- Create task breakdown via TodoWrite
- Establish milestone structure

### Wave 3: Generation
- Generate roadmap.md with milestone hierarchy
- Generate tasklist files per milestone
- Generate test-strategy.md
- Generate execution-prompt.md

### Wave 4: Validation (Multi-Agent)
- Task with quality-engineer prompt: Completeness, consistency
- Task with self-review prompt: 4-question validation protocol
- Score aggregation
- Decision: PASS (≥85%) | REVISE (70-84%) | REJECT (<70%)

### Wave 5: Completion
- think_about_whether_you_are_done()
- Memory persistence via Serena
- Git operations (if requested)
- Final output summary

## MCP Integration

- **Sequential**: Wave analysis and validation reasoning
- **Context7**: Template patterns and best practices
- **Serena**: Session persistence and memory

## Outputs (5 Required Artifacts)

| Artifact | Location | Description |
|----------|----------|-------------|
| `roadmap.md` | `<output>/roadmap.md` | Master roadmap document |
| `extraction.md` | `<output>/extraction.md` | Extracted requirements summary |
| `tasklists/M{N}-*.md` | `<output>/tasklists/` | Per-milestone task files |
| `test-strategy.md` | `<output>/test-strategy.md` | Testing and validation approach |
| `execution-prompt.md` | `<output>/execution-prompt.md` | Implementation instructions |

## Boundaries

### Will Do
- Generate structured roadmaps from specification files
- Apply multi-agent validation for quality assurance
- Create milestone-based task breakdowns
- Integrate with SuperClaude persona and MCP systems
- Persist session state via Serena memory
- Support multiple template types

### Will Not Do
- Execute implementation tasks (use `/sc:task` or `/sc:implement`)
- Make business prioritization decisions
- Generate roadmaps without specification input
- Override compliance tier verification without justification
- Skip validation for STRICT tier operations
- Write outside designated output directories

## Compliance Tier Classification

Default tier: **STANDARD** with automatic escalation to **STRICT** when:
- Complexity score > 0.8
- Security-related requirements detected
- Multi-domain scope (>3 domains)
- User specifies `--compliance strict`

## Related Commands

| Command | Integration | Usage |
|---------|-------------|-------|
| `/sc:task` | Execute roadmap tasks | `/sc:task "Implement M1 tasks"` |
| `/sc:implement` | Build roadmap features | `/sc:implement @roadmap.md M1.1` |
| `/sc:analyze` | Review roadmap quality | `/sc:analyze @roadmap.md --focus quality` |
| `/sc:improve` | Enhance roadmap | `/sc:improve @roadmap.md` |

---

## Implementation Details

### Wave 1: Detection & Analysis (Full Implementation)

#### T2.1: Specification File Validation

**Step 1: File Existence Check**
```yaml
validation_step_1:
  action: "Use Read tool to access specification file"
  on_success: "Proceed to step 2"
  on_failure:
    action: STOP
    message: "Specification file not found: <path>"
```

**Step 2: File Readability Validation**
```yaml
validation_step_2:
  action: "Check content length > 0"
  on_success: "Proceed to step 3"
  on_failure:
    action: STOP
    message: "Specification file is empty"
```

**Step 3: Minimum Content Check**
```yaml
validation_step_3:
  action: "Verify content length > 100 characters"
  on_success: "Proceed to step 4"
  on_failure:
    action: WARN
    message: "Specification file has minimal content, proceeding with caution"
```

**Step 4: Required Section Detection**
```yaml
validation_step_4:
  action: "Scan for title (H1 heading) and requirements section"
  title_detection:
    primary: "# <Title>" pattern (H1 heading)
    fallback: "Extract from filename if no H1 found"
  requirements_detection:
    patterns:
      - "## Requirements"
      - "## Functional Requirements"
      - "## FR-"
      - "## NFR-"
      - "- FR-XXX:"
      - "- NFR-XXX:"
  on_no_requirements:
    action: STOP
    message: "No requirements found in specification"
```

**Error Messages (per spec Section 8.1)**:
- File not found: `"Specification file not found: <path>"`
- Empty file: `"Specification file is empty"`
- No requirements: `"No requirements found in specification"`

---

#### T2.2: Requirements Extraction Engine

**Extraction Pipeline**:
```yaml
extraction_pipeline:
  step_1_title:
    action: "Extract title from H1 heading"
    pattern: "^# (.+)$"
    fallback: "Use filename without extension"
    output: "title"

  step_2_functional_requirements:
    action: "Extract FR-XXX patterns"
    patterns:
      - "FR-\\d{3}:\\s*(.+)"
      - "- FR-\\d{3}:\\s*(.+)"
      - "\\| FR-\\d{3} \\|"
    output: "functional_requirements[]"
    id_format: "FR-XXX"

  step_3_nonfunctional_requirements:
    action: "Extract NFR-XXX patterns"
    patterns:
      - "NFR-\\d{3}:\\s*(.+)"
      - "- NFR-\\d{3}:\\s*(.+)"
      - "\\| NFR-\\d{3} \\|"
    output: "nonfunctional_requirements[]"
    id_format: "NFR-XXX"

  step_4_scope_boundaries:
    action: "Extract In Scope / Out of Scope sections"
    in_scope_patterns:
      - "### In Scope"
      - "## In Scope"
      - "**In Scope**"
    out_scope_patterns:
      - "### Out of Scope"
      - "## Out of Scope"
      - "**Out of Scope**"
    output: "scope_boundaries"

  step_5_dependencies:
    action: "Extract dependencies section"
    patterns:
      - "## Dependencies"
      - "### Dependencies"
      - "**Dependencies**:"
    output: "dependencies[]"

  step_6_success_criteria:
    action: "Extract success criteria"
    patterns:
      - "## Success Criteria"
      - "### Success Criteria"
      - "- \\[ \\] (.+)"
    output: "success_criteria[]"

  step_7_risks:
    action: "Extract risks and mitigations"
    patterns:
      - "## Risks"
      - "## Risks & Mitigations"
      - "\\| Risk \\|"
    output: "risks[]"

  step_8_assign_ids:
    action: "Ensure all extracted items have unique IDs"
    id_assignment:
      requirements_without_id: "Assign FR-XXX or NFR-XXX sequentially"
      dependencies: "Assign DEP-XXX"
      risks: "Assign R-XXX"
    output: "all_items_with_ids"
```

**Output**: `extraction.md` with structured data

---

#### T2.3: Domain Analysis Classifier

**Domain Keywords (per spec Section 3.2)**:
```yaml
domain_keywords:
  frontend:
    keywords: [UI, components, UX, accessibility, responsive, React, Vue, Angular, CSS, HTML, component, layout, design, user interface, form, button, modal]
    weight: 1.0

  backend:
    keywords: [API, database, services, infrastructure, server, endpoint, REST, GraphQL, microservices, authentication, middleware, controller, model, repository]
    weight: 1.0

  security:
    keywords: [auth, encryption, compliance, vulnerabilities, tokens, OAuth, JWT, RBAC, permissions, audit, penetration, OWASP, security, authorization, credentials]
    weight: 1.2

  performance:
    keywords: [optimization, caching, scaling, latency, throughput, CDN, load balancing, profiling, benchmark, memory, CPU, response time]
    weight: 1.0

  documentation:
    keywords: [guides, references, migration, docs, README, wiki, tutorial, manual, specification, documentation]
    weight: 0.8
```

**Classification Algorithm**:
```yaml
classification_algorithm:
  step_1: "Concatenate all extracted text (requirements, scope, dependencies)"
  step_2: "For each domain, count keyword occurrences (case-insensitive)"
  step_3: "Apply keyword weights"
  step_4: "Calculate percentage distribution"
  step_5: "Normalize to 100%"

  formula: |
    domain_score[d] = sum(keyword_count[k] * weight[d]) for k in domain_keywords[d]
    total_score = sum(domain_score[d]) for all d
    domain_percentage[d] = (domain_score[d] / total_score) * 100

  output:
    domain_distribution:
      frontend: "XX%"
      backend: "XX%"
      security: "XX%"
      performance: "XX%"
      documentation: "XX%"
```

---

#### T2.4: Complexity Scoring System

**Complexity Factors (per spec Section 3.2)**:
```yaml
complexity_factors:
  requirement_count:
    weight: 0.25
    scoring:
      1-5: 0.2
      6-10: 0.4
      11-20: 0.6
      21-35: 0.8
      36+: 1.0

  dependency_depth:
    weight: 0.25
    scoring:
      none: 0.1
      1-2: 0.3
      3-5: 0.5
      6-10: 0.7
      11+: 1.0

  domain_spread:
    weight: 0.20
    scoring:
      1_domain: 0.2
      2_domains: 0.4
      3_domains: 0.6
      4_domains: 0.8
      5_domains: 1.0

  risk_severity:
    weight: 0.15
    scoring:
      no_risks: 0.1
      low_risks_only: 0.3
      medium_risks: 0.5
      high_risks: 0.7
      critical_risks: 1.0

  scope_size:
    weight: 0.15
    scoring:
      small: 0.2
      medium: 0.4
      large: 0.6
      xlarge: 0.8
      massive: 1.0
```

**Scoring Formula**:
```yaml
complexity_formula:
  calculation: |
    score = (req_count_score * 0.25) +
            (dep_depth_score * 0.25) +
            (domain_spread_score * 0.20) +
            (risk_sev_score * 0.15) +
            (scope_size_score * 0.15)

  normalization: "Score is already 0.0-1.0 scale"

  classification:
    LOW: "score < 0.4"
    MEDIUM: "0.4 <= score <= 0.7"
    HIGH: "score > 0.7"

  output:
    complexity_score: 0.XX
    complexity_classification: "LOW|MEDIUM|HIGH"
```

---

#### T2.5: Persona Auto-Activation

**Activation Rules (per spec Section 3.2)**:
```yaml
persona_activation_rules:
  primary_persona:
    threshold: "Domain >= 40% coverage"
    confidence: ">= 85%"
    selection: "Domain with highest qualifying coverage"

  consulting_personas:
    threshold: "Domain >= 15% coverage"
    confidence: ">= 70%"
    selection: "All domains meeting threshold"

  fallback:
    condition: "No domain reaches 40%"
    action: "Activate architect persona"
    rationale: "System-wide concerns require architect oversight"
```

**Persona-Domain Mapping**:
```yaml
persona_domain_mapping:
  frontend:
    persona: "frontend"
    capabilities: [UI, components, UX, accessibility]

  backend:
    persona: "backend"
    capabilities: [API, database, services]

  security:
    persona: "security"
    capabilities: [auth, encryption, compliance]

  performance:
    persona: "performance"
    capabilities: [optimization, caching, scaling]

  documentation:
    persona: "scribe"
    capabilities: [guides, references, documentation]
```

**Confidence Calculation**:
```yaml
confidence_calculation:
  formula: |
    base_confidence = domain_percentage / max_expected_coverage * 100
    specificity_boost = unique_domain_keywords / total_keywords * 10
    confidence = min(base_confidence + specificity_boost, 100)

  thresholds:
    primary_activation: 85
    consulting_activation: 70
```

**Output Format**:
```yaml
persona_assignment:
  primary:
    persona: "<persona_name>"
    domain_coverage: "XX%"
    confidence: "XX%"
    rationale: "X% of items are <DOMAIN> work"

  consulting:
    - persona: "<persona_name>"
      domain_coverage: "XX%"
      confidence: "XX%"

  fallback_used: true|false
  fallback_reason: "<reason if fallback used>"
```

---

### Wave 1 Output: extraction.md

**Template**:
```markdown
# Extraction: <Specification Title>

## Metadata
- Source: <spec-file-path>
- Generated: <timestamp>
- Generator: /sc:roadmap v1.0

## Extracted Requirements

| ID | Type | Domain | Description | Priority |
|----|------|--------|-------------|----------|
| FR-001 | Functional | <domain> | <description> | P0-P3 |
| NFR-001 | Non-Functional | <domain> | <description> | P0-P3 |

## Domain Distribution
- frontend: XX%
- backend: XX%
- security: XX%
- performance: XX%
- documentation: XX%

## Complexity Analysis
- Requirement count: X (score: 0.XX)
- Dependency depth: X (score: 0.XX)
- Domain spread: X domains (score: 0.XX)
- Risk severity: <level> (score: 0.XX)
- Scope size: <size> (score: 0.XX)
- **Total Complexity Score**: 0.XX (<LOW|MEDIUM|HIGH>)

## Persona Assignment
- **Primary**: <persona> (<XX%> domain coverage, confidence: <XX%>)
- **Consulting**: <persona1>, <persona2>
- **Fallback**: <architect if used>

## Dependencies
- <dependency_1>
- <dependency_2>

## Risks Identified
| Risk ID | Description | Impact | Mitigation |
|---------|-------------|--------|------------|
| R-001 | <description> | <impact> | <mitigation> |

## Success Criteria
- [ ] <criterion_1>
- [ ] <criterion_2>
```

---

*Skill definition for SuperClaude Framework v4.2.0+*
*Based on SC-ROADMAP-FEATURE-SPEC.md v1.1.0*
