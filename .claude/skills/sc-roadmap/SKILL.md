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

### Wave 0: Prerequisites
**Purpose**: Validate environment readiness before main workflow execution

```yaml
wave_0_prerequisites:
  step_1_template_directory:
    action: "Check template directory existence"
    paths:
      - "./templates/roadmaps/"
      - "~/.claude/templates/roadmaps/"
      - "plugins/superclaude/templates/roadmaps/"
    on_found: "Log template source, proceed to step 2"
    on_not_found: "Log warning: 'No template directories found, will use inline generation'"

  step_2_output_directory:
    action: "Validate output directory"
    default: ".roadmaps/<spec-name>/"
    checks:
      - "Parent directory exists"
      - "Path is writable"
    on_failure:
      action: STOP
      message: "Cannot create output directory: <path>"

  step_3_permissions:
    action: "Verify write permissions"
    targets:
      - "Output directory"
      - "Tasklist subdirectory"
    on_failure:
      action: STOP
      message: "Insufficient permissions for: <path>"

  step_4_fallback_logging:
    action: "Log fallback decisions"
    conditions:
      - template_fallback: "Log: 'Using inline template generation (no matching template)'"
      - permission_warning: "Log: 'Limited permissions detected, some features disabled'"
    proceed: "Wave 1"

  entry_criteria:
    - "Specification file path provided"
    - "Claude Code session active"

  exit_criteria:
    - "Template source identified (directory or inline)"
    - "Output directory validated and writable"
    - "All prerequisites logged"
```

---

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

#### Inline Template Generation Fallback
When no matching template is found, generate inline using this algorithm:

```yaml
inline_template_generation:
  milestone_count_selection:
    complexity_low: # score < 0.4
      range: 3-4 milestones
      typical: "Analysis → Implementation → Testing → Release"
    complexity_medium: # 0.4 <= score <= 0.7
      range: 4-6 milestones
      typical: "Analysis → Design → Implementation → Testing → Integration → Release"
    complexity_high: # score > 0.7
      range: 5-8 milestones
      typical: "Discovery → Design → Core Implementation → Extended Features → Testing → Integration → Validation → Release"

  domain_milestone_mapping:
    frontend_primary: # frontend >= 40%
      required_milestone: "UX Validation"
      focus: "User experience testing, accessibility audit"
    backend_primary: # backend >= 40%
      required_milestone: "API Specification"
      focus: "Contract definition, integration planning"
    security_primary: # security >= 40%
      required_milestone: "Security Audit"
      focus: "Threat modeling, vulnerability assessment"
    performance_primary: # performance >= 40%
      required_milestone: "Performance Baseline"
      focus: "Benchmarking, optimization targets"

  required_sections_per_milestone:
    - "Objective: Clear milestone goal"
    - "Type: FEATURE|IMPROVEMENT|DOC|TEST"
    - "Priority: P0-Critical|P1-High|P2-Medium|P3-Low"
    - "Deliverables: D{M}.{D}.{N} format"
    - "Dependencies: M{N} references"
    - "Acceptance_Criteria: Measurable outcomes"
    - "Risk_Level: Low|Medium|High"
    - "Files_Affected: Path patterns or TBD"

  reference: "See SC-ROADMAP-FEATURE-SPEC.md v1.1.0 Section 3.3.1 for edge cases and advanced scenarios"
```

#### Template Discovery Details

```yaml
template_discovery:
  search_order:
    - path: "./templates/roadmaps/"
      glob: "*.md"
      priority: 1
      description: "Local project templates (highest priority)"

    - path: "~/.claude/templates/roadmaps/"
      glob: "{type}-*.md"
      priority: 2
      description: "User templates (personal customizations)"

    - path: "plugins/superclaude/templates/roadmaps/"
      glob: "*.md"
      priority: 3
      description: "Plugin templates (framework defaults)"

    - path: "inline"
      condition: "No matching template found in any directory"
      priority: 4
      description: "Generated variant (fallback)"

  version_resolution:
    explicit: "Use exact version if --template-version specified"
    semantic: "Select latest by semantic versioning (1.2.0 > 1.1.9)"
    default: "First matching template in priority order"

  matching_criteria:
    - "frontmatter.applicable contains detected domain"
    - "frontmatter.template matches --template flag if provided"
    - "File exists and is readable"

  fallback_conditions:
    - "No templates in any search path → inline generation"
    - "No domain match → use generic template or inline"
    - "Template parse error → skip, try next in order"
```

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

### TodoWrite State Reference

| State | Meaning | Usage |
|-------|---------|-------|
| `pending` | Ready for execution | Initial state for new tasks |
| `in_progress` | Currently active | Only ONE task should be in_progress at a time |
| `completed` | Successfully finished | Mark when task is done |

#### Blocked Task Workaround
Since TodoWrite does not support a "blocked" state, use the content prefix pattern:

```yaml
# CORRECT - Use pending with prefix
- content: "[BLOCKED: waiting for API docs] Implement authentication"
  status: pending
  activeForm: "Implementing authentication (blocked on API docs)"

# State transitions for blocked tasks
blocked_workflow:
  1. Create task with [BLOCKED: reason] prefix
  2. Set status: pending (NOT in_progress)
  3. When unblocked: Remove prefix, set in_progress
  4. Complete normally when done
```

#### Anti-Patterns (Avoid)
```yaml
# WRONG - Invalid state
status: blocked  # Will fail! Not a valid TodoWrite state

# WRONG - Blocked task marked active
- content: "[BLOCKED: ...] Task"
  status: in_progress  # Don't mark blocked tasks as active

# WRONG - Multiple in_progress
# Only ONE task should be in_progress at any time
```

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

### Wave 2 Implementation Details

#### T3.1: Template Discovery Hierarchy

**Discovery Process**:
```yaml
template_discovery_process:
  step_1_local_search:
    action: "Check ./templates/roadmaps/ for *.md files"
    tool: "Glob with pattern ./templates/roadmaps/*.md"
    on_found:
      - "Parse frontmatter for 'applicable' field"
      - "Match against detected domains from Wave 1"
      - "Log: 'Found local template: <filename>'"
    on_not_found: "Proceed to step 2"

  step_2_user_search:
    action: "Check ~/.claude/templates/roadmaps/ for {type}-*.md"
    tool: "Glob with pattern ~/.claude/templates/roadmaps/*.md"
    expansion: "Expand ~ to user home directory"
    on_found:
      - "Parse frontmatter"
      - "Match against domains"
      - "Log: 'Found user template: <filename>'"
    on_not_found: "Proceed to step 3"

  step_3_plugin_search:
    action: "Check plugins/superclaude/templates/roadmaps/ for *.md"
    tool: "Glob with pattern plugins/superclaude/templates/roadmaps/*.md"
    expected_templates:
      - "feature-release.md"
      - "quality-release.md"
      - "documentation-release.md"
      - "security-release.md"
      - "performance-release.md"
      - "migration-release.md"
    on_found:
      - "Parse frontmatter"
      - "Match 'applicable' against domains"
      - "Log: 'Found plugin template: <filename>'"
    on_not_found: "Proceed to step 4"

  step_4_inline_fallback:
    action: "Generate template inline"
    trigger: "No matching template in any path"
    log: "WARN: No matching template found, generating inline variant"
    process: "See T3.3 Inline Template Generation"

  discovery_output:
    template_path: "<path to selected template or 'inline'>"
    discovery_log: "Array of search steps and results"
    match_reason: "Why this template was selected"
```

---

#### T3.2: Template Scoring Algorithm

**Scoring Factors** (per spec Section 3.3):
```yaml
template_scoring:
  factors:
    domain_alignment:
      weight: 0.40  # 40%
      calculation: |
        matching_domains = intersection(template.applicable, spec.domains)
        primary_match = template.applicable contains spec.primary_domain
        score = (len(matching_domains) / len(template.applicable)) * 0.7
        score += 0.3 if primary_match else 0
      max_score: 1.0

    structure_fit:
      weight: 0.30  # 30%
      calculation: |
        milestone_count_diff = abs(template.milestones - spec.estimated_milestones)
        phase_alignment = template.phases overlap with spec.required_phases
        score = 1.0 - (milestone_count_diff * 0.1)  # -10% per milestone difference
        score = max(score, 0)  # Floor at 0
      max_score: 1.0

    complexity_match:
      weight: 0.20  # 20%
      calculation: |
        template_range = template.estimated_milestones (e.g., "4-6")
        spec_complexity = spec.complexity_score
        # Map complexity to expected milestone range
        expected = complexity_to_range(spec_complexity)
        overlap = range_overlap(template_range, expected)
        score = overlap / max(len(template_range), len(expected))
      max_score: 1.0

    optional_section_relevance:
      weight: 0.10  # 10%
      calculation: |
        template_sections = template.optional_sections
        spec_needs = spec.detected_optional_needs
        relevant = intersection(template_sections, spec_needs)
        score = len(relevant) / max(len(template_sections), 1)
      max_score: 1.0

  final_score:
    formula: |
      total = (domain_alignment * 0.40) +
              (structure_fit * 0.30) +
              (complexity_match * 0.20) +
              (optional_relevance * 0.10)
    range: "0.0 - 1.0"

  threshold_logic:
    high_match: # score >= 0.80
      action: "Select template directly"
      log: "Template '<name>' selected with score <XX>%"

    moderate_match: # 0.60 <= score < 0.80
      action: "Create variant with adjustments"
      adjustments:
        - "Add missing domain-specific milestones"
        - "Adjust milestone count to match complexity"
        - "Include optional sections based on spec needs"
      log: "Template '<name>' selected with adjustments (score: <XX>%)"

    low_match: # score < 0.60
      action: "Prefer inline generation"
      log: "No suitable template (best score: <XX>%), using inline generation"

  output:
    selected_template: "<template name or 'inline'>"
    score: 0.XX
    score_breakdown:
      domain_alignment: 0.XX
      structure_fit: 0.XX
      complexity_match: 0.XX
      optional_relevance: 0.XX
    adjustments_needed: ["<adjustment_1>", "<adjustment_2>"]
    rationale: "<human-readable selection reason>"
```

---

#### T3.3: Inline Template Generation

**Milestone Count Formula** (per spec Section 3.3.1):
```yaml
milestone_count_algorithm:
  base_formula: |
    # Step 1: Calculate base count from requirements
    base_count = 3  # Minimum milestones

    # Step 2: Add milestones for requirement volume
    requirement_bonus = floor((requirement_count - 5) / 5)
    # Every 5 requirements beyond 5 adds 1 milestone

    # Step 3: Add milestone for domain spread
    domain_bonus = 1 if domain_spread > 2 else 0

    # Step 4: Sum
    raw_count = base_count + requirement_bonus + domain_bonus

  complexity_clamping:
    LOW:  # score < 0.4
      range: [3, 4]
      action: "clamp(raw_count, 3, 4)"

    MEDIUM:  # 0.4 <= score <= 0.7
      range: [4, 6]
      action: "clamp(raw_count, 4, 6)"

    HIGH:  # score > 0.7
      range: [5, 8]
      action: "clamp(raw_count, 5, 8)"

  examples:
    - input: {requirements: 8, domains: 2, complexity: 0.35}
      calculation: "base(3) + req_bonus(0) + domain_bonus(0) = 3, clamped to [3,4] = 3"
      output: 3

    - input: {requirements: 15, domains: 3, complexity: 0.55}
      calculation: "base(3) + req_bonus(2) + domain_bonus(1) = 6, clamped to [4,6] = 6"
      output: 6

    - input: {requirements: 25, domains: 4, complexity: 0.82}
      calculation: "base(3) + req_bonus(4) + domain_bonus(1) = 8, clamped to [5,8] = 8"
      output: 8

base_milestone_names:
  LOW_complexity:
    - "M1: Requirements Analysis"
    - "M2: Implementation"
    - "M3: Testing & Release"
    - "M4: Documentation"  # Optional, only if 4 milestones

  MEDIUM_complexity:
    - "M1: Discovery & Planning"
    - "M2: Core Implementation"
    - "M3: Extended Features"
    - "M4: Testing & Validation"
    - "M5: Integration"
    - "M6: Release & Documentation"

  HIGH_complexity:
    - "M1: Discovery & Analysis"
    - "M2: Architecture Design"
    - "M3: Foundation Implementation"
    - "M4: Core Features"
    - "M5: Extended Features"
    - "M6: Integration & Testing"
    - "M7: Validation & QA"
    - "M8: Release & Stabilization"

domain_milestone_mapping:
  single_primary:  # One domain >= 40%
    action: "Add 1 domain-specific milestone"
    mappings:
      frontend: "UX Validation"
      backend: "API Specification"
      security: "Security Audit"
      performance: "Performance Baseline"
      documentation: "Documentation Review"
    insertion: "After M1 (planning) phase"

  multi_primary:  # Multiple domains >= 40%
    action: "Add max 2 domain-specific milestones"
    priority_order: [security, backend, frontend, performance, documentation]
    selection: "Top 2 by coverage percentage"
    insertion: "Interleaved based on logical dependencies"

  no_primary:  # No domain reaches 40%
    action: "Use generic milestones + WARN"
    warning: "WARN: No dominant domain detected, using generic milestone structure"
    generic_milestone: "Cross-Domain Integration"

required_sections_per_milestone:
  mandatory:
    - "**Objective**: Clear, measurable goal"
    - "**Type**: FEATURE | IMPROVEMENT | DOC | TEST"
    - "**Priority**: P0-Critical | P1-High | P2-Medium | P3-Low"
    - "**Deliverables**: D{M}.{D}.{N} format items"
    - "**Dependencies**: M{N} references or 'None'"
    - "**Acceptance_Criteria**: Bullet list of measurable outcomes"
    - "**Risk_Level**: Low | Medium | High"
    - "**Files_Affected**: Path patterns or 'TBD'"

  optional:
    - "**Notes**: Additional context"
    - "**Alternatives**: Other approaches considered"
    - "**Blockers**: Known impediments"
```

---

#### T3.4: TodoWrite Task Initialization

**Initialization Process**:
```yaml
todowrite_initialization:
  purpose: "Create task tracking for roadmap generation workflow"

  valid_states:
    - pending: "Ready for execution, not yet started"
    - in_progress: "Currently being worked on (MAX ONE at a time)"
    - completed: "Successfully finished"

  CRITICAL_RULE: |
    There is NO "blocked" state in TodoWrite.
    Never use status: blocked - it will cause errors.

  blocked_workaround:
    pattern: "[BLOCKED: <reason>] <task description>"
    state: "pending"  # Always pending, NOT in_progress
    activeForm: "<task description> (blocked on <reason>)"
    example:
      content: "[BLOCKED: waiting for security review] Implement authentication middleware"
      status: pending
      activeForm: "Implementing authentication (blocked)"

  initialization_template:
    wave_2_tasks:
      - content: "Discover and score templates"
        status: in_progress  # First task active
        activeForm: "Discovering templates"

      - content: "Select or generate template"
        status: pending
        activeForm: "Selecting template"

      - content: "Create milestone structure"
        status: pending
        activeForm: "Creating milestones"

      - content: "Initialize task breakdown"
        status: pending
        activeForm: "Initializing tasks"

  state_transitions:
    start_task:
      - "Set current task to in_progress"
      - "Ensure NO other task is in_progress"

    complete_task:
      - "Set current task to completed"
      - "Set next pending task to in_progress"

    block_task:
      - "Prepend [BLOCKED: reason] to content"
      - "Keep status as pending"
      - "Move to next available task"

    unblock_task:
      - "Remove [BLOCKED: reason] prefix"
      - "Set to in_progress if ready to execute"

  validation_checks:
    - "Exactly ONE task in_progress at any time"
    - "No task has status 'blocked'"
    - "All blocked items use prefix pattern"
    - "All tasks have content and status fields"

  error_handling:
    invalid_state_error:
      cause: "Attempting to use status: blocked"
      fix: "Use [BLOCKED: reason] prefix with status: pending"

    multiple_active_error:
      cause: "More than one task in_progress"
      fix: "Set all but current task to pending"
```

---

### Wave 2 Output: Milestone Structure

**Template**:
```yaml
wave_2_output:
  template_selection:
    source: "<local|user|plugin|inline>"
    path: "<path or 'generated'>"
    score: 0.XX
    adjustments: ["<adj_1>", "<adj_2>"]

  milestone_structure:
    count: X
    complexity_classification: "<LOW|MEDIUM|HIGH>"
    domain_milestones_added: ["<milestone_1>"]

    milestones:
      - id: "M1"
        name: "<milestone name>"
        type: "FEATURE|IMPROVEMENT|DOC|TEST"
        priority: "P0|P1|P2|P3"
        dependencies: []
        deliverables: ["D1.1.1", "D1.1.2"]

      # ... additional milestones

  todowrite_state:
    total_tasks: X
    pending: X
    in_progress: 1
    completed: 0
    blocked_items: X  # Count of [BLOCKED:] prefixed items
```

---

### Wave 3 Implementation Details (Artifact Generation)

#### T4.1: roadmap.md Generator

**Generation Process**:
```yaml
roadmap_generator:
  output_file: "<output_dir>/roadmap.md"

  sections:
    section_1_metadata:
      content: |
        ---
        title: "<Specification Title> Roadmap"
        source: "<spec-file-path>"
        generated: "<ISO-8601 timestamp>"
        generator: "/sc:roadmap v1.0"
        ---
      data_source: "Wave 1 extraction"

    section_2_executive_summary:
      template: |
        ## Executive Summary

        This roadmap implements **<title>** with **<milestone_count>** milestones
        targeting **<primary_domain>** domain. Complexity: **<complexity_level>**.

        **Key Deliverables**: <deliverable_count> deliverables across <milestone_count> phases.
        **Estimated Scope**: <scope_description>
        **Primary Persona**: <persona_name> (<confidence>% confidence)
      data_source: "Wave 1 complexity and persona analysis"

    section_3_persona_assignment:
      template: |
        ## Persona Assignment

        | Role | Persona | Coverage | Confidence |
        |------|---------|----------|------------|
        | Primary | <persona> | <XX>% | <XX>% |
        | Consulting | <persona1>, <persona2> | <XX>% | <XX>% |
      data_source: "Wave 1 T2.5 persona activation"

    section_4_milestones_overview:
      template: |
        ## Milestones Overview

        | ID | Name | Type | Priority | Dependencies | Risk |
        |----|------|------|----------|--------------|------|
        | M1 | <name> | <type> | <priority> | None | <risk> |
        | M2 | <name> | <type> | <priority> | M1 | <risk> |
      data_source: "Wave 2 milestone structure"

    section_5_milestone_details:
      per_milestone:
        template: |
          ## M<N>: <Milestone Name>

          **Objective**: <clear_objective>
          **Type**: <FEATURE|IMPROVEMENT|DOC|TEST>
          **Priority**: <P0-Critical|P1-High|P2-Medium|P3-Low>
          **Dependencies**: <M{N} list or "None">
          **Risk Level**: <Low|Medium|High>

          ### Deliverables

          | ID | Type | Description | Acceptance Criteria | Files Affected |
          |----|------|-------------|---------------------|----------------|
          | D<M>.<N> | <type> | <description> | <criteria> | <paths> |

    section_6_dependency_graph:
      format: "mermaid"
      template: |
        ## Dependency Graph

        ```mermaid
        graph LR
            M1[M1: Foundation] --> M2[M2: Core]
            M2 --> M3[M3: Features]
            M2 --> M4[M4: Testing]
            M3 --> M5[M5: Release]
            M4 --> M5
        ```
      fallback: "ASCII art if mermaid unsupported"

    section_7_risk_register:
      template: |
        ## Risk Register

        | Risk ID | Description | Probability | Impact | Mitigation | Owner |
        |---------|-------------|-------------|--------|------------|-------|
        | R-001 | <description> | <Low/Med/High> | <Low/Med/High> | <strategy> | <persona> |
      data_source: "Wave 1 extraction risks"

    section_8_success_criteria:
      template: |
        ## Success Criteria

        - [ ] All milestones completed with acceptance criteria met
        - [ ] All deliverables produced and validated
        - [ ] Quality score ≥85/100
        - [ ] No HIGH severity issues remaining
        - [ ] Documentation complete

  id_schema:
    milestones: "M{1digit}"  # M1, M2, ... M9
    deliverables: "D{milestone}.{seq}"  # D1.1, D1.2, D2.1
    tasks: "T{milestone}.{seq}"  # T1.1, T1.2, T2.1
    risks: "R-{3digits}"  # R-001, R-002
```

---

#### T4.2: extraction.md Generator

**Generation Process**:
```yaml
extraction_generator:
  output_file: "<output_dir>/extraction.md"
  data_source: "Wave 1 analysis results"

  sections:
    section_1_metadata:
      template: |
        # Extraction: <Specification Title>

        ## Metadata
        - **Source**: <spec-file-path>
        - **Generated**: <ISO-8601 timestamp>
        - **Generator**: /sc:roadmap v1.0
        - **Extraction Version**: 1.0

    section_2_executive_summary:
      template: |
        ## Executive Summary

        Extracted **<FR_count>** functional requirements and **<NFR_count>** non-functional
        requirements from specification. Primary domain: **<primary_domain>** (<XX>%).
        Complexity score: **<score>** (<classification>).

    section_3_requirements_table:
      template: |
        ## Extracted Requirements

        | ID | Type | Domain | Description | Priority | Dependencies |
        |----|------|--------|-------------|----------|--------------|
        | FR-001 | Functional | <domain> | <description> | <P0-P3> | <deps> |
        | NFR-001 | Non-Functional | <domain> | <description> | <P0-P3> | <deps> |
      data_source: "T2.2 extraction pipeline output"

    section_4_domain_distribution:
      template: |
        ## Domain Distribution

        | Domain | Percentage | Keyword Hits | Classification |
        |--------|------------|--------------|----------------|
        | frontend | <XX>% | <count> | <Primary/Consulting/None> |
        | backend | <XX>% | <count> | <Primary/Consulting/None> |
        | security | <XX>% | <count> | <Primary/Consulting/None> |
        | performance | <XX>% | <count> | <Primary/Consulting/None> |
        | documentation | <XX>% | <count> | <Primary/Consulting/None> |

        **Primary Domain Threshold**: ≥40%
        **Consulting Threshold**: ≥15%
      data_source: "T2.3 domain classification output"

    section_5_complexity_analysis:
      template: |
        ## Complexity Analysis

        | Factor | Value | Score | Weight | Weighted |
        |--------|-------|-------|--------|----------|
        | Requirement Count | <X> | <0.XX> | 0.25 | <0.XX> |
        | Dependency Depth | <X> | <0.XX> | 0.25 | <0.XX> |
        | Domain Spread | <X> | <0.XX> | 0.20 | <0.XX> |
        | Risk Severity | <level> | <0.XX> | 0.15 | <0.XX> |
        | Scope Size | <size> | <0.XX> | 0.15 | <0.XX> |
        | **Total** | | | **1.00** | **<0.XX>** |

        **Classification**: <LOW|MEDIUM|HIGH>
      data_source: "T2.4 complexity scoring output"

    section_6_persona_assignment:
      template: |
        ## Persona Assignment

        **Primary**: <persona_name>
        - Domain Coverage: <XX>%
        - Confidence: <XX>%
        - Rationale: "<X>% of items are <DOMAIN> work"

        **Consulting**: <persona1>, <persona2>

        **Fallback Used**: <Yes/No>
        **Fallback Reason**: <reason if applicable>
      data_source: "T2.5 persona activation output"

    section_7_dependencies:
      template: |
        ## Dependencies Identified

        | ID | Type | Description | Impact |
        |----|------|-------------|--------|
        | DEP-001 | External | <description> | <impact> |
        | DEP-002 | Internal | <description> | <impact> |

    section_8_risks:
      template: |
        ## Risks Identified

        | Risk ID | Description | Impact | Probability | Mitigation |
        |---------|-------------|--------|-------------|------------|
        | R-001 | <description> | <High/Med/Low> | <High/Med/Low> | <strategy> |

    section_9_statistics:
      template: |
        ## Summary Statistics

        - Total Requirements: <total>
        - Functional Requirements: <FR_count>
        - Non-Functional Requirements: <NFR_count>
        - Dependencies: <dep_count>
        - Risks: <risk_count>
        - Complexity Score: <0.XX> (<classification>)
        - Primary Domain: <domain> (<XX>%)
```

---

#### T4.3: Tasklist Generator

**Generation Process**:
```yaml
tasklist_generator:
  output_dir: "<output_dir>/tasklists/"
  file_pattern: "M{N}-{name}.md"

  directory_creation:
    action: "Create tasklists/ directory if not exists"
    tool: "Bash mkdir -p"

  per_milestone_file:
    naming:
      pattern: "M{N}-{slug}.md"
      slug_rules:
        - "Lowercase milestone name"
        - "Replace spaces with hyphens"
        - "Remove special characters"
      examples:
        - "M1-foundation.md"
        - "M2-wave1.md"
        - "M3-wave2.md"

    template: |
      # Tasklist: M<N> - <Milestone Name>

      ## Metadata
      - **Milestone**: M<N>
      - **Dependencies**: <M{N} list or "None">
      - **Estimated Complexity**: <Low|Medium|High>
      - **Primary Persona**: <persona>
      - **Deliverables**: <count>

      ---

      ## Tasks

      ### T<M>.<N>: <Task Name>
      **Type**: <FEATURE|IMPROVEMENT|DOC|TEST>
      **Priority**: <P0-Critical|P1-High|P2-Medium|P3-Low>
      **Files Affected**:
      - `<file_path_1>`
      - `<file_path_2>`

      #### Steps
      1. <Specific action with expected outcome>
      2. <Next action>
      3. <Continue until complete>

      #### Acceptance Criteria
      - [ ] <Measurable criterion 1>
      - [ ] <Measurable criterion 2>
      - [ ] <Measurable criterion 3>

      #### Verification
      ```bash
      # <Description of what this verifies>
      <command to run>
      # Expected: <expected output>
      ```

      ---

      ## Milestone Completion Checklist

      - [ ] T<M>.1: <task name>
      - [ ] T<M>.2: <task name>
      - [ ] T<M>.3: <task name>

      ## Dependencies
      - <dependency description>

      ## Notes
      - <important notes for implementer>

      ---

      *Tasklist generated by SuperClaude Roadmap Generator v1.0*

  task_generation_rules:
    task_per_deliverable: true
    steps_per_task: "3-7 actionable steps"
    acceptance_criteria: "2-5 measurable outcomes"
    verification: "1-2 bash commands with expected output"

  file_write_order:
    sequential: "Write files in milestone order M1 → M2 → ... → MN"
    reason: "Later files may reference earlier ones"
```

---

#### T4.4: test-strategy.md Generator

**Generation Process**:
```yaml
test_strategy_generator:
  output_file: "<output_dir>/test-strategy.md"

  template: |
    # Test Strategy: <Specification Title>

    ## Test Environment

    ### Paths
    - **Test Location**: `tests/<spec-slug>/`
    - **Fixtures**: `tests/<spec-slug>/fixtures/`
    - **Mocks**: `tests/<spec-slug>/mocks/`

    ### Test Runner
    - **Framework**: pytest (Python) / vitest (TypeScript)
    - **Command**: `uv run pytest tests/<spec-slug>/ -v`
    - **Coverage**: `uv run pytest --cov=<module> tests/<spec-slug>/`

    ---

    ## Test Categories

    ### Unit Tests
    **Purpose**: Validate individual functions and components in isolation
    **Scope**: Single function/method, no external dependencies
    **Naming**: `test_<function>_<scenario>.py`

    ### Integration Tests
    **Purpose**: Validate multi-component workflows
    **Scope**: Multiple components working together
    **Naming**: `test_integration_<workflow>.py`

    ### Compliance Tests
    **Purpose**: Validate tier classification accuracy
    **Scope**: STRICT/STANDARD/LIGHT/EXEMPT classification
    **Naming**: `test_compliance_<tier>.py`

    ### E2E Tests
    **Purpose**: Full skill invocation and output validation
    **Scope**: Complete workflow from input to output
    **Naming**: `test_e2e_<scenario>.py`

    ---

    ## Test Matrix

    | Deliverable | Unit | Integration | Compliance | E2E |
    |-------------|------|-------------|------------|-----|
    | D1.1 | ✅ | ✅ | ❌ | ❌ |
    | D1.2 | ✅ | ✅ | ❌ | ✅ |
    | D2.1 | ✅ | ✅ | ✅ | ✅ |

    ---

    ## SuperClaude-Specific Validation

    ### TodoWrite State Validation
    - [ ] Only 3 states used: `pending`, `in_progress`, `completed`
    - [ ] No `blocked` state in any TodoWrite call
    - [ ] `[BLOCKED: reason]` prefix used for blocked items
    - [ ] Only ONE task `in_progress` at any time

    ### Task Tool Validation
    - [ ] Prompts contain complete instructions (no subagent_type references)
    - [ ] Sub-agent delegation uses Task tool with prompt parameter
    - [ ] Agent responses properly processed

    ### Wave Orchestration Validation
    - [ ] Waves execute in order (0 → 1 → 2 → 3 → 4 → 5)
    - [ ] Wave prerequisites checked before execution
    - [ ] Wave outputs available to subsequent waves

    ### Compliance Tier Validation
    - [ ] STRICT tier triggers on security/multi-file keywords
    - [ ] EXEMPT tier triggers on read-only/exploration
    - [ ] LIGHT tier triggers on typo/minor changes
    - [ ] STANDARD tier is default fallback

    ### MCP Circuit Breaker Validation
    - [ ] Sequential server failure triggers native fallback
    - [ ] Context7 failure triggers WebSearch fallback
    - [ ] Serena failure triggers basic file operations
    - [ ] Circuit breaker states properly tracked

    ---

    ## Test Data

    ### Sample Specifications
    - `fixtures/simple-spec.md` - LOW complexity, single domain
    - `fixtures/medium-spec.md` - MEDIUM complexity, 2-3 domains
    - `fixtures/complex-spec.md` - HIGH complexity, multi-domain

    ### Expected Outputs
    - `fixtures/expected/simple-roadmap.md`
    - `fixtures/expected/medium-roadmap.md`
    - `fixtures/expected/complex-roadmap.md`

    ---

    *Test strategy generated by SuperClaude Roadmap Generator v1.0*
```

---

#### T4.5: execution-prompt.md Generator

**Generation Process**:
```yaml
execution_prompt_generator:
  output_file: "<output_dir>/execution-prompt.md"

  template: |
    # Execution Prompt: <Specification Title>

    ## Overview

    This document provides step-by-step instructions for implementing the
    **<title>** roadmap. Follow milestones in order, respecting dependencies.

    **Total Milestones**: <count>
    **Estimated Complexity**: <LOW|MEDIUM|HIGH>
    **Primary Persona**: <persona>

    ---

    ## Prerequisites

    Before starting execution:

    - [ ] Read `roadmap.md` for complete milestone overview
    - [ ] Review `extraction.md` for requirement details
    - [ ] Ensure development environment is ready
    - [ ] Activate appropriate personas: `--persona-<primary>`
    - [ ] Enable MCP servers: Sequential, Context7, Serena

    ---

    ## Execution Order

    ```
    M1 ──► M2 ──► M3 ──► M4 ──► M5
                    └──► M6 (parallel eligible)
    ```

    ### Phase 1: Foundation
    - **M1**: <milestone name> (no dependencies)

    ### Phase 2: Core Implementation
    - **M2**: <milestone name> (depends on M1)
    - **M3**: <milestone name> (depends on M2)

    ### Phase 3: Validation & Release
    - **M4**: <milestone name> (depends on M3)
    - **M5**: <milestone name> (depends on M4)

    ---

    ## Per-Milestone Instructions

    ### M1: <Milestone Name>

    **Command**: `/sc:task-unified @tasklists/M1-<name>.md --compliance strict`

    **Key Tasks**:
    1. T1.1: <task description>
    2. T1.2: <task description>

    **Critical Notes**:
    - ⚠️ <important warning>
    - ℹ️ <helpful information>

    **Verification**:
    ```bash
    <verification command>
    ```

    ---

    ## Post-Execution Checklist

    After completing all milestones:

    - [ ] All milestone completion checklists marked done
    - [ ] Quality analysis score ≥85/100
    - [ ] All HIGH severity issues resolved
    - [ ] Test suite passes
    - [ ] Documentation updated
    - [ ] Memory files written for session persistence

    ---

    ## Troubleshooting

    ### Common Issues

    | Issue | Symptom | Solution |
    |-------|---------|----------|
    | TodoWrite Error | "blocked is not a valid state" | Use `[BLOCKED: reason]` prefix with `pending` status |
    | Template Not Found | "No matching template" | Check plugin templates exist, or use `--template inline` |
    | Low Quality Score | Score <70% | Review ISS-XXX issues, apply remediation |
    | MCP Timeout | Server not responding | Check circuit breaker, use fallback |

    ### Recovery Procedures

    **If milestone fails**:
    1. Read error message carefully
    2. Check tasklist for specific task that failed
    3. Fix issue and re-run failed task only
    4. Continue with remaining tasks

    **If quality gate fails**:
    1. Run `/sc:analyze --focus quality` on outputs
    2. Create remediation tasklist (M{N}.5)
    3. Execute remediation
    4. Re-run quality analysis

    ---

    ## Success Verification

    Execution is complete when:

    1. ✅ All milestones show 100% task completion
    2. ✅ Quality score ≥85/100
    3. ✅ All 5 required artifacts generated:
       - roadmap.md
       - extraction.md
       - tasklists/M*.md
       - test-strategy.md
       - execution-prompt.md
    4. ✅ Verification commands pass
    5. ✅ Memory files written

    **Final Command**:
    ```bash
    /sc:reflect @roadmap.md --verify-completion
    ```

    ---

    *Execution prompt generated by SuperClaude Roadmap Generator v1.0*
```

---

#### T4.6: Wave 3 Parallelization

**Parallelization Strategy**:
```yaml
wave_3_parallelization:
  dependency_graph:
    roadmap.md: []  # No dependencies, generate first
    extraction.md: []  # Can generate early from Wave 1 data
    tasklists/: [roadmap.md]  # Needs milestone structure
    test-strategy.md: [tasklists/]  # Needs task details
    execution-prompt.md: [tasklists/]  # Needs task details

  execution_order:
    phase_1_concurrent:
      files: [roadmap.md, extraction.md]
      reason: "Both use Wave 1/2 data, no interdependencies"
      tool: "Parallel Write operations"

    phase_2_sequential:
      files: [tasklists/]
      reason: "Must complete before phase 3"
      tool: "Sequential Write per milestone file"

    phase_3_concurrent:
      files: [test-strategy.md, execution-prompt.md]
      reason: "Both depend on tasklists, no interdependency"
      tool: "Parallel Write operations"

  performance_target:
    improvement: "30-45% over sequential execution"
    baseline: "5 sequential writes"
    optimized: "2 sequential phases + 2 concurrent batches"
    calculation: |
      Sequential: 5 file writes = 5 units
      Parallel: (2 concurrent) + 1 + (2 concurrent) = 3 units
      Improvement: (5-3)/5 = 40%

  implementation:
    parallel_write:
      method: "Multiple Write tool calls in single response"
      example: |
        # In single Claude response:
        Write(roadmap.md, content1)
        Write(extraction.md, content2)  # Concurrent with above

    completion_tracking:
      phase_1_complete: "roadmap.md AND extraction.md exist"
      phase_2_complete: "All M*.md files in tasklists/"
      phase_3_complete: "test-strategy.md AND execution-prompt.md exist"

  error_handling:
    partial_failure:
      action: "Retry failed file only"
      preserve: "Successfully written files"
    race_condition:
      prevention: "No shared state between concurrent writes"
      verification: "Check file existence after write"
```

---

### Wave 3 Output: Generated Artifacts

**Artifact Summary**:
```yaml
wave_3_output:
  artifacts:
    - name: "roadmap.md"
      location: "<output_dir>/roadmap.md"
      sections: 8
      generated_by: "T4.1"

    - name: "extraction.md"
      location: "<output_dir>/extraction.md"
      sections: 9
      generated_by: "T4.2"

    - name: "tasklists/"
      location: "<output_dir>/tasklists/"
      file_count: "<milestone_count>"
      pattern: "M{N}-{name}.md"
      generated_by: "T4.3"

    - name: "test-strategy.md"
      location: "<output_dir>/test-strategy.md"
      sections: 6
      generated_by: "T4.4"

    - name: "execution-prompt.md"
      location: "<output_dir>/execution-prompt.md"
      sections: 7
      generated_by: "T4.5"

  validation:
    all_artifacts_exist: true
    id_schema_consistent: true
    cross_references_valid: true

  statistics:
    total_files: "<5 + milestone_count>"
    total_sections: "<40+ depending on milestones>"
    generation_time: "<estimated seconds>"
```

---

*Skill definition for SuperClaude Framework v4.2.0+*
*Based on SC-ROADMAP-FEATURE-SPEC.md v1.1.0*
